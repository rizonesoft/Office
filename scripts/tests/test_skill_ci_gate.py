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
SECTION = SKILLS / "process-todo-section" / "SKILL.md"
REVIEW = SKILLS / "review-todo-section" / "SKILL.md"

EXIT_BULLETS = {  # the four exit actions of the CI watch, pinned whole: any change to one is a deliberate test edit
    'green': "- 0 (green): run the dependency merge below first, while the tree is still clean and `HEAD` pushed. If it merged anything, `main` has a new head on GitHub, which the local `HEAD` may not have (`merged-then-failed`: the pull after the merge failed): run `git fetch origin main` and `git pull --ff-only origin main` so the clone matches the merged head (if it still cannot, park with `ci-unknown: cannot align with origin/main`, since no repair can start from a stale checkout), then `python scripts/ci-status.py HEAD --wait --timeout 1800` and act on it by these same rules (repair, wait, retry or park), all before any row is claimed. Then append `ci-pending <sha> <UTC>` and `ci-green <sha>` for each push checked, and the merge's outcome, to the run file; they ride with the next section's commit, so no bookkeeping push exists to go unchecked.",
    'red': '- 1 (red): repair it before the next row, as below.',
    'pending': '- 3 (pending): watch it, do not wait for it. Every push is watched from the moment it is made: start `python scripts/ci-status.py <sha> --wait --timeout 1800` in the background right after the push, then claim the next row and build. Its result arrives as a notification while the build goes on. Green: record it at the next boundary. Red: finish the edit in hand, commit nothing further of the section, and repair the red head at once as below, before any other push; the section carries on after the repair is green. The head is waited for in the foreground only when it is still pending 45 minutes after its push or when a later stamp is ready to be pushed on top of it. No dependency merge runs and no `ci-green` is recorded for a head that is not green yet (owner, 2026-11-12, decision 45: the run builds while CI tests, and a red CI is detected early and fixed).',
    'unknown': '- 2 (unknown: `gh` cannot be read, or no push run 10 minutes after the commit): retry once after five minutes; still 2, park the campaign with `ci-unknown` as the reason, since green cannot be established.',
}

# (obligation, skill, phrases that must all appear)
OBLIGATIONS = [
    # D00 T05 §8: a phase closes only once the lesson store is within its upkeep.
    ("lesson upkeep before the closeout", "phase", [
        "**Lesson upkeep comes first.** At a phase's closeout, before the closeout is written, run "
        "`python scripts/lessons.py report --check`",
        "For each group it names over the ceiling, and for each lesson it lists as mergeable or as still failing, "
        "apply one of the four remedies until the check exits 0",
        "merge lessons about one thing into one (`python scripts/lessons.py reassign <id> --to lesson:<other> "
        "--delete` moves the triage lines; an `apart` key records two that teach different things)",
        "retire a lesson with `retired_by` once a check or test enforces it",
        "rewrite one that did not stop its fault and give it a `revised` date",
        "delete one that taught nothing (`reassign <id> --to one-off <reason> --delete`)",
        "A listed lesson is never left as it is",
        "Commit the upkeep in a commit of its own, before the closeout commit"]),
    # D00 T05 §4: a section reads its lessons before it builds, and its review writes them before the last pass.
    ("lessons are read before the build", "section", [
        "**Read the lessons first.** Before building, run `python scripts/lessons.py query --role main --path <path>`",
        "with one `--path` for each path the section names",
        "read every lesson it prints"]),
    ("each outcome of the read is handled", "section", [
        "exit 0 with lessons, they are read and the build follows them",
        "exit 0 with none, no lesson applies, which one line records under a `## Writer note:` heading in the "
        "section's findings file, beside the plan review (step 3a)",
        "exit 1, the store breaks a rule or the index cannot be written, and a failed query has read nothing: run "
        "`python scripts/lessons.py check`, fix what it names, and run the query again until it exits 0",
        "exit 2, the command is wrong"]),
    ("the round's findings are triaged", "review", [
        "**Triage the round's findings before the completion review.**",
        "give every finding of the plan review and of the round that was confirmed and fixed one line in the "
        "record's triage file, `docs/lessons/triage/<path>.md` for `docs/reviews/<path>.md`",
        "`<pass> finding K: <disposition> [reason]` (the pass written `plan` or `round N`)",
        "`lesson:<id>` (the kind can recur and no check stops it)",
        "`enforced:<path>` (a check or test in the repository now stops it)",
        "`one-off` with a reason",
        "Write the lesson file for each new `lesson:<id>`"]),
    ("triage lands in the reviewed candidate", "review", [
        "before the completion review is dispatched",
        "Run `python scripts/lessons.py check` until it exits 0 and commit the lines and the lessons, so they are in "
        "the candidate the completion review reads",
        "A completion review's gaps, and the new findings of a reconciliation, are triaged the same way "
        "(`completion finding K`, `reconciliation N finding K`) once they are fixed and before the next "
        "reconciliation is dispatched"]),
    ("an enforceable lesson is retired", "review", [
        "A lesson this section's own work made enforceable (it added the check or the test) is retired in the same "
        "commit: `status: retired` with `retired_by` naming it"]),
    ("a resume writes no second line", "review", [
        "On a resumed section run `python scripts/lessons.py candidates --untriaged --p3 <the record>` (`--p3` "
        "because a fixed `P3` finding is triaged too) and write only what it prints: a finding never gets a second "
        "line"]),
    ("the passes covered are named", "review", [
        "All four kinds of pass are covered: the plan review, the round, the completion review and each "
        "reconciliation (D00 T05 §9)"]),
    ("parks record a notice, never an email", "plan", [  # D00 T03 §53: decision 32, one weekly email only
        "Nothing emails at once: decision 32 allows one weekly email, the owner digest, and no other interruption",
        "recorded them as a notice for the weekly owner digest through `.conclave/automations/alert.py`",
        "record a notice for the weekly owner digest with `python .conclave/automations/alert.py --notice"]),
    ("measure again when due", "plan", [  # D00 T03 §37: both triggers, the command that tells them, and the cycle
        "run `python scripts/measure-modes.py due --model <the full model id this session runs on>`",
        "when 300 sections were stamped since the stored verdict was decided",
        "or when this session's model differs from the one the verdict was measured on",
        "`python scripts/measure-modes.py decide --results <that folder>/results.json`",
        "a refused `decide` keeps the stored verdict"]),
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
    ("a green reconciliation settles the recovery before the merge or any row", "plan", [
        "Whenever it establishes `origin/main`'s head as green (exit 0; exit 1 whose newest head is green and whose "
        "earlier red heads are superseded; or a pending newest head that turns green after the wait), run "
        "`python scripts/ci-recovery.py settle <origin/main sha>` next, before the dependency merge and before any row"]),
    ("the phase settles the recovery before any row", "phase", [
        "once it establishes `origin/main`'s head as green, run `python scripts/ci-recovery.py settle <origin/main sha>` "
        "before any row, as `process-plan` says"]),
    ("a progressing reconciliation is continued before any row", "plan", [
        "Exit 4 means the try ran out of time but saved its progress in `build/ci-reconcile.json` (D00 T03 §22): run it "
        "again at once, before any row, as often as it returns 4, without spending the one retry for exit 2 or the "
        "recovery budget"]),
    ("confirmed heads are recorded before the rerun", "plan", [
        "Before each rerun, record `ci-green` for every head on a `confirmed green` line it printed"]),
    ("the checkpoint is dropped only after the records", "plan", [
        "Once the records it led to (`ci-green`, `ci-superseded`) are written, run "
        "`python scripts/ci-status.py --pending <run file> --ack` to drop the checkpoint."]),
    ("the phase continues a progressing reconciliation", "phase", [
        "an exit 4 (progress saved) is run again at once, before any row, and `--ack` drops the checkpoint after the "
        "records are written"]),
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
    ("exit 3 pending", "plan", "repair the red head at once as below, before any other push", "note the red head and carry on"),
    ("exit 2 unknown", "plan", "retry once after five minutes; still 2, ", ""),
    ("recovery budget", "plan", "the budget is four attempts per recovery", "the budget is unlimited per recovery"),
    ("a progressing reconciliation is continued before any row", "plan", "run it again at once, before any row, as "
     "often as it returns 4,", "treat it as exit 2,"),
    ("confirmed heads are recorded before the rerun", "plan", "Before each rerun, record `ci-green` for every head "
     "on a `confirmed green` line it printed", "Before each rerun, ignore every `confirmed green` line it printed"),
    ("the checkpoint is dropped only after the records", "plan", "Once the records it led to (`ci-green`, "
     "`ci-superseded`) are written, run", "Before the records are written, run"),
    ("the phase continues a progressing reconciliation", "phase", "an exit 4 (progress saved) is run again at once, "
     "before any row,", "an exit 4 (progress saved) parks the campaign,"),
    ("a green reconciliation settles the recovery before the merge or any row", "plan",
     "`python scripts/ci-recovery.py settle <origin/main sha>` next, before the dependency merge and before any row",
     "`python scripts/ci-recovery.py settle <origin/main sha>` after the dependency merge"),
    ("a green reconciliation settles the recovery before the merge or any row", "plan",
     "(exit 0; exit 1 whose newest head is green and whose earlier red heads are superseded; or a pending newest head "
     "that turns green after the wait)", "(exit 0)"),
    ("the phase settles the recovery before any row", "phase",
     "run `python scripts/ci-recovery.py settle <origin/main sha>` before any row", "claim the next row"),
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
     '661f597647fdef41de768f08f065dd7b8aa40811807248f8ea7e0e44976fa120'),
    ('plan', 'A resume after a host-not-ready park is a fresh run',
     'f09c7cbf1a5a6134dac5fc4624971a99f5403721306a92869d49aed3b53cc356'),
    ('plan', 'The campaign pushes to `main`, so it also reads',
     '36d26d7650a0dd6c99673e1ebc7a9d4a69bb3a91d0c010b8726ddf10d85766cb'),
    ('plan', '- 0 (green):',
     '247777df036eb233500291dc78866129b391d28670ccc57145e5beb7de155414'),
    ('plan', '- 1 (red):',
     '5f865d999153a2f005ce26e1ad87e9bbe4e8f4a38b7d2b4a0d5cfa17c558b8f4'),
    ('plan', '- 3 (pending):',
     '55b30efbd20c62183750fcb19aac583563cabaf99ccdb21538c9e090dd194502'),
    ('plan', '- 2 (unknown',
     '160e3153fb8c7d774fe9d1ca750dcddc0a31515cac2d9098e51fca1cafff0df0'),
    ('plan', 'Repair a red run before the next row',
     '9f0495da0f431ca61a5a4d830f6119212972d736e2daa194a6afd7e8f5bc5a9d'),
    ('plan', 'Bound the repair:',
     '8a8ee9705a7b045b206fdf521b615d1bf1172de97aed036a7d19def2044445dd'),
    ('plan', 'A `ci-red` or `ci-unknown` park ends the whole campaign',
     'c456e052a7e314ab360c8f08bee13f1dc6a66e566a50d1319bc8b09873c46492'),
    ('plan', 'Every campaign push gets a `ci-pending',
     '70ee904f5ec22338104e4707535a7be043000b7cd11acca69ac58c198ef6cdf6'),
    ('plan', 'Reconcile from the pushed history',
     '4e767c7eb7416f6b9add9094cd9dd482291b1a8f1bec3b620a99071706fc293b'),
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
     '5765665acd622c6fef2f08894bbf735949f14ddc53fc596bbfd1d2f78b70b5bb'),
    ('phase', 'When every row of the phase table is `[x]`:',
     '0bdbdf1b91d4d42374916f1e2917dd410c943bf744022f7f3f4e080e2413bb2b'),
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
        self.texts = {"plan": PLAN.read_text(encoding="utf-8"), "phase": PHASE.read_text(encoding="utf-8"),
                 "section": SECTION.read_text(encoding="utf-8"), "review": REVIEW.read_text(encoding="utf-8")}

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


    LESSON_STEPS = {  # obligation -> (skill, the heading or item it follows, the one it precedes)
        "lesson upkeep before the closeout": ("phase", "## Step 4: closeout",
                                              "When every row of the phase table is `[x]`: `process-todo-file`"),
        "lessons are read before the build": ("section", "### 2. Validate the plan before building it",
                                              "### 4. Build the corrected contract"),
        "each outcome of the read is handled": ("section", "### 2. Validate the plan before building it",
                                                "### 4. Build the corrected contract"),
        "the round's findings are triaged": ("review", "2. **The round**", "3. **The completion review** of the final"),
        "triage lands in the reviewed candidate": ("review", "2. **The round**",
                                                   "3. **The completion review** of the final"),
        "an enforceable lesson is retired": ("review", "2. **The round**", "3. **The completion review** of the final"),
        "a resume writes no second line": ("review", "2. **The round**", "3. **The completion review** of the final"),
    }

    @classmethod
    def misplaced(cls, texts):
        """Every (obligation, phrase) of the lesson steps that does not sit between its two markers."""
        found = []
        for name, skill, phrases in OBLIGATIONS:
            if name not in cls.LESSON_STEPS:
                continue
            _, after, before = cls.LESSON_STEPS[name]
            text = texts[skill]
            for phrase in phrases:
                if not text.index(after) < text.index(phrase) < text.index(before):
                    found.append((name, phrase[:50]))
        return found

    def test_the_lesson_steps_sit_where_they_take_effect(self):
        # D00 T05 §4: the read comes before the build, and every sentence of the triage step between the round and
        # the completion review, so all of it is in the candidate the last pass reads.
        self.assertEqual(self.misplaced(self.texts), [])
        review = self.texts["review"]
        marker = "   **Triage the round's findings before the completion review.**"
        start = review.index(marker)
        paragraph = review[start:review.index("\n", start)]
        # The whole step moved after the completion review: every sentence is then misplaced, heading or no heading.
        rest = review.replace(paragraph + "\n", "", 1)
        moved = dict(self.texts, review=rest + "\n" + paragraph + "\n")
        self.assertEqual({name for name, _ in self.misplaced(moved)},
                         {name for name, (skill, _, _) in self.LESSON_STEPS.items() if skill == "review"})
        # Only its instructions moved, the heading words left in place: still caught.
        body = paragraph[len(marker):]
        kept = dict(self.texts, review=review.replace(paragraph, marker, 1) + "\n" + body + "\n")
        self.assertTrue(self.misplaced(kept))
    def test_the_readme_states_the_ceiling_and_the_four_remedies(self):
        # D00 T05 §8: the README's Upkeep section, by its words, and the ceiling it names is the code's.
        readme = (SKILLS.parents[1] / "docs" / "lessons" / "README.md").read_text(encoding="utf-8")
        upkeep = readme.split("## Upkeep\n", 1)[1].split("\n## ", 1)[0]
        sys.path.insert(0, str(SKILLS.parents[1] / "scripts" / "lib"))
        import lessons
        for phrase in (f"an area holds at most {lessons.LESSON_CEILING} active lessons",
                       f"texts that share at least {round(lessons.MERGE_SIMILARITY * 100)} percent of their words",
                       "run on a later day than the later of its `added` and `revised` dates",
                       "merge lessons about one thing into one", "retire a lesson a check or test now enforces",
                       "rewrite one that did not stop its fault and set `revised`", "delete one that taught nothing",
                       "A listed lesson is never left as it is"):
            self.assertIn(phrase, upkeep)

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
        texts = {"plan": PLAN.read_text(encoding="utf-8"), "phase": PHASE.read_text(encoding="utf-8"),
                 "section": SECTION.read_text(encoding="utf-8"), "review": REVIEW.read_text(encoding="utf-8")}
        for skill, prefix, _ in PINNED:
            line = pinned_line(texts[skill], prefix)
            print(skill, prefix, hashlib.sha256(line.encode("utf-8")).hexdigest() if line else "MISSING")
    else:
        unittest.main()
