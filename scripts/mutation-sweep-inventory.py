#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Prove that every rule of the inventory checker is held by a test: remove each rule on its own and run the
checker's tests (D02 T01 §27).

    python -B scripts/mutation-sweep-inventory.py            # the whole sweep; ends with `survivors: N`
    python -B scripts/mutation-sweep-inventory.py --list     # the rules it would remove, one per line
    python -B scripts/mutation-sweep-inventory.py --only "guard check-inventory.py:812"

A rule is one guard of scripts/check-inventory.py (an `if` whose body adds a problem, raises `Unreadable` or returns
a refusal), one keyword of design/inventory/schema.json the checker's validator reads, one entry of a `properties`
map, or one top-level alternative of a `pattern`. The alternation bars inside a top-level alternative define that
family's exemptions and are not removed one by one (noHost alone holds over 4,000).

Each removal runs in a private copy of scripts/ and design/inventory/, on disk, in a fresh process, so a test that
reads the schema itself or starts the checker as a subprocess sees it, and nothing of one removal reaches the next.
An unmutated run comes first and must pass in full, or the sweep exits 2 having removed nothing. A removal is killed
only when a test fails with every test discovered; one whose tests only error, that discovers fewer tests, that runs
out of time or whose process dies is reported as such. Each child runs in a process tree with a time limit and an
output limit (scripts/lib/process_tree.py). Exit 0 when every rule is killed, 1 otherwise, 2 when it cannot start.
"""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
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


def run_tests(copy_root, result_path, pattern):
    """In the child: discover and run the checker's tests in the copy, and write what happened as JSON."""
    loader = unittest.TestLoader()
    suite = loader.discover(str(copy_root / TESTS), pattern=pattern, top_level_dir=str(copy_root / TESTS))
    discovered = suite.countTestCases()
    with open(Path(result_path).with_suffix(".log"), "w", encoding="utf-8") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=1).run(suite)
    failed_import = sum(1 for test, _ in result.errors if type(test).__name__ == "_FailedTest")
    Path(result_path).write_text(json.dumps({
        "discovered": discovered, "ran": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors) - failed_import, "import_errors": failed_import + len(loader.errors),
        "skipped": len(result.skipped)}), encoding="utf-8")
    return 0


class Workspace:
    """A private copy of scripts/ and design/inventory/ a removal is written into, one run at a time."""

    def __init__(self, root, parent):
        self.root = Path(tempfile.mkdtemp(prefix="sweep-", dir=parent))
        shutil.copytree(root / "scripts", self.root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(root / "design" / "inventory", self.root / "design" / "inventory")
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
    if counts["import_errors"] or counts["discovered"] < baseline["discovered"] or counts["ran"] < counts["discovered"]:
        return "UNDISCOVERED"
    if counts["failures"]:
        return "KILLED"
    if counts["errors"]:
        return "ERRORED"
    return "SURVIVED"


def main(argv=None, root=ROOT):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--list", action="store_true", help="print the rules and stop")
    ap.add_argument("--only", action="append", default=[], help="remove only the rules whose name holds this text")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=None, help="seconds one run may take (default: 5x unmutated)")
    ap.add_argument("--pattern", default=PATTERN, help=argparse.SUPPRESS)
    ap.add_argument("--run-tests", type=Path, help=argparse.SUPPRESS)
    ap.add_argument("--result", type=Path, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if args.run_tests:
        return run_tests(args.run_tests, args.result, args.pattern)
    root = Path(root)
    try:
        rules = rules_of(root)
    except (OSError, SyntaxError, ValueError) as exc:
        print(f"mutation-sweep: the checker or the schema cannot be read ({exc})", file=sys.stderr)
        return 2
    if args.only:
        rules = [r for r in rules if any(o in r.name for o in args.only)]
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
        print(f"unmutated: {baseline['discovered']} tests pass in {seconds:.0f} s; {len(rules)} rules", flush=True)
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
                    detail = f"{counts['failures']} failing, {counts['errors']} erroring"
                else:
                    word = {"time limit": "TIMED-OUT", "output limit": "FLOODED"}.get(state, "CRASHED")
                    detail = state
                tally[word] = tally.get(word, 0) + 1
                print(f"{word:<12} {detail:<24} {rule.name}", flush=True)
    survivors = tally.get("SURVIVED", 0)
    others = sum(n for w, n in tally.items() if w not in ("KILLED", "SURVIVED"))
    print(f"rules: {len(rules)}, killed: {tally.get('KILLED', 0)}, other outcomes: {others}")
    print(f"survivors: {survivors}")
    return 0 if survivors == 0 and others == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
