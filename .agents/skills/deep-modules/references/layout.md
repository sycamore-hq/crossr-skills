# Layout

A reader scans a directory and scrolls a file. Both have a size past which they stop reading and start searching.

## Rules

MD-05  No wide directories. A directory holds at most fifteen entries counting source files and subdirectories that contain source files.
         check: scripts/check-structure --max-entries 15

MD-06  No long files. A source file has at most 2,000 lines, counting blank lines, comments and test code.
         check: scripts/check-structure --max-lines 2000

## How

Both limits are smoke detectors for `MD-01` to `MD-04`. A directory with twenty files is usually two or three concepts sharing a folder; group them by what they are about, and each group becomes a module with its own narrow interface. Splitting alphabetically or by file type (`types/`, `utils/`, `helpers/`) satisfies the count and fails the point.

A 2,000-line file almost always contains a module that wants out. Find the cluster of functions that share data and nothing else, and promote it to a child module whose interface is the two or three calls the rest of the file makes into it.

Run the check from the repository root:

```bash
.agents/skills/deep-modules/scripts/check-structure . --ext .rs
```

`--ext` repeats for other languages (`--ext .ml --ext .mli`). Build output and vendored trees (`target`, `_build`, `node_modules`, `vendor`) and every dot-directory (`.git`, `.venv`, …) are skipped. Exit code 1 means new findings; 2 means bad arguments or an unreadable file.

Thresholds are flags so a project can tighten them. Loosening them needs the same justification as a baseline entry (`MD-08`).
