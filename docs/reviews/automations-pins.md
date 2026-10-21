## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-10-21T00:02:01Z
- Effort: medium
- Lines: 27
- Digest: e11e1886e4588957

Review based on the supplied diff. The shell helper failed before execution, so I could not inspect `run.py` or `alert.py`, or run reproductions. The reproduction cases below are derived from the code.

## adversarial: needs-attention

1. **[P1] Interrupted proposals permanently block subsequent runs.** `scripts/lib/pin_proposal.py:116` deletes the unfinished branch before recovering its worktree. If the process dies after line 126 creates the worktree, Git refuses that deletion because the branch remains checked out. Every subsequent run returns 1 without removing or recovering the abandoned worktree. **Reproduce:** terminate a proposal during its build, then rerun `update`. The existing test creates only a bare branch, so it misses the actual interrupted-run state.

2. **[P1] A malformed feed can move the .NET pin outside .NET 11.** `scripts/check-dotnet-pin.py:74` validates the target’s syntax and membership but not its channel. The channel check at line 193 applies only to the current pin. **Reproduce:** supply `latest-sdk: "12.0.100"` and releases listing both that version and the current .NET 11 pin. With no solution, `update` proposes `dotnet/12.0.100`, passes checks and records completion. Validate the target’s major and minor before comparison or proposal.

3. **[P2] Valid four-part NuGet pins are falsely rejected as unpublished.** `scripts/check-nuget-pins.py:43` uses textual membership, while `scripts/lib/package_versions.py:55` compares tuples of different lengths. NuGet normalizes a zero fourth component away. **Reproduce:** pin `4.3.0.0` and return `{"versions":["4.3.0","4.4.0"]}`. The automation reports the installed pin as unpublished instead of proposing `4.4.0`. Separately, `stable_key("4.3.0.0") > stable_key("4.3.0")` incorrectly treats equivalent versions as different releases. Normalize membership and comparison consistently with [NuGet’s version rules](https://learn.microsoft.com/en-us/nuget/concepts/package-versioning#normalized-version-numbers).

## consistency: needs-attention

4. **[P2] New test subprocesses omit `CREATE_NO_WINDOW`.** `scripts/tests/test_pin_automations.py:76`, `:79` and `:317`, plus `scripts/tests/test_check_winui_pin.py:81`, launch Git without `creationflags`. **Reproduce:** run these tests through a windowless Windows interpreter and capture their subprocess arguments. The no-console assertion in `test_automations.py` scans selected production files only, so it cannot catch these violations.

5. **[P2] SDK discovery hardcodes an operator-specific absolute path.** `scripts/check-conclave-kits.py:28` embeds `R:\GitHub\Conclave-SDK`. This violates the repository’s explicit requirement to resolve tools through configuration, discovery, then a setup-required state, and to keep discovered paths in ignored local configuration. **Reproduce:** unset `CONCLAVE_SDK_ROOT` on a machine with the SDK installed elsewhere. The check uses the hardcoded path without discovery and fails.

## integration: needs-attention

6. **[P1] A failed doctor can be reported as healthy.** `scripts/check-conclave-kits.py:84` parses stdout without checking `result.returncode`; line 88 accepts missing `checks` as an empty successful report. **Reproduce:** stub each doctor invocation to return exit 1, stdout `{}`, and stderr explaining its failure, with no file drift. `main` returns 0 and prints that the doctor reports no gap. Require a successful exit and a validated report schema. The new tests never exercise `doctor()`.

7. **[P2] SDK validation does not enforce the exact-SDK build contract.** `scripts/check-dotnet-pin.py:82` reads only `sdk.version`, and line 116 checks only that version string. Neither verifies `rollForward: "disable"`. **Reproduce:** commit a `global.json` with a valid current pin and `rollForward: "latestMajor"`, then propose a newer .NET 11 SDK. The proposal preserves that policy and can pass a build using a later installed SDK, despite the email asserting roll-forward is disabled. Validate the SDK selection policy before accepting the baseline or proposal.

## record: needs-attention

8. **[P2] “No email means every pin is current” is false under the documented completion model.** `.conclave/automations/README.md:36` makes that claim, but `scripts/lib/pin_proposal.py:108` suppresses subsequent emails whenever the completion ref exists, regardless of whether main was updated. **Reproduce:** successfully propose an update, leave it unmerged, then run the task again. Main remains behind, but the task returns success without emailing. Deleting the proposal branch also preserves this silence. The documentation must distinguish a current pin from a previously announced, unresolved proposal.

OVERALL: needs-attention

## Dispositions of the first round

1. Fixed: `_drop` prunes, then removes an abandoned worktree under an `office-pin-*` folder before deleting the branch; a worktree anywhere else is reported, never removed (`test_a_run_killed_mid_proposal_is_recovered`, `test_the_operators_own_worktree_is_never_removed`).
2. Fixed: `latest()` refuses a `latest-sdk` outside channel 11.0 as unreadable (exit 2), so no other channel is ever proposed.
3. Fixed: `stable_key` drops a zero fourth part as NuGet normalizes it, and `published()` compares normalized versions.
4. Not a defect: `CREATE_NO_WINDOW` is the rule for processes a scheduled run starts, so no console opens on the desktop. Tests run in a console, as every existing test under `scripts/tests` does.
5. Fixed: the SDK comes from `CONCLAVE_SDK_ROOT`, else a `Conclave-SDK` folder beside the repository, else setup required (exit 2); no hardcoded path.
6. Fixed: a doctor report without a non-empty `checks` list, or a non-zero exit with no gap named, raises and the check exits 2.
7. Fixed: `global.json` must set `rollForward` to `disable`, or the pin check fails.
8. Fixed: the README says one email per new version or state, that no new email is not proof every pin is current, and how to list open proposals.

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-10-21T00:07:07Z
- Effort: medium
- Lines: 17
- Digest: 2da586f93241482e

Review based on the supplied diff. The shell failed before execution, so I could not read additional files or run reproductions. Line references are from the diff.

## adversarial: needs-attention

1. **[P1] Recovery can forcibly delete an operator-owned worktree and its uncommitted work.** `scripts/lib/pin_proposal.py:115` treats any path component beginning with `office-pin-` as proof of ownership. An operator worktree at `R:\scratch\office-pin-review\tree`, or anywhere beneath an ancestor named `office-pin-project`, passes this check. Line 118 then runs `git worktree remove --force`. **Reproduce:** create a personal worktree on `winui/2.5.1` at either path, leave uncommitted changes, ensure no completion ref exists, and run `update`. Recovery attempts to delete it. Require durable evidence that the automation created that specific worktree; a directory prefix is insufficient.

## integration: needs-attention

2. **[P2] Doctor schema validation still accepts malformed reports as healthy.** `scripts/check-conclave-kits.py:95` accesses `c["name"]` only when `status != "ok"`. Consequently, exit 0 with `{"checks":[{"status":"ok"}]}` passes validation and returns no gaps, despite the stated requirement for named checks. Non-string statuses and names also become ordinary gap text instead of invalid-report failures. **Reproduce:** pass `doctor_run(0, '{"checks":[{"status":"ok"}]}')` to `kits.doctor`; it returns `[]`. Validate every entry’s required fields and types before filtering. The new doctor tests omit these malformed-entry cases.

3. **[P2] The ownership regression test does not establish its claimed guarantee.** `scripts/tests/test_check_winui_pin.py:137` tests only an operator path without the accepted prefix. It therefore passes while finding 1 remains destructive. **Reproduce:** change that fixture’s parent to an operator-created `office-pin-review` directory and retain its preservation assertions. Add an uncommitted file and assert its contents survive recovery.

## record: needs-attention

4. **[P2] The recovery disposition claims ownership protection the implementation does not provide.** `docs/reviews/automations-pins.md:39` closes finding 1 using `test_the_operators_own_worktree_is_never_removed`, but that test covers only one naming case. The implementation classifies ownership by ancestor names, not creation evidence. **Reproduce:** use finding 1’s operator-owned path; it satisfies the deletion predicate despite never having been created by the automation. The disposition should remain open until ownership is established and the destructive counterexample is tested.

OVERALL: needs-attention

## Dispositions of the second round

1. Fixed: a directory name is no longer evidence. `propose` writes an owner record (`office-pin-owner.json`, naming the branch and the worktree path) beside the worktree before creating it, and `_drop` removes a leftover worktree only when that record names this branch and that exact path. Any other worktree, whatever its path, is reported and kept with its uncommitted files.
2. Fixed: every doctor entry must be an object with a non-empty text `name` and `status`, or the check cannot check (exit 2); the malformed cases are in `test_a_failed_or_empty_doctor_is_never_healthy`.
3. Fixed: `test_an_operators_worktree_is_never_removed_whatever_its_path` covers an `office-pin-review` folder, an owner record for another branch, and a plain folder, each with an uncommitted file that must survive; it fails on the round 1 code.
4. Fixed: the first round's disposition 1 is superseded by disposition 1 above.
