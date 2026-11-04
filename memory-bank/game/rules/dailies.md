# Dailies rules

Read when running or extending the daily loop (`python -m sxs daily`): sign-in, events, Journal, Material Realms, milestones.

## Thrilling Events (home, top right)

### R-096 · Thrilling Events: only Sign-in and Growth Trial
- Thrilling Events (0.91, 0.125) opens "Featured": Dawnstar Prelude, Growth Trial (R-098), Daily Sign-in (R-097), Link Account.
- **Never Dawnstar Prelude (gacha draws) or Link Account** (R-043).
*observed* · node `featured` · R-097, R-098, R-043

### R-097 · Daily Sign-in: claim today's tile, never Catch Up
- 30-tile calendar. Today's tile shows a green "Claim"; tap for "YOU RECEIVED" (e.g. 10 Stellatie, R-093).
- **Missed days show "Catch Up": spending, never press.**
- Days 5/20: gold card item x50; 10/25: red item; 15/30: purple crystal.
- Daily step `sign_in`. Dailies reset 8:00 server time (UTC-5, R-024); `sxs/loops/daily.py` keeps done marks in `logs/daily.json` by server date.
*observed* · `daily_signin.png`, `daily_signin_received.png` · node `daily_signin` · R-024, R-043

### R-098 · Growth Trial: claim free trial quests, never Advanced Trial
- 19-day event; Day 1-7 tabs of trial quests (Reach Lv. 20, Arrive at Drasilgard, Total Resource Level 30, Enhance Gear x4 to +15) pay points toward a 100-700 chest track. Daily step `growth_trial` claims finished ones.
- **"Advanced Trial" (top right) is paid: never.**
*observed* · `growth_trial.png` · node `growth_trial` · R-043

## Journal (home bottom bar)

### R-094 · The Journal routes to the tower, gathering and realms
- Journal: 2nd bottom-bar icon (0.31, 0.97). Cards: Fantasia Ascent (top right, (0.78, 0.23), R-079), Map Exploration (R-108), Material Realms (R-095), Weekly Events (Void Rift), two Unavailable.
*observed* · `journal.png` · node `travel_journal`, `fantasia_ascent` · R-079, R-095, R-108

### R-095 · Material Realms: mine with free hammers; never buy hammers
- First realm Ironvein Pit (Raw and Refined Ore); three more locked. Inside: hammer button (0.5, 0.72), "Iron Mined" counter, tabs Ironvein Pit / Rankings / Goals (Iron Mined 5-25 goals pay fruit items).
- Each Iron Hammer mines once (about +115 Raw Ore); count shows top right and on the button. Free hammers come from Prayer Goals (R-093) and other Goals tabs (R-116).
- **At 0 hammers the button opens "Purchase Iron Hammer" (60 Dawnium each, limit 20/day): never buy, Cancel (0.32, 0.65).** Tap it only while the counter reads 1+.
- Daily step `material_realms` (also claims the Goals tab).
*observed* · `material_realms.png`, `ironvein_pit.png`, `purchase_iron_hammer.png` · node `material_realms`, `ironvein_pit` · R-043, R-093, R-092

### R-015 · Material dungeons: two free attempts each
- 2 free attempts a day per material dungeon. **Extra attempts cost Dawnium: never.**
*reported* · node `dungeons` · R-018, R-043

## Events and milestones

### R-051 · Event sign-ins are on the Notice board
- Menu, Notice (tabs Notice / System / News) lists events. An event's daily sign-in (e.g. "Haunted Carnival" Carnival Sign-In, to 14 Nov) is a daily task while it runs.
- Read names and dates each time; don't hard-code. Notice tab badges mean unread posts, not claims (R-063).
*observed* · `notice.png` · node `notice` · R-063

### R-052 · Exploration Goals: milestone rewards
- World tab, bottom-left button. Progress tab: per-region milestones (e.g. Verdantglade 0/5, 0/10, ...). Explore tab: Destiny Exploration Goals (to 0/100). The world overview shows each island's score and player rank.
- Probably worth claiming in the daily loop ❓.
*observed* · `exploration_goals.png`, `destiny_exploration_goals.png` · node `exploration_goals` · R-002, R-076, R-116
