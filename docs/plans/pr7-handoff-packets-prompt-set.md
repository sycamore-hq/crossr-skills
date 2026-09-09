# PR 7 prompt set — Handoff packets, envelopes, AVRIL batching

Plan: `docs/plans/gan-layer-separation-plan.md` §3.3 / §3.8 / §4 PR 7 / §6 / §7
row 7. Work#12. 7a and 7b recorded that this file was not on `main`; 7d lands
the settlement table and the measured status. No HTML twin (Unresolved 1).

Decisions 1–13 below are the PR 7 settlement (plan §8 decision 13). They are
the facts the four briefs were blessed against, reconstructed from the landed
PRs. They do not invent new law.

| # | Decision |
|---|---|
| 1 | Scratch path. Packets live at the disclosed path, default `${TMPDIR:-/tmp}/crossr-packets/<pbi-id>/`. Never inside the repo, never committed. |
| 2 | Packet field schema lives in `gan-verdict` (items 8–10). Adding a field changes that file, never a conductor card. |
| 3 | A bare BLESS over a set is not a verdict. One line per id: `BLESS <id>` \| `REJECT <id> — <blockers>`. |
| 4 | `batch: true` on AVRIL adversaries. `verify-protocol` requires a per-item declaration on batch personas. Mixed `<gate>: BLESS` on a batch persona fails. |
| 5 | `audit-packet` is the mechanical gate. `brief` before an adversary reads a packet; `verdict` before a conductor reads a reply. Red never reaches a persona. |
| 6 | Packet grammar in `references/handoff-packet.md`. Never a sibling SKILL.md, a previous-phase essay, a whole-board dump, or dashboard HTML. |
| 7 | Envelope stays last (items 1–7 unchanged). Packet fields are a second schema with the same field-add rule (item 10). |
| 8 | No CI. Tags cut after pasted validation on the merge commit. Never re-point. |
| 9 | No batch-size cap. |
| 10 | AXEL packet ritual: audit before every delegation; drop review prose after commit. The plan record names PR 6 landed (no tag; retired by 7a/7b) so the closer does not lie. |
| 11 | Bootstrap installs `audit-packet` from the skills pin. HARNESS-SPEC §6 names the packet audit in the diff gate; §12 discloses the scratch path. |
| 12 | Landed §7 rows are frozen. Row 7 stayed a draft until this merge, then was edited in place to the measured statement. |
| 13 | Phase closes with 7d. Status leading word is `complete`. Acceptance condition 1 stays undemonstrated (no Elm/Melange run); condition 2 is a running measure. |

---

## Status (measured 2026-09-09)

7a/7b/7c have tracker rows on their remotes. 7d closes the PR 7 stack and the
`gan-layer-separation` phase. No HTML twin for this file.

| PR | Repo | State | Evidence |
|---|---|---|---|
| 7a | skills | **Landed** | [#126](https://github.com/sycamore-hq/crossr-skills/pull/126), rebase-merged 2026-09-09 as `ed45131`..`7536be9` (4 commits). Tag `v1-packets` peels to `7536be9162f21bd82530bdc741b53e3d5f7fb1a7`. |
| 7b | loops | **Landed** | [#12](https://github.com/sycamore-hq/crossr-loops/pull/12), rebase-merged 2026-09-09 as `9f4a239`..`9e5b3f1`. Tag `v1-packets-consumers` (`10bbff33`) peels to `9e5b3f16d0adc82032bd9e12642d5de6250e6be2`. |
| 7c | harness | **Landed** | [#11](https://github.com/sycamore-hq/crossr-harness/pull/11), rebase-merged 2026-09-09 as `338f83c`..`006508d`. Merge SHA `006508d63de8fc185cc026ee873710ae878cba2e`. No tag cut. |
| 7d | skills | **This PR** | [#127](https://github.com/sycamore-hq/crossr-skills/pull/127). Pin `loops = "v1-packets-consumers"` at every locus `test_pr5f.py` reads. `just regen-agents` twice. Plan twins mark PR 6 and PR 7 landed. Phase status `completed`. No tag cut. |
