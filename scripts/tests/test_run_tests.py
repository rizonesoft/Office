# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The parallel test runner reports what its files did and leaves no process behind.

Each case runs `scripts/run-tests.py` over a throwaway folder of small test files, never over this folder, so the
runner is judged on results it cannot have arranged: a pass, a failure it must surface, a file that hangs with a
child of its own, and a pattern that matches nothing.
"""
import contextlib
import importlib.util
import io
import json
import os
import re
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

RUNNER = Path(__file__).resolve().parents[1] / "run-tests.py"
RUNNER_SECONDS = 120  # far more than any case needs; past it the runner's whole tree is stopped
HANG_SECONDS = 90  # how long the hanging fixture and its child sleep when nothing stops them: a bound, not forever

PASSING = "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_a(self):\n        pass\n\n" \
          "    def test_b(self):\n        pass\n"
FAILING = "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_wrong(self):\n" \
          "        self.assertEqual(1, 2, 'the fixture fails on purpose')\n"
HANGING = (
    "import subprocess, sys, time, unittest\n\n\nclass T(unittest.TestCase):\n    def test_hang(self):\n"
    f"        child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep({HANG_SECONDS})'])\n"
    "        with open(__file__ + '.pid', 'w', encoding='utf-8') as fh:\n"
    "            fh.write(str(child.pid))\n"
    f"        time.sleep({HANG_SECONDS})\n"
)
LEAVING = (  # starts a child, records it, and ends without stopping it: once passing, once failing
    "import subprocess, sys, unittest\n\n\nclass T(unittest.TestCase):\n    def test_leave(self):\n"
    f"        child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep({HANG_SECONDS})'])\n"
    "        with open(__file__ + '.pid', 'w', encoding='utf-8') as fh:\n"
    "            fh.write(str(child.pid))\n"
    "        self.assertTrue(PASSES, 'the fixture fails on purpose')\n"
)
WATCHING = (  # runs beside a LEAVING file and passes only if that file's child is gone while the run still goes on
    "import ctypes, os, pathlib, time, unittest\n\n\ndef alive(pid):\n"
    "    if os.name != 'nt':\n        try:\n            os.kill(pid, 0)\n        except ProcessLookupError:\n"
    "            return False\n        return True\n"
    "    k = ctypes.WinDLL('kernel32')\n    k.OpenProcess.restype = ctypes.c_void_p\n"
    "    k.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]\n"
    "    k.CloseHandle.argtypes = [ctypes.c_void_p]\n    h = k.OpenProcess(0x00100000, False, pid)\n"
    "    if not h:\n        return False\n    try:\n        return k.WaitForSingleObject(h, 0) == 0x102\n"
    "    finally:\n        k.CloseHandle(h)\n\n\nclass T(unittest.TestCase):\n    def test_watch(self):\n"
    "        mark = pathlib.Path(__file__).with_name('test_leave_ok.py.pid')\n"
    "        end = time.monotonic() + 30\n        while not mark.is_file() and time.monotonic() < end:\n"
    "            time.sleep(0.1)\n        time.sleep(0.3)\n        pid = int(mark.read_text(encoding='utf-8'))\n"
    "        while alive(pid) and time.monotonic() < end:\n            time.sleep(0.2)\n"
    "        self.assertFalse(alive(pid), 'the child outlived its file while the run went on')\n"
)
NO_BYTECODE = "import sys, unittest\n\n\nclass T(unittest.TestCase):\n    def test_flag(self):\n" \
              "        self.assertTrue(sys.dont_write_bytecode, 'the file was not started with -B')\n"


def stop_tree(pid):
    if os.name == "nt":
        taskkill = os.path.join(os.environ.get("SystemRoot") or r"C:\Windows", "System32", "taskkill.exe")
        subprocess.run([taskkill, "/T", "/F", "/PID", str(pid)], capture_output=True, timeout=30, check=False)
    else:
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def alive(pid):
    """Whether a process is still running, without signalling it (os.kill(pid, 0) would end it on Windows)."""
    if os.name == "nt":
        import ctypes
        synchronize, timeout = 0x00100000, 0x00000102
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.restype = ctypes.c_void_p
        kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = kernel32.OpenProcess(synchronize, False, pid)
        if not handle:
            return False
        try:
            return kernel32.WaitForSingleObject(handle, 0) == timeout
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def load_runner():
    """scripts/run-tests.py as a module, for the tests that change one of its constants."""
    spec = importlib.util.spec_from_file_location("run_tests_under_test", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*args):
    """The runner's exit code and output; its whole tree is stopped if it outlives RUNNER_SECONDS."""
    extra = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt"
             else {"start_new_session": True})
    process = subprocess.Popen([sys.executable, "-B", str(RUNNER), *args], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, text=True, encoding="utf-8",
                               errors="replace", **extra)
    try:
        out, _ = process.communicate(timeout=RUNNER_SECONDS)
    except subprocess.TimeoutExpired:
        stop_tree(process.pid)
        out, _ = process.communicate(timeout=30)
        raise AssertionError(f"the runner outlived {RUNNER_SECONDS} s:\n{out}") from None
    return process.returncode, out


def fixture(classes):
    """A test file whose classes each hold the named tests: {"A": ["test_a", ...], ...}."""
    return "import unittest\n\n\n" + "\n\n".join(
        f"class {cls}(unittest.TestCase):\n" + "".join(f"    def {name}(self):\n        pass\n\n" for name in names)
        for cls, names in classes.items())


INHERITED = ("import unittest\n\n\nclass Base(unittest.TestCase):\n    def test_shared(self):\n        pass\n\n\n"
             "class Child(Base):\n    pass\n")


class Shares(unittest.TestCase):
    """`--shard i/n` (D00 T03 §60): the shares together run every test once, weighed by the recorded seconds."""

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.dir = Path(folder.name)
        (self.dir / "test_big.py").write_text(
            fixture({"Slow": ["test_s1", "test_s2"], "Quick": ["test_q1"], "Other": ["test_o1", "test_o2"]}),
            encoding="utf-8")
        (self.dir / "test_heirs.py").write_text(INHERITED, encoding="utf-8")
        for name in ("test_a.py", "test_b.py", "test_c.py"):
            (self.dir / name).write_text(fixture({"T": ["test_one", "test_two"]}), encoding="utf-8")

    def durations(self, data):
        (self.dir / "durations.json").write_text(json.dumps(data), encoding="utf-8")

    def record(self):
        return json.loads((self.dir / "durations.json").read_text(encoding="utf-8"))

    RECORD = {"files": {"test_big.py": 100, "test_heirs.py": 70, "test_a.py": 9, "test_b.py": 2},
              "classes": {"test_big.py": {"Slow": 50, "Quick": 5, "Other": 15},
                          "test_heirs.py": {"Base": 30, "Child": 40}}}

    def listed(self, share):
        code, out = run("-s", str(self.dir), "--shard", share, "--list")
        self.assertEqual(code, 0, out)
        return out.split()

    def executed(self, *args):
        """Every test id the runner ran with these arguments, read from its verbose output."""
        code, out = run("-s", str(self.dir), "-v", *args)
        self.assertEqual(code, 0, out)
        return sorted(re.findall(r"(?m)^(\w+) \((\w+\.\w+)\.\w+\)", out))

    def test_every_test_runs_in_exactly_one_share_whatever_the_number_of_shares(self):
        self.durations(self.RECORD)
        whole = self.executed()
        self.assertEqual(len(whole), 13)  # 5 in test_big, 2 in test_heirs (one inherited), 6 in the three small files
        for count in (1, 2, 4, 7):
            together = []
            for share in range(1, count + 1):
                together += self.executed("--shard", f"{share}/{count}")
            self.assertEqual(sorted(together), whole, count)

    def test_the_same_tree_and_record_give_the_same_shares(self):
        self.durations(self.RECORD)
        self.assertEqual([self.listed(f"{i}/3") for i in (1, 2, 3)], [self.listed(f"{i}/3") for i in (1, 2, 3)])

    def test_the_recorded_seconds_decide_the_shares(self):
        self.durations(self.RECORD)
        self.assertEqual([self.listed(f"{i}/2") for i in (1, 2)],
                         [["test_big.py::Slow", "test_big.py::Other", "test_a.py", "test_c.py"],  # 50 + 15 + 9 + 5
                          ["test_heirs.py::Child", "test_heirs.py::Base", "test_big.py::Quick", "test_b.py"]])  # 77
        changed = json.loads(json.dumps(self.RECORD))
        changed["classes"]["test_big.py"] = {"Slow": 1, "Quick": 59, "Other": 15}
        self.durations(changed)
        self.assertEqual(self.listed("1/2")[0], "test_big.py::Quick")
        self.assertEqual(self.listed("1/2"), ["test_big.py::Quick", "test_big.py::Other", "test_c.py", "test_b.py"])
        self.assertIn("test_big.py::Slow", self.listed("2/2"))  # the unit that led share 1 is now the lightest

    def test_a_class_added_or_renamed_since_the_record_still_runs(self):
        self.durations(self.RECORD)
        (self.dir / "test_big.py").write_text(
            fixture({"Renamed": ["test_s1", "test_s2"], "Quick": ["test_q1"], "Other": ["test_o1", "test_o2"],
                     "Added": ["test_new"]}), encoding="utf-8")
        together = self.executed("--shard", "1/2") + self.executed("--shard", "2/2")
        self.assertEqual(sorted(together), self.executed())
        self.assertIn(("test_new", "test_big.Added"), together)
        self.assertIn(("test_s1", "test_big.Renamed"), together)

    def test_a_class_that_only_inherits_its_tests_is_a_unit_of_its_own(self):
        self.durations(self.RECORD)
        together = self.executed("--shard", "1/2") + self.executed("--shard", "2/2")
        self.assertEqual(sorted(t for t in together if t[1].startswith("test_heirs.")),
                         [("test_shared", "test_heirs.Base"), ("test_shared", "test_heirs.Child")])

    def test_a_class_recorded_as_slow_is_dealt_into_parts_that_together_run_all_its_tests(self):
        record = json.loads(json.dumps(self.RECORD))
        record["classes"]["test_big.py"] = {"Slow": 150, "Quick": 5, "Other": 15}  # 150 s: three parts of a 2-test
        self.durations(record)                                                    # class can only be two
        units = self.listed("1/1")
        self.assertIn("test_big.py::Slow#1/2", units)
        self.assertIn("test_big.py::Slow#2/2", units)
        self.assertNotIn("test_big.py::Slow", units)
        (self.dir / "test_big.py").write_text(
            fixture({"Slow": [f"test_s{n}" for n in range(1, 8)], "Quick": ["test_q1"], "Other": ["test_o1"]}),
            encoding="utf-8")
        self.assertEqual(sorted(u for u in self.listed("1/1") if "Slow" in u),
                         ["test_big.py::Slow#1/3", "test_big.py::Slow#2/3", "test_big.py::Slow#3/3"])
        together = []
        for share in (1, 2, 3):
            together += self.executed("--shard", f"{share}/3")
        self.assertEqual(sorted(together), self.executed())
        self.assertEqual(sum(1 for test, cls in together if cls == "test_big.Slow"), 7)
        self.assertGreater(len({share for share in (1, 2, 3)
                                if any("Slow#" in u for u in self.listed(f"{share}/3"))}), 1)

    def test_a_file_the_record_does_not_know_runs_whole(self):
        self.durations({"files": {}, "classes": {}})
        units = self.listed("1/1")
        self.assertEqual(sorted(units), ["test_a.py", "test_b.py", "test_big.py", "test_c.py", "test_heirs.py"])

    def test_without_a_record_the_shares_still_cover_every_file(self):
        self.assertEqual(sorted(self.listed("1/2") + self.listed("2/2")),
                         ["test_a.py", "test_b.py", "test_big.py", "test_c.py", "test_heirs.py"])

    def test_a_share_that_does_not_exist_is_a_usage_error(self):
        for bad in ("0/4", "5/4", "x", "2", "1/0", "-1/2"):
            code, out = run("-s", str(self.dir), "--shard", bad)
            self.assertEqual(code, 2, bad + out)
            self.assertIn("--shard takes I/N", out, bad)

    def test_a_record_that_names_a_missing_file_or_is_malformed_is_refused(self):
        self.durations({"files": {"test_gone.py": 3}, "classes": {}})
        code, out = run("-s", str(self.dir), "--shard", "1/2")
        self.assertEqual(code, 2, out)
        self.assertIn("test_gone.py", out)
        self.assertIn("--record-durations", out)
        for bad in ('{"files": {}}', '{"files": {"test_a.py": "slow"}, "classes": {}}', "not json", "[]"):
            (self.dir / "durations.json").write_text(bad, encoding="utf-8")
            code, out = run("-s", str(self.dir), "--shard", "1/2")
            self.assertEqual(code, 2, bad + out)
            self.assertIn("durations.json", out, bad)

    def test_recording_writes_every_file_run_and_keeps_the_rest(self):
        self.durations({"files": {"test_a.py": 999, "test_c.py": 999}, "classes": {}})
        code, out = run("-s", str(self.dir), "-p", "test_[ab]*.py", "--record-durations")
        self.assertEqual(code, 0, out)
        first = self.record()
        self.assertEqual(sorted(first["files"]), ["test_a.py", "test_b.py", "test_big.py", "test_c.py"])
        self.assertEqual(first["files"]["test_c.py"], 999)          # not run this time: kept as it was
        self.assertLess(first["files"]["test_a.py"], 60)            # run: its measured seconds replaced the old
        self.assertEqual(first["classes"], {})                      # nothing here is slow enough to split
        code, out = run("-s", str(self.dir), "-p", "test_[ab]*.py", "--record-durations")
        self.assertEqual(code, 0, out)
        second = self.record()
        self.assertEqual((sorted(second["files"]), second["classes"]), (sorted(first["files"]), first["classes"]))
        self.assertEqual(list(self.dir.glob(".durations-*")), [])   # no temporary file left behind

    def test_recording_drops_a_file_that_is_gone_and_the_shares_work_again(self):
        self.durations({"files": {"test_gone.py": 3, "test_a.py": 999, "test_c.py": 7},
                        "classes": {"test_gone.py": {"T": 3}}})
        self.assertEqual(run("-s", str(self.dir), "--shard", "1/2", "--list")[0], 2)  # refused while it is stale
        code, out = run("-s", str(self.dir), "-p", "test_a.py", "--record-durations")
        self.assertEqual(code, 0, out)
        record = self.record()
        self.assertEqual((sorted(record["files"]), record["classes"]), (["test_a.py", "test_c.py"], {}))
        self.assertEqual(record["files"]["test_c.py"], 7)
        self.assertEqual(run("-s", str(self.dir), "--shard", "1/2", "--list")[0], 0)

    def test_a_failed_run_records_nothing(self):
        self.durations({"files": {"test_a.py": 999}, "classes": {}})
        (self.dir / "test_b.py").write_text(FAILING, encoding="utf-8")
        code, out = run("-s", str(self.dir), "--record-durations")
        self.assertEqual(code, 1, out)
        self.assertEqual(self.record(), {"files": {"test_a.py": 999}, "classes": {}})
        self.assertNotIn("durations:", out)

    def test_a_slow_file_is_recorded_class_by_class_from_what_ran(self):
        slow = ("import time, unittest\n\n\nclass Sleeper(unittest.TestCase):\n    def test_wait(self):\n"
                "        time.sleep(0.4)\n\n\nclass Brisk(unittest.TestCase):\n    def test_wait(self):\n"
                "        time.sleep(0.05)\n")
        (self.dir / "test_slow.py").write_text(slow, encoding="utf-8")
        runner = load_runner()
        with mock.patch.object(runner, "SPLIT_OVER", 0.2), mock.patch.object(runner, "DEFAULT_START", self.dir):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.main(["-s", str(self.dir), "-p", "test_slow.py", "--record-durations"]), 0)
        classes = self.record()["classes"]["test_slow.py"]
        self.assertEqual(sorted(classes), ["Brisk", "Sleeper"])
        self.assertGreaterEqual(classes["Sleeper"], 0.4)
        self.assertLess(classes["Brisk"], classes["Sleeper"])

    def test_recording_and_a_share_cannot_be_asked_for_together(self):
        code, out = run("-s", str(self.dir), "--shard", "1/2", "--record-durations")
        self.assertEqual(code, 2, out)


class RunTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.dir = Path(folder.name)

    def write(self, name, text):
        (self.dir / name).write_text(text, encoding="utf-8")

    def test_passing_files_exit_zero_with_their_counts(self):
        self.write("test_one.py", PASSING)
        self.write("test_two.py", PASSING)
        code, out = run("-s", str(self.dir), "-j", "2")
        self.assertEqual(code, 0, out)
        self.assertIn("Ran 4 tests in 2 files", out)
        self.assertRegex(out, r"(?m)^ok +test_one\.py +\d+\.\d s  2 tests$")
        self.assertTrue(out.rstrip().endswith("OK"), out)

    def test_a_failing_file_fails_the_run_and_shows_its_output(self):
        self.write("test_good.py", PASSING)
        self.write("test_bad.py", FAILING)
        code, out = run("-s", str(self.dir))
        self.assertEqual(code, 1, out)
        self.assertIn("FAILED: test_bad.py (FAIL)", out)
        self.assertIn("the fixture fails on purpose", out)
        self.assertRegex(out, r"(?m)^ok +test_good\.py")
        self.assertNotIn("===== test_good.py", out)  # a passing file's output is shown only with -v

    def test_verbose_shows_every_file(self):
        self.write("test_good.py", PASSING)
        code, out = run("-s", str(self.dir), "-v")
        self.assertEqual(code, 0, out)
        self.assertIn("===== test_good.py: ok =====", out)
        self.assertIn("test_a", out)

    def test_a_file_past_its_timeout_is_stopped_with_its_children(self):
        self.write("test_hang.py", HANGING)
        pid_file = self.dir / "test_hang.py.pid"
        began = time.monotonic()
        code, out = run("-s", str(self.dir), "--timeout", "8")
        self.assertEqual(code, 1, out)
        self.assertIn("FAILED: test_hang.py (TIMEOUT)", out)
        self.assertLess(time.monotonic() - began, HANG_SECONDS - 10, "the runner waited for the hang to end")
        self.assertTrue(pid_file.is_file(), f"the fixture never started its child:\n{out}")
        child = int(pid_file.read_text(encoding="utf-8"))
        self.addCleanup(stop_tree, child)
        deadline = time.monotonic() + 15
        while alive(child) and time.monotonic() < deadline:
            time.sleep(0.2)
        self.assertFalse(alive(child), "the hanging file's own child outlived the runner's stop")

    def test_a_child_left_by_a_file_that_ended_is_stopped(self):
        for passes, code_wanted in ((True, 0), (False, 1)):
            with self.subTest(passes=passes):
                name = f"test_leave_{'ok' if passes else 'bad'}.py"
                self.write(name, f"PASSES = {passes}\n" + LEAVING)
                code, out = run("-s", str(self.dir), "-p", name)
                self.assertEqual(code, code_wanted, out)
                child = int((self.dir / (name + ".pid")).read_text(encoding="utf-8"))
                self.addCleanup(stop_tree, child)
                deadline = time.monotonic() + 15
                while alive(child) and time.monotonic() < deadline:
                    time.sleep(0.2)
                self.assertFalse(alive(child), "a child outlived the test file that started it")

    def test_a_left_child_ends_with_its_file_not_with_the_run(self):
        # Closing the runner ends every job anyway, so only a file still running can tell when the child ended.
        self.write("test_leave_ok.py", "PASSES = True\n" + LEAVING)
        self.write("test_watch.py", WATCHING)
        code, out = run("-s", str(self.dir), "-j", "2")
        pid_file = self.dir / "test_leave_ok.py.pid"
        if pid_file.is_file():
            self.addCleanup(stop_tree, int(pid_file.read_text(encoding="utf-8")))
        self.assertEqual(code, 0, out)

    def test_no_bytecode_is_passed_on_to_every_file(self):
        self.write("test_flag.py", NO_BYTECODE)
        code, out = run("-s", str(self.dir))  # run() starts the runner with -B
        self.assertEqual(code, 0, out)
        self.assertFalse(list(self.dir.rglob("*.pyc")), "a file run under -B wrote bytecode")

    def test_no_matching_file_is_a_usage_error(self):
        self.write("test_one.py", PASSING)
        code, out = run("-s", str(self.dir), "-p", "nothing_*.py")
        self.assertEqual(code, 2, out)
        self.assertIn("no test file matches", out)

    def test_list_names_the_files_largest_first_and_runs_nothing(self):
        self.write("test_a_small.py", PASSING)  # first by name, so an order by name fails this case
        self.write("test_z_large.py", PASSING + "# " + "x" * 400 + "\n")
        code, out = run("-s", str(self.dir), "--list")
        self.assertEqual(code, 0, out)
        self.assertEqual(out.split(), ["test_z_large.py", "test_a_small.py"])


if __name__ == "__main__":
    unittest.main()
