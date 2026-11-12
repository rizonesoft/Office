# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/lessons.py and scripts/lessons.py check (D00 T05 §1): a lesson is read exactly, and every rule of
docs/lessons/README.md refuses what breaks it. Each test builds its own small git repository in a temporary folder."""
import contextlib
import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS / "lib"))
import lessons

spec = importlib.util.spec_from_file_location("lessons_cli", SCRIPTS / "lessons.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)

RECORD = "docs/reviews/00-workspace/D99-T01-s1.md"
RECORD_TEXT = """## Plan review: astra (`gpt-6-astra` via `codex`)

1. **P2:** a plan finding.

OVERALL: needs-attention

## Round 1: astra (`gpt-6-astra` via `codex`)

## adversarial: needs-attention

1. **P1, `scripts/a.py:3`:** the first finding.
2. **P2:** the second finding.

OVERALL: needs-attention

## Re-think

1. A writer's numbered note, not a finding.
2. Another.
3. And a third.

## Round 2: astra (`gpt-6-astra` via `codex`)

1. **P3:** a later one.

OVERALL: approve
"""
SPEC_TEXT = "# Spec\n\n## Decisions\n\n1. **First:** one.\n2. **Second:** two.\n"


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60, check=True).stdout


class Store(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)
        files = {"docs/lessons/README.md": (ROOT / "docs" / "lessons" / "README.md").read_text(encoding="utf-8"),
                 RECORD: RECORD_TEXT, cli.SPEC: SPEC_TEXT, "scripts/a.py": "x = 1\n", "scripts/lib/b.py": "y = 2\n"}
        for name, text in files.items():
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_text(text, encoding="utf-8")
        git(self.root, "init", "-q")
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "add", "-A")
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "base")
        self.fix = git(self.root, "rev-parse", "HEAD").strip()
        self.folder = self.root / "docs" / "lessons"

    def fields(self, **changes):
        base = {"id": "keep-gates-whole", "applies": "scripts/*.py", "topics": "tests, tooling", "roles": "main",
                "source": f"{RECORD}#round-1/finding-2", "fix": self.fix, "added": "2026-11-12", "status": "active"}
        base.update(changes)
        return {k: v for k, v in base.items() if v is not None}

    def write(self, body="A gate that is missing must never count as passing; require every gate by name.", name=None,
              raw=None, **changes):
        fields = self.fields(**changes)
        name = name or fields.get("id", "keep-gates-whole")
        text = raw if raw is not None else "---\n" + "".join(f"{k}: {v}\n" for k, v in fields.items()) + "---\n" + body + "\n"
        (self.folder / f"{name}.md").write_text(text, encoding="utf-8")
        return self.folder / f"{name}.md"

    def check(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cli.main(["check"], root=self.root)
        return code, out.getvalue()

    def refused(self, fragment, **kwargs):
        self.write(**kwargs)
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn(fragment, out)
        return out


class Reader(Store):
    def test_every_field_and_the_body_are_read_exactly(self):
        path = self.write(body="Line one of the paragraph,\ncontinued on a second line.")
        lesson = lessons.read(path)
        self.assertEqual(lesson, {**self.fields(), "body": "Line one of the paragraph,\ncontinued on a second line."})

    def test_each_unreadable_shape_is_refused_naming_the_file_and_key(self):
        cases = {
            "unknown key 'colour'": "---\nid: x\ncolour: red\n---\nb\n",
            "duplicate key 'id'": "---\nid: x\nid: x\n---\nb\n",
            "missing key 'source'": "---\nid: x\napplies: *\ntopics: tests\nroles: all\nadded: 2026-11-12\nstatus: active\n---\nb\n",
            "differs from the file name": "---\nid: y\napplies: *\ntopics: tests\nroles: all\nsource: decision-1\n"
                                          "added: 2026-11-12\nstatus: active\n---\nb\n",
            "no frontmatter": "id: x\n",
            "not closed": "---\nid: x\n",
            "not a flat key: value line": "---\n  nested: x\n---\nb\n",
        }
        for fragment, raw in cases.items():
            with self.subTest(fragment):
                path = self.folder / "x.md"
                path.write_text(raw, encoding="utf-8")
                with self.assertRaises(lessons.LessonError) as caught:
                    lessons.read(path)
                self.assertIn("x.md", str(caught.exception))
                self.assertIn(fragment, str(caught.exception))

    def test_the_topics_are_the_readme_list(self):
        words = lessons.topics(self.folder / "README.md")
        self.assertIn("tests", words)
        self.assertIn("windows", words)
        self.assertNotIn("Topics", words)


class Accepted(Store):
    def test_both_source_forms_pass(self):
        self.write()
        self.write(name="owner-said-so", id="owner-said-so", source="decision-2", fix=None, roles="all", applies="*")
        code, out = self.check()
        self.assertEqual((code, out.strip()), (0, "2 lesson(s), all valid"))

    def test_a_mixed_folder_reads_only_the_lessons(self):
        self.write()
        (self.folder / "triage").mkdir()
        (self.folder / "triage" / "candidate.md").write_text("not a lesson at all\n", encoding="utf-8")
        code, out = self.check()
        self.assertEqual((code, out.strip()), (0, "1 lesson(s), all valid"))
        self.assertEqual([p.name for p in lessons.lesson_files(self.folder)], ["keep-gates-whole.md"])

    def test_the_repository_store_passes(self):
        self.assertEqual(cli.main(["check"]), 0)


class Values(Store):
    def test_each_bad_value_is_refused_naming_the_lesson_and_key(self):
        cases = [
            ({"topics": ""}, "empty value: topics is empty"),
            ({"id": "Keep_Gates", "name": "Keep_Gates"}, "id: 'Keep_Gates' is not kebab-case"),
            ({"status": "draft"}, "status: 'draft' is neither active nor retired"),
            ({"added": "12/11/2026"}, "added: '12/11/2026' is not a YYYY-MM-DD date"),
            ({"added": "2026-02-30"}, "added: '2026-02-30' is not a YYYY-MM-DD date"),
            ({"status": "retired", "retired_by": ""}, "empty value: retired_by is empty"),
            ({"status": "retired"}, "retired_by: a retired lesson names what now enforces it"),
            ({"body": ""}, "body: the body is empty"),
            ({"body": "First paragraph.\n\nSecond paragraph."}, "body: the body is more than one paragraph"),
            ({"body": "x" * 601}, "body length: 601 characters, more than 600"),
            ({"body": "Use a comma — not this."}, "dash: an em dash"),
            ({"body": "Pages 1–2."}, "dash: an en dash"),
            ({"topics": "tests, gardening"}, "topics: 'gardening' is not in the README's Topics list"),
            ({"roles": "section-writer"}, "roles: 'section-writer' is not all, main or reader"),
            ({"roles": "principal-implementer"}, "roles: 'principal-implementer' is not all, main or reader"),
            ({"roles": "all, main"}, "roles: all stands alone"),
        ]
        for changes, fragment in cases:
            with self.subTest(fragment):
                for old in self.folder.glob("*.md"):
                    if old.name != "README.md":
                        old.unlink()
                lesson_id = changes.get("id", "keep-gates-whole")
                out = self.refused(fragment, **changes)
                self.assertIn(f"{lesson_id}: ", out)

    def test_reader_roles_pass(self):
        self.write(roles="main, reader")
        self.assertEqual(self.check()[0], 0)


class Sources(Store):
    def test_review_source_refusals(self):
        other = git(self.root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q",
                    "--allow-empty", "-m", "off history")
        off = git(self.root, "rev-parse", "HEAD").strip()
        git(self.root, "reset", "-q", "--hard", "HEAD~1")
        del other
        cases = [
            ({"source": "docs/reviews/00-workspace/missing.md#round-1/finding-1"}, "is not a review record"),
            ({"source": "docs/lessons/README.md#round-1/finding-1"}, "is not a review record"),
            ({"source": f"{RECORD}#round-3/finding-1"}, "has no ## Round 3 heading"),
            ({"source": f"{RECORD}#round-1/finding-3"}, "round 1 of"),
            ({"fix": None}, "fix: a review source names the commit"),
            ({"fix": "deadbeefdeadbeef"}, "is not a commit in the history of HEAD"),
            ({"fix": "main"}, "is not a commit in the history of HEAD"),
            ({"fix": off}, "is not a commit in the history of HEAD"),
            ({"source": f"{RECORD}#round-1"}, "is neither <record>#round-N/finding-K nor decision-<N>"),
            ({"source": "owner:2026-11-12", "fix": None}, "is neither"),
            ({"source": "decision-9", "fix": None}, "has no decision 9"),
            ({"source": "decision-1"}, "only a review source takes a fix commit"),
        ]
        for changes, fragment in cases:
            with self.subTest(fragment):
                self.refused(fragment, **changes)

    def test_a_plan_review_finding_is_not_a_round_finding(self):
        # Round 2 has only finding 1; the plan review's finding 1 above round 1 does not count for round 1's 3.
        self.write(source=f"{RECORD}#round-2/finding-1")
        self.assertEqual(self.check()[0], 0)
        self.refused("round 2 of", source=f"{RECORD}#round-2/finding-2")


class RoundFixes(Store):
    """Round 1 of D00 T05 §1's review."""

    def test_a_list_that_names_nothing_is_refused(self):
        for key in ("applies", "topics", "roles"):
            with self.subTest(key):
                self.refused(f"empty value: {key} names nothing", **{key: ", ,"})

    def test_a_huge_number_is_a_refusal_not_a_crash(self):
        self.write(name="huge", id="huge", source="decision-" + "9" * 4301, fix=None)
        self.write()
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("huge: source:", out)
        self.assertIn("2 lesson(s), 1 problem(s)", out)
        self.refused("is neither", source=f"{RECORD}#round-1/finding-" + "1" * 50)

    def test_a_lens_heading_stays_in_its_round_and_a_writer_heading_does_not(self):
        self.write(source=f"{RECORD}#round-1/finding-1")  # under `## adversarial`, a level-2 lens heading
        self.assertEqual(self.check()[0], 0)
        self.refused("round 1 of", source=f"{RECORD}#round-1/finding-3")  # only the Re-think has a 3

    def test_a_real_record_of_this_repository_is_read(self):
        record = ROOT / "docs" / "reviews" / "00-workspace" / "D00-T03-s15.md"
        text = record.read_text(encoding="utf-8")
        self.assertIn("\n## adversarial", text)  # the older shape, lens headings at level 2
        self.assertTrue(cli.finding_in(text, "1", "1"))
        self.assertTrue(cli.finding_in(text, "2", "1"))


class Globs(Store):
    def test_a_glob_matching_nothing_is_refused_unless_retired(self):
        self.refused("applies: 'src/**/*.cpp' matches no file the repository holds", applies="src/**/*.cpp")
        self.write(applies="src/**/*.cpp", status="retired", retired_by="scripts/a.py")
        self.assertEqual(self.check()[0], 0)

    def test_star_and_double_star(self):
        self.write(applies="scripts/**/*.py, *")
        self.assertEqual(self.check()[0], 0)
        self.refused("'scripts/*.cpp' matches no file", applies="scripts/*.cpp")

    def test_an_unstaged_deletion_and_a_committed_deletion_are_both_gone(self):
        (self.root / "scripts" / "a.py").unlink()  # still in the index
        self.refused("'scripts/a.py' matches no file", applies="scripts/a.py")
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-am", "drop a")
        self.refused("'scripts/a.py' matches no file", applies="scripts/a.py")


class WholeRun(Store):
    def test_every_problem_in_one_run_and_duplicate_ids(self):
        self.write(name="first", id="first", topics="gardening", body="x" * 700)
        self.write(name="second", raw="---\nid: second\napplies: *\ntopics: tests\nroles: all\nadded: 2026-11-12\n"
                                       "status: active\n---\nb\n")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("first: topics:", out)
        self.assertIn("first: body length:", out)
        self.assertIn("second.md: missing key 'source'", out)
        self.assertIn("2 lesson(s), 3 problem(s)", out)

    def test_every_structural_fault_of_one_file_in_one_run(self):
        # Completion review: a file with an unknown key, a duplicate, a bad line, two missing keys and a wrong id.
        self.write(name="many", raw="---\nid: other\ncolour: red\nid: again\n  nested\napplies: *\ntopics: tests\n"
                                     "roles: all\nstatus: active\n---\nb\n")
        code, out = self.check()
        self.assertEqual(code, 1)
        for fragment in ("unknown key 'colour'", "duplicate key 'id'", "line 5 is not a flat key: value line",
                         "missing key 'source'", "missing key 'added'", "id 'other' differs from the file name 'many'"):
            self.assertIn(f"many.md: {fragment}", out)
        self.assertIn("1 lesson(s), 6 problem(s)", out)

    def test_two_files_with_one_id(self):
        self.write(name="same", id="same")
        self.write(name="Same2", raw=(self.folder / "same.md").read_text(encoding="utf-8"))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("differs from the file name", out)


if __name__ == "__main__":
    unittest.main()
