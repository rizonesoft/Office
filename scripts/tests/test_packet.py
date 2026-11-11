# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Tests for scripts/packet.py: a worker's change is read whole, accepted exactly as reviewed, or set aside without
losing a byte (D00 T03 §34)."""
import importlib.util
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "packet.py"
sys.path.insert(0, str(REPO / "scripts" / "lib"))
from todo_graph import git as git_path  # noqa: E402  the absolute git, as the script uses

SPEC = importlib.util.spec_from_file_location("packet", SCRIPT)
packet = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packet)

NAME = "D00 T03 §34, test"


class Stop(BaseException):
    """A run that dies at a chosen point (BaseException, so nothing in the script handles it)."""


class Packet(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name)
        for args in (["init", "-q", "-b", "main"], ["config", "user.email", "t@example.com"],
                     ["config", "user.name", "T"], ["config", "core.autocrlf", "false"],
                     ["config", "commit.gpgsign", "false"]):
            self.git(*args)
        self.put(".gitignore", "build/\n")
        self.put("src/a.py", "a = 1\n")
        self.put("docs/note.md", "note\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run([git_path(), "-C", str(self.repo), *args], capture_output=True, text=True,
                              encoding="utf-8", check=True, timeout=60).stdout

    def put(self, path, text):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))

    def read(self, path):
        return (self.repo / path).read_bytes().decode("utf-8")

    def cli(self, *args):
        r = subprocess.run([sys.executable, "-B", str(SCRIPT), "--repo", str(self.repo), *args],
                           capture_output=True, text=True, encoding="utf-8", timeout=120)
        return r.returncode, r.stdout, r.stderr

    def run_in_process(self, *args):
        """main() in this process, so a test can stop it or save a file at a chosen point."""
        out, err = io.TextIOWrapper(io.BytesIO(), encoding="utf-8"), io.StringIO()
        with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "stderr", err):
            code = packet.main(["--repo", str(self.repo), *args])
            out.flush()
        return code, out.buffer.getvalue().decode("utf-8"), err.getvalue()

    def begin(self, *paths):
        code, _, err = self.cli("begin", "--name", NAME, *[a for p in paths for a in ("--path", p)])
        self.assertEqual(code, 0, err)

    def status(self):
        return self.git("status", "--porcelain=v1", "--untracked-files=all")

    def state(self):
        return json.loads((self.repo / "build/packet.json").read_text(encoding="utf-8"))

    def snapshot(self, out):
        return re.search(r"^snapshot: (sha256:[0-9a-f]{64})$", out, re.M)[1]

    # begin

    def test_begin_refuses_a_tree_with_changes_and_names_them(self):
        self.put("src/a.py", "a = 2\n")
        self.put("new/dir/b.py", "b\n")
        code, _, err = self.cli("begin", "--name", "x", "--path", "src")
        self.assertEqual(code, 2)
        self.assertIn("src/a.py", err)
        self.assertIn("new/dir/b.py", err)
        self.assertFalse((self.repo / "build/packet.json").exists())

    def test_begin_records_name_paths_and_head_on_a_tree_without_changes(self):
        self.begin("src", "docs\\note.md", "./src")
        self.assertEqual(self.state(), {"name": NAME, "paths": ["src", "docs/note.md"],
                                        "head": self.git("rev-parse", "HEAD").strip(), "folder_links": []})
        self.assertEqual(list((self.repo / "build").glob(".packet-*")), [])

    def test_begin_refuses_paths_that_leave_the_repository_and_a_second_packet(self):
        for bad in ("../x", "src/../../x", "/abs", "C:/abs", ".git/config", "", "."):
            code, _, _ = self.cli("begin", "--name", "x", "--path", bad)
            self.assertEqual(code, 2, bad)
        self.begin("src")
        code, _, err = self.cli("begin", "--name", "y", "--path", "docs")
        self.assertEqual(code, 2)
        self.assertIn("already open", err)

    # show

    def test_show_lists_every_kind_of_change_with_its_mark_and_prints_the_whole_change(self):
        self.begin("src", "docs/note.md")
        self.put("src/a.py", "a = 2\n")
        self.git("add", "src/a.py")                      # staged
        self.put("docs/note.md", "note, edited\n")       # unstaged
        self.put("src/new.py", "new = True\n")           # a new file
        self.put("src/deep/er/nest.py", "nest = 1\n")    # a new file in a new folder
        self.put("owner.txt", "the owner saved this\n")  # outside: an owner's edit saved during the packet
        code, out, err = self.cli("show")
        self.assertEqual(code, 1)
        for line in ("inside  src/a.py", "inside  docs/note.md", "inside  src/new.py", "inside  src/deep/er/nest.py",
                     "outside owner.txt"):
            self.assertIn(line + "\n", out)
        for shown in ("+a = 2", "+note, edited", "new = True", "nest = 1", "the owner saved this"):
            self.assertIn(shown, out)
        self.assertIn("outside the packet's paths: owner.txt", err)
        self.snapshot(out)

    def test_an_edit_staged_and_undone_in_the_working_tree_shows_both_versions(self):
        self.begin("src")
        self.put("src/a.py", "a = 'B'\n")
        self.git("add", "src/a.py")
        self.put("src/a.py", "a = 1\n")  # back to HEAD's bytes, so git diff HEAD would show nothing
        code, out, err = self.cli("show")
        self.assertEqual(code, 0, err)
        self.assertIn("inside  src/a.py\n", out)
        staged, unstaged = out.split("--- unstaged", 1)
        self.assertIn("+a = 'B'", staged)
        self.assertIn("-a = 'B'", unstaged)
        self.assertIn("+a = 1", unstaged)

    def test_show_exits_0_when_every_change_is_inside_and_head_held(self):
        self.begin("src")
        self.put("src/a.py", "a = 3\n")
        self.put("src/new/b.py", "b\n")
        code, _, err = self.cli("show")
        self.assertEqual(code, 0, err)
        self.assertTrue((self.repo / "build/packet.json").exists())

    def test_show_exits_1_when_head_moved(self):
        self.begin("src")
        self.put("src/a.py", "a = 4\n")
        self.git("commit", "-q", "-am", "a worker committed")
        self.put("src/a.py", "a = 5\n")
        code, _, err = self.cli("show")
        self.assertEqual(code, 1)
        self.assertIn("HEAD moved", err)

    def test_show_exits_1_on_an_empty_change(self):
        self.begin("src")
        code, _, err = self.cli("show")
        self.assertEqual(code, 1)
        self.assertIn("nothing changed", err)

    def test_a_rename_out_of_the_packet_names_both_sides(self):
        self.begin("src")
        self.git("mv", "docs/note.md", "src/note.md")
        code, out, _ = self.cli("show")
        self.assertEqual(code, 1)
        self.assertIn("outside docs/note.md\n", out)
        self.assertIn("inside  src/note.md\n", out)

    def test_a_sibling_whose_name_starts_with_a_packet_path_is_outside(self):
        self.begin("src")
        self.put("src2/x.py", "x\n")
        self.put("src.txt", "y\n")
        code, out, _ = self.cli("show")
        self.assertEqual(code, 1)
        self.assertIn("outside src2/x.py\n", out)
        self.assertIn("outside src.txt\n", out)

    def test_the_snapshot_names_the_bytes_and_changes_with_them(self):
        self.begin("src")
        self.put("src/a.py", "a = 9\n")
        first = self.snapshot(self.cli("show")[1])
        self.assertEqual(self.snapshot(self.cli("show")[1]), first)
        self.put("src/a.py", "a = 10\n")
        self.assertNotEqual(self.snapshot(self.cli("show")[1]), first)

    # show --stage

    def test_stage_puts_exactly_the_reviewed_bytes_of_the_packet_paths_in_the_index_and_closes_it(self):
        self.begin("src")
        self.put("src/a.py", "a = 6\n")
        self.put("src/new/b.py", "b\n")
        (self.repo / "src/a.py").rename(self.repo / "src/moved.py")
        digest = self.snapshot(self.cli("show")[1])
        code, out, err = self.cli("show", "--stage", "--snapshot", digest)
        self.assertEqual(code, 0, err)
        self.assertEqual(sorted(self.git("diff", "--cached", "--name-only").split()),
                         ["src/a.py", "src/moved.py", "src/new/b.py"])
        self.assertEqual(self.git("show", ":src/moved.py"), "a = 6\n")
        self.assertEqual(self.git("ls-files", "src/a.py"), "")
        self.assertEqual(self.status().count("??"), 0)
        self.assertFalse((self.repo / "build/packet.json").exists())
        self.assertIn("staged 3 path(s) exactly as reviewed", out)

    def test_stage_needs_the_reviewed_snapshot_and_refuses_a_stale_one(self):
        self.begin("src")
        self.put("src/a.py", "a = 11\n")
        code, _, err = self.cli("show", "--stage")
        self.assertEqual(code, 2)
        self.assertIn("--snapshot", err)
        digest = self.snapshot(self.cli("show")[1])
        self.put("src/a.py", "a = 12, saved after the review\n")
        code, _, err = self.cli("show", "--stage", "--snapshot", digest)
        self.assertEqual(code, 1)
        self.assertIn("no longer holds the reviewed snapshot", err)
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "")
        self.assertTrue((self.repo / "build/packet.json").exists())

    def test_stage_stages_nothing_after_a_refusal(self):
        self.begin("src")
        self.put("src/a.py", "a = 7\n")
        self.put("outside.txt", "o\n")
        digest = self.snapshot(self.cli("show")[1])
        code, _, _ = self.cli("show", "--stage", "--snapshot", digest)
        self.assertEqual(code, 1)
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "")
        self.assertTrue((self.repo / "build/packet.json").exists())

    def test_a_save_between_the_read_and_the_staging_is_left_unstaged_and_named(self):
        self.begin("src")
        self.put("src/a.py", "a = 13, reviewed\n")
        digest = self.snapshot(self.cli("show")[1])
        real = packet.stage_bytes

        def save_first(*args, **kwargs):
            self.put("src/a.py", "a = 14, saved while staging\n")
            return real(*args, **kwargs)

        with mock.patch.object(packet, "stage_bytes", save_first):
            code, out, err = self.run_in_process("show", "--stage", "--snapshot", digest)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.git("show", ":src/a.py"), "a = 13, reviewed\n")
        self.assertEqual(self.read("src/a.py"), "a = 14, saved while staging\n")
        self.assertIn("changed after the review, left unstaged: src/a.py", out)

    # reject

    def assert_in_stash(self, commit, path, text, part=""):
        self.assertEqual(self.git("show", f"{commit}{part}:{path}"), text)

    def test_reject_sets_every_change_aside_recoverably_and_empties_the_tree(self):
        self.begin("src")
        self.put("src/a.py", "a = 8\n")                  # tracked edit
        self.put("docs/note.md", "staged owner edit\n")
        self.git("add", "docs/note.md")                  # staged edit
        self.put("new/dir/c.py", "c\n")                  # untracked file in a new folder
        code, out, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.status(), "")
        self.assertFalse((self.repo / "new").exists())
        self.assertFalse((self.repo / "build/packet.json").exists())
        found = re.search(r"set aside as (stash@\{0\}) \(([0-9a-f]{40})\): rejected packet: D00 T03 §34, test", out)
        self.assertIsNotNone(found, out)
        self.assertIn("rejected packet: D00 T03 §34, test", self.git("stash", "list"))
        self.assert_in_stash("stash@{0}", "src/a.py", "a = 8\n")
        self.assert_in_stash("stash@{0}", "docs/note.md", "staged owner edit\n")
        self.assert_in_stash("stash@{0}", "docs/note.md", "staged owner edit\n", "^2")  # the index commit
        self.assert_in_stash("stash@{0}", "new/dir/c.py", "c\n", "^3")                   # the untracked commit
        # git itself can bring the whole rejected change back.
        self.git("stash", "apply", "--index", "stash@{0}")
        self.assertEqual(self.read("src/a.py"), "a = 8\n")
        self.assertEqual(self.read("new/dir/c.py"), "c\n")
        self.assertIn("M  docs/note.md", self.status())

    def test_reject_with_nothing_changed_closes_the_packet_without_a_stash(self):
        self.begin("src")
        code, out, _ = self.cli("reject")
        self.assertEqual(code, 0)
        self.assertEqual(self.git("stash", "list"), "")
        self.assertIn("nothing to set aside", out)

    def test_reject_refuses_when_head_moved_and_changes_nothing(self):
        for leave_more in (False, True):
            with self.subTest(committed_plus_uncommitted=leave_more):
                self.begin("src")
                self.put("src/a.py", f"a = {leave_more}\n")
                self.git("commit", "-q", "-am", "the worker committed")
                if leave_more:
                    self.put("src/b.py", "uncommitted\n")
                before = self.status()
                code, _, err = self.cli("reject")
                self.assertEqual(code, 1)
                self.assertIn("HEAD moved", err)
                self.assertIn("the worker committed", err)
                self.assertEqual(self.status(), before)
                self.assertEqual(self.git("stash", "list"), "")
                self.assertTrue((self.repo / "build/packet.json").exists())
                (self.repo / "build/packet.json").unlink()
                if leave_more:
                    (self.repo / "src/b.py").unlink()

    def test_a_save_after_the_capture_is_kept_on_disk_and_named(self):
        self.begin("src")
        self.put("src/a.py", "a = 15, the worker's\n")
        self.put("src/b.py", "b, the worker's\n")
        real = packet.store

        def owner_saves(*args, **kwargs):
            real(*args, **kwargs)
            self.put("src/a.py", "a = 16, the owner saved this mid-rejection\n")

        with mock.patch.object(packet, "store", owner_saves):
            code, out, err = self.run_in_process("reject")
        self.assertEqual(code, 1)
        self.assertEqual(self.read("src/a.py"), "a = 16, the owner saved this mid-rejection\n")
        self.assertFalse((self.repo / "src/b.py").exists())
        self.assertIn("kept on disk, saved after the capture and not in the stash: src/a.py", out)
        self.assert_in_stash("stash@{0}", "src/a.py", "a = 15, the worker's\n")
        # A further reject sets the kept save aside too, in a stash of its own.
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assert_in_stash("stash@{0}", "src/a.py", "a = 16, the owner saved this mid-rejection\n")
        self.assert_in_stash("stash@{1}", "src/a.py", "a = 15, the worker's\n")
        self.assertEqual(self.status(), "")

    def stopped_reject(self, target, after=True):
        """Run reject in-process and stop it at `target`, after (or before) the real call."""
        real = getattr(packet, target)

        def stop(*args, **kwargs):
            if after:
                real(*args, **kwargs)
            raise Stop(target)

        with mock.patch.object(packet, target, stop), self.assertRaises(Stop):
            self.run_in_process("reject")

    def test_a_reject_stopped_after_the_stash_commit_is_made_resumes_with_the_same_commit(self):
        self.begin("src")
        self.put("src/a.py", "a = 17\n")
        self.put("src/c.py", "c\n")
        self.stopped_reject("store", after=False)
        recorded = self.state()["rejection"]
        self.assertFalse(recorded["stored"])
        self.assertEqual(self.git("stash", "list"), "")
        self.assertEqual(self.read("src/a.py"), "a = 17\n")
        code, out, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertIn(recorded["stash"], out)
        self.assertEqual(self.git("rev-parse", "stash@{0}").strip(), recorded["stash"])
        self.assertEqual(self.status(), "")

    def test_a_reject_stopped_after_the_stash_is_stored_resumes_without_a_second_stash(self):
        self.begin("src")
        self.put("src/a.py", "a = 18\n")
        self.stopped_reject("store")
        recorded = self.state()["rejection"]
        self.assertEqual(len(self.git("stash", "list").splitlines()), 1)
        code, out, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertIn(recorded["stash"], out)
        self.assertEqual(len(self.git("stash", "list").splitlines()), 1)
        self.assertEqual(self.status(), "")
        self.assertFalse((self.repo / "build/packet.json").exists())

    def test_a_resume_never_stores_the_same_stash_twice_even_under_a_later_stash(self):
        self.begin("src")
        self.put("src/a.py", "a = 20\n")
        self.stopped_reject("store")  # stored in git, but the record still says it is not
        stash = self.state()["rejection"]["stash"]
        # Someone stashes something else on top before the resume: a stash-shaped commit (HEAD and an index commit).
        tree = self.git("rev-parse", "HEAD^{tree}").strip()
        index = self.git("commit-tree", tree, "-p", "HEAD", "-m", "index on main").strip()
        other = self.git("commit-tree", tree, "-p", "HEAD", "-p", index, "-m", "On main: another").strip()
        self.git("stash", "store", "-m", "another stash", other)
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        listed = self.git("stash", "list", "--format=%H").split()
        self.assertEqual(listed.count(stash), 1, listed)

    def test_an_index_staged_between_an_interrupted_reject_and_its_retry_is_kept(self):
        # Review round 1, finding 1: the retry returned the index to HEAD and lost the newer staged state.
        self.begin("src")
        self.put("src/a.py", "a = 21\n")
        self.stopped_reject("store")
        self.put("docs/note.md", "staged by the owner after the capture\n")
        self.git("add", "docs/note.md")
        self.put("docs/note.md", "note\n")  # and undone on disk, so the staged blob is the only copy
        code, out, _ = self.cli("reject")
        self.assertEqual(code, 1)
        self.assertIn("kept the index", out)
        self.assertEqual(self.git("show", ":docs/note.md"), "staged by the owner after the capture\n")
        self.assertEqual(self.read("src/a.py"), "a = 1\n")
        # A further reject sets the kept index aside in a stash of its own.
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assert_in_stash("stash@{0}", "docs/note.md", "staged by the owner after the capture\n", "^2")
        self.assertEqual(self.status(), "")

    def test_a_staged_new_file_already_gone_from_disk_does_not_block_the_rejection(self):
        # Review round 1, finding 2: unlinking the absent file failed on every retry.
        self.begin("src")
        self.put("src/staged.py", "staged then deleted\n")
        self.git("add", "src/staged.py")
        (self.repo / "src/staged.py").unlink()
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assert_in_stash("stash@{0}", "src/staged.py", "staged then deleted\n", "^2")
        self.assertEqual(self.status(), "")

    def test_a_folder_that_took_a_tracked_files_name_is_shown_and_rejected(self):
        # Review round 1, finding 3: reading the folder as a file made both verbs exit 3.
        self.begin("docs")
        (self.repo / "docs/note.md").unlink()
        self.put("docs/note.md/part.md", "a folder now holds the name\n")
        code, out, err = self.cli("show")
        self.assertEqual(code, 0, err)
        self.assertIn("inside  docs/note.md\n", out)
        self.assertIn("inside  docs/note.md/part.md\n", out)
        self.assertIn("a folder now holds the name", out)
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.read("docs/note.md"), "note\n")
        self.assert_in_stash("stash@{0}", "docs/note.md/part.md", "a folder now holds the name\n", "^3")
        self.assertEqual(self.status(), "")

    def test_a_staged_file_whose_new_folder_is_gone_too_does_not_block_the_rejection(self):
        # Review round 2, finding 1: the emptied-folder walk read a folder that no longer existed.
        self.begin("src")
        self.put("src/new/file.py", "staged in a new folder\n")
        self.git("add", "src/new/file.py")
        (self.repo / "src/new/file.py").unlink()
        (self.repo / "src/new").rmdir()
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assert_in_stash("stash@{0}", "src/new/file.py", "staged in a new folder\n", "^2")
        self.assertEqual(self.status(), "")

    def tracked_group(self):
        self.put("docs/group/note.md", "grouped note\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "a tracked folder")

    def test_a_file_that_took_a_tracked_folders_name_is_rejected_and_the_folder_returns(self):
        # Review round 2, finding 2: HEAD's tree entry was written into the file as if it were a blob.
        self.tracked_group()
        self.begin("docs")
        (self.repo / "docs/group/note.md").unlink()
        (self.repo / "docs/group").rmdir()
        self.put("docs/group", "a file now holds the folder's name\n")
        code, out, err = self.cli("show")
        self.assertEqual(code, 0, err)
        self.assertIn("inside  docs/group\n", out)
        self.assertIn("inside  docs/group/note.md\n", out)
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.read("docs/group/note.md"), "grouped note\n")
        self.assert_in_stash("stash@{0}", "docs/group", "a file now holds the folder's name\n", "^3")
        self.assertEqual(self.status(), "")

    def file_in_group_place(self, stage_deletion):
        self.tracked_group()
        self.begin("docs")
        (self.repo / "docs/group/note.md").unlink()
        (self.repo / "docs/group").rmdir()
        if stage_deletion:
            self.git("add", "-u", "docs/group")
        self.put("docs/group", "a file now holds the folder's name\n")

    def test_a_file_in_a_folders_place_with_only_the_deletion_staged_is_rejected(self):
        # Review round 4, finding 1: the file took the folder's tree mode, and the stash could not be built.
        self.file_in_group_place(stage_deletion=True)
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.read("docs/group/note.md"), "grouped note\n")
        self.assertRegex(self.git("ls-tree", "stash@{0}^3", "docs/group"), r"^100644 blob ")
        self.assertEqual(self.status(), "")

    def test_a_file_in_a_folders_place_is_staged_after_the_folders_entries_go(self):
        # Review round 4, finding 2: the file was added while the folder's entry was still in the index.
        self.file_in_group_place(stage_deletion=False)
        digest = self.snapshot(self.cli("show")[1])
        code, _, err = self.cli("show", "--stage", "--snapshot", digest)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.git("show", ":docs/group"), "a file now holds the folder's name\n")
        self.assertEqual(self.git("ls-files", "docs/group/note.md"), "")
        self.assertRegex(self.git("ls-files", "-s", "docs/group"), r"^100644 ")

    def test_a_folder_in_a_files_place_is_staged_with_file_modes(self):
        self.begin("docs")
        (self.repo / "docs/note.md").unlink()
        self.put("docs/note.md/part.md", "a folder now holds the name\n")
        digest = self.snapshot(self.cli("show")[1])
        code, _, err = self.cli("show", "--stage", "--snapshot", digest)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.git("show", ":docs/note.md/part.md"), "a folder now holds the name\n")

    def test_a_kept_file_in_a_folders_place_holds_back_the_files_under_it(self):
        self.tracked_group()
        self.begin("docs")
        (self.repo / "docs/group/note.md").unlink()
        (self.repo / "docs/group").rmdir()
        self.put("docs/group", "the worker's file\n")
        real = packet.store

        def owner_saves(*args, **kwargs):
            real(*args, **kwargs)
            self.put("docs/group", "the owner saved over it mid-rejection\n")

        with mock.patch.object(packet, "store", owner_saves):
            code, out, _ = self.run_in_process("reject")
        self.assertEqual(code, 1)
        self.assertEqual(self.read("docs/group"), "the owner saved over it mid-rejection\n")
        self.assertIn("kept on disk, saved after the capture and not in the stash: docs/group", out)
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.read("docs/group/note.md"), "grouped note\n")
        self.assertEqual(self.status(), "")

    def can_link(self):
        probe = self.repo / "build" / "link-probe"
        probe.parent.mkdir(exist_ok=True)
        try:
            os.symlink("nowhere", probe)
        except (OSError, NotImplementedError):
            return False
        probe.unlink()
        return True

    def test_an_untracked_link_is_set_aside_as_a_link_and_never_followed(self):
        # Review round 3, finding 1: a dangling link was read as absent and unlinked without being stashed.
        if not self.can_link():
            self.skipTest("this account cannot create symbolic links")
        self.begin("src")
        os.symlink("does/not/exist", self.repo / "src/dangling")
        os.symlink("../docs", self.repo / "src/to-folder", target_is_directory=True)
        os.symlink("a.py", self.repo / "src/to-file")
        code, out, err = self.cli("show")
        self.assertEqual(code, 0, err)
        self.assertIn("--- new link src/dangling -> does/not/exist", out)
        self.assertIn("--- new link src/to-file -> a.py", out)
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        listing = self.git("ls-tree", "stash@{0}^3", "src/")
        for name, goal in (("dangling", "does/not/exist"), ("to-folder", "../docs"), ("to-file", "a.py")):
            self.assertRegex(listing, rf"120000 blob [0-9a-f]+\tsrc/{name}\n")
            self.assertEqual(self.git("cat-file", "-p", f"stash@{{0}}^3:src/{name}"), goal)
            self.assertFalse(os.path.lexists(self.repo / "src" / name), name)
        self.assertEqual(self.read("docs/note.md"), "note\n")  # never followed into the folder it named
        self.assertEqual(self.status(), "")

    def test_a_staged_file_under_a_folder_replaced_by_a_link_never_reaches_through_the_link(self):
        # Review round 5, finding 1: the child was read and deleted through the link, outside the repository.
        if not self.can_link():
            self.skipTest("this account cannot create symbolic links")
        with tempfile.TemporaryDirectory() as outside:
            (pathlib.Path(outside) / "file.txt").write_bytes(b"outside the repository\n")
            self.begin("src")
            self.put("src/new/file.txt", "outside the repository\n")  # the same bytes, so a follow would match
            self.git("add", "src/new/file.txt")
            (self.repo / "src/new/file.txt").unlink()
            (self.repo / "src/new").rmdir()
            os.symlink(outside, self.repo / "src/new", target_is_directory=True)
            code, _, err = self.cli("reject")
            self.assertEqual(code, 0, err)
            self.assertEqual((pathlib.Path(outside) / "file.txt").read_bytes(), b"outside the repository\n")
            self.assertFalse(os.path.lexists(self.repo / "src/new"))
            self.assert_in_stash("stash@{0}", "src/new/file.txt", "outside the repository\n", "^2")
            self.assertRegex(self.git("ls-tree", "stash@{0}^3", "src/new"), r"^120000 blob ")
            self.assertEqual(self.status(), "")

    def test_a_staged_file_under_a_folder_replaced_by_a_junction_never_reaches_through_it(self):
        # Review round 6, finding 1: a Windows junction is not a symlink to is_symlink(), so the guard let it through.
        try:
            import _winapi
        except ImportError:
            self.skipTest("junctions are a Windows feature")
        with tempfile.TemporaryDirectory() as outside:
            (pathlib.Path(outside) / "file.txt").write_bytes(b"outside the repository\n")
            self.begin("src")
            self.put("src/new/file.txt", "outside the repository\n")
            self.git("add", "src/new/file.txt")
            (self.repo / "src/new/file.txt").unlink()
            (self.repo / "src/new").rmdir()
            _winapi.CreateJunction(outside, str(self.repo / "src/new"))
            self.assertTrue((self.repo / "src/new").is_junction())
            code, _, err = self.cli("reject")
            self.assertEqual((pathlib.Path(outside) / "file.txt").read_bytes(), b"outside the repository\n")
            self.assertEqual(code, 0, err)
            self.assertFalse(os.path.lexists(self.repo / "src/new"))
            self.assertTrue((pathlib.Path(outside) / "file.txt").is_file())
            self.assert_in_stash("stash@{0}", "src/new/file.txt", "outside the repository\n", "^2")
            self.assertEqual(self.status(), "")

    def test_a_dangling_folder_link_comes_back_as_a_folder_link(self):
        # Review round 7, finding 1: it came back as a file link, which Windows never lets reach into a folder.
        if os.name != "nt" or not self.can_link():
            self.skipTest("folder and file links differ only on Windows, and this account must be able to link")
        self.git("config", "core.symlinks", "true")
        os.symlink("..\\generated", self.repo / "src/gen", target_is_directory=True)  # as git for Windows writes it
        self.git("add", "src/gen")
        self.git("commit", "-q", "-m", "a link to a folder made by a build")
        self.begin("src")
        self.assertEqual(self.state()["folder_links"], ["src/gen"])
        os.rmdir(self.repo / "src/gen")  # a folder link is removed as a folder on Windows
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(os.readlink(self.repo / "src/gen"), "..\\generated")
        self.put("generated/made.txt", "built later\n")
        self.assertEqual((self.repo / "src/gen/made.txt").read_bytes(), b"built later\n")
        self.assertEqual(self.git("cat-file", "-p", "HEAD:src/gen"), "../generated")

    def test_an_empty_folder_in_a_tracked_files_place_settles(self):
        # Review round 3, finding 2: the empty folder blocked the file's return on every retry.
        self.begin("docs")
        (self.repo / "docs/note.md").unlink()
        (self.repo / "docs/note.md/empty/inner").mkdir(parents=True)
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.read("docs/note.md"), "note\n")
        self.assertEqual(self.status(), "")

    def test_a_folder_holding_a_file_in_a_tracked_files_place_is_never_emptied_by_force(self):
        self.begin("docs")
        (self.repo / "docs/note.md").unlink()
        self.put("docs/note.md/kept.txt", "inside the folder\n")
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)  # the file is captured, stashed and removed, then the note returns
        self.assert_in_stash("stash@{0}", "docs/note.md/kept.txt", "inside the folder\n", "^3")
        self.assertEqual(self.read("docs/note.md"), "note\n")

    def test_a_path_that_cannot_be_written_keeps_the_packet_open_until_a_retry_finishes(self):
        self.begin("src")
        self.put("src/a.py", "a = 19\n")
        self.put("src/b.py", "b\n")
        real = packet.return_path

        def locked(repo, path, *args):
            if path == "src/a.py":
                raise PermissionError("the file is open in another program")
            return real(repo, path, *args)

        with mock.patch.object(packet, "return_path", locked):
            code, out, err = self.run_in_process("reject")
        self.assertEqual(code, 1)
        self.assertIn("src/a.py", err)
        stash = self.state()["rejection"]["stash"]
        self.assertIn(stash, out)
        self.assertEqual(self.state()["rejection"]["settled"], {"src/b.py": "returned"})
        code, out, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertIn(stash, out)
        self.assertEqual(self.read("src/a.py"), "a = 1\n")
        self.assertEqual(self.status(), "")

    # every kind of occupant, replaced by and replacing every other (review rounds 1 to 8, the takeover)

    def kinds(self):
        """The kinds of thing this account can put at a name: links need the right to create them, a folder link is
        its own kind only on Windows, and so is a junction."""
        found = ["nothing", "file", "folder"]
        if self.can_link():
            found.append("link")
            if os.name == "nt":
                found.append("folder link")
        if os.name == "nt":
            found.append("junction")
        return found

    def occupy(self, path, kind, outside):
        """Put the worker's occupant of `kind` at `path`; a folder link and a junction point at `outside`."""
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if kind == "file":
            target.write_bytes(b"the worker's file\n")
        elif kind == "folder":
            (target / "empty" / "inner").mkdir(parents=True)
        elif kind == "link":
            os.symlink("the-workers-target.txt", target)
        elif kind == "folder link":
            os.symlink(outside, target, target_is_directory=True)
        elif kind == "junction":
            import _winapi
            _winapi.CreateJunction(str(outside), str(target))

    def vacate(self, path):
        """Take away what holds `path`, without following it."""
        target = self.repo / path
        if target.is_dir() and not target.is_symlink() and not target.is_junction():
            for inner in sorted(target.rglob("*"), reverse=True):
                inner.rmdir() if inner.is_dir() else inner.unlink()
            target.rmdir()
        elif os.path.lexists(target):
            try:
                os.unlink(target)
            except OSError:
                os.rmdir(target)

    def is_folder_link(self, path):
        return bool(getattr(os.lstat(self.repo / path), "st_file_attributes", 0) & 0x10)

    def leftovers(self):
        return [str(p.relative_to(self.repo)) for p in self.repo.rglob(".packet-*") if ".git" not in p.parts]

    def outside_folder(self, stack):
        outside = pathlib.Path(stack.enter_context(tempfile.TemporaryDirectory()))
        (outside / "note.md").write_bytes(b"outside the repository\n")
        return outside

    def assert_outside_untouched(self, outside):
        self.assertEqual(sorted(p.name for p in outside.iterdir()), ["note.md"])
        self.assertEqual((outside / "note.md").read_bytes(), b"outside the repository\n")

    def test_occupant_names_each_kind_and_never_looks_through_a_link_or_a_file(self):
        import contextlib
        with contextlib.ExitStack() as stack:
            outside = self.outside_folder(stack)
            for kind in self.kinds():
                self.occupy(f"k/{kind}", kind, outside)
                self.assertEqual(packet.occupant(self.repo, f"k/{kind}"), kind)
                below = packet.occupant(self.repo, f"k/{kind}/note.md")
                if kind == "nothing":
                    self.assertEqual(below, "nothing")
                elif kind == "folder":
                    self.assertEqual(packet.occupant(self.repo, f"k/{kind}/empty"), "folder")
                else:  # a file, a link of either kind, a junction: nothing below it belongs to this tree
                    self.assertEqual(below, "beyond", kind)
                    self.assertIsNone(packet.read_entry(self.repo, f"k/{kind}/note.md"), kind)
                    self.assertIs(packet.return_path(self.repo, f"k/{kind}/note.md", ("file", b"written\n")), False)
                    self.assertIs(packet.return_path(self.repo, f"k/{kind}/note.md", None), True)
            self.assert_outside_untouched(outside)

    def test_a_pipe_is_never_read_written_over_or_removed(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("this system has no named pipes in the file system")
        os.mkfifo(self.repo / "src/pipe")
        self.assertEqual(packet.occupant(self.repo, "src/pipe"), "other")
        self.assertIsNone(packet.read_entry(self.repo, "src/pipe"))
        self.assertIs(packet.return_path(self.repo, "src/pipe", ("file", b"written\n")), False)
        self.assertIs(packet.return_path(self.repo, "src/pipe", None), True)
        self.assertEqual(packet.occupant(self.repo, "src/pipe"), "other")

    def test_a_retargeted_folder_link_returns_to_the_target_head_has(self):
        # Review round 8, finding 1: os.replace cannot take a name a folder link holds on Windows, so the return
        # failed on every retry and each attempt left its temporary link behind.
        if not self.can_link():
            self.skipTest("this account cannot create symbolic links")
        self.git("config", "core.symlinks", "true")
        os.symlink(os.path.join("..", "docs"), self.repo / "src/gen", target_is_directory=True)
        self.git("add", "src/gen")
        self.git("commit", "-q", "-m", "a folder link")
        self.put("elsewhere/other.md", "elsewhere\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "another folder")
        self.begin("src")
        self.vacate("src/gen")
        os.symlink(os.path.join("..", "elsewhere"), self.repo / "src/gen", target_is_directory=True)
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(os.readlink(self.repo / "src/gen"), os.path.join("..", "docs"))
        self.assertEqual((self.repo / "src/gen/note.md").read_bytes(), b"note\n")  # it reaches into the folder again
        self.assertEqual(self.git("cat-file", "-p", "stash@{0}:src/gen"), "../elsewhere")
        self.assertEqual(self.read("elsewhere/other.md"), "elsewhere\n")
        self.assertEqual(self.leftovers(), [])
        self.assertEqual(self.status(), "")

    def test_each_tracked_kind_returns_over_each_kind_of_occupant(self):
        if not self.can_link():
            self.skipTest("this account cannot create symbolic links")
        import contextlib
        self.git("config", "core.symlinks", "true")
        tracked = ["file", "link"] + (["folder link"] if os.name == "nt" else [])
        pairs = [(head, held) for head in tracked for held in self.kinds()]
        for head, held in pairs:
            path = f"m/{head} under {held}".replace(" ", "-")
            if head == "file":
                self.put(path, "tracked file\n")
            elif head == "link":
                (self.repo / "m").mkdir(exist_ok=True)
                os.symlink("a-tracked-target.txt", self.repo / path)
            else:
                (self.repo / "m").mkdir(exist_ok=True)
                os.symlink(os.path.join("..", "docs"), self.repo / path, target_is_directory=True)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "one tracked entry of each kind for each occupant")
        with contextlib.ExitStack() as stack:
            outside = self.outside_folder(stack)
            self.begin("m")
            for head, held in pairs:
                path = f"m/{head} under {held}".replace(" ", "-")
                self.vacate(path)
                self.occupy(path, held, outside)
            code, _, err = self.cli("reject")
            self.assertEqual(code, 0, err)
            for head, held in pairs:
                path = f"m/{head} under {held}".replace(" ", "-")
                with self.subTest(head=head, held=held):
                    if head == "file":
                        self.assertEqual(packet.kind_of(self.repo / path), "file")
                        self.assertEqual(self.read(path), "tracked file\n")
                    elif head == "link":
                        self.assertEqual(os.readlink(self.repo / path), "a-tracked-target.txt")
                        self.assertFalse(os.name == "nt" and self.is_folder_link(path))
                    else:
                        self.assertEqual(os.readlink(self.repo / path), os.path.join("..", "docs"))
                        self.assertTrue(self.is_folder_link(path))
                        self.assertEqual((self.repo / path / "note.md").read_bytes(), b"note\n")
                    # What the worker left is in the stash, as git records that kind.
                    listed = self.git("ls-tree", "stash@{0}", path)
                    if held == "file":
                        self.assertRegex(listed, r"^100644 blob ")
                        self.assert_in_stash("stash@{0}", path, "the worker's file\n")
                    elif held == "link":
                        self.assertRegex(listed, r"^120000 blob ")
                        self.assertEqual(self.git("cat-file", "-p", f"stash@{{0}}:{path}"), "the-workers-target.txt")
                    elif held in ("folder link", "junction"):
                        self.assertRegex(listed, r"^120000 blob ")
                    else:  # nothing, or a folder holding nothing: a deletion
                        self.assertEqual(listed, "")
            self.assert_outside_untouched(outside)
            self.assertEqual(self.leftovers(), [])
            self.assertEqual(self.status(), "")

    def test_each_kind_of_untracked_occupant_is_set_aside_and_removed(self):
        import contextlib
        kinds = [k for k in self.kinds() if k not in ("nothing", "folder")]  # git lists neither as a change
        for kind in kinds:
            self.put(f"docs/group-{kind}/note.md".replace(" ", "-"), "grouped note\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "tracked folders")
        with contextlib.ExitStack() as stack:
            outside = self.outside_folder(stack)
            self.begin("src", "docs")
            for kind in kinds:
                slug = kind.replace(" ", "-")
                self.occupy(f"src/new-{slug}", kind, outside)            # at a free name
                self.occupy(f"src/deep-{slug}/in/it", kind, outside)     # in new folders
                self.vacate(f"docs/group-{slug}")
                self.occupy(f"docs/group-{slug}", kind, outside)         # in a tracked folder's place
            code, _, err = self.cli("reject")
            self.assertEqual(code, 0, err)
            for kind in kinds:
                slug = kind.replace(" ", "-")
                with self.subTest(kind=kind):
                    self.assertFalse(os.path.lexists(self.repo / f"src/new-{slug}"))
                    self.assertFalse(os.path.lexists(self.repo / f"src/deep-{slug}"))
                    self.assertEqual(packet.kind_of(self.repo / f"docs/group-{slug}"), "folder")
                    self.assertEqual(self.read(f"docs/group-{slug}/note.md"), "grouped note\n")
                    for path in (f"src/new-{slug}", f"src/deep-{slug}/in/it", f"docs/group-{slug}"):
                        listed = self.git("ls-tree", "stash@{0}^3", path)
                        if kind == "file":
                            self.assertRegex(listed, r"^100644 blob ")
                            self.assert_in_stash("stash@{0}", path, "the worker's file\n", "^3")
                        else:
                            self.assertRegex(listed, r"^120000 blob ")
                    # The tracked file the occupant displaced is recorded as gone in the stash's working tree.
                    self.assertEqual(self.git("ls-tree", "stash@{0}", f"docs/group-{slug}/note.md"), "")
            self.assert_outside_untouched(outside)
            self.assertEqual(self.leftovers(), [])
            self.assertEqual(self.status(), "")

    def test_a_junction_holding_the_same_files_as_the_tracked_folder_is_a_change(self):
        # git for Windows reads through a junction and reports no change; this command never reads through one.
        if os.name != "nt":
            self.skipTest("junctions are a Windows feature")
        import _winapi
        self.tracked_group()
        with tempfile.TemporaryDirectory() as outside:
            (pathlib.Path(outside) / "note.md").write_bytes(b"grouped note\n")
            self.vacate("docs/group")
            _winapi.CreateJunction(outside, str(self.repo / "docs/group"))
            code, _, err = self.cli("begin", "--name", NAME, "--path", "docs")
            self.assertEqual(code, 2)
            self.assertIn("docs/group", err)
            self.vacate("docs/group")
            self.put("docs/group/note.md", "grouped note\n")
            self.begin("docs")
            self.vacate("docs/group")
            _winapi.CreateJunction(outside, str(self.repo / "docs/group"))
            code, out, err = self.cli("show")
            self.assertEqual(code, 0, err)
            self.assertIn("inside  docs/group\n", out)
            self.assertIn("inside  docs/group/note.md\n", out)
            code, _, err = self.cli("reject")
            self.assertEqual(code, 0, err)
            self.assertEqual(packet.kind_of(self.repo / "docs/group"), "folder")
            self.assertEqual(self.read("docs/group/note.md"), "grouped note\n")
            self.assertEqual((pathlib.Path(outside) / "note.md").read_bytes(), b"grouped note\n")
            self.assertRegex(self.git("ls-tree", "stash@{0}^3", "docs/group"), r"^120000 blob ")
            self.assertEqual(self.status(), "")

    def test_no_temporary_is_left_when_a_return_fails_and_the_retry_finishes(self):
        if not self.can_link():
            self.skipTest("this account cannot create symbolic links")
        self.git("config", "core.symlinks", "true")
        (self.repo / "m").mkdir()
        os.symlink("a-tracked-target.txt", self.repo / "m/link")
        os.symlink("a-tracked-target.txt", self.repo / "m/gone")
        os.symlink(os.path.join("..", "docs"), self.repo / "m/folder-link", target_is_directory=True)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "tracked links")
        self.begin("src", "m")
        self.put("src/a.py", "a = 22, the worker's\n")
        for path, kind in (("m/link", "link"), ("m/folder-link", "folder link" if os.name == "nt" else "link")):
            self.vacate(path)
            self.occupy(path, kind, self.repo / "src")
        self.vacate("m/gone")
        held = {p: packet.read_entry(self.repo, p) for p in ("src/a.py", "m/link", "m/folder-link", "m/gone")}
        targets = {str(self.repo / p) for p in held}
        real_replace, real_rename = os.replace, os.rename

        refused = set()

        def refuse(real):
            def move(source, destination, *args, **kwargs):
                if str(destination) in targets and str(destination) not in refused:
                    refused.add(str(destination))  # the new entry is refused; an occupant going back is let in
                    raise PermissionError(13, "the name is held by another program", str(destination))
                return real(source, destination, *args, **kwargs)
            return move

        with mock.patch.object(packet.os, "replace", refuse(real_replace)), \
                mock.patch.object(packet.os, "rename", refuse(real_rename)):
            code, _, err = self.run_in_process("reject")
        self.assertEqual(code, 1)
        for path, entry in held.items():
            self.assertIn(path, err)
            self.assertEqual(packet.read_entry(self.repo, path), entry, path)  # what was there is there still
        self.assertEqual(self.leftovers(), [])
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.read("src/a.py"), "a = 1\n")
        self.assertEqual(os.readlink(self.repo / "m/link"), "a-tracked-target.txt")
        self.assertEqual(os.readlink(self.repo / "m/gone"), "a-tracked-target.txt")
        self.assertEqual(os.readlink(self.repo / "m/folder-link"), os.path.join("..", "docs"))
        self.assertEqual(self.leftovers(), [])
        self.assertEqual(self.status(), "")

    def test_a_path_returned_by_a_run_that_stopped_before_recording_it_is_not_taken_for_a_save(self):
        self.begin("src")
        self.put("src/a.py", "a = 23\n")
        self.put("src/b.py", "b\n")
        self.stopped_reject("return_path")  # the first path is returned, and the run dies before it is recorded
        self.assertEqual(self.state()["rejection"]["settled"], {})
        code, out, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertNotIn("kept on disk", out)
        self.assertEqual(self.read("src/a.py"), "a = 1\n")
        self.assertEqual(self.status(), "")

    def test_show_and_reject_refuse_without_an_open_packet(self):
        for verb in (("show",), ("show", "--stage", "--snapshot", "sha256:0"), ("reject",)):
            code, _, err = self.cli(*verb)
            self.assertEqual(code, 2, verb)
            self.assertIn("no packet is open", err)

    def test_the_script_never_discards_or_takes_back_a_change(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for word in ("stash drop", "stash pop", "stash clear", "restore", "clean", "reset"):
            self.assertIsNone(re.search(re.escape(word), source, re.I), word)


if __name__ == "__main__":
    unittest.main()
