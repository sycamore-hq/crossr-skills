---
name: html-explainer
description: |
  Write a single self-contained HTML page that explains an idea, plan, PR,
  system, or research result with diagrams and playable flows. Use when the
  user asks for an HTML explainer, HTML artifact, explainer page, interactive
  doc, plan-as-HTML, PR writeup page, concept explainer, or Thariq-style HTML
  documentation. Also use when markdown would bury a flow, architecture,
  sequence, or comparison that should be seen. Not for compact in-thread
  visuals (show-me). Not for posting review threads or issuing a BLESS/REJECT.
---

# HTML explainer

A page someone will actually read. One file. No build. Open it in a browser.

Source of the practice: Thariq (@trq212), "The unreasonable effectiveness of
HTML" — https://x.com/trq212/status/2052809885763747935 and the example set at
https://thariqs.github.io/html-effectiveness/. Steal the jobs, not the chrome.

## Harness Context (Stratified Disclosure)

Save path, palette, preview command, and screenshot tool are supplied by the
invoking harness. The house palette below is the CrossR disclosure example.
Other harnesses substitute their own. Place the file next to the work or under
the harness plan directory. Open it with whatever preview the environment
provides. Screenshot with whatever capture the environment provides.

House palette when the artifact is for Sycamore / CrossR:

- Well pitch `#171412`
- Plaster page `#F3EEE6`
- Packed mile `#C4A882`
- Split fig `#9E4E36`
- Dust leaf `#6A7348`
- Canopy shade `#2E342C`

## When this is the output

Default to HTML instead of a long markdown file when the reader needs to see
structure, compare options, walk a flow, or hand the page to someone else.
Keep markdown for git-reviewed law, commit notes, and anything whose diff has
to stay readable.

`show-me` is the smaller sibling: a tree, a Mermaid block, a shape-diff, or one
focused figure next to short prose. This skill is the page.

## Shape

- One `.html` file. Inline CSS and JS. No bundler, no framework.
- System fonts unless the page is a design artifact that needs a face.
- CDN only if a library is load-bearing (charts, a map). Prefer none.
- The page answers one question. Title is that question or the thing named.

Do not dump the source markdown into styled `<article>` tags and call it an
explainer.

## Visual spine (required)

Every explainer has at least one of these, usually two:

1. A diagram for the idea. Architecture, sequence, flowchart, comparison
   matrix, state machine, before/after. Draw it. ASCII in a `<pre>` is a
   failure of the format.
2. A playable flow when the page describes a process. Step through it.
   Play / pause / reset. Highlight the active node. Show what moves at each
   tick. A static numbered list is the fallback only when the flow is one
   sentence.

How to draw and animate: [references/diagrams.md](references/diagrams.md).

## Write it

1. Read the source (code, plan, PR, paper). Name the one question.
2. Pick the spine first. Boxes and arrows on paper if you have to. Then HTML.
3. Surround the spine with the minimum prose: lede, the facts that make the
   diagram legible, gotchas, links back to code. Cut the rest.
4. Code samples: a few annotated snippets, not the file. Highlight the line
   that matters.
5. Comparisons: a real grid or table, one option per cell, tradeoff labeled
   on the cell.

Taste: dark or light is fine; pick one and stay there. High contrast.
Tabular numbers. Sticky toc only if the page is long. No hero gradients, no
card shadows stacking three deep, no stock illustration.

## Look at it before you share

Do not hand the file over on generate.

1. Open the page with the harness preview.
2. Screenshot desktop (~1280) and mobile (~390).
3. Inspect the shots. The usual faults are overflowing labels and crossed
   lines. Also: text colliding with nodes, clipped buttons, horizontal
   scroll, contrast failure, animation that cannot be reset, click targets
   under 32px.
4. Fix the file. Screenshot again. Stop when the shots are clean.
5. Then tell the user the path.

Checklist: [references/qa.md](references/qa.md).

If the environment has no screenshot tool, say so and inspect the live page
at both widths before sharing. Do not skip the look.

## Jobs this format is good at

- Concept or feature explainer (diagram + playable flow + short gotchas).
- Implementation plan (timeline, data-flow, a couple of mockups, risk table).
- PR writeup (annotated diff, severity color, jump links).
- Side-by-side options (several approaches, one grid, tradeoff on each).
- Status or incident (timeline you can scrub, not a wall of bullets).
- Throwaway editor with a copy-out button (JSON, markdown, prompt). Only when
  the user needs to push data back into chat.

A product UI on a route is a prototype, not this skill. A slide deck as a
`.pptx` is out of scope.

This skill presents a page. It does not review, bless, reject, or open a PR.

## Verification

In a fresh activation the following six behaviors are directly observable
and scorable:

- The agent writes one self-contained `.html` file (inline CSS/JS, no
  bundler) instead of restyling the source markdown as an `<article>`.
- The page contains a diagram for the idea. ASCII-in-`<pre>` does not count.
- When the page describes a process, the flow is playable: Play / Pause /
  Step / Reset, active node marked, caption per tick.
- The agent looks at the running page at ~1280 and ~390 (screenshot when the
  harness has a capture tool) and fixes overflowing labels and crossed lines
  before sharing the path.
- The agent does not substitute a `show-me` compact form when the user asked
  for an explainer page, and does not post a review thread, issue a
  BLESS/REJECT, or open a PR.
- Save path, palette, and preview come from Harness Context. The agent does
  not invent a house directory or a house open command.

Violations against any of these six observable criteria during fresh
activation indicate the skill was not followed and must be corrected before
the work can be considered complete.

## Specialization

This skill is the long-form HTML-documentation specialization of the writing
layer (precondition: a topic that needs to be seen, not only read). It
supplies the single-file contract, the diagram-and-playable-flow spine, and
the screenshot-before-share gate (postcondition: a page the reader can open,
play, and hand to someone else). Compact visuals stay on `show-me`. Gates
stay on `github-pr-review`, `architecture`, and `gan-verdict`.

## One-Sentence Mandate (Memorize This)

> "Draw the idea, play the flow, look at a screenshot before you share."
