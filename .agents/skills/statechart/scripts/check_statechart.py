#!/usr/bin/env python3
"""Check one statechart machine: the SCXML chart and, if given, its page.

Usage:
    check_statechart.py MACHINE.scxml [MACHINE.html] [--template PATH] [--strict]
                        [--dictionary STE.tsv]

Checks the SCXML against references/scxml-profile.md. With a page, also checks:
  - the page is the template with only the two data blocks changed
  - the embedded SCXML equals MACHINE.scxml (canonical XML)
  - the explainer JSON covers every state, event, condition, and transition,
    and names nothing the chart lacks (references/explainer-data.md)
  - every prose string passes the mechanical STE rules (references/ste.md)
  - with a dictionary (--dictionary or $STE_DICTIONARY), every word is approved,
    a technical name, or a glossary term

Prints one line per finding. Exit 0 when there are no errors (and, with
--strict, no warnings). Exit 1 otherwise. Exit 2 on bad usage.
Stdlib only. Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

SCXML_NS = "http://www.w3.org/2005/07/scxml"
CROSSR_NS = "https://sycamore-hq.github.io/crossr/scxml/1"
STATE_TAGS = frozenset({"state", "parallel", "final"})
NODE_TAGS = STATE_TAGS | {"history"}
DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "explainer-template.html"

SCXML_BLOCK = re.compile(r'(<script type="application/scxml\+xml" id="scxml">)(.*?)(</script>)', re.S)
JSON_BLOCK = re.compile(r'(<script type="application/json" id="explainer">)(.*?)(</script>)', re.S)
SOURCE_REF = re.compile(r"^[^\s:,][^:,]*:\d+(-\d+)?$")
XML_ID = re.compile(r"^[A-Za-z_][\w.\-]*$")

DESCRIPTIVE_MAX = 25
PROCEDURAL_MAX = 20
PARAGRAPH_MAX = 6

# Common words that are not approved in ASD-STE100, with a usual replacement.
# Not the dictionary: see references/ste.md.
AVOID = {
    "utilize": "use", "utilise": "use", "utilizes": "uses", "utilized": "used",
    "commence": "start", "commences": "starts", "initiate": "start", "initiates": "starts",
    "terminate": "stop or end", "terminates": "stops or ends", "terminated": "stopped or ended",
    "prior to": "before", "subsequent to": "after", "subsequently": "after or then",
    "in order to": "to", "perform": "do", "performs": "does", "performed": "done",
    "obtain": "get", "obtains": "gets", "attempt": "try", "attempts": "tries",
    "sufficient": "enough", "additional": "more", "approximately": "about",
    "assist": "help", "indicate": "show", "indicates": "shows", "modify": "change",
    "modifies": "changes", "numerous": "many", "ensure": "make sure", "ensures": "makes sure",
    "facilitate": "help", "via": "through", "e.g.": "for example", "i.e.": "that is",
    "etc.": "the full list",
}
AVOID_RE = re.compile(r"(?<![\w-])(" + "|".join(re.escape(w) for w in sorted(AVOID, key=len, reverse=True)) + r")(?![\w-])", re.I)
ING_OK = frozenset({
    "thing", "things", "string", "strings", "during", "nothing", "something", "anything",
    "everything", "bring", "ring", "spring", "swing", "wing", "ceiling", "morning", "evening",
    "king", "sing", "sting", "ping", "single",
})
PASSIVE_RE = re.compile(r"\b(?:is|are|was|were|be|been|being)\s+(?:not\s+)?(\w+(?:ed|en))\b", re.I)
PASSIVE_OK = frozenset({"open", "often", "even", "seven", "eleven", "given", "hidden", "broken", "token", "kitten"})


@dataclass(frozen=True)
class Finding:
    level: str  # "error" | "warning"
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.level}: {self.where}: {self.message}"


def err(where: str, message: str) -> Finding:
    return Finding("error", where, message)


def warn(where: str, message: str) -> Finding:
    return Finding("warning", where, message)


# ---------------------------------------------------------------- data: model


@dataclass(frozen=True)
class Node:
    id: str
    tag: str
    parent: str | None
    children: tuple[str, ...]
    initial: tuple[str, ...]


@dataclass(frozen=True)
class Transition:
    id: str
    source: str
    events: tuple[str, ...]
    cond: str
    targets: tuple[str, ...]


@dataclass(frozen=True)
class Model:
    name: str
    nodes: dict[str, Node]
    transitions: tuple[Transition, ...]
    data: tuple[str, ...]

    @property
    def events(self) -> list[str]:
        names = {
            e[:-2] if e.endswith(".*") else e
            for t in self.transitions
            for e in t.events
            if e != "*" and not e.startswith("done.")
        }
        return sorted(names)


def local(tag: str) -> str:
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def in_scxml(el: ET.Element) -> bool:
    return el.tag.startswith("{" + SCXML_NS + "}")


def crossr(el: ET.Element, name: str) -> str:
    return el.get(f"{{{CROSSR_NS}}}{name}", "")


def scxml_kids(el: ET.Element) -> Iterator[ET.Element]:
    return (c for c in el if in_scxml(c))


# ------------------------------------------------------- calculations: SCXML


def parse_xml(text: str, where: str) -> tuple[ET.Element | None, list[Finding]]:
    try:
        root = ET.fromstring(text.strip().encode("utf-8"))
    except ET.ParseError as exc:
        return None, [err(where, f"XML does not parse: {exc}")]
    if root.tag != f"{{{SCXML_NS}}}scxml":
        return None, [err(where, "root element is not {%s}scxml" % SCXML_NS)]
    if root.get("version") != "1.0":
        return root, [err(where, 'scxml version must be "1.0"')]
    return root, []


def build_model(root: ET.Element, where: str) -> tuple[Model, list[Finding]]:
    findings: list[Finding] = []
    nodes: dict[str, Node] = {}
    transitions: list[Transition] = []
    seen_tids: set[str] = set()
    root_id = "__root"

    def visit(el: ET.Element, parent: str | None) -> str:
        tag = local(el.tag)
        nid = root_id if tag == "scxml" else el.get("id", "")
        here = f"{where}: <{tag} id={nid!r}>"
        if tag != "scxml":
            if not nid:
                findings.append(err(where, f"<{tag}> has no id"))
                nid = f"__anon{len(nodes)}"
            elif not XML_ID.match(nid):
                findings.append(err(here, "id is not a valid XML id"))
            if nid in nodes:
                findings.append(err(here, "duplicate state id"))
            if not crossr(el, "source"):
                findings.append(err(here, "missing crossr:source"))
            elif not all(SOURCE_REF.match(p.strip()) for p in crossr(el, "source").split(",")):
                findings.append(err(here, "crossr:source must be path:line or path:start-end"))
        if tag == "history" and el.get("type", "shallow") not in ("shallow", "deep"):
            findings.append(err(here, 'history type must be "shallow" or "deep"'))
        children: list[str] = []
        initial = tuple((el.get("initial") or "").split())
        for c in scxml_kids(el):
            ctag = local(c.tag)
            if ctag in NODE_TAGS:
                children.append(visit(c, nid))
            elif ctag == "transition":
                transitions.append(make_transition(c, nid, here))
            elif ctag == "initial":
                it = next((x for x in scxml_kids(c) if local(x.tag) == "transition"), None)
                initial = tuple((it.get("target") or "").split()) if it is not None else ()
        nodes[nid] = Node(nid, tag, parent, tuple(children), initial)
        return nid

    def make_transition(el: ET.Element, source: str, here: str) -> Transition:
        tid = crossr(el, "id")
        if not tid:
            findings.append(err(here, "a <transition> has no crossr:id"))
            tid = f"__t{len(transitions)}"
        elif tid in seen_tids:
            findings.append(err(here, f"duplicate crossr:id {tid!r}"))
        seen_tids.add(tid)
        if not crossr(el, "source"):
            findings.append(err(f"{where}: transition {tid!r}", "missing crossr:source"))
        elif not all(SOURCE_REF.match(p.strip()) for p in crossr(el, "source").split(",")):
            findings.append(err(f"{where}: transition {tid!r}", "crossr:source must be path:line or path:start-end"))
        return Transition(
            tid, source, tuple((el.get("event") or "").split()), el.get("cond") or "",
            tuple((el.get("target") or "").split()),
        )

    visit(root, None)
    data = tuple(d.get("id", "") for d in root.iter(f"{{{SCXML_NS}}}data"))
    return Model(root.get("name") or "", nodes, tuple(transitions), data), findings


def is_descendant(model: Model, nid: str, anc: str) -> bool:
    p = model.nodes[nid].parent
    while p is not None:
        if p == anc:
            return True
        p = model.nodes[p].parent
    return False


def child_states(model: Model, nid: str) -> list[str]:
    return [c for c in model.nodes[nid].children if model.nodes[c].tag in STATE_TAGS]


def default_initial(model: Model, nid: str) -> tuple[str, ...]:
    node = model.nodes[nid]
    kids = child_states(model, nid)
    if node.tag not in ("state", "scxml") or not kids:
        return ()
    return node.initial or (kids[0],)


def reference_findings(model: Model, where: str) -> list[Finding]:
    out: list[Finding] = []
    for t in model.transitions:
        out += [err(f"{where}: transition {t.id!r}", f"target {x!r} names no state") for x in t.targets if x not in model.nodes]
    for n in model.nodes.values():
        for x in n.initial:
            if x not in model.nodes:
                out.append(err(f"{where}: <{n.tag} id={n.id!r}>", f"initial {x!r} names no state"))
            elif not is_descendant(model, x, n.id):
                out.append(err(f"{where}: <{n.tag} id={n.id!r}>", f"initial {x!r} is not a descendant"))
        if n.tag == "scxml" and not child_states(model, n.id):
            out.append(err(where, "the chart has no states"))
    return out


# condition grammar: see references/scxml-profile.md#conditions
COND_TOKEN = re.compile(r"\s*(\|\||&&|!|\(|\)|In\s*\(\s*'([^']*)'\s*\)|In\s*\(\s*\"([^\"]*)\"\s*\)|[A-Za-z_$][\w$.]*)")


def cond_names(src: str) -> tuple[list[str], list[str]]:
    """Parse a condition. Return (data names, In() state ids). Raise ValueError on bad syntax."""
    toks: list[tuple[str, str]] = []
    i = 0
    while i < len(src):
        if not src[i:].strip():
            break
        m = COND_TOKEN.match(src, i)
        if not m:
            raise ValueError(f"unsupported syntax at {src[i:]!r}")
        tok = m.group(1)
        if tok.startswith("In"):
            toks.append(("in", m.group(2) if m.group(2) is not None else m.group(3)))
        elif tok in ("||", "&&", "!", "(", ")"):
            toks.append((tok, tok))
        elif tok in ("true", "false"):
            toks.append(("lit", tok))
        else:
            toks.append(("var", tok))
        i = m.end()
    pos = 0
    names: list[str] = []
    states: list[str] = []

    def peek() -> str:
        return toks[pos][0] if pos < len(toks) else ""

    def expr() -> None:
        nonlocal pos
        term()
        while peek() == "||":
            pos += 1
            term()

    def term() -> None:
        nonlocal pos
        factor()
        while peek() == "&&":
            pos += 1
            factor()

    def factor() -> None:
        nonlocal pos
        if pos >= len(toks):
            raise ValueError("ends too early")
        kind, val = toks[pos]
        pos += 1
        if kind == "!":
            factor()
        elif kind == "(":
            expr()
            if peek() != ")":
                raise ValueError("no closing bracket")
            pos += 1
        elif kind == "var":
            names.append(val)
        elif kind == "in":
            states.append(val)
        elif kind != "lit":
            raise ValueError(f"operator {val!r} in the wrong place")

    expr()
    if pos != len(toks):
        raise ValueError("extra text")
    return names, states


def cond_findings(model: Model, root: ET.Element, where: str) -> list[Finding]:
    out: list[Finding] = []
    declared = set(model.data)
    exprs = [(f"transition {t.id!r}", t.cond) for t in model.transitions if t.cond]
    exprs += [(f"<data id={d.get('id')!r}>", d.get("expr") or "false") for d in root.iter(f"{{{SCXML_NS}}}data")]
    exprs += [(f"<assign location={a.get('location')!r}>", a.get("expr") or "") for a in root.iter(f"{{{SCXML_NS}}}assign")]
    for label, src in exprs:
        here = f"{where}: {label}"
        try:
            names, states = cond_names(src)
        except ValueError as exc:
            out.append(err(here, f"condition {src!r} is outside the profile grammar: {exc}"))
            continue
        out += [err(here, f"condition names undeclared data {n!r}") for n in names if n not in declared]
        out += [err(here, f"In({s!r}) names no state") for s in states if s not in model.nodes]
    for a in root.iter(f"{{{SCXML_NS}}}assign"):
        if a.get("location") not in declared:
            out.append(err(f"{where}: <assign>", f"location {a.get('location')!r} is not declared data"))
    if any(t.cond and cond_names(t.cond)[0] for t in model.transitions if _parses(t.cond)) and root.get("datamodel") != "ecmascript":
        out.append(err(where, 'conditions name data, so datamodel must be "ecmascript"'))
    if root.get("datamodel") not in (None, "null", "ecmascript"):
        out.append(err(where, 'datamodel must be "null" or "ecmascript"'))
    return out


def _parses(src: str) -> bool:
    try:
        cond_names(src)
    except ValueError:
        return False
    return True


def entry_closure(model: Model, nid: str) -> set[str]:
    """States entered when a transition targets nid, ignoring history records."""
    out: set[str] = set()
    work = [nid]
    while work:
        cur = work.pop()
        if cur in out:
            continue
        out.add(cur)
        node = model.nodes[cur]
        if node.tag == "parallel":
            work += child_states(model, cur)
        elif node.tag == "history":
            work += [x for t in model.transitions if t.source == cur for x in t.targets if x in model.nodes]
        else:
            work += [x for x in default_initial(model, cur) if x in model.nodes]
        child, p = cur, node.parent
        while p is not None and p != "__root" and p not in out:
            out.add(p)
            if model.nodes[p].tag == "parallel":
                work += [c for c in child_states(model, p) if c != child]
            child, p = p, model.nodes[p].parent
    return out


def reachability_findings(model: Model, where: str) -> list[Finding]:
    if any(x not in model.nodes for t in model.transitions for x in t.targets):
        return []
    reached: set[str] = set()
    for x in default_initial(model, "__root"):
        if x in model.nodes:
            reached |= entry_closure(model, x)
    changed = True
    while changed:
        changed = False
        for t in model.transitions:
            src_active = t.source in reached
            if not src_active:
                continue
            for x in t.targets:
                new = entry_closure(model, x) - reached
                if new:
                    reached |= new
                    changed = True
    out: list[Finding] = []
    for n in model.nodes.values():
        if n.tag == "scxml":
            continue
        if n.id not in reached:
            out.append(warn(f"{where}: <{n.tag} id={n.id!r}>", "no transition or initial path enters this state"))
    sources = {t.source for t in model.transitions}
    for n in model.nodes.values():
        if n.tag != "state" or child_states(model, n.id):
            continue
        chain = [n.id]
        p = n.parent
        while p is not None:
            chain.append(p)
            p = model.nodes[p].parent
        if not any(c in sources for c in chain):
            out.append(warn(f"{where}: <state id={n.id!r}>", "dead end: not final and has no way out"))
    return out


def check_scxml_text(text: str, where: str) -> tuple[Model | None, list[Finding]]:
    root, findings = parse_xml(text, where)
    if root is None:
        return None, findings
    model, more = build_model(root, where)
    findings += more
    findings += reference_findings(model, where)
    findings += cond_findings(model, root, where)
    findings += reachability_findings(model, where)
    return model, findings


# --------------------------------------------------------- calculations: page


def template_findings(page: str, template: str, where: str) -> list[Finding]:
    def blank(s: str) -> str:
        s = SCXML_BLOCK.sub(lambda m: m.group(1) + m.group(3), s, count=1)
        return JSON_BLOCK.sub(lambda m: m.group(1) + m.group(3), s, count=1)

    if blank(page) != blank(template):
        return [err(where, "the page differs from the template outside the two data blocks")]
    return []


def canonical(text: str) -> str:
    return ET.canonicalize(text.strip(), strip_text=True)


def embed_findings(page: str, scxml_text: str, where: str) -> tuple[str | None, list[Finding]]:
    m_x = SCXML_BLOCK.search(page)
    m_j = JSON_BLOCK.search(page)
    out: list[Finding] = []
    if not m_x:
        out.append(err(where, 'no <script type="application/scxml+xml" id="scxml"> block'))
    elif canonical(m_x.group(2)) != canonical(scxml_text):
        out.append(err(where, "the embedded SCXML differs from the .scxml file"))
    if not m_j:
        out.append(err(where, 'no <script type="application/json" id="explainer"> block'))
        return None, out
    if "</script" in m_j.group(2).lower():
        out.append(err(where, "the JSON block contains </script"))
    return m_j.group(2), out


def prose_strings(info: dict) -> Iterator[tuple[str, str, str]]:
    """Yield (where, text, mode) for every prose string. mode is descriptive|procedural."""
    for key in ("summary", "context"):
        for i, p in enumerate(info.get(key) or []):
            yield f"{key}[{i}]", p, "descriptive"
    for g in info.get("glossary") or []:
        yield f"glossary[{g.get('term')!r}]", g.get("definition", ""), "descriptive"
    for section, fields in (("states", ("meaning",)), ("events", ("meaning", "origin")),
                            ("conditions", ("meaning",)), ("transitions", ("meaning",))):
        for k, v in (info.get(section) or {}).items():
            for f in fields:
                if isinstance(v, dict) and v.get(f):
                    yield f"{section}[{k!r}].{f}", v[f], "descriptive"
    for i, sc in enumerate(info.get("scenarios") or []):
        if sc.get("goal"):
            yield f"scenarios[{i}].goal", sc["goal"], "descriptive"
        for j, st in enumerate(sc.get("steps") or []):
            yield f"scenarios[{i}].steps[{j}].caption", st.get("caption", ""), "descriptive"
    for i, e in enumerate(info.get("evidence") or []):
        yield f"evidence[{i}].note", e.get("note", ""), "descriptive"
    for i, n in enumerate(info.get("notes") or []):
        yield f"notes[{i}].text", n.get("text", ""), "descriptive"


def coverage_findings(model: Model, info: dict, where: str) -> list[Finding]:
    out: list[Finding] = []
    if info.get("schema") != 1:
        out.append(err(where, "schema must be 1"))
    for key in ("title", "summary", "context", "glossary", "scenarios"):
        if not info.get(key):
            out.append(err(where, f"{key} is missing or empty"))
    kind = info.get("kind")
    if kind not in ("explicit", "implicit"):
        out.append(err(where, 'kind must be "explicit" or "implicit"'))
    if info.get("confidence") not in (None, "high", "medium", "low"):
        out.append(err(where, 'confidence must be "high", "medium", or "low"'))
    if kind == "implicit":
        if not info.get("confidence"):
            out.append(err(where, "an implicit machine needs confidence"))
        if not info.get("evidence"):
            out.append(err(where, "an implicit machine needs evidence"))

    expected = {
        "states": [n for n in model.nodes if n != "__root"],
        "events": model.events,
        "conditions": list(model.data),
        "transitions": [t.id for t in model.transitions],
    }
    for section, ids in expected.items():
        given = info.get(section) or {}
        if not isinstance(given, dict):
            out.append(err(where, f"{section} must be an object keyed by id"))
            continue
        for i in ids:
            v = given.get(i)
            if not isinstance(v, dict) or not str(v.get("meaning", "")).strip():
                out.append(err(f"{where}: {section}", f"{i!r} has no meaning"))
        for extra in sorted(set(given) - set(ids)):
            out.append(err(f"{where}: {section}", f"{extra!r} is not in the chart"))
    for i, sc in enumerate(info.get("scenarios") or []):
        if not sc.get("name"):
            out.append(err(f"{where}: scenarios[{i}]", "no name"))
        if not sc.get("steps"):
            out.append(err(f"{where}: scenarios[{i}]", "no steps"))
        for j, st in enumerate(sc.get("steps") or []):
            here = f"{where}: scenarios[{i}].steps[{j}]"
            if not st.get("caption"):
                out.append(err(here, "no caption"))
            if not st.get("event") and not st.get("set"):
                out.append(err(here, "needs an event, a set, or both"))
            if st.get("event") and not _event_known(model, st["event"]):
                out.append(err(here, f"event {st['event']!r} is not in the chart"))
            out += [err(here, f"set names {k!r}, which is not a condition") for k in (st.get("set") or {}) if k not in model.data]
    for i, e in enumerate(info.get("evidence") or []):
        if not all(SOURCE_REF.match(p.strip()) for p in str(e.get("source", "")).split(",")):
            out.append(err(f"{where}: evidence[{i}]", "source must be path:line or path:start-end"))
    return out


def _event_known(model: Model, name: str) -> bool:
    for t in model.transitions:
        for d in t.events:
            base = d[:-2] if d.endswith(".*") else d.rstrip(".")
            if d == "*" or name == base or name.startswith(base + "."):
                return True
    return False


# ----------------------------------------------------------- calculations: STE

CODE_SPAN = re.compile(r"`[^`]*`")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[]|CODE)")


def sentences(text: str) -> list[str]:
    flat = CODE_SPAN.sub("CODE", text.strip())
    return [s for s in SENTENCE_SPLIT.split(flat) if s.strip()]


def word_count(sentence: str) -> int:
    return sum(1 for w in sentence.split() if re.search(r"[\w]", w))


def ste_findings(where: str, text: str, mode: str, technical: frozenset[str]) -> list[Finding]:
    out: list[Finding] = []
    if not isinstance(text, str) or not text.strip():
        return [err(where, "empty prose string")]
    limit = PROCEDURAL_MAX if mode == "procedural" else DESCRIPTIVE_MAX
    sents = sentences(text)
    if len(sents) > PARAGRAPH_MAX:
        out.append(err(where, f"STE: {len(sents)} sentences in one paragraph (max {PARAGRAPH_MAX})"))
    for s in sents:
        n = word_count(s)
        if n > limit:
            out.append(err(where, f"STE: {n} words in a {mode} sentence (max {limit}): {s[:60]!r}"))
    plain = CODE_SPAN.sub(" ", text)
    if ";" in plain:
        out.append(err(where, "STE: semicolon. Write two sentences"))
    for m in AVOID_RE.finditer(plain):
        out.append(err(where, f"STE: {m.group(1)!r} is not approved. Use {AVOID[m.group(1).lower()]!r}"))
    lowered = plain.lower()
    for term in technical:
        lowered = re.sub(r"(?<!\w)" + re.escape(term) + r"(?!\w)", " ", lowered)
    for w in sorted(set(re.findall(r"\b([a-z]{3,}ing)\b", lowered)) - ING_OK):
        out.append(warn(where, f"STE: {w!r} may be an -ing noun or adjective. Rewrite, or define it as a technical name"))
    for m in PASSIVE_RE.finditer(lowered):
        if m.group(1) not in PASSIVE_OK:
            out.append(warn(where, f"STE: possible passive {m.group(0)!r}. Prefer the active voice"))
    return out


# The ASD-STE100 dictionary is copyrighted. The checker reads it from a local
# TSV that never goes into a repository: word, status, part of speech, alternative.


@dataclass(frozen=True)
class Dictionary:
    approved: frozenset[str]
    rejected: dict[str, str]  # word -> approved alternative


def parse_dictionary(text: str) -> Dictionary:
    """Pure. Lines: word<TAB>approved|rejected<TAB>pos<TAB>alternative. '#' starts a comment."""
    approved: set[str] = set()
    rejected: dict[str, str] = {}
    for line in text.splitlines():
        cols = [c.strip() for c in line.split("\t")]
        if not cols[0] or cols[0].startswith("#") or len(cols) < 2:
            continue
        word, status = cols[0].lower(), cols[1].lower()
        if status == "approved":
            approved.add(word)
        elif status == "rejected":
            rejected.setdefault(word, cols[3] if len(cols) > 3 else "")
    return Dictionary(frozenset(approved), rejected)


def base_forms(word: str) -> list[str]:
    """The word and the simple bases it can inflect from, most specific first."""
    forms = [word]
    for suffix, repl in (("ies", "y"), ("ied", "y"), ("es", ""), ("s", ""), ("ed", ""), ("d", ""), ("ing", ""), ("ing", "e")):
        if word.endswith(suffix) and len(word) - len(suffix) >= 2:
            forms.append(word[: -len(suffix)] + repl)
    if len(word) > 4 and word[-3:-2] == word[-4:-3] and word.endswith(("ed", "er")):
        forms.append(word[:-3])  # stopped -> stop
    return forms


def dictionary_findings(where: str, text: str, dictionary: Dictionary, technical: frozenset[str]) -> list[Finding]:
    lowered = CODE_SPAN.sub(" ", text).lower()
    for term in technical:
        lowered = re.sub(r"(?<!\w)" + re.escape(term) + r"(?:s|es|ed|d)?(?!\w)", " ", lowered)
    out: list[Finding] = []
    for word in sorted(set(re.findall(r"[a-z][a-z'-]*[a-z]|[a-z]", lowered))):
        forms = base_forms(word)
        if any(f in dictionary.approved for f in forms):
            continue
        hit = next((f for f in forms if f in dictionary.rejected), None)
        if hit is not None:
            alt = dictionary.rejected[hit]
            out.append(err(where, f"STE dictionary: {word!r} is not approved" + (f". Use {alt!r}" if alt else "")))
        else:
            out.append(warn(where, f"STE dictionary: {word!r} is not in the dictionary. Use an approved word, or define it in the glossary"))
    return out


def technical_names(model: Model, info: dict) -> frozenset[str]:
    names = {str(g.get("term", "")).lower() for g in info.get("glossary") or []}
    names |= {n.lower().replace("_", " ") for n in model.nodes}
    names |= {n.lower() for n in model.nodes}
    return frozenset(n for n in names if n)


def check_page(page: str, template: str, scxml_text: str, model: Model, where: str,
               dictionary: Dictionary | None = None) -> list[Finding]:
    findings = template_findings(page, template, where)
    raw, more = embed_findings(page, scxml_text, where)
    findings += more
    if raw is None:
        return findings
    try:
        info = json.loads(raw)
    except json.JSONDecodeError as exc:
        return findings + [err(where, f"explainer JSON does not parse: {exc}")]
    if not isinstance(info, dict):
        return findings + [err(where, "explainer JSON must be an object")]
    findings += coverage_findings(model, info, where)
    tech = technical_names(model, info)
    for loc, text, mode in prose_strings(info):
        findings += ste_findings(f"{where}: {loc}", text, mode, tech)
        if dictionary is not None and isinstance(text, str):
            findings += dictionary_findings(f"{where}: {loc}", text, dictionary, tech)
    return findings


# ------------------------------------------------------------------- actions


def run(scxml_path: Path, html_path: Path | None, template_path: Path,
        dictionary_path: Path | None = None) -> list[Finding]:
    scxml_text = scxml_path.read_text(encoding="utf-8")
    model, findings = check_scxml_text(scxml_text, scxml_path.name)
    if html_path is not None and model is not None:
        findings += check_page(
            html_path.read_text(encoding="utf-8"), template_path.read_text(encoding="utf-8"),
            scxml_text, model, html_path.name,
            parse_dictionary(dictionary_path.read_text(encoding="utf-8")) if dictionary_path else None,
        )
    return findings


def report(findings: Iterable[Finding], strict: bool) -> int:
    fs = list(findings)
    for f in fs:
        print(f)
    errors = sum(f.level == "error" for f in fs)
    warnings = len(fs) - errors
    print(f"{'FAIL' if errors or (strict and warnings) else 'PASS'}: {errors} errors, {warnings} warnings")
    return 1 if errors or (strict and warnings) else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("scxml", type=Path)
    ap.add_argument("html", type=Path, nargs="?")
    ap.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    ap.add_argument("--dictionary", type=Path, default=_env_path("STE_DICTIONARY"),
                    help="local ASD-STE100 wordlist TSV (default: $STE_DICTIONARY)")
    args = ap.parse_args(argv)
    for p in [args.scxml, args.html, args.template if args.html else None, args.dictionary]:
        if p is not None and not p.is_file():
            print(f"error: {p}: file not found", file=sys.stderr)
            return 2
    if args.html:
        print(f"note: STE dictionary {'loaded from ' + str(args.dictionary) if args.dictionary else 'not loaded: mechanical STE rules only'}")
    return report(run(args.scxml, args.html, args.template, args.dictionary), args.strict)


def _env_path(name: str) -> Path | None:
    value = os.environ.get(name, "").strip()
    return Path(value).expanduser() if value else None


if __name__ == "__main__":
    sys.exit(main())
