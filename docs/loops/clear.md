# Clear Zone loop (one zone to 100%, one named objective at a time)

Code: `sxs/loops/clear.py` (`run`), helpers in `sxs/actions/mapnav.py`. Command: `python -m sxs clear [--area NAME]
[--minutes N]`. Called by [roam.md](roam.md). Design and why: [step6-clear-zone.md](../step6-clear-zone.md).
Replaces the Fog Walk (scrapped 2026-11-10, [fogwalk-postmortem.md](../fogwalk-postmortem.md)). Rules: R-065, R-068,
R-131, R-132, R-140, R-142, R-143, R-147, R-148, R-150, R-155.

**Goal:** bring one unexplored zone to 100% by clearing its objects: the quest ring's targets, dots, monsters,
structures, statues. Every leg names its objective; progress is the zone's % or an object cleared, never tiles.
**End condition:** 100% (or the tracker moved on), no objective left, 4 legs in a row without progress, a power
gate met 3 times, a lost fight, an unfamiliar screen, or the time.
**Ok statuses:** `zone_done`, `no_objective`, `no_progress`, `puzzle` (3 gold squares in a row that open nothing and move no %: floor-puzzle tiles, R-153; the zone is marked blocked), `power_gate`, `blocked_item`, `explored`, `timeout`.
Needs a look: `defeated`, `unknown_screen`, `repeating_card`, `left_area:home`, `not_on_map`, `not_in_zone`.

## The leg loop

```mermaid
flowchart TD
    S(["Start"]) --> M{"On the island map?"}
    M -->|no| TW["home, World, the island"]
    TW -->|failed| NOM(["not_on_map"])
    TW -->|ok| A
    M -->|yes| A{"--area given?"}
    A -->|yes| GO[["goto the zone by area map"]] --> EX
    A -->|no| EX{"Zone explored already?<br/>(location tree)"}
    EX -->|yes| XP(["explored"])
    EX -->|no| L
    L["Between legs: read the % (tracker Explore N/100 if it is this zone's)"] --> D{"100%, or tracker moved<br/>on to the next zone?"}
    D -->|yes| ZD(["zone_done"])
    D -->|no| Z{"Still in our zone?<br/>(minimap name, R-140)"}
    Z -->|"no, twice"| BK[["goto back into the zone"]] --> L
    Z -->|yes| ST{"4 legs in a row<br/>without progress?"}
    ST -->|yes| NP(["no_progress"])
    ST -->|no| P1{"1. Quest ring for this zone?"}
    P1 -->|yes| LEG["Leg: tap the target under the ring"]
    P1 -->|no| P2{"2. Known object on screen?<br/>(R-131 crops)"}
    P2 -->|yes| LEG2["Leg: tap it (from the next tile if needed, R-155)"]
    P2 -->|no| P3{"3. Dot or structure anywhere<br/>on the minimap (up to 10 tiles)?"}
    P3 -->|yes| LEG3["Leg: walk along the minimap path until it is on screen<br/>(up to 3 walk taps), then tap it"]
    P3 -->|no| P4{"4. Anything in our zone on the big map that counts for exploration?<br/>blue ! statues and wheels, green pickups, orange monsters,<br/>gold structures and chests"}
    P4 -->|yes| LEG4[["Leg: big-map walk to it, tap the centre"]]
    P4 -->|no| P5{"5. Frontier: the nearest fog in our zone<br/>touching walkable ground we can reach?<br/>(3 per run)"}
    P5 -->|yes| LEG5[["Leg: one big-map walk to the frontier"]]
    P5 -->|no| NO(["no_objective: leftovers written to the location tree"])
    LEG --> R
    LEG2 --> R
    LEG3 --> R
    LEG4 --> R
    LEG5 --> R
    R["Handle what the leg opened (table below) until back on the map"] --> RES{"Leg result"}
    RES -->|"% up or object cleared"| G["gain: no-progress count = 0"] --> L
    RES -->|"got there, nothing"| N1["reached: count + 1"] --> L
    RES -->|"didn't get there"| N2["failed: count + 1; the spot fails twice = skipped this run"] --> L
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef look fill:#fde2c8,stroke:#c25e00,color:#000
    classDef sub fill:#dbe9ff,stroke:#1f5fbf,color:#000
    class ZD,NP,NO,XP ok
    class NOM look
    class GO,BK,LEG4,LEG5 sub
```

Each leg logs `[leg N] goal: <source> <what> at <where>` before it starts and `[leg N] result: <gain|reached|failed>
<% before -> after>` after. The runner's stall check sees the leg count and the %, not the coordinates.

## Screens a leg can open

| Screen | Action | Leg result / ends with |
|---|---|---|
| battle_prep | heal from the portrait if HP under 70% (2 tries), else Start Battle; save the monster crop (R-131) | gain (a fight) |
| battle, loading, dialogue, tap_to_continue | wait / pass through | |
| reward_popup | close | gain (a pickup) |
| defeated | OK | `defeated` |
| player_profile | close (a stray tap on our character) | |
| tower screens | tower climb if not done today (R-079), then back to the zone | |
| area_map | close (left open by a big-map walk) | |
| home | | `left_area:home` |
| Lucky Wheel, free spin showing (R-147) | spin once | gain |
| Gate of Elements (Gate of Wind...) | add companions, Open (R-057) | gain, or the spot skipped if still short |
| dialogue_choice (a puzzle NPC) | Leave; puzzle noted on the zone (R-153) | the spot skipped |
| dialogue_choice with no Leave (a story choice) | save the screen to `docs/screens/dialogs/choice_<zone>_<choices>.png`, ask mae (mae, 2026-11-11) | `needs_decision` |
| any other card | card rules (`resource/policy/cards.json`, goal explore) | acted on: gain; dismissed: the spot skipped; Gate of Power: the spot skipped, `power_gate` the 3rd time; "Required Item": `blocked_item` |
| unknown, 5 in a row | frame saved | `unknown_screen` |
