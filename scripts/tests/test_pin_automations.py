"""The pin automations: the shared libraries, the .NET 11 and NuGet pins, and the checks of this machine."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import package_versions as pv
import pin_proposal
import pin_sources


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dotnet = load("check_dotnet_pin", "check-dotnet-pin.py")
nuget = load("check_nuget_pins", "check-nuget-pins.py")
python_pin = load("check_python_pin", "check-python-pin.py")
vs = load("check_visual_studio", "check-visual-studio.py")
kits = load("check_conclave_kits", "check-conclave-kits.py")

RC1 = "11.0.100-rc.1.26425.128"
RC2 = "11.0.100-rc.2.26504.105"
GLOBAL = '{\n  "sdk": {\n    "version": "%s",\n    "allowPrerelease": true,\n    "rollForward": "disable"\n  }\n}\n'
PROPS = """<Project>
  <ItemGroup>
    <PackageVersion Include="Microsoft.WindowsAppSDK" Version="2.5.1" />
    <PackageVersion Version='4.3.0' Include='Serilog' />
  </ItemGroup>
</Project>
"""


def feed(latest, *sdks):
    return {"latest-sdk": latest, "releases": [
        {"release-version": "11.0.0-x", "release-date": "2026-10-13", "release-notes": "https://example.invalid/notes",
         "sdk": {"version": v}, "sdks": [{"version": v}]} for v in sdks]}


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


class PackageVersions(unittest.TestCase):
    def test_pins_read_every_live_package(self):
        self.assertEqual(pv.pins(PROPS), {"Microsoft.WindowsAppSDK": "2.5.1", "Serilog": "4.3.0"})

    def test_a_package_pinned_twice_is_refused(self):
        twice = PROPS.replace("</ItemGroup>", '<PackageVersion Include="Serilog" Version="4.0.0" /></ItemGroup>')
        with self.assertRaises(ValueError):
            pv.pins(twice)

    def test_repinning_handles_attribute_order_and_quotes(self):
        out = pv.repinned(PROPS, "Serilog", "4.3.0", "4.4.0")
        self.assertIn("<PackageVersion Version='4.4.0' Include='Serilog' />", out)
        self.assertIn('Include="Microsoft.WindowsAppSDK" Version="2.5.1"', out)

    def test_a_zero_fourth_part_is_the_same_version(self):
        self.assertEqual(pv.stable_key("4.3.0.0"), pv.stable_key("4.3.0"))
        self.assertTrue(pv.published("4.3.0.0", ["4.3.0", "4.4.0"]))
        self.assertFalse(pv.published("4.3.0.1", ["4.3.0", "4.4.0"]))
        self.assertGreater(pv.stable_key("4.3.0.1"), pv.stable_key("4.3.0"))

    def test_latest_stable_skips_prereleases(self):
        self.assertEqual(pv.latest_stable(["4.3.0", "4.10.0", "5.0.0-rc.1", "4.9.1.2"]), "4.10.0")
        self.assertIsNone(pv.stable_key("5.0.0-rc.1"))

    def test_unreadable_nuget_is_typed(self):
        with self.assertRaises(pin_sources.Unreadable):
            pin_sources.nuget_versions("Serilog", fetch=lambda url: {"versions": "4.3.0"})


class DotnetVersions(unittest.TestCase):
    def test_sdk_versions_order_by_stage_then_number(self):
        order = ["11.0.100-preview.7.26381.103", RC1, RC2, "11.0.100", "11.0.101", "11.0.200-preview.1.1.1", "11.0.200"]
        self.assertEqual(sorted(reversed(order), key=dotnet.sdk_key), order)
        self.assertIsNone(dotnet.sdk_key("11.0.100-alpha.1"))

    def test_latest_must_be_an_sdk_the_feed_lists(self):
        self.assertEqual(dotnet.latest(feed(RC2, RC2, RC1))[0], RC2)
        with self.assertRaises(pin_sources.Unreadable):
            dotnet.latest(feed("11.0.100", RC2))
        with self.assertRaises(pin_sources.Unreadable):  # a feed that names another channel never moves the pin
            dotnet.latest(feed("12.0.100", "12.0.100", RC2))

    def test_only_the_sdk_version_changes(self):
        self.assertEqual(dotnet.repinned(GLOBAL % RC1, RC1, RC2), GLOBAL % RC2)
        with self.assertRaises(ValueError):
            dotnet.repinned(GLOBAL % RC1, RC2, "11.0.100")


class DotnetPin(GitRepo):
    FILES = {"global.json": GLOBAL % RC1}

    def main(self, *argv, data=None, run=None):
        return quiet(dotnet.main, list(argv), fetch=lambda url: data or feed(RC2, RC2, RC1), root=self.root,
                     run=run or self.sdks(RC1, RC2), mail=self.mail)

    @staticmethod
    def sdks(*versions):
        def run(cmd, **_kw):
            return subprocess.CompletedProcess(cmd, 0, stdout="".join(f"{v} [C:\\dotnet\\sdk]\n" for v in versions))
        return run

    def test_check_fails_while_a_newer_sdk_is_out(self):
        self.assertEqual(self.main("check")[0], 1)
        self.assertEqual(self.main("check", data=feed(RC1, RC1))[0], 0)

    def test_update_proposes_the_newest_sdk_on_a_branch(self):
        code, out = self.main("update")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(self.git("show", f"dotnet/{RC2}:global.json"))["sdk"]["version"], RC2)
        self.assertEqual(json.loads(self.git("show", "main:global.json"))["sdk"]["version"], RC1)
        self.assertIn(f"git merge dotnet/{RC2}", self.mails[0][1])
        self.assertEqual(self.main("update")[0], 0)
        self.assertEqual(len(self.mails), 1)

    def test_the_release_replaces_the_release_candidate(self):
        code, out = self.main("update", data=feed("11.0.100", "11.0.100", RC2, RC1))
        self.assertEqual(code, 0, out)
        self.assertIn('"version": "11.0.100"', self.git("show", "dotnet/11.0.100:global.json"))

    def test_a_solution_needs_the_sdk_installed_here_before_it_is_built(self):
        self.commit({"Office.slnx": "<Solution />"})
        code, out = self.main("update", run=self.sdks(RC1))
        self.assertEqual(code, 1)
        self.assertIn(f".NET SDK {RC2} is not installed on this machine", out)
        self.assertEqual((self.git("branch", "--list", "dotnet/*"), self.mails), ("", []))

    def test_a_broken_pin_on_main_fails(self):
        self.commit({"global.json": GLOBAL % "10.0.402"})
        self.assertIn("not a .NET 11.0 SDK", self.main("check")[1])
        self.commit({"global.json": GLOBAL % "11.0.100-rc.3.1.1"})
        self.assertIn("does not list", self.main("check")[1])
        self.commit({"global.json": GLOBAL % RC2})
        self.assertIn("ahead of the newest", self.main("check", data=feed(RC1, RC1, RC2))[1])

    def test_a_pin_that_may_roll_forward_fails(self):
        self.commit({"global.json": (GLOBAL % RC1).replace('"disable"', '"latestMajor"')})
        code, out = self.main("update")
        self.assertEqual(code, 1)
        self.assertIn('rollForward must be "disable"', out)
        self.assertEqual(self.git("branch", "--list", "dotnet/*"), "")

    def test_a_feed_naming_another_channel_cannot_check(self):
        self.assertEqual(self.main("update", data=feed("12.0.100", "12.0.100", RC1))[0], 2)
        self.assertEqual(self.git("branch", "--list", "dotnet/*"), "")

    def test_local_announces_a_missing_sdk_once(self):
        args = dict(root=self.root, run=self.sdks(RC2), mail=self.mail, host="TestPC")
        self.assertEqual(quiet(dotnet.local, **args)[0], 0)
        self.assertEqual(quiet(dotnet.local, **args)[0], 0)
        self.assertEqual(len(self.mails), 1)
        self.assertIn(f"install .NET SDK {RC1} on TestPC", self.mails[0][0])
        self.assertEqual(quiet(dotnet.local, self.root, self.sdks(RC1), self.mail, "TestPC")[0], 0)
        self.assertEqual(len(self.mails), 1)

    def test_local_without_dotnet_cannot_check(self):
        def missing(*_a, **_kw):
            raise FileNotFoundError("dotnet")

        self.assertEqual(quiet(dotnet.local, self.root, missing, self.mail, "TestPC")[0], 2)


class NugetPins(GitRepo):
    FILES = {"Directory.Packages.props": PROPS}

    def main(self, *argv, versions=("4.3.0", "4.4.0", "5.0.0-rc.1")):
        def fetch(url):
            assert "windowsappsdk" not in url, "the WinUI 3 pin belongs to check-winui-pin.py"
            return {"versions": list(versions)}
        return quiet(nuget.main, list(argv), fetch=fetch, root=self.root, mail=self.mail)

    def test_a_behind_pin_is_proposed_and_winui_is_left_alone(self):
        self.assertEqual(self.main("check")[0], 1)
        code, out = self.main("update")
        self.assertEqual(code, 0, out)
        branch = self.git("branch", "--list", "pins/nuget-*").strip(" *")
        props = self.git("show", f"{branch}:Directory.Packages.props")
        self.assertIn("Version='4.4.0' Include='Serilog'", props)
        self.assertIn('Include="Microsoft.WindowsAppSDK" Version="2.5.1"', props)
        self.assertIn("Serilog 4.3.0 -> 4.4.0", self.mails[0][1])

    def test_a_four_part_pin_is_compared_as_nuget_normalizes_it(self):
        self.commit({"Directory.Packages.props": PROPS.replace("4.3.0", "4.3.0.0")})
        code, out = self.main("check")
        self.assertEqual(code, 1)
        self.assertIn("Serilog 4.3.0.0 is behind 4.4.0", out)

    def test_current_pins_pass(self):
        self.assertEqual(self.main("check", versions=("4.3.0",))[0], 0)

    def test_a_prerelease_or_unpublished_pin_fails(self):
        self.assertIn("not published", self.main("check", versions=("4.4.0",))[1])
        self.commit({"Directory.Packages.props": PROPS.replace("4.3.0", "5.0.0-rc.1")})
        self.assertIn("not an exact stable version", self.main("check")[1])


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


class ConclaveKits(GitRepo):
    FILES = {"AGENTS.md": "project\n"}

    def sdk(self, files):
        sdk = Path(self.tmp.name) / "sdk"
        for rel, text in files.items():
            path = sdk / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode())
        for args in (["init", "-q"], ["add", "."], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "kits"]):
            subprocess.run(["git", *args], cwd=sdk, check=True, capture_output=True)
        return sdk

    def test_drift_compares_managed_files_with_the_sdk_head(self):
        skill = ".claude/skills/add-todo/SKILL.md"
        sdk = self.sdk({f"kits/todo/templates/{skill}": "kit\n", "kits/todo/templates/todo/plan.json": "{}",
                        "kits/base/templates/scripts/verify-agent-tiers.mjs": "x\n"})
        (self.root / skill).parent.mkdir(parents=True)
        (self.root / skill).write_bytes(b"kit\r\n")  # a CRLF checkout is not drift
        found = kits.drift(sdk, self.root, allow={})
        self.assertEqual(found, ["scripts/verify-agent-tiers.mjs is missing (kit base)"])  # todo/ is project data
        (self.root / skill).write_text("local\n", encoding="utf-8")
        self.assertIn(f"{skill} differs from the SDK (kit todo)", kits.drift(sdk, self.root, allow={}))
        self.assertEqual(kits.drift(sdk, self.root, allow={skill: "r", "scripts/verify-agent-tiers.mjs": "r"}), [])

    @staticmethod
    def doctor_run(code, stdout, stderr=""):
        def run(cmd, **_kw):
            return subprocess.CompletedProcess(cmd, code, stdout=stdout, stderr=stderr)
        return run

    def test_a_failed_or_empty_doctor_is_never_healthy(self):
        ok = json.dumps({"checks": [{"name": "AGENTS.md", "status": "ok"}]})
        self.assertEqual(kits.doctor(self.root, self.root, self.doctor_run(0, ok)), [])
        gap = json.dumps({"checks": [{"name": "stop-hook", "status": "setup_required"}]})
        self.assertEqual(kits.doctor(self.root, self.root, self.doctor_run(1, gap))[0], "doctor base: setup_required stop-hook")
        for run in (self.doctor_run(1, "{}", "boom"), self.doctor_run(0, '{"checks": []}'), self.doctor_run(1, ok),
                    self.doctor_run(0, "not json"), self.doctor_run(0, '{"checks": [{"status": "ok"}]}'),
                    self.doctor_run(0, '{"checks": [{"name": "x", "status": 1}]}'), self.doctor_run(0, '{"checks": ["ok"]}')):
            with self.assertRaises(RuntimeError):
                kits.doctor(self.root, self.root, run)

    def test_the_sdk_comes_from_config_then_discovery_then_setup_required(self):
        repo = Path(self.tmp.name) / "work" / "Office"
        repo.mkdir(parents=True)
        self.assertIsNone(kits.sdk_root(repo, environ={}))
        beside = repo.parent / "Conclave-SDK"
        beside.mkdir()
        (beside / "forge.py").write_text("", encoding="utf-8")
        self.assertEqual(kits.sdk_root(repo, environ={}), beside)
        configured = Path(self.tmp.name) / "elsewhere"
        configured.mkdir()
        (configured / "forge.py").write_text("", encoding="utf-8")
        self.assertEqual(kits.sdk_root(repo, environ={"CONCLAVE_SDK_ROOT": str(configured)}), configured)
        code, out = quiet(kits.main, ["check"], root=Path(self.tmp.name) / "nowhere" / "Office")
        self.assertEqual(code, 2)
        self.assertIn("setup required", out)

    def test_an_allow_entry_needs_a_reason(self):
        (self.root / ".conclave").mkdir()
        (self.root / kits.ALLOW).write_text("scripts/x.py |\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            kits.allowed(self.root)


if __name__ == "__main__":
    unittest.main()
