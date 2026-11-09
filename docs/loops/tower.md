# Fantasia Ascent loop (tower)

Code: `sxs/loops/tower.py` (`open_from_home`, `climb`). Command: `python -m sxs tower [--tower NAME] [--to F] [--floors N]`;
daily step `fantasia_ascent`. Also called by [explore.md](explore.md) and [fogwalk.md](fogwalk.md) when a tower
screen shows. Rules: R-079, R-112, R-127, R-061.

**Goal:** one climb a day with Auto Challenge on, until the first loss. Never Retry a loss.
**End condition:** first loss, a floor more than 1.25x our power, no Challenge left, `--to` floor cleared,
Auto Challenge already climbing, or an unfamiliar screen.
**Ok statuses:** `lost`, `too_strong`, `floors_done`, `reached`, `auto_running`. Needs a look: `low_hp`,
`unknown_screen`, `not_tower`, `timeout`. The daily step marks the day done on any ok status; the loop also marks
it on a loss.

```mermaid
flowchart TD
    S(["Start"]) --> O{"On a tower screen or battle prep?"}
    O -->|no| OP["home, Journal, Fantasia Ascent card"]
    OP -->|"list didn't show"| U0(["unknown_screen"])
    OP --> D
    O -->|yes| D["Read the screen"]
    D --> W{"Screen?"}
    W -->|tower_list| TL{"Card for --tower, or the 'Current' card?"}
    TL -->|no| U1(["unknown_screen"])
    TL -->|yes| TLT["Open it"] --> D
    W -->|tower_floors| AC{"Floor shows Auto-Challenging?"}
    AC -->|yes| AR(["auto_running: leave it climbing"])
    AC -->|no| CB{"Challenge button?"}
    CB -->|no| FD(["floors_done"])
    CB -->|yes| PWR{"Floor power within 1.25x ours? (R-127)"}
    PWR -->|no| TS(["too_strong"])
    PWR -->|yes| CH["Challenge"] --> D
    W -->|battle_prep| HP{"HP 70%+ after healing from the portrait?"}
    HP -->|no| LH(["low_hp"])
    HP -->|yes| SB["Start Battle"] --> D
    W -->|tower_result| RES{"VICTORY?"}
    RES -->|"no: DEFEAT"| LOSS["Mark today done, back arrow (never Retry)"] --> LO(["lost"])
    RES -->|"yes, same floor as last time"| WAIT["Wait for the countdown"] --> D
    RES -->|yes| V["Tick Auto Challenge if off; note the floor"]
    V --> TO{"Reached --to, or --floors cleared?"}
    TO -->|yes| RCH(["reached / floors_done"])
    TO -->|no| CONT["Continue"] --> D
    W -->|background_fight| BG["Wait (our Auto Challenge fight)"] --> D
    W -->|"battle, loading, dialogue, rewards"| PT["Pass through"] --> D
    W -->|"unknown, 5 in a row"| U2(["unknown_screen"])
    W -->|"any other known screen"| NT(["not_tower"])
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef look fill:#fde2c8,stroke:#c25e00,color:#000
    class AR,FD,TS,LO,RCH ok
    class U0,U1,LH,U2,NT look
```

When explore or fogwalk meet a tower screen, they check today's mark first: if the day's climb already ran they
leave the tower; otherwise they climb and mark the day (R-079, [open-questions.md](open-questions.md) Q10).
