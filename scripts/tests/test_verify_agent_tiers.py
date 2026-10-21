# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/verify-agent-tiers.mjs: agent frontmatter Claude Code cannot load is refused (D00 T03 §8).

The UNLOADABLE cases were measured against the `yaml` 2.9.1 and `js-yaml` 4.1.0 loaders: at least one of them
rejects each (docs/reviews/00-workspace/D00-T03-s8.md), and this check accepts only what both load. The ACCEPTED
ones load in both. The POLICY cases load in YAML but sit
outside the closed subset this check reads (tabs, block scalars and escapes in `hooks:`), so it refuses them by
design, never claiming YAML does.
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
TAB, NBSP, BACKSLASH = chr(9), chr(0xA0), chr(92)
UNLOADABLE_COMMANDS = ["echo: bad", "ends:", "- dash", "@at",
                       '"echo": bad',                    # a second key after a quoted one
                       '"' + BACKSLASH + 'q"',           # an escape YAML does not define
                       "|++"]                            # two chomping indicators
POLICY_COMMANDS = ["echo" + TAB + "x",                   # loads, but tabs are not read in hooks
                   '"' + BACKSLASH + 'n"',               # loads, but escapes are not decoded
                   "|"]                                  # loads, but block scalars are not read in hooks
ACCEPTED_COMMANDS = ["echo ok", "plain, fine", '"quoted: fine"', "'it''s fine'"]
# Top-level frontmatter bodies after "name: probe": at least one loader rejects each unloadable one; the accepted
# ones load in both.
UNLOADABLE_BODIES = ['description: "a"b"\nmodel: sonnet\n',
                     "model: sonnet\ndescription: |\n    first\n  second\n",
                     "model: sonnet\ndescription: |\n    \n  text\n",              # a deeper leading blank line
                     "model: sonnet\ndescription: a" + chr(1) + "b\n",           # a control character
                     "model: sonnet\nhooks:\n  -" + TAB + "@bad\n",              # a tab after a sequence dash
                     "model: sonnet\nhooks:\n  PreToolUse:\n    - matcher: Bash\n   hooks: value\n",  # misaligned
                     "model: sonnet\nhooks:\n  command: first\n  command: second\n",               # duplicate key
                     "model: sonnet\nhooks:\n  command: first\n  command : second\n",              # the same key
                     "model: sonnet\nhooks:\n  1: first\n  0x1: second\n",                         # one int key
                     "model: sonnet\n" + NBSP + "\n",                                             # NBSP is content
                     "model: sonnet\ndescription: |\n  text\n" + NBSP + "\n",
                     "model: sonnet\ndescription: |\n  text\n" + TAB + "\n",                      # yaml refuses it
                     "model: sonnet\nhooks:\n  true: first\n  TRUE: second\n",                    # one boolean key
                     "model: sonnet\ntrue: a\nTRUE: b\n"]
ACCEPTED_BODIES = ["description: hello:" + NBSP + "\nmodel: sonnet\n",   # a non-breaking space is content
                   "description: 'it''s fine'\nmodel: sonnet\n",
                   "model: sonnet\ndescription: |\n    first\n      deeper\n",
                   "model: sonnet\ndescription: |\n  text\n  " + TAB + "more\n",   # a tab past the indentation
                   "model: sonnet\nhooks:\n  command : ok\n",                       # a space before the colon
                   "model: sonnet\ndescription: |\n  text\n  " + TAB + "\n",        # a tab past the indentation
                   "model: sonnet\nhooks:\n  PreToolUse:\n  - matcher: Bash\n    hooks:\n    - type: command\n"
                   "      command: echo ok\n"]                                     # YAML's compact sequences


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
        for command in UNLOADABLE_COMMANDS:
            with self.subTest(command=command):
                result = self.verify(extra=HOOKS.format(command=command))
                self.assertEqual(result.returncode, 1, result.stdout)

    def test_a_hooks_value_outside_the_closed_subset_is_refused_by_policy(self):
        for command in POLICY_COMMANDS:
            with self.subTest(command=command):
                self.assertEqual(self.verify(extra=HOOKS.format(command=command)).returncode, 1)

    def test_a_hooks_value_yaml_loads_passes(self):
        for command in ACCEPTED_COMMANDS:
            with self.subTest(command=command):
                result = self.verify(extra=HOOKS.format(command=command))
                self.assertEqual(result.returncode, 0, result.stderr)

    def verify_body(self, body):
        with tempfile.TemporaryDirectory() as tmp:
            agents = Path(tmp) / ".claude" / "agents"
            agents.mkdir(parents=True)
            text = "---\nname: probe\ntools: Read, Grep\n" + body + "---\n\nYou are a probe.\n"
            (agents / "probe.md").write_bytes(text.encode("utf-8"))
            return subprocess.run([NODE, str(VERIFIER)], cwd=tmp, capture_output=True, text=True)

    def test_quoting_and_block_scalar_lines_yaml_refuses_are_refused(self):
        for body in UNLOADABLE_BODIES:
            with self.subTest(body=body):
                self.assertEqual(self.verify_body(body).returncode, 1)

    def test_quoting_and_block_scalar_lines_yaml_loads_pass(self):
        for body in ACCEPTED_BODIES:
            with self.subTest(body=body):
                result = self.verify_body(body)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_this_repositorys_agents_pass(self):
        result = subprocess.run([NODE, str(VERIFIER)], cwd=REPO, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
