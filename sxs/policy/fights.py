"""Which fights are worth taking, by power (CP). No model calls.

mae, 2026-11-04: monsters are usually stronger than us on CP, but skills and gear win, so take on anything with up
to 25% more power than ours. This covers recommended powers (area-map labels such as "12K", tower floors). It does
not cover Gates of Power: those pillars open only when our power reaches their number (R-086).
"""

from __future__ import annotations

from typing import Optional

POWER_MARGIN = 1.25  # accept an opponent with up to this many times our power


def within_reach(needed: Optional[float], power: Optional[float]) -> bool:
    """True when a fight needing `needed` power is worth taking at our `power` (both in the same unit, e.g. K).
    No requirement means yes; an unknown power of ours means no (we can't tell)."""
    if not needed:
        return True
    if not power:
        return False
    return needed <= power * POWER_MARGIN
