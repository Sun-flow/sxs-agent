# Game knowledge

> **Last updated**: 2026-11-04
> What the bot needs to know about Sword x Staff itself: the rules of the world and how the menus connect. The rest of `memory-bank/` is about the project; this folder is about the game.

| File | What it holds | How to change it |
|---|---|---|
| `rules/` | Rules of the world, one file per situation (policy, ui, home, overworld, quests, combat, dailies, guild, gathering, upgrades, economy, world). `rules/README.md` says which file to read when and lists retired IDs; `python3 scripts/index.py rules` prints every ID's file and title. | Add an entry under the right heading of the right file with the ID from `python3 scripts/check-rules.py --next` (after `git fetch`); the heading is its index entry. Never reuse or renumber an ID. When a rule is merged into another, add the old ID to the retired table. Run `python3 scripts/check-rules.py`. |
| `nav-graph.json` | Machine-readable graph of screens (nodes) and the actions that move between them (edges). The bot and the supervisor traverse this. | Edit the JSON, then run `python3 scripts/nav-graph.py check` and `python3 scripts/nav-graph.py render`. |
| `nav-graph.md` | Generated diagram and tables of the graph. | Don't edit by hand; `python3 scripts/nav-graph.py render` rewrites it. |

## Confidence levels

Used by the rules and the graph, so an agent knows what to trust:

- **observed**: seen in game on our test account (cite the capture or the session).
- **told**: stated by mae, not yet observed by the bot.
- **reported**: from a third-party guide or wiki (step 1 doc sources); may be out of date or wrong for our server or season.

Promote an entry to `observed` when a session sees it in game, and add the capture.

## Images

Screen captures and icon crops live wherever the hands-and-eyes layer commits them; reference them in a rule's meta line (relative to `docs/screens/`, or a full repo path for `resource/image/...`) or in a node's `images` field. Don't copy images into this folder.

## Using the graph

```bash
python3 scripts/nav-graph.py check           # validate ids, edges and fields
python3 scripts/nav-graph.py render          # rewrite nav-graph.md from the JSON
python3 scripts/nav-graph.py path home shop  # shortest sequence of actions between two screens
```

Format of `nav-graph.json`:

- `nodes[]`: `id` (snake_case, matches the state detector's state name), `name` (as the game labels it), `kind` (`hub`, `menu`, `popup`, `battle`, `world`, `overlay`), `confidence`, `unlock` (what opens it, or null), `detect` (what tells you you're on it: `{type: ocr|template, text or template, roi}`, matching the step 2 pipeline's `resource/pipeline/state.json`), `images`, `notes`.
- `edges[]`: `from`, `to`, `action` (`type`: `tap`, `back`, `swipe`, `wait`, `auto`; `target`: what to tap, described in words; `template`: the matcher's template name if one exists; `pos`: `[x, y]` as fractions of the 720×1280 portrait screen, null if not located yet, with a null coordinate inside when it varies, such as a list row), `confidence`, `notes`.
- Popups and overlays (`kind` popup or overlay) can appear on their own; `"to": "previous"` means the action returns to whatever was underneath.
- `when` (optional): the condition under which a script should take the edge, in the same words as the decision policy (`resource/policy/cards.json` on the step 3 branch), for example `goal=explore and hp_ok`. Edges without `when` are always fine to take.
- `"from": "*"` means the edge works from any screen (for example the Android back key closing a popup).
