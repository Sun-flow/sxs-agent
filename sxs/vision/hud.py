"""Numbers on the island-map and home HUD: stamina (top right) and power (next to the crossed swords)."""

from __future__ import annotations

from typing import Optional

from .ocr import power_k, read_fraction, read_line

MAP_STAMINA_ROI = [540, 25, 180, 45]  # "171/300" top right on the world map
HUD_POWER_ROI = [110, 70, 170, 40]  # "16.9K" next to the crossed-swords icon on the map and home HUDs


def read_stamina(det, roi=MAP_STAMINA_ROI, frame=None) -> Optional[int]:
    """Current stamina from an "a/b" counter (default: the map HUD), or None."""
    c = read_fraction(det, roi, frame)
    return c[0] if c else None


def read_power(det, frame=None) -> Optional[float]:
    """Our power in K from the HUD, or None."""
    return power_k(read_line(det, HUD_POWER_ROI, frame))
