# resource: MaaFramework bundle

| Path | Holds |
|---|---|
| `pipeline/state.json` | `State.*` screen detectors; `State.Detect` lists them in priority order (first hit wins) |
| `pipeline/explore.json`, `home.json`, `upgrade.json`, `tutorial.json` | Template/OCR nodes used by the loops (`Explore.*`, `Gather.*`, `Home.*`, `Guild.*`, `Tutorial.*`) |
| `image/<group>/` | Templates the pipelines and code match (paths are relative to `image/`) |
| `policy/cards.json` | Card/popup decision rules (`sxs/decide.py`) |
| `policy/gather.json` | Material priority for the Gather Loop |
| `model/ocr/` | OCR models (fetched by `scripts/fetch-ocr-models.py`, gitignored except `keys.txt`) |

Reference screenshots are not here: they live in `docs/screens/`. A template made from a screenshot names its source in a comment or rule.
