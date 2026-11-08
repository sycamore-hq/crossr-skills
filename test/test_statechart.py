#!/usr/bin/env python3
"""statechart: checker, page builder, and shipped examples.

The checker is the mechanical half of the skill's Verification section. These
tests pin what it accepts and rejects, and that the shipped template sample
and the fixture page stay valid and in sync with the template.

Calculations are pure (strings in, findings out). Temp files are the action.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".agents" / "skills" / "statechart"
FIXTURES = ROOT / "test" / "fixtures" / "statechart"
sys.path.insert(0, str(SKILL / "scripts"))

import build_page  # noqa: E402
import check_statechart as cs  # noqa: E402

TEMPLATE = (SKILL / "assets" / "explainer-template.html").read_text(encoding="utf-8")
SAMPLE_SCXML = cs.SCXML_BLOCK.search(TEMPLATE).group(2).strip()
SAMPLE_INFO = json.loads(cs.JSON_BLOCK.search(TEMPLATE).group(2))

MINI = """<?xml version="1.0"?>
<scxml xmlns="http://www.w3.org/2005/07/scxml" xmlns:crossr="https://sycamore-hq.github.io/crossr/scxml/1"
       version="1.0" datamodel="ecmascript" name="mini" initial="a">
  <datamodel><data id="ok" expr="false"/></datamodel>
  <state id="a" crossr:source="x.rs:1">
    <transition crossr:id="t-go" event="go" cond="ok" target="b" crossr:source="x.rs:2"/>
  </state>
  <final id="b" crossr:source="x.rs:3"/>
</scxml>"""


def errors(findings):
    return [f.message for f in findings if f.level == "error"]


def warnings(findings):
    return [f.message for f in findings if f.level == "warning"]


def scxml(text):
    return cs.check_scxml_text(text, "m.scxml")


class ShippedExamples(unittest.TestCase):
    def test_template_sample_passes_with_no_findings(self):
        model, findings = scxml(SAMPLE_SCXML)
        findings += cs.check_page(TEMPLATE, TEMPLATE, SAMPLE_SCXML, model, "t.html")
        self.assertEqual([str(f) for f in findings], [])

    def test_fixture_passes_with_no_findings(self):
        text = (FIXTURES / "media-player.scxml").read_text(encoding="utf-8")
        page = (FIXTURES / "media-player.html").read_text(encoding="utf-8")
        model, findings = scxml(text)
        findings += cs.check_page(page, TEMPLATE, text, model, "mp.html")
        self.assertEqual([str(f) for f in findings], [])

    def test_fixture_page_is_the_build_of_its_inputs(self):
        built = build_page.fill(
            TEMPLATE,
            (FIXTURES / "media-player.scxml").read_text(encoding="utf-8"),
            json.loads((FIXTURES / "media-player.json").read_text(encoding="utf-8")),
        )
        self.assertEqual(built, (FIXTURES / "media-player.html").read_text(encoding="utf-8"),
                         "rebuild with scripts/build_page.py")

    def test_skill_links_resolve(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for target in re.findall(r"\]\(((?:references|assets)/[^)#]+)", text):
            with self.subTest(link=target):
                self.assertTrue((SKILL / target).is_file())


class ScxmlProfile(unittest.TestCase):
    def test_minimal_chart_is_clean(self):
        _, findings = scxml(MINI)
        self.assertEqual([str(f) for f in findings], [])

    def test_rejects_non_scxml_root(self):
        self.assertIn("root element", errors(scxml("<foo/>")[1])[0])

    def test_rejects_bad_xml(self):
        self.assertIn("does not parse", errors(scxml("<scxml")[1])[0])

    def test_requires_provenance_on_states_and_transitions(self):
        _, f = scxml(MINI.replace(' crossr:source="x.rs:1"', "").replace(' crossr:source="x.rs:2"', ""))
        self.assertEqual(sum("missing crossr:source" in m for m in errors(f)), 2)

    def test_rejects_malformed_source_ref(self):
        _, f = scxml(MINI.replace('crossr:source="x.rs:1"', 'crossr:source="x.rs"'))
        self.assertTrue(any("path:line" in m for m in errors(f)))

    def test_requires_unique_transition_ids(self):
        dup = MINI.replace('<final id="b"', '<state id="c" crossr:source="x.rs:9"><transition crossr:id="t-go" event="go" target="b" crossr:source="x.rs:9"/></state><final id="b"')
        self.assertTrue(any("duplicate crossr:id" in m for m in errors(scxml(dup)[1])))

    def test_rejects_unknown_target(self):
        self.assertTrue(any("names no state" in m for m in errors(scxml(MINI.replace('target="b"', 'target="nope"'))[1])))

    def test_rejects_initial_outside_the_state(self):
        bad = MINI.replace('<state id="a" crossr:source="x.rs:1">', '<state id="a" initial="b" crossr:source="x.rs:1">')
        self.assertTrue(any("not a descendant" in m for m in errors(scxml(bad)[1])))

    def test_condition_grammar(self):
        for cond, ok in [("ok", True), ("!ok && In('a')", True), ("(ok || false)", True),
                         ("ok == 1", False), ("ok &&", False), ("x.y()", False)]:
            with self.subTest(cond=cond):
                errs = errors(scxml(MINI.replace('cond="ok"', f'cond="{escape(cond)}"'))[1])
                self.assertEqual(not errs, ok, errs)

    def test_condition_names_must_be_declared(self):
        self.assertTrue(any("undeclared data" in m for m in errors(scxml(MINI.replace('cond="ok"', 'cond="nope"'))[1])))

    def test_data_conditions_need_ecmascript(self):
        self.assertTrue(any("ecmascript" in m for m in errors(scxml(MINI.replace('datamodel="ecmascript"', 'datamodel="null"'))[1])))

    def test_warns_on_unreachable_and_dead_end(self):
        extra = MINI.replace('<final id="b"', '<state id="island" crossr:source="x.rs:7"/><final id="b"')
        w = warnings(scxml(extra)[1])
        self.assertTrue(any("no transition or initial path" in m for m in w))
        self.assertTrue(any("dead end" in m for m in w))

    def test_parallel_regions_are_reachable(self):
        model, _ = scxml((FIXTURES / "media-player.scxml").read_text(encoding="utf-8"))
        closure = cs.entry_closure(model, "playing")
        self.assertTrue({"active", "playback", "volume", "unmuted"} <= closure)
        self.assertNotIn("buffering", closure)


def page_for(info: dict, scxml_text: str = SAMPLE_SCXML) -> str:
    return build_page.fill(TEMPLATE, scxml_text, info)


def page_errors(info: dict, page: str | None = None) -> list[str]:
    model, _ = scxml(SAMPLE_SCXML)
    return errors(cs.check_page(page or page_for(info), TEMPLATE, SAMPLE_SCXML, model, "p.html"))


class Page(unittest.TestCase):
    def info(self):
        return json.loads(json.dumps(SAMPLE_INFO))

    def test_template_edit_is_rejected(self):
        page = page_for(self.info()).replace("--hot: #9E4E36;", "--hot: red;")
        self.assertTrue(any("differs from the template" in m for m in page_errors({}, page)))

    def test_embedded_scxml_must_match_file(self):
        page = page_for(self.info(), SAMPLE_SCXML.replace('id="draft"', 'id="draft2"').replace('initial="draft"', 'initial="draft2"'))
        self.assertTrue(any("embedded SCXML differs" in m for m in page_errors({}, page)))

    def test_every_part_needs_a_meaning(self):
        info = self.info()
        del info["states"]["paid"]
        del info["transitions"]["t-cancel"]
        errs = page_errors(info)
        self.assertTrue(any("'paid' has no meaning" in m for m in errs))
        self.assertTrue(any("'t-cancel' has no meaning" in m for m in errs))

    def test_prose_cannot_add_parts(self):
        info = self.info()
        info["states"]["refunded"] = {"meaning": "The shop gave the money back."}
        self.assertTrue(any("'refunded' is not in the chart" in m for m in page_errors(info)))

    def test_implicit_needs_confidence_and_evidence(self):
        info = self.info()
        info.update(kind="implicit")
        info.pop("confidence")
        info.pop("evidence")
        errs = page_errors(info)
        self.assertTrue(any("needs confidence" in m for m in errs))
        self.assertTrue(any("needs evidence" in m for m in errs))

    def test_scenario_steps_must_name_chart_parts(self):
        info = self.info()
        info["scenarios"][0]["steps"].append({"event": "order.ship", "set": {"nope": True}, "caption": "The order ships."})
        errs = page_errors(info)
        self.assertTrue(any("'order.ship' is not in the chart" in m for m in errs))
        self.assertTrue(any("'nope', which is not a condition" in m for m in errs))

    def test_build_refuses_script_close_in_scxml(self):
        with self.assertRaises(ValueError):
            build_page.fill(TEMPLATE, "<scxml></script></scxml>", {})

    def test_build_escapes_script_close_in_json(self):
        page = build_page.fill(TEMPLATE, SAMPLE_SCXML, {"title": "</script>"})
        self.assertNotIn("</script>\"", page)
        self.assertEqual(json.loads(cs.JSON_BLOCK.search(page).group(2))["title"], "</script>")


class Ste(unittest.TestCase):
    def lint(self, text, mode="descriptive"):
        return cs.ste_findings("x", text, mode, frozenset({"pending"}))

    def test_clean_sentence(self):
        self.assertEqual(self.lint("The order goes into the `pending` state."), [])

    def test_sentence_length_limits(self):
        long26 = " ".join(["word"] * 26) + "."
        long21 = " ".join(["word"] * 21) + "."
        self.assertTrue(errors(self.lint(long26)))
        self.assertFalse(errors(self.lint(long21)))
        self.assertTrue(errors(self.lint(long21, "procedural")))

    def test_code_span_counts_as_one_word(self):
        text = " ".join(["word"] * 24) + " `a b c d e`."
        self.assertFalse(errors(self.lint(text)))

    def test_paragraph_limit(self):
        self.assertTrue(errors(self.lint("It stops. " * 7)))
        self.assertFalse(errors(self.lint("It stops. " * 6)))

    def test_semicolon_and_avoided_words(self):
        errs = errors(self.lint("The job will utilize the queue; then it stops."))
        self.assertTrue(any("semicolon" in m for m in errs))
        self.assertTrue(any("'utilize'" in m for m in errs))

    def test_heuristic_warnings(self):
        w = warnings(self.lint("The processing step was rejected."))
        self.assertTrue(any("'processing'" in m for m in w))
        self.assertTrue(any("passive" in m for m in w))

    def test_technical_names_are_exempt_from_ing_warning(self):
        self.assertEqual(warnings(self.lint("The order is in the pending state.")), [])


class Dictionary(unittest.TestCase):
    DICT = cs.parse_dictionary(
        "# word\tstatus\tpos\talternative\n"
        "the\tapproved\tart\t\nstop\tapproved\tv\t\njob\tapproved\tn\t\n"
        "terminate\trejected\tv\tstop\nquickly\trejected\tadv\t\n"
    )

    def lint(self, text):
        return cs.dictionary_findings("x", text, self.DICT, frozenset({"queue"}))

    def test_parse_skips_comments_and_keeps_alternatives(self):
        self.assertIn("stop", self.DICT.approved)
        self.assertEqual(self.DICT.rejected["terminate"], "stop")
        self.assertNotIn("# word", self.DICT.approved)

    def test_inflections_of_approved_words_pass(self):
        self.assertEqual(self.lint("The job stopped. The jobs stop."), [])

    def test_rejected_word_is_an_error_with_its_alternative(self):
        errs = errors(self.lint("The job terminates."))
        self.assertEqual(len(errs), 1)
        self.assertIn("Use 'stop'", errs[0])

    def test_unknown_word_is_a_warning(self):
        self.assertTrue(any("'banana'" in m for m in warnings(self.lint("The banana stops."))))

    def test_code_spans_and_technical_names_are_exempt(self):
        self.assertEqual(self.lint("The `fooBar` queues stop."), [])

    def test_check_page_uses_the_dictionary(self):
        model, _ = scxml(SAMPLE_SCXML)
        findings = cs.check_page(TEMPLATE, TEMPLATE, SAMPLE_SCXML, model, "t.html", self.DICT)
        self.assertTrue(any("STE dictionary" in f.message for f in findings))


class Cli(unittest.TestCase):
    def test_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            good = Path(d) / "m.scxml"
            good.write_text(MINI, encoding="utf-8")
            bad = Path(d) / "bad.scxml"
            bad.write_text(MINI.replace('target="b"', 'target="z"'), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(cs.main([str(good)]), 0)
                self.assertEqual(cs.main([str(bad)]), 1)
                self.assertEqual(cs.main([str(Path(d) / "missing.scxml")]), 2)
                self.assertEqual(cs.main([str(good), "--dictionary", str(Path(d) / "none.tsv")]), 2)


if __name__ == "__main__":
    unittest.main()
