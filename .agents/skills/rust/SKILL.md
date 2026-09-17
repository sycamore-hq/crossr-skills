---
name: rust
description: |
  Rust language book. Card routes to situational references. Generator loads How + Rules for the situation; adversaries load the generated RULES.md only.
  Fully portable across agentskills.io environments and models. Always activate together with `code-writer`.
metadata:
  book: "true"
---

# Rust Book

Load `code-writer` first. This card says which reference applies. It is not the law.

Anti-Pattern Severity / Fines live in `code-writer`. Do not photocopy them here.

## When to load which reference

| Situation | Load |
|---|---|
| Fallible ops, thiserror, unwrap, From | `references/error-handling.md` |
| Wire → domain at the adapter edge | `references/input-parsing.md` |
| Newtypes-as-data, Option, Default | `references/type-system.md` |
| Layers, actions / calculations / data | `references/layering.md` |
| Combinators, nesting, exhaustive match | `references/control-flow.md` |
| Tests, AAA, `cfg(test)` | `references/testing.md` |
| `pub` items, docs, semver | `references/api-surface.md` |
| fmt, clippy, crates, imports | `references/tooling.md` |
| unsafe, overflow, secrets, input trust | `references/safety-performance-and-security.md` |
| Tokio workers, `spawn_blocking`, schedule latency, locks that park a worker | `references/tokio-runtime.md` |

Generator: this card + the reference for the situation (Rules + How).
Adversaries: `RULES.md` only. Never `references/`.
Test verifier: rules tagged `test` in `RULES.md`.

Contract refs (not topics; extractor skips them): `references/specialization.md`, `references/verification.md`.

## Topic prefixes

Registry: `docs/book-topics.md` (baseline, not a closed set). A later book may mint a prefix the registry does not list. The extractor accepts unknown prefixes. This book mints `RY` (tokio-runtime).

## One-Sentence Mandate (Memorize This)

> Load the rust book with `code-writer`; apply the reference that matches the situation; adversaries read RULES.md only.

**When using this skill**: Always combine it with `code-writer`. Pick the reference that matches the work. Do not load every reference.

**Activation Statement**
> Using `code-writer` + `rust` for this Rust work.
