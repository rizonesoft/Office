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

BUILD = "16.0.20430.20182"
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
        ctx = cu.Context("word", BUILD, IDS)
        lower = E("Pane", kids=[E("Group", "Acrobat", kids=[E("Group", "Create", kids=[E("Button", "Bold", "Bold")])])])
        self.assertEqual(cu.walk_tab(E("TabItem", "Acrobat"), 9, lower, ctx), [])
        self.assertIn("no identifier", ctx.skipped[0])
        self.assertEqual([(r["kind"], r["baselineMissing"]) for r in ctx.unverified],
                         [("tab", True), ("group", True), ("control", True)])

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
               {"id": "word.home.gone", "label": "Gone", "behaviour": "Kept."}]
        new = [{"id": "word.home.font.bold", "label": "Bold", "order": 5, "source": f"uia:{BUILD}",
                "bounds": {"x": 9, "y": 9, "width": 9, "height": 9}, "captureProfile": "fhd-100"},
               {"id": "word.home.font.italic", "label": "Italic", "order": 6}]
        out = {r["id"]: r for r in cu.merge(old, new)}
        bold = out["word.home.font.bold"]
        self.assertEqual((bold["behaviour"], bold["source"], bold["order"], bold["bounds"]["x"]), ("Ours.", "uia:1.2.3.4", 5, 9))
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
        out = {r["id"]: r for r in cu.merge(old, new)}
        item = next(r for r in out.values() if r["label"] == "Item")
        self.assertEqual(item["parent"], "word.v.g.x-2")  # Second keeps its own id, and its new item hangs under it
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


class Round3(unittest.TestCase):
    def test_each_apps_build_is_read_in_its_own_form(self):
        word = type("W", (), {"Build": "16.0.20430", "Version": "16.0"})()
        excel = type("X", (), {"Build": 20430, "Version": "16.0"})()
        self.assertEqual((cu.reported_build(word), cu.reported_build(excel)), ("16.0.20430", "16.0.20430"))
        excel_com = type("X", (), {"Build": 20430.0, "Version": "16.0"})()  # what Excel really returns through COM
        self.assertEqual(cu.reported_build(excel_com), "16.0.20430")
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
        launched = type("L", (), {"proc": type("P", (), {"pid": 1})(), "hwnd": 5})()
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
        proxy = cu.Proxy({"hwnd": 1, "pid": 2, "build": "16.0.20430", "language": 1033}, lambda q: "now holds 2")
        with self.assertRaises(cu.Refused):
            proxy.check_alone()
        self.assertEqual((proxy.language(), cu.reported_build(proxy.app)), (1033, "16.0.20430"))

    def test_a_worker_that_ends_silently_is_a_refusal(self):
        self.assertIn("refused", cu.converse(iter([]), lambda r: None, None))

if __name__ == "__main__":
    unittest.main()
