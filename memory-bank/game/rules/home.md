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
- Settings (builder, 2026-11-11): Alchemy Pot tabs Dish / Combine / Dismantle / Goals. On Dismantle keep "Exclude High-Power Gear" ticked, tick Common, Rare and Epic (Legendary off), up to 99 per press, then Dismantle: a "Dismantled" banner lists the Raw Ore (red ore from Epic). First pass: 211 pieces gave about 2.9K Raw Ore and 110 red ore; 7 high-power pieces (green double chevrons) stayed for gear swaps (R-088).
- Alchemy Goals has Dismantle and Dish sub-tabs: Claim each lit row (R-116). Combine ("Select items for combination") is unused.
*told, observed* · `home/alchemy_dismantle.png`, `home/alchemy_dismantle_selected.png`, `home/alchemy_dismantled.png`, `home/alchemy_dismantle_left_highpower.png`, `home/alchemy_goals.png`, `home/alchemy_dish_goals.png`, `home/alchemy_combine.png` · node `alchemy_pot` · R-023, R-047, R-088, R-092, R-116

### R-166 · Locked furniture: tap the crate, not the "Open" marker; Unlock is free
- An "Open" marker over a crate in the house (upper floor) or on home (the stone left of the Cart) marks a locked furniture slot. Tapping "Open" only walks the character there; tap the crate or stone itself to get the furniture card, whose Unlock carries a red "!" and no cost: press it, then "UNLOCKED <name> / Tap to Continue" (builder, 2026-11-11).
- **Workbench** (house, upper floor; "study your collection of Relics") opens the Relic screen: element tabs (Light, ...), Affinity and Aegis counters, Resonance Level 1 (4 display slots, +20% elemental stats of displayed relics), tabs Relic / Goals. With no relics it shows "No eligible Relics" and "Go to Aeonic Gacha": never tap that link (R-167).
- **Aeonic Gacha** (stone left of the Cart): R-167.
*observed* · `home/home_house_open_slot.png`, `home/furniture_workbench.png`, `home/workbench_relics.png`, `home/home_stone_open.png`, `home/furniture_aeonic_gacha.png` · nodes `workbench`, `aeonic_gacha` · R-047, R-159

### R-167 · Aeonic Gacha: unlock it free, claim its quest, never draw without mae
- A "time-frozen gacha machine" that draws Relics with Auroral Badges. The free Unlock (R-166) adds the tracker quest "Aeonic Gacha: Unlock Aeonic Gacha" (50 badges): tap the tracker to claim it (R-044).
- Screen: tabs Kingdom / Element / Goals; banner "Sylvan Relics" (Verdantglade); Draw x1 = 10 badges, Draw x10 = 100 badges; "Gacha Draws Today n/10000"; a guaranteed Rare in 10. We hold 230 badges (2026-11-11).
- **Draws are pulls: never draw** until mae says so (asked 2026-11-11); same footing as Prayer pulls (R-093).
*observed* · `home/aeonic_gacha.png` · node `aeonic_gacha` · R-043, R-093, R-159, R-166

### R-168 · Mailbox (the owl): Claim All daily, never Delete Read
- The owl on the house's left balcony is the Mailbox: tabs Mail / Gifts. "Claim All" (0.69, 0.81) is free: press it once a day. Never press "Delete Read" (R-043 spirit: no deleting) (builder, 2026-11-11).
- First Claim All gave 400 Dawnium, 20K Rolla, 10 Bond Trinket, 10 Stellatie, weapons, 5 T4 Battle Essence Casket, 50 Rare Auroral Badge and 2 Visage gift boxes. Receiving Dawnium is fine; spending it is not (R-018).
*observed* · `home/mailbox.png`, `home/mailbox_received.png` · node `mail` · R-018, R-043, R-116

### R-169 · Item bag: open Treasure Chest items, leave gifts, ask on a choose-one box
- The chest on the house's ground floor (badge with a count) is the Item bag. Usable boxes carry a "!" (blue or red). Tapping one opens a "Treasure Chest" card with Cancel / Use; a stack shows a quantity slider that defaults to max (builder, 2026-11-11).
- Open every Treasure Chest item with Use at the max quantity: T1/T2/T4 Battle Essence Caskets (400/530/840 each), T2 Raw Ore Casket (420), Yummy Bites Weapon and Outfit Visage gift boxes (cosmetics; opening only adds them, choosing a look stays mae's, R-134).
- Gift items (e.g. "Rolla Management Made Easy") are companion affinity gifts: leave them.
- A selection box ("choose one") is a choice: stop and ask mae (R-129).
*observed* · `home/bag_items.png`, `home/bag_casket_card.png`, `home/bag_casket_multi.png`, `home/bag_visage_giftbox.png` · node `item_bag` · R-129, R-134

### R-170 · Tap the little things around Home for small resources
- Tiny creatures at the Home base (mice, sometimes sitting in burrows), pink leaf piles and clay jars or pots can be tapped for a small amount of resources (mae, 2026-11-11 04:57). The Home routine includes a tap pass over them, found by template after panning.
- A tracker line "...ers X 0/100" showed next to three leaf piles: likely a collect counter for them ❓.
- Drop names and fuller reference images: to come from the strengthening thread.
*told* · `home/home_tap_mouse.png`, `home/home_tap_mice_burrows.png`, `home/home_tap_critters.png`, `home/home_tap_leaf_pile.png`, `home/home_tap_overview.png` · node `home` · R-020, R-126
