#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Prove that every rule of the inventory checker is held by a test: remove each rule on its own and run the
checker's tests (D02 T01 §27).

    python -B scripts/mutation-sweep-inventory.py            # the whole sweep; ends with `survivors: N`
    python -B scripts/mutation-sweep-inventory.py --list     # the rules it would remove, one per line
    python -B scripts/mutation-sweep-inventory.py --only "guard check-inventory.py:812"
    python -B scripts/mutation-sweep-inventory.py --shard 2/4                  # the second of four shares of the rules
    python -B scripts/mutation-sweep-inventory.py --if-changed <base>..<head>  # only when a swept file changed

A rule is one guard of scripts/check-inventory.py (an `if` whose body adds a problem, raises `Unreadable` or returns
a refusal), one keyword of design/inventory/schema.json the checker's validator reads, one entry of a `properties`
map, or one top-level alternative of a `pattern`. The alternation bars inside a top-level alternative define that
family's exemptions and are not removed one by one (noHost alone holds over 4,000).

Each removal runs in a private copy of scripts/, design/inventory/ and todo/, on disk, in a fresh process, so a test that
reads the schema itself or starts the checker as a subprocess sees it, and nothing of one removal reaches the next.
An unmutated run comes first and must pass in full, or the sweep exits 2 having removed nothing. A removal is killed
only when a test fails with every test discovered, and its run stops at that first failure, which is all the verdict
needs (D02 T01 §38); one whose tests only error, that discovers fewer tests, that runs out of time or whose process
dies is reported as such. Each child runs in a process tree with a time limit and an
output limit (scripts/lib/process_tree.py). Exit 0 when every rule is killed, 1 otherwise, 2 when it cannot start.

One line per rule: the outcome, then how its tests ended and how many ran, then the rule:

    KILLED       1 failing, 0 erroring, 57 passing, 0 skipped, 58 of 133 run     guard check-inventory.py:339 if ...

so the record of a sweep shows for each removal that every test was discovered, and for one that was not killed that
every test ran, not only that none failed.

CI runs the sweep as the four `sweep` shares of .github/workflows/ci.yml (D02 T01 §38). `--shard <i>/<n>` deals the
rules, in the order `--list` prints them, to `n` shares by position, and each share starts with its own unmutated
run. `--if-changed <base>..<head>` is one argument: when `git diff --name-only <base> <head>` names none of the swept
files (SWEPT) it prints `sweep skipped: ...` and exits 0 having removed nothing; when it names one, or when either
commit cannot be read (an empty base, as a pull request or a manual run gives; the all-zero base of a first push; a
commit that is not in the clone; git failing), it prints why and runs the sweep.
"""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import process_tree  # noqa: E402  (scripts/lib is put on the path just above)

CHECKER = Path("scripts") / "check-inventory.py"
SCHEMA = Path("design") / "inventory" / "schema.json"
TESTS = Path("scripts") / "tests"
PATTERN = "test_check_inventory.py"
# The keywords the checker's validator reads (scripts/check-inventory.py, validate): removing one removes its rule.
KEYWORDS = ("type", "const", "enum", "minLength", "maxLength", "pattern", "required", "additionalProperties",
            "dependentRequired", "not", "allOf", "items", "minimum", "$ref", "if", "then")
OUTPUT_LIMIT = 50 * 1024 * 1024  # a test run that writes more than this is stopped
# Functions whose every non-None return is a refusal (what they found), not a problem list.
REFUSERS = ("unfinished_call",)
# The files whose change can add a rule no test holds or drop the test that held one: what --if-changed looks for.
SWEPT = tuple(p.as_posix() for p in (CHECKER, SCHEMA, TESTS / PATTERN, Path("scripts") / "mutation-sweep-inventory.py"))
SHARD = re.compile(r"([0-9]+)/([0-9]+)")
GIT_SECONDS = 60  # one `git diff --name-only` may take this long
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class Rule:
    """One rule the sweep removes: its name, the file it lives in, and how to write that file without it."""

    def __init__(self, name, path, remove):
        self.name, self.path, self.remove = name, path, remove


def adds_refusal(body, refuser=False):
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if refuser and isinstance(node, ast.Return) and node.value is not None and not (
                isinstance(node.value, ast.Constant) and node.value.value is None):
            return True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "append" \
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "problems":
            return True
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id == "problems":
            return True
        if isinstance(node, ast.Raise) and node.exc is not None and "Unreadable" in ast.unparse(node.exc):
            return True
        if isinstance(node, ast.Return) and isinstance(node.value, (ast.List, ast.BinOp)) and (
                not isinstance(node.value, ast.List) or node.value.elts):
            return True
    return False


def guard_rules(source):
    """Every guard of the checker: its condition is replaced with False in the source text, the rest kept as is."""
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    rules, tree = [], ast.parse(source)
    refusing = {id(n) for f in ast.walk(tree) if isinstance(f, ast.FunctionDef) and f.name in REFUSERS
                for n in ast.walk(f)}
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and adds_refusal(node.body, id(node) in refusing):
            test = node.test
            start = offsets[test.lineno - 1] + len(lines[test.lineno - 1].encode("utf-8")[:test.col_offset]
                                                   .decode("utf-8"))
            end = offsets[test.end_lineno - 1] + len(lines[test.end_lineno - 1].encode("utf-8")[:test.end_col_offset]
                                                     .decode("utf-8"))
            text = " ".join(ast.unparse(test).split())

            def remove(src, start=start, end=end):
                return src[:start] + "False" + src[end:]
            rules.append((node.lineno, Rule(f"guard {CHECKER.name}:{node.lineno} if {text[:90]}", CHECKER, remove)))
    return [r for _, r in sorted(rules, key=lambda x: x[0])]


def top_alternatives(pattern):
    """The pattern's top-level alternatives (outside groups and classes), as written."""
    out, cur, depth, in_class, i = [], "", 0, False, 0
    while i < len(pattern):
        c = pattern[i]
        if c == "\\":
            cur += pattern[i:i + 2]
            i += 2
            continue
        if in_class:
            in_class = c != "]"
        elif c == "[":
            in_class = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "|" and depth == 0:
            out.append(cur)
            cur = ""
            i += 1
            continue
        cur += c
        i += 1
    return out + [cur]


def schema_rules(schema):
    """Every keyword the validator reads, every `properties` entry and every top-level pattern alternative."""
    rules = []

    def at(doc, path):
        for key in path:
            doc = doc[key]
        return doc

    def rule(name, path, edit):
        def remove(text, path=path, edit=edit):
            doc = json.loads(text)
            edit(at(doc, path))
            return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        rules.append(Rule(f"schema {name}", SCHEMA, remove))

    def walk(node, path):
        if isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, path + [i])
            return
        if not isinstance(node, dict):
            return
        where = "/" + "/".join(str(p) for p in path)
        for key in KEYWORDS:
            if key in node:
                rule(f"{where} {key}", path, lambda d, key=key: d.pop(key))
        if isinstance(node.get("properties"), dict):
            for name in node["properties"]:
                rule(f"{where} properties.{name}", path, lambda d, name=name: d["properties"].pop(name))
        if isinstance(node.get("pattern"), str):
            alts = top_alternatives(node["pattern"])
            if len(alts) > 1:
                for i, alt in enumerate(alts):
                    rest = "|".join(a for j, a in enumerate(alts) if j != i)
                    rule(f"{where} pattern alternative {i + 1} of {len(alts)}: {alt[:60]}", path,
                         lambda d, rest=rest: d.__setitem__("pattern", rest))
        for key, value in node.items():
            walk(value, path + [key])
    walk(schema, [])
    return rules


def rules_of(root):
    # The raw text, line endings as they are: a guard's place is counted in the text its removal is written into.
    return guard_rules((root / CHECKER).read_bytes().decode("utf-8")) + \
        schema_rules(json.loads((root / SCHEMA).read_text(encoding="utf-8")))


def changed_between(root, span):
    """(run, line) for `--if-changed <base>..<head>`: False only when git shows that no swept file changed."""
    base, _, head = span.partition("..")
    if not base or not head or base.startswith("-") or head.startswith("-"):
        return True, f"sweep runs: a commit of {span!r} cannot be read (it is empty)"
    try:
        done = subprocess.run(["git", "-C", str(root), "diff", "--name-only", base, head, "--"], capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=GIT_SECONDS,
                              creationflags=NO_WINDOW)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return True, f"sweep runs: git could not compare {base} and {head} ({type(exc).__name__})"
    if done.returncode != 0:
        return True, f"sweep runs: {base} or {head} cannot be read (git diff exit {done.returncode})"
    named = [name for name in done.stdout.splitlines() if name in SWEPT]
    if named:
        return True, f"sweep runs: {', '.join(named)} changed between {base} and {head}"
    return False, f"sweep skipped: no swept file changed between {base} and {head}"


class StopAtFailure(unittest.TextTestResult):
    """Ends a run at its first failing test: one failure is all a removal's verdict needs. An error does not end
    it, because a removal whose tests only error is not killed, and a later test of the same run may still fail.
    unittest finishes the test method it is in, so a test whose subtests fail runs its other subtests first; the
    counts are of tests, never of subtests (run_tests), so such a test is one failing test."""

    stopped_on_failure = False

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stopped_on_failure = True
        self.stop()

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None and issubclass(err[0], test.failureException):
            self.stopped_on_failure = True
            self.stop()


def run_tests(copy_root, result_path, pattern):
    """In the child: discover and run the checker's tests in the copy, and write what happened as JSON."""
    loader = unittest.TestLoader()
    suite = loader.discover(str(copy_root / TESTS), pattern=pattern, top_level_dir=str(copy_root / TESTS))
    discovered = suite.countTestCases()
    with open(Path(result_path).with_suffix(".log"), "w", encoding="utf-8") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=1, resultclass=StopAtFailure).run(suite)
    failed_import = sum(1 for test, _ in result.errors if type(test).__name__ == "_FailedTest")

    def tests(entries):
        # The tests behind a result's entries: a subtest stands for the test it is part of, so a test with three
        # failing subtests is one failing test, as `ran` and `discovered` count it (round 1, finding 1).
        return {getattr(test, "test_case", test).id() for test, _ in entries}
    failing = tests(result.failures)
    erroring = tests(result.errors) - failing  # a test that both fails and errors is a failing test
    skipped = tests(result.skipped) - failing - erroring
    Path(result_path).write_text(json.dumps({
        "discovered": discovered, "ran": result.testsRun, "failures": len(failing),
        "errors": len(erroring) - failed_import, "import_errors": failed_import + len(loader.errors),
        "skipped": len(skipped), "stopped": result.stopped_on_failure,
        # What neither failed, errored nor was skipped; an expected failure or an unexpected success is not a pass.
        "passed": result.testsRun - len(failing) - len(erroring) - len(skipped)
        - len(result.expectedFailures) - len(result.unexpectedSuccesses)}), encoding="utf-8")
    return 0


def counts_text(counts):
    """How one run's tests ended and how many ran, as a sweep line and its record show it."""
    return (f"{counts['failures']} failing, {counts['errors']} erroring, {counts['passed']} passing, "
            f"{counts['skipped']} skipped, {counts['ran']} of {counts['discovered']} run")


class Workspace:
    """A private copy of scripts/ and design/inventory/ a removal is written into, one run at a time."""

    def __init__(self, root, parent):
        self.root = Path(tempfile.mkdtemp(prefix="sweep-", dir=parent))
        shutil.copytree(root / "scripts", self.root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(root / "design" / "inventory", self.root / "design" / "inventory")
        if (root / "todo").is_dir():
            # The checker looks the sections of design/inventory/authoring.json up in the TODO tree (D02 T01 §22).
            shutil.copytree(root / "todo", self.root / "todo")
        self.lock = threading.Lock()

    def run(self, rule, pattern, timeout):
        """(outcome, counts) for one removal (None: the unmutated run); the copy is put back afterwards."""
        target = self.root / rule.path if rule else None
        pristine = target.read_bytes() if target else None
        try:
            if rule:
                target.write_bytes(rule.remove(pristine.decode("utf-8")).encode("utf-8"))
            result = self.root / "result.json"
            result.unlink(missing_ok=True)
            out = self.root / "run.out"
            outcome = process_tree.run(
                [sys.executable, "-B", str(self.root / "scripts" / "mutation-sweep-inventory.py"), "--run-tests",
                 str(self.root), "--result", str(result), "--pattern", pattern],
                cwd=str(self.root), stdout_path=str(out), stderr_path=str(out), timeout=timeout,
                max_bytes=OUTPUT_LIMIT, watched=[str(result.with_suffix(".log"))])
            if outcome.stopped:
                return outcome.stopped, None, outcome.seconds
            if outcome.exit != 0 or not result.is_file():
                return "crashed", None, outcome.seconds
            return "ran", json.loads(result.read_text(encoding="utf-8")), outcome.seconds
        finally:
            if target:
                target.write_bytes(pristine)


def verdict(counts, baseline):
    if counts["import_errors"] or counts["discovered"] < baseline["discovered"]:
        return "UNDISCOVERED"
    if counts["failures"] and (counts.get("stopped") or counts["ran"] == counts["discovered"]):
        return "KILLED"  # every test was discovered; the run ended at its first failure, so fewer ran
    if counts["ran"] < counts["discovered"]:
        return "UNDISCOVERED"
    if counts["errors"]:
        return "ERRORED"
    return "SURVIVED"


def main(argv=None, root=ROOT):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--list", action="store_true", help="print the rules and stop")
    ap.add_argument("--only", action="append", default=[], help="remove only the rules whose name holds this text")
    ap.add_argument("--shard", metavar="I/N", help="remove share I of N of the rules (1 to N)")
    ap.add_argument("--if-changed", metavar="BASE..HEAD",
                    help="run only when a swept file changed between the two commits, or when one cannot be read")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=None, help="seconds one run may take (default: 5x unmutated)")
    ap.add_argument("--pattern", default=PATTERN, help=argparse.SUPPRESS)
    ap.add_argument("--run-tests", type=Path, help=argparse.SUPPRESS)
    ap.add_argument("--result", type=Path, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if args.run_tests:
        return run_tests(args.run_tests, args.result, args.pattern)
    root = Path(root)
    share = SHARD.fullmatch(args.shard or "1/1")
    if not share or not 1 <= int(share.group(1)) <= int(share.group(2)):
        print("mutation-sweep: --shard takes I/N with 1 <= I <= N, as in 2/4", file=sys.stderr)
        return 2
    if args.if_changed is not None:
        if ".." not in args.if_changed:
            print("mutation-sweep: --if-changed takes one argument, <base>..<head>, as in 1a2b3c..4d5e6f",
                  file=sys.stderr)
            return 2
        run, line = changed_between(root, args.if_changed)
        print(line, flush=True)
        if not run:
            return 0
    try:
        rules = rules_of(root)
    except (OSError, SyntaxError, ValueError) as exc:
        print(f"mutation-sweep: the checker or the schema cannot be read ({exc})", file=sys.stderr)
        return 2
    if args.only:
        rules = [r for r in rules if any(o in r.name for o in args.only)]
    rules = rules[int(share.group(1)) - 1::int(share.group(2))]  # dealt by position, in the order --list prints
    if args.list:
        for r in rules:
            print(r.name)
        print(f"rules: {len(rules)}")
        return 0
    with tempfile.TemporaryDirectory(prefix="mutation-sweep-") as parent:
        spaces = [Workspace(root, parent) for _ in range(max(1, args.workers))]
        state, counts, seconds = spaces[0].run(None, args.pattern, args.timeout or 3600)
        if state != "ran" or counts["failures"] or counts["errors"] or counts["import_errors"] \
                or not counts["discovered"]:
            print(f"mutation-sweep: the unmutated run did not pass ({state}, {counts}); nothing was removed",
                  file=sys.stderr)
            return 2
        baseline, timeout = counts, args.timeout or max(120.0, 5 * seconds)
        print(f"unmutated: {baseline['discovered']} tests pass in {seconds:.0f} s ({counts_text(baseline)}); "
              f"{len(rules)} rules" + (f", share {args.shard}" if args.shard else ""), flush=True)
        free = list(spaces)
        pool_lock = threading.Lock()

        def one(rule):
            with pool_lock:
                space = free.pop()
            try:
                return rule, space.run(rule, args.pattern, timeout)
            finally:
                with pool_lock:
                    free.append(space)
        tally = {}
        with ThreadPoolExecutor(max_workers=len(spaces)) as pool:
            for rule, (state, counts, _) in pool.map(one, rules):
                if state == "ran":
                    word = verdict(counts, baseline)
                    detail = counts_text(counts)
                else:
                    word = {"time limit": "TIMED-OUT", "output limit": "FLOODED"}.get(state, "CRASHED")
                    detail = state
                tally[word] = tally.get(word, 0) + 1
                print(f"{word:<12} {detail:<66} {rule.name}", flush=True)
    survivors = tally.get("SURVIVED", 0)
    others = sum(n for w, n in tally.items() if w not in ("KILLED", "SURVIVED"))
    print(f"rules: {len(rules)}, killed: {tally.get('KILLED', 0)}, other outcomes: {others}")
    print(f"survivors: {survivors}")
    return 0 if survivors == 0 and others == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
