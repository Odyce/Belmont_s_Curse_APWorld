# Castlevania: Belmont's Curse Setup Guide

> This world is in beta (v0.1.0). Read the [known issues](https://github.com/Odyce/Belmont_s_Curse_APWorld#known-issues) before playing.

## Required Software

- A legal copy of **Castlevania: Belmont's Curse** on Steam, updated to the latest version (tested with the 2026-11-19 build).
- **BepInEx 6.0.0-be.793**, the `BepInEx-Unity.IL2CPP-win-x64` build, from the [BepInEx bleeding edge builds](https://builds.bepinex.dev/projects/bepinex_be). Other versions are not supported.
- **Archipelago 0.6.x**, from the [Archipelago releases page](https://github.com/ArchipelagoMW/Archipelago/releases).
- The two files of this world, from the [project releases page](https://github.com/Odyce/Belmont_s_Curse_APWorld/releases):
  - `cvbc.apworld`, the world for Archipelago;
  - `CVBC.Client.zip`, the game client.

## Installing the game client

1. Open the game folder: in Steam, right-click the game, then *Manage > Browse local files*.
2. Extract the BepInEx archive in that folder, next to the game's `.exe`.
3. Launch the game once, then close it. The first launch with BepInEx is long (it prepares the game files), this is normal.
4. Extract `CVBC.Client.zip` in `BepInEx/plugins`. You must end up with a `BepInEx/plugins/CVBC.Client` folder containing `CVBC.Client.dll`.
5. Launch the game once more, then close it. This creates the client settings file.

## Configuring the client

Open `BepInEx/config/odyce.cvbc.client.cfg` with any text editor:

```ini
[Archipelago]
Server = localhost:38281
Slot = Rose
Password =
```

- **Server**: the address and port of the room, for example `archipelago.gg:12345`.
- **Slot**: your slot name, exactly as written in your YAML.
- **Password**: the room password, empty if there is none.

The game must be restarted after changing these settings.

## Installing the world

Double-click `cvbc.apworld`, or copy it into the `custom_worlds` folder of your Archipelago installation.

## Configuring your YAML file

### What is a YAML file and why do I need one?

See the guide on setting up a basic YAML at the Archipelago setup
guide: [Basic Multiworld Setup Guide](/tutorial/Archipelago/setup/en)

### Where do I get a YAML file?

Open the Archipelago Launcher and click **Generate Template Options**. A folder opens with a template YAML for every installed world, including `Castlevania Belmont's Curse.yaml`. Every option is explained inside.

Some options are forced off in v0.1.0, whatever your YAML says: Works of Mercy, Progressive Virtues, the First Fight with Death flag, traps and DeathLink.

## Generating and hosting a game

Follow the [Archipelago setup guide](/tutorial/Archipelago/setup/en) to generate and host a multiworld. Since this world is not part of Archipelago yet, generation must be done locally, with the `.apworld` installed.

## Playing

1. Launch the game. A small status line appears at the bottom-left of the screen.
2. **Start a new save for each new seed.** Never reuse a save from another seed or from the vanilla game.
3. Play! Checks are sent and items are received automatically.

### The status line

- **White, "AP: connected"**: everything is fine.
- **Yellow, "AP: disconnected, reconnecting..."**: the client lost the server and retries on its own. Your checks are kept on disk and sent at the next connection, you can keep playing.
- **Yellow, "Version mismatch"**: the seed was generated with another version of the world than your client. Update both to the same release.

## Troubleshooting

- **The status line never turns white**: check the three settings in the `.cfg` file, and that the room is running.
- **Something went wrong**: quit the game normally (not with Alt+F4), then open an issue on the [GitHub page](https://github.com/Odyce/Belmont_s_Curse_APWorld/issues) with the `BepInEx/LogOutput.log` file attached.
