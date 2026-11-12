# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The owner digest's delivery record (D00 T07 §3): what was delivered, the attempt in flight, and the lock that lets
one digest run at a time.

`build/automations/owner-digest.json` holds:

- `delivered`: the last period delivered, `{"start", "end", "token", "email_id", "at", "confirmed"}`, or null.
  `confirmed` is false for an attempt SMTP2GO's log could no longer decide (past `alert.SETTLE_DAYS`), which the next
  digest says may not have reached the owner.
- `attempt`: the digest being delivered, `{"token", "subject", "start", "end", "at", "stage"}`, or null. `stage` is
  `sending` (recorded before the send, so a run killed after it is settled by the log and never sent twice), `unsure`
  (the send may have gone out), or `failed` (it surely did not: the retry sends the period again).
- `open`: earlier attempts still `sending` or `unsure` when a later digest went out: each is settled by the log on
  its own, and one found not sent makes `missed_from` its start, so its period is reported again.
- `missed_from`: the earliest start of a period found not delivered after a later digest went out, or null; the next
  digest reaches back to it.
- `unconfirmed`: attempts the log could no longer decide (past `alert.SETTLE_DAYS`), each `{"at", "start", "end"}`:
  counted delivered, and named in the next digest that is delivered, then dropped.
- `tries`: `{local date: sends that day}`, so no day takes more than MAX_TRIES sends, across restarts.
- `due`: true from the moment a weekly run starts until its digest is sent, so a run that fails before the send (a
  notice queue that cannot be claimed, the day's sends spent) leaves the retry a digest to send.

Every write is a temporary file then a replace. Stdlib only.
"""
from __future__ import annotations

import datetime
import json
import os
import socket
import tempfile
import urllib.error

STATE = os.path.join("build", "automations", "owner-digest.json")
LOCK = os.path.join("build", "automations", "owner-digest.lock")
MAX_TRIES = 4  # sends on one local day, the weekly run's included
FIRST_DAYS = 7  # with nothing delivered yet, the first period starts this many days before the first attempt
KEYS = {"delivered", "attempt", "open", "missed_from", "unconfirmed", "tries", "due"}


class StateError(Exception):
    """The state file exists but cannot be read or does not hold a delivery record."""


def fresh() -> dict:
    return {"delivered": None, "attempt": None, "open": [], "missed_from": None, "unconfirmed": [], "tries": {},
            "due": False}


def load(root) -> dict:
    """The record; a fresh one when the file is missing (the first run); StateError when it is broken."""
    path = os.path.join(str(root), STATE)
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return fresh()
    except OSError as error:
        raise StateError(f"{STATE.replace(os.sep, '/')} cannot be read ({type(error).__name__})") from None
    except ValueError:
        raise StateError(f"{STATE.replace(os.sep, '/')} is not JSON") from None
    if (not isinstance(data, dict) or set(data) != KEYS or not isinstance(data["tries"], dict)
            or not all(isinstance(data[k], list) and all(isinstance(a, dict) for a in data[k])
                       for k in ("open", "unconfirmed"))):
        raise StateError(f"{STATE.replace(os.sep, '/')} is not a delivery record")
    for part in ("delivered", "attempt"):
        if data[part] is not None and not isinstance(data[part], dict):
            raise StateError(f"{STATE.replace(os.sep, '/')}: {part} is not an object")
    return data


def save(root, state: dict) -> None:
    """Write the record: a temporary file in its folder, then a replace. OSError when it cannot be written."""
    path = os.path.join(str(root), STATE)
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".owner-digest.", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(state, handle, indent=1, sort_keys=True)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def period_start(state: dict, today: datetime.date) -> datetime.date:
    """Where the next digest's period starts: a failed attempt's own start (kept through every retry); otherwise the
    last day of the newest period already sent or still being settled (inclusive: a receipt holds only its date, so a
    section can show twice, never not at all), else FIRST_DAYS before today; and never after `missed_from`, a period
    found not delivered after a later digest went out."""
    attempt = state["attempt"]
    if attempt and attempt["stage"] == "failed":
        start = datetime.date.fromisoformat(attempt["start"])
    else:
        ends = [datetime.date.fromisoformat(a["end"]) for a in
                [state["delivered"], attempt, *state["open"]] if a]
        start = max(ends) if ends else today - datetime.timedelta(days=FIRST_DAYS)
    if state["missed_from"]:
        start = min(start, datetime.date.fromisoformat(state["missed_from"]))
    return start


def supersede(state: dict) -> None:
    """A digest goes out while the last attempt is still being settled: that attempt joins `open`, settled on its
    own, and the new digest starts after its period."""
    if state["attempt"] and state["attempt"]["stage"] in ("sending", "unsure"):
        state["open"].append(state["attempt"])
        state["attempt"] = None

def tries_today(state: dict, today: datetime.date) -> int:
    return int(state["tries"].get(today.isoformat(), 0))


def count_try(state: dict, today: datetime.date) -> None:
    """Count a send on `today`, keeping only today's count (an earlier day's limit is spent)."""
    state["tries"] = {today.isoformat(): tries_today(state, today) + 1}


def definite(error: BaseException, refused: type) -> bool:
    """Whether a failed send surely did not go out: SMTP2GO's own refusal (`refused`, the alert module's Refused, or
    an HTTP error status it answered with), or a failure before anything was sent (the name did not resolve, the
    connection was refused). Anything else (a timeout, a reset, a cut connection, an unreadable answer) may have
    gone out after the request was sent."""
    if isinstance(error, (refused, urllib.error.HTTPError)):
        return True
    reason = error.reason if isinstance(error, urllib.error.URLError) else error
    return isinstance(reason, (socket.gaierror, ConnectionRefusedError))


def settle(state: dict, ask, now: datetime.datetime, young_minutes: int, settle_days: int, refused: type) -> list:
    """Settle every attempt in `sending` or `unsure` (the current one and the open ones) by SMTP2GO's log
    (`ask(subject, since)` is `alert.delivery`), on the rules D00 T03 §53's claims follow; the lines saying what
    happened. The record is changed in place."""
    said = []
    for attempt in [state["attempt"], *list(state["open"])]:
        if not attempt or attempt["stage"] not in ("sending", "unsure"):
            continue
        verdict, email_id = _judge(attempt, ask, now, young_minutes, settle_days, refused)
        day = attempt["at"][:10]
        current = attempt is state["attempt"]
        if verdict == "wait":
            continue
        if verdict == "sent":
            said.append(f"the digest of {day} was delivered (SMTP2GO's log)")
            if current:
                deliver(state, email_id=email_id, confirmed=True, at=attempt["at"])  # SMTP2GO's id, from its log
            else:
                state["open"].remove(attempt)
        elif verdict == "failed":
            said.append(f"the digest of {day} did not go out (SMTP2GO's log); its period is sent again")
            if current:
                attempt["stage"] = "failed"
            else:
                state["open"].remove(attempt)
                state["missed_from"] = min(filter(None, [state["missed_from"], attempt["start"]]))
        else:  # expired: no evidence can come any more; that digest itself is named in the next one
            said.append(f"the digest of {day} could not be confirmed; counted delivered, and said so")
            state["unconfirmed"].append({"at": attempt["at"], "start": attempt["start"], "end": attempt["end"]})
            if current:
                deliver(state, email_id="", confirmed=False, at=attempt["at"])
            else:
                state["open"].remove(attempt)
    return said


def _judge(attempt, ask, now, young_minutes, settle_days, refused) -> tuple:
    """(sent | failed | expired | wait, SMTP2GO's email id when the log gave one). `ask` answers the word alone or
    (word, id), as `alert.delivery` does with `with_id`."""
    at = datetime.datetime.strptime(attempt["at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    age = now - at
    since = (at - datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        answer = ask(attempt["subject"], since)
    except refused:
        answer = None  # the log cannot be read now: asked again at the next run, unless its history has passed
    answer, email_id = answer if isinstance(answer, tuple) else (answer, "")
    if answer == "sent":
        return "sent", email_id
    if answer == "not-sent":
        return "failed", email_id  # rejected or bounced: the log's own record of a failure
    if age > datetime.timedelta(days=settle_days):
        return "expired", ""  # past the log's history its silence proves nothing: an absence is not a failure
    if answer == "absent" and age > datetime.timedelta(minutes=young_minutes):
        return "failed", ""
    return "wait", ""  # pending, young and absent, or the log unreadable


def deliver(state: dict, email_id: str, confirmed: bool, at: str) -> None:
    """Move the attempt's period to `delivered` and clear the attempt; a reported period that reached back to
    `missed_from` clears it."""
    attempt = state["attempt"]
    state["delivered"] = {"start": attempt["start"], "end": attempt["end"], "token": attempt["token"],
                          "email_id": email_id, "at": at, "confirmed": confirmed}
    state["attempt"] = None
    if state["missed_from"] and attempt["start"] <= state["missed_from"]:
        state["missed_from"] = None

class Lock:
    """One digest run at a time: an operating-system lock on an open handle (`msvcrt.locking` on Windows, `flock`
    elsewhere), released by the system when its holder dies, so a killed run never leaves it held."""

    def __init__(self, root):
        self.path = os.path.join(str(root), LOCK)
        self.fd = None

    def acquire(self) -> bool:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            if os.name == "nt":
                import msvcrt
                os.lseek(self.fd, 0, os.SEEK_SET)
                msvcrt.locking(self.fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            os.close(self.fd)
            self.fd = None
            return False

    def release(self) -> None:
        if self.fd is None:
            return
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
