---
name: statechart
description: |
  Find every state machine in a codebase, explicit and implicit, and write two
  files for each one: a W3C SCXML chart and a self-contained interactive HTML
  explainer that renders the chart, lets the reader fire events, and explains
  every state, event, condition, and transition in ASD-STE100 Simplified
  Technical English. Use when the user asks to find, map, document, audit, or
  explain state machines, statecharts, lifecycles, status fields, workflows,
  or flag clusters; says "SCXML", "what states can X be in", "draw the
  lifecycle of Y"; or wants a newcomer to understand a stateful part of the
  system. Not for one inline diagram (show-me). Not for a general explainer
  page about something that is not a state machine (html-explainer). Does
  not change application code.
metadata:
  author: scull7
  short-description: SCXML chart + interactive STE explainer per state machine
---

# Statechart explainer

Each state machine in the code gets a chart a tool can read and a page a
stranger can read. The chart is SCXML. The page is one HTML file that draws
the chart, runs it, and says what each part means in ASD-STE100.

## Harness Context (Stratified Disclosure)

This skill is portable. The invoking harness supplies:

- The output directory. Default when none is given: `docs/state-machines/`
  at the repository root.
- The preview and screenshot tool for the look step.
- The base URL for source links (`repo.url`, `repo.rev`), when one exists.

The template uses the CrossR house palette. Do not edit the template per
machine; another harness ships its own copy of the template.

## Install

The skill is this directory. Copy all of it, not only `SKILL.md`: the
scripts and the template live next to it. From a `crossr-skills` checkout:

| Agent | Command | Use |
| --- | --- | --- |
| Claude Code | `./scripts/sync-claude-skills statechart` | `/statechart` |
| Codex | `./scripts/sync-claude-skills --target ~/.codex/skills statechart` | `$statechart`, or ask for state machines |
| Other agentskills.io agents | Copy `.agents/skills/statechart/` into the agent's skills directory | By name |

Needs Python 3.9+ for the scripts and a browser for the look step.

Optional, recommended: make a local copy of the ASD-STE100 wordlist and set
`STE_DICTIONARY` to its path. The checker then checks each word.

```bash
python3 scripts/extract_ste_dictionary.py ASD-STE100.pdf ~/.config/crossr/ste100.tsv
export STE_DICTIONARY=~/.config/crossr/ste100.tsv
```

The standard is free from https://www.asd-ste100.org, but ASD owns the
copyright. Never commit or share the wordlist. See
[references/ste.md](references/ste.md).

## Inputs and outputs

Input: a repository, or a path inside it. Optional: one named machine.

Output, in the output directory:

| File | Contents |
| --- | --- |
| `<machine-id>.scxml` | The chart. W3C SCXML 1.0 under the profile in [references/scxml-profile.md](references/scxml-profile.md). |
| `<machine-id>.json` | The prose, in STE, under [references/explainer-data.md](references/explainer-data.md). |
| `<machine-id>.html` | [assets/explainer-template.html](assets/explainer-template.html) with two data blocks filled: the same SCXML and the prose JSON. |
| `README.md` | Inventory: one row per machine with id, kind, confidence, and source files. Candidates you rejected, with the reason. |

`<machine-id>` is kebab-case and stable across runs. A rerun overwrites the
files for machines it finds and reports machines that disappeared. It does
not delete them.

## Workflow

1. **Survey.** Read the repo guidance files, the build manifests, and the
   directory layout. Name the domain in one sentence. You need it for the
   glossary.
2. **Discover.** Sweep for explicit and implicit machines with the signals
   in [references/discovery.md](references/discovery.md). Record every
   candidate with file and line evidence. For a large repo, split the sweep
   by top-level directory and run the parts in parallel.
3. **Decide.** Keep a candidate when it has two or more states, one or more
   transitions, and behavior that depends on the current state. Merge
   candidates that are one lifecycle seen from different layers (database
   enum, API field, UI). Record each rejection with its reason.
4. **Model.** For each kept machine, extract states, events, conditions,
   transitions, and entry and exit actions from the code. Follow
   [references/discovery.md](references/discovery.md#extract-the-model).
   Every state and transition gets a `crossr:source`. Do not invent a
   transition the code does not make. When the code allows something the
   domain seems to forbid, model what the code does and write a note.
5. **Write the SCXML** under [references/scxml-profile.md](references/scxml-profile.md).
6. **Write the prose JSON** under
   [references/explainer-data.md](references/explainer-data.md). Write it in
   STE under [references/ste.md](references/ste.md). Write for a reader who
   does not know this project or this domain. Define each domain word in the
   glossary before you use it.
7. **Build the page.** Run
   `python3 scripts/build_page.py <id>.scxml <id>.json <id>.html`. It puts
   the SCXML and the JSON in the template's two data blocks and changes
   nothing else. Keep `<id>.json` next to the page so a rerun can rebuild it.
8. **Check.** Run `python3 scripts/check_statechart.py <id>.scxml <id>.html`.
   Paths to `scripts/` are relative to this file. The checker uses the
   STE dictionary when `STE_DICTIONARY` is set, and says so. Fix every error. Fix
   each warning, or write in the inventory why it stays.
9. **Look.** Open the page at about 1280 px and about 390 px wide. Play each
   scenario to the end. The page shows a red self-check banner when a
   scenario step does nothing or data is missing. Fix the cause. When edges
   cross or labels collide, add `layout` hints (see
   [references/explainer-data.md](references/explainer-data.md#layout))
   and look again.
10. **Report.** Give the user the output directory, the inventory table, and
    the defects you found in the code (unreachable states, dead ends,
    transitions from any state, layers that disagree).

## Rules

- One machine, one chart, one page. Do not put two machines in one chart
  because they interact. Name the other machine in a note and link its page.
- The SCXML is the truth. The page renders the embedded SCXML. The prose
  explains it. The prose never adds a state or transition the chart lacks.
- Implicit machines say so. Set `kind` to `implicit`, set `confidence`, and
  list the evidence that makes the code a machine.
- Every prose string obeys [references/ste.md](references/ste.md). Code
  identifiers go in backticks and count as one word.
- The page loads nothing from the network. No CDN, no fonts, no images by
  URL. Links to the source code are allowed.
- This skill reads code and writes documents. It does not fix the defects
  it finds, and it does not open a pull request.

## Failure modes

| Situation | Action |
| --- | --- |
| No machines found | Write the inventory with the rejected candidates and stop. Tell the user. |
| State set depends on runtime data (states loaded from a database table) | Model the states the code and seed data name. Add a note that the set is open. Set `confidence` to `low`. |
| Guard too complex to name | Name it after the function that computes it. Explain it in `conditions`. |
| Machine too large to read (more than about 40 states) | Split along compound states into child machines. Each child gets a page. The parent page links them. |
| Checker cannot run (no Python 3.9+) | Say so. Do the checks in the references by hand. Do not claim a pass. |

## Verification

In a fresh activation these behaviors are directly observable:

- Each kept machine has a `.scxml` file that passes
  `check_statechart.py` with no errors, and a `.html` file built from the
  unmodified template.
- The SCXML in the page equals the `.scxml` file.
- Every state, event, condition, and transition has a meaning in the JSON,
  and every state and transition has a `crossr:source` file and line.
- Implicit machines carry `kind: implicit`, a confidence, and evidence.
- All prose passes the STE lint in the checker, and the glossary defines
  each domain term the prose uses.
- The agent looked at the page at both widths and played every scenario
  before it reported the path.

## One-Sentence Mandate

> "Find each machine, chart it in SCXML, and explain it in STE so a stranger can run it."
