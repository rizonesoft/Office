# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/ci-status.py: the governing push run of a commit decides green, red, pending or unknown (D00 T03 §15)."""
import contextlib
from datetime import datetime, timedelta, timezone
import re
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

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
        self.origin = "https://github.com/rizonesoft/Office.git"
        self.calls = []
        self.argv = []

    def call(self, name, args, seconds):
        self.calls.append((name, args[:2], seconds))
        self.argv.append((name, list(args)))
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
        if name == "git" and args[0] == "remote":
            return subprocess.CompletedProcess(args, 0, self.origin + "\n", "")
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
        clock = self.clock = Clock()
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


class Repository(Base):
    def test_every_gh_call_names_origin_whatever_gh_repo_says(self):
        jobs = [{"name": "gates", "conclusion": "failure", "steps": []}]
        fake = Fake(runs=[[run(conclusion="failure")]], jobs=jobs, log="x")
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        with mock.patch.dict("os.environ", {"GH_REPO": "someone/elsewhere", "GH_HOST": "ghe.example"}):
            self.main(fake, "--log", str(tmp / "ci.log"))
        gh = [args for name, args in fake.argv if name == "gh"]
        self.assertEqual(len(gh), 3)  # run list, run view --json jobs, run view --log-failed
        for args in gh:
            self.assertEqual(args[args.index("--repo") + 1], "github.com/rizonesoft/Office", args)

    def test_an_origin_that_is_not_github_is_unknown(self):
        fake = Fake()
        fake.origin = "https://gitlab.example/rizonesoft/Office.git"
        code, out = self.main(fake)
        self.assertEqual(code, 2)
        self.assertNotIn("gitlab.example/rizonesoft", out)  # never the URL, which can carry a token


class Waiting(Base):
    def test_turns_green_after_two_polls(self):
        pending = [run(status="in_progress", conclusion="")]
        code, out = self.main(Fake(runs=[pending, pending, [run()]]), "--wait", "--timeout", "600")
        self.assertEqual(code, 0)

    def test_a_run_that_never_ends_is_pending_at_the_timeout(self):
        code, out = self.main(Fake(runs=[[run(status="in_progress", conclusion="")]]), "--wait", "--timeout", "100")
        self.assertEqual(code, 3)
        self.assertIn("still pending at the 100 s timeout", out)
        self.assertEqual(self.clock.t - 1000, 100 - ci.RESERVE)  # its last look started a second before the timeout

    def test_every_call_is_bounded_by_sixty_seconds_or_the_time_left(self):
        # Each of a look's four calls takes 20 s and honours its deadline; the fourth gets only the 40 s left. The
        # first look ends at 80 s; the wait looks again at 99 s with 1 s left, which the timeout cuts short.
        clock = Clock()
        fake = Fake(runs=[[run(status="in_progress", conclusion="")]])
        real = fake.call

        def slow(name, args, seconds):
            self.assertLess(clock.t - 1000, 100, "a call started after the timeout")
            if 20 > seconds:
                clock.t += seconds
                raise ci.DeadlinePassed("cut short")
            clock.t += 20
            return real(name, args, seconds)
        fake.call = slow
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ci.main(["HEAD", "--wait", "--timeout", "100"], tools=fake, clock=clock, sleep=clock.sleep,
                           now=lambda: COMMITTED + timedelta(minutes=5))
        self.assertEqual(code, 3)
        self.assertIn("still pending", out.getvalue())
        self.assertTrue(all(0 < seconds <= ci.CALL_SECONDS for _, _, seconds in fake.calls), fake.calls)
        self.assertTrue(any(seconds < ci.CALL_SECONDS for _, _, seconds in fake.calls), "never bounded by time left")
        self.assertEqual(clock.t - 1000, 100)  # it neither stopped early nor ran past the timeout

    def test_a_run_turning_green_in_the_last_seconds_is_seen(self):
        # Polls at 0, 30, 60 and 90 s, then one last at 99 s: a run that turns green at 98 s is green.
        pending = [run(status="in_progress", conclusion="")]
        code, _ = self.main(Fake(runs=[pending] * 4 + [[run()]]), "--wait", "--timeout", "100")
        self.assertEqual(code, 0)
        self.assertEqual(self.clock.t - 1000, 99)

    def test_no_call_is_made_after_the_deadline(self):
        # Two git calls of 40 s spend a 60 s wait, so gh never starts.
        clock = Clock()
        fake = Fake()
        real = fake.call

        def slow(name, args, seconds):  # a call that honours its deadline, as subprocess.run's timeout does
            self.assertGreater(seconds, 0)
            if name == "git":
                if 40 > seconds:
                    clock.t += seconds
                    raise ci.DeadlinePassed("cut short")
                clock.t += 40
            return real(name, args, seconds)
        fake.call = slow
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ci.main(["HEAD", "--wait", "--timeout", "60"], tools=fake, clock=clock, sleep=clock.sleep,
                           now=lambda: COMMITTED + timedelta(minutes=5))
        self.assertEqual(code, 2)
        self.assertIn("unknown HEAD: cut short", out.getvalue())  # the first look: no earlier result to keep
        self.assertFalse([c for c in fake.calls if c[0] == "gh"])

    def test_a_call_is_never_given_no_time(self):
        # Two git calls of 30 s use exactly a 60 s wait: the gh call would get 0 s, so it is never made.
        clock = Clock()
        fake = Fake()
        real = fake.call

        def exact(name, args, seconds):
            self.assertGreater(seconds, 0, f"{name} {args[0]} was given no time")
            if name == "git":
                clock.t += 30
            return real(name, args, seconds)
        fake.call = exact
        with contextlib.redirect_stdout(io.StringIO()):
            code = ci.main(["HEAD", "--wait", "--timeout", "60"], tools=fake, clock=clock, sleep=clock.sleep,
                           now=lambda: COMMITTED + timedelta(minutes=5))
        self.assertEqual(code, 2)
        self.assertFalse([c for c in fake.calls if c[0] == "gh"])

    def test_a_hung_gh_is_unknown_within_its_deadline(self):
        hung = ci.Unknown("gh run did not answer within 60 seconds")
        code, out = self.main(Fake(fail={"gh run list": hung}), "--wait", "--timeout", "600")
        self.assertEqual(code, 2)
        self.assertIn("did not answer", out)


class RealCalls(unittest.TestCase):
    """Tools.call itself: a program that hangs is ended at its deadline and reported as Unknown."""

    def test_a_hung_program_is_unknown_at_its_deadline(self):
        dispatch = ci.todo_graph.review_dispatch()
        started = time.monotonic()
        with mock.patch.object(dispatch, "find_cli", lambda name: sys.executable), \
                mock.patch.object(ci, "CALL_SECONDS", 1):  # its own allowance, not the wait's deadline, runs out
            with self.assertRaises(ci.Unknown) as caught:
                ci.Tools().call("gh", ["-c", "import time; time.sleep(30)"], 1)
        self.assertLess(time.monotonic() - started, 15)
        self.assertIn("did not answer within 1 seconds", str(caught.exception))

    def test_a_call_gets_exactly_the_time_left(self):
        dispatch = ci.todo_graph.review_dispatch()
        with mock.patch.object(dispatch, "find_cli", lambda name: sys.executable), \
                mock.patch.object(ci.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")) as ran:
            ci.Tools().call("gh", ["run", "list"], 0.125)
        self.assertEqual(ran.call_args.kwargs["timeout"], 0.125)
        with self.assertRaises(ci.DeadlinePassed):
            ci.Tools().call("gh", ["run", "list"], 0)

    def test_a_call_cut_short_by_the_wait_is_a_passed_deadline(self):
        dispatch = ci.todo_graph.review_dispatch()
        with mock.patch.object(dispatch, "find_cli", lambda name: sys.executable), \
                self.assertRaises(ci.DeadlinePassed):
            ci.Tools().call("gh", ["-c", "import time; time.sleep(30)"], 0.5)

    def test_a_missing_program_is_unknown(self):
        dispatch = ci.todo_graph.review_dispatch()
        with mock.patch.object(dispatch, "find_cli", lambda name: None), self.assertRaises(ci.Unknown):
            ci.Tools().call("gh", ["run", "list"], 5)



def sha(n):
    """A distinct SHA whose 7-character prefix, as run files record it, is distinct too."""
    return f"{n:07x}" + "c" * 33


class Repo:
    """A scripted clone and GitHub for --pending: a first-parent history (newest first), push runs by head, and what
    `git fetch` brings in."""

    def __init__(self, history, runs, fetched=None, fail=None, ahead=0, local=None, total=None, extra_runs=()):
        self.history = list(history)
        self.total = total  # the API's total_count, when it should differ from the runs served
        self.extra_runs = list(extra_runs)  # further raw API runs (an older attempt of a head, another branch)
        self.pages_read = []
        self.after_page = {}  # page number -> a function run after that page is served (a run created mid-scan)
        self.fail_pages = set()  # page numbers that fail once
        self.attempts = {}  # head -> attempt number, to model a rerun
        self.ahead = ahead  # local commits origin/main lacks
        self.local = local  # the clone's HEAD when it is not origin/main
        self.fetched = fetched
        self.runs = runs  # head -> conclusion ("success", "failure", or None while in progress)
        self.fail = fail or {}
        self.calls = []

    def api_runs(self):
        """The workflow's runs as the API lists them, newest first."""
        runs = [{"id": int(h[:7], 16), "status": "completed" if c else "in_progress", "conclusion": c,
                 "created_at": "2026-10-23T10:00:05Z", "head_sha": h, "event": "push", "head_branch": "main",
                 "run_attempt": self.attempts.get(h, 1)}
                for h, c in self.runs.items()] + self.extra_runs
        return list(reversed(runs))

    def run_record(self, head):
        conclusion = self.runs[head]
        return run(headSha=head, databaseId=int(head[:7], 16), status="completed" if conclusion else "in_progress",
                   conclusion=conclusion or "", attempt=self.attempts.get(head, 1))

    def call(self, name, args, seconds):
        self.calls.append((name, list(args)))
        key = f"{name} {args[0]}"
        if key in self.fail:
            return subprocess.CompletedProcess(args, 1, "", self.fail[key])
        out = None
        if name == "git" and args[0] == "fetch":
            if self.fetched is not None:
                self.history = self.fetched
            out = ""
        elif name == "git" and args[:2] == ["rev-list", "--count"]:
            out = f"{self.ahead}\n"
        elif name == "git" and args[0] == "rev-list":
            limit = next((int(a.split("=")[1]) for a in args if a.startswith("--max-count=")), None)
            out = "\n".join(self.history[:limit]) + "\n"
        elif name == "git" and args[0] == "rev-parse":
            ref = args[2].split("^")[0]
            if ref == "HEAD":
                out = (self.local or (sha(999) if self.ahead else self.history[0])) + "\n"
            else:
                out = (self.history[0] if ref == "origin/main" else ref) + "\n"
        elif name == "git" and args[0] == "show":
            out = COMMITTED.isoformat() + "\n"
        elif name == "git" and args[0] == "remote":
            out = "https://github.com/rizonesoft/Office.git\n"
        elif args[:2] == ["run", "list"] and "--commit" in args:
            head = args[args.index("--commit") + 1]
            out = json.dumps([self.run_record(head)] if head in self.runs else [])
        elif args[0] == "api":
            url = args[-1]
            self.pages_read.append(url)
            runs = self.api_runs()
            if "branch=" in url or "event=" in url:  # GitHub caps a filtered search at 1,000 results
                runs = [r for r in runs if r["event"] == "push" and r["head_branch"] == "main"][:1000]
            page = int(re.search(r"[?&]page=(\d+)", url)[1]) if "page=" in url else 1
            if page in self.fail_pages:
                self.fail_pages.discard(page)
                return subprocess.CompletedProcess(args, 1, "", "HTTP 502")
            total = len(runs) if self.total is None else self.total
            out = json.dumps({"total_count": total, "workflow_runs": runs[(page - 1) * 100:page * 100]})
            self.after_page.pop(page, lambda: None)()
        elif args[:2] == ["run", "view"]:
            out = json.dumps({"jobs": []})
        if out is None:
            raise AssertionError(f"unexpected call {name} {args}")
        return subprocess.CompletedProcess(args, 0, out, "")


class Pending(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        self.run_file = self.dir / "2026-10-23-phase-0.md"

    def record(self, *lines, name=None):
        path = self.dir / (name or self.run_file.name)
        path.write_text("# Phase run\n\n## Critical events\n\n" + "".join(f"- {line}\n" for line in lines),
                        encoding="utf-8")

    def pending(self, repo, *extra, clock=None):
        clock = clock or Clock()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ci.main(["--pending", str(self.run_file), *extra], tools=repo, clock=clock, sleep=clock.sleep,
                           now=lambda: COMMITTED + timedelta(minutes=30), checkpoint=self.dir / "ci-reconcile.json")
        return code, out.getvalue()

    def listed(self, out):
        words = [line.split() for line in out.splitlines() if line.strip()]
        return [w[1].rstrip(":") for w in words if w[0] in ("green", "red", "pending", "unknown") and len(w) > 1
                and len(w[1].rstrip(":")) == 7]

    def test_unrecorded_merge_closeout_and_stamp_pushes_are_listed(self):
        base, merge, closeout, stamp = sha(1), sha(2), sha(3), sha(4)
        self.record(f"ci-green {base[:7]}")
        code, out = self.pending(Repo([stamp, closeout, merge, base],
                                      {base: "success", merge: "success", closeout: "success", stamp: "success"}))
        self.assertEqual(code, 0)
        self.assertEqual(self.listed(out), [merge[:7], closeout[:7], stamp[:7]])

    def test_commits_pushed_with_their_stamp_are_covered_by_it(self):
        base, impl1, impl2, stamp = sha(1), sha(2), sha(3), sha(4)
        self.record(f"ci-green {base[:7]}")
        code, out = self.pending(Repo([stamp, impl2, impl1, base], {base: "success", stamp: "success"}))
        self.assertEqual(self.listed(out), [stamp[:7]])

    def test_a_later_green_head_never_covers_an_earlier_unchecked_one(self):
        base, a, b = sha(1), sha(2), sha(3)
        self.record(f"ci-green {base[:7]}", f"ci-green {b[:7]}")
        code, out = self.pending(Repo([b, a, base], {base: "success", a: "failure", b: "success"}))
        self.assertEqual(code, 1)
        self.assertEqual(self.listed(out), [a[:7]])

    def test_a_recorded_pending_push_is_a_head_even_without_a_run_yet(self):
        base, stamp = sha(1), sha(2)
        self.record(f"ci-green {base[:7]}", f"ci-pending {stamp[:7]} 2026-10-23T10:00:00Z")
        code, out = self.pending(Repo([sha(3), stamp, base], {base: "success"}))
        self.assertIn(stamp[:7], self.listed(out))

    def test_an_outcome_record_alone_makes_a_head_and_the_baseline(self):
        # Review round 1 of D00 T03 §17, finding 2: A's run is no longer returned; its ci-green record still counts.
        a, b, c = sha(1), sha(2), sha(3)
        self.record(f"ci-green {a[:7]}")
        code, out = self.pending(Repo([c, b, a], {b: "failure", c: "success"}))
        self.assertIn(f"baseline {a[:7]}", out)
        self.assertEqual(self.listed(out), [b[:7], c[:7]])
        self.assertEqual(code, 1)

    def test_a_recorded_outcome_off_the_history_is_unknown(self):
        self.record(f"ci-green {sha(9)[:7]}")
        code, out = self.pending(Repo([sha(2), sha(1)], {sha(1): "success", sha(2): "success"}))
        self.assertEqual(code, 2)
        self.assertIn("no recorded outcome is on origin/main's history", out)

    def test_more_than_one_page_of_runs_is_read_in_full(self):
        # D00 T03 §20: no page cap; 650 push runs, the unchecked head among the oldest.
        heads = [sha(n) for n in range(1, 651)]
        unchecked = heads[1]
        self.record(f"ci-green {heads[0][:7]}", *(f"ci-green {h[:7]}" for h in heads[2:]))
        code, out = self.pending(Repo(list(reversed(heads)), {h: "success" for h in heads}))
        self.assertEqual(self.listed(out), [unchecked[:7]])
        self.assertEqual(code, 0)

    def test_runs_short_of_the_total_count_are_unknown(self):
        self.record(f"ci-green {sha(1)[:7]}")
        code, out = self.pending(Repo([sha(1)], {sha(1): "success"}, total=1001))
        self.assertEqual(code, 2)
        self.assertIn("returned 1 of 1001 runs", out)

    def test_a_history_longer_than_any_window_is_read_to_the_baseline(self):
        # D00 T03 §20: 5,200 first-parent commits; the baseline and an unchecked head lie beyond the old 5,000 window.
        base, unchecked, tip = sha(1), sha(2), sha(3)
        filler = [sha(1000 + n) for n in range(5200)]
        self.record(f"ci-green {base[:7]}", f"ci-green {tip[:7]}")
        code, out = self.pending(Repo([tip, *filler, unchecked, base], {base: "success", unchecked: "success",
                                                                         tip: "success"}))
        self.assertEqual(self.listed(out), [unchecked[:7]])
        self.assertEqual(code, 0)

    def test_an_earliest_run_baseline_needs_no_older_run(self):
        first, later = sha(1), sha(2)  # the workflow's first run is the green baseline
        code, out = self.pending(Repo([later, first], {first: "success", later: "failure"}))
        self.assertIn(f"baseline {first[:7]}", out)
        self.assertEqual(self.listed(out), [later[:7]])

    def test_an_empty_workflow_history_lists_every_head(self):
        tip = sha(1)
        code, out = self.pending(Repo([tip], {}))
        self.assertIn("no baseline", out)
        self.assertEqual(self.listed(out), [tip[:7]])

    def test_several_pages_with_no_green_run_list_every_head(self):
        heads = [sha(n) for n in range(1, 251)]
        code, out = self.pending(Repo(list(reversed(heads)), {h: "failure" for h in heads}))
        self.assertIn("no baseline", out)
        self.assertEqual(len(self.listed(out)), 250)
        self.assertEqual(code, 1)

    def test_red_then_pending_and_red_then_red_report_both_heads(self):
        # D00 T03 §20: --pending reports each head's state so the skill can settle the newest first.
        base, a, b = sha(1), sha(2), sha(3)
        for newest, state, code_wanted in ((None, "pending", 1), ("failure", "red", 1)):
            with self.subTest(newest=state):
                self.record(f"ci-green {base[:7]}")
                code, out = self.pending(Repo([b, a, base], {base: "success", a: "failure", b: newest}))
                self.assertEqual(self.listed(out), [a[:7], b[:7]])
                self.assertIn(f"red {a[:7]}", out)
                self.assertIn(f"{state} {b[:7]}", out)
                self.assertEqual(code, code_wanted)

    def test_every_head_with_an_outcome_lists_nothing(self):
        base, a, b = sha(1), sha(2), sha(3)
        self.record(f"ci-green {base[:7]}", f"ci-superseded {a[:7]} by {b[:7]}", f"ci-green {b[:7]}")
        code, out = self.pending(Repo([b, a, base], {base: "success", a: "failure", b: "success"}))
        self.assertEqual((code, self.listed(out)), (0, []))
        self.assertIn("0 unchecked push head(s)", out)

    def test_a_clone_behind_the_fetched_head_is_unknown_until_it_fast_forwards(self):
        # Review round 8 of D00 T03 §17: records from a stale checkout, or a head the pull then moves past, never pass.
        base, new = sha(1), sha(2)
        self.record(f"ci-green {base[:7]}")
        code, out = self.pending(Repo([base], {base: "success", new: "success"}, fetched=[new, base], local=base))
        self.assertEqual(code, 2)
        self.assertIn("fast-forward", out)

    def test_the_remote_is_fetched_before_enumeration(self):
        base, new = sha(1), sha(2)
        self.record(f"ci-green {base[:7]}")
        repo = Repo([base], {base: "success", new: "failure"}, fetched=[new, base], local=new)
        code, out = self.pending(repo)
        self.assertEqual(code, 1)
        self.assertEqual(self.listed(out), [new[:7]])
        self.assertEqual(repo.calls[0][1][:1], ["fetch"])

    def test_a_clone_ahead_of_origin_is_unknown_until_it_pushes(self):
        # Review round 7 of D00 T03 §17: a stamp commit left unpushed must not pass as reconciled.
        self.record(f"ci-green {sha(1)[:7]}")
        code, out = self.pending(Repo([sha(1)], {sha(1): "success"}, ahead=1))
        self.assertEqual(code, 2)
        self.assertIn("HEAD has 1 commit(s) origin/main lacks", out)
        self.assertEqual(self.pending(Repo([sha(1)], {sha(1): "success"}, ahead=0))[0], 0)

    def test_a_failed_fetch_is_unknown(self):
        self.record(f"ci-green {sha(1)[:7]}")
        code, out = self.pending(Repo([sha(1)], {sha(1): "success"}, fail={"git fetch": "network"}))
        self.assertEqual(code, 2)
        self.assertIn("git fetch origin main failed", out)

    def test_the_first_run_baseline_is_the_newest_green_push_head(self):
        old, green, after = sha(1), sha(2), sha(3)
        repo = lambda: Repo([after, green, old], {old: "failure", green: "success", after: "failure"})
        for setup in ("no run file", "empty run file", "no outcome recorded"):
            with self.subTest(setup=setup):
                for f in self.dir.glob("*.md"):
                    f.unlink()
                if setup == "empty run file":
                    self.run_file.write_text("", encoding="utf-8")
                elif setup == "no outcome recorded":
                    self.record("run opened", name="2026-10-22-phase-2.md")
                code, out = self.pending(repo())
                self.assertIn(f"baseline {green[:7]}", out)
                self.assertEqual(self.listed(out), [after[:7]])

    def test_the_first_run_baseline_uses_each_heads_governing_run(self):
        # Review round 3 of D00 T03 §17, finding 1: an older success under a newer failure is not green.
        a = sha(1)
        older = {"id": 999999, "status": "completed", "conclusion": "success", "created_at": "2026-10-23T09:00:00Z",
                 "head_sha": a, "event": "push", "head_branch": "main"}
        code, out = self.pending(Repo([a], {a: "failure"}, extra_runs=[older]))
        self.assertIn("no baseline", out)
        self.assertEqual(self.listed(out), [a[:7]])

    def test_with_no_green_run_every_head_is_listed(self):
        a, b = sha(1), sha(2)
        code, out = self.pending(Repo([b, a], {a: "failure", b: "failure"}))
        self.assertIn("no baseline", out)
        self.assertEqual(self.listed(out), [a[:7], b[:7]])

    def test_an_unreadable_run_file_is_unknown(self):
        (self.dir / "2026-10-22-phase-1.md").write_bytes(b"\xff\xfe not utf-8")
        code, out = self.pending(Repo([sha(1)], {sha(1): "success"}))
        self.assertEqual(code, 2)
        self.assertIn("cannot read the run file", out)

    def test_a_page_that_cannot_be_read_is_unknown(self):
        self.record(f"ci-green {sha(1)[:7]}")
        code, _ = self.pending(Repo([sha(1)], {sha(1): "success"}, fail={"gh api": "HTTP 502"}))
        self.assertEqual(code, 2)


class Scale(Pending):
    """D00 T03 §22: past the 1,000-result search cap, across tries, with a checkpoint bound to its inputs."""

    def slow_clock_repo(self, repo, page_seconds=0, head_seconds=0):
        clock = Clock()
        real = repo.call

        def call(name, args, seconds):
            cost = page_seconds if args[:1] == ["api"] else head_seconds if args[:2] == ["run", "list"] else 0
            if cost > seconds:
                clock.t += seconds
                raise ci.DeadlinePassed("cut short")
            clock.t += cost
            return real(name, args, seconds)
        repo.call = call
        return clock

    def test_more_than_a_thousand_runs_are_read_from_the_unfiltered_pages(self):
        heads = [sha(n) for n in range(1, 1101)]
        self.record(f"ci-green {heads[0][:7]}", *(f"ci-green {h[:7]}" for h in heads[2:]))
        repo = Repo(list(reversed(heads)), {h: "success" for h in heads})
        code, out = self.pending(repo)
        self.assertEqual((code, self.listed(out)), (0, [heads[1][:7]]))
        self.assertFalse([u for u in repo.pages_read if "branch=" in u or "event=" in u])
        self.assertEqual(len(repo.pages_read), 12)  # 1,100 runs, 100 a page, the last page short

    def test_late_pushes_shuffled_dates_and_other_branches_still_find_every_head(self):
        base, a, b = sha(1), sha(2), sha(3)
        others = [{"id": 50000 + n, "status": "completed", "conclusion": "success",
                   "created_at": f"2026-10-2{n % 9}T00:00:00Z", "head_sha": sha(900 + n),
                   "event": "pull_request" if n % 2 else "push", "head_branch": "main" if n % 2 else "feature"}
                  for n in range(250)]  # whole pages hold only other branches or events, with dates in any order
        self.record(f"ci-green {base[:7]}")
        repo = Repo([b, a, base], {base: "success", a: "success", b: "success"}, extra_runs=others)
        code, out = self.pending(repo)
        self.assertEqual(self.listed(out), [a[:7], b[:7]])

    def test_an_unchanged_try_reads_no_page_twice_and_a_push_is_found_on_the_next(self):
        old = [sha(n) for n in range(10, 260)]  # three pages of older, recorded history
        base, a, new = sha(1), sha(2), sha(3)
        self.record(*(f"ci-green {h[:7]}" for h in old), f"ci-green {base[:7]}")
        repo = Repo([a, base, *reversed(old)], {**{h: "success" for h in old}, base: "success", a: "success"})
        self.pending(repo)
        read = len(repo.pages_read)
        self.pending(repo)  # same inputs: the scan is not repeated; only the newest page is read again for reruns
        self.assertEqual(repo.pages_read[read:], [repo.pages_read[0]])
        repo.history, repo.runs[new] = [new, a, base, *reversed(old)], "failure"  # a push and its run land between tries
        code, out = self.pending(repo)
        self.assertEqual(self.listed(out), [a[:7], new[:7]])
        self.assertEqual(code, 1)
        # Two more pushes land between tries; the first is a head only through its run, which only a refresh finds.
        first, second = sha(4), sha(5)
        repo.history = [second, first, new, a, base]
        repo.runs[first], repo.runs[second] = "failure", "success"
        code, out = self.pending(repo)
        self.assertIn(first[:7], self.listed(out))

    def test_pages_read_before_a_failure_are_kept(self):
        heads = [sha(n) for n in range(1, 701)]
        self.record(f"ci-green {heads[0][:7]}", *(f"ci-green {h[:7]}" for h in heads[1:]))
        repo = Repo(list(reversed(heads)), {h: "success" for h in heads})
        repo.fail_pages = {5}
        self.assertEqual(self.pending(repo)[0], 2)  # page 5 failed after pages 1 to 4 were read
        before = len(repo.pages_read)
        self.assertEqual(self.pending(repo)[0], 0)
        pages = [u.rsplit("=", 1)[1] for u in repo.pages_read[before:]]
        self.assertEqual(pages, ["1", "5", "6", "7", "8"])  # the newest page again for new runs, then on from page 5

    def test_a_stored_red_result_is_reported_after_an_interruption(self):
        base, a, b = sha(1), sha(2), sha(3)
        self.record(f"ci-green {base[:7]}")
        repo = Repo([b, a, base], {base: "success", a: "failure", b: "success"})
        # The first try settles A (red), then runs out of time on B.
        clock = self.slow_clock_repo(repo, head_seconds=55)
        with mock.patch.object(ci, "PENDING_SECONDS", 100):
            code, out = self.pending(repo, clock=clock)
        self.assertEqual(code, ci.PROGRESSING)
        lookups = len([c for c in repo.calls if c[1][:2] == ["run", "list"]])
        code, out = self.pending(repo)  # the next try reports A from the checkpoint and settles B
        self.assertEqual(len([c for c in repo.calls if c[1][:2] == ["run", "list"]]) - lookups, 1)  # only B
        self.assertEqual(code, 1)
        self.assertIn(f"red {a[:7]}", out)
        self.assertIn(f"green {b[:7]}", out)

    def test_heads_settled_between_saves_are_kept_at_the_deadline(self):
        base, a, b, c = sha(1), sha(2), sha(3), sha(4)
        self.record(f"ci-green {base[:7]}")
        repo = Repo([c, b, a, base], {base: "success", a: "success", b: "failure", c: "success"})
        clock = self.slow_clock_repo(repo, head_seconds=1)  # A and B settle within one save interval, C is cut short
        with mock.patch.object(ci, "PENDING_SECONDS", 2.5):
            self.assertEqual(self.pending(repo, clock=clock)[0], ci.PROGRESSING)
        lookups = len([c for c in repo.calls if c[1][:2] == ["run", "list"]])
        code, out = self.pending(repo)
        self.assertEqual(len([c for c in repo.calls if c[1][:2] == ["run", "list"]]) - lookups, 1)  # only C
        self.assertEqual(code, 1)

    def test_a_rerun_between_interrupted_tries_replaces_a_stored_result(self):
        base, a, b = sha(1), sha(2), sha(3)
        self.record(f"ci-green {base[:7]}")
        repo = Repo([b, a, base], {base: "success", a: "success", b: "success"})
        clock = self.slow_clock_repo(repo, head_seconds=55)
        with mock.patch.object(ci, "PENDING_SECONDS", 100):
            self.assertEqual(self.pending(repo, clock=clock)[0], ci.PROGRESSING)  # A settled green, B cut short
        repo.runs[a], repo.attempts[a] = "failure", 2  # A is rerun and fails
        code, out = self.pending(repo)
        self.assertEqual(code, 1)
        self.assertIn(f"red {a[:7]} run {int(a[:7], 16)} attempt 2", out)

    def test_a_delayed_run_is_found_without_a_change_of_head_or_records(self):
        base, a, b = sha(1), sha(2), sha(3)
        self.record(f"ci-green {base[:7]}")
        repo = Repo([b, a, base], {base: "success", b: "success"})  # A's push run has not started yet
        code, out = self.pending(repo)
        self.assertEqual((code, self.listed(out)), (0, [b[:7]]))
        repo.runs = {a: "failure", **repo.runs}  # A's run arrives; it is the newest run
        code, out = self.pending(repo)
        self.assertEqual((code, self.listed(out)), (1, [a[:7], b[:7]]))

    def test_a_rerun_on_the_same_conclusion_is_reported_on_its_new_attempt(self):
        base, a = sha(1), sha(2)
        self.record(f"ci-green {base[:7]}")
        repo = Repo([a, base], {base: "success", a: "failure"})
        self.assertEqual(self.pending(repo)[0], 1)
        repo.attempts[a] = 2  # rerun, and it failed again
        code, out = self.pending(repo)
        self.assertIn(f"red {a[:7]} run {int(a[:7], 16)} attempt 2", out)

    def test_a_run_created_during_the_scan_is_found_in_the_same_try(self):
        old = [sha(n) for n in range(10, 260)]
        base, a = sha(1), sha(2)
        self.record(*(f"ci-green {h[:7]}" for h in old), f"ci-green {base[:7]}")
        repo = Repo([base, *reversed(old)], {**{h: "success" for h in old}, base: "success"})

        def push():  # a run is created while page 2 is read, pushing every older run one place down
            repo.runs[a] = "failure"
        repo.after_page[2] = push
        code, out = self.pending(repo)
        self.assertEqual(code, 0)
        self.assertNotIn("cut off", out)

    def test_a_rerun_of_a_first_run_baseline_past_the_first_page_is_seen(self):
        tip = sha(1)
        others = [{"id": 70000 + n, "status": "completed", "conclusion": "success", "created_at": "2026-10-23T11:00:00Z",
                   "head_sha": sha(500 + n), "event": "pull_request", "head_branch": "feature"} for n in range(150)]
        repo = Repo([tip], {tip: "success"}, extra_runs=others)  # newer runs of other branches fill page 1
        self.assertIn(f"baseline {tip[:7]}", self.pending(repo)[1])
        repo.runs[tip], repo.attempts[tip] = "failure", 2
        code, out = self.pending(repo)
        self.assertEqual((code, self.listed(out)), (1, [tip[:7]]))

    def test_a_rerun_of_the_first_run_baseline_is_seen(self):
        tip = sha(1)
        repo = Repo([tip], {tip: "success"})  # no outcome recorded: the green tip is the first-run baseline
        code, out = self.pending(repo)
        self.assertIn(f"baseline {tip[:7]}", out)
        repo.runs[tip], repo.attempts[tip] = "failure", 2
        code, out = self.pending(repo)
        self.assertEqual((code, self.listed(out)), (1, [tip[:7]]))

    def test_a_pending_head_is_checked_again_and_a_rerun_replaces_a_stored_result(self):
        base, a = sha(1), sha(2)
        self.record(f"ci-green {base[:7]}")
        repo = Repo([a, base], {base: "success", a: None})
        self.assertEqual(self.pending(repo)[0], 3)
        repo.runs[a] = "failure"
        self.assertEqual(self.pending(repo)[0], 1)  # the pending head was checked again
        repo.runs[a], repo.attempts[a] = "success", 2  # a rerun turned it green
        code, out = self.pending(repo)
        self.assertEqual(code, 0)
        self.assertIn(f"green {a[:7]} run", out)

    def test_the_checkpoint_survives_until_acknowledged(self):
        base, a = sha(1), sha(2)
        self.record(f"ci-green {base[:7]}")
        repo = Repo([a, base], {base: "success", a: "success"})
        self.pending(repo)
        cp = self.dir / "ci-reconcile.json"
        self.assertTrue(cp.exists())  # the records are not written yet: the work is kept
        read = len(repo.pages_read)
        self.assertEqual(self.pending(repo)[0], 0)
        self.assertEqual(len(repo.pages_read), read + 1)  # only the newest page again, for reruns
        self.assertEqual(self.pending(repo, "--ack")[0], 0)
        self.assertFalse(cp.exists())

    def test_a_long_reconciliation_completes_over_several_tries(self):
        # 2,000 runs at 25 s a page (20 pages, 500 s) and 16 unchecked heads at 50 s each (800 s): paging alone takes
        # longer than a call and settling longer than a 600 s try; each call stays bounded, every try saves progress,
        # and a head settled in an interrupted try is not looked up again, so the third try completes.
        heads = [sha(n) for n in range(1, 2001)]
        unchecked = heads[-16:]
        self.record(f"ci-green {heads[0][:7]}", *(f"ci-green {h[:7]}" for h in heads[1:-16]))
        repo = Repo(list(reversed(heads)), {h: "success" for h in heads})
        codes = []
        for _ in range(10):
            clock = self.slow_clock_repo(repo, page_seconds=25, head_seconds=50)
            code, out = self.pending(repo, clock=clock)
            codes.append(code)
            if code != ci.PROGRESSING:
                break
        self.assertGreaterEqual(codes.count(ci.PROGRESSING), 2)
        self.assertEqual(codes[-1], 0)
        self.assertEqual(self.listed(out), [h[:7] for h in unchecked])

    def test_a_large_backlog_on_slow_pages_completes_over_several_tries(self):
        # 2,500 runs at 30 s a page (25 pages, 750 s) and every head but the oldest unchecked: the runs the heads rest
        # on cannot all be read in one 600 s try, so the pass's cursor carries over and every try still progresses.
        heads = [sha(n) for n in range(1, 2501)]
        self.record(f"ci-green {heads[0][:7]}")
        repo = Repo(list(reversed(heads)), {h: "success" for h in heads})
        codes = []
        for _ in range(8):
            clock = self.slow_clock_repo(repo, page_seconds=30)
            code, out = self.pending(repo, clock=clock)
            codes.append(code)
            if code != ci.PROGRESSING:
                break
        self.assertEqual(codes[-1], 0)
        self.assertTrue(all(c == ci.PROGRESSING for c in codes[:-1]))
        self.assertEqual(len(self.listed(out)), 2499)

    def test_reading_a_new_pass_across_tries_is_progress(self):
        # A finished reconciliation of 2,500 pending runs; the next one must read them all again in its own pass, which
        # takes longer than one try: the pages its cursor reads are progress, though they change nothing.
        heads = [sha(n) for n in range(1, 2501)]
        self.record(f"ci-green {heads[0][:7]}")
        repo = Repo(list(reversed(heads)), {heads[0]: "success", **{h: None for h in heads[1:]}})
        for _ in range(8):
            if self.pending(repo, clock=self.slow_clock_repo(repo, page_seconds=30))[0] != ci.PROGRESSING:
                break
        code, out = self.pending(repo, clock=self.slow_clock_repo(repo, page_seconds=30))
        self.assertEqual(code, ci.PROGRESSING)
        self.assertEqual(self.pending(repo, clock=self.slow_clock_repo(repo, page_seconds=30))[0], 3)

    def test_a_try_without_progress_is_unknown(self):
        self.record(f"ci-green {sha(1)[:7]}")
        repo = Repo([sha(1)], {sha(1): "success"})
        clock = self.slow_clock_repo(repo, page_seconds=700)  # no page fits in a call, so nothing is ever saved
        code, out = self.pending(repo, clock=clock)
        self.assertEqual(code, 2)
        self.assertIn("no progress", out)


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

    def test_a_log_that_cannot_be_written_is_reported_and_the_status_stands(self):
        target = self.tmp / "ci.log"
        with mock.patch.object(Path, "mkdir", side_effect=PermissionError(13, "Access is denied")):
            code, out = self.main(Fake(runs=[[run(conclusion="failure")]], log="x"), "--log", str(target))
        self.assertEqual(code, 1)
        self.assertIn("red aaaaaaa", out)
        self.assertIn("log not written: Access is denied", out)
        self.assertFalse(target.exists())

    def test_a_log_that_cannot_be_read_is_reported_and_the_status_stands(self):
        fake = Fake(runs=[[run(conclusion="failure")]], fail={"gh run view": "HTTP 500"})
        code, out = self.main(fake, "--log", str(self.tmp / "ci.log"))
        self.assertEqual(code, 1)
        self.assertIn("log not written", out)
        self.assertIn("the failing jobs could not be read", out)


if __name__ == "__main__":
    unittest.main()
