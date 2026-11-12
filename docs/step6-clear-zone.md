# Step 6: Clear Zone, goal-directed exploration (replaces the Fog Walk)

<!-- index: Clear Zone: goal-directed exploration (every leg a named objective, progress = % or objects), which replaced the Fog Walk -->

mae, 2026-11-10 23:48: the fog walk "is candidly bad, and we need to scrap it"; the idea of fog-walking has been
poisoning navigation. Why it failed is in [fogwalk-postmortem.md](fogwalk-postmortem.md). In short: it counted
"stood on a new tile" as progress, so it could hop 1-3 tiles at a time round the same patch for minutes while the
zone's % stayed flat (run 13: 62 hops, 4 object legs; every % point came from the object legs).

This page is the design of its replacement. The flowchart is [loops/clear.md](loops/clear.md).

## The idea in four rules

1. **Every leg has a named objective.** The bot never taps "somewhere": each walk is a *leg* toward one thing it
   can name, and the readout says what it is ("leg 4: quest ring, Explore Verdantglade IX 35/100").
2. **Progress is the zone's %, or an object cleared.** Not tiles, not coordinates. A fight, a pickup, an opened
   structure, a free wheel spin or a gate opened counts as an object cleared; the zone's % (tracker or area map)
   is the real score.
3. **Objectives come from a fixed list, best first.** Each leg takes the first source that has one:

   | # | Source | Where it's read | How the leg walks |
   |---|---|---|---|
   | 1 | The zone's own Explore quest ring (R-142) | gold ring on screen, locate icon once | tap the target under the ring |
   | 2 | An object on screen we know (R-131 crops) | screen | tap it (R-155: from the next tile if the first tap does nothing) |
   | 2b | A monster group in gold brackets or under a red skull marker: it guards what lies behind it (R-139; live run 21, Lakeside Camp) | screen | tap it to fight |
   | 3 | A dot or structure anywhere on the minimap (up to 10 tiles; mae: if it shows there it is close enough) | minimap | walk along the minimap path until it is on screen, then tap it |
   | 4 | The nearest thing in our zone on the big map that counts for exploration: blue "!" statues and wheels first, then green pickups, orange monsters, gold structures and chests (R-068, R-148) | area map | tap it there, close, tap the centre |
   | 5 | A **frontier**: the nearest fog in our zone that touches walkable ground we can reach (mae, 2026-11-11) | area map | one long big-map walk there |

   Fog matters only because it hides objects, so the frontier is the last source, and it is one long leg to a
   named spot, never a string of short hops. A frontier leg must reveal or clear something. Objects it uncovers on the minimap are a
   gain. Fog that shrank round the spot (the area map's fog share there, before the walk and after) means the leg
   worked but found nothing yet: the next frontier, farther in, follows; it isn't a gain, so 4 of those in a row
   still stop the run `no_progress`. A spot whose fog didn't shrink is spent, and the next frontier aims more than
   45 degrees away from it. The spot is framed half ground, half fog (mae, 2026-11-11 18:23): on revealed ground
   of the patch we stand on, a few px back from the fog, with both in view round it, never in the middle of the
   fog: a tap on fog paths to the nearest valid tile, which can be across an impassable wall. Up to 6 frontier legs a run (run 22, Grotto Peninsula: the first frontier found no
   object, and "revealed nothing" ended all frontier legs while the zone's ground ran on north into fog).
4. **No objective, or no progress, means stop and say why.** The run ends with a named status instead of
   wandering:
   - `zone_done`: 100%, or the tracker moved on to the next zone's Explore quest.
   - `no_objective`: no source has anything left and the % isn't 100. The zone's leftovers are written to the
     location tree (what was tried, what blocked), so mae or a later run can see them.
   - `no_progress`: 4 legs in a row with no % and no object cleared. Repeating a stuck point is a defect to fix,
     not something to retry.
   - `power_gate`, `blocked_item`, `defeated`, `unknown_screen`: as before. A lost fight also writes `lost_at`
     (our power then) on the zone, and roam skips the zone until power is 0.5K higher.

## What a leg is

A leg is: an objective (source, what, where), a small budget (taps or one big-map walk), and a result:
`gain` (% up or an object cleared), `reached` (got there, nothing happened) or `failed` (didn't get there).
A spot that fails twice is skipped for the rest of the run; nothing else is put off limits (the fog walk's
growing "outside" radius once hid Zephyr Vale's last pickups).

The ring is not dropped for the whole run after a few misses any more (the fog walk stopped using it after 3).
It's asked again after every leg that changed something.

## Readout

Each leg logs one line before (`[leg 4] goal: ...`) and one after (`[leg 4] result: gain, 35% -> 37%`), plus a
run summary at the end: legs by source, % before and after, why it stopped. The runner's stall check is fed the
leg count and the %, not the coordinates, so a run that only walks gets stopped.

## What changes in the code

- New: `sxs/loops/clear.py` (`python -m sxs clear --area NAME`), the leg loop.
- New: `sxs/actions/mapnav.py`, the helpers worth keeping from `fogwalk.py`: zone check (R-140), quest ring and
  tracker counter (with the 1X -> IX fix), object taps, Gate of Elements, Lucky Wheel, HUD and own-character
  keep-outs, the big-map nearest-object picker, and a new frontier picker.
- Deleted: `fogwalk.py` (in `sxs/loops/`) and the `fogwalk` command; fog-edge tap points, fog leads and shaded-tile goals
  in `sxs/vision/minimap.py`; the new-tile watchdog.
- `sxs/loops/roam.py` calls `clear.run` per zone. When every zone in reach is blessed it ends
  `exploration_concluded` instead of a last fog walk. Zone entry stays as it is (the tree's known way in first, then
  the explored ground nearest the zone's label, R-150) but drops "then work outward to the fog".
- Rules: R-065, R-130, R-146 and the second half of R-150 described the fog walk; they're rewritten to this design.

## Not in this step

- `--farm` (fighting and taking pickups in blessed zones) goes with the fog walk; farming belongs to Gather.
- Puzzles (R-153) and the Magic Drill (R-151) stay out: a zone blocked by one ends `no_objective` with the
  blocker named.
