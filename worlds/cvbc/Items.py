# So the goal here is to have a catalog of all the items in your game
# To correctly generate a games items they need to be bundled in a list
# A list in programming terms is anything in square brackets [] to put it simply

# When a list is described its described as a list of x where x is the type of variable within it
# IE: ["apple", "pear", "grape"] is a list of strings (anything inside "" OR '' are considered strings)

## Unlike what I did in Types.py, I will immediately delete all the references code from this files for this file is much longer
## I will however keep the comments that I feel are useful "as is"

# Logging = output. How you'll figure out whats going wrong
import logging

# Built in AP imports
from BaseClasses import ItemClassification

# These come from the other files in this example. If you want to see the source ctrl + click the name
# You can also do that ctrl + click for any functions to see what they do
from .Types import ItemData, C_BC_Category, C_BC_Item
from .Locations import location_table
from typing import List, Dict, TYPE_CHECKING

# This is just making sure nothing gets confused dw about what its doing exactly
if TYPE_CHECKING:
   from . import CBCWorld


# This is a generic function to create a singular item

## And it will be kept mostly the same
def create_item(world: "CBCWorld", name: str) -> C_BC_Item:
    data = item_table[name]
    return C_BC_Item(name, data.classification, data.ap_code, world.player)


# If you're curious about the -> List[Item] that is a syntax to make sure you return the correct variable type
# In this instance we're saying we only want to return a list of items
# You'll see a bunch of other examples of this in other functions
# It's main purpose is to protect yourself from yourself

## Perfectly explained, I just adapted it to our specific class of items
## And furthermore, I decided to create the pool by basing it on the locations, it just make more sense in this APWorld
def create_itempool(world: "CBCWorld") -> List[C_BC_Item]:
    # This is the empty list of items. You'll add all the items in the game to this list
    itempool: List[C_BC_Item] = []
    unlocked_count = 0

    ## Here we make a loop that goes through each location, and check if it's item must be shuffled or not
    ## And if it does, it is added to the pool
    for name, data in location_table.items():
        if must_stay_vanilla(world, name, data):
            world.get_location(name).place_locked_item(create_item(world, data.vanilla_item))
        else:
            itempool.append(create_item(world, data.vanilla_item))
            unlocked_count += 1

    itempool = apply_progressive_weapons(world, itempool)
    itempool = apply_progressive_virtues(world, itempool)
    itempool = apply_traps(world, itempool)
    assert len(itempool) == unlocked_count, f"Pool size {len(itempool)} != {unlocked_count} unlocked locations"
    return itempool

## The next tables and function are custom made to check the logic of checks
table_categorie_option = {
    C_BC_Category.RELIC: "randomise_relics",
    C_BC_Category.WEAPON: "randomise_weapons",
    C_BC_Category.CLUE: "randomise_clues",
    C_BC_Category.TAROT: "randomise_tarot_cards",
    C_BC_Category.AUGMENTATION: "randomise_augmentations",
    C_BC_Category.WOMU: "randomise_works_of_mercy",
    C_BC_Category.KIS: "randomise_key_items",
    C_BC_Category.EXPS: "randomise_exp_statues",
}

prg_virtues = {
    'Virtue of Courage',
    'Virtue of Temperance',
    'Virtue of Justice',
    'Virtue of Prudence',
    'Tarot : The Self'
} ## Note: A safekeep that checks the names of these items in the original table is a good idea in case of renaming/typo in the spreadsheet

def must_stay_vanilla(world: "CBCWorld", name, data) -> bool:
    options = world.options
    item = data.vanilla_item

    if item in prg_virtues:
        if options.progressive_virtues and options.randomise_tarot_cards:
            return False
    
    if item == "The Shadow Confronted":
        if options.randomise_shadows_flag and options.randomise_key_items:
            return False
        else:
            return True
    
    option = table_categorie_option[data.vanilla_category]
    return not getattr(options, option)


## And the next functions are made to modify the pool with the progressive items and traps
def apply_progressive_weapons(world: "CBCWorld", itempool: List[C_BC_Item]) -> List[C_BC_Item]:
    if not world.options.progressive_weapons:
        return itempool
    new_pool = []
    for item in itempool:
        data = item_table[item.name]
        if data.progressive_tier is not None: 
            new_pool.append(create_item(world, f"Progressive {data.progressive_group}")) ## Note: A safekeep that checks the names of these items in the original table is a good idea in case of renaming/typo in the spreadsheet
        else:
            new_pool.append(item)
    return new_pool

def apply_progressive_virtues(world: "CBCWorld", itempool: List[C_BC_Item]) -> List[C_BC_Item]:
    options = world.options
    if not (options.progressive_virtues and options.randomise_tarot_cards):
        return itempool
    return [create_item(world, "Progressive Virtue") if item.name in prg_virtues else item
            for item in itempool]

trap_weight_options = {
    "Burn Trap": "burn_trap_weight",
    "Bleed Trap": "bleed_trap_weight",
    "Petrify Trap": "petrify_trap_weight",
    "Plague Trap": "plague_trap_weight",
    "Turned to Gold Trap": "gold_trap_weight",
    "Stun Trap": "stun_trap_weight",
} ## Note: A safekeep that checks the names of these items in the original table is a good idea in case of renaming/typo in the spreadsheet

def apply_traps(world: "CBCWorld", itempool: List[C_BC_Item]) -> List[C_BC_Item]:
    chance = world.options.trap_chance.value
    if chance == 0:
        return itempool

    trap_names = list(trap_weight_options.keys())
    trap_weights = [getattr(world.options, option).value for option in trap_weight_options.values()]
    if sum(trap_weights) == 0:
        return itempool

    new_pool = []
    for item in itempool:
        data = item_table[item.name]
        if data.classification == ItemClassification.filler and world.random.randint(1, 100) <= chance:
            trap = world.random.choices(trap_names, weights=trap_weights)[0]
            new_pool.append(create_item(world, trap))
        else:
            new_pool.append(item)
    return new_pool


# Time for the fun part of listing all of the items
# Watch out for overlap with your item codes

## In the older version of this file, there were many tables for each category of item, I removed them altogether since we have an existing category system
## In order to get or update the following item table, just go in the "tools" directory and use "Spreadsheet_to_table.py"
## That way you will directly get the table from the reference sheet, as the spreadsheet is law in this APWorld
item_table: Dict[str, ItemData] = {
    # Relic
    'Abyssal Eye': ItemData(7001001, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    "Banshee's Wall": ItemData(7001002, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    "Beelzebub's Seal": ItemData(7001003, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Blackened Heart': ItemData(7001004, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Blood Vial': ItemData(7001005, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Crypt Key': ItemData(7001006, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Crystallized Blood': ItemData(7001007, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Cursed Coin': ItemData(7001008, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Dark Sigil': ItemData(7001009, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Dusk Amulet': ItemData(7001010, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Ebony Claw': ItemData(7001011, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Eldritch Talisman': ItemData(7001012, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Forsaken Ring': ItemData(7001013, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Ghostly Pendant': ItemData(7001014, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Gloomstone': ItemData(7001015, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Grim Token': ItemData(7001016, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Haunting Relic': ItemData(7001017, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Hollow Bone': ItemData(7001018, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Infernal Medallion': ItemData(7001019, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    "Lich's Mark": ItemData(7001020, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Midnight Tear': ItemData(7001021, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Moonlit Shard': ItemData(7001022, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Mourning Bead': ItemData(7001023, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Necro Charm': ItemData(7001024, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Nightshade': ItemData(7001025, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Obsidian Fang': ItemData(7001026, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Pale Thorn': ItemData(7001027, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Phantom Ring': ItemData(7001028, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    "Raven's Feather": ItemData(7001029, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    "Revenant's Shard": ItemData(7001030, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Sand Charm': ItemData(7001031, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Shadow Veil': ItemData(7001032, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Sinister Rune': ItemData(7001033, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Soul Fragment': ItemData(7001034, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    "Specter's Whisper": ItemData(7001035, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Twilight Gem': ItemData(7001036, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Vampire Fang': ItemData(7001037, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    'Vile Trinket': ItemData(7001038, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    "Witch's Brew": ItemData(7001039, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    "Witch's Knot": ItemData(7001040, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    "Wraith's Tear": ItemData(7001041, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    "Family's Grave": ItemData(7001042, ItemClassification.useful, C_BC_Category.RELIC, count=1),
    # Weapon
    'Whip': ItemData(7002001, ItemClassification.progression, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Whip', progressive_tier=1),
    'Thorn Whip': ItemData(7002002, ItemClassification.progression, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Whip', progressive_tier=2),
    'Morning Star': ItemData(7002003, ItemClassification.progression, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Whip', progressive_tier=3),
    'Vampire Killer': ItemData(7002004, ItemClassification.progression, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Whip', progressive_tier=4),
    'Longsword': ItemData(7002005, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='OHSword', progressive_tier=1),
    'Bastard Sword': ItemData(7002006, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='OHSword', progressive_tier=2),
    'Joyeuse': ItemData(7002007, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='OHSword', progressive_tier=3),
    'Valmanway': ItemData(7002008, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='OHSword', progressive_tier=4),
    'Burnt Sword of Fierbois': ItemData(7002009, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='THSword', progressive_tier=1),
    'Claymore': ItemData(7002010, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='THSword', progressive_tier=2),
    'Durandal': ItemData(7002011, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='THSword', progressive_tier=3),
    'Excalibur': ItemData(7002012, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='THSword', progressive_tier=4),
    'Pair of Longswords': ItemData(7002013, ItemClassification.progression, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Dual Blades', progressive_tier=1),
    'Rapiers': ItemData(7002014, ItemClassification.progression, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Dual Blades', progressive_tier=2),
    'Almace and Hauteclaire': ItemData(7002015, ItemClassification.progression, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Dual Blades', progressive_tier=3),
    'War and Famine': ItemData(7002016, ItemClassification.progression, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Dual Blades', progressive_tier=4),
    'Lance': ItemData(7002017, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Spear', progressive_tier=1),
    'Halberd': ItemData(7002018, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Spear', progressive_tier=2),
    'Gungnir': ItemData(7002019, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Spear', progressive_tier=3),
    'Chauve-Souris': ItemData(7002020, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Spear', progressive_tier=4),
    'Cestus': ItemData(7002021, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Fists', progressive_tier=1),
    'Jewel Knuckles': ItemData(7002022, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Fists', progressive_tier=2),
    'Fists of Talos': ItemData(7002023, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Fists', progressive_tier=3),
    "Bernhard's Wrath": ItemData(7002024, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Fists', progressive_tier=4),
    'Rusted Harpe and Aegis': ItemData(7002025, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Sword and Shield', progressive_tier=1),
    'Fleuret and Tower Shield': ItemData(7002026, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Sword and Shield', progressive_tier=2),
    "Arondight and Lancelot's Shield": ItemData(7002027, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Sword and Shield', progressive_tier=3),
    "Alucard's Sword and Shield": ItemData(7002028, ItemClassification.useful, C_BC_Category.WEAPON, count=1, is_progressive=True, progressive_group='Sword and Shield', progressive_tier=4),
    'Progressive Whip': ItemData(7002029, ItemClassification.progression, C_BC_Category.WEAPON, count=0, is_progressive=True, progressive_group='Whip'),
    'Progressive OHSword': ItemData(7002030, ItemClassification.useful, C_BC_Category.WEAPON, count=0, is_progressive=True, progressive_group='OHSword'),
    'Progressive THSword': ItemData(7002031, ItemClassification.useful, C_BC_Category.WEAPON, count=0, is_progressive=True, progressive_group='THSword'),
    'Progressive Dual Blades': ItemData(7002032, ItemClassification.progression, C_BC_Category.WEAPON, count=0, is_progressive=True, progressive_group='Dual Blades'),
    'Progressive Spear': ItemData(7002033, ItemClassification.useful, C_BC_Category.WEAPON, count=0, is_progressive=True, progressive_group='Spear'),
    'Progressive Fists': ItemData(7002034, ItemClassification.useful, C_BC_Category.WEAPON, count=0, is_progressive=True, progressive_group='Fists'),
    'Progressive Sword and Shield': ItemData(7002035, ItemClassification.useful, C_BC_Category.WEAPON, count=0, is_progressive=True, progressive_group='Sword and Shield'),
    # Clue
    'The Cursed Clue': ItemData(7003001, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Self Clue': ItemData(7003002, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Fallen First Clue': ItemData(7003003, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Fallen Second Clue': ItemData(7003004, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Warrior First Clue': ItemData(7003005, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Warrior Second Clue': ItemData(7003006, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Prophetess First Clue': ItemData(7003007, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Prophetess Second Clue': ItemData(7003008, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Prophetess Third Clue': ItemData(7003009, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Prophetess Fourth Clue': ItemData(7003010, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Builder First Clue': ItemData(7003011, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Builder Second Clue': ItemData(7003012, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Artist First Clue': ItemData(7003013, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Artist Second Clue': ItemData(7003014, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Artist Third Clue': ItemData(7003015, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Artist Fourth Clue': ItemData(7003016, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Occultist First Clue': ItemData(7003017, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Occultist Second Clue': ItemData(7003018, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Occultist Third Clue': ItemData(7003019, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Occultist Fourth Clue': ItemData(7003020, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Occultist Fifth Clue': ItemData(7003021, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Shadow First Clue': ItemData(7003022, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Shadow Second Clue': ItemData(7003023, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Shadow Third Clue': ItemData(7003024, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Shadow Fourth Clue': ItemData(7003025, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Shadow Fifth Clue': ItemData(7003026, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Shadow Sixth Clue': ItemData(7003027, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Miser First Clue': ItemData(7003028, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Miser Second Clue': ItemData(7003029, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Miser Third Clue': ItemData(7003030, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Miser Fourth Clue': ItemData(7003031, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Whisperer Clue': ItemData(7003032, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Zealot Clue': ItemData(7003033, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Temptress Clue': ItemData(7003034, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Brittle King Clue': ItemData(7003035, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Judge Clue': ItemData(7003036, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Sage First Clue': ItemData(7003037, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Sage Second Clue': ItemData(7003038, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Sage Third Clue': ItemData(7003039, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    'The Sage Fourth Clue': ItemData(7003040, ItemClassification.filler, C_BC_Category.CLUE, count=1),
    # Tarot Cards
    'Tarot : The Cursed': ItemData(7004001, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Self': ItemData(7004002, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Fallen': ItemData(7004003, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Warrior': ItemData(7004004, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Prophetess': ItemData(7004005, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Builder': ItemData(7004006, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Artist': ItemData(7004007, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Occultist': ItemData(7004008, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Shadow': ItemData(7004009, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Miser': ItemData(7004010, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Whisperer': ItemData(7004011, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Zealot': ItemData(7004012, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Temptress': ItemData(7004013, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Brittle King': ItemData(7004014, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Judge': ItemData(7004015, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    'Tarot : The Sage': ItemData(7004016, ItemClassification.progression, C_BC_Category.TAROT, count=1),
    # Augmentation
    'Brave Heart Fragment': ItemData(7005001, ItemClassification.progression, C_BC_Category.AUGMENTATION, count=24),
    'Wise Heart Fragment': ItemData(7005002, ItemClassification.progression, C_BC_Category.AUGMENTATION, count=24),
    'ATK Book': ItemData(7005003, ItemClassification.useful, C_BC_Category.AUGMENTATION, count=14),
    'DEF Book': ItemData(7005004, ItemClassification.useful, C_BC_Category.AUGMENTATION, count=14),
    # Work of Mercy upgrade
    'WOM Cursed Flame': ItemData(7006001, ItemClassification.useful, C_BC_Category.WOMU, count=1),
    'WOM Absolution': ItemData(7006002, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    'WOM Holy Cross': ItemData(7006003, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    'WOM Infernal Pyre': ItemData(7006004, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    'WOM Petrifying Gaze': ItemData(7006005, ItemClassification.useful, C_BC_Category.WOMU, count=2),
    'WOM Fist of Talos': ItemData(7006006, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    'WOM Masterpiece': ItemData(7006007, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    'WOM Blood Spikes': ItemData(7006008, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    'WOM Soul Harvest': ItemData(7006009, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    'WOM Wheel of Chaos': ItemData(7006010, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    'WOM Freezing Path': ItemData(7006011, ItemClassification.useful, C_BC_Category.WOMU, count=2),
    'WOM Chronomantic Dive': ItemData(7006012, ItemClassification.useful, C_BC_Category.WOMU, count=2),
    'WOM Life Drain': ItemData(7006013, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    'WOM Stained-Glass Shield': ItemData(7006014, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    'WOM Chains of Justice': ItemData(7006015, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    'WOM Mirror Walk': ItemData(7006016, ItemClassification.useful, C_BC_Category.WOMU, count=3),
    # Key Item / Skill
    "The Fallen's Key": ItemData(7007001, ItemClassification.progression, C_BC_Category.KIS, count=1),
    "The Warrior's Key": ItemData(7007002, ItemClassification.progression, C_BC_Category.KIS, count=1),
    "The Prophetess's Key": ItemData(7007003, ItemClassification.progression, C_BC_Category.KIS, count=1),
    "Brauner's Paintbrush": ItemData(7007004, ItemClassification.progression, C_BC_Category.KIS, count=1),
    "Ferryman's Obol": ItemData(7007005, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Arcane Whip': ItemData(7007006, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Holy Light': ItemData(7007007, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Aerial Rush': ItemData(7007008, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Smash': ItemData(7007009, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Double Jump': ItemData(7007010, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Virtue of Courage': ItemData(7007011, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Virtue of Temperance': ItemData(7007012, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Virtue of Justice': ItemData(7007013, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Virtue of Prudence': ItemData(7007014, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Progressive Virtue': ItemData(7007015, ItemClassification.progression, C_BC_Category.KIS, count=0),
    'The Shadow Confronted': ItemData(7007016, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Oozing Eye': ItemData(7007018, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Trembling Eye': ItemData(7007019, ItemClassification.progression, C_BC_Category.KIS, count=1),
    'Thrilling Eye': ItemData(7007020, ItemClassification.progression, C_BC_Category.KIS, count=1),
    # EXP Statue
    'Experience Statue 100': ItemData(7008001, ItemClassification.filler, C_BC_Category.EXPS, count=28),
    'Experience Statue 150': ItemData(7008002, ItemClassification.filler, C_BC_Category.EXPS, count=15),
    'Experience Statue 200': ItemData(7008003, ItemClassification.filler, C_BC_Category.EXPS, count=20),
    'Experience Statue 250': ItemData(7008004, ItemClassification.filler, C_BC_Category.EXPS, count=21),
    'Experience Statue 300': ItemData(7008005, ItemClassification.filler, C_BC_Category.EXPS, count=49),
    'Experience Statue 350': ItemData(7008006, ItemClassification.filler, C_BC_Category.EXPS, count=14),
    # Trap
    'Burn Trap': ItemData(7009001, ItemClassification.trap, C_BC_Category.TRAP, count=0),
    'Bleed Trap': ItemData(7009002, ItemClassification.trap, C_BC_Category.TRAP, count=0),
    'Petrify Trap': ItemData(7009003, ItemClassification.trap, C_BC_Category.TRAP, count=0),
    'Turned to Gold Trap': ItemData(7009004, ItemClassification.trap, C_BC_Category.TRAP, count=0),
    'Stun Trap': ItemData(7009005, ItemClassification.trap, C_BC_Category.TRAP, count=0),
    'Plague Trap': ItemData(7009006, ItemClassification.trap, C_BC_Category.TRAP, count=0),
}

for name, data in item_table.items():
    if data.is_progressive:
        assert data.progressive_group is not None, f"Error: Progressive group not filled for {name}."
    else:
        assert data.progressive_group is None, f"Error: Progressive groupe should be False for {name} but possesses a progressive group."


## Called by Archipelago (through __init__.py) when it needs an extra filler item,
def get_filler_item_name(world: "CBCWorld") -> str:
    statues = [name for name, data in item_table.items() if data.category == C_BC_Category.EXPS]
    return world.random.choice(statues)