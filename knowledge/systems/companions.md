# Companions

<!-- index: Read before using companion gifts, picking a commission reward, or deciding which companion to level next -->

> **Summary:** Companions are story NPCs whose bond level gives permanent stats. New ones unlock from journals
> that drop from Premium Commissions. Level them in a fixed order: all to 20, class-matching ones to 50, all to
> 50, class-matching to 70, and so on to 100, using only each companion's favoured gifts [S-01].
> **Applies:** all seasons (new companions arrive with each new kingdom/season)
> **Related:** [Commissions](commissions.md), [Fantomons](fantomons.md), [Relics](relics.md),
> [Shops](shops.md), [Events](events.md), [World and kingdoms](world-and-kingdoms.md),
> data: [companions.json](../data/companions.json), rules R-133, R-159, R-169

## What companions give

- Companion affinity is a **permanent** system: it is not reset by a season [S-03]. SOF lists Companions with
  Relics, Fantomons and the Astral Pact as permanent power and calls them "VERY strong" [S-01].
- Each companion gives flat general stats on most levels and **special stats** at certain levels [S-01].
- Companions also act as helpers: Akane, Qin and Killian fill the party in the Auroradrasil story dungeon
  (R-133) and carry elemental Affinity that can open a Gate of Elements (R-159).
- Note on names: some sites call Fantomons "companions" [S-25]. **Bond Trinkets are not a companion item**:
  they are the Fantomon summon token ([Fantomons](fantomons.md), [Gacha](gacha.md)) [S-25].

## Unlocking companions

- New companions are unlocked through **journals** obtained from **Premium Commissions** [S-01]. SOF therefore
  picks Premium Commissions first among daily commission rewards (they can also give recipes to sell), and
  completes commissions aggressively even when they cost stamina [S-01]. See [Commissions](commissions.md).
- Feature unlock level: 38 ❓ [S-27]. The same page says companions come "via draws", which contradicts the
  journal route in [S-01]; this page follows [S-01].
- The first companions are met in the story (Akane, then Reina) [S-03].

## Levelling: gifts

- Bond is raised with **gifts**. Each companion has **favoured gifts: use only those on that companion** [S-01].
  The favoured gifts are shown behind the "!" on the companion's detail page ❓ [S-21, S-27].
- Do not gift a companion that is not next in the level order [S-21] ❓.
- Known gift items and sources:

| Gift | Source | Reference |
|---|---|---|
| Iris | Drasilgard Kingdom Shop (Hermes), 300 Abundance Leaves | `docs/shop-tables.md` |
| Jungle Fables (book) | Drasilgard Kingdom Shop, 300 Abundance Leaves | `docs/shop-tables.md` |
| "Rolla Management Made Easy" (book) | Item bag; the bot leaves gifts untouched | R-169 |
| Golden Leaf, Sunflower, Iris | Gift-code rewards ❓ | [S-04] |
| "Companion Gifts" | Grand Treasure Hunt Level 2 reward ❓ | [S-23] |

- Which gift each companion favours is not in any source we could read ❓.

## Level milestones

| Level | What unlocks | Source |
|---|---|---|
| 20 | First special stat: DMG Boost (offensive companions) or DMG Reduction (defensive) ❓ | [S-21], [S-27] |
| 50 | The companion's key special stat: Crit Rate or Accuracy (offensive); Block or Crit Resist (defensive) | [S-01] ("Stat Priority (Level 50 Companion)"); detail [S-21] ❓ |
| 60 | A skin; no stat ❓ | [S-21] |
| 70 | The level-20 stat again ❓ | [S-21] |
| 100 | The level-50 stat again ❓; **Healing Boost only unlocks at level 100** | [S-21] ❓; Healing Boost at 100: [S-01] |

## Level order (do not deviate)

SOF's order, stated as mandatory [S-01]; EOG and Mobi repeat it [S-21, S-27]:

1. Every companion to level 20.
2. Class-matching companions to level 50.
3. Every companion to level 50.
4. Class-matching companions to level 70.
5. Repeat the pattern until level 100.

"Class-matching" = the companion's level-50 special stat is one your class wants:

| Class / role | Stat to match | Source |
|---|---|---|
| Knight line (tank) | Block, Crit Resist | [S-01] |
| DPS (Duelist line, Sorcerer line, DPS Sage) | Crit Rate, Accuracy | [S-01] |
| Healer (Sage line) | Own preference; Healing Boost arrives only at companion level 100 | [S-01] |
| Sage (DoT/DPS build) | Accuracy, then Crit Rate ❓ | [S-21] |

For a Mage -> Sorcerer or Sage account: match **Crit Rate and Accuracy** companions first; a healer Sage
follows the plain order and takes Healing Boost companions to 100 last [S-01].

## Companion list

Season 1 companions and their descriptions come from the Fandom page [S-03]. The stat group column comes from
Mobi.gg's grouped list [S-27] (tier D; the group labels are our reading of that page, and they match SOF's
table for all five Loong Haven companions), so every stat group not confirmed by [S-02] carries a ❓.

| Companion | Who | Kingdom / origin | Stat group |
|---|---|---|---|
| Akane | Mysterious girl who guides the adventurer; NPC party member (R-133); Wind Affinity 101 as a gate helper (R-159) | Start / Verdantglade | Accuracy ❓ |
| Reina | Akane's older sister, second person met | Start | Crit Rate ❓ |
| Molly | Travelling merchant child (Vendor Booth, Molly's Deals) | Everywhere | Block ❓ (a "Starfrost" Molly variant is listed under Crit Rate ❓) |
| Narss (Chief) | Chief of Drasilgard | Verdantglade | Healing ❓ (a "Santa" Chief variant is listed under Accuracy ❓) |
| Hermes | Merchant and alchemist of Drasilgard (Kingdom Shop) | Verdantglade | Accuracy ❓ |
| Qin | Young Loongborn girl, Killian's sister; NPC party member; Wind Affinity 101 | Verdantglade ❓ | Crit Rate ❓ |
| Killian | Dryason archaeologist, Qin's brother; NPC party member; Wind Affinity 101 | Verdantglade ❓ | Healing ❓ |
| Mysterious Merchant | Cloaked merchant (appears at Home after Destiny Exploration and Chaos Invasion) | Everywhere | ❓ |
| Naira | Ruler of Fortburg | Cinder Ridge | Crit Rate ❓ |
| Micaela | Inventor at the forge | Cinder Ridge | Block ❓ |
| Karlos | Hot-blooded trainee | Cinder Ridge | Crit Rate ❓ |
| Braulio | Burly merchant, big brother | Cinder Ridge | Block ❓ |
| Mateo | Small, bookish | Cinder Ridge | Accuracy ❓ |
| Wuji | | Loong Haven (Season 2) | **Crit Rate and DMG Boost** [S-02] |
| Ming | | Loong Haven (Season 2) | **Crit Rate and DMG Boost** [S-02] |
| Hui | | Loong Haven (Season 2) | **Block and Block Efficiency** [S-02] |
| Jiangwang | | Loong Haven (Season 2) | **Accuracy and DMG Boost** [S-02] |
| Suimo | | Loong Haven (Season 2) | **Healing Boost, Crit Res and DMG Res** [S-02] |

Further names that appear only in [S-27] ❓ (probably Aqualis and later or event companions; none has a
description in our sources):

| Stat group ❓ | Names |
|---|---|
| Block | Gerald, Juubee, Vigard |
| Accuracy | Mio, Ophelia, Sylvia |
| Crit Rate | Elichi, Freya, Mayoi |
| Healing | Astrid, Isla, Suzu |
| KonoSuba collaboration (stat group not stated) | Aqua, Darkness, Kazuma, Megumin |

Reading the groups: Block group = level-50 Block (tank companions), Crit Rate group and Accuracy group = the
two DPS groups, Healing group = Healing Boost at level 100 [S-27, S-21] ❓.

## Season 2 companions

"With a new season comes new companions" [S-02]. Loong Haven adds Wuji, Ming (Crit Rate and DMG Boost), Hui
(Block and Block Efficiency), Jiangwang (Accuracy and DMG Boost) and Suimo (Healing Boost, Crit Res, DMG Res)
[S-02]. They restart at level 1, so step 1 of the level order (everyone to 20) applies again at the start of
each season.

## How companions connect to other systems

- [Commissions](commissions.md): Premium Commissions -> journals -> new companions [S-01].
- [Shops](shops.md): Kingdom Shops sell gifts for kingdom currency (`docs/shop-tables.md`); kingdom tools
  (potion, drill, key) have priority over gifts for the same currency [S-01].
- [World and kingdoms](world-and-kingdoms.md): companions lend elemental Affinity to open Gates of Elements
  before relics can (R-159).
- [Events](events.md): Grand Treasure Hunt Level 2 pays companion gifts ❓ [S-23].

## Open questions
- ❓ Favoured gifts per companion (read the "!" on each companion page in game).
- ❓ Exact stat and value at each level for each companion; whether level 70/100 repeat the 20/50 stats.
- ❓ Unlock level of the Companions feature (38 per tier D) and how many journals a companion needs.
- ❓ Which kingdom each later companion belongs to, and the full list after Loong Haven.
- ❓ Whether collaboration companions (KonoSuba) are still obtainable.

## Sources
- [S-01] "Companions" page; Exploration section (Premium Commissions, journals)
- [S-02] "Companions" page (Loong Haven companions and stats)
- [S-03] Fandom "Companions" and the character pages (Akane, Reina, Narss, Hermes, Molly); "Seasonal Systems"
- [S-04] sword-x-staff.wiki vouchers page (gift code contents; leads only)
- [S-21] EOG.GG companion upgrade guide; [S-23] EOG.GG Grand Treasure Hunt
- [S-25] zeroluck.gg currencies (Bond Trinket definition)
- [S-27] Mobi.gg companions guide (grouped name list)
- Rules R-133, R-159, R-169; `docs/shop-tables.md`
