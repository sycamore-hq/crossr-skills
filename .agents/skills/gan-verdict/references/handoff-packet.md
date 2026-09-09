# Handoff packet

Inbound field schema. The conductor fills this; the adversary
receives nothing else. `audit-packet brief` is the gate.

Location: the disclosed scratch path, fallback
`${TMPDIR:-/tmp}/crossr-packets/<pbi-id>/phase-<k>.<gate>.packet.md`.
Never committed. Never under the repo tree.

No `## ` heading other than Files, Diff, AC, Claims, Prior
verdicts, Envelope is legal. Prose outside list items is illegal
outside the fence.

Shape:

- heading: `# Packet: <phase-id>`
- `- k of n: <k> of <n>`
- `- gate: <gate-name>`
- `## Files` — `- <path>` (≥ 1)
- `## Diff` — `- ref: <path-or-range>` and/or a ```diff fence
- `## AC` — `- AC-nn: <text>` (≥ 1)
- `## Claims` — `- C-nn` (optional)
- `## Prior verdicts` — may be empty; each line `- <gate> BLESS` or `- <gate> REJECT: <≤140 chars>`
- `## Envelope` — `- name: value` from gan-verdict item 5

Example:

````markdown
# Packet: T-1
- k of n: 1 of 3
- gate: code-review
## Files
- src/parse.py
## Diff
- ref: HEAD~1
```diff
--- a/src/parse.py
+++ b/src/parse.py
@@ -1,2 +1,3 @@
 context
+added
```
## AC
- AC-01: parse rejects empty input
## Claims
- C-01
## Prior verdicts
- testing BLESS
## Envelope
- findings shape: one-liners
- max length: 40 lines
- citations: file:line
````
