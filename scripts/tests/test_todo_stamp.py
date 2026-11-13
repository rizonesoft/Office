# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Tests for stamping in scripts/lib/todo_graph.py: a stamp binds a section to its plan review, its rounds and its
completion review under the schedule of the pin it ran under, rotation or three-pass."""
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
import todo_graph as tg  # noqa: E402
from test_todo_graph import git_started  # noqa: E402  (discovery puts this folder on the path)

ADJACENCY = ("**Adjacency:** list=not-applicable (fixture); document=not-applicable (fixture); "
             "settings=not-applicable (fixture); reporting=not-applicable (fixture); "
             "notifications=not-applicable (fixture); permissions=not-applicable (fixture); "
             "audit=not-applicable (fixture); exchange=not-applicable (fixture); "
             "reverse=not-applicable (fixture)")


def section(n, title, phase, needs, extra=""):
    # A section waiting on the owner carries an owner action (D00 T03 §35), so every fixture is valid as written.
    waits = bool({v.strip() for v in needs.split(",")} & tg.OWNER_NEEDS)
    action = "**Owner action:** answer in the session; the session records it and removes the Need.\n" if waits else ""
    return (f"## {n}. {title}\n\n**Phase:** {phase}\n**Needs:** {needs}\n{action}**Surface:** no\n\n**Build order:**\n\n"
            f"1. Do it. Done when: it shows.\n\n- [ ] Work.\n- [ ] Commit: `x: {title.lower()}`\n\n"
            f"**Test checkpoint:** `true` exits 0.{extra}\n")


def envelope(n, reviewer="astra (`m` via `codex`)", overall="approve"):
    """One round as scripts/review-dispatch.py records it (without the optional Lines and Digest fields), at the
    uniform schedule the Stamp fixture pins."""
    return (f"## Round {n}: {reviewer}\n\n- Writer: claude\n- Run: 2026-10-21T00:00:00Z\n- Effort: low\n"
            f"- Lenses: adversarial\n\nReview text.\n\nOVERALL: {overall}\n\n")


# A reviewer pin whose schedule runs every round at the same effort and lens, so tests that are not about the schedule
# need not follow one; SCHEDULE_PIN is the live shape the schedule tests use.
UNIFORM_PIN = """schema_version = 1

[reviewers.astra]
cli = "codex"
model = "m"
effort = "medium"

[routes]
claude = ["astra"]

[schedule]
severity_stop_after = 3
plan = { effort = "medium", lenses = ["plan"] }
completion = { effort = "medium" }
rounds = [{ effort = "low", lenses = ["adversarial"] }]
rotation = { effort = "low", lenses = ["adversarial"] }
escalation = { effort = "low", lenses = ["adversarial"] }
"""
SCHEDULE_PIN = UNIFORM_PIN.split("[schedule]")[0] + """[schedule]
severity_stop_after = 3
plan = { effort = "medium", lenses = ["plan"] }
completion = { effort = "medium" }
rounds = [{ effort = "high", lenses = ["adversarial", "integration", "source-defect", "plan-delivery"] },
          { effort = "medium", lenses = ["adversarial"] }, { effort = "low", lenses = ["adversarial"] }]
rotation = { effort = "low", lenses = ["consistency", "quality", "design", "optimization", "record"] }
escalation = { effort = "medium", lenses = ["adversarial"] }
"""
STARTED = "> **Started:** 2026-10-23T00:00Z\n\n"


def todo_file(rows, *, ident="alpha", domain="00-workspace", status="active", depends_on=None,
              table_override=None, inputs="- i"):
    """rows: (number, title, phase, needs, depends) tuples."""
    front = ["schema_version: 1", f"id: {ident}", f"domain: {domain}", f"status: {status}",
             'title: "TODO-01 -- A"']
    if depends_on is not None:
        front.append("depends_on: " + json.dumps(depends_on))
    table = table_override or "\n".join(
        f"| {i} | §{n} | {t} | {dep} | [ ] |" for i, (n, t, _, _, dep) in enumerate(rows, 1))
    bodies = "\n".join(section(n, t, ph, nd) for n, t, ph, nd, _ in rows)
    return ("---\n" + "\n".join(front) + "\n---\n\n# TODO-01 -- A\n\n> **Goal:** g.\n\n"
            "> **Current state:** c.\n\n## Inputs\n\n" + inputs + "\n\n## Outcome\n\n- o\n\n"
            + ADJACENCY + "\n\n"
            "## Implementation Order\n\n| Order | Section | Deliverable | Depends On | Status |\n"
            "| ----- | ------- | ----------- | ---------- | ------ |\n"
            + table + "\n\n" + bodies + "\n## Verification\n\n- v\n")


class Tree(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "todo/00-workspace").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, text, name="TODO-01-a.md", domain="00-workspace", index=True):
        d = self.root / "todo" / domain
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(text, encoding="utf-8")
        if index:
            self.index(name, domain)

    def index(self, name, domain="00-workspace"):
        domain_index = self.root / "todo" / domain / "INDEX.md"
        existing = domain_index.read_text(encoding="utf-8") if domain_index.exists() else "# Index\n"
        if name not in existing:
            domain_index.write_text(existing + f"- {name}\n", encoding="utf-8")
        root_index = self.root / "todo/TODO-00-INDEX.md"
        root_existing = root_index.read_text(encoding="utf-8") if root_index.exists() else "# Index\n"
        entry = f"{domain}/{name}"
        if entry not in root_existing:
            root_index.write_text(root_existing + f"- {entry}\n", encoding="utf-8")

    def refuses(self, fragment):
        with self.assertRaises(tg.Refused) as ctx:
            tg.graph(self.root)
        self.assertIn(fragment, str(ctx.exception))


class Stamp(Tree):
    def setUp(self):
        super().setUp()
        self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "owner-decision", "--")]).replace(
            "**Test checkpoint:**", STARTED + "**Test checkpoint:**", 1))
        report_path = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("# Review findings\n\n" + envelope(1), encoding="utf-8")
        (self.root / ".conclave").mkdir()
        (self.root / tg.PIN).write_text(self.PIN_TEXT, encoding="utf-8")
        for args in (["init", "-q"], ["config", "user.email", "t@example.com"],
                     ["config", "user.name", "T"], ["add", "-A"], ["commit", "-qm", "x"]):
            subprocess.run(["git", "-C", str(self.root), *args], check=True)
        self.sha = self.head()
        self.start = self.sha  # the commit that records §1's Started line: the build began here
        self.reviews = [{"round": 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md",
                         "verdict": "clean"}]
        self.write_completion()
        self.write_plan()

    COMPLETION = "docs/reviews/00-workspace/D00-T01-s1-completion.md"
    PLAN = "docs/reviews/00-workspace/D00-T01-s1.md"  # the section's own findings file, beside its rounds
    PIN_TEXT = UNIFORM_PIN  # the pin the first commit holds; ThreePassStamp commits a three-pass one there

    @staticmethod
    def only(text, plans):
        """The findings file text with only its plan reviews (plans) or with every record but them, header kept."""
        head, *records = re.split(r"(?m)^(?=## (?:Round |Plan review))", text)
        return head + "".join(r for r in records if r.startswith("## Plan review") == plans)

    def head(self):
        return subprocess.run(["git", "-C", str(self.root), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()

    def commit(self, message="more"):
        for args in (["add", "-A"], ["commit", "-q", "--allow-empty", "-m", message]):
            subprocess.run(["git", "-C", str(self.root), *args], check=True)
        return self.head()

    def write_plan(self, review="1. Controls: all present.\n\nHIGHEST: none\n\nPLAN: complete\n\nOVERALL: approve",
                   reviewer="astra", cli="codex", writer="claude", effort="medium", lenses=("plan",), candidate=None,
                   path=None, keep=False):
        """A plan review as scripts/review-dispatch.py --kind plan records it (keep: after the attempts already there;
        otherwise the earlier plan reviews are dropped and the file's rounds stay)."""
        target = self.root / (path or self.PLAN)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not keep and target.exists():
            target.write_bytes(self.only(target.read_bytes().decode("utf-8"), plans=False).encode("utf-8"))
        result = {"writer": writer, "reviewer": reviewer, "model": "m", "cli": cli, "effort": effort,
                  "lenses": list(lenses), "failover": [] if reviewer else [{"reviewer": "astra", "reason": "exited 3"}],
                  "review": review if reviewer else None}
        tg.review_dispatch().record_completion(target, result, "2026-10-22T00:00:00Z", candidate or self.start,
                                               kind="plan")

    def write_completion(self, review="1. Open file: present.\n\nCOMPLETION: complete", notes="", reviewer="sol",
                         candidate=None, path=None, effort="medium", keep=False):
        """A completion review as scripts/review-dispatch.py --kind completion records it, then the writer's notes."""
        target = self.root / (path or self.COMPLETION)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not keep:
            target.unlink(missing_ok=True)
        result = {"writer": "claude", "reviewer": reviewer, "model": "gpt-6.1-sol", "cli": "codex", "effort": effort,
                  "failover": [] if reviewer else [{"reviewer": "sol", "reason": "exited 3"}],
                  "review": review if reviewer else None}
        tg.review_dispatch().record_completion(target, result, "2026-10-23T00:00:00Z", candidate or self.sha)
        if notes:
            with open(target, "a", encoding="utf-8", newline="") as handle:
                handle.write("\n" + notes + "\n")

    def ensure_plan(self, ref="D00 T01 §1"):
        """The returned plan review back in the section's own findings file when a test rewrote that file for its
        rounds (or never wrote it), as the real file carries it beside them. A file holding any plan attempt, or one
        the dispatcher cannot read, is left as the test wrote it. Returns the file."""
        report = tg.section_findings(self.root, ref)
        target = self.root / report
        plans = tg.review_dispatch().read_plans(target.read_bytes().decode("utf-8")) if target.exists() else []
        if plans == []:
            self.write_plan(path=report, keep=True)
        return report

    def stamp(self, *args, completion=None, plan=None, **kwargs):
        """tg.stamp on this tree, with a clean completion review and the section's own plan review unless the test
        names others (see ensure_plan)."""
        if plan is None:
            plan = self.ensure_plan(args[0])
        return tg.stamp(self.root, *args, completion=completion or {"report": self.COMPLETION, "verdict": "complete"},
                        plan=plan, **kwargs)

    def completion_refuses(self, completion, fragment):
        before = self.snapshot()
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-23", completion=completion)
        self.assertIn(fragment, str(ctx.exception))
        self.assertEqual(self.snapshot(), before, "a refused stamp wrote something")

    def test_a_stamp_without_a_completion_review_refuses(self):
        self.tick_work()
        before = self.snapshot()
        with self.assertRaises(tg.Refused) as ctx:
            tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-23")
        self.assertIn("--completion '<findings file>:<complete|completed|filed|reconciled>' is required",
                      str(ctx.exception))
        self.assertEqual(self.snapshot(), before)

    def test_an_unknown_completion_verdict_refuses(self):
        self.tick_work()
        for verdict in ("done", "gaps", "Complete", ""):
            with self.subTest(verdict=verdict):
                self.completion_refuses({"report": self.COMPLETION, "verdict": verdict},
                                        "--completion verdict must be one of complete, completed, filed")

    def test_a_findings_file_without_a_completion_review_refuses(self):
        self.tick_work()
        self.completion_refuses({"report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "complete"},
                                "holds no ## Completion review")
        self.completion_refuses({"report": "docs/reviews/00-workspace/none.md", "verdict": "complete"},
                                "missing or empty review report")
        self.completion_refuses({"report": "../outside.md", "verdict": "complete"}, "invalid review report path")

    def test_a_completion_pass_that_returned_no_review_refuses(self):
        self.tick_work()
        self.write_completion(reviewer=None)
        self.completion_refuses({"report": self.COMPLETION, "verdict": "complete"},
                                "must hold exactly one completion review returned by another model family")
        self.write_completion(review="1. Open file: present.\n\nCOMPLETION: unsure")
        self.completion_refuses({"report": self.COMPLETION, "verdict": "complete"},
                                "must hold exactly one completion review returned by another model family")

    def test_the_completion_verdict_must_match_the_review(self):
        self.tick_work()
        self.write_completion(review="1. Ctrl+O: missing-in-scope.\n\nCOMPLETION: gaps")
        self.completion_refuses({"report": self.COMPLETION, "verdict": "complete"},
                                "completion verdict complete needs a review ending COMPLETION: complete")
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-23",
                             completion={"report": self.COMPLETION, "verdict": "completed"})
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        self.assertEqual(data["completion"], {"report": self.COMPLETION, "verdict": "completed", "candidate": self.sha,
                                              "reviewer": "sol", "model": "gpt-6.1-sol", "filed": []})
        self.assertEqual(tg.review_rounds(self.root)["sections"][0]["completion"], "completed")

    def test_filed_gaps_must_be_listed_and_must_resolve(self):
        self.tick_work()
        gaps = "1. Recent files: missing-out-of-scope.\n\nCOMPLETION: gaps"
        filed = {"report": self.COMPLETION, "verdict": "filed"}
        self.write_completion(review=gaps)
        self.completion_refuses(filed, "completion verdict filed needs each filed section listed")
        self.write_completion(review=gaps, notes="- Filed: D00 T09 §1 (recent files)")
        self.completion_refuses(filed, "completion gap filed as D00 T09 §1, which does not resolve")
        self.write_completion(review=gaps, notes="- Filed: D00 T01 §1 (itself)")
        self.completion_refuses(filed, "cannot file a completion gap to itself")
        self.write_completion(review=gaps, notes="- Filed: D00 T01 §2 (recent files)")
        self.completion_refuses({"report": self.COMPLETION, "verdict": "completed"},
                                "and only filed lists any")
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-23", completion=filed)
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        self.assertEqual((data["completion"]["verdict"], data["completion"]["filed"]), ("filed", ["D00 T01 §2"]))
        tg.graph(self.root)

    def test_a_filed_section_that_stops_resolving_refuses(self):
        other = self.root / "todo/00-workspace/TODO-02-b.md"
        other.write_text(todo_file([(1, "Recent files", 0, "none", "--")], ident="bravo"), encoding="utf-8")
        self.index("TODO-02-b.md")
        self.tick_work()
        self.write_completion(review="1. Recent files: missing-out-of-scope.\n\nCOMPLETION: gaps",
                              notes="- Filed: D00 T02 §1 (recent files)")
        self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-23",
                   completion={"report": self.COMPLETION, "verdict": "filed"})
        other.unlink()
        self.refuses("completion gap filed as D00 T02 §1, which does not resolve: D00 T01 §1")

    def test_the_completion_candidate_is_the_stamped_commit_or_before_it(self):
        self.tick_work()
        subprocess.run(["git", "-C", str(self.root), "commit", "-q", "--allow-empty", "-m", "later"], check=True)
        later = subprocess.run(["git", "-C", str(self.root), "rev-parse", "HEAD"], capture_output=True,
                               text=True).stdout.strip()
        self.write_completion(candidate=later)
        self.completion_refuses({"report": self.COMPLETION, "verdict": "complete"},
                                "is not the stamped commit or an ancestor of it")
        self.write_completion(candidate="f" * 40)
        self.completion_refuses({"report": self.COMPLETION, "verdict": "complete"}, "not a commit")

    def test_a_receipt_records_the_completion_review_and_edits_refuse(self):
        self.tick_work()
        receipt = self.root / self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-23")
        data = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(data["completion"]["verdict"], "complete")
        for key, value in (("verdict", "completed"), ("filed", ["D00 T01 §2"]), ("reviewer", "astra")):
            with self.subTest(key=key):
                edited = json.loads(json.dumps(data))
                edited["completion"][key] = value
                receipt.write_text(json.dumps(edited), encoding="utf-8")
                with self.assertRaises(tg.Refused):
                    tg.graph(self.root)
        receipt.write_text(json.dumps(data), encoding="utf-8")
        tg.graph(self.root)
        # An edit inside the recorded completion review breaks its digest, so the receipt no longer validates.
        path = self.root / self.COMPLETION
        path.write_text(path.read_text(encoding="utf-8").replace("present", "absent"), encoding="utf-8")
        self.refuses("is not a findings file the dispatcher can read")

    def test_a_receipt_from_before_the_plan_review_validates_only_while_frozen(self):
        # Office receipts stamped before 2026-11-11 name the pre-build completion record (D00 T03 §13) as a path and
        # carry no plan review or schedule. That shape is valid only for a receipt LEGACY_RECEIPTS froze by digest, and
        # it is still held to the rules it was written under.
        self.tick_work()
        contract = tg.contract_digest(tg.graph(self.root)["D00 T01 §1"])
        receipt = self.root / self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-23")
        data = json.loads(receipt.read_text(encoding="utf-8"))
        del data["plan"], data["schedule"], data["schedule_sha"]
        data["completion"], data["completion_rules"] = self.COMPLETION, 2
        record = self.root / self.COMPLETION
        record.write_text("# Completion review: D00 T01 §1\n", encoding="utf-8")
        tg.review_dispatch().record(record, {
            "writer": "claude", "reviewer": "astra", "model": "m", "cli": "codex", "effort": "medium", "failover": [],
            "review": f"SECTION: D00 T01 §1\nPURPOSE: completion\nCONTRACT: {contract}\n\nNo gap.\n\nCOMPLETE: yes\n"
                      "HIGHEST: none\nOVERALL: approve"}, "2026-10-23T10:00:00Z")
        receipt.write_text(json.dumps(data), encoding="utf-8")
        self.refuses(tg.LEGACY_RECEIPTS)  # the old shape, and not one of the frozen receipts

        def freeze(content):
            (self.root / tg.LEGACY_RECEIPTS).write_text(json.dumps(
                {"schema_version": 1, "receipts": {}, "before_plan": {"D00 T01 §1": tg.receipt_digest(content)}}),
                encoding="utf-8")
        freeze(data)
        tg.graph(self.root)
        self.assertIsNone(tg.review_rounds(self.root)["sections"][0]["completion"])
        # D00 T03 §16: it stays bound to the contract its completion review read.
        todo = self.root / self.TODO_A
        stamped = todo.read_text(encoding="utf-8")
        todo.write_text(stamped.replace("Work.", "Different work.", 1), encoding="utf-8")
        self.refuses("it changed after its completion review")
        todo.write_text(stamped, encoding="utf-8")
        # A frozen receipt that is edited is no longer the frozen one.
        receipt.write_text(json.dumps({**data, "checks": ["other -> ok"]}), encoding="utf-8")
        self.refuses(tg.LEGACY_RECEIPTS)
        receipt.write_text(json.dumps(data), encoding="utf-8")
        tg.graph(self.root)
        # Frozen, it still answers to its own rules: without its completion record it refuses.
        without = {k: v for k, v in data.items() if k not in ("completion", "completion_rules")}
        receipt.write_text(json.dumps(without), encoding="utf-8")
        freeze(without)
        self.refuses("must name its completion record")
        receipt.write_text(json.dumps(data), encoding="utf-8")
        freeze(data)
        record.write_text(record.read_text(encoding="utf-8").replace("COMPLETE: yes", "COMPLETE: no"), encoding="utf-8")
        self.refuses("is not a findings file the dispatcher can read")

    def tick_work(self):
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        path.write_text(path.read_text(encoding="utf-8").replace("- [ ] Work.", "- [x] Work.", 1),
                        encoding="utf-8")

    def test_stamp_writes_receipt_and_validates(self):
        self.tick_work()
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        rows = tg.graph(self.root)
        self.assertTrue(rows["D00 T01 §1"].done)
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))
                         ["implementation_sha"], self.sha)

    def test_receipt_records_rounds_spent_against_the_cap(self):
        self.tick_work()
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        report.write_text("# Review findings\n\n" + envelope(1, "none") + envelope(2, overall="needs-attention")
                          + envelope(3), encoding="utf-8")
        reviews = [{"round": 2, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "fixed"},
                   {"round": 3, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "clean"}]
        receipt = self.stamp("D00 T01 §1", self.sha, reviews, ["true -> ok"], "2026-10-13")
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        self.assertEqual((data["rounds_spent"], data["round_cap"]), (3, tg.REVIEW_ROUND_CAP))
        self.assertNotIn("cap_outcome", data)
        summary = tg.review_rounds(self.root)
        self.assertEqual(summary["sections"][0]["rounds_spent"], 3)
        self.assertEqual(summary["summary"]["stopped_at_cap"], 0)

    def record_rounds(self, last, report="docs/reviews/00-workspace/D00-T01-s1.md"):
        (self.root / report).write_text("".join(envelope(n, overall="needs-attention") for n in range(1, last + 1)),
                                        encoding="utf-8")
        self.ensure_plan()

    def test_the_cap_is_33_and_earlier_caps_stay_valid(self):
        # Owner decision 2026-10-23: the review-round cap moved from 22 to 33.
        self.assertEqual(tg.REVIEW_ROUND_CAP, 33)
        self.assertIn("stopped-at-33", tg.VERDICTS)
        for earlier in (22, 13, 8, 3):
            self.assertIn(f"stopped-at-{earlier}", tg.VERDICTS)
        self.assertEqual(tg.EARLIER_CAPS, {8, 13, 22})

    def test_a_receipt_written_under_the_22_round_cap_still_validates(self):
        self.tick_work()
        self.record_rounds(22)
        stopped = [{"round": 22, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "stopped-at-22"}]
        with self.assertRaises(tg.Refused):  # a new stamp stops only at the current cap
            self.stamp("D00 T01 §1", self.sha, stopped, ["true -> ok"], "2026-10-13", cap_outcome="filed")
        self.record_rounds(33)
        receipt = self.root / self.stamp("D00 T01 §1", self.sha, [
            {"round": 33, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "stopped-at-33"}],
            ["true -> ok"], "2026-10-13", cap_outcome="filed")
        # The same section as a receipt from the 22-round era: 22 rounds, stopped-at-22, round_cap 22.
        self.record_rounds(22)
        data = json.loads(receipt.read_text(encoding="utf-8"))
        data.update(reviews=stopped, rounds_spent=22, round_cap=22)
        receipt.write_text(json.dumps(data), encoding="utf-8")
        tg.graph(self.root)
        data["round_cap"] = 33  # but a 22-round stop is not a stop at the 33-round cap
        receipt.write_text(json.dumps(data), encoding="utf-8")
        self.refuses("must be stopped-at-33")

    def test_a_stopped_review_must_say_what_was_done(self):
        self.tick_work()
        cap = tg.REVIEW_ROUND_CAP
        self.record_rounds(cap)
        stopped = [{"round": cap, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": f"stopped-at-{cap}"}]
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T01 §1", self.sha, stopped, ["true -> ok"], "2026-10-13")
        self.assertIn("--cap-outcome", str(ctx.exception))
        with self.assertRaises(tg.Refused):
            self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13",
                     cap_outcome="nothing stopped")
        receipt = self.stamp("D00 T01 §1", self.sha, stopped, ["true -> ok"], "2026-10-13",
                           cap_outcome="filed two leftovers as D00 T01 §2")
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        self.assertEqual((data["rounds_spent"], data["cap_outcome"]), (cap, "filed two leftovers as D00 T01 §2"))
        self.assertEqual(tg.review_rounds(self.root)["summary"]["stopped_at_cap"], 1)
        # A receipt that drops the outcome no longer validates.
        del data["cap_outcome"]
        (self.root / receipt).write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused):
            tg.graph(self.root)

    def test_a_receipt_without_rounds_spent_holds_only_what_the_old_process_wrote(self):
        self.tick_work()
        receipt = self.root / self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        data = json.loads(receipt.read_text(encoding="utf-8"))
        del data["rounds_spent"], data["round_cap"], data["plan"], data["schedule"]
        receipt.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:  # the old shape alone does not make a receipt old
            tg.graph(self.root)
        self.assertIn(tg.LEGACY_RECEIPTS, str(ctx.exception))
        legacy = self.root / tg.LEGACY_RECEIPTS
        legacy.write_text(json.dumps({"schema_version": 1, "receipts": {"D00 T01 §1": tg.receipt_digest(data)}}),
                          encoding="utf-8")
        tg.graph(self.root)  # a frozen old receipt still validates
        data["date"] = "2026-10-22"
        receipt.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused):  # and any change to it is no longer the frozen receipt
            tg.graph(self.root)
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        for rounds in ([{"round": 9, "report": report, "verdict": "stopped-low-severity"}],
                       [{"round": 1, "report": report, "verdict": "stopped-at-33"}]):
            data["reviews"] = rounds
            receipt.write_text(json.dumps(data), encoding="utf-8")
            with self.subTest(rounds=rounds), self.assertRaises(tg.Refused) as ctx:
                tg.graph(self.root)
            self.assertIn("without rounds_spent", str(ctx.exception))

    def test_a_loop_past_the_cap_refuses_even_when_it_ends_clean(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        last = tg.REVIEW_ROUND_CAP + 1
        (self.root / report).write_text("".join(envelope(n, overall="needs-attention") for n in range(1, last))
                                        + envelope(last), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T01 §1", self.sha, [{"round": last, "report": report, "verdict": "clean"}],
                     ["true -> ok"], "2026-10-13")
        self.assertIn(f"over the {tg.REVIEW_ROUND_CAP}-round cap", str(ctx.exception))

    def test_a_repeated_round_number_refuses(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        (self.root / report).write_text("".join(envelope(1, overall="needs-attention") for _ in range(3))
                                        + envelope(1), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("must number its rounds 1 to 4 in order", str(ctx.exception))

    def test_a_loop_whose_last_round_returned_no_review_refuses(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        (self.root / report).write_text(envelope(1) + envelope(2, "none", overall="blocked"), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:  # round 2 ran after the approval and returned nothing
            self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("ends with round 2, which returned no review", str(ctx.exception))

    def test_rounds_spent_must_be_what_the_findings_files_record(self):
        self.tick_work()
        receipt = self.root / self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        data = json.loads(receipt.read_text(encoding="utf-8"))
        data["rounds_spent"] = 999
        receipt.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            tg.graph(self.root)
        self.assertIn("receipt rounds_spent 999 is not the 1 rounds", str(ctx.exception))

    def test_a_receipt_names_a_cap_the_process_has_used(self):
        self.tick_work()
        receipt = self.root / self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        data = json.loads(receipt.read_text(encoding="utf-8"))
        data["round_cap"] = 50
        receipt.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            tg.graph(self.root)
        self.assertIn("round_cap is invalid", str(ctx.exception))

    def test_a_review_with_carriage_returns_is_read_as_the_dispatcher_wrote_it(self):
        self.tick_work()
        dispatch = tg.review_dispatch()
        review = ["Captured progress: 10%\rCaptured progress: 100%", "Example heading:", "## Round 999: none",
                  "OVERALL: approve"]
        text = ("## Round 1: astra (`m` via `codex`)\n\n- Writer: claude\n- Run: 2026-10-21T00:00:00Z\n"
                "- Effort: low\n- Lenses: adversarial\n"
                f"- Lines: 4\n- Digest: {dispatch.digest(review)}\n\n" + "\n".join(review) + "\n")
        (self.root / "docs/reviews/00-workspace/D00-T01-s1.md").write_bytes(text.encode("utf-8"))
        self.assertIsNotNone(dispatch.read_rounds(text))
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))["rounds_spent"], 1)
        tg.graph(self.root)

    def test_a_round_verdict_must_match_its_review(self):
        self.tick_work()
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        before = self.snapshot()
        report.write_text(envelope(1, overall="needs-attention"), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:  # a rejecting review claimed as clean
            self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("verdict matching clean", str(ctx.exception))
        fixed_only = [{"round": 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "fixed"}]
        with self.assertRaises(tg.Refused) as ctx:  # fixed, but no later round saw the fixes
            self.stamp("D00 T01 §1", self.sha, fixed_only, ["true -> ok"], "2026-10-13")
        self.assertIn("must end at its last reviewed round", str(ctx.exception))
        report.write_text(envelope(1), encoding="utf-8")
        with self.assertRaises(tg.Refused):  # an approving review claimed as fixed
            self.stamp("D00 T01 §1", self.sha,
                     fixed_only + [{"round": 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "clean"}],
                     ["true -> ok"], "2026-10-13")
        report.unlink()
        self.assertEqual({k: v for k, v in self.snapshot().items() if not k.endswith("D00-T01-s1.md")},
                         {k: v for k, v in before.items() if not k.endswith("D00-T01-s1.md")})

    def test_a_loop_ends_at_its_last_reviewed_round(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        (self.root / report).write_text(envelope(1) + envelope(2, overall="needs-attention"), encoding="utf-8")
        before = self.snapshot()
        for claimed in ([{"round": 1, "report": report, "verdict": "clean"}, {"round": 2, "report": report, "verdict": "fixed"}],
                        [{"round": 1, "report": report, "verdict": "clean"}]):
            with self.assertRaises(tg.Refused) as ctx:  # a later failing review cannot be left behind an approval
                self.stamp("D00 T01 §1", self.sha, claimed, ["true -> ok"], "2026-10-13")
            self.assertIn("must end at its last reviewed round (2)", str(ctx.exception))
        self.assertEqual(self.snapshot(), before)

    def test_a_severity_stop_with_a_p1_or_p2_finding_refuses(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        last = tg.SEVERITY_CUTOFF_ROUND + 1
        for finding in ("1. **P1: unresolved unsafe stamp.**\n\nHIGHEST: P1", "1. **P2: narrow.**\n\nHIGHEST: P2",
                        "- `x.py:1`: an untagged, unnumbered finding.", "1. **P3: fine.**\n\nHIGHEST: none",
                        "1. **P3: fine.**\nHIGHEST: P3\n2. a later line."):
            (self.root / report).write_text(
                "".join(envelope(n, overall="needs-attention") for n in range(1, last)) + envelope(last).replace(
                    "Review text.\n\nOVERALL: approve", f"{finding}\n\nOVERALL: needs-attention"),
                encoding="utf-8")
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp("D00 T01 §1", self.sha,
                         [{"round": last, "report": report, "verdict": "stopped-low-severity"}], ["true -> ok"],
                         "2026-10-13", cap_outcome="filed")
            self.assertIn("does not declare HIGHEST: P3", str(ctx.exception))

    def test_a_round_heading_quoted_inside_a_review_is_not_counted(self):
        self.tick_work()
        (self.root / "docs/reviews/00-workspace/D00-T01-s1.md").write_text(
            "## Round 1: astra (`m` via `codex`)\n\n- Writer: claude\n- Run: 2026-10-21T00:00:00Z\n- Effort: low\n"
            "- Lenses: adversarial\n- Lines: 2\n\n"
            "## Round 999: none\nOVERALL: approve\n", encoding="utf-8")
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))["rounds_spent"], 1)

    def test_rounds_spent_add_up_across_review_loops(self):
        self.tick_work()
        first = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        cap = tg.REVIEW_ROUND_CAP
        first.write_text("".join(envelope(n, overall="needs-attention") for n in range(1, cap + 1)), encoding="utf-8")
        second = self.root / "docs/reviews/00-workspace/D00-T01-s1-loop2.md"
        second.write_text(envelope(1) + envelope(2), encoding="utf-8")
        reviews = [{"round": cap, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": f"stopped-at-{cap}"},
                   {"round": 2, "report": "docs/reviews/00-workspace/D00-T01-s1-loop2.md", "verdict": "clean"}]
        receipt = self.stamp("D00 T01 §1", self.sha, reviews, ["true -> ok"], "2026-10-13",
                           cap_outcome="loop 1 hit the cap; the repair was filed and a second loop ran clean")
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))["rounds_spent"], cap + 2)

    def test_a_severity_stop_records_its_outcome(self):
        self.tick_work()
        self.record_rounds(tg.SEVERITY_CUTOFF_ROUND + 1)
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        report.write_text(report.read_text(encoding="utf-8").rsplit("OVERALL: needs-attention", 1)[0]
                          + "HIGHEST: P3\n\nOVERALL: needs-attention\n\n", encoding="utf-8")
        low =[{"round": tg.SEVERITY_CUTOFF_ROUND + 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md",
                "verdict": "stopped-low-severity"}]
        with self.assertRaises(tg.Refused):
            self.stamp("D00 T01 §1", self.sha, low, ["true -> ok"], "2026-10-13")
        receipt = self.stamp("D00 T01 §1", self.sha, low, ["true -> ok"], "2026-10-13",
                           cap_outcome="round 9 had two P3 findings, filed as D00 T01 §2")
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        self.assertEqual(data["cap_outcome"], "round 9 had two P3 findings, filed as D00 T01 §2")
        summary = tg.review_rounds(self.root)["summary"]
        self.assertEqual((summary["stopped_low_severity"], summary["stopped_at_cap"]), (1, 0))

    def test_a_cap_stop_must_be_the_current_cap_reached(self):
        self.tick_work()
        self.record_rounds(tg.REVIEW_ROUND_CAP)
        before = self.snapshot()
        for n, verdict in ((1, f"stopped-at-{tg.REVIEW_ROUND_CAP}"), (3, "stopped-at-3"), (13, "stopped-at-13")):
            early = [{"round": n, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": verdict}]
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp("D00 T01 §1", self.sha, early, ["true -> ok"], "2026-10-13", cap_outcome="filed")
            self.assertRegex(str(ctx.exception), f"must be stopped-at-{tg.REVIEW_ROUND_CAP}|"
                                                 f"a cap stop is the round that returns review {tg.REVIEW_ROUND_CAP}")
        self.assertEqual(self.snapshot(), before)

    def test_a_severity_stop_with_only_p3_findings_stamps(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        last = tg.SEVERITY_CUTOFF_ROUND + 1
        (self.root / report).write_text(
            "".join(envelope(n, overall="needs-attention") for n in range(1, last)) + envelope(last).replace(
                "Review text.\n\nOVERALL: approve", "1. **P3: wording.**\n2. **P3: the comment describing P1 findings.**\n\nHIGHEST: P3\n\nOVERALL: needs-attention"),
            encoding="utf-8")
        self.stamp("D00 T01 §1", self.sha, [{"round": last, "report": report, "verdict": "stopped-low-severity"}],
                 ["true -> ok"], "2026-10-13", cap_outcome="two P3 findings filed")

    def test_outage_rounds_do_not_earn_a_stop(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        # At the live cutoff of 0 any returned review may stop; outages count toward no cutoff, which shows at 3.
        with mock.patch.object(tg, "SEVERITY_CUTOFF_ROUND", 3):
            last = 4
            (self.root / report).write_text(
                "".join(envelope(n, "none") for n in range(1, last)) + envelope(last).replace(
                    "Review text.\n\nOVERALL: approve", "1. **P3: wording.**\n\nHIGHEST: P3\n\nOVERALL: needs-attention"), encoding="utf-8")
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp("D00 T01 §1", self.sha, [{"round": last, "report": report, "verdict": "stopped-low-severity"}],
                         ["true -> ok"], "2026-10-13", cap_outcome="filed")
            self.assertIn("follows only 1 returned reviews", str(ctx.exception))
        cap = tg.REVIEW_ROUND_CAP
        (self.root / report).write_text(envelope(1, "none") + "".join(
            envelope(n, overall="needs-attention") for n in range(2, cap + 1)), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T01 §1", self.sha, [{"round": cap, "report": report, "verdict": f"stopped-at-{cap}"}],
                     ["true -> ok"], "2026-10-13", cap_outcome="filed")
        self.assertIn("a cap stop is the round that returns review", str(ctx.exception))
        # Blocked or empty replies are not returned reviews either (at the cutoff of 3, as above).
        cutoff = mock.patch.object(tg, "SEVERITY_CUTOFF_ROUND", 3)
        cutoff.start()
        self.addCleanup(cutoff.stop)
        for filler in (envelope(1).replace("OVERALL: approve", "OVERALL: blocked"), envelope(1).replace("OVERALL: approve", ""),
                       envelope(1, "claude (`claude-opus-5` via `claude`)", overall="needs-attention")):
            (self.root / report).write_text("".join(filler.replace("## Round 1:", f"## Round {n}:") for n in range(1, last))
                                            + envelope(last).replace("Review text.\n\nOVERALL: approve",
                                                                     "1. **P3: wording.**\n\nHIGHEST: P3\n\nOVERALL: needs-attention"),
                                            encoding="utf-8")
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp("D00 T01 §1", self.sha,
                         [{"round": last, "report": report, "verdict": "stopped-low-severity"}],
                         ["true -> ok"], "2026-10-13", cap_outcome="filed")
            self.assertIn("follows only 1 returned reviews", str(ctx.exception))
        # An outage before the cap moves the cap stop to the round that returns the cap's last review.
        (self.root / report).write_text(envelope(1, "none") + "".join(
            envelope(n, overall="needs-attention") for n in range(2, cap + 2)), encoding="utf-8")
        self.stamp("D00 T01 §1", self.sha, [{"round": cap + 1, "report": report, "verdict": f"stopped-at-{cap}"}],
                 ["true -> ok"], "2026-10-13", cap_outcome="filed")

    def test_a_severity_stop_before_the_cutoff_refuses(self):
        # The live cutoff is 0, so no round comes before it; the refusal is checked at the
        # earlier cutoff of 3, which a later decision could restore.
        with mock.patch.object(tg, "SEVERITY_CUTOFF_ROUND", 3):
            self.tick_work()
            self.record_rounds(3)
            before = self.snapshot()
            for n in (1, 3):
                early = [{"round": n, "report": "docs/reviews/00-workspace/D00-T01-s1.md",
                          "verdict": "stopped-low-severity"}]
                with self.assertRaises(tg.Refused) as ctx:
                    self.stamp("D00 T01 §1", self.sha, early, ["true -> ok"], "2026-10-13", cap_outcome="filed")
                self.assertIn("only after round 3", str(ctx.exception))
            self.assertEqual(self.snapshot(), before)

    def test_the_live_cutoff_stops_on_the_first_p3_round(self):
        self.assertEqual(tg.SEVERITY_CUTOFF_ROUND, 0)

    def test_a_claimed_round_must_be_a_reviewed_round_in_its_report(self):
        self.tick_work()
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        before = self.snapshot()
        for text in ("# No independent review has run\n", envelope(1, "none"), envelope(2),
                     envelope(1, "claude (`claude-opus-5` via `claude`)"),
                     envelope(1).replace("- Writer: claude", "- Writer: codex"),
                     envelope(1).replace("- Writer: claude", "- Writer: someone"),
                     envelope(1).replace("OVERALL: approve", "OVERALL: blocked"),
                     envelope(1).replace("OVERALL: approve", ""),
                     "## Round 1: astra (`m` via `codex`)\n\n- Writer: claude\n- Run: 2026-10-21T00:00:00Z\n- Lines: 0\n",
                     "## Round 1: fake\n\nNo reviewer returned a review.\n",
                     "## Round 1: astra (`m` via `codex`)\n\nNo metadata block.\n"):
            report.write_text(text, encoding="utf-8")
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
            self.assertRegex(str(ctx.exception), "is not a review returned by another model family|"
                                                 "is not a findings file the dispatcher can read|holds no returned review|"
                                                 "must number its rounds")
        for bad in (0, -1, True):
            with self.assertRaises(tg.Refused):
                self.stamp("D00 T01 §1", self.sha,
                         [{"round": bad, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "clean"}],
                         ["true -> ok"], "2026-10-13")
        report.write_text("# Review findings\n\n" + envelope(1), encoding="utf-8")
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        # A receipt edited to claim a round its report never recorded no longer validates.
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        data["reviews"][0]["round"] = 999
        data["rounds_spent"] = 999
        (self.root / receipt).write_text(json.dumps(data), encoding="utf-8")
        self.refuses("round 999 is not a review returned by another model family")

    def test_a_stamped_section_with_a_waiting_need_refuses(self):
        self.tick_work()
        self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        path.write_text(path.read_text(encoding="utf-8").replace("**Needs:** none", "**Needs:** owner-decision", 1),
                        encoding="utf-8")
        self.refuses("stamped section has a waiting Need")

    def test_stale_deferral_refuses_when_owner_stamps(self):
        self.tick_work()
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        text = path.read_text(encoding="utf-8")
        target = "## 2. B\n"
        path.write_text(text.replace(target, target + "\n> **Deferred:** wait on 1 -> XREF: §1\n"),
                        encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("stale deferral", str(ctx.exception))

    def test_unticked_items_refuse(self):
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("unticked", str(ctx.exception))

    def test_waiting_section_cannot_be_stamped(self):
        with self.assertRaises(tg.Refused):
            self.stamp("D00 T01 §2", self.sha, self.reviews, ["true -> ok"], "2026-10-13")

    def test_unknown_commit_refuses(self):
        self.tick_work()
        with self.assertRaises(tg.Refused):
            self.stamp("D00 T01 §1", "0" * 40, self.reviews, ["true -> ok"], "2026-10-13")

    def test_no_review_round_refuses(self):
        self.tick_work()
        with self.assertRaises(tg.Refused):
            self.stamp("D00 T01 §1", self.sha, [], ["true -> ok"], "2026-10-13")

    def test_missing_review_report_refuses(self):
        self.tick_work()
        for bad_path in (r"\Users\outside.md", "../outside.md", "docs/reviews/../outside.md", "outside.md"):
            bad_round = [{"round": 1, "report": bad_path, "verdict": "clean"}]
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp("D00 T01 §1", self.sha, bad_round, ["true -> ok"], "2026-10-13")
            self.assertIn("invalid review report path", str(ctx.exception))
        missing = [{"round": 1, "report": "docs/reviews/00-workspace/missing.md", "verdict": "clean"}]
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T01 §1", self.sha, missing, ["true -> ok"], "2026-10-13")
        self.assertIn("missing or empty review report", str(ctx.exception))
        self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        (self.root / "docs/reviews/00-workspace/D00-T01-s1.md").unlink()
        self.refuses("missing or empty review report")

    def test_receipt_for_another_commit_refuses(self):
        self.tick_work()
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        data["implementation_sha"] = "f" * 40
        (self.root / receipt).write_text(json.dumps(data), encoding="utf-8")
        self.refuses("receipt does not match its stamp")

    def test_matching_fabricated_sha_in_stamp_and_receipt_refuses(self):
        self.tick_work()
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        fake_sha = "0" * 40
        todo_path = self.root / "todo/00-workspace/TODO-01-a.md"
        todo_path.write_text(todo_path.read_text(encoding="utf-8").replace(self.sha, fake_sha),
                             encoding="utf-8")
        receipt_path = self.root / receipt
        receipt_path.write_text(receipt_path.read_text(encoding="utf-8").replace(self.sha, fake_sha),
                                encoding="utf-8")
        self.refuses("not a commit")

    def snapshot(self):
        self.ensure_plan()  # the fixture's plan review is put back before, not during, a refused stamp
        return {str(f.relative_to(self.root)): f.read_bytes()
                for f in self.root.rglob("*") if f.is_file() and ".git" not in f.parts}

    def test_bad_verdict_writes_nothing(self):
        self.tick_work()
        before = self.snapshot()
        bad = [{"round": 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "cleen"}]
        with self.assertRaises(tg.Refused):
            self.stamp("D00 T01 §1", self.sha, bad, ["true -> ok"], "2026-10-13")
        self.assertEqual(self.snapshot(), before)
        tg.graph(self.root)

    def test_bad_date_writes_nothing(self):
        self.tick_work()
        before = self.snapshot()
        with self.assertRaises(tg.Refused):
            self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "13 Oct")
        self.assertEqual(self.snapshot(), before)

    def test_failed_stamp_write_rolls_back_receipt_and_allows_retry(self):
        self.tick_work()
        tg.projections(self.root, sync=True)
        before = self.snapshot()
        real_atomic = tg.atomic
        for fail_at in (2, 3):
            calls = []

            def fail_on_nth_write(path, data, target=fail_at):
                calls.append(path)
                if len(calls) == target:
                    raise OSError("simulated disk write failure")
                return real_atomic(path, data)

            tg.atomic = fail_on_nth_write
            try:
                with self.assertRaises(OSError):
                    self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                             "2026-10-13", sync_plan=True)
            finally:
                tg.atomic = real_atomic
            self.assertEqual(len(calls), 4 if fail_at == 3 else 2)
            self.assertFalse((self.root / "docs/reviews/d00-t01-s1.json").exists())
            self.assertEqual(self.snapshot(), before)
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                           "2026-10-13", sync_plan=True)
        self.assertTrue((self.root / receipt).is_file())
        tg.projections(self.root)

    def test_an_interrupted_stamp_rolls_back_and_allows_retry(self):
        self.tick_work()
        tg.projections(self.root, sync=True)
        before = self.snapshot()
        real_atomic = tg.atomic
        calls = []

        def interrupt_on_second_write(path, data):
            calls.append(path)
            if len(calls) == 2:
                raise KeyboardInterrupt
            return real_atomic(path, data)

        tg.atomic = interrupt_on_second_write
        try:
            with self.assertRaises(KeyboardInterrupt):
                self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
        finally:
            tg.atomic = real_atomic
        self.assertEqual(self.snapshot(), before)
        self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)

    TODO_A = "todo/00-workspace/TODO-01-a.md"

    def two_rounds(self):
        """The findings file holds a needs-attention round 2 and a clean round 3; returns the two-round claim."""
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        (self.root / report).write_text("# Review findings\n\n" + envelope(1, "none") + envelope(2, overall="needs-attention")
                                        + envelope(3), encoding="utf-8")
        return [{"round": 2, "report": report, "verdict": "fixed"}, {"round": 3, "report": report, "verdict": "clean"}]

    def cut_short(self, keep_todo, reviews=None):
        """A real stamp, then the files put back as a process killed between its writes leaves them: the receipt kept
        and the plan (and, unless keep_todo, the TODO file) as they were before. Returns the receipt path, its bytes
        and the plan and TODO bytes before and after the stamp."""
        self.tick_work()
        self.ensure_plan()
        tg.projections(self.root, sync=True)
        todo, plan = self.root / self.TODO_A, self.root / tg.PLAN
        todo_before, plan_before = todo.read_bytes(), plan.read_bytes()
        receipt = self.stamp("D00 T01 §1", self.sha, reviews or self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
        held = (self.root / receipt).read_bytes()
        todo_after = todo.read_bytes()
        plan.write_bytes(plan_before)
        if not keep_todo:
            todo.write_bytes(todo_before)
        return receipt, held, todo_before, todo_after, plan_before

    def retry(self, **kwargs):
        args = dict(sha=self.sha, reviews=self.reviews)
        args.update(kwargs)
        return self.stamp("D00 T01 §1", args["sha"], args["reviews"], ["true -> ok"], "2026-10-14", sync_plan=True)

    def test_a_stamp_killed_after_its_receipt_is_completed_by_the_same_retry(self):
        receipt, held, todo_before, todo_after, _ = self.cut_short(keep_todo=False)
        self.assertEqual(self.retry(), receipt)
        self.assertTrue(tg.graph(self.root)["D00 T01 §1"].done)
        self.assertIn("> **Verified:** 2026-10-14 | §1 | " + self.sha,
                      (self.root / self.TODO_A).read_text(encoding="utf-8"))
        tg.projections(self.root)

    def test_a_leftover_receipt_of_another_request_refuses_and_stays_as_it_was(self):
        receipt, held, todo_before, _, plan_before = self.cut_short(keep_todo=False)
        other = self.commit("later work")
        before = self.snapshot()
        with self.assertRaises(tg.Refused) as ctx:
            self.retry(sha=other)
        self.assertIn(receipt, str(ctx.exception))
        self.assertIn("commit", str(ctx.exception))
        self.assertEqual((self.root / receipt).read_bytes(), held)
        self.assertEqual(self.snapshot(), before, "a refused retry wrote something")

    def test_a_retry_whose_write_fails_puts_the_leftover_receipt_back(self):
        receipt, held, *_ = self.cut_short(keep_todo=False)
        before = self.snapshot()
        real_atomic = tg.atomic
        calls = []

        def fail_on_todo_write(path, data):
            calls.append(path)
            if len(calls) == 2:
                raise OSError("simulated disk write failure")
            return real_atomic(path, data)

        tg.atomic = fail_on_todo_write
        try:
            with self.assertRaises(OSError):
                self.retry()
        finally:
            tg.atomic = real_atomic
        self.assertEqual((self.root / receipt).read_bytes(), held)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.retry(), receipt)

    def test_a_stamp_killed_before_its_plan_write_is_completed_by_the_same_retry(self):
        receipt, held, _, todo_after, _ = self.cut_short(keep_todo=True)
        with self.assertRaises(tg.Refused):
            tg.projections(self.root)  # the state a kill leaves: plan --check fails
        self.assertEqual(self.retry(), receipt)
        tg.projections(self.root)
        self.assertEqual((self.root / receipt).read_bytes(), held)
        self.assertEqual((self.root / self.TODO_A).read_bytes(), todo_after)

    def test_a_stamped_section_refuses_a_request_that_differs_from_its_receipt(self):
        rounds = self.two_rounds()
        receipt, held, _, todo_after, plan_before = self.cut_short(keep_todo=True, reviews=rounds)
        other = self.commit("later work")
        verdict = [dict(rounds[1], verdict="fixed")]  # round 3 is a clean round: "fixed" does not match it
        for label, kwargs in (("commit", {"sha": other, "reviews": rounds}), ("reviews", {"reviews": rounds[1:]}),
                              ("verdict", {"reviews": verdict})):
            with self.subTest(label):
                before = self.snapshot()
                with self.assertRaises(tg.Refused) as ctx:
                    self.retry(**kwargs)
                if label != "verdict":  # a verdict the findings do not bear out is refused by its own check first
                    self.assertIn("already verified", str(ctx.exception))
                self.assertEqual(self.snapshot(), before, "a refused retry wrote something")
        self.assertEqual((self.root / receipt).read_bytes(), held)
        self.assertEqual((self.root / self.TODO_A).read_bytes(), todo_after)
        self.assertEqual((self.root / tg.PLAN).read_bytes(), plan_before)

    def test_a_failing_plan_write_on_the_retry_keeps_the_stamp_and_a_further_retry_succeeds(self):
        receipt, held, _, todo_after, plan_before = self.cut_short(keep_todo=True)
        real_atomic = tg.atomic

        def fail(path, data):
            raise OSError("simulated disk write failure")

        tg.atomic = fail
        try:
            with self.assertRaises(OSError):
                self.retry()
        finally:
            tg.atomic = real_atomic
        self.assertEqual((self.root / receipt).read_bytes(), held)
        self.assertEqual((self.root / self.TODO_A).read_bytes(), todo_after)
        self.assertEqual((self.root / tg.PLAN).read_bytes(), plan_before)
        self.assertEqual(self.retry(), receipt)
        tg.projections(self.root)

    def test_unstamp_reopens_a_regressed_section_and_allows_a_restamp(self):
        self.tick_work()
        tg.projections(self.root, sync=True)
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
        before = self.snapshot()
        for bad in (("D00 T01 §2", "x"), ("D00 T01 §1", ""), ("D00 T01 §1", "two\nlines")):
            with self.assertRaises(tg.Refused):
                tg.unstamp(self.root, bad[0], bad[1], "2026-10-21T00:00:00Z")
        self.assertEqual(self.snapshot(), before)
        revoked = tg.unstamp(self.root, "D00 T01 §1", "checkpoint fails at abc1234; repair -> XREF: §2", "2026-10-21T00:00:00Z")
        rows = tg.graph(self.root)
        self.assertFalse(rows["D00 T01 §1"].done)
        self.assertEqual(tg.disposition(rows["D00 T01 §1"], rows), 0)
        self.assertFalse((self.root / receipt).exists())
        self.assertEqual((self.root / revoked).read_bytes(), before[str(pathlib.Path(receipt))])
        text = (self.root / "todo/00-workspace/TODO-01-a.md").read_text(encoding="utf-8")
        self.assertIn("> **Unstamped:** 2026-10-21T00:00:00Z: checkpoint fails", text)
        self.assertIn("- [ ] Commit:", text)
        tg.projections(self.root)  # the plan was synced
        # The old cycle's records are kept under a revoked name and the findings file is free for a fresh cycle:
        # with them still in it the dispatcher refuses a new plan review, so the section could never re-stamp.
        kept = self.root / "docs/reviews/00-workspace/D00-T01-s1.revoked-2026-10-21.md"
        self.assertEqual(kept.read_bytes(), before[str(pathlib.Path(self.PLAN))])
        self.assertFalse((self.root / self.PLAN).exists())
        self.assertIn("review record kept as `docs/reviews/00-workspace/D00-T01-s1.revoked-2026-10-21.md`", text)
        self.assertNotIn("> **Started:**", text)
        self.assertIn("> **Duration:** started 2026-10-23T00:00Z, reopened 2026-10-21T00:00:00Z", text)
        todo = self.root / self.TODO_A
        todo.write_text(text.replace("> **Duration:** started", "> **Started:** 2026-10-22T00:00Z\n\n> **Duration:** started",
                                     1), encoding="utf-8")
        (self.root / self.PLAN).write_text("# Review findings\n\n" + envelope(1), encoding="utf-8")
        self.start = self.sha = self.commit("reopened")
        self.write_completion()
        self.write_plan()
        self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-22", sync_plan=True)
        self.assertTrue(tg.graph(self.root)["D00 T01 §1"].done)

    def test_unstamping_a_prerequisite_leaves_its_consumers_stamped_and_suspect(self):
        path = self.root / "todo/00-workspace/TODO-02-b.md"
        path.write_text(todo_file([(1, "Base", 0, "none", "--"), (2, "Mid", 0, "none", "§1"), (3, "Top", 0, "none", "§2")],
                                  ident="bravo").replace("- [ ] Work.", "- [x] Work.")
                        .replace("**Test checkpoint:**", STARTED + "**Test checkpoint:**"), encoding="utf-8")
        self.index("TODO-02-b.md")
        self.commit("start bravo")
        for n in (1, 2, 3):
            self.stamp(f"D00 T02 §{n}", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        tg.unstamp(self.root, "D00 T02 §1", "checkpoint fails", "2026-10-21T00:00:00Z")
        rows = tg.graph(self.root)
        self.assertEqual([rows[f"D00 T02 §{n}"].done for n in (1, 2, 3)], [False, True, True])
        self.assertEqual(tg.suspects(self.root, "D00 T02 §1"), ["D00 T02 §2", "D00 T02 §3"])
        # New work on a suspect stamp waits, and cannot stamp, until the reopened ancestor re-stamps.
        extra = self.root / "todo/00-workspace/TODO-03-c.md"
        extra.write_text(todo_file([(1, "On top", 0, "none", "D00 T02 §3")], ident="charlie")
                         .replace("- [ ] Work.", "- [x] Work."), encoding="utf-8")
        self.index("TODO-03-c.md")
        rows = tg.graph(self.root)
        self.assertEqual(tg.disposition(rows["D00 T03 §1"], rows), 4)
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T03 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-21")
        self.assertIn("resting on a reopened section", str(ctx.exception))
        extra.unlink()
        # Without the Unstamped note, a stamped consumer of an open section still refuses.
        path.write_text(path.read_text(encoding="utf-8").replace("> **Unstamped:** ", "> **Note:** "), encoding="utf-8")
        self.refuses("stamped section has open dependency")

    def test_an_interrupted_unstamp_rolls_back(self):
        self.tick_work()
        tg.projections(self.root, sync=True)
        self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
        before = self.snapshot()
        real_atomic = tg.atomic
        calls = []

        def interrupt_on_second_write(path, data):
            calls.append(path)
            if len(calls) == 2:
                raise KeyboardInterrupt
            return real_atomic(path, data)

        tg.atomic = interrupt_on_second_write
        try:
            with self.assertRaises(KeyboardInterrupt):
                tg.unstamp(self.root, "D00 T01 §1", "regressed", "2026-10-21T00:00:00Z")
        finally:
            tg.atomic = real_atomic
        self.assertEqual(self.snapshot(), before)
        tg.graph(self.root)

    def test_stamping_the_last_section_marks_the_file_done(self):
        path = self.root / "todo/00-workspace/TODO-02-b.md"
        path.write_text(todo_file([(1, "Only", 0, "none", "--")], ident="bravo")
                        .replace("- [ ] Work.", "- [x] Work.")
                        .replace("**Test checkpoint:**", STARTED + "**Test checkpoint:**"), encoding="utf-8")
        self.index("TODO-02-b.md")
        self.commit("start bravo")
        self.stamp("D00 T02 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("status: done", path.read_text(encoding="utf-8"))
        self.assertTrue(tg.graph(self.root)["D00 T02 §1"].done)

    def test_malformed_receipt_refuses_instead_of_crashing(self):
        self.tick_work()
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        unhashable = json.dumps({"ref": "D00 T01 §1", "implementation_sha": self.sha,
                                 "reviews": [{"round": 1, "report": "r", "verdict": []}],
                                 "checks": ["x"], "date": "2026-10-13"})
        for bad in ("[]", json.dumps({"ref": "D00 T01 §1", "implementation_sha": self.sha,
                                      "reviews": [None], "checks": ["x"], "date": "2026-10-13"}),
                    "not json", unhashable):
            (self.root / receipt).write_text(bad, encoding="utf-8")
            self.refuses("receipt")

    def test_missing_receipt_refuses(self):
        self.tick_work()
        receipt = self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        (self.root / receipt).unlink()
        self.refuses("missing receipt")

    # The plan review and the review schedule (2026-10-24): stamp refuses a section whose reviews did not follow them.

    LOOP = "docs/reviews/00-workspace/D00-T01-s1.md"
    ROUND_1 = ["adversarial", "integration", "source-defect", "plan-delivery"]

    def live(self, surface=False):
        """Pin the live schedule shape (and, with surface, make §1 a surface section), committed as the stamped commit."""
        (self.root / tg.PIN).write_text(SCHEDULE_PIN, encoding="utf-8")
        if surface:
            path = self.root / "todo/00-workspace/TODO-01-a.md"
            path.write_text(path.read_text(encoding="utf-8").replace(
                "**Surface:** no", "**Surface:** yes\n**Fidelity:** f.\n**Job:** j.\n**Treatment:** t.\n**Chrome:** c.",
                1), encoding="utf-8")
        self.sha = self.commit("live schedule")

    def loop(self, steps, surface=False):
        """Record a review loop as the dispatcher would, each round at the pass `scheduled` gives it. A step is a
        severity (a returned needs-attention review declaring it), "clean", "outage", "self" (a self-review) or
        "malformed" (a reply without the final OVERALL line)."""
        dispatch = tg.review_dispatch()
        schedule = tg.pin_schedule(self.root, self.sha, "test")
        path = self.root / self.LOOP
        if path.exists():  # a fresh loop: the rounds go, the section's plan review stays
            path.write_bytes(self.only(path.read_bytes().decode("utf-8"), plans=True).encode("utf-8"))
        for step in steps:
            existing = path.read_bytes().decode("utf-8") if path.exists() else ""
            plan = dispatch.scheduled(schedule, "round", dispatch.read_rounds(existing), surface)
            result = {"writer": "claude", "effort": plan["effort"], "lenses": plan["lenses"], "failover": [],
                      "reviewer": "astra", "model": "m", "cli": "codex",
                      "review": "1. ok.\n\nHIGHEST: none\n\nOVERALL: approve"}
            if step == "outage":
                result.update(reviewer=None, review=None, skipped=[{"reviewer": "astra", "reason": "exited 3"}])
            elif step == "self":
                result.update(reviewer="opus", cli="claude")
            elif step == "malformed":
                result["review"] = "1. The reply stopped before its verdict."
            elif step != "clean":
                result["review"] = f"1. [{step}] gap.\n\nHIGHEST: {step}\n\nOVERALL: needs-attention"
            dispatch.record(path, result, "2026-10-23T00:00:00Z")
        self.reviews = [{"round": len(steps), "report": self.LOOP, "verdict": "clean"}]

    def edit_round(self, n, effort, lenses):
        """Rewrite round n's Effort and Lenses lines, which sit outside its digest, as a hand edit would."""
        path = self.root / self.LOOP
        text = path.read_bytes().decode("utf-8")
        start = text.index(f"## Round {n}: ")
        end = text.find("\n## Round ", start)
        end = len(text) if end < 0 else end
        block = re.sub(r"^- Effort: .*$", f"- Effort: {effort}", text[start:end], count=1, flags=re.M)
        block = re.sub(r"^- Lenses: .*$", f"- Lenses: {', '.join(lenses)}", block, count=1, flags=re.M)
        path.write_bytes((text[:start] + block + text[end:]).encode("utf-8"))

    def stamp_refuses(self, fragment):
        self.tick_work()
        before = self.snapshot()
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-24")
        self.assertIn(fragment, str(ctx.exception))
        self.assertEqual(self.snapshot(), before, "a refused stamp wrote something")
        return str(ctx.exception)

    def test_a_stamp_without_a_plan_review_refuses(self):
        self.tick_work()
        before = self.snapshot()
        with self.assertRaises(tg.Refused) as ctx:
            tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-24",
                     completion={"report": self.COMPLETION, "verdict": "complete"})
        self.assertIn("--plan '<findings file>' is required", str(ctx.exception))
        self.assertEqual(self.snapshot(), before)

    def test_a_plan_review_must_be_one_returned_by_another_model_family(self):
        family = "must hold exactly one plan review returned by another model family"
        for kwargs in ({"reviewer": "opus", "cli": "claude"}, {"reviewer": None},
                       {"review": "1. ok.\n\nHIGHEST: none\n\nOVERALL: approve"},
                       {"review": "1. ok.\n\nOVERALL: approve\n\nPLAN: complete"}):
            with self.subTest(kwargs=kwargs):
                self.write_plan(**kwargs)
                self.stamp_refuses(family)
        self.write_plan()
        path = self.root / self.PLAN
        text = path.read_bytes().decode("utf-8")
        path.write_bytes(self.only(text, plans=False).encode("utf-8"))
        self.tick_work()
        with self.assertRaises(tg.Refused) as ctx:
            tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-24", plan=self.PLAN,
                     completion={"report": self.COMPLETION, "verdict": "complete"})
        self.assertIn("holds no ## Plan review", str(ctx.exception))
        path.write_bytes(text.encode("utf-8"))
        for plan in ("docs/reviews/00-workspace/D00-T01-s2.md", self.COMPLETION,
                     "docs\\reviews\\00-workspace\\D00-T01-s1.md", "../plan.md"):
            with self.subTest(plan=plan):
                self.tick_work()
                with self.assertRaises(tg.Refused) as ctx:
                    self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-24", plan=plan)
                self.assertIn(f"--plan must be the section's own findings file {self.PLAN}", str(ctx.exception))
        path.unlink()
        self.tick_work()
        with self.assertRaises(tg.Refused) as ctx:
            tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-24", plan=self.PLAN,
                     completion={"report": self.COMPLETION, "verdict": "complete"})
        self.assertIn("missing or empty review report", str(ctx.exception))

    def test_another_sections_plan_review_does_not_stand_in(self):
        # §2's own findings file holds a returned plan review on the build-start commit; §1 cannot stamp on it.
        other = "docs/reviews/00-workspace/D00-T01-s2.md"
        self.write_plan(path=other)
        self.tick_work()
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-24", plan=other)
        self.assertIn(f"--plan must be the section's own findings file {self.PLAN}, not {other}", str(ctx.exception))
        # Nor through a receipt edited after the stamp to name it.
        receipt = self.root / self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-24")
        data = json.loads(receipt.read_text(encoding="utf-8"))
        data["plan"]["report"] = other
        receipt.write_text(json.dumps(data), encoding="utf-8")
        self.refuses(f"--plan must be the section's own findings file {self.PLAN}, not {other}")

    def test_a_plan_review_after_the_build_began_refuses(self):
        later = self.commit("the build")
        self.write_plan(candidate=later)
        self.stamp_refuses("is not the commit the build began at")
        self.write_plan(candidate="f" * 40)
        self.stamp_refuses("not a commit")
        # Without a Started line or a commit naming the section, there is no build start to check the plan against.
        self.write_plan()
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        path.write_text(path.read_text(encoding="utf-8").replace(STARTED, ""), encoding="utf-8")
        self.stamp_refuses("cannot find the commit the build began at")

    def test_the_plan_and_completion_passes_run_at_their_scheduled_effort(self):
        self.live()
        self.loop(["clean"])
        self.write_plan(effort="high")
        self.stamp_refuses("the plan review in docs/reviews/00-workspace/D00-T01-s1.md ran at high")
        self.write_plan(lenses=("adversarial",))
        self.stamp_refuses("lenses ['adversarial']; the schedule expects medium with ['plan']")
        self.write_plan()
        self.write_completion(effort="xhigh")
        self.stamp_refuses("the completion review in docs/reviews/00-workspace/D00-T01-s1-completion.md ran at xhigh")

    def test_every_plan_and_completion_attempt_runs_at_its_scheduled_effort(self):
        self.live()
        self.loop(["clean"])
        self.write_plan(reviewer=None, effort="low", lenses=("adversarial",))
        self.write_plan(keep=True)
        self.stamp_refuses("the plan review in docs/reviews/00-workspace/D00-T01-s1.md ran at low with lenses "
                           "['adversarial']")
        self.write_plan()
        self.write_completion(reviewer=None, effort="low")
        self.write_completion(keep=True)
        self.stamp_refuses("the completion review in docs/reviews/00-workspace/D00-T01-s1-completion.md ran at low")

    def test_the_schedule_check_needs_no_temporary_directory(self):
        # A reviewer's read-only sandbox runs validate with no writable temporary directory.
        self.live()
        real = tempfile.tempdir
        tempfile.tempdir = str(self.root / "no-such-directory")
        try:
            schedule = tg.pin_schedule(self.root, self.sha, "D00 T01 §1")
        finally:
            tempfile.tempdir = real
        self.assertEqual(schedule["plan"], {"effort": "medium", "lenses": ["plan"]})

    def test_the_build_start_matches_the_whole_reference(self):
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src/a.txt").write_text("a", encoding="utf-8")
        self.commit("build\n\nD00 T01 §11")
        (self.root / "src/b.txt").write_text("b", encoding="utf-8")
        mine = self.commit("build\n\nThe section (D00 T01 §1).")
        self.assertEqual(tg.build_start(self.root, "todo/00-workspace/TODO-01-a.md", "", "D00 T01 §1"), mine)

    def test_the_build_start_is_the_sections_own_whole_started_line(self):
        # §1's Started line is in the first commit; §2 records a prefix of it, then the identical line, later.
        path = "todo/00-workspace/TODO-01-a.md"

        def record(line):
            text = (self.root / path).read_text(encoding="utf-8")
            two = tg.section_text(text, 2)
            two_now = re.sub(r"(?m)^> \*\*Started:\*\* .*\n\n", "", two)
            two_now = two_now.replace("**Test checkpoint:**", line + "\n\n**Test checkpoint:**", 1)
            (self.root / path).write_text(text.replace(two, two_now), encoding="utf-8")
            return self.commit("start §2"), tg.section_text((self.root / path).read_text(encoding="utf-8"), 2)

        prefix, body = record("> **Started:** 2026-10-23")
        self.assertEqual(tg.build_start(self.root, path, body, "D00 T01 §2"), prefix)
        whole, body = record(STARTED.strip())
        self.assertEqual(tg.build_start(self.root, path, body, "D00 T01 §2"), whole)
        self.assertEqual(tg.build_start(self.root, path, tg.section_text((self.root / path).read_text(
            encoding="utf-8"), 1), "D00 T01 §1"), self.start)

    def test_round_1_runs_at_high_effort(self):
        self.live()
        self.loop(["clean"])
        self.edit_round(1, "medium", self.ROUND_1)
        message = self.stamp_refuses(f"{self.LOOP} round 1 ran at medium")
        self.assertIn(f"the schedule expects high with {self.ROUND_1} (position 1)", message)

    def test_round_1_runs_all_four_lenses(self):
        self.live()
        self.loop(["clean"])
        self.edit_round(1, "high", self.ROUND_1[:3])
        self.stamp_refuses(f"round 1 ran at high with lenses {self.ROUND_1[:3]}; the schedule expects high with "
                           f"{self.ROUND_1}")

    def test_a_rotation_round_runs_its_one_lens(self):
        self.live()
        self.loop(["P2", "P2", "P2", "clean"])
        self.edit_round(4, "low", ["quality"])
        self.stamp_refuses("round 4 ran at low with lenses ['quality']; the schedule expects low with ['consistency'] "
                           "(position 4)")

    def test_the_design_lens_is_only_for_surface_sections(self):
        self.live()
        self.loop(["P2", "P2", "P2", "P2", "P2", "clean"])
        self.edit_round(6, "low", ["design"])
        self.stamp_refuses("round 6 ran at low with lenses ['design']; the schedule expects low with ['optimization']")

    def test_a_low_round_with_a_p1_escalates_the_next(self):
        self.live()
        self.loop(["P2", "P2", "P1", "clean"])
        self.edit_round(4, "low", ["consistency"])
        self.stamp_refuses("round 4 ran at low with lenses ['consistency']; the schedule expects medium with "
                           "['adversarial'] (position 4, escalated)")

    def test_an_outage_or_a_self_review_does_not_advance_the_schedule(self):
        for skipped in ("outage", "self", "malformed"):
            with self.subTest(skipped=skipped):
                self.live()
                self.loop([skipped, "clean"])
                self.edit_round(2, "medium", ["adversarial"])
                self.stamp_refuses(f"round 2 ran at medium with lenses ['adversarial']; the schedule expects high with "
                                   f"{self.ROUND_1} (position 1)")

    def test_a_receipt_records_the_plan_review_and_schedule_and_edits_refuse(self):
        self.tick_work()
        receipt = self.root / self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-24")
        data = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(data["plan"], {"report": self.PLAN, "candidate": self.sha, "reviewer": "astra", "model": "m",
                                        "effort": "medium", "lenses": ["plan"]})
        self.assertEqual(data["schedule"]["rounds"], [{"effort": "low", "lenses": ["adversarial"]}])
        edits = [("plan", "effort", "high"), ("plan", "lenses", []), ("plan", "candidate", "f" * 40),
                 ("plan", "reviewer", "sol"), ("plan", "model", "other"), ("plan", "report", self.COMPLETION),
                 ("plan", "extra", 1), ("schedule", "severity_stop_after", 2)]
        for where, key, value in edits:
            with self.subTest(where=where, key=key):
                edited = json.loads(json.dumps(data))
                edited[where][key] = value
                receipt.write_text(json.dumps(edited), encoding="utf-8")
                with self.assertRaises(tg.Refused):
                    tg.graph(self.root)
        for dropped, fragment in ((("plan",), "plan and schedule together"),
                                  (("plan", "schedule"), "a receipt without a plan review must be one of the old")):
            with self.subTest(dropped=dropped):
                edited = json.loads(json.dumps(data))
                for key in dropped:
                    del edited[key]
                receipt.write_text(json.dumps(edited), encoding="utf-8")
                self.refuses(fragment)
        receipt.write_text(json.dumps(data), encoding="utf-8")
        tg.graph(self.root)
        # The recorded plan pass is what the findings file still says: its effort line edited after the stamp refuses.
        path = self.root / self.PLAN
        path.write_bytes(path.read_bytes().replace(b"- Effort: medium", b"- Effort: high"))
        self.refuses("receipt plan does not match its findings file")

    def test_a_loop_that_follows_the_whole_schedule_stamps(self):
        self.live(surface=True)
        self.loop(["P2", "outage", "P2", "self", "P1", "P3", "P2", "P2", "P2", "clean"], surface=True)
        self.tick_work()
        receipt = self.root / self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-24")
        self.assertTrue(tg.graph(self.root)["D00 T01 §1"].done)
        rounds = tg.review_dispatch().read_rounds((self.root / self.LOOP).read_bytes().decode("utf-8"))
        self.assertEqual([(r["effort"], r["lenses"]) for r in rounds], [
            ("high", self.ROUND_1), ("medium", ["adversarial"]), ("medium", ["adversarial"]),
            ("low", ["adversarial"]), ("low", ["adversarial"]), ("medium", ["adversarial"]), ("low", ["quality"]),
            ("low", ["design"]), ("low", ["optimization"]), ("low", ["record"])])
        self.assertEqual(json.loads(receipt.read_text(encoding="utf-8"))["rounds_spent"], 10)

    # Office's own rules beside the reviewer kit's: the pre-build completion records of receipts from before the plan
    # review (D00 T03 §13), and the contract digest those receipts are bound to (D00 T03 §14 and §16).

    def test_a_pre_build_completion_record_is_never_a_round_report(self):
        self.tick_work()
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp("D00 T01 §1", self.sha, [{"round": 1, "report": self.COMPLETION, "verdict": "clean"}],
                       ["true -> ok"], "2026-10-13")
        self.assertIn("is a completion record, not a review of the implementation", str(ctx.exception))

    def test_the_contract_digest_ignores_ticks_and_stamps_but_not_wording(self):
        def contract():
            return tg.contract_digest(tg.graph(self.root)["D00 T01 §1"])
        before = contract()
        self.tick_work()
        self.assertEqual(contract(), before)
        path = self.root / self.TODO_A
        text = path.read_text(encoding="utf-8")
        deferred = text.replace("## 1. A\n\n", "## 1. A\n\n> **Deferred:** the export -> XREF: §2\n\n", 1)
        path.write_text(deferred, encoding="utf-8")
        moved = contract()
        self.assertNotEqual(moved, before)  # a deferral moves scope, so it is a new contract
        path.write_text(deferred.replace("> **Deferred:** the export", "> **Resolved:** the export", 1),
                        encoding="utf-8")
        self.assertEqual(contract(), moved)  # closing the deferral once its owner ships is the same contract
        path.write_text(text.replace("Work.", "Different work.", 1), encoding="utf-8")
        self.assertNotEqual(contract(), before)
        path.write_text(text, encoding="utf-8")
        self.stamp("D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertEqual(contract(), before)  # the Verified and Review lines and the ticked Commit item


THREE_PASS_PIN =UNIFORM_PIN.split("[schedule]")[0] + """[schedule]
policy = "three-pass"
pass_cap = 45
plan = { effort = "medium", lenses = ["plan"] }
rounds = [{ effort = "medium", lenses = ["adversarial", "integration"] }]
completion = { effort = "medium", lenses = ["plan-delivery", "record"] }
reconciliation = { effort = "medium", lenses = ["adversarial", "plan-delivery", "record"] }
"""


class ThreePassStamp(Stamp):
    """The three-pass chain (plan, one round, completion, reconciliations) recorded by the dispatcher's own writers,
    stamped, and read back through the graph."""
    PIN_TEXT = THREE_PASS_PIN
    FILE = Stamp.PLAN
    CLI, MODEL = "codex", "m"   # what the fixture pin's one reviewer runs through
    LENSES = {"plan": ["plan"], "round": ["adversarial", "integration"], "completion": ["plan-delivery", "record"],
              "reconciliation": ["adversarial", "plan-delivery", "record"]}

    def setUp(self):
        super().setUp()
        # The rotation fixture's records go: a three-pass section keeps every pass in its own findings file.
        (self.root / self.COMPLETION).unlink()
        (self.root / self.FILE).write_text("# Review findings\n", encoding="utf-8")
        self.clock = 0

    def pin(self, text):
        """Commit another pin as the repository's first one would have been: only the tests of a moved pin use it."""
        (self.root / tg.PIN).write_text(text, encoding="utf-8")
        return self.commit("pin")

    def passed(self, kind, candidate, top="none", gaps=False, lenses=None, reviewer="astra", review=None, notes="",
               effort="medium"):
        """One returned pass as the dispatcher records it."""
        dispatch = tg.review_dispatch()
        self.clock += 1
        names = self.LENSES[kind] if lenses is None else lenses
        lines = [f"LENS {n}: {'findings' if gaps else 'clean'}" for n in names] + [f"HIGHEST: {top}"]
        if kind == "plan":
            lines += ["PLAN: gaps" if gaps else "PLAN: complete"]
        lines += [f"OVERALL: {'needs-attention' if gaps else 'approve'}"] if kind in ("plan", "round") else \
            [f"{kind.upper()}: {'gaps' if gaps else 'complete'}"]
        result = {"writer": "claude", "reviewer": reviewer, "model": self.MODEL, "cli": self.CLI, "effort": effort,
                  "lenses": names, "failover": [], "review": review or "\n".join(["1. text.", *lines])}
        when = f"2026-10-23T00:00:{self.clock:02d}Z"
        path = self.root / self.FILE
        if kind == "round":
            dispatch.record(path, result, when, candidate)
        else:
            dispatch.record_completion(path, result, when, candidate, kind=kind)
        if notes:
            with open(path, "a", encoding="utf-8", newline="") as handle:
                handle.write("\n" + notes + "\n")

    def build(self, message="build"):
        (self.root / "work.txt").write_text(message + "\n", encoding="utf-8")
        return self.commit(message)

    def chain(self, completion=("none", False), reconciliations=(), round_gaps=False, notes=""):
        """Plan at the start commit, a build, the round and the completion on it, then one repair commit and
        reconciliation per (top, gaps) pair; `notes` go under the last pass. Returns the last candidate."""
        self.passed("plan", self.start)
        self.tick_work()
        sha = self.build()
        self.passed("round", sha, top="P2" if round_gaps else "none", gaps=round_gaps)
        last = not reconciliations
        self.passed("completion", sha, *completion, notes=notes if last else "")
        for n, (top, gaps) in enumerate(reconciliations, 1):
            sha = self.build(f"repair {n}")
            self.passed("reconciliation", sha, top, gaps, notes=notes if n == len(reconciliations) else "")
        return sha

    def stamp3(self, sha, verdict="complete", round_verdict="clean"):
        receipt = tg.stamp(self.root, "D00 T01 §1", sha, [{"round": 1, "report": self.FILE, "verdict": round_verdict}],
                           ["true -> ok"], "2026-10-24", completion={"report": self.FILE, "verdict": verdict},
                           plan=self.FILE)
        self.assertTrue(tg.graph(self.root)["D00 T01 §1"].done)
        return json.loads((self.root / receipt).read_text(encoding="utf-8"))

    def stamp3_refuses(self, sha, fragment, verdict="complete", round_verdict="clean"):
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp3(sha, verdict, round_verdict)
        self.assertIn(fragment, str(ctx.exception))
        self.assertFalse((self.root / "docs/reviews/d00-t01-s1.json").exists())

    def test_a_clean_chain_stamps_and_reads_back(self):
        data = self.stamp3(self.chain())
        self.assertEqual((data["passes_spent"], data["pass_cap"], data["rounds_spent"]), (3, 45, 1))
        self.assertEqual(data["schedule_sha"], self.start)
        self.assertEqual(data["schedule"]["policy"], "three-pass")

    def test_a_round_that_found_something_may_end_fixed(self):
        self.stamp3(self.chain(round_gaps=True), round_verdict="fixed")

    def test_gaps_need_a_reconciliation_that_ends_complete(self):
        sha = self.chain(completion=("P2", True))
        # `completed` is the rotation verdict for gaps fixed in the section: under three-pass a reconciliation proves it.
        self.stamp3_refuses(sha, "takes completion verdict complete or reconciled", verdict="completed")
        self.stamp3_refuses(sha, "needs a returned ## Reconciliation review", verdict="reconciled")
        repaired = self.build("repair")
        self.passed("reconciliation", repaired)
        data = self.stamp3(repaired, verdict="reconciled")
        self.assertEqual((data["passes_spent"], data["completion"]["candidate"]), (4, repaired))

    def test_a_reconciliation_that_still_has_gaps_does_not_stamp(self):
        sha = self.chain(completion=("P2", True), reconciliations=[("P2", True)])
        self.stamp3_refuses(sha, "a last reconciliation ending RECONCILIATION: complete", verdict="reconciled")

    def test_the_chain_is_one_plan_one_round_one_completion_in_order_on_the_stamped_commit(self):
        with self.subTest("two rounds"):
            sha = self.chain()
            self.passed("round", sha)
            self.stamp3_refuses(sha, "the review loop")
        self.setUp_again()
        with self.subTest("a round without a candidate"):
            self.passed("plan", self.start)
            self.tick_work()
            sha = self.build()
            self.passed("round", None)
            self.passed("completion", sha)
            self.stamp3_refuses(sha, "recorded no --candidate")
        self.setUp_again()
        with self.subTest("the last pass on another commit than the stamped one"):
            sha = self.chain()
            later = self.build("later")
            self.stamp3_refuses(later, "not the stamped commit")
            del sha
        self.setUp_again()
        with self.subTest("a completion on a commit before the round's"):
            self.passed("plan", self.start)
            self.tick_work()
            sha = self.build()
            later = self.build("more")
            self.passed("round", later)
            self.passed("completion", sha)
            self.stamp3_refuses(later, "must run after the round")
        self.setUp_again()
        with self.subTest("another reviewer than the pinned one"):
            self.passed("plan", self.start)
            self.tick_work()
            sha = self.build()
            self.passed("round", sha, reviewer="sol")
            self.passed("completion", sha)
            self.stamp3_refuses(sha, "not the reviewer astra")

    def setUp_again(self):
        self.tearDown()
        self.setUp()

    def test_the_cap_is_the_sections_pins(self):
        self.tearDown()
        type(self).PIN_TEXT = THREE_PASS_PIN.replace("pass_cap = 45", "pass_cap = 4")
        try:
            self.setUp()
            sha = self.chain(completion=("P2", True), reconciliations=[("P2", True), ("none", False)])
            self.stamp3_refuses(sha, "allows 4 review passes (pass_cap), not 5", verdict="reconciled")
        finally:
            type(self).PIN_TEXT = THREE_PASS_PIN

    def test_a_reconciliation_must_have_been_eligible(self):
        with self.subTest("after a completion that was complete"):
            sha = self.chain(reconciliations=[("none", False)])
            self.stamp3_refuses(sha, "", verdict="reconciled")
        for label, pin, completion, recs, fragment in (
                ("below the blocking levels", 'pass_cap = 45\nblocking = ["P1", "P2"]', ("P3", True),
                 [("none", False)], "below the pin's blocking levels"),
                ("past a stalled chain", "pass_cap = 45\nno_progress_cap = 1", ("P2", True),
                 [("P2", True), ("none", False)], "no_progress_cap of 1")):
            self.tearDown()
            type(self).PIN_TEXT = THREE_PASS_PIN.replace("pass_cap = 45", pin)
            try:
                self.setUp()
                with self.subTest(label):
                    sha = self.chain(completion=completion, reconciliations=recs)
                    self.stamp3_refuses(sha, fragment, verdict="reconciled")
            finally:
                type(self).PIN_TEXT = THREE_PASS_PIN

    def filed_case(self, blocking, reconciled):
        """A chain whose last pass ends HIGHEST: P2 and gaps, its finding filed as §2, under `blocking`."""
        self.tearDown()
        type(self).PIN_TEXT = THREE_PASS_PIN.replace("pass_cap = 45", f"pass_cap = 45\nblocking = {blocking}")
        try:
            self.setUp()
            note = "- Filed: D00 T01 §2 (the P2 finding)"
            if reconciled:
                return self.chain(completion=("P1", True), reconciliations=[("P2", True)], notes=note)
            return self.chain(completion=("P2", True), notes=note)
        finally:
            type(self).PIN_TEXT = THREE_PASS_PIN

    def test_filed_is_for_a_last_pass_below_the_blocking_levels(self):
        for reconciled in (False, True):
            with self.subTest(reconciled=reconciled, blocking="P1 and P2"):
                sha = self.filed_case('["P1", "P2"]', reconciled)
                self.stamp3_refuses(sha, "below the pin's blocking levels", verdict="filed")
            with self.subTest(reconciled=reconciled, blocking="P1 only"):
                sha = self.filed_case('["P1"]', reconciled)
                data = self.stamp3(sha, verdict="filed")
                self.assertEqual((data["completion"]["filed"], data["passes_spent"]),
                                 (["D00 T01 §2"], 4 if reconciled else 3))
        with self.subTest("a pin without blocking takes no filed verdict"):
            self.tearDown()
            self.setUp()
            sha = self.chain(completion=("P3", True), notes="- Filed: D00 T01 §2 (x)")
            self.stamp3_refuses(sha, "takes completion verdict complete or reconciled", verdict="filed")

    def test_the_receipt_is_held_to_the_pin_at_the_plan_reviews_candidate(self):
        self.passed("plan", self.start)
        self.tick_work()
        (self.root / tg.PIN).write_text(THREE_PASS_PIN.replace('"adversarial", "integration"', '"quality"', 1),
                                        encoding="utf-8")
        sha = self.build("build with a moved pin")
        # The dispatcher ran the round under the earlier pin, so the earlier lenses are what the stamp expects.
        self.passed("round", sha)
        self.passed("completion", sha)
        data = self.stamp3(sha)
        self.assertEqual(data["schedule"]["rounds"][0]["lenses"], ["adversarial", "integration"])
        receipt = self.root / "docs/reviews/d00-t01-s1.json"
        for label, change in (("deleted", lambda d: d.pop("schedule_sha")),
                              ("replaced by the stamped commit", lambda d: d.update(schedule_sha=sha)),
                              ("passes_spent edited", lambda d: d.update(passes_spent=2)),
                              ("pass_cap edited", lambda d: d.update(pass_cap=99)),
                              ("pass accounting dropped", lambda d: (d.pop("pass_cap"), d.pop("passes_spent")))):
            with self.subTest(label):
                edited = dict(data)
                change(edited)
                receipt.write_text(json.dumps(edited, indent=2) + "\n", encoding="utf-8")
                with self.assertRaises(tg.Refused):
                    tg.graph(self.root)
        receipt.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        tg.graph(self.root)

    def test_conditional_lenses_are_replayed_from_the_changed_files(self):
        self.tearDown()
        type(self).PIN_TEXT = THREE_PASS_PIN + (
            '\n[[schedule.conditional]]\nlenses = ["design"]\npasses = ["plan", "round"]\npaths = ["src/ui/"]\n')
        try:
            self.setUp()
            self.passed("plan", self.start, lenses=["plan", "design"])   # named with --paths before the build
            self.tick_work()
            (self.root / "src/ui").mkdir(parents=True)
            (self.root / "src/ui/a.txt").write_text("x\n", encoding="utf-8")
            sha = self.commit("ui build")
            self.passed("round", sha)                                      # recorded without the lens its files call for
            self.passed("completion", sha)
            self.stamp3_refuses(sha, "the schedule expects medium with ['adversarial', 'integration', 'design']")
            self.setUp_again()
            self.passed("plan", self.start)
            self.tick_work()
            sha = self.build()                                              # touches nothing under src/ui/
            self.passed("round", sha, lenses=["adversarial", "integration", "design"])
            self.passed("completion", sha)
            self.stamp3_refuses(sha, "the schedule expects medium with ['adversarial', 'integration']")
            self.setUp_again()
            self.passed("plan", self.start, lenses=["plan", "design"])
            self.tick_work()
            (self.root / "src/ui").mkdir(parents=True)
            (self.root / "src/ui/a.txt").write_text("x\n", encoding="utf-8")
            sha = self.commit("ui build")
            self.passed("round", sha, lenses=["adversarial", "integration", "design"])
            self.passed("completion", sha)
            self.stamp3(sha)
        finally:
            type(self).PIN_TEXT = THREE_PASS_PIN

    def test_a_changed_promise_between_the_completion_and_its_reconciliation_refuses(self):
        todo = self.root / "todo/00-workspace/TODO-01-a.md"
        self.passed("plan", self.start)
        self.tick_work()
        sha = self.build()
        self.passed("round", sha)
        self.passed("completion", sha, "P2", True)
        text = todo.read_text(encoding="utf-8")
        todo.write_text(text.replace("- [x] Work.", "- [x] Work, but less of it.", 1), encoding="utf-8")
        narrowed = self.commit("narrow the section")
        self.passed("reconciliation", narrowed)
        self.stamp3_refuses(narrowed, "the section's contract changed", verdict="reconciled")

    def test_a_complete_footer_never_overrides_a_blocking_finding(self):
        # Round 1 of D00 T01 §3: HIGHEST: P1 then COMPLETION: complete stamped as complete.
        with self.subTest("completion"):
            sha = self.chain(completion=("P1", False))
            self.stamp3_refuses(sha, "ends complete but declares HIGHEST: P1")
        self.setUp_again()
        with self.subTest("reconciliation"):
            sha = self.chain(completion=("P2", True), reconciliations=[("P2", False)])
            self.stamp3_refuses(sha, "ends complete but declares HIGHEST: P2", verdict="reconciled")
        self.tearDown()
        type(self).PIN_TEXT = THREE_PASS_PIN.replace("pass_cap = 45", 'pass_cap = 45\nblocking = ["P1", "P2"]')
        try:
            self.setUp()
            with self.subTest("a finding below the blocking levels does not hold a complete verdict"):
                self.stamp3(self.chain(completion=("P3", False)))
            self.setUp_again()
            with self.subTest("no HIGHEST line counts as P1 under a pin that names blocking levels"):
                # Round 2 of D00 T01 §3.
                self.passed("plan", self.start)
                self.tick_work()
                sha = self.build()
                self.passed("round", sha)
                self.passed("completion", sha, review="1. [P1] open.\nLENS plan-delivery: findings\n"
                                                      "LENS record: clean\nCOMPLETION: complete")
                self.stamp3_refuses(sha, "declares no HIGHEST line, which counts as P1")
        finally:
            type(self).PIN_TEXT = THREE_PASS_PIN

    def test_a_failed_plan_attempt_is_held_to_the_pin_at_its_own_candidate(self):
        # Round 1 of D00 T01 §3: an attempt that returned no review, made under another pin on another candidate,
        # was judged against the pin of the plan review that later returned.
        dispatch = tg.review_dispatch()
        (self.root / tg.PIN).write_text(THREE_PASS_PIN.replace('plan = { effort = "medium"', 'plan = { effort = "high"'),
                                        encoding="utf-8")
        other = self.commit("another pin, on another candidate")
        failed = {"writer": "claude", "reviewer": None, "effort": "high", "lenses": ["plan"], "review": None,
                  "failover": [{"reviewer": "astra", "reason": "timed out"}]}
        dispatch.record_completion(self.root / self.FILE, failed, "2026-10-22T00:00:00Z", other, kind="plan")
        self.stamp3(self.chain())
        # The same failed attempt on the returned plan review's own candidate is held to that pin, and refuses.
        self.setUp_again()
        dispatch.record_completion(self.root / self.FILE, failed, "2026-10-22T00:00:00Z", self.start, kind="plan")
        self.stamp3_refuses(self.chain(), "ran at high")

    def test_a_chain_reviewed_through_antigravity_stamps(self):
        # Completion review of D00 T01 §3: the dispatcher recorded no effort for Antigravity, and the replay refused.
        self.tearDown()
        type(self).PIN_TEXT = THREE_PASS_PIN.replace('cli = "codex"\nmodel = "m"\neffort = "medium"',
                                                     'cli = "agy"\nmodel = "gemini-4-argon-medium"')
        type(self).CLI, type(self).MODEL = "agy", "gemini-4-argon-medium"
        try:
            self.setUp()
            data = self.stamp3(self.chain())
            self.assertEqual((data["plan"]["effort"], data["plan"]["model"]), ("medium", "gemini-4-argon-medium"))
        finally:
            type(self).PIN_TEXT, type(self).CLI, type(self).MODEL = THREE_PASS_PIN, "codex", "m"

    def test_the_help_and_the_refusal_name_the_three_pass_order_and_verdicts(self):
        cli = subprocess.run([sys.executable, str(SCRIPTS / "todo-graph.py"), "stamp", "--help"],
                             capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(cli.returncode, 0, cli.stderr)
        text = " ".join(cli.stdout.split()).replace("- ", "-")   # argparse may wrap after a hyphen
        for needle in ("reconciled (three-pass pins)", "completed (rotation pins only)", "below the pin's blocking"):
            self.assertIn(needle, text)
        self.tick_work()
        with self.assertRaises(tg.Refused) as ctx:
            tg.stamp(self.root, "D00 T01 §1", self.sha, [{"round": 1, "report": self.FILE, "verdict": "clean"}],
                     ["true -> ok"], "2026-10-24", plan=self.FILE)
        self.assertIn("under a three-pass pin after the round, under a rotation pin before the rounds",
                      str(ctx.exception))

    def test_a_step_without_an_effort_is_recorded_and_replayed_with_none(self):
        self.tearDown()
        type(self).PIN_TEXT = THREE_PASS_PIN.replace(
            'rounds = [{ effort = "medium", lenses', 'rounds = [{ lenses')
        try:
            self.setUp()
            self.passed("plan", self.start)
            self.tick_work()
            sha = self.build()
            self.passed("round", sha, effort=None)
            self.passed("completion", sha)
            self.stamp3(sha)
            self.setUp_again()
            self.passed("plan", self.start)
            self.tick_work()
            sha = self.build()
            self.passed("round", sha)                       # recorded at medium, which the step does not set
            self.passed("completion", sha)
            self.stamp3_refuses(sha, "ran at medium")
        finally:
            type(self).PIN_TEXT = THREE_PASS_PIN

    def test_ticking_boxes_and_recording_evidence_does_not_change_the_promise(self):
        todo = self.root / "todo/00-workspace/TODO-01-a.md"
        before = tg.section_contract(self.root, self.start, "D00 T01 §1")
        self.tick_work()
        text = todo.read_text(encoding="utf-8")
        todo.write_text(text.replace("- [x] Work.", "- [x] Work. **Corrected 2026-11-11:** a note.", 1),
                        encoding="utf-8")
        ticked = self.commit("ticked, with a dated note")
        self.assertEqual(tg.section_contract(self.root, ticked, "D00 T01 §1"), before)
        # Parking a started section and resuming it are not changes to what it promises (D00 T03 §59).
        started = text.replace("## 1. A\n\n", "## 1. A\n\n> **Started:** 2026-11-12T00:00:00Z\n\n", 1)
        self.assertIn("> **Started:**", started)
        todo.write_text(started.replace(
            "> **Started:** 2026-11-12T00:00:00Z\n",
            "> **Started:** 2026-11-12T00:00:00Z\n> **Parked:** 2026-11-12T01:00:00Z until 2099-01-01T00:00:00Z: an event\n", 1),
            encoding="utf-8")
        parked = self.commit("parked")
        self.assertEqual(tg.section_contract(self.root, parked, "D00 T01 §1"), before)
        todo.write_text(text.replace("- [x] Work.", "- [x] Other work.", 1), encoding="utf-8")
        changed = self.commit("another promise")
        self.assertNotEqual(tg.section_contract(self.root, changed, "D00 T01 §1"), before)

    def test_a_section_that_began_under_rotation_is_held_to_it_after_the_switch(self):
        self.tearDown()
        type(self).PIN_TEXT = UNIFORM_PIN
        try:
            Stamp.setUp(self)              # the rotation fixture: plan, completion and one clean round
        finally:
            type(self).PIN_TEXT = THREE_PASS_PIN
        self.tick_work()
        (self.root / tg.PIN).write_text(THREE_PASS_PIN, encoding="utf-8")
        switched = self.commit("switch to three-pass")
        self.write_completion(candidate=switched)
        receipt = self.stamp("D00 T01 §1", switched, self.reviews, ["true -> ok"], "2026-10-24")
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        self.assertEqual(data["schedule_sha"], self.start)
        self.assertNotIn("policy", data["schedule"])
        self.assertNotIn("passes_spent", data)
        self.assertTrue(tg.graph(self.root)["D00 T01 §1"].done)


# ThreePassStamp borrows Stamp's fixture and helpers, not its tests: those are the rotation contract and run once,
# in Stamp. unittest skips a name that is not callable.
for _name in dir(Stamp):
    if _name.startswith("test_") and _name not in vars(ThreePassStamp):
        setattr(ThreePassStamp, _name, None)


class GraphReadProcesses(ThreePassStamp):
    """How many git processes one graph read starts, and that a conditional lens is still replayed (D00 T03 §62)."""

    WATCHED = ('\n[[schedule.conditional]]\nlenses = ["design"]\npasses = [%s]\npaths = ["src/ui/"]\n')

    def another_section(self, k):
        """TODO file k with one section, taken through its own three-pass chain and stamped."""
        name = f"TODO-{k:02d}-x.md"
        self.write(todo_file([(1, f"S{k}", 0, "none", "--")], ident=f"extra{k}").replace(
            "**Test checkpoint:**", STARTED + "**Test checkpoint:**", 1), name=name)
        self.FILE = f"docs/reviews/00-workspace/D00-T{k:02d}-s1.md"
        (self.root / self.FILE).write_text("# Review findings\n", encoding="utf-8")
        start = self.commit(f"section {k}")
        self.passed("plan", start)
        path = self.root / "todo/00-workspace" / name
        path.write_text(path.read_text(encoding="utf-8").replace("- [ ] Work.", "- [x] Work.", 1), encoding="utf-8")
        sha = self.build(f"build {k}")
        self.passed("round", sha)
        self.passed("completion", sha)
        tg.stamp(self.root, f"D00 T{k:02d} §1", sha, [{"round": 1, "report": self.FILE, "verdict": "clean"}],
                 ["true -> ok"], "2026-10-24", completion={"report": self.FILE, "verdict": "complete"}, plan=self.FILE)

    def read_graph(self):
        started, rows = git_started(lambda: tg.graph(self.root))
        return sorted(started), sum(1 for row in rows.values() if row.done)

    def test_a_read_starts_the_same_two_processes_for_two_stamped_sections_and_for_twelve(self):
        self.stamp3(self.chain())
        self.another_section(2)
        self.assertEqual(self.read_graph(), (["cat-file", "rev-list"], 2))
        for k in range(3, 13):
            self.another_section(k)
        self.assertEqual(self.read_graph(), (["cat-file", "rev-list"], 12))

    def ui_build(self):
        (self.root / "src/ui").mkdir(parents=True)
        (self.root / "src/ui/a.txt").write_text("x\n", encoding="utf-8")
        return self.commit("ui build")

    def with_pin(self, passes, body):
        self.tearDown()
        type(self).PIN_TEXT = THREE_PASS_PIN + self.WATCHED % passes
        try:
            self.setUp()
            body()
        finally:
            type(self).PIN_TEXT = THREE_PASS_PIN

    def test_a_watched_pass_is_compared_once_and_must_carry_its_lens(self):
        def body():
            self.passed("plan", self.start)
            self.tick_work()
            sha = self.ui_build()
            self.passed("round", sha, lenses=["adversarial", "integration", "design"])
            self.passed("completion", sha)
            self.stamp3(sha)
            # The entry names the round alone: one comparison for it, none for the plan review or the completion.
            self.assertEqual(self.read_graph(), (["-c", "cat-file", "rev-list"], 1))
            findings = self.root / self.FILE
            recorded = findings.read_bytes()
            with_lens = b"- Lenses: adversarial, integration, design\n"
            self.assertEqual(recorded.count(with_lens), 1)
            # The same receipt with the lens its changed file calls for left out of the recorded round is refused.
            findings.write_bytes(recorded.replace(with_lens, b"- Lenses: adversarial, integration\n"))
            with self.assertRaises(tg.Refused) as ctx:
                tg.graph(self.root)
            self.assertIn("the schedule expects medium with ['adversarial', 'integration', 'design']",
                          str(ctx.exception))
        self.with_pin('"round"', body)

    def test_a_pass_that_changed_no_watched_file_carries_no_conditional_lens(self):
        def body():
            sha = self.chain()  # the build touches nothing under src/ui/
            self.stamp3(sha)
            self.assertEqual(self.read_graph(), (["-c", "cat-file", "rev-list"], 1))
        self.with_pin('"round"', body)

    def test_two_passes_on_one_pair_of_commits_are_compared_once(self):
        def body():
            self.passed("plan", self.start)
            self.tick_work()
            sha = self.ui_build()
            self.passed("round", sha, lenses=["adversarial", "integration", "design"])
            self.passed("completion", sha, lenses=["plan-delivery", "record", "design"])
            self.stamp3(sha)
            self.assertEqual(self.read_graph(), (["-c", "cat-file", "rev-list"], 1))
        self.with_pin('"round", "completion"', body)

    def test_a_pin_with_no_conditional_entry_compares_nothing(self):
        self.stamp3(self.chain(completion=("P2", True), reconciliations=[("none", False)]), verdict="reconciled")
        self.assertEqual(self.read_graph(), (["cat-file", "rev-list"], 1))

    def refusal(self):
        """What graph() refuses with, read through the batch process and then with every question asked the direct
        way, as it was before D00 T03 §62: the same message both ways. No read and no batch process is left."""
        batches, real = [], subprocess.Popen

        def popen(args, *rest, **kwargs):
            process = real(args, *rest, **kwargs)
            if "cat-file" in [str(a) for a in args]:
                batches.append(process)
            return process
        with mock.patch.object(tg.subprocess, "Popen", popen), self.assertRaises(tg.Refused) as batched:
            tg.graph(self.root)
        self.assertEqual(tg._READS, [])
        self.assertTrue(all(process.poll() is not None for process in batches), "a batch process outlived its read")
        with mock.patch.object(tg, "_reading", lambda root: None), self.assertRaises(tg.Refused) as direct:
            tg.graph(self.root)
        self.assertEqual(str(batched.exception), str(direct.exception))
        return str(batched.exception), len(batches)

    def test_a_tampered_receipt_is_refused_as_before_and_leaves_no_process(self):
        sha = self.chain()
        data = self.stamp3(sha)
        findings, receipt = self.root / self.FILE, self.root / "docs/reviews/d00-t01-s1.json"
        todo = self.root / "todo/00-workspace/TODO-01-a.md"
        kept = {path: path.read_bytes() for path in (findings, receipt, todo)}

        def restore():
            for path, content in kept.items():
                path.write_bytes(content)
        later = self.build("later")
        with self.subTest("a round on a candidate after the completion's"):
            text = kept[findings].decode("utf-8")
            at = text.index("- Candidate: ", text.index("## Round 1"))
            findings.write_bytes((text[:at] + text[at:].replace(sha, later, 1)).encode("utf-8"))
            message, batches = self.refusal()
            self.assertIn("the completion review must run after the round, on a candidate at or after it", message)
            self.assertEqual(batches, 1)  # the read had asked its batch process before it refused
        restore()
        with self.subTest("a plan review candidate that holds no pin"):
            (self.root / tg.PIN).unlink()
            bare = self.commit("no pin")
            (self.root / tg.PIN).write_text(self.PIN_TEXT, encoding="utf-8")
            self.commit("pin back")
            edited = json.loads(json.dumps(data))
            edited["plan"]["candidate"] = bare
            receipt.write_text(json.dumps(edited, indent=2) + "\n", encoding="utf-8")
            text = kept[findings].decode("utf-8")
            at = text.index("- Candidate: ", text.index("## Plan review"))
            findings.write_bytes((text[:at] + text[at:].replace(self.start, bare, 1)).encode("utf-8"))
            message, _ = self.refusal()
            self.assertIn("the commit whose pin the section ran under", message)
        restore()
        with self.subTest("a fabricated stamp commit"):
            fake = "0" * 40
            for path in (todo, receipt, findings):
                path.write_bytes(kept[path].replace(sha.encode("ascii"), fake.encode("ascii")))
            message, _ = self.refusal()
            self.assertIn("not a commit: " + fake, message)
        restore()
        self.assertTrue(tg.graph(self.root)["D00 T01 §1"].done)  # and the untouched receipt still reads back

    def test_an_attempt_on_a_commit_the_repository_no_longer_holds_is_still_refused(self):
        # Round 1, finding 1: a completion attempt that returned no review, on a build that was then replaced and
        # pruned. The comparison of its candidate with the plan's was the one check that failed on it, so skipping
        # the comparison for an unwatched pass must not skip that refusal.
        self.passed("plan", self.start)
        self.tick_work()
        abandoned = self.build("first build")
        outage = {"writer": "claude", "reviewer": None, "model": self.MODEL, "cli": self.CLI, "effort": "medium",
                  "lenses": self.LENSES["completion"], "failover": [{"reviewer": "astra", "reason": "exited 3"}],
                  "review": None}
        self.clock += 1
        tg.review_dispatch().record_completion(self.root / self.FILE, outage, f"2026-10-23T00:00:{self.clock:02d}Z",
                                               abandoned, kind="completion")
        subprocess.run(["git", "-C", str(self.root), "reset", "-q", "--soft", "HEAD~1"], check=True)
        sha = self.build("the build that replaced it")
        self.passed("round", sha)
        self.passed("completion", sha)
        self.stamp3(sha)
        # While the abandoned commit is still in the object store the receipt reads back, and the read compares it
        # with the plan's candidate the direct way, since it is outside HEAD's history.
        self.assertEqual(self.read_graph(), (["-c", "cat-file", "rev-list"], 1))
        for args in (["reflog", "expire", "--expire=now", "--all"], ["gc", "-q", "--prune=now"]):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)
        gone = subprocess.run(["git", "-C", str(self.root), "cat-file", "-e", abandoned], capture_output=True)
        self.assertNotEqual(gone.returncode, 0)
        message, _ = self.refusal()
        self.assertIn(f"cannot list the files changed between {self.start} and {abandoned}", message)


# GraphReadProcesses borrows ThreePassStamp's fixture, not its tests: those run once, in ThreePassStamp.
for _name in dir(ThreePassStamp):
    if _name.startswith("test_") and _name not in vars(GraphReadProcesses):
        setattr(GraphReadProcesses, _name, None)


if __name__ == "__main__":
    unittest.main()
