# 2026-11-11 00:01 · Exploration moves by named objectives; the Fog Walk is scrapped (mae)

- **Decision**: exploration (`python -m sxs clear`, called by roam) walks in legs, each toward an objective it can name: the zone's quest ring, a known object on screen, a minimap object a few tiles away, the nearest object in the zone on the big map, then a fog frontier (one long big-map walk). Progress is the zone's % or an object cleared, never a new tile. No objective left, or 4 legs without progress, ends the run with a named status.
- **Rationale**: mae, 2026-11-10 23:48: "the idea of fog-walk has been poisoning our navigation". Counting new tiles as progress let the walk hop round one patch for minutes (run 13: 62 hops, 4 object legs; every % from objects, R-143). Her standing principle: consistent trackable progress, never wander. Design: `docs/step6-clear-zone.md`; post-mortem: `docs/fogwalk-postmortem.md`.
- **Alternatives considered**: patching the fog walk (progress by %, ring first, longer frontier legs), as the exploration thread first proposed; rejected because mae asked for the approach to be replaced, not layered on.
- **Status**: Accepted
