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
WINDOWS = ("explorer", "mailitem", "taskitem")
NAMES = [f"{app}controls.xlsx" for app in imp.APPS] + [f"outlook{w}controls.xlsx" for w in WINDOWS]
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
        for window in WINDOWS:
            workbook(self.src / f"outlook{window}controls.xlsx", WORD[3:5] if window == "mailitem" else WORD[:1])
        self.sources = Path(self.tmp.name) / "baseline-sources.json"

    def seal(self):
        """The manifest for the fixture as it stands, so each test reaches the refusal it is about."""
        blobs = {n: imp.git_blob(self.src / n) if (self.src / n).is_file() else "0" * 40 for n in NAMES}
        self.sources.write_text(json.dumps({"commit": COMMIT, "blobs": blobs}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *extra, seal=True):
        if seal:
            self.seal()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = imp.main([str(self.src), *extra], inventory=self.inv, sources=self.sources)
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
        expected = [w for w in WINDOWS for _ in range(2 if w == "mailitem" else 1)]
        self.assertEqual([r["window"] for r in rows], expected)

    def test_outlook_window_set_must_match_the_manifest(self):
        (self.src / "outlooktaskitemcontrols.xlsx").unlink()
        self.assertEqual(self.run_main()[0], 2)
        workbook(self.src / "outlooktaskitemcontrols.xlsx", WORD[:1])
        for extra in ("outlookmail-readcontrols.xlsx", "outlookcontrols.xlsx"):
            workbook(self.src / extra, WORD[:1])
            self.assertEqual(self.run_main()[0], 1, extra)
            (self.src / extra).unlink()
        self.assertEqual(self.run_main()[0], 0)

    def test_an_edited_workbook_is_not_the_upstream_file(self):
        self.seal()
        workbook(self.src / "wordcontrols.xlsx", WORD[:-1])
        code, out = self.run_main(seal=False)
        self.assertEqual(code, 1)
        self.assertIn("git blob id differs", out)

    def test_the_manifest_must_pin_the_source_folder_commit(self):
        self.seal()
        doc = json.loads(self.sources.read_text(encoding="utf-8"))
        self.sources.write_text(json.dumps(dict(doc, commit="f" * 40)), encoding="utf-8")
        self.assertEqual(self.run_main(seal=False)[0], 1)

    def test_non_text_cells_are_never_identifiers(self):
        for bad in ((True, "button", "None (Core Tab)", "TabHome", None, None, None, 1),
                    ("X", True, "None (Core Tab)", "TabHome", None, None, None, 1),
                    ("X", "button", True, "TabHome", None, None, None, 1),
                    ("X", "button", "None (Core Tab)", "TabHome", None, 7, None, 1)):
            workbook(self.src / "wordcontrols.xlsx", WORD + [bad])
            self.assertEqual(self.run_main()[0], 1, bad)

    def test_a_second_worksheet_stops_the_import(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(HEADER)
        for r in WORD:
            ws.append(list(r) + [None])
        wb.create_sheet("more").append(["Hidden", "button"])
        wb.save(self.src / "wordcontrols.xlsx")
        self.assertEqual(self.run_main()[0], 1)

    def test_check_compares_bytes(self):
        self.run_main()
        path = self.inv / "word" / "baseline.json"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(self.run_main("--check")[0], 1)

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
                    ("X", "button", "None (Core Tab)", "TabHome", None, None, None, -1),
                    ("X", "unexpected prose (button)", "None (Core Tab)", "TabHome", None, None, None, 1),
                    ("None (Core Tab)", "button", "None (Core Tab)", "TabHome", None, None, None, 1),
                    ("X", "button", "None (Core Tab)", "TabHome", None, "None (Core Tab)", None, 1),
                    ("X", "button", "None (Core Tab)", "None (Context Menu)", None, None, None, 1),
                    ("X", "button", "None (Core Tab)", "TabHome", "=CONCAT(1)", None, None, 1),
                    ("X", None, "None (Core Tab)", "TabHome", None, None, None, 1)):
            workbook(self.src / "wordcontrols.xlsx", WORD + [bad])
            code, out = self.run_main()
            self.assertEqual(code, 1, (bad, out))
            self.assertFalse((self.inv / "word" / "baseline.json").exists(), bad)

    def test_a_value_only_in_the_extra_column_stops_the_import(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(HEADER)
        for r in WORD:
            ws.append(list(r) + [None])
        ws.append([None] * len(imp.HEADER) + ["stray"])
        wb.save(self.src / "wordcontrols.xlsx")
        self.assertEqual(self.run_main()[0], 1)

    def test_a_formula_only_in_the_extra_column_stops_the_import(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(HEADER)
        for r in WORD:
            ws.append(list(r) + [None])
        ws.append([None] * len(imp.HEADER) + ['="stray"'])
        wb.save(self.src / "wordcontrols.xlsx")
        self.assertEqual(self.run_main()[0], 1)

    def test_a_blank_tab_set_is_no_tab_set(self):
        workbook(self.src / "wordcontrols.xlsx", WORD + [("Y", "button", " ", None, None, None, None, 3)])
        self.run_main()
        rows, _ = self.baseline("word")
        self.assertEqual([(r["placement"], r["tabSet"]) for r in rows if r["idMso"] == "Y"], [(None, None)])

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

    def complete(self, outlook_windows=WINDOWS, drop=None, empty=None):
        row = ["Bold", "toggleButton", "coreTab", None, "TabHome", "GroupFont", None, None, 113]
        blobs = {n: "0" * 40 for n in NAMES}
        (self.inv / ci.SOURCES).write_text(json.dumps({"commit": COMMIT, "blobs": blobs}), encoding="utf-8")
        for app in ci.APPS:
            (self.inv / app).mkdir(exist_ok=True)
            if app == drop:
                (self.inv / app / "baseline.json").unlink(missing_ok=True)
                continue
            if app == "outlook":
                doc = self.doc([[w] + row for w in outlook_windows], ["window"] + imp.COLUMNS)
            else:
                doc = self.doc([] if app == empty else [row])
            (self.inv / app / "baseline.json").write_text(json.dumps(doc), encoding="utf-8")
        return ci.check([str(self.inv)], inventory=self.inv)

    def test_the_whole_inventory_needs_every_baseline_and_window(self):
        self.assertEqual(self.complete(), [])
        self.assertTrue(any("visio" in p and "missing baseline" in p for p in self.complete(drop="visio")))
        self.assertTrue(any("no rows" in p for p in self.complete(empty="excel")))
        self.assertTrue(any("no rows for the windows ['taskitem']" in p
                            for p in self.complete(outlook_windows=WINDOWS[:2])))
        self.assertTrue(any("not a window in the manifest" in p
                            for p in self.complete(outlook_windows=WINDOWS + ("invented",))))

    def test_a_baseline_from_another_commit_fails_against_the_manifest(self):
        self.complete()
        doc = self.doc([["Bold", "toggleButton", "coreTab", None, "TabHome", None, None, None, 1]])
        (self.inv / "word" / "baseline.json").write_text(json.dumps(dict(doc, source="baseline:" + "f" * 40)),
                                                         encoding="utf-8")
        self.assertTrue(any("not the manifest commit" in p for p in ci.check([str(self.inv)], inventory=self.inv)))

    def test_the_repository_records_its_baseline_source(self):
        self.assertTrue((ci.INVENTORY / ci.SOURCES).is_file())

    def test_the_reference_documents_the_baseline_commit(self):
        commit = json.loads((ci.INVENTORY / ci.SOURCES).read_text(encoding="utf-8"))["commit"]
        text = (ci.INVENTORY / "REFERENCE.md").read_text(encoding="utf-8")
        self.assertIn("## Baseline", text)
        section = text[text.index("## Baseline"):]
        self.assertIn(commit, section)
        # What the section must keep explaining: the manifest, the Outlook windows, null ids and how to refresh.
        for obligation in ("baseline-sources.json", "`mailitem` (compose)", "null `idMso`", "`baselineMissing`",
                           "To refresh:", "--check"):
            self.assertIn(obligation, section)

    def test_baseline_rows_are_not_inventory_records(self):
        rec = {"id": "word.home", "app": "word", "kind": "tab", "label": "Home"}
        (self.inv / "word" / "ribbon.json").write_text(json.dumps([rec]), encoding="utf-8")
        self.assertEqual(self.problems(self.doc([["Bold", "toggleButton", "coreTab", None, "TabHome", None, None,
                                                  None, 1]])), [])


if __name__ == "__main__":
    unittest.main()
