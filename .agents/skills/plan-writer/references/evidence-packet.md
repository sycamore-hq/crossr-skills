# Evidence packet (plan-time)

When a prior evidence packet exists, load it before writing claims.
Do not invent a packet. Absence is `## Preserve` →
`none — no prior verified record`.

A packet is a completion record, an AC-evidence bundle, or any
verified record the harness discloses for a prior increment.

## Become claims

- Each **gap** in the packet becomes a claim (`G-01 → C-nn`).
- Each **preservation constraint** becomes a claim (`PV-01 → C-nn`).
- Preserve-vs-grow is rule 5: every increment lists functionality
  that must survive, sourced from those records when present.

```markdown
## Evidence packet
- path: docs/evidence/<prior-id>.md
- gap G-01 → C-04
- preserve PV-01 → C-02
```

`scripts/audit-plan` fails a named packet that maps a gap or preserve
id to a missing or superseded claim, or that names a path and then
maps nothing.

## Not this card

Scope change still returns to AVRIL. This card does not re-bless
product intent. AXEL does not either.
