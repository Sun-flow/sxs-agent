"""Repo paths, importable without MaaFramework."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESOURCE = REPO_ROOT / "resource"
POLICY = RESOURCE / "policy"
SCREENS = REPO_ROOT / "docs" / "screens"
CAPTURES = REPO_ROOT / "captures"  # gitignored runtime frames
LOGS = REPO_ROOT / "logs"  # gitignored runtime logs and marks
