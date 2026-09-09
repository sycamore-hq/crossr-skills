# PR 7 prompt set — Handoff packets, envelopes, AVRIL batching

Work item: [sycamore-hq/work#12](https://github.com/sycamore-hq/work/issues/12) (`pr7`).
Plan: `crossr-skills/docs/plans/gan-layer-separation-plan.md` §3.3 (envelope), §3.8 (packets),
§4 PR 7, §6 "Per-item BLESS", §7 row 7. Repos: `crossr-skills`, `crossr-loops`,
`crossr-harness` (decision 11 widens the card; the issue as filed names two).

**The one rule this stack exists to make mechanical:** a reviewer that is handed a set
blesses by skim. So every verdict names one id, every packet is audited by a script before
an LLM sees it, and every claim in every PR body is a pasted command output. Nothing in
this stack is accepted on an agent's word.

## Preconditions (measured 2026-09-09 on the trees, `origin/main`)

| repo | head | `skills` pin | `loops` pin | suite | verifiers |
|---|---|---|---|---|---|
| crossr-skills | `f4783ad` | `v1-gan-layers` | `v1-one-law-consumers` | 81 tests OK | `verify-docs` PASS |
| crossr-loops | `5448096` | `v1-one-law` | `v1-cards` | 48 tests OK | `graphs-verify` 5 OK · `verify-protocol` PASS (7 adversaries) |
| crossr-harness | `1d60943` | `v1-one-law` | `v1-one-law-consumers` | phase `gan-layer-separation` completed (`pr6c` last) | smoke pins hardcode `v1-one-law` / `v1-one-law-consumers` |

Tags on the remotes: skills `v1-one-law` → `507c509`; loops `v1-one-law-consumers` → `cea6e59`.
PR 6 landed on all three remotes (skills#125 `f4783ad`, loops#11 `5448096`, harness#10 `1d60943`)
and **cut no tag**.

### Measured finding the stack must absorb

```
$ CROSSR_SKILLS_PATH=<checkout of skills v1-one-law> ./scripts/verify-skill-refs   # in crossr-loops
  ✗ axel: skill 'plan-writer' has no .agents/skills/plan-writer/SKILL.md ... CROSSR_SKILLS_PATH=...
✗ verify-skill-refs FAILED (1 problem(s))

$ CROSSR_SKILLS_PATH=<checkout of skills main f4783ad> ./scripts/verify-skill-refs
✓ verify-skill-refs PASS (5 graphs, 18 check(s))
```

`graphs/axel.json` requires `plan-writer`; the pinned catalog tag predates it. Loops is green
only against an untagged `main`. PR 7 adds a second such reference (`gan-verdict` grows fields
loops will cite), so this stack cuts the tags PR 6 did not: `v1-packets` on skills after 7a,
`v1-packets-consumers` on loops after 7b. 7b moves the loops `skills` pin to `v1-packets`
and pastes `verify-skill-refs` green **against that tag**, not against `main`.

The same gap exists on harness: HARNESS-SPEC §6 says bootstrap installs `plan-audit` from
the skills pin, and the pin is `v1-one-law`, which has no `scripts/audit-plan`. Harness's
bootstrap block at `scripts/harness-bootstrap:404` is a no-op against its own pin today.
7c retires that.

The plan header (`gan-layer-separation-plan.md:3`) and the `### PR 6` heading still do not
say PR 6 landed. 7d records it.

Byte baselines (`wc -c`, the numbers the caps below are measured against):

| file | bytes |
|---|---|
| skills `gan-verdict/SKILL.md` | 1,132 |
| loops `avril/SKILL.md` | 4,984 (§7 row 4, frozen) |
| loops `axel/SKILL.md` | 5,693 |
| loops `product-owner-agent.md` / `qa-architect-agent.md` / `visionary-cto-agent.md` | 1,839 / 2,067 / 2,182 |
| loops `axel-conductor-agent.md` / `avril-conductor-agent.md` | 2,713 / 2,555 |

---

## Stack (four PRs, merge order is stack order)

```
7a  skills   gan-verdict: inbound packet fields + per-item verdict rule;
             scripts/audit-packet (brief + verdict modes); test/test_pr7.py
             → cut skills tag v1-packets on the merge commit
7b  loops    skills pin → v1-packets; graph node `batch`; verify-protocol batch rule;
             avril batch review + per-item tokens + set-size log; PO/QA/CTO personas;
             axel packet ritual + references/handoff-packet.md; test/test_pr7.py
             → cut loops tag v1-packets-consumers on the merge commit
7c  harness  pins → v1-packets / v1-packets-consumers at every locus; bootstrap
             installs audit-packet + `packet-audit` next to audit-plan; HARNESS-SPEC
             §6 packet gate + §12 scratch-path disclosure; smoke; test/test_pr7.py
             → no tag
7d  skills   loops pin → v1-packets-consumers; just regen-agents ×2; plan record
             (PR 6 + PR 7 landed, §7 row 7 measured, phase closed); tracker rows
             → no tag
```

Tags are immutable once cut. Cut on the merge commit, after the brief's own pasted validation
has been re-run against that commit. There is no CI (plan decision 8). Never re-point a tag.

---

## Decisions settled BEFORE dispatch

Numbered so a brief can cite them. Each was a default; 1, 9, 11, and 13 were confirmed by the
human on 2026-09-09. None is open.

1. **A packet is a file, or it is not audited.** §3.8 says "conductor sends brief + envelope
   spec". A prompt string cannot be gated mechanically; a file can. The conductor writes the
   packet to the **packet scratch path**, runs `audit-packet brief` on it, and only a green
   packet is delegated. The path is a harness-disclosed parameter (HARNESS-SPEC §12 owns
   paths, as it does for the plan artifact), with a **portable fallback outside the repo
   tree**: `${TMPDIR:-/tmp}/crossr-packets/<pbi-id>/phase-<k>.<gate>.packet.md`. Never
   under the repo, never under `.pinto/` (§2.10), never committed, never gitignored because
   there is nothing in the tree to ignore. Packets are ephemeral: the 20-line Completion
   Record is the memory (§3.8 last paragraph); a committed packet would be a second memory
   carrying a full diff.
2. **Envelope out and packet in are both `gan-verdict`.** Decision #4 put the envelope field
   schema there. The inbound packet field schema is the same kind of thing (a fixed menu the
   conductor selects from) and gets the same home. Still a field list, not law: names and
   types only. §3.3 "cap it at a field list" holds; the byte cap below enforces it.
3. **Per-item verdict is protocol, not conductor prose.** `BLESS <id>` / `REJECT <id>` one
   line per id is a `gan-verdict` rule (7a). AVRIL cites it (7b). The sentence
   `A bare BLESS over a set is not a verdict.` is a **verbatim constant**: `verify-protocol`
   greps for it in every `batch: true` persona, and loops tests grep for it on the avril
   card. Paraphrase fails the gate on purpose.
4. **Batching is declared in topology.** `graphs/schema.json` node gains
   `"batch": {"type": "boolean"}`; `avril.json`'s three adversaries set it. `verify-protocol`
   enforces the per-item declaration only on `batch: true` nodes. AXEL's single-phase gates
   keep `<gate>: BLESS | REJECT` and are untouched. No new graph nodes, no edge changes: a
   packet audit before a delegation is ritual on the card, the same way pre-flight is.
5. **Prior verdicts are one-liners, enforced by length and shape.** A prior verdict line in
   a packet must match `^- \S+ (BLESS|REJECT)(: .{1,140})?$`. Longer is prose. Prose is what
   the packet exists to keep out.
6. **The diff rides inside the packet, fenced, and the fence is grammar-checked.** A
   ```` ```diff ```` fence whose every line matches unified-diff line grammar
   (`diff --git`, `index`, `---`, `+++`, `@@`, or a first char in `+-\ ` or empty). Anything
   else in the fence fails. Or `- ref: <path-or-range>` instead. Either satisfies
   `## Diff`; both is fine; neither fails.
7. **Forbidden content is a fixed list, not a judgment.** Fail on: a SKILL.md frontmatter
   (`^---$` followed within two lines by `^name: `), `<!DOCTYPE` / `<html`, a JSON board
   dump (a line starting with `{` or `[` outside a fence, or `"tasks":` / `"items":`
   anywhere), any `## ` heading not in the packet grammar, more than `--max-lines`
   (default 200) non-diff lines. These are the four "never" items of §3.8, one check each.
8. **REJECT loops the item, not the siblings — and that is already the card's rule.**
   `avril/SKILL.md` "Material edit after any BLESS invalidates all three blessings for that
   item" is per item today. 7b adds the batch delegation shape and the guard; it does not
   rewrite the rejection loop.
9. **No batch-size cap; instrument instead.** The plan sets none. The per-item token is the
   guard, and a cap would be a number with nothing measured behind it (the same posture §8
   open question 1 takes on the 30% quota). So 7b makes the skim signal observable: the
   Blessed Backlog Summary's blessing log records the **set size per cycle** and the per-item
   verdicts, one line per cycle (`- cycle 2: set 7 · PO 7/0 · QA 6/1 · CTO 6/0`). If the
   REJECT rate falls as set size grows, that is the evidence a cap needs. Adding a cap later
   is one avril line plus `audit-packet verdict --max-items N`, mechanical either way.
10. **Card byte caps are deltas, measured.** `avril/SKILL.md` ≤ 5,400 B (4,984 + ≤ 416),
    `axel/SKILL.md` ≤ 6,100 B (5,693 + ≤ 407), `gan-verdict/SKILL.md` ≤ 2,048 B. §7 row 4
    is frozen (decision #12): 7d appends a **new** row-7 line and does not touch row 4.
    Everything that is a template or an explanation goes in `references/`.
11. **Harness is in the stack, as 7c.** The issue as filed names loops and skills. But
    without the harness half no consumer repo can run the packet ritual: bootstrap must
    install `audit-packet` (as it does `audit-plan`), §12 must disclose the scratch path,
    and the pins must reach the two new tags. Landed-but-not-runnable is not done. So
    `work.json` `pr7.repos` gains `crossr-harness` (one field; `just project-roadmap`
    relabels the issue), and 7c is the harness brief. This is the PR 6 shape (one card,
    three remotes), not the PR 5 shape (`pr5e` as its own card). No new ledger card.
12. **Scripts are Python 3 stdlib, in the `audit-plan` shape.** Pure calculations, one
    action (read the file), exit 0 pass / 1 fail / 2 usage, failure lines human-readable,
    tests load the script by path with `SourceFileLoader` exactly as `test/test_pr6.py` does.
    Rust is the house first choice for implementation; this catalog's scripts are Python
    and the harness bootstrap copies them as-is, so this one matches the existing standard.
13. **The phase closes in 7d.** PR 7 is the last unit in §4. §5 "also worth doing" is not a
    set of units (the work ledger's plan audit already says so) and §7's two acceptance
    conditions are a demonstration and a trend, not PRs. House precedent closes a phase when
    its named units land (`gan-close-4b`; the `dashboard-phase` miscount was a phase left
    open). The header word becomes `complete` with one clause that acceptance condition 1
    (an Elm or Melange AXEL run) is undemonstrated and condition 2 is a running measure. An
    Elm run or a §5 item gets its own card or phase when someone wants it.

---

## Shared guardrails (paste into every brief verbatim)

```
GUARDRAILS (crossr v2 review standard — violations get the PR rejected):
- Read docs/plans/gan-layer-separation-plan.md (§3.3, §3.8, §4 PR 7, §6, §7 row 7 govern
  this work), docs/plans/pr7-handoff-packets-prompt-set.md (decisions 1–13), and AGENTS.md
  in the repo you are editing, before writing anything.
- Every acceptance criterion in your brief has a command and an expected result next to
  it. Run every one. Paste every output in the PR body under a "## Validation" heading,
  in the order the brief lists them. A criterion without pasted output is unmet.
- Red demonstrations are required where the brief says "demonstrate red": show the check
  failing on the bad input, then passing on the good one. A gate that has never been seen
  red is not known to gate.
- Enumerate EVERY protected-law edit in the PR body, one numbered item each, with the
  exact before/after text (gan-verdict, avril/SKILL.md, axel/SKILL.md, personas, graphs,
  schema, HARNESS-SPEC). Undisclosed law edits are an automatic REJECT (#107 precedent).
- The three AXEL verdict-format lines are untouchable:
    reviewer-agent.md   **Verdict format** (per `gan-verdict`): `code-review: BLESS | REJECT`
    tester-agent.md     **Verdict format** (per `gan-verdict`): `testing: BLESS | REJECT`
    architect-agent.md  **Verdict format** (per `gan-verdict`): `architecture: BLESS | REJECT`
  verify-protocol does not check the gate-name prefix; you do. Paste the grep.
- NO BOOK NAME in graphs/, gate cards, gan-verdict, or role personas (PR 5 standard).
- Never hand-write generated output: graphs/index.html only via verify-graphs --html;
  .opencode/agent/ only via just regen-agents; RULES.md only via extract-rules. Every
  generator is idempotent: run it twice, git status clean.
- Byte caps are measured with wc -c on the tree and pasted. Never estimated.
- Do not touch progress.md / MIGRATION history / features.json except the tracker
  append your brief names. Nothing outside the declared file list. Scope creep is REJECT.
- Tags are immutable once cut. Cut on the merge commit after re-running the pasted
  validation against that commit. No CI (decision 8). The PR body carries the stack line
  (what merged before, what tag is cut, what comes next).
- Verdict tokens stay exactly BLESS / REJECT. No new token. Per-item is a line shape,
  not a new vocabulary.
- Packets never land in a repo tree. The scratch path is disclosed or the temp-dir
  fallback (decision 1). A packet path under the repo is a REJECT.
- One PR, reviewable in < 10 minutes. If the diff grows past that, stop and split; do
  not ship a long PR with a long apology.
```

---

## Brief 7a — skills: `gan-verdict` fields, `audit-packet`, tests

```
You are implementing crossr v2 PR 7a in sycamore-hq/crossr-skills, on a branch off
main at or after f4783ad (pr6a landed). Work item: sycamore-hq/work#12.

[paste GUARDRAILS]

GOAL: the handoff packet and the batch verdict become artifacts a script can reject.
§3.8 packet fields land in gan-verdict as a field list; the per-item verdict line becomes
protocol; scripts/audit-packet is the mechanical gate that runs before any adversary
reads a packet and before any conductor reads a verdict. Decisions 1, 2, 3, 5, 6, 7, 12.

FILES (exhaustive — anything else is scope creep):
  .agents/skills/gan-verdict/SKILL.md                  edit (cap 2,048 B)
  .agents/skills/gan-verdict/references/handoff-packet.md   NEW — the packet grammar
  .agents/skills/gan-verdict/references/batch-verdict.md    NEW — the per-item grammar
  scripts/audit-packet                                 NEW (executable)
  justfile                                             + packet-audit MODE FILE target
  AGENTS.md                                            one line under Project Commands
  test/test_pr7.py                                     NEW
  features.json, progress.md                           pr7a row + section (append only)

CHANGES:

1. gan-verdict/SKILL.md — append, do not rewrite. Existing items 1–7 keep their numbers
   and their text byte-for-byte (paste `git diff` proving items 1–7 are context lines).
   Add:
   8. Handoff packet — inbound field schema (conductor fills; adversary receives nothing
      else): phase id · "k of n" · gate · file list · diff (fenced, or a ref) · AC subset
      claimed · claim ids covered · prior verdicts as one-liners · envelope (item 5).
      Never: a sibling SKILL.md, a previous-phase essay, a whole-board dump, dashboard
      HTML. Grammar: `references/handoff-packet.md`. Gate: `audit-packet brief`. Lives
      at the disclosed packet scratch path, never in the tree.
   9. Set review — one verdict line per id: `BLESS <id>` | `REJECT <id> — <blockers>`.
      A bare BLESS over a set is not a verdict. Gate: `audit-packet verdict --items`.
   10. Adding a packet field means changing this file — never a conductor card (same rule
      as item 7).
   The sentence "A bare BLESS over a set is not a verdict." appears verbatim (decision 3).
   wc -c ≤ 2,048 after the edit. Paste it.

2. references/handoff-packet.md — the grammar, with one complete example. Exactly this
   shape (audit-packet parses it; do not improvise a second shape):

     # Packet: <phase-id>
     - k of n: <k> of <n>
     - gate: <gate-name>
     ## Files
     - <path>            (≥ 1)
     ## Diff
     - ref: <path-or-range>     and/or a ```diff fence (decision 6)
     ## AC
     - AC-nn: <text>     (≥ 1)
     ## Claims           (optional)
     - C-nn
     ## Prior verdicts   (may be empty; each line per decision 5)
     - <gate> BLESS
     - <gate> REJECT: <≤140 chars>
     ## Envelope         (items from gan-verdict item 5, `- name: value`)
     - findings shape: one-liners
     - max length: 40 lines
     - citations: file:line

   No other `## ` heading is legal. Prose outside list items is illegal outside the fence.
   State the location rule once: disclosed scratch path, fallback
   `${TMPDIR:-/tmp}/crossr-packets/<pbi-id>/phase-<k>.<gate>.packet.md`, never committed.

3. references/batch-verdict.md — the per-item grammar and an example with one BLESS and
   one REJECT. Single-gate form for AXEL (`<gate>: BLESS | REJECT`, exactly one line) and
   set form for AVRIL (`BLESS <id> — …` / `REJECT <id> — …`, exactly one line per id;
   REJECT needs the ` — ` blockers). State the two failure classes by name: `silence`
   (an id with no line) and `blanket` (a token with no id, or `all`).

4. scripts/audit-packet — two modes, decision 12 shape:
     audit-packet brief [--max-lines N] <packet.md>
     audit-packet verdict (--gate <name> | --items id1,id2,...) <verdict.md>
   brief fails on (one failure line each, all of them, not first-only):
     - missing `# Packet:` heading; missing/malformed `- k of n:` (k ≤ n, both ints);
       missing `- gate:`
     - missing required section (Files, Diff, AC, Prior verdicts, Envelope); unknown
       `## ` heading (this is the prior-phase-essay catch — §3.8 "never" #2)
     - Files empty; AC empty or a line not matching `^- AC-\d+: .+$`
     - Diff satisfied by neither `- ref:` nor a fence; a fence line outside the unified-
       diff grammar (decision 6)
     - a prior-verdict line not matching decision 5's regex
     - forbidden content per decision 7: SKILL.md frontmatter (§3.8 "never" #1), board
       dump (#3), dashboard HTML (#4), non-diff line count > --max-lines
     - Envelope item that is not `- <name>: <value>` or whose name is not one of
       gan-verdict item 5's six names (lower-case, spaces allowed)
   verdict --gate G fails on: zero or more than one line matching `^G: (BLESS|REJECT)`;
     REJECT without a following `— ` or `: ` blockers text; any line `^(BLESS|REJECT)$`
     or `^(BLESS|REJECT) (all|everything)`.
   verdict --items fails on: an id with zero lines (silence) or ≥ 2 lines; any line
     matching `^(BLESS|REJECT)( all| everything)?\s*$` (blanket); a `REJECT <id>` line
     without ` — `; a verdict line whose id is not in --items (stray).
   Fenced blocks other than ```diff are ignored for grammar but still scanned for
   forbidden content (a pasted SKILL.md inside a fence is still a pasted SKILL.md).
   The script never resolves the scratch path; it takes a file argument. Location is
   the conductor's business (decision 1), grammar is this script's.

5. justfile: `packet-audit MODE FILE:` → `@./scripts/audit-packet {{MODE}} {{FILE}}`
   next to plan-audit. Document the two modes in the AGENTS.md "Project Commands" list
   (one line; this is the only AGENTS.md edit).

6. test/test_pr7.py — the test_pr6.py pattern (module docstring names the brief and the
   work item; script loaded by SourceFileLoader; Calculations pure, LiveTree reads the
   tree). Required assertions, each its own test:
     - a good packet (the reference example, verbatim) passes with []
     - each failure class above produces a failure line naming it — one test per bullet
       in CHANGES 4 (that is ~16 tests; do not merge them)
     - the three §3.8 "never" fixtures are separate tests named for the never:
       sibling SKILL.md pasted (frontmatter), board JSON pasted, dashboard HTML pasted
     - a prior verdict of 141 chars fails; 140 passes
     - a ```diff fence containing a prose line fails; a well-formed fence passes
     - verdict --gate: one line passes; two lines fail; bare `BLESS` fails
     - verdict --items a,b: `BLESS a — ok` + `REJECT b — why` passes; missing b fails
       (silence); `BLESS` alone fails (blanket); `BLESS a` twice fails; `BLESS c` fails
       (stray)
     - LiveTree: gan-verdict/SKILL.md ≤ 2,048 B; contains the decision-3 sentence
       verbatim; items 1–7 unchanged against the literal text of f4783ad (embed the
       seven lines in the test); references/handoff-packet.md example passes
       audit-packet brief when extracted from its fence; the fallback path string in
       references/handoff-packet.md starts with `${TMPDIR:-/tmp}/` (a packet path under
       the tree is the failure this guards).

7. features.json: gan-layer-separation gets a `pr7a` row, status completed, features
   ["gan-verdict-packet-fields", "per-item-verdict", "audit-packet-script"].
   progress.md: `### gan-layer-separation — PR 7a (COMPLETED)` in the pr6a shape,
   with a Verification Status block listing the commands below.

VALIDATE (paste all, in this order):
  wc -c .agents/skills/gan-verdict/SKILL.md                               → ≤ 2048
  grep -c 'A bare BLESS over a set is not a verdict\.' .agents/skills/gan-verdict/SKILL.md → 1
  git diff main -- .agents/skills/gan-verdict/SKILL.md | grep '^-' | grep -v '^---' → (empty: nothing removed)
  ./scripts/audit-packet brief <the reference example extracted to a file>; echo $?  → 0
  three red demos: a packet with a pasted SKILL.md frontmatter, one with `"tasks": [`,
    one with `<html`; each → exit 1 and a failure line naming the never
  ./scripts/audit-packet verdict --items T-1,T-2 <file with a bare BLESS>; echo $? → 1 "blanket"
  python3 -m unittest discover -s test -v                                  → OK, count ≥ 81 + your tests
  just harness-validate                                                    → PASS (docs-verify, claude-skills-check soft, rules-check, features.json)
  grep -rnE '\b(rust|ocaml)\b' .agents/skills/gan-verdict/                → 0 hits
Stack line for the body: "7a of 4. Nothing merges before. Cut skills tag v1-packets on
the merge commit after re-running this block on it. 7b (loops) is next."
```

---

## Brief 7b — loops: batch topology, per-item personas, AXEL packet ritual

```
You are implementing crossr v2 PR 7b in sycamore-hq/crossr-loops, on a branch off main at
or after 5448096 (pr6b landed). Work item: sycamore-hq/work#12.
Precondition: skills tag v1-packets exists. `git ls-remote --tags
https://github.com/sycamore-hq/crossr-skills.git v1-packets` — paste the peeled SHA in
the PR body. If it does not exist, stop; 7a is not merged.

[paste GUARDRAILS]

GOAL: AVRIL reviews the set with one verdict line per id and never a blanket token;
REJECT loops the item, not the siblings; the set size is logged so a cap can be a
measured decision later; AXEL delegates only audited packets and drops review prose
after commit. Decisions 1, 3, 4, 5, 8, 9, 10.

FILES (exhaustive):
  lockfile.toml, README.md:9                           skills pin → v1-packets (both loci)
  graphs/schema.json                                   node `batch` boolean
  graphs/avril.json                                    `"batch": true` on po, qa, cto
  graphs/index.html                                    regenerated only
  scripts/verify-graphs                                ALLOWED_NODE += "batch"
  scripts/verify-protocol                              batch rule (below)
  .agents/skills/avril/SKILL.md                        batch delegation shape (cap 5,400 B)
  .agents/skills/avril/references/batch-review.md      NEW
  .agents/skills/avril/references/blessed-backlog-summary.md   set-size log line
  .agents/agents/product-owner-agent.md, qa-architect-agent.md, visionary-cto-agent.md
  .agents/agents/avril-conductor-agent.md              steps 5–6
  .agents/skills/axel/SKILL.md                         packet ritual (cap 6,100 B)
  .agents/skills/axel/references/handoff-packet.md     NEW (AXEL-side template)
  .agents/skills/axel/references/harness-parameters.md one line: packet scratch path
  .agents/skills/axel/references/completion-record.md  retention line
  .agents/agents/axel-conductor-agent.md               step 8
  book/src/pipeline/avril.md, axel.md                  one paragraph each
  templates/harness/opencode/command/avril.md          `review <ids>` hint line
  test/test_pr7.py                                     NEW
  features.json, progress.md                           pr7b row + section

CHANGES:

1. Pin. lockfile.toml `skills = "v1-packets"`; README.md:9 says the same. Two loci, one
   commit. verify-skill-refs must be pasted green against a checkout of THAT TAG
   (CROSSR_SKILLS_PATH=<clone at v1-packets>), which also retires the measured PR 6
   gap (plan-writer unresolved at v1-one-law). Paste the failing run at v1-one-law and
   the passing run at v1-packets side by side. This is the PR's first commit.

2. Schema + graph. schema.json node properties gain
   "batch": {"type": "boolean", "description": "Adversary reviews a set; one verdict
   line per id (gan-verdict item 9)."}. verify-graphs ALLOWED_NODE gains "batch".
   avril.json: po, qa, cto nodes get "batch": true. No node added, no edge touched —
   paste `git diff graphs/avril.json` showing only the three inserted keys.
   graphs/index.html via ./scripts/verify-graphs --html only; run twice, clean.

3. verify-protocol batch rule (decision 3/4). For every adversary node with
   `batch: true`, the persona file must contain, verbatim:
     `BLESS <id>`  and  `REJECT <id>`  and
     the sentence  A bare BLESS over a set is not a verdict.
   Failure text: "<graph>: batch adversary <nid> persona <name> lacks per-item verdict
   declaration: <which>". Nodes without `batch` are unchanged. Also assert that no
   `batch: true` node's persona declares a `<gate>: BLESS` single-gate format (that is
   the AXEL shape; a batch persona carrying both is two protocols on one card).
   Demonstrate red: temporarily set batch: true on code-gan.json's reviewer node
   (whose persona has no `BLESS <id>`), paste the failure, revert. Do not commit the
   fixture; the unit test carries it.

4. avril/SKILL.md (delta ≤ 416 B, measured). In "AVRIL Method" item 2, the adversary
   line becomes set-wise: each adversary reviews the active set in one delegation, fixed
   order preserved (PO the set → QA the set → CTO the set). One verdict line per id.
   Then, verbatim: A bare BLESS over a set is not a verdict. The conductor runs the
   verdict gate (`audit-packet verdict --items <ids>`, installed by the harness from the
   skills pin) before reading a reply; red → re-delegate. `REJECT <id>` loops that id
   alone; unchanged siblings keep their BLESS (decision 8 — item 3 and the Ruthless
   Checklist's "Material edit … for that item" line already say per-item; do not
   rewrite them, cite them). Details → references/batch-review.md. The Ruthless
   Checklist gains one line: "Every verdict names one id; no bare token over a set."
   No batch-size cap and no word about one (decision 9).

5. references/batch-review.md: the delegation shape (persona + gate/avril card + the
   set + envelope last), the reply grammar (link gan-verdict references/batch-verdict.md
   by name — do not copy it: one law, one home), the per-item loop with a worked
   three-item example where item 2 is REJECTed and items 1 and 3 keep their BLESS, the
   material-edit rule, and decision 9 verbatim: no cap; the set-size log is the
   instrument; a cap is a later measured decision.

6. references/blessed-backlog-summary.md: the `## Blessing log` block gains one line
   per cycle in this exact shape, before the per-id lines:
     - cycle <n>: set <size> · PO <bless>/<reject> · QA <bless>/<reject> · CTO <bless>/<reject>
   This is the decision-9 instrument. The per-id lines (`- <id>: PO BLESS | QA BLESS |
   CTO BLESS`) stay as they are.

7. PO / QA / CTO personas. Each already ends "every reviewed item" with
   `BLESS <id> — …` / `REJECT <id> — …`. Add, in the Invocation Protocol, one item:
   "When given a set: one line per id, in the set's order. A bare BLESS over a set is
   not a verdict." (verbatim sentence). Nothing else on these files. Do not touch
   `code-writer` in their Required Skills — out of scope, park it in the PR body.

8. avril-conductor-agent.md steps 5–6: delegate the set, run the verdict gate, loop the
   rejected id only, write the cycle line to the blessing log. Keep the One-Sentence
   Mandate byte-identical (paste grep).

9. axel/SKILL.md §4 (delta ≤ 407 B). Before each adversary delegation: write the
   handoff packet (references/handoff-packet.md) to the disclosed packet scratch path,
   run `audit-packet brief` (mechanical, zero tokens), red → fix the packet, green →
   delegate persona + gate card + RULES.md + packet, envelope last. On reply run
   `audit-packet verdict --gate <gate>`; keep the one-liner as the next packet's prior
   verdict. After commit: keep the Completion Record, drop the review prose. Never
   paste a sibling SKILL.md, a previous-phase essay, the whole board, or dashboard
   HTML. Orchestration rules gain: "Packets are audited before an adversary reads
   them; prose is dropped after commit."

10. axel/references/handoff-packet.md: the AXEL fill-in of gan-verdict's grammar —
    which field comes from where (phase id and k of n from the blessed plan's Phases,
    file list and diff from `git diff --stat` / `git diff` of this phase, AC subset and
    claim ids from the plan, prior verdicts from this phase's earlier gates, envelope
    from item 5). Link, do not copy, the gan-verdict grammar.
    harness-parameters.md gains one line in its disclosed-parameters list: "Packet
    scratch path — disclosed by the harness (HARNESS-SPEC §12); fallback
    `${TMPDIR:-/tmp}/crossr-packets/<pbi-id>/`; never inside the repo, never
    committed." That line is the only edit to that file.

11. completion-record.md: one line under `## Phases`: "- retained: this record; review
    prose dropped (§3.8)".

12. axel-conductor-agent.md step 8: insert the packet audit before Tester and Reviewer
    and the verdict audit after each. Mandate byte-identical (paste grep).

13. Book pages and the /avril command: one paragraph in avril.md (set review, per-item
    tokens, sibling BLESS survives, cycle line in the log), one in axel.md (packet in,
    audited; prose out after commit); avril.md command template `review <ids>` route
    gains "(one verdict line per id)". No other template edit.

14. test/test_pr7.py in the test_pr6.py shape. Required:
    Calculations (pure, on dict/str inputs):
      - batch_nodes(graph) returns the ids with batch: true; avril → {po, qa, cto}
      - persona_declares_per_item(text) true iff `BLESS <id>`, `REJECT <id>`, and the
        decision-3 sentence are all present; false for each one missing (3 tests)
      - a batch persona that also carries `<gate>: BLESS` is flagged
      - cycle_line(n, size, po, qa, cto) renders the decision-9 shape; a parser round-
        trips it (the log line is data, so it gets a parser)
    LiveTree:
      - schema.json allows `batch`; verify-graphs ALLOWED_NODE contains "batch"
      - avril.json: exactly po, qa, cto are batch; no code-gan / axel node is batch
      - each batch persona passes persona_declares_per_item
      - avril card contains the decision-3 sentence verbatim, "one verdict line per id"
        (case-insensitive), "audit-packet verdict", and "siblings"; and does NOT match
        `(?i)max(imum)? (batch|set) size|at most \d+ (items|PBIs)` (decision 9)
      - blessed-backlog-summary.md contains the literal `- cycle <n>: set <size>`
      - avril card ≤ 5,400 B; axel card ≤ 6,100 B (wc -c numbers in the assertion
        message)
      - axel card contains "audit-packet brief", "audit-packet verdict", "scratch",
        "drop" + "review prose", and, negatively, none of the strings "paste the
        board", "pinto list --json" (this is a card, not a dump)
      - harness-parameters.md names the packet scratch path and the `${TMPDIR:-/tmp}/`
        fallback; no packet path in any loops file matches `^docs/|^\.pinto/`
      - references/handoff-packet.md (axel) names every gan-verdict item-8 field by
        its name (phase id, k of n, gate, files, diff, AC, claims, prior verdicts,
        envelope) — assert each token
      - completion-record.md contains "review prose dropped"
      - both conductor mandates unchanged against their literal 5448096 text (embed)
      - the three AXEL verdict-format lines unchanged (embed all three literally)
      - verify-protocol red fixture: a temp graph with a batch adversary whose persona
        lacks the sentence → the batch check reports it (call the script's functions,
        do not shell out)

15. features.json: gan-layer-separation `pr7b` row, status completed, features
    ["batch-topology", "verify-protocol-batch", "avril-set-review", "set-size-log",
    "axel-packet-ritual"]. progress.md: PR 7b (COMPLETED) section with Verification
    Status.

VALIDATE (paste all, in order):
  git ls-remote --tags https://github.com/sycamore-hq/crossr-skills.git v1-packets     → SHA
  CROSSR_SKILLS_PATH=<v1-one-law checkout> ./scripts/verify-skill-refs                 → FAIL (plan-writer) — the before
  CROSSR_SKILLS_PATH=<v1-packets checkout> ./scripts/verify-skill-refs                 → PASS — the after
  ./scripts/verify-graphs; ./scripts/verify-graphs --html; git status --short graphs/  → 5 graphs OK; clean after second run
  ./scripts/verify-protocol                                                             → PASS, ≥ 7 adversaries, batch lines for po/qa/cto
  red demo: batch: true on code-gan reviewer → verify-protocol FAIL naming reviewer-agent; reverted
  wc -c .agents/skills/avril/SKILL.md .agents/skills/axel/SKILL.md                      → ≤ 5400, ≤ 6100
  grep -c 'A bare BLESS over a set is not a verdict\.' .agents/skills/avril/SKILL.md .agents/agents/{product-owner,qa-architect,visionary-cto}-agent.md → 1 each
  grep -n 'cycle <n>: set <size>' .agents/skills/avril/references/blessed-backlog-summary.md → 1 line
  grep -n 'Verdict format' .agents/agents/{reviewer,tester,architect}-agent.md          → the three literal lines
  git diff main -- .agents/agents/{avril,axel}-conductor-agent.md | grep -A1 'One-Sentence Mandate' → (empty)
  grep -rnE '\b(rust|ocaml)\b' graphs/ .agents/agents/ .agents/skills/avril .agents/skills/axel → 0 hits
  grep -rnE 'packet.*(docs/|\.pinto/)' .agents/ book/ templates/                        → 0 hits
  python3 -m unittest discover -s test -v                                               → OK, ≥ 48 + your tests
Stack line: "7b of 4. 7a merged as <sha>, skills tag v1-packets → <sha>. Cut loops tag
v1-packets-consumers on the merge commit after re-running this block on it. 7c
(harness) is next."
```

---

## Brief 7c — harness: pins, `audit-packet` install, §6 + §12, smoke

```
You are implementing crossr v2 PR 7c in sycamore-hq/crossr-harness, on a branch off main
at or after 1d60943 (pr6c landed). Work item: sycamore-hq/work#12.
Precondition: skills tag v1-packets AND loops tag v1-packets-consumers exist; paste both
peeled SHAs. If either is missing, stop.

[paste GUARDRAILS]

GOAL: a consumer repo bootstrapped from the pins can run the packet ritual. Pins reach
the tags that carry it, bootstrap installs the gate, the spec discloses the scratch path
and names the packet audit in the diff gate. Decisions 1, 11.

FILES (exhaustive):
  lockfile.toml                                        skills = v1-packets; loops = v1-packets-consumers
  README.md:7, :22, :31, :32                           the same two tags
  test/harness-bootstrap-smoke.sh:25-26, :69, :100     the same two tags
  scripts/harness-bootstrap                            audit-packet block after the audit-plan block (:404–:415)
  HARNESS-SPEC.md                                      §6 diff gate line; §12 disclosure line
  templates/harness/AGENTS.md.template                 one line naming `just packet-audit`
  test/test_pr7.py                                     NEW
  test/harness-bootstrap-smoke.sh                      audit-packet install assertions
  features.json, progress.md                           pr7c row + section

CHANGES:

1. Pins. Every locus above moves in one commit. Then grep the tree for the old tags
   outside progress.md / MIGRATION.md and paste zero hits. The smoke script hardcodes
   the pins three times; all three move, or the smoke lies.

2. Bootstrap. Mirror the audit-plan block exactly (same if/cp/chmod/echo shape, same
   "kept existing" branch, same justfile append guard):
     if [ -f "$SKILLS_TREE/scripts/audit-packet" ]; then … scripts/audit-packet …
       justfile: packet-audit MODE FILE:\n    @./scripts/audit-packet {{MODE}} {{FILE}}
   Nothing else in the script changes. Paste `git diff scripts/harness-bootstrap` — it
   must be one inserted block.

3. HARNESS-SPEC.md. §6 "Diff gate" gains one numbered line before `testing`: "0. Packet
   audit (`just packet-audit brief <packet>`, installed by bootstrap from the skills pin)
   on every adversary delegation; `packet-audit verdict` on every reply. Red never
   reaches a persona." §12's disclosed list gains: "- Packet scratch path (default
   `${TMPDIR:-/tmp}/crossr-packets/<pbi-id>/`; never inside the repo, never
   committed)". Two lines. Paste the diff; it is the whole protected-law edit.

4. AGENTS.md.template: one line under the just targets naming `just packet-audit`.

5. Smoke. After the existing audit-plan assertions (or next to where bootstrap output
   is checked), assert: `scripts/audit-packet` exists and is executable in the
   bootstrapped target; the justfile carries `^packet-audit`; running it twice keeps
   the file (the "kept existing" branch prints). Demonstrate red: run the smoke against
   a skills checkout at v1-one-law (no audit-packet) and paste the failing line, then
   green at v1-packets.

6. test/test_pr7.py (test_pr6.py shape, section() helper reused): §6 names `packet-audit
   brief` and `packet-audit verdict`; §12 names "Packet scratch path" and the
   `${TMPDIR:-/tmp}/` fallback; no line in HARNESS-SPEC places a packet under `docs/`
   or `.pinto/`; lockfile pins are the two tags; the bootstrap script contains the
   audit-packet block (assert the four literal lines).

7. features.json: gan-layer-separation `pr7c` row, completed (the phase is already
   completed on this remote; a completed phase may gain a completed child — test_
   features_phase only guards the reverse). progress.md: PR 7c (COMPLETED) section.

VALIDATE (paste all, in order):
  git ls-remote --tags https://github.com/sycamore-hq/crossr-skills.git v1-packets           → SHA
  git ls-remote --tags https://github.com/sycamore-hq/crossr-loops.git v1-packets-consumers  → SHA
  grep -rn 'v1-one-law' --exclude-dir=.git --exclude=progress.md --exclude=MIGRATION.md .    → 0 hits
  git diff main -- scripts/harness-bootstrap | grep -c '^+'                                 → the block's line count, nothing removed
  CROSSR_SKILLS_PATH=<v1-one-law checkout> ./test/harness-bootstrap-smoke.sh                → FAIL on audit-packet — the before
  CROSSR_SKILLS_PATH=<v1-packets checkout> CROSSR_LOOPS_PATH=<v1-packets-consumers checkout> ./test/harness-bootstrap-smoke.sh → PASS
  just test                                                                                  → OK (all four test files + smoke)
  grep -n 'Packet scratch path\|packet-audit' HARNESS-SPEC.md                                → §6 line + §12 line
Stack line: "7c of 4. 7b merged as <sha>, loops tag v1-packets-consumers → <sha>. No tag
cut here. 7d (skills closer) is next."
```

---

## Brief 7d — skills: pin bump, regen, plan record, phase close

```
You are implementing crossr v2 PR 7d in sycamore-hq/crossr-skills, on a branch off main
at or after the 7a merge. Work item: sycamore-hq/work#12.
Precondition: loops tag v1-packets-consumers exists and harness 7c is merged; paste the
peeled SHA and the harness merge SHA. If either is missing, stop.

[paste GUARDRAILS]

GOAL: the catalog consumes the loops it just made possible, the plan record stops lying
about PR 6, and the phase closes. Decisions 10, 13.

FILES (exhaustive):
  lockfile.toml, README.md:24, AGENTS.md:53            loops pin → v1-packets-consumers (the loci test_pr5f.py reads: lockfile, README "Current pins", AGENTS "Consumer pins" and its "are in the `<tag>` pin" sentence)
  .agents/agents/*.md (loop-owned copies), .opencode/agent/*   regenerated only
  docs/plans/gan-layer-separation-plan.md + .html      record (below)
  docs/plans/pr7-handoff-packets-prompt-set.md         Status table (below)
  test/test_pr5f.py                                    PIN constant → v1-packets-consumers
  test/test_pr7.py                                     + record assertions
  features.json, progress.md                           pr7d row; phase status

CHANGES:

1. Pin bump at every locus test_pr5f.py checks; then `just regen-agents` twice; `git
   status --short` clean after the second. Paste the diff of .agents/agents/ — it must
   contain exactly the 7b persona changes (per-item lines on PO/QA/CTO, step edits on
   the two conductors) and nothing else. If regen pulls something you did not expect,
   stop and report; do not hand-edit the copies.

2. Plan record, both twins, hand-maintained, must agree:
   - `### PR 6 — The v2 chain` → `### PR 6 — The v2 chain ✅ landed` with the three PR
     links (skills#125, loops#11, harness#10) and "no tag cut; retired by 7a/7b".
   - `### PR 7 — …` → `✅ landed` with links to the four PRs and both tags.
   - Header `**Status:**` line (decision 13): leading word becomes `complete`; append
     `· PR 6 landed (…) · PR 7 landed (…; tags v1-packets / v1-packets-consumers) ·
     acceptance condition 1 undemonstrated (no Elm/Melange run yet); condition 2 is a
     running measure`. test_gan_record.phase_disagrees_with_plan fails a completed
     phase under an "in progress" header, so the word and the phase move together.
   - §7 row 7 is a draft until this merge (decision #12), so edit it in place to the
     measured statement: "audit-packet brief rejects a pasted SKILL.md, a board dump,
     dashboard HTML, and any non-grammar heading (N tests); axel card mandates the
     audit before every delegation; verify-protocol enforces per-item verdicts on the
     three batch adversaries; bootstrap installs the gate." Fill N from the 7a suite.
     Do not touch rows 0–6.
   - §6 "Per-item BLESS when AVRIL batches (PR 7)" → keep; append "(landed: gan-verdict
     item 9 + verify-protocol batch rule)".
   - §8: add decision 13, one row, pointing at this prompt set's decisions 1–13 as the
     PR 7 settlement (the PR 5 decisions got the same treatment).

3. Prompt set Status table: add a `## Status (measured <date>)` section to
   pr7-handoff-packets-prompt-set.md in the pr5 shape — 7a / 7b / 7c / 7d rows with PR
   links, merge SHAs, tags. No HTML twin exists for this file (Unresolved 1).

4. Tracker: features.json `pr7d` row completed; gan-layer-separation phase status →
   completed (decision 13). progress.md PR 7d (COMPLETED) + a phase-close note that
   names the undemonstrated acceptance condition.

5. test/test_pr7.py additions (LiveTree): plan header starts `**Status:** complete`,
   contains "PR 6 landed", "PR 7 landed", and "condition 1 undemonstrated"; both
   `### PR 6` and `### PR 7` headings carry ✅; html twin names both tags; phase status
   agrees with the header (reuse test_gan_record's calculation); all pin loci read
   v1-packets-consumers (test_pr5f asserts this once PIN moves — move PIN, do not
   duplicate).

VALIDATE (paste all, in order):
  git ls-remote --tags https://github.com/sycamore-hq/crossr-loops.git v1-packets-consumers → SHA
  grep -rn 'v1-one-law-consumers' --exclude-dir=.git --exclude=progress.md --exclude=MIGRATION.md . | grep -v docs/plans → 0 hits outside history
  just regen-agents; just regen-agents; git status --short                                  → clean
  grep -c '✅' docs/plans/gan-layer-separation-plan.md                                       → previous count + 2
  python3 -c 'import json;print(json.load(open("features.json"))["gan-layer-separation"]["status"])' → completed
  python3 -m unittest discover -s test -v                                                    → OK
  just harness-validate                                                                      → PASS
Stack line: "7d of 4, closes PR 7 and the gan-layer-separation phase. 7c merged as <sha>.
No tag cut here. Next: work ledger flip."
```

---

## Ledger steps (sycamore-hq/work) — the record, not a view

`work.json` is the record; issues and the Project are views. Three ledger commits, each
with `just test` + `just status-html` pasted:

1. **Before 7a dispatch** — `pr7.repos` gains `"crossr-harness"` (decision 11); `notes`
   names this prompt set. `just project-roadmap --dry-run` pasted: the planned change is
   one added `repo:crossr-harness` label on #12. A human runs the write.
2. **At 7a merge** — `pr7` `todo` → `in_progress`; `notes` names skills#<7a> and the
   `v1-packets` SHA; `source_as_of` updated. Commit message in the house shape
   (`work-00: pr7 in progress on skills#<n> <range>`).
3. **At 7d merge** — `pr7` → `done`; `notes` carries the four PR ranges and both tags,
   and the phase-close clause. `progress.md` gets the pr7 done paragraph in the pr6 shape.
   `just project-roadmap --dry-run` pasted; the write needs org project write.

No new ledger card. The ledger tests assert invariants, not ids, so none of the three
commits touches the suite.

---

## Review gauntlet (what gets checked when each PR comes back)

- **7a**: gan-verdict items 1–7 are context lines in the diff; ≤ 2,048 B measured; the
  decision-3 sentence verbatim; audit-packet exit codes 0/1/2 shown; **three never-fixtures
  red on screen** (SKILL.md frontmatter, board JSON, dashboard HTML); a 141-char prior
  verdict red and 140 green; a prose line inside a diff fence red; `verdict --items`
  blanket / silence / stray each red; every CHANGES-4 bullet has its own test (count them);
  the fallback path starts with `${TMPDIR:-/tmp}/`; no rust/ocaml token; harness-validate
  pasted; features/progress appended, not rewritten; stack line present; tag cut after
  re-validation on the merge commit.
- **7b**: pin moved at both loci; verify-skill-refs pasted **red at v1-one-law and green at
  v1-packets** (the PR 6 gap retired, in front of me); avril.json diff is three inserted
  keys; schema + ALLOWED_NODE both carry `batch`; verify-protocol batch failure demonstrated
  on the code-gan reviewer and reverted; the sentence verbatim on the avril card and all
  three batch personas; **no cap language on the avril card** and the cycle line in the
  blessing log; the three AXEL verdict-format lines and both conductor mandates
  byte-identical (diff empty); card caps measured; axel card names both audit modes and
  the prose-drop; harness-parameters names the scratch path with the temp-dir fallback
  and no packet path under `docs/` or `.pinto/`; no gan-verdict grammar copied into loops
  (linked by name); book and command edits are one paragraph / one hint each; index.html
  regenerated twice clean; tag cut after re-validation.
- **7c**: old tags zero hits outside history, smoke's three hardcoded pins included;
  bootstrap diff is one inserted block mirroring audit-plan; smoke **red at v1-one-law
  and green at v1-packets**; §6 and §12 edits are two lines and both pasted as
  protected-law edits; the scratch path in §12 is the temp-dir fallback, not a repo path;
  `just test` green with the new test file; no tag.
- **7d**: regen twice clean and the persona diff is exactly 7b's; PR 6 recorded landed
  (it never was); header says `complete` and names the undemonstrated condition; phase
  `completed`; §7 row 7 filled with the 7a test count, rows 0–6 untouched; decision 13
  row present; prompt-set Status table added; test_pr5f PIN moved, not duplicated;
  harness-validate green.
- **Throughout**: every acceptance line has pasted output; a "verified" without a command
  is a REJECT; no new verdict token; no book name; nothing outside the file lists; no
  packet path inside a repo tree.

---

## Unresolved questions

1. **HTML twin for this prompt set.** The PR 5 set keeps hand-maintained md + html twins and
   `test_gan_record` reads both. This file has no twin. Default: none until a generator
   exists; AGENTS.md rule 11 prefers HTML for human deliverables, so the human decides
   whether the twin is worth a second hand-maintained file.
2. **`code-writer` on the AVRIL personas.** PO / QA / CTO still require `code-writer`; the
   avril card says "load no writer skill". Out of PR 7's scope; 7b parks it in the PR body.
   Needs a card.

Settled 2026-09-09 and folded into the decisions above: packet scratch path (decision 1),
batch-size cap (decision 9), phase close (decision 13), harness in the stack (decision 11).
