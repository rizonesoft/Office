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

    def test_integral_float_is_an_integer(self):
        self.write("word/ribbon.json", [dict(TAB, order=1.0), dict(GROUP, order=1e0)])
        self.assertEqual(self.problems(), [])
        self.write("word/ribbon.json", [dict(TAB, order=1.5)])
        self.assertTrue(any("expected integer" in p for p in self.problems()))

    def test_minimum_and_wrong_types_fail(self):
        self.write("word/ribbon.json", [dict(TAB, order=-1), dict(GROUP, label=7),
                                        dict(BOLD, bounds={"x": 1, "y": 2, "width": -3, "height": 4})])
        problems = self.problems()
        self.assertTrue(any("order: below 0" in p for p in problems))
        self.assertTrue(any("label: expected string" in p for p in problems))
        self.assertTrue(any("width: below 0" in p for p in problems))

    def test_blank_and_missing_base_fields_fail(self):
        rec = {k: v for k, v in TAB.items() if k != "kind"}
        self.write("word/ribbon.json", [rec, dict(GROUP, label="   ")])
        problems = self.problems()
        self.assertTrue(any("missing kind" in p for p in problems))
        self.assertTrue(any("label" in p and "does not match" in p for p in problems))

    def test_control_without_control_type_fails(self):
        rec = {k: v for k, v in PASTE.items() if k != "controlType"}
        self.write("word/ribbon.json", [TAB, rec])
        self.assertTrue(any("missing controlType" in p for p in self.problems()))

    def test_shortcut_needs_chord_and_existing_target(self):
        sc = {"id": "word.shortcuts.bold", "app": "word", "kind": "shortcut", "label": "Bold", "target": "word.nope"}
        self.write("word/shortcuts.json", [sc])
        problems = self.problems()
        self.assertTrue(any("missing shortcut" in p for p in problems))
        self.assertTrue(any("target word.nope names no record" in p for p in problems))

    def test_bounds_member_missing_fails(self):
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, bounds={"x": 1, "y": 2, "width": 3})])
        self.assertTrue(any("missing height" in p for p in self.problems()))

    def test_source_must_carry_a_host_or_a_build(self):
        for bad in ("https://", "uia:", "baseline:", "listcommands:"):
            self.write("word/ribbon.json", [TAB, dict(PASTE, source=bad)])
            self.assertTrue(any("source" in p and "does not match" in p for p in self.problems()), bad)

    def test_require_behaviour_refuses_blank_sentence(self):
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, behaviour="Bold.", source="https://support.microsoft.com/x"),
                                        dict(PASTE, behaviour=" ", source="https://support.microsoft.com/y")])
        problems = self.problems(behaviour=True)
        self.assertTrue(any("behaviour" in p for p in problems))

    def test_unparseable_file_raises_unreadable(self):
        (self.inv / "word" / "broken.json").write_text("[{", encoding="utf-8")
        with self.assertRaises(ci.Unreadable):
            self.problems()

    def test_hostile_files_exit_2_with_a_diagnostic(self):
        for name, text in (("broken.json", "[{"), ("deep.json", "[" * 100000 + "]" * 100000),
                           ("huge-int.json", "[" + "9" * 5000 + "]")):
            path = self.inv / "word" / name
            path.write_text(text, encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                code = ci.main([str(path)])
            self.assertEqual(code, 2, name)
            self.assertIn("cannot read", err.getvalue(), name)
            path.unlink()


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
