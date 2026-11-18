# Skills: techniques and charms

<!-- index: Read to understand how skills are obtained (Prayer), equipped (4 + 4 slots, loadouts), levelled (Battle Essence), ascended (shards, vouchers), what resets each season and how auto-battle uses them -->

> **Summary:** You pull skills, not characters. A loadout is 4 Techniques (active) and 4 Charms (passive). Skill **levels** cost Battle Essence, are capped by character level and are seasonal above Lv 100; skill **ascension** (Rare to Immortal, 10 of the skill's own shards per step) is permanent. Level everything with Quick Upgrade, ascend whenever a skill shows "!", pull only x10 on the Standard Prayer through mae's script, and keep Skill Shard Vouchers for skills that survive into later class tiers.
> **Applies:** all seasons
> **Related:** [Classes overview](classes-overview.md), [Gacha](gacha.md), [Currencies](currencies.md), [Seasons](seasons.md), [Astral Pact](astral-pact.md), [Material Realms](material-realms.md), [data/skills.json](../data/skills.json), rules R-037, R-104, R-115, R-093, R-080

## Kinds of skill

| Kind | What it is | Where it sits |
|---|---|---|
| Technique | Active skill: an attack, heal, buff, move or summon cast in battle, with a range, an area on the grid and usually a cooldown | 4 technique slots (left column of the loadout) [R-037] |
| Charm | Passive: a stat bonus or a triggered effect (extra hit, shield, revive, debuff) | 4 charm slots (right column) [R-037] |
| Passive / class trait | Built into the class (Crit Rate for Duelists, Block for Knights, and so on) | Class page [S-03][S-10] |
| Gear skill | Comes with a piece of gear | [Gear](gear.md) [S-03] |
| Fantomon skill | The deployed Fantomon's own skill | [Fantomons](fantomons.md) [S-01] |

- Damage is booked in categories: Technique Damage, Charm Damage, Buff Damage, and Unclassified Damage (Fantomon, NPC and gear skills) [S-03]. Affixes such as "Technique damage dealt to enemies with debuffs" only boost the first category [S-02].
- Every skill is built from a **flat part** ("Basic Damage", the number on the right of the skill card) and a **percentage part** (on the left), or only one of them [S-03].
- Every skill carries **tags**: DMG, Knockback, Drag, Move, Self Buff, Ally, Buff, Heal, Dispel, Debuff, Ailment, Summon, Shield, Stats, Burn, Counterattack, Revive. Some effects only apply to skills with a given tag [S-03].
- The game has more than 200 skills [S-03]; a database site counts 238 player skills: 85 Legendary, 78 Epic, 75 Rare [S-10][S-80]. The publisher said "over 200" in April and "300+" at launch [S-87]; eog's database lists 361 across all classes and tiers, with cooldown and damage per quality: [data/skill-database.json](../data/skill-database.json) [S-85].
- Each class tier adds its own set. Tier 1 has 13 Techniques and 13 Charms per starting class; each Tier 2 class page lists 6 Techniques and 5 Charms [S-03]. A Tier 3 class has four Legendary skills (2 Techniques, 2 Charms) [S-03].
- You can equip skills of your current class and of the lower classes on your line: Tier 1 Mage skills stay usable as Sorcerer, Archmage and beyond, and several stay in the best builds [S-03][S-11].

## Slots and loadouts

- Character > Skill opens the loadout: 4 technique slots on the left, 4 charm slots on the right [R-037]. Fandom agrees: "only 4 skill slots and 4 charm slots" [S-03].
- Slots open with level: our Lv 13 character still had the 4th charm slot locked [R-080]. Exact unlock levels of each slot ❓.
- Equip: Technique or Charm tab, tap a card, Equip, tap an empty slot. A filled slot's button reads Replace; the bot never presses Replace on a charm card [R-037][R-158].
- Empty charm slots show a red badge on the profile's charm row; fill them [R-080].

### Loadouts

- The game stores several saved loadouts so you can swap whole builds: per element for a Mage, single-target against bosses, AoE for farming, PvP, healer for parties [S-03]. One source says there are up to seven loadout slots [S-11] ❓.
- The game also shows recommended loadouts per class (a "Rcmd. Loadouts" screen exists in our navigation, R-080); the three conversion options of a lossless class change follow the same archetypes [S-03].
- Changing loadout is free; that is why a "mechanic" (Shield, Taunt, freeze lock, Lifesteal) can be swapped per fight while a "style" (your stats) cannot [S-03].

## Getting skills: the Prayer

Skills come from the Prayer statue at home (the goddess Statue furniture beside the "Class to Unlock" stone) [R-093]. The screen has tabs Prayer / Exchange / Goals, a banner selector, a counter "Prayers Today n/10000", a "200 Prayers Bonus" and a pity counter [R-093]. Full banner detail: [Gacha](gacha.md).

| Banner | Currency | Cost | Pool | Notes | Sources |
|---|---|---|---|---|---|
| Standard (blue orb) | Stellatie | x10 = 10 Stellatie | The skills your current class can use: its own tier plus the lower tiers of its line | The only banner our bot uses, x10 only, through mae's pull script | R-093, [S-10][S-15] |
| Affection / Friend Prayer | Affection tokens (red) | x10 = 250 | ❓ | Not used by the bot | R-093, [S-10] |
| Premium (pink orb) | Covenite | ❓ | Skills of your current class only; each new class has its own, selectable premium pool [S-85] | Unlocks after clearing Verdantglade and making the Tier 2 class change (so in Cinder Ridge) [S-85]. Covenite is a skill selection ticket from Molly's Deals, the Wheel of Destiny [S-01], Chaos Invasion [S-03] and the Arena Shop [S-42]; eog's reading, "earned from Standard pulls, not bought with Dawnium" [S-15][S-85], is lower tier and not followed | [S-11][S-15][S-85] ❓ |

Rates (two tier C sources that disagree; a second reading of each site repeated its own numbers [S-80][S-85]; both unverified against the in-game rate card; zeroluck gives the Premium banner the same rates [S-80]):

| Result | zeroluck.gg [S-10] | EOG.GG [S-15] |
|---|---|---|
| Legendary skill | 2.41% | 1% |
| Epic skill | 7.9% | 7% |
| Rare skill | 24% | 22% |
| Common skill shard | 65.69% | (rest) |

Pity and guarantees:

- **200 Prayers Bonus: a Legendary skill of your choice** every 200 Standard prayers [R-093][S-11][S-04]. One source says the choice is among Tier 1 Legendaries [S-15] ❓.
- Rare or better within 10 pulls, Epic or better within 30, Legendary within 70 [S-15][S-85] ❓. zeroluck states no pity [S-80].
- Pity is account-wide and is not reset by changing class [S-15] ❓.
- What you can pull depends on your class and tier [S-10]. That is the point of the Class Rollback: dropping to a lower tier shrinks the pool so pulls land on low-tier skills [S-03].
- A skill you already own arrives as shards of that skill, which feed ascension (below).

Stellatie sources seen or reported: Daily Sign-in 10 a day [R-097]; Prayer Goals milestones for total Standard prayers [R-093]; Guild Shop (500 Guild Tokens, limit 3); Vendor Booth Vault at a discount [S-03]; Molly's Deals [S-01]; map chests and free Wheel of Destiny spins; gift codes. See [Currencies](currencies.md).

Pull policy:

- Only `python -m sxs pray --pulls N --handler-approved`, started by mae, x10 only, Standard banner, Stellatie only; never the "+" button, never Dawnium [R-093].
- Late in a season stop pulling and bank Stellatie for the next class tier: new-tier skills replace most of the old ones [S-01].
- Do not buy Stellatie with Dawnium in Verdantglade: the early pool is low-tier skills [S-11][S-15] ❓.

## Levelling skills (Battle Essence)

- Each Technique and Charm has a level. Levelling costs **Battle Essence** (purple orb) and raises the flat part of the skill [R-037][S-03].
- Skill level is capped by character level ("Unlocks at Character Lv. 6") [R-037]. A new technique starts at Lv 1; Lv 1 to 10 costs about 490 Battle Essence [R-037].
- **Quick Upgrade** on the Skill page levels every equipped skill, charms included, as far as Battle Essence allows; press it whenever any skill icon shows a blue arrow. One press raised every skill 2 to 4 levels for about 3K essence [R-104].
- High skill level is one of the cheapest large power gains, and the flat part protects your damage floor when a debuff cuts your ATK [S-03].
- Not every skill grows well: some Charms have low growth, and lower-class skills grow less than current-class skills [S-03]. Level what is equipped first.
- Skill level above 100 is seasonal: it resets to 100 at the season change [S-03]. "Season skill level" is one of the five things the [Astral Pact](astral-pact.md) rates at season end [S-01].
- One guide says upgrades belong to the slot and a swapped-in skill inherits the level [S-11]; our game shows per-skill levels with new techniques at Lv 1 [R-037]. The publisher's handbook also says Battle Essence "upgrades skill slots" [S-87] (tier B). The rule is tier A, so this page follows the rule; check again if a swapped-in skill ever shows the old level.

Battle Essence sources: the Cart (hourly) [R-020]; overworld pickups at 5 stamina each [R-106]; the Battle Essence Material Realm (guides buy 4 extra tools a day in the 4-2-4-4 or 4-4-4-4 split) [S-01][S-02]; Battle Essence Caskets from mail and rewards (T1 400, T2 530, T4 840 each) [R-169]; Skill Goals pay out for essence spent (8.8K, 13.1K, ...) [R-116]. Do not spend Cart upgrades on the Battle Essence row before Wood and Stone [S-01], R-136.

## Ascending skills (shards)

- Ascension raises a skill's star and quality with the skill's **own shards**: 10 shards per step, no Dawnium. Seen: Rare -> Rare 1-star -> Epic [R-115].
- A "!" on a skill icon (equipped or in the bag) means it can ascend: do it [R-115].
- Qualities: **Rare -> Epic -> Legendary -> Mythic -> Divine -> Immortal** [S-03]. eog counts the ascension steps inside each quality as Rare 2, Epic 3, Legendary 4, Mythic 6, Divine 8, Immortal 11 (34 in all) [S-85] ❓. A skill keeps its *base* rarity for class-change conversion however far it is ascended [S-03].
- A star inside a quality raises only the flat part, about 15% per star (15-30% depending on the skill). A quality step raises both flat and percentage parts: about 25% for Techniques and 20% for Charms [S-03].
- Worked examples [S-03]: Boiling Bloodlust gives 30% Crit Rate at Epic, then about 38 / 47 / 59 / 73% (in game 70% at Immortal). Blade of Lament gives 2.44% lifesteal at Legendary, then about 2.93 / 3.51 / 4.22%.
- Because flat and percentage are each about half of a skill, one star on a skill that does 30% of your damage is only about +5% total damage. The quality step is what matters: push a skill to the next quality, then stop and move to another skill [S-03].
- **Ascension is permanent**: it survives the season reset [S-03].

### Skill Shard Vouchers

- A voucher stands in for shards of a skill you choose, so it is the only way to aim ascension [S-01][S-03].
- Sources: top-priority pick on the Wheel of Destiny [S-01]; events and packs.
- Rules of use:
  1. Do not spend early vouchers on Tier 1 or Tier 2 skills; hold them for Tier 3 and later [S-15] ❓, in line with [S-01].
  2. Spend them on core skills that **persist across tiers**. The model case is the Conqueror charm Piercing Assault: worth every voucher even if you change class at Tier 5 [S-01].
  3. Stop at a quality breakpoint, then switch skills [S-03].
  4. Your voucher and relic-element choices decide which build you are strong in; switching build later costs power [S-03].

### Skills that stay in use across tiers

Most skills become obsolete when a new class tier arrives [S-01]. These are still in recommended builds one or more tiers later, so shards and vouchers in them last (lists from tier D build guides unless tagged):

| Line | Skills that persist | Seen in builds at |
|---|---|---|
| Sorcerer | Mana Surge, Void Bubble, Water Assault, Wind's Delight, Tempest Sphere, Lightning Chain, Light of Dawn, Fiery Star Trail, Heart of Flame; Radiance Sear, Howling Hurricane, Meteoric Flames (from Tier 3) | Tier 3 [S-11][S-12], Tier 5 [S-11] |
| Sage | Healing Touch, Void Blessing, Radiant Restoration, Resurrection, Healing Mastery, Shadow Erosion, Shadow Impact, Dark Bullet, Mana Surge; Shadow of Termination, Abyssal Hand, Frenzy Totem (from Tier 3) | Tier 3 [S-11][S-04], Tier 4 [S-16] |
| Duelist | Insightful Eye, Indomitable Will, Flame Aura; Piercing Assault (from Tier 4) | Tier 4 [S-11], beyond [S-01] |
| Knight | Luminous Shield, Valor Surge, Heart of Challenge, Block Awareness; Desperate Protection (from Tier 3) | Tier 4 [S-11] |

## What resets and what stays

| Item | At season change | Source |
|---|---|---|
| Skills you own | Kept | [S-03] |
| Skill ascension (stars, quality) | Kept: permanent power | [S-03] |
| Skill level | Reset to 100 if above | [S-03] |
| Usefulness of old skills | Drops: the new class tier's skills replace most of them | [S-01] |
| Prayer pity counter | ❓ | |

SOF's guide files "Skills" under seasonal power for this reason: the levels reset and the kit turns over each tier, even though ascension itself is kept [S-01].

## How auto-battle uses skills

- All battles are automatic; the bot only starts, minimises or waits [R-001].
- Fights run in turns on a grid. Skill text is written in grids: "1 enemy within 4 grids", "1x5 area in front", "all enemies within 2 grids of the target grid" [S-03]. The AI moves the character, picks targets and casts [S-03].
- Cast order can be changed, so slot order is the rotation you set [S-03]. Put buffs before the hit they boost (Energy Burst makes the *next* damaging Technique deal 50% more), pulls before AoE (Cyclone, Gravity Pull), and Erosion finishers last (Shadow of Termination) [S-03][S-04].
- Techniques have cooldowns. Some say "Zero Initial CD" (ready on turn one: summons, Luminous Shield, Guardian Ring) and some cast once before or at the start of battle (Valor Surge, Heart of Challenge) [S-03]. A few have no cooldown at all (Flickering Blade) [S-11] ❓. You cannot use all four techniques every round [S-03].
- Cooldown tools: the Archmage charm Rapid Cast (first technique one turn earlier) [S-11][S-12] ❓, the Fantomon Pandarial (cuts cooldowns at battle start) [S-14][S-02].
- "(Prioritizes large targets)" skills go for bosses; multi-hit skills hit large bodies several times (Water Assault, Ricocheting Shield) [S-03].
- "Base chance" effects (Frozen 40%, Immobilize 30%, Erosion 50%) are modified by your Effect Hit Rate [S-03][S-11].

### Status effects named in skill text

| Effect | Meaning | Applied by (examples) | Source |
|---|---|---|---|
| Frozen | Target loses its turn | Ice Spike, Frosty Nova, Water to Ice | [S-03] |
| Wet | Raises the chance to be Frozen | Aqua Vortex | [S-12] ❓ |
| Immobilize | Cannot move | Iron Thorn | [S-03] |
| Stun | Loses its turn | Ricocheting Shield, Stunning Strike | [S-03] |
| Taunt | Must attack the taunter | Heart of Challenge | [S-03] |
| Burn (on grids) | Burning tiles damage whoever stands on them; one burn per tile | Flaming Path, Raging Wildfire | [S-03][S-12] |
| Erosion | Stacking Dark damage-over-time lasting 3 turns [S-85] that some skills set off at once | Dark Bullet, Shadow Erosion, Shadow Impact, Shadow of Termination | [S-03] |
| Weakened | Target deals less | Weakening Hex | [S-03] |
| Armor Break | Target's defence cut | Leap Attack | [S-03] |
| Cold | Stacking Water debuff | Ripple Impact | [S-03] |
| Sigil | Duelist mark on a target | Shattering Sigil | [S-03] |
| Flame | Ally buff | Flame Aura | [S-03] |
| Airborne, knockback, drag, action delay | Displacement and turn-order control | Heavy Impact, Unstable Aura, Cyclone, Wind's Shadow | [S-03] |
| Indomitable, Revitalization, Dodge | Survival buffs that cannot be dispelled | Indomitable Will, Resurrection, Void Bubble | [S-03] |
| Doom DMG | Damage type that deals +100% to shields and summons | Flash Dash, Fire Slash, Fiery Star Trail, Light of Dawn | [S-03][S-85] |

Heals scale with max HP [S-85]. All 70 skill keywords: [data/skill-database.json](../data/skill-database.json).

### Skill Test

- A damage dummy at Home > Character > Skills > Test, from Lv 40: a Boss with unlimited HP, no element, 50 rounds [S-85]. Use it to compare loadouts. A loadout cannot be named "Test" [S-85].
- eog's test result: 40 Elemental or Physical Mastery is about +1% damage; Wind's Delight tested best for Sorcerer [S-85] ❓.

Knocking melee enemies back or delaying them denies them the "proactiveness" (energy) to use their skills, which is the idea behind Wind builds [S-03].

## What to do, in order

1. Fill every open technique and charm slot (badges on the profile) [R-080].
2. Press Quick Upgrade whenever a blue arrow shows [R-104].
3. Ascend every skill showing "!" [R-115].
4. Claim Skill and Prayer Goals [R-116][R-093].
5. Build one loadout per element or purpose and use the one the enemy is weak to [S-03].
6. Keep vouchers for persistent skills; stop each skill at a quality step [S-01][S-03].

## Open questions

- ❓ Unlock levels of the 4 technique and 4 charm slots.
- ❓ Number of loadout slots (seven per one tier D source).
- ❓ True Standard Prayer rates and pity (zeroluck [S-80] and eog [S-85] still disagree after a second pass); read the in-game rate card.
- ❓ Premium banner: Covenite cost per pull; confirm the unlock in game.
- ❓ Whether the 200-prayer pick covers every Legendary in the current pool or only Tier 1.
- ❓ How many shards one Skill Shard Voucher is worth and whether it has a rarity.
- ❓ Shards needed per step above Epic (10 per step seen up to Epic).
- ❓ Exact rule for cast order (slot order, cooldown order or AI priority). Cooldowns per skill are now in [data/skill-database.json](../data/skill-database.json) [S-85], unchecked in game.
- ❓ Whether the Prayer pity counter resets with a season.

## Sources

- [S-01] permanent vs seasonal power; skill vouchers; Wheel of Destiny priority; Material Realm split
- [S-02] gear affix names; Pandarial
- [S-03] Fandom: Skill Overview, Skill Ascend, Seasonal Systems, Classes Overview, Class Selection, Everything about Class Change, class skill pages
- [S-04] sxswiki skills and build pages (leads)
- [S-10] zeroluck.gg summoning page: banners, rates, skill counts
- [S-11] BlueStacks guides: 200-pull pick, Premium banner, loadout slots
- [S-12] Roonby Archmage builds; [S-14] Pro Game Guides; [S-15] EOG.GG gacha and pity; [S-16] Treyex Dominator builds
- [S-80] zeroluck.gg second reading; [S-85] eog.gg section (skill database, Skill Test, keywords); [S-87] official site posts; [S-42] player blog (Arena Shop)
- R-001, R-020, R-037, R-080, R-093, R-097, R-104, R-106, R-115, R-116, R-136, R-158, R-169
