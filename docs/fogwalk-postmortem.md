# Fog Walk post-mortem (2026-11-10)

mae (23:48Z): the fog-walk approach is bad and is being scrapped; a new thread designs the replacement navigation. This note lists where it lives, what leans on it, what went wrong, and what is worth keeping.

## What went wrong

- **Wrong progress signal.** The watchdog counts "stood on a tile not stood on this run" as progress. In an unexplored zone the % only rises from objects (R-143), so a walk can reach new tiles forever while the % stays flat. Run 13 (Verdantglade IX): 62 short walk taps against 4 object legs; 18:44-18:48 every tap stayed in a 7x9-tile box (129-135, 55-63).
- **Greedy nearest target, short legs.** `minimap_target` picks the nearest unvisited "fog lead" tile (walkable, touching fog) and taps at most 4 tiles along the path. The nearest lead is nearly always 1-3 tiles away, so the walk hops round its own neighbourhood.
- **The quest ring is dropped for the run** after 3 ring steps that don't move the counter (`QUEST_FAILS_MAX`), even though the ring was the best goal source every time it worked (VIII 13 -> 66% today).
- **Zone checks by OCR on every step**: misreads ("Croll Lair", "Verdantglade1X", "/erdantglade") ended or bounced walks again and again; each fix was a special case.
- **Off-limits spots grow without limit** (`outside`): a dismissed card or a crossing puts a radius off limits, which once hid the last pickups of Zephyr Vale beside its statue.
- The loop is one 600-line function (`walk`) with flags (`objects_done`, `map_tries`, `fog_worked`, `quest_fails`, `still`) that interact in ways that are hard to predict or read in a log.

## Where it lives

`fogwalk.py` in `sxs/loops/` (~1130 lines; deleted 2026-11-11, replaced by Clear Zone, `docs/step6-clear-zone.md`):

| Function | What it does | Keep? |
|---|---|---|
| `walk` (526-1110) | the loop: card handling, zone checks, quest ring, minimap targets, big-map walks, fog leads, watchdog | **delete**; salvage the card/screen branches (battle wait, dialogue Leave, rewards, Gate of Elements, Lucky Wheel, puzzle Leave, Timed Packs) into the new navigator |
| `minimap_target` (140) | nearest object, else gold building, else fog lead, else shaded tile | delete the fog-lead/shaded parts; object-first planning may be reused |
| `fog_edge_target` (56), `walkable_at`, `fog_worked` | fog-edge picking | delete |
| `quest_counter`, `_explore_quest`, `quest_moved_on` | read "Explore <zone> N/100" (with the 1X -> IX fix) | **keep**: the % is the real progress signal |
| `find_quest_ring`, `quest_step` | follow the gold quest ring (R-142) | **keep**: best goal source |
| `tap_object` | tap an object; walk beside it if the tap didn't move us (R-155) | keep |
| `elemental_gate`, `lucky_wheel_free` | Gate of Wind with companions; free first wheel spin | keep |
| `off_hud`, `off_me` | keep taps out of the HUD and off our own character (R-158, R-142) | keep |
| `zone_here`, `zone_by_map`, `map_labels`, `zone_picker` | zone by minimap name then big-map dot (R-140); nearest object on the area map | keep `zone_here`/`map_labels`; `zone_picker` is the useful "nearest object on the big map" (R-068) |

`sxs/vision/minimap.py`: `fog_lead` / `walk_unexplored` goal kinds, `path_to_nearest`, border detection (`border_mask`, `shade_border`). The minimap reader and dot classes are worth keeping; the fog-lead goals go.

## What depends on it

- `sxs/loops/roam.py`: `approach()` (R-150 entrance: "explored ground nearest the zone", which picked Drasilgard for VIII when the real entrance was VII's south edge), `run()` calls `fogwalk.walk` per zone and for "leftover ground", `bless_near` uses `quest_step`, the survey uses `map_labels`. Roam's survey, location tree (`resource/world/zones.json`: entries, links, blocked, objectives) and statue blessing are independent of the fog walk and worth keeping.
- Rules: R-065 (walk the fog edge), R-130 (fog-walk toward the light/striped edge), R-146 (never tap fog: tap ground beside it), R-150 (entrance then outward to the fog), R-132 border handling, R-143. R-065/R-130/R-146 and the second half of R-150 describe the fog walk and would be retired or rewritten with the new design.
- Docs: `docs/loops/fogwalk.md`, `docs/loops/roam.md`, `docs/loops/explore.md` (fog-edge fallback), `docs/step3-explore.md`.
- `scripts/tap_trace.py` (fog walk or roam with every tap logged and the frame saved): keep, retarget at the new loop. It found most of today's bugs.
- `sxs/loops/__init__.py` registers the `fogwalk` CLI loop.

## What worked today (to carry over)

- Quest ring first (VIII 13 -> 66%), objects by the big map (R-068: tap it on the area map, close, tap the middle), Gate of Elements with companions, statue cards by rule, the % read from the tracker and the area-map label.
- Ways in found by looking at the area map: VIII from VII's south edge (102,110), Zephyr Vale through the Gate of Wind at (153,109), Monolith Ruins I from V at (151,122). A navigator that reads the area map for the zone's border and explored neighbours would have found these without wandering.
