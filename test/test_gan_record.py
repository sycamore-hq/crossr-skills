#!/usr/bin/env python3
"""Books on disk must have tracker rows. Phase status must match the plan header.

Issue #5 (pr5-record): rust/ocaml books landed; features.json, progress.md,
and the plan/prompt-set headers still stopped at PR 4 / "5b in flight".
Issue #6 (gan-close-4b): a completed phase while the plan header says
in progress is the contradiction; recorded-children-all-done is not.

Calculations are pure. Loading the tree is the action.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_loader(
    "extract_rules",
    importlib.machinery.SourceFileLoader(
        "extract_rules", str(ROOT / "scripts" / "extract-rules")
    ),
)
extract_rules = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(extract_rules)

PHASE = "gan-layer-separation"
BOOK_PR = {"rust": "5a", "ocaml": "5b"}
BOOK_COMMIT = {"rust": "pr5a", "ocaml": "pr5b"}
STATUS_MD = re.compile(
    r"^\|\s*(5[a-g])\s*\|\s*\S+\s*\|\s*\**([^*|]+?)\**\s*\|",
    re.M,
)
STATUS_HTML = re.compile(
    r'<td class="mono">(5[a-g])</td>\s*<td>[^<]+</td>\s*<td[^>]*>([^<]+)</td>',
)
PROGRESS_DONE = re.compile(
    r"^### gan-layer-separation — PR (5[ab]) \(COMPLETED\)",
    re.M,
)
LANDED = re.compile(r"(?:PR\s+)?(5[ab])\s+landed", re.I)
PLAN_IN_PROGRESS = re.compile(r"(?i)\bin progress\b")


def completed_ids(phase: dict) -> set[str]:
    return {
        c["id"]
        for c in phase.get("commits") or []
        if c.get("status") == "completed" and c.get("id")
    }


def books_missing_rows(
    books: list[str], commit_ids: set[str], mapping: dict[str, str] = BOOK_COMMIT
) -> list[str]:
    """A book on disk is recorded iff its PR-5 commit id is completed."""
    missing = []
    for book in books:
        commit_id = mapping.get(book)
        if commit_id is None or commit_id not in commit_ids:
            missing.append(book)
    return missing


def plan_status_line(text: str) -> str:
    return next((line for line in text.splitlines() if line.startswith("**Status:**")), "")


def phase_disagrees_with_plan(phase: dict, status_line: str) -> bool:
    """True when features.json closed the phase and the plan header did not."""
    return phase.get("status") == "completed" and bool(PLAN_IN_PROGRESS.search(status_line))


def inflight_rows(rows: list[tuple[str, str]], books: list[str]) -> list[str]:
    needed = {BOOK_PR[b] for b in books if b in BOOK_PR}
    return [
        pr
        for pr, state in rows
        if pr in needed and "in flight" in state.lower()
    ]


def landed_prs(text: str) -> set[str]:
    return {m.group(1) for m in LANDED.finditer(text)}


def header_missing_landed(text: str, books: list[str]) -> list[str]:
    found = landed_prs(text)
    return [BOOK_PR[b] for b in books if b in BOOK_PR and BOOK_PR[b] not in found]


class Calculations(unittest.TestCase):
    def test_book_row_is_the_pr5_commit_id(self):
        ids = {"pr5a", "pr4b"}
        self.assertEqual(books_missing_rows(["rust", "ocaml"], ids), ["ocaml"])
        self.assertEqual(books_missing_rows(["rust"], ids), [])

    def test_unmapped_book_is_reported(self):
        self.assertEqual(books_missing_rows(["elm"], {"pr5a", "pr5b"}), ["elm"])

    def test_rust_team_lead_title_is_not_the_rust_book_row(self):
        ids = completed_ids({
            "commits": [
                {"id": "pr3a", "title": "delete rust-team-lead", "status": "completed"},
            ]
        })
        self.assertEqual(books_missing_rows(["rust"], ids), ["rust"])

    def test_completed_phase_against_in_progress_plan_disagrees(self):
        self.assertTrue(
            phase_disagrees_with_plan(
                {"status": "completed"},
                "**Status:** in progress · PR 5b landed",
            )
        )

    def test_in_progress_phase_against_in_progress_plan_agrees(self):
        self.assertFalse(
            phase_disagrees_with_plan(
                {"status": "in_progress"},
                "**Status:** in progress · PR 5b landed",
            )
        )

    def test_completed_phase_against_done_plan_agrees(self):
        self.assertFalse(
            phase_disagrees_with_plan(
                {"status": "completed"},
                "**Status:** complete · PR 7 landed",
            )
        )

    def test_plan_status_line_is_the_status_heading(self):
        text = "# Plan\n\n**Status:** in progress · PR 5b landed\n**Scope:** x\n"
        self.assertEqual(plan_status_line(text), "**Status:** in progress · PR 5b landed")

    def test_inflight_only_counts_books_that_exist(self):
        rows = [("5a", "Landed"), ("5b", "In flight"), ("5c", "In flight")]
        self.assertEqual(inflight_rows(rows, ["rust", "ocaml"]), ["5b"])
        self.assertEqual(inflight_rows(rows, ["rust"]), [])

    def test_header_requires_landed_word(self):
        text = "Status: in progress · PR 4 landed · PR 5a landed (#117)"
        self.assertEqual(header_missing_landed(text, ["rust", "ocaml"]), ["5b"])


class LiveTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = [p.name for p in extract_rules.discover_books(ROOT / ".agents" / "skills")]
        cls.features = json.loads((ROOT / "features.json").read_text())
        cls.phase = cls.features[PHASE]
        cls.progress = (ROOT / "progress.md").read_text()
        cls.plan = (ROOT / "docs" / "plans" / "gan-layer-separation-plan.md").read_text()
        cls.plan_html = (ROOT / "docs" / "plans" / "gan-layer-separation-plan.html").read_text()
        cls.prompt = (ROOT / "docs" / "plans" / "pr5-one-law-prompt-set.md").read_text()
        cls.prompt_html = (ROOT / "docs" / "plans" / "pr5-one-law-prompt-set.html").read_text()

    def test_each_book_has_a_completed_gan_row(self):
        missing = books_missing_rows(self.books, completed_ids(self.phase))
        self.assertEqual(missing, [], f"gan-layer-separation missing rows for {missing}")

    def test_progress_records_5a_and_5b_completed(self):
        found = set(PROGRESS_DONE.findall(self.progress))
        needed = {BOOK_PR[b] for b in self.books if b in BOOK_PR}
        self.assertEqual(needed - found, set(), f"progress.md missing COMPLETED sections for {needed - found}")

    def test_plan_header_names_5a_and_5b_landed(self):
        status = next((l for l in self.plan.splitlines() if l.startswith("**Status:**")), "")
        missing = header_missing_landed(status, self.books)
        self.assertEqual(missing, [], f"plan Status line omitted landed {missing}: {status}")

    def test_plan_html_names_5a_and_5b_landed(self):
        missing = header_missing_landed(self.plan_html, self.books)
        self.assertEqual(missing, [], f"plan HTML omitted landed {missing}")

    def test_prompt_set_does_not_leave_a_landed_book_in_flight(self):
        rows = STATUS_MD.findall(self.prompt)
        self.assertTrue(rows, "prompt-set markdown has no status table")
        self.assertEqual(inflight_rows(rows, self.books), [])

    def test_prompt_set_html_does_not_leave_a_landed_book_in_flight(self):
        rows = STATUS_HTML.findall(self.prompt_html)
        self.assertTrue(rows, "prompt-set HTML has no status table")
        self.assertEqual(inflight_rows(rows, self.books), [])

    def test_phase_status_agrees_with_plan_header(self):
        status = plan_status_line(self.plan)
        self.assertFalse(
            phase_disagrees_with_plan(self.phase, status),
            f"{PHASE} is {self.phase.get('status')!r}; plan header is {status!r}",
        )


if __name__ == "__main__":
    unittest.main()
