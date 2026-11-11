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

    # one name, two spellings (review round 9): a path is its exact spelling, never another that answers to it

    def ignores_case(self):
        return (self.repo / "SRC" / "A.PY").exists()

    def respell(self, old, new):
        """Rename on disk alone, by way of a third name, so a change of case only is made on every system."""
        between = self.repo / (old + ".between")
        (self.repo / old).rename(between)
        between.rename(self.repo / new)

    def names_in(self, folder):
        return sorted(os.listdir(self.repo / folder))

    def tracked_sub(self):
        self.put("src/Sub/x.py", "x = 1\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "a tracked folder with a capital")

    def test_occupant_answers_for_the_exact_spelling_and_nothing_goes_through_another(self):
        if not self.ignores_case():
            self.skipTest("this file system keeps two spellings apart by itself")
        self.assertEqual(packet.occupant(self.repo, "src/a.py"), "file")
        for other in ("src/A.py", "SRC/a.py", "SRC/A.PY", "SRC/new.py", "Src/new/deep.py"):
            with self.subTest(spelling=other):
                self.assertEqual(packet.occupant(self.repo, other), "alias")
                self.assertIsNone(packet.read_entry(self.repo, other))
                self.assertIs(packet.return_path(self.repo, other, ("file", b"written through\n")), False)
                self.assertIs(packet.return_path(self.repo, other, None), True)
        self.assertEqual(self.names_in("."), [".git", ".gitignore", "docs", "src"])
        self.assertEqual(self.names_in("src"), ["a.py"])
        self.assertEqual(self.read("src/a.py"), "a = 1\n")
        self.assertEqual(self.leftovers(), [])

    def test_a_staged_rename_that_changes_only_the_case_is_staged_as_the_new_spelling_alone(self):
        # Review round 9, finding 1: both spellings read the one file, so both were added and the deletion was lost.
        self.begin("src")
        self.git("mv", "src/a.py", "src/A.py")
        code, out, err = self.cli("show")
        self.assertEqual(code, 0, err)
        self.assertIn("inside  src/a.py\n", out)
        self.assertIn("inside  src/A.py\n", out)
        code, out, err = self.cli("show", "--stage", "--snapshot", self.snapshot(out))
        self.assertEqual(code, 0, err)
        self.assertEqual(self.git("ls-files", "src").split(), ["src/A.py"])
        self.assertEqual(sorted(self.git("diff", "--cached", "--name-only", "--no-renames").split()),
                         ["src/A.py", "src/a.py"])
        self.assertEqual(self.git("show", ":src/A.py"), "a = 1\n")
        self.assertNotIn("left unstaged", out)

    def test_a_rename_on_disk_that_changes_only_the_case_is_shown_and_staged_as_a_rename(self):
        # git for Windows reports no change at all here: the index still says src/a.py and the folder says A.py.
        self.begin("src")
        self.respell("src/a.py", "src/A.py")
        self.put("src/A.py", "a = 2, under the new spelling\n")
        code, out, err = self.cli("show")
        self.assertEqual(code, 0, err)
        self.assertIn("inside  src/a.py\n", out)
        self.assertIn("inside  src/A.py\n", out)
        code, _, err = self.cli("show", "--stage", "--snapshot", self.snapshot(out))
        self.assertEqual(code, 0, err)
        self.assertEqual(self.git("ls-files", "src").split(), ["src/A.py"])
        self.assertEqual(self.git("show", ":src/A.py"), "a = 2, under the new spelling\n")
        self.assertEqual(self.names_in("src"), ["A.py"])

    def test_an_unedited_rename_on_disk_that_changes_only_the_case_is_a_change_git_does_not_list(self):
        self.respell("src/a.py", "src/A.py")
        code, _, err = self.cli("begin", "--name", NAME, "--path", "src")
        self.assertEqual(code, 2)
        self.assertIn("  src/a.py\n", err)
        self.assertIn("  src/A.py\n", err)
        self.respell("src/A.py", "src/a.py")
        self.begin("src")
        self.respell("src/a.py", "src/A.py")
        code, out, err = self.cli("show")
        self.assertEqual(code, 0, err)
        self.assertIn("--- new file src/A.py (6 bytes)\na = 1\n", out)
        if self.ignores_case():  # elsewhere git lists the old spelling as deleted in its own diff
            self.assertIn("--- gone src/a.py ", out)

    def test_reject_of_a_staged_case_only_rename_returns_heads_spelling_and_stashes_the_workers(self):
        self.begin("src")
        self.git("mv", "src/a.py", "src/A.py")
        self.put("src/A.py", "a = 3, edited after the rename\n")
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.names_in("src"), ["a.py"])
        self.assertEqual(self.read("src/a.py"), "a = 1\n")
        self.assertEqual(self.git("ls-files", "src").split(), ["src/a.py"])
        self.assertEqual(self.status(), "")
        self.assertEqual(self.git("ls-tree", "-r", "--name-only", "stash@{0}", "src").split(), ["src/A.py"])
        self.assertEqual(self.git("ls-tree", "-r", "--name-only", "stash@{0}^2", "src").split(), ["src/A.py"])
        self.assert_in_stash("stash@{0}", "src/A.py", "a = 3, edited after the rename\n")
        self.assert_in_stash("stash@{0}", "src/A.py", "a = 1\n", "^2")
        self.assertEqual(self.leftovers(), [])

    def test_reject_of_a_case_only_rename_on_disk_returns_heads_spelling_and_stashes_the_workers(self):
        self.begin("src")
        self.respell("src/a.py", "src/A.py")
        self.put("src/A.py", "a = 4, the worker's\n")
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.names_in("src"), ["a.py"])
        self.assertEqual(self.read("src/a.py"), "a = 1\n")
        self.assertEqual(self.status(), "")
        self.assertEqual(self.git("ls-tree", "-r", "--name-only", "stash@{0}", "src"), "")  # the old spelling is gone
        self.assert_in_stash("stash@{0}", "src/A.py", "a = 4, the worker's\n", "^3")
        self.assertEqual(self.leftovers(), [])

    def test_heads_spelling_is_held_back_while_a_kept_save_has_the_name_under_the_other(self):
        self.begin("src")
        self.respell("src/a.py", "src/A.py")
        self.put("src/A.py", "a = 5, the worker's\n")
        real = packet.store

        def owner_saves(*args, **kwargs):
            real(*args, **kwargs)
            self.put("src/A.py", "a = 6, the owner saved this mid-rejection\n")

        with mock.patch.object(packet, "store", owner_saves):
            code, out, _ = self.run_in_process("reject")
        self.assertEqual(code, 1)
        self.assertEqual(self.names_in("src"), ["A.py"])  # neither written through nor removed for HEAD's spelling
        self.assertEqual(self.read("src/A.py"), "a = 6, the owner saved this mid-rejection\n")
        self.assertIn("kept on disk, saved after the capture and not in the stash: src/A.py", out)
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.names_in("src"), ["a.py"])
        self.assertEqual(self.read("src/a.py"), "a = 1\n")
        self.assert_in_stash("stash@{0}", "src/A.py", "a = 6, the owner saved this mid-rejection\n", "^3")
        self.assert_in_stash("stash@{1}", "src/A.py", "a = 5, the worker's\n", "^3")
        self.assertEqual(self.status(), "")

    def respell_sub(self, staged):
        if staged:  # git for Windows refuses the one-step move of a folder onto another case of its own name
            self.git("mv", "src/Sub", "src/between")
            self.git("mv", "src/between", "src/sub")
        else:
            self.respell("src/Sub", "src/sub")
        self.put("src/sub/new.py", "new = 1\n")

    def test_a_folder_renamed_only_in_case_is_staged_under_the_new_spelling_alone(self):
        for staged in (True, False):
            with self.subTest(staged=staged):
                self.tracked_sub()
                self.begin("src")
                self.respell_sub(staged)
                code, out, err = self.cli("show")
                self.assertEqual(code, 0, err)
                for path in ("src/Sub/x.py", "src/sub/x.py", "src/sub/new.py"):
                    self.assertIn(f"inside  {path}\n", out)
                self.assertNotIn("src/Sub/new.py", out)
                code, _, err = self.cli("show", "--stage", "--snapshot", self.snapshot(out))
                self.assertEqual(code, 0, err)
                self.assertEqual(self.git("ls-files", "src").split(), ["src/a.py", "src/sub/new.py", "src/sub/x.py"])
                self.assertEqual(self.git("show", ":src/sub/x.py"), "x = 1\n")
                self.git("commit", "-q", "-m", "accepted")
                self.git("mv", "src/sub", "src/between")  # back for the next round
                self.git("mv", "src/between", "src/Sub")
                self.git("rm", "-q", "-f", "src/Sub/new.py")
                self.git("commit", "-q", "-m", "back")
                self.respell("src/Sub", "src/between")  # git leaves the folder's spelling on disk as it was
                self.respell("src/between", "src/Sub")
                self.git("rm", "-q", "-f", "src/Sub/x.py")
                self.git("commit", "-q", "-m", "without the folder")

    def test_reject_of_a_folder_renamed_only_in_case_returns_heads_spelling(self):
        for staged in (True, False):
            with self.subTest(staged=staged):
                self.tracked_sub()
                self.begin("src")
                self.respell_sub(staged)
                code, _, err = self.cli("reject")
                self.assertEqual(code, 0, err)
                self.assertEqual(self.names_in("src"), ["Sub", "a.py"])
                self.assertEqual(self.names_in("src/Sub"), ["x.py"])
                self.assertEqual(self.read("src/Sub/x.py"), "x = 1\n")
                self.assertEqual(self.status(), "")
                self.assertEqual(self.git("ls-tree", "-r", "--name-only", "stash@{0}", "src/Sub"), "")
                part = "" if staged else "^3"  # staged: tracked under the new spelling; on disk only: untracked
                self.assert_in_stash("stash@{0}", "src/sub/x.py", "x = 1\n", part)
                self.assert_in_stash("stash@{0}", "src/sub/new.py", "new = 1\n", "^3")
                self.assertEqual(self.leftovers(), [])
                self.git("rm", "-q", "-r", "src/Sub")
                self.git("commit", "-q", "-m", "without the folder")

    # attributes: a file comes back as HEAD's own .gitattributes check it out, never as the rejected ones do

    def checked_out_with_autocrlf(self, files):
        """Commit `files` with core.autocrlf=true (the owner's setting) and let git itself check the whole tree
        out again; returns the bytes git wrote for every tracked file."""
        self.git("config", "core.autocrlf", "true")
        for path, content in files.items():
            self.put(path, content)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "attributes fixture")
        tracked = [name for name in self.git("ls-files", "-z").split("\0") if name]
        for path in tracked:
            (self.repo / path).unlink()
        self.git("checkout", "--", ".")
        self.assertEqual(self.status(), "")
        return {path: (self.repo / path).read_bytes() for path in tracked}

    def assert_tree_is(self, checkout):
        self.assertEqual(self.status(), "")
        tracked = [name for name in self.git("ls-files", "-z").split("\0") if name]
        self.assertEqual({path: (self.repo / path).read_bytes() for path in tracked}, checkout)

    def test_reject_returns_a_file_by_heads_attributes_when_the_worker_changed_its_rule(self):
        # Round 10: HEAD's blob was converted by the .gitattributes on disk, the rejected one, so a hook whose rule
        # the worker turned from eol=lf to eol=crlf came back with CRLF beside the LF rule that had returned.
        checkout = self.checked_out_with_autocrlf({".gitattributes": "scripts/hooks/** text eol=lf\n",
                                                   "scripts/hooks/pre-commit": "#!/bin/sh\necho ok\n"})
        self.assertEqual(checkout["scripts/hooks/pre-commit"], b"#!/bin/sh\necho ok\n")
        self.assertEqual(checkout["src/a.py"], b"a = 1\r\n")  # no rule: core.autocrlf decides
        self.begin(".gitattributes", "scripts/hooks")
        self.put(".gitattributes", "scripts/hooks/** text eol=crlf\n")
        self.put("scripts/hooks/pre-commit", "#!/bin/sh\r\necho changed\r\n")
        code, out, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertIn("tree returned to HEAD; packet closed", out)
        self.assertEqual((self.repo / "scripts/hooks/pre-commit").read_bytes(), b"#!/bin/sh\necho ok\n")
        self.assert_tree_is(checkout)
        # The worker's change is whole in the stash, stored as git stash push stores it under the worker's rule.
        self.assert_in_stash("stash@{0}", ".gitattributes", "scripts/hooks/** text eol=crlf\n")
        self.assert_in_stash("stash@{0}", "scripts/hooks/pre-commit", "#!/bin/sh\necho changed\n")

    def test_reject_returns_a_file_by_heads_attributes_when_the_worker_added_a_rule_head_lacks(self):
        checkout = self.checked_out_with_autocrlf({"src/b.py": "b = 1\n"})
        self.assertNotIn(".gitattributes", checkout)
        self.assertEqual(checkout["src/a.py"], b"a = 1\r\n")
        self.begin(".gitattributes", "src")
        self.put(".gitattributes", "*.py text eol=lf\n")  # untracked: HEAD has no .gitattributes at all
        self.put("src/a.py", "a = 2\n")
        (self.repo / "src/b.py").unlink()
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertFalse((self.repo / ".gitattributes").exists())
        self.assertEqual((self.repo / "src/a.py").read_bytes(), b"a = 1\r\n")
        self.assertEqual((self.repo / "src/b.py").read_bytes(), b"b = 1\r\n")
        self.assert_tree_is(checkout)
        self.assert_in_stash("stash@{0}", ".gitattributes", "*.py text eol=lf\n", "^3")
        self.assert_in_stash("stash@{0}", "src/a.py", "a = 2\n")

    def test_a_rule_kept_on_disk_has_no_say_in_what_returns_either(self):
        # The rejected .gitattributes is saved again after the capture, so it stays on disk: the hook still
        # comes back as HEAD's rule checks it out.
        checkout = self.checked_out_with_autocrlf({".gitattributes": "scripts/hooks/** text eol=lf\n",
                                                   "scripts/hooks/pre-commit": "#!/bin/sh\necho ok\n"})
        self.begin(".gitattributes", "scripts/hooks")
        self.put(".gitattributes", "scripts/hooks/** text eol=crlf\n")
        self.put("scripts/hooks/pre-commit", "#!/bin/sh\r\necho changed\r\n")
        real = packet.store

        def store_then_save(*args):
            real(*args)
            self.put(".gitattributes", "scripts/hooks/** text eol=crlf\n# saved later\n")

        with mock.patch.object(packet, "store", store_then_save):
            code, _, err = self.run_in_process("reject")
        self.assertEqual(code, 1)
        self.assertIn(".gitattributes", err)
        self.assertEqual(self.read(".gitattributes"), "scripts/hooks/** text eol=crlf\n# saved later\n")
        self.assertEqual((self.repo / "scripts/hooks/pre-commit").read_bytes(), checkout["scripts/hooks/pre-commit"])

    def test_reject_refuses_and_changes_nothing_when_git_cannot_read_attributes_from_a_commit(self):
        self.begin("src")
        self.put("src/a.py", "a = 30\n")
        self.put("src/new.py", "new\n")
        real, asked = packet.run_git, []

        def old_git(repo, *args, **kwargs):
            if args[0].startswith("--attr-source="):
                asked.append(args)
                raise packet.GitFailed(f"git {args[0]} failed: unknown option: {args[0]}")
            return real(repo, *args, **kwargs)

        before = self.state()
        with mock.patch.object(packet, "run_git", old_git):
            code, _, err = self.run_in_process("reject")
        self.assertEqual(code, 2, err)
        self.assertEqual(len(asked), 1)  # asked once, before anything else, and nothing was converted without it
        self.assertIn("cannot read attributes from a commit", err)
        self.assertIn("nothing was changed", err)
        self.assertEqual(self.read("src/a.py"), "a = 30\n")
        self.assertEqual(self.read("src/new.py"), "new\n")
        self.assertEqual(self.git("stash", "list"), "")
        self.assertEqual(self.state(), before)
        code, _, err = self.cli("reject")  # the packet is still open: the same call under a git that can
        self.assertEqual(code, 0, err)
        self.assertEqual(self.status(), "")

    def test_a_file_from_head_is_never_converted_without_naming_heads_attributes(self):
        self.begin("src")
        self.put("src/a.py", "a = 31\n")
        real, converted = packet.run_git, []

        def watch(repo, *args, **kwargs):
            if "--filters" in args:
                converted.append(args)
            return real(repo, *args, **kwargs)

        with mock.patch.object(packet, "run_git", watch):
            code, _, err = self.run_in_process("reject")
        self.assertEqual(code, 0, err)
        at, stash = self.git("rev-parse", "HEAD").strip(), self.git("rev-parse", "stash@{0}").strip()
        # Round 13: the stash is read back too, by its own attributes; no conversion reads the rules on disk.
        self.assertEqual(converted, [(f"--attr-source={stash}", "cat-file", "--filters", f"{stash}:src/a.py"),
                                     (f"--attr-source={at}", "cat-file", "--filters", f"{at}:src/a.py")])

    # reject and the index: one step under git's own lock (round 11, finding 1)

    def index_path(self):
        return self.repo / ".git" / "index"

    def lock_path(self):
        return self.repo / ".git" / "index.lock"

    def owner_blob(self, text):
        """A version that exists nowhere but in git's object store until it is staged: no file on disk holds it."""
        made = subprocess.run([git_path(), "-C", str(self.repo), "hash-object", "-w", "--stdin"],
                              input=text.encode("utf-8"), capture_output=True, check=True, timeout=60)
        return made.stdout.decode().strip()

    def reject_with(self, between):
        """Run reject in-process and call `between` once, after reject has compared the index with the one its
        stash captured and before it replaces it: the moment it asks git for HEAD's index (`read-tree <HEAD>`)."""
        base, real, called = self.git("rev-parse", "HEAD").strip(), packet.run_git, []

        def run(repo, *args, **kwargs):
            if args == ("read-tree", base) and not called:
                called.append(args)
                between()
            return real(repo, *args, **kwargs)

        with mock.patch.object(packet, "run_git", run):
            result = self.run_in_process("reject")
        self.assertEqual(len(called), 1, "reject never asked for HEAD's index")
        return result

    def test_a_staging_git_attempts_between_the_compare_and_the_replace_is_refused_by_gits_own_lock(self):
        # Round 11: nothing was held across the compare and the replace, so this staging landed and was overwritten.
        self.begin("src")
        self.put("src/a.py", "a = 40\n")
        blob, attempts = self.owner_blob("staged by the owner, in no file\n"), []

        def stage():
            attempts.append(subprocess.run(
                [git_path(), "-C", str(self.repo), "update-index", "--cacheinfo", f"100644,{blob},docs/note.md"],
                capture_output=True, text=True, encoding="utf-8", timeout=60))

        code, out, err = self.reject_with(stage)
        self.assertNotEqual(attempts[0].returncode, 0, "the owner's staging landed in an index about to be replaced")
        self.assertIn("index.lock", attempts[0].stderr)  # git itself told the owner, naming the lock
        self.assertEqual(code, 0, err)  # nothing landed, so nothing was overwritten and nothing is left to keep
        self.assertIn("tree returned to HEAD; packet closed", out)
        self.assertFalse(self.lock_path().exists())
        self.assertEqual(self.status(), "")
        self.assert_in_stash("stash@{0}", "src/a.py", "a = 40\n")

    def test_an_index_written_past_the_lock_between_the_compare_and_the_replace_is_kept_and_named(self):
        # The same moment, by a program that does not ask for git's lock: the staged version is in no stash and
        # in no file, so the index that holds it is never replaced.
        self.begin("src")
        self.put("src/a.py", "a = 41\n")
        blob = self.owner_blob("staged past the lock, in no file\n")

        def stage():
            private = self.repo / ".git" / "owner-index"
            private.write_bytes(self.index_path().read_bytes())
            subprocess.run([git_path(), "-C", str(self.repo), "update-index", "--cacheinfo",
                            f"100644,{blob},docs/note.md"], env={**os.environ, "GIT_INDEX_FILE": str(private)},
                           capture_output=True, check=True, timeout=60)
            os.replace(private, self.index_path())

        code, out, err = self.reject_with(stage)
        self.assertEqual(code, 1, out + err)
        self.assertIn("kept the index", out)
        self.assertIn("docs/note.md", err)
        self.assertEqual(self.git("show", ":docs/note.md"), "staged past the lock, in no file\n")
        self.assertTrue((self.repo / "build/packet.json").exists())
        self.assertNotIn("packet closed", out)
        self.assertFalse(self.lock_path().exists())
        self.assertEqual(self.read("src/a.py"), "a = 1\n")  # the captured paths still went back
        # A further reject sets the kept index aside in a stash of its own.
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assert_in_stash("stash@{0}", "docs/note.md", "staged past the lock, in no file\n", "^2")
        self.assertEqual(self.status(), "")

    def test_an_index_lock_already_there_makes_reject_refuse_naming_it_and_change_nothing(self):
        self.begin("src")
        self.put("src/a.py", "a = 42\n")
        self.put("docs/note.md", "staged\n")
        self.git("add", "docs/note.md")
        self.lock_path().write_bytes(b"another command's")
        before, index = self.state(), self.index_path().read_bytes()
        code, out, err = self.cli("reject")
        self.assertEqual(code, 2, out + err)
        self.assertIn("index.lock", err)
        self.assertIn("nothing was changed", err)
        self.assertEqual(self.lock_path().read_bytes(), b"another command's")  # never removed, never written
        self.assertEqual(self.index_path().read_bytes(), index)
        self.assertEqual(self.state(), before)
        self.assertEqual(self.git("stash", "list"), "")
        self.assertEqual(self.read("src/a.py"), "a = 42\n")
        self.assertEqual(self.git("show", ":docs/note.md"), "staged\n")
        self.lock_path().unlink()  # the other command finished
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.status(), "")

    def test_an_index_lock_that_appears_once_the_stash_is_stored_stops_reject_and_is_left_alone(self):
        self.begin("src")
        self.put("src/a.py", "a = 43\n")
        self.put("docs/note.md", "staged\n")
        self.git("add", "docs/note.md")
        real, seen = packet.store, {}

        def store_then_lock(*args):
            real(*args)
            seen["index"] = self.index_path().read_bytes()
            self.lock_path().write_bytes(b"another command's")

        with mock.patch.object(packet, "store", store_then_lock):
            code, out, err = self.run_in_process("reject")
        self.assertEqual(code, 3, out + err)
        self.assertIn("index.lock", err)
        self.assertEqual(self.lock_path().read_bytes(), b"another command's")
        self.assertEqual(self.index_path().read_bytes(), seen["index"])
        self.assertEqual(self.read("src/a.py"), "a = 43\n")  # nothing is returned before the index is settled
        self.assertEqual(len(self.git("stash", "list").splitlines()), 1)
        self.assertTrue(self.state()["rejection"]["stored"])
        self.lock_path().unlink()
        code, _, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(len(self.git("stash", "list").splitlines()), 1)
        self.assertEqual(self.status(), "")
        self.assert_in_stash("stash@{0}", "docs/note.md", "staged\n", "^2")

    def test_a_failure_under_the_lock_removes_the_lock_and_leaves_the_index_byte_for_byte(self):
        for target, error in (("index_from", packet.GitFailed("git read-tree failed: no")),
                              ("publish_index", OSError("the rename was refused"))):
            with self.subTest(fails=target):
                self.begin("src")
                self.put("src/a.py", "a = 44\n")
                self.put("docs/note.md", "staged\n")
                self.git("add", "docs/note.md")
                seen = {}

                def fail(*args, **kwargs):
                    seen["index"] = self.index_path().read_bytes()
                    seen["locked"] = self.lock_path().exists()
                    raise error

                with mock.patch.object(packet, target, fail):
                    code, out, err = self.run_in_process("reject")
                self.assertEqual(code, 3, out + err)
                self.assertTrue(seen["locked"])  # the failure struck while this command held the lock
                self.assertFalse(self.lock_path().exists())
                self.assertEqual(self.index_path().read_bytes(), seen["index"])
                self.assertEqual(self.git("show", ":docs/note.md"), "staged\n")
                self.assertEqual(sorted(p.name for p in (self.repo / ".git").glob("tmp*")), [])
                self.assertTrue((self.repo / "build/packet.json").exists())
                code, _, err = self.cli("reject")
                self.assertEqual(code, 0, err)
                self.assertEqual(self.status(), "")
                self.assert_in_stash("stash@{0}", "docs/note.md", "staged\n", "^2")

    def died_at_the_rename(self):
        """A reject that dies right after the new index took its name, before it could record that it did."""
        self.begin("src")
        self.put("src/a.py", "a = 45\n")
        self.put("docs/note.md", "staged\n")
        self.git("add", "docs/note.md")
        self.stopped_reject("publish_index")
        noted = self.state()["rejection"]["index"]
        self.assertEqual(noted["state"], "replacing")
        self.assertNotEqual(noted["was"], noted["next"])
        self.assertFalse(self.lock_path().exists())
        self.assertEqual(self.read("src/a.py"), "a = 45\n")
        return noted

    def resume_without_writing_the_index(self):
        real, made = packet.run_git, []

        def watch(repo, *args, **kwargs):
            if args[0] == "read-tree":
                made.append(args)
            return real(repo, *args, **kwargs)

        with mock.patch.object(packet, "run_git", watch), \
                mock.patch.object(packet, "publish_index", side_effect=AssertionError("the index was written twice")):
            code, out, err = self.run_in_process("reject")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(made, [])
        self.assertIn("tree returned to HEAD; packet closed", out)
        self.assertEqual(self.status(), "")
        self.assertFalse((self.repo / "build/packet.json").exists())
        self.assertEqual(len(self.git("stash", "list").splitlines()), 1)
        self.assert_in_stash("stash@{0}", "docs/note.md", "staged\n", "^2")
        self.assert_in_stash("stash@{0}", "src/a.py", "a = 45\n")

    def test_a_reject_that_died_right_after_the_rename_finds_the_new_index_landed(self):
        noted = self.died_at_the_rename()
        self.assertEqual(packet.fingerprint(self.index_path().read_bytes()), noted["next"])
        self.resume_without_writing_the_index()

    def test_a_reject_that_died_right_after_the_rename_resumes_after_git_wrote_the_index_again(self):
        # The owner's own git command writes the index before the resume (git status stores what it learned of
        # each file), so its bytes are no longer the recorded ones: the tree they hold still says HEAD's landed.
        noted = self.died_at_the_rename()
        self.status()
        self.assertNotEqual(packet.fingerprint(self.index_path().read_bytes()), noted["next"])
        self.resume_without_writing_the_index()

    def test_an_index_staged_after_a_reject_died_at_the_rename_is_kept(self):
        self.died_at_the_rename()
        blob = self.owner_blob("staged after the crash, in no file\n")
        self.git("update-index", "--cacheinfo", f"100644,{blob},docs/note.md")
        code, out, _ = self.cli("reject")
        self.assertEqual(code, 1)
        self.assertIn("kept the index", out)
        self.assertEqual(self.git("show", ":docs/note.md"), "staged after the crash, in no file\n")
        self.assertTrue((self.repo / "build/packet.json").exists())

    def test_reject_builds_its_stash_without_a_git_command_on_the_live_index_and_writes_it_once(self):
        # Every git call that names an index names a private one; the live index changes only at the rename.
        self.begin("src")
        self.put("src/a.py", "a = 46\n")
        self.put("docs/note.md", "staged\n")
        self.git("add", "docs/note.md")
        real, live, renames = packet.run_git, [], []
        writers = ("write-tree", "read-tree", "update-index", "add", "rm", "mv", "checkout", "commit", "apply")

        def watch(repo, *args, **kwargs):
            if args[0] in writers and "GIT_INDEX_FILE" not in (kwargs.get("env") or {}):
                live.append(args)
            return real(repo, *args, **kwargs)

        real_publish = packet.publish_index

        def publish(lock, index):
            renames.append((pathlib.Path(lock), pathlib.Path(index)))
            real_publish(lock, index)

        with mock.patch.object(packet, "run_git", watch), mock.patch.object(packet, "publish_index", publish):
            code, _, err = self.run_in_process("reject")
        self.assertEqual(code, 0, err)
        self.assertEqual(live, [])
        self.assertEqual(renames, [(self.lock_path(), self.index_path())])

    def test_git_never_inherits_an_attribute_source(self):
        # An inherited GIT_ATTR_SOURCE redirected hash-object --path and cat-file --filters to a tree the shell
        # named; one that names nothing made every conversion fail.
        self.begin("src")
        self.put("src/a.py", "a = 47\n")
        with mock.patch.dict(os.environ, {"GIT_ATTR_SOURCE": "refs/heads/names-nothing"}):
            self.assertNotIn("GIT_ATTR_SOURCE", packet.git_environment())
            self.assertEqual(packet.git_environment({"GIT_INDEX_FILE": "x"})["GIT_INDEX_FILE"], "x")
            blob = packet.run_git(self.repo, "hash-object", "--stdin", "--path=src/a.py", data=b"a = 47\n")
            code, out, err = self.run_in_process("reject")
        self.assertEqual(blob.decode().strip(), self.owner_blob("a = 47\n"))
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.read("src/a.py"), "a = 1\n")
        self.assert_in_stash("stash@{0}", "src/a.py", "a = 47\n")

    def test_git_never_follows_an_inherited_attribute_source_to_another_trees_rules(self):
        # A source that does name a tree: its eol=crlf rule must have no say in what is stashed.
        self.put(".gitattributes", "*.py text eol=crlf\n")
        self.git("add", ".gitattributes")
        self.git("commit", "-q", "-m", "a rule on a side branch")
        self.git("branch", "ruled")
        (self.repo / ".gitattributes").unlink()
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "no rule here")
        self.begin("src")
        self.put("src/a.py", "a = 48\r\n")
        with mock.patch.dict(os.environ, {"GIT_ATTR_SOURCE": "ruled"}):
            code, out, err = self.run_in_process("reject")
        self.assertEqual(code, 0, out + err)
        stored = subprocess.run([git_path(), "-C", str(self.repo), "cat-file", "blob", "stash@{0}:src/a.py"],
                                capture_output=True, check=True, timeout=60).stdout
        self.assertEqual(stored, b"a = 48\r\n")  # under `ruled`'s rule the blob would hold LF alone

    # reject and the index: one read behind the listing and the stash (round 12, finding 1)

    def every_kind_of_change(self):
        """A tree holding each kind of change the tests above use, with a packet open over it; what `git status`
        and both diffs say of it, and the bytes of its untracked files."""
        for name in ("gone", "lost", "old", "kept"):
            self.put(f"docs/{name}.md", f"{name}\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "more to change")
        self.begin("src")
        self.put("src/a.py", "a = 50\n")
        self.git("add", "src/a.py")
        self.put("src/a.py", "a = 51\n")                 # staged, then edited again
        self.put("docs/note.md", "note, edited\n")       # an unstaged edit
        self.put("src/staged.py", "staged = True\n")
        self.git("add", "src/staged.py")                 # a staged new file
        self.put("src/new.py", "new = True\n")           # an untracked file
        self.put("new/dir/c.py", "c\n")                  # an untracked file in a new folder
        self.git("rm", "-q", "docs/gone.md")             # a staged deletion
        (self.repo / "docs/lost.md").unlink()            # an unstaged deletion
        self.git("mv", "docs/old.md", "docs/renamed.md")  # a staged rename
        return self.whole_state()

    def whole_state(self):
        loose = self.git("ls-files", "--others", "--exclude-standard", "-z").split("\0")
        return {"status": self.status(), "staged": self.git("diff", "--cached"), "unstaged": self.git("diff"),
                "untracked": {path: self.read(path) for path in loose if path}}

    def paths_in(self, commit):
        return set(filter(None, self.git("ls-tree", "-r", "-z", "--name-only", commit).split("\0")))

    def reject_while_the_owner_stages(self, *staging):
        """Run reject in-process; right after it has listed and read the changed paths, and before it builds the
        stash, the owner's `git <staging>` lands in the live index. The stash commit and reject's result."""
        real = packet.capture

        def capture_then_stage(*args, **kwargs):
            captured = real(*args, **kwargs)
            if staging:
                self.git(*staging)
            return captured

        with mock.patch.object(packet, "capture", capture_then_stage):
            code, out, err = self.run_in_process("reject")
        return self.git("rev-parse", "stash@{0}").strip(), code, out + err

    def assert_the_stash_brings_back(self, stash, before):
        """`stash` is in git's standard shape, and `git stash apply --index` on HEAD's tree brings back `before`."""
        self.assertEqual(self.paths_in(stash) & self.paths_in(stash + "^3"), set(),
                         "a path is in both the stash's working-tree commit and its untracked parent")
        self.assertEqual(self.paths_in(stash + "^2") & self.paths_in(stash + "^3"), set(),
                         "a path is in both the stash's index commit and its untracked parent")
        for _ in range(3):  # whatever the first reject kept is set aside too, in stashes of its own
            if not (self.repo / "build/packet.json").exists():
                break
            self.cli("reject")
        self.assertEqual(self.status(), "")
        self.assertFalse((self.repo / "build/packet.json").exists())
        applied = subprocess.run([git_path(), "-C", str(self.repo), "stash", "apply", "--index", stash],
                                 capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        self.assertEqual(self.whole_state(), before)
        self.assertEqual(sorted(p.name for p in (self.repo / ".git").glob("tmp*")), [])
        self.assertFalse(self.lock_path().exists())

    def test_reject_then_stash_apply_brings_back_every_kind_of_change(self):
        before = self.every_kind_of_change()
        stash, code, out = self.reject_while_the_owner_stages()
        self.assertEqual(code, 0, out)
        self.assertIn("tree returned to HEAD; packet closed", out)
        self.assert_the_stash_brings_back(stash, before)

    def test_an_untracked_file_staged_between_the_listing_and_the_stash_is_in_the_stash_once(self):
        # Round 12: the file was listed as untracked, then the index read for the stash had it, so it went into
        # both the working-tree commit and the untracked parent and `git stash apply --index` could not bring
        # it back.
        before = self.every_kind_of_change()
        stash, code, out = self.reject_while_the_owner_stages("add", "src/new.py")
        staged_in_stash = "src/new.py" in self.paths_in(stash + "^2")
        self.assertTrue(staged_in_stash or (code == 1 and "kept the index" in out), out)
        if not staged_in_stash:  # kept and named: the staging is still in the live index, in no stash yet
            self.assertEqual(self.git("show", ":src/new.py"), "new = True\n")
            self.assertTrue((self.repo / "build/packet.json").exists())
            self.assertNotIn("packet closed", out)
            self.assert_the_stash_brings_back(stash, before)
            # The staging itself went into the next reject's stash, as its index commit.
            self.assert_in_stash("stash@{0}", "src/new.py", "new = True\n", "^2")
        else:
            self.assertEqual(self.paths_in(stash) & self.paths_in(stash + "^3"), set())

    def test_a_tracked_edit_staged_between_the_listing_and_the_stash_is_stashed_as_it_was_listed(self):
        # The same two reads: docs/note.md was listed as an unstaged edit and stashed as a staged one.
        before = self.every_kind_of_change()
        stash, code, out = self.reject_while_the_owner_stages("add", "docs/note.md")
        self.assertEqual(code, 1, out)
        self.assertIn("kept the index", out)
        self.assertEqual(self.git("show", ":docs/note.md"), "note, edited\n")
        self.assertEqual(self.git("show", stash + "^2:docs/note.md"), "note\n")
        self.assert_the_stash_brings_back(stash, before)

    def test_a_file_unstaged_between_the_listing_and_the_stash_stays_in_the_stash_and_on_disk(self):
        # The same two reads: docs/kept.md was listed as tracked and unchanged, then the index read for the stash
        # no longer had it, so the stash recorded its deletion and applying the stash removed the file.
        before = self.every_kind_of_change()
        stash, code, out = self.reject_while_the_owner_stages("rm", "-q", "--cached", "docs/kept.md")
        self.assertEqual(code, 1, out)
        self.assertIn("kept the index", out)
        self.assertEqual(self.read("docs/kept.md"), "kept\n")
        self.assertIn("docs/kept.md", self.paths_in(stash))
        self.assertIn("docs/kept.md", self.paths_in(stash + "^2"))
        self.assert_the_stash_brings_back(stash, before)
        self.assertEqual(self.read("docs/kept.md"), "kept\n")

    def test_reject_asks_the_live_index_nothing_and_leaves_its_bytes_alone_until_the_stash_is_stored(self):
        # Every git call that reads or writes an index, from the listing to the stored stash, names one private
        # index file, the same one for the listing and for the stash's index commit.
        self.every_kind_of_change()
        asks = ("diff", "ls-files", "status", "write-tree", "read-tree", "update-index", "diff-index", "diff-files")
        real, real_store, before = packet.run_git, packet.store, self.index_path().read_bytes()
        live, private, seen = [], {}, {}

        def watch(repo, *args, **kwargs):
            if args[0] in asks and "stored" not in seen:
                named = (kwargs.get("env") or {}).get("GIT_INDEX_FILE")
                if named is None:
                    live.append(args)
                else:
                    private.setdefault(named, []).append(args[0])
            return real(repo, *args, **kwargs)

        def store(*args, **kwargs):
            seen["stored"] = self.index_path().read_bytes()
            return real_store(*args, **kwargs)

        with mock.patch.object(packet, "run_git", watch), mock.patch.object(packet, "store", store):
            code, out, err = self.run_in_process("reject")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(live, [])
        self.assertEqual(seen["stored"], before)
        listed = [calls for calls in private.values() if "ls-files" in calls and "diff" in calls]
        self.assertEqual(len(listed), 1, private)
        self.assertIn("status" if "status" in listed[0] else "diff", listed[0])
        self.assertIn("write-tree", listed[0])  # the stash's index commit is the tree of the index that was listed

    def test_a_save_made_in_the_second_the_index_was_written_is_still_listed_from_the_private_copy(self):
        # git reads a file's content, whatever its recorded size and times say, when the file is as new as the
        # index itself. A private copy stamped with the time it was made would be newer than every file, and a
        # save of the same size made in the index's own second would be listed nowhere.
        moment = 1_600_000_000 * 10**9  # seconds before any copy this test's reject can make
        os.utime(self.repo / "src/a.py", ns=(moment, moment))
        self.git("add", "src/a.py")  # the index records the file's time; its content is HEAD's still
        self.begin("src")
        self.put("src/a.py", "a = 9\n")  # the only change: the same size, and the time the index recorded
        os.utime(self.repo / "src/a.py", ns=(moment, moment))
        os.utime(self.index_path(), ns=(moment, moment))  # and the index was written in that same moment
        code, out, err = self.cli("reject")
        self.assertEqual(code, 0, out + err)
        self.assertNotIn("nothing to set aside", out)
        self.assert_in_stash("stash@{0}", "src/a.py", "a = 9\n")
        self.assertEqual(self.read("src/a.py"), "a = 1\n")
        self.assertEqual(self.status(), "")

    def test_the_private_index_keeps_the_time_the_live_index_was_written(self):
        self.begin("src")
        self.put("src/a.py", "a = 62\n")
        self.git("add", "src/a.py")
        long_ago = 1_600_000_000 * 10**9
        os.utime(self.index_path(), ns=(long_ago, long_ago))
        raw = self.index_path().read_bytes()
        with packet.index_snapshot(self.repo) as env:
            copy = pathlib.Path(env["GIT_INDEX_FILE"])
            self.assertNotEqual(copy, self.index_path())
            self.assertEqual(copy.read_bytes(), raw)
            self.assertEqual(os.stat(copy).st_mtime_ns, long_ago)
            folder = copy.parent
        self.assertFalse(folder.exists())
        self.assertEqual(self.index_path().read_bytes(), raw)

    def test_no_private_index_is_left_when_the_stash_cannot_be_built(self):
        for target in ("capture", "build_stash", "stash_entry"):
            with self.subTest(fails=target):
                self.begin("src")
                self.put("src/a.py", "a = 63\n")
                before, stashes = self.index_path().read_bytes(), self.git("stash", "list")
                with mock.patch.object(packet, target, side_effect=OSError("no")):
                    code, out, err = self.run_in_process("reject")
                self.assertEqual(code, 3, out + err)
                self.assertEqual(sorted(p.name for p in (self.repo / ".git").glob("tmp*")), [])
                self.assertEqual(self.index_path().read_bytes(), before)
                self.assertEqual(self.read("src/a.py"), "a = 63\n")
                self.assertEqual(self.git("stash", "list"), stashes)
                code, _, err = self.cli("reject")
                self.assertEqual(code, 0, err)
                self.assert_in_stash("stash@{0}", "src/a.py", "a = 63\n")

    # reject: the stored stash gives back every captured path, or nothing is removed (round 13, finding 1)

    MIXED = b"one\r\ntwo\nthree\r\n"

    def put_bytes(self, path, raw):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def raw(self, path):
        return (self.repo / path).read_bytes()

    def blob(self, name):
        """The bytes of the object `name`, exactly as git stores them."""
        return subprocess.run([git_path(), "-C", str(self.repo), "cat-file", "blob", name], capture_output=True,
                              check=True, timeout=60).stdout

    def commit_rule(self, rule):
        self.put(".gitattributes", rule)
        self.git("add", ".gitattributes")
        self.git("commit", "-q", "-m", "a rule")

    def reject_with_a_save_after_the_capture(self, save):
        """Run reject in-process; `save` runs at the seam, when every changed path has been read and before the
        stash is built from what was read. The stash commit and reject's result."""
        real = packet.capture

        def capture_then_save(*args, **kwargs):
            captured = real(*args, **kwargs)
            save()
            return captured

        with mock.patch.object(packet, "capture", capture_then_save):
            code, out, err = self.run_in_process("reject")
        return self.git("rev-parse", "stash@{0}").strip(), code, out + err

    def finish_and_apply(self, stash):
        """Set aside whatever the first reject left (a save made after its capture), then let git itself bring
        `stash` back onto HEAD's tree."""
        for _ in range(3):
            if not (self.repo / "build/packet.json").exists():
                break
            self.cli("reject")
        self.assertEqual(self.status(), "")
        self.assertFalse((self.repo / "build/packet.json").exists())
        applied = subprocess.run([git_path(), "-C", str(self.repo), "stash", "apply", "--index", stash],
                                 capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)

    def test_an_untracked_file_whose_rule_is_edited_between_the_capture_and_the_stash_comes_back_whole(self):
        # Round 13: the blob was made under the rule on disk when the stash was built (eol=lf, saved after the
        # file was read under -text), so the stash held LF alone, and reject then removed the file: its mixed
        # endings were in neither the stash nor the tree.
        self.commit_rule("src/fixture.txt -text\n")
        self.begin("src")
        self.put_bytes("src/fixture.txt", self.MIXED)
        stash, code, out = self.reject_with_a_save_after_the_capture(
            lambda: self.put(".gitattributes", "src/fixture.txt text eol=lf\n"))
        self.assertEqual(code, 1, out)  # the rule saved after the capture is in no stash yet: kept and named
        self.assertIn(".gitattributes", out)
        self.assertFalse((self.repo / "src/fixture.txt").exists())
        self.assertEqual(self.read(".gitattributes"), "src/fixture.txt text eol=lf\n")
        self.assertEqual(self.blob(f"{stash}^3:src/fixture.txt"), self.MIXED)
        self.assertIn("stored as the bytes they are, which the stash gives back exactly", out)
        self.finish_and_apply(stash)
        self.assertEqual(self.raw("src/fixture.txt"), self.MIXED)
        self.assertEqual(self.read(".gitattributes"), "src/fixture.txt -text\n")

    def test_a_tracked_file_whose_rule_is_edited_between_the_capture_and_the_stash_comes_back_whole(self):
        self.commit_rule("src/a.py -text\n")
        self.begin("src")
        self.put_bytes("src/a.py", self.MIXED)
        stash, code, out = self.reject_with_a_save_after_the_capture(
            lambda: self.put(".gitattributes", "src/a.py text eol=lf\n"))
        self.assertEqual(code, 1, out)
        self.assertEqual(self.read("src/a.py"), "a = 1\n")  # it still held the captured bytes, so HEAD's returned
        self.assertEqual(self.blob(f"{stash}:src/a.py"), self.MIXED)
        self.finish_and_apply(stash)
        self.assertEqual(self.raw("src/a.py"), self.MIXED)
        self.assertEqual(self.status(), " M src/a.py\n")

    def test_every_kind_of_change_comes_back_whole_when_a_rule_is_edited_between_the_capture_and_the_stash(self):
        self.commit_rule("* -text\n")
        self.every_kind_of_change()
        mixed = ("src/a.py", "docs/note.md", "src/new.py", "new/dir/c.py")  # staged and edited, edited, untracked
        for path in mixed:
            self.put_bytes(path, self.MIXED + path.encode())
        before = self.whole_state()
        stash, code, out = self.reject_with_a_save_after_the_capture(
            lambda: self.put(".gitattributes", "* text eol=lf\n"))
        self.assertEqual(code, 1, out)
        for path in mixed[2:]:
            self.assertFalse((self.repo / path).exists(), path)
        self.assert_the_stash_brings_back(stash, before)
        for path in mixed:
            self.assertEqual(self.raw(path), self.MIXED + path.encode(), path)

    def test_mixed_line_endings_git_would_normalise_are_stored_as_they_are_and_come_back_whole(self):
        # No save in between is needed: under core.autocrlf (the owner's setting) the blob git add makes of a
        # file with mixed endings holds LF alone and checks out with CRLF alone.
        self.git("config", "core.autocrlf", "true")
        self.begin("src")
        self.put_bytes("src/a.py", self.MIXED)
        self.put_bytes("src/new.txt", self.MIXED)
        self.put_bytes("src/crlf.txt", b"one\r\ntwo\r\n")
        before = self.whole_state()
        code, out, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertIn("stored as the bytes they are, which the stash gives back exactly (the blob git add makes of "
                      "them would not): src/a.py, src/new.txt\n", out)
        self.assertEqual(self.blob("stash@{0}^3:src/crlf.txt"), b"one\ntwo\n")  # as git add stores it: it comes back
        self.finish_and_apply("stash@{0}")
        self.assertEqual(self.raw("src/a.py"), self.MIXED)
        self.assertEqual(self.raw("src/new.txt"), self.MIXED)
        self.assertEqual(self.raw("src/crlf.txt"), b"one\r\ntwo\r\n")
        self.assertEqual(self.whole_state(), before)

    def test_a_file_git_converts_on_every_checkout_is_stored_as_its_bytes_and_named(self):
        # A file saved with LF where the stash's own rules check out CRLF: no blob comes back as LF, so the blob
        # is the bytes themselves and git reads what it writes back as the same content.
        self.git("config", "core.autocrlf", "true")
        self.begin("src")
        self.put("src/a.py", "a = 2\n")
        self.put("src/new.py", "new\n")
        before = self.whole_state()
        code, out, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        stash = self.git("rev-parse", "stash@{0}").strip()
        self.assertIn(f"`git cat-file blob {stash}:<path>` (`{stash}^3:<path>` for a new file) prints them exactly: "
                      "src/a.py, src/new.py\n", out)
        self.assertEqual(self.blob(f"{stash}:src/a.py"), b"a = 2\n")
        self.assertEqual(self.blob(f"{stash}^3:src/new.py"), b"new\n")
        self.finish_and_apply(stash)
        self.assertEqual(self.raw("src/a.py"), b"a = 2\r\n")  # git's own conversion, of exactly those bytes
        self.assertEqual(self.raw("src/new.py"), b"new\r\n")
        after = self.whole_state()
        self.assertEqual((after["status"], after["staged"], after["unstaged"]),
                         (before["status"], before["staged"], before["unstaged"]))

    def one_way_filter(self):
        """A filter that does not undo itself, on *.dat, tracked in HEAD's .gitattributes; a packet open over an
        edit, a staged edit and an untracked file under that filter."""
        self.git("config", "filter.oneway.clean", "cat")
        self.git("config", "filter.oneway.smudge", "tr a b")
        self.commit_rule("*.dat filter=oneway\n")
        self.begin("src")
        self.put("src/a.py", "a = 70\n")
        self.put("docs/note.md", "staged\n")
        self.git("add", "docs/note.md")
        self.put("src/data.dat", "banana\n")

    def test_a_path_no_stored_form_gives_back_stops_reject_before_anything_is_changed(self):
        self.one_way_filter()
        index = self.index_path().read_bytes()
        for attempt in (1, 2):  # the second call finds nothing new and stores no second stash
            with self.subTest(attempt=attempt):
                code, out, err = self.cli("reject")
                self.assertEqual(code, 1, out + err)
                self.assertIn("NOT REJECTED", err)
                self.assertIn("in any form they can be stored in: src/data.dat. Nothing in the tree", err)
                self.assertEqual(self.read("src/data.dat"), "banana\n")
                self.assertEqual(self.read("src/a.py"), "a = 70\n")
                self.assertEqual(self.index_path().read_bytes(), index)
                self.assertFalse(self.lock_path().exists())
                self.assertEqual(sorted(p.name for p in (self.repo / ".git").glob("tmp*")), [])
                rejection = self.state()["rejection"]
                self.assertEqual(rejection["forms"], {"docs/note.md": "filtered", "src/a.py": "filtered",
                                                      "src/data.dat": "none"})
                self.assertEqual(rejection["settled"], {})
                self.assertEqual(self.git("stash", "list", "--format=%H").split(), [rejection["stash"]])
                self.assertEqual(self.blob(f"{rejection['stash']}^3:src/data.dat"), b"banana\n")
                self.assert_in_stash(rejection["stash"], "src/a.py", "a = 70\n")
                self.assert_in_stash(rejection["stash"], "docs/note.md", "staged\n", "^2")

    def test_reject_goes_on_once_the_rule_that_had_no_form_is_changed(self):
        self.one_way_filter()
        self.assertEqual(self.cli("reject")[0], 1)
        first = self.state()["rejection"]["stash"]
        self.put(".gitattributes", "*.dat -text\n")  # the owner takes the filter off: a change like any other
        code, out, err = self.cli("reject")
        self.assertEqual(code, 0, out + err)
        self.assertIn("tree returned to HEAD; packet closed", out)
        self.assertEqual(self.status(), "")
        self.assertFalse((self.repo / "src/data.dat").exists())
        self.assertEqual(self.read(".gitattributes"), "*.dat filter=oneway\n")
        stashes = self.git("stash", "list", "--format=%H").split()
        self.assertEqual(stashes[1:], [first])  # never taken back out
        self.git("stash", "apply", "--index", stashes[0])
        self.assertEqual(self.read("src/data.dat"), "banana\n")
        self.assertEqual(self.read(".gitattributes"), "*.dat -text\n")
        self.assertEqual(self.read("src/a.py"), "a = 70\n")

    def test_an_untracked_file_is_checked_by_the_rules_git_applies_to_it_from_the_tracked_tree(self):
        # git writes a stash's untracked files with the tracked .gitattributes in place: read by the untracked
        # parent's rules alone (it has none), this file would pass as LF and come back from git as CRLF.
        self.commit_rule("*.txt text eol=crlf\n")
        self.begin("src")
        self.put_bytes("src/crlf.txt", b"one\r\ntwo\r\n")
        self.put_bytes("src/lf.txt", b"one\ntwo\n")
        code, out, err = self.cli("reject")
        self.assertEqual(code, 0, err)
        self.assertIn("prints them exactly: src/lf.txt\n", out)
        self.assertNotIn("src/crlf.txt", out)
        self.finish_and_apply("stash@{0}")
        self.assertEqual(self.raw("src/crlf.txt"), b"one\r\ntwo\r\n")
        self.assertEqual(self.raw("src/lf.txt"), b"one\r\ntwo\r\n")

    def test_the_form_of_every_changed_path_is_recorded_before_the_stash_is_stored(self):
        self.every_kind_of_change()
        self.stopped_reject("store", after=False)
        rejection = self.state()["rejection"]
        self.assertFalse(rejection["stored"])
        self.assertEqual(rejection["forms"], {
            "docs/gone.md": "absent", "docs/lost.md": "absent", "docs/old.md": "absent", "docs/note.md": "filtered",
            "docs/renamed.md": "filtered", "new/dir/c.py": "filtered", "src/a.py": "filtered",
            "src/new.py": "filtered", "src/staged.py": "filtered"})
        self.assertEqual(sorted(rejection["forms"]), sorted(rejection["paths"]))
        code, _, err = self.cli("reject")  # the resumed run keeps the record it found
        self.assertEqual(code, 0, err)
        self.assertEqual(self.git("rev-parse", "stash@{0}").strip(), rejection["stash"])

    def test_show_writes_the_marks_before_the_diffs_when_its_output_is_a_pipe(self):
        # The marks went through the text layer and the diffs past it, so a pipe or a file got the diffs first.
        self.begin("src")
        self.put("src/a.py", "a = 24\n")
        self.put("src/new.py", "new\n")
        code, out, err = self.cli("show")  # cli() reads standard output through a pipe
        self.assertEqual(code, 0, err)
        places = [out.index(line) for line in ("packet: " + NAME + "\n", "inside  src/a.py\n", "inside  src/new.py\n",
                                               "--- staged (", "--- unstaged (", "--- new file src/new.py",
                                               "snapshot: sha256:")]
        self.assertEqual(places, sorted(places))
        self.assertEqual(places[0], 0)
        digest = self.snapshot(out)
        code, out, err = self.cli("show", "--stage", "--snapshot", digest)
        self.assertEqual(code, 0, err)
        self.assertLess(out.index("snapshot: sha256:"), out.index("staged 2 path(s) exactly as reviewed"))

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
