#!/usr/bin/env python3
"""Refuse a design document that is not ready: missing headings, placeholder text, dash characters or wide table rows.

    python scripts/check-design-doc.py docs/brand/naming-brief.md --require Exclusions --require "Structure options"

A required heading matches a Markdown heading line (any level) whose text equals the required words, or starts with
them at a word boundary, ignoring case: --require "Status bar" matches "## Status bar and zoom" but never a paragraph.
Exit 0 when the document passes, 1 with one line per problem, 2 when the file cannot be read. Stdlib only.
"""
import argparse
from pathlib import Path
import re
import sys

PLACEHOLDERS = re.compile(r"\bCHANGEME\b|\bTBD\b|\bTODO:|\blorem ipsum\b", re.IGNORECASE)
DASHES = {"—": "em dash", "–": "en dash"}
MAX_ROW = 100
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")


def prose_lines(text):
    """Yield (line number, line, inside fenced code) for every line."""
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            yield number, line, True
            fenced = not fenced
            continue
        yield number, line, fenced


def headings(text):
    return [HEADING.match(line)[1] for _, line, fenced in prose_lines(text) if not fenced and HEADING.match(line)]


def missing_headings(text, required):
    found = [h.casefold() for h in headings(text)]
    missing = []
    for want in required:
        w = want.strip().casefold()
        if not any(h == w or (h.startswith(w) and not h[len(w)].isalnum()) for h in found):
            missing.append(f"missing heading: {want}")
    return missing


def placeholders(text):
    return [f"line {n}: placeholder {m.group(0)!r}" for n, line, fenced in prose_lines(text) if not fenced
            for m in PLACEHOLDERS.finditer(line)]


def dashes(text):
    return [f"line {n}: {DASHES[ch]} (use a comma, colon, parentheses or a full stop)"
            for n, line, fenced in prose_lines(text) if not fenced for ch in DASHES if ch in line]


def wide_rows(text):
    return [f"line {n}: table row is {len(line)} characters (max {MAX_ROW})"
            for n, line, fenced in prose_lines(text) if not fenced and line.lstrip().startswith("|") and len(line) > MAX_ROW]


def check(text, required):
    return missing_headings(text, required) + placeholders(text) + dashes(text) + wide_rows(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Refuse a design document that is not ready.")
    parser.add_argument("path", type=Path, help="Markdown document to check")
    parser.add_argument("--require", action="append", default=[], metavar="HEADING",
                        help="heading the document must contain (repeatable)")
    args = parser.parse_args(argv)
    try:
        text = args.path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"{args.path}: cannot read ({exc})", file=sys.stderr)
        return 2
    problems = check(text, args.require)
    for problem in problems:
        print(f"{args.path}: {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
