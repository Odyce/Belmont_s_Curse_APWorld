# This is where your imports go. That means any functions or variables that you want to use here but exist in another file
# What I have here is just some of the basic Archipelago classes that are widely used

# A more indepth explanation of the types of imports
# THE LINES FROM 7-12 ARE EXAMPLE IMPORTS AND NOT NECESSARILY REQUIRED

# import random
# With that import you are importing every single function, class, variable, whatever else that is allowed to be imported from random. Super useful and simple but somewhat bulky

# from random import randrange
# Here you are only grabbing the randrange function from random. This is less bulky but you need to put exactly what you want from that file/library
# If you want more things from the import add a comma like the worlds.AutoWorld import below
import logging

from BaseClasses import Item, Tutorial
from worlds.AutoWorld import World, WebWorld
from typing import Dict, Any

from .Locations import get_location_names
from .Items import create_item, create_itempool, item_table, get_filler_item_name
from .Options import C_BC_Options, create_option_groups
from .Regions import create_regions
from .Types import GAME_NAME
from .Groups import item_groups, location_groups
from .Rules import set_rules

# This is where you setup the page on the site!
# Typically is the name of your game with web
# Whatever you named the folder you are holding all of this in
class CBCWeb(WebWorld):
    # Theres a few different themes so have fun with it
    theme = "ice"
    
    # You shouldnt have to change much here except the name at the bottom!
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Castlevania: Belmont's Curse for Archipelago. "
        "This guide covers single-player, multiworld, and related software.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Odyce"]
    )]

    option_groups = create_option_groups()

# This class is the real meat and potatoes
# Same as the first class its normally named whatever you named your folder with World at the end
class CBCWorld(World):
    """
    1499: In the name of his most royal majesty, the King of France, I request post-haste your presence, for a great evil has descended upon Paris.
    The moon burns red and the city is pandemonium. We have sought every exorcist, every doctor, every scholar to purge this invisible terror. All have failed.
    So now, we appeal to you, Rose Belmont, newest of House Belmont, greatest of the vampire hunters.
    Come deliver Paris from calamity, on a quest together with your friends through the power of Archipelago!
    """

    # You want to put the full name of the game here. If you shortened the name for the folder and class names, dont do that here
    game = GAME_NAME
    # The item_table will be setup in  your Items.py. This line gets all the items you put into item_table and puts it in a way that AP can understand it
    item_name_to_id = {name: data.ap_code for name, data in item_table.items()}
    # get_location_names() will come from your Locations.py
    location_name_to_id = get_location_names()
    # And these 2 are the name of your Options.py class. 
    options_dataclass = C_BC_Options
    options: C_BC_Options
    # The name of the class above
    web = CBCWeb()
    ## Let's add the group we created
    item_name_groups = item_groups
    location_name_groups = location_groups

    # There are other built in variables for AP. You can look at other worlds to see your options
    # Like PLEASE look at the various worlds. Its so helpful. Find one you like and you can duplicate a bunch of it

    # Generate early you do things just before the generation
    # Super important for doing things like adjusting the item pool based on options and the like
    # Can technically be skipped if you dont need to do anything or if you handle it elsewhere like a short hike
    def generate_early(self):
        # I highly recommend looking at other apworlds init files to see some examples
        opt = self.options
        if opt.randomise_tarot_cards.value == 0 and opt.progressive_virtues:
            opt.progressive_virtues.value = 0
            logging.warning(f"{self.player_name}: You can't have progressive virtues if the tarot cards aren't randomised, so it was disabled")
        
        if opt.randomise_weapons.value == 0 and opt.progressive_weapons:
            opt.progressive_weapons.value = 0
            logging.warning(f"{self.player_name}: You can't have progressive weapons if the weapons aren't randomised, so it was disabled")
        
        if opt.trap_chance.value != 0:
            total = opt.burn_trap_weight.value + opt.bleed_trap_weight.value + opt.petrify_trap_weight.value 
            total = total + opt.plague_trap_weight.value + opt.gold_trap_weight.value + opt.stun_trap_weight.value
            if total == 0:
                opt.trap_chance.value = 0
                logging.warning(f"{self.player_name}: You can't have traps if all their weight is equal to 0")
        
        if opt.randomise_key_items.value == 0 and opt.randomise_shadows_flag:
            opt.randomise_shadows_flag.value = 0
            logging.warning(f"{self.player_name}: You can't randomise the First Battle with Death flag if the key items aren't randomised, so it was disabled")

        # Push precollected is how you give your player items they need to start with
        # This is for options though. Dont worry about the starting inventory option thats in all yamls
        # AP handles that one

        ## I gotta had a way to have the starting items set asides and put them here
        ## In the meantime I'll comment the code
        ##self.multiworld.push_precollected(self.create_item(starting_chapter))

    # Regions are the different locations in your world. So like Undead Burgh in dark souls or Pacifilog Town in pokemon
    # They dont have to match your game, they can be whatever you need them to be for organization
    def create_regions(self):
        # This function comes from your Regions.py and dont worry that it matches the function that its in
        create_regions(self)

        # You can also use this space to do other location creation activities
        # Like if an option is enabled to add extra locations
        # Or the opposite, whatever it is. Just be careful that you arent duplicating locations

    # These are some examples of creating items. The create_itempool(self) function is coming from Items.py in this instance
    # The important part is that the items get into the self.multiworld.itempool as a list of Items
    # Ill try to explain better in the Items.py file 
    def create_items(self):
        self.multiworld.itempool += create_itempool(self)

    # This is just a helper function for turning names into Items. You could do some other stuff here as well
    # ahit does similar if you want another look and bomb rush cyberfunk does it in a slightly different way by turning it into a specific item for that game
    # Again hopefully I do a better job of explaining the Items.py file
    def create_item(self, name: str) -> Item:
        return create_item(self, name)
    
    ## Function to go throught the rules of creation, for now basic, will be improved later
    def set_rules(self):
        set_rules(self)

    # The slot data is what youre sending to the AP server kinda. You dont have to add all your options. Really you want the ones you think a pop tracker would use
    ## I did the very least required, I'll see later if it needs to be extended
    def fill_slot_data(self) -> Dict[str, Any]:
        return self.options.as_dict("end_goal", "death_link", "death_link_mercy", "randomise_shadows_flag")

    def get_filler_item_name(self) -> str:
        return get_filler_item_name(self)