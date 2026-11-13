# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/mutation-sweep-inventory.py over a tiny fixture checker, schema and test file (D02 T01 §27): each kind of
rule is enumerated, and a killed, a surviving, an erroring, a timed-out and an undiscovered removal are reported
apart, with a failing unmutated run stopping the sweep."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
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
        self.assertTrue(self.line(out, "if value == 'a'").startswith(
            f"KILLED       1 failing, 0 erroring, {int(total) - 1} passing, 0 skipped, {total} of {total} run"),
            self.line(out, "if value == 'a'"))
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


if __name__ == "__main__":
    unittest.main()
