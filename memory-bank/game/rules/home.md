# Home rules

Read when acting on the Home scene (Cart, Statue, Vendor Booth, house) or when home looks wrong.

## Finding things on home

### R-126 · Find home objects by template; the camera keeps its pan
- Home pans both ways and remembers its camera, so fixed taps miss. Use template search.
- Left to right: Cart and pink tree (R-020), goddess Statue for pulls (R-093), Vendor Booth wagon (R-120), gate, house with bed (R-101). The house is **right** of the Cart, not above.
- Pan with slow drags (about 1 s) over the ground at y≈0.64; the scene moves about 1.25 px per px dragged. Fast swipes at mid height (y≈0.47) often don't register and never leave the left end (R-100). The default camera sits about 900 px right of the Cart.
- The Cart's body changes with its level and load: match its wheel (`resource/image/home/cart_day.png`, `resource/image/home/cart_night.png`).
- Top right: "Thrilling Events" (R-096) and "Starter Pack". **Starter Pack is a shop: never buy** (R-043).
*observed* · `home/home.png`, `home/home_events.png` · node `home` · R-100, R-059

### R-100 · Home stuck on sky: restart the game
After long sessions home can show only sky; swipes don't move it. "Home, but no Cart bubble and no Statue" means restart the game, not keep swiping. Seen again in the Cart run (04:54); the Cart script restarts the game itself. The "sky" (with floating islands) is the scene's left end, where fast swipes leave you (R-126).
*observed* · node `home` · R-126

### R-059 · Filter home labels out of tracker OCR
Scene labels (e.g. "Class to Unlock") overlap the quest tracker region; filter them out.
*observed* · R-044

## The Cart

### R-020 · Collect the Cart's AFK rewards from its bubble
- The Cart fills offline up to a cap (reported); collect at least once per cap period.
- Tap the loot bubble (`resource/image/home/cart_bubble.png`): reward popup (Rolla, Stone, Wood).
- Find the Cart by its wheel: the sprite changes when it is loaded with goods.
- Tapping the cart opens hourly income, each row with a level and upgrade arrow: Rolla, Wood, Stone, Raw Ore, Battle Essence, Gear (unlocks at Lv 15; now open at +2/h), Chrono Sand (an Unlock button with "!": press it, R-137), Treats (unlocks at Lv 45). "Claim All" (0.5, 0.86); close with (0.5, 0.95).
*observed* · `home/home_cart.png`, `home/cart.png`, `home/cart_lv3.png`, `dialogs/reward_popup.png` · node `cart` · R-126, R-136

### R-136 · Upgrade only Stone and Wood on the Cart, keeping their levels even
- Upgrade the Stone and Wood income rows only. Keep the two rows at the same level: upgrade whichever is lower, Stone first on a tie (default until mae picks an order ❓).
- Never upgrade Rolla, Raw Ore or Battle Essence (or Gear when it unlocks), even when their arrows are lit.
- The upgrade arrows show only after the Cart has been claimed, so claim first (R-020), then upgrade.
- Each row's upgrade opens "Furniture Upgrade" (`home/cart_furniture_upgrade.png`, state `furniture_upgrade`): tabs per row at y≈0.12 (Rolla, Wood, Stone, Raw Ore, Battle Essence), "Lv. N → Lv. N+1" at y≈0.34, cost icons with have/need at y≈0.77–0.80, "Upgrade ×1" at (0.5, 0.865).
- Costs are ordinary resources only, no Dawnium: the other material, the row's own material, and Rolla. Lv 3 → 4: 65 + 25 + 190; 4 → 5: 70 + 30 + 205; 5 → 6: 75 + 30 + 215. Check the cost icons before every press and stop on any Dawnium icon (policy).
- Cap: a row's level is capped by the bed's Blessing Level (R-035). At the cap the button reads "Unlocks at Blessing Lv. N" (Stone Lv 5 → 6 needs Blessing Lv 6): stop there, not an error.
- Live 04:54: Stone and Wood both Lv 3 → 5, alternating Stone first; the other rows stay Lv 3. Code: `python -m sxs cart`, daily step `cart_upgrade`.
*told, observed* · `home/cart_furniture_upgrade.png`, `home/cart_lv3.png` · nodes `cart`, `furniture_upgrade` · R-020, R-035, R-099

### R-137 · Unlock every available Cart production row
- When a Cart row shows an Unlock button (often with a red "!"), press it. Unlocking is free (mae). Chrono Sand was the first such row.
- This is separate from upgrading: unlocking a row doesn't make it an upgrade target. Upgrades stay Stone and Wood only (R-136).
- Rows still locked behind a level (Treats, Lv 45) show no Unlock button yet; check again on later runs.
- Code: `CartUpgrader.unlock_rows` in `sxs/loops/cart.py` presses an exact "Unlock" before upgrading. If a confirmation shows any cost or spend word, it backs out and asks (needs a decision). Live-verified 2026-11-09 on Chrono Sand.
*told, observed* · node `cart` · R-020, R-136

## The house

### R-035 · Use the bed's free speed-up once a day
- The bed ("Sleep to earn AFK EXP...") shows Blessing Level, EXP/Hr, EXP Reserve and more.
- "Today's Free Speedup": one free a day. It is its **own task, not a daily step** (mae, 2026-11-09). Save it until the day's exploration is complete (the content wall, not reached yet), so it adds the most; it will be called on purpose later in the day. Collecting the bed's stored EXP is separate (R-101).
- Furniture slots unlock by level (Lv 7: Alchemy Pot, R-047). Unlocking a zone's Goddess Statue raises Blessing Level by 1 (Verdantglade V: 5 → 6, which raised Max Cart Level 5 → 6 and AFK EXP 592 → 608; Verdantglade VI: 6 → 7, Max Cart Level 7, AFK EXP 620 → 636; R-070). Blessing 7 lets Stone and Wood go to Lv 7. Blessing Level caps the Cart's row levels (R-136).
*observed* · `home/home_house.png`, `home/bed.png`, `home/furniture_unlock.png`, `dialogs/unlocked.png` · node `home_house`, `bed` · R-101

### R-101 · Collect bed EXP daily, and when close to levelling
- Ready: blue orbs above the bed, the top one in a yellow bubble with a red "!", plus a red "!" on the bed.
- From the Cart view, one right-to-left drag shows the bed (the `bed` step pans right, then up). Template `resource/image/home/bed_xp_bubble.png`; mae's `home/bed_xp_ready.png` is reference only (wrong scale).
- Tap the bed to collect. Daily step `bed` in `sxs.loops.daily`, not an upgrade-loop step; also check it when close to a level-up. It can give many levels at once.
*told, observed* · `home/bed_xp_ready.png`, `home/home_bed_xp.png` · node `home_house`, `bed` · R-035, R-126

### R-047 · Cook healing food in the Alchemy Pot
- House furniture (Lv 7). Dish tab: Green Riceball restores 8% + 1000 HP for ingredients shown at the top; Cook shows "Cooked". Jelly Bean Pals is a second recipe.
- Green Riceball is probably R-061's cheap healing food ❓; keep it stocked for the explore loop (R-046).
*observed* · `home/furniture_alchemy_pot.png`, `home/alchemy_pot.png`, `home/cooked.png` · node `alchemy_pot` · R-061

### R-165 · Dismantle in the Alchemy Pot is safe: use it for ore
- The Alchemy Pot's Dismantle only takes gear with lower CP than the gear currently equipped, so anything better than what we wear is protected (mae, 2026-11-11 04:50).
- Dismantling is allowed and is a good source of ore for gear enhancement (R-023, R-092); dismantled advanced gear gives Refined Ore (R-125).
- This replaces the old "never dismantle items" never-do. Deleting items is still mae's call.
*told* · node `alchemy_pot` · R-023, R-047, R-088, R-092
