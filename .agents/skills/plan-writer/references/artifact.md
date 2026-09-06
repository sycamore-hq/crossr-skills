# Plan artifact

## Path

| Harness | Path |
|---|---|
| Pinto disclosed | `docs/plans/pbi/<id>.plan.md` |
| Portable fallback | `<disclosed-backlog-path>/plans/<id>.plan.md` |
| Never | `.pinto/tasks/` |

Blessed means committed, then immutable. The plan commit carries the PBI
id and lands **before** the first implementation commit.

## Required skeleton

```markdown
# Plan: <pbi-id>

## Phases
### Phase 1 of n: <name>
…

## Acceptance Criteria
- AC-01: …

## Claims
- C-01: mechanical · AC-01 · <command> → <expect>

## Preserve
- none — no prior verified record
# or
- PV-01 → C-02: <what must survive>

## Unresolved questions
- …
```

`## Phases` **is** the decomposition. The conductor does not invent
phase boundaries after the fact.

## Five rules (restated)

1. Blessed means immutable; commit before implementation.
2. Claim ids are append-only.
3. Coverage is bidirectional — `scripts/audit-plan` is the script.
4. The plan outlives the PBI; the Completion Record gains `## Plan`.
5. Preserve-vs-grow: list what must survive, from a verified record
   when one exists.

Audit red never costs an Architect token. Revise the plan.
