# Home tap pass: implementation and test plan

Rule: R-170 (mae, 2026-11-11 04:57). Tiny creatures (mice, some in burrows), pink leaf piles and clay jars or pots around the Home base give a small amount of resources when tapped. The plan is written so a builder can pick it up at a time mae approves. It does not run on the emulator until she does.

## Where it fits

- A new daily step home_taps in `sxs/loops/daily.py`, after `cart` / `cart_upgrade` and before `bed`. Those steps already sweep the home scene (`cart._sweep_for_cart`, `daily.bed` pans), so the tap pass reuses the same sweep instead of adding another.
- Not once a day: the critters and piles probably respawn. Start with ("home_taps", False) and log how many targets each run finds. If the count is always 0 on a second run the same day, switch it to once a day.
- Budget: one full sweep (right then left, the same swipes as the Cart sweep) and at most 12 taps a run.

## Detecting the targets

1. **Templates first** (same method as `Home.Cart` and `Home.BedXP`): crop each target from a full-frame 720x1280 capture into `resource/image/home/` (home_mouse.png, home_mouse_burrow.png, home_leaf_pile.png, home_jar.png) and add Home.Mouse, Home.LeafPile, Home.Jar nodes to `resource/pipeline/state.json` with `find_all`.
   - mae's crops in `docs/screens/home/home_tap_*.png` are cut from screenshots of a different scale, so they show what to look for but are not usable as templates. Take new crops from the emulator.
   - Mice move: match on the head and ears only, with a lower threshold (about 0.7), and tap the match centre straight away.
   - Leaf piles are pink and fixed in place. A colour mask (pink hue, high saturation, inside the ground band) is a cheap backup if the template misses some.
2. **Later, the UI detector**: once the targets are labelled, add a home_critter class (mice and jars) and a home_leaf_pile class to `resource/detect/classes.json` and label them in the labeler. The template path stays the fallback.
3. **Stay out of**: the chat strip (y 0.82–0.90, it opens server chat), the Cart, the bed, the house furniture, and the HUD (R-158). Taps only go on matched targets, never blind.

## Each tap

- Tap the match centre and wait about 1.5 s.
- Read the result:
  - a floating pickup text or a reward popup: record it, close any popup with `close_rewards`;
  - a card: dismiss it and add the target to a skip list for the run;
  - another screen (profile, furniture card): back out with `nav.go_home()` and skip that target.
- Re-detect after every tap, because a tapped pile or mouse may disappear or move.

## Reference images to capture (one session)

Save full frames to `docs/screens/home/`:

- each target type before tapping: home_mouse_full.png, home_mouse_burrow_full.png, home_leaf_piles_full.png, home_jars_full.png;
- what each tap gives: home_tap_drop_mouse.png, home_tap_drop_leaf.png, home_tap_drop_jar.png;
- the tracker line "...ers X 0/100" before and after tapping leaf piles: home_tap_tracker_before.png, home_tap_tracker_after.png.

Add a row to `docs/screens/README.md` and entries to `docs/screens/expected.json` (state `home`).

## Tests

- **Offline** (a new check, check_home_taps, no device): run the new templates over the captured full frames and check the expected number of matches per frame, and no matches on `home/home.png`, `home/home_cart.png` and the house frames. Add a row to `tests/README.md`.
- **States**: `tests/check_states_offline.py` must still pass. The new frames must detect as `home`.
- **Live, at an approved time**: announce the run first (readout rule). Run python -m sxs daily --only home_taps twice. Check the log for targets found, taps made, and drops read. Record the Rolla and material counts before and after. Second run: confirm whether the targets respawned.

## What to report back for the rules (R-170)

- drop names and amounts per target type;
- whether the leaf-pile tracker counts these taps, and what its quest is called;
- the respawn interval, if it shows.
