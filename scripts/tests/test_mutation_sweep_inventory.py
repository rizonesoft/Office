# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/mutation-sweep-inventory.py over a tiny fixture checker, schema and test file (D02 T01 §27): each kind of
rule is enumerated, and a killed, a surviving, an erroring, a timed-out and an undiscovered removal are reported
apart, with a failing unmutated run stopping the sweep. D02 T01 §38: the shares of the rules, a killed removal's
run ending at its first failure, the check of what a push changed, and the `sweep` job of the CI workflow."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
import textwrap
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mutation_sweep", SCRIPTS / "mutation-sweep-inventory.py")
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)

CHECKER = '''
class Unreadable(Exception):
    pass


def check(value):
    problems = []
    if value == "a":
        problems.append("a")
    if value == "b":
        problems.append("b")
    if value == "c":
        problems.append("c")
    if value == "slow":
        problems.append("slow")
    if value == "raise":
        raise Unreadable(value)
    return problems


def typed(value):
    if not isinstance(value, str):
        return [f"expected text, not {value!r}"]
    return []


def both(value):
    problems = []
    if value == "d":
        problems.append("d")
    return problems
'''
SCHEMA = {"type": "object", "required": ["id"],
          "properties": {"id": {"type": "string", "pattern": "^a|^b"}, "note": {"type": "string"}}}
TESTS = '''
import importlib.util
import json
from pathlib import Path
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("ci", ROOT / "scripts" / "check-inventory.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)
SCHEMA = json.loads((ROOT / "design" / "inventory" / "schema.json").read_text(encoding="utf-8"))
assert "required" in SCHEMA  # removing `required` breaks discovery


class Rules(unittest.TestCase):
    def test_a(self):
        self.assertEqual(ci.check("a"), ["a"])

    def test_c(self):
        self.assertEqual(ci.check("c")[0].upper(), "C")  # an IndexError, not a failure, once the guard goes

    def test_d_errors_first(self):
        self.assertEqual(ci.both("d")[0], "d")  # an IndexError once the guard goes, and the run goes on

    def test_d_then_fails(self):
        self.assertEqual(ci.both("d"), ["d"])  # the failure after that error: the removal is killed here

    def test_slow(self):
        if not ci.check("slow"):
            time.sleep(20)  # bounded: the sweep's time limit stops it first

    def test_raise(self):
        with self.assertRaises(ci.Unreadable):
            ci.check("raise")

    def test_typed(self):
        self.assertTrue(ci.typed(5))

    def test_pattern(self):
        self.assertEqual(SCHEMA["properties"]["id"]["pattern"].split("|")[0], "^a")
'''


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "scripts" / "lib").mkdir(parents=True)
        (self.root / "scripts" / "tests").mkdir()
        (self.root / "design" / "inventory").mkdir(parents=True)
        shutil.copyfile(SCRIPTS / "mutation-sweep-inventory.py", self.root / "scripts" / "mutation-sweep-inventory.py")
        shutil.copyfile(SCRIPTS / "lib" / "process_tree.py", self.root / "scripts" / "lib" / "process_tree.py")
        (self.root / "scripts" / "check-inventory.py").write_text(textwrap.dedent(CHECKER), encoding="utf-8")
        (self.root / "scripts" / "tests" / "test_check_inventory.py").write_text(TESTS, encoding="utf-8")
        (self.root / "design" / "inventory" / "schema.json").write_text(json.dumps(SCHEMA), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def sweep(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ms.main(["--workers", "2", "--timeout", "8", *argv], root=self.root)
        return code, out.getvalue(), err.getvalue()

    def line(self, out, name):
        return next(x for x in out.splitlines() if x.endswith(name) or name in x)


class Enumeration(Fixture):
    def test_every_kind_of_rule_is_listed(self):
        code, out, _ = self.sweep("--list")
        self.assertEqual(code, 0)
        names = out.splitlines()
        for want in ('guard check-inventory.py:8 if value == \'a\'', "guard check-inventory.py:16 if value == 'raise'",
                     "guard check-inventory.py:22 if not isinstance(value, str)",  # a refusal returned directly
                     "schema / type", "schema / required", "schema / properties.id", "schema / properties.note",
                     "schema /properties/id pattern", "schema /properties/id pattern alternative 1 of 2: ^a"):
            self.assertTrue(any(n.startswith(want) for n in names), want)
        self.assertEqual(names[-1], f"rules: {len(names) - 1}")

    def test_a_guard_is_removed_in_place_whatever_the_line_endings(self):
        for ending in ("\n", "\r\n"):  # a CRLF checker once shifted each removal by a character a line
            path = self.root / "scripts" / "check-inventory.py"
            path.write_bytes(textwrap.dedent(CHECKER).replace("\n", ending).encode("utf-8"))
            rule = next(r for r in ms.rules_of(self.root) if "if value == 'b'" in r.name)
            removed = rule.remove(path.read_bytes().decode("utf-8"))
            self.assertIn("    if False:" + ending + "        problems.append(\"b\")", removed, repr(ending))
            compile(removed, "check-inventory.py", "exec")

    def test_the_real_checker_and_schema_enumerate(self):
        rules = ms.rules_of(SCRIPTS.parent)
        self.assertTrue(any(r.name.startswith("guard check-inventory.py") and "unfinished" not in r.name
                            for r in rules))
        self.assertTrue(any("properties." in r.name for r in rules))
        self.assertTrue(any(r.name.endswith(" then") for r in rules))
        self.assertTrue(any(r.name.endswith(" if") for r in rules))  # a conditional's test is a rule of its own


class Outcomes(Fixture):
    def test_each_outcome_is_reported_apart_and_the_sweep_fails(self):
        code, out, err = self.sweep("--only", "guard", "--only", "required", "--only", "alternative")
        self.assertEqual(code, 1, err)
        # Each line carries how every test of that run ended and that all of them ran (completion review, gap 1):
        # a count of failures alone would not show that discovery was complete.
        total = out.splitlines()[0].split(" tests pass")[0].split()[-1]
        self.assertEqual(out.splitlines()[0].split(" (")[1].split(")")[0],
                         f"0 failing, 0 erroring, {total} passing, 0 skipped, {total} of {total} run")
        # D02 T01 §38: a killed removal's run ends at its first failing test, here the first test of all.
        self.assertGreater(int(total), 1)
        self.assertTrue(self.line(out, "if value == 'a'").startswith(
            f"KILLED       1 failing, 0 erroring, 0 passing, 0 skipped, 1 of {total} run"),
            self.line(out, "if value == 'a'"))
        # An error does not end the run: the test after it fails, and that failure kills the removal.
        self.assertTrue(self.line(out, "if value == 'd'").startswith(
            f"KILLED       1 failing, 1 erroring, 2 passing, 0 skipped, 4 of {total} run"),
            self.line(out, "if value == 'd'"))
        self.assertTrue(self.line(out, "if value == 'b'").startswith(
            f"SURVIVED     0 failing, 0 erroring, {total} passing, 0 skipped, {total} of {total} run"),
            self.line(out, "if value == 'b'"))
        self.assertTrue(self.line(out, "if value == 'c'").startswith(
            f"ERRORED      0 failing, 1 erroring, {int(total) - 1} passing, 0 skipped, {total} of {total} run"),
            self.line(out, "if value == 'c'"))
        undiscovered = self.line(out, "schema / required")
        self.assertIn(" passing, ", undiscovered)
        self.assertNotIn(f"{total} of {total} run", undiscovered)  # fewer tests found or run than the unmutated run
        for line in out.splitlines()[1:-2]:  # the rule always starts in the same column, whatever the counts
            self.assertIn(line[80:86], ("guard ", "schema"), line)
        self.assertTrue(self.line(out, "if value == 'slow'").startswith("TIMED-OUT"))
        self.assertTrue(self.line(out, "if value == 'raise'").startswith("KILLED"))
        self.assertTrue(self.line(out, "isinstance(value, str)").startswith("KILLED"))
        self.assertTrue(self.line(out, "schema / required").startswith("UNDISCOVERED"))
        self.assertTrue(self.line(out, "alternative 1 of 2").startswith("KILLED"))
        self.assertTrue(self.line(out, "alternative 2 of 2").startswith("SURVIVED"))
        self.assertIn("survivors: 2", out)

    def test_a_clean_sweep_exits_zero(self):
        code, out, _ = self.sweep("--only", "if value == 'a'", "--only", "if value == 'raise'")
        self.assertEqual(code, 0)
        self.assertIn("survivors: 0", out)
        self.assertEqual((self.root / "scripts" / "check-inventory.py").read_text(encoding="utf-8"),
                         textwrap.dedent(CHECKER))  # the fixture itself is never touched

    def test_the_private_copy_takes_the_todo_tree_when_there_is_one(self):
        # D02 T01 §22: the checker looks up the sections design/inventory/authoring.json names, so its tests need them.
        with tempfile.TemporaryDirectory() as parent:
            bare = ms.Workspace(self.root, parent)
            self.assertFalse((bare.root / "todo").exists())  # the fixture has no TODO tree, and none is invented
            (self.root / "todo" / "00-x").mkdir(parents=True)
            (self.root / "todo" / "00-x" / "TODO-01-a.md").write_text("## 1. A\n", encoding="utf-8")
            copied = ms.Workspace(self.root, parent)
            self.assertEqual((copied.root / "todo" / "00-x" / "TODO-01-a.md").read_text(encoding="utf-8"), "## 1. A\n")

    def test_a_failing_unmutated_run_stops_the_sweep(self):
        path = self.root / "scripts" / "tests" / "test_check_inventory.py"
        path.write_text(TESTS + "\n\nclass Broken(unittest.TestCase):\n    def test_x(self):\n        self.fail()\n",
                        encoding="utf-8")
        code, out, err = self.sweep()
        self.assertEqual(code, 2)
        self.assertIn("the unmutated run did not pass", err)
        self.assertNotIn("KILLED", out)

    def test_a_run_short_of_its_tests_is_killed_only_when_a_failure_ended_it(self):
        full = {"import_errors": 0, "discovered": 9, "ran": 9, "failures": 0, "errors": 0}
        self.assertEqual(ms.verdict(dict(full, ran=3, failures=1, stopped=True), full), "KILLED")
        self.assertEqual(ms.verdict(dict(full, ran=3, failures=1, stopped=False), full), "UNDISCOVERED")
        self.assertEqual(ms.verdict(dict(full, ran=3), full), "UNDISCOVERED")
        self.assertEqual(ms.verdict(dict(full, discovered=8, ran=1, failures=1, stopped=True), full), "UNDISCOVERED")
        self.assertEqual(ms.verdict(dict(full, import_errors=1, failures=1, stopped=True), full), "UNDISCOVERED")
        self.assertEqual(ms.verdict(dict(full, errors=2), full), "ERRORED")
        self.assertEqual(ms.verdict(full, full), "SURVIVED")

    def test_a_test_whose_subtests_fail_ends_the_run_as_one_failing_test(self):
        # Round 1, finding 1: unittest runs the other subtests of the method it is in, and each failed one was
        # counted as a failing test, which made the count of passing tests negative.
        path = self.root / "scripts" / "tests" / "test_check_inventory.py"
        path.write_text(TESTS.replace(
            '        self.assertEqual(ci.check("a"), ["a"])',
            '        for n in range(3):\n            with self.subTest(n=n):\n'
            '                self.assertEqual(ci.check("a"), ["a"])'), encoding="utf-8")
        code, out, err = self.sweep("--only", "if value == 'a'")
        self.assertEqual(code, 0, err)
        total = out.splitlines()[0].split(" tests pass")[0].split()[-1]
        self.assertTrue(self.line(out, "if value == 'a'").startswith(
            f"KILLED       1 failing, 0 erroring, 0 passing, 0 skipped, 1 of {total} run"),
            self.line(out, "if value == 'a'"))

    def test_a_test_whose_subtests_error_and_fail_is_one_failing_test(self):
        path = self.root / "scripts" / "tests" / "test_check_inventory.py"
        path.write_text(TESTS.replace(
            '        self.assertEqual(ci.check("a"), ["a"])',
            '        with self.subTest(n=0):\n            self.assertEqual(ci.check("a")[0], "a")\n'
            '        with self.subTest(n=1):\n            self.assertEqual(ci.check("a"), ["a"])'), encoding="utf-8")
        code, out, err = self.sweep("--only", "if value == 'a'")
        self.assertEqual(code, 0, err)
        self.assertIn("KILLED       1 failing, 0 erroring, 0 passing, 0 skipped, 1 of ",
                      self.line(out, "if value == 'a'"))


class Shares(Fixture):
    def listed(self, *argv):
        code, out, err = self.sweep("--list", *argv)
        self.assertEqual(code, 0, err)
        return out.splitlines()[:-1]

    def test_four_shares_are_disjoint_and_together_the_whole_list(self):
        whole = self.listed()
        shares = [self.listed("--shard", f"{i}/4") for i in (1, 2, 3, 4)]
        self.assertGreater(len(whole), 8)
        self.assertEqual(sum(len(s) for s in shares), len(whole))
        self.assertEqual(len({name for s in shares for name in s}), len(whole))  # no rule in two shares
        for i, share in enumerate(shares):  # dealt by position, in the order --list prints
            self.assertEqual(share, whole[i::4])
        self.assertLessEqual(max(map(len, shares)) - min(map(len, shares)), 1)

    def test_a_share_that_is_not_one_of_n_is_refused(self):
        for bad in ("0/4", "5/4", "x", "2", "1/0", "-1/4"):
            with self.subTest(bad=bad):
                code, out, err = self.sweep(f"--shard={bad}", "--list")
                self.assertEqual(code, 2)
                self.assertIn("--shard takes I/N", err)
                self.assertEqual(out, "")

    def test_every_share_starts_with_its_own_unmutated_run(self):
        code, out, err = self.sweep("--only", "if value == 'a'", "--only", "if value == 'raise'", "--shard", "2/2")
        self.assertEqual(code, 0, err)
        self.assertTrue(out.splitlines()[0].startswith("unmutated: "), out)
        self.assertTrue(out.splitlines()[0].endswith("1 rules, share 2/2"), out)
        self.assertIn("if value == 'raise'", out)
        self.assertNotIn("if value == 'a'", out)


NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
ONE = ("--only", "if value == 'a'")  # one rule, so a sweep that runs is quick


class Repository(Fixture):
    """The fixture as a git repository of its own, with no hook and no signing of whoever runs the tests."""

    def setUp(self):
        super().setUp()
        self.git("init", "-q")
        (self.root / "README.md").write_text("one\n", encoding="utf-8")
        self.base = self.commit("base")

    def git(self, *args):
        done = subprocess.run(
            ["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
             "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", "-c", f"core.hooksPath={self.root / 'none'}",
             *args], capture_output=True, text=True, encoding="utf-8", timeout=60, creationflags=NO_WINDOW)
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout.strip()

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def change(self, relative):
        path = self.root / relative
        path.write_bytes(path.read_bytes() + b"\n")
        return self.commit(f"change {relative}")


class IfChanged(Repository):
    def test_a_push_that_changed_no_swept_file_removes_nothing(self):
        head = self.change("README.md")
        code, out, err = self.sweep("--if-changed", f"{self.base}..{head}")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, f"sweep skipped: no swept file changed between {self.base} and {head}\n")

    def test_a_change_to_each_swept_file_runs_the_sweep(self):
        self.assertEqual(ms.SWEPT, ("scripts/check-inventory.py", "design/inventory/schema.json",
                                    "scripts/tests/test_check_inventory.py", "scripts/mutation-sweep-inventory.py"))
        before = self.base
        for swept in ms.SWEPT:
            with self.subTest(swept=swept):
                head = self.change(swept)
                code, out, err = self.sweep("--if-changed", f"{before}..{head}", *ONE)
                self.assertEqual(code, 0, err)
                self.assertEqual(out.splitlines()[0], f"sweep runs: {swept} changed between {before} and {head}")
                self.assertTrue(out.splitlines()[1].startswith("unmutated: "), out)
                self.assertIn("survivors: 0", out)
                before = head

    def test_a_base_that_cannot_be_read_runs_the_sweep(self):
        head = self.change("README.md")  # nothing swept changed: only the unreadable base makes it run
        unknown = "1234567890abcdef1234567890abcdef12345678"
        for base, line in (("", f"sweep runs: a commit of '..{head}' cannot be read (it is empty)"),
                           ("0" * 40, f"sweep runs: {'0' * 40} or {head} cannot be read (git diff exit 128)"),
                           (unknown, f"sweep runs: {unknown} or {head} cannot be read (git diff exit 128)")):
            with self.subTest(base=base):
                code, out, err = self.sweep("--if-changed", f"{base}..{head}", *ONE)
                self.assertEqual(code, 0, err)
                self.assertEqual(out.splitlines()[0], line)
                self.assertTrue(out.splitlines()[1].startswith("unmutated: "), out)
                self.assertIn("survivors: 0", out)

    def test_git_that_cannot_run_runs_the_sweep(self):
        head = self.change("README.md")
        real = ms.subprocess.run

        def missing(argv, **kwargs):
            raise FileNotFoundError(argv[0])

        def slow(argv, **kwargs):
            raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
        for fake, name in ((missing, "FileNotFoundError"), (slow, "TimeoutExpired")):
            ms.subprocess.run = fake
            try:
                run, line = ms.changed_between(self.root, f"{self.base}..{head}")
            finally:
                ms.subprocess.run = real
            self.assertTrue(run)
            self.assertEqual(line, f"sweep runs: git could not compare {self.base} and {head} ({name})")

    def test_an_argument_that_is_not_a_span_is_refused(self):
        head = self.change("scripts/check-inventory.py")
        for bad in (head, f"{self.base} {head}", ""):
            with self.subTest(bad=bad):
                code, out, err = self.sweep(f"--if-changed={bad}")
                self.assertEqual(code, 2)
                self.assertIn("--if-changed takes one argument, <base>..<head>", err)
                self.assertEqual(out, "")

    def test_a_commit_that_reads_as_an_option_is_never_given_to_git(self):
        head = self.change("README.md")
        run, line = ms.changed_between(self.root, f"--output=x..{head}")
        self.assertTrue(run)
        self.assertIn("cannot be read", line)
        self.assertFalse((self.root / "x").exists())


class Workflow(Repository):
    """The `sweep` job of .github/workflows/ci.yml, read as text, and its command as each event renders it."""

    COMMAND = ('python -B scripts/mutation-sweep-inventory.py --shard ${{ matrix.share }}/4 --if-changed '
               '"${{ github.event.before || github.event.pull_request.base.sha }}..${{ github.sha }}"')

    def job(self):
        text = (SCRIPTS.parent / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        jobs = re.split(r"(?m)^  (?=[a-z][a-z-]*:\s*$)", text.split("\njobs:\n", 1)[1])
        found = [j for j in jobs if j.startswith("sweep:")]
        self.assertEqual(len(found), 1)
        return found[0]

    def test_the_job_runs_four_shares_on_the_whole_history(self):
        job = self.job()
        for want in ("runs-on: windows-latest", "fail-fast: false", "share: [1, 2, 3, 4]",
                     "name: sweep (${{ matrix.share }}/4)", "fetch-depth: 0", "actions/setup-python@",
                     "python -m pip install -r scripts/requirements.txt", f"run: {self.COMMAND}\n"):
            self.assertIn(want, job, want)
        self.assertEqual(job.count("mutation-sweep-inventory.py --shard"), 1)

    def render(self, context):
        def value(match):
            for name in match.group(1).split("||"):
                if context.get(name.strip()):
                    return str(context[name.strip()])
            return ""  # as GitHub renders an expression that is null
        return re.sub(r"\$\{\{(.*?)\}\}", value, self.COMMAND)

    def test_each_event_gives_the_tool_one_argument_it_can_act_on(self):
        head = self.change("README.md")
        events = {
            "push": ({"github.event.before": self.base}, "sweep skipped: no swept file changed between"),
            "pull_request": ({"github.event.pull_request.base.sha": self.base},
                             "sweep skipped: no swept file changed between"),
            "workflow_dispatch": ({}, f"sweep runs: a commit of '..{head}' cannot be read (it is empty)"),
        }
        for event, (context, line) in events.items():
            with self.subTest(event=event):
                argv = shlex.split(self.render(dict(context, **{"matrix.share": 1, "github.sha": head})))[3:]
                self.assertEqual(argv[:3], ["--shard", "1/4", "--if-changed"])
                self.assertEqual(len(argv), 4, argv)  # the span is one argument whatever the event left empty
                self.assertTrue(argv[3].endswith(f"..{head}"), argv)
                code, out, err = self.sweep(*argv, *ONE)
                self.assertEqual(code, 0, err)
                self.assertTrue(out.splitlines()[0].startswith(line), out)
                self.assertEqual("unmutated: " in out, event == "workflow_dispatch", out)


if __name__ == "__main__":
    unittest.main()
