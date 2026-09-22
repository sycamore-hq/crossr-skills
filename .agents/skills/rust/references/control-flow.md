# Control flow

Flat combinators first. Nesting is a smell.

## Rules

RF-01  Prefer combinators + `?`, then early returns / guards, then small private helpers.

RF-02  Nesting deeper than 3–4 levels is forbidden.

RF-03  Max 5 parameters per function; use a builder or config struct beyond that.

RF-04  Prefer borrowing (`&T`, `&mut T`) over ownership when either works.

RF-05  Match exhaustively. A `_` arm that hides a real case is a defect.

RF-06  Single responsibility per function and type.

## How

Priority is strict:

1. `map` / `and_then` / `or_else` / `inspect` / `transpose` + `?`
2. Guard clauses that return early
3. A helper with a name that states the case

Arrow code, triple-nested loops, and `match` inside `if let` inside `for` fail this topic. Extract until the happy path reads left-to-right.

If a chain needs a type conversion, put it in a `From` impl and use `?` — do not leave a `.map_err` at the call site (RE-02).

A helper extracted under RF-01 is an inherent fn on the type it is about when RL-05 applies. Do not leave a cluster of private module-level fns that all take the same `&T`.
