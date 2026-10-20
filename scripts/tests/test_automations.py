"""The Office-2028 automations: tasks.json, run.py, alert.py, the installer and the README."""
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


run = load("office2028_run", AUTO / "run.py")
alert = load("office2028_alert", AUTO / "alert.py")
# One well-formed task, for tests that must not depend on what tasks.json lists today.
FIXTURE_TASK = {"name": "office-2028-fixture", "description": "Fixture check", "command": ["python", "scripts/fixture.py"],
                "trigger": {"weekly": "Monday", "at": "07:00"}, "timeout_minutes": 5}


class Manifest(unittest.TestCase):
    def test_the_manifest_loads_and_every_command_script_exists(self):
        tasks = run.load_tasks(str(AUTO / "tasks.json"))
        for name, task in tasks.items():
            with self.subTest(name=name):
                self.assertEqual(task["command"][0], "python")
                self.assertTrue((REPO / task["command"][1]).is_file(), task["command"][1])

    def test_the_readme_lists_exactly_the_manifest(self):
        rows = [line.split("|")[1].strip().strip("`") for line in (AUTO / "README.md").read_text(encoding="utf-8")
                .splitlines() if line.startswith("| `office-2028-")]
        self.assertEqual(sorted(rows), sorted(run.load_tasks(str(AUTO / "tasks.json"))))

    def test_the_installer_reads_the_manifest_and_names_no_task(self):
        text = (AUTO / "install.ps1").read_text(encoding="utf-8")
        self.assertIn("tasks.json", text)
        self.assertNotIn("office-2028-", text)

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
        self.tasks = {"schema_version": 1, "folder": "\\Office-2028\\", "tasks": [
            self.task("office-2028-pass", "print('all good')"),
            self.task("office-2028-fail", "import sys; print('line one'); print('it broke'); sys.exit(3)"),
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
        self.assertEqual(self.main("office-2028-pass"), 0)
        outcome = self.last("office-2028-pass")
        self.assertEqual(outcome["exit"], 0)
        self.assertIn("all good", (self.root / outcome["log"]).read_text(encoding="utf-8"))
        self.assertEqual(self.alerts, [])

    def test_a_failing_run_alerts_with_its_log_tail(self):
        self.assertEqual(self.main("office-2028-fail"), 3)
        (name, task, outcome, tail), = self.alerts
        self.assertEqual((name, outcome["exit"], task["description"]), ("office-2028-fail", 3, "fixture office-2028-fail"))
        self.assertIn("it broke", tail)

    def test_a_timeout_stops_the_run_and_alerts(self):
        killed = []

        class Hung:
            pid = 0

            def __init__(self, *a, **kw):
                pass

            def wait(self, timeout=None):
                raise subprocess.TimeoutExpired("hung", timeout)

        self.assertEqual(self.main("office-2028-pass", popen=Hung, killer=killed.append), 124)
        self.assertEqual(len(killed), 1)
        self.assertTrue(self.last("office-2028-pass")["timed_out"])
        self.assertEqual(len(self.alerts), 1)

    def test_an_unsent_alert_exits_3_and_says_so_in_the_log(self):
        def refuse(*_a):
            raise alert.Refused("vault field credential is unavailable")

        self.tasks["tasks"][1]["command"][-1] = "import sys; sys.exit(5)"
        (self.root / ".conclave" / "automations" / "tasks.json").write_text(json.dumps(self.tasks), encoding="utf-8")
        self.assertEqual(self.main("office-2028-fail", alerter=refuse), 3)
        log = (self.root / self.last("office-2028-fail")["log"]).read_text(encoding="utf-8")
        self.assertIn("alert not sent: Refused: vault field credential is unavailable", log)

    def test_only_the_newest_logs_are_kept(self):
        folder = self.root / "build" / "automations" / "office-2028-pass"
        folder.mkdir(parents=True)
        for i in range(run.KEEP_LOGS + 5):
            (folder / f"20000101T0000{i:02d}Z.log").write_text("old", encoding="utf-8")
        self.main("office-2028-pass")
        self.assertEqual(len(list(folder.glob("*.log"))), run.KEEP_LOGS)
        self.assertTrue((self.root / self.last("office-2028-pass")["log"]).exists())

    def test_a_command_that_cannot_start_is_recorded_and_alerted(self):
        def cannot_start(*_a, **_kw):
            raise PermissionError(13, "Access is denied")

        self.assertEqual(self.main("office-2028-pass", popen=cannot_start), 126)
        outcome = self.last("office-2028-pass")
        self.assertEqual(outcome["exit"], 126)
        self.assertIn("could not start", (self.root / outcome["log"]).read_text(encoding="utf-8"))
        (_name, _task, alerted, tail), = self.alerts
        self.assertEqual(alerted["exit"], 126)
        self.assertIn("Access is denied", tail)

    def test_every_nested_launch_opens_no_console(self):
        for path in (AUTO / "run.py", AUTO / "alert.py"):
            text = path.read_text(encoding="utf-8")
            calls = text.count("subprocess.run([") + text.count("subprocess.Popen(") + text.count("run([\"wsl.exe\"")
            flagged = text.count("creationflags=")
            with self.subTest(path=path.name):
                self.assertGreaterEqual(flagged, calls - text.count('"git", "init"'), path.name)

    def test_an_unknown_task_is_refused(self):
        self.assertEqual(self.main("office-2028-missing"), 2)


class Alert(unittest.TestCase):
    TASK = {"description": "Fixture check", "command": ["python", "scripts/fixture.py"]}
    OUTCOME = {"exit": 1, "started": "2026-10-19T05:15:00Z", "finished": "2026-10-19T05:16:00Z",
               "log": "build/automations/office-2028-fixture/x.log", "timed_out": False}

    def test_the_message_names_the_task_its_exit_and_its_log_tail(self):
        subject, body = alert.message("office-2028-fixture", self.TASK, self.OUTCOME, "fixture failed", "PC")
        self.assertEqual(subject, "Office-2028 automation failed: office-2028-fixture on PC")
        for text in ("exit 1", "Fixture check", "fixture failed", "Start-ScheduledTask -TaskPath '\\Office-2028\\'"):
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

    def test_a_dry_run_reads_no_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".conclave" / "automations").mkdir(parents=True)
            (root / ".conclave" / "automations" / "tasks.json").write_text(json.dumps(
                {"schema_version": 1, "folder": "\\Office-2028\\", "tasks": [FIXTURE_TASK]}), encoding="utf-8")

            def no_vault(*_a, **_kw):
                raise AssertionError("a dry run must not read the vault")

            out = io.StringIO()
            sys.stdout, saved = out, sys.stdout
            try:
                code = alert.main(["office-2028-fixture", "--dry-run"], run=no_vault, host="PC", root=str(root))
            finally:
                sys.stdout = saved
            self.assertEqual(code, 0)
            self.assertIn("Subject: Office-2028 automation failed: office-2028-fixture on PC", out.getvalue())


class RoundOneFixes(unittest.TestCase):
    """Defects the first independent review found in the ported code (D00 T03 §1)."""

    def manifest(self, tmp, tasks, folder=None):
        auto = Path(tmp) / ".conclave" / "automations"
        auto.mkdir(parents=True, exist_ok=True)
        doc = {"schema_version": 1, "folder": folder or chr(92) + "Office-2028" + chr(92), "tasks": tasks}
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
            first = run.execute("office-2028-fixture", task, tmp)
            second = run.execute("office-2028-fixture", task, tmp)
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
            outcome = run.execute("office-2028-fixture", FIXTURE_TASK, tmp, popen=Hung, killer=broken_killer)
            self.assertEqual((outcome["exit"], outcome["timed_out"], outcome.get("cleanup_failed")), (124, True, True))
            self.assertTrue((Path(tmp) / "build" / "automations" / "office-2028-fixture" / "last.json").exists())
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
        doc = {"schema_version": 1, "folder": folder or chr(92) + "Office-2028" + chr(92), "tasks": tasks}
        (auto / "tasks.json").write_text(json.dumps(doc), encoding="utf-8")
        return auto / "install.ps1"

    def pwsh(self, script, *args):
        return subprocess.run(["pwsh", "-NoProfile", "-File", str(script), *args], capture_output=True, text=True,
                              timeout=120)

    def test_dry_run_lists_what_it_would_register(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.pwsh(self.fixture(tmp, [FIXTURE_TASK]), "-DryRun")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("would register " + chr(92) + "Office-2028" + chr(92) + "office-2028-fixture", result.stdout)

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
        return {"schema_version": 1, "folder": chr(92) + "Office-2028" + chr(92), "tasks": [FIXTURE_TASK], **over}

    def test_malformed_types_are_task_errors_not_crashes(self):
        bad_docs = [self.base(schema_version=True), self.base(schema_version=1.0), self.base(tasks=[None]),
                    self.base(tasks=[{**FIXTURE_TASK, "name": 123}]),
                    self.base(tasks=[{**FIXTURE_TASK, "trigger": None}]),
                    self.base(tasks=[{**FIXTURE_TASK, "description": ""}]),
                    self.base(tasks=[{**FIXTURE_TASK, "name": "office-2028-fixture" + chr(10)}]),
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
            folder = Path(tmp) / "build" / "automations" / "office-2028-fixture"
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
                outcome = run.execute("office-2028-fixture", {**FIXTURE_TASK, "command": ["python", "-c", "pass"]}, tmp)
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
                code = run.main(["office-2028-fixture"], root=tmp, popen=Hung, killer=broken_killer,
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
            folder = chr(92) + "Office-2028" + chr(92)
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
        keep = {**FIXTURE_TASK, "name": "office-2028-keep",
                "trigger": {"at_logon_delay_minutes": 3, "every_minutes": 60}}
        folder = chr(92) + "Office-2028" + chr(92)
        existing = [{"path": folder, "name": "office-2028-keep"}, {"path": folder, "name": "office-2028-stale"},
                    {"path": chr(92) + "Other" + chr(92), "name": "someone-else"}]
        result, calls = self.run_installer([keep], existing)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        registers = [c for c in calls if c["op"] == "register"]
        self.assertEqual([c["name"] for c in registers], ["office-2028-keep"])
        triggers = registers[0]["triggers"]
        self.assertEqual(sum(1 for t in triggers if t["Repeat"]), 1, triggers)
        self.assertTrue(any(t["AtLogOn"] and t["Delay"] == "PT3M" for t in triggers), triggers)
        self.assertEqual(registers[0]["logon"], "Interactive")
        self.assertEqual([c["name"] for c in calls if c["op"] == "unregister"], ["office-2028-stale"])

    def test_uninstall_removes_only_this_folder_and_dry_run_changes_nothing(self):
        folder = chr(92) + "Office-2028" + chr(92)
        existing = [{"path": folder, "name": "office-2028-keep"}, {"path": chr(92) + "Other" + chr(92), "name": "x"}]
        result, calls = self.run_installer([FIXTURE_TASK], existing, "-Uninstall", "-DryRun")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(calls, [])
        self.assertIn("would remove " + folder + "office-2028-keep", result.stdout)
        result, calls = self.run_installer([FIXTURE_TASK], existing, "-Uninstall")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual([c["name"] for c in calls if c["op"] == "unregister"], ["office-2028-keep"])


if __name__ == "__main__":
    unittest.main()
