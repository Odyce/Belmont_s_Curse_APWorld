# Project vision

This file explains in details what I want the Belmont's Curse world to be, and the choices already made. If you want to propose something different, open an "Idea / improvement" issue, I'm open to discussion.

The source of truth for every item, location, ID and rule is the inventory spreadsheet ([`inventory_cvbc.xlsx`](inventory_cvbc.xlsx)). The code must follow it, not the other way. Part of that sheet was updated following a file named `Belmonts Curse AP Logic.xlsx`, you can find it on the discord channel.

## How the project is split

The project has two halves that only share item and location IDs:

- **The APWorld** (Python, `worlds/cvbc`): items, locations, regions, rules and options. It is only used to generate seeds.
- **The client** (C#, a BepInEx 6 plugin, the game is a Unity IL2CPP build): it runs inside the game, turns game events into checks, gives the received items to Rose and reports the goal.

The game name must be exactly `Castlevania: Belmont's Curse` on both sides.

## Items

8 categories, each one can be shuffled or kept vanilla from the YAML:

| Category | Count | Notes |
| --- | --- | --- |
| Relics | 42 | Silver chests |
| Weapons | 28 | 7 groups of 4 tiers, gold chests and boss events |
| Clues | 40 | Ghosts, Spy Statues, notes and steles |
| Tarot Cards | 16 | A card and its spell are the same thing: getting the card unlocks the spell |
| Augmentations | 76 | 24 Brave Heart Fragments (HP), 24 Wise Heart Fragments (MP), 14 ATK Books, 14 DEF Books |
| Work of Mercy upgrades | 44 | The upgrades of each card's spell, completed through the cards challenges |
| Key Items & Skills | 19 | Arcane Whip, Holy Light, Aerial Rush, Smash, Double Jump, the gem keys, the Virtues, The Shadow Confronted, Mirror Kneel, the three Mammon eyes... |
| EXP Statues | 147 | Filler |

Rules about the item pool:

- **No location is ever removed.** A category that is not shuffled keeps its locations, with the vanilla item locked on them.
- One AP ID per item name (all copies share it), one AP ID per location. IDs never change once released.
- All shuffled categories mix freely: a weapon can be in a statue, a relic in somebody else's game.

## Locations

Every check of the game becomes a location: chests, unique rewards, boss and NPC absorptions, clues, augmentations, EXP statues, the Virtue bells, and the Works of Mercy.

Works of Mercy are challenges the player can do at any moment, so they don't have a place on the map. They still count as locations: the client watches their flag and sends the check, without giving the vanilla upgrade. In the logic they hang on a virtual region and only need their card (plus what the challenge itself needs).

## Logic

- No tricks, no glitches in the logic for now.
- Progression mostly rests on the 5 skills, the gem keys, The Shadow Confronted, Mirror Kneel, Brauner's Paintbrush and a few Tarot cards.
- Saint Louis is a scripted interaction. His scales need at least 320 HP + MP: the game starts at 100 HP + 100 MP and every full heart (4 fragments) gives +20, so the rule is 24 Heart Fragments, HP and MP mixed.
- Some boss rooms can softlock the player right after without the skill the boss gives: Leon (Arcane Whip), Jeanne d'Arc (Holy Light), Carmilla (Aerial Rush), Talos (Smash), Death (Double Jump). In the randomizer, entering these rooms requires the skill, and the client will block the door until the player has it.

## Goals

The YAML lets the player choose one of three goals:

- **Bad Ending**: enter the Master's Quarter from the Clock Tower without disarming the Death Trap with The Shadow.
- **Neutral Ending**: defeat Dracula without doing anything during the scripted window.
- **True Ending**: defeat Dracula, then use The Self during that window. The Self needs the four Virtues (one trial per card: The Warrior, The Whisperer, The Judge, The Sage), then the Doppelganger.

An ending is not final in the game: a save can go on and reach another one. The client only reports the ending chosen as goal.

## Options

| Option | Effect |
| --- | --- |
| Shuffle <category> (x8) | Off: the category stays vanilla |
| Goal | Bad / Neutral / True Ending |
| Progressive Weapons | One "Progressive <group>" item per weapon group instead of the 28 named weapons |
| Shuffle Works of Mercy | Off: the four Virtues and The Self stay vanilla too |
| Progressive Virtues | 5 "Progressive Virtue": the four Virtues, then The Self, to make the True Ending harder to reach |
| Shuffle The Shadow's Flag | On by default: the first fight against Death becomes a check and "The Shadow Confronted" is shuffled |
| Traps | Trap chance + a weight for each status effect (Burn, Bleed, Petrify, Plague...) |
| DeathLink | With 1 to 5 deaths before it triggers |
| Later | Enemy randomizer (with a list of enemies never shuffled), boss room randomizer (the whole room is swapped), maybe area entrance randomizer, possibly the library puzzles randomizer (really unsure about the feasability of that one, but I like the idea) |

## Client

- Connection menu, send checks, receive items.
- The index of received items is stored in the save, so nothing is given twice.
- Work of Mercy upgrades received before their card are stored and applied when the card arrives.
- The Virtues are game flags, not inventory items: the client sends the check at the end of a trial without setting the flag, and sets it when the item is received.
- One zip with BepInEx, the plugin and the config, to unpack in the game folder.

## Names

Jeanne d'Arc and Aliénor d'Aquitaine keep their French names everywhere (see the README). Please respect it.
