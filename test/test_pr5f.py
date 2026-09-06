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

PIN = "v1-one-law-consumers"
DYING = (
    "rust-code-writer",
    "rust-errors",
    "ocaml-code-writer",
    "rust-code-reviewer",
    "rust-code-tester",
)

LOCKFILE_LOOPS = re.compile(r'(?m)^loops\s*=\s*"([^"]+)"')
AGENTS_PINS = re.compile(r'Consumer pins:.*?loops = "([^"]+)"')
AGENTS_TOPO = re.compile(r"are in the `([^`]+)` pin")
README_PINS = re.compile(r'Current pins:.*?loops = "([^"]+)"')
README_TOPO = re.compile(r"is in the `([^`]+)` pin")
ROW5_MD = re.compile(r"^\| 5 \| (.+) \|$", re.M)
ROW5_HTML = re.compile(
    r'<td class="mono">5</td><td>(.*?)</td>',
    re.S,
)


def lockfile_loops(text: str) -> str | None:
    m = LOCKFILE_LOOPS.search(text)
    return m.group(1) if m else None


def doc_pin_loci(agents: str, readme: str) -> dict[str, str | None]:
    """The three documentation copies of the lockfile loops pin."""
    agents_pins = AGENTS_PINS.search(agents)
    agents_topo = AGENTS_TOPO.search(agents)
    readme_pins = README_PINS.search(readme)
    readme_topo = README_TOPO.search(readme)
    return {
        "AGENTS.md pins": agents_pins.group(1) if agents_pins else None,
        "AGENTS.md topo": agents_topo.group(1) if agents_topo else None,
        "README.md pins": readme_pins.group(1) if readme_pins else None,
        "README.md topo": readme_topo.group(1) if readme_topo else None,
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
    def test_lockfile_reads_the_loops_assignment(self):
        self.assertEqual(lockfile_loops('loops  = "v1-cards"\n'), "v1-cards")
        self.assertIsNone(lockfile_loops('skills = "v1-gan-layers"\n'))

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
        self.assertEqual(set(loci.values()), {"v1-cards"})

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
        cls.progress = (ROOT / "progress.md").read_text()
        cls.features = json.loads((ROOT / "features.json").read_text())
        agent_dir = ROOT / ".opencode" / "agent"
        cls.agents_on_disk = {
            p.name: p.read_text() for p in agent_dir.glob("*.md")
        }

    def test_lockfile_loops_is_the_one_law_consumers_tag(self):
        self.assertEqual(lockfile_loops(self.lockfile), PIN)

    def test_three_doc_loci_match_the_lockfile(self):
        loci = doc_pin_loci(self.agents, self.readme)
        stale = {k: v for k, v in loci.items() if v != PIN}
        self.assertEqual(stale, {}, f"pin loci still off {PIN}: {stale}")

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
        gaps = twin_gaps(
            self.plan,
            self.plan_html,
            (
                PIN,
                "v1-one-law",
                "requires.book",
                "metadata.book",
                "zero-line",
                "drift-detectable",
            ),
        )
        self.assertEqual(gaps, [])

    def test_features_records_pr5f_completed(self):
        phase = self.features["gan-layer-separation"]
        missing = missing_stack_rows(completed_ids(phase))
        self.assertEqual(missing, [], f"gan-layer-separation missing {missing}")

    def test_progress_records_5f_completed(self):
        self.assertRegex(
            self.progress,
            r"(?m)^### gan-layer-separation — PR 5f \(COMPLETED\)",
        )


if __name__ == "__main__":
    unittest.main()
