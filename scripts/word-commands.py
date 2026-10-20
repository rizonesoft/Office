#!/usr/bin/env python3
"""Capture Word's command catalogue and default shortcut map through its built-in ListCommands command.

    python scripts/word-commands.py            # writes design/inventory/word/commands.json and shortcuts.json

Word is driven through COM in a hidden instance this script starts itself (DispatchEx), never the operator's own
Word. Its process is taken from that instance's own window and held open by handle, so no other Word can be
mistaken for it; it is quit without saving, and the run fails unless that process has exited. The instance must be uncustomised (no key bindings
in its Normal template, no add-ins), or the map would not be Word's default, so a customised instance stops the run.
ListCommands lists one row per command entry: its name as Word shows it, and the modifiers and key of one shortcut.
Names repeat, either for a second shortcut or for a different command sharing the name, and the table cannot tell
the two apart, so each row becomes one `command` record (repeats get -2, -3 in the id) and each row with a key also
becomes a `shortcut` record targeting it. A command whose name, with spaces removed, is a Word identifier in the
baseline carries that `idMso`; the rest are listed in build/word-commands-unmatched.txt for review.
Both files are published together: if either cannot be written, both keep their previous contents. The run is a
capture of the reference build only (design/inventory/REFERENCE.md, Builds), compared component by component.
Exit 0 written; 1 when the instance is customised, the table is not the expected shape, the build is not the
reference, or the instance it started is still running afterwards; 2 when Word cannot start.
"""
import json
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
WORD = ROOT / "design" / "inventory" / "word"
UNMATCHED = ROOT / "build" / "word-commands-unmatched.txt"
REFERENCE = ROOT / "design" / "inventory" / "REFERENCE.md"
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
    commands, shortcuts, unmatched, taken = [], [], [], set()
    source = f"listcommands:{build}"
    for order, (name, modifiers, key) in enumerate(table):
        if modifiers != modifiers.strip() or key != key.strip():
            raise Refused(f"row {order + 2} ({name.strip()}): spaces around {modifiers!r} {key!r} would be lost")
        name = name.strip()  # a name is a label; only its outer whitespace goes
        if not name:
            raise Refused(f"row {order + 2} has no command name")
        if bool(modifiers) and not key:
            raise Refused(f"row {order + 2} ({name}) has modifiers but no key")
        if split_chord(modifiers + key) != (modifiers, key):
            # The chord is stored whole (the schema's `shortcut`); it must split back into the row's own values.
            raise Refused(f"row {order + 2} ({name}): {modifiers!r} {key!r} would not split back unambiguously")
        base, n = slug(name), 1
        while (f"{base}-{n}" if n > 1 else base) in taken:  # a natural "Foo 2" never meets a second "Foo"
            n += 1
        final = f"{base}-{n}" if n > 1 else base
        taken.add(final)
        cid = f"word.command.{final}"
        rec = {"id": cid, "app": "word", "kind": "command", "label": name, "order": order,
               "source": source, "capturedFrom": build}
        if key:
            rec["shortcut"] = modifiers + key  # the row's modifiers end in "+", so this is the chord as listed
        compact = name.replace(" ", "")
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


MODIFIERS = ("Ctrl+", "Alt+", "Shift+")


def split_chord(chord):
    """A chord's modifiers (a run of Ctrl+, Alt+ and Shift+) and its key, which may itself hold a plus (Num +)."""
    mods = ""
    while any(chord.startswith(m) and len(chord) > len(m) for m in MODIFIERS):
        m = next(m for m in MODIFIERS if chord.startswith(m))
        mods, chord = mods + m, chord[len(m):]
    return mods, chord


def baseline_identifiers(path=WORD / "baseline.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    col = data["columns"].index("idMso")
    return {r[col] for r in data["rows"] if r[col]}


def reference_build(path=REFERENCE):
    """The pinned Word build: the Build cell of the Word row under ## Builds in design/inventory/REFERENCE.md."""
    text = Path(path).read_text(encoding="utf-8")
    section = text[text.index("## Builds"):]
    match = re.search(r"^\| Word \| [^|]+ \| ([0-9]+(?:\.[0-9]+){3}) \|", section, re.MULTILINE)
    if not match:
        raise Refused(f"{path}: no Word row with a four-part build under ## Builds")
    return match[1]


def installed_build():
    """The installed build, from the Click-to-Run configuration."""
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Office\ClickToRun\Configuration") as key:
        return winreg.QueryValueEx(key, "VersionToReport")[0]


def same_build(reported, reference):
    """Word reports a build as a prefix of components (16.0.20430); it must equal the reference's leading ones."""
    have, want = str(reported).split("."), reference.split(".")
    return 2 <= len(have) <= len(want) and have == want[:len(have)]


class OwnProcess:
    """The process behind one Word instance's window, held by handle so its id cannot be reused under us."""

    SYNCHRONIZE, QUERY_LIMITED = 0x00100000, 0x1000

    def __init__(self, hwnd):
        import ctypes
        from ctypes import wintypes
        self.k32, user32 = ctypes.windll.kernel32, ctypes.windll.user32
        pid = wintypes.DWORD()
        if not user32.GetWindowThreadProcessId(wintypes.HWND(int(hwnd)), ctypes.byref(pid)) or not pid.value:
            raise Refused("the Word instance's window has no process")
        self.pid = pid.value
        self.handle = self.k32.OpenProcess(self.SYNCHRONIZE | self.QUERY_LIMITED, False, self.pid)
        if not self.handle:
            raise Refused(f"cannot open the Word instance's process {self.pid}")
        size = wintypes.DWORD(32768)
        buf = ctypes.create_unicode_buffer(size.value)
        if not self.k32.QueryFullProcessImageNameW(self.handle, 0, buf, ctypes.byref(size)) \
                or not buf.value.upper().endswith("WINWORD.EXE"):
            self.close()
            raise Refused(f"process {self.pid} behind the instance's window is not Word")

    def exited(self, seconds):
        return self.k32.WaitForSingleObject(self.handle, int(seconds * 1000)) == 0  # WAIT_OBJECT_0

    def close(self):
        if self.handle:
            self.k32.CloseHandle(self.handle)
            self.handle = None


def own_process(app):
    return OwnProcess(app.ActiveWindow.Hwnd)


def list_commands(dispatch=None, owner=own_process, wait=60.0):
    """Start a hidden Word of our own, list its commands, quit it, and confirm its process has exited."""
    if dispatch is None:
        import win32com.client
        dispatch = win32com.client.DispatchEx
    app = dispatch("Word.Application")
    proc = None
    try:  # from here on the instance is ours to quit, whatever fails
        app.Visible = False
        app.Documents.Add()  # the instance's first window, whose process is the one to watch
        proc = owner(app)
        if app.KeyBindings.Count or app.AddIns.Count:
            raise Refused(f"this Word is customised ({app.KeyBindings.Count} key bindings, {app.AddIns.Count} "
                          "add-ins), so its map is not Word's default")
        app.ListCommands(True)
        table = app.ActiveDocument.Tables(1)
        result = parse_table(table.Range.Text, table.Rows.Count, table.Columns.Count), str(app.Build)
    finally:
        try:
            for doc in list(app.Documents):
                doc.Close(SaveChanges=0)
        finally:
            try:
                app.Quit(SaveChanges=0)
            finally:  # even when Quit fails, the process is waited for and its handle released
                try:
                    gone = proc is not None and proc.exited(wait)
                    if proc is not None and not gone:
                        print(f"word-commands: the Word instance it started is still running (pid {proc.pid})",
                              file=sys.stderr)
                finally:
                    if proc is not None:
                        proc.close()
    # The contract is no leftover process: one still running, or one never identified, is not a success.
    if proc is None:
        raise Refused("the Word instance's process was never identified, so its exit cannot be confirmed")
    if not gone:
        raise Refused(f"the Word instance it started (pid {proc.pid}) did not exit")
    return result


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


def publish(files, write=None, rename=os.replace):
    """Write every file or none. All new content is written to temporary files first, so a full disk fails before
    anything changes; the originals are then renamed aside and the new files renamed in, and any failure from there
    renames the originals back. Renames need no free space, so the rollback cannot fail the way the writes did."""
    write = write or (lambda path, data: path.write_bytes(data))
    staged, aside, placed = {}, {}, []
    try:
        for path, text in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".new")
            os.close(fd)
            staged[path] = Path(tmp)
            write(staged[path], text.encode("utf-8"))
            if staged[path].read_bytes() != text.encode("utf-8"):
                raise OSError(f"{tmp}: read-back differs from what was written")
        for path in files:
            if path.is_file():
                aside[path] = path.with_name(path.name + f".{os.getpid()}.old")
                rename(path, aside[path])
            rename(staged[path], path)
            del staged[path]  # placed: no longer a leftover to clean up
            placed.append(path)
    except BaseException:
        for path in placed:
            if path not in aside:
                path.unlink()
        for path, old in aside.items():
            rename(old, path)
        raise
    finally:
        for tmp in staged.values():
            if tmp.exists():
                tmp.unlink()
    for old in aside.values():
        old.unlink()


def render(recs):
    return "[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in recs) + "\n]\n"


def main(argv=None, lister=list_commands, build=reference_build, installed=installed_build, out=WORD,
         unmatched_path=UNMATCHED):
    if argv:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    try:
        expected = build()
    except (OSError, ValueError, Refused) as exc:
        print(f"word-commands: no reference build ({exc})", file=sys.stderr)
        return 1
    if installed() != expected:
        print(f"word-commands: the installed build {installed()} is not the reference {expected}; record a new "
              "reference first", file=sys.stderr)
        return 1
    try:
        table, word_build = lister()
    except Refused as exc:
        print(f"word-commands: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # COM raises its own error types; any of them means Word did not run for us
        print(f"word-commands: Word could not be driven ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2
    if not same_build(word_build, expected):
        print(f"word-commands: Word reports build {word_build}, not the reference {expected}", file=sys.stderr)
        return 1
    try:
        commands, shortcuts, unmatched = records(table, expected, baseline_identifiers(Path(out) / "baseline.json"))
    except Refused as exc:
        print(f"word-commands: {exc}", file=sys.stderr)
        return 1
    publish({Path(out) / "commands.json": render(commands), Path(out) / "shortcuts.json": render(shortcuts)})
    write_atomic(Path(unmatched_path), "\n".join(unmatched) + "\n")  # a review list, outside the inventory
    print(f"{len(table)} rows: {len(commands)} command records ({len(commands) - len(unmatched)} with an idMso), "
          f"{len(shortcuts)} shortcut records; {len(unmatched)} unmatched names in {unmatched_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
