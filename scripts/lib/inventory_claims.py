# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Which inventory records a TODO section claims to build (D02 T01 §18 and §22).

A section claims a record only on a blockquote line opening `> **Implements:**`, each backticked id on it one claim.
An id named anywhere else in the section (an example, a capture step, a test) claims nothing.
"""
import re

LINE = re.compile(r"^> \*\*Implements:\*\*(.*)$", re.M)
TICKED = re.compile(r"`([^`\s]+)`")


def claims(body: str) -> list:
    """The ids the section body claims, in the order its `Implements` lines name them."""
    out = []
    for line in LINE.findall(body or ""):
        out += TICKED.findall(line)
    return out


def implemented(sections) -> dict:
    """Each record id a verified section claims, with the references of the verified sections claiming it. A
    section the TODO graph does not read as verified (no stamp, however many items are ticked) claims nothing yet."""
    out = {}
    for section in sections:
        if section.done:
            for rid in claims(section.body):
                out.setdefault(rid, []).append(section.ref)
    return out


def owners(sections) -> dict:
    """Each record id any section claims, stamped or not, with the references of the sections claiming it: ownership
    is what the plan says, so an open section owns what it claims (D02 T01 §22). A section naming an id twice claims
    it once."""
    out = {}
    for section in sections:
        for rid in dict.fromkeys(claims(section.body)):
            out.setdefault(rid, []).append(section.ref)
    return out
