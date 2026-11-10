# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The parallel test runner reports what its files did and leaves no process behind.

Each case runs `scripts/run-tests.py` over a throwaway folder of small test files, never over this folder, so the
runner is judged on results it cannot have arranged: a pass, a failure it must surface, a file that hangs with a
child of its own, and a pattern that matches nothing.
"""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

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
