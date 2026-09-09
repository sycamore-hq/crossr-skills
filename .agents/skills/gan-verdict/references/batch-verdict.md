# Batch verdict

Tokens stay `BLESS` / `REJECT`. Two forms.

Single-gate (AXEL): exactly one line, `<gate>: BLESS | REJECT`.
`REJECT` needs ` — ` or `: ` blockers.

```
code-review: BLESS
```

Set (AVRIL): exactly one line per id.

- `BLESS <id>` (an optional ` — …` note is allowed)
- `REJECT <id> — …` (the ` — ` blockers are required)

A bare BLESS over a set is not a verdict.
Fences do not hide a token: `audit-packet verdict` reads raw lines.

Failure classes:

- `silence` — an id with no line
- `blanket` — a token with no id, or `all`

Example:

```
BLESS T-1 — AC-01 covered
REJECT T-2 — no error path for empty input
```
