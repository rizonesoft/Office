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

Every file runs in its own process tree (`scripts/lib/process_tree.py`: on Windows a job object it joins before it
runs, elsewhere its own process group), so a file that outlives `--timeout` is stopped with everything it started
and reported as TIMEOUT, an interrupt stops every running file the same way, and a process a test started and never
stopped ends with its file even when the file ended by itself. `python -B` is passed on to
every file, so a run asked not to write bytecode leaves none (the mutation checks depend on that).

Exit 0 when every file passed, 1 when any failed or timed out, 2 on a usage error or when no file matched.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import re
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import process_tree  # found through scripts/lib, put on the path just above
DEFAULT_START = ROOT / "scripts" / "tests"
DEFAULT_TIMEOUT = 1800  # seconds a single file may run; the slowest takes about a minute
MAX_DEFAULT_JOBS = 4  # the tests start git, node and PowerShell children of their own, so more gains little
RAN = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)
SKIPPED = re.compile(r"skipped=(\d+)")


def default_jobs():
    """Half the logical processors, at most MAX_DEFAULT_JOBS: timing-sensitive tests keep a core each."""
    return min(MAX_DEFAULT_JOBS, max(1, (os.cpu_count() or 2) // 2))


class Runner:
    def __init__(self, start, verbose, timeout):
        self.start, self.verbose, self.timeout = start, verbose, timeout
        self.stop = threading.Event()  # set by cancel(): every running file's tree is stopped at its next poll

    def run(self, name):
        """One test file in its own process tree: (name, outcome, seconds, tests, skipped, output)."""
        command = [sys.executable, *(["-B"] if sys.dont_write_bytecode else []),
                   "-m", "unittest", "discover", "-s", str(self.start), "-p", name]
        if self.verbose:
            command.append("-v")
        if self.stop.is_set():
            return name, "CANCELLED", 0.0, 0, 0, ""
        handle, log = tempfile.mkstemp(prefix="office-tests-", suffix=".log")
        os.close(handle)
        began = time.monotonic()
        try:
            try:
                outcome = process_tree.run(command, cwd=str(ROOT), stdout_path=log, stderr_path=log,
                                           timeout=self.timeout, cancel=self.stop)
                result = {"time limit": "TIMEOUT", "cancelled": "CANCELLED"}.get(
                    outcome.stopped, "ok" if outcome.exit == 0 else "FAIL")
                note = ""
            except process_tree.TreeError as error:  # it never ran, or its tree would not end: a failure, said aloud
                result, note = "FAIL", f"\nrun-tests: {name}: {error}\n"
            text = Path(log).read_text(encoding="utf-8", errors="replace") + note
        finally:
            try:
                os.unlink(log)
            except OSError as error:  # a process the file started still holds it open
                print(f"run-tests: left {log}: {error}", file=sys.stderr)
        if self.stop.is_set() and result != "ok":
            result = "CANCELLED"
        ran = RAN.search(text)
        skipped = SKIPPED.search(text)
        return (name, result, time.monotonic() - began, int(ran.group(1)) if ran else 0,
                int(skipped.group(1)) if skipped else 0, text)

    def cancel(self):
        self.stop.set()

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
