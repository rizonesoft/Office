# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/word_dialogs.py: the rules of Word's dialog inventory, and the checker's use of them (D02 T01 §34)."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import word_dialogs as wd  # noqa: E402  (scripts/lib is put on the path just above)

spec = importlib.util.spec_from_file_location("check_inventory_for_dialogs", SCRIPTS / "check-inventory.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

SOURCE = {"source": "uia:16.0.20527.20150", "capturedFrom": "16.0.20527.20150"}
OPENERS = {dialog["openedBy"] for dialog in wd.DIALOGS}


def rec(rid, kind, label, parent=None, order=0, **extra):
    record = {"id": rid, "app": "word", "kind": kind, "label": label, "order": order, **SOURCE, **extra}
    if parent:
        record["parent"] = parent
    return record


def inventory():
    """A whole dialogs inventory, built from the hand-written lists: every dialog with its tabs and every control
    the lists require. A list of a newer dialog holds two choices; a list of an old one holds none."""
    records = []
    for order, dialog in enumerate(wd.DIALOGS):
        rid, used, mine = wd.dialog_id(dialog), set(), []
        parts = [(tab, wd.tab_id(dialog, tab)) for tab in dialog["tabs"]] + [("", rid)]
        for at, (tab, part) in enumerate(parts):
            under = []
            for n, entry in enumerate(wd.REQUIRED[dialog["slug"]].get(tab, ())):
                label, ctype, condition = (tuple(entry) + (None,))[:3]
                cid, k = f"{part}.{wd.slug(label)}", 1
                while cid in used:
                    k += 1
                    cid = f"{part}.{wd.slug(label)}-{k}"
                used.add(cid)
                extra = {"condition": condition} if condition else {}
                opens = ctype in ("dropdown", "menu") and not dialog.get("old")
                under.append(rec(cid, "setting", label, part, n, controlType=ctype, **extra,
                                 **({"itemCount": 2} if opens else {})))
                if opens:
                    under += [rec(f"{cid}.one", "menuItem", "One", cid, 0),
                              rec(f"{cid}.two", "menuItem", "Two", cid, 1)]
            if tab:
                mine.append(rec(part, "dialogTab", tab, rid, at,
                                itemCount=sum(1 for r in under if r["kind"] == "setting")))
            mine += under
        records.append(rec(rid, "dialog", dialog["title"], order=order, openedBy=dialog["openedBy"],
                           itemCount=sum(1 for r in mine if r["kind"] in wd.COUNTED)))
        records += mine
    return records


class Rules(unittest.TestCase):
    def refused(self, records, *said, ribbon=OPENERS):
        with self.assertRaises(wd.Invalid) as ctx:
            wd.validate(records, ribbon)
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

    def lowered(self, records, *ids):
        """`records` with each count that holds one of `ids` lowered to match, as a file edited by hand would be."""
        gone = [r for r in inventory() if r["id"] in ids]
        for lost in gone:
            for holder in records:
                if "itemCount" in holder and lost["id"].startswith(holder["id"] + ".") and holder["kind"] != "setting":
                    holder["itemCount"] -= 1
        return [r for r in records if r["id"] not in ids]

    def test_a_whole_inventory_passes_and_the_list_names_twelve_dialogs(self):
        self.assertIsNone(wd.validate(inventory(), OPENERS))
        self.assertIsNone(wd.validate(inventory()))
        self.assertEqual(len(wd.DIALOGS), 12)
        self.assertEqual(set(wd.REQUIRED), {d["slug"] for d in wd.DIALOGS})
        self.assertEqual([d["slug"] for d in wd.DIALOGS if not d.get("old")], ["track-changes-options"])
        self.assertEqual([d["slug"] for d in wd.DIALOGS][-2:], ["find-and-replace", "mail-merge-recipients"])
        named = {"font", "paragraph", "page-setup", "find-and-replace", "insert-table", "symbol", "index",
                 "table-of-contents", "bookmark", "mail-merge-recipients"}  # the ten the section names
        self.assertFalse(named - set(wd.REQUIRED))
        for dialog in wd.DIALOGS:  # every tab of the list has controls, and no tab is named that the dialog lacks
            self.assertEqual(set(wd.REQUIRED[dialog["slug"]]) - {""}, set(dialog["tabs"]), dialog["slug"])

    def test_a_count_the_capture_reports_about_itself_is_not_what_holds_a_dialog(self):
        # A required control removed, a whole tab removed, an expanded control removed: each with the counts
        # lowered to match, and each still refused.
        hidden = "word.dialogs.font.font.hidden"
        self.refused(self.lowered(inventory(), hidden), "the Font dialog must show Hidden (checkBox) on Font")
        self.assertNotIn("holds", str(self.failure(self.lowered(inventory(), hidden))))
        tab = [r["id"] for r in inventory() if r["id"].startswith("word.dialogs.font.advanced")]
        self.refused(self.lowered(inventory(), *tab), "the Font dialog must show the tabs Font, Advanced")
        find = "word.dialogs.find-and-replace.find"
        self.refused(self.lowered(inventory(), find + ".match-case"),
                     "the Find and Replace dialog must show Match case (checkBox, expanded) on Find")
        # A control of the expanded dialog recorded without its condition is not that control.
        self.refused(self.changed(find + ".match-case", condition=None),
                     "must show Match case (checkBox, expanded) on Find")
        self.refused(self.changed(find + ".find-what", condition="collapsed"),
                     "the only condition of a dialog's record is expanded")
        # The dialog's own controls are those no tab holds: one moved into a tab is missing from the dialog.
        self.refused(self.lowered(inventory(), "word.dialogs.font.cancel"),
                     "the Font dialog must show Cancel (button) of its own")
        self.refused(self.changed(hidden, controlType="radioButton"), "must show Hidden (checkBox) on Font")
        # And a count that does not agree fails on its own.
        self.refused(self.changed("word.dialogs.font", itemCount=3), "word.dialogs.font: holds", "of the 3 tabs, "
                     "headings and controls the capture recorded")
        self.refused(self.changed("word.dialogs.font.font", itemCount=None), "no itemCount, so a lost record")

    def failure(self, records):
        try:
            wd.validate(records, OPENERS)
        except wd.Invalid as exc:
            return exc
        self.fail("the records passed")

    def test_every_dialog_of_the_list_is_there_under_its_title_and_its_opener(self):
        gone = [r["id"] for r in inventory() if r["id"].startswith("word.dialogs.bookmark")]
        self.refused([r for r in inventory() if r["id"] not in gone],
                     "the Bookmark dialog (word.dialogs.bookmark) is not recorded")
        self.refused(self.changed("word.dialogs.index", label="Index and Tables"),
                     "word.dialogs.index: is titled 'Index and Tables', not Index")
        self.refused(self.changed("word.dialogs.font", openedBy="word.home.paragraph.paragraph"),
                     "openedBy is 'word.home.paragraph.paragraph', not word.home.font.font-fontdialog")
        self.refused(inventory(), "its opener word.insert.links.bookmark is not a record of the ribbon inventory",
                     ribbon=OPENERS - {"word.insert.links.bookmark"})
        self.refused(inventory() + [rec("word.dialogs.columns", "dialog", "Columns", openedBy="word.x")],
                     "word.dialogs.columns: not one of the dialogs scripts/lib/word_dialogs.py lists")

    def test_a_list_is_recorded_with_its_choices_or_closed_by_rule(self):
        pane = "word.dialogs.track-changes-options.show.reviewing-pane"
        records = inventory()
        target = next((r for r in records if r["label"] == "Reviewing Pane"), None)
        self.assertIsNotNone(target)
        pane = target["id"]
        self.refused([r for r in records if r["id"] != pane + ".two"], f"{pane}: holds 1 of the 2 choices")
        self.refused([r for r in self.changed(pane, itemCount=None) if r.get("parent") != pane],
                     "Reviewing Pane opens to choices, and none is recorded")
        # A list of an old dialog is recorded closed: choices under it are not something the capture read.
        style = "word.dialogs.font.font.underline-style"
        self.refused(self.changed(style, itemCount=1) + [rec(style + ".single", "menuItem", "Single", style)],
                     "Underline style is recorded without choices")
        self.assertTrue(wd.is_environment(wd.by_slug("font"))(style, "Underline style"))
        self.assertFalse(wd.is_environment(wd.by_slug("track-changes-options"))(pane, "Reviewing Pane"))
        hidden = "word.dialogs.font.font.hidden"
        self.refused(inventory() + [rec(hidden + ".x", "menuItem", "X", hidden)],
                     "a checkBox has no choices, and 1 are recorded under it")

    def test_the_shape_of_the_file_is_held(self):
        hidden = "word.dialogs.font.font.hidden"
        self.refused(self.changed(hidden, app="excel"), "app must be 'word'")
        self.refused(self.changed(hidden, parent="word.dialogs.nowhere"), "its parent word.dialogs.nowhere is not in")
        self.refused(self.changed(hidden, openedBy="word.home.font"), "`openedBy` belongs to the dialog")
        self.refused(self.changed(hidden, label="someone@example.org"), "an e-mail address is the owner's data")
        self.refused(self.changed(hidden, controlType=None), "a control has a controlType")
        self.refused(self.changed("word.dialogs.font", parent="word.dialogs.index"), "a dialog has no parent")
        self.refused(inventory() + [dict(inventory()[2])], "duplicate record id")
        self.refused(inventory() + [rec("word.panes.stray", "setting", "Stray", "word.dialogs.font",
                                        controlType="button")], "a dialog record's id starts with word.dialogs.")
        self.refused([{"app": "word"}], "a dialog record has no id")

    def test_the_parts_the_capture_builds_on(self):
        self.assertEqual(wd.clean(" Underline style: "), "Underline style")
        self.assertEqual(wd.clean("Font Color (Automatic)"), "Font Color")
        self.assertEqual(wd.clean("Sounds like (English)"), "Sounds like (English)")  # only a colour names its value
        ok, cancel = {"role": "Button", "name": "OK"}, {"role": "Button", "name": "Cancel"}
        a, b = {"role": "CheckBox", "name": "A"}, {"role": "Button", "name": "Only here"}
        common, own = wd.split_common([[a, ok, cancel], [b, ok, cancel]])
        self.assertEqual((common, own), ([ok, cancel], [[a], [b]]))
        self.assertEqual(wd.split_common([[a, ok]]), ([], [[a, ok]]))  # one reading: nothing is every tab's
        more = {"role": "Button", "name": "More >>", "rect": (1, 1, 2, 2)}
        less = {"role": "Button", "name": "<< Less", "rect": (1, 1, 2, 2)}
        case = {"role": "CheckBox", "name": "Match case", "rect": (1, 5, 2, 6)}
        self.assertEqual(wd.added([a, more], [a, less, case], "<< Less"), [case])
        self.assertTrue(wd.ignore({"role": "Edit", "name": "RichEdit Control", "class_name": "RichEdit20W"}))
        self.assertTrue(wd.ignore({"role": "Edit", "name": ""}))
        self.assertFalse(wd.ignore({"role": "Edit", "name": "Find what"}))


class Checker(unittest.TestCase):
    def test_the_checker_runs_the_rules_on_the_dialogs_file_only(self):
        self.assertTrue(ci.is_word_dialogs(ci.INVENTORY / "word" / "dialogs.json"))
        self.assertFalse(ci.is_word_dialogs(ci.INVENTORY / "word" / "options.json"))
        self.assertFalse(ci.is_word_dialogs(ci.INVENTORY / "excel" / "dialogs.json"))
        self.assertEqual(ci.check_word_dialogs("dialogs.json", inventory()), [])
        broken = [r for r in inventory() if not r["id"].startswith("word.dialogs.symbol")]
        problems = ci.check_word_dialogs("dialogs.json", broken)
        self.assertEqual(len(problems), 1)
        self.assertIn("dialogs.json: the Symbol dialog (word.dialogs.symbol) is not recorded", problems[0])

    def test_the_schema_takes_the_dialogs_records(self):
        schema = json.loads((ci.INVENTORY / "schema.json").read_text(encoding="utf-8"))
        self.assertEqual(ci.validate(inventory(), schema, schema), [])

    def test_the_committed_dialogs_inventory_is_whole_and_holds_no_data(self):
        path = ci.INVENTORY / "word" / "dialogs.json"
        records = json.loads(path.read_text(encoding="utf-8"))
        ribbon = json.loads((ci.INVENTORY / "word" / "ribbon.json").read_text(encoding="utf-8"))
        self.assertIsNone(wd.validate(records, {r["id"] for r in ribbon}))
        self.assertEqual(sum(1 for r in records if r["kind"] == "dialog"), 12)
        text = path.read_text(encoding="utf-8")
        for data in ("\\\\", "Document1", "@", "Euro Sign", "Alt+Ctrl"):
            self.assertNotIn(data, text)


if __name__ == "__main__":
    unittest.main()
