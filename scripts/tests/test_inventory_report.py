# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/inventory-report.py: the parity scoreboard over a fixture inventory and TODO tree (D02 T01 §18)."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import inventory_claims  # noqa: E402  (scripts/lib is put on the path just above)

spec = importlib.util.spec_from_file_location("inventory_report", SCRIPTS / "inventory-report.py")
ir = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ir)
spec = importlib.util.spec_from_file_location("check_design_doc", SCRIPTS / "check-design-doc.py")
cdd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cdd)

COLUMNS = ["idMso", "controlType", "placement", "tabSet", "tab", "group", "parent", "secondaryParent", "policyId"]


def row(mso, ctype, placement, tab=None):
    return [mso, ctype, placement, None, tab, None, None, None, 1]


def rec(rid, kind, parent=None, **extra):
    r = {"id": rid, "app": rid.split(".")[0], "kind": kind, "label": rid.rsplit(".", 1)[-1], **extra}
    if parent:
        r["parent"] = parent
    return r


RIBBON = [rec("word.home", "tab", idMso="TabHome"), rec("word.home.font", "group", "word.home", idMso="GroupFont"),
          rec("word.home.font.bold", "control", "word.home.font", idMso="Bold", controlType="toggleButton"),
          rec("word.home.font.italic", "control", "word.home.font", idMso="Italic", controlType="toggleButton"),
          rec("word.review", "tab", idMso="TabReviewWord"),
          rec("word.review.protect.block-authors", "control", "word.review", idMso="BlockAuthorsMenu",
              controlType="menu"),
          rec("word.developer", "tab", idMso="TabDeveloper"),
          rec("word.developer.protect.block-authors", "control", "word.developer", idMso="BlockAuthorsMenu",
              controlType="menu")]
BASELINE = [row("TabHome", "tab", "coreTab"), row("TabReviewWord", "tab", "coreTab"),
            row("TabDeveloper", "tab", "coreTab"), row("TabSyntex", "tab", "coreTab"),
            row("GroupFont", "group", "coreTab", "TabHome"), row("Bold", "toggleButton", "coreTab", "TabHome"),
            row("Italic", "toggleButton", "coreTab", "TabHome"),
            row("BlockAuthorsMenu", "menu", "coreTab", "TabReviewWord"),
            row("BlockAuthorsMenu", "menu", "coreTab", "TabDeveloper"),
            row("SyntexThing", "button", "coreTab", "TabSyntex"), row("CopyMenu", "button", "contextMenu"),
            row("FileSave", "button", "quickAccessToolbar"), row(None, "button", "coreTab", "TabHome")]


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        inv = self.root / "design" / "inventory"
        for app, files in {"word": {"ribbon.json": RIBBON, "baseline.json": {"columns": COLUMNS, "rows": BASELINE}},
                           "shell": {"chrome.json": [rec("shell.qat.save", "control", idMso="FileSave",
                                                         controlType="button")]},
                           "excel": {"baseline.json": {"columns": COLUMNS, "rows": [row("TabHome", "tab", "coreTab")]}}
                           }.items():
            (inv / app).mkdir(parents=True)
            for name, data in files.items():
                (inv / app / name).write_text(json.dumps(data), encoding="utf-8")
        self.sections = []  # the TODO graph's sections, as the report reads them
        patcher = mock.patch.object(ir.todo_graph, "graph", lambda root: {s.ref: s for s in self.sections})
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def run_report(self, *argv, write=None):
        out, err = io.StringIO(), io.StringIO()
        kwargs = {"write": write} if write else {}
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ir.main(list(argv), root=self.root, **kwargs)
        return code, out.getvalue(), err.getvalue()

    def edit_ribbon(self, keep):
        path = self.root / "design" / "inventory" / "word" / "ribbon.json"
        path.write_text(json.dumps([r for r in RIBBON if keep(r)]), encoding="utf-8")

    @property
    def report(self):
        return self.root / ir.REPORT


class Counts(Fixture):
    def test_records_are_counted_per_app_and_kind_and_a_baseline_only_app_is_pending(self):
        code, out, _ = self.run_report()
        self.assertEqual(code, 0)
        self.assertIn("| word | control | 4 | 0 |", out)
        self.assertIn("| shell | control | 1 | 0 |", out)
        self.assertIn("| excel | 1 | pending inventory |", out)
        self.assertNotIn("| excel | tab", out)

    def test_the_baseline_states(self):
        code, out, _ = self.run_report()
        # 13 rows: 3 tabs + font, bold, italic, 2 block-authors and the QAT row captured (9); TabSyntex and the row on
        # it documented absent (2); the context menu row pending (1); the row with no idMso apart (1)
        self.assertIn("| word | 13 | 9 | 2 | 0 | 1 | 1 |", out)
        self.assertIn("| word | contextMenu | 1 |", out)

    def test_a_removed_control_is_named_and_a_documented_absence_is_not(self):
        self.edit_ribbon(lambda r: r["id"] != "word.home.font.italic")
        _, out, _ = self.run_report("--missing")
        self.assertEqual(out, "word\tItalic\ttoggleButton\tTabHome\n")
        self.assertNotIn("Syntex", out)
        self.assertNotIn("CopyMenu", out)

    def test_each_occurrence_is_matched_under_its_own_tab(self):
        self.edit_ribbon(lambda r: r["id"] != "word.developer.protect.block-authors")
        _, out, _ = self.run_report("--missing")
        self.assertEqual(out, "word\tBlockAuthorsMenu\tmenu\tTabDeveloper\n")  # Review's copy still matches

    def test_a_quick_access_row_matches_the_shells_record(self):
        _, out, _ = self.run_report("--missing")
        self.assertEqual(out, "")


class Implemented(Fixture):
    def section(self, ref, done, body):
        self.sections.append(SimpleNamespace(ref=ref, done=done, body=body))

    def bold_count(self):
        _, out, _ = self.run_report("--app", "word", "--kind", "control")
        return out

    def test_a_verified_sections_claim_counts_and_unstamping_takes_it_out(self):
        self.section("D09 T01 §1", True, "> **Implements:** `word.home.font.bold`")
        self.assertIn("4 records, 1 implemented", self.bold_count())
        self.sections[0].done = False  # unstamped
        self.assertIn("4 records, 0 implemented", self.bold_count())

    def test_claims_that_do_not_count(self):
        self.section("D09 T01 §1", False, "> **Implements:** `word.home.font.bold`")  # not stamped
        self.section("D09 T01 §2", False, "- [x] Build `word.home.font.bold`.\n- [x] Test it.")  # ticked, no stamp
        self.section("D09 T01 §3", True, "Builds `word.home.font.italic` (an example, not a claim).")
        self.assertIn("4 records, 0 implemented", self.bold_count())

    def test_a_record_claimed_twice_counts_once(self):
        self.section("D09 T01 §1", True, "> **Implements:** `word.home.font.bold` `word.home.font.italic`")
        self.section("D09 T01 §2", True, "> **Implements:** `word.home.font.bold`")
        self.assertIn("4 records, 2 implemented", self.bold_count())
        self.assertEqual(inventory_claims.implemented(self.sections)["word.home.font.bold"],
                         ["D09 T01 §1", "D09 T01 §2"])
        _, out, _ = self.run_report()
        self.assertIn("| word | control | 4 | 2 |", out)


class Filters(Fixture):
    def cite(self, text):
        path = self.root / "spec.md"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def test_a_spec_citing_half_the_tabs_reports_fifty_percent(self):
        code, out, _ = self.run_report("--app", "word", "--kind", "tab", "--cited-in", self.cite(
            "Builds word.home and `word.review`."))
        self.assertEqual(code, 0)
        self.assertIn("cited in", out)
        self.assertIn(": 2 of 3 (67 percent)", out)
        _, out, _ = self.run_report("--app", "word", "--kind", "tab", "--cited-in", self.cite("Only word.home."))
        self.assertIn(": 1 of 3 (33 percent)", out)
        self.edit_ribbon(lambda r: r["id"] != "word.developer" and "developer" not in r["id"])
        _, out, _ = self.run_report("--app", "word", "--kind", "tab", "--cited-in", self.cite("Only word.home."))
        self.assertIn(": 1 of 2 (50 percent)", out)

    def test_a_citation_is_a_whole_token(self):
        self.assertTrue(ir.cited("See word.home.font.bold.", "word.home.font.bold"))
        self.assertFalse(ir.cited("See word.home.font.bold-2.", "word.home.font.bold"))
        self.assertFalse(ir.cited("See word.home.font.boldness", "word.home.font.bold"))
        self.assertFalse(ir.cited("See xword.home", "word.home"))
        self.assertFalse(ir.cited("See word.home.font", "word.home"))

    def test_an_empty_filter_and_the_control_types(self):
        code, out, _ = self.run_report("--app", "word", "--kind", "dialog", "--cited-in", self.cite("x"))
        self.assertEqual(code, 0)
        self.assertIn(": 0 of 0 (no matching record)", out)
        _, out, _ = self.run_report("--app", "word", "--kind", "control", "--cited-in",
                                    self.cite("word.home.font.bold"), "--control-types")
        self.assertIn("  toggleButton: 1 cited, 1 not", out)
        self.assertIn("  menu: 0 cited, 2 not", out)

    def test_a_filtered_run_never_writes_the_report(self):
        self.run_report()
        before = self.report.read_bytes()
        self.edit_ribbon(lambda r: r["id"] != "word.home.font.italic")
        for argv in (("--app", "word"), ("--kind", "tab"), ("--missing",), ("--cited-in", self.cite("x"))):
            self.run_report(*argv)
            self.assertEqual(self.report.read_bytes(), before, argv)


class Publication(Fixture):
    def test_the_report_is_written_read_back_and_regenerates_to_the_same_bytes(self):
        code, _, _ = self.run_report()
        self.assertEqual(code, 0)
        first = self.report.read_bytes()
        self.assertIn(b"| word | control | 4 | 0 |", first)
        self.assertEqual(cdd.check(first.decode("utf-8"), []), [])  # the design-document rules, rows of 120 at most
        self.run_report()
        self.assertEqual(self.report.read_bytes(), first)

    def test_check_finds_a_stale_report(self):
        self.run_report()
        self.assertEqual(self.run_report("--check")[0], 0)
        self.edit_ribbon(lambda r: r["id"] != "word.home.font.italic")
        code, _, err = self.run_report("--check")
        self.assertEqual(code, 1)
        self.assertIn("design/inventory/COVERAGE.md is stale", err)

    def test_a_failed_write_keeps_the_previous_report(self):
        self.run_report()
        before = self.report.read_bytes()
        self.edit_ribbon(lambda r: r["id"] != "word.home.font.italic")

        def fails(path, data):
            raise OSError("disk full")
        code, _, err = self.run_report(write=fails)
        self.assertEqual(code, 1)
        self.assertIn("was not written (disk full); the previous copy is kept", err)
        self.assertEqual(self.report.read_bytes(), before)

    def test_a_failed_replace_keeps_the_previous_report(self):
        self.run_report()
        before = self.report.read_bytes()
        self.edit_ribbon(lambda r: r["id"] != "word.home.font.italic")
        with mock.patch.object(ir.todo_graph.os, "replace", side_effect=OSError("replace refused")):
            code, _, err = self.run_report()
        self.assertEqual(code, 1)
        self.assertEqual(self.report.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in self.report.parent.iterdir()), ["COVERAGE.md", "excel", "shell",
                                                                                "word"])  # no temporary left


class Committed(unittest.TestCase):
    def test_the_committed_report_is_current_and_well_formed(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ir.main(["--check"])
        self.assertEqual(code, 0, err.getvalue())


if __name__ == "__main__":
    unittest.main()
