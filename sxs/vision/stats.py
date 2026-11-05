"""Read account stats off the screen for the progress tracker: top-bar currencies, the player profile (power, level,
class, rank, gear, techniques, charms), the Journal (Fantasia Ascent floor), the Cart panel, the guild lobby and
the Guild Shop token count. Readers only: nothing here taps.

Every reader takes `det` (a StateDetector) and a frame, and returns a dict whose missing readings are None, so a
bad read shows up in the report as "not read" instead of as a fake change. Small labels on badges are read
enlarged (`ocr.zoomed_lines`); at their real size OCR misses most of them.

Reference screens these regions were measured on (720x1280): docs/screens/home/home.png, home/journal.png,
home/cart.png, character/player_profile*.png, guild/guild_lobby.png, guild/guild_shop_top.png.
"""

from __future__ import annotations

import re
from typing import Optional

import cv2
import numpy as np

from .ocr import amount_in, power_k, zoomed_lines

# --- top bar: currency pills ------------------------------------------------------------------------------------

BAR_X0, BAR_Y_TOP, BAR_Y_BOTTOM = 280, (41, 44), (63, 66)  # rows just inside the pills' top and bottom edges
BAR_TEXT = (38, 32)  # y and height of the text inside a pill


def topbar_pills(frame) -> list[list[int]]:
    """The dark currency pills in the top bar, left to right, as [x, y, w, h] text boxes (icon excluded: it sticks
    out of the pill, so the pill edge rows are dark only beside it). Found by column darkness along the pill's top
    and bottom edges, so it works whatever the amounts' widths."""
    g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    band = np.vstack([g[BAR_Y_TOP[0]:BAR_Y_TOP[1], BAR_X0:], g[BAR_Y_BOTTOM[0]:BAR_Y_BOTTOM[1], BAR_X0:]])
    dark = list((band < 70).mean(axis=0) > 0.8) + [False]
    runs, start = [], None
    for i, v in enumerate(dark):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= 12:
                runs.append([BAR_X0 + start, BAR_TEXT[0], i - start, BAR_TEXT[1]])
            start = None
    return runs


def _pill_text(det, frame, box) -> str:
    lines = zoomed_lines(det, frame, box)
    # The Journal's pills end in a "+" button: drop it and any stray icon fragments.
    return " ".join(lines).replace("+", " ").strip()


def read_topbar(det, frame) -> dict:
    """Rolla, Dawnium and stamina from the top bar of home, the main menu or the Journal (pills in that order,
    stamina last as "a/b"). On screens without stamina (Character) the last two pills are Rolla and Dawnium.
    Amounts above 1,000 show rounded ("43.2K"); they're stored as shown, in units (43200)."""
    out = {"rolla": None, "dawnium": None, "stamina": None, "stamina_cap": None}
    texts = [_pill_text(det, frame, b) for b in topbar_pills(frame)]
    if texts and re.search(r"\d+\s*/\s*\d+", texts[-1]):
        m = re.search(r"(\d+)\s*/\s*(\d+)", texts.pop())
        out["stamina"], out["stamina_cap"] = int(m.group(1)), int(m.group(2))
    if len(texts) >= 2:
        out["rolla"], out["dawnium"] = amount_in(texts[-2]), amount_in(texts[-1])
    return out


# --- HUD (top left, on every main screen) -------------------------------------------------------------------------

HUD_LEVEL_BOX = [22, 86, 72, 26]  # "Lv. 23" under the portrait
HUD_POWER_BOX = [140, 74, 130, 32]  # "17.4K" right of the crossed swords


def level_in(text: str) -> Optional[int]:
    m = re.search(r"(?:L[vV]|LV|Level)\s*\.?\s*(\d+)", (text or "").replace(",", ""))
    return int(m.group(1)) if m else None


def _power(text: str) -> Optional[float]:
    """Power in K: "17.4K" -> 17.4; under 1,000 there's no K ("819" -> 0.819)."""
    k = power_k(text)
    if k is not None:
        return k
    m = re.search(r"(\d{2,3})\s*$", (text or "").strip())
    return int(m.group(1)) / 1000 if m else None


def read_hud(det, frame) -> dict:
    """Level and power (in K) from the HUD under and beside the portrait."""
    return {"level": level_in(" ".join(zoomed_lines(det, frame, HUD_LEVEL_BOX))),
            "power_k": _power(" ".join(zoomed_lines(det, frame, HUD_POWER_BOX)))}


# --- player profile (tap the portrait; docs/screens/character/player_profile*.png) --------------------------------

PROFILE_POWER_BOX = [62, 208, 240, 52]
PROFILE_CLASS_BOX = [62, 280, 300, 30]  # "Mage" / "No Class"
PROFILE_CLASS_LEVEL_BOX = [62, 306, 300, 34]  # "Class Level 2"
PROFILE_RANK_BOX = [226, 462, 160, 32]  # "Apprentice I" under the rank badge
PROFILE_LEVEL_BOX = [560, 360, 110, 36]  # "Level 13"
GEAR_BADGES = [[85, 755, 70, 32], [210, 755, 70, 32], [335, 755, 70, 32], [460, 755, 70, 32]]  # "+15" per slot
GEAR_SLOTS = ["weapon", "head", "chest", "boots"]  # profile Equip row, left to right (staff, hat, shirt, boots)
SKILL_X = [97, 171, 245, 319]  # Technique row centres
CHARM_X = [406, 480, 554, 628]  # Charm row centres
SLOT_BADGE_Y, SLOT_ICON_Y = (898, 28), (868, 27)  # "Lv. 10" badge; the icon above it
EMPTY_SLOT_SATURATION = 30  # an empty slot is a grey "+" disc (mean S < 25); an equipped one is coloured (> 35)


def _rank(text: str) -> Optional[str]:
    """ "Apprenticel" -> "Apprentice I", "ApprenticeII" -> "Apprentice II"; "No Rank" stays."""
    t = (text or "").strip()
    if not t:
        return None
    if re.fullmatch(r"No\s*Rank", t, re.I):
        return "No Rank"
    m = re.fullmatch(r"([A-Za-z]+?)\s*([Il1|]{1,3}|IV|V|Il?V)?", t)
    if not m:
        return t
    numeral = (m.group(2) or "").replace("l", "I").replace("1", "I").replace("|", "I")
    return f"{m.group(1)} {numeral}".strip()


def _slot_empty(frame, x: int) -> bool:
    y, h = SLOT_ICON_Y
    hsv = cv2.cvtColor(frame[y:y + h, x - 22:x + 22], cv2.COLOR_BGR2HSV)
    return float(hsv[..., 1].mean()) < EMPTY_SLOT_SATURATION


def _slot_levels(det, frame, xs) -> list[Optional[int]]:
    """Lv. of each equipped technique / charm; None for an empty slot or a badge that didn't read."""
    out = []
    y, h = SLOT_BADGE_Y
    for x in xs:
        out.append(None if _slot_empty(frame, x) else level_in(" ".join(zoomed_lines(det, frame, [x - 32, y, 66, h]))))
    return out


def _gear_levels(det, frame) -> dict:
    out = {}
    for name, box in zip(GEAR_SLOTS, GEAR_BADGES):
        m = re.search(r"\+\s*(\d+)", " ".join(zoomed_lines(det, frame, box)))
        out[name] = int(m.group(1)) if m else None  # None: empty slot or not read
    return out


def read_profile(det, frame) -> dict:
    """Everything the player profile shows that the tracker keeps."""
    cls = " ".join(zoomed_lines(det, frame, PROFILE_CLASS_BOX)).strip() or None
    cl = re.search(r"Class\s*Level\s*([\dO]+)", " ".join(zoomed_lines(det, frame, PROFILE_CLASS_LEVEL_BOX)))
    return {
        "power_k": _power(" ".join(zoomed_lines(det, frame, PROFILE_POWER_BOX))),
        "class": cls,
        "class_level": int(cl.group(1).replace("O", "0")) if cl else None,
        "rank": _rank(" ".join(zoomed_lines(det, frame, PROFILE_RANK_BOX))),
        "level": level_in(" ".join(zoomed_lines(det, frame, PROFILE_LEVEL_BOX))),
        "gear": _gear_levels(det, frame),
        "techniques": _slot_levels(det, frame, SKILL_X),
        "charms": _slot_levels(det, frame, CHARM_X),
    }


# --- Journal (bottom nav; docs/screens/home/journal.png) --------------------------------------------------------

JOURNAL_TOWER_BOX = [430, 186, 280, 40]  # "Moonveil Woods  6" on the Fantasia Ascent card


def read_journal(det, frame) -> dict:
    """The Fantasia Ascent card: tower name and the floor number it shows. On 2026-11-04 the card read 6 with
    F1-5 cleared, so the number is taken as the next floor to climb (❓ confirm against the floors screen)."""
    t = " ".join(zoomed_lines(det, frame, JOURNAL_TOWER_BOX)).strip()
    m = re.fullmatch(r"(.*?[A-Za-z])\s*(\d+)", t)
    if not m:
        return {"tower": t or None, "tower_floor": None}
    return {"tower": m.group(1).strip(), "tower_floor": int(m.group(2))}


# --- Cart panel (docs/screens/home/cart.png) -------------------------------------------------------------------

CART_ROWS_Y = [444, 520, 595, 670, 746, 821]  # top of each row's text
CART_ROWS = ["rolla", "wood", "stone", "raw_ore", "battle_essence", "gear"]  # ❓ order as on 2026-11-04 (Lv 1)


def read_cart(det, frame) -> dict:
    """Each Cart row's level and hourly rate: {"rolla": {"level": 1, "per_hour": 1000}, "raw_ore": "locked", ...}.
    A row with an Unlock button or "Unlocks at Lv. N" is "locked"."""
    out = {}
    for name, y in zip(CART_ROWS, CART_ROWS_Y):
        lv = level_in(" ".join(zoomed_lines(det, frame, [38, y + 21, 66, 30])))
        text = " ".join(zoomed_lines(det, frame, [170, y - 4, 500, 40]))
        rate = re.search(r"\+\s*([\d.,]+\s*[KM]?)\s*/\s*h", text)
        if rate:
            out[name] = {"level": lv, "per_hour": amount_in(rate.group(1))}
        elif re.search(r"Unlock", text):
            out[name] = "locked"
        else:
            out[name] = None
    return out


# --- guild (docs/screens/guild/guild_lobby.png, guild_shop_top.png) ---------------------------------------------

GUILD_LEVEL_BOX = [220, 745, 50, 32]  # the number after "Level"
GUILD_MEMBERS_BOX = [380, 745, 100, 32]  # "28/30"
GUILD_ACTIVENESS_BOX = [600, 745, 100, 32]  # "2.82K"
GUILD_TOKENS_BOX = [630, 35, 90, 40]  # Guild Shop, top right


def read_guild_lobby(det, frame) -> dict:
    lv = re.search(r"\d+", " ".join(zoomed_lines(det, frame, GUILD_LEVEL_BOX)))
    mem = re.search(r"(\d+)\s*/\s*(\d+)", " ".join(zoomed_lines(det, frame, GUILD_MEMBERS_BOX)))
    return {"guild_level": int(lv.group(0)) if lv else None,
            "guild_members": int(mem.group(1)) if mem else None,
            "guild_activeness": amount_in(" ".join(zoomed_lines(det, frame, GUILD_ACTIVENESS_BOX)))}


def read_guild_tokens(det, frame) -> Optional[float]:
    return amount_in(" ".join(zoomed_lines(det, frame, GUILD_TOKENS_BOX)))


# --- banding ----------------------------------------------------------------------------------------------------

def band(levels, step: int = 5) -> Optional[dict]:
    """mae's bands (R-092 gear, R-104 skills): everything is raised a band of `step` levels together, so progress
    is the band the lowest piece has reached, plus how many pieces already sit in the next one.
    [13, 13, 15, 13] -> {"band": 10, "next": 15, "in_next": 1, "of": 4}. Empty slots (None) are left out."""
    lv = [v for v in (levels.values() if isinstance(levels, dict) else levels) if isinstance(v, int)]
    if not lv:
        return None
    b = min(lv) // step * step
    return {"band": b, "next": b + step, "in_next": sum(v >= b + step for v in lv), "of": len(lv)}
