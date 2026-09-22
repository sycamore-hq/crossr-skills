# Layering

One level of abstraction per function. Actions at the edges.

## Rules

RL-01  Every function operates at one consistent level of abstraction.

RL-02  Calculations are pure. Actions sit at the edges. Data is immutable.

RL-03  Higher layers compose lower ones. The call graph must be obvious.

RL-04  An error type stays in its layer. Crossing a boundary is a `From` conversion, not a mix-in.

RL-05  A calculation about one type lives in `impl Type` when Self is monomorphic and the fn does not need late-bound lifetimes. Leave it free only when the impl would inherit unused generics or lifetimes, or a `for<'a> fn(...)` pointer is required.

## How

A handler that parses, queries SQL, and formats HTML is three layers pretending to be one. Split it.

Calculations take data and return data. They do not touch the clock, the disk, or a socket. Actions do, and they call calculations — never the other way around.

`code-writer` already owns this split. This topic is the Rust shape of it: structs and enums as data; calculations as inherent methods or associated fns on that data when RL-05 applies; adapters as action. Purity does not require a module-level `fn`. `fn volume(&self) -> f64` on `Rect` is still a calculation.

A pile of `parse_foo` / `render_foo` / `foo_from_bar` that all take `&Foo` is a navigation defect. Put them on `Foo` — method if they operate on an instance, associated fn if they construct or do not need `self`.

That move is free for a monomorphic type: same FnAbi, same body, different symbol. Keep the function free when the only home is `impl<T> Foo<T>` and the fn does not use `T`, when the impl header would early-bind a lifetime the caller needs late-bound, or when the fn is a combinator over several types with no owner.

Do not invent a dummy unit struct just to namespace helpers. Attach to the type that already exists.
