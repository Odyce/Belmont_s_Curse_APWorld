"""
Reads and checks every access rule of the cvbc spreadsheet, then generates RuleTable.py:
every rule already turned into a tree, so the APWorld never has to read rule texts itself.

Usage:
    python spreadsheet_rules.py <path/to/inventory_cvbc.xlsx>                 check everything, write tmp/RuleTable.py
    python spreadsheet_rules.py <path/to/inventory_cvbc.xlsx> --check-only    check everything, write nothing
    python spreadsheet_rules.py <path/to/inventory_cvbc.xlsx> --show "<location name or 'Src -> Dest'>"
                                                                               print how one rule is understood
The result is to be used as if by puting RuleTable.py into the folder worlds/cvbc/
(And also I find the comment of connection useless so I remove them while doing so)

What is checked:
    - the "Access prerequisites" column of the Locations sheet
    - the "Prerequisites A → B" and "Prerequisites B → A" columns of the Areas sheet
    - the "Access prerequisites" column of the Endings sheet, if that column exists
    for each text: syntax, unknown item / group / region names, items that are not progression
    (the logic never counts them), "Region:" used in a connection, "All of region:" pointing
    at the location's own region (infinite recursion in Archipelago).

Nothing is written if a problem is found: every problem is listed and the script exits with code 1.
The result goes to tmp/RuleTable.py next to this script. Copy it as-is into worlds/cvbc/RuleTable.py
(replace the whole file each time, never edit it). It contains:
    connections     List[(source region, destination region, tree)]  -> Regions.py and Rules.py
    location_rules  Dict[location name, tree]                         -> Rules.py
    ending_rules    Dict[ending name, tree]                           -> Rules.py

Why trees and not ready-made lambdas: some rules depend on the YAML options (progressive weapons,
progressive virtues), and the options are only known when a seed is generated. So the script does
all the reading and checking once, and Rules.py only turns each tree into a lambda (see TREE FORMAT).

Rule syntax (keywords are case-insensitive, except AND / OR which must be in capitals):
    A AND B                      both                (AND is applied before OR, like && and || in C)
    A OR B                       one of them
    ( ... )                      grouping
    N of: A, B, C                at least N of the list (put it in parentheses if something follows it)
    N x Name                     at least N copies of an item, or N items of a group in total
    Region: Name                 can reach the region (locations only)
    All of region: Name          can reach every location of the region (locations only)
    Nothing extra                always true
    Name                         has the item (or at least one item of the group)

Requires openpyxl (pip install openpyxl). Dev tool, never imported by the APWorld itself.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl is missing: run 'pip install openpyxl' first.")


HEADER_ROW = 2
FIRST_DATA_ROW = 3

# Item groups usable in rules. The groups live in Groups.py, which this script can't import
# (it needs Archipelago), so keep this dict in sync with Groups.py by hand.
KNOWN_GROUPS = {
    "Heart Fragments": {"Brave Heart Fragment", "Wise Heart Fragment"},
    "Mammon's Eyes": {"Oozing Eye", "Trembling Eye", "Thrilling Eye"},
    "Keys": {"The Fallen's Key", "The Warrior's Key", "The Prophetess's Key", "Brauner's Paintbrush"},
    "Skills": {"Arcane Whip", "Holy Light", "Aerial Rush", "Smash", "Double Jump"},
    "Virtues": {"Virtue of Courage", "Virtue of Temperance", "Virtue of Justice", "Virtue of Prudence",
                "Progressive Virtue"},
}

# Text of the "B → A" column meaning "no connection in this direction"
NO_CONNECTION = {"impossible"}


class RuleError(Exception):
    pass


# ============================================================================================
# READING THE SPREADSHEET
# ============================================================================================

def clean(value):
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def read_sheet(workbook, sheet_name: str, wanted: dict) -> list:
    """List of (row number, {key: value}). Columns are found by their header (row 2)."""
    if sheet_name not in workbook.sheetnames:
        sys.exit(f"Sheet '{sheet_name}' not found.")
    sheet = workbook[sheet_name]
    columns = {}
    for cell in sheet[HEADER_ROW]:
        if isinstance(cell.value, str):
            columns[cell.value.replace("▼", "").strip()] = cell.column
    missing = [header for header in wanted.values() if header not in columns]
    if missing:
        sys.exit(f"{sheet_name}: column(s) not found in row {HEADER_ROW}: {', '.join(missing)}")
    rows = []
    for row in range(FIRST_DATA_ROW, sheet.max_row + 1):
        values = {key: clean(sheet.cell(row, columns[header]).value) for key, header in wanted.items()}
        if any(value is not None for value in values.values()):
            rows.append((row, values))
    return rows


# ============================================================================================
# SCANNER: text -> tokens
# ============================================================================================
# Tokens are tuples:
#   ("(",) (")",) (",",) ("AND",) ("OR",)
#   ("NOF", n)                    "3 of:"
#   ("REGION", name, all_of)      "Region: X" / "All of region: X"
#   ("TEXT", text)                anything else (item name, "24 x Name", "Nothing extra")

RE_OPERATOR = re.compile(r"(AND|OR)(?![\w'])")
RE_N_OF = re.compile(r"(\d+)\s+of\s*:", re.IGNORECASE)
RE_REGION = re.compile(r"(all\s+of\s+)?region\s*:\s*", re.IGNORECASE)
RE_TEXT_END = re.compile(r"\s+(?:AND|OR)(?![\w'])|[(),]")


def tokenize(text: str, region_names: list) -> list:
    # Longest names first, so "Clock Tower (Upper)" wins over "Clock Tower".
    # Region names can contain parentheses: that's why they are matched whole, never split.
    regions_by_length = sorted(region_names, key=len, reverse=True)
    tokens, pos = [], 0
    while True:
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos >= len(text):
            return tokens
        rest = text[pos:]

        if rest[0] in "(),":
            tokens.append((rest[0],))
            pos += 1
            continue

        match = RE_OPERATOR.match(rest)
        if match:
            tokens.append((match.group(1),))
            pos += match.end()
            continue

        match = RE_N_OF.match(rest)
        if match:
            tokens.append(("NOF", int(match.group(1))))
            pos += match.end()
            continue

        match = RE_REGION.match(rest)
        if match:
            after = rest[match.end():]
            name = next((region for region in regions_by_length if after.startswith(region)), None)
            if name is None:
                word = RE_TEXT_END.split(after, 1)[0].strip()
                raise RuleError(f"unknown region after '{match.group(0).strip()}': {word!r}")
            tokens.append(("REGION", name, match.group(1) is not None))
            pos += match.end() + len(name)
            continue

        end = RE_TEXT_END.search(rest)
        chunk = rest[:end.start()] if end else rest
        tokens.append(("TEXT", chunk.strip()))
        pos += len(chunk)


# ============================================================================================
# PARSER: tokens -> tree (recursive descent)
# ============================================================================================
# TREE FORMAT. Each node is a tuple, its first element says what it is:
#   ("true",)                       always true                            "Nothing extra"
#   ("item", name, count)           has at least count copies of the item  "Smash", "20 x Wise Heart Fragment"
#   ("group", name, count)          has at least count items of the group  "24 x Heart Fragments"
#   ("region", name)                can reach the region                   "Region: Notre-Dame"
#   ("all_of_region", name)         can reach every location of the region "All of region: Main Hall"
#   ("and", (node, node, ...))      every child is true                    "A AND B"
#   ("or", (node, node, ...))       at least one child is true             "A OR B"
#   ("n_of", n, (node, node, ...))  at least n children are true           "2 of: A, B, C"

RE_COUNT = re.compile(r"^(\d+)\s*x\s+(.+)$", re.IGNORECASE)


class Parser:
    def __init__(self, tokens, item_names):
        self.tokens = tokens
        self.pos = 0
        self.item_names = item_names

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self, kind=None):
        token = self.peek()
        if token is None:
            raise RuleError("missing ')'" if kind == ")" else "the text ends too early (nothing after AND / OR / ',' ?)")
        if kind is not None and token[0] != kind:
            raise RuleError(f"expected '{kind}', found {describe(token)}")
        self.pos += 1
        return token

    def parse(self):
        node = self.expr()
        if self.peek() is not None:
            raise RuleError(f"unexpected {describe(self.peek())} (missing AND / OR, or a parenthesis?)")
        return node

    def expr(self):          # expr := term ("OR" term)*
        nodes = [self.term()]
        while self.peek() == ("OR",):
            self.take()
            nodes.append(self.term())
        return nodes[0] if len(nodes) == 1 else ("or", tuple(nodes))

    def term(self):          # term := factor ("AND" factor)*
        nodes = [self.factor()]
        while self.peek() == ("AND",):
            self.take()
            nodes.append(self.factor())
        return nodes[0] if len(nodes) == 1 else ("and", tuple(nodes))

    def factor(self):
        token = self.take()
        kind = token[0]

        if kind == "(":
            node = self.expr()
            self.take(")")
            return node

        if kind == "NOF":    # N of: factor ("," factor)*
            nodes = [self.factor()]
            while self.peek() == (",",):
                self.take()
                nodes.append(self.factor())
            if token[1] > len(nodes):
                raise RuleError(f"'{token[1]} of:' but the list only has {len(nodes)} element(s)")
            return ("n_of", token[1], tuple(nodes))

        if kind == "REGION":
            return ("all_of_region" if token[2] else "region", token[1])

        if kind == "TEXT":
            return self.name(token[1])

        raise RuleError(f"unexpected {describe(token)}")

    def name(self, text):
        if text.lower() == "nothing extra":
            return ("true",)
        count = 1
        match = RE_COUNT.match(text)
        if match and match.group(2) in self.item_names | set(KNOWN_GROUPS):
            count, text = int(match.group(1)), match.group(2)
        if text in self.item_names:
            return ("item", text, count)
        if text in KNOWN_GROUPS:
            return ("group", text, count)
        raise RuleError(f"unknown item or group: {text!r}")


def describe(token):
    if token[0] == "TEXT":
        return repr(token[1])
    if token[0] == "NOF":
        return f"'{token[1]} of:'"
    if token[0] == "REGION":
        return f"region '{token[1]}'"
    return f"'{token[0]}'"


def parse_rule(text, region_names, item_names):
    if text is None:
        raise RuleError("empty prerequisite (write 'Nothing extra' if there is none)")
    return Parser(tokenize(text, region_names), item_names).parse()


def walk(node):
    """Every node of the tree, the node itself included."""
    yield node
    if node[0] in ("and", "or"):
        for child in node[1]:
            yield from walk(child)
    elif node[0] == "n_of":
        for child in node[2]:
            yield from walk(child)


def show(node, indent=0):
    pad = "    " * indent
    kind = node[0]
    if kind == "true":
        return [pad + "always true"]
    if kind == "item":
        return [pad + (f"has {node[2]} x {node[1]}" if node[2] > 1 else f"has {node[1]}")]
    if kind == "group":
        return [pad + f"has {node[2]} item(s) of the group {node[1]}"]
    if kind == "region":
        return [pad + f"can reach the region {node[1]}"]
    if kind == "all_of_region":
        return [pad + f"can reach every location of {node[1]}"]
    title = {"and": "ALL of:", "or": "ONE of:"}.get(kind, f"AT LEAST {node[1]} of:" if kind == "n_of" else kind)
    children = node[1] if kind in ("and", "or") else node[2]
    lines = [pad + title]
    for child in children:
        lines += show(child, indent + 1)
    return lines


# ============================================================================================
# CHECKS
# ============================================================================================

def check_tree(tree, where, own_region, is_connection, progression, errors):
    for node in walk(tree):
        kind = node[0]
        if kind == "item" and node[1] not in progression:
            errors.append(f"{where}: '{node[1]}' is not progression, the logic will never count it")
        if kind == "group":
            useless = sorted(KNOWN_GROUPS[node[1]] - progression)
            if useless:
                errors.append(f"{where}: group '{node[1]}' contains non progression items: {useless}")
        if kind in ("region", "all_of_region") and is_connection:
            errors.append(f"{where}: 'Region:' can't be used in a connection "
                          f"(Archipelago would need an indirect condition)")
        if kind == "all_of_region" and node[1] == own_region:
            errors.append(f"{where}: 'All of region: {node[1]}' is the location's own region "
                          f"(the location would depend on itself)")


def has_column(workbook, sheet_name, header):
    if sheet_name not in workbook.sheetnames:
        return False
    return any(isinstance(cell.value, str) and cell.value.replace("▼", "").strip() == header
               for cell in workbook[sheet_name][HEADER_ROW])


def main():
    parser = argparse.ArgumentParser(description="Checks the cvbc spreadsheet rules and generates RuleTable.py.")
    parser.add_argument("spreadsheet", type=Path, help="path to inventory_cvbc.xlsx")
    parser.add_argument("--check-only", action="store_true", help="check everything, write nothing")
    parser.add_argument("--show", metavar="NAME", help="print how one rule (location, ending or 'Src -> Dest') is understood")
    args = parser.parse_args()

    if not args.spreadsheet.is_file():
        sys.exit(f"File not found: {args.spreadsheet}")
    workbook = openpyxl.load_workbook(args.spreadsheet, data_only=True)

    items = read_sheet(workbook, "Items", {"name": "Item name", "classification": "Classification"})
    item_names = {v["name"] for _, v in items if v["name"]}
    progression = {v["name"] for _, v in items
                   if v["name"] and v["classification"] in ("progression", "progression_skip_balancing")}

    areas = read_sheet(workbook, "Areas", {
        "src": "Region (Area - Sub-area)",
        "dest": "Connected to",
        "forward": "Prerequisites A → B",
        "backward": "Prerequisites B → A",
    })
    locations = read_sheet(workbook, "Locations", {
        "name": "Location name",
        "prerequisite": "Access prerequisites",
        "region": "Logic region",
    })
    endings = []
    if has_column(workbook, "Endings", "Access prerequisites"):
        endings = read_sheet(workbook, "Endings", {"name": "Ending", "prerequisite": "Access prerequisites"})

    region_names = set()
    for _, v in areas:
        region_names.update(r for r in (v["src"], v["dest"]) if r)
    region_names.update(v["region"] for _, v in locations if v["region"])
    region_names = sorted(region_names)

    for group, members in KNOWN_GROUPS.items():
        unknown = sorted(members - item_names)
        if unknown:
            sys.exit(f"KNOWN_GROUPS['{group}'] contains unknown items {unknown}: update this script.")

    errors = []
    texts = {}          # name -> (original text, tree), for --show and the comments of the generated file

    def read_rule(name, text, where, own_region, is_connection):
        if name in texts:
            errors.append(f"{where}: '{name}' is written twice")
            return None
        try:
            tree = parse_rule(text, region_names, item_names)
        except RuleError as error:
            errors.append(f"{where}: {error}")
            return None
        texts[name] = (text, tree)
        check_tree(tree, where, own_region, is_connection, progression, errors)
        return tree

    # Connections, in both directions
    connections = []
    for row, v in areas:
        if not v["src"] or not v["dest"]:
            errors.append(f"Areas row {row}: region or 'Connected to' missing")
            continue
        directions = [(v["src"], v["dest"], v["forward"], "A → B")]
        if v["backward"] and v["backward"].lower() not in NO_CONNECTION:
            directions.append((v["dest"], v["src"], v["backward"], "B → A"))
        for src, dest, text, column in directions:
            name = f"{src} -> {dest}"
            tree = read_rule(name, text, f"Areas row {row} ({name}, {column})", None, True)
            if tree is not None:
                connections.append((src, dest, tree))

    # Locations
    location_rules = {}
    for row, v in locations:
        if v["name"]:
            tree = read_rule(v["name"], v["prerequisite"], f"Locations row {row} ({v['name']})", v["region"], False)
            if tree is not None:
                location_rules[v["name"]] = tree

    # Endings (optional column)
    ending_rules = {}
    for row, v in endings:
        if v["name"]:
            tree = read_rule(v["name"], v["prerequisite"], f"Endings row {row} ({v['name']})", None, False)
            if tree is not None:
                ending_rules[v["name"]] = tree

    if args.show:
        if args.show not in texts:
            sys.exit(f"'{args.show}' not found (or its rule has an error, run without --show to see it).")
        text, tree = texts[args.show]
        print(f"{args.show}\n  text: {text}\n  understood as:")
        print("\n".join("    " + line for line in show(tree)))
        return

    if errors:
        print(f"{len(errors)} problem(s) found, nothing was written:", file=sys.stderr)
        for problem in errors:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: {len(connections)} connections, {len(location_rules)} locations and "
          f"{len(ending_rules)} endings understood.")
    if not endings:
        print("Note: no 'Access prerequisites' column in the Endings sheet, ending_rules is empty.")
    if args.check_only:
        return

    lines = [
        f"# AUTO-GENERATED by spreadsheet_rules.py from {args.spreadsheet.name} on {date.today().isoformat()}.",
        "# Do not edit by hand: fix the spreadsheet and run the script again.",
        "# Tree format: see the TREE FORMAT comment in tools/spreadsheet_rules.py",
        "",
        "from typing import Dict, List, Tuple",
        "",
        "Rule = tuple",
        "",
        "## (source region, destination region, rule). Region.connect names the entrance \"Source -> Destination\"",
        "connections: List[Tuple[str, str, Rule]] = [",
    ]
    for src, dest, tree in connections:
        lines.append(f"    # {texts[f'{src} -> {dest}'][0]}")
        lines.append(f"    ({src!r}, {dest!r}, {tree!r}),")
    lines += ["]", "", "location_rules: Dict[str, Rule] = {"]
    for name, tree in location_rules.items():
        lines.append(f"    # {texts[name][0]}")
        lines.append(f"    {name!r}: {tree!r},")
    lines += ["}", "", "ending_rules: Dict[str, Rule] = {"]
    for name, tree in ending_rules.items():
        lines.append(f"    # {texts[name][0]}")
        lines.append(f"    {name!r}: {tree!r},")
    lines.append("}")

    out_dir = Path(__file__).resolve().parent / "tmp"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "RuleTable.py"
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Written to {out_file}")


if __name__ == "__main__":
    main()
