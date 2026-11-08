# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/capture-ui.py: UI Automation trees become inventory records, facts only, with safe launch and closing."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("capture_ui", SCRIPTS / "capture-ui.py")
cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cu)


def _never_start(exe):
    raise AssertionError(f"a test tried to start {exe}")


cu.start_process = _never_start  # every launch in these tests is injected; a real program must never start
spec = importlib.util.spec_from_file_location("check_inventory", SCRIPTS / "check-inventory.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

BUILD = "16.0.20527.20150"
IDS = {"TabHome", "PasteMenu", "Paste", "Cut", "Bold", "FontDialog", "QuickStylesGallery", "ChangeCaseGallery"}


class E:
    """A fake UI Automation element."""
    counter = 0

    def __init__(self, ctype, name="", aid="", key="", cls="", rect=(0, 0, 10, 10), kids=(), toggle=False):
        self.control_type, self.name, self.automation_id, self.access_key = ctype, name, aid, key
        self.class_name, self.rect, self.kids, self.toggle = cls, rect, list(kids), toggle
        E.counter += 1
        self.rid = (E.counter,)

    def children(self):
        return iter(self.kids)

    def can_toggle(self):
        return self.toggle

    def runtime_id(self):
        return self.rid


def home():
    paste = E("SplitButton", "Paste", key="Alt, H, V", rect=(20, 82, 62, 158),
              kids=[E("Button", "Paste", "Paste"), E("MenuItem", "More Options", "PasteMenu_Dropdown")])
    clipboard = E("Group", "Clipboard", key="Alt, H, Z L", kids=[paste, E("Button", "Cut", "Cut", "Alt, H, X")])
    font = E("Group", "Font", key="Alt, H, Z F", kids=[
        E("ComboBox", "Font", "Font", kids=[E("Edit", "Font"), E("Button", "Open")]),
        E("Button", "Bold", "Bold", "Alt, H, 1", rect=(104, 122, 128, 146), toggle=True),
        E("MenuItem", "Change Case", "ChangeCaseGallery", "Alt, H, 7"),
        E("Button", "Font...", "FontDialog", "Alt, H, F N", cls="NetUISimpleButton")])
    styles = E("Group", "Styles", key="Alt, H, Z S", kids=[E("Group", "Styles", kids=[E("MenuItem", "", "QuickStylesGallery")])])
    addin = E("Group", "Adobe Acrobat", kids=[E("Button", "Create PDF", "AcrobatCreate")])
    lower = E("Pane", "Lower Ribbon", kids=[E("Group", "Home", kids=[clipboard, font, styles, addin])])
    tab = E("TabItem", "Home", "TabHome", "Alt, H", rect=(58, 48, 113, 78))
    return tab, lower


class Walk(unittest.TestCase):
    def records(self, origin=None):
        tab, lower = home()
        ctx = cu.Context("word", BUILD, IDS, origin=origin)
        return cu.walk_tab(tab, 0, lower, ctx), ctx

    def test_tab_groups_and_controls_with_facts_only(self):
        recs, ctx = self.records()
        by = {r["label"]: r for r in recs}
        self.assertEqual((by["Home"]["kind"], by["Home"]["idMso"], by["Home"]["keytip"]), ("tab", "TabHome", "H"))
        self.assertEqual((by["Paste"]["controlType"], by["Paste"]["idMso"], by["Paste"]["keytip"]),
                         ("splitButton", "PasteMenu", "V"))
        self.assertEqual((by["Bold"]["controlType"], by["Bold"]["keytip"]), ("toggleButton", "1"))
        self.assertEqual(by["Font..."]["controlType"], "dialogLauncher")
        self.assertEqual(by["Change Case"]["controlType"], "gallery")
        self.assertEqual([r["label"] for r in recs if r.get("parent") == "word.home.styles"], ["Styles"])
        self.assertEqual(by["Font"]["controlType"], "comboBox")  # its Edit and Open parts are not controls
        self.assertNotIn("Open", by)
        self.assertEqual([r["label"] for r in recs if r["kind"] == "group"], ["Clipboard", "Font", "Styles"])
        self.assertEqual(ctx.skipped, ["group 'Adobe Acrobat' on 'Home': no control the baseline knows, so its "
                                       "provenance is unverified"])
        aside = {r["label"]: r for r in ctx.unverified}
        self.assertEqual((aside["Adobe Acrobat"]["kind"], aside["Create PDF"]["uiaId"], aside["Create PDF"]["baselineMissing"]),
                         ("group", "AcrobatCreate", True))
        self.assertNotIn("Create PDF", by)
        self.assertEqual((by["Bold"]["uiaId"], by["Paste"].get("uiaId")), ("Bold", None))
        self.assertEqual({r["source"] for r in recs}, {f"uia:{BUILD}"})
        self.assertFalse(any("bounds" in r for r in recs))

    def test_bounds_and_size_only_under_the_profile(self):
        recs, _ = self.records(origin=(0, 0))
        by = {r["label"]: r for r in recs}
        self.assertEqual(by["Paste"]["bounds"], {"x": 20, "y": 82, "width": 42, "height": 76})
        self.assertEqual((by["Paste"]["size"], by["Bold"]["size"]), ("large", "small"))
        self.assertTrue(all(r.get("captureProfile") == "fhd-100" for r in recs if "bounds" in r))

    def test_a_tab_without_an_identifier_is_set_aside_with_its_groups(self):
        for tab, expected_why in ((E("TabItem", "Acrobat"), "no identifier"),
                                  (E("TabItem", "Acrobat", "ThirdPartyTab"), "identifier 'ThirdPartyTab' is not in the baseline")):
            ctx = cu.Context("word", BUILD, IDS)
            lower = E("Pane", kids=[E("Group", "Acrobat", kids=[E("Group", "Create", kids=[E("Button", "Bold", "Bold")])])])
            self.assertEqual(cu.walk_tab(tab, 9, lower, ctx), [])
            self.assertIn(expected_why, ctx.skipped[0])
            self.assertEqual([(r["kind"], r["baselineMissing"], r.get("idMso")) for r in ctx.unverified],
                             [("tab", True, None), ("group", True, None), ("control", True, "Bold")])

    def test_unverified_records_pass_the_checker(self):
        recs, ctx = self.records()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "inventory" / "word" / "unverified.json"  # its groups hang off the main capture's tab
            path.parent.mkdir(parents=True)
            (path.parent / "ribbon.json").write_text(cu.render(recs), encoding="utf-8")
            path.write_text(cu.render(ctx.unverified), encoding="utf-8")
            self.assertEqual(ci.check([str(path)], inventory=path.parent.parent), [])

    def test_records_pass_the_inventory_checker(self):
        for origin in (None, (0, 0)):
            recs, _ = self.records(origin)
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "inventory" / "word" / "ribbon.json"
                path.parent.mkdir(parents=True)
                path.write_text(cu.render(recs), encoding="utf-8")
                self.assertEqual(ci.check([str(path.parent.parent)], inventory=path.parent.parent), [])

    def test_screentip_text_is_never_read(self):
        source = (SCRIPTS / "capture-ui.py").read_text(encoding="utf-8")
        self.assertNotIn("GetPixel", source)  # owner decision 2026-10-20: the theme is not part of the profile
        for prop in ("CurrentHelpText", "CurrentFullDescription", "HelpTextProperty", "FullDescriptionProperty"):
            self.assertNotIn(prop, source)
        self.assertFalse([n for n in dir(cu.Element) if "help" in n.lower() or "description" in n.lower()])

    def test_keytips_and_ids(self):
        self.assertEqual([cu.keytip(k) for k in ("Alt, H, F P", "Alt, H", "Alt, H, C 1", "")], ["FP", "H", "C1", None])
        ids = cu.Ids()
        self.assertEqual([ids.make("word.home", x) for x in ("Font", "Font...", "Font 2")],
                         ["word.home.font", "word.home.font-2", "word.home.font-2-2"])
        ids = cu.Ids()
        self.assertEqual([ids.make("word.home.font", "Font", "Font"), ids.make("word.home.font", "Font...", "FontDialog")],
                         ["word.home.font.font", "word.home.font.font-fontdialog"])


class Merge(unittest.TestCase):
    def test_hand_written_fields_survive_and_positions_refresh(self):
        old = [{"id": "word.home.font.bold", "label": "Bold", "order": 3, "behaviour": "Ours.", "source": "uia:1.2.3.4",
                "bounds": {"x": 1, "y": 1, "width": 1, "height": 1}},
               {"id": "word.home.font.cut", "label": "Cut", "order": 4, "behaviour": "Cuts.",
                "source": "uia:16.0.20430.20182", "capturedFrom": "16.0.20430.20182"},
               {"id": "word.home.gone", "label": "Gone", "behaviour": "Kept."}]
        new = [{"id": "word.home.font.bold", "label": "Bold", "order": 5, "source": f"uia:{BUILD}",
                "bounds": {"x": 9, "y": 9, "width": 9, "height": 9}, "captureProfile": "fhd-100"},
               {"id": "word.home.font.cut", "label": "Cut", "order": 6, "source": f"uia:{BUILD}",
                "capturedFrom": BUILD},
               {"id": "word.home.font.italic", "label": "Italic", "order": 7}]
        out = {r["id"]: r for r in cu.merge(old, new)}
        bold, cut = out["word.home.font.bold"], out["word.home.font.cut"]
        self.assertEqual((bold["behaviour"], bold["source"], bold["order"], bold["bounds"]["x"]), ("Ours.", "uia:1.2.3.4", 5, 9))
        self.assertEqual((cut["behaviour"], cut["source"], cut["capturedFrom"], cut["order"]),
                         ("Cuts.", f"uia:{BUILD}", BUILD, 6))
        self.assertIn("word.home.gone", out)
        self.assertIn("word.home.font.italic", out)

    def test_annotations_follow_the_control_not_the_encounter_order(self):
        old = [{"id": "word.v.g.x", "parent": "word.v.g", "uiaId": "First", "label": "X", "behaviour": "About First."},
               {"id": "word.v.g.x-2", "parent": "word.v.g", "uiaId": "Second", "label": "X", "behaviour": "About Second."}]
        # A later build lists the two the other way round, so the ids a fresh capture hands out are swapped.
        new = [{"id": "word.v.g.x", "parent": "word.v.g", "uiaId": "Second", "label": "X", "order": 0},
               {"id": "word.v.g.x-2", "parent": "word.v.g", "uiaId": "First", "label": "X", "order": 1}]
        out = cu.merge(old, new)
        self.assertEqual({r["uiaId"]: (r["behaviour"], r["order"]) for r in out},
                         {"First": ("About First.", 1), "Second": ("About Second.", 0)})
        self.assertEqual(len(out), 2)

    def test_children_follow_their_parent_through_a_remapped_id(self):
        old = [{"id": "word.v.g.x", "parent": "word.v.g", "uiaId": "First", "label": "X", "behaviour": "About First."},
               {"id": "word.v.g.x-2", "parent": "word.v.g", "uiaId": "Second", "label": "X"}]
        new = [{"id": "word.v.g.x", "parent": "word.v.g", "uiaId": "Second", "label": "X"},
               {"id": "word.v.g.x.item", "parent": "word.v.g.x", "label": "Item"},
               {"id": "word.v.g.x-2", "parent": "word.v.g", "uiaId": "First", "label": "X"}]
        unverified = [{"id": "word.v.g.addin", "parent": "word.v.g.x", "label": "Addin", "baselineMissing": True},
                      {"id": "word.v.g.addin.btn", "parent": "word.v.g.addin", "label": "Btn", "baselineMissing": True}]
        out = {r["id"]: r for r in cu.merge(old, new, unverified)}
        item = next(r for r in out.values() if r["label"] == "Item")
        self.assertEqual(item["parent"], "word.v.g.x-2")  # Second keeps its own id, and its new item hangs under it
        self.assertEqual(unverified[0]["parent"], "word.v.g.x-2")  # Sidecar parent is remapped to the retained ID
        self.assertEqual(out["word.v.g.x"]["behaviour"], "About First.")

    def test_a_new_control_on_a_taken_id_is_kept_under_its_own(self):
        old = [{"id": "word.home.g.x", "parent": "word.home.g", "uiaId": "Old", "label": "X", "behaviour": "Old one."}]
        new = [{"id": "word.home.g.x", "parent": "word.home.g", "uiaId": "New", "label": "X"}]
        out = cu.merge(old, new)
        self.assertEqual(sorted((r["id"], r["uiaId"]) for r in out),
                         [("word.home.g.x", "Old"), ("word.home.g.x-2", "New")])


class Profile(unittest.TestCase):
    GOOD = {"window": (-1928, 1072, 8, 2120), "dpi": 96, "zoomed": True}
    MONITOR = {"rect": (-1920, 1080, 0, 2160), "dpi": 96}

    def test_all_values_hold(self):
        self.assertEqual(cu.profile_problems(self.GOOD, self.MONITOR, 1033, 120), [])

    def test_each_value_is_checked(self):
        cases = [(dict(self.GOOD, dpi=144), self.MONITOR, 1033, 120, "DPI"),
                 (dict(self.GOOD, zoomed=False), self.MONITOR, 1033, 120, "maximised"),
                 (self.GOOD, None, 1033, 120, "no display"),
                 (dict(self.GOOD, window=(0, 0, 3840, 2160)), self.MONITOR, 1033, 120, "not on"),
                 (self.GOOD, self.MONITOR, 1036, 120, "language"),
                 (self.GOOD, self.MONITOR, 1033, 20, "ribbon")]
        for state, monitor, lang, height, word in cases:
            problems = cu.profile_problems(state, monitor, lang, height)
            self.assertTrue(any(word in p for p in problems), (word, problems))

    def test_the_profile_display_is_found(self):
        mons = [{"rect": (0, 0, 3840, 2160), "dpi": 144}, self.MONITOR]
        self.assertEqual(cu.profile_monitor(mons), self.MONITOR)
        self.assertIsNone(cu.profile_monitor(mons[:1]))


class Popups(unittest.TestCase):
    def test_items_are_read_once_from_nested_menus(self):
        items = [E("ListItem", "Underline"), E("ListItem", "Double underline"), E("MenuItem", "More Underlines...")]
        inner = E("Menu", "Underline", kids=items)
        outer = E("Menu", "Underline", kids=[inner] + items)  # Office repeats the same elements one level up
        shell = E("Menu", "Underline")  # Word puts an empty Menu first
        root = E("Window", "Doc", kids=[E("Pane", "Lower Ribbon"), shell, outer])
        self.assertEqual([i.name for i in cu.popup_items(root)], ["Underline", "Double underline", "More Underlines..."])

    def test_a_menu_still_rebuilding_is_read_again(self):
        calls = []

        class Flaky(E):
            def children(self):
                calls.append(1)
                if len(calls) <= 2:
                    raise cu.Gone("element not available")
                return iter(self.kids)

        root = Flaky("Window", kids=[E("Menu", "Paste", kids=[E("MenuItem", "Keep Text Only")])])
        real = cu.time.sleep
        cu.time.sleep = lambda s: None
        try:
            self.assertEqual([i.name for i in cu.popup_items(root)], ["Keep Text Only"])
        finally:
            cu.time.sleep = real

    def test_a_popup_that_reports_collapsed_while_open_is_closed_again(self):
        class Drop:
            def __init__(self, stubborn):
                self.open, self.calls, self.stubborn = True, [], stubborn

            def expand_state(self):
                return 1  # never trusted: this drop-down claims to be expanded even when it is closed

            def expand(self):
                self.calls.append("expand")

            def collapse(self):
                self.calls.append("collapse")
                if self.calls.count("expand") >= 1 and not self.stubborn:
                    self.open = False

        drop = Drop(stubborn=False)
        cu.wait_for, real = (lambda test, seconds=0, step=0: test()), cu.wait_for
        try:
            cu.close_popup(drop, lambda: drop.open, "Underline")
            self.assertEqual(drop.calls, ["collapse", "expand", "collapse"])
            stuck = Drop(stubborn=True)
            with self.assertRaises(cu.Refused):
                cu.close_popup(stuck, lambda: stuck.open, "Underline")
        finally:
            cu.wait_for = real
        self.assertEqual(cu.expand_items({"id": "word.home.font.underline"}, None, [E("ListItem", "Wave"), E("ListItem", "")],
                                         cu.Context("word", BUILD, set()))[0]["controlType"], "galleryItem")


class FakeApp:
    def __init__(self, count):
        self.count, self.quit, self.made = count, False, []
        app = self

        class Docs:
            @property
            def Count(self):
                return app.count

            def Add(self):
                app.count += 1
                doc = Doc()
                app.made.append(doc)
                return doc

        class Doc:
            closed = False

            def Close(self, SaveChanges=None):
                self.closed = True
                app.count -= 1

        self.Presentations = self.Documents = Docs()
        self.Visible = False

    def Quit(self, SaveChanges=None):
        self.quit = True


class Proc:
    def __init__(self, pid):
        self.pid, self.closed = pid, False

    def exited(self, seconds):
        return True

    def close(self):
        self.closed = True


class Launch(unittest.TestCase):
    def launched(self, app, key="powerpoint", started=7, window_pid=7):
        real = cu.Launched.running, cu.Win
        cu.Launched.running = staticmethod(lambda exe: False)
        cu.Win = lambda: type("W", (), {"top": lambda self, h: h})()
        app.HWND = 5
        app.ActiveWindow = type("AW", (), {"Hwnd": 5})()
        try:
            return cu.Launched(key, dispatch=lambda progid: app, starter=lambda exe: started,
                               owner=lambda hwnd, exe: Proc(window_pid))
        finally:
            cu.Launched.running, cu.Win = real

    def test_an_instance_that_already_holds_documents_is_never_used_or_closed(self):
        app = FakeApp(count=1)
        real = cu.Launched.running, cu.Win
        cu.Launched.running = staticmethod(lambda exe: False)
        try:
            with self.assertRaises(cu.Unsafe):
                cu.Launched("word", dispatch=lambda progid: app, owner=lambda hwnd, exe: Proc(7))
        finally:
            cu.Launched.running, cu.Win = real
        self.assertEqual((app.count, app.quit, app.made), (1, False, []))

    def test_an_empty_instance_from_another_process_is_never_used(self):
        app = FakeApp(count=0)
        with self.assertRaises(cu.Unsafe):
            self.launched(app, started=7, window_pid=99)  # the operator's PowerPoint answered the COM call
        self.assertEqual((app.count, app.quit, app.made), (0, False, []))

    def test_project_is_refused_until_ownership_can_be_proven(self):
        real = cu.Launched.running
        cu.Launched.running = staticmethod(lambda exe: False)
        try:
            with self.assertRaises(cu.Unsafe):
                cu.Launched("project", dispatch=lambda progid: self.fail("dispatched"), starter=lambda exe: 7)
        finally:
            cu.Launched.running = real

    def test_an_instance_whose_documents_cannot_be_counted_is_left_running(self):
        app = FakeApp(count=0)
        launched = self.launched(app)

        def broken():
            raise OSError("RPC call failed")

        launched.open_documents = broken
        with self.assertRaises(cu.Refused):
            launched.close()
        self.assertFalse(app.quit)

    def test_only_the_tools_own_document_is_closed_and_a_shared_instance_is_left_running(self):
        app = FakeApp(count=0)
        launched = self.launched(app)
        app.count += 1  # the operator opens a presentation in the instance while the capture runs
        with self.assertRaises(cu.Refused):
            launched.close()
        self.assertEqual((app.made[0].closed, app.quit, app.count), (True, False, 1))
        quiet = FakeApp(count=0)
        self.launched(quiet).close()
        self.assertTrue(quiet.quit)

    def test_core_tabs_come_from_the_baseline(self):
        self.assertIn("TabHome", cu.baseline_core_tabs("word"))

    def test_outlook_is_never_started(self):
        with self.assertRaises(cu.Unsafe):
            cu.Launched("outlook")

    def test_a_running_single_instance_app_is_refused(self):
        real = cu.Launched.running
        cu.Launched.running = staticmethod(lambda exe: True)
        try:
            with self.assertRaises(cu.Unsafe):
                cu.Launched("powerpoint", dispatch=lambda progid: self.fail("dispatched into the operator's app"))
        finally:
            cu.Launched.running = real

    def test_an_existing_file_needs_merge_and_unsafe_launch_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "ribbon.json"
            out.write_text("[]", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(cu.main(["--app", "word", "--tab", "Home", "--out", str(out)]), 1)

                def unsafe(app):
                    raise cu.Unsafe("running")

                self.assertEqual(cu.main(["--app", "powerpoint", "--tab", "Home", "--out", str(Path(tmp) / "p.json")],
                                         launcher=unsafe), 2)
            self.assertEqual(out.read_text(encoding="utf-8"), "[]")



class Writes(unittest.TestCase):
    def test_a_missing_app_exits_2_naming_its_process(self):
        def missing(app):
            raise OSError("Invalid class string")

        err = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stderr(err):
            code = cu.main(["--app", "visio", "--tab", "Home", "--out", str(Path(tmp) / "v.json")], launcher=missing)
        self.assertEqual(code, 2)
        self.assertIn("VISIO.EXE could not be started", err.getvalue())

    def test_a_leftover_backup_name_never_replaces_the_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ribbon.json"
            path.write_text("original", encoding="utf-8")
            for stale in (Path(tmp) / "ribbon.json.1.old",):
                stale.write_text("stale", encoding="utf-8")

            def link_fails(src, dst):
                raise OSError("link refused")

            with self.assertRaises(OSError):
                cu.publish({path: "new"}, link=link_fails)
            self.assertEqual(path.read_text(encoding="utf-8"), "original")

    def test_the_destination_never_goes_missing_during_a_replace(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ribbon.json"
            path.write_text("[]" + chr(10), encoding="utf-8")
            seen = []

            def watching_rename(src, dst):
                seen.append(path.exists())
                os.replace(src, dst)
                seen.append(path.exists())

            cu.publish({path: cu.render([{"id": "word.home"}])}, rename=watching_rename)
            self.assertEqual(seen, [True, True])
            self.assertIn("word.home", path.read_text(encoding="utf-8"))
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["ribbon.json"])

    def test_an_interrupted_write_leaves_the_previous_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ribbon.json"
            path.write_text("[]\n", encoding="utf-8")

            def killed(target, data):
                target.write_bytes(data[:5])
                raise KeyboardInterrupt  # the process stops mid-write

            with self.assertRaises(KeyboardInterrupt):
                cu.publish({path: cu.render([{"id": "word.home"}])}, write=killed)
            self.assertEqual(path.read_text(encoding="utf-8"), "[]\n")
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["ribbon.json"])

    def test_transacted_replace_enlists_before_reading_and_rolls_back_on_mismatch(self):
        events = []

        class FakeKtm:
            def CreateTransaction(self, *args):
                events.append("CreateTransaction")
                return 101

            def CommitTransaction(self, tx):
                events.append(("CommitTransaction", tx))
                return 1

            def RollbackTransaction(self, tx):
                events.append(("RollbackTransaction", tx))
                return 1

        class FakeKernel:
            def CreateFileTransactedW(self, dst, access, share, sec, disp, flags, tpl, tx, mv, ext):
                events.append(("CreateFileTransactedW", dst, access, share, tx))
                return 202

            def CreateHardLinkTransactedW(self, backup, dst, sec, tx):
                events.append(("CreateHardLinkTransactedW", backup, dst, tx))
                return 1

            def MoveFileTransactedW(self, src, dst, prog, data, flags, tx):
                events.append(("MoveFileTransactedW", src, dst, flags, tx))
                return 1

            def DeleteFileTransactedW(self, dst, tx):
                events.append(("DeleteFileTransactedW", dst, tx))
                return 1

            def CloseHandle(self, h):
                events.append(("CloseHandle", h))
                return 1

        cu.transacted_replace(
            Path("staged.new"), Path("out.json"), Path("out.old"), b"expected",
            on_enlisted=lambda d: events.append(("on_enlisted", str(d))),
            ktmw32=FakeKtm(), kernel32=FakeKernel(),
            open_osf=lambda h, mode: (events.append(("open_osf", h)) or 303),
            fdopen=lambda fd, mode: io.BytesIO(b"expected"),
        )
        self.assertEqual(events, [
            "CreateTransaction",
            ("CreateFileTransactedW", "out.json", 0x80000000 | 0x00010000, 1, 101),
            ("open_osf", 202),
            ("on_enlisted", "out.json"),
            ("CreateHardLinkTransactedW", "out.old", "out.json", 101),
            ("MoveFileTransactedW", "staged.new", "out.json", 1, 101),
            ("CommitTransaction", 101),
            ("CloseHandle", 101),
        ])
        events.clear()
        with self.assertRaises(cu.Refused):
            cu.transacted_replace(
                Path("staged.new"), Path("out.json"), Path("out.old"), b"expected",
                ktmw32=FakeKtm(), kernel32=FakeKernel(),
                open_osf=lambda h, mode: 303,
                fdopen=lambda fd, mode: io.BytesIO(b"modified_by_editor"),
            )
        self.assertEqual(events, [
            "CreateTransaction",
            ("CreateFileTransactedW", "out.json", 0x80000000 | 0x00010000, 1, 101),
            ("RollbackTransaction", 101),
            ("CloseHandle", 101),
        ])
        # Transacted rollback unlink and restore also enlist in KTM before comparing and roll back on mismatch.
        events.clear()
        self.assertTrue(cu.transacted_unlink(
            Path("out.json"), b"expected", ktmw32=FakeKtm(), kernel32=FakeKernel(),
            open_osf=lambda h, mode: 303, fdopen=lambda fd, mode: io.BytesIO(b"expected"),
        ))
        self.assertEqual(events, [
            "CreateTransaction",
            ("CreateFileTransactedW", "out.json", 0x80000000 | 0x00010000, 1, 101),
            ("DeleteFileTransactedW", "out.json", 101),
            ("CommitTransaction", 101),
            ("CloseHandle", 101),
        ])
        events.clear()
        self.assertFalse(cu.transacted_unlink(
            Path("out.json"), b"expected", ktmw32=FakeKtm(), kernel32=FakeKernel(),
            open_osf=lambda h, mode: 303, fdopen=lambda fd, mode: io.BytesIO(b"edited_after_place"),
        ))
        self.assertEqual(events, [
            "CreateTransaction",
            ("CreateFileTransactedW", "out.json", 0x80000000 | 0x00010000, 1, 101),
            ("RollbackTransaction", 101),
            ("CloseHandle", 101),
        ])
        events.clear()
        self.assertTrue(cu.transacted_restore(
            Path("out.old"), Path("out.json"), b"expected", ktmw32=FakeKtm(), kernel32=FakeKernel(),
            open_osf=lambda h, mode: 303, fdopen=lambda fd, mode: io.BytesIO(b"expected"),
        ))
        self.assertEqual(events, [
            "CreateTransaction",
            ("CreateFileTransactedW", "out.json", 0x80000000 | 0x00010000, 1, 101),
            ("MoveFileTransactedW", "out.old", "out.json", 1, 101),
            ("CommitTransaction", 101),
            ("CloseHandle", 101),
        ])
        events.clear()
        self.assertFalse(cu.transacted_restore(
            Path("out.old"), Path("out.json"), b"expected", ktmw32=FakeKtm(), kernel32=FakeKernel(),
            open_osf=lambda h, mode: 303, fdopen=lambda fd, mode: io.BytesIO(b"edited_after_place"),
        ))
        self.assertEqual(events, [
            "CreateTransaction",
            ("CreateFileTransactedW", "out.json", 0x80000000 | 0x00010000, 1, 101),
            ("RollbackTransaction", 101),
            ("CloseHandle", 101),
        ])

        # If restoration fails transiently (for example a sharing violation on CreateFileTransactedW),
        # the backup is preserved rather than deleted, whereas if dst was superseded by a concurrent save,
        # the backup is unlinked.
        unlinked = []

        class FakeBackupPath:
            def __init__(self, name="out.old"):
                self.name = name

            def __str__(self):
                return self.name

            def exists(self):
                return True

            def unlink(self):
                unlinked.append(self.name)

        class SharingViolationKernel(FakeKernel):
            def CreateFileTransactedW(self, dst, access, share, sec, disp, flags, tpl, tx, mv, ext):
                import ctypes
                ctypes.set_last_error(32)  # ERROR_SHARING_VIOLATION
                events.append(("CreateFileTransactedW_locked", dst))
                return 0

        events.clear()
        self.assertFalse(cu.transacted_restore(
            FakeBackupPath(), Path("out.json"), b"expected", ktmw32=FakeKtm(), kernel32=SharingViolationKernel(),
        ))
        self.assertEqual(unlinked, [])
        self.assertFalse(cu.transacted_restore(
            FakeBackupPath(), Path("out.json"), b"expected", ktmw32=FakeKtm(), kernel32=FakeKernel(),
            open_osf=lambda h, mode: 303, fdopen=lambda fd, mode: io.BytesIO(b"edited_after_place"),
        ))
        self.assertEqual(unlinked, ["out.old"])
        unlink_status = []
        self.assertFalse(cu.transacted_unlink(
            Path("out.json"), b"expected", ktmw32=FakeKtm(), kernel32=SharingViolationKernel(),
            status_out=unlink_status,
        ))
        self.assertEqual(unlink_status, ["failed"])
        unlink_status.clear()
        self.assertFalse(cu.transacted_unlink(
            Path("out.json"), b"expected", ktmw32=FakeKtm(), kernel32=FakeKernel(),
            open_osf=lambda h, mode: 303, fdopen=lambda fd, mode: io.BytesIO(b"edited_after_place"),
            status_out=unlink_status,
        ))
        self.assertEqual(unlink_status, ["superseded"])


class Round3(unittest.TestCase):
    def test_each_apps_build_is_read_in_its_own_form(self):
        word = type("W", (), {"Build": "16.0.20527", "Version": "16.0"})()
        excel = type("X", (), {"Build": 20527, "Version": "16.0"})()
        self.assertEqual((cu.reported_build(word), cu.reported_build(excel)), ("16.0.20527", "16.0.20527"))
        excel_com = type("X", (), {"Build": 20527.0, "Version": "16.0"})()  # what Excel really returns through COM
        self.assertEqual(cu.reported_build(excel_com), "16.0.20527")
        self.assertTrue(cu.same_build(cu.reported_build(excel), BUILD))

    def test_a_classic_capture_needs_the_simplified_layout_off(self):
        class T(E):
            def __init__(self, state):
                super().__init__("Button", "Simplified", "SingleLineRibbonToggle")
                self.state = state

            def toggle_state(self):
                return self.state

        self.assertIsNone(cu.layout_problem(E("Window", kids=[T(0)]), "classic"))
        self.assertIn("Simplified layout", cu.layout_problem(E("Window", kids=[T(1)]), "classic"))
        self.assertIsNone(cu.layout_problem(E("Window"), "classic"))
        self.assertIn("no Simplified Ribbon switch", cu.layout_problem(E("Window"), "simplified"))
        self.assertIn("§15", cu.layout_problem(E("Window", kids=[T(0)]), "simplified"))

    def test_a_document_opened_mid_capture_stops_it(self):
        launched = cu.Launched.__new__(cu.Launched)
        launched.exe, launched.created = "POWERPNT.EXE", [object()]
        launched.open_documents = lambda: 2
        with self.assertRaises(cu.Refused):
            launched.check_alone()
        launched.open_documents = lambda: 1
        launched.check_alone()

    def test_geometry_that_moved_is_dropped(self):
        ctx = cu.Context("word", BUILD, IDS, origin=(0, 0))
        a = {"window": (0, 0, 10, 10), "origin": (0, 0), "dpi": 96, "zoomed": True}
        self.assertTrue(cu.same_geometry(a, dict(a)))
        self.assertFalse(cu.same_geometry(a, dict(a, window=(5, 0, 15, 10))))
        ctx.drop_geometry("moved")
        self.assertIsNone(ctx.origin)
        self.assertIn("no bounds: moved", ctx.notes)

    def test_split_buttons_without_their_own_id_merge_by_idmso(self):
        old = [{"id": "w.g.x", "parent": "w.g", "idMso": "First", "label": "X", "behaviour": "About First."},
               {"id": "w.g.x-second", "parent": "w.g", "idMso": "Second", "label": "X"}]
        new = [{"id": "w.g.x", "parent": "w.g", "idMso": "Second", "label": "X", "order": 0},
               {"id": "w.g.x-first", "parent": "w.g", "idMso": "First", "label": "X", "order": 1}]
        out = {r["idMso"]: r for r in cu.merge(old, new)}
        self.assertEqual((out["First"].get("behaviour"), out["First"]["order"], len(out)), ("About First.", 1, 2))

    def test_expand_reads_items_from_a_separate_popup_window(self):
        class Drop(E):
            def __init__(self):
                super().__init__("MenuItem", "Select", "SelectMenu")
                self.open = False

            def expand_state(self):
                return 1 if self.open else 0

            def expand(self):
                self.open = True

            def collapse(self):
                self.open = False

        drop = Drop()
        popup = E("Window", "Select", kids=[E("MenuItem", "Select All", "SelectAll"), E("MenuItem", "Selection Pane")])
        ctx = cu.Context("word", BUILD, {"SelectMenu", "SelectAll"})
        rec = ctx.base("word.home.editing.select", "control", "Select", 0, drop, parent="word.home.editing",
                       controlType="menu", idMso="SelectMenu")
        launched = type("L", (), {"proc": type("P", (), {"pid": 1})(), "hwnd": 5, "check_alone": lambda self: None})()
        uia = type("U", (), {"element": lambda self, h: popup if h == 77 else E("Window", "Doc")})()
        win = type("W", (), {"popups": lambda self, pid: [77] if drop.open else []})()
        real = cu.wait_for
        cu.wait_for = lambda test, seconds=0, step=0: test()
        try:
            out = cu.expand_all([rec], None, ctx, launched, uia, win)
        finally:
            cu.wait_for = real
        self.assertEqual([r["label"] for r in out[1:]], ["Select All", "Selection Pane"])
        self.assertEqual(out[1]["idMso"], "SelectAll")
        self.assertFalse(drop.open)

    def test_expand_checks_ownership_before_each_ui_action(self):
        class Drop(E):
            def __init__(self, stay_open=False):
                super().__init__("MenuItem", "Select", "SelectMenu")
                self.open, self.calls, self.stay_open = False, [], stay_open

            def expand_state(self):
                return 1 if self.open else 0

            def expand(self):
                self.calls.append("expand")
                self.open = True

            def collapse(self):
                self.calls.append("collapse")
                if not self.stay_open:
                    self.open = False

        real_wait, real_sleep = cu.wait_for, cu.time.sleep
        cu.wait_for = lambda test, seconds=0, step=0: test()
        cu.time.sleep = lambda s: None
        try:
            for fail_on, stay_open, expected_calls in (
                (1, False, []),
                (2, False, ["expand"]),
                (3, True, ["expand", "collapse"]),
                (4, True, ["expand", "collapse", "expand"]),
            ):
                drop = Drop(stay_open=stay_open)
                ctx = cu.Context("word", BUILD, {"SelectMenu"})
                rec = ctx.base("word.home.editing.select", "control", "Select", 0, drop, parent="word.home.editing",
                               controlType="menu", idMso="SelectMenu")
                seen = []

                def check(self, limit=fail_on, counter=seen):
                    counter.append(1)
                    if len(counter) >= limit:
                        raise cu.Refused("now holds 2 documents")

                launched = type("L", (), {"proc": type("P", (), {"pid": 1})(), "hwnd": 5, "check_alone": check})()
                uia = type("U", (), {"element": lambda self, h: E("Window", "Doc")})()
                win = type("W", (), {"popups": lambda self, pid, d=drop: [77] if d.open else []})()
                with self.assertRaises(cu.Refused):
                    cu.expand_all([rec], None, ctx, launched, uia, win)
                self.assertEqual(drop.calls, expected_calls)
        finally:
            cu.wait_for, cu.time.sleep = real_wait, real_sleep

    def test_new_controls_in_verified_groups_carry_baseline_missing(self):
        recs, _ = Walk().records()
        by = {r["label"]: r for r in recs}
        self.assertNotIn("baselineMissing", by["Bold"])
        self.assertIs(by["Font"].get("baselineMissing"), True)
        self.assertIsNone(by["Font"].get("idMso"))
        # An empty unverified group on a verified tab is routed to ctx.unverified, not the main inventory.
        ctx = cu.Context("word", BUILD, IDS)
        lower = E("Pane", "Lower Ribbon", kids=[E("Group", "Home", kids=[E("Group", "EmptyAddin")])])
        tab = E("TabItem", "Home", "TabHome")
        main_recs = cu.walk_tab(tab, 0, lower, ctx)
        self.assertEqual([r["kind"] for r in main_recs], ["tab"])
        self.assertEqual([(r["label"], r["kind"], r["baselineMissing"]) for r in ctx.unverified],
                         [("EmptyAddin", "group", True)])
        self.assertIn("EmptyAddin", ctx.skipped[0])

    def test_replacement_document_and_close_reference_release(self):
        import ctypes
        import threading
        import weakref
        caller_tid = threading.get_ident()
        tids, hresults = [], []

        def record_com():
            tids.append(threading.get_ident())
            apt_type = ctypes.c_int(-1)
            apt_qual = ctypes.c_int(-1)
            hresults.append(ctypes.windll.ole32.CoGetApartmentType(ctypes.byref(apt_type), ctypes.byref(apt_qual)))

        app = FakeApp(count=0)
        real_add = app.Presentations.Add
        app.Presentations.Add = lambda: (record_com(), real_add())[1]
        launched = Launch().launched(app)
        launched.check_alone()
        launched._apartment.call(record_com)
        self.assertEqual(hresults, [0, 0])
        self.assertEqual(len(set(tids)), 1)
        self.assertNotEqual(tids[0], caller_tid)
        # Closing the tool's document and opening an operator document keeps Count == 1, but must be refused.
        app.made[0].Close()
        real_add()
        self.assertEqual(launched.open_documents(), 1)
        with self.assertRaises(cu.Refused):
            launched.check_alone()
        with self.assertRaises(cu.Refused):
            launched.close()
        self.assertFalse(app.quit)
        launched._apartment.close()
        # Verify loop reference is released before proc.exited() waits.
        q_launched = Launch().launched(FakeApp(count=0))
        doc_ref = weakref.ref(q_launched.created[0])
        alive_during_wait = []
        q_launched.proc.exited = lambda seconds: (alive_during_wait.append(doc_ref() is not None) or True)
        q_launched.close()
        self.assertEqual(alive_during_wait, [False])
        # Verify blocked COM initialization is bounded by init_timeout and cleans up the apartment and instance.
        import time
        unblock = threading.Event()
        late_app = FakeApp(0)
        created_apt = []
        orig_apt_init = cu._Apartment.__init__

        def track_apt(apt_self, *args, **kwargs):
            orig_apt_init(apt_self, *args, **kwargs)
            created_apt.append(apt_self)

        cu._Apartment.__init__ = track_apt
        try:
            t0 = time.monotonic()
            with self.assertRaises(cu.Refused) as err:
                cu.Launched("word", dispatch=lambda p: (unblock.wait(2.0), late_app)[1], init_timeout=0.05)
            elapsed = time.monotonic() - t0
            unblock.set()
            created_apt[-1]._thread.join(timeout=1.0)
            self.assertFalse(created_apt[-1]._thread.is_alive())
            self.assertLess(elapsed, 1.0)
            self.assertIn("did not finish starting", str(err.exception))
            self.assertEqual(len(late_app.made), 0)
            self.assertTrue(late_app.quit)
            # Also verify if Documents.Add() blocks past init_timeout, the late document is closed and app quits.
            unblock_add = threading.Event()
            late_doc_app = FakeApp(0)
            orig_doc_add = late_doc_app.Documents.Add
            late_doc_app.Documents.Add = lambda: (unblock_add.wait(2.0), orig_doc_add())[1]
            with self.assertRaises(cu.Refused):
                cu.Launched("word", dispatch=lambda p: late_doc_app, init_timeout=0.05)
            unblock_add.set()
            created_apt[-1]._thread.join(timeout=1.0)
            self.assertFalse(created_apt[-1]._thread.is_alive())
            self.assertEqual(len(late_doc_app.made), 1)
            self.assertTrue(late_doc_app.made[0].closed)
            self.assertTrue(late_doc_app.quit)
        finally:
            cu._Apartment.__init__ = orig_apt_init
        # Verify in a real child subprocess that exits immediately after cu.main() returns 2 on launch timeout:
        # 1) When Documents.Add() outlasts both init_timeout and _recover_hung_launch's initial join (e.g. 0.9s delay
        #    with init_timeout=0.05, so doc_closed and quit are still False when main() returns 2), _Apartment's
        #    bounded atexit hook waits for the delayed Documents.Add() to finish and runs cleanup before exit.
        import subprocess
        import sys
        probe_delayed = (
            "import atexit, importlib.util, json, sys, time\n"
            f"spec = importlib.util.spec_from_file_location('cu', {str(SCRIPTS / 'capture-ui.py')!r})\n"
            "cu = importlib.util.module_from_spec(spec); spec.loader.exec_module(cu)\n"
            "state = {'doc_closed': False, 'quit': False}\n"
            "class Doc:\n"
            "    Name = 'Doc1'; FullName = 'Doc1'\n"
            "    def Close(self, SaveChanges=0): state['doc_closed'] = True; Docs.Count = 0\n"
            "class Docs:\n"
            "    Count = 0\n"
            "    def Add(self): time.sleep(0.9); Docs.Count = 1; return Doc()\n"
            "    def __iter__(self): return iter([])\n"
            "class App:\n"
            "    Visible = False; Documents = Docs()\n"
            "    def Quit(self, SaveChanges=0): state['quit'] = True\n"
            "atexit.register(lambda: print('ATEXIT:' + json.dumps(state), flush=True))\n"
            "rc = cu.main(['--app', 'word', '--tab', 'Home', '--merge', '--out', 'nonexistent_out.json'],\n"
            "             launcher=lambda app: cu.Launched(app, dispatch=lambda p: App(), init_timeout=0.05))\n"
            "print('AT_MAIN_RETURN:' + json.dumps(state), flush=True)\n"
            "print('MAIN_RC:' + str(rc), flush=True)\n"
            "sys.exit(rc)\n"
        )
        proc = subprocess.run([sys.executable, "-c", probe_delayed], capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("MAIN_RC:2", proc.stdout)
        self.assertIn('AT_MAIN_RETURN:{"doc_closed": false, "quit": false}', proc.stdout)
        self.assertIn('ATEXIT:{"doc_closed": true, "quit": true}', proc.stdout)
        # 2) When an owned instance's Documents.Add() blocks beyond the atexit shutdown budget (waits on an unset
        #    Event forever), ownership (hwnd and proc) is bound before Documents.Add(), and _abandon_hung_launch
        #    closes any open document, calls App.Quit(), and closes proc before the CLI process exits with code 2.
        probe_hung_add = (
            "import atexit, importlib.util, json, sys, threading\n"
            f"spec = importlib.util.spec_from_file_location('cu', {str(SCRIPTS / 'capture-ui.py')!r})\n"
            "cu = importlib.util.module_from_spec(spec); spec.loader.exec_module(cu)\n"
            "cu.Win = lambda: type('W', (), {'top': lambda self, h: h})()\n"
            "never = threading.Event()\n"
            "state = {'bound_before_add': False, 'doc_closed': False, 'quit': False, 'proc_closed': False}\n"
            "class Proc:\n"
            "    pid = 77\n"
            "    def exited(self, s): return True\n"
            "    def close(self): state['proc_closed'] = True\n"
            "class Doc:\n"
            "    Name = 'Doc1'; FullName = 'Doc1'; closed = False\n"
            "    def Close(self, SaveChanges=0): self.closed = True; state['doc_closed'] = True; Docs.items.clear()\n"
            "class Docs:\n"
            "    items = []\n"
            "    @property\n"
            "    def Count(self): return len(self.items)\n"
            "    def Add(self):\n"
            "        self.items.append(Doc())\n"
            "        never.wait()\n"
            "        return self.items[-1]\n"
            "    def __iter__(self): return iter(list(self.items))\n"
            "class App:\n"
            "    Visible = False; Documents = Docs()\n"
            "    ActiveWindow = type('AW', (), {'Hwnd': 42})()\n"
            "    def Quit(self, SaveChanges=0): state['quit'] = True\n"
            "def make_owner(hwnd, exe):\n"
            "    if not Docs.items:\n"
            "        state['bound_before_add'] = True\n"
            "    return Proc()\n"
            "atexit.register(lambda: print('ATEXIT:' + json.dumps(state), flush=True))\n"
            "rc = cu.main(['--app', 'word', '--tab', 'Home', '--merge', '--out', 'nonexistent_out.json'],\n"
            "             launcher=lambda app: cu.Launched(app, dispatch=lambda p: App(), owner=make_owner, init_timeout=0.05))\n"
            "print('AT_MAIN_RETURN:' + json.dumps(state), flush=True)\n"
            "print('MAIN_RETURNED:' + str(rc), flush=True)\n"
            "sys.exit(rc)\n"
        )
        proc_hung_add = subprocess.run([sys.executable, "-c", probe_hung_add], capture_output=True, text=True, timeout=3.5)
        self.assertEqual(proc_hung_add.returncode, 2, proc_hung_add.stderr)
        self.assertIn("MAIN_RETURNED:2", proc_hung_add.stdout)
        self.assertIn(
            'AT_MAIN_RETURN:{"bound_before_add": true, "doc_closed": false, "quit": false, "proc_closed": false}',
            proc_hung_add.stdout,
        )
        self.assertIn(
            'ATEXIT:{"bound_before_add": true, "doc_closed": true, "quit": true, "proc_closed": true}',
            proc_hung_add.stdout,
        )
        # 3) When dispatch itself is permanently hung before ownership is established, the CLI exits promptly with code 2.
        probe_hung = (
            "import importlib.util, sys, threading\n"
            f"spec = importlib.util.spec_from_file_location('cu', {str(SCRIPTS / 'capture-ui.py')!r})\n"
            "cu = importlib.util.module_from_spec(spec); spec.loader.exec_module(cu)\n"
            "never = threading.Event()\n"
            "rc = cu.main(['--app', 'word', '--tab', 'Home', '--merge', '--out', 'nonexistent_out.json'],\n"
            "             launcher=lambda app: cu.Launched(app, dispatch=lambda p: never.wait(), init_timeout=0.05))\n"
            "print('MAIN_RETURNED:' + str(rc), flush=True)\n"
            "sys.exit(rc)\n"
        )
        proc_hung = subprocess.run([sys.executable, "-c", probe_hung], capture_output=True, text=True, timeout=3.5)
        self.assertEqual(proc_hung.returncode, 2, proc_hung.stderr)
        self.assertIn("MAIN_RETURNED:2", proc_hung.stdout)


class Worker(unittest.TestCase):
    def test_the_parent_answers_ownership_checks_until_the_outcome(self):
        replies, checks = [], []
        launched = type("L", (), {"check_alone": lambda self: checks.append(1)})()
        lines = [json.dumps({"ask": "check_alone"}), json.dumps({"ask": "check_alone"}),
                 json.dumps({"result": {"records": []}}), json.dumps({"never": "read"})]
        outcome = cu.converse(iter(lines), replies.append, launched)
        self.assertEqual((outcome, replies, len(checks)), ({"result": {"records": []}}, ["ok", "ok"], 2))

    def test_a_failed_check_is_answered_with_its_reason(self):
        def refuse(self):
            raise cu.Refused("now holds 2 documents")

        replies = []
        cu.converse(iter([json.dumps({"ask": "check_alone"}), json.dumps({"refused": "x"})]), replies.append,
                    type("L", (), {"check_alone": refuse})())
        self.assertEqual(replies, ["now holds 2 documents"])
        proxy = cu.Proxy({"hwnd": 1, "pid": 2, "build": "16.0.20527", "language": 1033}, lambda q: "now holds 2")
        with self.assertRaises(cu.Refused):
            proxy.check_alone()
        self.assertEqual((proxy.language(), cu.reported_build(proxy.app)), (1033, "16.0.20527"))

    def test_a_worker_that_ends_silently_is_a_refusal(self):
        self.assertIn("refused", cu.converse(iter([]), lambda r: None, None))

    def test_capture_in_worker_enforces_timeout_and_roundtrips_results(self):
        import argparse
        import ctypes
        import sys
        import time
        args = argparse.Namespace(app="word", tab="Home", all_tabs=False, expand=False, layout="classic",
                                  merge=False, out=None)
        checks = []

        def check_with_com(self):
            apt_type = ctypes.c_int(-1)
            apt_qual = ctypes.c_int(-1)
            hr = ctypes.windll.ole32.CoGetApartmentType(ctypes.byref(apt_type), ctypes.byref(apt_qual))
            checks.append(hr)

        launched = type("L", (), {"hwnd": 5, "proc": type("P", (), {"pid": 7})(),
                                  "app": type("A", (), {"Build": "16.0.20527", "Version": "16.0"})(),
                                  "language": lambda self: 1033, "check_alone": check_with_com})()
        t0 = time.monotonic()
        with self.assertRaises(cu.Refused) as ctx_err:
            cu.capture_in_worker(args, launched, timeout=0.15,
                                 worker_cmd=[sys.executable, "-c", "import time; time.sleep(5)"])
        self.assertLess(time.monotonic() - t0, 2.0)
        self.assertIn("timed out", str(ctx_err.exception))
        script = (
            "import json, sys\n"
            "spec = json.loads(sys.stdin.readline())\n"
            "print(json.dumps({'ask': 'check_alone'}), flush=True)\n"
            "ans = json.loads(sys.stdin.readline())['answer']\n"
            "assert ans == 'ok'\n"
            "print(json.dumps({'result': {'records': [{'id': 'word.home'}], 'problems': [], "
            "'skipped': ['s'], 'notes': ['n'], 'unverified': [{'id': 'word.u'}]}}), flush=True)\n"
        )
        recs, problems, ctx = cu.capture_in_worker(args, launched, timeout=5.0,
                                                   worker_cmd=[sys.executable, "-c", script])
        self.assertEqual((recs, problems, ctx.skipped, ctx.notes, ctx.unverified, checks),
                         ([{"id": "word.home"}], [], ["s"], ["n"], [{"id": "word.u"}], [0]))
        # A parent-side ownership check that hangs is also bounded by the worker deadline.
        slow_launched = type("L", (), {"hwnd": 5, "proc": type("P", (), {"pid": 7})(),
                                       "app": type("A", (), {"Build": "16.0.20527", "Version": "16.0"})(),
                                       "language": lambda self: 1033,
                                       "check_alone": lambda self: time.sleep(1.5)})()
        t1 = time.monotonic()
        with self.assertRaises(cu.Refused) as slow_err:
            cu.capture_in_worker(args, slow_launched, timeout=0.2,
                                 worker_cmd=[sys.executable, "-c", script])
        self.assertLess(time.monotonic() - t1, 1.0)
        self.assertIn("timed out", str(slow_err.exception))


class CaptureIntegration(unittest.TestCase):
    def _window_tree(self, extra_kids=()):
        tab, lower = home()
        tab.select = lambda: None
        lower.rect = (0, 80, 1920, 200)
        tabs_bar = E("Tab", "Ribbon Tabs", kids=[tab])
        return E("Window", "Document1 - Word", kids=[tabs_bar, lower, *extra_kids])

    def test_capture_refuses_licensing_or_activation_notice(self):
        import argparse
        args = argparse.Namespace(app="word", tab="Home", all_tabs=False, expand=False, layout="classic",
                                  merge=False, out=None)
        launched = type("L", (), {"hwnd": 5, "proc": type("P", (), {"pid": 7})(),
                                  "app": type("A", (), {"Build": "16.0.20527", "Version": "16.0"})(),
                                  "language": lambda self: 1033, "check_alone": lambda self: None})()
        win = type("W", (), {"monitors": lambda self: [Profile.MONITOR], "place": lambda self, h, m: None,
                             "state": lambda self, h: dict(Profile.GOOD, origin=(0, 0), monitor=1)})()
        root = self._window_tree(extra_kids=[E("Pane", "Unlicensed Product - Most features are disabled")])
        uia = type("U", (), {"element": lambda self, h: root})()
        real_ib, real_sleep = cu.installed_build, cu.time.sleep
        cu.installed_build = lambda: BUILD
        cu.time.sleep = lambda s: None
        try:
            with self.assertRaises(cu.Refused) as err:
                cu.capture(args, launched, uia, win)
            self.assertIn("licence or activation notice", str(err.exception))
        finally:
            cu.installed_build, cu.time.sleep = real_ib, real_sleep

    def test_geometry_invalidation_strips_sidecar_bounds_and_reports_no_bounds(self):
        root = self._window_tree()
        states = [
            dict(Profile.GOOD, origin=(0, 0), monitor=1),
            dict(Profile.GOOD, origin=(0, 0), monitor=1),
            dict(Profile.GOOD, window=(10, 10, 1930, 1090), origin=(10, 10), monitor=1),
        ]
        launched = type("L", (), {"hwnd": 5, "proc": type("P", (), {"pid": 7})(),
                                  "app": type("A", (), {"Build": "16.0.20527", "Version": "16.0"})(),
                                  "language": lambda self: 1033, "check_alone": lambda self: None,
                                  "close": lambda self: None})()
        win = type("W", (), {"monitors": lambda self: [Profile.MONITOR], "place": lambda self, h, m: None,
                             "state": lambda self, h: states.pop(0) if len(states) > 1 else states[0]})()
        uia = type("U", (), {"element": lambda self, h: root})()
        real_ib, real_sleep, real_unv = cu.installed_build, cu.time.sleep, cu.UNVERIFIED
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "home.json"
            cu.installed_build = lambda: BUILD
            cu.time.sleep = lambda s: None
            cu.UNVERIFIED = Path(tmp) / "unverified"
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    rc = cu.main(["--app", "word", "--tab", "Home", "--out", str(out_path)],
                                 launcher=lambda app: launched, uia_factory=lambda: uia, win_factory=lambda: win)
            finally:
                cu.installed_build, cu.time.sleep, cu.UNVERIFIED = real_ib, real_sleep, real_unv
            self.assertEqual(rc, 0)
            written = json.loads(out_path.read_text(encoding="utf-8"))
            sidecar = json.loads((Path(tmp) / "unverified" / "word-unverified.json").read_text(encoding="utf-8"))
            self.assertTrue(written and sidecar)
            for rec in written + sidecar:
                for key in ("bounds", "captureProfile", "size"):
                    self.assertNotIn(key, rec)
            self.assertIn("; no bounds: the window moved or changed size during the capture", buf.getvalue())
            self.assertNotIn("bounds recorded under", buf.getvalue())

    def test_concurrent_create_or_modify_is_never_overwritten(self):
        root = self._window_tree()
        win = type("W", (), {"monitors": lambda self: [Profile.MONITOR], "place": lambda self, h, m: None,
                             "state": lambda self, h: dict(Profile.GOOD, origin=(0, 0), monitor=1)})()
        real_ib, real_sleep, real_unv = cu.installed_build, cu.time.sleep, cu.UNVERIFIED
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "home.json"
            cu.installed_build = lambda: BUILD
            cu.time.sleep = lambda s: None
            cu.UNVERIFIED = Path(tmp) / "unverified"
            try:
                # 1. File created concurrently during a non-merge capture is not overwritten.
                def uia_creates_file():
                    out_path.write_text('[{"id": "word.concurrent"}]\n', encoding="utf-8")
                    return type("U", (), {"element": lambda self, h: root})()

                launched = type("L", (), {"hwnd": 5, "proc": type("P", (), {"pid": 7})(),
                                          "app": type("A", (), {"Build": "16.0.20527", "Version": "16.0"})(),
                                          "language": lambda self: 1033, "check_alone": lambda self: None,
                                          "close": lambda self: None})()
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    rc = cu.main(["--app", "word", "--tab", "Home", "--out", str(out_path)],
                                 launcher=lambda app: launched, uia_factory=uia_creates_file, win_factory=lambda: win)
                self.assertEqual(rc, 1)
                self.assertEqual(out_path.read_text(encoding="utf-8"), '[{"id": "word.concurrent"}]\n')

                # 2. File modified concurrently during a --merge capture is not overwritten.
                def uia_modifies_file():
                    out_path.write_text('[{"id": "word.edited"}]\n', encoding="utf-8")
                    return type("U", (), {"element": lambda self, h: root})()

                with contextlib.redirect_stderr(io.StringIO()):
                    rc = cu.main(["--app", "word", "--tab", "Home", "--merge", "--out", str(out_path)],
                                 launcher=lambda app: launched, uia_factory=uia_modifies_file, win_factory=lambda: win)
                self.assertEqual(rc, 1)
                self.assertEqual(out_path.read_text(encoding="utf-8"), '[{"id": "word.edited"}]\n')

                # 3. During transactional publish, a concurrent atomic save or write after byte comparison and before
                # MoveFileTransactedW is kernel-blocked (ERROR_TRANSACTIONAL_CONFLICT) so editor work is never lost.
                import os
                orig_bytes = out_path.read_bytes()
                editor_tmp = out_path.with_name("editor.tmp")
                editor_tmp.write_text('[{"id": "word.saved_during_tx"}]\n', encoding="utf-8")
                conflict_errors = []

                def attempt_concurrent_atomic_save_after_check(enlisted_dst):
                    with self.assertRaises(OSError) as ctx_os:
                        os.replace(editor_tmp, enlisted_dst)
                    conflict_errors.append(ctx_os.exception.winerror)
                    with self.assertRaises(OSError) as ctx_write:
                        Path(enlisted_dst).write_text('[{"id": "word.in_place"}]\n', encoding="utf-8")
                    conflict_errors.append(ctx_write.exception.winerror)

                cu.publish({out_path: '[{"id": "word.ours"}]\n'}, expected_bytes={out_path: orig_bytes},
                           on_enlisted=attempt_concurrent_atomic_save_after_check)
                self.assertEqual(conflict_errors[0], 6800)
                self.assertEqual(len(conflict_errors), 2)
                self.assertEqual(editor_tmp.read_text(encoding="utf-8"), '[{"id": "word.saved_during_tx"}]\n')
                self.assertEqual(out_path.read_text(encoding="utf-8"), '[{"id": "word.ours"}]\n')

                # 4. If a failure occurs while enlisted before commit, KTM rolls back leaving destination untouched.
                orig_bytes2 = out_path.read_bytes()
                with self.assertRaises(cu.Refused):
                    cu.publish({out_path: '[{"id": "word.ours2"}]\n'}, expected_bytes={out_path: orig_bytes2},
                               on_enlisted=lambda d: (_ for _ in ()).throw(cu.Refused("aborted in tx")))
                self.assertEqual(out_path.read_bytes(), orig_bytes2)

                # 5. Rollback of a newly created output does not delete concurrent edits made before a second file fails.
                new_out = Path(tmp) / "fresh.json"
                second_out = Path(tmp) / "sidecar.json"

                def link_edits_first_then_fails_second(src, dst):
                    if Path(dst) == new_out:
                        os.link(src, dst)
                        return
                    new_out.write_text('[{"id": "word.annotated_by_operator"}]\n', encoding="utf-8")
                    raise OSError("simulated failure on second output")

                with self.assertRaises(OSError):
                    cu.publish({new_out: '[{"id": "word.initial"}]\n', second_out: '[]\n'},
                               link=link_edits_first_then_fails_second, create_only={new_out, second_out})
                self.assertTrue(new_out.exists())
                self.assertEqual(new_out.read_text(encoding="utf-8"), '[{"id": "word.annotated_by_operator"}]\n')

                # 6. If rollback restoration fails due to a sharing violation, the backup copy is preserved and reported.
                import ctypes
                first_existing = Path(tmp) / "first_existing.json"
                second_existing = Path(tmp) / "second_existing.json"
                first_existing.write_text('[{"id": "word.original_recovery"}]\n', encoding="utf-8")
                second_existing.write_text('[{"id": "word.second_orig"}]\n', encoding="utf-8")
                lock_handles = []

                def rename_locks_first_then_fails_second(src, dst):
                    if Path(dst) == first_existing:
                        os.replace(src, dst)
                        # Open first_existing without FILE_SHARE_DELETE (share=1, FILE_SHARE_READ only) so rollback fails.
                        h = ctypes.windll.kernel32.CreateFileW(
                            str(first_existing), 0x80000000, 1, None, 3, 0, None
                        )
                        lock_handles.append(h)
                        return
                    raise OSError("simulated failure on second output")

                err_buf = io.StringIO()
                try:
                    with contextlib.redirect_stderr(err_buf), self.assertRaises(OSError):
                        cu.publish({first_existing: '[{"id": "word.new1"}]\n',
                                    second_existing: '[{"id": "word.new2"}]\n'},
                                   rename=rename_locks_first_then_fails_second)
                finally:
                    for h in lock_handles:
                        ctypes.windll.kernel32.CloseHandle(h)
                backups = list(Path(tmp).glob("first_existing.json.*.old"))
                self.assertEqual(len(backups), 1)
                self.assertEqual(backups[0].read_text(encoding="utf-8"), '[{"id": "word.original_recovery"}]\n')
                self.assertIn("backup kept at", err_buf.getvalue())

                # 7. If rollback deletion of a newly created output fails due to a sharing violation, publish reports it.
                first_new_locked = Path(tmp) / "first_new_locked.json"
                second_new_locked = Path(tmp) / "second_new_locked.json"
                new_lock_handles = []

                def link_locks_first_then_fails_second(src, dst):
                    if Path(dst) == first_new_locked:
                        os.link(src, dst)
                        h = ctypes.windll.kernel32.CreateFileW(
                            str(first_new_locked), 0x80000000, 1, None, 3, 0, None
                        )
                        new_lock_handles.append(h)
                        return
                    raise OSError("simulated failure on second newly created output")

                err_buf_new = io.StringIO()
                try:
                    with contextlib.redirect_stderr(err_buf_new), self.assertRaises(OSError) as cm_new:
                        cu.publish({first_new_locked: '[{"id": "word.new_locked"}]\n',
                                    second_new_locked: '[]\n'},
                                   link=link_locks_first_then_fails_second,
                                   create_only={first_new_locked, second_new_locked})
                finally:
                    for h in new_lock_handles:
                        ctypes.windll.kernel32.CloseHandle(h)
                self.assertIn("rollback could not remove newly created", err_buf_new.getvalue())
                self.assertIn(str(first_new_locked), err_buf_new.getvalue())
                if hasattr(cm_new.exception, "__notes__"):
                    self.assertTrue(any("rollback could not remove newly created" in n for n in cm_new.exception.__notes__))
            finally:
                cu.installed_build, cu.time.sleep, cu.UNVERIFIED = real_ib, real_sleep, real_unv


if __name__ == "__main__":
    unittest.main()
