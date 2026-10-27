# Contributing

Thanks for your interest in the project! Here is how to help without stepping on each other's toes.

## Issues first

Before writing code, there should be an issue for it. There are a few relevant templates, including:

- **Bug report**: something crashes or behaves wrong (generation, client, docs).
- **Logic / data error**: a location in the wrong area, a missing requirement, a wrong item name, a wrong vanilla item...
- **Idea / improvement**: a new option, a different design choice, anything you would like to see.
- **Task**: a concrete piece of work from the roadmap, mainly for the people already working on it.

If you want to work on an issue, say it in a comment so two people don't do the same thing.

## Branches and pull requests

`main` must always generate. I'm the only one who merges in it, everything else goes through pull requests.

1. Click **Fork** on GitHub to get your own copy of the repository, then clone your fork.
2. Keep your fork up to date with this repository (the **Sync fork** button on GitHub, then `git pull`).
3. Create a branch in your fork, with a short name:
   - `feature/<thing>` for something new (`feature/progressive-weapons`)
   - `fix/<thing>` for a bug (`fix/notre-dame-rule`)
   - `data/<thing>` for items, locations or rules changes (`data/clock-tower-statues`)
   - `docs/<thing>` for documentation
4. Commit small and often, with clear messages, I won't ask any specific commit name convention as I tend to be unreliable myself in that regard, just keep it clear (`cvbc: add Clock Tower regions`).
5. Push your branch to your fork and open a pull request to `main` of this repository. Link the issue in the description (`Closes #12`).
6. I review it, maybe ask for some changes, then merge it (or explain why not).

## Before opening a pull request

- Generate at least one seed with a test YAML: `python Generate.py` (the YAML goes in `Players/`).
- Run the tests scoped to our world (`pip install pytest pytest-subtests` first): `AP_TEST_WORLDS=cvbc pytest` (on Windows PowerShell: `$env:AP_TEST_WORLDS="cvbc"; pytest`).
- Follow the Archipelago code style (PEP 8, see [docs/style.md](docs/style.md)).

## The rules that matter

- **The spreadsheet is the source of truth.** Names, IDs and rules come from `inventory_cvbc.xlsx`. If you change one in the code, change it in the spreadsheet too, in the same pull request.
- **Never change an AP ID** once it is used. New items and locations take the next free ID in their category range.
- **Names are used as-is** in the Python files and the client: exact spelling, apostrophes included.
- **No location is removed**, whatever the options. Not shuffled means vanilla, not deleted.
- **Jeanne d'Arc and Aliénor d'Aquitaine** stay in French, everywhere. It's a little quirk of mine, please respect it. (Sorry, I feel like I keep repeating it, but I really wish for it to stay that way)

## Talking

For quick questions, the Archipelago Discord thread of the project is the best place. For anything that should be remembered, use an issue.
