# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/word_states.py and scripts/make-word-state-fixtures.py: the document states the inventory is
captured in, and the fixtures made for them, against a fake Word (D02 T01 §36). No test starts Word."""
import contextlib
import copy
import importlib.util
import json
import io
import os
from pathlib import Path
import stat
import sys
import tempfile
import threading
import unittest
import unittest.mock

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
                        say=lambda text, file=None: said.append(text),
                        end=lambda pid: self.fail("the script ended a Word that was answering"))
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

    def test_a_word_that_stops_answering_is_ended_and_fails_the_run(self):
        # A hidden Word that waits on something never says so (on 2026-11-15 it blocked for good on adding an
        # ActiveX control). The run has a time limit: the script's own process is ended, the fixture it was making
        # is deleted, and the run fails saying so.
        released, app, ended, proc = threading.Event(), FakeApp(), [], Proc()
        real_add, calls = app.Documents.Add, {"n": 0}

        def add():
            calls["n"] += 1
            if calls["n"] == 3:  # the instance's first window, the saved fixture, then the one that hangs
                (ws.folder(self.tmp) / "read-only.docx").write_bytes(b"half made")
                released.wait(10)
                raise OSError("the RPC server is unavailable")
            return real_add()
        app.Documents.Add = add

        def end(pid):
            ended.append(pid)
            released.set()
        with self.assertRaises(Refused) as ctx:
            mk.run(list(ws.STATES), self.tmp, dispatch=lambda progid: app, owner=lambda a: proc,
                   mark=lambda path, zone: None, say=lambda text, file=None: None, limit=0.2, end=end)
        self.assertIn("Word did not answer within 0 s; the instance the script started (pid 4242) was ended, and "
                      "the fixture it was making is deleted", str(ctx.exception))
        self.assertEqual((ended, app.quit, proc.closed), ([4242], 0, True))
        self.assertTrue((ws.folder(self.tmp) / "saved.docx").exists())  # made and confirmed before the hang: kept
        self.assertFalse((ws.folder(self.tmp) / "read-only.docx").exists())
        # a run that ends in time ends nothing
        ended.clear()
        failed, _, _, _ = self.make(FakeApp())
        self.assertEqual((failed, ended), ([], []))

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


SOURCE = {"source": "uia:16.0.20527.20150", "capturedFrom": "16.0.20527.20150"}


def rec(rid, kind, label, parent=None, order=0, **extra):
    record = {"id": rid, "app": "word", "kind": kind, "label": label, "order": order, **SOURCE, **extra}
    if parent:
        record["parent"] = parent
    return record


def blank():
    """A small blank-document capture: Save shows Save As, Info holds a menu and a properties group, Print a page."""
    b = "word.backstage"
    return [
        rec(f"{b}.info", "backstagePage", "Info", order=0, idMso="TabInfo"),
        rec(f"{b}.info.protect-document", "group", "Protect Document", f"{b}.info", 0, idMso="GroupPermissions"),
        rec(f"{b}.info.protect-document.protect-document", "control", "Protect Document",
            f"{b}.info.protect-document", 0, controlType="menu", itemCount=1,
            behaviour="Opens the ways to protect the document. Always available."),
        rec(f"{b}.info.protect-document.protect-document.mark-as-final", "menuItem", "Mark as Final",
            f"{b}.info.protect-document.protect-document", 0, idMso="FileMarkAsFinal"),
        rec(f"{b}.info.properties", "group", "Properties", f"{b}.info", 1),
        rec(f"{b}.info.properties.title", "control", "Title", f"{b}.info.properties", 0, controlType="editBox"),
        rec(f"{b}.save", "backstagePage", "Save", order=1, target=f"{b}.save-as"),
        rec(f"{b}.save-as", "backstagePage", "Save As", order=2, idMso="TabSave"),
        rec(f"{b}.save-as.browse", "control", "Browse", f"{b}.save-as", 0, controlType="button"),
        rec(f"{b}.print", "backstagePage", "Print", order=3, idMso="TabPrint"),
        rec(f"{b}.print.print", "control", "Print", f"{b}.print", 0, controlType="button"),
        rec(f"{b}.close", "control", "Close", order=4, controlType="button"),
    ]


def captured(*changes, drop=(), add=()):
    """A whole capture over a fixture: the blank one's facts (nothing written by hand), with some records changed
    (`(id, fields)`), dropped or added."""
    out = [{k: v for k, v in r.items() if k not in ws.HAND} for r in blank() if r["id"] not in drop]
    for rid, fields in changes:
        target = next(r for r in out if r["id"] == rid)
        for key, value in fields.items():
            if value is None:
                target.pop(key, None)
            else:
                target[key] = value
    return out + list(add)


class StateRecords(unittest.TestCase):
    SAVED = ws.by_name("saved")
    B = "word.backstage"
    S = "word.backstage.states.saved"

    def saved(self):
        """Over a saved document: Save is a plain button, Info gains a location group, Print is as it was."""
        return captured(
            (f"{self.B}.save", {"kind": "control", "controlType": "button", "target": None}),
            add=[rec(f"{self.B}.info.location-information", "group", "Location Information", f"{self.B}.info", 2),
                 rec(f"{self.B}.info.location-information.location", "control", "Location",
                     f"{self.B}.info.location-information", 0, controlType="button")])

    def test_a_state_is_recorded_whole_against_the_blank_capture(self):
        out = ws.state_records(self.SAVED, self.saved(), blank())
        by = {r["id"]: r for r in out}
        root = out[0]
        self.assertEqual({k: root[k] for k in ("id", "kind", "label", "order", "condition", "captureState")}, {
            "id": self.S, "kind": "region", "label": "Saved document", "order": 0,
            "condition": "an ordinary document saved to a file", "captureState": "saved"})
        self.assertEqual(root["itemCount"], len(out) - 1)
        # the keys stand in one order whatever process made the record: two captures are the same bytes
        self.assertEqual(list(root), ["id", "app", "kind", "label", "order", "condition", "captureState", "source",
                                      "capturedFrom", "itemCount"])
        self.assertEqual(list(by[f"{self.S}.print"]), ["id", "app", "kind", "label", "order", "source",
                                                        "capturedFrom", "captureState", "unchanged", "variantOf",
                                                        "parent"])
        self.assertTrue(all(r["captureState"] == "saved" and r["id"].startswith(self.S) for r in out))
        # Save: a page that shows Save As over the blank document, a plain button over a saved one (gap 1)
        save = by[f"{self.S}.save"]
        self.assertEqual((save["kind"], save["controlType"], save["variantOf"], "target" in save),
                         ("control", "button", f"{self.B}.save", False))
        # a page that differs carries every record of it, each joined to its counterpart; what the state adds has none
        info = [r for r in out if r["id"].startswith(f"{self.S}.info")]
        self.assertEqual(len(info), 8)
        self.assertEqual(by[f"{self.S}.info.properties.title"]["variantOf"], f"{self.B}.info.properties.title")
        self.assertEqual(by[f"{self.S}.info.properties.title"]["parent"], f"{self.S}.info.properties")
        self.assertNotIn("variantOf", by[f"{self.S}.info.location-information"])
        self.assertNotIn("variantOf", by[f"{self.S}.info.location-information.location"])
        self.assertNotIn("unchanged", by[f"{self.S}.info"])
        # what was written by hand on the blank record is not a fact, and is not copied into the state
        self.assertNotIn("behaviour", by[f"{self.S}.info.protect-document.protect-document"])
        # a page that is the blank capture's, record for record, says so and carries none of them
        page = by[f"{self.S}.print"]
        self.assertEqual((page["unchanged"], page["variantOf"], page["parent"]), (True, f"{self.B}.print", self.S))
        self.assertNotIn(f"{self.S}.print.print", by)
        self.assertNotIn("idMso", page)
        self.assertEqual(by[f"{self.S}.save-as"]["unchanged"], True)
        self.assertEqual(by[f"{self.S}.close"]["variantOf"], f"{self.B}.close")
        ws.validate_states(out, {r["id"] for r in blank()})

    def test_what_a_state_disables_hides_or_renames_is_seen(self):
        final = ws.by_name("final")
        s = "word.backstage.states.final"
        got = captured(
            (f"{self.B}.print.print", {"enabled": False}),  # disabled by the state
            (f"{self.B}.info.protect-document", {"label": "Alert - Protect Document"}),  # renamed, its id with it
            drop=(f"{self.B}.info.properties.title",))  # hidden by the state
        for r in got:  # a renamed group: the capture gives it, and what stands under it, another id
            for key in ("id", "parent"):
                if key in r:
                    r[key] = r[key].replace("info.protect-document", "info.alert-protect-document", 1)
        out = ws.state_records(final, got, blank())
        by = {r["id"]: r for r in out}
        self.assertIs(by[f"{s}.print.print"]["enabled"], False)
        self.assertNotIn("unchanged", by[f"{s}.print"])
        # the hidden control has no record, on a page that is not unchanged: the blank record nobody points at
        self.assertNotIn(f"{s}.info.properties.title", by)
        claimed = {r["variantOf"] for r in out if "variantOf" in r}
        self.assertNotIn(f"{self.B}.info.properties.title", claimed)
        # the renamed group keeps its counterpart by its idMso, and its controls keep theirs through it
        group = by[f"{s}.info.alert-protect-document"]
        self.assertEqual((group["label"], group["variantOf"]), ("Alert - Protect Document",
                                                                 f"{self.B}.info.protect-document"))
        self.assertEqual(by[f"{s}.info.alert-protect-document.protect-document"]["variantOf"],
                         f"{self.B}.info.protect-document.protect-document")
        self.assertEqual(by[f"{s}.info.alert-protect-document.protect-document.mark-as-final"]["variantOf"],
                         f"{self.B}.info.protect-document.protect-document.mark-as-final")
        ws.validate_states(out, {r["id"] for r in blank()})

    def test_a_page_the_state_does_not_offer_is_recorded_disabled_and_unopened(self):
        got = captured((f"{self.B}.save-as", {"enabled": False}), drop=(f"{self.B}.save-as.browse",))
        out = ws.state_records(ws.by_name("protected-view"), got, blank())
        page = next(r for r in out if r["id"].endswith(".save-as"))
        self.assertEqual((page["enabled"], page["variantOf"], "unchanged" in page), (False, f"{self.B}.save-as", False))

    def test_a_capture_that_cannot_be_held_is_refused(self):
        with self.assertRaises(ws.Invalid) as ctx:
            ws.state_records(self.SAVED, captured(add=[rec("word.options.general", "group", "General")]), blank())
        self.assertIn("'word.options.general', which is not a Backstage record", str(ctx.exception))
        with self.assertRaises(ws.Invalid) as ctx:
            ws.state_records(self.SAVED, captured(add=[rec(f"{self.B}.info.x", "control", "X", f"{self.B}.gone")]),
                             blank())
        self.assertIn("stands under word.backstage.gone, which the capture does not hold", str(ctx.exception))
        # two records of the state that would stand for one blank record
        twice = captured(add=[rec(f"{self.B}.info.again", "group", "Again", f"{self.B}.info", 5,
                                  idMso="GroupPermissions")])
        with self.assertRaises(ws.Invalid) as ctx:
            ws.state_records(self.SAVED, twice, blank())
        self.assertIn("both stand for word.backstage.info.protect-document of the blank-document capture",
                      str(ctx.exception))
        with self.assertRaises(ws.Invalid):
            ws.state_id(self.SAVED, "word.backstage.states.saved.info")
        with self.assertRaises(ws.Invalid):
            ws.state_id(self.SAVED, "word.ribbon.home")

    def test_two_states_that_add_the_same_control_each_keep_their_own_record(self):
        # gap 2: the same addition in two states, a recapture of either, and a blank-document merge
        ids = {r["id"] for r in blank()}
        saved = ws.state_records(self.SAVED, self.saved(), blank())
        read_only = ws.state_records(ws.by_name("read-only"), self.saved(), blank())
        both = ws.merge_state(saved, read_only, ws.by_name("read-only"))
        self.assertEqual(len(both), len(saved) + len(read_only))
        self.assertEqual(len({r["id"] for r in both}), len(both))
        self.assertIn("word.backstage.states.saved.info.location-information.location", {r["id"] for r in both})
        self.assertIn("word.backstage.states.read-only.info.location-information.location", {r["id"] for r in both})
        ws.validate_states(both, ids)
        # a hand-written field on one state's record is carried by that state's recapture, and the other state's
        # records stay byte for byte
        mine = "word.backstage.states.saved.info.location-information.location"
        told = [dict(r, behaviour="Shows the folder. Always available.") if r["id"] == mine else r for r in both]
        fresh = ws.state_records(self.SAVED, self.saved(), blank())
        again = ws.merge_state(told, fresh, self.SAVED)
        self.assertEqual(next(r for r in again if r["id"] == mine)["behaviour"],
                         "Shows the folder. Always available.")
        self.assertEqual([r for r in again if r["captureState"] == "read-only"], read_only)
        self.assertEqual([r["captureState"] for r in again], ["saved"] * len(saved) + ["read-only"] * len(read_only))
        # recapturing the later state leaves the earlier one as it is, and the order is the list's
        once_more = ws.merge_state(again, read_only, ws.by_name("read-only"))
        self.assertEqual(once_more, again)
        # a state whose capture shrank loses the records it no longer shows, and only its own
        smaller = ws.state_records(ws.by_name("read-only"), captured(), blank())
        shrunk = ws.merge_state(again, smaller, ws.by_name("read-only"))
        self.assertEqual([r for r in shrunk if r["captureState"] == "saved"],
                         [r for r in again if r["captureState"] == "saved"])
        self.assertNotIn("word.backstage.states.read-only.info.location-information.location",
                         {r["id"] for r in shrunk})
        ws.validate_states(shrunk, ids)

    def test_only_what_a_state_adds_counts_as_captured_beside_the_blank_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(ws.captured_ids(tmp), frozenset())  # no states file yet: nothing more is captured
            path = Path(tmp) / ws.FILE
            path.write_text(json.dumps([
                {"id": "word.backstage.states.read-only.info.alert", "idMso": "GroupReadOnly"},
                {"id": "word.backstage.states.read-only.info.protect", "idMso": "GroupPermissions",
                 "variantOf": "word.backstage.info.protect-document"},
                {"id": "word.backstage.states.read-only.info.x"}, {"id": "y", "idMso": ""}]), encoding="utf-8")
            # a record that stands for a blank record adds nothing: a group lost from the blank capture must not
            # pass as captured because a state still shows it
            self.assertEqual(ws.captured_ids(tmp), frozenset({"GroupReadOnly"}))
            for text in ("{}", "[1]", "not json"):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError, msg=text):
                    ws.captured_ids(tmp)

    def refusal(self, records, whole=False):
        try:
            ws.validate_states(records, {r["id"] for r in blank()}, whole=whole)
        except ws.Invalid as exc:
            return str(exc)
        return ""

    def test_a_file_of_states_that_is_not_lawful_is_refused(self):
        good = ws.state_records(self.SAVED, self.saved(), blank())
        self.assertEqual(self.refusal(good), "")

        def changed(rid, **fields):
            out = copy.deepcopy(good)
            target = next(r for r in out if r["id"] == rid)
            for key, value in fields.items():
                if value is None:
                    target.pop(key)
                else:
                    target[key] = value
            return self.refusal(out)
        self.assertIn("its captureState 'signed' is not a state", changed(f"{self.S}.close", captureState="signed"))
        self.assertIn("its captureState None is not a state", changed(f"{self.S}.close", captureState=None))
        self.assertIn(f"a record of the read-only state has an id under word.backstage.states.read-only",
                      changed(f"{self.S}.close", captureState="read-only"))
        self.assertIn("is called 'Saved', not Saved document", changed(self.S, label="Saved"))
        self.assertIn("its condition is 'a file', not the document the list gives the state",
                      changed(self.S, condition="a file"))
        self.assertIn("the root of a state is a region with no parent", changed(self.S, kind="group"))
        self.assertIn(f"holds {len(good) - 1} of the {len(good)} records the capture recorded",
                      changed(self.S, itemCount=len(good)))
        self.assertIn("its parent 'word.backstage.info' is not a record of the saved state",
                      changed(f"{self.S}.info.properties", parent="word.backstage.info"))
        self.assertIn("its variantOf 'word.backstage.gone' is not a record of the blank-document capture",
                      changed(f"{self.S}.close", variantOf="word.backstage.gone"))
        self.assertIn("word.backstage.print is already the counterpart of",
                      changed(f"{self.S}.close", variantOf="word.backstage.print"))
        self.assertIn("`unchanged` is true, on a page of a state only", changed(f"{self.S}.close", unchanged=True))
        self.assertIn("`unchanged` is true, on a page of a state only", changed(f"{self.S}.print", unchanged=False))
        self.assertIn("a page that is unchanged names the blank-document page it equals",
                      changed(f"{self.S}.print", variantOf=None))
        self.assertIn("`condition` belongs to the root of a state", changed(f"{self.S}.close", condition="x"))
        self.assertIn("app must be 'word'", changed(f"{self.S}.close", app="excel"))
        under = copy.deepcopy(good) + [dict(rec(f"{self.S}.print.print", "control", "Print", f"{self.S}.print"),
                                            captureState="saved")]
        under[0]["itemCount"] += 1
        self.assertIn("a page that is unchanged carries no records of its own, and 1 stand under it",
                      self.refusal(under))
        self.assertIn(f"duplicate record id {self.S}.close", self.refusal(good + [copy.deepcopy(good[-1])]))
        self.assertIn("the saved state has records and no root", self.refusal(good[1:]))
        with self.assertRaises(ws.Invalid):
            ws.validate_states([{"captureState": "saved"}], set())

    def test_the_whole_file_holds_every_state_the_list_names(self):
        ids = {r["id"] for r in blank()}
        every = []
        for state in ws.STATES:
            every = ws.merge_state(every, ws.state_records(state, self.saved(), blank()), state)
        ws.validate_states(every, ids, whole=True)
        self.assertEqual([r["captureState"] for r in every if r["kind"] == "region"], list(ws.NAMES))
        without = [r for r in every if r["captureState"] != "final"]
        self.assertEqual(self.refusal(without), "")  # a file that is being built holds what was captured so far
        self.assertIn("the final state (Marked as final) is not recorded", self.refusal(without, whole=True))
        # a state the list says this PC cannot produce is not asked for, and is refused when it is there
        with unittest.mock.patch.dict(ws.UNPRODUCIBLE, {"final": "no document can be marked as final here"}):
            self.assertEqual(self.refusal(without, whole=True), "")
            self.assertIn("the final state is recorded, and scripts/lib/word_states.py says this PC cannot produce it",
                          self.refusal(every, whole=True))


if __name__ == "__main__":
    unittest.main()
