#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Refuse a design document that is not ready: missing headings, placeholder text, dash characters or wide table rows.

    python scripts/check-design-doc.py docs/brand/naming-brief.md --require Exclusions --require "Structure options"

A required heading matches a Markdown heading line (any level) whose text equals the required words, or starts with
them at a word boundary, ignoring case: --require "Status bar" matches "## Status bar and zoom" but never a paragraph.
Placeholders are refused everywhere, fenced code included; dashes are refused outside fenced code, which may quote
text byte for byte. Table rows are checked with or without outer pipes. Exit 0 when the document passes, 1 with one
line per problem, 2 when the file cannot be read or the arguments are invalid. Stdlib only.
"""
import argparse
from pathlib import Path
import re
import sys

PLACEHOLDERS = re.compile(r"\bCHANGEME\b|\bTBD\b|\bTODO:|\blorem ipsum\b", re.IGNORECASE)
DASHES = {"\u2014": "em dash", "\u2013": "en dash"}
MAX_ROW = 100
# CommonMark fences: up to 3 spaces of indent, then 3 or more backticks or tildes. A backtick fence's info string
# may not contain a backtick. A closing fence uses the same character, at least as many, and nothing after it.
OPEN_FENCE = re.compile(r"^ {0,3}(?P<run>`{3,}|~{3,})(?P<info>.*)$")
HEADING = re.compile(r"^ {0,3}#{1,6}\s+(.*?)(?:\s+#+)?\s*$")  # a closing # run counts only after whitespace
TABLE_DELIMITER = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")
# Lines that start another block and so end a table (GFM): heading, fence, quote, thematic break, list item.
BLOCK_START = re.compile(r"^ {0,3}(#{1,6}(\s|$)|`{3,}|~{3,}|>|([-*_])(\s*\3){2,}\s*$|[-+*]\s|\d{1,9}[.)]\s)")
LINE_END = re.compile(r"\r\n|\r|\n")


def md_lines(text):
    """Split on Markdown line endings only; U+2028 and other Unicode separators stay inside a line."""
    lines = LINE_END.split(text)
    return lines[:-1] if lines and lines[-1] == "" else lines


def indent_columns(line):
    """Leading indentation in columns, with tabs advancing to the next multiple of 4 (CommonMark)."""
    col = 0
    for ch in line:
        if ch == " ":
            col += 1
        elif ch == "\t":
            col += 4 - col % 4
        else:
            break
    return col


def lines_with_fences(text):
    """Return [(line number, line, inside fenced code)] and the line number of a fence left open (or None)."""
    out, fence, opened_at = [], None, None
    for number, line in enumerate(md_lines(text), 1):
        if fence is None:
            m = OPEN_FENCE.match(line)
            if m and not (m["run"][0] == "`" and "`" in m["info"]):
                fence, opened_at = m["run"], number
                out.append((number, line, True))
                continue
            out.append((number, line, False))
        else:
            out.append((number, line, True))
            stripped = line.strip(" \t")
            if indent_columns(line) <= 3 and stripped and set(stripped) == {fence[0]} and len(stripped) >= len(fence):
                fence, opened_at = None, None
    return out, opened_at


def headings(text):
    lines, _ = lines_with_fences(text)
    return [m[1] for _, line, fenced in lines if not fenced for m in [HEADING.match(line)] if m]


def missing_headings(text, required):
    found = [h.casefold() for h in headings(text)]
    missing = []
    for want in required:
        w = want.strip().casefold()
        if not any(h == w or (h.startswith(w) and not re.match(r"\w", h[len(w)])) for h in found):
            missing.append(f"missing heading: {want}")
    return missing


def unclosed_fence(text):
    """An unclosed fence would hide every later line from the dash and table rules."""
    _, opened_at = lines_with_fences(text)
    return [f"line {opened_at}: code fence is never closed"] if opened_at else []


def placeholders(text):
    return [f"line {n}: placeholder {m.group(0)!r}" for n, line in enumerate(md_lines(text), 1)
            for m in PLACEHOLDERS.finditer(line)]


def dashes(text):
    lines, _ = lines_with_fences(text)
    return [f"line {n}: {DASHES[ch]} (use a comma, colon, parentheses or a full stop)"
            for n, line, fenced in lines if not fenced for ch in DASHES if ch in line]


def table_rows(text):
    """Line numbers of Markdown table rows: lines starting with a pipe, and every row of a pipe table with or
    without outer pipes (header, delimiter and body until a blank line)."""
    lines, _ = lines_with_fences(text)
    rows = {n for n, line, fenced in lines if not fenced and line.lstrip().startswith("|")}
    for i, (n, line, fenced) in enumerate(lines):
        if fenced or i == 0 or not TABLE_DELIMITER.match(line) or "|" not in lines[i - 1][1] or lines[i - 1][2]:
            continue
        rows.update({lines[i - 1][0], n})
        for m, body, body_fenced in lines[i + 1:]:
            if body_fenced or not body.strip() or BLOCK_START.match(body):
                break
            rows.add(m)
    return rows


def wide_rows(text):
    by_number = dict(enumerate(md_lines(text), 1))
    return [f"line {n}: table row is {len(by_number[n])} characters (max {MAX_ROW})"
            for n in sorted(table_rows(text)) if len(by_number[n]) > MAX_ROW]


def check(text, required):
    return (missing_headings(text, required) + unclosed_fence(text) + placeholders(text) + dashes(text)
            + wide_rows(text))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Refuse a design document that is not ready.")
    parser.add_argument("path", type=Path, help="Markdown document to check")
    parser.add_argument("--require", action="append", default=[], metavar="HEADING",
                        help="heading the document must contain (repeatable)")
    args = parser.parse_args(argv)
    if any(not r.strip() for r in args.require):
        parser.error("--require needs heading text; an empty value would match every heading")
    try:
        text = args.path.read_text(encoding="utf-8-sig")  # tolerate a byte order mark before the first heading
    except (OSError, UnicodeDecodeError) as exc:
        print(f"{args.path}: cannot read ({exc})", file=sys.stderr)
        return 2
    problems = check(text, args.require)
    for problem in problems:
        print(f"{args.path}: {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
