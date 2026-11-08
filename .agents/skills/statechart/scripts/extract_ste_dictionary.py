#!/usr/bin/env python3
"""Extract the ASD-STE100 dictionary (Part 2) into the TSV the checker reads.

Usage:
    extract_ste_dictionary.py ASD-STE100.pdf OUT.tsv
    extract_ste_dictionary.py ASD-STE100.txt OUT.tsv     # text from `pdftotext -layout`

The standard is copyrighted by ASD. Its distribution needs written permission
from the STEMG. Write OUT.tsv to a private location. Never commit it.

Output: one line per entry, tab-separated: word, approved|rejected, part of
speech, approved alternatives ("; "-separated). Approved verbs also get one
"approved" line for each listed form (CLOSES, CLOSED).

Reads a PDF with `pdftotext -layout` (poppler). Otherwise stdlib only.
Tested with Issue 9 (2025-01-15). A different issue can change the layout:
check the entry count the script prints.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

POS = r"(?:n|v|adj|adv|prep|pron|conj|art|TN|TV)"
POS_LIST = POS + r"(?:\s*,\s*" + POS + r")*"
# First column of a headword line: "WORD (pos)" or "word (pos)", optional trailing comma
HEAD = re.compile(r"^([A-Za-z][A-Za-z0-9'./\-]*(?: [A-Za-z0-9'./\-]+)*) \((" + POS_LIST + r")\),?(?:\s+(.*))?$")
WORDS = re.compile(r"^[A-Za-z][A-Za-z0-9'./\-]*(?: [A-Za-z0-9'./\-]+)*,?$")
# Verb forms in column 0: "CLOSES," or "IS, WAS," or "(also ARE, WERE)"
FORMS = re.compile(r"(?:\(also )?[A-Z][A-Z'\-]*(?:,\s*[A-Z][A-Z'\-]*)*,?\)?")
POS_LINE = re.compile(r"^\((" + POS_LIST + r")\),?$")
ALTERNATIVE = re.compile(r"\b([A-Z][A-Z'\-]*(?: [A-Z][A-Z'\-]*)*) \((" + POS + r")\)")
HEADER = re.compile(r"^\(part of speech\)\s+ALTERNATIVES")
NOISE = re.compile(r"^(Issue \d|Page \d|\d{4}-\d\d-\d\d|ASD.STE100|Word\s|\(part of speech\))")


def first_column(line: str) -> tuple[str, str]:
    """Split a column-0 line at its first run of two or more spaces."""
    m = re.match(r"^(\S(?:.*?\S)?)(?:\s{2,}(.*))?$", line)
    return (m.group(1), m.group(2) or "") if m else (line.strip(), "")


@dataclass(frozen=True)
class Entry:
    word: str
    status: str  # approved | rejected
    pos: str
    alternatives: tuple[str, ...]

    def tsv(self) -> str:
        return "\t".join((self.word, self.status, self.pos, "; ".join(self.alternatives)))


def dictionary_lines(text: str) -> list[str]:
    """Pure. The lines from the first dictionary page header on, without page chrome."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if HEADER.match(line)), None)
    if start is None:
        raise ValueError("no dictionary page header '(part of speech)  ALTERNATIVES' found")
    return [line.rstrip() for line in lines[start:] if line.strip() and not NOISE.match(line.strip())]


def parse(text: str) -> list[Entry]:
    """Pure. Parse `pdftotext -layout` output of the standard into entries."""
    lines = dictionary_lines(text)
    entries: list[Entry] = []
    current: dict | None = None

    def flush() -> None:
        if current is None:
            return
        word = current["word"]
        approved = word == word.upper()
        alts = () if approved else tuple(dict.fromkeys(current["alts"]))
        entries.append(Entry(word.lower(), "approved" if approved else "rejected", current["pos"], alts))
        entries.extend(Entry(f.lower(), "approved", current["pos"], ()) for f in current["forms"])

    def start(word: str, pos: str, rest: str) -> dict:
        alts = [a for a, _ in ALTERNATIVE.findall(re.split(r"\s{2,}", rest)[0])] if rest else []
        return {"word": word, "pos": pos.replace(" ", ""), "forms": [], "alts": alts, "in_forms": True}

    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.startswith(" "):
            m = HEAD.match(line)
            if m:
                flush()
                current = start(m.group(1), m.group(2), m.group(3) or "")
                continue
            col, rest = first_column(line)
            # a headword hyphen-split over two lines: ELECTROMAG- / NETIC (adj)
            while col.endswith("-") and i < len(lines) and not lines[i].startswith(" "):
                nxt, nrest = first_column(lines[i])
                col, rest, i = col[:-1] + nxt, rest or nrest, i + 1
            m = HEAD.match(col)
            if m:
                flush()
                current = start(m.group(1), m.group(2), rest)
                continue
            p = POS_LINE.match(first_column(lines[i])[0]) if i < len(lines) else None
            if p and WORDS.match(col) and not col.endswith(","):
                flush()  # the part of speech wrapped: "According to" / "(prep)"
                current = start(col, p.group(1), rest)
                i += 1
                continue
            if (current is not None and current["in_forms"] and current["word"].isupper()
                    and "v" in current["pos"].split(",") and FORMS.fullmatch(col)):
                current["forms"] += re.findall(r"[A-Z][A-Z'\-]*", col.replace("(also", ""))
                continue
        if current is None:
            continue
        current["in_forms"] = False
        # alternatives sit in the second column, before the STE example column
        current["alts"] += [a for a, _ in ALTERNATIVE.findall(line[:48])]
    flush()
    return entries


def read_text(path: Path) -> str:
    """Action: text of the standard, through pdftotext for a PDF."""
    if path.suffix.lower() != ".pdf":
        return path.read_text(encoding="utf-8")
    if shutil.which("pdftotext") is None:
        raise ValueError("pdftotext not found. Install poppler, or pass the text from `pdftotext -layout`")
    done = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise ValueError(f"pdftotext failed: {done.stderr.strip()}")
    return done.stdout


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    src, out = Path(args[0]), Path(args[1])
    try:
        entries = parse(read_text(src))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    header = "# ASD-STE100 wordlist extracted for local use only. Copyright ASD. Do not commit or distribute.\n"
    out.write_text(header + "\n".join(e.tsv() for e in entries) + "\n", encoding="utf-8")
    approved = sum(e.status == "approved" for e in entries)
    print(f"wrote {out}: {len(entries)} entries ({approved} approved, {len(entries) - approved} rejected)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
