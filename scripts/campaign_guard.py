#!/usr/bin/env python3
"""The campaign run guard for process-plan: the Claude Code Stop hook and its lifecycle commands.

    python scripts/campaign_guard.py stop-hook                      (the Stop hook; reads the payload on stdin)
    python scripts/campaign_guard.py acquire --session S --phase N --run-file F --cron-id J [--scope plan|phase] [--generation G] [--handover REASON]
    python scripts/campaign_guard.py end --session S --reason closeout|park|plan-done|operator-stop|escalation|stall
    python scripts/campaign_guard.py hook-error [--session S] [--ack LINE]
    python scripts/campaign_guard.py mint-generation
    python scripts/campaign_guard.py whoami --session S --generation G
    python scripts/campaign_guard.py reset-state --session S | --expect-no-guard yes
    python scripts/campaign_guard.py pending-cancel | cancel-confirmed --cron-id J
    python scripts/campaign_guard.py reconcile --session S --jobs J1,J2
    python scripts/campaign_guard.py health --session S --jobs J1,J2
    python scripts/campaign_guard.py expiry --session S [--now ISO]

A campaign run has three parts. The guard file (`build/claude-campaign-guard.json`) names the session that owns the
run, its phase, run file, heartbeat job and run id; it is written and deleted only through this module, under an
interprocess lock. The Stop hook (`stop-hook`, wired in `.claude/settings.json`) blocks that session's end of turn
while the run is open and lets go when the run file carries this run's `## Closeout run=<id>` heading or column-0
`PARKED <UTC> run=<id>` line, when `query ready` has nothing runnable, or when the stall breaker trips after 3 blocks
with no change to the tree. The heartbeat is a `CronCreate` job inside the session (process-plan holds its prompt)
that resumes an idle run. There is no keep-alive outside the session: a session that died is resumed by the operator,
and the new session takes the guard with `acquire --handover`.

The hook fails open on a bad payload, a missing guard or any error, and records the error for the heartbeat to report
(`hook-error`). Every command takes `--root` to act on a fixture workspace instead of this repository. Ported from
Isotone's `scripts/campaign_guard.py` and `.claude/hooks/campaign-stop.ps1` (2026-10-20), with the hook in Python so
it runs the same on Windows and WSL, and without Isotone's CI repair ledger.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
END_REASONS = ("closeout", "park", "plan-done", "operator-stop", "escalation", "stall")
LOCK_WAIT = 10.0
MAX_BLOCKS_WITHOUT_PROGRESS = 3
SCOPES = ("plan", "phase")
# Claude Code stops a Stop hook at the timeout .claude/settings.json gives it (60 seconds) and treats that as a
# non-blocking error, so the hook keeps its own deadline well inside it and still has time to record a failure.
HOOK_BUDGET_SECONDS = 40.0
UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class GuardError(ValueError):
    """A refusal naming why the guard was not changed."""


def _paths(root: str) -> tuple[str, str]:
    return (os.path.join(root, "build", "claude-campaign-guard.json"),
            os.path.join(root, "build", "claude-campaign-state.json"))


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name, "")
    return int(value) if value.isdigit() else default


class _Lock:
    """An interprocess lock on the guard. Every change (acquire, re-point, handover, end, the hook's state write)
    holds it, so a read-then-replace never interleaves with another change. It is an operating-system lock on an open
    handle (`msvcrt.locking` on Windows, `flock` elsewhere): it never expires while its holder lives, the OS releases
    it when the holder dies, and the lock file itself is never deleted."""

    def __init__(self, root: str, wait: float = LOCK_WAIT):
        self.path = os.path.join(root, "build", "claude-campaign-guard.lock")
        self.wait = wait
        self.fd = None

    def _try(self) -> bool:
        if os.name == "nt":
            import msvcrt
            try:
                os.lseek(self.fd, 0, os.SEEK_SET)
                msvcrt.locking(self.fd, msvcrt.LK_NBLCK, 1)
                return True
            except OSError:
                return False
        import fcntl
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        deadline = time.monotonic() + self.wait
        while not self._try():
            if time.monotonic() >= deadline:
                os.close(self.fd)
                self.fd = None
                raise GuardError(f"the guard is locked by another change ({self.path}); retry")
            time.sleep(0.05)
        return self

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


def _write_json(path: str, doc) -> None:
    tmp = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_guard(root: str) -> dict | None:
    guard, _ = _paths(root)
    try:
        with open(guard, encoding="utf-8-sig") as fh:
            doc = json.load(fh)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as exc:
        raise GuardError(f"the guard file {guard} does not parse: {exc}")
    if not isinstance(doc, dict):
        raise GuardError(f"the guard file {guard} is not an object")
    return doc


def _read_state(root: str) -> dict:
    _, state_path = _paths(root)
    try:
        with open(state_path, encoding="utf-8-sig") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return {}
    return doc if isinstance(doc, dict) else {}


def mint_generation() -> str:
    """A fresh generation: the heartbeat prompt carries it, so a replaced job in the same session knows it is obsolete."""
    return uuid.uuid4().hex[:12]


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime(UTC_FORMAT)


def acquire(root: str, session: str, phase: int, run_file: str, cron_id: str,
            handover: str | None = None, generation: str | None = None, scope: str | None = None) -> str:
    """Write the guard for `session`. Only one session can hold it: every guard change holds the lock, so two sessions
    racing to start a run cannot both win; the owner re-points its own guard; a live guard owned by another session is
    refused unless the operator hands it over, and the handover is recorded in the guard.

    `scope` is what the run covers: `plan` (process-plan chains every ready phase) or `phase` (process-phase was asked
    for one phase), so a heartbeat resumes only what was asked for. A re-point keeps the scope unless one is given."""
    if not session or not run_file or not cron_id:
        raise GuardError("acquire needs --session, --run-file, and --cron-id")
    if os.path.isabs(run_file) or ".." in run_file.replace("\\", "/").split("/"):
        raise GuardError(f"run file {run_file!r} must be a repo-relative path inside the workspace")
    if scope is not None and scope not in SCOPES:
        raise GuardError(f"scope {scope!r} is not one of {', '.join(SCOPES)}")
    with _Lock(root):
        return _acquire_locked(root, session, phase, run_file, cron_id, handover, generation, scope)


def _acquire_locked(root: str, session: str, phase: int, run_file: str, cron_id: str,
                    handover: str | None, generation: str | None, scope: str | None) -> str:
    guard, state_path = _paths(root)
    os.makedirs(os.path.dirname(guard), exist_ok=True)
    exists = os.path.exists(guard)
    try:
        previous = read_guard(root) or {}
    except GuardError:
        previous = {}  # a torn or unreadable guard: only an operator handover may replace it (below)
    same_run = previous.get("run_file") == run_file and previous.get("session_id") == session
    doc = {"runner": "claude", "workspace": root.replace("\\", "/"), "phase": phase,
           "run_file": run_file, "session_id": session, "cron_id": cron_id,
           "scope": scope or (previous.get("scope") if previous.get("session_id") == session or
                              (handover and previous.get("run_file") == run_file) else None) or "plan",
           # The generation the heartbeat prompt carries, and when its job was created (the 7-day expiry counts
           # from it).
           "generation": generation or (previous.get("generation") if same_run and
                                        previous.get("cron_id") == cron_id else None) or mint_generation(),
           "job_created_at": (previous.get("job_created_at") if previous.get("cron_id") == cron_id
                              and previous.get("job_created_at") else _utc_now()),
           # A stable run identity every terminal marker must carry, so a reused run file's old markers never end
           # this run however the file is edited.
           "run_id": (previous.get("run_id") if (same_run or (handover and previous.get("run_file") == run_file))
                      and previous.get("run_id") else mint_generation())}
    what = "created"
    if exists:
        owner = str(previous.get("session_id", ""))
        if owner != session:
            if not handover:
                raise GuardError(f"the guard is live for session {owner or '<unreadable>'}; "
                                 f"refusing to take it without an operator handover (--handover REASON)")
            doc["handover_from"] = owner or "<unreadable guard>"
            doc["handover_reason"] = handover
        what = "handed over" if owner != session else "re-pointed"
    # Published whole through a temporary file and a rename, under the lock held since the read above, so neither a
    # reader nor a crash ever sees a torn guard and no other change lands in between.
    _write_json(guard, doc)
    if what != "re-pointed" or not same_run:
        try:
            os.unlink(state_path)  # a fresh or handed-over run starts a fresh breaker
        except FileNotFoundError:
            pass
    return (f"acquire: guard {what} for session {session} (phase {phase}, scope {doc['scope']}, {run_file}, "
            f"job {cron_id}, generation {doc['generation']}, run {doc['run_id']})")


def ready_rows(root: str, timeout: float = 300.0, phase: int | None = None) -> tuple[int | None, str]:
    """How many rows `query ready` offers, and the first one, or (None, "") when the query cannot be read.

    The SDK's todo-graph prints a JSON list of ready rows; a graph that prints a `N runnable now` summary (Isotone's)
    is read by that line instead. With `phase`, only that phase's rows count. The text summary does not say which
    phase a row is in, so for a phase it is unknown (None, ""): a phase run then ends on its own closeout or park
    marker, never on another phase's count, and is never pointed at another phase's row.
    """
    try:
        proc = subprocess.run([sys.executable, os.path.join(root, "scripts", "todo-graph.py"), "query", "ready"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=root,
                              timeout=max(timeout, 1.0))
    except (OSError, subprocess.TimeoutExpired):
        return None, ""
    if proc.returncode != 0:
        return None, ""
    out = proc.stdout.strip()
    try:
        rows = json.loads(out)
    except ValueError:
        rows = None
    if isinstance(rows, list):
        if phase is not None:  # a phase-scoped run: only that phase's rows (the JSON rows name their phase)
            rows = [r for r in rows if isinstance(r, dict) and r.get("phase") == phase]
        first = rows[0] if rows else {}
        label = f"{first.get('ref', '')}  {first.get('title', '')}".strip() if isinstance(first, dict) else ""
        return len(rows), label
    counts = re.findall(r"(\d+) runnable now", out)
    if not counts or phase is not None:
        return None, ""
    lines = [ln.strip() for ln in out.splitlines() if ln.strip() and "runnable now" not in ln]
    return int(counts[-1]), (lines[0] if lines else "")


def marker_run(line: str) -> str | None:
    m = re.search(r"\brun=([0-9a-f]{6,})\b", line)
    return m.group(1) if m else None


def _run_markers_text(root: str, run_rel: str, guard: dict) -> str:
    """The run file's lines that count as this run's markers: every line when the guard has no run id, else only
    `## Closeout` and `PARKED` lines carrying `run=<this run's id>`, wherever they sit in the file."""
    try:
        with open(os.path.join(root, run_rel), encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return ""
    run_id = guard.get("run_id")
    if not run_id:
        return text
    keep = [ln for ln in text.splitlines()
            if not re.match(r"\A(## Closeout\b|PARKED\b)", ln) or marker_run(ln) == run_id]
    return "\n".join(keep)


def end(root: str, session: str, reason: str) -> str:
    """End the run on one of its end paths: check the path's marker, then delete the guard file and the state file.
    The heartbeat job lives in the session, not on disk, so the caller deletes it (`CronDelete`) and the returned line
    names it."""
    if reason not in END_REASONS:
        raise GuardError(f"reason {reason!r} is not one of {', '.join(END_REASONS)}")
    if not session:
        raise GuardError("end needs --session (the session that owns the guard)")
    # The plan query runs before the lock, so no subprocess is ever held under it.
    ready = ready_rows(root)[0] if reason == "plan-done" else None
    with _Lock(root):
        return _end_locked(root, session, reason, ready)


def _end_locked(root: str, session: str, reason: str, ready: int | None) -> str:
    guard_path, state_path = _paths(root)
    guard = read_guard(root)
    if guard is None:
        raise GuardError("no guard file: the run is already over")
    if str(guard.get("session_id", "")) != session:
        raise GuardError(f"the guard belongs to session {guard.get('session_id')}, not {session}")
    run_rel = str(guard.get("run_file", ""))
    text = _run_markers_text(root, run_rel, guard)
    rid = guard.get("run_id")
    tag = f" run={rid}" if rid else ""
    if reason == "closeout" and not re.search(r"(?m)^## Closeout\b", text):
        raise GuardError(f"closeout needs a '## Closeout{tag}' heading in {run_rel}")
    if reason == "park" and not re.search(r"(?m)^PARKED\b", text):
        raise GuardError(f"park needs a column-0 'PARKED <UTC>{tag} <reason>' line in {run_rel}")
    if reason == "escalation" and not re.search(r"(?m)^PARKED\b.*\bescalation:", text):
        raise GuardError(f"escalation needs a column-0 'PARKED <UTC>{tag} escalation: <cause>' line in {run_rel}")
    if reason == "plan-done" and ready != 0:
        raise GuardError(f"plan-done needs nothing runnable; query ready reads {ready}")
    if reason == "stall":
        try:
            trips = int(_read_state(root).get("trips", 0))
        except (TypeError, ValueError):
            trips = 0
        if trips < 2:
            raise GuardError(f"stall needs a state file with trips of 2 or more; it reads {trips}")
    # The job id outlives the guard until CronDelete is confirmed, so a failed delete stays recoverable, and a later
    # end never overwrites an earlier unconfirmed cancellation.
    jobs = [j for j in _pending_jobs(root) if j.get("cron_id") != guard.get("cron_id")]
    jobs.append({"cron_id": guard.get("cron_id"), "reason": reason, "at": _utc_now()})
    _write_json(_pending_path(root), jobs)
    for path in (guard_path, state_path):
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
    left = [p for p in (guard_path, state_path) if os.path.exists(p)]
    if left:
        raise GuardError(f"could not delete {', '.join(left)}")
    return (f"end: {reason}: guard and state deleted; CronDelete {guard.get('cron_id')} now "
            f"(the heartbeat job), confirm it is gone with CronList, then run "
            f"cancel-confirmed --cron-id {guard.get('cron_id')}")


def _pending_path(root: str) -> str:
    return os.path.join(root, "build", "claude-campaign-pending-cancel.json")


def _pending_jobs(root: str) -> list[dict]:
    try:
        with open(_pending_path(root), encoding="utf-8") as fh:
            doc = json.load(fh)
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        raise GuardError("the pending-cancellation record is unreadable: list the jobs with CronList and delete any "
                         "run-guard heartbeat by hand")
    if isinstance(doc, dict):
        doc = [doc]
    return [j for j in doc if isinstance(j, dict)] if isinstance(doc, list) else []


def pending_cancel(root: str) -> str:
    try:
        jobs = _pending_jobs(root)
    except GuardError as exc:
        return f"pending-cancel: {exc}"
    return "\n".join(f"pending-cancel: CronDelete {j.get('cron_id')} (ended by {j.get('reason')} at {j.get('at')})"
                     for j in jobs)


def cancel_confirmed(root: str, cron_id: str) -> str:
    with _Lock(root):
        jobs = _pending_jobs(root)
        if not jobs:
            return "cancel-confirmed: nothing pending"
        if cron_id not in [str(j.get("cron_id")) for j in jobs]:
            raise GuardError(f"no pending cancellation names job {cron_id} "
                             f"(pending: {', '.join(str(j.get('cron_id')) for j in jobs)})")
        rest = [j for j in jobs if str(j.get("cron_id")) != cron_id]
        if rest:
            _write_json(_pending_path(root), rest)
            return (f"cancel-confirmed: job {cron_id} is gone; still pending: "
                    f"{', '.join(str(j.get('cron_id')) for j in rest)}")
        os.unlink(_pending_path(root))
        return f"cancel-confirmed: job {cron_id} is gone; nothing pending"


def whoami(root: str, session: str, generation: str | None = None) -> str:
    """What this heartbeat is to the run: OWNER, NOT THE OWNER, NOT THE CURRENT JOB (a replaced job in the owning
    session), NO GUARD, or MALFORMED GUARD."""
    with _Lock(root):
        try:
            guard = read_guard(root)
        except GuardError:
            return "MALFORMED GUARD"
    if guard is None:
        return "NO GUARD"
    if str(guard.get("session_id", "")) != session:
        return "NOT THE OWNER"
    if generation and str(guard.get("generation", "")) != generation:
        return "NOT THE CURRENT JOB"
    # The run id rides the answer, so the heartbeat reads which markers are this run's.
    scope = guard.get("scope") or "plan"
    return f"OWNER run={guard.get('run_id')} scope={scope}" if guard.get("run_id") else f"OWNER scope={scope}"


def reset_state(root: str, session: str | None = None, expect_no_guard: bool = False) -> str:
    """Delete the breaker state under the lock, re-checking ownership or absence first: never a direct delete."""
    _, state_path = _paths(root)
    with _Lock(root):
        try:
            guard = read_guard(root)
        except GuardError:
            raise GuardError("the guard is unreadable; refusing to reset its state")
        if expect_no_guard and guard is not None:
            raise GuardError("a guard exists: a new run started; its state is not this heartbeat's to delete")
        if not expect_no_guard and (guard is None or str(guard.get("session_id", "")) != session):
            raise GuardError("reset-state needs the owning --session of a live guard")
        try:
            os.unlink(state_path)
            return "reset-state: state deleted"
        except FileNotFoundError:
            return "reset-state: no state"


def reconcile(root: str, session: str, jobs: list[str]) -> list[str]:
    """Startup reconciliation between the guard and the live heartbeat jobs: what to delete or recreate before a run
    starts."""
    with _Lock(root):
        try:
            guard = read_guard(root)
        except GuardError:
            return ["reconcile: the guard is unreadable: report it to the operator and start nothing"]
    out: list[str] = []
    try:
        out += [f"reconcile: a pending cancellation is unconfirmed: CronDelete {j.get('cron_id')}, then cancel-confirmed"
                for j in _pending_jobs(root)]
    except GuardError as exc:
        out.append(f"reconcile: {exc}")
    if guard is None:
        out += [f"reconcile: orphan job {j} has no guard: CronDelete it" for j in jobs]
        return out or ["reconcile: consistent (no guard, no job)"]
    owner, job = str(guard.get("session_id", "")), str(guard.get("cron_id", ""))
    if owner != session:
        return [f"reconcile: the guard belongs to session {owner}: start nothing and report the owner"]
    if job not in jobs:
        out.append(f"reconcile: the guard names job {job}, which is not live: CronCreate a heartbeat "
                   f"and re-point with acquire --cron-id")
    out += [f"reconcile: stale job {j} is not the guard's: CronDelete it" for j in jobs if j != job]
    return out or [f"reconcile: consistent (guard and job {job})"]


def health(root: str, session: str, jobs: list[str]) -> tuple[int, str]:
    with _Lock(root):
        try:
            guard = read_guard(root)
        except GuardError:
            return 1, "health: the guard is unreadable"
    if guard is None or str(guard.get("session_id", "")) != session:
        return 1, "health: this session holds no live guard"
    job = str(guard.get("cron_id", ""))
    if job not in jobs:
        return 1, f"health: job {job} is missing: CronCreate a heartbeat and re-point with acquire --cron-id"
    return 0, f"health: ok, job {job} is live"


def expiry(root: str, session: str, now: str | None = None, days: float = 7.0,
           margin_hours: float = 12.0) -> tuple[int, str]:
    """Whether the heartbeat job nears its 7-day expiry: exit 1 `replace due` inside the margin, else how long is left."""
    with _Lock(root):
        try:
            guard = read_guard(root)
        except GuardError:
            return 1, "expiry: the guard is unreadable"
    if guard is None or str(guard.get("session_id", "")) != session:
        return 1, "expiry: this session holds no live guard"
    try:
        created = datetime.datetime.strptime(str(guard.get("job_created_at")), UTC_FORMAT)
    except ValueError:
        return 1, "expiry: the job's creation time is unknown: replace the job"
    current = (datetime.datetime.strptime(now, UTC_FORMAT) if now else
               datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0, tzinfo=None))
    left = datetime.timedelta(days=days) - (current - created)
    if left <= datetime.timedelta(hours=margin_hours):
        return 1, (f"expiry: replace due, job {guard.get('cron_id')} created {guard.get('job_created_at')} "
                   f"expires in {max(left.total_seconds(), 0) / 3600:.1f}h: CronCreate a replacement and re-point")
    return 0, f"expiry: ok, job {guard.get('cron_id')} expires in {left.total_seconds() / 3600:.1f}h"


def _hook_errors_dir(root: str) -> str:
    return os.path.join(root, "build", "claude-campaign-hook-errors")


def hook_error(root: str, session: str | None = None, ack: str | None = None) -> str:
    """Print the error the hook recorded, if any, and clear it on its exact `--ack`. With a session, a guard owned by
    another session is refused before anything is read or cleared, so a former owner's heartbeat never consumes the
    current owner's failure record."""
    with _Lock(root):
        unreadable = False
        if session:
            try:
                guard = read_guard(root)
            except GuardError:
                guard, unreadable = None, True
            if guard is not None and str(guard.get("session_id", "")) != session:
                raise GuardError(f"the guard belongs to session {guard.get('session_id')}, not {session}")
        _, state_path = _paths(root)
        state = _read_state(root)
        err, at = state.get("hook_error"), state.get("hook_error_at")
        if not err:
            return _hook_error_log(root, ack)
        note = " (the guard file is unreadable: repair it before resuming)" if unreadable else ""
        line = f"campaign-stop hook failed at {at}: {err}{note}"
        if ack is None:
            return line
        if ack != line:
            raise GuardError("the acknowledgement does not match the recorded error; nothing cleared")
        state.pop("hook_error", None)
        state.pop("hook_error_at", None)
        _write_json(state_path, state)
        return f"hook-error: acknowledged and cleared: {line}"


def _hook_error_log(root: str, ack: str | None) -> str:
    """The oldest error the hook recorded without the lock: one file per error, so a writer never races this drain."""
    try:
        names = sorted(n for n in os.listdir(_hook_errors_dir(root)) if n.endswith(".txt"))
    except OSError:
        return ""
    if not names:
        return ""
    oldest = os.path.join(_hook_errors_dir(root), names[0])
    try:
        with open(oldest, encoding="utf-8", errors="replace") as fh:
            at, _, reason = fh.read().strip().partition(" ")
    except OSError:
        return ""
    line = f"campaign-stop hook failed at {at}: {reason} (recorded without the lock)"
    if ack is None:
        return line
    if ack != line:
        raise GuardError("the acknowledgement does not match the recorded error; nothing cleared")
    os.unlink(oldest)
    return f"hook-error: acknowledged and cleared: {line}"


# The Stop hook.

def _git(root: str, deadline: float, *args: str) -> bytes:
    proc = subprocess.run(["git", *args], cwd=root, capture_output=True, timeout=max(deadline - time.monotonic(), 1.0))
    return proc.stdout


def _remaining(deadline: float) -> float:
    left = deadline - time.monotonic()
    if left <= 0:
        raise GuardError("the hook ran out of its time budget before deciding")
    return left


# The guard's own files: a repository that does not ignore build/ would otherwise see every state write as progress.
OWN_FILES = re.compile(r"^build/claude-campaign-(guard|state|pending-cancel)\.json(\.[0-9]+\.tmp)?$|"
                       r"^build/claude-campaign-guard\.lock$|^build/claude-campaign-hook-errors/")


def fingerprint(root: str, run_rel: str, run_text: str, deadline: float | None = None) -> str:
    """HEAD, the working-tree diff, the untracked files, and the run file without its `- bookkeeping:` lines.

    The run file leaves the diff and the untracked set and is hashed on its own, so a heartbeat or retry note in its
    Critical events never passes for progress, while any other line still counts. Untracked content is hashed for the
    first 500 files up to 4 MB each, the next 5000 count by size and write time, and any past that by name alone, so a
    huge scratch tree cannot stall the hook and no untracked path drops out.
    """
    deadline = deadline if deadline is not None else time.monotonic() + HOOK_BUDGET_SECONDS
    max_hashed = _env_int("CAMPAIGN_HASH_FILES", 500)
    max_bytes = _env_int("CAMPAIGN_HASH_BYTES", 4 * 1024 * 1024)
    max_stat = _env_int("CAMPAIGN_STAT_FILES", 5000)
    run_path = run_rel.replace("\\", "/")
    digest = hashlib.sha256()
    digest.update(_git(root, deadline, "rev-parse", "HEAD").strip() + b"\n")
    digest.update(_git(root, deadline, "diff", "HEAD", "--", ".", f":(exclude){run_path}",
                       ":(exclude)build/claude-campaign-*") + b"\n")
    listed = _git(root, deadline, "ls-files", "-z", "--others", "--exclude-standard").decode("utf-8", "replace")
    for index, path in enumerate((p for p in listed.split("\0") if p and p != run_path and not OWN_FILES.match(p)),
                                 1):
        _remaining(deadline)
        full = os.path.join(root, path)
        try:
            info = os.stat(full)
        except OSError:
            digest.update(f"{path} missing\n".encode("utf-8"))
            continue
        if index <= max_hashed and info.st_size <= max_bytes:
            with open(full, "rb") as fh:
                digest.update(f"{path} ".encode("utf-8") + hashlib.sha256(fh.read()).hexdigest().encode() + b"\n")
        elif index <= max_hashed + max_stat:
            digest.update(f"{path} {info.st_size} {info.st_mtime_ns}\n".encode("utf-8"))
        else:
            digest.update(f"{path}\n".encode("utf-8"))
    digest.update(re.sub(r"(?m)^- bookkeeping:.*(\r?\n)?", "", run_text).encode("utf-8"))
    return digest.hexdigest()


def _same_run(still: dict | None, guard: dict) -> bool:
    return (still is not None and str(still.get("session_id", "")) == str(guard.get("session_id", ""))
            and str(still.get("run_file", "")) == str(guard.get("run_file", ""))
            and str(still.get("run_id", "")) == str(guard.get("run_id", "")))


def stop_decision(root: str, session: str) -> dict | None:
    """The hook's decision for one Stop event: None allows the stop, a dict is the `block` payload to print."""
    guard = read_guard(root)
    if guard is None or not session or str(guard.get("session_id", "")) != session:
        return None  # only the campaign session; a second session or a subagent ends its turns normally
    run_rel = str(guard.get("run_file", ""))
    if not run_rel or os.path.isabs(run_rel) or ".." in run_rel.replace("\\", "/").split("/"):
        return None
    try:
        with open(os.path.join(root, run_rel), encoding="utf-8", errors="replace") as fh:
            run_text = fh.read()
    except FileNotFoundError:
        return None
    run_id = str(guard.get("run_id") or "")
    for line in run_text.splitlines():
        if re.match(r"(## Closeout\b|PARKED\b)", line) and (not run_id or marker_run(line) == run_id):
            return None
    deadline = time.monotonic() + _env_int("CAMPAIGN_HOOK_BUDGET_SECONDS", int(HOOK_BUDGET_SECONDS))
    phase_only = guard.get("scope") == "phase"
    ready, next_row = ready_rows(root, timeout=_remaining(deadline) / 2,
                                 phase=guard.get("phase") if phase_only else None)
    if ready == 0:
        return None  # nothing runnable here: blocking cannot produce work that does not exist
    print_ = fingerprint(root, run_rel, run_text, deadline)
    _, state_path = _paths(root)
    with _Lock(root, wait=_env_int("CAMPAIGN_LOCK_WAIT_MS", 5000) / 1000):
        # A handover or an end that landed while this hook worked means the state is no longer this run's.
        try:
            still = read_guard(root)
        except GuardError:
            still = None
        if not _same_run(still, guard):
            print("campaign-stop: the guard changed while this hook waited; nothing written", file=sys.stderr)
            return None
        old = _read_state(root)
        state = {"fingerprint": str(old.get("fingerprint", "")), "blocks": int(old.get("blocks", 0) or 0),
                 "trips": int(old.get("trips", 0) or 0), "stalled": False}
        # An error the heartbeat has not acknowledged yet stays until it is (`hook-error --ack`).
        state.update({k: old[k] for k in ("hook_error", "hook_error_at") if old.get(k)})
        if state["fingerprint"] != print_:
            state.update(fingerprint=print_, blocks=0, trips=0)  # the tree moved: real progress resets the breaker
        if state["blocks"] >= MAX_BLOCKS_WITHOUT_PROGRESS:
            # Repeated pushes with no change to the tree mean the session is stuck, not idle: let it stop.
            state.update(blocks=0, trips=state["trips"] + 1, stalled=True, stalled_at=_utc_now())
            _write_json(state_path, state)
            print(f"campaign-stop: stall breaker tripped ({state['trips']}) after {MAX_BLOCKS_WITHOUT_PROGRESS} "
                  f"blocks with no tree change", file=sys.stderr)
            return None
        state["blocks"] += 1
        _write_json(state_path, state)
    tag = f" run={run_id}" if run_id else ""
    onward = (f" of Phase {guard.get('phase')} only (this run covers that phase)" if phase_only
              else ", then the next phase")
    reason = (f"Campaign run is still open ({run_rel}). Do not end the turn. Finish the open section's checklist, "
              f"run its review and stamp it, then the next section{onward}. A commit, a green suite, a "
              f"red CI (repair it) or a status report is not a stop.")
    if next_row:
        reason += f" Next ready row: {next_row}."
    reason += (f" Finished means a '## Closeout{tag}' heading or a column-0 'PARKED <UTC>{tag} <reason>' line in the "
               f"run file. Escalating to the operator ends the run first: write a column-0 'PARKED <UTC>{tag} "
               f"escalation: <cause>' line, run 'python scripts/campaign_guard.py end --session {session} --reason "
               f"escalation', CronDelete the heartbeat it names, then report. The breaker allows the stop after "
               f"{MAX_BLOCKS_WITHOUT_PROGRESS} pushes with no tree change (this is push {state['blocks']}).")
    return {"decision": "block", "reason": reason}


def _record_hook_error(root: str, guard: dict | None, reason: str) -> None:
    """Record a failure for the heartbeat: in the state file under the lock when this run still owns it, else in a
    file of its own that needs no lock. Best effort: the hook has already failed open."""
    at = _utc_now()
    try:
        with _Lock(root, wait=1.0):
            try:
                still = read_guard(root)
            except GuardError:
                still = None
            if guard is not None and _same_run(still, guard):
                state = _read_state(root)
                state.update(hook_error=reason, hook_error_at=at)
                _write_json(_paths(root)[1], state)
                return
    except (GuardError, OSError):
        pass
    folder = _hook_errors_dir(root)
    os.makedirs(folder, exist_ok=True)
    name = os.path.join(folder, f"{time.time_ns():020d}-{os.getpid()}.txt")
    with open(name + ".tmp", "w", encoding="utf-8") as fh:  # the drain lists only .txt, so it never reads a torn file
        fh.write(f"{at} {reason}")
    os.replace(name + ".tmp", name)


def stop_hook(stdin: str, project_dir: str | None) -> tuple[int, str]:
    """Run the hook on one Stop payload; returns (exit, stdout). Always exits 0: a failure allows the stop."""
    root, guard = None, None
    try:
        if not stdin.strip():
            return 0, ""
        event = json.loads(stdin)
        root = project_dir or str(event.get("cwd") or "")
        if not root:
            return 0, ""
        guard = read_guard(root)
        decision = stop_decision(root, str(event.get("session_id") or ""))
        return 0, json.dumps(decision) if decision else ""
    except Exception as error:  # fail open, but never silently: the heartbeat reports what is recorded here
        reason = f"{type(error).__name__}: {error}"
        print(f"campaign-stop: {reason}", file=sys.stderr)
        if root:
            try:
                _record_hook_error(root, guard, reason)
            except OSError:
                pass
        return 0, ""


def _opts(argv: list[str]) -> dict:
    out: dict = {}
    i = 0
    while i < len(argv):
        if not argv[i].startswith("--") or i + 1 >= len(argv):
            raise GuardError(f"bad argument {argv[i]!r}")
        out[argv[i][2:].replace("-", "_")] = argv[i + 1]
        i += 2
    return out


def main(argv: list[str]) -> int:
    if argv == ["stop-hook"]:
        code, out = stop_hook(sys.stdin.read(), os.environ.get("CLAUDE_PROJECT_DIR"))
        if out:
            print(out)
        return code
    if not argv:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    try:
        opts = _opts(argv[1:])
        root = opts.pop("root", REPO)
        if argv[0] == "acquire":
            print(acquire(root, opts.get("session", ""), int(opts.get("phase", "0")), opts.get("run_file", ""),
                          opts.get("cron_id", ""), opts.get("handover"), opts.get("generation"), opts.get("scope")))
            return 0
        if argv[0] == "end":
            print(end(root, opts.get("session", ""), opts.get("reason", "")))
            return 0
        if argv[0] == "hook-error" and set(opts) <= {"session", "ack"}:
            line = hook_error(root, opts.get("session"), opts.get("ack"))
            if line:
                print(line)
            return 0
        if argv[0] == "mint-generation" and not opts:
            print(mint_generation())
            return 0
        if argv[0] == "whoami":
            print(whoami(root, opts.get("session", ""), opts.get("generation")))
            return 0
        if argv[0] == "reset-state":
            print(reset_state(root, opts.get("session"), opts.get("expect_no_guard") == "yes"))
            return 0
        if argv[0] == "pending-cancel" and not opts:
            line = pending_cancel(root)
            if line:
                print(line)
            return 0
        if argv[0] == "cancel-confirmed":
            print(cancel_confirmed(root, opts.get("cron_id", "")))
            return 0
        if argv[0] in ("reconcile", "health"):
            jobs = [j for j in opts.get("jobs", "").split(",") if j]
            if argv[0] == "reconcile":
                print("\n".join(reconcile(root, opts.get("session", ""), jobs)))
                return 0
            code, line = health(root, opts.get("session", ""), jobs)
            print(line, file=sys.stdout if code == 0 else sys.stderr)
            return code
        if argv[0] == "expiry":
            code, line = expiry(root, opts.get("session", ""), opts.get("now"))
            print(line, file=sys.stdout if code == 0 else sys.stderr)
            return code
    except (GuardError, ValueError) as exc:
        print(f"campaign_guard: {exc}", file=sys.stderr)
        return 1
    print(f"campaign_guard: unknown command {' '.join(argv)!r}; see the module docstring", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
