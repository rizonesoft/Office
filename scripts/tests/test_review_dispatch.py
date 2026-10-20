"""scripts/review-dispatch.py: routing, failover, read-only invocations and records, with fake reviewer CLIs."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
import unittest.mock

SCRIPTS = Path(__file__).resolve().parents[1]
REPO_PIN = SCRIPTS.parent / ".conclave" / "reviewers.toml"

# The kit's shipped reviewers and routes. The suite exercises the dispatcher against this fixture, never against the
# repository's own pin, which a project may narrow (one reviewer, no failover) without changing what is tested here.
FIXTURE_PIN = textwrap.dedent('''    schema_version = 1

    [reviewers.astra]
    cli = "codex"
    model = "gpt-6-astra"
    effort = "medium"

    [reviewers.gemini]
    cli = "agy"
    model = "gemini-4-argon-high"

    [reviewers.sonnet]
    cli = "claude"
    model = "claude-sonnet-5-5"
    effort = "high"

    [routes]
    claude = ["astra", "gemini"]
    codex = ["gemini", "sonnet"]
    gemini = ["astra", "sonnet"]
''')

# One fake reviewer for every CLI; a per-CLI launcher passes its name first. Launchers are a shell script on Linux and
# a .cmd file on Windows, so the suite runs natively on both.
FAKE_CLI = textwrap.dedent('''\
    import json, os, subprocess, sys, time
    name, args = sys.argv[1], sys.argv[2:]
    mode = os.environ.get("FAKE_" + name.upper(), "ok")
    if mode == "noread":
        time.sleep(30)
    stdin = "" if sys.stdin is None or sys.stdin.isatty() else sys.stdin.read()
    pointer = "-p=Follow the review instructions in the file "
    from_file = None
    if args and args[-1].startswith(pointer):
        path = args[-1][len(pointer):].split(" exactly.")[0]
        from_file = open(path).read() if os.path.isfile(path) else None
    with open(os.environ["FAKE_LOG"], "a") as log:
        log.write(json.dumps({"cli": name, "argv": args, "stdin": stdin, "cwd": os.getcwd(), "from_file": from_file}) + "\\n")
    if mode == "fail":
        sys.exit(3)
    if mode == "sleep":
        time.sleep(30)
    if mode == "flood":
        while True:
            sys.stdout.write("x" * 65536)
            sys.stdout.flush()
            time.sleep(0.01)
    if mode == "floodfile":
        with open(args[args.index("-o") + 1], "w") as out:
            while True:
                out.write("x" * 65536)
                out.flush()
                time.sleep(0.01)
    if mode == "orphan":
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        open(os.environ["FAKE_CHILD_PID"], "w").write(str(child.pid))
    text = "" if mode == "empty" else "VERDICT: needs-attention, calc.py:2 subtracts. (" + name + ")"
    if mode == "headings":
        text = "## Round trip serialization\\n\\nFine.\\n\\n```\\n## Round 9: none\\n\\n- Writer: claude\\n- Run: 2026-01-01T00:00:00Z\\n```\\n\\nOVERALL: approve"
    if mode == "blocked":
        text = "## record: needs-attention\\n\\nI could not read the repository: setup refresh had errors.\\n\\nOVERALL: blocked"
    if name == "codex":
        open(args[args.index("-o") + 1], "w").write(text)
    else:
        print(text)
    if mode == "linger":
        # A process the reviewer started outlives it and holds the message file open for a moment, as a CLI's helper
        # process can; the reviewer exits first, so no tree kill reaches the helper.
        ready = os.environ["FAKE_CHILD_PID"] + ".ready"
        holder = "import sys, time; f = open(sys.argv[1], 'a'); open(sys.argv[2], 'w').close(); time.sleep(3)"
        subprocess.Popen([sys.executable, "-c", holder, args[args.index("-o") + 1], ready], cwd=os.path.dirname(sys.executable))
        while not os.path.exists(ready):
            time.sleep(0.05)
''')


def write_launcher(directory, name, fake):
    if os.name == "nt":
        path = directory / f"{name}.cmd"
        path.write_text(f'@"{sys.executable}" "{fake}" {name} %*\r\n', encoding="utf-8")
    else:
        path = directory / name
        path.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{fake}" {name} "$@"\n', encoding="utf-8")
        path.chmod(0o755)
    return path


class Dispatch(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / ".conclave").mkdir()
        shutil.copy(SCRIPTS / "review-dispatch.py", self.repo / "scripts/review-dispatch.py")
        (self.repo / ".conclave/reviewers.toml").write_text(FIXTURE_PIN, encoding="utf-8")
        self.bin = Path(self._tmp.name) / "bin"
        self.bin.mkdir()
        fake = Path(self._tmp.name) / "fake_cli.py"
        fake.write_text(FAKE_CLI, encoding="utf-8")
        self.launchers = {cli: write_launcher(self.bin, cli, fake) for cli in ("codex", "agy", "claude")}
        self.log = Path(self._tmp.name) / "calls.jsonl"
        self.scratch = Path(self._tmp.name) / "scratch"
        self.scratch.mkdir()
        self.prompt = self.repo / "prompt.md"
        self.prompt.write_text("Review calc.py. Do not modify any file.\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def dispatch(self, *args, cwd=None, **modes):
        system_root = {"SYSTEMROOT": os.environ["SYSTEMROOT"]} if os.name == "nt" else {}
        env = {"PATH": f"{self.bin}{os.pathsep}{Path(sys.executable).parent}", "FAKE_LOG": str(self.log),
               "FAKE_CHILD_PID": str(Path(self._tmp.name) / "child.pid"), **system_root,
               **{var: str(self.scratch) for var in ("TMP", "TEMP", "TMPDIR")},
               **{f"FAKE_{k.upper()}": v for k, v in modes.items()}}
        result = subprocess.run([sys.executable, "-B", str(self.repo / "scripts/review-dispatch.py"), *args],
                                capture_output=True, text=True, env=env, timeout=60, cwd=cwd)
        summary = json.loads(result.stdout) if result.stdout.strip().startswith("{") else None
        return result, summary

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_astra_reviews_claude_work_read_only(self):
        result, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((summary["reviewer"], summary["model"]), ("astra", "gpt-6-astra"))
        self.assertIn("(codex)", summary["review"])
        call = self.calls()[0]
        self.assertEqual(call["argv"][:3], ["exec", "-m", "gpt-6-astra"])
        for flag in ("--sandbox", "read-only", "--ephemeral", "model_reasoning_effort=medium"):
            self.assertIn(flag, call["argv"])
        self.assertEqual(call["stdin"], self.prompt.read_text())
        self.assertEqual(Path(call["cwd"]).resolve(), self.repo.resolve())

    def test_astra_never_reviews_astra(self):
        result, summary = self.dispatch("--writer", "codex", "--prompt", str(self.prompt))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(summary["reviewer"], "gemini")
        self.assertEqual([c["cli"] for c in self.calls()], ["agy"])

    def test_gemini_runs_in_plan_mode_with_the_prompt_as_the_p_value(self):
        _, summary = self.dispatch("--writer", "codex", "--prompt", str(self.prompt))
        call = self.calls()[0]
        self.assertEqual(summary["model"], "gemini-4-argon-high")
        self.assertIn("--sandbox", call["argv"])
        self.assertEqual(call["argv"][call["argv"].index("--mode") + 1], "plan")
        if os.name == "nt":
            # The fake is a .cmd shim on Windows, so the prompt must arrive by file, never as argument text.
            self.assertTrue(call["argv"][-1].startswith("-p=Follow the review instructions in the file "))
            self.assertEqual(call["from_file"], self.prompt.read_text())
        else:
            self.assertEqual(call["argv"][-1], "-p=" + self.prompt.read_text())

    def test_a_route_is_one_reviewer_and_one_fallback_never_the_writers_family(self):
        result, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), codex="fail")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(summary["reviewer"], "gemini")
        self.log.unlink()
        result, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), codex="fail", agy="empty")
        self.assertEqual(result.returncode, 1, "a third reviewer ran after the fallback")
        self.assertEqual([f["reason"] for f in summary["failover"]], ["exited 3", "returned no review"])
        self.assertEqual([c["cli"] for c in self.calls()], ["codex", "agy"], "Sonnet must never review Claude's work")

    def test_the_fallback_for_codex_work_is_sonnet_in_plan_mode(self):
        result, summary = self.dispatch("--writer", "codex", "--prompt", str(self.prompt), agy="fail")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(summary["reviewer"], "sonnet")
        sonnet = self.calls()[-1]
        self.assertEqual(sonnet["argv"][sonnet["argv"].index("--permission-mode") + 1], "plan")
        self.assertEqual(sonnet["argv"][sonnet["argv"].index("--model") + 1], "claude-sonnet-5-5")

    def test_a_reviewer_that_could_not_reach_the_candidate_fails_over(self):
        # A reply ending OVERALL: blocked says the reviewer never saw the work (a sandbox that cannot read the
        # repository): it is not a review, so the next reviewer runs.
        result, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), codex="blocked")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(summary["reviewer"], "gemini")
        self.assertEqual(summary["failover"][0]["reviewer"], "astra")
        self.assertIn("could not review: ", summary["failover"][0]["reason"])
        self.assertIn("setup refresh had errors", summary["failover"][0]["reason"])
        result, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt),
                                        codex="blocked", agy="blocked", claude="blocked")
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(summary["review"])

    def test_a_missing_cli_fails_over(self):
        self.launchers["codex"].unlink()
        _, summary = self.dispatch("--writer", "gemini", "--prompt", str(self.prompt))
        self.assertEqual(summary["reviewer"], "sonnet")
        self.assertEqual(summary["failover"], [{"reviewer": "astra", "reason": "codex is not installed"}])

    def test_a_timeout_fails_over(self):
        _, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--timeout", "2", codex="sleep")
        self.assertEqual(summary["reviewer"], "gemini")
        self.assertEqual(summary["failover"][0]["reason"], "timed out")

    def test_no_review_is_never_an_approval(self):
        record = self.repo / "docs/reviews/round.md"
        result, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(record),
                                        codex="fail", agy="fail", claude="fail")
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(summary["reviewer"])
        self.assertIn("not an approval", record.read_text())

    def test_rounds_are_numbered_and_appended(self):
        record = self.repo / "docs/reviews/round.md"
        record.parent.mkdir(parents=True)
        record.write_text("# Findings\n", encoding="utf-8")
        self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(record))
        _, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(record), codex="fail")
        text = record.read_text()
        self.assertEqual(summary["round"], 2)
        self.assertTrue(text.startswith("# Findings\n"))
        self.assertIn("## Round 1: astra (`gpt-6-astra` via `codex`)", text)
        self.assertIn("## Round 2: gemini (`gemini-4-argon-high` via `agy`)", text)
        self.assertIn("- Skipped: astra (exited 3)", text)

    def check_pin(self, *args):
        result, _ = self.dispatch("--check-pin", *args)
        return result

    def test_check_pin_reports_a_valid_pin(self):
        result = self.check_pin("--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        spec = importlib.util.spec_from_file_location("dispatch_pin", self.repo / "scripts/review-dispatch.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        pin = module.load_pin(self.repo / ".conclave/reviewers.toml")
        self.assertEqual((report["ok"], report["schema_version"]), (True, 1))
        self.assertEqual((report["reviewers"], report["routes"]), (pin["reviewers"], pin["routes"]))
        self.assertEqual(sorted(report["clis"]), sorted(module.CLIS))
        self.assertTrue(all(isinstance(v, bool) for v in report["clis"].values()))
        self.assertTrue(report["clis"]["codex"], "the fake codex launcher is on PATH")
        self.assertEqual(self.calls(), [], "--check-pin ran a reviewer")

    def test_check_pin_reports_a_refused_pin(self):
        spec = importlib.util.spec_from_file_location("dispatch_refusal", self.repo / "scripts/review-dispatch.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        pin = self.repo / ".conclave/reviewers.toml"
        good = pin.read_text()
        for bad in bad_pins(good) + (good.replace("schema_version = 1", "schema_version = true"), "not toml ["):
            with self.subTest(bad=bad[-40:]):
                self.assertNotEqual(bad, good, "the replacement must match the fixture, or the case tests nothing")
                pin.write_text(bad, encoding="utf-8")
                with self.assertRaises(module.Refused) as refused:
                    module.load_pin(pin)
                result = self.check_pin("--json")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(json.loads(result.stdout), {"ok": False, "error": str(refused.exception)})
        self.assertEqual(self.calls(), [])

    def test_a_pin_that_cannot_be_read_is_refused_not_a_crash(self):
        pin = self.repo / ".conclave/reviewers.toml"
        cases = {"directory": lambda: (pin.unlink(), pin.mkdir()),
                 "not UTF-8": lambda: pin.write_bytes(b"schema_version = 1\n# \xff\n"),
                 "nested too deep": lambda: pin.write_text("x = " + "[" * 5000 + "0" + "]" * 5000 + "\n"),
                 "integer too long": lambda: pin.write_text("schema_version = " + "9" * 5000 + "\n")}
        for name, make in cases.items():
            with self.subTest(name):
                if pin.is_dir():
                    pin.rmdir()
                make()
                result = self.check_pin("--json")
                self.assertEqual(result.returncode, 2, result.stderr)
                report = json.loads(result.stdout)
                self.assertFalse(report["ok"])
                self.assertTrue(report["error"].startswith("unreadable reviewer pin"), report["error"])
                review, _ = self.dispatch("--writer", "claude", "--prompt", str(self.prompt))
                self.assertEqual(review.returncode, 2, review.stderr)
                self.assertIn("review-dispatch refused: unreadable reviewer pin", review.stderr)
        self.assertEqual(self.calls(), [])

    def test_check_pin_reports_a_missing_pin(self):
        (self.repo / ".conclave/reviewers.toml").unlink()
        result = self.check_pin("--json")
        self.assertEqual(result.returncode, 2)
        self.assertTrue(json.loads(result.stdout)["error"].startswith("no reviewer pin at"), result.stdout)

    def test_check_pin_without_json_prints_one_line(self):
        result = self.check_pin()
        self.assertEqual((result.returncode, result.stdout), (0, "ok\n"))
        pin = self.repo / ".conclave/reviewers.toml"
        pin.write_text(pin.read_text().replace('effort = "medium"', 'effort = "extreme"'), encoding="utf-8")
        result = self.check_pin()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "refused: reviewer 'astra' needs effort = one of low, medium, high, xhigh\n")

    def test_check_pin_needs_no_writer_or_prompt(self):
        self.assertEqual(self.check_pin("--json").returncode, 0)
        result, _ = self.dispatch("--writer", "claude")
        self.assertEqual(result.returncode, 2, "a review without --prompt must still be refused")
        self.assertIn("--writer and --prompt are required", result.stderr)

    def test_list_rounds_reads_back_what_record_wrote(self):
        # Two rounds written by record itself: one reviewed, one where every reviewer was skipped.
        record = self.repo / "docs/reviews/00-design/D00-T01-s1.md"
        self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(record))
        self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(record),
                      codex="fail", agy="fail")
        result, listing = self.dispatch("--list-rounds", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        (only,) = listing["records"]
        self.assertEqual(only["path"], "docs/reviews/00-design/D00-T01-s1.md")
        reviewed, skipped = only["rounds"]
        self.assertEqual({k: reviewed[k] for k in ("number", "reviewer", "model", "cli", "writer", "effort", "skipped")},
                         {"number": 1, "reviewer": "astra", "model": "gpt-6-astra", "cli": "codex", "writer": "claude",
                          "effort": "medium", "skipped": []})
        self.assertRegex(reviewed["run"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual({k: skipped[k] for k in ("number", "reviewer", "model", "cli", "effort", "skipped")},
                         {"number": 2, "reviewer": None, "model": None, "cli": None, "effort": None,
                          "skipped": [{"reviewer": "astra", "reason": "exited 3"},
                                      {"reviewer": "gemini", "reason": "exited 3"}]})
        self.assertNotIn("unreadable", listing)

    def test_list_rounds_with_no_records_and_with_an_unreadable_heading(self):
        result, listing = self.dispatch("--list-rounds", "--json")
        self.assertEqual((result.returncode, listing), (0, {"records": []}))
        good = self.repo / "docs/reviews/a.md"
        self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(good))
        bad = self.repo / "docs/reviews/b.md"
        bad.write_text("# Findings\n\n## Round two: astra\n\n- Writer: claude\n", encoding="utf-8")
        result, listing = self.dispatch("--list-rounds", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([r["path"] for r in listing["records"]], ["docs/reviews/a.md"])
        self.assertEqual(listing["unreadable"], ["docs/reviews/b.md"])
        self.assertEqual(self.calls()[-1:], self.calls()[:1], "listing ran a reviewer")
        result, _ = self.dispatch("--prompt", str(self.prompt))
        self.assertEqual(result.returncode, 2, "a review without --writer must still be refused")

    def test_review_text_that_looks_like_a_round_is_neither_counted_nor_listed(self):
        # A review quoting `## Round ...` lines, one a whole fake round in a fence, round-trips through record.
        record = self.repo / "docs/reviews/r.md"
        self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(record), codex="headings")
        result, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(record))
        self.assertEqual(summary["round"], 2, "record counted review text as a round")
        text = record.read_text(encoding="utf-8")
        # Stored byte for byte: no escape inside or outside the fence.
        self.assertIn("\n## Round trip serialization\n", text)
        self.assertIn("```\n## Round 9: none\n", text)
        _, listing = self.dispatch("--list-rounds", "--json")
        self.assertEqual([r["number"] for r in listing["records"][0]["rounds"]], [1, 2])
        self.assertNotIn("unreadable", listing)

    def test_the_line_count_envelope_holds_against_other_line_breaks_and_hand_edits(self):
        spec = importlib.util.spec_from_file_location("dispatch_reader", self.repo / "scripts/review-dispatch.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        base = {"writer": "claude", "reviewer": "astra", "model": "gpt-6-astra", "cli": "codex", "effort": "medium",
                "failover": []}
        path = self.repo / "docs/reviews/u.md"
        # U+2028 and U+0085 split lines for str.splitlines but not for record: a fake round behind them stays text.
        module.record(path, {**base, "review": "Quoted ## Round 9: none\n\n- Writer: codex\n- Run: now\u0085x"},
                      "2026-10-20T00:00:00Z")
        module.record(path, {**base, "review": "Plain."}, "2026-10-20T00:00:01Z")
        self.assertEqual([r["number"] for r in module.read_rounds(path.read_text(encoding="utf-8"))], [1, 2])
        # A round recorded before the count (no Lines field) still reads, running to the next heading.
        legacy = ("## Round 1: astra (`gpt-6-astra` via `codex`)\n\n- Writer: claude\n- Run: 2026-10-16T00:00:00Z\n\n"
                  "Review.\n\n")
        self.assertEqual([r["number"] for r in module.read_rounds(legacy)], [1])
        # A hand edit that changes the review's line count is refused, not misread.
        text = path.read_text(encoding="utf-8")
        self.assertIsNone(module.read_rounds(text.replace("- Lines: 1", "- Lines: 3")))
        self.assertIsNone(module.read_rounds(text.replace("Plain.", "Plain.\nAdded by hand.")))

    def module(self):
        spec = importlib.util.spec_from_file_location("dispatch_record", self.repo / "scripts/review-dispatch.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    RESULT = {"writer": "claude", "reviewer": "astra", "model": "gpt-6-astra", "cli": "codex", "effort": "medium",
              "failover": []}

    def test_a_lines_value_that_is_not_ascii_digits_is_unreadable_not_a_crash(self):
        # D06 T01 §8 (1): "²" passes str.isdigit and int() raises; so does a count past Python's digit limit.
        good = self.repo / "docs/reviews/good.md"
        self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(good))
        recorded = good.read_text(encoding="utf-8")
        for name, value in (("superscript.md", "²"), ("huge.md", "9" * 5000)):
            body = re.sub(r"- Lines: \d+", "- Lines: " + value, recorded)
            self.assertNotEqual(body, recorded, name)
            (self.repo / "docs/reviews" / name).write_text(body, encoding="utf-8")
        result, listing = self.dispatch("--list-rounds", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([r["path"] for r in listing["records"]], ["docs/reviews/good.md"])
        self.assertEqual(sorted(listing["unreadable"]), ["docs/reviews/huge.md", "docs/reviews/superscript.md"])

    def test_an_edit_inside_a_review_that_keeps_its_line_count_is_refused(self):
        # D06 T01 §8 (2): the count alone cannot see an edit of the same length; the digest can.
        module, path = self.module(), self.repo / "docs/reviews/d.md"
        module.record(path, {**self.RESULT, "review": "Finding one.\nOVERALL: needs-attention"}, "2026-10-20T00:00:00Z")
        text = path.read_bytes().decode("utf-8")
        self.assertRegex(text, r"\n- Digest: [0-9a-f]{16}\n")
        self.assertEqual(len(module.read_rounds(text)), 1)
        self.assertIsNone(module.read_rounds(text.replace("needs-attention", "approve")))
        # A CRLF checkout of the same file still reads, and its digest still matches.
        self.assertEqual(len(module.read_rounds(text.replace("\n", "\r\n"))), 1)

    def test_a_review_is_stored_byte_for_byte_and_an_append_keeps_it_readable(self):
        # D06 T01 §8 (3): a CRLF pair and a lone CR inside a review are stored as they came, and a second round
        # appended after them does not turn the lone CR into a line break that breaks the first round's count.
        module, path = self.module(), self.repo / "docs/reviews/b.md"
        module.record(path, {**self.RESULT, "review": "A\r\nB\rC\nD"}, "2026-10-20T00:00:00Z")
        self.assertIn(b"\nA\r\nB\rC\nD\n", path.read_bytes())
        module.record(path, {**self.RESULT, "review": "Second."}, "2026-10-20T00:00:01Z")
        raw = path.read_bytes()
        self.assertIn(b"\nA\r\nB\rC\nD\n", raw)
        self.assertEqual([r["number"] for r in module.read_rounds(raw.decode("utf-8"))], [1, 2])

    def test_a_model_or_name_ending_in_a_newline_is_refused(self):
        # D06 T01 §8 (4): `$` in MODEL and NAME accepted a trailing newline, which then broke the round heading.
        pin = self.repo / ".conclave/reviewers.toml"
        good = pin.read_text(encoding="utf-8")
        cases = {'model = "gpt-6-astra\\n"': "reviewer 'astra' has a malformed model",
                 '[reviewers."sonnet\\n"]': "invalid reviewer 'sonnet\\n'"}
        for edit, message in cases.items():
            with self.subTest(edit):
                old = 'model = "gpt-6-astra"' if edit.startswith("model") else "[reviewers.sonnet]"
                pin.write_text(good.replace(old, edit), encoding="utf-8")
                result = self.check_pin("--json")
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(json.loads(result.stdout)["error"], message)
                review, _ = self.dispatch("--writer", "claude", "--prompt", str(self.prompt))
                self.assertEqual(review.returncode, 2, review.stderr)
        self.assertEqual(self.calls(), [])

    def test_record_refuses_to_append_to_a_findings_file_it_cannot_read(self):
        # D06 T01 §8 (5): numbering an unreadable file by counting headings counted quoted ones; now nothing is
        # appended, the review still reaches stdout, and the exit is 2.
        bad = self.repo / "docs/reviews/bad.md"
        bad.parent.mkdir(parents=True)
        body = "# Findings\n\n## Round two: astra\n\n- Writer: claude\n"
        bad.write_bytes(body.encode("utf-8"))
        result, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(bad))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(bad.read_bytes(), body.encode("utf-8"), "record appended to a file it cannot read")
        self.assertIn("calc.py:2 subtracts", summary["review"])
        self.assertIsNone(summary["round"])
        self.assertIn("cannot be read back", result.stderr)

    def test_a_cli_in_the_working_directory_is_not_on_path(self):
        # D01 T01 §5: Windows shutil.which looks in the working directory first unless NoDefaultCurrentDirectoryInExePath
        # is set, so a codex committed to the reviewed repository was reported as installed and run as the reviewer.
        # The dispatch() environment never sets that variable, so this runs as a plain Windows shell would.
        self.launchers["codex"].unlink()
        planted = self.repo / ("codex.cmd" if os.name == "nt" else "codex")
        marker = self.repo / "planted-ran.txt"
        if os.name == "nt":
            planted.write_text(f'@echo planted> "{marker}"\r\n', encoding="utf-8")
        else:
            planted.write_text(f'#!/bin/sh\necho planted > "{marker}"\n', encoding="utf-8")
            planted.chmod(0o755)
        result, _ = self.dispatch("--check-pin", "--json", cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["clis"]["codex"], "a codex in the working directory counted as on PATH")
        result, summary = self.dispatch("--writer", "gemini", "--prompt", str(self.prompt), cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists(), "the planted codex in the working directory ran as the reviewer")
        self.assertEqual(summary["reviewer"], "sonnet")
        self.assertEqual([f["reviewer"] for f in summary["failover"]], ["astra"])

    @unittest.skipUnless(os.name == "nt", "drive-relative paths, PATHEXT and extensionless lookups are Windows rules")
    def test_find_cli_on_windows_paths(self):
        # Review round 1 of D01 T01 §5: a drive-relative entry (\work\repo) passed os.path.isabs on Python 3.11 and
        # 3.12; an empty PATHEXT found nothing; an extensionless executable was no longer found.
        module = self.module()
        folder = Path(self._tmp.name) / "clis"
        folder.mkdir()
        (folder / "codex.cmd").write_text("@exit /b 0\r\n", encoding="utf-8")
        drive_relative = str(folder)[2:]  # "R:\x\clis" -> "\x\clis", resolved against the current drive
        with unittest.mock.patch.dict(os.environ, {"PATH": drive_relative, "PATHEXT": ".CMD"}):
            self.assertIsNone(module.find_cli("codex"), "a drive-relative PATH entry was searched")
        with unittest.mock.patch.dict(os.environ, {"PATH": str(folder), "PATHEXT": ""}):
            self.assertEqual(module.find_cli("codex"), str(folder / "codex.CMD"), "an empty PATHEXT found nothing")
        # Round 2: a PATHEXT entry is an extension, never a path that climbs out of the PATH directory.
        outside = Path(self._tmp.name) / "reviewed"
        outside.mkdir()
        (outside / "codex.cmd").write_text("@exit /b 0\r\n", encoding="utf-8")
        (folder / "codex").mkdir()
        with unittest.mock.patch.dict(os.environ, {"PATH": str(folder), "PATHEXT": "\\..\\..\\reviewed\\codex.cmd"}):
            # The malformed entry is dropped and the defaults find the codex.cmd inside the PATH directory.
            self.assertEqual(module.find_cli("codex"), str(folder / "codex.CMD"), "a PATHEXT entry led outside PATH")
        (folder / "codex").rmdir()
        # npm puts an extensionless shell script beside codex.cmd; Windows cannot run the script, so .cmd comes first,
        # and the bare name is found only when no PATHEXT candidate is there.
        (folder / "codex").write_text("#!/bin/sh\n", encoding="utf-8")
        with unittest.mock.patch.dict(os.environ, {"PATH": str(folder), "PATHEXT": ".EXE;.CMD"}):
            self.assertEqual(module.find_cli("codex"), str(folder / "codex.CMD"))
            (folder / "codex.cmd").unlink()
            self.assertEqual(module.find_cli("codex"), str(folder / "codex"), "an extensionless executable was lost")

    def test_a_round_number_past_the_digit_limit_is_unreadable_and_keeps_the_review(self):
        # Review round 1 of D06 T01 §8: a 5,000-digit round number made the reader's int() raise, so record lost the
        # finished review's output and the listing would abort. The reader never raises; the file is just unreadable.
        bad = self.repo / "docs/reviews/huge-number.md"
        bad.parent.mkdir(parents=True)
        body = "## Round " + "9" * 5000 + ": none\n\n- Writer: claude\n- Run: 2026-10-20T00:00:00Z\n"
        bad.write_bytes(body.encode("utf-8"))
        self.assertIsNone(self.module().read_rounds(body))
        result, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(bad))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("calc.py:2 subtracts", summary["review"])
        self.assertEqual(bad.read_bytes(), body.encode("utf-8"))
        result, listing = self.dispatch("--list-rounds", "--json")
        self.assertEqual((result.returncode, listing["unreadable"]), (0, ["docs/reviews/huge-number.md"]))

    def test_the_largest_review_record_writes_is_one_its_reader_reads(self):
        # Review round 1 of D06 T01 §8: record wrote a 7-digit Lines count the 6-digit reader refused. The largest
        # review a reviewer can return (MAX_OUTPUT_BYTES of newlines) must read back and take another round.
        module, path = self.module(), self.repo / "docs/reviews/large.md"
        module.record(path, {**self.RESULT, "review": "\n" * module.MAX_OUTPUT_BYTES}, "2026-10-20T00:00:00Z")
        module.record(path, {**self.RESULT, "review": "Second."}, "2026-10-20T00:00:01Z")
        self.assertEqual([r["number"] for r in module.read_rounds(path.read_bytes().decode("utf-8"))], [1, 2])

    @unittest.skipIf(os.name == "nt", "creating a symlink needs a privilege Windows does not grant by default")
    def test_a_symlink_loop_is_reported_without_aborting_the_listing(self):
        good = self.repo / "docs/reviews/good.md"
        self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(good))
        os.symlink("loop.md", self.repo / "docs/reviews/loop.md")
        result, listing = self.dispatch("--list-rounds", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([r["path"] for r in listing["records"]], ["docs/reviews/good.md"])
        self.assertEqual(listing["unreadable"], ["docs/reviews/loop.md"])

    def test_a_malformed_or_unreadable_record_is_named_and_the_rest_still_listed(self):
        good = self.repo / "docs/reviews/good.md"
        self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--record", str(good))
        recorded = good.read_text(encoding="utf-8")
        cases = {
            "empty-effort.md": recorded.replace("- Effort: medium", "- Effort:\n- Skipped: x (y)"),
            "two-writers.md": recorded.replace("- Writer: claude", "- Writer: claude\n- Writer: codex"),
            "no-blank.md": recorded.replace("via `codex`)\n\n", "via `codex`)\n"),
        }
        for name, body in cases.items():
            self.assertNotEqual(body, recorded, name)
            (self.repo / "docs/reviews" / name).write_text(body, encoding="utf-8")
        (self.repo / "docs/reviews/not-utf8.md").write_bytes(recorded.replace("claude", "claud\udcff", 1)
                                                              .encode("utf-8", "surrogateescape"))
        (self.repo / "docs/reviews/folder.md").mkdir()  # a path that cannot be read as a file
        result, listing = self.dispatch("--list-rounds", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([r["path"] for r in listing["records"]], ["docs/reviews/good.md"])
        self.assertEqual(sorted(listing["unreadable"]), sorted(
            f"docs/reviews/{n}" for n in (*cases, "not-utf8.md", "folder.md")))

    def test_a_large_prompt_reaches_gemini_by_file(self):
        self.prompt.write_text("x" * 150_000, encoding="utf-8")
        self.dispatch("--writer", "codex", "--prompt", str(self.prompt))
        call = self.calls()[0]
        self.assertTrue(call["argv"][-1].startswith("-p=Follow the review instructions in the file "))
        self.assertEqual(call["from_file"], "x" * 150_000)

    def test_a_runaway_reviewer_is_stopped_while_it_runs(self):
        started = time.monotonic()
        _, summary = self.dispatch("--writer", "codex", "--prompt", str(self.prompt), "--timeout", "40", agy="flood")
        self.assertLess(time.monotonic() - started, 30, "the cap was only applied at the timeout")
        self.assertEqual(summary["reviewer"], "sonnet")
        self.assertEqual(summary["failover"][0]["reason"], "returned more than 2000000 bytes")

    def test_codex_flooding_its_message_file_is_stopped_while_it_runs(self):
        started = time.monotonic()
        _, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--timeout", "40", codex="floodfile")
        self.assertLess(time.monotonic() - started, 30, "the cap was only applied at the timeout")
        self.assertEqual(summary["reviewer"], "gemini")
        self.assertEqual(summary["failover"][0]["reason"], "returned more than 2000000 bytes")

    def test_a_file_still_held_after_the_reviewer_exits_does_not_cost_the_round(self):
        result, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), codex="linger")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(summary["reviewer"], "astra")
        self.assertIn("(codex)", summary["review"])
        self.assertNotIn("left", result.stderr)
        self.assertEqual(list(self.scratch.iterdir()), [], "the reviewer's scratch directory was not removed")

    def test_a_reviewer_that_never_reads_a_large_prompt_still_times_out(self):
        # Larger than any pipe buffer: a blocking write here would hang past the timeout.
        self.prompt.write_text("Review this.\n" + "x" * 1_000_000, encoding="utf-8")
        started = time.monotonic()
        _, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), "--timeout", "3", codex="noread")
        self.assertLess(time.monotonic() - started, 20)
        self.assertEqual(summary["failover"][0], {"reviewer": "astra", "reason": "timed out"})

    def test_a_prompt_with_a_nul_byte_is_refused_before_any_reviewer_runs(self):
        self.prompt.write_text("Review this.\x00", encoding="utf-8")
        result, _ = self.dispatch("--writer", "codex", "--prompt", str(self.prompt))
        self.assertEqual(result.returncode, 2)
        self.assertIn("NUL byte", result.stderr)
        self.assertEqual(self.calls(), [])

    @unittest.skipIf(os.name == "nt", "Windows cannot reach a child once its reviewer has exited (see kill_tree)")
    def test_a_reviewers_children_do_not_outlive_it(self):
        _, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt), codex="orphan")
        self.assertEqual(summary["reviewer"], "astra")
        pid = int((Path(self._tmp.name) / "child.pid").read_text())
        for _ in range(50):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.1)
        os.kill(pid, 9)
        self.fail("the reviewer's child process was still running")

    def test_a_windows_shim_never_gets_prompt_text_in_its_arguments(self):
        spec = importlib.util.spec_from_file_location("dispatch_under_test", self.repo / "scripts/review-dispatch.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        reviewer = {"cli": "agy", "model": "gemini-4-argon-high"}
        argv, stdin = module.command(reviewer, "C:/tools/agy.cmd", "x & del *", Path("C:/p.md"), Path("o"), 60)
        self.assertEqual(argv[-1], f"-p=Follow the review instructions in the file {Path('C:/p.md')} exactly. Do not modify any file.")
        self.assertIsNone(stdin)
        argv, _ = module.command(reviewer, "/usr/bin/agy", "short prompt", Path("/p.md"), Path("o"), 60)
        self.assertEqual(argv[-1], "-p=short prompt")

    def test_a_reviewer_that_cannot_start_fails_over(self):
        # Installed, but not a program the system can start, so the launch itself fails.
        self.launchers["codex"].unlink()
        if os.name == "nt":
            (self.bin / "codex.exe").write_bytes(b"not a program")
        else:
            write_launcher(self.bin, "codex", "unused").write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
        _, summary = self.dispatch("--writer", "claude", "--prompt", str(self.prompt))
        self.assertEqual(summary["reviewer"], "gemini")
        self.assertTrue(summary["failover"][0]["reason"].startswith("could not start"), summary["failover"])

    def test_a_non_integer_schema_version_is_refused(self):
        # TOML true is Python True and 1.0 == 1, so both passed a `!= 1` check and loaded.
        pin = self.repo / ".conclave/reviewers.toml"
        good = pin.read_text()
        for bad in ("schema_version = true", "schema_version = 1.0"):
            with self.subTest(bad=bad):
                pin.write_text(good.replace("schema_version = 1", bad), encoding="utf-8")
                result, _ = self.dispatch("--writer", "claude", "--prompt", str(self.prompt))
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("needs exactly schema_version = 1, [reviewers.*] and [routes]", result.stderr)
                self.assertEqual(self.calls(), [])

    def test_a_bad_pin_refuses_before_any_reviewer_runs(self):
        pin = self.repo / ".conclave/reviewers.toml"
        good = pin.read_text()
        for bad in bad_pins(good):
            with self.subTest(bad=bad[-60:]):
                self.assertNotEqual(bad, good, "the replacement must match the fixture, or the case tests nothing")
                pin.write_text(bad, encoding="utf-8")
                result, _ = self.dispatch("--writer", "claude", "--prompt", str(self.prompt))
                self.assertEqual(result.returncode, 2)
                self.assertEqual(self.calls(), [])
        pin.unlink()
        result, _ = self.dispatch("--writer", "claude", "--prompt", str(self.prompt))
        self.assertEqual(result.returncode, 2)
        self.assertIn("no reviewer pin", result.stderr)


def bad_pins(good):
    """Every rule a parsable pin can break, each as one edit of the shipped pin, shared by the review and check tests."""
    mini = '\n[reviewers.mini]\ncli = "codex"\nmodel = "gpt-6-mini"\neffort = "low"\n'
    return (good.replace('effort = "medium"', 'effort = "extreme"'),
            good.replace('cli = "codex"', 'cli = "bash"'),
            good.replace('codex = ["gemini", "sonnet"]', 'codex = ["gemini", "opus"]'),
            good.replace('model = "gpt-6-astra"', 'model = "gpt-6-astra; rm -rf ~"'),
            good + '\n[extra]\nkey = 1\n',
            good.replace('codex = ["gemini", "sonnet"]', 'codex = [["gemini"], "sonnet"]'),
            good.replace('model = "gemini-4-argon-high"', 'model = "gemini-4-argon-high"\neffort = "high"'),
            # A reviewer of the writer's own family, and a second fallback.
            good.replace('claude = ["astra", "gemini"]', 'claude = ["astra", "sonnet"]'),
            good.replace('gemini = ["astra", "sonnet"]', 'gemini = ["gemini", "sonnet"]'),
            good.replace('claude = ["astra", "gemini"]', 'claude = ["astra", "gemini", "mini"]') + mini,
            # A fallback of the reviewer's own family is not the third family the route promises.
            good.replace('claude = ["astra", "gemini"]', 'claude = ["astra", "mini"]') + mini)


class RepositoryPin(unittest.TestCase):
    def test_the_repository_pin_loads_under_the_dispatchers_rules(self):
        spec = importlib.util.spec_from_file_location("dispatch_pin_check", SCRIPTS / "review-dispatch.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        pin = module.load_pin(REPO_PIN)
        self.assertTrue(pin["routes"], "the repository pin routes no writer")


if __name__ == "__main__":
    unittest.main()
