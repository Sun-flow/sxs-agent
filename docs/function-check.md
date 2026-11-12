# Function check: what the bot can do (2026-11-04, updated after the live shakedown)

<!-- index: What each loop does, how to run it, what it reports, whether it has run live -->

Every loop runs as `python -m sxs <loop> [options]` from the repo root (`.venv\Scripts\python`). Each one logs
mae's banner (`[Running X Loop]` / `[Goal]` / `[End condition]`), and ends with one JSON line such as
`{"loop": "explore", "status": "complete", "ok": true, "seconds": 84}`. Exit code 0 = ok, 1 = needs a look,
2 = refused. Every run is capped at `--budget` (default 120 s, status `over_budget`), and loops that report
progress also stop as `stalled` after `--stall` seconds (default 60) with no change. No module calls a model.

## Loops

| Command | What it does | Ends when | Ran live before? |
|---|---|---|---|
| `upgrade` | Follows every red "!" on the Character screen: banded gear enhance, Resonance, skill Quick Upgrade, technique ascension, class levels, rank goals | no badge left | Yes, partly (skills/class/rank passes were done by hand) |
| `gearswap` | New: equips the better piece wherever a gear slot shows "!"; power compare decides; separate from enhancing; also a daily step | no flagged slot left | Not yet (the old blind version inside `strengthen` has) |
| `strengthen` | Cart loot, rank first at the level cap, Aeonic Gacha x10, Workbench relics, better gear and charms, Upgrade loop (`--only` picks steps) | every step once, each with its own budget | Yes for the old order; the 2026-11-11 order not yet |
| `gacha` | Aeonic Gacha: ticket counter, Draw x10 on every tier with a full x10 of badges (never x1, short xN or Dawnium), Goals | no tier can pay a full x10 | Not yet (`docs/strengthen-live-test-plan.md`) |
| `relics` | Workbench: activate new relics, ascend with own shards, enhance in bands with Chrono Sand (never Replace) | short, or 30 presses | Not yet; needs the Workbench template first |
| `daily` | Sign-in, Mall gifts, Vendor stamina, Cart, bed EXP, Growth Trial, Fantasia Ascent, quests, guild x3, gather, strengthen (120 s per step) | every step tried once | Yes, all steps |
| `explore` | Follows the quest tracker marker; fights, cards, dialogue, healing, unsticking | tracker 100/100, no marker, unknown screen | Yes (`--chain` played the quest line) |
| `clear` | Clears one zone: each leg toward a named objective (quest ring, objects, big map, fog frontier) | zone_done, no_objective, no_progress | No (replaced the fog walk 2026-11-10; to be tested live) |
| `roam` | Picks unexplored areas under our power on the area map, walks there, clears them, blesses statues | no eligible area left | Yes (Damp Woods) |
| `goto` | Walks to an area via the area map | arrived / failed | Yes |
| `gather` | Spends stamina above 70 on the priority material via Map Exploration; `--harvest` picks Bellflowers | stamina at 70 | Yes for ore; harvest detector weak |
| `tower` | Fantasia Ascent daily climb, Auto Challenge, no retries | first loss | Yes |
| `guild` | Donate (max 2, by the game's counter), Forge AFK slot, Conquest attempts | each step done | Donate/AFK yes; Conquest with attempts left not yet |
| `mall` | Free gift box on each Mall page, never a price | pages checked | Yes |
| `vendor` | Vault free x30 stamina only | claimed / not there | ❓ not sure |
| `tutorial` | Taps the yellow tutorial highlight | nothing highlighted | Yes |
| `pray` | x10 skill pulls, only with `--pulls N --handler-approved` (never called by other loops) | pulls done | Yes, by request |

## Tools

`python -m sxs state | screenshot | tap X Y | swipe | back | start | stop | capture NAME | watch`;
`python -m sxs see badges|minimap|gift [FRAME]` runs one detector; `python -m sxs bank | label` manages
unlabelled screenshots; `scripts/probe.py`. Offline checks: `tests/check_repo.py`, `tests/check_loops.py`,
`tests/check_states_offline.py`, `tests/check_rewards_offline.py`, `tests/check_upgrade_logic.py`,
`scripts/check-rules.py`.

## Fight threshold

`sxs/policy/fights.py`: a recommended power up to 1.25x ours is worth fighting (mae). `roam` uses it to pick areas.
Gates of Power still open only once our power reaches their number.

## Live shakedown results (2026-11-04 evening)

| Loop | Result |
|---|---|
| `upgrade` | Works. Goals pass first; ascended Ice Spike and Elemental Mystery from their shards (18.5K to 18.8K). |
| `gearswap` | Works. Compared all 4 slots, kept every piece (equipped ones stronger). |
| `daily` | Works after fixes: sign-in, Growth Trial, quests, Conquest (both attempts), Ironvein, Mall halves, Vendor, guild donate/AFK. |
| `tower` | Works after fixes: 25% check, starts Auto Challenge, which climbs in the background (F6 to F24). |
| `explore` | Works: Verdantglade III 0 to 73/100 in four 2-minute runs. |
| `roam` / `clear` | Ends cleanly, but can't walk into Verdantglade III (the only area left); the quest route can. |
| `gather` | Picked 2 ore, then stopped as stuck when panning found nothing. |
