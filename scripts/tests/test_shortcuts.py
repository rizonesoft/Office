# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/shortcuts.py and scripts/lib/word_shortcuts.py: how a shortcut writes its keys, the conflict rule,
and the checklist design/inventory/word/shortcuts.json is held to (D02 T01 §17)."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import shutil
import tempfile
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
import shortcuts as sc  # noqa: E402  (scripts/lib is put on the path just above)
import word_shortcuts as ws  # noqa: E402

spec = importlib.util.spec_from_file_location("check_inventory", REPO / "scripts" / "check-inventory.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)
COMMITTED = REPO / "design" / "inventory" / "word" / "shortcuts.json"


def rec(rid, chord, scope="document", **extra):
    return {"id": f"word.shortcut.{rid}", "app": "word", "kind": "shortcut", "label": rid, "shortcut": chord,
            "scope": scope, **extra}


class Notation(unittest.TestCase):
    def test_modifier_order_does_not_make_another_chord(self):
        self.assertEqual(sc.canonical("Alt+Ctrl+V"), sc.canonical("Ctrl+Alt+V"))
        self.assertEqual(sc.problems([rec("a", "Alt+Ctrl+V"), rec("b", "Ctrl+Alt+V")]),
                         ["word.shortcut.b: Ctrl+Alt+V in document is already word.shortcut.a's"])

    def test_the_same_chord_in_two_scopes_is_two_bindings(self):
        self.assertEqual(sc.problems([rec("a", "Tab"), rec("b", "Tab", "table"), rec("c", "Tab", "ribbon")]), [])

    def test_a_sequence_is_not_the_chord_of_the_same_keys(self):
        self.assertNotEqual(sc.canonical("Alt, F"), sc.canonical("Alt+F"))
        self.assertEqual(sc.steps("Alt, H, F, O"), tuple((frozenset(), k) for k in ("Alt", "H", "F", "O")))
        self.assertEqual(sc.problems([rec("a", "Alt, F"), rec("b", "Alt+F")]), [])

    def test_plus_and_comma_keys_are_named(self):
        self.assertEqual(sc.steps("Ctrl+Plus"), ((frozenset({"Ctrl"}), "Plus"),))
        self.assertEqual(sc.steps("Ctrl+Shift+Comma"), ((frozenset({"Ctrl", "Shift"}), "Comma"),))
        self.assertEqual(sc.steps("Alt+Ctrl+Num +"), ((frozenset({"Alt", "Ctrl"}), "Num +"),))
        for literal in ("Ctrl++", "Ctrl+Shift+,", ","):
            with self.assertRaises(sc.Malformed):
                sc.steps(literal)
        for bad in ("", "Ctrl+", "Ctrl+Ctrl+B", "Ctrl+ B"):
            with self.assertRaises(sc.Malformed):
                sc.steps(bad)

    def test_each_alternative_of_one_action_is_checked_on_its_own(self):
        alternatives = [rec("copy", "Ctrl+C"), rec("copy-2", "Ctrl+Insert")]
        self.assertEqual(sc.problems(alternatives), [])
        self.assertEqual(sc.problems(alternatives + [rec("other", "Ctrl+Insert")]),
                         ["word.shortcut.other: Ctrl+Insert in document is already word.shortcut.copy-2's"])

    def test_a_field_of_the_wrong_type_is_reported_not_raised(self):
        for field, value in (("scope", []), ("app", ["word"]), ("id", {"a": 1}), ("shortcut", 5)):
            bad = dict(rec("a", "Ctrl+B"), **{field: value})
            out = sc.problems([bad, rec("b", "Ctrl+B")])  # round 1: a list scope raised TypeError
            self.assertTrue(out, field)
            self.assertEqual(sc.conflicts([bad, rec("b", "Ctrl+B")]), [], field)

    def test_a_scope_outside_the_set_is_refused(self):
        self.assertIn("scope 'menu' is not one of", sc.problems([rec("a", "Esc", "menu")])[0])


class Checklist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads(COMMITTED.read_text(encoding="utf-8"))

    def test_the_committed_file_is_on_the_checklist_and_covers_every_row(self):
        self.assertEqual(ws.validate(self.records), [])
        self.assertEqual(sc.problems(self.records), [])
        self.assertGreaterEqual(len(self.records), 255)

    def test_every_row_of_every_table_is_covered(self):
        for name, rows in ws.COVERAGE.items():
            self.assertEqual(len(rows), ws.ROWS[name], name)
            self.assertTrue(all(rows), name)

    def test_a_lost_binding_is_refused_naming_it(self):
        recs = [r for r in self.records if r["id"] != "word.shortcut.bold"]
        self.assertIn("word.shortcut.bold: on the checklist but not in the file", ws.validate(recs))

    def test_a_record_off_the_checklist_is_refused(self):
        recs = self.records + [dict(rec("extra", "Ctrl+Alt+Shift+F12"), behaviour="Does nothing.")]
        self.assertIn("word.shortcut.extra: not on the checklist", "\n".join(ws.validate(recs)))

    def test_a_record_without_scope_or_behaviour_or_with_a_bad_scope_is_refused(self):
        for field, value, want in (("scope", None, "no scope"), ("behaviour", None, "no behaviour"),
                                   ("scope", "menu", "no scope, or one outside the set"),
                                   ("condition", " ", "an empty condition")):
            recs = copy.deepcopy(self.records)
            target = next(r for r in recs if r["id"] == "word.shortcut.bold")
            if value is None:
                del target[field]
            else:
                target[field] = value
            self.assertIn(f"word.shortcut.bold: {want}", "\n".join(ws.validate(recs)), field)

    def test_a_row_left_uncovered_or_a_row_count_changed_is_refused(self):
        saved = copy.deepcopy(ws.COVERAGE)
        try:
            ws.COVERAGE["common"][0] = []
            self.assertIn("row 1 of the checklist's common table is covered by no record", ws.validate(self.records))
            ws.COVERAGE["common"].pop()
            self.assertIn("the checklist's common table holds 25 rows, not its 26", ws.validate(self.records))
        finally:
            ws.COVERAGE.clear()
            ws.COVERAGE.update(saved)

    def test_the_checker_refuses_a_conflict_and_a_checklist_gap_in_the_committed_file(self):
        recs = copy.deepcopy(self.records)
        next(r for r in recs if r["id"] == "word.shortcut.italic")["shortcut"] = "Ctrl+B"
        del next(r for r in recs if r["id"] == "word.shortcut.underline")["behaviour"]
        with tempfile.TemporaryDirectory() as tmp:  # a copy of the inventory, never the committed file
            inventory = Path(tmp) / "inventory"
            shutil.copytree(ci.INVENTORY, inventory)
            (inventory / "word" / "shortcuts.json").write_text(json.dumps(recs), encoding="utf-8")
            with mock.patch.object(ci, "INVENTORY", inventory):
                problems = "\n".join(ci.check([str(inventory / "word" / "shortcuts.json")], inventory=inventory))
        self.assertIn("word.shortcut.italic: Ctrl+B in document is already word.shortcut.bold's", problems)
        self.assertIn("word.shortcut.underline: no behaviour", problems)

    def test_checking_one_file_still_sees_a_conflict_with_another(self):
        with tempfile.TemporaryDirectory() as tmp:  # round 1: only the later record's file reported it
            inventory = Path(tmp) / "inventory"
            shutil.copytree(ci.INVENTORY, inventory)
            ribbon = inventory / "word" / "ribbon.json"
            recs = json.loads(ribbon.read_text(encoding="utf-8"))
            recs.insert(0, {"id": "word.shortcut.incoming", "app": "word", "kind": "shortcut", "label": "Incoming",
                            "shortcut": "Ctrl+B", "scope": "document"})
            ribbon.write_text(json.dumps(recs), encoding="utf-8")
            with mock.patch.object(ci, "INVENTORY", inventory):
                for named in (ribbon, inventory / "word" / "shortcuts.json"):
                    problems = "\n".join(ci.check([str(named)], inventory=inventory))
                    self.assertIn("Ctrl+B in document is already", problems, named.name)

    def test_a_dialog_key_is_its_own_record_not_the_documents(self):
        row = ws.COVERAGE["function-keys"][5]  # F6 and its combinations
        dialog = [r for r in self.records if r["id"] in row and r["scope"] == "dialog"]
        self.assertEqual([r["shortcut"] for r in dialog], ["Alt+F6"])  # round 1: it pointed at Next Window
        self.assertNotIn("target", dialog[0])

    def test_word_key_codes_are_what_findkey_takes(self):
        self.assertEqual(ws.key_code({"Ctrl"}, "B"), 512 | 66)
        self.assertEqual(ws.key_code({"Alt", "Ctrl"}, "V"), 1024 | 512 | 86)
        self.assertEqual(ws.key_code({"Ctrl", "Shift"}, "Comma"), 512 | 256 | 188)
        self.assertIsNone(ws.key_code(set(), "Wheel"))


if __name__ == "__main__":
    unittest.main()
