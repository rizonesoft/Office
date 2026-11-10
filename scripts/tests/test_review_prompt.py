# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/review-prompt.py: each prompt is filled from the section and the range, and a wrong input is refused
(D00 T03 §27)."""
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
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
REPO = SCRIPTS.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_todo_graph as fixtures

spec = importlib.util.spec_from_file_location("review_prompt", SCRIPTS / "review-prompt.py")
review_prompt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review_prompt)
tg = review_prompt.todo_graph

SURFACE = "\n\nThe ribbon follows design/SPEC.md chapter 3."
ANGLES = "\n\nA body may hold `<x>`, `<one or two sentences>` and ```` fences."


class Base(unittest.TestCase):
    """A fixture repository: the two real templates, a TODO tree with three sections, and scratch beside it."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root = self.tmp / "repo"
        self.scratch = self.tmp / "scratch"
        self.scratch.mkdir()
        (self.root / "docs").mkdir(parents=True)
        for name in review_prompt.TEMPLATES.values():
            shutil.copy(REPO / name, self.root / name)
        todo = self.root / "todo" / "00-workspace"
        todo.mkdir(parents=True)
        rows = [(1, "Tooling", 0, "none", "--"), (2, "Ribbon", 0, "none", "--"), (3, "Angles", 0, "none", "--")]
        text = fixtures.todo_file(rows)
        text = text.replace("**Test checkpoint:** `true` exits 0.\n\n## 3.", "**Test checkpoint:** `true` exits 0."
                            + SURFACE + "\n\n## 3.")
        text = text.replace("**Test checkpoint:** `true` exits 0.\n\n## Verification",
                            "**Test checkpoint:** `true` exits 0." + ANGLES + "\n\n## Verification")
        (todo / "TODO-01-a.md").write_text(text, encoding="utf-8")
        (todo / "INDEX.md").write_text("# Index\n- TODO-01-a.md\n", encoding="utf-8")
        (self.root / "todo" / "TODO-00-INDEX.md").write_text("# Index\n- 00-workspace/TODO-01-a.md\n", encoding="utf-8")
        self.out = self.scratch / "prompt.md"

    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = review_prompt.main([str(a) for a in argv], root=self.root)
        return code, out.getvalue(), err.getvalue()

    def refused(self, *argv, reason):
        """The command exits 2 with `reason` in its one line, and an `--out` already there keeps its bytes."""
        self.out.write_bytes(b"earlier prompt\n")
        code, out, err = self.run_main(*argv)
        self.assertEqual((code, out), (2, ""), err)
        self.assertTrue(err.startswith("refused: "), err)
        self.assertEqual(len(err.strip().splitlines()), 1, err)
        self.assertIn(reason, err)
        self.assertEqual(self.out.read_bytes(), b"earlier prompt\n")
        return err


class Completion(Base):
    def completion(self, ref, *extra):
        return self.run_main("completion", ref, "--purpose", "It builds  the thing.", *extra, "--out", self.out)

    def test_the_prompt_holds_the_section_and_its_contract_digest(self):
        code, out, err = self.completion("D00 T01 §1", "--no-context", "tooling with no SPEC chapter")
        self.assertEqual(code, 0, err)
        row = tg.graph(self.root)["D00 T01 §1"]
        digest = tg.contract_digest(row)
        prompt = self.out.read_text(encoding="utf-8")
        self.assertEqual(json.loads(out), {"kind": "completion", "ref": "D00 T01 §1", "contract": digest,
                                           "out": str(self.out.resolve())})
        self.assertIn(f"- Contract: `{digest}`.", prompt)
        self.assertIn("- Reference and title: `D00 T01 §1 Tooling`.", prompt)
        self.assertIn("## 1. Tooling\n\n" + row.body.strip(), prompt)
        self.assertIn("- What the feature is for the user: It builds the thing.", prompt)
        self.assertIn("| 1 | §1 | Tooling | -- | [ ] |", prompt)  # the Implementation Order table
        self.assertIn("No further context: tooling with no SPEC chapter", prompt)
        self.assertTrue(prompt.startswith("You are an independent completion reviewer."), prompt[:80])
        for filled, _ in review_prompt.FILLS["completion"]:
            self.assertNotIn(filled, prompt)
        self.assertIn("`SECTION: <DNN TNN §N>`", prompt)  # the reply format stays as the template has it
        self.assertIn("`CONTRACT: sha256:<digest>`", prompt)

    def test_the_command_line_digest_is_the_one_in_the_prompt(self):
        self.completion("D00 T01 §1", "--no-context", "tooling")
        prompt = self.out.read_text(encoding="utf-8")
        self.assertIn(tg.contract_digest(tg.graph(self.root)["D00 T01 §1"]), prompt)

    def test_exactly_one_context_option_is_required(self):
        context = self.scratch / "context.md"
        context.write_text("The SPEC excerpt.\n", encoding="utf-8")
        self.refused("completion", "D00 T01 §1", "--purpose", "p", "--out", self.out,
                     reason="exactly one of --context <file> and --no-context <reason>")
        self.refused("completion", "D00 T01 §1", "--purpose", "p", "--context", context, "--no-context", "none",
                     "--out", self.out, reason="exactly one of --context <file> and --no-context <reason>")

    def test_a_section_that_cites_the_spec_needs_its_context(self):
        err = self.refused("completion", "D00 T01 §2", "--purpose", "p", "--no-context", "none", "--out", self.out,
                           reason="D00 T01 §2 needs --context, not --no-context")
        self.assertIn("design/SPEC.md", err)
        context = self.scratch / "context.md"
        context.write_text("SPEC chapter 3, inlined: the ribbon has four tabs.\n", encoding="utf-8")
        code, _, err = self.completion("D00 T01 §2", "--context", context)
        self.assertEqual(code, 0, err)
        self.assertIn("SPEC chapter 3, inlined: the ribbon has four tabs.", self.out.read_text(encoding="utf-8"))

    def test_surface_and_implements_lines_need_context_too(self):
        for line, why in (("**Surface:** yes", "Surface"), ("> **Implements:** INV-1", "Implements")):
            with self.subTest(line=line):
                rows = {"D00 T01 §1": mock.Mock(body=f"Context.\n\n{line}\n", number=1, title="T", path="x")}
                with mock.patch.object(review_prompt, "section_row", return_value=("D00 T01 §1", rows["D00 T01 §1"])):
                    err = self.refused("completion", "D00 T01 §1", "--purpose", "p", "--no-context", "none",
                                       "--out", self.out, reason="needs --context")
                self.assertIn(why, err)

    def test_an_output_that_cannot_be_replaced_is_a_refusal_not_a_crash(self):
        # Review round 1: a prompt left open in an editor makes the replace fail on Windows.
        with mock.patch.object(tg.os, "replace", side_effect=PermissionError(13, "Access is denied")):
            err = self.refused("completion", "D00 T01 §1", "--purpose", "p", "--no-context", "tooling",
                               "--out", self.out, reason="cannot write --out")
        self.assertIn("Access is denied", err)
        self.assertEqual([p.name for p in self.scratch.iterdir()], [self.out.name])  # no temporary file left

    def test_angle_brackets_in_a_section_are_written_through(self):
        code, _, err = self.completion("D00 T01 §3", "--no-context", "tooling")
        self.assertEqual(code, 0, err)
        prompt = self.out.read_text(encoding="utf-8")
        self.assertIn("A body may hold `<x>`, `<one or two sentences>` and ```` fences.", prompt)
        self.assertIn("\n`````markdown\n## 3. Angles", prompt)  # a fence longer than the one in the body


class Templates(Base):
    def test_the_real_templates_are_accepted(self):
        for kind in review_prompt.TEMPLATES:
            with self.subTest(kind=kind):
                self.assertTrue(review_prompt.template(REPO, kind))

    def change(self, kind, old, new):
        path = self.root / review_prompt.TEMPLATES[kind]
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def test_an_added_placeholder_is_refused(self):
        self.change("completion", "## Context to read", "- Budget: `<the performance budget>`.\n\n## Context to read")
        err = self.refused("completion", "D00 T01 §1", "--purpose", "p", "--no-context", "none", "--out", self.out,
                           reason="docs/completion-review-prompt.md changed")
        self.assertIn("<the performance budget>", err)

    def test_a_removed_placeholder_is_refused(self):
        self.change("completion", "- What the feature is for the user: `<one or two sentences>`.\n", "")
        self.refused("completion", "D00 T01 §1", "--purpose", "p", "--no-context", "none", "--out", self.out,
                     reason="docs/completion-review-prompt.md changed")

    def test_a_reworded_reply_format_is_refused(self):
        self.change("completion", "`SECTION: <DNN TNN §N>`", "`SECTION: <ref>`")
        self.refused("completion", "D00 T01 §1", "--purpose", "p", "--no-context", "none", "--out", self.out,
                     reason="'SECTION: <ref>'")

    def test_a_template_without_its_rule_line_is_refused(self):
        self.change("round", "\n---\n", "\n")
        with self.assertRaises(review_prompt.Refused):
            review_prompt.template(self.root, "round")


class Round(Base):
    """A repository with three commits of different trees on main and a side branch from the first."""

    def setUp(self):
        super().setUp()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        self.git("config", "core.autocrlf", "false")
        self.first = self.commit({"tool.py": "print(1)\n", "test_tool.py": "assert True\n"}, "first")
        self.second = self.commit({"tool.py": "print(2)\n", "test_tool.py": "assert 2\n"}, "second")
        self.third = self.commit({"tool.py": "print(3)\n"}, "third")
        self.git("checkout", "-q", "-b", "side", self.first)
        self.side = self.commit({"other.py": "print('side')\n"}, "side")
        self.git("checkout", "-q", "main")

    def git(self, *args):
        done = subprocess.run([tg.git(), *args], cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout.strip()

    def commit(self, files, message):
        for name, text in files.items():
            (self.root / name).write_text(text, encoding="utf-8", newline="\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def round(self, base, tip, *extra):
        return self.run_main("round", "D00 T01 §1", base, tip, "--purpose", "It prints.", "--governing", "`AGENTS.md`",
                             *extra, "--out", self.out)

    def args(self, base, tip, *extra):
        return ("round", "D00 T01 §1", base, tip, "--purpose", "p", "--governing", "g", *extra, "--out", self.out)

    def test_a_forward_range_gives_both_shas_the_section_and_the_diff(self):
        code, out, err = self.round(self.first[:10], "HEAD")
        self.assertEqual(code, 0, err)
        prompt = self.out.read_text(encoding="utf-8")
        self.assertEqual(json.loads(out), {"kind": "round", "ref": "D00 T01 §1", "base": self.first, "tip": self.third,
                                           "included": ["test_tool.py", "tool.py"], "omitted": [],
                                           "out": str(self.out.resolve())})
        self.assertIn(f"- Commit or range: `{self.first}..{self.third}` (the diff is inlined below", prompt)
        self.assertIn("- What it is meant to do: It prints.", prompt)
        self.assertIn("- TODO section, when there is one: `D00 T01 §1` (its contract is inlined below", prompt)
        self.assertIn("- Governing documents: `AGENTS.md` and `AGENTS.md`.", prompt)
        self.assertIn('"title": "Tooling"', prompt)
        self.assertIn("-print(1)\n+print(3)", prompt)
        self.assertIn("-assert True\n+assert 2", prompt)
        self.assertNotIn("Not in this prompt", prompt)
        self.assertTrue(prompt.startswith("You are an independent, adversarial code reviewer."), prompt[:80])
        for filled, _ in review_prompt.FILLS["round"]:
            self.assertNotIn(filled, prompt)

    def test_a_note_is_carried(self):
        note = self.scratch / "note.md"
        note.write_text("This is round 2; round 1 found `<x>`.\n", encoding="utf-8")
        code, _, err = self.round(self.first, self.third, "--note", note)
        self.assertEqual(code, 0, err)
        self.assertIn("## Note from the writer\n\nThis is round 2; round 1 found `<x>`.", self.out.read_text("utf-8"))

    def test_a_round_output_that_cannot_be_replaced_is_a_refusal_not_a_crash(self):
        with mock.patch.object(tg.os, "replace", side_effect=PermissionError(13, "Access is denied")):
            self.refused(*self.args(self.first, self.third), reason="cannot write --out")
        self.assertEqual([p.name for p in self.scratch.iterdir()], [self.out.name])

    def test_a_reversed_range_is_refused(self):
        self.refused(*self.args(self.third, self.first), reason="the range is reversed")

    def test_a_divergent_range_is_refused(self):
        self.refused(*self.args(self.second, self.side), reason="the range is divergent")

    def test_an_equal_range_is_refused(self):
        self.refused(*self.args("HEAD", self.third), reason="the base and the tip are the same commit")

    def test_a_part_names_what_it_leaves_out(self):
        code, out, err = self.round(self.first, self.second, "--path", "test_tool.py")
        self.assertEqual(code, 0, err)
        prompt = self.out.read_text(encoding="utf-8")
        summary = json.loads(out)
        self.assertEqual((summary["included"], summary["omitted"]), (["test_tool.py"], ["tool.py"]))
        scope = prompt[prompt.index("## Scope"):prompt.index("## Section contract")]
        self.assertIn("changes 2 path(s)", scope)
        self.assertIn("Included in this prompt:\n\n- `test_tool.py`", scope)
        self.assertIn("Not in this prompt (review them in another round part):\n\n- `tool.py`", scope)
        self.assertIn("This prompt covers only the included paths.", scope)
        diff = prompt[prompt.index("## Diff"):]
        self.assertIn("+assert 2", diff)
        self.assertNotIn("print(2)", diff)

    def test_the_inlined_diff_is_bounded_whole_and_in_part(self):
        big = "".join(f"line {n}\n" for n in range(400))
        tip = self.commit({"tool.py": big, "test_tool.py": "assert 3\n"}, "big")
        with mock.patch.object(review_prompt, "MAX_DIFF_BYTES", 1000):
            err = self.refused(*self.args(self.third, tip), reason="over the limit of 1000")
            self.assertIn("--path", err)
            self.refused(*self.args(self.third, tip, "--path", "tool.py"), reason="over the limit of 1000")
            self.out.unlink()
            code, out, err = self.round(self.third, tip, "--path", "test_tool.py")
            self.assertEqual(code, 0, err)
            self.assertEqual(json.loads(out)["omitted"], ["tool.py"])
            self.assertIn("+assert 3", self.out.read_text(encoding="utf-8"))

    def test_an_unknown_section_is_refused(self):
        self.refused("round", "D00 T01 §9", self.first, self.third, "--purpose", "p", "--governing", "g",
                     "--out", self.out, reason="no such section: D00 T01 §9")
        self.refused("round", "the ribbon", self.first, self.third, "--purpose", "p", "--governing", "g",
                     "--out", self.out, reason="no section reference")

    def test_an_unknown_commit_is_refused(self):
        self.refused(*self.args("0" * 40, self.third), reason="git does not know the commit")
        self.refused(*self.args(self.first, "no-such-branch"), reason="git does not know the commit 'no-such-branch'")

    def test_an_option_shaped_commit_is_not_run_as_an_option(self):
        # argparse refuses a positional that starts with a dash; the function itself must not hand one to git either.
        with self.assertRaises(SystemExit) as caught, contextlib.redirect_stderr(io.StringIO()):
            review_prompt.main([str(a) for a in self.args(self.first, "--output=x")], root=self.root)
        self.assertEqual(caught.exception.code, 2)
        with self.assertRaises(review_prompt.Refused) as refused:
            review_prompt.commit(self.root, "--output=x")
        self.assertIn("git does not know the commit", str(refused.exception))
        self.assertFalse((self.root / "x").exists())

    def test_out_inside_the_repository_is_refused(self):
        for inside in (self.root / "prompt.md", self.root / "docs" / "p.md"):
            with self.subTest(inside=inside.name):
                code, out, err = self.run_main("round", "D00 T01 §1", self.first, self.third, "--purpose", "p",
                                               "--governing", "g", "--out", inside)
                self.assertEqual((code, out), (2, ""))
                self.assertIn("is inside the repository", err)
                self.assertFalse(inside.exists())
        code, out, err = self.run_main("completion", "D00 T01 §1", "--purpose", "p", "--no-context", "none",
                                       "--out", self.root / "c.md")
        self.assertEqual((code, out), (2, ""))
        self.assertFalse((self.root / "c.md").exists())


class CommandLine(unittest.TestCase):
    def test_the_real_command_refuses_an_equal_range(self):
        with tempfile.TemporaryDirectory() as scratch:
            out = Path(scratch) / "p.md"
            done = subprocess.run([sys.executable, str(SCRIPTS / "review-prompt.py"), "round", "D00 T03 §27", "HEAD",
                                   "HEAD", "--purpose", "x", "--governing", "y", "--out", str(out)],
                                  cwd=REPO, capture_output=True, text=True, encoding="utf-8", timeout=120)
            self.assertEqual(done.returncode, 2, done.stderr)
            self.assertIn("the base and the tip are the same commit", done.stderr)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
