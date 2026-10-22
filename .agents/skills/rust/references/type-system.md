# Type system and data

Newtypes as data. Option over sentinels. Immutable by default.

## Rules

RD-01  Use newtypes for semantically distinct values (`UserId(u64)` vs `OrderId(u64)`). Wire-originated strings are RP-01's case, not a second rule here. Do not implement `Deref` on a newtype to inherit the inner type's methods; only smart pointers implement `Deref` / `DerefMut`.

RD-02  Prefer `Option<T>` over sentinel values. A parameter that selects behaviour is an enum (`Mode::Strict`), not a `bool` or an `Option` used as a switch.

RD-03  Derive `Debug`, `Clone`, `PartialEq`, `Eq`, `Hash` where those traits are honest. Every public type implements `Debug`, and its output is never empty.
       check: RC-09 lint `missing_debug_implementations` (existence only; non-empty output stays a review check)

RD-04  `#[derive(Default)]` only when a truly sensible default exists.

RD-05  Treat data as immutable by default.

RD-06  Use a builder for complex construction with private fields (invariants enforced in `build()`).

RD-07  Conversions use the standard traits: `From` / `Into` when infallible, `TryFrom` / `FromStr` with a typed error when they can fail, `AsRef` / `AsMut` for cheap borrowed views. No ad-hoc `convert_x` functions.

## How

`UserId(u64)` and `OrderId(u64)` are different types. Mixing them is a compile error, not a review comment. Wire-originated strings (`Email`, …) are parsed at the edge under RP-01 / RP-02 — this topic owns newtypes-as-data, not the edge ban.

A `status: i32` where `0` means missing is a sentinel. Use `Option<Status>`. A `is_admin: bool` paired with `role: String` is a flag hiding an enum.

Default is a value the domain believes in. An empty `Config` that will panic on first use is not a default — it is a trap.

When a type has private fields and multi-step setup, expose a builder (or a single infallible/fallible constructor) so invalid states cannot be named. RF-03 still covers the over-five-parameters case; this rule covers the private-fields case even with fewer parameters.
