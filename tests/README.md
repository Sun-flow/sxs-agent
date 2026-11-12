# tests

Offline checks and the live smoke test. The list is built from each test's own docstring, so no branch ever edits a
shared table:

```
python3 scripts/index.py tests    # | File | Needs | Checks |
```

Run every test whose Needs doesn't say live emulator after any code change; `smoke_test.py` (live emulator) after
changing navigation.

## Adding a test

Its module docstring carries two fields (continuation lines indented two spaces):

```
"""What it checks, offline: python tests/<name>.py

Needs: OpenCV, MaaFramework (imports only)
Checks: portal icon finder on reference big maps, teleport-or-close decision, zone travel tries a portal first
"""
```

`python3 tests/check_repo.py` fails on a test without them.
