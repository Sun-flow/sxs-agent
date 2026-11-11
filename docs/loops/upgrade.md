# Upgrade loop and the Strengthen loop

Code: `sxs/loops/upgrade.py` (`Upgrader`), `sxs/loops/strengthen.py` (`Strengthener`). Commands:
`python -m sxs upgrade [--only skills,gear,...]`, `python -m sxs strengthen`. Notes: `docs/step5-upgrades.md`.
Rules: R-080, R-088, R-092, R-104, R-105, R-115 to R-119.

## Upgrade loop

**Goal:** take every upgrade a red "!" on the Character screen offers, using only soft resources (Rolla, ore,
Battle Essence, shards, class badges).
**End condition:** each pass run once (90 s budget each), its tap budget spent, or an unexpected screen.
**Ok statuses:** `done`. `unknown_screen` (Character screen didn't open) needs a look. A pass that fails is
recorded and the next pass runs.

```mermaid
flowchart TD
    S(["Start"]) --> CH["1. go_home, Character screen"]
    CH -->|"didn't open"| U(["unknown_screen"])
    CH --> BD["2. Read badges (2 frames: they pulse)"]
    BD --> LIT["Lit passes: skills always (blue arrows show no !);<br/>gear if a gear slot shows the blue up-arrow pip<br/>(a red ! there means swap: gearswap); class if Class has !;<br/>rank if the rank badge has !; relics never (locked)"]
    LIT --> G{"3. goals: any page lit?"}
    G -->|yes| GP["Open each lit page; claim its Goals tab if the tab has ! (R-116)"]
    G -->|no| SK
    GP --> RE{"Claimed anything?"}
    RE -->|yes| BD2["Read badges again: a ! that only meant Goals is gone"] --> SK
    RE -->|no| SK
    SK[["4. skills"]] --> GE{"gear lit?"}
    GE -->|yes| GEA[["5. gear"]] --> CL
    GE -->|no| CL{"class lit?"}
    CL -->|yes| CLA[["6. class_levels"]] --> RK
    CL -->|no| RK{"rank lit?"}
    RK -->|yes| RKA[["7. rank"]] --> RL
    RK -->|no| RL["8. relics: not unlocked, skipped"]
    RL --> OK(["done"])
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef look fill:#fde2c8,stroke:#c25e00,color:#000
    classDef sub fill:#dbe9ff,stroke:#1f5fbf,color:#000
    class OK ok
    class U look
    class SK,GEA,CLA,RKA sub
```

Each pass starts from the Character screen and goes home after. `--only` runs the named passes whether or not
they're lit.

### What each pass does

```mermaid
flowchart LR
    subgraph skills["skills (Skill page)"]
        direction TB
        s1["Quick Upgrade while its 'Upgrade' caption shows (max 5)"] --> s2["Each skill icon with !: Enhance, Ascend while Ascend has ! (R-115)"]
        s2 --> s3["Technique and Charm bag tabs with !: same"]
        s3 --> s4["Charm tab with !: put owned charms in empty slots"]
        s4 --> s5["Goals tab with !: claim Level and Quality"]
    end
    subgraph gear["gear"]
        direction TB
        g1["Enhance Gear in 5-level bands, weapon, head, chest, boots (R-092)<br/>until short or no change, max 60 taps"] --> g2["Resonance with !: Activate each tier (R-119)"]
        g2 --> g3["Goals tab with !: claim"]
    end
    subgraph class_levels["class_levels"]
        direction TB
        c1["Class Hierarchy: each card with !: OK the badge popup"] --> c2["Upgrade tab: press Upgrade while it has !"]
        c2 --> c3["Goals tab with !: claim. Never Change Class (R-117)"]
    end
    subgraph rank["rank"]
        direction TB
        r1["Advance only while its button has ! (R-118);<br/>a blue pip means a material is short"] --> r2["Goals tab with !: claim Level and Power"]
    end
```

Every button press first checks that no spend word sits on its row (`policy/claims.SPEND`), and stops when the
"!" goes away. A screen that isn't the expected one saves the frame and ends that pass.

## Get stronger (`get_stronger`, the Strengthen loop)

**Goal:** everything that raises power with soft resources, in one call. **Used by:** `explore --chain` after 3 lost
fights in a row, the daily loop's `strengthen` step (without the gear swap, which is its own daily step), and
`python -m sxs strengthen [--only cart,rank,gacha,relics,gear_swap,charms,upgrade]`. **Ok statuses:** `done`.
Each step has its own time budget and stall check (`STEP_BUDGET_S` in `sxs/loops/upgrade.py`); a step that fails or
runs out is recorded and the next one starts.

Rank comes first when the level is at the cap (mae, 2026-11-11 05:20, R-118): a rank-up is the biggest single power
gain (Apprentice III applied the banked bed EXP, Lv 30 → 37, power 30.6K → 35.9K). Then the Aeonic Gacha (mae 05:22,
R-167) and the Workbench (R-172), so new relics are activated and enhanced in the same pass: both are drawn in
[gacha.md](gacha.md). Built 2026-11-11 (`Upgrader.rank_first`, `get_stronger`); not yet run live.

```mermaid
flowchart TD
    S(["Start"]) --> A[["1. cart: claim the Cart (home sweep, adb pan fallback)"]]
    A --> RP["2. rank: Character > rank badge; read 'Level: N/M'"]
    RP --> CAP{"N = M (at the cap)?"}
    CAP -->|"no / unreadable"| GA
    CAP -->|yes| RA{"Advance button?"}
    RA -->|"! (all met)"| ADV["Advance, tap through RANK UP,<br/>claim rank Goals (R-116)"] --> BED["Collect bed EXP (daily bed step)"] --> GA
    RA -->|"blue pip (short)"| SH{"Middle cost (Bellflowers) short<br/>and tagged 'Available'?"}
    SH -->|"yes (first time)"| GAT[["gather: Flower Harvest (R-123)"]] --> RP
    SH -->|"no (Rolla, leaves, unknown)"| NOTE["Log the costs; carry on"] --> GA
    GA[["3. gacha: x10 on every tier with a full x10 (gacha.md)"]]
    GA --> RL[["4. relics: activate, ascend, enhance in bands (gacha.md)"]]
    RL --> B[["5. gear_swap: every slot with a red !"]]
    B --> C["6. charms: portrait, fill empty charm slots if the charm row has !"]
    C --> D[["7. upgrade: goals, skills, gear, class, rank"]]
    D --> OK(["done"])
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef sub fill:#dbe9ff,stroke:#1f5fbf,color:#000
    class OK ok
    class A,B,D,GA,RL,GAT sub
```

The Bellflower gather runs at most once per pass; a second shortfall is logged. Rank's own pass in the Upgrade loop
(step 7) stays: after step 2 it usually finds nothing, but it still claims rank Goals when they light up.
