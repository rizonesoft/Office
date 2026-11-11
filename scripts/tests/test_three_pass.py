# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/review-dispatch.py under policy = "three-pass": the pass order, the section's own pin, the caps, blocking
levels, lens verdict lines and conditional lenses, driven through the command line with a fake reviewer in a real git
repository."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap
import time
import unittest
import unittest.mock

# The scratch repository and the fake reviewer CLIs; unittest discovery puts this folder on sys.path.
from test_review_dispatch import Harness

PIN = textwrap.dedent('''\
    schema_version = 1

    [reviewers.sol]
    cli = "codex"
    model = "gpt-6.1-sol"
    effort = "xhigh"

    [routes]
    claude = ["sol"]
    gemini = ["sol"]

    [schedule]
    policy = "three-pass"
    pass_cap = 5

    [schedule.lenses]
    concurrency = "Which lock or teardown order is wrong on two CPUs?"

    [schedule.plan]
    effort = "medium"
    lenses = ["plan"]

    [[schedule.rounds]]
    effort = "medium"
    lenses = ["adversarial", "integration"]

    [schedule.completion]
    effort = "medium"
    lenses = ["plan-delivery", "record"]

    [schedule.reconciliation]
    effort = "medium"
    lenses = ["adversarial", "plan-delivery", "record"]

    [[schedule.conditional]]
    lenses = ["concurrency"]
    passes = ["plan", "round"]
    paths = ["src/kernel/"]
''')
RECORD = "docs/reviews/00-core/D00-T01-s1.md"


def reply(kind, lenses, top="none", gaps=False):
    """A complete reply of one kind: a verdict line per lens, HIGHEST, and the kind's final lines."""
    lines = [f"LENS {name}: {'findings' if gaps else 'clean'}" for name in lenses] + [f"HIGHEST: {top}"]
    if kind == "plan":
        lines += ["PLAN: gaps" if gaps else "PLAN: complete"]
    if kind in ("plan", "round"):
        lines += ["OVERALL: needs-attention" if gaps else "OVERALL: approve"]
    else:
        lines += [f"{kind.upper()}: {'gaps' if gaps else 'complete'}"]
    return "\n".join(["1. P2 a.py:3 is wrong." if gaps else "Nothing found.", *lines])


LENSES = {"plan": ["plan"], "round": ["adversarial", "integration"], "completion": ["plan-delivery", "record"],
          "reconciliation": ["adversarial", "plan-delivery", "record"]}


class ThreePass(Harness):
    def setUp(self):
        super().setUp()
        self.git_dir = str(Path(shutil.which("git")).parent)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "T")
        self.git("config", "core.autocrlf", "false")
        self.record = self.repo / RECORD
        self.base = self.commit("pin", {".conclave/reviewers.toml": PIN})

    def git(self, *args):
        done = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True, timeout=60)
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout.strip()

    def commit(self, message, files=None):
        for name, text in (files or {}).items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD")

    def dispatch(self, *args, **modes):
        # The dispatcher asks git for the section's pin and changed files, so git is on the fake PATH here.
        system_root = {"SYSTEMROOT": os.environ["SYSTEMROOT"]} if os.name == "nt" else {}
        env = {"PATH": os.pathsep.join([str(self.bin), str(Path(sys.executable).parent), self.git_dir]),
               "FAKE_LOG": str(self.log), "FAKE_CHILD_PID": str(Path(self._tmp.name) / "child.pid"), **system_root,
               **{var: str(self.scratch) for var in ("TMP", "TEMP", "TMPDIR")},
               **{f"FAKE_{k.upper()}": v for k, v in modes.items()}}
        result = subprocess.run([sys.executable, "-B", str(self.repo / "scripts/review-dispatch.py"), *args],
                                capture_output=True, text=True, env=env, timeout=60, cwd=str(self.repo))
        summary = json.loads(result.stdout) if result.stdout.strip().startswith("{") else None
        return result, summary

    def run_pass(self, kind, candidate, say=None, top="none", gaps=False, extra=(), record=True, writer="claude"):
        say = reply(kind, LENSES[kind], top, gaps) if say is None else say
        args = ["--kind", kind, "--writer", writer, "--prompt", str(self.prompt), *extra]
        args += ["--candidate", candidate] if candidate else []
        args += ["--record", str(self.record)] if record else []
        return self.dispatch(*args, codex="say", say=say)

    def refused(self, kind, candidate, needle, **kwargs):
        before = len(self.calls())
        result, _ = self.run_pass(kind, candidate, **kwargs)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(needle, result.stderr)
        self.assertEqual(len(self.calls()), before, "a refused pass must not reach the reviewer")

    def ok(self, kind, candidate, **kwargs):
        result, summary = self.run_pass(kind, candidate, **kwargs)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return summary

    def findings(self):
        return self.module().read_findings(self.record.read_bytes().decode("utf-8"))

    def to_completion(self, top="P2", gaps=True):
        """Plan, build, round, then a completion review; returns the last candidate."""
        self.ok("plan", self.base)
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        self.ok("round", built)
        self.ok("completion", built, top=top, gaps=gaps)
        return built


class Chain(ThreePass):
    def test_a_whole_chain_runs_and_reads_back(self):
        plan = self.ok("plan", self.base, gaps=True, top="P2")
        self.assertEqual((plan["kind"], plan["candidate"], plan["lenses"], plan["effort"]),
                         ("plan", self.base, ["plan"], "medium"))
        self.assertEqual((plan["highest"], plan["blocking"]), ("P2", True))
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        rnd = self.ok("round", built)
        self.assertEqual((rnd["position"], rnd["severity_stop"], rnd["escalated"], rnd["round"], rnd["candidate"]),
                         (1, False, False, 1, built))
        self.assertEqual((rnd["highest"], rnd["blocking"]), ("none", False))
        completion = self.ok("completion", built, gaps=True, top="P2")
        self.assertEqual(completion["lenses"], ["plan-delivery", "record"])
        repaired = self.commit("repair", {"src/app/a.py": "x = 2\n"})
        done = self.ok("reconciliation", repaired)
        self.assertEqual((done["kind"], done["candidate"], done["recorded"]), ("reconciliation", repaired, True))
        found = self.findings()
        self.assertEqual([len(found[k]) for k in ("plans", "rounds", "completions", "reconciliations")], [1, 1, 1, 1])
        self.assertEqual(found["rounds"][0]["candidate"], built)
        self.assertEqual(found["reconciliations"][0]["lenses"], ["adversarial", "plan-delivery", "record"])
        listing, _ = self.dispatch("--list-rounds", "--records", str(self.repo / "docs/reviews"))
        self.assertIn("Reconciliation review: sol", listing.stdout)
        # The reviewer was given each lens's question and the verdict line it owes.
        prompt = self.calls()[1]["stdin"]
        self.assertIn("LENS adversarial: <clean|findings>", prompt)
        self.assertIn("- `integration`:", prompt)

    def test_a_pass_out_of_order_is_refused_before_a_reviewer_runs(self):
        self.refused("round", self.base, "needs the section's returned plan review first")
        self.refused("completion", self.base, "needs the section's returned plan review first")
        self.ok("plan", self.base)
        self.refused("plan", self.base, "the plan review runs once")
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        self.refused("round", None, "a section's round needs --candidate")
        self.refused("round", "0" * 40, "is not a commit in this repository")
        self.git("checkout", "-q", "--orphan", "other")
        unrelated = self.commit("unrelated", {"z.txt": "z\n"})
        self.git("checkout", "-q", "main")
        self.refused("round", unrelated, "does not descend from the plan review's")
        self.refused("completion", built, "after the section's returned round")
        self.refused("reconciliation", built, "a reconciliation follows one round and a completion")
        self.ok("round", built)
        self.refused("round", built, "allows one round")
        self.refused("completion", self.base, "does not descend from the round's")
        self.ok("completion", built, gaps=True, top="P2")
        self.refused("completion", built, "runs once")
        self.refused("reconciliation", self.base, "does not descend from the last pass's")
        repaired = self.commit("repair", {"src/app/a.py": "x = 2\n"})
        self.ok("reconciliation", repaired)
        self.refused("reconciliation", repaired, "already returned complete")

    def lock_path(self, record):
        module = self.module()
        with unittest.mock.patch.object(module.tempfile, "gettempdir", return_value=str(self.scratch)):
            return module.section_lock_path(str(record))

    def test_a_second_launch_of_a_sections_pass_is_refused_while_the_first_runs(self):
        # Rounds 2 and 3 of D00 T01 §2: two launches both passed the order check and both spent a review, and a
        # launch with a shorter timeout took a live review's lock.
        self.ok("plan", self.base)
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        lock = self.lock_path(self.record)
        live = f"12345 {time.time() + 1800:.0f} feedfeedfeedfeed"
        lock.write_text(live, encoding="ascii")
        # The running review's own expiry decides, not this launch's timeout.
        self.refused("round", built, "is already running", extra=("--timeout", "1"))
        self.assertEqual(lock.read_text(encoding="ascii"), live, "a refused launch must leave the other run's lock")
        # A lock past the expiry its owner wrote belongs to a dead run: it is taken over, and released afterwards.
        lock.write_text(f"12345 {time.time() - 5:.0f} feedfeedfeedfeed", encoding="ascii")
        self.ok("round", built)
        self.assertFalse(lock.exists())
        self.assertFalse(lock.with_name(lock.name + ".takeover").exists())

    def test_an_expired_lock_is_taken_over_by_one_launch_at_a_time(self):
        self.ok("plan", self.base)
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        lock = self.lock_path(self.record)
        expired = f"12345 {time.time() - 5:.0f} feedfeedfeedfeed"
        lock.write_text(expired, encoding="ascii")
        takeover = lock.with_name(lock.name + ".takeover")
        takeover.write_text("another launch", encoding="ascii")
        self.refused("round", built, "is already running")
        self.assertEqual(lock.read_text(encoding="ascii"), expired)
        # An abandoned takeover is cleared, so the launch after it goes through.
        old = time.time() - 3600
        os.utime(takeover, (old, old))
        self.refused("round", built, "is already running")
        self.assertFalse(takeover.exists())
        self.ok("round", built)
        # A lock that cannot be read is believed for the grace period, then taken over.
        lock.write_text("garbage", encoding="ascii")
        self.refused("completion", built, "is already running")
        os.utime(lock, (old, old))
        self.ok("completion", built)

    def test_a_review_outside_a_section_takes_no_lock(self):
        self.record = self.repo / "docs/reviews/topic.md"
        other = self.lock_path(self.record)
        other.write_text(f"12345 {time.time() + 1800:.0f} feedfeedfeedfeed", encoding="ascii")
        self.ok("round", None)

    def test_a_completion_that_is_complete_takes_no_reconciliation(self):
        built = self.to_completion(top="none", gaps=False)
        self.refused("reconciliation", built, "a completion review that returned gaps")

    def test_a_rotation_pin_has_no_reconciliation_and_takes_no_paths(self):
        rotation = PIN.partition("[schedule]")[0]
        base = self.commit("no schedule", {".conclave/reviewers.toml": rotation})
        self.record = self.repo / "docs/reviews/00-core/D00-T01-s2.md"
        self.refused("reconciliation", base, "only policy = \"three-pass\" takes one")
        self.refused("round", None, "--paths goes with a three-pass pin", extra=("--paths", "src/kernel/a.c"))


class Incomplete(ThreePass):
    def test_a_reply_missing_a_lens_line_is_recorded_as_no_review_and_can_be_rerun(self):
        self.ok("plan", self.base)
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        partial = reply("round", ["adversarial"])
        result, summary = self.run_pass("round", built, say=partial)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIsNone(summary["reviewer"])
        self.assertEqual(summary["incomplete"], ["integration"])
        self.assertIn("incomplete: no LENS verdict line for integration", summary["failover"][0]["reason"])
        self.assertEqual(summary["review"].splitlines(), partial.splitlines())
        text = self.record.read_text(encoding="utf-8")
        self.assertIn("## Round 1: none", text)
        self.assertIn("- Skipped: sol (incomplete: no LENS verdict line for integration)", text)
        self.assertIn("LENS adversarial: clean", text)
        # It did not count as the section's round: the round runs again, and only then may the completion follow.
        self.refused("completion", built, "after the section's returned round")
        again = self.ok("round", built)
        self.assertEqual((again["round"], again["position"]), (2, 1))
        self.ok("completion", built)

    def test_a_complete_verdict_that_declares_a_blocking_finding_is_not_a_review(self):
        # Round 1 of D00 T01 §3: HIGHEST: P1 then COMPLETION: complete was recorded as a complete completion.
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        self.ok("plan", self.base)
        self.ok("round", built)
        result, summary = self.run_pass("completion", built, top="P1", gaps=False)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ends COMPLETION: complete but declares HIGHEST: P1", summary["failover"][0]["reason"])
        self.assertIn("COMPLETION: complete", summary["review"])
        # It did not count: the completion review runs again.
        self.ok("completion", built)

    def test_a_reply_without_its_final_verdict_lines_is_incomplete_for_every_kind(self):
        no_footer = "LENS plan: clean\nHIGHEST: none\nLooks fine."
        result, summary = self.run_pass("plan", self.base, say=no_footer)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no final plan verdict line", summary["failover"][0]["reason"])
        self.ok("plan", self.base)
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        self.ok("round", built)
        result, summary = self.run_pass("completion", built, say="LENS plan-delivery: clean\nLENS record: clean\nfine")
        self.assertEqual(result.returncode, 1)
        self.assertIn("no final completion verdict line", summary["failover"][0]["reason"])
        self.ok("completion", built, gaps=True, top="P2")
        repaired = self.commit("repair", {"src/app/a.py": "x = 2\n"})
        result, _ = self.run_pass("reconciliation", repaired, say=reply("reconciliation", ["adversarial"]))
        self.assertEqual(result.returncode, 1)
        # Four returned passes so far under pass_cap 5: the failed attempts did not count, so this one still runs.
        self.ok("reconciliation", repaired)
        found = self.findings()
        self.assertEqual([len(found[k]) for k in ("plans", "completions", "reconciliations")], [2, 2, 2])


class Caps(ThreePass):
    def gaps_until_refused(self, tops):
        """Completion with gaps, then one reconciliation with gaps per severity in `tops`; returns the last commit."""
        built = self.to_completion(top=tops[0])
        for n, top in enumerate(tops[1:], 1):
            built = self.commit(f"repair {n}", {"src/app/a.py": f"x = {n + 1}\n"})
            self.ok("reconciliation", built, gaps=True, top=top)
        return built

    def test_a_section_that_has_spent_its_passes_is_refused(self):
        last = self.gaps_until_refused(["P2", "P2", "P2"])   # plan, round, completion, two reconciliations: five
        again = self.commit("repair again", {"src/app/a.py": "x = 9\n"})
        self.refused("reconciliation", again, "has spent its 5 review passes (pass_cap)")
        del last

    def test_the_cap_is_the_one_in_the_sections_own_pin(self):
        self.base = self.commit("cap 4", {".conclave/reviewers.toml": PIN.replace("pass_cap = 5", "pass_cap = 4")})
        self.gaps_until_refused(["P2", "P2"])
        # Raising the cap in a later commit does not reach a section whose plan review read the earlier pin.
        again = self.commit("cap 9", {".conclave/reviewers.toml": PIN.replace("pass_cap = 5", "pass_cap = 9")})
        self.refused("reconciliation", again, "has spent its 4 review passes (pass_cap)")

    def test_no_progress_cap_counts_reconciliations_that_got_no_less_severe(self):
        stalled = PIN.replace("pass_cap = 5", "pass_cap = 30\nno_progress_cap = 2")
        self.base = self.commit("stall 2", {".conclave/reviewers.toml": stalled})
        # P1, then P2 (progress), then P2 and P2: two in a row without progress.
        self.gaps_until_refused(["P1", "P2", "P2"])
        mid = self.commit("repair mid", {"src/app/a.py": "x = 50\n"})
        # One stalled pass so far, and a failed attempt does not add to it.
        result, _ = self.run_pass("reconciliation", mid, say="no verdict lines at all")
        self.assertEqual(result.returncode, 1)
        self.ok("reconciliation", mid, gaps=True, top="P2")
        last = self.commit("repair last", {"src/app/a.py": "x = 51\n"})
        self.refused("reconciliation", last, "made no progress (no_progress_cap 2)")

    def test_without_no_progress_cap_only_pass_cap_stops_the_loop(self):
        self.base = self.commit("cap 8", {".conclave/reviewers.toml": PIN.replace("pass_cap = 5", "pass_cap = 8")})
        last = self.gaps_until_refused(["P2", "P2", "P2", "P2", "P2", "P2"])
        self.refused("reconciliation", self.commit("more", {"src/app/a.py": "x = 99\n"}), "pass_cap")
        del last


class Blocking(ThreePass):
    def setUp(self):
        super().setUp()
        pin = PIN.replace("pass_cap = 5", 'pass_cap = 9\nblocking = ["P1", "P2"]')
        self.base = self.commit("blocking", {".conclave/reviewers.toml": pin})

    def test_a_pass_below_the_blocking_levels_takes_no_further_pass(self):
        built = self.to_completion(top="P3")
        repaired = self.commit("repair", {"src/app/a.py": "x = 2\n"})
        self.refused("reconciliation", repaired, "worst finding is P3, below the pin's blocking levels (P1, P2)")
        del built

    def test_a_pin_without_blocking_never_ends_the_loop_on_severity(self):
        # Round 1 of D00 T01 §2: a reply ending HIGHEST: none then COMPLETION: gaps crashed on the missing key.
        self.base = self.commit("no blocking", {".conclave/reviewers.toml": PIN})
        self.to_completion(top="none")
        repaired = self.commit("repair", {"src/app/a.py": "x = 2\n"})
        self.ok("reconciliation", repaired)

    def test_a_blocking_pass_is_followed_by_a_reconciliation(self):
        self.to_completion(top="P2")
        repaired = self.commit("repair", {"src/app/a.py": "x = 2\n"})
        self.ok("reconciliation", repaired, gaps=True, top="P3")
        # That reconciliation ended below the blocking levels, so the loop ends there too.
        self.refused("reconciliation", self.commit("more", {"src/app/a.py": "x = 3\n"}), "below the pin's blocking")

    def test_the_summary_says_whether_the_worst_finding_blocks(self):
        for top, want in (("P2", ("P2", True)), ("P3", ("P3", False)), ("none", ("none", False))):
            with self.subTest(top=top):
                summary = self.ok("plan", self.base, top=top, gaps=top != "none", record=False)
                self.assertEqual((summary["highest"], summary["blocking"]), want)
        # Round 2 of D00 T01 §3: a reply with no HIGHEST line gave the blocking rule nothing to read. It is incomplete.
        silent = "LENS plan: findings\nPLAN: gaps\nOVERALL: needs-attention"
        result, summary = self.run_pass("plan", self.base, say=silent, record=False)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("no HIGHEST line", summary["failover"][0]["reason"])
        self.assertNotIn("blocking", summary)


class SectionPin(ThreePass):
    def test_a_section_finishes_under_the_pin_its_plan_review_read(self):
        self.ok("plan", self.base)
        changed = PIN.replace('model = "gpt-6.1-sol"', 'model = "gpt-9-other"').replace(
            'lenses = ["adversarial", "integration"]', 'lenses = ["quality"]')
        built = self.commit("pin moved", {".conclave/reviewers.toml": changed, "src/app/a.py": "x = 1\n"})
        summary = self.ok("round", built)
        self.assertEqual((summary["model"], summary["lenses"]), ("gpt-6.1-sol", ["adversarial", "integration"]))
        self.assertIn("gpt-6.1-sol", self.calls()[-1]["argv"])
        # A working-tree pin that no longer loads, or has switched policy, does not stop the section either.
        (self.repo / ".conclave/reviewers.toml").write_text("not toml [", encoding="utf-8")
        self.ok("completion", built)

    def test_a_plan_review_runs_under_the_pin_at_its_own_candidate(self):
        moved = self.commit("new route", {".conclave/reviewers.toml": PIN.replace("gpt-6.1-sol", "gpt-9-other")})
        summary = self.ok("plan", self.base)
        self.assertEqual(summary["model"], "gpt-6.1-sol")
        del moved

    def test_a_plan_candidate_without_a_loadable_pin_is_refused_naming_the_commit(self):
        self.git("rm", "-q", ".conclave/reviewers.toml")
        bare = self.commit("no pin")
        self.refused("plan", bare, "no reviewer pin at")
        broken = self.commit("broken pin", {".conclave/reviewers.toml": PIN.replace("pass_cap = 5", "pass_cap = 2")})
        self.refused("plan", broken, f"the reviewer pin at {broken} does not load: [schedule] pass_cap")

    def test_a_rotation_section_follows_the_working_tree_pin_as_it_always_did(self):
        # Round 1 of D00 T01 §2: keeping the plan review's pin is the three-pass rule; a rotation section is not bound.
        rotation = PIN.partition("[schedule]")[0]
        base = self.commit("rotation", {".conclave/reviewers.toml": rotation})
        self.ok("plan", base, say="x\nPLAN: complete\nOVERALL: approve")
        self.commit("new model", {".conclave/reviewers.toml": rotation.replace("gpt-6.1-sol", "gpt-9-other")})
        summary = self.ok("round", None, say="fine\nOVERALL: approve")
        self.assertEqual(summary["model"], "gpt-9-other")

    def test_a_three_pass_plan_review_needs_its_pin_committed_at_the_candidate(self):
        # Round 4 of D00 T01 §2: a pin that exists only in the working tree froze nothing for the section.
        rotation = PIN.partition("[schedule]")[0]
        for label, text in (("rotation pin committed", rotation), ("no pin committed", None)):
            with self.subTest(case=label):
                if text is None:
                    self.git("rm", "-q", "-f", ".conclave/reviewers.toml")
                    candidate = self.commit("no pin")
                else:
                    candidate = self.commit("rotation", {".conclave/reviewers.toml": text})
                (self.repo / ".conclave").mkdir(exist_ok=True)
                (self.repo / ".conclave/reviewers.toml").write_text(PIN, encoding="utf-8")
                self.refused("plan", candidate, f"the plan review's candidate {candidate} does not hold it")
                self.git("add", "-A")

    def test_a_section_that_began_under_rotation_finishes_under_it_after_the_switch(self):
        rotation = PIN.partition("[schedule]")[0]
        base = self.commit("rotation", {".conclave/reviewers.toml": rotation})
        self.ok("plan", base, say="x\nPLAN: complete\nOVERALL: approve")
        self.commit("switch to three-pass", {".conclave/reviewers.toml": PIN.replace("gpt-6.1-sol", "gpt-9-other")})
        # Under the three-pass pin this second round would be refused and the model would be the new one.
        for number in (1, 2):
            summary = self.ok("round", None, say="fine\nOVERALL: approve")
            self.assertEqual((summary["round"], summary["model"]), (number, "gpt-6.1-sol"))
            self.assertNotIn("blocking", summary)

    def test_a_respelled_findings_path_is_still_the_sections_on_windows(self):
        self.ok("plan", self.base)
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        self.ok("round", built)
        if os.name != "nt":
            self.skipTest("only Windows opens a differently cased path as the same file")
        self.record = self.repo / RECORD.replace("docs/reviews", "DOCS/Reviews")
        self.refused("round", built, "allows one round")

    def test_a_review_outside_a_section_uses_the_working_tree_pin(self):
        self.record = self.repo / "docs/reviews/topic.md"
        (self.repo / ".conclave/reviewers.toml").write_text(PIN.replace("gpt-6.1-sol", "gpt-9-other"),
                                                            encoding="utf-8")
        self.assertEqual(self.ok("round", None)["model"], "gpt-9-other")
        # No order outside a section: a second round is just another round.
        self.assertEqual(self.ok("round", None)["round"], 2)


class Conditional(ThreePass):
    def test_a_conditional_lens_joins_a_pass_whose_candidate_changed_a_matching_file(self):
        self.ok("plan", self.base)
        built = self.commit("kernel", {"src/kernel/schéd.c": "int x;\n", "README.md": "x\n"})
        both = LENSES["round"] + ["concurrency"]
        summary = self.ok("round", built, say=reply("round", both))
        self.assertEqual(summary["lenses"], both)
        self.assertIn("- `concurrency`: Which lock or teardown order is wrong on two CPUs?",
                      self.calls()[-1]["stdin"])
        self.assertEqual(self.findings()["rounds"][0]["lenses"], both)
        # Completion is not one of the entry's passes.
        self.assertEqual(self.ok("completion", built)["lenses"], LENSES["completion"])

    def test_a_failed_changed_file_lookup_is_a_refusal(self):
        # Round 5 of D00 T01 §2: the test below stops at the pin lookup, so the diff failure itself had no test.
        module = self.module()
        self.assertEqual(module.changed_paths(self.base, self.base), [])
        with self.assertRaises(module.Refused) as refused:
            module.changed_paths("0" * 40, self.base)
        self.assertIn("cannot list the files changed between", str(refused.exception))

    def test_a_missing_git_refuses_before_a_reviewer_runs(self):
        self.ok("plan", self.base)
        built = self.commit("build", {"src/kernel/a.c": "int x;\n"})
        before = len(self.calls())
        # The base harness's PATH holds the fake reviewers and Python only: git cannot be found.
        result, _ = Harness.dispatch(self, "--kind", "round", "--writer", "claude", "--prompt", str(self.prompt),
                                     "--candidate", built, "--record", str(self.record), codex="say",
                                     say=reply("round", LENSES["round"]))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("review-dispatch refused", result.stderr)
        self.assertEqual(len(self.calls()), before)
        self.assertEqual(len(self.findings()["rounds"]), 0)

    def test_a_file_moved_out_of_a_watched_folder_still_counts(self):
        self.base = self.commit("kernel file", {"src/kernel/a.c": "int x;\nint y;\nint z;\n"})
        self.ok("plan", self.base)
        (self.repo / "src/app").mkdir(parents=True, exist_ok=True)
        self.git("mv", "src/kernel/a.c", "src/app/a.c")
        moved = self.commit("moved out")
        both = LENSES["round"] + ["concurrency"]
        self.assertEqual(self.ok("round", moved, say=reply("round", both))["lenses"], both)

    def test_no_matching_file_means_no_conditional_lens(self):
        self.ok("plan", self.base)
        built = self.commit("app only", {"src/app/a.py": "x = 1\n", "src/kernelish.c": "int y;\n"})
        self.assertEqual(self.ok("round", built)["lenses"], LENSES["round"])

    def test_paths_serve_a_plan_review_and_a_standalone_review_only(self):
        summary = self.ok("plan", self.base, say=reply("plan", ["plan", "concurrency"]),
                          extra=("--paths", "src\\kernel\\a.c"))
        self.assertEqual(summary["lenses"], ["plan", "concurrency"])
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        self.refused("round", built, "--paths goes with a plan review or a review outside a section",
                     extra=("--paths", "src/kernel/a.c"))
        self.record = self.repo / "docs/reviews/topic.md"
        standalone = self.ok("round", None, say=reply("round", LENSES["round"] + ["concurrency"]),
                             extra=("--paths", "src/kernel/a.c", "docs/x.md"))
        self.assertEqual(standalone["lenses"], LENSES["round"] + ["concurrency"])

    def test_surface_still_gates_design_on_a_pin_without_conditional_entries(self):
        plain = PIN.partition("[[schedule.conditional]]")[0].replace(
            'lenses = ["adversarial", "integration"]', 'lenses = ["adversarial", "design"]')
        self.base = self.commit("design in the round", {".conclave/reviewers.toml": plain})
        self.ok("plan", self.base)
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        self.record = self.repo / "docs/reviews/topic.md"
        (self.repo / ".conclave/reviewers.toml").write_text(plain, encoding="utf-8")
        self.assertEqual(self.ok("round", None, say=reply("round", ["adversarial"]))["lenses"], ["adversarial"])
        with_surface = self.ok("round", None, say=reply("round", ["adversarial", "design"]), extra=("--surface",))
        self.assertEqual(with_surface["lenses"], ["adversarial", "design"])
        del built


class Writers(ThreePass):
    def test_agy_and_gemini_are_one_writer(self):
        # The fixture routes `gemini`; a review asked for as `agy` finds that route, and the other way round.
        self.assertEqual(self.ok("plan", self.base, writer="agy", record=False)["writer"], "agy")
        swapped = self.commit("agy route", {".conclave/reviewers.toml": PIN.replace('gemini = ["sol"]', 'agy = ["sol"]')})
        (self.repo / ".conclave/reviewers.toml").write_text(PIN.replace('gemini = ["sol"]', 'agy = ["sol"]'),
                                                            encoding="utf-8")
        self.assertEqual(self.ok("plan", swapped, writer="gemini", record=False)["reviewer"], "sol")
        module = self.module()
        both = PIN.replace('gemini = ["sol"]', 'gemini = ["sol"]\nagy = ["sol"]')
        with self.assertRaises(module.Refused) as refused:
            module.load_pin(data=both.encode("utf-8"))
        self.assertIn("names both agy and gemini, which are one writer", str(refused.exception))
        own = PIN.replace('cli = "codex"\nmodel = "gpt-6.1-sol"\neffort = "xhigh"',
                          'cli = "agy"\nmodel = "gemini-4-argon-medium"').replace(
            'claude = ["sol"]\ngemini = ["sol"]', 'agy = ["sol"]')
        with self.assertRaises(module.Refused) as refused:
            module.load_pin(data=own.encode("utf-8"))
        self.assertIn("route 'agy' names sol, of the writer's own family", str(refused.exception))
        # A recorded round by the agy writer counts as a review from another family.
        entry = {"reviewer": "sol", "writer": "agy", "cli": "codex", "review": "x\nOVERALL: approve"}
        self.assertTrue(module.returned_review(entry))


class NoLenses(ThreePass):
    def test_a_pass_with_no_lenses_is_still_asked_for_its_highest_line(self):
        # D00 T01 §4: a completion step without lenses (a pin from before completion had its own) got no appended
        # request, so its reply had no HIGHEST line and was recorded as incomplete.
        earlier = PIN.replace('[schedule.completion]\neffort = "medium"\nlenses = ["plan-delivery", "record"]',
                              '[schedule.completion]\neffort = "medium"')
        self.assertNotEqual(earlier, PIN)
        self.base = self.commit("completion without lenses", {".conclave/reviewers.toml": earlier})
        self.ok("plan", self.base)
        built = self.commit("build", {"src/app/a.py": "x = 1\n"})
        self.ok("round", built)
        summary = self.ok("completion", built, say="Nothing missing.\nHIGHEST: none\nCOMPLETION: complete")
        self.assertEqual(summary["lenses"], [])
        prompt = self.calls()[-1]["stdin"]
        self.assertIn("write one line `HIGHEST: P1`", prompt)
        self.assertNotIn("LENS ", prompt)
        (entry,) = self.findings()["completions"]
        self.assertEqual(entry["reviewer"], "sol")


class Antigravity(ThreePass):
    def test_a_pass_reviewed_through_antigravity_records_the_scheduled_effort(self):
        # Completion review of D00 T01 §3: the record held no effort, so the stamp's replay of the schedule refused it.
        argon = PIN.replace('cli = "codex"\nmodel = "gpt-6.1-sol"\neffort = "xhigh"',
                            'cli = "agy"\nmodel = "gemini-4-argon-medium"').replace('gemini = ["sol"]\n', "")
        self.base = self.commit("antigravity reviewer", {".conclave/reviewers.toml": argon})
        module = self.module()
        schedule = module.load_pin(self.repo / ".conclave/reviewers.toml")["schedule"]
        say = reply("plan", LENSES["plan"])
        result, summary = self.dispatch("--kind", "plan", "--writer", "claude", "--prompt", str(self.prompt),
                                        "--candidate", self.base, "--record", str(self.record), agy="say", say=say)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((summary["cli"], summary["effort"]), ("agy", "medium"))
        self.assertFalse([a for a in self.calls()[-1]["argv"] if "effort" in a])
        (entry,) = self.findings()["plans"]
        expected = module.scheduled(schedule, "plan", [], False)
        self.assertEqual((entry["effort"], entry["lenses"]), (expected["effort"], expected["lenses"]))


class Decoding(ThreePass):
    def test_a_reply_is_utf8_or_windows_1252_and_never_raises(self):
        module = self.module()
        self.assertEqual(module.decode_reply("it’s é".encode("utf-8")), "it’s é")
        self.assertEqual(module.decode_reply(b"it\x92s"), "it’s")
        self.assertEqual(module.decode_reply(b"a\x81b"), "a�b")


if __name__ == "__main__":
    unittest.main()
