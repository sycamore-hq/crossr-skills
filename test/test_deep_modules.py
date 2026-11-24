#!/usr/bin/env python3
"""deep-modules: the book extracts as a cross-cutting book, and check-structure
reports long files and wide directories, honours a baseline, and rejects bad input.
"""

from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / ".agents" / "skills" / "deep-modules"
SCRIPT = BOOK / "scripts" / "check-structure"
sys.path.insert(0, str(ROOT / "scripts"))


def load(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


CHECK = load("check_structure", SCRIPT)
EXTRACT = load("extract_rules", ROOT / "scripts" / "extract-rules")


def write(root: Path, relative: str, lines: int = 1) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x\n" * lines, encoding="utf-8")


def run(*words: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = CHECK.main(list(words))
    return code, out.getvalue(), err.getvalue()


class Book(unittest.TestCase):
    def test_is_a_cross_cutting_book(self):
        self.assertIn(BOOK, EXTRACT.discover_books(ROOT / ".agents" / "skills"))
        self.assertEqual(EXTRACT.book_scope(BOOK / "SKILL.md"), "cross-cutting")

    def test_rules_are_md_01_to_08(self):
        ids = [rule["bare_id"] for rule in EXTRACT.collect_book(BOOK)]
        self.assertEqual(sorted(ids), [f"MD-0{n}" for n in range(1, 9)])

    def test_committed_rules_match_extraction(self):
        rendered = EXTRACT.render(BOOK.name, EXTRACT.collect_book(BOOK))
        self.assertEqual((BOOK / "RULES.md").read_text(encoding="utf-8"), rendered)
        self.assertIn("check: scripts/check-structure --max-lines 2000", rendered)

    def test_upstream_tool_is_credited_but_not_required(self):
        card = (BOOK / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Deterministic Machines", card)
        self.assertIn("MIT", card)
        self.assertNotIn("cargo install", "".join(
            p.read_text(encoding="utf-8") for p in BOOK.rglob("*.md")))


class Layout(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_tree_passes(self):
        write(self.root, "src/lib.rs", 10)
        self.assertEqual(run(str(self.root))[0], 0)

    def test_long_file_is_reported(self):
        write(self.root, "src/lib.rs", 11)
        code, out, _ = run(str(self.root), "--max-lines", "10")
        self.assertEqual(code, 1)
        self.assertIn("MD-06 src/lib.rs has 11 lines, more than 10", out)

    def test_wide_directory_counts_files_and_source_subdirectories(self):
        write(self.root, "src/a.rs")
        write(self.root, "src/b.rs")
        write(self.root, "src/c/d.rs")
        write(self.root, "src/notes.txt")
        code, out, _ = run(str(self.root), "--max-entries", "2")
        self.assertEqual(code, 1)
        self.assertIn("MD-05 src/ holds 3 source entries, more than 2", out)

    def test_build_output_is_skipped(self):
        write(self.root, "target/debug/big.rs", 50)
        self.assertEqual(run(str(self.root), "--max-lines", "10")[0], 0)

    def test_other_languages_by_extension(self):
        write(self.root, "lib/a.ml", 11)
        self.assertEqual(run(str(self.root), "--max-lines", "10")[0], 0)
        self.assertEqual(run(str(self.root), "--max-lines", "10", "--ext", ".ml")[0], 1)

    def test_baseline_ratchet(self):
        write(self.root, "src/old.rs", 11)
        baseline = self.root / "baseline"
        self.assertEqual(run(str(self.root), "--max-lines", "10", "--write-baseline", str(baseline))[0], 0)
        self.assertEqual(baseline.read_text(), "MD-06 src/old.rs\n")
        self.assertEqual(run(str(self.root), "--max-lines", "10", "--baseline", str(baseline))[0], 0)
        write(self.root, "src/new.rs", 11)
        code, out, _ = run(str(self.root), "--max-lines", "10", "--baseline", str(baseline))
        self.assertEqual(code, 1)
        self.assertIn("src/new.rs", out)
        self.assertNotIn("src/old.rs", out)

    def test_fixed_baseline_entry_is_listed_as_stale(self):
        baseline = self.root / "baseline"
        baseline.write_text("MD-06 src/gone.rs\n")
        write(self.root, "src/lib.rs")
        code, out, _ = run(str(self.root), "--baseline", str(baseline))
        self.assertEqual(code, 0)
        self.assertIn("stale baseline entry, delete it: MD-06 src/gone.rs", out)

    def test_wide_root_directory(self):
        for name in "abc":
            write(self.root, f"{name}.rs")
        code, out, _ = run(str(self.root), "--max-entries", "2")
        self.assertEqual(code, 1)
        self.assertIn("MD-05 the root directory holds 3 source entries", out)

    def test_dot_directories_are_skipped(self):
        write(self.root, ".venv/lib/big.py", 50)
        self.assertEqual(run(str(self.root), "--ext", ".py", "--max-lines", "10")[0], 0)

    def test_lines_are_newlines_not_form_feeds(self):
        (self.root / "a.rs").write_text("x\fy\n" * 10, encoding="utf-8")
        self.assertEqual(run(str(self.root), "--max-lines", "10")[0], 0)

    def test_repeated_ext_checks_every_extension(self):
        write(self.root, "a.ml", 11)
        write(self.root, "a.mli", 11)
        code, out, _ = run(str(self.root), "--max-lines", "10", "--ext", ".ml", "--ext", ".mli")
        self.assertEqual(code, 1)
        self.assertIn("a.ml has", out)
        self.assertIn("a.mli has", out)

    def test_unwritable_baseline_is_an_error(self):
        target = self.root / "missing" / "baseline"
        code, _, err = run(str(self.root), "--write-baseline", str(target))
        self.assertEqual(code, 2)
        self.assertIn("unwritable", err)

    def test_malformed_baseline_is_an_error(self):
        baseline = self.root / "baseline"
        baseline.write_text("ZZ-01 thing\n")
        code, _, err = run(str(self.root), "--baseline", str(baseline))
        self.assertEqual(code, 2)
        self.assertIn("bad-baseline", err)


class Arguments(unittest.TestCase):
    def test_defaults(self):
        options = CHECK.parse_arguments([])
        self.assertEqual((options.max_lines, options.max_entries), (2000, 15))

    def test_errors_are_typed(self):
        cases = {
            ("--max-lines", "0"): CHECK.Failure.BAD_ARGUMENTS,
            ("--max-lines",): CHECK.Failure.BAD_ARGUMENTS,
            ("--max-lines", "\u00b2"): CHECK.Failure.BAD_ARGUMENTS,
            ("--bogus",): CHECK.Failure.BAD_ARGUMENTS,
            ("--ext", "rs"): CHECK.Failure.BAD_ARGUMENTS,
            ("a", "b"): CHECK.Failure.BAD_ARGUMENTS,
            ("--baseline", "x", "--write-baseline", "y"): CHECK.Failure.BAD_ARGUMENTS,
        }
        for words, kind in cases.items():
            with self.subTest(words=words), self.assertRaises(CHECK.Error) as caught:
                CHECK.parse_arguments(list(words))
            self.assertEqual(caught.exception.kind, kind)

    def test_help_exits_0(self):
        code, out, _ = run("--help")
        self.assertEqual(code, 0)
        self.assertIn("Usage:", out)

    def test_missing_root_exits_2(self):
        self.assertEqual(run("/nonexistent/deep-modules")[0], 2)


if __name__ == "__main__":
    unittest.main()
