#!/usr/bin/env python3
"""Build an explainer page: the template with its two data blocks filled.

Usage:
    build_page.py MACHINE.scxml MACHINE.json OUT.html [--template PATH]

Reads the SCXML and the prose JSON, puts them in the template's
<script id="scxml"> and <script id="explainer"> blocks, and writes OUT.html.
Changes nothing else. Exit 1 when an input cannot go in a <script> block.
Stdlib only. Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from check_statechart import DEFAULT_TEMPLATE, JSON_BLOCK, SCXML_BLOCK


def fill(template: str, scxml_text: str, info: dict) -> str:
    """Pure: return the page. Raise ValueError when an input breaks the block."""
    if "</script" in scxml_text.lower():
        raise ValueError("the SCXML contains </script")
    body = json.dumps(info, indent=2, ensure_ascii=False).replace("</", "<\\/")
    if not SCXML_BLOCK.search(template) or not JSON_BLOCK.search(template):
        raise ValueError("the template has no data blocks")
    page = SCXML_BLOCK.sub(lambda m: m.group(1) + "\n" + scxml_text.strip() + "\n" + m.group(3), template, count=1)
    return JSON_BLOCK.sub(lambda m: m.group(1) + "\n" + body + "\n" + m.group(3), page, count=1)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("scxml", type=Path)
    ap.add_argument("prose", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    args = ap.parse_args(argv)
    try:
        info = json.loads(args.prose.read_text(encoding="utf-8"))
        page = fill(args.template.read_text(encoding="utf-8"), args.scxml.read_text(encoding="utf-8"), info)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.out.write_text(page, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
