# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/word_menus.py: the rules of Word's context menu inventory, and the checker's use of them
(D02 T01 §35)."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest
import unittest.mock

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import word_menus as wm  # noqa: E402  (scripts/lib is put on the path just above)

spec = importlib.util.spec_from_file_location("check_inventory_for_menus", SCRIPTS / "check-inventory.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

SOURCE = {"source": "uia:16.0.20527.20150", "capturedFrom": "16.0.20527.20150"}


def item(entry, choices=None):
    """An item as word_menus.menu_items and toolbar_items make it, from an entry of REQUIRED."""
    label, ctype, flags = entry[0], entry[1], set(entry[2:])
    made = {"label": label, "type": ctype, "node": None}
    if label not in wm.FOLLOWS:
        made["enabled"] = "disabled" not in flags
    if flags & {"checked", "unchecked"}:
        made["checked"] = "checked" in flags
    if choices is not None:
        made["choices"] = [item(c) for c in choices]
    return made


def base(rid, kind, label, order, node, parent, **extra):
    record = {"id": rid, "app": "word", "kind": kind, "label": label, "order": order, **SOURCE, **extra}
    if parent:
        record["parent"] = parent
    return record


def inventory(required=None):
    """A whole menus inventory, built by the module's own `records` from the hand-written lists: every context
    with the items, the states, the fixed submenus' choices and the mini toolbar the lists require."""
    required, out = required or wm.REQUIRED, []
    for order, spec_ in enumerate(wm.CONTEXTS):
        wanted = required[spec_["slug"]]
        items = [item(e, wanted.get("submenus", {}).get(e[0]) if e[0] in spec_["submenus"] else None)
                 for e in wanted["menu"]]
        tools = [item(e) for e in wanted["toolbar"]] if spec_["toolbar"] else None
        out += wm.records(spec_, order, None, items, None, tools, base)
    return out


def refusal(records):
    try:
        wm.validate(records)
    except wm.Invalid as exc:
        return str(exc)
    return ""


def without(records, rid):
    """The records without `rid` and what stands under it, the counts of what holds it lowered to match: a file
    whose own counts agree, so only the hand-written list can tell."""
    gone = {rid}
    for rec in records:  # records stand after their parent
        if rec.get("parent") in gone:
            gone.add(rec["id"])
    kept = copy.deepcopy([r for r in records if r["id"] not in gone])
    by_id = {r["id"]: r for r in records}
    parent = by_id[rid].get("parent")
    direct = True
    while parent:
        holder = next(r for r in kept if r["id"] == parent)
        if "itemCount" in holder:
            holder["itemCount"] -= len(gone) if holder["kind"] == "contextMenu" or not direct else 1
        direct, parent = False, by_id[parent].get("parent")
    return kept


class Rules(unittest.TestCase):
    def test_the_lists_agree_with_each_other(self):
        self.assertEqual(set(wm.REQUIRED), {c["slug"] for c in wm.CONTEXTS})
        self.assertEqual(len(wm.CONTEXTS), 11)
        for spec_ in wm.CONTEXTS:
            wanted = wm.REQUIRED[spec_["slug"]]
            self.assertTrue(wanted["menu"], spec_["slug"])
            self.assertEqual(spec_["toolbar"], bool(wanted.get("toolbar")), spec_["slug"])
            self.assertEqual(set(spec_["submenus"]), set(wanted.get("submenus", {})), spec_["slug"])
            labels = {e[0] for e in wanted["menu"]}
            self.assertLessEqual(set(spec_["submenus"]), labels, spec_["slug"])
            unnamed = [e[0] for e in wanted.get("toolbar", ()) if e[1] in ("comboBox", "menu")]
            self.assertEqual(unnamed, list(spec_["unnamed"]), spec_["slug"])
            for entry in list(wanted["menu"]) + list(wanted.get("toolbar", ())) + [
                    c for choices in wanted.get("submenus", {}).values() for c in choices]:
                self.assertLessEqual(set(entry[2:]), {"disabled", "checked", "unchecked"}, entry)
                self.assertFalse(entry[0] in wm.FOLLOWS and entry[2:], entry)
        # the two text states and the header and the footer are contexts of their own (plan review, gap 1)
        self.assertLessEqual({"text-selected", "text-caret", "header", "footer"}, set(wm.REQUIRED))

    def test_a_whole_inventory_passes_and_the_checker_agrees(self):
        records = inventory()
        self.assertEqual(refusal(records), "")
        self.assertEqual(ci.check_word_menus("menus.json", records), [])
        self.assertEqual(sum(1 for r in records if r["kind"] == "contextMenu"), 11)
        self.assertEqual(sum(1 for r in records if r["kind"] == "miniToolbar"), 9)
        by_id = {r["id"]: r for r in records}
        self.assertEqual(by_id["word.menus.text-caret"]["condition"],
                         "the caret stands in a word of body text, nothing selected")
        self.assertIs(by_id["word.menus.text-caret.cut"]["enabled"], False)
        self.assertNotIn("enabled", by_id["word.menus.text-selected.cut"])
        self.assertNotIn("enabled", by_id["word.menus.text-selected.paste-options"])
        self.assertIs(by_id["word.menus.tracked-change.track-changes"]["checked"], False)
        self.assertIs(by_id["word.menus.hyperlink.mini-toolbar.underline"]["checked"], True)
        insert = by_id["word.menus.table.insert"]
        self.assertEqual((insert["controlType"], insert["itemCount"]), ("menu", 5))
        self.assertEqual(by_id["word.menus.table.insert.insert-rows-above"]["parent"], insert["id"])
        self.assertEqual(by_id["word.menus.comment"]["itemCount"], 3)

    def test_a_missing_context_is_refused_by_name_though_its_twin_is_there(self):
        records = inventory()
        for slug, title in (("text-caret", "Text, a caret in a word"), ("text-selected", "Text, a word selected"),
                            ("footer", "Footer"), ("header", "Header")):
            said = refusal(without(records, f"word.menus.{slug}"))
            self.assertIn(f"the {title} context menu (word.menus.{slug}) is not recorded", said)
            self.assertEqual(said.count("is not recorded"), 1, said)
        said = ci.check_word_menus("menus.json", without(records, "word.menus.footer"))
        self.assertEqual(len(said), 1)
        self.assertIn("the Footer context menu", said[0])

    def test_a_state_that_changed_is_refused_with_every_item_and_count_kept(self):
        records = inventory()

        def changed(rid, **fields):
            out = copy.deepcopy(records)
            rec = next(r for r in out if r["id"] == rid)
            for key, value in fields.items():
                if value is None:
                    rec.pop(key)
                else:
                    rec[key] = value
            self.assertEqual(len(out), len(records))
            return refusal(out)
        self.assertIn("must show Cut available in its menu", changed("word.menus.text-selected.cut", enabled=False))
        self.assertIn("must show Cut disabled in its menu", changed("word.menus.text-caret.cut", enabled=None))
        self.assertIn("Paste Options without a state in its menu",
                      changed("word.menus.text-caret.paste-options", enabled=False))
        self.assertIn("New Comment disabled on its mini toolbar",
                      changed("word.menus.header.mini-toolbar.new-comment", enabled=None))
        self.assertIn("a toggle is recorded with whether it is on",
                      changed("word.menus.text-selected.mini-toolbar.bold", checked=None))
        self.assertIn("Underline on its mini toolbar ticked",
                      changed("word.menus.hyperlink.mini-toolbar.underline", checked=False))
        self.assertIn("Track Changes in its menu not ticked",
                      changed("word.menus.tracked-change.track-changes", checked=True))
        self.assertIn("Cut in its menu without `checked`", changed("word.menus.text-selected.cut", checked=True))
        self.assertIn("Edit Wrap Points disabled under Wrap Text",
                      changed("word.menus.picture.wrap-text.edit-wrap-points", enabled=None))
        self.assertIn("its condition is 'a word is selected', not the selection the list gives it",
                      changed("word.menus.text-selected", condition="a word is selected"))
        self.assertIn("`condition` belongs to the context menu",
                      changed("word.menus.text-selected.cut", condition="a word of body text is selected"))

    def test_a_required_entry_is_counted(self):
        required = copy.deepcopy(wm.REQUIRED)
        required["comment"]["menu"] += (("Delete thread", "button"),)  # the list asks for two of them
        with unittest.mock.patch.dict(wm.REQUIRED, required):
            two = inventory()
            self.assertEqual(refusal(two), "")
            one = without(two, "word.menus.comment.delete-thread-2")
            self.assertIn("must show Delete thread (button) 2 times in its menu", refusal(one))

    def test_what_a_context_must_show_is_held_whatever_the_counts_say(self):
        records = inventory()
        for rid, said in (
                ("word.menus.text-selected.synonyms", "must show Synonyms (menu) in its menu"),
                ("word.menus.shape.mini-toolbar.fill", "must show Fill (menu) on its mini toolbar"),
                ("word.menus.table.insert.insert-cells", "must show Insert Cells... (button) under Insert"),
                ("word.menus.shape.send-to-back.send-backward", "must show Send Backward (button) under Send to Back"),
                ("word.menus.picture.wrap-text.square", "must show Square (galleryItem) under Wrap Text")):
            self.assertIn(said, refusal(without(records, rid)), rid)
        # another type under the same label does not stand in for it
        out = copy.deepcopy(records)
        next(r for r in out if r["id"] == "word.menus.text-selected.synonyms")["controlType"] = "button"
        self.assertIn("must show Synonyms (menu) in its menu", refusal(out))

    def test_the_mini_toolbar_is_there_where_the_list_says_and_only_there(self):
        records = inventory()
        said = refusal(without(records, "word.menus.table.mini-toolbar"))
        self.assertIn("the Table cell context shows a mini toolbar, and 0 are recorded", said)
        out = copy.deepcopy(records)
        out.append(base("word.menus.spelling-error.mini-toolbar", "miniToolbar", wm.TOOLBAR, 99, None,
                        "word.menus.spelling-error", itemCount=0))
        next(r for r in out if r["id"] == "word.menus.spelling-error")["itemCount"] += 1
        self.assertIn("the Spelling error context shows no mini toolbar, and one is recorded", refusal(out))

    def test_a_submenu_is_open_only_where_the_list_names_it(self):
        out = copy.deepcopy(inventory())
        owner = next(r for r in out if r["id"] == "word.menus.text-caret.synonyms")
        owner["itemCount"] = 1
        out.append(base("word.menus.text-caret.synonyms.terms", "menuItem", "terms", 0, None, owner["id"],
                        controlType="button"))
        next(r for r in out if r["id"] == "word.menus.text-caret")["itemCount"] += 1
        self.assertIn("word.menus.text-caret.synonyms: a submenu is recorded open only where the list names it",
                      refusal(out))

    def test_counts_identity_and_shape_are_held(self):
        records = inventory()
        out = copy.deepcopy(records)
        del out[5]
        self.assertIn("word.menus.text-selected: holds 27 of the 28 records the capture recorded", refusal(out))
        out = copy.deepcopy(records)
        next(r for r in out if r["id"] == "word.menus.table.insert").pop("itemCount")
        self.assertIn("word.menus.table.insert: no itemCount", refusal(out))
        out = copy.deepcopy(records) + [copy.deepcopy(records[1])]
        self.assertIn(f"duplicate record id {records[1]['id']}", refusal(out))
        out = copy.deepcopy(records)
        out.append(base("word.menus.footnote", "contextMenu", "Footnote", 11, None, None, itemCount=0))
        self.assertIn("word.menus.footnote: not one of the contexts", refusal(out))
        out = copy.deepcopy(records)
        out[1]["label"] = "someone@example.com"
        self.assertIn("an e-mail address is the owner's data", refusal(out))
        out = copy.deepcopy(records)
        out[0]["app"] = "excel"
        self.assertIn("app must be 'word'", refusal(out))
        with self.assertRaises(wm.Invalid):
            wm.validate([{"kind": "contextMenu"}])
        self.assertEqual(ci.check_word_menus("menus.json", [])[0].count("is not recorded"), 11)


def node(role, name="", cls="", enabled=True, **extra):
    """A plain node as the capture makes it; `reads` counts how often its name was fetched."""
    made = {"role": role, "class_name": cls, "enabled": enabled, "rect": (0, 0, 1, 1), "reads": 0, **extra}

    def read():
        made["reads"] += 1
        return name
    made["read"] = read
    return made


class Reading(unittest.TestCase):
    SPEC = wm.by_slug("shape")

    def test_items_groups_separators_and_states(self):
        clipboard = [node("ListItem", "Keep Source Formatting")]
        inner = [node("MenuItem", "Link last used on this PC"), node("Button", "Link")]
        nodes = [
            node("Edit", "Type to search"),
            node("Group", children=[node("MenuItem", "Cut", enabled=False), node("MenuItem", "Copy"),
                                    node("Menu", "Paste Options", cls=wm.GALLERY_CLASS, enabled=False,
                                         kids=clipboard)]),
            node("Group", children=[node("MenuItem", "Edit Points", toggle=wm.UNTICKED),
                                    node("MenuItem", "Synonyms", expandable=True),
                                    node("SplitButton", "Link", expandable=True, kids=inner)]),
            node("Group", children=[node("ListItem", "Square")]),
        ]
        items = wm.menu_items(nodes, self.SPEC)
        self.assertEqual([(i["label"], i["type"]) for i in items], [
            ("Type to search", "editBox"), ("Cut", "button"), ("Copy", "button"), ("Paste Options", "gallery"),
            (wm.SEPARATOR, "separator"), ("Edit Points", "button"), ("Synonyms", "menu"), ("Link", "splitButton"),
            (wm.SEPARATOR, "separator"), ("Square", "galleryItem")])
        by = {i["label"]: i for i in items}
        self.assertIs(by["Cut"]["enabled"], False)
        self.assertIs(by["Copy"]["enabled"], True)
        self.assertNotIn("enabled", by["Paste Options"])  # it follows the clipboard: no state
        self.assertIs(by["Edit Points"]["checked"], False)
        self.assertNotIn("checked", by["Copy"])
        # what stands under a gallery or a split button is this PC's: its name is never fetched
        self.assertEqual([n["reads"] for n in clipboard + inner], [0, 0, 0])

    def test_what_the_rules_do_not_know_is_refused_not_passed_over(self):
        with self.assertRaises(wm.Invalid) as ctx:
            wm.menu_items([node("Group", children=[node("Slider", "Zoom")])], self.SPEC)
        self.assertIn("holds a Slider", str(ctx.exception))
        with self.assertRaises(wm.Invalid) as ctx:  # an open submenu's frame among the items
            wm.menu_items([node("Menu", "", cls=wm.FRAME_CLASS)], self.SPEC)
        self.assertIn("holds a Menu (NetUIToolWindow)", str(ctx.exception))
        with self.assertRaises(wm.Invalid) as ctx:
            wm.menu_items([node("MenuItem", "")], self.SPEC)
        self.assertIn("has no name", str(ctx.exception))

    def test_a_tick_that_cannot_be_read_is_refused_not_recorded_as_off(self):
        for raw in (None, 2, "on"):
            with self.assertRaises(wm.Invalid) as ctx:
                wm.menu_items([node("MenuItem", "Track Changes", toggle=raw)], self.SPEC)
            self.assertIn("whether Track Changes of the Shape menu is ticked could not be read", str(ctx.exception))
            with self.assertRaises(wm.Invalid) as ctx:
                wm.toolbar_items([node("Button", "Bold", toggle=raw)], dict(self.SPEC, unnamed=()))
            self.assertIn("whether Bold of the Shape mini toolbar is on could not be read", str(ctx.exception))

    def test_a_toolbar_names_by_position_what_has_no_name_of_its_own(self):
        font = node("ComboBox", "Calibri, the font of this PC")
        fill = node("MenuItem", "Fill Orange, Accent 2")
        nodes = [node("Button", "Edit with Copilot ", enabled=False), font, node("Button", "Bold", toggle=wm.TICKED),
                 node("SplitButton", "Bullets", toggle=wm.UNTICKED), node("SplitButton", "Font Color"), fill]
        tools = wm.toolbar_items(nodes, dict(self.SPEC, unnamed=("Font", "Fill")))
        self.assertEqual([(t["label"], t["type"], t.get("checked"), t["enabled"]) for t in tools], [
            ("Edit with Copilot", "button", None, False), ("Font", "comboBox", None, True),
            ("Bold", "toggleButton", True, True), ("Bullets", "splitButton", False, True),
            ("Font Color", "splitButton", None, True), ("Fill", "menu", None, True)])
        self.assertEqual((font["reads"], fill["reads"]), (0, 0))
        with self.assertRaises(wm.Invalid) as ctx:
            wm.toolbar_items(nodes, dict(self.SPEC, unnamed=("Font",)))
        self.assertIn("more unnamed controls", str(ctx.exception))
        with self.assertRaises(wm.Invalid) as ctx:
            wm.toolbar_items(nodes, dict(self.SPEC, unnamed=("Font", "Fill", "Outline")))
        self.assertIn("fewer unnamed controls", str(ctx.exception))
        self.assertIn("Outline not seen", str(ctx.exception))
        with self.assertRaises(wm.Invalid):
            wm.toolbar_items([node("Slider", "Zoom")], self.SPEC)

    def test_two_readings_differ_on_a_label_a_state_or_a_choice(self):
        one = [item(("Cut", "button")), item(("Insert", "menu"), [("Rows", "button")])]
        self.assertEqual(wm.signature(one), wm.signature(copy.deepcopy(one)))
        for other in ([item(("Cut", "button", "disabled")), one[1]],
                      [item(("Cut", "button", "unchecked")), one[1]],
                      [one[0], item(("Insert", "menu"), [("Columns", "button")])],
                      [one[1], one[0]]):
            self.assertNotEqual(wm.signature(one), wm.signature(other))

    def test_ids_are_told_apart_and_separators_are_recorded(self):
        items = [item(("Cut", "button")), {"label": wm.SEPARATOR, "type": "separator", "node": None},
                 item(("Cut", "button")), {"label": wm.SEPARATOR, "type": "separator", "node": None}]
        made = wm.records(wm.by_slug("comment"), 10, None, items, None, None, base)
        self.assertEqual([r["id"].rsplit(".", 1)[1] for r in made[1:]], ["cut", "separator", "cut-2", "separator-2"])
        self.assertEqual((made[0]["itemCount"], made[0]["condition"]),
                         (4, "the More thread actions button of a comment's card"))
        self.assertEqual([r.get("controlType") for r in made[1:]], ["button", "separator", "button", "separator"])
        self.assertTrue(all("enabled" not in r for r in made))


if __name__ == "__main__":
    unittest.main()
