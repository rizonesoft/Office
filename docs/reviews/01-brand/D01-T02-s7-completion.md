# Completion review: D01 T02 §7

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T10:56:26Z
- Effort: medium
- Type: adversarial
- Lines: 17
- Digest: 8dc641a41e9474f7

SECTION: D01 T02 §7
PURPOSE: completion
CONTRACT: sha256:b9a3338109963903f6a0aadac821d9b0a35201b13f682a48d29e3d800f89ca8e

1. **[P2] The comparison uses the wrong asset source.** `todo/01-brand/TODO-02-icon-system.md:237` takes icons from `build/icons/`, but §6 exports the shipped family into `assets/icons/`; `build/icons/` only holds the optional app contact sheet. A clean checkout therefore cannot supply the required file-icon comparisons through this instruction. **Remedy: extend** §7 to build the sheet from freshly verified `assets/icons/` outputs.

2. **[P2] Suite and variant coverage is unspecified.** `todo/01-brand/TODO-02-icon-system.md:238` requires rows for apps and file icons but omits the suite mark, despite distinctness rule 7 explicitly governing it. It also permits one large rendering per icon to stand for independently drawn small variants. A passing large icon can therefore conceal a confusing small icon or an unreviewed suite mark. §2, §4 and §5 own creation, not this comparison against Microsoft. **Remedy: extend** the comparison inventory to include the suite mark, monochrome mark and each distinct app/file drawing at representative displayed sizes.

3. **[P2] The repair instruction edits generated files.** `todo/01-brand/TODO-02-icon-system.md:239` directs the builder to redraw the §3, §4 or §5 file and then regenerate. Those sections name generated SVGs; `scripts/build-icons.py:127`, `:131` and `:155` recreate them from drawing code. Following the instruction can erase the repair and restore the failed artwork. **Remedy: extend** the step to change the owning generator, regenerate, then repeat the comparison on the resulting exports before recording pass.

4. **[P2] The checkpoint accepts a completely absent review.** `todo/01-brand/TODO-02-icon-system.md:244` checks only a heading and the absence of a literal failure cell. I exercised the checker with only `## Sign-off`; it returned no errors, and that text also contains no failure cell. Thus removing every verdict, reviewer identity and evidence reference still satisfies the checkpoint. **Remedy: extend** the checkpoint to verify the required comparison rows and applicable rule results, plus the dated independent approval and its evidence record. This can be a recorded inspection; it does not require a new framework.

5. **[P2] The later owner audit lacks an identified evidence set.** `todo/01-brand/TODO-02-icon-system.md:241` records the reviewer and review path but does not require identifying the compared asset revision, Microsoft reference versions/sources, or retained comparison-sheet location. A subsequent regeneration or replacement of scratch images leaves the owner unable to establish which artwork was approved, contrary to decision 3’s evidence-backed audit. **Remedy: extend** the sign-off record with the reviewed asset revision, reference identities and retained evidence paths outside the repository, and require approval to refer to the final regenerated comparison.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome after round 1

- Extended: 1, 2, 3, 4, 5 (updated `D01 T02 §7` in `todo/01-brand/TODO-02-icon-system.md` to build the sheets from verified `assets/icons/` outputs and `design/icons/suite/rizonesoft-office-mono.svg`, cover the suite mark, monochrome mark, 6 apps and 26 file types across their distinct drawing tiers/variants, redraw in the owning `scripts/lib/` generators before regenerating and re-checking, record the audited git revision, generator digests, Microsoft reference build/sources and scratch sheet SHA-256 digests under `## Sign-off`, and verify all 5 required headings plus a `test_build_icons.py` completeness test in the Test checkpoint)
- Filed: none


## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T10:59:26Z
- Effort: medium
- Type: adversarial
- Lines: 11
- Digest: 9911d4455b508d64

SECTION: D01 T02 §7
PURPOSE: completion
CONTRACT: sha256:6dc9c84804ff120a7a02e93c10498b2fabaeaf77278d0fcaaaad6577c8ae46f5

No completion gaps found. The revised section addresses all five previous findings: verified asset sources, distinct drawing coverage, repairs in generators, substantive completeness checks, and independent approval tied to retained evidence. The specified comparison sizes match the generator’s drawing selection.

Asset creation and export remain owned by §§2 to 6; Plan’s deferred native file icon belongs to D03 T01 §5. This approves the plan’s completeness, not the artwork or the pending sign-off.

COMPLETE: yes
HIGHEST: none
OVERALL: approve
