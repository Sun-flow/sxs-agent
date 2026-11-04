# Home rules

Read when acting on the Home scene (Cart, Statue, Vendor Booth, house) or when home looks wrong.

## Finding things on home

### R-126 · Find home objects by template; the camera keeps its pan
- Home pans both ways and remembers its camera, so fixed taps miss. Use template search.
- Left to right: Cart and pink tree (R-020), goddess Statue for pulls (R-093), Vendor Booth wagon (R-120), gate, house with bed (R-101). The house is **right** of the Cart, not above.
- Top right: "Thrilling Events" (0.91, 0.125) (R-096) and "Starter Pack". **Starter Pack is a shop: never buy** (R-043).
*observed* · `home.png`, `home_events.png` · node `home` · R-100, R-059

### R-100 · Home stuck on sky: restart the game
After long sessions home can show only sky; swipes don't move it. "Home, but no Cart bubble and no Statue" means restart the game, not keep swiping.
*observed* · node `home` · R-126

### R-059 · Filter home labels out of tracker OCR
Scene labels (e.g. "Class to Unlock") overlap the quest tracker region; filter them out.
*observed* · R-044

## The Cart

### R-020 · Collect the Cart's AFK rewards from its bubble
- The Cart fills offline up to a cap (reported); collect at least once per cap period.
- Tap the loot bubble (`resource/image/home/cart_bubble.png`): reward popup (Rolla, Stone, Wood).
- Tapping the cart opens hourly income (Rolla, Wood, Stone, Raw Ore +100/h, Battle Essence +125/h), each with a level and upgrade arrow. "Claim All" (0.5, 0.86); close with (0.5, 0.95).
*observed* · `home_cart.png`, `cart.png`, `reward_popup.png` · node `home` · R-126

## The house

### R-035 · Use the bed's free speed-up once a day
- The bed ("Sleep to earn AFK EXP...") shows Blessing Level, Activated Lost Goddess Statues, EXP/Hr, EXP Reserve and more.
- "Today's Free Speedup" is a **daily task**: one free a day.
- Furniture slots unlock by level (Lv 7: Alchemy Pot, R-047). Blessing statues likely raise Blessing Level ❓ (R-070).
*observed* · `home_house.png`, `bed.png`, `furniture_unlock.png`, `unlocked.png` · node `home_house`, `bed` · R-101

### R-101 · Collect bed EXP daily, and when close to levelling
- Ready: blue orbs above the bed, the top one in a yellow bubble with a red "!", plus a red "!" on the bed.
- From the Cart view, one right-to-left drag shows the bed (the `bed` step pans right, then up). Template `resource/image/home/bed_xp_bubble.png`; mae's `bed_xp_ready.png` is reference only (wrong scale).
- Tap the bed to collect. Daily step `bed` in `sxs.daily`, not an upgrade-loop step; also check it when close to a level-up. It can give many levels at once.
*told, observed* · `bed_xp_ready.png`, `home_bed_xp.png` · node `home_house`, `bed` · R-035, R-126

### R-047 · Cook healing food in the Alchemy Pot
- House furniture (Lv 7). Dish tab: Green Riceball restores 8% + 1000 HP for ingredients shown at the top; Cook shows "Cooked". Jelly Bean Pals is a second recipe.
- Green Riceball is probably R-061's cheap healing food ❓; keep it stocked for the explore loop (R-046).
*observed* · `furniture_alchemy_pot.png`, `alchemy_pot.png`, `cooked.png` · node `alchemy_pot` · R-061
