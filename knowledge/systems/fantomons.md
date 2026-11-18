# Fantomons

<!-- index: Read before spending Bond Trinkets, Summon Crystals, Treats or aptitude materials, or when choosing which Fantomon is Main, Sub or Deployed -->

> **Summary:** Fantomons are pets that give permanent stats and one combat ability. Put the Fantomon whose
> aptitudes you want in the Main slot (100% of its stats), one of each type in the three Sub slots (50%), and
> mark as Deployed the one whose skill you want in battle; Main and Deployed need not be the same [S-01].
> Save Summon Crystals for a Mythic and its duplicate (2 x 60); at Lv 108 the duplicate turns it into an
> Adult, which is a large power jump [S-02].
> **Applies:** all seasons (unlocks at Lv 51 per R-011, Lv 50 per the publisher; Adult evolution from Lv 108, Season 2)
> **Related:** [Gacha](gacha.md), [Companions](companions.md), [Relics](relics.md), [Guild](guild.md),
> [Shops](shops.md), [Cart and home](cart-and-home.md), [Seasons](seasons.md), [Astral Pact](astral-pact.md),
> [Currencies](currencies.md), data: [fantomons.json](../data/fantomons.json), rules R-011, R-020, R-066, R-114

## What a Fantomon is

- A pet system that adds to overall Power [S-03]. Every owned Fantomon adds stats; the four in the lineup add
  far more [S-04, S-24].
- Permanent power: Fantomon ascensions and Fantomon aptitudes survive a season reset [S-03]. SOF lists
  Fantomons with Relics, Companions and the Astral Pact as the permanent power sources [S-01].
- Seasonal part: Fantomon levels above 100 give stats for the season only and fall back to 100 at the reset
  [S-03]. "Season Fantomon level" is one of the five things the [Astral Pact](astral-pact.md) rates [S-01].
- **Auto-Pick:** once a Fantomon is deployed, items dropped during exploration are collected automatically
  [S-03]. (Our overworld rule R-066 expects this for the green collectible dots.)

## Unlock

| What | When | Source |
|---|---|---|
| Fantomon system | Character **Lv 51** per our rule [R-011] (tier A, the figure this page follows); the publisher, eog and the wikis say Lv 50 [S-87], [S-85], [S-03], [S-20], [S-26] (see [conflicts](../conflicts.md)) | [R-011]; [S-87] |
| Where | **Arborisfatum**, the big tree at Home; summon there (Destiny Fruit also comes from it) | [S-03], [S-25], [S-87] |
| Cart "Treats" row (level-up food income) | Cart row unlocks at Lv 45 | R-020 |
| Adult evolution ("Fantomon Manifestation" on eog; Childhood to Adulthood in the game data [S-80]) | Lv 108 (Season 2, Loong Haven); S-04, S-20 and S-26 add "Nimbuville unlocked" ❓. eog also lists a "Fantomon Bond" feature at Lv 180 ❓ | [S-02], [S-85] |

## Types and their aptitude material

Each Fantomon has one of three types. The type decides its aptitude material and the special stats on its
Aptitude pages.

| Type (in-game icon) | Also called | Aptitude material | Special stats in the Aptitude pages | Sources |
|---|---|---|---|---|
| Attack (red) | DPS, Attacker | Magic Wool | Crit Rate and Accuracy | [S-01], [S-03] |
| Tank (orange shield) | | Brown Egg | Block and Crit Res (Aegiswing: Block and Block Efficiency [S-02]) | [S-01], [S-03] |
| Support (green plus) | | Fresh Essence | DMG Boost and DMG Reduction (Pandarial: Healing Boost [S-02]) | [S-01], [S-03] |

- The roster has 13 Fantomons: 4 Attackers, 4 Tanks, 5 Supports; 12 of them evolve from Childhood to Adulthood, which upgrades the model, stats and skill quality [S-25][S-80]. Per-Fantomon type is still not readable from either site.
- Wool, Egg and Essence come in rarities; the Wheel of Destiny offers "Legendary Fantomon resources (wool,
  egg, essence)" [S-01]. The Fantomon summon also drops "ability food" of Rare and Epic grade [S-25].
- Where aptitude materials come from: the weekly [Guild](guild.md) shop (SOF: "Fantomon Aptitude mats /
  Summon tokens are the highest priority Guild shop purchases every week" [S-01]); the guild shop sells
  livestock and plants (sheep, chickens, sprouts) for the guild Sheepfold, Roost and Garden, which is where
  wool, eggs and essence are produced (shop stock per R-114). zeroluck's guild page confirms the link: the
  **Garden** gives oil, the **Sheepfold** wool and the **Roost** eggs [S-80]; its "oil" is most likely our Fresh
  Essence ❓. Each facility runs timed AFK sessions of 6 / 9 / 12 minutes that pay 60 Basic / 20 Premium / 60
  Premium Treats plus 6 / 12 / 24 random materials of its kind [S-80]. See [Guild](guild.md) and
  [life-skills.json](../data/life-skills.json).

## Rarities

- Rarity ladder used across the game: Rare -> Epic -> Legendary -> Mythic -> Divine -> Immortal [S-03].
- The summon itself yields Epic and Legendary Fantomons; the three Mythics (Nyxarchon, Aegiswing, Pandarial)
  are bought with Summon Crystals in the exchange shop [S-87][S-85][S-20, S-25, S-26]. Sources disagree on what the
  0.8% top summon rate is called (see [Gacha](gacha.md#fantomon-summon-arborisfatum)).
- Rarity counts: 3 Mythic, 6 Legendary, 4 Epic [S-25][S-80][S-85]. eog names them: Mythic Aegiswing, Nyxarchon,
  Pandarial; Legendary Armopi, Herbote, Kels, Sylvaerie, Terragon, Zeioletus; Epic Boaro, Chomusuke, Falko,
  Mandragora [S-85] (second-hand: eog credits Prydwen for these rows). Skills per Fantomon:
  [fantomon-skills.json](../data/fantomon-skills.json).

## Lineup: Main, Sub, Deployed

The lineup screen shows one **Main** slot ("100% Base Boost") and three **Sub** slots ("50% Base Boost"), with a
**Deployed** badge on one of the four [S-01, page image].

| Role | What it does | What to look at when choosing |
|---|---|---|
| Main | 100% of that Fantomon's stats go to the character | Its **aptitudes** (the stats it gives) [S-01][S-85] |
| Sub (x3) | 50% each | One Fantomon of each type, so every type's stats are covered [S-01] |
| Rest of the collection | 20% each | Nothing to choose [S-85][S-04, S-24, S-26] |
| Deployed | The one that fights beside you; any of the four | Its **skill** (passive/assist ability, and its Adult active skill) [S-01, S-02] |

- **Main is not Deployed.** SOF's own example: Nyxarchon as Main (for Crit Rate and Accuracy aptitudes) with
  Aegiswing Deployed (for its passive in combat); Subs Aegiswing (Tank), Sylvaerie (Support), Zeioletus
  (Attack) [S-01].
- Rule of thumb for the Main: Knight -> Aegiswing or another Tank Fantomon; DPS -> Nyxarchon or another
  Attack Fantomon; Support -> your preference or a Support Fantomon [S-01].

## Levelling and Resonance

- Feed **Treats** to level a Fantomon [S-03]. Treat grades: Basic, Premium, Deluxe (more EXP per grade) [S-25][S-80].
- Only the 4 lineup Fantomons need levels: **Resonance Level = the lowest level among the four**, and every
  other Fantomon automatically counts at that level [S-03][S-87][S-85]. Level the four evenly [S-03]. A deployed
  Fantomon also picks up loot automatically [S-87].
- Treat sources: Cart idle income (the Treats row, R-020), the Vendor Booth, guild plants/animals [S-26] ❓;
  Grand Treasure Hunt Level 1 reward (Basic Treats) [S-23] ❓; gift code rewards [S-04] ❓.
- SOF puts Treats last in the Cart upgrade order (Wood/Stone -> Rolla -> Ore/Sand -> Battle Essence -> Treats)
  [S-01]; see [Cart and home](cart-and-home.md).
- Levels above 100 are seasonal [S-03].

## Aptitudes

- Each Fantomon has Aptitude pages (a node tree) that raise its own stats and give the character the type's
  special stats [S-01, S-25].
- Investment order [S-01]:
  1. Max the **Main** first.
  2. Then the two Subs whose type differs from the Main.
  3. Do **not** spend on the Sub that shares the Main's type.
- An aptitude reset that refunds the materials is reported by tier D sources only ❓ [S-04, S-26].
- Season 2 focus [S-02]: DPS -> all aptitude resources into Nyxarchon (Crit Rate/Accuracy); Tank -> Aegiswing
  (Block/Block Efficiency); Support/healer -> Pandarial (Healing Boost).

## Skills: assist and Adult (Materialization)

- Every Fantomon has one skill that triggers in combat while it is Deployed (the Fandom table calls these
  "Fantomons & Skills") [S-03]. Fantomon skill damage is its own damage category, not Technique or Charm
  damage [S-03].
- **Adult evolution** unlocks at Lv 108 and "provides a massive combat boost"; it requires the Fantomon's
  skill at **Mythic rarity**, which for Nyxarchon/Aegiswing costs **one duplicate from the exchange shop**
  [S-02]. A duplicate is 60 Summon Crystals, so a Mythic Adult costs 120 crystals in total [S-85][S-20, S-24]; eog words it as "evolution needs 120 shards, which is one duplicate" [S-85].
- The skill can be raised further to **Immortal** rarity with more copies; SOF's roadmap targets Immortal
  Pandarial and Immortal Nyxarchon, and says an Immortal Nyxarchon gives roughly 30% Crit Rate and Accuracy
  through its aptitudes [S-02]. How many copies each step takes is not stated ❓.
- Non-Mythic Fantomons can also become Adult: SOF tells players without a Mythic to "Adult a filler Fantomon
  (like Armopi or Zeioletus)" [S-02]. (Tier D pages that say only Mythics evolve are wrong on this [S-04].)
- Tier D description of the Adult form in battle ❓ [S-04, S-26]: energy rings around the Fantomon icon fill
  during the fight; when full it "materializes" and uses battle skills instead of its assist skill; if it
  faints it drops back to assist mode and the gauge resets.

## Known Fantomons

Type and rarity are marked ❓ where no source states them outright; the "inferred" entries are our best fit to
the role counts in [S-25] and to the lineup icons in [S-01].

| Fantomon | Type | Rarity | Skill (assist form) | Adult / other notes | Sources |
|---|---|---|---|---|---|
| Nyxarchon ("Nyx") | Attack | Mythic | **Requiem Blast**: when a damaging Technique is used, deals Dark DMG once to one target and all enemies within 2 grids; 100% chance of 1 stack of 10% DEF Reduction (max 3 stacks) for 2 turns; at most twice every 2 turns; large targets can be hit several times | Best DPS Main: aptitudes give Crit Rate and Accuracy | [S-01], [S-02], [S-03] |
| Aegiswing ("Aegis") | Tank | Mythic | **Radiant Sanctuary**: at battle start grants the character Guardian Angel for 3 turns; when it expires, restores 50% of lost HP and grants Power Unsealed for the whole battle | Best Tank Main: Block and Block Efficiency; Adult form adds Taunt/Retribution effects ❓ [S-26]; useful in PvP | [S-01], [S-02], [S-03] |
| Pandarial ("Panda") | Support | Mythic [S-85] | **Ink Burst** ❓: at battle start reduces every Technique's cooldown by 1 turn and gives a battle-long damage boost [S-26, S-28] | Arrives on **day 46 of Season 2**; its active (Adult) skill makes it the main Deployed Fantomon for every class; "much better in 4v4" than Aegiswing. Adult skills ❓: Bamboo Gale / Verdant Spikes (damage, applies Fragility: enemies take +5% damage), Emerald Dew (heals allies within 4 grids) [S-26, S-28]. Healing Boost aptitude | [S-02] |
| Sylvaerie | Support | Legendary [S-85] | **Wind Embrace**: raises the caster's ATK and SPD for 1 turn after the caster's turn ends | Sold in the Summon Crystal shop for 18 crystals as the rotating Legendary ❓ [S-20, S-26] | [S-01], [S-03] |
| Zeioletus | Attack | Legendary [S-85] | **Lotus Step**: when a damaging Technique is used, deals Light DMG once to one target and all enemies within 1 grid and knocks them airborne; at most twice every 2 turns; +20% DMG to large targets | Named by SOF as a filler to turn Adult | [S-01], [S-02], [S-03] |
| Armopi | Tank (inferred) ❓ | Legendary [S-85] | **Armor Protection**: 1 stack of DEF Up at the end of the caster's turn; at 3 stacks, removes them and grants a shield based on the caster's DEF | Named by SOF as a filler to turn Adult | [S-02], [S-03] |
| Kels | Support (inferred) ❓ | Legendary [S-85] | **Purging Spell**: when a damaging Technique is used, deals Water DMG once to one target and dispels 1 random buff; once per turn | Not in the summon pool: bought as shards (60) in the Arena shop ❓ [S-04, S-26]; Fandom confirms the Arena Shop sells "special Fantomon shards" [S-03]. Adult "Water Drill": 50% base chance of -20% DEF for 2 turns ❓ [S-26] | [S-03] |
| Terragon | Tank (inferred) ❓ | Legendary [S-85] | **Sandstone Shot**: when a damaging Technique is used, deals Physical DMG once to one target, 50% base chance to cut its ATK by 25% for 1 turn; once per turn | | [S-03] |
| Herbote | Support (inferred) ❓ | Legendary [S-85] (S-04 says Epic) | **Emergency Aid**: if the caster starts a turn below 80% HP, heals the caster once, 50% chance to dispel 1 ailment or debuff | | [S-03] |
| Mandragora | Support (inferred) ❓ | Epic [S-85] | When a Technique is used on allies, heals 1 target once | | [S-03] |
| Falko | Attack (inferred) ❓ | Epic [S-85] | When a damaging Technique is used, deals Physical DMG once to one target and all enemies within 1 grid ("Golden Flash" [S-26] ❓) | | [S-03] |
| Boaro | Tank (inferred) ❓ | Epic [S-85] | Each time the caster has lost a cumulative 15% of max HP, grants a shield based on the caster's DEF; up to 5 times per battle | | [S-03] |
| Chomusuke | Attack (inferred) ❓ | Epic [S-85][S-26] | Extra Physical area attack after a damaging Technique, 50% chance of -15% DEF ❓ | Only in [S-26]; the name matches the KonoSuba collaboration, so it may be event-limited ❓ | [S-26] |

Aliases seen in tier D pages: "Arcanine" = Nyxarchon, "Aegis Wing" = Aegiswing, "Kells" = Kels, "Seolatus" =
Zeioletus, "Silveria" / "Sylvarie" / "Forestry" = Sylvaerie, "Pandariel" / "Pandaria" = Pandarial [S-04, S-27, S-28].

## How to obtain Fantomons

| Route | Details | Sources |
|---|---|---|
| Summon at Arborisfatum | Costs **Bond Trinkets** (the "summon tokens"). Drops Fantomons, Fantomon shards, ability food and **Summon Crystals** | [S-25], [S-20] ❓ |
| Summon Crystal exchange shop | Mythic Nyxarchon 60, Mythic Aegiswing 60, rotating Legendary (Sylvaerie) 18; Pandarial joins on day 46 of Season 2. Crystals drop at about 4.2% per pull with at least 1 per 10-pull | [S-02] (exchange shop, day 46); numbers [S-20, S-24, S-26] ❓ |
| Arena shop | Kels shards / "special Fantomon shards" | [S-03]; [S-04] ❓ |
| Bond Trinket sources | Guild shop (400 Guild Tokens, limit 2 a week, needs guild Shop Lv 3; R-114 and `docs/shop-tables.md`), Vendor Booth refreshes [S-01], Wheel of Destiny third-priority prize [S-01], Mailbox gifts (R-168), Grand Treasure Hunt Level 4 option [S-23] ❓, Delegate Tasks and Arena shop [S-20] ❓ | as marked |

Details of rates and pity: [Gacha](gacha.md#fantomon-summon-arborisfatum).

## Tier list

No tier B source ranks every Fantomon; SOF only states the top of the list. Lower rows are tier D opinion ❓.

| Tier | Fantomons | Basis |
|---|---|---|
| S | Pandarial (best Deployed for everyone), Nyxarchon (best DPS Main), Aegiswing (best Tank Main, PvP) | [S-02]; agreed by [S-26] |
| A | Kels, Zeioletus, Sylvaerie, Terragon | [S-26] ❓ ([S-27] rates Armopi, Herbote, Terragon A) |
| B | Armopi, Chomusuke, Mandragora, Herbote, Boaro, Falko | [S-26] ❓ ([S-27] puts Falko lowest) |

## Recommendation per role

| Role | Main (aptitudes) | Deployed (skill) | Subs | Aptitude spending |
|---|---|---|---|---|
| DPS (Duelist/Sorcerer lines, DPS Sage) | Nyxarchon, else any Attack Fantomon | Before Pandarial: the best skill you own (SOF used Aegiswing). After: Pandarial | One Tank, one Support, one Attack | Everything into Nyxarchon (Crit Rate/Accuracy); then the Tank and Support subs; never the Attack sub |
| Tank (Knight line) | Aegiswing, else any Tank Fantomon | Aegiswing, later Pandarial | One of each type | Everything into Aegiswing (Block/Block Efficiency) |
| Support / healer (Sage line) | Your preference or a Support Fantomon; Pandarial once owned | Pandarial once owned | One of each type | Pandarial for Healing Boost |

Sources: [S-01] (rule of thumb, sub rules), [S-02] (Season 2 focus).

## Roadmap by season

**Season 1 (Lv 51 to 100)** [S-01]
1. Unlock at Lv 51 [R-011] (Lv 50 per [S-87]); put the best Fantomon of your role's type in Main and one of each type in Sub.
2. Level the four evenly with Treats (Resonance) [S-03].
3. Buy aptitude materials and Bond Trinkets from the Guild shop every week; they are its top priority.
4. Save Summon Crystals for the Mythic of your role (DPS: Nyxarchon, Tank: Aegiswing) and then its duplicate;
   do not spend crystals on the 18-crystal Legendary ❓ [S-20].
5. Keep building Fantomons through the end of the season: they are permanent power.

**Season 2 start (Loong Haven, Lv 108)** [S-02]
- Do **not** wait 45 days for Pandarial with no Adult Fantomon.
- Own Nyxarchon or Aegiswing: buy **one** duplicate, turn it Adult immediately, then stop and save every
  crystal for Pandarial.
- Pulled the "wrong" Mythic for your class: turn that one Adult anyway (or an Epic filler); do not buy the
  other Mythic from scratch now.
- Own neither: turn a filler (Armopi, Zeioletus) Adult and save for Pandarial, to make it Adult on release.

**Late Season 2 and beyond** [S-02]

| Step | DPS classes | Tanks / healers |
|---|---|---|
| 1 | Mythic (Adult) Nyxarchon | Mythic (Adult) Aegiswing |
| 2 | Immortal Pandarial (main Deployed unit) | Immortal Pandarial |
| 3 | Immortal Nyxarchon (about 30% Crit Rate and Accuracy, frees gear affix slots) | Immortal Aegiswing |
| 4 | Mythic Aegiswing last, for PvP only | |

## Open questions
- ❓ Exact unlock level: this page follows 51 [R-011]; the publisher and eog say 50 [S-87][S-85]. Confirm on our account when it happens.
- ❓ Type of Armopi, Kels, Terragon, Herbote, Mandragora, Falko, Boaro, Chomusuke (rarities are now given by [S-85]): read the roster in game.
- ❓ Copies needed for each skill rarity step (Mythic, Divine, Immortal) and the Adult cost for non-Mythics.
- ❓ Bond Trinket cost per summon and per x10; Summon Crystal price of Pandarial (assumed 60).
- ❓ Aptitude node costs per level and the real stat values per type.
- ❓ Whether zeroluck's "oil" (Garden) is Fresh Essence; what the 12.04% "Legendary other" line of the summon table is [S-80].

## Sources
- [S-01] "Fantomons" page (text and lineup screenshot), Wheel of Destiny priorities, Cart order
- [S-02] Section V "Fantomons" (Adult evolution, Pandarial timing, long-term roadmap)
- [S-03] Fandom "Fantomon", "Fantamons", "Seasonal Systems", "Skill Overview"
- [S-04] sword-x-staff.wiki Fantomon guide and tier list (leads only)
- [S-20] [S-23] [S-24] EOG.GG gacha, Grand Treasure Hunt and tips pages
- [S-25] zeroluck.gg summoning, currencies and companions (pet) pages
- [S-80] zeroluck second reading (roster counts, evolution stages, Treat grades, guild facilities); [S-85] eog.gg hub (rarity per Fantomon, slot weights, crystal costs, Lv 108); [S-87] official Tips post
- [S-26] BlueStacks Fantomon guide; [S-27] Mobi.gg tier list; [S-28] LDShop Pandarial page
- Rules R-011, R-020, R-066, R-114, R-168; `docs/shop-tables.md`
