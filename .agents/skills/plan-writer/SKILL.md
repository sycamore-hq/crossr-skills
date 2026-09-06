---
name: plan-writer
description: |
  Plan-time generator card. Emits a typed, bidirectionally-covered
  implementation plan before any code exists. Language-neutral.
  Never loads code-writer. A skill, not a persona.
---

# Plan Writer

**You write the implementation plan. You do not write code.**

Load this card + the disclosed book's Rules + the PBI.
Do not load `code-writer`. That law is for diffs.

## Taxonomy

mechanical (command → expect) · observable (`file:line`) · judgment (LLM).
Judgment ≤ 30% of active claims. Ids `C-01` are append-only.
`references/taxonomy.md`.

## Artifact

`docs/plans/pbi/<id>.plan.md` or `<backlog>/plans/<id>.plan.md`.
Never `.pinto/tasks/`. `references/artifact.md`.

Required: Phases (the decomposition), Acceptance Criteria, Claims
(`C-01: <type> · AC-01 · text`), Preserve, Unresolved questions.

`scripts/audit-plan` runs before the Architect. Red = no LLM.

## Five rules

1. Blessed means immutable. Commit the plan before implementation.
2. Claim ids are append-only. Supersede; never delete or renumber.
3. Coverage is bidirectional (a script). Every AC ↔ ≥1 claim.
4. The plan outlives the PBI. Completion Record names path + verdicts.
5. Preserve-vs-grow. Every increment lists functionality that must survive,
   sourced from a prior evidence packet when one exists. Gaps and
   preservation become claims. Scope change returns to AVRIL.

## Evidence packet

When a prior evidence packet exists, load it
(`references/evidence-packet.md`). Gaps and preservation become claims.

## Stop

Blocking question → stop. Audit red → revise; do not call the Architect.

## Verification

- Typed claims, bidirectional AC coverage, no code.
- Judgment ≤ 30%. Mechanical claims carry `→`.
- Does not load `code-writer`. Loads a prior evidence packet when present.

## Specialization

Plan-time generator card (precondition: a blessed PBI). Owns taxonomy,
five rules, and phase decomposition. Not a persona. Architect blesses.

**One-Sentence Mandate**
> Write a typed, bidirectionally-covered implementation plan whose claims an architect can reject for underspecification and a reviewer can later verify — before any code exists.
