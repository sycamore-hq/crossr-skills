#!/usr/bin/env python3
"""PR 5f acceptance: one loops pin, dead names gone, plan twins close the stack.

Brief VALIDATE: four pin loci read v1-one-law-consumers; .opencode/agent/
dying-name grep is zero; just harness-validate (this file is in that path);
plan twins agree; §7 row 5 says drift-detectable; tracker rows exist.

Calculations are pure. Loading the tree is the action.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DYING = (
    "rust-code-writer",
    "rust-errors",
    "ocaml-code-writer",
    "rust-code-reviewer",
    "rust-code-tester",
)

LOCKFILE_PIN = r'(?m)^{key}\s*=\s*"([^"]+)"'

# Loops pins we have deliberately moved off. Append when you retire one; never
# remove. Asserting the *current* pin by literal made every legitimate bump edit
# a test, which is the wrong direction to spend attention: moving forward is the
# normal case, and regressing onto a superseded pin is the failure worth catching.
RETIRED_LOOPS_PINS = {
    "v1-cards",
    "v1-one-law-consumers",
    "v1-packets-consumers",
}
AGENTS_PINS = re.compile(r'Consumer pins:.*?loops = "([^"]+)"')
AGENTS_SKILLS = re.compile(r'Consumer pins:.*?skills = "([^"]+)"')
AGENTS_TOPO = re.compile(r"are in the `([^`]+)` pin")
README_PINS = re.compile(r'Current pins:.*?loops = "([^"]+)"')
README_SKILLS = re.compile(r'Current pins:.*?skills = "([^"]+)"')
README_TOPO = re.compile(r"is in the `([^`]+)` pin")
ROW5_MD = re.compile(r"^\| 5 \| (.+) \|$", re.M)
ROW5_HTML = re.compile(
    r'<td class="mono">5</td><td>(.*?)</td>',
    re.S,
)


def lockfile_pin(text: str, key: str) -> str | None:
    """The tag a lockfile assigns to `key` (skills or loops)."""
    m = re.search(LOCKFILE_PIN.format(key=key), text)
    return m.group(1) if m else None


def lockfile_loops(text: str) -> str | None:
    return lockfile_pin(text, "loops")


def doc_pin_loci(agents: str, readme: str) -> dict[str, tuple[str, str | None]]:
    """Every documentation copy of a lockfile pin, tagged with the key it copies.

    The topo loci say which pin holds `graphs/`, which is a loops fact by
    meaning — they stay keyed to loops even though they sit beside a skills
    sentence.
    """
    found = {
        "AGENTS.md skills": ("skills", AGENTS_SKILLS.search(agents)),
        "AGENTS.md pins": ("loops", AGENTS_PINS.search(agents)),
        "AGENTS.md topo": ("loops", AGENTS_TOPO.search(agents)),
        "README.md skills": ("skills", README_SKILLS.search(readme)),
        "README.md pins": ("loops", README_PINS.search(readme)),
        "README.md topo": ("loops", README_TOPO.search(readme)),
    }
    return {
        name: (key, match.group(1) if match else None)
        for name, (key, match) in found.items()
    }


def dying_hits(text: str, names: tuple[str, ...] = DYING) -> list[str]:
    return [name for name in names if name in text]


def dying_hits_in_dir(files: dict[str, str]) -> list[str]:
    """filename:name for every dying-skill hit in generated agent files."""
    hits = []
    for filename, text in sorted(files.items()):
        for name in dying_hits(text):
            hits.append(f"{filename}:{name}")
    return hits


def row5_body(text: str, html: bool = False) -> str:
    pat = ROW5_HTML if html else ROW5_MD
    m = pat.search(text)
    return m.group(1) if m else ""


def says_drift_detectable(row: str) -> bool:
    return "drift-detectable" in row


def pr5_landed_phrase(text: str) -> bool:
    return bool(re.search(r"PR 5\s+landed", text, re.I))


def twin_gaps(md: str, html: str, phrases: tuple[str, ...]) -> list[str]:
    """Phrases that are missing from one twin or the other."""
    gaps = []
    for phrase in phrases:
        in_md = phrase in md
        in_html = phrase in html
        if in_md and in_html:
            continue
        if not in_md and not in_html:
            gaps.append(f"both missing {phrase!r}")
        elif not in_md:
            gaps.append(f"md missing {phrase!r}")
        else:
            gaps.append(f"html missing {phrase!r}")
    return gaps


def completed_ids(phase: dict) -> set[str]:
    return {
        c["id"]
        for c in phase.get("commits") or []
        if c.get("status") == "completed" and c.get("id")
    }


def missing_stack_rows(ids: set[str], needed: tuple[str, ...] = ("pr5f",)) -> list[str]:
    return [i for i in needed if i not in ids]


class Calculations(unittest.TestCase):
    def test_lockfile_reads_either_assignment(self):
        text = 'skills = "v1-board"\nloops  = "v1-cards"\n'
        self.assertEqual(lockfile_pin(text, "loops"), "v1-cards")
        self.assertEqual(lockfile_pin(text, "skills"), "v1-board")
        self.assertIsNone(lockfile_pin('skills = "v1-board"\n', "loops"))
        self.assertEqual(lockfile_loops(text), "v1-cards")

    def test_doc_loci_are_independent_sentences(self):
        agents = (
            'Consumer pins: `skills = "v1-gan-layers"`, `loops = "v1-cards"`. '
            "Graphs live in `crossr-loops/graphs/` and are in the `v1-cards` pin."
        )
        readme = (
            'Current pins: `skills = "v1-gan-layers"`, `loops = "v1-cards"`.\n'
            "Topology lives in graphs/ and is in the `v1-cards` pin."
        )
        loci = doc_pin_loci(agents, readme)
        self.assertEqual(
            loci,
            {
                "AGENTS.md skills": ("skills", "v1-gan-layers"),
                "AGENTS.md pins": ("loops", "v1-cards"),
                "AGENTS.md topo": ("loops", "v1-cards"),
                "README.md skills": ("skills", "v1-gan-layers"),
                "README.md pins": ("loops", "v1-cards"),
                "README.md topo": ("loops", "v1-cards"),
            },
        )

    def test_dying_hits_are_exact_names(self):
        self.assertEqual(dying_hits("Activate rust-code-reviewer."), ["rust-code-reviewer"])
        self.assertEqual(dying_hits("code-review and testing"), [])

    def test_dying_hits_in_dir_names_the_file(self):
        files = {
            "reviewer-agent.md": "requires rust-code-reviewer",
            "axel.md": "clean",
        }
        self.assertEqual(dying_hits_in_dir(files), ["reviewer-agent.md:rust-code-reviewer"])

    def test_row5_drift_detectable_is_a_substring(self):
        self.assertTrue(says_drift_detectable("Rules projections drift-detectable, gated"))
        self.assertFalse(says_drift_detectable("Rules projections generated, not hand-copied"))

    def test_pr5_landed_needs_both_words(self):
        self.assertTrue(pr5_landed_phrase("PR 5 landed as the seven-PR stack"))
        self.assertFalse(pr5_landed_phrase("PR 5 — One ruleset, progressively disclosed"))
        self.assertFalse(pr5_landed_phrase("PR 4 landed\n\n### PR 5 — later a word landed"))

    def test_twin_gaps_report_which_side(self):
        self.assertEqual(twin_gaps("alpha beta", "alpha", ("alpha", "beta")), ["html missing 'beta'"])
        self.assertEqual(twin_gaps("alpha", "alpha", ("alpha",)), [])

    def test_missing_stack_rows_are_the_absent_ids(self):
        self.assertEqual(missing_stack_rows({"pr4b", "pr5a"}), ["pr5f"])
        self.assertEqual(missing_stack_rows({"pr5f"}), [])


class LiveTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lockfile = (ROOT / "lockfile.toml").read_text()
        cls.agents = (ROOT / "AGENTS.md").read_text()
        cls.readme = (ROOT / "README.md").read_text()
        cls.plan = (ROOT / "docs" / "plans" / "gan-layer-separation-plan.md").read_text()
        cls.plan_html = (ROOT / "docs" / "plans" / "gan-layer-separation-plan.html").read_text()
        agent_dir = ROOT / ".opencode" / "agent"
        cls.agents_on_disk = {
            p.name: p.read_text() for p in agent_dir.glob("*.md")
        }
        cls.pin = lockfile_loops(cls.lockfile)

    def test_lockfile_loops_is_present(self):
        self.assertTrue(self.pin, "lockfile.toml has no loops assignment")

    def test_lockfile_loops_is_not_a_retired_pin(self):
        self.assertNotIn(
            self.pin,
            RETIRED_LOOPS_PINS,
            f"loops pin {self.pin!r} was retired; a bump must go forward",
        )

    def test_doc_loci_match_the_lockfile(self):
        pins = {
            "skills": lockfile_pin(self.lockfile, "skills"),
            "loops": self.pin,
        }
        loci = doc_pin_loci(self.agents, self.readme)
        stale = {
            name: f"{value!r} != {key} pin {pins[key]!r}"
            for name, (key, value) in loci.items()
            if value != pins[key]
        }
        self.assertEqual(stale, {}, f"doc pin loci are stale: {stale}")

    def test_opencode_agents_name_none_of_the_dying_skills(self):
        hits = dying_hits_in_dir(self.agents_on_disk)
        self.assertEqual(hits, [], f"dying names still in .opencode/agent/: {hits}")

    def test_plan_twins_mark_pr5_landed(self):
        self.assertTrue(pr5_landed_phrase(self.plan), "plan md does not say PR 5 landed")
        self.assertTrue(pr5_landed_phrase(self.plan_html), "plan html does not say PR 5 landed")

    def test_section_7_row_5_says_drift_detectable_in_both_twins(self):
        md_row = row5_body(self.plan, html=False)
        html_row = row5_body(self.plan_html, html=True)
        self.assertTrue(md_row, "plan md has no §7 row 5")
        self.assertTrue(html_row, "plan html has no §7 row 5")
        self.assertTrue(says_drift_detectable(md_row), md_row)
        self.assertTrue(says_drift_detectable(html_row), html_row)

    def test_plan_twins_share_the_close_facts(self):
        # The facts are this campaign's, not today's. Reading the live pin here
        # made the guard demand that an archived plan name a tag cut after it
        # closed — which would be falsifying the record to satisfy a test.
        gaps = twin_gaps(
            self.plan,
            self.plan_html,
            (
                "v1-packets-consumers",
                "507c509",
                "requires.book",
                "metadata.book",
                "zero-line",
                "drift-detectable",
            ),
        )
        self.assertEqual(gaps, [])

if __name__ == "__main__":
    unittest.main()
