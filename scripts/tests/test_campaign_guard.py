"""scripts/campaign_guard.py: its built-in self-test drives the guard, the lock, and the Stop hook in fixture workspaces.

The self-test also reads the real process-plan skill for the guard steps (its `skill-*` cases). Those steps land in
D00 T03 §4, which tightens this test to a clean exit; until then every other case must pass.
"""
from pathlib import Path
import re
import subprocess
import sys
import unittest

REPO = Path(__file__).resolve().parents[2]
SKILL_TEXT_CASES_PENDING = False  # D00 T03 §4 landed the skill text: the self-test must exit 0


class GuardSelfTest(unittest.TestCase):
    def test_the_guard_self_test_passes(self):
        result = subprocess.run([sys.executable, str(REPO / "scripts" / "campaign_guard.py"), "--self-test"],
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        output = result.stdout + result.stderr
        summary = re.search(r"self-test: (\d+) cases, (\d+) failed", output)
        self.assertIsNotNone(summary, output[-4000:])
        failures = [line.split()[1] for line in output.splitlines() if line.startswith("FAIL ")]
        self.assertEqual(len(failures), int(summary.group(2)), output[-4000:])
        self.assertNotIn("Traceback", output, output[-4000:])
        if SKILL_TEXT_CASES_PENDING:
            unexpected = [name for name in failures if not name.startswith("skill-")]
            self.assertEqual(unexpected, [], output[-4000:])
            self.assertGreater(int(summary.group(1)), 100)
            # The self-test exits 1 exactly when a case failed, so the exit code must agree with the summary.
            self.assertEqual(result.returncode, 1 if failures else 0, output[-4000:])
        else:
            # Strict: every case ran and passed, and the exit code agrees, so neither a quiet failure nor an
            # empty run can pass.
            self.assertEqual((failures, int(summary.group(2))), ([], 0), output[-4000:])
            self.assertGreater(int(summary.group(1)), 100, output[-4000:])
            self.assertEqual(result.returncode, 0, output[-4000:])


if __name__ == "__main__":
    unittest.main()
