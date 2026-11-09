# Completion review: D02 T01 §4

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-09T03:26:33Z
- Effort: medium
- Type: adversarial
- Lines: 13
- Digest: a21c28b554177e9c

SECTION: D02 T01 §4
PURPOSE: completion
CONTRACT: sha256:f5f47ef934d64ae437f9db513711c284324020f4a3656ac875927eb96de033a2

1. **P2: Project and Outlook shell measurements have no owner.** [TODO-01-parity-inventory.md:180](D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:180) permits baseline-backed overrides as the completed inventory. Those baselines contain identifiers and placement classifications, not measured bounds, visible labels or observed behaviour. Consequently, Project’s QAT and Outlook’s shell can pass this section without anyone measuring them. §13 and §15 own ribbon captures, including layout-switch discovery; §14 and §16 own app panes and Backstage. None requires replacing these shell overrides with live measurements. **Remedy: extend** this section to require measured shell differences for both apps, including applicable Outlook window types. If capture must wait, assign that capture explicitly to another section instead of treating baseline records as completed measurements.

2. **P2: Required layout inputs can ship without geometry, and the checkpoint accepts them.** [TODO-01-parity-inventory.md:178](D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:178) and line 179 require behaviour and sources for search, regions, KeyTips, Backstage and status bar frames, but omit a bounds requirement. [TODO-02-interface-spec.md:110](D:/GitHub/Office/todo/02-interface/TODO-02-interface-spec.md:110) explicitly derives region dimensions from those bounds. The schema makes bounds optional, and the checkpoint at line 183 only requires counts, prefixes and annotations. An in-memory probe containing 60 region records passed schema validation and that checkpoint’s assertion with zero bounds and zero control identifiers. Downstream work would have to invent dimensions or repeat the capture. **Remedy: extend** the acceptance criteria to require measured bounds and capture provenance for each named visible element. Check exact required records and meaningful geometry, with refusal tests for missing elements and measurements.

3. **P2: App overrides cannot distinguish removal, replacement and containment.** [TODO-01-parity-inventory.md:180](D:/GitHub/Office/todo/02-interface/TODO-01-parity-inventory.md:180) represents both absent controls, such as Excel’s Editing selector, and additional controls as ordinary records whose `parent` names a shared record. But [schema.json:91](D:/GitHub/Office/design/inventory/schema.json:91) defines `parent` as containment; the format has no override operation or applicability field. A consumer cannot determine whether an Excel child replaces the shared selector, removes it or appears inside it. The §22 ownership checker would also treat a record describing an absent control as something requiring implementation. §28 owns cloud-feature dispositions, not per-app shell inheritance. **Remedy: extend** this section with an explicit representation and resolution rule for app additions, replacements and absences. Verify the effective shell for each app, including that Excel has no Editing selector while Word retains it.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention
