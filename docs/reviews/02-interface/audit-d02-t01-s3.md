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
- All seven post-cap fixes from `D02 T01 §3` Round 3 (`docs/reviews/02-interface/D02-T01-s3.md`), the UIA worker subprocess boundary (`capture_in_worker`), document ownership checks across expansion and collapse (`expand_all` and `close_popup`), baseline membership verification on tabs (`walk_tab`), end-to-end geometry invalidation across main and sidecar outputs (`capture` and `main`), and licensing/activation refusal (`licensing_problem`) are covered by the 43 unit and integration tests in `scripts/tests/test_capture_ui.py` and the live capture checkpoint on Word Home (`R:\scratch\word-home.json`, 55 records with `bounds` recorded under `fhd-100`).
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
