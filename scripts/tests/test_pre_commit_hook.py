# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/hooks/pre-commit: a commit that stages TODO changes with a stale plan is refused before CI sees it."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from test_todo_graph import todo_file  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which("git"), "needs git (which runs the hook with its own shell)")
class PreCommitHook(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        for rel in ("scripts/todo-graph.py", "scripts/lib/todo_graph.py", "scripts/review-dispatch.py",
                    "scripts/hooks/pre-commit", "scripts/inventory-report.py", "scripts/lib/inventory_claims.py",
                    "scripts/lib/word_absences.py", "scripts/lib/word_backstage.py"):
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, self.root / rel)
        (self.root / "scripts/hooks/pre-commit").chmod(0o755)  # git runs only an executable hook on Linux
        todo = self.root / "todo/00-workspace"
        todo.mkdir(parents=True)
        (todo / "TODO-01-a.md").write_text(todo_file([(1, "A", 0, "none", "--")]), encoding="utf-8")
        (todo / "INDEX.md").write_text("# Index\n- TODO-01-a.md\n", encoding="utf-8")
        (self.root / "todo/TODO-00-INDEX.md").write_text("# Index\n- 00-workspace/TODO-01-a.md\n", encoding="utf-8")
        self.sync()
        self.record("word.home", "tab")
        self.report()
        for args in (["init", "-q"], ["config", "user.email", "t@example.com"], ["config", "user.name", "T"],
                     ["config", "core.autocrlf", "false"], ["add", "-A"], ["commit", "-qm", "seed"],
                     ["config", "core.hooksPath", "scripts/hooks"]):
            self.git(*args)

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, check=True)

    def sync(self):
        subprocess.run([sys.executable, str(self.root / "scripts/todo-graph.py"), "plan", "--sync"], check=True,
                       capture_output=True)

    def record(self, rid, kind):
        """Add one record to the fixture's Word inventory."""
        path = self.root / "design/inventory/word/ribbon.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        records = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        path.write_text(json.dumps(records + [{"id": rid, "app": "word", "kind": kind, "label": rid}]),
                        encoding="utf-8")

    def report(self):
        subprocess.run([sys.executable, str(self.root / "scripts/inventory-report.py")], check=True,
                       capture_output=True)

    def commit(self):
        return subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "tick"], capture_output=True, text=True)

    def tick(self):
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        path.write_text(path.read_text(encoding="utf-8").replace("- [ ] Work.", "- [x] Work."), encoding="utf-8")

    def test_a_todo_change_with_a_stale_plan_is_refused(self):
        self.tick()
        self.git("add", "todo/00-workspace/TODO-01-a.md")
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("plan --sync", result.stderr)
        self.sync()
        self.git("add", "-A")
        self.assertEqual(self.commit().returncode, 0)

    def test_unstaged_todo_changes_are_refused(self):
        self.tick()
        self.sync()
        self.git("add", "todo/00-workspace/TODO-01-a.md")  # the synced plan is left unstaged
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("todo/ has unstaged or untracked changes", result.stderr)

    def test_an_untracked_review_file_beside_a_todo_change_is_refused(self):
        self.tick()
        self.sync()
        (self.root / "docs/reviews").mkdir(parents=True)
        (self.root / "docs/reviews/D00-T01-s1.json").write_text("{}" + chr(10), encoding="utf-8")  # left out of the commit
        self.git("add", "todo")
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("docs/reviews/ has unstaged or untracked changes", result.stderr)

    def test_an_ignored_review_file_beside_a_todo_change_is_refused(self):
        self.tick()
        self.sync()
        (self.root / "docs/reviews").mkdir(parents=True)
        (self.root / "docs/reviews/D00-T01-s1.json").write_text("{}" + chr(10), encoding="utf-8")
        (self.root / ".git/info/exclude").write_text("docs/reviews/" + chr(10), encoding="utf-8")
        self.git("add", "todo")
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("docs/reviews/ has unstaged or untracked changes", result.stderr)

    def test_the_hook_is_tracked_as_executable(self):
        mode = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-s", "scripts/hooks/pre-commit"],
                              capture_output=True, text=True, check=True).stdout.split()[0]
        self.assertEqual(mode, "100755")

    def test_a_new_record_without_its_report_is_refused(self):
        self.record("word.insert", "tab")
        self.git("add", "design/inventory/word/ribbon.json")
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("design/inventory/COVERAGE.md is stale", result.stderr)

    def test_a_regenerated_report_left_unstaged_is_refused(self):
        self.record("word.insert", "tab")
        self.report()
        self.git("add", "design/inventory/word/ribbon.json")  # the report regenerated but not staged
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("design/inventory/ has unstaged or untracked changes", result.stderr)

    def test_a_new_record_with_its_regenerated_report_is_committed(self):
        self.record("word.insert", "tab")
        self.report()
        self.git("add", "design/inventory/")
        self.assertEqual(self.commit().returncode, 0)

    def test_a_todo_commit_is_refused_while_the_report_is_stale(self):
        # A stamp changes what is implemented without touching the inventory; the report is checked for TODO
        # commits too. A stale report is committed past the hook, then an ordinary TODO commit is refused.
        self.record("word.insert", "tab")
        self.git("add", "design/inventory/word/ribbon.json")
        self.git("commit", "-qm", "stale", "--no-verify")
        self.tick()
        self.sync()
        self.git("add", "todo/")
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("design/inventory/COVERAGE.md is stale", result.stderr)

    def test_an_inventory_commit_with_an_unstaged_review_file_is_refused(self):
        # Round 1: the coverage check reads the TODO graph, which reads the receipts and findings in docs/reviews/.
        reviews = self.root / "docs/reviews"
        reviews.mkdir(parents=True, exist_ok=True)
        (reviews / "note.md").write_text("draft\n", encoding="utf-8")
        self.record("word.insert", "tab")
        self.report()
        self.git("add", "design/inventory/")
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("docs/reviews/ has unstaged or untracked changes", result.stderr)

    def test_a_commit_without_todo_changes_is_not_checked(self):
        (self.root / "notes.txt").write_text("x\n", encoding="utf-8")
        (self.root / "todo/00-workspace/TODO-01-a.md").write_text("broken\n", encoding="utf-8")  # unstaged, untouched
        self.git("add", "notes.txt")
        self.assertEqual(self.commit().returncode, 0)


if __name__ == "__main__":
    unittest.main()
