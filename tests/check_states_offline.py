"""Run the state detector over the reference screenshots in docs/screens/ and check each against its expected state.

    python tests/check_states_offline.py

No emulator needed. The expected state for each file is in EXPECTED; add an entry when you add a screenshot.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.device import REPO_ROOT  # noqa: E402
from sxs.replay import ImageDevice  # noqa: E402
from sxs.state import StateDetector  # noqa: E402

EXPECTED = {
    "achievement_quest": "quests",
    "guild_tutorial_intro": "dialogue",
    "guild_no_guild": "guild_no_guild",
    "guild_join_list": "guild_join_list",
    "guild_island": "guild",
    "guild_island_east": "guild",
    "guild_island_west": "guild",
    "guild_island_afk_on": "guild",
    "guild_lobby": "guild_panel",
    "guild_territory": "guild_panel",
    "guild_upgrade": "guild_panel",
    "guild_warehouse_locked": "guild_panel",
    "guild_forge": "guild_panel",
    "guild_forge_afk": "guild_panel",
    "guild_power_station": "guild_panel",
    "guild_power_station_afk": "guild_panel",
    "guild_events": "guild_panel",
    "guild_conquest_goals": "guild_panel",
    "guild_conquest_personal": "guild_panel",
    "guild_conquest_rankings": "guild_panel",
    "guild_conquest_result": "tap_to_continue",
    "guild_donation": "guild_donation",
    "guild_donation_paid": "guild_donation",
    "guild_conquest": "guild_conquest",
    "guild_conquest_boss": "guild_conquest",
    "guild_conquest_prep": "battle_prep",
    "guild_conquest_battle": "background_fight",
    "guild_afk_switch_confirm": "confirm_dialog",
    "guild_donation_confirm": "confirm_dialog",
    "battle": "battle",
    "battle_prep": "battle_prep",
    "cart": "cart",
    "character": "character",
    "tutorial_highlight": "unknown",
    "tutorial_highlight_dim": "unknown",
    "confirm_dialog": "confirm_dialog",
    "defeated": "defeated",
    "dialogue": "dialogue",
    "dungeon_floor": "dungeon_floor",
    "dialogue_choice": "dialogue_choice",
    "class_choice": "dialogue_choice",
    "dialogue_loadout": "dialogue",
    "home": "home",
    "logging_in": "loading",
    "splash": "unknown",
    "title": "title",
    "unlocked": "tap_to_continue",
    "blessing_level": "tap_to_continue",
    "furniture_unlock": "unknown",
    "title_loading": "loading",
    "home_cart": "home",
    "interact_portal": "interact",
    "interact_temple": "interact",
    "interact_ironvein_pit": "interact",
    "interact_obelisk": "interact",
    "loading": "loading",
    "loadout_edit": "unknown",
    "main_menu": "main_menu",
    "prayer": "prayer",
    "prayer_result": "prayer_result",
    "prayer_tickets": "prayer",
    "prayer_affection": "prayer",
    "growth_trial": "growth_trial",
    "daily_signin": "daily_signin",
    "daily_signin_received": "reward_popup",
    "journal": "journal",
    "material_realms": "material_realms",
    "ironvein_pit": "material_realms",
    "purchase_iron_hammer": "unknown",
    "notice_board": "notice",
    "player_profile": "player_profile",
    "player_profile_hp": "player_profile",
    "quest_detail": "quest_detail",
    "quest_detail_go": "quest_detail",
    "quest_list": "quests",
    "reward_popup": "reward_popup",
    "cooked": "reward_popup",
    "alchemy_pot": "unknown",
    "furniture_alchemy_pot": "unknown",
    "world_map": "world_map",
    "wounded": "confirm_dialog",
    "world_map_moonveil_entry": "world_map",
    "quest_detail_unlock": "quest_detail",
    "dungeon_gate_moonveil": "interact",
    "confirm_fantasia_home": "confirm_dialog",
    "fantasia_ascent": "tower_list",
    "fantasia_floors": "tower_floors",
    "fantasia_victory": "tower_result",
    "fantasia_defeat": "tower_result",
    "player_profile_charm_badges": "player_profile",
    "world_map_player_pointer": "world_map",
    "world_map_tile_puzzle_chests": "world_map",
    "lost_goddess_statue": "unknown",
    "gate_of_power": "unknown",
    "world_map_tracker_gift": "world_map",
    "world_map_explore": "world_map",
    "world_map_monsters": "world_map",
    "world_overview": "world_overview",
    # upgrade systems (2026-11-04)
    "skill_page": "skill_page",
    "skill_page_after_quick_upgrade": "skill_page",
    "technique_upgrade": "technique_upgrade",
    "technique_ascend": "technique_upgrade",
    "skill_goals_quality": "upgrade_goals",
    "class_page": "class_page",
    "class_hierarchy": "class_page",
    "class_info": "class_page",
    "class_upgrade": "class_page",
    "class_goals": "upgrade_goals",
    "class_badge_received": None,
    "rank_advancement": "rank_advancement",
    "rank_level_goals": "upgrade_goals",
    "rank_power_goals": "upgrade_goals",
    "item_bellflower": None,
    "gear_resonance": "gear_resonance",
    "gear_goals": "upgrade_goals",
    "map_exploration": "map_exploration",
    "confirm_enter_explore": "confirm_dialog",
    "explore_resource_tracker": "world_map",
    "explore_resource_tracker2": "world_map",
    "explore_stamina_boar": "world_map",
    "explore_ore_rocks": "world_map",
    "explore_ore_rocks_near": "world_map",
    "explore_ore_mined": "world_map",
    "area_map_resource": None,
    "rating_popup": "rating_popup",
    "home_white_sheet_tutorial": None,
    "vendor_booth_unlock": None,
}


def main() -> int:
    dev = ImageDevice()
    det = StateDetector(dev)
    failures = 0
    for png in sorted((REPO_ROOT / "docs" / "screens").glob("*.png")):
        want = EXPECTED.get(png.stem)
        dev.set_frame(png)
        got = det.detect()
        ok = want is None or got.state == want
        failures += not ok
        mark = "ok " if ok else "BAD"
        print(f"{mark} {png.stem:24} -> {got.state:16} (want {want}) {got.elapsed_ms} ms")
    print("all good" if not failures else f"{failures} wrong")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
