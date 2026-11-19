# Castlevania: Belmont's Curse

## Where is the options page?

The [player options page for this game](../player-options) contains all the options you need to configure and export a
config file.

## What does randomization do to this game?

Almost everything Rose can pick up becomes a check, which can hold an item for any player of the multiworld:

- Chests (silver and gold)
- Experience statues
- ATK and DEF books
- Brave and Wise Heart fragments
- Clues
- Boss rewards, both on defeat and on absorption
- The starting weapon, relic, clue and tarot card

Each item category can be shuffled or kept vanilla from the YAML: Relics, Weapons, Clues, Tarot Cards, Augmentations, Key Items & Skills and EXP Statues. A location is never removed: when a category is kept vanilla, its locations stay and give their vanilla item.

The goal is one of the three endings of the game: Bad, Neutral or True Ending.

In v0.1.0, the Works of Mercy, the four Virtues and the First Fight with Death always stay vanilla.

## Which items can be in another player's world?

Every item of a shuffled category. The Works of Mercy upgrades, the four Virtues and "The Shadow Confronted" always stay in your own world, at their vanilla place, in v0.1.0.

## When the player receives an item, what happens?

- **Inventory items** (weapons, relics, tarot cards, skills, key items): the game's own acquisition card is shown. If a menu is open, the card waits until it is closed.
- **Augmentations and experience**: Brave and Wise Heart fragments, books and experience are applied directly to Rose's stats. Fragments still merge by four, like in the vanilla game.
- **Clues**: added to your codex, without a card.

When Rose finds an item for another player, or an item that has no card in the game, an Archipelago card is shown instead, with the item name, who it is for and which game it belongs to.

## A little quirk

**Jeanne d'Arc** and **Aliénor d'Aquitaine** keep their French names everywhere in this world.
