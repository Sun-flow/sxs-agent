# Roam loop (non-quest exploration)

Code: `sxs/loops/roam.py` (`Roamer`). Command: `python -m sxs roam [--area NAME] [--minutes N] [--max-areas N] [--walk-minutes N]`.
Rules: R-135 (order), R-065 (exploration goal), R-070 (statues), R-127 (1.25x power), R-132 (zone borders).

**Goal:** bring every zone in reach to 100% and bless its statue, lowest recommended power first; then walk any
then exploration is concluded for now.
**End condition:** no zone left in reach, a power wall, a lost fight, an unfamiliar screen, `--max-areas` zones
done, or the time.
**Ok statuses:** `exploration_concluded`, `all_explored`, `power_wall`, `area_done`, `max_areas`, `timeout`.
Needs a look: `not_on_map`, `no_area_map`, `no_progress`, `defeated`, `unknown_screen`, `left_area:home`.

## The loop

```mermaid
flowchart TD
    S(["Start"]) --> W{"On the island map?<br/>else home, World, Verdantglade's island"}
    W -->|no| NOM(["not_on_map"])
    W -->|yes| SV["1. Look around (docs/big-map-survey.md): a discovery survey only if due<br/>(first pass of the server day, --discover, or the tree has nothing to pick):<br/>survey zoom, full 3x3 pan grid, every label, % and power line, statue ! badges,<br/>saved to the location tree, back to the walking zoom.<br/>Otherwise no map at all: the location tree's zones + statues seen in glances"]
    SV --> SV2{"Any zone read?"}
    SV2 -->|no| NAM(["no_area_map"])
    SV2 -->|yes| BL{"2. Statue with a red ! on the map?"}
    BL -->|yes| BR["Walk there the big-map way, tap the centre,<br/>card rules: Unlock (up to 3)"] --> SV
    BL -->|no| PK["3. Pick the next zone (location tree):<br/>the zone we stand in if unfinished (R-132), else<br/>lowest power first among zones under 100%,<br/>within 1.25x ours, not given up today; no power line last"]
    PK --> PK2{"A zone picked?"}
    PK2 -->|"no, but one is behind a power wall"| PW(["power_wall"])
    PK2 -->|"no zone left"| EC(["exploration_concluded"])
    PK2 -->|yes| AP["4. Approach (skipped if we already stand in it):<br/>the neighbour the tree knows got in before, then walked links,<br/>then the nearest explored label (failed today goes last);<br/>then 60% of the way toward the target's label"]
    AP --> FW[["5. Clear Zone in the target zone<br/>(the neighbour counts as inside)"]]
    FW --> FW2{"Clear Zone ended defeated, unknown_screen,<br/>needs_decision, repeating_card or at home?"}
    FW2 -->|yes| STOP(["that status"])
    FW2 -->|no| RS["6. Clear Zone's last glance if under a minute old and showing the zone,<br/>else one glance at the walking zoom (no survey)"]
    RS --> RS2{"Target zone now?"}
    RS2 -->|"no % line read, label near the bottom edge"| SV
    RS2 -->|"no % shown: 100%"| BN["Walk to the statue icon near its label,<br/>tap the centre, card rules: Unlock"] --> CNT{"Zones done = --max-areas?"}
    CNT -->|yes| MA(["max_areas"])
    CNT -->|no| SV
    RS2 -->|"same % as before"| NB{"Neighbours tried today?"}
    NB -->|"under 3"| SKIP["Skip it this run; the next run tries the next neighbour"] --> SV
    NB -->|"3"| GU["Give up on it today<br/>(retried sooner if power grows 0.5K)"] --> SV
    RS2 -->|"% went up"| SV
    RS2 -->|"label not read"| SKIP
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef look fill:#fde2c8,stroke:#c25e00,color:#000
    classDef sub fill:#dbe9ff,stroke:#1f5fbf,color:#000
    class PW,EC,MA ok
    class NOM,NAM,STOP look
    class FW sub
```

With `--area NAME` step 3 is skipped: the named zone is the target; when it shows no % the loop blesses its
statue and ends `area_done`; a pass without progress ends `no_progress`.

## State kept between runs

`logs/roam.json`: statues already opened, zones given up today (with the power at the time), and which neighbours
failed as a way into each zone today. The location tree (`resource/world/zones.json`, `sxs/policy/zones.py`,
`python -m sxs zones`): every zone with kingdom, power, %, blessed, neighbours, and which neighbour a walk got in
from (or failed from). Built in PR #43, not run live yet.

## Screens

Roam itself only sees the island map, the area map and statue cards; everything else happens inside Clear Zone
([clear.md](clear.md)) and `goto` (`sxs/actions/goto.py`).

| Screen | Action |
|---|---|
| home, menus | go_home, then World, then Verdantglade's island |
| world_overview | tap Verdantglade's island |
| world_map | survey, walk, or hand to Clear Zone |
| area_map | read labels, % and power lines, statue badges; close with the back arrow |
| statue card | card rules (`goal explore`): Goddess Statue Unlock, blessed statue dismiss |
