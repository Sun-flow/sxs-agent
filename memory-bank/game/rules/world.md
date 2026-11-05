# World rules

Read for background facts: regions, servers, level unlocks, seasons, server time, and towns (what each NPC does).

## Regions and servers

### R-006 · Regions and servers
- Regions: Originisle (start), Verdantglade, Cinder Ridge, Aqualis, Loong Haven.
- Servers hold up to 5,000 players and later merge; guilds are per server. The account is on Forgehall.
*observed, reported* · node `world_map`

## Unlocks

### R-011 · Some features unlock by level; seasons partly reset levels
- Reported: Guild Lv 15, Vendor Booth Lv 18, Fantomons Lv 51.
- The Guild tab says "unlocks at Character Lv. 15" but unlocked at Lv 20 ❓: the bottom bar's 4th icon (crest, (0.68, 0.97)) lit with a tutorial highlight (R-102).
- Travel Journal: "Unlock any mode to unlock Travel Journal".
- Seasons (first about a month, later 2-3 months) partly reset levels: re-check unlocks each season.
*observed, reported* · `home/home_guild_tutorial.png` · node `guild`, `vendor` · R-010, R-102

## Time and resets

### R-024 · Server time is UTC-5; dailies reset 8:00, achievements Mondays 8:00
The server clock (UTC-5) is on the menu screen. Dailies reset at 8:00 (Daily Sign-in, R-097); achievement quests Mondays 8:00.
*observed* · `home/main_menu.png`, `dailies/daily_signin.png` · node `main_menu` · R-097, R-099

## Towns

### R-134 · Drasilgard: what each NPC and object does
- **Village Chief** (big house, north): story only; points to Auroradrasil (R-133).
- **Hermes**, "Smiling Merchant" (mushroom-roof shop, east): Kingdom Shop for Abundance Leaves; buy nothing until mae fills Buy? (`docs/shop-tables.md`, R-114).
- **Carol the Black Cat** (wizard hat, by the dome house, west), Verdantglade's shapeshifting witch: the first meeting gives a free Shapeshifting Mirror. Menu Transform! / Chat / "Let me think about it". Transform opens Reshape (General, Hair, Face, Trait); **Complete costs 1 Mirror and changes the look: mae's choice, never press it** (policy).
- A card titled **"Limpid Legion"** opened from a tap somewhere in town; unknown, dismissed ❓ (ask mae).
- **Portal** east of the stone ring: already activated; its card shows Teleport. The notice board stall and the "G" dome house are decoration; the stone ring gives no card.
- The Bellflower-like plants in town (south of centre, near the dome house) are decoration: walking onto one removed it, but the rank count stayed at 4/30. Bellflowers come only from the Flower Harvest field (R-123).
- Zoomed-out area map from here: Wildbloom Coast 20.4K, Hidden Camp, Verdantglade V 14.8K (78%), Monolith Ruins I, Zephyr Vale, Troll Lair 17K, Verdantglade IV, Jungle Camp 12.6K; all others 0%. Yellow-star markers north-east on the minimap are unmapped ❓.
*observed* · `world/drasilgard_hermes_menu.png`, `unlabeled/drasilgard_carol_dialogue.png`, `unlabeled/drasilgard_carol_gift.png`, `unlabeled/drasilgard_carol_menu.png`, `unlabeled/drasilgard_carol_reshape.png`, `unlabeled/drasilgard_portal_teleport.png`, `unlabeled/area_map_verdantglade_zoomed_out.png` · nodes `drasilgard`, `hermes_menu`, `kingdom_shop`, `carol_menu`, `reshape` · R-114, R-118, R-123, R-127, R-133
