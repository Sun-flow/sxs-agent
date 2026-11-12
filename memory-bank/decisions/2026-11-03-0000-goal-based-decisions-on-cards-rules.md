# 2026-11-03 · Goal-based decisions on cards, rules in a data file

- **Decision**: Every popup or card is read (title, text, buttons) and matched against ordered rules in `resource/policy/cards.json`, keyed on the current goal (explore, daily, idle) and circumstances (HP). A rule picks a button, Cancel, or dismiss. A card with no rule is dismissed and stops the run after 3, so a rule gets added once. Lasting choices (class) always stop with `needs_decision`.
- **Rationale**: mae asked for "select the correct option given goals and circumstances" rather than menu-advancing scripts. Rules as data let the supervisor (a model, later) add one rule per new card instead of editing code, so each new card costs model tokens once.
- **Alternatives considered**: always pressing the main button (walks into purchases and wrong dungeons); hard-coding per-screen handlers in Python (every new card needs a code change).
- **Status**: Accepted
