# Tooling

fmt, pedantic clippy, approved crates. Clippy fines live here.

## Rules

RC-01  `cargo fmt` is clean before any change is complete.
       check: cargo fmt --all --check

RC-02  `cargo clippy --all-targets -- -W clippy::pedantic -D warnings` is clean.
       check: cargo clippy --all-targets -- -W clippy::pedantic -D warnings

RC-03  Never add `#[allow(clippy::too_many_*)]`. Refactor instead.

RC-04  No wildcard imports except preludes or `use super::*` in tests.

RC-05  Import order: `std` → approved external crates → local modules.

RC-06  Prefer the standard library. A new third-party crate needs explicit user approval.

RC-07  No `dbg!`, `println!`, or commented-out code in production paths. Diagnostics go through `tracing` (exported with `tracing-opentelemetry` where OpenTelemetry is in use), never `eprintln!`. User-facing CLI output (results, `--help`) is the only exception.
       check: rg 'dbg!|println!|eprintln!' src/ → review each hit; only CLI output remains

RC-08  `cargo build` and `cargo test` run with zero warnings.

## How

The checklist is the completion gate, not a suggestion. Pedantic clippy is on. `-D warnings` means a warning is a fail.

`#[allow(clippy::too_many_arguments)]` and `#[allow(clippy::too_many_lines)]` are the $100 / $100,000 shape without a dollar sign: the allow is the fine. Extract a config struct or a helper.

A new crate is a dependency the next human has to trust. Ask first.
