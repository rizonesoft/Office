# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/ci-recovery.py: one bounded recovery per red main, kept across resumes (D00 T03 §18)."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ci_recovery", SCRIPTS / "ci-recovery.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)


def sha(n):
    return f"{n:07x}" + "d" * 33


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.state = self.tmp / "build" / "ci-recovery.json"
        self.ancestors = {}  # head -> set of its ancestors

    def git(self, argv):
        first, head = argv[-2], argv[-1]
        return subprocess.CompletedProcess(argv, 0 if first in self.ancestors.get(head, set()) else 1, "", "")

    def cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = rec.main(list(argv), state_path=self.state, run=self.git)
        return code, out.getvalue().strip()


class Recovery(Base):
    def test_a_repair_that_turns_another_job_red_stays_in_the_same_recovery(self):
        red, repair1, repair2 = sha(1), sha(2), sha(3)
        self.cli("open", red)
        self.cli("reserve", "repair")
        self.cli("attach", repair1)
        self.cli("result", "red")  # another job is red now
        self.assertIn("recovery 0000001 already open", self.cli("open", repair1)[1])
        self.cli("reserve", "repair")
        self.cli("attach", repair2)
        _, shown = self.cli("show")
        self.assertIn("2 of 4 attempts spent", shown)
        self.assertIn("heads 0000001, 0000002, 0000003", shown)

    def test_the_budget_resets_only_on_a_descendant_green(self):
        red, repair, unrelated = sha(1), sha(2), sha(9)
        self.ancestors[repair] = {red}
        self.cli("open", red)
        self.cli("reserve", "repair")
        code, out = self.cli("close", unrelated)
        self.assertEqual(code, 1)
        self.assertIn("does not descend", out)
        self.assertEqual(self.cli("close", repair)[0], 0)
        self.assertIn("no open recovery", self.cli("show")[1])
        self.cli("open", sha(5))
        self.assertIn("0 of 4 attempts spent", self.cli("show")[1])

    def test_each_kind_is_spent_and_a_fifth_attempt_is_exhausted(self):
        self.cli("open", sha(1))
        for kind, outcome in (("repair", "red"), ("rerun", "red"), ("wait", "pending"), ("unreadable", "unreadable")):
            with self.subTest(kind=kind):
                self.assertEqual(self.cli("reserve", kind)[0], 0)
                self.cli("result", outcome)
        code, out = self.cli("reserve", "repair")
        self.assertEqual(code, 1)
        self.assertIn("exhausted: 4 of 4", out)

    def test_repeated_pending_and_unreadable_results_spend_the_budget(self):
        self.cli("open", sha(1))
        for _ in range(2):
            self.cli("reserve", "wait")
            self.cli("result", "pending")
            self.cli("reserve", "unreadable")
            self.assertIn(self.cli("result", "unreadable")[1].split(";")[1].strip(),
                          ("2 attempt(s) left", "0 attempt(s) left, exhausted"))
        self.assertEqual(self.cli("reserve", "wait")[0], 1)

    def test_a_fourth_attempt_that_succeeds_closes_the_recovery(self):
        self.cli("open", sha(1))
        for _ in range(3):
            self.cli("reserve", "repair")
            self.cli("result", "red")
        self.cli("reserve", "repair")  # the skill's order: reserve, fix, push, then attach the repair head
        self.cli("attach", sha(4))
        self.ancestors[sha(4)] = {sha(1)}
        guidance = self.cli("result", "green")[1]
        self.assertIn("close the recovery", guidance)
        self.assertNotIn(sha(1)[:7], guidance)  # never names the red head as the green one
        code, out = self.cli("close", sha(4))
        self.assertEqual(code, 0)
        self.assertIn("closed", out)
        self.assertIn("no open recovery", self.cli("show")[1])

    def test_a_green_result_alone_never_closes_or_resets(self):
        # Review round 1 of D00 T03 §18, finding 1: a green result for an unrelated head must not reset the budget.
        self.cli("open", sha(1))
        self.cli("reserve", "wait", "--head", sha(9))
        self.cli("result", "green")
        self.assertIn("1 of 4 attempts spent", self.cli("show")[1])
        self.assertEqual(self.cli("close", sha(9))[0], 1)  # it does not descend from the first head

    def test_a_resumed_red_head_that_was_never_attached_joins_the_recovery(self):
        # Review round 1 of D00 T03 §18, finding 2: repair B was pushed, then the session died before `attach B`.
        a, b = sha(1), sha(2)
        self.cli("open", a)
        self.cli("reserve", "rerun")
        self.cli("result", "red")
        self.cli("reserve", "repair")  # B is pushed; the session dies here
        self.assertIn(f"{b[:7]} is its newest head", self.cli("open", b)[1])
        self.assertEqual(self.cli("reserve", "rerun")[1], f"attempt 3 of 4: rerun on {b[:7]}")

    def test_a_second_rerun_for_the_same_head_is_refused(self):
        self.cli("open", sha(1))
        self.assertEqual(self.cli("reserve", "rerun")[0], 0)
        self.cli("result", "red")
        code, out = self.cli("reserve", "rerun")
        self.assertEqual(code, 1)
        self.assertIn("already used", out)
        self.cli("attach", sha(2))
        self.assertEqual(self.cli("reserve", "rerun")[0], 0)  # a new head has its own one rerun

    def test_an_interrupted_reservation_is_spent_and_never_repeated_after_a_resume(self):
        # Each step is its own process, as separate sessions are: the reserving process ends before any result, and
        # the resumed one (with a new run file, which the state does not depend on) reads the same state file.
        def process(*argv):
            return subprocess.run([sys.executable, "-B", str(SCRIPTS / "ci-recovery.py"), "--state", str(self.state),
                                   *argv], capture_output=True, text=True)
        self.assertEqual(process("open", sha(1)).returncode, 0)
        self.assertEqual(process("reserve", "rerun").returncode, 0)  # the session dies here: no result
        shown = process("show").stdout
        self.assertIn("1 of 4 attempts spent", shown)
        self.assertIn("no result (spent)", shown)
        self.assertEqual(process("reserve", "rerun").returncode, 1)  # the reserved rerun is not run again
        self.assertEqual(process("reserve", "repair").stdout.strip(), "attempt 2 of 4: repair on 0000001")

    def test_the_state_is_written_atomically_and_never_reset_when_unreadable(self):
        self.cli("open", sha(1))
        self.assertTrue(json.loads(self.state.read_text(encoding="utf-8"))["recovery"])
        self.assertFalse(self.state.with_name(self.state.name + ".tmp").exists())
        self.state.write_text("{ not json", encoding="utf-8")
        code, out = self.cli("reserve", "repair")
        self.assertEqual(code, 2)
        self.assertEqual(self.state.read_text(encoding="utf-8"), "{ not json")

    def test_every_malformed_state_is_unreadable_never_a_crash(self):
        # Review round 2 of D00 T03 §18: shapes the writer never makes still exit 2.
        self.cli("open", sha(1))
        good = json.loads(self.state.read_text(encoding="utf-8"))
        bad_shapes = [{}, {"recovery": None, "extra": 1}, [], {"recovery": {**good["recovery"], "heads": []}},
                      {"recovery": {**good["recovery"], "first": "x"}},
                      {"recovery": {**good["recovery"], "attempts": [{"n": 2, "kind": "repair"}]}},
                      {"recovery": {**good["recovery"], "reruns": [1]}}]
        for shape in bad_shapes:
            with self.subTest(shape=str(shape)[:60]):
                self.state.write_text(json.dumps(shape), encoding="utf-8")
                for argv in (("show",), ("reserve", "repair"), ("open", sha(2))):
                    self.assertEqual(self.cli(*argv)[0], 2, argv)

    def test_a_refused_request_changes_nothing(self):
        self.cli("open", sha(1))
        before = self.state.read_bytes()
        self.assertEqual(self.cli("close", sha(7))[0], 1)
        self.assertEqual(self.cli("result", "red")[0], 1)  # nothing reserved yet
        self.assertEqual(self.state.read_bytes(), before)

    def test_nothing_happens_without_an_open_recovery(self):
        for argv in (("attach", sha(2)), ("reserve", "repair"), ("result", "red"), ("close", sha(2))):
            with self.subTest(argv=argv):
                self.assertEqual(self.cli(*argv)[0], 1)

    def test_descent_is_read_from_real_git(self):
        head = subprocess.run(["git", "-C", str(rec.ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        parent = subprocess.run(["git", "-C", str(rec.ROOT), "rev-parse", "HEAD~1"], capture_output=True,
                                text=True).stdout.strip()
        self.assertTrue(rec.descends(parent, head, subprocess.run))
        self.assertFalse(rec.descends(head, parent, subprocess.run))

    def test_a_green_found_at_resume_settles_an_interrupted_recovery(self):
        # D00 T03 §21: attempt four turned green, then the session died before `close`.
        red, repair = sha(1), sha(4)
        self.ancestors[repair] = {red}
        self.cli("open", red)
        for _ in range(3):
            self.cli("reserve", "repair")
            self.cli("result", "red")
        self.cli("reserve", "repair")
        self.cli("attach", repair)
        self.cli("result", "green")  # the session dies here
        code, out = self.cli("settle", repair)  # the resume's reconciliation found origin/main green
        self.assertEqual(code, 0)
        self.assertIn("closed on green 0000004 after 4 of 4 attempts", out)
        self.cli("open", sha(7))  # a later, unrelated failure
        self.assertIn("0 of 4 attempts spent", self.cli("show")[1])

    def test_settle_leaves_a_recovery_open_for_a_head_that_does_not_end_it(self):
        self.cli("open", sha(1))
        self.cli("reserve", "repair")
        code, out = self.cli("settle", sha(9))
        self.assertEqual(code, 0)
        self.assertIn("stays open", out)
        self.assertIn("1 of 4 attempts spent", self.cli("show")[1])

    def test_settle_without_a_recovery_is_a_no_op(self):
        self.assertEqual(self.cli("settle", sha(1)), (0, "settle: no open recovery"))

    def test_only_full_shas_are_accepted(self):
        self.assertEqual(self.cli("open", "abc1234")[0], 1)


if __name__ == "__main__":
    unittest.main()
