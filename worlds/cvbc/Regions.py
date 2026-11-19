from BaseClasses import Region
from .Types import C_BC_Location, C_BC_Item
from .RuleTable import connections
from .Locations import get_locations_from_region, ending_table, location_table
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import CBCWorld

## Dev Note, I almost completely rewrote this file without commenting it, bad habbit, sorry
## I will put comments later when I have some times for a future release

region_names = [
    "Menu", 
    "Works of Mercy (virtual)",
    "Paris Streets (Start)",
    "Paris Streets",
    "Holy Innocents' Cemetery",
    "Catacombs of Paris (Entrance)",
    "Catacombs of Paris",
    "Ferryman's Wharf",
    "Mammon's Lair",
    "Main Hall",
    "Library",
    "Notre-Dame",
    "Hall of Mirrors",
    "Clock Tower",
    "Clock Tower (Upper)",
    "Master's Quarter (Bad Ending)",
    "Master's Quarter",
]

def create_regions(world: "CBCWorld"):
    regions = {name: create_region(world, name) for name in region_names}

    for ending in ending_table.values():
        regions[ending.region].add_event(ending.name, ending.name, location_type=C_BC_Location, item_type=C_BC_Item)

    for src, dest, prereq in connections:
        regions[src].connect(regions[dest])

    ## Quick verification that every location belongs in a created region
    created = set()
    for region in regions.values():
        for location in region.locations:
            if location.address is not None:
                created.add(location.name)

    missing = set(location_table) - created
    assert not missing, f"{len(missing)} location(s) were not created, check the region names: {sorted(missing)[:5]}"


def create_region(world: "CBCWorld", name: str) -> Region:
    reg = Region(name, world.player, world.multiworld)
    reg.add_locations(get_locations_from_region(reg.name), C_BC_Location)
    world.multiworld.regions.append(reg)
    return reg