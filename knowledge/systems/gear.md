# Gear

<!-- index: Read before enhancing, replacing, dismantling, refining or selling gear, and to judge which affixes are worth keeping -->

> **Summary:** Five gear slots carry most of a season's power. Gear comes from daily dungeons (gear and shards),
> the Cart and the market; it is enhanced with Raw Ore, Refined Ore and Rolla, evenly in 5-level bands (R-092).
> Enhancement level is the heaviest input to the end-of-season Astral Pact score, so never stop enhancing. From
> Season 2, affixes can be re-rolled (Divinecraft Stones) and inherited onto new gear: 1-2 good affixes per piece
> is the affordable target.
> **Applies:** all seasons; refinement and cross-season inheritance from Season 2
> **Related:** [Gems](gems.md), [Dungeons](dungeons.md), [Astral Pact](astral-pact.md), [Seasons](seasons.md),
> [Cart and home](cart-and-home.md), [Material Realms](material-realms.md), [Auction House](auction-house.md),
> [Relics](relics.md); rules R-023, R-088, R-092, R-119, R-165

## Slots

| Slot | In-game names seen | Notes | Source |
|---|---|---|---|
| Weapon | Main Hand (sword, staff, blade ...) | Class-typed: swords for the Warrior line, staffs for the Mage line; the data has two weapon types, Sword and Wand [S-80] | [S-01][S-02] |
| Offhand | Off-hand (Shield, Glove, Book or Ball [S-80]) | Gear starts with 4 slots; the Off-hand opens after reaching Class II [S-87]. Not yet unlocked on our account at Lv 37; takes every gem colour | [R-023][S-01][S-87] |
| Helmet | Headpiece | | [S-01][R-092] |
| Armor | Body Armor, chest | | [S-01][S-02] |
| Boots | Boots, leggings | | [S-01] |

Inheritance and comparison work only within the same kind (sword to sword, shield to shield) [S-02]. Weapons of
another class can score higher and are equipped for seasonal ranking pushes after a lossless class change [S-03].

## Rarities

Common, Rare, Epic, Legendary, Mythic, Divine, in rising order [R-165][S-02].

A database site describes six quality colours instead and gives the affix ("substat") lines and the roll
multiplier on a line's base value for each [S-80] ❓:

| Colour | Substat lines | Roll multiplier |
|---|---|---|
| White | 0 | 0.7 to 0.8 |
| Blue | 1-2 | 0.7 to 0.9 |
| Purple | 3 | 0.8 to 1.0 |
| Orange | 4 | 0.8 to 1.15 |
| Gold | 4 | 0.8 to 1.25 |
| Red | 4 | 0.8 to 1.25 |

- The site does not say how the colours map to the rarity names; white to red most likely equals Common to
  Divine in order ❓. Its advice: quality beats enhancement; enhance white and blue only as a stopgap [S-80].
- Counts in the data: 629 pieces, 28 sets, each with a 2-piece and a 4-piece bonus [S-80]. Set names and
  bonuses per dungeon (eog's translations): [data/dungeon-gear-sets.json](../data/dungeon-gear-sets.json) [S-85].
- Tables: [data/gear-tables.json](../data/gear-tables.json).

- Divine pieces of one dungeon form a set with 2-piece and 4-piece bonuses (Season 2 sets: Assimilation,
  Indomitable; Ephemeral, Cratering; Masterful, Pursuit; Trial by Fire, Cold) [S-02].
- Only Mythic and Divine gear can be refined; rarity does not change the affix values that can roll [S-02].
- The first Season 2 dungeon (Demonseal Gorge) drops Mythic at most [S-02].

## Where gear comes from

| Source | What | Notes | Source |
|---|---|---|---|
| Daily dungeons | Gear pieces and gear shards, by difficulty | Highest rarity from the highest difficulty; gated by level and power. 2 free runs a day, unused runs bank up to 6 | [S-01][S-52][S-53] |
| Cart | Random gear over time | A higher Cart level raises the chance of high-tier Legendary gear; on a new dungeon's opening day Cart Legendaries can already beat the last dungeon's Mythic (one was 15K CP above) | [S-01][S-02] |
| Shards | Combine into a piece; tradable | Old-dungeon Divine shards get cheap; buy them when you need gear rating | [S-02] |
| Commercium (Trading House, Auction House) | Gear and shards from other players, for Dawnium; premium bids need Luminium | Unlocks at Lv 40; only gold-quality gear and above can be auctioned ❓ | [S-03][S-54] |
| Map chests, quests, mini-dungeons | Early gear | | [R-076][R-071] |

Selling: gear and shards you do not need are the F2P Dawnium income, especially from the first dungeon of a
season, whose gear is outclassed within two weeks [S-02][S-01].

## Enhancement

- Character, gear slot, Enhance. Cost per step: Raw Ore and Rolla; higher steps add Refined Ore [R-023].
- **Band rule:** raise all equipped pieces evenly in 5-level bands; lowest piece first [R-092].
- **Gear Resonance:** a set bonus that activates each time all pieces reach +5, +10, +15 ... (e.g. HP +2%);
  activate it whenever a band completes [R-119]. The publisher says the same: every 5 enhancement levels across
  all slots unlocks a Resonance step, a percent boost to base stats, so upgrade evenly [S-87]. A database site
  has a step every 5 gear levels cycling HP, ATK, DEF, SPD, 240 steps in all, and calls each "+20% flat"
  [S-80] ❓; that size disagrees with the small per-band bonus the rule shows (tier A), which this page follows.
- Enhancement levels stay on the slot when a piece is replaced, so replacing loses nothing [R-088][S-87]. The
  cap rises with character level [S-87].
- Enhancement above +100 is seasonal and resets to +100 at season end [S-03]. Season 2 examples show +160 to +180
  [S-02]. The game data runs to +250 [S-80]; that is most likely the data ceiling, not a live cap, and the
  seasonal figures above (tier B) are what this page follows.
- Cost of one level on one piece (Rolla / Raw Ore / Refined Ore) [S-80] ❓: +1 70/35/0; +10 160/80/30; +20
  1,160/580/170; +40 4,160/2,080/330; +250 200,000/100,000/550. Rolla is always twice the Raw Ore. Total +0 to
  +250: 17.4M Rolla, 8.7M Raw Ore, 22,280 Refined Ore. More points: [data/gear-tables.json](../data/gear-tables.json).
- Ore sources: Cart (Raw Ore per hour), Material Realms (the ore realm; the standard purchase split is "4 Ore, 2
  or 4 Rolla, 4 Battle Essence, 4 Sand" extra tools a day), stamina gathering, dismantling, Guidance quests, Vault
  and Vendor Booth [R-092][R-165][S-01].
- Timing inside a season: relic Sand first, then from mid-season put stamina and realm purchases into Ore, because
  gear catches up with relics; near the end, gear enhancement is the best Primostar investment [S-01][S-02].

## Item level and seasonal scaling

| Dungeon (season) | Gear level | Example power (Mythic / Divine) | Source |
|---|---|---|---|
| Hellhold (S1) | 190 | Divine weapon 617K CP, 169K base ATK | [S-03] |
| Demonseal Gorge (S2 pre-season) | 130 | Jade Sword +165: 166K (Mythic only) | [S-02] |
| Warlord's Rest (S2) | 165 | Ink Blade +165: 428K / 508K | [S-02] |
| Cloudcrest Temple (S2) | 195 | Blessed Divider +165: 761K / 842K | [S-02] |
| Bladeshire (S2) | 225 | Flame Blade +180: 1.57M / 1.69M | [S-02] |
| Celestship (S2) | 250 | Qilin's Oracle Staff 2.33M / Qilin's Holy Sword 2.59M | [S-02] |

- Each new dungeon roughly doubles the power of a piece; Divine is worth about 80K to 260K more than Mythic of the
  same dungeon [S-02].
- After the season, seasonal gear is scaled down to level 100: the 617K Hellhold weapon drops to 64.2K CP and
  15.7K base ATK. "Most of your CP during a season will come from seasonal gear" [S-03].

## Affixes

Gear carries random affix lines (0 to 4 by quality, see [Rarities](#rarities)). eog's list of 140 affixes:
[data/equipment-affixes.json](../data/equipment-affixes.json) [S-85]. A community table (labelled Champion III, Season 2) gives four groups, the
chance that one specific affix appears on a roll, and the roll range from low to high [S-02]:

| Group | Affixes in group | Chance per specific affix | Whole group |
|---|---|---|---|
| Standard | 20 | 4.750% | 95.0% |
| Dual high-roll | 7 | 0.343% | 2.401% |
| Conditional / conversion | 13 | 0.138% | 1.794% |
| Trigger / unique | 12 | 0.067% | 0.804% |

**Standard (one stat):**

| Affix | Low | High |
|---|---|---|
| HP %, ATK %, DEF %, SPD % | 12% | 18.7% |
| Crit Rate, Crit RES, Block Rate, Accuracy | 4.8% | 7.5% |
| Crit DMG | 7.2% | 11.2% |
| Healing Boost | 9.6% | 15% |
| Flat ATK, DEF, Effect RES, Effect Hit Rate, Elemental Mastery, Elemental RES, Physical Mastery, Physical RES | 3.42K | 5.36K |
| Flat SPD | 2.74K | 4.28K |
| Flat HP | 17.1K | 26.8K |

**Dual high-roll (two stats on one line):**

| Affix | Stat 1 | Stat 2 |
|---|---|---|
| Crit Rate + Crit DMG | Crit Rate 9.6-15.3% | Crit DMG 14.4-23% |
| Crit Rate + Accuracy | Crit Rate 9.6-15.3% | Accuracy 9.6-15.3% |
| Block + Efficiency | Block Rate 9.6-15.3% | Block Efficiency 14.4-23% |
| Crit RES + Block | Crit RES 9.6-15.3% | Block Rate 9.6-15.3% |
| Mitigation + Healing | DMG RES 4.8-7.68% | Healing Boost 19.2-30.7% |
| PvE damage package | PvE Bonus DMG 9.6-15.3% | PvE DMG RES 9.6-15.3% |
| PvP damage package | PvP Bonus DMG 9.6-15.3% | PvP DMG RES 9.6-15.3% |

**Conditional / conversion:**

| Affix | Effect | Low | High |
|---|---|---|---|
| Debuff Punisher | Technique DMG to enemies with debuffs | +15% | +22.5% |
| Freeze / Stun Punisher | Technique DMG to frozen and stunned enemies | +15% | +22.5% |
| Airborne Punisher | Technique DMG to airborne enemies | +15% | +22.5% |
| Shield Breaker | Technique DMG to shielded enemies | +14.4% | +21.6% |
| Anti-Summon Damage | DMG to enemy summons | +14.4% | +21.6% |
| Shielded Defense | Less Technique DMG taken while shielded | 14.4% | 21.6% |
| Counterattack Damage | Counterattack skills deal more DMG | +12.6% | +18.9% |
| Collision Damage | Collision DMG | +12% | +18% |
| SPD to ATK | Converts SPD into ATK | 9.6% | 14.4% |
| DEF to ATK | Converts DEF into ATK | 7.5% | 11.2% |
| Effect Hit to ATK | Converts Effect Hit into ATK | 7.5% | 11.2% |
| HP to ATK | Converts HP into ATK | 1.5% | 2.25% |
| Effect RES to DEF | Converts Effect RES into DEF | 7.5% | 11.2% |

**Trigger / unique** (the % is the trigger chance):

| Affix | Trigger | Low | High |
|---|---|---|---|
| Dodge (unique) | When taking DMG: dodge chance; up to 6-10 triggers per battle | 8.4% | 12.5% |
| Wind Shield (unique) | At the start of battle | fixed effect | |
| Summon: Gnoll Bruiser | Before the turn starts | fixed effect | |
| Summon: Gnoll Flinger | Before the turn starts | fixed effect | |
| Blazing Burst | Dealing Crit DMG with a Technique | 30% | 45% |
| Meteor Strike | At the start of the wearer's turn | 30% | 45% |
| Surging Blast | When killing an enemy | 30% | 45% |
| Thunder Strike | An enemy within 3 grids moves | 23.1% | 34.5% |
| Dodge Chain | Single-target Technique DMG | 20.1% | 30% |
| Electric Arc | When taking Technique Crit DMG | 15% | 22.5% |
| Shock Blast | When blocking a Technique attack | 15% | 22.5% |
| Fire Ring | When taking Technique DMG | 4.95% | 7.5% |

### Seasonal bonus on affixes

- The first dungeon of every season is pre-season: its gear is not "seasonal gear" and its affixes sit at their
  worst value [S-02].
- Gear from every later dungeon of the season gets a bonus on affixes: "200% rate for unique lines and 20% for
  standard lines" [S-02].
- An affix found on first-dungeon gear can be inherited onto seasonal gear and then receives the bonus, so good
  affixes from the first dungeon are still valuable [S-02].

### Top affixes per class

| Class line | Look for (best first) | Source |
|---|---|---|
| Duelist | Crit Rate + Crit DMG; SPD / HP / DEF converted to ATK; Crit Rate + Accuracy; Dodge (from Loong Haven); Technique DMG to debuffed enemies | [S-02] |
| Knight | Block + Block Efficiency; any Block Rate or Block Efficiency line. In Season 2 prefer Block Efficiency over block chance | [S-02] |
| Sorcerer | Crit Rate + Crit DMG; SPD / HP / DEF converted to ATK; Crit Rate + Accuracy; "Flash" (from Loong Haven); Technique DMG to debuffed enemies | [S-02] |
| Sage, general | Technique DMG to debuffed enemies; SPD / HP / DEF converted to ATK | [S-02] |
| Sage, DPS | Crit Rate + Crit DMG; Crit Rate + Accuracy | [S-02] |
| Sage, healer | Block + Block Efficiency; DMG reduction + Healing Boost | [S-02] |

- "Flash" is not a line in the affix table; it may be the table's Wind Shield or another unique line ❓.
- A Fantomon can replace affixes: an Immortal Nyxarchon gives roughly 30% Crit Rate and Accuracy, "freeing up gear
  affix slots" [S-02]. See [Fantomons](fantomons.md).

## Affix Refinement and Divinecraft Stones (Season 2+)

- Refinement re-rolls the affixes of a Mythic or Divine piece; lines can be locked so they are kept [S-02].
- It costs Divinecraft Stones, which come only from dismantling gear [S-02].

| Locked lines | Stones per re-roll |
|---|---|
| 0 | 100 |
| 1 | 300 |
| 2 | 1,200 |
| 3 | 3,200 |

- Rule of thumb: 1-2 good affixes per piece is enough; 3-4 is whale territory and will bankrupt an F2P or light
  spender. Fix other progression first [S-02].

## Affix Inheritance (Season 2+)

- **Season Inheritance:** move affixes from an old piece to a new piece of the same kind, free of charge [S-02].
- **Cross-Season Inheritance:** from Season 2 on, all affixes can be inherited onto future seasons' gear [S-02].
- **Warning: the source piece is destroyed.** Check the direction twice: the good affixes must move onto the new
  gear, not the other way round [S-02].
- Use: hunt top affixes for your own class and for other classes in the first dungeon, then carry them from
  dungeon to dungeon; watch the Auction House for pieces whose seller missed the affix value [S-02].
- Two views on the first dungeon: sell its shards and gear for sure Dawnium, or keep rolling its Mythic gear for
  affixes with a high ceiling. Either way, making the next dungeon's power threshold comes first [S-02].

## +drop gear ("dungeon reward" stats)

- Some gear lines raise dungeon rewards: a chance to double the rating reward (shards and gear) and a chance to
  raise the rarity of a drop (a Legendary becomes a Mythic) [S-01].
- Keep such pieces even if weaker, as long as you still meet the newest dungeon's power threshold; equip them
  before entering the highest dungeon you can enter, and ask for a carry [S-01].
- The stat is region-specific: an Aqualis line works only in Aqualis dungeons [S-01].
- Stack it with the Lucky Statue relic (Grand Treasure Hunt; "Dungeon: 2x Rating Reward Rate") kept in the main
  relic line for the 20% resonance bonus, and with the Astral Pact nodes "[Dungeon] Gear Drop Ascension Rate +3%"
  and "Dungeon evaluation double reward +2%" [S-01][S-51].
- Keep using the set after you are geared: extra shards sell for Dawnium [S-01].

## Dismantling

- Alchemy Pot at Home, Dismantle tab, from Lv 12 [S-87]. It only takes gear weaker than what is equipped; Common, Rare and Epic give Raw Ore,
  Epic and above also Refined Ore [R-165].
- From Season 2 dismantling also yields Divinecraft Stones [S-02].
- When a new dungeon opens, dismantle the previous dungeon's shards [S-52] (or sell them first if they still have
  a price [S-02]).

## Gem sockets

- Sockets are per piece: 2 on level-130 gear in Season 2, at most 4 [S-85]; SOF has one socket per piece in
  Season 1 and one more each season [S-01][S-02]. See [Gems](gems.md).

## Gear and the Astral Pact

- "Season Gear Level" is the biggest of the five rating categories: 38 points per average enhancement level, up to
  7,220 points at level 190 in Season 1, out of about 17,200 [S-51][S-01].
- The Gear tab has its own rating: two Divine and three Mythic pieces from Hellhold give SSS in Season 1; two
  Hellhold Divine plus two Aquorigin Divine plus one Hellhold Mythic also reach SSS on aggregate score [S-02].
- See [Astral Pact](astral-pact.md).

## Open questions

- ❓ How the six quality colours of [S-80] map to rarity names, and whether refinement re-rolls all unlocked lines at once.
- ❓ Divinecraft Stones per dismantled piece by rarity.
- ❓ Exact meaning of "200% rate" (value multiplier or roll chance) for unique lines.
- ❓ Live enhancement cap per season (+100 base; +165 to +180 seen in Season 2; +250 in data [S-80]).
- ❓ What gear Resonance's "+20%" in [S-80] applies to.
- ❓ The full text of the Season 2 Divine set bonuses (the infographic is too small to read reliably).

## Sources

- [S-01] sections 2 (combat power, +drop gear), 3, 4 (Cart gear), 6
- [S-02] sections I, III (refinement, inheritance, top attributes), infographics "Season 2 gear power comparison"
  and "Gear affixes"
- [S-03] Seasonal Systems, Commercium, Everything about Class Change
- [S-51] gear weight; [S-52] dismantle tip; [S-53], [S-54]
- [S-80] zeroluck.gg gear page ([notes](../sources/notes/zeroluck.md)); [S-85] eog.gg data ([notes](../sources/notes/eog.md)); [S-87] official Handbook Vol. 1
- Rules R-023, R-071, R-076, R-088, R-092, R-119, R-165
