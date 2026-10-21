## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-10-21T18:03:56Z
- Effort: medium
- Lines: 24
- Digest: fa7f8e0bf72e3bd8

## adversarial: needs-attention

1. **P1** `scripts/lib/todo_graph.py:237`: Removing `rounds_spent` bypasses all returned-review, verdict-matching, severity and outcome checks. The legacy branch even accepts `stopped-low-severity`, which never existed in legacy receipts. Reproduce with round 9, that verdict, a nonempty report containing “No reviewer ran”, and no `rounds_spent`, `round_cap` or `cap_outcome`. An in-memory call to `receipt_data_ok` accepted this.

2. **P1** `scripts/lib/todo_graph.py:286`: The 22-round limit is checked only for `stopped-at-*` verdicts. A loop with 23 returned reviews ending in approval validates as `clean` with `round_cap: 22`. Reproduced through the actual receipt validator with an in-memory findings file. Enforce the maximum returned-review count independently of the selected verdict.

3. **P1** `scripts/hooks/pre-commit:8`: The hook checks staged consistency only under `todo/`, although validation also reads receipts and findings under `docs/reviews/`. Reproduce by stamping a section, staging its TODO file and regenerated plan, and leaving the new receipt and findings untracked. The hook reads those local files and passes; the committed tree lacks required evidence and fails validation in a clean checkout.

## consistency: needs-attention

4. **P2** `todo/02-interface/TODO-01-parity-inventory.md:596`: Every backticked inventory ID is treated as ownership, including documentation and test examples. Section 22 itself cites both `word.home.font.bold` and deliberately nonexistent `word.home.font.nosuch`; section 18 also cites the former. Implementing these instructions literally creates unknown-ID and duplicate-owner failures before application sections claim their records. Distinguish explicit implementation ownership from examples, capture work and test references, and add refusal/acceptance fixtures for that distinction.

5. **P3** `.codex/skills/groom-plan/SKILL.md:29`: Grooming now leaves implemented items unchecked, but `todo/README.md:94` still explicitly instructs grooming to tick them. The same conflict affects the other mirrors. Reproduce by following both documents for an already implemented open item: they prescribe opposite checkbox states.

## integration: needs-attention

6. **P1** `scripts/hooks/pre-commit:1`: The inline diff adds the hook with mode `100644`. On a fresh Linux or WSL checkout, Git ignores this non-executable hook even after configuring `core.hooksPath`. Reproduce by cloning there, enabling the hook path, and committing a stale TODO plan. Track the hook as executable. The test fixture also uses `shutil.copyfile` at `scripts/tests/test_pre_commit_hook.py:23`, which does not establish executable permissions, so it needs corresponding handling.

## record: advisory

The claimed 430-test run and Task Scheduler removal were not independently reproduced. Verification here used file inspection and read-only, in-memory validator probes; no files were changed and no git commands ran.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after round 1

Candidate `0e11949..68b0b7a`. All six findings verified against the code and fixed in the next commit:

1. P1 legacy receipt bypass: fixed. `receipt_data_ok` now refuses a receipt without `rounds_spent` unless every round is 1 to 3 with a verdict from the old process (`clean`, `fixed`, `stopped-at-3`) and it carries no `round_cap` or `cap_outcome`; `stamp`'s argument pass is marked `building=True`. Test: `test_a_receipt_without_rounds_spent_holds_only_what_the_old_process_wrote`.
2. P1 no cap on clean loops: fixed. Every findings file may hold at most `round_cap` returned reviews, and `round_cap` must be 22 or an earlier cap (8, 13). Tests: `test_a_loop_past_the_cap_refuses_even_when_it_ends_clean`, `test_a_receipt_names_a_cap_the_process_has_used`.
3. P1 hook ignores `docs/reviews/`: fixed. The hook refuses unstaged or untracked files in `todo/` and `docs/reviews/` and runs `validate` before `plan --check`. Test: `test_an_untracked_review_file_beside_a_todo_change_is_refused` (fails on the old hook).
4. P2 every backticked id claims ownership: fixed in the plan. D02 T01 §22 now counts only ids on a section's `> **Implements:**` lines, documents that line in `todo/README.md`, and tests an example-only fixture; D02 T01 §18 and D03 T01 §13 use the same line.
5. P3 README contradicts groom-plan: fixed. `todo/README.md` now says groom-plan appends `Already shipped:` and leaves the item open.
6. P1 hook not executable: fixed. Tracked as `100755`; the hook test copies it with mode 755 and `test_the_hook_is_tracked_as_executable` checks the index.

Gates: `python -m unittest discover -s scripts/tests` -> 435 tests OK (2 skipped); `python scripts/todo-graph.py validate` -> `valid: 83 sections`; `plan --check` -> `plan current`.

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-10-21T18:13:49Z
- Effort: medium
- Lines: 18
- Digest: e342bdf8b7d54831

## adversarial: needs-attention

1. **P1** `scripts/lib/todo_graph.py:242`: The legacy bypass remains for rounds 1 to 3. Reproduce with a round-1 `clean` receipt dated `2026-10-21`, a report containing only `No reviewer ran`, and no `rounds_spent` or `round_cap`. `receipt_data_ok(..., root=...)` accepts it. Adding those fields correctly causes refusal. Confirmed with an in-memory probe. The new shape restriction does not establish that a receipt is genuinely historical, so round 1 finding 1 is only partially fixed.

2. **P1** `scripts/lib/todo_graph.py:269`: Duplicate round numbers overwrite earlier reviews before the cap and final-verdict checks. Reproduce with 23 dispatcher-format envelopes numbered `1`, the first 22 returning `needs-attention` and the last returning `approve`. A receipt claiming round 1 as `clean`, with `rounds_spent: 1` and `round_cap: 22`, passes. Confirmed in memory: the dispatcher reader returns 23 records, but the validator collapses them to one. Reject duplicate round numbers before constructing the dictionary.

## consistency: approve

## integration: needs-attention

3. **P1** `scripts/hooks/pre-commit:10`: `--exclude-standard` hides ignored evidence files from the check, although validation still reads them. Reproduce by excluding a new receipt and findings file through `.git/info/exclude`, leaving them untracked, and staging the stamped TODO plus synchronized plan. Neither the tracked diff check nor the untracked check detects the missing evidence; validation reads the local files and the hook can pass. The resulting commit fails validation in a clean checkout. Verify that every referenced evidence file exists in the index and matches the working copy. This is a static finding; git was not run.

## record: advisory

The dispositions overstate completion of findings 1 and 3: both retain bypasses described above. The claimed 435-test run was not independently reproduced. Verification here used file inspection and in-memory probes without modifying files or running git.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after round 2

Candidate `0e11949..b33a390`. All three findings verified and fixed in the next commit:

1. P1 legacy bypass by shape: fixed. A receipt without `rounds_spent` must also match, by content digest (`receipt_digest`, key order and line endings ignored), one of the 14 receipts frozen in `docs/reviews/legacy-receipts.json`, generated from the receipts on disk at `b33a390`. Test: `test_a_receipt_without_rounds_spent_holds_only_what_the_old_process_wrote` now refuses the old shape unless frozen, and refuses a frozen receipt once edited.
2. P1 repeated round numbers: fixed. A findings file must number its rounds 1 to N in order, once each. Test: `test_a_repeated_round_number_refuses`.
3. P1 ignored evidence files: fixed. The hook lists untracked files without `--exclude-standard`, so ignored files under `todo/` or `docs/reviews/` refuse the commit too. Test: `test_an_ignored_review_file_beside_a_todo_change_is_refused` (fails on the previous hook).

Gates: `python -m unittest discover -s scripts/tests` -> 437 tests OK (2 skipped); `validate` -> `valid: 83 sections`; `plan --check` -> `plan current`.

## Round 3: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-10-21T18:21:56Z
- Effort: medium
- Lines: 18
- Digest: 68afcba3370d8494

## adversarial: needs-attention

1. **P1** `scripts/lib/todo_graph.py:340`: A later failed review attempt does not invalidate an earlier approval. Reproduce with sequential dispatcher envelopes: round 1 approves, round 2 records `none` with `OVERALL: blocked`; submit round 1 as `clean`, with `rounds_spent: 2`. The validator accepts it because it checks the last **returned review**, excluding the later outage. Confirmed in memory. This permits stamping after the latest review failed, contrary to the skill’s requirement to stop without a stamp.

## consistency: needs-attention

2. **P3** `docs/todo-workflow.md:11` and `todo/README.md:56`: Both prescribe table rows under 140 characters, conflicting with Office’s 100-character rule and retained plan-table refusal. Reproduce by following that guidance with a 120-character row: it satisfies these documents but violates `AGENTS.md`. Align the documented limit.

## integration: approve

## record: needs-attention

3. **P2** `scripts/lib/todo_graph.py:276`: `rounds_spent` is not checked against the findings files. Reproduce with one valid round-1 approval and `rounds_spent: 999`; validation accepts it, and `query rounds` uses that false count in its totals and mean. Confirmed in memory. Validate the count against the recorded rounds across the referenced reports.

The claimed 437-test run was not independently reproduced. Verification used file inspection and in-memory probes, without writes or git commands.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after round 3

Candidate `0e11949..98f9c59`. All three findings verified and fixed in the next commit:

1. P1 a later outage left behind an approval: fixed. A findings file's last recorded round must be a returned review; a loop ending in an outage gets another round before stamping. Test: `test_a_loop_whose_last_round_returned_no_review_refuses`.
2. P3 the 140-character row figure: fixed. `docs/todo-workflow.md` and `todo/README.md` now state Office's 100-character limit (`MAX_TABLE_ROW`, `AGENTS.md`).
3. P2 `rounds_spent` unchecked: fixed. A receipt's `rounds_spent` must equal `rounds_recorded` over its findings files. Test: `test_rounds_spent_must_be_what_the_findings_files_record`.

Gates: `python -m unittest discover -s scripts/tests` -> 439 tests OK (2 skipped); `validate` -> `valid: 83 sections`; `plan --check` -> `plan current`.

## Round 4: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-10-21T18:29:37Z
- Effort: medium
- Lines: 18
- Digest: 6813c0ae19a1e324

## adversarial: approve

## consistency: needs-attention

1. **P3** `todo/00-workspace/TODO-02-licensing-and-contributions.md:60`: An open implementation item still requires preserving identifiers declared by Conclave-SDK kits, although this candidate removes the kit manifest and SDK relationship. Reproduce by following that item: its source for identifying kit files and their declared licences is gone. Replace this instruction with explicit, locally verifiable provenance. Stale SDK instructions also remain at `todo/01-brand/TODO-01-suite-naming.md:167` and `todo/03-architecture/TODO-01-tech-stack.md:289`.

## integration: needs-attention

2. **P2** `scripts/lib/todo_graph.py:343`, `scripts/lib/todo_graph.py:911`: Auditing a stamped section can invalidate its receipt and prevent `unstamp` from reopening it. The audit workflow reuses the section’s findings file, but receipt validation requires that file’s latest round to match the existing receipt. `unstamp` first calls `graph(root)`, which enforces that validation.

   Reproduce: stamp after round 1, then append an independent audit as round 2 to the same findings file. Even an approving audit makes validation refuse because the receipt names round 1; an outage triggers the new last-round refusal. Calling `unstamp` encounters the same refusal before changing anything. Confirmed the receipt failure with an in-memory probe. Give audit rounds a separate evidence file or explicit review-loop identity, preserving validation of the original stamped evidence.

## record: advisory

The claimed 439-test run, live scheduled-task removal and Git executable mode were not independently verified. Review used file inspection and in-memory probes, without file modifications or Git commands.

HIGHEST: P2
OVERALL: needs-attention

## Dispositions after round 4

Candidate `0e11949..fbd8aa1`. Both findings verified and fixed in the next commit:

1. P3 open TODO items still named the Conclave SDK: fixed. D00 T02 §2 now heads every Rizonesoft-authored script, including those first ported from the Conclave SDK or Recto, leaving only third-party files in `THIRD-PARTY-NOTICES.md`; D01 T01 and D03 T01 cheaper substitutes name the adaptation placeholder. The remaining mentions are dated `Current state` measurements and stamped sections, left as written.
2. P2 audit rounds appended to the stamped findings file: fixed at the skill layer. `review-todo-section` (all three mirrors) now records audit rounds in `docs/reviews/<NN-domain>/audit-d<NN>-t<NN>-s<N>.md`, never in the stamped findings file, and says why (the receipt names that file's last round; a round appended there breaks validation and `unstamp`). This is Recto's practice (`docs/reviews/06-quality/audit-*.md`).

Gates: `validate` -> `valid: 83 sections`; `plan --check` -> `plan current`. No code changed in this commit.

## Round 5: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-10-21T18:31:37Z
- Effort: medium
- Lines: 18
- Digest: 9bf7edd0498f83eb

## adversarial: approve

No new actionable finding.

## consistency: approve

No remaining round 4 defect identified in the revised TODO instructions or the three skill mirrors.

## integration: approve

The separate audit findings path addresses the receipt-validation and `unstamp` conflict. No new integration defect identified.

## record: advisory

Review was limited to the supplied diff and repository file inspection. The claimed 439-test run, live scheduled-task removal, Git executable mode, and validation outputs were not independently reproduced. No files were modified or Git commands run.

HIGHEST: none
OVERALL: approve

## Outcome

Round 5 approved every lens on `0e11949..42f174e` (`HIGHEST: none`, `OVERALL: approve`): clean after four rounds of fixes, well inside the 22-round cap.
