# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The campaign skills keep their CI gate and campaign-ending parks (D00 T03 §19).

The gate lives in skill prose, so these checks pin each obligation to the words that carry it: an edit that drops or
weakens one fails here instead of letting the campaign build on a red main. `process-phase` runs `process-plan`'s one
procedure by reference, so it is checked for that reference and for its own closeout and resume steps.
"""
import hashlib
from pathlib import Path
import sys
import unittest

SKILLS = Path(__file__).resolve().parents[2] / ".claude" / "skills"
PLAN = SKILLS / "process-plan" / "SKILL.md"
PHASE = SKILLS / "process-phase" / "SKILL.md"

EXIT_BULLETS = {  # the four exit actions of the CI watch, pinned whole: any change to one is a deliberate test edit
    'green': "- 0 (green): run the dependency merge below first, while the tree is still clean and `HEAD` pushed. If it merged anything, `main` has a new head on GitHub, which the local `HEAD` may not have (`merged-then-failed`: the pull after the merge failed): run `git fetch origin main` and `git pull --ff-only origin main` so the clone matches the merged head (if it still cannot, park with `ci-unknown: cannot align with origin/main`, since no repair can start from a stale checkout), then `python scripts/ci-status.py HEAD --wait --timeout 1800` and act on it by these same rules (repair, wait, retry or park), all before any row is claimed. Then append `ci-pending <sha> <UTC>` and `ci-green <sha>` for each push checked, and the merge's outcome, to the run file; they ride with the next section's commit, so no bookkeeping push exists to go unchecked.",
    'red': '- 1 (red): repair it before the next row, as below.',
    'pending': '- 3 (pending): run `python scripts/ci-status.py <sha> --wait --timeout 1800` and act on that result.',
    'unknown': '- 2 (unknown: `gh` cannot be read, or no push run 10 minutes after the commit): retry once after five minutes; still 2, park the campaign with `ci-unknown` as the reason, since green cannot be established.',
}

# (obligation, skill, phrases that must all appear)
OBLIGATIONS = [
    ("boundary check", "plan", ["At the next section boundary, before the next row is claimed, run "
                                "`python scripts/ci-status.py <sha>`"]),
    ('exit 0 green', "plan", [EXIT_BULLETS['green']]),
    ('exit 1 red', "plan", [EXIT_BULLETS['red']]),
    ('exit 3 pending', "plan", [EXIT_BULLETS['pending']]),
    ('exit 2 unknown', "plan", [EXIT_BULLETS['unknown']]),
    ("three hard gates", "plan", ["Green is a hard gate in three places: a phase closeout (`process-phase` Step 4), a "
                                  "draft release, and the campaign's end (`plan-done`) each run "
                                  "`python scripts/ci-status.py HEAD --wait --timeout 3600`"]),
    ("reconciliation at start and resume", "plan", [
        "Reconcile from the pushed history (D00 T03 §17) at campaign start, at every phase start and on every manual "
        "or heartbeat resume", "`python scripts/ci-status.py --pending <run file>`"]),
    ("recovery budget", "plan", ["the budget is four attempts per recovery, any mix of kinds, a repair that turns "
                                 "another job red included",
                                 "When `reserve` refuses with `exhausted` (exit 1), file the failure through `add-todo`",
                                 "and park with `ci-red` as the reason, even when no useful code change exists.",
                                 "`python scripts/ci-recovery.py open <red sha>`",
                                 "`python scripts/ci-recovery.py reserve <kind>`",
                                 "`python scripts/ci-recovery.py close <green sha>`", "`exhausted`"]),
    ("heartbeat ends on every campaign park, either scope", "plan", [
        '"host-not-ready", "ci-red" or "ci-unknown", whatever the scope']),
    ("heartbeat matches the current run", "plan", ['column-0 "PARKED" line carrying "run=<run id>" and '
                                                   '"host-not-ready"']),
    ("heartbeat ends the run on a campaign park", "plan", [
        "the campaign is over until the owner resumes it by hand: run `<python> scripts/campaign_guard.py end "
        "--session $CLAUDE_CODE_SESSION_ID --reason park`, CronDelete this job, confirm, run cancel-confirmed for it, "
        "and reply RUN FINISHED, even when rows are ready and the host check would now pass."]),
    ("reconciliation settles the newest head first", "plan", [
        "1, settle from the newest head back: when `origin/main`'s head is already green (listed green, or recorded "
        "`ci-green`), each listed red head before it is recorded `ci-superseded <sha> by <that sha>` and never repaired; "
        "otherwise settle the newest listed head first and the earlier ones only after it:"]),
    ("earlier red heads are superseded only once the newest is green", "plan", [
        "only once the newest head is green is each earlier red head recorded `ci-superseded <sha> by <newest sha>` and "
        "never repaired"]),
    ("heartbeat resume reconciles before any row", "plan", [
        "Then run `<python> scripts/ci-status.py --pending <run file>` (it checks `origin/main` and every unchecked push "
        "head before it) and act on it as the skill's CI watch step says before claiming any row."]),
    ("hard gates proceed only on green", "plan", ["`python scripts/ci-status.py HEAD --wait --timeout 3600` and proceed "
                                                  "only on exit 0."]),
    ("no chaining after a CI park", "plan", ["Never chain to another phase after it."]),
    ("guard end on a CI park", "plan", ["commit it and push it",
                                        "run `python scripts/campaign_guard.py end --session $CLAUDE_CODE_SESSION_ID "
                                        "--reason park`, `CronDelete` the heartbeat, confirm with `CronList`"]),
    ("fresh-run resume", "plan", ["An owner resume is a fresh run",
                                  "Never `acquire --handover` onto a run parked for host readiness."]),
    ("phase runs the one CI procedure by reference", "phase", ["run `process-plan`'s CI watch (one procedure for both "
                                                               "skills, so they never diverge)"]),
    ("phase reconciles at start and resume", "phase", [
        "At this phase's start and on every manual or heartbeat resume, the one CI step is `process-plan`'s "
        "reconciliation, `python scripts/ci-status.py --pending <run file>`"]),
    ("heartbeat closeout ends only on green", "plan", ["and unless both exit 0 resume under step 7, whose CI watch "
                                                       "repairs or parks, instead of ending:"]),
    ("heartbeat plan-done ends only on green", "plan", ["unless both exit 0, do not end the run; resume under step 7, "
                                                        "where the skill's CI watch repairs or parks. On exit 0,"]),
    ("phase closeout gate", "phase", ["require green CI for that pushed closeout commit "
                                      "(`python scripts/ci-status.py HEAD --wait --timeout 3600` exits 0"]),
    ("phase names the three gates", "phase", ["Green CI is a hard gate in three places"]),
]

# Weakenings that keep a phrase's neighbourhood but break its meaning: each must make one obligation fail.
WEAKENINGS = [
    ("heartbeat ends on every campaign park, either scope", "plan",
     '"host-not-ready", "ci-red" or "ci-unknown", whatever the scope', '"host-not-ready" or "ci-unknown", whatever the scope'),
    ("heartbeat matches the current run", "plan", 'carrying "run=<run id>" and "host-not-ready"', 'and "host-not-ready"'),
    ("no chaining after a CI park", "plan", "Never chain to another phase after it.", "Chain to the next phase."),
    ("guard end on a CI park", "plan", "--reason park`, `CronDelete` the heartbeat, confirm with `CronList`",
     "--reason park`"),
    ("fresh-run resume", "plan", "An owner resume is a fresh run", "An owner resume continues the run by handover"),
    ("heartbeat ends the run on a campaign park", "plan",
     "the campaign is over until the owner resumes it by hand: run `<python> scripts/campaign_guard.py end --session "
     "$CLAUDE_CODE_SESSION_ID --reason park`, CronDelete this job, confirm, run cancel-confirmed for it, and reply RUN "
     "FINISHED, even when rows are ready and the host check would now pass.", "resume under step 7."),
    ("hard gates proceed only on green", "plan", "and proceed only on exit 0.", "and proceed on any exit."),
    ("exit 3 pending", "plan", "--wait --timeout 1800` and act on that result.", "--wait --timeout 1800` and claim the next row regardless of that result."),
    ("exit 2 unknown", "plan", "retry once after five minutes; still 2, ", ""),
    ("recovery budget", "plan", "the budget is four attempts per recovery", "the budget is unlimited per recovery"),
    ("reconciliation settles the newest head first", "plan", "settle the newest listed head first and the earlier ones "
     "only after it:", "settle the oldest listed head first:"),
    ("reconciliation settles the newest head first", "plan", "when `origin/main`'s head is already green (listed green, "
     "or recorded `ci-green`)", "when `origin/main`'s head is listed green"),
    ("earlier red heads are superseded only once the newest is green", "plan", "only once the newest head is green is "
     "each earlier red head recorded", "each earlier red head with any later green head is recorded"),
    ("heartbeat closeout ends only on green", "plan", "and unless both exit 0 resume under step 7, whose CI watch "
     "repairs or parks, instead of ending:", "and regardless of either exit:"),
    ("heartbeat plan-done ends only on green", "plan", "On exit 0, run `<python> scripts/campaign_guard.py end",
     "regardless of either exit, run `<python> scripts/campaign_guard.py end"),
    ("phase reconciles at start and resume", "phase", "At this phase's start and on every manual or heartbeat resume, "
     "the one CI step is", "Optionally, the one CI step is"),
    ("recovery budget", "plan", "and park with `ci-red` as the reason, even when no useful code change exists.",
     "and carry on."),
    ("heartbeat resume reconciles before any row", "plan",
     "Then run `<python> scripts/ci-status.py --pending <run file>` (it checks `origin/main` and every unchecked push "
     "head before it) and act on it as the skill's CI watch step says before claiming any row.", ""),
]


# Every paragraph that carries the CI gate or a terminal park, pinned whole by SHA-256 of its line (the line that
# starts with, or for a sentence inside a paragraph contains, the prefix). Any change fails until the pin is
# updated on purpose: `python scripts/tests/test_skill_ci_gate.py --print-pins` prints the current values.
PINNED = [
    ('plan', 'It runs at four entry points:',
     'bc32fd5225a75855cea6ac3eef77045318c0aac3ab76f2cbb0696bb9b94215d4'),
    ('plan', 'A resume after a host-not-ready park is a fresh run',
     'f09c7cbf1a5a6134dac5fc4624971a99f5403721306a92869d49aed3b53cc356'),
    ('plan', 'The campaign pushes to `main`, so it also reads',
     '36d26d7650a0dd6c99673e1ebc7a9d4a69bb3a91d0c010b8726ddf10d85766cb'),
    ('plan', '- 0 (green):',
     '247777df036eb233500291dc78866129b391d28670ccc57145e5beb7de155414'),
    ('plan', '- 1 (red):',
     '5f865d999153a2f005ce26e1ad87e9bbe4e8f4a38b7d2b4a0d5cfa17c558b8f4'),
    ('plan', '- 3 (pending):',
     '5bdff7409a3ab6d5f5de1646bdf8c5c1f277c3492565ef3c48d61046c521afcc'),
    ('plan', '- 2 (unknown',
     '160e3153fb8c7d774fe9d1ca750dcddc0a31515cac2d9098e51fca1cafff0df0'),
    ('plan', 'Repair a red run before the next row',
     '7f1ff312bf223a0e5a4a3d733ce89612ed953fb5c94cd691e882302bd0db2d22'),
    ('plan', 'Bound the repair:',
     '433a2fbcecd02a7dcc4a66e7138944459678464b427b482f8c1447bdbeefdc0f'),
    ('plan', 'A `ci-red` or `ci-unknown` park ends the whole campaign',
     'c456e052a7e314ab360c8f08bee13f1dc6a66e566a50d1319bc8b09873c46492'),
    ('plan', 'Every campaign push gets a `ci-pending',
     '70ee904f5ec22338104e4707535a7be043000b7cd11acca69ac58c198ef6cdf6'),
    ('plan', 'Reconcile from the pushed history',
     '53ac635cfa7d6acf54ff1bda6bf2db7006a7583280e4a0160eff4c19e62e963d'),
    ('plan', 'Green is a hard gate in three places',
     '95411b47eb82906b2f147ddba0955e900e15464ca2efc3996793ed01866648e8'),
    ('plan', 'Nothing is written to the run file at a boundary',
     '86ece21c2d0c913a1b1ae10e9b7a2fca9effa5f973981361dd7cae2b1e7c45b4'),
    ('plan', '5. If <run file> has a column-0',
     '22f8055f10a4f31316ec2f820c9840a77106dd5e7d1936ac1f988ea3d6b0de1f'),
    ('plan', 'Re-run `python scripts/todo-graph.py query ready`. If another phase has a ready row',
     '949d6bbdd5b8c206a645abd8547621f222db37114861c5bdf73e7be9d559e8ab'),
    ('plan', 'Then run the CI watch above for the stamp push; only on green',
     '9f697e7921277ce78948bfcce76f74ff28c32ee8c7645a2ae261d86c38c729c0'),
    ('plan', '7. Otherwise resume',
     '7f74d9f507109e6b89772a2e74b5d2116ff8158d06643fd9f85bff5a5c3c8afb'),
    ('phase', 'Then run the host readiness check',
     'd790d41adb7901713ca29916762cd12f4bfa1676c8eda5fd64b36f4ca1f5de42'),
    ('phase', "In the generated plan's table order, for each open row",
     '34791bf68ed53aeb9a494443276fd41b890d7279337c5d323b5eaf349d19e893'),
    ('phase', 'When the phase table is all `[x]`',
     'ee4ddf73abbee2baf437dc1a02107c2963465fc845ebfe5db233ebaca378b959'),
]


def pinned_line(text, prefix):
    """The first line that starts with the prefix, else the first that contains it (a sentence inside a paragraph)."""
    lines = text.split("\n")
    return next((line for line in lines if line.startswith(prefix)),
                next((line for line in lines if prefix in line), None))


def pin_failures(texts):
    """The pinned paragraphs that are missing or changed."""
    failures = []
    for skill, prefix, digest in PINNED:
        line = pinned_line(texts[skill], prefix)
        if line is None or hashlib.sha256(line.encode("utf-8")).hexdigest() != digest:
            failures.append(prefix)
    return failures


def missing(texts):
    """The obligations whose phrases are not all present in the given {'plan': ..., 'phase': ...} texts."""
    return [name for name, skill, phrases in OBLIGATIONS if not all(p in texts[skill] for p in phrases)]


class SkillCiGate(unittest.TestCase):
    def setUp(self):
        self.texts = {"plan": PLAN.read_text(encoding="utf-8"), "phase": PHASE.read_text(encoding="utf-8")}

    def test_every_obligation_is_present(self):
        self.assertEqual(missing(self.texts), [])

    def test_removing_any_obligation_fails(self):
        for name, skill, phrases in OBLIGATIONS:
            for phrase in phrases:
                with self.subTest(name=name, phrase=phrase[:50]):
                    copy = dict(self.texts)
                    copy[skill] = copy[skill].replace(phrase, "")
                    self.assertIn(name, missing(copy))

    def test_weakening_a_terminal_park_obligation_fails(self):
        for name, skill, old, new in WEAKENINGS:
            with self.subTest(name=name):
                self.assertIn(old, self.texts[skill], "the weakening no longer matches the skill text")
                copy = dict(self.texts)
                copy[skill] = copy[skill].replace(old, new)
                self.assertIn(name, missing(copy))


    def test_every_pinned_paragraph_is_unchanged(self):
        self.assertEqual(pin_failures(self.texts), [])

    def test_changing_or_removing_a_pinned_paragraph_fails(self):
        for skill, prefix, _ in PINNED:
            line = pinned_line(self.texts[skill], prefix)
            for changed in (line.replace(" ", "  ", 1), ""):  # one word moved, or the paragraph gone
                with self.subTest(prefix=prefix, removed=not changed):
                    copy = dict(self.texts)
                    copy[skill] = copy[skill].replace(line, changed)
                    self.assertIn(prefix, pin_failures(copy))


if __name__ == "__main__":
    if sys.argv[1:] == ["--print-pins"]:
        texts = {"plan": PLAN.read_text(encoding="utf-8"), "phase": PHASE.read_text(encoding="utf-8")}
        for skill, prefix, _ in PINNED:
            line = pinned_line(texts[skill], prefix)
            print(skill, prefix, hashlib.sha256(line.encode("utf-8")).hexdigest() if line else "MISSING")
    else:
        unittest.main()
