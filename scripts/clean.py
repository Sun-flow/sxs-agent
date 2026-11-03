"""Delete working files: everything under captures/ and MaaFramework's debug log in .maa/debug/.

    python scripts/clean.py            # run at the end of a session
    python scripts/clean.py --dry-run  # list what would go

Nothing here is committed; reference screenshots live in docs/screens/ and are never touched.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [ROOT / "captures", ROOT / ".maa" / "debug"]


def size(p: Path) -> int:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) if p.exists() else 0


def main() -> int:
    dry = "--dry-run" in sys.argv
    total = 0
    for t in TARGETS:
        n = size(t)
        total += n
        print(f"{'would remove' if dry else 'removing'} {t.relative_to(ROOT)} ({n / 1e6:.1f} MB)")
        if not dry and t.exists():
            shutil.rmtree(t, ignore_errors=True)  # a log MaaFramework still holds open is skipped
    print(f"{total / 1e6:.1f} MB {'reclaimable' if dry else 'freed'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
