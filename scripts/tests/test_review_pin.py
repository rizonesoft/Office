# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/review_pin.py: the pin's rules. Every key refuses a wrong value with a message naming the key, a rotation
pin means what it meant, and the three-pass lookups (lenses, caps, blocking, lens verdicts) answer from the pin."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import tomllib
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("review_pin_under_test", SCRIPTS / "review_pin.py")
review_pin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review_pin)

HEAD = textwrap.dedent('''\
    schema_version = 1

    [reviewers.astra]
    cli = "codex"
    model = "gpt-6-astra"
    effort = "medium"

    [routes]
    claude = ["astra"]
''')

ROTATION = HEAD + textwrap.dedent('''
    [schedule]
    severity_stop_after = 0

    [schedule.plan]
    effort = "medium"
    lenses = ["plan"]

    [schedule.completion]
    effort = "medium"

    [[schedule.rounds]]
    effort = "high"
    lenses = ["adversarial", "integration"]

    [[schedule.rounds]]
    effort = "low"
    lenses = ["adversarial"]

    [schedule.rotation]
    effort = "low"
    lenses = ["consistency", "design", "record"]

    [schedule.escalation]
    effort = "medium"
    lenses = ["adversarial"]
''')

THREE_PASS = HEAD + textwrap.dedent('''
    [schedule]
    policy = "three-pass"
    pass_cap = 45
    no_progress_cap = 3
    blocking = ["P1", "P2"]

    [schedule.lenses]
    concurrency = "On two or more CPUs, which lock or teardown order is wrong?"

    [schedule.plan]
    effort = "medium"
    lenses = ["plan"]

    [[schedule.rounds]]
    effort = "medium"
    lenses = ["adversarial", "integration", "quality"]

    [schedule.completion]
    effort = "medium"
    lenses = ["plan-delivery", "record"]

    [schedule.reconciliation]
    effort = "medium"
    lenses = ["adversarial", "plan-delivery", "record"]

    [[schedule.conditional]]
    lenses = ["concurrency"]
    passes = ["round", "reconciliation"]
    paths = ["src/kernel/", "include/kernel/"]

    [[schedule.conditional]]
    lenses = ["design"]
    passes = ["plan", "round"]
    paths = ["src/ui/"]
''')

# The three-pass pin as it was written before completion had lenses and before the optional keys existed.
EARLIER_THREE_PASS = HEAD + textwrap.dedent('''
    [schedule]
    policy = "three-pass"

    [schedule.plan]
    effort = "medium"
    lenses = ["plan"]

    [[schedule.rounds]]
    effort = "medium"
    lenses = ["adversarial", "plan-delivery", "record", "design"]

    [schedule.completion]
    effort = "medium"

    [schedule.reconciliation]
    effort = "medium"
    lenses = ["adversarial", "plan-delivery", "record"]
''')


def load(text):
    return review_pin.load_pin(data=text.encode("utf-8"))


class Cases(unittest.TestCase):
    def refuses(self, text, *needles):
        self.assertNotIn(text, (ROTATION, THREE_PASS, EARLIER_THREE_PASS), "the edit matched nothing")
        with self.assertRaises(review_pin.Refused) as refused:
            load(text)
        for needle in needles:
            self.assertIn(needle, str(refused.exception))


class Rotation(Cases):
    def test_a_rotation_pin_schedules_what_it_always_did(self):
        schedule = load(ROTATION)["schedule"]
        step = review_pin.scheduled
        self.assertEqual(step(schedule, "plan", [], False),
                         {"position": None, "effort": "medium", "lenses": ["plan"], "escalated": False})
        self.assertEqual(step(schedule, "completion", [], False),
                         {"position": None, "effort": "medium", "lenses": [], "escalated": False})
        self.assertEqual(step(schedule, "round", [], False),
                         {"position": 1, "effort": "high", "lenses": ["adversarial", "integration"],
                          "escalated": False})

        def returned(effort, top):
            return {"reviewer": "astra", "writer": "claude", "cli": "codex", "effort": effort,
                    "review": f"1. x\nHIGHEST: {top}\nOVERALL: needs-attention"}
        two = [returned("high", "P2"), returned("low", "P2")]
        self.assertEqual(step(schedule, "round", two, False)["lenses"], ["consistency"])
        # The design lens joins the rotation only for a section with a surface.
        three = two + [returned("low", "P2")]
        self.assertEqual(step(schedule, "round", three, False)["lenses"], ["record"])
        self.assertEqual(step(schedule, "round", three, True)["lenses"], ["design"])
        # A low-effort round that found a P1 is followed by the escalation step.
        escalated = step(schedule, "round", [returned("high", "P2"), returned("low", "P1")], False)
        self.assertEqual((escalated["effort"], escalated["lenses"], escalated["escalated"]),
                         ("medium", ["adversarial"], True))
        # An outage does not move the position.
        self.assertEqual(step(schedule, "round", [{"reviewer": None, "writer": "claude"}], False)["position"], 1)

    def test_a_rotation_schedule_takes_none_of_the_three_pass_keys(self):
        for key in ('pass_cap = 33', 'no_progress_cap = 3', 'blocking = ["P1"]'):
            with self.subTest(key=key):
                self.refuses(ROTATION.replace("severity_stop_after = 0", f"severity_stop_after = 0\n{key}"),
                             "[schedule] needs exactly", "severity_stop_after")
        self.refuses(ROTATION + '\n[schedule.reconciliation]\neffort = "low"\nlenses = ["record"]\n',
                     "[schedule] needs exactly")
        self.refuses(ROTATION + '\n[[schedule.conditional]]\nlenses = ["design"]\npasses = ["round"]\npaths = ["a/"]\n',
                     "[schedule] needs exactly")

    def test_an_unknown_policy_is_refused(self):
        self.refuses(ROTATION.replace("severity_stop_after = 0", 'policy = "rotation"\nseverity_stop_after = 0'),
                     "policy", "three-pass")
        self.refuses(THREE_PASS.replace('policy = "three-pass"', "policy = 3"), "policy")

    def test_effort_is_optional_on_reviewers_and_steps(self):
        bare = ROTATION.replace('effort = "medium"\n', "").replace('effort = "high"\n', "").replace('effort = "low"\n', "")
        self.assertNotIn("effort", bare)
        schedule = load(bare)["schedule"]
        self.assertIsNone(review_pin.scheduled(schedule, "plan", [], False)["effort"])
        self.assertIsNone(review_pin.scheduled(schedule, "round", [], False)["effort"])
        self.assertNotIn("effort", load(THREE_PASS.replace('effort = "medium"\n', ""))["reviewers"]["astra"])
        # A wrong one still refuses, naming where.
        self.refuses(ROTATION.replace('[schedule.plan]\neffort = "medium"', '[schedule.plan]\neffort = "extreme"'),
                     "[schedule] plan needs effort")
        self.refuses(ROTATION.replace('[schedule.plan]\neffort = "medium"', '[schedule.plan]\neffort = 3'),
                     "[schedule] plan needs effort")
        self.refuses(THREE_PASS.replace('[schedule.reconciliation]\neffort = "medium"',
                                        '[schedule.reconciliation]\neffort = "max"'),
                     "[schedule] reconciliation needs effort")
        self.refuses(HEAD.replace('effort = "medium"', 'effort = "extreme"'), "reviewer 'astra' needs effort")
        self.refuses(HEAD.replace('effort = "medium"', "effort = 5"), "reviewer 'astra' needs effort")


class ThreePass(Cases):
    def test_the_policy_needs_its_four_passes_and_exactly_one_round(self):
        schedule = load(THREE_PASS)["schedule"]
        self.assertEqual(schedule["policy"], review_pin.THREE_PASS)
        second = '\n[[schedule.rounds]]\neffort = "medium"\nlenses = ["optimization"]\n'
        self.refuses(THREE_PASS + second, "exactly one round in rounds")
        head, _, tail = THREE_PASS.partition("[schedule.reconciliation]")
        self.refuses(head + "[[schedule.conditional]]" + tail.partition("[[schedule.conditional]]")[2],
                     "needs exactly", "reconciliation")
        self.refuses(THREE_PASS.replace("pass_cap = 45", "pass_cap = 45\nseverity_stop_after = 0"), "needs exactly")
        self.refuses(THREE_PASS.replace('lenses = ["plan"]', 'lenses = ["vibes"]'), "[schedule] plan needs lenses")
        self.refuses(THREE_PASS.replace('lenses = ["plan"]', 'lenses = ["plan", "plan"]'), "distinct lenses")

    def test_the_earlier_three_pass_pin_still_loads(self):
        # A section keeps the pin it began under, so a pin from before completion lenses and the optional keys loads.
        schedule = load(EARLIER_THREE_PASS)["schedule"]
        self.assertEqual(review_pin.pass_cap(schedule), 33)
        self.assertIsNone(review_pin.no_progress_cap(schedule))
        self.assertEqual(review_pin.scheduled(schedule, "completion", [], False)["lenses"], [])
        self.assertTrue(all(review_pin.blocks(schedule, level) for level in ("P1", "P2", "P3", None)))
        # Without a conditional entry, --surface still decides the round's design lens.
        self.assertNotIn("design", review_pin.scheduled(schedule, "round", [], False)["lenses"])
        self.assertIn("design", review_pin.scheduled(schedule, "round", [], True)["lenses"])

    def test_a_lens_has_one_owner_among_plan_round_and_completion(self):
        both = THREE_PASS.replace('lenses = ["adversarial", "integration", "quality"]',
                                  'lenses = ["adversarial", "integration", "quality", "plan-delivery"]')
        self.refuses(both, "the lens plan-delivery is listed in both round and completion")
        self.refuses(THREE_PASS.replace('lenses = ["plan-delivery", "record"]', 'lenses = ["plan", "record"]'),
                     "the lens plan is listed in both plan and completion")
        # A conditional entry cannot hand an owned lens to another of the three passes (round 1 of D00 T01 §1).
        entry = '[[schedule.conditional]]\nlenses = ["design"]\npasses = ["plan", "round"]\npaths = ["src/ui/"]\n'
        self.assertIn(entry, THREE_PASS)
        for lens, passes, owner in (("plan", '["round"]', "plan"), ("quality", '["plan"]', "round"),
                                    ("record", '["round"]', "completion"), ("adversarial", '["completion"]', "round")):
            with self.subTest(lens=lens, passes=passes):
                moved = entry.replace('["design"]', f'["{lens}"]').replace('["plan", "round"]', passes)
                self.refuses(THREE_PASS.replace(entry, moved), f"the lens {lens}, which belongs to {owner}")
        # Reconciliation may be given an owned lens by path, as it may list one outright.
        given = entry.replace('["design"]', '["quality"]').replace('["plan", "round"]', '["reconciliation"]')
        schedule = load(THREE_PASS.replace(entry, given))["schedule"]
        self.assertIn("quality", review_pin.lenses_for(schedule, "reconciliation", ["src/ui/a.c"]))
        # Reconciliation repeats the round's and the completion's lenses in the fixture, and loads.
        reconciliation = load(THREE_PASS)["schedule"]["reconciliation"]["lenses"]
        self.assertEqual(reconciliation, ["adversarial", "plan-delivery", "record"])

    def test_extra_lenses_are_declared_with_their_question(self):
        schedule = load(THREE_PASS)["schedule"]
        self.assertIn("concurrency", review_pin.lens_table(schedule))
        named = THREE_PASS.replace('lenses = ["adversarial", "integration", "quality"]',
                                   'lenses = ["adversarial", "integration", "quality", "bare-metal"]')
        self.refuses(named, "[schedule] round 1 needs lenses")
        declared = named.replace('concurrency = "On', 'bare-metal = "What fails on real hardware?"\nconcurrency = "On')
        self.assertIn("bare-metal", load(declared)["schedule"]["rounds"][0]["lenses"])
        line = 'concurrency = "On two or more CPUs, which lock or teardown order is wrong?"'
        for bad, needle in ((THREE_PASS.replace(line, "concurrency = 7"), "'concurrency' needs its question"),
                            (THREE_PASS.replace(line, 'concurrency = ""'), "'concurrency' needs its question"),
                            (THREE_PASS.replace(line, line + '\nBad_Name = "x"'), "'Bad_Name' is not a lens name"),
                            (THREE_PASS.replace(line, line + '\nquality = "Mine"'), "'quality' is already a built-in"),
                            (THREE_PASS.replace("[schedule.lenses]\n" + line, "").replace(
                                "blocking = [\"P1\", \"P2\"]", "blocking = [\"P1\", \"P2\"]\nlenses = 3"),
                             "[schedule.lenses] must be a table")):
            with self.subTest(needle=needle):
                self.refuses(bad, "[schedule.lenses]", needle)

    def test_conditional_lenses_join_only_a_named_pass_with_a_matching_path(self):
        schedule = load(THREE_PASS)["schedule"]
        base = ["adversarial", "integration", "quality"]
        lenses = review_pin.lenses_for
        self.assertEqual(lenses(schedule, "round"), base)
        self.assertEqual(lenses(schedule, "round", ["docs/a.md", "src/app/x.c"]), base)
        self.assertEqual(lenses(schedule, "round", ["src/kernel/sched.c"]), base + ["concurrency"])
        self.assertEqual(lenses(schedule, "round", ["src/ui/a.c", "include/kernel/x.h"]),
                         base + ["concurrency", "design"])
        # Named passes only: completion never takes them, plan takes design, reconciliation takes concurrency.
        self.assertEqual(lenses(schedule, "completion", ["src/kernel/sched.c", "src/ui/a.c"]),
                         ["plan-delivery", "record"])
        self.assertEqual(lenses(schedule, "plan", ["src/kernel/sched.c", "src/ui/a.c"]), ["plan", "design"])
        self.assertEqual(lenses(schedule, "reconciliation", ["src/kernel/sched.c", "src/ui/a.c"]),
                         ["adversarial", "plan-delivery", "record", "concurrency"])
        # `scheduled` is the same lookup, so the dispatcher and the stamp agree.
        self.assertEqual(review_pin.scheduled(schedule, "round", [], False, ["src/kernel/sched.c"])["lenses"],
                         base + ["concurrency"])

    def test_a_hidden_folder_is_a_path_prefix_like_any_other(self):
        hidden = THREE_PASS.replace('paths = ["src/ui/"]', 'paths = [".github/", ".conclave/reviewers.toml"]')
        schedule = load(hidden)["schedule"]
        self.assertIn("design", review_pin.lenses_for(schedule, "round", [".github/workflows/ci.yml"]))
        self.assertIn("design", review_pin.lenses_for(schedule, "plan", [".conclave/reviewers.toml"]))
        self.assertNotIn("design", review_pin.lenses_for(schedule, "round", ["github/x", "src/.github/x"]))

    def test_a_key_refusal_names_the_offending_key(self):
        self.refuses(THREE_PASS.replace("pass_cap = 45", "pass_cpa = 45"), "(unknown: pass_cpa)")
        head, _, tail = THREE_PASS.partition("[schedule.reconciliation]")
        self.refuses(head + "[[schedule.conditional]]" + tail.partition("[[schedule.conditional]]")[2],
                     "(missing: reconciliation)")
        self.refuses(ROTATION.replace("severity_stop_after = 0", "severity_stop = 0"),
                     "[schedule] needs exactly", "(unknown: severity_stop; missing: severity_stop_after)")
        self.refuses(THREE_PASS.replace('paths = ["src/ui/"]', 'path = ["src/ui/"]'),
                     "[[schedule.conditional]] entry 2", "(unknown: path; missing: paths)")
        self.refuses(THREE_PASS.replace('[schedule.plan]\neffort = "medium"', '[schedule.plan]\nefort = "medium"'),
                     "[schedule] plan needs", "(unknown: efort)")
        self.refuses(ROTATION.replace('[schedule.completion]\neffort = "medium"',
                                      '[schedule.completion]\neffort = "medium"\nlenses = ["record"]'),
                     "[schedule] completion needs only effort", "(unknown: lenses)")
        self.refuses(ROTATION.replace('[schedule.plan]\neffort = "medium"\nlenses = ["plan"]',
                                      '[schedule.plan]\neffort = "medium"'),
                     "[schedule] plan needs", "(missing: lenses)")

    def test_a_conditional_entry_refuses_each_wrong_value(self):
        entry = '[[schedule.conditional]]\nlenses = ["concurrency"]\npasses = ["round", "reconciliation"]\n' \
                'paths = ["src/kernel/", "include/kernel/"]\n'
        self.assertIn(entry, THREE_PASS)
        for old, new, needle in (
                ('lenses = ["concurrency"]', 'lenses = "concurrency"', "needs lenses"),
                ('lenses = ["concurrency"]', 'lenses = ["nope"]', "needs lenses"),
                ('lenses = ["concurrency"]', 'lenses = ["concurrency", "concurrency"]', "needs lenses"),
                ('lenses = ["concurrency"]', 'lenses = ["adversarial"]', "repeats the lens adversarial, which the round"),
                ('passes = ["round", "reconciliation"]', 'passes = ["rounds"]', "needs passes"),
                ('passes = ["round", "reconciliation"]', 'passes = ["round", "round"]', "needs passes"),
                ('passes = ["round", "reconciliation"]', 'passes = "round"', "needs passes"),
                ('passes = ["round", "reconciliation"]', "passes = []", "needs passes"),
                ('paths = ["src/kernel/", "include/kernel/"]', 'paths = ["/abs/"]', "needs paths"),
                ('paths = ["src/kernel/", "include/kernel/"]', 'paths = ["src/../etc/"]', "needs paths"),
                ('paths = ["src/kernel/", "include/kernel/"]', 'paths = ["./src/"]', "needs paths"),
                ('paths = ["src/kernel/", "include/kernel/"]', 'paths = ["C:/src/"]', "needs paths"),
                ('paths = ["src/kernel/", "include/kernel/"]', 'paths = ["src\\\\kernel"]', "needs paths"),
                ('paths = ["src/kernel/", "include/kernel/"]', 'paths = ["a/", "a/"]', "needs paths"),
                ('paths = ["src/kernel/", "include/kernel/"]', "paths = [3]", "needs paths"),
                ('paths = ["src/kernel/", "include/kernel/"]', "paths = []", "needs paths"),
                ('paths = ["src/kernel/", "include/kernel/"]', 'paths = ["a/"]\nwhen = "always"', "needs exactly")):
            with self.subTest(new=new):
                self.refuses(THREE_PASS.replace(entry, entry.replace(old, new)), "[[schedule.conditional]] entry 1",
                             needle)
        # A prefix that could never match a changed file is refused rather than silently ignored.
        for bad in ('paths = ["src//x/"]', 'paths = ["src/./"]', 'paths = ["/"]', 'paths = [" src/"]'):
            with self.subTest(bad=bad):
                self.refuses(THREE_PASS.replace(entry, entry.replace(
                    'paths = ["src/kernel/", "include/kernel/"]', bad)), "needs paths")
        self.refuses(THREE_PASS.partition("[[schedule.conditional]]")[0].replace(
            "pass_cap = 45", "pass_cap = 45\nconditional = 3"), "[[schedule.conditional]] must be an array")

    def test_blocking_names_the_levels_that_hold_the_stamp(self):
        schedule = load(THREE_PASS)["schedule"]
        self.assertTrue(review_pin.blocks(schedule, "P1"))
        self.assertTrue(review_pin.blocks(schedule, "P2"))
        self.assertFalse(review_pin.blocks(schedule, "P3"))
        self.assertFalse(review_pin.blocks(schedule, "none"))
        # A review that declared no HIGHEST line counts as P1.
        self.assertTrue(review_pin.blocks(schedule, None))
        only_p1 = load(THREE_PASS.replace('blocking = ["P1", "P2"]', 'blocking = ["P1"]'))["schedule"]
        self.assertFalse(review_pin.blocks(only_p1, "P2"))
        for bad in ('blocking = ["P2", "P3"]', 'blocking = ["P1", "P4"]', 'blocking = ["P1", "P1"]',
                    'blocking = "P1"', "blocking = []", "blocking = [1]"):
            with self.subTest(bad=bad):
                self.refuses(THREE_PASS.replace('blocking = ["P1", "P2"]', bad), "[schedule] blocking needs")

    def test_declared_highest_reads_the_last_highest_line(self):
        self.assertEqual(review_pin.declared_highest("x\nHIGHEST: P2\nCOMPLETION: gaps"), "P2")
        self.assertEqual(review_pin.declared_highest("HIGHEST: P1\nlater\nHIGHEST: none\nOVERALL: approve"), "none")
        self.assertIsNone(review_pin.declared_highest("no line here"))

    def test_the_caps_come_from_the_pin(self):
        schedule = load(THREE_PASS)["schedule"]
        self.assertEqual(review_pin.pass_cap(schedule), 45)
        self.assertEqual(review_pin.no_progress_cap(schedule), 3)
        without = load(THREE_PASS.replace("pass_cap = 45\n", "").replace("no_progress_cap = 3\n", ""))["schedule"]
        self.assertEqual(review_pin.pass_cap(without), 33)
        self.assertIsNone(review_pin.no_progress_cap(without))
        for bad in ("pass_cap = true", "pass_cap = 2", "pass_cap = 1000", 'pass_cap = "33"', "pass_cap = 3.0"):
            with self.subTest(bad=bad):
                self.refuses(THREE_PASS.replace("pass_cap = 45", bad).replace("no_progress_cap = 3\n", ""),
                             "[schedule] pass_cap needs")
        for bad in ("no_progress_cap = true", "no_progress_cap = 0", "no_progress_cap = 46", 'no_progress_cap = "3"'):
            with self.subTest(bad=bad):
                self.refuses(THREE_PASS.replace("no_progress_cap = 3", bad), "[schedule] no_progress_cap needs")
        # The bound is the pin's own pass_cap, 33 when the key is absent.
        self.refuses(THREE_PASS.replace("pass_cap = 45\n", "").replace("no_progress_cap = 3", "no_progress_cap = 34"),
                     "[schedule] no_progress_cap needs", "(33)")

    def test_an_antigravity_model_name_agrees_with_the_schedules_efforts(self):
        argon = THREE_PASS.replace('cli = "codex"\nmodel = "gpt-6-astra"\neffort = "medium"',
                                   'cli = "agy"\nmodel = "gemini-4-argon-medium"')
        self.assertEqual(load(argon)["reviewers"]["astra"]["cli"], "agy")
        self.refuses(argon.replace("gemini-4-argon-medium", "gemini-4-argon-high"),
                     "runs at the effort in its model name gemini-4-argon-high", "effort = medium")
        # With no effort set by the schedule there is nothing to disagree with.
        bare = argon.replace("gemini-4-argon-medium", "gemini-4-argon-high").replace('effort = "medium"\n', "")
        self.assertNotIn("effort", bare)
        load(bare)
        # A rotation pin with an Antigravity reviewer loads as it always did, whatever its efforts.
        load(ROTATION.replace('cli = "codex"\nmodel = "gpt-6-astra"\neffort = "medium"',
                              'cli = "agy"\nmodel = "gemini-4-argon-high"'))

    def test_the_lens_block_asks_each_lens_its_question_and_for_its_verdict_line(self):
        schedule = load(THREE_PASS)["schedule"]
        plan = review_pin.scheduled(schedule, "round", [], False, ["src/kernel/a.c"])
        block = review_pin.lens_block(plan, schedule)
        self.assertIn(f"- `adversarial`: {review_pin.LENSES['adversarial']}", block)
        self.assertIn("- `concurrency`: On two or more CPUs, which lock or teardown order is wrong?", block)
        for name in plan["lenses"]:
            self.assertIn(f"LENS {name}: <clean|findings>", block)
        self.assertIn("HIGHEST: none", block)
        self.assertIn("Round 1 runs at medium reasoning effort", block)
        # A rotation block is the text it always was: no verdict lines are asked for.
        rotation = load(ROTATION)["schedule"]
        old = review_pin.lens_block(review_pin.scheduled(rotation, "round", [], False), rotation)
        self.assertNotIn("LENS ", old)
        self.assertTrue(old.endswith(f"- `integration`: {review_pin.LENSES['integration']}\n"))
        # A step with no effort says so without naming one.
        bare = review_pin.lens_block({"position": None, "effort": None, "lenses": ["plan"], "escalated": False})
        self.assertIn("This pass has these lenses.", bare)

    def test_a_reply_owes_one_verdict_line_per_lens(self):
        lenses = ["adversarial", "integration", "quality"]
        reply = "1. P2 a.py:3 breaks\nLENS adversarial: findings\n`LENS integration: clean`\n  LENS quality: clean  \n" \
                "HIGHEST: P2\nOVERALL: needs-attention"
        self.assertEqual(review_pin.missing_lens_verdicts(lenses, reply), [])
        self.assertEqual(review_pin.missing_lens_verdicts(lenses, reply.replace("LENS quality: clean", "")),
                         ["quality"])
        # Only the two verdict words count, and a line with anything else on it is not a verdict line.
        self.assertEqual(review_pin.missing_lens_verdicts(lenses, reply.replace("quality: clean", "quality: maybe")),
                         ["quality"])
        self.assertEqual(review_pin.missing_lens_verdicts(lenses, reply.replace("LENS adversarial", "- LENS adversarial")),
                         ["adversarial"])
        self.assertEqual(review_pin.missing_lens_verdicts(lenses, ""), lenses)
        self.assertEqual(review_pin.missing_lens_verdicts([], "anything"), [])


class Faults(unittest.TestCase):
    """`faults`: every independent fault at once, in the order of the pin's tables, while `load_pin` keeps its own."""

    def found(self, text):
        return review_pin.faults(data=text.encode("utf-8"))

    def first(self, text):
        with self.assertRaises(review_pin.Refused) as refused:
            load(text)
        return str(refused.exception)

    def test_a_pin_that_loads_has_no_faults(self):
        for text in (HEAD, ROTATION, THREE_PASS, EARLIER_THREE_PASS):
            self.assertEqual(self.found(text), [])

    def test_three_independent_faults_are_all_reported(self):
        bad = THREE_PASS.replace("pass_cap = 45", "pass_cap = 2").replace(
            'blocking = ["P1", "P2"]', 'blocking = ["P2"]').replace(
            'lenses = ["adversarial", "plan-delivery", "record"]', 'lenses = ["adversarial", "vibes"]')
        found = self.found(bad)
        self.assertEqual(len(found), 3, found)
        self.assertIn("[schedule] pass_cap needs", found[0])
        self.assertIn("[schedule] blocking needs", found[1])
        self.assertIn("[schedule] reconciliation needs lenses", found[2])
        # load_pin still raises one of them, and it is among those listed.
        self.assertIn(self.first(bad), found)

    def test_the_loader_keeps_its_order_while_faults_follows_the_file(self):
        # The loader checks the steps before the caps; the file has pass_cap before [schedule.plan].
        bad = THREE_PASS.replace("pass_cap = 45", "pass_cap = 2").replace('lenses = ["plan"]', 'lenses = ["vibes"]')
        self.assertIn("[schedule] plan needs lenses", self.first(bad))
        found = self.found(bad)
        self.assertEqual([m.split(" needs")[0] for m in found], ["[schedule] pass_cap", "[schedule] plan"])

    def test_faults_across_reviewers_routes_and_the_schedule(self):
        bad = THREE_PASS.replace('cli = "codex"', 'cli = "bash"').replace(
            'claude = ["astra"]', 'claude = ["astra"]\nopus = ["astra"]').replace("pass_cap = 45", "pass_cap = 1000")
        found = self.found(bad)
        self.assertEqual(len(found), 3, found)
        self.assertIn("reviewer 'astra' needs cli", found[0])
        self.assertIn("[routes] may only name the writers", found[1])
        self.assertIn("[schedule] pass_cap needs", found[2])
        # The route to the reviewer whose own entry is at fault adds nothing of its own.
        only = self.found(THREE_PASS.replace('cli = "codex"', 'cli = "bash"'))
        self.assertEqual(len(only), 1, only)
        self.assertIn("reviewer 'astra' needs cli", only[0])
        # A route that is itself wrong is still reported beside a sound reviewer.
        routes = self.found(HEAD.replace('claude = ["astra"]', 'claude = ["astra", "astra"]\ncodex = ["nobody"]'))
        self.assertEqual(len(routes), 2, routes)
        self.assertIn("route 'claude' must list exactly one reviewer", routes[0])
        self.assertIn("route 'codex' must list a defined reviewer", routes[1])

    def test_a_rotation_schedule_reports_each_bad_step(self):
        bad = ROTATION.replace('[schedule.plan]\neffort = "medium"', '[schedule.plan]\neffort = "extreme"').replace(
            '[schedule.escalation]\neffort = "medium"\nlenses = ["adversarial"]',
            '[schedule.escalation]\neffort = "medium"\nlenses = ["nope"]').replace(
            "severity_stop_after = 0", "severity_stop_after = 99")
        found = self.found(bad)
        self.assertEqual(len(found), 3, found)
        self.assertIn("severity_stop_after needs", found[0])
        self.assertIn("[schedule] plan needs effort", found[1])
        self.assertIn("[schedule] escalation needs lenses", found[2])
        # A wrong key set is one fault, and nothing under it is looked at.
        keys = self.found(ROTATION.replace("severity_stop_after = 0", "severity_stop = 0").replace(
            '[schedule.plan]\neffort = "medium"', '[schedule.plan]\neffort = "extreme"'))
        self.assertEqual(len(keys), 1, keys)
        self.assertIn("(unknown: severity_stop; missing: severity_stop_after)", keys[0])

    def test_extra_lenses_and_conditional_entries_are_each_checked(self):
        line = 'concurrency = "On two or more CPUs, which lock or teardown order is wrong?"'
        bad = THREE_PASS.replace(line, line + '\nquality = "Mine"\nBad_Name = "x"').replace(
            'passes = ["plan", "round"]', 'passes = ["rounds"]').replace(
            'paths = ["src/kernel/", "include/kernel/"]', 'paths = ["/abs/"]')
        found = self.found(bad)
        self.assertEqual(len(found), 4, found)
        self.assertIn("'quality' is already a built-in lens", found[0])
        self.assertIn("'Bad_Name' is not a lens name", found[1])
        self.assertIn("[[schedule.conditional]] entry 1 needs paths", found[2])
        self.assertIn("[[schedule.conditional]] entry 2 needs passes", found[3])

    def test_a_bad_lens_declaration_is_reported_once_where_it_is_declared(self):
        # Round of D00 T01 §5: an empty question also made every entry naming that lens look at fault.
        line = 'concurrency = "On two or more CPUs, which lock or teardown order is wrong?"'
        found = self.found(THREE_PASS.replace(line, 'concurrency = ""'))
        self.assertEqual(len(found), 1, found)
        self.assertIn("'concurrency' needs its question", found[0])

    def test_independent_faults_inside_one_table_are_each_reported(self):
        # Round of D00 T01 §5: only the first fault of a step was reported.
        step = self.found(THREE_PASS.replace('[schedule.plan]\neffort = "medium"\nlenses = ["plan"]',
                                             '[schedule.plan]\neffort = "bogus"\nlenses = ["unknown"]'))
        self.assertEqual(len(step), 2, step)
        self.assertIn("[schedule] plan needs effort", step[0])
        self.assertIn("[schedule] plan needs lenses", step[1])
        rotation = self.found(ROTATION.replace('[schedule.escalation]\neffort = "medium"\nlenses = ["adversarial"]',
                                               '[schedule.escalation]\neffort = "max"\nlenses = []'))
        self.assertEqual(len(rotation), 2, rotation)
        reviewer = self.found(HEAD.replace('model = "gpt-6-astra"\neffort = "medium"',
                                           'model = "bad model"\neffort = "extreme"\nsandbox = "x"'))
        self.assertEqual(len(reviewer), 3, reviewer)
        self.assertIn("unknown keys: sandbox", reviewer[0])
        self.assertIn("malformed model", reviewer[1])
        self.assertIn("needs effort", reviewer[2])
        # The effort rests on the cli: with a bad cli only the cli is reported.
        cli = self.found(HEAD.replace('cli = "codex"', 'cli = "bash"').replace('effort = "medium"', 'effort = "extreme"'))
        self.assertEqual(len(cli), 1, cli)
        entry = self.found(THREE_PASS.replace('lenses = ["design"]\npasses = ["plan", "round"]\npaths = ["src/ui/"]',
                                              'lenses = ["nope"]\npasses = ["rounds"]\npaths = ["/abs/"]'))
        self.assertEqual(len(entry), 3, entry)
        lens = self.found(THREE_PASS.replace('concurrency = "On two or more CPUs, which lock or teardown order is wrong?"',
                                             'Bad_Name = 7'))
        self.assertIn("'Bad_Name' is not a lens name", lens[0])
        self.assertIn("'Bad_Name' needs its question", lens[1])

    def test_the_one_owner_rule_reads_lenses_not_efforts_and_reports_every_conflict(self):
        # Completion review of D00 T01 §5: a bad effort hid an ownership conflict, and only the first conflict showed.
        hidden = self.found(THREE_PASS.replace('[schedule.plan]\neffort = "medium"', '[schedule.plan]\neffort = "bogus"')
                            .replace('lenses = ["plan-delivery", "record"]', 'lenses = ["plan", "record"]'))
        self.assertEqual(len(hidden), 2, hidden)
        self.assertIn("[schedule] plan needs effort", hidden[0])
        self.assertIn("the lens plan is listed in both plan and completion", hidden[1])
        two = self.found(THREE_PASS.replace('lenses = ["plan-delivery", "record"]', 'lenses = ["plan", "quality"]'))
        self.assertEqual(len(two), 2, two)
        self.assertIn("the lens plan is listed in both plan and completion", two[0])
        self.assertIn("the lens quality is listed in both round and completion", two[1])
        # Correcting either one leaves exactly the other.
        one = self.found(THREE_PASS.replace('lenses = ["plan-delivery", "record"]', 'lenses = ["record", "quality"]'))
        self.assertEqual(len(one), 1, one)
        self.assertIn("the lens quality", one[0])
        # load_pin still refuses with the first.
        self.assertEqual(self.first(THREE_PASS.replace('lenses = ["plan-delivery", "record"]',
                                                       'lenses = ["plan", "quality"]')), two[0])

    def test_a_check_that_rests_on_a_reported_part_is_skipped(self):
        # The round's lenses are at fault, so the one-owner rule and a conditional overlap that read them are not run.
        bad = THREE_PASS.replace('lenses = ["adversarial", "integration", "quality"]',
                                 'lenses = ["adversarial", "nope", "plan"]')
        found = self.found(bad)
        self.assertEqual(len(found), 1, found)
        self.assertIn("[schedule] round 1 needs lenses", found[0])
        # With sound steps the one-owner rule is reported, once.
        owner = self.found(THREE_PASS.replace('lenses = ["plan-delivery", "record"]', 'lenses = ["plan", "record"]'))
        self.assertEqual(len(owner), 1, owner)
        self.assertIn("the lens plan is listed in both plan and completion", owner[0])
        # A bad pass_cap is reported once; no_progress_cap is not blamed for a bound it cannot be held to.
        cap = self.found(THREE_PASS.replace("pass_cap = 45", "pass_cap = true"))
        self.assertEqual(len(cap), 1, cap)
        both = self.found(THREE_PASS.replace("pass_cap = 45", "pass_cap = true").replace(
            "no_progress_cap = 3", "no_progress_cap = 0"))
        self.assertEqual([m.split(" needs")[0] for m in both], ["[schedule] pass_cap", "[schedule] no_progress_cap"])
        # An unknown policy, or a wrong key set, is the schedule's one fault.
        policy = self.found(THREE_PASS.replace('policy = "three-pass"', 'policy = "two-pass"').replace(
            "pass_cap = 45", "pass_cap = 2"))
        self.assertEqual(len(policy), 1, policy)
        self.assertIn("policy must be", policy[0])
        keys = self.found(THREE_PASS.replace("pass_cap = 45", "pass_cpa = 2").replace(
            'lenses = ["plan"]', 'lenses = ["vibes"]'))
        self.assertEqual(len(keys), 1, keys)
        self.assertIn("(unknown: pass_cpa)", keys[0])

    def test_every_single_fault_the_loader_refuses_is_what_faults_reports(self):
        cases = (HEAD.replace("schema_version = 1", "schema_version = 2"),
                 HEAD.replace('model = "gpt-6-astra"', 'model = "bad model"'),
                 HEAD.replace('claude = ["astra"]', 'claude = []'),
                 HEAD.replace('claude = ["astra"]', 'claude = ["astra"]\ngemini = ["astra"]\nagy = ["astra"]'),
                 ROTATION.replace('lenses = ["consistency", "design", "record"]', "lenses = []"),
                 THREE_PASS + '\n[[schedule.rounds]]\neffort = "medium"\nlenses = ["optimization"]\n',
                 THREE_PASS.replace('lenses = ["design"]\npasses = ["plan", "round"]',
                                    'lenses = ["quality"]\npasses = ["plan"]'),
                 THREE_PASS.replace('cli = "codex"\nmodel = "gpt-6-astra"\neffort = "medium"',
                                    'cli = "agy"\nmodel = "gemini-4-argon-high"'))
        for text in cases:
            with self.subTest(text=text[-60:]):
                self.assertEqual(self.found(text), [self.first(text)])

    def test_a_pin_that_cannot_be_read_is_its_one_fault(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for label, make in (("missing", lambda p: None), ("a folder", lambda p: p.mkdir()),
                                ("not UTF-8", lambda p: p.write_bytes(b"schema_version = 1\n\xff\xfe")),
                                ("not TOML", lambda p: p.write_text("not toml [", encoding="utf-8"))):
                with self.subTest(label):
                    path = folder / (label.replace(" ", "-") + ".toml")
                    make(path)
                    with self.assertRaises(review_pin.Refused) as refused:
                        review_pin.load_pin(path)
                    self.assertEqual(review_pin.faults(path), [str(refused.exception)])


class CommandLine(unittest.TestCase):
    def run_cli(self, text, *args):
        with tempfile.TemporaryDirectory() as tmp:
            pin = Path(tmp) / "reviewers.toml"
            pin.write_text(text, encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPTS / "review_pin.py"), *args, "--pin", str(pin)],
                                  capture_output=True, text=True, encoding="utf-8", timeout=60)

    def test_check_says_ok_or_refuses_with_the_message(self):
        for text in (ROTATION, THREE_PASS, HEAD):
            done = self.run_cli(text, "--check")
            self.assertEqual((done.returncode, done.stdout), (0, "ok\n"), done.stderr)
        bad = self.run_cli(THREE_PASS.replace("pass_cap = 45", "pass_cap = 2"), "--check")
        self.assertEqual(bad.returncode, 2)
        self.assertIn("review-pin refused: [schedule] pass_cap needs", bad.stderr)
        self.assertEqual(bad.stdout, "")

    def test_check_all_lists_every_fault_and_only_goes_with_check(self):
        bad = THREE_PASS.replace("pass_cap = 45", "pass_cap = 2").replace(
            'blocking = ["P1", "P2"]', 'blocking = ["P2"]').replace(
            'lenses = ["adversarial", "plan-delivery", "record"]', 'lenses = ["adversarial", "vibes"]')
        done = self.run_cli(bad, "--check", "--all")
        self.assertEqual(done.returncode, 2)
        lines = done.stderr.splitlines()
        self.assertEqual(len(lines), 3, done.stderr)
        self.assertTrue(all(line.startswith("review-pin refused: [schedule] ") for line in lines), done.stderr)
        self.assertEqual(done.stdout, "")
        self.assertNotIn("Traceback", done.stderr)
        # The plain check still stops at the first, in the loader's own order.
        one = self.run_cli(bad, "--check")
        self.assertEqual((one.returncode, len(one.stderr.splitlines())), (2, 1))
        ok = self.run_cli(THREE_PASS, "--check", "--all")
        self.assertEqual((ok.returncode, ok.stdout, ok.stderr), (0, "ok\n", ""))
        unreadable = self.run_cli("not toml [", "--check", "--all")
        self.assertEqual(unreadable.returncode, 2)
        self.assertEqual(len(unreadable.stderr.splitlines()), 1)
        self.assertIn("review-pin refused: unreadable reviewer pin", unreadable.stderr)
        self.assertNotIn("Traceback", unreadable.stderr)
        alone = self.run_cli(THREE_PASS, "--caps", "--all")
        self.assertEqual(alone.returncode, 2)
        self.assertIn("--all goes with --check", alone.stderr)
        # A pin that cannot be read: one line, the same message --check gives, exit 2 and no traceback.
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "a-folder.toml").mkdir()
            (folder / "not-utf8.toml").write_bytes(b"schema_version = 1\n\xff\xfe")
            (folder / "not-toml.toml").write_text("not toml [", encoding="utf-8")
            for name, needle in (("missing.toml", "no reviewer pin at"), ("a-folder.toml", "unreadable reviewer pin"),
                                 ("not-utf8.toml", "not UTF-8 text"), ("not-toml.toml", "unreadable reviewer pin")):
                with self.subTest(pin=name):
                    runs = [subprocess.run([sys.executable, str(SCRIPTS / "review_pin.py"), "--check", *extra, "--pin",
                                            str(folder / name)], capture_output=True, text=True, encoding="utf-8",
                                           timeout=60) for extra in ((), ("--all",))]
                    for run in runs:
                        self.assertEqual(run.returncode, 2, run.stderr)
                        self.assertNotIn("Traceback", run.stderr)
                        self.assertEqual(run.stdout, "")
                        self.assertEqual(len(run.stderr.splitlines()), 1, run.stderr)
                        self.assertIn("review-pin refused: ", run.stderr)
                        self.assertIn(needle, run.stderr)
                    self.assertEqual(runs[0].stderr, runs[1].stderr)

    def test_lenses_prints_each_lens_with_its_question(self):
        table = review_pin.lens_table(tomllib.loads(THREE_PASS)["schedule"])
        done = self.run_cli(THREE_PASS, "--lenses", "round")
        self.assertEqual(done.stdout.splitlines(),
                         [f"{name}: {table[name]}" for name in ("adversarial", "integration", "quality")], done.stderr)
        with_paths = self.run_cli(THREE_PASS, "--lenses", "round", "--paths", "src/kernel/a.c", "README.md")
        self.assertEqual(with_paths.stdout.splitlines()[-1], f"concurrency: {table['concurrency']}")
        self.assertEqual(len(with_paths.stdout.splitlines()), 4)
        completion = self.run_cli(THREE_PASS, "--lenses", "completion")
        self.assertEqual([line.split(":")[0] for line in completion.stdout.splitlines()], ["plan-delivery", "record"])

    def test_caps_prints_the_configured_caps(self):
        self.assertEqual(self.run_cli(THREE_PASS, "--caps").stdout, "pass_cap 45\nno_progress_cap 3\n")
        self.assertEqual(self.run_cli(EARLIER_THREE_PASS, "--caps").stdout, "pass_cap 33\nno_progress_cap none\n")
        rotation = self.run_cli(ROTATION, "--caps")
        self.assertEqual(rotation.returncode, 2)
        self.assertIn("three-pass", rotation.stderr)


if __name__ == "__main__":
    unittest.main()
