# Kingdom Rank (Rank Advancement)

<!-- index: Read when the character level stops at a cap, before spending Material Realm attempts, or when a Sealed Stone Gate asks for a rank -->

> **Summary:** Rank Advancement is the gate on character level: at each cap you must advance your rank (level plus
> materials plus Rolla) before EXP counts again. Rank also opens Sealed Stone Gates and scales Material Realm
> rewards. Advance the moment the cap is reached; from Season 2 each kingdom has three ranks, and the top rank of
> Loong Haven is Champion III at Lv 120.
> **Applies:** all seasons
> **Related:** [Levels and unlocks](levels-and-unlocks.md), [Material Realms](material-realms.md),
> [Exploration](exploration.md), [World and kingdoms](world-and-kingdoms.md), [Seasons](seasons.md); rules R-118,
> R-123, R-145

## How it works

- Character screen, rank badge (it reads "Apprentice I" at the start), Rank Advancement [R-118].
- An advance needs: the character at the current level cap, a few kingdom materials, and Rolla. No Dawnium [R-118].
- Until you advance, the level stays at the cap; bed EXP keeps banking and is applied at once on rank-up (our
  account went Lv 30 to 37 in one step) [R-118].
- The badge shows a red "!" when everything is ready and a blue pip while a material is short [R-118].
- The game and the guides use both names: "Rank Advancement" (the screen), "Rank" (Material Realm tip) and
  "Kingdom rank" (guides) [R-118][S-03][S-01].

## What rank gates

| Gated thing | Detail | Source |
|---|---|---|
| Character level cap | Each rank lifts the cap (20, 30, 40 ...) | [R-118] |
| Sealed Stone Gates between zones | Verdantglade V to VI needs Apprentice II; XI to XII needs Apprentice III | [R-145] |
| Material Realm rewards | Rewards scale with rank; save attempts for higher ranks unless the materials are needed now | [S-03][S-87][S-01][S-02] |
| Stamina | Reaching Champion I "raises Stamina and Material Realm rewards"; eog's calculator scales pickup yield per 5 stamina by rank | [S-53][S-85] |
| Grand Arena | Needs Lv 40 and a completed Rank Advancement | [S-87][S-03] |
| Gear enhancement cap | Rises with character level, so indirectly with rank | [S-87] |
| Gear affix roll ranges | The published affix table is labelled "Champion III, Season 2"; ranges "may vary earlier or later" | [S-02] |

## Rank table

| Kingdom | Rank | Needs level | Materials | Rolla | New level cap | Source |
|---|---|---|---|---|---|---|
| Originisle / Verdantglade | Apprentice I | start | - | - | 20 | [R-118] |
| Verdantglade | Apprentice II | 20 | 5 grey stones (name ❓), 20 Bellflowers | 5.5K | 30 | [R-118] |
| Verdantglade | Apprentice III | 30 | 5 green leaves (name ❓), 30 Bellflowers | 10.5K | 40 | [R-118] |
| Verdantglade / Cinder Ridge | next rank (name ❓) | 40 | ❓ | ❓ | ❓ | not read yet [R-118] |
| Cinder Ridge | ❓ | ❓ | ❓ | ❓ | ❓ | |
| Aqualis | ❓ (the last Season 1 rank lifts the cap past 100; Season 1 ended near Lv 124) | ❓ | ❓ | ❓ | ❓ | cap from [S-51] |
| Loong Haven | Champion I | ❓ (between 100 and 120) | ❓ | ❓ | ❓ | [S-53] |
| Loong Haven | Champion II | ❓ | ❓ | ❓ | ❓ | implied by I and III |
| Loong Haven | Champion III (top rank of Season 2) | 120 | ❓ | ❓ | ❓ | [S-02] |

- "Starting from Season 2, every Kingdom only has three ranks" [S-01]. This implies Season 1 kingdoms had more
  than three steps between them, or uneven ones; the names between Apprentice and Champion are not in any source ❓.
- eog's calculator uses six rank bands of three sub-ranks each: Black Iron, Bronze, Silver, Gold, Sanctuary,
  Legend [S-85]. These are eog's translations; the game shows Apprentice and Champion, and the mapping between
  the two sets is not stated ❓. Eighteen steps over six bands also fits "three ranks per kingdom".
- In Season 2 the second dungeon needs Lv 130 [S-53][S-02], so the level cap after Champion III is at least 130.

## Materials

- **Bellflowers** (Verdantglade): free picks in the Verdantglade Flower Harvest field in Moonveil Woods, +2 per
  plant; the rank cost card links straight to it [R-123]. A map tool marks 34 Bellflower spots in Verdantglade
  (its sidebar says 6) [S-50].
- The other two material icons (grey stones, green leaves) were already owned when needed [R-118]; their names and
  sources are not recorded ❓.
- Later kingdoms' rank flowers or equivalents: ❓. A Season 2 checklist says to "gather what's needed to reach
  Champion I" before the season starts, so at least part of it can be collected in advance [S-53].

## The Material Realm saving trick

- Material Realm rewards scale with Kingdom Rank [S-03][S-87][S-01]. eog puts numbers on it: a multiplier from
  1.6 at the lowest sub-rank to 45 at the highest, with the biggest jumps between bands (tier C, unchecked ❓);
  table in [Material Realms](material-realms.md#rewards-scale-with-kingdom-rank) [S-85].
- Save unused Material Realm attempts and tools and spend them after reaching the top rank of the current
  kingdom; meanwhile run only 10 Rolla attempts a day to finish the daily quests ("0/10/0/0") [S-01].
- Season 2: keep all consumable realm tools locked in the bag until Champion III (Lv 120); "almost every veteran
  player" recommends waiting, and pre-season is low pressure [S-02].
- Limit: do not hoard if that makes you miss a dungeon power threshold [S-01].
- See [Material Realms](material-realms.md) for the tools and the 4444 / 4244 split.

## Priority

Rank advancement comes before all other strengthening when the level is at its cap; gather free materials a few
levels early [R-118].

## Open questions

- ❓ All rank names and requirements between Apprentice III and Champion I. Read each Rank Advancement screen as
  it appears and add rows to [kingdoms.json](../data/kingdoms.json).
- ❓ Whether eog's rank multipliers (1.6 to 45) hold in game, and which game rank each of its bands is.
- ❓ Whether rank resets with the season (level above 100 resets, so Champion ranks probably start fresh each
  season).
- ❓ The level needed for Champion I and II.

## Sources

- [S-01] section 7 (Material Realms: saving uses; three ranks per kingdom)
- [S-02] section IV (Champion III at Lv 120) and the affix infographic header
- [S-85] eog.gg stamina calculator (rank bands, multipliers); [S-87] official posts (Arena, realm rewards, enhancement cap)
- [S-03] Material Realm, Arena; [S-50] Bellflower markers; [S-51] Season 1 end level; [S-53] Champion I
- Rules R-118, R-123, R-145
