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
        "idMso": "Bold",
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

    def test_require_behaviour_needs_only_a_sentence(self):
        self.write("word/ribbon.json", [TAB, GROUP, BOLD])
        self.assertTrue(any("has no behaviour" in p for p in self.problems(behaviour=True)))
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, behaviour="Turns heavy type on or off for the selection.")])
        self.assertEqual(self.problems(behaviour=True), [])

    def test_screentip_field_is_refused(self):
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, screentip={"title": "Bold"})])
        self.assertTrue(any("unknown field screentip" in p for p in self.problems()))

    def test_web_source_is_refused(self):
        self.write("word/ribbon.json", [TAB, dict(PASTE, source="https://example.com/paste")])
        problems = self.problems()
        self.assertTrue(any("source" in p and "does not match" in p for p in problems), problems)
        self.assertTrue(any("link" in p for p in problems), problems)

    def test_capture_provenance_sources_pass(self):
        for good in ("uia:16.0.20430.20182", "listcommands:16.0.20430.20182", "baseline:4f1c2ab"):
            self.write("word/ribbon.json", [TAB, dict(PASTE, source=good)])
            self.assertEqual(self.problems(), [], good)
        for bad in ("uia:latest", "baseline:main", "uia:16.0.20430.20182 extra"):
            self.write("word/ribbon.json", [TAB, dict(PASTE, source=bad)])
            self.assertTrue(any("does not match" in p for p in self.problems()), bad)

    def test_a_link_anywhere_in_a_record_is_refused(self):
        for rec in (dict(BOLD, behaviour="Makes text bold, see https://example.com/bold."),
                    dict(BOLD, label="Bold www.example.com"), dict(BOLD, menuPath="HTTP://example.com")):
            self.write("word/ribbon.json", [TAB, GROUP, rec])
            problems = self.problems()
            self.assertEqual(len([p for p in problems if ": link" in p]), 1, (rec, problems))

    def test_a_link_in_an_untyped_nested_value_is_reported(self):
        # The schema types no unknown field, so only the whole-record rule can name the link inside one.
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, extra={"items": ["see https://example.com"]})])
        problems = self.problems()
        self.assertTrue(any(".extra.items[0]: link" in p for p in problems), problems)

    def test_every_string_field_carries_the_link_rule(self):
        schema = ci.load(ci.SCHEMA)
        props = schema["$defs"]["record"]["properties"]
        strings = [k for k, v in props.items() if v.get("type") == "string"]
        self.assertIn("behaviour", strings)
        self.assertNotIn("screentip", props)
        missing = [k for k in strings if {"$ref": "#/$defs/noLink"} not in props[k].get("allOf", [])]
        self.assertEqual(missing, [])

    def test_a_control_character_in_any_string_is_refused(self):
        schema = ci.load(ci.SCHEMA)
        problems = ci.validate([dict(BOLD, label="Number Format: " + chr(1) + ".a.")], schema, schema)
        self.assertTrue(any(".label: control character" in p for p in problems), problems)
        self.assertEqual(ci.validate([dict(BOLD, label=chr(0xB6) + " Normal")], schema, schema), [])

    def test_the_schema_alone_refuses_a_link(self):
        schema = ci.load(ci.SCHEMA)
        for field, value in (("behaviour", "See HTTPS://example.com/help"), ("label", "www.example.com"),
                             ("menuPath", "File > http://x.example")):
            problems = ci.validate([dict(BOLD, **{field: value})], schema, schema)
            self.assertTrue(any(f".{field}: link" in p for p in problems), (field, problems))
        self.assertEqual(ci.validate([dict(BOLD, behaviour="Turns heavy type on or off.")], schema, schema), [])

    def test_a_trailing_newline_does_not_satisfy_an_anchored_pattern(self):
        for rec in (dict(PASTE, source="uia:16.0.20430.20182" + chr(10)), dict(PASTE, source="baseline:4f1c2ab" + chr(10)),
                    dict(PASTE, id="word.home.paste" + chr(10))):
            self.write("word/ribbon.json", [TAB, rec])
            self.assertTrue(any("does not match" in p for p in self.problems()), rec)
        self.assertIsNotNone(ci.ecma("^a[$]$").search("a$"))
        self.assertIsNone(ci.ecma("^a$").search("a" + chr(10)))

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

    def test_source_must_carry_a_build_or_commit(self):
        for bad in ("https://", "uia:", "baseline:", "listcommands:"):
            self.write("word/ribbon.json", [TAB, dict(PASTE, source=bad)])
            self.assertTrue(any("source" in p and "does not match" in p for p in self.problems()), bad)

    def test_numbers_are_checked_exactly(self):
        (self.inv / "word" / "ribbon.json").write_text(
            '[{"id": "word.home", "app": "word", "kind": "tab", "label": "Home", "order": 1.0000000000000001},'
            ' {"id": "word.view", "app": "word", "kind": "tab", "label": "View", "order": -1e-400}]', encoding="utf-8")
        problems = self.problems()
        self.assertTrue(any("[0].order: expected integer" in p for p in problems), problems)
        self.assertTrue(any("[1].order: expected integer" in p for p in problems), problems)

    def test_shortcut_target_must_be_a_command_or_control(self):
        sc = {"id": "word.shortcuts.bold", "app": "word", "kind": "shortcut", "label": "Bold", "shortcut": "Ctrl+B"}
        self.write("word/ribbon.json", [TAB, GROUP, BOLD])
        self.write("word/shortcuts.json", [dict(sc, target="word.home")])
        self.assertTrue(any("is a tab, not a command or control" in p for p in self.problems()))
        self.write("word/shortcuts.json", [dict(sc, target="word.home.font.bold")])
        self.assertEqual(self.problems(), [])

    def test_each_independent_constraint_refuses_alone(self):
        # Each fixture breaks exactly one constraint, and the expected diagnostic names that constraint.
        cases = {
            ".captureProfile: empty": dict(BOLD, captureProfile=""),
            ".keytip: empty": dict(BOLD, keytip=""),
            ".idMso: empty": dict(BOLD, idMso=""),
            ".capturedFrom: empty": dict(BOLD, capturedFrom=""),
            ".shortcut: empty": dict(BOLD, shortcut=""),
            ".size: 'huge' is not one of": dict(BOLD, size="huge"),
            ".bounds: unknown field z": dict(BOLD, bounds={"x": 1, "y": 2, "width": 3, "height": 4, "z": 5}),
            ".kind: 'widget' is not one of": dict(BOLD, kind="widget"),
            ".baselineMissing: expected boolean": dict(BOLD, baselineMissing="yes"),
            ".bounds: expected object": dict(BOLD, bounds=[1, 2, 3, 4]),
        }
        for expected, rec in cases.items():
            self.write("word/ribbon.json", [TAB, GROUP, rec])
            problems = self.problems()
            self.assertTrue(any(expected in p for p in problems), (expected, problems))
        # The app enum is tested on the property alone: a record with an unknown app also breaks the id pattern.
        schema = ci.load(ci.SCHEMA)
        app_problems = ci.validate("paint", schema["$defs"]["record"]["properties"]["app"], schema)
        self.assertTrue(any("'paint' is not one of" in p for p in app_problems), app_problems)

    def test_huge_exponent_exits_2(self):
        path = self.inv / "word" / "exponent.json"
        path.write_text('[{"id": "word.home", "app": "word", "kind": "tab", "label": "Home", '
                        '"order": 1e999999999999999999999999999999999999}]', encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ci.main([str(path)]), 2)
        self.assertIn("cannot read", err.getvalue())

    def test_reference_to_an_id_defined_twice_elsewhere_is_ambiguous(self):
        self.write("word/a.json", [TAB])
        self.write("word/b.json", [TAB])
        other = self.write("word/c.json", [GROUP])
        self.assertTrue(any("parent word.home is ambiguous" in p for p in self.problems(other)))

    def test_require_behaviour_refuses_blank_sentence(self):
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, behaviour="Heavy type."), dict(PASTE, behaviour=" ")])
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
    def test_validation_failure_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "capture.json"
            path.write_text(json.dumps([dict(TAB, kind="widget")]), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = ci.main([str(path)])
        self.assertEqual(code, 1)
        self.assertIn("kind", out.getvalue())

    def test_missing_path_exits_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(ci.main(["Z:/no/such/inventory.json"]), 2)

    def test_repository_inventory_is_clean(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = ci.main([])
        self.assertEqual(code, 0, out.getvalue())


if __name__ == "__main__":
    unittest.main()
