# Subtraction

Take complexity out before you add anything.

## Rules

DS-01  Before adding any component, layer, dependency, configuration flag, code path, or mutable state, the plan runs a subtraction pass over the affected scope and lists what can be deleted, consolidated, or eliminated. An explicit empty list with a reason is valid; an omitted pass is not. If net architectural complexity still increases, the plan says why subtraction alone cannot meet the requirement.

DS-02  Identified removals precede the additions that depend on them, as a separately verifiable phase, and the plan shows the additions build on the simplified design. Ordering follows `foundations.md`.

## How

The affected scope is the components the change modifies plus the dependencies, interfaces, and state whose complexity it alters. It is not the whole system. A subtraction pass is not a license for unrelated refactoring.

"Separately verifiable" does not mean a separate deploy. When removing an old interface before its replacement would leave an unsafe intermediate state, remove and replace atomically. The removal still gets its own claim.

Measure net architectural complexity, not item count. Deleting three functions while adding a distributed coordinator is a net increase.

Cut before you polish. Design for observed usage, not speculative edge cases. Add no validators, parsers, or guards beyond what the spec demands. Delete a reference with no novel content rather than leaving a stub.

The function-level rule, delete or collapse first, lives in `code-writer`.
