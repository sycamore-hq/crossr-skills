# HoH evidence packet — fold into PR 6 / PR 7

**Status:** draft rider, 2026-09-05. Absorbs into
`docs/plans/gan-layer-separation-plan.md` (§3.7 rule 5, §3.8, §4 PR 6, §4 PR 7,
§6, §7 rows 6–7, decision #13). Not a new PR number. Not a fifth remote.

Source: Yan et al., *Harness-of-Harness*, arXiv:2609.01481 (1 Sep 2026).
Evaluated against the live remotes the same day. Steal the packet contract.
Do not wrap HoH.

## What lands

Normalized evidence packet `E_t` is the memory between loops. Chat is not.

Fields (schema on the `gan-verdict` menu; conductor fills; adding a field
edits `gan-verdict`, not a conductor card):

- claim id
- observation path (`file:line`, log, screenshot, test name)
- status: `verified` or `gap`
- preservation constraint (what must still work next loop)
- frozen commit SHA

Packet lives in the completion record / `progress.md` / the ledger.

## PR 6 — `plan-writer` consumes `E_t`

When a prior packet exists, `plan-writer` loads it. Gaps and preservation
constraints become claims.

Preserve-vs-grow is a plan rule: every increment lists functionality that
must survive, sourced from verified records when present. An AC that only
adds capability and never names preservation is incomplete.

Scope change still returns to AVRIL. AXEL does not re-bless product intent.

`plan-writer` stays a skill, not a persona (decision #11).

## PR 7 — write `E_t`, freeze-then-QA, feed-forward

Envelope schema grows the fields above.

After the phase commit, Tester runs a read-only pass on that SHA and writes
the packet. Tester stays the persona. No new role. The candidate is frozen;
Tester may not repair during the evidence pass.

Next AVRIL activation loads the packet. AXEL still does not re-bless intent.

Per-item `BLESS` inside AVRIL batches stays required.

## §7 measurables (unlanded rows; drafts may move)

- PR 6: when a prior packet exists, the plan consumes it and names
  preservation claims.
- PR 7: packet fields are on the `gan-verdict` menu; post-commit QA writes
  `verified`|`gap` records frozen to a SHA; next AVRIL activation can load
  the packet without the chat.

## Do not cut / do not do

- Independent QA on a frozen candidate.
- Evidence packet as memory. The next planner reads the packet, not the chat.
- No fifth control plane. HoH confirms this shape. It is not a product to
  wrap. Graph runner stays parked (`sycamore-hq/work#14`). Lights-off factory
  stays refused; Berea remains the andon.

## Tickets

- `sycamore-hq/work#11` (`pr6`)
- `sycamore-hq/work#12` (`pr7`)
- `sycamore-hq/work#14` stays parked
