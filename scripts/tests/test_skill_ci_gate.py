# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The campaign skills keep their CI gate and campaign-ending parks (D00 T03 §19).

The gate lives in skill prose, so these checks pin each obligation to the words that carry it: an edit that drops or
weakens one fails here instead of letting the campaign build on a red main. `process-phase` runs `process-plan`'s one
procedure by reference, so it is checked for that reference and for its own closeout and resume steps.
"""
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
