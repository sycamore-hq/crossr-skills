# Dependencies

Modules read in an order. Things that know each other in a loop have to be learned together.

## Rules

MD-01  No module cycles. Sibling modules under one parent never use each other, directly or through other siblings, in a circle. A module using its own children, or a child using its ancestors, is not a cycle; crates and packages are already ordered by the build tool.

MD-02  No tangles. Types or functions that use each other in a circle live in one module, and there are at most seven of them. A loop that crosses modules, or one too big to hold in mind, is broken by moving the shared decision up a layer.

## How

Build the "uses" graph for one parent at a time: an edge from sibling A to sibling B when code inside A names anything defined inside B. Any strongly connected group of two or more siblings is an `MD-01` finding. Draw it before fixing it.

The fix is a layering decision, not a file move. Ask which sibling is lower level. Usually one of them only needs a constant, a type, or a small helper that the other owns; move that piece down into the lower module (or a new, lower sibling) and the circle opens. Re-exporting the item from the parent, or moving it to a third module that both still import, keeps the cycle in spirit and fails review.

A tangle (`MD-02`) is the same problem at the level of types and functions: `Tasks` calls `Timers`, and `Timers` calls back into `Tasks`. Moving an `impl` block or a file does not change it, because the loop is in who calls whom. Break it by giving the decision that needs both to their common caller: a `tick` in the parent that asks timers what is due and then wakes the tasks, so neither knows the other.

Seven is the count a reader can hold at once. A loop of three types in one module is fine to read together; a loop of ten is not, even in one file.

Test-only code is out of scope: test helpers that reach across siblings are not cycles.
