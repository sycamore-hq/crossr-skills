# Plan: Mechanizing the GAN Loop & Hardening the v2 Harness

> **Archived — historical record of a completed campaign.**
> Nothing below is current practice. Work state now lives on the project's tracking
> board (harness `HARNESS-SPEC.md` §3.2, `docs/board-contract.md`). The
> `features.json` and `progress.md` trackers this document references were removed,
> and so was the file-based board it names; the harness requires a board and names
> no product. Read this for what was decided and why, never for how to work today.

**Status**: Executed — All PRs in the chain created and open  
**Goal**: Turn the current aspirational GAN process into something mechanical and reliable, while hardening the core harness tooling.

This plan follows the same strict stacked-PR discipline used for the original v2 harness work (each PR < 10 min deep review).

## Context & Problems Identified

During the post-merge GAN review, the following gaps were called out:

- The GAN (Generator → Reviewer → Tester → Architect) loop is still **cultural**, not mechanical.
- `harness-bootstrap` is fragile and has almost no automated tests.
- JSON Schema exists but is not enforced.
- No sustainable story for syncing skills across projects.
- No agent definitions yet in `.agents/agents/`.

## Proposed Stacked PR Chain

We will deliver the work as a new stacked chain (PRs will be numbered continuing from the previous series or given clear names).

### PR A — Agent Definitions (Highest Leverage)

- Create `.agents/agents/` directory
- Add three core agent definitions:
  - `rust-reviewer-agent.md`
  - `rust-tester-agent.md`
  - `rust-architect-agent.md`
- Define the canonical GAN invocation pattern (how an agent should call the three in sequence)
- Add activation guidance in `agent-harness` skill

**Why first?** This makes the entire review process actually usable by agents.

### PR B — Bootstrap Hardening + Tests

- Add a `test/` directory for the bootstrap script (simple shell-based tests or `bats` if we decide to adopt it)
- Improve error handling and user experience in `scripts/harness-bootstrap`
- Add basic smoke tests that can run in CI

### PR C — Real Schema Enforcement

- Make `just harness-validate` actually enforce `features.schema.json`
- Options to evaluate:
  - Pure `jq` validation (limited but zero-dependency)
  - Optional `ajv-cli` or `jsonschema` (documented)
- Update bootstrap output and documentation

### PR D — Official Skill Syncing Mechanism

- Create `scripts/sync-skills` (or equivalent)
- Decide and document the canonical way projects should pull skills from crossr-skills
- Recommended approach: small script that can copy or symlink from a local checkout of crossr-skills

### PR E — Documentation & Closing Polish

- Update `HARNESS-SPEC.md` with the new mechanical GAN expectations
- Update `README.md` and any getting-started docs
- Add `features.json` version field + migration note
- Mark the mechanization effort complete in `progress.md`

## Execution Rules (Self-Applied)

- Every PR must be reviewable in < 10 minutes.
- Each PR will follow the same format as the previous chain (explicit "This is PR #X", stacked-on link, risk note, reviewability statement).
- We will dogfood the new agent definitions as we create each PR.

## Open Questions (to resolve before or during execution)

- Should we adopt `bats` for shell testing, or keep it dependency-free with simple bash assertions?
- What is the minimal viable version of the agent definition files? (full prompt vs. reference to skills?)
- For skill syncing: do we prefer a "point at your crossr-skills checkout" model or a "download latest" model?
- Do we want to version `features.json` starting at `2` now that the schema exists?

## Success Criteria

When this chain is complete:

- An agent can be instructed to "run the full GAN review" and will actually invoke the three reviewer agents in order.
- Running `just harness-validate` on a valid `features.json` will succeed (and fail on bad data).
- `scripts/harness-bootstrap` has automated tests and is noticeably more robust.
- There is a documented, working way for other projects to stay in sync with crossr-skills skills.

---

**Next Action**: Begin PR A (Agent Definitions) as the first PR in the new stacked chain.