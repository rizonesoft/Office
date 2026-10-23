# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/check-campaign-host.py: each readiness check passes a ready PC and fails naming its fix (D00 T03 §12)."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_campaign_host", SCRIPTS / "check-campaign-host.py")
host_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(host_check)
todo_graph = host_check.todo_graph

OFFICE = r"C:\Program Files\Microsoft Office"
FULL_VS = [{"displayName": "Visual Studio Professional 2026", "installationVersion": "18.11.12315.225",
            "installationPath": r"C:\Program Files\Microsoft Visual Studio\18\Professional", "isPrerelease": False,
            "packages": [{"id": i, "type": "Component"} for i in host_check.TOOLCHAIN]
            + [{"id": "Microsoft.VisualStudio.Component.Windows11SDK.26100", "type": "Component"}]}]


def section(ref, needs=(), done=False, phase=2, status="active", depends=()):
    return todo_graph.Section(ref=ref, path=f"todo/{ref}.md", number=1, title=ref, phase=phase,
                              depends=list(depends), needs=list(needs), done=done, status=status, body="",
                              receipt="")


class Fake:
    """A ready PC; each test changes one fact."""

    def __init__(self, root):
        self.root = Path(root)
        self.session = (1, host_check.WTS_ACTIVE, host_check.WTS_SESSIONSTATE_UNLOCK)
        self.power = {host_check.STANDBYIDLE: 0, host_check.HIBERNATEIDLE: 0}
        self.values = {
            (host_check.HKCU, host_check.DESKTOP, "ScreenSaveActive"): "1",
            (host_check.HKCU, host_check.DESKTOP, "ScreenSaverIsSecure"): "0",
            (host_check.HKCU, host_check.DESKTOP, "SCRNSAVE.EXE"): r"C:\WINDOWS\system32\Mystify.scr",
            (host_check.HKCU, host_check.DESKTOP, "ScreenSaveTimeOut"): "3600",
            (host_check.HKLM, host_check.CLICK_TO_RUN, "InstallPath"): OFFICE,
            (host_check.HKLM, host_check.CLICK_TO_RUN + r"\Configuration", "VersionToReport"): "16.0.20430.20182",
        }
        self.files = {str(Path(OFFICE) / "root" / "Office16" / exe) for _, exe in host_check.OFFICE_APPS}
        self.tree = {"D02 T01 §24": section("D02 T01 §24", needs=["office", "display-session"])}
        self.instances = json.loads(json.dumps(FULL_VS))
        self.on_path = {"gh": r"C:\gh\gh.exe", "codex": r"C:\npm\codex.cmd"}
        self.gh_status = 0
        self.reviewer_status = 0
        self.probe_error = {}  # program name -> the exception its probe raises
        self.pin = ("sol", "codex")
        self.free = 300 * 10**9
        self.calls = []

    def console_session(self):
        if isinstance(self.session, Exception):
            raise self.session
        return self.session

    def power_ac(self, subgroup, setting):
        assert subgroup == host_check.SUB_SLEEP
        return self.power[setting]

    def registry(self, hive, key, name):
        return self.values.get((hive, key, name))

    def is_file(self, path):
        return str(path) in self.files

    def sections(self):
        if isinstance(self.tree, Exception):
            raise self.tree
        return self.tree() if callable(self.tree) else self.tree

    def vswhere(self):
        return self.instances

    def find(self, name):
        return self.on_path.get(name)

    def run(self, argv):
        self.calls.append(argv)
        program = Path(argv[0]).stem
        if program in self.probe_error:
            raise self.probe_error[program]
        status = self.gh_status if program == "gh" else self.reviewer_status
        return subprocess.CompletedProcess(argv, status, "Logged in as someone@example.com", "")

    def reviewer_cli(self):
        if isinstance(self.pin, Exception):
            raise self.pin
        return self.pin

    def free_bytes(self):
        return self.free


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.host = Fake(self.tmp)

    def result(self, name):
        return next(r for r in host_check.run_checks(self.host) if r["name"] == name)

    def main(self, *argv, mail=None):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = host_check.main(list(argv), host=self.host, mail=mail or self.fail_mail)
        return code, out.getvalue()

    def fail_mail(self, *args):
        raise AssertionError("no email expected")


class ReadyHost(Base):
    def test_every_check_passes_and_exits_zero(self):
        code, out = self.main()
        self.assertEqual(code, 0)
        self.assertEqual([line.split()[0] for line in out.splitlines()[:8]], ["ok"] * 8)
        for name in host_check.NAMES:
            self.assertIn(f" {name}: ", out)
        self.assertIn("ready: every check passed", out)


class Session(Base):
    def test_locked_screen_fails_naming_it(self):
        self.host.session = (1, host_check.WTS_ACTIVE, host_check.WTS_SESSIONSTATE_LOCK)
        r = self.result("session")
        self.assertEqual(r["state"], "fail")
        self.assertIn("screen locked", r["detail"])

    def test_no_console_user_fails(self):
        self.host.session = None
        self.assertEqual(self.result("session")["state"], "fail")

    def test_disconnected_console_fails(self):
        self.host.session = (1, 4, host_check.WTS_SESSIONSTATE_UNLOCK)  # WTSDisconnected
        r = self.result("session")
        self.assertEqual(r["state"], "fail")
        self.assertIn("not active", r["detail"])

    def test_unknown_lock_state_cannot_check(self):
        self.host.session = (1, host_check.WTS_ACTIVE, -1)
        self.assertEqual(self.result("session")["state"], "error")
        self.assertEqual(self.main()[0], 2)

    def test_api_failure_cannot_check(self):
        self.host.session = host_check.Unreadable("WTSQuerySessionInformationW failed (error 5)")
        self.assertEqual(self.result("session")["state"], "error")


class Power(Base):
    def test_sleep_timeout_fails_naming_powercfg(self):
        self.host.power[host_check.STANDBYIDLE] = 1800
        r = self.result("power")
        self.assertEqual(r["state"], "fail")
        self.assertIn("sleep after 30 minutes", r["detail"])
        self.assertEqual(r["fix"], "powercfg /change standby-timeout-ac 0")

    def test_hibernate_timeout_fails_naming_powercfg(self):
        self.host.power[host_check.HIBERNATEIDLE] = 10800
        self.assertEqual(self.result("power")["fix"], "powercfg /change hibernate-timeout-ac 0")


class ScreenLock(Base):
    def test_secure_screen_saver_fails(self):
        self.host.values[(host_check.HKCU, host_check.DESKTOP, "ScreenSaverIsSecure")] = "1"
        r = self.result("screen lock")
        self.assertEqual(r["state"], "fail")
        self.assertIn("ScreenSaverIsSecure 0", r["fix"])

    def test_secure_screen_saver_by_policy_fails_naming_the_policy(self):
        self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, "ScreenSaverIsSecure")] = "1"
        r = self.result("screen lock")
        self.assertEqual(r["state"], "fail")
        self.assertIn("policy", r["fix"])

    def test_policy_turning_the_saver_off_passes(self):
        self.host.values[(host_check.HKCU, host_check.DESKTOP, "ScreenSaverIsSecure")] = "1"
        self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, "ScreenSaveActive")] = "0"
        self.assertEqual(self.result("screen lock")["state"], "ok")

    def test_a_zero_timeout_never_starts_the_saver_so_it_passes(self):
        self.host.values[(host_check.HKCU, host_check.DESKTOP, "ScreenSaverIsSecure")] = "1"
        self.host.values[(host_check.HKCU, host_check.DESKTOP, "ScreenSaveTimeOut")] = "0"
        self.assertEqual(self.result("screen lock")["state"], "ok")

    def test_a_zero_timeout_set_by_policy_wins_over_the_users(self):
        self.host.values[(host_check.HKCU, host_check.DESKTOP, "ScreenSaverIsSecure")] = "1"
        self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, "ScreenSaveTimeOut")] = "0"
        self.assertEqual(self.result("screen lock")["state"], "ok")

    def test_a_missing_timeout_never_starts_the_saver_so_it_passes(self):
        self.host.values[(host_check.HKCU, host_check.DESKTOP, "ScreenSaverIsSecure")] = "1"
        del self.host.values[(host_check.HKCU, host_check.DESKTOP, "ScreenSaveTimeOut")]
        self.assertEqual(self.result("screen lock")["state"], "ok")

    def test_an_unreadable_timeout_cannot_check(self):
        self.host.values[(host_check.HKCU, host_check.DESKTOP, "ScreenSaveTimeOut")] = "soon"
        self.assertEqual(self.result("screen lock")["state"], "error")

    def test_inactivity_policy_fails(self):
        self.host.values[(host_check.HKLM, host_check.SYSTEM_POLICY, "InactivityTimeoutSecs")] = 900
        r = self.result("screen lock")
        self.assertEqual(r["state"], "fail")
        self.assertIn("InactivityTimeoutSecs", r["fix"])


class Office(Base):
    def test_missing_visio_fails_naming_it(self):
        self.host.files.discard(str(Path(OFFICE) / "root" / "Office16" / "VISIO.EXE"))
        r = self.result("office")
        self.assertEqual(r["state"], "fail")
        self.assertIn("VISIO.EXE", r["detail"])
        self.assertIn("16.0.20430.20182", r["detail"])

    def test_no_click_to_run_fails(self):
        del self.host.values[(host_check.HKLM, host_check.CLICK_TO_RUN, "InstallPath")]
        self.assertEqual(self.result("office")["state"], "fail")

    def test_skipped_when_no_open_section_needs_office(self):
        self.host.tree = {"D02 T01 §24": section("D02 T01 §24", needs=["office"], done=True),
                          "D00 T03 §12": section("D00 T03 §12", needs=["windows-host"], phase=0)}
        self.host.files.clear()
        self.assertEqual(self.result("office")["state"], "skip")

    def test_checked_after_phase_2_while_a_later_section_needs_office(self):
        # The last Phase 2 capture has stamped; D03 T01 §3's page counts still need Office.
        self.host.tree = {"D02 T01 §24": section("D02 T01 §24", needs=["office"], done=True),
                          "D03 T01 §3": section("D03 T01 §3", needs=["office"], phase=3)}
        self.host.files.discard(str(Path(OFFICE) / "root" / "Office16" / "WINPROJ.EXE"))
        r = self.result("office")
        self.assertEqual(r["state"], "fail")
        self.assertIn("D03 T01 §3", r["detail"])

    def test_superseded_sections_do_not_count(self):
        self.host.tree = {"D02 T01 §24": section("D02 T01 §24", needs=["office"], status="superseded")}
        self.assertEqual(self.result("office")["state"], "skip")

    def test_unreadable_tree_still_checks_office(self):
        self.host.tree = todo_graph.Refused("canonical TODO tree is missing or empty")
        self.host.files.discard(str(Path(OFFICE) / "root" / "Office16" / "EXCEL.EXE"))
        r = self.result("office")
        self.assertEqual(r["state"], "fail")
        self.assertIn("cannot be read", r["detail"])


class OfficeFromTheFiles(unittest.TestCase):
    """The real Host reads the TODO files, never build/todo-cache.json, so a missing or stale cache cannot skip Office."""

    TODO = """---
schema_version: 1
id: capture
domain: 02-inventory
status: active
title: "TODO-01 -- Capture"
---

# TODO-01 -- Capture

> **Goal:** g.

> **Current state:** c.

## Inputs

- i.

## Outcome

- o.

**Adjacency:** all=not-applicable (fixture)

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Capture | -- | [ ] |

## 1. Capture

**Phase:** 2
**Needs:** office
**Surface:** no

**Build order:**

1. Capture `x`. Done when: y.

- [ ] Capture `x`. Done when: y.
- [ ] Commit: `capture`

**Test checkpoint:** `true` passes.

## Verification

- v.
"""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "todo" / "02-inventory").mkdir(parents=True)
        (self.root / "todo" / "02-inventory" / "TODO-01-capture.md").write_text(self.TODO, encoding="utf-8")
        (self.root / "todo" / "02-inventory" / "INDEX.md").write_text("# Index\n- TODO-01-capture.md\n", encoding="utf-8")
        (self.root / "todo" / "TODO-00-INDEX.md").write_text("# Index\n- 02-inventory/TODO-01-capture.md\n",
                                                            encoding="utf-8")
        host = host_check.Host()
        host.root = self.root
        self.host = host

    def needed(self):
        refs, note = host_check.office_needed(self.host)
        self.assertIsNone(note, note)
        return refs

    def test_missing_cache_still_finds_the_office_section(self):
        self.assertFalse((self.root / "build" / "todo-cache.json").exists())
        self.assertEqual(self.needed(), ["D02 T01 §1"])

    def test_stale_cache_saying_nothing_needs_office_is_ignored(self):
        (self.root / "build").mkdir()
        (self.root / "build" / "todo-cache.json").write_text(json.dumps({"sections": []}), encoding="utf-8")
        self.assertEqual(self.needed(), ["D02 T01 §1"])


class Toolchain(Base):
    def test_missing_llvm_clang_fails_with_one_install_command(self):
        packages = self.host.instances[0]["packages"]
        self.host.instances[0]["packages"] = [p for p in packages
                                              if p["id"] != "Microsoft.VisualStudio.Component.VC.Llvm.Clang"]
        r = self.result("toolchain")
        self.assertEqual(r["state"], "fail")
        self.assertIn("LLVM clang", r["detail"])
        self.assertIn("modify --installPath", r["fix"])
        self.assertIn("--add Microsoft.VisualStudio.Component.VC.Llvm.Clang", r["fix"])
        self.assertEqual(r["fix"].count("--add"), 1)

    def test_missing_windows_sdk_fails(self):
        self.host.instances[0]["packages"] = [p for p in self.host.instances[0]["packages"]
                                              if "Windows11SDK" not in p["id"]]
        r = self.result("toolchain")
        self.assertEqual(r["state"], "fail")
        self.assertIn(host_check.WINDOWS_SDK_ADD, r["fix"])

    def test_no_visual_studio_fails(self):
        self.host.instances = None
        self.assertEqual(self.result("toolchain")["state"], "fail")

    def test_prerelease_only_fails(self):
        self.host.instances[0]["isPrerelease"] = True
        self.assertEqual(self.result("toolchain")["state"], "fail")

    def test_newest_instance_is_judged(self):
        older = json.loads(json.dumps(FULL_VS[0]))
        older["installationVersion"] = "18.10.1.1"
        self.host.instances[0]["packages"] = []
        self.host.instances.append(older)
        self.assertEqual(self.result("toolchain")["state"], "fail")


class Services(Base):
    def test_gh_signed_out_fails(self):
        self.host.gh_status = 1
        r = self.result("gh")
        self.assertEqual((r["state"], r["fix"]), ("fail", "gh auth login"))
        self.assertIn([r"C:\gh\gh.exe", "auth", "status"], self.host.calls)

    def test_gh_missing_fails(self):
        del self.host.on_path["gh"]
        self.assertEqual(self.result("gh")["state"], "fail")

    def test_reviewer_cli_missing_fails(self):
        del self.host.on_path["codex"]
        r = self.result("reviewer")
        self.assertEqual(r["state"], "fail")
        self.assertIn("codex", r["detail"])

    def test_reviewer_signed_out_fails(self):
        self.host.reviewer_status = 1
        r = self.result("reviewer")
        self.assertEqual((r["state"], r["fix"]), ("fail", "codex login"))
        self.assertIn([r"C:\npm\codex.cmd", "login", "status"], self.host.calls)

    def test_reviewer_that_cannot_start_fails(self):
        self.host.probe_error["codex"] = FileNotFoundError(2, "The system cannot find the file specified")
        r = self.result("reviewer")
        self.assertEqual(r["state"], "fail")
        self.assertIn("cannot start", r["detail"])

    def test_probe_output_is_never_printed(self):
        self.assertNotIn("someone@example.com", self.main()[1])

    def test_refused_pin_fails(self):
        self.host.pin = todo_graph.review_dispatch().Refused("no reviewer pin at x")
        self.assertEqual(self.result("reviewer")["state"], "fail")

    def test_real_pin_names_the_codex_cli(self):
        self.assertEqual(host_check.Host().reviewer_cli()[1], "codex")

    def test_low_disk_fails(self):
        self.host.free = 49 * 10**9
        r = self.result("disk")
        self.assertEqual(r["state"], "fail")
        self.assertIn("under 50 GB", r["detail"])


def alive(pid):
    """Whether a process is still running, without signalling it."""
    if os.name == "nt":
        import ctypes
        kernel32 = ctypes.WinDLL("kernel32")
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
            return code.value == 259  # STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


class Probe(unittest.TestCase):
    """The real Host.run: a deadline and an output bound hold even when the probe leaves a grandchild behind."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def tree(self, sleep):
        """A probe that starts a grandchild (which writes its PID) and then sleeps itself."""
        pid_file = self.tmp / "grandchild.pid"
        grandchild = f"import os, pathlib, time; pathlib.Path({str(pid_file)!r} + '.tmp').write_text(str(os.getpid())); " \
                     f"os.replace({str(pid_file)!r} + '.tmp', {str(pid_file)!r}); time.sleep(60)"
        # The parent waits for the PID file before it sleeps or exits, so the test measures cleanup, not scheduling.
        parent = (f"import pathlib, subprocess, sys, time; subprocess.Popen([sys.executable, '-c', {grandchild!r}]); "
                  f"p = pathlib.Path({str(pid_file)!r})\n"
                  f"while not (p.exists() and p.read_text()): time.sleep(0.01)\n"
                  f"time.sleep({sleep})")
        return [sys.executable, "-c", parent], pid_file

    def grandchild_gone(self, pid_file):
        for _ in range(100):
            if pid_file.exists() and pid_file.read_text():
                break
            time.sleep(0.05)
        pid = int(pid_file.read_text())
        for _ in range(50):
            if not alive(pid):
                return True
            time.sleep(0.1)
        os.kill(pid, 9)
        return False

    def test_empty_vswhere_output_cannot_check(self):
        host = host_check.Host()
        host.run = lambda argv, seconds=None: subprocess.CompletedProcess(argv, 0, "", "")
        with mock.patch.object(host_check, "VSWHERE", Path(sys.executable)), \
                self.assertRaises(host_check.Unreadable):
            host.vswhere()

    def test_vswhere_output_that_is_not_a_list_cannot_check(self):
        host = host_check.Host()
        host.run = lambda argv, seconds=None: subprocess.CompletedProcess(argv, 0, "{}", "")
        with mock.patch.object(host_check, "VSWHERE", Path(sys.executable)), \
                self.assertRaises(host_check.Unreadable):
            host.vswhere()

    @unittest.skipUnless(os.name == "nt", "the job object is the Windows containment")
    def test_a_job_that_never_empties_is_reported_not_trusted(self):
        with mock.patch.object(host_check.Containment, "active", lambda self: 1), \
                mock.patch.object(host_check, "KILL_SECONDS", 1):
            with self.assertRaises(host_check.Unreadable) as caught:
                host_check.Host().run([sys.executable, "-c", "print(1)"])
        self.assertIn("could not be ended", str(caught.exception))

    def test_output_and_exit_code_are_returned(self):
        r = host_check.Host().run([sys.executable, "-c", "import sys; print('hello'); sys.exit(3)"])
        self.assertEqual((r.returncode, r.stdout.strip()), (3, "hello"))

    def test_a_hung_probe_tree_is_ended_at_its_deadline(self):
        argv, pid_file = self.tree(60)
        started = time.monotonic()
        with self.assertRaises(host_check.Unreadable) as caught:
            host_check.Host().run(argv, seconds=2)
        self.assertLess(time.monotonic() - started, 20)
        self.assertIn("did not finish within 2 seconds", str(caught.exception))
        self.assertTrue(self.grandchild_gone(pid_file), "the probe's grandchild outlived the deadline")

    def test_a_flood_written_before_the_first_poll_is_still_refused(self):
        burst = "import sys; sys.stdout.write('x' * 2_000_000)"
        with mock.patch.object(host_check, "MAX_PROBE_BYTES", 1_000_000), \
                mock.patch.object(host_check, "POLL_SECONDS", 5):
            with self.assertRaises(host_check.Unreadable) as caught:
                host_check.Host().run([sys.executable, "-c", burst], seconds=30)
        self.assertIn("wrote more than 1000000 bytes", str(caught.exception))
    def test_a_flood_of_output_is_stopped_at_the_bound(self):
        flood = "import sys\nwhile True: sys.stdout.write('x' * 65536)"
        with mock.patch.object(host_check, "MAX_PROBE_BYTES", 1_000_000):
            with self.assertRaises(host_check.Unreadable) as caught:
                host_check.Host().run([sys.executable, "-c", flood], seconds=30)
        self.assertIn("wrote more than 1000000 bytes", str(caught.exception))

    def test_a_grandchild_left_behind_by_a_finished_probe_is_ended_with_it(self):
        argv, pid_file = self.tree(0)
        started = time.monotonic()
        r = host_check.Host().run(argv, seconds=20)
        self.assertLess(time.monotonic() - started, 15)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(self.grandchild_gone(pid_file), "a descendant outlived the probe that started it")

class Exit(Base):
    def test_a_failure_exits_one_listing_the_fix(self):
        self.host.power[host_check.STANDBYIDLE] = 1800
        code, out = self.main()
        self.assertEqual(code, 1)
        self.assertIn("FAIL  power", out)
        self.assertIn("fix: powercfg /change standby-timeout-ac 0", out)
        self.assertEqual(sum(line.startswith("ok ") for line in out.splitlines()), 7)

    def test_cannot_check_outranks_a_failure(self):
        self.host.power[host_check.STANDBYIDLE] = 1800
        self.host.session = host_check.Unreadable("no API")
        self.assertEqual(self.main()[0], 2)

    def test_a_crashing_check_exits_two_not_a_traceback(self):
        def crash():
            raise RuntimeError("vswhere wrote something unexpected")
        self.host.vswhere = crash
        code, out = self.main()
        self.assertEqual(code, 2)
        self.assertIn("ERROR toolchain", out)

    def test_a_probe_past_its_deadline_cannot_check_and_the_rest_still_report(self):
        self.host.probe_error["gh"] = subprocess.TimeoutExpired(["gh", "auth", "status"], 120)
        code, out = self.main()
        self.assertEqual(code, 2)
        self.assertIn("ERROR gh: could not check", out)
        self.assertEqual(sum(line.startswith("ok ") for line in out.splitlines()), 7)

    def test_a_failure_beside_a_timeout_exits_two_and_lists_the_fix(self):
        self.host.probe_error["gh"] = subprocess.TimeoutExpired(["gh"], 120)
        self.host.free = 1
        code, out = self.main()
        self.assertEqual(code, 2)
        self.assertIn("FAIL  disk", out)

    def test_notify_emails_the_lines_on_failure(self):
        self.host.gh_status = 1
        sent = []
        code, _ = self.main("--notify", mail=lambda root, subject, body: sent.append((subject, body)))
        self.assertEqual(code, 1)
        self.assertEqual(len(sent), 1)
        self.assertIn("campaign host not ready", sent[0][0])
        self.assertIn("gh auth login", sent[0][1])

    def test_notify_sends_nothing_when_ready(self):
        self.assertEqual(self.main("--notify")[0], 0)

    def test_a_failed_email_keeps_the_exit_code(self):
        self.host.gh_status = 1

        def broken(*args):
            raise OSError("network down")
        code, out = self.main("--notify", mail=broken)
        self.assertEqual(code, 1)
        self.assertIn("email not sent: network down", out)


if __name__ == "__main__":
    unittest.main()
