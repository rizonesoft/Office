# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/lib/lessons.py and scripts/lessons.py check (D00 T05 §1): a lesson is read exactly, and every rule of
docs/lessons/README.md refuses what breaks it. Each test builds its own small git repository in a temporary folder."""
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
        triage = self.folder / "triage"
        triage.mkdir()
        (triage / "r.md").write_text("".join(f"f{n}: lesson:gen-0004\n" for n in range(3))
                                     + "f: lesson:gen-0008\n", encoding="utf-8")
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
        triage = self.folder / "triage"
        triage.mkdir()
        (triage / "r.md").write_text(
            "round 1 finding 1: one-off, already covered by lesson:existing and lesson:existing again\n"
            "round 1 finding 2: enforced:scripts/a.py (see lesson:existing)\n"
            "- round 2 finding 1: lesson:other, it recurs; compare lesson:other\n", encoding="utf-8")
        self.assertEqual(lessons.evidence(self.root), {"other": 1})
        shown, _ = lessons.query(self.root, paths=["scripts/a.py"])
        self.assertEqual([(l["id"], l["evidence"]) for l in shown], [("other", 1), ("existing", 0)])


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
