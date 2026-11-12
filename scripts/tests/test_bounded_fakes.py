# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""No fake or fixture in the tests loops without a bound (the global rules, "A child process never outlives its
test": a fixture that writes in a loop has a bound).

On 2026-11-12 a fake reviewer of `test_review_dispatch.py` that flooded its standard output in a `while True` loop
outlived the test run that started it and wrote 229 GB into the scratch drive until the drive was full. Every fake
now writes a bounded amount (a `for` loop over a fixed count) and then hangs or exits; this test fails on any
`while True` in a test file, including inside the source text of a fake a test writes out.
"""
from pathlib import Path
import re
import unittest

TESTS = Path(__file__).resolve().parent
UNBOUNDED = re.compile(r"while\s+(True|1)\s*:")


def offenders(folder=TESTS):
    found = []
    for path in sorted(folder.glob("*.py")):
        if path.name == Path(__file__).name:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if UNBOUNDED.search(line):
                found.append(f"{path.name}:{number}")
    return found


class BoundedFakes(unittest.TestCase):
    def test_no_test_file_loops_without_a_bound(self):
        self.assertEqual(offenders(), [])

    def test_an_unbounded_loop_in_a_fake_is_found(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "test_x.py").write_text('FAKE = """\nwhile True:\n    print(1)\n"""\n', encoding="utf-8")
            (Path(tmp) / "test_y.py").write_text("for _ in range(3):\n    pass\n", encoding="utf-8")
            self.assertEqual(offenders(Path(tmp)), ["test_x.py:2"])


if __name__ == "__main__":
    unittest.main()
