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
import shutil
import socket
import subprocess
import sys
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
REVIEWER_STATUS = {"codex": ["login", "status"]}  # exits 0 only when the CLI is signed in
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

    def is_file(self, path):
        return Path(path).is_file()

    def sections(self):
        return todo_graph.graph(self.root)

    def vswhere(self):
        """vswhere's instances of Visual Studio 2026 with their packages, or None when vswhere is not installed."""
        if not VSWHERE.is_file():
            return None
        result = subprocess.run([str(VSWHERE), "-products", "*", "-version", f"[{VS_MAJOR}.0,{VS_MAJOR + 1}.0)",
                                 "-format", "json", "-utf8", "-include", "packages"],
                                capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL,
                                timeout=PROBE_SECONDS, creationflags=pin_proposal.NO_WINDOW)
        if result.returncode != 0:
            raise Unreadable(f"vswhere failed: {result.stderr.strip()}")
        try:
            return json.loads(result.stdout or "[]")
        except ValueError as exc:
            raise Unreadable(f"vswhere output: {exc}") from None

    def find(self, name):
        """A command's path from the absolute PATH entries only, never the working directory (review-dispatch's rule)."""
        return todo_graph.review_dispatch().find_cli(name)

    def run(self, argv):
        """Run a probe with no input and a deadline; its output is never printed (it may name the signed-in account)."""
        return subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              stdin=subprocess.DEVNULL, timeout=PROBE_SECONDS, creationflags=pin_proposal.NO_WINDOW)

    def reviewer_cli(self):
        """(reviewer name, CLI name) the pin routes Claude's work to; review-dispatch's Refused when the pin is bad."""
        dispatch = todo_graph.review_dispatch()
        pin = dispatch.load_pin(self.root / ".conclave" / "reviewers.toml")
        name = pin["routes"]["claude"][0]
        return name, pin["reviewers"][name]["cli"]

    def free_bytes(self):
        return shutil.disk_usage(self.root).free


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
    def desktop(name):  # the screen saver policy, when set, overrides the user's own setting
        value = host.registry(HKCU, DESKTOP_POLICY, name)
        return (value, True) if value is not None else (host.registry(HKCU, DESKTOP, name), False)

    fixes, found = [], []
    (active, _), (secure, by_policy) = desktop("ScreenSaveActive"), desktop("ScreenSaverIsSecure")
    saver, _ = desktop("SCRNSAVE.EXE")
    if str(active) == "1" and str(secure) == "1" and saver:
        timeout, _ = desktop("ScreenSaveTimeOut")
        found.append(f"the screen saver locks the PC after {timeout or 'its timeout in'} seconds")
        fixes.append("ask the administrator to remove the password-protected screen saver policy" if by_policy else
                     "Set-ItemProperty 'HKCU:\\Control Panel\\Desktop' ScreenSaverIsSecure 0")
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
    except (todo_graph.Refused, OSError, ValueError) as exc:
        return None, f"the TODO tree cannot be read ({exc}), so Office is checked"
    refs = [s.ref for s in todo_graph.ordered(sections)
            if not s.done and s.status != "superseded" and "office" in s.needs]
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
    newest = max(stable, key=lambda i: [int(p) for p in str(i.get("installationVersion", "0")).split(".")
                                        if p.isdigit()])
    have = {p.get("id") for p in newest.get("packages") or [] if isinstance(p, dict)}
    missing = [i for i in TOOLCHAIN if i not in have]
    if not any(str(i).startswith(WINDOWS_SDK) for i in have):
        missing.append(WINDOWS_SDK_ADD)
    name = newest.get("displayName", "Visual Studio")
    if missing:
        what = [TOOLCHAIN.get(i, "a Windows 11 SDK") for i in missing]
        add = " ".join(f"--add {i}" for i in missing)
        return fail("toolchain", f"{name} lacks {', '.join(what)}",
                    f"in an elevated PowerShell: & '{SETUP}' modify --installPath "
                    f"'{newest.get('installationPath')}' {add} --passive")
    return ok("toolchain", f"{name} has every C++ component the build needs")


def check_gh(host):
    gh = host.find("gh")
    if not gh:
        return fail("gh", "gh is not on PATH", "install the GitHub CLI: winget install GitHub.cli")
    result = host.run([gh, "auth", "status"])
    if result.returncode != 0:
        return fail("gh", "gh is not signed in", "gh auth login")
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
    if result.returncode != 0:
        return fail("reviewer", f"the pinned reviewer {reviewer}'s CLI {cli} is not signed in", f"{cli} login")
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


def main(argv=None, host=None, mail=pin_proposal.notify):
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
            mail(host.root, f"Office: campaign host not ready on {socket.gethostname()}",
                 "\n".join(lines + ["", "The campaign parks until these are fixed and it is resumed by hand."]))
        except Exception as exc:  # the park still happens: the line below lands in the run file with the fixes
            print(f"email not sent: {exc}")
    return code


if __name__ == "__main__":
    sys.exit(main())
