"""scripts/import-office-ids.py: workbook rows become baseline rows in order, facts only, with refusals."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

import openpyxl

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("import_office_ids", SCRIPTS / "import-office-ids.py")
imp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(imp)
spec = importlib.util.spec_from_file_location("check_inventory", SCRIPTS / "check-inventory.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

COMMIT = "0123456789abcdef0123456789abcdef01234567"
HEADER = list(imp.HEADER) + ["Column1"]
WORD = [
    ("AutoSaveSwitch", "toggleButton", "None (Quick Access Toolbar)", "Quick Access Toolbar", None, None, None, 27520),
    ("GroupClipboard", "group", "None (Core Tab)", "TabHome", None, None, None, 12597),
    ("PasteMenu", "splitButton", "None (Core Tab)", "TabHome", "GroupClipboard", None, None, 15502),
    ("Paste", "button", "None (Core Tab)", "TabHome", "GroupClipboard", "PasteMenu", None, 22),
    ("GroupFont", "group", "None (Core Tab)", "TabHome", None, None, None, 12598),
    ("Bold", "toggleButton", "None (Core Tab)", "TabHome", "GroupFont", None, None, 113),
    ("FontDialog", "button (dialogBoxLauncher)", "None (Core Tab)", "TabHome", "GroupFont", None, None, 926),
    ("GroupParagraph", "group", "None (Core Tab)", "TabHome", None, None, None, 12599),
    (None, "gallery", "None (Core Tab)", "TabHome", "GroupParagraph", None, None, 33502),
    ("_3DRotationGallery", "gallery", "TabSetDrawingTools", "TabDrawingToolsFormat", "Group3DEffects", None, None, 9),
    ("TextMenu", "contextMenu", "None (Context Menu)", "None (Context Menu)", "None (Context Menu)", None, None, 5),
]


def workbook(path, rows, header=HEADER):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header)
    for r in rows:
        ws.append(list(r) + [None])
    wb.save(path)


class Import(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = Path(self.tmp.name) / COMMIT
        self.src.mkdir()
        self.inv = Path(self.tmp.name) / "inventory"
        for app in imp.APPS:
            workbook(self.src / f"{app}controls.xlsx", WORD)
        workbook(self.src / "outlookexplorercontrols.xlsx", WORD[:3])
        workbook(self.src / "outlookmailitemcontrols.xlsx", WORD[3:5])

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = imp.main([str(self.src), *extra], inventory=self.inv)
        return code, out.getvalue() + err.getvalue()

    def baseline(self, app):
        data = json.loads((self.inv / app / "baseline.json").read_text(encoding="utf-8"))
        return [dict(zip(data["columns"], r)) for r in data["rows"]], data

    def test_rows_keep_workbook_order_and_group_order(self):
        self.assertEqual(self.run_main()[0], 0)
        rows, data = self.baseline("word")
        self.assertEqual(data["source"], f"baseline:{COMMIT}")
        self.assertEqual([r["idMso"] for r in rows], [r[0] for r in WORD])
        groups = []
        for r in rows:
            if r["tab"] == "TabHome" and r["group"] and r["group"] not in groups:
                groups.append(r["group"])
        self.assertEqual(groups, ["GroupClipboard", "GroupFont", "GroupParagraph"])

    def test_values_are_facts_in_our_own_terms(self):
        self.run_main()
        rows, _ = self.baseline("word")
        by_id = {r["idMso"]: r for r in rows}
        self.assertEqual((by_id["AutoSaveSwitch"]["placement"], by_id["AutoSaveSwitch"]["tab"]), ("quickAccessToolbar", None))
        self.assertEqual(by_id["FontDialog"]["controlType"], "dialogBoxLauncher")
        self.assertEqual((by_id["_3DRotationGallery"]["placement"], by_id["_3DRotationGallery"]["tabSet"]),
                         ("contextualTab", "TabSetDrawingTools"))
        self.assertEqual((by_id["TextMenu"]["placement"], by_id["TextMenu"]["tab"], by_id["TextMenu"]["group"]),
                         ("contextMenu", None, None))
        self.assertEqual([r["policyId"] for r in rows if r["idMso"] is None], [33502])
        text = (self.inv / "word" / "baseline.json").read_text(encoding="utf-8")
        self.assertNotIn("None (", text)
        self.assertNotIn("Quick Access Toolbar", text)

    def test_outlook_windows_merge_under_their_window(self):
        self.run_main()
        rows, data = self.baseline("outlook")
        self.assertEqual(data["columns"][0], "window")
        self.assertEqual([r["window"] for r in rows], ["explorer"] * 3 + ["mailitem"] * 2)

    def test_written_baselines_pass_the_inventory_checker(self):
        self.run_main()
        self.assertEqual(ci.check([str(self.inv)], inventory=self.inv), [])

    def test_check_reports_stale_then_up_to_date(self):
        code, out = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("stale", out)
        self.run_main()
        self.assertEqual(self.run_main("--check")[0], 0)

    def test_unmapped_wording_and_bad_values_stop_the_import(self):
        for bad in (("X", "button", "None (Somewhere New)", "TabHome", None, None, None, 1),
                    ("Has space", "button", "None (Core Tab)", "TabHome", None, None, None, 1),
                    ("X", "button", "None (Core Tab)", "TabHome", "see https://example.com", None, None, 1),
                    ("X", "button", "None (Core Tab)", "TabHome", None, None, None, "12"),
                    ("X", None, "None (Core Tab)", "TabHome", None, None, None, 1)):
            workbook(self.src / "wordcontrols.xlsx", WORD + [bad])
            code, out = self.run_main()
            self.assertEqual(code, 1, (bad, out))
            self.assertFalse((self.inv / "word" / "baseline.json").exists(), bad)

    def test_unexpected_columns_stop_the_import(self):
        workbook(self.src / "wordcontrols.xlsx", WORD, header=HEADER[:-1] + ["Description"])
        self.assertEqual(self.run_main()[0], 1)

    def test_missing_workbook_exits_2(self):
        (self.src / "visiocontrols.xlsx").unlink()
        self.assertEqual(self.run_main()[0], 2)

    def test_source_folder_must_name_the_commit(self):
        renamed = self.src.with_name("latest")
        self.src.rename(renamed)
        self.src = renamed
        self.assertEqual(self.run_main()[0], 1)


class Checker(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.inv = Path(self.tmp.name) / "inventory"
        (self.inv / "word").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def problems(self, doc, app="word"):
        (self.inv / app).mkdir(exist_ok=True)
        (self.inv / app / "baseline.json").write_text(json.dumps(doc), encoding="utf-8")
        return ci.check([str(self.inv)], inventory=self.inv)

    def doc(self, rows, columns=None):
        return {"source": f"baseline:{COMMIT}", "columns": columns or imp.COLUMNS, "rows": rows}

    def test_valid_baseline_passes(self):
        self.assertEqual(self.problems(self.doc([["Bold", "toggleButton", "coreTab", None, "TabHome", "GroupFont",
                                                  None, None, 113]])), [])

    def test_bad_cells_columns_and_envelope_fail(self):
        good = ["Bold", "toggleButton", "coreTab", None, "TabHome", "GroupFont", None, None, 113]
        cases = {
            "placement": self.doc([good[:2] + ["sideways"] + good[3:]]),
            "does not match": self.doc([good[:5] + ["https://example.com"] + good[6:]]),
            "cells, expected 9": self.doc([good[:-1]]),
            "expected integer": self.doc([good[:-1] + ["113"]]),
            "controlType": self.doc([good[:1] + [None] + good[2:]]),
            "columns": self.doc([good], columns=list(reversed(imp.COLUMNS))),
            "source": dict(self.doc([good]), source="baseline:main"),
            "unknown field labels": dict(self.doc([good]), labels=["Bold"]),
        }
        for expected, doc in cases.items():
            problems = self.problems(doc)
            self.assertTrue(any(expected in p for p in problems), (expected, problems))

    def test_outlook_baseline_needs_the_window_column(self):
        row = ["explorer", "Bold", "toggleButton", "coreTab", None, "TabHome", "GroupFont", None, None, 113]
        self.assertEqual(self.problems(self.doc([row], ["window"] + imp.COLUMNS), "outlook"), [])
        self.assertTrue(any("columns" in p for p in self.problems(self.doc([row[1:]]), "outlook")))

    def test_baseline_rows_are_not_inventory_records(self):
        rec = {"id": "word.home", "app": "word", "kind": "tab", "label": "Home"}
        (self.inv / "word" / "ribbon.json").write_text(json.dumps([rec]), encoding="utf-8")
        self.assertEqual(self.problems(self.doc([["Bold", "toggleButton", "coreTab", None, "TabHome", None, None,
                                                  None, 1]])), [])


if __name__ == "__main__":
    unittest.main()
