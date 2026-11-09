# Gear Swap loop

Code: `sxs/loops/gearswap.py` (`GearSwap`). Command: `python -m sxs gearswap [--check] [--all]`; daily step
`gear_swap`. Rules: R-088, R-080.

**Goal:** wherever a gear slot on the Character screen shows "!", put on the better piece. The badge says where to
look; the power compare decides.
**End condition:** every flagged slot tried once, or an unknown screen.
**Ok statuses:** `done`, `nothing`, `checked`. Needs a look: `unknown_screen`.

```mermaid
flowchart TD
    S(["Start"]) --> C["1. go_home, Character screen"]
    C -->|"didn't open"| U(["unknown_screen"])
    C --> F["2. Flagged slots: a ! on the rim of weapon, head, chest, boots<br/>(2 frames)"]
    F --> CK{"--check?"}
    CK -->|yes| CHK(["checked"])
    CK -->|no| L{"3. Next slot to try?<br/>(flagged ones; every slot with --all)"}
    L -->|none left| E{"Swapped any?"}
    E -->|yes| D(["done"])
    E -->|no| N(["nothing"])
    L -->|slot| T["Tap the piece: item card"]
    T --> R{"Replace or Equip button?"}
    R -->|no| KEEP1["Close the card: no_replace"] --> L
    R -->|yes| RL["Replace: Replace Gear list (best first)"]
    RL --> RL2{"List opened?"}
    RL2 -->|no| U2(["unknown_screen"])
    RL2 -->|yes| CMP["First candidate: compare screen,<br/>read power equipped vs new"]
    CMP --> PW{"New power higher?"}
    PW -->|yes| SW["Replace under the new piece"]
    PW -->|no| KEEP2["Keep"]
    SW --> BK["Tap back out to the Character screen"]
    KEEP2 --> BK
    BK --> FL{"Swapped and the slot still flagged?"}
    FL -->|yes| GU["Give it up for this run"] --> L
    FL -->|no| L
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef look fill:#fde2c8,stroke:#c25e00,color:#000
    class D,N,CHK ok
    class U,U2 look
```

Never touched here: Rcmd Loadouts, Change Class, charms, techniques, enhancing (that's the Upgrade loop). The
enhancement level carries over to the new piece (R-088). No offhand slot yet.
