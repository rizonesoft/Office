#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Run the tooling tests one file per process, several files at a time.

    python scripts/run-tests.py                      # every scripts/tests/test_*.py
    python scripts/run-tests.py -p "test_ci_*.py"    # the files a pattern matches
    python scripts/run-tests.py -j 2 -v              # two at a time, every file's full output
    python scripts/run-tests.py --shard 2/4          # the second of four shares of the tests (CI runs the four)
    python scripts/run-tests.py --record-durations   # run, then write how long each file and class took

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

`--shard <i>/<n>` runs one of `n` shares (D00 T03 §60): CI runs the shares as parallel jobs, so a push's result
arrives in a fraction of the time and nobody needs the whole suite on one machine. The unit shared out is a test
file, or each test class of a file that `durations.json` (beside the tests) records as slow, or a part of a class
that is itself slow (its tests dealt out in name order), since a share can be no quicker than its longest unit. Units go, heaviest first, to the lightest share, by the recorded seconds; a file or
class the record does not know still runs, at a default weight. The classes of a split file are read from the file
itself every time, so a class added since the record was written is never left out.

Exit 0 when every file passed, 1 when any failed or timed out, 2 on a usage error or when no file matched.
"""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import re
import subprocess
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
DURATIONS = "durations.json"  # beside the test files: {"files": {name: seconds}, "classes": {name: {class: seconds}}}
SPLIT_OVER = 60.0  # seconds: a file slower than this is recorded class by class, and shared out class by class
DEFAULT_WEIGHT = 5.0  # seconds assumed for a file or class the record does not know
SHARD = re.compile(r"([0-9]+)/([0-9]+)")
SLOWEST = re.compile(r"^(\d+\.\d+)s\s+\S+ \(([\w.]+)\)\s*$", re.MULTILINE)  # a line of `unittest --durations`
LIST_CLASSES = ("import sys, unittest\n"
                "def walk(suite):\n"
                "    for item in suite:\n"
                "        if isinstance(item, unittest.TestSuite):\n"
                "            yield from walk(item)\n"
                "        else:\n"
                "            yield item\n"
                "tests = list(walk(unittest.defaultTestLoader.discover(sys.argv[1], pattern=sys.argv[2])))\n"
                "if any(type(t).__module__.startswith('unittest.') for t in tests):\n"
                "    sys.exit(3)\n"
                "print('\\n'.join(sorted({type(t).__name__ + ' ' + t._testMethodName for t in tests})))\n")
RAN = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)
SKIPPED = re.compile(r"skipped=(\d+)")


def default_jobs():
    """Half the logical processors, at most MAX_DEFAULT_JOBS: timing-sensitive tests keep a core each."""
    return min(MAX_DEFAULT_JOBS, max(1, (os.cpu_count() or 2) // 2))


class Usage(Exception):
    """A request the runner cannot carry out as given: exit 2 with the reason."""


def load_durations(start, names):
    """The record beside the tests, or an empty one. Refused when it is unreadable, of another shape, or names a
    test file that is no longer there: a stale record would weigh the shares by tests that do not exist."""
    path = start / DURATIONS
    if not path.is_file():
        return {"files": {}, "classes": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise Usage(f"{path} cannot be read: {error}") from None

    def seconds(value):
        return isinstance(value, dict) and all(
            isinstance(k, str) and type(v) in (int, float) and v >= 0 for k, v in value.items())
    if not (isinstance(data, dict) and set(data) == {"files", "classes"} and seconds(data["files"])
            and isinstance(data["classes"], dict) and all(seconds(v) for v in data["classes"].values())):
        raise Usage(f'{path} must hold {{"files": {{name: seconds}}, "classes": {{name: {{class: seconds}}}}}}')
    gone = sorted((set(data["files"]) | set(data["classes"])) - set(names))
    if gone:
        raise Usage(f"{path} names test files that are not in {start}: {', '.join(gone)}; "
                    f"run python scripts/run-tests.py --record-durations")
    return data


def classes_of(start, name):
    """{test class: its test names, sorted} for one file, read by loading it as unittest would; None when it cannot
    be loaded, so the file runs whole and fails where its error can be read."""
    try:
        done = subprocess.run([sys.executable, "-B", "-c", LIST_CLASSES, str(start), name], cwd=str(ROOT),
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
                              stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None
    found = {}
    for line in done.stdout.splitlines():
        cls, _, test = line.strip().partition(" ")
        if test:
            found.setdefault(cls, []).append(test)
    return found if done.returncode == 0 and found else None


def units_of(start, names, durations):
    """(file, part or None, seconds, -k patterns) for every unit of work: a file; each class of a file recorded as
    slow; or, for a class recorded as slow itself, each of the parts its tests are dealt into in name order."""
    units = []
    for name in names:
        recorded = durations["classes"].get(name)
        classes = classes_of(start, name) if recorded is not None else None
        if classes is None:
            units.append((name, None, durations["files"].get(name, DEFAULT_WEIGHT), ()))
            continue
        for cls, tests in sorted(classes.items()):
            seconds = recorded.get(cls, DEFAULT_WEIGHT)
            parts = min(len(tests), max(1, -(-int(seconds) // int(SPLIT_OVER))))
            if parts == 1:
                units.append((name, cls, seconds, (f"*.{cls}.*",)))
            else:
                units += [(name, f"{cls}#{k + 1}/{parts}", seconds / parts,
                           tuple(f"*.{cls}.{test}" for test in tests[k::parts])) for k in range(parts)]
    return units


def shares(units, count):
    """`count` lists of units: heaviest first, each to the share that is lightest so far (the lowest on a tie)."""
    out, load = [[] for _ in range(count)], [0.0] * count
    for unit in sorted(units, key=lambda u: (-u[2], u[0], u[1] or "")):
        lightest = load.index(min(load))
        out[lightest].append(unit)
        load[lightest] += unit[2]
    return out


def label(unit):
    return unit[0] if unit[1] is None else f"{unit[0]}::{unit[1]}"


def record(start, results, durations):
    """Write how long each file took, and each class of a file slower than SPLIT_OVER, keeping what is recorded for
    files this run left out. Through a temporary file and os.replace, so a reader never sees half a record."""
    for (name, _, _, _), _, seconds, _, _, text in results:
        durations["files"][name] = round(seconds, 1)
        if seconds > SPLIT_OVER:
            by_class = {}
            for spent, test_id in SLOWEST.findall(text):
                parts = test_id.split(".")
                if len(parts) >= 2:
                    by_class[parts[-2]] = by_class.get(parts[-2], 0.0) + float(spent)
            durations["classes"][name] = {cls: round(spent, 1) for cls, spent in sorted(by_class.items())}
        else:
            durations["classes"].pop(name, None)
    path = start / DURATIONS
    text = json.dumps({"files": dict(sorted(durations["files"].items())),
                       "classes": dict(sorted(durations["classes"].items()))}, indent=2) + "\n"
    handle, temporary = tempfile.mkstemp(dir=str(start), prefix=".durations-")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as out:
            out.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return path


class Runner:
    def __init__(self, start, verbose, timeout, durations=False):
        self.start, self.verbose, self.timeout, self.durations = start, verbose, timeout, durations
        self.stop = threading.Event()  # set by cancel(): every running file's tree is stopped at its next poll

    def run(self, unit):
        """One unit (a test file, or one class of it) in its own process tree:
        (unit, outcome, seconds, tests, skipped, output)."""
        name = unit[0]
        command = [sys.executable, *(["-B"] if sys.dont_write_bytecode else []),
                   "-m", "unittest", "discover", "-s", str(self.start), "-p", name]
        for pattern in unit[3]:
            command += ["-k", pattern]
        if self.durations:
            command += ["--durations", "0"]
        if self.verbose:
            command.append("-v")
        name = unit
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
                result, note = "FAIL", f"\nrun-tests: {label(unit)}: {error}\n"
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
    parser.add_argument("--shard", metavar="I/N", help="run share I of N of the tests (1 to N)")
    parser.add_argument("--record-durations", action="store_true",
                        help=f"after the run, write each file's seconds to {DURATIONS} beside the tests")
    args = parser.parse_args(argv)
    share = SHARD.fullmatch(args.shard or "1/1")
    if share is None or not 1 <= int(share[1]) <= int(share[2]):
        parser.error("--shard takes I/N with 1 <= I <= N, as in 2/4")
    if args.shard and args.record_durations:
        parser.error("--record-durations times whole files, so it cannot be given with --shard")
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
    names = [path.name for path in files]
    units = [(name, None, 0.0, ()) for name in names]
    try:
        if args.shard or args.record_durations:
            every = sorted(p.name for p in start.glob("test_*.py") if p.is_file())
            durations = load_durations(start, every)
        if args.shard:
            units = shares(units_of(start, names, durations), int(share[2]))[int(share[1]) - 1]
    except Usage as error:
        print(f"run-tests: {error}", file=sys.stderr)
        return 2
    if args.list:
        for unit in units:
            print(label(unit))
        return 0

    runner = Runner(start, args.verbose, args.timeout, durations=args.record_durations)
    results, began = [], time.monotonic()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(runner.run, unit) for unit in units]
        try:
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                unit, outcome, seconds, tests, skipped, _ = result
                note = f", {skipped} skipped" if skipped else ""
                print(f"{outcome:<9} {label(unit):<36} {seconds:7.1f} s  {tests} tests{note}", flush=True)
        except KeyboardInterrupt:
            runner.cancel()
            for future in futures:
                future.cancel()
            print("run-tests: interrupted; every running file was stopped", file=sys.stderr)
            return 1
    results.sort(key=lambda r: label(r[0]))
    bad = [r for r in results if r[1] != "ok"]
    for unit, outcome, _, _, _, text in (results if args.verbose else bad):
        print(f"\n===== {label(unit)}: {outcome} =====\n{text.rstrip()}", flush=True)
    tests, skipped = sum(r[3] for r in results), sum(r[4] for r in results)
    note = f", {skipped} skipped" if skipped else ""
    of = f", share {args.shard}" if args.shard else ""
    print(f"\nRan {tests} tests in {len({r[0][0] for r in results})} files in {time.monotonic() - began:.1f} s "
          f"({args.jobs} at a time{of}){note}")
    if bad:
        print("FAILED: " + ", ".join(f"{label(r[0])} ({r[1]})" for r in bad))
        return 1
    if args.record_durations:
        print(f"durations: {record(start, results, durations)}")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
