# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/measure-modes.py: every arm is built in its own clone, gated and reviewed blind, fixed until approved, and
resumed by stage (D00 T03 §36).

No test starts a real session or a real review: the measured repository is a fixture whose `todo-graph.py`, gates,
prompt builder and dispatcher are fakes, and `claude` on PATH is a fake that commits a file and prints a JSON reply.
Every fake writes a bounded amount, and every process the harness starts runs in a process tree it stops.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("measure_modes", SCRIPTS / "measure-modes.py")
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_process_tree import alive

# The fixture repository's tools. Each reads the test's control folder from MEASURE_FAKE.
TODO_GRAPH = textwrap.dedent('''
    import json, os, sys, time
    from pathlib import Path
    control = Path(os.environ["MEASURE_FAKE"])
    (control / "gate-calls").mkdir(exist_ok=True)
    (control / "gate-calls" / f"{time.time_ns()}-{os.getpid()}.txt").write_text(" ".join(sys.argv[1:]) + "\\n" + os.getcwd())
    if sys.argv[1] == "resolve":
        sections = json.loads(Path("sections.json").read_text(encoding="utf-8"))
        found = sections.get(sys.argv[2])
        if found is None:
            sys.exit(1)
        if found.get("exit", 0):
            sys.exit(found["exit"])
        print(json.dumps({"skill_arg": sys.argv[2], "title": found["title"], "path": "todo/x.md", "body": found["body"]}))
    elif sys.argv[1:3] == ["query", "stats"]:
        verified = control / "verified.txt"
        print(json.dumps({"total": 999, "verified": int(verified.read_text()) if verified.exists() else 10}))
    else:
        print("valid: 1 sections" if sys.argv[1] == "validate" else "plan current")
''')
RUN_TESTS = textwrap.dedent('''
    import os, sys, time
    from pathlib import Path
    control = Path(os.environ["MEASURE_FAKE"])
    (control / "gate-calls").mkdir(exist_ok=True)
    (control / "gate-calls" / f"{time.time_ns()}-{os.getpid()}.txt").write_text("tests\\n" + os.getcwd())
    if Path(".fake/tests-hang").exists():
        time.sleep(300)
    if Path(".fake/tests-fail").exists():
        print("FAILED (failures=1)")
        sys.exit(1)
    print("Ran 1 tests")
    print("OK")
''')
REVIEW_PROMPT = textwrap.dedent('''
    import sys
    from pathlib import Path
    args = sys.argv[1:]
    out = Path(args[args.index("--out") + 1])
    out.write_text("Review the range " + args[args.index("--base") + 1] + ".." + args[args.index("--candidate") + 1]
                   + " for section " + args[args.index("--ref") + 1] + ". Purpose: " + args[args.index("--purpose") + 1])
''')
REVIEW_DISPATCH = textwrap.dedent('''
    import json, os, sys
    from pathlib import Path
    control = Path(os.environ["MEASURE_FAKE"])
    model = Path(".fake/model").read_text().strip() if Path(".fake/model").exists() else "none"
    plan = json.loads((control / "reviews.json").read_text())
    replies = plan.get(model, plan.get("default", ["approve"]))
    counter = control / ("review-count-" + Path.cwd().name)
    n = int(counter.read_text()) if counter.exists() else 0
    counter.write_text(str(n + 1))
    (control / "prompts").mkdir(exist_ok=True)
    args = sys.argv[1:]
    (control / "prompts" / f"{Path.cwd().name}-{n}.md").write_text(Path(args[args.index("--prompt") + 1]).read_text())
    reply = replies[min(n, len(replies) - 1)]
    if reply == "fail":
        print(json.dumps({"reviewer": None, "failover": "astra: timed out", "review": ""}))
        sys.exit(1)
    if reply == "malformed":
        print("not json {")
        sys.exit(0)
    if reply == "empty":
        sys.exit(0)
    if reply == "nohighest":
        print(json.dumps({"reviewer": "astra", "review": "1. P2 something\\nOVERALL: needs-attention"}))
        sys.exit(0)
    if reply == "approve":
        text = "LENS correctness: clean\\nHIGHEST: none\\nOVERALL: approve"
    else:
        text = f"1. **{reply}, scripts/x.py:1:** a finding\\n2. P3 a nit\\nHIGHEST: {reply}\\nOVERALL: needs-attention"
    print(json.dumps({"reviewer": "astra", "review": text, "highest": reply}))
''')
# The fake headless session. Its behaviour per call comes from claude.json: {"<model>": [action, ...], "default": [...]}
FAKE_CLAUDE = textwrap.dedent('''
    import json, os, subprocess, sys, time
    from pathlib import Path
    control = Path(os.environ["MEASURE_FAKE"])
    argv = sys.argv[1:]
    model = argv[argv.index("--model") + 1]
    stdin = sys.stdin.buffer.read().decode("utf-8")  # the harness writes the task as UTF-8, as claude reads it
    started = time.time()
    plan = json.loads((control / "claude.json").read_text())
    actions = plan.get(model, plan.get("default", [{}]))
    counter = control / ("claude-count-" + Path.cwd().name)
    n = int(counter.read_text()) if counter.exists() else 0
    counter.write_text(str(n + 1))
    act = actions[min(n, len(actions) - 1)]
    Path(".fake").mkdir(exist_ok=True)
    Path(".fake/model").write_text(model)
    if act.get("child"):
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
        (control / f"child-{Path.cwd().name}.pid").write_text(str(child.pid))
    if act.get("flood"):
        for _ in range(256):  # at most 16 MB
            sys.stdout.write("x" * 65536)
            sys.stdout.flush()
            time.sleep(0.01)
    time.sleep(act.get("sleep", 0))
    for name in ("tests-fail", "tests-hang"):
        if act.get(name.replace("-", "_")):
            Path(".fake/" + name).write_text("1")
        elif act.get("clear"):
            Path(".fake/" + name).unlink(missing_ok=True)
    Path(f"work-{n}.txt").write_text(stdin[:200])
    if act.get("commit", True):
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-q", "-m", f"work {n}"], check=True)
    if act.get("untracked"):
        Path("left-behind.txt").write_text("x")
    ended = time.time()
    (control / "calls").mkdir(exist_ok=True)
    (control / "calls" / f"{Path.cwd().name}-{n}.json").write_text(json.dumps(
        {"argv": argv, "stdin": stdin, "cwd": os.getcwd(), "start": started, "end": ended, "model": model}))
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "num_turns": 3,
                      "duration_ms": 1000, "total_cost_usd": act.get("cost", 1.25),
                      "modelUsage": {"claude-" + model: {"inputTokens": 10, "outputTokens": 20,
                                                         "cacheReadInputTokens": 30, "cacheCreationInputTokens": 40,
                                                         "costUSD": act.get("cost", 1.25)}}}))
''')


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.control = self.tmp / "control"
        self.work = self.tmp / "work"
        self.bin = self.tmp / "bin"
        for folder in (self.repo / "scripts", self.control, self.bin):
            folder.mkdir(parents=True)
        (self.repo / "scripts" / "todo-graph.py").write_text(TODO_GRAPH)
        (self.repo / "scripts" / "run-tests.py").write_text(RUN_TESTS)
        (self.repo / "scripts" / "review-prompt.py").write_text(REVIEW_PROMPT)
        (self.repo / "scripts" / "review-dispatch.py").write_text(REVIEW_DISPATCH)
        self.sections({"D00 T01 §1": {"title": "One", "body": "BODY ONE AT BASE"},
                       "D00 T01 §2": {"title": "Two", "body": "BODY TWO AT BASE"},
                       "D00 T01 §3": {"title": "Three", "body": "stamped", "exit": 3}})
        (self.bin / "fake_claude.py").write_text(FAKE_CLAUDE)
        if os.name == "nt":
            (self.bin / "claude.cmd").write_text(f'@"{sys.executable}" "%~dp0fake_claude.py" %*\r\n')
        else:
            launcher = self.bin / "claude"
            launcher.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$(dirname "$0")/fake_claude.py" "$@"\n')
            launcher.chmod(0o755)
        env = {"MEASURE_FAKE": str(self.control), "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
               "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@example.invalid"}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.assertEqual(Path(shutil.which("claude")).parent, self.bin)  # never a real session
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.repo)], check=True)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.base = self.git("rev-parse", "HEAD")
        self.claude_plan({"default": [{}]})
        self.reviews({"default": ["approve"]})

    def tearDown(self):
        measure.remove_tree(self.tmp)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True,
                              text=True).stdout.strip()

    def sections(self, sections):
        (self.repo / "sections.json").write_text(json.dumps(sections), encoding="utf-8")

    def claude_plan(self, plan):
        (self.control / "claude.json").write_text(json.dumps(plan))

    def reviews(self, plan):
        (self.control / "reviews.json").write_text(json.dumps(plan))

    def run_main(self, *extra, sections=("D00 T01 §1",), arms=measure.ARMS):
        argv = ["run", "--work", str(self.work), "--repo", str(self.repo), "--base", self.base]
        for ref in sections:
            argv += ["--section", ref]
        return measure.main(argv + list(extra), arms=arms)

    def results(self):
        return json.loads((self.work / "results.json").read_text(encoding="utf-8"))

    def calls(self):
        folder = self.control / "calls"
        return [json.loads(p.read_text()) for p in sorted(folder.glob("*.json"))] if folder.is_dir() else []

    def gate_calls(self):
        folder = self.control / "gate-calls"
        return [p.read_text().splitlines()[0] for p in folder.glob("*.txt")] if folder.is_dir() else []

    def run_of(self, arm):
        return next(r for r in self.results()["runs"].values() if r["arm"] == arm)


class ArmTable(unittest.TestCase):
    def test_the_two_arms(self):
        arms = measure.load_arms(measure.ARMS)
        self.assertEqual([a.name for a in arms], ["opus-alone", "fable-alone"])
        self.assertEqual([a.model for a in arms], ["opus", "fable"])

    def test_a_duplicate_name_is_refused(self):
        row = measure.Arm("opus-alone", "opus", True, "x")
        with self.assertRaisesRegex(measure.Refused, "twice"):
            measure.load_arms([row, row])

    def test_an_empty_table_is_refused(self):
        with self.assertRaises(measure.Refused):
            measure.load_arms([])


class ReviewParsing(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def parse(self, exit_code, text, stopped=None):
        path = self.tmp / "out.json"
        path.write_text(text, encoding="utf-8")
        return measure.parse_review(exit_code, stopped, path)

    def test_a_review_with_counts(self):
        reply = {"reviewer": "astra", "review": "1. **P1, a.py:1:** x\n2. P2 y\n3. P2 z\n- P3 w\nHIGHEST: P1\n"
                                                "OVERALL: needs-attention"}
        verdict = self.parse(0, json.dumps(reply))
        self.assertEqual((verdict["reviewed"], verdict["highest"], verdict["p1"], verdict["p2"], verdict["p3"],
                          verdict["overall"]), (True, "P1", 1, 2, 1, "needs-attention"))

    def test_none_is_approval_material(self):
        verdict = self.parse(0, json.dumps({"reviewer": "astra", "review": "HIGHEST: none\nOVERALL: approve"}))
        self.assertEqual(verdict["highest"], "none")

    def test_every_non_review_is_unreviewed(self):
        cases = {"failed": (1, json.dumps({"reviewer": None, "failover": "timed out"})),
                 "malformed": (0, "not json {"), "empty": (0, ""),
                 "no highest": (0, json.dumps({"reviewer": "astra", "review": "1. P2 x\nOVERALL: needs-attention"})),
                 "refused": (2, ""), "not an object": (0, "[1]")}
        for name, (code, text) in cases.items():
            with self.subTest(name):
                self.assertFalse(self.parse(code, text)["reviewed"])
        self.assertFalse(self.parse(0, "{}", stopped="time limit")["reviewed"])


class Sections(Fixture):
    def test_unknown_and_stamped_sections_are_refused_before_any_session(self):
        for ref in ("D09 T09 §9", "D00 T01 §3"):
            with self.subTest(ref):
                self.assertEqual(self.run_main(sections=(ref,)), 2)
                self.assertEqual(self.calls(), [])
                self.assertFalse((self.work / "results.json").exists())
                self.assertFalse((self.work / "base").exists())

    def test_every_arm_gets_the_section_as_the_base_commit_has_it(self):
        self.sections({"D00 T01 §1": {"title": "One", "body": "BODY CHANGED LATER"}})
        self.git("commit", "-q", "-am", "later")
        self.assertEqual(self.run_main(), 0)
        stdins = [c["stdin"] for c in self.calls()]
        self.assertEqual(len(stdins), 2)
        task = self.results()["tasks"]["D00 T01 §1"]
        self.assertIn("BODY ONE AT BASE", task)
        self.assertNotIn("CHANGED", task)
        for stdin in stdins:
            self.assertTrue(stdin.startswith(task))

    def test_a_section_named_twice_is_refused(self):
        self.assertEqual(self.run_main(sections=("D00 T01 §1", "D00 T01 §1")), 2)


class Runs(Fixture):
    def test_each_arm_in_its_own_clone_with_the_record(self):
        self.assertEqual(self.run_main("--budget", "12.5"), 0)
        doc = self.results()
        self.assertEqual(sorted(doc["clones"]), ["run-1", "run-2"])
        self.assertEqual(sorted(r["arm"] for r in doc["runs"].values()), ["fable-alone", "opus-alone"])
        for name, run in doc["runs"].items():
            clone = self.work / run["clone"]
            self.assertEqual(run["clone"], name)
            self.assertNotIn("opus", name + run["clone"])
            self.assertNotIn("fable", name + run["clone"])
            self.assertEqual(subprocess.run(["git", "remote"], cwd=clone, capture_output=True, text=True).stdout, "")
            self.assertEqual(run["end"], "approved")
            stage = run["stages"][0]
            session = stage["session"]
            self.assertEqual((session["exit"], session["stopped"], session["cost_usd"]), (0, None, 1.25))
            self.assertGreaterEqual(session["wall_seconds"], 0)
            model = next(iter(session["models"].values()))
            self.assertEqual((model["inputTokens"], model["outputTokens"], model["costUSD"]), (10, 20, 1.25))
            self.assertEqual(stage["commits"], 1)
            self.assertIn("file", stage["shortstat"])
            self.assertEqual(stage["candidate"], subprocess.run(["git", "rev-parse", "HEAD"], cwd=clone,
                                                                capture_output=True, text=True).stdout.strip())
            self.assertEqual(sorted(stage["gates"]), ["clean-tree", "plan-check", "tests", "validate"])
            self.assertTrue(all(g["exit"] == 0 for g in stage["gates"].values()))
            self.assertEqual(stage["gates"]["tests"]["tail"][-1], "OK")
            self.assertEqual((stage["review"]["reviewed"], stage["review"]["highest"]), (True, "none"))
        for call in self.calls():
            argv = call["argv"]
            self.assertEqual(argv[argv.index("--max-budget-usd") + 1], "12.5")
            self.assertEqual(argv[argv.index("--output-format") + 1], "json")
            self.assertIn("-p", argv)
            self.assertIn(Path(call["cwd"]).name, ("run-1", "run-2"))

    def test_the_review_prompt_names_no_arm(self):
        self.assertEqual(self.run_main(), 0)
        prompts = list((self.control / "prompts").glob("*.md"))
        self.assertEqual(len(prompts), 2)
        for prompt in prompts:
            text = prompt.read_text().lower()
            self.assertNotIn("opus", text)
            self.assertNotIn("fable", text)
            self.assertIn("d00 t01 §1", text)
            self.assertIn(self.base[:12], text)

    def test_fix_rounds_until_approved_and_no_more(self):
        self.reviews({"opus": ["P1", "P2", "approve"], "default": ["approve"]})
        self.assertEqual(self.run_main(), 0)
        run = self.run_of("opus-alone")
        self.assertEqual([s["kind"] for s in run["stages"]], ["build", "fix", "fix"])
        self.assertEqual([s["review"]["highest"] for s in run["stages"]], ["P1", "P2", "none"])
        self.assertEqual(run["end"], "approved")
        opus_calls = [c for c in self.calls() if c["model"] == "opus"]
        self.assertEqual(len(opus_calls), 3)
        self.assertIn("a finding", opus_calls[1]["stdin"])  # the review reached the fix session
        self.assertEqual(len(self.run_of("fable-alone")["stages"]), 1)

    def test_a_p3_review_approves(self):
        self.reviews({"default": ["P3"]})
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(self.run_of("opus-alone")["end"], "approved")

    def test_fix_rounds_stop_at_the_limit(self):
        self.reviews({"default": ["P1"]})
        self.assertEqual(self.run_main("--fix-rounds", "2"), 0)
        run = self.run_of("opus-alone")
        self.assertEqual(len(run["stages"]), 3)
        self.assertEqual(run["end"], "fix-rounds-exhausted")

    def test_a_failing_gate_with_a_clean_review_starts_a_fix_round(self):
        self.claude_plan({"opus": [{"tests_fail": True}, {"clear": True}], "default": [{}]})
        self.assertEqual(self.run_main(), 0)
        run = self.run_of("opus-alone")
        self.assertEqual(run["stages"][0]["gates"]["tests"]["exit"], 1)
        self.assertEqual(run["stages"][0]["review"]["highest"], "none")
        self.assertEqual([s["kind"] for s in run["stages"]], ["build", "fix"])
        self.assertIn("tests: exit 1", [c for c in self.calls() if c["model"] == "opus"][1]["stdin"])
        self.assertEqual(run["end"], "approved")

    def test_an_untracked_file_fails_the_clean_tree_gate(self):
        self.claude_plan({"opus": [{"untracked": True}, {}], "default": [{}]})
        self.assertEqual(self.run_main(), 0)
        run = self.run_of("opus-alone")
        first = run["stages"][0]
        self.assertEqual(first["gates"]["clean-tree"]["exit"], 1)
        self.assertEqual(first["uncommitted"], 1)
        self.assertEqual(len(first["candidate"]), 40)
        self.assertEqual(run["end"], "approved")
        self.assertEqual(len(run["stages"]), 2)

    def test_no_review_is_never_approval(self):
        for reply in ("fail", "malformed", "empty", "nohighest"):
            with self.subTest(reply):
                measure.remove_tree(self.work)
                for counter in self.control.glob("*-count-*"):
                    counter.unlink()
                self.reviews({"default": [reply]})
                self.assertEqual(self.run_main(), 0)
                for run in self.results()["runs"].values():
                    self.assertEqual(run["end"], "unreviewed")
                    self.assertEqual(run["stages"][-1]["review"]["attempts"], 2)
                    self.assertFalse(run["stages"][-1]["review"]["reviewed"])

    def test_no_more_sessions_at_a_time_than_parallel(self):
        self.claude_plan({"default": [{"sleep": 1.5}]})
        self.assertEqual(self.run_main("--parallel", "2", sections=("D00 T01 §1", "D00 T01 §2")), 0)
        calls = self.calls()
        self.assertEqual(len(calls), 4)
        overlap = max(sum(1 for c in calls if c["start"] < t["start"] + 0.01 < c["end"]) for t in calls)
        self.assertLessEqual(overlap, 2)
        self.assertGreaterEqual(overlap, 2)  # they did run side by side

    def test_a_session_past_its_time_limit_is_stopped_with_its_child(self):
        self.claude_plan({"opus": [{"child": True, "sleep": 60}, {}], "default": [{}]})
        start = time.monotonic()
        self.assertEqual(self.run_main("--minutes", "0.05"), 0)
        self.assertLess(time.monotonic() - start, 50)
        run = self.run_of("opus-alone")
        session = run["stages"][0]["session"]
        self.assertEqual((session["exit"], session["stopped"]), (None, "time limit"))
        # The fake and its sleeping child, and on Windows the fake under its cmd.exe launcher: both were left running.
        if os.name == "nt":
            self.assertIn("python.exe", session["strays_stopped"])
        else:
            self.assertIsInstance(session["strays_stopped"], list)
        child = int((self.control / f"child-{run['clone']}.pid").read_text())
        self.assertFalse(alive(child))

    def test_a_flooding_session_is_stopped_at_the_output_limit(self):
        self.claude_plan({"opus": [{"child": True, "flood": True, "sleep": 60}, {}], "default": [{}]})
        with mock.patch.object(measure, "MAX_OUTPUT_BYTES", 1024 * 1024):
            self.assertEqual(self.run_main(), 0)
        run = self.run_of("opus-alone")
        session = run["stages"][0]["session"]
        self.assertEqual(session["stopped"], "output limit")
        log = self.work / "logs" / run["clone"] / "stage-0.reply.json"
        self.assertLess(log.stat().st_size, 8 * 1024 * 1024)
        child = int((self.control / f"child-{run['clone']}.pid").read_text())
        self.assertFalse(alive(child))

    def test_a_relative_work_folder_still_reaches_the_review(self):
        cwd = os.getcwd()
        os.chdir(self.tmp)
        try:  # restored before tearDown removes the folder, which Windows refuses while it is the working folder
            argv = ["run", "--work", "work", "--repo", str(self.repo), "--base", self.base, "--section", "D00 T01 §1"]
            self.assertEqual(measure.main(argv), 0)
        finally:
            os.chdir(cwd)
        for run in self.results()["runs"].values():
            self.assertEqual(run["end"], "approved")
            self.assertTrue(run["stages"][0]["review"]["reviewed"])

    def test_a_folder_the_measurement_did_not_make_is_never_deleted(self):
        occupied = self.work / "run-1"
        occupied.mkdir(parents=True)
        (occupied / "keep.txt").write_text("someone else's")
        self.assertEqual(self.run_main(), 2)
        self.assertEqual((occupied / "keep.txt").read_text(), "someone else's")
        self.assertEqual(self.calls(), [])

    def test_a_hung_gate_is_stopped_and_fixed(self):
        self.claude_plan({"opus": [{"tests_hang": True}, {"clear": True}], "default": [{}]})
        self.assertEqual(self.run_main("--gate-minutes", "0.05"), 0)
        run = self.run_of("opus-alone")
        self.assertEqual(run["stages"][0]["gates"]["tests"]["stopped"], "time limit")
        self.assertEqual(run["end"], "approved")


class Resume(Fixture):
    def interrupt_once(self, method):
        original = getattr(measure.Measurement, method)
        state = {"done": False}

        def wrapper(this, name, run, stage, *rest):
            if not state["done"] and (method != "session" or stage["kind"] == "fix"):
                state["done"] = True
                if method == "session":  # partial work the interrupted session left in the clone
                    clone = this.work / run["clone"]
                    (clone / "partial.txt").write_text("x")
                    subprocess.run(["git", "add", "-A"], cwd=clone, check=True)
                    subprocess.run(["git", "commit", "-q", "-m", "partial"], cwd=clone, check=True)
                    (clone / "partial.txt").write_text("edited again")  # a checkout to the candidate would refuse
                this.cancel.set()
                raise measure.Cancelled()
            return original(this, name, run, stage, *rest)
        return mock.patch.object(measure.Measurement, method, wrapper)

    def test_interrupted_after_a_build_resumes_with_the_gates(self):
        with self.interrupt_once("gates"):
            self.assertEqual(self.run_main("--parallel", "1"), 130)
        builds = len(self.calls())
        self.assertGreaterEqual(builds, 1)
        self.assertEqual(self.run_main("--parallel", "1"), 0)
        self.assertEqual(len(self.calls()), 2)  # the recorded build is not run again; the other arm builds once
        self.assertTrue(all(r["end"] == "approved" for r in self.results()["runs"].values()))

    def test_interrupted_after_the_gates_resumes_with_the_review(self):
        with self.interrupt_once("review"):
            self.assertEqual(self.run_main("--parallel", "1"), 130)
        gates_before = len(self.gate_calls())
        self.assertEqual(self.run_main("--parallel", "1"), 0)
        # Only the other arm's three gates ran; the interrupted run's gates were recorded and kept.
        self.assertEqual(len([g for g in self.gate_calls()]) - gates_before, 3)
        self.assertEqual(len(self.calls()), 2)

    def test_interrupted_inside_a_fix_round_runs_it_again_from_the_last_candidate(self):
        self.reviews({"opus": ["P1", "approve"], "default": ["approve"]})
        with self.interrupt_once("session"):
            self.assertEqual(self.run_main("--parallel", "1"), 130)
        run = self.run_of("opus-alone")
        self.assertEqual(run["stages"][-1]["kind"], "fix")
        self.assertNotIn("session", run["stages"][-1])
        self.assertEqual(self.run_main("--parallel", "1"), 0)
        run = self.run_of("opus-alone")
        self.assertEqual(run["end"], "approved")
        clone = self.work / run["clone"]
        log = subprocess.run(["git", "log", "--format=%s"], cwd=clone, capture_output=True, text=True).stdout
        self.assertNotIn("partial", log)
        self.assertFalse((clone / "partial.txt").exists())
        parent = subprocess.run(["git", "rev-parse", "HEAD~1"], cwd=clone, capture_output=True, text=True).stdout
        self.assertEqual(parent.strip(), run["stages"][0]["candidate"])

    def test_another_measurement_in_the_same_folder_is_refused(self):
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(self.run_main("--budget", "5"), 2)
        self.assertEqual(self.run_main("--parallel", "1"), 2)
        self.assertEqual(self.run_main(sections=("D00 T01 §2",)), 2)

    def test_a_finished_measurement_runs_nothing_again(self):
        self.assertEqual(self.run_main(), 0)
        calls = len(self.calls())
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(len(self.calls()), calls)


class Clean(Fixture):
    def test_clean_removes_only_the_listed_clones(self):
        self.assertEqual(self.run_main(), 0)
        (self.work / "keep-me").mkdir()
        (self.work / "run-99").mkdir()  # not this measurement's: it is not listed
        self.assertEqual(measure.main(["clean", "--work", str(self.work)]), 0)
        self.assertFalse((self.work / "run-1").exists())
        self.assertFalse((self.work / "run-2").exists())
        for kept in ("keep-me", "run-99", "results.json", "logs"):
            self.assertTrue((self.work / kept).exists(), kept)

    def test_clean_refuses_while_a_run_holds_the_folder(self):
        self.assertEqual(self.run_main(), 0)
        with measure.Lock(self.work):
            self.assertEqual(measure.main(["clean", "--work", str(self.work)]), 2)
            self.assertEqual(self.run_main(), 2)
        self.assertTrue((self.work / "run-1").exists())

    def test_clean_refuses_without_a_record(self):
        self.work.mkdir()
        self.assertEqual(measure.main(["clean", "--work", str(self.work)]), 2)

    def test_clean_refuses_a_listed_path_outside_the_folder(self):
        self.assertEqual(self.run_main(), 0)
        doc = self.results()
        doc["clones"].append("../repo")
        measure.atomic_json(self.work / "results.json", doc)
        self.assertEqual(measure.main(["clean", "--work", str(self.work)]), 2)
        self.assertTrue(self.repo.exists())


def stage(cost, highest="none", reviewed=True, dirty=False, wall=100.0, model="claude-opus-5-5"):
    """One §36 results stage with its session, gates and review."""
    gates = {name: {"exit": 0, "tail": []} for name in ("validate", "plan-check", "tests")}
    gates["clean-tree"] = {"exit": 1 if dirty else 0, "tail": []}
    review = {"reviewed": True, "highest": highest, "p1": 0, "p2": 0, "p3": 0} if reviewed else \
        {"reviewed": False, "reason": "no reviewer"}
    return {"kind": "build", "session": {"exit": 0, "cost_usd": cost, "wall_seconds": wall,
                                         "models": {model: {"costUSD": cost}}},
            "candidate": "c" * 40, "gates": gates, "review": review}


def results(arms, sections=("D00 T01 §1", "D00 T01 §2", "D00 T01 §3"), base="b" * 40):
    """A §36 results document. `arms` maps an arm to a function of the section giving (stages, end)."""
    runs, n = {}, 0
    for arm, make in arms.items():
        for ref in sections:
            n += 1
            stages, end = make(ref)
            runs[f"run-{n}"] = {"section": ref, "arm": arm, "clone": f"run-{n}", "stages": stages, "end": end}
    return {"schema": 1, "identity": {"base": base}, "runs": runs}


def approved(*costs, **kw):
    """Stages costing `costs`, all but the last reviewed P1, the last approving."""
    stages = [stage(c, highest="P1", **kw) for c in costs[:-1]] + [stage(costs[-1], **kw)]
    return lambda ref: (stages, "approved")


class Decide(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(measure.remove_tree, self.tmp)
        self.verdict = self.tmp / "operating-mode.json"
        self.records = self.tmp / "reviews"
        patcher = mock.patch.object(measure, "verified_count", return_value=68)
        patcher.start()
        self.addCleanup(patcher.stop)

    def decide(self, doc):
        path = self.tmp / f"results-{time.time_ns()}.json"
        path.write_text(json.dumps(doc), encoding="utf-8")
        code = measure.main(["decide", "--results", str(path), "--verdict", str(self.verdict), "--records",
                             str(self.records), "--root", str(self.tmp)])
        return code, (json.loads(self.verdict.read_text()) if self.verdict.exists() else None)

    def test_cheap_to_build_and_dear_to_fix_loses_to_the_reverse(self):
        code, verdict = self.decide(results({"opus-alone": approved(1.0, 1.5, 1.5), "fable-alone": approved(3.0)}))
        self.assertEqual(code, 0)
        self.assertEqual((verdict["arm"], verdict["model"]), ("fable-alone", "fable"))
        self.assertEqual(verdict["branch"], "the lowest cost to an approved review")
        self.assertEqual(verdict["totals"]["opus-alone"]["cost_usd"], 12.0)
        self.assertEqual(verdict["totals"]["fable-alone"]["cost_usd"], 9.0)

    def test_an_arm_that_never_reaches_approval_is_ineligible(self):
        never = lambda ref: ([stage(0.5, highest="P1")], "fix-rounds-exhausted" if ref.endswith("3") else "approved")
        code, verdict = self.decide(results({"opus-alone": never, "fable-alone": approved(3.0)}))
        self.assertEqual((code, verdict["arm"], verdict["branch"]), (0, "fable-alone", "the only eligible arm"))
        self.assertFalse(verdict["totals"]["opus-alone"]["eligible"])

    def test_a_dirty_tree_or_no_review_makes_an_arm_ineligible_whatever_its_end_says(self):
        for name, broken in (("dirty", stage(0.5, dirty=True)), ("unreviewed", stage(0.5, reviewed=False))):
            with self.subTest(name):
                cheap = lambda ref, b=broken: ([b], "approved")  # a record claiming approval it did not earn
                code, verdict = self.decide(results({"opus-alone": cheap, "fable-alone": approved(3.0)}))
                self.assertEqual((code, verdict["arm"]), (0, "fable-alone"))
                self.assertFalse(verdict["totals"]["opus-alone"]["eligible"])

    def test_a_run_missing_a_gate_is_not_approval(self):
        # Round 1 finding 1: a gate the record lacks never counts as passed.
        def thin(ref):
            s = stage(0.5)
            s["gates"] = {"validate": {"exit": 0, "tail": []}}
            return [s], "approved"
        code, verdict = self.decide(results({"opus-alone": thin, "fable-alone": approved(3.0)}))
        self.assertEqual((code, verdict["arm"]), (0, "fable-alone"))
        self.assertFalse(verdict["totals"]["opus-alone"]["eligible"])

    def test_the_lead_model_is_the_alias_family_not_the_dearest_model(self):
        # Round 1 finding 3: the readers' Sonnet may cost more than the lead itself.
        def with_readers(ref):
            s = stage(3.0)
            s["session"]["models"] = {"claude-opus-5-5": {"costUSD": 1.0}, "claude-sonnet-5-5": {"costUSD": 2.0}}
            return [s], "approved"
        code, verdict = self.decide(results({"opus-alone": with_readers, "fable-alone": approved(9.0)}))
        self.assertEqual((code, verdict["arm"], verdict["resolved_model"]), (0, "opus-alone", "claude-opus-5-5"))

    def test_a_cost_tie_goes_to_fewer_reviews_then_to_the_shorter_wall_time(self):
        # Fewer reviews must beat a shorter wall time: fable has one review per section but the longer run.
        code, verdict = self.decide(results({"opus-alone": approved(1.0, 1.0),
                                             "fable-alone": approved(2.0, wall=300.0)}))
        self.assertGreater(verdict["totals"]["fable-alone"]["wall_seconds"], verdict["totals"]["opus-alone"]["wall_seconds"])
        self.assertEqual((verdict["arm"], verdict["branch"]), ("fable-alone", "a tie on cost, broken by fewer reviews"))
        code, verdict = self.decide(results({"opus-alone": approved(2.0, wall=50.0),
                                             "fable-alone": approved(2.0, wall=80.0)}))
        self.assertEqual((verdict["arm"], verdict["branch"]),
                         ("opus-alone", "a tie on cost and reviews, broken by the shorter wall time"))

    def test_refusals_leave_the_stored_verdict_as_it_was(self):
        self.assertEqual(self.decide(results({"opus-alone": approved(1.0), "fable-alone": approved(2.0)}))[0], 0)
        before = self.verdict.read_bytes()
        two = ("D00 T01 §1", "D00 T01 §2")
        missing_cost = lambda ref: ([stage(None)], "approved")
        no_review_key = lambda ref: ([{k: v for k, v in stage(1.0).items() if k != "review"}], "approved")
        open_run = lambda ref: ([stage(1.0)], None)
        cases = {
            "fewer than three sections": results({"opus-alone": approved(1.0), "fable-alone": approved(2.0)}, two),
            "no eligible arm": results({"opus-alone": lambda r: ([stage(1, "P1")], "fix-rounds-exhausted"),
                                        "fable-alone": lambda r: ([stage(1, "P2")], "fix-rounds-exhausted")}),
            "missing cost": results({"opus-alone": missing_cost, "fable-alone": approved(2.0)}),
            "missing review": results({"opus-alone": no_review_key, "fable-alone": approved(2.0)}),
            "unfinished run": results({"opus-alone": open_run, "fable-alone": approved(2.0)}),
        }
        different = results({"opus-alone": approved(1.0)})
        other = results({"fable-alone": approved(2.0)}, ("D00 T01 §1", "D00 T01 §2", "D00 T01 §9"))
        different["runs"].update({f"run-{n + 10}": run for n, run in enumerate(other["runs"].values())})
        cases["different sections"] = different
        twice = results({"opus-alone": approved(1.0), "fable-alone": approved(2.0)},
                        ("D00 T01 §1", "D00 T01 §1", "D00 T01 §2", "D00 T01 §3"))
        cases["a section twice"] = twice
        for name, doc in cases.items():
            with self.subTest(name):
                self.assertEqual(self.decide(doc)[0], 2)
                self.assertEqual(self.verdict.read_bytes(), before)

    def test_the_verdict_and_the_record_match_the_input(self):
        never = lambda ref: ([stage(0.25, highest="P2")], "fix-rounds-exhausted")
        doc = results({"opus-alone": approved(1.0, 0.5), "fable-alone": approved(2.0), "orchestrated": never})
        code, verdict = self.decide(doc)
        self.assertEqual(code, 0)
        self.assertEqual({k: verdict[k] for k in ("arm", "model", "resolved_model", "base", "verified_at_decision")},
                         {"arm": "opus-alone", "model": "opus", "resolved_model": "claude-opus-5-5",
                          "base": "b" * 40, "verified_at_decision": 68})
        record = (self.tmp / verdict["record"]).read_text(encoding="utf-8")
        rows = [line for line in record.splitlines() if line.startswith("| run-")]
        self.assertEqual(len(rows), len(doc["runs"]))
        for name, run in doc["runs"].items():
            cost = sum(s["session"]["cost_usd"] for s in run["stages"])
            line = next(r for r in rows if r.startswith(f"| {name} |"))
            self.assertIn(f"| {run['section']} | {run['arm']} | ${cost:.2f} |", line)
            self.assertTrue(line.endswith(f"| {run['end']} |"))
        self.assertIn("| opus-alone | $4.50 | 6 |", record)
        self.assertIn("| orchestrated | $0.75 | 3 | 300 | no |", record)
        self.assertIn("opus-alone, by the lowest cost to an approved review.", record)
        checker = subprocess.run([sys.executable, str(SCRIPTS / "check-design-doc.py"), str(self.tmp / verdict["record"]),
                                  "--require", "Runs", "--require", "Totals", "--require", "Verdict"],
                                 capture_output=True, text=True)
        self.assertEqual(checker.returncode, 0, checker.stdout + checker.stderr)

    def test_the_2026_11_10_layout_gives_its_recorded_verdict(self):
        source = SCRIPTS.parent / "docs" / "experiments" / "operating-mode-2026-11-10.json"
        code, verdict = self.decide(json.loads(source.read_text(encoding="utf-8")))
        self.assertEqual((code, verdict["arm"], verdict["resolved_model"]), (0, "opus-alone", "claude-opus-5-5"))
        self.assertEqual(round(verdict["totals"]["opus-alone"]["cost_usd"], 2), 6.76)
        self.assertEqual(round(verdict["totals"]["fable-alone"]["cost_usd"], 2), 8.69)
        self.assertFalse(verdict["totals"]["orchestrated"]["eligible"])

    def test_a_dirty_tree_in_the_2026_11_10_layout_is_not_approval(self):
        source = SCRIPTS.parent / "docs" / "experiments" / "operating-mode-2026-11-10.json"
        doc = json.loads(source.read_text(encoding="utf-8"))
        for run in doc["runs"].values():
            if run["arm"] == "opus-alone":
                run["uncommitted"] = 1
        code, verdict = self.decide(doc)
        self.assertEqual((code, verdict["arm"]), (0, "fable-alone"))


class Due(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(measure.remove_tree, self.tmp)
        self.verdict = self.tmp / "operating-mode.json"
        measure.atomic_json(self.verdict, {"verified_at_decision": 100, "model": "opus",
                                           "resolved_model": "claude-opus-5-5"})

    def due(self, now, model="claude-opus-5-5"):
        with mock.patch.object(measure, "verified_count", return_value=now):
            return measure.main(["due", "--model", model, "--verdict", str(self.verdict)])

    def test_299_stamps_are_not_due_and_300_are(self):
        self.assertEqual(self.due(399), 1)
        self.assertEqual(self.due(400), 0)

    def test_a_different_model_is_due(self):
        self.assertEqual(self.due(150), 1)
        self.assertEqual(self.due(150, model="claude-opus-6-0"), 0)

    def test_a_pending_switch_to_another_family_is_not_due(self):
        # Round 1 finding 2: the verdict chose Fable while this Opus session runs on until the next start.
        measure.atomic_json(self.verdict, {"verified_at_decision": 100, "model": "fable",
                                           "resolved_model": "claude-fable-5-2"})
        self.assertEqual(self.due(101, model="claude-opus-5-5"), 1)
        self.assertEqual(self.due(101, model="claude-fable-5-2"), 1)
        self.assertEqual(self.due(101, model="claude-fable-5-3"), 0)  # the alias moved within the family
        self.assertEqual(self.due(400, model="claude-opus-5-5"), 0)  # 300 stamps are due whatever the model

    def test_an_unreadable_verdict_or_count_cannot_tell(self):
        self.verdict.write_text("{", encoding="utf-8")
        self.assertEqual(self.due(100), 2)
        measure.atomic_json(self.verdict, {"verified_at_decision": 100, "model": "m", "resolved_model": "m"})
        with mock.patch.object(measure, "verified_count", side_effect=measure.Refused("no stats")):
            self.assertEqual(measure.main(["due", "--model", "m", "--verdict", str(self.verdict)]), 2)


class Cycles(Fixture):
    """The measurement cycle process-plan runs when one is due: run, decide, clean, twice, then a refused decide."""

    def cycle(self, name):
        work = self.tmp / name
        for counter in self.control.glob("*-count-*"):
            counter.unlink()
        argv = ["run", "--work", str(work), "--repo", str(self.repo), "--base", self.base, "--fix-rounds", "1"]
        for ref in ("D00 T01 §1", "D00 T01 §2", "D00 T01 §4"):
            argv += ["--section", ref]
        self.assertEqual(measure.main(argv), 0)
        code = measure.main(["decide", "--results", str(work / "results.json"), "--verdict", str(self.verdict),
                             "--records", str(self.tmp / "records"), "--root", str(self.repo)])
        self.assertEqual(measure.main(["clean", "--work", str(work)]), 0)
        self.assertFalse(any(work.glob("run-*")))
        return code

    def test_two_cycles_replace_the_verdict_and_a_refused_third_keeps_it(self):
        self.verdict = self.tmp / "operating-mode.json"
        sections = json.loads((self.repo / "sections.json").read_text(encoding="utf-8"))
        sections["D00 T01 §4"] = {"title": "Four", "body": "BODY FOUR"}
        self.sections(sections)
        self.git("commit", "-q", "-am", "four")
        self.base = self.git("rev-parse", "HEAD")
        self.claude_plan({"opus": [{"cost": 2.0}], "fable": [{"cost": 1.0}]})
        self.assertEqual(self.cycle("measure-modes-1"), 0)
        self.assertEqual(json.loads(self.verdict.read_text())["arm"], "fable-alone")
        self.claude_plan({"opus": [{"cost": 0.5}], "fable": [{"cost": 1.0}]})
        self.assertEqual(self.cycle("measure-modes-2"), 0)
        second = self.verdict.read_bytes()
        self.assertEqual(json.loads(second)["arm"], "opus-alone")
        self.reviews({"default": ["P1"]})
        self.assertEqual(self.cycle("measure-modes-3"), 2)  # no arm reaches approval
        self.assertEqual(self.verdict.read_bytes(), second)


class Help(unittest.TestCase):
    def test_help_shows_a_complete_invocation(self):
        text = measure.parser().format_help()
        self.assertIn('run --section "D00 T03 §32"', text)


if __name__ == "__main__":
    unittest.main()
