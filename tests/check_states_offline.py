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
    "world_map_tracker_gift": "world_map",
    "world_map_explore": "world_map",
    "world_map_monsters": "world_map",
    "world_overview": "world_overview",
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
