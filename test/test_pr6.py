#!/usr/bin/env python3
"""PR 6 acceptance: plan-writer exists; audit is a script; code-writer is
absent from the plan-time card; preserve-vs-grow is rule 5.

Brief VALIDATE (work#11 / gan-layer-separation-plan §4 PR 6 / §7 row 6):
plan-writer exists; code-writer is absent from the plan-time window;
bidirectional AC↔claim coverage passes by script; judgment quota is a
gate; evidence-packet gaps and preservation become claims.

Calculations are pure. Loading the tree is the action.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_loader(
    "audit_plan",
    importlib.machinery.SourceFileLoader(
        "audit_plan", str(ROOT / "scripts" / "audit-plan")
    ),
)
audit_plan = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules["audit_plan"] = audit_plan
_spec.loader.exec_module(audit_plan)

CARD_BUDGET = 2560
GATE_BUDGET = 2048
PLAN_WRITER = ROOT / ".agents" / "skills" / "plan-writer" / "SKILL.md"

GOOD_PLAN = """\
# Plan: T-9

## Phases
### Phase 1 of 1: land the parser

## Acceptance Criteria
- AC-01: parse rejects empty input
- AC-02: parse accepts a one-field record

## Claims
- C-01: mechanical · AC-01 · rg 'unwrap' src/ → 0
- C-02: observable · AC-01 · ParseError has From<io::Error>
- C-03: observable · AC-02 · Record::parse is pub
- C-04: judgment · AC-02 · retry policy is comprehensible

## Preserve
- none — no prior verified record

## Unresolved questions
- none
"""

PACKET_PLAN = """\
# Plan: T-10

## Phases
### Phase 1 of 1: grow the parser

## Acceptance Criteria
- AC-01: empty input still rejected
- AC-02: two-field records parse

## Claims
- C-01: mechanical · AC-01 · rg 'unwrap' src/ → 0
- C-02: observable · AC-01 · empty-input test remains
- C-03: observable · AC-02 · Record has field two
- C-04: mechanical · AC-01 · just test → 0

## Preserve
- PV-01 → C-02: empty-input rejection survives

## Evidence packet
- path: docs/evidence/T-9.md
- gap G-01 → C-03
- preserve PV-01 → C-02

## Unresolved questions
- none
"""


def good_plan() -> str:
    return GOOD_PLAN


def packet_plan() -> str:
    return PACKET_PLAN


def with_line(plan: str, old: str, new: str) -> str:
    return plan.replace(old, new, 1)


def extra_claim(plan: str, line: str) -> str:
    return plan.replace(
        "## Preserve",
        f"{line}\n\n## Preserve",
        1,
    )


class AuditCalculations(unittest.TestCase):
    def test_good_plan_passes(self):
        self.assertEqual(audit_plan.audit_text(good_plan()), [])

    def test_packet_plan_passes(self):
        self.assertEqual(audit_plan.audit_text(packet_plan()), [])

    def test_uncovered_ac_fails(self):
        text = with_line(
            good_plan(),
            "- AC-02: parse accepts a one-field record",
            "- AC-02: parse accepts a one-field record\n- AC-03: writes a file",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("AC-03" in f for f in fails), fails)

    def test_orphan_claim_fails(self):
        text = extra_claim(
            good_plan(),
            "- C-05: observable · AC-99 · silently added work",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("C-05" in f and "orphan" in f for f in fails), fails)

    def test_judgment_quota_is_thirty_percent(self):
        # 2 judgment / 4 active = 50%
        text = with_line(
            good_plan(),
            "- C-03: observable · AC-02 · Record::parse is pub",
            "- C-03: judgment · AC-02 · names are nice",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("judgment quota" in f for f in fails), fails)

    def test_one_judgment_in_four_is_under_quota(self):
        ratio = audit_plan.judgment_ratio(
            audit_plan.active_claims(audit_plan.parse_plan(good_plan()))
        )
        self.assertLessEqual(ratio, audit_plan.JUDGMENT_QUOTA)

    def test_duplicate_claim_id_fails(self):
        text = extra_claim(
            good_plan(),
            "- C-01: mechanical · AC-01 · rg 'todo' src/ → 0",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("duplicate" in f and "C-01" in f for f in fails), fails)

    def test_superseded_and_active_cannot_share_an_id(self):
        text = extra_claim(
            good_plan(),
            "- C-01 [superseded]: mechanical · AC-01 · old check → 0",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("duplicate" in f for f in fails), fails)

    def test_superseded_claim_is_excluded_from_active(self):
        text = with_line(
            good_plan(),
            "- C-03: observable · AC-02 · Record::parse is pub",
            "- C-03 [superseded]: judgment · AC-02 · old",
        )
        text = extra_claim(
            text,
            "- C-05: observable · AC-02 · Record::parse is pub",
        )
        self.assertEqual(audit_plan.audit_text(text), [])
        active = {
            c.cid
            for c in audit_plan.active_claims(audit_plan.parse_plan(text))
        }
        self.assertNotIn("C-03", active)
        self.assertIn("C-05", active)

    def test_mechanical_claim_needs_an_arrow(self):
        text = with_line(
            good_plan(),
            "- C-01: mechanical · AC-01 · rg 'unwrap' src/ → 0",
            "- C-01: mechanical · AC-01 · please grep for unwrap",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("C-01" in f and "→" in f for f in fails), fails)

    def test_empty_preserve_fails(self):
        text = with_line(
            good_plan(),
            "- none — no prior verified record",
            "",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("Preserve is empty" in f for f in fails), fails)

    def test_none_plus_items_fails(self):
        text = with_line(
            good_plan(),
            "- none — no prior verified record",
            "- none — no prior verified record\n- PV-01 → C-02: leftover",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("declares none" in f for f in fails), fails)

    def test_gap_map_fails_without_a_path_line(self):
        text = with_line(
            packet_plan(),
            "- path: docs/evidence/T-9.md\n",
            "",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("G-01" in f or "no path" in f for f in fails), fails)

    def test_preserve_packet_mismatch_is_one_line(self):
        text = with_line(
            packet_plan(),
            "- preserve PV-01 → C-02",
            "- preserve PV-01 → C-99",
        )
        fails = audit_plan.audit_text(text)
        mismatch = [f for f in fails if "PV-01" in f]
        self.assertEqual(len(mismatch), 1, fails)
        self.assertTrue(any("packet maps to C-99" in f for f in mismatch), fails)

    def test_preserve_none_plus_packet_map_is_one_line(self):
        text = with_line(
            packet_plan(),
            "- PV-01 → C-02: empty-input rejection survives",
            "- none — no prior verified record",
        )
        fails = audit_plan.audit_text(text)
        pv = [f for f in fails if "PV-01" in f or "packet maps preserve" in f]
        self.assertEqual(len(pv), 1, fails)
        self.assertTrue(
            any("declares none but packet maps" in f for f in fails), fails
        )

    def test_unmapped_preserve_id_reports_once(self):
        text = with_line(
            packet_plan(),
            "- PV-01 → C-02: empty-input rejection survives",
            "- PV-01 → C-99: empty-input rejection survives",
        )
        text = with_line(text, "- preserve PV-01 → C-02", "- preserve PV-01 → C-99")
        fails = audit_plan.audit_text(text)
        pv = [f for f in fails if "PV-01" in f]
        self.assertEqual(len(pv), 1, fails)

    def test_fenced_claims_block_is_ignored(self):
        text = with_line(
            good_plan(),
            "## Unresolved questions\n- none\n",
            "## Unresolved questions\n- none\n\n```\n## Claims\n"
            "- C-99: judgment · AC-01 · quoted\n```\n",
        )
        self.assertEqual(audit_plan.audit_text(text), [])

    def test_phase_heading_outside_phases_does_not_count(self):
        text = with_line(good_plan(), "### Phase 1 of 1: land the parser\n", "")
        text = with_line(
            text,
            "## Unresolved questions\n- none\n",
            "## Unresolved questions\n### Phase 1 of 1: not a phase\n- none\n",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("Phase N" in f for f in fails), fails)

    def test_packet_gap_must_map_to_an_active_claim(self):
        text = with_line(
            packet_plan(),
            "- gap G-01 → C-03",
            "- gap G-01 → C-99",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("G-01" in f for f in fails), fails)

    def test_packet_without_maps_fails(self):
        text = with_line(
            packet_plan(),
            "- gap G-01 → C-03\n- preserve PV-01 → C-02",
            "",
        )
        # still has ## Preserve item, so the "no maps" check is the empty
        # evidence mappings — drop the preserve section item too
        text = with_line(
            text,
            "- PV-01 → C-02: empty-input rejection survives",
            "- none — no prior verified record",
        )
        fails = audit_plan.audit_text(text)
        self.assertTrue(any("evidence packet" in f for f in fails), fails)

    def test_missing_heading_fails(self):
        fails = audit_plan.audit_text("## Claims\n")
        self.assertTrue(any("Plan:" in f for f in fails), fails)

    def test_parse_ac_list_splits_on_comma(self):
        self.assertEqual(
            audit_plan.parse_ac_list("AC-01, AC-02"),
            ("AC-01", "AC-02"),
        )


class LiveTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = PLAN_WRITER.read_text() if PLAN_WRITER.is_file() else ""
        cls.public = json.loads(
            (ROOT / "docs" / "public-skills.json").read_text()
        )
        cls.readme = (ROOT / "README.md").read_text()
        cls.plan = (ROOT / "docs" / "plans" / "gan-layer-separation-plan.md").read_text()
        cls.plan_html = (
            ROOT / "docs" / "plans" / "gan-layer-separation-plan.html"
        ).read_text()
        cls.features = json.loads((ROOT / "features.json").read_text())
        cls.progress = (ROOT / "progress.md").read_text()
        cls.architecture = (
            ROOT / ".agents" / "skills" / "architecture" / "SKILL.md"
        ).read_text()
        cls.review = (
            ROOT / ".agents" / "skills" / "code-review" / "SKILL.md"
        ).read_text()
        cls.testing = (
            ROOT / ".agents" / "skills" / "testing" / "SKILL.md"
        ).read_text()
        cls.review_ref = (
            ROOT / ".agents" / "skills" / "code-review" / "references" / "verification.md"
        ).read_text()
        cls.testing_ref = (
            ROOT / ".agents" / "skills" / "testing" / "references" / "verification.md"
        ).read_text()

    def test_plan_writer_skill_exists(self):
        self.assertTrue(PLAN_WRITER.is_file(), "missing plan-writer/SKILL.md")

    def test_card_is_about_two_kb(self):
        n = len(self.card.encode())
        self.assertGreater(n, 800, f"plan-writer card too thin: {n} B")
        self.assertLessEqual(n, CARD_BUDGET, f"plan-writer card {n} B > {CARD_BUDGET}")

    def test_code_writer_is_not_a_plan_time_load(self):
        self.assertRegex(
            self.card,
            r"(?i)do not load [`']?code-writer",
        )
        for m in re.finditer(r"(?im)^.*code-writer.*$", self.card):
            line = m.group(0).lower()
            self.assertTrue(
                "do not load" in line
                or "does not load" in line
                or "never loads" in line
                or "absent" in line,
                line,
            )

    def test_card_names_the_taxonomy(self):
        for word in ("mechanical", "observable", "judgment"):
            self.assertIn(word, self.card, f"taxonomy missing {word}")

    def test_card_names_bidirectional_coverage(self):
        self.assertRegex(self.card, r"(?i)bidirectional")

    def test_card_names_append_only_ids(self):
        self.assertRegex(self.card, r"(?i)append-only")

    def test_card_names_preserve_vs_grow(self):
        self.assertTrue(
            "must survive" in self.card or "Preserve-vs-grow" in self.card,
            "rule 5 (preserve-vs-grow) missing from the card",
        )

    def test_card_names_the_artifact_path(self):
        self.assertIn("docs/plans/pbi/", self.card)

    def test_card_is_a_skill_not_a_persona(self):
        self.assertNotRegex(self.card, r"(?i)agent personality")
        self.assertNotRegex(self.card, r"(?im)^## Output Format")
        self.assertIn("One-Sentence Mandate", self.card)

    def test_card_consumes_an_evidence_packet(self):
        self.assertRegex(self.card, r"(?i)evidence packet")

    def test_allowlist_includes_plan_writer(self):
        names = [s["name"] for s in self.public["skills"]]
        self.assertIn("plan-writer", names)

    def test_readme_tables_plan_writer(self):
        self.assertRegex(self.readme, r"(?m)^\|\s*`plan-writer`")

    def test_audit_script_is_executable_law(self):
        script = ROOT / "scripts" / "audit-plan"
        self.assertTrue(script.is_file())
        self.assertIn("JUDGMENT_QUOTA", script.read_text())

    def test_architecture_is_the_plan_time_gate(self):
        self.assertRegex(self.architecture, r"(?i)plan time")
        self.assertRegex(self.architecture, r"(?i)underspecif")
        self.assertNotIn(
            "You are the last gate before any code lands.",
            self.architecture,
        )
        self.assertNotIn("final architecture gate", self.architecture)
        self.assertNotIn("All code generation", self.architecture)

    def test_reviewer_is_conformance_plus_capped_risk(self):
        self.assertRegex(self.review, r"(?i)conformance")
        self.assertRegex(self.review, r"(?i)unanticipated")
        self.assertIn("three", self.review.lower())
        self.assertRegex(self.review, r"(?i)this lane only|cap applies to this lane")
        self.assertRegex(self.review_ref, r"(?i)C-nn|claim id")
        self.assertRegex(self.review_ref, r"(?i)unanticipated")
        self.assertRegex(self.review_ref, r"(?i)separat")

    def test_tester_is_ac_coverage_and_zero_regressions(self):
        self.assertRegex(self.testing, r"(?i)acceptance crit|AC coverage")
        self.assertRegex(self.testing, r"(?i)regression")
        self.assertRegex(self.testing_ref, r"(?i)AC")
        self.assertRegex(self.testing_ref, r"(?i)regression|previously passing")

    def test_gate_cards_stay_at_or_under_two_kb(self):
        for name in ("code-review", "testing"):
            path = ROOT / ".agents" / "skills" / name / "SKILL.md"
            n = len(path.read_bytes())
            self.assertLessEqual(n, GATE_BUDGET, f"{name} {n} B > {GATE_BUDGET}")

    def test_plan_twins_carry_rule_five(self):
        self.assertRegex(self.plan, r"(?i)must survive")
        self.assertRegex(self.plan_html, r"(?i)must survive")

    def test_features_records_pr6a(self):
        phase = self.features["gan-layer-separation"]
        ids = {
            c["id"]
            for c in phase.get("commits") or []
            if c.get("status") == "completed"
        }
        self.assertIn("pr6a", ids)

    def test_progress_records_pr6a(self):
        self.assertRegex(
            self.progress,
            r"(?m)^### gan-layer-separation — PR 6a \(COMPLETED\)",
        )


if __name__ == "__main__":
    unittest.main()
