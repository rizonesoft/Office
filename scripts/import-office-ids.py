#!/usr/bin/env python3
"""Convert the published Office control identifier workbooks into design/inventory/<app>/baseline.json.

    python scripts/import-office-ids.py R:/scratch/office-ui-ids/<commit>        # all six apps
    python scripts/import-office-ids.py R:/scratch/office-ui-ids/<commit> --check

The workbooks (MIT licensed, pinned by commit in design/inventory/REFERENCE.md) list every ribbon tab, group and
control of each app. The source folder is named after the full upstream commit, which each baseline file records.
Only facts are kept: identifier, control type, where it sits (placement, tab set, tab, group, parents) and policy id,
one row per workbook row in workbook order, so a row's position is its order. Rows the workbook lists without an
identifier are kept with a null idMso: they are real controls, known by policy id and position. The workbooks hold no
labels or descriptions, and none are added. Placements the workbooks spell as "None (...)" become our own enum, and
any other value that is not an identifier stops the import, so new upstream wording is mapped by hand, never copied.
Outlook's per-window workbooks merge into one file whose first column is the window.
Writes go to a temporary file in the destination folder, then replace the original, and are read back.
Exit 0 written (or up to date with --check), 1 on a stale file or an unmappable value, 2 when a workbook is missing.
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "design" / "inventory"
APPS = ("word", "excel", "powerpoint", "visio", "project")
# Every Outlook item window the pinned commit publishes; a missing or unknown one stops the import.
OUTLOOK_WINDOWS = ("addritem", "apptitem", "dlstitem", "explorer", "logitem", "mailitem", "mailread", "mmsedit",
                   "mmsread", "postitem", "postread", "reportitem", "reqread", "reqsend", "resenditem", "respcounter",
                   "responseread", "responsesend", "rssitem", "shareitem", "smsedit", "smsread", "taskitem")
# Compound type spellings and the role each names; any other compound spelling stops the import.
COMPOUND_TYPES = {"button (dialogBoxLauncher)": "dialogBoxLauncher"}
HEADER = ("Control Name", "Control Type", "Tab Set", "Tab", "Group/Context Menu Name", "Parent Control",
          "Secondary Parent Control", "Policy ID")
COLUMNS = ["idMso", "controlType", "placement", "tabSet", "tab", "group", "parent", "secondaryParent", "policyId"]
PLACEMENTS = {
    "None (Core Tab)": "coreTab",
    "None (Context Menu)": "contextMenu",
    "None (Not in the Ribbon)": "notInRibbon",
    "None (Backstage View)": "backstage",
    "None (Quick Access Toolbar)": "quickAccessToolbar",
}
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")  # _3DRotationGallery is one
COMMIT = re.compile(r"^[0-9a-f]{40}$")
# The Quick Access Toolbar rows name the toolbar in words in the Tab column; the placement already says it.
QAT_TAB = "Quick Access Toolbar"


class Unmappable(Exception):
    """A workbook value that is not an identifier and has no mapping here."""


def ident(value, where):
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    value = str(value).strip()
    if value in PLACEMENTS:  # the Tab and Group columns repeat the placement in words; the placement field holds it
        return None
    if not IDENTIFIER.match(value):
        raise Unmappable(f"{where}: {value!r} is not an identifier; map it in import-office-ids.py")
    return value


def control_type(value, where):
    value = str(value or "").strip()
    result = ident(COMPOUND_TYPES.get(value, value), where)
    if result is None:
        raise Unmappable(f"{where}: no control type")
    return result


def read_rows(path):
    import openpyxl  # read-only, pinned in scripts/requirements.txt
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = wb.worksheets[0].iter_rows(values_only=True)
        header = next(rows, ())
        if tuple(header[:len(HEADER)]) != HEADER:
            raise Unmappable(f"{path.name}: unexpected header {header[:len(HEADER)]}")
        extra = [h for h in header[len(HEADER):] if h is not None and h != "Column1"]
        if extra:
            raise Unmappable(f"{path.name}: unmapped columns {extra}")
        # A row is kept when any cell holds a value, so a value only in an extra column reaches the refusal below.
        return [r for r in rows if r and any(v is not None for v in r)]
    finally:
        wb.close()


def convert(path):
    rows = []
    for n, r in enumerate(read_rows(path)):
        where = f"{path.name} row {n + 2}"
        tab_set, tab = r[2], r[3]
        if isinstance(tab_set, str) and tab_set.startswith("None ("):
            if tab_set not in PLACEMENTS:
                raise Unmappable(f"{where}: placement {tab_set!r} has no mapping")
            placement, tab_set = PLACEMENTS[tab_set], None
        elif tab_set is None:
            placement = None
        else:
            placement = "contextualTab"
        if placement == "quickAccessToolbar" and tab == QAT_TAB:
            tab = None
        policy = r[7]
        if policy is not None and not (isinstance(policy, int) and not isinstance(policy, bool) and policy >= 0):
            raise Unmappable(f"{where}: policy id {policy!r} is not a non-negative integer")
        if len(r) > len(HEADER) and any(v is not None for v in r[len(HEADER):]):
            raise Unmappable(f"{where}: a value beyond the known columns")
        rows.append([ident(r[0], where), control_type(r[1], where), placement, ident(tab_set, where),
                     ident(tab, where), ident(r[4], where), ident(r[5], where), ident(r[6], where), policy])
    if not rows:
        raise Unmappable(f"{path.name}: no rows")
    return rows


def render(commit, columns, rows):
    # One row per line keeps the file reviewable and its diffs small.
    head = json.dumps({"source": f"baseline:{commit}", "columns": columns})[:-1]
    return head + ', "rows": [\n' + ",\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n]}\n"


def build(source):
    source = Path(source)
    commit = source.name
    if not COMMIT.match(commit):
        raise Unmappable(f"{source}: the folder must be named after the full upstream commit")
    out = {}
    for app in APPS:
        path = source / f"{app}controls.xlsx"
        if not path.is_file():
            raise FileNotFoundError(path)
        out[app] = render(commit, COLUMNS, convert(path))
    found = {p.name[len("outlook"):-len("controls.xlsx")] for p in source.glob("outlook*controls.xlsx")}
    unknown = sorted(found - set(OUTLOOK_WINDOWS))
    if unknown:
        raise Unmappable(f"{source}: unknown Outlook windows {unknown}; add them to OUTLOOK_WINDOWS")
    merged = []
    for window in OUTLOOK_WINDOWS:
        path = source / f"outlook{window}controls.xlsx"
        if not path.is_file():
            raise FileNotFoundError(path)
        merged += [[window] + row for row in convert(path)]
    out["outlook"] = render(commit, ["window"] + COLUMNS, merged)
    return out


def write_atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(text.encode("utf-8"))
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    if path.read_bytes() != text.encode("utf-8"):
        raise OSError(f"{path}: read-back differs from what was written")


def main(argv=None, inventory=INVENTORY):
    parser = argparse.ArgumentParser(description="Import the Office control identifier baseline.")
    parser.add_argument("source", help="folder named after the pinned upstream commit, holding its workbooks")
    parser.add_argument("--check", action="store_true", help="report stale baseline files instead of writing")
    args = parser.parse_args(argv)
    try:
        files = build(args.source)
    except FileNotFoundError as exc:
        print(f"import-office-ids: missing workbook {exc}", file=sys.stderr)
        return 2
    except Unmappable as exc:
        print(f"import-office-ids: {exc}", file=sys.stderr)
        return 1
    stale = []
    for app, text in files.items():
        path = Path(inventory) / app / "baseline.json"
        current = path.read_bytes() if path.is_file() else None  # bytes: a CRLF checkout is stale
        if current == text.encode("utf-8"):
            continue
        if args.check:
            stale.append(str(path))
        else:
            write_atomic(path, text)
            print(f"wrote {path} ({len(json.loads(text)['rows'])} rows)")
    for path in stale:
        print(f"{path}: stale; rerun without --check")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
