# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The campaign launcher starts Claude Code on the latest Opus, by alias (owner, 2026-11-10)."""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[1] / "start-campaign.ps1"


class StartCampaignModelTest(unittest.TestCase):
    def setUp(self):
        self.text = LAUNCHER.read_text(encoding="utf-8")

    def test_model_is_the_opus_alias(self):
        self.assertRegex(self.text, r"(?m)^\$model = 'opus'$")

    def test_goal_fits_the_goal_limit(self):
        goal = re.search(r"(?m)^\$goal = '(.*)'$", self.text).group(1).replace("''", "'")
        self.assertLessEqual(len(goal), 4000)

    def test_every_claude_start_passes_the_model(self):
        starts = [line.strip() for line in self.text.splitlines()
                  if "claude --" in line and "--dangerously-skip-permissions" in line]
        self.assertEqual(len(starts), 2, starts)  # the dry-run print and the real start
        for line in starts:
            self.assertIn("claude --model $model --dangerously-skip-permissions", line)

    def test_no_pinned_model_version_in_code(self):
        code = [line for line in self.text.splitlines() if not line.lstrip().startswith("#")]
        self.assertFalse([line for line in code if re.search(r"claude-(opus|sonnet|haiku|fable)-\d", line)])


PWSH = shutil.which("pwsh")


@unittest.skipUnless(sys.platform == "win32", "the launcher and its Stop control are Windows only")
class StopControlTest(unittest.TestCase):
    """The owner's Stop shortcut (owner, 2026-11-10): `-Stop` writes the request, `-Stop -Now` also ends the launcher."""

    def setUp(self):
        self.assertIsNotNone(PWSH, "pwsh is not on PATH; the launcher cannot run")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "scripts").mkdir()
        shutil.copyfile(LAUNCHER, self.root / "scripts" / "start-campaign.ps1")
        self.started = []
        self.addCleanup(self.stop_started)

    def stop_started(self):
        for process in self.started:
            if process.poll() is None:
                subprocess.run(["taskkill", "/T", "/F", "/PID", str(process.pid)], capture_output=True)
            process.wait(timeout=30)

    def stop(self, *extra):
        return subprocess.run([PWSH, "-NoLogo", "-NoProfile", "-File", str(self.root / "scripts" / "start-campaign.ps1"),
                               "-Stop", *extra], capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)

    def sleeper(self):
        process = subprocess.Popen([PWSH, "-NoLogo", "-NoProfile", "-Command", "Start-Sleep -Seconds 300"],
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.started.append(process)
        started = subprocess.run(
            [PWSH, "-NoLogo", "-NoProfile", "-Command",
             f"(Get-Process -Id {process.pid}).StartTime.ToUniversalTime().ToString('o')"],
            capture_output=True, text=True, timeout=60).stdout.strip()
        self.assertTrue(started, "the sleeper's start time could not be read")
        return process, started

    def record(self, pid, started):
        (self.root / "build").mkdir(exist_ok=True)
        (self.root / "build" / "campaign-launcher.json").write_text(json.dumps({"pid": pid, "started": started}),
                                                                   encoding="utf-8")

    def test_stop_now_writes_the_request_when_nothing_is_running(self):
        result = self.stop("-Now")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "build" / "campaign-stop-request").is_file())
        self.assertIn("No running launcher was found", result.stdout)

    def test_stop_now_ends_the_recorded_launcher(self):
        process, started = self.sleeper()
        self.record(process.pid, started)
        result = self.stop("-Now")
        self.assertEqual(result.returncode, 0, result.stderr)
        process.wait(timeout=30)  # raises when the launcher was not ended
        self.assertIn("Stopped now", result.stdout)

    def test_stop_now_spares_a_process_that_only_reuses_the_number(self):
        process, _ = self.sleeper()
        self.record(process.pid, "2001-01-01T00:00:00.0000000Z")
        result = self.stop("-Now")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(process.poll(), "a process with another start time must not be ended")
        self.assertIn("No running launcher was found", result.stdout)

    def test_both_shortcuts_are_installed(self):
        text = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn("'Rizonesoft Office campaign.lnk'", text)
        self.assertIn("'Rizonesoft Office campaign - Stop.lnk'", text)


FAKE_CLAUDE = r"""
# A stand-in for Claude Code: it records each start, leaves a run guard so the launcher sees a run still open,
# and exits at once, which is how a session that died looks to the launcher.
$root = $env:OFFICE_FAKE_ROOT
New-Item -ItemType Directory -Force -Path (Join-Path $root 'build') | Out-Null
Add-Content -LiteralPath (Join-Path $root 'claude-calls.txt') -Value ($args -join ' ').Substring(0, 40)
Set-Content -LiteralPath (Join-Path $root 'build/claude-campaign-guard.json') -Value '{"session_id":"s","run_file":"r"}'
if ($env:CLAUDE_CODE_OAUTH_TOKEN) { Set-Content -LiteralPath (Join-Path $root 'token-seen.txt') -Value 'yes' }
exit 0
"""


@unittest.skipUnless(sys.platform == "win32", "the launcher is Windows only")
class LauncherRunTest(unittest.TestCase):
    """The launcher run for real in a scratch clone, with a stand-in for Claude Code and for the host check."""

    def setUp(self):
        self.assertIsNotNone(PWSH, "pwsh is not on PATH; the launcher cannot run")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "clone"
        (self.root / "scripts").mkdir(parents=True)
        shutil.copyfile(LAUNCHER, self.root / "scripts" / "start-campaign.ps1")
        self.host_check = self.root / "scripts" / "check-campaign-host.py"
        self.host_check.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
        # An importer that must never run: the launcher reads the env file and nothing else.
        (self.root / "scripts" / "import-secrets.py").write_text(
            "from pathlib import Path\nPath(__file__).resolve().parents[1].joinpath('importer-ran.txt').write_text('x')\n",
            encoding="utf-8")
        self.bin = Path(self.tmp.name) / "bin"
        self.bin.mkdir()
        (self.bin / "claude.ps1").write_text(FAKE_CLAUDE, encoding="utf-8")
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ["PATH"], OFFICE_FAKE_ROOT=str(self.root))
        self.env.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
        self.processes = []
        self.addCleanup(self.end_processes)

    def end_processes(self):
        for process in self.processes:
            if process.poll() is None:
                subprocess.run(["taskkill", "/T", "/F", "/PID", str(process.pid)], capture_output=True)
            process.communicate(timeout=30)

    def launch(self, *extra):
        process = subprocess.Popen(
            [PWSH, "-NoLogo", "-NoProfile", "-File", str(self.root / "scripts" / "start-campaign.ps1"), *extra],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=self.env)
        self.processes.append(process)
        return process

    def wait_for(self, path, seconds=60):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if path.exists():
                return
            time.sleep(0.1)
        self.fail(f"{path.name} did not appear within {seconds} seconds")

    def calls(self):
        path = self.root / "claude-calls.txt"
        return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    def request_stop(self):
        (self.root / "build").mkdir(exist_ok=True)
        (self.root / "build" / "campaign-stop-request").write_text("now", encoding="utf-8")

    def test_a_stop_during_the_restart_wait_starts_no_new_session(self):
        launcher = self.launch("-RestartSeconds", "4")
        self.wait_for(self.root / "claude-calls.txt")
        time.sleep(1)  # the launcher is now in its wait before the restart
        self.request_stop()
        output, _ = launcher.communicate(timeout=120)
        self.assertEqual(len(self.calls()), 1, output)
        self.assertIn("Stopped on your request", output)
        self.assertFalse((self.root / "build" / "campaign-launcher.json").exists())

    def test_without_a_stop_the_session_is_started_again(self):
        launcher = self.launch("-RestartSeconds", "1")
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline and len(self.calls()) < 2:
            time.sleep(0.2)
        self.request_stop()
        output, _ = launcher.communicate(timeout=120)
        self.assertGreaterEqual(len(self.calls()), 2, output)  # so the test above can fail

    def test_a_stop_now_during_startup_ends_the_launcher_before_any_session(self):
        self.host_check.write_text("import sys, time\ntime.sleep(20)\nsys.exit(0)\n", encoding="utf-8")
        launcher = self.launch()
        self.wait_for(self.root / "build" / "campaign-launcher.json")  # recorded before the slow host check
        stop = subprocess.run([PWSH, "-NoLogo", "-NoProfile", "-File", str(self.root / "scripts" / "start-campaign.ps1"),
                               "-Stop", "-Now"], capture_output=True, text=True, timeout=120, env=self.env,
                              stdin=subprocess.DEVNULL)
        self.assertIn("Stopped now", stop.stdout, stop.stderr)
        launcher.communicate(timeout=60)
        self.assertEqual(self.calls(), [])

    def test_a_stop_request_written_during_startup_is_not_erased(self):
        self.host_check.write_text("import sys, time\ntime.sleep(4)\nsys.exit(0)\n", encoding="utf-8")
        launcher = self.launch()
        self.wait_for(self.root / "build" / "campaign-launcher.json")
        self.request_stop()  # the earlier request was removed first; this one belongs to this start
        output, _ = launcher.communicate(timeout=120)
        self.assertEqual(self.calls(), [], output)
        self.assertIn("Stopped on your request", output)
        self.assertTrue((self.root / "build" / "campaign-stop-request").exists())

    def test_a_start_removes_a_request_left_from_before(self):
        self.request_stop()
        launcher = self.launch("-RestartSeconds", "30")
        self.wait_for(self.root / "claude-calls.txt")
        self.assertFalse((self.root / "build" / "campaign-stop-request").exists())
        self.request_stop()
        launcher.communicate(timeout=120)

    def test_a_missing_token_starts_with_the_interactive_sign_in_and_runs_no_importer(self):
        launcher = self.launch("-RestartSeconds", "30")
        self.wait_for(self.root / "claude-calls.txt")
        self.request_stop()
        output, _ = launcher.communicate(timeout=120)
        self.assertIn("python scripts/import-secrets.py", output)
        self.assertFalse((self.root / "importer-ran.txt").exists(), "the launcher must not run the importer")
        self.assertFalse((self.root / "token-seen.txt").exists())

    def test_an_inherited_token_never_reaches_the_session(self):
        self.env["CLAUDE_CODE_OAUTH_TOKEN"] = "sk-ant-oat01-" + "i" * 48  # left in the shell, not in the env file
        launcher = self.launch("-RestartSeconds", "30")
        self.wait_for(self.root / "claude-calls.txt")
        self.request_stop()
        output, _ = launcher.communicate(timeout=120)
        self.assertFalse((self.root / "token-seen.txt").exists(), output)

    def test_a_second_start_is_refused_and_stop_still_ends_the_first(self):
        first = self.launch("-RestartSeconds", "60")
        self.wait_for(self.root / "claude-calls.txt")
        record = (self.root / "build" / "campaign-launcher.json").read_text(encoding="utf-8")
        second = self.launch("-RestartSeconds", "60")
        output, _ = second.communicate(timeout=120)
        self.assertEqual(second.returncode, 3, output)
        self.assertIn("already running", output)
        self.assertEqual((self.root / "build" / "campaign-launcher.json").read_text(encoding="utf-8"), record)
        self.assertFalse((self.root / "build" / "campaign-stop-request").exists())  # the refused start cleared nothing
        self.assertEqual(len(self.calls()), 1)
        stop = subprocess.run([PWSH, "-NoLogo", "-NoProfile", "-File", str(self.root / "scripts" / "start-campaign.ps1"),
                               "-Stop", "-Now"], capture_output=True, text=True, timeout=120, env=self.env,
                              stdin=subprocess.DEVNULL)
        self.assertIn("Stopped now", stop.stdout, stop.stderr)
        first.communicate(timeout=60)

    def test_a_window_left_open_after_the_run_does_not_block_the_next_start(self):
        # The desktop shortcut runs the launcher with -NoExit, so its window, and its process, outlive the run.
        first = subprocess.Popen(
            [PWSH, "-NoLogo", "-NoProfile", "-NoExit", "-File", str(self.root / "scripts" / "start-campaign.ps1"),
             "-RestartSeconds", "60"],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=self.env)
        self.processes.append(first)
        self.wait_for(self.root / "claude-calls.txt")
        self.request_stop()
        record = self.root / "build" / "campaign-launcher.json"
        deadline = time.monotonic() + 120
        while record.exists() and time.monotonic() < deadline:
            time.sleep(0.2)
        self.assertFalse(record.exists(), "the first launcher did not finish")
        self.assertIsNone(first.poll(), "the window must still be open for this test to mean anything")
        second = self.launch("-RestartSeconds", "60")
        deadline = time.monotonic() + 90
        while len(self.calls()) < 2 and second.poll() is None and time.monotonic() < deadline:
            time.sleep(0.2)
        self.assertEqual(len(self.calls()), 2, "the second start was refused while only an idle window was left")
        self.request_stop()
        second.communicate(timeout=120)

    def test_a_start_that_fails_after_taking_the_lock_gives_it_back(self):
        # A run guard that cannot be read ends the start with an error, after the lock was taken and before the
        # session loop. The window stays open (-NoExit), as the shortcut's does.
        (self.root / "build").mkdir(exist_ok=True)
        (self.root / "build" / "claude-campaign-guard.json").write_text("this is not JSON", encoding="utf-8")
        # The host check runs after the lock and the record, so its marker proves the first start got that far.
        self.host_check.write_text(
            "import sys\nfrom pathlib import Path\n"
            "Path(__file__).resolve().parents[1].joinpath('host-check-ran.txt').write_text('x')\nsys.exit(0)\n",
            encoding="utf-8")
        first = subprocess.Popen(
            [PWSH, "-NoLogo", "-NoProfile", "-NoExit", "-File", str(self.root / "scripts" / "start-campaign.ps1")],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=self.env)
        self.processes.append(first)
        self.wait_for(self.root / "host-check-ran.txt", seconds=120)
        self.assertTrue((self.root / "build" / "campaign-launcher.lock").exists())
        record = self.root / "build" / "campaign-launcher.json"
        deadline = time.monotonic() + 60
        while record.exists() and time.monotonic() < deadline:
            time.sleep(0.2)
        self.assertFalse(record.exists(), "the failed start did not clean up its record")
        self.assertIsNone(first.poll(), "the first window must still be open for this test to mean anything")
        (self.root / "host-check-ran.txt").unlink()
        second = self.launch()
        output, _ = second.communicate(timeout=120)
        self.assertNotEqual(second.returncode, 3, output)
        self.assertNotIn("already running", output)
        self.assertTrue((self.root / "host-check-ran.txt").exists(), "the second start was not admitted")
        self.assertEqual(self.calls(), [])

    def test_two_starts_at_the_same_moment_admit_exactly_one(self):
        # Both are still in the host check when the other starts, so neither has launched a session yet.
        self.host_check.write_text("import sys, time\ntime.sleep(5)\nsys.exit(0)\n", encoding="utf-8")
        launchers = [self.launch("-RestartSeconds", "60") for _ in range(4)]
        self.wait_for(self.root / "claude-calls.txt", seconds=120)
        refused = []
        for launcher in launchers:
            try:
                output, _ = launcher.communicate(timeout=60)
                refused.append((launcher.returncode, output))
            except subprocess.TimeoutExpired:
                pass  # the one that was admitted is still running
        self.assertEqual([code for code, _ in refused], [3, 3, 3], refused)
        for _, output in refused:
            self.assertIn("already running", output)
        self.assertEqual(len(self.calls()), 1)
        admitted = [launcher for launcher in launchers if launcher.poll() is None]
        self.assertEqual(len(admitted), 1)
        record = json.loads((self.root / "build" / "campaign-launcher.json").read_text(encoding="utf-8"))
        self.assertEqual(record["pid"], admitted[0].pid)  # Stop reaches the one that is running
        self.request_stop()

    def test_a_stop_that_cannot_end_the_launcher_says_so_and_exits_1(self):
        first = self.launch("-RestartSeconds", "60")
        self.wait_for(self.root / "claude-calls.txt")
        refuses = self.bin / "refuses.cmd"
        refuses.write_text("@exit /b 5\n", encoding="utf-8")
        stop = subprocess.run([PWSH, "-NoLogo", "-NoProfile", "-File", str(self.root / "scripts" / "start-campaign.ps1"),
                               "-Stop", "-Now", "-TaskKillPath", str(refuses)], capture_output=True, text=True,
                              timeout=120, env=self.env, stdin=subprocess.DEVNULL)
        self.assertEqual(stop.returncode, 1, stop.stdout + stop.stderr)
        self.assertIn("NOT stopped", stop.stdout)
        self.assertNotIn("Stopped now", stop.stdout)
        self.assertIsNone(first.poll())
        self.assertTrue((self.root / "build" / "campaign-stop-request").exists())  # the graceful request stands

    def test_a_stored_token_reaches_the_session_and_is_not_printed(self):
        token = "sk-ant-oat01-" + "z" * 48
        (self.root / ".secrets").mkdir()
        (self.root / ".secrets" / "office.env").write_text(f"CLAUDE_CODE_OAUTH_TOKEN={token}\n", encoding="utf-8")
        launcher = self.launch("-RestartSeconds", "30")
        self.wait_for(self.root / "token-seen.txt")
        self.request_stop()
        output, _ = launcher.communicate(timeout=120)
        self.assertNotIn(token, output)
        self.assertIn(".secrets/office.env", output)

    def test_a_dry_run_runs_no_importer_and_leaves_a_stop_request(self):
        self.request_stop()
        done = subprocess.run([PWSH, "-NoLogo", "-NoProfile", "-File", str(self.root / "scripts" / "start-campaign.ps1"),
                               "-DryRun"], capture_output=True, text=True, timeout=120, env=self.env,
                              stdin=subprocess.DEVNULL)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertTrue((self.root / "build" / "campaign-stop-request").exists())
        self.assertFalse((self.root / "importer-ran.txt").exists())
        self.assertFalse((self.root / "build" / "campaign-launcher.json").exists())
        self.assertEqual(self.calls(), [])


if __name__ == "__main__":
    unittest.main()
