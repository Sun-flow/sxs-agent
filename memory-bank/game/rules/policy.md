# Policy rules

Read before pressing any button that might spend, and on any class, social, account or rating prompt. This file alone lists every never-do and every exception.

## Spending and other never-dos

### R-043 · Never press a spending button unless an exception below allows it
**Never press:**
- **Any button reading Buy, Purchase, Refresh, Spend, Pray, Recharge or Top up, or showing Dawnium or a USD price.** The only Dawnium spend is the first two daily guild donations.
- **"Catch Up"** on the sign-in calendar (R-097); **"Advanced Trial"** (R-098); **Dawnstar Prelude draws** (R-096).
- **"Purchase Iron Hammer"** (60 Dawnium): tap Cancel (0.32, 0.65) (R-095).
- **Prayer "+"** (buys tickets); **Pray x1 ever; Pray x10 outside mae's pull script** (R-093).
- **Packs**: main-menu event banner (R-053), home "Starter Pack" (R-126), every Mall pack and the Top Up tab (R-121).
- **Shop Refresh**: Vendor Booth (4K Rolla) (R-120), Daily Shop (R-019).
- **Any shop item, in any shop, until mae has filled the Buy? column of `docs/shop-tables.md` and the shop has a buy list in the repo** (mae) (R-120). Read stock only via info cards (R-125).
- **Extra material-dungeon attempts** (Dawnium; 2 free a day) (R-015).
- **"Create Guild"** (R-102); **Link Account** or anything account-related (R-096).

**Never do:**
- **A 3rd guild donation in a day** (R-103).
- **Choose a class or press "Change Class"**: mae's call (R-054, R-117).
- **"Rcmd Loadouts"** or its Apply (R-080).
- **Anything social** (requests, Apply, Team, other players); guild choice beyond joining one random open guild is mae's (R-057, R-077, R-102).
- **Delete or dismantle items**; **accept agreements or account prompts** (mae).
- **Type in chat**; close Server Chat with the down arrow (0.06, 0.96) (R-027).
- **Rate the game or open the store**: rating popups get **Later** (mae) (R-060).
- **Retry on the Fantasia Ascent DEFEAT screen**, or tick Auto Challenge there (R-079).
- **Spend stamina while exploring**: in explored, blessed areas, respawned monsters and most interactables cost stamina; don't tap them (even on a reference-crop match) unless a loop is deliberately farming, e.g. battle essence for skills (mae) (R-065, R-131).
- **Pick a "Choose Your Reward" option when both are valid**: ask mae; only a lone Class Mismatch lets the bot take the other (R-129).

**Allowed (the only exceptions):**
- **Healing food**: buy with Rolla or cook, eat freely; conserve stat-boost **dishes** (R-061).
- **Skill pulls**: only `python -m sxs pray --pulls N --handler-approved`, started by mae for that run, x10 only (R-093).
- **Guild donations**: the first two a day, the 2nd costing 20 Dawnium (R-103).
- **Vendor Booth Vault "Free" x30 Stamina**: once a day, only if OCR reads exactly "Free" (mae) (R-120).
- **Mall free gift boxes** (top-left box with "!"), once per refresh, nothing else on the page (mae) (R-121).
- **Free card buttons**: safe verbs on map-object cards (R-030; a map card's "Pray" is not the Prayer gacha), Gate of Power "Open" (R-086), free Explore/Challenge on mini-dungeon and gate cards (R-071, R-082), free travel OK (R-089), claims behind red "!" (R-063).
- **Upgrades with soft currency or materials**: gear enhancement (Rolla, ore), techniques (Battle Essence), ascension (shards), class badges; rank advancement only when Advance shows "!" and with free materials (R-118).
- **Stamina** above the 70 reserve (R-107); mining with free Iron Hammers (R-095).
*told* · R-042, R-093, R-103, R-120

## Answering cards and dialogs

### R-042 · Answer cards by a goal-dependent policy, not a fixed tap
Policy: `resource/policy/cards.json`, `sxs/policy/decide.py`; nav-graph edges mirror it in `when`. The `never` regex in that file blocks the R-043 buttons (Buy, Purchase, Refresh, Spend, Dawnium, Pray, Recharge, Top up, Catch Up, Advanced Trial, Create Guild, Change Class, USD/$, hammer) whatever the card; `sxs.loops.pray` doesn't use the decider.
- Defeated: OK (home). Travel prompt: OK when exploring or doing dailies, Cancel when only going home. Portal: Activate.
- Mini-dungeon card: Explore only if the goal is explore and HP is fine, else dismiss. Dungeon floor: Next Floor if HP is fine, else the back arrow.
- Unknown card: dismiss and log.
*told* · R-043, R-091

## Skill pulls (Prayer)

### R-093 · Skill pulls run only from mae's pull script, x10 only
- Prayer (skill gacha) is the home **goddess Statue furniture** ("Pray to the goddess...") beside the "Class to Unlock" stone, about (0.07, 0.63) on the default camera; find it by template (R-126). Not the map statues that bless areas (R-070).
- **The bot never taps Pray itself.** Pulls run only via `python -m sxs pray --pulls N --handler-approved`, started by mae for that run. No loop or decision function may call it.
- **x10 only, never x1** (mae). N is a multiple of 10; under 10 Stellatie, no pull.
- Standard banner, Stellatie only (x10 = 10). The script never presses "+", cancels purchase prompts, and stops if Dawnium changes. The Affection banner (red tokens, x10 = 250) is not used.
- Screen: tabs Prayer / Exchange / Goals, banner selector, "Prayers Today n/10000", "200 Prayers Bonus" (Legendary of choice), pity counter.
- Stellatie: Daily Sign-in, 10 a day (R-097). Goals tab "Total Standard Prayers" milestones (10, 20 ... 60) are free claims; 10 paid 3 Iron Hammers (R-095).
*told, observed* · `home/prayer.png`, `home/prayer_result.png`, `home/prayer_tickets.png`, `home/prayer_affection.png`, `home/furniture_statue.png` · node `prayer`, `prayer_result` · R-043, R-095, R-097

## Class choice

### R-054 · Class choices are mae's: pick Leave and stop
- After the Guardian Colossi boss, "Crossroads of Classes: Talk to the Mysterious Elder" leads to the Chief at the Originisle V pillar: "Ascend to Mage", "Change Class" or "Leave".
- **The bot never chooses a class.** It picks Leave and stops with `needs_decision`; `python -m sxs explore --choose "<regex>"` applies a human's choice. mae chose **Mage**.
- The class screen shows trait stats and a class-skill grid, Ascend at (0.5, 0.86).
- Boss loot (chests, an orb, an ore pile) lies around the pillar: collect it.
*observed, told* · `character/class_choice.png`, `character/class_ascend.png` · node `class_choice`, `class_ascend` · R-117, R-062

## Social

### R-057 · Leave social requests alone
- **Never accept, decline or touch social requests: mae's call.**
- The badged person icon on the map's left edge (0.06, 0.6) opens "Apply" (Friends / Team Up / Challenge / Room; Decline All, Agree All). Don't use it.
- Ignore Friend Request toasts (X / check) on home near the tracker. Never tap other players in the world (R-123).
*observed, told* · `guild/apply_requests.png` · node `apply_requests` · R-077, R-027, R-102

### R-077 · Leave the Team panel alone
The flag at the map's top left (0.08, 0.12) opens the Team panel (Players, Team Goal, World Call / Invite / Nearby). **Don't touch it.**
*observed* · `home/team.png` · node `team` · R-057
