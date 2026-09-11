# Plan: loops-generator-pin

Write-up only. This file plans the fix; it does not cut the tag, does not
edit any `lockfile.toml`, and blesses nothing. Closes
[crossr-loops#21](https://github.com/sycamore-hq/crossr-loops/issues/21).
Parent context only, not closed by this chain:
[crossr-loops#19](https://github.com/sycamore-hq/crossr-loops/issues/19).

Lane S (ship the pin) — chosen over Lane D (docs-only). Lane D would have
restated the CARD law that `book/src/destinations/grok-bot.md` already
states on `crossr-loops` `main`:

> Eight seats need a loops pin whose `.agents/agents/` contains
> `generator-agent.md`. On a pin without it: card, do not mint seven. Do not
> edit `lockfile.toml`. Do not invent a writer brief. Route to such a pin:
> tag loops from `main`, bump harness `loops =`, let bootstrap write the
> tag.

That sentence already names the fix. Lane D was rejected as a plan because
writing it again in `crossr-skills` would be enforcement theater, not
enforcement. This chain does the two things the sentence assumes exist and
today do not: a tag consumers can pin to, and a runbook in
`crossr-harness` for the bump the sentence describes. `just plan-audit
docs/plans/loops-generator-pin-plan.md` gates this file. No HTML twin.

## Preconditions (measured 2026-09-11, `crossr-loops` `origin/main`)

| Fact | Evidence |
|---|---|
| `main` HEAD | `6b958b23a50dbb17e610dc56e2579da3023b9f9` (`6b958b2`, committed 2026-09-10) |
| `.agents/agents/generator-agent.md` on `main` | present, 14 files total in `.agents/agents/` (13 other personas + generator) |
| `generator-agent.md` landed | `1158aa2` ("fix #17: host-neutral generator, tracking, README roster"), an ancestor of `main` |
| Published tags containing `generator-agent.md` | none — checked `v0`, `v1-runtime-agents`, `v1-no-rtl`, `v1-cards`, `v1-one-law-consumers`, `v1-packets-consumers` |
| Harness greenfield pins | `skills = "v1-packets"`, `loops = "v1-packets-consumers"` |
| `crossr-skills` `lockfile.toml` (this repo) | `skills = "v1-gan-layers"`, `loops = "v1-packets-consumers"` — unaffected by this chain |
| `crossr-harness` `HARNESS-SPEC.md` §8 | documents the `lockfile.toml` pin shape (`skills =`, `loops =`, `books =`) and first bootstrap; no runbook exists yet for *moving* an existing pin |

## Decisions settled BEFORE dispatch

| # | Decision |
|---|---|
| 1 | Tag name: `v1-generator-consumers`, an **annotated** git tag in `crossr-loops`, following the precedent of every prior pin tag (`v0`, `v1-runtime-agents`, `v1-no-rtl`, `v1-cards`, `v1-one-law-consumers`, `v1-packets-consumers`) — none of which are GitHub Release objects except `v0`. No Release is cut here either. |
| 2 | The tag is cut from `main`'s tip at execution time, not a cherry-pick of `generator-agent.md` alone. "Cut from current main" means whatever else has landed on `main` (today: the fix #17 destinations series) ships too, same as every prior pin tag. The measured tip as of this writing is `6b958b2`; if `main` moves before Phase 1 executes, tag its new tip instead — still satisfies this decision. |
| 3 | No code or persona-file change lands in `crossr-loops` for this chain. `generator-agent.md` is already on `main` (landed with fix #17); the tag only makes it reachable through the pin mechanism. |
| 4 | The bump runbook lands in `crossr-harness` `HARNESS-SPEC.md`, as a new subsection inside the existing §8 "Bootstrap & Adoption" (next to the `lockfile.toml` pin block already there), not as a new top-level numbered section. Sections 9–12 keep their numbers. |
| 5 | The runbook documents exactly the sequence the destinations law already names: tag the source remote from `main`, edit the consumer's `lockfile.toml` pin, re-run bootstrap. It does not add a new bootstrap flag or script — `harness-bootstrap` already re-copies `.agents/agents/` and `.agents/skills/` from whatever tag `lockfile.toml` names (HARNESS-SPEC.md §8). |
| 6 | `crossr-loops#21` closes by comment + close, naming the new tag and the `crossr-harness` PR. `#19` stays open (parent, context only). `#20` and `#22` are not touched, not referenced as closed, and not bundled into either landing PR. |
| 7 | No `lockfile.toml` is hand-edited by this chain — not this repo's, not any consumer's. Phase 2 documents the edit a *future* consumer makes when it chooses to bump; that edit is a separate, later, per-consumer PR outside this chain. |
| 8 | This PR (in `crossr-skills`) carries the plan artifact only. No `features.json` / `progress.md` row: neither `scripts/verify-docs` nor `just harness-validate` requires one for a `docs/plans/*.md` file, and nothing in this repo changes as a result of this chain (Preconditions row: this repo's `lockfile.toml` is unaffected). |

## Not this chain

- Lane D (docs-only restatement of CARD law) — rejected as a plan; enforcement already exists in `book/src/destinations/grok-bot.md`.
- `crossr-loops#19` (Grok Bot stand-up playbook / labor split) — linked as parent context only.
- `crossr-loops#20` — untouched.
- `crossr-loops#22` (one-line playbook ask) — later, not this chain.
- Any consumer's `lockfile.toml` pin bump, including this repo's — Phase 2 documents the step; executing it is a separate future PR per consumer.
- Hand-editing any `.opencode/agent/` generated file.
- Minting a partial (seven-seat) roster anywhere.
- A GitHub Release object for the new tag.
- Renumbering `HARNESS-SPEC.md` §9–§12, or touching AVRIL/AXEL/BRICK cycle law.

## Phases

### Phase 1 of 3: crossr-loops — cut `v1-generator-consumers` from `main`
- est. LOC: 0
- `git tag -a v1-generator-consumers <main HEAD> -m '<message naming #21 and generator-agent.md>' && git push origin v1-generator-consumers`. No file changes; the tag is a ref.

### Phase 2 of 3: crossr-harness — document the pin bump path
- est. LOC: 25
- Add a "Bumping an existing pin" subsection to `HARNESS-SPEC.md` §8, immediately after the existing `lockfile.toml` pin block, stating the four-step sequence: (1) confirm the needed file is on the source remote's `main` and cut/select a tag from it; (2) edit the consumer's `lockfile.toml` pin (`loops =` or `skills =`) to that tag — the only hand-edit `lockfile.toml` allows; (3) re-run `./scripts/harness-bootstrap .`; (4) verify the previously-missing seat file is now present and nothing else changed except the tag's own diff. Suggested text:

  ```
  ### Bumping an existing pin

  A pin missing a seat file a consumer now needs (for example, `loops`
  without `.agents/agents/generator-agent.md`) is not fixed by hand-editing
  the installed copies or minting a partial roster. Bump the pin:

  1. In the source remote (`crossr-loops` for `loops`, `crossr-skills` for
     `skills`), confirm `main` contains the needed file, then cut (or
     select an existing) annotated tag from `main` that includes it. Push
     the tag.
  2. In the consumer repo, edit `lockfile.toml`'s `loops = "<tag>"` (or
     `skills = "<tag>"`) to the new tag. This is the only hand-edit
     `lockfile.toml` allows — never hand-edit the installed copies under
     `.agents/` or the generated `.opencode/` files.
  3. Re-run `./scripts/harness-bootstrap .` (or the project's bootstrap
     shim). Bootstrap re-copies `.agents/agents/` and `.agents/skills/`
     from the new pin and regenerates `.opencode/agent/` from the copied
     personas; it never overwrites an unmarked file.
  4. Verify: the file that was missing is present, and every other pinned
     file is unchanged except by the tag's own diff.
  ```

### Phase 3 of 3: close crossr-loops#21
- est. LOC: 0
- Comment on and close `crossr-loops#21`, naming `v1-generator-consumers` and linking the `crossr-harness` PR from Phase 2. Confirm in the closing comment that `#19` stays open and `#20`/`#22` are untouched.

## Acceptance Criteria

- AC-01: A published `crossr-loops` git tag exists, cut from a commit on `main`, whose `.agents/agents/` contains `generator-agent.md` alongside the 13 other persona files already on that lineage (`avril-conductor`, `axel-conductor`, `planning-architect`, `product-owner`, `qa-architect`, `visionary-cto`, `generator`, `architect`, `tester`, `reviewer`, `brick-coder`, `brick-mutator`, `brick-refactorer`, `brick-specifier`).
- AC-02: The new tag is consumable by the existing pin mechanism with zero changes to `harness-bootstrap` or to `lockfile.toml`'s schema (`skills =`, `loops =`, `books =`).
- AC-03: `crossr-harness` documents, in one place, the exact steps a consumer follows to move from a pin missing a seat file to one that has it: cut/select the tag, edit the `lockfile.toml` pin, re-run bootstrap, verify the file landed.
- AC-04: `crossr-loops#21` is closed referencing the new tag and the harness doc PR; `#19` remains open as parent context; `#20` and `#22` are untouched by both landing PRs.
- AC-05: No `lockfile.toml` (this repo, `crossr-harness`, or any consumer) is hand-edited by this chain; no `.opencode/` generated file is hand-edited; no partial (seven-seat) roster is minted; destinations law text is unchanged; `HARNESS-SPEC.md` sections 1–7 and 9–12 are unchanged.

## Claims

- C-01: mechanical · AC-01 · `git -C <loops-checkout> fetch --tags -q && git rev-parse v1-generator-consumers^{commit}` → a commit that is `main`'s HEAD at cut time (measured `6b958b23a50dbb17e610dc56e2579da3023b9f9` on 2026-09-11) or a later fast-forward of it, never an earlier commit or a cherry-pick
- C-02: mechanical · AC-01 · `git -C <loops-checkout> show v1-generator-consumers:.agents/agents/generator-agent.md | head -1` → `# generator-agent`
- C-03: mechanical · AC-01 · `git -C <loops-checkout> ls-tree v1-generator-consumers --name-only .agents/agents/ | wc -l` → `14`
- C-04: mechanical · AC-01 · `git -C <loops-checkout> tag --contains 1158aa2 | rg -c '^v1-generator-consumers$'` → `1`
- C-05: observable · AC-01 · `git -C <loops-checkout> cat-file -t v1-generator-consumers` → `tag` (annotated, matching every prior published loops tag), not `commit`
- C-06: mechanical · AC-02 · `git -C <harness-checkout> diff --stat origin/main..HEAD -- scripts/` → empty (bootstrap script itself is not modified by this chain)
- C-07: observable · AC-02 · `HARNESS-SPEC.md` §8's existing pin block (`skills =`, `loops =`, `books =`) is unchanged — only a new subsection is appended after it
- C-08: observable · AC-03 · `HARNESS-SPEC.md` §8 gains a "Bumping an existing pin" subsection stating, in order: cut/select a tag from `main` containing the needed file; edit `lockfile.toml`'s pin; re-run `./scripts/harness-bootstrap .`; verify the file landed
- C-09: mechanical · AC-03 · `rg -n 'Bumping an existing pin' HARNESS-SPEC.md` → 1 hit, inside §8
- C-10: mechanical · AC-03 · `git -C <harness-checkout> diff --stat origin/main..HEAD` → exactly `HARNESS-SPEC.md`
- C-11: mechanical · AC-04 · `gh issue view 21 --repo sycamore-hq/crossr-loops --json state --jq .state` → `CLOSED`
- C-12: observable · AC-04 · the closing comment on `crossr-loops#21` names `v1-generator-consumers` and links the `crossr-harness` PR that carries C-08/C-09/C-10
- C-13: mechanical · AC-04 · `gh issue view 19 --repo sycamore-hq/crossr-loops --json state --jq .state` → `OPEN`; `gh issue view 20 --repo sycamore-hq/crossr-loops --json state --jq .state` and `gh issue view 22 --repo sycamore-hq/crossr-loops --json state --jq .state` → unchanged from their state recorded in the Phase 3 PR body
- C-14: mechanical · AC-05 · `git diff --stat -- lockfile.toml` in `crossr-skills`, `crossr-harness`, and every touched consumer → empty everywhere this chain runs
- C-15: mechanical · AC-05 · `git -C <harness-checkout> diff origin/main..HEAD -- HARNESS-SPEC.md | rg '^[+-]## '` → 0 lines (no top-level section heading added, removed, or renumbered)
- C-16: judgment · AC-05 · reviewer read of every diff in this chain confirms no `.opencode/` generated file is hand-edited and no partial seat roster is minted anywhere

## Preserve

- PV-01 → C-14: `crossr-skills` `lockfile.toml` (`skills = "v1-gan-layers"`, `loops = "v1-packets-consumers"`) stays byte-identical through this chain
- PV-02 → C-06: `harness-bootstrap` and every other script stay byte-identical; only `HARNESS-SPEC.md` gains text
- PV-03 → C-16: `book/src/destinations/grok-bot.md` destinations law (eight-seats/CARD/no-hand-edit/no-partial-mint/AVRIL-first) stays byte-identical — this chain ships the pin the law already prescribes, it does not rewrite the law
- PV-04 → C-13: `crossr-loops#19`, `#20`, `#22` stay open and untouched by this chain except `#19` as linked parent context

## VALIDATE (run after each phase lands, paste in that phase's PR body)

Phase 1 (`crossr-loops`):
```
git fetch --tags -q
git rev-parse v1-generator-consumers^{commit}                       # C-01
git show v1-generator-consumers:.agents/agents/generator-agent.md | head -1   # C-02 → "# generator-agent"
git ls-tree v1-generator-consumers --name-only .agents/agents/ | wc -l        # C-03 → 14
git tag --contains 1158aa2 | rg -c '^v1-generator-consumers$'        # C-04 → 1
git cat-file -t v1-generator-consumers                               # C-05 → tag
```

Phase 2 (`crossr-harness`):
```
git diff --stat origin/main..HEAD -- scripts/                        # C-06 → empty
git diff --stat origin/main..HEAD                                    # C-10 → HARNESS-SPEC.md only
rg -n 'Bumping an existing pin' HARNESS-SPEC.md                       # C-09 → 1 hit
git diff origin/main..HEAD -- HARNESS-SPEC.md | rg '^[+-]## '        # C-15 → 0 lines
```

Phase 3 (issue closure):
```
gh issue view 21 --repo sycamore-hq/crossr-loops --json state --jq .state   # C-11 → CLOSED
gh issue view 19 --repo sycamore-hq/crossr-loops --json state --jq .state   # C-13 → OPEN
gh issue view 20 --repo sycamore-hq/crossr-loops --json state --jq .state
gh issue view 22 --repo sycamore-hq/crossr-loops --json state --jq .state   # C-13 → both unchanged
```

Plan-gate (this repo, run now):
```
./scripts/audit-plan docs/plans/loops-generator-pin-plan.md          # PASS required before this PR merges
```

## Unresolved questions

None blocking. One left for the Architect at Phase 2 dispatch, non-blocking:
whether `crossr-harness`'s `README.md` also gets a one-line pointer to the
new §8 subsection, or the subsection stands alone. Decision 4 fixes where
the runbook lives; it does not fix whether a second file points at it.
