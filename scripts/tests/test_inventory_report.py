# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/inventory-report.py: the parity scoreboard over a fixture inventory and TODO tree (D02 T01 §18)."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import inventory_claims  # noqa: E402  (scripts/lib is put on the path just above)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_todo_stamp as tts  # noqa: E402  (the stamp tests' fixture makes a real stamped section)

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
            row("Bold", "toggleButton", "contextMenu"),
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
        # 14 rows: 3 tabs + font, bold, italic, 2 block-authors, the QAT row and the context menu's Bold (held by the
        # ribbon's record) captured (10); TabSyntex and the row on it documented absent (2); the context menu row no
        # record holds pending (1); the row with no idMso apart (1)
        self.assertIn("| word | 14 | 10 | 2 | 0 | 1 | 1 |", out)
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

    def test_a_row_on_no_tab_matches_any_record_of_the_app_or_the_shell(self):
        _, out, _ = self.run_report("--missing")
        self.assertEqual(out, "")  # the QAT's FileSave is the shell's; the context menu's Bold is the ribbon's
        shell = self.root / "design" / "inventory" / "shell" / "chrome.json"
        shell.write_text("[]", encoding="utf-8")
        _, out, _ = self.run_report("--missing")
        self.assertEqual(out, "word\tFileSave\tbutton\t\n")  # round 1: a row with no tab was matched only on the QAT


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


class Owners(Fixture):
    """Who the plan says builds each record (D02 T01 §22). Word's domain is authored by D09 T01 §1, the shell's by
    §2 and Excel's (a baseline and no captured record) by §3; other sections claim records."""

    WORD = [r["id"] for r in RIBBON]
    AUTHORING = {"word": "D09 T01 §1", "shell": "D09 T01 §2", "excel": "D09 T01 §3"}

    def setUp(self):
        super().setUp()
        self.authoring(self.AUTHORING)
        self.authors = {app: self.section(ref, False, "") for app, ref in self.AUTHORING.items()}

    def authoring(self, data):
        path = self.root / "design" / "inventory" / "authoring.json"
        path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")

    def section(self, ref, done, body):
        self.sections.append(SimpleNamespace(ref=ref, done=done, body=body))
        return self.sections[-1]

    def claim(self, ref, *ids, done=False):
        return self.section(ref, done, "> **Implements:** " + " ".join(f"`{i}`" for i in ids))

    def owners(self, *argv):
        return self.run_report("--owners", *argv)

    def test_a_claim_is_what_an_implements_line_names_whoever_made_it(self):
        self.claim("D09 T02 §1", "word.home.font.bold", "word.home.font.bold")       # named twice, claimed once
        self.section("D09 T02 §2", True, "- [x] Build `word.home.font.italic`.\n\nSee `word.home`, for example.")
        self.claim("D09 T02 §3", "word.home.font", done=True)
        self.assertEqual(inventory_claims.owners(self.sections),
                         {"word.home.font.bold": ["D09 T02 §1"], "word.home.font": ["D09 T02 §3"]})
        code, out, err = self.owners()
        self.assertEqual((code, err), (0, ""))
        self.assertIn("word: pending authoring (D09 T01 §1 is open): 2 of 8 records owned\n", out)
        self.assertIn("  control: 1 of 4\n", out)
        self.assertIn("  group: 1 of 1\n", out)
        self.assertNotIn("unowned control word.home.font.bold", out)
        self.assertIn("  unowned control word.home.font.italic\n", out)  # ticked in an item, claimed nowhere

    def test_every_app_is_in_one_of_three_states(self):
        self.authors["shell"].done = True
        code, out, err = self.owners()
        self.assertEqual((code, err), (0, ""))
        self.assertIn("excel: pending inventory (no captured record; D09 T01 §3 authors it)\n", out)
        self.assertIn("shell: enforced (D09 T01 §2 is stamped): 0 of 1 records owned\n", out)
        self.assertIn("word: pending authoring (D09 T01 §1 is open): 0 of 8 records owned\n", out)
        self.claim("D09 T02 §1", *self.WORD[:3])
        self.assertIn("word: pending authoring (D09 T01 §1 is open): 3 of 8 records owned\n", self.owners()[1])
        self.authors["word"].done = True  # the same fixture with that section stamped
        self.assertIn("word: enforced (D09 T01 §1 is stamped): 3 of 8 records owned\n", self.owners()[1])
        self.authors["excel"].done = True  # stamped or not, an app with no captured record is pending inventory
        self.assertIn("excel: pending inventory", self.owners()[1])

    def test_removing_a_claim_from_an_enforced_app_names_the_record(self):
        self.authors["word"].done = self.authors["shell"].done = True
        word = self.claim("D09 T02 §1", *self.WORD)
        self.claim("D09 T02 §2", "shell.qat.save")
        self.assertEqual(self.owners("--check")[::2], (0, ""))
        word.body = word.body.replace(" `word.home.font.italic`", "")
        code, out, err = self.owners("--check")
        self.assertEqual(code, 1)
        self.assertEqual(err, "refused: word: 1 record(s) no section claims on an Implements line\n"
                              "  unowned control word.home.font.italic\n")
        self.assertIn("word: enforced (D09 T01 §1 is stamped): 7 of 8 records owned\n", out)
        self.assertNotIn("unowned", out)  # with --check a refusal is on stderr alone
        code, out, err = self.owners()  # the report itself names it and refuses nothing
        self.assertEqual((code, err), (0, ""))
        self.assertIn("  unowned control word.home.font.italic\n", out)

    def test_a_pending_app_is_counted_and_an_enforced_one_refused(self):
        self.assertEqual(self.owners("--check")[::2], (0, ""))  # every record unowned, every app pending
        self.claim("D09 T02 §1", *self.WORD[:4])
        code, out, err = self.owners("--check")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("word: pending authoring (D09 T01 §1 is open): 4 of 8 records owned\n", out)
        self.assertNotIn("unowned", out)  # counted, not listed: the hook's output stays short for a pending app
        self.authors["word"].done = True
        code, _, err = self.owners("--check")
        self.assertEqual(code, 1)
        self.assertEqual(err.splitlines()[0], "refused: word: 4 record(s) no section claims on an Implements line")
        self.assertEqual(sorted(line.split()[-1] for line in err.splitlines()[1:]), sorted(self.WORD[4:]))

    def test_an_unknown_claim_and_a_double_claim_are_refused_in_every_state(self):
        self.claim("D09 T02 §1", "word.nothing")
        code, _, err = self.owners("--check")
        self.assertEqual((code, err), (1, "refused: unknown claim: word.nothing, claimed by D09 T02 §1, is not a "
                                          "record of the inventory\n"))
        self.sections.pop()
        self.claim("D09 T02 §1", "word.home.font.bold")
        self.claim("D09 T02 §2", "word.home.font.bold", done=True)
        code, _, err = self.owners("--check")
        self.assertEqual((code, err), (1, "refused: double claim: word.home.font.bold is claimed by D09 T02 §1 and "
                                          "D09 T02 §2\n"))
        code, out, err = self.owners()  # the report lists it and refuses nothing
        self.assertEqual((code, err), (0, ""))
        self.assertIn("double claim: word.home.font.bold is claimed by D09 T02 §1 and D09 T02 §2\n", out)

    def test_a_claim_is_printed_escaped(self):
        self.claim("D09 T02 §1", "word.\x1b[2Jgone")
        _, _, err = self.owners("--check")
        self.assertIn("unknown claim: word.\\x1b[2Jgone, claimed by", err)
        self.assertNotIn("\x1b", err)

    def test_one_app_can_be_brought_to_zero_at_a_time(self):
        self.authors["word"].done = self.authors["shell"].done = True
        self.claim("D09 T02 §1", *self.WORD)
        self.claim("D09 T02 §2", "shell.nothing")
        self.claim("D09 T02 §3", "shell.nothing")
        code, out, err = self.owners("--check", "--app", "word")
        self.assertEqual((code, err), (0, ""))  # the shell's unowned record and its unknown, doubled claim are not Word's
        self.assertEqual(out.splitlines()[0], "word: enforced (D09 T01 §1 is stamped): 8 of 8 records owned")
        self.assertNotIn("shell", out)
        code, _, err = self.owners("--check", "--app", "shell")
        self.assertEqual(code, 1)
        self.assertIn("refused: shell: 1 record(s) no section claims on an Implements line\n"
                      "  unowned control shell.qat.save\n", err)
        self.assertIn("refused: unknown claim: shell.nothing, claimed by D09 T02 §2, D09 T02 §3", err)
        self.assertIn("refused: double claim: shell.nothing is claimed by D09 T02 §2 and D09 T02 §3", err)

    def test_an_app_that_is_no_app_folder_is_refused_not_passed(self):
        for argv in (("--check", "--all", "--app", "wrod"), ("--app", "wrod"), ("--check", "--app", "Word")):
            code, out, err = self.owners(*argv)
            self.assertEqual((code, out), (2, ""), argv)
            self.assertIn("is not an app folder of the inventory (excel, shell, word)", err)

    def test_all_holds_every_app_as_enforced(self):
        code, _, err = self.owners("--check", "--all")
        self.assertEqual(code, 1)
        self.assertIn("refused: excel has no captured record, and --all holds every app\n", err)
        self.assertIn("refused: shell: 1 record(s) no section claims on an Implements line\n", err)
        self.assertIn("refused: word: 8 record(s) no section claims on an Implements line\n", err)
        code, _, err = self.owners("--check", "--all", "--app", "excel")
        self.assertEqual((code, err), (1, "refused: excel has no captured record, and --all holds every app\n"))
        half = self.claim("D09 T02 §1", *self.WORD[:4])
        code, _, err = self.owners("--check", "--all", "--app", "word")  # half claimed, its authoring section open
        self.assertEqual(code, 1)
        self.assertEqual(sorted(line.split()[-1] for line in err.splitlines()[1:]), sorted(self.WORD[4:]))
        half.body += " " + " ".join(f"`{rid}`" for rid in self.WORD[4:])  # the rest claimed on the same line
        self.assertEqual(self.owners("--check", "--all", "--app", "word")[::2], (0, ""))
        # With every app captured and every record claimed, the gate over all of them passes.
        self.claim("D09 T02 §2", "shell.qat.save")
        shutil.rmtree(self.root / "design" / "inventory" / "excel")
        self.authoring({k: v for k, v in self.AUTHORING.items() if k != "excel"})
        self.assertEqual(self.owners("--check", "--all")[::2], (0, ""))

    def test_a_long_refusal_is_bounded(self):
        many = [rec(f"shell.x{n:03d}", "control") for n in range(60)]
        (self.root / "design" / "inventory" / "shell" / "chrome.json").write_text(json.dumps(many), encoding="utf-8")
        self.authors["shell"].done = True
        code, _, err = self.owners("--check", "--app", "shell")
        self.assertEqual(code, 1)
        lines = err.splitlines()
        self.assertEqual(lines[0], "refused: shell: 60 record(s) no section claims on an Implements line")
        self.assertEqual((len(lines), lines[-1]), (ir.OWNERS_SHOWN + 2, "  and 10 more"))

    def test_the_authoring_file_is_held_before_any_state_is_read(self):
        ok = dict(self.AUTHORING)
        cases = {
            "missing: it names, for each app folder": None,
            "cannot be read": "{not json",
            "cannot be read (repeated key word)": '{"word": "D09 T01 §1", "word": "D09 T01 §1"}',
            "not a JSON object of app folder to section reference": "[]",
            "no section named for the app folder excel": {k: v for k, v in ok.items() if k != "excel"},
            "'paint' is not an app folder of the inventory (excel, shell, word)": dict(ok, paint="D09 T01 §1"),
            "word: '§1' is not a section reference (DNN TNN §N)": dict(ok, word="§1"),
            "word: 7 is not a section reference (DNN TNN §N)": dict(ok, word=7),
            "word: D09 T09 §9 is not a section of the TODO tree": dict(ok, word="D09 T09 §9"),
        }
        path = self.root / "design" / "inventory" / "authoring.json"
        for expected, data in cases.items():
            if data is None:
                path.unlink()
            else:
                self.authoring(data)
            for argv in ((), ("--check",), ("--check", "--all")):
                code, out, err = self.owners(*argv)
                self.assertEqual((code, out), (2, ""), (expected, argv))  # no state is printed, pending least of all
                self.assertIn("authoring.json: " + expected, err, argv)

    def test_a_reader_that_stops_listening_does_not_change_the_verdict(self):
        # Round 1, finding 1: with the pipe to its reader closed, a failing check still exits 1 and its refusals
        # still reach stderr; only a report with nothing to refuse ends 0.
        class Closed(io.StringIO):
            def write(self, text):
                raise BrokenPipeError(32, "Broken pipe")

        class Full(io.StringIO):
            def write(self, text):
                raise OSError(28, "No space left on device")

        def run(*argv, stream=Closed):
            err, stand_in = io.StringIO(), stream()
            with contextlib.redirect_stdout(stand_in), contextlib.redirect_stderr(err):
                code = ir.main(["--owners", *argv], root=self.root)
                replaced = sys.stdout
            if replaced is not stand_in:
                replaced.close()  # the report pointed stdout at the null device; give the handle back
            return code, err.getvalue()
        code, err = run("--check", "--all")
        self.assertEqual(code, 1)
        self.assertIn("refused: word: 8 record(s) no section claims on an Implements line\n", err)
        self.assertIn("refused: excel has no captured record", err)
        self.assertEqual(run("--check"), (0, ""))  # every app pending: the check passes, closed pipe or not
        self.assertEqual(run(), (0, ""))           # and the plain report has nothing to fail

        code, err = run(stream=Full)
        self.assertEqual(code, 1)  # a report that could not be written is not a report
        self.assertIn("the report could not be written", err)

    def test_owners_takes_no_other_mode_and_all_goes_with_the_check(self):
        for argv in (("--owners", "--missing"), ("--owners", "--kind", "tab"), ("--owners", "--control-types"),
                     ("--owners", "--cited-in", str(self.report))):
            code, out, err = self.run_report(*argv)
            self.assertEqual((code, out), (2, ""), argv)
            self.assertIn("--owners takes --check, --all and --app only", err)
        for argv in (("--all",), ("--owners", "--all"), ("--check", "--all")):
            code, out, err = self.run_report(*argv)
            self.assertEqual((code, out), (2, ""), argv)
            self.assertIn("--all goes with --owners --check", err)

    def test_the_other_modes_are_as_they_were(self):
        self.claim("D09 T02 §1", "word.home.font.bold", done=True)
        self.assertIn("4 records, 1 implemented", self.run_report("--app", "word", "--kind", "control")[1])
        self.run_report()
        self.assertEqual(self.run_report("--check")[0], 0)  # --check alone is still the report's staleness
        self.authoring("[]")
        self.assertEqual(self.run_report("--check")[0], 0)  # and reads no authoring file

    # D02 T01 §28: what we do with a record. Word holds one record with no disposition, one of each value.

    DECIDED = ("word.a", "word.b", "word.c", "word.d")

    def decided(self, **changed):
        """Word's records replaced by four controls: `word.a` with no disposition, `word.b` build, `word.c`
        equivalent, `word.d` excluded (a keyword changes one record's disposition)."""
        reason = "Depends on a Microsoft cloud service; our own replaces it."
        values = dict({"a": None, "b": "build", "c": "equivalent", "d": "excluded"}, **changed)
        recs = []
        for name, value in values.items():
            extra = {} if value is None else {"disposition": value}
            if value in ("equivalent", "excluded"):
                extra["dispositionReason"] = reason
            recs.append(rec(f"word.{name}", "control", **extra))
        path = self.root / "design" / "inventory" / "word" / "ribbon.json"
        path.write_text(json.dumps(recs), encoding="utf-8")

    def dispositions_row(self, app="word"):
        code, out, err = self.run_report()
        self.assertEqual((code, err), (0, ""))
        table = out.split("\n## Dispositions\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("| App | Build | Equivalent | Excluded | Accounted for |", table)
        return next(line for line in table.splitlines() if line.startswith(f"| {app} |"))

    def test_coverage_counts_each_disposition_and_what_is_accounted_for(self):
        self.decided()
        self.assertEqual(self.dispositions_row(), "| word | 2 | 1 | 1 | 1 |")  # absent is build; only the exclusion
        self.assertEqual(self.dispositions_row("shell"), "| shell | 1 | 0 | 0 | 0 |")
        claims = self.claim("D09 T02 §1", "word.a", "word.b", "word.c")  # an open section: nothing is built yet
        self.assertEqual(self.dispositions_row(), "| word | 2 | 1 | 1 | 1 |")
        claims.done = True  # stamped: the three it implements, and the exclusion
        self.assertEqual(self.dispositions_row(), "| word | 2 | 1 | 1 | 4 |")
        claims.body = "> **Implements:** `word.b` `word.c`"  # an unclaimed record is never accounted for
        self.assertEqual(self.dispositions_row(), "| word | 2 | 1 | 1 | 3 |")
        self.assertEqual(self.run_report("--check")[0], 0)
        self.decided(a="equivalent")  # a disposition changes: the committed report is stale until regenerated
        code, _, err = self.run_report("--check")
        self.assertEqual(code, 1)
        self.assertIn("design/inventory/COVERAGE.md is stale", err)
        self.assertEqual(self.dispositions_row(), "| word | 1 | 2 | 1 | 3 |")
        self.assertEqual(self.run_report("--check")[0], 0)
        claims.done = False  # and a stamp that goes takes its records out again
        self.assertEqual(self.run_report("--check")[0], 1)
        self.assertEqual(self.dispositions_row(), "| word | 1 | 2 | 1 | 1 |")

    def test_a_disposition_the_schema_does_not_allow_is_not_guessed_at(self):
        self.decided(a="maybe")
        for argv in ((), ("--owners",), ("--owners", "--check")):
            code, out, err = self.run_report(*argv)
            self.assertEqual((code, out), (2, ""), argv)
            self.assertIn("word.a: disposition 'maybe' is not one of build, equivalent, excluded", err)

    def test_an_excluded_record_needs_no_owner_and_takes_none(self):
        self.decided()
        self.authors["word"].done = True
        claims = self.claim("D09 T02 §1", "word.a", "word.b", "word.c")
        for argv in (("--check",), ("--check", "--all", "--app", "word"), ("--check", "--app", "word")):
            code, out, err = self.owners(*argv)
            self.assertEqual((code, err), (0, ""), argv)  # the exclusion is the one record nobody claims
            self.assertIn("word: enforced (D09 T01 §1 is stamped): 3 of 3 records owned, 1 excluded\n", out)
            self.assertIn("  control: 3 of 3\n", out)
        for dropped, kind in (("word.c", "equivalent"), ("word.b", "build"), ("word.a", "no disposition")):
            claims.body = "> **Implements:** " + " ".join(f"`{i}`" for i in self.DECIDED[:3] if i != dropped)
            code, out, err = self.owners("--check")
            self.assertEqual(code, 1, kind)
            self.assertEqual(err, "refused: word: 1 record(s) no section claims on an Implements line\n"
                                  f"  unowned control {dropped}\n", kind)
            self.assertIn("word: enforced (D09 T01 §1 is stamped): 2 of 3 records owned, 1 excluded\n", out)

    def test_a_claim_of_an_excluded_record_is_refused_in_every_state(self):
        self.decided()
        self.claim("D09 T02 §1", "word.a", "word.b", "word.c", "word.d")
        refusal = "refused: excluded claim: word.d is excluded, and D09 T02 §1 claims it\n"
        for argv in (("--check",), ("--check", "--all", "--app", "word"), ("--check", "--app", "word")):
            code, out, err = self.owners(*argv)  # Word is pending authoring here
            self.assertEqual((code, err), (1, refusal), argv)
            self.assertIn("word: pending authoring (D09 T01 §1 is open): 3 of 3 records owned, 1 excluded\n", out)
        self.assertEqual(self.owners("--check", "--app", "shell")[::2], (0, ""))  # not the shell's to report
        self.authors["word"].done = True
        self.assertEqual(self.owners("--check")[::2], (1, refusal))
        code, out, err = self.owners()  # the report lists it and refuses nothing
        self.assertEqual((code, err), (0, ""))
        self.assertIn("excluded claim: word.d is excluded, and D09 T02 §1 claims it\n", out)

    def test_a_pending_app_with_unclaimed_exclusions_still_passes(self):
        self.decided(a="excluded", b="excluded")
        code, out, err = self.owners("--check")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("word: pending authoring (D09 T01 §1 is open): 0 of 1 records owned, 3 excluded\n", out)
        self.decided(a="excluded", b="excluded", c="excluded")  # nothing left to build: still a captured app
        code, out, err = self.owners("--check", "--all", "--app", "word")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("word: pending authoring (D09 T01 §1 is open): 0 of 0 records owned, 4 excluded\n", out)


class Layout(Fixture):
    """Layout blocks (D02 T01 §29): where each child of a record sits, generated for a section and checked there."""

    BLOCK = "\n".join([
        "**Layout:** `word.home.para` (capture profile `fhd-100`)",
        "",
        "```text",
        "order   id        label    type         size   x   y   width  height  keytip",
        "parent  .         para     group                       251    96      ZP",
        "0       bullets   Bullets  splitButton  small  8   10  39     24      U",
        "1       sort      Sort...  button       small  49  10  24     24",
        "2       far       Far      button",
        "5       word.odd  Odd      menuItem",
        "        late      Late     button       large  90  10  40     24      L",
        "        zed       Zed      control",
        "children  bullets  2  --layout word.home.para.bullets",
        "```"])

    def setUp(self):
        super().setUp()
        def box(x, y, width, height):
            return {"x": x, "y": y, "width": width, "height": height}
        inv = self.root / "design" / "inventory" / "word"
        (inv / "ribbon.json").write_text(json.dumps([
            rec("word.home", "tab", idMso="TabHome", order=0, bounds=box(0, 60, 1900, 120), captureProfile="fhd-100"),
            rec("word.home.para", "group", "word.home", order=2, keytip="ZP", bounds=box(408, 80, 251, 96),
                captureProfile="fhd-100"),
            rec("word.home.para.sort", "control", "word.home.para", order=1, controlType="button", size="small",
                bounds=box(457, 90, 24, 24), label="Sort..."),
            rec("word.home.para.bullets", "control", "word.home.para", order=0, controlType="splitButton",
                size="small", keytip="U", bounds=box(416, 90, 39, 24), label="Bullets"),
            rec("word.home.para.far", "control", "word.home.para", order=2, controlType="button", label="Far"),
            rec("word.home.para.zed", "control", "word.home.para", label="Zed"),
            rec("word.home.para.late", "control", "word.home.para", controlType="button", size="large", keytip="L",
                bounds=box(498, 90, 40, 24), label="Late"),
            rec("word.home.para.bullets.none", "menuItem", "word.home.para.bullets", order=0, label="None"),
            rec("word.home.para.bullets.disc", "menuItem", "word.home.para.bullets", order=1, label="Disc"),
            rec("word.flat", "group", label="Flat"),
            rec("word.flat.one", "control", "word.flat", order=0, controlType="button", bounds=box(5, 5, 9, 9),
                label="One"),
        ]), encoding="utf-8")
        # A child kept in another file of the app, whose id is not written from the parent's.
        (inv / "extra.json").write_text(json.dumps([rec("word.odd", "menuItem", "word.home.para", order=5,
                                                        label="Odd")]), encoding="utf-8")

    def section(self, ref, body, done=False, path="todo/09-x/TODO-01-a.md"):
        number = int(ref.rsplit("§", 1)[1])
        self.sections.append(SimpleNamespace(ref=ref, done=done, body=body, path=path, number=number))
        return self.sections[-1]

    def layout(self, parent):
        return self.run_report("--layout", parent)

    def check(self, *argv):
        return self.run_report("--layout-check", *argv)

    def test_a_block_lists_the_parent_and_its_children_in_order_from_the_parents_corner(self):
        code, out, err = self.layout("word.home.para")
        self.assertEqual((code, err), (0, ""))
        # Far has no bounds, so its position and size are blank; Odd is in another file and keeps its own id; Late and
        # Zed have no order and come last, in id order; Bullets has two menu items of its own.
        self.assertEqual(out, self.BLOCK + "\n")
        self.assertEqual(self.layout("word.home.para")[1], out)  # the same bytes every time
        code, out, _ = self.layout("word.flat")  # a parent with no bounds and no profile: no positions at all
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines()[0], "**Layout:** `word.flat` (no capture profile)")
        self.assertEqual(out.splitlines()[4:6], ["parent  .    Flat   group",
                                                 "0       one  One    button              9      9"])
        code, out, _ = self.layout("word.home.para.bullets")
        self.assertEqual(out.splitlines()[5:7], ["0       none  None     menuItem", "1       disc  Disc     menuItem"])
        for line in self.BLOCK.splitlines()[3:-1]:
            self.assertNotRegex(line, r"^\s*([-*+>`]|\d+[.)])")  # no row reads as a list item, a quote or a fence

    def test_an_id_that_cannot_be_laid_out_and_a_mode_beside_it_are_refused(self):
        for parent, said in (("word.nothing", "--layout: word.nothing is not a record of the inventory"),
                             ("word.home.para.sort", "--layout: word.home.para.sort has no children in the inventory")):
            code, out, err = self.layout(parent)
            self.assertEqual((code, out), (2, ""))
            self.assertIn(said, err)
        for argv in (("--layout", "word.home.para", "--check"), ("--layout", "word.home.para", "--owners"),
                     ("--layout-check", "--app", "word"), ("--layout", "word.home.para", "--layout-check"),
                     ("--layout-check", "--all")):
            code, out, err = self.run_report(*argv)
            self.assertEqual((code, out), (2, ""), argv)
            self.assertIn("each stand alone", err)
        code, _, err = self.run_report("--layout", "word.home.para", "--write", "todo/09-x/TODO-01-a.md")
        self.assertEqual(code, 2)
        self.assertIn("--write goes with --layout-check", err)

    def test_a_block_that_differs_from_the_inventory_is_named_with_its_section_and_parent(self):
        claim = "> **Implements:** `word.home.para.sort` `word.home.para.bullets`\n\n"
        section = self.section("D09 T01 §1", claim + self.BLOCK + "\n\n**Build order:**\n")
        self.section("D09 T01 §2", "No claim and no block here.\n")
        self.assertEqual(self.check(), (0, "layout blocks: 1 checked in 2 sections, 0 problem(s)\n", ""))
        stale = "refused: D09 T01 §1: the layout of `word.home.para` differs from the inventory; print it again " \
                "with --layout\n"
        for change in (("39     24      U", "38     24      U"),            # one width
                       ("(capture profile `fhd-100`)", "(capture profile `qhd-150`)"),  # the line alone
                       ("Sort...", "Sort"), ("```text\n", "```text\n\n")):
            section.body = claim + self.BLOCK.replace(*change) + "\n\n**Build order:**\n"
            self.assertNotEqual(section.body, claim + self.BLOCK + "\n\n**Build order:**\n", change)
            code, out, err = self.check()
            self.assertEqual((code, err), (1, stale), change)
            self.assertEqual(out, "layout blocks: 1 checked in 2 sections, 1 problem(s)\n")

    def test_a_malformed_an_unknown_and_a_repeated_block_are_each_named(self):
        line = self.BLOCK.splitlines()[0]
        cases = {
            line + "\n\nNo block follows.\n": "has no fenced `text` block after its Layout line",
            self.BLOCK[:-4] + "\n\nThe fence is still open.\n": "has a block whose fence never closes",
            self.BLOCK + "\n\n" + self.BLOCK + "\n": "has two layout blocks in this section",
        }
        section = self.section("D09 T01 §1", "")
        for body, wrong in cases.items():
            section.body = body
            code, _, err = self.check()
            self.assertEqual((code, err), (1, f"refused: D09 T01 §1: the layout of `word.home.para` {wrong}\n"), wrong)
        section.body = self.BLOCK.replace("word.home.para`", "word.gone`")
        code, _, err = self.check()
        self.assertEqual((code, err), (1, "refused: D09 T01 §1: the layout of `word.gone` cannot be laid out: "
                                          "word.gone is not a record of the inventory\n"))

    def test_a_section_that_claims_a_parents_children_carries_that_parents_block(self):
        section = self.section("D09 T01 §1", "> **Implements:** `word.home.para.sort` `word.home.para.bullets`\n")
        missing = "refused: D09 T01 §1: the layout of `{}` has children this section claims and no layout block " \
                  "here; add the block --layout prints\n"
        self.assertEqual(self.check()[::2], (1, missing.format("word.home.para")))
        section.body += "\n" + self.BLOCK + "\n"
        self.assertEqual(self.check()[::2], (0, ""))
        # A tab's group is a child too: claiming the group asks for the tab's block.
        tab = self.layout("word.home")[1]
        section.body = "> **Implements:** `word.home.para`\n"
        self.assertEqual(self.check()[::2], (1, missing.format("word.home")))
        section.body += "\n" + tab
        self.assertEqual(self.check()[::2], (0, ""))
        # A tab has no parent to lay out, and an id the inventory lacks is the ownership check's to refuse.
        section.body = "> **Implements:** `word.home` `word.nothing`\n"
        self.assertEqual(self.check()[::2], (0, ""))
        section.body = "Names `word.home.para.sort` in passing: no claim, so no block.\n"
        self.assertEqual(self.check()[::2], (0, ""))

    def test_a_stamped_section_is_told_the_repair_is_a_new_section(self):
        stale = self.BLOCK.replace("Sort...", "Sort")
        self.section("D09 T01 §1", stale + "\n", done=True)
        self.section("D09 T01 §2", "> **Implements:** `word.home.para.sort`\n", done=True)
        code, _, err = self.check()
        self.assertEqual(code, 1)
        told = "the inventory changed after this section was stamped; a stamped section is never rewritten, so " \
               "file the repair as a new section through add-todo and reopen this one with unstamp"
        self.assertEqual(err, f"refused: D09 T01 §1: the layout of `word.home.para` differs from the inventory: {told}\n"
                              f"refused: D09 T01 §2: the layout of `word.home.para` has children this section claims "
                              f"and no layout block here: {told}\n")

    def test_many_problems_in_one_section_are_bounded(self):
        line = self.BLOCK.splitlines()[0]
        self.section("D09 T01 §1", "\n\n".join(line.replace("word.home.para", f"word.x{n}") for n in range(60)))
        code, out, err = self.check()
        self.assertEqual(code, 1)
        self.assertEqual((len(err.splitlines()), err.splitlines()[-1]),
                         (ir.LAYOUT_SHOWN + 1, "refused: D09 T01 §1: and 10 more layout problems"))
        self.assertEqual(out, "layout blocks: 60 checked in 1 sections, 60 problem(s)\n")

    def todo_file(self, windows=False):
        """A TODO file with an open section and a stamped one, each holding the same stale block."""
        stale = self.BLOCK.replace("Sort...", "Sort").replace("fhd-100", "old-profile")
        text = ("# TODO-01 -- A\n\n## 1. Open\n\nBefore.\n\n" + stale + "\n\nAfter the block.\n\n"
                "## 2. Stamped\n\n" + stale + "\n\n## Verification\n\n- v\n")
        path = self.root / "todo" / "09-x" / "TODO-01-a.md"
        path.parent.mkdir(parents=True)
        path.write_bytes((text.replace("\n", "\r\n") if windows else text).encode("utf-8"))
        for number, done in ((1, False), (2, True)):
            self.section(f"D09 T01 §{number}", ir.todo_graph.section_text(text, number), done=done)
        return path, text, stale

    def test_write_replaces_the_stale_blocks_of_open_sections_and_nothing_else(self):
        for windows in (False, True):
            with self.subTest(windows=windows):
                path, text, stale = self.todo_file(windows)
                code, out, err = self.check("--write", str(path))
                wanted = text.replace(stale, self.BLOCK, 1)  # the open section's block, and only that
                self.assertEqual(path.read_bytes(),
                                 (wanted.replace("\n", "\r\n") if windows else wanted).encode("utf-8"))
                self.assertEqual(wanted.count(stale), 1)  # the stamped section keeps its stale block
                self.assertEqual(code, 1)  # which the check that follows still refuses
                self.assertIn("todo/09-x/TODO-01-a.md: 1 layout block(s) rewritten\n", out)
                self.assertTrue(err.startswith("refused: D09 T01 §2: the layout of `word.home.para` differs"))
                self.assertNotIn("D09 T01 §1", err)
                self.assertEqual(sorted(p.name for p in path.parent.iterdir()), ["TODO-01-a.md"])
                code, out, _ = self.check("--write", "todo/09-x/TODO-01-a.md")  # again: nothing left to rewrite
                self.assertNotIn("rewritten", out)
            self.sections.clear()
            shutil.rmtree(self.root / "todo")

    def test_a_write_that_fails_leaves_the_file_as_it_was(self):
        path, text, _ = self.todo_file()
        before = path.read_bytes()
        failures = {"os.fsync": mock.patch.object(ir.todo_graph.os, "fsync", side_effect=OSError(28, "No space left")),
                    "os.replace": mock.patch.object(ir.todo_graph.os, "replace",
                                                    side_effect=PermissionError(13, "sharing violation"))}
        for stage, failing in failures.items():
            with failing:
                code, out, err = self.check("--write", str(path))
            self.assertEqual(code, 1, stage)
            self.assertIn("refused: todo/09-x/TODO-01-a.md was not written (", err)
            self.assertIn("); it is as it was\n", err)
            self.assertIn("refused: D09 T01 §1: the layout of `word.home.para` differs", err)  # still stale, and said
            self.assertNotIn("rewritten", out)
            self.assertEqual(path.read_bytes(), before, stage)
            self.assertEqual(sorted(p.name for p in path.parent.iterdir()), ["TODO-01-a.md"], stage)

    def test_write_takes_a_todo_file_of_this_tree(self):
        self.todo_file()
        other = self.root / "notes.md"
        other.write_text("x", encoding="utf-8")
        for target in (other, self.root / "todo" / "09-x" / "TODO-09-missing.md", Path(self.root).parent / "x.md"):
            code, out, err = self.check("--write", str(target))
            self.assertEqual((code, out), (2, ""), target)
            self.assertIn("is not a TODO file of this tree", err)


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


def stamp_fixture():
    """The stamp tests' fixture (a TODO tree whose section 1 can be stamped for real), with section 1 claiming
    `word.home`, a Word inventory holding it, and the scripts the pre-commit hook runs. Built here rather than
    subclassed at module level, so the stamp tests' own tests are not collected again."""
    class Claiming(tts.Stamp):
        def write(self, text, *args, **kwargs):
            text = text.replace("**Test checkpoint:**", "> **Implements:** `word.home`\n\n**Test checkpoint:**", 1)
            inv = self.root / "design" / "inventory" / "word"
            inv.mkdir(parents=True, exist_ok=True)
            (inv / "ribbon.json").write_text(json.dumps([rec("word.home", "tab", idMso="TabHome")]),
                                             encoding="utf-8")
            (inv.parent / "authoring.json").write_text(json.dumps({"word": "D00 T01 §1"}), encoding="utf-8")
            if not (self.root / "scripts").exists():  # the scripts the hook runs, and the reviewer kit they load
                shutil.copytree(SCRIPTS, self.root / "scripts", ignore=shutil.ignore_patterns("tests", "__pycache__"))
            (self.root / "scripts/hooks/pre-commit").chmod(0o755)
            return super().write(text, *args, **kwargs)
    return Claiming("test_stamp_writes_receipt_and_validates")


@unittest.skipUnless(shutil.which("git"), "needs git (which runs the hook with its own shell)")
class RealStamp(unittest.TestCase):
    """Round 1: a real stamp and unstamp of a section that claims a record, read by the TODO graph and held by the
    real pre-commit hook, with no inventory change."""

    def setUp(self):
        self.fx = stamp_fixture()
        self.fx.setUp()
        self.addCleanup(self.fx.tearDown)
        self.root = self.fx.root

    def report(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            ir.main(list(argv), root=self.root)
        return out.getvalue() + err.getvalue()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True)

    def commit_through_hook(self):
        self.git("add", "-A")
        return self.git("commit", "-qm", "step")

    def test_a_stamp_and_an_unstamp_move_the_count_and_the_hook_holds_both(self):
        self.report()  # the report as it stands before the stamp, committed before the hook is enabled
        self.git("add", "-A")
        self.git("commit", "-qm", "report")
        self.git("config", "core.hooksPath", "scripts/hooks")
        self.assertIn("1 records, 0 implemented", self.report("--app", "word"))

        self.fx.tick_work()
        self.fx.stamp("D00 T01 §1", self.fx.sha, self.fx.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
        self.assertIn("1 records, 1 implemented", self.report("--app", "word"))
        refused = self.commit_through_hook()
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("design/inventory/COVERAGE.md is stale", refused.stderr)
        self.report()
        done = self.commit_through_hook()
        self.assertEqual(done.returncode, 0, done.stderr)

        tts.tg.unstamp(self.root, "D00 T01 §1", "test", "2026-10-14T00:00:00Z")
        subprocess.run([sys.executable, str(self.root / "scripts/todo-graph.py"), "plan", "--sync"], check=True,
                       capture_output=True, cwd=self.root)  # the unstamp changes the plan; only the report is stale
        self.assertIn("1 records, 0 implemented", self.report("--app", "word"))
        refused = self.commit_through_hook()
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("design/inventory/COVERAGE.md is stale", refused.stderr)


    def test_the_hook_holds_an_enforced_apps_records_to_their_owners(self):
        # D02 T01 §22: section 1 authors Word's domain and claims `word.home`; section 2, open, claims a second
        # record. Once section 1 is really stamped Word is enforced, and a commit that drops section 2's claim is
        # refused by the hook, naming the record.
        todo = self.root / "todo/00-workspace/TODO-01-a.md"
        ribbon = self.root / "design/inventory/word/ribbon.json"
        ribbon.write_text(json.dumps([rec("word.home", "tab", idMso="TabHome"),
                                      rec("word.review", "tab", idMso="TabReviewWord")]), encoding="utf-8")
        head, checkpoint, tail = todo.read_text(encoding="utf-8").rpartition("**Test checkpoint:**")
        claim = "> **Implements:** `word.review`\n\n"
        todo.write_text(head + claim + checkpoint + tail, encoding="utf-8")

        def sync():
            subprocess.run([sys.executable, str(self.root / "scripts/todo-graph.py"), "plan", "--sync"], check=True,
                           capture_output=True, cwd=self.root)
        sync()
        self.report()
        self.git("add", "-A")
        self.git("commit", "-qm", "two records, two claims")
        self.git("config", "core.hooksPath", "scripts/hooks")
        self.assertIn("word: pending authoring (D00 T01 §1 is open): 2 of 2 records owned", self.report("--owners"))

        self.fx.tick_work()
        self.fx.stamp("D00 T01 §1", self.fx.sha, self.fx.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
        self.report()
        self.assertIn("word: enforced (D00 T01 §1 is stamped): 2 of 2 records owned", self.report("--owners"))
        done = self.commit_through_hook()
        self.assertEqual(done.returncode, 0, done.stderr)

        todo.write_text(todo.read_text(encoding="utf-8").replace(claim, "", 1), encoding="utf-8")
        sync()
        refused = self.commit_through_hook()
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("refused: word: 1 record(s) no section claims on an Implements line", refused.stderr)
        self.assertIn("  unowned tab word.review", refused.stderr)
        self.assertIn("pre-commit: give each record named above one owner", refused.stderr)
        self.assertNotIn("pending", refused.stderr + refused.stdout)  # the states go to stdout, which the hook drops


class Committed(unittest.TestCase):
    def test_the_committed_report_is_current_and_well_formed(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ir.main(["--check"])
        self.assertEqual(code, 0, err.getvalue())

    def test_a_failing_check_exits_1_into_a_closed_pipe(self):
        # Round 1, finding 1, as the reviewer ran it: the gate over Word, whose records nobody claims yet, with its
        # output piped to a reader that has already gone.
        process = subprocess.Popen([sys.executable, "-B", str(SCRIPTS / "inventory-report.py"), "--owners", "--check",
                                    "--all", "--app", "word"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.stdout.close()
        try:
            refusals = process.stderr.read().decode("utf-8", "replace")
            code = process.wait(timeout=120)
        finally:
            if process.poll() is None:
                process.kill()
            process.stderr.close()
        rows, *_ = ir.ownership(ir.ROOT, ir.load_inventory(ir.ROOT)[0], ir.read_sections(ir.ROOT), "word")
        unowned = sum(len(pair[1]) for pair in rows[0][3].values())
        if unowned:
            self.assertEqual(code, 1, refusals)
            self.assertIn(f"refused: word: {unowned} record(s) no section claims on an Implements line", refusals)
        else:  # once every Word record has its owner the same command passes, pipe or no pipe
            self.assertEqual(code, 0, refusals)
        self.assertNotIn("Traceback", refusals)
        self.assertNotIn("Exception ignored", refusals)

    def test_the_repositorys_layout_blocks_are_current_and_the_paragraph_group_has_its_controls(self):
        # D02 T01 §29's checkpoint, on the repository: the block of the Home tab's Paragraph group, and the check.
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ir.main(["--layout", "word.home.paragraph"])
        self.assertEqual((code, err.getvalue()), (0, ""))
        rows = [line for line in out.getvalue().splitlines() if re.match(r"\d+ ", line)]
        self.assertEqual(len(rows), 15)
        self.assertRegex(rows[0], r"^0 +bullets +Bullets +splitButton +small +8 +10 +39 +24 +U$")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ir.main(["--layout-check"])
        self.assertEqual((code, err.getvalue()), (0, ""))

    def test_the_repositorys_ownership_check_passes_and_names_every_app(self):
        # D02 T01 §22's checkpoint: the report runs on the repository, and the check the hook runs passes there.
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ir.main(["--owners", "--check"])
        self.assertEqual((code, err.getvalue()), (0, ""))
        named = [line.split(":", 1)[0] for line in out.getvalue().splitlines() if not line.startswith(" ")]
        self.assertEqual(named, ["excel", "outlook", "powerpoint", "project", "shell", "visio", "word"])


if __name__ == "__main__":
    unittest.main()
