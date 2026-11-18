# Knowledge base conventions

<!-- index: How every file in knowledge/ is written: page template, source tags, confidence marks, links, data files -->

Every file in `knowledge/` follows this page, so an agent can trust the same marks everywhere.

## What goes where

| Folder | Holds | Not for |
|---|---|---|
| `glossary.md` | Every game term, one line each, linking to the page that explains it | Explanations longer than two lines |
| `systems/` | One page per game system: what it is, how it works, numbers, how it links to other systems | Advice (goes to `strategy/`) |
| `classes/` | One page per class: role, skills, builds, stat priorities | |
| `strategy/` | What to do and in what order: roadmaps, routines, spending plans, decision tables | Raw facts without a decision |
| `data/` | Machine-readable tables (JSON) that code or an agent can load | Prose |
| `sources/` | Where facts come from: the source register, guide transcriptions, fetched wiki text | Our own conclusions |
| `conflicts.md` | Places where a guide disagrees with a rule in `memory-bank/game/rules/` or with another source | |

Rules of the world the bot acts on (tap positions, never-dos) stay in `memory-bank/game/rules/`. Link to a rule by
its ID (`R-043`); never copy its text here. This folder is reference and strategy; the rules folder is binding.

## Page template

```
# Title

<!-- index: one line saying when to read this page -->

> **Summary:** two or three sentences an agent can act on without reading further.
> **Applies:** all seasons | Season 1 | Season 2+ | early game (Lv 1-60) ...
> **Related:** [Other page](../systems/other.md), rule R-NNN

## Sections...

## Open questions
- ❓ what is unknown, and what would confirm it

## Sources
- [S-01] page or section used
```

## Source tags and confidence

Every non-obvious fact carries a source tag in square brackets at the end of its sentence, bullet or table row,
e.g. `Fantomons unlock at Lv 51 [S-03]`. Tags are defined in `sources/README.md`. Reliability tiers:

| Tier | Meaning | Tags |
|---|---|---|
| A | Seen in our own game by the bot or stated by mae | `[R-NNN]` (a rule ID) |
| B | Written by experienced players who play the live game | `[S-01]`, `[S-02]` (the SOF guides) |
| C | Community wiki, written near launch (may be outdated) | `[S-03]` (Fandom), `[S-05]` (Prydwen, via search results only) |
| D | SEO or auto-written guide sites: often vague, sometimes wrong, sometimes using wrong item names | `[S-04]` (sword-x-staff.wiki) and others in the register |

- A fact with only a tier D source is marked ❓ unless a higher tier agrees.
- When sources disagree, state both and which one this page follows; add a row to `conflicts.md`.
- Never invent a number. Unknown values are `❓` in prose and `null` in JSON.
- Game terms are written exactly as the game spells them (Rolla, Dawnium, Stellatie, Fantomon). A source's
  misspelling is noted once in `glossary.md` as an alias.
- No player names, guild names or account names, except guide authors credited in `sources/README.md`.

## Links

Relative markdown links between pages. `python3 scripts/kb_check.py` fails on a broken link, a missing index line,
an undefined source tag, or a JSON file that doesn't parse.

## Data files

`data/*.json`: an object with `"_meta": {"description", "sources", "updated"}` and one list of records. Every
record has a stable lowercase `id` and a `sources` list. New records are appended; ids are never reused.
