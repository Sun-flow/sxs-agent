# Cart Upgrade loop

Code: `sxs/loops/cart.py` (`CartUpgrader`), Cart claim in `sxs/loops/strengthen.py` (`Strengthener.claim_cart`).
Command: `python -m sxs cart [--check] [--max N]`; daily steps `cart` (claim) and `cart_upgrade`. Rules: R-020,
R-100, R-126, R-136.

**Goal:** claim the Cart's AFK loot, then raise the Stone and Wood income rows with ordinary materials, keeping them
level: the lower one first, Stone on a tie. Every other row and every Unlock button is left alone.
**End condition:** a cost we can't pay (`short`), the Blessing Level cap (`capped`), a cost we don't recognise, a
level that won't rise, or an unexpected screen.
**Ok statuses:** `done`, `short`, `capped`, `checked`, `max_upgrades`. Needs a look: `needs_decision`, `no_cart`,
`unknown_screen`, `unreadable_level`, `no_change`, `no_cost`, `no_button`.

```mermaid
flowchart TD
    S(["Start"]) --> C1["1. go_home; sweep home slowly left then right<br/>for the Cart's loot bubble; tap it, Claim All"]
    C1 --> C2["2. Sweep again for the Cart itself (by its wheel), tap it"]
    C2 --> C3{"Cart panel open?"}
    C3 -->|"no, first time"| RS["Restart the game (home stuck on sky, R-100)"] --> C2
    C3 -->|"no, after a restart"| NC(["no_cart"])
    C3 -->|yes| C4["3. Stone row's arrow: Furniture Upgrade"]
    C4 --> C5{"furniture_upgrade?"}
    C5 -->|no| U1(["unknown_screen"])
    C5 -->|yes| C6["4. Read Stone and Wood levels from their tabs"]
    C6 --> C7{"Both read?"}
    C7 -->|no| UL(["unreadable_level"])
    C7 -->|yes| PK["5. Pick the lower row; Stone on a tie"]
    PK --> RC["6. Read the cost: icons and have/need"]
    RC --> K{"Cost check, in order"}
    K -->|"a spend word (Dawnium, Buy, USD...)<br/>or an icon we don't know"| ND(["needs_decision"])
    K -->|"no cost read"| NOC(["no_cost"])
    K -->|"have under need"| SH(["short / done"])
    K -->|"button says Unlocks at Blessing Lv. N"| CAP(["capped / done"])
    K -->|"no Upgrade button"| NB(["no_button"])
    K -->|"all fine, --check"| CHK(["checked"])
    K -->|"all fine"| UP["7. Upgrade x1"]
    UP --> V{"Still on furniture_upgrade<br/>(after closing a banner)?"}
    V -->|no| U2(["unknown_screen"])
    V -->|yes| LV{"Level went up?"}
    LV -->|no| NCH(["no_change"])
    LV -->|yes| MX{"--max upgrades done? (default 50)"}
    MX -->|yes| MU(["max_upgrades"])
    MX -->|no| PK
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef look fill:#fde2c8,stroke:#c25e00,color:#000
    class SH,CAP,CHK,MU ok
    class NC,U1,UL,ND,NOC,NB,U2,NCH look
```

`short` and `capped` become `done` when at least one upgrade went through this run. Today (05:11, 2026-11-05)
Stone and Wood are Lv 5, capped by Blessing Lv 5: raising the bed's Blessing Level is what unblocks this loop.

**Not yet in the loop:** mae asked on 2026-11-09 to always unlock any production row that can be unlocked (free).
The loop and R-136 still ignore Unlock buttons: see [open-questions.md](open-questions.md) Q1.
