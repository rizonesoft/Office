# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The Office automations: tasks.json, run.py, alert.py, the installer and the README."""
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
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
# The tests never read this clone's real credentials: the env file is looked for in an empty folder.
_NO_SECRETS = tempfile.TemporaryDirectory()
alert.SECRETS_ROOT = _NO_SECRETS.name
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
        seen = []

        def hung(argv, **kw):
            seen.append(kw["timeout"])
            return run.process_tree.Outcome(exit=None, stopped="time limit", seconds=60.0, strays=[])

        self.assertEqual(self.main("office-pass", runner=hung), 124)
        self.assertEqual(seen, [60])  # the task's own limit, in seconds
        self.assertTrue(self.last("office-pass")["timed_out"])
        self.assertEqual(len(self.alerts), 1)

    def test_an_unsent_alert_exits_3_and_says_so_in_the_log(self):
        def refuse(*_a):
            raise alert.Refused("SMTP2GO_API_KEY is not in .secrets/office.env")

        self.tasks["tasks"][1]["command"][-1] = "import sys; sys.exit(5)"
        (self.root / ".conclave" / "automations" / "tasks.json").write_text(json.dumps(self.tasks), encoding="utf-8")
        self.assertEqual(self.main("office-fail", alerter=refuse), 3)
        log = (self.root / self.last("office-fail")["log"]).read_text(encoding="utf-8")
        self.assertIn("notice not recorded: Refused: SMTP2GO_API_KEY is not in .secrets/office.env", log)

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
            raise run.process_tree.TreeError("start: Access is denied", "start", "Access is denied")

        self.assertEqual(self.main("office-pass", runner=cannot_start), 126)
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

    def stored(self, text):
        """Point the mailer at a folder whose env file holds `text` (or no file at all for None)."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.addCleanup(setattr, alert, "SECRETS_ROOT", alert.SECRETS_ROOT)
        alert.SECRETS_ROOT = tmp.name
        if text is not None:
            folder = Path(tmp.name) / ".secrets"
            folder.mkdir()
            (folder / "office.env").write_text(text, encoding="utf-8")

    def test_the_key_comes_from_the_env_file(self):
        self.stored("SMTP2GO_API_KEY=api-" + "B" * 32 + "\n")
        self.assertEqual(alert.key(), "api-" + "B" * 32)

    def test_a_missing_or_malformed_key_is_refused_with_the_command_to_run(self):
        for text in (None, "", "SMTP2GO_API_KEY=api-short\n", "SMTP2GO_API_KEY=" + "x" * 36 + "\n", "OTHER=api-" + "B" * 32):
            with self.subTest(text=(text or "")[:24]):
                self.stored(text)
                with self.assertRaises(alert.Refused) as refused:
                    alert.key()
                self.assertIn("python scripts/import-secrets.py", str(refused.exception))

    def test_the_mailer_never_reads_the_vault_or_starts_a_process(self):
        # Owner, 2026-11-10: the repository is self-contained; importing is the operator's explicit step.
        source = (AUTO / "alert.py").read_text(encoding="utf-8")
        self.assertNotIn("vault_read", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("wsl", source.lower())

    def test_a_dry_run_reads_no_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".conclave" / "automations").mkdir(parents=True)
            (root / ".conclave" / "automations" / "tasks.json").write_text(json.dumps(
                {"schema_version": 1, "folder": "\\Office\\", "tasks": [FIXTURE_TASK]}), encoding="utf-8")

            out = io.StringIO()
            sys.stdout, saved = out, sys.stdout
            try:
                code = alert.main(["office-fixture", "--dry-run"], host="PC", root=str(root))  # no key is stored here
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

    @staticmethod
    def stuck(exit_code, stopped):
        """A runner whose child ran (and stopped or not) and whose tree would not end afterwards."""
        def runner(argv, **kw):
            error = run.process_tree.TreeError("the tree of process 1 was still running 10 s after it was stopped")
            error.outcome = run.process_tree.Outcome(exit=exit_code, stopped=stopped, seconds=1.0, strays=[])
            raise error
        return runner

    def test_a_failed_kill_still_records_the_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            outcome = run.execute("office-fixture", FIXTURE_TASK, tmp, runner=self.stuck(None, "time limit"))
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
        for name in ("install.ps1", "task-settings.ps1", "run.py", "alert.py"):
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

    def test_every_task_is_registered_to_restart_after_a_failed_launch(self):
        # D00 T07 §4: on 2026-11-09 two tasks ended with 0x8007010B before run.py started and were not tried again.
        probe = (". '{0}'; $s = New-OfficeTaskSettings -TimeoutMinutes 5; "
                 "\"$($s.RestartCount) $($s.RestartInterval) $($s.ExecutionTimeLimit) $($s.StartWhenAvailable)\"")
        done = subprocess.run(["pwsh", "-NoProfile", "-Command", probe.format(AUTO / "task-settings.ps1")],
                              capture_output=True, text=True, timeout=120)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout.strip(), "3 PT10M PT10M True")
        installer = (AUTO / "install.ps1").read_text(encoding="utf-8")
        self.assertIn(". (Join-Path $here 'task-settings.ps1')", installer)
        self.assertIn("$settings = New-OfficeTaskSettings -TimeoutMinutes $task.timeout_minutes", installer)
        self.assertNotIn("New-ScheduledTaskSettingsSet", installer)  # one place sets them, shared with the proof
        proof = (AUTO / "check-task-retry.ps1").read_text(encoding="utf-8")
        self.assertIn("New-OfficeTaskSettings -TimeoutMinutes 5 -RestartCount $RestartCount -RestartMinutes 1", proof)
        self.assertNotIn("New-ScheduledTaskSettingsSet", proof)

    def test_the_installer_says_whether_the_scheduler_log_is_on(self):
        installer = (AUTO / "install.ps1").read_text(encoding="utf-8")
        self.assertIn("wevtutil sl $schedulerLog /e:true", installer)
        self.assertIn("Turn it on once from an elevated window: wevtutil sl $schedulerLog /e:true", installer)
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

        alerts = []
        with tempfile.TemporaryDirectory() as tmp:
            auto = Path(tmp) / ".conclave" / "automations"
            auto.mkdir(parents=True)
            (auto / "tasks.json").write_text(json.dumps(self.base()), encoding="utf-8")
            with contextlib_redirect():
                code = run.main(["office-fixture"], root=tmp, runner=RoundOneFixes.stuck(None, "time limit"),
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
            for name in ("install.ps1", "task-settings.ps1", "run.py", "alert.py"):
                (auto / name).write_text((AUTO / name).read_text(encoding="utf-8"), encoding="utf-8")
            folder = chr(92) + "Office" + chr(92)
            (auto / "tasks.json").write_text(json.dumps({"schema_version": 1, "folder": folder, "tasks": tasks}),
                                             encoding="utf-8")
            (Path(tmp) / "existing.json").write_text(json.dumps(existing), encoding="utf-8")
            log = Path(tmp) / "calls.log"
            env = {**os.environ, "FAKE_EXISTING": str(Path(tmp) / "existing.json"), "FAKE_LOG": str(log),
                   "FAKE_SCRIPT": str(auto / "install.ps1"), "FAKE_SCHEDULER_LOG": getattr(self, "scheduler_log", "off")}
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

    def test_each_registered_task_restarts_three_times_ten_minutes_apart(self):
        result, calls = self.run_installer([FIXTURE_TASK], [])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual([c["restart"] for c in calls if c["op"] == "register"], ["3 x 00:10:00"])

    def test_the_scheduler_log_is_only_ever_touched_through_the_stand_in(self):
        # Round 1 of D00 T07 §4: these tests ran the real wevtutil, which from an elevated window would have
        # changed this PC's logging. Each state the installer can meet, by the calls it makes and what it says.
        channel = "Microsoft-Windows-TaskScheduler/Operational"
        cases = {"on": ([["gl", channel]], "operational log is on."),
                 "off": ([["gl", channel], ["sl", channel, "/e:true"]], "was off and is now on."),
                 "denied": ([["gl", channel], ["sl", channel, "/e:true"]],
                            f"Turn it on once from an elevated window: wevtutil sl {channel} /e:true")}
        for state, (expected, said) in cases.items():
            with self.subTest(state):
                self.scheduler_log = state
                result, calls = self.run_installer([FIXTURE_TASK], [])
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual([c["args"] for c in calls if c["op"] == "wevtutil"], expected)
                self.assertIn(said, " ".join(result.stdout.split()))

    def test_the_proof_script_refuses_a_retry_count_it_cannot_prove(self):
        done = subprocess.run(["pwsh", "-NoProfile", "-File", str(AUTO / "check-task-retry.ps1"), "-RestartCount", "1"],
                              capture_output=True, text=True, timeout=120)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("RestartCount", done.stdout + done.stderr)
        self.assertNotIn("registered", done.stdout)  # refused before any task was registered
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
            raise run.process_tree.TreeError("start: embedded null byte", "start", "embedded null byte")

        alerts = []
        with tempfile.TemporaryDirectory() as tmp:
            auto = Path(tmp) / ".conclave" / "automations"
            auto.mkdir(parents=True)
            doc = {"schema_version": 1, "folder": chr(92) + "Office" + chr(92), "tasks": [FIXTURE_TASK]}
            (auto / "tasks.json").write_text(json.dumps(doc), encoding="utf-8")
            with contextlib_redirect():
                code = run.main(["office-fixture"], root=tmp, runner=bad_popen, alerter=lambda *a: alerts.append(a))
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
                code = run.main(["office-fixture"], root=tmp, **({"alerter": alerter} if alerter else {}))
            queue = Path(tmp) / "build" / "automations" / "notices.jsonl"
            self.queue = queue.read_text(encoding="utf-8") if queue.exists() else ""
            last = json.loads((Path(tmp) / "build" / "automations" / "office-fixture" / "last.json")
                              .read_text(encoding="utf-8"))
            self.records = [json.loads(r.read_text(encoding="utf-8")) for r in sorted(
                (Path(tmp) / "build" / "automations" / "office-fixture").glob("*.alert.json"))]
            return code, last

    def test_a_recorded_notice_is_noted_with_its_id(self):
        code, last = self.run_failing(lambda *a: "N123")
        self.assertEqual(code, 1)
        self.assertEqual(last["alert"]["notice_id"], "N123")
        self.assertIn("noticed_at", last["alert"])

    def test_the_real_recorder_queues_the_failure_for_the_digest_and_sends_nothing(self):
        # D00 T03 §53 (decision 32): no email at once; the notice waits for the Monday digest.
        requests = []
        self.addCleanup(setattr, alert.urllib.request, "urlopen", alert.urllib.request.urlopen)
        alert.urllib.request.urlopen = lambda *a, **kw: requests.append(a)
        code, last = self.run_failing(None)
        self.assertEqual(code, 1)
        self.assertEqual(requests, [])
        notice = json.loads(self.queue.splitlines()[-1])
        self.assertEqual(notice["id"], last["alert"]["notice_id"])
        self.assertEqual((notice["sender"], notice["reported"]), ("run.py", None))
        self.assertIn("office-fixture failed", notice["body"])
    def test_a_slow_alert_never_overwrites_a_newer_outcome(self):
        def slow(name, task, outcome, tail):
            # A newer run finishes while this alert is in flight.
            folder = Path(self.tmp) / "build" / "automations" / "office-fixture"
            (folder / "last.json").write_text(json.dumps({"log": "build/automations/office-fixture/newer.log",
                                                          "exit": 0}), encoding="utf-8")
            return "N-OLD"
        code, last = self.run_failing(slow)
        self.assertEqual(last["log"], "build/automations/office-fixture/newer.log")
        self.assertNotIn("alert", last)
        self.assertEqual(len(self.records), 1)
        self.assertEqual(self.records[0]["alert"]["notice_id"], "N-OLD")

    def test_an_unsent_alert_is_recorded_with_its_error(self):
        def refuse(*a):
            raise alert.Refused("bad sender")
        code, last = self.run_failing(refuse)
        self.assertEqual(code, 3)
        self.assertIn("bad sender", last["alert"]["error"])

class SharedTree(unittest.TestCase):
    """Each scheduled task runs in scripts/lib/process_tree.py's tree (D00 T03 §55)."""

    PARENT = ("import subprocess, sys, time\n"
              "c = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
              "open(sys.argv[1], 'w').write(str(c.pid))\n"
              "time.sleep(float(sys.argv[2]))\n")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def task(self, sleep):
        pid = self.root / "child.pid"
        script = self.root / "parent.py"
        script.write_text(self.PARENT, encoding="utf-8")
        return {**FIXTURE_TASK, "command": [sys.executable, str(script), str(pid), str(sleep)]}, pid

    @staticmethod
    def alive(pid):
        sys.path.insert(0, str(REPO / "scripts" / "tests"))
        from test_process_tree import alive
        return alive(pid)

    def test_a_child_left_by_a_task_that_exited_0_ends_with_its_run(self):
        task, pid = self.task(0)
        outcome = run.execute("office-fixture", task, str(self.root))
        self.assertEqual(outcome["exit"], 0)
        self.assertFalse(self.alive(int(pid.read_text())))

    def test_a_child_of_a_task_past_its_limit_ends_with_it(self):
        task, pid = self.task(60)

        def quick(argv, **kw):  # the real helper, with a limit of seconds instead of the task's minutes
            return run.process_tree.run(argv, **{**kw, "timeout": 2})
        outcome = run.execute("office-fixture", task, str(self.root), runner=quick)
        self.assertEqual((outcome["exit"], outcome["timed_out"]), (124, True))
        self.assertFalse(self.alive(int(pid.read_text())))

    def main_with(self, runner):
        auto = self.root / ".conclave" / "automations"
        auto.mkdir(parents=True)
        (auto / "tasks.json").write_text(json.dumps({"schema_version": 1, "folder": chr(92) + "Office" + chr(92),
                                                     "tasks": [FIXTURE_TASK]}), encoding="utf-8")
        alerts = []
        with contextlib_redirect():
            code = run.main(["office-fixture"], root=str(self.root), runner=runner,
                            alerter=lambda *a: alerts.append(a) or "N1")
        last = json.loads((self.root / "build/automations/office-fixture/last.json").read_text(encoding="utf-8"))
        return code, last, (self.root / last["log"]).read_text(encoding="utf-8"), alerts

    def test_a_tree_that_will_not_end_after_a_normal_exit_is_a_failure(self):
        code, last, log, alerts = self.main_with(RoundOneFixes.stuck(0, None))
        self.assertEqual((code, last["exit"], last.get("cleanup_failed"), last["timed_out"]), (125, 125, True, False))
        self.assertIn("could not stop what the task started", log)
        self.assertEqual(len(alerts), 1)

    def test_a_tree_that_will_not_end_after_a_timeout_keeps_the_timeout(self):
        code, last, log, alerts = self.main_with(RoundOneFixes.stuck(None, "time limit"))
        self.assertEqual((code, last["exit"], last.get("cleanup_failed"), last["timed_out"]), (124, 124, True, True))
        self.assertIn("could not stop what the task started", log)
        self.assertEqual(len(alerts), 1)

    def test_a_task_that_failed_keeps_its_own_code_when_its_tree_will_not_end(self):
        code, last, _, _ = self.main_with(RoundOneFixes.stuck(4, None))
        self.assertEqual((code, last["exit"], last.get("cleanup_failed")), (4, 4, True))

    def test_run_py_finds_the_helper_in_its_own_repository(self):
        auto = self.root / ".conclave" / "automations"
        auto.mkdir(parents=True)
        for name in ("run.py", "alert.py"):
            shutil.copy(AUTO / name, auto / name)
        (self.root / "scripts" / "lib").mkdir(parents=True)
        for name in ("process_tree.py", "secret_store.py"):
            shutil.copy(REPO / "scripts" / "lib" / name, self.root / "scripts" / "lib" / name)
        task = {**FIXTURE_TASK, "command": [sys.executable, "-c", "print('ran in its tree')"]}
        (auto / "tasks.json").write_text(json.dumps({"schema_version": 1, "folder": chr(92) + "Office" + chr(92),
                                                     "tasks": [task]}), encoding="utf-8")
        done = subprocess.run([sys.executable, str(auto / "run.py"), "office-fixture"], capture_output=True,
                              text=True, timeout=120)
        self.assertEqual(done.returncode, 0, done.stderr)
        last = json.loads((self.root / "build/automations/office-fixture/last.json").read_text(encoding="utf-8"))
        self.assertIn("ran in its tree", (self.root / last["log"]).read_text(encoding="utf-8"))


class NoticeQueue(unittest.TestCase):
    """build/automations/notices.jsonl, the queue every sender records into for the weekly digest (D00 T03 §53)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        self.queue = Path(self.root) / alert.NOTICES

    def test_a_notice_reads_back_in_a_fresh_process(self):
        notice_id = alert.record_notice("run.py", "s", "body", self.root)
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import alert; "
                "print(alert.pending_notices(sys.argv[2])[0]['id'])")
        out = subprocess.run([sys.executable, "-c", code, str(AUTO), self.root], capture_output=True,
                             text=True, timeout=60)
        self.assertEqual(out.stdout.strip(), notice_id, out.stderr)

    def test_two_writers_at_once_both_keep_their_notice(self):
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import alert\n"
                "for n in range(20): alert.record_notice(sys.argv[3], f'{sys.argv[3]} {n}', 'b', sys.argv[2])\n")
        writers = [subprocess.Popen([sys.executable, "-c", code, str(AUTO), self.root, name])
                   for name in ("first", "second")]
        for writer in writers:
            self.assertEqual(writer.wait(timeout=120), 0)
        subjects = sorted(n["subject"] for n in alert.pending_notices(self.root))
        self.assertEqual(len(subjects), 40)
        self.assertEqual(len(set(n["id"] for n in alert.pending_notices(self.root))), 40)

    def test_a_malformed_queue_is_refused_and_kept_byte_for_byte(self):
        alert.record_notice("run.py", "s", "b", self.root)
        broken = self.queue.read_bytes() + b"not a notice\n"
        self.queue.write_bytes(broken)
        with self.assertRaises(alert.Refused) as caught:
            alert.record_notice("run.py", "s2", "b", self.root)
        self.assertIn("line 2", str(caught.exception))
        with self.assertRaises(alert.Refused):
            alert.pending_notices(self.root)
        self.assertEqual(self.queue.read_bytes(), broken)

    def test_unicode_line_separators_in_a_notice_never_poison_the_queue(self):
        # Review round 1, finding 1: U+0085, U+2028 and U+2029 are text, not record separators.
        texts = ["A\u0085B", "A B", "A B"]
        for text in texts:
            alert.record_notice("campaign", f"subject {text}", f"body {text}", self.root)
        alert.record_notice("run.py", "after", "b", self.root)
        bodies = [n["body"] for n in alert.pending_notices(self.root)]
        self.assertEqual(bodies, [f"body {t}" for t in texts] + ["b"])

    def test_a_failed_write_leaves_the_queue_whole(self):
        alert.record_notice("run.py", "kept", "b", self.root)
        before = self.queue.read_bytes()
        with mock.patch.object(alert.os, "replace", side_effect=PermissionError("denied")):
            with self.assertRaises(alert.Refused):
                alert.record_notice("run.py", "lost", "b", self.root)
        self.assertEqual(self.queue.read_bytes(), before)
        self.assertEqual([p.name for p in self.queue.parent.glob("notices.*.tmp")], [])

    def test_only_the_captured_batch_is_marked(self):
        first = alert.record_notice("run.py", "one", "b", self.root)
        batch = [n["id"] for n in alert.pending_notices(self.root)]
        late = alert.record_notice("run.py", "two", "b", self.root)  # arrives while the digest is being sent
        self.assertEqual(alert.mark_reported(batch, self.root), 1)
        self.assertEqual([n["id"] for n in alert.pending_notices(self.root)], [late])
        self.assertNotIn(first, [n["id"] for n in alert.pending_notices(self.root)])

    def test_the_notice_command_queues_a_notice(self):
        body = Path(self.root) / "body.txt"
        body.write_text("the fixes", encoding="utf-8")
        with contextlib_redirect():
            code = alert.main(["--notice", "campaign parked", str(body), "--sender", "campaign"], root=self.root)
        self.assertEqual(code, 0)
        (notice,) = alert.pending_notices(self.root)
        self.assertEqual((notice["sender"], notice["subject"], notice["body"]), ("campaign", "campaign parked",
                                                                                  "the fixes"))


class DeliveryEvidence(unittest.TestCase):
    """alert.delivery asks SMTP2GO's activity log what became of a digest, and settle_claims acts on it (D00 T03 §53)."""

    SUBJECT = "Office weekly: 1 waiting on you, 0 verified this week"

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def ask(self, answer, subject=SUBJECT):
        seen = []

        def opener(request, timeout=None):
            seen.append((request.full_url, request.get_header("X-smtp2go-api-key"), json.loads(request.data)))
            if isinstance(answer, Exception):
                raise answer
            return self.Response(json.dumps(answer).encode())
        return alert.delivery("api-k", subject, "2026-11-09T05:00:00Z", opener), seen

    def events(self, *kinds, subject=SUBJECT):
        return {"data": {"events": [{"event": kind, "email_id": "E1", "subject": subject} for kind in kinds]}}

    def test_the_request_names_the_subject_and_the_window(self):
        _, seen = self.ask({"data": {"events": []}})
        url, key, body = seen[0]
        self.assertEqual((url, key), ("https://api.smtp2go.com/v3/activity/search", "api-k"))
        self.assertEqual((body["search_subject"], body["start_date"]), (self.SUBJECT, "2026-11-09T05:00:00Z"))
        self.assertIn("end_date", body)

    def test_only_a_delivered_event_of_exactly_that_subject_is_proof(self):
        self.assertEqual(self.ask(self.events("processed", "delivered"))[0], "sent")
        self.assertEqual(self.ask(self.events("delivered", subject="Office weekly: 2 waiting"))[0], "absent")
        for failed in ("rejected", "hard-bounced", "soft-bounced"):
            with self.subTest(failed):
                self.assertEqual(self.ask(self.events("processed", failed))[0], "not-sent")
        self.assertEqual(self.ask(self.events("processed"))[0], "pending")
        self.assertEqual(self.ask({"data": {"events": []}})[0], "absent")

    def test_an_unreadable_log_is_refused(self):
        for answer in (OSError("down"), {"data": None}, {"data": {"events": "x"}}, {"error": "bad key"}):
            with self.subTest(answer=str(answer)):
                with self.assertRaises(alert.Refused):
                    self.ask(answer)

    def settle(self, answer, age, evidence=False):
        import datetime
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        scratch = mock.patch.dict(os.environ, {"OFFICE_SCRATCH": str(Path(tmp.name) / "scratch")})
        scratch.start()
        self.addCleanup(scratch.stop)
        notice = alert.record_notice("run.py", "s", "b", tmp.name)
        alert.claim_notices([notice], "d1", tmp.name, self.SUBJECT)
        if evidence:
            alert.record_sent("d1", "E1")
        claimed_at = alert.claimed_notices(tmp.name)[0]["claimed"]["at"]
        now = datetime.datetime.strptime(claimed_at, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc) + age

        def ask(subject, since):
            if isinstance(answer, Exception):
                raise answer
            return answer
        counts = alert.settle_claims(tmp.name, ask, now)
        self.last_root = tmp.name
        return counts, alert.pending_notices(tmp.name), alert.claimed_notices(tmp.name)

    def test_settling_by_what_the_log_says(self):
        import datetime
        day, hour = datetime.timedelta(days=1), datetime.timedelta(hours=2)
        cases = {  # answer, age, the digest's own record of acceptance: (outcome counted, pending, still claimed)
            ("sent", day, False): ("confirmed", 0, 0), ("not-sent", day, False): ("released", 1, 0),
            ("not-sent", datetime.timedelta(minutes=5), True): ("released", 1, 0),  # a bounce decides at any age
            ("not-sent", 6 * day, True): ("released", 1, 0),
            ("absent", day, False): ("released", 1, 0), ("absent", datetime.timedelta(minutes=5), False): ("kept", 0, 1),
            ("absent", day, True): ("kept", 0, 1),  # accepted, not yet in the log: wait, a bounce may still come
            ("pending", day, True): ("kept", 0, 1), ("pending", day, False): ("kept", 0, 1),
            ("pending", 6 * day, True): ("confirmed", 0, 0),  # the log can no longer decide: the record does
            ("pending", 6 * day, False): ("expired", 0, 0), ("absent", 6 * day, False): ("expired", 0, 0),
            ("sent", 6 * day, False): ("confirmed", 0, 0),
        }
        for (answer, age, evidence), (outcome, pending, claimed) in cases.items():
            with self.subTest(answer=answer, age=age, evidence=evidence):
                counts, now_pending, now_claimed = self.settle(answer, age, evidence)
                self.assertEqual(counts[outcome], 1)
                self.assertEqual((len(now_pending), len(now_claimed)), (pending, claimed))
                if outcome == "expired":  # neither sent again nor dropped: kept, named once by the next digest
                    self.assertEqual(len(alert.unconfirmed_notices(self.last_root)), 1)
        counts, now_pending, now_claimed = self.settle(alert.Refused("down"), hour)
        self.assertEqual((counts["kept"], len(now_claimed)), (1, 1))  # an unreadable log keeps the claim

    def test_every_scheduled_run_settles_the_claims(self):
        import datetime
        with tempfile.TemporaryDirectory() as tmp:
            auto = Path(tmp) / ".conclave" / "automations"
            auto.mkdir(parents=True)
            task = {**FIXTURE_TASK, "command": [sys.executable, "-c", "print('ok')"]}
            (auto / "tasks.json").write_text(json.dumps({"schema_version": 1, "folder": chr(92) + "Office" + chr(92),
                                                         "tasks": [task]}), encoding="utf-8")
            notice = alert.record_notice("run.py", "s", "b", tmp)
            alert.claim_notices([notice], "d1", tmp, self.SUBJECT)
            asked = []
            real = run._alert_module

            def fake_alert():
                module = real()
                module.SECRETS_ROOT = alert.SECRETS_ROOT
                module.delivery = lambda key, subject, since, *a: asked.append(subject) or "sent"
                module.key = lambda: "k"
                return module
            with mock.patch.object(run, "_alert_module", fake_alert), contextlib_redirect():
                self.assertEqual(run.main(["office-fixture"], root=tmp), 0)
            self.assertEqual(asked, [self.SUBJECT])
            self.assertEqual(alert.claimed_notices(tmp), [])
            log = Path(tmp) / json.loads((Path(tmp) / "build/automations/office-fixture/last.json").read_text())["log"]
            self.assertIn("digest claims settled: 1 confirmed sent", log.read_text(encoding="utf-8"))
            self.assertTrue(datetime)

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
