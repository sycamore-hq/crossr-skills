---
name: system-design
description: |
  Cross-cutting system-design book. Load when making an architectural decision or plan: data model and phase order, removing complexity, repeated failed fixes, trust boundaries, shared mutable state, idempotent effects. Card routes to situational references. Plan generator loads this card + RULES.md + the references for the situation; the architecture gate loads RULES.md only; execute, review, and test agents do not load it.
  Fully portable across agentskills.io environments and models. At plan time it pairs with `plan-writer`, which does not load `code-writer`; outside the plan loop, activate it with `code-writer`.
metadata:
  book: "true"
  scope: "cross-cutting"
---

# System Design Book

At plan time, load with `plan-writer` (which does not load `code-writer`). Outside the plan loop, load `code-writer` first. This card says which reference applies. It is not the law.

`code-writer` owns the function-level half of these ideas. This book owns the plan-level half: what to build first, what to take out, when to stop patching, where trust changes, who may write shared state, and how effects survive a rerun.

## When to load which reference

| Situation | Load |
|---|---|
| Ordering phases; settling types, schemas, wire shapes, state ownership | `references/foundations.md` |
| A second fix on the same premise failed the same gate; a requirement the old design never anticipated | `references/premise.md` |
| Any plan that adds a component, layer, dependency, flag, path, or state | `references/subtraction.md` |
| Where outside data enters; layers and adapters; who owns an invariant | `references/boundaries.md` |
| Two or more actors that may write the same state | `references/shared-state.md` |
| Any Action that changes externally observable state | `references/idempotency.md` |
| Every plan: declaring which topics apply | `references/applicability.md` |

Plan generator: this card + the reference for the situation (Rules + How).
Adversaries: `RULES.md` only. Never `references/`.
Execute generator, reviewer, tester: not loaded. `code-writer` carries the overlap.

Contract refs (not topics; extractor skips them): `references/specialization.md`, `references/verification.md`.

## Topic prefixes

Registry: `docs/book-topics.md`. This book mints `D*` prefixes: `DF` foundations, `DP` premise, `DS` subtraction, `DB` boundaries, `DX` shared state, `DI` idempotency, `DA` applicability.

## One-Sentence Mandate (Memorize This)

> Load the system-design book when deciding structure, with `plan-writer` at plan time and `code-writer` otherwise; apply the reference that matches the decision; adversaries read RULES.md only.

**When using this skill**: Combine it with `plan-writer` at plan time, `code-writer` otherwise. Pick the reference that matches the decision. Do not load every reference.

**Activation Statement**
> Using `plan-writer` + `system-design` for this architectural plan.
