# Completion review: D00 T03 §13

## Round 1: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T23:38:26Z
- Effort: xhigh
- Lines: 13
- Digest: dbe3475de9bca44a

1. **[P1] extend: Make resolved gaps a condition of stamping.** The planned check requires a returned independent review, but does not require a valid completion verdict or resolution of its findings. A `COMPLETE: no` review with unresolved gaps satisfies that description. Require either approval of the final section or an explicit disposition for every gap, including resolving XREFs for separately owned work. Add tests refusing unresolved findings, missing outcomes and contradictory verdicts.

2. **[P2] extend: Bind completion evidence to the section reviewed.** A readable `...-completion.md` file from another model family does not establish that it reviewed this section, its current contract, or even used the completion prompt. Another section’s report or a renamed code review could qualify. Record and verify the canonical section reference, reviewed contract snapshot, review purpose and pinned reviewer identity. Test wrong-section, wrong-purpose and stale evidence.

3. **[P2] extend: Own completion refusal and recovery states.** The section does not specify what happens when the initial dispatch fails, its reply is malformed, or the single permitted re-review still reports gaps. `process-phase` and `process-plan` also need a way to record that section as blocked, continue other work and resume without repeatedly consuming completion passes. Define these transitions before building, preserve outcomes across session death, and test them. D00 T03 §12 owns host readiness, which does not cover these review failures.

4. **[P2] extend: Migrate the retained review instructions completely.** The rewrite list omits writer routing instructions in the two review skills; their separately listed changes concern the cap and stamp example. [independent-review](/R:/GitHub/Office/.claude/skills/independent-review/SKILL.md:10) still advertises three writers and Astra, while [review-todo-section](/R:/GitHub/Office/.claude/skills/review-todo-section/SKILL.md:50) offers `claude|codex|gemini`. Those instructions would advertise routes the new parser rejects, and the proposed grep misses them. Explicitly replace these tables and commands with Claude and Sol, with a check covering retired writer names.

5. **[P2] extend: Define adoption for unfinished and reopened sections.** Preserving existing receipts leaves unfinished review loops unaddressed. The [paused campaign record](/R:/GitHub/Office/docs/phase-runs/2026-10-22-phase-2.md:17) directs D02 T01 §23 to stamp at round 22, but new stamps would use cap 33 and require completion evidence that predates building. Specify how such sections continue, how completion applies to remaining work, and when reopened sections need fresh evidence. Test migration and re-stamping while preserving historical records.

COMPLETE: no
HIGHEST: P1
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. extended
4. extended
5. extended

## Round 2: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T23:44:46Z
- Effort: xhigh
- Lines: 14
- Digest: 890159fa3a942819

SECTION: D00 T03 §13
PURPOSE: completion

1. **[P2] extend: Bind evidence to the reviewed contract version.** The planned checks establish section identity and review purpose, but never record the contract snapshot requested in round 1. An open section can change after approval and still stamp using that approval. Record a contract snapshot or digest, define how authorised extensions and filing dispositions update that binding, and test rejection of evidence for an earlier contract.

2. **[P2] extend: Distinguish a pending re-check from completed dispositions.** `## Outcome` exists before the mandatory re-check following an extension. If the session dies there, the reuse rule does not establish whether that re-check remains pending. Moreover, the stamp predicate accepts the first returned review plus `extended` dispositions, including after a subsequent outage. Persist the completion stage, associate outcomes with their round, and refuse stamping while the required re-check is pending. Test interruption before dispatch, after return, and before recording the final dispositions.

3. **[P2] extend: Own dispatcher refusal and recording-failure recovery.** Recovery specifies exit 1 and missing reply fields, but the dispatcher can exit 2 after returning a valid review whose record it refused to append (`scripts/review-dispatch.py:526`). That leaves no defined transition for the unattended campaign. Require successful recording and read-back before building, define parking and bounded recovery for refusal or damaged records, and test this path. D00 T03 §12 owns host readiness, which does not cover these failures.

4. **[P2] extend: Make reopening freshness precise within a day.** `Unstamped:` currently records only `YYYY-MM-DD`. Rejecting reviews before that date allows a morning review to qualify after an afternoon reopen, contrary to the promised fresh review. Record a UTC reopening instant or generation and bind completion evidence to the latest reopening. Test same-day reopening and repeated reopenings.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 2)

1. filed -> D00 T03 §14
2. filed -> D00 T03 §14
3. filed -> D00 T03 §14
4. filed -> D00 T03 §14
