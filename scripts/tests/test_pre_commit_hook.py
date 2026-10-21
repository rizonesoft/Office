"""scripts/hooks/pre-commit: a commit that stages TODO changes with a stale plan is refused before CI sees it."""
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
                    "scripts/hooks/pre-commit"):
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, self.root / rel)
        todo = self.root / "todo/00-workspace"
        todo.mkdir(parents=True)
        (todo / "TODO-01-a.md").write_text(todo_file([(1, "A", 0, "none", "--")]), encoding="utf-8")
        (todo / "INDEX.md").write_text("# Index\n- TODO-01-a.md\n", encoding="utf-8")
        (self.root / "todo/TODO-00-INDEX.md").write_text("# Index\n- 00-workspace/TODO-01-a.md\n", encoding="utf-8")
        self.sync()
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
        self.assertIn("unstaged changes", result.stderr)

    def test_a_commit_without_todo_changes_is_not_checked(self):
        (self.root / "notes.txt").write_text("x\n", encoding="utf-8")
        (self.root / "todo/00-workspace/TODO-01-a.md").write_text("broken\n", encoding="utf-8")  # unstaged, untouched
        self.git("add", "notes.txt")
        self.assertEqual(self.commit().returncode, 0)


if __name__ == "__main__":
    unittest.main()
