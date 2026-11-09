# Screens and who acts on them

Every screen the state detector knows (`resource/pipeline/state.json`, in detection order), what any loop does there,
and what `go_home` does there. Use it to answer "we're on screen X: what can happen next?". The per-loop pages have
the detail.

Legend: **Interrupt** = handled the same way inside every loop ([runner.md](runner.md)). **Pass** = every walking
loop passes through it (`actions/common.pass_through`). **Cards** = the card rules in `resource/policy/cards.json`.
**No way home** = `go_home` has no tap for it and falls back to guessing (tap below the popup, back arrow).

| Screen | Loops that act on it, and how | go_home |
|---|---|---|
| agreement | Nobody. go_home stops: a human accepts it once | stops |
| loading | Pass: wait | wait |
| title | Nobody but go_home | Tap to play |
| chat | Interrupt: close the panel (R-027) | close |
| choose_reward | Interrupt: class-matched pick, else stop `needs_decision` (R-129) | no way home |
| area_map | roam, fogwalk, goto: read labels, tap targets; fogwalk closes a leftover one | back |
| rating_popup | Interrupt: Later (R-060) | Later |
| reward_popup, tap_to_continue | Pass: close; gather, tutorial, mall, vendor close it too | close |
| defeated | explore, fogwalk: Cards (OK, home), run ends `defeated` | OK |
| confirm_dialog | explore, fogwalk: Cards; gather: OK only on "explore" travel; guild: OK only for a donation of 20 or less / an AFK switch; vendor, pray, material_realms: Cancel | Cancel |
| dungeon_floor | explore, fogwalk: Cards (Next Floor) | no way home |
| tower_list, tower_floors, tower_result | tower; explore and fogwalk hand over to tower | back |
| quest_detail | explore, fogwalk: Cards (Go / Track) | no way home |
| player_profile | explore: heal under 80%, fill charms once, close; fogwalk: close; gather: close, 3rd time `stuck_self`; daily strengthen: fill charms | no way home |
| guild_donation, guild_conquest, guild_panel | guild | above the popup / back |
| interact | explore, fogwalk: Cards (map object, statue, mini-dungeon, gate) | no way home |
| dialogue_choice | explore: `--choose`, else stop on Ascend/Change Class, else lowest option; tutorial: Leave and stop on Ascend/Change Class, else the detected option (Q11) | no way home |
| dialogue | Pass: next (explore logs the text) | next |
| guild_join_list, guild_no_guild | Nobody (joining was done once by hand) | back / Home |
| battle_prep | explore: heal under 70% then Start; fogwalk: back out when fights are off, else heal then Start; tower: heal then Start; guild conquest: Start; gather: heal then Start, then resume gathering (back out after 3 guard fights) | back |
| background_fight | tower: wait (Auto Challenge); guild conquest: minimise | minimise |
| battle | Pass: wait | wait |
| furniture_upgrade | cart | no way home |
| cart | cart, strengthen: Claim All, row arrows | tap outside |
| home | Start of every menu loop; explore: tap the tracker; fogwalk: run ends `left_area:home`; interrupt: tutorial highlight | (goal) |
| world_overview | roam, fogwalk: tap Verdantglade's island | Home |
| world_map | explore, fogwalk, roam, gather, goto; interrupt: tutorial highlight | back |
| character | upgrade, gearswap, strengthen | Home |
| main_menu | daily quests, mall | back |
| enhance_gear | upgrade gear pass, strengthen | back |
| mall | mall | back |
| companions | Interrupt: tutorial (Invite, R-057) | no way home |
| map_exploration | gather | no way home |
| gear_resonance | upgrade gear pass | no way home |
| rank_advancement | upgrade rank pass; gather's Bellflower route | no way home |
| upgrade_goals | Nobody by name (upgrade claims Goals tabs from the page it's on) | no way home |
| class_page | upgrade class pass | no way home |
| technique_upgrade | upgrade skills pass | no way home |
| skill_page | upgrade skills pass | no way home |
| featured, daily_signin, growth_trial | daily | back |
| journal | daily, tower, gather | Home |
| material_realms | daily | back |
| notice | Nobody (event sign-ins, R-051, not automated) | back |
| prayer, prayer_result | pray only | back |
| quests | daily | back |
| guild | guild | Home |
| unknown | Every loop counts them and stops after a few (`unknown_screen`), saving the frame to `captures/unknown/` | guess, 40 tries |
