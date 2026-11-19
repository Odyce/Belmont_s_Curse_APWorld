## I created this file because Items.py was starting to be really long, then merged the location groups in it
## It's used to create item and location groups, for Rules.py or later in custom YAML files
## (hints, start_inventory, exclude_locations, priority_locations...)
## __init__.py declares them with:
##     item_name_groups = item_groups
##     location_name_groups = location_groups
##
## Archipelago rules (checked by its unit tests, and at the end of this file):
##   - an item group can't have an item's name, a location group can't have a location's name
##   - a group can't be empty
##   - a group can only contain existing items / locations
## "Everything" (items) and "Everywhere" (locations) are created by Archipelago, don't redefine them.

from typing import Dict, Set

from BaseClasses import ItemClassification
from .Items import item_table
from .Locations import location_table
from .Types import C_BC_Category


## Shared by both kinds of groups: category -> group name
## An item group "Relics" = the relic items, a location group "Relics" = where the relics are in vanilla
category_group_names: Dict[C_BC_Category, str] = {
    C_BC_Category.RELIC: "Relics",
    C_BC_Category.WEAPON: "Weapons",
    C_BC_Category.CLUE: "Clues",
    C_BC_Category.TAROT: "Tarot Cards",
    C_BC_Category.AUGMENTATION: "Augmentations",
    C_BC_Category.WOMU: "Work of Mercy Upgrades",
    C_BC_Category.KIS: "Key Items and Skills",
    C_BC_Category.EXPS: "EXP Statues",
    C_BC_Category.TRAP: "Traps",
}


# ============================================================================================
# ITEM GROUPS
# ============================================================================================

## One group per weapon type: the 4 weapons + the matching "Progressive ..." item
## Key = progressive_group in the item table, value = group name
weapon_group_names: Dict[str, str] = {
    "Whip": "Whips",
    "OHSword": "One-Handed Swords",
    "THSword": "Two-Handed Swords",
    "Dual Blades": "Dual Blades",
    "Spear": "Spears",
    "Fists": "Fists",
    "Sword and Shield": "Swords and Shields",
}

## Hand-made item groups, for things the table can't deduce on its own
custom_item_groups: Dict[str, Set[str]] = {
    "Skills": {"Arcane Whip", "Holy Light", "Aerial Rush", "Smash", "Double Jump"},
    "Keys": {"The Fallen's Key", "The Warrior's Key", "The Prophetess's Key", "Brauner's Paintbrush"},
    "Mammon's Eyes": {"Oozing Eye", "Trembling Eye", "Thrilling Eye"},
    "Virtues": {"Virtue of Courage", "Virtue of Temperance", "Virtue of Justice", "Virtue of Prudence", "Progressive Virtue"},
    "Heart Fragments": {"Brave Heart Fragment", "Wise Heart Fragment"},
    "Books": {"ATK Book", "DEF Book"},
}


def build_item_groups() -> Dict[str, Set[str]]:
    groups: Dict[str, Set[str]] = {}

    for category, group_name in category_group_names.items():
        groups[group_name] = {name for name, data in item_table.items() if data.category == category}

    for progressive_group, group_name in weapon_group_names.items():
        groups[group_name] = {name for name, data in item_table.items() if data.progressive_group == progressive_group}

    ## The 7 "Progressive ..." weapon items: progressive group but no tier
    groups["Progressive Weapons"] = {name for name, data in item_table.items()
                                     if data.progressive_group is not None and data.progressive_tier is None}

    ## Every item that can unlock something (useful for hints)
    groups["Progression Items"] = {name for name, data in item_table.items()
                                   if data.classification & ItemClassification.progression}

    groups.update(custom_item_groups)
    return groups


# ============================================================================================
# LOCATION GROUPS
# ============================================================================================

## One group per area, read from the prefix of the location name ("PS - Sewer Reservoir : ...")
## Every location must match one prefix, otherwise the safekeep at the end of the file fails
area_prefixes: Dict[str, str] = {
    "PS - ": "Paris Streets",
    "HIC - ": "Holy Innocents' Cemetery",
    "CoP - ": "Catacombs of Paris",
    "MH - ": "Main Hall",
    "L - ": "Library",
    "CT - ": "Clock Tower",
    "ND - ": "Notre-Dame",
    "HoM - ": "Hall of Mirrors",
    "MQ - ": "Master's Quarter",
    "WOM - ": "Works of Mercy",
    "Ferryman's Wharf : ": "Ferryman's Wharf",
}

## Groups by type of check, read from the end of the location name (after " : ")
## Key = group name, value = text the description must contain
check_type_groups: Dict[str, str] = {
    "Silver Chests": "Silver Chest",
    "Gold Chests": "Gold Chest",
    "Unique Rewards": "Unique Reward",
    "Absorptions": "Absorbed",
    "Spy Statues": "Spy Statue",
    "Ghosts": "Ghost",
    "Virtue Bells": "Bell Rang",
    "Starting Locations": "Starting",
}


def build_location_groups() -> Dict[str, Set[str]]:
    groups: Dict[str, Set[str]] = {}

    ## By area (name prefix)
    for prefix, group_name in area_prefixes.items():
        groups[group_name] = {name for name in location_table if name.startswith(prefix)}

    ## By vanilla category: same group names as the item categories
    for category, group_name in category_group_names.items():
        members = {name for name, data in location_table.items() if data.vanilla_category == category}
        if members:     # no location has a trap as vanilla item: no empty "Traps" group
            groups[group_name] = members

    ## By type of check (text after " : " in the name)
    for group_name, text in check_type_groups.items():
        groups[group_name] = {name for name in location_table if text in name.split(" : ", 1)[-1]}

    return groups


item_groups: Dict[str, Set[str]] = build_item_groups()
location_groups: Dict[str, Set[str]] = build_location_groups()


# ============================================================================================
# SAFEKEEPS: same checks as the Archipelago unit tests, but they fail right at import
# ============================================================================================

for group_name, members in item_groups.items():
    assert group_name not in item_table, f"Item group '{group_name}' has the same name as an item."
    assert members, f"Item group '{group_name}' is empty."
    for member in members:
        assert member in item_table, f"Item group '{group_name}' contains '{member}', which is not an item."

for group_name, members in location_groups.items():
    assert group_name not in location_table, f"Location group '{group_name}' has the same name as a location."
    assert members, f"Location group '{group_name}' is empty."
    for member in members:
        assert member in location_table, f"Location group '{group_name}' contains '{member}', which is not a location."

## Every location must belong to exactly one area group
for name in location_table:
    areas = [group_name for prefix, group_name in area_prefixes.items() if name.startswith(prefix)]
    assert len(areas) == 1, f"Location '{name}' matches {len(areas)} area prefixes instead of 1: {areas}"
