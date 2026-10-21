# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/merge_prs.py: green dependency pull requests merge one at a time, only into a safe clone (D00 T03 §9)."""
import contextlib
import copy
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
            "isDraft": False, "baseRefName": "main", "headRefOid": f"{number:040d}", "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN", "statusCheckRollup": [{"name": "gates", "conclusion": "SUCCESS"}],
            "changedFiles": 1, "title": f"bump {number}", "state": "OPEN", "files": [".github/workflows/ci.yml"]}
    base.update(over)
    return base


class Fake:
    """A scripted git and gh over a little GitHub: pull requests can change between the listing and their merge,
    a merge must name the current head, and every call is recorded."""

    def __init__(self, prs=(), status="", branch="main", head=SHA, upstream=SHA, fail=None, views=None,
                 after_merge=None, during_files=None, before_merge=None, after_pull=None,
                 origin="https://github.com/rizonesoft/Office.git"):
        self.calls, self.fail = [], fail or {}
        self.during_files = during_files   # called while the file list is read: a change during the slow reads
        self.before_merge = before_merge   # called as the merge request arrives: a change after the last read
        self.after_pull = after_pull       # called after a pull: a push by someone else between merges
        self.prs = {p["number"]: p for p in prs}
        self.views = views or {}           # number -> the fresh state `gh pr view` returns instead
        self.after_merge = after_merge     # called after each successful merge, to change the clone
        # "remote" is main on GitHub; "upstream" is the local origin/main ref, which only a fetch moves.
        self.state = {"status": status, "branch": branch, "head": head, "upstream": upstream, "remote": upstream}
        self.merged = []
        self.origin = origin

    def __call__(self, args, root):
        self.calls.append(list(args))
        key = " ".join(str(a) for a in args)
        for needle, (code, err) in self.fail.items():
            if needle in key:
                return code, "", err
        if args[:3] == ["gh", "pr", "list"]:
            listed = [{k: v for k, v in p.items() if k not in ("files", "state")} for p in self.prs.values()]
            return 0, json.dumps(listed), ""
        if args[:3] == ["gh", "pr", "view"]:
            number = int(args[3])
            view = copy.deepcopy(self.views.get(number, self.prs[number]))
            view.pop("files", None)
            return 0, json.dumps(view), ""
        if args[:2] == ["gh", "api"]:
            number = int(next(a for a in args if str(a).startswith("repos/")).split("/")[-2])
            if self.during_files:
                self.during_files(self)
            files = self.views.get(number, self.prs[number])["files"]
            pairs = [entry if isinstance(entry, (list, tuple)) else (entry, "") for entry in files]
            return 0, "".join(json.dumps(list(pair)) + "\n" for pair in pairs), ""
        if args[:3] == ["gh", "pr", "merge"]:
            number, sha = int(args[3]), args[args.index("--match-head-commit") + 1]
            if self.before_merge:
                self.before_merge(self)
            current = self.views.get(number, self.prs[number])["headRefOid"]
            if sha != current:
                return 1, "", "head commit does not match"
            self.merged.append(number)
            if self.after_merge:
                self.after_merge(self)
            return 0, "", ""
        if args[:4] == ["git", "remote", "get-url", "origin"]:
            return 0, self.origin + "\n", ""
        if args[:2] == ["git", "fetch"]:
            self.state["upstream"] = self.state["remote"]
            return 0, "", ""
        if args[:2] == ["git", "pull"]:  # a pull fetches and fast-forwards: HEAD and origin/main meet the remote
            self.state.update(head=self.state["remote"], upstream=self.state["remote"])
            if self.after_pull:
                self.after_pull(self)
            return 0, "", ""
        if str(args[-1]) == "validate":
            return 0, "", ""
        if args[:2] == ["git", "status"]:
            return 0, self.state["status"], ""
        if args[:3] == ["git", "rev-parse", "--abbrev-ref"]:
            return 0, self.state["branch"] + "\n", ""
        if args[:3] == ["git", "rev-parse", "HEAD"]:
            return 0, self.state["head"] + "\n", ""
        if args[:3] == ["git", "rev-parse", "origin/main"]:
            return 0, self.state["upstream"] + "\n", ""
        raise AssertionError(f"unexpected command {args}")


def run_main(fake, argv=(), owner=None, started=()):
    out = io.StringIO()
    with mock.patch.object(merge_prs, "campaign_owner", return_value=owner), \
            mock.patch.object(merge_prs, "in_progress_sections", return_value=list(started)), \
            mock.patch.object(merge_prs, "guard_lock", side_effect=lambda root: contextlib.nullcontext()), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = merge_prs.main(list(argv), root=Path("."), runner=fake)
    return code, out.getvalue()


class Safety(unittest.TestCase):
    def test_each_unsafe_state_refuses_and_names_itself(self):
        cases = [(Fake(prs=[pr(1)], status=" M file.py\n"), {}, "uncommitted or untracked"),
                 (Fake(prs=[pr(1)], status="?? new.py\n"), {}, "uncommitted or untracked"),
                 (Fake(prs=[pr(1)], branch="feature"), {}, "not main"),
                 (Fake(prs=[pr(1)], head="b" * 40), {}, "is not origin/main"),
                 (Fake(prs=[pr(1)]), {"started": ["D00 T03 §9"]}, "a section is in progress: D00 T03 §9"),
                 (Fake(prs=[pr(1)]), {"owner": "other-session"}, "a campaign run is open for session other-session")]
        for fake, kw, message in cases:
            with self.subTest(message=message):
                code, out = run_main(fake, **kw)
                self.assertEqual(code, 2)
                self.assertIn(message, out)
                self.assertEqual(fake.merged, [])

    def test_the_session_that_owns_the_campaign_may_merge(self):
        fake = Fake(prs=[pr(1)])
        code, out = run_main(fake, ["--session", "me"], owner="me")
        self.assertEqual(code, 0, out)
        self.assertEqual(fake.merged, [1])

    def test_a_clone_made_unsafe_mid_batch_stops_the_next_merge(self):
        fake = Fake(prs=[pr(1), pr(2)], after_merge=lambda f: f.state.update(status=" M edited.py\n"))
        code, out = run_main(fake)
        self.assertEqual(code, 2)
        self.assertEqual(fake.merged, [1])
        self.assertIn("merged #1; not merging further: the working tree", out)

    def test_main_moved_by_someone_else_mid_batch_stops_the_next_merge(self):
        fake = Fake(prs=[pr(1), pr(2)], after_pull=lambda f: f.state.update(remote="c" * 40))  # after our pull
        code, out = run_main(fake)
        self.assertEqual(code, 2)
        self.assertEqual(fake.merged, [1])
        self.assertIn("is not origin/main", out)

    def test_each_merge_holds_the_run_guard_lock(self):
        events = []

        @contextlib.contextmanager
        def lock(root):
            events.append("lock")
            yield
            events.append("unlock")

        fake = Fake(prs=[pr(1), pr(2)], after_merge=lambda f: events.append(f"merged {f.merged[-1]}"))
        with mock.patch.object(merge_prs, "campaign_owner", return_value=None), \
                mock.patch.object(merge_prs, "in_progress_sections", return_value=[]), \
                mock.patch.object(merge_prs, "guard_lock", side_effect=lock), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(merge_prs.main([], root=Path("."), runner=fake), 0)
        self.assertEqual(events, ["lock", "merged 1", "unlock", "lock", "merged 2", "unlock"])

    def test_a_busy_run_guard_is_an_unsafe_moment_not_a_crash(self):
        import campaign_guard

        def busy(root):
            raise campaign_guard.GuardError("the guard lock is held by another process")

        out = io.StringIO()
        with mock.patch.object(merge_prs, "campaign_owner", return_value=None), \
                mock.patch.object(merge_prs, "in_progress_sections", return_value=[]), \
                mock.patch.object(merge_prs, "guard_lock", side_effect=busy), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = merge_prs.main(["--skip-unsafe"], root=Path("."), runner=Fake(prs=[pr(1)]))
        self.assertEqual(code, 0)
        self.assertIn("the run guard is busy", out.getvalue())

    def test_a_git_or_gh_that_cannot_run_or_read_is_a_failure_even_when_skipping_unsafe_moments(self):
        for needle in ("git fetch", "gh pr list", "gh pr view", "gh api"):
            with self.subTest(failing=needle):
                code, out = run_main(Fake(prs=[pr(1)], fail={needle: (127, "cannot run")}), ["--skip-unsafe"])
                self.assertEqual(code, 3)
                self.assertIn("cannot run", out)

    def test_a_missing_executable_is_reported_not_raised(self):
        code, _, err = merge_prs.run(["no-such-command-merge-prs"], ".")
        self.assertEqual(code, 127)
        self.assertIn("cannot run", err)

    def test_an_open_campaign_is_a_quiet_skip_even_when_github_cannot_be_reached(self):
        code, out = run_main(Fake(prs=[pr(1)], fail={"git fetch": (1, "network unavailable")}), ["--skip-unsafe"],
                             owner="active-session")
        self.assertEqual(code, 0)
        self.assertIn("a campaign run is open", out)

    def test_an_off_main_checkout_is_a_quiet_skip_even_when_github_cannot_be_reached(self):
        code, out = run_main(Fake(prs=[pr(1)], branch="feature", fail={"git fetch": (1, "network unavailable")}),
                             ["--skip-unsafe"])
        self.assertEqual(code, 0)
        self.assertIn("not main", out)

    def test_every_github_call_names_github_com_and_the_repository_origin_points_at(self):
        for origin in ("https://github.com/rizonesoft/Office.git", "git@github.com:rizonesoft/Office.git",
                       "https://github.com/rizonesoft/Office", "ssh://git@github.com/rizonesoft/Office.git",
                       "https://user@github.com/rizonesoft/Office.git"):
            with self.subTest(origin=origin):
                fake = Fake(prs=[pr(1)], origin=origin)
                with mock.patch.dict("os.environ", {"GH_REPO": "someone/elsewhere", "GH_HOST": "ghe.example"}):
                    self.assertEqual(run_main(fake)[0], 0)
                gh_calls = [c for c in fake.calls if c[0] == "gh"]
                self.assertTrue(gh_calls)
                for call in gh_calls:
                    if call[1] == "api":  # an API path names the repository, --hostname the host
                        self.assertEqual(call[call.index("--hostname") + 1], "github.com", call)
                        self.assertTrue(any(str(a).startswith("repos/rizonesoft/Office/") for a in call), call)
                    else:
                        self.assertEqual(call[call.index("--repo") + 1], "github.com/rizonesoft/Office", call)

    def test_an_origin_not_on_github_com_is_unreadable(self):
        for origin in ("https://gitlab.example/x/y.git", "https://notgithub.com/rizonesoft/Office.git",
                       "https://mirror.example/github.com/rizonesoft/Office.git", "git@github.com.evil:x/y.git",
                       "https://github.com.evil/rizonesoft/Office.git"):
            with self.subTest(origin=origin):
                fake = Fake(prs=[pr(1)], origin=origin)
                code, out = run_main(fake)
                self.assertEqual(code, 3)
                self.assertIn("is not a github.com repository", out)
                self.assertEqual(fake.merged, [])

    def test_command_output_echoed_in_a_failure_masks_url_credentials(self):
        secret = "SYNTHETIC-TOKEN-1111"
        message = f"fatal: unable to access 'https://user:{secret}@github.com/rizonesoft/Office.git/': 403"
        for needle in ("git fetch", "gh pr merge 1", "git pull"):
            with self.subTest(failing=needle):
                code, out = run_main(Fake(prs=[pr(1)], fail={needle: (128, message)}))
                self.assertNotIn(secret, out)
                self.assertIn("https://***@github.com/", out)

    def test_a_rejected_origin_never_prints_its_credentials(self):
        secret = "SYNTHETIC-TOKEN-0000"
        for origin in (f"https://user:{secret}@gitlab.example/x/y.git", f"https://{secret}@notgithub.com/o/r.git"):
            with self.subTest(origin=origin):
                code, out = run_main(Fake(prs=[pr(1)], origin=origin))
                self.assertEqual(code, 3)
                self.assertNotIn(secret, out)

    def test_the_scheduled_task_skips_an_unsafe_moment_without_failing(self):
        code, out = run_main(Fake(prs=[pr(1)]), ["--skip-unsafe"], owner="campaign-session")
        self.assertEqual(code, 0)
        self.assertIn("not merging further: a campaign run is open", out)


class Eligibility(unittest.TestCase):
    def test_only_green_labelled_bot_pull_requests_on_main_are_chosen(self):
        prs = [pr(1), pr(2, author={"login": "someone"}), pr(3, labels=[{"name": "feature"}]), pr(4, isDraft=True),
               pr(5, mergeable="CONFLICTING"), pr(6, mergeStateStatus="BLOCKED"), pr(7, statusCheckRollup=[]),
               pr(8, statusCheckRollup=[{"name": "gates", "conclusion": "FAILURE"}]),
               pr(9, statusCheckRollup=[{"name": "gates", "conclusion": None, "status": "IN_PROGRESS"}]),
               pr(10, files=["global.json"]), pr(11, author={"login": "app/github-actions"}, labels=[{"name": "pins"}]),
               pr(12, statusCheckRollup=[{"context": "legacy", "state": "SUCCESS"}]), pr(13, baseRefName="release")]
        fake = Fake(prs=prs)
        code, out = run_main(fake)
        self.assertEqual(code, 0, out)
        self.assertEqual(fake.merged, [1, 11, 12])
        for number in (2, 3, 4, 5, 6, 7, 8, 9, 10, 13):
            self.assertIn(f"skipping #{number}:", out)

    def test_every_file_is_read_so_a_late_global_json_is_seen(self):
        files = [f"src/f{i}.cs" for i in range(150)] + ["sdk/global.json"]
        fake = Fake(prs=[pr(1, changedFiles=len(files), files=files)])
        code, out = run_main(fake)
        self.assertEqual(fake.merged, [])
        self.assertIn("changes global.json", out)

    def test_renaming_global_json_away_is_a_change_to_it(self):
        fake = Fake(prs=[pr(1, files=[("sdk-pin.json", "global.json")])])
        _, out = run_main(fake)
        self.assertEqual(fake.merged, [])
        self.assertIn("changes global.json", out)

    def test_a_label_removed_while_the_files_are_read_stops_the_merge(self):
        def unlabel(f):
            f.views[1] = pr(1, labels=[])
        fake = Fake(prs=[pr(1)], during_files=unlabel)
        _, out = run_main(fake)
        self.assertEqual(fake.merged, [])
        self.assertIn("skipping #1: not labelled", out)

    def test_a_head_pushed_after_the_last_read_is_refused_and_the_rest_stay_open(self):
        def push(f):
            f.views[1] = pr(1, headRefOid="e" * 40)
        fake = Fake(prs=[pr(1), pr(2)], before_merge=lambda f: push(f) if 1 not in f.views else None)
        code, out = run_main(fake)
        self.assertEqual(code, 1)
        self.assertEqual(fake.merged, [])
        self.assertIn("head commit does not match", out)
        self.assertFalse(any(c[:4] == ["gh", "pr", "merge", "2"] for c in fake.calls))

    def test_a_checkout_changed_while_the_files_are_read_stops_the_merge(self):
        changes = {"uncommitted or untracked": {"status": " M edited.py\n"},
                   "not main": {"branch": "feature"},           # a clean switch to another branch
                   "is not origin/main": {"head": "b" * 40}}    # a clean, unpushed commit
        for message, change in changes.items():
            with self.subTest(change=message):
                fake = Fake(prs=[pr(1)], during_files=lambda f, change=change: f.state.update(change))
                code, out = run_main(fake)
                self.assertEqual(code, 2)
                self.assertEqual(fake.merged, [])
                self.assertIn(message, out)

    def test_an_incomplete_file_list_is_refused(self):
        fake = Fake(prs=[pr(1, changedFiles=3, files=["a.yml"])])
        run_main(fake)
        self.assertEqual(fake.merged, [])

    def test_a_pull_request_changed_since_the_listing_is_judged_on_its_fresh_state(self):
        changes = {"label removed": {"labels": []}, "retargeted": {"baseRefName": "release"},
                   "check re-run": {"statusCheckRollup": [{"name": "gates", "conclusion": None}]},
                   "closed": {"state": "MERGED"}}
        for name, change in changes.items():
            with self.subTest(change=name):
                fake = Fake(prs=[pr(1)], views={1: pr(1, **change)})
                code, out = run_main(fake)
                self.assertEqual(code, 0)
                self.assertEqual(fake.merged, [])
                self.assertIn("skipping #1", out)

    def test_a_new_head_pushed_since_the_listing_is_judged_and_merged_by_its_own_sha(self):
        fake = Fake(prs=[pr(1)], views={1: pr(1, headRefOid="f" * 40)})
        run_main(fake)
        merge = next(c for c in fake.calls if c[:3] == ["gh", "pr", "merge"])
        self.assertEqual(merge[-1], "f" * 40)
        self.assertEqual(fake.merged, [1])


class Merging(unittest.TestCase):
    def test_each_merge_is_rebased_against_its_head_then_pulled_and_validated(self):
        fake = Fake(prs=[pr(2), pr(1)])
        code, _ = run_main(fake)
        self.assertEqual(code, 0)
        steps = [("merge" if c[:3] == ["gh", "pr", "merge"] else "pull" if c[:2] == ["git", "pull"] else "validate")
                 for c in fake.calls if c[:3] == ["gh", "pr", "merge"] or c[:2] == ["git", "pull"]
                 or str(c[-1]) == "validate"]
        self.assertEqual(steps, ["merge", "pull", "validate"] * 2)
        self.assertEqual(fake.merged, [1, 2])  # lowest number first
        self.assertIn("--rebase", next(c for c in fake.calls if c[:3] == ["gh", "pr", "merge"]))

    def test_a_failed_merge_stops_with_nothing_merged_and_the_rest_open(self):
        fake = Fake(prs=[pr(1), pr(2)], fail={"gh pr merge 1": (1, "boom")})
        code, out = run_main(fake)
        self.assertEqual(code, 1)
        self.assertEqual(fake.merged, [])
        self.assertIn("merged nothing", out)

    def test_a_failure_after_a_merge_reports_that_merge(self):
        for needle in ("git pull", "validate"):
            with self.subTest(failing=needle):
                fake = Fake(prs=[pr(1), pr(2)], fail={needle: (1, "boom")})
                code, out = run_main(fake)
                self.assertEqual(code, 1)
                self.assertEqual(fake.merged, [1])  # merged on GitHub before the local step failed
                self.assertIn("merge-prs: merged #1", out)
                self.assertIn("#1 merged, then", out)

    def test_a_dry_run_merges_nothing(self):
        fake = Fake(prs=[pr(1)])
        code, out = run_main(fake, ["--dry-run"])
        self.assertEqual(code, 0)
        self.assertEqual(fake.merged, [])
        self.assertIn("would merge #1", out)


class State(unittest.TestCase):
    def tree(self, root):
        from test_todo_graph import todo_file
        todo = root / "todo" / "00-workspace"
        todo.mkdir(parents=True)
        text = todo_file([(1, "A", 0, "none", "--")]).replace(
            "## 1. A\n\n", "## 1. A\n\n> **Started:** 2026-10-22T00:00:00Z\n\n")
        (todo / "TODO-01-a.md").write_text(text, encoding="utf-8")
        (todo / "INDEX.md").write_text("# Index\n- TODO-01-a.md\n", encoding="utf-8")
        (root / "todo" / "TODO-00-INDEX.md").write_text("# Index\n- 00-workspace/TODO-01-a.md\n", encoding="utf-8")

    def test_a_started_open_section_is_in_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.tree(Path(tmp))
            self.assertEqual(merge_prs.in_progress_sections(Path(tmp)), ["D00 T01 §1"])

    def test_a_started_section_that_is_stamped_is_not_in_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            done = mock.Mock(done=True, body="> **Started:** 2026-10-22T00:00:00Z")
            with mock.patch("todo_graph.graph", return_value={"D00 T01 §1": done}):
                self.assertEqual(merge_prs.in_progress_sections(Path(tmp)), [])

    def test_the_campaign_owner_is_read_from_the_run_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(merge_prs.campaign_owner(tmp))
            (Path(tmp) / "build").mkdir()
            (Path(tmp) / "build" / "claude-campaign-guard.json").write_text(json.dumps({"session_id": "s1"}))
            self.assertEqual(merge_prs.campaign_owner(tmp), "s1")


if __name__ == "__main__":
    unittest.main()
