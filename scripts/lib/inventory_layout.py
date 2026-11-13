# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Layout blocks: where each child of an inventory record sits, as a TODO section carries it (D02 T01 §29).

A section that builds a parent's children (a group's controls, a menu's items, a tab's groups) carries one unit for
that parent, generated here and never typed by hand:

    **Layout:** `word.home.paragraph` (capture profile `fhd-100`)

    ```text
    order   id       label      type         size   x  y   width  height  keytip
    parent  .        Paragraph  group                      251    96      ZP
    0       bullets  Bullets    splitButton  small  8  10  39     24      U
    children  bullets  10  --layout word.home.paragraph.bullets
    ```

The unit is the `**Layout:**` line, a blank line and the fenced block. A row is one child, ordered by `order` and then
by id (a child with no `order` after those with one); its id is written from the parent's, and x and y are measured
from the parent's top left corner, so the block does not change when the window moves. A cell with no value is
blank. A `children` line names a child that is itself a parent, with the id to ask for its own block. No row starts
with a list marker, a quote mark or a backtick, so the TODO graph reads none of them as an item and no label can
close the fence.

`render` prints a unit, `units` finds the units a section holds, `check` compares every unit in the tree with the
inventory and names each section that claims a parent's children without that parent's unit, and `rewrite` puts the
generated unit in place of a stale one.
"""
import re

LINE = re.compile(r"^\*\*Layout:\*\* `([^`\n]*)`[^\n]*$", re.M)
OPEN, CLOSE = "```text", "```"
COLUMNS = ("order", "id", "label", "type", "size", "x", "y", "width", "height", "keytip")
STAMPED = ("the inventory changed after this section was stamped; a stamped section is never rewritten, so file the "
           "repair as a new section through add-todo and reopen this one with unstamp")


class Unknown(Exception):
    """An id the inventory does not hold, or one with no children."""


def index(records):
    """({id: record}, {parent id: [child records]}) over every record of the inventory, whichever app and file."""
    by_id, children = {}, {}
    for recs in records.values():
        for r in recs:
            if isinstance(r.get("id"), str):
                by_id[r["id"]] = r
    for r in by_id.values():
        if isinstance(r.get("parent"), str):
            children.setdefault(r["parent"], []).append(r)
    return by_id, children


def _ordered(kids):
    def key(r):
        order = r.get("order")
        has = isinstance(order, int) and not isinstance(order, bool)
        return (0, order, r["id"]) if has else (1, 0, r["id"])
    return sorted(kids, key=key)


def _cell(value):
    """A value as a cell: text with the characters that would break a row (a line break, a tab) written as a space."""
    if value is None or isinstance(value, bool):
        return ""
    return re.sub(r"\s", " ", str(value))


def _box(record):
    bounds = record.get("bounds")
    return bounds if isinstance(bounds, dict) and all(
        isinstance(bounds.get(k), int) and not isinstance(bounds.get(k), bool) for k in ("x", "y", "width", "height")
    ) else None


def render(by_id, children, parent_id):
    """The whole unit for `parent_id`: the same text for the same inventory. Raises Unknown."""
    parent = by_id.get(parent_id)
    if parent is None:
        raise Unknown(f"{parent_id} is not a record of the inventory")
    kids = _ordered(children.get(parent_id, []))
    if not kids:
        raise Unknown(f"{parent_id} has no children in the inventory")
    origin = _box(parent)
    rows = [COLUMNS, ("parent", ".", _cell(parent.get("label")), _cell(parent.get("kind")), "", "", "",
                      _cell(origin["width"]) if origin else "", _cell(origin["height"]) if origin else "",
                      _cell(parent.get("keytip")))]
    for kid in kids:
        box = _box(kid)
        relative = kid["id"][len(parent_id) + 1:] if kid["id"].startswith(parent_id + ".") else kid["id"]
        order = kid.get("order")
        rows.append((
            _cell(order) if isinstance(order, int) and not isinstance(order, bool) else "", relative,
            _cell(kid.get("label")), _cell(kid.get("controlType") or kid.get("kind")), _cell(kid.get("size")),
            _cell(box["x"] - origin["x"]) if box and origin else "",
            _cell(box["y"] - origin["y"]) if box and origin else "",
            _cell(box["width"]) if box else "", _cell(box["height"]) if box else "", _cell(kid.get("keytip"))))
    widths = [max(len(row[i]) for row in rows) for i in range(len(COLUMNS))]
    lines = ["  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip() for row in rows]
    for kid in kids:
        if children.get(kid["id"]):
            relative = kid["id"][len(parent_id) + 1:] if kid["id"].startswith(parent_id + ".") else kid["id"]
            lines.append(f"children  {relative}  {len(children[kid['id']])}  --layout {kid['id']}")
    profile = parent.get("captureProfile")
    profile = f"capture profile `{profile}`" if isinstance(profile, str) and profile else "no capture profile"
    return "\n".join([f"**Layout:** `{parent_id}` ({profile})", "", OPEN, *lines, CLOSE])


UNCLOSED = "has a block that is not closed before a blank line, another Layout line or another fence"


def units(body):
    """The units of a section body, in order: (parent id, start, end, problem). `body[start:end]` is the unit as the
    section holds it, from its `**Layout:**` line to its closing fence. A line with no fenced block after it, or a
    block that does not close, has a problem instead and ends at the line's own end.

    A block is rows and nothing else, so it ends at the first line that is its closing fence, and a blank line,
    another `**Layout:**` line or another fence before that means it was never closed: the search for the closing
    fence never runs on into the text after the block, where the next fence belongs to something else. A unit
    therefore never holds a line of the section that the generator did not write, which is what lets `rewrite`
    replace one without touching anything around it."""
    out, inside = [], 0
    for match in LINE.finditer(body):
        if match.start() < inside:
            continue  # a Layout line inside the block before it: that block is already refused as not closed
        rest = body[match.end():]
        opened = re.match(r"\n\n" + re.escape(OPEN) + r"\n", rest)
        if opened is None:
            out.append((match[1], match.start(), match.end(), "has no fenced `text` block after its Layout line"))
            continue
        at, closed = match.end() + opened.end(), None
        while at < len(body):
            stop = body.find("\n", at)
            stop = len(body) if stop == -1 else stop
            line = body[at:stop]
            if line.rstrip(" \t") == CLOSE:
                closed = at + len(CLOSE)
                break
            if not line.strip() or line.startswith(CLOSE) or LINE.match(line):
                break
            at = stop + 1
        if closed is None:
            out.append((match[1], match.start(), match.end(), UNCLOSED))
            inside = at  # nothing up to the line that interrupted it is read as another unit's start
            continue
        out.append((match[1], match.start(), closed, None))
        inside = closed
    return out


def problems_of(section, by_id, children, claimed):
    """The layout problems of one section, as (parent id, what is wrong) pairs: a unit that is malformed, names a
    parent the inventory lacks, is given twice, or differs from the inventory; and a parent whose children the
    section claims with no unit for it. `claimed` is the ids on its Implements lines."""
    found, seen = [], {}
    for parent_id, start, end, problem in units(section.body):
        seen[parent_id] = seen.get(parent_id, 0) + 1
        if seen[parent_id] == 2:
            found.append((parent_id, "has two layout blocks in this section"))
        if problem:
            found.append((parent_id, problem))
            continue
        try:
            generated = render(by_id, children, parent_id)
        except Unknown as exc:
            found.append((parent_id, f"cannot be laid out: {exc}"))
            continue
        if section.body[start:end] != generated:
            found.append((parent_id, "differs from the inventory" + (f": {STAMPED}" if section.done else
                                                                     "; print it again with --layout")))
    needed = {by_id[rid]["parent"] for rid in claimed
              if rid in by_id and isinstance(by_id[rid].get("parent"), str) and by_id[rid]["parent"] in by_id}
    for parent_id in sorted(needed - set(seen)):
        found.append((parent_id, "has children this section claims and no layout block here"
                      + (f": {STAMPED}" if section.done else "; add the block --layout prints")))
    return found


def rewrite(text, sections, by_id, children, section_text):
    """`text` (a TODO file, line endings as `\\n`) with every stale, well-formed unit of its open `sections` replaced
    by the generated one; (the new text, how many units changed). A stamped section, a malformed unit and a unit for
    a parent the inventory lacks are left as they are: the check names them."""
    changed = 0
    for section in sections:
        if section.done:
            continue
        body = section_text(text, section.number)
        if body is None:
            continue
        at = text.index(body)
        new, offset = body, 0
        for parent_id, start, end, problem in units(body):
            if problem:
                continue
            try:
                generated = render(by_id, children, parent_id)
            except Unknown:
                continue
            if body[start:end] != generated:
                new = new[:start + offset] + generated + new[end + offset:]
                offset += len(generated) - (end - start)
                changed += 1
        text = text[:at] + new + text[at + len(body):]
    return text, changed
