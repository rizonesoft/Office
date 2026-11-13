# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
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
         "order": 0, "controlType": "splitButton", "size": "large", "source": "uia:16.0.20430.20182",
         "capturedFrom": "16.0.20430.20182"}  # a live capture records its build (design/inventory/REFERENCE.md)


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
        for good in ("uia:16.0.20430.20182", "listcommands:16.0.20430.20182", "baseline:b230a0d"):
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
        for rec in (dict(PASTE, source="uia:16.0.20430.20182" + chr(10)), dict(PASTE, source="baseline:b230a0d" + chr(10)),
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

    def test_a_record_cannot_contain_itself(self):
        # Audit D02 T01 section 23, finding 1: a parent chain that loops names no real containment.
        self.write("word/ribbon.json", [dict(TAB, parent="word.home")])
        self.assertTrue(any("parent chain loops: word.home -> word.home" in p for p in self.problems()))
        self.write("word/ribbon.json", [dict(TAB, parent="word.home.font"), GROUP])
        self.assertTrue(any("parent chain loops" in p for p in self.problems()))
        self.write("word/ribbon.json", [TAB, GROUP, BOLD])
        self.assertEqual(self.problems(), [])

    def test_a_blank_shortcut_is_refused(self):
        # Audit finding 2: a chord of spaces records no key.
        sc = {"id": "word.shortcuts.bold", "app": "word", "kind": "shortcut", "label": "Bold"}
        for chord in (" ", "\u00a0\u2003"):
            self.write("word/shortcuts.json", [dict(sc, shortcut=chord)])
            self.assertTrue(any(".shortcut" in p for p in self.problems()), repr(chord))

    def test_web_addresses_without_http_are_refused(self):
        # Audit finding 3: the no-link rule covers any scheme, mailto:, a dotted host with a path, and common domains.
        for text in ("support.microsoft.com/en-us/office", "mailto:help@example.org", "ftp://files.example",
                     "see example.com", "Office.NET"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("link" in p for p in self.problems()), text)
        # Words that look like hosts but are ordinary labels and ids stay valid.
        self.write("word/ribbon.json", [dict(TAB, label="Info"), dict(GROUP, id="word.command.app-restore",
                                                                         parent="word.home", label="Restore")])
        self.assertEqual(self.problems(), [])

    def test_a_repeated_member_is_unreadable(self):
        # Audit finding 4: json keeps the last of two equal keys, so the first (here a link) would vanish unchecked.
        path = self.inv / "word" / "ribbon.json"
        path.write_text('[{"id": "word.home", "app": "word", "kind": "tab", "label": "https://example.com", '
                        '"label": "Home", "order": 1}]', encoding="utf-8")
        with self.assertRaises(ci.Unreadable) as raised:
            self.problems()
        self.assertIn("repeated member label", str(raised.exception))

    def test_a_malformed_outlook_window_cell_is_a_problem_not_a_crash(self):
        # Audit finding 5: a window cell that is not a string reached a set lookup and raised TypeError.
        real = ci.INVENTORY
        data = json.loads((real / "outlook" / "baseline.json").read_text(encoding="utf-8"))
        data["rows"][0][0] = {}
        sources = ci.load(real / ci.SOURCES)
        problems = ci.check_baseline(Path("outlook/baseline.json"), data, ci.load(ci.BASELINE_SCHEMA), sources)
        self.assertTrue(any("$.rows[0].window" in p and "not a window name" in p for p in problems))
        (self.inv / "outlook").mkdir()
        (self.inv / "outlook" / "baseline.json").write_text(json.dumps(data), encoding="utf-8")
        (self.inv / ci.SOURCES).write_text((real / ci.SOURCES).read_text(encoding="utf-8"), encoding="utf-8")
        whole = ci.check([str(self.inv)], inventory=self.inv)  # the whole-inventory window gate must not crash either
        self.assertTrue(any("not a window name" in p for p in whole))

    def test_capture_provenance_must_be_recorded_in_the_reference(self):
        # Audit finding 6: captureProfile and capturedFrom name what design/inventory/REFERENCE.md records.
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, captureProfile="does-not-exist")])
        self.assertTrue(any("captureProfile does-not-exist is not a profile" in p for p in self.problems()))
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, capturedFrom="not-a-build")])
        self.assertTrue(any("capturedFrom not-a-build is not a build" in p for p in self.problems()))
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, source="uia:16.0.1.2")])
        self.assertTrue(any("source build 16.0.1.2 is not capturedFrom" in p for p in self.problems()))

    def test_a_host_name_in_text_is_refused(self):
        # Audit round 2, finding 1: any dotted host in text a person reads, whatever its ending.
        for text in ("support.microsoft.co.uk", "Visit office.microsoft.ie today", "learn.microsoft.de"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name" in p for p in self.problems()), text)
        # Ordinary text with dots stays valid, and dotted ids are not host names.
        self.write("word/ribbon.json", [dict(TAB, label="Save As..."),
                                        dict(GROUP, behaviour="Version 16.0 only, for example.")])
        self.assertEqual(self.problems(), [])

    def test_a_host_name_ending_a_sentence_is_refused(self):
        # Audit round 3, finding 1: the full stop that ends a sentence does not hide the host before it.
        for text in ("Visit support.microsoft.co.uk.", "See office.microsoft.ie. Then return."):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name" in p for p in self.problems()), text)

    def test_ecma_whitespace_is_blank_text(self):
        # Audit round 3, finding 2: U+FEFF is whitespace to the schema (ECMA-262), so it is no label, chord or
        # behaviour, and the behaviour gate agrees with the schema.
        sc = {"id": "word.shortcuts.bold", "app": "word", "kind": "shortcut", "label": "Bold"}
        self.write("word/ribbon.json", [dict(TAB, label="\ufeff")])
        self.assertTrue(any(".label" in p for p in self.problems()))
        self.write("word/ribbon.json", [TAB])
        self.write("word/shortcuts.json", [dict(sc, shortcut="\ufeff")])
        self.assertTrue(any(".shortcut" in p for p in self.problems()))
        self.write("word/shortcuts.json", [dict(sc, shortcut="Ctrl+B")])
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, behaviour="\ufeff\u3000")])
        self.assertTrue(any("behaviour" in p for p in self.problems()))
        self.write("word/ribbon.json", [TAB, GROUP, BOLD])
        self.assertTrue(any("has no behaviour" in p for p in self.problems(behaviour=True)))
        # The behaviour gate strips the schema's whitespace: a sentence padded with U+3000 (a real space) still counts.
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, behaviour="\u3000Makes the text bold.")])
        self.assertEqual(self.problems(behaviour=True), [])

    def test_ecma_translates_whitespace_classes(self):
        self.assertFalse(ci.ecma(r"\S").search("\ufeff\u2028\u00a0"))
        self.assertTrue(ci.ecma(r"\S").search("\x1c"))  # a C0 separator is not whitespace to ECMA
        self.assertTrue(ci.ecma(r"^\s*\S").search("\ufeff x"))
        with self.assertRaises(ValueError):
            ci.ecma(r"[^\S]")

    def test_a_host_after_an_ellipsis_is_refused(self):
        # Audit round 4, finding 1: punctuation before a host does not hide it.
        for text in ("Visit ...support.microsoft.co.uk", "(learn.microsoft.de)", "-office.microsoft.ie"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name" in p for p in self.problems()), text)

    def test_deep_nesting_is_a_problem_not_a_crash(self):
        # Audit round 4, finding 2: the link scan walks any depth the loader accepts without recursing.
        nested = 0
        for _ in range(5000):
            nested = [nested]
        self.write("word/ribbon.json", [dict(TAB, extra=nested)])
        self.assertTrue(any("unknown field extra" in p for p in self.problems()))
        deep_link = "https://example.com"
        for _ in range(5000):
            deep_link = [deep_link]
        self.assertEqual(len(ci.links({"extra": deep_link}, "$[0]", ci.ecma(r"https?://"))), 1)

    def test_every_text_and_reference_field_refuses_an_empty_value(self):
        # Audit round 4, finding 3: each field below must refuse "" on its own, so removing any one field's rule fails
        # this test. The list is written out here, not read from the schema.
        fields = ("label", "parent", "keytip", "shortcut", "target", "menuPath", "captureProfile", "behaviour",
                  "idMso", "uiaId", "source", "capturedFrom", "id", "condition", "dispositionReason")
        for field in fields:
            rec = dict(BOLD, **{field: ""})
            self.write("word/ribbon.json", [TAB, GROUP, rec])
            # D02 T01 §27: the length rule's own word, so a pattern that also refuses "" cannot stand in for it; id
            # and source have no length rule, and their patterns refuse it.
            expected = "does not match" if field in ("id", "source") else "empty"
            self.assertTrue(any(f".{field}: " in p and expected in p for p in self.problems()), field)

    def test_any_address_in_text_is_refused(self):
        # Audit round 5, findings 1 and 3: punycode hosts and URI schemes other than scheme:// in text a person reads.
        # Each address fits the shortest text field (a keytip, 16 characters), so the address rule, not the length
        # rule, is what refuses it.
        for text in ("xn--e1a.xn--p1ai", "data:text/plain", "javascript:x()", "tel:+2711000000"):
            for field in ("label", "behaviour", "menuPath", "keytip", "shortcut"):
                rec = dict(BOLD, **{field: text})
                self.write("word/ribbon.json", [TAB, GROUP, rec])
                self.assertTrue(any(f".{field}" in p and "host name or address" in p for p in self.problems()),
                                (field, text))
        # A colon followed by a space, and digits around a dot, stay valid in text.
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, behaviour="Zoom: sets 1.5 line spacing.")])
        self.assertEqual(self.problems(), [])

    def test_a_hyphenated_dotted_call_must_complete_at_any_depth(self):
        # D02 T01 §27: noHost's pattern counts parentheses only to a fixed depth; from about 20 nested calls an
        # unclosed or prose-interrupted call passed it. The checker now counts them at any depth up to maxLength.
        refused = []
        for n in (20, 40, 120):
            refused += ["=1-REGISTER.ID(" + "SUM(" * n + "1" + ")" * n + " \"help desk\"",
                        "=1-REGISTER.ID(" + "SUM(" * n + "1" + ")" * (n - 1) + " help desk",
                        "=1-REGISTER.ID(" + "SUM(" * n + "\"help" + ")" * n + ")",
                        "=1-REGISTER.ID(" + "SUM(" * n + "\"help\" desk" + ")" * n + ")"]
        for text in refused:
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, behaviour=text)])
            self.assertTrue(any(".behaviour" in p and "host name or address" in p for p in self.problems()),
                            text[:40] + "..." + text[-20:])
        for n in (20, 40, 120):
            for text in ("=1-REGISTER.ID(" + "SUM(" * n + "1" + ")" * n + ")",
                         "=1-REGISTER.ID(" + "SUM(" * n + "\"a \"\"b\"\"\"" + ")" * n + ") is a lookup.",
                         "=1-STDEV.S(" + "SUM(" * n + "1, 2" + ")" * n + "+1)"):
                self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, behaviour=text)])
                self.assertEqual(self.problems(), [], text[:40] + "..." + text[-20:])

    def host_pattern(self):
        return ci.ecma(ci.load(ci.SCHEMA)["$defs"]["noHost"]["not"]["pattern"])

    def test_a_hyphenated_call_must_close_whatever_it_quotes(self):
        # D02 T01 §27: the scan counts parentheses outside "..." and '...' only (a doubled quote inside either is a
        # quote), and takes only a call glued to its hyphen. Round 1, finding 1: a parenthesis inside a quoted sheet
        # name was counted as call syntax, so a valid reference was refused.
        host = self.host_pattern()

        def f(text):
            return ci.unfinished_call(text, host)
        for whole in ("=1-STDEV.S(1,2) and prose after the call", '=1-REGISTER.ID(SUM("a""b"), 2)',
                      "=1-STDEV.S('Q1 (draft)'!A1)", "=1-STDEV.S('It''s (x)'!A1, \"a)\")", "=1-REGISTER.ID(SUM(1) )",
                      "No call here: STDEV.S without a hyphen before it.",
                      "=1 - REGISTER.ID(SUM(1", "=x -NORM.S.DIST(1"):  # a spaced hyphen is the pattern's to judge
            self.assertIsNone(f(whole), whole)
        for open_call, call in (('=1-REGISTER.ID(SUM("a""b) x', "1-REGISTER.ID("), ("=1-STDEV.S('Q1 (draft!A1)", "1-STDEV.S("),
                                ("=SUM(1)-NORM.S.DIST(1", ")-NORM.S.DIST("), ("=Table1[Amount]-NORM.S.DIST((1)", "]-NORM.S.DIST("),
                                ("=1-STDEV.S(1)+2-REGISTER.ID(3", "2-REGISTER.ID(")):
            self.assertEqual(f(open_call), f"the call {call} is not completed", open_call)
        schema = ci.load(ci.SCHEMA)
        record = {"id": "excel.probe", "app": "excel", "kind": "tab", "label": "Probe",
                  "behaviour": "=1-STDEV.S('Q1 (draft)'!A1)"}  # the record the round reproduced the refusal with
        self.assertEqual(ci.validate([record], schema, schema), [])

    def test_a_call_nested_deeper_than_the_pattern_counts_is_read_level_by_level(self):
        # D02 T01 §27: the depth the pattern counts is measured on the pattern, and from that depth each level of the
        # call is read by the pattern on its own, so a deep call is refused for exactly what refuses a shallow one.
        host, schema = self.host_pattern(), ci.load(ci.SCHEMA)
        counted = ci.counted_depth("REGISTER.ID(", host)
        self.assertLess(counted, ci.DEPTH_PROBED)
        unfinished = "=1-REGISTER.ID(" + "(" * (counted - 1) + "1" + ")" * (counted - 1)
        self.assertIsNotNone(host.search(unfinished))  # one level short of it, the pattern still refuses this itself
        self.assertIsNone(host.search("=1-REGISTER.ID(" + "(" * counted + "1" + ")" * counted))  # and from it, not

        def behaviour(text):
            return ci.validate([dict(BOLD, behaviour=text)], schema, schema)
        for n in (counted, counted + 1, 40):
            nested = "=1-REGISTER.ID(" + "SUM(" * n + "1" + ")" * n
            self.assertEqual(behaviour(nested + ")"), [], n)
            self.assertEqual(behaviour(nested + ",'Q1 (draft)'!A1)"), [], n)
            for glued, part in (("?)", "REGISTER.ID(SUM(1)?)"), ("'x')", "REGISTER.ID(SUM(1)'x')"),
                                (",SUM(2) [x])", "REGISTER.ID(SUM(1),SUM(1) [x])")):
                self.assertIsNone(host.search(nested + glued))  # the pattern alone lets it stand at this depth
                self.assertEqual(behaviour(nested + glued),
                                 ["$[0].behaviour: host name or address (the call 1-REGISTER.ID( nests deeper than "
                                  f"the address rule counts, and its part {part} is refused when read alone)"], (n, glued))
        # A long refused part is cut short in the diagnostic.
        long_part = "=1-REGISTER.ID(" + "SUM(" * 20 + "1" + ")" * 20 + "?" + "2" * 80 + ")"
        self.assertIsNone(host.search(long_part))
        self.assertEqual(behaviour(long_part), ["$[0].behaviour: host name or address (the call 1-REGISTER.ID( nests "
                                                "deeper than the address rule counts, and its part REGISTER.ID(SUM(1)?"
                                                + "2" * 50 + "...) is refused when read alone)"])
        # Inside an inner call the pattern lets the same text stand at any depth it counts, so it stands deep too.
        self.assertIsNone(host.search("=1-REGISTER.ID(SUM(IF(1)?2))"))
        self.assertEqual(behaviour("=1-REGISTER.ID(" + "SUM(" * 20 + "IF(1)?2" + ")" * 20 + ")"), [])

    def test_nesting_depth_never_changes_the_address_verdict(self):
        # D02 T01 §27: the scan exists only for the depth noHost's pattern cannot count, so over generated calls it
        # must (1) refuse nothing the pattern accepts at a depth the pattern counts, and (2) give a deep call the
        # verdict the pattern gives the same call nested one, two and three times. Without the scan, (2) fails for a
        # call glued to its hyphen. Three earlier scans failed here: one that also took a spaced hyphen failed (1)
        # 1,728 times, one that took only a name before the hyphen failed (2) after `)` and `]`, and one that judged
        # what may follow an inner call with rules of its own failed (1) for every parenthesis in a quoted sheet name
        # (round 1, finding 1), which is why each level is now read by the pattern itself.
        host = self.host_pattern()
        counted = ci.counted_depth("REGISTER.ID(", host)
        cores = ("1", '"help"', '"a ""b"""', '"help', "'Q1 (draft)'!A1", "'It''s (x)'!A1", "'Q1", "A1:B2",
                 "Table1[Amount (USD)]", "{1,2}", "#N/A", "NORM.S.DIST(1)", "x.y", "John's", "(1+2)*3", "")
        endings = (")", ") is a lookup.", "+1)", " desk)", "", ' "help desk"', ' "desk")', " .x)", " [x])", "desk)",
                   ",'Q1 (draft)'!A1)", " 'Q1'!A1)", '"x")', "'x')", ")-STDEV.S(1)", ") and 1-STDEV.S(", ")'",
                   "?)", "~1)", "}1)", ",SUM(1) [x])", ",(1)?)")
        after = "?[]`|~}{'\"$@_.x1 "  # one character after an inner call, with and without more after it

        def shapes(n, opening):
            out = []
            for core in cores:
                nested = opening * n + core + ")" * n
                out += [nested + end for end in endings]
                out += [nested[:-1] + " help desk", nested[:-n] + " desk" + ")" * n + ")"]
            plain = opening * n + "1" + ")" * n
            for x in after:
                out += [plain + x + ")", plain + x + "1)", plain + " " + x + "1)",
                        opening * n + '"s"' + x + ")" * n + ")"]
            return out

        heads = ("=1-REGISTER.ID(", "Type =SUM(1)-NORM.S.DIST(", "=Table1[Amount]-NORM.S.DIST(",
                 "=1 - REGISTER.ID(", '="a"-REGISTER.ID(')
        verdicts = set()
        for head in heads:
            for opening in ("SUM(", "SUM(1,"):
                by_depth = []
                for n in (1, 2, 3):
                    row = []
                    for shape in shapes(n, opening):
                        by_pattern = host.search(ci.utf16(head + shape)) is None
                        self.assertFalse(by_pattern and ci.unfinished_call(head + shape, host),
                                         f"the scan refuses what the pattern accepts: {head + shape}")
                        row.append(by_pattern)
                    by_depth.append(row)
                self.assertEqual(by_depth[0], by_depth[1], head)
                self.assertEqual(by_depth[0], by_depth[2], head)
                for n in (counted - 1, counted, counted + 1, 40):
                    for shallow, shape in zip(by_depth[0], shapes(n, opening)):
                        text = head + shape
                        deep = host.search(ci.utf16(text)) is None and ci.unfinished_call(text, host) is None
                        self.assertEqual(deep, shallow, f"nested {n} times: {text[:60]} ... {text[-40:]}")
                verdicts.update(by_depth[0])
        self.assertEqual(verdicts, {True, False})  # the texts hold both calls that stand and calls that are refused

    def test_nested_hyphenated_calls_cost_bounded_time(self):
        # Each call inside another shares its levels with it; they are read once, so sixty calls nested in each other
        # cost no more than their levels.
        import time
        schema = ci.load(ci.SCHEMA)
        ci.validate([dict(BOLD, behaviour="=1-REGISTER.ID(" + "(" * 20 + "1" + ")" * 21)], schema, schema)  # measures
        text = "=" + "1-REGISTER.ID(" * 60 + "1" + ")" * 60
        start = time.perf_counter()
        self.assertEqual(ci.validate([dict(BOLD, behaviour=text)], schema, schema), [])
        self.assertLess(time.perf_counter() - start, 3.0)

    def test_unicode_host_names_are_refused(self):
        # Audit round 6, finding 1: host names with the full-stop forms IDNA normalises, and in other scripts.
        for text in ("support。microsoft。com", "office．microsoft．com", "a｡example｡org",
                     "пример.рф", "data：text/plain,hello"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name or address" in p for p in self.problems()), ascii(text))

    def test_any_host_name_or_address_in_text_is_refused_by_its_dots(self):
        # Audit round 7, findings 1 and 3: hosts in any plane and numeric addresses are refused, and padding with a
        # Unicode space after a sentence is not mistaken for a host.
        for text in ("\U00010428.com", "8.8.8.8", "Visit 10.0.0.1 now", "*.example.com", ".example.com",
                     "*.example.dotm", "doc.docx.dotm", "1.25.dotm", "Normal..dotm", "contoso.xyz", "office.live",
                     "example.ht", "EXAMPLE.TEST", "MICROSOFT.ID", "WWW.MICROSOFT.COM", "ATTACKER.ID", "SERVER.ID",
                     "Visit ATTACKER.ID now", "XREGISTER.ID", "FOO-REGISTER.ID", "1-REGISTER.ID", "a-b.STDEV.S",
                     "Visit FOO-REGISTER.ID(help desk)", "Visit 1-REGISTER.ID(help desk)", "Visit 1-REGISTER.ID(1,2)",
                     "Visit (1-REGISTER.ID(1,2))", "Visit  (1-REGISTER.ID(1,2))", "Visit [1-REGISTER.ID(1,2)]",
                     "Visit \u201c(1-REGISTER.ID(1,2))\u201d", 'Visit "label=(1-REGISTER.ID(1,2))"',
                     '=SUM(1) Visit "(1-REGISTER.ID(1,2))"', '=1-STDEV.S(1,2) Visit "(1-REGISTER.ID(1,2))"',
                     '=1-STDEV.S(1,2) Visit "(1  -  REGISTER.ID(1,2))"',
                     "Visit ((1-REGISTER.ID(1,2)))", "=1-REGISTER.ID(SUM(1) \"help desk\")", "10%-REGISTER.ID(1,2)",
                     "=1-REGISTER.ID(SUM(RAND()) \"help desk\")", "=1-REGISTER.ID(SUM((1)) \"help desk\")",
                     "=1-REGISTER.ID(SUM(SUM((1))) \"help desk\")", "=1-REGISTER.ID(SUM(1)+1 \"help desk\")",
                     "=1-REGISTER.ID(SUM(1), 2 \"help desk\")", "Visit =1-REGISTER.ID(SUM(RAND()) \"help desk\")",
                     "Visit =1-REGISTER.ID(SUM((1)) \"help desk\")", "=1-REGISTER.ID(SUM(RAND()) \"help (desk)\")",
                     "=1-REGISTER.ID(SUM(1) (prose) \"help desk\")", "=1-REGISTER.ID(SUM(RAND()) + (1) \"help desk\")",
                     "=1-REGISTER.ID(SUM(RAND()) \"help desk\"+SUM(1))",
                     "=1-REGISTER.ID(SUM(RAND()) \"help desk\"+SUM(RAND()))",
                     "=1-REGISTER.ID(SUM(RAND()) \"help desk\"+SUM(SUM(RAND())))",
                     "Visit =1-REGISTER.ID(SUM(RAND()) \"help desk\"+SUM(RAND()))",
                     "=1-REGISTER.ID(SUM(RAND()) \"help desk\" = SUM(1))",
                     "=1-REGISTER.ID(SUM(RAND()) \"help desk\" = SUM(RAND()))",
                     "=1-REGISTER.ID(SUM(RAND()) \"help desk\" or =SUM(RAND()))",
                     "=1-REGISTER.ID(SUM(RAND()) \"help desk\" or =1)",
                     "=1-REGISTER.ID(SUM(RAND()) \"help desk\"+SUM(SUM(SUM(SUM(1)))))",
                     "=1-REGISTER.ID(SUM(RAND()) \"help desk\"+SUM(SUM(SUM(SUM(SUM(1))))))",
                     "=1-REGISTER.ID(SUM(RAND()) \"help desk\"+" + "SUM(" * 10 + "1" + ")" * 10 + ")",
                     "Visit =1-REGISTER.ID(SUM(RAND()) \"help desk\"+SUM(SUM(SUM(SUM(SUM(1))))))",
                     "=1-REGISTER.ID(SUM(RAND())", "=1-REGISTER.ID(SUM(RAND()) \"help desk\"",
                     "=1-REGISTER.ID(SUM(SUM(RAND()) \"help desk\"))", "=1-REGISTER.ID((SUM(RAND()) \"help desk\"))",
                     "=1-REGISTER.ID(SUM(SUM(SUM(SUM(SUM(SUM(1)))))) \"help desk\")",
                     "=1-REGISTER.ID(SUM(SUM(SUM(SUM(SUM(SUM(SUM(1))))))) \"help desk\")",
                     "=1-REGISTER.ID(SUM(SUM(SUM(SUM(SUM(SUM(SUM(1)))))))",
                     "=1-REGISTER.ID(" + "SUM(" * 12 + "1" + ")" * 12 + " \"help desk\")",
                     "=1-REGISTER.ID(" + "SUM(" * 12 + "1" + ")" * 12,
                     "=1-REGISTER.ID(" + "SUM(" * 20 + "1" + ")" * 20 + " \"help desk\")",
                     "=1-STDEV.S(A1:B3 B2:C4) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(1:3 2:4) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January North) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January North+1) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January North=1) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January North+SUM(1)) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January North+SUM(SUM(SUM(1)))) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January North+SUM(SUM({1,2}))) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January North+SUM(Table1[[#Data],[Amount]])) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January North+SUM(RANDARRAY(,2))) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January North+SUM(RAND())) Visit \"(1-REGISTER.ID(1,2))\"",
                     "See (=SUM(1) then X+SUM(SUM(SUM(FOO-REGISTER.ID(1,2)))))",
                     "See (=SUM(1) then X+SUM(SUM({1,2}), FOO-REGISTER.ID(1,2)))",
                     "See (=SUM(1) then X+SUM(Table1[[#Data],[Amount]], FOO-REGISTER.ID(1,2)))",
                     "See (=SUM(1) then X+SUM(RANDARRAY(,2), FOO-REGISTER.ID(1,2)))",
                     "See (=SUM(1) then X+SUM(RAND(), FOO-REGISTER.ID(1,2)))",
                     "See (=SUM(1) then X+SUM(1, FOO-REGISTER.ID(1,2)))",
                     "See (=SUM(1) then X+SUM(1), FOO-REGISTER.ID(1,2))",
                     "=1-STDEV.S(Revenue January North + SUM(1, FOO-REGISTER.ID(1,2)))",
                     "=1-STDEV.S(Revenue January=1) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January+SUM(1)) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(Revenue January=SUM(1)) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(A1:B3 (INDEX(A1:C3,1,0))) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=1-STDEV.S(R[-1]C R[-2]C) Visit \"(1-REGISTER.ID(1,2))\"",
                     "=SUM(1) and FOO-REGISTER.ID(1,2)", "=SUM(1) and 1-REGISTER.ID(1,2)",
                     "=SUM(1)  and FOO-REGISTER.ID(1,2)", "=SUM(1) AND FOO-REGISTER.ID(1,2)",
                     "=SUM(1) or FOO-REGISTER.ID(1,2)", "=SUM(1) OR FOO-REGISTER.ID(1,2)",
                     "=SUM(1) then FOO-REGISTER.ID(1,2)", "=SUM(1) FOO-REGISTER.ID(1,2)",
                     "See (=SUM(1) then FOO-REGISTER.ID(1,2))", "=SUM(1) then FOO-REGISTER.ID(1,2), or bar",
                     "=A1 and FOO-REGISTER.ID(1,2)", "=A1 then FOO-REGISTER.ID(1,2)",
                     "=Revenue and FOO-REGISTER.ID(1,2)", "=Revenue then FOO-REGISTER.ID(1,2)",
                     "=A1 FOO-REGISTER.ID(1,2)", "=Revenue FOO-REGISTER.ID(1,2)",
                     "See (=A1 FOO-REGISTER.ID(1,2))", "=A1 FOO-REGISTER.ID(1,2), or bar",
                     "=(1) and FOO-REGISTER.ID(1,2)", "See (=A1 then FOO-REGISTER.ID(1,2))",
                     "=A1 then FOO-REGISTER.ID(1,2), or bar", "=1 and FOO-REGISTER.ID(1,2)",
                     "=1-STDEV.S(Revenue and FOO-REGISTER.ID(1,2))",
                     "=1-STDEV.S(Revenue January and FOO-REGISTER.ID(1,2))",
                     "=1-STDEV.S(Revenue January North and FOO-REGISTER.ID(1,2))",
                     "=1-STDEV.S(Revenue January + FOO-REGISTER.ID(1,2))",
                     "=1-STDEV.S(Revenue January North + FOO-REGISTER.ID(1,2))",
                     "See (=SUM(1) then X+FOO-REGISTER.ID(1,2))",
                     "=SUM(1) then X+FOO-REGISTER.ID(1,2), or bar",
                     "=SUM(1)  and 1-REGISTER.ID(1,2)", "=SUM(1) AND 1-REGISTER.ID(1,2)",
                     "=SUM(1) then 1-REGISTER.ID(1,2)",
                     "=1-STDEV.S(1,2) and =1-REGISTER.ID(SUM(1) \"help desk\")", "=(1-REGISTER.ID())",
                     "=SUM(1) (FTP:X)", "=SUM(1) (1-REGISTER.ID(1,2))",
                     "=SUM(Table1[Col) (FTP:X)", "=SUM(Table1[[Col]) (FTP:X)",
                     "FOO.DIST", "BAR.S", "BAZ.TEST", "HOST.INTL", "XT.DIST.2T", "X.T.DIST.2T",
                     "http:B2", "FTP:X", "See (FTP:X)", "See (  FTP:X)", "See [ (FTP:X)]", "See \u201c(FTP:X)\u201d",
                     'See "mode=fast,(FTP:X)"', '=SUM(1) See "(FTP:X)"', '=SUM(FTP:FTP) See "(FTP:X)"',
                     '=SUM($FTP:$FTP) See "($FTP:X)"', 'See "($FTP:$FTP)"', 'See "(FTP:FTP%)"',
                     '=SUM(  FTP:FTP) See "(  FTP:X)"', '=SUM(2*FTP:FTP) See "(2*FTP:X)"',
                     '=SUM(FTP:FTP) See "(FTP:FTP)"', "See (FTP:FTP)", "See (A:A,FTP:FTP)", "s3:bucket"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name or address" in p for p in self.problems()), ascii(text))
        for text in ("Opens the dialog.\u2002", "Sets 1.5 line spacing.", "Ctrl+Shift+.", "Save As...", "(see Help.)",
                     "Word Document (*.docx)", "Excel Add-In (*.xla)", "PowerPoint Add-In (*.ppa)",
                     "Visio XML Drawing (*.vdx)", "Opens a .docx file.", ".docx", "Save as (.docx)",
                     "Loads Normal.dotm as the default template.", "Saves to Normal.dotm.",
                     "Calculates =STDEV.S(1,2).", "=NORM.S.DIST(0,TRUE)", "=1-STDEV.S(1,2)", "=-NORM.S.DIST(0,TRUE)",
                     "Calculates =1-STDEV.S(1,2) in each row.", "=SUM(1) and =1-STDEV.S(1,2)",
                     "=1 - STDEV.S(1,2)", "=1  -  STDEV.S(1,2)",
                     "=10-STDEV.S(1,2)", "=10%-STDEV.S(1,2)", "=A10-STDEV.S(1,2)", "=A100000-STDEV.S(1,2)",
                     "=XFD1048576-STDEV.S(1,2)", "=STDEV.S(A1:B3 B2:C4)", "=1-STDEV.S(A1:B3 B2:C4)",
                     "=1-STDEV.S($A$1:$B$3 $B$2:$C$4)", "=1-STDEV.S(Sheet1!A1:B3 Sheet1!B2:C4)",
                     "=1-STDEV.S('Sales Data'!A1:B3 'Sales Data'!B2:C4)", "=1-STDEV.S(Table1[Col1] Table1[Col2])",
                     "=STDEV.S(1:3 2:4)", "=1-STDEV.S(1:3 2:4)", "=1-STDEV.S($1:$3 $2:$4)",
                     "=STDEV.S(Revenue January)", "=1-STDEV.S(Revenue January)", "=1-STDEV.S(Revenue January North)",
                     "=STDEV.S(Revenue January North+1)", "=1-STDEV.S(Revenue January North+1)",
                     "=1-STDEV.S(Revenue January North + 1)", "=1-STDEV.S(Revenue January North=1)",
                     "=1-STDEV.S(Revenue January North = 1)", "=1-STDEV.S(Revenue January North+SUM(1))",
                     "=STDEV.S(Revenue January North+SUM(SUM(SUM(1))))",
                     "=1-STDEV.S(Revenue January North+SUM(SUM(1)))",
                     "=1-STDEV.S(Revenue January North+SUM(SUM(SUM(1))))",
                     "=1-STDEV.S(Revenue January North+SUM(SUM(SUM(SUM(SUM(1))))))",
                     "=1-STDEV.S(Revenue January North=SUM(SUM(SUM(1))))",
                     "=1-STDEV.S(Revenue January+SUM(SUM(SUM(1))))",
                     "=1-STDEV.S(Revenue January=SUM(SUM(SUM(1))))",
                     "=STDEV.S(Revenue January North+SUM(SUM({1,2})))",
                     "=1-STDEV.S(Revenue January North+SUM(SUM({1,2})))",
                     "=1-STDEV.S(Revenue January North+SUM({1,2}))",
                     "=1-STDEV.S(Revenue January North+{1,2})",
                     "=STDEV.S(Revenue January North+SUM(Table1[[#Data],[Amount]]))",
                     "=1-STDEV.S(Revenue January North+SUM(Table1[[#Data],[Amount]]))",
                     "=1-STDEV.S(Revenue January North+Table1[[#Data],[Amount]])",
                     "=1-STDEV.S(Revenue January North+SUM(SUM(Table1[[#Data],[Amount]])))",
                     "=1-STDEV.S(Revenue January North+SUM(SUM('John''s Data'!A1:A2)))",
                     "=1-STDEV.S(Revenue January North+SUM(IFERROR(#N/A,1)))",
                     "=1-STDEV.S(Revenue January IFERROR(#N/A,1))",
                     "=1-STDEV.S(Revenue January (#N/A))",
                     "=1-STDEV.S(A1:'Sales Data'!B2)",
                     "=1-STDEV.S(Table1[Amount]:'Sales Data'!B2)",
                     "=1-STDEV.S((Table1[[#Data],[Amount]]) January)",
                     "=STDEV.S(Revenue January North+SUM(RANDARRAY(,2)))",
                     "=1-STDEV.S(Revenue January North+SUM(RANDARRAY(,2)))",
                     "=1-STDEV.S(Revenue January North+SUM(RANDARRAY(;2)))",
                     "=1-STDEV.S(Revenue January North+SUM(RANDARRAY(1,2)))",
                     "=1-STDEV.S(Revenue January RANDARRAY(,2))",
                     "=1-STDEV.S(RANDARRAY(2,)+1)-STDEV.S(1,2)",
                     "=1-STDEV.S((A1+B1)%)-STDEV.S(1,2)",
                     "=STDEV.S(Revenue January North+SUM(RAND()))",
                     "=1-STDEV.S(Revenue January North+SUM(RAND()))",
                     "=1-STDEV.S(Revenue January North+SUM(NOW()))",
                     "=1-STDEV.S(Revenue January North+SUM(RANDARRAY()))",
                     "=1-STDEV.S(Revenue January North+RAND())",
                     "=1-STDEV.S(Revenue January ROW())",
                     "=1-STDEV.S(A1:B2 @A1:A10)",
                     "=SUM(A1:B2 @A1:A10, FTP:FTP)",
                     "=1-STDEV.S(SUM(RAND()), 2)", "=1-STDEV.S(SUM((1)), 2)",
                     "=1-REGISTER.ID(SUM(RAND()), 2)", "=1-REGISTER.ID(SUM((1)), 2)",
                     "=1-REGISTER.ID(SUM(RAND())+SUM(RAND()), 2)",
                     "Inserts REGISTER.ID, =1-REGISTER.ID(A1:B2) or =-REGISTER.ID(1,2).",
                     "=1-STDEV.S(1,2) returns \"number\".",
                     "=1-STDEV.S(1,2) returns \"number\" (example).",
                     "=STDEV.S(1,2) returns \"number\" (example).",
                     "=1-STDEV.S(1,2) returns \"number\" ((nested) example).",
                     "=1-REGISTER.ID(1,2) returns \"number\" (example).",
                     "=1-REGISTER.ID(1, SUM(RAND())) returns \"number\" (example).",
                     "=1-STDEV.S(1, SUM(RAND())) returns \"number\" (example).",
                     "=1-STDEV.S(1,2) returns \"number\" (for example, =SUM(SUM(1))).",
                     "=STDEV.S(1,2) returns \"number\" (for example, =SUM(SUM(1))).",
                     "=1-STDEV.S(1,2) returns \"number\" (((example))).",
                     "=1-STDEV.S(1, SUM(RAND())) returns \"number\" (for example, =SUM(SUM(1))).",
                     "=1-REGISTER.ID(1,2) returns \"number\" (for example, =SUM(SUM(1))).",
                     "(=1-STDEV.S(1,2) returns \"number\")",
                     "=1-STDEV.S(Revenue January North=SUM(1))", "=1-STDEV.S(Revenue January North-STDEV.S(1,2))",
                     "=1-STDEV.S(Revenue January North - STDEV.S(1,2))",
                     "=1-STDEV.S(Revenue January North Q1+1)", "=1-STDEV.S(Revenue January North A1:B3+1)",
                     "=1-STDEV.S((Revenue) January North+1)", "=1-STDEV.S((Revenue) January North=1)",
                     "=1-STDEV.S((Revenue) January North+SUM(1))",
                     "=1-STDEV.S(Revenue (January) North+1)", "=1-STDEV.S(A1:B3 January North+1)",
                     "=SUM(Revenue January North+1, FTP:FTP)", "=SUM(Revenue January North=1, FTP:FTP)",
                     "=STDEV.S(Revenue January=1)", "=1-STDEV.S(Revenue January=1)", "=1-STDEV.S(Revenue January = 1)",
                     "=STDEV.S(Revenue January+SUM(1))", "=1-STDEV.S(Revenue January+SUM(1))",
                     "=1-STDEV.S(Revenue January + SUM(1))", "=STDEV.S(Revenue January=SUM(1))",
                     "=1-STDEV.S(Revenue January=SUM(1))", "=1-STDEV.S(Revenue January = SUM(1))",
                     "=1-STDEV.S(Revenue January-STDEV.S(1,2))", "=1-STDEV.S(Revenue January - STDEV.S(1,2))",
                     "=1-STDEV.S(Revenue January*SUM(A1:A2))", "=1-STDEV.S(Revenue January/SUM(A1:A2))",
                     "=1-STDEV.S(Revenue January>=SUM(1))",
                     "=SUM(Revenue January+SUM(1), FTP:FTP)", "=SUM(Revenue January=SUM(1), FTP:FTP)",
                     "=STDEV.S(R[-1]C R[-2]C)", "=1-STDEV.S(R[-1]C R[-2]C)", "=1-STDEV.S(R[-1]C[-1] R[-2]C[-2])",
                     "=1-STDEV.S(R[-1]C:R[-2]C)", "=1-STDEV.S(R1:R3 C1:C3)", "=1-STDEV.S(R[-1]:R[1] C[-1]:C[1])",
                     "=1-STDEV.S((A1:B3) (B2:C4))", "=1-STDEV.S((Revenue) (January))",
                     "=STDEV.S(A1:B3 (INDEX(A1:C3,1,0)))", "=1-STDEV.S(A1:B3 (INDEX(A1:C3,1,0)))",
                     "=1-STDEV.S((INDEX(A1:C3,0,1)) (INDEX(A1:C3,1,0)))",
                     "=1-STDEV.S(((A1:B3)) ((INDEX(A1:C3,1,0))))",
                     "=1-STDEV.S(Revenue (INDEX(A1:C3,1,0))=1)", "=1-STDEV.S((Revenue) January North)",
                     "=1-STDEV.S((Revenue) January+SUM(1))", "=1-STDEV.S((Revenue) January=1)",
                     "=1-STDEV.S((A1:B3) January)", "=1-STDEV.S((Sheet1!A1:B3) January)",
                     "=1-STDEV.S(('Sales Data'!A1:B3) January)", "=1-STDEV.S((Table1[Amount]) January)",
                     "=1-STDEV.S(A1:B3 Revenue B2:C4)", "=1-STDEV.S(A1:B3 Revenue Sheet1!B2:C4)",
                     "=1-STDEV.S(A1:B3 Revenue Table1[Amount])", "=1-STDEV.S(A1:B3 Revenue INDEX(A1:C3,1,0))",
                     "=1-STDEV.S(A1:B3 (Sheet1!B2:C4))", "=1-STDEV.S(A1:B3 ('Sales Data'!B2:C4))",
                     "=1-STDEV.S(A1:B3 (Table1[Amount]))", "=1-STDEV.S(A1:B3 (OFFSET(SUM(A1),0,0,2,2)))",
                     "=1-STDEV.S(PI(), 2)", "=1-STDEV.S(ROW(), COLUMN())",
                     "=1-STDEV.S(A1:INDEX(A1:C3,3,3))", "=1-STDEV.S(INDEX(A1:C3,1,1):B3)",
                     "=1-STDEV.S({-1, 2; 3, 4})",
                     "=1-STDEV.S(INDEX(A1:C3,0,1) INDEX(A1:C3,1,0))", "=1-STDEV.S(A1# B1#)",
                     "=1-STDEV.S(Sheet1:Sheet3!A1:B2)", "=SUM(Sheet1:Sheet3!A1:B2, FTP:FTP)",
                     "=SUM(Revenue January, FTP:FTP)", "=SUM(Revenue January=1, FTP:FTP)",
                     "=SUM(A1:B3 (INDEX(A1:C3,1,0)), FTP:FTP)",
                     "=SUM(R[-1]C R[-2]C, FTP:FTP)", "=SUM(1:3 2:4, FTP:FTP)",
                     "=Total-STDEV.S(A1:A2)", "=Table1[Amount]-STDEV.S(A1:A2)", "=SUM('Sales Data'!A1)-STDEV.S(A1:A2)",
                     "=SUM('John''s Data'!A1)-STDEV.S(A1:A2)", "=SUM(Table1[[#Data],[Amount]])-STDEV.S(A1:A2)",
                     "=SUM(Table1[QuarterlyRevenueForecastAmount])-STDEV.S(A1:A2)",
                     "=SUM(A1 + B1)-STDEV.S(A1:A2)",
                     "=1-STDEV.S(1, 2)", "=1-STDEV.S(SUM(A1:A2),2)", "=1-STDEV.S(SUM(SUM(A1:A2)),2)",
                     "=1-STDEV.S(SUM(SUM(SUM(SUM(A1:A2)))),2)", "=1-STDEV.S(Sheet1!A1:A2)", "=1-STDEV.S(A1:A2,3%)",
                     "=1-STDEV.S('Sales Data'!A1:A2)", "=1-STDEV.S('John''s Data'!A1:A2)",
                     "=1-STDEV.S(Table1[Amount])", "=1-STDEV.S(Table1[[#Data],[Amount]])", "=1-STDEV.S({1,2,3})",
                     "Calculates =SUM(A1:B2).", "=SUM($A$1:$B$2, XFD1:XFD1048576, A:Z, R1C1:R2C2)",
                     "=SUM(FTP:FTP)", "=SUM($FTP:$FTP)", "=SUM($FTP:FTP)", "=SUM(FTP:$FTP)",
                     "=SUM(FTP:FTP%)", "=SUM($FTP:$FTP%)", "=SUM(2*$FTP:$FTP%)",
                     "=SUM(A1:B3 FTP:FTP)", "=SUM(FTP:FTP B2:C4)", "=SUM($FTP:$FTP B2:C4)",
                     "=SUM( FTP:FTP)", "=SUM(  FTP:FTP)", "=SUM(FTP:FTP )", "=SUM(FTP:FTP+1)",
                     "=SUM(FTP:FTP*2)", "=SUM(2*FTP:FTP)", "=SUM(2 * FTP:FTP)", "=SUM(A1+FTP:FTP)",
                     "=SUM(FTP:FTP/2)", "=SUM(2/FTP:FTP)", "=SUM((FTP:FTP)*2)", "=SUM(2*(FTP:FTP))",
                     "=SUM(A:A,FTP:FTP)", "=SUM(A:A, FTP:FTP)", "=SUM(A:A,  FTP:FTP)",
                     "=SUM(1) and =SUM(FTP:FTP)", "=SUM(A1 + B1,FTP:FTP)", "=SUM('Sales Data'!A1,FTP:FTP)",
                     "=SUM('Sales Data'!  FTP:FTP)", "=SUM('John''s Data'!A1,FTP:FTP)",
                     "=SUM(Table1[[#Data],[Amount]],FTP:FTP)", "=SUM(Table1[QuarterlyRevenueForecastAmount],FTP:FTP)",
                     "=SUM(SUM(FTP:FTP))", "=SUM(SMB:SMB)", "=SUM(Sheet1!FTP:FTP)", "=SUM(Sheet1!  FTP:FTP)"):
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, label="Word Document (*.docx)", behaviour=text)])
            self.assertEqual(self.problems(), [], ascii(text))
        schema = json.loads((Path(__file__).resolve().parents[2] / ci.SCHEMA).read_text(encoding="utf-8"))
        exts = ("docx", "docm", "dotx", "dotm", "doc", "dot", "xlsx", "xlsm", "xltx", "xltm", "xlsb", "xls", "xlt",
                "xlam", "xla", "pptx", "pptm", "potx", "potm", "ppsx", "ppsm", "ppt", "pot", "pps", "ppam", "ppa",
                "vsdx", "vsdm", "vstx", "vstm", "vssx", "vssm", "vsd", "vst", "vss", "vdx", "vsx", "vtx", "mpp",
                "mpt", "mpx", "msg", "pst", "ost", "eml", "ics", "vcf", "oft", "pab", "oab", "odt", "ods", "odp",
                "odg", "odf", "ott", "ots", "otp", "otg", "otf", "rtf", "txt", "csv", "tsv", "pdf", "xps", "oxps",
                "xml", "json", "htm", "html", "mht", "mhtml", "svg", "png", "jpg", "jpeg", "gif", "bmp", "tif",
                "tiff", "emf", "wmf", "ico", "thmx", "dic", "acl", "accda", "accdb", "accde", "accdr", "accdt",
                "mdb", "ddb", "dif", "slk", "prn", "iqy", "dqy", "oqy", "rqy", "odc", "udl", "dsn", "cub", "exe",
                "dll", "ini", "bas", "vbs", "bak", "tmp", "log", "bin", "dat")
        self.assertEqual(len(exts), 115)
        for ext in exts:
            for variant in (ext, ext.upper()):
                rec = dict(BOLD, label=f"Format (*.{variant})", behaviour=f"Saves File.{variant} or .{variant}.")
                self.assertEqual(ci.validate([rec], schema, schema), [], variant)
        funcs = ("BETA.DIST", "BETA.INV", "BINOM.DIST", "BINOM.DIST.RANGE", "BINOM.INV", "CEILING.MATH",
                 "CEILING.PRECISE", "CHISQ.DIST", "CHISQ.DIST.RT", "CHISQ.INV", "CHISQ.INV.RT", "CHISQ.TEST",
                 "CONFIDENCE.NORM", "CONFIDENCE.T", "COVARIANCE.P", "COVARIANCE.S", "ECMA.CEILING", "ERF.PRECISE",
                 "ERFC.PRECISE", "ERROR.TYPE", "EXPON.DIST", "F.DIST", "F.DIST.RT", "F.INV", "F.INV.RT", "F.TEST",
                 "FLOOR.MATH", "FLOOR.PRECISE", "FORECAST.ETS", "FORECAST.ETS.CONFINT", "FORECAST.ETS.SEASONALITY",
                 "FORECAST.ETS.STAT", "FORECAST.LINEAR", "GAMMA.DIST", "GAMMA.INV", "GAMMALN.PRECISE", "HYPGEOM.DIST",
                 "ISO.CEILING", "LOGNORM.DIST", "LOGNORM.INV", "MODE.MULT", "MODE.SNGL", "NEGBINOM.DIST",
                 "NETWORKDAYS.INTL", "NORM.DIST", "NORM.INV", "NORM.S.DIST", "NORM.S.INV", "PERCENTILE.EXC",
                 "PERCENTILE.INC", "PERCENTRANK.EXC", "PERCENTRANK.INC", "POISSON.DIST", "QUARTILE.EXC",
                 "QUARTILE.INC", "RANK.AVG", "RANK.EQ", "REGISTER.ID", "SKEW.P", "SQL.REQUEST", "STDEV.P", "STDEV.S",
                 "T.DIST", "T.DIST.2T", "T.DIST.RT", "T.INV", "T.INV.2T", "T.TEST", "VAR.P", "VAR.S", "WEIBULL.DIST",
                 "WORKDAY.INTL", "Z.TEST")
        self.assertEqual(len(funcs), 73)
        for fn in funcs:
            rec = dict(BOLD, label=fn, behaviour=f"Inserts {fn}, =1-{fn}(A1:B2) or =-{fn}(1,2).")
            self.assertEqual(ci.validate([rec], schema, schema), [], fn)

    def test_unencodable_record_text_is_reported_not_a_crash(self):
        # Audit round 7, finding 2: a lone surrogate in a record reaches the report; printing it must not raise.
        path = self.inv / "word" / "ribbon.json"
        path.write_text('[{"id": "word.home", "app": "word", "kind": "tab", "label": "Home", "order": 1, '
                        '"captureProfile": "\\ud800"}]', encoding="utf-8")
        out = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
        with contextlib.redirect_stdout(out):
            code = ci.main([str(path)])
        out.flush()
        self.assertEqual(code, 1)
        self.assertIn(b"\\ud800", out.buffer.getvalue())

    def test_the_manifest_lists_the_upstream_workbook_set(self):
        # Audit round 11, finding 1: one workbook per single-workbook app, at least one Outlook window, nothing else.
        real = json.loads((ci.INVENTORY / ci.SOURCES).read_text(encoding="utf-8"))
        word = real["blobs"]["wordcontrols.xlsx"]
        removed = json.loads(json.dumps(real)); del removed["blobs"]["wordcontrols.xlsx"]
        invented = json.loads(json.dumps(removed)); invented["blobs"]["notepadcontrols.xlsx"] = word
        no_outlook = json.loads(json.dumps(real))
        no_outlook["blobs"] = {k: v for k, v in real["blobs"].items() if not k.startswith("outlook")}
        for name, manifest in (("removed", removed), ("invented", invented), ("no Outlook", no_outlook)):
            (self.inv / ci.SOURCES).write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(ci.Unreadable, msg=name):
                ci.check([str(self.inv)], inventory=self.inv)

    def test_an_unreadable_reference_exits_2(self):
        # Audit round 11, finding 2: REFERENCE.md that cannot be read is a controlled failure.
        # (main turns Unreadable into exit 2; test_hostile_files_exit_2_with_a_diagnostic covers that step.)
        self.write("word/ribbon.json", [TAB])
        (self.inv / ci.REFERENCE).write_bytes(b"\xff\xfe not utf-8 \x80")
        with self.assertRaises(ci.Unreadable) as raised:
            ci.check([str(self.inv)], inventory=self.inv)
        self.assertIn("REFERENCE.md: cannot read", str(raised.exception))

    def test_long_strings_cost_bounded_time(self):
        # Audit round 11, finding 3, round 15, finding 2, round 16, finding 1, and round 17, finding 1: the link and
        # address patterns never search past a field's maxLength, repeated formula-span tokens below maxLength run in
        # bounded time without backtracking, and a subprocess timeout guards against any future catastrophic regex hang.
        import subprocess
        import sys
        import time
        for field in ("label", "behaviour", "uiaId"):
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, **{field: "a" * 40000})])
            start = time.perf_counter()
            problems = self.problems()
            self.assertLess(time.perf_counter() - start, 3.0, field)
            self.assertTrue(any(f".{field}: longer than" in p for p in problems), field)
        accepted = (
            "=1" + (" + " * 30) + "2",
            "=SUM(Table1[" + "a" * 30 + "])",
            "=SUM(Table1[QuarterlyRevenueForecastAmount])",
            "=SUM(" + ("'John''s Data'!A1," * 15) + "FTP:FTP)",
            "=SUM(" + ("Table1[[#Data],[Amount]]," * 15) + "FTP:FTP)",
            "=" + "SUM(" * 20 + "1" + ")" * 20,
            "=" + "+".join(f"SUM(A{i})" for i in range(1, 21)),
            "=1-STDEV.S(" + "SUM(" * 20 + "1" + ")" * 21,
        )
        refused = (
            "=SUM(Table1[" + "a" * 30 + ") (FTP:X)",
            "=SUM(Table1[[" + "a" * 30 + "]) (FTP:X)",
            "=" + "SUM(" * 20 + "1" + ")" * 20 + ' See "(FTP:X)"',
        )
        for text in refused:
            self.assertGreater(len(text), 0)
        probe = (
            "import importlib.util, json, pathlib, time; "
            "spec = importlib.util.spec_from_file_location('ci', 'scripts/check-inventory.py'); "
            "ci = importlib.util.module_from_spec(spec); spec.loader.exec_module(ci); "
            "schema = json.loads(pathlib.Path('design/inventory/schema.json').read_text(encoding='utf-8')); "
            f"accepted = {accepted!r}; refused = {refused!r}; base = {BOLD!r}; "
            "run = lambda t: (start := time.perf_counter(), "
            "p := ci.validate([dict(base, label='Word Document (*.docx)', behaviour=t)], schema, schema, 't'), "
            "time.perf_counter() - start)[1:]; "
            "assert all(p == [] and dt < 1.0 for p, dt in (run(t) for t in accepted)); "
            "assert all(any('host name or address' in m for m in p) and dt < 1.0 "
            "for p, dt in (run(t) for t in refused))"
        )
        subprocess.run([sys.executable, "-c", probe], cwd=str(SCRIPTS.parent), timeout=5.0, check=True)

    def test_each_file_is_loaded_once_per_check(self):
        # Audit round 23, finding 1: schema and relationship checks must inspect the same loaded content, so a file
        # that changes between two reads cannot pass by combining two invalid versions.
        named = self.write("word/ribbon.json", [TAB])
        versions = [
            [{"id": "word.home", "app": "word", "kind": "tab"}],
            [{"id": "word.home", "app": "word", "kind": "tab", "label": "Home", "parent": "word.home"}],
        ]
        real_load = ci.load
        calls = []

        def changing_load(path):
            if Path(path).resolve() == named.resolve():
                calls.append(path)
                return versions[min(len(calls) - 1, len(versions) - 1)]
            return real_load(path)

        ci.load = changing_load
        try:
            problems = ci.check([str(named)], inventory=self.inv)
        finally:
            ci.load = real_load
        self.assertEqual(len(calls), 1)
        self.assertTrue(any("missing label" in p for p in problems), problems)

    def test_outlook_baseline_columns_take_any_folder_case(self):
        # Audit round 23, finding 2: OUTLOOK/baseline.json on a case-insensitive file system still uses Outlook's
        # column layout.
        data = json.loads((ci.INVENTORY / "outlook" / "baseline.json").read_text(encoding="utf-8"))
        problems = ci.check_baseline(Path("OUTLOOK/baseline.json"), data, ci.load(ci.BASELINE_SCHEMA),
                                     ci.load(ci.INVENTORY / ci.SOURCES))
        self.assertEqual(problems, [])

    def test_compatibility_characters_with_an_ascii_form_are_refused_in_text(self):
        # Audit round 22, re-think of the text rule: fullwidth digits spell 127.0.0.1 to IDNA, so every compatibility
        # character whose normalised form holds a visible ASCII character is refused, not one family per round. The
        # class is generated from the Unicode data of the Python CI pins; a newer Python fails here until it is
        # regenerated, which is the signal to do so.
        import unicodedata
        one = chr(0xFF11)
        for text in (one + "27" + ".0.0.1", "127.0.0." + one, chr(0x2460) + "com", chr(0xFB01) + "le"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name or address" in p for p in self.problems()), ascii(text))
        pattern = ci.ecma(ci.load(ci.SCHEMA)["$defs"]["noHost"]["not"]["pattern"])
        missed = [hex(c) for c in range(0x80, 0x10000) if not 0xD800 <= c <= 0xDFFF and c != 0x2026
                  and unicodedata.normalize("NFKC", chr(c)) != chr(c)
                  and any(0x21 <= ord(x) < 0x7F for x in unicodedata.normalize("NFKC", chr(c)))
                  and not pattern.search(chr(c))]
        self.assertEqual(missed, [])
        # Text with no compatibility form, or one that is only a space, is untouched.
        for text in ("R" + chr(0xE9) + "sum" + chr(0xE9), "Page" + chr(0xA0) + "1", chr(0x2014) + " Gallery"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertEqual(self.problems(), [], ascii(text))

    def test_a_hexadecimal_number_beside_a_full_stop_is_an_address(self):
        # Audit round 22, finding 1: inet_aton reads 127.0x0.1 and 0x7f.1 as addresses.
        for text in ("127.0x0.1", "0x7f.1", "1.0X1"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name or address" in p for p in self.problems()), text)

    def test_a_baseline_in_any_case_takes_the_baseline_checks(self):
        # Audit round 22, finding 2: on a case-insensitive file system BASELINE.JSON is the baseline.
        self.assertTrue(ci.is_baseline(Path("word") / "BASELINE.JSON"))
        self.assertTrue(ci.is_baseline("word/Baseline.Json"))
        self.assertFalse(ci.is_baseline("word/baseline.json.bak"))
        self.write("word/ribbon.json", [TAB])
        named = self.inv / "word" / "BASELINE.JSON"
        named.write_text(json.dumps([dict(TAB, id="word.probe")]), encoding="utf-8")
        problems = ci.check([str(named)], inventory=self.inv)
        self.assertTrue(any("expected object" in p or "is not of type 'object'" in p for p in problems), problems[:3])

    def test_a_baseline_row_of_the_wrong_length_is_refused(self):
        # Audit round 22, finding 3: the row-length guard, on its own.
        data = json.loads((ci.INVENTORY / "word" / "baseline.json").read_text(encoding="utf-8"))
        data["rows"][0] = data["rows"][0][:-1]
        problems = ci.check_baseline(Path("word/baseline.json"), data, ci.load(ci.BASELINE_SCHEMA))
        self.assertTrue(any("cells, expected" in p for p in problems), problems)

    def test_compatibility_expansions_cannot_spell_an_address(self):
        # Audit round 21, finding 1: U+33C2 U+33C7 is a.m.Co. once normalised, an address its raw spelling hides.
        import unicodedata
        self.write("word/ribbon.json", [dict(TAB, label=chr(0x33C2) + chr(0x33C7))])
        self.assertTrue(any("host name or address" in p for p in self.problems()))
        pattern = ci.ecma(ci.load(ci.SCHEMA)["$defs"]["noHost"]["not"]["pattern"])
        missed = [hex(c) for c in range(0x10000) if not 0xD800 <= c <= 0xDFFF and c not in (0x2E, 0x3A, 0x2026)
                  and any(m in unicodedata.normalize("NFKC", chr(c)) for m in ".:") and not pattern.search(chr(c))]
        self.assertEqual(missed, [])
        # The plain full stop and the ellipsis still end a label.
        for text in ("Save As...", "Save As" + chr(0x2026)):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertEqual(self.problems(), [], ascii(text))

    def test_a_dotted_host_with_a_path_is_a_link_in_identifier_fields(self):
        # Audit round 21, finding 2: the host-and-path alternative of noLink, on its own.
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, uiaId="microsoft.de/help")])
        self.assertTrue(any(".uiaId" in p and "link" in p for p in self.problems()))

    def test_characters_containing_a_full_stop_are_address_marks(self):
        # Audit round 20, finding 1: U+2488 normalises to "1.", so "<U+2488>com" is 1.com to IDNA.
        import unicodedata
        for code in (0x2488, 0x33C2, 0x2025):
            self.write("word/ribbon.json", [dict(TAB, label=chr(code) + "com")])
            self.assertTrue(any("host name or address" in p for p in self.problems()), hex(code))
        pattern = ci.ecma(ci.load(ci.SCHEMA)["$defs"]["noHost"]["not"]["pattern"])
        missed = [hex(c) for c in range(0x10000) if not 0xD800 <= c <= 0xDFFF
                  and "." in unicodedata.normalize("NFKC", chr(c)) and not pattern.search(chr(c) + "com")]
        self.assertEqual(missed, [])

    def test_the_reference_commit_row_is_read_in_any_spacing_and_required(self):
        # Audit round 20, finding 2: extra spaces in the row must not switch the comparison off; no row is unreadable.
        text = (ci.INVENTORY / ci.REFERENCE).read_text(encoding="utf-8")
        real = json.loads((ci.INVENTORY / ci.SOURCES).read_text(encoding="utf-8"))
        real["commit"] = "0" * 40
        (self.inv / ci.SOURCES).write_text(json.dumps(real), encoding="utf-8")
        named = self.write("word/ribbon.json", [TAB])
        spaced = text.replace("| Commit | ", "|  Commit  |   ", 1)
        missing = text.replace("| Commit |", "| Revision |", 1)
        for reference in (spaced, missing):
            (self.inv / ci.REFERENCE).write_text(reference, encoding="utf-8")
            with self.assertRaises(ci.Unreadable):
                ci.check([str(named)], inventory=self.inv)

    def test_a_baseline_with_the_wrong_columns_is_refused(self):
        # Audit round 20, finding 3: the column-layout guard, on its own.
        data = json.loads((ci.INVENTORY / "word" / "baseline.json").read_text(encoding="utf-8"))
        data["columns"][0] = "tab"
        problems = ci.check_baseline(Path("word/baseline.json"), data, ci.load(ci.BASELINE_SCHEMA))
        self.assertTrue(any("columns" in p and "are not" in p for p in problems), problems)

    def test_compatibility_full_stops_and_colons_are_address_marks(self):
        # Audit round 19, finding 1: IDNA normalises U+2024 and U+FE52 to a full stop, so they separate a host too.
        for dot in (0x2024, 0xFE52, 0xFF0E, 0x3002):
            label = "support" + chr(dot) + "microsoft" + chr(dot) + "com"
            self.write("word/ribbon.json", [dict(TAB, label=label)])
            self.assertTrue(any("host name or address" in p for p in self.problems()), hex(dot))
        for colon in (0xFE13, 0xFE55):
            self.write("word/ribbon.json", [dict(TAB, label="https" + chr(colon) + "x")])
            self.assertTrue(any("host name or address" in p for p in self.problems()), hex(colon))
        # The classes hold every character whose compatibility form is a full stop or a colon.
        import unicodedata
        pattern = ci.ecma(ci.load(ci.SCHEMA)["$defs"]["noHost"]["not"]["pattern"])
        for target in (".", ":"):
            forms = [c for c in range(0x10000) if not 0xD800 <= c <= 0xDFFF
                     and unicodedata.normalize("NFKC", chr(c)) == target]
            missed = [hex(c) for c in forms if not pattern.search("https" + chr(c) + "x" if target == ":"
                                                                  else "a" + chr(c) + "b")]
            self.assertEqual(missed, [], target)

    def test_identifier_fields_are_ascii(self):
        # Audit round 19, finding 1, identifier side: no look-alike reaches idMso or uiaId.
        for field, text in (("idMso", "File" + chr(0xFF0E) + "Save"), ("uiaId", "Ribbon" + chr(0x3002) + "x"),
                            ("idMso", "File Save"), ("uiaId", "two  spaces")):
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, **{field: text})])
            self.assertTrue(any(f".{field}" in p for p in self.problems()), (field, ascii(text)))
        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, uiaId="Ribbon Tab Home")])
        self.assertEqual(self.problems(), [])

    def test_a_link_in_the_inventory_is_unreadable(self):
        # Audit round 19, finding 2: a symbolic link (or junction) would hide files or bring in outside ones.
        import os
        self.write("word/ribbon.json", [TAB])
        real_scandir = os.scandir
        word = (self.inv / "word").resolve()

        class Entry:
            def __init__(self, entry):
                self._entry, self.name, self.path = entry, entry.name, entry.path

            def is_symlink(self):
                return Path(self.path).resolve() == word

            def is_junction(self):
                return False

            def is_dir(self, **kwargs):
                return self._entry.is_dir(**kwargs)

            def is_file(self, **kwargs):
                return self._entry.is_file(**kwargs)

        class Listing:
            def __init__(self, path):
                self._it = real_scandir(path)

            def __enter__(self):
                return (Entry(e) for e in self._it)

            def __exit__(self, *exc):
                self._it.close()

        os.scandir = Listing
        try:
            with self.assertRaises(ci.Unreadable) as raised:
                ci.check([str(self.inv)], inventory=self.inv)
            self.assertIn("a link in the inventory", str(raised.exception))
        finally:
            os.scandir = real_scandir

    def test_the_manifest_commit_is_the_reference_commit(self):
        # Audit round 19, finding 3: manifest and baselines agreeing among themselves is not enough.
        real = json.loads((ci.INVENTORY / ci.SOURCES).read_text(encoding="utf-8"))
        real["commit"] = "0" * 40
        (self.inv / ci.SOURCES).write_text(json.dumps(real), encoding="utf-8")
        # The inventory's own reference pins the commit (a scratch inventory without one is not bound to the
        # repository's).
        reference = (ci.INVENTORY / ci.REFERENCE).read_text(encoding="utf-8")
        (self.inv / ci.REFERENCE).write_text(reference, encoding="utf-8")
        named = self.write("word/ribbon.json", [TAB])
        with self.assertRaises(ci.Unreadable) as raised:
            ci.check([str(named)], inventory=self.inv)
        self.assertIn("is not the commit REFERENCE.md pins", str(raised.exception))

    def test_an_unknown_outlook_window_is_refused(self):
        # Audit round 19, finding 4: the window guard, on its own.
        data = json.loads((ci.INVENTORY / "outlook" / "baseline.json").read_text(encoding="utf-8"))
        data["rows"][0][0] = "inventedwindow"
        problems = ci.check_baseline(Path("outlook/baseline.json"), data, ci.load(ci.BASELINE_SCHEMA),
                                     ci.load(ci.INVENTORY / ci.SOURCES))
        self.assertTrue(any("is not a window in the manifest" in p for p in problems), problems[:3])

    def test_every_format_character_is_refused(self):
        # Audit round 18, finding 1: the interlinear annotation controls, and every other BMP format character.
        import unicodedata
        for code in (0xFFF9, 0xFFFA, 0xFFFB, 0x0600, 0x06DD, 0x2066):
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, label=chr(code), behaviour=chr(code))])
            self.assertTrue(any(".label" in p and "control character" in p for p in self.problems()), hex(code))
        # The class covers every BMP format and control character this Python's Unicode data knows.
        pattern = ci.ecma(ci.load(ci.SCHEMA)["$defs"]["noControl"]["not"]["pattern"])
        missed = [hex(c) for c in range(0x10000) if not 0xD800 <= c <= 0xDFFF
                  and unicodedata.category(chr(c)) in ("Cc", "Cf") and not pattern.search(chr(c))]
        self.assertEqual(missed, [])

    def test_astral_characters_are_refused_in_both_regex_modes(self):
        # Audit round 18, finding 3: without the u flag a character outside the BMP is two surrogate code units; with
        # it, one code point. The pattern refuses it either way.
        import re
        source = ci.load(ci.SCHEMA)["$defs"]["noControl"]["not"]["pattern"]
        pattern = ci.ecma(source)
        for code in (0xE0100, 0x1F600):
            self.assertTrue(pattern.search(ci.utf16(chr(code))), hex(code))  # code units, as without the u flag
            self.assertTrue(pattern.search(chr(code)), hex(code))  # code points, as with it

    def test_an_unclassifiable_entry_is_unreadable(self):
        # Audit round 18, finding 2: an entry whose kind cannot be read must not drop out of discovery.
        import os
        self.write("word/ribbon.json", [TAB])
        real_scandir = os.scandir
        word = (self.inv / "word").resolve()

        class Entry:
            def __init__(self, entry):
                self._entry = entry
                self.name, self.path = entry.name, entry.path

            def is_dir(self, **kwargs):
                if Path(self.path).resolve() == word:
                    raise PermissionError(13, "Access is denied", self.path)
                return self._entry.is_dir(**kwargs)

            def is_file(self, **kwargs):
                return self._entry.is_file(**kwargs)

            def is_symlink(self):
                return self._entry.is_symlink()

            def is_junction(self):
                return False

        class Listing:
            def __init__(self, path):
                self._it = real_scandir(path)

            def __enter__(self):
                return (Entry(e) for e in self._it)

            def __exit__(self, *exc):
                self._it.close()

        os.scandir = Listing
        try:
            with self.assertRaises(ci.Unreadable):
                ci.check([str(self.inv)], inventory=self.inv)
        finally:
            os.scandir = real_scandir

    def test_a_baseline_source_must_name_the_manifest_commit(self):
        # Audit round 18, finding 4: the baseline envelope's source is compared with the manifest's commit.
        data = json.loads((ci.INVENTORY / "word" / "baseline.json").read_text(encoding="utf-8"))
        data["source"] = "baseline:" + "0" * 40
        problems = ci.check_baseline(Path("word/baseline.json"), data, ci.load(ci.BASELINE_SCHEMA),
                                     ci.load(ci.INVENTORY / ci.SOURCES))
        self.assertTrue(any("is not the manifest commit" in p for p in problems), problems)

    def test_characters_outside_the_bmp_are_refused(self):
        # Audit round 17, finding 1: supplementary ignorables (variation selectors, tags) and anything else astral.
        sc = {"id": "word.shortcuts.bold", "app": "word", "kind": "shortcut", "label": "Bold"}
        for code in (0xE0100, 0xE0001, 0x1F600):
            self.write("word/ribbon.json", [dict(TAB, label=chr(code))])
            self.assertTrue(any(".label" in p and "control character" in p for p in self.problems()), hex(code))
            self.write("word/ribbon.json", [TAB])
            self.write("word/shortcuts.json", [dict(sc, shortcut="Ctrl+B" + chr(code))])
            self.assertTrue(any(".shortcut" in p for p in self.problems()), hex(code))
        self.assertEqual(ci.utf16(chr(0xE0100)), chr(0xDB40) + chr(0xDD00))

    def test_an_unreadable_folder_is_unreadable_not_empty(self):
        # Audit round 17, finding 2: a folder that cannot be listed must not pass for an empty one.
        import os
        self.write("word/ribbon.json", [TAB])
        real_scandir = os.scandir

        def refusing(path=".", *args):
            if Path(path).resolve() == (self.inv / "word").resolve():
                raise PermissionError(13, "Access is denied", str(path))
            return real_scandir(path, *args)
        os.scandir = refusing
        try:
            with self.assertRaises(ci.Unreadable):
                ci.check([str(self.inv)], inventory=self.inv)
        finally:
            os.scandir = real_scandir

    def test_a_baseline_with_no_rows_is_refused(self):
        # Audit round 17, finding 3: the empty-row rule, on its own.
        data = json.loads((ci.INVENTORY / "word" / "baseline.json").read_text(encoding="utf-8"))
        data["rows"] = []
        problems = ci.check_baseline(Path("word/baseline.json"), data, ci.load(ci.BASELINE_SCHEMA))
        self.assertTrue(any("no rows" in p for p in problems), problems)

    def test_invisible_characters_cannot_hide_an_address(self):
        # Audit round 16, finding 1: URL parsers drop U+FEFF and other default-ignorables, so they are refused.
        self.write("word/ribbon.json", [dict(TAB, label="https:\ufeffsupport.\ufeffmicrosoft.\ufeffcom/x")])
        self.assertTrue(any("control character" in p for p in self.problems()))
        for ch in ("\u200b", "\u00ad", "\u2060", "\ufe0f", "\u202e"):
            self.write("word/ribbon.json", [dict(TAB, label=f"Ho{ch}me")])
            self.assertTrue(any("control character" in p for p in self.problems()), ascii(ch))

    def test_naming_a_folder_above_the_inventory_runs_the_whole_inventory_gate(self):
        # Audit round 16, finding 2: checking design/ (or the repository) must require every baseline too.
        real = json.loads((ci.INVENTORY / ci.SOURCES).read_text(encoding="utf-8"))
        (self.inv / ci.SOURCES).write_text(json.dumps(real), encoding="utf-8")
        self.write("word/ribbon.json", [TAB])
        above = self.inv.parent
        problems = ci.check([str(above)], inventory=self.inv)
        self.assertTrue(any("missing baseline" in p for p in problems), problems[:3])
        self.assertFalse(any("missing baseline" in p for p in ci.check([str(self.inv / "word")], inventory=self.inv)))

    def test_a_malformed_manifest_commit_is_unreadable(self):
        # Audit round 16, finding 4: the commit must be a 40-hex Git id, even when one file is checked alone.
        real = json.loads((ci.INVENTORY / ci.SOURCES).read_text(encoding="utf-8"))
        real["commit"] = "not-a-git-id"
        (self.inv / ci.SOURCES).write_text(json.dumps(real), encoding="utf-8")
        named = self.write("word/ribbon.json", [TAB])
        with self.assertRaises(ci.Unreadable):
            ci.check([str(named)], inventory=self.inv)

    def test_identifier_fields_hold_no_colon(self):
        # Audit round 15, finding 1: a scheme with no slashes (https:localhost) resolves too; identifiers take no colon.
        for field in ("id", "uiaId", "idMso", "parent", "target", "captureProfile", "capturedFrom"):
            for text in ("https:localhost", "x：y"):
                self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, **{field: text})])
                self.assertTrue(any(f".{field}" in p and "colon" in p for p in self.problems()), (field, ascii(text)))

    def test_long_keys_do_not_amplify_the_report(self):
        # Audit round 15, finding 2: a 4000-character key over 400 links made 1.6 million diagnostic characters.
        rec = dict(TAB)
        rec["x" * 4000] = ["//x"] * 400
        self.write("word/ribbon.json", [rec])
        problems = self.problems()
        self.assertLess(sum(len(p) for p in problems), 20000)
        self.assertTrue(any("and 380 more links in this record" in p for p in problems), problems[-2:])

    def test_a_boolean_is_not_an_integer(self):
        # Audit round 15, finding 3: true is not an order, though Python counts bool as int.
        for value in (True, False):
            self.write("word/ribbon.json", [dict(TAB, order=value)])
            self.assertTrue(any(".order: expected integer" in p for p in self.problems()), value)

    def test_an_uncompressed_ipv6_address_is_refused(self):
        # Audit round 15, finding 3: the full eight-group form, with no ::.
        self.write("word/ribbon.json", [dict(TAB, label="2001:4860:4860:0000:0000:0000:0000:8888")])
        self.assertTrue(any("host name or address" in p for p in self.problems()))

    def test_noncanonical_links_are_refused(self):
        # Audit round 14, finding 1: backslash network paths and single-slash schemes still resolve to addresses.
        for field, text in (("label", "\\\\localhost\\help"), ("uiaId", "https:/localhost/help"),
                            ("uiaId", "\\\\server\\share"), ("idMso", "file:\\c")):
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, **{field: text})])
            self.assertTrue(any(f".{field}" in p and "link" in p for p in self.problems()), (field, text))
        # Sources keep their colon, which no slash follows.
        self.write("word/ribbon.json", [TAB, GROUP, BOLD])
        self.assertEqual(self.problems(), [])

    def test_ambiguous_reference_diagnostics_are_bounded(self):
        # Audit round 14, finding 2: 400 copies of a parent named by 400 children made 10 million characters.
        children = [dict(GROUP, id=f"word.home.g{i}") for i in range(400)]
        self.write("word/ribbon.json", [dict(TAB)] * 400 + children)
        problems = [p for p in self.problems() if "is ambiguous" in p]
        self.assertEqual(len(problems), 400)
        self.assertLess(max(len(p) for p in problems), 600)
        self.assertTrue(problems[0].endswith("and 395 more"), problems[0][-40:])

    def test_a_chain_into_a_loop_in_another_file_is_reported(self):
        # Audit round 14, finding 3: a named file whose child leads into a two-record cycle defined elsewhere.
        a = {"id": "word.a", "app": "word", "kind": "group", "label": "A", "parent": "word.b"}
        b = {"id": "word.b", "app": "word", "kind": "group", "label": "B", "parent": "word.a"}
        child = {"id": "word.c", "app": "word", "kind": "group", "label": "C", "parent": "word.a"}
        # The cycle's file sorts first, so its ids are settled before the child is walked: the child's answer must
        # come from the known loop, not from finding the cycle again.
        self.write("word/a-cycle.json", [a, b])
        named = self.write("word/z-child.json", [child])
        problems = self.problems(named)
        self.assertTrue(any("word.c -> word.a -> word.b -> word.a" in p for p in problems), problems)

    def test_ipv4_shorthand_in_text_is_refused(self):
        # Audit round 13, finding 1: three dotted numbers is an address too (127.0.1 is 127.0.0.1 to a resolver).
        for text in ("Visit 127.0.1", "10.1.1 or 192.168.1.1"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name or address" in p for p in self.problems()), text)
        self.write("word/ribbon.json", [dict(TAB, label="1.5")])  # a decimal, as in Word's line spacing
        self.assertEqual(self.problems(), [])

    def test_duplicate_id_diagnostics_are_bounded(self):
        # Audit round 13, finding 2: 800 copies of one id produced 43 million characters of diagnostics.
        self.write("word/ribbon.json", [dict(TAB)] * 800)
        problems = [p for p in self.problems() if "duplicate id" in p]
        self.assertEqual(len(problems), 800)
        self.assertLess(max(len(p) for p in problems), 600)
        self.assertTrue(problems[0].endswith("and 794 more)"), problems[0][-40:])

    def test_the_file_and_record_types_hold(self):
        # Audit round 13, finding 3: a file is an array of objects, so {} and [null] are refused.
        for data in ({}, [None], [1], "x"):
            path = self.inv / "word" / "ribbon.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertTrue(any("expected" in p for p in self.problems()), repr(data))

    def test_every_string_field_has_its_length_limit(self):
        # Audit round 12, finding 2: each field below must refuse one character over its limit, written out here.
        limits = {"id": 200, "label": 200, "parent": 200, "keytip": 16, "shortcut": 64, "target": 200, "menuPath": 500,
                  "captureProfile": 64, "behaviour": 1000, "idMso": 200, "uiaId": 200, "source": 100,
                  "capturedFrom": 64, "condition": 200, "dispositionReason": 500}
        for field, limit in limits.items():
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, **{field: "a" * (limit + 1)})])
            self.assertTrue(any(f".{field}: longer than {limit}" in p for p in self.problems()), field)

    def test_many_malformed_records_cost_linear_time(self):
        # Audit round 12, finding 1: 8000 records each missing a label took 14 seconds when every record rebuilt the
        # set of reported locations.
        import time
        self.write("word/ribbon.json", [{"id": f"word.r{i}", "app": "word", "kind": "tab"} for i in range(8000)])
        start = time.perf_counter()
        problems = self.problems()
        self.assertLess(time.perf_counter() - start, 4.0)
        self.assertEqual(sum("missing label" in p for p in problems), 8000)

    def test_parent_loops_cost_linear_time(self):
        # Audit round 11, finding 4: a 20000-record chain or cycle is resolved in one pass.
        import time
        for parents in ({f"n{i}": f"n{i + 1}" for i in range(20000)},
                        {**{f"n{i}": f"n{i + 1}" for i in range(20000)}, "n20000": "n0"}):
            start = time.perf_counter()
            ci.parent_loops(parents)
            self.assertLess(time.perf_counter() - start, 2.0)

    def test_every_bounds_member_is_an_integer(self):
        # Audit round 11, finding 5: each bounds member below must refuse a non-integer on its own, written out here.
        for member in ("x", "y", "width", "height"):
            rec = json.loads(json.dumps(BOLD))
            rec["bounds"][member] = "not pixels"
            self.write("word/ribbon.json", [TAB, GROUP, rec])
            self.assertTrue(any(f"bounds.{member}: expected integer" in p for p in self.problems()), member)

    def test_a_network_path_is_refused(self):
        # Audit round 10, finding 1: // followed by a host is a link with no scheme and no dot.
        for field, text in (("label", "//localhost/help"), ("behaviour", "See //intranet/docs."), ("uiaId", "//x")):
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, **{field: text})])
            self.assertTrue(any(f".{field}" in p and "link" in p for p in self.problems()), field)

    def test_non_json_constants_are_unreadable(self):
        # Audit round 10, finding 2: NaN and Infinity are not JSON, in an inventory file or the manifest.
        for constant in ("NaN", "Infinity", "-Infinity"):
            path = self.inv / "word" / "ribbon.json"
            record = f'{{"id": "word.home", "app": "word", "kind": "tab", "label": "Home", "order": {constant}}}'
            path.write_text(f"[{record}]", encoding="utf-8")
            with self.assertRaises(ci.Unreadable, msg=constant):
                self.problems()

    def test_repeated_member_detection_is_linear(self):
        # Audit round 10, finding 3: a large object decodes in linear time (30000 members took minutes before).
        import time
        text = "{" + ", ".join(f'"field{i}": {i}' for i in range(30000)) + "}"
        start = time.perf_counter()
        json.loads(text, object_pairs_hook=ci.unique_pairs)
        self.assertLess(time.perf_counter() - start, 3.0)

    def test_manifest_blob_ids_are_git_ids(self):
        # Audit round 10, finding 4: every blob is a known workbook name with a 40-hex Git blob id.
        real = json.loads((ci.INVENTORY / ci.SOURCES).read_text(encoding="utf-8"))
        for blob in ({}, None, 123, "https://example.com", "abc"):
            manifest = json.loads(json.dumps(real))
            manifest["blobs"]["wordcontrols.xlsx"] = blob
            (self.inv / ci.SOURCES).write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(ci.Unreadable, msg=repr(blob)):
                ci.check([str(self.inv)], inventory=self.inv)

    def test_every_string_field_refuses_a_control_character(self):
        # Audit round 10, finding 5: each string field below must refuse U+0001 on its own, written out here.
        fields = ("id", "label", "parent", "keytip", "shortcut", "target", "menuPath", "captureProfile", "behaviour",
                  "idMso", "uiaId", "source", "capturedFrom", "condition", "dispositionReason")
        for field in fields:
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, **{field: BOLD.get(field, "x") + "\u0001"})])
            # D02 T01 §27: the rule's own word, so a field's pattern that also refuses U+0001 cannot stand in for it.
            self.assertTrue(any(f".{field}: control character" in p for p in self.problems()), field)

    def test_a_baseline_source_names_the_pinned_baseline(self):
        # Audit round 9, finding 1: baseline: names the commit the manifest pins (a prefix of it), not any hex.
        for bad in ("0" * 40, "b230a0e", "deadbeef"):
            self.write("word/ribbon.json", [TAB, dict(PASTE, source=f"baseline:{bad}")])
            self.assertTrue(any("is not the pinned baseline" in p for p in self.problems()), bad)
        self.write("word/ribbon.json", [TAB, dict(PASTE, source="baseline:b230a0df45036b2d5e8b49ebf368b3f90ada8d63")])
        self.assertEqual(self.problems(), [])

    def test_diagnostics_escape_control_characters(self):
        # Audit round 9, finding 2: a record's text cannot send control or bidi characters to the terminal.
        path = self.inv / "word" / "ribbon.json"
        path.write_text(json.dumps([dict(TAB, captureProfile="\u001b[2JFORGED\u202e")]), encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ci.main([str(path)])
        self.assertEqual(code, 1)
        self.assertNotIn("\u001b", out.getvalue())
        self.assertNotIn("\u202e", out.getvalue())
        self.assertIn("\\x1b[2JFORGED\\u202e", out.getvalue())

    def test_a_time_is_not_an_ipv6_address(self):
        # Audit round 9, finding 3: three colon-joined groups is a time, not an address.
        for text in ("12:30:45", "Starts at 09:15:00"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertEqual(self.problems(), [], text)

    def test_ipv6_addresses_in_text_are_refused(self):
        # Audit round 8, finding 1: colon-joined hexadecimal groups, :: included.
        for text in ("[2001:4860:4860::8888]", "::1", "fe80::1"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name or address" in p for p in self.problems()), text)
        self.write("word/ribbon.json", [dict(TAB, label="Ratio 1:2")])
        self.assertEqual(self.problems(), [])

    def test_a_file_named_like_the_manifest_elsewhere_is_checked(self):
        # Audit round 8, finding 2: only the manifest at the inventory's root is left out.
        self.write("word/ribbon.json", [TAB])
        self.write("word/baseline-sources.json", [{"label": "https://example.com"}])
        problems = self.problems()
        self.assertTrue(any("baseline-sources.json" in p for p in problems), problems)

    def test_unreadable_diagnostics_do_not_crash_on_unencodable_text(self):
        # Audit round 8, finding 3: an unreadable file's report carries its text too.
        path = self.inv / "word" / "ribbon.json"
        path.write_text('[{"\\ud800": 1, "\\ud800": 2}]', encoding="utf-8")
        err = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
        with contextlib.redirect_stderr(err):
            code = ci.main([str(path)])
        err.flush()
        self.assertEqual(code, 2)
        self.assertIn(b"\\ud800", err.buffer.getvalue())

    def test_patterns_use_ecma_ascii_digits(self):
        # Audit round 8, finding 4: \d in the schema means 0 to 9 only, as in ECMA-262.
        for text in ("1.٥", "1.５"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name or address" in p for p in self.problems()), ascii(text))
        self.assertFalse(ci.ecma(r"\d").search("٥５"))

    def test_every_bounds_member_is_required(self):
        # Audit round 8, finding 5: each member below must be required on its own, written out here.
        for member in ("x", "y", "width", "height"):
            rec = json.loads(json.dumps(BOLD))
            del rec["bounds"][member]
            self.write("word/ribbon.json", [TAB, GROUP, rec])
            self.assertTrue(any(f"bounds: missing {member}" in p for p in self.problems()), member)

    def test_every_base_field_is_required(self):
        # Audit round 7, finding 4: each base field below must be required on its own, written out here.
        for field in ("id", "app", "kind", "label"):
            rec = {k: v for k, v in TAB.items() if k != field}
            self.write("word/ribbon.json", [rec])
            self.assertTrue(any(f"missing {field}" in p for p in self.problems()), field)

    def test_every_numeric_minimum_holds(self):
        # Audit round 6, finding 3: each bounded number below must refuse -1 on its own, written out here.
        for field in ("order", "bounds.width", "bounds.height"):
            rec = json.loads(json.dumps(BOLD))
            if field.startswith("bounds."):
                rec["bounds"][field.split(".", 1)[1]] = -1
            else:
                rec[field] = -1
            self.write("word/ribbon.json", [TAB, GROUP, rec])
            self.assertTrue(any(f".{field}: below 0" in p for p in self.problems()), field)
        schema = ci.load(ci.SCHEMA)  # D02 T01 §27: a menu's item count starts at one
        self.assertEqual(ci.validate([dict(BOLD, itemCount=0)], schema, schema), ["$[0].itemCount: below 1"])
        self.assertEqual(ci.validate([dict(BOLD, itemCount=1)], schema, schema), [])

    def test_every_text_and_reference_field_refuses_a_blank_value(self):
        # Audit round 5, finding 4: each field below must refuse a value of spaces on its own, written out here.
        fields = ("label", "parent", "keytip", "shortcut", "target", "menuPath", "captureProfile", "behaviour",
                  "idMso", "uiaId", "source", "capturedFrom", "id", "condition", "dispositionReason")
        for field in fields:
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, **{field: "  "})])
            self.assertTrue(any(f".{field}" in p or f" {field} " in p or "orphan" in p and field == "parent"
                                for p in self.problems()), field)

    def test_a_malformed_manifest_is_unreadable_not_a_crash(self):
        # Audit round 5, finding 2: the source manifest must be an object with a commit and a blobs object.
        real = ci.INVENTORY
        for manifest in ([1], {"commit": "x", "blobs": None}, {"blobs": {}}, None):
            (self.inv / ci.SOURCES).write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(ci.Unreadable, msg=repr(manifest)):
                ci.check([str(self.inv)], inventory=self.inv)
        (self.inv / ci.SOURCES).write_text((real / ci.SOURCES).read_text(encoding="utf-8"), encoding="utf-8")
        ci.check([str(self.inv)], inventory=self.inv)  # the real manifest still reads

    def test_malformed_outlook_rows_are_a_problem_not_a_crash(self):
        # Audit round 2, finding 2: rows that are not a list reached the whole-inventory window gate.
        real = ci.INVENTORY
        data = json.loads((real / "outlook" / "baseline.json").read_text(encoding="utf-8"))
        data["rows"] = None
        (self.inv / "outlook").mkdir()
        (self.inv / "outlook" / "baseline.json").write_text(json.dumps(data), encoding="utf-8")
        (self.inv / ci.SOURCES).write_text((real / ci.SOURCES).read_text(encoding="utf-8"), encoding="utf-8")
        whole = ci.check([str(self.inv)], inventory=self.inv)
        self.assertTrue(any("outlook" in p and "rows" in p for p in whole), whole[:5])

    def test_a_live_capture_records_a_recorded_build(self):
        # Audit round 2, finding 3: a source stamped with a build needs capturedFrom, and the build must be recorded.
        rec = {k: v for k, v in PASTE.items() if k != "capturedFrom"}
        self.write("word/ribbon.json", [TAB, rec])
        problems = self.problems()
        self.assertTrue(any("source requires capturedFrom" in p or "missing capturedFrom" in p for p in problems))
        self.write("word/ribbon.json", [TAB, dict(PASTE, source="uia:1.2.3.4", capturedFrom="1.2.3.4")])
        problems = self.problems()
        self.assertTrue(any("source build 1.2.3.4 is not a build" in p for p in problems), problems)

    def test_a_target_defined_twice_is_ambiguous(self):
        # Audit finding 7: the ambiguous-target branch had no test of its own.
        sc = {"id": "word.shortcuts.bold", "app": "word", "kind": "shortcut", "label": "Bold", "shortcut": "Ctrl+B",
              "target": "word.home.font.bold"}
        self.write("word/ribbon.json", [TAB, GROUP, BOLD])
        self.write("word/more.json", [dict(BOLD, parent="word.home")])
        self.write("word/shortcuts.json", [sc])
        self.assertTrue(any("target word.home.font.bold is ambiguous" in p for p in self.problems()))

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
            ".scope: 'everywhere' is not one of": dict(BOLD, scope="everywhere"),
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


    # D02 T01 §27, the mutation sweep (docs/reviews/02-interface/inventory-mutation-sweep.md): each test from here to
    # the end of the class holds a rule whose removal no test noticed. Their lists are written out, never read from
    # the schema, so a rule removed from the schema is still asked for here.

    def test_every_string_field_refuses_another_type(self):
        # The type rule's own diagnostic and nothing else: without it a number would reach the field's other rules,
        # which either pass it (they read strings only) or refuse it under another name.
        schema = ci.load(ci.SCHEMA)
        for field in ("id", "parent", "keytip", "shortcut", "condition", "target", "menuPath", "captureProfile",
                      "idMso", "uiaId", "source", "capturedFrom"):
            self.assertEqual(ci.validate([dict(BOLD, **{field: 7})], schema, schema),
                             [f"$[0].{field}: expected string"], field)
        self.assertEqual(ci.validate([dict(BOLD, itemCount="3")], schema, schema),
                         ["$[0].itemCount: expected integer"])

    def test_a_condition_is_text_a_person_reads(self):
        # A shortcut's condition takes the address rule of every field a person reads.
        schema = ci.load(ci.SCHEMA)
        self.assertEqual(ci.validate([dict(BOLD, condition="Only while a table is selected")], schema, schema), [])
        self.assertEqual(ci.validate([dict(BOLD, condition="See a.b for the state")], schema, schema),
                         ["$[0].condition: host name or address"])

    def test_a_record_without_a_kind_owes_no_kind_specific_field(self):
        # What a control or a shortcut owes is asked only of a record that says it is one: a record with no kind is
        # told its kind is missing, not also that it lacks a control type, a source and a chord.
        schema = ci.load(ci.SCHEMA)
        rec = {k: v for k, v in TAB.items() if k != "kind"}
        self.assertEqual(ci.validate([rec], schema, schema), ["$[0]: missing kind"])

    def test_each_link_mark_is_refused_alone(self):
        # Each text holds one mark of a link that no other alternative of the link rule reads.
        schema = ci.load(ci.SCHEMA)
        for text in ("www.internal", "mailto:someone"):
            self.assertIn("$[0].label: link", ci.validate([dict(BOLD, label=text)], schema, schema), text)
        # A scheme and its two slashes are also read by the scheme-and-one-slash alternative, so the rule shows in what
        # the whole-record scan names: the mark as written.
        link = ci.ecma(schema["$defs"]["noLink"]["not"]["pattern"])
        self.assertEqual(ci.links({"extra": "see https://example"}, "$[0]", link),
                         ["$[0].extra: link 'https://' in a record"])

    def test_a_hexadecimal_number_before_a_full_stop_and_a_bare_decimal_point_are_address_marks(self):
        # Each text is refused by one alternative of the address rule alone: a hexadecimal number followed by a full
        # stop (a resolver reads 0x7f.1), and a full stop followed by a digit with no digit before it.
        schema = ci.load(ci.SCHEMA)
        for text in ("Set the mask to 0x1F.", "Scale by .5 of the width"):
            self.assertEqual(ci.validate([dict(BOLD, label=text)], schema, schema),
                             ["$[0].label: host name or address"], text)

    def test_the_whole_inventory_gate_names_a_missing_baseline_and_a_window_without_rows(self):
        real = ci.INVENTORY
        sources = json.loads((real / ci.SOURCES).read_text(encoding="utf-8"))
        data = json.loads((real / "outlook" / "baseline.json").read_text(encoding="utf-8"))
        gone, kept, rows = ci.outlook_windows(sources)[0], set(), []
        for row in data["rows"]:  # one row for each window but the first: enough for the gate, and quick to check
            if row[0] != gone and row[0] not in kept:
                kept.add(row[0])
                rows.append(row)
        data["rows"] = rows
        (self.inv / "outlook").mkdir()
        (self.inv / "outlook" / "baseline.json").write_text(json.dumps(data), encoding="utf-8")
        (self.inv / ci.SOURCES).write_text(json.dumps(sources), encoding="utf-8")
        whole = ci.check([str(self.inv)], inventory=self.inv)
        # Outlook's baseline is there, so a missing one is reported for the app that lacks it, not as a file that
        # cannot be read.
        self.assertIn(f"{self.inv / 'word' / 'baseline.json'}: missing baseline", whole)
        self.assertNotIn(f"{self.inv / 'outlook' / 'baseline.json'}: missing baseline", whole)
        self.assertIn(f"{self.inv / 'outlook' / 'baseline.json'}: no rows for the windows {[gone]}", whole)

    def test_a_manifest_of_the_wrong_shape_is_named_as_such(self):
        # A commit that is not a string is refused as no manifest, before it is compared with the reference's commit.
        (self.inv / ci.REFERENCE).write_text((ci.INVENTORY / ci.REFERENCE).read_text(encoding="utf-8"),
                                             encoding="utf-8")
        (self.inv / ci.SOURCES).write_text(json.dumps({"commit": 7, "blobs": {}}), encoding="utf-8")
        named = self.write("word/ribbon.json", [TAB])
        with self.assertRaises(ci.Unreadable) as raised:
            ci.check([str(named)], inventory=self.inv)
        self.assertIn("not a manifest (an object with a commit string and a blobs object)", str(raised.exception))

    def test_a_number_in_a_window_cell_is_no_window_name(self):
        # A number can be looked up in a set without raising, so only the type rule says it is no window name; without
        # that rule it would be reported as a window the manifest lacks.
        real = ci.INVENTORY
        data = json.loads((real / "outlook" / "baseline.json").read_text(encoding="utf-8"))
        data["rows"] = data["rows"][:2]
        data["rows"][1][0] = 7
        problems = ci.check_baseline(Path("outlook/baseline.json"), data, ci.load(ci.BASELINE_SCHEMA),
                                     ci.load(real / ci.SOURCES))
        self.assertEqual([p.split(": ", 1)[1] for p in problems], ["$.rows[1].window: 7 is not a window name"])

    def test_a_reference_that_pins_two_commits_is_unreadable(self):
        # Two Commit rows are refused even when the first is the manifest's: which one binds the baselines cannot be
        # told, and taking the first would pass.
        text = (ci.INVENTORY / ci.REFERENCE).read_text(encoding="utf-8")
        row = next(line for line in text.splitlines() if line.startswith("| Commit |"))
        (self.inv / ci.SOURCES).write_text((ci.INVENTORY / ci.SOURCES).read_text(encoding="utf-8"), encoding="utf-8")
        named = self.write("word/ribbon.json", [TAB])
        (self.inv / ci.REFERENCE).write_text(text, encoding="utf-8")
        self.assertEqual(ci.check([str(named)], inventory=self.inv), [])  # one row naming the manifest's commit reads
        (self.inv / ci.REFERENCE).write_text(text.replace(row, row + "\n" + row, 1), encoding="utf-8")
        with self.assertRaises(ci.Unreadable) as raised:
            ci.check([str(named)], inventory=self.inv)
        self.assertIn("pins 2 commits, not one", str(raised.exception))

    def test_the_inventory_files_with_rules_of_their_own_take_them(self):
        # check() hands the shell chrome file, and the repository's Word ribbon, Backstage, shortcut and Options files, to their
        # own checks. Those rules have their own tests; here each check is stood in for, and what is held is that it
        # runs for its file in the repository's inventory and not for a file of that name in a scratch inventory.
        from unittest import mock
        for name in (ci.SOURCES, ci.REFERENCE):
            (self.inv / name).write_text((ci.INVENTORY / name).read_text(encoding="utf-8"), encoding="utf-8")
        self.write("shell/chrome.json", [])
        checks = {"ribbon": "check_word_ribbon", "backstage": "check_word_backstage",
                  "shortcuts": "check_word_shortcuts", "options": "check_word_options",
                  "panes": "check_word_panes", "statusbar": "check_word_statusbar"}
        for name in checks:
            self.write(f"word/{name}.json", [])
        with contextlib.ExitStack() as stack:
            for name, function in checks.items():
                stack.enter_context(mock.patch.object(ci, function, return_value=[f"{name}: its own check ran"]))
            scratch = self.problems()
            with mock.patch.object(ci, "INVENTORY", self.inv):
                own = self.problems()
        for name in checks:
            self.assertIn(f"{name}: its own check ran", own)
            self.assertNotIn(f"{name}: its own check ran", scratch)
        chrome = f"{self.inv / 'shell' / 'chrome.json'}: shell chrome inventory holds 0 records"
        self.assertTrue(any(p.startswith(chrome) for p in scratch), scratch[:5])


    # D02 T01 §22: design/inventory/authoring.json names, for each app folder, the section that authors its domain.

    def authoring(self, data):
        path = self.inv / ci.AUTHORING
        path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
        return path

    def test_the_authoring_file_names_a_section_for_every_app_folder(self):
        self.write("word/ribbon.json", [TAB])
        (self.inv / "excel").mkdir()
        path = self.authoring({"word": "D03 T01 §19", "excel": "D03 T01 §20"})
        self.assertEqual(self.problems(), [])  # two app folders, each with a section the TODO tree holds
        cases = {
            f"{path}: no section named for the app folder excel": {"word": "D03 T01 §19"},
            f"{path}: 'paint' is not an app folder of the inventory (excel, word)":
                {"word": "D03 T01 §19", "excel": "D03 T01 §20", "paint": "D03 T01 §19"},
            f"{path}: word: 'section 19' is not a section reference (DNN TNN §N)":
                {"word": "section 19", "excel": "D03 T01 §20"},
            f"{path}: word: D03 T01 §999 is not a section of the TODO tree":
                {"word": "D03 T01 §999", "excel": "D03 T01 §20"},
            f"{path}: not a JSON object of app folder to section reference": "[]",
        }
        for expected, data in cases.items():
            self.authoring(data)
            self.assertEqual(self.problems(), [expected])
        self.authoring("{not json")
        self.assertTrue(self.problems()[0].startswith(f"{path}: cannot be read ("))
        # The file holds no records: it is never read as an inventory file, and a check of one file does not read it.
        self.authoring("[]")
        self.assertEqual(self.problems(self.inv / "word" / "ribbon.json"), [])
        self.assertEqual(self.problems(self.inv / "word"), [])
        self.assertNotIn(path.resolve(), [f.resolve() for f in ci.inventory_files([self.inv], self.inv / ci.SOURCES)])
        nested = self.write("word/authoring.json", {"word": "D03 T01 §19"})  # of that name elsewhere: a record file
        self.assertTrue(any(str(nested) in p and "expected array" in p for p in self.problems()))

    def test_the_repositorys_inventory_must_have_its_authoring_file(self):
        from unittest import mock
        self.write("word/ribbon.json", [TAB])
        self.assertEqual(self.problems(), [])  # a scratch inventory names no authoring sections
        for name in (ci.SOURCES, ci.REFERENCE):
            (self.inv / name).write_text((ci.INVENTORY / name).read_text(encoding="utf-8"), encoding="utf-8")
        missing = f"{self.inv / ci.AUTHORING}: missing: it names, for each app folder, the section that authors that " \
                  f"app's domain"
        with mock.patch.object(ci, "INVENTORY", self.inv):
            self.assertIn(missing, self.problems())
            self.authoring({"word": "D03 T01 §19"})
            self.assertFalse(any(ci.AUTHORING in p for p in self.problems()))
        self.assertTrue((ci.INVENTORY / ci.AUTHORING).is_file())  # and the repository's own has one

    def test_a_todo_tree_that_cannot_be_read_is_unreadable_not_a_missing_section(self):
        import sys
        from unittest import mock
        sys.path.insert(0, str(SCRIPTS / "lib"))
        import todo_graph
        self.write("word/ribbon.json", [TAB])
        self.authoring({"word": "D03 T01 §19"})
        with mock.patch.object(todo_graph, "section_exists", side_effect=todo_graph.Refused("two files for one number")):
            with self.assertRaises(ci.Unreadable) as raised:
                self.problems()
        self.assertIn("the TODO tree cannot be read (two files for one number)", str(raised.exception))


    # D02 T01 §28: what we do with a record (owner decision 6).

    def test_a_disposition_says_what_we_do_with_a_record(self):
        schema = ci.load(ci.SCHEMA)
        reason = "Depends on a Microsoft cloud dictation service; Windows speech replaces it."

        def problems(**fields):
            return ci.validate([dict(TAB, **fields)], schema, schema)
        for accepted in ({}, {"disposition": "build"}, {"disposition": "equivalent", "dispositionReason": reason},
                         {"disposition": "excluded", "dispositionReason": reason},
                         {"disposition": "excluded", "dispositionReason": "a" * 500}):
            self.assertEqual(problems(**accepted), [], accepted)
        refused = (
            ({"disposition": "unknown"}, ["$[0].disposition: 'unknown' is not one of the allowed values"]),
            ({"disposition": 7}, ["$[0].disposition: 7 is not one of the allowed values"]),
            ({"disposition": "equivalent"}, ["$[0]: missing dispositionReason"]),
            ({"disposition": "excluded"}, ["$[0]: missing dispositionReason"]),
            ({"dispositionReason": reason}, ["$[0]: dispositionReason requires disposition"]),
            ({"disposition": "build", "dispositionReason": reason},
             ["$[0]: a dispositionReason on a record that is built as captured"]),
            ({"disposition": "excluded", "dispositionReason": 7}, ["$[0].dispositionReason: expected string"]),
            ({"disposition": "excluded", "dispositionReason": ""},
             ["$[0].dispositionReason: empty", "$[0].dispositionReason: '' does not match ^\\s*\\S"]),
            ({"disposition": "excluded", "dispositionReason": "   "},
             ["$[0].dispositionReason: '   ' does not match ^\\s*\\S"]),
            ({"disposition": "excluded", "dispositionReason": "Uses a.b for it"},
             ["$[0].dispositionReason: host name or address"]),
            ({"disposition": "excluded", "dispositionReason": "No equivalent" + chr(1)},
             ["$[0].dispositionReason: control character (or an invisible one)"]),
            ({"disposition": "excluded", "dispositionReason": "a" * 501},
             ["$[0].dispositionReason: longer than 500 characters"]),
        )
        for fields, expected in refused:
            self.assertEqual(problems(**fields), expected, fields)
        self.assertIn("$[0].dispositionReason: link",
                      problems(disposition="excluded", dispositionReason="See mailto:someone for it"))
        # And through the checker, on a file: an unknown disposition fails, a reasoned exclusion passes.
        self.write("word/ribbon.json", [dict(TAB, disposition="unknown")])
        self.assertTrue(any("disposition: 'unknown' is not one of the allowed values" in p for p in self.problems()))
        self.write("word/ribbon.json", [dict(TAB, disposition="excluded", dispositionReason=reason)])
        self.assertEqual(self.problems(), [])

    def test_the_reference_says_who_sets_a_disposition(self):
        text = (ci.INVENTORY / ci.REFERENCE).read_text(encoding="utf-8")
        section = text.split("\n## Disposition\n", 1)[1].split("\n## ", 1)[0]
        for said in ("decision 6", "`build`", "`equivalent`", "`excluded`", "`dispositionReason`", "D03 T01 §14",
                     "D03 T01 §20 to §24", "a recapture carries both fields over"):
            self.assertIn(said, section)
        self.assertNotIn("only D03 T01 §14", section.replace("Only", "only"))


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

    def test_the_program_reports_an_unfinished_call_an_orphan_and_a_missing_target(self):
        # D02 T01 §27 (mutation sweep): each of these three rules stands before a lookup that raises without it, so a
        # test inside this process only errors when the rule is removed. Run as a program, the checker either prints
        # the rule's line or it does not.
        import sys
        sys.path.insert(0, str(SCRIPTS / "lib"))
        import process_tree
        deep = "=1-REGISTER.ID(" + "SUM(" * 20 + "1" + ")" * 19 + " help desk"  # closed one level short of its end
        records = [
            {"id": "word.sweepprobe", "app": "word", "kind": "tab", "label": "Probe", "behaviour": deep},
            {"id": "word.sweepprobe.orphan", "app": "word", "kind": "group", "label": "Orphan",
             "parent": "word.sweepprobe.nobody"},
            {"id": "word.sweepprobe.pointer", "app": "word", "kind": "group", "label": "Pointer",
             "parent": "word.sweepprobe", "target": "word.sweepprobe.nothing"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "capture.json"
            path.write_text(json.dumps(records), encoding="utf-8")
            out = Path(tmp) / "out.txt"
            outcome = process_tree.run([sys.executable, "-B", str(SCRIPTS / "check-inventory.py"), str(path)],
                                       cwd=str(SCRIPTS.parent), stdout_path=str(out), stderr_path=str(out),
                                       timeout=300, max_bytes=1024 * 1024)
            text = out.read_text(encoding="utf-8", errors="replace")
        self.assertEqual((outcome.stopped, outcome.exit), (None, 1), text[-2000:])
        lines = text.splitlines()
        self.assertEqual(len(lines), 3, text[-2000:])
        self.assertTrue(lines[0].endswith("capture.json: $[0].behaviour: host name or address (the call "
                                          "1-REGISTER.ID( is not completed)"), lines[0])
        self.assertTrue(lines[1].endswith("capture.json[1]: orphan, parent word.sweepprobe.nobody names no record"),
                        lines[1])
        self.assertTrue(lines[2].endswith("capture.json[2]: target word.sweepprobe.nothing names no record"),
                        lines[2])


class OptionsRules(unittest.TestCase):
    """What Word's Options inventory asked of the schema (D02 T01 §31): Markdown's file pattern, and `enabled`."""

    def test_markdown_is_a_file_name_only_as_its_pattern(self):
        schema = json.loads((Path(__file__).resolve().parents[2] / ci.SCHEMA).read_text(encoding="utf-8"))

        def problems(label):
            return ci.validate([dict(BOLD, label=label)], schema, schema)
        for label in ("Markdown (*.md)", "Markdown (*.MD)", "Saves as *.md", "Markdown (*.md, *.docx)"):
            self.assertEqual(problems(label), [], label)
        for label in ("contoso.md", "Notes.md", "a.md", "See contoso.md", "*.example.md", "*.mda", "*.mdx",
                      "*.md.docx", "x.*.md", "Opens .md files", "(.md)", "**.example.md"):
            self.assertTrue(problems(label), label)

    def test_enabled_is_false_and_on_a_setting_or_a_choice_only(self):
        # D02 T01 §31: a control of a dialog that was disabled when it was captured says so; nothing else does.
        schema = json.loads((Path(__file__).resolve().parents[2] / ci.SCHEMA).read_text(encoding="utf-8"))
        setting = {"id": "word.options.general.show-all", "app": "word", "kind": "setting", "label": "Show all",
                   "parent": "word.options.general", "order": 0, "controlType": "checkBox"}
        choice = dict(setting, id=setting["id"] + ".never", kind="menuItem", label="Never", parent=setting["id"])
        choice.pop("controlType")

        def problems(record, **fields):
            return ci.validate([dict(record, **fields)], schema, schema)
        for record in (setting, choice, BOLD, TAB, GROUP):  # a record that does not say is whatever its kind
            self.assertEqual(problems(record), [], record["id"])
        self.assertEqual(problems(setting, enabled=False), [])
        self.assertEqual(problems(choice, enabled=False), [])
        for value in (True, "false", 0, None):
            self.assertTrue(problems(setting, enabled=value), repr(value))
        for record in (BOLD, TAB, GROUP):
            self.assertTrue(problems(record, enabled=False), record["id"])

    def test_a_pane_says_where_it_docks_and_what_opens_it_and_nothing_else_does(self):
        # D02 T01 §32: `dock` and `openedBy` are a pane's; a tab of a pane is a control type.
        schema = json.loads((Path(__file__).resolve().parents[2] / ci.SCHEMA).read_text(encoding="utf-8"))
        pane = {"id": "word.panes.navigation", "app": "word", "kind": "pane", "label": "Navigation", "order": 0,
                "dock": "left", "openedBy": "word.view.show.navigation-pane"}
        tab = dict(BOLD, id="word.panes.navigation.headings", parent="word.panes.navigation", label="Headings",
                   controlType="tab")
        for key in ("size", "shortcut", "idMso", "keytip"):
            tab.pop(key, None)

        def problems(record, **fields):
            return ci.validate([dict(record, **fields)], schema, schema)
        for record in (pane, tab, BOLD, TAB, GROUP):
            self.assertEqual(problems(record), [], record["id"])
        for dock in ("left", "right", "top", "bottom", "floating"):
            self.assertEqual(problems(pane, dock=dock), [], dock)
        for dock in ("middle", "Left", "", 1, None):
            self.assertTrue(problems(pane, dock=dock), repr(dock))
        for opener in ("", 7, None, "x" * 201, "word.home:styles", "see http://x.example", "word.home" + chr(1)):
            self.assertTrue(problems(pane, openedBy=opener), repr(opener))
        # D02 T01 §33: a tick is an item of a menu's, and it is true or false.
        item = {"id": "word.statusbar.customize.section", "app": "word", "kind": "menuItem", "label": "Section",
                "parent": "word.statusbar.customize", "order": 1}
        self.assertEqual(problems(item), [])
        for value in (True, False):
            self.assertEqual(problems(item, checked=value), [], value)
        for value in (0, 1, "true", None, [True]):
            self.assertEqual(problems(item, checked=value), ["$[0].checked: expected boolean"], repr(value))
        for record in (pane, tab, BOLD, TAB, GROUP):
            self.assertTrue(problems(record, checked=True), record["id"])
        for value in (7, None, ["word.home"]):  # an id is text, and the schema says so in those words
            self.assertEqual(problems(pane, openedBy=value), ["$[0].openedBy: expected string"], repr(value))
        for record in (BOLD, TAB, GROUP):  # each field on its own belongs to a pane
            self.assertTrue(problems(record, dock="left"), record["id"])
            self.assertTrue(problems(record, openedBy="word.view.show.navigation-pane"), record["id"])


if __name__ == "__main__":
    unittest.main()
