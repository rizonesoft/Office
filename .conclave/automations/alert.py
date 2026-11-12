# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Queue the operator's notices for the weekly digest, and send the emails this repository sends.

    python .conclave/automations/alert.py --notice SUBJECT BODY_FILE   queue a notice (the campaign's parks)
    python .conclave/automations/alert.py --list                       the notices no digest has completed
    python .conclave/automations/alert.py NAME            send the failure email for NAME's last run now (by hand)
    python .conclave/automations/alert.py NAME --dry-run  print that email instead, reading no key

Decision 32 of the campaign scope record allows one email a week, the owner digest, and no other interruption
(D00 T03 §53): run.py records a failed or timed-out task as a notice (`record_notice`), as do the host check, the
version checks and the campaign's parks, and `scripts/owner-digest.py` reports the pending ones and marks that batch
reported once it was delivered. The notice carries the task, its exit, its start and finish, and the tail of that
run's log. Sending one failure email at once stays available by hand, as above.

It goes through SMTP2GO's `/v3/email/send` from the Rizonetech website sender, the same verified sender and
key the Rizonetech automations use (Rizonesoft is a brand of Rizonetech). The key comes from the repository's
own untracked env file, `.secrets/office.env`, which `python scripts/import-secrets.py` fills from the Conclave
vault item "Rizonetech SMTP2GO (website mail)" (owner, 2026-11-10: the repository is self-contained). Nothing here
reads the vault: without the import a send is refused with the command to run. The key is never an argument or in
the output.
SMTP2GO answers a refused send with HTTP 200 and
`succeeded: 0`, so anything but one success and no failures is a refusal.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import socket
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts", "lib"))
import secret_store  # noqa: E402

NAME = "SMTP2GO_API_KEY"
SECRETS_ROOT = REPO  # where .secrets/office.env is looked for; the tests point it at an empty folder
ENDPOINT = "https://api.smtp2go.com/v3/email/send"
SENDER = "Office automations <website@rizonetech.com>"
TO = "rizonetech@gmail.com"
TAIL_BYTES = 256 * 1024
LOG_LINES = 60


class Refused(Exception):
    pass


def key() -> str:
    """The API key from the repository's own env file, refused when it is not there; never echoed.

    The file holds only values of the right shape (`secret_store.read_all` drops any other), and nothing here reads
    the vault or starts another program: importing is the operator's explicit step, `python scripts/import-secrets.py`."""
    stored = secret_store.get(NAME, SECRETS_ROOT)
    if not stored:
        raise Refused(f"{NAME} is not in {secret_store.FOLDER}/{secret_store.FILE}; "
                      "run python scripts/import-secrets.py")
    return stored


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


def send(api_key: str, subject: str, body: str, opener=urllib.request.urlopen,
         attachments: list[tuple[str, str]] | None = None) -> str:
    """Post the email; refuse anything but one success and no failures. `attachments` are (filename, text) pairs, sent
    as plain-text files in SMTP2GO's `attachments` field (`filename`, base64 `fileblob`, `mimetype`; the API
    reference of /email/send, read 2026-11-11), for the weekly owner digest (D00 T03 §35)."""
    message = {"sender": SENDER, "to": [TO], "subject": subject, "text_body": body}
    if attachments:
        message["attachments"] = [{"filename": name, "mimetype": "text/plain",
                                   "fileblob": base64.b64encode(text.encode("utf-8")).decode("ascii")}
                                  for name, text in attachments]
    payload = json.dumps(message).encode()
    request = urllib.request.Request(ENDPOINT, data=payload, method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json", "X-Smtp2go-Api-Key": api_key})
    with opener(request, timeout=60) as response:
        data = json.loads(response.read().decode() or "{}").get("data", {})
    sent, failed = data.get("succeeded"), data.get("failed")
    if type(sent) is not int or type(failed) is not int or sent != 1 or failed != 0:  # bool is not a count
        raise Refused(f"SMTP2GO refused the send: {data.get('failures') or data.get('error') or data}")
    return data.get("email_id", "")


ACTIVITY = "https://api.smtp2go.com/v3/activity/search"


DELIVERED = "delivered"
NOT_DELIVERED = ("rejected", "hard-bounced", "soft-bounced", "bounce", "refused", "spam", "cancelled")
SETTLE_DAYS = 5  # SMTP2GO keeps 5 days of activity on its free plan; past this no evidence can come
YOUNG_MINUTES = 60  # a log can lag a send by minutes ("allow around two minutes"): younger empty answers wait


def delivery(api_key: str, subject: str, since: str, opener=urllib.request.urlopen) -> str:
    """What SMTP2GO's activity log says of the email with exactly this subject sent at or after `since` (UTC,
    ISO-8601): "sent" when it shows it delivered, "not-sent" when it shows it rejected or bounced or shows no such
    email, "pending" while it shows it only in flight (D00 T03 §53). `POST /v3/activity/search` with `search_subject`,
    `start_date` and `end_date` (developers.smtp2go.com, "View account activity", read 2026-11-12; `/email/search` is
    deprecated there). Refused when the log cannot be read."""
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = json.dumps({"start_date": since, "end_date": now, "search_subject": subject, "limit": 100}).encode()
    request = urllib.request.Request(ACTIVITY, data=payload, method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json", "X-Smtp2go-Api-Key": api_key})
    try:
        with opener(request, timeout=60) as response:
            data = json.loads(response.read().decode() or "{}").get("data")
    except (OSError, ValueError) as error:
        raise Refused(f"SMTP2GO's activity log could not be read: {error}") from None
    if not isinstance(data, dict) or not isinstance(data.get("events"), list):
        raise Refused(f"SMTP2GO's activity log answered without events: {data}")
    kinds = {str(e.get("event", "")).lower() for e in data["events"]
             if isinstance(e, dict) and e.get("subject") == subject and e.get("email_id")}
    if DELIVERED in kinds:
        return "sent"
    if kinds & set(NOT_DELIVERED):
        return "not-sent"  # rejected or bounced: a final failure, whatever came before it
    if kinds:
        return "pending"  # processed or deferred: on its way, not yet proof either way
    return "not-sent"


def settle_claims(root: str = REPO, ask=None, now=None) -> dict:
    """Reconcile every claimed, unconfirmed notice against the delivery evidence (D00 T03 §53). A claim whose digest
    SMTP2GO shows delivered is marked reported and never sent again; one it shows rejected, bounced or absent is
    released and sent again in full. One it cannot judge yet (the log unreadable, the email in flight, or absent but
    younger than YOUNG_MINUTES) is kept and asked again at the next settlement, which every scheduled task runs; only
    a claim still undecided after SETTLE_DAYS, when SMTP2GO no longer holds its evidence, is released and sent again
    marked as a possible repeat, since a lost notice is the one failure the owner cannot see. `ask(subject, since)`
    answers for SMTP2GO (default: `delivery` with this repository's key). Returns the count per outcome."""
    import datetime
    if ask is None:
        def ask(subject, since):
            return delivery(key(), subject, since)
    now = now or datetime.datetime.now(datetime.timezone.utc)
    counts = {"confirmed": 0, "released": 0, "kept": 0, "expired": 0}
    digests = {}
    for notice in claimed_notices(root):
        claim = notice["claimed"]
        digests.setdefault(claim.get("by"), (claim.get("subject"), claim.get("at"), []))[2].append(notice["id"])
    for digest, (subject, since, ids) in digests.items():
        try:
            age = now - datetime.datetime.strptime(since, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        except (TypeError, ValueError):
            age = datetime.timedelta(days=SETTLE_DAYS + 1)  # a claim with no readable time can never be settled
        try:
            answer = ask(subject, since) if subject and since else "pending"
        except Refused:
            answer = "pending"
        if answer == "not-sent" and age < datetime.timedelta(minutes=YOUNG_MINUTES):
            answer = "pending"
        if answer == "sent":
            mark_reported(ids, root)
            counts["confirmed"] += len(ids)
        elif answer == "not-sent":
            release_claim(digest, root)
            counts["released"] += len(ids)
        elif age > datetime.timedelta(days=SETTLE_DAYS):
            release_claim(digest, root)
            counts["expired"] += len(ids)
        else:
            counts["kept"] += len(ids)
    return counts

def send_failure(name: str, task: dict, outcome: dict, tail: str, opener=urllib.request.urlopen,
                 host: str | None = None) -> str:
    subject, body = message(name, task, outcome, tail, host or socket.gethostname())
    return send(key(), subject, body, opener)


# The notice queue (D00 T03 §53; decision 32: one weekly email and no other interruption). Every sender records its
# notice here and the Monday digest reports what is pending, then marks that batch reported once it was delivered.
NOTICES = os.path.join("build", "automations", "notices.jsonl")
NOTICE_LOCK = os.path.join("build", "automations", "notices.lock")
LOCK_SECONDS = 30


class _QueueLock:
    """An exclusive lock on the queue's lock file for one read-modify-write, released by the system if the holder
    dies; waiting is bounded, and a lock that cannot be had is a Refused, never an unlocked write."""

    def __init__(self, root: str):
        self.path = os.path.join(root, NOTICE_LOCK)
        self.handle = None

    def __enter__(self):
        import time
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.handle = open(self.path, "a+b")
        deadline = time.monotonic() + LOCK_SECONDS
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    self.handle.seek(0)
                    msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError:
                if time.monotonic() > deadline:
                    self.handle.close()
                    raise Refused(f"the notice queue's lock {self.path} was held for {LOCK_SECONDS} s") from None
                time.sleep(0.05)

    def __exit__(self, *exc):
        try:
            if os.name == "nt":
                import msvcrt
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()
        return False


def _read_notices(root: str) -> list[dict]:
    """Every notice in the queue, oldest first; Refused (the file left as it is) when a line does not parse."""
    path = os.path.join(root, NOTICES)
    try:
        with open(path, encoding="utf-8") as fh:
            # One record per "\n": str.splitlines() would also split at U+0085, U+2028 and U+2029, which a notice's
            # text may hold and the writer keeps (D00 T03 §53, review round 1).
            lines = [line.rstrip("\r") for line in fh.read().split("\n")]
    except FileNotFoundError:
        return []
    except (OSError, UnicodeDecodeError) as error:
        raise Refused(f"{NOTICES} cannot be read: {error}") from None
    notices = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            notice = json.loads(line)
        except ValueError:
            notice = None
        if not isinstance(notice, dict) or not isinstance(notice.get("id"), str) or "subject" not in notice:
            raise Refused(f"{NOTICES} line {number} is not a notice; the queue is left as it is")
        notices.append(notice)
    return notices


def _write_notices(root: str, notices: list[dict]) -> None:
    """The whole queue through a temporary file in its folder and os.replace, read back; a failed write leaves the
    previous file whole."""
    import tempfile
    path = os.path.join(root, NOTICES)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix="notices.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            for notice in notices:
                fh.write(json.dumps(notice, ensure_ascii=False) + "\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    if [n["id"] for n in _read_notices(root)] != [n["id"] for n in notices]:
        raise Refused(f"{NOTICES} did not read back as written")


def record_notice(sender: str, subject: str, body: str, root: str = REPO) -> str:
    """Queue a notice for the weekly digest and return its id; Refused when the queue cannot be read or written."""
    import datetime
    import uuid
    notice = {"id": uuid.uuid4().hex, "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "sender": sender, "subject": subject, "body": body, "reported": None}
    try:
        with _QueueLock(root):
            _write_notices(root, [*_read_notices(root), notice])
    except OSError as error:
        raise Refused(f"{NOTICES} could not be written: {error}") from None
    return notice["id"]


def pending_notices(root: str = REPO) -> list[dict]:
    """The notices no digest has reported or claimed yet, oldest first."""
    return [n for n in _read_notices(root) if not n.get("reported") and not n.get("claimed")]


def claimed_notices(root: str = REPO) -> list[dict]:
    """Notices a digest claimed and never confirmed: it was delivered and could not mark them, or it stopped before
    or during its send. Nothing on disk tells the two apart."""
    return [n for n in _read_notices(root) if n.get("claimed") and not n.get("reported")]


def release_unconfirmed(root: str = REPO) -> int:
    """Give every claimed, unconfirmed notice back to the queue, keeping its `attempts`, so the next digest sends it
    again, marked as possibly repeated. A notice is never lost to a digest that may not have gone out (D00 T03 §53,
    reconciliation review: of a repeat and a loss, the repeat is the one the owner can see and discard)."""
    def change(notice):
        if notice.get("claimed") and not notice.get("reported"):
            notice["claimed"] = None
            return True
        return False
    return _update(root, change)


def _update(root: str, change) -> int:
    """Apply `change(notice) -> bool` to every notice under the lock and write the queue; how many it changed."""
    try:
        with _QueueLock(root):
            notices = _read_notices(root)
            changed = sum(1 for notice in notices if change(notice))
            _write_notices(root, notices)
    except OSError as error:
        raise Refused(f"{NOTICES} could not be written: {error}") from None
    return changed


def claim_notices(ids, digest: str, root: str = REPO, subject: str | None = None) -> int:
    """Before a digest is sent, mark its batch as claimed by that digest and count the attempt, so a notice the next
    digest sends again says it may be a repeat. Refused when the queue cannot be written: then nothing may be sent."""
    import datetime
    wanted, now = set(ids), datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def change(notice):
        if notice["id"] in wanted and not notice.get("reported") and not notice.get("claimed"):
            # The digest's subject is kept with the claim, written before the send, so a later digest can ask the mail
            # service whether that email went out (D00 T03 §53, the delivery evidence).
            notice["claimed"] = {"by": digest, "at": now, "subject": subject}
            notice["attempts"] = int(notice.get("attempts") or 0) + 1
            return True
        return False
    return _update(root, change)


def release_claim(digest: str, root: str = REPO) -> int:
    """After a refused send, give the digest's claimed notices back to the queue."""
    def change(notice):
        if (notice.get("claimed") or {}).get("by") == digest and not notice.get("reported"):
            notice["claimed"] = None
            return True
        return False
    return _update(root, change)


def mark_reported(ids, root: str = REPO) -> int:
    """Mark exactly the given notices reported (a delivered digest's batch); a notice recorded after that batch was
    read keeps `reported: null`. Returns how many were marked."""
    import datetime
    wanted, now = set(ids), datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def change(notice):
        if notice["id"] in wanted and not notice.get("reported"):
            notice["reported"] = now
            return True
        return False
    return _update(root, change)


def tail_of(path: str, lines: int = LOG_LINES) -> str:
    try:
        with open(path, "rb") as fh:  # read only the end, so a huge log cannot exhaust memory
            fh.seek(0, os.SEEK_END)
            fh.seek(max(0, fh.tell() - TAIL_BYTES))
            text = fh.read().decode("utf-8", errors="replace")
    except OSError:
        return ""
    return "\n".join(text.splitlines()[-lines:]).rstrip()


def notice_main(argv, root=REPO) -> int:
    """`alert.py --notice SUBJECT BODY_FILE [--sender NAME]`: queue a notice for the weekly digest (the campaign's
    parks record theirs this way, D00 T03 §53). Exit 0 with the id, 1 when it cannot be recorded."""
    p = argparse.ArgumentParser(prog="alert.py --notice", description="Queue a notice for the weekly owner digest.")
    p.add_argument("subject")
    p.add_argument("body_file", help="a UTF-8 text file holding the notice's body")
    p.add_argument("--sender", default="campaign", help="who records it (default campaign)")
    args = p.parse_args(argv)
    try:
        with open(args.body_file, encoding="utf-8") as fh:
            body = fh.read()
        notice_id = record_notice(args.sender, args.subject, body, root)
    except (Refused, OSError, UnicodeDecodeError) as error:
        print(f"notice not recorded: {error}", file=sys.stderr)
        return 1
    print(f"notice {notice_id} recorded for the weekly digest")
    return 0


def main(argv=None, opener=urllib.request.urlopen, host=None, root=REPO) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--notice"]:
        return notice_main(argv[1:], root)
    if argv[:1] == ["--list"]:  # what the queue holds that no digest has completed: pending, then claimed
        try:
            pending, claimed = pending_notices(root), claimed_notices(root)
        except Refused as error:
            print(f"the notice queue cannot be read: {error}", file=sys.stderr)
            return 1
        for notice in pending:
            print(f"pending  {notice['at']} {notice['sender']}: {notice['subject']}")
        for notice in claimed:
            print(f"claimed by the digest of {notice['claimed']['at']}  {notice['at']} {notice['sender']}: "
                  f"{notice['subject']}")
        return 0
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("name", help="the task that failed, e.g. office-python-pin")
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
        email_id = send_failure(args.name, task, outcome, tail, opener, host)
    except (Refused, OSError, ValueError) as error:
        print(f"alert not sent: {error}", file=sys.stderr)
        return 1
    print(f"alert sent to {TO} for {args.name} (SMTP2GO email {email_id})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
