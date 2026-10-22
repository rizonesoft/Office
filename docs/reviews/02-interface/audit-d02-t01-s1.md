# Audit findings: D02 T01 §1 Inventory Schema and Checker

Audit stance under the current review process (D02 T01 §23). Candidate: the stamped implementation `602f9dd` and every later change to the files it owns, up to `179ec01`: `scripts/check-inventory.py`, `scripts/tests/test_check_inventory.py`, `design/inventory/schema.json`.

## Checkpoint at the current tip

```text
python -m unittest discover -s scripts/tests -p "test_check_inventory.py"   -> Ran 37 tests ... OK
python scripts/check-inventory.py                                          -> exit 0
```

The section's checkpoint (at least 6 tests and OK) passes; no regression at the tip.

## Self-review

- The three round-3 fixes made after the old cap (huge exponent exits 2; isolated-constraint diagnostics; ambiguous duplicate ids) are present with their tests at the tip.
- Later changes to the owned files came from §3, §19, §20 and §21 and the SPDX headers; each was reviewed in its own section. This audit reviews the checker as it stands.

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-10-22T08:23:20Z
- Effort: medium
- Lines: 30
- Digest: 8eab2460ab5e2f0d

## source-defect: needs-attention

1. **P1: Cyclic containment passes.** `scripts/check-inventory.py:263` checks parent existence and ambiguity, but never cycles. Reproduce with `{"id":"word.home","app":"word","kind":"tab","label":"Home","parent":"word.home"}`. `check()` returns `[]`. Two records naming each other as parent also pass. These cannot represent the containing-record relationship.

2. **P1: A blank shortcut passes.** `design/inventory/schema.json:141` requires length, but not meaningful content. Reproduce with `{"id":"word.shortcut","app":"word","kind":"shortcut","label":"Example","shortcut":" "}`. `check()` returns `[]`, although no key chord is recorded.

3. **P1: Web addresses bypass the no-link rule.** `design/inventory/schema.json:334` and `scripts/check-inventory.py:34` recognize only HTTP(S) prefixes and `www.`. Set a valid record’s label to `support.microsoft.com/en-us/office`. Both schema validation and `check()` return no problems despite the explicit prohibition on web addresses.

## adversarial: needs-attention

4. **P1: Duplicate JSON members silently erase forbidden content.** `scripts/check-inventory.py:148` uses the decoder’s last-value-wins behavior. Reproduce with `[{"id":"word.home","app":"word","kind":"tab","label":"https://example.com","label":"Home"}]`. Loading followed by checking returns `[]`; the stored link disappears before validation. Reject duplicate members during decoding.

5. **P2: Malformed Outlook window cells crash validation.** `scripts/check-inventory.py:235` inserts window values into a set before validating their types; line 192 also performs unsafe set membership. Replace the first Outlook baseline row’s window cell with `{}`. Whole-inventory `main([])` raises uncaught `TypeError`; checking that baseline individually also crashes. Validate cell types before using them as set elements.

## consistency: needs-attention

6. **P1: Capture provenance need not match the reference.** `design/inventory/schema.json:205` accepts any nonempty profile, while line 270 accepts any nonempty `capturedFrom`; the checker never resolves either against `REFERENCE.md`. Reproductions that return `[]`:
   - A valid record with bounds and `captureProfile:"does-not-exist"`.
   - A control with `source:"uia:1.2.3.4"` and `capturedFrom:"not-a-build"`.

   `REFERENCE.md` requires the named capture profile and a recorded reference build. These accepted records provide neither trustworthy geometry provenance nor build provenance.

## record: needs-attention

7. **P3: The ticked every-rule test claim remains unsupported.** `todo/02-interface/TODO-01-parity-inventory.md:89` claims tests fail when any rule is disabled. `scripts/tests/test_check_inventory.py:246` tests ambiguous parents only; the shortcut tests at line 206 use unique targets. Removing the ambiguous-target branch at `scripts/check-inventory.py:272` is not exercised by any supplied fixture. Add an isolated duplicate-target test before retaining that claim.

Malformed-input results above were reproduced using in-memory fixtures without modifying files.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 1

All seven findings verified against the checker at the tip and fixed at their owning layer in the next commit. Each fix has a regression test; six of the tests fail against the stamped checker and schema (run with the fixes stashed), and the seventh fails when the branch it covers is removed:

1. P1 a parent chain that loops passed: the checker follows each record's parent chain through ids defined once and reports `parent chain loops: a -> ... -> a` (`test_a_record_cannot_contain_itself`, self and two-record loops).
2. P1 a blank shortcut passed: the schema's `shortcut` now needs a non-space character (`pattern: \S`), as `label` already did (`test_a_blank_shortcut_is_refused`, spaces and non-breaking spaces).
3. P1 web addresses without `http` passed: the schema's `noLink` rule now refuses a URL with any scheme, `mailto:`, `www.`, a dotted host followed by a path, and a name ending in `.com`, `.org`, `.net`, `.gov` or `.edu`. The checker's whole-record scan uses that same schema pattern instead of a second copy, so the two cannot drift. Endings that are also inventory words (`app`, `dev`, `io`, `info`) are left out, since `word.command.app-restore` and Backstage's Info page use them; the first broader draft flagged six real Word ids and was narrowed (`test_web_addresses_without_http_are_refused`, with the real words kept valid).
4. P1 a repeated member erased its first value: the loader refuses a repeated member in any object as unreadable, exit 2 (`test_a_repeated_member_is_unreadable`).
5. P2 a non-string Outlook window cell crashed: window cells are type-checked before any set lookup, in the row check and in the whole-inventory window gate (`test_a_malformed_outlook_window_cell_is_a_problem_not_a_crash`).
6. P1 provenance was not resolved: `captureProfile` must be a profile and `capturedFrom` a build that `design/inventory/REFERENCE.md` records, and a source stamped with a build must match `capturedFrom` (`test_capture_provenance_must_be_recorded_in_the_reference`).
7. P3 the ambiguous-target branch had no test: `test_a_target_defined_twice_is_ambiguous`.

`python scripts/check-inventory.py` over the committed inventory still exits 0; the checker tests run 44 and pass.
