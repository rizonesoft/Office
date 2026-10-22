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
