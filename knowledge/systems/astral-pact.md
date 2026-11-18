# Astral Pact and Primostars

<!-- index: Read to plan the end of a season: how the season rating becomes Primostars, what the targets are and where points come from -->

> **Summary:** At the end of each season the game rates five seasonal levels (gear, character, skills, Fantomons,
> relics), converts the rating into Primostars, and each Primostar is one level on the Astral Pact track of
> permanent bonuses. Gear enhancement carries by far the most points. Targets: Season 1 at least 104 (F2P; 128 if
> possible), Season 2 680 then 800 (F2P). It is the most important permanent progression because each season
> can be scored only once.
> **Applies:** all seasons (scored at each season's end)
> **Related:** [Seasons](seasons.md), [Gear](gear.md), [Relics](relics.md), [Fantomons](fantomons.md),
> [Skills](skills.md), [Levels and unlocks](levels-and-unlocks.md), [Gems](gems.md)

## Terms

| Term | Meaning | Source |
|---|---|---|
| Astral Destiny | The system (and a tab beside Astral Pact) that ties seasonal progress to permanent bonuses | [S-03][S-01] |
| Season Rating Score ("Progression Rating") | Points for the current season, from five seasonal levels | [S-03][S-01] |
| Primostar (also "Primordial Star") | Currency paid at season end from the rating; 1 Primostar = 1 Astral Pact level | [S-01][S-51] |
| Astral Pact | The track of permanent bonuses; fill it with Primostars ("Hold to Fill") | [S-01] |

The season screen has tabs Overview, Gameplay, Progression and Gear; the Progression tab shows the five levels,
the rating letter, the Primostars it will convert to, and "Claimable in" with the time left [S-01].

## The five rating categories

"Season levels" count only the seasonal part: character levels above 100, relic levels above +10, and so on
[S-51][S-03].

| Category | What is counted | Points per level | Season 1 maximum | Example from a top Season 1 account, 4 days before the end | Source |
|---|---|---|---|---|---|
| Season Gear Level | Enhancement level of the five pieces (average) | 38 | 7,220 (level 190) | 133 = 5,054 pts | [S-51][S-01] |
| Season Relic Level | Relic levels above +10, summed (20 relics x 3 levels) | 57 (derived) | 3,420 (all relics +13) | 53 = 3,021 pts | [S-51][S-01] |
| Season Skill Level | Skill levels above 100, summed | 13 (derived) | 2,496 (skill level 124) | 176 = 2,288 pts | [S-51][S-01] |
| Season Character Level | Levels above 100 | about 100 (derived) | 2,400 (Lv 124) | 22 = 2,232 pts | [S-51][S-01] |
| Season Fantomon Level | Fantomon levels above 100, summed | 14 (derived) | 1,680 (level 130) | 69 = 966 pts | [S-51][S-01] |
| **Total** | | | **17,216** | **13,561** | |

- "Derived" weights are our division of the example's points by its levels; they match the calculator's caps
  (57 x 60 = 3,420; 13 x 192 = 2,496; 14 x 120 = 1,680) [S-51][S-01].
- Gear is about 42% of the maximum and is the category that moves fastest per resource: "the more you level your
  gear, the more disproportionately high your Primostar score will increase" [S-01].
- Share of the maximum: gear 42%, relics 20%, skills 14.5%, character 14%, Fantomons 10% [S-51].
- eog's star calculator states the same Season 1 weights outright, per slot: gear 38 per level per piece (5
  pieces), character 100 per level, skill 13 per slot (8 slots), relic 57 per slot (20), Fantomon 14 per slot (4),
  all counted above the floor (Lv 100, relic +10) [S-85]. So the "derived" weights are confirmed by a second
  tier C reading, and the gear level is the **sum over the five pieces**, not an average or the lowest piece
  (7,220 = 38 x 5 pieces x 38 levels) [S-85].
- Relic scale: resonance up to +10 is permanent; in Season 1 it can be pushed to +13, and only +11 to +13 is
  scored here and resets with the season ([Relics](relics.md) calls +10 the soft cap for the same reason)
  [S-51][S-85].

### Later seasons

| Season | Points per Primostar | Flat grant | Level floor | Relic floor | Gear per level per piece | Character per level | Skill per slot | Relic per slot | Fantomon per slot | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 100 | 10 | 100 | +10 | 38 | 100 | 13 | 57 | 14 | [S-85][S-51] |
| 2 | 27 | 45 | 130 | +13 | 18 | 100 | 7 | 33 | 8 | [S-85] |
| 3 | 13 | 65 | 160 | +16 | 14 | 100 | 5 | 26 | 6 | [S-85] |

- Season 2 and 3 rows are community-maintained calculator values, not published by the developer ❓ [S-85]. Full
  table, formula and calculator defaults: [astral-pact-scoring.json](../data/astral-pact-scoring.json).

## From rating to Primostars

- Season 1 conversion: Primostars = 10 + rating / 100, rounded down. The example's 13,561 points show "145"
  [S-01]; the calculator states the same rule as "score needed = (target stars - 10 - already owned) x 100" [S-51].
- So each Primostar costs 100 points: 2.6 gear levels, or 1.75 relic levels, or 7.7 skill levels, or one
  character level, or 7 Fantomon levels.
- The conversion happens once, when the season ends; season levels then reset [S-01].

| Season 1 target | Rating needed | Who | Reward named at that level | Source |
|---|---|---|---|---|
| 104 | 9,400 | F2P minimum goal | | [S-01][S-02] |
| 128 | 11,800 | F2P stretch | | [S-02] |
| 152 | 14,200 | Light / mid spender | | [S-02] |
| 176 | 16,600 | Light / mid spender | Dungeon evaluation double reward +2% | [S-02][S-51] |
| 200 | 19,000 | Stretch goal | EXP gain +2% | [S-02][S-51] |

- 200 Primostars needs more points than the 17,216 we can account for, so some source of points is missing from
  the table above (a rating-letter bonus, off-class gear, or higher caps) ❓. eog's milestone ladder even runs to
  320 stars, with the same weights and no extra source named [S-85].
- Season 1 milestone ladder [S-85]: 10, 20, 30, 40, 56, 72, 88, 104, 128, 152, 176, 200, 230, 260, 290, 320 stars,
  cycling four bonuses in order: Ascension drop rate +3%, Gem acquisition +5%, Dungeon evaluation double reward
  +2%, EXP gain +2%. This agrees with the rewards named at 176 and 200 above; rows in
  [astral-pact-scoring.json](../data/astral-pact-scoring.json).
- "Don't stress too much if you cannot hit this number": 104 is a reference point, more is better [S-01].

| Season 2 target | Who | Reward at that level | Source |
|---|---|---|---|
| 680 | F2P | Exp Gain +2% | [S-02] |
| 800 | F2P | Gem Drop +5% | [S-02] |
| 920 | Light / mid spender | Exp Gain +2% | [S-02] |
| 990 | Light / mid spender | Ascension +3% (dungeon gear drop ascension rate) | [S-02] |
| 1060 | Light / mid spender | Gem Drop +5% | [S-02] |

- "Nothing changes about how the Astral Pact works in Season 2" [S-02]. The Season 2 numbers are several times
  the Season 1 ones. eog's calculator explains it as both: Primostars carried from earlier seasons count toward
  the total, and a Season 2 Primostar costs only 27 points (flat grant 45) against 100 in Season 1 [S-85] ❓
  (community values; [S-02] itself does not say). Season 2 levels also go much higher (gear to +180, level 130+).

## The Astral Pact track

First levels of the track, from a screenshot [S-01]:

| Level | Bonus |
|---|---|
| 5 | ATK +1% |
| 10 | [Dungeon] Gear Drop Ascension Rate +3% |
| 15 | DEF +1% |
| 20 | Gem Drop Rate +5% |
| 25 | HP +1% |

The pattern seems to repeat every 25 levels with rarer nodes mixed in (Exp Gain +2%, dungeon double reward +2%)
❓ [S-51][S-02]. The rarer nodes are the 16 milestones listed under "From rating to Primostars" [S-85]; the
screenshot's level 10 and 20 nodes match that ladder. Bonuses add up across all seasons and are always active [S-01].

## Rating letters

- The Progression tab shows a letter; the example account had SSS at 13,561 points [S-01]. Thresholds for the
  letters are not published ❓.
- The Gear tab is rated separately. In Season 1, two Divine plus three Mythic pieces from Hellhold give SSS; two
  Hellhold Divine, two Aquorigin Divine and one Hellhold Mythic also reach SSS on aggregate score. If you need
  gear for the rating, buy Aquorigin Divine shards or pieces, which are cheap late in the season; still run the
  latest dungeon when you can [S-02].
- What the letter itself pays (beyond the Primostars) is not stated ❓.

## Why it matters most

- It is permanent, it accumulates over every season, and it can be scored only once per season: relics can still
  be pulled in a later season, a missed Primostar cannot be earned again [S-01].
- It does not replace the normal plan: follow the usual progression all season and only tilt toward Primostars at
  the end [S-01].

## How to raise the score (cheapest first)

1. Enhance all five gear pieces evenly as far as ore allows (band rule R-092); from mid-season spend stamina and
   Material Realm purchases on ore [S-01].
2. Push relic resonance above +10 on all five elements; all 20 relics count [S-01][S-51].
3. Keep levelling the character: rank up at each cap, light statues, consider holding speed-ups for the last
   days [S-53].
4. Quick Upgrade skills with Battle Essence; level all four deployed Fantomons [S-51].
5. The +drop dungeon strategy gears you faster and so lifts the gear category earlier ([Gear](gear.md)) [S-01].
6. In the final week compare the cost of the next Primostar in each category and buy the cheapest.

## Open questions

- ❓ Rating letter thresholds and rewards. Read the Progression tab's info button late in a season.
- ❓ Where the points beyond 17,216 come from (needed for 176-200 Primostars).
- ❓ The stat nodes (ATK, DEF, HP) of the Astral Pact track beyond level 25; the 16 milestone bonuses are known [S-85].
- ❓ Season 2 and 3 conversion values seen in our own game (27 and 13 points per Primostar are community values [S-85]).
- ❓ Whether a mid-season joiner's low score is scaled in any way (it is not, as far as sources say).

## Sources

- [S-01] section 6 (Astral Pact and Primostars, two screenshots), section 3
- [S-02] section I (targets, SSS conditions), section VI (Season 2 targets)
- [S-03] Seasonal Systems (Season Reset and Astral Destiny)
- [S-85] eog.gg star calculator: per-slot weights for Seasons 1 to 3, flat grants, 16 Season 1 milestones ([astral-pact-scoring.json](../data/astral-pact-scoring.json))
- [S-51] calculator: gear weight, caps, conversion, Season 1 milestones; [S-53] speed-up alternative
