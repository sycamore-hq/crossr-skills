# Error handling

SOLE OWNER of unwrap. Other topics do not restate it.

## Rules

RE-01  Every layer defines its own error enum via thiserror. Never `anyhow`.
       check: RC-09 lint `disallowed_types` (clippy.toml bans `anyhow::Error` / `anyhow::Result`)

RE-02  Cross-layer propagation uses `#[from]` / `From`; never inline `.map_err` at a call site — a call-site `.map_err` means a `From` impl is missing, add the impl.
       check: rg '\.map_err\(' --glob '*.rs' → review each hit

RE-03  Never `.unwrap()` in production paths.
       check: RC-09 lint `unwrap_used` (clippy.toml `allow-unwrap-in-tests = true`)

RE-04  `.expect()` only for documented invariants, with an explanatory comment.
       check: RC-09 lint `expect_used`; each allowed use carries a scoped `#[expect(clippy::expect_used, reason = "...")]` naming the invariant

RE-05  Fallible operations return `Result<T, E>`. Propagate with `?`.

RE-06  The public API boundary converts domain errors into the gateway type via `From`.

RE-07  No string-payload errors: no `Result<_, String>`, no catch-all `Invalid(String)` / `Other(String)` variant filled with `format!`. One variant per failure; the data goes in fields, the wording in `#[error(...)]`.
       check: rg 'Result<[^>]*, String>|Invalid\(format!|Invalid\(String\)' --glob '*.rs' → 0

## How

One enum per layer. Conversions live on the type, once.

```rust
#[derive(thiserror::Error, Debug)]
pub enum QueryError {
    #[error("row not found")]
    NotFound,
    #[error(transparent)]
    Sql(#[from] rusqlite::Error),
}

#[derive(thiserror::Error, Debug)]
pub enum GatewayError {
    #[error("query failed: {0}")]
    Query(#[from] QueryError),
}

fn get_user(id: u64) -> Result<User, GatewayError> {
    let row = repo.find(id)?; // QueryError → GatewayError via From
    Ok(row.into())
}
```

Bad — the same mapping, pasted:

```rust
repo.find(id).map_err(|e| GatewayError::Query(e.into()))?;
```

`anyhow` is forbidden. Inline wrapping is a design smell, not a style preference.
