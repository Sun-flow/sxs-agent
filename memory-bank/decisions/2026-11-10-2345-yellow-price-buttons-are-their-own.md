# 2026-11-10 23:45 · Yellow price buttons are their own detector class, btn_price

- **Decision**: Mall, Vendor Booth and purchase-prompt price buttons (USD, Dawnium) are labelled `btn_price`, a new class appended to `resource/detect/classes.json`, never `btn_primary`.
- **Rationale**: mae (2026-11-10, decision card). They look identical to action buttons; a separate class lets the bot refuse spend buttons by class as a second safeguard beside the text check.
- **Alternatives considered**: label them `btn_primary` and rely on the text check only; leave shop screens unlabelled (the model would still fire on them).
- **Status**: Accepted
