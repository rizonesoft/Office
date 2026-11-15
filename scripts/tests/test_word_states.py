# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/word_states.py and scripts/make-word-state-fixtures.py: the document states the inventory is
captured in, and the fixtures made for them, against a fake Word (D02 T01 §36). No test starts Word."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import word_states as ws  # noqa: E402  (scripts/lib is put on the path just above)
from office_com import Refused  # noqa: E402

spec = importlib.util.spec_from_file_location("make_word_state_fixtures", SCRIPTS / "make-word-state-fixtures.py")
mk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mk)


class Unreadable(Exception):
    """What Word raises for a property it will not give."""


class FakeDoc:
    """A document of the fake Word. What was saved is kept in the app's `disk` by path, so opening it again gives
    what a real Word would: a file with the read-only attribute, one that recommends read-only and one marked as
    final all open read-only, and Word will not say whether a final document recommends read-only."""

    def __init__(self, app, path=None, props=None):
        self.app, self.path, self.closed = app, path, False
        self.props = dict(props or {"ReadOnlyRecommended": False, "Final": False, "CompatibilityMode": 15,
                                    "RemovePersonalInformation": False})
        self.opened_read_only = False
        self.Saved = path is not None
        outer = self

        class Content:
            def InsertAfter(self, text):
                outer.text, outer.Saved = text, False
        self.Content = Content()

    def __getattr__(self, name):
        if name == "ReadOnly":
            return self.opened_read_only
        props = self.__dict__.get("props", {})
        if name in props:
            if name in self.app.unreadable or (name == "ReadOnlyRecommended" and props["Final"]):
                raise Unreadable(name)
            return props[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ("ReadOnlyRecommended", "Final", "RemovePersonalInformation"):
            if name in self.app.ignored:  # a Word that does not take the property
                return
            self.props[name] = value
            self.__dict__["Saved"] = name == "Final"  # marking as final saves by itself
            if name == "Final":
                self.app.disk[self.path] = dict(self.props)
            return
        self.__dict__[name] = value

    def SaveAs2(self, path, FileFormat=None, AddToRecentFiles=True):
        self.app.calls.append(("SaveAs2", path, FileFormat, AddToRecentFiles))
        self.path = path
        self.props["CompatibilityMode"] = 11 if FileFormat == ws.DOC97 else 15
        Path(path).write_bytes(b"a fake document")
        self.app.disk[path] = dict(self.props)
        self.__dict__["Saved"] = True

    def Save(self):
        self.app.calls.append(("Save", self.path))
        self.app.disk[self.path] = dict(self.props)
        self.__dict__["Saved"] = True

    def Close(self, SaveChanges=None):
        self.app.calls.append(("Close", self.path, SaveChanges))
        if self.app.stuck:
            raise Unreadable("the document will not close")
        self.closed = True
        self.app.open.remove(self)


class FakeApp:
    def __init__(self, ignored=(), unreadable=(), foreign=0, stuck=False, among_documents=False, uncounted=False,
                 window_before=0):
        self.ignored, self.unreadable, self.stuck = set(ignored), set(unreadable), stuck
        self.among_documents, self.uncounted = among_documents, uncounted
        self.disk, self.calls, self.open, self.windows, self.quit = {}, [], [], window_before, 0
        self.foreign = foreign
        app = self

        class Documents:
            @property
            def Count(self):
                if app.uncounted and app.quit_asked:
                    raise Unreadable("Count")
                return len(app.open) + app.foreign

            def Add(self):
                doc = FakeDoc(app)
                app.open.append(doc)
                return doc

            def Open(self, path, AddToRecentFiles=True, ConfirmConversions=True):
                app.calls.append(("Open", path, AddToRecentFiles))
                doc = FakeDoc(app, path, app.disk[path])
                doc.opened_read_only = bool(not os.access(path, os.W_OK) or doc.props["ReadOnlyRecommended"]
                                            or doc.props["Final"])
                app.open.append(doc)
                return doc

        class Windows:
            @property
            def Count(self):
                return app.windows

            def Open(self, path, AddToRecentFiles=True):
                app.calls.append(("ProtectedOpen", path, AddToRecentFiles))
                if app.among_documents:
                    app.foreign += 1
                app.windows += 1

                class Window:
                    def Close(self):
                        app.calls.append(("CloseWindow", path))
                        app.windows -= 1
                return Window()
        self.Documents, self.ProtectedViewWindows = Documents(), Windows()
        self.quit_asked = False

    def Quit(self, SaveChanges=None):
        self.quit += 1


class Proc:
    def __init__(self, exits=True):
        self.pid, self.exits, self.closed = 4242, exits, False

    def exited(self, seconds):
        return self.exits

    def close(self):
        self.closed = True


class Rules(unittest.TestCase):
    def test_the_list_is_whole_and_agrees_with_itself(self):
        self.assertEqual(ws.NAMES, ("saved", "read-only", "read-only-recommended", "final", "compatibility",
                                    "personal-information-removed", "protected-view"))
        self.assertEqual(len({s["file"] for s in ws.STATES}), len(ws.STATES))
        for state in ws.STATES:
            self.assertEqual(Path(state["file"]).stem, state["name"])
            self.assertIn(state["view"], ws.VIEWS)
            self.assertTrue(state["title"] and state["condition"])
            self.assertEqual(bool(state["confirm"]), state["view"] == "document", state["name"])
            for name, value in state["set"]:  # what the script sets, Word is asked for again
                self.assertEqual(state["confirm"].get(name), value, state["name"])
        self.assertIs(ws.by_name("final"), ws.STATES[3])
        with self.assertRaises(ws.Invalid) as ctx:
            ws.by_name("signed")
        self.assertIn("'signed' is not a document state", str(ctx.exception))

    def test_a_fixture_stands_in_the_fixtures_folder_itself_and_nowhere_else(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = ws.folder(tmp)
            home.mkdir(parents=True)
            self.assertEqual(home, Path(tmp) / "fixtures" / "word-states")
            good = ws.fixture(ws.by_name("saved"), tmp)
            self.assertEqual(ws.inside(good, tmp), good.resolve())
            (home / "deeper").mkdir()
            outside = Path(tmp) / "saved.docx"
            for path in (outside, home / ".." / "saved.docx", home / "deeper" / "saved.docx",
                         home / "report.docx", home / "deeper" / ".." / ".." / "word-states-2" / "saved.docx",
                         Path(tmp) / "fixtures" / "word-contextual.docx"):
                with self.assertRaises(ws.Invalid, msg=str(path)):
                    ws.inside(path, tmp)
            self.assertEqual(ws.inside(home / "deeper" / ".." / "saved.docx", tmp), good.resolve())
            link = home / "final.docx"
            try:
                outside.write_bytes(b"x")
                os.symlink(outside, link)
            except OSError:
                return  # this account may not make links: the rule above already refuses what a link resolves to
            with self.assertRaises(ws.Invalid):
                ws.inside(link, tmp)

    def test_a_property_word_cannot_give_or_gives_otherwise_is_unconfirmed(self):
        state = ws.by_name("read-only-recommended")
        said = {"ReadOnly": True, "ReadOnlyRecommended": True}
        self.assertEqual(ws.unconfirmed(state, said.__getitem__), [])
        self.assertEqual(ws.unconfirmed(state, {"ReadOnly": -1, "ReadOnlyRecommended": 1}.__getitem__), [])
        self.assertEqual(ws.unconfirmed(state, dict(said, ReadOnlyRecommended=False).__getitem__),
                         ["ReadOnlyRecommended is False, not True"])

        def refuses(name):
            raise Unreadable(name)
        self.assertEqual(ws.unconfirmed(state, refuses), ["ReadOnly could not be read (Unreadable)",
                                                          "ReadOnlyRecommended could not be read (Unreadable)"])
        for odd in (None, "True", 2, []):  # not an answer: never taken for the expected value
            self.assertEqual(ws.unconfirmed(state, dict(said, ReadOnly=odd).__getitem__),
                             [f"ReadOnly is {odd!r}, which is neither true nor false"])
        mode = ws.by_name("compatibility")
        self.assertEqual(ws.unconfirmed(mode, {"ReadOnly": False, "CompatibilityMode": 11}.__getitem__), [])
        for odd in (15, True, "11", None):
            self.assertEqual(ws.unconfirmed(mode, {"ReadOnly": False, "CompatibilityMode": odd}.__getitem__),
                             [f"CompatibilityMode is {odd!r}, not 11"])
        self.assertEqual(ws.unconfirmed(ws.by_name("protected-view"), refuses), [])  # nothing is asked of the document


class Fixtures(unittest.TestCase):
    def make(self, app, states=ws.STATES, proc=None, root=None):
        proc = proc or Proc()
        said, marks = [], []
        failed = mk.run(list(states), root or self.tmp, dispatch=lambda progid: app, owner=lambda a: proc,
                        mark=lambda path, zone: marks.append((str(path), zone)),
                        say=lambda text, file=None: said.append(text))
        return failed, said, marks, proc

    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(self.unlock, holder)
        self.tmp = holder.name

    def unlock(self, holder):
        for path in Path(holder.name).rglob("*"):
            if path.is_file():
                os.chmod(path, stat.S_IWRITE)
        holder.cleanup()

    def test_every_state_is_made_confirmed_and_nothing_else_is_touched(self):
        app = FakeApp()
        failed, said, marks, proc = self.make(app)
        home = ws.folder(self.tmp)
        self.assertEqual(failed, [])
        self.assertEqual(sorted(p.name for p in home.iterdir()), sorted(s["file"] for s in ws.STATES))
        self.assertEqual(said, [f"{s['name']}: {(home / s['file']).resolve()}" for s in ws.STATES])
        saves = [c for c in app.calls if c[0] == "SaveAs2"]
        self.assertEqual([Path(c[1]).parent for c in saves], [home.resolve()] * 7)  # nothing saved anywhere else
        self.assertEqual([c[2] for c in saves], [16, 16, 16, 16, 0, 16, 16])
        # nothing is added to Word's list of recent files, by a save or by an open
        self.assertTrue(all(c[-1] is False for c in app.calls if c[0] in ("SaveAs2", "Open", "ProtectedOpen")))
        self.assertTrue(all(c[2] == mk.DISCARD for c in app.calls if c[0] == "Close"))
        self.assertFalse(os.access(home / "read-only.docx", os.W_OK))
        self.assertEqual(marks, [(str((home / "protected-view.docx").resolve()), 3)])
        self.assertEqual([c[0] for c in app.calls if "protected-view" in str(c[1])],
                         ["SaveAs2", "Close", "ProtectedOpen", "CloseWindow"])  # never opened among the documents
        self.assertEqual((app.quit, app.open, app.windows, proc.closed), (1, [], 0, True))
        self.assertEqual((app.Visible, app.DisplayAlerts), (False, 0))

    def test_a_second_run_replaces_each_fixture_and_gives_the_same_states(self):
        first = self.make(FakeApp())
        (ws.folder(self.tmp) / "saved.docx").write_bytes(b"what an earlier run left")
        second_app = FakeApp()
        second = self.make(second_app)
        self.assertEqual((first[0], second[0]), ([], []))
        self.assertEqual(first[1], second[1])
        self.assertEqual((ws.folder(self.tmp) / "saved.docx").read_bytes(), b"a fake document")
        self.assertEqual(sorted(second_app.disk), sorted(str((ws.folder(self.tmp) / s["file"]).resolve())
                                                         for s in ws.STATES))

    def test_a_fixture_word_does_not_confirm_is_deleted_and_fails_the_run(self):
        for app, name, why in (
                (FakeApp(ignored={"ReadOnlyRecommended"}), "read-only-recommended", "ReadOnly is False, not True"),
                (FakeApp(ignored={"Final"}), "final", "Final is False, not True"),
                (FakeApp(unreadable={"RemovePersonalInformation"}), "saved",
                 "RemovePersonalInformation could not be read (Unreadable)")):
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                failed, said, _, _ = self.make(app, root=tmp)
                self.assertIn(name, failed)
                self.assertTrue(any(f"{name} is not a fixture of its state and was deleted" in t and why in t
                                    for t in said), said)
                self.assertFalse((ws.folder(tmp) / ws.by_name(name)["file"]).exists())
                self.assertEqual(app.quit, 1)  # the instance holds nothing: it is quit
                for path in ws.folder(tmp).iterdir():
                    os.chmod(path, stat.S_IWRITE)
        # a marked file that opens among the documents is no Protected View fixture: it is deleted, and the
        # instance, which now holds a document the script cannot account for, is not quit
        app, said = FakeApp(among_documents=True), []
        with self.assertRaises(Refused):
            mk.run([ws.by_name("protected-view")], self.tmp, dispatch=lambda progid: app, owner=lambda a: Proc(),
                   mark=lambda path, zone: None, say=lambda text, file=None: said.append(text))
        self.assertIn("protected-view is not a fixture of its state and was deleted: it opened among the documents, "
                      "not in Protected View", said[0])
        self.assertFalse((ws.folder(self.tmp) / "protected-view.docx").exists())
        self.assertEqual(app.quit, 0)
        app, said = FakeApp(window_before=1), []
        with self.assertRaises(Refused):  # a window that is not the script's: nothing is opened beside it, and
            mk.run([ws.by_name("protected-view")], self.tmp, dispatch=lambda progid: app,  # the instance is not quit
                   owner=lambda a: Proc(), mark=lambda path, zone: None, say=lambda text, file=None: said.append(text))
        self.assertIn("a Protected View window was open before the fixture was", said[0])
        self.assertFalse(any(c[0] == "ProtectedOpen" for c in app.calls))
        self.assertFalse((ws.folder(self.tmp) / "protected-view.docx").exists())
        self.assertEqual(app.quit, 0)

    def test_only_the_scripts_own_instance_is_quit_and_not_one_that_holds_anothers_document(self):
        app = FakeApp(foreign=1)
        with self.assertRaises(Refused) as ctx:
            self.make(app)
        self.assertIn("still holds 1 document(s) or Protected View window(s) it could not close or did not make; "
                      "it is left running and is not quit", str(ctx.exception))
        self.assertEqual(app.quit, 0)
        app = FakeApp(stuck=True)  # a document of the script's that will not close: the instance is not quit over it
        with self.assertRaises(Refused) as ctx:
            self.make(app, states=[ws.by_name("saved")])
        self.assertIn("it is left running and is not quit (after Unreadable: the document will not close)",
                      str(ctx.exception))
        self.assertEqual(app.quit, 0)
        app = FakeApp(uncounted=True)
        app.quit_asked = True  # what the instance holds cannot be seen: unknown is not none
        with self.assertRaises(Refused) as ctx:
            self.make(app, states=[])
        self.assertIn("could not see what its Word instance still holds; it is left running and is not quit",
                      str(ctx.exception))
        self.assertEqual(app.quit, 0)
        app, proc = FakeApp(), Proc(exits=False)
        with self.assertRaises(Refused) as ctx:
            self.make(app, proc=proc)
        self.assertIn("(pid 4242) did not exit", str(ctx.exception))
        self.assertEqual((app.quit, proc.closed), (1, True))

    def run_main(self, argv, runner, installed="16.0.1.1", build="16.0.1.1"):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = mk.main(argv, runner=runner, build=lambda: build, installed=lambda: installed, root=self.tmp)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_the_command_line(self):
        asked = []

        def runner(states, root):
            asked.append(([s["name"] for s in states], root))
            return []
        code, out, _ = self.run_main([], runner)
        self.assertEqual((code, asked), (0, [(list(ws.NAMES), self.tmp)]))
        self.assertIn(f"7 fixtures made and confirmed in {ws.folder(self.tmp)}", out)
        code, _, _ = self.run_main(["--state", "final", "--state", "saved"], runner)
        self.assertEqual((code, asked[-1][0]), (0, ["saved", "final"]))
        code, _, err = self.run_main(["--state", "signed"], runner)
        self.assertEqual(code, 2)
        self.assertIn("invalid choice: 'signed'", err)
        code, _, err = self.run_main([], lambda states, root: ["final", "saved"])
        self.assertEqual(code, 1)
        self.assertIn("2 of 7 fixtures were not made: final, saved", err)

        def refused(states, root):
            raise Refused("the Word instance the script started (pid 7) did not exit")
        code, _, err = self.run_main([], refused)
        self.assertEqual(code, 1)
        self.assertIn("did not exit", err)

        def broken(states, root):
            raise OSError("the RPC server is unavailable")
        code, _, err = self.run_main([], broken)
        self.assertEqual(code, 2)
        self.assertIn("Word could not be driven (OSError: the RPC server is unavailable)", err)

    def test_a_build_that_is_not_the_reference_is_refused_before_word_is_started(self):
        def never(states, root):
            raise AssertionError("Word was started for a build that is not the reference")
        code, _, err = self.run_main([], never, installed="16.0.2.2")
        self.assertEqual(code, 1)
        self.assertIn("the installed build 16.0.2.2 is not the reference 16.0.1.1", err)

        def no_reference():
            raise ValueError("no Builds table")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = mk.main([], runner=never, build=no_reference, installed=lambda: "16.0.1.1", root=self.tmp)
        self.assertEqual(code, 1)
        self.assertIn("no reference build (no Builds table)", err.getvalue())

    def test_the_zone_mark_is_the_files_own_stream(self):
        path = Path(self.tmp) / "marked.docx"
        path.write_bytes(b"a document")
        try:
            mk.mark_from_internet(path, 3)
        except OSError:
            self.skipTest("this folder's file system keeps no named streams")
        with open(f"{path}:Zone.Identifier", encoding="ascii", newline="") as stream:
            self.assertEqual(stream.read(), "[ZoneTransfer]\r\nZoneId=3\r\n")
        self.assertEqual(path.read_bytes(), b"a document")  # the document itself is as it was

    def test_a_fixture_of_an_earlier_run_is_removed_even_when_it_is_read_only(self):
        path = Path(self.tmp) / "old.docx"
        path.write_bytes(b"old")
        os.chmod(path, stat.S_IREAD)
        mk.remove(path)
        self.assertFalse(path.exists())
        mk.remove(path)  # one that is not there is no fault


if __name__ == "__main__":
    unittest.main()
