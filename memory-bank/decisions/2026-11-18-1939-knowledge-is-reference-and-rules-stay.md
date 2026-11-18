# 2026-11-18 19:39 · knowledge/ is reference; rules in memory-bank/game/rules/ stay binding (mae, 2026-11-18)

- **Decision**: Game facts and advice from player guides and public wikis go in `knowledge/`, each with a source tag and a tier. They are reference. What the bot may do is still decided only by `memory-bank/game/rules/`. Where a guide's advice disagrees with a rule, the disagreement is listed in `knowledge/conflicts.md` with a recommendation, and mae decides; the rule changes only then.
- **Rationale**: mae asked for an exhaustive wiki ("this is not memory bank files, but wiki information"), which is too large and too unverified for the memory bank; rules were confirmed on our own account. mae also said Dawnium spending is allowed and wants spend and income plans, while R-018 and R-043 still say never spend: that change needs an explicit, approved spend plan, not a silent edit.
- **Alternatives considered**: putting guide facts into the rules files (mixes unverified facts with binding rules; the docs thread owns rule edits); editing the Dawnium rules in the same PR (a spending change the bot would act on without mae reviewing the plan).
- **Status**: Accepted
