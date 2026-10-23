# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The Office automations: tasks.json, run.py, alert.py, the installer and the README."""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from shutil import which as shutil_which

REPO = Path(__file__).resolve().parents[2]


def contextlib_redirect():
    """Silence a call's stdout and stderr."""
    import contextlib
    stack = contextlib.ExitStack()
    stack.enter_context(redirect_stdout(io.StringIO()))
    stack.enter_context(redirect_stderr(io.StringIO()))
    return stack
AUTO = REPO / ".conclave" / "automations"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run = load("office_run", AUTO / "run.py")
alert = load("office_alert", AUTO / "alert.py")
# One well-formed task, for tests that must not depend on what tasks.json lists today.
FIXTURE_TASK = {"name": "office-fixture", "description": "Fixture check", "command": ["python", "scripts/fixture.py"],
                "trigger": {"weekly": "Monday", "at": "07:00"}, "timeout_minutes": 5}




class Manifest(unittest.TestCase):
    def test_the_manifest_loads_and_every_command_script_exists(self):
        tasks = run.load_tasks(str(AUTO / "tasks.json"))
        for name, task in tasks.items():
            with self.subTest(name=name):
                self.assertEqual(task["command"][0], "python")
                self.assertTrue((REPO / task["command"][1]).is_file(), task["command"][1])

    @staticmethod
    def readme_rows(text):
        """Every table row whose first cell names an office- task, with or without backticks."""
        rows = {}
        for line in text.splitlines():
            cells = [c.strip().strip("`").strip() for c in line.strip().strip("|").split("|")]
            if line.lstrip().startswith("|") and cells and cells[0].startswith("office-"):
                rows[cells[0]] = cells
        return rows

    def test_the_readme_lists_exactly_the_manifest(self):
        tasks = run.load_tasks(str(AUTO / "tasks.json"))
        rows = self.readme_rows((AUTO / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(sorted(rows), sorted(tasks))
        for name, task in tasks.items():
            with self.subTest(name=name):
                script = task["command"][1] if len(task["command"]) > 1 else task["command"][0]
                self.assertIn(script, rows[name][2], "the Runs column must name the task's script")

    def test_the_readme_row_check_sees_unformatted_rows(self):
        rows = self.readme_rows("| office-ghost | Monday | scripts/ghost.py | nonzero |")
        self.assertIn("office-ghost", rows)

    def test_the_installer_reads_the_manifest_and_names_no_task(self):
        text = (AUTO / "install.ps1").read_text(encoding="utf-8")
        self.assertIn("tasks.json", text)
        self.assertNotIn("office-", text)

    def test_a_malformed_manifest_is_refused(self):
        good = json.loads((AUTO / "tasks.json").read_text(encoding="utf-8"))
        first = FIXTURE_TASK
        cases = {
            "bad name": {**first, "name": "rizonetech-x"},
            "extra key": {**first, "enabled": True},
            "empty command": {**first, "command": []},
            "zero timeout": {**first, "timeout_minutes": 0},
            "bad day": {**first, "trigger": {"weekly": "Funday", "at": "07:00"}},
            "bad time": {**first, "trigger": {"weekly": "Monday", "at": "7am"}},
            "bad daily time": {**first, "trigger": {"daily_at": "25:00"}},
            "daily with extra key": {**first, "trigger": {"daily_at": "06:23", "every_minutes": 5}},
            "unknown trigger": {**first, "trigger": {"daily": "07:00"}},
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.json"
            for label, task in cases.items():
                with self.subTest(label):
                    path.write_text(json.dumps({**good, "tasks": [task]}), encoding="utf-8")
                    with self.assertRaises(run.TaskError):
                        run.load_tasks(str(path))
            path.write_text(json.dumps({**good, "tasks": [first, first]}), encoding="utf-8")
            with self.assertRaises(run.TaskError):
                run.load_tasks(str(path))


class Runner(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".conclave" / "automations").mkdir(parents=True)
        self.tasks = {"schema_version": 1, "folder": "\\Office\\", "tasks": [
            self.task("office-pass", "print('all good')"),
            self.task("office-fail", "import sys; print('line one'); print('it broke'); sys.exit(3)"),
        ]}
        (self.root / ".conclave" / "automations" / "tasks.json").write_text(json.dumps(self.tasks), encoding="utf-8")
        self.alerts = []

    def tearDown(self):
        self._tmp.cleanup()

    @staticmethod
    def task(name, code):
        return {"name": name, "description": f"fixture {name}", "command": [sys.executable, "-c", code],
                "trigger": {"weekly": "Monday", "at": "07:00"}, "timeout_minutes": 1}

    def main(self, name, **kw):
        kw.setdefault("alerter", lambda *a: self.alerts.append(a))
        return run.main([name], root=str(self.root), **kw)

    def last(self, name):
        return json.loads((self.root / "build" / "automations" / name / "last.json").read_text(encoding="utf-8"))

    def test_a_passing_run_keeps_its_log_and_sends_nothing(self):
        self.assertEqual(self.main("office-pass"), 0)
        outcome = self.last("office-pass")
        self.assertEqual(outcome["exit"], 0)
        self.assertIn("all good", (self.root / outcome["log"]).read_text(encoding="utf-8"))
        self.assertEqual(self.alerts, [])

    def test_a_failing_run_alerts_with_its_log_tail(self):
        self.assertEqual(self.main("office-fail"), 3)
        (name, task, outcome, tail), = self.alerts
        self.assertEqual((name, outcome["exit"], task["description"]), ("office-fail", 3, "fixture office-fail"))
        self.assertIn("it broke", tail)

    def test_a_timeout_stops_the_run_and_alerts(self):
        killed = []

        class Hung:
            pid = 0

            def __init__(self, *a, **kw):
                pass

            def wait(self, timeout=None):
                raise subprocess.TimeoutExpired("hung", timeout)

        self.assertEqual(self.main("office-pass", popen=Hung, killer=killed.append), 124)
        self.assertEqual(len(killed), 1)
        self.assertTrue(self.last("office-pass")["timed_out"])
        self.assertEqual(len(self.alerts), 1)

    def test_an_unsent_alert_exits_3_and_says_so_in_the_log(self):
        def refuse(*_a):
            raise alert.Refused("vault field credential is unavailable")

        self.tasks["tasks"][1]["command"][-1] = "import sys; sys.exit(5)"
        (self.root / ".conclave" / "automations" / "tasks.json").write_text(json.dumps(self.tasks), encoding="utf-8")
        self.assertEqual(self.main("office-fail", alerter=refuse), 3)
        log = (self.root / self.last("office-fail")["log"]).read_text(encoding="utf-8")
        self.assertIn("alert not sent: Refused: vault field credential is unavailable", log)

    def test_only_the_newest_logs_are_kept(self):
        folder = self.root / "build" / "automations" / "office-pass"
        folder.mkdir(parents=True)
        for i in range(run.KEEP_LOGS + 5):
            (folder / f"20000101T0000{i:02d}Z.log").write_text("old", encoding="utf-8")
        self.main("office-pass")
        self.assertEqual(len(list(folder.glob("*.log"))), run.KEEP_LOGS)
        self.assertTrue((self.root / self.last("office-pass")["log"]).exists())

    def test_a_command_that_cannot_start_is_recorded_and_alerted(self):
        def cannot_start(*_a, **_kw):
            raise PermissionError(13, "Access is denied")

        self.assertEqual(self.main("office-pass", popen=cannot_start), 126)
        outcome = self.last("office-pass")
        self.assertEqual(outcome["exit"], 126)
        self.assertIn("could not start", (self.root / outcome["log"]).read_text(encoding="utf-8"))
        (_name, _task, alerted, tail), = self.alerts
        self.assertEqual(alerted["exit"], 126)
        self.assertIn("Access is denied", tail)

    def test_every_nested_launch_opens_no_console(self):
        scripts = REPO / "scripts"
        for path in (AUTO / "run.py", AUTO / "alert.py", scripts / "check-visual-studio.py",
                     scripts / "merge_prs.py", scripts / "lib" / "pin_proposal.py"):
            text = path.read_text(encoding="utf-8")
            calls = text.count("subprocess.run(") + text.count("subprocess.Popen(") + text.count("run([wsl()")
            flagged = text.count("creationflags=")
            with self.subTest(path=path.name):
                self.assertGreaterEqual(flagged, calls - text.count('"git", "init"'), path.name)

    def test_an_unknown_task_is_refused(self):
        self.assertEqual(self.main("office-missing"), 2)


class Alert(unittest.TestCase):
    TASK = {"description": "Fixture check", "command": ["python", "scripts/fixture.py"]}
    OUTCOME = {"exit": 1, "started": "2026-10-19T05:15:00Z", "finished": "2026-10-19T05:16:00Z",
               "log": "build/automations/office-fixture/x.log", "timed_out": False}

    def test_the_message_names_the_task_its_exit_and_its_log_tail(self):
        subject, body = alert.message("office-fixture", self.TASK, self.OUTCOME, "fixture failed", "PC")
        self.assertEqual(subject, "Office automation failed: office-fixture on PC")
        for text in ("exit 1", "Fixture check", "fixture failed", "Start-ScheduledTask -TaskPath '\\Office\\'"):
            self.assertIn(text, body)
        _, timed = alert.message("x", self.TASK, {**self.OUTCOME, "timed_out": True}, "", "PC")
        self.assertIn("timed out", timed)

    def test_a_send_smtp2go_refused_is_a_refusal(self):
        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        refused = Response(json.dumps({"data": {"succeeded": 0, "failed": 1, "failures": ["bad sender"]}}).encode())
        with self.assertRaises(alert.Refused):
            alert.send("api-" + "a" * 32, "s", "b", opener=lambda *a, **kw: refused)
        ok = Response(json.dumps({"data": {"succeeded": 1, "failed": 0, "email_id": "E1"}}).encode())
        self.assertEqual(alert.send("api-" + "a" * 32, "s", "b", opener=lambda *a, **kw: ok), "E1")

    def test_a_key_without_the_smtp2go_shape_is_refused(self):
        def vault(value, code=0):
            return lambda *a, **kw: subprocess.CompletedProcess(a, code, stdout=value, stderr="")

        self.assertEqual(alert.key(vault("api-" + "B" * 32 + "\n")), "api-" + "B" * 32)
        for bad, code in (("", 0), ("api-short", 0), ("x" * 36, 0), ("api-" + "B" * 32, 1)):
            with self.subTest(bad=bad[:8], code=code), self.assertRaises(alert.Refused):
                alert.key(vault(bad, code))

    def test_the_key_is_read_through_wsl_by_its_system32_path(self):
        calls = []

        def vault(argv, **kw):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, stdout="api-" + "C" * 32, stderr="")

        alert.key(vault)
        self.assertTrue(os.path.isabs(calls[0][0]), calls[0][0])
        self.assertEqual(Path(calls[0][0]).parts[-2:], ("System32", "wsl.exe"))
        argv = calls[0]
        # wsl.exe starts systemd-run itself, so nothing (no profile) runs before the bounded unit exists.
        self.assertEqual(argv[1:4], ["-e", "systemd-run", "--user"])
        for flag in ("--pipe", "--wait", "--collect", f"RuntimeMaxSec={alert.LINUX_SECONDS}",
                     f"MemoryMax={alert.LINUX_MEMORY}"):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index("--") + 1:argv.index("--") + 3], ["bash", "-lc"])
        self.assertLess(alert.LINUX_SECONDS, 90)

    def test_a_dry_run_reads_no_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".conclave" / "automations").mkdir(parents=True)
            (root / ".conclave" / "automations" / "tasks.json").write_text(json.dumps(
                {"schema_version": 1, "folder": "\\Office\\", "tasks": [FIXTURE_TASK]}), encoding="utf-8")

            def no_vault(*_a, **_kw):
                raise AssertionError("a dry run must not read the vault")

            out = io.StringIO()
            sys.stdout, saved = out, sys.stdout
            try:
                code = alert.main(["office-fixture", "--dry-run"], run=no_vault, host="PC", root=str(root))
            finally:
                sys.stdout = saved
            self.assertEqual(code, 0)
            self.assertIn("Subject: Office automation failed: office-fixture on PC", out.getvalue())


class RoundOneFixes(unittest.TestCase):
    """Defects the first independent review found in the ported code (D00 T03 §1)."""

    def manifest(self, tmp, tasks, folder=None):
        auto = Path(tmp) / ".conclave" / "automations"
        auto.mkdir(parents=True, exist_ok=True)
        doc = {"schema_version": 1, "folder": folder or chr(92) + "Office" + chr(92), "tasks": tasks}
        (auto / "tasks.json").write_text(json.dumps(doc), encoding="utf-8")
        return auto / "tasks.json"

    def test_a_command_string_and_boolean_numbers_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            for bad in ({**FIXTURE_TASK, "command": "python"}, {**FIXTURE_TASK, "timeout_minutes": True},
                        {**FIXTURE_TASK, "trigger": {"at_logon_delay_minutes": True, "every_minutes": 60}}):
                with self.subTest(bad=bad), self.assertRaises(run.TaskError):
                    run.load_tasks(str(self.manifest(tmp, [bad])))

    def test_validate_mode_exits_1_on_a_bad_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.manifest(tmp, [FIXTURE_TASK], folder=chr(92) + "Other" + chr(92))
            with contextlib_redirect():
                self.assertEqual(run.main(["--validate"], root=tmp), 1)
            self.manifest(tmp, [FIXTURE_TASK])
            with contextlib_redirect():
                self.assertEqual(run.main(["--validate"], root=tmp), 0)

    def test_two_runs_in_one_second_keep_both_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            task = {**FIXTURE_TASK, "command": ["python", "-c", "print('hi')"]}
            first = run.execute("office-fixture", task, tmp)
            second = run.execute("office-fixture", task, tmp)
            self.assertNotEqual(first["log"], second["log"])
            self.assertTrue((Path(tmp) / first["log"]).exists() and (Path(tmp) / second["log"]).exists())

    def test_a_failed_kill_still_records_the_timeout(self):
        class Hung:
            pid = 1
            def __init__(self, *a, **kw):
                pass
            def wait(self, timeout=None):
                raise subprocess.TimeoutExpired("x", timeout)

        def broken_killer(proc):
            raise subprocess.TimeoutExpired("taskkill", 60)

        with tempfile.TemporaryDirectory() as tmp:
            outcome = run.execute("office-fixture", FIXTURE_TASK, tmp, popen=Hung, killer=broken_killer)
            self.assertEqual((outcome["exit"], outcome["timed_out"], outcome.get("cleanup_failed")), (124, True, True))
            self.assertTrue((Path(tmp) / "build" / "automations" / "office-fixture" / "last.json").exists())
            self.assertIn("could not stop", (Path(tmp) / outcome["log"]).read_text(encoding="utf-8"))

    def test_the_log_tail_reads_only_the_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "big.log"
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("x" * (alert.TAIL_BYTES * 4) + "\n" + "\n".join(f"line {i}" for i in range(100)) + "\n")
            tail = alert.tail_of(str(path))
            self.assertTrue(tail.endswith("line 99"))
            self.assertLessEqual(len(tail), alert.TAIL_BYTES)
            self.assertEqual(len(tail.splitlines()), alert.LOG_LINES)


# Task Scheduler and its installer exist only on Windows with PowerShell 7; elsewhere there is nothing to install.
@unittest.skipUnless(os.name == "nt" and shutil_which("pwsh"), "Windows with PowerShell 7 is needed to run the installer")
class InstallerDryRun(unittest.TestCase):
    def fixture(self, tmp, tasks, folder=None):
        auto = Path(tmp) / ".conclave" / "automations"
        auto.mkdir(parents=True)
        for name in ("install.ps1", "run.py", "alert.py"):
            (auto / name).write_text((AUTO / name).read_text(encoding="utf-8"), encoding="utf-8")
        doc = {"schema_version": 1, "folder": folder or chr(92) + "Office" + chr(92), "tasks": tasks}
        (auto / "tasks.json").write_text(json.dumps(doc), encoding="utf-8")
        return auto / "install.ps1"

    def pwsh(self, script, *args):
        return subprocess.run(["pwsh", "-NoProfile", "-File", str(script), *args], capture_output=True, text=True,
                              timeout=120)

    def test_dry_run_lists_what_it_would_register(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.pwsh(self.fixture(tmp, [FIXTURE_TASK]), "-DryRun")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("would register " + chr(92) + "Office" + chr(92) + "office-fixture", result.stdout)

    def test_a_foreign_folder_is_refused_before_anything_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.pwsh(self.fixture(tmp, [], folder=chr(92) + "Microsoft" + chr(92)), "-DryRun")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not valid", result.stdout + result.stderr)

    def test_uninstall_dry_run_previews_removal(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.pwsh(self.fixture(tmp, [FIXTURE_TASK]), "-Uninstall", "-DryRun")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("would register", result.stdout)
            self.assertIn("nothing changed", result.stdout)



class RoundTwoFixes(unittest.TestCase):
    """Defects the second independent review found (D00 T03 §1)."""

    def load(self, doc):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            return run.load_tasks(str(path))

    def base(self, **over):
        return {"schema_version": 1, "folder": chr(92) + "Office" + chr(92), "tasks": [FIXTURE_TASK], **over}

    def test_malformed_types_are_task_errors_not_crashes(self):
        bad_docs = [self.base(schema_version=True), self.base(schema_version=1.0), self.base(tasks=[None]),
                    self.base(tasks=[{**FIXTURE_TASK, "name": 123}]),
                    self.base(tasks=[{**FIXTURE_TASK, "trigger": None}]),
                    self.base(tasks=[{**FIXTURE_TASK, "description": ""}]),
                    self.base(tasks=[{**FIXTURE_TASK, "name": "office-fixture" + chr(10)}]),
                    self.base(tasks=[{**FIXTURE_TASK, "command": ["python", "a" + chr(0)]}]),
                    self.base(tasks=[{**FIXTURE_TASK, "trigger": {"weekly": "Monday", "at": 7}}]), []]
        for doc in bad_docs:
            with self.subTest(doc=str(doc)[:60]), self.assertRaises(run.TaskError):
                self.load(doc)

    def test_send_needs_exactly_one_success_and_zero_failures(self):
        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        for data in ({"succeeded": 2, "failed": 0}, {"succeeded": 1, "failed": -1}, {"succeeded": "1", "failed": 0}):
            body = json.dumps({"data": data}).encode()
            with self.subTest(data=data), self.assertRaises(alert.Refused):
                alert.send("api-" + "a" * 32, "s", "b", opener=lambda *a, **kw: Response(body))

    def test_a_pruning_failure_cannot_cost_the_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "build" / "automations" / "office-fixture"
            folder.mkdir(parents=True)
            for i in range(run.KEEP_LOGS + 2):
                (folder / f"20000101T0000{i:02d}.000000Z-1.log").write_text("old", encoding="utf-8")
            real = os.unlink

            def locked(path, *a, **kw):
                if str(path).endswith(".log"):
                    raise PermissionError("in use")
                return real(path, *a, **kw)

            os.unlink = locked
            try:
                outcome = run.execute("office-fixture", {**FIXTURE_TASK, "command": ["python", "-c", "pass"]}, tmp)
            finally:
                os.unlink = real
            self.assertTrue((folder / "last.json").exists())
            self.assertEqual(outcome["exit"], 0)

    def test_a_timeout_whose_kill_fails_is_still_alerted(self):
        class Hung:
            pid = 1

            def __init__(self, *a, **kw):
                pass

            def wait(self, timeout=None):
                raise subprocess.TimeoutExpired("x", timeout)

        def broken_killer(proc):
            raise OSError("taskkill failed")

        alerts = []
        with tempfile.TemporaryDirectory() as tmp:
            auto = Path(tmp) / ".conclave" / "automations"
            auto.mkdir(parents=True)
            (auto / "tasks.json").write_text(json.dumps(self.base()), encoding="utf-8")
            with contextlib_redirect():
                code = run.main(["office-fixture"], root=tmp, popen=Hung, killer=broken_killer,
                                alerter=lambda *a: alerts.append(a))
        self.assertEqual(code, 124)
        self.assertEqual(len(alerts), 1)


@unittest.skipUnless(os.name == "nt" and shutil_which("pwsh"), "Windows with PowerShell 7 is needed to run the installer")
class InstallerWithFakeScheduler(unittest.TestCase):
    """The real install.ps1 against stand-ins for the ScheduledTasks commands: registers and removes nothing real."""

    HARNESS = Path(__file__).resolve().parent / "fixtures" / "fake-scheduler.ps1"

    def run_installer(self, tasks, existing, *args):
        with tempfile.TemporaryDirectory() as tmp:
            auto = Path(tmp) / ".conclave" / "automations"
            auto.mkdir(parents=True)
            for name in ("install.ps1", "run.py", "alert.py"):
                (auto / name).write_text((AUTO / name).read_text(encoding="utf-8"), encoding="utf-8")
            folder = chr(92) + "Office" + chr(92)
            (auto / "tasks.json").write_text(json.dumps({"schema_version": 1, "folder": folder, "tasks": tasks}),
                                             encoding="utf-8")
            (Path(tmp) / "existing.json").write_text(json.dumps(existing), encoding="utf-8")
            log = Path(tmp) / "calls.log"
            env = {**os.environ, "FAKE_EXISTING": str(Path(tmp) / "existing.json"), "FAKE_LOG": str(log),
                   "FAKE_SCRIPT": str(auto / "install.ps1")}
            result = subprocess.run(["pwsh", "-NoProfile", "-File", str(self.HARNESS), *args],
                                    capture_output=True, text=True, timeout=120, env=env)
            calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
            return result, calls

    def test_install_registers_each_task_with_one_repeating_trigger_and_removes_stale_ones(self):
        keep = {**FIXTURE_TASK, "name": "office-keep",
                "trigger": {"at_logon_delay_minutes": 3, "every_minutes": 60}}
        folder = chr(92) + "Office" + chr(92)
        existing = [{"path": folder, "name": "office-keep"}, {"path": folder, "name": "office-stale"},
                    {"path": chr(92) + "Other" + chr(92), "name": "someone-else"}]
        result, calls = self.run_installer([keep], existing)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        registers = [c for c in calls if c["op"] == "register"]
        self.assertEqual([c["name"] for c in registers], ["office-keep"])
        triggers = registers[0]["triggers"]
        self.assertEqual(sum(1 for t in triggers if t["Repeat"]), 1, triggers)
        self.assertTrue(any(t["AtLogOn"] and t["Delay"] == "PT3M" for t in triggers), triggers)
        self.assertEqual(registers[0]["logon"], "Interactive")
        self.assertEqual([c["name"] for c in calls if c["op"] == "unregister"], ["office-stale"])

    def test_a_daily_task_registers_one_daily_trigger(self):
        daily = {**FIXTURE_TASK, "name": "office-daily", "trigger": {"daily_at": "06:23"}}
        result, calls = self.run_installer([daily], [])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        triggers = [c for c in calls if c["op"] == "register"][0]["triggers"]
        self.assertEqual([(t["Daily"], t["At"]) for t in triggers], [(True, "06:23")])

    def test_an_empty_manifest_installs_on_a_clean_scheduler(self):
        result, calls = self.run_installer([], [])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(calls, [])
        self.assertIn("No tasks registered", result.stdout)

    def test_uninstall_removes_only_this_folder_and_dry_run_changes_nothing(self):
        folder = chr(92) + "Office" + chr(92)
        existing = [{"path": folder, "name": "office-keep"}, {"path": chr(92) + "Other" + chr(92), "name": "x"}]
        result, calls = self.run_installer([FIXTURE_TASK], existing, "-Uninstall", "-DryRun")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(calls, [])
        self.assertIn("would remove " + folder + "office-keep", result.stdout)
        result, calls = self.run_installer([FIXTURE_TASK], existing, "-Uninstall")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual([c["name"] for c in calls if c["op"] == "unregister"], ["office-keep"])

class RoundThreeFixes(unittest.TestCase):
    """Defects the third independent review found, fixed after the review cap (D00 T03 §1)."""

    def test_boolean_counts_are_not_a_successful_send(self):
        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        body = json.dumps({"data": {"succeeded": True, "failed": False}}).encode()
        with self.assertRaises(alert.Refused):
            alert.send("api-" + "a" * 32, "s", "b", opener=lambda *a, **kw: Response(body))

    def test_an_unlistable_log_folder_cannot_cost_the_outcome(self):
        real = os.listdir

        def refuse(path="."):
            if str(path).endswith("office-fixture"):
                raise PermissionError("denied")
            return real(path)

        with tempfile.TemporaryDirectory() as tmp:
            os.listdir = refuse
            try:
                outcome = run.execute("office-fixture", {**FIXTURE_TASK, "command": ["python", "-c", "pass"]}, tmp)
            finally:
                os.listdir = real
            self.assertEqual(outcome["exit"], 0)

    def test_a_launch_value_error_is_a_failed_run_and_alerted(self):
        def bad_popen(*a, **kw):
            raise ValueError("embedded null byte")

        alerts = []
        with tempfile.TemporaryDirectory() as tmp:
            auto = Path(tmp) / ".conclave" / "automations"
            auto.mkdir(parents=True)
            doc = {"schema_version": 1, "folder": chr(92) + "Office" + chr(92), "tasks": [FIXTURE_TASK]}
            (auto / "tasks.json").write_text(json.dumps(doc), encoding="utf-8")
            with contextlib_redirect():
                code = run.main(["office-fixture"], root=tmp, popen=bad_popen, alerter=lambda *a: alerts.append(a))
        self.assertEqual(code, 126)
        self.assertEqual(len(alerts), 1)

class AlertRecord(unittest.TestCase):
    """last.json records whether a failure's alert was sent (D00 T03 §5)."""

    def run_failing(self, alerter):
        with tempfile.TemporaryDirectory() as tmp:
            self.tmp = tmp
            auto = Path(tmp) / ".conclave" / "automations"
            auto.mkdir(parents=True)
            task = {**FIXTURE_TASK, "command": ["python", "-c", "import sys; sys.exit(1)"]}
            (auto / "tasks.json").write_text(json.dumps({"schema_version": 1, "folder": chr(92) + "Office" + chr(92),
                                                         "tasks": [task]}), encoding="utf-8")
            with contextlib_redirect():
                code = run.main(["office-fixture"], root=tmp, alerter=alerter)
            last = json.loads((Path(tmp) / "build" / "automations" / "office-fixture" / "last.json")
                              .read_text(encoding="utf-8"))
            self.records = [json.loads(r.read_text(encoding="utf-8")) for r in sorted(
                (Path(tmp) / "build" / "automations" / "office-fixture").glob("*.alert.json"))]
            return code, last

    def test_a_sent_alert_is_recorded_with_its_id(self):
        code, last = self.run_failing(lambda *a: "E123")
        self.assertEqual(code, 1)
        self.assertEqual(last["alert"]["email_id"], "E123")
        self.assertIn("sent_at", last["alert"])

    def test_the_real_sender_records_its_email_id(self):
        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        ok = json.dumps({"data": {"succeeded": 1, "failed": 0, "email_id": "E-REAL"}}).encode()
        vault = lambda *a, **kw: subprocess.CompletedProcess(a, 0, stdout="api-" + "B" * 32 + chr(10), stderr="")
        code, last = self.run_failing(lambda name, task, outcome, tail: alert.send_failure(
            name, task, outcome, tail, run=vault, opener=lambda *a, **kw: Response(ok), host="PC"))
        self.assertEqual((code, last["alert"]["email_id"]), (1, "E-REAL"))

    def test_an_accepted_send_without_an_id_says_so(self):
        code, last = self.run_failing(lambda *a: None)
        self.assertEqual(code, 1)
        self.assertIsNone(last["alert"]["email_id"])
        self.assertIn("without an email id", last["alert"]["note"])

    def test_a_slow_alert_never_overwrites_a_newer_outcome(self):
        def slow(name, task, outcome, tail):
            # A newer run finishes while this alert is in flight.
            folder = Path(self.tmp) / "build" / "automations" / "office-fixture"
            (folder / "last.json").write_text(json.dumps({"log": "build/automations/office-fixture/newer.log",
                                                          "exit": 0}), encoding="utf-8")
            return "E-OLD"
        code, last = self.run_failing(slow)
        self.assertEqual(last["log"], "build/automations/office-fixture/newer.log")
        self.assertNotIn("alert", last)
        self.assertEqual(len(self.records), 1)
        self.assertEqual(self.records[0]["alert"]["email_id"], "E-OLD")

    def test_an_unsent_alert_is_recorded_with_its_error(self):
        def refuse(*a):
            raise alert.Refused("bad sender")
        code, last = self.run_failing(refuse)
        self.assertEqual(code, 3)
        self.assertIn("bad sender", last["alert"]["error"])

class LastJsonLocking(unittest.TestCase):
    """Every last.json write holds the task lock, so a late alert and a newer run cannot interleave."""

    def test_an_alert_waits_for_a_run_holding_the_lock_and_then_skips_its_newer_outcome(self):
        import threading
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "build" / "automations" / "office-fixture"
            folder.mkdir(parents=True)
            (folder / "a.log").write_text("a", encoding="utf-8")
            old = {"log": "build/automations/office-fixture/a.log", "exit": 1}
            (folder / "last.json").write_text(json.dumps(old), encoding="utf-8")
            done = threading.Event()
            holder = run.TaskLock(str(folder))
            holder.__enter__()
            worker = threading.Thread(target=lambda: (run._record_alert(tmp, str(folder), old, {'email_id': 'E1'}),
                                                      done.set()))
            worker.start()
            self.assertFalse(done.wait(0.5), 'the alert wrote last.json while another writer held the lock')
            # The newer run publishes its outcome while it holds the lock, then releases it.
            newer = {"log": "build/automations/office-fixture/b.log", "exit": 0}
            (folder / "last.json").write_text(json.dumps(newer), encoding="utf-8")
            holder.__exit__(None, None, None)
            self.assertTrue(done.wait(10))
            worker.join()
            self.assertEqual(json.loads((folder / "last.json").read_text(encoding="utf-8")), newer)
            self.assertEqual(json.loads((folder / "a.log.alert.json").read_text(encoding="utf-8"))["alert"]["email_id"], "E1")

    def test_an_alert_record_whose_log_is_gone_is_pruned(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "old.log.alert.json").write_text("{}", encoding="utf-8")
            (folder / "kept.log").write_text("x", encoding="utf-8")
            (folder / "kept.log.alert.json").write_text("{}", encoding="utf-8")
            run._prune(str(folder))
            self.assertFalse((folder / "old.log.alert.json").exists())
            self.assertTrue((folder / "kept.log.alert.json").exists())

    def test_a_late_alert_for_a_pruned_log_leaves_no_record_behind(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "build" / "automations" / "office-fixture"
            folder.mkdir(parents=True)
            gone = {"log": "build/automations/office-fixture/gone.log", "exit": 1}
            run._record_alert(tmp, str(folder), gone, {'email_id': 'E2'})
            self.assertEqual(list(folder.glob("*.alert.json")), [])


if __name__ == "__main__":
    unittest.main()
