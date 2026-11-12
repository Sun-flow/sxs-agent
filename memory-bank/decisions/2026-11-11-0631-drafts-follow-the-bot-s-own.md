# 2026-11-11 06:31 · Drafts follow the bot's own readers; removed drafts are remembered

- **Decision**: the pre-labeller drafts an area-map object only where `sxs/vision/area_map.objects()` reports one, never drafts item symbols on map areas, and skips anything in `docs/screens/rejected.json` (drafts mae removed). Review is one class at a time in the labeler's grid.
- **Rationale**: a separate copy of the reader drifted and drafted red text, badges and the zoom knob; forgotten removals came back on every re-draft (`docs/labeler-diagnosis.md`).
- **Alternatives considered**: tuning the copy's thresholds (would drift again); deleting "Confirm all drafts" (kept, but it now confirms only the shown category).
