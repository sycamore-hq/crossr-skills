---
name: agent-harness
description: |
  Specialized skill for designing and bootstrapping **effective harnesses** for
  long-running AI agents.
  Combines Anthropic's long-running agent scaffolding, AIHero's
  Plan-Execute-Test-Commit loop, and Revfactory Harness patterns.
  Use this skill whenever you need agents to maintain state, make incremental
  progress, and leave production-ready code across multiple sessions.
  Harness-layer skill with clean stratified disclosure. Fully portable across agentskills.io environments and models when paired with a compatible harness. Always activate together with `code-writer` + the disclosed book (and domain skills the harness discloses).
---

# Agent Harness Skill

**This skill extends `code-writer`.** (Layer on the disclosed book + relevant domain skills when a language book is disclosed.)  
You **MUST** apply the core coding philosophy first, then layer on these harness-specific rules for any project using a compatible harness.

**Primary reference:** Reference the harness specification disclosed at activation via the invoking harness (typically through its root rules file and equivalent spec artifact). This skill is the practical implementation guide.

## Purpose

A **harness** is the persistent scaffolding that turns stateless AI sessions into reliable, multi-session agents. It guarantees:

- State continuity across context resets
- Incremental, verifiable progress (one small task per session)
- Clean, merge-ready handovers
- Self-critique and automated verification

Inspired by:

- [Anthropic – Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [AIHero – AGENTS.md for plans agents actually read](https://www.aihero.dev/my-agents-md-file-for-building-plans-you-actually-read)
- [Revfactory Harness – meta-skill for agent teams & skill generation](https://github.com/revfactory/harness)

## Harness Context (Stratified Disclosure)

This is a harness-layer skill for long-running agent orchestration and scaffolding. It turns the abstract patterns from the three inspirations into concrete, repeatable rituals that any agentskills.io project can adopt.

The skill definition itself is portable and harness-agnostic. Concrete artifact names, commands, the exact pre-flight ritual, traceability conventions, and even the name of the rules file (AGENTS.md vs CLAUDE.md) are parameters of the invoking harness and are disclosed to the agent at activation time via the project's root rules file, its HARNESS-SPEC (or equivalent), and the live git / progress / tracking state. The invariants — persistent state via artifacts, the Plan-Execute-Test-Commit loop, GAN self-critique, strict agentskills.io compliance, incremental reviewable units, and clean handovers — are enforced uniformly regardless of the specific harness implementation or project domain.

## Core Harness Concerns

A complete harness addresses the following concerns. The precise realization (filenames, schemas, bootstrap commands, and validation steps) is defined in the invoking harness's disclosed specification (often named HARNESS-SPEC.md in CrossR-style harnesses) and supplied at activation:

- Canonical skills live in `.agents/skills/<name>/SKILL.md` following the official agentskills.io format exactly. Claude compatibility files (when the invoking harness uses them) are generated rather than hand-maintained.
- Bootstrap entrypoints (init.sh, justfile, or equivalent) that reproduce the environment and the build/test/clippy matrices used by CI and the rules file.
- A **tracking board** holding work state: stable item ids, a status vocabulary that maps onto done / in progress / todo, containers for workstreams, machine-readable reads, and a URL per item. Which board is a parameter the invoking harness discloses; that there is one is not optional. Work state does not live in a file in the repository — two trackers means two truths.
- A **record on each item**: what changed, the verification that ran, the adversary verdicts, and the commit carrying it, appended after each increment. An agent starting cold continues the work by reading the board.
- Git hygiene combined with a documented session-start ritual that surfaces full current state before any work.
- Root rules file (AGENTS.md / CLAUDE.md) that declares skill activations, the Plan Mode contract, and links to the harness spec.

## Stacked PR Decomposition + Multi-Tier Verification Harnesses

Large or high-risk features must be decomposed into small, stacked, reviewable PRs.

**Key patterns to internalize and enforce:**

- Decompose large or high-risk features into small, stacked, reviewable PRs (typically 8–16 for complex work).
- Each PR must have an explicit "What this PR contains / Next PR / Verification" summary and a risk note.
- Use stable traceability IDs in PR titles, code comments, test names, and tracking artifacts.
- Build **literal verification harnesses** at multiple tiers (in-process parity tests, real packaging/substrate tests, etc.).
- Enforce policy / security gates before any effectful or data-access work.
- Add "reviewability comments" liberally so a human or agent can understand intent in < 2 minutes.
- Decouple documentation (beautiful single-file static deploy guide + its own CI) so docs never block code.

The specific patterns and traceability scheme in use on a given project are documented in its root rules file (AGENTS.md or equivalent, as disclosed by the invoking harness) and harness specification.

## Plan Mode (AIHero Pattern)

```markdown
## Plan Mode (Agents must follow this exactly)

- Make every plan extremely concise. Sacrifice grammar for scannability.
- At the end of each plan, give a bulleted list of unresolved questions (if any).
- Always follow the Plan → Execute → Test → Commit loop.
- Never skip planning. Never jump straight to code.
```

### Plan → Execute → Test → Commit Loop

Repeat every session:

1. **Plan** — Read current progress / tracking + git log → propose next task + plan.
2. **Execute** — Implement using appropriate skills + reference to the harness spec.
3. **Test** — Full matrix + `code-review` + `testing` + `architecture` (or equivalent GAN).
4. **Commit** — Small, reviewable diff + update artifacts + append to progress log.

GAN gate verdicts and report envelopes follow the `gan-verdict` catalog skill — the contract lives there, not here.

## Session Rituals & Error Recovery

Every agent **begins** by executing the harness's disclosed minimal start-of-session ritual. This typically surfaces git state, recent progress, the current tracking snapshot, bootstraps the environment, and runs quick validation checks. The agent then consults the tracking artifact for the next pending granular item.

- Agents must self-verify before marking work complete.
- Use `code-review` (and the full GAN when appropriate) ruthlessly on every code change.
- Git is the safety net — **never** force-push; always commit.
- If state is broken, re-bootstrap via the harness entrypoint and revert to last good commit.

## Activation Statement

> Using `code-writer` + `agent-harness` + [relevant domain skills] (reference the harness specification disclosed at activation for this task).

When bootstrapping a new project, run the harness bootstrap tooling (as defined in the invoking harness's disclosed specification or templates). It creates the initial artifacts (root rules file, tracking files, skills directory, optional compatibility layer, etc.) per the disclosed harness bootstrap. Commit the empty harness. All future work is tracked and executed inside the harness.

## How to Adopt This Skill

1. Ensure this file (or its canonical source) is present at `.agents/skills/agent-harness/SKILL.md`.
2. Update your root rules file to reference `agent-harness` (with the activation statement above) and link to your harness specification (as disclosed by the invoking harness).
3. Run your harness bootstrap when starting a new project or adopting the full pattern.

## Verification

In a fresh activation the following six behaviors are directly observable and scorable:

- The agent recites the One-Sentence Mandate verbatim before emitting any guidance, ritual description, or activation advice.
- The agent explicitly surfaces and treats the invoking harness's disclosed parameters (artifact names, ritual commands, traceability scheme, rules file name, and current state from git state / progress logs / tracking snapshot or the equivalent names disclosed by the invoking harness at activation) as the concrete context, rather than assuming or embedding any fixed CrossR/Tensorwave/ferro names or commands in its output.
- The agent enforces the full Plan → Execute → Test → Commit loop (including concise planning ending in unresolved questions, and post-work self-critique via the appropriate reviewer skills) on every increment and refuses to proceed without each step.
- The agent consistently cites and preserves the three external inspirations (Anthropic long-running scaffolding, AIHero Plan-Execute-Test-Commit, Revfactory Harness) while mapping them onto the disclosed harness without injecting project-specific examples.
- The agent produces only portable, harness-agnostic recommendations; any concrete examples or lists it gives are clearly labeled as "typical" or "as disclosed by the harness" and contain zero hard-coded commands, JSON snippets, PR names, or "every project must" mandates.
- After describing or guiding a unit of work, the agent directs (or performs in its own orchestration) the post-verification update of the harness tracking artifacts and a clean commit before declaring the increment complete or moving on.

Violations against any of these six observable criteria during fresh activation indicate the skill was not followed and must be corrected before the work can be considered complete.

## Specialization

This skill is the dedicated harness-layer specialization (precondition: `code-writer` active; add the disclosed book + domain skills as needed). It supplies the practical, battle-tested voice and patterns for turning the three inspirations into reliable long-running agent behavior — persistent artifacts for state continuity, the Plan-Execute-Test-Commit loop with integrated GAN self-critique, strict agentskills.io compliance, stacked incremental delivery, and clean handovers — while preserving every principle of the base skills (postcondition: combined output satisfies this contract plus the specialization with zero contradictions).

## One-Sentence Mandate (Memorize This)

> “Build harnesses that make long-running agents **reliable**, **incremental**, **self-verifying**, and **handover-clean** by combining Anthropic’s long-running scaffolding, AIHero’s Plan-Execute-Test-Commit loop, and Revfactory patterns inside a portable agentskills.io structure with persistent artifacts and strict verification discipline.”

---

This skill is the canonical authority on effective harnesses for long-running AI agents following agentskills.io standards.

All multi-session or long-running agent work **MUST** be structured inside a harness (defined via the invoking harness's specification or equivalent) that incorporates the patterns and discipline from this skill.

**When using this skill**: Always combine it with the core `code-writer` (plus the disclosed book + domain skills when a language book is disclosed). Reference the harness specification disclosed at activation for exact artifact names, commands, and rituals. Apply the Plan → Execute → Test → Commit loop and ruthless self-critique on every task. Keep the practical, battle-tested voice.

**Activation Statement**  
> Using `code-writer` + `agent-harness` + [relevant domain skills] (reference the harness specification disclosed at activation for this task).

Apply this skill **mercilessly** on every long-running agent scaffolding, bootstrap, or session orchestration task.
