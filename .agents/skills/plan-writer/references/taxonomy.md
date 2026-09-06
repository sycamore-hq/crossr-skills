# Claim taxonomy

Three types. No fourth.

| Type | Verified by | Example |
|---|---|---|
| **mechanical** | a command + expected exit | `rg '\.unwrap\(' src/` → 0 |
| **observable** | pointing at `file:line`, no judgment | "`ParseError` has `From<io::Error>`" |
| **judgment** | an LLM read | "the retry policy is comprehensible" |

## Quota

Judgment claims may not exceed 30% of **active** (non-superseded) claims.
`scripts/audit-plan` enforces this. The Architect rejects a plan that
fails the quota — that is underspecification, not a style note.

## Ids

- Claims: `C-01`, `C-02`, …
- Acceptance criteria: `AC-01`, `AC-02`, …
- Preserve items: `PV-01`, …
- Evidence-packet gaps: `G-01`, …

Append-only. A superseded claim keeps its id and is marked
`C-01 [superseded]: …`. The replacement gets a new id. Deleting or
renumbering a claim breaks reviewer citations and the unsatisfiable-claim
escalation trigger.

## Line shape

```
- C-01: mechanical · AC-01 · rg '\.unwrap\(' src/ → 0
- C-02: observable · AC-01, AC-02 · ParseError has From<io::Error>
- C-03: judgment · AC-02 · retry policy is comprehensible
```

A mechanical claim without `→` fails the audit. An active claim whose AC
ids are unknown is an orphan — scope creep, caught by script.
