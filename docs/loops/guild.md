# Guild loop

Code: `sxs/loops/guild.py` (`Guild`). Command: `python -m sxs guild [--only donate,afk,conquest]`; daily steps
`guild_donate` ★, `guild_afk`, `guild_conquest` ★ (★ once a day). Rules: R-102, R-103, R-110, R-111, R-112, R-113, R-114.

**Goal:** the guild dailies: two donations, the character parked at the Forge, both Conquest attempts used in the
background, goals claimed.
**End condition:** each step tried once, then home.
**Ok statuses:** each step reports `done`, `nothing` or `unknown_screen`; the loop itself always ends `done`.

```mermaid
flowchart TD
    S(["Start"]) --> DN[["1. donate"]] --> AF[["2. afk"]] --> CQ[["3. conquest"]] --> H["Back to the island, go_home"] --> OK(["done"])
    classDef ok fill:#d4edda,stroke:#2e7d32,color:#000
    classDef sub fill:#dbe9ff,stroke:#1f5fbf,color:#000
    class OK ok
    class DN,AF,CQ sub
```

## donate (R-103)

```mermaid
flowchart TD
    S(["Guild island, Guild Lobby, Donation"]) --> N{"Read 'Daily Donations: N/5'"}
    N -->|unreadable| E1(["stop"])
    N -->|"N >= 2"| E2(["stop"])
    N -->|"N < 2"| B{"Button reads Free, or a cost of 20 or less?"}
    B -->|no| E3(["stop: over the 20 Dawnium cap"])
    B -->|yes| T["Tap Donate"]
    T --> C{"Confirm dialog?"}
    C -->|"says donation and x20 or less"| OK1["OK"] --> N
    C -->|"anything else"| CN["Cancel"] --> E4(["stop"])
    C -->|"no dialog"| N
```

## afk (R-110)

```mermaid
flowchart TD
    S(["Read our name from the HUD"]) --> F["Next facility: Forge, then Mine, then Power Station"]
    F --> IN{"Our name on its slot list?<br/>(two screens for the Forge)"}
    IN -->|yes| N(["nothing: already there"])
    IN -->|no| SL{"Empty + slot?"}
    SL -->|no| F
    SL -->|yes| AD["Tap it: AFK Details, Start"]
    AD --> SWQ{"'Switch anyway?' confirm?"}
    SWQ -->|yes| OKS["OK"] --> RW
    SWQ -->|no| RW["Close 'You received'"] --> D(["done"])
    F -->|"all three full"| N2(["nothing"])
```

## conquest (R-111, R-112)

```mermaid
flowchart TD
    S(["Gate of Expedition, Conquest"]) --> BF{"Floor says Boss defeated? (up to 6)"}
    BF -->|yes| CH["Claim its chest, step right"] --> BF
    BF -->|no| AT{"Attempts left (Daily Challenge Attempts N/2)?"}
    AT -->|"yes, up to 3 loops"| C["Challenge"]
    C --> P{"Battle prep or the fight?"}
    P -->|battle_prep| SB["Start Battle"] --> MIN
    P -->|background_fight| MIN["Minimise (background icon)"]
    P -->|"neither"| GO
    MIN --> AT
    AT -->|no| GO{"Back on Conquest?"}
    GO -->|no| E(["done if a fight started, else unknown_screen"])
    GO -->|yes| GL["Goals: claim Serverwide, then Personal"] --> D(["done / nothing"])
```

Never: Create, Upgrade, Construction, Guildmates actions, chat, the guild Shop (R-114).
