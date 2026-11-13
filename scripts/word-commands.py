#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
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
A chord the table gives more than one row keeps its shortcut only on the row whose command Word itself runs for it
(asked of the same instance through FindKey); the others keep their command record without a shortcut and are
listed (D02 T01 §17). A key that is itself `,` or `+` is written `Comma` or `Plus` (scripts/lib/shortcuts.py).
The shortcut file also holds what D02 T01 §17 adds by hand: each record's `scope`, `condition` and `behaviour` are
carried to the record of the same id, and every `published:` record is kept. A binding of the committed file that
moves to another chord or leaves the table stops the run before anything is written, naming it, so it is
reconciled by hand.
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

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import office_com  # noqa: E402,F401  (tests reach the shared helpers through it)
import shortcuts as chords  # noqa: E402  (scripts/lib is put on the path just above)
import word_shortcuts  # noqa: E402
from office_com import (REFERENCE, OwnProcess, Refused, baseline_identifiers, installed_build,  # noqa: E402,F401
                        own_process, publish, reference_build, same_build, write_atomic)

ROOT = Path(__file__).resolve().parents[1]
WORD = ROOT / "design" / "inventory" / "word"
UNMATCHED = ROOT / "build" / "word-commands-unmatched.txt"
HEADER = ["Command Name", "Modifiers", "Key"]
CELL_END = "\r\x07"  # Word ends every cell's text, and every row, with these two characters


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


def ribbon_label_identifiers(ribbon_records):
    """Map each control or menuItem label in `ribbon_records` to its `idMso` when every control or menuItem with that
    label carries the same non-empty `idMso` (and none lacks `idMso`)."""
    by_label = {}
    for rec in ribbon_records or ():
        if not isinstance(rec, dict) or rec.get("kind") not in ("control", "menuItem"):
            continue
        label = (rec.get("label") or "").strip()
        if not label:
            continue
        by_label.setdefault(label, set()).add(rec.get("idMso") or None)
    return {
        label: next(iter(ids))
        for label, ids in by_label.items()
        if None not in ids and len(ids) == 1
    }


def word_chord(modifiers, key):
    """The chord as the shortcut file writes it: the row's own modifiers and key, a `,` or `+` key by its name."""
    return modifiers + chords.LITERAL.get(key, key)


def canonical(name, modifiers, key):
    """The row's chord in canonical form; Refused, naming the row, when it cannot be read as one."""
    try:
        return chords.canonical(word_chord(modifiers, key))
    except chords.Malformed as exc:
        raise Refused(f"{name.strip()}: {exc}") from None


def shared_chords(table):
    """The chords (canonical) the table gives more than one row."""
    seen, shared = set(), set()
    for name, modifiers, key in table:
        if key:
            c = canonical(name, modifiers, key)
            (shared if c in seen else seen).add(c)
    return shared


def winners(table, effective):
    """For each chord the table gives several rows, the row Word runs for it: the first whose name, spaces removed,
    is the command FindKey named. Raises Refused when Word named none of them."""
    rows = {}
    for order, (name, modifiers, key) in enumerate(table):
        if key:
            rows.setdefault(canonical(name, modifiers, key), []).append((order, name.strip()))
    out = {}
    for chord, entries in rows.items():
        if len(entries) < 2:
            continue
        command = (effective or {}).get(chord)
        match = next((order for order, name in entries if name.replace(" ", "") == command), None)
        if match is None:
            raise Refused(f"Word's table gives {chord} to {', '.join(n for _, n in entries)}, and Word runs "
                          f"{command!r} for it")
        out[chord] = match
    return out


def records(table, build, identifiers, ribbon_records=(), effective=None):
    """Command and shortcut records for the table rows, in table order, the names with no identifier, and the rows
    whose shortcut another row's command takes (`effective`: what Word runs for each shared chord)."""
    commands, shortcuts, unmatched, taken, shadowed = [], [], [], set(), []
    winner = winners(table, effective)
    source = f"listcommands:{build}"
    name_counts = {}
    for row in table:
        if row:
            stripped = row[0].strip()
            name_counts[stripped] = name_counts.get(stripped, 0) + 1
    label_ids = ribbon_label_identifiers(ribbon_records)
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
        chord = word_chord(modifiers, key) if key else ""
        if chord and winner.get(canonical(name, modifiers, key), order) != order:
            shadowed.append(f"{name} ({chord})")
            chord = ""  # Word runs another row's command for this chord
        if chord:
            rec["shortcut"] = chord  # the row's modifiers end in "+", so this is the chord as listed
        compact = name.replace(" ", "")
        if compact in identifiers:
            rec["idMso"] = compact
        elif name_counts.get(name, 0) == 1 and name in label_ids:
            rec["idMso"] = label_ids[name]
        else:
            unmatched.append(name)
        commands.append(rec)
        if chord:
            shortcuts.append({"id": cid.replace("word.command.", "word.shortcut.", 1), "app": "word",
                              "kind": "shortcut", "label": name, "shortcut": chord, "target": cid,
                              "source": source, "capturedFrom": build})
    return commands, shortcuts, unmatched, shadowed


HAND = ("scope", "condition", "behaviour")  # what D02 T01 §17 writes on a shortcut record; the table never does


def carry(existing, fresh):
    """The fresh shortcut records with the hand-written fields of the committed records of the same id, then every
    committed `published:` record. Raises Refused, naming each, when a committed binding moved or left the table."""
    old = {r["id"]: r for r in existing if str(r.get("source", "")).startswith("listcommands:")}
    new = {r["id"]: r for r in fresh}
    moved = [f"{rid} ({rec['shortcut']} -> {new[rid]['shortcut']})" for rid, rec in old.items()
             if rid in new and chords.canonical(new[rid]["shortcut"]) != chords.canonical(rec["shortcut"])]
    gone = sorted(rid for rid in old if rid not in new)
    if moved or gone:
        raise Refused("committed bindings changed; reconcile them by hand first: " +
                      "; ".join(moved + [f"{rid} left the table" for rid in gone]))
    out = [dict(r, **{k: old[r["id"]][k] for k in HAND if k in old.get(r["id"], {})}) for r in fresh]
    return out + [r for r in existing if str(r.get("source", "")).startswith("published:")]


MODIFIERS = ("Ctrl+", "Alt+", "Shift+")


def split_chord(chord):
    """A chord's modifiers (a run of Ctrl+, Alt+ and Shift+) and its key, which may itself hold a plus (Num +)."""
    mods = ""
    while any(chord.startswith(m) and len(chord) > len(m) for m in MODIFIERS):
        m = next(m for m in MODIFIERS if chord.startswith(m))
        mods, chord = mods + m, chord[len(m):]
    return mods, chord


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
        rows = parse_table(table.Range.Text, table.Rows.Count, table.Columns.Count)
        effective = {}
        for chord in sorted(shared_chords(rows)):  # which of the rows sharing a chord Word runs
            (mods, key), = chords.steps(chord)
            code = word_shortcuts.key_code(mods, key)
            effective[chord] = None if code is None else str(app.FindKey(code).Command)
        result = rows, str(app.Build), effective
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
        table, word_build, effective = lister()
    except Refused as exc:
        print(f"word-commands: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # COM raises its own error types; any of them means Word did not run for us
        print(f"word-commands: Word could not be driven ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2
    if not same_build(word_build, expected):
        print(f"word-commands: Word reports build {word_build}, not the reference {expected}", file=sys.stderr)
        return 1
    ribbon_path = Path(out) / "ribbon.json"
    ribbon_records = ()
    if ribbon_path.is_file():
        try:
            loaded_ribbon = json.loads(ribbon_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"word-commands: {ribbon_path} could not be read ({exc})", file=sys.stderr)
            return 1
        if isinstance(loaded_ribbon, list):
            ribbon_records = loaded_ribbon
    shortcut_path = Path(out) / "shortcuts.json"
    try:
        existing = json.loads(shortcut_path.read_text(encoding="utf-8")) if shortcut_path.is_file() else []
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"word-commands: {shortcut_path} could not be read ({exc})", file=sys.stderr)
        return 1
    try:
        commands, shortcuts, unmatched, shadowed = records(
            table, expected, baseline_identifiers(Path(out) / "baseline.json"), ribbon_records=ribbon_records,
            effective=effective)
        shortcuts = carry(existing if isinstance(existing, list) else [], shortcuts)
    except Refused as exc:
        print(f"word-commands: {exc}", file=sys.stderr)
        return 1
    publish({Path(out) / "commands.json": render(commands), Path(out) / "shortcuts.json": render(shortcuts)})
    write_atomic(Path(unmatched_path), "\n".join(unmatched) + "\n")  # a review list, outside the inventory
    print(f"{len(table)} rows: {len(commands)} command records ({len(commands) - len(unmatched)} with an idMso), "
          f"{len(shortcuts)} shortcut records; {len(unmatched)} unmatched names in {unmatched_path}")
    for row in shadowed:
        print(f"shortcut not recorded, Word runs another command for it: {row}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
