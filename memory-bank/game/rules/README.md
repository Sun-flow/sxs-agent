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
| Background: regions, servers, level unlocks, seasons, server time | `world.md` |

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

- New rule: next free ID (**next free: R-134**), under the right `##` heading of the right file, plus a row in the ID index below.
- Never reuse or renumber an ID. When merging a rule into another, delete it, add it to the retired table, and repoint citations.
- Run `python3 scripts/check-rules.py`: it checks that every cited ID resolves, retired IDs aren't cited, every file is listed here, and image paths exist.

## ID index

| ID | File | Title |
|---|---|---|
| R-001 | `combat.md` | All battles are automatic |
| R-002 | `overworld.md` | Full exploration = every green dot cleared and all mist revealed |
| R-004 | `overworld.md` | Minimap and coordinates give relative positions |
| R-006 | `world.md` | Regions and servers |
| R-007 | `quests.md` | Follow the quest guide to finish the tutorial |
| R-010 | `ui.md` | A locked menu means "not yet", not an error |
| R-011 | `world.md` | Some features unlock by level; seasons partly reset levels |
| R-015 | `dailies.md` | Material dungeons: two free attempts each |
| R-018 | `economy.md` | Dawnium is the premium currency: never spend it |
| R-019 | `economy.md` | Rolla is the common currency |
| R-020 | `home.md` | Collect the Cart's AFK rewards from its bubble |
| R-021 | `quests.md` | The Explore counter rises with fog, pickups, fights and objects |
| R-022 | `quests.md` | Track a quest: a gold ring marks its next target |
| R-023 | `upgrades.md` | Enhancing gear costs ore and Rolla |
| R-024 | `world.md` | Server time is UTC-5; dailies reset 8:00, achievements Mondays 8:00 |
| R-025 | `overworld.md` | Tap to walk, swipe to pan; the camera doesn't follow |
| R-026 | `ui.md` | Use the on-screen back arrow, not the Android back key |
| R-027 | `ui.md` | Keep away from the chat strip |
| R-028 | `ui.md` | Tap through story dialogue, then carry on |
| R-030 | `overworld.md` | Map objects open a card with one action |
| R-031 | `combat.md` | "Incapacitated" and "badly wounded" are both losses |
| R-035 | `home.md` | Use the bed's free speed-up once a day |
| R-036 | `ui.md` | Tap what the tutorial highlights |
| R-037 | `upgrades.md` | Techniques level with Battle Essence, capped by character level |
| R-040 | `combat.md` | Temple Ruins: multi-floor mini-dungeon |
| R-041 | `quests.md` | Beat a target's bracketed guards before it responds |
| R-042 | `policy.md` | Answer cards by a goal-dependent policy, not a fixed tap |
| R-043 | `policy.md` | Never press a spending button unless an exception below allows it |
| R-044 | `quests.md` | The main chain, side quests and claiming from the tracker |
| R-046 | `combat.md` | "Badly wounded" dialog |
| R-047 | `home.md` | Cook healing food in the Alchemy Pot |
| R-051 | `dailies.md` | Event sign-ins are on the Notice board |
| R-052 | `dailies.md` | Exploration Goals: milestone rewards |
| R-053 | `ui.md` | Find menu buttons by label; they move as features unlock |
| R-054 | `policy.md` | Class choices are mae's: pick Leave and stop |
| R-057 | `policy.md` | Social features are open to the bot: team up freely |
| R-059 | `home.md` | Filter home labels out of tracker OCR |
| R-060 | `ui.md` | Close popups by tapping above them; rating popups get Later |
| R-061 | `combat.md` | Heal to 70% before any fight; retry a lost fight at most twice |
| R-062 | `overworld.md` | Talk to red "!" NPCs first; they gate what's around them |
| R-063 | `ui.md` | A red "!" on a menu button or tab means something to claim |
| R-064 | `overworld.md` | If the marker leads nowhere, follow NPC instructions |
| R-065 | `overworld.md` | When stuck or between quests, walk the fog edge |
| R-066 | `overworld.md` | Minimap legend: it shows the true tiles |
| R-067 | `overworld.md` | Areas join by land bridges: head for the connection, not the straight line |
| R-068 | `overworld.md` | Travel far or into unexplored ground through the area map |
| R-069 | `overworld.md` | The Voyage Obelisk travels to the next kingdom |
| R-070 | `overworld.md` | Goddess Statues bless a fully explored area |
| R-071 | `combat.md` | Mines: mini-dungeons with first-clear rewards |
| R-072 | `overworld.md` | Energy Circuits puzzle: not automated |
| R-073 | `combat.md` | Fight monsters that block the path |
| R-074 | `overworld.md` | Edge pointers: tap one to pan the camera to its target |
| R-076 | `overworld.md` | The area map shows resources, progress and power gates |
| R-077 | `policy.md` | The Team panel: invite and team up |
| R-078 | `combat.md` | Read HP on the HUD bar; heal via the HUD portrait |
| R-079 | `combat.md` | Fantasia Ascent: one climb a day, Auto Challenge on, never Retry |
| R-080 | `upgrades.md` | A "!" on the player or the character screen means an upgrade is waiting: take it |
| R-082 | `quests.md` | Counterless unlock quests: talk to the NPC, then the gate |
| R-084 | `overworld.md` | A recommended power far above yours is a wall: stop exploring there |
| R-085 | `overworld.md` | Stone tile floor puzzle: step on every tile for chests |
| R-086 | `overworld.md` | Gate of Power: a wall until power meets it, then press Open |
| R-088 | `upgrades.md` | Replace gear with better items from the profile |
| R-089 | `overworld.md` | Travel from home through the quest tracker |
| R-091 | `combat.md` | Heal between floors; a defeat ends the run |
| R-092 | `upgrades.md` | Enhance all gear evenly, in 5-level bands |
| R-093 | `policy.md` | Skill pulls run only from mae's pull script, x10 only |
| R-094 | `dailies.md` | The Journal routes to the tower, gathering and realms |
| R-095 | `dailies.md` | Material Realms: mine with free hammers; never buy hammers |
| R-096 | `dailies.md` | Thrilling Events: only Sign-in and Growth Trial |
| R-097 | `dailies.md` | Daily Sign-in: claim today's tile, never Catch Up |
| R-098 | `dailies.md` | Growth Trial: claim free trial quests, never Advanced Trial |
| R-099 | `quests.md` | Guidance quests are an ore source |
| R-100 | `home.md` | Home stuck on sky: restart the game |
| R-101 | `home.md` | Collect bed EXP daily, and when close to levelling |
| R-102 | `guild.md` | Join a random open guild; never create one |
| R-103 | `guild.md` | Donate twice a day, never more |
| R-104 | `upgrades.md` | Level everything at once with Quick Upgrade |
| R-105 | `upgrades.md` | Enhance relics in bands of 1, element by element (not unlocked yet) |
| R-106 | `gathering.md` | Four upgrade materials, each gathered for 5 stamina a pickup |
| R-107 | `gathering.md` | Keep 70 stamina for daily commissions; spend the rest on the priority material |
| R-108 | `gathering.md` | Track a material through Journal > Map Exploration > Resource Hunt |
| R-109 | `gathering.md` | Always tap special nodes with a green timer circle |
| R-110 | `guild.md` | AFK gathering: keep the character at the Forge |
| R-111 | `guild.md` | Conquest: claim floors, use both attempts in the background |
| R-112 | `combat.md` | Background fights: start, minimise, move on |
| R-113 | `guild.md` | Find buildings by label; find the Gate from the Lobby label |
| R-114 | `guild.md` | Guild Shop: buy nothing until mae's buy list exists |
| R-115 | `upgrades.md` | Ascend a badged skill with its own shards |
| R-116 | `ui.md` | Claim every lit Goals tab with the claim-goals task |
| R-117 | `upgrades.md` | Level classes with Class Badges; never Change Class |
| R-118 | `upgrades.md` | Rank Advancement raises the level cap |
| R-119 | `upgrades.md` | Activate Gear Resonance each time a band completes |
| R-120 | `economy.md` | Molly's Vendor Booth: claim only the free Vault stamina |
| R-121 | `economy.md` | Mall: claim the free gift boxes, never a pack |
| R-122 | `gathering.md` | Prefer pickups with a blue aura |
| R-123 | `gathering.md` | Bellflowers come from the free Verdantglade Flower Harvest |
| R-124 | `gathering.md` | The collector's tap order |
| R-125 | `ui.md` | Read items through their info cards, never the price button |
| R-126 | `home.md` | Find home objects by template; the camera keeps its pan |
| R-127 | `combat.md` | Take fights against up to 25% more CP than ours |
| R-128 | `quests.md` | Daily Quest: the default Quest page |
| R-129 | `ui.md` | "Choose Your Reward": take the class match, else ask mae |
| R-130 | `overworld.md` | Fog-walk and pathfind toward the light-green to striped-green edge |
| R-131 | `overworld.md` | Save a reference of every collectible and monster met while exploring |
| R-132 | `overworld.md` | Dotted lines mark zone borders: finish the zone you're in first |
| R-133 | `combat.md` | Auroradrasil: a free 4-player story dungeon with NPC companions |

## Retired IDs

Merged into another rule during the 2026-11-04 consolidation. Cite the new ID.

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
