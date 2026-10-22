# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The pin automations: the shared proposal and notice library, and the checks of this machine."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import pin_proposal


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


python_pin = load("check_python_pin", "check-python-pin.py")
vs = load("check_visual_studio", "check-visual-studio.py")

def quiet(fn, *args, **kwargs):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = fn(*args, **kwargs)
    return code, out.getvalue()


class GitRepo(unittest.TestCase):
    """A throwaway repository on main with the given files committed."""
    FILES = {}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for args in (["init", "-q", "-b", "main"], ["config", "user.email", "t@example.invalid"],
                     ["config", "user.name", "T"], ["config", "commit.gpgsign", "false"]):
            self.run_git(*args)
        self.commit(self.FILES)
        self.mails = []

    def tearDown(self):
        self.tmp.cleanup()

    def run_git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True).stdout.strip()

    def commit(self, files):
        for rel, text in files.items():
            (self.root / rel).write_text(text, encoding="utf-8", newline="")
        (self.root / ".keep").write_text(str(len(self.git("log", "--oneline").splitlines())), encoding="utf-8")
        self.run_git("add", ".")
        self.run_git("commit", "-q", "-m", "fixture")

    def mail(self, _root, subject, body, _dry_run=False):
        self.mails.append((subject, body))


class Notice(GitRepo):
    def test_a_notice_is_sent_once_per_key(self):
        args = dict(root=self.root, key="vs-18.12.0", subject="s", body="b", mail=self.mail)
        self.assertEqual(quiet(pin_proposal.notice, **args)[0], 0)
        self.assertEqual(quiet(pin_proposal.notice, **args)[0], 0)
        self.assertEqual(len(self.mails), 1)
        self.assertTrue(self.git("rev-parse", "--verify", "refs/office-notice/vs-18.12.0"))

    def test_an_unsent_notice_is_retried_next_run(self):
        def refuse(*_a):
            raise RuntimeError("refused")

        code, out = quiet(pin_proposal.notice, root=self.root, key="k", subject="s", body="b", mail=refuse)
        self.assertEqual(code, 1)
        self.assertIn("next run will try again", out)
        self.assertEqual(self.git("for-each-ref", "refs/office-notice"), "")

    def test_a_dry_run_records_nothing(self):
        quiet(pin_proposal.notice, root=self.root, key="k", subject="s", body="b", dry_run=True, mail=self.mail)
        self.assertEqual(self.git("for-each-ref", "refs/office-notice"), "")

    def test_notify_sends_through_the_alert_module(self):
        sent = []

        class Alert:
            @staticmethod
            def key():
                return "api-key"

            @staticmethod
            def send(key, subject, body):
                sent.append((key, subject, body))

        pin_proposal.notify(self.root, "s", "b", alert_module=Alert)
        self.assertEqual(sent, [("api-key", "s", "b")])


class Proposal(GitRepo):
    """`pin_proposal.propose` on a neutral pin file: a branch from main, checks, an email, never main or the checkout.
    Moved here from the retired WinUI 3 pin tests on 2026-10-22 (D00 T03 §10); the C++ toolchain pins reuse it."""
    FILES = {"pin.txt": "1.0.0\n"}
    BRANCH = "pins/demo-2.0.0"

    def propose(self, *, checks=lambda tree: [], rewrite=None, dry_run=False, mail=None):
        def bump(tree):
            (tree / "pin.txt").write_text("2.0.0\n", encoding="utf-8", newline="")
            return ["pin.txt"]

        return quiet(pin_proposal.propose, root=self.root, key="demo-2.0.0", branch=self.BRANCH,
                     rewrite=rewrite or bump, checks=checks, message=["deps: pin demo 2.0.0"],
                     subject="Office: demo 2.0.0 is ready to merge", body=lambda commit: f"git merge {self.BRANCH}",
                     dry_run=dry_run, mail=mail or self.mail)

    def test_proposes_on_a_branch_and_leaves_main_and_the_checkout_alone(self):
        code, out = self.propose()
        self.assertEqual(code, 0, out)
        self.assertEqual((self.root / "pin.txt").read_text(encoding="utf-8"), "1.0.0\n")
        self.assertEqual(self.git("show", "main:pin.txt"), "1.0.0")
        self.assertEqual(self.git("show", f"{self.BRANCH}:pin.txt"), "2.0.0")
        self.assertEqual(self.git("worktree", "list").count("\n"), 0)  # the temporary worktree is gone
        self.assertEqual(len(self.mails), 1)
        self.assertIn(f"git merge {self.BRANCH}", self.mails[0][1])
        self.assertTrue(self.git("rev-parse", "--verify", "refs/office-pin/demo-2.0.0"))
        self.assertEqual(self.propose()[0], 0)  # finished: nothing is redone or re-sent
        self.run_git("branch", "-D", self.BRANCH)
        self.assertEqual(self.propose()[0], 0)  # even after the operator deletes the branch
        self.assertEqual(len(self.mails), 1)

    def test_main_is_the_baseline_not_the_checkout(self):
        (self.root / "pin.txt").write_text("9.9.9\n", encoding="utf-8")
        seen = []

        def bump(tree):
            seen.append((tree / "pin.txt").read_text(encoding="utf-8"))
            (tree / "pin.txt").write_text("2.0.0\n", encoding="utf-8", newline="")
            return ["pin.txt"]

        self.assertEqual(self.propose(rewrite=bump)[0], 0)
        self.assertEqual(seen, ["1.0.0\n"])

    def test_nothing_to_propose_when_main_holds_the_target(self):
        code, out = self.propose(rewrite=lambda tree: [])
        self.assertEqual(code, 0, out)
        self.assertIn("nothing to propose", out)
        self.assertEqual((self.git("branch", "--list", "pins/*"), self.mails), ("", []))

    def test_an_unfinished_branch_is_discarded_and_redone(self):
        self.run_git("branch", self.BRANCH)  # a branch with no done ref: a run cut short
        code, out = self.propose()
        self.assertEqual(code, 0, out)
        self.assertIn(f"discarded the unfinished {self.BRANCH}", out)
        self.assertEqual(self.git("show", f"{self.BRANCH}:pin.txt"), "2.0.0")
        self.assertEqual(len(self.mails), 1)

    def test_a_killed_run_whose_folder_is_gone_is_recovered(self):
        abandoned = self.root / "build" / "office-pin-killed" / "tree"
        self.run_git("worktree", "add", "-b", self.BRANCH, str(abandoned), "main")
        shutil.rmtree(abandoned.parent)  # the run died and its temporary folder was cleaned up
        code, out = self.propose()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.git("show", f"{self.BRANCH}:pin.txt"), "2.0.0")

    def test_a_worktree_holding_the_branch_is_never_removed_whatever_its_path(self):
        for name in ("office-pin-killed", "office-pin-review", "review"):
            with self.subTest(name=name):
                held = self.root.parent / f"{name}-{self.root.name}" / "tree"
                self.run_git("worktree", "add", "-b", self.BRANCH, str(held), "main")
                (held / "notes.txt").write_text("my uncommitted work", encoding="utf-8")
                try:
                    code, out = self.propose()
                    self.assertEqual(code, 1)
                    self.assertIn("git worktree remove --force", out)  # the alert says how to release it
                    self.assertEqual((held / "notes.txt").read_text(encoding="utf-8"), "my uncommitted work")
                    self.assertEqual(self.mails, [])
                finally:
                    self.run_git("worktree", "remove", "--force", str(held))
                    self.run_git("branch", "-D", self.BRANCH)
        self.assertEqual(self.propose()[0], 0)  # released, the next run proposes as usual

    def test_an_unsent_email_leaves_no_proposal(self):
        def refuse(*_a):
            raise RuntimeError("SMTP2GO refused")

        code, out = self.propose(mail=refuse)
        self.assertEqual(code, 1)
        self.assertIn("next run proposes it again", out)
        self.assertEqual(self.git("branch", "--list", "pins/*"), "")
        self.assertEqual(self.git("for-each-ref", "refs/office-pin"), "")

    def test_a_failed_check_proposes_nothing(self):
        code, out = self.propose(checks=lambda tree: ["the build failed"])
        self.assertEqual(code, 1)
        self.assertIn("the build failed", out)
        self.assertEqual(self.git("branch", "--list", "pins/*"), "")
        self.assertEqual(self.mails, [])

    def test_a_rewrite_that_raises_leaves_no_branch_or_worktree(self):
        def broken(tree):
            raise ValueError("the pin was not found")

        with self.assertRaises(ValueError):
            self.propose(rewrite=broken)
        self.assertEqual((self.git("branch", "--list", "pins/*"), self.git("worktree", "list").count("\n")), ("", 0))

    def test_dry_run_changes_and_sends_nothing(self):
        code, out = self.propose(dry_run=True)
        self.assertEqual(code, 1)
        self.assertIn(f"would create {self.BRANCH}", out)
        self.assertEqual((self.git("branch", "--list", "pins/*"), self.mails), ("", []))

    def test_git_opens_no_console(self):
        seen = []

        def fake_run(cmd, **kwargs):
            seen.append((cmd[0], kwargs.get("creationflags")))
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        real = pin_proposal.subprocess.run
        pin_proposal.subprocess.run = fake_run
        try:
            pin_proposal.git("status", cwd=self.root)
        finally:
            pin_proposal.subprocess.run = real
        self.assertEqual([c for c, _ in seen], ["git"])
        if sys.platform == "win32":
            self.assertEqual(seen[0][1], 0x08000000)


class PythonPin(GitRepo):
    RELEASES = [{"name": "Python 3.15.0"}, {"name": "Python 3.14.5"}, {"name": "Python 3.14.4"}, {"name": "Python 3.16.0a1"}]

    def main(self, local):
        return quiet(python_pin.main, ["notify"], fetch=lambda url: self.RELEASES, root=self.root, local=local,
                     mail=self.mail)

    def test_findings_name_a_minor_or_a_patch_behind(self):
        newest, by_minor = python_pin.latest_releases(self.RELEASES)
        self.assertEqual(newest, (3, 15, 0))
        self.assertIn("newest stable minor 3.15", python_pin.findings(newest, by_minor, (3, 14, 5))[0])
        self.assertIn("latest patch 3.14.5", python_pin.findings((3, 14, 5), by_minor, (3, 14, 4))[0])
        self.assertEqual(python_pin.findings(newest, by_minor, (3, 15, 0)), [])

    def test_being_behind_is_emailed_once(self):
        self.assertEqual(self.main((3, 14, 4))[0], 0)
        self.assertEqual(self.main((3, 14, 4))[0], 0)
        self.assertEqual(len(self.mails), 1)
        self.assertEqual(self.main((3, 15, 0))[0], 0)
        self.assertEqual(len(self.mails), 1)


class VisualStudio(GitRepo):
    def main(self, mode, installed):
        vswhere = self.root / "vswhere.exe"
        vswhere.write_text("", encoding="utf-8")
        rows = [{"displayName": "Visual Studio Professional 2026", "catalog": {"productDisplayVersion": v}}
                for v in installed]

        def run(cmd, **kwargs):
            self.flags = kwargs.get("creationflags")
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(rows), stderr="")
        return quiet(vs.main, [mode], fetch=lambda url: {"info": {"productDisplayVersion": "18.12.0"}}, root=self.root,
                     run=run, vswhere=vswhere, mail=self.mail)

    def test_behind_is_emailed_once_per_release(self):
        self.assertEqual(self.main("check", ["18.11.1"])[0], 1)
        self.assertEqual(self.main("notify", ["18.11.1"])[0], 0)
        self.assertEqual(self.main("notify", ["18.11.1"])[0], 0)
        self.assertEqual(len(self.mails), 1)
        self.assertIn("Visual Studio 18.12.0 is available", self.mails[0][0])
        if sys.platform == "win32":
            self.assertEqual(self.flags, 0x08000000)

    def test_current_passes_and_missing_fails(self):
        self.assertEqual(self.main("check", ["18.12.0"])[0], 0)
        self.assertEqual(self.main("check", [])[0], 1)


if __name__ == "__main__":
    unittest.main()
