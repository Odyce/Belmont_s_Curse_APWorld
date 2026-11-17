## Access rules of the cvbc APWorld
## Every rule comes from the spreadsheet, through tools/spreadsheet_rules.py, which writes RuleTable.py.
## RuleTable.py holds each rule as a tree (see the TREE FORMAT comment in tools/spreadsheet_rules.py),
## this file only turns each tree into a function "state -> bool" and puts it where it belongs

from typing import Callable, List, TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import set_rule
from .Items import item_table
from .Locations import location_table, ending_table
from .RuleTable import connections, location_rules, ending_rules, Rule

if TYPE_CHECKING:
    from . import CBCWorld

RuleFunction = Callable[[CollectionState], bool]

## The progressive virtues, in the order they are received (5th = The Self)
## The logic only asks for "all four Virtues" or "The Self" for now, so the order of the first four
## doesn't change anything here, but the client must use the same order.
progressive_virtue_order: List[str] = [
    "Virtue of Courage",
    "Virtue of Temperance",
    "Virtue of Justice",
    "Virtue of Prudence",
    "Tarot : The Self",
]

## Same list as end_goal in Options.py: value 0 = Bad, 1 = Neutral, 2 = True
goal_names: List[str] = ["Bad Ending", "Neutral Ending", "True Ending"]


def set_rules(world: "CBCWorld") -> None:
    player = world.player

    ## Connections: Region.connect named each entrance "Source -> Destination"
    for src, dest, tree in connections:
        set_rule(world.get_entrance(f"{src} -> {dest}"), build_rule(world, tree))

    ## Locations
    for name, tree in location_rules.items():
        set_rule(world.get_location(name), build_rule(world, tree, current_location=name))

    ## Endings: the event location has the same name as the ending
    for name, tree in ending_rules.items():
        set_rule(world.get_location(name), build_rule(world, tree, current_location=name))

    ## Victory: having the item of the chosen ending (put on its event by Regions.py)
    goal = goal_names[world.options.end_goal.value]
    world.multiworld.completion_condition[player] = lambda state: state.has(goal, player)


def build_rule(world: "CBCWorld", tree: Rule, current_location: str = "") -> RuleFunction:
    ## Turns one tree node into a function, calling itself on the children
    ## Every lambda is created inside a function call (and not inside a loop), so each one keeps its own values
    player = world.player
    kind = tree[0]

    if kind == "true":
        return lambda state: True

    if kind == "item":
        return item_rule(world, tree[1], tree[2])

    if kind == "group":
        group, count = tree[1], tree[2]
        return lambda state: state.has_group(group, player, count)

    if kind == "region":
        region = tree[1]
        return lambda state: state.can_reach_region(region, player)

    if kind == "all_of_region":
        ## Every location of the region, without the location being built (it can't depend on itself)
        names = [name for name, data in location_table.items()
                 if data.region == tree[1] and name != current_location]
        return lambda state: all(state.can_reach_location(name, player) for name in names)

    if kind == "and":
        children = [build_rule(world, child, current_location) for child in tree[1]]
        return lambda state: all(child(state) for child in children)

    if kind == "or":
        children = [build_rule(world, child, current_location) for child in tree[1]]
        return lambda state: any(child(state) for child in children)

    if kind == "n_of":
        needed = tree[1]
        children = [build_rule(world, child, current_location) for child in tree[2]]
        return lambda state: sum(1 for child in children if child(state)) >= needed

    raise ValueError(f"Unknown rule node {tree!r}, RuleTable.py and Rules.py don't match")


def item_rule(world: "CBCWorld", name: str, count: int) -> RuleFunction:
    ## "Has the item", translated when a progressive option replaced it in the pool (see Items.py)
    player = world.player
    options = world.options
    data = item_table[name]

    ## Progressive weapons: "Morning Star" (tier 3) = 3 x "Progressive Whip"
    ## Same conditions as apply_progressive_weapons in Items.py: weapons in the pool and the option on
    if (options.progressive_weapons and options.randomise_weapons
            and data.progressive_tier is not None):
        progressive = f"Progressive {data.progressive_group}"
        tier = data.progressive_tier
        return lambda state: state.has(progressive, player, tier)

    ## Progressive virtues: the k-th virtue of the list = k x "Progressive Virtue"
    ## Same conditions as apply_progressive_virtues in Items.py
    if (options.progressive_virtues and options.randomise_tarot_cards
            and name in progressive_virtue_order):
        tier = progressive_virtue_order.index(name) + 1
        return lambda state: state.has("Progressive Virtue", player, tier)

    return lambda state: state.has(name, player, count)


## Safekeeps: RuleTable.py, Items.py and Locations.py must agree (fails right at import, not during a seed)
for _name in progressive_virtue_order:
    assert _name in item_table, f"Progressive virtue '{_name}' is not an item, check progressive_virtue_order."
for _name in location_rules:
    assert _name in location_table, f"RuleTable.py has a rule for '{_name}', which is not a location: regenerate it."
for _name in location_table:
    assert _name in location_rules, f"Location '{_name}' has no rule in RuleTable.py: regenerate it."
for _name in ending_rules:
    assert _name in ending_table, f"RuleTable.py has a rule for the ending '{_name}', which is not in ending_table."
assert set(goal_names) == set(ending_table), "goal_names and ending_table don't have the same endings."