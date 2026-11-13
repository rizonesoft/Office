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
"""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import inventory_claims  # noqa: E402  (scripts/lib is put on the path just above)
import todo_graph  # noqa: E402
import word_absences  # noqa: E402

REPORT = Path("design") / "inventory" / "COVERAGE.md"
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


def gather(root):
    records, baselines = load_inventory(root)
    try:
        sections = todo_graph.graph(root).values()
    except todo_graph.Refused as exc:
        raise Unreadable(f"the TODO tree: {exc}") from None
    implemented = inventory_claims.implemented(sections)
    return records, baselines, implemented


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
    args = ap.parse_args(argv)
    root = Path(root)
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
    report = render(records, baselines, implemented)
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
