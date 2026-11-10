#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Run the tooling tests one file per process, several files at a time.

    python scripts/run-tests.py                      # every scripts/tests/test_*.py
    python scripts/run-tests.py -p "test_ci_*.py"    # the files a pattern matches
    python scripts/run-tests.py -j 2 -v              # two at a time, every file's full output

Every test file already runs alone (`python -m unittest discover -s scripts/tests -p <file>`), so the files are
independent processes. Measured on 2026-11-10 with 958 tests in 22 files: 394 s serially
(`python -m unittest discover -s scripts/tests`, which stays valid and is what a section's Test checkpoint quotes)
against 176 s four at a time on a busy PC. The largest files start first. Each child writes to a temporary file, so
no pipe can fill and stall it, and nothing is held in memory but the result lines.

A file that outlives `--timeout` has its whole process tree stopped (`taskkill /T /F` on Windows, the process
group elsewhere) and is reported as TIMEOUT; an interrupt stops every running file the same way. A file that ends
by itself is contained too: on Windows it runs in a job object that is closed when it ends, elsewhere its process
group is signalled, so a process a test started and never stopped ends with its file. `python -B` is passed on to
every file, so a run asked not to write bytecode leaves none (the mutation checks depend on that).

Exit 0 when every file passed, 1 when any failed or timed out, 2 on a usage error or when no file matched.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_START = ROOT / "scripts" / "tests"
DEFAULT_TIMEOUT = 1800  # seconds a single file may run; the slowest takes about a minute
MAX_DEFAULT_JOBS = 4  # the tests start git, node and PowerShell children of their own, so more gains little
RAN = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)
SKIPPED = re.compile(r"skipped=(\d+)")


def default_jobs():
    """Half the logical processors, at most MAX_DEFAULT_JOBS: timing-sensitive tests keep a core each."""
    return min(MAX_DEFAULT_JOBS, max(1, (os.cpu_count() or 2) // 2))


def stop_tree(process):
    """Stop a child and everything it started, and say so when that could not be done."""
    if process.poll() is not None:
        return
    try:
        if os.name == "nt":
            taskkill = os.path.join(os.environ.get("SystemRoot") or r"C:\Windows", "System32", "taskkill.exe")
            done = subprocess.run([taskkill, "/T", "/F", "/PID", str(process.pid)], stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL, timeout=30, check=False)
            if done.returncode != 0 and process.poll() is None:
                print(f"run-tests: taskkill exited {done.returncode} for the tree of pid {process.pid}",
                      file=sys.stderr)
        else:
            os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return  # it ended between the poll and the signal
    except (OSError, subprocess.SubprocessError) as error:
        print(f"run-tests: could not stop the tree of pid {process.pid}: {error}", file=sys.stderr)
    try:
        process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        process.kill()
        print(f"run-tests: pid {process.pid} outlived its tree stop and was killed alone; a child of it may remain",
              file=sys.stderr)


class Job:
    """A Windows job object that ends every process in it when closed, so what a test file started and left
    running ends with the file even though its parent, the file's own process, is already gone."""

    def __init__(self, process):
        import ctypes
        from ctypes import wintypes

        class Basic(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class Extended(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", Basic), ("IoInfo", ctypes.c_uint64 * 6),
                        ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

        kill_on_close, extended_limits = 0x2000, 9
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p,
                                                          wintypes.DWORD]
        self.kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handle = self.kernel32.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = Extended()
        limits.BasicLimitInformation.LimitFlags = kill_on_close
        if not (self.kernel32.SetInformationJobObject(self.handle, extended_limits, ctypes.byref(limits),
                                                      ctypes.sizeof(limits))
                and self.kernel32.AssignProcessToJobObject(self.handle, int(process._handle))):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def close(self):
        if self.handle:
            self.kernel32.CloseHandle(self.handle)
            self.handle = None


def end_leftovers(process, job):
    """End whatever a finished test file left running: close its job on Windows, signal its group elsewhere."""
    if job is not None:
        job.close()
    elif os.name != "nt":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return  # the usual case: the file left nothing behind


class Runner:
    def __init__(self, start, verbose, timeout):
        self.start, self.verbose, self.timeout = start, verbose, timeout
        self.live, self.lock, self.cancelled = set(), threading.Lock(), False

    def run(self, name):
        """One test file in its own process: (name, outcome, seconds, tests, skipped, output)."""
        command = [sys.executable, *(["-B"] if sys.dont_write_bytecode else []),
                   "-m", "unittest", "discover", "-s", str(self.start), "-p", name]
        if self.verbose:
            command.append("-v")
        handle, log = tempfile.mkstemp(prefix="office-tests-", suffix=".log")
        began, job = time.monotonic(), None
        try:
            with os.fdopen(handle, "wb") as out:
                with self.lock:
                    if self.cancelled:
                        return name, "CANCELLED", 0.0, 0, 0, ""
                    extra = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt"
                             else {"start_new_session": True})
                    process = subprocess.Popen(command, cwd=str(ROOT), stdout=out, stderr=subprocess.STDOUT,
                                               stdin=subprocess.DEVNULL, **extra)
                    self.live.add(process)
                if os.name == "nt":
                    try:
                        job = Job(process)
                    except OSError as error:  # the file still runs; say that it is not contained
                        print(f"run-tests: {name} runs outside a job object: {error}", file=sys.stderr)
                try:
                    code = process.wait(timeout=self.timeout)
                    outcome = "ok" if code == 0 else "FAIL"
                except subprocess.TimeoutExpired:
                    stop_tree(process)
                    outcome = "TIMEOUT"
                finally:
                    end_leftovers(process, job)
                    with self.lock:
                        self.live.discard(process)
            text = Path(log).read_text(encoding="utf-8", errors="replace")
        finally:
            try:
                os.unlink(log)
            except OSError as error:  # a process the file started still holds it open
                print(f"run-tests: left {log}: {error}", file=sys.stderr)
        if self.cancelled and outcome != "ok":
            outcome = "CANCELLED"
        ran = RAN.search(text)
        skipped = SKIPPED.search(text)
        return (name, outcome, time.monotonic() - began, int(ran.group(1)) if ran else 0,
                int(skipped.group(1)) if skipped else 0, text)

    def cancel(self):
        with self.lock:
            self.cancelled = True
            live = list(self.live)
        for process in live:
            stop_tree(process)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the tooling tests one file per process, in parallel.")
    parser.add_argument("-s", "--start-directory", default=str(DEFAULT_START), help="folder holding the test files")
    parser.add_argument("-p", "--pattern", default="test_*.py", help="glob the test file names must match")
    parser.add_argument("-j", "--jobs", type=int, default=default_jobs(), help="files to run at once")
    parser.add_argument("-v", "--verbose", action="store_true", help="print every file's full output")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="seconds one file may run")
    parser.add_argument("--list", action="store_true", help="print the files that would run, and stop")
    args = parser.parse_args(argv)
    start = Path(args.start_directory).resolve()
    if args.jobs < 1 or args.timeout <= 0:
        parser.error("--jobs must be 1 or more and --timeout more than 0")
    if not start.is_dir():
        print(f"run-tests: no such folder: {start}", file=sys.stderr)
        return 2
    files = sorted((p for p in start.glob(args.pattern) if p.is_file()), key=lambda p: (-p.stat().st_size, p.name))
    if not files:
        print(f"run-tests: no test file matches {args.pattern!r} in {start}", file=sys.stderr)
        return 2
    if args.list:
        for path in files:
            print(path.name)
        return 0

    runner, results, began = Runner(start, args.verbose, args.timeout), [], time.monotonic()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(runner.run, path.name) for path in files]
        try:
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                name, outcome, seconds, tests, skipped, _ = result
                note = f", {skipped} skipped" if skipped else ""
                print(f"{outcome:<9} {name:<36} {seconds:7.1f} s  {tests} tests{note}", flush=True)
        except KeyboardInterrupt:
            runner.cancel()
            for future in futures:
                future.cancel()
            print("run-tests: interrupted; every running file was stopped", file=sys.stderr)
            return 1
    results.sort(key=lambda r: r[0])
    bad = [r for r in results if r[1] != "ok"]
    for name, outcome, _, _, _, text in (results if args.verbose else bad):
        print(f"\n===== {name}: {outcome} =====\n{text.rstrip()}", flush=True)
    tests, skipped = sum(r[3] for r in results), sum(r[4] for r in results)
    note = f", {skipped} skipped" if skipped else ""
    print(f"\nRan {tests} tests in {len(results)} files in {time.monotonic() - began:.1f} s "
          f"({args.jobs} at a time){note}")
    if bad:
        print("FAILED: " + ", ".join(f"{r[0]} ({r[1]})" for r in bad))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
