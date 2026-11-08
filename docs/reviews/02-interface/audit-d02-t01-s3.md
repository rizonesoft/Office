# Audit findings: D02 T01 §3 UIA Capture Tool

Audit stance under the current review process (D02 T01 §24). Candidate: the stamped implementation `59a4e067a17b78e10346424b33e1e43db8704b63` and every later change to the files it owns, up to the current tip: `scripts/capture-ui.py`, `scripts/lib/office_com.py`, `scripts/tests/test_capture_ui.py`, `scripts/tests/test_word_commands.py`, and `design/inventory/REFERENCE.md`.

## Checkpoint at the audit's start

```text
python scripts/todo-graph.py resolve "D02 T01 §3"                        -> exit 3 (done: true)
python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json ->
group 'Adobe Acrobat' on 'Home': no control the baseline knows, so its provenance is unverified
baseline core tabs not shown in this window: ['TabAddIns', 'TabBackgroundRemoval', 'TabBlogInsert', 'TabBlogPost', 'TabBroadcastPresentation', 'TabConflicts', 'TabDeveloper', 'TabDrawInk', 'TabOutlining', 'TabPrintPreview', 'TabSyntex']
File (Backstage) is not a ribbon tab; its pages are captured by the app's Backstage section
4 unverified records in D:\GitHub\Office\build\capture-ui\word-unverified.json
R:\scratch\word-home.json: 55 records; bounds recorded under fhd-100
python scripts/check-inventory.py R:\scratch\word-home.json              -> exit 0
python -m unittest discover -s scripts/tests -p "test_capture_ui.py"     -> Ran 39 tests in 4.651s OK
python -m unittest discover -s scripts/tests -p "test_word_commands.py"  -> Ran 18 tests in 0.219s OK
python scripts/check-inventory.py design/inventory                       -> exit 0
```

## Self-review

- `design/inventory/REFERENCE.md` now records the installed Microsoft 365 Current Channel build `16.0.20527.20150` (read 2026-11-08) for all six apps while preserving `16.0.20430.20182` (read 2026-10-20) as a historical row so `design/inventory/word/commands.json` and `shortcuts.json` continue to validate against `REFERENCE.md`, and `scripts/tests/test_capture_ui.py` and `scripts/tests/test_word_commands.py` align their `BUILD` fixtures with `16.0.20527.20150`.
- All seven post-cap fixes from `D02 T01 §3` Round 3 (`docs/reviews/02-interface/D02-T01-s3.md`), the UIA worker subprocess boundary (`capture_in_worker`), document ownership and identity verification across expansion, collapse, and retries (`check_alone`, `expand_all`, and `close_popup`), COM reference release before process-exit waiting (`Launched.close`), baseline membership verification on tabs, controls, and menu items (`walk_tab` and `expand_items`), atomic non-overwriting publication and merge-change detection (`publish` and `main`), end-to-end geometry invalidation across main and sidecar outputs (`capture` and `main`), and licensing/activation refusal (`licensing_problem`) are covered by the 46 unit and integration tests in `scripts/tests/test_capture_ui.py` and the live capture checkpoint on Word Home (`R:\scratch\word-home.json`, 55 records with `bounds` recorded under `fhd-100`).
- Driving the Simplified Ribbon switch (`SingleLineRibbonToggle`) remains explicitly deferred to `D02 T01 §15` (`Outlook Ribbon and Item Windows`) per the dated correction in `D02 T01 §3`, and `capture-ui.py --layout simplified` exits 2 naming either the missing `SingleLineRibbonToggle` or `D02 T01 §15`.

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T21:52:36Z
- Effort: medium
- Type: adversarial
- Lines: 32
- Digest: 144b2491dc7e8ba3

## adversarial: needs-attention

1. **[P2] The worker timeout never bounds capture.** `scripts/capture-ui.py:864` blocks on `stdout.readline()` before reaching `child.wait()`. The `timeout` argument at line 848 is unused. If an Office UIA call hangs, the parent never reaches worker termination or application cleanup. A controlled child taking 0.3 seconds still completed normally with `timeout=0.01`; the call took 0.351 seconds. Apply the deadline while reading worker output.

2. **[P1] Expansion continues after the instance becomes shared.** `scripts/capture-ui.py:769` expands controls without checking document ownership. The last check is before tab selection at line 699. During a lengthy `--expand` run, opening and activating an operator presentation in the shared PowerPoint instance allows subsequent ribbon operations against that presentation. Cleanup detects this only afterward. An in-memory probe supplied a `check_alone()` that refused ownership; `expand_all()` nevertheless expanded and returned records. Check ownership before each expansion and subsequent UI action.

## consistency: needs-attention

3. **[P2] A nonempty automation ID incorrectly establishes tab provenance.** `scripts/capture-ui.py:173` treats every tab with an automation ID as verified, regardless of baseline membership. Reproduce with an add-in tab carrying `ThirdPartyTab` and a group containing a built-in control such as Bold. The tab and group enter the main inventory without `baselineMissing`, instead of the unverified sidecar. The in-memory probe confirmed this classification. An arbitrary UIA identifier is not verification against the reference baseline.

## integration: needs-attention

4. **[P2] Invalidated geometry survives in the sidecar and produces a misleading success summary.** `scripts/capture-ui.py:712` removes geometry only from `records`, leaving `ctx.unverified` unchanged. Those records are published at line 951. The summary at line 957 also relies on the initial `problems` list, which geometry invalidation never updates. Reproduce by moving the window after initial profile validation while capturing an unverified group. The probe returned zero main-record bounds, two sidecar records retaining bounds, and `problems=[]`. Consequently, invalidated geometry remains certified as `fhd-100`, and the final summary says bounds were recorded under that profile.

## source-defect: needs-attention

5. **[P1] The required activation refusal is absent.** `design/inventory/REFERENCE.md:51` requires refusing an app showing a licence, activation or reduced-functionality notice. The checks beginning at `scripts/capture-ui.py:672` only require a ribbon, acceptable layout and profile properties. Reproduce with an expired subscription whose ribbon remains accessible alongside an activation notice. An in-memory UIA tree containing `Unlicensed Product` returned 11 records with no problems. This permits restricted UI to become reference inventory despite the explicit refusal contract.

## design: advisory

Surface: no. No separate rendered-surface finding.

## excellence: needs-attention

Findings 1 and 4 violate the stated reliability and clear-feedback requirements in `docs/product-principles.md:22`: capture can wait indefinitely, and its summary can certify geometry that it discarded as invalid.

## record: needs-attention

6. **[P3] The audit overstates integration verification.** `docs/reviews/02-interface/audit-d02-t01-s3.md:24` says all seven post-cap fixes and worker separation are verified by the 39 tests and Word Home checkpoint. The worker tests at `scripts/tests/test_capture_ui.py:547` exercise only `converse()` and `Proxy`; none invokes `capture_in_worker()`. The geometry test at line 496 exercises helpers without invoking `capture()`. Breaking worker launch or geometry removal would leave those tests passing, and the ordinary Word checkpoint does not exercise these failure paths. Narrow the evidence claim and add tests at the actual integration boundaries.

HIGHEST: P1
OVERALL: needs-attention

### Round 1 disposition

1. **[P2] The worker timeout never bounds capture**: fixed in `scripts/capture-ui.py` (`capture_in_worker`) by reading `child.stdout` on a daemon thread into a `queue.Queue`, enforcing the monotonic `deadline` on each line read (`timed_lines`) and on `child.wait()`, killing and reaping the worker in `finally`, and closing its pipes cleanly; covered by `Worker.test_capture_in_worker_enforces_timeout_and_roundtrips_results` in `scripts/tests/test_capture_ui.py`.
2. **[P1] Expansion continues after the instance becomes shared**: fixed in `scripts/capture-ui.py` (`capture`, `expand_all`, and `close_popup`) by calling `launched.check_alone()` after tab selection, before each control expansion, before `target.collapse()`, and before any retry `target.expand()`/`target.collapse()` in `close_popup`; covered by `Round3.test_expand_checks_ownership_before_each_ui_action` in `scripts/tests/test_capture_ui.py`.
3. **[P2] A nonempty automation ID incorrectly establishes tab provenance**: fixed in `scripts/capture-ui.py` (`walk_tab`) by requiring `tab.automation_id in ctx.identifiers` so any tab with an empty or non-baseline automation ID is routed with all of its groups and controls to `ctx.unverified` with `baselineMissing=True`; covered by `Walk.test_a_tab_without_an_identifier_is_set_aside_with_its_groups` in `scripts/tests/test_capture_ui.py`.
4. **[P2] Invalidated geometry survives in the sidecar and produces a misleading success summary**: fixed in `scripts/capture-ui.py` (`Context.drop_geometry` and `capture`) by recording dropped-geometry reasons on `Context`, stripping `bounds`, `captureProfile`, and `size` from `records + ctx.unverified` when `ctx.origin is None`, and appending `ctx.dropped_reasons` to `problems` so `main()` reports `; no bounds: ...`; covered by `CaptureIntegration.test_geometry_invalidation_strips_sidecar_bounds_and_reports_no_bounds` in `scripts/tests/test_capture_ui.py`.
5. **[P1] The required activation refusal is absent**: fixed in `scripts/capture-ui.py` (`licensing_problem` and `capture`) by scanning the window root and its descendants for licensing, activation, or reduced-functionality notices (`LICENSING_PHRASES`) and raising `Refused`; covered by `CaptureIntegration.test_capture_refuses_licensing_or_activation_notice` in `scripts/tests/test_capture_ui.py`.
6. **[P3] The audit overstates integration verification**: fixed in `docs/reviews/02-interface/audit-d02-t01-s3.md` (`## Self-review`) and `scripts/tests/test_capture_ui.py` by adding integration-boundary tests for `capture_in_worker()`, `capture()`, and `main()` (`Worker.test_capture_in_worker_enforces_timeout_and_roundtrips_results` and `CaptureIntegration`).
- Layer: `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (43 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T22:03:15Z
- Effort: medium
- Type: adversarial
- Lines: 32
- Digest: 32768c727f3faa6f

## adversarial: needs-attention

1. **[P1] Publication can overwrite a concurrently created file without `--merge`.** `scripts/capture-ui.py:999` checks existence only before capture; `:1033` later publishes through unconditional replacement at `scripts/lib/office_com.py:139`. Reproduce by starting two captures targeting the same initially absent output. After the first publishes, the second silently overwrites it. An in-memory reproduction replaced intervening handwritten content and returned 0. Publication needs an atomic no-overwrite operation; merge also needs protection against changes after its read.

2. **[P2] Document count does not establish document ownership.** `scripts/capture-ui.py:548` accepts any collection whose count equals `len(self.created)`. If the operator closes the tool’s blank presentation and opens their own in the shared PowerPoint instance between checks, the count remains one and ribbon automation continues against their presentation. The replacement-document probe passed this check. Verify the identities of the remaining documents, not just their count.

## consistency: approve

## integration: needs-attention

3. **[P2] Cleanup retains a document reference while waiting for process exit.** `scripts/capture-ui.py:595` clears instance fields but leaves the loop variable `doc` from `:575` alive through `self.proc.exited(wait)` at `:597`. For the Excel/PowerPoint shutdown behavior explicitly described at `:592`, this defeats the required COM-reference release: capture waits, then refuses before publishing. A weak-reference probe confirmed the document remained alive throughout the exit check and was released only after `close()` returned. Release the loop reference before waiting. This was reproduced with a lifetime-sensitive fake, not live Office.

## source-defect: needs-attention

4. **[P2] New controls inside verified groups lack the required baseline marker.** `scripts/capture-ui.py:204` derives a control’s `baselineMissing` solely from its group’s verification status. Add an unknown `NewCommand` beside baseline-known Bold in Font: it enters the main inventory without `idMso` **or** `baselineMissing`. The in-memory probe confirmed this. `design/inventory/REFERENCE.md:69` explicitly requires newer controls to carry that marker. Evaluate baseline membership per control independently of group routing.

## design: advisory

Surface: no.

## excellence: needs-attention

Finding 1 violates the “Never lose work” requirement at `docs/product-principles.md:16`. Atomic replacement prevents partial bytes, but does not prevent overwriting concurrent work.

## record: needs-attention

5. **[P3] The claimed ownership regression coverage exceeds what the test exercises.** `docs/reviews/02-interface/audit-d02-t01-s3.md:72` claims coverage before collapse and retry actions. However, `scripts/tests/test_capture_ui.py:570` makes ownership fail immediately, so the test exits before the first expansion and never reaches those paths. Removing ownership checks from `close_popup()` leaves this regression passing. Test ownership changing after expansion and during retries, and narrow the evidence claim accordingly.

Verification here: 27 read-only tests passed; additional in-memory probes exposed the failures above. No files were modified, and no live Office capture was run.

HIGHEST: P1
OVERALL: needs-attention

### Round 2 disposition

1. **[P1] Publication can overwrite a concurrently created file without `--merge`**: fixed in `scripts/lib/office_com.py` (`publish`) and `scripts/capture-ui.py` (`main`) by adding atomic no-overwrite creation via `link(staged[path], path)` (`create_only`) when `--merge` is not set and verifying under `--merge` that `out` did not change during capture or between reading and backup-linking (`expected_bytes`); covered by `CaptureIntegration.test_concurrent_create_or_modify_is_never_overwritten` in `scripts/tests/test_capture_ui.py`.
2. **[P2] Document count does not establish document ownership**: fixed in `scripts/capture-ui.py` (`Launched.__init__`, `Launched._doc_meta`, `Launched._same_doc`, and `Launched.check_alone`) by verifying that the created document was not closed or renamed and that the live collection and active document match `self.created`; covered by `Round3.test_replacement_document_and_close_reference_release` in `scripts/tests/test_capture_ui.py`.
3. **[P2] Cleanup retains a document reference while waiting for process exit**: fixed in `scripts/capture-ui.py` (`Launched.close`) by clearing the loop variable `doc = None` and `self._created_meta = []` alongside `self.created` and `self.app` before `gc.collect()` and `self.proc.exited(wait)`, and skipping already-closed documents during cleanup; covered by `Round3.test_replacement_document_and_close_reference_release` in `scripts/tests/test_capture_ui.py`.
4. **[P2] New controls inside verified groups lack the required baseline marker**: fixed in `scripts/capture-ui.py` (`walk_tab` and `expand_items`) by setting `baselineMissing=True` whenever `idmso is None` regardless of whether the parent group is verified; covered by `Round3.test_new_controls_in_verified_groups_carry_baseline_missing` in `scripts/tests/test_capture_ui.py`.
5. **[P3] The claimed ownership regression coverage exceeds what the test exercises**: fixed in `scripts/tests/test_capture_ui.py` (`Round3.test_expand_checks_ownership_before_each_ui_action`) by testing ownership failure at all four action points (before initial `expand`, before initial `collapse`, before retry `expand`, and before retry `collapse`).
- Layer: `scripts/lib/office_com.py`, `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (46 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).

## Round 3: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T22:16:55Z
- Effort: medium
- Type: adversarial
- Lines: 32
- Digest: ce486574cca50396

## adversarial: needs-attention

1. **[P1] Conflict detection can itself discard a concurrent edit.** `scripts/lib/office_com.py:167-168` restores every backup, including destinations it never replaced. Reproduce during `--merge`: create the backup link at line 148, then let an editor atomically save the destination before line 150 checks it. The check detects the change and raises, but rollback replaces the editor’s file with the old backup. An in-memory filesystem probe reproduced the refusal followed by restoration of the original bytes. This requires an ordinary concurrent save. Roll back only changes this invocation actually published, with protection against subsequent edits.

2. **[P2] A blocked ownership check bypasses the worker deadline.** `scripts/capture-ui.py:945` calls `launched.check_alone()` synchronously in the supervising process. Its Office COM calls can block while Office is unresponsive; meanwhile, nothing checks the deadline or terminates the worker. A probe with `timeout=0.2` and a 0.8-second ownership check returned after 0.972 seconds. An indefinitely blocked check never reaches cleanup. The timeout must also cover parent-side COM requests.

## consistency: approve

## integration: needs-attention

3. **[P2] Merge attributes refreshed measurements to the previous Office build.** `scripts/capture-ui.py:228` refreshes geometry and order, while lines 247-248 retain the old `capturedFrom`. Reproduce by merging a capture from `16.0.20527.20150` into records captured from `16.0.20430.20182`: the result contains the new bounds but still declares the historical build. The in-memory probe confirmed this. This is the normal reference-update workflow introduced by this candidate, and contradicts `design/inventory/REFERENCE.md:19`. Preserve annotations while explicitly representing the provenance of refreshed measurements.

## source-defect: needs-attention

4. **[P3] An empty unverified group is admitted to the main inventory.** `scripts/capture-ui.py:191` uses `members and not any(ids)`, which is false when no supported controls were found. Reproduce with a baseline-known Home tab containing an add-in group with no children, or only unsupported child types. `walk_tab()` emits the group into the main records without `baselineMissing` or a warning. The probe confirmed this. This needs an empty or incompletely exposed group, but violates the stated rule at lines 174-176 that groups without a known control go to the sidecar.

## design: advisory

Surface: no.

## excellence: needs-attention

Finding 1 violates the “Never lose work” requirement in `docs/product-principles.md:16`. Finding 2 leaves the intended bounded failure recovery incomplete.

## record: needs-attention

Finding 1 contradicts the concurrency-fix claim in `docs/reviews/02-interface/audit-d02-t01-s3.md:124`. The cited test at `scripts/tests/test_capture_ui.py:748` changes the destination during capture, before publication; it never exercises a concurrent save after backup-link creation.

Verification here: 48 tests that require no file writes passed. Additional in-memory probes reproduced the findings. No files were modified and no live Office capture was run.

HIGHEST: P1
OVERALL: needs-attention

### Round 3 disposition

1. **[P1] Conflict detection can itself discard a concurrent edit**: fixed in `scripts/lib/office_com.py` (`publish`) by verifying `backup.read_bytes() == expected[path]` and `path.read_bytes() == expected[path]` before registering `aside[path] = backup` (unlinking `backup` immediately if `path` changed before replacement) and during rollback restoring `old` only when `path in placed` and `path` still holds the bytes placed by this invocation (or when `path` is absent); covered by `CaptureIntegration.test_concurrent_create_or_modify_is_never_overwritten` in `scripts/tests/test_capture_ui.py`.
2. **[P2] A blocked ownership check bypasses the worker deadline**: fixed in `scripts/capture-ui.py` (`capture_in_worker`) by running `launched.check_alone()` on a daemon thread bounded by `remaining = deadline - time.monotonic()` (`timed_check_alone`) so a blocked parent-side COM check raises `Refused` at the worker deadline and terminates the worker; covered by `Worker.test_capture_in_worker_enforces_timeout_and_roundtrips_results` in `scripts/tests/test_capture_ui.py`.
3. **[P2] Merge attributes refreshed measurements to the previous Office build**: fixed in `scripts/capture-ui.py` (`merge`) by including `capturedFrom` in `refreshed` and updating `source` to `new["source"]` when `old`'s `source` was `uia:<old_capturedFrom>`, preserving hand-written fields while recording the refreshed build provenance; covered by `Merge.test_hand_written_fields_survive_and_positions_refresh` in `scripts/tests/test_capture_ui.py`.
4. **[P3] An empty unverified group is admitted to the main inventory**: fixed in `scripts/capture-ui.py` (`walk_tab`) by treating any group with `not any(ids)` (whose own `automation_id` is not in `ctx.identifiers`) as `unverified` even when `members` is empty; covered by `Round3.test_new_controls_in_verified_groups_carry_baseline_missing` in `scripts/tests/test_capture_ui.py`.
- Layer: `scripts/lib/office_com.py`, `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (46 tests OK) and `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK).
