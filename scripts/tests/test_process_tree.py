# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/process_tree.py: a child and everything it starts end together, with the strays named (D00 T03 §36)."""
import os
from pathlib import Path
import sys
import tempfile
import textwrap
import time
import unittest
from unittest import mock

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
            strays = tree.end()
        # The grandchild is the one stray this test made; elsewhere a process group cannot be listed by name.
        self.assertEqual([s for s in strays if s.startswith("python") or s == "(process group)"],
                         ["python.exe" if os.name == "nt" else "(process group)"], strays)
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
        self.assertEqual((outcome.exit, outcome.stopped), (3, None))
        # The child started nothing: no python process is left. What else Windows attaches to a console child is the
        # system's (the hosted CI runner shows one more member than a desktop PC), so it is named, not counted.
        self.assertEqual([s for s in outcome.strays if s.startswith("python")], [], outcome.strays)
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


class ForTheTools(unittest.TestCase):
    """What the host check, the review dispatcher and the test runner need of the helper (D00 T03 §54)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_piped_input_reaches_the_child(self):
        out = self.tmp / "out.txt"
        outcome = process_tree.run([sys.executable, "-c", "import sys; print(sys.stdin.read().upper())"],
                                   stdout_path=out, stdin_text="hello", timeout=60)
        self.assertEqual((outcome.exit, out.read_text().strip()), (0, "HELLO"))

    def test_a_child_that_never_reads_its_input_cannot_block_the_caller(self):
        # 8 MB of input, more than any pipe buffer, to a child that exits without reading.
        started = time.monotonic()
        outcome = process_tree.run([sys.executable, "-c", "import time; time.sleep(0.5)"],
                                   stdin_text="x" * 8_000_000, timeout=30)
        self.assertEqual(outcome.exit, 0)
        self.assertLess(time.monotonic() - started, 20)

    def test_standard_error_can_share_the_output_file(self):
        out = self.tmp / "both.txt"
        process_tree.run([sys.executable, "-c", "import sys; print('out'); sys.stdout.flush(); print('err', "
                          "file=sys.stderr)"], stdout_path=out, stderr_path=out, timeout=60)
        self.assertEqual(sorted(out.read_text().split()), ["err", "out"])

    def test_the_memory_limit_fails_a_tree_past_it_and_not_one_below(self):
        grandchild = "x = bytearray({} * 1024 * 1024); print(len(x))"
        parent = "import subprocess, sys; sys.exit(subprocess.run([sys.executable, '-c', {!r}]).returncode)"
        limit = 256 * 1024 * 1024
        over = process_tree.run([sys.executable, "-c", parent.format(grandchild.format(600))],
                                stdout_path=self.tmp / "over.txt", timeout=60, memory_bytes=limit)
        under = process_tree.run([sys.executable, "-c", parent.format(grandchild.format(16))],
                                 stdout_path=self.tmp / "under.txt", timeout=60, memory_bytes=limit)
        self.assertNotEqual(over.exit, 0)
        self.assertNotIn(str(600 * 1024 * 1024), (self.tmp / "over.txt").read_text())
        self.assertEqual(under.exit, 0)
        self.assertIn(str(16 * 1024 * 1024), (self.tmp / "under.txt").read_text())

    @unittest.skipUnless(os.name == "nt", "the start steps are the Windows job's")
    def test_each_failed_start_step_is_named_with_the_child_reaped_and_the_job_closed_once(self):
        for method, step in (("_create_job", "create job"), ("_configure_job", "configure job"),
                             ("_assign", "assign to job"), ("_resume", "resume")):
            with self.subTest(step):
                closed, children = [], []
                real_close, real_popen = process_tree.Tree._close_job, process_tree.subprocess.Popen

                def close(this, real=real_close):
                    if this.job is not None:
                        closed.append(1)
                    real(this)

                def popen(*args, **kwargs):
                    children.append(real_popen(*args, **kwargs))
                    return children[-1]

                with mock.patch.object(process_tree.Tree, method, side_effect=OSError("injected failure")), \
                        mock.patch.object(process_tree.Tree, "_close_job", close), \
                        mock.patch.object(process_tree.subprocess, "Popen", popen):
                    with self.assertRaises(process_tree.TreeError) as caught:
                        process_tree.run([sys.executable, "-c", "import time; time.sleep(60)"], timeout=30)
                self.assertEqual((caught.exception.step, caught.exception.why), (step, "injected failure"))
                self.assertEqual(str(caught.exception), f"{step}: injected failure")
                self.assertEqual(len(closed), 0 if step == "create job" else 1)
                for child in children:
                    self.assertIsNotNone(child.returncode, "the suspended child was not killed and reaped")
                    self.assertFalse(alive(child.pid))


if __name__ == "__main__":
    unittest.main()
