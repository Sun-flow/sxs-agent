# Knowledge base: Sword x Staff

<!-- index: Start here: what the knowledge base is, how to find a term, a system, a class, a plan or a number, and how it is kept honest -->

> **Summary:** a reference and strategy guide for the game, built from two guides by a top-ranked player, the
> public wikis, and our own observed rules. Use it to find out what a thing is ([glossary](glossary.md)), how a
> system works (`systems/`), how a class is built (`classes/`), and what to do next and why (`strategy/`).
> It is reference, not orders: the bot acts on `memory-bank/game/rules/`. Where advice and rules differ, see
> [conflicts](conflicts.md).

## Find something

| I want to know | Go to |
|---|---|
| What a word on screen or in a guide means | [glossary.md](glossary.md) (`python3 scripts/kb_check.py --terms` lists every term) |
| What to do next, today, this week, this season | [strategy/README.md](strategy/README.md) |
| How a system works and its numbers | the `systems/` table below |
| How to build a class; which class next | [systems/classes-overview.md](systems/classes-overview.md), then `classes/` |
| A table a program can load | `data/*.json` (list below) |
| Where a fact came from and how far to trust it | [sources/README.md](sources/README.md) |
| What later seasons will bring | [systems/future-content.md](systems/future-content.md) |
| Whether a guide disagrees with our rules | [conflicts.md](conflicts.md) |
| How pages are written | [CONVENTIONS.md](CONVENTIONS.md) |

The full page index is built from the pages: `python3 scripts/kb_check.py --index`.

## Systems

| Area | Pages |
|---|---|
| Character | [classes-overview](systems/classes-overview.md), [skills](systems/skills.md), [gear](systems/gear.md), [gems](systems/gems.md), [levels-and-unlocks](systems/levels-and-unlocks.md), [kingdom-rank](systems/kingdom-rank.md) |
| Permanent collections | [relics](systems/relics.md), [fantomons](systems/fantomons.md), [companions](systems/companions.md), [gacha](systems/gacha.md), [astral-pact](systems/astral-pact.md) |
| Economy | [currencies](systems/currencies.md), [shops](systems/shops.md), [material-realms](systems/material-realms.md), [stamina](systems/stamina.md), [commissions](systems/commissions.md), [cart-and-home](systems/cart-and-home.md), [auction-house](systems/auction-house.md), [cooking-and-dishes](systems/cooking-and-dishes.md), [codes](systems/codes.md) |
| World | [world-and-kingdoms](systems/world-and-kingdoms.md), [exploration](systems/exploration.md), [goddess-statues](systems/goddess-statues.md), [monsters](systems/monsters.md) |
| Content | [dungeons](systems/dungeons.md), [towers](systems/towers.md), [arena-and-pvp](systems/arena-and-pvp.md), [events](systems/events.md), [guild](systems/guild.md) |
| Time | [seasons](systems/seasons.md), [future-content](systems/future-content.md) |

## Classes

| Tier | Warrior line | Mage line |
|---|---|---|
| 1 | [Warrior](classes/warrior.md) | [Mage](classes/mage.md) |
| 2 (Lv 44) | [Duelist](classes/duelist.md), [Knight](classes/knight.md) | [Sorcerer](classes/sorcerer.md), [Sage](classes/sage.md) |
| 3 | [Berserker](classes/berserker.md), [Paladin](classes/paladin.md) | [Archmage](classes/archmage.md), [Arcanist](classes/arcanist.md) |
| 4 (Lv 106) and later | [Tier 4](classes/tier-4.md) | [Tier 4](classes/tier-4.md) |

## Data files

Run `ls knowledge/data/`; each file starts with `_meta` (description, sources, date). The main ones: classes,
skills, currencies, shops, dungeons, events, season-schedule, dawnium-daily-plan, unlocks, kingdoms, relics,
fantomons, companions, gems.

## How it is kept honest

- Every fact carries a source tag; tiers A to D say how far to trust it; unknowns are marked ❓ ([CONVENTIONS](CONVENTIONS.md)).
- `python3 scripts/kb_check.py` checks links, index lines, source tags, rule IDs and data files.
- `python3 scripts/kb_fetch.py all` refreshes the local copies of the public wikis ([sources](sources/README.md)).
- When the bot sees something in game that settles a ❓, record it as a rule in `memory-bank/game/rules/` and
  update the page to cite the rule.

## What is weak

- Numbers past the early game come from other servers and, for later seasons, from the Chinese version.
- Our server's day 1 is unknown, so schedules are in server days, not dates.
- Prydwen's guides were not read (bot check). mae can upload saved pages to add them.
