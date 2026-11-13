# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/word-commands.py: ListCommands rows become command and shortcut records from Word's own hidden instance."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("word_commands", SCRIPTS / "word-commands.py")
wc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wc)
spec = importlib.util.spec_from_file_location("check_inventory", SCRIPTS / "check-inventory.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

BUILD = "16.0.20527.20150"
TABLE = [["Command Name", "Modifiers", "Key"], ["About", "", ""], ["Align Left", "", ""], ["Align Left", "", ""],
         ["Bold", "Ctrl+", "B"], ["Bold", "Ctrl+Shift+", "B"], ["Help", "", "F1"], ["Zoom200", "", ""]]


def table_text(rows):
    return "".join("".join(c + wc.CELL_END for c in row) + wc.CELL_END for row in rows)


class Fake:
    """A Word.Application stand-in that records what the script did to it."""

    def __init__(self, rows=TABLE, bindings=0, addins=0, build="16.0.20527"):
        self.rows, self.quit, self.closed, self.Build = rows, False, 0, build
        self.KeyBindings = type("K", (), {"Count": bindings})()
        self.AddIns = type("A", (), {"Count": addins})()
        self.docs = []
        fake = self

        class Docs:
            def Add(self):
                fake.docs.append(Doc())

            def __iter__(self):
                return iter(list(fake.docs))

        class Doc:
            def Close(self, SaveChanges):
                assert SaveChanges == 0
                fake.closed += 1

            def Tables(self, n):
                rng = type("R", (), {"Text": table_text(fake.rows)})()
                return type("T", (), {"Range": rng, "Rows": type("C", (), {"Count": len(fake.rows)})(),
                                      "Columns": type("C", (), {"Count": len(fake.rows[0])})()})()

        self.Documents = Docs()

    @property
    def ActiveDocument(self):
        return self.docs[-1]

    def ListCommands(self, all_commands):
        assert all_commands is True
        self.docs.append(type(self.docs[0])())

    def Quit(self, SaveChanges):
        assert SaveChanges == 0
        self.quit = True


class Records(unittest.TestCase):
    def test_every_row_is_one_command_and_keyed_rows_are_shortcuts(self):
        table = wc.parse_table(table_text(TABLE), len(TABLE), 3)
        commands, shortcuts, unmatched, _ = wc.records(table, BUILD, {"Bold", "Zoom200"})
        self.assertEqual(len(commands), len(TABLE) - 1)
        self.assertEqual([c["id"] for c in commands][1:3], ["word.command.align-left", "word.command.align-left-2"])
        self.assertEqual([(s["shortcut"], s["target"]) for s in shortcuts],
                         [("Ctrl+B", "word.command.bold"), ("Ctrl+Shift+B", "word.command.bold-2"),
                          ("F1", "word.command.help")])
        self.assertEqual([c.get("idMso") for c in commands if c.get("idMso")], ["Bold", "Bold", "Zoom200"])
        self.assertEqual(unmatched, ["About", "Align Left", "Align Left", "Help"])
        dashed, _, left, _ = wc.records([["B-old", "", ""]], BUILD, {"Bold"})
        self.assertNotIn("idMso", dashed[0])
        self.assertEqual(left, ["B-old"])
        self.assertEqual({c["source"] for c in commands + shortcuts}, {f"listcommands:{BUILD}"})

    def test_records_pass_the_inventory_checker(self):
        commands, shortcuts, _, _ = wc.records(wc.parse_table(table_text(TABLE), len(TABLE), 3), BUILD, set())
        with tempfile.TemporaryDirectory() as tmp:
            inv = Path(tmp) / "inventory" / "word"
            inv.mkdir(parents=True)
            (inv / "commands.json").write_text(wc.render(commands), encoding="utf-8")
            (inv / "shortcuts.json").write_text(wc.render(shortcuts), encoding="utf-8")
            self.assertEqual(ci.check([str(inv.parent)], inventory=inv.parent), [])

    def test_ids_are_unique_even_against_natural_suffixes(self):
        rows = [["Foo", "Ctrl+", "F"], ["Foo", "", ""], ["Foo 2", "Alt+", "F"]]
        commands, shortcuts, _, _ = wc.records(rows, BUILD, set())
        ids = [c["id"] for c in commands]
        self.assertEqual(len(set(ids)), 3, ids)
        self.assertEqual(len({s["id"] for s in shortcuts}), 2)
        self.assertEqual(commands[0]["shortcut"], "Ctrl+F")
        self.assertNotIn("shortcut", commands[1])

    def test_every_chord_splits_back_into_its_modifiers_and_key(self):
        rows = [["Bold", "Ctrl+Shift+", "B"], ["Help", "", "F1"], ["Zoom In", "Alt+Ctrl+", "Num +"], ["Plus", "Ctrl+", "+"]]
        commands, _, _, _ = wc.records(rows, BUILD, set())
        for rec, row in zip(commands, rows):  # a `+` key is written Plus, so no separator is ever a key
            self.assertEqual(wc.split_chord(rec["shortcut"]), (row[1], {"+": "Plus"}.get(row[2], row[2])))
        for row in (["Odd", "Ctrl", "B"], ["Twice", "Ctrl+", "Shift+B"], ["Spaced", "Ctrl+", " B "]):
            with self.assertRaises(wc.Refused):
                wc.records([row], BUILD, set())

    def test_the_process_must_be_exactly_the_expected_executable(self):
        office = "C:" + chr(92) + "Program Files" + chr(92) + "Microsoft Office" + chr(92) + "root" + chr(92) + "Office16" + chr(92)
        self.assertTrue(wc.office_com.is_executable(office + "WINWORD.EXE", "WINWORD.EXE"))
        self.assertTrue(wc.office_com.is_executable(office + "EXCEL.EXE", "excel.exe"))
        self.assertFalse(wc.office_com.is_executable(office + "NOTWINWORD.EXE", "WINWORD.EXE"))
        self.assertFalse(wc.office_com.is_executable(office + "EXCEL.EXE", "WINWORD.EXE"))

    def test_build_components_must_match(self):
        self.assertTrue(wc.same_build("16.0.20527", BUILD))
        self.assertTrue(wc.same_build(BUILD, BUILD))
        for bad in ("16.0.2052", "16.0.20528", "16", "16.0.20527.20150.1"):
            self.assertFalse(wc.same_build(bad, BUILD), bad)

    def test_the_reference_build_is_read_from_the_reference(self):
        self.assertEqual(wc.reference_build(), BUILD)
        with tempfile.TemporaryDirectory() as tmp:
            ref = Path(tmp) / "REFERENCE.md"
            ref.write_text("# R\n\n## Builds\n\n| App | Version | Build |\n| Excel | 16.0 | 16.0.1.2 |\n",
                           encoding="utf-8")
            with self.assertRaises(wc.Refused):
                wc.reference_build(ref)

    def test_bad_tables_are_refused(self):
        for text, rows, cols in ((table_text(TABLE), len(TABLE), 4), (table_text(TABLE)[:-2], len(TABLE), 3),
                                 (table_text([["Name", "Modifiers", "Key"]] + TABLE[1:]), len(TABLE), 3)):
            with self.assertRaises(wc.Refused):
                wc.parse_table(text, rows, cols)
        for row in (["", "", ""], ["Bold", "Ctrl+", ""]):
            with self.assertRaises(wc.Refused):
                wc.records([row], BUILD, set())

    def test_single_row_commands_link_to_unambiguous_ribbon_control_labels(self):
        ribbon = [
            {"id": "word.home.p.left", "kind": "control", "label": "Align Left", "idMso": "AlignLeft"},
            {"id": "word.home.f.grow", "kind": "control", "label": "Increase Font Size", "idMso": "FontSizeIncreaseWord"},
            {"id": "word.ctx.f.grow", "kind": "control", "label": "Increase Font Size", "idMso": "FontSizeIncreaseWord"},
            {"id": "word.insert.c.chart", "kind": "control", "label": "Chart", "idMso": "ChartInsert"},
            {"id": "word.home.ambig.a", "kind": "control", "label": "Format", "idMso": "FormatOne"},
            {"id": "word.home.ambig.b", "kind": "menuItem", "label": "Format", "idMso": "FormatTwo"},
            {"id": "word.home.partial.a", "kind": "control", "label": "Partial", "idMso": "PartialId"},
            {"id": "word.home.partial.b", "kind": "menuItem", "label": "Partial"},
            {"id": "word.home.menu.keep", "kind": "menuItem", "label": "Keep Text Only", "idMso": "PasteTextOnly"},
        ]
        self.assertEqual(
            wc.ribbon_label_identifiers(ribbon),
            {
                "Align Left": "AlignLeft",
                "Increase Font Size": "FontSizeIncreaseWord",
                "Chart": "ChartInsert",
                "Keep Text Only": "PasteTextOnly",
            },
        )
        rows = [
            ["Increase Font Size", "Ctrl+Shift+", ">"],
            ["Keep Text Only", "", ""],
            ["Chart", "", ""],
            ["Chart", "", ""],
            ["Chart", "", ""],
            ["Format", "", ""],
            ["Partial", "", ""],
        ]
        commands, _, unmatched, _ = wc.records(rows, BUILD, set(), ribbon_records=ribbon)
        by_id = {c["id"]: c for c in commands}
        self.assertEqual(by_id["word.command.increase-font-size"].get("idMso"), "FontSizeIncreaseWord")
        self.assertEqual(by_id["word.command.keep-text-only"].get("idMso"), "PasteTextOnly")
        self.assertIsNone(by_id["word.command.chart"].get("idMso"))
        self.assertIsNone(by_id["word.command.chart-2"].get("idMso"))
        self.assertIsNone(by_id["word.command.chart-3"].get("idMso"))
        self.assertIsNone(by_id["word.command.format"].get("idMso"))
        self.assertIsNone(by_id["word.command.partial"].get("idMso"))
        self.assertEqual(unmatched, ["Chart", "Chart", "Chart", "Format", "Partial"])


class Proc:
    def __init__(self, exits=True):
        self.pid, self.exits, self.closed, self.waited = 222, exits, False, None

    def exited(self, seconds):
        self.waited = seconds
        return self.exits

    def close(self):
        self.closed = True


class Instance(unittest.TestCase):
    def test_its_own_instance_is_watched_through_its_own_window_and_gone_after(self):
        fake, proc, seen = Fake(), Proc(), []

        def owner(app):
            seen.append(app)
            return proc

        table, build, effective = wc.list_commands(dispatch=lambda prog: fake, owner=owner, wait=5)
        self.assertEqual(seen, [fake])  # the process comes from the dispatched instance, not a process list
        self.assertEqual(len(table), len(TABLE) - 1)
        self.assertTrue(fake.quit and proc.closed)
        self.assertEqual((fake.closed, proc.waited, build), (2, 5, "16.0.20527"))
        self.assertEqual(effective, {})  # no chord in the fake table has two rows

    def test_a_customised_instance_is_refused_and_still_quit(self):
        for fake in (Fake(bindings=3), Fake(addins=1)):
            proc = Proc()
            with self.assertRaises(wc.Refused):
                wc.list_commands(dispatch=lambda prog, f=fake: f, owner=lambda app: proc)
            self.assertTrue(fake.quit and proc.closed)

    def test_a_lingering_instance_fails_the_run(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(wc.Refused):
            wc.list_commands(dispatch=lambda prog: Fake(), owner=lambda app: Proc(exits=False))
        self.assertIn("still running (pid 222)", err.getvalue())

    def test_a_failing_quit_still_waits_and_releases_the_handle(self):
        fake, proc = Fake(), Proc(exits=False)

        def quit_fails(SaveChanges):
            raise OSError("RPC server unavailable")

        fake.Quit = quit_fails
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(OSError):
            wc.list_commands(dispatch=lambda prog: fake, owner=lambda app: proc, wait=3)
        self.assertEqual((proc.waited, proc.closed), (3, True))

    def test_an_unidentified_process_fails_closed_and_still_quits(self):
        fake = Fake()

        def owner(app):
            raise wc.Refused("no window")

        with self.assertRaises(wc.Refused):
            wc.list_commands(dispatch=lambda prog: fake, owner=owner)
        self.assertTrue(fake.quit)


WORD_DIR = SCRIPTS.parent / "design" / "inventory" / "word"
# The rows of Word's table whose chord another row's command takes (Word runs that command; D02 T01 §17).
SHADOWED = {"word.command.open-or-close-up-para": ("Ctrl+", "0"), "word.command.paste-special": ("Alt+Ctrl+", "V"),
            "word.command.show-all-headings-2": ("Alt+Shift+", "A")}
EFFECTIVE = {"Ctrl+0": "Zoom100", "Ctrl+Alt+V": "PasteFormat", "Alt+Shift+A": "ShowAllHeadings"}


def committed_table():
    """Word's key table as the committed command catalogue records it, with the shadowed rows' keys put back."""
    rows = []
    for rec in json.loads((WORD_DIR / "commands.json").read_text(encoding="utf-8")):
        mods, key = wc.split_chord(rec["shortcut"]) if "shortcut" in rec else SHADOWED.get(rec["id"], ("", ""))
        rows.append([rec["label"], mods, {"Comma": ",", "Plus": "+"}.get(key, key)])
    return rows


class Rerun(unittest.TestCase):
    """D02 T01 §17: rerunning the producer keeps what the section adds by hand, and stops when a binding moves."""

    def rerun(self, table):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "word"
            out.mkdir()
            for name in ("baseline.json", "ribbon.json", "shortcuts.json"):
                (out / name).write_bytes((WORD_DIR / name).read_bytes())
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = wc.main([], lister=lambda: (table, BUILD, EFFECTIVE), build=lambda: BUILD,
                               installed=lambda: BUILD, out=out, unmatched_path=Path(tmp) / "u.txt")
            return code, stdout.getvalue() + stderr.getvalue(), (out / "shortcuts.json").read_bytes()

    def test_a_rerun_over_the_committed_file_gives_the_same_file(self):
        code, out, written = self.rerun(committed_table())
        self.assertEqual(code, 0, out)
        self.assertEqual(written, (WORD_DIR / "shortcuts.json").read_bytes())
        self.assertIn("Word runs another command for it: Open or Close Up Para (Ctrl+0)", out)

    def test_a_moved_binding_stops_the_run_and_writes_nothing(self):
        table = committed_table()
        bold = next(row for row in table if row[0] == "Bold" and row[2] == "B" and row[1] == "Ctrl+")
        bold[1] = "Alt+Ctrl+"  # Word now gives Bold another chord
        code, out, written = self.rerun(table)
        self.assertEqual(code, 1, out)
        self.assertIn("word.shortcut.bold (Ctrl+B -> Alt+Ctrl+B)", out)
        self.assertEqual(written, (WORD_DIR / "shortcuts.json").read_bytes())
        table.remove(bold)
        code, out, _ = self.rerun(table)
        self.assertEqual(code, 1, out)
        self.assertIn("left the table", out)

    def refresh(self, table, prepare):
        """A run over a copy of the committed Word inventory that `prepare(folder)` edited first: (exit code, what
        it printed, the command records and the shortcut records it left on disk)."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "word"
            out.mkdir()
            for name in ("baseline.json", "ribbon.json", "shortcuts.json", "commands.json"):
                (out / name).write_bytes((WORD_DIR / name).read_bytes())
            prepare(out)
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = wc.main([], lister=lambda: (table, BUILD, EFFECTIVE), build=lambda: BUILD,
                               installed=lambda: BUILD, out=out, unmatched_path=Path(tmp) / "u.txt")
            read = {name: json.loads((out / name).read_text(encoding="utf-8"))
                    for name in ("commands.json", "shortcuts.json")}
            return code, stdout.getvalue() + stderr.getvalue(), read["commands.json"], read["shortcuts.json"]

    def test_a_refresh_keeps_the_dispositions_written_by_hand(self):
        # D02 T01 §28: the table holds no disposition, so both files carry it over from the committed records.
        decided = {"disposition": "excluded", "dispositionReason": "Depends on a Microsoft cloud assistant."}
        marked = {"commands.json": "word.command.ask-copilot", "shortcuts.json": "word.shortcut.bold"}

        def prepare(out):
            for name, rid in marked.items():
                recs = json.loads((out / name).read_text(encoding="utf-8"))
                next(r for r in recs if r["id"] == rid).update(decided)
                (out / name).write_text(wc.render(recs), encoding="utf-8")
        table = committed_table() + [["Zzz Brand New Command", "", ""]]
        code, out, commands, shortcuts = self.refresh(table, prepare)
        self.assertEqual(code, 0, out)
        for recs, rid in ((commands, marked["commands.json"]), (shortcuts, marked["shortcuts.json"])):
            kept = next(r for r in recs if r["id"] == rid)
            self.assertEqual({k: kept.get(k) for k in decided}, decided, rid)
            self.assertEqual([r["id"] for r in recs if "disposition" in r or "dispositionReason" in r], [rid])
        self.assertTrue(any(r["label"] == "Zzz Brand New Command" for r in commands))  # new to the table: neither field
        # A command the owner decided about and the table no longer lists stops the refresh, and nothing is written.
        label = next(r["label"] for r in commands if r["id"] == marked["commands.json"])
        code, out, commands, _ = self.refresh([row for row in committed_table() if row[0] != label], prepare)
        self.assertEqual(code, 1, out)
        self.assertIn("committed command records that carry a disposition left the table; reconcile them by hand "
                      "first: word.command.ask-copilot", out)
        self.assertTrue(any(r["id"] == marked["commands.json"] and r.get("disposition") == "excluded"
                            for r in commands))

    def test_a_shared_chord_keeps_the_row_word_runs_and_refuses_when_word_names_none(self):
        rows = [["Open or Close Up Para", "Ctrl+", "0"], ["Zoom100", "Ctrl+", "0"]]
        commands, shortcuts, _, shadowed = wc.records(rows, BUILD, set(), effective={"Ctrl+0": "Zoom100"})
        self.assertEqual([s["label"] for s in shortcuts], ["Zoom100"])
        self.assertNotIn("shortcut", commands[0])
        self.assertEqual(shadowed, ["Open or Close Up Para (Ctrl+0)"])
        with self.assertRaises(wc.Refused):
            wc.records(rows, BUILD, set(), effective={"Ctrl+0": "SomethingElse"})


class Main(unittest.TestCase):
    def run_main(self, lister, build=BUILD, installed=BUILD):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "word"
            out.mkdir()
            (out / "baseline.json").write_text(json.dumps({"source": "baseline:" + "0" * 40, "columns": ["idMso"],
                                                           "rows": [["Bold"]]}), encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = wc.main([], lister=lister, build=lambda: build, installed=lambda: installed, out=out,
                               unmatched_path=Path(tmp) / "u.txt")
            files = {p.name: p.read_text(encoding="utf-8") for p in out.glob("*.json")}
            return code, stdout.getvalue() + stderr.getvalue(), files

    def test_writes_both_files_with_counts(self):
        table = wc.parse_table(table_text(TABLE), len(TABLE), 3)
        code, out, files = self.run_main(lambda: (table, "16.0.20527", {}))
        self.assertEqual(code, 0, out)
        self.assertEqual(len(json.loads(files["commands.json"])), 7)
        self.assertEqual(len(json.loads(files["shortcuts.json"])), 3)
        self.assertIn("7 rows: 7 command records (2 with an idMso), 3 shortcut records", out)

    def test_an_installed_build_other_than_the_reference_is_refused(self):
        table = wc.parse_table(table_text(TABLE), len(TABLE), 3)
        code, out, files = self.run_main(lambda: (table, "16.0.20500", {}), installed="16.0.20500.20000")
        self.assertEqual(code, 1, out)
        self.assertEqual(sorted(files), ["baseline.json"])

    def test_persistent_write_and_rename_failures_leave_both_files_as_they_were(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "commands.json", Path(tmp) / "shortcuts.json"

            def reset():
                a.write_text("old-a", encoding="utf-8")
                b.write_text("old-b", encoding="utf-8")

            def full_after_first(path, data, n=[0]):
                n[0] += 1
                if n[0] > 1:
                    raise OSError("disk full")  # and stays full for the rest of the run
                path.write_bytes(data)

            calls = []

            def rename_fails_on_second_placement(src, dst):
                calls.append((Path(src).name, Path(dst).name))
                if Path(dst) == b and Path(src).suffix == ".new":
                    raise OSError("rename refused")
                os.replace(src, dst)

            for kwargs in ({"write": full_after_first}, {"rename": rename_fails_on_second_placement}):
                reset()
                with self.assertRaises(OSError):
                    wc.publish({a: "new-a", b: "new-b"}, **kwargs)
                self.assertEqual((a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8")), ("old-a", "old-b"),
                                 kwargs)
                self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ["commands.json", "shortcuts.json"])
            wc.publish({a: "new-a", b: "new-b"})
            self.assertEqual((a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8")), ("new-a", "new-b"))
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ["commands.json", "shortcuts.json"])

    def test_both_files_or_neither(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "commands.json", Path(tmp) / "shortcuts.json"
            a.write_text("old-a", encoding="utf-8")
            b.write_text("old-b", encoding="utf-8")
            real, calls = (lambda path, data: path.write_bytes(data)), []

            def flaky(path, data):
                calls.append(path)
                if len(calls) == 2:
                    raise OSError("disk full")
                real(path, data)

            def short_write(path, data):
                calls.append(path)
                real(path, data[:-1] if len(calls) == 2 else data)  # the read-back then differs

            for broken in (flaky, short_write):
                calls.clear()
                with self.assertRaises(OSError):
                    wc.publish({a: "new-a", b: "new-b"}, write=broken)
                self.assertEqual((a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8")), ("old-a", "old-b"),
                                 broken.__name__)

    def test_refusals_and_failures_write_nothing(self):
        def refused():
            raise wc.Refused("customised")

        def broken():
            raise OSError("no Word")

        table = wc.parse_table(table_text(TABLE), len(TABLE), 3)
        odd = [["Odd", "Ctrl", "B"]]
        for lister, build, want in ((refused, BUILD, 1), (broken, BUILD, 2),
                                    (lambda: (table, "16.0.19000", {}), BUILD, 1), (lambda: (odd, "16.0.20527", {}), BUILD, 1)):
            code, out, files = self.run_main(lister, build)
            self.assertEqual(code, want, out)
            self.assertEqual(sorted(files), ["baseline.json"])


if __name__ == "__main__":
    unittest.main()
