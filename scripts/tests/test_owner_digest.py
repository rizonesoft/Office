# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Tests for scripts/owner-digest.py: the owner's one weekly email (D00 T03 §35)."""
import base64
import datetime
import importlib.util
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import types
import unittest
from contextlib import redirect_stdout
from unittest import mock

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
sys.path.insert(0, str(REPO / "scripts" / "tests"))
import todo_graph as tg  # noqa: E402  (the library sits beside the scripts, not on the path)
from test_todo_graph import FIXTURE_ACTION, todo_file  # noqa: E402  (the shared TODO fixtures)

SPEC = importlib.util.spec_from_file_location("owner_digest", REPO / "scripts" / "owner-digest.py")
digest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(digest)

TODAY = datetime.date(2026, 11, 16)
ACTION = FIXTURE_ACTION.split("**Owner action:** ", 1)[1].strip()


def waiting_file(rows, ident="alpha", name="TODO-01-a.md"):
    """A todo_file; its sections waiting on the owner carry the fixture's owner action (FIXTURE_ACTION)."""
    return todo_file(rows, ident=ident), name


class Tree(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        (self.root / ".conclave" / "automations").mkdir(parents=True)
        (self.root / ".conclave/automations/alert.py").write_bytes((REPO / ".conclave/automations/alert.py").read_bytes())
        (self.root / "scripts/lib").mkdir(parents=True)
        (self.root / "scripts/lib/secret_store.py").write_bytes((REPO / "scripts/lib/secret_store.py").read_bytes())
        # The digest's second store of delivery evidence lives under the scratch folder: a private one per test.
        scratch = mock.patch.dict(os.environ, {"OFFICE_SCRATCH": str(self.root / "scratch")})
        scratch.start()
        self.addCleanup(scratch.stop)
        pause = mock.patch.object(digest, "MARK_PAUSE", 0)
        pause.start()
        self.addCleanup(pause.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, text, name="TODO-01-a.md", domain="00-workspace"):
        folder = self.root / "todo" / domain
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text(text, encoding="utf-8")
        index = folder / "INDEX.md"
        index.write_text((index.read_text(encoding="utf-8") if index.exists() else "# Index\n") + f"- {name}\n",
                         encoding="utf-8")
        top = self.root / "todo/TODO-00-INDEX.md"
        top.write_text((top.read_text(encoding="utf-8") if top.exists() else "# Index\n") + f"- {domain}/{name}\n",
                       encoding="utf-8")

    def rows(self):
        return tg.graph(self.root)


class Waiting(Tree):
    def test_a_waiting_section_is_listed_with_its_action_and_everything_behind_it(self):
        self.write(*waiting_file([(1, "Ask", 0, "owner-decision", "--"), (2, "Next", 0, "none", "§1"),
                                  (3, "Then", 0, "none", "§2")]))
        items = digest.waiting(self.rows())
        self.assertEqual([(i["ref"], i["behind"], i["needs"]) for i in items], [("D00 T01 §1", 2, ["owner-decision"])])
        self.assertEqual(items[0]["action"], ACTION)
        lines = "\n".join(digest.item_lines(items[0], self.root))
        self.assertIn("2 open sections wait behind it", lines)
        self.assertIn("To do: " + ACTION[:40], lines)

    def test_the_list_is_ordered_by_what_waits_behind_largest_first(self):
        self.write(*waiting_file([(1, "Small", 0, "operator", "--"), (2, "Big", 0, "third-party", "--"),
                                  (3, "A", 0, "none", "§2"), (4, "B", 0, "none", "§2"), (5, "C", 0, "none", "§1")]))
        self.assertEqual([i["ref"] for i in digest.waiting(self.rows())], ["D00 T01 §2", "D00 T01 §1"])

    def test_nothing_waiting_says_so(self):
        self.write(*waiting_file([(1, "A", 0, "none", "--")]))
        _, body, attachments = digest.compose(self.root, self.rows(), TODAY, ["CI: green for abc1234."], "Running")
        self.assertIn("Nothing is waiting on you.", body)
        self.assertEqual(attachments, [])


class Progress(unittest.TestCase):
    def test_only_receipts_dated_in_the_last_seven_days_are_listed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            rows = {}
            # Review round 3: the window reaches back to last Monday (11-09), a day before 11-10, and stops there.
            for n, date in ((1, "2026-11-16"), (2, "2026-11-09"), (3, "2026-11-08")):
                receipt = f"docs/reviews/r{n}.json"
                (root / receipt).parent.mkdir(parents=True, exist_ok=True)
                (root / receipt).write_text(json.dumps({"date": date}), encoding="utf-8")
                rows[f"D00 T01 §{n}"] = types.SimpleNamespace(done=True, receipt=receipt, ref=f"D00 T01 §{n}",
                                                               title=f"S{n}")
            rows["D00 T01 §4"] = types.SimpleNamespace(done=False, receipt="", ref="D00 T01 §4", title="Open")
            found = digest.verified_since(root, rows, TODAY)
        self.assertEqual([ref for ref, _, _ in found], ["D00 T01 §1", "D00 T01 §2"])


class RunState(Tree):
    def run_file(self, name, text):
        folder = self.root / "docs/phase-runs"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text(text, encoding="utf-8")

    def guard_with_life(self, transcript_age=None, guard_text=None):
        """A guard for session `s-1234567`, and that session's transcript `transcript_age` seconds old (or none)."""
        (self.root / "build").mkdir(exist_ok=True)
        (self.root / "build/claude-campaign-guard.json").write_text(guard_text or json.dumps(
            {"run_id": "abc", "phase": 2, "run_file": "docs/phase-runs/x.md", "session_id": "s-1234567",
             "job_created_at": "2026-11-12T01:00:00Z"}), encoding="utf-8")
        config = self.root / "claude-config"
        (config / "projects" / "P").mkdir(parents=True, exist_ok=True)
        if transcript_age is not None:
            path = config / "projects" / "P" / "s-1234567.jsonl"
            path.write_text("{}\n", encoding="utf-8")
            when = time.time() - transcript_age
            os.utime(path, (when, when))
        return digest.run_state(self.root, config_dir=str(config))

    def test_a_guard_whose_session_shows_life_is_running(self):
        line = self.guard_with_life(transcript_age=60)
        self.assertTrue(line.startswith("Running: run abc, phase 2, docs/phase-runs/x.md (last sign of life "), line)

    def test_a_guard_whose_session_went_quiet_is_stalled(self):
        line = self.guard_with_life(transcript_age=5 * 3600)
        self.assertTrue(line.startswith("Stalled since "), line)
        self.assertIn("run abc, phase 2", line)
        (self.root / "claude-config" / "projects" / "P" / "s-1234567.jsonl").unlink()  # no sign of life at all
        self.assertTrue(self.guard_with_life().startswith("Stalled since 2026-11-12T01:00:00Z"))

    def test_a_malformed_guard_is_unknown(self):
        self.assertTrue(self.guard_with_life(guard_text="{nope").startswith("Unknown: the run guard cannot be read"))

    def test_each_ending_of_the_newest_run_file(self):
        cases = [("## Closeout run=abc\n", "Completed"),
                 ("PARKED 2026-11-11T00:00:00Z run=abc host-not-ready: session locked\n", "Parked: 2026-11-11"),
                 ("- 2026-11-10T22:56:41Z operator stop (said in session).\n", "Stopped by the operator"),
                 ("- nothing ended here\n", "Not running")]
        for text, expected in cases:
            with self.subTest(expected=expected):
                self.run_file("2026-11-11-phase-0.md", "# Phase run\n\n- 2026-11-11T01:00:00Z opened\n" + text)
                self.run_file("2026-11-10-phase-0.md", "- 2026-11-10T01:00:00Z opened\n## Closeout run=old\n")  # older
                self.assertTrue(digest.run_state(self.root).startswith(expected), digest.run_state(self.root))

    def test_the_operator_stop_as_the_real_run_file_records_it(self):
        recorded = (REPO / "docs/phase-runs/2026-11-11-phase-0.md").read_text(encoding="utf-8")
        self.run_file("2026-11-11-phase-0.md", recorded)
        self.assertTrue(digest.run_state(self.root).startswith("Stopped by the operator"))

    def test_a_later_suffix_is_newer(self):
        self.run_file("2026-11-11-phase-0.md", "- 2026-11-11T00:30:00Z opened\n## Closeout run=a\n")
        self.run_file("2026-11-11-phase-0-2.md", "PARKED 2026-11-11T01:00:00Z run=b ci-red: gates\n")
        self.assertTrue(digest.run_state(self.root).startswith("Parked"))

    def test_the_last_ending_wins(self):
        # Review round 1, finding 4: a phase closeout followed by the campaign's park read as Completed.
        self.run_file("2026-11-11-phase-0.md", "## Closeout run=a\n\nPARKED 2026-11-11T05:00:00Z run=a no ready row\n")
        self.assertTrue(digest.run_state(self.root).startswith("Parked"), digest.run_state(self.root))
        self.run_file("2026-11-11-phase-0.md", "PARKED 2026-11-11T05:00:00Z run=a x\n\n## Closeout run=b\n")
        self.assertTrue(digest.run_state(self.root).startswith("Completed"))

    def test_a_mention_of_an_operator_stop_in_prose_is_no_stop(self):
        # Review round 2, finding 2: the word anywhere in the file, a lesson or an audit line, read as a stop.
        self.run_file("2026-11-11-phase-0.md", "- 2026-11-11T01:00:00Z opened; the earlier run's operator stop named"
                      " the next row\n\n## Closeout run=a\n\n## Lessons\n\n- An operator stop is always honoured.\n")
        self.assertTrue(digest.run_state(self.root).startswith("Completed"), digest.run_state(self.root))

    def test_the_newest_run_file_is_the_one_last_written_by_the_run(self):
        # Review round 1, finding 5: 2026-11-11-phase-0-2.md sorted after 2026-11-11-phase-1.md, written later.
        self.run_file("2026-11-11-phase-0-2.md", "- 2026-11-11T03:00:00Z opened\n## Closeout run=a\n")
        self.run_file("2026-11-11-phase-1.md", "- 2026-11-11T04:00:00Z opened\nPARKED 2026-11-11T05:00:00Z run=b x\n")
        self.assertTrue(digest.run_state(self.root).startswith("Parked"), digest.run_state(self.root))

    def test_an_unreadable_run_file_names_no_full_path(self):
        # Review round 1, finding 2: the error text carried the absolute path of the file.
        (self.root / "build").mkdir()
        # The guard is read by campaign_guard.liveness now (D00 T07 §1), so it is made unreadable for real: a folder
        # where the file should be.
        (self.root / "build/claude-campaign-guard.json").mkdir()
        state = digest.run_state(self.root)
        self.assertTrue(state.startswith("Unknown: the run guard cannot be read (the guard file "
                                         "build/claude-campaign-guard.json does not parse"), state)
        self.assertNotIn(str(self.root), state)

    def test_an_unreadable_guard_is_unknown(self):
        (self.root / "build").mkdir()
        (self.root / "build/claude-campaign-guard.json").write_text("{not json", encoding="utf-8")
        self.assertTrue(digest.run_state(self.root).startswith("Unknown"))


class Ci(unittest.TestCase):
    def runner(self, code, out="", err="", raises=None):
        def run(argv, **kwargs):
            if raises:
                raise raises
            return subprocess.CompletedProcess(argv, code, out, err)
        return run

    def state(self, runner):
        with mock.patch.object(digest, "git", return_value="a" * 40):
            return digest.ci_state(REPO, runner)

    def test_green_red_pending_and_unknown(self):
        self.assertEqual(self.state(self.runner(0, "green aaaa")), ["CI: green for aaaaaaa."])
        red = self.state(self.runner(1, "red aaaa run 1\n  gates (failure): Run the tooling tests (failure)\n"))
        self.assertEqual(red[0], "CI: red for aaaaaaa.")
        self.assertIn("gates (failure)", red[1])
        self.assertEqual(self.state(self.runner(3, "pending aaaa")), ["CI: pending for aaaaaaa."])
        unknown = self.state(self.runner(2, "", "gh: not signed in\n"))
        self.assertTrue(unknown[0].startswith("CI: unknown for aaaaaaa"), unknown)

    def test_red_keeps_every_unsuccessful_job_the_producer_names(self):
        # Review round 1, finding 3: a cancelled or timed-out job was dropped.
        red = self.state(self.runner(1, "red aaaa run 1\n  gates (cancelled): Build (cancelled)\n"
                                        "  icons (timed_out): Render (timed_out)\n"))
        self.assertEqual(red, ["CI: red for aaaaaaa.", "  gates (cancelled): Build (cancelled)",
                               "  icons (timed_out): Render (timed_out)"])

    def test_a_git_that_hangs_is_unknown_ci_not_a_crash(self):
        # Review round 1, finding 1: git() raised out of ci_state.
        with mock.patch.object(digest.subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 60)):
            self.assertEqual(digest.ci_state(REPO, self.runner(0)), ["CI: unknown (origin/main cannot be fetched)."])

    def test_long_ci_lines_are_wrapped_in_the_body(self):
        # Review round 1, finding 6.
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            long = "CI: unknown for aaaaaaa (" + "the network said no " * 8 + ")."
            with mock.patch.object(digest, "totals", return_value=dict.fromkeys(
                    ("total", "verified", "ready", "blocked", "to_author"), 0)), \
                    mock.patch.object(digest, "waiting", return_value=[]), \
                    mock.patch.object(digest, "verified_since", return_value=[]):
                _, body, _ = digest.compose(root, {}, TODAY, [long], "Running")
        self.assertTrue(all(len(line) <= digest.WIDTH for line in body.splitlines()))
        self.assertIn("the network said no", body)

    def test_every_launch_opens_no_window(self):
        # Review round 4: run.py's convention is CREATE_NO_WINDOW on every nested launch of a task.
        flags = []

        def record(argv, **kwargs):
            flags.append(kwargs.get("creationflags"))
            return subprocess.CompletedProcess(argv, 0, "a" * 40, "")
        with mock.patch.object(digest.subprocess, "run", record):
            digest.ci_state(REPO, record)
        self.assertEqual(len(flags), 3)  # git fetch, git rev-parse, ci-status.py
        self.assertEqual(set(flags), {digest.NO_WINDOW})

    def test_an_unreachable_runner_or_ref_never_stops_the_email(self):
        self.assertTrue(self.state(self.runner(0, raises=subprocess.TimeoutExpired("ci", 300)))[0].startswith(
            "CI: unknown"))
        with mock.patch.object(digest, "git", return_value=None):
            self.assertEqual(digest.ci_state(REPO, self.runner(0)), ["CI: unknown (origin/main cannot be fetched)."])


class Size(Tree):
    def many(self, count):
        for f in range(count // 50):
            rows = [(n, f"Ask {f}-{n}", 0, "owner-decision", "--") for n in range(1, 51)]
            self.write(*waiting_file(rows, ident=f"file-{f:02d}", name=f"TODO-{f + 1:02d}-f.md"))

    # D00 T07 §2: a long week of stamps.

    def stamps(self, count, long_titles=False):
        title = ("A section whose title is long enough to wrap onto a second line of the body when it is shown in "
                 "the digest") if long_titles else "Short"
        return [(f"D09 T01 §{n}", f"{title} {n}", TODAY - datetime.timedelta(days=n % 7)) for n in range(1, count + 1)]

    def composed(self, built, notices=(), unconfirmed=()):
        with mock.patch.object(digest, "verified_since", return_value=built):
            return digest.compose(self.root, self.rows(), TODAY, ["CI: green for abc1234."], "Running",
                                  notices=notices, unconfirmed=unconfirmed)

    def check_limits(self, body):
        lines = body.splitlines()
        self.assertLessEqual(len(lines), digest.BODY_LINES)
        self.assertTrue(all(len(line) <= digest.WIDTH for line in lines), max(lines, key=len))
        self.assertEqual(lines[2], "Running")
        self.assertTrue(lines[3].startswith("CI: "))
        self.assertTrue(lines[4].startswith("Plan: "))
        return lines

    def shown_and_said(self, body, prefix, noun):
        shown = sum(1 for line in body.splitlines() if line.startswith(prefix))
        said = re.search(rf"\.\.\. and (\d+) more {noun}", " ".join(body.splitlines()))
        return shown, int(said[1]) if said else 0

    def test_a_long_progress_list_alone_goes_in_its_own_attachment(self):
        self.write(*waiting_file([(1, "Ask", 0, "owner-decision", "--")]))
        _, body, attachments = self.composed(self.stamps(130))
        lines = self.check_limits(body)
        self.assertEqual([name for name, _ in attachments], [digest.PROGRESS_ATTACHMENT])
        self.assertEqual(attachments[0][1].count("\n- D09 T01 §"), 130)
        self.assertIn("Waiting on you (1):", body)  # the waiting list is whole in the body and not attached
        shown, said = self.shown_and_said(body, "- D09 T01 §", "verified sections this week")
        self.assertEqual(shown + said, 130)
        self.assertGreater(shown, 0)
        self.assertTrue(lines[-1].endswith(f"{digest.PROGRESS_ATTACHMENT}."), lines[-1])

    def test_both_lists_overflowing_go_in_their_attachments(self):
        self.many(300)
        _, body, attachments = self.composed(self.stamps(130))
        lines = self.check_limits(body)
        self.assertEqual([name for name, _ in attachments], [digest.ATTACHMENT, digest.PROGRESS_ATTACHMENT])
        self.assertEqual(attachments[0][1].count("To do: "), 300)
        self.assertEqual(attachments[1][1].count("\n- D09 T01 §"), 130)
        shown, said = self.shown_and_said(body, "- D09 T01 §", "verified sections this week")
        self.assertEqual(shown + said, 130)
        self.assertGreaterEqual(shown, 1)
        waited, more = self.shown_and_said(body, "- D00 T", "waiting on you")
        self.assertEqual(waited + more, 300)
        self.assertIn(digest.ATTACHMENT, lines[-1] + lines[-2])
        self.assertIn(digest.PROGRESS_ATTACHMENT, lines[-1] + lines[-2])

    def test_a_wrapped_entry_is_shown_whole_or_not_at_all(self):
        self.write(*waiting_file([(1, "Ask", 0, "owner-decision", "--")]))
        _, body, _ = self.composed(self.stamps(130, long_titles=True))
        lines = self.check_limits(body)
        starts = [i for i, line in enumerate(lines) if line.startswith("- D09 T01 §")]
        for i in starts:  # every shown entry has its second line right after it
            self.assertTrue(lines[i + 1].startswith("shown in the digest "), lines[i:i + 2])
        shown, said = self.shown_and_said(body, "- D09 T01 §", "verified sections this week")
        self.assertEqual(shown + said, 130)

    def test_notices_keep_their_room_beside_two_overflowing_lists(self):
        self.many(300)
        notices = [{"at": f"2026-11-1{n % 6}T00:00:00Z", "sender": "office-task", "subject": f"Notice {n}",
                    "body": f"Body {n}"} for n in range(20)]
        unconfirmed = [{"at": "2026-11-02T00:00:00Z", "sender": "office-task", "subject": "Old", "body": "Old body",
                        "claimed": {"at": "2026-11-09T07:00:00Z"}}]
        _, body, attachments = self.composed(self.stamps(130), notices=notices, unconfirmed=unconfirmed)
        lines = self.check_limits(body)
        self.assertIn("Notices since the last digest (20):", body)
        self.assertIn("could not be confirmed delivered", body)
        self.assertEqual([name for name, _ in attachments],
                         [digest.ATTACHMENT, digest.PROGRESS_ATTACHMENT, digest.NOTICES_ATTACHMENT])
        joined = " ".join(lines)
        for name in (digest.ATTACHMENT, digest.PROGRESS_ATTACHMENT, digest.NOTICES_ATTACHMENT):
            self.assertIn(name, joined)
        self.assertEqual(attachments[2][1].count("Body "), 20)
        self.assertIn("Old body", attachments[2][1])

    def test_an_unreadable_queue_keeps_its_line_when_both_lists_overflow(self):
        self.many(300)
        _, body, _ = self.composed(self.stamps(130), notices="permission denied")
        self.check_limits(body)
        self.assertIn("Notices: the queue could not be read", body)

    def test_a_long_waiting_list_is_cut_in_the_body_and_whole_in_the_attachment(self):
        self.many(300)
        _, body, attachments = digest.compose(self.root, self.rows(), TODAY, ["CI: green for abc1234."], "Running")
        lines = body.splitlines()
        self.assertLessEqual(len(lines), digest.BODY_LINES)
        self.assertTrue(all(len(line) <= digest.WIDTH for line in lines))
        self.assertIn(f"in the attached {digest.ATTACHMENT}", body)
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0][0], digest.ATTACHMENT)
        self.assertEqual(attachments[0][1].count("\n- D00 T"), 300)
        self.assertEqual(attachments[0][1].count("To do: "), 300)
        self.assertEqual(lines[2], "Running")  # the run state, CI and totals stay at the top
        self.assertTrue(lines[3].startswith("CI: "))
        # Review round 2, finding 3: the attachment's pointer is the body's last line.
        self.assertIn(f"in the attached {digest.ATTACHMENT}", " ".join(lines[-2:]))
        self.assertTrue(lines[-1].endswith(f"{digest.ATTACHMENT}."), lines[-1])

    def test_a_remote_that_cannot_be_fetched_is_unknown_ci(self):
        # Review round 2, finding 1: the cached origin/main was checked, which may be a week old.
        calls = []

        def fake_git(root, *args):
            calls.append(args)
            return None if args[0] == "fetch" else "a" * 40
        with mock.patch.object(digest, "git", fake_git):
            self.assertEqual(digest.ci_state(self.root, lambda *a, **k: None),
                             ["CI: unknown (origin/main cannot be fetched)."])
        self.assertEqual(calls[0][:2], ("fetch", "--quiet"))

    def test_every_kind_of_absolute_path_is_kept_out_of_the_email(self):
        # Review rounds 1 and 5: paths reached the email from a run-file error and from gh's error via ci-status.py.
        root = pathlib.Path(r"D:\Office")
        cases = [
            (r"CI: unknown (gh: cannot read C:\Users\Owner\AppData\Roaming\GitHub CLI\config.yml).",
             "CI: unknown (gh: cannot read <path outside the repository>)."),
            (r"read \\?\C:\Users\me\x.txt, then stopped", "read <path outside the repository>, then stopped"),
            (r"share \\server\share\folder\f.txt", "share <path outside the repository>"),
            ("mounts /home/me/x and /mnt/r/scratch", "mounts <path outside the repository>"),
            (r"inside D:\Office\build\x.json here", r"inside build\x.json here"),
            ("inside D:/Office/build/x.json here", "inside build/x.json here"),
            # Review round 7: a sibling sharing the prefix, and a climb out of the tree, are paths outside.
            (r"backup D:\Office-backup\private\config.yml", "backup <path outside the repository>"),
            (r"climb D:\Office\..\Private\config.yml", "climb <path outside the repository>"),
            (r"climb D:\Office\build\..\..\Private\x", "climb <path outside the repository>"),
            (r"stays D:\Office\build\..\docs\x.md", r"stays build\..\docs\x.md"),
            ("relative scripts/owner-digest.py and docs/x.md stay", "relative scripts/owner-digest.py and docs/x.md stay"),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(digest.without_paths(text, root), expected)

    def test_a_path_in_any_part_of_the_email_is_removed(self):
        self.many(50)
        leaked = r"CI: unknown for aaaaaaa (gh: open C:\Users\Owner\AppData\Roaming\GitHub CLI\config.yml)."
        _, body, _ = digest.compose(self.root, self.rows(), TODAY, [leaked], r"Unknown: D:\Secret\run.md")
        self.assertNotIn("Owner", body)
        self.assertNotIn("Secret", body)
        self.assertIn("<path outside the repository>", body)

    def test_a_long_path_is_cleared_before_it_is_wrapped_and_lines_stay_in_width(self):
        # Review round 6: the guard ran on wrapped lines, so a long path's continuation and a placeholder longer than
        # a short path both slipped through.
        self.many(50)
        long = (r"CI: unknown for aaaaaaa (gh: cannot read "
                r"C:\Users\Owner\AppData\Roaming\GitHub CLI\profiles\work-account\config.yml).")
        short = "x" * 71 + r" C:\a."
        _, body, attachments = digest.compose(self.root, self.rows(), TODAY, [long, short], "Running")
        for text in (body, *(t for _, t in attachments)):
            self.assertNotIn("work-account", text)
            self.assertNotIn("Owner", text)
        self.assertTrue(all(len(line) <= digest.WIDTH for line in body.splitlines()))

    def test_no_line_names_a_path_outside_the_repository(self):
        self.many(50)
        _, body, attachments = digest.compose(self.root, self.rows(), TODAY, ["CI: green for abc1234."], "Running")
        for text in (body, *(t for _, t in attachments)):
            self.assertIsNone(re.search(r"[A-Za-z]:\\|/mnt/|/home/|\\Users\\", text))


class Send(Tree):
    def setUp(self):
        super().setUp()
        self.write(*waiting_file([(1, "Ask", 0, "operator", "--")]))

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    activity = None  # SMTP2GO's activity log as the fake serves it: a list of events, or an exception to raise

    def run_main(self, argv, opener=None, attach=False):
        requests = []
        self.searches = getattr(self, "searches", [])

        def capture(request, timeout=None):
            if request.full_url.endswith("/activity/search"):  # the delivery evidence (D00 T03 §53)
                self.searches.append(json.loads(request.data.decode()))
                if isinstance(self.activity, Exception):
                    raise self.activity
                return self.Response(json.dumps({"data": {"events": self.activity or []}}).encode())
            requests.append(json.loads(request.data.decode()))
            return self.Response(json.dumps({"data": {"succeeded": 1, "failed": 0, "email_id": "e1"}}).encode())

        out = io.StringIO()
        with mock.patch.object(digest, "ci_state", return_value=["CI: green for abc1234."]), \
                mock.patch.object(digest, "run_state", return_value="Running"), redirect_stdout(out):
            alert = digest.load_alert(self.root)

            def no_network(*a, **kw):
                raise AssertionError("a test reached the network")
            with mock.patch.object(digest, "load_alert", return_value=alert), \
                    mock.patch.object(alert, "key", return_value="k"), \
                    mock.patch.object(alert.urllib.request, "urlopen", no_network):
                if attach:
                    real = digest.compose
                    with mock.patch.object(digest, "compose",
                                           side_effect=lambda *a: (*real(*a)[:2],
                                                                   [("waiting-on-you.txt", "the whole list\n")])):
                        code = digest.main(argv, root=self.root, today=TODAY, opener=opener or capture)
                else:
                    code = digest.main(argv, root=self.root, today=TODAY, opener=opener or capture)
        return code, out.getvalue(), requests

    def test_dry_run_prints_the_email_and_sends_nothing(self):
        code, out, requests = self.run_main(["--dry-run"])
        self.assertEqual(code, 0)
        self.assertEqual(requests, [])
        self.assertIn("Subject: Office weekly: 1 waiting on you", out)
        self.assertIn("D00 T01 §1 Ask [operator]", out)

    def test_a_send_is_one_request_with_the_digest_as_its_body(self):
        code, out, requests = self.run_main([])
        self.assertEqual(code, 0, out)
        self.assertEqual(len(requests), 1)
        self.assertIn("D00 T01 §1 Ask [operator]", requests[0]["text_body"])
        self.assertNotIn("attachments", requests[0])

    def test_an_overflowing_list_is_sent_as_an_attachment(self):
        code, _, requests = self.run_main([], attach=True)
        self.assertEqual(code, 0)
        attached = requests[0]["attachments"]
        self.assertEqual([(a["filename"], a["mimetype"]) for a in attached], [("waiting-on-you.txt", "text/plain")])
        self.assertEqual(base64.b64decode(attached[0]["fileblob"]).decode(), "the whole list\n")

    def test_a_refused_send_exits_1(self):
        def refuse(request, timeout=None):
            return self.Response(json.dumps({"data": {"succeeded": 0, "failed": 1}}).encode())
        code, _, _ = self.run_main([], opener=refuse)
        self.assertEqual(code, 1)


class Notices(Send):
    """The queued notices in the digest, and the batch marked only once it was delivered (D00 T03 §53)."""

    def queue(self, count, body_lines=60):
        alert = digest.load_alert(self.root)
        return [alert.record_notice("run.py", f"Office automation failed: task-{n}",
                                    "\n".join(f"log line {i} of failure {n}" for i in range(body_lines)), str(self.root))
                for n in range(count)]

    def pending(self):
        return [n["id"] for n in digest.load_alert(self.root).pending_notices(str(self.root))]

    def test_long_notices_are_summarised_in_the_body_and_whole_in_the_attachment(self):
        ids = self.queue(14)
        code, out, requests = self.run_main([])
        self.assertEqual(code, 0, out)
        body = requests[0]["text_body"]
        self.assertLessEqual(len(body.splitlines()), digest.BODY_LINES)
        self.assertIn("Notices since the last digest (14):", body)
        self.assertIn("D00 T01 §1 Ask [operator]", body)  # the waiting list is intact
        self.assertIn("Office weekly: 1 waiting on you", requests[0]["subject"])
        self.assertLess(body.index("Waiting on you"), body.index("Notices since the last digest"))
        attached = {a["filename"]: base64.b64decode(a["fileblob"]).decode() for a in requests[0]["attachments"]}
        for n in range(14):
            self.assertIn(f"task-{n}", attached["notices.txt"])
            self.assertIn(f"log line 59 of failure {n}", attached["notices.txt"])
        self.assertEqual(self.pending(), [])  # every delivered notice is marked
        self.assertTrue(ids)

    def test_a_dry_run_marks_nothing(self):
        ids = self.queue(2)
        code, out, requests = self.run_main(["--dry-run"])
        self.assertEqual((code, requests), (0, []))
        self.assertIn("Notices since the last digest (2):", out)
        self.assertEqual(self.pending(), ids)

    def test_a_refused_send_marks_nothing(self):
        ids = self.queue(2)

        def refuse(request, timeout=None):
            return self.Response(json.dumps({"data": {"succeeded": 0, "failed": 1}}).encode())
        code, _, _ = self.run_main([], opener=refuse)
        self.assertEqual(code, 1)
        self.assertEqual(self.pending(), ids)

    def test_a_notice_recorded_during_the_send_stays_pending(self):
        self.queue(1)
        late = []

        def sending(request, timeout=None):
            late.extend(self.queue(1))  # recorded while the digest is on its way
            return self.Response(json.dumps({"data": {"succeeded": 1, "failed": 0, "email_id": "e2"}}).encode())
        code, _, _ = self.run_main([], opener=sending)
        self.assertEqual(code, 0)
        self.assertEqual(self.pending(), late)

    def test_an_unreadable_queue_is_said_in_the_digest_and_nothing_is_marked(self):
        self.queue(1)
        queue = self.root / "build" / "automations" / "notices.jsonl"
        broken = queue.read_bytes() + b"not a notice\n"
        queue.write_bytes(broken)
        code, out, requests = self.run_main([])
        self.assertEqual(code, 0, out)
        self.assertIn("Notices: the queue could not be read", requests[0]["text_body"])
        self.assertEqual(queue.read_bytes(), broken)

    def test_a_path_in_a_notice_is_cleared_in_the_body_and_the_attachment(self):
        # Review round 1, finding 2: the attachment's heading line took the subject as it came.
        alert = digest.load_alert(self.root)
        alert.record_notice("campaign", r"Cannot open C:\Users\Owner\Private\file.txt", "body", str(self.root))
        code, _, requests = self.run_main([])
        self.assertEqual(code, 0)
        attached = {a["filename"]: base64.b64decode(a["fileblob"]).decode() for a in requests[0]["attachments"]}
        for text in (requests[0]["text_body"], attached["notices.txt"]):
            self.assertNotIn("Private", text)
            self.assertNotIn(r"C:\Users", text)

    def unconfirmed_then_next(self, first_run):
        """Run `first_run`, a digest that claims its batch and never confirms it, then a normal digest; return the
        second digest's request and the queue after it."""
        ids = self.queue(1)
        first_run()
        self.assertEqual(self.pending(), [])  # claimed, so not pending until the next digest releases it
        self.age_claims(hours=2)  # past the minutes a log may lag a send
        code, _, second = self.run_main([])
        self.assertEqual(code, 0)
        queue = [json.loads(line) for line in (self.root / "build/automations/notices.jsonl").read_text(
            encoding="utf-8").splitlines()]
        return ids, second[0], queue

    def age_claims(self, hours):
        """Move every claim's time back by `hours`, as if the digest that made it ran that long ago."""
        import datetime
        path = self.root / "build/automations/notices.jsonl"
        notices = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        for notice in notices:
            if notice.get("claimed"):
                at = datetime.datetime.strptime(notice["claimed"]["at"], "%Y-%m-%dT%H:%M:%SZ")
                notice["claimed"]["at"] = (at - datetime.timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
        path.write_text("".join(json.dumps(n) + "\n" for n in notices), encoding="utf-8")

    def assert_sent_again_in_full(self, ids, request, queue):
        self.assertIn("Notices since the last digest (1):", request["text_body"])
        self.assertIn("(an earlier digest did not deliver it)", " ".join(request["text_body"].split()))
        attached = {a["filename"]: base64.b64decode(a["fileblob"]).decode() for a in request["attachments"]}
        self.assertIn("log line 59 of failure 0", attached["notices.txt"])
        self.assertEqual([n["id"] for n in queue if n["reported"]], ids)

    def delivered_then_mark_fails(self):
        alert = digest.load_alert(self.root)
        with mock.patch.object(alert, "mark_reported", side_effect=alert.Refused("disk full")), \
                mock.patch.object(digest, "load_alert", return_value=alert):
            code, _, sent = self.run_main([])
        self.assertEqual(code, 1)
        return sent[0]["subject"]

    def test_a_delivered_batch_that_cannot_be_marked_is_confirmed_by_the_log_and_never_sent_again(self):
        # Completion review: the send succeeds and the mark fails (a full disk); SMTP2GO's log shows the digest.
        subject = []
        first = lambda: subject.append(self.delivered_then_mark_fails())
        ids = self.queue(1)
        first()
        for evidence in (self.root / "scratch" / "office-digest-evidence").glob("*.json"):
            evidence.unlink()  # the second store failed too: only SMTP2GO's log can say
        self.age_claims(hours=2)
        self.activity = [{"event": "delivered", "email_id": "e1", "subject": subject[0]}]
        code, out, second = self.run_main([])
        self.assertEqual(code, 0)
        self.assertNotIn("Notices since the last digest", second[0]["text_body"])
        self.assertIn("1 confirmed sent", out)
        search = self.searches[-1]
        self.assertEqual(search["search_subject"], subject[0])
        queue = [json.loads(line) for line in (self.root / "build/automations/notices.jsonl").read_text(
            encoding="utf-8").splitlines()]
        self.assertEqual([n["id"] for n in queue if n["reported"]], ids)

    def test_a_batch_the_log_does_not_show_and_nothing_proves_sent_is_sent_again(self):
        self.activity = []
        self.assert_sent_again_in_full(*self.unconfirmed_then_next(self.interrupted_send))

    def test_a_digest_the_log_does_not_show_yet_but_smtp2go_accepted_is_not_repeated(self):
        self.queue(1)
        self.delivered_then_mark_fails()
        self.age_claims(hours=2)
        self.activity = []  # the log lags or has purged it; the digest's own record says it was accepted
        code, _, second = self.run_main([])
        self.assertEqual(code, 0)
        self.assertNotIn("Notices since the last digest", second[0]["text_body"])

    def interrupted_send(self):
        def interrupted(request, timeout=None):
            raise KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.run_main([], opener=interrupted)

    def test_a_delivered_digest_whose_mark_failed_is_never_repeated_even_after_the_log_is_gone(self):
        # Reconciliation review 6: delivered, the mark fails, the PC is off past SMTP2GO's history.
        ids = self.queue(1)
        self.delivered_then_mark_fails()
        self.age_claims(hours=24 * 6)
        self.activity = OSError("SMTP2GO no longer holds it")
        code, out, second = self.run_main([])
        self.assertEqual(code, 0)
        self.assertNotIn("Notices since the last digest", second[0]["text_body"])
        self.assertNotIn("could not be confirmed", second[0]["text_body"])
        self.assertNotIn("attachments", second[0])
        self.assertIn("1 confirmed sent", out)
        queue = [json.loads(line) for line in (self.root / "build/automations/notices.jsonl").read_text(
            encoding="utf-8").splitlines()]
        self.assertEqual([n["id"] for n in queue if n["reported"]], ids)
        self.assertEqual(list((self.root / "scratch" / "office-digest-evidence").glob("*.json")), [])

    def test_a_log_that_cannot_be_read_keeps_the_claim_until_it_can_judge_it_or_the_evidence_is_gone(self):
        ids = self.queue(1)
        self.interrupted_send()  # cut off mid-send: no proof of delivery either way
        self.age_claims(hours=2)
        self.activity = OSError("SMTP2GO is down")
        code, out, second = self.run_main([])
        self.assertEqual(code, 0)
        self.assertNotIn("Notices since the last digest", second[0]["text_body"])  # neither repeated nor lost
        self.assertIn("1 kept to ask again", out)
        self.assertEqual(self.pending(), [])
        self.age_claims(hours=24 * 6)  # past the five days SMTP2GO keeps its activity log
        code, _, third = self.run_main([])
        self.assertEqual(code, 0)
        body = " ".join(third[0]["text_body"].split())
        self.assertNotIn("Notices since the last digest", body)  # not presented as new
        self.assertIn("1 notice(s) of the digest of", body)
        self.assertIn("could not be confirmed delivered", body)
        self.assertIn("may already have reached you", body)
        attached = {a["filename"]: base64.b64decode(a["fileblob"]).decode() for a in third[0]["attachments"]}
        self.assertIn("it may already have reached you", attached["notices.txt"])  # the one labelled repeat
        self.assertIn("log line 59 of failure 0", attached["notices.txt"])  # its full text: nothing is lost
        queue = [json.loads(line) for line in (self.root / "build/automations/notices.jsonl").read_text(
            encoding="utf-8").splitlines()]
        self.assertEqual([n["id"] for n in queue if n["reported"]], ids)  # closed only after that delivery
        code, _, fourth = self.run_main([])
        self.assertNotIn("could not be confirmed", fourth[0]["text_body"])  # and never again

    def test_a_mark_refused_twice_then_written_closes_the_batch(self):
        ids = self.queue(1)
        alert = digest.load_alert(self.root)
        real, calls = alert.mark_reported, []

        def flaky(batch, root):
            calls.append(1)
            if len(calls) < 3:
                raise alert.Refused("the file is held for a moment")
            return real(batch, root)
        with mock.patch.object(alert, "mark_reported", flaky), mock.patch.object(digest, "load_alert", return_value=alert):
            code, _, _ = self.run_main([])
        self.assertEqual((code, len(calls)), (0, 3))
        self.assertEqual(self.pending(), [])
        self.assertEqual(alert.claimed_notices(str(self.root)), [])
        queue = [json.loads(line) for line in (self.root / "build/automations/notices.jsonl").read_text(
            encoding="utf-8").splitlines()]
        self.assertEqual([n["id"] for n in queue if n["reported"]], ids)

    def test_an_unconfirmed_notice_once_delivered_is_never_delivered_again(self):
        # Reconciliation review 7: the digest that carries an unconfirmed notice claims it like any other.
        ids = self.queue(1)
        self.interrupted_send()
        self.age_claims(hours=24 * 6)
        self.activity = OSError("SMTP2GO no longer holds it")
        alert = digest.load_alert(self.root)
        with mock.patch.object(alert, "mark_reported", side_effect=alert.Refused("disk full")), \
                mock.patch.object(digest, "load_alert", return_value=alert):
            code, _, carried = self.run_main([])  # it goes out in full, labelled, and the mark fails
        self.assertEqual(code, 1)
        self.assertIn("could not be confirmed delivered", " ".join(carried[0]["text_body"].split()))
        self.age_claims(hours=24 * 6)
        code, out, after = self.run_main([])
        self.assertEqual(code, 0)
        self.assertNotIn("could not be confirmed", after[0]["text_body"])
        self.assertNotIn("Notices since the last digest", after[0]["text_body"])
        self.assertIn("1 confirmed sent", out)
        queue = [json.loads(line) for line in (self.root / "build/automations/notices.jsonl").read_text(
            encoding="utf-8").splitlines()]
        self.assertEqual([n["id"] for n in queue if n["reported"]], ids)

    def test_another_digest_with_the_same_counts_is_never_taken_as_the_evidence(self):
        # Reconciliation review 4: subjects repeat week to week, so each digest's subject carries its own id.
        ids = self.queue(1)

        def interrupted(request, timeout=None):
            raise KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.run_main([], opener=interrupted)
        code, _, second = self.run_main([])  # at once: the young claim is kept, a new digest goes out
        self.assertEqual(code, 0)
        self.age_claims(hours=2)
        self.activity = [{"event": "delivered", "email_id": "e1", "subject": second[0]["subject"]}]
        code, _, third = self.run_main([])
        self.assertEqual(code, 0)
        self.assert_sent_again_in_full(ids, third[0], [json.loads(line) for line in (
            self.root / "build/automations/notices.jsonl").read_text(encoding="utf-8").splitlines()])
        self.assertNotEqual(second[0]["subject"], third[0]["subject"])

    def test_a_digest_the_log_shows_bounced_is_sent_again(self):
        subject = []
        ids = self.queue(1)
        subject.append(self.delivered_then_mark_fails())
        self.age_claims(hours=2)
        self.activity = [{"event": "processed", "email_id": "e1", "subject": subject[0]},
                         {"event": "hard-bounced", "email_id": "e1", "subject": subject[0]}]
        code, _, second = self.run_main([])
        self.assertEqual(code, 0)
        self.assert_sent_again_in_full(ids, second[0], [json.loads(line) for line in (
            self.root / "build/automations/notices.jsonl").read_text(encoding="utf-8").splitlines()])

    def test_a_send_interrupted_after_the_claim_loses_nothing(self):
        # Reconciliation review: the process stops between the claim and the send's end.
        def first():
            def interrupted(request, timeout=None):
                raise KeyboardInterrupt
            with self.assertRaises(KeyboardInterrupt):
                self.run_main([], opener=interrupted)
        self.assert_sent_again_in_full(*self.unconfirmed_then_next(first))

    def test_a_refused_send_whose_release_fails_loses_nothing(self):
        def first():
            alert = digest.load_alert(self.root)

            def refuse(request, timeout=None):
                return self.Response(json.dumps({"data": {"succeeded": 0, "failed": 1}}).encode())
            with mock.patch.object(alert, "release_claim", side_effect=alert.Refused("read-only")), \
                    mock.patch.object(digest, "load_alert", return_value=alert):
                self.assertEqual(self.run_main([], opener=refuse)[0], 1)
        self.assert_sent_again_in_full(*self.unconfirmed_then_next(first))

    def test_a_notice_sent_once_carries_no_repeat_mark(self):
        self.queue(1)
        code, _, requests = self.run_main([])
        self.assertEqual(code, 0)
        self.assertNotIn("may repeat", requests[0]["text_body"])
    def test_a_batch_that_cannot_be_claimed_is_not_sent(self):
        self.queue(1)
        alert = digest.load_alert(self.root)
        with mock.patch.object(alert, "claim_notices", side_effect=alert.Refused("read-only")):
            with mock.patch.object(digest, "load_alert", return_value=alert):
                code, _, requests = self.run_main([])
        self.assertEqual((code, requests), (1, []))
        self.assertEqual(len(self.pending()), 1)

    def test_list_shows_every_unfinished_notice_with_its_text(self):
        alert = digest.load_alert(self.root)
        first, second, third = self.queue(3)
        alert.claim_notices([first], "d1", str(self.root), "s1")
        alert.claim_notices([third], "d3", str(self.root), "s3")
        alert.mark_unconfirmed("d3", str(self.root))
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(alert.main(["--list"], root=str(self.root)), 0)
        heads = [line for line in out.getvalue().splitlines() if not line.startswith("    ")]
        self.assertEqual([line.split()[0] for line in heads], ["pending", "claimed", "unconfirmed"])
        self.assertIn("task-1", heads[0])
        self.assertIn("task-0", heads[1])
        self.assertIn("task-2", heads[2])
        self.assertIn("    log line 59 of failure 2", out.getvalue())  # the text of each, unconfirmed included

    def test_no_notices_adds_no_part(self):
        code, _, requests = self.run_main([])
        self.assertNotIn("Notices", requests[0]["text_body"])
        self.assertNotIn("attachments", requests[0])


class Repository(unittest.TestCase):
    def test_the_digest_of_this_repository_prints(self):
        r = subprocess.run([sys.executable, str(REPO / "scripts/owner-digest.py"), "--dry-run"], capture_output=True,
                           text=True, encoding="utf-8", timeout=600)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Subject: Office weekly:", r.stdout)


if __name__ == "__main__":
    unittest.main()
