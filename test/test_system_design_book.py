#!/usr/bin/env python3
"""The cross-cutting system-design book extracts exactly like a language book.

SYC-16: extract-rules must select `scope: cross-cutting` books, keep their ids
stable, and catch drift or disappeared ids in them the same way it does for
rust and ocaml. Absent scope keeps the language-book meaning.

Calculations are pure. Copying the book into a temp tree is the action.
"""

from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".agents" / "skills"
BOOK = SKILLS / "system-design"
_spec = importlib.util.spec_from_loader(
    "extract_rules",
    importlib.machinery.SourceFileLoader("extract_rules", str(ROOT / "scripts" / "extract-rules")),
)
extract_rules = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(extract_rules)

TOPIC_PREFIXES = {"DF", "DP", "DS", "DB", "DX", "DI", "DA"}


def quiet_check(book_dir: Path) -> int:
    rendered = extract_rules.render(book_dir.name, extract_rules.collect_book(book_dir))
    with contextlib.redirect_stderr(io.StringIO()):
        return extract_rules.write_or_check(book_dir, rendered, check=True)


class Discovery(unittest.TestCase):
    def test_system_design_is_a_discovered_book(self):
        names = [p.name for p in extract_rules.discover_books(SKILLS)]
        self.assertIn("system-design", names)

    def test_system_design_is_cross_cutting(self):
        self.assertEqual(extract_rules.book_scope(BOOK / "SKILL.md"), "cross-cutting")

    def test_language_books_default_to_language_scope(self):
        for name in ("rust", "ocaml"):
            with self.subTest(book=name):
                self.assertEqual(extract_rules.book_scope(SKILLS / name / "SKILL.md"), "language")


class Rules(unittest.TestCase):
    def test_ids_are_qualified_and_use_only_registered_prefixes(self):
        rules = extract_rules.collect_book(BOOK)
        self.assertEqual({r["prefix"] for r in rules}, TOPIC_PREFIXES)
        self.assertTrue(all(r["qualified"].startswith("system-design/") for r in rules))

    def test_no_prefix_collides_with_a_language_book(self):
        language = {
            r["prefix"]
            for name in ("rust", "ocaml")
            for r in extract_rules.collect_book(SKILLS / name)
        }
        self.assertEqual(TOPIC_PREFIXES & language, set())

    def test_contract_files_are_not_extracted(self):
        topics = {r["topic"] for r in extract_rules.collect_book(BOOK)}
        self.assertEqual(topics & {"specialization", "verification"}, set())

    def test_committed_rules_are_clean(self):
        self.assertEqual(quiet_check(BOOK), 0)


class DriftInACopy(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.book = self.tmp / "system-design"
        shutil.copytree(BOOK, self.book)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_edited_rule_text_is_drift(self):
        ref = self.book / "references" / "idempotency.md"
        ref.write_text(ref.read_text().replace("is idempotent", "should be idempotent", 1))
        self.assertEqual(quiet_check(self.book), 1)

    def test_removed_rule_id_is_a_disappearance(self):
        ref = self.book / "references" / "premise.md"
        text = ref.read_text()
        start = text.index("DP-03")
        ref.write_text(text[:start] + text[text.index("## How"):])
        self.assertEqual(quiet_check(self.book), 1)


class Wiring(unittest.TestCase):
    """The planner loads the How; the gate loads Rules only; DA-01 is enforced."""

    def test_gate_consumes_cross_cutting_rules_not_references(self):
        gate = (SKILLS / "architecture" / "SKILL.md").read_text()
        self.assertIn("cross-cutting", gate)
        self.assertIn("system-design/RULES.md", gate)
        self.assertIn("DA-01", gate)
        self.assertRegex(gate, r"Never a book's `references/`")

    def test_planner_loads_cross_cutting_card_rules_and_routed_references(self):
        card = (SKILLS / "plan-writer" / "SKILL.md").read_text()
        self.assertRegex(card, r"cross-cutting book's card, Rules, and the references")
        self.assertIn("System-design applicability", card)

    def test_execute_review_and_test_cards_do_not_name_the_book(self):
        for name in ("code-review", "testing"):
            with self.subTest(card=name):
                self.assertNotIn("system-design", (SKILLS / name / "SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
