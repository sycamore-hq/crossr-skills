#!/usr/bin/env python3
"""PR 7a acceptance: the handoff packet and the batch verdict become
artifacts a script can reject.

Brief VALIDATE (work#12 / gan-layer-separation-plan §3.8 / §4 PR 7):
packet fields land in gan-verdict; per-item verdict is protocol;
audit-packet is the mechanical gate. Decisions 1, 2, 3, 5, 6, 7, 12.

Calculations are pure. Loading the tree is the action.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_loader(
    "audit_packet",
    importlib.machinery.SourceFileLoader(
        "audit_packet", str(ROOT / "scripts" / "audit-packet")
    ),
)
audit_packet = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules["audit_packet"] = audit_packet
_spec.loader.exec_module(audit_packet)

CARD_BUDGET = 2048
GAN_VERDICT = ROOT / ".agents" / "skills" / "gan-verdict" / "SKILL.md"
HANDOFF_REF = (
    ROOT / ".agents" / "skills" / "gan-verdict" / "references" / "handoff-packet.md"
)

DECISION_3 = "A bare BLESS over a set is not a verdict."

ITEMS_1_TO_7 = """\
1. Verdict tokens: exactly `BLESS` or `REJECT`. Silence, hedge, or "LGTM" is not approval.
2. One verdict per delegation.
3. The verdict names its gate: `<gate>: BLESS | REJECT` (e.g. `architecture: BLESS`).
4. `REJECT` must cite concrete blockers.
5. Report envelope — field schema (all fields optional; the conductor selects which apply and fills the values at delegation time):
   - phase id
   - "k of n"
   - AC ids claimed
   - findings shape (one-liners | prose)
   - max length
   - `file:line` citations
6. The envelope goes **last** in the delegation prompt, after persona + gate card — persona and ruleset are the stable cacheable prefix; the envelope varies per delegation, and splicing it above the ruleset destroys prefix stability.
7. Adding an envelope field means changing this file — never a conductor card.
"""

GOOD_PACKET = """\
# Packet: T-1
- k of n: 1 of 3
- gate: code-review
## Files
- src/parse.py
## Diff
- ref: HEAD~1
```diff
--- a/src/parse.py
+++ b/src/parse.py
@@ -1,2 +1,3 @@
 context
+added
```
## AC
- AC-01: parse rejects empty input
## Claims
- C-01
## Prior verdicts
- testing BLESS
## Envelope
- findings shape: one-liners
- max length: 40 lines
- file:line citations: yes
"""

GOOD_DIFF = """\
```diff
--- a/src/parse.py
+++ b/src/parse.py
@@ -1,2 +1,3 @@
 context
+added
```
"""

PROSE_DIFF = """\
```diff
this is why the change exists
```
"""


def good_packet() -> str:
    return GOOD_PACKET


def with_line(packet: str, old: str, new: str) -> str:
    return packet.replace(old, new, 1)


def drop_diff_fence(packet: str) -> str:
    return with_line(packet, GOOD_DIFF, "")


def extract_fenced_packet(text: str) -> str:
    """First fenced body that starts with `# Packet:`."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^(`{3,})", lines[i])
        if m:
            ticks = m.group(1)
            body: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith(ticks):
                body.append(lines[i])
                i += 1
            blob = "\n".join(body) + "\n"
            if blob.lstrip().startswith("# Packet:"):
                return blob
        i += 1
    raise AssertionError("no fenced packet example")


def fenced(body: str) -> str:
    return good_packet() + f"```\n{body}\n```\n"


class AuditCalculations(unittest.TestCase):
    def test_good_packet_passes(self):
        self.assertEqual(audit_packet.audit_brief(good_packet()), [])

    def test_missing_packet_heading(self):
        text = with_line(good_packet(), "# Packet: T-1\n", "")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("Packet:" in f for f in fails), fails)

    def test_missing_k_of_n(self):
        text = with_line(good_packet(), "- k of n: 1 of 3\n", "")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("k of n" in f for f in fails), fails)

    def test_malformed_k_of_n(self):
        text = with_line(good_packet(), "- k of n: 1 of 3", "- k of n: 3 of 1")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("k of n" in f for f in fails), fails)

    def test_k_of_n_zero_fails(self):
        text = with_line(good_packet(), "- k of n: 1 of 3", "- k of n: 0 of 3")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("missing/malformed" in f for f in fails), fails)

    def test_missing_gate(self):
        text = with_line(good_packet(), "- gate: code-review\n", "")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("gate" in f for f in fails), fails)

    def test_missing_required_section(self):
        text = with_line(good_packet(), "## Envelope\n", "")
        text = with_line(text, "- findings shape: one-liners\n", "")
        text = with_line(text, "- max length: 40 lines\n", "")
        text = with_line(text, "- file:line citations: yes\n", "")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(
            any("required section" in f and "Envelope" in f for f in fails), fails
        )

    def test_unknown_heading(self):
        text = with_line(
            good_packet(),
            "## Envelope\n",
            "## Previous phase\n- leftover essay\n## Envelope\n",
        )
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("unknown heading" in f for f in fails), fails)

    def test_extra_h1_fails(self):
        text = with_line(
            good_packet(),
            "## Files\n",
            "# Previous phase essay title\n## Files\n",
        )
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("unknown heading" in f for f in fails), fails)

    def test_files_empty(self):
        text = with_line(good_packet(), "- src/parse.py\n", "")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("Files empty" in f for f in fails), fails)

    def test_ac_empty(self):
        text = with_line(good_packet(), "- AC-01: parse rejects empty input\n", "")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("AC empty" in f for f in fails), fails)

    def test_ac_line_not_matching(self):
        text = with_line(
            good_packet(),
            "- AC-01: parse rejects empty input",
            "- not an AC line",
        )
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("AC line" in f for f in fails), fails)
        self.assertTrue(any(re.search(r"line \d+:", f) for f in fails), fails)

    def test_diff_neither_ref_nor_fence(self):
        text = drop_diff_fence(good_packet())
        text = with_line(text, "- ref: HEAD~1\n", "")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("Diff" in f and "neither" in f for f in fails), fails)

    def test_fence_outside_unified_diff(self):
        text = with_line(good_packet(), GOOD_DIFF, PROSE_DIFF)
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("unified-diff" in f for f in fails), fails)

    def test_prior_verdict_not_matching(self):
        text = with_line(
            good_packet(),
            "- testing BLESS",
            "- reviewer said yes",
        )
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("prior-verdict" in f for f in fails), fails)

    def test_never_sibling_skill_md_pasted(self):
        text = fenced("---\nname: code-review\ndescription: pasted\n---")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(
            any("SKILL.md" in f or "frontmatter" in f for f in fails), fails
        )

    def test_never_board_json_pasted(self):
        text = fenced('"tasks": [')
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("board" in f for f in fails), fails)

    def test_never_board_json_compact(self):
        text = fenced('{"tasks":[')
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("board" in f for f in fails), fails)

    def test_never_dashboard_html_pasted(self):
        text = fenced("<html><body>dash</body></html>")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("dashboard" in f or "HTML" in f for f in fails), fails)

    def test_never_dashboard_doctype(self):
        text = fenced("<!DOCTYPE html>")
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("dashboard" in f or "HTML" in f for f in fails), fails)

    def test_max_lines_exceeded(self):
        fails = audit_packet.audit_brief(good_packet(), max_lines=3)
        self.assertTrue(any("max-lines" in f for f in fails), fails)

    def test_envelope_not_name_value(self):
        text = with_line(
            good_packet(),
            "- findings shape: one-liners",
            "- findings shape one-liners",
        )
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("envelope" in f and "name" in f for f in fails), fails)

    def test_envelope_unknown_name(self):
        text = with_line(
            good_packet(),
            "- file:line citations: yes",
            "- vibe: good",
        )
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("envelope" in f and "vibe" in f for f in fails), fails)

    def test_envelope_citations_alias_rejected(self):
        text = with_line(
            good_packet(),
            "- file:line citations: yes",
            "- citations: file:line",
        )
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("envelope" in f and "citations" in f for f in fails), fails)

    def test_prose_failure_names_line(self):
        text = with_line(
            good_packet(),
            "## Files\n",
            "## Files\nthis is leftover essay prose\n",
        )
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("prose" in f and "line " in f for f in fails), fails)

    def test_prior_verdict_141_fails(self):
        reason = "x" * 141
        text = with_line(
            good_packet(),
            "- testing BLESS",
            f"- testing REJECT: {reason}",
        )
        fails = audit_packet.audit_brief(text)
        self.assertTrue(any("prior-verdict" in f for f in fails), fails)

    def test_prior_verdict_140_passes(self):
        reason = "x" * 140
        text = with_line(
            good_packet(),
            "- testing BLESS",
            f"- testing REJECT: {reason}",
        )
        self.assertEqual(audit_packet.audit_brief(text), [])

    def test_well_formed_fence_passes(self):
        text = with_line(good_packet(), "- ref: HEAD~1\n", "")
        self.assertEqual(audit_packet.audit_brief(text), [])

    def test_verdict_gate_one_line_passes(self):
        self.assertEqual(
            audit_packet.audit_verdict_gate("code-review: BLESS\n", "code-review"),
            [],
        )

    def test_verdict_gate_two_lines_fail(self):
        fails = audit_packet.audit_verdict_gate(
            "code-review: BLESS\ncode-review: BLESS\n",
            "code-review",
        )
        self.assertTrue(fails, fails)

    def test_verdict_gate_bare_bless_fails(self):
        fails = audit_packet.audit_verdict_gate("BLESS\n", "code-review")
        self.assertTrue(any("blanket" in f for f in fails), fails)

    def test_verdict_gate_zero_lines_fail(self):
        fails = audit_packet.audit_verdict_gate("testing: BLESS\n", "code-review")
        self.assertTrue(any("exactly one" in f for f in fails), fails)

    def test_verdict_gate_reject_without_blockers(self):
        fails = audit_packet.audit_verdict_gate(
            "code-review: REJECT\n", "code-review"
        )
        self.assertTrue(any("blockers" in f for f in fails), fails)

    def test_verdict_gate_blessed_fails(self):
        fails = audit_packet.audit_verdict_gate(
            "code-review: BLESSED\n", "code-review"
        )
        self.assertTrue(fails, fails)

    def test_verdict_gate_bless_trailing_text_fails(self):
        fails = audit_packet.audit_verdict_gate(
            "code-review: BLESS — with reservations, fix X first\n",
            "code-review",
        )
        self.assertTrue(fails, fails)

    def test_verdict_items_bless_and_reject_pass(self):
        self.assertEqual(
            audit_packet.audit_verdict_items(
                "BLESS a — ok\nREJECT b — why\n", ["a", "b"]
            ),
            [],
        )

    def test_verdict_items_silence(self):
        fails = audit_packet.audit_verdict_items("BLESS a — ok\n", ["a", "b"])
        self.assertTrue(any("silence" in f for f in fails), fails)

    def test_verdict_items_blanket(self):
        fails = audit_packet.audit_verdict_items("BLESS\n", ["a", "b"])
        self.assertTrue(any("blanket" in f for f in fails), fails)

    def test_verdict_items_duplicate(self):
        fails = audit_packet.audit_verdict_items(
            "BLESS a — ok\nBLESS a — again\nREJECT b — why\n",
            ["a", "b"],
        )
        self.assertTrue(any("a" in f and "2" in f for f in fails), fails)

    def test_verdict_items_stray(self):
        fails = audit_packet.audit_verdict_items(
            "BLESS a — ok\nREJECT b — why\nBLESS c — no\n",
            ["a", "b"],
        )
        self.assertTrue(any("stray" in f for f in fails), fails)

    def test_verdict_items_reject_without_emdash(self):
        fails = audit_packet.audit_verdict_items(
            "BLESS a — ok\nREJECT b\n", ["a", "b"]
        )
        self.assertTrue(any(" — " in f or "REJECT" in f for f in fails), fails)

    def test_verdict_items_reject_empty_blockers(self):
        fails = audit_packet.audit_verdict_items(
            "BLESS a — ok\nREJECT b — \n", ["a", "b"]
        )
        self.assertTrue(any("REJECT" in f for f in fails), fails)

    def test_verdict_items_blanket_all_with_note(self):
        fails = audit_packet.audit_verdict_items("BLESS all — fine\n", ["a", "b"])
        self.assertTrue(any("blanket" in f for f in fails), fails)
        self.assertFalse(any("stray" in f for f in fails), fails)

    def test_cli_brief_and_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = Path(tmp) / "packet.md"
            packet.write_text(good_packet())
            self.assertEqual(
                audit_packet.main(["audit-packet", "brief", str(packet)]),
                0,
            )
            verdict = Path(tmp) / "verdict.md"
            verdict.write_text("BLESS\n")
            self.assertEqual(
                audit_packet.main(
                    ["audit-packet", "verdict", "--items", "T-1,T-2", str(verdict)]
                ),
                1,
            )
        self.assertEqual(audit_packet.main(["audit-packet"]), 2)


class LiveTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = GAN_VERDICT.read_text() if GAN_VERDICT.is_file() else ""
        cls.handoff = HANDOFF_REF.read_text() if HANDOFF_REF.is_file() else ""

    def test_gan_verdict_byte_cap(self):
        n = len(self.card.encode())
        self.assertLessEqual(n, CARD_BUDGET, f"gan-verdict {n} B > {CARD_BUDGET}")

    def test_decision_3_sentence(self):
        self.assertIn(DECISION_3, self.card)

    def test_items_1_to_7_unchanged(self):
        self.assertIn(ITEMS_1_TO_7, self.card)

    def test_handoff_example_passes_brief(self):
        extracted = extract_fenced_packet(self.handoff)
        self.assertEqual(audit_packet.audit_brief(extracted), [])

    def test_fallback_path_starts_with_tmpdir(self):
        self.assertIn("${TMPDIR:-/tmp}/", self.handoff)
        self.assertTrue(
            any(
                line.strip().startswith("${TMPDIR:-/tmp}/")
                or "${TMPDIR:-/tmp}/" in line
                for line in self.handoff.splitlines()
            )
        )
        self.assertRegex(
            self.handoff,
            r"\$\{TMPDIR:-/tmp\}/",
        )


if __name__ == "__main__":
    unittest.main()
