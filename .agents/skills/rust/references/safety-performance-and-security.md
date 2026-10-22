# Safety, performance, and security

unsafe, overflow, input trust, secrets. Unwrap lives in error-handling. Do not restate it.

## Rules

RS-01  Never use `unsafe` without documented safety invariants and a justification.
       check: RC-09 lints `unsafe_code`, `undocumented_unsafe_blocks`, `multiple_unsafe_ops_per_block`; a crate that needs unsafe carries a scoped `#[expect(unsafe_code, reason = "...")]`

RS-02  Minimize allocations: prefer `&str` / `Cow<'_, str>` over `String` when either works.

RS-03  Use `Vec::with_capacity` when the size is known up front.

RS-04  Prefer borrowing and channels over `Arc` / `Rc` / `Mutex` when either works.

RS-05  Prefer `RwLock` over `Mutex` for read-heavy cases.

RS-06  Never store secrets in source.

RS-07  Configuration comes from the environment or an approved crate. Never from literals in code.

RS-08  Never log passwords, tokens, or PII.

RS-09  Do not trust untrusted input past the parse edge.

## How

`unsafe` is a documented hole in the type system. No comment, no `unsafe`.

Performance is not an excuse to tangle layers. Borrow first. Share last.

Secrets in git are a breach, not a style miss. Env vars and approved secret crates are the door. Logs that print a bearer token are the same class of bug.

Input trust is the security face of parse-at-the-edge. Once a value is a domain type, the core does not re-check "did the user send SQL."
