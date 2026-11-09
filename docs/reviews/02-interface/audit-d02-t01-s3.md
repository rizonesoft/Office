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
- All seven post-cap fixes from `D02 T01 §3` Round 3 (`docs/reviews/02-interface/D02-T01-s3.md`), the UIA worker subprocess boundary (`capture_in_worker`), bounded COM initialization and persistent STA apartment execution (`_Apartment`, `Launched`), document ownership and identity verification across expansion, collapse, and retries (`check_alone`, `expand_all`, and `close_popup`), COM reference release before process-exit waiting (`Launched.close`), baseline membership verification on tabs, controls, and menu items (`walk_tab` and `expand_items`), atomic non-overwriting publication and KTM kernel-transacted merge replacement (`publish` and `transacted_replace`), end-to-end geometry invalidation across main and sidecar outputs (`capture` and `main`), and licensing/activation refusal (`licensing_problem`) are covered by the 47 unit and integration tests in `scripts/tests/test_capture_ui.py` and the live capture checkpoint on Word Home (`R:\scratch\word-home.json`, 55 records with `bounds` recorded under `fhd-100`).
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

## Round 4: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T22:23:36Z
- Effort: medium
- Type: adversarial
- Lines: 30
- Digest: 1ec1976927a09c2f

## adversarial: needs-attention

1. **[P1] Merge can still overwrite a concurrent save.** `scripts/lib/office_com.py:149` checks destination bytes, then line 153 replaces the destination unconditionally. An editor saving between those operations loses its changes, and publication reports success. An in-memory probe injected that save immediately before replacement and confirmed the editor’s bytes were overwritten. Precondition: an ordinary concurrent save during `--merge`. Comparison and replacement need protection covering both operations.

2. **[P1] Rollback deletes concurrent edits to newly created output.** `scripts/lib/office_com.py:165-167` unconditionally unlinks published paths without backups. Reproduce by publishing a previously absent inventory, saving an annotation into it, then failing publication of the unverified sidecar. Rollback deletes the annotated inventory. The in-memory probe confirmed the destination disappeared. Precondition: concurrent editing plus a second-file publication failure. Rollback must establish ownership of the current destination before deleting it.

## consistency: approve

## integration: needs-attention

3. **[P2] Ownership checks use Office COM objects from an uninitialized thread.** `scripts/capture-ui.py:1010-1015` passes `launched.check_alone()` to a fresh Python thread, although its application and document proxies were created on the launching thread. There is neither COM initialization nor interface marshaling. Normal worker capture reaches this path before selecting a tab and can fail instead of capturing. A native `CoGetApartmentType` probe inside this exact callback returned `-2147221008`, “CoInitialize has not been called.” Keep COM operations in a correctly initialized owning apartment with a bounded process-level recovery mechanism.

## source-defect: approve

## design: advisory

Surface: no.

## excellence: needs-attention

Findings **1 and 2 [P1]** violate the “Never lose work” requirement in `docs/product-principles.md:16`. Atomic replacement alone does not preserve concurrent work.

## record: needs-attention

4. **[P3] The ownership-check fix lacks evidence for its actual COM execution path.** `docs/reviews/02-interface/audit-d02-t01-s3.md:177` declares the threaded fix covered, but `scripts/tests/test_capture_ui.py:673-675` substitutes a Python callback, and lines 696-699 substitute `sleep`. Both pass despite finding 3. The latest disposition at line 181 supplies unit-suite results without a post-change live checkpoint. Add coverage exercising the COM apartment boundary and record the current candidate’s live result.

Verification: 48 selected tests passed; three additional tests were blocked by the read-only environment’s temporary-directory restriction. In-memory publication probes reproduced findings 1 and 2. No files were modified; no live Office capture was run.

HIGHEST: P1
OVERALL: needs-attention

### Round 4 disposition

1. **[P1] Merge can still overwrite a concurrent save**: fixed in `scripts/lib/office_com.py` (`publish`) by wrapping `rename(staged[path], path)` for expected-bytes destinations in `guarded_replace`, which checks destination bytes immediately before replacement and, if a save occurred after backup creation, verifies the backup content or restores the saved bytes if `backup` and `path` shared the same link, raising `Refused` without overwriting the editor's save; covered by `CaptureIntegration.test_concurrent_create_or_modify_is_never_overwritten` (subtest 4) in `scripts/tests/test_capture_ui.py`.
2. **[P1] Rollback deletes concurrent edits to newly created output**: fixed in `scripts/lib/office_com.py` (`publish`) by recording `placed_ino[path]` and checking during rollback of newly created files (`path not in aside`) that `os.stat(path).st_ino == placed_ino.get(path)` and `path.read_bytes() == files[path].encode("utf-8")` before unlinking, so concurrent edits to a newly created output survive a later failure; covered by `CaptureIntegration.test_concurrent_create_or_modify_is_never_overwritten` (subtest 5) in `scripts/tests/test_capture_ui.py`.
3. **[P2] Ownership checks use Office COM objects from an uninitialized thread**: fixed in `scripts/capture-ui.py` (`_Apartment`, `Launched`, and `capture_in_worker`) by running a persistent single-threaded COM apartment thread (`ole32.CoInitialize(None)`) per `Launched` session so document creation, `open_documents`, `check_alone`, `language`, and `close` all execute inside the owning STA while `capture_in_worker` passes `timeout=remaining` to bound parent-side COM checks; covered by `Round3.test_replacement_document_and_close_reference_release` and `Worker.test_capture_in_worker_enforces_timeout_and_roundtrips_results` in `scripts/tests/test_capture_ui.py`.
4. **[P3] The ownership-check fix lacks evidence for its actual COM execution path**: fixed in `scripts/tests/test_capture_ui.py` (`Round3.test_replacement_document_and_close_reference_release` and `Worker.test_capture_in_worker_enforces_timeout_and_roundtrips_results`) by asserting `ole32.CoGetApartmentType` returns `0` (`S_OK`) and all COM callbacks execute on the same initialized STA thread, and by recording the post-change live Word Home capture checkpoint below.
- Layer: `scripts/lib/office_com.py`, `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (46 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` (`R:\scratch\word-home.json: 55 records; bounds recorded under fhd-100`) + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).

## Round 5: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T22:36:01Z
- Effort: medium
- Type: adversarial
- Lines: 28
- Digest: 7f911cd18b67f93d

## adversarial: needs-attention

1. **[P1] Merge still loses concurrent atomic saves.** `scripts/lib/office_com.py:159-162` checks the destination, then replaces it without protection spanning both operations. An editor can atomically save between those steps. The backup still contains the original bytes, so the subsequent check at line 176 passes and publication reports success. An in-memory filesystem probe reproduced success with the editor’s bytes lost. Precondition: an ordinary concurrent save during `--merge`. Moving the check closer to replacement does not eliminate this race.

2. **[P2] Office initialization can hang indefinitely before the worker deadline starts.** `scripts/capture-ui.py:568` calls `_init_com` without a timeout; `_Apartment.call` consequently waits indefinitely at line 533. If COM activation or `Documents.Add()` blocks, execution never reaches `capture_in_worker` or its deadline. A controlled blocked-dispatch probe confirmed that launch remained blocked until explicitly released. Precondition: Office becomes unresponsive during startup or document creation. Bound initialization and provide recovery for partially launched instances.

## consistency: approve

## integration: approve

## source-defect: approve

## design: advisory

Surface: no.

## excellence: needs-attention

Finding **1 [P1]** violates the “Never lose work” requirement in `docs/product-principles.md:16`. Atomic replacement does not make the preceding comparison atomic.

## record: needs-attention

3. **[P3] The concurrency regression test does not establish the claimed fix.** `scripts/tests/test_capture_ui.py:856-859` inserts its edit before calling the temporarily patched `os.replace`, so the new guard sees that edit. It never exercises an atomic save after the guard and before the underlying replacement, which reproduces finding 1. Consequently, `docs/reviews/02-interface/audit-d02-t01-s3.md:225` incorrectly declares that race fixed.

Verification: 48 selected tests passed. In-memory probes exercised publication and blocked initialization. No files were modified; no live Office capture was run. Tests requiring temporary-file writes were excluded.

HIGHEST: P1
OVERALL: needs-attention

### Round 5 disposition

1. **[P1] Merge still loses concurrent atomic saves**: fixed in `scripts/lib/office_com.py` (`transacted_replace` and `publish`) by executing expected-bytes verification, backup hard-link creation, and destination replacement inside a single Windows KTM kernel transaction (`CreateTransaction`, `CreateFileTransactedW` with `GENERIC_READ | DELETE` and `FILE_SHARE_READ`, `CreateHardLinkTransactedW`, `MoveFileTransactedW`, and `CommitTransaction` / `RollbackTransaction`), so the destination is kernel-locked against concurrent writes and atomic `os.replace` (`WinError 6800: ERROR_TRANSACTIONAL_CONFLICT`) before its bytes are read and remains locked until the replacement commits; covered by `Writes.test_transacted_replace_enlists_before_reading_and_rolls_back_on_mismatch` and `CaptureIntegration.test_concurrent_create_or_modify_is_never_overwritten` in `scripts/tests/test_capture_ui.py`.
2. **[P2] Office initialization can hang indefinitely before the worker deadline starts**: fixed in `scripts/capture-ui.py` (`Launched.__init__` and `Launched._recover_hung_launch`) by bounding `_init_com` with `init_timeout=60.0` on `self._apartment.call(...)` and, on `TimeoutError`, closing the apartment, posting `WM_CLOSE` if an owned window handle was created, closing any `self.proc`, and raising `Refused`; covered by `Round3.test_replacement_document_and_close_reference_release` in `scripts/tests/test_capture_ui.py`.
3. **[P3] The concurrency regression test does not establish the claimed fix**: fixed in `scripts/tests/test_capture_ui.py` (`CaptureIntegration.test_concurrent_create_or_modify_is_never_overwritten` subtests 3 and 4 and `Writes.test_transacted_replace_enlists_before_reading_and_rolls_back_on_mismatch`) by attempting an atomic `os.replace(editor_tmp, enlisted_dst)` and an in-place write inside `on_enlisted` (after `transacted_replace` has read and verified the destination bytes and before `MoveFileTransactedW`), confirming the kernel blocks the concurrent atomic save with `WinError 6800` and preserves `editor_tmp`.
- Layer: `scripts/lib/office_com.py`, `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (47 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` (`R:\scratch\word-home.json: 55 records; bounds recorded under fhd-100`) + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).

## Round 6: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T22:52:24Z
- Effort: medium
- Type: adversarial
- Lines: 30
- Digest: f2e445812a1a018a

## adversarial: needs-attention

1. **[P1] Rollback can still destroy a concurrent save.** `scripts/lib/office_com.py:249-251` compares the destination’s inode and bytes, then restores the backup using an unprotected rename. Reproduce by publishing the inventory, failing publication of its sidecar, and atomically saving an annotation after rollback’s comparison but before its rename. Recovery overwrites the annotation with the original inventory. An in-memory filesystem probe reproduced this loss. The new transaction protects forward replacement, but ends before rollback. The deletion at lines 244-245 has the equivalent race. Precondition: an ordinary concurrent save during recovery from a publication failure.

2. **[P2] Launch timeout does not cancel initialization or recover a partially launched instance.** `scripts/capture-ui.py:580-593` queues apartment shutdown and clears references, but the running `_init_com` call continues. If activation or `Documents.Add()` stalls before line 617 assigns `hwnd`, recovery cannot even post its close message. Releasing a blocked dispatch after the timeout reproduced creation of a document after refusal, followed by apartment exit with `quit=False`. Precondition: slow or temporarily unresponsive Office startup. Initialization needs cancellation-aware cleanup on its owning apartment, including recovery when no window handle has yet been recorded.

## consistency: approve

## integration: needs-attention

3. **[P2] Merge leaves sidecar records pointing to discarded parent IDs.** `scripts/capture-ui.py:1238-1241` remaps identities only in the main records, then publishes `ctx.unverified` unchanged. Reproduce with an existing Home tab whose retained ID is `word.home-reviewed` and whose `uiaId` is `TabHome`, then capture Home with an unverified add-in group. Merge retains `word.home-reviewed`, but the sidecar group still references `word.home`, which exists in neither output. An in-memory `main()` probe returned success with this dangling reference. Precondition: an existing tab ID differs from the fresh capture’s generated ID. Apply the same identity mapping to both outputs.

## source-defect: approve

## design: advisory

Surface: no.

## excellence: needs-attention

Finding **1 [P1]** violates the “Never lose work” requirement at `docs/product-principles.md:15`: recovery itself can discard annotations.

## record: needs-attention

4. **[P3] The startup regression test does not establish cleanup.** `scripts/tests/test_capture_ui.py:722-730` claims to verify apartment cleanup, but asserts only elapsed time and refusal text. It releases the blocked dispatch without joining the apartment or checking whether initialization subsequently creates documents or quits Office. It passes despite finding 2, so the recovery coverage cited at `docs/reviews/02-interface/audit-d02-t01-s3.md:273` is incomplete.

Verification: 49 selected tests passed. Sixteen tests requiring filesystem writes were excluded under the read-only restriction. Three additional in-memory probes reproduced the findings above. No files were modified; no live Office capture was run.

HIGHEST: P1
OVERALL: needs-attention

### Round 6 disposition

1. **[P1] Rollback can still destroy a concurrent save**: fixed in `scripts/lib/office_com.py` (`transacted_unlink`, `transacted_restore`, and `publish`) by executing rollback deletion of newly created outputs and rollback restoration of replaced outputs inside Windows KTM kernel transactions (`CreateTransaction`, `CreateFileTransactedW` with `GENERIC_READ | DELETE` and `FILE_SHARE_READ`, `DeleteFileTransactedW` / `MoveFileTransactedW`, and `CommitTransaction` / `RollbackTransaction`), so the destination is kernel-locked before its bytes are verified and rolled back only if its bytes still match what `publish` wrote; covered by `Writes.test_transacted_replace_enlists_before_reading_and_rolls_back_on_mismatch` and `CaptureIntegration.test_concurrent_create_or_modify_is_never_overwritten` in `scripts/tests/test_capture_ui.py`.
2. **[P2] Launch timeout does not cancel initialization or recover a partially launched instance**: fixed in `scripts/capture-ui.py` (`Launched.__init__`, `Launched._recover_hung_launch`, and `Launched._init_com`) by setting `self._cancelled = True` on launch timeout while keeping apartment state intact until the apartment thread finishes, checking `self._cancelled` at each step after `self.owned = True` inside `_init_com`, and running `self.close()` in `except BaseException:` on the owning apartment thread so a delayed dispatch or `Documents.Add()` closes any created document, quits an owned empty instance, and exits the apartment cleanly; covered by `Round3.test_replacement_document_and_close_reference_release` in `scripts/tests/test_capture_ui.py`.
3. **[P2] Merge leaves sidecar records pointing to discarded parent IDs**: fixed in `scripts/capture-ui.py` (`merge` and `main`) by passing `ctx.unverified` into `merge` and remapping each sidecar record's `parent` through `mapping` so unverified groups and controls follow retained parent tab IDs; covered by `Merge.test_children_follow_their_parent_through_a_remapped_id` in `scripts/tests/test_capture_ui.py`.
4. **[P3] The startup regression test does not establish cleanup**: fixed in `scripts/tests/test_capture_ui.py` (`Round3.test_replacement_document_and_close_reference_release`) by joining the apartment thread after releasing both a blocked `dispatch` and a blocked `Documents.Add()`, asserting `_thread.is_alive()` is `False`, no unclosed documents remain, and `quit` is `True`.
- Layer: `scripts/lib/office_com.py`, `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (47 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` (`R:\scratch\word-home.json: 55 records; bounds recorded under fhd-100`) + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).

## Round 7: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T23:03:45Z
- Effort: medium
- Type: adversarial
- Lines: 30
- Digest: 89520e52e4addc96

## adversarial: needs-attention

1. **[P1] Failed rollback deletes the original recovery copy.** `scripts/lib/office_com.py:271` deletes the backup whenever restoration did not commit, including sharing violations and failed moves or commits. Reproduce by publishing the first output, failing the second output, and holding the first output open without delete sharing during rollback. Restoration fails, but its backup is deleted; `publish()` also ignores the failure at line 327. An injected `ERROR_SHARING_VIOLATION` reproduced `restore=False` followed by backup deletion. Precondition: an ordinary file lock during publication recovery. Preserve failed-restoration backups and report their paths.

2. **[P2] CLI exit terminates the startup cleanup before it runs.** `scripts/capture-ui.py:506` makes the COM apartment thread a daemon. After startup times out, recovery only queues shutdown; `main()` returns 2 at line 1221 and the interpreter exits. If `Documents.Add()` remains blocked, the cancellation checks and cleanup never execute. A subprocess probe with delayed `Add()` reproduced `MAIN_EXIT 2` and `quit=False` at interpreter exit. Precondition: slow or temporarily unresponsive Office startup. Cleanup must survive the CLI’s timeout return.

## consistency: approve

## integration: needs-attention

Finding **1 [P1]** also affects `scripts/word-commands.py:184`, which publishes commands and shortcuts through the shared helper. A second-file failure can leave mismatched outputs while destroying the original first-file backup.

## source-defect: approve

## design: advisory

Surface: no.

## excellence: needs-attention

Finding **1 [P1]** violates the recovery requirement in `docs/product-principles.md:15`: a recoverable publication failure can destroy the recovery data itself.

## record: needs-attention

3. **[P3] The startup regression supplies lifecycle management absent from production.** `scripts/tests/test_capture_ui.py:794` and line 808 explicitly join the apartment after releasing blocked initialization. Those joins allow cleanup to finish, whereas the CLI exits immediately. Consequently, the test passes despite finding 2, and the fixed disposition at `docs/reviews/02-interface/audit-d02-t01-s3.md:321` overstates recovery. Add a subprocess test that follows the actual CLI exit path.

Verification: 49 selected tests passed; 16 tests requiring filesystem writes were excluded. The whole-inventory checker exited 0. Two additional probes reproduced the failures above. No files were modified; no live Office capture was run.

HIGHEST: P1
OVERALL: needs-attention

### Round 7 disposition

1. **[P1] Failed rollback deletes the original recovery copy**: fixed in `scripts/lib/office_com.py` (`transacted_restore` and `publish`) by tracking `superseded = True` only when `dst` was not placed (`not placed_ok`) or `actual != expected_bytes` (so `transacted_restore` unlinks `backup` only when `dst` was superseded by a concurrent save, preserving `backup` on transient failures such as sharing violations or failed moves/commits), and by collecting any unrestored backups in `publish` and reporting their preserved paths to `sys.stderr` and via `exc.add_note(...)`; covered by `Writes.test_transacted_replace_enlists_before_reading_and_rolls_back_on_mismatch` (in-memory) and `CaptureIntegration.test_concurrent_create_or_modify_is_never_overwritten` subtest 6 in `scripts/tests/test_capture_ui.py`.
2. **[P2] CLI exit terminates the startup cleanup before it runs**: fixed in `scripts/capture-ui.py` (`_Apartment.__init__`, `_Apartment.close`, `Launched.__init__`, and `Launched._recover_hung_launch`) by making `Launched`'s COM apartment thread non-daemon (`daemon=False` by default) and bounding `_Apartment.close(join_timeout=...)` so interpreter shutdown after `main()` returns 2 waits for any delayed `Documents.Add()` or `dispatch` on the owning STA thread to reach the cancellation check and run `self.close()`; covered by `Round3.test_replacement_document_and_close_reference_release` in `scripts/tests/test_capture_ui.py`.
3. **[P3] The startup regression supplies lifecycle management absent from production**: fixed in `scripts/tests/test_capture_ui.py` (`Round3.test_replacement_document_and_close_reference_release`) by adding a child subprocess probe that invokes `cu.main(...)` with a delayed `Documents.Add()` exceeding `init_timeout`, calls `sys.exit(rc)` immediately without any manual thread join, and asserts via `atexit` that `rc == 2` and `{"doc_closed": true, "quit": true}`.
- Layer: `scripts/lib/office_com.py`, `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (47 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` (`R:\scratch\word-home.json: 55 records; bounds recorded under fhd-100`) + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).

## Round 8: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T23:20:16Z
- Effort: medium
- Type: adversarial
- Lines: 26
- Digest: 89d5507288ce5cd8

## adversarial: needs-attention

1. **[P2] A hung COM call still prevents CLI termination after timeout.** `scripts/capture-ui.py:506` creates a non-daemon apartment thread; `:575` uses that default. Recovery at `:596` only bounds the join, leaving Python shutdown waiting indefinitely for the blocked thread. Reproduce with an injected dispatch that waits on an unset event and `init_timeout=0.05`: the probe printed the timeout refusal and `MAIN_RETURNED`, but remained alive after three seconds and required termination. Precondition: an Office COM call that remains unresponsive. Cleanup needs a lifecycle that preserves recovery without indefinitely blocking the caller’s exit.

## consistency: approve

## integration: approve

## source-defect: approve

## design: advisory

Surface: no.

## excellence: needs-attention

Finding **1 [P2]** conflicts with the reliability and clear-feedback requirements in `docs/product-principles.md:22`: reporting a startup timeout does not release the invoking process.

## record: needs-attention

2. **[P3] The new subprocess regression does not exercise cleanup after CLI exit.** `scripts/tests/test_capture_ui.py:866` delays `Documents.Add()` by 0.3 seconds, while `:873` sets `init_timeout=0.15`. Recovery at `scripts/capture-ui.py:582` then joins for another 0.75 seconds, allowing cleanup to finish before `main()` returns. Consequently, the test does not establish the interpreter-shutdown behavior claimed in the Round 7 disposition. An in-memory mutation restoring daemon threads still produced `doc_closed=True`, `quit=True`, and exit 0 with those timings. Make the delayed operation outlast the recovery join, and separately verify genuinely blocked calls cannot hold the CLI indefinitely.

Verification: 49 selected tests passed; one additional test was blocked by the read-only filesystem when creating a temporary directory. The whole-inventory checker exited 0. No files were modified; no live Office capture was run.

HIGHEST: P2
OVERALL: needs-attention

### Round 8 disposition

1. **[P2] A hung COM call still prevents CLI termination after timeout**: fixed in `scripts/capture-ui.py` (`_Apartment.__init__`, `_Apartment.close`, `_Apartment._join_at_exit`, `Launched.__init__`, `Launched._recover_hung_launch`, and `Launched._abandon_hung_launch`) by keeping the COM apartment thread a daemon (`daemon=True`) while registering a bounded `atexit` cleanup waiter (`_join_at_exit`, bounded by `shutdown_timeout`) when `_thread.is_alive()` remains `True` after `_recover_hung_launch`'s brief join, so a delayed-but-completing COM call finishes cleanup during interpreter shutdown while a permanently unresponsive COM call is abandoned after `shutdown_timeout` and never blocks CLI exit; covered by `Round3.test_replacement_document_and_close_reference_release` in `scripts/tests/test_capture_ui.py`.
2. **[P3] The new subprocess regression does not exercise cleanup after CLI exit**: fixed in `scripts/tests/test_capture_ui.py` (`Round3.test_replacement_document_and_close_reference_release`) by testing both a delayed `Documents.Add(0.25s)` with `init_timeout=0.05` (asserting `AT_MAIN_RETURN:{"doc_closed": false, "quit": false}` when `main()` returns 2 and `ATEXIT:{"doc_closed": true, "quit": true}` at interpreter shutdown) and a permanently hung `dispatch` waiting on an unset `threading.Event()` with `init_timeout=0.05` (asserting the child CLI process terminates with exit code 2 within 2.5s).
- Layer: `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (47 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` (`R:\scratch\word-home.json: 55 records; bounds recorded under fhd-100`) + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).

## Round 9: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T23:36:10Z
- Effort: medium
- Type: adversarial
- Lines: 28
- Digest: 5c1b3cfea5c1e781

## adversarial: needs-attention

1. **[P2] Startup timeout still abandons a partially launched Office instance.** `scripts/capture-ui.py:565` stops waiting after the shutdown budget, while `:624` can request closure only when `self.hwnd` exists. That handle is assigned after `new_document()` returns at `:671`. If document creation remains blocked beyond both budgets, the daemon thread dies without closing the document or quitting Office. Reproduced by changing the existing subprocess probe’s delay from 0.25 to 0.9 seconds with `init_timeout=0.05`: it exited 2 with `ATEXIT:{"doc_closed": false, "quit": false}`. Precondition: slow Office document creation. Recovery needs ownership established before the blocking operation and a cleanup lifecycle that survives the caller’s exit.

## consistency: approve

## integration: needs-attention

2. **[P2] Failed rollback of a newly created output is silently ignored.** `scripts/lib/office_com.py:332` discards the result of `transacted_unlink()`. If publication creates the first file, fails on the second, and a reader temporarily prevents deletion of the first, publication leaves partial output without reporting the failed recovery or its path. An in-memory probe reproduced a remaining `first.json` and an empty recovery diagnostic. Precondition: an ordinary file lock during rollback. Handle failed deletion explicitly, as the restoration path already does for existing files.

## source-defect: approve

## design: advisory

Surface: no.

## excellence: needs-attention

Findings **1 and 2 [P2]** leave recovery incomplete without actionable diagnostics, contrary to the reliability and clear-feedback requirements in `docs/product-principles.md`.

## record: needs-attention

3. **[P3] The startup recovery test proves only completion within the extra grace period.** `scripts/tests/test_capture_ui.py:867` delays creation by 0.25 seconds, fitting inside the 0.5-second shutdown wait. The permanently hung probe at `:892` blocks dispatch before establishing ownership. Neither tests an owned instance whose document creation outlasts shutdown. Consequently, the recovery claim at `docs/reviews/02-interface/audit-d02-t01-s3.md:413` remains incomplete; finding 1 reproduces the missing case.

Verification: 49 tests passed; three were blocked by filesystem restrictions and 13 were excluded because they require writes. The whole-inventory checker exited 0. No files changed; no live Office capture ran.

HIGHEST: P2
OVERALL: needs-attention

### Round 9 disposition

1. **[P2] Startup timeout still abandons a partially launched Office instance**: fixed in `scripts/capture-ui.py` (`Launched.__init__`, `Launched._init_com`, `Launched._try_bind_window`, and `Launched._abandon_hung_launch`) by raising the `atexit` shutdown grace budget floor to `1.5s` (`min(2.0, max(1.5, init_timeout * 5.0))`), binding `self.hwnd` and `self.proc` via `_try_bind_window` before calling `self.new_document()`, and running a bounded (`0.2s`) emergency cleanup in `_abandon_hung_launch` when `self._thread.is_alive()` remains `True` after `shutdown_timeout` (closing any open document in `self.created` or `self.documents()`, calling `self.app.Quit`, posting `WM_CLOSE` to `self.hwnd`, and closing `self.proc`); covered by `Round3.test_replacement_document_and_close_reference_release` in `scripts/tests/test_capture_ui.py`.
2. **[P2] Failed rollback of a newly created output is silently ignored**: fixed in `scripts/lib/office_com.py` (`transacted_unlink` and `publish`) by tracking `status_out` on `transacted_unlink` (`"superseded"` when `actual != expected_bytes`, `"absent"` when already missing, and `"failed"` when enlistment, deletion, or commit fails) and reporting any newly created outputs that failed rollback removal (`rollback could not remove newly created ...`) to `sys.stderr` and via `exc.add_note(...)`; covered by `Writes.test_transacted_replace_enlists_before_reading_and_rolls_back_on_mismatch` (in-memory) and `CaptureIntegration.test_concurrent_create_or_modify_is_never_overwritten` subtest 7 in `scripts/tests/test_capture_ui.py`.
3. **[P3] The startup recovery test proves only completion within the extra grace period**: fixed in `scripts/tests/test_capture_ui.py` (`Round3.test_replacement_document_and_close_reference_release`) by raising `probe_delayed`'s `Documents.Add()` delay to `0.9s` (`init_timeout=0.05`) and adding `probe_hung_add`, which tests an owned instance whose `Documents.Add()` blocks indefinitely past `shutdown_timeout`, asserting `bound_before_add=True`, `doc_closed=True`, `quit=True`, and `proc_closed=True` at `atexit`.
- Layer: `scripts/lib/office_com.py`, `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (47 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` (`R:\scratch\word-home.json: 55 records; bounds recorded under fhd-100`) + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).

## Round 10: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T23:48:16Z
- Effort: medium
- Type: adversarial
- Lines: 28
- Digest: 35dfac28df311af1

## adversarial: needs-attention

1. **[P2] Emergency startup cleanup runs without COM initialization.** `scripts/capture-ui.py:667` starts a new thread that calls the owning STA’s document and application proxies without initializing COM or marshaling them. Exceptions from `Close` and `Quit` are swallowed at lines 656 and 664. **Precondition:** document creation outlasts the startup and shutdown budgets, and the posted `WM_CLOSE` cannot complete. Cleanup then abandons the instance without verifying termination. Reproduced by adding `CoGetApartmentType` checks to the existing hung-add subprocess fixture: both calls returned `0x800401F0`, and shutdown reported `doc_closed=false`, `quit=false`, `proc_closed=true`. Closing the process handle does not close Office.

## consistency: needs-attention

Finding **1 [P2]** bypasses the same-apartment COM lifecycle explicitly established by `_Apartment` at `scripts/capture-ui.py:495`. Emergency cleanup needs a valid COM ownership and execution path too.

## integration: approve

## source-defect: approve

## design: advisory

Surface: no.

## excellence: needs-attention

Finding **1 [P2]** leaves recovery incomplete and silently suppresses its failures, contrary to the reliability and actionable-feedback requirements in `docs/product-principles.md:22`.

## record: needs-attention

2. **[P3] The hung-startup regression cannot detect invalid COM cleanup.** `scripts/tests/test_capture_ui.py:913` and `:926` implement `Close` and `Quit` as unconditional Python flag assignments. Consequently, the test passes despite finding 1. **Reproduce:** require a successful `CoGetApartmentType` result before either assignment; the existing subprocess exits with both cleanup flags false. The assertion at `:946` therefore does not establish the Office cleanup claimed by the Round 9 disposition. Exercise apartment validity and proxy ownership in this failure path.

Verification: 49 tests passed; 16 filesystem-writing tests were excluded from this read-only review. The whole-inventory checker exited 0. Additional probes ran entirely in memory. No live Office capture ran; no repository files changed.

HIGHEST: P2
OVERALL: needs-attention

### Round 10 disposition

1. **[P2] Emergency startup cleanup runs without COM initialization:** Fixed in `Launched._marshal_app`, `Launched._release_marshaled_app`, `Launched._unmarshal_app`, `Launched._emergency_close_com`, `Launched._abandon_hung_launch`, `Launched._init_com`, and `Launched._close_impl` (`scripts/capture-ui.py`). `_init_com` marshals the owning STA's application proxy (`CoMarshalInterThreadInterfaceInStream` for real COM `PyIDispatch` proxies, `__com_marshal__` for apartment-bound test doubles, or owner-thread handoff) before calling `new_document()`, and releases the marshaled stream once `_init_com` or `_close_impl` completes on the owning STA. When `_thread.is_alive()` remains `True` past `shutdown_timeout`, `_abandon_hung_launch` runs `_emergency_close_com` inside a dedicated COM-initialized `_Apartment(daemon=True)` (`cleanup_apt`), unmarshals the application proxy onto `cleanup_apt`'s STA thread, enumerates open documents from `self._documents_of(app)` on that STA thread, closes them, verifies `int(self._documents_of(app).Count) == 0`, calls `app.Quit`, releases COM references and runs `gc.collect()`, verifies process exit via `self.proc.exited(0.5)` before `self.proc.close()`, and records and reports any cleanup or exit failures to `self.cleanup_errors` and `sys.stderr`.
2. **[P3] The hung-startup regression cannot detect invalid COM cleanup:** Fixed in `Round3.test_replacement_document_and_close_reference_release` (`scripts/tests/test_capture_ui.py`), which now enforces `CoGetApartmentType == 0` and per-thread apartment proxy ownership (`threading.get_ident() == self._owner_tid`) across both `probe_delayed` and `probe_hung_add` (via `__com_marshal__` cross-apartment unmarshaling onto `cleanup_apt`'s STA thread and `proc.exited` verification before `proc.close`), plus a `probe_hung_fail` subprocess test verifying that `Close`, `Quit`, and `proc.exited` failures are reported to `sys.stderr`.
- Layer: `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (47 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` (`R:\scratch\word-home.json: 55 records; bounds recorded under fhd-100`) + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).

## Round 11: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-09T00:07:50Z
- Effort: medium
- Type: adversarial
- Lines: 30
- Digest: 3c97ffd2b584dc58

## adversarial: needs-attention

1. **[P1] Emergency startup cleanup discards documents the tool does not own.** `scripts/capture-ui.py:695` enumerates every open document, and `:708` closes them without comparing their identities against `self.created`. For PowerPoint, `:719` sets `Saved = True` before closing, suppressing recovery of unsaved changes. The unconditional `Quit` at `:734` also runs when document enumeration fails.

   **Precondition:** startup exceeds its timeout and shutdown grace period while an operator presentation has opened in the shared PowerPoint instance. This is ordinary concurrent use, already recognized by the normal-cleanup test at `scripts/tests/test_capture_ui.py:374`.

   **Reproduction:** supply the emergency cleanup with two presentations, registering only the first in `self.created`. The in-memory probe returned `foreign_closed=True`, `foreign_saved=True`, `quit=True`, and no cleanup errors. Emergency cleanup must preserve unowned documents and leave the application running when ownership cannot be established.

## consistency: needs-attention

Finding **1 [P1]** bypasses the ownership restriction implemented by normal cleanup at `scripts/capture-ui.py:968`, which closes only `self.created` and refuses to quit when other documents remain.

## integration: approve

## source-defect: approve

## design: advisory

Surface: no.

## excellence: needs-attention

Finding **1 [P1]** violates the “Never lose work” requirement in `docs/product-principles.md`: timeout recovery can discard an unrelated presentation’s unsaved changes.

## record: advisory

49 selected tests passed; 16 tests requiring filesystem writes were excluded from this read-only review. The whole-inventory checker exited 0. The failure reproduction used in-memory doubles, not live Office. No files were modified.

HIGHEST: P1
OVERALL: needs-attention

### Round 11 disposition

1. **[P1] Emergency startup cleanup discards documents the tool does not own:** Fixed in `Launched._emergency_close_com`, `Launched._is_unmodified_blank_doc`, `Launched._abandon_hung_launch`, `Launched._recover_hung_launch`, `Launched._init_com`, and `Launched._close_impl` (`scripts/capture-ui.py`). `_emergency_close_com` now restricts document closure strictly to owned unmodified blank documents: when `self.created` is non-empty, only open documents matching `self.created` (with unchanged `self._created_meta` and ` _is_unmodified_blank_doc(doc)` true, so `Saved` is never `False` and `Path`/file extension are absent) are closed, while any unowned document in `self._documents_of(app)` is left untouched without setting `Saved = True` or calling `Close()`. When `self.created` is empty, a document is closed only if `self._adding_document` is `True`, `Count == 1`, and the single document satisfies `_is_unmodified_blank_doc(doc)`. `app.Quit()` (and `self.proc.exited(0.5)`) is invoked only when document enumeration succeeded (`not enum_failed`), no cleanup errors occurred (`not failures`), `unowned_count == 0`, and `remaining == 0`; otherwise the application is left running and the reason is recorded in `failures` / `self.cleanup_errors`. Also removed raw `WM_CLOSE` posting so window closure never bypasses COM ownership checks. Added regression tests in `Round3.test_replacement_document_and_close_reference_release` (`scripts/tests/test_capture_ui.py`) covering two presentations (only the first in `self.created` and the foreign presentation having `Saved = False`) as well as document-enumeration failure.
- Layer: `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (47 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` (`R:\scratch\word-home.json: 55 records; bounds recorded under fhd-100`) + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).

## Round 12: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-09T00:25:38Z
- Effort: medium
- Type: adversarial
- Lines: 36
- Digest: 5d872149d5d629a0

## adversarial: needs-attention

1. **[P1] Cleanup still discards unsaved PowerPoint changes.** `scripts/capture-ui.py:680` tests `Saved is False`. PowerPoint returns an `MsoTriState` integer, where `msoFalse` is `0`; `0 is False` fails. Consequently, an unsaved presentation with no path passes as “unmodified,” and cleanup sets `Saved = True` and closes it at `:804` or `:1081`. Microsoft explicitly documents that this suppresses saving and loses changes. See [Presentation.Saved](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.presentation.saved) and [MsoTriState](https://learn.microsoft.com/en-us/office/vba/api/office.msotristate).

   **Precondition:** concurrent PowerPoint use during capture or a stalled startup. The emergency branch at `:784` also treats a sole presentation as owned while `Add()` is pending, without an ownership identity.

   **Reproduction:** supply `Name=FullName="Presentation1"`, `Path=""`, `Saved=0`. Both normal and emergency cleanup accepted and closed it. With `created=[]`, `_adding_document=True`, and that presentation as the sole open document, emergency cleanup likewise returned no errors, marked it saved, closed it and quit.

## consistency: approve

## integration: needs-attention

Finding **1 [P1]**: the cleanup guard does not honor PowerPoint’s COM return type. Normalize the value and establish document ownership independently of document count.

## source-defect: needs-attention

Finding **1 [P1]** violates the own-document-only contract in `todo/02-interface/TODO-01-parity-inventory.md:141`.

## design: advisory

Surface: no.

## excellence: needs-attention

Finding **1 [P1]** violates the “Never lose work” requirement in `docs/product-principles.md`.

## record: needs-attention

2. **[P3] The new regression does not prove dirty-document protection.** `scripts/tests/test_capture_ui.py:1022` creates a clean owned presentation and a dirty foreign presentation. The foreign presentation bypasses the blank-document predicate because ownership matching already excludes it. The fixture also uses Python booleans instead of PowerPoint’s integer enum.

   **Reproduction:** replacing `_is_unmodified_blank_doc` with an unconditional `True` in memory still passed `test_replacement_document_and_close_reference_release`. Therefore, the protection claimed at `docs/reviews/02-interface/audit-d02-t01-s3.md:551` is not established. Test dirty owned documents and the pending-`Add()` branch with actual enum values.

Verification: 49 selected tests passed; 16 filesystem-writing tests were excluded. The whole-inventory checker exited 0. Failure and mutation probes used in-memory doubles. No live Office capture ran; no files were modified.

HIGHEST: P1
OVERALL: needs-attention

### Round 12 disposition

1. **[P1] Cleanup still discards unsaved PowerPoint changes:** Fixed in `Launched._is_unmodified_blank_doc`, `Launched._marshal_doc`, `Launched._unmarshal_docs`, `Launched._emergency_close_com`, `Launched._close_impl`, and `Launched._same_doc` (`scripts/capture-ui.py`). `_is_unmodified_blank_doc` now reads `saved = getattr(doc, "Saved", True)` and rejects `saved is None or not bool(saved)`, which handles PowerPoint `MsoTriState` integer `0` (`msoFalse`) as well as `False` and `None` while accepting `-1` (`msoTrue`), `1`, and `True`; both `_emergency_close_com` and `_close_impl` refuse to set `Saved = True` or close a document when `_is_unmodified_blank_doc` returns `False`. Furthermore, created document proxies are marshaled across COM apartments via `_marshal_doc` / `_unmarshal_docs`, and `_emergency_close_com` requires explicit COM object identity matching (`self._same_doc` against `owned_docs` from `self.created` / `self._marshaled_docs`), removing the `created = []` / `_adding_document` count-based fallback so a sole presentation open while `Add()` is pending is never treated as owned.
2. **[P3] The new regression does not prove dirty-document protection:** Fixed in `Round3.test_replacement_document_and_close_reference_release` (`scripts/tests/test_capture_ui.py`). Updated the fixtures to use PowerPoint `MsoTriState` integer values (`Saved = -1` for `msoTrue`, `Saved = 0` for `msoFalse`), added direct assertions that both `_emergency_close_com` and `_close_impl` refuse to close a dirty owned presentation (`Saved = 0`, leaving `dirty_own.closed == False` and `dirty_own.Saved == 0`, so replacing `_is_unmodified_blank_doc` with `True` fails the test), and verified that when `created = []` (`_adding_document = True`) a sole open presentation (`Saved = 0` or `Saved = -1`) is left untouched without calling `Close()` or `Quit()`.
- Layer: `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (47 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` (`R:\scratch\word-home.json: 55 records; bounds recorded under fhd-100`) + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).


## Round 13: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-09T00:37:06Z
- Effort: medium
- Type: adversarial
- Lines: 28
- Digest: 987866c2ed2115f3

## adversarial: needs-attention

1. **[P2] Popup timeout silently accepts an incomplete reading.** `scripts/capture-ui.py:1204` returns the last item list even when the stability condition never succeeded. **Precondition:** a gallery continues populating during the four-second reading budget. Reproduce with successive readings containing one, two, three and four items, then expire the deadline. The in-memory probe returned four items without refusing; `expand_all()` treats that nonempty result as successful. Require stability before accepting the result, or explicitly report incomplete capture.

## consistency: approve

## integration: needs-attention

2. **[P2] Sequential tab merges erase previously captured unverified records.** `scripts/capture-ui.py:1607` replaces the app-wide sidecar with only the current capture’s unverified records, although the main inventory preserves previously captured tabs. **Precondition:** capture tabs individually using the supported `--tab` and `--merge` options. Reproduced through `main()` with in-memory storage: capture Home, then Insert, each containing an unverified group. Both calls returned `0`; the main output retained both tabs, but the sidecar retained only `word.insert.new`. Home’s unresolved inventory disappeared. Merge the sidecar consistently with the main inventory, preserving records outside the current capture.

## source-defect: needs-attention

Finding **1 [P2]** undermines the item-capture requirement at `todo/02-interface/TODO-01-parity-inventory.md:147`: an unfinished gallery reading can be published without identifying omitted items.

## design: advisory

Surface: no.

## excellence: needs-attention

Findings **1 and 2 [P2]** leave incomplete inventory or discard unresolved capture evidence during supported workflows, contrary to the reliability requirement in `docs/product-principles.md`.

## record: advisory

49 selected tests passed; 16 filesystem-writing tests were excluded. The whole-inventory checker exited `0`. Both reproductions used in-memory doubles. No live Office capture ran, and no files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 13 disposition

1. **[P2] Popup timeout silently accepts an incomplete reading:** Fixed in `popup_items` and `expand_all` (`scripts/capture-ui.py`). `popup_items` now compares the full item signature (`(runtime_id(), control_type, name, automation_id)` across all items, not merely `len(items)`) and raises `Refused(f"{label!r} items did not stabilise before timeout")` whenever the four-second deadline expires with `stable < 2` and any items or rebuilding (`Gone`) or changing readings were observed. Added regression test `Popups.test_a_popup_that_never_stabilises_is_refused` in `scripts/tests/test_capture_ui.py`.
2. **[P2] Sequential tab merges erase previously captured unverified records:** Fixed in `main` (`scripts/capture-ui.py`). When `--merge` is passed, `main` reads the existing sidecar `build/capture-ui/<app>-unverified.json`, verifies it was not modified concurrently during the capture, merges `ctx.unverified` into the existing sidecar records via `merge()`, and publishes the merged sidecar under KTM transaction protection (`expected_bytes[unverified_path] = initial_unverified`). Added a sequential `--tab Home` then `--tab Insert --merge` regression test in `CaptureIntegration.test_concurrent_create_or_modify_is_never_overwritten` (`scripts/tests/test_capture_ui.py`) confirming both `word.home.adobe-acrobat` and `word.insert.new` are retained in `word-unverified.json`.
- Layer: `scripts/capture-ui.py`, `scripts/tests/test_capture_ui.py`, `docs/reviews/02-interface/audit-d02-t01-s3.md`
- Verified: `python -m unittest discover -s scripts/tests -p "test_capture_ui.py"` (48 tests OK), `python -m unittest discover -s scripts/tests -p "test_word_commands.py"` (18 tests OK), and `python scripts/capture-ui.py --app word --tab Home --out R:\scratch\word-home.json` (`R:\scratch\word-home.json: 55 records; bounds recorded under fhd-100`) + `python scripts/check-inventory.py R:\scratch\word-home.json` (exit 0).

