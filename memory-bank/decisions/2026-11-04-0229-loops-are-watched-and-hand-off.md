# 2026-11-04 02:29 · Loops are watched and hand off to each other

- **Decision**: Each loop (`sxs.loops.explore`, `sxs.loops.tower`, `sxs.loops.fogwalk`, `sxs.actions.goto`) logs a banner at start, a heartbeat every 30 s, and ends early with a named reason (stuck_progress, stuck_self, stuck, unknown_screen with a saved frame, power_gate, repeating_card) instead of idling. Stalls rotate through unstick strategies (walk to the quest's area, talk to a red "!", fight a blocker or guard, pan). The explore loop calls the tower loop on Fantasia Ascent screens and resumes after.
- **Rationale**: mae (2026-11-04): loops must notice being stuck, report unfamiliar screens, and call each other; a stuck loop is a robustness bug to fix, not a restart.
- **Alternatives considered**: one 5-minute give-up timer (what we had; it idled silently on a counterless quest).
- **Status**: Accepted
