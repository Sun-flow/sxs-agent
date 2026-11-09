# resource: MaaFramework bundle

| Path | Holds |
|---|---|
| `pipeline/state.json` | `State.*` screen detectors; `State.Detect` lists them in priority order (first hit wins) |
| `pipeline/explore.json`, `home.json`, `upgrade.json`, `tutorial.json` | Template/OCR nodes used by the loops (`Explore.*`, `Gather.*`, `Home.*`, `Guild.*`, `Tutorial.*`) |
| `image/<group>/` | Templates the pipelines and code match (paths are relative to `image/`) |
| `image/labels/` | Crops of boxes mae drew in the labeler (`python -m sxs labeler`), one folder per screen, `manifest.json` (`sxs/core/labels.py`) |
| `policy/cards.json` | Card/popup decision rules (`sxs/policy/decide.py`) |
| `policy/gather.json` | Material priority for the Gather Loop |
| `world/zones.json` | The location tree: zones, CP, exploration %, blessed, connections, ways in, open questions. Read and written by `sxs/policy/zones.py` (roam surveys and fog-walk crossings update it; commit it with the session). `python -m sxs zones` prints it |
| `model/ocr/` | OCR models (fetched by `scripts/fetch-ocr-models.py`, gitignored except `keys.txt`) |

Reference screenshots are not here: they live in `docs/screens/`. A template made from a screenshot names its source in a comment or rule.
