# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/check-layout.py: a built app's capture against the inventory, on fixtures (D02 T01 §30)."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_layout", SCRIPTS / "check-layout.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)

PROFILE = "fhd-100"


def box(x, y, width, height):
    return {"x": x, "y": y, "width": width, "height": height}


def rec(rid, kind, label, parent=None, **extra):
    record = {"id": rid, "app": "word", "kind": kind, "label": label, "captureProfile": PROFILE, **extra}
    if parent:
        record["parent"] = parent
    return record


def inventory():
    """Two tabs. Home: a Paragraph group of three controls (one with a uiaId), a group with two items of one label,
    and an Effects group holding a Shadow menu. Insert: an Effects group holding a Shadow menu of the same label
    and type, which only its branch tells from Home's. View: two groups of one label."""
    return [
        rec("word.home", "tab", "Home", uiaId="TabHome", order=0, bounds=box(0, 60, 1900, 120)),
        rec("word.home.para", "group", "Paragraph", "word.home", order=0, bounds=box(408, 80, 251, 96)),
        rec("word.home.para.bullets", "control", "Bullets", "word.home.para", uiaId="Bullets", order=0,
            controlType="splitButton", bounds=box(416, 90, 39, 24)),
        rec("word.home.para.sort", "control", "Sort", "word.home.para", order=1, controlType="button",
            bounds=box(457, 90, 24, 24)),
        rec("word.home.para.show", "control", "Show All", "word.home.para", order=2, controlType="toggleButton",
            bounds=box(483, 90, 24, 24)),
        rec("word.home.lines", "group", "Lines", "word.home", order=1, bounds=box(700, 80, 100, 96)),
        rec("word.home.lines.line", "control", "Line", "word.home.lines", order=0, controlType="galleryItem",
            bounds=box(704, 90, 20, 20)),
        rec("word.home.lines.line-2", "control", "Line", "word.home.lines", order=1, controlType="galleryItem",
            bounds=box(728, 90, 20, 20)),
        rec("word.home.fx", "group", "Effects", "word.home", order=2, bounds=box(900, 80, 100, 96)),
        rec("word.home.fx.shadow", "control", "Shadow", "word.home.fx", order=0, controlType="menu",
            bounds=box(904, 90, 40, 24)),
        rec("word.home.fx.shadow.outer", "menuItem", "Outer", "word.home.fx.shadow", order=0,
            bounds=box(904, 120, 80, 20)),
        rec("word.home.fx.shadow.inner", "menuItem", "Inner", "word.home.fx.shadow", order=1,
            bounds=box(904, 140, 80, 20)),
        rec("word.insert", "tab", "Insert", uiaId="TabInsert", order=1, bounds=box(0, 60, 1900, 120)),
        rec("word.insert.fx", "group", "Effects", "word.insert", order=0, bounds=box(100, 80, 100, 96)),
        rec("word.insert.fx.shadow", "control", "Shadow", "word.insert.fx", order=0, controlType="menu",
            bounds=box(104, 90, 40, 24)),
        rec("word.insert.fx.shadow.outer", "menuItem", "Outer", "word.insert.fx.shadow", order=0,
            bounds=box(104, 120, 80, 20)),
        rec("word.insert.fx.shadow.inner", "menuItem", "Inner", "word.insert.fx.shadow", order=1,
            bounds=box(104, 140, 80, 20)),
        rec("word.view", "tab", "View", uiaId="TabView", order=2, bounds=box(0, 60, 1900, 120)),
        rec("word.view.macros", "group", "Macros", "word.view", order=0, bounds=box(8, 80, 60, 96)),
        rec("word.view.macros.run", "control", "Run", "word.view.macros", order=0, controlType="button",
            bounds=box(12, 90, 40, 24)),
        rec("word.view.macros-2", "group", "Macros", "word.view", order=1, bounds=box(80, 80, 60, 96)),
        rec("word.view.macros-2.record", "control", "Record", "word.view.macros-2", order=0, controlType="button",
            bounds=box(84, 90, 40, 24)),
    ]


class Layout(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "design" / "inventory" / "word").mkdir(parents=True)
        self.records = inventory()
        self.write_inventory()

    def tearDown(self):
        self.tmp.cleanup()

    def write_inventory(self):
        (self.root / "design" / "inventory" / "word" / "ribbon.json").write_text(json.dumps(self.records),
                                                                                 encoding="utf-8")

    def built(self):
        """What a capture of our own app would hold when it matches: the same elements under ids of its own, given
        in another order than the inventory's file."""
        records = copy.deepcopy(self.records)
        for record in records:
            record["id"] = "write" + record["id"][4:]
            if "parent" in record:
                record["parent"] = "write" + record["parent"][4:]
            record.pop("app")
        return list(reversed(records))

    def element(self, capture, rid):
        return next(r for r in capture if r["id"] == "write" + rid[4:])

    def run_check(self, parent, capture, *argv):
        path = self.root / "capture.json"
        path.write_text(capture if isinstance(capture, str) else json.dumps(capture), encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cl.main(["--parent", parent, "--capture", str(path), *argv], root=self.root)
        return code, out.getvalue(), err.getvalue()

    def counts(self, parent, children, paired, **kinds):
        return f"{parent}: {children} children, {paired} paired, " + ", ".join(
            f"{kinds.get(kind, 0)} {kind}" for kind in cl.KINDS) + "\n"

    PARA = "word.home.para"

    def test_a_capture_that_matches_passes_whatever_order_its_file_is_in(self):
        code, out, err = self.run_check(self.PARA, self.built())
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out, self.counts(self.PARA, 3, 3))
        for parent, children in (("word.home", 3), ("word.home.lines", 2), ("word.home.fx.shadow", 2),
                                 ("word.insert.fx.shadow", 2), ("word.view.macros-2", 1)):
            self.assertEqual(self.run_check(parent, self.built()), (0, self.counts(parent, children, children), ""))

    def test_a_missing_control_fails_and_an_added_one_does_not(self):
        capture = [r for r in self.built() if r["id"] != "write.home.para.sort"]
        code, out, err = self.run_check(self.PARA, capture)
        self.assertEqual(code, 1)
        self.assertEqual(err, "missing word.home.para.sort: no captured element for 'Sort' (button)\n")
        self.assertEqual(out, self.counts(self.PARA, 3, 2, missing=1))
        added = self.built() + [{"id": "write.home.para.new", "kind": "control", "label": "Focus", "order": 9,
                                 "controlType": "button", "parent": "write.home.para", "captureProfile": PROFILE,
                                 "bounds": box(520, 90, 24, 24)}]
        code, out, err = self.run_check(self.PARA, added)
        self.assertEqual(code, 0)  # an improvement may add a control; it may never lose one
        self.assertEqual(err, "extra write.home.para.new: 'Focus' (button) is in the capture and not in the "
                              "inventory\n")
        self.assertEqual(out, self.counts(self.PARA, 3, 3, extra=1))

    def test_a_rename_and_a_type_change_are_reported_with_and_without_a_uia_id(self):
        cases = (  # (the record, the field changed in the capture, its new value, the finding)
            ("word.home.para.bullets", "label", "Bullet List",
             "renamed word.home.para.bullets: 'Bullets' in the inventory, 'Bullet List' in the capture\n"),
            ("word.home.para.bullets", "controlType", "gallery",
             "retyped word.home.para.bullets: splitButton in the inventory, gallery in the capture\n"),
            ("word.home.para.sort", "controlType", "splitButton",  # paired by its label
             "retyped word.home.para.sort: button in the inventory, splitButton in the capture\n"),
            ("word.home.para.sort", "label", "Sort Rows",  # paired by its place between Bullets and Show All
             "renamed word.home.para.sort: 'Sort' in the inventory, 'Sort Rows' in the capture\n"),
        )
        for rid, field, value, finding in cases:
            capture = self.built()
            self.element(capture, rid)[field] = value
            code, out, err = self.run_check(self.PARA, capture)
            self.assertEqual((code, err), (1, finding), (rid, field))
            self.assertEqual(out, self.counts(self.PARA, 3, 3, **{finding.split()[0]: 1}))
        capture = self.built()  # no uiaId, and both its label and its type changed: one removed, one added
        self.element(capture, "word.home.para.sort").update(label="Arrange", controlType="menu")
        code, out, err = self.run_check(self.PARA, capture)
        self.assertEqual(code, 1)
        self.assertEqual(err, "missing word.home.para.sort: no captured element for 'Sort' (button)\n"
                              "extra write.home.para.sort: 'Arrange' (menu) is in the capture and not in the "
                              "inventory\n")
        self.assertEqual(out, self.counts(self.PARA, 3, 2, missing=1, extra=1))

    def test_an_id_is_an_identity_and_a_label_is_not_one_for_an_element_that_has_an_id(self):
        capture = self.built()  # the captured Sort carries a uiaId, the record none: not the same control
        self.element(capture, "word.home.para.sort")["uiaId"] = "SortButton"
        code, _, err = self.run_check(self.PARA, capture)
        self.assertEqual(code, 1)
        self.assertIn("missing word.home.para.sort: no captured element for 'Sort' (button)\n", err)
        self.assertIn("extra write.home.para.sort: 'Sort' (button)", err)
        capture = self.built()  # and a record's uiaId is not found under another label
        self.element(capture, "word.home.para.bullets")["uiaId"] = "SomethingElse"
        code, _, err = self.run_check(self.PARA, capture)
        self.assertIn("missing word.home.para.bullets", err)
        capture = self.built()  # nor under its own label, on a captured element that has lost the id
        del self.element(capture, "word.home.para.bullets")["uiaId"]
        code, out, err = self.run_check(self.PARA, capture)
        self.assertEqual(code, 1)
        self.assertIn("missing word.home.para.bullets", err)
        self.assertIn("extra write.home.para.bullets", err)
        self.assertEqual(out, self.counts(self.PARA, 3, 2, missing=1, extra=1))

    def test_children_out_of_their_order_are_reported_and_an_added_one_between_them_is_not(self):
        capture = self.built()
        self.element(capture, "word.home.para.sort")["order"] = 2
        self.element(capture, "word.home.para.show")["order"] = 1
        code, out, err = self.run_check(self.PARA, capture, "--no-bounds")
        self.assertEqual(code, 1)
        self.assertEqual(err.count("reordered "), 1)  # one of the two moved past the other
        self.assertRegex(err, r"^reordered word\.home\.para\.(sort|show): place [23] of 3 paired children in the "
                              r"inventory, place [23] in the capture\n$")
        self.assertEqual(out, self.counts(self.PARA, 3, 3, reordered=1))
        capture = self.built()  # a new control between the first and the second renumbers them, and reorders nothing
        for rid, order in (("word.home.para.sort", 2), ("word.home.para.show", 3)):
            self.element(capture, rid)["order"] = order
        capture.append({"id": "write.home.para.new", "kind": "control", "label": "Focus", "order": 1,
                        "controlType": "button", "parent": "write.home.para", "captureProfile": PROFILE})
        code, out, _ = self.run_check(self.PARA, capture, "--no-bounds")
        self.assertEqual((code, out), (0, self.counts(self.PARA, 3, 3, extra=1)))

    def test_a_position_and_a_size_are_held_within_the_tolerance(self):
        def shifted(field, by):
            capture = self.built()
            self.element(capture, "word.home.para.sort")["bounds"][field] += by
            return capture
        was = "x 49, y 10, 24 by 24 in the inventory"
        for field, kind, now in (("x", "moved", "x 54, y 10, 24 by 24"), ("y", "moved", "x 49, y 15, 24 by 24"),
                                 ("width", "resized", "x 49, y 10, 29 by 24"),
                                 ("height", "resized", "x 49, y 10, 24 by 29")):
            code, out, err = self.run_check(self.PARA, shifted(field, 5))
            self.assertEqual((code, err), (1, f"{kind} word.home.para.sort: {was}; {now} in the capture\n"), field)
            self.assertEqual(out, self.counts(self.PARA, 3, 3, **{kind: 1}))
            self.assertEqual(self.run_check(self.PARA, shifted(field, 1))[::2], (0, ""), field)   # within 2 pixels
            self.assertEqual(self.run_check(self.PARA, shifted(field, -2))[0], 0, field)
            self.assertEqual(self.run_check(self.PARA, shifted(field, 3))[0], 1, field)
            self.assertEqual(self.run_check(self.PARA, shifted(field, 1), "--tolerance", "0")[0], 1, field)
            self.assertEqual(self.run_check(self.PARA, shifted(field, 5), "--tolerance", "5")[0], 0, field)
            self.assertEqual(self.run_check(self.PARA, shifted(field, 5), "--no-bounds")[::2], (0, ""), field)
        # The whole window moved: positions are measured from the parent's corner, so nothing did.
        capture = self.built()
        for record in capture:
            if "bounds" in record:
                record["bounds"]["x"] += 300
                record["bounds"]["y"] += 40
        self.assertEqual(self.run_check(self.PARA, capture)[::2], (0, ""))

    def test_a_pair_that_cannot_be_measured_fails_unless_positions_are_not_compared(self):
        def without(rid, side):
            self.records = inventory()
            capture = self.built()
            if side == "capture":
                del self.element(capture, rid)["bounds"]
            else:
                del next(r for r in self.records if r["id"] == rid)["bounds"]
            self.write_inventory()
            return capture
        cases = (("word.home.para.sort", "inventory", ["sort"], "the record"),
                 ("word.home.para.sort", "capture", ["sort"], "the captured element"),
                 (self.PARA, "inventory", ["bullets", "sort", "show"], "the inventory's parent"),
                 (self.PARA, "capture", ["bullets", "sort", "show"], "the captured parent"))
        for rid, side, named, lacking in cases:
            capture = without(rid, side)
            code, out, err = self.run_check(self.PARA, capture)
            self.assertEqual(code, 1, (rid, side))
            self.assertEqual(err, "".join(f"unmeasured word.home.para.{name}: no bounds on {lacking}\n"
                                          for name in named))
            self.assertEqual(out, self.counts(self.PARA, 3, 3, unmeasured=len(named)))
            self.assertEqual(self.run_check(self.PARA, capture, "--no-bounds")[::2], (0, ""), (rid, side))

    def test_a_capture_at_another_profile_is_refused_and_no_bounds_still_holds_presence(self):
        capture = self.built()
        for record in capture:
            record["captureProfile"] = "qhd-150"
        code, out, err = self.run_check(self.PARA, capture)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("the capture is at profile qhd-150 and word.home.para.bullets was recorded at fhd-100", err)
        self.assertEqual(self.run_check(self.PARA, capture, "--no-bounds")[::2], (0, ""))
        capture = [r for r in capture if r["id"] != "write.home.para.show"]
        code, _, err = self.run_check(self.PARA, capture, "--no-bounds")
        self.assertEqual((code, err), (1, "missing word.home.para.show: no captured element for 'Show All' "
                                          "(toggleButton)\n"))

    def test_siblings_of_one_label_and_type_pair_in_order(self):
        capture = self.built()
        self.element(capture, "word.home.lines.line-2")["bounds"]["x"] += 9  # the second Line, not the first
        code, _, err = self.run_check("word.home.lines", capture)
        self.assertEqual(code, 1)
        self.assertEqual(err, "moved word.home.lines.line-2: x 28, y 10, 20 by 20 in the inventory; x 37, y 10, 20 by "
                              "20 in the capture\n")

    def test_the_parent_is_found_by_its_branch_not_by_its_label(self):
        # Home's Shadow menu lost an item and Insert's, of the same label and type, did not.
        capture = [r for r in self.built() if r["id"] != "write.home.fx.shadow.inner"]
        code, out, err = self.run_check("word.home.fx.shadow", capture)
        self.assertEqual((code, err), (1, "missing word.home.fx.shadow.inner: no captured element for 'Inner' "
                                          "(menuItem)\n"))
        self.assertEqual(self.run_check("word.insert.fx.shadow", capture),
                         (0, self.counts("word.insert.fx.shadow", 2, 2), ""))
        # The branch itself is missing: Insert's Effects group is not in the capture, Home's still is.
        capture = [r for r in self.built() if not r["id"].startswith("write.insert.fx")]
        code, out, err = self.run_check("word.insert.fx.shadow", capture)
        self.assertEqual(code, 1)
        self.assertEqual(err, "missing word.insert.fx.shadow: the capture does not hold its ancestor word.insert.fx, "
                              "so nothing under it was compared\n")
        self.assertEqual(out, self.counts("word.insert.fx.shadow", 2, 0, missing=1))
        capture = [r for r in self.built() if not r["id"].startswith("write.home.fx.shadow")]
        code, _, err = self.run_check("word.home.fx.shadow", capture)
        self.assertEqual((code, err), (1, "missing word.home.fx.shadow: the capture does not hold it, so nothing "
                                          "under it was compared\n"))

    def test_a_level_that_cannot_be_told_apart_is_refused_not_guessed(self):
        # View has two Macros groups in the inventory; the capture shows one, and nothing says which.
        capture = [r for r in self.built() if not r["id"].startswith("write.view.macros-2")]
        for parent in ("word.view.macros", "word.view.macros-2"):
            code, out, err = self.run_check(parent, capture)
            self.assertEqual((code, out), (2, ""), parent)
            self.assertIn(f"{parent} cannot be told apart in the capture: the inventory holds 2 with its label "
                          f"and type at that level and the capture holds 1", err)
        self.assertEqual(self.run_check("word.view.macros-2", self.built())[0], 0)  # both there: paired in order

    def test_a_second_element_of_the_parents_identity_in_the_capture_is_refused_not_chosen(self):
        # The built app shows two Paragraph groups where the inventory holds one. The added one is whole and comes
        # first; the original has lost Sort. Choosing the first would pass a group that lost a control.
        capture = [r for r in self.built() if r["id"] != "write.home.para.sort"]
        for record in self.built():
            if record["id"] == "write.home.para" or record.get("parent") == "write.home.para":
                twin = dict(record, id=record["id"].replace("write.home.para", "write.home.para-twin"))
                if "parent" in twin:
                    twin["parent"] = twin["parent"].replace("write.home.para", "write.home.para-twin")
                if twin["id"] == "write.home.para-twin":
                    twin["order"] = -1
                capture.append(twin)
        code, out, err = self.run_check(self.PARA, capture)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("word.home.para cannot be told apart in the capture: the inventory holds 1 with its label and "
                      "type at that level and the capture holds 2; give the built element a uiaId of its own", err)
        # The same for a level above the parent, and for an identity that is a uiaId: two Home tabs.
        capture = self.built()
        capture.append(dict(self.element(capture, "word.home"), id="write.home-twin", order=-1))
        for parent in ("word.home", self.PARA, "word.home.fx.shadow"):
            code, out, err = self.run_check(parent, capture)
            self.assertEqual((code, out), (2, ""), parent)
            self.assertIn("word.home cannot be told apart in the capture: the inventory holds 1 with its uiaId at "
                          "that level and the capture holds 2", err)
        self.assertEqual(self.run_check("word.insert.fx.shadow", capture)[0], 0)  # another branch is not touched

    def test_a_place_is_the_pair_before_and_the_pair_after(self):
        # A, X, B, D in the inventory and A, Y, D, B in the capture: X was removed, Y added and B and D swapped.
        # X and Y both follow A, and that alone does not make Y a renamed X.
        self.records.append(rec("word.home.seq", "group", "Sequence", "word.home", order=3))
        for order, label in enumerate("AXBD"):
            self.records.append(rec(f"word.home.seq.{label.lower()}", "control", label, "word.home.seq", order=order,
                                    controlType="button"))
        self.write_inventory()
        capture = self.built()
        self.element(capture, "word.home.seq.x")["label"] = "Y"
        self.element(capture, "word.home.seq.b")["order"] = 3
        self.element(capture, "word.home.seq.d")["order"] = 2
        code, out, err = self.run_check("word.home.seq", capture, "--no-bounds")
        self.assertEqual(code, 1)
        self.assertNotIn("renamed", err)
        self.assertIn("missing word.home.seq.x: no captured element for 'X' (button)", err)
        self.assertIn("extra write.home.seq.x: 'Y' (button)", err)
        self.assertEqual(err.count("reordered "), 1)
        self.assertEqual(out, self.counts("word.home.seq", 4, 3, missing=1, extra=1, reordered=1))
        # With its neighbours where they were, the same change of label is a rename, at either end too.
        for label in "AXD":
            capture = self.built()
            self.element(capture, f"word.home.seq.{label.lower()}")["label"] = "Y"
            code, out, err = self.run_check("word.home.seq", capture, "--no-bounds")
            self.assertEqual((code, err), (1, f"renamed word.home.seq.{label.lower()}: '{label}' in the inventory, "
                                              f"'Y' in the capture" + chr(10)), label)

    def test_a_record_the_pairing_cannot_use_is_refused_on_either_side(self):
        for change, said in (({"uiaId": ["bad"]}, "record 1 has a `uiaId` that is not text"),
                             ({"label": {"text": "Sort"}}, "record 1 has a `label` that is not text"),
                             ({"controlType": 7}, "record 1 has a `controlType` that is not text"),
                             ({"kind": ["control"]}, "record 1 has a `kind` that is not text"),
                             ({"parent": 5}, "record 1 has a `parent` that is not text"),
                             ({"captureProfile": 100}, "record 1 has a `captureProfile` that is not text"),
                             ({"id": 12}, "record 1 has no `id` that is text"),
                             ({"id": ""}, "record 1 has no `id` that is text"),
                             ({"id": None}, "record 1 has no `id` that is text")):
            capture = self.built()
            capture[0].update(change)
            code, out, err = self.run_check(self.PARA, capture)
            self.assertEqual((code, out), (2, ""), said)
            self.assertIn(said, err)
        code, out, err = self.run_check(self.PARA, [{"id": "bad", "uiaId": ["bad"]}])  # the reviewer's capture
        self.assertEqual((code, out), (2, ""))
        self.assertIn("record 1 has a `uiaId` that is not text", err)
        capture = self.built()
        capture.append(dict(capture[3]))
        code, out, err = self.run_check(self.PARA, capture)
        self.assertEqual((code, out), (2, ""))
        self.assertIn(f"record {len(capture)} has the `id` of an earlier record ({capture[3]['id']})", err)
        capture = self.built()
        next(r for r in self.records if r["id"] == "word.view.macros")["label"] = ["Macros"]
        self.write_inventory()
        code, out, err = self.run_check(self.PARA, capture)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("the inventory's record word.view.macros has a `label` that is not text", err)
        self.records = inventory()
        self.records[1]["parent"] = "word.home.para.sort"  # the group under its own child
        self.write_inventory()
        code, out, err = self.run_check(self.PARA, capture)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("is its own ancestor in the inventory", err)

    def test_inputs_that_cannot_be_compared_are_refused(self):
        good = self.built()
        for parent, capture, argv, said in (
                ("word.nothing", good, (), "--parent word.nothing is not a record of the inventory"),
                ("word.home.para.sort", good, (), "--parent word.home.para.sort has no children in the inventory"),
                (self.PARA, "{not json", (), "cannot be read"),
                (self.PARA, "{}", (), "is not a JSON array of records"),
                (self.PARA, "[1, 2]", (), "is not a JSON array of records"),
                (self.PARA, good, ("--tolerance", "-1"), "--tolerance -1 is not a whole number of pixels from 0 up"),
                (self.PARA, good, ("--tolerance", "1.5"), "--tolerance 1.5 is not a whole number"),
                (self.PARA, good, ("--tolerance", "two"), "--tolerance two is not a whole number")):
            code, out, err = self.run_check(parent, capture, *argv)
            self.assertEqual((code, out), (2, ""), said)
            self.assertIn(said, err)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cl.main(["--parent", self.PARA, "--capture", str(self.root / "no-such.json")], root=self.root)
        self.assertEqual(code, 2)
        self.assertIn("cannot be read", err.getvalue())
        (self.root / "design" / "inventory" / "word" / "ribbon.json").write_text("{not json", encoding="utf-8")
        code, _, err = self.run_check(self.PARA, good)
        self.assertEqual(code, 2)
        self.assertIn("the inventory cannot be read", err)

    def test_text_from_either_file_is_printed_escaped_and_a_closed_reader_does_not_change_the_verdict(self):
        capture = [r for r in self.built() if r["id"] != "write.home.para.sort"]
        capture.append({"id": "write.home.para.\x1b[2J", "kind": "control", "label": "Clear\x1b[2J", "order": 7,
                        "controlType": "button", "parent": "write.home.para", "captureProfile": PROFILE})
        code, _, err = self.run_check(self.PARA, capture)
        self.assertEqual(code, 1)
        self.assertNotIn("\x1b", err)
        self.assertIn("extra write.home.para.\\x1b[2J: 'Clear\\x1b[2J' (button)", err)

        class Closed(io.StringIO):
            def write(self, _text):
                raise BrokenPipeError(32, "Broken pipe")
        path = self.root / "capture.json"
        path.write_text(json.dumps(capture), encoding="utf-8")
        err, stand_in = io.StringIO(), Closed()
        with contextlib.redirect_stdout(stand_in), contextlib.redirect_stderr(err):
            code = cl.main(["--parent", self.PARA, "--capture", str(path)], root=self.root)
            import sys
            replaced = sys.stdout
        if replaced is not stand_in:
            replaced.close()
        self.assertEqual(code, 1)  # the findings were already on stderr, and the exit code is the comparison's
        self.assertIn("missing word.home.para.sort", err.getvalue())


class Reference(unittest.TestCase):
    def test_the_reference_documents_the_command(self):
        text = (SCRIPTS.parent / "design" / "inventory" / "REFERENCE.md").read_text(encoding="utf-8")
        section = text.split("\n## Layout check\n", 1)[1].split("\n## ", 1)[0]
        for said in ("scripts/check-layout.py", "--parent", "--capture", "--tolerance", "--no-bounds", "`missing`",
                     "`extra`", "`renamed`", "`retyped`", "`reordered`", "`moved`", "`resized`", "`unmeasured`",
                     "2 pixels"):
            self.assertIn(said, section)


if __name__ == "__main__":
    unittest.main()
