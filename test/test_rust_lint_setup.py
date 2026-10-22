#!/usr/bin/env python3
"""rust/RC-09: the lint templates pass check-lint-setup, and broken setups fail.

The clippy self-test builds a throwaway crate from the templates with deliberate
violations and asserts clippy rejects it. It is skipped when cargo-clippy is
not installed.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".agents" / "skills" / "rust"
TEMPLATES = SKILL / "templates"
SCRIPT = SKILL / "scripts" / "check-lint-setup"


def load_checker():
    loader = importlib.machinery.SourceFileLoader("check_lint_setup", str(SCRIPT))
    spec = importlib.util.spec_from_loader("check_lint_setup", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


CHECK = load_checker()
LINTS = (TEMPLATES / "Cargo.lints.toml").read_text(encoding="utf-8")
CONFIG = (TEMPLATES / "clippy.toml").read_text(encoding="utf-8")
PACKAGE = '[package]\nname = "{name}"\nversion = "0.1.0"\nedition = "2021"\n\n'
INHERIT = "[lints]\nworkspace = true\n"


def write_repo(root: Path, *, root_manifest: str, config: str = CONFIG,
               member: str | None = None) -> Path:
    (root / "Cargo.toml").write_text(root_manifest, encoding="utf-8")
    (root / "clippy.toml").write_text(config, encoding="utf-8")
    if member is not None:
        (root / "crates" / "a").mkdir(parents=True)
        (root / "crates" / "a" / "Cargo.toml").write_text(member, encoding="utf-8")
    return root


def single_crate(extra: str = "") -> str:
    return "[workspace]\n\n" + PACKAGE.format(name="demo") + INHERIT + "\n" + LINTS + extra


class TemplatesPass(unittest.TestCase):
    def test_single_crate_from_templates_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = write_repo(Path(tmp), root_manifest=single_crate())
            self.assertEqual(CHECK.check_repo(repo), [])

    def test_virtual_workspace_with_inheriting_member_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = '[workspace]\nmembers = ["crates/a"]\n\n' + LINTS
            repo = write_repo(Path(tmp), root_manifest=root,
                              member=PACKAGE.format(name="a") + INHERIT)
            self.assertEqual(CHECK.check_repo(repo), [])

    def test_repo_clippy_toml_is_the_template(self):
        self.assertEqual((ROOT / "clippy.toml").read_text(encoding="utf-8"), CONFIG)


class DeliberateViolationsFail(unittest.TestCase):
    def problems(self, **kwargs) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            return CHECK.check_repo(write_repo(Path(tmp), **kwargs))

    def test_lints_table_in_clippy_toml(self):
        found = self.problems(root_manifest=single_crate(),
                              config=CONFIG + '\n[lints.clippy]\nunwrap_used = "deny"\n')
        self.assertTrue(any("[lints] table" in p for p in found), found)

    def test_member_not_inheriting(self):
        root = '[workspace]\nmembers = ["crates/a"]\n\n' + LINTS
        found = self.problems(root_manifest=root, member=PACKAGE.format(name="a"))
        self.assertTrue(any("workspace = true" in p for p in found), found)

    def test_required_lint_missing(self):
        found = self.problems(root_manifest=single_crate().replace('unwrap_used = "deny"\n', ""))
        self.assertTrue(any("`unwrap_used`" in p for p in found), found)

    def test_required_lint_too_weak(self):
        found = self.problems(root_manifest=single_crate().replace(
            'print_stderr = "deny"', 'print_stderr = "warn"'))
        self.assertTrue(any("`print_stderr` is 'warn'" in p for p in found), found)

    def test_threshold_changed(self):
        found = self.problems(root_manifest=single_crate(), config=CONFIG.replace(
            "excessive-nesting-threshold = 4", "excessive-nesting-threshold = 9"))
        self.assertTrue(any("excessive-nesting-threshold" in p for p in found), found)

    def test_anyhow_not_disallowed(self):
        found = self.problems(root_manifest=single_crate(),
                              config=CONFIG.replace('"anyhow::Error"', '"other::Error"'))
        self.assertTrue(any("anyhow::Error" in p for p in found), found)

    def test_no_workspace_lints(self):
        found = self.problems(root_manifest="[workspace]\n\n" + PACKAGE.format(name="d") + INHERIT)
        self.assertTrue(any("[workspace.lints]" in p for p in found), found)


@unittest.skipUnless(shutil.which("cargo") and subprocess.run(
    ["cargo", "clippy", "--version"], capture_output=True).returncode == 0,
    "cargo clippy not installed")
class ClippyRejectsViolations(unittest.TestCase):
    def test_clippy_denies_deliberate_violations(self):
        bad = ('//! demo\nfn main() {\n    let v: Option<u8> = None;\n'
               '    eprintln!("{}", v.unwrap());\n    let _ = std::env::var("X");\n}\n')
        with tempfile.TemporaryDirectory() as tmp:
            repo = write_repo(Path(tmp), root_manifest=single_crate())
            (repo / "src").mkdir()
            (repo / "src" / "main.rs").write_text(bad, encoding="utf-8")
            run = subprocess.run(["cargo", "clippy", "--all-targets", "--offline", "-q"],
                                 cwd=repo, capture_output=True, text=True, timeout=600)
        self.assertNotEqual(run.returncode, 0)
        for needle in ("eprintln!", "unwrap()", "disallowed method `std::env::var`"):
            self.assertIn(needle, run.stderr)


if __name__ == "__main__":
    unittest.main()
