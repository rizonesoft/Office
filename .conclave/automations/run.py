"""Run one Office-2028 automation, keep its log, and email the operator when it fails.

    python .conclave/automations/run.py NAME

Task Scheduler starts this through `pythonw.exe` (install.ps1 registers every task in tasks.json with it). It
runs the task's command from the repository root with the task's timeout, writes the combined output to
`build/automations/<name>/<UTC>.log` (the newest 20 kept) and the outcome to `build/automations/<name>/last.json`,
and on a non-zero exit, a timeout, or a command that cannot start (126) sends the failure email through
alert.py. Every process it starts, and every nested launch in the tasks, carries CREATE_NO_WINDOW, so a
scheduled run never opens a console on the desktop. Windows has no systemd
`OnFailure=`, so this wrapper is the one place a failure is reported. Its own exit is the command's (124 on a
timeout, or 3 when the alert could not be sent), so Task Scheduler's Last Run Result shows the failure too.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
NAME = re.compile(r"^office-2028-[a-z0-9-]+$")
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
KEEP_LOGS = 20
NO_WINDOW = 0x08000000


class TaskError(ValueError):
    pass


def load_tasks(path: str) -> dict[str, dict]:
    """The tasks in tasks.json by name, refused unless every entry is well formed (types checked before use)."""
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    if (not isinstance(doc, dict) or type(doc.get("schema_version")) is not int or doc["schema_version"] != 1
            or doc.get("folder") != "\\Office-2028\\" or not isinstance(doc.get("tasks"), list)):
        raise TaskError("tasks.json needs schema_version 1, folder \\Office-2028\\, and a tasks list")
    out: dict[str, dict] = {}
    for task in doc["tasks"]:
        if not isinstance(task, dict):
            raise TaskError(f"every task must be an object, not {task!r}")
        name = task.get("name")
        if not isinstance(name, str) or not NAME.fullmatch(name) or name in out:
            raise TaskError(f"task name {name!r} must be a unique office-2028-* name")
        if set(task) != {"name", "description", "command", "trigger", "timeout_minutes"}:
            raise TaskError(f"{name}: needs exactly name, description, command, trigger, timeout_minutes")
        if not isinstance(task["description"], str) or not task["description"].strip():
            raise TaskError(f"{name}: description must be non-empty text")
        command = task["command"]
        if (not isinstance(command, list) or not command
                or not all(isinstance(c, str) and c and chr(0) not in c for c in command)):
            raise TaskError(f"{name}: command must be a non-empty list of strings without NUL")
        if not _whole(task["timeout_minutes"]):
            raise TaskError(f"{name}: timeout_minutes must be a positive whole number")
        trigger = task["trigger"]
        if not isinstance(trigger, dict):
            raise TaskError(f"{name}: trigger must be an object")
        if set(trigger) == {"at_logon_delay_minutes", "every_minutes"}:
            if not all(_whole(trigger[k]) for k in trigger):
                raise TaskError(f"{name}: a logon trigger needs positive whole minutes")
        elif set(trigger) == {"weekly", "at"}:
            if (trigger["weekly"] not in DAYS or not isinstance(trigger["at"], str)
                    or not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", trigger["at"])):
                raise TaskError(f"{name}: a weekly trigger needs a day name and an HH:MM time")
        else:
            raise TaskError(f"{name}: trigger must be at-logon-and-every or weekly-at")
        out[name] = task
    return out


def _whole(value) -> bool:
    """A positive whole number; JSON true is not one, though Python counts bool as int."""
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def resolve(command: list[str]) -> list[str]:
    """`python` is the console interpreter beside this one (Task Scheduler starts pythonw.exe)."""
    if command[0] != "python":
        return command
    here = sys.executable
    console = os.path.join(os.path.dirname(here), "python.exe")
    return [console if os.name == "nt" and os.path.isfile(console) else here] + command[1:]


def _utc(stamp: bool = False) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    # The file stamp carries microseconds and the process id, so two runs in one second never share a log.
    return now.strftime("%Y%m%dT%H%M%S.%fZ") + f"-{os.getpid()}" if stamp else now.strftime("%Y-%m-%dT%H:%M:%SZ")


def _kill_tree(proc) -> None:
    if os.name == "nt":
        done = subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, timeout=60,
                              creationflags=NO_WINDOW)
        if done.returncode != 0 and proc.poll() is None:
            raise OSError(f"taskkill exited {done.returncode}: {done.stderr.decode(errors='replace').strip()}")
    else:
        proc.kill()
    proc.wait(timeout=60)


def execute(name: str, task: dict, root: str, popen=subprocess.Popen, killer=_kill_tree) -> dict:
    """Run the task's command into a fresh log; returns the outcome recorded in last.json."""
    folder = os.path.join(root, "build", "automations", name)
    os.makedirs(folder, exist_ok=True)
    log = os.path.join(folder, _utc(stamp=True) + ".log")
    outcome = {"name": name, "started": _utc(), "log": os.path.relpath(log, root).replace("\\", "/"),
               "timed_out": False}
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    with open(log, "wb") as out:
        try:
            proc = popen(resolve(task["command"]), cwd=root, stdout=out, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, env=env, creationflags=NO_WINDOW if os.name == "nt" else 0)
        except (OSError, ValueError) as error:  # never started: a failed run like any other, so it is alerted
            out.write(f"run.py: could not start {task['command'][0]}: {error}\n".encode("utf-8"))
            proc = None
            outcome["exit"] = 126
        if proc is not None:
            try:
                outcome["exit"] = proc.wait(timeout=task["timeout_minutes"] * 60)
            except subprocess.TimeoutExpired:
                outcome.update(exit=124, timed_out=True)
                try:
                    killer(proc)
                except (OSError, subprocess.SubprocessError) as error:  # still a timeout: recorded and alerted
                    out.write(f"run.py: could not stop the timed-out process: {error}\n".encode("utf-8"))
                    outcome["cleanup_failed"] = True
    outcome["finished"] = _utc()
    with TaskLock(folder):
        _write_outcome(folder, outcome)
    _prune(folder)  # after the outcome is safe, and never fatal: a locked old log must not cost the alert
    return outcome


class TaskLock:
    """An interprocess lock per task folder (msvcrt on Windows, flock elsewhere), held around every last.json read
    and write so a run's outcome and a late alert's update can never interleave. The OS releases it if the holder
    dies; waiting is bounded, and a lock that cannot be had is an error, never a silent unlocked write."""

    def __init__(self, folder: str, wait: float = 60.0):
        self.path = os.path.join(folder, ".last.lock")
        self.wait = wait
        self.fd = None

    def __enter__(self):
        import time
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        deadline = time.monotonic() + self.wait
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    os.lseek(self.fd, 0, os.SEEK_SET)
                    msvcrt.locking(self.fd, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError:
                if time.monotonic() >= deadline:
                    os.close(self.fd)
                    self.fd = None
                    raise TimeoutError(f"could not lock {self.path} within {self.wait:.0f}s")
                time.sleep(0.05)

    def __exit__(self, *exc):
        if self.fd is not None:
            try:
                if os.name == "nt":
                    import msvcrt
                    os.lseek(self.fd, 0, os.SEEK_SET)
                    msvcrt.locking(self.fd, msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.fd, fcntl.LOCK_UN)
            finally:
                os.close(self.fd)
                self.fd = None
        return False


def _write_outcome(folder: str, outcome: dict) -> None:
    """last.json, replaced atomically through a temporary file unique to this run."""
    fd, tmp = tempfile.mkstemp(dir=folder, prefix="last.json.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(outcome, fh, indent=2)
        os.replace(tmp, os.path.join(folder, "last.json"))
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _prune(folder: str) -> None:
    """Keep the newest logs. Optional housekeeping: any failure here is left for the next run."""
    try:
        logs = sorted(f for f in os.listdir(folder) if f.endswith(".log"))
    except OSError:
        return
    for old in logs[:-KEEP_LOGS]:
        try:
            os.unlink(os.path.join(folder, old))
        except OSError:
            pass  # in use or already gone; the next run tries again
    try:  # alert records are swept on their own: any whose log is gone, however it went
        for name in os.listdir(folder):
            if name.endswith(".log.alert.json") and not os.path.exists(os.path.join(folder, name[:-len(".alert.json")])):
                try:
                    os.unlink(os.path.join(folder, name))
                except OSError:
                    pass
    except OSError:
        return


def _alert_module():
    spec = importlib.util.spec_from_file_location("office2028_alert", os.path.join(HERE, "alert.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str], root: str = REPO, popen=subprocess.Popen, alerter=None, killer=_kill_tree) -> int:
    if len(argv) != 1:
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        return 2
    manifest = os.path.join(root, ".conclave", "automations", "tasks.json")
    if argv[0] == "--validate":  # the installer's gate: every rule in load_tasks, nothing run
        try:
            print(f"tasks.json valid: {len(load_tasks(manifest))} task(s)")
        except (TaskError, OSError, ValueError) as error:
            print(f"run: tasks.json is not valid: {error}", file=sys.stderr)
            return 1
        return 0
    tasks = load_tasks(manifest)
    task = tasks.get(argv[0])
    if task is None:
        print(f"run: no task named {argv[0]} in tasks.json", file=sys.stderr)
        return 2
    outcome = execute(argv[0], task, root, popen, killer)
    if outcome["exit"] == 0:
        return 0
    alert = _alert_module()
    folder = os.path.join(root, "build", "automations", argv[0])
    try:
        sent = (alerter or alert.send_failure)(argv[0], task, outcome, alert.tail_of(os.path.join(root, outcome["log"])))
    except Exception as error:  # the run already failed; an unsent alert must still show, as exit 3
        with open(os.path.join(root, outcome["log"]), "a", encoding="utf-8") as fh:
            fh.write(f"\nrun.py: alert not sent: {type(error).__name__}: {error}\n")
        _record_alert(root, folder, outcome, {"error": f"{type(error).__name__}: {error}", "at": _utc()})
        return 3
    if isinstance(sent, str) and sent:
        result = {"sent_at": _utc(), "email_id": sent}
    else:  # accepted, but SMTP2GO named no message: say so rather than invent an id
        result = {"sent_at": _utc(), "email_id": None, "note": "the send was accepted without an email id"}
    _record_alert(root, folder, outcome, result)
    return outcome["exit"]


def _record_alert(root: str, folder: str, outcome: dict, result: dict) -> None:
    """Record the alert beside this run's log, and in last.json only while last.json still describes this run:
    a slow alert must never overwrite a newer run's outcome."""
    log = os.path.join(root, outcome["log"])
    record = {"log": outcome["log"], "alert": result}
    with TaskLock(folder):  # the read, the comparison and the replacement are one step for every writer
        if os.path.exists(log):  # a log already pruned keeps no sidecar, so none can be orphaned
            fd, tmp = tempfile.mkstemp(dir=folder, prefix="alert.", suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    json.dump(record, fh, indent=2)
                os.replace(tmp, log + ".alert.json")
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
        try:
            with open(os.path.join(folder, "last.json"), encoding="utf-8") as fh:
                current = json.load(fh)
        except (OSError, ValueError):
            return
        if current.get("log") == outcome["log"]:
            _write_outcome(folder, {**current, "alert": result})


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
