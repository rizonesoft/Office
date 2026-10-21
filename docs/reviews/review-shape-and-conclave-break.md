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
