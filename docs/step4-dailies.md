# Step 4: dailies

```bash
python -m sxs.daily                     # every step not yet done today
python -m sxs.daily --only a,b          # some steps
python -m sxs.daily --force             # ignore today's done marks
python -m sxs.guild [--only donate,afk,conquest]
```

`sxs/daily.py` runs the steps below in order. Each starts and ends at home. Once-a-day steps are marked in `logs/daily.json` under the server day (`device.server_day()`, R-024). Each step has a 12-minute budget; a failing step saves its frame to `captures/unknown/`, goes home and the loop moves on; two failed recoveries end it with `needs_help` (exit 1).

| Step | Once | Module / route | Rule |
|---|---|---|---|
| `sign_in` | yes | Thrilling Events → Daily Sign-in: today's tile, never Catch Up | R-096, R-097 |
| `mall_gifts` | yes | `sxs/mall.py`: free gift box on each Mall page, never a price | R-121 |
| `vendor_stamina` | yes | `sxs/vendor.py`: Vault's free x30 Stamina only | R-120 |
| `cart` | | `Strengthener.claim_cart` | R-126 |
| `bed` | yes | Tap the bed's EXP bubble | R-101 |
| `growth_trial` | | Claim finished trial quests per day tab; never Advanced Trial | R-098 |
| `fantasia_ascent` | yes | `tower.open_from_home` + `tower.climb`; heal to 70% (`sxs/heal.py`) | R-079, R-094 |
| `material_realms` | | Journal → Material Realms → Ironvein Pit: use owned Iron Hammers (free from Prayer Goals), claim Goals. Tap the hammer only while its counter is ≥ 1 (at 0 it opens a Dawnium purchase) | R-095 |
| `guild_donate` | yes | `sxs/guild.py`: at most 2 a day by the game's counter | R-103 |
| `guild_afk` | | Keep the character on a guild gather slot, Forge first | R-110 |
| `guild_conquest` | yes | Claim floors, 2 attempts sent to the background, claim goals | R-111, R-112 |
| `quests` | | Claim finished guidance quests (ore) | R-099 |
| `gather` | | `sxs.gather` (step 5) | R-107 |
| `strengthen` | | Better gear and charms from the profile, then `sxs.upgrade` (step 5) | R-080, R-088 |

`quests` and `strengthen` run a second time only if the first `quests` pass claimed something (enhancing finishes quests; quests pay ore).

## Hard constraints

- Claims go through `sxs/claims.py`: press only buttons whose whole text is Claim / Claim All / Collect / Collect All / Receive, never one with a `claims.SPEND` word on the same row (Pray, Buy, Purchase, Refresh, Spend, Dawnium, Recharge, Top up, prices, Catch Up, Draw, Advanced). R-043.
- No Dawnium except the 2nd guild donation (20, mae-approved, R-103). No class choices, no social, no Rcmd Loadouts, no Fantasia retries.
- Skill pulls are never part of this loop: `python -m sxs.pray --pulls N --handler-approved` (N a multiple of 10; `--check` reads tickets only) runs only when the handler asks (R-093).
- Shops: nothing bought until mae fills the Buy? column in `docs/shop-tables.md`; the Guild Shop is untouched (R-114).

Not automated: the bed's free speed-up (R-035).
