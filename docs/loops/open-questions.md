# Open questions: where the loops, the rules and mae's asks don't line up

Found while drawing the loop pages (2026-11-09, code as of PR #42). Each item says what the rules or mae say, what
the code does, and a recommendation. Nothing here is changed yet: these pages only describe. When one is settled,
fix the code or the rule, update the loop page, and delete the item here.

## Decided by mae, not built yet

**Q1. Unlock every free Cart production row** (mae, 2026-11-09). The Cart loop and R-136 ignore Unlock buttons, and
R-020 still lists Chrono Sand's Unlock as a question. *To do:* a rule update (R-020, R-136), and a Cart step that
presses a row's Unlock when its cost is free (no cost icons, no spend word), before the Stone/Wood upgrades.

**Q2. Spot a zone border before crossing it** (R-132; mae, 2026-11-09: high priority). Fog Walk only notices a
border after the walk crossed it (the HUD area name changes), then walks back and marks that ground off limits
([fogwalk.md](fogwalk.md) step 3). Nothing reads the dotted lines on the minimap or the zone labels in the world
before a tap.

## Needs mae's call

**Q3. What should start gear enhancing?** The Upgrade loop's gear pass runs only when a gear slot on the Character
screen shows "!" ([upgrade.md](upgrade.md)). By R-088 that "!" means a better piece is in the bag, which the daily
`gear_swap` step handles just before. Once the swap clears the badge, the gear pass is skipped, so gear is enhanced
only when a swap badge happens to stay. *Recommend:* always run the gear pass, like skills (enhancing stops by itself
when materials run short), unless mae knows a separate enhance signal.

**Q4. Quick Heal on the "badly wounded" card.** The card rules press Quick Heal there (explore and daily goals).
R-046 says that Quick Heal costs dishes, and R-061 says to conserve dishes. Is spending them here fine, or should the
bot take Return to Home and heal with food?

**Q5. Guarded pickups while gathering.** Gather backs out of any fight and ends `guarded`. R-073 says to fight a
monster standing between us and a pickup. *Recommend:* fight it when HP is 70%+ and it's within 1.25x our power
(R-127), else skip that pickup instead of ending the run. Note: in explored zones a fight costs stamina (R-065).

**Q6. Guild AFK when the Forge is full.** The code falls back to the Mine, then the Power Station. R-110 only says
Forge. Is the fallback fine?

**Q7. What else belongs in the daily loop?** Not in it today: event sign-ins on the Notice board (R-051),
Exploration Goals claims (R-052, marked ❓), the bed's free speed-up (R-035), and any exploring. *Recommend:* add
the Exploration Goals claim and the bed speed-up as daily steps; run `roam` as its own loop after the dailies rather
than inside them (it runs long).

**Q8. Cart tie-break** (asked 2026-11-05, still open): Stone first when Stone and Wood are level is the default.

## Code that goes against a rule (recommend fixing)

**Q9. Explore's "get stronger" step uses the old path.** After 3 losses `explore --chain` runs the Strengthen loop,
which levels techniques by tapping Upgrade up to 12 times each instead of Quick Upgrade (R-104), and skips gear swap
(R-088), Goals (R-116), class and rank. *Recommend:* run the same pieces as the daily `strengthen` step (gear swap,
charms, Upgrade loop), then retire the Strengthen loop.

**Q10. A second tower climb on the same day.** When explore or fogwalk meets a tower screen they call `tower.climb`
without checking whether today's climb already happened. After the daily climb ended in a loss, a quest's "Reach
<Tower> Fn" can start the tower again: a retry R-079 forbids. *Recommend:* the hand-over checks the day's mark and
leaves the tower if it's set.

**Q11. The tutorial follower answers dialogue choices blind.** On `dialogue_choice` it taps an option without reading
it. Explore stops on "Ascend to" / "Change Class" (R-054); the tutorial (also run as an interrupt) doesn't.
*Recommend:* the same check in `tutorial.follow`, ending `needs_decision`.

**Q12. Known screens with no way home.** `go_home` has no tap for `choose_reward`, `dungeon_floor`, `quest_detail`,
`player_profile`, `interact`, `dialogue_choice`, `furniture_upgrade`, `companions`, `map_exploration`,
`gear_resonance`, `rank_advancement`, `upgrade_goals`, `class_page`, `technique_upgrade`, `skill_page`; it guesses
(tap below, back arrow) as on an unknown screen. *Recommend:* add each to `TOWARD_HOME` in `sxs/core/nav.py` (back
arrow for the pages, tap outside for the cards, Home for the profile).

**Q13. Vendor Booth pans fast.** It swipes in 500 ms; R-126 says fast swipes often don't register on home and to use
slow 1 s drags over the ground, as the Cart sweep does.

## Gaps: screens or cards with no defined action

**Q14. Cards without a rule** are dismissed and logged: Auroradrasil's "1 More Floor(s)", "Dungeon Room Map" and
"Highest tier" (R-133), "Limpid Legion" (Drasilgard), Carol's Reshape (R-134: never press Complete; dismissing is
right, but a rule would make it explicit). The `notice` and `guild_join_list` screens have no loop.

**Q15. Roam treats "no % shown" as done.** R-135 picks "the lowest-CP zone not yet blessed". Roam picks zones under
100%; a zone at 100% whose statue wasn't blessed is only caught when its red "!" shows on the area map. If that badge
isn't detected, the zone counts as finished.

## Rule text that's out of date (for the docs thread)

- R-023 says Enhance Gear is not a detector state and `go_home` gets stuck there; it is a state now and `go_home`
  backs out of it.
- R-042 says a dungeon floor gets "Next Floor if HP is fine, else the back arrow"; R-091 (mae) and `cards.json` say
  low HP is no reason to leave: heal, then Next Floor. R-042 should match R-091.
- R-061 notes explore heals at 80% after a fight, while the rule is 70% before one; both thresholds are in the code
  (`HEAL_BELOW` in `sxs/loops/explore.py`, `FIGHT_MIN_HP` in `sxs/actions/heal.py`).
