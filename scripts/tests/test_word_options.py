# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/word_options.py: the rules of Word's Options inventory, and the checker's use of them (D02 T01 §31)."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import word_options as wo  # noqa: E402  (scripts/lib is put on the path just above)

spec = importlib.util.spec_from_file_location("check_inventory_for_options", SCRIPTS / "check-inventory.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

SOURCE = {"source": "uia:16.0.20527.20150", "capturedFrom": "16.0.20527.20150"}


def rec(rid, kind, label, parent=None, order=0, **extra):
    record = {"id": rid, "app": "word", "kind": kind, "label": label, "order": order, **SOURCE, **extra}
    if parent:
        record["parent"] = parent
    return record


def inventory():
    """A whole Options inventory in small: two categories; a heading with a check box, a list of two fixed choices,
    a list of this PC's data and a disabled list; a list box; and the dialog's two buttons."""
    g = "word.options.general"
    ui = g + ".user-interface-options"
    return [
        rec("word.options", "dialog", "Word Options", itemCount=2),
        rec(g, "dialogTab", "General", "word.options", 0, itemCount=5),
        rec(ui, "group", "User Interface options", g, 0),
        rec(ui + ".show-mini-toolbar", "setting", "Show Mini Toolbar", ui, 0, controlType="checkBox"),
        rec(ui + ".screentip-style", "setting", "ScreenTip style", ui, 1, controlType="dropdown", itemCount=2),
        rec(ui + ".screentip-style.show", "menuItem", "Show", ui + ".screentip-style", 0),
        rec(ui + ".screentip-style.hide", "menuItem", "Hide", ui + ".screentip-style", 1, enabled=False),
        rec(ui + ".default-tray", "setting", "Default tray", ui, 2, controlType="dropdown"),
        rec(ui + ".sound-level", "setting", "Sound level", ui, 3, controlType="dropdown", enabled=False),
        rec("word.options.language", "dialogTab", "Language", "word.options", 1, itemCount=1),
        rec("word.options.language.display-language", "setting", "Display Language", "word.options.language", 0,
            controlType="listBox"),
        rec("word.options.ok", "control", "OK", "word.options", 2, controlType="button"),
        rec("word.options.cancel", "control", "Cancel", "word.options", 3, controlType="button"),
    ]


class Rules(unittest.TestCase):
    def refused(self, records, *said):
        with self.assertRaises(wo.Invalid) as ctx:
            wo.validate(records)
        for text in said:
            self.assertIn(text, str(ctx.exception))

    def without(self, *ids):
        return [r for r in inventory() if r["id"] not in ids]

    def changed(self, rid, **fields):
        records = inventory()
        target = next(r for r in records if r["id"] == rid)
        for key, value in fields.items():
            if value is None:
                target.pop(key, None)
            else:
                target[key] = value
        return records

    def test_a_whole_inventory_passes(self):
        self.assertIsNone(wo.validate(inventory()))

    def test_a_lost_category_setting_or_choice_fails(self):
        lang = [r["id"] for r in inventory() if r["id"].startswith("word.options.language")]
        self.refused(self.without(*lang), "word.options: holds 1 of the 2 categories the capture recorded")
        ui = "word.options.general.user-interface-options"
        self.refused(self.without(ui + ".show-mini-toolbar"),
                     "word.options.general: holds 4 of the 5 headings and controls the capture recorded")
        self.refused(self.without(ui + ".screentip-style.hide"),
                     ui + ".screentip-style: holds 1 of the 2 choices the capture recorded")
        self.refused(self.changed("word.options", itemCount=None), "word.options: no itemCount, so a lost category")
        self.refused(self.changed("word.options.language", itemCount=None), "so a lost heading or control goes unseen")
        self.refused(self.changed("word.options.general", itemCount=True), "no itemCount")
        self.refused(self.without("word.options.language.display-language"),
                     "word.options.language: the category holds no setting")

    def test_a_list_holds_its_choices_and_a_list_of_this_pcs_data_holds_none(self):
        ui = "word.options.general.user-interface-options"
        # A fixed list recorded without its choices.
        self.refused([r for r in self.changed(ui + ".screentip-style", itemCount=None)
                      if r.get("parent") != ui + ".screentip-style"],
                     "ScreenTip style opens to choices, and none is recorded")
        # A list of this PC's data, and a disabled list, recorded with choices.
        for rid in (ui + ".default-tray", ui + ".sound-level"):
            records = self.changed(rid, itemCount=1) + [rec(rid + ".one", "menuItem", "One", rid)]
            self.refused(records, "is recorded without choices")
        # The Quick Access Toolbar's list of commands sources lists this PC's tabs; Customize Ribbon's does not.
        self.assertTrue(wo.environment("word.options.quick-access-toolbar.choose-commands-from",
                                       "Choose commands from"))
        self.assertFalse(wo.environment("word.options.customize-ribbon.choose-commands-from",
                                        "Choose commands from"))
        self.assertTrue(wo.environment("word.options.advanced.print.default-tray", "Default tray"))
        # A list box never has entries under it.
        rid = "word.options.language.display-language"
        self.refused(inventory() + [rec(rid + ".english", "menuItem", "English", rid)],
                     "a listBox has no choices, and 1 are recorded under it")

    def test_enabled_is_false_on_a_setting_or_a_choice_and_nothing_else(self):
        ui = "word.options.general.user-interface-options"
        self.refused(self.changed(ui + ".show-mini-toolbar", enabled=True), "`enabled` is written only as false")
        self.refused(self.changed(ui, enabled=False), "`enabled` is written only as false")
        self.refused(self.changed("word.options.ok", enabled=False), "`enabled` is written only as false")

    def test_the_shape_of_the_file_is_held(self):
        ui = "word.options.general.user-interface-options"
        self.refused(self.without("word.options"), "the dialog record word.options is missing")
        self.refused(inventory() + [copy.deepcopy(inventory()[3])], "duplicate record id")
        self.refused(self.changed(ui + ".show-mini-toolbar", parent="word.options.nowhere"),
                     "its parent word.options.nowhere is not in the file")
        self.refused(self.changed(ui + ".show-mini-toolbar", app="excel"), "app must be 'word'")
        self.refused(self.changed(ui + ".show-mini-toolbar", controlType=None), "a setting has a controlType")
        self.refused(inventory() + [rec("word.backstage.stray", "control", "Stray", "word.options",
                                        controlType="button")], "an Options record's id starts with word.options")
        self.refused(inventory() + [rec("word.options.stray", "setting", "Stray", "word.options",
                                        controlType="checkBox")], "only a category or one of the dialog's own buttons")
        self.refused(self.changed(ui + ".show-mini-toolbar", label="someone@example.org"),
                     "an e-mail address is the owner's data")
        self.refused(self.changed(ui + ".show-mini-toolbar", label="Adobe PDF options"), "a third-party entry")
        self.refused([{"app": "word"}], "an Options record has no id")

    def test_only_the_names_of_changed_options_are_reported(self):
        before = {"SaveInterval": 10, "Overtype": 0, "CreateBackup": 1}
        self.assertEqual(wo.changed(before, dict(before)), [])
        self.assertEqual(wo.changed(before, dict(before, SaveInterval=7, Overtype=1)), ["Overtype", "SaveInterval"])
        self.assertEqual(wo.changed(before, {"SaveInterval": 10, "Overtype": 0}), ["CreateBackup"])
        self.assertEqual(wo.changed({"Overtype": 0}, {"Overtype": False}), [])  # the same value

    def test_a_caption_is_told_from_a_sentence(self):
        self.assertFalse(wo.is_prose("Keyboard shortcuts"))
        self.assertTrue(wo.is_prose("General options for working with Word."))
        self.assertTrue(wo.is_prose("x" * 81))
        self.assertEqual(wo.clean("  Preserve fidelity when sharing this document: "),
                         "Preserve fidelity when sharing this document")
        self.assertEqual(wo.category_id("Quick Access Toolbar"), "word.options.quick-access-toolbar")
        self.assertEqual(len(wo.SAMPLE), 16)
        self.assertFalse([name for name in wo.SAMPLE if "Path" in name or "Name" in name])


class Checker(unittest.TestCase):
    def test_the_checker_runs_the_rules_on_the_options_file_only(self):
        self.assertTrue(ci.is_word_options(ci.INVENTORY / "word" / "options.json"))
        self.assertFalse(ci.is_word_options(ci.INVENTORY / "word" / "backstage.json"))
        self.assertFalse(ci.is_word_options(ci.INVENTORY / "excel" / "options.json"))
        self.assertEqual(ci.check_word_options("options.json", inventory()), [])
        broken = [r for r in inventory() if not r["id"].startswith("word.options.language")]
        problems = ci.check_word_options("options.json", broken)
        self.assertEqual(len(problems), 1)
        self.assertIn("options.json: word.options: holds 1 of the 2 categories", problems[0])

    def test_the_schema_takes_enabled_false_on_a_setting_or_a_choice_only(self):
        schema = json.loads((ci.INVENTORY / "schema.json").read_text(encoding="utf-8"))
        ui = "word.options.general.user-interface-options"

        def problems(rid, **fields):
            record = dict(next(r for r in inventory() if r["id"] == rid), **fields)
            return ci.validate([record], schema, schema)
        self.assertEqual(ci.validate(inventory(), schema, schema), [])
        self.assertEqual(problems(ui + ".sound-level"), [])
        self.assertEqual(problems(ui + ".screentip-style.hide"), [])
        self.assertTrue(problems(ui + ".sound-level", enabled=True))
        self.assertTrue(problems(ui + ".sound-level", enabled="no"))
        self.assertTrue(problems(ui, enabled=False))
        self.assertTrue(problems("word.options.ok", enabled=False))

    def test_the_committed_options_inventory_is_whole_and_holds_no_data(self):
        path = ci.INVENTORY / "word" / "options.json"
        records = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsNone(wo.validate(records))
        tabs = [r for r in records if r["kind"] == "dialogTab"]
        self.assertGreaterEqual(len(tabs), 10)
        for tab in tabs:
            self.assertTrue(any(r["kind"] == "setting" and r["id"].startswith(tab["id"] + ".") for r in records))
        text = path.read_text(encoding="utf-8")
        for data in ("\\\\", "Document1", "@"):
            self.assertNotIn(data, text)


if __name__ == "__main__":
    unittest.main()
