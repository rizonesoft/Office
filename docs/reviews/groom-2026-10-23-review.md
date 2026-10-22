## Round 1: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T22:40:38Z
- Effort: xhigh
- Lines: 35
- Digest: 89d5fdb0755d333f

### Completeness: needs-attention

1. **P1, [tech-stack.md:667](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:667): VBA compatibility is silently limited to the corpus.** The object models cover only members used by the selected macros. Members absent from that corpus have no required implementation, and UI inventory ownership cannot detect missing programmatic APIs. Define the required object-model surface independently of corpus selection.

### Sequence: needs-attention

2. **P1, [automations-and-keep-alive.md:333](R:/GitHub/Office/todo/00-workspace/TODO-03-automations-and-keep-alive.md:333): the Phase 3 pin section consumes Phase 4 outputs.** It requires the current `vcpkg.json` baseline to pass and a proposal to build a CMake preset. Neither file exists; [tech-stack.md:426](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:426) assigns their creation to the future platform domain. The foundation-plan document does not create them. Move the watcher work after executable build configuration exists, or introduce that configuration as an earlier prerequisite.

3. **P1, [tech-stack.md:433](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:433): the dependency contract can spread the Entra hold across every app.** Graph integration shares a TODO file with essential local saving, recovery, clipboard and printing. The contract prescribes file-level cross-domain dependencies, which the graph expands into dependencies on every section of the prerequisite file. Apps consuming this file would therefore wait on its Graph registration section. Isolate the optional integration or specify section-level prerequisites so unrelated implementation continues.

4. **P2, [tech-stack.md:57](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:57): the foundation plan precedes its newly added design inputs.** §12 has no dependency on cloud equivalents, localisation or updates and diagnostics (§14 to §16), and its architecture checklist still requires only §1 to §11. No later step reconciles the foundation plan with those decisions. Add the prerequisite edges and require the architecture to incorporate the new records.

### Unattended: needs-attention

5. **P1, [tech-stack.md:342](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:342): the ownership gate has an unsatisfiable intermediate condition.** `query blocked` includes ordinary unmet prerequisites, not just waiting Needs. Immediately after domain authoring, app sections waiting on unfinished platform sections will appear there. Consequently, the required result containing only the permitted holds cannot pass at this Phase 3 gate. Check Needs separately from prerequisite readiness.

6. **P1, [tech-stack.md:440](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:440): the domain-authoring checkpoints do not detect missing domains.** The repeated §17 to §27 pattern runs `validate` and `query stats`. Validation checks existing files; statistics report global totals, without domain counts or assertions. These commands can succeed before the requested domain exists. Require explicit checks for the expected domains, files, subject ownership and dependency edges.

7. **P1, [tech-stack.md:691](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:691): “every domain stamped” prevents the unsigned 1.0 draft.** That condition includes domains containing the six parked Phase 99 items and the signing/MSIX work intentionally left waiting. Literally, it also includes the release domain containing this gate. Define the exact prerequisite sections and permitted exclusions. The owner explicitly authorised unsigned drafts while signing waits.

### Consistency: needs-attention

8. **P1, [interface-spec.md:341](R:/GitHub/Office/todo/02-interface/TODO-02-interface-spec.md:341): the mockup acceptance rule contradicts modernisation.** Every region must remain within two pixels of the classic Microsoft reference, while the new Visio, Project and Outlook instructions permit documented region moves and newer layouts. A compliant modernised mockup can therefore fail sign-off. Compare unchanged regions against the capture and changed regions against their approved modernisation specifications.

9. **P1, [tech-stack.md:88](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:88): obsolete decisions remain active checklist obligations.** §1 still requires signed, Store-ready MSIX distribution and a signing-certificate source despite the unsigned/no-Store decision. Separately, [line 240](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:240) still instructs the executor to write OneDrive and SharePoint into a later milestone despite their inclusion in 1.0. Adding newer introductory text leaves conflicting contracts. Mark the earlier decisions as superseded history and make the executable checklist record the current decisions.

### Record: needs-attention

10. **P2, [groom-2026-10-23.md:32](R:/GitHub/Office/docs/reviews/groom-2026-10-23.md:32): the purported full diff omits the host-readiness work.** The record says D00 T03 §12 was added, and the readable working-tree file contains it, but that file has no hunk in the supplied diff. The inlined additions account for 15 new sections; the recorded increase requires 16. Include the missing hunk so the review candidate and record describe the same change.

11. **P3, [groom-2026-10-23.md:36](R:/GitHub/Office/docs/reviews/groom-2026-10-23.md:36): the five-part micro-step claim is inaccurate.** New checklist items at tech-stack.md:361 to 365, 383 to 385, 403 and 405 lack a concrete backticked path, symbol or command in the item itself. Several also combine decisions for multiple services. Correct those items before recording universal compliance with the five-part rule.

HIGHEST: P1

OVERALL: needs-attention

## Round 2: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T22:49:33Z
- Effort: xhigh
- Lines: 31
- Digest: 77d4280c4e2a9665

### Completeness: needs-attention

1. **P2, [tech-stack.md:672](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:672): the VBA capture lacks schema and ownership integration.** Round 1’s corpus limitation is removed, but the new class/member/signature inventory has no specified schema, checker support or tested ownership check. The existing schema permits UI record kinds and rejects additional properties; `check-inventory.py:485` applies it to every non-baseline inventory file. Require the capture format, validation and member-ownership checks explicitly, including how the Phase 6 capture adds claims after §13 enables the standing ownership gate.

### Sequence: needs-attention

2. **P1, [tech-stack.md:430](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:430): the pin prerequisite is installed too late.** The checklist assigns adding the dependency to the future build section. Meanwhile, [automations-and-keep-alive.md:46](R:/GitHub/Office/todo/00-workspace/TODO-03-automations-and-keep-alive.md:46) depends only on §10 and the authoring section. After authoring, the watcher is ready and sorts before the platform section that creates its inputs. Add the executable prerequisite during §17 authoring, before §17 stamps, and require it to provide a runnable CMake preset. Round 1 finding 2 remains unresolved.

3. **P2, [tech-stack.md:318](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:318): the foundation-plan section requires future build commands to work.** Its completion condition requires application build and test commands to run on a clean clone, but Phase 4 creates that build configuration, and its authoring depends on this section. Move executable verification to the build-foundation work; §12 can document the planned commands.

The Graph isolation contract and §12’s new design-input dependencies address round 1 findings 3 and 4.

### Unattended: needs-attention

4. **P2, [automations-and-keep-alive.md:355](R:/GitHub/Office/todo/00-workspace/TODO-03-automations-and-keep-alive.md:355): Office readiness stops being checked too early.** The check skips Office after Phase 2, although Phase 3 measurements and Phase 6 interoperability and VBA capture still require it. An unavailable reference installation would pass readiness and fail mid-section. Keep checking the required applications while unfinished `office` sections remain.

The Needs query, explicit file-presence checkpoints and release-gate exclusions address round 1 findings 5 to 7.

### Consistency: approve

The modernised-region overlay rule and superseded distribution/storage decisions address round 1 findings 8 and 9.

### Record: needs-attention

5. **P3, [groom-2026-10-23.md:44](R:/GitHub/Office/docs/reviews/groom-2026-10-23.md:44): “64 waiting on prerequisites” mislabels the blocked total.** Read-only reconstruction finds 111 sections, 37 stamped, 60 with unmet prerequisites and six with waiting person Needs. Their union is 64 blocked; four person-held rows have no unmet prerequisite. Record “64 blocked” or give the categories separately.

The missing host-readiness hunk is now supplied, and the decision items name their record files, addressing round 1 findings 10 and 11. No files were modified; Git-backed gates were not rerun.

HIGHEST: P1

OVERALL: needs-attention

## Round 3: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T22:53:58Z
- Effort: xhigh
- Lines: 27
- Digest: 34446461dce89d85

### Completeness: approve

Round 2 finding 1 is addressed: §26 specifies the VBA schema, validation, member ownership and an atomic capture-and-claims commit.

### Sequence: approve

Round 2 findings 2 and 3 are addressed: §17 installs the build prerequisite before stamping and requires runnable presets; §12 documents planned commands, with execution verified by the build foundation.

### Unattended: needs-attention

1. **P2, [automations-and-keep-alive.md:355](R:/GitHub/Office/todo/00-workspace/TODO-03-automations-and-keep-alive.md:355): Phase 3 still escapes the Office check.** Every current unstamped `office` section is in Phase 2. D03 T01 §3 requires page counts from Word but declares `Needs: none` at [tech-stack.md:128](R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:128). After Phase 2 closes, before §25 and §26 author future Office work, the new condition skips Office despite these measurements remaining. Add the missing `office` Needs and require a fixture covering that transition. Round 2 finding 4 remains partially unresolved.

2. **P2, [automations-and-keep-alive.md:355](R:/GitHub/Office/todo/00-workspace/TODO-03-automations-and-keep-alive.md:355): the new trigger trusts an unmaintained cache.** Neither the checker contract nor its startup wiring requires refreshing `build/todo-cache.json`. The current cache contains 95 sections against the canonical 111; a clean clone may have none. `validate`, `query` and `plan --sync` do not regenerate it. Require the checker to read the canonical graph, or establish cache freshness before reading it, with stale-cache and missing-cache fixtures. Otherwise readiness can skip required checks or park unnecessarily.

### Consistency: approve

No additional conflicting obligation found. The distribution, modernisation and ownership corrections remain consistent.

### Record: approve

Round 2 finding 5 is addressed. Read-only reconstruction confirms 111 sections, 37 stamped, 10 ready and 64 blocked: 60 with unmet prerequisites, six person-held, four person-held without unmet prerequisites. The “all fixed” statement should reflect the outstanding Office-readiness findings.

No files were modified. Git-backed gates were not rerun.

HIGHEST: P2

OVERALL: needs-attention

## Round 4: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T22:59:42Z
- Effort: xhigh
- Lines: 30
- Digest: e7ece6915691d4c0

### Completeness: approve

No new scope gap found in the revised grooming contracts.

### Sequence: approve

Existing prerequisite fixes hold. Cache regeneration now precedes both consumers.

### Unattended: approve

Both round 3 fixes hold:

- [D03 T01 §3](/R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:128) declares `office, windows-host`.
- [D00 T03 §12](/R:/GitHub/Office/todo/00-workspace/TODO-03-automations-and-keep-alive.md:355) requires rebuilding the cache and specifies missing-cache, stale-cache and Phase 2 handover fixtures.

The [§13 Needs audit](/R:/GitHub/Office/todo/03-architecture/TODO-01-tech-stack.md:341) also rebuilds first.

### Consistency: approve

The shortened titles retain their scope. Read-only reconstruction matches the generated plan exactly; checked Markdown table rows stay within 100 characters. No new defect found.

### Record: approve

Reconstruction confirms 111 sections, 37 stamped, 10 ready and 64 blocked: 60 with unmet prerequisites, six person-held, with four person-held rows having no unmet prerequisite.

No files modified. Git ancestry, receipt validation and tests were not rerun; the new readiness fixtures remain implementation requirements.

HIGHEST: none

OVERALL: approve
