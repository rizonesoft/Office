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

    def test_an_operator_stop_meets_the_goal(self):
        # 2026-11-11: the goal named only a park as an end by its own rules, so after the operator asked for a stop
        # and the guard had ended, the goal's own stop check still read "not met" and kept the session working.
        goal = re.search(r"(?m)^\$goal = '(.*)'$", self.text).group(1).replace("''", "'")
        met = goal[goal.index("The goal also counts as met"):]
        self.assertIn("campaign_guard.py end --reason operator-stop", met)
        self.assertIn("build/campaign-stop-request", met)
        self.assertIn("in words in this session", met)
        self.assertRegex(met, r"An operator stop is always honoured: the goal is then met")

    def test_the_real_start_passes_the_goal(self):
        # The goal's wording only matters if the session receives it: the one line that starts Claude ends with it.
        starts = [line.strip() for line in self.text.splitlines() if line.strip().startswith("claude --")]
        self.assertEqual(starts, ["claude --model $model --dangerously-skip-permissions $goal"])
        self.assertEqual(len(re.findall(r"(?m)^\$goal = ", self.text)), 1)  # one goal, never reassigned

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

    def test_only_the_start_shortcut_is_installed_in_a_normal_window(self):
        # Owner, 2026-11-11: the Stop shortcut is gone (stopping is asked of the session), and the start
        # shortcut opens a normal window, not a maximised one (WindowStyle 1, never 3).
        text = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn("'Rizonesoft Office campaign.lnk'", text)
        self.assertNotIn("Stop.lnk", text)
        self.assertIn("$shortcut.WindowStyle = 1", text)
        self.assertNotIn("WindowStyle = 3", text)


FAKE_CLAUDE = r"""
# A stand-in for Claude Code: it records each start, leaves a run guard so the launcher sees a run still open,
# and exits at once, which is how a session that died looks to the launcher.
$root = $env:OFFICE_FAKE_ROOT
New-Item -ItemType Directory -Force -Path (Join-Path $root 'build') | Out-Null
Add-Content -LiteralPath (Join-Path $root 'claude-calls.txt') -Value ($args -join ' ').Substring(0, 40)
Set-Content -LiteralPath (Join-Path $root 'build/claude-campaign-guard.json') -Value '{"session_id":"s","run_file":"r"}'
if ($env:CLAUDE_CODE_OAUTH_TOKEN) { Set-Content -LiteralPath (Join-Path $root 'token-seen.txt') -Value 'yes' }
# What the session's own children would get for clangd: the program that runs, by its output, or none.
$found = Get-Command clangd.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
$ran = if ($found) { (& $found.Source | Out-String).Trim() } else { 'none' }
Set-Content -LiteralPath (Join-Path $root 'clangd-ran.txt') -Value $ran
Set-Content -LiteralPath (Join-Path $root 'session-path.txt') -Value $env:PATH
exit 0
"""

# Stand-ins for the bootstrap and the host check, which log each call in order. The bootstrap's --bin-dirs prints
# the folders OFFICE_FAKE_BIN_DIRS names and the problems OFFICE_FAKE_BIN_ERR names, and exits OFFICE_FAKE_BIN_EXIT.
FAKE_BOOTSTRAP = """import os, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
with open(root / "order.txt", "a", encoding="utf-8") as log:
    log.write("bootstrap " + " ".join(sys.argv[1:]) + "\\n")
if sys.argv[1:] == ["--bin-dirs"]:
    for folder in filter(None, os.environ.get("OFFICE_FAKE_BIN_DIRS", "").split(";")):
        print(folder)
    for problem in filter(None, os.environ.get("OFFICE_FAKE_BIN_ERR", "").split(";")):
        print(problem, file=sys.stderr)
    sys.exit(int(os.environ.get("OFFICE_FAKE_BIN_EXIT", "0")))
sys.exit(int(os.environ.get("OFFICE_FAKE_BOOT_EXIT", "0")))
"""
FAKE_HOST_CHECK = """import sys
from pathlib import Path
with open(Path(__file__).resolve().parents[1] / "order.txt", "a", encoding="utf-8") as log:
    log.write("host check\\n")
sys.exit(0)
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
        self.host_check.write_text(FAKE_HOST_CHECK, encoding="utf-8")
        (self.root / "scripts" / "bootstrap-tools.py").write_text(FAKE_BOOTSTRAP, encoding="utf-8")
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

    def dry_run(self):
        done = subprocess.run([PWSH, "-NoLogo", "-NoProfile", "-File", str(self.root / "scripts" / "start-campaign.ps1"),
                               "-DryRun"], capture_output=True, text=True, timeout=120, env=self.env,
                              stdin=subprocess.DEVNULL)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return done.stdout

    def verdict(self, text):
        (self.root / ".conclave").mkdir(exist_ok=True)
        (self.root / ".conclave" / "operating-mode.json").write_text(text, encoding="utf-8")

    def test_each_arm_of_the_stored_verdict_reaches_the_command_line(self):
        # D00 T03 §37: the measurement's verdict names the lead model; the launcher starts whatever it says.
        for model in ("opus", "fable"):
            with self.subTest(model):
                self.verdict(json.dumps({"arm": f"{model}-alone", "model": model}))
                out = self.dry_run()
                self.assertIn(f"Lead model: {model}, from .conclave/operating-mode.json", out)
                self.assertIn(f"claude --model {model} --dangerously-skip-permissions", out)

    def test_a_missing_or_unreadable_verdict_falls_back_to_opus(self):
        cases = {"missing": None, "not json": "{", "no model": "{}", "not an alias": '{"model": "opus; rm -rf x"}',
                 "not text": '{"model": 5}'}
        for name, text in cases.items():
            with self.subTest(name):
                path = self.root / ".conclave" / "operating-mode.json"
                if text is None:
                    path.unlink(missing_ok=True)
                else:
                    self.verdict(text)
                out = self.dry_run()
                self.assertIn("Lead model: opus, from the fallback", out)
                self.assertIn("claude --model opus --dangerously-skip-permissions", out)

    def test_a_real_start_passes_the_stored_model(self):
        self.verdict(json.dumps({"arm": "fable-alone", "model": "fable"}))
        self.launch()
        self.wait_for(self.root / "claude-calls.txt")
        self.request_stop()
        self.assertTrue(self.calls()[0].startswith("--model fable "), self.calls())

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


    # D00 T04 §4: the pinned tools, run for real. Two different programs stand in for two clangd builds, told
    # apart by what they print: the pinned one is a copy of whoami, the machine's is a copy of hostname.

    def clangd_fixtures(self):
        system = Path(os.environ.get("SystemRoot") or r"C:\Windows") / "System32"
        pinned = self.root / ".tools" / "llvm-1" / "bin"
        machine = Path(self.tmp.name) / "machine-llvm"
        other = self.root / ".tools" / "cmake-1" / "bin"
        for folder in (pinned, machine, other):
            folder.mkdir(parents=True)
        shutil.copyfile(system / "whoami.exe", pinned / "clangd.exe")
        shutil.copyfile(system / "hostname.exe", machine / "clangd.exe")
        said = {name: subprocess.run([str(system / f"{name}.exe")], capture_output=True, text=True).stdout.strip()
                for name in ("whoami", "hostname")}
        self.env["PATH"] = str(self.bin) + os.pathsep + str(machine) + os.pathsep + self.env["PATH"]
        return pinned, machine, other, said

    def run_session(self, **env):
        self.env.update(env)
        launcher = self.launch("-RestartSeconds", "30")
        self.wait_for(self.root / "clangd-ran.txt")
        self.request_stop()
        output, _ = launcher.communicate(timeout=120)
        return output, (self.root / "clangd-ran.txt").read_text(encoding="utf-8").strip()

    def order(self):
        return (self.root / "order.txt").read_text(encoding="utf-8").splitlines()

    def test_the_bootstrap_runs_before_the_host_check(self):
        pinned, _, _, _ = self.clangd_fixtures()
        self.run_session(OFFICE_FAKE_BIN_DIRS=str(pinned))
        self.assertEqual(self.order()[:3], ["bootstrap ", "bootstrap --bin-dirs", "host check"])

    def test_a_failed_bootstrap_still_starts_the_session(self):
        pinned, _, _, _ = self.clangd_fixtures()
        output, _ = self.run_session(OFFICE_FAKE_BOOT_EXIT="1", OFFICE_FAKE_BIN_DIRS=str(pinned))
        self.assertIn("Build tools: the bootstrap failed (exit 1); the start goes on", output)
        self.assertTrue(self.calls(), "no session was started")

    def test_the_session_runs_the_pinned_clangd_not_the_machine_one(self):
        pinned, machine, _, said = self.clangd_fixtures()
        self.assertNotEqual(said["whoami"], said["hostname"])
        output, ran = self.run_session(OFFICE_FAKE_BIN_DIRS=str(pinned))
        self.assertEqual(ran, said["whoami"])
        self.assertIn(f"clangd: {pinned / 'clangd.exe'}", output)

    def test_after_a_partial_bootstrap_the_usable_folders_lead_and_the_problems_are_shown(self):
        pinned, _, other, said = self.clangd_fixtures()
        output, ran = self.run_session(OFFICE_FAKE_BIN_DIRS=f"{pinned};{other}", OFFICE_FAKE_BIN_EXIT="1",
                                       OFFICE_FAKE_BIN_ERR="ninja 1.0 is not installed as tools.lock.json pins it")
        self.assertEqual(ran, said["whoami"])
        session_path = (self.root / "session-path.txt").read_text(encoding="utf-8").strip().split(";")
        self.assertEqual(session_path[:2], [str(pinned), str(other)])
        self.assertIn("Build tools: ninja 1.0 is not installed", output)
        self.assertNotIn("ninja 1.0 is not installed", ";".join(session_path))

    def test_without_a_pinned_clangd_the_machine_one_is_left_off_and_the_start_goes_on(self):
        _, machine, other, _ = self.clangd_fixtures()
        output, ran = self.run_session(OFFICE_FAKE_BIN_DIRS=str(other), OFFICE_FAKE_BIN_EXIT="1",
                                       OFFICE_FAKE_BIN_ERR="llvm 1 is not installed as tools.lock.json pins it")
        self.assertEqual(ran, "none")
        self.assertIn("clangd: none (the pinned clangd is not installed: run python scripts/bootstrap-tools.py)", output)
        holding = [e for e in self.env["PATH"].split(os.pathsep) if e and (Path(e) / "clangd.exe").is_file()]
        self.assertIn(str(machine), holding)
        self.assertIn(f"{len(holding)} folder(s) holding another clangd were left off", output)
        session_path = (self.root / "session-path.txt").read_text(encoding="utf-8")
        self.assertNotIn(str(machine), session_path)
        self.assertIn(str(other), session_path)
        self.assertTrue(self.calls())

    def test_a_dry_run_names_the_pinned_clangd_and_installs_nothing(self):
        pinned, _, _, _ = self.clangd_fixtures()
        self.env["OFFICE_FAKE_BIN_DIRS"] = str(pinned)
        out = self.dry_run()
        self.assertIn(f"clangd: {pinned / 'clangd.exe'}", out)
        self.assertIn("Build tools: a real start runs python scripts/bootstrap-tools.py first.", out)
        self.assertEqual(self.order(), ["bootstrap --bin-dirs", "host check"])


if __name__ == "__main__":
    unittest.main()
