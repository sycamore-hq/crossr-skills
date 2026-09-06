# PR 5 prompt set v2 — One ruleset per book, progressively disclosed

Plan: `crossr-skills/docs/plans/gan-layer-separation-plan.md` §4 PR 5 / §3.4, plus the parked
items recorded under §4 PR 5 ("Parked here from PR 1a review" and "Parked here from PR 3a / 3b
review"). Preconditions, measured on this tree:

| repo | `skills` pin | `loops` pin |
|---|---|---|
| crossr-skills | `v1-gan-layers` | `v1-cards` (landed #110 / 4b) |
| crossr-harness | `v1-gan-layers` | `v1-cards` |
| crossr-loops | `v1-gan-layers` | `v0` (self-pin; brief 5d leaves it) |

PR 4 is fully landed (skills#110, harness#6). 5f is a **one-tag** loops bump
(`v1-cards` → `v1-one-law-consumers`), not a skip.

## What changed from v1 of this prompt set

| v1 | v2 | Why |
|---|---|---|
| OCaml parked | **OCaml included** (own PR) | One book cannot prove the infrastructure is language-agnostic; hardcoding survives a single-book PR undetected. Elm / TypeScript / JavaScript targets already exist in crossr-using repos. |
| `generate` node → `rust` | **Graph fully neutral**; book disclosed per project | `axel/references/harness-parameters.md` already owns the language stack ("disclose at session start"). The graph naming a language is a second authority for the same fact — the dual-mandate bug (plan decision #3) reborn. |
| `rust/references/RULES.md` | **`<book>/RULES.md`** | The v1 path put the extractor's output inside its own input glob. Also makes `references/` = generator-only / How-bearing and `RULES.md` = adversary-facing, structurally. |
| 6 topics | **9 rust topics, per-book sets, open prefix registry** | The v1 six left Safety, Security, Code Style **and Type System & Data** homeless *in Rust too*; OCaml additionally orphans monad pipelines. Prefixes are a baseline, not a closed set. The projection contract is universal; the topic list is per-book. |
| Absorb + delete in one PR | **Additive first, delete last** | Book creation is additive: no window, no dangling name, no coordinated tag. All breakage collapses into the retarget PRs. |
| 6 PRs | **7 PRs**, each smaller | v1's 5a alone was larger than any PR here. |

**Stack (seven PRs):**

```
5a  skills   book infrastructure + rust/ book                     ADDITIVE — deletes nothing
5b  skills   ocaml/ book                                          ADDITIVE — genericity test
5c  skills   gate cards, architecture CP2, two-shape retargets,
             featured/README, delete the three absorbed writers
             → cut skills tag v1-one-law on the 5c merge commit
5d  loops    pin; neutral code-gan.json + requires.book; schema +
             verifier; personas; harness-parameters Language stack
             → cut loops tag v1-one-law-consumers on the merge commit
5e  harness  HARNESS-SPEC §6; lockfile books; smoke; measured sweep
5f  skills   loops pin bump + just regen-agents + plan record closing PR 5
5g  landing  (rider, any time after 5c) drop rust-team-lead + the five retired names
             + the stale harness card at site/templates/index.html:230
```

Tag names `v1-one-law` / `v1-one-law-consumers` are the names. Cut them where the stack
says, on the merge commit after the brief's own pasted validation has been re-run
against that commit. There is no CI (decision 8). Never re-point a cut tag.

---

## Status (measured 2026-09-03)

5a/5b have tracker rows. 5f still closes the PR 5 stack. This section and its HTML
twin must agree with each other.

| PR | Repo | State | Evidence |
|---|---|---|---|
| 5a | skills | **Landed** | [#117](https://github.com/sycamore-hq/crossr-skills/pull/117), rebase-merged 2026-09-03 as `ecc1e62`..`94e3a15` (7 commits). 15 review threads, all resolved. |
| 5b | skills | **Landed** | [#118](https://github.com/sycamore-hq/crossr-skills/pull/118), rebase-merged 2026-09-03 as `e2647be`..`0bd2c40` (3 commits). `ocaml/` book on main; extractor unchanged. |
| 5c | skills | Not started | 5c acceptance grep hits 13 files. No skills tag exists; `v1-one-law` uncut. |
| 5d | loops | Not started | `graphs/code-gan.json` still names `rust-code-writer` / `rust-code-reviewer` / `rust-code-tester`. Pins `skills = v1-gan-layers`, `loops = v0`. |
| 5e | harness | Not started | `HARNESS-SPEC.md:196-197`, `AGENTS.md:12`, `templates/harness/AGENTS.md.template:12` still name dead skills. Pins `v1-gan-layers` / `v1-cards`. |
| 5f | skills | Not started | Loops pin `v1-cards` at all four loci. Plan §4 PR 5 not marked landed. |
| 5g | landing | Not started | `site/templates/index.html` :222, :230, :259-260, :287 all still stale. |

### What 5a landed (measured on main at `94e3a15`)

- `.agents/skills/rust/`: card 2,035 B; 9 topic refs + 2 contract refs; `RULES.md` 5,142 B,
  52 rules. `scripts/extract-rules --check` clean.
- `scripts/extract-rules` (8,374 B); `just rules-sync` / `rules-check`; `rules-check` in
  `harness-validate`.
- `docs/book-topics.md` (630 B) — the only home of the prefix rows.
- Deprecation markers on `rust-code-writer` (7,674 B) and `rust-errors` (5,470 B). Catalog
  entries carry `superseded-by: rust`; `featured` unchanged (5c).

### Amendments the 5a review settled (the briefs below are patched to match)

1. **Book marker is `metadata.book: "true"`**, quoted, not a top-level `book: true`. A
   top-level key is outside the agentskills.io frontmatter set and fails strict validators;
   `metadata` is the spec's extension point. `extract-rules` reads the `book` key after an
   indentation-blind split, so it accepts the metadata shape and nothing needs the top-level
   form. 5b writes the metadata shape; 5d's `verify-skill-refs` selects on the same key.
   (Decision 6; briefs 5a / 5b / 5d; gauntlet 5a / 5b / 5d.)
2. **Rule retirement is supersession, not deletion.** §3.7 applied to ids: keep the bare id
   in the topic `## Rules` block, rewrite the body to `Superseded by <book>/<PREFIX>-nn`,
   drop that rule's `check:` and `tag:`. Write and `--check` stay green because the id did
   not disappear. No `--retire` flag, no `retired:` list on the card. Documented in the
   `scripts/extract-rules` docstring. Append-only began at the #117 merge.
3. **Prefix rows live only in `docs/book-topics.md`.** The rust card links to the registry
   instead of carrying a second copy ("Left to the human" item 4 said card + registry). 5b
   appends `RM` there.
4. **Append-only guard anchors ids at line start**, so an id mentioned in another rule's
   prose no longer masks a disappeared rule. Ids with three or more digits parse; a second
   `check:` / `tag:` on one rule fails loud.
5. **Rules dedupe from review:** RE-06 folded into RE-02 (then-uncommitted, so legal); RD-01
   points at RP-01 for wire strings; RD-06 keeps the builder-with-private-fields mandate;
   RE-02 / RE-03 checks are review-each-hit; RE-02 names no directory; RE-03 still names
   `src/` (the #117 RE-03 thread kept that path).

---

## Decisions settled BEFORE dispatch

1. **OCaml is in** (reverses the "park OCaml" recommendation). `ocaml-code-writer` (19,551 B) is
   absorbed in 5b. Rationale: the infrastructure must be language-agnostic for Elm / TS / JS, and
   generality is unfalsifiable with a single book. Second consequence: OCaml gains adversaries for
   the first time (§2.4 `ocaml reviewer ✗ tester ✗ architect ✗`) the moment the gate cards go
   language-neutral in 5c. §7 row 5 is amended in 5f — it is unsatisfiable as written either way.
2. **The graph carries no language.** `code-gan.json`'s `generate` node retargets to `code-writer`,
   not to a book. The book is disclosed per project via `lockfile.toml` `books = [...]`. Do **not**
   call `books` / `requires.book` "mechanical" until all three readers exist (they land in 5d/5e):
   (i) lockfile schema accepts `books`; (ii) AXEL pre-flight step 4 reads it; (iii) `requires.book:
   true` + an explicit `books = []` (or a consumer lockfile supplied via env whose `books` is
   empty) is a verifier or smoke failure, not only a graph-shape check. Absence of the `books`
   key on the loops self-pin is not a failure — loops is not a language consumer and must not
   grow a `books` key. The empty-array demo lives in the 5e smoke fixture, not in
   `just verify-skill-refs` against loops' own lockfile.
   `requires.book: true` alone only fails a graph that *names* a book skill — session-time
   "undisclosed language stack → stop" stays `axel/SKILL.md:101` until (ii) and (iii) land.
   Multi-book (`books = ["rust", "ts"]`): the session discloses which book applies **per PBI**.
   If unspecified, stop and ask. Do not default to first-listed. Retargeting `generate` to `rust`
   would pin one book inside a shared graph and force `code-gan-<lang>.json` forks with identical
   topology — which is the duplication PR 3 deleted `rust-team-lead` to kill.
3. **The Rules projection is `<book>/RULES.md`** — one generated file per book, committed,
   drift-detectable (gated by review discipline; decision 8), ids fully qualified. Not under
   `references/`: that directory is the extractor's input, and keeping it How-only makes "the
   reviewer never sees How" a path rule.
4. **The projection contract is universal; the topic set is per book.** The contract governs
   **topic** references: each carries `## Rules` + `## How`; ids are append-only; `RULES.md` is
   generated. `specialization.md` and `verification.md` are **contract** references: they carry
   neither heading, the extractor skips them, and fail-loud does not apply to them. Same home as
   the PR 4 exemplar (`axel/references/specialization.md` + `verification.md`). 19 of 21 catalog
   skills already carry both sections; the two without are `gan-verdict` and `obsidian-cli`.
   *Which* topics a book has is the book's business — JS has no `.mli`, Elm has no `unsafe`. The
   extractor collects `## Rules` blocks from opted-in book directories and never hardcodes a
   topic list. Prefixes are a **baseline, not a closed set**: sharing `RE` = errors is nice for
   humans; enforcing the eight (now nine) rust prefixes is how OCaml monads get stuffed into
   `RF`. A book may mint a prefix the rust book does not use. The extractor accepts unknown
   prefixes.
5. **Staged duplication is allowed and time-boxed.** 5a/5b create books while `rust-code-writer`,
   `rust-errors` and `ocaml-code-writer` still exist. The **old path stays authoritative through
   5b**. 5c deletes the superseded writers. 5d moves the consumer disclosure (`harness-parameters`,
   the graph). The pin insulates consumers between 5c and 5d. Superseded skills are frozen (no
   edits) and carry a deprecation marker. Do not write "old path authoritative until 5d" in a 5a
   PR body — a 5c reviewer will treat a correct deletion as a brief violation.
6. **Book membership is explicit.** A book is a catalog skill directory whose `SKILL.md`
   frontmatter carries `metadata.book: "true"` (quoted; a top-level `book:` key is outside the
   agentskills.io frontmatter set — 5a review). `extract-rules` selects on that marker.
   `verify-skill-refs` reads the same marker. Membership is not inferred from "any `references/*.md` with a `## Rules`
   heading" and is not inferred from "a directory containing `RULES.md`". `diataxis` ships
   `references/` with no `## Rules` (six files, verified) and is the progressive-disclosure
   precedent §3.4 cites — it must not become a book by accident. Frontmatter, not the consumer
   `books` array: the extractor runs in crossr-skills and must not need a consumer lockfile.
7. **Featured set after 5c** is
   `["code-writer", "rust", "code-review", "agent-harness", "skill-evaluator"]`.
   Today's `docs/public-skills.json` `featured` is
   `["code-writer", "rust-code-writer", "rust-code-reviewer", "agent-harness", "skill-evaluator"]`.
   `verify-docs` asserts `featured ⊆ skills`. 5c cites this decision; 5e reconciles the harness
   must-list against it; 5g mirrors it in the landing pills. Product choice, not an agent's call.
8. **There is no CI.** Measured against the live remotes: loops and harness have no `.github/`;
   skills has one Pages-deploy workflow (`deploy-moved.yml`, triggered on `docs/moved/**`, no
   validation); this prompt-set PR reports zero check runs. Do not fold a workflow into PR 5 —
   that is a different concern and would widen an already-large stack. Tags cut on the merge
   commit after the brief's own pasted validation has been re-run against that commit. Every
   gate this stack adds (`rules-check`, `extract-rules --check`, the `verify-skill-refs` rules,
   `harness-bootstrap-smoke.sh`) is **drift-detectable, gated by review discipline**: a script
   exists; a script running is the pasted output in the PR body. Write §7 row 5 that way, not
   "drift-gated". "Mechanical" in this stack means a script exists, not that a runner invokes it.

---

## Shared guardrails (paste into every brief verbatim)

```
GUARDRAILS (crossr v2 review standard — violations get the PR rejected):
- Read docs/plans/gan-layer-separation-plan.md (the law; §3.4 and §4 PR 5 govern this
  work) and AGENTS.md in the repo you are editing, before writing anything.
- Enumerate EVERY protected-law edit in the PR body, one numbered item each, with the
  exact before/after phrasing. Undisclosed law edits are an automatic REJECT (#107
  precedent).
- No intermediate delta skills (no rust-review, rust-testing) — shape B, plan decision #2.
- NO BOOK NAME may appear in graphs/, in a gate card (code-review, testing), or in a
  role persona. The book is disclosed per project, never hardcoded. A language-specific
  domain skill (rust-axum-backend, rust-tui, rust-frontend) MAY name its own book —
  that is its subject, not a default. brick-coder and agent-harness may NOT — they
  take the disclosed book. Paste the proving grep in the PR body.
- Never hand-write generated output: graphs/index.html only via verify-graphs --html;
  .opencode/agent/ only via the harness generator; <book>/RULES.md only via
  scripts/extract-rules. Every generator must be idempotent — run it twice, git status
  clean, no timestamps.
- A skill carrying a DEPRECATED marker is frozen: never edit it. Changes go to the book
  that supersedes it.
- Byte tables in the PR body are measured (wc -c on the tree), never estimated.
- Run the repo's validations yourself before opening the PR and paste the results:
  skills: just harness-validate (docs-verify + claude-skills-check + rules-check +
          features.json)
  loops:  just graphs-verify / verify-protocol / verify-skill-refs
  harness: ./test/harness-bootstrap-smoke.sh
- Do not touch progress.md / MIGRATION history / features.json except 5f's plan-record
  append, gan-verdict (tokens are final — §4 PR 5 parked note), or anything outside
  the declared file list. Scope creep is a REJECT.
- Tags are immutable once cut. Cut on the merge commit, after the brief's own
  pasted validation has been re-run against that commit. There is no CI
  (decision 8). Merge order is the stack order. The PR body carries the stack
  line (what merges before, what tag is cut, what comes next).
- The Tester is starved, never deleted. The testing gate card must exist and load.
```

---

## Brief 5a — skills: book infrastructure + the `rust` book (additive)

```
You are implementing crossr v2 PR 5a in sycamore-hq/crossr-skills.

[paste GUARDRAILS]

GOAL — §3.4: one ruleset per language, one location, progressively disclosed, two
projections per topic. This PR builds the book INFRASTRUCTURE and the first book. It
is ADDITIVE: it deletes no skill, renames nothing, and breaks no consumer. The old
Rust path stays authoritative through 5b; 5c deletes it; 5d moves the disclosure;
the pin insulates consumers in between. Say that in the PR body — a reviewer will
otherwise read the duplication as the regression this plan exists to cure.

THE PROJECTION CONTRACT (universal; every book obeys it, now and for Elm/TS/JS):
- The contract governs TOPIC references. Every topic file carries exactly two
  sections:
  ## Rules  — normative, checkable. Each rule <=3 lines. A `check:` command line
              where mechanically checkable; `check:` does NOT count against the
              3-line cap (a rule + check: is 4 lines and is legal). Tag `test` on
              rules the test verifier owns.
  ## How    — examples, patterns, reasoning. Adversaries must NEVER load this.
- Contract references (`specialization.md`, `verification.md`) carry neither
  heading. The extractor skips them. Fail-loud does not apply to them. Same
  home as the PR 4 exemplar (axel/references/specialization.md +
  verification.md). 19 of 21 catalog skills already carry both sections.
- Rule ids: bare `<TOPIC>-nn` in the source file, emitted fully qualified as
  `<book>/<TOPIC>-nn` in the generated projection. Append-only from birth:
  superseded, never renumbered (§3.7 logic applies to rule ids). Do not park this.
- Topic prefix baseline (nice for humans, NOT a closed set the extractor enforces):
  RE error-handling, RP input-parsing, RD type-system-and-data, RL layering,
  RF control-flow, RT testing, RA api-surface, RC tooling,
  RS safety-performance-and-security.
- Put that table in docs/book-topics.md only; the rust card links to the registry (the cross-book
  prefix registry). A third book that needs a topic not in this list allocates a
  prefix there. The extractor ACCEPTS unknown prefixes; it does not enforce this
  list. Sharing prefixes is optional — do not require OCaml to reuse RF for monads.
- The topic SET is per book. Do not hardcode this list anywhere in the tooling.

CREATE .agents/skills/rust/ with `metadata.book: "true"` in SKILL.md frontmatter:
- SKILL.md — a ~2 KB card in the style of the PR-4 conductor cards (see
  crossr-loops .agents/skills/axel/SKILL.md at tag v1-cards, 5,989 B, for the
  *shape*, not the size — pointing at a 6 KB exemplar for a 2 KB target will
  land as a 6 KB card). Which reference applies to which situation, nothing else.
  No persona. A one-sentence contract-summary mandate is allowed per the 8920866
  foundation-mandate decision; keep it to one sentence. Link the prefix registry.
- references/error-handling.md      RE  — absorbs rust-errors/SKILL.md (5,470 B).
                                        SOLE OWNER of unwrap: "Never `.unwrap()`
                                        in production paths". RS does not restate it.
- references/input-parsing.md       RP  — parse-don't-validate, newtypes at the
                                        *edge* (wire → domain). Not the rest of
                                        the type system.
- references/type-system.md         RD  — rust-code-writer "Type System & Data":
                                        newtypes-as-data, Option, Default,
                                        immutability. Homeless in the v1 six and
                                        in the v2 eight; RP is "newtypes at the
                                        edge", not Derive/Default/immutability.
- references/layering.md            RL  — stratification, actions/calculations/data
- references/control-flow.md        RF  — Code Style & Structure: combinator
                                        style, nesting depth, exhaustive match
- references/testing.md             RT  — AAA, error paths, cfg(test); rules tagged `test`
- references/api-surface.md         RA  — pub items, docs, semver
- references/tooling.md             RC  — fmt, clippy pedantic, deny lists,
                                        approved crates, Imports & Dependencies.
                                        Clippy fines (`#[allow(clippy::too_many_*)]`)
                                        live here — they leave the personas in 5d.
- references/safety-performance-and-security.md RS
                                        — Safety & Performance + Security, merged
                                        honestly in the filename. unsafe/overflow,
                                        input trust, secrets. NOT unwrap (RE owns
                                        that). Performance is not Security; the
                                        name admits the merge.
- references/specialization.md          — CONTRACT, not a topic. Precondition/
                                        postcondition against code-writer.
                                        Extractor skips it. rust-code-writer's
                                        Specialization is 444 B.
- references/verification.md            — CONTRACT, not a topic. The six
                                        "directly observable and scorable"
                                        activation criteria. skill-evaluator
                                        reads this. Extractor skips it.
                                        rust-code-writer's Verification is
                                        the evaluation hook; rust-code-reviewer's
                                        is 1,051 B of 5,059 B.

  control-flow, type-system, and safety-performance-and-security are new relative
  to the plan's six-file sketch. The sketch left rust-code-writer's "Code Style &
  Structure", "Type System & Data", "Safety & Performance" and "Security" sections
  with no honest home. Note the additions in the PR body as a disclosed refinement
  of §3.4, not a silent expansion. specialization.md and verification.md are not
  new topics — they are the two canonical sections 19 of 21 catalog skills already
  carry, homed the way PR 4's axel card already answered.

SOURCE MATERIAL (measured on main) — COPY, DO NOT DELETE. Deletion is 5c:
- rust-code-writer/SKILL.md      7,674 B
- rust-errors/SKILL.md           5,470 B
- the Rust-specific bodies of rust-code-reviewer (5,059 B) and rust-code-tester
  (5,083 B) — roughly the ~2-3 KB that is actually Rust per §2.3.
Do NOT restate code-writer's Anti-Pattern Severity / Fines System in any reference.
It was deliberately upstreamed (features.json: harness-v2 pr3 "Fines upstream into
code-writer") and BOTH rust-code-writer and ocaml-code-writer photocopy it — that is
the §2.7 photocopy, twice. Cite `code-writer` in one line instead. Same rule for the
Non-Negotiable Core Principles.

CREATE scripts/extract-rules:
- BOOK-GENERIC. Selects skill directories whose SKILL.md frontmatter has
  `metadata.book: "true"` (prompt-set decision 6). Iterates only those dirs'
  references/*.md; emits one .agents/skills/<book>/RULES.md per book. The
  output path is deliberately OUTSIDE references/ so the extractor never
  ingests its own output. Do not hardcode `rust`, and do not hardcode the
  topic list. Do NOT iterate every .agents/skills/*/references/*.md — that
  glob hits diataxis (six files, none with ## Rules) and would either fail
  loud on arrival or silently mint a book from any skill that later grows a
  ## Rules heading (architecture is the likely candidate; that would then
  fail code-gan.json validation with a monoculture error).
- GENERATED marker at the top of each RULES.md naming this script. Topic headers,
  rule ids fully qualified (`rust/RE-01`), `check:` lines and tags carried through.
- --check mode diffs against the committed file, exits non-zero on drift. ALSO
  fail if any previously-committed rule id DISAPPEARS (append-only, mechanical —
  a tidy renumber that is consistent in source and projection would otherwise
  pass). Learn from scripts/verify-docs GONE list and scripts/regen-agents
  justfile-strip guard (both exist, landed 3c / #109): silent skips manufacture
  the drift this script exists to prevent.
- Fail LOUD on any malformed Rules block in a *topic* reference of a selected
  book (missing id, duplicate id within a book, no `## Rules` section, a rule
  over 3 lines excluding the optional `check:` line). Skip `specialization.md`
  and `verification.md` (no `## Rules`, not topics). Do not fail on non-book
  references/ trees.
- Deterministic (no timestamps) and idempotent: second run byte-identical.
- justfile: `rules-sync` + `rules-check`; add rules-check to harness-validate.

CREATE docs/book-topics.md — the prefix registry. Starting table is the rust
baseline above. 5b will append. The extractor does not read this file as a
closed set; it is for humans allocating a prefix.

DEPRECATION MARKERS (rust-code-writer, rust-errors) — one block at the top of each
SKILL.md: superseded-by path, the PR that deletes it (5c), and its measured byte count
at absorb time. The byte count is a drift detector: if it changes during the staging
window, the absorb was no longer a move.

CATALOG BOOKKEEPING:
- docs/public-skills.json: ADD `rust` (category "Rust Book"). Add
  "status": "superseded-by: rust" to the rust-code-writer and rust-errors entries.
  Do not remove them yet. Do not change `featured` yet (that is 5c, decision 7).
  README table must match by name (verify-docs compares names).
  NOTE: verify-docs enforces allowlist -> disk and README == allowlist, but has NO
  reverse check — a skill directory absent from the allowlist passes silently. So an
  unlisted book would leave the catalog carrying an undocumented skill for the whole
  window. List it.
- Grep the catalog for `rust-errors` and `rust-code-writer`; list every referrer in the
  PR body and state that all of them remain correct until 5c (the old path is still the
  live one). Nothing is dangling in this PR — that is the point of the ordering.
- Do not write dying skill names (`rust-code-writer`, `rust-errors`,
  `ocaml-code-writer`, `rust-code-reviewer`, `rust-code-tester`) into the new
  book trees. Deprecation markers stay on the dying SKILL.md files (deleted in
  5c). 5c's `.agents/skills/` grep hits the book trees; a How note that names
  the source skill paints a correct 5c red.

VALIDATE: just harness-validate PASS including the new rules-check;
./scripts/extract-rules twice -> git status clean; --check red/green demonstrated (edit
a rule, show it fail, revert, show it pass) AND disappeared-id demonstrated (delete
one id, show --check fail, revert). wc -c table: rust/SKILL.md (~2 KB target),
each reference, RULES.md.

PR BODY: stack line (5a -> 5b -> 5c, tag v1-one-law on 5c); "ADDITIVE — deletes
nothing, old path authoritative through 5b; 5c deletes; 5d moves disclosure";
the added topics (RF, RD, RS-rename) disclosed; every protected-law edit
enumerated; the staging-window discipline (frozen skills, markers).
```

---

## Brief 5b — skills: the `ocaml` book (additive; the genericity test)

```
You are implementing crossr v2 PR 5b in sycamore-hq/crossr-skills, stacked on 5a
(the projection contract, the extractor and the rust/ book exist).

[paste GUARDRAILS]

GOAL: a second book. This PR is the test of whether 5a's infrastructure is actually
language-agnostic — the property the whole book model rests on for Elm, TypeScript and
JavaScript, which are already in play in crossr-using repos.

HARD ACCEPTANCE CONDITION:
  This PR touches ZERO lines of scripts/extract-rules and ZERO lines of the justfile
  rules-* targets. If you find you need to change either, STOP and report it — 5a
  hardcoded something and the fix belongs in a 5a follow-up, not here. State the
  zero-line result in the PR body with `git diff --stat`.

CREATE .agents/skills/ocaml/ with `metadata.book: "true"` in SKILL.md frontmatter, absorbing
ocaml-code-writer/SKILL.md (19,551 B — the largest file in the catalog). Same
contract, ids `ocaml/<TOPIC>-nn`. Its topic set is OCaml's, not Rust's. From the
source headings, expect:
- error-handling      RE  — Result errors, fail-closed combinators
- input-parsing       RP  — wire strings parsed to domain types at the edge.
                            Pattern matching's "stringly types die at the edge"
                            lives HERE, not in RF.
- layering            RL  — Modules & Layering, .ml/.mli stratification
- control-flow        RF  — no nested match, combinators then match then helpers.
                            Code Style & Structure. NOT monads. NOT stringly types.
- monads              RM  — NEW FILE ocaml/references/monads.md. `let*` = Result /
                            `let**` = Option monad discipline. Prefix the rust
                            book does not use. Append RM to docs/book-topics.md.
                            Do not stuff this into RF — that is the junk drawer
                            shared-mandatory-prefixes would force.
- testing             RT  — rules tagged `test`
- api-surface         RA  — .mli-first, abstract `type t`, documentation
                            (Documentation heading already belongs here)
- tooling             RC  — dune build @check @fmt @runtest, ocamlformat pinning,
                            imports & dependencies
- safety-performance-and-security RS
                          — no Obj.magic / List.hd / catch-all try, no [@warning]
                            suppressions
Distribute "OCaml-Specific Anti-Patterns" into the topic each belongs to. Do NOT create
an anti-patterns grab-bag reference — a bag with no topic has no reviewer projection.
Do NOT restate code-writer's Fines System (see 5a).
Remaining Pattern Matching rules that are match-discipline (not edge parsing) go in RF.
Add the same two contract references as 5a: references/specialization.md and
references/verification.md. Extractor already skips them (5a). Same rule: do not
write dying skill names into the ocaml book tree.

DEPRECATION MARKER on ocaml-code-writer (superseded-by ocaml, deleted in 5c, measured
19,551 B). Do not delete it here.

CATALOG BOOKKEEPING: add `ocaml` (category "OCaml Book") to docs/public-skills.json +
README; mark the ocaml-code-writer entry "status": "superseded-by: ocaml".

VALIDATE: just harness-validate PASS; rules-check now covers BOTH books; extractor twice
-> clean; wc -c table for ocaml/SKILL.md, each reference, RULES.md.

PR BODY: the zero-line extractor result (headline — it is what this PR proves); stack
line; topic-set differences from the rust book (RM especially) and why each is a
language fact rather than a contract violation.
```

---

## Brief 5c — skills: gate cards, architecture CP2, two-shape retargets, deletions

```
You are implementing crossr v2 PR 5c in sycamore-hq/crossr-skills, stacked on 5b
(both books exist; the three writers are staged for deletion and frozen).

[paste GUARDRAILS]

GOAL: the adversary skills become thin, LANGUAGE-NEUTRAL gate cards named for the
activity (plan decision #1); every writer-stack reference retargets; the superseded
writers are deleted; featured and README stay internally consistent. After this PR
the catalog has ONE writer skill (code-writer) plus N books, and the tag v1-one-law
is cut on the merge commit after this brief's pasted validation has been re-run
against that commit (decision 8 — there is no CI).

This PR stays one PR, not 5c′. Retargets and deletions are atomic — a dangling
rust-code-writer name in a live skill is the class of bug verify-skill-refs exists
for. The two retarget shapes are separate instruction blocks below, not a second PR.

RENAMES (git mv, keep history):
- rust-code-reviewer (5,059 B) -> code-review. Strip to the gate card: what this gate
  verifies, its inputs, the gan-verdict response contract line. Target <=2 KB (§7 row 5).
  KEEP the existing inputs sentence (line 15 of today's card), do not invent a second
  formulation of the same contract in the same PR that deletes the first:
    "Your inputs are the disclosed gate card inputs: the change under review, its
     brief, and the disclosed book Rules projection when one exists."
  Never `rust/RULES.md` — a gate card naming a book is the monoculture bug one layer up,
  and it would fail the language-neutrality grep below.
  The card must also state that adversaries load RULES.md ONLY, never <book>/references/
  (§3.4: a reviewer fed How suggests implementations).
  The ~2 KB of real Rust law (thiserror / no anyhow / no unwrap / pedantic clippy /
  approved crates) was copied into the rust book in 5a — DELETE it here and prove nothing
  was lost: map every deleted section to its book reference file + rule ids in the PR body.
  Delete the "Non-Negotiable Core Principles" restatement outright (§2.7 photocopy).
- rust-code-tester (5,083 B) -> testing. Same treatment, same inputs sentence.
  The tester's Rust delta lives in rust/references/testing.md tagged `test`; the card
  says "rules tagged `test` in the disclosed book's Rules projection".
  rust-code-tester:35 still delegates fixes to `rust-code-writer`. That locus dies
  here. Point it at the generator (`code-writer`), not a book.
- gan-verdict/SKILL.md is generic: `<gate>: BLESS | REJECT` (e.g. `architecture:
  BLESS`). It does not carry the literal `code-review:` / `testing:` strings.
  Do not edit it (tokens are final — §4 PR 5 parked note; also in the guardrails).
  A 5c grep of this repo cannot verify the gate names — they live in the
  crossr-loops personas, which this PR cannot see:
    reviewer-agent.md:27   code-review: BLESS | REJECT
    tester-agent.md:28     testing: BLESS | REJECT
    architect-agent.md:27  architecture: BLESS | REJECT
  Verifying and protecting those three lines is 5d's job, not 5c's.
- Both gate cards CARRY Verification and Specialization as contract references,
  not in the <=2 KB card. rust-code-reviewer's Verification alone is 1,051 B of
  5,059 B. Same home as the books and as axel: references/specialization.md +
  references/verification.md. The card routes. Dropping them would make rust,
  ocaml, code-review and testing the first four catalog skills since the split
  to lose the canonical structure, and verify-docs only checks SKILL.md is
  non-empty.
  verification.md transfers verbatim — it is already language-neutral in both
  cards and already says "the disclosed book Rules projection when one exists".
  specialization.md must be de-Rusted in this PR: the gate is language-neutral
  now, so "the dedicated Rust code quality review gate card" -> "the code
  quality review gate card", "pedantic Rust code quality review for all Rust
  code" -> "...for the code under review", "All Rust code generation" ->
  "All code generation". Four loci in the reviewer, three in the tester.
  Enumerate them in the PR body — they are protected-law edits like any other.
  This does not apply to the books: rust/references/specialization.md and
  ocaml/references/specialization.md name their language. The neutrality grep
  never looks at them.

ARCHITECTURE (protected law — one disclosed edit; architecture/SKILL.md is 4,791 B):
- Core Principle 2, "Violates the principles of `code-writer` + `rust-code-writer` (and
  their specializations)" -> "Violates `code-writer` or the disclosed book's Rules
  projection". Zero other checklist edits (1a's zero-checklist-edits discipline). This
  is the parked 1a item — cite it.

DOMAIN SKILL RETARGETS — two shapes. Enumerate every locus, per file, in the PR body.

  SHAPE A — subject is Rust (may name the rust book):
  rust-axum-backend 7,728 B, rust-tui 7,986 B, rust-frontend 9,005 B.
  Every "activate together with `code-writer` + `rust-code-writer`" and every
  "extends rust-code-writer" locus -> `code-writer` + the `rust` book.
  rust-axum-backend alone has ~9 loci (frontmatter, MUST-apply, verification
  scorable, Specialization, mandate, activation statement). Counted 9/9/9.
  These skills MAY name the `rust` book: a Rust domain skill's subject is Rust.
  That is not the hardcoding the guardrail forbids; gate cards and graphs are.
  Domain skills stay separate skills (§8 open q. 4) — do NOT absorb them.

  SHAPE B — language-clean (must NOT pin to rust):
  brick-coder 7,210 B, agent-harness 11,732 B.
  Today's brick-coder already says "disclosed language skills" with Rust as an
  example (`rust-code-writer`, plus `rust-errors` … as applicable). Keep that
  architecture. Retarget to `code-writer` + the *disclosed* book. Keep the Rust
  example; drop the hardcoded writer name. Pinning brick-coder to the rust book
  makes BRICK Rust-only and contradicts §8 q.3 (brick stays parked / language-clean)
  and prompt-set decision 2 (the graph carries no language).
  agent-harness has six loci (lines 10, 15, 85, 95, 126, 138) and appears in no
  other brief. Same shape as brick-coder: `code-writer` + the disclosed book
  (and the disclosed gate cards, not `rust-code-reviewer` / `rust-code-tester`).
  It is a public catalog skill, not history. If you omit it the acceptance grep
  cannot go to zero and the guardrails forbid touching it as scope creep.

DELETIONS (the staging window closes here):
- .agents/skills/rust-code-writer/, rust-errors/, ocaml-code-writer/.
  There are no in-repo Claude compatibility copies — scripts/sync-claude-skills
  writes to $HOME/.claude/skills (or $CLAUDE_SKILLS_DIR) and NEVER deletes
  (FOREIGN copies are reported and left alone, by design). Previously-installed
  copies persist on developer machines and will show up as
  "left alone (not in this repo)" in claude-skills-check. Note that in the PR
  body. Do not attempt to remove them. Do not invent a --prune flag in this PR.
- docs/public-skills.json:
  drop the three writer entries; drop the "status" markers from 5a/5b;
  rust-code-reviewer -> code-review, rust-code-tester -> testing;
  retarget `featured` to prompt-set decision 7:
    ["code-writer", "rust", "code-review", "agent-harness", "skill-evaluator"]
  After the three deletions, categories "Rust Core" and "OCaml Core" are empty
  (they contained exactly rust-code-writer and ocaml-code-writer; rust-errors
  is Backend). Drop the empty categories. 5a/5b already added "Rust Book" /
  "OCaml Book". Disclose this in the PR body — it is a consequence, not a surprise.
- README.md table to match (verify-docs parses table rows).
- README.md:78 prose (NOT the table; verify-docs will not catch it):
  "Every skill is reviewed by `rust-code-reviewer`, `rust-code-tester`, and
  `architecture`" -> `code-review`, `testing`, and `architecture`.

ACCEPTANCE GREPS, paste results in the body:
  grep -rnE 'rust-code-writer|rust-errors|ocaml-code-writer|rust-code-reviewer|rust-code-tester' \
    .agents/skills/ README.md AGENTS.md docs/public-skills.json
  -> zero hits. Do NOT include .opencode/ — those five files are GENERATED
  (reviewer-agent, tester-agent, brick-*-agent) from loop personas. 5d retargets
  the sources; 5f runs regen-agents. A 5c grep over .opencode/ cannot be zero
  until 5f, and the guardrails forbid hand-editing generated output. History
  files (progress.md, features.json titles, docs/plans/) are excluded by
  construction — do not edit them.
  grep -rniE '\b(rust|ocaml)\b' .agents/skills/code-review/ .agents/skills/testing/
  -> zero hits. This is the language-neutrality proof for the gate cards.
  Word boundaries are load-bearing: a bare `rust` matches `trust`, and the rust
  book's RS topic is "input trust, secrets". -i is load-bearing: the dying
  prose is `Rust` / `OCaml`, and a case-sensitive grep misses most of it
  (measured: reviewer card 1 vs 10 lines; ocaml-code-writer 5 vs 25).

VALIDATE: just harness-validate PASS (rules-check still green — deleting the
writers must not disturb either book; featured ⊆ skills). wc -c table:
code-review, testing (both <=2 KB), architecture (4,791 B ± the CP2 line).

PR BODY: mapping table old law -> book file + rule ids, line by line; every
protected-law edit enumerated (architecture CP2, both gate-card strips, the
seven specialization.md de-Rust loci, each domain locus, both shape-B loci,
featured, README:78); stack line (merge after
5b, cut tag v1-one-law here after pasted validation); the named consumers that break until 5d
(loops graphs + personas at the current pin — the pin insulates them; nothing
breaks until the pin moves, which is what the tags are for); the Claude-copy
note (FOREIGN, left alone).
```

---

## Brief 5d — loops: neutral graph, disclosure mechanism, personas

```
You are implementing crossr v2 PR 5d in sycamore-hq/crossr-loops.
Precondition: skills tag v1-one-law exists (verify with git ls-remote; state the peeled
SHA in the PR body).

[paste GUARDRAILS]

GOAL: the loop stops naming a language. The graph carries topology; the book is disclosed
per project. This is the prompt-set-decision-2 half of PR 5. (Plan decision #2 is "no
delta skills / shape B". Do not write "decision #2" without the qualifier — an agent
with the plan open will load the wrong #2.)

- lockfile.toml: skills = "v1-one-law" (the loops self-pin line: leave as is).
  README.md:9 writes the same skills pin today (`skills = "v1-gan-layers"`).
  Update it here. A pin written in two places that only one brief moves is
  the same single-authority bug decision 2 killed for the language.

- graphs/code-gan.json (the 3a park, recorded in the plan):
    generate  node uses.skill: rust-code-writer   -> code-writer
    reviewer  node uses.skill: rust-code-reviewer -> code-review
    tester    node uses.skill: rust-code-tester   -> testing
    architect node: unchanged
    requires.skills: ["code-writer", "code-review", "testing", "architecture"]
    requires.book: true        <-- NEW
  Topology unchanged. NO book name appears in this file. graphs/index.html regenerated
  via ./scripts/verify-graphs --html only.

- graphs/schema.json: `requires` currently has "additionalProperties": false, so
  `requires.book` MUST be added to the schema in this PR or the graph fails validation.
  Add it as {"type": "boolean", "description": "Runs only against a disclosed language
  book; the graph never names one."}.

- scripts/verify-skill-refs — three additions, each a separate commit with its own test
  output:
  1. If a graph declares requires.book: true, FAIL if any uses.skill or requires.skills
     entry resolves to a book skill. A book skill is a catalog skill directory whose
     SKILL.md frontmatter has `metadata.book: "true"` (prompt-set decision 6 — the same marker
     extract-rules selects on). Do NOT infer book-ness from "directory contains
     RULES.md": that definition disagrees with 5a and makes membership an emergent
     property of file contents. The day architecture grows a references/ file with
     a ## Rules heading, the old definition would fail code-gan.json with a
     monoculture error for an unrelated change.
  2. If a graph declares requires.book: true AND a consumer lockfile (supplied
     via env, not the loops self-pin) has an explicit `books = []`, FAIL. Absence
     of the `books` key is not a failure. This is reader (iii) of prompt-set
     decision 2. The loops self-pin is `skills` + `loops = "v0"` only and must
     not grow a `books` key. The empty-array demo lives in the 5e smoke fixture
     (`requires.book: true + books = []`), not in `just verify-skill-refs`
     against loops' own lockfile. Graph-shape alone does not fail a session
     that disclosed no book.
  3. Resolve persona Required Skills lines against the catalog. Today verify-skill-refs
     checks graphs only — nothing mechanical catches a stale persona requirement, which
     is why this brief has to enumerate them by hand below.

- PERSONAS (.agents/agents/) — two classes of edit, enumerate each:
  1. Required Skills retargets: reviewer-agent requires rust-code-reviewer -> code-review;
     tester-agent requires rust-code-tester -> testing. Also brick-coder-agent,
     brick-mutator-agent and brick-refactorer-agent. Today all three brick personas
     say `rust-code-writer` (or the disclosed language writer). The parenthetical is
     already the architecture. Drop the writer name; keep "the disclosed book".
     Do NOT follow the 5c shape-A pattern and pin them to `rust`.
     (`brick` itself stays parked per §8 q. 3 — its personas still break without this).
  2. Voice de-Rust (the 2a parked gap). The title line is not enough. reviewer-agent
     still has: mandate "Make every piece of Rust code…"; personality "functional
     purity in Rust"; invocation `#[allow(clippy::too_many_*)]` — that last is book
     law, not persona voice. Sweep tester-agent ("Obsessive Rust Testing Guardian"),
     architect-agent and both conductor personas. Put clippy fines in the rust book
     (RC, 5a already placed them). The persona keeps the $100 / $100,000 *shape*
     without the Rust token. If the gauntlet greps `Rust` in .agents/agents/, these
     have to move or the grep is theatre.
  3. DON'T TOUCH the verdict-format lines. They sit two lines from the
     Rust-flavoured role line this brief de-Rusts:
       reviewer-agent.md:27  **Verdict format** (per gan-verdict): code-review: BLESS | REJECT
       tester-agent.md:28    **Verdict format** (per gan-verdict): testing: BLESS | REJECT
       architect-agent.md:27 **Verdict format** (per gan-verdict): architecture: BLESS | REJECT
     verify-protocol checks that personas declare BLESS/REJECT verbatim and
     carry no retired tokens. It never checks the gate-name prefix. Clipping
     `code-review:` would leave validation green and break the verdict
     protocol. Protect those three lines. gan-verdict itself is generic
     (`<gate>: BLESS | REJECT`) and is not in this repo.

- .agents/skills/axel/references/harness-parameters.md §"Language stack (stratified)" —
  THE DISCLOSURE AUTHORITY, and the file v1 of this prompt set never named. Its "Rust
  (default when the repo is Rust / harness says so)" block hardcodes the whole dying
  triple plus rust-errors and the domain skills. Rewrite it book-driven:
    - The harness discloses `books` (from the consumer repo's lockfile.toml) at session
      start. This is reader (ii) of prompt-set decision 2 — AXEL pre-flight step 4.
    - Generator loads: code-writer + <book> (card + the references for the situation) +
      domain skills.
    - Adversaries load: the gate card + <book>/RULES.md. Never <book>/references/.
    - Test verifier: rules tagged `test` in that same RULES.md.
    - No book disclosed -> stop and ask the human (axel/SKILL.md:101, now reading
      lockfile `books` instead of vibes). Multi-book: disclose which book applies
      per PBI; if unspecified, stop and ask; do not default to first-listed.
  axel/SKILL.md:29 pre-flight step 4 ("State language stack + adversary chain") stays —
  it is now satisfiable from the lockfile.

- REPO-WIDE SWEEP. v1 of this prompt set told the agent to grep book/src/pipeline/*.md,
  README.md and templates/harness/opencode/command/*.md. Measured: NONE of those contain
  a single hit. The actual referrers of the four dying names are:
      graphs/code-gan.json                                 (above)
      .agents/agents/reviewer-agent.md, tester-agent.md    (above)
      .agents/agents/brick-coder-agent.md, brick-mutator-agent.md,
        brick-refactorer-agent.md                          (above)
      .agents/skills/axel/references/harness-parameters.md (above)
      AGENTS.md                                            (retarget)
      graphs/index.html                                    (generated — regenerate)
      progress.md                                          (history — do not touch)
  Re-run the grep yourself repo-wide (exclude .git, progress.md, MIGRATION) and paste it;
  do not trust this list to still be complete.
  While in the book: the stale scull7/crossr-skills HARNESS-SPEC links (axel.md, avril.md)
  are parked review debt — fix them to
  sycamore-hq/crossr-harness/blob/main/HARNESS-SPEC.md in this pass.

VALIDATE: graphs-verify, verify-protocol and verify-skill-refs all PASS with
CROSSR_SKILLS_PATH pointed at a v1-one-law checkout; paste the output, including a
demonstration that the new requires.book rule fails when you temporarily point a node at
a book. Do NOT demo "when books is empty" against the loops checkout — that is
unsatisfiable without poisoning the self-pin. Empty-books is the 5e smoke fixture.
The three verdict-format lines above are unchanged. Cut tag v1-one-law-consumers
on the merge commit after this brief's pasted validation has been re-run against
that commit (decision 8 — there is no CI; stack line in the body).
```

---

## Brief 5e — harness: spec, the `books` declaration, smoke, measured sweep

```
You are implementing crossr v2 PR 5e in sycamore-hq/crossr-harness.
Precondition: tags v1-one-law (skills) and v1-one-law-consumers (loops) exist — verify
and state peeled SHAs.

[paste GUARDRAILS]

- lockfile.toml + lockfile.toml.example: skills = "v1-one-law",
  loops = "v1-one-law-consumers". Example comment updated.
  README.md writes the same pins today (lines 7, 20, 29-30). Update those
  three loci here. Same single-authority rule as 5f.

- NEW: the per-project book declaration. Add to lockfile.toml.example, with a comment:
      books = ["rust"]     # disclosed language books; ["ocaml"], ["rust", "ts"], ...
  Keep `books` in this PR (do not park to PR 6). It is a DISCLOSURE filter, not a
  copy filter: scripts/harness-bootstrap copy_skill_dirs copies every skill
  directory that has a SKILL.md, unconditionally, does not read `books`, and that
  stays true. Document the distinction in HARNESS-SPEC.md so nobody later
  "optimizes" bootstrap into partial copies.
  This is reader (i) of prompt-set decision 2 — lockfile schema accepts `books`.
  Do not call the declaration "mechanical" in the spec until you have also:
    * accepted the key in whatever parses lockfile.toml
    * wired AXEL pre-flight step 4 (5d reader ii; already briefed)
    * added a smoke failure for requires.book: true + books == []
      (reader iii — this fixture is the home; 5d verify-skill-refs does
      not fail the loops self-pin for a missing books key)
  Multi-book selection (state it in the spec, do not leave it implicit): when
  more than one book is listed, the session discloses which applies per PBI;
  if unspecified, stop and ask; do not default to first-listed.

- HARNESS-SPEC.md §6 (the 3b park, recorded in the plan): gate 2 rust-code-reviewer ->
  code-review, gate 3 rust-code-tester -> testing. Gate 4 is already architecture.
  Sweep the whole spec for the five dead names, listed:
      rust-code-writer, rust-errors, rust-code-reviewer, rust-code-tester,
      ocaml-code-writer
  ("the four above plus ocaml-code-writer" is three, not five — use this list).
  Enumerate every edit. Add the book/disclosure model to the spec's GAN section.

- MEASURED SWEEP. v1 of this prompt set named chief-of-staff and dashboard-prompt.
  Measured on crossr-harness main, those two have ZERO hits. The five dead names
  appear in exactly three files:
      HARNESS-SPEC.md                        2 hits  (§6 gates 2 and 3 — named above)
      AGENTS.md:12                           1 hit   — rust-code-writer
      templates/harness/AGENTS.md.template   1 hit   — rust-code-writer
  The template is the highest-blast-radius referrer in the stack:
  harness-bootstrap:249-250 copies it verbatim into every newly bootstrapped
  consumer repo. Left stale, PR 5 deletes rust-code-writer from the catalog and
  then keeps writing its name into AGENTS.md of every project bootstrapped
  afterwards — a dangling skill reference in *consumer* repos (the class of bug
  verify-skill-refs exists for). Retarget the template book-driven, matching
  whatever harness-parameters.md says after 5d — not a one-word name swap.
  Re-run the grep yourself repo-wide (exclude .git, progress.md, MIGRATION) and
  paste it; do not trust this list to still be complete. Retarget every live hit.

- scripts/verify-docs: the site block is dead code here (guarded on a site/ directory this
  repo does not have — established in the 3b review) and its must-list still requires
  rust-team-lead. Either delete the site block outright (recommended — the site lives in
  crossr-web-landing, which owns its own copy checks) or fix the must-list to prompt-set
  decision 7's featured set. State which and why. This is the harness half of the
  "move the allowlist and the landing copy together" plan item — cite it; 5g is the
  landing half.

- test/harness-bootstrap-smoke.sh: pins updated. Add assertions that a fresh target has
  .agents/skills/rust/, .agents/skills/ocaml/, .agents/skills/code-review/ and
  .agents/skills/testing/ — and, more importantly, that it has NO rust-code-writer/,
  rust-errors/, ocaml-code-writer/, rust-code-reviewer/ or rust-code-tester/. The ABSENCE
  assertions are the ones that matter: presence-of-books would have passed during the
  5a/5b staging window too and proved nothing.
  Also assert each book ships a committed RULES.md (bootstrap copies files and never runs
  generators, so an uncommitted projection means consumers get nothing).
  Also assert the example lockfile has a non-empty `books` array, and that a fixture
  with requires.book: true + books = [] fails (reader iii).
  Conductor window unchanged: axel 5,989 + gan-verdict 1,132 = 7,121. Books are
  subagent-side and must NOT appear in the conductor window — assert that too.

VALIDATE: ./test/harness-bootstrap-smoke.sh PASS end-to-end, paste the tail.
```

---

## Brief 5f — skills: closer + plan record

```
You are implementing crossr v2 PR 5f in sycamore-hq/crossr-skills.
Precondition: 5a-5e merged; loops tag v1-one-law-consumers exists.

[paste GUARDRAILS]
This brief's plan-record append to progress.md / features.json / the plan twins
is the guardrail carve-out. Do that work. Do not treat "do not touch progress.md"
as higher law than this brief.

- lockfile.toml: loops = "v1-one-law-consumers".
  Starting pin is v1-cards (measured; landed #110 / 4b). This is a one-tag bump.
  The same pin is written in three more places that agree with lockfile.toml
  today. Update all four or the stack desynchronizes four currently-consistent
  statements of the same fact (the single-authority bug decision 2 killed
  for the language):
      lockfile.toml          loops  = "v1-cards"          (authority)
      AGENTS.md:53           Consumer pins: ... loops = "v1-cards"
                             ...and are in the `v1-cards` pin
      README.md:24           Current pins: ... loops = "v1-cards"
      README.md:26           Topology ... is in the `v1-cards` pin
  lockfile.toml is the pin. The other three are documentation of it. They
  move in this PR because a second authority for the pin is already in the
  tree.

- Deleted/stale check first, then just regen-agents. This target EXISTS — it
  landed in 3c (skills#109): scripts/regen-agents + the justfile recipe. It is
  bootstrap + GONE-list strip, idempotent. Do not invent a new script. Do not
  treat gan-layer-separation-plan.md:648's original "would make" sentence as
  current tense; the plan's later landed note already records 3c.
  Personas changed in 5d — the regenerated .opencode/agent/ files pick up the
  de-Rusted voice and retargeted required skills. Second run: git status clean.
  No orphan-persona warnings — that warning is warn_orphan_personas in
  crossr-harness/scripts/harness-bootstrap. If 5d's edits left stale copies
  anywhere, delete and rerun.

- ACCEPTANCE GREP (the one 5c cannot run), paste in the body:
  grep -rnE 'rust-code-writer|rust-errors|ocaml-code-writer|rust-code-reviewer|rust-code-tester' \
    .opencode/agent/
  -> zero hits. These five generated files (reviewer-agent, tester-agent,
  brick-coder-agent, brick-mutator-agent, brick-refactorer-agent) still name
  the dying skills until this regen. That is why 5c dropped .opencode/ from
  its grep.

- PLAN RECORD (docs/plans/gan-layer-separation-plan.md AND its hand-maintained HTML twin
  docs/plans/gan-layer-separation-plan.html — there is no generator for the twin; both
  must be edited and must agree; this prompt-set holds itself to the same rule):
  - Mark PR 5 landed with all seven PR links and both tags.
  - §7 row 5, replace the unsatisfiable "one writer skill remains (code-writer)" with:
      "One universal writer skill (code-writer) plus one book per language. Zero
       <lang>-code-writer skills remain — rust-code-writer, rust-errors and
       ocaml-code-writer absorbed. Rules projections generated per book and
       drift-detectable, gated by review discipline (decision 8);
       gate cards <=2 KB and book-agnostic; the code-gan graph names no language."
    Record the measured results: N rules per book with stable ids, gate-card bytes,
    reviewer load set (gate card + RULES.md) against the pre-PR reviewer skill at 5,059 B.
  - §2.4 monoculture table: rust and ocaml now both have writer + reviewer + tester +
    architect coverage. That table was the plan's original diagnosis; update it.
  - §8: close open question 3's sibling reasoning where it was applied to OCaml, and
    record the reversal honestly — the pre-dispatch recommendation was to park OCaml; it
    was overruled because a single book cannot demonstrate that the infrastructure is
    language-agnostic, which is the property Elm / TypeScript / JavaScript targets depend
    on. Record 5b's zero-line extractor diff as the evidence that it does.
  - Add the decisions this stack settled that the plan did not previously contain:
    the projection contract vs. per-book topic sets; <book>/RULES.md placement;
    requires.book; the lockfile `books` declaration; `metadata.book: "true"` frontmatter;
    featured set (decision 7); open prefix registry; check: excluded from the 3-line cap;
    contract vs topic references (specialization.md / verification.md); no CI /
    drift-detectable (decision 8).
  - Discharge the parked items this stack closed: architecture CP2 (1a), code-gan.json
    (3a), HARNESS-SPEC §6 (3b), persona voice (2a), the harness half of the featured-set
    item (5e). Mark the landing half (5g) as the only remaining piece if it has not
    merged yet.
  - Acceptance condition 1 status note: with the book split and the neutral graph, an
    Elm/Melange run loads code-writer + the axel card + the universal gate cards and does
    not halt; what remains before it can be demonstrated live is an `elm` book and
    books = ["elm"] in that repo's lockfile. State it plainly — the condition is not yet
    demonstrated, only unblocked.
- progress.md + features.json entries per house style. In scope here.
- VALIDATE: just harness-validate PASS (including rules-check). .opencode/ grep above
  is green. All four pin loci read `v1-one-law-consumers`.
```

---

## Brief 5g — web-landing rider (any time after 5c)

```
You are implementing the crossr v2 landing fix in sycamore-hq/crossr-web-landing.
Recorded debt: gan-layer-separation-plan §4 PR 3 landed block ("move the allowlist and
the landing copy together").

- site/templates/index.html:222 — the crossr-loops card says "AVRIL, AXEL, BRICK
  conductor, rust-team-lead. ...". Drop rust-team-lead; if the card lists what loops
  ships, the current truth is "AVRIL, AXEL, BRICK conductor, code-gan graph".
- site/templates/index.html:230 — the crossr-harness card still says
  `skills = v0-last-monolith`, `loops = v0`, "Never overwrites `.opencode/`".
  All three claims died in PR 2/4. "Do not add new claims" is correct; retargeting
  a false claim is not adding one. Name this card. Current truth: pins follow the
  lockfile (`skills = v1-one-law`, `loops = v1-one-law-consumers` once 5e lands;
  until then, the pins that are actually true on harness main), and bootstrap
  *does* generate `.opencode/agent/` from persona sources (unmarked files are
  never overwritten — that is the remaining half of the old claim).
- Sweep the site for the names retired by PR 5 (rust-code-writer, rust-errors,
  ocaml-code-writer, rust-code-reviewer, rust-code-tester) and rust-team-lead; retarget
  or drop each. Where the site describes the catalog, the current truth is
  "code-writer + language books (rust, ocaml) + activity gates (code-review, testing,
  architecture)".
- Featured pills (site/templates/index.html:259-260 and any mirror) currently pill
  rust-code-writer and rust-code-reviewer. Mirror prompt-set decision 7:
  code-writer, rust, code-review, agent-harness, skill-evaluator.
- Do not add new claims. The site links out and owns no law.
- State in the PR body that this is the landing half of the plan item whose harness half
  was 5e (cite both).
```

---

## Review gauntlet (what I will check when each PR comes back)

- **5a**: extractor run twice, byte-identical; --check demonstrated red AND green AND
  disappeared-id; every rule id unique and <=3 lines (`check:` excluded); no code-writer /
  Fines photocopy in any reference; RULES.md outside references/; nothing deleted;
  deprecation markers carry measured bytes; `metadata.book: "true"` on rust; extractor ignores
  diataxis; RD / RF / RS-rename disclosed as a §3.4 refinement, not slipped in;
  rust/SKILL.md is ~2 KB, not a 6 KB axel photocopy; specialization.md +
  verification.md exist as contract refs (extractor skips them); no dying names
  in the rust book tree.
- **5b**: `git diff --stat` proves zero lines of scripts/extract-rules — this is the PR's
  entire point; OCaml topic set justified per-topic; RM is its own file, not stuffed
  into RF; no anti-patterns grab-bag; ids namespaced `ocaml/`; `metadata.book: "true"` on ocaml;
  docs/book-topics.md appended; specialization.md + verification.md present; no dying
  names in the ocaml book tree.
- **5c**: mapping table verified line by line against the books; gate cards <=2 KB measured
  AND `grep -rniE '\b(rust|ocaml)\b'`-clean; CP2 the only architecture edit; all three
  writers gone; featured is decision 7; README:78 retargeted; empty Rust Core / OCaml
  Core categories gone; shape B (brick-coder, agent-harness) uses the disclosed book,
  not `rust`; .opencode/ not in the grep; Claude-copy note in the body; acceptance
  greps re-run in front of me; gan-verdict untouched; both gate cards ship
  references/specialization.md + verification.md.
- **5d**: code-gan.json names no language; requires.book in schema AND enforced by
  verify-skill-refs (names-a-book demonstrated; empty-books is the 5e fixture, not
  a fail against the loops self-pin); book-ness is `metadata.book: "true"`, not RULES.md presence;
  persona Required Skills greps; voice grep for 'Rust' in .agents/agents/ actually
  clean (mandate, personality, clippy) AND the three verdict-format lines still
  carry `code-review:` / `testing:` / `architecture:`; brick personas say disclosed
  book, not rust; harness-parameters.md Language stack actually rewritten (the file
  v1 forgot); repo-wide grep pasted, not the hand-listed subset; README.md:9 pin
  moved with lockfile.toml.
- **5e**: smoke run locally with the ABSENCE assertions failing on a pre-5c tree;
  conductor window still 7,121; books present with committed RULES.md; empty-books
  fixture fails (reader iii home); verify-docs decision argued; the
  disclosure-vs-copy distinction documented; AGENTS.md and
  templates/harness/AGENTS.md.template retargeted (measured list, not
  chief-of-staff / dashboard-prompt); README pin loci moved with lockfile.toml.
- **5f**: double regen clean; .opencode/ dying-name grep zero; plan twins consistent;
  §7 row 5 and §2.4 both updated; every park discharged or re-parked with a home;
  the OCaml reversal recorded with its evidence; progress.md + features.json appended;
  all four pin loci read `v1-one-law-consumers`; §7 row 5 says drift-detectable.
- **5g**: :222 and :230 both retargeted; featured pills match decision 7.
- **Throughout**: no delta skills, no hand-copied Rules, no book name in a graph / gate
  card / persona, tags cut where the stack says (after pasted validation; no CI).

---

## Left to the human

Answers recorded on the lines they belong to; repeated here so the twins agree.
There is no generator for this twin. Both files are hand-maintained and must agree.
(The PR body that claimed the HTML was generated from the markdown was false — the
HTML had this section and the markdown did not.)

1. **`books = [...]` in 5e.** Keep it. Do not park to PR 6. Do not call it mechanical
   until the three readers in prompt-set decision 2 exist (schema + pre-flight +
   empty-books smoke fixture). Absence of `books` on the loops self-pin is not a
   failure. Multi-book: per-PBI, or stop and ask. Not first-listed.
2. **Tag names.** `v1-one-law` / `v1-one-law-consumers`. Keep them. Cut on the merge
   commit after the brief's own pasted validation has been re-run against that
   commit. There is no CI (decision 8). Never re-point.
3. **5c size.** Keep as one PR. Retargets and deletions are atomic. The two retarget
   shapes (Rust-subject vs disclosed-book) are separate instruction blocks, not a 5c′
   PR. Splitting 5c′ *after* deletions leaves dangling `rust-code-writer` names in
   live skills; splitting it *before* deletions makes the 5c acceptance grep
   unsatisfiable. brick-coder and agent-harness stay language-clean.
4. **Rule id scheme.** Keep bare `<TOPIC>-nn` in source, `<book>/<TOPIC>-nn` in the
   projection, append-only from birth. Do not park. Do not enforce the prefix list
   as a closed set. Registry is `docs/book-topics.md` alone; the card links to it (5a
   review). Extractor
   accepts unknown prefixes. `check:` does not count against the 3-line cap.
   `--check` fails on disappeared ids.
5. **No CI, no workflow in PR 5.** Tags cut after pasted validation. §7 row 5 is
   "drift-detectable, gated by review discipline". Decision 8.
6. **Contract references.** `specialization.md` + `verification.md` on every book
   and both gate cards. Extractor skips them. PR 4's axel card is the exemplar.
   Gate-card `specialization.md` is de-Rusted in 5c so the language-neutrality
   grep stays green. Books keep their language names.

Review measurements that were stale on this tree, recorded so they are not re-raised
as blockers:

- `just regen-agents` / `scripts/regen-agents` exist (landed 3c, skills#109). 5f runs
  the existing target; it does not invent one.
- This catalog's loops pin is `v1-cards` (landed #110 / 4b), not `v1-runtime-agents`.
  5f is a one-tag bump.
- There is no CI. loops and harness have no `.github/`; skills has one Pages-deploy
  workflow; this PR reports zero check runs. "After CI" was asserted without measuring.
- `gan-verdict/SKILL.md` is generic (`<gate>:`). Literal gate names live in the
  loops personas at reviewer-agent.md:27, tester-agent.md:28, architect-agent.md:27.
