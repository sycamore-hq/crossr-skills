#!/usr/bin/env python3
"""Work state lives on the board. It never lives in a file in this repo.

`features.json`, `features.schema.json` and `progress.md` were removed at the
board cutover (harness `HARNESS-SPEC.md` §3.2). They are named here so they
cannot come back quietly.

The failure mode is specific and was observed, not imagined: a file tracker and
a board both claim to know what is in flight, they drift, and the one someone is
reading is the stale one. At the cutover, two units sat at `in_progress` in a
committed `features.json` while the work had already shipped. Nothing caught it
because nothing was looking.

This is what looks.

Calculations are pure. Walking the tree is the action.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Exact names, because the failure mode is these files returning — not a fuzzy
# resemblance to them. A board export written to disk is a view and is fine; it
# just must not be called one of these.
TRACKER_NAMES = frozenset({"features.json", "features.schema.json", "progress.md"})

# Build output and vendored trees are not this repo's tracking decisions.
PRUNED_DIRS = frozenset({".git", "__pycache__", "target", "node_modules", ".venv", "public"})


def tracker_files(root: Path, names: frozenset[str] = TRACKER_NAMES) -> list[str]:
    """Repo-relative paths of any file tracker in the tree, sorted."""
    hits: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in PRUNED_DIRS]
        for name in filenames:
            if name in names:
                hits.append(str(Path(dirpath, name).relative_to(root)))
    return sorted(hits)


class Calculations(unittest.TestCase):
    """The finder has to actually find things, or the guard below is theatre."""

    def test_finds_a_tracker_at_the_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "features.json").write_text("{}")
            self.assertEqual(tracker_files(Path(tmp)), ["features.json"])

    def test_finds_a_tracker_nested_anywhere(self):
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "docs" / "archive"
            nested.mkdir(parents=True)
            (nested / "progress.md").write_text("x")
            self.assertEqual(tracker_files(Path(tmp)), ["docs/archive/progress.md"])

    def test_finds_every_named_tracker(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in TRACKER_NAMES:
                (Path(tmp) / name).write_text("x")
            self.assertEqual(len(tracker_files(Path(tmp))), len(TRACKER_NAMES))

    def test_build_output_is_not_a_tracking_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            pruned = Path(tmp) / "target" / "debug"
            pruned.mkdir(parents=True)
            (pruned / "features.json").write_text("{}")
            self.assertEqual(tracker_files(Path(tmp)), [])

    def test_a_clean_tree_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "board.json").write_text("{}")
            (Path(tmp) / "lockfile.toml").write_text("")
            self.assertEqual(tracker_files(Path(tmp)), [])


class LiveTree(unittest.TestCase):
    def test_repo_has_no_file_tracker(self):
        found = tracker_files(ROOT)
        self.assertEqual(
            found,
            [],
            "work state belongs on the board, not in these files "
            f"(HARNESS-SPEC.md §3.2): {found}",
        )


if __name__ == "__main__":
    unittest.main()
