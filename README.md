# crossr-skills

**Where the Cross meets clean code.**

Portable agent skills. Load them in Claude, Cursor, or Grok without buying CrossR process.

> Forged in the Cross. Built for craft.

---

## What is this?

A curated collection of **Agent Skills** (`.agents/skills/`). The skills strictly follow the [agentskills.io](https://agentskills.io) specification.

Process, loops, and the public site live in sibling remotes under [sycamore-hq](https://github.com/sycamore-hq):

| After cut | What |
|-----------|------|
| **this repo** | Capability skills, BRICK stages, `agent-harness`, `skill-evaluator`, `sync-claude-skills` |
| [crossr-loops](https://github.com/sycamore-hq/crossr-loops) | `avril`, `axel`, `brick` conductor, `orchestrator-prompt`, loop personas, `/avril` `/axel` bodies, `code-gan` |
| [crossr-harness](https://github.com/sycamore-hq/crossr-harness) | HARNESS-SPEC, bootstrap, dashboard, `dashboard-prompt`, `chief-of-staff`, `/status` |
| [crossr-web-landing](https://github.com/sycamore-hq/crossr-web-landing) | Public site. Links out. Owns no law. |

Last tree that still contained everything: [`v0-last-monolith`](https://github.com/sycamore-hq/crossr-skills/releases/tag/v0-last-monolith). Current pins: `skills = "v1-gan-layers"`, `loops = "v1-packets-consumers"` ([lockfile.toml](lockfile.toml)).

**Split complete (split-09 graphs).** Topology lives in [crossr-loops `graphs/`](https://github.com/sycamore-hq/crossr-loops/tree/main/graphs) and is in the `v1-packets-consumers` pin. SKILL.md stays the law. Plan: [`docs/plans/skills-loops-harness-split.html`](docs/plans/skills-loops-harness-split.html) ([markdown](docs/plans/skills-loops-harness-split.md)).

The public door is [`crossr-web-landing`](https://github.com/sycamore-hq/crossr-web-landing) → https://sycamore-hq.github.io/crossr-web-landing/ . This repo's Pages host is a **moved stub**, not the catalog UI.

**Freeze:** do not add new orchestration skills here (conductors, `orchestrator-prompt`, `dashboard-prompt`, `chief-of-staff`). Writers, reviewers, testers, architects, domain skills, writing skills, `skill-evaluator`, and BRICK *stage* skills still land here.

New projects: bootstrap from [sycamore-hq/crossr-harness](https://github.com/sycamore-hq/crossr-harness). `.opencode/agent/` files with a persona source are generated (do not hand-edit); `avril.md` is generated from `avril-conductor-agent`; `status.md` stays hand-written. A target that still has an unmarked `avril.md` must delete it by hand before regen (never-overwrite). The old `./scripts/harness-bootstrap` and `./scripts/sync-skills` are shims — they print `deprecated: use sycamore-hq/crossr-harness` and exit 1.

---

## Skills

All skills are designed with the same standards applied to production Rust code: functional purity, stratified design, zero technical debt, and handover-clean artifacts.

Public catalog SSOT: [`docs/public-skills.json`](docs/public-skills.json) (22 skills). Names below must match that file.

| Skill                  | Purpose                                              | Category      |
|------------------------|------------------------------------------------------|---------------|
| `code-writer`          | Core coding philosophy (Grokking Simplicity + SICP) | Foundation    |
| `plan-writer`          | Plan-time generator: typed claims, bidirectional AC coverage | Foundation |
| `rust`                 | Rust language book: situational Rules + How, generated RULES.md | Rust Book |
| `ocaml`                | OCaml language book: situational Rules + How, generated RULES.md | OCaml Book |
| `code-review`          | Ruthless code quality guardian                       | Quality       |
| `testing`              | Obsessive test coverage and error-path verification  | Quality       |
| `architecture`         | System-level architecture gate: stratification, layers, 2-year maintainability | Architecture  |
| `brick-specifier`       | BRICK stage 1 — approved tasks to pruned Gherkin | Orchestration |
| `brick-coder`          | BRICK stage 2 — Gherkin to red tests then green code | Orchestration |
| `brick-refactorer`     | BRICK stage 3 — complexity, duplication, property tests | Orchestration |
| `brick-mutator`        | BRICK stage 4 — mutation testing gate, zero survivors | Orchestration |
| `rust-axum-backend`    | Clean layered Axum HTTP APIs with policy gates       | Backend       |
| `rust-frontend`        | Leptos + WASM + Polars with anti-slop guidance       | Frontend      |
| `rust-tui`             | ratatui Component + Action + two-phase dispatch      | TUI           |
| `agent-harness`        | Full harness process (stacked PRs, GAN, HTML-first)  | Harness       |
| `skill-evaluator`      | Audit and remediate agent skills against CrossR standards | Meta     |
| `voice-dna`            | CrossR sharp-human writing voice with full unslop pattern list | Writing       |
| `unslop`               | Voice-agnostic pass that strips AI tells from prose  | Writing       |
| `show-me`              | Compact visuals for PRs, plans, and architecture plans | Writing     |
| `gan-verdict`          | GAN verdict tokens and report envelope schema        | Protocol      |
| `github-pr-review`     | Structured inline PR review: severity grammar, clusters, Done-when conditions | Quality       |
| `github-pr-fix`        | Apply PR review threads, push to the PR head, reply and resolve only what holds | Quality       |

**Not in the public catalog:** `obsidian-cli`, `diataxis` (deferred), empty `diataxis-*` stubs — see `out` in `docs/public-skills.json`.

---

## Core Philosophy

> “Write code that is layered, modular, and built from pure calculations operating on immutable data; isolate all actions; prefer the language’s standard library; use abstraction and higher-order functions to control complexity so that any human reader can understand and safely modify the system.”

This mindset applies to every skill.

---

## Principles

- **No garbage** — Every skill is reviewed by `code-review`, `testing`, and `architecture`.
- **Small and focused** — One skill = one clear responsibility.
- **Self-verifying** — Skills contain their own usage rules and activation statements.
- **Portable** — A catalog skill loads without CrossR process. Process lives in [crossr-harness](https://github.com/sycamore-hq/crossr-harness). Loops live in [crossr-loops](https://github.com/sycamore-hq/crossr-loops).

---

## Contributing

Contributions are welcome, especially new high-quality skills that follow the same standards.

Process for this repo: [HARNESS-SPEC.md](https://github.com/sycamore-hq/crossr-harness/blob/main/HARNESS-SPEC.md) in `crossr-harness`. Stacked PRs, < 10 min deep review.

---

## License

MIT — use freely, improve boldly, give credit where it’s due.

---

## About

Maintained by **Nathan Sculli** (@scull7)  
Christian • Father • Functionally Obsessed

> “Whatever you do, work at it with all your heart, as working for the Lord.” — Colossians 3:23
