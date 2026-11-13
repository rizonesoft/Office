# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/review-prompt.py: fills the four prompt templates in docs/, refuses what it cannot fill, and writes
atomically. Every test runs the script from a scratch project that holds copies of it and of the templates."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
import unittest.mock

# The scratch repository, the dispatcher and the fake reviewer CLIs; unittest discovery puts this folder on sys.path.
from test_review_dispatch import Harness

SCRIPTS = Path(__file__).resolve().parents[1]
DOCS = SCRIPTS.parent / "docs"
TEMPLATES = ("plan-review-prompt.md", "review-round-prompt.md", "completion-review-prompt.md",
             "reconciliation-review-prompt.md")
KINDS = ("plan", "round", "completion", "reconciliation")
CAND = "0123456789abcdef0123456789abcdef01234567"
BASE = "89abcdef0123456789abcdef0123456789abcdef"
FAILED = "fedcba9876543210fedcba9876543210fedcba98"
LAST = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
REF = "D00 T01 §7"
TODO = "todo/00-reviewer/TODO-01-three-pass-review.md"
PLACEHOLDER = re.compile(r"`<[^`\n]*>`")
# The final verdict each kind's reply format must still carry after filling.
VERDICT = {"plan": ["PLAN: complete", "OVERALL: approve"], "round": ["OVERALL: approve"],
           "completion": ["COMPLETION: complete"], "reconciliation": ["RECONCILIATION: complete"]}
# The values every kind needs besides the candidate.
COMMON = {"plan": ["--governing", "docs/plan.md"],
          "round": ["--purpose", "Fill review prompts.", "--governing", "docs/plan.md"],
          "completion": ["--purpose", "Fill review prompts.", "--governing", "docs/plan.md"],
          "reconciliation": ["--failed", FAILED, "--findings", "docs/reviews/00-reviewer/D00-T01-s7.md",
                             "--governing", "docs/plan.md"]}


def install(root: Path, graph=None):
    """A scratch project: scripts/review-prompt.py beside docs/<templates>, and a stand-in todo-graph.py if given."""
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "docs").mkdir(exist_ok=True)
    shutil.copy(SCRIPTS / "review-prompt.py", root / "scripts" / "review-prompt.py")
    for name in TEMPLATES:
        shutil.copy(DOCS / name, root / "docs" / name)
    if graph is not None:
        (root / "scripts" / "todo-graph.py").write_text(graph, encoding="utf-8")


class Filler(unittest.TestCase):
    graph = None

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "project"
        install(self.root, self.graph)
        self.out = Path(self._tmp.name) / "out" / "prompt.md"
        self.out.parent.mkdir()
        self.gates = Path(self._tmp.name) / "gates.txt"
        self.gates.write_text("python -m unittest: OK (12 tests)\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def run_filler(self, args):
        return subprocess.run([sys.executable, "-B", str(self.root / "scripts/review-prompt.py"), *args],
                              capture_output=True, text=True, timeout=60, cwd=self.root, encoding="utf-8",
                              env={**os.environ, "PYTHONIOENCODING": "utf-8"})

    def fill(self, kind, *extra, out=None, common=True):
        args = ["--kind", kind, "--candidate", CAND, "--out", str(out or self.out)]
        if common:
            args += COMMON[kind]
            if kind == "reconciliation":
                args += ["--gates", str(self.gates)]
        return self.run_filler(args + list(extra))

    def ok(self, kind, *extra, **kwargs):
        done = self.fill(kind, *extra, **kwargs)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(Path(done.stdout.strip()), self.out)
        return self.out.read_text(encoding="utf-8")

    def refused(self, kind, needle, *extra, **kwargs):
        """The run exits 2 naming `needle`, prints nothing, and leaves an earlier output byte for byte."""
        self.out.write_bytes(b"EARLIER OUTPUT\n")
        done = self.fill(kind, *extra, **kwargs)
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn(needle, done.stderr)
        self.assertEqual(done.stdout, "")
        self.assertEqual(self.out.read_bytes(), b"EARLIER OUTPUT\n", "a refusal must leave the earlier output alone")
        self.assertEqual([p.name for p in self.out.parent.iterdir()], [self.out.name], "no temp file left behind")
        return done.stderr


class CommitItem(Filler):
    """D00 T03 §57: the completion and reconciliation prompts say the stamp ticks the Commit item."""

    SENTENCE = ("The section's `- [ ] Commit:` item is ticked by `stamp` when it writes the section's `Verified:` "
                "line, so an unticked Commit item whose commit exists is never a gap.")

    def test_the_completion_and_reconciliation_prompts_say_it(self):
        for kind in ("completion", "reconciliation"):
            with self.subTest(kind):
                self.assertIn(self.SENTENCE, self.ok(kind))


class OwnerDecision(Filler):
    """D00 T03 §61: a reconciliation closes an obligation the owner gave up, and only the owner can give one up."""

    CONDITIONS = (
        "the writer cannot narrow, reclassify or waive them to obtain approval",
        "Only the owner can decide between two of them that conflict",
        "cannot both be met in the same state",
        "a numbered, dated decision in the governing document named above",
        "which is the owner's record and not the writer's",
        "it identifies the gap, by naming this section, or the section filed to settle the gap (which names this one), "
        "or by saying plainly which behaviour is chosen",
        "is closed by the repair, shown by the `path:line` or test and the writer's `- Implemented:` line, with one "
        "exception: an obligation the owner gave up, which check 4 closes and nothing else does",
        "it was made after the failed completion review",
        "`- Decided: <gap> by owner decision <N> of <record>`",
        "Read the decision in the record itself",
        "The obligation the owner kept is checked like any other",
        "`closed by owner decision <N>` when the candidate does exactly what the decision says",
        "no more of the given-up behaviour than the decision allows",
        "a test holds that behaviour; say which test",
        "A writer's note, a re-think, a filed section by itself, a decision that does not identify the gap in one of "
        "those ways, or one that predates the completion review, settles nothing: the gap stays open",
        "A decision never closes a gap the repair could have closed without giving anything up",
    )

    def test_the_reconciliation_prompt_carries_every_condition(self):
        text = " ".join(self.ok("reconciliation", "--ref", REF).split())
        for condition in self.CONDITIONS:
            self.assertIn(condition, text)
        self.assertNotIn("they cannot be narrowed, reclassified or waived", text)  # the rule now names who it binds
        self.assertNotIn("is closed only by the repair", text)  # no unconditional rule left to contradict check 4

    def test_the_decision_this_rule_was_written_for_qualifies(self):
        # Decision 46 chose the digest's behaviour and names D00 T03 §56, the section filed to settle the gap of
        # D00 T03 §53's reconciliations; §56 names §53. That is the second way the prompt lets a decision identify a gap.
        record = (DOCS / "specs" / "2026-10-23-campaign-scope-design.md").read_text(encoding="utf-8")
        decision = next(line for line in record.splitlines() if line.startswith("46. "))
        self.assertIn("(2026-11-13)", decision)
        self.assertIn("The weekly digest repeats, labelled, the notices of a digest whose delivery no record can show "
                      "(D00 T03 §56)", decision)
        todo = (SCRIPTS.parent / "todo/00-workspace/TODO-03-automations-and-keep-alive.md").read_text(encoding="utf-8")
        settled_by = todo.split("\n## 56. ", 1)[1].split("\n## ", 1)[0]
        self.assertIn("from the review of §53", settled_by)
        self.assertIn("**Owner's choice, 2026-11-13", settled_by)

    def test_no_other_prompt_lets_an_owner_decision_close_anything(self):
        for name in TEMPLATES[:3]:  # the plan review, the round and the completion review
            self.assertNotIn("owner decision", (DOCS / name).read_text(encoding="utf-8"), name)

    def test_the_skill_names_the_line_and_who_decides(self):
        skill = (SCRIPTS.parent / ".claude" / "skills" / "review-todo-section" / "SKILL.md").read_text(encoding="utf-8")
        for phrase in ("`- Decided: <gap> by owner decision <N> of <record>`", "the choice is the owner's, never the writer's",
                       "file it as an `owner-decision` section and park this one on it",
                       "The line is never written for a gap the repair can close"):
            self.assertIn(phrase, skill)


class FillEachKind(Filler):
    def test_every_kind_fills_with_no_placeholder_left(self):
        for kind in KINDS:
            with self.subTest(kind):
                extra = ["--ref", REF] + (["--todo", TODO] if kind in ("plan", "completion") else [])
                text = self.ok(kind, *extra)
                self.assertEqual(PLACEHOLDER.findall(text), [])
                self.assertNotIn("<DNN TNN", text)
                self.assertTrue(text.startswith("You are an independent"), "only the prompt after `---` is written")
                self.assertIn("## Reply format", text)
                for verdict in VERDICT[kind]:
                    self.assertIn(verdict, text)
                self.assertTrue(text.endswith("\n") and not text.endswith("\n\n"))

    def test_saved_file_is_the_prompt_and_values_appear(self):
        text = self.ok("completion", "--ref", REF, "--todo", TODO, "--fidelity", "design/main-window.png")
        self.assertEqual(self.out.read_text(encoding="utf-8"), text)
        self.assertIn(f"- Commit or range: `{CAND}` (inspect", text)
        self.assertIn(f"- TODO section: `{REF}` (its contract: `python3 scripts/todo-graph.py resolve \"{REF}\"`)", text)
        self.assertIn(f"`{TODO}`", text)
        self.assertIn("- Fidelity: `design/main-window.png`.", text)
        self.assertNotIn("none (Surface: no)", text)
        self.assertIn("- What the feature is for: Fill review prompts.", text)
        self.assertIn("`AGENTS.md` and `docs/plan.md`", text)

    def test_fidelity_defaults_to_no_surface(self):
        self.assertIn("- Fidelity: `none (Surface: no)`.", self.ok("plan", "--ref", REF, "--todo", TODO))

    def test_single_commit_versus_range(self):
        single = self.ok("round", "--ref", REF)
        self.assertIn(f"- Commit or range: `{CAND}` (inspect", single)
        self.assertNotIn(BASE, single)
        ranged = self.ok("round", "--ref", REF, "--base", BASE)
        self.assertIn(f"- Commit or range: `{BASE}..{CAND}`, tip `{CAND}` (inspect", ranged)

    def test_reconciliation_names_failed_and_last_in_their_places(self):
        same = self.ok("reconciliation", "--ref", REF)
        self.assertIn(f"- The failed completion's candidate: `{FAILED}`.", same)
        self.assertIn(f"(the failed completion's, or the last reconciliation's): `{FAILED}`.", same)
        self.assertIn(f"The repair is `{FAILED}..{CAND}`, read all of it, with `{FAILED}..{CAND}` the newest part",
                      same)
        second = self.ok("reconciliation", "--ref", REF, "--last", LAST)
        self.assertIn(f"- The failed completion's candidate: `{FAILED}`.", second)
        self.assertIn(f"or the last reconciliation's): `{LAST}`.", second)
        self.assertIn(f"- The repaired candidate: `{CAND}`. The repair is `{FAILED}..{CAND}`", second)
        self.assertIn(f"with `{LAST}..{CAND}` the newest part", second)
        self.assertIn("`docs/reviews/00-reviewer/D00-T01-s7.md`", second)
        self.assertIn("- Gate results on the repaired candidate: `python -m unittest: OK (12 tests)`.", second)
        self.assertEqual(PLACEHOLDER.findall(second), [])

    def test_multiline_gate_output_goes_in_a_fence_and_is_not_rescanned(self):
        self.gates.write_text("ran 3 checks\nOK `<not a placeholder>`\n", encoding="utf-8")
        text = self.ok("reconciliation", "--ref", REF)
        self.assertIn("- Gate results on the repaired candidate:\n\n```\nran 3 checks\nOK `<not a placeholder>`\n```\n\n"
                      "- Governing", text)

    def test_supplied_text_is_never_taken_for_the_gate_placeholder(self):
        # Round of D00 T01 §7: a purpose holding the filler's own gate marker crashed it, and with gate output present
        # the supplied text was replaced by that output.
        text = self.ok("round", "--purpose", "Handle @@GATES@@ in supplied text", common=False,
                       *(["--governing", "docs/plan.md"]))
        self.assertIn("Handle @@GATES@@ in supplied text", text)
        self.gates.write_text("true -> exit 0\n", encoding="utf-8")
        text = self.ok("reconciliation", "--ref", REF, "--governing", "docs/@@GATES@@.md", common=False,
                       *(["--failed", CAND, "--findings", "docs/reviews/x.md", "--gates", str(self.gates)]))
        self.assertIn("docs/@@GATES@@.md", text)
        self.assertEqual(text.count("true -> exit 0"), 1)
        self.assertNotIn("\0", text)

    def test_lens_verdict_text_is_left_alone(self):
        self.assertIn("`LENS <name>: clean`", self.ok("reconciliation", "--ref", REF))

    def test_round_without_ref_drops_the_todo_line_and_nothing_else(self):
        with_ref = self.ok("round", "--ref", REF).splitlines()
        text = self.ok("round")
        self.assertNotIn("- TODO section", text)
        self.assertNotIn("todo-graph", text)
        self.assertEqual(PLACEHOLDER.findall(text), [])
        self.assertEqual([line for line in with_ref if "todo-graph" not in line], text.splitlines())

    def test_plan_and_completion_without_ref_drop_the_section_and_file_lines(self):
        for kind in ("plan", "completion"):
            with self.subTest(kind):
                text = self.ok(kind)
                self.assertNotIn("- TODO section", text)
                self.assertNotIn("- The TODO file", text)
                self.assertEqual(PLACEHOLDER.findall(text), [])
                self.assertIn("- Fidelity:", text)

    def test_todo_without_ref_keeps_the_file_line(self):
        text = self.ok("plan", "--todo", TODO)
        self.assertIn(f"`{TODO}`", text)
        self.assertNotIn("- TODO section", text)


class Refusals(Filler):
    def test_missing_value_names_the_placeholder_and_its_option(self):
        cases = [("round", ["--governing", "x"], "`<one or two sentences>`", "--purpose"),
                 ("round", ["--purpose", "x"], "`<the spec, plan or design file that applies>`", "--governing"),
                 ("completion", ["--governing", "x"], "`<one or two sentences: the user", "--purpose"),
                 ("plan", [], "`<the spec or plan that applies>`", "--governing"),
                 ("reconciliation", ["--governing", "x"], "`<docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md>`",
                  "--findings"),
                 ("reconciliation", ["--governing", "x", "--findings", "f.md"], "`<COMPLETION_SHA>`", "--failed"),
                 ("reconciliation", ["--governing", "x", "--findings", "f.md", "--failed", FAILED],
                  "`<quoted output>`", "--gates")]
        for kind, args, placeholder, flag in cases:
            with self.subTest(kind=kind, placeholder=placeholder):
                message = self.refused(kind, placeholder, *args, common=False)
                self.assertIn(f"(give {flag})", message)
                self.assertIn("no value for", message)

    def test_a_value_the_kind_has_no_place_for_is_refused(self):
        self.refused("plan", "no place for --purpose", "--purpose", "x")
        self.refused("plan", "no place for --base", "--base", BASE)
        self.refused("round", "no place for --gates", "--gates", str(self.gates))
        self.refused("reconciliation", "no place for --fidelity", "--ref", REF, "--fidelity", "x")

    def test_missing_template(self):
        (self.root / "docs" / "review-round-prompt.md").unlink()
        message = self.refused("round", "review-round-prompt.md")
        self.assertIn("cannot be read", message)

    def test_template_without_its_rule_line(self):
        (self.root / "docs" / "review-round-prompt.md").write_text("no rule here\n", encoding="utf-8")
        self.refused("round", "no `---` line")

    def test_bad_shas(self):
        for bad in ("abc123", CAND.upper(), CAND + "0", "g" * 40, ""):
            with self.subTest(bad=bad):
                done = self.run_filler(["--kind", "plan", "--candidate", bad, "--out", str(self.out),
                                        "--governing", "x"])
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn("40-character", done.stderr)
                self.assertFalse(self.out.exists())
        self.refused("round", "--base must be a full 40-character", "--base", "abc")
        self.refused("reconciliation", "--failed must be a full 40-character", "--failed", "abc")
        self.refused("round", "--ref must look like", "--ref", "section seven")

    def test_unreadable_or_empty_gates_file(self):
        missing = self.gates.parent / "nope.txt"
        message = self.refused("reconciliation", "cannot be read", "--failed", FAILED, "--findings", "f.md",
                               "--governing", "x", "--gates", str(missing), common=False)
        self.assertIn("nope.txt", message)
        self.gates.write_text("\n", encoding="utf-8")
        self.refused("reconciliation", "is empty", "--ref", REF)

    def test_an_unknown_placeholder_in_a_template_is_refused_by_name(self):
        # Completion review of D00 T01 §7: only known placeholders with missing values were tested.
        template = self.root / "docs" / "review-round-prompt.md"
        template.write_text(template.read_text(encoding="utf-8") + "\n- A new field: `<SOMETHING_NEW>`.\n",
                            encoding="utf-8")
        self.refused("round", "<SOMETHING_NEW>")

    def test_a_failed_temporary_write_or_replacement_leaves_the_earlier_output(self):
        # Completion review of D00 T01 §7: the earlier tests never reached the write or the replace of an existing
        # prompt. The script is loaded in this process so that one call of its own can be made to fail.
        spec = importlib.util.spec_from_file_location("review_prompt_under_test", self.root / "scripts/review-prompt.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        args = ["--kind", "round", "--candidate", CAND, "--out", str(self.out), *COMMON["round"]]
        real_fdopen = os.fdopen

        class FullDisk:
            """The temporary file opened for real, whose write stores a little and then fails."""
            def __init__(self, handle):
                self.handle = handle

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                self.handle.close()
                return False

            def write(self, text):
                self.handle.write(text[:20])
                self.handle.flush()
                raise full()

        def full():
            return OSError(28, "No space left on device")

        for label, call, effect in (("opening the temporary file", "fdopen", full()),
                                    ("writing the temporary file", "fdopen",
                                     lambda *a, **k: FullDisk(real_fdopen(*a, **k))),
                                    ("the replacement", "replace", full())):
            with self.subTest(label):
                self.out.write_bytes(b"EARLIER OUTPUT\n")
                errors, printed = io.StringIO(), io.StringIO()
                with unittest.mock.patch.object(module.os, call, side_effect=effect), \
                        contextlib.redirect_stderr(errors), contextlib.redirect_stdout(printed), \
                        unittest.mock.patch.object(module.os, "getcwd", return_value=str(self.root)):
                    code = module.main(args)
                self.assertEqual(code, 2, errors.getvalue())
                self.assertIn("cannot be written", errors.getvalue())
                self.assertIn("No space left on device", errors.getvalue())
                self.assertEqual(printed.getvalue(), "")
                self.assertEqual(self.out.read_bytes(), b"EARLIER OUTPUT\n")
                self.assertEqual([p.name for p in self.out.parent.iterdir()], [self.out.name], "a temp file was left")
        # With nothing failing the same call writes the prompt.
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(module.main(args), 0)
        self.assertIn(CAND, self.out.read_text(encoding="utf-8"))

    def test_output_whose_parent_is_a_file(self):
        blocker = self.out.parent / "blocker"
        blocker.write_text("a file", encoding="utf-8")
        done = self.fill("round", "--ref", REF, out=blocker / "prompt.md")
        self.assertEqual(done.returncode, 2, done.stderr)
        self.assertIn("cannot be written", done.stderr)
        self.assertEqual(blocker.read_text(encoding="utf-8"), "a file")
        self.assertEqual([p.name for p in self.out.parent.iterdir()], ["blocker"])

    def test_output_that_is_a_directory(self):
        folder = self.out.parent / "folder"
        folder.mkdir()
        done = self.fill("round", "--ref", REF, out=folder)
        self.assertEqual(done.returncode, 2, done.stderr)
        self.assertIn("cannot be written", done.stderr)
        self.assertTrue(folder.is_dir())

    def test_a_refusal_leaves_an_earlier_prompt_untouched(self):
        self.ok("round", "--ref", REF)
        earlier = self.out.read_bytes()
        done = self.fill("round", "--governing", "x", common=False)
        self.assertEqual(done.returncode, 2)
        self.assertEqual(self.out.read_bytes(), earlier)


class TodoLookup(Filler):
    graph = textwrap.dedent('''\
        import json, sys
        if sys.argv[1:] == ["resolve", "D00 T01 §7"]:
            print(json.dumps({"ref": "D00 T01 §7", "path": "todo/00-x/TODO-01-y.md", "exit": 3}))
            sys.exit(3)
        print(json.dumps({"error": "no such section"}))
        sys.exit(1)
        ''')

    def test_ref_without_todo_resolves_the_file_even_on_exit_3(self):
        text = self.ok("plan", "--ref", REF)
        self.assertIn("`todo/00-x/TODO-01-y.md`", text)
        self.assertEqual(PLACEHOLDER.findall(text), [])

    def test_explicit_todo_wins(self):
        self.assertIn("`other/TODO.md`", self.ok("plan", "--ref", REF, "--todo", "other/TODO.md"))

    def test_unresolvable_section_asks_for_todo(self):
        message = self.refused("plan", "--todo is needed", "--ref", "D09 T09 §9")
        self.assertIn("named no file", message)


class NoGraph(Filler):
    def test_no_lookup_script_asks_for_todo(self):
        message = self.refused("plan", "--todo is needed", "--ref", REF)
        self.assertIn("todo-graph.py is not beside", message)

    def test_round_needs_no_lookup(self):
        self.assertIn(f"`{REF}`", self.ok("round", "--ref", REF))


class ThroughTheDispatcher(Harness):
    def test_a_filled_round_prompt_reaches_the_reviewer(self):
        install(self.repo)
        filled = self.scratch / "round.md"
        done = subprocess.run([sys.executable, "-B", str(self.repo / "scripts/review-prompt.py"), "--kind", "round",
                               "--candidate", CAND, "--purpose", "Fill review prompts.", "--governing", "docs/plan.md",
                               "--out", str(filled)], capture_output=True, text=True, timeout=60, cwd=self.repo)
        self.assertEqual(done.returncode, 0, done.stderr)
        result, summary = self.dispatch("--writer", "claude", "--prompt", str(filled), cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIsNotNone(summary)
        sent = self.calls()[-1]["stdin"]
        self.assertIn(CAND, sent)
        self.assertEqual(sent, filled.read_text(encoding="utf-8"))
        self.assertEqual(PLACEHOLDER.findall(sent), [])


if __name__ == "__main__":
    unittest.main()
