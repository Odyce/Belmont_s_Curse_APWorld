# This file is technically not required whatsoever
# I like to do this for organization and a few other worlds do similar
# Its helpful for grouping variables, making them easy to access, and consistent
## My comment as Odyce, main dev for the cvbc apworld will be written with a second # to be differenciated from the orignal ones
## I choose to keep this file, as a mainly C dev, it just makes more sense to code that way IMO

from enum import Enum
from typing import NamedTuple, Optional
from BaseClasses import Location, Item, ItemClassification

## The use of this variable is to reduce possible human error when typing
GAME_NAME = "Castlevania: Belmont's Curse"

# These 2 make it so that the generic Location and Item types are more specific for your game
## I obviously changed them to fit the game and switched their order so Item comes first, to keep it consistent
class C_BC_Item(Item):
    game = GAME_NAME

class C_BC_Location(Location):
    game = GAME_NAME

# I use these next 2 to convert the number you get from the options into a name
# Mainly used in Items.py for starting chapter
# Not important for a lot of games
# class ChapterType(IntEnum):
#     GreenHillZone = 1
#     Romania = 2
#     Sewer = 3
# chapter_type_to_name = {
#     ChapterType.GreenHillZone:  "Green Hill Zone",
#     ChapterType.Romania:        "Romania",
#     ChapterType.Sewer:          "The Sewer"
# }

## I commented the previous section as it could be useful as a reminder, I might delete it later
## The following Enum will simplify the transition from the spreadsheet to the actual code

class C_BC_Category(str, Enum):
    RELIC = "Relic"
    WEAPON = "Weapon"
    CLUE = "Clue"
    TAROT = "Tarot Cards"
    AUGMENTATION = "Augmentation"
    WOMU = "Work of Mercy upgrade"
    KIS = "Key Item / Skill"
    EXPS = "EXP Statue"
    TRAP = "Trap"

# Here is where all the stuff from the Items.py comes from
# You can add or take away anything you want but ap_code and classification are pretty important
# Adding Optional[] makes it so you dont have to include it when you create an ItemData
# Adding = x at the end adds a default to it so if you dont include it, it'll default to whatever you put after it
# class ItemData(NamedTuple):
#     ap_code: Optional[int]
#     classification: ItemClassification
#     count: Optional[int] = 1

# Again where all the Location.py things come from
# You can add whatever you want here as well but ap_code and region are pretty important
# class LocData(NamedTuple):
#     ap_code: Optional[int]
#     region: Optional[str]

## Once again the previous section is a good reminder, but will be deleted past V1 of the release
## I also added a class EndingData because as I've gathered, they are counted as either a Location or an Item with an ap_code = None
## Creating a separated class for them allow the removal of many Optionnal[] for both classes and it sorts it in a better way
class ItemData(NamedTuple):
    ap_code: int
    classification: ItemClassification
    category: C_BC_Category
    count: int = 1
    is_progressive: bool = False
    progressive_group: Optional[str] = None
    progressive_tier: Optional[int] = None

class LocationData(NamedTuple):
    ap_code: int
    region: str
    vanilla_item: str
    vanilla_category: C_BC_Category
    prerequisite: str = "Nothing extra"

class EndingData(NamedTuple):
    name: str
    region: str