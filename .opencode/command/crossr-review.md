---
description: CrossR Review conductor — Review Agent then Fix Agent until the PR is clean, then stamp APPROVE
agent: crossr-review
---

## Project preflight (read-only)

Optional tools: `git`. Anything missing degrades to a placeholder line — the
command still runs. Nothing below mutates the repo or the PR.

Branch, origin, and recent commits:
!`git status -sb 2>/dev/null && git remote get-url origin 2>/dev/null && git log --oneline -8 2>/dev/null || echo "(no git repository)"`

Treat the dump above as the current state of the checkout. Do not re-run these
commands just to confirm them.

Load the `crossr-review` skill with the skill tool. Recite the conductor
persona's One-Sentence Mandate, then handle this request:

$ARGUMENTS

**If the request above is empty, ask for a PR and stop.** Do not invent a PR.
Do not start the loop.

Hard rules: conductor never reviews the diff and never edits the PR branch;
only-`q` stops with no Fix and no stamp; dirty or max-rounds → no stamp;
clean → APPROVE or a conversation comment containing `APPROVED`.
