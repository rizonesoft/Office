"""Email the operator when a scheduled Office automation fails.

    python .conclave/automations/alert.py NAME            send the failure email for NAME's last run
    python .conclave/automations/alert.py NAME --dry-run  print that email instead, reading no key

run.py calls `send_failure` when a task exits non-zero or times out, so a failed run is reported by the
wrapper that saw it fail, whatever the command printed. The email carries the task, its exit, its start and
finish, and the tail of that run's log.

It goes through SMTP2GO's `/v3/email/send` from the Rizonetech website sender, the same verified sender and
key the Rizonetech automations use (Rizonesoft is a brand of Rizonetech). The key is read at send time from
the Conclave vault item "Rizonetech SMTP2GO (website mail)" through `conclave-op` in WSL, for this run only:
never written to disk, an argument, or the output. SMTP2GO answers a refused send with HTTP 200 and
`succeeded: 0`, so anything but one success and no failures is a refusal.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
ITEM = "op://Conclave/jq2q47sqbpdwacivbjead5rrku"
ENDPOINT = "https://api.smtp2go.com/v3/email/send"
SENDER = "Office automations <website@rizonetech.com>"
TO = "rizonetech@gmail.com"
TAIL_BYTES = 256 * 1024
LOG_LINES = 60


class Refused(Exception):
    pass


def key(run=subprocess.run) -> str:
    """The API key, refused unless it has SMTP2GO's shape ("api-" and 32 letters or digits); never echoed."""
    result = run(["wsl.exe", "-e", "bash", "-lc", f'conclave-op read "{ITEM}/credential"'],
                 capture_output=True, text=True, timeout=90,
                 creationflags=0x08000000 if os.name == "nt" else 0)  # CREATE_NO_WINDOW: run.py has no console
    value = (result.stdout or "").strip()
    if result.returncode != 0 or not value:
        raise Refused("vault field credential is unavailable")
    if len(value) != 36 or not value.startswith("api-") or not value[4:].isalnum() or not value.isascii():
        raise Refused("vault field credential does not have the SMTP2GO key shape")
    return value


def message(name: str, task: dict, outcome: dict, tail: str, host: str) -> tuple[str, str]:
    """The subject and plain-text body of the failure email."""
    exit_text = "timed out" if outcome.get("timed_out") else f"exit {outcome.get('exit')}"
    body = "\n".join([
        f"{name} failed on {host}: {exit_text}.",
        "",
        f"What it does: {task.get('description') or '(no description)'}",
        f"Command: {' '.join(task.get('command', []))}",
        f"Started: {outcome.get('started') or 'unknown'}",
        f"Finished: {outcome.get('finished') or 'unknown'}",
        "",
        f"Last {LOG_LINES} lines of this run's log ({outcome.get('log') or 'no log'}):",
        "",
        tail or "(the run wrote no output)",
        "",
        f"Run again: Start-ScheduledTask -TaskPath '\\Office\\' -TaskName {name}",
        f"Or directly: python .conclave/automations/run.py {name}",
    ])
    return f"Office automation failed: {name} on {host}", body


def send(api_key: str, subject: str, body: str, opener=urllib.request.urlopen) -> str:
    """Post the email; refuse anything but one success and no failures."""
    payload = json.dumps({"sender": SENDER, "to": [TO], "subject": subject, "text_body": body}).encode()
    request = urllib.request.Request(ENDPOINT, data=payload, method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json", "X-Smtp2go-Api-Key": api_key})
    with opener(request, timeout=60) as response:
        data = json.loads(response.read().decode() or "{}").get("data", {})
    sent, failed = data.get("succeeded"), data.get("failed")
    if type(sent) is not int or type(failed) is not int or sent != 1 or failed != 0:  # bool is not a count
        raise Refused(f"SMTP2GO refused the send: {data.get('failures') or data.get('error') or data}")
    return data.get("email_id", "")


def send_failure(name: str, task: dict, outcome: dict, tail: str, run=subprocess.run,
                 opener=urllib.request.urlopen, host: str | None = None) -> str:
    subject, body = message(name, task, outcome, tail, host or socket.gethostname())
    return send(key(run), subject, body, opener)


def tail_of(path: str, lines: int = LOG_LINES) -> str:
    try:
        with open(path, "rb") as fh:  # read only the end, so a huge log cannot exhaust memory
            fh.seek(0, os.SEEK_END)
            fh.seek(max(0, fh.tell() - TAIL_BYTES))
            text = fh.read().decode("utf-8", errors="replace")
    except OSError:
        return ""
    return "\n".join(text.splitlines()[-lines:]).rstrip()


def main(argv=None, run=subprocess.run, opener=urllib.request.urlopen, host=None, root=REPO) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("name", help="the task that failed, e.g. office-winui-pin")
    p.add_argument("--dry-run", action="store_true", help="print the email; read no key and send nothing")
    args = p.parse_args(argv)
    with open(os.path.join(root, ".conclave", "automations", "tasks.json"), encoding="utf-8") as fh:
        tasks = {t["name"]: t for t in json.load(fh)["tasks"]}
    task = tasks.get(args.name)
    if task is None:
        print(f"alert: no task named {args.name}", file=sys.stderr)
        return 2
    try:
        with open(os.path.join(root, "build", "automations", args.name, "last.json"), encoding="utf-8") as fh:
            outcome = json.load(fh)
    except (OSError, ValueError):
        outcome = {}
    tail = tail_of(os.path.join(root, outcome["log"])) if outcome.get("log") else ""
    if args.dry_run:
        subject, body = message(args.name, task, outcome, tail, host or socket.gethostname())
        print(f"To: {TO}\nSubject: {subject}\n\n{body}")
        return 0
    try:
        email_id = send_failure(args.name, task, outcome, tail, run, opener, host)
    except (Refused, OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"alert not sent: {error}", file=sys.stderr)
        return 1
    print(f"alert sent to {TO} for {args.name} (SMTP2GO email {email_id})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
