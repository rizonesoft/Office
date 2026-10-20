# Inventory Reference

What the parity inventory is measured against. D02 T01 §2 adds the reference build and capture profiles.

## Baseline

The control identifier baseline is a complete checklist of every tab, group and control each app publishes, so a live capture can be proven complete rather than assumed complete.

| Field | Value |
| ----- | ----- |
| Upstream | OfficeDev `office-fluent-ui-command-identifiers` |
| Folder | `Microsoft 365/Current Channel` |
| Commit | `b230a0df45036b2d5e8b49ebf368b3f90ada8d63` |
| Committed | 2024-03-18 |
| Licence | MIT (notice in `THIRD-PARTY-NOTICES.md`) |
| Imported | 2026-10-20, by `scripts/import-office-ids.py` |
| Files | `design/inventory/<app>/baseline.json` for the six apps |

`design/inventory/baseline-sources.json` holds the git blob id of every upstream workbook at the commit; the importer refuses any input that is missing, extra or not byte-identical to upstream, and `check-inventory.py` over the whole inventory requires all six baselines and every Outlook window it lists. Each baseline file records `baseline:<commit>` as its source, the columns, and one row per workbook row in workbook order, so a row's position is its order. Outlook's item-window workbooks merge into one file whose first column is the window, named as the workbook names it: `explorer`, `mailitem` (compose), `mailread`, `apptitem` (appointment), `addritem` (contact), `taskitem`, `dlstitem` (contact group), `logitem` (journal), `postitem`, `postread`, `reportitem`, `reqread`, `reqsend`, `resenditem`, `respcounter`, `responseread`, `responsesend`, `rssitem`, `shareitem`, `smsedit`, `smsread`, `mmsedit` and `mmsread`.

Rows with a null `idMso` are controls the workbooks list without an identifier; they keep their policy id and position. Anything newer than 2024-03-18 in the live build is found by the live capture and recorded on the inventory record as `baselineMissing`.

To refresh: download the six apps' Current Channel workbooks at a new commit into `R:\scratch\office-ui-ids\<full commit>\`, run `python scripts/import-office-ids.py R:/scratch/office-ui-ids/<full commit>`, and update this table and `THIRD-PARTY-NOTICES.md`. `--check` reports whether the committed files match a downloaded commit.
