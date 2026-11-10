# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""No agent definition or skill tells a session to make a git worktree (AGENTS.md, Working rules: the owner allows no
worktrees; a second copy of the tree is a scratch clone). On 2026-11-11 `mutation-tester` made one because its own
definition said to."""
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
WORKTREE = re.compile(r"git(?:\s+-C\s+\S+)?\s+worktree\s+add\b")


def instructions():
    yield from sorted((REPO / ".claude/agents").glob("*.md"))
    yield from sorted((REPO / ".claude/skills").glob("*/**/*.md"))


class NoWorktrees(unittest.TestCase):
    def test_no_instruction_makes_a_worktree(self):
        found = [f"{path.relative_to(REPO).as_posix()}:{n}"
                 for path in instructions()
                 for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
                 if WORKTREE.search(line) and "Never run `git worktree add`" not in line]
        self.assertEqual(found, [])

    def test_the_pattern_finds_a_worktree_command(self):
        for line in ("`git worktree add --detach x HEAD`", "git -C repo worktree add y"):
            self.assertIsNotNone(WORKTREE.search(line), line)
        self.assertIsNone(WORKTREE.search("git worktree list"))

    def test_there_are_instructions_to_read(self):
        self.assertIn(REPO / ".claude/agents/mutation-tester.md", list(instructions()))


if __name__ == "__main__":
    unittest.main()
