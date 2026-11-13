# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/word_panes.py: the rules of Word's task pane inventory, and the checker's use of them (D02 T01 §32)."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import word_panes as wp  # noqa: E402  (scripts/lib is put on the path just above)

spec = importlib.util.spec_from_file_location("check_inventory_for_panes", SCRIPTS / "check-inventory.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

SOURCE = {"source": "uia:16.0.20527.20150", "capturedFrom": "16.0.20527.20150"}
OPENERS = {pane["openedBy"] for pane in wp.PANES}


def rec(rid, kind, label, parent=None, order=0, **extra):
    record = {"id": rid, "app": "word", "kind": kind, "label": label, "order": order, **SOURCE, **extra}
    if parent:
        record["parent"] = parent
    return record


def inventory():
    """A whole panes inventory, built from the hand-written list: each pane where it docks first, with its title
    bar and every control it must show; a menu that opens holds two choices."""
    records = []
    for order, pane in enumerate(wp.PANES):
        rid = wp.pane_id(pane)
        controls = list(wp.CHROME) + list(pane["required"])
        records.append(rec(rid, "pane", pane["title"], order=order, dock=pane["docks"][0], openedBy=pane["openedBy"],
                           bounds={"x": 0, "y": 178, "width": 300, "height": 832}, captureProfile="fhd-100",
                           itemCount=len(controls)))
        for at, (label, ctype) in enumerate(controls):
            cid = f"{rid}.{wp.slug(label)}"
            opens = ctype == "menu" and label not in wp.CLOSED_MENUS
            count = {"itemCount": 2} if opens else {}
            records.append(rec(cid, "control", label, rid, at, controlType=ctype, **count))
            if opens:
                records += [rec(f"{cid}.one", "menuItem", "One", cid, 0),
                            rec(f"{cid}.two", "menuItem", "Two", cid, 1)]
    return records


class Rules(unittest.TestCase):
    def refused(self, records, *said, ribbon=OPENERS):
        with self.assertRaises(wp.Invalid) as ctx:
            wp.validate(records, ribbon)
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

    def test_a_whole_inventory_passes_and_the_list_names_eight_panes(self):
        self.assertIsNone(wp.validate(inventory(), OPENERS))
        self.assertIsNone(wp.validate(inventory()))  # without a ribbon inventory the openers' ids are still held
        self.assertEqual([p["slug"] for p in wp.PANES], [
            "navigation", "styles", "clipboard", "reviewing-vertical", "reviewing-horizontal", "editor", "selection",
            "format-shape"])
        self.assertEqual(len(wp.COMMANDS), 8)
        self.assertEqual([p["slug"] for p in wp.PANES if p.get("shape")], ["format-shape"])

    def test_a_count_the_capture_reports_about_itself_is_not_what_holds_a_pane(self):
        # A required control removed, and the pane's itemCount lowered to match: the count agrees and the pane
        # still lacks what the hand-written list says it must show.
        records = [r for r in self.changed("word.panes.selection", itemCount=6)
                   if r["id"] != "word.panes.selection.hide-all"]
        self.refused(records, "word.panes.selection: the Selection pane must show Hide All (button)")
        self.assertNotIn("holds", str(self.failure(records)))
        # The title bar is held the same way.
        records = [r for r in self.changed("word.panes.editor", itemCount=6)
                   if r["id"] != "word.panes.editor.close-pane"]
        self.refused(records, "word.panes.editor: the Editor pane must show Close pane (button)")
        # Editor is held to the checks the committed file and the reference record of it, each one.
        for label in ("Spelling", "Grammar", "Conciseness", "Document statistics",
                      "Tell us what you think about Editor"):
            rid = f"word.panes.editor.{wp.slug(label)}"
            records = [r for r in self.changed("word.panes.editor", itemCount=6) if r["id"] != rid]
            self.refused(records, f"word.panes.editor: the Editor pane must show {label} (button)")
        # Each required control is counted: one does not stand for two of the same label and type.
        twice = dict(wp.by_slug("selection"), required=wp.by_slug("selection")["required"] + (("Show All", "button"),))
        self.assertEqual(wp.missing(twice, inventory()), ["Show All (button)"])
        # The right label with another type is not the control.
        self.refused(self.changed("word.panes.navigation.search", controlType="button"),
                     "the Navigation pane must show Search (splitButton)")
        # And a count that does not agree fails on its own.
        self.refused(self.changed("word.panes.styles", itemCount=3),
                     "word.panes.styles: holds 9 of the 3 headings and controls the capture recorded")
        self.refused(self.changed("word.panes.styles", itemCount=None), "no itemCount, so a lost control goes unseen")

    def failure(self, records):
        try:
            wp.validate(records, OPENERS)
        except wp.Invalid as exc:
            return exc
        self.fail("the records passed")

    def test_each_reviewing_form_is_its_own_pane_docked_its_own_way(self):
        # One form replaced by a copy of the other: the horizontal pane's records, docked at the side.
        self.refused(self.changed("word.panes.reviewing-horizontal", dock="left"),
                     "word.panes.reviewing-horizontal: docks 'left', and the Revisions pane opened by "
                     "ReviewReviewingPaneHorizontal docks bottom or top")
        self.refused(self.changed("word.panes.reviewing-vertical", dock="bottom"),
                     "ReviewReviewingPaneVertical docks left or right")
        records = [r for r in inventory() if not r["id"].startswith("word.panes.reviewing-horizontal")]
        self.refused(records, "the Revisions pane (word.panes.reviewing-horizontal) is not recorded")
        self.refused(self.changed("word.panes.reviewing-horizontal",
                                  openedBy="word.review.markup.reviewing-pane.reviewing-pane-vertical"),
                     "openedBy is 'word.review.markup.reviewing-pane.reviewing-pane-vertical', not "
                     "word.review.markup.reviewing-pane.reviewing-pane-horizontal")

    def test_a_pane_docks_where_the_list_says_with_its_size_and_its_opener(self):
        self.refused(self.changed("word.panes.navigation", dock="bottom"), "docks 'bottom'", "docks left or right")
        self.refused(self.changed("word.panes.navigation", dock=None), "docks None")
        self.assertIsNone(wp.validate(self.changed("word.panes.styles", dock="right"), OPENERS))  # as it was left
        self.refused(self.changed("word.panes.clipboard", bounds=None), "no bounds, so its width and height")
        self.refused(self.changed("word.panes.clipboard", openedBy=None), "openedBy is None")
        self.refused(inventory(), "its opener word.home.editor.editor is not a record of the ribbon inventory",
                     ribbon=OPENERS - {"word.home.editor.editor"})
        self.refused(inventory() + [rec("word.panes.research", "pane", "Research", dock="right")],
                     "word.panes.research: not one of the panes scripts/lib/word_panes.py lists")

    def test_menus_lists_and_the_shape_of_the_file_are_held(self):
        menu = "word.panes.clipboard.options"
        self.refused([r for r in inventory() if r["id"] != menu + ".two"], f"{menu}: holds 1 of the 2 choices")
        self.refused([r for r in self.changed(menu, itemCount=None) if r.get("parent") != menu],
                     "Options opens to choices, and none is recorded")
        closed = "word.panes.clipboard.task-pane-options"
        self.refused(self.changed(closed, itemCount=1) + [rec(closed + ".move", "menuItem", "Move", closed)],
                     "Task Pane Options is recorded without choices")
        data = "word.panes.styles.styles"
        self.refused(inventory() + [rec(data + ".normal", "menuItem", "Normal", data)],
                     "a list of the owner's data is recorded without entries", "only a menu has choices")
        self.refused(self.changed("word.panes.navigation.search", dock="left"),
                     "`dock` and `openedBy` belong to a pane")
        self.refused(self.changed("word.panes.navigation.search", parent="word.panes.nowhere"),
                     "its parent word.panes.nowhere is not in the file")
        self.refused(self.changed("word.panes.navigation.search", app="excel"), "app must be 'word'")
        self.refused(self.changed("word.panes.navigation.search", label="someone@example.org"), "never a label")
        self.refused(inventory() + [dict(inventory()[1])], "duplicate record id")
        self.refused(self.changed("word.panes.navigation", parent="word.panes.styles"), "a pane has no parent")
        self.refused([{"app": "word"}], "a pane record has no id")

    def test_a_label_is_the_fact_and_a_dock_is_read_from_its_name(self):
        self.assertEqual(wp.clean("Spelling, 0 issues. Press space or enter to review the issues."), "Spelling")
        self.assertEqual(wp.clean("Cut, copy, and paste"), "Cut, copy, and paste")  # a comma alone is not a count
        self.assertEqual(wp.clean(" Options... "), "Options...")
        names = ("MsoDockLeft", "MsoDockRight", "MsoDockBottom", "MsoDockTop", "", "X")
        self.assertEqual([wp.dock_of(n) for n in names], ["left", "right", "bottom", "top", "floating", "floating"])


class Checker(unittest.TestCase):
    def test_the_checker_runs_the_rules_on_the_panes_file_only(self):
        self.assertTrue(ci.is_word_panes(ci.INVENTORY / "word" / "panes.json"))
        self.assertFalse(ci.is_word_panes(ci.INVENTORY / "word" / "options.json"))
        self.assertFalse(ci.is_word_panes(ci.INVENTORY / "excel" / "panes.json"))
        self.assertEqual(ci.check_word_panes("panes.json", inventory()), [])  # each opener is in the real ribbon file
        broken = [r for r in inventory() if not r["id"].startswith("word.panes.editor")]
        problems = ci.check_word_panes("panes.json", broken)
        self.assertEqual(len(problems), 1)
        self.assertIn("panes.json: the Editor pane (word.panes.editor) is not recorded", problems[0])

    def test_the_schema_takes_the_panes_records(self):
        schema = json.loads((ci.INVENTORY / "schema.json").read_text(encoding="utf-8"))
        self.assertEqual(ci.validate(inventory(), schema, schema), [])

    def test_the_committed_panes_inventory_is_whole_and_holds_no_data(self):
        path = ci.INVENTORY / "word" / "panes.json"
        records = json.loads(path.read_text(encoding="utf-8"))
        ribbon = json.loads((ci.INVENTORY / "word" / "ribbon.json").read_text(encoding="utf-8"))
        self.assertIsNone(wp.validate(records, {r["id"] for r in ribbon}))
        self.assertEqual(sum(1 for r in records if r["kind"] == "pane"), 8)
        text = path.read_text(encoding="utf-8")
        for data in ("\\\\", "Document1", "@"):
            self.assertNotIn(data, text)


if __name__ == "__main__":
    unittest.main()
