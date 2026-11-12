# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""One process-tree containment for every tool (D00 T03 §54).

`scripts/lib/process_tree.py` is the only place a Python tool may set up a Windows job object or stop a tree with
`taskkill`: three private copies once lived in the host check, the review dispatcher and the test runner, and they
shared a race (a job's member count reads 0 before its last member has exited) that only the shared helper fixed.

The check covers the Python tools under `scripts/` and `scripts/lib/`, the code that starts and contains children of
its own. Two other uses of `taskkill` are a different job and stay outside it: the launcher's `-Stop`
(`scripts/start-campaign.ps1`) ends another, already running launcher's tree by the process id that launcher
recorded, which no job of the stopping process holds; and the test files' teardown ends processes a test started
through the tool under test, after that tool's own containment is what the test examined.
"""
from pathlib import Path
import re
import shutil
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
HELPER = SCRIPTS / "lib" / "process_tree.py"
FORBIDDEN = re.compile(r"CreateJobObjectW|\btaskkill\b")


def offenders(scripts=SCRIPTS):
    """`path:line` of every forbidden use in the Python tools under `scripts`, the helper excepted."""
    helper = scripts / "lib" / "process_tree.py"
    found = []
    for path in sorted([*scripts.glob("*.py"), *(scripts / "lib").glob("*.py")]):
        if path == helper:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FORBIDDEN.search(line):
                found.append(f"{path.relative_to(scripts).as_posix()}:{number}")
    return found


class OneContainment(unittest.TestCase):
    def test_no_tool_contains_its_children_outside_the_helper(self):
        self.assertEqual(offenders(), [])

    def test_the_helper_is_where_the_containment_lives(self):
        self.assertIn("CreateJobObjectW", HELPER.read_text(encoding="utf-8"))

    def test_a_private_copy_is_found(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "lib").mkdir()
        (tmp / "lib" / "process_tree.py").write_text("CreateJobObjectW\n", encoding="utf-8")
        (tmp / "tool.py").write_text("x = 1\nsubprocess.run(['taskkill', '/T'])\n", encoding="utf-8")
        (tmp / "lib" / "other.py").write_text("kernel32.CreateJobObjectW(None, None)\n", encoding="utf-8")
        self.assertEqual(offenders(tmp), ["lib/other.py:1", "tool.py:2"])


if __name__ == "__main__":
    unittest.main()
