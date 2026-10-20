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
        self.assertEqual(ctx.skipped, ["group 'Adobe Acrobat' on 'Home': no control the baseline knows, an add-in"])
        self.assertEqual({r["source"] for r in recs}, {f"uia:{BUILD}"})
        self.assertFalse(any("bounds" in r for r in recs))

    def test_bounds_and_size_only_under_the_profile(self):
        recs, _ = self.records(origin=(0, 0))
        by = {r["label"]: r for r in recs}
        self.assertEqual(by["Paste"]["bounds"], {"x": 20, "y": 82, "width": 42, "height": 76})
        self.assertEqual((by["Paste"]["size"], by["Bold"]["size"]), ("large", "small"))
        self.assertTrue(all(r.get("captureProfile") == "fhd-100" for r in recs if "bounds" in r))

    def test_an_add_in_tab_is_skipped(self):
        ctx = cu.Context("word", BUILD, IDS)
        self.assertEqual(cu.walk_tab(E("TabItem", "Acrobat"), 9, E("Pane"), ctx), [])
        self.assertIn("no identifier", ctx.skipped[0])

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
        for prop in ("CurrentHelpText", "CurrentFullDescription", "HelpTextProperty", "FullDescriptionProperty"):
            self.assertNotIn(prop, source)
        self.assertFalse([n for n in dir(cu.Element) if "help" in n.lower() or "description" in n.lower()])

    def test_keytips_and_ids(self):
        self.assertEqual([cu.keytip(k) for k in ("Alt, H, F P", "Alt, H", "Alt, H, C 1", "")], ["FP", "H", "C1", None])
        ids = cu.Ids()
        self.assertEqual([ids.make("word.home", x) for x in ("Font", "Font...", "Font 2")],
                         ["word.home.font", "word.home.font-2", "word.home.font-2-2"])


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


class Profile(unittest.TestCase):
    GOOD = {"window": (-1928, 1072, 8, 2120), "dpi": 96, "zoomed": True}
    MONITOR = {"rect": (-1920, 1080, 0, 2160), "dpi": 96}

    def test_all_values_hold(self):
        self.assertEqual(cu.profile_problems(self.GOOD, self.MONITOR, 1033, 120, [(255, 255, 255)] * 4), [])

    def test_each_value_is_checked(self):
        cases = [(dict(self.GOOD, dpi=144), self.MONITOR, 1033, 120, [(255, 255, 255)], "DPI"),
                 (dict(self.GOOD, zoomed=False), self.MONITOR, 1033, 120, [(255, 255, 255)], "maximised"),
                 (self.GOOD, None, 1033, 120, [(255, 255, 255)], "no display"),
                 (dict(self.GOOD, window=(0, 0, 3840, 2160)), self.MONITOR, 1033, 120, [(255, 255, 255)], "not on"),
                 (self.GOOD, self.MONITOR, 1036, 120, [(255, 255, 255)], "language"),
                 (self.GOOD, self.MONITOR, 1033, 20, [(255, 255, 255)], "ribbon"),
                 (self.GOOD, self.MONITOR, 1033, 120, [(43, 87, 154)], "theme"),
                 (self.GOOD, self.MONITOR, 1033, 120, [], "theme")]
        for state, monitor, lang, height, pixels, word in cases:
            problems = cu.profile_problems(state, monitor, lang, height, pixels)
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


class Launch(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()
