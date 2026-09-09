# AGENTS.md — Instructions for AI Coding Agents

This file contains the rules, conventions, and workflows that all AI coding agents **must** follow when working in this repository.

This repo is the **skills catalog**. Process law lives in [`sycamore-hq/crossr-harness`](https://github.com/sycamore-hq/crossr-harness) ([HARNESS-SPEC.md](https://github.com/sycamore-hq/crossr-harness/blob/main/HARNESS-SPEC.md)). Loop law (AVRIL / AXEL / BRICK conductor, GAN personas) lives in [`sycamore-hq/crossr-loops`](https://github.com/sycamore-hq/crossr-loops).

---

## Core Behavioral Rules

These rules are non-negotiable and derived from repeated observed failures across many codebases.

1. **Think before acting.** Explicitly state your understanding, assumptions, and any ambiguities. Ask clarifying questions instead of guessing.
2. **Be surgically precise.** Modify *only* the minimal code necessary to complete the requested task. Never refactor unrelated areas "while you're here."
3. **Minimal changes only.** Solve exactly what was asked. Do not add speculative features, future-proofing, or unrelated improvements.
4. **Define success upfront.** Before writing code, state the success criteria. Iterate until they are met. Do not stop early.
5. **Read before writing.** Review relevant files, callers, exports, and context first.
6. **Match existing conventions exactly.** Follow the style, patterns, and decisions already present in the codebase — even if you disagree with them.
7. **Tests must verify real intent.** Write tests that validate the actual business logic or behavior, not just that code exists or runs.
8. **Checkpoint after significant work.** After major steps, summarize what was done, what was verified, what remains, and any open questions.
9. **Fail loud and early.** Surface uncertainty, errors, limitations, or conflicts immediately. Never hide problems or guess.
10. **Respect token budgets and context.** Be concise. Summarize when appropriate. Restart context when needed rather than continuing with degraded performance.
11. **Use HTML for human-facing deliverables.** When producing specs, reports, reviews, dashboards, prototypes, or any artifact primarily for human consumption, prefer a self-contained HTML file (with Tailwind via CDN) over raw Markdown. HTML dramatically improves human comprehension and engagement. For the visual forms (shape-diff, trees, Mermaid, focused HTML), use `show-me`.
12. **Follow the stacked PR discipline.** All work must be delivered in small, reviewable PRs (< 10 minutes deep review). Use explicit traceability, plan mode, and the PETC loop.

---

## Project Commands

Always use the `justfile` for canonical commands:

- `just init` — Environment bootstrap
- `just check`
- `just test`
- `just clippy`
- `just fmt`
- `just harness-validate` — Catalog `docs-verify` + Claude skill drift check + `features.json` shape
- `just regen-agents` — Refresh loop persona copies from the `loops` pin, regenerate marked `.opencode/agent/` files, strip the GONE-listed overlay
- `just claude-skills-sync` — Regenerate the Claude compatibility copies in `~/.claude/skills` from `.agents/skills/`
- `just docs-verify` — Allowlist vs README vs `SKILL.md`
- `just packet-audit MODE FILE` — Mechanical packet/verdict audit (`brief` or `verdict`)

`./scripts/harness-bootstrap` and `./scripts/sync-skills` are shims: they print `deprecated: use sycamore-hq/crossr-harness` and exit 1. Status dashboard and OpenCode `/avril` `/axel` `/status` live in harness + loops.

Run the appropriate commands before declaring work complete.

---

## Project Structure & Key Files

- `.agents/skills/` — All reusable capabilities (agentskills.io format). All skills follow the canonical portable structure with proper Harness Relationship (Stratified) disclosure.
- `.agents/agents/` — Skill GAN personas owned here (`skill-evaluator-agent`, `skill-remediator-agent`, `skill-reviewer-agent`) plus runtime copies of loop personas from the `loops` pin (refresh on pin move; do not hand-edit copies). Code GAN, AVRIL/AXEL, and BRICK conductor personas are authored in `crossr-loops`.
- `docs/public-skills.json` — Public catalog SSOT. README table must match. No `moved-to` after split-07.
- `lockfile.toml` — Consumer pins: `skills = "v1-gan-layers"`, `loops = "v1-one-law-consumers"`. Not a third tracker. Graphs live in `crossr-loops/graphs/` and are in the `v1-one-law-consumers` pin. Topology only — if a graph and a conductor `SKILL.md` disagree, the skill wins.
- `.opencode/agent/` — generated from `.agents/agents/` at bootstrap when a persona source exists (GENERATED marker; do not hand-edit). `avril.md` is generated from `avril-conductor-agent`. `status.md` is the only hand-written entrypoint.
- `features.json` + `progress.md` — Machine + human tracking of work (phase → commits → features model).
- `scripts/sync-claude-skills` — Catalog compatibility copies. Canonical source is always `.agents/skills/<name>/` (the whole directory: `SKILL.md` plus `references/`).
- `scripts/verify-docs` — Catalog gate.

**Do not add** orchestration skills here: `avril`, `axel`, `brick` conductor, `rust-team-lead`, `orchestrator-prompt`, `dashboard-prompt`, `chief-of-staff`. BRICK *stage* skills still land here.

---

## HTML Output Guidance (Human Interface Layer)

For any deliverable intended for human review — specs, architecture documents, PR summaries, reports, dashboards, prototypes, deployment guides, etc. — **generate a self-contained HTML file** as the primary artifact.

- Use Tailwind CSS via CDN for styling.
- Make it beautiful, scannable, and interactive where helpful.
- This is dramatically more effective than Markdown for human consumption ("the unreasonable effectiveness of HTML").
- You may also produce a Markdown version for git or agent handoff, but HTML is the primary human-facing output.

Example filenames: `architecture-review.html`, `pr-summary.html`, `deploy-guide.html`.

---

## Git & PR Workflow

- Follow the stacked PR pattern described in harness `HARNESS-SPEC.md`.
- Every PR must be reviewable in < 10 minutes.
- Use Plan Mode: plans are concise and end with a list of unresolved questions.
- Commit messages and PR titles should reference the relevant feature/phase IDs.

---

## Boundaries & Safety

- **Never** make destructive changes without explicit confirmation.
- **Never** touch unrelated files or systems.
- **Always** run verification commands (`just docs-verify`, `just test`, `just clippy`, etc.) before claiming completion.
- Surface any policy, security, or architectural concern immediately.

## Claude Skill Copies

`.agents/skills/` is the single source of truth. The Claude compatibility copies under `~/.claude/skills` (or `CLAUDE_SKILLS_DIR`) are **generated, never hand-edited**.

- `just claude-skills-sync` regenerates them; `./scripts/sync-claude-skills --all` installs every repo skill, and named arguments add specific ones.
- Skills in the target that this repo does not own (personal or project-local) are never deleted or modified — they are reported and left alone.
- Replaced files are backed up to a timestamped `skills.backup-*` directory.
- `just harness-validate` reports drift without failing; run the sync to clear it.

## How to Work in This Repo

1. Read the relevant skill in `.agents/skills/`. Process questions: harness `HARNESS-SPEC.md`. Loop questions: `crossr-loops`.
2. Activate the appropriate catalog skills.
3. Use Plan Mode for any non-trivial task.
4. Produce HTML for human review artifacts when applicable.
5. Skill changes: run the skill GAN (`skill-evaluator-agent` → `skill-remediator-agent` → `skill-reviewer-agent`).
6. Deliver work in small, stacked, reviewable PRs.
7. Update `features.json` + `progress.md` as you go.
8. `just docs-verify` must PASS. README table == `docs/public-skills.json`.

**All agents must follow these rules.** Violations will be called out during review.

## Cursor Cloud

Agents started on this repo use `.cursor/environment.json` + `.cursor/Dockerfile`
(just, Python 3, jq, Rust; pinned versions are the `ARG`s at the top of the Dockerfile). That file wins over a personal or team
dashboard environment. After checkout, `install` runs `.cursor/install.sh`
(`just init`). Canonical commands stay under Project Commands.
