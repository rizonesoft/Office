# Completion review: D02 T01 §25


## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T12:25:08Z
- Effort: medium
- Type: adversarial
- Lines: 11
- Digest: 9db742a53a2af461

SECTION: D02 T01 §25
PURPOSE: completion
CONTRACT: sha256:8ea4fa3d3073700f6b4d328f74e9d63ae563cb677f9e5849fe03800a0764bbab

1. **[P2] extend: Require current source-to-baseline reconciliation.** `todo/02-interface/TODO-01-parity-inventory.md:675` requires §19’s checkpoint, which checks fixture tests and inventory validity but omits the real-workbook `import-office-ids.py <source> --check` recorded in the original receipt. A dropped control can therefore escape the required gates: removing one Word row in memory reduced 5,638 rows to 5,637 and `check_baseline` returned no problems. §18 would then lack that control in its completeness denominator. Require the importer’s read-only comparison against all pinned workbooks, with provenance verification and quoted results for the audited tip; unavailable sources must leave fidelity unconfirmed. §23 and §27 own checker validation, not reconciliation of committed baseline contents.

2. **[P2] extend: Align the stopping path with the current review policy.** `todo/02-interface/TODO-01-parity-inventory.md:676` explicitly stops at 22 rounds, whereas `todo/README.md:110` requires the current 33-round process, including adoption by previously started loops. If round 22 still finds P2 issues, this section permits stopping and filing them eleven rounds before the governing policy allows. Replace the obsolete cap in the introduction and checklist with the current policy, preserving the severity cutoff and requiring the recorded outcome and receipt to agree with the actual stopping reason.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended


## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T12:28:53Z
- Effort: medium
- Type: adversarial
- Lines: 9
- Digest: d8e713487fe13633

SECTION: D02 T01 §25
PURPOSE: completion
CONTRACT: sha256:b72542104f310929e61e867c4839f8911a6ec10ad49364724ca33947cb50b2a9

No completion gaps found. The revised contract covers source reconciliation, missing or mismatched workbooks, regression reopening, and current review stopping rules. §18 explicitly depends on §25; §23 and §27 own checker validation. Approval covers the plan, not baseline verification results.

COMPLETE: yes
HIGHEST: none
OVERALL: approve
