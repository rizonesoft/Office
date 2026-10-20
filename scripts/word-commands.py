#!/usr/bin/env python3
"""Capture Word's command catalogue and default shortcut map through its built-in ListCommands command.

    python scripts/word-commands.py            # writes design/inventory/word/commands.json and shortcuts.json

Word is driven through COM in a hidden instance this script starts itself (DispatchEx), never the operator's own
Word, and that instance is quit without saving and confirmed gone. The instance must be uncustomised (no key bindings
in its Normal template, no add-ins), or the map would not be Word's default, so a customised instance stops the run.
ListCommands lists one row per command entry: its name as Word shows it, and the modifiers and key of one shortcut.
Names repeat, either for a second shortcut or for a different command sharing the name, and the table cannot tell
the two apart, so each row becomes one `command` record (repeats get -2, -3 in the id) and each row with a key also
becomes a `shortcut` record targeting it. A command whose name, with spaces removed, is a Word identifier in the
baseline carries that `idMso`; the rest are listed in build/word-commands-unmatched.txt for review.
Exit 0 written, 1 when the instance is customised or the table is not the expected shape, 2 when Word cannot start.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
WORD = ROOT / "design" / "inventory" / "word"
UNMATCHED = ROOT / "build" / "word-commands-unmatched.txt"
HEADER = ["Command Name", "Modifiers", "Key"]
CELL_END = "\r\x07"  # Word ends every cell's text, and every row, with these two characters


class Refused(Exception):
    pass


def slug(name):
    words = re.findall(r"[A-Za-z0-9]+", name)
    return "-".join(w.lower() for w in words) or "command"


def parse_table(text, rows, columns):
    """Rows of a Word table from its range text: each cell ends with CELL_END and so does each row."""
    if columns != len(HEADER):
        raise Refused(f"ListCommands table has {columns} columns, expected {len(HEADER)}")
    cells = text.split(CELL_END)
    if len(cells) != rows * (columns + 1) + 1:
        raise Refused(f"ListCommands table text has {len(cells)} parts for {rows} rows")
    table = [cells[i * (columns + 1):i * (columns + 1) + columns] for i in range(rows)]
    if table[0] != HEADER:
        raise Refused(f"ListCommands header is {table[0]}, expected {HEADER}")
    return table[1:]


def records(table, build, identifiers):
    """Command and shortcut records for the table rows, in table order, and the names with no identifier."""
    commands, shortcuts, unmatched, used = [], [], [], {}
    source = f"listcommands:{build}"
    for order, (name, modifiers, key) in enumerate(table):
        name, modifiers, key = name.strip(), modifiers.strip(), key.strip()
        if not name:
            raise Refused(f"row {order + 2} has no command name")
        if bool(modifiers) and not key:
            raise Refused(f"row {order + 2} ({name}) has modifiers but no key")
        base = slug(name)
        used[base] = used.get(base, 0) + 1
        cid = f"word.command.{base}" + (f"-{used[base]}" if used[base] > 1 else "")
        rec = {"id": cid, "app": "word", "kind": "command", "label": name, "order": order,
               "source": source, "capturedFrom": build}
        compact = re.sub(r"[^A-Za-z0-9_]", "", name)
        if compact in identifiers:
            rec["idMso"] = compact
        else:
            unmatched.append(name)
        commands.append(rec)
        if key:
            shortcuts.append({"id": cid.replace("word.command.", "word.shortcut.", 1), "app": "word",
                              "kind": "shortcut", "label": name, "shortcut": modifiers + key, "target": cid,
                              "source": source, "capturedFrom": build})
    return commands, shortcuts, unmatched


def baseline_identifiers(path=WORD / "baseline.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    col = data["columns"].index("idMso")
    return {r[col] for r in data["rows"] if r[col]}


def reference_build():
    """The installed build, from the Click-to-Run configuration that design/inventory/REFERENCE.md cites."""
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Office\ClickToRun\Configuration") as key:
        return winreg.QueryValueEx(key, "VersionToReport")[0]


def word_pids():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq WINWORD.EXE", "/FO", "CSV", "/NH"],
                         capture_output=True, text=True, check=False).stdout
    return {int(line.split('","')[1]) for line in out.splitlines() if line.startswith('"WINWORD')}


def list_commands(dispatch=None, pids=word_pids, wait=60.0, sleep=time.sleep):
    """Start a hidden Word of our own, list its commands, quit it, and confirm it is gone."""
    if dispatch is None:
        import win32com.client
        dispatch = win32com.client.DispatchEx
    before = pids()
    app = dispatch("Word.Application")
    mine = pids() - before
    try:
        app.Visible = False
        if app.KeyBindings.Count or app.AddIns.Count:
            raise Refused(f"this Word is customised ({app.KeyBindings.Count} key bindings, {app.AddIns.Count} "
                          "add-ins), so its map is not Word's default")
        app.Documents.Add()
        app.ListCommands(True)
        table = app.ActiveDocument.Tables(1)
        return parse_table(table.Range.Text, table.Rows.Count, table.Columns.Count), str(app.Build)
    finally:
        try:
            for doc in list(app.Documents):
                doc.Close(SaveChanges=0)
        finally:
            app.Quit(SaveChanges=0)
            deadline = time.monotonic() + wait
            while pids() & mine and time.monotonic() < deadline:
                sleep(1)
            left = pids() & mine
            if left:
                print(f"word-commands: the Word instance it started is still running (pid {sorted(left)})",
                      file=sys.stderr)


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


def render(recs):
    return "[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in recs) + "\n]\n"


def main(argv=None, lister=list_commands, build=reference_build, out=WORD, unmatched_path=UNMATCHED):
    if argv:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    expected = build()
    try:
        table, word_build = lister()
    except Refused as exc:
        print(f"word-commands: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # COM raises its own error types; any of them means Word did not run for us
        print(f"word-commands: Word could not be driven ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2
    if not expected.startswith(word_build):
        print(f"word-commands: Word reports build {word_build}, not the reference {expected}", file=sys.stderr)
        return 1
    commands, shortcuts, unmatched = records(table, expected, baseline_identifiers(Path(out) / "baseline.json"))
    write_atomic(Path(out) / "commands.json", render(commands))
    write_atomic(Path(out) / "shortcuts.json", render(shortcuts))
    write_atomic(Path(unmatched_path), "\n".join(unmatched) + "\n")
    print(f"{len(table)} rows: {len(commands)} command records ({len(commands) - len(unmatched)} with an idMso), "
          f"{len(shortcuts)} shortcut records; {len(unmatched)} unmatched names in {unmatched_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
