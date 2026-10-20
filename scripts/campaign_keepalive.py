"""The campaign keep-alive: resume an open campaign run whose owning Claude session has stopped.

    python scripts/campaign_keepalive.py observe [--session S]   record this session's Claude process
    python scripts/campaign_keepalive.py status                  what resurrect would do now, launching nothing
    python scripts/campaign_keepalive.py resurrect               resume the run's session if it is provably gone
    python scripts/campaign_keepalive.py --self-test

process-plan's heartbeat (`CronCreate`) runs inside its session, so it dies with it: a restart, a crash, or a
closed terminal leaves the guard (`build/claude-campaign-guard.json`) open with nobody working the run. The
`office-2028-claude-keepalive` task (`.conclave/automations/`, three minutes after logon and then hourly) runs
`resurrect`, which resumes that exact session headless with `claude -p --resume`, as Rizonetech's resurrect
timer does for its campaigns.

`observe` is the SessionStart hook (`.claude/settings.json`, the session id read from the hook's stdin) and
process-plan's acquire step: it records the Claude Code process of the session under
`build/claude-sessions/<session>.json` as a pid and creation time, so liveness is proven against the exact
process and never a reused pid.

Any one of these stops a launch, in this order:
- no guard: there is no open run;
- the guard's session was never observed, so its process cannot be proven gone;
- that session's recorded process is alive, or Windows will not say (access denied counts as alive);
- another observed Office-2028 session is alive, or unreadable: the operator is present, and one session owns
  the tree;
- a launch in the last 15 minutes;
- three resumes in a row that moved neither HEAD nor the run file, bookkeeping lines aside (reported once,
  then held).

While the resumed session runs, the supervisor ends its process tree the moment the guard goes away (an
operator stop or a run end), names another session (a handover), another Office-2028 session starts, the
operator resumes this same session in another process, or the supervision itself fails. Observations
older than a week are pruned, except the one the open guard names.
Every command takes `--root` to act on a fixture workspace instead of this repository.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
_spec = importlib.util.spec_from_file_location("campaign_guard", os.path.join(HERE, "campaign_guard.py"))
campaign_guard = importlib.util.module_from_spec(_spec)  # the guard file, its reader, and its lock
_spec.loader.exec_module(campaign_guard)

SESSION_ID = re.compile(r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$")
CLAUDE_EXES = ("claude.exe", "claude")
RELAUNCH_AFTER = 15 * 60
STALLED_RESUMES = 3
SUPERVISE_FOR = 4 * 3600
POLL = 30.0
NO_WINDOW = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW: a scheduled run opens no console
OBSERVED_DAYS = 7

PROMPT = ("Claude keep-alive for Office-2028: this session owns the open campaign run in "
          "build/claude-campaign-guard.json (phase {phase}, run file {run_file}, run {run_id}), and its process had "
          "stopped, so the office-2028-claude-keepalive task resumed it headless at {now}. Follow process-plan: append "
          "`- bookkeeping: keep-alive resumed {now}` to the run file's Critical events, then reconcile the heartbeat "
          "(CronList, then python scripts/campaign_guard.py reconcile). If CronCreate works here, create a fresh "
          "heartbeat and re-point the guard with acquire and its job id; if it does not, leave the guard as it is "
          "(it already names this session; the keep-alive task stands in for the heartbeat). Then continue the "
          "open phase from durable state. Every gate, review, and stop rule applies unchanged.")


class KeepAliveError(ValueError):
    """A refusal naming why nothing was recorded or launched."""


class ProcessUnknown(KeepAliveError):
    """Windows would not say whether a process is alive, so nothing may treat it as gone."""


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class WindowsProcesses:
    """Process identity from the Win32 API: the snapshot for parent links and image names, and the creation
    time, which together with the pid names one process for the life of the machine."""

    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.ctypes, self.wintypes = ctypes, wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        k32.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4

        class Entry(ctypes.Structure):
            _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                        ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                        ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                        ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long),
                        ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_wchar * 260)]

        k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
        k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
        self.k32, self.Entry = k32, Entry

    def table(self) -> dict[int, tuple[int, str]]:
        """pid -> (parent pid, image name) for every process."""
        snap = self.k32.CreateToolhelp32Snapshot(0x2, 0)
        if not snap or snap == self.ctypes.c_void_p(-1).value:
            raise OSError("CreateToolhelp32Snapshot failed")
        out: dict[int, tuple[int, str]] = {}
        entry = self.Entry()
        entry.dwSize = self.ctypes.sizeof(entry)
        try:
            ok = self.k32.Process32FirstW(snap, self.ctypes.byref(entry))
            while ok:
                out[int(entry.th32ProcessID)] = (int(entry.th32ParentProcessID), entry.szExeFile)
                ok = self.k32.Process32NextW(snap, self.ctypes.byref(entry))
        finally:
            self.k32.CloseHandle(snap)
        return out

    def created(self, pid: int) -> int | None:
        """The creation time of a running process, None only when it is proven gone (no such pid, or it has
        exited), and ProcessUnknown when Windows will not say (access denied, a failed query): a process that
        cannot be read is never taken for a dead one."""
        handle = self.k32.OpenProcess(0x1000, False, int(pid))  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            error = self.ctypes.get_last_error()
            if error == 87:  # ERROR_INVALID_PARAMETER: no process has this pid
                return None
            raise ProcessUnknown(f"cannot open process {pid} (Windows error {error})")
        try:
            code = self.wintypes.DWORD()
            if not self.k32.GetExitCodeProcess(handle, self.ctypes.byref(code)):
                raise ProcessUnknown(f"cannot read the exit state of process {pid}")
            if code.value != 259:  # not STILL_ACTIVE: it has exited
                return None
            times = [self.wintypes.FILETIME() for _ in range(4)]
            if not self.k32.GetProcessTimes(handle, *(self.ctypes.byref(t) for t in times)):
                raise ProcessUnknown(f"cannot read the creation time of process {pid}")
            return (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
        finally:
            self.k32.CloseHandle(handle)


def default_processes():
    if os.name != "nt":
        raise KeepAliveError("the keep-alive reads Windows process identity; Office-2028 campaigns run on Windows")
    return WindowsProcesses()


def identity(procs, pid: int) -> dict:
    """{pid, created, exe} of a running process, or {} when it is gone."""
    created = procs.created(pid)
    if created is None:
        return {}
    exe = procs.table().get(int(pid), (0, ""))[1]
    return {"pid": int(pid), "created": created, "exe": exe}


def alive(procs, owner: dict | None) -> bool:
    """True when the recorded process still runs; raises ProcessUnknown when Windows will not say."""
    return bool(owner) and owner.get("created") is not None and procs.created(owner.get("pid", 0)) == owner["created"]


def complete(owner) -> bool:
    """An owner record good enough to prove anything: a positive pid and a creation time."""
    pid, created = (owner.get("pid"), owner.get("created")) if isinstance(owner, dict) else (None, None)
    return (type(pid) is int and pid > 0 and type(created) is int)


def owners(rec: dict | None) -> list:
    """Every Claude process recorded for a session (older records carry only `owner`)."""
    if not isinstance(rec, dict):
        return []
    listed = rec.get("owners")
    if isinstance(listed, list):
        return listed
    return [rec["owner"]] if "owner" in rec else []


def session_alive(procs, rec: dict | None) -> bool:
    """True unless every recorded process of the session is provably gone. A record that is invalid, empty or
    incomplete proves nothing, so it counts as alive; raises ProcessUnknown when Windows will not say."""
    found = owners(rec)
    if not isinstance(rec, dict) or rec.get("invalid") or not found or not all(complete(o) for o in found):
        return True
    return any(alive(procs, o) for o in found)


def session_maybe_alive(procs, rec: dict | None) -> bool:
    try:
        return session_alive(procs, rec)
    except ProcessUnknown:
        return True


def maybe_alive(procs, owner: dict | None) -> bool:
    """alive(), with an unreadable process counted as alive: every caller that may launch or keep a second
    writer must assume the worst."""
    try:
        return alive(procs, owner)
    except ProcessUnknown:
        return True


def claude_ancestor(procs, start: int | None = None) -> dict:
    """The Claude Code process above this hook or tool subprocess."""
    table = procs.table()
    pid = os.getpid() if start is None else start
    for _ in range(16):
        parent, _exe = table.get(pid, (0, ""))
        if not parent or parent not in table:
            break
        if table[parent][1].lower() in CLAUDE_EXES:
            found = identity(procs, parent)
            if found:
                return found
            break
        pid = parent
    raise KeepAliveError("no Claude Code ancestor process: run observe from inside a Claude Code session")


def _sessions_dir(root: str) -> str:
    return os.path.join(root, "build", "claude-sessions")


def _state_path(root: str) -> str:
    return os.path.join(root, "build", "claude-keepalive.json")


def _atomic(path: str, doc: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
    os.replace(tmp, path)


def _read(path: str) -> dict:
    try:
        with open(path, encoding="utf-8-sig") as fh:
            doc = json.load(fh)
        return doc if isinstance(doc, dict) else {}
    except (OSError, ValueError):
        return {}


def observed(root: str) -> dict[str, dict]:
    """session id -> its observation record. An unreadable or mismatched record is kept as {"invalid": True},
    so it holds a launch instead of silently disappearing."""
    out = {}
    folder = _sessions_dir(root)
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if name.endswith(".json") and SESSION_ID.match(name[:-5]):
            rec = _read(os.path.join(folder, name))
            out[name[:-5]] = rec if rec.get("session") == name[:-5] else {"invalid": True, "session": name[:-5]}
    return out


class _SessionsLock:
    """Serialises observation updates: the guard's interprocess lock class on its own lock file."""

    def __init__(self, root: str):
        self.lock = campaign_guard._Lock(root)
        self.lock.path = os.path.join(root, "build", "claude-sessions.lock")

    def __enter__(self):
        os.makedirs(os.path.dirname(self.lock.path), exist_ok=True)
        return self.lock.__enter__()

    def __exit__(self, *exc):
        return self.lock.__exit__(*exc)


def _unobserved_flag(root: str, session: str) -> str:
    return os.path.join(_sessions_dir(root), f"unobserved-{session}.flag")


def unobserved(root: str) -> list[str]:
    """Sessions whose observation failed: until each observes successfully, no launch can prove the tree free."""
    folder = _sessions_dir(root)
    return sorted(n for n in os.listdir(folder) if n.startswith("unobserved-") and n.endswith(".flag")) \
        if os.path.isdir(folder) else []


def record(root: str, session: str, owner: dict, supervised: bool = False, procs=None) -> None:
    if not SESSION_ID.match(session or ""):
        raise KeepAliveError(f"session {session!r} is not a Claude Code session id")
    path = os.path.join(_sessions_dir(root), session + ".json")
    with _SessionsLock(root):  # read, merge and replace as one step, so concurrent observers lose nothing
        # Keep every process seen for this session (one session can run in several processes); a process leaves
        # the list only once it is proven gone, never to make room.
        previous = _read(path)
        if os.path.exists(path) and previous.get("session") != session:
            # Unreadable or someone else's: an unknown process may still own it, so keep an unresolved marker.
            keep = [{"pid": None, "created": None, "unresolved": "an unreadable observation was replaced"}]
        else:
            keep = [o for o in owners(previous)
                    if (o.get("pid"), o.get("created")) != (owner.get("pid"), owner.get("created"))
                    and (not complete(o) or procs is None or maybe_alive(procs, o))]
        _atomic(path, {"session": session, "owner": owner, "owners": keep + [owner], "seen_at": _now(),
                       "supervised": supervised})
        try:
            os.unlink(_unobserved_flag(root, session))
        except FileNotFoundError:
            pass


def observe(root: str, session: str, procs, start: int | None = None) -> str:
    """Record the Claude Code process of `session`, and drop week-old records of exited sessions, except the
    one the open guard names: the keep-alive needs it to prove that session gone."""
    owner = claude_ancestor(procs, start)
    record(root, session, owner, procs=procs)
    try:
        keep = str((campaign_guard.read_guard(root) or {}).get("session_id", ""))
    except campaign_guard.GuardError:
        return f"observe: session {session} is Claude process {owner['pid']} (guard unreadable, nothing pruned)"
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=OBSERVED_DAYS)
    for other, rec in observed(root).items():
        try:
            seen = datetime.datetime.strptime(rec.get("seen_at", ""), "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=datetime.timezone.utc)
        except ValueError:
            seen = cutoff
        if other not in (session, keep) and seen <= cutoff and not session_maybe_alive(procs, rec):
            with _SessionsLock(root):  # re-read under the lock: the session may have recorded itself since
                fresh = observed(root).get(other)
                if not fresh or fresh.get("seen_at") != rec.get("seen_at") or session_maybe_alive(procs, fresh):
                    continue
                try:
                    os.unlink(os.path.join(_sessions_dir(root), other + ".json"))
                except FileNotFoundError:
                    pass  # another session's observe pruned it first
    return f"observe: session {session} is Claude process {owner['pid']}"


def _fingerprint(root: str, guard: dict) -> str:
    """HEAD plus a hash of the run file without its bookkeeping lines: the line every resume is told to
    append is not progress, or a session that only records its own resume would never count as stalled."""
    import hashlib
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True,
                              timeout=30, creationflags=NO_WINDOW).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        head = ""
    try:
        with open(os.path.join(root, guard.get("run_file", "")), encoding="utf-8", errors="replace") as fh:
            body = "".join(line for line in fh if not line.lstrip().startswith("- bookkeeping:"))
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    except OSError:
        digest = "no-run-file"
    return f"{head}:{digest}"


def decide(root: str, procs, clock=time.time) -> tuple[str, dict | None, str]:
    """('launch' | 'hold' | 'report', guard, why) without launching anything."""
    guard = campaign_guard.read_guard(root)
    if not guard:
        return "hold", None, "idle: no open campaign run"
    session = str(guard.get("session_id", ""))
    if guard.get("runner", "claude") != "claude":
        return "hold", guard, f"held: a {guard.get('runner')} run owns the tree; only Claude runs are resumed"
    if not SESSION_ID.match(session):
        return "report", guard, f"the guard names {session!r}, not a Claude Code session id; repair the guard"
    sessions = observed(root)
    failed = unobserved(root)
    if failed:
        return "hold", guard, (f"held: a session's observation failed ({failed[0]}), so the tree cannot be proven "
                               "free; it clears when that session observes again, or remove it once it has ended")
    rec = sessions.get(session)
    if not rec:
        return "hold", guard, (f"held: session {session} was never observed, so its process cannot be proven gone "
                               "(start the campaign in a session with the SessionStart hook, or run observe in it)")
    if rec.get("invalid") or not owners(rec) or not all(complete(o) for o in owners(rec)):
        return "hold", guard, (f"held: the observation of session {session} is unreadable or incomplete, so its "
                               "process cannot be proven gone (repair or remove build/claude-sessions/" f"{session}.json)")
    try:
        owner_alive = session_alive(procs, rec)
    except ProcessUnknown as exc:
        return "hold", guard, f"held: cannot tell whether session {session} is alive ({exc})"
    if owner_alive:
        return "hold", guard, f"held: session {session} is alive (Claude process {rec['owner'].get('pid')})"
    present = [s for s, r in sessions.items() if s != session and session_maybe_alive(procs, r)]
    if present:
        return "hold", guard, f"held: attended, Office-2028 session {present[0]} is alive; one session owns the tree"
    state = _read(_state_path(root))
    if clock() - float(state.get("launched_at", 0)) < RELAUNCH_AFTER:
        return "hold", guard, "held: a resume launched less than 15 minutes ago"
    same_run = state.get("run_id") == guard.get("run_id")
    # The first resume stores stalled 0 and each unchanged one adds 1, so STALLED_RESUMES resumes without progress
    # leave stalled at STALLED_RESUMES - 1: that is the limit, never one resume more.
    if (same_run and state.get("stalled", 0) >= STALLED_RESUMES - 1
            and state.get("fingerprint") == _fingerprint(root, guard)):
        if state.get("reported") == state.get("fingerprint"):
            return "hold", guard, "held: still stopped after resumes without progress (reported)"
        return "report", guard, (f"stopped: {STALLED_RESUMES} resumes of run {guard.get('run_id')} moved neither HEAD "
                                 "nor the run file; end the run with campaign_guard.py end, or resume it by hand")
    return "launch", guard, f"launch: session {session} has stopped with run {guard.get('run_id')} open"


def writer_model(root: str) -> str:
    import tomllib
    # Office-2028 has no review panel file; the writer model the keep-alive resumes with lives here.
    with open(os.path.join(root, ".conclave", "keepalive.toml"), "rb") as fh:
        model = tomllib.load(fh)["writer"]["model"]
    if not isinstance(model, str) or not model.strip():
        raise ValueError(f"[writer] model must be a non-empty string, not {model!r}")
    return model.strip()


def resume_command(claude: str, guard: dict, model: str) -> list[str]:
    prompt = PROMPT.format(phase=guard.get("phase"), run_file=guard.get("run_file"), run_id=guard.get("run_id"),
                           now=_now())
    return [claude, "-p", "--resume", guard["session_id"], "--model", model, "--permission-mode",
            "bypassPermissions", prompt]


def _launch(argv: list[str], root: str, log_path: str):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    flags = 0x08000000 | 0x00000200 if os.name == "nt" else 0  # CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
    with open(log_path, "ab") as log:
        return subprocess.Popen(argv, cwd=root, stdout=log, stderr=log, stdin=subprocess.DEVNULL,
                                creationflags=flags)


def _kill_tree(child) -> None:
    if os.name == "nt" and getattr(child, "pid", None):
        subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"], capture_output=True, timeout=60,
                       creationflags=NO_WINDOW)
    else:
        child.kill()
    try:
        child.wait(timeout=30)
    except subprocess.TimeoutExpired:
        raise KeepAliveError(f"the resumed session (process {child.pid}) did not end after taskkill") from None


class _LaunchLock:
    """Held for the whole resurrect, so a tick that fires while a resume is supervised does nothing."""

    def __init__(self, root: str):
        self.path = os.path.join(root, "build", "claude-keepalive.lock")
        self.fd = None

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(self.fd)
            self.fd = None
            return False
        return True

    def __exit__(self, *exc):
        if self.fd is not None:
            if os.name == "nt":
                import msvcrt
                os.lseek(self.fd, 0, os.SEEK_SET)
                msvcrt.locking(self.fd, msvcrt.LK_UNLCK, 1)
            os.close(self.fd)
        return False


def _supervise(root: str, procs, child, session: str, clock, sleep, poll: float, limit: float,
               killer) -> tuple[int | None, str | None]:
    """Wait for the resumed session; end it the moment it would no longer be the only writer.
    Returns (exit code, why it was ended or None)."""
    owner = identity(procs, child.pid)
    previous = (observed(root).get(session) or {}).get("owner") or {}
    # An operator resume that recorded itself between the launch and here must stay visible, or the loop
    # below could never see it: the child takes the record only from a dead owner or from itself.
    if owner and (previous.get("pid") == child.pid or not maybe_alive(procs, previous)):
        record(root, session, owner, supervised=True, procs=procs)
    deadline = clock() + limit
    while True:
        code = child.poll()
        if code is not None:
            return code, None
        ended = None
        current = campaign_guard.read_guard(root)
        sessions = observed(root)
        mine = sessions.get(session)
        live_other = [o for o in owners(mine) if complete(o) and o.get("pid") != child.pid
                      and maybe_alive(procs, o)]
        if not current or str(current.get("session_id", "")) != session:
            ended = "the guard was ended or handed to another session"
        elif (not isinstance(mine, dict) or mine.get("invalid") or not owners(mine)
              or not all(complete(o) for o in owners(mine))):
            ended = f"the observation of session {session} became unreadable, so no other writer can be ruled out"
        elif unobserved(root):
            ended = f"a session's observation failed ({unobserved(root)[0]}), so no other writer can be ruled out"
        elif live_other:
            ended = f"the operator resumed session {session} in Claude process {live_other[0]['pid']}"
        else:
            others = [s for s, r in sessions.items() if s != session and session_maybe_alive(procs, r)]
            if others:
                ended = f"Office-2028 session {others[0]} started, and one session owns the tree"
        if not ended and clock() >= deadline:
            ended = f"the resume ran past {int(limit // 3600)}h"
        if ended:
            killer(child)
            return child.poll(), ended
        sleep(poll)


def resurrect(root: str, procs, launcher=_launch, killer=_kill_tree, clock=time.time, sleep=time.sleep,
              claude: str | None = None, poll: float = POLL, limit: float = SUPERVISE_FOR) -> tuple[int, str]:
    """Resume the run's session when it is provably gone, and supervise it. Returns (exit code, report)."""
    with _LaunchLock(root) as locked:
        if not locked:
            return 0, "held: another keep-alive is supervising a resume"
        action, guard, why = decide(root, procs, clock)
        state_path = _state_path(root)
        state = _read(state_path)
        if action == "report":
            if guard and guard.get("run_id") == state.get("run_id"):
                state["reported"] = state.get("fingerprint")
                _atomic(state_path, state)
            return 1, why
        if action == "hold":
            return 0, why
        claude = claude or shutil.which("claude")
        if not claude:
            return 1, "no claude executable on PATH; the keep-alive cannot resume the run"
        try:  # read before any state changes, so a setup gap never counts as a resume
            model = writer_model(root)
        except (OSError, KeyError, TypeError, ValueError) as error:
            return 1, f"setup required: .conclave/keepalive.toml must name [writer] model ({error})"
        session = guard["session_id"]
        fingerprint = _fingerprint(root, guard)
        same = state.get("run_id") == guard.get("run_id") and state.get("fingerprint") == fingerprint
        state = {"run_id": guard.get("run_id"), "session": session, "launched_at": clock(),
                 "resumes": (state.get("resumes", 0) if state.get("run_id") == guard.get("run_id") else 0) + 1,
                 "stalled": (state.get("stalled", 0) + 1) if same else 0, "fingerprint": fingerprint}
        action_now, guard_now, why_now = decide(root, procs, clock)
        if action_now != "launch" or (guard_now or {}).get("run_id") != guard.get("run_id"):
            return 0, f"held at launch: the situation changed while preparing ({why_now})"
        stamp = _now().replace(":", "")
        log = os.path.join(root, "build", "claude-keepalive", f"{guard.get('run_id')}-{stamp}.log")
        try:
            child = launcher(resume_command(claude, guard, model), root, log)
        except OSError as error:  # nothing started, so nothing is counted against the resume budget
            return 1, f"could not start claude to resume session {session}: {error}"
        try:
            _atomic(state_path, state)  # inside the boundary: a failed write must not leave the child unsupervised
            code, ended = _supervise(root, procs, child, session, clock, sleep, poll, limit, killer)
        except BaseException:
            # Whatever broke the supervision (an unreadable guard, a failed probe, an interrupt), the resumed
            # session must not outlive it, or no stop, attended session, or deadline would reach it.
            if child.poll() is None:
                killer(child)
            raise
        state.update(last_exit=code, ended=ended, finished_at=_now())
        _atomic(state_path, state)
        if ended and "past" in ended:
            return 1, f"resumed session {session}, then stopped it: {ended} (log {os.path.relpath(log, root)})"
        if ended:
            return 0, f"resumed session {session}, then stopped it: {ended}"
        if code:
            return 1, f"resumed session {session} exited {code} (log {os.path.relpath(log, root)})"
        return 0, f"resumed session {session}; it released its turn (exit 0, log {os.path.relpath(log, root)})"


# ---------------------------------------------------------------- self-test

class _FakeProcs:
    def __init__(self):
        self.procs: dict[int, tuple[int, str, int]] = {}  # pid -> (parent, exe, created)
        self.unknown: set[int] = set()  # pids Windows refuses to describe

    def add(self, pid: int, parent: int, exe: str, created: int) -> dict:
        self.procs[pid] = (parent, exe, created)
        return {"pid": pid, "created": created, "exe": exe}

    def table(self):
        return {pid: (p, exe) for pid, (p, exe, _c) in self.procs.items()}

    def created(self, pid):
        if int(pid) in self.unknown:
            raise ProcessUnknown(f"cannot open process {pid} (Windows error 5)")
        entry = self.procs.get(int(pid))
        return entry[2] if entry else None


class _FakeChild:
    def __init__(self, pid: int, exits_after: int | None, code: int = 0):
        self.pid, self.polls, self.exits_after, self.code, self.killed = pid, 0, exits_after, code, False

    def poll(self):
        if self.killed:
            return -9
        self.polls += 1
        return self.code if self.exits_after is not None and self.polls > self.exits_after else None


def _forget(root: str) -> None:
    try:
        os.remove(_state_path(root))
    except FileNotFoundError:
        pass  # no resume recorded since the last case


def _self_test() -> int:
    failed = 0

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal failed
        if not ok:
            failed += 1
            print(f"FAIL {name}: {detail}")

    s_run, s_other = "11111111-2222-3333-4444-555555555555", "66666666-7777-8888-9999-000000000000"
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "ws")
        os.makedirs(os.path.join(root, ".conclave"))
        with open(os.path.join(root, ".conclave", "keepalive.toml"), "w", encoding="utf-8") as fh:
            fh.write('[writer]\nmodel = "claude-opus-5-5"\n')
        subprocess.run(["git", "init", "-q", root], check=True)
        procs = _FakeProcs()
        clock = [1_000_000.0]
        launched: list[list[str]] = []
        children: list[_FakeChild] = []

        def launcher(exits_after=1, code=0, pid=900):
            def go(argv, _root, _log):
                launched.append(argv)
                child = _FakeChild(pid, exits_after, code)
                procs.add(pid, 1, "claude.exe", 9000 + len(launched))
                children.append(child)
                return child
            return go

        def run(**kw):
            kw.setdefault("launcher", launcher())
            return resurrect(root, procs, killer=lambda c: setattr(c, "killed", True), clock=lambda: clock[0],
                             sleep=lambda _s: clock.__setitem__(0, clock[0] + 30), claude="claude", poll=30,
                             **kw)

        code, msg = run()
        check("no guard is idle", code == 0 and msg.startswith("idle") and not launched, msg)

        campaign_guard.acquire(root, "codex-run", 4, "docs/phase-runs/run.md", campaign_guard.NO_JOB, runner="codex")
        code, msg = run()
        check("another runner's guard is held, never reported or resumed",
              code == 0 and "codex run owns the tree" in msg and not launched, msg)
        campaign_guard.end(root, "codex-run", "operator-stop")

        campaign_guard.acquire(root, s_run, 4, "docs/phase-runs/run.md", "job1")
        code, msg = run()
        check("an unobserved owner is held", code == 0 and "never observed" in msg and not launched, msg)

        owner = procs.add(500, 1, "claude.exe", 111)
        procs.add(501, 500, "bash.exe", 112)
        procs.add(502, 501, "python.exe", 113)
        check("claude_ancestor walks to claude.exe", claude_ancestor(procs, 502) == owner, str(claude_ancestor(procs, 502)))
        try:
            claude_ancestor(procs, 1)
            check("no ancestor refuses", False)
        except KeepAliveError:
            pass
        try:
            record(root, "../../evil", owner)
            check("a bad session id is refused", False)
        except KeepAliveError:
            pass
        record(root, s_run, owner)
        code, msg = run()
        check("a live owner is held", code == 0 and "is alive" in msg and not launched, msg)

        procs.procs[500] = (1, "claude.exe", 999)  # pid reused by another process: the owner is gone
        attended = procs.add(600, 1, "claude.exe", 222)
        record(root, s_other, attended)
        code, msg = run()
        check("an attended session holds the launch", code == 0 and "attended" in msg and not launched, msg)

        del procs.procs[600]
        second = procs.add(650, 1, "claude.exe", 333)  # the same session open in a second process
        record(root, s_run, second)
        code, msg = run()
        check("a session alive in a second process is held", code == 0 and "is alive" in msg and not launched, msg)
        del procs.procs[650]
        sess_file = os.path.join(_sessions_dir(root), s_run + ".json")
        saved = open(sess_file, encoding="utf-8").read()
        with open(sess_file, "w", encoding="utf-8") as fh:
            json.dump({"session": s_run}, fh)
        code, msg = run()
        check("an incomplete observation holds the launch", code == 0 and "incomplete" in msg and not launched, msg)
        bogus = os.path.join(_sessions_dir(root), s_other + ".json")
        with open(bogus, "w", encoding="utf-8") as fh:
            fh.write("{not json")
        with open(sess_file, "w", encoding="utf-8") as fh:
            fh.write(saved)
        code, msg = run()
        check("an unreadable other observation holds the launch", code == 0 and not launched, msg)
        os.remove(bogus)
        with open(sess_file, encoding="utf-8") as fh:
            doc = json.load(fh)
        doc["owners"] = [dict(o, created=str(o["created"])) for o in doc["owners"]]
        with open(sess_file, "w", encoding="utf-8") as fh:
            json.dump(doc, fh)
        code, msg = run()
        check("a text creation time proves nothing and holds", code == 0 and "incomplete" in msg and not launched, msg)
        with open(sess_file, "w", encoding="utf-8") as fh:
            fh.write(saved)
        first = procs.add(660, 1, "claude.exe", 444)
        record(root, s_run, first, procs=procs)
        for k in range(9):
            procs.add(670 + k, 1, "claude.exe", 500 + k)
            record(root, s_run, procs.procs and {"pid": 670 + k, "created": 500 + k, "exe": "claude.exe"}, procs=procs)
        for k in range(9):
            del procs.procs[670 + k]
        code, msg = run()
        check("an early live owner survives many later observations", code == 0 and "is alive" in msg
              and not launched, msg)
        del procs.procs[660]
        with open(sess_file, "w", encoding="utf-8") as fh:
            fh.write(saved)
        flag = _unobserved_flag(root, s_other)
        with open(flag, "w", encoding="utf-8") as fh:
            fh.write("failed" + chr(10))
        code, msg = run()
        check("a failed observation holds every launch", code == 0 and "observation failed" in msg and not launched, msg)
        os.remove(flag)
        state_before = open(_state_path(root), encoding="utf-8").read() if os.path.exists(_state_path(root)) else None

        def cannot_start(argv, r, log):
            raise OSError("claude.exe missing")
        code, msg = run(launcher=cannot_start)
        state_after = open(_state_path(root), encoding="utf-8").read() if os.path.exists(_state_path(root)) else None
        check("a launch that cannot start counts no resume", code == 1 and "could not start" in msg
              and state_before == state_after and not launched, msg)
        with open(sess_file, "w", encoding="utf-8") as fh:
            json.dump({"session": s_run, "owner": {"pid": 680}, "owners": [{"pid": 680}]}, fh)
        resumed = procs.add(681, 1, "claude.exe", 777)
        record(root, s_run, resumed, procs=procs)
        del procs.procs[681]
        code, msg = run()
        check("an unknown earlier owner survives a later observation", code == 0 and "incomplete" in msg
              and not launched, msg)
        with open(sess_file, "w", encoding="utf-8") as fh:
            fh.write(saved)
        conf = os.path.join(root, ".conclave", "keepalive.toml")
        for bad in ("123", '""', '"   "'):
            with open(conf, "w", encoding="utf-8") as fh:
                fh.write("[writer]" + chr(10) + "model = " + bad + chr(10))
            code, msg = run()
            check(f"an invalid writer model {bad} is a setup refusal", code == 1 and "setup required" in msg
                  and not launched, msg)
        with open(conf, "w", encoding="utf-8") as fh:
            fh.write("[writer]" + chr(10) + 'model = "claude-opus-5-5"' + chr(10))
        os.replace(conf, conf + ".away")
        state_file = os.path.join(root, "build", "claude-keepalive.json")
        before = open(state_file, encoding="utf-8").read() if os.path.exists(state_file) else None
        code, msg = run()
        after = open(state_file, encoding="utf-8").read() if os.path.exists(state_file) else None
        check("a missing writer model is a setup refusal that counts no resume",
              code == 1 and "setup required" in msg and not launched and before == after, msg)
        os.replace(conf + ".away", conf)
        code, msg = run()
        argv = launched[-1] if launched else []
        check("a gone owner is resumed", code == 0 and len(launched) == 1 and "released its turn" in msg, msg)
        check("the resume names the session, the writer model, and bypass",
              argv[:8] == ["claude", "-p", "--resume", s_run, "--model", "claude-opus-5-5", "--permission-mode",
                           "bypassPermissions"] and "keep-alive resumed" in argv[8], str(argv[:8]))
        rec = observed(root)[s_run]
        check("the resumed process is recorded as the owner", rec["owner"]["pid"] == 900 and rec["supervised"], str(rec))

        del procs.procs[900]
        code, msg = run()
        check("a relaunch within 15 minutes is held", code == 0 and "15 minutes" in msg and len(launched) == 1, msg)

        for _ in range(STALLED_RESUMES - 1):  # the first resume above plus these makes STALLED_RESUMES in all
            clock[0] += RELAUNCH_AFTER + 1
            procs.procs.pop(900, None)
            run()
        clock[0] += RELAUNCH_AFTER + 1
        procs.procs.pop(900, None)
        before = len(launched)
        code, msg = run()
        state = _read(_state_path(root))
        check("three resumes without progress are reported", code == 1 and "moved neither HEAD" in msg
              and len(launched) == before == STALLED_RESUMES, f"{len(launched)} launches: {msg} {state}")
        code, msg = run()
        check("a reported stall is held, not re-reported", code == 0 and "(reported)" in msg, msg)

        os.makedirs(os.path.join(root, "docs", "phase-runs"), exist_ok=True)
        with open(os.path.join(root, "docs", "phase-runs", "run.md"), "w") as fh:
            fh.write("progress\n")
        clock[0] += RELAUNCH_AFTER + 1
        code, msg = run()
        check("progress clears the stall and a resume launches", len(launched) == before + 1, msg)

        os.remove(_state_path(root))
        procs.procs.pop(900, None)
        child_box = {}

        def end_mid_run(argv, r, log):
            child = launcher(exits_after=None)(argv, r, log)
            child_box["c"] = child
            campaign_guard.end(root, s_run, "operator-stop")
            return child
        code, msg = run(launcher=end_mid_run)
        check("an operator stop ends the resumed session", code == 0 and child_box["c"].killed
              and "guard was ended" in msg, msg)

        campaign_guard.acquire(root, s_run, 4, "docs/phase-runs/run.md", "job2")
        os.remove(_state_path(root))
        procs.procs.pop(900, None)
        for label, mutate, expect in (
                ("a failed observation during a resume ends it",
                 lambda: open(_unobserved_flag(root, s_other), "w", encoding="utf-8").write("failed"),
                 "observation failed"),
                ("an emptied observation during a resume ends it",
                 lambda: _atomic(os.path.join(_sessions_dir(root), s_run + ".json"),
                                 {"session": s_run, "owners": []}),
                 "became unreadable")):
            box = {}

            def mid_run(argv, r, log, mutate=mutate, box=box):
                child = launcher(exits_after=None)(argv, r, log)
                box["c"] = child
                return child

            def sleep_then_mutate(_s, mutate=mutate, done=[False]):
                clock.__setitem__(0, clock[0] + 30)
                if not done[0]:
                    mutate()
                    done[0] = True
            code, msg = resurrect(root, procs, launcher=mid_run, killer=lambda c: setattr(c, "killed", True),
                                  clock=lambda: clock[0], sleep=sleep_then_mutate, claude="claude", poll=30)
            check(label, bool(box.get("c")) and box["c"].killed and expect in msg, msg)
            for flag in unobserved(root):
                os.remove(os.path.join(_sessions_dir(root), flag))
            clock[0] += RELAUNCH_AFTER + 1
            procs.procs.pop(900, None)
            record(root, s_run, {"pid": 500, "created": 111, "exe": "claude.exe"})
            if os.path.exists(_state_path(root)):
                os.remove(_state_path(root))

        def attend_mid_run(argv, r, log):
            child = launcher(exits_after=None)(argv, r, log)
            child_box["c"] = child
            record(root, s_other, procs.add(601, 1, "claude.exe", 333))
            return child
        code, msg = run(launcher=attend_mid_run)
        check("an attended session ends the resumed one", code == 0 and child_box["c"].killed and "started" in msg, msg)

        del procs.procs[601]
        os.remove(_state_path(root))
        procs.procs.pop(900, None)
        code, msg = run(launcher=launcher(exits_after=1, code=3))
        check("a resumed session that exits non-zero is a failure", code == 1 and "exited 3" in msg, msg)

        os.remove(_state_path(root))
        procs.procs.pop(900, None)
        code, msg = run(launcher=launcher(exits_after=None), limit=60)
        check("a resume past its limit is stopped and reported", code == 1 and "ran past" in msg, msg)

        with _LaunchLock(root) as held:
            code, msg = run() if held else (None, "lock not taken")
        check("a held launch lock holds the tick", code == 0 and "supervising" in msg, msg)

        # Independent review round 1 (e1504c5): the five findings, each as a case.
        _forget(root)
        procs.procs.pop(900, None)

        def resume_same_session(argv, r, log):
            child = launcher(exits_after=None)(argv, r, log)
            child_box["c"] = child
            record(root, s_run, procs.add(700, 1, "claude.exe", 444))  # SessionStart of the operator's resume
            return child
        code, msg = run(launcher=resume_same_session)
        check("an attended resume of the same session ends the headless one", code == 0
              and child_box["c"].killed and "operator resumed session" in msg, msg)

        del procs.procs[700]
        _forget(root)
        procs.procs.pop(900, None)
        record(root, s_run, procs.add(800, 1, "claude.exe", 555))
        procs.unknown.add(800)
        code, msg = run()
        check("an owner Windows will not describe is held, never taken for dead",
              code == 0 and "cannot tell" in msg, msg)
        procs.unknown.discard(800)
        record(root, s_other, procs.add(801, 1, "claude.exe", 556))
        procs.unknown.add(801)
        del procs.procs[800]
        code, msg = run()
        check("an unreadable other session counts as attended", code == 0 and "attended" in msg, msg)
        procs.unknown.discard(801)
        del procs.procs[801]

        run_file = os.path.join(root, "docs", "phase-runs", "run.md")
        guard = campaign_guard.read_guard(root)
        before_fp = _fingerprint(root, guard)
        with open(run_file, "a", encoding="utf-8") as fh:
            fh.write("- bookkeeping: keep-alive resumed 2026-10-19T00:00:00Z\n")
        check("a bookkeeping line is not progress", _fingerprint(root, guard) == before_fp)
        with open(run_file, "a", encoding="utf-8") as fh:
            fh.write("- shipped D00 T01 §3\n")
        check("a real run-file line is progress", _fingerprint(root, guard) != before_fp)

        old = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=OBSERVED_DAYS + 1)).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        for sess in (s_run, s_other):
            _atomic(os.path.join(_sessions_dir(root), sess + ".json"),
                    {"session": sess, "owner": {"pid": 1, "created": 1}, "seen_at": old})
        third = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        procs.add(910, 1, "claude.exe", 666)
        procs.add(911, 910, "python.exe", 667)
        observe(root, third, procs, start=911)
        kept = observed(root)
        check("pruning keeps the observation the open guard names", s_run in kept and s_other not in kept
              and third in kept, str(sorted(kept)))
        del procs.procs[910], procs.procs[911]
        os.remove(os.path.join(_sessions_dir(root), third + ".json"))

        _forget(root)
        record(root, s_run, {"pid": 1, "created": 1})
        guard_path = campaign_guard._paths(root)[0]
        with open(guard_path, encoding="utf-8") as fh:
            good_guard = fh.read()

        def corrupt_guard(argv, r, log):
            child = launcher(exits_after=None)(argv, r, log)
            child_box["c"] = child
            with open(guard_path, "w", encoding="utf-8") as fh:
                fh.write("{not json")
            return child
        try:
            run(launcher=corrupt_guard)
            check("a broken guard mid-run raises", False)
        except campaign_guard.GuardError:
            check("a broken guard mid-run ends the resumed session", child_box["c"].killed)
        with open(guard_path, "w", encoding="utf-8") as fh:
            fh.write(good_guard)

    print(f"campaign_keepalive self-test: {failed} failed")
    return 1 if failed else 0


def _hook_session() -> str:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return ""
    return str(payload.get("session_id", "")) if isinstance(payload, dict) else ""


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return _self_test()
    if not argv or argv[0] not in ("observe", "status", "resurrect"):
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        return 2
    try:
        opts = campaign_guard._opts(argv[1:])
        root = opts.pop("root", REPO)
        if argv[0] == "observe":
            hook = "session" not in opts
            session = ""
            try:
                session = opts.get("session") or _hook_session()
                print(observe(root, session, default_processes()))
            except (KeepAliveError, OSError) as exc:
                # As the SessionStart hook it fails open: a session must never be blocked from starting. The flag
                # keeps the gap visible: no launch can prove the tree free until this session observes again.
                print(f"campaign_keepalive observe: {exc}", file=sys.stderr)
                if SESSION_ID.match(session or ""):
                    try:
                        os.makedirs(_sessions_dir(root), exist_ok=True)
                        with open(_unobserved_flag(root, session), "w", encoding="utf-8") as fh:
                            fh.write(f"{_now()} {exc}" + chr(10))
                    except OSError as flag_error:
                        print(f"campaign_keepalive observe: could not flag the failure: {flag_error}", file=sys.stderr)
                return 0 if hook else 1
            return 0
        procs = default_processes()
        if argv[0] == "status":
            action, _guard, why = decide(root, procs)
            print(f"report: {why}" if action == "report" else why)
            return 0
        code, line = resurrect(root, procs)
        print(line, file=sys.stdout if code == 0 else sys.stderr)
        return code
    except (KeepAliveError, campaign_guard.GuardError, OSError) as exc:
        print(f"campaign_keepalive: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
