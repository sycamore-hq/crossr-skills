# Plan artifact

## Path

| Harness | Path |
|---|---|
| Plan path disclosed | that path |
| Otherwise | `docs/plans/pbi/<id>.plan.md` |
| Never | the board's own item store, wherever it lives |

`<id>` is the board's item id, so the plan, the commits and the item all
carry the same name. The plan is a repository artifact under review; the
board holds work state. Writing a plan into the tracker's store puts a
reviewable document somewhere nothing reviews it.

Blessed means committed, then immutable. The plan commit carries the PBI
id and lands **before** the first implementation commit.

## Required skeleton

```markdown
# Plan: <pbi-id>

## Phases
### Phase 1 of n: <name>
- est. LOC: <added + deleted, only when decomposition mode is disclosed>
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
phase boundaries after the fact. An over-threshold phase is rejected
here, by the Architect. A phase that measures over threshold at code
time halts the commit and returns to this plan with superseding
claims; nobody splits it at code time.

## Five rules (restated)

1. Blessed means immutable; commit before implementation.
2. Claim ids are append-only.
3. Coverage is bidirectional — `scripts/audit-plan` is the script.
4. The plan outlives the PBI; the Completion Record gains `## Plan`.
5. Preserve-vs-grow: list what must survive, from a verified record
   when one exists.

Audit red never costs an Architect token. Revise the plan.
