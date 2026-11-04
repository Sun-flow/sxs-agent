# Step 4: dailies and upgrades

`python -m sxs.daily` runs the daily chores and the character-upgrade passes in one loop (`sxs/daily.py`). Each step
starts from home and ends there; once-a-day steps are marked in `logs/daily.json` under the server day (UTC-5,
refresh at 8:00 server time, see `device.server_day`).

| Step | Route | Notes |
|---|---|---|
| `sign_in` | Home → Thrilling Events (0.91, 0.125) → Daily Sign-in card | Claims today's tile. "Catch Up" tiles (missed days) are skipped as possible spending. Once a day. |
| `cart` | Home scene sweep for the Cart's loot bubble | `Strengthener.claim_cart`. |
| `growth_trial` | Thrilling Events → Growth Trial | Claims finished trial quests on each day tab. "Advanced Trial" is paid: never. |
| `fantasia_ascent` | Journal tab (bottom bar, 2nd icon) → Fantasia Ascent card | `tower.open_from_home` + `tower.climb`: Auto Challenge on, no retries, heal to 70% on battle prep (`sxs/heal.py`). Once a day. |
| `quests` | Home menu → Quest | Claims finished guidance quests; their rewards are ore, which feeds gear enhancement. |
| `strengthen` | Profile (HUD portrait), Character | Better gear and charms, banded gear enhancement (all pieces to the next multiple of 5 in `GEAR_PRIORITY` order), techniques. |

After the first `strengthen`, `quests` and `strengthen` run again if the first quest pass claimed something
(enhancing finishes quests, quests pay ore).

Claims go through `sxs/claims.py`: only buttons whose whole text is Claim / Claim All / Collect / Receive, never one
with a spend word (Pray, Buy, Purchase, Refresh, Spend, Dawnium, Recharge, Top up, prices, Catch Up, Draw,
Advanced) on the same row.

Not automated yet: Material Realms (Ironvein Pit) needs Iron Hammers, and buying them costs Dawnium, so it only
makes sense with free hammers; the Bed's free speed-up; the Daily Shop's free stamina pack (a Mall screen, left
alone until mae says which buttons are safe).
