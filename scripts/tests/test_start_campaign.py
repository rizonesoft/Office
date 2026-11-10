# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The campaign launcher starts Claude Code on the latest Opus, by alias (owner, 2026-11-10)."""

import re
import unittest
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[1] / "start-campaign.ps1"


class StartCampaignModelTest(unittest.TestCase):
    def setUp(self):
        self.text = LAUNCHER.read_text(encoding="utf-8")

    def test_model_is_the_opus_alias(self):
        self.assertRegex(self.text, r"(?m)^\$model = 'opus'$")

    def test_every_claude_start_passes_the_model(self):
        starts = [line.strip() for line in self.text.splitlines()
                  if "claude --" in line and "--dangerously-skip-permissions" in line]
        self.assertEqual(len(starts), 2, starts)  # the dry-run print and the real start
        for line in starts:
            self.assertIn("claude --model $model --dangerously-skip-permissions", line)

    def test_no_pinned_model_version_in_code(self):
        code = [line for line in self.text.splitlines() if not line.lstrip().startswith("#")]
        self.assertFalse([line for line in code if re.search(r"claude-(opus|sonnet|haiku|fable)-\d", line)])


if __name__ == "__main__":
    unittest.main()
