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

PROPS = """<Project>
  <ItemGroup>
    <!-- keep this comment -->
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

    def test_experimental_never_counts_even_unmarked(self):
        sneaky = [release("winui3/release/9.9.9-experimental"), release("winui3/release/2.5.1")]
        self.assertEqual(wp.latest_stable(sneaky)[0], "2.5.1")
        labelled = [dict(release("winui3/release/2.6.0"), name="WinUI 3 in WinAppSDK 2.6.0-experimental"),
                    release("winui3/release/2.5.1")]
        self.assertEqual(wp.latest_stable(labelled)[0], "2.5.1")

    def test_versions_compare_numerically(self):
        self.assertEqual(wp.latest_stable([release("winui3/release/2.9.0"), release("winui3/release/2.10.0")])[0], "2.10.0")
        self.assertTrue(wp.newer("2.10.0", "2.9.9"))
        self.assertFalse(wp.newer("2.5.1", "2.5.1"))

    def test_only_the_version_changes(self):
        out = wp.repinned(PROPS, "2.4.0", "2.5.1")
        self.assertEqual(out, PROPS.replace('Version="2.4.0"', 'Version="2.5.1"'))
        with self.assertRaises(ValueError):
            wp.repinned(PROPS, "1.0.0", "2.5.1")


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        run = lambda *a: subprocess.run(["git", *a], cwd=self.root, check=True, capture_output=True)
        run("init", "-q", "-b", "main")
        run("config", "user.email", "test@example.invalid")
        run("config", "user.name", "Test")
        (self.root / "Directory.Packages.props").write_text(PROPS, encoding="utf-8", newline="")
        run("add", ".")
        run("commit", "-q", "-m", "init")
        self.mails = []

    def tearDown(self):
        self.tmp.cleanup()

    def main(self, *argv, releases=RELEASES, nuget=("2.4.0", "2.5.1")):
        def fetch(url):
            return releases if "github" in url else {"versions": list(nuget)}

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = wp.main(list(argv), fetch=fetch, root=self.root, mail=lambda s, b, d=False: self.mails.append((s, b)))
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
        self.assertIn('Version="2.4.0"', self.git("show", "main:Directory.Packages.props"))
        self.assertIn('Version="2.5.1"', self.git("show", "winui/2.5.1:Directory.Packages.props"))
        self.assertIn("keep this comment", self.git("show", "winui/2.5.1:Directory.Packages.props"))
        self.assertEqual(self.git("worktree", "list").count("\n"), 0)  # the temporary worktree is gone
        self.assertEqual(len(self.mails), 1)
        self.assertIn("git merge winui/2.5.1", self.mails[0][1])
        self.assertEqual(self.main("update")[0], 0)  # proposed before: nothing is redone or re-sent
        self.assertEqual(len(self.mails), 1)

    def test_a_failed_check_proposes_nothing(self):
        code, out = self.main("update", nuget=("2.4.0",))
        self.assertEqual(code, 1)
        self.assertIn("NuGet has no", out)
        self.assertEqual(self.git("branch", "--list", "winui/*"), "")
        self.assertEqual(self.mails, [])

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

        real = wp.subprocess.run
        wp.subprocess.run = fake_run
        try:
            wp.git("status")
            with tempfile.TemporaryDirectory() as tmp:
                tree = Path(tmp)
                (tree / "Directory.Packages.props").write_text(PROPS, encoding="utf-8")
                (tree / "Office.slnx").write_text("<Solution />", encoding="utf-8")
                wp.checks(tree, "2.4.0", {"2.4.0"}, build=fake_run)
        finally:
            wp.subprocess.run = real
        self.assertEqual([c for c, _ in seen], ["git", "dotnet"])
        if wp.sys.platform == "win32":
            self.assertTrue(all(flags == 0x08000000 for _, flags in seen), seen)


class RepositoryPin(unittest.TestCase):
    def test_the_repository_pins_one_windows_app_sdk_version(self):
        self.assertRegex(wp.pinned(), r"^\d+\.\d+\.\d+$")


if __name__ == "__main__":
    unittest.main()
