# Guild rules

Read before any guild screen. Code: `sxs/loops/guild.py` (`python -m sxs guild [--only donate,afk,conquest]`), daily steps `guild_donate`, `guild_afk`, `guild_conquest`.

## Joining

### R-102 · Join a random open guild; never create one
- Unlocks with level (R-011): bottom bar 4th icon (0.68, 0.97), Akane dialogue, then "Join Guild Go>>" (0.71, 0.38) / "Create Guild <<Go" (0.29, 0.77).
- Join list: search (name or ID), Refresh; rows offer instant "Join" or "Apply" (approval); a red "50K+ Power" label is a power requirement.
- mae: join a random instant-"Join" guild. **Never Create Guild** (may cost Dawnium). Choosing or leaving guilds otherwise is mae's call (R-057). Current guild: karsa_1515 (ID 700460600036).
*observed, told* · `guild_tutorial_intro.png`, `guild_no_guild.png`, `guild_join_list.png` · node `guild_no_guild`, `guild_join_list` · R-011, R-043, R-057

## Guild island

### R-113 · Find buildings by label; find the Gate from the Lobby label
- State `guild` (bottom label "Guild"); pans sideways and remembers the last pan.
- West: Guild Lobby, Gate of Expedition. East: Power Station, Forge, Warehouse, Shop. Also Mine, Donation.
- The Gate label hides behind the bottom-right AFK widget: in the west view the Lobby label is at (0.44, 0.49) and the Gate about (+0.38, +0.15) from it (274, 196 px).
- Lobby: Donation (0.29, 0.82), Guildmates, More; tabs Guild, Territory (resources, facility levels, AFK counts), Upgrade (leader only). **No Guildmates actions, Upgrade or Construction.**
*observed* · `guild_island.png`, `guild_lobby.png`, `guild_territory.png`, `guild_upgrade.png` · node `guild`, `guild_lobby` · R-103, R-110, R-111

## Daily guild steps

### R-103 · Donate twice a day, never more
- **Max 2 donations a day** (mae). Lobby, Donation (0.29, 0.82): "Daily Donations: N/5" is the source of truth, so reruns never make a third.
- 1st free; 2nd 20 Dawnium behind a confirm: **the one approved Dawnium use** (exception to R-043). 3rd costs 50: stop; never pay above 20.
- Each pays 300 Guild Tokens and 500 of each guild resource.
- Guild Farm: plant and harvest once a day ❓ (reported, not seen).
*told, observed* · `guild_donation.png`, `guild_donation_confirm.png` · node `guild` · R-043, R-113

### R-110 · AFK gathering: keep the character at the Forge
- Forge (7800/h), Power Station and Mine (5400/h), 10 slots each; the Forge's list continues on a second screen.
- Empty "+" slot: AFK Details (+600/h to the guild, capped at 36 h; personally 120 Guild Tokens/h plus a random item), then Start.
- One slot per character; switching asks "Currently AFK: ... Switch anyway?" and collects the old slot. mae: **Forge**; already there = done.
- Bottom-right widget: sleeping figure = idle; character with timer = gathering.
*observed, told* · `guild_forge.png`, `guild_power_station.png`, `guild_afk_switch_confirm.png` · node `guild_facility` · R-113

### R-111 · Conquest: claim floors, use both attempts in the background
- Gate of Expedition: Guild Events, Conquest (guild boss) and Guild Clash (unlocks 2026-11-12).
- Shared boss per floor; "Daily Challenge Attempts: N/2" (OCR gives "Dailly Challenge Attempts:O/2": match "Challenge Attempts", read O as 0).
- Beaten floor: claim its chest (0.49, 0.57), then step right (0.95, 0.37) to the live floor.
- Challenge (0.50, 0.77), Start Battle (0.50, 0.75), 50-round fight: minimise it (R-112). Result: damage and participation rewards (10 Dawnium, 150 Guild Tokens), Tap to Continue. A "Done Conquest Fn" chip then shows at left, y≈0.75, on home and island.
- Goals tab: claim Serverwide (per server floor) and Personal (total challenges 10/20/...). Rankings tab is a known state (the detector once misread Challenge as a map object and wandered in).
*observed* · `guild_events.png`, `guild_conquest.png`, `guild_conquest_battle.png`, `guild_conquest_result.png`, `guild_conquest_rankings.png` · node `guild_events`, `guild_conquest`, `guild_conquest_result` · R-112, R-113

## Guild shop and Warehouse

### R-114 · Guild Shop: buy nothing until mae's buy list exists
- Warehouse: locked, leader or deputies build it.
- Shop (east, NEW badge): Guild Tokens, weekly refresh, Shop Lv 1/1 (guild-side). Most items locked until Shop Lv 2-6; buyable now: Stellatie (500, limit 3), Lucky Ticket (1.5K, limit 1). Table: `docs/shop-tables.md`.
- **Buy nothing until mae fills Buy? and a buy list exists** (R-120). Read items via info cards (R-125).
*observed, told* · `guild_warehouse_locked.png`, `guild_shop_top.png`, `guild_shop_bottom.png` · node `guild` · R-120, R-125, R-043
