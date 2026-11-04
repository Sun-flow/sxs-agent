"""Screen coordinates shared by more than one module, and small tap helpers. Portrait frame, 720 wide x 1280 tall.

A coordinate used by one module only stays in that module. When a second module needs it, move it here.
"""

from __future__ import annotations

import time

# --- our character ---
PLAYER_NAME = "gromb2"  # name label under the character; tells our own "!" and ring from an NPC's

# --- bottom bar and page chrome ---
NAV_CHARACTER = (80, 1240)
NAV_JOURNAL = (220, 1236)  # Fantasia Ascent, Material Realms, Map Exploration, ...
NAV_HOME = (360, 1240)
NAV_GUILD = (490, 1242)
NAV_WORLD = (640, 1240)
BACK_ARROW = (60, 1216)  # bottom-left "<" on full-screen pages
HOME_MENU_BUTTON = (664, 1006)  # box icon above the chat strip on home -> main_menu
HOME_EVENTS_BUTTON = (656, 160)  # "Thrilling Events" top right of home -> featured
BACKGROUND_FIGHT = (72, 1216)  # minimise a background fight; it carries on by itself

# --- popups, dialogs, dialogue ---
ABOVE_POPUP = (360, 60)  # closes the player profile, reward cards and most popups (a tap below often doesn't)
BELOW_POPUP = (360, 1230)  # closes item and gear cards
BOTTOM_EDGE = (360, 1250)
REWARD_CLOSE = (360, 200)  # "YOU RECEIVED" and other reward popups
DIALOGUE_NEXT = (360, 1150)  # story box: next line (also closes "tap to continue")
CONFIRM_OK = (490, 735)  # two-button confirm dialog
CONFIRM_CANCEL = (232, 735)
TAP_TO_PLAY = (360, 1056)  # title screen

# --- fights and HP ---
HUD_PORTRAIT = (70, 60)  # top-left avatar: opens the player profile (HP, Quick Heal, charms) on any screen with it
QUICK_HEAL = (510, 1064)  # player profile: Quick Heal (one cooked dish)
START_BATTLE = (360, 956)  # battle prep

# --- Character screen ---
SKILL_BUTTON = (296, 760)
CLASS_BUTTON = (424, 760)
RANK_BADGE = (590, 916)  # "Apprentice I" badge right of the level bar
TECHNIQUE_CARD_ENHANCE = (490, 946)  # technique card: Enhance

# --- island map ---
MINIMAP = (610, 170)  # tapping the minimap opens the area map
SCREEN_CENTRE = (360, 640)


def centre(box) -> tuple[int, int]:
    """Centre of an [x, y, w, h] box."""
    x, y, w, h = box
    return x + w // 2, y + h // 2


def tap(dev, xy, wait: float = 2.0) -> None:
    """Tap and give the screen time to react."""
    dev.tap(*xy)
    time.sleep(wait)


def tap_box(dev, box, wait: float = 2.0) -> None:
    tap(dev, centre(box), wait)


def near(a, b, r) -> bool:
    """Both coordinates of points a and b within r px."""
    return abs(a[0] - b[0]) < r and abs(a[1] - b[1]) < r


def inside(xy, box) -> bool:
    """Point inside an (x0, y0, x1, y1) box."""
    return box[0] <= xy[0] <= box[2] and box[1] <= xy[1] <= box[3]
