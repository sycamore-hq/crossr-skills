---
name: gan-verdict
description: |
  Verdict and report-envelope protocol for every CrossR GAN gate.
  Owned by neither conductor nor adversary; referenced by both, redefinable by neither. The conductor may specify what it wants to hear, never what counts as approval.
---

# GAN Verdict Protocol

1. Verdict tokens: exactly `BLESS` or `REJECT`. Silence, hedge, or "LGTM" is not approval.
2. One verdict per delegation.
3. The verdict names its gate: `<gate>: BLESS | REJECT` (e.g. `architecture: BLESS`).
4. `REJECT` must cite concrete blockers.
5. Report envelope — field schema (all fields optional; the conductor selects which apply and fills the values at delegation time):
   - phase id
   - "k of n"
   - AC ids claimed
   - findings shape (one-liners | prose)
   - max length
   - `file:line` citations
6. The envelope goes **last** in the delegation prompt, after persona + gate card — persona and ruleset are the stable cacheable prefix; the envelope varies per delegation, and splicing it above the ruleset destroys prefix stability.
7. Adding an envelope field means changing this file — never a conductor card.
8. Handoff packet — inbound field schema (conductor fills; adversary receives nothing else): phase id · "k of n" · gate · file list · diff (fenced, or a ref) · AC subset claimed · claim ids covered · prior verdicts as one-liners · envelope (item 5). Never: a sibling SKILL.md, a previous-phase essay, a whole-board dump, dashboard HTML. Grammar: `references/handoff-packet.md`. Gate: `audit-packet brief`. Lives at the disclosed packet scratch path, never in the tree.
9. Set review — one verdict line per id: `BLESS <id>` | `REJECT <id> — <blockers>`. A bare BLESS over a set is not a verdict. Gate: `audit-packet verdict --items`.
10. Adding a packet field means changing this file — never a conductor card (same rule as item 7).
