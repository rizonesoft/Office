#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Say whether this PC can run an unattended `process-plan` campaign, before it starts and at every phase start.

    python scripts/check-campaign-host.py            # one line per check; exit 0 ready, 1 fixes listed, 2 cannot check
    python scripts/check-campaign-host.py --notify   # as above, and a failure is emailed to the operator

The campaign runs on this PC for days to months and is resumed by hand when it stops (owner decisions 1, 2 and 15 in
`docs/specs/2026-10-23-campaign-scope-design.md`). A locked screen, a PC that sleeps, a missing Office app or a missing
compiler should park the run with a reason the owner reads on return, not fail mid-section (D00 T03 §12). Every check
only reads: the console session, the AC sleep and screen lock settings, the Office reference apps while an open section
still needs them, the C++ toolchain, `gh`, the pinned reviewer's CLI and the free disk space.

Exit 2 (a check could not run) outranks exit 1 (a check failed): either parks the campaign, and both print every line.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import pin_proposal
import todo_graph

VS_MAJOR = 18  # Visual Studio 2026, whose MSVC toolset builds the C++23 code (D03 T01 §2)
INSTALLER = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Microsoft Visual Studio" / "Installer"
VSWHERE = INSTALLER / "vswhere.exe"
SETUP = INSTALLER / "setup.exe"
TOOLCHAIN = {
    "Microsoft.VisualStudio.Workload.NativeDesktop": "the desktop C++ workload",
    "Microsoft.VisualStudio.Component.VC.Tools.x86.x64": "the MSVC x64 tools",
    "Microsoft.VisualStudio.Component.VC.Tools.ARM64": "the MSVC Arm64 tools",
    "Microsoft.VisualStudio.Component.VC.CMake.Project": "CMake",
    "Microsoft.VisualStudio.Component.Vcpkg": "vcpkg",
    "Microsoft.VisualStudio.Component.VC.Llvm.Clang": "the LLVM clang tools",
}
WINDOWS_SDK = "Microsoft.VisualStudio.Component.Windows11SDK."  # any Windows 11 SDK
WINDOWS_SDK_ADD = WINDOWS_SDK + "26100"  # the one the owner installed on 2026-10-23
OFFICE_APPS = (("Word", "WINWORD.EXE"), ("Excel", "EXCEL.EXE"), ("PowerPoint", "POWERPNT.EXE"),
               ("Outlook (classic)", "OUTLOOK.EXE"), ("Visio", "VISIO.EXE"), ("Project", "WINPROJ.EXE"))
CLICK_TO_RUN = r"SOFTWARE\Microsoft\Office\ClickToRun"
SUB_SLEEP = "238c9fa8-0aad-41ed-83f4-97be242c8f20"
STANDBYIDLE = "29f6c1db-86da-48c5-9fdb-f2b67b1f44da"
HIBERNATEIDLE = "9d7815a6-7ee4-497e-8888-515a05f02364"
DESKTOP = r"Control Panel\Desktop"
DESKTOP_POLICY = r"Software\Policies\Microsoft\Windows\Control Panel\Desktop"
SYSTEM_POLICY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
MIN_FREE_BYTES = 50 * 10**9
PROBE_SECONDS = 120  # every subprocess probe ends by then, so a hung tool cannot hold the campaign before its park
MAX_PROBE_BYTES = 8 * 1024 * 1024  # vswhere with packages prints well under 1 MB
POLL_SECONDS = 0.1
PROBE_MEMORY_BYTES = 2 * 1024**3  # all of a probe's processes together; the TODO reader needs about 60 MB
KILL_SECONDS = 10  # an ended probe is gone by then; past it the probe is reported and left
REVIEWER_STATUS = {"codex": ["login", "status"]}  # exits 0 only when the CLI is signed in
SECTIONS_CODE = """import json, sys
sys.path.insert(0, sys.argv[1])
import todo_graph
print(json.dumps([s.public() for s in todo_graph.ordered(todo_graph.graph(sys.argv[2]))]))
"""
NOTIFY_SECONDS = 180  # the vault read (90 s at most) and the send (60 s at most), with room
NOTICE_CODE = """import json, sys
sys.path.insert(0, sys.argv[1])
import pin_proposal
notice = json.load(open(sys.argv[2], encoding="utf-8"))
try:
    pin_proposal.notify(notice["root"], notice["subject"], notice["body"])
except Exception as exc:
    sys.exit(f"{type(exc).__name__}: {exc}")
"""
SIGNED_OUT = 1  # `gh auth status` and `codex login status` exit 1 when signed out; any other failure is a crash
WTS_ACTIVE = 0
WTS_SESSIONSTATE_LOCK, WTS_SESSIONSTATE_UNLOCK = 0, 1
NO_CONSOLE = 0xFFFFFFFF
HKCU, HKLM = "HKCU", "HKLM"


class Unreadable(Exception):
    """A check could not run, so this PC's readiness is unknown."""


class Host:
    """The real readers. Each returns raw facts; the checks below judge them, so tests replace only this class."""

    root = ROOT

    def console_session(self):
        """(session id, WTS_CONNECTSTATE_CLASS, session flags) of the physical console, or None when nobody is on it."""
        import ctypes
        from ctypes import wintypes

        class Level1(ctypes.Structure):  # WTSINFOEX_LEVEL1_W
            _fields_ = [("SessionId", wintypes.ULONG), ("SessionState", ctypes.c_int),
                        ("SessionFlags", wintypes.LONG), ("WinStationName", wintypes.WCHAR * 33),
                        ("UserName", wintypes.WCHAR * 21), ("DomainName", wintypes.WCHAR * 18),
                        ("LogonTime", wintypes.LARGE_INTEGER), ("ConnectTime", wintypes.LARGE_INTEGER),
                        ("DisconnectTime", wintypes.LARGE_INTEGER), ("LastInputTime", wintypes.LARGE_INTEGER),
                        ("CurrentTime", wintypes.LARGE_INTEGER), ("IncomingBytes", wintypes.DWORD),
                        ("OutgoingBytes", wintypes.DWORD), ("IncomingFrames", wintypes.DWORD),
                        ("OutgoingFrames", wintypes.DWORD), ("IncomingCompressedBytes", wintypes.DWORD),
                        ("OutgoingCompressedBytes", wintypes.DWORD)]

        class InfoEx(ctypes.Structure):  # WTSINFOEXW; its union holds only the level 1 record
            _fields_ = [("Level", wintypes.DWORD), ("Data", Level1)]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        wtsapi32 = ctypes.WinDLL("wtsapi32", use_last_error=True)
        kernel32.WTSGetActiveConsoleSessionId.restype = wintypes.DWORD
        query = wtsapi32.WTSQuerySessionInformationW
        query.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p),
                          ctypes.POINTER(wintypes.DWORD)]
        query.restype = wintypes.BOOL
        wtsapi32.WTSFreeMemory.argtypes = [ctypes.c_void_p]
        session = kernel32.WTSGetActiveConsoleSessionId()
        if session == NO_CONSOLE:
            return None
        buffer, size = ctypes.c_void_p(), wintypes.DWORD()
        if not query(None, session, 25, ctypes.byref(buffer), ctypes.byref(size)):  # 25 = WTSSessionInfoEx
            raise Unreadable(f"WTSQuerySessionInformationW failed (error {ctypes.get_last_error()})")
        try:
            if size.value < ctypes.sizeof(InfoEx):
                raise Unreadable(f"WTSQuerySessionInformationW returned {size.value} bytes")
            info = ctypes.cast(buffer, ctypes.POINTER(InfoEx)).contents
            if info.Level != 1:
                raise Unreadable(f"WTSINFOEXW level {info.Level}")
            return session, info.Data.SessionState, info.Data.SessionFlags
        finally:
            wtsapi32.WTSFreeMemory(buffer)

    def power_ac(self, subgroup, setting):
        """The active power scheme's AC value of one setting, read through the power API (not localised text)."""
        import ctypes
        from ctypes import wintypes

        class GUID(ctypes.Structure):
            _fields_ = [("bytes", ctypes.c_ubyte * 16)]

        def guid(text):
            return GUID.from_buffer_copy(uuid.UUID(text).bytes_le)

        powrprof = ctypes.WinDLL("powrprof")
        kernel32 = ctypes.WinDLL("kernel32")
        scheme = ctypes.POINTER(GUID)()
        error = powrprof.PowerGetActiveScheme(None, ctypes.byref(scheme))
        if error:
            raise Unreadable(f"PowerGetActiveScheme failed (error {error})")
        try:
            value = wintypes.DWORD()
            sub, item = guid(subgroup), guid(setting)
            error = powrprof.PowerReadACValueIndex(None, scheme, ctypes.byref(sub), ctypes.byref(item),
                                                   ctypes.byref(value))
            if error:
                raise Unreadable(f"PowerReadACValueIndex {setting} failed (error {error})")
            return value.value
        finally:
            kernel32.LocalFree(scheme)

    def registry(self, hive, key, name):
        """A registry value, or None when the key or the value is absent."""
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER if hive == HKCU else winreg.HKEY_LOCAL_MACHINE, key) as k:
                return winreg.QueryValueEx(k, name)[0]
        except FileNotFoundError:
            return None

    def screen_saver(self):
        """The live session's screen saver: active, password on resume, and timeout in seconds (SystemParametersInfoW,
        not the stored profile, which a temporary setting can differ from)."""
        import ctypes
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        values = {}
        for name, action, kind in (("active", 0x0010, ctypes.c_int), ("timeout", 0x000E, ctypes.c_int),
                                   ("secure", 0x0076, ctypes.c_int)):  # SPI_GETSCREENSAVE{ACTIVE,TIMEOUT,SECURE}
            value = kind()
            if not user32.SystemParametersInfoW(action, 0, ctypes.byref(value), 0):
                raise Unreadable(f"SystemParametersInfoW {action:#06x} failed (error {ctypes.get_last_error()})")
            values[name] = value.value
        return {"active": bool(values["active"]), "secure": bool(values["secure"]), "timeout": values["timeout"]}

    def is_file(self, path):
        return Path(path).is_file()

    def sections(self):
        """Every section's public fields, in plan order, read from the TODO files by a contained child: the reader runs
        git, and a hung git must not hold the check past its deadline."""
        result = self.run([sys.executable, "-c", SECTIONS_CODE, str(ROOT / "scripts" / "lib"), str(self.root)])
        if result.returncode != 0:
            raise Unreadable((result.stderr.strip().splitlines() or [f"exit {result.returncode}"])[-1])
        rows = json.loads(result.stdout)
        # A record missing a field could otherwise read as "needs no Office" and skip the check.
        if not isinstance(rows, list) or not rows or not all(
                isinstance(r, dict) and isinstance(r.get("ref"), str) and isinstance(r.get("done"), bool)
                and isinstance(r.get("status"), str) and isinstance(r.get("needs"), list)
                and all(isinstance(n, str) for n in r["needs"]) for r in rows):
            raise Unreadable("the TODO reader did not print a list of complete section records")
        return rows

    def vswhere(self):
        """vswhere's instances of Visual Studio 2026 with their packages, or None when vswhere is not installed."""
        if not VSWHERE.is_file():
            return None
        result = self.run([str(VSWHERE), "-products", "*", "-version", f"[{VS_MAJOR}.0,{VS_MAJOR + 1}.0)",
                           "-format", "json", "-utf8", "-include", "packages"])
        if result.returncode != 0:
            raise Unreadable(f"vswhere failed: {result.stderr.strip()}")
        try:
            instances = json.loads(result.stdout)  # vswhere prints [] when nothing matches, never nothing
        except ValueError as exc:
            raise Unreadable(f"vswhere output: {exc}") from None
        if not isinstance(instances, list) or not all(isinstance(i, dict) for i in instances):
            raise Unreadable("vswhere output is not a list of instances")
        for i in instances:
            if not (isinstance(i.get("installationPath"), str) and i["installationPath"]
                    and isinstance(i.get("installationVersion"), str)
                    and re.fullmatch(r"[0-9]+(\.[0-9]+){1,3}", i["installationVersion"])
                    and isinstance(i.get("packages"), list)
                    and all(isinstance(p, dict) and isinstance(p.get("id"), str) for p in i["packages"])):
                raise Unreadable("vswhere printed an instance without its path, version or packages")
        return instances

    def find(self, name):
        """A command's path from the absolute PATH entries only, never the working directory (review-dispatch's rule)."""
        return todo_graph.review_dispatch().find_cli(name)

    def run(self, argv, seconds=None):
        """Run a probe with no input and a deadline, contained with every process it starts, and end them all after.

        On Windows the probe starts suspended, joins a job object that kills every member when it is closed, and only
        then runs, so a descendant can neither escape the job nor outlive the probe; on Linux and WSL it leads its own
        session, whose process group is killed. Output goes to files, not pipes (a descendant holding a pipe would hold
        the read past any deadline), watched while the probe runs and checked again once the tree is ended, so neither
        a hang nor a flood of output gets past PROBE_SECONDS or MAX_PROBE_BYTES: either is reported as Unreadable. The
        output is never printed (it may name the signed-in account).
        """
        limit = PROBE_SECONDS if seconds is None else seconds
        # A descendant ended a moment ago may still hold the output files, so a failed removal is ignored.
        with tempfile.TemporaryDirectory(prefix="campaign-host-", ignore_cleanup_errors=True) as scratch:
            paths = Path(scratch) / "out", Path(scratch) / "err"
            too_big = lambda: any(p.stat().st_size > MAX_PROBE_BYTES for p in paths)
            with open(paths[0], "wb") as out, open(paths[1], "wb") as err, Containment() as box:
                work = Path(scratch) / "work"
                work.mkdir()
                process = box.start(argv, out, err, work)
                problem, deadline = None, time.monotonic() + limit
                while process.poll() is None:
                    if too_big():
                        problem = f"wrote more than {MAX_PROBE_BYTES} bytes"
                        break
                    if time.monotonic() > deadline:
                        problem = f"did not finish within {limit} seconds"
                        break
                    time.sleep(POLL_SECONDS)
                if not box.end(process):
                    problem = (problem or "left processes running") + ", and could not be ended"
            if problem is None and too_big():
                problem = f"wrote more than {MAX_PROBE_BYTES} bytes"
            if problem:
                raise Unreadable(f"{Path(argv[0]).name} {problem}")

            def read(path):
                with open(path, "rb") as handle:
                    return handle.read(MAX_PROBE_BYTES).decode("utf-8", errors="replace")
            return subprocess.CompletedProcess(argv, process.returncode, read(paths[0]), read(paths[1]))
    def notify(self, subject, body):
        """Email the operator through alert.py, in a contained child with a deadline: the sender reads its key through
        WSL with pipes, and a descendant holding one must not keep the campaign from parking."""
        with tempfile.TemporaryDirectory(prefix="campaign-notice-", ignore_cleanup_errors=True) as scratch:
            notice = Path(scratch) / "notice.json"
            notice.write_text(json.dumps({"root": str(self.root), "subject": subject, "body": body}), encoding="utf-8")
            result = self.run([sys.executable, "-c", NOTICE_CODE, str(ROOT / "scripts" / "lib"), str(notice)],
                              seconds=NOTIFY_SECONDS)
        if result.returncode != 0:
            raise Unreadable((result.stderr.strip().splitlines() or [f"exit {result.returncode}"])[-1])

    def reviewer_cli(self):
        """(reviewer name, CLI name) the pin routes Claude's work to; review-dispatch's Refused when the pin is bad."""
        dispatch = todo_graph.review_dispatch()
        pin = dispatch.load_pin(self.root / ".conclave" / "reviewers.toml")
        name = pin["routes"]["claude"][0]
        return name, pin["reviewers"][name]["cli"]

    def free_bytes(self):
        return shutil.disk_usage(self.root).free


class Containment:
    """A probe and everything it starts, ended together: a Windows job object, or a POSIX session's process group."""

    def __enter__(self):
        self.job = None
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            class Basic(ctypes.Structure):  # JOBOBJECT_BASIC_LIMIT_INFORMATION
                _fields_ = [("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
                            ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER), ("LimitFlags", wintypes.DWORD),
                            ("MinimumWorkingSetSize", ctypes.c_size_t), ("MaximumWorkingSetSize", ctypes.c_size_t),
                            ("ActiveProcessLimit", wintypes.DWORD), ("Affinity", ctypes.c_size_t),
                            ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]

            class Extended(ctypes.Structure):  # JOBOBJECT_EXTENDED_LIMIT_INFORMATION
                _fields_ = [("BasicLimitInformation", Basic), ("IoInfo", ctypes.c_ulonglong * 6),
                            ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                            ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

            self.ctypes = ctypes
            self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            self.ntdll = ctypes.WinDLL("ntdll")
            self.kernel32.CreateJobObjectW.restype = wintypes.HANDLE
            self.kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
            for name in ("SetInformationJobObject", "AssignProcessToJobObject", "TerminateJobObject", "CloseHandle"):
                getattr(self.kernel32, name).restype = wintypes.BOOL
            self.kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p,
                                                              wintypes.DWORD]
            self.kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
            self.kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
            self.kernel32.QueryInformationJobObject.restype = wintypes.BOOL
            self.kernel32.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p,
                                                                wintypes.DWORD, ctypes.c_void_p]
            self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            self.ntdll.NtResumeProcess.argtypes = [wintypes.HANDLE]
            self.job = self.kernel32.CreateJobObjectW(None, None)
            if not self.job:
                raise Unreadable(f"CreateJobObjectW failed (error {ctypes.get_last_error()})")
            info = Extended()
            # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_JOB_MEMORY: the memory limit bounds what any member
            # buffers (a nested capture of git or WSL output included), which the output files alone cannot see.
            info.BasicLimitInformation.LimitFlags = 0x2000 | 0x200
            info.JobMemoryLimit = PROBE_MEMORY_BYTES
            if not self.kernel32.SetInformationJobObject(self.job, 9, ctypes.byref(info), ctypes.sizeof(info)):
                self.kernel32.CloseHandle(self.job)  # 9 = JobObjectExtendedLimitInformation
                raise Unreadable(f"SetInformationJobObject failed (error {ctypes.get_last_error()})")
        return self

    def start(self, argv, out, err, cwd):
        """Start the probe in `cwd`, a scratch folder: Windows looks for a bare program name in the working directory
        first, so neither the probe nor anything it starts by a bare name runs a program planted in the repository."""
        if os.name != "nt":
            def limit():  # per process on POSIX, where there is no job: each member is held to the same bound
                import resource
                resource.setrlimit(resource.RLIMIT_AS, (PROBE_MEMORY_BYTES, PROBE_MEMORY_BYTES))
            return subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err, cwd=cwd,
                                    start_new_session=True, preexec_fn=limit)
        create_suspended = 0x00000004
        process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err, cwd=cwd,
                                   creationflags=create_suspended | pin_proposal.NO_WINDOW)
        handle = int(process._handle)
        # Joined while suspended, so nothing it starts can be outside the job. NtResumeProcess resumes it: Popen keeps
        # no handle to the primary thread that ResumeThread would need.
        if not self.kernel32.AssignProcessToJobObject(self.job, handle):
            process.kill()
            raise Unreadable(f"AssignProcessToJobObject failed (error {self.ctypes.get_last_error()})")
        status = self.ntdll.NtResumeProcess(handle)
        if status:
            process.kill()
            raise Unreadable(f"NtResumeProcess failed (status {status & 0xFFFFFFFF:#x})")
        return process

    def active(self):
        """How many processes are still in the job (termination is asynchronous: TerminateJobObject only starts it)."""
        ctypes = self.ctypes

        class Accounting(ctypes.Structure):  # JOBOBJECT_BASIC_ACCOUNTING_INFORMATION
            _fields_ = [("TotalUserTime", ctypes.c_longlong), ("TotalKernelTime", ctypes.c_longlong),
                        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
                        ("ThisPeriodTotalKernelTime", ctypes.c_longlong), ("TotalPageFaultCount", ctypes.c_ulong),
                        ("TotalProcesses", ctypes.c_ulong), ("ActiveProcesses", ctypes.c_ulong),
                        ("TotalTerminatedProcesses", ctypes.c_ulong)]

        info = Accounting()
        if not self.kernel32.QueryInformationJobObject(self.job, 1, ctypes.byref(info), ctypes.sizeof(info), None):
            return None  # 1 = JobObjectBasicAccountingInformation; unreadable counts as not yet empty
        return info.ActiveProcesses

    def end(self, process):
        """End the probe and every descendant; True when all of them are gone within KILL_SECONDS, so no output is
        still pending when the caller measures it."""
        deadline = time.monotonic() + KILL_SECONDS
        if os.name == "nt":
            self.kernel32.TerminateJobObject(self.job, 1)
            while self.active() != 0:
                if time.monotonic() > deadline:
                    return False
                time.sleep(POLL_SECONDS)
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass  # nothing in the group is left to kill
        if process.poll() is None:
            process.kill()  # through the handle
        try:
            process.wait(timeout=max(0.0, deadline - time.monotonic()))
            return True
        except subprocess.TimeoutExpired:
            return False

    def __exit__(self, *exc):
        if self.job:
            self.kernel32.TerminateJobObject(self.job, 1)
            self.kernel32.CloseHandle(self.job)  # KILL_ON_JOB_CLOSE ends anything that is somehow still in it
        return False


def ok(name, detail):
    return {"name": name, "state": "ok", "detail": detail, "fix": None}


def fail(name, detail, fix):
    return {"name": name, "state": "fail", "detail": detail, "fix": fix}


def skip(name, detail):
    return {"name": name, "state": "skip", "detail": detail, "fix": None}


def check_session(host):
    found = host.console_session()
    if found is None:
        return fail("session", "no user is signed in at the console", "sign in at this PC's console and leave it unlocked")
    session, state, flags = found
    if state != WTS_ACTIVE:
        return fail("session", f"console session {session} is not active (state {state})",
                    "sign in at this PC's console (not only over Remote Desktop) and leave it unlocked")
    if flags == WTS_SESSIONSTATE_LOCK:
        return fail("session", f"screen locked (console session {session})", "unlock this PC and leave it unlocked")
    if flags != WTS_SESSIONSTATE_UNLOCK:
        raise Unreadable(f"console session {session} reports an unknown lock state ({flags})")
    return ok("session", f"console session {session} is active and unlocked")


def minutes(seconds):
    return f"{seconds // 60} minutes" if seconds % 60 == 0 else f"{seconds} seconds"


def check_power(host):
    fixes, found = [], []
    for setting, what, command in ((STANDBYIDLE, "sleep", "standby-timeout-ac"),
                                   (HIBERNATEIDLE, "hibernate", "hibernate-timeout-ac")):
        seconds = host.power_ac(SUB_SLEEP, setting)
        if seconds:
            found.append(f"{what} after {minutes(seconds)} on AC")
            fixes.append(f"powercfg /change {command} 0")
    if fixes:
        return fail("power", ", ".join(found), "; ".join(fixes))
    return ok("power", "sleep and hibernate are off on AC")


def check_screen_lock(host):
    """The screen saver as the live session runs it: SystemParametersInfo's values, which can differ from the stored
    profile, each overridden by the screen saver policy where the policy sets it."""
    live = host.screen_saver()

    def effective(name, current, flag=True):
        value = host.registry(HKCU, DESKTOP_POLICY, name)
        if value is None:
            return current, False
        if flag and str(value).strip() not in ("0", "1"):
            raise Unreadable(f"the screen saver policy {name} is {value!r}, not 0 or 1")
        return value, True

    fixes, found = [], []
    active, _ = effective("ScreenSaveActive", "1" if live["active"] else "0")
    secure, by_policy = effective("ScreenSaverIsSecure", "1" if live["secure"] else "0")
    timeout, _ = effective("ScreenSaveTimeOut", str(live["timeout"]), flag=False)
    saver = host.registry(HKCU, DESKTOP_POLICY, "SCRNSAVE.EXE") or host.registry(HKCU, DESKTOP, "SCRNSAVE.EXE")
    try:
        seconds = int(str(timeout).strip())
    except ValueError:
        raise Unreadable(f"ScreenSaveTimeOut is not a number of seconds: {timeout!r}") from None
    if not 0 <= seconds <= 86400:  # 0 (off) or 1 to 86400 seconds, as Microsoft's ScreenSaveTimeOut policy allows
        raise Unreadable(f"ScreenSaveTimeOut is {seconds}, outside 0 to 86400 seconds")
    # A timeout of 0 never starts the screen saver, so it never locks (Microsoft's ScreenSaveTimeOut policy).
    if str(active).strip() == "1" and str(secure).strip() == "1" and saver and seconds > 0:
        found.append(f"the screen saver locks the PC after {seconds} seconds")
        fixes.append("ask the administrator to remove the password-protected screen saver policy" if by_policy else
                     "clear 'On resume, display logon screen' in Screen Saver Settings (control desk.cpl,,@screensaver)")
    inactivity = host.registry(HKLM, SYSTEM_POLICY, "InactivityTimeoutSecs")
    if inactivity:
        found.append(f"the machine inactivity limit locks the PC after {inactivity} seconds")
        fixes.append("in an elevated PowerShell: Remove-ItemProperty "
                     "'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System' InactivityTimeoutSecs")
    if fixes:
        return fail("screen lock", "; ".join(found), "; ".join(fixes))
    return ok("screen lock", "no screen saver lock and no inactivity limit")


def office_needed(host):
    """The open sections that need live Office, read from the TODO files; when the tree cannot be read, assume some do."""
    try:
        sections = host.sections()
    except Exception as exc:  # any failure to read the tree (a refusal, a git timeout, a bug) falls back to checking
        return None, f"the TODO tree cannot be read ({type(exc).__name__}: {exc}), so Office is checked"
    refs = [s["ref"] for s in sections if not s["done"] and s["status"] != "superseded" and "office" in s["needs"]]
    return refs, None


def check_office(host):
    refs, note = office_needed(host)
    if refs == []:
        return skip("office", "no open section needs Office")
    why = note or f"{len(refs)} open sections need Office, first {refs[0]}"
    install = host.registry(HKLM, CLICK_TO_RUN, "InstallPath")
    if not install:
        return fail("office", f"Microsoft 365 Apps (Click-to-Run) is not installed; {why}",
                    "install Microsoft 365 Apps with Visio and Project (Click-to-Run)")
    folder = Path(install) / "root" / "Office16"
    missing = [f"{app} ({exe})" for app, exe in OFFICE_APPS if not host.is_file(folder / exe)]
    build = host.registry(HKLM, CLICK_TO_RUN + r"\Configuration", "VersionToReport") or "unknown"
    if missing:
        return fail("office", f"missing from {folder}: {', '.join(missing)} (build {build}); {why}",
                    "add the missing apps to the Click-to-Run install")
    return ok("office", f"{', '.join(app for app, _ in OFFICE_APPS)} present, build {build}; {why}")


def check_toolchain(host):
    instances = host.vswhere()
    stable = [i for i in instances or [] if not i.get("isPrerelease")]
    if not stable:
        return fail("toolchain", f"no stable Visual Studio {VS_MAJOR} (2026) is installed",
                    "install Visual Studio 2026 with the desktop C++ workload")
    newest = max(stable, key=lambda i: [int(p) for p in i["installationVersion"].split(".")])  # validated by vswhere()
    have = {p.get("id") for p in newest.get("packages") or [] if isinstance(p, dict)}
    missing = [i for i in TOOLCHAIN if i not in have]
    if not any(str(i).startswith(WINDOWS_SDK) for i in have):
        missing.append(WINDOWS_SDK_ADD)
    name = newest.get("displayName", "Visual Studio")
    if missing:
        what = [TOOLCHAIN.get(i, "a Windows 11 SDK") for i in missing]
        add = " ".join(f"--add {i}" for i in missing)
        quote = lambda path: "'" + str(path).replace("'", "''") + "'"  # a PowerShell single-quoted string
        return fail("toolchain", f"{name} lacks {', '.join(what)}",
                    f"in an elevated PowerShell: & {quote(SETUP)} modify --installPath "
                    f"{quote(newest['installationPath'])} {add} --passive")
    return ok("toolchain", f"{name} has every C++ component the build needs")


def exit_text(code):
    """An exit code as a person reads it: a Windows NTSTATUS crash code in hex, a POSIX signal by number."""
    if code < 0:
        return f"killed by signal {-code}"
    return f"exit {code:#010x}" if code >= 0xC0000000 else f"exit {code}"


def check_gh(host):
    gh = host.find("gh")
    if not gh:
        return fail("gh", "gh is not on PATH", "install the GitHub CLI: winget install GitHub.cli")
    result = host.run([gh, "auth", "status"])
    if result.returncode == SIGNED_OUT:
        return fail("gh", "gh is not signed in", "gh auth login")
    if result.returncode != 0:
        raise Unreadable(f"gh auth status ended abnormally ({exit_text(result.returncode)})")
    return ok("gh", "gh is signed in")


def check_reviewer(host):
    try:
        reviewer, cli = host.reviewer_cli()
    except todo_graph.review_dispatch().Refused as exc:
        return fail("reviewer", f"the reviewer pin is refused: {exc}", "repair .conclave/reviewers.toml")
    path = host.find(cli)
    if not path:
        return fail("reviewer", f"the pinned reviewer {reviewer}'s CLI {cli} is not on PATH",
                    "install the Codex CLI: npm install -g @openai/codex")
    try:
        result = host.run([path] + REVIEWER_STATUS[cli])
    except OSError as exc:
        return fail("reviewer", f"the pinned reviewer {reviewer}'s CLI {cli} cannot start ({exc.strerror or exc})",
                    "reinstall the Codex CLI: npm install -g @openai/codex")
    if result.returncode == SIGNED_OUT:
        return fail("reviewer", f"the pinned reviewer {reviewer}'s CLI {cli} is not signed in", f"{cli} login")
    if result.returncode != 0:
        raise Unreadable(f"{cli} login status ended abnormally ({exit_text(result.returncode)})")
    return ok("reviewer", f"the pinned reviewer {reviewer}'s CLI {cli} is on PATH and signed in")


def check_disk(host):
    free = host.free_bytes()
    gb = free / 10**9
    drive = Path(host.root).anchor or str(host.root)
    if free < MIN_FREE_BYTES:
        return fail("disk", f"{gb:.0f} GB free on {drive}, under {MIN_FREE_BYTES // 10**9} GB",
                    f"free space on {drive}")
    return ok("disk", f"{gb:.0f} GB free on {drive}")


CHECKS = (check_session, check_power, check_screen_lock, check_office, check_toolchain, check_gh, check_reviewer,
          check_disk)
NAMES = ("session", "power", "screen lock", "office", "toolchain", "gh", "reviewer", "disk")


def run_checks(host):
    results = []
    for check, name in zip(CHECKS, NAMES):
        try:
            results.append(check(host))
        except Exception as exc:  # a check that cannot finish leaves readiness unknown: exit 2, never a traceback
            results.append({"name": name, "state": "error", "detail": f"could not check: {exc}", "fix": None})
    return results


def report(results):
    lines = []
    for r in results:
        line = f"{r['state'].upper() if r['state'] != 'ok' else 'ok':<5} {r['name']}: {r['detail']}"
        lines.append(line + (f"\n      fix: {r['fix']}" if r["fix"] else ""))
    return lines


def main(argv=None, host=None, mail=None):
    parser = argparse.ArgumentParser(description="Say whether this PC can run an unattended campaign.")
    parser.add_argument("--notify", action="store_true", help="email the operator when a check fails")
    args = parser.parse_args(argv)
    host = host or Host()
    results = run_checks(host)
    lines = report(results)
    print("\n".join(lines))
    code = 2 if any(r["state"] == "error" for r in results) else 1 if any(r["state"] == "fail" for r in results) else 0
    print({0: "ready: every check passed", 1: "not ready: apply the fixes above",
           2: "unknown: a check could not run"}[code])
    if code and args.notify:
        try:
            body = "\n".join(lines + ["", "The campaign parks until these are fixed and it is resumed by hand."])
            (mail or host.notify)(f"Office: campaign host not ready on {socket.gethostname()}", body)
        except Exception as exc:  # the park still happens: the line below lands in the run file with the fixes
            print(f"email not sent: {exc}")
    return code


if __name__ == "__main__":
    sys.exit(main())
