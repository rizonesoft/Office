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
                  "idMso", "uiaId", "source", "capturedFrom", "id")
        for field in fields:
            rec = dict(BOLD, **{field: ""})
            self.write("word/ribbon.json", [TAB, GROUP, rec])
            self.assertTrue(any(f".{field}" in p for p in self.problems()), field)

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

    def test_unicode_host_names_are_refused(self):
        # Audit round 6, finding 1: host names with the full-stop forms IDNA normalises, and in other scripts.
        for text in ("support。microsoft。com", "office．microsoft．com", "a｡example｡org",
                     "пример.рф", "data：text/plain,hello"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name or address" in p for p in self.problems()), ascii(text))

    def test_any_host_name_or_address_in_text_is_refused_by_its_dots(self):
        # Audit round 7, findings 1 and 3: hosts in any plane and numeric addresses are refused, and padding with a
        # Unicode space after a sentence is not mistaken for a host.
        for text in ("\U00010428.com", "8.8.8.8", "Visit 10.0.0.1 now"):
            self.write("word/ribbon.json", [dict(TAB, label=text)])
            self.assertTrue(any("host name or address" in p for p in self.problems()), ascii(text))
        for text in ("Opens the dialog.\u2002", "Sets 1.5 line spacing.", "Ctrl+Shift+.", "Save As...", "(see Help.)"):
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, behaviour=text)])
            self.assertEqual(self.problems(), [], ascii(text))

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
        # Audit round 11, finding 3: the link and address patterns never search past a field's maxLength.
        import time
        for field in ("label", "behaviour", "uiaId"):
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, **{field: "a" * 40000})])
            start = time.perf_counter()
            problems = self.problems()
            self.assertLess(time.perf_counter() - start, 3.0, field)
            self.assertTrue(any(f".{field}: longer than" in p for p in problems), field)

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
        for field in ("uiaId", "idMso", "parent", "target", "captureProfile", "capturedFrom"):
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
                  "capturedFrom": 64}
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
                  "idMso", "uiaId", "source", "capturedFrom")
        for field in fields:
            self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, **{field: BOLD.get(field, "x") + "\u0001"})])
            self.assertTrue(any(f".{field}" in p for p in self.problems()), field)

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

    def test_every_text_and_reference_field_refuses_a_blank_value(self):
        # Audit round 5, finding 4: each field below must refuse a value of spaces on its own, written out here.
        fields = ("label", "parent", "keytip", "shortcut", "target", "menuPath", "captureProfile", "behaviour",
                  "idMso", "uiaId", "source", "capturedFrom", "id")
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
