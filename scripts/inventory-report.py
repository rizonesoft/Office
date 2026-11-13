#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The parity scoreboard: what design/inventory/ records per app and kind, how much of it verified sections build,
and how each app's baseline compares with its captured inventory (D02 T01 §18).

    python scripts/inventory-report.py                      # prints the report and writes design/inventory/COVERAGE.md
    python scripts/inventory-report.py --check              # exit 1 when the committed COVERAGE.md is stale
    python scripts/inventory-report.py --missing [--app A]  # the baseline idMsos no captured record matches
    python scripts/inventory-report.py --app A --kind K     # counts for one app and kind (prints only)
    python scripts/inventory-report.py --app word --kind tab --cited-in F [--control-types]
    python scripts/inventory-report.py --owners [--app A]   # who builds each record: state and counts, unowned ids
    python scripts/inventory-report.py --owners --check [--all] [--app A]   # exit 1 on a record nobody owns
    python scripts/inventory-report.py --layout word.home.paragraph        # the layout block of a parent's children
    python scripts/inventory-report.py --layout-check [--write TODO-FILE]  # exit 1 on a stale or missing block

Records are counted per app (the shell counts as one) and `kind`; a record is implemented when a verified TODO
section claims it on a `> **Implements:**` line (scripts/lib/inventory_claims.py). A baseline row is one
occurrence of an `idMso` on its `tab` (a row with no `idMso` is counted apart, since nothing can match it): on a
tab or Backstage page the inventory captured, it is captured when a record with its `idMso` sits under that page's
record, documented absent when REFERENCE.md lists it
(scripts/lib/word_absences.py), and unmatched otherwise. A row on no tab is captured when any record of the app or
the shell holds its `idMso`; otherwise a Quick Access Toolbar row is unmatched and a row of any other placement is
counted as pending until its surface is captured. An app with a baseline
and no captured record is one `pending inventory` row. The report holds no value of the run, so writing it twice
gives the same bytes. A filtered run (--app, --kind, --cited-in, --missing) only prints. Exit 0 written or printed;
1 when --check finds the report stale or a write fails; 2 when an input cannot be read.

Ownership (--owners, D02 T01 §22): parity is 1:1, so every record is built by exactly the section that claims it on
a `> **Implements:**` line, open or stamped. Each app (the shell counts as one) is in one of three states:
`pending inventory` (no captured record), `pending authoring` (captured records, and the section that authors the
app's domain, named in design/inventory/authoring.json, not yet stamped) and `enforced` (that section stamped).
--owners prints each app's state with its owned and total counts, the counts per kind, and every unowned id.
--owners --check exits 1 when an enforced app has a record nobody owns, when a claim names an id the inventory does
not hold, when two sections claim one id, or when a section claims an excluded record; a pending app's unowned
records are counted, not refused. An excluded record (`disposition`, D02 T01 §28) is built by nobody: it needs no
owner and is counted apart on its app's line. --all holds
every app as enforced, so an app with no captured record is refused too: the gate for a finished plan. --app takes
one app, and with --owners refuses a name that is no app folder. Refusals go to stderr, states and counts to stdout.

Layout (--layout, --layout-check, D02 T01 §29): a section that builds a parent's children carries that parent's
layout block, which scripts/lib/inventory_layout.py generates and describes. --layout prints the block for one
parent (exit 2 for an id the inventory lacks or one with no children). --layout-check compares every block in the
TODO tree with the inventory, the `**Layout:**` line included, and names each section whose block differs, is
malformed or given twice, and each section that claims a parent's children without that parent's block: exit 1.
--write, with --layout-check, first replaces the stale blocks of the named TODO file's open sections with the
generated ones (through a temporary file; a stamped section is never touched), then checks.
"""
import argparse
import errno
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import inventory_authoring  # noqa: E402  (scripts/lib is put on the path just above)
import inventory_claims  # noqa: E402
import inventory_layout  # noqa: E402
import todo_graph  # noqa: E402
import word_absences  # noqa: E402

REPORT = Path("design") / "inventory" / "COVERAGE.md"
DISPOSITIONS = ("build", "equivalent", "excluded")  # design/inventory/schema.json, `disposition` (D02 T01 §28)
SURFACES = ("tab", "contextualTab", "backstagePage")  # the records a baseline row's `tab` names
ID_CHAR = r"A-Za-z0-9_\-"


class Unreadable(Exception):
    """An input the report cannot read."""


def load_inventory(root):
    """{app: [records]} from design/inventory/<app>/*.json, and {app: [baseline rows as dicts]}."""
    inventory = Path(root) / "design" / "inventory"
    records, baselines = {}, {}
    for folder in sorted(p for p in inventory.iterdir() if p.is_dir()):
        for f in sorted(folder.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise Unreadable(f"{f}: {exc}") from None
            if f.name == "baseline.json":
                if not isinstance(data, dict) or not isinstance(data.get("columns"), list):
                    raise Unreadable(f"{f}: not a baseline")
                baselines[folder.name] = [dict(zip(data["columns"], row)) for row in data.get("rows", [])]
            elif isinstance(data, list):
                records.setdefault(folder.name, []).extend(r for r in data if isinstance(r, dict))
            else:
                raise Unreadable(f"{f}: not a list of records")
    return records, baselines


def disposition(record):
    """What we do with a record: `build` when it carries no `disposition` (the schema's default). A value the schema
    does not allow is a file the checker refuses, and the report does not guess what it meant."""
    value = record.get("disposition", "build")
    if value not in DISPOSITIONS:
        raise Unreadable(f"{shown(record.get('id'))}: disposition {shown(repr(value))} is not one of "
                         f"{', '.join(DISPOSITIONS)}; run python scripts/check-inventory.py")
    return value


def surface_of(records):
    """Each record id with the idMso of the tab or Backstage page it sits under (itself, for a page)."""
    by_id = {r.get("id"): r for r in records if isinstance(r.get("id"), str)}
    out = {}
    for rid in by_id:
        seen, cur = set(), by_id[rid]
        while cur is not None and cur.get("id") not in seen:
            seen.add(cur.get("id"))
            if cur.get("kind") in SURFACES:
                out[rid] = cur.get("idMso")
                break
            cur = by_id.get(cur.get("parent"))
    return out


def baseline_counts(app, rows, app_records, shell_records):
    """(counts, unmatched rows, pending rows per placement) for one app's baseline against its inventory."""
    absent = word_absences.documented(app)
    surfaces = {r["idMso"] for r in app_records if r.get("kind") in SURFACES and r.get("idMso")}
    under = surface_of(app_records)
    held = {}  # (idMso, surface idMso) for every record with an idMso
    for r in app_records:
        if r.get("idMso"):
            held.setdefault((r["idMso"], under.get(r.get("id"))), True)
    anywhere = {r["idMso"] for r in app_records + shell_records if r.get("idMso")}
    counts = {"rows": 0, "captured": 0, "absent": 0, "unmatched": 0, "pending": 0, "unidentified": 0}
    unmatched, pending = [], {}
    for row in rows:
        mso, tab, placement = row.get("idMso"), row.get("tab"), row.get("placement")
        counts["rows"] += 1
        if not mso:
            state = "unidentified"  # the baseline names no idMso for it, so no record can match it
        elif row.get("controlType") == "tab":
            state = "captured" if mso in surfaces else "absent" if mso in absent else "unmatched"
        elif tab and tab in surfaces:
            state = "captured" if (mso, tab) in held else "absent" if mso in absent else "unmatched"
        elif tab and tab in absent:
            state = "absent"  # a row on a tab the reconciliation documents as absent
        elif not tab and mso in anywhere:
            state = "captured"  # a row on no tab matches any record of the app or the shell holding its idMso
        elif not tab and placement == "quickAccessToolbar":
            state = "unmatched"
        else:
            state = "pending"
            pending[placement or "none"] = pending.get(placement or "none", 0) + 1
        counts[state] += 1
        if state == "unmatched":
            unmatched.append(row)
    return counts, unmatched, pending


def read_sections(root):
    try:
        return list(todo_graph.graph(root).values())
    except todo_graph.Refused as exc:
        raise Unreadable(f"the TODO tree: {exc}") from None


def gather(root):
    records, baselines = load_inventory(root)
    implemented = inventory_claims.implemented(read_sections(root))
    return records, baselines, implemented


OWNERS_SHOWN = 50  # unowned ids a refusal names for one app before counting the rest


def stop_writing():
    """Point stdout at the null device, so what it still holds is dropped quietly now and when Python flushes it at
    exit, instead of failing a second time there (which would replace the exit code with Python's own 120)."""
    try:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    except (OSError, ValueError, AttributeError):  # stdout is not a real file: a stand-in with no descriptor
        sys.stdout = open(os.devnull, "w", encoding="utf-8")


def shown(text):
    """text with anything that is not printable written as an escape: a claim is whatever a TODO file backticked."""
    return "".join(ch if ch.isprintable() else ascii(ch)[1:-1] for ch in str(text))


def ownership(root, records, sections, app=None):
    """Who the plan says builds each record (D02 T01 §22): (one row per app, the unknown claims, the double claims,
    the claims of excluded records). A row is (app, state, its authoring section's reference, {kind: [owned ids,
    unowned ids]}, the excluded ids). An excluded record (D02 T01 §28) is built by nobody: it is outside the owned
    and unowned ids, and a claim of it is a wrong claim in every state. The states are in the module's description.
    An unknown, double or excluded claim belongs to the app its first dotted part names. Raises Unreadable for an
    authoring file the reader refuses and for an `app` that is no app folder."""
    inventory = Path(root) / "design" / "inventory"
    by_ref = {section.ref: section for section in sections}
    authoring, problems = inventory_authoring.read(inventory, lambda ref: ref in by_ref)
    if problems:
        raise Unreadable("\n".join(problems))
    apps = inventory_authoring.app_folders(inventory)
    if app is not None and app not in apps:
        raise Unreadable(f"--app {shown(app)} is not an app folder of the inventory ({', '.join(apps)})")
    claimed = inventory_claims.owners(sections)
    held = {r["id"] for recs in records.values() for r in recs if isinstance(r.get("id"), str)}
    left_out = {r["id"] for recs in records.values() for r in recs
                if isinstance(r.get("id"), str) and disposition(r) == "excluded"}
    mine = (lambda rid: app is None or rid.split(".", 1)[0] == app)
    unknown = sorted((rid, refs) for rid, refs in claimed.items() if rid not in held and mine(rid))
    doubled = sorted((rid, refs) for rid, refs in claimed.items() if len(refs) > 1 and mine(rid))
    excluded = sorted((rid, refs) for rid, refs in claimed.items() if rid in left_out and mine(rid))
    rows = []
    for name in apps if app is None else [app]:
        kinds, captured, out = {}, False, set()
        for r in records.get(name, []):
            if isinstance(r.get("id"), str):
                captured = True
                if r["id"] in left_out:
                    out.add(r["id"])
                else:
                    kinds.setdefault(str(r.get("kind")), set()).add(r["id"])
        section = by_ref[authoring[name]]
        state = "pending inventory" if not captured else "enforced" if section.done else "pending authoring"
        rows.append((name, state, section.ref, {kind: [sorted(i for i in ids if i in claimed),
                                                      sorted(i for i in ids if i not in claimed)]
                                                for kind, ids in sorted(kinds.items())}, sorted(out)))
    return rows, unknown, doubled, excluded


def owners_report(root, app=None, check=False, hold_all=False):
    """The ownership report, decided before a line of it is written: (the exit code, 0 or 1 when `check` finds a
    refusal; the lines for stdout, states and counts; the lines for stderr, refusals). Nothing is printed here, so
    the verdict cannot depend on whether its reader is still listening."""
    out, err = [], []
    records, _ = load_inventory(root)
    rows, unknown, doubled, excluded = ownership(root, records, read_sections(root), app)
    refusals = 0
    for name, state, ref, kinds, left_out in rows:
        owned = sum(len(pair[0]) for pair in kinds.values())
        unowned = [(kind, rid) for kind, pair in kinds.items() for rid in pair[1]]
        if state == "pending inventory":
            out.append(f"{name}: pending inventory (no captured record; {ref} authors it)")
        else:
            waits = "is stamped" if state == "enforced" else "is open"
            out.append(f"{name}: {state} ({ref} {waits}): {owned} of {owned + len(unowned)} records owned"
                       + (f", {len(left_out)} excluded" if left_out else ""))
            for kind, pair in kinds.items():
                out.append(f"  {kind}: {len(pair[0])} of {len(pair[0]) + len(pair[1])}")
        held_to = hold_all or state == "enforced"
        if check and held_to and state == "pending inventory":
            refusals += 1
            err.append(f"refused: {name} has no captured record, and --all holds every app")
        elif check and held_to and unowned:
            refusals += 1
            err.append(f"refused: {name}: {len(unowned)} record(s) no section claims on an Implements line")
            for kind, rid in unowned[:OWNERS_SHOWN]:
                err.append(f"  unowned {kind} {shown(rid)}")
            if len(unowned) > OWNERS_SHOWN:
                err.append(f"  and {len(unowned) - OWNERS_SHOWN} more")
        elif not check:
            for kind, rid in unowned:
                out.append(f"  unowned {kind} {shown(rid)}")
    for rid, refs in unknown:
        refusals += 1
        (err if check else out).append(f"{'refused: ' if check else ''}unknown claim: {shown(rid)}, claimed by "
                                       f"{', '.join(refs)}, is not a record of the inventory")
    for rid, refs in doubled:
        refusals += 1
        (err if check else out).append(f"{'refused: ' if check else ''}double claim: {shown(rid)} is claimed by "
                                       f"{' and '.join(refs)}")
    for rid, refs in excluded:
        refusals += 1
        (err if check else out).append(f"{'refused: ' if check else ''}excluded claim: {shown(rid)} is excluded, and "
                                       f"{', '.join(refs)} claims it")
    return (1 if check and refusals else 0), out, err


LAYOUT_SHOWN = 50  # layout problems named for one section before the rest are counted


def layout_check(root, write_path=None, write=todo_graph.atomic):
    """Every layout block of the TODO tree against the inventory (D02 T01 §29), decided before a line is written:
    (the exit code, the lines for stdout, the lines for stderr). With `write_path`, the stale blocks of that TODO
    file's open sections are replaced first; a write that fails leaves the file as it was and is a refusal."""
    out, err, refusals = [], [], 0
    records, _ = load_inventory(root)
    by_id, children = inventory_layout.index(records)
    sections = read_sections(root)
    bodies = {section.ref: section.body for section in sections}
    if write_path is not None:
        target = Path(write_path)
        target = target if target.is_absolute() else Path(root) / target
        try:
            relative = target.resolve().relative_to(Path(root).resolve()).as_posix()
        except ValueError:
            relative = None
        mine = [section for section in sections if section.path == relative]
        if not mine:
            raise Unreadable(f"--write {shown(write_path)} is not a TODO file of this tree "
                             f"(todo/<NN-domain>/TODO-NN-<name>.md)")
        raw = target.read_bytes()
        text = raw.decode("utf-8")
        windows = "\r\n" in text
        new, changed = inventory_layout.rewrite(text.replace("\r\n", "\n"), mine, by_id, children,
                                                todo_graph.section_text)
        if changed:
            try:
                write(target, new.replace("\n", "\r\n") if windows else new)
            except OSError as exc:
                refusals += 1
                err.append(f"refused: {relative} was not written ({exc}); it is as it was")
            else:
                out.append(f"{relative}: {changed} layout block(s) rewritten")
                for section in mine:  # what the file holds now is what is checked below
                    bodies[section.ref] = todo_graph.section_text(new, section.number) or ""
    blocks = 0
    for section in sections:
        body = bodies[section.ref]
        now = type(section)(**{**vars(section), "body": body}) if body is not section.body else section
        blocks += len(inventory_layout.units(body))
        found = inventory_layout.problems_of(now, by_id, children, inventory_claims.claims(body))
        refusals += len(found)
        for parent_id, wrong in found[:LAYOUT_SHOWN]:
            err.append(f"refused: {section.ref}: the layout of `{shown(parent_id)}` {wrong}")
        if len(found) > LAYOUT_SHOWN:
            err.append(f"refused: {section.ref}: and {len(found) - LAYOUT_SHOWN} more layout problems")
    out.append(f"layout blocks: {blocks} checked in {len(sections)} sections, {refusals} problem(s)")
    return (1 if refusals else 0), out, err


def finish(code, lines, refusals):
    """Write a decided result: the refusals to stderr first, then the lines to stdout, and return the exit code. No
    failure of stdout can improve the code: a reader that stopped listening (a broken pipe, which Windows reports as
    an invalid argument) only ends the writing; anything else (a full disk) is a result that was not written."""
    for line in refusals:
        print(line, file=sys.stderr)
    try:
        for line in lines:
            print(line)
        sys.stdout.flush()
    except OSError as exc:
        gone = isinstance(exc, BrokenPipeError) or exc.errno == errno.EPIPE or (
            os.name == "nt" and exc.errno == errno.EINVAL)
        stop_writing()
        if not gone:
            print(f"inventory-report: the report could not be written ({exc})", file=sys.stderr)
            return code or 1
    return code


def render(records, baselines, implemented):
    """COVERAGE.md: the whole scoreboard, the same bytes for the same inputs."""
    lines = ["# Inventory Coverage", "",
             "Generated by `python scripts/inventory-report.py` from `design/inventory/` and the TODO tree; run it "
             "again after either changes (the pre-commit hook refuses a stale copy). Definitions: "
             "`scripts/inventory-report.py`.", "", "## Records", "",
             "| App | Kind | Records | Implemented |", "| --- | --- | ---: | ---: |"]
    for app in sorted(records):
        kinds = {}
        for r in records[app]:
            kinds.setdefault(str(r.get("kind")), []).append(r.get("id"))
        for kind in sorted(kinds):
            ids = kinds[kind]
            lines.append(f"| {app} | {kind} | {len(ids)} | {sum(1 for i in set(ids) if i in implemented)} |")
    lines += ["", "## Dispositions", "",
              "What we do with each record (owner decision 6): build it as captured, build an equivalent of our own "
              "for a control that depends on a Microsoft cloud service, or exclude it. Accounted for: the build and "
              "equivalent records a verified section implements, and every excluded record.", "",
              "| App | Build | Equivalent | Excluded | Accounted for |", "| --- | ---: | ---: | ---: | ---: |"]
    for app in sorted(records):
        by = {name: set() for name in DISPOSITIONS}
        for r in records[app]:
            if isinstance(r.get("id"), str):
                by[disposition(r)].add(r["id"])
        accounted = len(by["excluded"]) + sum(1 for rid in by["build"] | by["equivalent"] if rid in implemented)
        lines.append(f"| {app} | {len(by['build'])} | {len(by['equivalent'])} | {len(by['excluded'])} | {accounted} |")
    lines += ["", "## Baseline", "",
              "| App | Rows | Captured | Documented absent | Unmatched | Pending surface | No idMso |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    pending_rows = []
    for app in sorted(baselines):
        if app not in records:
            continue
        counts, _, pending = baseline_counts(app, baselines[app], records[app], records.get("shell", []))
        lines.append(f"| {app} | {counts['rows']} | {counts['captured']} | {counts['absent']} | "
                     f"{counts['unmatched']} | {counts['pending']} | {counts['unidentified']} |")
        pending_rows += [(app, placement, n) for placement, n in sorted(pending.items())]
    if pending_rows:
        lines += ["", "## Pending Surfaces", "", "Baseline rows on a surface no capture has recorded yet.", "",
                  "| App | Placement | Rows |", "| --- | --- | ---: |"]
        lines += [f"| {app} | {placement} | {n} |" for app, placement, n in pending_rows]
    waiting = [app for app in sorted(baselines) if app not in records]
    if waiting:
        lines += ["", "## Pending Inventory", "", "Apps with a baseline and no captured record.", "",
                  "| App | Baseline rows | State |", "| --- | ---: | --- |"]
        lines += [f"| {app} | {len(baselines[app])} | pending inventory |" for app in waiting]
    return "\n".join(lines) + "\n"


def cited(text, rid):
    """Whether `rid` appears in `text` as a whole token: no id character on either side (a sentence's full stop
    after it is not part of it)."""
    return re.search(rf"(?<![{ID_CHAR}.]){re.escape(rid)}(?![{ID_CHAR}]|\.[{ID_CHAR}])", text) is not None


def main(argv=None, root=ROOT, write=todo_graph.atomic):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 when the committed COVERAGE.md is stale")
    ap.add_argument("--missing", action="store_true", help="print the baseline idMsos no captured record matches")
    ap.add_argument("--app")
    ap.add_argument("--kind")
    ap.add_argument("--cited-in", type=Path, help="the share of matching record ids this file names")
    ap.add_argument("--control-types", action="store_true", help="with --cited-in: cited and not, per controlType")
    ap.add_argument("--owners", action="store_true", help="who builds each record; with --check, exit 1 on a refusal")
    ap.add_argument("--all", action="store_true", help="with --owners --check: hold every app as enforced")
    ap.add_argument("--layout", metavar="PARENT", help="print the layout block of this record's children")
    ap.add_argument("--layout-check", action="store_true", help="exit 1 when a layout block is stale or missing")
    ap.add_argument("--write", type=Path, metavar="TODO-FILE",
                    help="with --layout-check: first rewrite the stale blocks of this file's open sections")
    args = ap.parse_args(argv)
    root = Path(root)
    if args.layout is not None or args.layout_check or args.write is not None:
        others = (args.check or args.missing or args.app or args.kind or args.cited_in or args.control_types
                  or args.owners or args.all)
        if others or (args.layout is not None and args.layout_check):
            print("inventory-report: --layout and --layout-check each stand alone (--write goes with --layout-check)",
                  file=sys.stderr)
            return 2
        if args.write is not None and not args.layout_check:
            print("inventory-report: --write goes with --layout-check", file=sys.stderr)
            return 2
        try:
            if args.layout is not None:
                records, _ = load_inventory(root)
                by_id, children = inventory_layout.index(records)
                try:
                    code, lines, refusals = 0, [inventory_layout.render(by_id, children, args.layout)], []
                except inventory_layout.Unknown as exc:
                    raise Unreadable(f"--layout: {shown(exc)}") from None
            else:
                code, lines, refusals = layout_check(root, args.write, write)
        except (Unreadable, OSError, UnicodeDecodeError) as exc:
            print(f"inventory-report: {exc}", file=sys.stderr)
            return 2
        return finish(code, lines, refusals)
    if args.all and not (args.owners and args.check):
        print("inventory-report: --all goes with --owners --check", file=sys.stderr)
        return 2
    if args.owners:
        if args.missing or args.kind or args.cited_in or args.control_types:
            print("inventory-report: --owners takes --check, --all and --app only", file=sys.stderr)
            return 2
        try:
            code, lines, refusals = owners_report(root, args.app, args.check, args.all)
        except (Unreadable, OSError, UnicodeDecodeError) as exc:
            print(f"inventory-report: {exc}", file=sys.stderr)
            return 2
        return finish(code, lines, refusals)  # the verdict is decided; nothing that happens to stdout changes it
    try:
        records, baselines, implemented = gather(root)
        text = args.cited_in.read_text(encoding="utf-8") if args.cited_in else None
    except (Unreadable, OSError, UnicodeDecodeError) as exc:
        print(f"inventory-report: {exc}", file=sys.stderr)
        return 2
    if args.missing:
        for app in sorted(baselines):
            if app in records and (not args.app or app == args.app):
                _, unmatched, _ = baseline_counts(app, baselines[app], records[app], records.get("shell", []))
                for row in unmatched:
                    print(f"{app}\t{row.get('idMso')}\t{row.get('controlType')}\t{row.get('tab') or ''}")
        return 0
    if args.app or args.kind or args.cited_in:
        matching = [r for app, recs in records.items() if not args.app or app == args.app
                    for r in recs if not args.kind or r.get("kind") == args.kind]
        ids = sorted({r["id"] for r in matching if isinstance(r.get("id"), str)})
        done = sum(1 for i in ids if i in implemented)
        print(f"{args.app or 'all apps'} {args.kind or 'all kinds'}: {len(ids)} records, {done} implemented")
        if text is not None:
            hit = [i for i in ids if cited(text, i)]
            share = f"{100 * len(hit) / len(ids):.0f} percent" if ids else "no matching record"
            print(f"cited in {args.cited_in}: {len(hit)} of {len(ids)} ({share})")
            if args.control_types:
                types = {}
                for r in matching:
                    if r.get("controlType"):
                        t = types.setdefault(r["controlType"], [0, 0])
                        t[0 if cited(text, r["id"]) else 1] += 1
                for name in sorted(types):
                    print(f"  {name}: {types[name][0]} cited, {types[name][1]} not")
        return 0
    try:
        report = render(records, baselines, implemented)
    except Unreadable as exc:  # a record the report cannot count: a disposition the schema does not allow
        print(f"inventory-report: {exc}", file=sys.stderr)
        return 2
    target = root / REPORT
    if args.check:
        current = target.read_bytes() if target.is_file() else b""
        if current.replace(b"\r\n", b"\n") != report.encode("utf-8"):
            print(f"inventory-report: {REPORT.as_posix()} is stale; run python scripts/inventory-report.py and "
                  "stage it", file=sys.stderr)
            return 1
        return 0
    try:
        write(target, report)
    except OSError as exc:
        print(f"inventory-report: {REPORT.as_posix()} was not written ({exc}); the previous copy is kept",
              file=sys.stderr)
        return 1
    print(report, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
