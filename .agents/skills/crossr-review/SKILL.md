---
name: crossr-review
description: >
  Conducts a Review Agent then Fix Agent loop on a GitHub pull request until
  the review returns zero issues and zero questions, then stamps APPROVE or
  comments APPROVED. Use only when the user invokes /crossr-review.
disable-model-invocation: true
metadata:
  author: scull7
  short-description: Loop github-pr-review and github-pr-fix until a clean PR
---

# CrossR Review Loop

You are the conductor. You never review the diff and you never edit the PR
branch. You only resolve inputs, launch the two sub-agents, and stamp a clean
result.

## Code Review  Loop

You will review the pull request using the "Review Agent" for the code review, then the "Fix Agent" to fix all issues found during the review.  You will loop this process until the review returns with zero issues and questions found.

### Sub-Agents

  Name: Review Agent
  Skill: /github-pr-review
  Model: ask, unless `--model-review` is set
  ---
  Name: Fix Agent:
  Skill: /github-pr-fix
  Model: ask, unless `--model-fix` is set

Launch Fix Agent with "the user asked for nits". `q` threads are not fixes.

## Flags

Parse from the invocation. Unknown flags: stop and ask.

| Flag | Default | Meaning |
|---|---|---|
| `--model-review <id>` | ask | Review Agent model |
| `--model-fix <id>` | ask | Fix Agent model |
| `--max-rounds <n>` | `8` | Review→Fix cycles before a dirty stop |

A bare PR reference (URL, `owner/repo#N`, `pr 58`, `#91`) is the target, not a flag.

### Models

`--model-review` and `--model-fix` are harness parameters. Neither has a
default model. No flag → ask the user which model runs that agent, then
wait. Ask once per agent, before its first launch, and reuse the answer
on later rounds. Do not pick a model, and do not use the session default.

A provided id is a raw session slug. There is no short-id map.

If the slug is not in this session's list, stop and ask. Do not substitute
another model.

Pass the chosen slug on the sub-agent launch as `--model-review <id>` or
`--model-fix <id>`.

## Resolve the PR

Collect candidates from the invocation and this conversation: GitHub PR URL,
`owner/repo#N`, `pr <n>`, `#<n>`.

- One distinct PR → use it.
- Several distinct PRs → ask which.
- `#<n>` only → take `owner/repo` from `origin`.
- None → request a PR and stop.

## Sibling skills

`github-pr-review` and `github-pr-fix` must be readable before the first
Review Agent launch.

**Found** if the name is in this session's skill list, or a `SKILL.md` exists
under `.agents/skills/`, `.cursor/skills/`, `~/.cursor/skills/`, or
`~/.agents/skills/`.

**Missing:** ask once to load the missing trees from
`https://github.com/sycamore-hq/crossr-skills` (paths
`.agents/skills/github-pr-review/` and `.agents/skills/github-pr-fix/`).
Do not fetch without approval.

On approval, copy each missing tree to `~/.cursor/skills/<name>/`. Copy into
`.agents/skills/<name>/` only when the user wants them committed here. Then
read each `SKILL.md` and pass that path to the sub-agent. Do not wait for
a session restart.

On refusal, stop.

## Loop

```
round = 1
while true:
  run Review Agent on the PR
  if clean → stamp, report, stop
  if only `q` remain → report questions, no Fix, no stamp, stop
  if round > max_rounds → report dirty, no Fix, no stamp, stop
  run Fix Agent on the PR; the user asked for nits
  round += 1
```

**Clean** means the Review Agent report has no `blocker`, `should-fix`,
`nit`, or `q` rows (empty findings table, or an `APPROVE` / zero-finding
`COMMENT`). Open questions keep it dirty even when every issue is gone.

**Review Agent** reads `github-pr-review` and the PR. It posts the review.
It does not push.

**Fix Agent** reads `github-pr-fix` (the user asked for nits) and the PR. It
implements, pushes to the PR head, replies, and resolves only threads whose
`Done when` holds. It does not open a new review.

Launch each as a sub-agent. Wait for its report table before the next step.
The conductor does not substitute for a missing report.

## Stamp

After a clean review, the PR must show an approval or the word `APPROVED`:

1. If the last Review Agent event is `APPROVE`, that is the stamp.
2. Else submit an approving review on the PR.
3. If GitHub refuses (author cannot approve their own PR), post a
   conversation-tab comment whose body contains the word `APPROVED`.

Verify one of those exists before claiming done. Do not stamp on a dirty
stop or a questions-only stop.

## Report

One table, then at most two lines.

```
Loop: <clean|questions|dirty> — <PR url> — rounds <n>/<max>

| Round | Review event | Issues | Questions | Fix |
|---|---|---|---|---|
```

`Fix` is `—` on the last clean or questions-only review. The extra line is
the stamp (`APPROVE` / `APPROVED` comment url) or why there is none.

## Do not

- Review or edit the PR yourself.
- Launch Fix when the review is clean or only `q` remains.
- Stamp a dirty or questions-only result.
- Fetch sibling skills without approval.
- Invent a PR, a model slug, or a finding.

## Catalog

This conductor lives in `sycamore-hq/crossr-loops`. Register it in the
invoking project's `AGENTS.md` Skills list. The capability catalog
(`sycamore-hq/crossr-skills` `docs/public-skills.json`) does not take
orchestration skills.
