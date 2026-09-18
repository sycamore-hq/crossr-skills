#!/usr/bin/env python3
"""A landed book must not still read as in flight in the plan or prompt set.

Issue #5 (pr5-record): the rust and ocaml books landed while the plan and
prompt-set headers still stopped at PR 4 / "5b in flight". The tracker half of
this guard left with features.json and progress.md; the plan documents are still
repository artifacts, and they can still lie.

Calculations are pure. Loading the tree is the action.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
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
STATUS_MD = re.compile(
    r"^\|\s*(5[a-g])\s*\|\s*\S+\s*\|\s*\**([^*|]+?)\**\s*\|",
    re.M,
)
STATUS_HTML = re.compile(
    r'<td class="mono">(5[a-g])</td>\s*<td>[^<]+</td>\s*<td[^>]*>([^<]+)</td>',
)
LANDED = re.compile(r"(?:PR\s+)?(5[ab])\s+landed", re.I)


def plan_status_line(text: str) -> str:
    return next((line for line in text.splitlines() if line.startswith("**Status:**")), "")


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
        cls.plan = (ROOT / "docs" / "plans" / "gan-layer-separation-plan.md").read_text()
        cls.plan_html = (ROOT / "docs" / "plans" / "gan-layer-separation-plan.html").read_text()
        cls.prompt = (ROOT / "docs" / "plans" / "pr5-one-law-prompt-set.md").read_text()
        cls.prompt_html = (ROOT / "docs" / "plans" / "pr5-one-law-prompt-set.html").read_text()

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


if __name__ == "__main__":
    unittest.main()
