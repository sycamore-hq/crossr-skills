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

RC-09  Encode the checkable rules as lints so the RC-02 clippy run in CI (`cargo clippy --all-targets -- -W clippy::pedantic -D warnings`) enforces them, not the reviewer (`cargo build` and `cargo test` do not run clippy lints). Every crate denies `print_stderr`, `dbg_macro` and `print_stdout` in both libraries and binaries: either in its own `[lints.clippy]` table, or in a workspace root `[workspace.lints.clippy]` table that each member inherits with `[lints] workspace = true`. A CLI's one output function gets a scoped `#[expect(clippy::print_stdout, reason = "...")]`; tests, examples and benches that print get a scoped `#[expect]` too, which keeps RC-07's production-path intent. CI also fails on any hit of RE-07's zero-hit `check:` grep; the RP-04 and RC-07 greps stay review checks because their allowed locations (parser impls, the one output function) always match.
       check: the RC-02 clippy run passes; RE-07's grep has 0 hits; every Cargo.toml (rg --files -g Cargo.toml) either lists print_stderr, dbg_macro and print_stdout as deny under its own [lints.clippy], or has `[lints] workspace = true` and the root [workspace.lints.clippy] lists all three as deny

## How

The checklist is the completion gate, not a suggestion. Pedantic clippy is on. `-D warnings` means a warning is a fail.

`#[allow(clippy::too_many_arguments)]` and `#[allow(clippy::too_many_lines)]` are the $100 / $100,000 shape without a dollar sign: the allow is the fine. Extract a config struct or a helper.

A new crate is a dependency the next human has to trust. Ask first.
