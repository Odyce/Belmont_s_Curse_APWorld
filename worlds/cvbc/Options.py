from typing import List, Dict, Any
from dataclasses import dataclass
from Options import Choice, OptionGroup, Toggle, Range, DeathLink, PerGameCommonOptions, DefaultOnToggle

# If youve ever gone to an options page and seen how sometimes options are grouped
# This is that
def create_option_groups() -> List[OptionGroup]:
    option_group_list: List[OptionGroup] = []
    for name, options in c_bc_option_groups.items():
        option_group_list.append(OptionGroup(name=name, options=options))

    return option_group_list

## There is not much information on this file, all comments have been kept, but it's pretty clear that it is used for the YAML configuration of the apworld
## I once again removed the APSkeleton template exemples, as it was of no use. But the format is pretty clear, and I'll detail it once

## Here you name your options as a class, and define what kind of option is it (toggle, choice, range...etc)
class RandomiseRelics(DefaultOnToggle):
    ## Then you describe what this option will be used for in the final game
    """
    Choose if you want to randomise the relics or not, this option does not include the eyes of Mammon
    Off: The relics will stay in their vanilla silver chest
    """
    ## And here after you configure the parameters of the option, which depends on what kind of option it is
    display_name = "Randomise Relics"

class RandomiseWeapons(DefaultOnToggle):
    """
    Choose if you want to randomise the weapons or not
    Off: The weapons will stay in their vanilla gold chest
    """
    display_name = "Randomise Weapons"

class ProgressiveWeapons(Toggle):
    """
    Makes it so the weapons will be grouped by category, so you'll get each weapon class in order from weakest to strongest
    Off: You can get any weapon at any point of the Archipelago, no matter if you got the previous one in its class or not
    WARNING: Turning it on will have no effect whatsoever if the weapons are not randomised
    """
    display_name = "Progressive Weapons"

class RandomiseTarotCards(DefaultOnToggle):
    """
    Choose if you want to randomise the Tarot Cards or not
    Off: The tarot cards will stay linked to their respective boss/npc absorption
    """
    display_name = "Randomise Tarot Cards"

class ProgressiveVirtues(Toggle):
    """
    This options makes the tarot card "The Self" the 5th part of a progressive check including all Virtues as if they were tangible items
    Getting to the Dopppelganger fight also requires the first four parts of this progressive check
    Off: You can get "The Self" in its vanilla location or by any check, depending on the randomisation of tarot cards
    WARNING: Turning it on will have no effect whatsoever if the tarot cards are not randomised, but it will randomise the Virtues even if the Key Items are not randomised.
    """
    display_name = "Progressive Virtues"

class RandomiseWorksOfMercy(DefaultOnToggle):
    """
    Choose if you want to randomise the Works of Mercy rewards or not
    Off: The Works of Mercy will be unlocked standardly by choice after completing their challenges
    """
    display_name = "Randomise Works of Mercy"

class RandomiseKeyItems(DefaultOnToggle):
    """
    Choose if you want to randomise the Key Items and Skill or not
    This option includes the Eyes of Mammon (even if they are technically relics) and the Four Virtues
    Off: Every Key Item and Skill will be obtained where they would be in the vanilla game
    WARNING: The Four Virtues will still be randomised if you checked the "Progressive Virtues" option
    """
    display_name = "Randomise Key Items"

class RandomiseAugmentations(DefaultOnToggle):
    """
    Choose if you want to randomise the augmentations or not, it includes ATK boost, DEF boost, Wise Heart Fragments and Brave Heart Fragments
    Off: The augmentations will stay in their vanilla locations
    """
    display_name = "Randomise Augmentations"

class RandomiseClues(DefaultOnToggle):
    """
    Choose if you want to randomise the clues or not
    Off: The clues will stay in their vanilla locations
    """
    display_name = "Randomise Clues"

class RandomiseEXPStatues(DefaultOnToggle):
    """
    Choose if you want to randomise the EXP Statues or not (their bonus experience basically)
    Off: The statues will give their vanilla experience point rather than checks
    """
    display_name = "Randomise EXP Statues"

class RandomiseShadowsFlag(Toggle):
    """
    Choose if you want to randomise the effect of the first boss battle with Death or not
    It's still being tested, but this affect Dracula's Castle apparition and access, mirror Kneeling, and access to the first Death Boss battle
    Off: The effects will happen once you've defeated Death in the Catacombs of Paris
    Note: Turning it on will have no effect whatsoever if the key items and skill are not randomised
    WARNING: This option is HIGHLY UNSTABLE!!! It is being experimented on and refined in the current releases! Proceed at your own risk!
    """
    display_name = "Randomise Death First Battle Flag"

class EndGoal(Choice):
    """
    Choose which ending you want to reach to conclude your game (default: Neutral Ending)
    Note: You can do any of other two endings without softlocking your game, however they ARE NOT checks
    """
    display_name = "End goal"
    option_bad_ending = 0
    option_neutral_ending = 1
    option_true_ending = 2
    default = 1

class TrapChance(Range):
    """
    Percentage of filler items replaced by a trap, it will spice up your game
    WARNING: At least one trap weight options must be superior to 0, otherwise it won't work
    """
    display_name = "Trap Chance"
    range_start = 0
    range_end = 100
    default = 0

class BurnTrapWeight(Range):
    """
    Relative weight (percentage) of traps that will burn Rose, (default 22%)
    """
    display_name = "Burn Trap Weight"
    range_start = 0
    range_end = 100
    default = 22

class BleedTrapWeight(Range):
    """
    Relative weight (percentage) of traps that will make Rose bleed, (default 22%)
    """
    display_name = "Bleed Trap Weight"
    range_start = 0
    range_end = 100
    default = 22

class PetrifyTrapWeight(Range):
    """
    Relative weight (percentage) of traps that will petrify Rose, (default 22%)
    """
    display_name = "Petrify Trap Weight"
    range_start = 0
    range_end = 100
    default = 22

class PlagueTrapWeight(Range):
    """
    Relative weight (percentage) of traps that will plague Rose, (default 22%)
    """
    display_name = "Plague Trap Weight"
    range_start = 0
    range_end = 100
    default = 22

class GoldTrapWeight(Range):
    """
    Relative weight (percentage) of traps that will turn Rose into gold, like in the Mammon Boss fight (default 6%)
    """
    display_name = "Turned to Gold Trap Weight"
    range_start = 0
    range_end = 100
    default = 6

class StunTrapWeight(Range):
    """
    Relative weight (percentage) of traps that will stun Rose, (default 6%)
    """
    display_name = "Stun Trap Weight"
    range_start = 0
    range_end = 100
    default = 6

class CBCDeathLink(DeathLink):
    """
    Activate Death link or not. Meaning that when you will die other player will die as well, and it works both way
    """
    display_name = "DeathLink"

class CBCDeathLinkMercy(Range):
    """
    Choose how many deaths Rose can endure before the Deathlink activates (default 1)
    """
    display_name = "Death Link Mercy"
    range_start = 1
    range_end = 5
    default = 1


## And finally here, you gather all the options for you game as a list
@dataclass
class C_BC_Options(PerGameCommonOptions):
    randomise_relics:           RandomiseRelics
    randomise_weapons:          RandomiseWeapons
    progressive_weapons:        ProgressiveWeapons
    randomise_tarot_cards:      RandomiseTarotCards
    progressive_virtues:        ProgressiveVirtues
    randomise_works_of_mercy:   RandomiseWorksOfMercy
    randomise_key_items:        RandomiseKeyItems
    randomise_augmentations:    RandomiseAugmentations
    randomise_clues:            RandomiseClues
    randomise_exp_statues:      RandomiseEXPStatues
    randomise_shadows_flag:     RandomiseShadowsFlag
    end_goal:                   EndGoal
    trap_chance:                TrapChance
    burn_trap_weight:           BurnTrapWeight
    bleed_trap_weight:          BleedTrapWeight
    petrify_trap_weight:        PetrifyTrapWeight
    plague_trap_weight:         PlagueTrapWeight
    gold_trap_weight:           GoldTrapWeight
    stun_trap_weight:           StunTrapWeight
    death_link:                 CBCDeathLink
    death_link_mercy:           CBCDeathLinkMercy
    

# This is where you organize your options
# Its entirely up to you how you want to organize it
c_bc_option_groups: Dict[str, List[Any]] = {
    "General Options": [EndGoal, CBCDeathLink, CBCDeathLinkMercy],
    "Randomisations Options": [RandomiseRelics, RandomiseWeapons, ProgressiveWeapons, RandomiseTarotCards, ProgressiveVirtues, RandomiseWorksOfMercy,
                                RandomiseKeyItems, RandomiseAugmentations, RandomiseClues, RandomiseEXPStatues, RandomiseShadowsFlag],
    "Trap Options": [TrapChance, BurnTrapWeight, BleedTrapWeight, PetrifyTrapWeight, PlagueTrapWeight, GoldTrapWeight, StunTrapWeight]
}
