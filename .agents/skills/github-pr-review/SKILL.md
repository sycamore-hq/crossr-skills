---
name: github-pr-review
description: "Reviews a GitHub pull request and posts the findings as structured inline review comments (severity-tagged, one issue per thread, with a checkable 'Done when') submitted as a single review with the right event. Use whenever the user wants review feedback on a PR — 'review this PR', 'take a look at #42', 'thoughts on this diff', 'is this safe to merge', 'code review', 'second pass on my PR', `/review-pr` — including when all they give is a PR reference (URL, owner/repo#N, 'pr 58', '#91'). Also covers re-reviews after new pushes, checking whether previously flagged threads were actually fixed, and cases where the user wants verification (build/tests/tracing callers) before comments are posted, or wants the findings in chat without posting. Works through GitHub MCP tools or the gh CLI. Not for applying review feedback to code (use github-pr-fix), summarizing a diff, or opening a PR."
metadata:
  author: scull7
  short-description: Review a PR with structured, verifiable inline comments
---

# PR Review

Read a pull request, verify what you can, and post the defects you are sure of
as inline review threads that an implementing agent (or a human) can act on and
resolve one at a time without talking to you.

The comments you write are work items, not commentary. Downstream, `github-pr-fix`
(or a person) will take each thread, make the change, check `Done when` against
the new HEAD, and resolve it. Every rule below exists to make that possible: a
comment that is not anchored to a line can't be resolved; a comment that bundles
two issues can't be half-resolved; a comment without a checkable condition can't
be verified; a comment that turns out to be wrong costs the author an hour and
your credibility on the next twenty.

The job is done when the review is submitted on GitHub with the correct event,
every finding is an inline thread, and the chat has a short report. A review
that exists only in chat did not happen — unless the user asked for exactly
that ("don't post", "just tell me", "is this safe to merge?"). Then do every
step except the post: the validated draft file is the deliverable, and the
chat report says which event it *would* have carried and where the file is, so
the user can post it later with one command.

## Model

No `--model-*` flag → ask which model should run this review and stop until
the user answers. Do not choose a model and do not start the review.

The id on a flag is a raw session slug. It must be this session's model. If
it is not, stop and say so. Do not substitute another model. An answer in
chat is the model for this run; the same rule applies.

## Workflow

1. Parse `owner`, `repo`, and the number from the URL or `owner/repo#n`.
2. Gather context — tool and command shapes are in
   [references/github.md](references/github.md):
   - PR body, base/head refs, `headRefOid`, linked issues, CI status.
   - The diff `base...head` and the changed files at HEAD. Diff against the
     PR's recorded base commit, not whatever `main` you have locally; a stale
     local base makes untouched files look changed and the anchor check
     meaningless.
   - Every existing review thread, paginated to the end. A plan built on the
     first page silently duplicates the second.
   - Your own previous reviews on this PR, if any. Their presence switches you
     into [re-review mode](#re-review).
   - Repo guidance: `AGENT.md` / `AGENTS.md` / `CLAUDE.md`, `CONTEXT.md`,
     `CONTRIBUTING.md`, `docs/adr/`. An accepted ADR settles the questions it
     covers; do not reopen them in a review.
3. Get the head on disk when you can: `gh pr checkout <n>`, or without `gh`,
   fetch the head ref and `git worktree add` it somewhere scratch (details in
   the reference). Reading a diff tells you what changed; the tree tells you
   what it broke. Don't switch branches in a checkout you share with anything
   else.
4. Review the changed lines and the lines they directly affect — callers of a
   changed signature, readers of a changed field, the match arms a new variant
   must reach. Not the rest of the repo. Work through the [scope order](#scope-in-this-order).
5. [Verify](#verify-before-you-post) each candidate finding.
6. Draft every comment into a local file first (the JSON shape in
   `references/github.md`) and run `scripts/validate_review.py` against the
   diff. It checks:
   - First line matches `<severity> [<slug>] <problem>` (slug optional).
   - `path` is in the diff and `line` is on the RIGHT side of a hunk. GitHub
     rejects comments on lines the diff doesn't touch, and a 422 on one
     comment fails the whole review.
   - Count ≤ 15; if over, drop nits first, then merge siblings into a cluster.
   - The event matches the severities present.
7. **Re-fetch the thread inventory right before posting** and drop any comment
   that now duplicates an open thread on the same lines for the same issue.
   Minutes pass between inventory and submit; another reviewer (or another
   session on your own account) can land in that window, and a duplicate
   thread is the one thing the fixer cannot resolve cleanly.
8. Post it as **one review** — pending review, all comments attached, submitted
   with the event chosen by the [severity](#severity) present. Fifteen separate
   single-comment reviews send fifteen notifications and make the event
   meaningless.
9. If you used clusters and the tooling lets you edit a posted comment,
   backfill the anchor with permalinks to its children. If it doesn't, the
   `path:line` list stands.
10. [Report](#report) in chat.

## Verify before you post

The line between "I'm sure" and "I'm guessing" is whether you looked. Before a
finding becomes a comment:

- **Claims about behavior** ("this panics on empty input", "this races"): read
  the callee, trace the inputs, and when a tree is checked out, run the narrowest
  thing that would show it — a single test, a `cargo check`, the script against
  a scratch directory. Cite the reproduction in the comment rather than
  asserting the conclusion.
- **Run the whole story you are about to tell.** If the comment says "and it
  never recovers", run the recovery step too. A finding that reproduces the
  first half and extrapolates the second is the most convincing kind of wrong:
  it comes with evidence. Start each reproduction from a fresh scratch state;
  a target left over from the previous one silently changes which branch of
  the code runs.
- **Claims about callers** ("nothing handles the new variant", "this breaks
  `foo`'s contract"): grep for them. Name the file you found in the comment.
- **Claims about tests** ("untested"): look for the test, including in files the
  diff doesn't touch. Absence in the diff is not absence in the repo.
- **Claims about conventions** ("we don't do it this way here"): find the
  convention in repo docs or in two other places in the code. Otherwise it is
  your preference, which is at most a nit.

Verification is not only for shooting down candidates; it is how you find the
defects worth posting. The PR body's list of what was tested is the author's
mental model, and the bugs live in the states it doesn't mention: the
pre-existing directory, the symlink, the copy that fails halfway, the second run
in the same second, the empty input, the caller that passes `None`. When a PR
says "exercised against a scratch target", re-run that and then take one step
past it.

Some reproductions lie in a sandbox. Running as root makes every permission
check pass; a mocked clock makes every timeout succeed. When the failure you
are provoking depends on the environment, provoke it another way (an
unprivileged user, a `PATH` shim that fails the command, an injected input) and
say in the comment which way you used.

If a tree isn't available (no clone, no toolchain), reduce confidence rather
than skip verification: a finding you could not check is posted as `q`, phrased
as the question you would have answered by running it, or not posted at all.
Never post a `blocker` you did not verify.

Run what the repo actually uses when you run checks: named commands in
`AGENT.md` / `CONTRIBUTING.md`, a `Makefile` or `justfile` target, the CI
workflow, then the ecosystem default. A check that is already red on the base
branch is context, not a finding against this PR.

## Comment shape

Every finding is an inline comment on a specific line or range. Nothing goes in
the conversation tab except the one-line review summary.

```
<blocker|should-fix|nit|q> [<cluster-slug>] <one-line problem>

Issue: <what is wrong, one or two sentences, with the evidence you found>
Why it matters: <bug | security | compat | perf | maintainability — and the consequence>
Suggested fix: <concrete change; a GitHub suggestion block when the edit is local>
Done when: <observable condition the next reader can check on HEAD>
```

The first line is parsed by machines; keep the grammar exact — one space
between the parts. The `[slug]` is present only for cluster members. A `q` may
say `Suggested fix: none until answered`. Shapes and worked examples are in
[references/examples.md](references/examples.md).

Each comment is atomic: one issue, one fix, one condition. If you find yourself
writing "also" or "and while you're here", that is a second comment. A thread
that bundles two issues gets resolved when the first is fixed and the second is
quietly lost.

`Done when` is the acceptance test the fixer will run. "Handles errors properly"
is not checkable. "`parse_port` returns `Err(ParseError::Range)` for 70000, with
a test asserting it" is. Write the condition you would check yourself.

Use a suggestion block when the fix is a local edit of the lines you are
anchored to. Suggestions are one-click to apply and unambiguous; prose fixes
are neither. Do not use a suggestion block for a change that touches lines
outside the anchor — GitHub will apply exactly what you wrote, to exactly those
lines.

Wrap literal angle brackets and placeholders in backticks. Markdown renders
`<name>` as an HTML tag and shows nothing, and some tool paths strip them on
read-back; a `Done when` that lost its placeholder is not checkable.

### When the real line is not in the diff

Some findings live on a line the PR does not touch: a doc the change made
stale, a caller two functions down, a range in the same file outside any hunk.
GitHub will not anchor a comment there. Anchor on the changed line that causes
the problem — the header that now contradicts the doc, the signature the
caller breaks on — and put the real location (`path:line`) in the Issue line so
the fixer knows where to go. In the chat report, write the anchor followed by
the real location in parentheses: `scripts/sync:7 (real: AGENTS.md:56)`. Do not drop the finding because the anchor is
imperfect, and do not move it to the conversation tab where nothing can resolve
it.

## Severity

- **blocker** — wrong, unsafe, breaks a contract, or contradicts an accepted
  ADR. Must be fixed before merge. You verified it.
- **should-fix** — a real defect or design miss. The fixer applies it unless
  they have a better argument, in which case they reply and leave it open.
- **nit** — optional, including "fine now, risky later". The fixer skips nits
  unless asked. Never block on one, and never let nits crowd out the findings
  that matter: if the review is mostly nits, the reader assumes nothing is
  seriously wrong, so make sure that is true.
- **q** — a question. No code changes until a human answers. Use this for
  things you could not verify, and for genuine design questions. It is not a
  softer way to say should-fix; if you know the answer, say it.

The review event follows from the severities present:

| Findings | Event |
|---|---|
| any `blocker` | `REQUEST_CHANGES` |
| only `should-fix` / `nit` / `q` | `COMMENT` |
| none | `APPROVE`, with a one-sentence body |

Zero findings is a real outcome. Say what you checked in the sentence, submit
APPROVE, and do not invent nits to look thorough. One exception GitHub
enforces: the PR's author cannot approve their own PR. Reviewing as the author
(a self-review, a second pass on your own branch), a zero-finding review is a
`COMMENT` with that same one sentence.

## Clusters

Some findings are one structural change spread across several files: an error
type that should be introduced and then used in four places, an authorization
check that belongs in a layer rather than in each handler. Posting four
independent comments loses the structure; posting one essay loses the
line anchors. Use a cluster:

- Pick a short slug: `parse-errors`, `authz-layer`.
- Post one **anchor** on the most relevant entry point — the type, the module,
  the function the change starts from. The anchor carries the design: the full
  Issue / Why / Suggested fix / Done when for the structural change, and a list
  of children as `path:line` (permalinks after the backfill pass).
- Post a **child** on each specific line with the same `[slug]`. A child states
  only its local edit and points at the anchor. Do not paste the design into
  every child.
- The anchor's `Done when` is the cluster's. Children's conditions are local.

The fixer reads the anchor, makes the structural change, then the children, and
resolves the anchor last. Write the cluster so that reading order works.

## Re-review

If you have already reviewed this PR, the job changes: the author has pushed,
and the question is what changed since you last looked and whether the threads
you opened were actually addressed.

1. Find the `commit_id` of your last submitted review. Diff from that commit to
   HEAD, not from base — the base diff is what you already reviewed.
2. For each thread you opened, check its `Done when` on HEAD:
   - **Resolved, and `Done when` holds** — leave it alone.
   - **Resolved, but `Done when` does not hold** — reply on the thread stating
     what is still missing, and unresolve it. Do not open a new thread for the
     same issue; the history belongs together. If checking it also showed your
     original claim was overstated, say so in the same reply and give the
     corrected severity.
   - **Open, with a reply arguing against the change** — read the argument. If
     it convinces you, reply that you agree and resolve it. If not, reply once
     with the specific point it misses, keep it open, and let a human close the
     disagreement.
   - **Open, with a `q` that got an answer** — if the answer settles it, resolve.
     If the answer reveals a defect, reply with the finding at its real severity
     (the thread keeps the history) rather than opening a new one.
   - **Open, untouched, no reply** — not addressed. Leave it; a second comment
     saying "still open" adds a notification and no information.
   - **Outdated** (the line moved) — locate the code at its new position and
     judge it there. Outdated is not the same as fixed. If it is now fixed,
     reply with the commit that fixed it and resolve.
3. Review the new diff for new defects only — including the ones the fix
   itself introduced, which is where they usually are. Do not re-flag things
   you chose not to flag last time; the author is entitled to a stable bar.
4. Do the per-thread replies and (un)resolves **first**, then create the
   pending review for the new findings. On the MCP path a reply is itself a
   tiny review, and it collides with a pending one.
5. Submit a new review. The event is decided by what is *still* open at
   `blocker` severity, not by what you found the first time: if everything you
   blocked on is fixed and the new diff is clean, that is an APPROVE (or a
   COMMENT if you are the author). Open `should-fix` threads with no new
   findings are a COMMENT. If the new push only partially addressed a blocker,
   that is still REQUEST_CHANGES, and the body says which thread.

Threads opened by other reviewers are context. Do not resolve them, do not
re-post their findings under your severity grammar, and do not pile a second
comment onto their thread unless you have evidence they lack.

If HEAD is the commit your last review was on, there is no incremental diff.
A pass is still worth doing when the user asks for one: re-check each open
thread's `Done when` (pushes are not the only way things change — replies,
resolves, and your own earlier mistakes are), and post only what is genuinely
new. Nothing new is a valid answer; say so in the report and post nothing.

If the pass you are about to post is already on GitHub — a sibling session on
the same account got there first with the same verdicts — verify its work as
you would your own and stop. Two identical reviews are noise; a review that
disagrees with the earlier one on a specific thread is a reply on that thread.

## Scope, in this order

1. Correctness and bugs — logic, edge cases, races, resource leaks.
2. Security — validation, injection, authz, secrets, unsafe blocks.
3. API and contract changes, backward compatibility, migrations.
4. Error handling and observability — swallowed errors, lost context, missing
   logs at the boundary where someone will debug this at 3am.
5. Performance, only where it plausibly matters — a hot path, an O(n²) over
   user-controlled input, an unbounded allocation. Not micro-optimizations.
6. Readability and maintainability, at should-fix only when the cost is
   concrete (a lifetime nobody can reason about, a 400-line function that was
   200 before this PR).
7. Test coverage for the changed behavior — the tests that would have caught
   the defects you found in 1–4, and tests for the edge cases the PR's own
   description claims to handle.

Spend your comment budget top-down. A review with three nits and no mention of
the race in step 1 is worse than no review, because it signals the code was
looked at.

## Do not

- Restate the diff, summarize the PR, or post praise-only comments. Every
  thread is something someone has to act on.
- Comment on what tools already own: formatter output, clippy/linter findings,
  lockfiles, generated files, import order. If CI enforces it, CI will say so.
- Re-litigate an accepted ADR or a decision the PR body says is settled. If
  the PR contradicts an ADR, that is a blocker citing the ADR — not a debate.
- Post a finding you did not verify as anything above `q`.
- Duplicate an open thread on the same lines for the same issue, including
  another reviewer's.
- Post more than one review for one pass, or put findings in the conversation
  tab where nothing can resolve them.
- Leave a pending review unsubmitted. If posting fails partway, delete the
  pending review and re-post the batch; a half-posted review with no event is
  the worst state to leave behind. But only delete a pending review you
  created in this session — one you did not create belongs to a live sibling
  session, and deleting it destroys their batch.
- Push commits to the PR. Reviewing is not fixing; if the user wants the
  changes applied, that is `github-pr-fix`.

## If you posted something wrong

A submitted review cannot be edited into a different event and its comments
cannot be unposted. If one of your own threads turns out to be a duplicate or
mistaken, reply on it saying so (one line, pointing at the thread that stands
or the evidence that overturned it) and resolve it. The reply costs the reader
five seconds; a silently resolved thread costs them the question of why.

## Report

A short table in chat, nothing else — except a `show-me` visual when the
PR's shape is the point. Do not restate the GitHub diff. The review lives
on GitHub; the chat gets the index.

```
Review: <REQUEST_CHANGES|COMMENT|APPROVE> — <PR url>

| # | Severity | Cluster | Path:line | Problem |
|---|---|---|---|---|
```

Under the table, at most two short lines: one for what you ran (checks,
reproductions, the commit you ran them on) and one for anything a human needs
to decide — a check you could not run, a `q` that gates a finding, a thread
from a prior review you unresolved. When the user asked a question ("is this
safe to merge?"), the second line is the answer, stated as yes or no and tied
to whether a blocker exists. On a re-review, add a `Prior threads`
table with the same columns plus `Status` and `Action`. On a zero-finding
review, the findings table is replaced by the one sentence you put in the
review body. When the user asked for no post, the first line says `(drafted,
not posted)` and where the draft file is.
