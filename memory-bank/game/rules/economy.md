# Economy rules

Read when a currency, shop or purchase screen is involved. Shop info cards: R-125 (ui.md). Guild Shop: R-114 (guild.md).

## Currencies

### R-018 · Dawnium is the premium currency: never spend it
Dawnium (orange diamond, top bar) buys extra dungeon attempts and Vault items. **Never spend Dawnium**, except the two guild donations a day (R-103). Spend buttons: R-043.
*observed, reported* · `resource/image/currency/dawnium.png` · R-015, R-043, R-103

### R-019 · Rolla is the common currency
Rolla (gold coin, top bar, "1.38K") pays for gear enhancement (R-023), Rank Advancement (R-118) and shop refreshes (**never press Refresh**, R-043). On the world map the top bar shows a fruit counter in its place. Gather it via R-108.
*observed, reported* · `resource/image/currency/rolla.png` · R-023, R-106, R-118

## Shops

### R-120 · Molly's Vendor Booth: claim only the free Vault stamina
- Green-roofed wagon on home, about (0.58, 0.63); template `Home.VendorBooth` (night-lit crop, may need a daylight copy). Unlocked free by the tutorial the Bellflower source link plays (R-123).
- Tabs: General (Rolla) | Vault (Dawnium) | Goals (Vendor Booth Pts, claim per R-116). Stock refreshes daily (timer top left). **Never press Refresh** (4K Rolla).
- **Claim the Vault's "Free" x30 Stamina once a day** (mae): tap only that Free button. No confirm. The cell still reads "Free" afterwards, so the step keeps its own done-today mark.
- Code: `python -m sxs vendor`, daily step `vendor_stamina` before `gather`; taps the first Vault cell only if OCR reads exactly "Free".
- **Every shop (mae): buy nothing until mae fills the Buy? column in `docs/shop-tables.md` and a per-shop buy list exists** (R-043). Map stock safely with `scripts/shop_survey.py` (R-125).
*observed, told* · `home/home_white_sheet_tutorial.png`, `shops/vendor_booth.png`, `shops/vendor_booth_unlock.png`, `shops/vendor_booth_general.png`, `shops/vendor_booth_vault.png`, `shops/vendor_booth_goals.png` · node `home` · R-043, R-114, R-116, R-125

### R-121 · Mall: claim the free gift boxes, never a pack
- **Every Mall pack is real money (USD): never tap a pack or price, never open Top Up.** Packs: Welcome Gift, Halloween Charmer, Little Devil, Pilgrimage Pass, Daily Deals, Weekly Deals, Pathfinder Pack.
- Route: Home menu (0.92, 0.79), Mall (0.72, 0.65): "Premium Picks" (state `mall`), tabs Event | Monthly Pass | Top Up.
- Each pack page has a free gift box top left, red "!" above-right while claimable; one tap claims it (mae allows). Daily Gift (4 h refresh), Weekly Gift (5 d), Welcome Benefit (once), plus boxes on Halloween Charmer and Little Devil. Claim each once per refresh; tap nothing else.
- Code: `python -m sxs mall`, daily step `mall_gifts`.
*told, observed* · `shops/mall_premium_picks.png`, `shops/mall_premium_picks_2.png`, `shops/mall_welcome_gift.png`, `shops/mall_welcome_benefit.png`, `shops/mall_halloween_charmer.png`, `shops/mall_daily_deals.png`, `shops/mall_weekly_deals.png` · node `mall` · R-043, R-063
