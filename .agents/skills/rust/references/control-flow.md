# Control flow

Flat combinators first. Nesting is a smell.

## Rules

RF-01  Prefer combinators + `?`, then early returns / guards, then small private helpers.

RF-02  Nesting deeper than 3–4 levels is forbidden.

RF-03  Max 5 parameters per function; use a builder or config struct beyond that.

RF-04  Prefer borrowing (`&T`, `&mut T`) over ownership when either works.

RF-05  Match exhaustively. A `_` arm that hides a real case is a defect.

RF-06  Single responsibility per function and type.

RF-07  A function that validates or compiles several things reads as a list of named steps (`check_*`, `compile_*`), one per concern. No inline run of `for … { if … { return Err(…) } }` blocks.
       check: review any fn with more than two `return Err(` — each should be its own named step

RF-08  If most of a function body sits inside one `if` / `if let`, invert the condition into a guard that returns early. The happy path stays at the left margin.
       check: review any fn whose body is a single `if` block followed by a trailing return value

RF-09  Parsing arguments and acting on them are separate steps. `main` (or the command entry point) parses argv/config into a typed command value (an enum or struct, failing with a typed error), then hands that value to a function that does the work. Action functions never read argv, env, or raw strings; parsing functions never do I/O beyond reading their input.
       check: rg 'env::(args|args_os|var|var_os|vars|vars_os)\b|use std::env::|::(try_)?parse(_from)?\(|\.parse(::<[^>]+>)?\(' src/ → each hit sits in the entry point, not in an action function (best-effort grep; review covers aliased imports)

## How

Priority is strict:

1. `map` / `and_then` / `or_else` / `inspect` / `transpose` + `?`
2. Guard clauses that return early
3. A helper with a name that states the case

Arrow code, triple-nested loops, and `match` inside `if let` inside `for` fail this topic. Extract until the happy path reads left-to-right.

If a chain needs a type conversion, put it in a `From` impl and use `?` — do not leave a `.map_err` at the call site (RE-02).

### Validation and compile functions (RF-07)

A "compile the config" function is where arrow code grows fastest: one loop per field, an `if` per rule, an error built inline. The reader has to hold every rule in their head to find the happy path. Write the top-level function as the table of contents and push each rule into a helper whose name is the rule:

```rust
fn compile(raw: RawPolicy) -> Result<Policy, PolicyError> {
    check_stale_after(raw.stale_after_hours)?;
    check_tiers(&raw.tiers)?;
    let labor = compile_labor(raw.labor)?;
    let rules = ModelRules::compile(raw.model_rules, &raw.tiers, &labor)?;
    Ok(Policy { labor, rules, /* … */ })
}

fn check_drafts(&self, tiers: &BTreeMap<String, Tier>) -> Result<(), PolicyError> {
    let Some(drafts) = &self.drafts else {
        return Ok(());
    };
    if tiers.contains_key(&drafts.tier) {
        return Ok(());
    }
    Err(PolicyError::UnknownDraftTier(drafts.tier.clone()))
}
```

Each helper has one concern, guards first, and returns a typed variant (RE-07). Keep doc comments attached to the item they describe; a comment left above the wrong function after a move costs the reader more than no comment.

A helper extracted under RF-01 is an inherent fn on the type it is about when RL-05 applies. Do not leave a cluster of private module-level fns that all take the same `&T`.
