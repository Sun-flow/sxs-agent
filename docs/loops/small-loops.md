# Small loops: Mall, Vendor Booth, Tutorial, Progress, Pray

## Mall gifts

Code: `sxs/loops/mall.py`. Command: `python -m sxs mall [--part 1|2]`; daily steps `mall_gifts` ★ and `mall_gifts_2` ★.
Rule: R-121. **Goal:** the free gift box on each Mall page; never a price. **Ok:** `done`, `nothing`.

```mermaid
flowchart TD
    S(["Start"]) --> O["home, Menu, Mall"]
    O -->|"not mall"| U(["unknown_screen"])
    O --> P["Next banner: part 1 = first four, part 2 = four after one scroll"]
    P --> T["Tap it"]
    T --> Q{"A page opened?"}
    Q -->|no| P
    Q -->|yes| G{"Red ! in the page's top-left box? (look 2 s)"}
    G -->|yes| C["Tap the box, close YOU RECEIVED (max 2)"] --> G
    G -->|no| B["Back arrow to the list"] --> P
    P -->|"no banner left"| E(["done if any claimed, else nothing"])
```

## Vendor Booth

Code: `sxs/loops/vendor.py`. Command: `python -m sxs vendor [--check]`; daily step `vendor_stamina` ★. Rule: R-120.
**Goal:** the Vault's free x30 Stamina; nothing else. **Ok:** `done`, `nothing`, `free_available`.

```mermaid
flowchart TD
    S(["Start"]) --> O["home, pan sideways until the wagon shows, tap it"]
    O -->|"not found, or title isn't Vendor"| U(["unknown_screen"])
    O --> V["Vault tab"]
    V --> F{"First cell's price reads exactly 'Free'?"}
    F -->|no| N(["nothing"])
    F -->|"yes, --check"| FA(["free_available"])
    F -->|yes| T["Tap it"]
    T --> R{"Then?"}
    R -->|"reward popup"| C["Close"] --> D(["done"])
    R -->|"a confirm dialog"| X["Cancel, save the frame"] --> ND(["needs_decision"])
```

## Tutorial follower

Code: `sxs/loops/tutorial.py` (`follow`). Command: `python -m sxs tutorial [--steps N]`. Also run by the
interrupt table ([runner.md](runner.md)) on world_map, home and companions. Rules: R-036, R-057.
**Goal:** tap what the game's tutorial highlights, through its dialogue. **Ok:** `done`, `steps`.

```mermaid
flowchart TD
    D["Read the screen (up to --steps times)"] --> W{"Screen?"}
    W -->|dialogue_choice| DC["Tap the detected option"] --> D
    W -->|dialogue| DN["Next"] --> D
    W -->|"reward_popup, tap_to_continue"| RW["Close"] --> D
    W -->|loading| LD["Wait"] --> D
    W -->|"companions, invites off"| ND(["needs_decision"])
    W -->|other| H{"Yellow highlight box? (filled glow on companions)"}
    H -->|no| HT{"Akane hint bubble?"}
    HT -->|yes| HB["Tap 100 px below it"] --> D
    HT -->|"no, 6th time"| DONE(["done"])
    HT -->|no| D
    H -->|"same box 3 times"| ST(["stuck"])
    H -->|"text is a spend word"| SP(["spend_prompt"])
    H -->|yes| TAP["Tap the box"] --> D
    D -->|"steps used"| STEPS(["steps"])
```

## Progress (read only)

Code: `sxs/loops/progress.py`. Commands: `python -m sxs progress [--only hud,profile,...] [--guild-shop]`,
`python -m sxs report [--day D]`; daily step `progress`. Notes: `docs/progress-tracker.md`.
**Goal:** read the account's numbers, keep one snapshot per server day, write the day's report. Taps nothing that
acts. Sections run in order, each with its own budget: `hud` (home top bar), `profile` (portrait), `journal`
(tower floor), `guild` (lobby), `areas` (area map %). The daily step reads only hud, profile and journal.

## Pray (mae only)

Code: `sxs/loops/pray.py`. Command: `python -m sxs pray --check` or `python -m sxs pray --pulls N --handler-approved`.
Rule: R-093. **Nothing calls this loop**; it runs only when mae starts it for that run.

```mermaid
flowchart TD
    S(["Start"]) --> A{"--check, or --pulls N (multiple of 10) with --handler-approved?"}
    A -->|neither| RF(["refused"])
    A -->|"--check"| CK["Open Prayer, read tickets and Dawnium"] --> C(["checked"])
    A -->|pulls| O["home, goddess Statue, Prayer, Standard banner"]
    O --> L{"Pulls left?"}
    L -->|no| D(["done"])
    L -->|yes| T{"Tickets read twice the same, and 10 or more?"}
    T -->|"unreadable"| E0(["unknown_screen"])
    T -->|"under 10"| E(["out_of_tickets"])
    T -->|yes| P["Pray x10"]
    P --> SD{"Purchase or shortage dialog?"}
    SD -->|yes| X["Cancel"] --> E2(["would_spend"])
    SD -->|no| R["Wait for the result, note what came"]
    R --> DW{"Dawnium went down?"}
    DW -->|yes| E3(["dawnium_changed"])
    DW -->|no| L
```

After pulling it claims the Prayer Goals tab (Iron Hammers). No Prayer screen: `no_statue`.
