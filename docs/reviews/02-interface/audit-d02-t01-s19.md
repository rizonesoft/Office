# Audit findings: D02 T01 §19 Control ID Baseline

Audit stance under the current review process (D02 T01 §25). Candidate: the stamped implementation `8193634e3a193aefd853262271a5a2fb2a35893b` and every later change to the files it owns, up to `c291d99dc816fb37f607d4785df91f3848701849`: `scripts/import-office-ids.py`, `scripts/tests/test_import_office_ids.py`, `design/inventory/baseline.schema.json`, `design/inventory/baseline-sources.json`, `design/inventory/REFERENCE.md` (`## Baseline`), `THIRD-PARTY-NOTICES.md`, and the six `design/inventory/<app>/baseline.json` files.

## Checkpoint at the audit's start

```text
python -m unittest discover -s scripts/tests -p "test_import_office_ids.py" -> Ran 27 tests in 1.342s OK
python scripts/check-inventory.py design/inventory                          -> exit 0
python scripts/import-office-ids.py R:/scratch/office-ui-ids/b230a0df45036b2d5e8b49ebf368b3f90ada8d63 --check -> exit 0
python scripts/todo-graph.py resolve "D02 T01 §19"                          -> exit 3 (done: true)
```

The section's checkpoint and the read-only real-workbook reconciliation (`import-office-ids.py <source> --check` across all 28 pinned workbooks at `b230a0df45036b2d5e8b49ebf368b3f90ada8d63`) pass, and all six `design/inventory/<app>/baseline.json` files (`word`, `excel`, `powerpoint`, `visio`, `project`, `outlook`) are present and verified; no regression at the tip.

## Self-review

- All four Round 3 dispositions made after the old 3-round cap (`design/inventory/baseline-sources.json` git blob verification, rejecting non-text cells in `ident()` and `control_type()`, whole-inventory baseline and Outlook window completeness checks in `scripts/check-inventory.py`, and rejecting workbooks with more than one worksheet in `read_rows()`) are present and covered by `scripts/tests/test_import_office_ids.py` (27 tests) and `scripts/tests/test_check_inventory.py` (117 tests).
- Later changes to the owned files (`4c3beb0`, `c549c60`, `3afb456`, `e3fc181`, `6790444`, and `315ea60` in `D02 T01 §23`) kept the committed baselines byte-identical to `b230a0df45036b2d5e8b49ebf368b3f90ada8d63`.

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T12:31:33Z
- Effort: medium
- Type: adversarial
- Lines: 22
- Digest: 83ff1c0658539bf1

## adversarial: approve

## consistency: approve

## integration: approve

## source-defect: needs-attention

1. **[P2] The documented refresh procedure cannot succeed.** [design/inventory/REFERENCE.md:70](D:/GitHub/Office/design/inventory/REFERENCE.md:70) instructs the operator to download a new commit’s workbooks, run the importer, then update the reference and notices. It omits updating `baseline-sources.json`. [scripts/import-office-ids.py:164](D:/GitHub/Office/scripts/import-office-ids.py:164) rejects every commit different from that manifest before reading any workbook. Reproduced by calling `build()` with a different SHA-named source path. The precondition is an ordinary documented refresh. Document how to obtain and verify the new upstream blob manifest, and require updating it before importing.

## design: advisory

Not applicable (`Surface: no`).

## excellence: approve

## record: advisory

The real-workbook `--check` and whole-inventory check independently exited 0. The recorded test counts match the source. Full test execution remains unverified here because the read-only sandbox prevents temporary-file creation; the recorded test timing was not independently reproduced.

HIGHEST: P2
OVERALL: needs-attention

### Round 1 disposition

- **Round 1 `source-defect` 1 (`P2`, refresh procedure in `design/inventory/REFERENCE.md:70` omits updating `design/inventory/baseline-sources.json`):** Verified and fixed in `design/inventory/REFERENCE.md` (`## Baseline`). The refresh instructions now direct the operator to read the upstream commit's tree (`git ls-tree <full commit> -- "Microsoft 365/Current Channel"` in a clone of `OfficeDev/office-fluent-ui-command-identifiers`), verify each downloaded workbook's git blob id (`git hash-object <file>`), and update `design/inventory/baseline-sources.json` with the new `commit` and `blobs` map before running `python scripts/import-office-ids.py R:/scratch/office-ui-ids/<full commit>`. Covered by `test_the_reference_documents_the_baseline_commit` in `scripts/tests/test_import_office_ids.py`, which asserts that `baseline-sources.json` appears before `scripts/import-office-ids.py` in the `To refresh:` block alongside `git ls-tree` and `git hash-object`.


## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T12:36:55Z
- Effort: medium
- Type: adversarial
- Lines: 22
- Digest: 697b4d77c13e3ef6

## adversarial: approve

## consistency: approve

## integration: approve

## source-defect: needs-attention

1. **[P2] The refresh command does not expose workbook blob IDs.** [design/inventory/REFERENCE.md:70](/D:/GitHub/Office/design/inventory/REFERENCE.md:70) specifies `git ls-tree <full commit> -- "Microsoft 365/Current Channel"`. Without `-r`, this lists the directory’s tree entry, not its workbook entries. An operator following the documented refresh therefore lacks the upstream blob IDs needed to verify downloads and populate the manifest. Use `git ls-tree -r <full commit> -- "Microsoft 365/Current Channel"` from the clone root. This behavior follows [Git’s documented directory and recursion semantics](https://git-scm.com/docs/git-ls-tree). The new regression assertions pass despite this defect because they check command names, not whether the command supplies the required information.

## design: advisory

Not applicable (`Surface: no`).

## excellence: approve

## record: advisory

The real-workbook `--check` and whole-inventory checker independently exited 0. Recorded row counts and test counts match the workspace. The reference assertions and seven in-memory malformed-cell probes passed. Full fixture tests and recorded timings remain independently unverified because they require filesystem writes.

HIGHEST: P2
OVERALL: needs-attention

### Round 2 disposition

- **Round 2 `source-defect` 1 (`P2`, `git ls-tree` without `-r` lists the directory tree object rather than its workbook blob entries):** Verified and fixed in `design/inventory/REFERENCE.md` (`## Baseline`). The refresh command now specifies `git ls-tree -r <full commit> -- "Microsoft 365/Current Channel"` from the root of a clone of `OfficeDev/office-fluent-ui-command-identifiers`, and `test_the_reference_documents_the_baseline_commit` in `scripts/tests/test_import_office_ids.py` asserts the exact `-r` invocation.


## Round 3: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T12:40:09Z
- Effort: medium
- Type: adversarial
- Lines: 22
- Digest: 5ca1fd0f3a8cd70c

## adversarial: approve

## consistency: approve

## integration: approve

## source-defect: approve

## design: advisory

Not applicable (`Surface: no`).

## excellence: approve

## record: advisory

The real-workbook `--check` and whole-inventory checker independently exited 0. Recorded row counts and test counts match the workspace. The updated reference assertions and seven malformed-row probes passed.

Full fixture execution and recorded timings remain independently unverified because the sandbox prohibits filesystem writes. The local licence matches the notice after the explicitly documented LF normalization.

HIGHEST: none
OVERALL: approve
