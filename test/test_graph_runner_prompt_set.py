#!/usr/bin/env python3
"""The graph-runner prompt set is a plan artifact and stays one.

work#14 (graph-runner): the prompt set is written in the plan-writer shape so
`scripts/audit-plan` gates it. This file keeps that true on every run of
`just harness-validate`: audit green (with and without the LOC threshold),
one brief per phase, every brief carries the guardrails paste and a VALIDATE
block, no template placeholders, and Rhai is only ever named as absent.

Calculations are pure. Loading the tree is the action.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT_SET = ROOT / "docs" / "plans" / "graph-runner-prompt-set.md"
LOC_THRESHOLD = 600

_spec = importlib.util.spec_from_loader(
    "audit_plan",
    importlib.machinery.SourceFileLoader(
        "audit_plan", str(ROOT / "scripts" / "audit-plan")
    ),
)
audit_plan = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules.setdefault("audit_plan", audit_plan)
_spec.loader.exec_module(audit_plan)

PHASE_RE = re.compile(r"^### Phase (\d+) of (\d+): (R\d+) — ", re.M)
BRIEF_RE = re.compile(r"^## Brief (R\d+) — ", re.M)
STATUS_ROW_RE = re.compile(r"^\| (R\d+) \| (\w+) \| ", re.M)
FENCE_RE = re.compile(r"^```\n(.*?)^```", re.M | re.S)
GUARDRAILS_PASTE = "[paste GUARDRAILS]"
GUARDRAILS_HEADING = "## Shared guardrails (paste into every brief verbatim)"
RHAI_RE = re.compile(r"rhai", re.I)
NEGATION_RE = re.compile(r"\b(no|not|never)\b|\brg\b", re.I)


def phases(text: str) -> list[tuple[int, int, str]]:
    return [(int(n), int(of), rid) for n, of, rid in PHASE_RE.findall(text)]


def brief_ids(text: str) -> list[str]:
    return BRIEF_RE.findall(text)


def status_rows(text: str) -> dict[str, str]:
    return dict(STATUS_ROW_RE.findall(text))


def brief_bodies(text: str) -> dict[str, str]:
    """Map brief id → the first fenced block after its heading."""
    out: dict[str, str] = {}
    for match in BRIEF_RE.finditer(text):
        fence = FENCE_RE.search(text, match.end())
        if fence:
            out[match.group(1)] = fence.group(1)
    return out


def rhai_lines_not_negated(text: str) -> list[str]:
    """Lines that name Rhai without a negation or a grep pattern on the line."""
    return [
        line
        for line in text.splitlines()
        if RHAI_RE.search(line) and not NEGATION_RE.search(line)
    ]


class Calculations(unittest.TestCase):
    def test_phase_heading_parses_number_total_and_id(self):
        self.assertEqual(
            phases("### Phase 2 of 4: R2 — loops: x\n"), [(2, 4, "R2")]
        )

    def test_brief_bodies_take_the_first_fence_after_each_heading(self):
        text = "## Brief R1 — a\n\n```\nbody one\n```\n## Brief R2 — b\n```\nbody two\n```\n"
        self.assertEqual(
            brief_bodies(text), {"R1": "body one\n", "R2": "body two\n"}
        )

    def test_rhai_named_as_absent_is_allowed(self):
        self.assertEqual(rhai_lines_not_negated("No Rhai. Never.\n"), [])

    def test_rhai_named_as_present_is_caught(self):
        self.assertEqual(
            rhai_lines_not_negated("embed rhai here\n"), ["embed rhai here"]
        )


class LiveTree(unittest.TestCase):
    text = PROMPT_SET.read_text()

    def test_plan_audit_passes(self):
        self.assertEqual(audit_plan.audit_text(self.text), [])

    def test_plan_audit_passes_under_loc_threshold(self):
        self.assertEqual(
            audit_plan.audit_text(self.text, loc_threshold=LOC_THRESHOLD), []
        )

    def test_phases_are_numbered_one_to_n(self):
        found = phases(self.text)
        self.assertTrue(found)
        total = found[0][1]
        self.assertEqual([n for n, _, _ in found], list(range(1, total + 1)))
        self.assertTrue(all(of == total for _, of, _ in found))

    def test_every_phase_has_a_brief_and_a_status_row(self):
        ids = [rid for _, _, rid in phases(self.text)]
        self.assertEqual(brief_ids(self.text), ids)
        self.assertEqual(list(status_rows(self.text)), ids)

    def test_every_brief_pastes_guardrails_and_validates(self):
        self.assertIn(GUARDRAILS_HEADING, self.text)
        bodies = brief_bodies(self.text)
        self.assertEqual(list(bodies), brief_ids(self.text))
        for rid, body in bodies.items():
            with self.subTest(brief=rid):
                self.assertIn("VALIDATE", body)
                if rid != "R4":
                    self.assertIn(GUARDRAILS_PASTE, body)

    def test_no_template_placeholders(self):
        self.assertNotIn("{{", self.text)

    def test_rhai_is_only_named_as_absent(self):
        self.assertEqual(rhai_lines_not_negated(self.text), [])

    def test_ends_with_unresolved_questions(self):
        sections = re.findall(r"^## (.+)$", self.text, re.M)
        self.assertEqual(sections[-1], "Unresolved questions")


if __name__ == "__main__":
    unittest.main()
