"""scripts/word-commands.py: ListCommands rows become command and shortcut records from Word's own hidden instance."""
import contextlib
import importlib.util
import io
import json
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

BUILD = "16.0.20430.20182"
TABLE = [["Command Name", "Modifiers", "Key"], ["About", "", ""], ["Align Left", "", ""], ["Align Left", "", ""],
         ["Bold", "Ctrl+", "B"], ["Bold", "Ctrl+Shift+", "B"], ["Help", "", "F1"], ["Zoom200", "", ""]]


def table_text(rows):
    return "".join("".join(c + wc.CELL_END for c in row) + wc.CELL_END for row in rows)


class Fake:
    """A Word.Application stand-in that records what the script did to it."""

    def __init__(self, rows=TABLE, bindings=0, addins=0, build="16.0.20430"):
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
        commands, shortcuts, unmatched = wc.records(table, BUILD, {"Bold", "Zoom200"})
        self.assertEqual(len(commands), len(TABLE) - 1)
        self.assertEqual([c["id"] for c in commands][1:3], ["word.command.align-left", "word.command.align-left-2"])
        self.assertEqual([(s["shortcut"], s["target"]) for s in shortcuts],
                         [("Ctrl+B", "word.command.bold"), ("Ctrl+Shift+B", "word.command.bold-2"),
                          ("F1", "word.command.help")])
        self.assertEqual([c.get("idMso") for c in commands if c.get("idMso")], ["Bold", "Bold", "Zoom200"])
        self.assertEqual(unmatched, ["About", "Align Left", "Align Left", "Help"])
        self.assertEqual({c["source"] for c in commands + shortcuts}, {f"listcommands:{BUILD}"})

    def test_records_pass_the_inventory_checker(self):
        commands, shortcuts, _ = wc.records(wc.parse_table(table_text(TABLE), len(TABLE), 3), BUILD, set())
        with tempfile.TemporaryDirectory() as tmp:
            inv = Path(tmp) / "inventory" / "word"
            inv.mkdir(parents=True)
            (inv / "commands.json").write_text(wc.render(commands), encoding="utf-8")
            (inv / "shortcuts.json").write_text(wc.render(shortcuts), encoding="utf-8")
            self.assertEqual(ci.check([str(inv.parent)], inventory=inv.parent), [])

    def test_ids_are_unique_even_against_natural_suffixes(self):
        rows = [["Foo", "Ctrl+", "F"], ["Foo", "", ""], ["Foo 2", "Alt+", "F"]]
        commands, shortcuts, _ = wc.records(rows, BUILD, set())
        ids = [c["id"] for c in commands]
        self.assertEqual(len(set(ids)), 3, ids)
        self.assertEqual(len({s["id"] for s in shortcuts}), 2)
        self.assertEqual(commands[0]["shortcut"], "Ctrl+F")
        self.assertNotIn("shortcut", commands[1])

    def test_build_components_must_match(self):
        self.assertTrue(wc.same_build("16.0.20430", BUILD))
        self.assertTrue(wc.same_build(BUILD, BUILD))
        for bad in ("16.0.2043", "16.0.20431", "16", "16.0.20430.20182.1"):
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


class Instance(unittest.TestCase):
    def pids(self, live):
        return lambda: set(live)

    def test_only_its_own_instance_is_used_and_it_is_gone_after(self):
        live = {111}  # the operator's Word
        fake = Fake()

        def dispatch(prog):
            self.assertEqual(prog, "Word.Application")
            live.add(222)
            return fake

        sleeps = []

        def sleep(_):
            sleeps.append(1)
            live.discard(222)  # the instance exits a moment after Quit

        table, build = wc.list_commands(dispatch=dispatch, pids=self.pids(live), sleep=sleep)
        self.assertEqual(len(table), len(TABLE) - 1)
        self.assertTrue(fake.quit)
        self.assertEqual(fake.closed, 2)
        self.assertEqual(live, {111})
        self.assertEqual(build, "16.0.20430")

    def test_a_customised_instance_is_refused_and_still_quit(self):
        for fake in (Fake(bindings=3), Fake(addins=1)):
            with self.assertRaises(wc.Refused):
                wc.list_commands(dispatch=lambda prog, f=fake: f, pids=lambda: set(), sleep=lambda _: None)
            self.assertTrue(fake.quit)

    def test_a_lingering_instance_fails_the_run(self):
        live = {111}
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(wc.Refused):
            wc.list_commands(dispatch=lambda prog: (live.add(222), Fake())[1], pids=self.pids(live),
                             wait=0, sleep=lambda _: None)
        self.assertIn("still running (pid [222])", err.getvalue())

    def test_a_failure_right_after_start_still_quits_the_instance(self):
        fake, calls = Fake(), []

        def pids():
            calls.append(1)
            if len(calls) == 2:
                raise OSError("tasklist failed")
            return set()

        with self.assertRaises(OSError):
            wc.list_commands(dispatch=lambda prog: fake, pids=pids, sleep=lambda _: None)
        self.assertTrue(fake.quit)


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
        code, out, files = self.run_main(lambda: (table, "16.0.20430"))
        self.assertEqual(code, 0, out)
        self.assertEqual(len(json.loads(files["commands.json"])), 7)
        self.assertEqual(len(json.loads(files["shortcuts.json"])), 3)
        self.assertIn("7 rows: 7 command records (2 with an idMso), 3 shortcut records", out)

    def test_an_installed_build_other_than_the_reference_is_refused(self):
        table = wc.parse_table(table_text(TABLE), len(TABLE), 3)
        code, out, files = self.run_main(lambda: (table, "16.0.20500"), installed="16.0.20500.20000")
        self.assertEqual(code, 1, out)
        self.assertEqual(sorted(files), ["baseline.json"])

    def test_both_files_or_neither(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "commands.json", Path(tmp) / "shortcuts.json"
            a.write_text("old-a", encoding="utf-8")
            b.write_text("old-b", encoding="utf-8")
            real, calls = wc.write_atomic, []

            def flaky(path, text):
                calls.append(path)
                if path == b and len(calls) == 2:
                    raise OSError("disk full")
                real(path, text)

            wc.write_atomic = flaky
            try:
                with self.assertRaises(OSError):
                    wc.publish({a: "new-a", b: "new-b"})
            finally:
                wc.write_atomic = real
            self.assertEqual((a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8")), ("old-a", "old-b"))

    def test_refusals_and_failures_write_nothing(self):
        def refused():
            raise wc.Refused("customised")

        def broken():
            raise OSError("no Word")

        table = wc.parse_table(table_text(TABLE), len(TABLE), 3)
        for lister, build, want in ((refused, BUILD, 1), (broken, BUILD, 2),
                                    (lambda: (table, "16.0.19000"), BUILD, 1)):
            code, out, files = self.run_main(lister, build)
            self.assertEqual(code, want, out)
            self.assertEqual(sorted(files), ["baseline.json"])


if __name__ == "__main__":
    unittest.main()
