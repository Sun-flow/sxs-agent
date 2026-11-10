# Item symbol survey screens

Reference screens for the item catalogue (`resource/items/`, `python -m sxs items`). Two kinds of file:

- `<place>.png`: the screen a symbol was cropped from (every sighting's `screen` in `items.json` points here).
  Boxes for every sighting are in `docs/screens/labels.json` as `item_icon` boxes with the item id.
- `<item id>_popup.png`: that item's info card, the source of its name and description (`named_by: popup`).

Private details are blacked out: the Player ID on `profile.png`, the chat strip on `home_top_bar.png`.

## How the survey was done (2026-11-10, gromb2 on mae's PC)

Tap only the symbol itself, read the card, close it with a tap outside the card. Places visited: profile, home top
bar, Material Realms (3 realms), Daily Dungeon Goals, Map Exploration, Daily/Weekly quests, Vendor Booth
(General, Vault, Goals), Cart, gear Enhance, Rank Advancement, Skill page, Guild Shop, Fantasia Ascent (floors,
goals), Growth Trial (days 1-6), Haunted Carnival Spooky Shop.

What the cards look like and where to be careful:

- Item card: name, category, "Owned" N, effect line, grey flavour text, then "Source" rows (locked sources greyed).
  Treasure chests list their contents in the card; tapping a content icon opens that item's card on top, and a tap
  outside closes only the top card (used for Random Epic Gift, T3 Livestock Selection Chest).
- Guild AFK materials add "Requires ... Implement Level / Space Required / ... EXP" rows and a Reward Preview.
- Visage cosmetics show Style Scores and Compatible Body Types instead of Owned.
- No card: Cart row icons (a yield tooltip instead),
  the Resource Hunt choice icons in Map Exploration (tapping them changes the gather choice; not tapped),
  the Growth Trial points coin.
- Never tapped: price buttons, Free claims, Refresh, `+` next to a counter (purchase), the big Material Realm use
  button (catalogued from the screen as kind `usage`), Carnival Sign-In days (their "Catch Up" tags may cost).
- The Cart's coin bubble collects AFK income when tapped; open the Cart by tapping the cart body.
- Skill page: shards, techniques and charms open cards (shard: "Charm/Technique Shard", rarity, Skill Effect;
  technique/charm: rarity, tags, Level, stats, prose, with Replace/Enhance buttons: close with a tap above the
  card at (360, 160)). The "All" box adds class-mismatch skills; switch it back off afterwards.
- Every item has a `group` (material type, e.g. ore, realm_key, companion_gift, skill_shard, technique, charm).
- The Growth Trial points coin is an event completion tracker, not a resource (mae): `growth_trial_points`.
- OCR mistakes fixed by hand against the popup: joined words ("RawOre", "Flavorsof"), a full stop added at line
  ends, missing spaces after full stops. Check new reads against the `_popup.png`.
