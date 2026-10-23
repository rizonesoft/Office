# Completion review: D00 T03 §15

## Round 1: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T10:11:18Z
- Effort: medium
- Lines: 23
- Digest: 5e942c198c21922c

SECTION: D00 T03 §15
PURPOSE: completion
CONTRACT: sha256:d6546fd8f5be3a2331b6b5ae915d0291e9ce5ccbfcce4c129fecfac221edc4c1

1. **[P1] Boundary handling for nonterminal and unreadable results is missing.** The boundary command runs without `--wait`, but only green and red have prescribed actions. A queued run, missing run or lost GitHub access therefore has no rule preventing the next row from being claimed. **Remedy: extend** with an explicit action for every exit code: bounded waiting for pending results, bounded recovery for unreadable results, and a campaign park when green cannot be established.

2. **[P2] Independently started phases lack boundary monitoring and repair.** The boundary records, repair procedure and repair bound are assigned to `process-plan`; `process-phase` receives only the closeout gates. A phase started directly can ship several sections before checking CI. **Remedy: extend** both skills to invoke the same boundary procedure before claiming another row, including after manual and heartbeat resumes.

3. **[P2] Pending-check recovery and coverage of other pushes are unowned.** Recording only stamp pushes does not cover dependency merges, other campaign pushes, or a session dying after a successful push but before `ci-pending` is appended. Reading unresolved notes from the latest phase run does not reconstruct an absent record or define cross-phase reconciliation. **Remedy: extend** with startup and resume reconciliation against pushed history, durable pending records for every relevant new main commit, and explicit ordering around §9 dependency merges and closeout pushes.

4. **[P2] Run identity and terminal outcomes are underspecified.** The workflow runs on pushes, pull requests and manual dispatches, while lookup selects only by commit. The plan does not define which matching run or rerun attempt governs the gate, how `HEAD` resolves to a full commit SHA, or what happens for cancelled, skipped and other nonsuccess conclusions. **Remedy: extend** with an authoritative push-run selection rule, explicit ref resolution, current-attempt handling, and classification of every terminal outcome. Fixtures must cover competing runs and reruns.

5. **[P1] A `ci-red` park does not override the existing continuation paths.** Today, `process-plan` chains after phase parks, and its heartbeat treats only `host-not-ready` as a campaign-wide park. Merely naming `ci-red` leaves instructions that can restart work on red main. **Remedy: extend** the chaining and heartbeat rules to honour this park, write the required run marker, end the guard, cancel and confirm the heartbeat, and require CI reconciliation before an owner resume claims work. Notification failure must be recorded without preventing the park.

6. **[P2] The repair bound misses ordinary failures that produce no repair commit.** Three commits leaving the same job red does not bound an infrastructure outage, an unavailable diagnostic log, an unsuccessful rerun, or repairs that alternate failing jobs. **Remedy: extend** with an overall bounded recovery budget, persist its consumption across resumes, define the single flake-rerun attempt, and escalate unresolved failures even when no useful code change exists.

7. **[P2] The wait timeout does not bound GitHub subprocesses.** Polling for 3,600 seconds does not itself prevent one `gh` invocation from hanging indefinitely. The no-run grace period also has no duration or defined starting point. **Remedy: extend** with subprocess deadlines capped by the remaining wait budget, a defined grace period, and fixtures for hung probes, delayed run creation and diagnostic-read failures.

8. **[P2] The checkpoint cannot prove the campaign integration works.** Script fixtures and requirements that skills merely “name” steps can pass while standalone phases bypass checks, resumes lose pending work, or heartbeats continue after a park. **Remedy: extend** with falsifiable integration checks covering claim blocking, repair and rerun outcomes, persisted recovery, campaign-wide parking, and all three hard gates against the intended pushed SHA.

COMPLETE: no
HIGHEST: P1
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. filed -> D00 T03 §17
4. extended
5. extended
6. filed -> D00 T03 §18
7. extended
8. filed -> D00 T03 §19

## Round 2: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T10:14:25Z
- Effort: medium
- Lines: 9
- Digest: 9be1fac07ca2b1f4

SECTION: D00 T03 §15
PURPOSE: completion
CONTRACT: sha256:39852ab618fafffcc60929d9f4b01e04e8fcd552087428da9ae960cd86eb3b1b

1. **P2 | extend: distinguish push heads from intermediate commits.** §17 owns reconciliation, but its requirement to check every commit conflicts with §15’s requirement for an exact-SHA push run. The existing workflow permits multiple implementation commits followed by a stamp commit in one push. GitHub’s push workflow runs against that push’s tip, so intermediate commits normally have no matching run. [GitHub documents this behaviour](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#push). On resume, §17 would submit those intermediate SHAs to §15, which would eventually park a healthy campaign as `ci-unknown`. Align §15 and §17 around actual push heads, preserve their identity across interrupted sessions, and distinguish commits included in a push from commits independently checked green. Add a fixture with two implementation commits and a stamp pushed together: reconciliation must check the stamp’s run without demanding nonexistent runs for its intermediate commits.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 2)

1. filed -> D00 T03 §17
