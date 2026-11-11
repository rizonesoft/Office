# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Start a child so that it and everything it starts can be stopped together (D00 T03 §36).

On Windows the child starts suspended inside a job object set to kill every member when the job closes, joins the job
before it has run an instruction, and is then resumed, so nothing it starts can be outside the job (a job without
JOB_OBJECT_LIMIT_BREAKAWAY_OK lets no member leave it). Elsewhere the child leads a new session, so its process group
holds its descendants. `Tree.end()` stops every member, waits until they are gone and says how many were still running
besides the child: a test or harness that ends a child this way leaves no orphan behind, which `subprocess.run(timeout=)`
does not promise (it kills one process; the 2026-11-08 incident in the global rules).

    with process_tree.Tree() as tree:
        child = tree.start(argv, cwd=folder, stdin=handle, stdout=out, stderr=err)
        ...
        strays = tree.end()

`run()` wraps that for the common case: a time limit, a limit on the size of the output files, and the outcome.
"""
from dataclasses import dataclass
import os
from pathlib import Path
import signal
import subprocess
import time

POLL_SECONDS = 0.2
KILL_SECONDS = 10  # an ended tree is gone well before this; past it end() raises instead of pretending
NO_WINDOW = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW: a scheduled run opens no console
CREATE_SUSPENDED = 0x00000004
CREATE_NEW_PROCESS_GROUP = 0x00000200
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
EXTENDED_LIMIT_INFORMATION = 9  # JobObjectExtendedLimitInformation
BASIC_ACCOUNTING_INFORMATION = 1  # JobObjectBasicAccountingInformation


class TreeError(OSError):
    """The containment could not be set up, or a tree would not end."""


def _win32():
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

    class Accounting(ctypes.Structure):  # JOBOBJECT_BASIC_ACCOUNTING_INFORMATION
        _fields_ = [("TotalUserTime", ctypes.c_longlong), ("TotalKernelTime", ctypes.c_longlong),
                    ("ThisPeriodTotalUserTime", ctypes.c_longlong), ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
                    ("TotalPageFaultCount", ctypes.c_ulong), ("TotalProcesses", ctypes.c_ulong),
                    ("ActiveProcesses", ctypes.c_ulong), ("TotalTerminatedProcesses", ctypes.c_ulong)]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    ntdll = ctypes.WinDLL("ntdll")
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    for name in ("SetInformationJobObject", "AssignProcessToJobObject", "TerminateJobObject", "CloseHandle",
                 "QueryInformationJobObject"):
        getattr(kernel32, name).restype = wintypes.BOOL
    kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel32.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
                                                   ctypes.c_void_p]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                                    ctypes.POINTER(wintypes.DWORD)]
    ntdll.NtResumeProcess.argtypes = [wintypes.HANDLE]
    ntdll.NtResumeProcess.restype = ctypes.c_int32
    return ctypes, kernel32, ntdll, Extended, Accounting


class Tree:
    """One child and all its descendants. Use as a context manager: leaving it always ends the tree."""

    def __init__(self, memory_bytes=None):
        self.memory_bytes = memory_bytes  # Windows: a limit on the whole job's committed memory; None for none
        self.job = None
        self.child = None
        self.ended = False

    def __enter__(self):
        if os.name == "nt":
            self.ctypes, self.kernel32, self.ntdll, extended, self.accounting = _win32()
            self.job = self.kernel32.CreateJobObjectW(None, None)
            if not self.job:
                raise TreeError(f"CreateJobObjectW failed (error {self.ctypes.get_last_error()})")
            info = extended()
            info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if self.memory_bytes:
                info.BasicLimitInformation.LimitFlags |= 0x200  # JOB_OBJECT_LIMIT_JOB_MEMORY
                info.JobMemoryLimit = self.memory_bytes
            if not self.kernel32.SetInformationJobObject(self.job, EXTENDED_LIMIT_INFORMATION,
                                                         self.ctypes.byref(info), self.ctypes.sizeof(info)):
                error = self.ctypes.get_last_error()
                self.kernel32.CloseHandle(self.job)
                self.job = None
                raise TreeError(f"SetInformationJobObject failed (error {error})")
        return self

    def __exit__(self, *exc):
        try:
            self.end()
        finally:
            if self.job is not None:
                self.kernel32.CloseHandle(self.job)  # kill on close: nothing survives the handle either
                self.job = None
        return False

    def start(self, argv, cwd=None, stdin=None, stdout=None, stderr=None, env=None):
        """Start the one child of this tree. `stdin`, `stdout` and `stderr` are open files or None (the null device),
        never pipes: a pipe nobody drains stalls the child, and a harness has no reason to hold output in memory."""
        if self.child is not None:
            raise TreeError("a tree holds one child; start another tree")
        stdin = subprocess.DEVNULL if stdin is None else stdin
        stdout = subprocess.DEVNULL if stdout is None else stdout
        stderr = subprocess.DEVNULL if stderr is None else stderr
        if os.name != "nt":
            self.child = subprocess.Popen(argv, cwd=cwd, stdin=stdin, stdout=stdout, stderr=stderr, env=env,
                                          start_new_session=True)
            return self.child
        flags = CREATE_SUSPENDED | CREATE_NEW_PROCESS_GROUP | NO_WINDOW
        child = subprocess.Popen(argv, cwd=cwd, stdin=stdin, stdout=stdout, stderr=stderr, env=env,
                                 creationflags=flags)
        handle = int(child._handle)
        # Joined while suspended, so nothing it starts is outside the job; NtResumeProcess resumes it because Popen
        # keeps no handle to the primary thread that ResumeThread would need.
        if not self.kernel32.AssignProcessToJobObject(self.job, handle):
            error = self.ctypes.get_last_error()
            child.kill()
            child.wait()
            raise TreeError(f"AssignProcessToJobObject failed (error {error})")
        status = self.ntdll.NtResumeProcess(handle)
        if status:
            child.kill()
            child.wait()
            raise TreeError(f"NtResumeProcess failed (status {status & 0xFFFFFFFF:#x})")
        self.child = child
        return child

    def active(self):
        """How many processes of the tree are running, the child included (Windows: read from the job; elsewhere:
        whether the process group still has a member, so 0 or at least 1)."""
        if self.child is None:
            return 0
        if os.name == "nt":
            info = self.accounting()
            if not self.kernel32.QueryInformationJobObject(self.job, BASIC_ACCOUNTING_INFORMATION,
                                                           self.ctypes.byref(info), self.ctypes.sizeof(info), None):
                raise TreeError(f"QueryInformationJobObject failed (error {self.ctypes.get_last_error()})")
            return int(info.ActiveProcesses)
        self.child.poll()  # reap the child itself, or the group reads as alive while it is a zombie
        try:
            os.killpg(self.child.pid, 0)
            return 1
        except (ProcessLookupError, PermissionError):
            return 0

    def _members(self):
        """The ids of the processes in the job now (JobObjectBasicProcessIdList), Windows only."""
        ctypes = self.ctypes
        size = 1024
        while True:
            class IdList(ctypes.Structure):  # JOBOBJECT_BASIC_PROCESS_ID_LIST with room for `size` ids
                _fields_ = [("NumberOfAssignedProcesses", ctypes.c_ulong), ("NumberOfProcessIdsInList", ctypes.c_ulong),
                            ("ProcessIdList", ctypes.c_size_t * size)]
            info = IdList()
            if self.kernel32.QueryInformationJobObject(self.job, 3, ctypes.byref(info), ctypes.sizeof(info), None):
                return [int(info.ProcessIdList[i]) for i in range(info.NumberOfProcessIdsInList)]
            if ctypes.get_last_error() != 234 or size >= 1 << 16:  # ERROR_MORE_DATA: grow the list and ask again
                raise TreeError(f"QueryInformationJobObject failed (error {ctypes.get_last_error()})")
            size *= 4

    def _image(self, handle):
        """The file name of a process's executable, lower case, or "" when it cannot be read."""
        ctypes = self.ctypes
        buffer = ctypes.create_unicode_buffer(32768)
        length = ctypes.c_ulong(len(buffer))
        if not self.kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(length)):
            return ""
        return os.path.basename(buffer.value).lower()

    def _end_job(self, deadline):
        """Terminate the job and wait on each member's own handle until it has exited. The job's member count can read
        0 a moment before the last member's process object is signalled, so the count alone is not proof. Returns the
        strays: members other than the child, not counting the console host Windows starts for a console child
        (conhost.exe belongs to the child's console, not to anything the child started)."""
        synchronize_and_query = 0x00100000 | 0x1000  # SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION
        handles = []
        strays = 0
        try:
            for pid in self._members():
                handle = self.kernel32.OpenProcess(synchronize_and_query, False, pid)
                if not handle:
                    continue  # it exited between the listing and the open
                handles.append(handle)
                if pid != self.child.pid and self._image(handle) != "conhost.exe" \
                        and self.kernel32.WaitForSingleObject(handle, 0) == 0x102:  # WAIT_TIMEOUT: still running
                    strays += 1
            self.kernel32.TerminateJobObject(self.job, 1)
            for handle in handles:
                left = max(0, int((deadline - time.monotonic()) * 1000))
                if self.kernel32.WaitForSingleObject(handle, left) != 0:  # WAIT_OBJECT_0: the process has exited
                    raise TreeError(f"the tree of process {self.child.pid} was still running {KILL_SECONDS} s after "
                                    f"it was stopped")
        finally:
            for handle in handles:
                self.kernel32.CloseHandle(handle)
        while self.active():  # a member that joined after the listing is ended by the terminate too
            if time.monotonic() > deadline:
                raise TreeError(f"the tree of process {self.child.pid} was still running {KILL_SECONDS} s after it was "
                                f"stopped")
            time.sleep(POLL_SECONDS / 4)
        return strays

    def end(self):
        """Stop every member, wait until they are gone and reap the child. Returns how many processes the child had
        started that were still running when it was called (on Windows the exact count; elsewhere 1 when the child had
        exited and its process group still had a member, else 0). Raises TreeError when the tree is still running
        KILL_SECONDS later. Calling it again returns 0."""
        if self.child is None or self.ended:
            return 0
        deadline = time.monotonic() + KILL_SECONDS
        if os.name == "nt":
            strays = self._end_job(deadline)
        else:
            strays = 1 if self.child.poll() is not None and self.active() else 0
            try:
                os.killpg(self.child.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass  # the group is already empty
        try:
            self.child.wait(timeout=max(0.1, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            raise TreeError(f"process {self.child.pid} did not exit {KILL_SECONDS} s after it was stopped") from None
        self.ended = True
        return strays


@dataclass
class Outcome:
    exit: int | None  # the child's exit code; None when it was stopped
    stopped: str | None  # why it was stopped: "time limit", "output limit" or "cancelled"; None when it ended itself
    seconds: float
    strays: int  # processes the child left running, stopped with it


def _too_big(paths, max_bytes):
    """Whether the files together hold more than `max_bytes`: a child that splits a flood between its output files
    is bounded as one that writes it to one."""
    total = 0
    for path in paths:
        try:
            total += Path(path).stat().st_size
        except OSError:
            continue  # not written yet
    return total > max_bytes


def run(argv, cwd=None, stdin_path=None, stdout_path=None, stderr_path=None, timeout=None, max_bytes=None,
        watched=(), env=None, cancel=None):
    """Run `argv` to its end inside a Tree, with its standard input read from `stdin_path` and its output written to
    the two files. The tree is stopped when the time limit passes, when the output files together (the two, and every
    path in `watched`) pass `max_bytes`, or when the `cancel` event (a threading.Event) is set, and it is always stopped at
    the end, so whatever the child left running ends with it. Returns an Outcome."""
    started = time.monotonic()
    paths = [p for p in (stdout_path, stderr_path, *watched) if p]
    stdin = open(stdin_path, "rb") if stdin_path else None
    out = open(stdout_path, "wb") if stdout_path else None
    err = open(stderr_path, "wb") if stderr_path else None
    try:
        with Tree() as tree:
            child = tree.start(argv, cwd=cwd, stdin=stdin, stdout=out, stderr=err, env=env)
            stopped = None
            while child.poll() is None:
                if cancel is not None and cancel.is_set():
                    stopped = "cancelled"
                    break
                if timeout is not None and time.monotonic() - started > timeout:
                    stopped = "time limit"
                    break
                if max_bytes is not None and _too_big(paths, max_bytes):
                    stopped = "output limit"
                    break
                try:
                    child.wait(timeout=POLL_SECONDS)
                except subprocess.TimeoutExpired:
                    pass
            if stopped is None and max_bytes is not None and _too_big(paths, max_bytes):
                stopped = "output limit"  # a child that floods and exits at once is still over the limit
            strays = tree.end()
            code = None if stopped else child.returncode
    finally:
        for handle in (stdin, out, err):
            if handle is not None:
                handle.close()
    return Outcome(exit=code, stopped=stopped, seconds=round(time.monotonic() - started, 1), strays=strays)
