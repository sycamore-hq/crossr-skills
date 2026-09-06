# Plan: crossr v2 — Layer Separation, Shared Ruleset, Plan-First GAN

**Status:** in progress · PR 0 merged (#105) · PR 1 landed · PR 2 landed · PR 3 landed · PR 4 landed (loops [#7](https://github.com/sycamore-hq/crossr-loops/pull/7), skills [#110](https://github.com/sycamore-hq/crossr-skills/pull/110)) · PR 5 landed (skills [#117](https://github.com/sycamore-hq/crossr-skills/pull/117) / [#118](https://github.com/sycamore-hq/crossr-skills/pull/118) / [#120](https://github.com/sycamore-hq/crossr-skills/pull/120), loops [#9](https://github.com/sycamore-hq/crossr-loops/pull/9), harness [#8](https://github.com/sycamore-hq/crossr-harness/pull/8), landing [#10](https://github.com/sycamore-hq/crossr-web-landing/pull/10); tags `v1-one-law` / `v1-one-law-consumers`)
**Scope:** `crossr-skills`, `crossr-loops`, `crossr-harness`
**Origin:** token-burn critique of the crossr-* agent infrastructure, verified against the trees 2026-08-30.

Three moves, in dependency order. **Separate the layers** (persona / gate card / book /
protocol) so nothing is loaded that cannot be used. **Collapse the ruleset to one source of truth** with
progressive disclosure, so the generator and the adversaries stop disagreeing about the law. **Reorder
the gates by blast radius**, so the expensive gate runs when there is nothing to throw away.

---

## 1. The problem in one paragraph

The conductor loads writer and adversary skills it is forbidden to use, pays for the
same GAN description twice, restarts a three-gate chain on every `REJECT`, and can only
run on Rust — because the entire adversary layer is named `rust-*` while being almost
entirely language-neutral. Underneath that, persona and ruleset are smeared across two
file layers that already exist, producing two contradictory mandates per role and three
mutually incompatible verdict vocabularies that no conductor can actually parse.

The `orchestrator-prompt` template already encodes the cheap version of all of this —
tight briefs, cheap runners, expensive judge, don't swallow transcripts, ledger the cost.
None of that discipline reaches the in-harness skill loops.

---

## 2. Verified evidence

Every number below was measured against the working tree. Cite these when reviewing.

### 2.1 Static weight

| Skill | Bytes |
|---|---|
| `ocaml-code-writer` | 19,551 |
| `axel` | 18,716 |
| `chief-of-staff` | 13,086 |
| `avril` | 12,627 |
| `agent-harness` | 11,615 |
| `rust-team-lead` | 10,074 |
| `brick` | 9,363 |

Naive Rust AXEL load set — `code-writer` + `axel` + `rust-code-writer` + `rust-team-lead`
+ `rust-code-reviewer` + `rust-code-tester` + `rust-architect` + `agent-harness` =
**73,031 bytes ≈ 18k tokens** of SKILL.md before a single diff enters the window. Add a
domain skill (`rust-axum-backend`, 7,728) and it is ~81KB.

No conductor skill has a `references/` directory. There is zero progressive disclosure in
the hot path, in a catalog that ships `diataxis`.

### 2.2 The conductor loads what it may not use

Three files independently declare the fat load set:

- `crossr-skills/.opencode/agent/axel.md` and `crossr-loops/templates/harness/opencode/agent/axel.md`
  — "load `axel` and `code-writer` … Rust: `rust-code-writer` + `rust-team-lead`".
- `crossr-loops/.agents/agents/axel-conductor-agent.md:9-12` — requires `code-writer`,
  `axel`, `rust-code-writer`, `rust-team-lead`, **and** `rust-code-reviewer`,
  `rust-code-tester`, `rust-architect`, in a persona whose step 11 forbids it from
  authoring review content.
- `crossr-loops/graphs/axel.json` `requires.skills` — the same flat union, even though its
  only code node is a subgraph reference.

### 2.3 The adversaries are not Rust skills

`rust-architect/SKILL.md`: **every** occurrence of "Rust" is in the name, description,
prerequisite line, Specialization boilerplate, or mandate. Not one line of the Core
Principles or the Ruthless Architecture Checklist is Rust-specific.

`rust-code-tester`: ~90% generic. Rust delta is `#[cfg(test)]`, `cargo test --workspace`,
pedantic clippy.

`rust-code-reviewer`: the only real Rust body — `thiserror` / no `anyhow` / no `.unwrap()`
/ pedantic clippy / approved crates, roughly 2KB. Its "Non-Negotiable Core Principles"
section is `code-writer` restated verbatim.

Of ~18.9KB of adversary law, **~16KB is language-neutral and ~2-3KB is actually Rust.**

### 2.4 The catalog is a monoculture

```
rust     writer ✓  reviewer ✓  tester ✓  architect ✓
ocaml    writer ✓  reviewer ✓  tester ✓  architect ✓
elm / ts / py / go / hs        unblocked (no book yet)
```

**Discharged in PR 5.** Writer is `code-writer` plus the language book. Reviewer /
tester / architect are the language-neutral gate cards (`code-review`, `testing`,
`architecture`) plus the disclosed book's `RULES.md`. OCaml picked up the three
adversaries the moment the gate cards dropped the `rust-*` names (5c). Elm / TS / JS
load the same gates today; what they lack is a book, not a halt.

`ocaml-code-writer` was the largest file in the catalog and had no adversaries. Someone
already tried to go multi-language, wrote the writer, and hit the wall where every
adversary was named `rust-*`.

`axel/SKILL.md:71-75` handles this correctly in principle — "harness-disclosed reviewer →
tester → architect … If no code GAN is disclosed, **stop**". But for Elm or Melange there
is nothing to disclose, so **AXEL is designed to halt on any non-Rust language**, while the
entrypoints hardcode the Rust triple and would review Elm against `thiserror` rules.

Contamination is localized: `axel` has 18 Rust-ish lines of 317. `avril` has **0**.
`brick` has **0**. `code-writer`'s single hit is the line instructing language-agnosticism.

### 2.5 Persona and ruleset are smeared

Both layers already exist and ship — `crossr-harness/scripts/harness-bootstrap:131-140`
copies `.agents/agents/` into every target repo.

Every adversary role has **two different One-Sentence Mandates**, both labeled "Memorize
This", while `rust-architect/SKILL.md:60` makes verbatim recitation a scorable behavior:

| Role | Agent file | Skill file |
|---|---|---|
| architect | "Protect the long-term clarity and evolvability of the system above all else." | "Guard the entire Rust system architecture with Torvalds-level ruthlessness…" |
| reviewer | "Make every piece of Rust code so clear, layered, and correct that any experienced developer can understand and safely modify it in under 10 minutes." | "**Write** layered, modular Rust code built from pure calculations on immutable data…" |
| tester | "Every calculation and every public item must have clear, fast, exhaustive tests…" | "Ensure every calculation and public item has complete, layered, deterministic tests…" |

The reviewer's skill-layer mandate is a **writer's** mandate, in a skill whose iron
boundary is *never write code*.

Persona blocks inside skills are small and cleanly fenced — reviewer 371 B, tester 608 B,
architect 618 B — and contain zero Rust. Six skills carry persona: `avril`, `axel`,
`rust-team-lead`, `rust-code-reviewer`, `rust-code-tester`, `rust-architect`.

**§2.5 discharged (PR 4).** PR 1 lifted skill-layer mandates for the three adversary
gates only. `axel` and `avril` kept skill-layer One-Sentence Mandates that contradicted
their personas until PR 4 deleted them — persona wins. One mandate per conductor role,
on the persona only. The finding is fully discharged. `brick` and `orchestrator-prompt`
still carry skill-layer mandates (no persona counterpart; out of scope).

### 2.6 The verdict protocol is broken

`avril/SKILL.md:72` — "Advancement requires the exact token `BLESS` from each adversary.
Silence, hedge, or 'LGTM' without `BLESS` counts as incomplete." Graph edges fire on
`"when": "BLESS"`.

What the adversaries emit:

| Gate | Declared OUTPUT FORMAT |
|---|---|
| `rust-code-reviewer` | **none — no output format section at all** |
| `rust-code-tester` | `TEST VERDICT: PASSED \| REJECTED` |
| `rust-architect` | `ARCHITECTURE VERDICT: BLESSED \| REJECTED` |

Token census: `BLESS` 71, `REJECT` 38 (conductor + graph) against `BLESSED` 2, `PASSED` 1,
`NACK` 2 (persona). **No code adversary emits the token its conductor requires**, and the
first gate in the chain has no response contract at all.

An LLM conductor reads `PASSED` as approval, so nothing visibly breaks — which means the
"exact token" rule is decorative and *silence ≠ approval* is currently enforced by nothing.
It becomes a hard break the moment a runner string-matches `when: "BLESS"`.

Also: no adversary persona is registered as a runtime agent. `.opencode/agent/` contains
only `avril`, `axel`, `status`. Every `rust-reviewer-agent` reference in `axel/SKILL.md`,
the entrypoints, and both graph JSONs resolves to a markdown file nobody loads.

### 2.7 The law is hand-copied three times

`rust-code-reviewer`'s "Non-Negotiable Core Principles" section is `code-writer` restated verbatim.
`rust-code-tester` restates it again. Three hand-maintained copies of one law.

This is not merely duplicated weight. **Any drift between the generator's rules and the reviewer's
checklist manufactures a rejection** — the generator writes to law A, the reviewer rejects against
law B, and a full adversary cycle burns on a disagreement between two documents that were supposed
to say the same thing. Deduplication here removes a class of iteration, not just bytes.

`rust-errors` (5,470 B) is already a situational how-to document — thiserror layering, `From` impls,
the no-inline-`map_err` corollary — shipped as a top-level skill that must be manually combined.
It is `references/error-handling.md` wearing a skill costume. The catalog was already growing toward
progressive disclosure; it just had no place to put it.

### 2.8 The system architect appears in exactly one place

`planning-architect-agent.md:3` — "Role: **Generator** in the AVRIL planning GAN." AVRIL's
adversaries are PO, QA, and CTO. The Torvalds-style system architect that guards stratification
is **not in AVRIL at all**; its only appearance in either loop is the AXEL code gate, where it runs
*after* implementation — so every architect `REJECT` discards a completed implementation.

### 2.9 `rust-team-lead` is AXEL with a different input noun

Its own `SKILL.md:19` declares the skill "portable and harness-agnostic" while being named
`rust-*` and hardcoding three Rust adversary names.

Content vs `axel`: GAN method (duplicated), adversary chain in fixed order (duplicated),
ruthless checklist (duplicated), Status Dashboard (near-duplicate — 1,169 B vs axel's
1,281 B, differing only in "plan" vs "board" and the checkpoint list), Verification,
Specialization, mandate. The only conceptual difference is that RTL executes "a planning
document" and AXEL executes "a blessed PBI" — but `axel` step 1 emits a plan and step 3
decomposes it into phases, then step 4 runs the identical chain.

`graphs/axel.json` already resolved this: node `rust-gan`, `role: graph`,
`uses.graph: rust-team-lead`. The decision is made; only the prose is stale.

25 files reference `rust-team-lead`; **8 are load-bearing** — `axel/SKILL.md` (×10), both
`opencode/agent/axel.md`, `axel-conductor-agent.md`, both graph JSONs, `HARNESS-SPEC.md`,
`AGENTS.md`. The rest are `progress.md`, pinto tasks, and MIGRATION, which should keep the
name as history. (§2.9 referenced from PR 3.)

### 2.10 Pinto hard-errors on any non-task file in `.pinto/tasks/`

Verified against Pinto 0.2.0 in an isolated scratch board. Dropping `T-1.plan.md` beside
`T-1.md` in `.pinto/tasks/`:

```
$ pinto list
error: missing `+++` frontmatter delimiter in .pinto/tasks/T-1.plan.md
$ pinto list --json
error: missing `+++` frontmatter delimiter in .pinto/tasks/T-1.plan.md
```

Not a warning — a fatal error that takes down the entire board read. AXEL's pre-flight step 3
loads board state via `pinto list --json`, so a plan file in that directory breaks **every AXEL
session**. `.pinto/plans/` and `docs/plans/pbi/` were both verified clean.

`pinto link` binds commit SHAs to PBIs and discovers them by matching PBI ids in commit messages
(`pinto link sync`). There is no file-attachment mechanism; git is the linkage.

### 2.11 The full-chain restart is encoded structurally

`axel/SKILL.md:127` and both entrypoints: any `REJECT` restarts all three gates. In
`graphs/rust-team-lead.json`, every `REJECT` edge points at `generate`, whose only
out-edge is `reviewer`. Changing this rule requires editing the graph, not just the prose —
`scripts/verify-graphs` is a gate.

### 2.12 `skill-evaluator` blocked the refactor (historical — fixed by PR 0, #105)

Its rubric already condemns the current shape — first three items are *Concise*, *Single
Responsibility* ("one clear thing"), *Progressively Disclosed*.

But `skill-evaluator/SKILL.md:122` sets the postcondition: "preserving 100% of the original
target skill's intent, **voice**, and checklist wording."

The rubric says split; the postcondition says preserve voice. The evaluator was deadlocked
against itself and the remediator would have rejected every de-personaed skill. PR 0
(#105, follow-up 8920866) removed the voice postcondition; kept here as the evidence that
motivated it.

---

## 3. Target architecture

### 3.1 Four layers, one owner each

| Layer | Owns | Language | Example | Size |
|---|---|---|---|---|
| **Persona** | voice, boundary, mandate | neutral | `architect-agent` | ~600 B |
| **Gate card** | the *job*: what this gate verifies, its envelope | neutral | `architecture`, `code-review`, `testing` | ~1–2 KB |
| **Book** | the *law*: rules + how, per language | specific | `rust/references/*` | per topic |
| **Protocol** | verdict vocabulary + envelope schema | neutral | `gan-verdict` | ~10 lines |

Gate cards own the job; the book owns the law. There are **no intermediate delta skills**
(`rust-review`, `rust-testing`) — adversaries load their gate card plus the Rules projection
of the relevant book references (§3.4). A language with no book yet runs on the universal
gate cards alone, which preserves the day-one-language property in stronger form: it no
longer depends on empty placeholder files existing.

Worked example:

```
architect   persona   architect-agent    ~600 B  neutral
            gate card architecture       ~2 KB   neutral (already 100% neutral today)
            book      rust/references/layering.md — Rules projection only

reviewer    persona   reviewer-agent     ~400 B  neutral
            gate card code-review        ~1 KB   the job + envelope
            book      rust/references/*  — Rules projections (thiserror, no anyhow,
                                           no unwrap, clippy, crates live here)
```

**A missing book is a feature.** Today, no `elm-architect` means AXEL halts. After the
split, no `elm/` book means "no Elm-specific law yet" and the universal gate cards still
run. New languages work on day one; books accumulate later.

### 3.2 Load by role, not by stack

| Window | Loads |
|---|---|
| Conductor | conductor card + current PBI + 20-line handoff packet + board snapshot of that item |
| Generator subagent (**plan** phase) | `plan-writer` + book **Rules** + the PBI |
| Generator subagent (**execute** phase) | `code-writer` + language writer + domain |
| Reviewer subagent | `reviewer-agent` + `code-review` card + book Rules projection |
| Tester subagent | `tester-agent` + `testing` card + book Rules (tagged `test`) |
| Architect subagent | `architect-agent` + `architecture` card + book Rules (layering) |

The conductor loads no writer skill and no adversary skill. "Conductor writes no code" is
already law; this enforces it in the load set.

### 3.3 Split the contract by owner

**Verdict protocol — invariant, NOT conductor-owned.** Token vocabulary (`BLESS` /
`REJECT`), silence ≠ approval, one verdict per delegation, verdict names its gate. Lives in
a **tiny dedicated catalog skill, `gan-verdict`** (~10 lines), referenced by conductors and
adversaries alike, redefinable by neither. Not `agent-harness` — that file is an 11 KB
harness-building essay that already hardcodes the Rust adversary triple in its PETC example
(line 85); dropping the contract in there is the smear with a new heading. `agent-harness`
points at `gan-verdict`.

*Rationale:* if the conductor defines what counts as approval, a conductor under context
pressure can define an approval that is cheaper to obtain. That is the orchestrator grading
its own homework — precisely the failure the GAN exists to prevent.

**Report envelope — schema in `gan-verdict`, values conductor-filled.** The field
vocabulary (phase id, "k of n", AC ids claimed, findings shape, max length, `file:line`
citations) is fixed in `gan-verdict` as a ten-line list with optional fields. The conductor
selects which optional fields apply and fills the values at delegation time — AXEL fills AC
evidence refs, AVRIL per-PBI ids, BRICK stage signals. Adding a *field* requires changing
`gan-verdict`, never a conductor card. This sharpens the ownership rule rather than
weakening it: the conductor chooses what it wants to hear **from a fixed menu**, which makes
the envelope mechanically checkable too.

> **The rule: the conductor may specify what it wants to hear, never what counts as approval.**

Two constraints:

- **Put the envelope last.** Persona + ruleset are the stable cacheable prefix; the envelope
  varies per delegation. Splicing it above the ruleset destroys prefix stability on exactly
  the text you were trying to make free on turns 2–N.
- **Cap it at a field list.** Ten lines, names and types. The moment it explains *why* a
  field matters it has become law and belongs in the ruleset.


### 3.4 One ruleset, progressively disclosed, three projections

Collapse the per-role checklists into a single language skill whose body is a card and whose law
lives in situational references. `diataxis` already ships this pattern in this catalog.

```
rust/
  SKILL.md                ~2 KB card — which reference applies to which situation
  references/
    error-handling.md     (absorbs rust-errors)
    input-parsing.md      parse-don't-validate, newtypes at the edge
    layering.md           stratification, actions / calculations / data
    testing.md            AAA, error paths, cfg(test)
    api-surface.md        pub items, docs, semver
    tooling.md            fmt, clippy pedantic, deny lists
```

Every reference file carries **two projections of one law**:

```markdown
## Rules (normative, checkable)
RE-01  Every layer defines its own error enum via thiserror.
RE-02  Cross-layer propagation uses #[from]; never inline .map_err at a call site.
       check: rg '\.map_err\(' src/ --glob '!adapters/**' → expect 0

## How
<examples, patterns, the reasoning>
```

| Role | Loads |
|---|---|
| Generator | the whole reference for the situation at hand |
| Reviewer | the **Rules** block only |
| Test verifier | Rules tagged `test` only |

The Rules-only projection for adversaries is not an optimization — hand a reviewer the *How*
section and you get a reviewer that suggests implementations, which breaks the boundary the whole
GAN rests on.

**Stable rule IDs** buy three things: the reviewer cites `RE-02` instead of re-deriving it, the
generator self-checks before submitting, and rejection counts per rule id tell you which reference
needs a better *How* section. That is a feedback loop on the token spend itself.

### 3.5 The v2 chain: gates ordered by blast radius

```
PBI (AVRIL-blessed)
  │
  ├─ Generator     implementation plan + typed claim list
  │      ├ Mechanical  bidirectional AC↔claim coverage · quota · id integrity  [no LLM]
  │      ↕ Architect   blesses the plan, or rejects for underspecification     [loop]
  │
  ├─ Generator     execute the blessed plan
  │
  ├─ Mechanical    fmt · clippy · build · test · import-lint     [no LLM spend]
  │                  red → back to Generator, zero tokens burned
  │
  ├─ Test verifier do the tests cover every AC? zero regressions?
  │
  └─ Reviewer      faithful to the plan claims and the PBI AC?
                   + one bounded unanticipated-risk pass
        │
      commit
```

Each gate's rejection invalidates less downstream than the gate before it. Today an architect
`REJECT` discards a finished implementation; at plan time it discards a paragraph. **This is the
single largest saving in the plan.**

It also unifies the topology: `graphs/avril.json` is `generator → adversary … → stop` with
`REJECT → generator`. The AXEL inner loop becomes AVRIL's shape one level down — propose, get
blessed, then execute.

**One adversary per artifact type, mechanical checks before every LLM gate.**

| Artifact | Mechanical | LLM adversary |
|---|---|---|
| the plan | bidirectional coverage · judgment quota · id integrity | Architect |
| the diff | fmt · clippy · build · test · import-lint | Test verifier → Reviewer |

Each adversary reviews the artifact class it is expert in, exactly once. The architect reviews
designs; the reviewer and test verifier review implementations.

**Why the other adversaries do not join the plan gate.** The test verifier cannot judge test quality
before tests exist; its only plan-time contribution is AC coverage, which is a script — paying a
persona for it contradicts mechanical-before-LLM. The reviewer's job is *faithfulness to the plan*,
which is definitionally post-implementation; at plan time it can offer only a second architectural
opinion, duplicating the architect. AVRIL's PO/QA/CTO already reviewed scope at PBI blessing;
re-running them is the `scope change → back to AVRIL` edge, not a gate.

There is also a cost argument. The Architect↔Generator loop is the **most iterated** loop in the
chain; a second persona there multiplies iterations on the one gate that can least afford to be
chatty.

*The honest downside:* the plan has one LLM gate where the diff has two. That is a real reduction in
rigor, mitigated by the fact that a bad plan still surfaces downstream and the unsatisfiable-claim-id
trigger escalates it back to the architect. Detected later, not undetected.

**Two guards this ordering requires.**

*The reviewer needs a second, capped mandate.* "Faithful to plan and AC" is bounded and checkable,
which is the point — but a plan saying "add a retry wrapper" is satisfied by a retry wrapper with an
unbounded loop. Conformant, and still wrong. So: conformance **plus one bounded pass for
unanticipated risk in the diff** — each finding names a concrete failure mode, at most three, and
anything architectural escalates rather than being resolved inline.

*The generator writes the plan it must then satisfy.* It will write one it finds easy. The architect
gate only mitigates that if it can reject a plan **for being underspecified**, which puts the entire
weight on the claim taxonomy below.

*Same role, different card.* The plan and the diff are different artifacts needing different law, so
the Generator loads **`plan-writer`** at plan time and `code-writer` at execute time (§3.2). It stays
**one persona**: the plan-first chain's saving depends on the paragraph being the implementer's own
cheap draft, and the §3.6 escalation trigger is only a high-signal tripwire while the agent that
cannot satisfy claim N is the agent that wrote it. See decision #11 for the evidence that would
justify splitting the role itself.

*The plan loop gets a trip limit.* Architect↔Generator is the most iterated loop in the chain and
has no natural terminus. **Three architect REJECTs on one plan stops the loop for a human.**
Without the cap, v2 spends the tokens it saved on implementation restarts playing plan tennis.

### 3.6 Claim taxonomy — what "verifiable" means

Most architectural constraints are not mechanically checkable. Do not make the requirement binary;
make it a taxonomy with a quota.

| Claim type | Verified by | Example |
|---|---|---|
| **Mechanical** | a command + expected exit code | `rg '\.unwrap\(' src/ → 0` |
| **Observable** | pointing at `file:line`, no judgment | "`ParseError` has `From<io::Error>`" |
| **Judgment** | an LLM read | "the retry policy is comprehensible" |

**The architect rejects any plan whose judgment claims exceed ~30% of the total.** That is what turns
"mechanically verifiable" from aspiration into a gate, and it gives the reviewer a bounded job: run
the mechanical claims, point at the observable ones, judge only the capped remainder.

This extends an existing rule down one level — `.pinto/dod.md` already requires that "acceptance
criteria are falsifiable checkboxes."

**Code-time architect escalation** gets a mechanical trigger rather than a judgment call: plan claims
carry ids, so *if the Generator cannot satisfy claim N, that is an automatic architect escalation.*
Deviation from the plan is detectable, so the trigger costs nothing.

### 3.7 The plan artifact

The implementation plan is the reviewer's contract. It lives **alongside the PBI it implements**,
with the same stratification AXEL already applies to the board backend.

| Harness | Path |
|---|---|
| Pinto disclosed | `docs/plans/pbi/<id>.plan.md` |
| Portable fallback | `<disclosed-backlog-path>/plans/<id>.plan.md` |

**Never `.pinto/tasks/`** — see §2.10. `.pinto/plans/` also works today, but Pinto has just
demonstrated that it errors on unexpected files in directories it owns; staying outside `.pinto/`
removes the class of risk, and `docs/plans/` is already the established home.

Linkage needs no new machinery: the plan's own commit carries the PBI id, so `pinto link sync`
binds it to the PBI through the existing commit-matching path.

**Four rules make the artifact load-bearing rather than decorative.**

1. **Blessed means immutable, and committed before implementation begins.** If the Generator can
   edit the plan after writing code, conformance review is worthless — it is the same self-grading
   failure as letting the conductor own the verdict contract (§3.3). The blessed plan lands in its
   own commit, referencing the PBI id, *before* the first implementation commit.
2. **Claim ids are append-only.** Architect and Generator iterate, so plans have revisions. A
   renumbered claim breaks both the reviewer's citations and the escalation trigger. New claims get
   new ids; superseded claims are marked superseded, never deleted or renumbered.
3. **Coverage is bidirectional, and it is a script.** Every AC maps to at least one claim id —
   nothing silently dropped. And **every claim maps to at least one AC** — nothing silently added.
   An orphan claim *is* scope creep, and it is the one failure a plan introduces that the architect
   will not catch: a plan that satisfies the letter of every AC while quietly growing the work.
   Detecting it would otherwise need a PO voice at plan time; with bidirectional coverage it is
   `comm` on two id lists.
4. **The plan outlives the PBI.** It is the record of why the code looks the way it does. The PBI
   Completion Record gains a `## Plan` line naming the path and the per-claim verdicts.

**A gap this closes that is not otherwise on the list.** Today `axel/SKILL.md` step 3 —
*Decompose into the smallest semantic phases* — is performed by the conductor alone, with zero
adversary review. Phase boundaries are an architectural decision currently made unilaterally.
Once the Generator writes the plan and the Architect blesses it, the decomposition is inside the
blessed artifact and gets reviewed for the first time.

### 3.8 Handoff packets, both directions

Conductor sends `brief + envelope spec`. Persona returns `verdict + envelope`.

Each adversary receives:

- phase id and "k of n"
- file list + `git diff` of this phase
- the AC subset this phase claims
- prior verdicts as one-liners (`reviewer BLESS`, `tester REJECT: no error path for X`)

Never: sibling SKILL.md files, previous-phase essays, `pinto list --json` of the whole
board, dashboard HTML pasted back into the window.

After the phase commits the conductor keeps the 20-line completion record and drops the
review prose. `features.json` / `progress.md` / the ledger are the memory. The chat is not.

---

## 4. PR sequence

Ordered by dependency, then by cost. Each PR is independently shippable and measurable.

### PR 0 — Unblock the evaluator ✅ merged (#105, + follow-up 8920866)

**Files:** `crossr-skills/.agents/skills/skill-evaluator/SKILL.md`

Rewrite the Specialization postcondition (line 122) from "preserving 100% of the original
target skill's intent, voice, and checklist wording" to preserve **intent and checklist
wording**, with voice explicitly assigned to the persona layer. Add a rubric note that a
skill carrying an `Agent Personality` block fails *Single Responsibility*.

~20 minutes. Load-bearing for everything after it. Without this the skill GAN rejects the
refactor its own rubric demands.

**Merged as #105**, with a follow-up (8920866) applying two review findings: the
clarifier gained **flag-don't-strip** transition semantics, and its scope was narrowed to
`Agent Personality` blocks only — the broad wording would have failed every catalog skill
on sight and broken the evaluator's own self-exemplar check. One-Sentence Mandates and
`OUTPUT FORMAT` are explicitly out of scope for the check *for now*: OUTPUT FORMAT moves
to `gan-verdict` and role mandates lift in PR 1, at which point the clarifier can widen
again. Still owed to PR 1: `skill-remediator-agent.md:20` instructs matching "the exact …
one-sentence mandate format" — the preserve-vs-condemn deadlock one layer down — and the
narrowing commit deliberately left open whether foundation skills without personas
(`code-writer`, the book) keep their mandates; decide that when the trio lifts land.

### PR 1 — Peel persona, mandate, and protocol (no ruleset moves) ✅ landed

**Landed as the stacked pair** skills `pr1-peel-persona-protocol` → loops
`pr1-personas-verify-protocol`. Stack order: 1a (catalog) first; the loops PR retargets
`skills = "v1-gan-layers"` — a tag to be cut from crossr-skills `main` at the 1a merge
commit before the loops PR merges. No shim: `v0-last-monolith` is a frozen tag, so
existing consumers never see the rename; `harness-bootstrap` clones by
`--branch <tag>`, which fails loudly (not silently) if the new tag is missing.

**Foundation-mandate decision (owed by PR 0):** foundation skills without personas
(`code-writer`, later the language books) **keep their One-Sentence Mandates** — there
the mandate is the skill's own contract summary, not a role voice (the 8920866
position). The widened evaluator clarifier records this in one sentence.

**Contact notes:** two protected-law strings collided with the acceptance greps and were
edited minimally — `architecture` Core Principle 3's `BLESSED`/`REJECTED` tokens became
`BLESS`/`REJECT`, and the tester checklist item "Exact OUTPUT FORMAT used" now points at
`gan-verdict`. The architect personality's "NACK." verdict style was dropped when the
block landed in the persona — `verify-protocol` forbids `NACK` as a verdict token.

**Files:** `rust-architect`, `rust-code-reviewer`, `rust-code-tester`, `agent-harness`,
new `gan-verdict` (crossr-skills); `rust-architect-agent`, `rust-reviewer-agent`,
`rust-tester-agent` (crossr-loops); `scripts/verify-protocol` (crossr-loops, beside the
graphs it must read).

PR 1 **peels; it does not restructure law.** The rust-* skill bodies stay where they are
until PR 5 folds them into the book — building intermediate `rust-review` / `rust-testing`
delta skills that PR 5 would then delete is touching adversary law twice, which this plan
forbids. The one rename that happens now is `rust-architect` → `architecture`, because it
is already 100% language-neutral (§2.3) and survives as a gate card.

1. `rust-architect` → `architecture`. Pure rename; **zero checklist edits**.
2. Lift `Agent Personality` blocks into the persona files. Delete from skills.
3. **One mandate per role, in the persona.** Delete the skill-layer mandates. Fix the
   reviewer's writer-mandate bug.
4. **Strip writer prerequisites everywhere they appear** — not just the architect.
   `rust-code-reviewer` and `rust-code-tester` both say "MUST also apply `code-writer` +
   `rust-code-writer`" (tester line 16 and five echoes), and all three persona files list
   the writer skills as required. Left in place, these lines put the 73 KB stack back into
   every subagent the moment PR 2 makes the personas real. Replace with "the disclosed
   gate card + book Rules projection".
5. **Create `gan-verdict`** (~10 lines): `BLESS` / `REJECT`, silence ≠ approval, one
   verdict per delegation, verdict names its gate, plus the envelope field schema (§3.3).
   Delete all three `OUTPUT FORMAT` blocks from the skills. `agent-harness` gets a pointer,
   not a copy.
6. **Lift the skill-GAN trio's mandates too** (`skill-evaluator`, and any mandate in
   `skill-remediator` / `skill-reviewer` contract files) into their existing persona files —
   the evaluator is itself a valid GAN target and self-condemns until this lands. Its
   `## Output Format` stays: that is the job's report contract, gate-card material, not
   persona. Delete the remediator's mandate-format-matching clause (line 20) in the same
   pass.
7. Add `scripts/verify-protocol` **in crossr-loops next to the graphs** (it must read the
   graphs' `when:` values, which live in that remote), asserting every persona's declared
   verdict token matches the edge vocabulary. Wire into `just`.

Personas are edited **under their current names** — the `rust-` prefix drops in PR 2,
when they become runtime agents and every referrer (entrypoints, `axel.json`
`uses.persona`) is being rewritten anyway. Renaming here would break graph references
PR 1 does not otherwise touch.

**Remote split:** these files span two remotes — adversary skills and `gan-verdict` in
crossr-skills, personas and the script in crossr-loops. "One pass" means **two stacked
PRs landed together**, loops first or with a shim, not one PR.

**Pin/shim:** crossr-loops `lockfile.toml` pins `skills = "v0-last-monolith"`. The
`rust-architect` → `architecture` rename breaks that pin unless the loops PR retargets it
in the same stack, or the catalog keeps a `rust-architect` shim (frontmatter pointing at
`architecture`) until the pin moves. Prefer the simultaneous stack; shim only if the loops
PR must lag.

**Retires as a side effect:** the dual-mandate contradiction *for the three adversary
gates*, the writer-mandate bug, and the three-vocabulary divergence. Conductor
skill-layer mandates (`axel`, `avril`) stayed until PR 4 — §2.5 was not fully
discharged here.

### PR 2 — Promote personas to runtime agents, by generation

**Files:** `crossr-loops/.agents/agents/*.md` (the source personas — renamed here to drop
the `rust-` prefix: `reviewer-agent`, `tester-agent`, `architect-agent`, per decision #1);
`crossr-harness/scripts/harness-bootstrap` (the generation step);
`crossr-skills/.opencode/agent/axel.md` and
`crossr-loops/templates/harness/opencode/agent/axel.md` (conductor entrypoints);
`crossr-loops/.agents/agents/axel-conductor-agent.md`; `crossr-loops/graphs/axel.json`.

Per decision #3, `.opencode/agent/` is **generated output, never hand-written** — the
generation step lands in `harness-bootstrap`, which already copies `.agents/agents/` into
target repos; it now also emits the OpenCode agent files from them. Hand-writing both
directories is the dual-mandate bug with a new folder name. PR 2 edits the *source*
personas' load sets; consuming repos regenerate.

The conductor entrypoint stops preloading writer and adversary skills. Fix
`requires.skills` in `axel.json` — the graph already models per-node `uses.skill` /
`uses.persona`; the bug is the flat union at graph level. Retarget graph `uses.persona`
values to the renamed personas in the same pass (`verify-graphs` gates this).

This is both the load-set fix and the thing that makes "delegate to `reviewer-agent`"
resolve to something real. **Measurable on the next AXEL session.** Spans loops + harness;
stack them like PR 1.

**Landed** as the three-PR stack:

- loops [#5](https://github.com/sycamore-hq/crossr-loops/pull/5) (2a) — personas renamed to role names; conductor load set is `axel` + `gan-verdict`; tag `v1-runtime-agents` cut on the merge commit.
- harness [#4](https://github.com/sycamore-hq/crossr-harness/pull/4) (2b) — `harness-bootstrap` generates `.opencode/agent/` from persona sources; unmarked files are never overwritten.
- skills [#108](https://github.com/sycamore-hq/crossr-skills/pull/108) (2c) — pin bump `skills = "v1-gan-layers"` / `loops = "v1-runtime-agents"`; delete unmarked `axel.md` then regenerate; plan record.

**Landed note:** `verify-skill-refs` added in 2a — graphs' `uses.skill` / `requires.skills` / `uses.persona` / `uses.graph` names are mechanically checked against the catalog and this checkout.

**§7 instrumentation:** landed on `axel-conductor-agent` invocation step 2 (persona, not law). The 2c brief's `.agents/skills/axel/SKILL.md` home was a briefing error — `axel` is loops-owned and absent from the `v1-gan-layers` catalog (`verify-docs` GONE list). No SKILL.md edit in this PR.

**Parked gaps:**

- AVRIL dual-source — **closed in PR 4.** `avril-conductor-agent` exists; `.opencode/agent/avril.md` is generated.
- Persona voice is still Rust-flavored; revisit in PR 5.
- `copy_agents` never overwrites: a `v0` checkout keeps `rust-*-agent` beside the renamed files. This catalog had none. Other dogfood repos must refresh personas on pin move (2b tripwire: `warn_orphan_personas`). This catalog's pin move is now `just regen-agents` (3c), which overwrites loop-owned copies from the pin before bootstrap.
- **Harness follow-on (landed 3b, [#5](https://github.com/sycamore-hq/crossr-harness/pull/5)):** [`crossr-harness/lockfile.toml`](https://github.com/sycamore-hq/crossr-harness/blob/main/lockfile.toml) is `skills = "v1-gan-layers"` / `loops = "v1-no-rtl"`.
- Catalog `just regen-agents` (landed 3c): bootstrap + GONE-list strip, so the next pin move is mechanical. This catalog's `/axel` stays decorative: the `axel` skill it loads is GONE-listed here.

### PR 3 — Delete `rust-team-lead` ✅ landed

**Files:** the 8 load-bearing referrers in §2.9. Leave `progress.md`, pinto tasks, and
MIGRATION alone.

`axel` already restates the entire inner GAN, so this is a deletion, not a merge.
**Intake stays three options — no fourth door.** The v2 plan artifact is produced *by* the
loop from a blessed PBI; a human-supplied plan document that never went through AVRIL is
unblessed work with better stationery. The legitimate path for "I have a design doc" is
already named: hand it to AVRIL as intent, get blessed PBIs, then AXEL. Collapse
`graphs/rust-team-lead.json` into `axel.json` or keep it as the named inner subgraph, but
delete the duplicated prose either way.

**Landed** as the three-PR stack:

- loops [#6](https://github.com/sycamore-hq/crossr-loops/pull/6) (3a) — deleted `.agents/skills/rust-team-lead/`; graph `git mv` `graphs/rust-team-lead.json` → `graphs/code-gan.json` (topology unchanged: generate → reviewer → tester → architect → commit; `axel.json` node/edges/`uses.graph` follow; `conductor` retargeted to `axel`); `axel-conductor-agent` step 7 is plain Generator; tag `v1-no-rtl` cut on the merge commit.
- harness [#5](https://github.com/sycamore-hq/crossr-harness/pull/5) (3b) — consumer pins `skills = "v1-gan-layers"` / `loops = "v1-no-rtl"`; HARNESS-SPEC + harness skills stop teaching the deleted skill.
- skills [#109](https://github.com/sycamore-hq/crossr-skills/pull/109) (3c) — catalog pin `loops = "v1-no-rtl"`; `just regen-agents`; refreshed `.agents/agents/` copies + regenerated `.opencode/agent/axel.md`; plan record.

**Graph rename:** the inner subgraph was kept, not collapsed into `axel.json`. Filename and law pointer are `code-gan`.

**`avril.md` template retention:** the plan's "delete the template entrypoints" line was overbroad. 3a deleted `templates/harness/opencode/agent/axel.md` only. **`avril.md` stayed** until PR 4 created `avril-conductor-agent` — **closed in 4a/4b.**

**`axel/SKILL.md` bytes:** 18,684 → **18,148** (536 B pairing prose). The §7 "axel under 14KB" measurable was unreachable from PR 3's file scope (Agent Personality, Status Dashboard, Mitchell, Verification, Specialization remain). Restated: PR 3 = RTL prose gone; 14 KB card split moves to PR 4.

**Writer-stack window — CLOSED in PR 4.** 3a dropped the RTL name; 4a dropped `code-writer` from the cards, `book/src/pipeline/{axel,avril}.md`, and `templates/harness/opencode/command/{axel,avril}.md`. No surviving locus in those loops files. This catalog's unmarked `.opencode/command/{axel,avril}.md` still teach `code-writer` (regen never overwrites them; `/axel` `/avril` are decorative here — GONE-listed skills).

**Parked from 3a / 3b / 3c review — discharged in PR 5:**

- `graphs/code-gan.json` nodes/`requires` named `rust-code-writer` / `rust-code-reviewer` / `rust-code-tester`. Retargeted in 5d; `requires.book: true`; the graph names no language.
- `HARNESS-SPEC.md` §6 gates 2–3 named `rust-code-reviewer` / `rust-code-tester`. Retargeted in 5e to `code-review` / `testing`.
- Landing named `rust-team-lead`; harness `verify-docs` featured-set required it. Harness half in 5e (featured set is decision 7). Landing half in 5g ([#10](https://github.com/sycamore-hq/crossr-web-landing/pull/10)).

### PR 4 — Card + `references/` split on `axel` and `avril` ✅ landed

Cheapest last, after the file has shed the Rust stack table and its own persona
block. RTL pairing prose is already gone (PR 3; `axel` was 18,148 B).

`SKILL.md` becomes the runtime card — gates, order, stop conditions. Move to
`references/`: Verification (scoring law for `skill-evaluator`, not runtime law),
Specialization, personality essays, the pinto flag encyclopedia, and the dashboard
reprint (replaced by one line: "refresh via the harness dashboard command").

**Landed** as the two-PR stack:

- loops [#7](https://github.com/sycamore-hq/crossr-loops/pull/7) (4a) — card + `references/` split; conductor mandates lift onto personas; new `avril-conductor-agent`; deleted `templates/harness/opencode/agent/avril.md`; tag `v1-cards` cut on the merge commit. Cards: `axel` **5,989** / `avril` **4,984**.
- skills [#110](https://github.com/sycamore-hq/crossr-skills/pull/110) (4b) — pin `loops = "v1-cards"`; `just regen-agents`; deleted unmarked `.opencode/agent/avril.md` (stale-target remedy — never-overwrite would have kept it forever) then regenerated from `avril-conductor-agent`; plan record.

**§7 correction (second restatement).** The PR 4 row said `axel/SKILL.md` ≤ 3KB
(the old “under 14KB” line lived here after 3c). That number is unreachable without
exiling runtime gates. Irreducible always-loaded law on the 4a tree:

| Block | Bytes |
|---|---:|
| Intake Gate | 899 |
| AXEL Method (steps 1–7, including AC evidence / board→done / next) | 2,998 |
| Strict Orchestration Rules | 969 |
| Ruthless Checklist | 480 |
| Frontmatter (card-sized) | 97 |
| **Irreducible subtotal** | **5,443** |

Opening + disclose list + activation bring the card to **5,989**. The plan's 1,963
“AXEL Method” figure matched steps 1–4 only; steps 5–7 are still gates. A 3KB card
would have to exile those. This is the **second restatement** of this measurable
(14KB → PR 4 in 3c, because pairing prose was only 536 B; 3KB → ≤6KB here). The
first was justified against PR 3's file scope. This one is sound because it is the
sum of gates the card still must load — not a wish. `avril` irreducible (portable
PBI 724 + method 1,946 + strict 611 + checklist 816) = 4,097, plus chrome →
**4,984** (≤5,000). Do not exile AC evidence or board→done to hit the old number.

**Conductor dual-mandate (§2.5) fully discharged.** PR 1 lifted mandates for the
three adversary gates only. `axel` and `avril` kept skill-layer One-Sentence
Mandates that contradicted their personas until 4a deleted them. Persona wins.
Card/command “recite” lines are gates, not a second sentence. `brick` and
`orchestrator-prompt` still carry skill-layer mandates (out of scope).

**Writer-stack window CLOSED** on the AXEL/AVRIL cards (`grep code-writer` → zero).
Conductor load set is the card + `gan-verdict`. 4a also reached
`book/src/pipeline/{axel,avril}.md` and `templates/harness/opencode/command/{axel,avril}.md`
— no surviving locus there. This catalog's unmarked `.opencode/command/{axel,avril}.md`
still teach `code-writer`; regen never overwrites them. Decorative here (GONE-listed
skills). Not a loops leak.

**AVRIL dual-source gap CLOSED.** `avril-conductor-agent` exists.
`.opencode/agent/avril.md` is GENERATED (marker present; round-trips against the
persona). `status.md` is the only remaining hand-written entrypoint.

**Dashboard home.** Blessed the parameterized pair
`axel/references/status-dashboard.md` + `avril/references/status-dashboard.md` as
the end state (same law, **board** vs **plan** noun). Do **not** inherit “dedup
into `agent-harness`” — conductors have not loaded `agent-harness` since 2a; law
lifted there would be decorative, which is worse than duplicated. That instruction
predates the load-set change.

**Owed to harness — discharged in 5e.** [`crossr-harness/lockfile.toml`](https://github.com/sycamore-hq/crossr-harness/blob/main/lockfile.toml) is `skills = "v1-one-law"`, `loops = "v1-one-law-consumers"`.

### PR 5 — One ruleset, progressively disclosed ✅ landed

**Depends on:** the PR 1 peel having landed.

Build `rust/SKILL.md` + `references/` per §3.4. Absorb `rust-errors`, the rust-*
adversary skill bodies left sitting by PR 1, **and `rust-code-writer` (7,674 B) — the
generator's copy of the same law.** Left sitting, the book is a third photocopy: the
generator writes to `rust-code-writer`, the reviewer checks book Rules, and drift between
them manufactures rejections again — §2.7 with new stationery. The generator's load set
becomes `code-writer` + the rust book (How + Rules for the situation) + domain.
`rust-code-reviewer` and `rust-code-tester` shrink to the thin gate cards `code-review`
and `testing` (the job + envelope, ~1–2 KB each). Retarget the domain skills' frontmatter
in the same pass — `rust-axum-backend`, `rust-tui`, `rust-frontend`, and `brick-coder` all
declare "activate together with `rust-code-writer`", which stops existing. Delete the duplicated
"Non-Negotiable Core Principles" — they are `code-writer` restated. Assign stable rule ids.
Add a script that extracts the Rules-only projection so the adversary load set is generated,
not hand-copied — hand-copying is what created this problem.

Domain skills (`rust-axum-backend`, `rust-tui`, `rust-frontend`) stay separate skills for now;
revisit once the reference model is proven.

**PR 5 landed** as the seven-PR stack. Tags cut on the merge commits (decision 8 — no CI;
never re-point):

- skills [#117](https://github.com/sycamore-hq/crossr-skills/pull/117) (5a) — book infrastructure + `rust/` book. Additive.
- skills [#118](https://github.com/sycamore-hq/crossr-skills/pull/118) (5b) — `ocaml/` book. Extractor zero-line diff vs 5a.
- skills [#120](https://github.com/sycamore-hq/crossr-skills/pull/120) (5c) — gate cards, absorb writers, featured = decision 7. Tag `v1-one-law` (`88d9ee2`) peels to `507c509`.
- loops [#9](https://github.com/sycamore-hq/crossr-loops/pull/9) (5d) — `skills = "v1-one-law"`; `code-gan` names no language; `requires.book` in schema + verifier. Tag `v1-one-law-consumers` (`69a05d2`) peels to `cea6e59`.
- harness [#8](https://github.com/sycamore-hq/crossr-harness/pull/8) (5e) — HARNESS-SPEC §6; lockfile `books`; empty-books smoke fixture.
- skills (5f, this PR) — catalog `loops = "v1-one-law-consumers"` at all four pin loci; `just regen-agents`; this record.
- landing [#10](https://github.com/sycamore-hq/crossr-web-landing/pull/10) (5g) — drop `rust-team-lead`; featured pills = decision 7.

Parked from PR 1a review — **discharged:**

- `architecture/SKILL.md` Core Principle 2 cited `code-writer` + `rust-code-writer`. 5c rewrote it to `code-writer` or the disclosed book's Rules projection. Verdict tokens were already final; `gan-verdict` untouched.
- Persona voice still Rust-flavored after PR 2 (the 2a park). 5d de-Rusted `.agents/agents/` and kept the three verdict-format lines.

Parked from PR 3a / 3b review — **discharged:**

- `graphs/code-gan.json` named `rust-code-writer` / `rust-code-reviewer` / `rust-code-tester`. 5d retargeted to `code-writer` / `code-review` / `testing` and added `requires.book: true`. No intermediate `rust-review` / `rust-testing` skills (shape B).
- `HARNESS-SPEC.md` §6 gates 2–3 named `rust-code-reviewer` / `rust-code-tester`. 5e retargeted them. Featured-set harness half is 5e; landing half is 5g (merged).

### PR 6 — The v2 chain

**Files:** `axel/SKILL.md`, both entrypoints, `graphs/axel.json`, `graphs/code-gan.json`
(renamed from `rust-team-lead.json` in PR 3), the architect / reviewer / tester personas;
new `plan-writer` (crossr-skills catalog).

**Includes a graph bug fix:** `graphs/axel.json`'s `plan` node currently uses
`axel-conductor-agent` as its generator persona. In v2 the plan author is the **code
Generator**, not the conductor — leave the node as-is and the conductor writes the plan it
is forbidden to write. Retarget the node's `uses.persona`.

Implement §3.5 and §3.6:

- **New catalog skill `plan-writer`** (language-neutral, ~2 KB card shape) is the plan-time
  Generator card: the claim taxonomy (§3.6), the plan artifact format and its four rules (§3.7),
  bidirectional AC↔claim mapping, append-only claim ids, and phase decomposition — which moves out
  of the conductor and becomes plan content. It is a **skill, not a persona** (decision #11).
  `code-writer` is absent from the plan window: its Data/Calculations/Actions law is diff law, and
  loading it to write a specification is the same category error PR 2 fixed on the conductor.
- Generator emits an implementation plan with a typed claim list before writing code.
- Architect moves to **plan time**; rejects for underspecification against the 30% judgment quota.
- Mechanical gate runs before any LLM gate; red never costs a token.
- Test verifier scoped to AC coverage + zero regressions (this absorbs the old "tester diet").
- Reviewer scoped to plan/AC conformance + one capped unanticipated-risk pass.
- Code-time architect escalation fires only on an unsatisfiable claim id.
- Plan loop trip limit: three architect REJECTs on one plan stops for a human (§3.5).
- Plan artifact per §3.7: `docs/plans/pbi/<id>.plan.md`, committed before implementation, immutable
  once blessed, append-only claim ids.
- Mechanical claim audit runs **before** the Architect at the plan gate: bidirectional AC↔claim
  coverage, judgment quota, id integrity. No second LLM persona at plan time.
- `axel` step 3 (Decompose) moves inside the plan, so phase boundaries are blessed rather than
  unilateral.

**This replaces the old REJECT matrix rather than patching it.** With gates ordered by blast radius
the restart rule nearly writes itself:

| Reject from | Re-run |
|---|---|
| Architect (plan time) | re-plan — no code exists, nothing to invalidate |
| Mechanical | Generator; free, no LLM |
| Test verifier | mechanical + test verifier; Reviewer only if production code changed |
| Reviewer | Reviewer only |
| Architect (escalated, code time) | full chain — rare by construction |
| Scope change | back to AVRIL — not a GAN restart |

### PR 7 — Handoff packets, envelopes, AVRIL batching

Per-conductor envelope specs (§3.3), packet format in (§3.4), and AVRIL batch review: PO
reviews the set, QA reviews the set, CTO reviews the set; `REJECT` loops the item, not the
siblings; unchanged items keep their `BLESS`.

**Required guard:** per-item `BLESS` tokens inside the batch verdict, never one blanket
`BLESS` over a set. Batching is exactly when a reviewer starts blessing by skim — without
per-item tokens you bank the savings and lose the gate.

---

## 5. Also worth doing

- **Size-route the diff gates only — never the plan gate.** Route on *touched paths*
  (public API, crate layout, module seams) **OR** size, not size alone. Below the bar the
  *diff* path may shrink to Generator → Reviewer → `just test`, but the plan gate always
  runs: a 12-line trait-boundary change is exactly the case the plan-first architect exists
  for, and skipping it would contradict acceptance condition 2.
- **Prompt-cache the immutable prefix.** Runtime card first, byte-identical across turns,
  never splice board dumps above it. Verify the host actually caches before betting on it —
  skill bodies are harness-injected and ordering may not be ours to control.
- **Model-route the roles.** Already in `orchestrator-prompt-template.md`, absent from the
  skills: cheapest pool model that passed probe for Generator and Reviewer, judge model for
  Architect and ACCEPTANCE, never dispatch labor on the orchestrator's model.
- **Don't put `voice-dna` / `unslop` on the code GAN.** Those are for human-facing prose.
  The code path should not pay ~20KB to sound like a person.

---

## 6. Do not cut

- **Three distinct adversary roles.** Collapsing them into one voice is how the product dies.
- **The `BLESS` token and silence ≠ approval.** Cheap to keep, and it is the anti-collusion
  property everything else rests on.
- **Blessed intake.** AXEL executing unblessed scope is how you spend tokens on work you
  throw away.
- **"Conductor writes no code."** That is the load-set constraint in PR 2, not decoration.
- **SKILL.md as law, graphs as maps.** Do not invent a second law document to save tokens.
- **The LLM Tester** (PR 6 starves its input, does not delete it).
- **Per-item BLESS** when AVRIL batches (PR 7).
- **The reviewer's unanticipated-risk pass.** Conformance-only review misses defects that neither
  the plan nor the AC anticipated. Cap it at three findings; do not delete it.
- **The judgment-claim quota.** Without it, "mechanically verifiable" degrades into a plan of
  unfalsifiable prose and the architect gate becomes theatre.
- **Plan immutability after blessing.** A plan the Generator can edit post-hoc turns conformance
  review into self-grading. Commit it before the code, or the reviewer gate is decorative.
- **`plan-writer` as a skill, not a role.** Promoting it to a persona splits plan from implementation
  and blinds the §3.6 escalation tripwire. Split only on the decision #11 evidence.
- **One adversary per artifact type.** Adding the reviewer or test verifier to the plan gate buys a
  duplicate architectural opinion and multiplies iterations on the chattiest loop in the chain.
- **The plan gate, at every size.** Size-routing may shrink the diff gates; it never skips the
  plan gate. The small seam change is the plan-first architect's canonical case.
- **Blessed intake, three doors only.** A plan document is an artifact of a blessed PBI, never a
  way in. Design docs enter through AVRIL as intent.

---

## 7. Measurement

There is no instrumentation today. `orchestrator-prompt-template.md` ledgers tokens per
ticket; the in-harness loops ledger nothing. Every number in this plan — and every number
about whether it worked — is otherwise an estimate.

Add to the conductor card in PR 2: **record load-set bytes at session start.** Baseline is
73,031 bytes for a naive Rust AXEL conductor window. **Landed in 2a** on
`axel-conductor-agent` invocation step 2 (persona, not the catalog `axel/SKILL.md` — that
skill is loops-owned). Measured conductor window after 2c regenerate: `axel` + `gan-verdict`
= 19,816 bytes. After PR 3 (`axel` 18,148): **19,280**. After PR 4 (`axel` 5,989):
**7,121**.

Per-PR success criteria:

| PR | Measurable |
|---|---|
| 0 | `skill-evaluator` scores a de-personaed skill ≥ its pre-split score |
| 1 | `verify-protocol` passes; one mandate per role; `gan-verdict` exists; zero writer prerequisites left in adversary skills or persona files |
| 2 | Conductor load-set bytes drop from 73,031; adversary skills absent from the conductor window; `.opencode/agent/` files carry a generated-do-not-edit header |
| 3 | `rust-team-lead` gone from all 8 load-bearing referrers; pairing prose 536 B (`axel` 18,148). 14 KB card split is PR 4 |
| 4 | `axel` **5,989** (irreducible gates **5,443**: Intake 899 + Method 2,998 + Strict 969 + Checklist 480 + frontmatter 97). `avril` **4,984** (irreducible 4,097). Floor is the always-loaded law, not a wish — ≤3KB could only be met by exiling AC evidence / board→done. Second restatement (14KB → PR 4 in 3c; 3KB → ≤6KB here); this one is sound because it is the sum of gates the card still must load. `references/` carries Verification and Specialization |
| 5 | One universal writer skill (`code-writer`) plus one book per language. Zero `<lang>-code-writer` skills remain — `rust-code-writer`, `rust-errors` and `ocaml-code-writer` absorbed. Rules projections generated per book and drift-detectable, gated by review discipline (decision 8); gate cards ≤2 KB and book-agnostic; the `code-gan` graph names no language. Measured on the 5f tree: rust **52** rules (`RULES.md` 5,142 B), ocaml **75** rules (`RULES.md` 13,442 B); `code-review` **1,454** B / `testing` **1,734** B (both ≤2 KB). Reviewer load set is the gate card + `RULES.md` (rust 1,454 + 5,142 = **6,596** B) against the pre-PR reviewer skill at 5,059 B. |
| 6 | `plan-writer` exists and `code-writer` is absent from the plan-time window; architect rejections occur at plan time, not after implementation; zero LLM tokens spent on a mechanically-red phase or an audit-red plan; bidirectional AC↔claim coverage passes by script; plan commit precedes first implementation commit |
| 7 | Adversary windows carry no sibling SKILL.md, no board dump, no prior-phase prose |

Two acceptance conditions for the whole plan:

1. **An Elm or Melange AXEL run works.** It loads `code-writer` + the axel card + the disclosed
   language writer, with `architecture` / `code-review` / `testing` in the subagents — and it runs,
   instead of halting or reviewing Elm against `thiserror` rules.
   **Status after PR 5:** unblocked, not demonstrated. With the book split and the neutral
   graph, an Elm run loads `code-writer` + the axel card + the universal gate cards and does
   not halt. What remains before it can be shown live is an `elm` book and `books = ["elm"]`
   in that repo's lockfile.
2. **No architect rejection ever discards a finished implementation.** Every seam objection is
   raised against a plan. Track the count of code-time architect escalations; it should trend to
   near zero, and each one is a signal that the plan's claim list was too weak.

Track alongside these: rejections per rule id (which reference needs a better *How* section), and
mechanical-gate catches (each one is an LLM cycle that did not happen).

---

## 8. Decisions and remaining questions

Questions 1–5, 10, 11 are now **decided in the body**; 1–5 and 10 were load-bearing for PR 1 and
a plan that says "decide before PR 1" and then doesn't is not a plan.

| # | Question | Decision |
|---|---|---|
| 1 | Naming | Skill = activity (`architecture`, `code-review`, `testing`). Persona = role (`architect-agent`, …). Book = language (`rust`). |
| 2 | Delta mechanism | **None.** Shape B (§3.1): language law lives in `rust/references/`; no intermediate delta skills. |
| 3 | Two agent directories | `.opencode/agent/` is **generated** from `.agents/agents/` at bootstrap. One hand-written source; two hand-written copies is the dual-mandate bug reborn. |
| 4 | Envelope location | Field schema in `gan-verdict`, last in the prompt; conductor selects fields and fills values (§3.3). No `contracts/` tree. |
| 5 | "Material change" trigger | **Superseded by PR 6.** The escalation trigger is an unsatisfiable claim id; the old matrix no longer exists to need it. |
| 10 | Plan artifact location | `docs/plans/pbi/<id>.plan.md`, committed before implementation, immutable once blessed (§3.7). |
| 11 | Plan authorship | **`plan-writer` is a skill, not a persona.** The plan and the diff are different artifacts needing different law, so the Generator loads a different card per phase (§3.2). It is not a second *role*: (a) §3.5's saving depends on the plan being the implementer's own cheap draft — a separate author makes it spec-handoff; (b) §3.6's "cannot satisfy claim N" tripwire and §7 acceptance condition 2 ("escalations trend to near zero") stop being measurable once the planner lacks the implementer's codebase knowledge, since unsatisfiable claims become routine; (c) the self-serving-plan hazard is already caught mechanically (underspecification REJECT, 30% quota, bidirectional coverage `comm`) — an LLM-layer fix for a scripted check violates *mechanical before LLM*; (d) a second persona at the plan gate multiplies iterations on the chain's most-iterated loop, the same cost argument that keeps the reviewer and test verifier out (§3.5). **Revisit when:** code-time architect escalations trend to near zero *while* architect plan-REJECTs are dominated by satisfiable-but-self-serving plans that the quota and coverage script passed. |
| 12 | Restating a landed measurable | **Landed §7 rows are frozen.** A row freezes when its PR merges: from then on it is the contract that PR was blessed against — a historical fact, not a current target. A restatement is a **new line naming the row it supersedes**; never an in-place overwrite. Rows for unlanded PRs are drafts and may be edited freely — **the rule starts at merge, not at first draft**, or §7 becomes a scratch pad. *This is not §3.7 rule 2 applied to the plan itself*: claim ids are append-only because they are **citations**; §7 rows are **criteria**, and they freeze because a landed criterion is a fact. No file split, no script, and **no retrofit** of rows already landed — 4b's PR 4 row already carries the 14 KB → ≤3 KB → ≤6 KB chain in prose, and rewriting settled rows to demonstrate a convention serves no reader. Rebase immediately before merge stays process, not tooling. *Why:* #111 vs 4b — a stale-base amendment still carried `≤3KB` while `main` carried the 5,989 / 5,443 derivation. A resolver who does not know which side is the contract can silently revert a landed number; append-shaped hunks do not prevent that resolve, this decision is what makes it illegal. |

Still open, none blocking PR 1:

1. **Is the judgment quota 30%?** A starting cap, not a law. Instrument on real plans before
   hardening; do not block PR 6 on the number.
2. **Mechanical command registries.** Two is fine: the harness owns `just test` / `just clippy`;
   each book reference owns its per-rule `check:` line. A merger script can come later if the
   split ever bites.
3. **`brick`.** Wait. It is language-clean with its own stage skills; let the AXEL path prove
   the model first. The sibling reasoning that parked a second language (OCaml) was
   **overruled before dispatch**. The pre-dispatch recommendation was to park OCaml; a
   single book cannot prove the infrastructure is language-agnostic, which is the property
   Elm / TypeScript / JavaScript targets depend on. 5b's extractor zero-line diff vs 5a is
   the evidence that it does. `brick` itself stays parked.
4. **Domain skills** (`rust-axum-backend`, `rust-tui`, `rust-frontend`). Stay skills until the
   book is proven, then become book references if the model holds.

### PR 5 decisions (settled in the prompt-set stack; the plan did not previously contain them)

- **Projection contract vs per-book topic sets.** Topic files carry `## Rules` + `## How`.
  Which topics a book has is the book's business. The extractor never hardcodes a topic list.
- **`<book>/RULES.md` placement.** Generated, committed, outside `references/` so the
  extractor never ingests its own output.
- **`requires.book`.** A graph that needs a disclosed book sets `requires.book: true` and
  must not *name* a book skill. Empty `books = []` on a consumer lockfile is a 5e smoke
  failure, not a loops self-pin failure.
- **Lockfile `books` declaration.** Disclosure filter, not a copy filter. Bootstrap still
  copies every skill directory. Multi-book: disclose per PBI, or stop and ask; never
  default to first-listed.
- **Book marker is `metadata.book: "true"`** (quoted). Frontmatter, not a top-level key.
  Same marker `extract-rules` and `verify-skill-refs` select on.
- **Featured set (decision 7):** `code-writer`, `rust`, `code-review`, `agent-harness`,
  `skill-evaluator`.
- **Open prefix registry.** `docs/book-topics.md` is the only home. Extractor accepts
  unknown prefixes. `check:` does not count against the 3-line cap.
- **Contract vs topic references.** `specialization.md` / `verification.md` carry neither
  `## Rules` nor `## How`. Extractor skips them.
- **No CI (decision 8).** Tags cut after pasted validation. Gates in this stack are
  drift-detectable, gated by review discipline.
