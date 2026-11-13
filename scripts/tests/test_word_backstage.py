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

    def test_scroll_bars_and_add_in_entries_are_not_recorded(self):
        recs = self.page(n("ScrollBar", kids=[n("Button", "Line up")]), n("Button", "Create Adobe PDF"),
                         n("Button", "Version History"))
        self.assertEqual([r["label"] for r in recs], ["Version History"])

    def test_a_printers_list_is_recorded_without_its_entries(self):
        recs = self.page(n("Group", "Printer", kids=[n("ComboBox", "Which Printer", opens=[n("ListItem", "PDF writer")])]),
                         n("ComboBox", "Page Size", opens=[n("ListItem", "A4")]))
        self.assertEqual([r["label"] for r in recs], ["Printer", "Which Printer", "Page Size"])

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

    def test_an_add_in_record_is_refused(self):
        recs = copy.deepcopy(self.records) + [{"id": "word.backstage.export.create-adobe-pdf", "app": "word",
                                               "kind": "control", "label": "Create Adobe PDF",
                                               "parent": "word.backstage.export", "behaviour": "x"}]
        self.refused(recs, "a third-party entry (Create Adobe PDF) is not Word's")


if __name__ == "__main__":
    unittest.main()
