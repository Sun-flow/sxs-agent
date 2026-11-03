# Game knowledge

> **Last updated**: 2026-11-03
> What the bot needs to know about Sword x Staff itself: the rules of the world and how the menus connect. The rest of `memory-bank/` is about the project; this folder is about the game.

| File | What it holds | How to change it |
|---|---|---|
| `rules.md` | One entry per rule of the world (currencies, quests, exploration, unlocks), each with a stable ID, its source and how sure we are. | Add an entry under the right topic with the next free ID. Never reuse or renumber an ID; mark a wrong rule `Superseded by R-NNN` instead of deleting it. |
| `nav-graph.json` | Machine-readable graph of screens (nodes) and the actions that move between them (edges). The bot and the supervisor traverse this. | Edit the JSON, then run `python3 scripts/nav-graph.py check` and `python3 scripts/nav-graph.py render`. |
| `nav-graph.md` | Generated diagram and tables of the graph. | Don't edit by hand; `python3 scripts/nav-graph.py render` rewrites it. |

## Confidence levels

Used by both files, so an agent knows what to trust:

- **observed**: seen in game on our test account (cite the capture or the session).
- **told**: stated by mae, not yet observed by the bot.
- **reported**: from a third-party guide or wiki (step 1 doc sources); may be out of date or wrong for our server or season.

Promote an entry to `observed` when a session sees it in game, and add the capture.

## Images

Screen captures and icon crops live wherever the hands-and-eyes layer commits them; reference them by repo path in the `images` field of a rule or a node. Don't copy images into this folder.

## Using the graph

```bash
python3 scripts/nav-graph.py check           # validate ids, edges and fields
python3 scripts/nav-graph.py render          # rewrite nav-graph.md from the JSON
python3 scripts/nav-graph.py path home shop  # shortest sequence of actions between two screens
```

Format of `nav-graph.json`:

- `nodes[]`: `id` (snake_case, matches the state detector's state name), `name` (as the game labels it), `kind` (`hub`, `menu`, `popup`, `battle`, `world`, `overlay`), `confidence`, `unlock` (what opens it, or null), `detect` (what tells you you're on it: text, template or region), `images`, `notes`.
- `edges[]`: `from`, `to`, `action` (`type`: `tap`, `back`, `swipe`, `wait`, `auto`; `target`: what to tap, described in words; `template`: the matcher's template name if one exists; `pos`: `[x, y]` as fractions of the 720×1280 portrait screen, or null), `confidence`, `notes`.
- `"from": "*"` means the edge works from any screen (for example the Android back key closing a popup).
