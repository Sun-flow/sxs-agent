# 2026-11-11 23:02 · World collectible classes and pre-roll buffer (Claude Code, cloud)

- mae approved two tiers (world_collectible + kind), the four class names, the pre-roll buffer; bellflower goes in a "misc" family; ore is a Resource Hunt target; the "stamina 5" board is a monster fight (essence) any monster gives once a zone is blessed.
- Built on PR #67: classes appended (ids 44-47 before #69's map_portal; whichever merges second renumbers), `resource/world/collectibles.json`, `collectible`/`cost` box fields, labeler menus and filter, `dataset --collectibles family|each|one`, `sxs/core/preroll.py` hooked into Device.screenshot, collectibles.save and gather pickups.
- Open: a stamina-drop pre-roll needs a stamina read in Clear Zone (that thread); first live run sizes the sequences.
