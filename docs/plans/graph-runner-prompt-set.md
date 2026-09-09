# Plan: graph-runner

Prompt set for [work#14](https://github.com/sycamore-hq/work/issues/14)
(`graph-runner`, repo `crossr-loops`). Parked at split-09 as "not this chain"
(`docs/plans/skills-loops-harness-split.md` "Not this chain"). This file is
the chain. It is written in the plan-artifact shape so `just plan-audit
docs/plans/graph-runner-prompt-set.md` gates it, and
`test/test_graph_runner_prompt_set.py` keeps it gated. No HTML twin.

Answers 1–6 (2026-09-09) are folded into the decisions table: serde
approved; explicit `start` key (R0); toolchain pinned; one book sentence;
`verify-graphs` shells out to cargo; ledger unparked.

Preconditions, measured 2026-09-09 on `origin/main` of each remote:

| repo | head | `skills` pin | `loops` pin | Rust crates |
|---|---|---|---|---|
| crossr-loops | `9e5b3f1` | `v1-packets` | `v1-cards` | none (`justfile` already says `cargo … \|\| echo "(no Rust crates)"`) |
| crossr-skills | `8b67bda` | — | `v1-packets-consumers` | none |
| work | `acc37fa` | — | — | — |

Loops gates on `9e5b3f1`: `verify-graphs` PASS (5 graphs), `verify-protocol`
PASS (7 adversary nodes, 17 checks), `python3 -m unittest discover -s test`
71 OK.

---

## What the runner is

A **stepper and replayer** over `graphs/*.json`. Give it a graph and a finite
list of events (the graphs' own `when` labels), and it walks the map and
prints the path. Exit 0 means the events reached a sink; anything else is
named on stderr. It calls no model, spawns no process, and never reads a
`SKILL.md`. Its only new capability is **mechanical replay**: a conductor's
recorded verdict sequence can be checked against the topology the same way
`audit-packet` checks a packet — red costs no LLM token.

What it is not, and this chain does not change: not an executor, not Rhai,
not an OpenCode-native runtime, not a second law. `SKILL.md` still wins over
a graph, and the graph still wins over the runner (the runner reads the graph;
nothing reads the runner).

## Decisions settled BEFORE dispatch

| # | Decision |
|---|---|
| 1 | Rust crate `runner/` in `crossr-loops` (workspace root `Cargo.toml`, binary `graph-runner`). Dependencies: `serde` + `serde_json` for the JSON (approved 2026-09-09), `thiserror` for typed errors. Nothing else — argv is hand-parsed. Edition `2021` and `rust-version = "1.94"` in `runner/Cargo.toml`; `rust-toolchain.toml` at the workspace root pins `channel = "1.94.1"` (the toolchain measured on the authoring container). Toolchain bumps follow the pin rule (answer 7, 2026-09-09): a bump is its own commit that says why, never inside a feature PR, never a side effect. |
| 2 | Stepper, not executor. No `std::process::Command`, no network crate, no interpreter. Events come from the caller. The runner never decides a verdict. |
| 3 | Semantics. Start node = the graph's required top-level `start` key, which must name a node (R0 adds it to `schema.json`, every graph, and `verify-graphs`; document order and in-degree are not the rule — `avril` and `code-gan` have no in-degree-0 node). Sink = a node with no out-edges (`code-gan/commit` is a `gate` sink; `role: terminal` is a sink by construction). An unlabeled edge fires on the reserved event `next`; a graph whose edge carries `when: "next"` fails to load. An adversary node accepts `BLESS` / `REJECT` and nothing else. Two out-edges of one node with the same label (or both unlabeled) fail to load as ambiguous. An event with no matching out-edge fails loud, naming the node and its accepted labels. |
| 4 | Completion. A walk is complete iff it stands on a sink at depth 0 with the event list exhausted. Events left over after a sink → `trailing events`. Events exhausted before a sink → `incomplete at <graph>:<node>`. Exit 0 / 1 / 2 (usage). |
| 5 | Descent (R3). A `role: graph` node descends into `<dir>/<uses.graph>.json` at that graph's `start`; the subgraph's sink returns to the parent node, and the **next** event selects the parent's out-edge. `--flat` treats the node as opaque. Descent is the default from R3 on; R2 commits walks only for graphs without `graph` nodes. |
| 6 | Walk files. `graphs/walks/<graph>.<name>.walk`, one event per line, `#` comments, blank lines ignored. The prefix before the first `.` names the graph. Committed. `graph-runner cover graphs` replays every walk (descent on) and reports every `(graph, edge)` no walk took; `cargo test` fails while that count is above zero. From R3, `scripts/verify-graphs` shells out to `cargo run -q -p graph-runner -- cover graphs` whenever `runner/Cargo.toml` exists and fails when cargo is missing or the count is above zero — no silent skip. `just graphs-cover` stays as the direct target. |
| 7 | `graphs/schema.json` stays the shape authority and `verify-graphs` stays the shape gate. The Rust loader is a consumer: `deny_unknown_fields`, the same role enum, and a test that reads the schema's role enum and compares it to the Rust enum so the two cannot drift silently. The schema and the five graphs change once, in R0, by the `start` key alone, and are byte-identical across R1–R3. |
| 8 | Not this chain: bootstrap installing the runner in consumers; a conductor card or persona invoking it; Rhai; OpenCode-native execution; a tag; a pin move. `lockfile.toml` is untouched. |
| 9 | The `justfile` fallbacks `\|\| echo "(no Rust crates)"` are deleted in R1. Once a crate exists they would swallow a red `cargo test`. |
| 10 | Docs move with the code: `graphs/GRAPH.md`, `README.md` Graphs line, `AGENTS.md` "topology, not a runtime" line, and one sentence in `book/src/pipeline/overview.md` after "Topology (not law)" naming the replayer. `progress.md` + `features.json` gain a `graph-runner` phase with one row per PR. Nothing else in `book/`. |
| 11 | No CI (standing decision 8 from PR 5 / PR 7). Every brief's VALIDATE output is pasted in the PR body and re-run on the merge commit. |
| 12 | Ledger. `work.json` `graph-runner` flips `parked` → `todo` / `planned` with this file as `source` (this prompt set's own PR in `work`). R4 flips it to `done`. `just project-roadmap` refreshes issue #14's labels — the human runs it (org write). |

---

## Status (measured 2026-09-09)

| PR | Repo | State | Evidence |
|---|---|---|---|
| R0 | loops | Not started | No `start` key in `graphs/schema.json` on `9e5b3f1`. |
| R1 | loops | Not started | No `Cargo.toml` on `9e5b3f1`. Blocked by R0. |
| R2 | loops | Not started | Blocked by R1. |
| R3 | loops | Not started | Blocked by R2. |
| R4 | work | Not started | `work.json` `graph-runner` is `parked`; this prompt set's PR makes it `todo`. |

---

## Phases

Stack order is merge order. Each loops PR is one reviewable unit; each
appends its own `progress.md` row and `features.json` commit row under the
`graph-runner` phase.

### Phase 1 of 5: R0 — loops: explicit `start` in schema, graphs, verify-graphs
- est. LOC: 60
- `graphs/schema.json` gains required `start` (node-id pattern); each of the five graphs gains `"start": "<entry node>"`; `scripts/verify-graphs` allows the key, requires it, and checks it names a node; `graphs/index.html` regenerated.

### Phase 2 of 5: R1 — loops: crate scaffold, typed graph model, `check`
- est. LOC: 440
- Workspace `Cargo.toml` + `rust-toolchain.toml` + `runner/` crate; `Graph` / `Node` / `Role` / `Edge` / `NodeId` / `Label` types; loader with `deny_unknown_fields`; load-time checks (reserved `next`, ambiguous edges, edge endpoints, `uses.graph` exclusive of `uses.skill`); `graph-runner check <dir>`; justfile fallbacks deleted; `runner-check` target.

### Phase 3 of 5: R2 — loops: stepper, `walk`, happy-path walks
- est. LOC: 450
- `Event` type (`Next` | `Verdict` | `Label`); pure `step` and `walk`; trace rendering; `graph-runner walk <graph.json> <walk-file>`; walk files for `avril`, `code-gan`, `brick`; unmatched-event and adversary tests.

### Phase 4 of 5: R3 — loops: descent, `cover`, full edge coverage, docs
- est. LOC: 450
- Subgraph descent with depth in the trace; `--flat`; `graph-runner cover <dir>`; walks for `axel` and `flagship` plus the REJECT / fail / missing-evidence / unsatisfiable-claim walks so every edge is taken; `cargo test` gate on zero uncovered edges; `verify-graphs` shells out to cover; GRAPH.md / README / AGENTS.md / book overview wording.

### Phase 5 of 5: R4 — work: ledger close
- est. LOC: 30
- `work.json` `graph-runner` → `done` with the three loops PR numbers and merge SHAs; board regenerated; `progress.md` line.

---

## Acceptance Criteria

- AC-01: `graph-runner` loads every committed `graphs/*.json` into typed domain values and refuses unknown keys, unknown roles, dangling edge endpoints, ambiguous out-edges, a `start` that names no node, and the reserved label `next`.
- AC-09: Every graph names its entry node in a required `start` key; `schema.json` and `verify-graphs` enforce it, and the five graphs change by that key alone.
- AC-02: The runner is a stepper and replayer only — no model call, no process spawn, no network, no interpreter, no `SKILL.md` read.
- AC-03: Stepping semantics are fixed and observable: start is the graph's `start` node, a sink has no out-edges, unlabeled edges fire on `next`, adversary nodes accept only `BLESS` / `REJECT`, an unmatched event fails loud naming the node and its accepted labels, and the exit code says whether the walk completed.
- AC-04: `role: graph` nodes descend into the referenced graph and return at its sink; `flagship` replays to its sink through `avril`, `axel`, and `code-gan`.
- AC-05: Every edge of every committed graph is taken by at least one committed walk under `graphs/walks/`, proven by `graph-runner cover`, gated by `cargo test`, and re-run by `verify-graphs` through cargo.
- AC-06: The existing gates stay green and the law stays byte-identical: `verify-graphs`, `verify-protocol`, `verify-skill-refs`, the Python tests; `graphs/*.json` and `graphs/schema.json` unchanged across R1–R3, every `SKILL.md`, every persona, and `lockfile.toml` unchanged across R0–R3.
- AC-07: The `just` ritual runs the Rust matrix for real — no `|| echo` fallback — on a pinned toolchain, and `cargo fmt --check`, `cargo clippy` (pedantic, `-D warnings`), and `cargo test` are green on every loops PR.
- AC-08: Docs and trackers say what the runner is and is not (GRAPH.md, README, AGENTS.md, the book overview, `progress.md`, `features.json`), name no Rhai and no OpenCode executor as a capability, and the work ledger closes `graph-runner`.

## Claims

- C-01: mechanical · AC-01 · `cargo run -q -p graph-runner -- check graphs` → exit 0, one `✓` line per graph, `5 graphs OK`
- C-02: mechanical · AC-01 · `cargo test -p graph-runner load_` → tests `load_rejects_unknown_key`, `load_rejects_unknown_role`, `load_rejects_dangling_edge`, `load_rejects_ambiguous_out_edges`, `load_rejects_reserved_next`, `load_rejects_start_naming_no_node` pass
- C-03: mechanical · AC-01, AC-03 · `cargo test -p graph-runner role_enum_matches_schema` → the `role` enum read from `graphs/schema.json` equals the Rust `Role` variants, in order
- C-04: observable · AC-02 · `runner/Cargo.toml` `[dependencies]` lists exactly `serde`, `serde_json`, `thiserror`
- C-05: mechanical · AC-02 · `rg -n 'process::Command|rhai|reqwest|SKILL\.md|std::net' runner/src` → 0 hits
- C-06: mechanical · AC-03 · `cargo run -q -p graph-runner -- walk graphs/avril.json graphs/walks/avril.happy.walk` → exit 0, last trace line ends at `stop`
- C-07: mechanical · AC-03 · `printf 'next\nfail\n' > /tmp/bad.walk && cargo run -q -p graph-runner -- walk graphs/avril.json /tmp/bad.walk` → exit 1, stderr names `po` and `BLESS, REJECT`
- C-08: mechanical · AC-03 · `cargo test -p graph-runner step_` → tests `step_unlabeled_edge_fires_on_next`, `step_adversary_rejects_non_verdict`, `step_start_is_the_start_key`, `step_sink_has_no_out_edges`, `walk_trailing_events_fail`, `walk_incomplete_names_node` pass
- C-09: mechanical · AC-04 · `cargo run -q -p graph-runner -- walk graphs/flagship.json graphs/walks/flagship.happy.walk` → exit 0, trace shows depth 1 lines for `avril` and `axel` and depth 2 lines for `code-gan`
- C-10: mechanical · AC-05 · `cargo run -q -p graph-runner -- cover graphs` → `uncovered edges: 0`, exit 0
- C-11: mechanical · AC-05 · `cargo test -p graph-runner committed_walks` → every `graphs/walks/*.walk` replays to a sink and `cover` reports zero uncovered edges
- C-12: mechanical · AC-06 · `git diff --stat origin/main..HEAD -- graphs/*.json graphs/schema.json .agents lockfile.toml` → empty on R1, R2, and R3 (and `-- .agents lockfile.toml` empty on R0)
- C-13: mechanical · AC-06 · `./scripts/verify-graphs && ./scripts/verify-protocol && python3 -m unittest discover -s test && CROSSR_SKILLS_PATH=<v1-packets checkout> ./scripts/verify-skill-refs` → PASS, PASS, OK (71 tests), PASS
- C-14: mechanical · AC-07 · `rg -n 'no Rust crates' justfile` → 0 hits
- C-15: mechanical · AC-07 · `cargo fmt --all --check && cargo clippy --workspace --all-targets --all-features -- -D warnings -W clippy::pedantic && cargo test --workspace` → exit 0
- C-16: mechanical · AC-08 · `rg -in 'rhai' graphs/GRAPH.md README.md AGENTS.md runner/ | rg -v -i 'no rhai'` → 0 lines
- C-17: observable · AC-08 · `graphs/GRAPH.md` states: start is the `start` key, a sink has no out-edges, `next` is the unlabeled-edge event, `SKILL.md` wins, the runner replays and never runs
- C-18: mechanical · AC-08 · in `work`: `python3 -m unittest discover -s test && python3 scripts/work-board --markdown` → OK and `graph-runner` absent from Startable / Held / In flight
- C-19: judgment · AC-02 · the trace vocabulary is the graphs' own labels and nothing a conductor could mistake for a verdict or an instruction
- C-20: judgment · AC-08 · GRAPH.md and README stay honest about "map, not executor" once a stepper exists
- C-21: mechanical · AC-01 · `test -f Cargo.lock && rg -n '^target/$' .gitignore` → both present
- C-22: mechanical · AC-06 · `git -C ../crossr-harness diff --stat origin/main..HEAD` → empty (the harness remote is untouched by this chain)
- C-23: mechanical · AC-09 · on R0: `git diff origin/main..HEAD -- 'graphs/*.json' ':!graphs/schema.json' | rg '^[+-]\s' | rg -v '"start"'` → 0 lines, and `rg -c '"start":' graphs/avril.json graphs/axel.json graphs/brick.json graphs/code-gan.json graphs/flagship.json` → 1 per graph (5 files)
- C-24: mechanical · AC-09 · on R0: `python3 -c 'import json;print("start" in json.load(open("graphs/schema.json"))["required"])'` → `True`; `./scripts/verify-graphs` → PASS; a `/tmp` copy of `avril.json` with `start` deleted, and one with `start: "nope"`, each → FAIL naming `start`
- C-25: mechanical · AC-07 · `rg -n '^channel = "1.94.1"' rust-toolchain.toml && rg -n '^rust-version = "1.94"' runner/Cargo.toml && rg -n '^edition = "2021"' runner/Cargo.toml` → three hits
- C-26: mechanical · AC-05 · on R3: `./scripts/verify-graphs` → output contains `uncovered edges: 0`; `PATH=/usr/bin:/bin ./scripts/verify-graphs` (no cargo) → exit 1 naming `cargo` and `rust-toolchain.toml`
- C-27: mechanical · AC-05 · `python3 -m unittest discover -s test -k cover` → `parse_cover` tests pass (a pure parse of the cover output: count found, count missing, non-zero count)
- C-28: observable · AC-08 · `book/src/pipeline/overview.md` carries one sentence after "Topology (not law)" naming `graph-runner` as a replayer that never runs a loop

## Preserve

- PV-01 → C-12: every `graphs/*.json` and `graphs/schema.json` byte-identical across R1–R3; every `SKILL.md` and persona byte-identical across R0–R3
- PV-02 → C-13: the three Python gates and the 71 loops unittest cases keep passing
- PV-03 → C-16: the split-09 promise — no Rhai, no OpenCode-native executor, no interpreter
- PV-04 → C-22: bootstrap, HARNESS-SPEC, and every consumer pin untouched; no tag cut

---

## Shared guardrails (paste into every brief verbatim)

```
GUARDRAILS (crossr v2 review standard — violations get the PR rejected):
- Read AGENTS.md and graphs/GRAPH.md in the repo you are editing, then
  docs/plans/graph-runner-prompt-set.md in crossr-skills (the decisions table
  is the law for this chain), before writing anything.
- The runner reads graphs/*.json and nothing else. It never reads a SKILL.md,
  never calls a model, never spawns a process, never opens a socket. Paste
  `rg -n 'process::Command|rhai|reqwest|SKILL\.md|std::net' runner/src` (0 hits)
  in the PR body.
- graphs/*.json and graphs/schema.json change only in R0, only by the `start`
  key. .agents/ and lockfile.toml never change. Paste `git diff --stat
  origin/main..HEAD -- graphs/*.json graphs/schema.json .agents lockfile.toml`
  (empty after R0) in the PR body.
- Dependencies are exactly serde, serde_json, thiserror (approved 2026-09-09).
  No clap, no anyhow, no rhai. A new crate is a REJECT. Toolchain is
  rust-toolchain.toml `1.94.1`; do not bump it inside a feature PR.
- Rust matrix on every commit: cargo fmt --all --check; cargo clippy
  --workspace --all-targets --all-features -- -D warnings -W clippy::pedantic;
  cargo test --workspace. Paste the output. Do not #[allow] your way past
  pedantic; fix it or justify the single allow in the PR body.
- Data / Calculations / Actions: graph types are data; step / walk / cover are
  pure functions with unit tests; file reads, argv, and stdout live in main.rs
  only. Never write generated output by hand (graphs/index.html only via
  ./scripts/verify-graphs --html, and it does not change here).
- Loop gates on every commit: ./scripts/verify-graphs, ./scripts/verify-protocol,
  python3 -m unittest discover -s test, and
  CROSSR_SKILLS_PATH=<checkout of tag v1-packets> ./scripts/verify-skill-refs.
  Paste the output.
- progress.md: append your row under `## graph-runner`; never rewrite history.
  features.json: one commit row under the `graph-runner` phase. Nothing else
  in either file.
- Scope is the declared file list. Scope creep is a REJECT. No tag, no pin move,
  no bootstrap change. book/ changes only in R3, only the one overview.md
  sentence.
- There is no CI. Re-run your pasted VALIDATE on the merge commit.
```

---

## Brief R0 — loops: explicit `start` in schema, graphs, verify-graphs

```
You are implementing graph-runner R0 in sycamore-hq/crossr-loops.
Precondition: origin/main is at or after 9e5b3f1; graphs/schema.json has no
`start` property.

[paste GUARDRAILS]

GOAL: every graph names its entry node explicitly (decision 3). Today the
entry is implied by document order, and `avril` / `code-gan` have no
in-degree-0 node, so nothing mechanical can recover it. This PR is Python
and JSON only — no crate yet.

FILES (the whole list):
  graphs/schema.json     add `"start": {"type": "string", "pattern":
                         "^[a-z][a-z0-9-]*$", "description": "Entry node id.
                         The runner starts here; document order is not the
                         rule."}` under properties, and "start" to `required`.
  graphs/avril.json      "start": "generator"
  graphs/axel.json       "start": "intake"
  graphs/brick.json      "start": "task-division"
  graphs/code-gan.json   "start": "generate"
  graphs/flagship.json   "start": "intent"
                         Place the key after "name" so the diff is one line
                         per file. Nothing else in these files changes.
  scripts/verify-graphs  ALLOWED_GRAPH gains "start"; validate() fails
                         `<name>: missing start` when absent and
                         `<name>: start <id!r> is not a node` when dangling.
                         Keep the pass line shape; append `start <id>` to it.
  graphs/index.html      regenerate with ./scripts/verify-graphs --html only.
  test/test_verify_graphs_start.py
                         pure tests over vg.validate with fixture graphs:
                         missing start fails, dangling start fails, present
                         start passes. Load the script the way test_pr7.py
                         loads verify_graphs.
  progress.md, features.json one row each (phase "graph-runner" created
                         here: status in_progress, commit gr-r0 "explicit
                         start in schema, graphs, verify-graphs", features
                         ["schema-start", "graph-start-keys",
                         "verify-graphs-start"]).

VALIDATE (paste all of it):
  git diff origin/main..HEAD -- 'graphs/*.json' ':!graphs/schema.json' | rg '^[+-]\s' | rg -v '"start"' → 0 lines (C-23)
  rg -c '"start":' graphs/avril.json graphs/axel.json graphs/brick.json graphs/code-gan.json graphs/flagship.json → 1 per file, 5 files (C-23)
  python3 -c 'import json;print("start" in json.load(open("graphs/schema.json"))["required"])' → True (C-24)
  ./scripts/verify-graphs                                     → PASS, 5 graphs, each line names its start (C-24)
  cp graphs/avril.json /tmp/g/avril.json (dir with schema.json) and delete
  start → ./scripts/verify-graphs against it fails naming `start`; set
  start "nope" → fails naming `start` and `nope` (C-24; run the validate
  function from a python one-liner if the script has no --dir flag — do not
  add a flag for the demo)
  ./scripts/verify-graphs --html; git status --short graphs/index.html → regenerated once, second run clean
  git diff --stat origin/main..HEAD -- .agents lockfile.toml   → empty (C-12)
  ./scripts/verify-protocol; python3 -m unittest discover -s test;
  CROSSR_SKILLS_PATH=<v1-packets checkout> ./scripts/verify-skill-refs → PASS/OK/PASS (C-13)
Stack line in the PR body: merges first; R1 follows; no tag.
```

---

## Brief R1 — loops: crate scaffold, typed graph model, `check`

```
You are implementing graph-runner R1 in sycamore-hq/crossr-loops.
Precondition: R0 merged (every graph has a `start` key); origin/main has
no Cargo.toml.

[paste GUARDRAILS]

GOAL: a typed Rust reading of graphs/*.json that refuses what schema.json
refuses, plus `graph-runner check`. No stepping yet.

FILES (the whole list):
  Cargo.toml                 workspace: members = ["runner"], resolver = "2"
  Cargo.lock                 committed (binary crate)
  rust-toolchain.toml        [toolchain] channel = "1.94.1", components =
                             ["rustfmt", "clippy"] (decision 1)
  .gitignore                 add `target/`
  runner/Cargo.toml          name = "graph-runner", edition = "2021",
                             rust-version = "1.94",
                             deps: serde (derive), serde_json, thiserror
  runner/src/lib.rs          pub mod graph; pub mod load;
  runner/src/graph.rs        data: Graph, Node, Role, Edge, NodeId, Label, Uses
  runner/src/load.rs         action + checks: read a file → Graph; load_dir
  runner/src/main.rs         argv → `check <dir>`; exit 0/1/2
  runner/tests/load.rs       tests named in C-02 / C-03
  justfile                   see below
  progress.md, features.json one row each

DOMAIN TYPES (encode the schema, do not re-invent it):
  - Role enum: Generator, Adversary, Stage, Gate, Terminal, Graph — serde
    rename_all = "kebab-case". A test reads graphs/schema.json
    (properties.nodes.items.properties.role.enum) and asserts it equals
    Role::ALL rendered the same way, in order (C-03).
  - Node { id: NodeId, role: Option<Role>, catalog: Option<bool>,
    batch: Option<bool>, uses: Option<Uses> }; Uses { skill, persona, graph }
    all Option<String>. deny_unknown_fields on every struct.
  - Edge { from: NodeId, to: NodeId, when: Option<Label> }.
  - Graph { #[serde(rename = "apiVersion")] api_version (const
    "crossr-loops/v0" checked after parse), kind, name, start: NodeId,
    title, description, conductor: Option<String>, nodes, edges, requires }.
    `requires` is Option<Requires { skills: Option<Vec<String>>,
    book: Option<bool> }>.
  - NodeId and Label are newtypes over String (Display, Eq, Hash, Ord).
  - Label::NEXT = "next" is reserved (decision 3).

LOAD-TIME CHECKS (typed LoadError via thiserror; every variant names the
graph and the node/edge):
  - nodes non-empty; duplicate node ids; edge endpoints not nodes;
  - `start` names no node → StartNotANode { graph, start };
  - two out-edges of one node with the same `when` (or both unlabeled) →
    AmbiguousOutEdges { node, label: Option<Label> };
  - `when: "next"` → ReservedLabel;
  - uses.graph together with uses.skill → ExclusiveUses;
  - uses.graph == graph name → SelfReference.
  These mirror verify-graphs. They do not replace it: verify-graphs is the
  gate, the runner is a consumer (decision 7). Do not check persona / skill
  file existence — that is verify-skill-refs' job and needs the catalog.

CLI: `graph-runner check <dir>` loads every *.json except schema.json,
prints `  ✓ <name>: <n> nodes, <m> edges, start <start>, sinks [<ids>]`
per graph and `✓ <k> graphs OK`, exit 0; any LoadError → the error on
stderr, exit 1; bad argv → usage on stderr, exit 2. Hand-parse argv; no clap.

JUSTFILE (decision 9):
  check:        cargo check --workspace --all-targets
  test:         python3 -m unittest discover -s test -v
                cargo test --workspace
  runner-check: cargo fmt --all --check
                cargo clippy --workspace --all-targets --all-features -- -D warnings -W clippy::pedantic
                cargo test --workspace
  graphs-check: cargo run -q -p graph-runner -- check graphs
  Delete both `2>/dev/null || echo "(no Rust crates)"` fallbacks. Keep
  graphs-verify / verify-protocol / verify-skill-refs / graphs-verify-html
  exactly as they are.

TRACKING: progress.md `### R1 (COMPLETED)` row under the `## graph-runner`
heading R0 created, listing the crate, the checks, and the justfile change;
features.json commit row under phase "graph-runner": { id "gr-r1", title
"graph-runner: crate scaffold, typed graph model, check", status completed,
features ["runner-crate", "graph-model", "load-checks", "graphs-check",
"toolchain-pin"] }. test/test_features_phase.py must still pass.

VALIDATE (paste all of it):
  cargo run -q -p graph-runner -- check graphs               → 5 graphs OK   (C-01)
  cargo test -p graph-runner load_                            → 6 tests pass  (C-02)
  cargo test -p graph-runner role_enum_matches_schema         → pass          (C-03)
  cat runner/Cargo.toml                                       → deps = serde, serde_json, thiserror (C-04)
  rg -n 'process::Command|rhai|reqwest|SKILL\.md|std::net' runner/src → 0 (C-05)
  git diff --stat origin/main..HEAD -- graphs/*.json graphs/schema.json .agents lockfile.toml → empty (C-12)
  ./scripts/verify-graphs; ./scripts/verify-protocol;
  python3 -m unittest discover -s test;
  CROSSR_SKILLS_PATH=<v1-packets checkout> ./scripts/verify-skill-refs  → PASS/PASS/OK/PASS (C-13)
  rg -n 'no Rust crates' justfile                             → 0             (C-14)
  cargo fmt --all --check && cargo clippy --workspace --all-targets --all-features -- -D warnings -W clippy::pedantic && cargo test --workspace → exit 0 (C-15)
  test -f Cargo.lock && rg -n '^target/$' .gitignore          → both          (C-21)
  rg -n '^channel = "1.94.1"' rust-toolchain.toml && rg -n '^rust-version = "1.94"' runner/Cargo.toml && rg -n '^edition = "2021"' runner/Cargo.toml → three hits (C-25)
  Demonstrate one red: temporarily add `"extra": 1` to a copy of
  graphs/avril.json under /tmp and show `check /tmp/<dir>` exit 1 naming the
  key. Do not commit the copy.
Stack line in the PR body: after R0; R2 follows; no tag.
```

---

## Brief R2 — loops: stepper, `walk`, happy-path walks

```
You are implementing graph-runner R2 in sycamore-hq/crossr-loops.
Precondition: R1 merged; `cargo run -q -p graph-runner -- check graphs`
prints 5 graphs OK on origin/main.

[paste GUARDRAILS]

GOAL: pure stepping semantics (decision 3 / 4) and `graph-runner walk`.
No descent yet: a `role: graph` node is opaque in R2, so walks are committed
only for avril, code-gan, and brick (decision 5).

FILES (the whole list):
  runner/src/event.rs        Event enum: Next | Verdict(Verdict) | Label(Label);
                             Verdict enum: Bless | Reject; FromStr for the
                             walk-file line grammar ("next", "BLESS", "REJECT",
                             anything else = Label)
  runner/src/step.rs         pure: step(&Graph, &NodeId, &Event) -> Result<NodeId, StepError>
                             walk(&Graph, &[Event]) -> Result<Trace, WalkError>
  runner/src/trace.rs        Trace { steps: Vec<Step>, end: End }; Display renders
                             `<graph>: <from> --<event>--> <to>` one per line
  runner/src/walkfile.rs     parse a .walk file: one event per line, `#` comments,
                             blank lines ignored; the graph name is the file-stem
                             prefix before the first `.`
  runner/src/main.rs         add `walk <graph.json> <walk-file>`
  runner/tests/step.rs       tests named in C-08
  runner/tests/walks.rs      `committed_walks`: every graphs/walks/*.walk whose
                             graph has no `role: graph` node replays to a sink
  graphs/walks/avril.happy.walk
  graphs/walks/code-gan.happy.walk
  graphs/walks/brick.happy.walk
  progress.md, features.json one row each

SEMANTICS (decision 3 / 4 — implement exactly, test each line):
  - start = graph.start (the R0 key; never nodes[0])
  - sink = node with no out-edges
  - step: out-edges of `node` whose `when` matches the event — `Next`
    matches an unlabeled edge, `Verdict` matches "BLESS"/"REJECT" labels,
    `Label(l)` matches `when == l`. Exactly one match → Ok(to).
    None → StepError::NoEdge { node, event, accepted: Vec<String> } where
    accepted lists the node's labels ("next" for unlabeled).
    (Ambiguity is impossible after R1's load check; keep an unreachable
    variant out of the enum — do not model states the loader forbids.)
  - adversary node + event that is not a Verdict → StepError::NotAVerdict
    { node, event } even if a label would have matched (verify-protocol
    guarantees the labels are BLESS/REJECT, so this only fires on a
    hand-written bad walk — still test it against a fixture graph).
    Display: `<graph>: <node> is an adversary and accepts BLESS, REJECT;
    got <event>` — C-07 greps stderr for the node and that list.
  - walk consumes events in order from start. End::Complete when on a sink
    and the events are exhausted. WalkError::TrailingEvents { at, remaining }
    when a sink is reached with events left. WalkError::Incomplete { at }
    when events run out before a sink. Both carry the partial Trace.
  - Exit codes: 0 Complete; 1 any error (print the trace so far to stdout,
    the error to stderr); 2 usage.

WALK FILES (events only, so a human can read a walk as a story):
  avril.happy.walk:    next BLESS BLESS BLESS        (generator→po→qa→cto→stop;
                       check the real edges — do not trust this comment)
  code-gan.happy.walk: next pass BLESS BLESS         (generate→mechanical→tester
                       →reviewer→commit — verify against the file)
  brick.happy.walk:    next human next human green green zero-survivors human
  Each file starts with a `#` line naming the graph and the path it tells.

TRACKING: progress.md `### R2 (COMPLETED)`; features.json commit row
{ id "gr-r2", title "graph-runner: stepper, walk, happy-path walks",
status completed, features ["event-type", "step-walk", "trace",
"walk-files"] }.

VALIDATE (paste all of it):
  cargo run -q -p graph-runner -- walk graphs/avril.json graphs/walks/avril.happy.walk → exit 0, last line ends at `stop` (C-06)
  printf 'next\nfail\n' > /tmp/bad.walk && cargo run -q -p graph-runner -- walk graphs/avril.json /tmp/bad.walk; echo $? → 1, stderr names `po` and `BLESS, REJECT` (C-07)
  cargo test -p graph-runner step_                             → 6 tests pass (C-08)
  cargo test -p graph-runner committed_walks                   → pass (3 walks)
  rg -n 'process::Command|rhai|reqwest|SKILL\.md|std::net' runner/src → 0 (C-05)
  git diff --stat origin/main..HEAD -- graphs/*.json graphs/schema.json .agents lockfile.toml → empty (C-12)
  loop gates as in R1                                          → PASS/PASS/OK/PASS (C-13)
  Rust matrix as in R1                                         → exit 0 (C-15)
Stack line: after R1; R3 follows; no tag.
```

---

## Brief R3 — loops: descent, `cover`, full edge coverage, docs

```
You are implementing graph-runner R3 in sycamore-hq/crossr-loops.
Precondition: R2 merged; `cargo test -p graph-runner committed_walks`
passes on origin/main with three walks.

[paste GUARDRAILS]

GOAL: subgraph descent (decision 5), `graph-runner cover` (decision 6),
enough committed walks that every edge of every graph is taken, and the
three doc lines that say what the runner is (decision 10).

FILES (the whole list):
  runner/src/step.rs         descent: walk takes a `Resolve` (graph name →
                             &Graph) so it stays pure; a `role: graph` node
                             descends to the subgraph's `start`; the subgraph's
                             sink returns to the parent node; the next event
                             selects the parent's out-edge. Depth in each Step.
                             `flat: bool` keeps R2 behaviour.
  runner/src/trace.rs        render depth as two spaces per level; descent and
                             return lines: `<graph>: <node> >> <sub>` and
                             `<sub>: <sink> << <graph>:<node>`
  runner/src/cover.rs        pure: cover(&Graphs, &[(graph, events)]) ->
                             Coverage { taken: BTreeSet<(name, edge index)>,
                             uncovered: Vec<(name, from, when, to)> }
  runner/src/load.rs         load_dir returns Graphs (BTreeMap<name, Graph>)
                             usable as Resolve; a `uses.graph` naming a file
                             that is not in the dir → LoadError::MissingSubgraph
  runner/src/main.rs         `walk [--flat] …`, `cover <dir>`
  runner/tests/walks.rs      committed_walks now replays every walk with
                             descent on, and asserts cover(...).uncovered is empty
  runner/tests/descent.rs    flagship reaches its sink; a walk that stops inside
                             code-gan is Incomplete at `code-gan:commit` (the
                             innermost frame, depth 2); --flat treats
                             axel/code-gan as opaque
  graphs/walks/axel.happy.walk
  graphs/walks/flagship.happy.walk
  graphs/walks/*.reject.walk et al. — as many as it takes for `cover` to reach
                             zero: every BLESS/REJECT pair, mechanical fail,
                             plan-audit fail, plan-architect REJECT, ac-evidence
                             missing-evidence, generate unsatisfiable-claim with
                             both architect verdicts, AVRIL rejects at po/qa/cto,
                             brick gates. Name each file for the story it tells.
  scripts/verify-graphs      decision 6: when ROOT/runner/Cargo.toml exists,
                             run `cargo run -q -p graph-runner -- cover graphs`
                             (subprocess, cwd ROOT). cargo missing from PATH →
                             fail naming `cargo` and `rust-toolchain.toml`.
                             Non-zero exit or a count above zero → fail with the
                             runner's uncovered lines. Pure `parse_cover(stdout)
                             -> int | None` reads the `uncovered edges: <u>`
                             line; the subprocess call is the only action.
                             Add the cover line to the --html report checks.
  test/test_verify_graphs_cover.py
                             pure tests for parse_cover: count found, count
                             missing, non-zero count reported. No cargo call
                             in tests.
  graphs/GRAPH.md            replace "No Rhai. No OpenCode-native executor. No
                             interpreter in v0." with a `## Runner` section:
                             replays, never runs; start = the `start` key; sink
                             = no out-edges; `next`; BLESS/REJECT on
                             adversaries; descent; walks dir; `just
                             graphs-verify` (now includes cover), `just
                             graphs-check`, `just graphs-cover`; "SKILL.md wins
                             over the graph; the graph wins over the runner."
                             Keep the No Rhai sentence.
  book/src/pipeline/overview.md
                             one sentence after "Topology (not law): …": the
                             `graph-runner` in crossr-loops replays a walk
                             against that topology and never runs one. Nothing
                             else in book/.
  README.md                  Graphs (topology) paragraph: one sentence naming
                             the runner as a replayer; keep "No Rhai."
  AGENTS.md                  "Graphs (topology, not a runtime)" → "(topology;
                             `graph-runner` replays walks, it does not run them)"
  justfile                   graphs-cover: cargo run -q -p graph-runner -- cover graphs
  progress.md, features.json one row each; phase status → completed

COVER SEMANTICS: every walk under graphs/walks/ is replayed with descent on
against the graph its file-stem prefix names. An edge is taken when a step
traverses it, in whichever graph it lives — so a flagship walk covers avril,
axel and code-gan edges. Output: `taken <k>/<n> edges`, then one line per
uncovered edge `<graph>: <from> --<when>--> <to>`, then `uncovered edges:
<u>`; exit 0 iff u == 0. A walk that does not Complete is an error, not
partial coverage.

TRACKING: progress.md `### R3 (COMPLETED)` with the walk count and the
cover line pasted; features.json commit row { id "gr-r3", title
"graph-runner: descent, cover, full edge coverage, docs", status completed,
features ["descent", "cover", "walk-coverage", "verify-graphs-cover",
"graph-docs", "book-sentence"] }; phase "graph-runner" status → completed.

VALIDATE (paste all of it):
  cargo run -q -p graph-runner -- walk graphs/flagship.json graphs/walks/flagship.happy.walk → exit 0; depth-1 lines for avril / axel, depth-2 for code-gan (C-09)
  cargo run -q -p graph-runner -- cover graphs                 → uncovered edges: 0, exit 0 (C-10)
  cargo test -p graph-runner committed_walks                   → pass, and paste `ls graphs/walks | wc -l` (C-11)
  ./scripts/verify-graphs                                      → PASS and the line `uncovered edges: 0` (C-26)
  PATH=/usr/bin:/bin ./scripts/verify-graphs; echo $?          → 1, names cargo and rust-toolchain.toml (C-26)
  python3 -m unittest discover -s test -k cover                → parse_cover tests pass (C-27)
  sed -n '/Topology (not law)/,+2p' book/src/pipeline/overview.md → the one sentence (C-28)
  rg -in 'rhai' graphs/GRAPH.md README.md AGENTS.md runner/ | rg -v -i 'no rhai' → 0 lines (C-16)
  sed -n '/^## Runner/,/^## /p' graphs/GRAPH.md               → the five statements in C-17
  rg -n 'process::Command|rhai|reqwest|SKILL\.md|std::net' runner/src → 0 (C-05)
  git diff --stat origin/main..HEAD -- graphs/*.json graphs/schema.json .agents lockfile.toml → empty (C-12)
  loop gates as in R1                                          → PASS/PASS/OK/PASS (C-13)
  Rust matrix as in R1                                         → exit 0 (C-15)
  Demonstrate one red: delete one walk file in the working tree, run
  `cover`, paste the uncovered line it prints, restore the file.
Stack line: after R2; closes the loops side; R4 (work) follows; no tag.
```

---

## Brief R4 — work: ledger close

```
You are closing graph-runner in sycamore-hq/work.
Precondition: crossr-loops R1, R2, R3 are merged; you have their PR numbers
and rebase-merge SHA ranges from `git log --oneline origin/main` on loops.

Read AGENTS.md. work.json is the record; the HTML and the Project are views.

FILES: work.json, docs/board.html (generated), progress.md.

- work.json item `graph-runner`: status "done"; notes: "Done <date>.
  crossr-loops#<R1> / #<R2> / #<R3> rebase-merged as <sha>..<sha>.
  graph-runner replays graphs; no Rhai, no executor, no tag, no pin move.
  cover: uncovered edges 0 on <merge sha>." `updated` and `source_as_of`
  to today's date and the R3 merge.
- Regenerate: python3 scripts/work-board --html --out docs/board.html
  (`just status-html`). Never hand-edit the HTML.
- progress.md: one paragraph under `## board — work-00` in the shape the
  pr7 paragraph uses (PR links, SHA ranges).
- Do not run `just project-roadmap` — it needs org write; tell the human
  to run it so issue #14 closes.

VALIDATE (paste):
  python3 -m unittest discover -s test -v                     → OK (C-18)
  python3 scripts/work-board --markdown                       → graph-runner absent from Startable / Held / In flight; done count +1 (C-18)
  git diff --stat                                             → exactly the three files
```

---

## Review gauntlet (what I will check when each PR comes back)

- **R0**: five one-line graph diffs, nothing else in those files; `required` carries `start`; both red demos pasted; `index.html` regenerated, second run clean; the new test exercises `validate` with fixtures, not the live tree only.
- **R1**: `rust-toolchain.toml` and `rust-version` present and agreeing; `Role` enum test actually reads `schema.json` (not a hand-copied list); `deny_unknown_fields` on every struct; `LoadError` variants name graph + node/edge; no `unwrap` outside tests (`rg '\.unwrap\(' runner/src` → 0); both justfile fallbacks gone; `Cargo.lock` committed; `target/` ignored; the red demo pasted; deps exactly three.
- **R2**: `step` and `walk` take references and return typed errors — no I/O in `step.rs`; `NoEdge.accepted` lists `next` for an unlabeled edge; the adversary rule tested against a fixture, not only the live graphs; three walk files start with a `#` story line; exit codes 0/1/2 demonstrated; trace lines match the grammar in the brief.
- **R3**: `verify-graphs` really shells out (paste the run), fails loud without cargo (paste that too), and `parse_cover` has pure tests; the book sentence is one sentence; `cover` counts edges by `(graph, index)`, so two identical-looking edges in different graphs are distinct; the flagship walk really descends two levels (paste the trace); every uncovered-edge line names `from --when--> to`; the deleted-walk red demo pasted; GRAPH.md `## Runner` carries all five statements; `No Rhai` survives in GRAPH.md and README; phase status `completed`; `test_features_phase.py` green.
- **R4**: three files only; notes carry PR numbers and SHA ranges; board regenerated (stamp changes); the roadmap refresh handed to the human, not skipped silently.
- **Throughout**: `graphs/*.json` and `schema.json` byte-identical after R0; `.agents/`, `lockfile.toml` byte-identical always; harness remote untouched; no tag; pedantic clippy clean without blanket `#[allow]`; every VALIDATE line pasted, not summarized.

---

## Unresolved questions

Questions 1–7 were answered 2026-09-09 and folded into the decisions table
(serde approved; explicit `start`; toolchain pinned; book sentence;
`verify-graphs` shells out; ledger unparked; toolchain bumps follow the pin
rule). None open. A new question goes here, never into a brief.
