# 2026-11-09 19:50 · The location tree is committed data the bot writes: `resource/world/zones.json`

- **Decision**: zones, their CP, exploration %, blessed flag, links (walked / map_adjacent / inside) and known ways in live in one JSON file under `resource/world/`, read and written by `sxs/policy/zones.py`. Roam surveys and fog-walk zone changes update it at runtime; builders commit it with their session. Roam picks targets and entry neighbours from it, not from one area-map reading.
- **Rationale**: mae (2026-11-09): the system should build a map of locations and explorations. One area-map reading misses zones off screen and loses % lines; per-run state in logs/roam.json was gitignored and forgot every way in. Committed data survives sessions and machines and shows its gaps (`python -m sxs zones`).
- **Alternatives considered**: keeping it under `memory-bank/game/` beside nav-graph.json (that folder is maintained by the docs thread through rules batches; runtime writes there would collide); gitignored logs/ (loses the map between machines); folding it into nav-graph.json (menus, not geography).
- **Status**: Accepted (live check pending)
