# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Tests for scripts/owner-digest.py: the owner's one weekly email (D00 T03 §35)."""
import base64
import datetime
import importlib.util
import io
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from unittest import mock

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
sys.path.insert(0, str(REPO / "scripts" / "tests"))
import todo_graph as tg  # noqa: E402  (the library sits beside the scripts, not on the path)
from test_todo_graph import FIXTURE_ACTION, todo_file, withdraw  # noqa: E402  (the shared TODO fixtures)

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
        lines = "\n".join(digest.item_lines(items[0]))
        self.assertIn("2 open sections wait behind it", lines)
        self.assertIn("To do: " + ACTION[:40], lines)

    def test_the_list_is_ordered_by_what_waits_behind_largest_first(self):
        self.write(*waiting_file([(1, "Small", 0, "operator", "--"), (2, "Big", 0, "third-party", "--"),
                                  (3, "A", 0, "none", "§2"), (4, "B", 0, "none", "§2"), (5, "C", 0, "none", "§1")]))
        self.assertEqual([i["ref"] for i in digest.waiting(self.rows())], ["D00 T01 §2", "D00 T01 §1"])

    def test_withdrawn_and_stamped_sections_wait_on_no_one(self):
        # Mutation 4 of §35: the withdrawn section must be one that would otherwise wait on the owner.
        text, name = waiting_file([(1, "Keep", 0, "none", "--"), (2, "Gone", 0, "operator", "--")])
        self.write(withdraw(text, 2), name)
        self.assertEqual(digest.waiting(self.rows()), [])

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

    def test_a_guard_means_running(self):
        (self.root / "build").mkdir()
        (self.root / "build/claude-campaign-guard.json").write_text(
            json.dumps({"run_id": "abc", "phase": 2, "run_file": "docs/phase-runs/x.md"}), encoding="utf-8")
        self.assertEqual(digest.run_state(self.root), "Running: run abc, phase 2, docs/phase-runs/x.md")

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
        guard = self.root / "build/claude-campaign-guard.json"
        guard.write_text("{}", encoding="utf-8")
        with mock.patch.object(pathlib.Path, "read_text", side_effect=PermissionError(13, "denied", str(guard))):
            state = digest.run_state(self.root)
        self.assertEqual(state, "Unknown: the run files cannot be read (PermissionError on build/claude-campaign-guard.json).")
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
                    ("total", "verified", "ready", "blocked", "withdrawn", "to_author"), 0)), \
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

    def run_main(self, argv, opener=None, attach=False):
        requests = []

        def capture(request, timeout=None):
            requests.append(json.loads(request.data.decode()))
            return self.Response(json.dumps({"data": {"succeeded": 1, "failed": 0, "email_id": "e1"}}).encode())

        out = io.StringIO()
        with mock.patch.object(digest, "ci_state", return_value=["CI: green for abc1234."]), \
                mock.patch.object(digest, "run_state", return_value="Running"), redirect_stdout(out):
            alert = digest.load_alert(self.root)
            with mock.patch.object(digest, "load_alert", return_value=alert), \
                    mock.patch.object(alert, "key", return_value="k"):
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


class Repository(unittest.TestCase):
    def test_the_digest_of_this_repository_prints(self):
        r = subprocess.run([sys.executable, str(REPO / "scripts/owner-digest.py"), "--dry-run"], capture_output=True,
                           text=True, encoding="utf-8", timeout=600)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Subject: Office weekly:", r.stdout)


if __name__ == "__main__":
    unittest.main()
