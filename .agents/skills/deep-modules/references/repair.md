# Repair

Findings are fixed by redesign, and old debt is ratcheted, never hidden.

## Rules

MD-07  Fix structure from first principles. A finding is resolved by deciding which layer each piece belongs to and what the narrow interface is, not by moving, renaming, re-exporting or wrapping code until a check stops reporting it. Each fix shows a before-and-after picture of the structure.

MD-08  Ratchet existing debt. A codebase adopting this book records today's findings in a committed baseline; a new finding fails, a fixed one is deleted from the baseline in the same change, and nothing is added to the baseline without a reason in the change description.
         check: scripts/check-structure --baseline .deep-modules.baseline

## How

For every finding, answer three questions before editing:

1. What layer is each module or type at? Draw the layers.
2. What are callers actually trying to do? List the patterns of use across all call sites.
3. What is the smallest interface that serves those patterns?

Then change the code to match the answer, and draw the after picture with `show-me` (a tree or box diagram is enough). If the answer is "this module should not exist," delete it; subtraction is a valid fix.

Mechanical moves that fail review: lifting one item into the parent to break a cycle while both siblings still depend on it; swapping a public field for a getter that returns `&mut`; splitting a long file into `part1`/`part2`; adding a re-export so callers keep reaching through.

Adopting the book on an existing codebase:

```bash
.agents/skills/deep-modules/scripts/check-structure . --write-baseline .deep-modules.baseline
git add .deep-modules.baseline
# from now on, in the project's test or check target:
.agents/skills/deep-modules/scripts/check-structure . --baseline .deep-modules.baseline
```

The baseline is plain text, one `<rule> <key>` per line, sorted. Fixing an entry never fails the check; instead the script lists it as a stale baseline entry, and `MD-08` requires deleting that line in the same change.
