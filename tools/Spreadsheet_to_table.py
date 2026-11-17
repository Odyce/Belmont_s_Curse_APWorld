"""
Generates the item or location table of the cvbc APWorld from the inventory spreadsheet.

Usage:
    python spreadsheet_to_table.py <path/to/inventory_cvbc.xlsx> <items|locations>

The result is written in a "tmp" folder next to this script (created if needed):
    tmp/ItemTable.py      -> item_table: Dict[str, ItemData]
    tmp/LocationTable.py  -> location_table: Dict[str, LocationData]

Nothing is written if the spreadsheet has an error: every problem found is listed
and the script exits with code 1. Fix the spreadsheet, not the generated file.

Requires openpyxl (pip install openpyxl). This is a dev tool, it is never imported
by the APWorld itself.
"""

import argparse
import sys
from datetime import date
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl is missing: run 'pip install openpyxl' first.")


## Spreadsheet text -> member of C_BC_Category in Types.py. Keep both in sync.
CATEGORIES = {
    "Relic": "RELIC",
    "Weapon": "WEAPON",
    "Clue": "CLUE",
    "Tarot Cards": "TAROT",
    "Augmentation": "AUGMENTATION",
    "Work of Mercy upgrade": "WOMU",
    "Key Item / Skill": "KIS",
    "EXP Statue": "EXPS",
    "Trap": "TRAP",
}

## Second digit block of the AP IDs for each category (see the "ID Range" sheet).
ID_BLOCKS = {
    "Relic": 1, "Weapon": 2, "Clue": 3, "Tarot Cards": 4, "Augmentation": 5,
    "Work of Mercy upgrade": 6, "Key Item / Skill": 7, "EXP Statue": 8, "Trap": 9,
}
ITEM_ID_BASE = 7_000_000
LOCATION_ID_BASE = 7_100_000

CLASSIFICATIONS = {"progression", "progression_skip_balancing", "useful", "filler", "trap"}

HEADER_ROW = 2
FIRST_DATA_ROW = 3


class SheetErrors(Exception):
    pass


def clean(value):
    """Strips strings, turns empty cells into None."""
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def read_sheet(workbook, sheet_name: str, wanted: dict) -> list:
    """
    Reads a sheet as a list of (row number, {key: value}).
    Columns are found by their header (row 2), so moving a column doesn't break anything.
    wanted = {key: header text without the dropdown arrow}
    """
    if sheet_name not in workbook.sheetnames:
        raise SheetErrors([f"Sheet '{sheet_name}' not found."])
    sheet = workbook[sheet_name]

    columns = {}
    for cell in sheet[HEADER_ROW]:
        if isinstance(cell.value, str):
            columns[cell.value.replace("▼", "").strip()] = cell.column
    missing = [header for header in wanted.values() if header not in columns]
    if missing:
        raise SheetErrors([f"{sheet_name}: column(s) not found in row {HEADER_ROW}: {', '.join(missing)}"])

    rows = []
    for row in range(FIRST_DATA_ROW, sheet.max_row + 1):
        values = {key: clean(sheet.cell(row, columns[header]).value) for key, header in wanted.items()}
        if any(value is not None for value in values.values()):
            rows.append((row, values))
    return rows


def check_formula_values(rows, sheet_name, errors):
    """With data_only=True, a formula never calculated by a spreadsheet app comes back as None."""
    for row, values in rows:
        for key, value in values.items():
            if isinstance(value, str) and value.startswith("="):
                errors.append(f"{sheet_name} row {row}: '{key}' is a formula without value, "
                              f"open and save the file in your spreadsheet app first")


def check_id(ap_id, category, base, where, errors, seen_ids):
    if not isinstance(ap_id, int):
        errors.append(f"{where}: AP ID must be an integer, got {ap_id!r}")
        return
    if ap_id in seen_ids:
        errors.append(f"{where}: AP ID {ap_id} already used by '{seen_ids[ap_id]}'")
    if category in ID_BLOCKS:
        start = base + ID_BLOCKS[category] * 1000
        if not start <= ap_id <= start + 999:
            errors.append(f"{where}: AP ID {ap_id} is out of the '{category}' range ({start}-{start + 999})")


def build_items(workbook) -> list:
    rows = read_sheet(workbook, "Items", {
        "name": "Item name",
        "category": "Category",
        "group": "Progressive group (weapons)",
        "tier": "Tier",
        "count": "Quantity",
        "classification": "Classification",
        "ap_id": "AP ID",
    })
    errors = []
    check_formula_values(rows, "Items", errors)
    items, seen_names, seen_ids = [], {}, {}

    for row, v in rows:
        where = f"Items row {row}"
        name = v["name"]
        if name is None:
            errors.append(f"{where}: no item name")
            continue
        where += f" ({name})"
        if name in seen_names:
            errors.append(f"{where}: name already used on row {seen_names[name]}")
        seen_names[name] = row

        if v["category"] not in CATEGORIES:
            errors.append(f"{where}: unknown category {v['category']!r}")
        if v["classification"] not in CLASSIFICATIONS:
            errors.append(f"{where}: unknown classification {v['classification']!r}")
        if not isinstance(v["count"], int) or v["count"] < 0:
            errors.append(f"{where}: quantity must be a positive integer, got {v['count']!r}")
        if v["tier"] is not None and not isinstance(v["tier"], int):
            errors.append(f"{where}: tier must be an integer, got {v['tier']!r}")
        if v["tier"] is not None and v["group"] is None:
            errors.append(f"{where}: has a tier but no progressive group")
        if v["group"] is not None and v["category"] != "Weapon":
            errors.append(f"{where}: only weapons can have a progressive group")
        check_id(v["ap_id"], v["category"], ITEM_ID_BASE, where, errors, seen_ids)
        if isinstance(v["ap_id"], int):
            seen_ids.setdefault(v["ap_id"], name)

        items.append(v)

    if errors:
        raise SheetErrors(errors)
    return items


def build_locations(workbook) -> list:
    rows = read_sheet(workbook, "Locations", {
        "name": "Location name",
        "category": "Vanilla category",
        "vanilla_item": "Vanilla item",
        "prerequisite": "Access prerequisites",
        "ap_id": "AP ID",
        "region": "Logic region",
    })
    # Used only to cross-check the locations
    item_names = {v["name"] for _, v in read_sheet(workbook, "Items", {"name": "Item name"}) if v["name"]}
    regions = set()
    for _, v in read_sheet(workbook, "Areas", {"from": "Region (Area - Sub-area)", "to": "Connected to"}):
        regions.update(region for region in (v["from"], v["to"]) if region)

    errors = []
    check_formula_values(rows, "Locations", errors)
    locations, seen_names, seen_ids = [], {}, {}

    for row, v in rows:
        where = f"Locations row {row}"
        name = v["name"]
        if name is None:
            errors.append(f"{where}: no location name")
            continue
        where += f" ({name})"
        if name in seen_names:
            errors.append(f"{where}: name already used on row {seen_names[name]}")
        seen_names[name] = row

        if v["category"] not in CATEGORIES:
            errors.append(f"{where}: unknown vanilla category {v['category']!r}")
        if v["vanilla_item"] is None:
            errors.append(f"{where}: no vanilla item")
        elif v["vanilla_item"] not in item_names:
            errors.append(f"{where}: vanilla item {v['vanilla_item']!r} doesn't exist in the Items sheet")
        if v["region"] is None:
            errors.append(f"{where}: no logic region")
        elif v["region"] not in regions:
            errors.append(f"{where}: logic region {v['region']!r} doesn't exist in the Areas sheet")
        if v["prerequisite"] is None:
            errors.append(f"{where}: no access prerequisite (write 'Nothing extra' if there is none)")
        elif v["prerequisite"].count("(") != v["prerequisite"].count(")"):
            errors.append(f"{where}: unbalanced parentheses in the prerequisite")
        check_id(v["ap_id"], v["category"], LOCATION_ID_BASE, where, errors, seen_ids)
        if isinstance(v["ap_id"], int):
            seen_ids.setdefault(v["ap_id"], name)

        locations.append(v)

    if errors:
        raise SheetErrors(errors)
    return locations


def header(source: Path, kind: str) -> list:
    return [
        f"# AUTO-GENERATED by spreadsheet_to_table.py from {source.name} on {date.today().isoformat()}.",
        f"# Do not edit by hand: fix the spreadsheet and run the script again ({kind}).",
        "",
        "from typing import Dict",
        "",
    ]


def write_items(items, source: Path) -> str:
    lines = header(source, "items")
    lines += [
        "from BaseClasses import ItemClassification",
        "from .Types import ItemData, C_BC_Category",
        "",
        "item_table: Dict[str, ItemData] = {",
    ]
    current_category = None
    for v in items:
        if v["category"] != current_category:
            current_category = v["category"]
            lines.append(f"    # {current_category}")
        args = [
            str(v["ap_id"]),
            f"ItemClassification.{v['classification']}",
            f"C_BC_Category.{CATEGORIES[v['category']]}",
            f"count={v['count']}",
        ]
        if v["group"] is not None:
            args += ["is_progressive=True", f"progressive_group={v['group']!r}"]
            if v["tier"] is not None:
                args.append(f"progressive_tier={v['tier']}")
        lines.append(f"    {v['name']!r}: ItemData({', '.join(args)}),")
    lines.append("}")
    return "\n".join(lines) + "\n"


def write_locations(locations, source: Path) -> str:
    lines = header(source, "locations")
    lines += [
        "from .Types import LocationData, C_BC_Category",
        "",
        "location_table: Dict[str, LocationData] = {",
    ]
    current_region = None
    for v in sorted(locations, key=lambda loc: (loc["region"], loc["ap_id"])):
        if v["region"] != current_region:
            current_region = v["region"]
            lines.append(f"    # {current_region}")
        args = [
            str(v["ap_id"]),
            repr(v["region"]),
            repr(v["vanilla_item"]),
            f"C_BC_Category.{CATEGORIES[v['category']]}",
            repr(v["prerequisite"]),
        ]
        lines.append(f"    {v['name']!r}: LocationData({', '.join(args)}),")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generates ItemTable.py or LocationTable.py from the cvbc spreadsheet.")
    parser.add_argument("spreadsheet", type=Path, help="path to inventory_cvbc.xlsx")
    parser.add_argument("table", choices=["items", "locations"], type=str.lower, help="which table to generate")
    args = parser.parse_args()

    if not args.spreadsheet.is_file():
        sys.exit(f"File not found: {args.spreadsheet}")
    # data_only=True: read the computed values, not the formulas
    workbook = openpyxl.load_workbook(args.spreadsheet, data_only=True)

    try:
        if args.table == "items":
            rows = build_items(workbook)
            content, file_name = write_items(rows, args.spreadsheet), "ItemTable.py"
        else:
            rows = build_locations(workbook)
            content, file_name = write_locations(rows, args.spreadsheet), "LocationTable.py"
    except SheetErrors as error:
        problems = error.args[0]
        print(f"{len(problems)} problem(s) found, nothing was written:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(__file__).resolve().parent / "tmp"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / file_name
    out_file.write_text(content, encoding="utf-8")
    print(f"{len(rows)} {args.table} written to {out_file}")


if __name__ == "__main__":
    main()
