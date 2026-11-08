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
- All seven post-cap fixes from `D02 T01 §3` Round 3 (`docs/reviews/02-interface/D02-T01-s3.md`) and the later UIA worker subprocess separation (`capture_in_worker`) are verified by the 39 unit tests in `scripts/tests/test_capture_ui.py` and the live capture checkpoint on Word Home (`R:\scratch\word-home.json`, 55 records with `bounds` recorded under `fhd-100`).
- Driving the Simplified Ribbon switch (`SingleLineRibbonToggle`) remains explicitly deferred to `D02 T01 §15` (`Outlook Ribbon and Item Windows`) per the dated correction in `D02 T01 §3`, and `capture-ui.py --layout simplified` exits 2 naming either the missing `SingleLineRibbonToggle` or `D02 T01 §15`.
