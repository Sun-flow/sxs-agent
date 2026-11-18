# Research leads: what to look up next

<!-- index: Read when you have time for more research: sources not yet read, facts no source gave, and Chinese-version forecasts left unfinished on 2026-11-18 -->

> **Summary:** The research of 2026-11-18 stopped on purpose before everything was read. This page lists what is
> left, most useful first, so a later session can pick one line and go. Nothing here is a fact yet.
> **Applies:** all seasons
> **Related:** [Source register](README.md), [provenance](provenance.md), [conflicts](../conflicts.md),
> [Future content](../systems/future-content.md), [CN version notes](notes/cn-version.md)

## Facts to read off our own account (cheapest, most reliable)

These settle open questions with one screenshot each; they need a live session, so they wait for mae's go-ahead.

| Lead | Why it matters | Where it goes |
|---|---|---|
| Our server's day number (and so its day 1) | Every season date in [seasons](../systems/seasons.md) and [season-schedule.json](../data/season-schedule.json) is counted in server days | `strategy/season-playbook.md`, `data/season-schedule.json` |
| Dawnium price of one pull and of a 10x, per banner | No source states it; the spend plan needs it | `systems/gacha.md`, `strategy/dawnium-plan.md` |
| Arena currency name, Arena Shop stock, extra-fight price ladder | Two ladders disagree | `systems/arena-and-pvp.md`, `data/shops.json` |
| Kingdom merchant currencies per kingdom ("Feathers", "Alloy" are unplaced leads) | Shop planning | `systems/currencies.md`, `systems/world-and-kingdoms.md` |
| Primal Forge prices and maximum level; Grand Treasure Hunt item prices | Not in any source | `systems/shops.md`, `systems/events.md` |
| Fantomon unlock at Lv 50 or Lv 51; Vendor Booth at Lv 18 or 20; Guild at Lv 15 or 20 | Sources and rules disagree by a level or two | `systems/levels-and-unlocks.md`, `data/unlocks.json` |
| Names of the six gear quality colours; Kingdom Rank names against eog's band names | Tables can't be joined without them | `systems/gear.md`, `systems/kingdom-rank.md` |
| Sand realm tool name ("shovel", "Crystal Shovel") | Only a low-tier lead | `systems/material-realms.md` |

## Sources not read yet

| Lead | State | How to continue |
|---|---|---|
| Prydwen (S-05), `www.prydwen.gg/sword-x-staff` | Shows a Cloudflare bot check; not read and not bypassed. eog says its Fantomon and companion rows come from Prydwen | mae saves the pages from a browser and uploads them; or wait until the site opens |
| zeroluck.gg (S-80) | Read only through a page-reading tool; direct requests get 404, so no raw copy and no item database | Re-run `python3 scripts/kb_fetch.py zeroluck` now and then; ask the site for its data source |
| lootandwaifus.com (S-86) | Section removed (all 404) | Nothing to do unless it returns |
| Miraheze / other fan wikis, Reddit threads, Discord pins | Seen in search results only | Add hosts to the cloud environment, then extend `kb_fetch.py`'s `SITES` table |
| Official site posts after 2026-06-05 | None existed on 2026-11-18 | `python3 scripts/kb_fetch.py official` picks up new posts |
| Fandom wiki | 55 pages snapshotted | Re-run `python3 scripts/kb_fetch.py fandom` and diff the manifest |

## Chinese-version forecast (stopped part-way)

[Future content](../systems/future-content.md), [cn-version.md](notes/cn-version.md), `data/class-tiers-cn.json` and
`data/skills-cn.json` are kept as they were when the research was stopped. They are forecasts (tier C at best).

| Lead | State |
|---|---|
| Warrior line (Berserker, Paladin and later) and Duelist/Knight at tiers 5 to 8 | Only Mage-line tiers were read in depth; other lines have a few posts |
| Tier 8 and tier 9 skills | Leak posts only, with speculation |
| Season 4 to 6 day numbers | GameKee's timeline was written early and is about 14 days off for Season 4; needs a second source |
| Fantomon Sync, Bond Adventure, third gem socket details | One or two player posts each |
| Whether the global game keeps matching the Chinese calendar after Season 2 | Check when Season 3 opens on a global server |
| Re-read list | The URLs at the end of [cn-version.md](notes/cn-version.md), once per season |

## Facts no source gave

Kept as ❓ on the pages; listed here so they are not searched for twice without a new source.

- Temporal Crystal sources; Affection banner contents; Arena reward tables; element type of each Fantomon.
- Monsters by kingdom (`data/monster-list.json` has the type only).
- Which gem fusion step each success rate applies to.
- About ten skills on the class pages with no match in `data/skill-database.json` (for example Afflicting Stars, Holy Redemption): probably eog's own translations differ.

## Housekeeping

- Bulk tables in `knowledge/data/` (relic, recipe, skill, map-point databases) were read from eog.gg, whose robots.txt allows reading and signals reference use. If mae prefers not to keep third-party tables in the repo, delete those files and keep the notes; `_meta.source` in each file names its origin.
- Several source tags point at the same site because each research pass registered the pages it read. Merging tags is cosmetic and can wait.
