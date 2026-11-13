# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/word_statusbar.py: the rules of Word's status bar inventory, and the checker's use of them
(D02 T01 §33)."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import word_statusbar as sb  # noqa: E402  (scripts/lib is put on the path just above)

spec = importlib.util.spec_from_file_location("check_inventory_for_statusbar", SCRIPTS / "check-inventory.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

SOURCE = {"source": "uia:16.0.20527.20150", "capturedFrom": "16.0.20527.20150"}


def rec(rid, kind, label, parent=None, order=0, **extra):
    record = {"id": rid, "app": "word", "kind": kind, "label": label, "order": order, **SOURCE, **extra}
    if parent:
        record["parent"] = parent
    return record


def inventory():
    """A whole status bar inventory, built from the two hand-written lists."""
    records = [rec("word.statusbar", "region", "Status Bar"),
               rec("word.statusbar.left", "region", "Left zone", "word.statusbar", 0),
               rec("word.statusbar.right", "region", "Right zone", "word.statusbar", 1)]
    order, used = {"left": 0, "right": 0}, set()
    for label, zone, ctype, _tick in sb.BAR:
        rid = f"word.statusbar.{zone}.{sb.slug(label)}"
        rid = rid if rid not in used else rid + "-2"
        used.add(rid)
        records.append(rec(rid, "statusItem", label, f"word.statusbar.{zone}", order[zone], controlType=ctype,
                           bounds={"x": 4 + 40 * len(used), "y": 1011, "width": 38, "height": 21},
                           captureProfile="fhd-100"))
        order[zone] += 1
    records.append(rec(sb.MENU_ID, "contextMenu", "Customize Status Bar", "word.statusbar", 2,
                       itemCount=len(sb.LABELS)))
    for at, label in enumerate(sb.LABELS):
        records.append(rec(f"{sb.MENU_ID}.{sb.slug(label)}", "menuItem", label, sb.MENU_ID, at, checked=True))
    return records


class Rules(unittest.TestCase):
    def refused(self, records, *said):
        with self.assertRaises(sb.Invalid) as ctx:
            sb.validate(records)
        for text in said:
            self.assertIn(text, str(ctx.exception))

    def changed(self, rid, **fields):
        records = inventory()
        target = next(r for r in records if r["id"] == rid)
        for key, value in fields.items():
            if value is None:
                target.pop(key, None)
            else:
                target[key] = value
        return records

    def test_a_whole_inventory_passes_and_the_lists_are_the_live_ones(self):
        self.assertIsNone(sb.validate(inventory()))
        self.assertEqual((len(sb.MENU), len(sb.LABELS), len(sb.BAR)), (8, 28, 16))
        self.assertEqual(len(set(sb.LABELS)), 28)
        self.assertEqual([entry[1] for entry in sb.BAR], ["left"] * 7 + ["right"] * 9)
        self.assertFalse([entry for entry in sb.BAR if entry[3] is not None and entry[3] not in sb.LABELS])

    def test_the_bars_own_items_are_held_whatever_the_menu_holds(self):
        # One bar record deleted, every menu entry there: the menu does not stand in for the bar.
        records = [r for r in inventory() if r["id"] != "word.statusbar.right.focus"]
        self.assertEqual(sum(1 for r in records if r["kind"] == "menuItem"), 28)
        self.refused(records, "the status bar must show Focus (right, button)")
        # In the other zone, of another type, or out of its place, it is not the item.
        self.refused(self.changed("word.statusbar.left.language", parent="word.statusbar.right", order=9),
                     "the status bar must show Language (left, button)")
        self.refused(self.changed("word.statusbar.left.word-count", controlType="button"),
                     "the status bar must show Word Count (left, label)")
        swapped = self.changed("word.statusbar.left.page-number", order=1)
        next(r for r in swapped if r["id"] == "word.statusbar.left.word-count")["order"] = 0
        self.refused(swapped, "the status bar must show Word Count (left) out of its place")
        # An item is expected by its tick: unticked, it is not expected on the bar; ticked, it is.
        language = f"{sb.MENU_ID}.language"
        hidden = [r for r in self.changed(language, checked=False) if r["id"] != "word.statusbar.left.language"]
        self.assertIsNone(sb.validate(hidden))
        self.refused([r for r in inventory() if r["id"] != "word.statusbar.left.language"],
                     "the status bar must show Language (left, button)")
        views = [r for r in self.changed(f"{sb.MENU_ID}.view-shortcuts", checked=False)
                 if r["label"] not in ("Read Mode", "Print Layout", "Web Layout")]
        self.assertIsNone(sb.validate(views))
        self.assertEqual(len(sb.expected()), 16)
        self.assertEqual(sb.expected({}), [("Display Settings", "right", "button")])  # the one no tick hides
        # Where an item stands is part of it.
        self.refused(self.changed("word.statusbar.left.language", bounds=None),
                     "word.statusbar.left.language: no bounds, so where it stands on the bar is not recorded")
        # An item the list does not name is recorded and allowed.
        extra = inventory() + [rec("word.statusbar.left.spelling-and-grammar-check", "statusItem",
                                   "Spelling and Grammar Check", "word.statusbar.left", 7, controlType="button",
                                   bounds={"x": 620, "y": 1011, "width": 30, "height": 21})]
        self.assertIsNone(sb.validate(extra))
        self.refused(self.changed("word.statusbar.left.language", controlType=None), "has a controlType")
        self.refused(self.changed("word.statusbar.left.language", parent="word.statusbar"),
                     "an item of the bar stands in one of its two zones")

    def test_the_menu_is_the_hand_written_one_in_order_with_every_tick(self):
        gone = f"{sb.MENU_ID}.track-changes"
        self.refused([r for r in self.changed(sb.MENU_ID, itemCount=27) if r["id"] != gone],
                     "the Customize Status Bar menu is not the one scripts/lib/word_statusbar.py lists: it lacks "
                     "Track Changes")
        swapped = self.changed(f"{sb.MENU_ID}.section", order=2)
        next(r for r in swapped if r["id"] == f"{sb.MENU_ID}.page-number")["order"] = 1
        self.refused(swapped, "its items are out of order")
        self.refused(inventory() + [rec(f"{sb.MENU_ID}.dictation", "menuItem", "Dictation", sb.MENU_ID, 28,
                                        checked=True)], "it also holds Dictation", "holds 29 of the 28 items")
        self.refused(self.changed(f"{sb.MENU_ID}.section", checked=None),
                     "word.statusbar.customize.section: no `checked`, so whether the bar shows it is not recorded")
        self.refused(self.changed(f"{sb.MENU_ID}.section", checked="yes"), "`checked` is true or false")
        self.refused(self.changed("word.statusbar.left.language", checked=True),
                     "`checked` is true or false, on an item of the menu")
        self.refused(self.changed(sb.MENU_ID, itemCount=5), "holds 28 of the 5 items the capture recorded")

    def test_the_shape_of_the_file_is_held(self):
        self.refused([r for r in inventory() if r["id"] != "word.statusbar.right" and
                      r.get("parent") != "word.statusbar.right"], "the region word.statusbar.right is not recorded")
        self.refused(self.changed("word.statusbar.left.language", app="excel"), "app must be 'word'")
        self.refused(self.changed("word.statusbar.left.language", label="someone@example.org"), "never a label")
        self.refused(inventory() + [dict(inventory()[4])], "duplicate record id")
        self.refused(inventory() + [rec("word.panes.stray", "statusItem", "Stray", "word.statusbar.left", 9,
                                        controlType="button")], "a status bar record's id starts with word.statusbar")
        self.refused([{"app": "word"}], "a status bar record has no id")

    def test_a_label_is_cut_from_the_one_name_word_gives_an_item(self):
        for name, label in (("Page Number Page 1 of 1", "Page Number"), ("Word Count 0 words", "Word Count"),
                            ("Language English (United States)", "Language"), ("Zoom 100%", "Zoom"), ("Zoom", "Zoom"),
                            ("Zoom Out (Ctrl -)", "Zoom Out"), ("Zoom In (Ctrl +)", "Zoom In"),
                            ("Zoom Slider", "Zoom Slider"), ("Coauthoring Mode ", "Coauthoring Mode"),
                            ("Text Predictions Text Predictions: Off", "Text Predictions"),
                            ("Character Count (with spaces) 0 characters", "Character Count (with spaces)"),
                            ("Accessibility Checker Accessibility: Good to go", "Accessibility Checker")):
            self.assertEqual(sb.label_of(name), (label, True), name)
        self.assertEqual(sb.label_of("Dictation (Alt+`)"), ("Dictation", False))  # no known label: the keys are cut
        self.assertEqual(sb.label_of("Zoom Out (Ctrl -)", sb.LABELS), ("Zoom", True))  # the menu's labels alone
        self.assertEqual(sb.label_of("Zoomed"), ("Zoomed", False))  # a label fits whole words only

    def test_the_widest_gap_divides_the_bar(self):
        self.assertEqual(sb.zones_of([(4, 75), (78, 135), (138, 170), (1441, 1555), (1555, 1617)]),
                         ["left", "left", "left", "right", "right"])
        self.assertEqual(sb.zones_of([(4, 75)]), ["left"])
        self.assertEqual(sb.zones_of([]), [])


class Checker(unittest.TestCase):
    def test_the_checker_runs_the_rules_on_the_status_bar_file_only(self):
        self.assertTrue(ci.is_word_statusbar(ci.INVENTORY / "word" / "statusbar.json"))
        self.assertFalse(ci.is_word_statusbar(ci.INVENTORY / "word" / "panes.json"))
        self.assertFalse(ci.is_word_statusbar(ci.INVENTORY / "excel" / "statusbar.json"))
        self.assertEqual(ci.check_word_statusbar("statusbar.json", inventory()), [])
        broken = [r for r in inventory() if r["id"] != "word.statusbar.right.focus"]
        problems = ci.check_word_statusbar("statusbar.json", broken)
        self.assertEqual(len(problems), 1)
        self.assertIn("statusbar.json: the status bar must show Focus (right, button)", problems[0])

    def test_the_schema_takes_the_status_bars_records(self):
        schema = json.loads((ci.INVENTORY / "schema.json").read_text(encoding="utf-8"))
        self.assertEqual(ci.validate(inventory(), schema, schema), [])

    def test_the_committed_status_bar_inventory_is_whole_and_holds_no_value(self):
        path = ci.INVENTORY / "word" / "statusbar.json"
        records = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsNone(sb.validate(records))
        self.assertEqual(sum(1 for r in records if r["kind"] == "menuItem"), 28)
        text = path.read_text(encoding="utf-8")
        for value in ("1 of 1", "0 words", "English", "100%", "Not Recording", "Good to go", "Ctrl", "Document1"):
            self.assertNotIn(value, text)


if __name__ == "__main__":
    unittest.main()
