# Gather loop

Code: `sxs/loops/gather.py` (`Gatherer.run`, `Gatherer.collect`). Command: `python -m sxs gather [--material M] [--check] [--harvest [bellflower]]`.
Policy: `resource/policy/gather.json` (`priority`, `keep_stamina`). Rules: R-106 to R-109, R-122 to R-124.

**Goal:** spend stamina above the 70 reserve on the priority material (ore today), 5 stamina a pickup; special
green-timer nodes always, blue-aura pickups first.
**End condition:** the pickup budget is spent, stamina at the reserve, 6 taps without a pickup, an unknown screen,
or 2 minutes.
**Ok statuses:** `budget_spent`, `no_spare_stamina`, `check`, `timeout`, `full`. Needs a look: `stamina_reserve`
(only when it hits the reserve before the budget), `stuck_progress`, `stuck_self`, `guarded`, `unknown_screen`,
`no_tracker`.

## Getting there (stamina materials)

```mermaid
flowchart TD
    S(["Start"]) --> P["1. Read the policy: material = priority[0], keep = 70"]
    P --> J["2. home, Journal, Map Exploration, tap the material"]
    J --> J2{"Screens opened?"}
    J2 -->|no| U(["unknown_screen"])
    J2 -->|yes| B["3. Read stamina; budget = (stamina - 70) / 5"]
    B --> B2{"--check, or budget 0?"}
    B2 -->|yes| CK(["check / no_spare_stamina"])
    B2 -->|no| E["4. Go, then OK on 'Enter ... to explore?'"]
    E --> E2{"On the island map?"}
    E2 -->|no| U
    E2 -->|yes| C[["5. collect(target, budget)"]]
    C --> H["6. go_home"] --> R(["collect's status"])
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef look fill:#fde2c8,stroke:#c25e00,color:#000
    classDef sub fill:#dbe9ff,stroke:#1f5fbf,color:#000
    class CK ok
    class U look
    class C sub
```

`--harvest bellflower` skips steps 1 to 4: it starts on the map with the item tracker showing (route R-123) and
collects until the tracker reads full (`full`), or `no_tracker` when there is none.

## The collector: one pass per screen read

```mermaid
flowchart TD
    D["Read the screen"] --> BS{"Budget spent?"}
    BS -->|yes| OK1(["budget_spent"])
    BS -->|no| W{"Screen?"}
    W -->|player_profile| SELF{"3rd time on ourselves?"}
    SELF -->|yes| SS(["stuck_self"])
    SELF -->|no| CL["Close it"] --> D
    W -->|"reward_popup, tap_to_continue"| RW["Close"] --> D
    W -->|dialogue| DL["Next"] --> D
    W -->|battle_prep| GD["Back arrow"] --> GDE(["guarded"])
    W -->|"anything else but world_map"| UK{"3rd time off the map?"}
    UK -->|yes| US(["unknown_screen"])
    UK -->|no| BA["Back arrow"] --> D
    W -->|world_map| ST{"Stamina under 75?"}
    ST -->|yes| SR(["stamina_reserve"])
    ST -->|no| PL{"What's in view? First match wins (R-124)"}
    PL -->|"1. green-timer special node"| T1["Tap it (free)"]
    PL -->|"2. material on the ground,<br/>blue aura first"| T2["Tap it"]
    PL -->|"3. tracking ring, over 70 px from us"| T3["Tap it"]
    PL -->|"4. ring at a screen edge"| T4["Tap it to pan"]
    PL -->|"5. ring only on the minimap"| T5["Centre camera, or walk a step toward it"]
    PL -->|nothing| T6["Centre camera or pan"]
    T1 --> PR
    T2 --> PR
    T3 --> PR
    T4 --> PR
    T5 --> PR
    T6 --> PR{"Stamina dropped (or tracker rose)?"}
    PR -->|yes| GOT["pickups + n, stale = 0"] --> D
    PR -->|"no, 6th tap"| SP(["stuck_progress"])
    PR -->|no| D
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef look fill:#fde2c8,stroke:#c25e00,color:#000
    class OK1 ok
    class SS,GDE,US,SR,SP look
```

Never tapped: the ring or icon floating over our own character (R-123), other players, anything inside the
minimap.
