# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/word_backstage.py: what a Backstage capture records and never records, and the checks the committed
design/inventory/word/backstage.json passes (D02 T01 §6)."""
import copy
import json
from pathlib import Path
import sys
import unittest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
import word_backstage as wb  # noqa: E402  (scripts/lib is put on the path just above)

INVENTORY = REPO / "design" / "inventory"


def base(rid, kind, label, order, node, parent, **extra):
    rec = {"id": rid, "app": "word", "kind": kind, "label": label, "order": order, **extra}
    if parent:
        rec["parent"] = parent
    return rec


def n(role, name="", aid="", cls="", kids=(), **extra):
    return {"role": role, "name": name, "automation_id": aid, "class_name": cls, "children": list(kids), **extra}


class Entries(unittest.TestCase):
    def test_navigation_entries_are_told_apart(self):
        self.assertEqual([wb.classify(x) for x in ("Back", "Home", "Save", "Close", "Options", "Save as Adobe PDF")],
                         ["back", "page", "action", "action", "action", "third-party"])

    def test_the_owners_data_is_taken_out_of_labels(self):
        self.assertEqual(wb.private("Subscription Product for someone@example.com"),
                         "Subscription Product for the signed-in account")
        self.assertEqual(wb.private("OneDrive - Contoso Ltd"), "OneDrive")
        self.assertEqual(wb.private("Sites - Contoso"), "Sites")
        self.assertEqual(wb.private("Print Preview"), "Print Preview")


class Records(unittest.TestCase):
    def page(self, *kids):
        return wb.record_tree("word.backstage.info", n("Group", "Info", kids=kids), base,
                              expand=lambda node: node.get("opens"))

    def test_groups_controls_and_an_opened_menu_are_recorded_in_order(self):
        menu = n("MenuItem", "Protect Document", opens=[n("Menu", kids=[n("Group", kids=[
            n("MenuItem", "Encrypt with Password"), n("MenuItem", "Mark as Final")])])])
        recs = self.page(n("Group", "Protect Document", "GroupPermissions", idMso="GroupPermissions",
                           kids=[menu, n("Text", "A description in Word's words.")]),
                         n("Spinner", "Copies", kids=[n("Edit", "Copies")]), n("ComboBox", "Margins",
                                                                                 opens=[n("ListItem", "Wide")]))
        self.assertEqual([(r["kind"], r["label"]) for r in recs], [
            ("group", "Protect Document"), ("control", "Protect Document"), ("menuItem", "Encrypt with Password"),
            ("menuItem", "Mark as Final"), ("control", "Copies"), ("control", "Margins"), ("menuItem", "Wide")])
        self.assertEqual(recs[0]["idMso"], "GroupPermissions")
        self.assertEqual([r.get("controlType") for r in recs if r["kind"] == "control"], ["menu", "spinner", "dropdown"])
        self.assertNotIn("description", json.dumps(recs))  # Word's prose is never copied

    def test_the_owners_lists_people_and_dates_are_never_recorded(self):
        recs = self.page(
            n("List", "Recent", kids=[n("ListItem", "Client proposal.docx", cls="NetUIListViewItem")]),
            n("Group", "Author", kids=[n("Button", "A Person, Presence unknown", cls="NetUIPersona"),
                                       n("Group", "A Person", cls="NetUIPeoplePicker",
                                         kids=[n("Edit", "A Person", cls="NetUIPeoplePickerWell")])]),
            n("Text", "Today, 03:32", cls="NetUIdatetime"),
            n("Group", "someone@example.com", kids=[n("Button", "Sign out")]),
            n("ComboBox", "", kids=[], opens=[n("ListItem", "Office printer on 10.0.0.5")]))
        text = json.dumps(recs)
        for private in ("Client proposal", "A Person", "03:32", "someone@example.com", "10.0.0.5"):
            self.assertNotIn(private, text)
        self.assertIn('"label": "Author"', text)  # the people picker is recorded under its field's name
        self.assertIn("the signed-in account", text)

    def test_a_task_list_records_word_tasks_but_not_the_accounts_places(self):
        recs = self.page(n("Group", "Open", "GroupOpenPlaces", kids=[n("Pane", kids=[n("Menu", kids=[n("Group", kids=[
            n("TabItem", "Recent"), n("TabItem", "OneDrive - Contoso"),
            n("TabItem", "Finance", kids=[n("Button", "Pin this item to the list.")]), n("TabItem", "This PC")])])])]))
        self.assertEqual([r["label"] for r in recs if r["kind"] == "control"], ["Recent", "OneDrive", "This PC"])

    def test_change_file_types_formats_are_recorded_and_other_galleries_are_not(self):
        recs = self.page(n("Group", "Change File Type", "GroupFileSave", kids=[n("Menu", kids=[
            n("Group", "Document File Types", cls="NetUIGalleryCategoryContainer", kids=[
                n("ListItem", "Document (*.docx)", cls="NetUIGalleryButton"),
                n("ListItem", "Template (*.dotx)", cls="NetUIGalleryButton")])]), n("Button", "Save As")]),
            n("Group", "Templates", kids=[n("ListItem", "Owner's template", cls="NetUIGalleryButton")]))
        self.assertEqual([r["label"] for r in recs if r["kind"] == "control"],
                         ["Document (*.docx)", "Template (*.dotx)", "Save As"])
        self.assertNotIn("Owner's template", json.dumps(recs))

    def test_scroll_bars_and_add_in_entries_are_not_recorded(self):
        recs = self.page(n("ScrollBar", kids=[n("Button", "Line up")]), n("Button", "Create Adobe PDF"),
                         n("Button", "Version History"))
        self.assertEqual([r["label"] for r in recs], ["Version History"])

    def test_a_printers_list_is_recorded_without_its_entries(self):
        recs = self.page(n("Group", "Printer", kids=[n("ComboBox", "Which Printer", opens=[n("ListItem", "PDF writer")])]),
                         n("ComboBox", "Page Size", opens=[n("ListItem", "A4")]))
        self.assertEqual([r["label"] for r in recs], ["Printer", "Which Printer", "Page Size"])

    def test_positions_are_counted_per_parent_across_containers_walked_through(self):
        recs = self.page(n("Pane", kids=[n("Button", "A"), n("Button", "B")]), n("Button", "C"),
                         n("Group", "", kids=[n("Button", "D")]))
        self.assertEqual([(r["label"], r["order"]) for r in recs], [("A", 0), ("B", 1), ("C", 2), ("D", 3)])

    def test_carrying_behaviours_keeps_only_records_the_fresh_capture_saw(self):
        existing = [{"id": "a", "behaviour": "Does a."}, {"id": "gone", "behaviour": "Was there."}]
        captured = [{"id": "a"}, {"id": "new"}]
        self.assertEqual(wb.carry_behaviours(existing, captured), [{"id": "a", "behaviour": "Does a."}, {"id": "new"}])

    def test_a_recapture_keeps_a_disposition_and_refuses_to_lose_one(self):
        # D02 T01 §28: a disposition is written by hand, as a behaviour is, and no capture produces it.
        decided = {"disposition": "excluded", "dispositionReason": "No equivalent is possible."}
        existing = [dict({"id": "a", "behaviour": "Does a."}, **decided), {"id": "b", "disposition": "build"},
                    {"id": "gone", "behaviour": "Was there."}]
        captured = [{"id": "a"}, {"id": "b"}, {"id": "new"}]
        self.assertEqual(wb.carry_behaviours(existing, captured),
                         [dict({"id": "a", "behaviour": "Does a."}, **decided), {"id": "b", "disposition": "build"},
                          {"id": "new"}])
        with self.assertRaises(wb.Invalid) as ctx:  # the capture no longer shows a record the owner decided about
            wb.carry_behaviours(existing + [dict({"id": "lost"}, **decided)], captured)
        self.assertIn("carry a disposition; reconcile them by hand first: lost", str(ctx.exception))

    def test_label_map_gives_ids_to_controls_ui_automation_shows_without_one(self):
        recs = [{"id": "word.backstage.share", "kind": "backstagePage", "idMso": "TabShare", "label": "Share"},
                {"id": "word.backstage.share.share.email", "kind": "control", "label": "Email"}]
        wb.apply_labels(recs)
        self.assertEqual(recs[1]["idMso"], "SendUsingEmail")


class Validate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads((INVENTORY / "word" / "backstage.json").read_text(encoding="utf-8"))
        cls.baseline = json.loads((INVENTORY / "word" / "baseline.json").read_text(encoding="utf-8"))
        cls.reference = (INVENTORY / "REFERENCE.md").read_text(encoding="utf-8")

    def refused(self, records, fragment, absent=None, reference=None):
        with self.assertRaises(wb.Invalid) as ctx:
            wb.validate(records, self.baseline, wb.ABSENT if absent is None else absent,
                        self.reference if reference is None else reference)
        self.assertIn(fragment, str(ctx.exception))

    def test_the_committed_capture_passes(self):
        wb.validate(self.records, self.baseline, wb.ABSENT, self.reference)

    def test_a_missing_page_is_refused_by_name(self):
        recs = [r for r in self.records if r["id"] != "word.backstage.print" and
                not r["id"].startswith("word.backstage.print.")]
        self.refused(recs, "baseline Backstage page TabPrint is neither captured nor listed absent")

    def test_a_missing_group_is_refused_by_name(self):
        recs = [r for r in self.records if r.get("idMso") != "GroupPermissions"]
        self.refused(recs, "baseline group GroupPermissions on TabInfo is neither captured nor listed absent")

    def test_an_absence_whose_reason_is_not_documented_is_refused(self):
        absent = dict(wb.ABSENT, GroupReadOnly="a-new-reason")
        self.refused(self.records, "the absence reason a-new-reason is not documented", absent=absent)

    def test_an_absence_reason_without_an_owner_or_a_final_disposition_is_refused(self):
        reference = self.reference + "\n- `server-state`: shown only for a document in a library.\n"
        self.refused(self.records, "the absence reason server-state has no owning section and is not final",
                     absent=dict(wb.ABSENT, GroupReadOnly="server-state"), reference=reference)
        self.refused(self.records, "REFERENCE.md does not say document-state is captured by D02 T01 §36",
                     reference=self.reference.replace("by `D02 T01 §36`", "later"))
        self.refused(self.records, "REFERENCE.md does not say not-offered is final",
                     reference=self.reference.replace("- `not-offered`: Final:", "- `not-offered`:"))

    def test_a_menu_that_lost_one_of_its_items_is_refused_naming_it(self):
        recs = [r for r in self.records if r["id"] != "word.backstage.print.print.settings.margins.custom-margins"]
        self.assertEqual(len(recs), len(self.records) - 1)
        self.refused(recs, "word.backstage.print.print.settings.margins: Margins holds 6 of the 7 items")
        recs = [dict(r) for r in self.records]
        del next(r for r in recs if r["id"] == "word.backstage.print.print.settings.margins")["itemCount"]
        self.refused(recs, "Margins has items but no itemCount")

    def test_an_absence_that_was_captured_after_all_is_refused(self):
        self.refused(self.records, "listed absent but captured: GroupPermissions",
                     absent=dict(wb.ABSENT, GroupPermissions="document-state"))

    def test_a_missing_behaviour_is_refused_naming_the_record(self):
        recs = copy.deepcopy(self.records)
        target = next(r for r in recs if r["kind"] == "menuItem")
        del target["behaviour"]
        self.refused(recs, f"menuItem {target['id']} has no behaviour")
        wb.validate(recs, self.baseline, wb.ABSENT, self.reference, require_behaviour=False)

    def test_an_action_left_out_or_an_owners_address_is_refused(self):
        self.refused([r for r in self.records if r["id"] != "word.backstage.close"],
                     "the navigation action Close is not recorded")
        recs = copy.deepcopy(self.records)
        recs[1]["label"] = "Signed in as someone@example.com"
        self.refused(recs, "an e-mail address is the owner's data")

    def test_a_behaviour_that_does_not_say_when_it_is_unavailable_is_refused(self):
        recs = copy.deepcopy(self.records)
        target = next(r for r in recs if r["id"] == "word.backstage.print.print-preview.zoom-in")
        target["behaviour"] = "Makes the preview larger."
        self.refused(recs, "word.backstage.print.print-preview.zoom-in: its behaviour does not say when it is unavailable")
        target["behaviour"] = "Makes the preview larger. Always available."
        wb.validate(recs, self.baseline, wb.ABSENT, self.reference)
        for incidental in ("Makes the document suggest opening read only.",  # reconciliation 2: a word, no condition
                           "Prints only when asked, and needs nothing more.", "Marks it final; readers see it read only."):
            target["behaviour"] = incidental
            self.refused(recs, "its behaviour does not say when it is unavailable")
        for stated in ("Shows the size; read only.", "Prints. Needs an installed printer.",
                       "Opens it; disabled until a name is entered."):
            target["behaviour"] = stated
            wb.validate(recs, self.baseline, wb.ABSENT, self.reference)

    def test_save_is_an_action_or_the_page_it_shows(self):
        recs = copy.deepcopy(self.records)
        save = next(r for r in recs if r["id"] == "word.backstage.save")
        save["target"] = "word.backstage.nowhere"
        self.refused(recs, "the navigation action Save is not recorded")

    def test_a_menu_recorded_without_its_items_is_refused(self):
        recs = [r for r in self.records if r.get("parent") != "word.backstage.print.print.settings.margins"]
        self.refused(recs, "word.backstage.print.print.settings.margins: Margins opens to items, and none is recorded")
        unexpanded = [r for r in self.records if r["kind"] != "menuItem" or r.get("idMso")]
        self.refused(unexpanded, "opens to items, and none is recorded")

    def test_an_environment_list_recorded_with_its_entries_is_refused(self):
        recs = copy.deepcopy(self.records) + [{"id": "word.backstage.print.print.printer.which-printer.office", "app": "word",
                                               "kind": "menuItem", "label": "Office printer", "behaviour": "x",
                                               "parent": "word.backstage.print.print.printer.which-printer"}]
        self.refused(recs, "Which Printer lists this PC's or organisation's data")

    def test_every_position_in_the_committed_capture_is_unique_under_its_parent(self):
        positions = [(r.get("parent"), r["order"]) for r in self.records]
        self.assertEqual(len(positions), len(set(positions)))

    def test_an_add_in_record_is_refused(self):
        recs = copy.deepcopy(self.records) + [{"id": "word.backstage.export.create-adobe-pdf", "app": "word",
                                               "kind": "control", "label": "Create Adobe PDF",
                                               "parent": "word.backstage.export", "behaviour": "x"}]
        self.refused(recs, "a third-party entry (Create Adobe PDF) is not Word's")


if __name__ == "__main__":
    unittest.main()
