"""scripts/check-inventory.py: schema subset, conditional rules, ids, parents and the behaviour gate."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_inventory", SCRIPTS / "check-inventory.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

TAB = {"id": "word.home", "app": "word", "kind": "tab", "label": "Home", "order": 1}
GROUP = {"id": "word.home.font", "app": "word", "kind": "group", "label": "Font", "parent": "word.home", "order": 1}
BOLD = {"id": "word.home.font.bold", "app": "word", "kind": "control", "label": "Bold", "parent": "word.home.font",
        "order": 3, "controlType": "toggleButton", "size": "small", "keytip": "1", "shortcut": "Ctrl+B",
        "bounds": {"x": 168, "y": 112, "width": 24, "height": 22}, "captureProfile": "fhd-100",
        "screentip": {"title": "Bold (Ctrl+B)", "description": "Make your text bold."}, "idMso": "Bold",
        "source": "uia:16.0.20430.20182", "capturedFrom": "16.0.20430.20182"}
PASTE = {"id": "word.home.clipboard.paste", "app": "word", "kind": "control", "label": "Paste", "parent": "word.home",
         "order": 0, "controlType": "splitButton", "size": "large", "source": "uia:16.0.20430.20182"}


class Inventory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.inv = Path(self.tmp.name) / "inventory"
        (self.inv / "word").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, records):
        path = self.inv / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(records), encoding="utf-8")
        return path

    def problems(self, *paths, behaviour=False):
        return ci.check([str(p) for p in paths] or [str(self.inv)], behaviour, inventory=self.inv)

    def test_example_records_validate(self):
        self.write("word/ribbon.json", [TAB, GROUP, BOLD, PASTE])
        self.assertEqual(self.problems(), [])

    def test_unknown_control_type_fails(self):
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, controlType="knob")])
        self.assertTrue(any("controlType" in p for p in self.problems()))

    def test_bounds_without_capture_profile_fails(self):
        rec = {k: v for k, v in BOLD.items() if k != "captureProfile"}
        self.write("word/ribbon.json", [TAB, GROUP, rec])
        self.assertTrue(any("bounds requires captureProfile" in p for p in self.problems()))

    def test_control_without_source_fails(self):
        rec = {k: v for k, v in PASTE.items() if k != "source"}
        self.write("word/ribbon.json", [TAB, rec])
        self.assertTrue(any("missing source" in p for p in self.problems()))

    def test_unknown_field_and_bad_id_fail(self):
        self.write("word/ribbon.json", [dict(TAB, colour="blue"), dict(GROUP, id="Word Font")])
        problems = self.problems()
        self.assertTrue(any("unknown field colour" in p for p in problems))
        self.assertTrue(any("does not match" in p for p in problems))

    def test_id_must_start_with_its_app(self):
        self.write("word/ribbon.json", [dict(TAB, app="excel")])
        self.assertTrue(any("does not start with its app" in p for p in self.problems()))

    def test_duplicate_id_across_files_fails(self):
        self.write("word/ribbon.json", [TAB])
        self.write("word/ribbon-simplified.json", [TAB])
        self.assertTrue(any("duplicate id word.home" in p for p in self.problems()))

    def test_orphan_parent_fails(self):
        self.write("word/ribbon.json", [GROUP])
        self.assertTrue(any("orphan" in p for p in self.problems()))

    def test_single_file_resolves_parents_elsewhere(self):
        self.write("word/ribbon.json", [TAB, GROUP])
        menus = self.write("word/menus.json", [BOLD])
        self.assertEqual(self.problems(menus), [])

    def test_require_behaviour_needs_sentence_and_web_source(self):
        self.write("word/ribbon.json", [TAB, GROUP, BOLD])
        problems = self.problems(behaviour=True)
        self.assertTrue(any("has no behaviour" in p for p in problems))
        self.assertTrue(any("no web source" in p for p in problems))
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, behaviour="Makes the selected text bold.",
                                                          source="https://support.microsoft.com/x")])
        self.assertEqual(self.problems(behaviour=True), [])

    def test_unparseable_file_exits_2(self):
        (self.inv / "word" / "broken.json").write_text("[{", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(ci.Unreadable):
                self.problems()


class Cli(unittest.TestCase):
    def test_missing_path_exits_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(ci.main(["Z:/no/such/inventory.json"]), 2)

    def test_repository_inventory_is_clean(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = ci.main([])
        self.assertEqual(code, 0, out.getvalue())


if __name__ == "__main__":
    unittest.main()
