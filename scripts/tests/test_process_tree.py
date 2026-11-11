# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/process_tree.py: a child and everything it starts end together, with the strays counted (D00 T03 §36)."""
import os
from pathlib import Path
import sys
import tempfile
import textwrap
import time
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import process_tree

# A parent that starts a sleeping grandchild, writes the grandchild's pid and then either sleeps or exits at once.
PARENT = textwrap.dedent("""
    import subprocess, sys, time
    grandchild = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    with open(sys.argv[1], "w") as f:
        f.write(str(grandchild.pid))
    if sys.argv[2] == "sleep":
        time.sleep(120)
""")


def alive(pid):
    """Whether process `pid` is still running (never signals it)."""
    if os.name == "nt":
        import ctypes
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.restype = ctypes.c_void_p
        handle = kernel32.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
        if not handle:
            return False
        try:
            return kernel32.WaitForSingleObject(ctypes.c_void_p(handle), 0) == 0x102  # WAIT_TIMEOUT: still running
        finally:
            kernel32.CloseHandle(ctypes.c_void_p(handle))
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    try:  # a zombie is gone in every way that matters here
        with open(f"/proc/{pid}/stat") as f:
            return f.read().split(") ")[-1][:1] != "Z"
    except OSError:
        return True


def wait_for(path, seconds=30):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if path.is_file() and path.read_text().strip():
            return int(path.read_text())
        time.sleep(0.05)
    raise AssertionError(f"{path} was never written")


class TreeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.script = self.tmp / "parent.py"
        self.script.write_text(PARENT)
        self.pidfile = self.tmp / "grandchild.pid"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_end_stops_the_child_and_its_grandchild(self):
        with process_tree.Tree() as tree:
            child = tree.start([sys.executable, str(self.script), str(self.pidfile), "sleep"])
            grandchild = wait_for(self.pidfile)
            self.assertTrue(alive(grandchild))
            tree.end()
        self.assertIsNotNone(child.returncode)
        self.assertFalse(alive(child.pid))
        self.assertFalse(alive(grandchild))

    def test_a_grandchild_left_by_an_exited_child_is_a_stray_and_is_stopped(self):
        with process_tree.Tree() as tree:
            child = tree.start([sys.executable, str(self.script), str(self.pidfile), "exit"])
            grandchild = wait_for(self.pidfile)
            child.wait(timeout=30)
            self.assertTrue(alive(grandchild))
            self.assertEqual(tree.end(), 1)
        self.assertFalse(alive(grandchild))

    def test_leaving_the_block_ends_the_tree_even_without_end(self):
        with process_tree.Tree() as tree:
            tree.start([sys.executable, str(self.script), str(self.pidfile), "sleep"])
            grandchild = wait_for(self.pidfile)
        self.assertFalse(alive(grandchild))

    def test_a_tree_holds_one_child(self):
        with process_tree.Tree() as tree:
            tree.start([sys.executable, "-c", "pass"])
            with self.assertRaises(process_tree.TreeError):
                tree.start([sys.executable, "-c", "pass"])


class RunTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_exit_code_input_and_output(self):
        stdin = self.tmp / "in.txt"
        stdin.write_text("hello")
        out, err = self.tmp / "out.txt", self.tmp / "err.txt"
        outcome = process_tree.run([sys.executable, "-c", "import sys; print(sys.stdin.read()); sys.exit(3)"],
                                   stdin_path=stdin, stdout_path=out, stderr_path=err, timeout=60)
        self.assertEqual((outcome.exit, outcome.stopped, outcome.strays), (3, None, 0))
        self.assertEqual(out.read_text().strip(), "hello")

    def test_time_limit_stops_the_tree(self):
        script = self.tmp / "parent.py"
        script.write_text(PARENT)
        pidfile = self.tmp / "grandchild.pid"
        outcome = process_tree.run([sys.executable, str(script), str(pidfile), "sleep"], timeout=3)
        self.assertEqual((outcome.exit, outcome.stopped), (None, "time limit"))
        self.assertLess(outcome.seconds, 30)
        self.assertFalse(alive(int(pidfile.read_text())))

    def test_output_limit_stops_a_flood(self):
        # Bounded: the flood writes at most 64 MB over about 10 s even if nothing stopped it, then sleeps.
        flood = "import sys, time\nfor _ in range(1024):\n    sys.stdout.write('x' * 65536)\n    sys.stdout.flush()\n" \
                "    time.sleep(0.01)\ntime.sleep(120)\n"
        out = self.tmp / "out.txt"
        outcome = process_tree.run([sys.executable, "-c", flood], stdout_path=out, timeout=60,
                                   max_bytes=1024 * 1024)
        self.assertEqual(outcome.stopped, "output limit")
        self.assertIsNone(outcome.exit)
        self.assertLess(outcome.seconds, 8)
        self.assertLess(out.stat().st_size, 32 * 1024 * 1024)

    def test_the_output_files_are_bounded_together(self):
        # 600 KB to each stream: neither alone passes 1 MB, together they do. Bounded at 1.2 MB, then it sleeps.
        split = "import sys, time\nsys.stdout.write('x' * 600000); sys.stdout.flush()\n" \
                "sys.stderr.write('y' * 600000); sys.stderr.flush()\ntime.sleep(120)\n"
        outcome = process_tree.run([sys.executable, "-c", split], stdout_path=self.tmp / "out.txt",
                                   stderr_path=self.tmp / "err.txt", timeout=60, max_bytes=1024 * 1024)
        self.assertEqual(outcome.stopped, "output limit")
        self.assertLess(outcome.seconds, 30)

    def test_a_watched_file_counts_toward_the_output_limit(self):
        side = self.tmp / "side.log"
        writer = f"open(r'{side}', 'w').write('y' * 2048); import time; time.sleep(120)"
        outcome = process_tree.run([sys.executable, "-c", writer], timeout=60, max_bytes=1024, watched=[side])
        self.assertEqual(outcome.stopped, "output limit")


if __name__ == "__main__":
    unittest.main()
