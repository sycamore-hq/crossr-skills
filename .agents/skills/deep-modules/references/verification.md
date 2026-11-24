# Verification

In a fresh activation the following behaviors are directly observable and scorable:

- The agent recites the deep-modules One-Sentence Mandate before planning or reviewing structure.
- The plan's applicability section declares `MD` as `applies` or `n/a — <reason>`.
- When a change adds files or directories, the agent runs `scripts/check-structure` (with the project's baseline when one exists) and reports the result.
- Each finding the agent fixes comes with a before-and-after structure picture and names the layer decision behind it.
- The agent loads only the references that match the situation, and never feeds How to an adversary.

## Gate interpretation

| Condition | Verdict |
|---|---|
| Sibling modules that use each other in a circle | REJECT |
| Types or functions in a loop across modules, or more than seven in one loop | REJECT |
| Outside code mutating, indexing or calling methods on a guarded field, directly or via accessor | REJECT |
| Outside code only reading a plain value from a field | BLESS |
| A crate or parent module that shows more than seven functions and at least as many as it hides | REJECT |
| A new file over the line limit or a directory over the entry limit, not in the baseline | REJECT |
| A finding silenced by a re-export, accessor, rename or file split with no layer decision | REJECT |
| A new baseline entry with no reason in the change description | REJECT |
| A baseline entry deleted because its finding was fixed | BLESS |

Violations against any of these during fresh activation mean the book was not followed.
