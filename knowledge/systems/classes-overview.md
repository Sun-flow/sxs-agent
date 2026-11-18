# Classes overview

<!-- index: Read to see the whole class tree, when each class change unlocks, how changing class works and what it costs, roles, elements, tier lists and party make-up -->

> **Summary:** Two starting classes (Warrior, Mage) each split into two lines at Lv 44; the line then promotes at Lv 82 (Tier 3) and Lv 106 (Tier 4), with a Tier 5 already known. Class choice is reversible: a free, lossless class change opens at Lv 100 in Aqualis (one free per week), so before Lv 100 never use the cheap 10-Dawnium swap, which leaves you without skills. Our account is a Mage (mae's choice, R-054); the bot never picks or changes a class itself.
> **Applies:** all seasons
> **Related:** [Skills](skills.md), [Mage](../classes/mage.md), [Sorcerer](../classes/sorcerer.md), [Sage](../classes/sage.md), [Tier 4 classes](../classes/tier-4.md), [Levels and unlocks](levels-and-unlocks.md), [Seasons](seasons.md), [data/classes.json](../data/classes.json), rules R-054, R-117

## The class tree

```
Tier 1          Tier 2 (Lv 44)   Tier 3 (Lv 82)   Tier 4 (Lv 106)   Tier 5 ("Legend")
Warrior  --+--  Duelist    ----  Berserker   ----  Conqueror   ----  Ravager
           +--  Knight     ----  Paladin     ----  Guardian    ----  Templar
Mage     --+--  Sorcerer   ----  Archmage    ----  Destroyer   ----  Magister
           +--  Sage       ----  Arcanist    ----  Dominator   ----  Prophet
```

- Tier 1 to Tier 4 names [S-03][S-11][S-13]; Tier 5 names [S-10][S-85], Magister also named as Tier 5 in [S-11].
- Later tiers, from eog's tier list (Chinese-server content, eog's translations ❓) [S-85], in the order Duelist / Knight / Sorcerer / Sage line: Tier 6 Reaver / Empyrean / Cataclyst / Oracle; Tier 7 Annihilator / Seraph / Voidcaller / Ascendant; Tier 8 Hellblade / Paragon / Obliterator / Fateweaver.
- There are no further branches after Tier 2: each of the four lines only moves up [S-03]. Players therefore name a class by its Tier 2 name plus a number: "3rd Sorcerer" = Archmage, "4th Sage" = Dominator [S-03].
- Fandom calls the Duelist "Fighter" and the Paladin "Heavy Knight" in one place [S-03]. sxswiki calls the Dominator "Controller" [S-04]; every other source says Dominator.
- The Chinese version was close to finishing its 8th hierarchy (about 30 classes) when the Fandom page was written, so more tiers will follow each season [S-03]. The global version was described as having 6 class ranks with a 7th in development [S-03].

| Line | Tier 2 | Tier 3 | Tier 4 | Tier 5 | Role | Elements | Off-hand | Class stat |
|---|---|---|---|---|---|---|---|---|
| Warrior | [Duelist](../classes/duelist.md) | [Berserker](../classes/berserker.md) | [Conqueror](../classes/tier-4.md#conqueror-4th-duelist) | Ravager | Melee burst DPS | Physical, Dark, Fire [S-11] | Gauntlets [S-11] | Crit Rate [S-10][S-03] |
| Warrior | [Knight](../classes/knight.md) | [Paladin](../classes/paladin.md) | [Guardian](../classes/tier-4.md#guardian-4th-knight) | Templar | Tank | Physical, Light, Water [S-11] | Shield [S-11] | Block [S-10][S-03] |
| Mage | [Sorcerer](../classes/sorcerer.md) | [Archmage](../classes/archmage.md) | [Destroyer](../classes/tier-4.md#destroyer-4th-sorcerer) | Magister | Ranged AoE DPS | Fire, Water, Wind, Light (all but Dark) [S-11][S-01] | Spellbook [S-11] | Accuracy [S-03] (zeroluck's data label for the same trait: "Block Penetration" [S-10][S-80]) |
| Mage | [Sage](../classes/sage.md) | [Arcanist](../classes/arcanist.md) | [Dominator](../classes/tier-4.md#dominator-4th-sage) | Prophet | Healer, debuffer, summoner | Dark (plus heals and summons) [S-11][S-01] | Orb [S-11] | Higher base stats; Crit Resistance and Healing Boost [S-10][S-11] |

## When each class change unlocks

| Change | Character level | Where | Server day | Class-level gate | Sources |
|---|---|---|---|---|---|
| Pick Warrior or Mage | Early (the story quest "Crossroads of Classes") | Originisle V, after the Guardian Colossi boss; the Chief offers "Ascend to Mage" | Day 1 | - | R-054 |
| Tier 2 (2nd class) | Lv 44 | Cinder Ridge | Day 4 | Tier 1 class at class level 18; total class level 20 | [S-03][S-11][S-85]; gate [S-10][S-80][S-85] |
| Tier 3 (3rd class) | Lv 82 | Aqualis | Day 12 | Tier 2 class at class level 16 (total 48) [S-10][S-80][S-85]; other reading: a Fandom example says job level 18 [S-03] | level and day [S-11][S-85] |
| Lossless class change | Lv 100 | Aqualis | - | - | [S-03], R-117 |
| Tier 4 (4th class) | Lv 106 | Loong Haven: the mentor Mei at "Unrakumotogo" in the Dragon Realm | Day 47 (start of Season 2) | Tier 3 class at class level 19 (total 89) | [S-02][S-03]; day [S-11][S-85]; gate [S-10][S-80][S-85] |
| Tier 5 ("Legend") | Lv 136 ❓ | Aethyris (Season 3) | Day 114 ❓ | Tier 4 class at class level 40 (total 180) | level and day [S-85]; gate [S-10][S-80][S-85] |
| Tier 6 | Lv 172 ❓ | Harpadia (Season 4) | Day 226 ❓ | Tier 5 class at class level 50 (total 280) | [S-85] |
| Tier 7 | Lv 198 ❓ | Ignis (Season 5) | Day 335 ❓ | Tier 6 class at class level 55 (total 380) | [S-85] |

- Class tiers open by **server age**, not by when the account started: a new tier and season arrive roughly every 2 to 3 months [S-11][S-13] ❓. On an old server a new account can promote as soon as it meets the level and class-level gates.
- sxswiki says the branch happens "at level 18", "level 40" and "level 45" on different pages [S-04]. The "18" is the **class level**, not the character level [S-10]; this page follows Lv 44 [S-03][S-11].
- The Tier 3 level, Lv 82, is now given by two sources: [S-11] (tier D) and eog's roadmap [S-85] (tier C); Fandom ties it to "reaching Aqualis" [S-03].
- Class-level gates: the Tier 3 gate is class level 16 with total 48. Two readings of zeroluck [S-10][S-80] and eog's roadmap ("Class Lv. 48 + 2nd Job Lv. 16") [S-85] agree; Fandom's "job level 18" example [S-03] is the same tier (C) but stands alone, and 18 is also the Tier 2 gate, so it is probably a mix-up. This page follows 16 / 48.
- Tier 5 and later rows are the Chinese schedule projected onto global by eog ❓ [S-85]; full list in [server-day-roadmap.json](../data/server-day-roadmap.json).

## Class level and Class Badges

Each class has its own level track, separate from character level [S-10], R-117.

- Class > Class Hierarchy: a class card with "!" pays out Class Badges, +2 for each skill of that class you own [R-117].
- 10 badges raise that class by one level, giving HP, ATK, DEF and SPD; levelling any class raises Total Class Level without changing your class [R-117].
- Because badges come from owning skills, **class level is driven by Prayer pulls**: "you must pull enough Knight skills to get job level 18" [S-03]. Promotion needs both the class level of the current class and a total class level [S-10].
- Levelling classes with badges is always allowed for the bot (soft materials only) [R-117].

Relative base stats by class [S-10] (a database site; the numbers show each class's weighting, not your final stats):

| Tier | Class | Line | HP | ATK | DEF | SPD | Class trait |
|---|---|---|---|---|---|---|---|
| 1 | Warrior | warrior | 900 | 600 | 900 | 600 | - |
| 1 | Mage | mage | 500 | 1400 | 500 | 600 | - |
| 2 | Duelist | warrior | 1000 | 1500 | 1000 | 1500 | Crit Rate |
| 2 | Knight | warrior | 1500 | 900 | 1500 | 1100 | Block |
| 2 | Sorcerer | mage | 1000 | 1900 | 900 | 1200 | Accuracy ("Block Penetration") |
| 2 | Sage | mage | 1250 | 1250 | 1250 | 1250 | Crit Resistance, Healing Boost |
| 3 | Berserker | warrior | 1700 | 2400 | 1700 | 2400 | Crit Rate |
| 3 | Paladin | warrior | 2400 | 1600 | 2400 | 1800 | Block |
| 3 | Archmage | mage | 1650 | 2950 | 1600 | 2000 | Accuracy ("Block Penetration") |
| 3 | Arcanist | mage | 2050 | 2050 | 2050 | 2050 | Crit Resistance, Healing Boost |
| 4 | Conqueror | warrior | 2650 | 3450 | 2700 | 3400 | Crit Rate |
| 4 | Guardian | warrior | 3400 | 2600 | 3400 | 2800 | Block |
| 4 | Destroyer | mage | 2700 | 3900 | 2600 | 3000 | Accuracy ("Block Penetration") |
| 4 | Dominator | mage | 3050 | 3050 | 3050 | 3050 | Crit Resistance, Healing Boost |
| 5 | Ravager | warrior | 3700 | 4400 | 3700 | 4900 | Crit Rate |
| 5 | Templar | warrior | 4400 | 3600 | 4900 | 3800 | Block |
| 5 | Magister | mage | 3700 | 5400 | 3600 | 4000 | Accuracy ("Block Penetration") |
| 5 | Prophet | mage | 4550 | 4050 | 4050 | 4050 | Crit Resistance, Healing Boost |


## How changing class works

There are two different operations. Both are **mae's decision**: the bot never presses "Change Class" (R-054, R-117).

### A. Simple swap (any level): avoid

| Property | Value | Source |
|---|---|---|
| Cost | 10 Dawnium each time | [S-03] |
| Availability | Any level; done at the class NPC in Verdantglade or Cinder Ridge | [S-03] |
| What you keep | Character level; the upgrades and skill levels of your old class stay stored on that class | [S-03] |
| What you lose | Use of every skill of the old class: they are locked. A Warrior turned Mage has only the two default Mage skills and must pull Mage skills from scratch | [S-03] |
| Tier | You restart at the base class and must earn the class level to promote again (a Berserker turned Knight restarts as Warrior, can promote to Knight, then needs Knight class level for Paladin) | [S-03] |

Before Aqualis / Lv 100, do not change class this way [S-03].

### B. Lossless class change (Lv 100, Aqualis)

| Property | Value | Source |
|---|---|---|
| Unlock | Lv 100 in Aqualis; in our game the Change Class button is locked until Lv 100 | [S-03], R-117 |
| Target | Any class except your current one, at the **same tier** (Berserker -> Paladin directly) | [S-03] |
| Cost | One Slate per change. One free Slate per week; unused Slates do not stack. Extra changes in the same week cost Dawnium (amount ❓). Story quests rarely give a Slate | [S-03] |
| Skill conversion | All pulled skills convert to the new class by **base rarity and class tier**: Techniques only into Techniques, Charms only into Charms, never across tiers. Conversion uses base rarity, not ascended rarity | [S-03] |
| Choice | The game shows three conversion results (they follow the game's recommended build archetypes) and you pick one | [S-03] |
| Undo | 8 hours to revert to the old class with all skills as before; after that the change is locked and going back costs a Slate | [S-03] |
| Weapon | The old weapon is locked (kept in the bag) and you get a blue-quality weapon for the new class | [S-03] |
| After the first lossless change | Later swaps in Verdantglade or Cinder Ridge no longer lose skills | [S-03] |

What carries over in a lossless change: character level, skills (converted), gear other than the weapon, relics, Fantomons, companions. What does not fit any more: your **style** stats. Gear affixes, relic choices and companion levels were picked for the old class (Block for a Knight, Crit for a Duelist), and rebuilding them can take months [S-03].

Because conversion inside a rarity is random, some swaps are bad: a 3rd Duelist has four Legendary skills (2 Techniques, 2 Charms) and one Legendary Charm is core damage, while both Paladin Legendary Charms are weak, so Duelist -> Knight loses value [S-03].

Typical uses of the lossless change: 4v4 Challenge matches, dungeons short of a role, Gem Tower ranking pushes in Loong Haven, seasonal ranking pushes with another class's higher-scoring weapon, or simply trying a class [S-03].

### C. Class Rollback (no conversion)

Offered next to the lossless change at Lv 100. It sends you back to Warrior or Mage and lets you switch off higher-tier skills, so Prayer pulls only land on low-tier skills [S-03]. Use: pushing a Tier 1 skill (example: Insightful Eye from Mythic to Immortal) or a Tier 2 skill (roll back to Mage, promote to Sage only) without diluting pulls with Tier 3 skills [S-03]. Rarely needed.

## Roles and party make-up

| Role | Classes | Notes |
|---|---|---|
| Tank | Knight line | Taunt, shields, Block. Needed for dungeons and raids; slow solo [S-03][S-13] |
| Melee DPS | Duelist line | Crit and multi-hit; best 1v1 and solo story progress at Tier 2 [S-11][S-13] |
| Ranged AoE DPS | Sorcerer line | Widest AoE, most fragile [S-03] |
| Healer / support | Sage line | Only line with group heals and a revive; can also be built as Dark DPS ("Shadow Priest") or summoner [S-03][S-11] |

- **Everyone clears the kingdom story solo**, so every class needs a damage loadout, including Knights and Sages [S-03].
- A standard dungeon party is one tank, one healer and two damage dealers; four of the same class performs worse whatever the class [S-03][S-04].
- Chaos Invasion scores best with 1 damage dealer and 3 supports, rotating who is the damage dealer [S-01]. See [Events](events.md).
- A whale healer or tank lifts the whole party: a free-to-play Sage heals about 25% of an ally's HP in a round, a heavy spender more than 100% in one skill [S-03].
- Styles, builds, mechanics [S-03]: a **style** is your stat direction (Crit Duelist, Block Sorcerer, Healer Sage) and is slow to change; a **build** is the core skill set (Light Sorcerer, Erosion Sage, Water Knight); a **mechanic** is how the loadout fights (Shield, Taunt, "Fridge" freeze lock, Lifesteal) and can be swapped per loadout.

Damage profile of each Tier 2 line [S-03]:

| Class | Stat identity | Damage range per hit |
|---|---|---|
| Duelist | High Crit Rate, low Accuracy: crits do 150%+ but blocked hits are cut hard | 50% to 300% |
| Knight | High Block for long fights; a little Crit gives big hits when luck lines up | 50% to 200% |
| Sorcerer | Trades Crit for class Accuracy: rarely blocked, steady | 100% to 250% |
| Sage | Higher base stats, very flexible; no innate damage reduction, so do not stack Block | 50% to 200% |

A crit deals 150% base damage; a blocked hit deals 50% and ignores the crit bonus; the attacker's Accuracy lowers the defender's Block chance (20% enemy Accuracy needs 120% Block to block everything) [S-11] ❓, consistent with [S-03].

## Elements

- Three main elements form a triangle: **Wind beats Water, Water beats Fire, Fire beats Wind** [S-03].
- A monster of an element takes half damage from the element it beats (a Water monster halves Fire); some, such as elemental slimes, are immune to it. It takes much more damage from the element that beats it [S-03].
- Physical is neutral: nothing resists it and nothing is weak to it [S-03].
- Light and Dark also exist as skill and relic elements (relics come in five elements) [S-01]. They sit outside the triangle: Dark is weak to Light, and a unit is immune to its own element [S-42] (one player's notes, tier C, as on [Arena and PvP](arena-and-pvp.md) and [Monsters](monsters.md)); whether Light is in turn weak to Dark is not stated ❓.
- Mastery: 40 Elemental Mastery (or Physical Mastery) is +1% damage, from eog's damage-dummy test [S-85].
- Mages should keep saved loadouts per element and switch to the one the enemies are weak to [S-03]. See [Skills](skills.md#loadouts).
- Element also decides which [relic](relics.md) resonance to raise first and which Gate of Elements affinity you carry (R-105, R-159).

Best relic element per class, to level first (all five get levelled in the end) [S-01]:

| Class line | Element | Notes |
|---|---|---|
| Duelist | Fire | |
| Knight | Water or Light | Water for AoE, Light otherwise |
| Sorcerer | Wind, Water, Fire or Light | Wind: PvP. Water: better in 4v4 than PvE. Fire: better in PvE than PvP. Light: equally good in both |
| Sage | Dark | |

## Tier lists

No class is permanently best: a class that is strong at one tier tends to get weaker skills at the next, and the lossless change lets you move [S-03]. Fandom's author argues against picking by tier list at all, because servers need every role [S-03]. Lists below are tier D opinion pieces; use them only as a tie-breaker.

| Source, date | S | A | B | C |
|---|---|---|---|---|
| Pocket Gamer, 2026-11-03, v1.0.45 [S-13] | T2: Sorcerer. T3: Berserker, Arcanist. T4: Destroyer, Dominator | T1: Mage, Warrior. T2: Sage, Duelist. T3: Archmage. T4: Conqueror | T2: Knight. T3: Paladin. T4: Guardian | - |
| BlueStacks, 2026-09-01 [S-11] | Sorcerer, Berserker, Arcanist, Destroyer, Dominator | Mage, Warrior, Sage, Duelist, Archmage, Conqueror | Knight, Paladin, Guardian | - |
| Pro Game Guides, 2026-06-11, free-to-play [S-14] | Duelist | Knight | Sorcerer | Sage, Mage, Warrior |
| Pro Game Guides, 2026-06-11, heavy spender [S-14] | Sage | Sorcerer, Duelist | Knight | Mage, Warrior |
| All Things How, 2026-05-25 [S-17] | same as Pro Game Guides | | | |
| sxswiki, 2026-05-20 [S-04] | Sorcerer (one page adds Sage) | Duelist (Knight) | Knight, Sage (Warrior, Mage) | - |

Reading across them: at Tier 2 the Sorcerer is the best PvE clearer and the Duelist the best duellist; by Tier 3 and Tier 4 both Mage lines sit at the top (Destroyer for AoE, Dominator as the most complete class), the Duelist line stays strong in PvP and on bosses, and the Knight line is always needed in parties but ranks low for solo play [S-13][S-11]. The free-to-play lists that put the Duelist first date from launch and judge Tier 1-2 only [S-14][S-17].

eog's tier list (tier C, grades relayed from one creator; one grade for all modes) [S-85] goes further up the tree, in the order Duelist / Knight / Sorcerer / Sage line: Tier 3 A / B / A / B; Tier 4 S / A / A / B; Tier 5 C / A / A / S; Tier 6 S / B / A / C; Tier 7 B / S / S / B; Tier 8 S / C / A / B. So the Sorcerer line grades A, A, A, A, S, A for tiers 3 to 8, the steadiest of the four; eog flags Ravager (Tier 5 Duelist) and Oracle (Tier 6 Sage) as tiers to avoid. Note that eog rates Dominator B where the tier D lists above rate it S. Grades and 22 named builds: [class-tier-list.json](../data/class-tier-list.json).

What this means for our Mage: either Mage line ends in an S-rated Tier 4 class. See the recommended path in [Mage](../classes/mage.md#recommended-path-for-a-free-to-play-mage-from-level-1).

## Open questions

- ❓ Character level for the Tier 3 change seen in our game (Lv 82 per [S-11][S-85]). Confirm on the Class Hierarchy screen once in Aqualis.
- ❓ Dawnium price of a second lossless change in the same week.
- ❓ Class-level gates (18 / 16 / 19 / 40) seen in our game: zeroluck [S-10][S-80] and eog [S-85] agree, Fandom's example says 18 for Tier 2 -> Tier 3. Read the requirement on the "Class to Unlock" stone at home.
- ❓ Whether Light is weak to Dark (only "Dark is weak to Light" is stated [S-42]).
- ❓ Whether global keeps the Chinese schedule for Tier 5 and later (Lv 136, day 114 per [S-85]).
- ❓ Whether class level or Class Badges reset with a season (not mentioned in any source).

## Sources

- [S-01] relic element per class; Chaos Invasion party; skill vouchers
- [S-02] Tier 4 at level 106
- [S-03] Fandom: Classes Overview, Class Change, Everything about Class Change, Class Selection
- [S-04] sxswiki class pages (leads only)
- [S-10] zeroluck.gg classes page: promotion gates, base stats, Tier 5 names
- [S-42] player blog: Light and Dark, own-element immunity
- [S-80] zeroluck second reading (same gates and weights); [S-85] eog.gg roadmap, tier list and dummy test (job levels, days, gates, Tier 5 to 8 names, grades)
- [S-11] BlueStacks class guide and tier list: promotion levels and days, elements, off-hands
- [S-13] Pocket Gamer tier list; [S-14] Pro Game Guides tier list; [S-17] All Things How tier list
- R-054, R-117, R-105, R-159
