# Game rules index

Rules of the world for an agent acting in Sword x Staff, split by situation. Read the file for the situation you're in; read `policy.md` before pressing anything that might spend, and on any class, social, account or rating prompt.

## Which file

| Situation | File |
|---|---|
| Any button that might spend; class, social, account, rating prompts; pulls | `policy.md` |
| Menus, popups, dialogue, tutorial highlights, red badges, reading a shop | `ui.md` |
| The Home scene: Cart, Statue, Vendor Booth, house and bed, home looks wrong | `home.md` |
| Island map: exploring, minimap, area map, travel, fog, statues, gates, puzzles, unreachable targets | `overworld.md` |
| The quest tracker: what's next, tracking, progressing, claiming | `quests.md` |
| Before a fight, low HP, losses, mini-dungeons, team dungeons, Fantasia Ascent | `combat.md` |
| Daily loop content: sign-in, events, Journal, Material Realms, milestones | `dailies.md` |
| Guild island, donations, AFK gathering, Conquest, Guild Shop | `guild.md` |
| Stamina, materials, pickups, Bellflowers | `gathering.md` |
| Character power: the character "!", gear, skills, charms, class, rank, relics | `upgrades.md` |
| Currencies, Vendor Booth, Mall | `economy.md` |
| Background: regions, servers, level unlocks, seasons, server time, towns and their NPCs | `world.md` |

## Entry format

```
### R-NNN · Title as an instruction or fact
1-6 short sentences or bullets: what to do, how to recognise it, where to tap, which code or template.
*observed* · `image.png` · node `node_id` · R-xxx
```

- Meta line: confidence (*observed* = seen in game by the bot; *told* = stated by mae, not yet seen; *reported* = third-party guide, may be wrong for our server), images (relative to `docs/screens/`, or a full `resource/image/...` path), nav-graph nodes, related rules. "(mae)" in the text marks mae's explicit decision: policy the bot must not override.
- Positions are (x, y) fractions of the 720×1280 portrait frame, or px in that frame. ❓ marks an open question.
- Write only what an acting agent needs: no sources, dates, history or account snapshots (those go in `memory-bank/log.md` and `memory-bank/status.md`).

## Adding or changing a rule

- New rule: take the ID from `python3 scripts/check-rules.py --next` (run `git fetch` first, so IDs that other open
  branches already took are counted), and put it under the right `##` heading of the right file. That heading is
  the whole registration: there is no index table to edit.
- Never reuse or renumber an ID. When merging a rule into another, delete it, add a row to the retired table below
  (rows sorted by old ID), and repoint citations.
- Run `python3 scripts/check-rules.py`: it checks that every rule ID is defined once, every cited ID resolves,
  retired IDs aren't cited, every file is in the situation table above, and image paths exist. If two branches took
  the same ID, the second to merge fails this check on main and renumbers its rule.

## Finding a rule by ID

The ID index is built from the rule headings, never kept by hand:

```
python3 scripts/index.py rules           # ID | file | title, for every live rule, and the next free ID
python3 scripts/index.py rules R-130     # print one rule (several IDs allowed)
```

Or search: `grep -rn "### R-130" memory-bank/game/rules/`.

## Retired IDs

Merged into another rule (most during the 2026-11-04 consolidation; R-141 on 2026-11-10, when mae withdrew its loop-switching ban). Cite the new ID.

| Old | Now |
|---|---|
| R-003 | R-070 |
| R-005 | R-076 |
| R-008 | R-002 |
| R-009 | R-022 |
| R-012 | R-011 |
| R-013 | R-006 |
| R-014 | R-070 |
| R-016 | R-103 |
| R-017 | R-107 |
| R-029 | R-044 |
| R-032 | R-025 |
| R-033 | R-107 |
| R-034 | R-002 |
| R-038 | R-080 |
| R-039 | R-037 |
| R-045 | R-074 |
| R-048 | R-118 |
| R-049 | R-092 |
| R-050 | R-054 |
| R-055 | R-093 |
| R-056 | R-037 |
| R-058 | R-062 |
| R-075 | R-126 |
| R-081 | R-004 |
| R-083 | R-044 |
| R-087 | R-066 |
| R-090 | R-031 |
| R-141 | R-139 |
