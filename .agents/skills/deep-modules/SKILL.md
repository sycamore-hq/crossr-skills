---
name: deep-modules
description: |
  Cross-cutting structure book: deep modules behind narrow interfaces. Load when deciding where code lives or reviewing a change that adds modules, types, fields, public functions, files or directories: dependency cycles between modules, things that know each other in a loop, fields worked on from outside their type, modules that show as much as they hide, directories too wide to scan, files too long to navigate. Card routes to situational references. Plan generator loads this card + RULES.md + the references for the situation; the architecture and code-review gates load RULES.md only.
  Language-neutral and fully portable across agentskills.io environments and models. Pairs with `code-writer`; the `rust` and `ocaml` books supply the idioms. Not a prose skill: for AI tells in writing use `unslop`; for comment cleanup see `code-writer`.
metadata:
  book: "true"
  scope: "cross-cutting"
---

# Deep Modules Book

A module earns its place by what it hides. Its interface is the price a reader pays to use it; what stays behind that interface is what they get for free. When the two are about equal, the module is overhead. When modules reach into each other, nobody can read one without the others.

This book turns that idea into six structural rules and one repair rule. `code-writer` owns function-level shape (purity, layering, naming). This book owns the shape between modules and types: who depends on whom, who touches whose data, and how much each one asks a reader to learn.

## When to load which reference

| Situation | Load |
|---|---|
| Adding a `use`/`open`, an import, or a call into a sibling module; two types that call each other | `references/dependencies.md` |
| Adding a field, a getter or setter, or a public function; code outside a type reaching into its data | `references/interfaces.md` |
| Adding a file or directory; a file or directory that keeps growing | `references/layout.md` |
| Fixing any finding above, or adopting these rules in a codebase that already breaks them | `references/repair.md` |

Plan generator: this card + `RULES.md` + the reference for the situation (Rules + How).
Adversaries: `RULES.md` only. Never `references/`.

## Mechanical checks

- `scripts/check-structure [ROOT]` checks `MD-05` and `MD-06` from file listings alone. Standard library Python 3.10+, no install. `--baseline FILE` mutes recorded findings so only new ones fail; `--write-baseline FILE` records today's.
- `MD-01` to `MD-04` need a symbol index. They are judgment rules for the gates in this release. For Rust, the upstream linter credited below checks all four mechanically; adopting it is a third-party dependency and is **pending approval**, so nothing here requires it.

## One-Sentence Mandate (Memorize This)

> "Hide more than you show: no module cycles, no loops between things, no fields worked on from outside, no interface as wide as its insides, and fix structure from first principles rather than by moving code until the check goes quiet."

---

**Attribution**: The six smells and the allowlist ratchet were inspired by [deslop-please](https://github.com/deterministic-machines/deslop-please) by Deterministic Machines, Inc. (MIT License), which in turn follows John Ousterhout's *A Philosophy of Software Design*. This book and its script are an independent CrossR implementation; no upstream code or text is copied.

**Activation Statement**
> Using `deep-modules` to keep module boundaries deep and interfaces narrow.
