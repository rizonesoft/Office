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
        self.own = 1  # the campaign's own session
        self.power = {host_check.STANDBYIDLE: 0, host_check.HIBERNATEIDLE: 0}
        self.saver = {"active": True, "secure": False, "timeout": 3600}  # the live session's values
        self.values = {
            (host_check.HKCU, host_check.DESKTOP, "ScreenSaveActive"): "1",
            (host_check.HKCU, host_check.DESKTOP, "ScreenSaverIsSecure"): "0",
            (host_check.HKCU, host_check.DESKTOP, "SCRNSAVE.EXE"): r"C:\WINDOWS\system32\Mystify.scr",
            (host_check.HKCU, host_check.DESKTOP, "ScreenSaveTimeOut"): "3600",
            (host_check.HKLM, host_check.CLICK_TO_RUN, "InstallPath"): OFFICE,
            (host_check.HKLM, host_check.CLICK_TO_RUN + r"\Configuration", "VersionToReport"): "16.0.20430.20182",
        }
        self.files = {str(Path(OFFICE) / "root" / "Office16" / exe) for _, exe in host_check.OFFICE_APPS}
        self.files.add(r"C:\WINDOWS\system32\Mystify.scr")
        self.policy_changed = False
        self.tree = {"D02 T01 §24": section("D02 T01 §24", needs=["office", "display-session"])}
        self.instances = json.loads(json.dumps(FULL_VS))
        self.on_path = {"gh": r"C:\gh\gh.exe", "codex": r"C:\npm\codex.cmd"}
        self.gh_status = 0
        self.reviewer_status = 0
        self.probe_error = {}  # program name -> the exception its probe raises
        self.pin = ("sol", "codex")
        self.free = 300 * 10**9
        self.calls = []

    def own_session(self):
        return self.own

    def console_session(self):
        if isinstance(self.session, Exception):
            raise self.session
        return self.session

    def power_ac(self, subgroup, setting):
        assert subgroup == host_check.SUB_SLEEP
        return self.power[setting]

    def screen_saver(self):
        if isinstance(self.saver, Exception):
            raise self.saver
        return self.saver

    def registry(self, hive, key, name):
        return self.values.get((hive, key, name))

    def is_file(self, path):
        return str(path) in self.files

    def changed_since_boot(self, key):
        assert key == host_check.SYSTEM_POLICY
        return self.policy_changed

    def sections(self):
        if isinstance(self.tree, Exception):
            raise self.tree
        return [s.public() for s in todo_graph.ordered(self.tree)]

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

    def test_another_users_unlocked_console_fails(self):
        self.host.own = 2  # the campaign's user was switched away from; user B is at the console
        r = self.result("session")
        self.assertEqual(r["state"], "fail")
        self.assertIn("runs in session 2", r["detail"])

    def test_the_real_reader_knows_its_own_session(self):
        if host_check.os.name != "nt":
            self.skipTest("Windows sessions")
        self.assertIsInstance(host_check.Host().own_session(), int)

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
        self.host.saver["secure"] = True
        r = self.result("screen lock")
        self.assertEqual(r["state"], "fail")
        self.assertIn("On resume, display logon screen", r["fix"])

    def test_a_live_setting_that_differs_from_the_stored_profile_wins(self):
        # The stored profile says no lock; the live session (a temporary SystemParametersInfo setting) locks in 60 s.
        self.host.values[(host_check.HKCU, host_check.DESKTOP, "ScreenSaverIsSecure")] = "0"
        self.host.values[(host_check.HKCU, host_check.DESKTOP, "ScreenSaveTimeOut")] = "0"
        self.host.saver.update(secure=True, timeout=60)
        r = self.result("screen lock")
        self.assertEqual(r["state"], "fail")
        self.assertIn("after 60 seconds", r["detail"])

    def test_secure_screen_saver_by_policy_fails_naming_the_policy(self):
        self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, "ScreenSaverIsSecure")] = "1"
        r = self.result("screen lock")
        self.assertEqual(r["state"], "fail")
        self.assertIn("policy", r["fix"])

    def test_policy_turning_the_saver_off_passes(self):
        self.host.saver["secure"] = True
        self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, "ScreenSaveActive")] = "0"
        self.assertEqual(self.result("screen lock")["state"], "ok")

    def test_a_zero_timeout_never_starts_the_saver_so_it_passes(self):
        self.host.saver.update(secure=True, timeout=0)
        self.assertEqual(self.result("screen lock")["state"], "ok")

    def test_a_zero_timeout_set_by_policy_wins_over_the_users(self):
        self.host.saver["secure"] = True
        self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, "ScreenSaveTimeOut")] = "0"
        self.assertEqual(self.result("screen lock")["state"], "ok")

    def test_no_saver_program_never_locks(self):
        self.host.saver["secure"] = True
        del self.host.values[(host_check.HKCU, host_check.DESKTOP, "SCRNSAVE.EXE")]
        self.assertEqual(self.result("screen lock")["state"], "ok")

    def test_a_malformed_policy_flag_cannot_check(self):
        self.host.saver["secure"] = True
        for name in ("ScreenSaverIsSecure", "ScreenSaveActive"):
            with self.subTest(name=name):
                self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, name)] = "invalid"
                self.assertEqual(self.result("screen lock")["state"], "error")
                del self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, name)]

    def test_a_timeout_out_of_range_cannot_check(self):
        self.host.saver.update(secure=True, timeout=60)
        for value in ("-1", "86401"):
            with self.subTest(value=value):
                self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, "ScreenSaveTimeOut")] = value
                self.assertEqual(self.result("screen lock")["state"], "error")
        self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, "ScreenSaveTimeOut")] = "86400"
        self.assertEqual(self.result("screen lock")["state"], "fail")

    def test_an_unreadable_policy_timeout_cannot_check(self):
        self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, "ScreenSaveTimeOut")] = "soon"
        self.assertEqual(self.result("screen lock")["state"], "error")

    def test_a_failed_live_read_cannot_check(self):
        self.host.saver = host_check.Unreadable("SystemParametersInfoW 0x0076 failed (error 5)")
        self.assertEqual(self.result("screen lock")["state"], "error")

    def test_a_saver_program_that_does_not_exist_never_locks(self):
        self.host.saver["secure"] = True
        self.host.values[(host_check.HKCU, host_check.DESKTOP, "SCRNSAVE.EXE")] = r"C:\missing.scr"
        self.assertEqual(self.result("screen lock")["state"], "ok")

    def test_a_missing_forced_saver_falls_back_to_the_users_own(self):
        self.host.saver.update(secure=True, timeout=60)
        self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, "SCRNSAVE.EXE")] = r"C:\missing.scr"
        self.assertEqual(self.result("screen lock")["state"], "fail")

    def test_an_existing_forced_saver_is_the_one_that_runs(self):
        self.host.saver.update(secure=True, timeout=60)
        del self.host.values[(host_check.HKCU, host_check.DESKTOP, "SCRNSAVE.EXE")]
        self.host.values[(host_check.HKCU, host_check.DESKTOP_POLICY, "SCRNSAVE.EXE")] = r"C:\WINDOWS\system32\Mystify.scr"
        self.assertEqual(self.result("screen lock")["state"], "fail")

    def test_a_removed_inactivity_limit_needs_a_restart(self):
        self.host.policy_changed = True
        r = self.result("screen lock")
        self.assertEqual(r["state"], "fail")
        self.assertIn("restart Windows", r["fix"])

    S = 10**7

    def test_a_write_after_boot_is_seen(self):
        boot = 1000 * self.S
        self.assertTrue(host_check.written_since_boot(boot + 30 * self.S, boot, [], boot + 600 * self.S))
        self.assertFalse(host_check.written_since_boot(boot - 30 * self.S, boot, [], boot + 600 * self.S))

    def test_a_forward_correction_after_the_change_does_not_hide_it(self):
        # Round 16: booted at B, policy removed at B+30, the clock stepped forward 120 s at B+100.
        boot, s = 1000 * self.S, self.S
        steps = [(boot + 220 * s, boot + 100 * s)]
        self.assertTrue(host_check.written_since_boot(boot + 30 * s, boot, steps, boot + 720 * s))

    def test_a_write_stamped_while_the_clock_was_set_back_is_seen(self):
        # Round 17: back 120 s at B+60, policy removed at uptime 90 (stamped B-30), the clock restored at B-10.
        boot, s = 1000 * self.S, self.S
        steps = [(boot - 60 * s, boot + 60 * s), (boot + 130 * s, boot - 10 * s)]
        self.assertTrue(host_check.written_since_boot(boot - 30 * s, boot, steps, boot + 600 * s))

    def test_a_write_before_a_reboot_with_the_clock_set_back_is_not_pending(self):
        # Round 20: removed at 12:00, the clock set back, rebooted at 11:01: the restart applied the removal.
        h, m = 3600 * self.S, 60 * self.S
        self.assertFalse(host_check.written_since_boot(12 * h, 11 * h + 1 * m, [], 11 * h + 30 * m))

    def test_a_deleted_key_or_ancestor_shows_in_the_nearest_surviving_one(self):
        key = host_check.SYSTEM_POLICY
        parent = key.rpartition("\\")[0]
        grandparent = parent.rpartition("\\")[0]

        def stamps(present):
            def written(path):
                if path not in present:
                    raise FileNotFoundError(path)
                return present[path]
            return written
        self.assertEqual(host_check.write_times(key, stamps({key: 5, parent: 9})), [5, 9])
        self.assertEqual(host_check.write_times(key, stamps({parent: 7})), [7])  # the key was deleted
        self.assertEqual(host_check.write_times(key, stamps({grandparent: 8})), [8])  # its parent was deleted too
        with self.assertRaises(host_check.Unreadable):
            host_check.write_times(key, stamps({}))

    def test_each_stamp_is_judged_on_its_own(self):
        # Round 21: the parent stamped 12:00 before a rollback, a reboot at 11:01, the value removed at 11:10.
        h, m = 3600 * self.S, 60 * self.S
        boot, now = 11 * h + 1 * m, 11 * h + 30 * m
        stamps = [11 * h + 10 * m, 12 * h]  # the key, then its parent
        self.assertTrue(any(host_check.written_since_boot(s, boot, [], now) for s in stamps))
        self.assertFalse(host_check.written_since_boot(max(stamps), boot, [], now))  # what max() alone would see

    def test_clock_steps_are_read_from_the_time_change_events(self):
        def event(new, old):
            return f"<Event><EventData><Data Name='NewTime'>{new}</Data><Data Name='OldTime'>{old}</Data></EventData></Event>"
        xml = (event("2026-10-23T08:00:00.0000000Z", "2026-10-23T08:02:00.0000000Z")
               + event("2026-10-23T09:00:00.25Z", "2026-10-23T09:00:00Z"))
        steps = host_check.clock_steps(xml)
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0][1] - steps[0][0], 120 * self.S)
        self.assertEqual(steps[1][0] - steps[1][1], 2_500_000)
        self.assertEqual(host_check.clock_steps(""), [])
        quoted = ('<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event"><EventData>'
                  '<Data Name="NewTime">2026-10-23T08:00:00Z</Data><Data Name="OldTime">2026-10-23T08:00:10Z</Data>'
                  '</EventData></Event>')
        self.assertEqual(len(host_check.clock_steps(quoted)), 1)
        for bad in (event("yesterday", "2026-10-23T09:00:00Z"),
                    "<Event><EventData><Data Name='NewTime'>2026-10-23T08:00:00Z</Data></EventData></Event>",
                    event("2026-10-23T08:00:00Z", "2026-10-23T08:02:00Z")[:-20]):
            with self.subTest(bad=bad[-40:]), self.assertRaises(host_check.Unreadable):
                host_check.clock_steps(bad)

    def test_the_start_event_gives_its_record_and_time(self):
        xml = ("<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'><System>"
               "<TimeCreated SystemTime='2026-10-22T19:11:30.8640802Z'/><EventRecordID>31239</EventRecordID>"
               "</System></Event>")
        record, at = host_check.start_event(xml)
        self.assertEqual(record, 31239)
        self.assertEqual(at, host_check.ticks("2026-10-22T19:11:30.8640802Z"))
        self.assertIsNone(host_check.start_event(""))
        with self.assertRaises(host_check.Unreadable):
            host_check.start_event("<Event><System><EventRecordID>x</EventRecordID></System></Event>")

    def test_the_real_event_reader_runs(self):
        if host_check.os.name != "nt":
            self.skipTest("Windows event log")
        started, steps = host_check.Host().boot_clock()
        self.assertIsInstance(steps, list)
        self.assertGreater(started, 0)

    START = ("<Event><System><TimeCreated SystemTime='2026-10-22T19:11:30Z'/><EventRecordID>31239</EventRecordID>"
             "</System></Event>")

    def reader(self, started, changes):
        host = host_check.Host()
        outputs = iter([subprocess.CompletedProcess([], 0, started, ""), subprocess.CompletedProcess([], 0, changes, "")])
        host.run = lambda argv, seconds=None: next(outputs)
        return host

    def test_a_log_without_this_boots_start_event_cannot_vouch(self):
        with self.assertRaises(host_check.Unreadable) as caught:
            self.reader("", "").boot_clock()
        self.assertIn("start event", str(caught.exception))

    def test_steps_are_read_after_the_boot_record(self):
        calls = []
        host = self.reader(self.START, "")
        run = host.run
        host.run = lambda argv, seconds=None: calls.append(argv) or run(argv, seconds)
        self.assertEqual(host.boot_clock()[1], [])
        self.assertIn("EventRecordID > 31239", calls[1][3])

    def test_a_full_page_of_steps_cannot_vouch(self):
        page = ("<Event><EventData><Data Name='NewTime'>2026-10-23T08:00:00Z</Data>"
                "<Data Name='OldTime'>2026-10-23T08:00:00Z</Data></EventData></Event>")
        with mock.patch.object(host_check, "MAX_TIME_EVENTS", 3):
            self.assertEqual(len(self.reader(self.START, page * 2).boot_clock()[1]), 2)
            with self.assertRaises(host_check.Unreadable):
                self.reader(self.START, page * 3).boot_clock()

    def test_the_real_reader_compares_with_boot_time(self):
        if host_check.os.name != "nt":
            self.skipTest("Windows registry")
        self.assertIsInstance(host_check.Host().changed_since_boot(host_check.SYSTEM_POLICY), bool)

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

    def test_an_unreadable_build_cannot_check(self):
        key = (host_check.HKLM, host_check.CLICK_TO_RUN + r"\Configuration", "VersionToReport")
        for value in (None, "not-a-build", "16.0"):
            with self.subTest(value=value):
                self.host.values[key] = value
                self.assertEqual(self.result("office")["state"], "error")

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

    def test_a_git_timeout_reading_the_tree_still_checks_office(self):
        self.host.tree = subprocess.TimeoutExpired(["git", "rev-list", "HEAD"], 30)
        self.host.files.discard(str(Path(OFFICE) / "root" / "Office16" / "VISIO.EXE"))
        r = self.result("office")
        self.assertEqual(r["state"], "fail")
        self.assertIn("VISIO.EXE", r["detail"])

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

    def test_the_reader_runs_in_a_contained_child(self):
        calls = []
        real = self.host.run
        self.host.run = lambda argv, seconds=None: calls.append(argv) or real(argv, seconds)
        self.assertEqual(self.needed(), ["D02 T01 §1"])
        self.assertEqual(calls[0][:2], [sys.executable, "-c"])

    def test_a_reader_that_fails_falls_back_to_checking_office(self):
        self.host.run = lambda argv, seconds=None: subprocess.CompletedProcess(argv, 1, "", "Refused: broken tree")
        refs, note = host_check.office_needed(self.host)
        self.assertIsNone(refs)
        self.assertIn("Refused: broken tree", note)

    def test_incomplete_section_records_fall_back_to_checking_office(self):
        for printed in ("[{}]", "[]", '[{"ref": "D02 T01 §1", "done": false, "status": "active"}]'):
            with self.subTest(printed=printed):
                self.host.run = lambda argv, seconds=None, out=printed: subprocess.CompletedProcess(argv, 0, out, "")
                refs, note = host_check.office_needed(self.host)
                self.assertIsNone(refs)
                self.assertIn("cannot be read", note)

    def test_the_repository_tree_reads(self):
        rows = host_check.Host().sections()
        self.assertTrue(any(r["ref"] == "D00 T03 §12" for r in rows))

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

    def test_the_install_command_quotes_an_apostrophe_in_the_path(self):
        self.host.instances[0]["installationPath"] = "D:\\Owner's Tools\\VS"
        self.host.instances[0]["packages"] = [p for p in self.host.instances[0]["packages"]
                                              if p["id"] != "Microsoft.VisualStudio.Component.Vcpkg"]
        fix = self.result("toolchain")["fix"]
        self.assertIn("--installPath 'D:\\Owner''s Tools\\VS'", fix)

    def test_missing_windows_sdk_fails(self):
        self.host.instances[0]["packages"] = [p for p in self.host.instances[0]["packages"]
                                              if "Windows11SDK" not in p["id"]]
        r = self.result("toolchain")
        self.assertEqual(r["state"], "fail")
        self.assertIn(host_check.WINDOWS_SDK_ADD, r["fix"])

    def test_no_visual_studio_fails(self):
        self.host.instances = None
        self.assertEqual(self.result("toolchain")["state"], "fail")

    def test_an_instance_without_its_path_cannot_check(self):
        host = host_check.Host()
        host.run = lambda argv, seconds=None: subprocess.CompletedProcess(argv, 0, "[{}]", "")
        with mock.patch.object(host_check, "VSWHERE", Path(sys.executable)), \
                self.assertRaises(host_check.Unreadable):
            host.vswhere()

    def test_an_instance_with_a_malformed_version_cannot_check(self):
        host = host_check.Host()
        record = json.loads(json.dumps(FULL_VS))
        record[0]["installationVersion"] = "not-a-version"
        host.run = lambda argv, seconds=None: subprocess.CompletedProcess(argv, 0, json.dumps(record), "")
        with mock.patch.object(host_check, "VSWHERE", Path(sys.executable)), \
                self.assertRaises(host_check.Unreadable):
            host.vswhere()

    def test_a_complete_record_is_accepted(self):
        host = host_check.Host()
        host.run = lambda argv, seconds=None: subprocess.CompletedProcess(argv, 0, json.dumps(FULL_VS), "")
        with mock.patch.object(host_check, "VSWHERE", Path(sys.executable)):
            self.assertEqual(host.vswhere()[0]["installationVersion"], "18.11.12315.225")

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

    def test_a_crashed_gh_cannot_check(self):
        self.host.gh_status = 0xC0000005  # access violation
        r = self.result("gh")
        self.assertEqual(r["state"], "error")
        self.assertIn("0xc0000005", r["detail"])

    def test_a_gh_killed_by_a_signal_cannot_check(self):
        self.host.gh_status = -9
        self.assertEqual(self.result("gh")["state"], "error")

    def test_a_crashed_reviewer_cli_cannot_check(self):
        self.host.reviewer_status = 0xC0000005
        code, out = self.main()
        self.assertEqual(code, 2)
        self.assertIn("ERROR reviewer", out)
        self.assertNotIn("fix: codex login", out)

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
        # Reading the file while the grandchild replaces it can fail on Windows (a sharing violation), so the parent
        # retries rather than exiting early, which made this test pass a probe that never hung.
        parent = (f"import pathlib, subprocess, sys, time; subprocess.Popen([sys.executable, '-c', {grandchild!r}]); "
                  f"p = pathlib.Path({str(pid_file)!r})\n"
                  f"def ready():\n"
                  f"    try:\n"
                  f"        return bool(p.read_text())\n"
                  f"    except OSError:\n"
                  f"        return False\n"
                  f"while not ready(): time.sleep(0.01)\n"
                  f"time.sleep({sleep})")
        return [sys.executable, "-c", parent], pid_file

    def grandchild_gone(self, pid_file):
        for _ in range(100):
            try:
                pid = int(pid_file.read_text())
                break
            except (OSError, ValueError):  # not written yet, or being replaced
                time.sleep(0.05)
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

    def test_the_notice_reaches_the_sender_in_a_child(self):
        seen = self.tmp / "seen.json"
        code = ("import json, sys\nn = json.load(open(sys.argv[2], encoding='utf-8'))\n"
                f"open({str(seen)!r}, 'w', encoding='utf-8').write(json.dumps(n))\n")
        with mock.patch.object(host_check, "NOTICE_CODE", code):
            host_check.Host().notify("subject", "body")
        self.assertEqual(json.loads(seen.read_text(encoding="utf-8"))["subject"], "subject")

    def test_a_sender_that_fails_is_reported(self):
        with mock.patch.object(host_check, "NOTICE_CODE", "import sys; sys.exit('Refused: no vault key')"):
            with self.assertRaises(host_check.Unreadable) as caught:
                host_check.Host().notify("s", "b")
        self.assertIn("Refused: no vault key", str(caught.exception))

    def test_a_sender_that_hangs_is_ended_at_its_deadline(self):
        argv, pid_file = self.tree(60)
        code = argv[2]
        started = time.monotonic()
        with mock.patch.object(host_check, "NOTICE_CODE", code), mock.patch.object(host_check, "NOTIFY_SECONDS", 2):
            with self.assertRaises(host_check.Unreadable):
                host_check.Host().notify("s", "b")
        self.assertLess(time.monotonic() - started, 20)
        self.assertTrue(self.grandchild_gone(pid_file))

    def test_a_probe_starts_in_a_scratch_folder_not_the_repository(self):
        r = host_check.Host().run([sys.executable, "-c", "import os; print(os.getcwd())"])
        where = Path(r.stdout.strip())
        self.assertEqual(where.name, "work")
        self.assertNotEqual(where.resolve(), Path.cwd().resolve())

    @unittest.skipUnless(os.name == "nt", "the job memory limit is the Windows containment")
    def test_a_nested_capture_is_held_to_the_job_memory_limit(self):
        grandchild = "x = bytearray(600 * 1024 * 1024); print(len(x))"
        parent = f"import subprocess, sys; sys.exit(subprocess.run([sys.executable, '-c', {grandchild!r}]).returncode)"
        with mock.patch.object(host_check, "PROBE_MEMORY_BYTES", 256 * 1024 * 1024):
            r = host_check.Host().run([sys.executable, "-c", parent], seconds=60)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("629145600", r.stdout)

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
        code, _ = self.main("--notify", mail=lambda subject, body: sent.append((subject, body)))
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
