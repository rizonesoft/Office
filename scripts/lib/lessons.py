# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Read the lesson files of `docs/lessons/` (D00 T05 §1; the format is `docs/lessons/README.md`).

A lesson is frontmatter of flat `key: value` lines between two `---` lines, then a one-paragraph body. `read` refuses
what makes a file unreadable as a lesson: no frontmatter, a line that is not `key: value`, an unknown or duplicate
key, a missing required key, and an `id` that differs from the file name. The value rules (dates, roles, sources and
the rest) are `scripts/lessons.py check`'s, which reports them all in one run. Stdlib only.
"""
from pathlib import Path
import re

REQUIRED = ("id", "applies", "topics", "roles", "source", "added", "status")
OPTIONAL = ("fix", "retired_by")
KEYS = REQUIRED + OPTIONAL
LINE = re.compile(r"^([a-z_]+):(?:[ \t]+(.*?))?\s*$")


class LessonError(Exception):
    """A file that cannot be read as a lesson; the message names the file and the key."""


def lesson_files(folder):
    """The lesson files of `folder`: every `*.md` in it but the README; `triage/` and other folders are not read."""
    return sorted(p for p in Path(folder).glob("*.md") if p.is_file() and p.name.lower() != "readme.md")


def read(path):
    """{key: value, ..., "body": text} of the lesson at `path`; LessonError when it cannot be read as one."""
    path = Path(path)
    name = path.name
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise LessonError(f"{name}: cannot be read ({error})") from None
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        raise LessonError(f"{name}: no frontmatter (the first line must be ---)")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise LessonError(f"{name}: the frontmatter is not closed by a --- line") from None
    fields = {}
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip():
            continue
        match = LINE.match(line)
        if not match:
            raise LessonError(f"{name}: line {number} is not a flat key: value line")
        key, value = match[1], (match[2] or "").strip()
        if key not in KEYS:
            raise LessonError(f"{name}: unknown key {key!r}")
        if key in fields:
            raise LessonError(f"{name}: duplicate key {key!r}")
        fields[key] = value
    missing = [k for k in REQUIRED if k not in fields]
    if missing:
        raise LessonError(f"{name}: missing key {missing[0]!r}")
    if fields["id"] != path.stem:
        raise LessonError(f"{name}: id {fields['id']!r} differs from the file name {path.stem!r}")
    fields["body"] = "\n".join(lines[end + 1:]).strip()
    return fields


def items(value):
    """The comma-separated items of a field value, stripped, empty ones dropped."""
    return [part.strip() for part in value.split(",") if part.strip()]


def topics(readme):
    """The words the README's Topics list allows: each `- \\`word\\`` item under its `## Topics` heading."""
    words, inside = set(), False
    for line in Path(readme).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line.strip().lower() == "## topics"
            continue
        match = re.match(r"^- `([a-z0-9-]+)`", line)
        if inside and match:
            words.add(match[1])
    return words
