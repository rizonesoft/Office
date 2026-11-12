# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/lessons.py and scripts/lessons.py check (D00 T05 §1): a lesson is read exactly, and every rule of
docs/lessons/README.md refuses what breaks it. Each test builds its own small git repository in a temporary folder."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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
# A second record with ten findings in one round, for tests that need many valid triage lines.
RECORD2 = "docs/reviews/00-workspace/D99-T02-s1.md"
RECORD2_TEXT = ("## Round 1: astra (`gpt-6-astra` via `codex`)\n\n"
                + "".join(f"{n}. **P2, `scripts/a.py:{n}`:** finding {n} of ten.\n" for n in range(1, 11))
                + "\nOVERALL: needs-attention\n")


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60, check=True).stdout


class Store(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)
        files = {"docs/lessons/README.md": (ROOT / "docs" / "lessons" / "README.md").read_text(encoding="utf-8"),
                 RECORD: RECORD_TEXT, RECORD2: RECORD2_TEXT, cli.SPEC: SPEC_TEXT, "scripts/a.py": "x = 1\n", "scripts/lib/b.py": "y = 2\n"}
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
        (self.folder / "triage" / "00-workspace").mkdir(parents=True)  # a triage file is never read as a lesson
        (self.folder / "triage" / "00-workspace" / "D99-T01-s1.md").write_text(
            "# Triage of D99 T01 §1\n\nround 1 finding 1: one-off, a typo\n", encoding="utf-8")
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
            ({"source": f"{RECORD}#round-1"}, "is neither <record>#round-N/finding-K (or #plan, #completion, "),
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


class Indexed(Store):
    """D00 T05 §2: the index and the query. Lessons here cite decision 1, so no commit is needed."""

    def lesson(self, lesson_id, applies="*", topics="tests", roles="main", added="2026-11-01", body=None,
               status="active", **more):
        return self.write(body=body or f"The body of {lesson_id} says what to do.", name=lesson_id, id=lesson_id,
                          applies=applies, topics=topics, roles=roles, added=added, status=status,
                          source="decision-1", fix=None, **more)

    def six(self):
        self.lesson("specific-file", applies="scripts/a.py", topics="tooling")
        self.lesson("whole-folder", applies="scripts/*.py", topics="tooling")
        self.lesson("everything", applies="*", topics="process")
        self.lesson("about-git", applies="scripts/lib/b.py", topics="git", body="Stage the plan before a commit.")
        self.lesson("for-readers", applies="scripts/lib/b.py", topics="review", roles="reader",
                    body="Quote the line a claim rests on.")
        self.lesson("retired-one", applies="scripts/a.py", topics="tooling", status="retired",
                    retired_by="scripts/a.py")

    def ids(self, **kwargs):
        shown, more = lessons.query(self.root, **kwargs)
        return [lesson["id"] for lesson in shown], more

    def cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(["query", *argv], root=self.root)
        return code, out.getvalue(), err.getvalue()

    def db(self):
        return self.root / "build" / "lessons.sqlite"

    def leftovers(self):
        return [p.name for p in (self.root / "build").iterdir() if p.name != "lessons.sqlite"]


class IndexBuild(Indexed):
    def test_one_row_per_active_lesson_and_no_leftover_file(self):
        self.six()
        self.assertEqual(lessons.build_index(self.root), 5)
        import sqlite3
        db = sqlite3.connect(self.db())
        try:
            rows = sorted(row[0] for row in db.execute("SELECT id FROM lessons"))
            globs = db.execute("SELECT COUNT(*) FROM globs").fetchone()[0]
            bodies = db.execute("SELECT COUNT(*) FROM bodies").fetchone()[0]
        finally:
            db.close()
        self.assertEqual(rows, ["about-git", "everything", "for-readers", "specific-file", "whole-folder"])
        self.assertEqual((globs, bodies), (5, 5))
        self.assertEqual(self.leftovers(), [])

    def test_a_changed_lesson_is_seen_by_the_next_query_with_no_build_call(self):
        self.six()
        self.assertEqual(self.ids(text="Stage")[0], ["about-git"])
        self.lesson("about-git", applies="scripts/lib/b.py", topics="git", body="Rebase before pushing, always.")
        self.assertEqual(self.ids(text="Stage")[0], [])
        self.assertEqual(self.ids(text="Rebase")[0], ["about-git"])

    def test_added_deleted_and_retired_lessons_change_the_next_query(self):
        self.six()
        self.assertEqual(self.ids(topics_asked=["tooling"])[0], ["specific-file", "whole-folder"])
        self.lesson("new-one", topics="tooling", added="2026-11-05")
        self.assertIn("new-one", self.ids(topics_asked=["tooling"])[0])
        (self.folder / "new-one.md").unlink()
        self.assertNotIn("new-one", self.ids(topics_asked=["tooling"])[0])
        self.lesson("whole-folder", applies="scripts/*.py", topics="tooling", status="retired",
                    retired_by="scripts/a.py")
        self.assertEqual(self.ids(topics_asked=["tooling"])[0], ["specific-file"])

    def test_a_missing_or_corrupt_database_is_rebuilt(self):
        self.six()
        self.ids(text="Stage")
        self.db().unlink()
        self.assertEqual(self.ids(text="Stage")[0], ["about-git"])
        self.db().write_bytes(b"this is not a database at all")
        self.assertEqual(self.ids(text="Stage")[0], ["about-git"])

    def test_a_failed_replace_keeps_the_earlier_database_and_leaves_no_file(self):
        self.six()
        self.ids(text="Stage")
        before = self.db().read_bytes()
        self.lesson("about-git", applies="scripts/lib/b.py", topics="git", body="Changed, so a rebuild is due.")
        with mock.patch.object(lessons.os, "replace", side_effect=OSError(13, "the file is in use")):
            with self.assertRaises(lessons.IndexError_):
                lessons.query(self.root, text="Changed")
            code, out, err = self.cli("--text", "Changed")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("the lesson index could not be written", err)
        self.assertEqual(self.db().read_bytes(), before)
        self.assertEqual(self.leftovers(), [])

    def test_a_failed_database_write_keeps_the_earlier_database_and_leaves_no_file(self):
        # Completion review: the commit of the new database fails, as on a full disk, before any replace.
        import sqlite3
        self.six()
        self.ids(text="Stage")
        before = self.db().read_bytes()
        self.lesson("about-git", applies="scripts/lib/b.py", topics="git", body="Changed, so a rebuild is due.")
        real = sqlite3.connect

        def full_disk(path, *args, **kwargs):
            connection = real(path, *args, **kwargs)
            if not str(path).endswith(".tmp"):
                return connection

            class Failing:
                def __getattr__(self, name):
                    return getattr(connection, name)

                def commit(self):
                    raise sqlite3.OperationalError("database or disk is full")
            return Failing()
        with mock.patch.object(lessons.sqlite3, "connect", side_effect=full_disk):
            with self.assertRaises(lessons.IndexError_) as caught:
                lessons.build_index(self.root)
            code, out, err = self.cli("--text", "Changed")
        self.assertIn("database or disk is full", str(caught.exception))
        self.assertEqual((code, out), (1, ""))
        self.assertIn("the lesson index could not be written (OperationalError: database or disk is full)", err)
        self.assertEqual(self.db().read_bytes(), before)
        self.assertEqual(self.leftovers(), [])
        self.assertEqual(self.ids(text="Changed")[0], ["about-git"])  # the fault gone, the next query rebuilds

    def test_an_invalid_store_shows_nothing_and_keeps_the_index(self):
        self.six()
        self.ids(text="Stage")
        before = self.db().read_bytes()
        cases = {"structurally broken": lambda: (self.folder / "broken.md").write_text("---\nid: broken\n---\nb\n",
                                                                                           encoding="utf-8"),
                 "a value rule": lambda: self.lesson("bad-topic", topics="gardening")}
        for name, make in cases.items():
            with self.subTest(name):
                make()
                code, out, err = self.cli("--text", "Stage")
                self.assertEqual((code, out), (1, ""))
                self.assertIn("so no lesson is shown", err)
                self.assertTrue("missing key" in err or "gardening" in err, err)
                self.assertEqual(self.db().read_bytes(), before)
                for name_ in ("broken.md", "bad-topic.md"):
                    (self.folder / name_).unlink(missing_ok=True)


class Matching(Indexed):
    def test_each_kind_of_match(self):
        self.six()
        self.assertEqual(self.ids(paths=["scripts/a.py"])[0], ["specific-file", "whole-folder", "everything"])
        self.assertEqual(self.ids(topics_asked=["git"])[0], ["about-git"])
        self.assertEqual(self.ids(text="plan commit")[0], ["about-git"])  # every word, in any order
        self.assertEqual(self.ids(paths=["scripts/lib/b.py"], role="reader")[0], ["for-readers"])

    def test_a_wrong_role_is_left_out_on_every_route(self):
        self.six()
        self.assertNotIn("for-readers", self.ids(paths=["scripts/lib/b.py"])[0])
        self.assertEqual(self.ids(topics_asked=["review"])[0], [])
        self.assertEqual(self.ids(text="Quote")[0], [])
        self.assertEqual(self.ids(topics_asked=["review"], role="reader")[0], ["for-readers"])
        self.assertEqual(self.ids(text="Quote", role="reader")[0], ["for-readers"])
        self.lesson("for-all", roles="all", topics="review", applies="scripts/lib/b.py")
        self.assertIn("for-all", self.ids(topics_asked=["review"])[0])
        self.assertIn("for-all", self.ids(topics_asked=["review"], role="reader")[0])

    def test_combined_and_repeated_selectors_return_each_lesson_once(self):
        self.six()
        found, more = self.ids(paths=["scripts/a.py", "scripts/lib/b.py"], topics_asked=["git", "tooling"],
                               text="Stage", limit=10)
        self.assertEqual(sorted(found), ["about-git", "everything", "specific-file", "whole-folder"])
        self.assertEqual(len(found), len(set(found)))
        self.assertEqual(more, 0)
        # about-git matches by its glob, its topic and its text: once, and as a path match.
        shown, _ = lessons.query(self.root, paths=["scripts/lib/b.py"], topics_asked=["git"], text="Stage")
        self.assertEqual([(l["id"], l["tier"]) for l in shown if l["id"] == "about-git"], [("about-git", 0)])

    def test_text_is_literal_words_never_an_expression(self):
        self.six()
        for text in ('"Stage', "Stage*", "Stage NEAR plan", "plan AND (commit", "col:Stage", "'; DROP TABLE lessons;--"):
            with self.subTest(text):
                found, _ = self.ids(text=text)
                self.assertIn(found, (["about-git"], []))
        self.assertEqual(self.ids(text="!!! ???")[0], [])  # no word at all matches nothing
        self.assertEqual(self.ids(text="Stage*")[0], ["about-git"])
        self.assertEqual(self.ids(text="Stage NEAR plan")[0], [])  # NEAR is a word the body does not hold


class Ranking(Indexed):
    def test_the_exact_order_holds_twice_and_across_a_rebuild(self):
        self.lesson("a-star", applies="*", added="2026-11-09")
        self.lesson("b-folder", applies="scripts/*.py")
        self.lesson("c-file", applies="scripts/a.py")
        self.lesson("d-file-newer", applies="scripts/a.py", added="2026-11-08")
        self.lesson("e-file-same-date", applies="scripts/a.py", added="2026-11-08")
        self.lesson("f-topic", applies="scripts/lib/b.py", topics="git")
        self.lesson("g-text", applies="scripts/lib/b.py", topics="docs", body="A word such as zebra is rare.")
        expected = ["d-file-newer", "e-file-same-date", "c-file", "b-folder", "a-star", "f-topic", "g-text"]
        ask = dict(paths=["scripts/a.py"], topics_asked=["git"], text="zebra", limit=10)
        self.assertEqual(self.ids(**ask)[0], expected)
        self.assertEqual(self.ids(**ask)[0], expected)
        self.db().unlink()
        self.assertEqual(self.ids(**ask)[0], expected)

    def test_evidence_from_the_triage_files_outranks_a_newer_date_and_refreshes_by_itself(self):
        self.lesson("older", applies="scripts/a.py", added="2026-11-01")
        self.lesson("newer", applies="scripts/a.py", added="2026-11-09")
        self.assertEqual(self.ids(paths=["scripts/a.py"])[0], ["newer", "older"])
        triage = self.folder / "triage" / "00-workspace"
        triage.mkdir(parents=True)
        (triage / "D99-T01-s1.md").write_text("round 1 finding 1: lesson:older\nround 1 finding 2: lesson:older\n"
                                               "round 2 finding 1: one-off, a typo\n", encoding="utf-8")
        shown, _ = lessons.query(self.root, paths=["scripts/a.py"])  # no build called: the digest covers triage
        self.assertEqual([l["id"] for l in shown], ["older", "newer"])
        self.assertIn("evidence 2", shown[0]["why"])
        (triage / "D99-T01-s1.md").write_text("round 1 finding 1: enforced:scripts/a.py\n", encoding="utf-8")
        shown, _ = lessons.query(self.root, paths=["scripts/a.py"])
        self.assertEqual([l["id"] for l in shown], ["newer", "older"])
        self.assertIn("evidence 0", shown[1]["why"])

    def test_five_thousand_lessons_answer_in_under_two_seconds(self):
        globs = ["scripts/a.py", "scripts/*.py", "scripts/**/*.py", "*"]
        frontmatter = ("---\nid: {id}\napplies: {applies}\ntopics: tests\nroles: main\nsource: decision-1\n"
                       "added: 2026-{month:02d}-{day:02d}\nstatus: active\n---\nLesson {n} body.\n")
        for n in range(5000):
            lesson_id = f"gen-{n:04d}"
            applies = globs[n % 4] if n < 300 else "scripts/lib/b.py"
            (self.folder / f"{lesson_id}.md").write_text(frontmatter.format(
                id=lesson_id, applies=applies, month=1 + n % 12, day=1 + n % 28, n=n), encoding="utf-8")
        triage = self.folder / "triage" / "00-workspace"
        triage.mkdir(parents=True)
        (triage / "D99-T02-s1.md").write_text("".join(f"round 1 finding {n}: lesson:gen-0004\n" for n in (1, 2, 3))
                                              + "round 1 finding 4: lesson:gen-0008\n", encoding="utf-8")
        lessons.build_index(self.root)
        import time
        started = time.monotonic()
        shown, more = lessons.query(self.root, paths=["scripts/a.py"])
        elapsed = time.monotonic() - started
        self.assertLess(elapsed, 2.0)
        self.assertEqual(more, 295)
        # The five most specific (the exact file), the best evidenced first, then the newest.
        self.assertEqual([l["id"] for l in shown][:2], ["gen-0004", "gen-0008"])
        self.assertTrue(all(l["why"].startswith("glob scripts/a.py") for l in shown))
        self.assertEqual([l["id"] for l in shown], [l["id"] for l in lessons.query(self.root, paths=["scripts/a.py"])[0]])


class RoundOne(Indexed):
    """Round 1 of D00 T05 §2's review."""

    def test_a_cached_index_is_not_served_once_check_would_refuse_the_store(self):
        self.lesson("about-a", applies="scripts/a.py", topics="tooling")
        self.assertEqual(self.ids(topics_asked=["tooling"])[0], ["about-a"])
        (self.root / "scripts" / "a.py").unlink()  # the file the lesson is about is gone; the lesson did not change
        with self.assertRaises(lessons.StoreInvalid) as caught:
            lessons.query(self.root, topics_asked=["tooling"])
        self.assertIn("'scripts/a.py' matches no file", caught.exception.problems[0])
        code, out, err = self.cli("--topic", "tooling")
        self.assertEqual((code, out), (1, ""))
        (self.root / "scripts" / "a.py").write_text("x = 1\n", encoding="utf-8")
        self.assertEqual(self.ids(topics_asked=["tooling"])[0], ["about-a"])  # back, and served again

    def test_a_cited_record_or_a_decision_that_changes_ends_the_cache_too(self):
        self.write()  # the review-sourced lesson of the fixture, citing RECORD round 1 finding 2
        self.assertEqual(self.ids(topics_asked=["tests"])[0], ["keep-gates-whole"])
        record = self.root / RECORD
        record.write_text(RECORD_TEXT.replace("2. **P2:** the second finding.\n", ""), encoding="utf-8")
        with self.assertRaises(lessons.StoreInvalid):
            lessons.query(self.root, topics_asked=["tests"])
        record.write_text(RECORD_TEXT, encoding="utf-8")
        self.assertEqual(self.ids(topics_asked=["tests"])[0], ["keep-gates-whole"])
        (self.folder / "keep-gates-whole.md").unlink()
        self.lesson("by-decision", topics="tests")
        self.assertEqual(self.ids(topics_asked=["tests"])[0], ["by-decision"])
        (self.root / cli.SPEC).write_text("# Spec\n\nNo decisions any more.\n", encoding="utf-8")
        with self.assertRaises(lessons.StoreInvalid):
            lessons.query(self.root, topics_asked=["tests"])

    def test_an_exact_path_outranks_every_pattern_whatever_its_length(self):
        self.lesson("exact", applies="scripts/a.py")
        self.lesson("bracket-class", applies="scripts/[abcdefghijklmnopqrstuvwxyz]*.py", added="2026-11-09")
        self.lesson("deep-pattern", applies="scripts/**/*.py", added="2026-11-09")
        self.lesson("folder-pattern", applies="scripts/*.py", added="2026-11-09")
        # The two broad patterns tie on specificity (9 each), so the id settles them.
        self.assertEqual(self.ids(paths=["scripts/a.py"])[0], ["exact", "folder-pattern", "bracket-class", "deep-pattern"])
        self.assertEqual(self.ids(paths=["scripts/a.py"], limit=1), (["exact"], 3))
        self.assertGreater(lessons.specificity("scripts/a.py"), lessons.specificity("scripts/[a-z]*.py"))
        self.assertLess(lessons.specificity("*"), lessons.specificity("scripts/**/*.py"))

    def test_evidence_counts_a_lines_own_disposition_once(self):
        self.lesson("existing", applies="scripts/a.py", added="2026-11-01")
        self.lesson("other", applies="scripts/a.py", added="2026-11-09")
        triage = self.folder / "triage" / "00-workspace"
        triage.mkdir(parents=True)
        (triage / "D99-T01-s1.md").write_text(
            "round 1 finding 1: one-off, already covered by lesson:existing and lesson:existing again\n"
            "round 1 finding 2: enforced:scripts/a.py (see lesson:existing)\n"
            "- round 2 finding 1: lesson:other, it recurs; compare lesson:other\n", encoding="utf-8")
        self.assertEqual(lessons.evidence(self.root), {"other": 1})
        shown, _ = lessons.query(self.root, paths=["scripts/a.py"])
        self.assertEqual([(l["id"], l["evidence"]) for l in shown], [("other", 1), ("existing", 0)])


class Triage(Indexed):
    """D00 T05 §3: the findings to triage, and the triage files that hold their dispositions."""

    TWO = "docs/reviews/00-workspace/D99-T03-s1.md"
    TWO_TEXT = ("## Round 1: astra (`gpt-6-astra` via `codex`)\n\n1. **[P1] Alpha breaks.** `scripts/a.py:1` it does.\n"
                "2. **P2, `scripts/a.py:2`: Beta breaks.** More.\n\nOVERALL: needs-attention\n\n"
                "### Dispositions\n\n1. **[P1] Alpha breaks**: Fixed.\n\n"
                "## Round 2: astra (`gpt-6-astra` via `codex`)\n\n1. **P1** Gamma breaks. Detail.\n"
                "2. **P3:** a nit.\n3. **P2:** Delta breaks.\n4. **P2**, Epsilon breaks.\n\nOVERALL: needs-attention\n")

    def setUp(self):
        super().setUp()
        (self.root / self.TWO).write_text(self.TWO_TEXT, encoding="utf-8")

    def triage(self, record, text):
        path = lessons.triage_path(self.root, record)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def listing(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(["candidates", *argv], root=self.root)
        return code, out.getvalue().splitlines(), err.getvalue()

    def keys(self, *argv):
        code, lines, err = self.listing(*argv)
        self.assertEqual(code, 0, err)
        found = []
        for line in lines:  # (record, round number, finding, severity); another pass shows as its label
            record, label, finding, severity = re.match(r"(\S+) (.+) finding (\d+) \[(P\d)\]", line).groups()
            found.append((record, label[len("round "):] if label.startswith("round ") else label, finding, severity))
        return found

    def test_the_tagged_findings_are_listed_and_a_p3_is_not(self):
        code, lines, err = self.listing(RECORD)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(lines, [f"{RECORD} plan finding 1 [P2]: a plan finding.",
                                 f"{RECORD} round 1 finding 1 [P1] scripts/a.py:3: the first finding.",
                                 f"{RECORD} round 1 finding 2 [P2]: the second finding."])

    def test_every_tag_form_is_read_and_the_writers_notes_after_a_round_are_not(self):
        self.assertEqual(self.keys(self.TWO), [(self.TWO, "1", "1", "P1"), (self.TWO, "1", "2", "P2"),
                                               (self.TWO, "2", "1", "P1"), (self.TWO, "2", "3", "P2"),
                                               (self.TWO, "2", "4", "P2")])

    def test_all_records_are_listed_when_none_is_named(self):
        records = {key[0] for key in self.keys()}
        self.assertEqual(records, {RECORD, RECORD2, self.TWO})

    def test_untriaged_prints_exactly_what_is_left_and_a_removed_line_returns(self):
        self.triage(self.TWO, "round 1 finding 1: one-off, a typo in a message\nround 2 finding 3: enforced:scripts/a.py\n")
        self.triage(RECORD, "round 1 finding 1: one-off, the same number in another record\n")
        left = self.keys("--untriaged", self.TWO, RECORD)
        self.assertEqual(left, [(self.TWO, "1", "2", "P2"), (self.TWO, "2", "1", "P1"), (self.TWO, "2", "4", "P2"),
                                (RECORD, "plan", "1", "P2"), (RECORD, "1", "2", "P2")])
        self.triage(self.TWO, "round 2 finding 3: enforced:scripts/a.py\n")
        self.assertIn((self.TWO, "1", "1", "P1"), self.keys("--untriaged", self.TWO))
        self.triage(self.TWO, "".join(f"round {r} finding {k}: one-off, fixed and gone\n"
                                      for r, k in ((1, 1), (1, 2), (2, 1), (2, 3), (2, 4))))
        self.assertEqual(self.listing("--untriaged", self.TWO), (0, [], ""))

    def test_each_bad_triage_line_is_refused_and_leaves_its_finding_untriaged(self):
        self.lesson("a-lesson")
        name = "docs/lessons/triage/00-workspace/D99-T03-s1.md"
        cases = [
            ("round 9 finding 1: one-off, no such round", "has no round 9 finding 1"),
            ("round 1 finding 7: one-off, no such finding", "has no round 1 finding 7"),
            ("round 1 finding 1: one-off, first\nround 1 finding 1: one-off, again", "already has a disposition"),
            ("round 1 finding 1: one-off, first\nround 1 finding 1: lesson:a-lesson", "already has a disposition"),
            ("round 1 finding 1: wontfix because", "'wontfix' is not lesson:<id>, enforced:<path> or one-off"),
            ("round 1 finding 1: one-off", "one-off needs a reason"),
            ("round 1 finding 1: enforced:scripts/gone.py", "names no file the repository holds"),
            ("round 1 finding 1: lesson:no-such-lesson", "lesson:no-such-lesson names no lesson file"),
            ("finding one is a lesson", "not a triage line"),
        ]
        for text, fragment in cases:
            with self.subTest(fragment):
                self.triage(self.TWO, text + "\n")
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                    code = cli.main(["check"], root=self.root)
                self.assertEqual(code, 1)
                self.assertIn(fragment, out.getvalue())
                self.assertIn(f"{name}:", out.getvalue())
                last = text.splitlines()[-1]
                if last.startswith("round 1 finding 1") and "first" not in text:
                    self.assertIn((self.TWO, "1", "1", "P1"), self.keys("--untriaged", self.TWO))

    def test_a_finding_with_two_lines_stays_outstanding(self):
        # Round 1: the first of two conflicting lines was kept, so the finding left the untriaged list.
        self.lesson("a-lesson")
        self.triage(self.TWO, "round 1 finding 1: one-off, a typo\nround 1 finding 1: lesson:a-lesson\n"
                              "round 1 finding 1: enforced:scripts/a.py\nround 1 finding 2: one-off, fine\n")
        left = self.keys("--untriaged", self.TWO)
        self.assertIn((self.TWO, "1", "1", "P1"), left)
        self.assertNotIn((self.TWO, "1", "2", "P2"), left)
        self.assertEqual(lessons.evidence(self.root).get("a-lesson", 0), 1)  # check refuses the store all the same
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["check"], root=self.root), 1)
        self.assertEqual(out.getvalue().count("already has a disposition"), 2)

    def test_two_lines_for_one_finding_leave_it_outstanding_in_either_order(self):
        # Completion review: an invalid line followed by a valid one for the same finding was accepted.
        self.lesson("a-lesson")
        orders = {"invalid first": "round 1 finding 1: lesson:no-such-lesson\nround 1 finding 1: enforced:scripts/a.py\n",
                  "valid first": "round 1 finding 1: enforced:scripts/a.py\nround 1 finding 1: lesson:no-such-lesson\n",
                  "both invalid": "round 1 finding 1: wontfix x\nround 1 finding 1: one-off\n",
                  "both valid": "round 1 finding 1: one-off, a typo\nround 1 finding 1: lesson:a-lesson\n"}
        for name, text in orders.items():
            with self.subTest(name):
                self.triage(self.TWO, text)
                self.assertIn((self.TWO, "1", "1", "P1"), self.keys("--untriaged", self.TWO))
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    self.assertEqual(cli.main(["check"], root=self.root), 1)
                self.assertIn("already has a disposition", out.getvalue())

    def test_the_location_first_form_is_read(self):
        # Round 1: `` **`path:line` (P2): ...`` findings of an older record were dropped without a word.
        record = "docs/reviews/00-workspace/D99-T04-s1.md"
        (self.root / record).write_text(
            "## Round 1: sol (`gpt` via `codex`)\n\n"
            "1. **`design/x.md:42` (P2): Installation is reported instead of licensing status.** More.\n"
            "2. **`a.py:1` and `b.py:2` (P1): Two places share one defect.** More.\n\nOVERALL: needs-attention\n",
            encoding="utf-8")
        code, lines, err = self.listing(record)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(lines, [
            f"{record} round 1 finding 1 [P2] design/x.md:42: Installation is reported instead of licensing status.",
            f"{record} round 1 finding 2 [P1] a.py:1: Two places share one defect."])

    def test_a_severity_in_an_unknown_form_refuses_the_record(self):
        record = "docs/reviews/00-workspace/D99-T05-s1.md"
        (self.root / record).write_text(
            "## Round 1: sol (`gpt` via `codex`)\n\n1. **Severity P1 (blocking)** A form nobody has taught the reader.\n"
            "\nOVERALL: needs-attention\n", encoding="utf-8")
        code, lines, err = self.listing(record)
        self.assertEqual((code, lines), (1, []))
        self.assertIn("round 1 finding 1 names a severity in a form this reader does not know", err)
        self.assertEqual(self.listing()[0], 1)  # and listing every record refuses too, rather than skip it

    def test_every_record_of_this_repository_is_read_whole(self):
        found = lessons.candidates(ROOT)
        self.assertGreater(len(found), 700)
        self.assertIn("docs/reviews/02-interface/D02-T01-s2.md", {item["record"] for item in found})

    # D00 T05 §9: every pass has an identity.

    ALL = "docs/reviews/00-workspace/D99-T06-s1.md"
    ALL_TEXT = (
        "## Plan review: astra (`gpt-6-astra` via `codex`)\n\n1. **P1, line 91:** The plan omits a role.\n"
        "2. **P2**, `todo/x.md:92`: The plan omits a test.\n\nPLAN: gaps\nOVERALL: needs-attention\n\n"
        "- Planned: gap 1 in abc1234\n\n"
        "## Round 1: astra (`gpt-6-astra` via `codex`)\n\n1. **P2, `scripts/a.py:5`: A round finding.** More.\n\n"
        "OVERALL: needs-attention\n\n"
        "## Completion review: astra (`gpt-6-astra` via `codex`)\n\nPart 1\n\n1. **present:** all of it.\n"
        "2. **missing-in-scope:** one thing, see the gap list.\n\nGap list\n\n"
        "1. **P2, missing-in-scope:** `scripts/a.py:9`: A completion gap.\n"
        "2. **missing-in-scope, P2**: `scripts/a.py:10` Another, its class first.\n"
        "3. **P1 | missing-in-scope:** `scripts/a.py:11` A third, with a bar.\n"
        "4. **missing-in-scope, P3:** `scripts/a.py:15`: A fourth, the colon inside the bold.\n\nCOMPLETION: gaps\n\n"
        "- Implemented: gap 1 in abc1234\n\n"
        "## Reconciliation review: astra (`gpt-6-astra` via `codex`)\n\n1. **closed, P2:** the first gap is closed.\n"
        "2. **P2, open: completion gap 2.** It is still open.\n3. **closed (original P1):** the third.\n"
        "4. **P2, `scripts/a.py:12`: A new defect in the repair.** More.\n\nRECONCILIATION: gaps\n\n"
        "## Reconciliation review: astra (`gpt-6-astra` via `codex`)\n\n1. **closed, P2:** done.\n\n"
        "No new findings.\n\nRECONCILIATION: gaps\n\n"
        "## Reconciliation review: astra (`gpt-6-astra` via `codex`)\n\n"
        "1. **P1, `scripts/a.py:13`: A defect the third pass found.** More.\n\nRECONCILIATION: complete\n")

    def all_passes(self):
        (self.root / self.ALL).write_text(self.ALL_TEXT, encoding="utf-8")

    def test_every_pass_lists_exactly_its_tagged_findings(self):
        self.all_passes()
        code, lines, err = self.listing(self.ALL)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual([line[len(self.ALL) + 1:] for line in lines], [
            "plan finding 1 [P1]: line 91: The plan omits a role.",
            "plan finding 2 [P2] todo/x.md:92: The plan omits a test.",
            "round 1 finding 1 [P2] scripts/a.py:5: A round finding.",
            "completion finding 1 [P2] scripts/a.py:9: A completion gap.",
            "completion finding 2 [P2] scripts/a.py:10: Another, its class first.",
            "completion finding 3 [P1] scripts/a.py:11: A third, with a bar.",
            "reconciliation 1 finding 1 [P2] scripts/a.py:12: A new defect in the repair.",
            "reconciliation 3 finding 1 [P1] scripts/a.py:13: A defect the third pass found."])

    def test_a_status_is_its_label_not_a_word_in_a_title(self):
        # Round 1 of §9: a new finding titled "... leaves the file handle open" was dropped as a status line.
        record = "docs/reviews/00-workspace/D99-T08-s1.md"
        (self.root / record).write_text(
            "## Reconciliation review: astra (`gpt-6-astra` via `codex`)\n\n"
            "1. **P2, `scripts/a.py:12`: Repair leaves the file handle open.** Reproduce by cancelling.\n"
            "2. **P1, `scripts/a.py:13`: A closed socket is written to.** More.\n"
            "3. **closed, P2:** an earlier gap.\n4. **open, P3, gap 2:** another.\n"
            "5. **P1, open: completion gap 1.** Still open.\n6. **P2, closed: a recovery command.** Done.\n"
            "7. **closed (original P2):** done.\n"
            "8. **P1, `scripts/a.py:14`: open overall: an earlier requirement.** Still open.\n\nRECONCILIATION: gaps\n",
            encoding="utf-8")
        code, lines, err = self.listing(record)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual([line[len(record) + 1:] for line in lines], [
            "reconciliation 1 finding 1 [P2] scripts/a.py:12: Repair leaves the file handle open.",
            "reconciliation 1 finding 2 [P1] scripts/a.py:13: A closed socket is written to."])

    def test_a_fenced_block_is_a_quotation(self):
        # The same review quoted a heading and a finding in a code block; both were read as real.
        record = "docs/reviews/00-workspace/D99-T09-s1.md"
        (self.root / record).write_text(
            "## Round 1: astra (`gpt-6-astra` via `codex`)\n\n1. **P2: A reader bug.** A reviewer can return:\n\n"
            "   ```text\n   ## Reconciliation review: astra (`gpt-6-astra` via `codex`)\n"
            "   1. **P2, `scripts/a.py:12`: Repair leaves the file handle open.**\n   RECONCILIATION: gaps\n   ```\n\n"
            "2. **P2: A second finding after the quotation.** More.\n\nOVERALL: needs-attention\n", encoding="utf-8")
        self.assertEqual(self.keys(record), [(record, "1", "1", "P2"), (record, "1", "2", "P2")])

    def test_three_real_records_of_this_repository_read_every_pass(self):
        expect = {"docs/reviews/00-workspace/D00-T05-s4.md": {"plan": 4, "round 1": 1, "completion": 2},
                  "docs/reviews/00-workspace/D00-T07-s3.md": {"plan": 6, "round 1": 3, "completion": 2},
                  "docs/reviews/00-workspace/D00-T04-s2.md": {"plan": 4, "round 1": 1, "completion": 1}}
        for record, counts in expect.items():
            with self.subTest(record):
                found = lessons.candidates(ROOT, [record])
                got = {}
                for item in found:
                    got[item["pass"]] = got.get(item["pass"], 0) + 1
                self.assertEqual(got, counts)

    def test_a_plan_only_record_is_listed_named_and_discovered(self):
        record = "docs/reviews/00-workspace/D99-T07-s1.md"
        (self.root / record).write_text("## Plan review: astra (`gpt-6-astra` via `codex`)\n\n"
                                        "1. **P1, line 5:** Only a plan review so far.\n\nPLAN: gaps\n", encoding="utf-8")
        self.assertEqual(self.keys(record), [(record, "plan", "1", "P1")])
        self.assertIn((record, "plan", "1", "P1"), self.keys())
        self.assertIn(record, lessons.review_records(self.root))

    def test_each_pass_is_triaged_by_its_own_name(self):
        self.all_passes()
        self.lesson("a-lesson")
        self.triage(self.ALL, "plan finding 1: lesson:a-lesson\ncompletion finding 2: enforced:scripts/a.py\n"
                              "reconciliation 1 finding 1: one-off, a slip in the repair\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["check"], root=self.root), 0, out.getvalue())
        self.assertEqual(self.keys("--untriaged", self.ALL), [
            (self.ALL, "plan", "2", "P2"), (self.ALL, "1", "1", "P2"), (self.ALL, "completion", "1", "P2"),
            (self.ALL, "completion", "3", "P1"), (self.ALL, "reconciliation 3", "1", "P1")])
        self.assertEqual(lessons.evidence(self.root), {"a-lesson": 1})
        for line, fragment in (("plan finding 3: one-off, none such", "has no plan finding 3"),
                               ("reconciliation 2 finding 1: one-off, that pass raised nothing",
                                "has no reconciliation 2 finding 1"),
                               ("reconciliation finding 1: one-off, no number", "not a triage line"),
                               ("completion 2 finding 1: one-off, there is one completion", "has no completion 2 finding 1")):
            with self.subTest(fragment):
                self.triage(self.ALL, line + "\n")
                with contextlib.redirect_stdout(out):
                    self.assertEqual(cli.main(["check"], root=self.root), 1)
                self.assertIn(fragment, out.getvalue())

    def test_reconciliations_keep_their_numbers_when_another_is_appended(self):
        self.all_passes()
        for name, source in (("from-a-reconciliation", "#reconciliation-3/finding-1"), ("from-the-plan", "#plan/finding-2"),
                             ("from-the-completion", "#completion/finding-3")):
            self.write(name=name, id=name, applies="*", source=self.ALL + source)
        self.triage(self.ALL, "reconciliation 3 finding 1: lesson:from-a-reconciliation\n")
        # The first reconciliation's finding 1 shares its number with the third's and stays outstanding.
        self.assertIn((self.ALL, "reconciliation 1", "1", "P2"), self.keys("--untriaged", self.ALL))
        self.assertNotIn((self.ALL, "reconciliation 3", "1", "P1"), self.keys("--untriaged", self.ALL))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["check"], root=self.root), 0, out.getvalue())
        (self.root / self.ALL).write_text(
            self.ALL_TEXT + "\n## Reconciliation review: astra (`gpt-6-astra` via `codex`)\n\n"
            "1. **P2, `scripts/a.py:14`: Found by a fourth pass.** More.\n\nRECONCILIATION: complete\n", encoding="utf-8")
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["check"], root=self.root), 0, out.getvalue())  # every line and source holds
        left = self.keys("--untriaged", self.ALL)
        self.assertIn((self.ALL, "reconciliation 4", "1", "P2"), left)
        self.assertNotIn((self.ALL, "reconciliation 3", "1", "P1"), left)

    def test_a_source_names_a_pass_that_exists(self):
        self.all_passes()
        for source, fragment in ((f"{self.ALL}#plan/finding-3", "plan of"), (f"{self.ALL}#completion-2/finding-1", "has no completion 2 review heading"),
                                 (f"{self.ALL}#reconciliation/finding-1", "is named with its number"),
                                 (f"{self.ALL}#reconciliation-2/finding-1", "reconciliation 2 of"),
                                 (f"{self.ALL}#round/finding-1", "is named with its number")):
            with self.subTest(source):
                for old in self.folder.glob("*.md"):
                    if old.name != "README.md":
                        old.unlink()
                self.write(name="cited", id="cited", applies="*", source=source)
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    self.assertEqual(cli.main(["check"], root=self.root), 1)
                self.assertIn(fragment, out.getvalue())
    def test_the_review_skills_triage_step_walked_through(self):
        # D00 T05 §4: what `review-todo-section` tells the lead to do between the round and the completion review.
        self.assertEqual(len(self.keys("--untriaged", self.TWO)), 5)  # the round's confirmed findings to triage
        self.lesson("ownership-is-checked-when-acting", applies="scripts/a.py", topics="tooling",
                    body="Check ownership in the step that acts, never at an earlier check.")
        self.triage(self.TWO, "# Triage of D99 T03 §1\n\nround 1 finding 1: lesson:ownership-is-checked-when-acting\n"
                              "round 1 finding 2: enforced:scripts/a.py\nround 2 finding 1: one-off, a typo in a message\n"
                              "round 2 finding 3: lesson:ownership-is-checked-when-acting\n"
                              "round 2 finding 4: enforced:scripts/lib/b.py\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["check"], root=self.root), 0, out.getvalue())  # the dispositions validate
        self.assertEqual(self.listing("--untriaged", self.TWO), (0, [], ""))  # nothing left, and a resume adds none
        shown, _ = lessons.query(self.root, paths=["scripts/a.py"])  # the next section's read step finds it
        self.assertEqual([(l["id"], l["evidence"]) for l in shown], [("ownership-is-checked-when-acting", 2)])
        # The section added the check that enforces it, so the lesson is retired in the same commit.
        self.lesson("ownership-is-checked-when-acting", applies="scripts/a.py", topics="tooling", status="retired",
                    retired_by="scripts/a.py", body="Check ownership in the step that acts, never at an earlier check.")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["check"], root=self.root), 0)
        self.assertEqual(lessons.query(self.root, paths=["scripts/a.py"]), ([], 0))  # retired: no longer returned

    def test_p3_findings_are_listed_on_request_so_a_resume_misses_none(self):
        # Round 1 of §4: a fixed P3 finding was invisible to the resume step.
        self.assertNotIn((self.TWO, "2", "2", "P3"), self.keys("--untriaged", self.TWO))
        self.assertIn((self.TWO, "2", "2", "P3"), self.keys("--untriaged", "--p3", self.TWO))
        self.triage(self.TWO, "round 2 finding 2: one-off, a nit about wording\n")
        self.assertNotIn((self.TWO, "2", "2", "P3"), self.keys("--untriaged", "--p3", self.TWO))
        self.assertEqual(len(self.keys("--p3", self.TWO)), 6)

    def test_a_failed_query_reads_nothing(self):
        # The section skill's read step: exit 1 shows no lesson, so it cannot count as the read.
        self.lesson("a-lesson", applies="scripts/a.py")
        self.lesson("bad-topic", applies="scripts/a.py", topics="gardening")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(["query", "--role", "main", "--path", "scripts/a.py"], root=self.root)
        self.assertEqual((code, out.getvalue()), (1, ""))
        self.assertIn("run python scripts/lessons.py check", err.getvalue())
        (self.folder / "bad-topic.md").unlink()  # repaired, as the skill says, and the query run again
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["query", "--role", "main", "--path", "scripts/a.py"], root=self.root), 0)
        self.assertIn("a-lesson", out.getvalue())

    def test_a_triage_file_without_its_record_is_refused(self):
        self.triage("docs/reviews/00-workspace/D99-T09-s9.md", "round 1 finding 1: one-off, orphaned\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(["check"], root=self.root)
        self.assertEqual(code, 1)
        self.assertIn("its review record docs/reviews/00-workspace/D99-T09-s9.md does not exist", out.getvalue())

    def test_a_valid_triage_passes_check_and_counts_as_evidence(self):
        self.lesson("a-lesson")
        self.triage(self.TWO, "# Triage\n\nround 1 finding 1: lesson:a-lesson\n- round 1 finding 2: lesson:a-lesson, the same\n"
                              "round 2 finding 1: enforced:scripts/a.py\nround 2 finding 3: one-off, a typo\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["check"], root=self.root), 0, out.getvalue())
        self.assertEqual(lessons.evidence(self.root), {"a-lesson": 2})

    def test_input_that_cannot_be_read_is_exit_1_naming_the_file(self):
        (self.root / "docs/reviews/00-workspace/empty.md").write_text("# Notes\n\nNo review here.\n", encoding="utf-8")
        for argv, fragment in ((["docs/reviews/00-workspace/missing.md"], "missing.md: cannot be read"),
                               (["docs/reviews/00-workspace/empty.md"], "empty.md: holds no review pass"),
                               (["--untriaged", "scripts/a.py"], "scripts/a.py: holds no review pass")):
            with self.subTest(fragment):
                code, lines, err = self.listing(*argv)
                self.assertEqual((code, lines), (1, []))
                self.assertIn(fragment, err)
        lessons.triage_path(self.root, self.TWO).mkdir(parents=True)  # a folder where the triage file should be
        code, lines, err = self.listing("--untriaged", self.TWO)
        self.assertEqual(code, 0)  # no triage file at that path: every finding is still outstanding
        self.assertEqual(len(lines), 5)
        lessons.triage_path(self.root, self.TWO).rmdir()
        path = self.triage(self.TWO, "round 1 finding 1: one-off, x\n")
        path.write_bytes(b"\xff\xfe\x00 not utf-8 \xff")
        code, lines, err = self.listing("--untriaged", self.TWO)
        self.assertEqual((code, lines), (1, []))
        self.assertIn("D99-T03-s1.md: cannot be read", err)


class CommandLine(Indexed):
    def test_the_plain_and_json_forms(self):
        self.six()
        code, out, err = self.cli("--topic", "git")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out, "about-git  (decision-1)\n  Stage the plan before a commit.\n")
        code, out, err = self.cli("--topic", "git", "--json")
        self.assertEqual(json.loads(out), [{"id": "about-git", "source": "decision-1",
                                            "body": "Stage the plan before a commit."}])

    def test_why_names_the_reason_and_the_lessons_not_returned(self):
        self.six()
        code, out, err = self.cli("--path", "scripts/a.py", "--limit", "2", "--why")
        self.assertEqual(code, 0)
        self.assertIn("specific-file  (decision-1)\n  why: glob scripts/a.py; evidence 0\n", out)
        self.assertIn("  why: glob scripts/*.py; evidence 0\n", out)
        self.assertTrue(out.endswith("1 more matching lesson(s) not returned\n"))
        self.assertNotIn("everything", out)  # it matched and was not shown: the count says so

    def test_why_with_json_keeps_standard_output_one_array(self):
        self.six()
        code, out, err = self.cli("--path", "scripts/a.py", "--limit", "1", "--why", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), [{"id": "specific-file", "source": "decision-1",
                                            "body": "The body of specific-file says what to do.",
                                            "why": "glob scripts/a.py; evidence 0"}])
        self.assertEqual(err, "2 more matching lesson(s) not returned\n")

    def test_the_edges(self):
        self.six()
        self.assertEqual(self.cli("--topic", "git")[1].split()[0], "about-git")  # the role defaults to main
        self.assertEqual(self.cli("--topic", "review")[1], "")
        for argv, fragment in ((["--role", "main"], "needs a --path"), (["--topic", "git", "--limit", "0"], "1 to 10"),
                               (["--topic", "git", "--limit", "11"], "1 to 10"),
                               (["--topic", "git", "--role", "principal-implementer"], "--role is one of"),
                               (["--topic", "git", "--role", "all"], "--role is one of")):
            with self.subTest(argv):
                code, out, err = self.cli(*argv)
                self.assertEqual((code, out), (2, ""))
                self.assertIn(fragment, err)
        self.assertEqual(self.cli("--topic", "ui"), (0, "", ""))  # no match: nothing, and not an error
        self.assertEqual(self.cli("--topic", "ui", "--json")[:2], (0, "[]\n"))
        self.assertEqual(self.cli("--topic", "git", "--limit", "10")[0], 0)

    def test_an_empty_store_answers_with_nothing(self):
        self.assertEqual(self.cli("--path", "scripts/x.py", "--role", "main"), (0, "", ""))

    def test_the_command_end_to_end_as_a_process(self):
        self.six()
        scripts = self.root / "scripts"
        shutil.copyfile(SCRIPTS / "lessons.py", scripts / "lessons.py")
        shutil.copyfile(SCRIPTS / "lib" / "lessons.py", scripts / "lib" / "lessons.py")

        def run(*argv):
            done = subprocess.run([sys.executable, "-B", str(scripts / "lessons.py"), "query", *argv],
                                  capture_output=True, text=True, timeout=120, encoding="utf-8")
            return done.returncode, done.stdout, done.stderr
        expected = [{"id": "specific-file", "source": "decision-1", "body": "The body of specific-file says what to do."},
                    {"id": "whole-folder", "source": "decision-1", "body": "The body of whole-folder says what to do."}]
        code, out, err = run("--path", "scripts/a.py", "--limit", "2", "--json")
        self.assertEqual((code, json.loads(out)), (0, expected), err)
        stamp = self.db().stat().st_mtime_ns
        code, out, err = run("--path", "scripts/a.py", "--limit", "2", "--json")  # from the stored index
        self.assertEqual((code, json.loads(out)), (0, expected), err)
        self.assertEqual(self.db().stat().st_mtime_ns, stamp, "an unchanged store was indexed again")
        code, out, err = run("--path", "scripts/a.py")
        self.assertEqual(out.count("\n  The body of"), 3)


if __name__ == "__main__":
    unittest.main()
