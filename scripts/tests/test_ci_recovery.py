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
        self.cli("reserve", "repair")
        code, out = self.cli("result", "green")
        self.assertEqual(code, 0)
        self.assertIn("closed", out)
        self.assertIn("no open recovery", self.cli("show")[1])

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
        self.cli("open", sha(1))
        self.cli("reserve", "rerun")  # the session dies here: no result was recorded
        # A resume, in a new session with a new run file, reads the same state file.
        _, shown = self.cli("show")
        self.assertIn("1 of 4 attempts spent", shown)
        self.assertIn("no result (spent)", shown)
        self.assertEqual(self.cli("reserve", "rerun")[0], 1)  # the reserved rerun is not run again
        self.assertEqual(self.cli("reserve", "repair")[1], "attempt 2 of 4: repair on 0000001")

    def test_the_state_is_written_atomically_and_never_reset_when_unreadable(self):
        self.cli("open", sha(1))
        self.assertTrue(json.loads(self.state.read_text(encoding="utf-8"))["recovery"])
        self.assertFalse(self.state.with_name(self.state.name + ".tmp").exists())
        self.state.write_text("{ not json", encoding="utf-8")
        code, out = self.cli("reserve", "repair")
        self.assertEqual(code, 2)
        self.assertEqual(self.state.read_text(encoding="utf-8"), "{ not json")

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

    def test_only_full_shas_are_accepted(self):
        self.assertEqual(self.cli("open", "abc1234")[0], 1)


if __name__ == "__main__":
    unittest.main()
