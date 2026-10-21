# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/verify-agent-tiers.mjs: agent frontmatter Claude Code cannot load is refused (D00 T03 §8).

Each refused case was measured against the `yaml` 2.9.1 and `js-yaml` 4.1.0 loaders, which both reject it
(docs/reviews/00-workspace/D00-T03-s8.md); the accepted ones load in both.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
VERIFIER = REPO / "scripts" / "verify-agent-tiers.mjs"
NODE = shutil.which("node")

AGENT = ("---\nname: probe\ndescription: {description}\nmodel: sonnet\ntools: Read, Grep\n{extra}---\n\n"
         "You are a probe.\n")
HOOKS = ("hooks:\n  PreToolUse:\n    - matcher: Bash\n      hooks:\n        - type: command\n"
         "          command: {command}\n")

REFUSED_DESCRIPTIONS = [
    "Use when: the user asks",          # ": " inside a plain scalar
    "ends with a colon:",               # a trailing ":"
    "@mention first",                   # reserved indicators
    "`backtick first",
    "%percent first",
    ",comma first",
    "]bracket first",
    "}brace first",
    "- dash space first",               # "-" or "?" followed by a space
    "? question space first",
]
ACCEPTED_DESCRIPTIONS = ["plain, with comma", "has a #hash inside", "a url https://example.com/x", "-dash no space"]
REFUSED_COMMANDS = ["echo: bad", "ends:", "- dash", "@at"]
ACCEPTED_COMMANDS = ["echo ok", "plain, fine", '"quoted: fine"']


class Frontmatter(unittest.TestCase):
    def setUp(self):
        # AGENTS.md runs this verifier with node after every agent change, so a missing node is a failure, not a skip.
        self.assertIsNotNone(NODE, "node is not on PATH; the agent tier verifier cannot run")

    def verify(self, description="A probe agent", extra=""):
        with tempfile.TemporaryDirectory() as tmp:
            agents = Path(tmp) / ".claude" / "agents"
            agents.mkdir(parents=True)
            (agents / "probe.md").write_text(AGENT.format(description=description, extra=extra), encoding="utf-8")
            return subprocess.run([NODE, str(VERIFIER)], cwd=tmp, capture_output=True, text=True)

    def test_a_plain_agent_passes(self):
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_top_level_value_yaml_cannot_load_is_refused(self):
        for description in REFUSED_DESCRIPTIONS:
            with self.subTest(description=description):
                result = self.verify(description=description)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("YAML can load", result.stderr)

    def test_a_top_level_value_yaml_loads_passes(self):
        for description in ACCEPTED_DESCRIPTIONS:
            with self.subTest(description=description):
                result = self.verify(description=description)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_hooks_value_yaml_cannot_load_is_refused(self):
        for command in REFUSED_COMMANDS:
            with self.subTest(command=command):
                result = self.verify(extra=HOOKS.format(command=command))
                self.assertEqual(result.returncode, 1, result.stdout)

    def test_a_hooks_value_yaml_loads_passes(self):
        for command in ACCEPTED_COMMANDS:
            with self.subTest(command=command):
                result = self.verify(extra=HOOKS.format(command=command))
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_this_repositorys_agents_pass(self):
        result = subprocess.run([NODE, str(VERIFIER)], cwd=REPO, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
