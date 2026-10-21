# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/campaign_guard.py, the process-plan run guard: the Stop hook against a throwaway workspace, and the
lifecycle commands.

The guard and the Stop hook wiring are read from this repository.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
GUARD_PY = REPO / "scripts" / "campaign_guard.py"
SESSION = "11111111-2222-3333-4444-555555555555"
OTHER = "99999999-8888-7777-6666-555555555555"
RUN_FILE = "docs/phase-runs/2099-01-01-phase-0.md"

spec = importlib.util.spec_from_file_location("campaign_guard_under_test", GUARD_PY)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

# The fake graph answers `query ready` the way the test asks: this repository's JSON list, or Isotone's text summary.
FAKE_GRAPH = """import json, os, sys
if sys.argv[2:3] == ["stats"]:  # open rows from open.txt (none when absent)
    path = os.path.join(os.path.dirname(__file__), 'open.txt')
    still_open = int(open(path).read()) if os.path.exists(path) else 0
    print(json.dumps({"total": 10, "verified": 10 - still_open}))
    sys.exit(0)
mode, n = open(os.path.join(os.path.dirname(__file__), 'ready.txt')).read().split()
rows = [{"ref": "D00 T01 \\u00a73", "title": "Interface SPEC and screenshots", "phase": 0}] * int(n)
if mode == "mixed":  # this phase's rows, and one ready row of a later phase
    print(json.dumps(rows + [{"ref": "D05 T01 \\u00a71", "title": "Kit manager", "phase": 5}]))
elif mode == "json":
    print(json.dumps(rows, indent=2))
elif mode == "crash":
    sys.exit(1)
elif mode == "sleep":
    import time
    time.sleep(int(n))
else:
    if rows:
        print("00-design/TODO-01.md \\u00a73  Interface SPEC and screenshots")
    print()
    print(f"{n} runnable now, 0 runnable elsewhere")
"""


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self._tmp.name, "ws")
        for folder in ("scripts", "build", "docs/phase-runs"):
            os.makedirs(os.path.join(self.root, folder))
        shutil.copy(GUARD_PY, os.path.join(self.root, "scripts", "campaign_guard.py"))
        self.write("scripts/todo-graph.py", FAKE_GRAPH)
        self.write(".gitignore", "build/\nscripts/ready.txt\nscripts/open.txt\n")
        self.ready(3)
        self.write(RUN_FILE, "# Phase run: Phase 0\n\n## Critical events\n")
        for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"],
                     ["config", "commit.gpgsign", "false"], ["add", "-A"], ["commit", "-qm", "seed"]):
            subprocess.run(["git", *args], cwd=self.root, capture_output=True, check=True)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text, mode="w"):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode, encoding="utf-8", newline="\n") as fh:
            fh.write(text)

    def ready(self, n, mode="json"):
        self.write("scripts/ready.txt", f"{mode} {n}")

    def acquire(self, session=SESSION, **kw):
        cron_id = kw.pop("cron_id", "job-1")
        return guard.acquire(self.root, session, 0, RUN_FILE, cron_id, **kw)

    def run_id(self):
        return guard.read_guard(self.root)["run_id"]

    def hook(self, session=SESSION, payload=None):
        code, out = guard.stop_hook(payload if payload is not None else
                                    json.dumps({"session_id": session, "cwd": self.root, "hook_event_name": "Stop"}),
                                    self.root)
        self.assertEqual(code, 0, "the hook always exits 0")
        return json.loads(out) if out else None

    def state(self):
        return guard._read_state(self.root)


class StopHook(Workspace):
    def test_no_guard_another_session_or_an_empty_payload_allows(self):
        self.assertIsNone(self.hook())
        self.acquire()
        self.assertIsNone(self.hook(session=OTHER))
        self.assertIsNone(self.hook(payload=""))

    def test_an_open_run_blocks_and_names_the_next_ready_row(self):
        self.acquire()
        decision = self.hook()
        self.assertEqual(decision["decision"], "block")
        self.assertIn("Next ready row: D00 T01 §3  Interface SPEC and screenshots.", decision["reason"])
        self.assertIn(f"## Closeout run={self.run_id()}", decision["reason"])
        self.assertEqual(self.state()["blocks"], 1)

    def test_a_text_summary_graph_is_read_too(self):
        self.acquire()
        self.ready(2, "text")
        self.assertIn("Next ready row: 00-design/TODO-01.md", self.hook()["reason"])
        self.ready(0, "text")
        self.assertIsNone(self.hook())

    def test_nothing_runnable_allows(self):
        self.acquire()
        self.ready(0)
        self.assertIsNone(self.hook())

    def test_an_unreadable_graph_still_blocks(self):
        self.acquire()
        self.ready(0, "crash")
        self.assertEqual(self.hook()["decision"], "block")

    def test_only_this_runs_markers_end_it(self):
        self.acquire()
        self.write(RUN_FILE, "## Closeout run=abcdef123456\nPARKED 2099-01-01T00:00:00Z run=abcdef123456 old\n", "a")
        self.assertEqual(self.hook()["decision"], "block", "an old run's markers ended this run")
        self.write(RUN_FILE, f"PARKED 2099-01-02T00:00:00Z run={self.run_id()} blocked here\n", "a")
        self.assertIsNone(self.hook())

    def test_a_closeout_with_this_runs_id_allows(self):
        self.acquire()
        self.write(RUN_FILE, f"\n## Closeout run={self.run_id()}\n\nShipped.\n", "a")
        self.assertIsNone(self.hook())

    def test_the_breaker_trips_after_three_blocks_without_progress(self):
        self.acquire()
        for push in (1, 2, 3):
            self.assertEqual(self.hook()["decision"], "block", push)
        self.assertIsNone(self.hook(), "the fourth stop without progress must be allowed")
        self.assertEqual((self.state()["trips"], self.state()["stalled"]), (1, True))

    def test_bookkeeping_is_not_progress_and_real_work_is(self):
        self.acquire()
        for _ in range(3):
            self.hook()
        self.write(RUN_FILE, "- bookkeeping: heartbeat resumed 2099-01-01T00:00:00Z\n", "a")
        self.assertIsNone(self.hook(), "a bookkeeping line reset the breaker")
        for change in (lambda: self.write("notes.txt", "new untracked file\n"),
                       lambda: self.write("notes.txt", "same file, new content\n"),
                       lambda: self.write(RUN_FILE, "- Section D00 T01 §3 shipped\n", "a")):
            for _ in range(3):
                self.hook()
            change()
            decision = self.hook()
            self.assertIsNotNone(decision, "real progress did not reset the breaker")
            self.assertEqual(self.state()["blocks"], 1)

    def test_a_failure_fails_open_and_is_recorded_for_the_heartbeat(self):
        self.acquire()
        os.unlink(os.path.join(self.root, RUN_FILE))
        os.makedirs(os.path.join(self.root, RUN_FILE))  # opening the run file now raises
        self.assertIsNone(self.hook())
        line = guard.hook_error(self.root, SESSION)
        self.assertTrue(line.startswith("campaign-stop hook failed at "), line)
        with self.assertRaises(guard.GuardError):
            guard.hook_error(self.root, OTHER)
        with self.assertRaises(guard.GuardError):
            guard.hook_error(self.root, SESSION, ack="not the line")
        self.assertIn("acknowledged and cleared", guard.hook_error(self.root, SESSION, ack=line))
        self.assertEqual(guard.hook_error(self.root, SESSION), "")

    def test_a_malformed_guard_fails_open_into_its_own_error_file(self):
        self.write("build/claude-campaign-guard.json", "{not json")
        self.assertIsNone(self.hook())
        line = guard.hook_error(self.root)
        self.assertIn("recorded without the lock", line)
        guard.hook_error(self.root, ack=line)
        self.assertEqual(os.listdir(os.path.join(self.root, "build", "claude-campaign-hook-errors")), [])

    def test_the_breaker_trips_where_build_is_not_ignored(self):
        # The guard's own state writes must never pass for progress, whatever the project ignores.
        self.write(".gitignore", "scripts/ready.txt\n")
        subprocess.run(["git", "commit", "-qam", "stop ignoring build"], cwd=self.root, capture_output=True, check=True)
        self.acquire()
        for push in (1, 2, 3):
            self.assertEqual(self.hook()["decision"], "block", push)
        self.assertIsNone(self.hook(), "the hook's own state file reset the breaker")

    def test_tracked_copies_of_the_guards_files_are_not_progress_either(self):
        self.write(".gitignore", "scripts/ready.txt\n")
        self.acquire()
        self.hook()
        subprocess.run(["git", "add", "-A"], cwd=self.root, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-qm", "track build"], cwd=self.root, capture_output=True, check=True)
        for push in (1, 2, 3):
            self.assertEqual(self.hook()["decision"], "block", push)
        self.assertIsNone(self.hook(), "a tracked state file reset the breaker")

    def test_a_phase_run_reads_and_pushes_only_its_phase(self):
        self.acquire(scope="phase")
        self.ready(1, "mixed")
        decision = self.hook()
        self.assertIn("of Phase 0 only", decision["reason"])
        self.assertNotIn("then the next phase", decision["reason"])
        self.assertIn("Next ready row: D00 T01 §3", decision["reason"])
        self.ready(0, "mixed")
        self.assertIsNone(self.hook(), "another phase's ready row held a phase-only run open")
        self.acquire(scope="plan")
        decision = self.hook()
        self.assertIn("Next ready row: D05 T01 §1", decision["reason"])
        self.assertIn("then the next phase", decision["reason"])

    def test_a_phase_run_on_a_text_graph_ends_only_on_its_marker(self):
        # A text summary names no phase: its count and rows belong to the whole plan, so a phase run ignores both.
        self.acquire(scope="phase")
        self.ready(1, "text")
        decision = self.hook()
        self.assertEqual(decision["decision"], "block")
        self.assertNotIn("Next ready row", decision["reason"], "a phase run was pointed at a row of unknown phase")
        self.ready(0, "text")
        self.assertEqual(self.hook()["decision"], "block", "another phase's empty count ended a phase run")
        self.write(RUN_FILE, f"## Closeout run={self.run_id()}\n", "a")
        self.assertIsNone(self.hook())

    def test_an_unacknowledged_hook_error_survives_a_later_stop(self):
        self.acquire()
        guard._record_hook_error(self.root, guard.read_guard(self.root), "OSError: transient")
        self.assertEqual(self.hook()["decision"], "block")
        line = guard.hook_error(self.root, SESSION)
        self.assertIn("OSError: transient", line)
        guard.hook_error(self.root, SESSION, ack=line)
        self.assertEqual(self.hook()["decision"], "block")
        self.assertEqual(guard.hook_error(self.root, SESSION), "")

    def test_the_hook_decides_inside_its_own_time_budget(self):
        self.acquire()
        self.ready(30, "sleep")
        os.environ["CAMPAIGN_HOOK_BUDGET_SECONDS"] = "4"
        try:
            started = __import__("time").monotonic()
            decision = self.hook()
            elapsed = __import__("time").monotonic() - started
        finally:
            del os.environ["CAMPAIGN_HOOK_BUDGET_SECONDS"]
        self.assertLess(elapsed, 12, "the hook waited on the graph past its budget")
        self.assertEqual(decision["decision"], "block", "an unreadable graph still blocks an open run")

    def test_the_configured_command_runs_the_hook_from_any_shell(self):
        settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
        command = settings["hooks"]["Stop"][0]["hooks"][0]["command"]
        self.acquire()
        # Claude Code runs hooks through Git Bash on Windows; `bash` on PATH there is often WSL's, which would not
        # carry CLAUDE_PROJECT_DIR into Linux.
        bash = "bash"
        if os.name == "nt" and shutil.which("git"):
            bash = str(Path(shutil.which("git")).resolve().parents[1] / "bin" / "bash.exe")
        shells = [[bash, "-c"]] + ([["powershell.exe", "-NoProfile", "-Command"]] if os.name == "nt" else [])
        ran = 0
        for shell in shells:
            if not shutil.which(shell[0]):
                continue
            with self.subTest(shell=shell[0]):
                env = dict(os.environ, CLAUDE_PROJECT_DIR=self.root)
                payload = json.dumps({"session_id": SESSION, "cwd": self.root, "hook_event_name": "Stop"})
                proc = subprocess.run([*shell, command], input=payload, capture_output=True, text=True,
                                      encoding="utf-8", env=env, cwd=self._tmp.name, timeout=120)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(json.loads(proc.stdout)["decision"], "block", proc.stderr)
                ran += 1
        self.assertGreater(ran, 0, "no shell could run the configured hook")


class Lifecycle(Workspace):
    def test_acquire_is_exclusive_and_a_handover_is_recorded(self):
        self.assertIn("guard created", self.acquire())
        rid = self.run_id()
        with self.assertRaises(guard.GuardError):
            self.acquire(session=OTHER, cron_id="job-2")
        self.assertIn("handed over", self.acquire(session=OTHER, cron_id="job-2", handover="session died"))
        doc = guard.read_guard(self.root)
        self.assertEqual((doc["handover_from"], doc["run_id"], doc["cron_id"]), (SESSION, rid, "job-2"))
        self.assertIn("re-pointed", self.acquire(session=OTHER, cron_id="job-3"))
        self.assertEqual(self.run_id(), rid, "a re-point of the same run keeps its id")

    def test_a_torn_guard_needs_a_handover_and_the_scope_is_kept(self):
        self.write("build/claude-campaign-guard.json", "")
        with self.assertRaises(guard.GuardError):
            self.acquire()
        self.assertIn("handed over", self.acquire(handover="torn guard after a crash", scope="phase"))
        self.assertEqual(guard.read_guard(self.root)["handover_from"], "<unreadable guard>")
        self.acquire(cron_id="job-2")
        self.assertEqual(guard.read_guard(self.root)["scope"], "phase", "a re-point dropped the scope")
        self.assertTrue(guard.whoami(self.root, SESSION).endswith("scope=phase"))
        with self.assertRaises(guard.GuardError):
            self.acquire(scope="everything")
        self.acquire(session=OTHER, cron_id="job-3", handover="resumed in a new session")
        self.assertEqual(guard.read_guard(self.root)["scope"], "phase", "a handover widened a phase run to the plan")

    def test_a_guard_write_that_fails_part_way_leaves_nothing_behind(self):
        real_dump = guard.json.dump

        def torn(doc, fh, **kw):
            fh.write('{"runner": "cla')
            raise OSError(28, "No space left on device")

        guard.json.dump = torn
        try:
            with self.assertRaises(OSError):
                self.acquire()
        finally:
            guard.json.dump = real_dump
        self.assertEqual(sorted(os.listdir(os.path.join(self.root, "build"))), ["claude-campaign-guard.lock"])
        self.assertIn("guard created", self.acquire())

    def test_a_failed_update_keeps_the_existing_guard_byte_for_byte(self):
        self.acquire()
        path = os.path.join(self.root, "build", "claude-campaign-guard.json")
        with open(path, "rb") as fh:
            before = fh.read()
        real_dump, real_replace, replaced = guard.json.dump, guard.os.replace, []

        def torn(doc, fh, **kw):
            fh.write('{"runner": "cla')
            raise OSError(28, "No space left on device")

        def spy(src, dst):
            replaced.append((src, dst))
            return real_replace(src, dst)

        guard.json.dump = torn
        try:
            with self.assertRaises(OSError):
                self.acquire(cron_id="job-2")
        finally:
            guard.json.dump = real_dump
        with open(path, "rb") as fh:
            self.assertEqual(fh.read(), before, "a failed re-point damaged the live guard")
        self.assertEqual(sorted(os.listdir(os.path.join(self.root, "build"))),
                         ["claude-campaign-guard.json", "claude-campaign-guard.lock"])
        guard.os.replace = spy
        try:
            self.acquire(cron_id="job-2")
        finally:
            guard.os.replace = real_replace
        (src, dst), = replaced
        self.assertEqual((os.path.dirname(src), dst), (os.path.dirname(path), path),
                         "the guard is not published by a rename from beside it")

    def test_the_lock_is_exclusive_and_a_dead_holder_releases_it(self):
        with guard._Lock(self.root):
            with self.assertRaises(guard.GuardError):
                guard._Lock(self.root, wait=0.2).__enter__()
        holder = subprocess.Popen([sys.executable, "-c", (
            "import importlib.util, sys, time\n"
            f"s = importlib.util.spec_from_file_location('g', {str(GUARD_PY)!r})\n"
            "g = importlib.util.module_from_spec(s); s.loader.exec_module(g)\n"
            f"l = g._Lock({self.root!r}); l.__enter__(); print('held', flush=True); time.sleep(60)\n")],
            stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(holder.stdout.readline().strip(), "held")
            with self.assertRaises(guard.GuardError):
                guard._Lock(self.root, wait=0.2).__enter__()
        finally:
            holder.kill()
            holder.wait(timeout=30)
            holder.stdout.close()
        self.assertIn("guard created", self.acquire(), "a dead holder's lock was not released")

    def test_acquire_refuses_a_run_file_outside_the_workspace(self):
        for bad in ("../outside.md", os.path.abspath("x.md")):
            with self.subTest(bad=bad), self.assertRaises(guard.GuardError):
                guard.acquire(self.root, SESSION, 0, bad, "job-1")

    def test_every_end_checks_its_marker_and_leaves_the_job_to_cancel(self):
        self.acquire()
        with self.assertRaises(guard.GuardError):
            guard.end(self.root, SESSION, "closeout")
        with self.assertRaises(guard.GuardError):
            guard.end(self.root, OTHER, "operator-stop")
        with self.assertRaises(guard.GuardError):
            guard.end(self.root, SESSION, "plan-done")
        with self.assertRaises(guard.GuardError):
            guard.end(self.root, SESSION, "stall")
        self.write(RUN_FILE, f"## Closeout run={self.run_id()}\n", "a")
        self.assertIn("CronDelete job-1", guard.end(self.root, SESSION, "closeout"))
        self.assertIsNone(guard.read_guard(self.root))
        self.assertIn("CronDelete job-1", guard.pending_cancel(self.root))
        with self.assertRaises(guard.GuardError):
            guard.cancel_confirmed(self.root, "job-9")
        self.assertIn("nothing pending", guard.cancel_confirmed(self.root, "job-1"))
        self.acquire(cron_id="job-4")
        self.ready(0)
        self.write("scripts/open.txt", "1")  # nothing ready, but a blocked row is still open: a park, not done
        with self.assertRaises(guard.GuardError) as ctx:
            guard.end(self.root, SESSION, "plan-done")
        self.assertIn("still open", str(ctx.exception))
        self.write("scripts/open.txt", "0")
        self.assertIn("plan-done", guard.end(self.root, SESSION, "plan-done"))

    def test_whoami_names_what_a_heartbeat_is_to_the_run(self):
        self.assertEqual(guard.whoami(self.root, SESSION), "NO GUARD")
        self.acquire(generation="gen000000001")
        self.assertEqual(guard.whoami(self.root, SESSION, "gen000000001"), f"OWNER run={self.run_id()} scope=plan")
        self.assertEqual(guard.whoami(self.root, SESSION, "gen000000000"), "NOT THE CURRENT JOB")
        self.assertEqual(guard.whoami(self.root, OTHER), "NOT THE OWNER")
        self.write("build/claude-campaign-guard.json", "{not json")
        self.assertEqual(guard.whoami(self.root, SESSION), "MALFORMED GUARD")

    def test_reconcile_health_and_expiry(self):
        self.assertEqual(guard.reconcile(self.root, SESSION, ["job-7"]),
                         ["reconcile: orphan job job-7 has no guard: CronDelete it"])
        self.acquire()
        self.assertEqual(guard.reconcile(self.root, SESSION, ["job-1"]), ["reconcile: consistent (guard and job job-1)"])
        self.assertIn("start nothing", guard.reconcile(self.root, OTHER, ["job-1"])[0])
        self.assertEqual(guard.health(self.root, SESSION, ["job-1"])[0], 0)
        self.assertEqual(guard.health(self.root, SESSION, [])[0], 1)
        created = guard.read_guard(self.root)["job_created_at"]
        self.assertEqual(guard.expiry(self.root, SESSION, now=created)[0], 0)
        import datetime
        later = (datetime.datetime.strptime(created, guard.UTC_FORMAT) + datetime.timedelta(days=6, hours=13))
        code, line = guard.expiry(self.root, SESSION, now=later.strftime(guard.UTC_FORMAT))
        self.assertEqual(code, 1)
        self.assertIn("replace due", line)

    def test_reset_state_rechecks_ownership_under_the_lock(self):
        self.acquire()
        self.hook()
        with self.assertRaises(guard.GuardError):
            guard.reset_state(self.root, OTHER)
        with self.assertRaises(guard.GuardError):
            guard.reset_state(self.root, expect_no_guard=True)
        self.assertEqual(guard.reset_state(self.root, SESSION), "reset-state: state deleted")

    def test_the_command_line_runs_against_a_fixture_root(self):
        def cli(*args):
            return subprocess.run([sys.executable, "-B", str(GUARD_PY), *args, "--root", self.root],
                                  capture_output=True, text=True, timeout=120)

        self.assertEqual(len(subprocess.run([sys.executable, "-B", str(GUARD_PY), "mint-generation"],
                                            capture_output=True, text=True).stdout.strip()), 12)
        result = cli("acquire", "--session", SESSION, "--phase", "0", "--run-file", RUN_FILE, "--cron-id", "job-1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(cli("whoami", "--session", SESSION).stdout.startswith("OWNER run="))
        self.assertEqual(cli("end", "--session", SESSION, "--reason", "nonsense").returncode, 1)
        self.assertEqual(cli("frobnicate").returncode, 2)


class Robustness(Workspace):
    """D00 T03 §7: the three defects reported 2026-10-21."""

    def test_a_device_a_fifo_or_a_symlink_never_blocks_or_breaks_the_fingerprint(self):
        import stat
        from unittest import mock
        self.write("notes.txt", "plain\n")
        self.write("dev0", "")  # reported below as a character device
        os.makedirs(os.path.join(self.root, "somedir"))
        links = False
        try:
            os.symlink(os.path.join(self.root, "somedir"), os.path.join(self.root, "dirlink"),
                       target_is_directory=True)
            links = True
        except (OSError, NotImplementedError):
            pass  # Windows without the symlink privilege: the device and FIFO cases still run
        if hasattr(os, "mkfifo"):
            os.mkfifo(os.path.join(self.root, "pipe"))  # opening it for reading would block forever
        real_lstat, opened = os.lstat, []
        real_open = os.open

        def lstat(path, *a, **kw):
            result = real_lstat(path, *a, **kw)
            if os.path.basename(path) == "dev0":
                fields = list(result)
                fields[0] = stat.S_IFCHR | 0o600
                return os.stat_result(fields)
            return result

        def tracking_open(path, *a, **kw):
            opened.append(os.path.basename(path))
            return real_open(path, *a, **kw)

        with mock.patch.object(guard.os, "lstat", lstat), mock.patch.object(guard.os, "open", tracking_open):
            first = guard.fingerprint(self.root, RUN_FILE, "")
        self.assertIn("notes.txt", opened)
        for special in ("dev0", "pipe", "dirlink"):
            self.assertNotIn(special, opened, f"{special} was opened")
        if links:  # the link is recorded by its target text, so retargeting it changes the fingerprint
            os.unlink(os.path.join(self.root, "dirlink"))
            os.symlink(os.path.join(self.root, "build"), os.path.join(self.root, "dirlink"), target_is_directory=True)
            with mock.patch.object(guard.os, "lstat", lstat):
                self.assertNotEqual(guard.fingerprint(self.root, RUN_FILE, ""), first)

    def test_a_path_past_both_bounds_makes_no_filesystem_call(self):
        from unittest import mock
        for name in ("a.txt", "b.txt", "c.txt"):
            self.write(name, name)
        seen = []
        real_lstat = os.lstat

        def lstat(path, *a, **kw):
            seen.append(os.path.basename(path))
            return real_lstat(path, *a, **kw)

        with mock.patch.dict(os.environ, {"CAMPAIGN_HASH_FILES": "1", "CAMPAIGN_STAT_FILES": "1"}), \
                mock.patch.object(guard.os, "lstat", lstat):
            guard.fingerprint(self.root, RUN_FILE, "")
        untracked = [p for p in seen if p.endswith(".txt")]
        self.assertEqual(len(untracked), 2, f"the third untracked path was touched: {seen}")

    def test_a_repoint_without_a_phase_keeps_the_phase_and_a_fresh_run_needs_one(self):
        with self.assertRaises(guard.GuardError) as ctx:
            guard.acquire(self.root, SESSION, None, RUN_FILE, "job-1")
        self.assertIn("--phase", str(ctx.exception))
        guard.acquire(self.root, SESSION, 2, RUN_FILE, "job-1")
        out = guard.acquire(self.root, SESSION, None, RUN_FILE, "job-2")  # the heartbeat repair at a boundary
        self.assertEqual(guard.read_guard(self.root)["phase"], 2)
        self.assertEqual(guard.read_guard(self.root)["cron_id"], "job-2")
        self.assertIn("phase 2", out)
        cli = subprocess.run([sys.executable, os.path.join(self.root, "scripts", "campaign_guard.py"), "acquire",
                              "--root", self.root, "--session", SESSION, "--run-file", RUN_FILE, "--cron-id", "job-3"],
                             capture_output=True, text=True)
        self.assertEqual(cli.returncode, 0, cli.stderr)
        self.assertEqual(guard.read_guard(self.root)["phase"], 2)

    def test_an_end_interrupted_after_it_began_never_resumes_the_run(self):
        from unittest import mock
        self.acquire()
        self.write(RUN_FILE, f"PARKED 2026-10-21T00:00:00Z run={self.run_id()} done here\n", mode="a")
        real_unlink = os.unlink

        def crash_on_guard(path, *a, **kw):
            if path.endswith("claude-campaign-guard.json"):
                raise KeyboardInterrupt("session died mid-end")
            return real_unlink(path, *a, **kw)

        with mock.patch.object(guard.os, "unlink", crash_on_guard), self.assertRaises(KeyboardInterrupt):
            guard.end(self.root, SESSION, "park")
        self.assertTrue(os.path.exists(os.path.join(self.root, "build", "claude-campaign-guard.json")))
        self.assertEqual(guard.whoami(self.root, SESSION), "NO GUARD")  # the heartbeat stands down
        self.assertIsNone(self.hook())  # the Stop hook lets the turn end
        self.assertFalse(os.path.exists(os.path.join(self.root, "build", "claude-campaign-guard.json")))
        self.assertIn("created", guard.acquire(self.root, SESSION, 0, RUN_FILE, "job-9"))  # a later run starts fresh


if __name__ == "__main__":
    unittest.main()
