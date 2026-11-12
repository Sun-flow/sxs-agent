# 2026-11-10 06:33 · Item symbols are catalogued and taught to the detector (mae)

- Every item, material and currency symbol gets a catalogue entry in `resource/items/` with its name and description read from its own in-game popup; the UI detector learns them (`item_icon`, one class per item in the export by default).
- Standing rule for every thread: when you see a material or currency symbol that is not in the catalogue, find out what it is and add it (`python -m sxs items add`). Not all of them matter to the bot; all of them help training.
