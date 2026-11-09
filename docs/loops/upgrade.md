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
    BD --> LIT["Lit passes: skills always (blue arrows show no !);<br/>gear if a gear slot has !; class if Class has !;<br/>rank if the rank badge has !; relics never (locked)"]
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
        r1["Advance only while its button has ! (R-118)"] --> r2["Goals tab with !: claim Level and Power"]
    end
```

Every button press first checks that no spend word sits on its row (`policy/claims.SPEND`), and stops when the
"!" goes away. A screen that isn't the expected one saves the frame and ends that pass.

## Strengthen loop (the older, simpler path)

**Goal:** get stronger between fights with soft resources. **Used by:** `explore --chain` after 3 lost fights in a
row. The daily loop's `strengthen` step does *not* use this; it uses the Upgrade loop above.
**Ok statuses:** `done` (it always returns done).

```mermaid
flowchart TD
    S(["Start"]) --> A["1. Claim the Cart (sweep home for the bubble)"]
    A --> B["2. Enhance gear in 5-level bands (same as the gear pass)"]
    B --> C["3. Skill page, first technique, Enhance:<br/>each of 4 tabs press Upgrade up to 12 times until 'Insufficient'"]
    C --> D["4. go_home"] --> OK(["done"])
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    class OK ok
```

Step 3 levels techniques one by one instead of Quick Upgrade (R-104), and the loop doesn't swap gear (R-088) or run
the Goals, class or rank passes. See [open-questions.md](open-questions.md) Q9.
