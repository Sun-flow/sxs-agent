# Runner and interrupt layer

Code: `sxs/core/loop.py` (runner, budgets), `sxs/core/interrupts.py` (mechanism), `sxs/actions/interrupts.py`
(the table), `sxs/core/nav.py` (`go_home`). Design notes: `docs/interrupts.md`.

**Goal:** run any loop the same way: one banner at the start, a stuck check instead of a hard time limit, the same
handling for screens that can show up anywhere, and one readout line at the end.

## A run, start to finish

```mermaid
flowchart TD
    S(["python -m sxs LOOP"]) --> A["1. Parse options, connect to the emulator"]
    A --> B["2. Wrap the detector with the interrupt table"]
    B --> C["3. Loop logs its banner: Running / Goal / End condition"]
    C --> D["4. Loop runs its own steps"]
    D --> E{"5. Every --budget seconds (default 120):<br/>progress reported in the last --stall s (60)?"}
    E -->|"yes, and fewer than 10 extensions"| D
    E -->|no| OB(["over_budget, then go home"])
    D --> F{"Loop reports progress, but the reading<br/>hasn't changed for --stall s?"}
    F -->|yes| ST(["stalled, then go home"])
    D --> G{"An interrupt handler raised LoopStop?"}
    G -->|yes| LS(["that status, e.g. needs_decision"])
    D --> H(["Loop returns its status"])
    H --> R["6. Log Result, print one JSON line,<br/>append to logs/runs.jsonl"]
    OB --> R
    ST --> R
    LS --> R
    R --> X{"Status in the loop's ok set?"}
    X -->|yes| X0(["exit 0"])
    X -->|"starts with refused"| X2(["exit 2"])
    X -->|no| X1(["exit 1: needs a look"])
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef look fill:#fde2c8,stroke:#c25e00,color:#000
    class X0 ok
    class OB,ST,LS,X1,X2 look
```

- Inside a loop, `with task(name, seconds)` gives one step its own budget and stall check: the step is cut and the
  loop goes on with the next one. Daily (120 s per step) and Upgrade (90 s per pass) work this way.
- A loop that never calls `progress(...)` ends at its first budget. Loops that report progress: explore and clear
  (Heartbeat), gather (pickups), roam (statues), cart, upgrade, tower floors, mall pages, gear swaps.

## Interrupts: checked after every screen read

Every `det.detect()` a loop makes goes through this table first, top row first. If a row matches, the loop waits
where it is, the handler runs under its own budget, the loop's resume step runs (if it registered one), and the loop
gets the screen after it.

```mermaid
flowchart TD
    D(["Loop calls det.detect()"]) --> R["Read the screen"]
    R --> O{"Row owned by this loop,<br/>or muted?"}
    O -->|yes| N["Skip that row"]
    O -->|no| M{"Row matches?<br/>checked in table order"}
    M -->|"choose_reward"| CR["Pick the class-matched reward (R-129)"]
    CR --> CR2{"Exactly one usable option?"}
    CR2 -->|no| STOP1(["LoopStop needs_decision"])
    CR2 -->|yes| RES
    M -->|"rating_popup"| RP["Tap Later (R-060)"] --> RES
    M -->|"chat"| CH["Close the chat panel (R-027)"] --> RES
    M -->|"tutorial highlight on<br/>world_map, home, companions"| TU[["tutorial.follow, 20 steps"]]
    TU --> TU2{"How did it end?"}
    TU2 -->|"highlight on a spend word"| STOP2(["LoopStop tutorial_spend_prompt"])
    TU2 -->|"companion invite with<br/>INVITE_COMPANIONS off"| STOP3(["LoopStop needs_decision"])
    TU2 -->|"same box 3 times"| MUTE["Mute the row for 120 s"] --> RES
    TU2 -->|"done or steps used"| RES
    M -->|"nothing matches"| BACK(["Loop gets the screen"])
    N --> M
    RES["Run the loop's resume step, if any<br/>(Clear Zone walks back to its zone)"] --> AG["Read the screen again<br/>(up to 3 handlers in a row)"]
    AG --> BACK
    classDef look fill:#fde2c8,stroke:#c25e00,color:#000
    classDef sub fill:#dbe9ff,stroke:#1f5fbf,color:#000
    class STOP1,STOP2,STOP3 look
    class TU sub
```

- A row that fires more than 5 times in 90 s is muted for 120 s, so a false match can't trap a loop.
- On purpose not in the table: fights, loading, dialogue, reward popups (every loop passes through them with
  `actions/common.pass_through`), defeat, battle prep and cards (the loop's goal decides), and `unknown` (each loop
  counts unknown screens itself and stops; mae's rule).

## Getting home: `nav.go_home()`

Every menu loop starts and ends with it, and the runner calls it after `over_budget` or `stalled`. One tap per
screen, from the table `TOWARD_HOME` in `sxs/core/nav.py`:

| Screen | Tap |
|---|---|
| title | Tap to play |
| loading, battle | wait |
| dialogue | next |
| reward_popup, tap_to_continue | close |
| confirm_dialog | Cancel |
| defeated | OK (goes home) |
| chat | close chevron |
| background_fight | minimise |
| rating_popup | Later |
| guild_donation | above the popup |
| cart | below the panel |
| world_overview, character, journal, guild, guild_no_guild | Home button |
| every other menu it knows (area_map, battle_prep, world_map, main_menu, quests, tower screens, enhance_gear, featured, daily_signin, growth_trial, material_realms, notice, guild screens, mall, prayer screens) | back arrow |
| game not running | start the game |
| agreement | stop: a human has to accept it |
| anything else (unknown, and the known screens listed in [states.md](states.md) as "no way home") | wait; every 3rd try tap below the popup, every 6th the back arrow; 40 tries, then give up |
