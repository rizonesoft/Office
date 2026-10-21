"""scripts/check-winui-pin.py: the pin follows the latest stable WinUI 3 release, proposed on a branch, never on main."""
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_winui_pin", SCRIPTS / "check-winui-pin.py")
wp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wp)
pv = wp.package_versions

PROPS = """<Project>
  <ItemGroup>
    <!-- keep this comment; <PackageVersion Include="Microsoft.WindowsAppSDK" Version="2.4.0" /> stays commented -->
    <PackageVersion Include="Microsoft.WindowsAppSDK" Version="2.4.0" />
  </ItemGroup>
</Project>
"""


def release(tag, prerelease=False):
    return {"tag_name": tag, "prerelease": prerelease, "published_at": "2026-09-16T22:53:27Z",
            "html_url": "https://example.invalid/" + tag}


RELEASES = [release("winui3/release/2.5.4-experimental", True), release("winui3/release/1.8.12"),
            release("winui3/release/2.5.1"), release("winui3/release/2.4.0"), release("winui2/release/2.8.7"),
            release("winui3/release/2.6.0-experimental")]


class Selection(unittest.TestCase):
    def test_the_newest_stable_winui3_release_wins(self):
        self.assertEqual(wp.latest_stable(RELEASES)[0], "2.5.1")

    def test_experimental_drafts_and_junk_never_count(self):
        sneaky = [release("winui3/release/9.9.9-experimental"), release("winui3/release/2.5.1")]
        self.assertEqual(wp.latest_stable(sneaky)[0], "2.5.1")
        labelled = [dict(release("winui3/release/2.6.0"), name="WinUI 3 in WinAppSDK 2.6.0-experimental"),
                    release("winui3/release/2.5.1")]
        self.assertEqual(wp.latest_stable(labelled)[0], "2.5.1")
        draft = [dict(release("winui3/release/2.7.0"), draft=True), "not a release", release("winui3/release/2.5.1")]
        self.assertEqual(wp.latest_stable(draft)[0], "2.5.1")

    def test_versions_compare_numerically(self):
        self.assertEqual(wp.latest_stable([release("winui3/release/2.9.0"), release("winui3/release/2.10.0")])[0], "2.10.0")
        self.assertTrue(wp.newer("2.10.0", "2.9.9"))
        self.assertFalse(wp.newer("2.5.1", "2.5.1"))

    def test_only_the_live_version_changes(self):
        out = pv.repinned(PROPS, wp.PACKAGE, "2.4.0", "2.5.1")
        self.assertEqual(out, PROPS.replace('<PackageVersion Include="Microsoft.WindowsAppSDK" Version="2.4.0" />\n',
                                            '<PackageVersion Include="Microsoft.WindowsAppSDK" Version="2.5.1" />\n'))
        self.assertIn('Version="2.4.0" /> stays commented', out)
        with self.assertRaises(ValueError):
            pv.repinned(PROPS, wp.PACKAGE, "1.0.0", "2.5.1")


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.run_git("init", "-q", "-b", "main")
        self.run_git("config", "user.email", "test@example.invalid")
        self.run_git("config", "user.name", "Test")
        self.run_git("config", "commit.gpgsign", "false")
        self.commit_props(PROPS)
        self.mails = []

    def tearDown(self):
        self.tmp.cleanup()

    def run_git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def commit_props(self, text):
        (self.root / "Directory.Packages.props").write_text(text, encoding="utf-8", newline="")
        self.run_git("add", ".")
        self.run_git("commit", "-q", "-m", "pin")

    def mail(self, _root, subject, body, _dry_run=False):
        self.mails.append((subject, body))

    def main(self, *argv, releases=RELEASES, nuget=("2.4.0", "2.5.1"), mail=None):
        def fetch(url):
            return releases if "github" in url else {"versions": list(nuget)}

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = wp.main(list(argv), fetch=fetch, root=self.root, mail=mail or self.mail)
        return code, out.getvalue() + err.getvalue()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True).stdout.strip()

    def test_check_fails_on_an_older_pin_and_passes_on_the_latest(self):
        self.assertEqual(self.main("check")[0], 1)
        self.assertEqual(self.main("check", releases=[release("winui3/release/2.4.0")])[0], 0)

    def test_update_proposes_on_a_branch_and_leaves_main_and_the_checkout_alone(self):
        before = (self.root / "Directory.Packages.props").read_text(encoding="utf-8")
        code, out = self.main("update")
        self.assertEqual(code, 0, out)
        self.assertEqual((self.root / "Directory.Packages.props").read_text(encoding="utf-8"), before)
        self.assertIn('Version="2.4.0" />\n', self.git("show", "main:Directory.Packages.props") + "\n")
        self.assertIn('Version="2.5.1" />', self.git("show", "winui/2.5.1:Directory.Packages.props"))
        self.assertIn("keep this comment", self.git("show", "winui/2.5.1:Directory.Packages.props"))
        self.assertEqual(self.git("worktree", "list").count("\n"), 0)  # the temporary worktree is gone
        self.assertEqual(len(self.mails), 1)
        self.assertIn("git merge winui/2.5.1", self.mails[0][1])
        self.assertTrue(self.git("rev-parse", "--verify", "refs/office-pin/winui-2.5.1"))
        self.assertEqual(self.main("update")[0], 0)  # finished: nothing is redone or re-sent
        self.run_git("branch", "-D", "winui/2.5.1")
        self.assertEqual(self.main("update")[0], 0)  # even after the operator deletes the branch
        self.assertEqual(len(self.mails), 1)

    def test_an_unfinished_branch_is_discarded_and_redone(self):
        self.run_git("branch", "winui/2.5.1")  # a branch with no done ref: a run cut short
        code, out = self.main("update")
        self.assertEqual(code, 0, out)
        self.assertIn("discarded the unfinished winui/2.5.1", out)
        self.assertIn('Version="2.5.1"', self.git("show", "winui/2.5.1:Directory.Packages.props"))
        self.assertEqual(len(self.mails), 1)

    def test_a_run_killed_mid_proposal_is_recovered(self):
        abandoned = self.root / "build" / "office-pin-killed" / "tree"
        self.run_git("worktree", "add", "-b", "winui/2.5.1", str(abandoned), "main")  # what a killed run leaves
        code, out = self.main("update")
        self.assertEqual(code, 0, out)
        self.assertNotIn(str(abandoned).replace(chr(92), "/"), self.git("worktree", "list").replace(chr(92), "/"))
        self.assertIn('Version="2.5.1"', self.git("show", "winui/2.5.1:Directory.Packages.props"))

    def test_the_operators_own_worktree_is_never_removed(self):
        mine = self.root.parent / (self.root.name + "-review")
        self.run_git("worktree", "add", "-b", "winui/2.5.1", str(mine), "main")
        try:
            code, out = self.main("update")
            self.assertEqual(code, 1)
            self.assertIn("which this automation did not create", out)
            self.assertTrue((mine / "Directory.Packages.props").is_file())
        finally:
            self.run_git("worktree", "remove", "--force", str(mine))

    def test_an_unsent_email_leaves_no_proposal(self):
        def refuse(*_a):
            raise RuntimeError("SMTP2GO refused")

        code, out = self.main("update", mail=refuse)
        self.assertEqual(code, 1)
        self.assertIn("next run proposes it again", out)
        self.assertEqual(self.git("branch", "--list", "winui/*"), "")
        self.assertEqual(self.git("for-each-ref", "refs/office-pin"), "")

    def test_a_failed_check_proposes_nothing(self):
        code, out = self.main("update", nuget=("2.4.0",))
        self.assertEqual(code, 1)
        self.assertIn("NuGet has no", out)
        self.assertEqual(self.git("branch", "--list", "winui/*"), "")
        self.assertEqual(self.mails, [])

    def test_a_rewrite_that_fails_exits_1_and_leaves_nothing(self):
        def broken(*_a):
            raise ValueError("the pin was not found")

        real, pv.repinned = pv.repinned, broken
        try:
            code, out = self.main("update")
        finally:
            pv.repinned = real
        self.assertEqual(code, 1)
        self.assertIn("check-winui-pin: the pin was not found", out)
        self.assertNotIn("Traceback", out)
        self.assertEqual((self.git("branch", "--list", "winui/*"), self.git("worktree", "list").count("\n")), ("", 0))

    def test_main_is_the_baseline_not_the_checkout(self):
        (self.root / "Directory.Packages.props").write_text(PROPS.replace('Version="2.4.0" />\n', 'Version="2.5.1" />\n'),
                                                           encoding="utf-8")
        self.assertEqual(self.main("check")[0], 1)  # the checkout already says 2.5.1, but main still pins 2.4.0

    def test_a_broken_pin_on_main_fails(self):
        self.commit_props(PROPS.replace('Version="2.4.0" />\n', 'Version="2.5.0-preview1" />\n'))
        self.assertIn("not an exact stable version", self.main("check")[1])
        self.commit_props(PROPS.replace('Version="2.4.0" />\n', 'Version="2.9.0" />\n'))
        self.assertIn("ahead of the newest", self.main("check", nuget=("2.9.0", "2.5.1"))[1])
        self.commit_props(PROPS.replace('Version="2.4.0" />\n', 'Version="2.5.1" />\n'))
        code, out = self.main("check", nuget=("2.4.0",))
        self.assertEqual(code, 1)
        self.assertIn("not published on NuGet", out)

    def test_unreadable_releases_exit_2(self):
        def broken(url):
            raise wp.Unreadable("offline")

        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(wp.main(["check"], fetch=broken, root=self.root), 2)

    def test_dry_run_changes_and_sends_nothing(self):
        code, out = self.main("update", "--dry-run")
        self.assertEqual(code, 1)
        self.assertIn("would create winui/2.5.1", out)
        self.assertEqual((self.git("branch", "--list", "winui/*"), self.mails), ("", []))


class NoConsole(unittest.TestCase):
    def test_every_process_it_starts_opens_no_console(self):
        seen = []

        def fake_run(cmd, **kwargs):
            seen.append((cmd[0], kwargs.get("creationflags")))
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        proposal = wp.pin_proposal
        real = proposal.subprocess.run
        proposal.subprocess.run = fake_run
        try:
            wp.git("status")
            with tempfile.TemporaryDirectory() as tmp:
                tree = Path(tmp)
                (tree / "Directory.Packages.props").write_text(PROPS, encoding="utf-8")
                (tree / "Office.slnx").write_text("<Solution />", encoding="utf-8")
                wp.checks(tree, "2.4.0", {"2.4.0"}, build=fake_run)
        finally:
            proposal.subprocess.run = real
        self.assertEqual([c for c, _ in seen], ["git", "dotnet"])
        if wp.sys.platform == "win32":
            self.assertTrue(all(flags == 0x08000000 for _, flags in seen), seen)


class RepositoryPin(unittest.TestCase):
    def test_the_repository_pins_one_windows_app_sdk_version(self):
        self.assertRegex(wp.pinned(), r"^\d+\.\d+\.\d+$")


if __name__ == "__main__":
    unittest.main()
