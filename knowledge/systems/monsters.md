# Monsters and bosses

<!-- index: Read before deciding whether to fight something: monster kinds, what they drop, stamina cost, the power rule, named bosses, and how to team up -->

> **Summary:** Monsters in unexplored zones are free to fight and count toward exploration; in blessed (explored) zones they respawn and each fight costs 5 stamina, which is how Battle Essence is farmed. Take a fight when the enemy's power is at most 1.25x ours, with HP at 70% or more, and stop after two losses. Bosses come as map bosses, gate bosses, dungeon bosses and ranked damage bosses (Conquest, Crucible of Hieromon, Chaos Tyrant); most group content can be carried by stronger players once you meet the entry threshold.
> **Applies:** all seasons
> **Related:** [Dungeons](dungeons.md), [Towers](towers.md), [Events](events.md), [Guild](guild.md), [Stamina](stamina.md), [Exploration](exploration.md), [Skills](skills.md), [Relics](relics.md), [World and kingdoms](world-and-kingdoms.md), rules R-001, R-061, R-127, R-065, R-073, R-041, R-156, R-084, R-057, R-077

## Kinds of enemy

| Kind | Where | How it looks / starts | Cost | Rounds | Rule / source |
|---|---|---|---|---|---|
| Roaming world monster | Overworld tiles | Tap the monster, Start Battle | Free in unexplored zones; 5 stamina in blessed zones | up to 15 | [R-001] [R-065] |
| Guard (bracketed) monster | Around an NPC or target | Gold corner brackets; all must be beaten before the target responds | Free | 15 | [R-041] |
| Pickup guard | Standing on a pickup | Fight first, then collect | as above | 15 | [R-139] [R-073] |
| Monster group card | Map card with Rcmd Power, Drop Preview, Challenge (e.g. "Limpid Legion", 28.5K) | Press Challenge | Free | ❓ | [R-156] |
| Map boss | Boss marker (white ring with a boss portrait) | Tap, Start Battle | Free first time | ❓ | [R-044] |
| Gate boss | Dungeon gate with a rune | First Clear Rewards, Challenge | Free | 20 | [R-082] |
| Mini-dungeon enemies | Ruins, mines, lairs | 6 enemies per floor | Free | 25 | [R-040] [R-071] |
| Daily Dungeon rooms and boss | Team dungeon | 4-player party | Daily attempts | ❓ | [Dungeons](dungeons.md) |
| Tower floor | Fantasia Ascent | Challenge per floor | Free | 15 | [Towers](towers.md) |
| Conquest boss | Guild, per floor | 2 attempts a day, damage counted | Free | 50 | [Guild](guild.md) |
| Hieromon | Crucible of Hieromon | 6-player boss fight | ❓ | 10 | this page |
| Chaos Tyrant | Chaos Invasion | Damage ranking by class | Chaos Shards | ❓ | [Events](events.md) |
| Void Rift packs and elites | Rift markers | Up to 5 floors | 10 reward attempts | ❓ | [Events](events.md) |
| Mimic Chest | Some map chests | The chest lunges; tap nearby ground to dodge | Free | - | [S-40] |
| Special monsters | Appear during Resource Hunt auto-play | Random spawn | - | - | [S-42] |
| Arena opponents | Grand Arena | Other players' teams (bots right after reset) | Tickets | ❓ | [Arena and PvP](arena-and-pvp.md) |

- All battles are automatic; the player only starts them [R-001]. A map win returns to the map after about 4 seconds without a result screen [R-001].
- "Elite" is used by guides for the stronger enemies of Void Rift floors 3-4 (an elite plus adds) ❓ [S-43]. The game's own type labels are **Minion Monster** (common field monsters, 159 in the data), **Elite Monster** (tougher named field monsters, 67), **Boss** (stage and zone bosses, 39) and **Hieromon** (9), plus the Chaos Tyrant as a Boss type of its own [S-80]. eog's list has 215 monsters: 100 normal, 71 elite, 37 boss, 6 Hieromon, 1 chaos boss [S-85].
- The data also gives each monster an attack profile: Near Weak, Near Strong (melee), Far Weak, Far Strong (ranged); "light" and "heavy" for Weak and Strong is the site's reading, not a rating [S-80]. No source gives monster elements, levels, stats, places or drops.
- Named examples [S-80]: Minion Monster: Wind / Fire / Water / Light / Dark Slime, Sylvanwolf Bruiser and Flinger, Boar, Saber Rabbit, Sickle Mantis. Elite Monster: Sylvanwolf Rider, Sylvanwolf Shaman, Slime Kings, Two-Headed Troll, Boar King. Boss: Golem, Sylvanwolf Chieftain, Corrupted Guardian, Spider Queen. Tables: [data/monsters.json](../data/monsters.json) (37 named, game labels) and [data/monster-list.json](../data/monster-list.json) (215, eog's translations, e.g. "Forest Wolf" = Sylvanwolf).

## Free vs stamina: unexplored and blessed zones

| Zone state | Monsters | Interactables | What to do | Source |
|---|---|---|---|---|
| Unexplored (below 100%, statue not blessed) | Free, do not respawn, count toward the Explore % | Free | Fight and collect everything within the power rule | [R-065] [R-021] |
| Blessed (100% explored, Goddess Statue activated) | Respawn; show a stamina mark; 5 stamina per fight | Most cost stamina | Skip unless deliberately farming | [R-065] |

- Picking up resources or fighting mobs on the world map costs 5 stamina each (in blessed zones) [R-065] [R-106] [S-42].
- Stamina regenerates 5 per hour up to 300, plus a free +30 a day from the Vendor Booth Vault [R-107]. See [Stamina](stamina.md).
- Resource Hunt: an auto-play mode that spends a chosen number of attempts; special monsters and Mining Nodes can appear during it [S-42].

## Drops

| Enemy | Drop | Source |
|---|---|---|
| World monsters in blessed zones | Battle Essence (skill upgrade material), the reason to spend stamina on them | [R-065] [R-106] |
| Dread Hollow realm monsters (fought with Worn Knuckles) | Battle Essence | [S-45], [Material Realms](material-realms.md) |
| Special monsters (Resource Hunt) | Dawnium and kingdom merchant currency (the blog calls them "Feathers" and "Alloy"; in-game names and kingdoms ❓, Verdantglade's is the Abundance Leaf: see [World and kingdoms](world-and-kingdoms.md)) | [S-42] |
| Monster group cards | Shown in the card's Drop Preview | [R-156] |
| Gate and mini-dungeon bosses | First Clear Rewards (e.g. Refined Ore 100, Raw Ore 640) | [R-071] [R-082] |
| Dungeon bosses | Gear and gear shards by rating | [Dungeons](dungeons.md) |
| Conquest boss | 10 Dawnium, 150 Guild Tokens per attempt, floor chests | [R-111] |
| Chaos Tyrant | Chaos Crystals; ranking pays Primal Forge Shards | [S-42] |
| Void Rift | Relic pulls up to Mythic ❓ | [S-43] |
| Any map fight in an unexplored zone | Explore counter progress | [R-021] |

- Battle Essence feeds skill slots ([Skills](skills.md)); ore feeds gear; sand feeds relics [R-106]. Which material to spend stamina on changes over a season: Sand early, Ore mid-season [S-01].
- Fantomons that are deployed auto-pick items dropped during exploration, but cannot open chests or mine nodes [S-40] [S-42].

## Power comparison: when to fight

| Check | Rule | Source |
|---|---|---|
| Power | Accept enemies with up to 25% more CP than ours (1.25x rule); above that it is a wall | [R-127] [R-084] |
| HP | At least 70% before any fight; heal from the HUD portrait | [R-061] [R-078] |
| Losses | Same fight lost twice after healing: stop and get stronger | [R-061] |
| Tower floors | Same 1.25x test on the floor's recommended power | [R-079] |
| Gates of Power | Hard number; no fight, wait until CP meets it | [R-086] |
| Dungeon difficulties | Hard CP thresholds per difficulty; inside, a carry can do the fighting | [S-01] |

- Zone labels show a recommended power (e.g. Troll Lair 17K, Verdantglade VIII 27K); pick zones by it [R-135].
- Example of a wall: Verdantglade III (12K) lost every fight at 8.1K and at 10K power [R-084].
- CP is not everything: monsters usually out-power us on paper, and skills and gear win when the character is well built [R-127]. Bosses reward multi-hit skills that trigger passives; room clears reward AoE ❓ [S-49].

## Elements

| Rule | Source |
|---|---|
| Five relic elements exist (Fire, Water, Wind, Light, Dark), each with its own resonance | [S-01] |
| Triangle: Wind beats Water, Water beats Fire, Fire beats Wind | [S-03]; two legs also in [S-42] |
| Dark is weak to Light (outside the triangle; the reverse is not stated ❓) | [S-42] |
| A unit is immune to its own element | [S-42] |
| Gates of Elements (e.g. Gate of Wind) need total affinity of one element | [R-159] |
| Class element choices: Duelist Fire, Sage Dark, Knight Water (AoE) or Light, Sorcerer Wind / Water / Fire / Light | [S-01] |

- The triangle is the firm part (two sources); the Light / Dark rule and own-element immunity rest on one player blog ❓. Which monsters carry which element is not documented, though slimes are named by element [S-80]. Elemental Mastery is a stat on gear and charms [S-03]. See [Relics](relics.md).

## Named bosses and monsters

| Name | Kingdom / place | What it is | Source |
|---|---|---|---|
| Guardian Colossi | Originisle (tutorial island) | Story boss of the quest "Fight the Guardian Colossi!"; beating it leads to the class choice | [R-044] |
| Moonveil wolf boss and 3 wolves | Verdantglade, Moonveil Woods gate | Gate boss, 20 rounds; opens the area of Fantasia Ascent | [R-082] |
| Spear wolves | Verdantglade | Common roaming monster that blocks paths | [R-073] |
| White rabbits | Verdantglade VII | Respawning monsters, 5 stamina each once the zone is blessed | [R-065] |
| Bracketed wolf-boss pack | Verdantglade, Highland Woods entrance | Guard pack, beaten at 10K power | [R-041] |
| Limpid Legion | Verdantglade | Monster group card, Rcmd Power 28.5K | [R-156] |
| Troll Lair | Verdantglade side zone, 17K | Named lair zone | [R-135] |
| Auroradrasil boss | Verdantglade | Final boss of the first Daily Dungeon | [R-133] [S-45] |
| Storm Griffin | Verdantglade peaks | Legendary Hieromon (wind) | [S-48] |
| Flamoenix | Cinder Ridge | Legendary Hieromon (fire, machine bird) | [S-48] |
| Yamata no Orochi | Aqualis | Legendary Hieromon, eight-headed serpent, guardian of Aqualis | [S-48] |
| Primordial Loong | Loong Haven | Legendary Hieromon, origin of the Loongborn | [S-48] |
| Lord of Decay, Lord of Ruin | ❓ (later kingdoms) | Hieromon named in game data (eog: "King of Decay", "King of Ruin") | [S-80][S-85] |
| Chaos Tyrant | Chaos Rifts | Chaos Invasion boss with very low armor | [S-42] [S-01] |
| Golem | Home screen weekly boss ❓ | A weekly boss that lets you pick Companions as support ❓ | [S-44] |
| Conquest floor bosses | Guild, Gate of Expedition | One shared boss per floor | [R-111] |

### Crucible of Hieromon

- A daily event: a 6-player boss fight that lasts 10 rounds or until all players fall; the boss has 200 life bars, so the goal is damage dealt, not a kill [S-42].
- It appears in the weekly achievement list together with Daily Dungeon and Split Mirage (reset Monday 8:00) [R-099].
- The Hieromon are the legendary beasts of each kingdom (table above) [S-48]. The game data has 9 Hieromon; 6 are named: Storm Griffin, Flamoenix, Yamata no Orochi, Primordial Loong, Lord of Decay, Lord of Ruin [S-80]. eog's list adds further names in its own translation (King of Thunder, King of the Riven Sky, King of Collapse, Starlit Evil Dragon); how they map to the game's names is unknown ❓ [S-85]. Which one is fought, and the rewards, are not documented ❓.

## Team-up mechanics

| Mechanic | How it works | Source |
|---|---|---|
| Team panel | Flag at the map's top left: Players (1/9 shown), Team Goal, and three ways to find people: World Call, Invite, Nearby | [R-077] |
| World Call | A server-wide call for party members from the Team panel ❓ (seen as a button, not yet used) | [R-077] |
| Requests | Badged person icon on the map's left edge: Apply panel with Friends / Team Up / Challenge / Room; Decline All, Agree All | [R-057] |
| NPC companions | Akane, Qin and Killian fill empty seats in a story dungeon; each also carries Wind Affinity 101 for Gates of Elements | [R-133] [R-159] |
| Matchmaking | Daily Dungeons can be queued with matchmaking, group of 4 | [S-42] |
| Party sizes | Daily Dungeon 4; Void Rift up to 4; Chaos Invasion 4 recommended; Crucible of Hieromon 6 | [S-42] [S-01] |
| Carry | You must meet the entry threshold yourself; a stronger player then clears the content | [S-01] |
| Support rotation | In damage rankings, 1 damage dealer + 3 supports, rotating over 4 runs | [S-01] [S-03] |
| Affection Tokens | Partying in daily events pays tokens: more with friends or guildmates than with strangers (1 or 2 with a stranger; the source contradicts itself) ❓. A second reading: Affection comes from praying, capped at 1,000 a week [S-85] ❓; both may be true, see [Gacha](gacha.md) | [S-42] |
| Companions as support | Not allowed in Chaos Invasion; selectable in the weekly boss ❓ | [S-03] [S-44] |
| Background fights | Long fights (Conquest, tower) can be minimised and finish on their own | [R-112] |

- Our bot may invite players, accept team-ups and use helpers; it never types in chat [R-057].
- The main story must be played solo, so every class, including tank and healer builds, needs a damage loadout ❓ [S-49].
- Best group for mixed content: 1 healer, 1 tank, 2 DPS [S-43]. Mage line roles: Sorcerer is the AoE damage seat, Sage the healer / buffer seat [S-42]. See [Sorcerer](../classes/sorcerer.md) and [Sage](../classes/sage.md).

## Open questions

- ❓ Marker colours of Minion, Elite and Boss monsters on the minimap.
- ❓ Respawn time of monsters in blessed zones.
- ❓ Battle Essence per monster fight vs per Dread Hollow run (which is the better use of stamina and Dawnium).
- ❓ Element of each monster family; whether Light is also weak to Dark.
- ❓ The three unnamed Hieromon and the kingdoms of Lord of Decay and Lord of Ruin.
- ❓ Crucible of Hieromon: unlock level, daily attempts, reward table.
- ❓ Split Mirage: what it is.
- ❓ Whether World Call has a cost or cooldown.
- ❓ Named world bosses of Cinder Ridge, Aqualis and Loong Haven.

## Sources

- [S-01] core philosophy (carries), Relics (elements), Chaos Invasion tips, stamina tips
- [S-03] Fandom Chaos Invasion guide, Elemental Mystery page
- [S-40] official checklist (Mimic Chests, Fantomon auto-pick); [S-48] official Hieromon post
- [S-42] player blog: stamina cost, elements, Crucible of Hieromon, special monsters, party sizes
- [S-80] zeroluck.gg bestiary ([notes](../sources/notes/zeroluck.md)); [S-85] eog.gg monster list ([notes](../sources/notes/eog.md))
- [S-43] EOG Void Rifts; [S-44] Kanstein Codex (weekly boss); [S-45] All Things How; [S-49] BlueStacks
- Rules R-001, R-021, R-040, R-041, R-044, R-057, R-061, R-065, R-071, R-073, R-077, R-078, R-079, R-082, R-084, R-086, R-099, R-106, R-107, R-111, R-112, R-127, R-133, R-135, R-139, R-156, R-159
