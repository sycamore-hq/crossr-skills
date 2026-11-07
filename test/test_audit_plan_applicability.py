#!/usr/bin/env python3
"""audit-plan checks the System-design applicability declaration (SYC-17).

Shape only: every disclosed topic key exactly once, `applies` or
`n/a — <reason>`, before `## Phases`. Required keys are derived from the
disclosed cross-cutting RULES.md, so a new topic needs no script change.
Whether an `n/a` is true stays with the architecture gate.

Calculations are pure. The CLI cases write temp files; that is the action.
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
_spec = importlib.util.spec_from_loader(
    "audit_plan",
    importlib.machinery.SourceFileLoader("audit_plan", str(ROOT / "scripts" / "audit-plan")),
)
audit_plan = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("audit_plan", audit_plan)
assert _spec.loader is not None
_spec.loader.exec_module(audit_plan)

KEYS = frozenset({"DF", "DP", "DS", "DB", "DX", "DI"})

VALID = """\
- DF: applies
- DP: n/a — no repeated fixes sharing a failed gate
- DS: applies
- DB: applies
- DX: n/a — no shared mutable state
- DI: n/a — no externally observable state changes
"""

PLAN = """\
# Plan: T-1

## System-design applicability
{declarations}
## Phases
### Phase 1 of 1: land it

## Acceptance Criteria
- AC-01: it lands

## Claims
- C-01: mechanical · AC-01 · just test → 0

## Preserve
- none — no prior verified record

## Unresolved questions
- none
"""

SYSTEM_DESIGN_RULES = (ROOT / ".agents" / "skills" / "system-design" / "RULES.md").read_text()


def plan(declarations: str = VALID) -> str:
    return PLAN.format(declarations=declarations)


def fails_for(declarations: str, keys: frozenset[str] = KEYS) -> list[str]:
    return audit_plan.audit_text(plan(declarations), topic_keys=keys)


def without(key: str) -> str:
    return "".join(line + "\n" for line in VALID.splitlines() if not line.startswith(f"- {key}:"))


class Declarations(unittest.TestCase):
    def test_valid_plan_passes(self):
        self.assertEqual(fails_for(VALID), [])

    def test_reordered_topics_pass(self):
        reordered = "".join(line + "\n" for line in reversed(VALID.splitlines()))
        self.assertEqual(fails_for(reordered), [])

    def test_omitted_topic_is_rejected(self):
        self.assertEqual(fails_for(without("DX")), ["applicability DX is not declared"])

    def test_invalid_status_is_rejected(self):
        fails = fails_for(VALID.replace("- DF: applies", "- DF: maybe"))
        self.assertEqual(len(fails), 1)
        self.assertIn("applicability DF: status must be", fails[0])

    def test_bare_na_is_rejected(self):
        fails = fails_for(VALID.replace("- DX: n/a — no shared mutable state", "- DX: n/a"))
        self.assertEqual(fails, ["applicability DX: status must be `applies` or `n/a — <reason>`"])

    def test_hyphen_instead_of_em_dash_gets_a_hint(self):
        fails = fails_for(VALID.replace("- DX: n/a — no", "- DX: n/a - no"))
        self.assertEqual(fails, ["applicability DX: use an em dash: `n/a — <reason>`"])

    def test_declaration_inside_a_fence_does_not_count(self):
        fenced = without("DI") + "```\n- DI: n/a — only an example\n```\n"
        self.assertEqual(fails_for(fenced), ["applicability DI is not declared"])

    def test_whitespace_only_reason_is_rejected(self):
        fails = fails_for(VALID.replace("- DX: n/a — no shared mutable state", "- DX: n/a —   "))
        self.assertEqual(fails, ["applicability DX: `n/a` needs a reason"])

    def test_duplicate_key_is_rejected(self):
        fails = fails_for(VALID + "- DF: applies\n")
        self.assertEqual(fails, ["applicability DF declared more than once"])

    def test_unknown_key_is_rejected(self):
        fails = fails_for(VALID + "- ZZ: applies\n")
        self.assertEqual(fails, ["applicability ZZ is not a disclosed topic"])

    def test_malformed_line_is_rejected(self):
        fails = fails_for(VALID + "- df applies\n")
        self.assertEqual(fails, ["malformed applicability line: - df applies"])

    def test_missing_section_is_rejected(self):
        text = plan().replace("## System-design applicability\n" + VALID, "")
        fails = audit_plan.audit_text(text, topic_keys=KEYS)
        self.assertEqual(fails, ["missing section ## System-design applicability"])

    def test_section_after_phases_is_rejected(self):
        block = "## System-design applicability\n" + VALID
        text = plan().replace(block, "").replace("## Acceptance Criteria", block + "\n## Acceptance Criteria")
        fails = audit_plan.audit_text(text, topic_keys=KEYS)
        self.assertEqual(fails, ["## System-design applicability must come before ## Phases"])

    def test_no_disclosed_books_means_no_requirement(self):
        text = plan().replace("## System-design applicability\n" + VALID, "")
        self.assertEqual(audit_plan.audit_text(text), [])
        self.assertEqual(audit_plan.audit_text(text, topic_keys=frozenset()), [])


class DerivedKeys(unittest.TestCase):
    def test_system_design_rules_yield_six_topics_without_da(self):
        keys, errors = audit_plan.topic_keys_from_rules([SYSTEM_DESIGN_RULES])
        self.assertEqual((keys, errors), (KEYS, []))

    def test_synthetic_prefix_is_required_without_a_script_change(self):
        extended = SYSTEM_DESIGN_RULES + "\n## telemetry\n\nsystem-design/DT-01  Every Action emits a trace.\n"
        keys, errors = audit_plan.topic_keys_from_rules([extended])
        self.assertEqual(errors, [])
        self.assertEqual(keys, KEYS | {"DT"})
        self.assertEqual(fails_for(VALID, keys), ["applicability DT is not declared"])
        self.assertEqual(fails_for(VALID + "- DT: applies\n", keys), [])

    def test_malformed_rule_id_is_an_error(self):
        _, errors = audit_plan.topic_keys_from_rules(["## x\n\nsystem-design/df-1  lower case.\n"])
        self.assertEqual(errors, ["system-design: malformed rule id df-1"])

    def test_duplicate_rule_id_is_an_error(self):
        text = "## x\n\nbook/DQ-01  one.\n\nbook/DQ-01  again.\n"
        _, errors = audit_plan.topic_keys_from_rules([text])
        self.assertEqual(errors, ["book: duplicate rule id DQ-01"])

    def test_rules_with_no_topic_keys_are_an_error(self):
        da_only = "## applicability\n\nsystem-design/DA-01  Declare.\n"
        for text in ("", da_only):
            with self.subTest(text=text[:20]):
                keys, errors = audit_plan.topic_keys_from_rules([text])
                self.assertEqual((keys, errors), (frozenset(), ["disclosed rules #1 yield no topic keys"]))

    def test_same_book_disclosed_twice_is_an_error(self):
        _, errors = audit_plan.topic_keys_from_rules([SYSTEM_DESIGN_RULES, SYSTEM_DESIGN_RULES])
        self.assertEqual(errors, ["book system-design disclosed more than once"])

    def test_prefix_collision_across_books_is_an_error(self):
        other = "## clash\n\nother-book/DF-01  Same prefix, different idea.\n"
        _, errors = audit_plan.topic_keys_from_rules([SYSTEM_DESIGN_RULES, other])
        self.assertEqual(errors, ["prefix DF claimed by both system-design and other-book"])


class Cli(unittest.TestCase):
    def run_main(self, args: list[str]) -> int:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return audit_plan.main(["audit-plan", *args])

    def test_default_uses_this_catalogs_cross_cutting_books(self):
        with tempfile.TemporaryDirectory() as tmp:
            good, bad = Path(tmp) / "good.md", Path(tmp) / "bad.md"
            good.write_text(plan())
            bad.write_text(plan(without("DI")))
            self.assertEqual(self.run_main([str(good)]), 0)
            self.assertEqual(self.run_main([str(bad)]), 1)

    def test_rules_flag_replaces_the_disclosed_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            rules = Path(tmp) / "RULES.md"
            rules.write_text("## only\n\nmini/MQ-01  One topic.\n")
            path = Path(tmp) / "plan.md"
            path.write_text(plan("- MQ: applies\n"))
            self.assertEqual(self.run_main(["--rules", str(rules), str(path)]), 0)
            self.assertEqual(self.run_main([str(path)]), 1)

    def test_language_book_rules_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            path.write_text(plan())
            rust = ROOT / ".agents" / "skills" / "rust" / "RULES.md"
            self.assertEqual(self.run_main(["--rules", str(rust), str(path)]), 1)

    def test_empty_rules_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            rules = Path(tmp) / "RULES.md"
            rules.write_text("")
            path = Path(tmp) / "plan.md"
            path.write_text(plan())
            self.assertEqual(self.run_main(["--rules", str(rules), str(path)]), 1)

    def test_flag_where_a_rules_path_belongs_is_a_usage_error(self):
        self.assertEqual(self.run_main(["--rules", "--loc-threshold", "5", "plan.md"]), 2)

    def test_missing_rules_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            path.write_text(plan())
            self.assertEqual(self.run_main(["--rules", str(Path(tmp) / "nope.md"), str(path)]), 1)


if __name__ == "__main__":
    unittest.main()
