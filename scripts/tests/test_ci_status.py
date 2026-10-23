# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/ci-status.py: the governing push run of a commit decides green, red, pending or unknown (D00 T03 §15)."""
import contextlib
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ci_status", SCRIPTS / "ci-status.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

SHA = "a" * 40
COMMITTED = datetime(2026, 10, 23, 10, 0, 0, tzinfo=timezone.utc)


def run(**over):
    base = {"databaseId": 7, "status": "completed", "conclusion": "success", "url": "https://x/runs/7",
            "createdAt": "2026-10-23T10:00:05Z", "headSha": SHA, "event": "push", "headBranch": "main", "attempt": 1}
    base.update(over)
    return base


class Fake:
    """A scripted git and gh. `runs` is a list of run lists, one per poll; every call is recorded with its deadline."""

    def __init__(self, runs=None, jobs=None, log="", fail=None):
        self.polls = list(runs if runs is not None else [[run()]])
        self.jobs = jobs if jobs is not None else []
        self.log = log
        self.fail = fail or {}
        self.calls = []

    def call(self, name, args, seconds):
        self.calls.append((name, args[:2], seconds))
        key = f"{name} {args[0]} {args[1] if len(args) > 1 else ''}".strip()
        if key in self.fail:
            failure = self.fail[key]
            if isinstance(failure, Exception):
                raise failure
            return subprocess.CompletedProcess(args, 1, "", failure)
        if name == "git" and args[0] == "rev-parse":
            return subprocess.CompletedProcess(args, 0, SHA + "\n", "")
        if name == "git" and args[0] == "show":
            return subprocess.CompletedProcess(args, 0, COMMITTED.isoformat() + "\n", "")
        if args[:2] == ["run", "list"]:
            current = self.polls[0] if len(self.polls) == 1 else self.polls.pop(0)
            return subprocess.CompletedProcess(args, 0, json.dumps(current), "")
        if args[:2] == ["run", "view"] and "--log-failed" in args:
            return subprocess.CompletedProcess(args, 0, self.log, "")
        if args[:2] == ["run", "view"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"jobs": self.jobs}), "")
        raise AssertionError(f"unexpected call {name} {args}")


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds


class Base(unittest.TestCase):
    def main(self, fake, *argv, minutes=5):
        clock = Clock()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ci.main(["HEAD", *argv], tools=fake, clock=clock, sleep=clock.sleep,
                           now=lambda: COMMITTED + timedelta(minutes=minutes) + timedelta(seconds=clock.t - 1000))
        return code, out.getvalue()


class States(Base):
    def test_green(self):
        code, out = self.main(Fake())
        self.assertEqual(code, 0)
        self.assertIn("green aaaaaaa run 7", out)

    def test_red_names_the_conclusion_and_failing_steps(self):
        jobs = [{"name": "gates", "conclusion": "failure",
                 "steps": [{"name": "Checkout", "conclusion": "success"}, {"name": "Tests", "conclusion": "failure"}]},
                {"name": "lint", "conclusion": "success", "steps": []}]
        code, out = self.main(Fake(runs=[[run(conclusion="failure")]], jobs=jobs))
        self.assertEqual(code, 1)
        self.assertIn("red aaaaaaa run 7 attempt 1 https://x/runs/7 (failure)", out)
        self.assertIn("gates (failure): Tests (failure)", out)
        self.assertNotIn("lint", out)

    def test_every_other_conclusion_is_red(self):
        for conclusion in ("cancelled", "timed_out", "startup_failure", "action_required", "skipped", "neutral",
                           "stale", None):
            with self.subTest(conclusion=conclusion):
                code, out = self.main(Fake(runs=[[run(conclusion=conclusion)]]))
                self.assertEqual(code, 1)
                self.assertIn(f"({conclusion or 'no conclusion'})", out)

    def test_queued_and_running_are_pending(self):
        for state in ("queued", "in_progress", "waiting"):
            with self.subTest(state=state):
                self.assertEqual(self.main(Fake(runs=[[run(status=state, conclusion="")]]))[0], 3)

    def test_no_run_inside_the_grace_period_is_pending_and_after_it_unknown(self):
        self.assertEqual(self.main(Fake(runs=[[]]), minutes=5)[0], 3)
        code, out = self.main(Fake(runs=[[]]), minutes=11)
        self.assertEqual(code, 2)
        self.assertIn("no ci.yml push run on main", out)

    def test_a_run_created_late_is_still_found(self):
        code, _ = self.main(Fake(runs=[[], [], [run()]]), "--wait", "--timeout", "600", minutes=1)
        self.assertEqual(code, 0)

    def test_gh_that_cannot_be_read_is_unknown(self):
        self.assertEqual(self.main(Fake(fail={"gh run list": "HTTP 401"}))[0], 2)
        self.assertEqual(self.main(Fake(fail={"gh run list": ci.Unknown("gh is not on PATH")}))[0], 2)
        fake = Fake()
        fake.polls = [["not", "runs"]]
        self.assertEqual(self.main(fake)[0], 2)

    def test_a_ref_that_is_not_a_commit_is_unknown(self):
        fake = Fake()
        real = fake.call
        fake.call = lambda name, args, seconds: (subprocess.CompletedProcess(args, 128, "", "bad")
                                                 if args[0] == "rev-parse" else real(name, args, seconds))
        self.assertEqual(self.main(fake)[0], 2)


class Identity(Base):
    def test_pull_request_and_manual_runs_never_count(self):
        runs = [run(event="pull_request", conclusion="success", databaseId=1),
                run(event="workflow_dispatch", conclusion="success", databaseId=2),
                run(conclusion="failure", databaseId=3)]
        code, out = self.main(Fake(runs=[runs]))
        self.assertEqual(code, 1)
        self.assertIn("run 3", out)

    def test_other_branches_and_commits_never_count(self):
        runs = [run(headBranch="feature", databaseId=1), run(headSha="b" * 40, databaseId=2)]
        self.assertEqual(self.main(Fake(runs=[runs]), minutes=11)[0], 2)

    def test_the_newest_push_run_governs(self):
        runs = [run(conclusion="failure", createdAt="2026-10-23T10:00:05Z", databaseId=1),
                run(conclusion="success", createdAt="2026-10-23T10:20:00Z", databaseId=2)]
        code, out = self.main(Fake(runs=[runs]))
        self.assertEqual(code, 0)
        self.assertIn("run 2", out)

    def test_a_rerun_attempt_that_turned_green_is_green(self):
        code, out = self.main(Fake(runs=[[run(attempt=2)]]))
        self.assertEqual(code, 0)
        self.assertIn("attempt 2", out)

    def test_the_ref_is_resolved_to_a_full_sha_for_the_lookup(self):
        fake = Fake()
        self.main(fake)
        self.assertIn(("git", ["rev-parse", "--verify"], fake.calls[0][2]), fake.calls)
        listed = [c for c in fake.calls if c[0] == "gh" and c[1] == ["run", "list"]]
        self.assertTrue(listed)


class Waiting(Base):
    def test_turns_green_after_two_polls(self):
        pending = [run(status="in_progress", conclusion="")]
        code, out = self.main(Fake(runs=[pending, pending, [run()]]), "--wait", "--timeout", "600")
        self.assertEqual(code, 0)

    def test_a_run_that_never_ends_is_pending_at_the_timeout(self):
        code, out = self.main(Fake(runs=[[run(status="in_progress", conclusion="")]]), "--wait", "--timeout", "120")
        self.assertEqual(code, 3)
        self.assertIn("still pending after 120 s", out)

    def test_every_call_is_bounded_by_sixty_seconds_or_the_time_left(self):
        fake = Fake(runs=[[run(status="in_progress", conclusion="")]])
        self.main(fake, "--wait", "--timeout", "100")
        self.assertTrue(all(0 < seconds <= ci.CALL_SECONDS for _, _, seconds in fake.calls), fake.calls)
        self.assertTrue(any(seconds < ci.CALL_SECONDS for _, _, seconds in fake.calls), "never bounded by time left")

    def test_a_hung_gh_is_unknown_within_its_deadline(self):
        hung = ci.Unknown("gh run did not answer within 60 seconds")
        code, out = self.main(Fake(fail={"gh run list": hung}), "--wait", "--timeout", "600")
        self.assertEqual(code, 2)
        self.assertIn("did not answer", out)


class Logs(Base):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_the_log_is_bounded_and_lands_outside_the_repository(self):
        log = "\n".join(f"line {n}" for n in range(1000))
        target = self.tmp / "ci.log"
        code, out = self.main(Fake(runs=[[run(conclusion="failure")]], log=log), "--log", str(target))
        self.assertEqual(code, 1)
        lines = target.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), ci.LOG_LINES)
        self.assertEqual(lines[-1], "line 999")

    def test_a_log_inside_the_repository_is_refused(self):
        target = ci.ROOT / "build" / "ci-test.log"
        code, out = self.main(Fake(runs=[[run(conclusion="failure")]], log="x"), "--log", str(target))
        self.assertEqual(code, 1)
        self.assertIn("inside the repository", out)
        self.assertFalse(target.exists())

    def test_a_log_that_cannot_be_read_is_reported_and_the_status_stands(self):
        fake = Fake(runs=[[run(conclusion="failure")]], fail={"gh run view": "HTTP 500"})
        code, out = self.main(fake, "--log", str(self.tmp / "ci.log"))
        self.assertEqual(code, 1)
        self.assertIn("log not written", out)
        self.assertIn("the failing jobs could not be read", out)


if __name__ == "__main__":
    unittest.main()
