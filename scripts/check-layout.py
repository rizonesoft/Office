#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Compare what a built app shows with what the parity inventory records for one parent (D02 T01 §30).

    python scripts/check-layout.py --parent word.home.paragraph --capture <scratch>/write-home.json
    python scripts/check-layout.py --parent outlook.home.new --capture <file> --no-bounds
    python scripts/check-layout.py --parent word.home.font --capture <file> --tolerance 1

The plan's acceptance bar is that every element works in its app at its inventoried position. `--parent` is a record
of design/inventory/ (a tab, a group, a menu, a dialog); `--capture` is the JSON array of draft records
`scripts/capture-ui.py --out` writes for a window of the built app. The parent's children in the inventory are
compared with their counterparts in the capture, and each difference is one finding:

    missing     a record with no captured element
    extra       a captured element with no record (an improvement may add a control; it is listed and does not fail)
    renamed     the label differs
    retyped     the control type differs
    reordered   the child sits at another place among its siblings
    moved       its position from the parent's top left corner differs by more than --tolerance pixels (default 2)
    resized     its width or height differs by more than --tolerance pixels
    unmeasured  it, its counterpart or either parent has no bounds, so its position could not be compared

How the two sides are paired. The parent is found from the top of its branch, one level at a time: the inventory
parent's topmost ancestor with a captured record that has no parent, then each next ancestor among the captured
children of the pair above it. Several parents share a label and a type in different branches (Word's `Shadow`
menus), and only the branch tells them apart. At every level, and for the children themselves: a record with a
`uiaId` pairs with the captured record of the same `uiaId`; a record without one pairs by label and type
(`controlType`, or `kind` where it has none) with a captured record that has no `uiaId` either, and where several
siblings share that label and type they pair in order, first with first. The children left unpaired on both sides
are then paired a second time: by label alone (reported `retyped`), then between the same paired neighbours where
as many records as captured children are left and their types agree in order (reported `renamed`). A control with no
`uiaId` whose label and type both changed cannot be told from one removed and one added, and is reported as that.

Positions are compared at the record's capture profile: a captured element of another profile is refused. With
--no-bounds (a parent whose layout design/SPEC.md modernises: Outlook, Visio and Project) presence, label, type and
order are still compared, and positions are not.

The findings go to stderr and one line of counts to stdout. Exit 0 when nothing is missing, renamed, retyped,
reordered, moved, resized or unmeasured; 1 otherwise; 2 when an input cannot be read, the parent is not a record with
children, a level of its branch cannot be told apart in the capture, or a profile differs. Stdlib only.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import inventory_layout  # noqa: E402  (scripts/lib is put on the path just above)

FAILING = ("missing", "renamed", "retyped", "reordered", "moved", "resized", "unmeasured")
KINDS = ("missing", "extra") + FAILING[1:]


class Refused(Exception):
    """An input the comparison cannot run on: exit 2."""


def shown(text):
    """text with anything that is not printable written as an escape: labels and ids come from the two files."""
    return "".join(ch if ch.isprintable() else ascii(ch)[1:-1] for ch in str(text))


def report_script():
    """scripts/inventory-report.py as a module: its reader of the inventory is the one this script uses."""
    spec = importlib.util.spec_from_file_location("inventory_report_for_layout",
                                                  ROOT / "scripts" / "inventory-report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def kind_of(record):
    return record.get("controlType") or record.get("kind")


def key_of(record):
    return (record.get("label"), kind_of(record))


def in_order(records):
    """Siblings in their order: by `order`, then by id; a record with no `order` after those with one."""
    def key(r):
        order = r.get("order")
        has = isinstance(order, int) and not isinstance(order, bool)
        return (0, order, str(r.get("id"))) if has else (1, 0, str(r.get("id")))
    return sorted(records, key=key)


def pair_exact(records, captured):
    """Pairs by identity alone: the same `uiaId`, or the same label and type where neither side has a `uiaId`
    (several siblings sharing them pair in order). Returns (pairs, unpaired records, unpaired captured)."""
    records, captured = in_order(records), in_order(captured)
    pairs, left, taken = [], [], set()
    by_uia = {}
    for cap in captured:
        if cap.get("uiaId"):
            by_uia.setdefault(cap["uiaId"], []).append(cap)
    by_key = {}
    for cap in captured:
        if not cap.get("uiaId"):
            by_key.setdefault(key_of(cap), []).append(cap)
    for rec in records:
        pool = by_uia.get(rec["uiaId"], []) if rec.get("uiaId") else by_key.get(key_of(rec), [])
        if pool:
            cap = pool.pop(0)
            taken.add(id(cap))
            pairs.append((rec, cap))
        else:
            left.append(rec)
    return pairs, left, [cap for cap in captured if id(cap) not in taken]


def pair_children(records, captured):
    """Every pair of the parent's children with its captured counterpart, the second chances included, and what is
    left: (pairs, missing records, extra captured). A pair made by label alone differs in type, and one made by its
    place differs in label, which the comparison then reports."""
    pairs, left, spare = pair_exact(records, captured)
    # Second chance, by label alone: a record with no uiaId whose type changed.
    by_label = {}
    for cap in spare:
        if not cap.get("uiaId"):
            by_label.setdefault(cap.get("label"), []).append(cap)
    still = []
    for rec in left:
        pool = by_label.get(rec.get("label"), []) if not rec.get("uiaId") else []
        if pool:
            pairs.append((rec, pool.pop(0)))
        else:
            still.append(rec)
    used = {id(cap) for _, cap in pairs}
    spare = [cap for cap in spare if id(cap) not in used]
    # Second chance, by place: between the same paired neighbours, as many records as captured children are left
    # and their types agree in order. Only records and captured children with no uiaId: an id is an identity.
    partner = {id(rec): cap for rec, cap in pairs}
    counterpart = {id(cap): rec for rec, cap in pairs}

    def gaps(sequence, paired, name):
        """Each unpaired item of `sequence` under the pair that precedes it (None before the first)."""
        out, before = {}, None
        for item in sequence:
            if id(item) in paired:
                before = name(paired[id(item)]) if name else id(item)
            else:
                out.setdefault(before, []).append(item)
        return out
    record_gaps = gaps(in_order(records), partner, lambda cap: id(cap))
    capture_gaps = gaps(in_order(captured), counterpart, None)
    missing, extra_ids = [], {id(cap) for cap in spare}
    for before, recs in record_gaps.items():
        recs = [rec for rec in recs if any(rec is s for s in still)]
        caps = [cap for cap in capture_gaps.get(before, []) if id(cap) in extra_ids]
        open_recs = [rec for rec in recs if not rec.get("uiaId")]
        open_caps = [cap for cap in caps if not cap.get("uiaId")]
        whole = len(open_recs) == len(recs) and len(open_caps) == len(caps)
        if open_recs and whole and len(open_recs) == len(open_caps) \
                and all(kind_of(rec) == kind_of(cap) for rec, cap in zip(open_recs, open_caps)):
            for rec, cap in zip(open_recs, open_caps):
                pairs.append((rec, cap))
                extra_ids.discard(id(cap))
        else:
            missing += recs
    return pairs, missing, [cap for cap in spare if id(cap) in extra_ids]


def box(record):
    bounds = record.get("bounds")
    ok = isinstance(bounds, dict) and all(isinstance(bounds.get(k), int) and not isinstance(bounds.get(k), bool)
                                           for k in ("x", "y", "width", "height"))
    return bounds if ok else None


def out_of_place(pairs):
    """The pairs that sit at another place among their siblings: the fewest whose removal leaves the inventory's
    sequence and the capture's the same (every pair outside a longest run that keeps its order)."""
    by_record = in_order([rec for rec, _ in pairs])
    rank = {id(cap): n for n, cap in enumerate(in_order([cap for _, cap in pairs]))}
    partner = {id(rec): cap for rec, cap in pairs}
    sequence = [rank[id(partner[id(rec)])] for rec in by_record]
    best, previous = [1] * len(sequence), [-1] * len(sequence)
    for i in range(len(sequence)):
        for j in range(i):
            if sequence[j] < sequence[i] and best[j] + 1 > best[i]:
                best[i], previous[i] = best[j] + 1, j
    keep, at = set(), max(range(len(sequence)), key=lambda i: best[i]) if sequence else -1
    while at != -1:
        keep.add(at)
        at = previous[at]
    return [(by_record[i], i, sequence[i]) for i in range(len(sequence)) if i not in keep]


def find_parent(parent_id, by_id, children, captured_children):
    """The capture's counterpart of the inventory record `parent_id`, found from the top of its branch. Returns it,
    or the id of the first level the capture does not hold. Raises Refused for a level that cannot be told apart."""
    chain, at = [], by_id[parent_id]
    while at is not None:
        chain.append(at)
        at = by_id.get(at.get("parent")) if isinstance(at.get("parent"), str) else None
    above_record, above_capture = None, None
    for level in reversed(chain):
        siblings = children.get(above_record["id"], []) if above_record else [r for r in by_id.values()
                                                                             if not isinstance(r.get("parent"), str)
                                                                             and r.get("app") == level.get("app")]
        candidates = captured_children.get(above_capture.get("id") if above_capture else None, [])
        if not level.get("uiaId"):
            alike = [r for r in siblings if not r.get("uiaId") and key_of(r) == key_of(level)]
            alike_captured = [c for c in candidates if not c.get("uiaId") and key_of(c) == key_of(level)]
            if len(alike) > 1 and len(alike_captured) and len(alike) != len(alike_captured):
                raise Refused(f"{shown(level['id'])} cannot be told apart in the capture: {len(alike)} siblings in "
                              f"the inventory share its label and type, and {len(alike_captured)} captured ones do")
        pairs, _, _ = pair_exact(siblings, candidates)
        found = next((cap for rec, cap in pairs if rec is level), None)
        if found is None:
            return level["id"]
        above_record, above_capture = level, found
    return above_capture


def compare(parent_id, by_id, children, capture, tolerance=2, bounds=True):
    """The findings for one parent: a list of (kind, id, what) and the counts line's numbers. Raises Refused."""
    if parent_id not in by_id:
        raise Refused(f"--parent {shown(parent_id)} is not a record of the inventory")
    records = children.get(parent_id, [])
    if not records:
        raise Refused(f"--parent {shown(parent_id)} has no children in the inventory")
    captured_children = {}
    for cap in capture:
        captured_children.setdefault(cap.get("parent") if isinstance(cap.get("parent"), str) else None, []).append(cap)
    parent = by_id[parent_id]
    found = find_parent(parent_id, by_id, children, captured_children)
    if isinstance(found, str):
        what = "it" if found == parent_id else f"its ancestor {shown(found)}"
        return [("missing", parent_id, f"the capture does not hold {what}, so nothing under it was compared")], 0
    captured = captured_children.get(found.get("id"), [])
    pairs, missing, extra = pair_children(records, captured)
    findings = [("missing", rec["id"], f"no captured element for {shown(repr(rec.get('label')))} "
                                       f"({shown(kind_of(rec))})") for rec in in_order(missing)]
    findings += [("extra", str(cap.get("id")), f"{shown(repr(cap.get('label')))} ({shown(kind_of(cap))}) is in the "
                                               f"capture and not in the inventory") for cap in in_order(extra)]
    ordered = sorted(pairs, key=lambda pair: in_order([rec for rec, _ in pairs]).index(pair[0]))
    for rec, cap in ordered:
        if rec.get("label") != cap.get("label"):
            findings.append(("renamed", rec["id"], f"{shown(repr(rec.get('label')))} in the inventory, "
                                                   f"{shown(repr(cap.get('label')))} in the capture"))
        if kind_of(rec) != kind_of(cap):
            findings.append(("retyped", rec["id"], f"{shown(kind_of(rec))} in the inventory, {shown(kind_of(cap))} in "
                                                   f"the capture"))
    for rec, was, now in out_of_place(pairs):
        findings.append(("reordered", rec["id"], f"place {was + 1} of {len(pairs)} paired children in the inventory, "
                                                 f"place {now + 1} in the capture"))
    if bounds:
        here, there = box(parent), box(found)
        for rec, cap in ordered:
            for side in (cap, found):
                if isinstance(rec.get("captureProfile"), str) and isinstance(side.get("captureProfile"), str) \
                        and rec["captureProfile"] != side["captureProfile"]:
                    raise Refused(f"the capture is at profile {shown(side['captureProfile'])} and "
                                  f"{shown(rec['id'])} was recorded at {shown(rec['captureProfile'])}; capture at the "
                                  f"record's profile, or compare without positions (--no-bounds)")
            mine, theirs = box(rec), box(cap)
            lacking = [name for name, value in (("the record", mine), ("the captured element", theirs),
                                                ("the inventory's parent", here), ("the captured parent", there))
                       if value is None]
            if lacking:
                findings.append(("unmeasured", rec["id"], f"no bounds on {' and '.join(lacking)}"))
                continue
            was = (mine["x"] - here["x"], mine["y"] - here["y"], mine["width"], mine["height"])
            now = (theirs["x"] - there["x"], theirs["y"] - there["y"], theirs["width"], theirs["height"])
            both = f"x {was[0]}, y {was[1]}, {was[2]} by {was[3]} in the inventory; x {now[0]}, y {now[1]}, " \
                   f"{now[2]} by {now[3]} in the capture"
            if abs(was[0] - now[0]) > tolerance or abs(was[1] - now[1]) > tolerance:
                findings.append(("moved", rec["id"], both))
            if abs(was[2] - now[2]) > tolerance or abs(was[3] - now[3]) > tolerance:
                findings.append(("resized", rec["id"], both))
    return findings, len(pairs)


def load_capture(path):
    try:
        data = json.loads(Path(path).read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise Refused(f"--capture {shown(path)} cannot be read ({exc})") from None
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise Refused(f"--capture {shown(path)} is not a JSON array of records, as scripts/capture-ui.py --out writes")
    return data


def main(argv=None, root=ROOT):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--parent", required=True, help="the inventory record whose children are compared")
    ap.add_argument("--capture", required=True, type=Path, help="the records scripts/capture-ui.py --out wrote")
    ap.add_argument("--tolerance", default="2", help="pixels a position or a size may differ by (default 2)")
    ap.add_argument("--no-bounds", action="store_true", help="compare presence, label, type and order only")
    args = ap.parse_args(argv)
    try:
        if not (args.tolerance.isascii() and args.tolerance.isdigit()):
            raise Refused(f"--tolerance {shown(args.tolerance)} is not a whole number of pixels from 0 up")
        report = report_script()
        try:
            records, _ = report.load_inventory(root)
        except (report.Unreadable, OSError) as exc:
            raise Refused(f"the inventory cannot be read ({exc})") from None
        by_id, children = inventory_layout.index(records)
        findings, paired = compare(args.parent, by_id, children, load_capture(args.capture),
                                   int(args.tolerance), not args.no_bounds)
    except Refused as exc:
        print(f"check-layout: {exc}", file=sys.stderr)
        return 2
    counts = {kind: sum(1 for found in findings if found[0] == kind) for kind in KINDS}
    code = 1 if any(counts[kind] for kind in FAILING) else 0
    total = len(children.get(args.parent, []))
    # The verdict is decided; the findings go out first, and nothing that happens to stdout changes it.
    for kind, rid, what in findings:
        print(f"{kind} {shown(rid)}: {what}", file=sys.stderr)
    summary = f"{shown(args.parent)}: {total} children, {paired} paired, " + ", ".join(
        f"{counts[kind]} {kind}" for kind in KINDS)
    return report.finish(code, [summary], [])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
