# API surface

`pub` is a contract. Keep it small. Document it.

## Rules

RA-01  Every public item is documented in the Rust rustdoc style.

RA-02  Keep the public surface small. `pub` is a promise, not a default. A public struct keeps its fields private unless it is plain data with no invariants; callers go through constructors and methods.

RA-03  A breaking change to a `pub` item is a major version.

RA-04  Names follow Rust convention. Conversions: `as_` is free and borrowed, `to_` is costly or borrowed-to-owned, `into_` consumes self. Getters are `field()` / `field_mut()`, never `get_field()`. Constructors are inherent `new` / `with_*` / `from_*`. Iterator methods are `iter` / `iter_mut` / `into_iter`. Error types name the failed action, verb first: `ParseConfigError`, not `ConfigParseError`.

RA-05  Public fallible, panicking or unsafe functions document it under `# Errors`, `# Panics` and `# Safety`. Doc examples propagate with `?`, never `.unwrap()`.
       check: RC-02 pedantic lints `missing_errors_doc`, `missing_panics_doc` and default lint `missing_safety_doc`

## How

If a helper is only used inside the crate, it is not `pub`. If a type is `pub`, its documented invariants are the API.

rustdoc on every public item is the minimum. Examples belong on the functions callers will actually invoke.

Semver is mechanical once the surface is honest. Hidden `pub` leakage is how minors become majors.
