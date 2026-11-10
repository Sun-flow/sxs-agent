# Open questions: where the loops, the rules and mae's asks don't line up

Found while drawing the loop pages (2026-11-09, code as of PR #42). Each item says what the rules or mae say, what
the code does, and a recommendation. When one is settled, fix the code or the rule, update the loop page, and move
the item to "Settled" at the bottom (keep its number, so links stay right).

## Needs mae's call

**Q6. Guild AFK when the Forge is full.** The code falls back to the Mine, then the Power Station. R-110 only says
Forge. Is the fallback fine?

**Q7. What else belongs in the daily loop?** Not in it today: event sign-ins on the Notice board (R-051) and
Exploration Goals claims (R-052, marked ❓). The bed's free speed-up is settled (see below). *Recommend:* add the
Exploration Goals claim as a daily step; run `roam` as its own loop after the dailies rather than inside them.

**Q8. Cart tie-break** (asked 2026-11-05, still open): Stone first when Stone and Wood are level is the default.

## Code that goes against a rule (recommend fixing)

**Q12. Known screens with no way home.** `go_home` has no tap for `choose_reward`, `dungeon_floor`, `quest_detail`,
`player_profile`, `interact`, `dialogue_choice`, `furniture_upgrade`, `companions`, `map_exploration`,
`gear_resonance`, `rank_advancement`, `upgrade_goals`, `class_page`, `technique_upgrade`, `skill_page`; it guesses
(tap below, back arrow) as on an unknown screen. *Recommend:* add each to `TOWARD_HOME` in `sxs/core/nav.py` (back
arrow for the pages, tap outside for the cards, Home for the profile).

**Q13. Vendor Booth pans fast.** It swipes in 500 ms; R-126 says fast swipes often don't register on home and to use
slow 1 s drags over the ground, as the Cart sweep does.

**Q16. Explore fights hurt after two heal tries.** `_on_battle_prep` in `sxs/loops/explore.py` heals up to twice,
then taps Start Battle even when the prep bar is still under 70%. R-061 says never fight under 70%; the shared
`start_fight` (used by gather) backs out instead. *Recommend:* call `start_fight`; if it returns
False, end the run `low_hp`.

**Q18. Two quest-ring followers.** Explore's `_follow_marker` and Fog Walk's `quest_step` do the same job differently;
`quest_step` is the live-proven one (R-142). *Recommend:* one shared action in `sxs/actions/` that both call, keeping
Explore's pan/toggle retries for when no ring shows.

**Q19. Mermaid labels starting "1. " draw as "Unsupported markdown: list"** in Mermaid 11 (seen in a local render of
explore.md; other pages use the same style, e.g. runner.md and the README legend). Explore now uses "Step 1 ·".
*Recommend:* check one page on GitHub; if it shows the error, switch the others too.

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

## Settled (mae, 2026-11-09 and 11-10)

**Q17. Explore's unstick reads the zone from the minimap name.** Not a problem (mae, 2026-11-10): the name under the
minimap is the most accurate way to confirm the player's zone; R-140 is being reworded to say so. No change.

**Q1. Unlock every free Cart production row.** *Built in PR #43, not run live yet:* `CartUpgrader.unlock_rows`
presses any row's exact "Unlock" before the upgrades and backs out of any cost or spend word (R-137). See
[cart.md](cart.md).

**Q2. Spot a zone border before crossing it.** *Built in PR #43, not run live yet:* `border_mask` in
`sxs/vision/minimap.py` finds the dotted line on the minimap and the Fog Walk's plan treats it as a wall (R-132); the
location tree (`sxs/policy/zones.py`) keeps zones, neighbours and entry points; roam finishes the zone it stands in
first. See [fogwalk.md](fogwalk.md) and [roam.md](roam.md).

**Q3. Gear enhancing starts on the blue pip.** A red "!" on a gear slot means a better piece to swap in (gearswap); a
blue up-arrow pip in the same place means the piece can be enhanced. *Done:* `find_up_pips` in
`sxs/vision/badges.py`, and the Upgrade loop's gear pass now runs when a slot shows the pip
(`gear_enhanceable` in `sxs/loops/upgrade.py`; checked on `docs/screens/character/character.png`). Rule update for the
docs thread: R-080, R-088, R-092.

**Q4. Quick Heal on "badly wounded" is fine.** Two kinds of dishes: permanent dishes (stat buffs, the Dishes menu in
the portrait) are the ones to conserve; healing dishes only heal and can be cooked without limit with Rolla, which is
approved. No code change. Rule update for the docs thread: R-046, R-061.

**Q5. Gather fights a guard, then resumes.** *Done:* on battle prep, gather calls the shared
`start_fight` (`sxs/actions/common.py`: heal to 70% from the portrait, then Start Battle), waits out the fight and
carries on collecting. It ends `low_hp` if HP stays low, `defeated` on a loss, `guarded` after 3 guard fights in a
run.

**Bed free speed-up (part of Q7).** Keep it as its own task, not in the daily loop: call it on purpose once the day's
exploration is done (content wall reached), to get the most from it. Not built yet.

**Q9. Explore's "get stronger" step.** *Done:* new `get_stronger` in `sxs/loops/upgrade.py` (Cart, gear swap,
charms, Upgrade loop). Explore calls it after 3 losses in a row, and `python -m sxs strengthen` now runs it. The old
one-tap-at-a-time technique levelling is gone.

**Q10. One tower climb a day.** *Done:* when explore or fogwalk meet a tower screen they first check today's mark.
If the day's climb already ran, explore goes home and ends `tower_done_today` (ok: the quest waits for tomorrow) and
fogwalk walks back to its zone. A climb they do start marks the day done.

**Q11. Tutorial dialogue choices.** *Done:* `tutorial.follow` reads the options first; on "Ascend to" / "Change
Class" it taps Leave and ends `needs_decision`, which stops whatever loop the interrupt paused (R-054).
