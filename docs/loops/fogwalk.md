# Fog Walk loop (one zone to 100%)

Code: `sxs/loops/fogwalk.py` (`walk`). Command: `python -m sxs fogwalk [--area NAME] [--farm] [--minutes N]`.
Called by [roam.md](roam.md). Rules: R-065, R-066, R-130, R-131, R-132, R-068, R-061, R-146, R-150.

**Goal:** bring one zone to 100% exploration: collect green dots, fight orange dots, open yellow structures, reveal
fog (R-065). In an unexplored zone fights and pickups are free; in an explored (blessed) zone they cost stamina and
are skipped unless `--farm` (which keeps 70 stamina, R-107).
**End condition:** no fog in view after 4 pans, 4 walk taps without a new tile (after up to 12 big-map walks), a
power gate, a lost fight, an unfamiliar screen, or the time.
**Ok statuses:** `no_fog`, `stuck`, `power_gate`, `timeout`. Needs a look: `defeated`, `unknown_screen`,
`repeating_card`, `left_area:home`, `not_on_map`.

## Before the walk

```mermaid
flowchart TD
    S(["Start"]) --> M{"On the island map?"}
    M -->|no| TW["home, World, Verdantglade's island"]
    TW -->|failed| NOM(["not_on_map"])
    M -->|yes| A
    TW -->|ok| A{"--area given and walk_there?"}
    A -->|yes| GO[["goto the zone by area map"]] --> NZ
    A -->|no| NZ{"Just walked in from another zone?"}
    NZ -->|yes| ENT["R-150: find the entrance between the two zones on the big map<br/>(crossing point, location tree's way in), centre the camera there"]
    ENT --> OUT["Walk to ground next to the fog, working outward from the entrance<br/>(never tap the fog itself, R-146)"] --> FREE
    NZ -->|no| FREE{"Zone shows a % on the area map?"}
    FREE -->|"yes: unexplored"| F1["Fights on, pickups on (free)"]
    FREE -->|"no: explored or blessed"| F2{"--farm?"}
    F2 -->|yes| F3["Fights on, pickups only above 75 stamina"]
    F2 -->|no| F4["Fights off, pickups off"]
    F1 --> LOOP(["Main loop"])
    F3 --> LOOP
    F4 --> LOOP
    classDef look fill:#fde2c8,stroke:#c25e00,color:#000
    classDef sub fill:#dbe9ff,stroke:#1f5fbf,color:#000
    class NOM look
    class GO sub
```

The new-zone entry step (R-150, mae 2026-11-10) is being built: today the walk goes straight to the main loop and
looks for fog first.

## Main loop: on the island map (`world_map`), checked in this order

```mermaid
flowchart TD
    D["Read the screen: world_map"] --> H{"1. HUD HP under 70%?"}
    H -->|"yes, under 2 tries"| QH["Quick Heal"] --> D
    H -->|no| G{"2. Tracker gift with a red !?<br/>(max 3 taps a run)"}
    G -->|yes| GT["Claim it"] --> D
    G -->|no| Z{"3. Area name on the HUD<br/>is another zone?"}
    Z -->|"yes: crossed a border anyway"| ZB["Mark the ground around here off limits (R-132),<br/>walk back to our zone by area map"] --> D
    Z -->|no| P{"4. Standing on a tile not stood on before?"}
    P -->|yes| RESET["Progress: still = 0"]
    P -->|no| STILL["still + 1"]
    STILL --> GU{"still = 2 or 3 and fights on?"}
    GU -->|"a bracketed guard in view"| ATK["Fight the guard"] --> D
    GU -->|no| BLK{"still >= 4?"}
    BLK -->|"yes, under 12 big-map walks"| BMW[["goto: nearest dot or structure on the area map"]] --> D
    BLK -->|"yes, out of big-map walks"| STK(["stuck"])
    BLK -->|no| PLAN
    RESET --> PLAN["5. Centre the camera on the character"]
    PLAN --> K{"6. A known collectible or monster<br/>on screen? (R-131 crops)"}
    K -->|yes| TAPK["Tap it"] --> D
    K -->|no| MM{"7. Minimap plan, nearest first:<br/>green dot (if pickups on), orange dot (if fights on),<br/>gold building not visited, fog lead, unexplored ground;<br/>the dotted zone border is a wall (R-132)"}
    MM -->|"a dot or building"| BMW2[["goto: nearest one on the area map"]] --> D
    MM -->|"ground tile"| TAPG["Tap a few tiles along the path<br/>(step aside if that spot opened a card before)"] --> D
    MM -->|"nothing"| BM3{"Big-map walks left (12 a run)?"}
    BM3 -->|"yes, and it arrived"| D
    BM3 -->|"no, or it didn't move us"| FE{"8. Fog edge in view?"}
    FE -->|yes| TAPF["Tap clear ground next to the fog"] --> D
    FE -->|"no, 4th time"| NF(["no_fog"])
    FE -->|no| SW["Pan one step"] --> D
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef sub fill:#dbe9ff,stroke:#1f5fbf,color:#000
    class STK,NF ok
    class BMW,BMW2 sub
```

## Other screens during the walk

| Screen | Action | Ends with |
|---|---|---|
| battle_prep, fights off | back arrow (monsters respawn in explored zones, R-065) | |
| battle_prep, fights on | heal from the portrait if the prep HP bar is under 70% (2 tries), else Start Battle; save a crop of the monster tapped (R-131) | |
| battle, loading, dialogue, reward_popup, tap_to_continue | pass through | |
| defeated | card rules: OK | `defeated` |
| player_profile | close it | |
| tower_list, tower_floors, tower_result | if today's climb already ran: leave it; else [tower.md](tower.md) climb and mark the day; then go home and walk back to the zone (R-079) | |
| area_map | close it (left open by a big-map walk) | |
| home | | `left_area:home` |
| any card (interact, dungeon_floor, confirm_dialog, quest_detail, ...) | card rules (see [explore.md](explore.md#card-rules-it-uses-resourcepolicycardsjson-goal-explore)); a dismissed card's spot is walked around; a structure's card is saved as a crop | `power_gate` on a Gate of Power without Open; `repeating_card` after the same card 4 times |
| unknown, 5 in a row | frame saved | `unknown_screen` |

After any interrupt (tutorial, reward choice) that leaves the game on home, the loop walks back to its zone before
carrying on (`resume_with`).
