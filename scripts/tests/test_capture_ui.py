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

    def test_a_popup_that_never_stabilises_is_refused(self):
        step = [0]

        class GrowingMenu(E):
            def children(self):
                step[0] += 1
                return iter([E("MenuItem", f"Item {i}") for i in range(1, min(step[0], 4) + 1)])

        root = E("Window", "Doc", kids=[GrowingMenu("Menu", "Styles")])
        clock = [0.0]

        def fake_monotonic():
            val = clock[0]
            clock[0] += 1.0  # 4 readings before 4.0s deadline expires, each with 1, 2, 3, 4 items
            return val

        real_sleep, real_mono = cu.time.sleep, cu.time.monotonic
        cu.time.sleep = lambda s: None
        cu.time.monotonic = fake_monotonic
        try:
            with self.assertRaises(cu.Refused) as err:
                cu.popup_items(root, label="Styles")
            self.assertIn("did not stabilise", str(err.exception))
        finally:
            cu.time.sleep, cu.time.monotonic = real_sleep, real_mono

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

        # Non-TxF volumes (WinError 6832) hold h_lock open via CreateFileW across verification, on_enlisted,
        # CreateHardLinkW, and SetFileInformationByHandle before closing h_lock.
        class NoTxfKernel(FakeKernel):
            def CreateFileTransactedW(self, dst, access, share, sec, disp, flags, tpl, tx, mv, ext):
                import ctypes
                ctypes.set_last_error(6832)
                events.append(("CreateFileTransactedW_no_txf", dst))
                return 0

            def CreateMutexW(self, sec, initial, name):
                events.append("CreateMutexW")
                return 401

            def WaitForSingleObject(self, h, ms):
                events.append(("WaitForSingleObject", h))
                return 0

            def ReleaseMutex(self, h):
                events.append(("ReleaseMutex", h))
                return 1

            def CreateFileW(self, path, access, share, sec, disp, flags, tpl):
                h = 502 if str(path).endswith("staged.new") or str(path).endswith("out.old") else 501
                events.append(("CreateFileW", str(path), access, share, h))
                return h

            def CreateHardLinkW(self, backup, dst, sec):
                events.append(("CreateHardLinkW", backup, dst))
                return 1

            def SetFileInformationByHandle(self, h, info_class, buf, size):
                import ctypes
                raw = ctypes.string_at(buf, size) if info_class == 22 else b""
                events.append(("SetFileInformationByHandle", h, info_class, raw))
                return 1

        events.clear()
        unicode_dst = Path("capture-\U0001f4c4.json")
        cu.transacted_replace(
            Path("staged.new"), unicode_dst, Path("out.old"), b"expected",
            on_enlisted=lambda d: events.append(("on_enlisted", str(d))),
            ktmw32=FakeKtm(), kernel32=NoTxfKernel(),
            open_osf=lambda h, mode: (events.append(("open_osf", h)) or 303),
            fdopen=lambda fd, mode: io.BytesIO(b"expected"),
        )
        rename_idx, rename_raw = next(
            (idx, e[3]) for idx, e in enumerate(events)
            if isinstance(e, tuple) and e[:3] == ("SetFileInformationByHandle", 502, 22)
        )
        # h_lock (501) is opened with FILE_SHARE_READ | FILE_SHARE_DELETE (1 | 4, excluding FILE_SHARE_WRITE)
        # and closed only AFTER SetFileInformationByHandle(502, 22), and supplementary Unicode
        # characters in the destination path encode their full UTF-16LE byte length without truncating the tail.
        self.assertIn(("CreateFileW", str(unicode_dst), 0x80000000, 1 | 4, 501), events)
        self.assertLess(rename_idx, events.index(("CloseHandle", 501)))
        import ctypes as _ct, os as _os
        len_off = _ct.sizeof(_ct.c_void_p) * 2
        fn_len = int.from_bytes(rename_raw[len_off:len_off + 4], "little")
        decoded_dst = rename_raw[len_off + 4:len_off + 4 + fn_len].decode("utf-16-le")
        self.assertEqual(decoded_dst, _os.path.abspath(str(unicode_dst)))
        events.clear()
        self.assertTrue(cu.transacted_unlink(
            Path("out.json"), b"expected",
            on_enlisted=lambda d: events.append(("on_enlisted", str(d))),
            ktmw32=FakeKtm(), kernel32=NoTxfKernel(),
            open_osf=lambda h, mode: 303, fdopen=lambda fd, mode: io.BytesIO(b"expected"),
        ))
        self.assertIn(("CreateFileW", "out.json", 0x80000000 | 0x00010000, 1, 501), events)
        self.assertLess(
            events.index(("SetFileInformationByHandle", 501, 13, b"")),
            events.index(("CloseHandle", 501)),
        )
        events.clear()
        self.assertFalse(cu.transacted_unlink(
            Path("out.json"), b"expected",
            ktmw32=FakeKtm(), kernel32=NoTxfKernel(),
            open_osf=lambda h, mode: 303, fdopen=lambda fd, mode: io.BytesIO(b"modified"),
            status_out=unlink_status,
        ))
        self.assertNotIn(("SetFileInformationByHandle", 501, 13, b""), events)
        events.clear()
        unlinked.clear()
        self.assertFalse(cu.transacted_restore(
            FakeBackupPath(), Path("out.json"), b"expected",
            ktmw32=FakeKtm(), kernel32=NoTxfKernel(),
            open_osf=lambda h, mode: 303, fdopen=lambda fd, mode: io.BytesIO(b"modified"),
        ))
        self.assertIn(("CreateFileW", "out.json", 0x80000000, 1 | 4, 501), events)
        self.assertEqual(unlinked, ["out.old"])
        self.assertFalse(any(isinstance(e, tuple) and e[0] == "SetFileInformationByHandle" for e in events))

        # If unlinking the staged temporary file fails after link() creates a create_only destination,
        # the destination is already registered in placed and rolled back via transacted_unlink.
        import unittest.mock as _mock
        rolled_back = []
        with _mock.patch("tempfile.mkstemp", side_effect=[(11, "main.json.1.new"), (12, "side.json.2.new")]), \
             _mock.patch("os.close"), \
             _mock.patch.object(Path, "mkdir"), \
             _mock.patch.object(Path, "read_bytes", side_effect=[b"main", b"side"]), \
             _mock.patch.object(Path, "exists", return_value=True), \
             _mock.patch.object(Path, "unlink", side_effect=[PermissionError("scanner lock"), None]), \
             _mock.patch("office_com.transacted_unlink", side_effect=lambda p, b, status_out=None: (rolled_back.append((str(p), b)) or True)):
            with self.assertRaises(PermissionError):
                cu.publish(
                    {Path("main.json"): "main", Path("side.json"): "side"},
                    write=lambda p, d: None,
                    link=lambda s, d: None,
                    create_only={Path("main.json"), Path("side.json")},
                )
        self.assertEqual(rolled_back, [("main.json", b"main")])

        # If unlinking a backup (.old) fails after all destinations have been replaced, publish()
        # preserves the committed outcome (does not raise or roll back), attempts cleanup of every
        # remaining backup, and reports the retained backup path on stderr.
        unlinked_backups = []

        def unlink_fails_on_first_old(self_path):
            name = str(self_path)
            unlinked_backups.append(name)
            if name.startswith("main.json.") and name.endswith(".old"):
                raise PermissionError("scanner holds backup")

        err_cleanup = io.StringIO()
        with _mock.patch("tempfile.mkstemp", side_effect=[(11, "main.json.1.new"), (12, "side.json.2.new")]), \
             _mock.patch("os.close"), \
             _mock.patch.object(Path, "mkdir"), \
             _mock.patch.object(Path, "read_bytes", side_effect=[b"main", b"side"]), \
             _mock.patch.object(Path, "is_file", return_value=True), \
             _mock.patch.object(Path, "exists", return_value=True), \
             _mock.patch.object(Path, "unlink", autospec=True, side_effect=unlink_fails_on_first_old), \
             contextlib.redirect_stderr(err_cleanup):
            cu.publish(
                {Path("main.json"): "main", Path("side.json"): "side"},
                write=lambda p, d: None,
                link=lambda s, d: None,
                rename=lambda s, d: None,
            )
        self.assertEqual(len(unlinked_backups), 2)
        self.assertIn("publish: backup cleanup could not remove main.json.", err_cleanup.getvalue())


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
        unv_drop = Drop()
        popup = E("Window", "Select", kids=[E("MenuItem", "Select All", "SelectAll"), E("MenuItem", "Selection Pane")])
        ctx = cu.Context("word", BUILD, {"SelectMenu", "SelectAll"})
        rec = ctx.base("word.home.editing.select", "control", "Select", 0, drop, parent="word.home.editing",
                       controlType="menu", idMso="SelectMenu")
        unv_group = ctx.base("word.home.addin", "group", "Addin", 1, E("Group", "Addin"), parent="word.home",
                             baselineMissing=True)
        unv_rec = ctx.base("word.home.addin.menu", "control", "AddinMenu", 0, unv_drop, parent="word.home.addin",
                           controlType="menu", baselineMissing=True)
        ctx.unverified.extend([unv_group, unv_rec])
        launched = type("L", (), {"proc": type("P", (), {"pid": 1})(), "hwnd": 5, "check_alone": lambda self: None})()
        uia = type("U", (), {"element": lambda self, h: popup if h == 77 else E("Window", "Doc")})()
        win = type("W", (), {"popups": lambda self, pid: [77] if (drop.open or unv_drop.open) else []})()
        real, real_sleep = cu.wait_for, cu.time.sleep
        cu.wait_for = lambda test, seconds=0, step=0: test()
        cu.time.sleep = lambda s: None
        try:
            out = cu.expand_all([rec], None, ctx, launched, uia, win, unverified_start=0)
        finally:
            cu.wait_for, cu.time.sleep = real, real_sleep
        self.assertEqual([r["label"] for r in out[1:]], ["Select All", "Selection Pane"])
        self.assertEqual(out[1]["idMso"], "SelectAll")
        self.assertFalse(drop.open)
        self.assertFalse(unv_drop.open)
        self.assertEqual(
            [(r["kind"], r["label"], r.get("parent"), r.get("baselineMissing")) for r in ctx.unverified],
            [
                ("group", "Addin", "word.home", True),
                ("control", "AddinMenu", "word.home.addin", True),
                ("menuItem", "Select All", "word.home.addin.menu", True),
                ("menuItem", "Selection Pane", "word.home.addin.menu", True),
            ],
        )

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
            "import atexit, ctypes, importlib.util, json, sys, threading, time\n"
            f"spec = importlib.util.spec_from_file_location('cu', {str(SCRIPTS / 'capture-ui.py')!r})\n"
            "cu = importlib.util.module_from_spec(spec); spec.loader.exec_module(cu)\n"
            "state = {'doc_closed': False, 'quit': False}\n"
            "def require_com(owner_tid):\n"
            "    at, aq = ctypes.c_int(-1), ctypes.c_int(-1)\n"
            "    if ctypes.windll.ole32.CoGetApartmentType(ctypes.byref(at), ctypes.byref(aq)) != 0:\n"
            "        raise RuntimeError('COM not initialized on thread')\n"
            "    if threading.get_ident() != owner_tid:\n"
            "        raise RuntimeError('proxy called on wrong apartment thread')\n"
            "class Doc:\n"
            "    Name = 'Doc1'; FullName = 'Doc1'\n"
            "    def __init__(self, tid): self._owner_tid = tid\n"
            "    def Close(self, SaveChanges=0):\n"
            "        require_com(self._owner_tid)\n"
            "        state['doc_closed'] = True; Docs.Count = 0\n"
            "class Docs:\n"
            "    Count = 0\n"
            "    def __init__(self, tid): self._owner_tid = tid\n"
            "    def Add(self):\n"
            "        require_com(self._owner_tid)\n"
            "        time.sleep(0.9); Docs.Count = 1; return Doc(self._owner_tid)\n"
            "    def __iter__(self): return iter([])\n"
            "class App:\n"
            "    Visible = False\n"
            "    def __init__(self):\n"
            "        self._owner_tid = threading.get_ident()\n"
            "        require_com(self._owner_tid)\n"
            "        self.Documents = Docs(self._owner_tid)\n"
            "    def Quit(self, SaveChanges=0):\n"
            "        require_com(self._owner_tid)\n"
            "        state['quit'] = True\n"
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
        # 2) When an owned instance's post-Add window lookup blocks beyond the atexit shutdown budget (waits on an
        #    unset Event forever), ownership (hwnd, proc, and marshaled created document) is bound before the hang,
        #    and _abandon_hung_launch marshals the COM proxies onto a COM-initialized emergency apartment, closes
        #    only the owned document, calls App.Quit(), verifies proc.exited(), and closes proc before exit.
        probe_hung_add = (
            "import atexit, ctypes, importlib.util, json, sys, threading\n"
            f"spec = importlib.util.spec_from_file_location('cu', {str(SCRIPTS / 'capture-ui.py')!r})\n"
            "cu = importlib.util.module_from_spec(spec); spec.loader.exec_module(cu)\n"
            "cu.Win = lambda: type('W', (), {'top': lambda self, h: h})()\n"
            "never = threading.Event()\n"
            "state = {\n"
            "    'bound_before_add': False, 'marshaled_on_sta': False, 'unmarshaled_on_new_sta': False,\n"
            "    'doc_closed': False, 'quit': False, 'exited_checked': False, 'proc_closed': False,\n"
            "}\n"
            "def require_com(owner_tid):\n"
            "    at, aq = ctypes.c_int(-1), ctypes.c_int(-1)\n"
            "    if ctypes.windll.ole32.CoGetApartmentType(ctypes.byref(at), ctypes.byref(aq)) != 0:\n"
            "        raise RuntimeError('COM not initialized on thread')\n"
            "    if threading.get_ident() != owner_tid:\n"
            "        raise RuntimeError('proxy called on wrong apartment thread')\n"
            "class Proc:\n"
            "    pid = 77\n"
            "    def exited(self, s):\n"
            "        state['exited_checked'] = bool(state['doc_closed'] and state['quit'])\n"
            "        return state['exited_checked']\n"
            "    def close(self): state['proc_closed'] = bool(state['exited_checked'])\n"
            "shared_docs = []\n"
            "class Doc:\n"
            "    Name = 'Doc1'; FullName = 'Doc1'; Saved = -1; closed = False\n"
            "    def __init__(self, tid, tok='doc-1'): self._owner_tid = tid; self._doc_token = tok\n"
            "    def __com_marshal__(self):\n"
            "        require_com(self._owner_tid)\n"
            "        tok = self._doc_token\n"
            "        return lambda: Doc(threading.get_ident(), tok)\n"
            "    def Close(self, SaveChanges=0):\n"
            "        require_com(self._owner_tid)\n"
            "        self.closed = True; state['doc_closed'] = True; shared_docs.clear()\n"
            "class Docs:\n"
            "    def __init__(self, tid): self._owner_tid = tid\n"
            "    @property\n"
            "    def Count(self):\n"
            "        require_com(self._owner_tid)\n"
            "        return len(shared_docs)\n"
            "    def Add(self):\n"
            "        require_com(self._owner_tid)\n"
            "        shared_docs.append(Doc(self._owner_tid))\n"
            "        return shared_docs[-1]\n"
            "    def Item(self, i):\n"
            "        require_com(self._owner_tid)\n"
            "        return Doc(self._owner_tid, shared_docs[0]._doc_token)\n"
            "    def __iter__(self):\n"
            "        require_com(self._owner_tid)\n"
            "        return iter([Doc(self._owner_tid, d._doc_token) for d in list(shared_docs)])\n"
            "class AW:\n"
            "    @property\n"
            "    def Hwnd(self):\n"
            "        if shared_docs:\n"
            "            never.wait()\n"
            "        return 42\n"
            "class App:\n"
            "    Visible = False\n"
            "    ActiveWindow = AW()\n"
            "    def __init__(self, tid=None):\n"
            "        self._owner_tid = tid or threading.get_ident()\n"
            "        require_com(self._owner_tid)\n"
            "        self.Documents = Docs(self._owner_tid)\n"
            "    def __com_marshal__(self):\n"
            "        require_com(self._owner_tid)\n"
            "        origin_tid = self._owner_tid\n"
            "        state['marshaled_on_sta'] = True\n"
            "        def unmarshal():\n"
            "            new_tid = threading.get_ident()\n"
            "            require_com(new_tid)\n"
            "            if new_tid == origin_tid:\n"
            "                raise RuntimeError('unmarshaled on blocked origin STA')\n"
            "            state['unmarshaled_on_new_sta'] = True\n"
            "            return App(tid=new_tid)\n"
            "        return unmarshal\n"
            "    def Quit(self, SaveChanges=0):\n"
            "        require_com(self._owner_tid)\n"
            "        state['quit'] = True\n"
            "def make_owner(hwnd, exe):\n"
            "    if not shared_docs:\n"
            "        state['bound_before_add'] = True\n"
            "    return Proc()\n"
            "atexit.register(lambda: print('ATEXIT:' + json.dumps(state), flush=True))\n"
            "rc = cu.main(['--app', 'word', '--tab', 'Home', '--merge', '--out', 'nonexistent_out.json'],\n"
            "             launcher=lambda app: cu.Launched(app, dispatch=lambda p: App(), owner=make_owner, init_timeout=0.05))\n"
            "print('AT_MAIN_RETURN:' + json.dumps(state), flush=True)\n"
            "print('MAIN_RETURNED:' + str(rc), flush=True)\n"
            "sys.exit(rc)\n"
        )
        proc_hung_add = subprocess.run([sys.executable, "-c", probe_hung_add], capture_output=True, text=True, timeout=4.5)
        self.assertEqual(proc_hung_add.returncode, 2, proc_hung_add.stderr)
        self.assertIn("MAIN_RETURNED:2", proc_hung_add.stdout)
        self.assertIn(
            'AT_MAIN_RETURN:{"bound_before_add": true, "marshaled_on_sta": true, "unmarshaled_on_new_sta": false, '
            '"doc_closed": false, "quit": false, "exited_checked": false, "proc_closed": false}',
            proc_hung_add.stdout,
        )
        self.assertIn(
            'ATEXIT:{"bound_before_add": true, "marshaled_on_sta": true, "unmarshaled_on_new_sta": true, '
            '"doc_closed": true, "quit": true, "exited_checked": true, "proc_closed": true}',
            proc_hung_add.stdout,
        )
        # 2b) Both normal and emergency cleanup honor PowerPoint's MsoTriState (msoTrue = -1, msoFalse = 0),
        #     refuse to close dirty owned documents (Saved = 0), refuse to close any document when created=[]
        #     (even if a sole blank presentation is open while Add() is pending), preserve unowned documents,
        #     and refuse to quit when foreign/dirty documents remain or document enumeration fails.
        class Pres:
            def __init__(self, name, saved=-1, path=""):
                self.Name, self.FullName = name, name
                self.Path = path
                self.Saved = saved
                self.closed = False

            def Close(self):
                self.closed = True

        own_pres = Pres("Presentation1", saved=-1)  # msoTrue = -1
        foreign_pres = Pres("Presentation2", saved=0)  # msoFalse = 0

        class PresCol:
            def __init__(self, items):
                self.items = items

            @property
            def Count(self):
                return sum(1 for p in self.items if not p.closed)

            def Item(self, i):
                open_items = [p for p in self.items if not p.closed]
                return open_items[i - 1]

        class PptApp:
            def __init__(self, col):
                self.Presentations = col
                self.quit = False

            def Quit(self):
                self.quit = True

        ppt_app = PptApp(PresCol([own_pres, foreign_pres]))
        ppt_launched = cu.Launched.__new__(cu.Launched)
        ppt_launched.key, ppt_launched.exe, ppt_launched.owned = "powerpoint", "POWERPNT.EXE", True
        ppt_launched.app = ppt_app
        ppt_launched.created = [own_pres]
        ppt_launched._created_meta = [cu.Launched._doc_meta(own_pres)]
        ppt_launched.proc = None
        ppt_launched.cleanup_errors = []
        ppt_launched._marshal_app(ppt_app)
        errs = ppt_launched._emergency_close_com()
        self.assertTrue(own_pres.closed)
        self.assertFalse(foreign_pres.closed)
        self.assertEqual(foreign_pres.Saved, 0)
        self.assertFalse(ppt_app.quit)
        self.assertTrue(any("did not create, so it was left running" in e for e in errs), errs)

        # Dirty owned presentation (Saved = 0, msoFalse) is preserved by BOTH emergency and normal cleanup.
        dirty_own = Pres("Presentation1", saved=0)
        dirty_app = PptApp(PresCol([dirty_own]))
        dirty_launched = cu.Launched.__new__(cu.Launched)
        dirty_launched.key, dirty_launched.exe, dirty_launched.owned = "powerpoint", "POWERPNT.EXE", True
        dirty_launched.app = dirty_app
        dirty_launched.created = [dirty_own]
        dirty_launched._created_meta = [cu.Launched._doc_meta(dirty_own)]
        dirty_launched.proc = None
        dirty_launched.cleanup_errors = []
        dirty_launched._marshal_app(dirty_app)
        dirty_errs = dirty_launched._emergency_close_com()
        self.assertFalse(dirty_own.closed)
        self.assertEqual(dirty_own.Saved, 0)
        self.assertFalse(dirty_app.quit)
        self.assertTrue(any("unsaved changes" in e for e in dirty_errs), dirty_errs)
        with self.assertRaises(cu.Refused):
            dirty_launched._close_impl()
        self.assertFalse(dirty_own.closed)
        self.assertEqual(dirty_own.Saved, 0)
        self.assertFalse(dirty_app.quit)

        # Sole open presentation while Add() is pending (created=[]) is never treated as owned (tested for both
        # Saved = 0 and Saved = -1).
        for initial_saved in (0, -1):
            sole_pres = Pres("Presentation1", saved=initial_saved)
            sole_app = PptApp(PresCol([sole_pres]))
            sole_launched = cu.Launched.__new__(cu.Launched)
            sole_launched.key, sole_launched.exe, sole_launched.owned = "powerpoint", "POWERPNT.EXE", True
            sole_launched.app = sole_app
            sole_launched.created = []
            sole_launched._created_meta = []
            sole_launched.proc = None
            sole_launched.cleanup_errors = []
            sole_launched._marshal_app(sole_app)
            sole_errs = sole_launched._emergency_close_com()
            self.assertFalse(sole_pres.closed)
            self.assertEqual(sole_pres.Saved, initial_saved)
            self.assertFalse(sole_app.quit)
            self.assertTrue(any("did not create, so it was left running" in e for e in sole_errs), sole_errs)

        # When document enumeration fails in emergency cleanup, Quit is never called.
        class BrokenCol:
            @property
            def Count(self):
                raise RuntimeError("RPC enumeration failed")

        broken_app = PptApp(BrokenCol())
        broken_launched = cu.Launched.__new__(cu.Launched)
        broken_launched.key, broken_launched.exe, broken_launched.owned = "powerpoint", "POWERPNT.EXE", True
        broken_launched.app = broken_app
        broken_launched.created = [Pres("Presentation1")]
        broken_launched._created_meta = [cu.Launched._doc_meta(broken_launched.created[0])]
        broken_launched._marshal_app(broken_app)
        enum_errs = broken_launched._emergency_close_com()
        self.assertFalse(broken_app.quit)
        self.assertTrue(any("enumerate documents failed" in e for e in enum_errs), enum_errs)

        # 2c) When emergency cleanup closes the owned blank document, calls Quit, and the process still does not exit,
        #     _abandon_hung_launch reports the failure to stderr instead of swallowing it silently.
        probe_hung_fail = (
            "import ctypes, importlib.util, sys, threading\n"
            f"spec = importlib.util.spec_from_file_location('cu', {str(SCRIPTS / 'capture-ui.py')!r})\n"
            "cu = importlib.util.module_from_spec(spec); spec.loader.exec_module(cu)\n"
            "cu.Win = lambda: type('W', (), {'top': lambda self, h: h})()\n"
            "never = threading.Event()\n"
            "class Proc:\n"
            "    pid = 88\n"
            "    def exited(self, s): return False\n"
            "    def close(self): pass\n"
            "class Doc:\n"
            "    Name = 'Doc1'; FullName = 'Doc1'; Saved = -1; closed = False; _doc_token = 'doc-fail'\n"
            "    def Close(self, SaveChanges=0): self.closed = True; Docs.items.clear()\n"
            "class Docs:\n"
            "    items = []\n"
            "    @property\n"
            "    def Count(self): return len(self.items)\n"
            "    def Add(self):\n"
            "        self.items.append(Doc())\n"
            "        return self.items[-1]\n"
            "    def __iter__(self): return iter(list(self.items))\n"
            "class AW:\n"
            "    @property\n"
            "    def Hwnd(self):\n"
            "        if Docs.items:\n"
            "            never.wait()\n"
            "        return 42\n"
            "class App:\n"
            "    Visible = False; Documents = Docs()\n"
            "    ActiveWindow = AW()\n"
            "    def Quit(self, SaveChanges=0): pass\n"
            "rc = cu.main(['--app', 'word', '--tab', 'Home', '--merge', '--out', 'nonexistent_out.json'],\n"
            "             launcher=lambda app: cu.Launched(app, dispatch=lambda p: App(), owner=lambda h, e: Proc(), init_timeout=0.05))\n"
            "sys.exit(rc)\n"
        )
        proc_hung_fail = subprocess.run([sys.executable, "-c", probe_hung_fail], capture_output=True, text=True, timeout=4.5)
        self.assertEqual(proc_hung_fail.returncode, 2, proc_hung_fail.stderr)
        self.assertIn("emergency shutdown incomplete", proc_hung_fail.stderr)
        self.assertIn("the WINWORD.EXE instance this tool started did not exit", proc_hung_fail.stderr)
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
            # A licence notice that appears only after the initial scan (e.g. during tab selection) is also refused.
            delayed_root = self._window_tree()
            tabs_bar = next(c for c in delayed_root.kids if c.name == "Ribbon Tabs")
            home_tab = tabs_bar.kids[0]
            home_tab.select = lambda: delayed_root.kids.append(
                E("Pane", "Product Activation Failed - Reduced functionality")
            )
            delayed_uia = type("U", (), {"element": lambda self, h: delayed_root})()
            with self.assertRaises(cu.Refused) as err_delayed:
                cu.capture(args, launched, delayed_uia, win)
            self.assertIn("licence or activation notice", str(err_delayed.exception))
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

                # 8. Sequential --tab captures with --merge preserve unverified records from earlier tabs in the sidecar.
                seq_out = Path(tmp) / "seq_ribbon.json"
                home_tab, home_lower = home()
                home_tab.select = lambda: None
                home_lower.rect = (0, 80, 1920, 200)
                insert_tab = E("TabItem", "Insert", "TabInsert", key="Alt, N", rect=(80, 40, 140, 70))
                insert_tab.select = lambda: None
                insert_lower = E("Pane", "Lower Ribbon", rect=(0, 80, 1920, 200), kids=[
                    E("Group", "Insert", kids=[
                        E("Group", "Pages", kids=[
                            E("Button", "Blank Page", "BlankPageInsert", rect=(10, 90, 60, 156)),
                        ]),
                        E("Group", "New", kids=[
                            E("Button", "Addin Insert", "UnknownInsertBtn", rect=(70, 90, 120, 156)),
                        ]),
                    ]),
                ])
                active_tab = ["Home"]

                def select_home():
                    active_tab[0] = "Home"

                def select_insert():
                    active_tab[0] = "Insert"

                home_tab.select = select_home
                insert_tab.select = select_insert

                def multi_tab_root():
                    lower_el = home_lower if active_tab[0] == "Home" else insert_lower
                    return E("Window", "Document1 - Word", kids=[
                        E("Tab", "Ribbon Tabs", kids=[home_tab, insert_tab]),
                        lower_el,
                    ])

                seq_uia = type("U", (), {"element": lambda self, h: multi_tab_root()})()
                with contextlib.redirect_stdout(io.StringIO()):
                    rc_home = cu.main(["--app", "word", "--tab", "Home", "--out", str(seq_out)],
                                      launcher=lambda app: launched, uia_factory=lambda: seq_uia, win_factory=lambda: win)
                    rc_ins = cu.main(["--app", "word", "--tab", "Insert", "--merge", "--out", str(seq_out)],
                                     launcher=lambda app: launched, uia_factory=lambda: seq_uia, win_factory=lambda: win)
                self.assertEqual((rc_home, rc_ins), (0, 0))
                merged_main = {r["id"] for r in json.loads(seq_out.read_text(encoding="utf-8"))}
                merged_sidecar = {r["id"] for r in json.loads(
                    (Path(tmp) / "unverified" / "word-unverified.json").read_text(encoding="utf-8")
                )}
                self.assertIn("word.home", merged_main)
                self.assertIn("word.insert", merged_main)
                self.assertIn("word.insert.pages", merged_main)
                self.assertIn("word.home.adobe-acrobat", merged_sidecar)
                self.assertIn("word.insert.new", merged_sidecar)

                # 9. An unpopulated or unstable Ribbon Tabs container is refused rather than publishing [].
                empty_tabs_out = Path(tmp) / "empty_tabs.json"
                empty_tabs_root = E("Window", "Document1 - Word", kids=[
                    E("Tab", "Ribbon Tabs", kids=[]),
                    home_lower,
                ])
                empty_tabs_uia = type("U", (), {"element": lambda self, h: empty_tabs_root})()
                clock = [0.0]

                def fast_monotonic():
                    val = clock[0]
                    clock[0] += 2.0
                    return val

                real_mono = cu.time.monotonic
                cu.time.monotonic = fast_monotonic
                try:
                    err_empty = io.StringIO()
                    with contextlib.redirect_stderr(err_empty):
                        rc_empty = cu.main(["--app", "word", "--all-tabs", "--out", str(empty_tabs_out)],
                                           launcher=lambda app: launched, uia_factory=lambda: empty_tabs_uia,
                                           win_factory=lambda: win)
                    self.assertEqual(rc_empty, 1)
                    self.assertFalse(empty_tabs_out.exists())
                    self.assertIn("ribbon tabs did not populate or stabilise", err_empty.getvalue())
                finally:
                    cu.time.monotonic = real_mono

                # 10. Clearing the live Lower Ribbon after lower_for_tab (during the second check_alone) does not
                # discard the validated snapshot.
                snap_out = Path(tmp) / "snap_home.json"
                snap_root = self._window_tree()
                snap_lower = next(c for c in snap_root.kids if c.name == "Lower Ribbon")
                check_calls = [0]

                def check_alone_clears_lower(_self=None):
                    check_calls[0] += 1
                    if check_calls[0] >= 2:
                        snap_lower.kids = []

                snap_launched = type("L", (), {"hwnd": 5, "proc": type("P", (), {"pid": 7})(),
                                               "app": type("A", (), {"Build": "16.0.20527", "Version": "16.0"})(),
                                               "language": lambda self: 1033, "check_alone": check_alone_clears_lower,
                                               "close": lambda self: None})()
                snap_uia = type("U", (), {"element": lambda self, h: snap_root})()
                with contextlib.redirect_stdout(io.StringIO()):
                    rc_snap = cu.main(["--app", "word", "--tab", "Home", "--out", str(snap_out)],
                                      launcher=lambda app: snap_launched, uia_factory=lambda: snap_uia,
                                      win_factory=lambda: win)
                self.assertEqual(rc_snap, 0)
                self.assertEqual(len(json.loads(snap_out.read_text(encoding="utf-8"))), 11)

                # 11. Capturing an entirely unverified tab succeeds and publishes its records to the unverified sidecar.
                unv_only_out = Path(tmp) / "acrobat_only.json"
                unv_sidecar_dir = Path(tmp) / "unverified_only"
                cu.UNVERIFIED = unv_sidecar_dir
                acrobat_tab = E("TabItem", "Acrobat", "ThirdPartyTab", key="Alt, B", rect=(80, 40, 140, 70))
                acrobat_tab.select = lambda: None
                acrobat_lower = E("Pane", "Lower Ribbon", rect=(0, 80, 1920, 200), kids=[
                    E("Group", "Acrobat", kids=[
                        E("Group", "Create", kids=[
                            E("Button", "Create PDF", "AcrobatCreate", rect=(10, 90, 60, 156)),
                        ]),
                    ]),
                ])
                acrobat_root = E("Window", "Document1 - Word", kids=[
                    E("Tab", "Ribbon Tabs", kids=[acrobat_tab]),
                    acrobat_lower,
                ])
                acrobat_uia = type("U", (), {"element": lambda self, h: acrobat_root})()
                with contextlib.redirect_stdout(io.StringIO()):
                    rc_acrobat = cu.main(["--app", "word", "--tab", "Acrobat", "--out", str(unv_only_out)],
                                         launcher=lambda app: launched, uia_factory=lambda: acrobat_uia,
                                         win_factory=lambda: win)
                self.assertEqual(rc_acrobat, 0)
                self.assertEqual(json.loads(unv_only_out.read_text(encoding="utf-8")), [])
                sidecar_recs = json.loads((unv_sidecar_dir / "word-unverified.json").read_text(encoding="utf-8"))
                self.assertEqual([r["kind"] for r in sidecar_recs], ["tab", "group", "control"])

                # 12. Separate fresh --out captures without --merge preserve earlier unverified records in the shared
                # sidecar and refuse concurrent modification of the sidecar.
                sep_sidecar_dir = Path(tmp) / "unverified_sep"
                cu.UNVERIFIED = sep_sidecar_dir
                sep_home_out = Path(tmp) / "sep_home.json"
                sep_ins_out = Path(tmp) / "sep_insert.json"
                with contextlib.redirect_stdout(io.StringIO()):
                    rc_sh = cu.main(["--app", "word", "--tab", "Home", "--out", str(sep_home_out)],
                                    launcher=lambda app: launched, uia_factory=lambda: seq_uia, win_factory=lambda: win)
                    rc_si = cu.main(["--app", "word", "--tab", "Insert", "--out", str(sep_ins_out)],
                                    launcher=lambda app: launched, uia_factory=lambda: seq_uia, win_factory=lambda: win)
                self.assertEqual((rc_sh, rc_si), (0, 0))
                sep_sidecar_ids = {
                    r["id"] for r in json.loads((sep_sidecar_dir / "word-unverified.json").read_text(encoding="utf-8"))
                }
                self.assertIn("word.home.adobe-acrobat", sep_sidecar_ids)
                self.assertIn("word.insert.new", sep_sidecar_ids)
            finally:
                cu.installed_build, cu.time.sleep, cu.UNVERIFIED = real_ib, real_sleep, real_unv


class ShellChrome(unittest.TestCase):
    def test_bidi_and_control_chars_are_stripped_from_element_names(self):
        self.assertEqual(
            cu.strip_control_chars("\u202a1 day ago\u202c\u0001\u200b"),
            "1 day ago",
        )
        raw = type("R", (), {
            "CurrentName": "\u202aEditor (F7)\u202c",
            "CurrentAutomationId": "WritingAssistanceCheckDocument",
            "CurrentAccessKey": "",
            "CurrentClassName": "",
            "CurrentControlType": 50000,
            "CurrentBoundingRectangle": type("Rect", (), {"left": 0, "top": 0, "right": 10, "bottom": 10})(),
        })()
        uia = type("U", (), {"type_name": lambda self, tid: "Button"})()
        el = cu.Element(uia, raw)
        self.assertEqual(el.name, "Editor (F7)")

    def test_account_and_email_labels_are_sanitised(self):
        self.assertEqual(cu.sanitize_shell_label("Derick Payne", uia_id="MeControlWidget"), "Account")
        self.assertEqual(cu.sanitize_shell_label("user@example.org"), "Account")
        self.assertEqual(cu.sanitize_shell_label("\u202aSave\u202c", id_mso="FileSave"), "Save")

    def test_powerpoint_window_handle_falls_back_to_main_window_discovery(self):
        launched = cu.Launched.__new__(cu.Launched)
        launched.key = "powerpoint"
        launched.started = 42
        launched.app = type("A", (), {})()  # no integer HWND or ActiveWindow.HWND
        real_win, real_wait = cu.Win, cu.wait_for
        cu.Win = lambda: type("W", (), {
            "main_window": lambda self, pid, cls=None: 9001 if (pid, cls) == (42, "PPTFrameClass") else None
        })()
        cu.wait_for = lambda fn, seconds=0, step=0: fn()
        try:
            self.assertEqual(launched.window_handle(), 9001)
        finally:
            cu.Win, cu.wait_for = real_win, real_wait

    def test_effective_shell_resolves_per_app_and_prunes_excluded_subtrees(self):
        records = json.loads((cu.INVENTORY / "shell" / "chrome.json").read_text(encoding="utf-8"))
        self.assertTrue(cu.validate_shell_chrome(records))

        # 1. Word retains editingMode and its three child mode items, plus autosave.
        word_eff = cu.effective_shell(records, "word")
        word_ids = {r["id"] for r in word_eff}
        for needed in (
            "shell.tabrow.editingMode",
            "shell.tabrow.editingMode.editing",
            "shell.tabrow.editingMode.reviewing",
            "shell.tabrow.editingMode.viewing",
            "shell.titlebar.autosave",
            "shell.qat.autosave",
        ):
            self.assertIn(needed, word_ids)

        # 2. Excel replaces the tab row without editingMode, pruning all three mode items and the keytip with zero orphans.
        excel_eff = cu.effective_shell(records, "excel")
        excel_by_id = {r["id"]: r for r in excel_eff}
        for excluded in (
            "shell.tabrow.editingMode",
            "shell.tabrow.editingMode.editing",
            "shell.tabrow.editingMode.reviewing",
            "shell.tabrow.editingMode.viewing",
            "shell.keytips.editingMode",
            "shell.qat.redo",
        ):
            self.assertNotIn(excluded, excel_by_id)
        self.assertIn("excel.shell.qat.redo", excel_by_id)
        self.assertEqual(excel_by_id["excel.shell.qat.redo"]["controlType"], "splitButton")
        # Retained descendants under share remap their parent to excel.shell.tabrow.share.
        self.assertEqual(excel_by_id["shell.tabrow.share.share"]["parent"], "excel.shell.tabrow.share")
        for r in excel_eff:
            if r.get("parent"):
                self.assertIn(r["parent"], excel_by_id)

        # 3. PowerPoint includes SlideShowFromBeginning on QAT and Present in Teams on tab row, and has moved QAT customize children.
        ppt_eff = cu.effective_shell(records, "powerpoint")
        ppt_by_id = {r["id"]: r for r in ppt_eff}
        self.assertIn("powerpoint.shell.qat.fromBeginning", ppt_by_id)
        self.assertIn("powerpoint.shell.tabrow.presentInTeams", ppt_by_id)
        self.assertNotIn("shell.tabrow.editingMode", ppt_by_id)
        self.assertEqual(
            ppt_by_id["powerpoint.shell.qat.customize.automatically-save"]["parent"],
            "powerpoint.shell.qat.customize",
        )

        # 4. Visio and Project omit autosave; Visio prunes menu items under its direct Share... button;
        #    Project moves search from title bar to tab row with app-specific search children inside the anchor;
        #    both retain KeyTips layer.
        visio_eff = cu.effective_shell(records, "visio")
        visio_ids = {r["id"] for r in visio_eff}
        self.assertNotIn("shell.titlebar.autosave", visio_ids)
        self.assertNotIn("shell.qat.autosave", visio_ids)
        self.assertIn("visio.shell.tabrow.closeDocument", visio_ids)
        self.assertIn("visio.shell.qat.undo.dropdown", visio_ids)
        self.assertNotIn("shell.tabrow.share.share", visio_ids)
        self.assertNotIn("shell.tabrow.share.copy-link", visio_ids)
        self.assertNotIn("shell.tabrow.share.manage-access", visio_ids)
        self.assertIn("shell.keytips.layer", visio_ids)
        self.assertIn("visio.shell.keytips.save", visio_ids)
        self.assertNotIn("shell.keytips.autosave", visio_ids)

        proj_by_id = {r["id"]: r for r in cu.effective_shell(records, "project")}
        self.assertNotIn("shell.titlebar.autosave", proj_by_id)
        self.assertNotIn("shell.qat.autosave", proj_by_id)
        self.assertNotIn("shell.titlebar.search", proj_by_id)
        self.assertIn("project.shell.tabrow.search", proj_by_id)
        self.assertIn("project.shell.search.input", proj_by_id)
        self.assertEqual(proj_by_id["project.shell.search.input"]["parent"], "project.shell.tabrow.search")
        anchor_b = proj_by_id["project.shell.tabrow.search"]["bounds"]
        input_b = proj_by_id["project.shell.search.input"]["bounds"]
        self.assertGreaterEqual(input_b["x"], anchor_b["x"])
        self.assertGreaterEqual(input_b["y"], anchor_b["y"])
        self.assertLessEqual(input_b["x"] + input_b["width"], anchor_b["x"] + anchor_b["width"])
        self.assertLessEqual(input_b["y"] + input_b["height"], anchor_b["y"] + anchor_b["height"])
        self.assertIn("shell.keytips.layer", proj_by_id)
        self.assertIn("project.shell.keytips.search", proj_by_id)
        self.assertNotIn("shell.keytips.autosave", proj_by_id)

        # 5. Outlook explorer and compose contexts resolve independently, exclude each other's context-only commands,
        #    and retain full title bar controls (systemMenu, qat, caption, search, account, minimize, maximize, close).
        ol_exp = {r["id"] for r in cu.effective_shell(records, "outlook", window="explorer")}
        ol_cmp = {r["id"] for r in cu.effective_shell(records, "outlook", window="compose")}
        self.assertIn("outlook.explorer.shell.qat.sendReceiveAll", ol_exp)
        self.assertIn("outlook.explorer.shell.qat.findContactCombo", ol_exp)
        self.assertNotIn("outlook.compose.shell.qat.save", ol_exp)
        self.assertIn("outlook.compose.shell.qat.save", ol_cmp)
        self.assertIn("outlook.compose.shell.qat.redo", ol_cmp)
        self.assertNotIn("outlook.explorer.shell.qat.sendReceiveAll", ol_cmp)
        self.assertNotIn("outlook.explorer.shell.qat.findContactCombo", ol_cmp)
        for tail in ("systemMenu", "qat", "caption", "search", "account", "minimize", "maximize", "close"):
            self.assertIn(f"outlook.explorer.shell.titlebar.{tail}", ol_exp)
            self.assertIn(f"outlook.compose.shell.titlebar.{tail}", ol_cmp)
        self.assertIn("shell.keytips.layer", ol_exp)
        self.assertIn("outlook.explorer.shell.keytips.sendReceiveAll", ol_exp)
        self.assertIn("shell.keytips.layer", ol_cmp)
        self.assertIn("outlook.compose.shell.keytips.save", ol_cmp)

    def test_validate_shell_chrome_refuses_missing_records_or_missing_bounds(self):
        # Unmeasured template records from build_shell_chrome_records are refused without live UIA measurements.
        with self.assertRaises(cu.Refused):
            cu.validate_shell_chrome(cu.build_shell_chrome_records(BUILD))

        base = json.loads((cu.INVENTORY / "shell" / "chrome.json").read_text(encoding="utf-8"))
        # Missing a required record is refused.
        without_search = [r for r in base if r["id"] != "shell.titlebar.search" and r.get("parent") != "shell.titlebar.search"]
        with self.assertRaises(cu.Refused):
            cu.validate_shell_chrome(without_search)

        # Missing bounds on a live-captured record is refused.
        no_bounds = [dict(r) for r in base]
        target = next(r for r in no_bounds if r["id"] == "shell.region.titlebar")
        target.pop("bounds", None)
        with self.assertRaises(cu.Refused):
            cu.validate_shell_chrome(no_bounds)

        # Zero width/height on a live-captured record is refused.
        zero_bounds = [dict(r) for r in base]
        target_z = next(r for r in zero_bounds if r["id"] == "project.shell.tabrow.search")
        target_z["bounds"] = {"x": 387, "y": 48, "width": 0, "height": 30}
        with self.assertRaises(cu.Refused):
            cu.validate_shell_chrome(zero_bounds)

        # Inline child falling outside its parent container bounds is refused.
        outside_parent = [dict(r) for r in base]
        target_p = next(r for r in outside_parent if r["id"] == "project.shell.search.input")
        target_p["bounds"] = {"x": 825, "y": 16, "width": 293, "height": 18}
        with self.assertRaises(cu.Refused):
            cu.validate_shell_chrome(outside_parent)

    def test_main_shell_writes_and_merges_valid_inventory(self):
        real_ib, real_rb, real_sleep = cu.installed_build, cu.reference_build, cu.time.sleep
        cu.installed_build = lambda: BUILD
        cu.reference_build = lambda app="Word": BUILD
        cu.time.sleep = lambda s: None
        committed = json.loads((cu.INVENTORY / "shell" / "chrome.json").read_text(encoding="utf-8"))
        expand_events = []

        def make_minimal_root():
            tab, lower = home()
            tab.select = lambda: None
            lower.rect = (0, 78, 1920, 178)
            tabs_bar = E("Tab", "Ribbon Tabs", rect=(58, 48, 1908, 78), kids=[tab])
            return E("Window", "Document1 - Word", kids=[tabs_bar, lower])

        def make_shell_root(overrides=None):
            overrides = overrides or {}
            tab, lower = home()
            tab.select = lambda: None
            lower.rect = (0, 78, 1920, 178)
            tabs_bar = E("Tab", "Ribbon Tabs", rect=(58, 48, 1908, 78), kids=[tab])
            top_kids = [tabs_bar, lower]
            deferred_groups = {}
            trigger_map = {
                "qat.customize.": "qat.customize",
                "tabrow.editingMode.": "tabrow.editingMode",
                "tabrow.share.": "tabrow.share",
                "ribbonDisplay.": "ribbonDisplay.button",
                "search.": "titlebar.search",
                "statusbar.customizeMenu": "statusbar.bar",
                "backstage.": "tabrow.file",
                "keytips.": "titlebar.systemMenu",
            }
            trigger_els = {}
            for rec in committed:
                if rec.get("app") == "outlook" or "bounds" not in rec:
                    continue
                rid = rec["id"]
                b = overrides.get(rid, rec["bounds"])
                rect = (b["x"], b["y"], b["x"] + b["width"], b["y"] + b["height"])
                ctype = "MenuItem" if rec.get("kind") == "menuItem" else "Button"
                el = E(ctype, rec["label"], rid, rect=rect)
                sid = "shell." + rid.split(".shell.", 1)[1] if ".shell." in rid else rid
                prefix = rid.split("shell.")[0] + "shell."
                deferred_to = None
                for child_seg, trig_seg in trigger_map.items():
                    if sid.startswith("shell." + child_seg) and sid != "shell." + trig_seg:
                        if trig_seg == "titlebar.search" and prefix == "project.shell.":
                            deferred_to = "project.shell.tabrow.search"
                        else:
                            deferred_to = prefix + trig_seg
                        break
                if deferred_to:
                    deferred_groups.setdefault(deferred_to, []).append(el)
                else:
                    top_kids.append(el)
                    trigger_els[rid] = el

            win_el = E("Window", "Document1 - Word", kids=top_kids)
            merged_deferred = {}
            for trig_id, popup_els in deferred_groups.items():
                fallback_id = "shell." + trig_id.split(".shell.", 1)[1] if ".shell." in trig_id else trig_id
                resolved_id = trig_id if trig_id in trigger_els else fallback_id
                if resolved_id in trigger_els:
                    merged_deferred.setdefault(resolved_id, []).extend(popup_els)
                else:
                    top_kids.extend(popup_els)
            for resolved_id, popup_els in merged_deferred.items():
                trig = trigger_els[resolved_id]
                trig.expand_state = lambda: 0

                def _make_expand_collapse(t_id, p_els):
                    def _exp():
                        expand_events.append(("expand", t_id))
                        for pe in p_els:
                            if pe not in win_el.kids:
                                win_el.kids.append(pe)

                    def _col():
                        expand_events.append(("collapse", t_id))
                        for pe in p_els:
                            if pe in win_el.kids:
                                win_el.kids.remove(pe)

                    return _exp, _col

                trig.expand, trig.collapse = _make_expand_collapse(resolved_id, popup_els)
            return win_el

        launched = type("L", (), {
            "hwnd": 5, "proc": type("P", (), {"pid": 7})(),
            "app": type("A", (), {"Build": "16.0.20527", "Version": "16.0"})(),
            "language": lambda self: 1033, "check_alone": lambda self: None, "close": lambda self: None,
        })()
        good_win = type("W", (), {
            "monitors": lambda self: [Profile.MONITOR], "place": lambda self, h, m: None,
            "state": lambda self, h: dict(Profile.GOOD, origin=(0, 0), monitor=1),
        })()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                out_path = Path(tmp) / "shell" / "chrome.json"
                # 1. Failing launcher, empty window, minimal window (only Ribbon Tabs and Lower Ribbon),
                #    or missing fhd-100 monitor must fail without publishing.
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(
                        cu.main(["--shell", "--out", str(out_path)],
                                launcher=lambda a: (_ for _ in ()).throw(OSError("no COM"))),
                        2,
                    )
                    self.assertFalse(out_path.exists())
                    self.assertEqual(
                        cu.main(["--shell", "--out", str(out_path)],
                                launcher=lambda a: launched,
                                uia_factory=lambda: type("U", (), {"element": lambda self, h: E("Window", "Empty")})(),
                                win_factory=lambda: good_win),
                        1,
                    )
                    self.assertFalse(out_path.exists())
                    self.assertEqual(
                        cu.main(["--shell", "--app", "word", "--out", str(out_path)],
                                launcher=lambda a: launched,
                                uia_factory=lambda: type("U", (), {"element": lambda self, h: make_minimal_root()})(),
                                win_factory=lambda: good_win),
                        1,
                    )
                    self.assertFalse(out_path.exists())
                    no_mon_win = type("W", (), {
                        "monitors": lambda self: [], "place": lambda self, h, m: None,
                        "state": lambda self, h: dict(Profile.GOOD, origin=(0, 0), monitor=1),
                    })()
                    self.assertEqual(
                        cu.main(["--shell", "--out", str(out_path)],
                                launcher=lambda a: launched,
                                uia_factory=lambda: type("U", (), {"element": lambda self, h: make_shell_root()})(),
                                win_factory=lambda: no_mon_win),
                        1,
                    )
                    self.assertFalse(out_path.exists())

                # 2. Initial live --shell capture opens menus/Backstage/KeyTips and writes valid inventory.
                expand_events.clear()
                root_instance = [None]

                def get_root():
                    if root_instance[0] is None:
                        root_instance[0] = make_shell_root()
                    return root_instance[0]

                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = cu.main(
                        ["--shell", "--out", str(out_path)],
                        launcher=lambda a: (root_instance.__setitem__(0, None) or launched),
                        uia_factory=lambda: type("U", (), {"element": lambda self, h: get_root()})(),
                        win_factory=lambda: good_win,
                    )
                self.assertEqual(rc, 0)
                self.assertIn(("expand", "shell.qat.customize"), expand_events)
                self.assertIn(("collapse", "shell.qat.customize"), expand_events)
                self.assertIn(("expand", "shell.tabrow.file"), expand_events)
                self.assertIn(("expand", "shell.titlebar.systemMenu"), expand_events)
                data = json.loads(out_path.read_text(encoding="utf-8"))
                self.assertGreaterEqual(len(data), 110)
                self.assertEqual(ci.check([str(out_path)], require_behaviour=True, inventory=Path(tmp)), [])

                # 3. Single-app --shell --app word --merge refuses an incomplete window without publishing,
                #    and on a complete Word window refreshes Word bounds while preserving Excel bounds and custom behaviour.
                for rec in data:
                    if rec["id"] == "shell.titlebar.search":
                        rec["behaviour"] = "Custom hand-written search behaviour."
                        rec["bounds"] = {"x": 1, "y": 2, "width": 3, "height": 4}
                    elif rec["id"] == "excel.shell.qat.redo":
                        rec["bounds"] = {"x": 444, "y": 9, "width": 38, "height": 29}
                out_path.write_text(cu.render(data), encoding="utf-8")

                with contextlib.redirect_stderr(io.StringIO()):
                    rc_bad_merge = cu.main(
                        ["--shell", "--app", "word", "--merge", "--out", str(out_path)],
                        launcher=lambda a: launched,
                        uia_factory=lambda: type("U", (), {"element": lambda self, h: make_minimal_root()})(),
                        win_factory=lambda: good_win,
                    )
                self.assertEqual(rc_bad_merge, 1)

                root_instance[0] = None
                with contextlib.redirect_stdout(io.StringIO()):
                    rc_merge = cu.main(
                        ["--shell", "--app", "word", "--merge", "--out", str(out_path)],
                        launcher=lambda a: launched,
                        uia_factory=lambda: type(
                            "U",
                            (),
                            {
                                "element": lambda self, h: (
                                    root_instance[0]
                                    or root_instance.__setitem__(
                                        0,
                                        make_shell_root(
                                            overrides={
                                                "shell.titlebar.search": {
                                                    "x": 790, "y": 8, "width": 360, "height": 32
                                                }
                                            }
                                        ),
                                    )
                                    or root_instance[0]
                                )
                            },
                        )(),
                        win_factory=lambda: good_win,
                    )
                self.assertEqual(rc_merge, 0)
                merged = {r["id"]: r for r in json.loads(out_path.read_text(encoding="utf-8"))}
                self.assertEqual(merged["shell.titlebar.search"]["behaviour"], "Custom hand-written search behaviour.")
                self.assertEqual(
                    merged["shell.titlebar.search"]["bounds"],
                    {"x": 790, "y": 8, "width": 360, "height": 32},
                )
                self.assertEqual(merged["excel.shell.qat.redo"]["bounds"]["x"], 444)
        finally:
            cu.installed_build, cu.reference_build, cu.time.sleep = real_ib, real_rb, real_sleep


if __name__ == "__main__":
    unittest.main()
