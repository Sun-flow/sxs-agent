# Progress tracker

mae, 2026-11-04: "a script for tracking daily progress. Every session it should record CP changes, gear
improvements, relics, resource pools with daily delta, overworld zones cleared today, Fantasia Ascent progress, Cart
upgrades, skill level change as bands, and other statistics worth tracking."

Code: `sxs/loops/progress.py` (loop and report), `sxs/vision/stats.py` (screen readers, never tap),
`sxs/core/records.py` (files). Check: `tests/check_progress.py`.

## How it runs

    python -m sxs progress                  # read the screens, save a snapshot, write the day's report
    python -m sxs progress --only hud,profile
    python -m sxs progress --guild-shop     # also read Guild Tokens (opens the Guild Shop, taps no price)
    python -m sxs report [--day 2026-11-04] # report from saved snapshots, no emulator

The daily loop ends with a `progress` step (home, profile, Journal), so every daily run leaves a snapshot.
Everything is read only: the route taps the portrait, the area above the profile to close it, the bottom nav,
the guild island's building labels and the back arrow. No claim, upgrade or price button.

Files, per server day (resets 13:00 UTC), on the game PC under `logs/` (gitignored):

| File | Holds |
|---|---|
| `logs/progress/<day>.json` | `snapshots` (what the progress loop read) and `notes` (readings other loops made on the way) |
| `logs/progress/<day>.md` | The day's report, rewritten after each snapshot |
| `logs/runs.jsonl` | Every loop run's JSON readout and exit code (written by the loop runner for every loop) |

The report compares the newest reading of the day with the last reading of the previous day. A failed reading is
"not read", never a change; the readout's `not_read` lists them.

## Where each stat comes from

| Stat (mae's list) | Screen | Reader | State |
|---|---|---|---|
| CP (power), level | Home HUD; player profile | `read_hud`, `read_profile` | Reads |
| Gear +N per piece, as a band | Player profile, Equip row | `read_profile` | Reads. A lower level on a slot = a new piece equipped |
| Skills as bands (techniques, charms) | Player profile, Technique / Charm rows | `read_profile`, `band` | Reads; empty slots left out |
| Class, class level, rank | Player profile | `read_profile` | Reads |
| Rolla, Dawnium, stamina | Top bar (home, Journal) | `read_topbar` | Reads. Over 1,000 the bar rounds (43.2K) |
| Guild Tokens | Guild Shop, top right | `read_guild_tokens` | Reads with `--guild-shop` (opt in: the Shop is mae's to open) |
| Guild level, members, activeness | Guild Lobby | `read_guild_lobby` | Reads |
| Fantasia Ascent floor | Journal card ("Moonveil Woods 6"); tower wins | `read_journal`; tower loop note | Reads. ❓ the card's number is taken as the next floor (6 with F1-5 cleared) |
| Zones cleared today, exploration % | Area map | Roam Loop's `read_areas` | Reads the areas in view; 100 = no % shown |
| Cart levels | Cart panel | `read_cart`, noted by the daily cart step | Only when the panel opens (loot ready). ❓ row order assumed Rolla, wood, stone, ore, essence, gear |
| Iron Hammers used | Ironvein Pit | daily `material_realms` note | Reads |
| Relics activated / ascended | not unlocked yet | none | **Needs a route** once relics unlock |
| Lumium, Material Realm tools (pickaxes, shovels, gloves) | the bag | none | **Needs a route**: the bag hasn't been found yet |

## Other stats worth tracking (recommendations)

Already in the report from `logs/runs.jsonl`: runs per loop with outcomes, exit codes (ok / needs a look /
refused), daily step results (bed EXP, donations, Conquest, sign-in...), gather pickups and the stamina they cost.

Worth adding, cheapest first:

1. **Stamina spent vs regenerated**: snapshots before and after gather, plus +5/h (R-107), show wasted stamina (cap hits).
2. **XP to next level**: the Character screen's "80/90" under the level bar; days to the next rank gate (Lv 30).
3. **Stellatie and pulls**: Stellatie on the Prayer screen; pulls from the pray loop's readout (handler-approved only).
4. **Rank materials**: Bellflowers and the Apprentice III flower (count on the rank screen), for the next rank-up.
5. **Battle Essence, ore, sand** (the upgrade materials): shown on the skill page and Enhance Gear top bars.
6. **Guild donations and Conquest tries used**: the guild loop already reads both counters; note them.
7. **Unknown screens per day**: count of files in `captures/unknown/` per day, a stuck-point trend.
8. **Time per loop**: `seconds` in each readout, to spot loops creeping past the 1-2 minute rule.
