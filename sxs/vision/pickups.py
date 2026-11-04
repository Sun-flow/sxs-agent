"""Overworld pickups and rings: the tracking ring (yellow/white), a special node's green timer circle, and the
faint blue aura that marks a rarer pickup (mae, 2026-11-04). Pixels only, no taps, no OCR."""

from __future__ import annotations

import cv2
import numpy as np

LEFT_PANEL = (0, 700, 140, 1000)  # quest/resource tracker icons on the left: ring-shaped, never targets


def blue_aura(hsv: np.ndarray, pt, r: int = 55) -> float:
    """Share of light-blue pixels round a point: the faint aura that marks a rarer pickup (mae, 2026-11-04)."""
    x, y = pt
    patch = hsv[max(0, y - r):y + r, max(0, x - r):x + r]
    return float(((patch[..., 0] >= 85) & (patch[..., 0] <= 105) & (patch[..., 1] > 60)
                  & (patch[..., 2] > 170)).mean())


def find_rings(frame: np.ndarray, colour: str = "track") -> list[tuple[int, int, int]]:
    """Circles (x, y, r) drawn round a target: the tracking ring is bright yellow pulsing to white; a special node's
    timer circle is green. Hough on a colour mask, radius 24-36 px."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    if colour == "green":
        mask = (h >= 40) & (h <= 85) & (s > 120) & (v > 150)
    else:
        mask = (v > 195) & (((h >= 18) & (h <= 40) & (s > 60)) | (s < 35))
    mask = mask.astype(np.uint8) * 255
    mask[:130, :140] = 0  # HUD portrait
    bottom_edge = mask[1180:, 200:620].copy()  # a ring clipped at the bottom edge sits here, between the buttons
    mask[1000:] = 0  # chat strip and bottom bar
    if colour != "green":
        mask[1180:, 200:620] = bottom_edge
    cs = cv2.HoughCircles(cv2.GaussianBlur(mask, (5, 5), 1), cv2.HOUGH_GRADIENT, dp=1, minDist=40, param1=100,
                          param2=22, minRadius=24 if colour != "green" else 14, maxRadius=36)
    if cs is None:
        return []
    out = []
    for x, y, r in np.round(cs[0]).astype(int):
        if LEFT_PANEL[0] <= x <= LEFT_PANEL[2] and LEFT_PANEL[1] <= y <= LEFT_PANEL[3]:
            continue
        if colour != "green" and not _ring_outline(hsv, x, y):
            continue  # a round glow (the teleport portal), not the drawn tracking ring
        out.append((int(x), int(y), int(r)))
    return out


def _ring_outline(hsv: np.ndarray, x: int, y: int) -> bool:
    """The tracking ring is a crisp circle: at some radius 20-38 px nearly the whole circumference is white (r ~26)
    or yellow (r ~28). The portal's glow and flowers never close a circle like that."""
    a = np.linspace(0, 2 * np.pi, 72, endpoint=False)
    for r in range(20, 40, 2):
        px = np.clip((x + r * np.cos(a)).astype(int), 0, hsv.shape[1] - 1)
        py = np.clip((y + r * np.sin(a)).astype(int), 0, hsv.shape[0] - 1)
        hh, ss, vv = hsv[py, px, 0], hsv[py, px, 1], hsv[py, px, 2]
        yellow = ((hh >= 15) & (hh <= 40) & (ss > 60) & (vv > 180)).mean()
        white = ((ss < 40) & (vv > 225)).mean()
        if yellow >= 0.6 or white >= 0.8:
            return True
    return False
