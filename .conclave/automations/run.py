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

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
NAME = re.compile(r"^office-2028-[a-z0-9-]+$")
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
KEEP_LOGS = 20
NO_WINDOW = 0x08000000


class TaskError(ValueError):
    pass


def load_tasks(path: str) -> dict[str, dict]:
    """The tasks in tasks.json by name, refused unless every entry is well formed."""
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    if doc.get("schema_version") != 1 or doc.get("folder") != "\\Office-2028\\" or not isinstance(doc.get("tasks"), list):
        raise TaskError("tasks.json needs schema_version 1, folder \\Office-2028\\, and a tasks list")
    out: dict[str, dict] = {}
    for task in doc["tasks"]:
        name = task.get("name", "")
        if not NAME.match(name) or name in out:
            raise TaskError(f"task name {name!r} must be a unique office-2028-* name")
        if set(task) != {"name", "description", "command", "trigger", "timeout_minutes"}:
            raise TaskError(f"{name}: needs exactly name, description, command, trigger, timeout_minutes")
        command = task["command"]
        if not command or not all(isinstance(c, str) and c for c in command):
            raise TaskError(f"{name}: command must be a non-empty list of strings")
        if not isinstance(task["timeout_minutes"], int) or task["timeout_minutes"] <= 0:
            raise TaskError(f"{name}: timeout_minutes must be a positive whole number")
        trigger = task["trigger"]
        if set(trigger) == {"at_logon_delay_minutes", "every_minutes"}:
            if not all(isinstance(trigger[k], int) and trigger[k] > 0 for k in trigger):
                raise TaskError(f"{name}: a logon trigger needs positive whole minutes")
        elif set(trigger) == {"weekly", "at"}:
            if trigger["weekly"] not in DAYS or not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", trigger["at"]):
                raise TaskError(f"{name}: a weekly trigger needs a day name and an HH:MM time")
        else:
            raise TaskError(f"{name}: trigger must be at-logon-and-every or weekly-at")
        out[name] = task
    return out


def resolve(command: list[str]) -> list[str]:
    """`python` is the console interpreter beside this one (Task Scheduler starts pythonw.exe)."""
    if command[0] != "python":
        return command
    here = sys.executable
    console = os.path.join(os.path.dirname(here), "python.exe")
    return [console if os.name == "nt" and os.path.isfile(console) else here] + command[1:]


def _utc(stamp: bool = False) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y%m%dT%H%M%SZ" if stamp else "%Y-%m-%dT%H:%M:%SZ")


def _kill_tree(proc) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, timeout=60,
                       creationflags=NO_WINDOW)
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
        except OSError as error:  # the command never started: a failed run like any other, so it is alerted
            out.write(f"run.py: could not start {task['command'][0]}: {error}\n".encode("utf-8"))
            proc = None
            outcome["exit"] = 126
        if proc is not None:
            try:
                outcome["exit"] = proc.wait(timeout=task["timeout_minutes"] * 60)
            except subprocess.TimeoutExpired:
                killer(proc)
                outcome.update(exit=124, timed_out=True)
    outcome["finished"] = _utc()
    logs = sorted(f for f in os.listdir(folder) if f.endswith(".log"))
    for old in logs[:-KEEP_LOGS]:
        os.unlink(os.path.join(folder, old))
    tmp = os.path.join(folder, "last.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(outcome, fh, indent=2)
    os.replace(tmp, os.path.join(folder, "last.json"))
    return outcome


def _alert_module():
    spec = importlib.util.spec_from_file_location("office2028_alert", os.path.join(HERE, "alert.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str], root: str = REPO, popen=subprocess.Popen, alerter=None, killer=_kill_tree) -> int:
    if len(argv) != 1:
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        return 2
    tasks = load_tasks(os.path.join(root, ".conclave", "automations", "tasks.json"))
    task = tasks.get(argv[0])
    if task is None:
        print(f"run: no task named {argv[0]} in tasks.json", file=sys.stderr)
        return 2
    outcome = execute(argv[0], task, root, popen, killer)
    if outcome["exit"] == 0:
        return 0
    alert = _alert_module()
    try:
        (alerter or alert.send_failure)(argv[0], task, outcome, alert.tail_of(os.path.join(root, outcome["log"])))
    except Exception as error:  # the run already failed; an unsent alert must still show, as exit 3
        with open(os.path.join(root, outcome["log"]), "a", encoding="utf-8") as fh:
            fh.write(f"\nrun.py: alert not sent: {type(error).__name__}: {error}\n")
        return 3
    return outcome["exit"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
