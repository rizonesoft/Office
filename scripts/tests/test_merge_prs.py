# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/merge_prs.py: green dependency pull requests merge one at a time, only when the clone is safe (D00 T03 §9)."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location("merge_prs", SCRIPTS / "merge_prs.py")
merge_prs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(merge_prs)

SHA = "a" * 40


def pr(number, **over):
    base = {"number": number, "author": {"login": "app/dependabot"}, "labels": [{"name": "dependencies"}],
            "isDraft": False, "headRefOid": f"{number:040d}", "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN",
            "statusCheckRollup": [{"name": "gates", "conclusion": "SUCCESS"}], "files": [{"path": ".github/workflows/ci.yml"}],
            "title": f"bump {number}"}
    base.update(over)
    return base


class Fake:
    """A scripted git and gh: the first matching prefix answers; every call is recorded."""

    def __init__(self, prs=(), status="", branch="main", head=SHA, upstream=SHA, fail=None):
        self.calls, self.prs, self.fail = [], list(prs), fail or {}
        self.answers = {("git", "status"): status, ("git", "fetch"): "", ("git", "pull"): "",
                        ("git", "rev-parse", "--abbrev-ref"): branch + "\n",
                        ("git", "rev-parse", "HEAD"): head + "\n", ("git", "rev-parse", "origin/main"): upstream + "\n"}

    def __call__(self, args, root):
        self.calls.append(list(args))
        key = " ".join(str(a) for a in args)
        for needle, (code, err) in self.fail.items():
            if needle in key:
                return code, "", err
        if args[:3] == ["gh", "pr", "list"]:
            return 0, json.dumps(self.prs), ""
        if args[:3] == ["gh", "pr", "merge"] or (len(args) > 2 and str(args[-1]) == "validate"):
            return 0, "", ""
        for prefix in sorted(self.answers, key=len, reverse=True):
            if tuple(args[:len(prefix)]) == prefix:
                return 0, self.answers[prefix], ""
        raise AssertionError(f"unexpected command {args}")

    def merges(self):
        return [c[3] for c in self.calls if c[:3] == ["gh", "pr", "merge"]]


def run_main(fake, argv=(), owner=None, started=()):
    out = io.StringIO()
    with mock.patch.object(merge_prs, "campaign_owner", return_value=owner), \
            mock.patch.object(merge_prs, "in_progress_sections", return_value=list(started)), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = merge_prs.main(list(argv), root=Path("."), runner=fake)
    return code, out.getvalue()


class Safety(unittest.TestCase):
    def test_each_unsafe_state_refuses_and_names_itself(self):
        cases = [(Fake(status=" M file.py\n"), {}, "uncommitted or untracked"),
                 (Fake(status="?? new.py\n"), {}, "uncommitted or untracked"),
                 (Fake(branch="feature"), {}, "not main"),
                 (Fake(head="b" * 40), {}, "is not origin/main"),
                 (Fake(), {"started": ["D00 T03 §9"]}, "a section is in progress: D00 T03 §9"),
                 (Fake(), {"owner": "other-session"}, "a campaign run is open for session other-session")]
        for fake, kw, message in cases:
            with self.subTest(message=message):
                code, out = run_main(fake, **kw)
                self.assertEqual(code, 2)
                self.assertIn(message, out)
                self.assertEqual(fake.merges(), [])

    def test_the_session_that_owns_the_campaign_may_merge(self):
        fake = Fake(prs=[pr(1)])
        code, out = run_main(fake, ["--session", "me"], owner="me")
        self.assertEqual(code, 0, out)
        self.assertEqual(fake.merges(), ["1"])

    def test_a_failed_git_or_gh_read_is_a_failure_even_when_skipping_unsafe_moments(self):
        for needle in ("git fetch", "gh pr list"):
            with self.subTest(failing=needle):
                code, out = run_main(Fake(fail={needle: (128, "no network")}), ["--skip-unsafe"])
                self.assertEqual(code, 3)
                self.assertIn(f"{needle} failed: no network", out)

    def test_the_scheduled_task_skips_an_unsafe_moment_without_failing(self):
        code, out = run_main(Fake(), ["--skip-unsafe"], owner="campaign-session")
        self.assertEqual(code, 0)
        self.assertIn("not merging: a campaign run is open", out)


class Eligibility(unittest.TestCase):
    def test_only_green_labelled_bot_pull_requests_are_chosen(self):
        prs = [pr(1), pr(2, author={"login": "someone"}), pr(3, labels=[{"name": "feature"}]), pr(4, isDraft=True),
               pr(5, mergeable="CONFLICTING"), pr(6, mergeStateStatus="BLOCKED"), pr(7, statusCheckRollup=[]),
               pr(8, statusCheckRollup=[{"name": "gates", "conclusion": "FAILURE"}]),
               pr(9, statusCheckRollup=[{"name": "gates", "conclusion": None, "status": "IN_PROGRESS"}]),
               pr(10, files=[{"path": "global.json"}]), pr(11, author={"login": "app/github-actions"},
                                                             labels=[{"name": "pins"}]),
               pr(12, statusCheckRollup=[{"context": "legacy", "state": "SUCCESS"}])]
        fake = Fake(prs=prs)
        code, out = run_main(fake)
        self.assertEqual(code, 0, out)
        self.assertEqual(fake.merges(), ["1", "11", "12"])
        for number in (2, 3, 4, 5, 6, 7, 8, 9, 10):
            self.assertIn(f"skipping #{number}:", out)


class Merging(unittest.TestCase):
    def test_each_merge_is_rebased_against_its_head_then_pulled_and_validated(self):
        fake = Fake(prs=[pr(2), pr(1)])
        code, _ = run_main(fake)
        self.assertEqual(code, 0)
        sequence = [c[:3] if c[0] in ("gh", "git") else ["validate"] for c in fake.calls
                    if c[:3] == ["gh", "pr", "merge"] or c[:2] == ["git", "pull"] or str(c[-1]) == "validate"]
        self.assertEqual(sequence, [["gh", "pr", "merge"], ["git", "pull", "--ff-only"], ["validate"]] * 2)
        first = next(c for c in fake.calls if c[:3] == ["gh", "pr", "merge"])
        self.assertEqual(first[3:], ["1", "--rebase", "--match-head-commit", f"{1:040d}"])  # lowest number first

    def test_the_first_failure_stops_and_leaves_the_rest_open(self):
        for needle in ("gh pr merge 1", "git pull", "validate"):
            with self.subTest(failing=needle):
                fake = Fake(prs=[pr(1), pr(2)], fail={needle: (1, "boom")})
                code, out = run_main(fake)
                self.assertEqual(code, 1)
                self.assertNotIn("2", fake.merges())
                self.assertIn("the rest stay open", out)

    def test_a_dry_run_merges_nothing(self):
        fake = Fake(prs=[pr(1)])
        code, out = run_main(fake, ["--dry-run"])
        self.assertEqual(code, 0)
        self.assertEqual(fake.merges(), [])
        self.assertIn("would merge #1", out)


class State(unittest.TestCase):
    def test_a_started_open_section_is_in_progress_and_a_stamped_one_is_not(self):
        from test_todo_graph import todo_file
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            todo = root / "todo" / "00-workspace"
            todo.mkdir(parents=True)
            text = todo_file([(1, "A", 0, "none", "--")]).replace("## 1. A\n\n", "## 1. A\n\n> **Started:** 2026-10-22T00:00:00Z\n\n")
            (todo / "TODO-01-a.md").write_text(text, encoding="utf-8")
            (todo / "INDEX.md").write_text("# Index\n- TODO-01-a.md\n", encoding="utf-8")
            (root / "todo" / "TODO-00-INDEX.md").write_text("# Index\n- 00-workspace/TODO-01-a.md\n", encoding="utf-8")
            self.assertEqual(merge_prs.in_progress_sections(root), ["D00 T01 §1"])

    def test_the_campaign_owner_is_read_from_the_run_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(merge_prs.campaign_owner(tmp))
            (Path(tmp) / "build").mkdir()
            (Path(tmp) / "build" / "claude-campaign-guard.json").write_text(json.dumps({"session_id": "s1"}))
            self.assertEqual(merge_prs.campaign_owner(tmp), "s1")


if __name__ == "__main__":
    unittest.main()
