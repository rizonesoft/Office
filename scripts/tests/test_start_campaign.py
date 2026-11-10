# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The campaign launcher starts Claude Code on the latest Fable, by alias (owner, 2026-11-10)."""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[1] / "start-campaign.ps1"


class StartCampaignModelTest(unittest.TestCase):
    def setUp(self):
        self.text = LAUNCHER.read_text(encoding="utf-8")

    def test_model_is_the_fable_alias(self):
        self.assertRegex(self.text, r"(?m)^\$model = 'fable'$")

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

    def test_the_restart_loop_honours_the_request_and_a_start_clears_it(self):
        text = LAUNCHER.read_text(encoding="utf-8")
        loop = text[text.index("while ($true) {"):]
        self.assertLess(loop.index("Test-Path -LiteralPath $stopFile"), loop.index("Start-Sleep -Seconds 30"),
                        "the stop request must be checked before a new session is started")
        before_loop = text[:text.index("while ($true) {")]
        self.assertIn("Remove-Item -LiteralPath $stopFile", before_loop)
        self.assertIn("Remove-Item -LiteralPath $launcherFile", text[text.index("} finally {"):])

    def test_both_shortcuts_are_installed(self):
        text = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn("'Rizonesoft Office campaign.lnk'", text)
        self.assertIn("'Rizonesoft Office campaign - Stop.lnk'", text)


class SignInTest(unittest.TestCase):
    """The launcher takes its token from the repository's own env file, never from WSL or the vault directly."""

    def test_the_launcher_reads_the_env_file_and_starts_no_wsl(self):
        code = [line for line in LAUNCHER.read_text(encoding="utf-8").splitlines() if not line.lstrip().startswith("#")]
        self.assertTrue([line for line in code if ".secrets/office.env" in line])
        self.assertFalse([line for line in code if "wsl" in line.lower() or "conclave-op" in line])

    def test_the_token_is_never_written_to_the_host(self):
        code = [line for line in LAUNCHER.read_text(encoding="utf-8").splitlines() if not line.lstrip().startswith("#")]
        self.assertFalse([line for line in code if "Write-Host" in line and "$token" in line])


if __name__ == "__main__":
    unittest.main()
