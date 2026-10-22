# Tooling

fmt, pedantic clippy, approved crates. Clippy fines live here.

## Rules

RC-01  `cargo fmt` is clean before any change is complete.
       check: cargo fmt --all --check

RC-02  `cargo clippy --all-targets -- -W clippy::pedantic -D warnings` is clean.
       check: cargo clippy --all-targets -- -W clippy::pedantic -D warnings

RC-03  Never suppress `clippy::too_many_*`, `cognitive_complexity` or `excessive_nesting` with `#[allow]` or `#[expect]`. Refactor instead.

RC-04  No wildcard imports except preludes or `use super::*` in tests.

RC-05  Import order: `std` → approved external crates → local modules.

RC-06  Prefer the standard library. A new third-party crate needs explicit user approval.

RC-07  No `dbg!`, `println!`, or commented-out code in production paths. Diagnostics go through `tracing` (exported with `tracing-opentelemetry` where OpenTelemetry is in use), never `eprintln!`. User-facing CLI output (results, `--help`) is the only exception.
       check: RC-09 lints `print_stdout`, `print_stderr`, `dbg_macro`, `use_debug`; commented-out code stays a review check

RC-08  `cargo build` and `cargo test` run with zero warnings.

RC-09  Encode the checkable rules as lints so the RC-02 clippy run in CI (`cargo clippy --all-targets -- -W clippy::pedantic -D warnings`) enforces them, not the reviewer (`cargo build` and `cargo test` do not run clippy lints). Lint levels live only in `Cargo.toml`: the workspace root has `[workspace.lints.rust]` and `[workspace.lints.clippy]` copied from `templates/Cargo.lints.toml`, and every package has `[lints] workspace = true` (a single-crate repo adds an empty `[workspace]` table). `clippy.toml` holds configuration only (`templates/clippy.toml`); a `[lints]` table there is silently ignored. Required at deny: rustc `missing_docs`, `unreachable_pub`, `unsafe_code`; clippy `print_stdout`, `print_stderr`, `dbg_macro`, `use_debug`, `unwrap_used`, `expect_used`, `panic`, `todo`, `unimplemented`, `unwrap_in_result`, `map_err_ignore`, `error_impl_error`, `disallowed_types`, `disallowed_methods`, `wildcard_enum_match_arm`, `undocumented_unsafe_blocks`, `multiple_unsafe_ops_per_block`, `tests_outside_test_module`, `allow_attributes`, `allow_attributes_without_reason`, `rc_mutex`, `mutex_atomic`, `clone_on_ref_ptr`, `cognitive_complexity`, `excessive_nesting`, `too_many_arguments`, `too_many_lines`. Required at warn (gated by `-D warnings`): `pedantic` and the nursery lints `redundant_clone`, `needless_pass_by_ref_mut`, `option_if_let_else`, `derive_partial_eq_without_eq`. An allowed exception is a scoped `#[expect(lint, reason = "...")]`, never `#[allow]`. CI also fails on any hit of RE-07's zero-hit `check:` grep; the RP-04 and RE-02 greps stay review checks.
       check: python3 <rust skill>/scripts/check-lint-setup <repo> exits 0, then the RC-02 clippy run passes

## How

The checklist is the completion gate, not a suggestion. Pedantic clippy is on. `-D warnings` means a warning is a fail.

`#[allow(clippy::too_many_arguments)]` and `#[allow(clippy::too_many_lines)]` are the $100 / $100,000 shape without a dollar sign: the allow is the fine. Extract a config struct or a helper.

A new crate is a dependency the next human has to trust. Ask first.

### Setting up clippy (RC-09)

1. Copy `templates/Cargo.lints.toml` into the workspace root `Cargo.toml`. A single-crate repo adds an empty `[workspace]` table above its `[package]`.
2. Add `[lints]` / `workspace = true` to every package `Cargo.toml`.
3. Copy `templates/clippy.toml` to the repo root. Thresholds: nesting 4 (RF-02), arguments 5 (RF-03), cognitive complexity 15 and function length 60 lines. 15 and 60 are this book's chosen defaults, not clippy's; the template marks them so. Tests may unwrap, expect, print and `dbg!`.
4. The only place that reads `std::env` is the entry point (RF-09), under one scoped `#[expect(clippy::disallowed_methods, reason = "entry point parses config")]`. The one CLI output function carries `#[expect(clippy::print_stdout, reason = "...")]`.
5. Prove it: run `python3 <rust skill>/scripts/check-lint-setup .`, then `cargo clippy --all-targets -- -W clippy::pedantic -D warnings`. Do not edit the checker's required lists to make it pass.
