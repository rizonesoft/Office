# Completion review: D00 T03 §16

## Round 1: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T11:14:54Z
- Effort: medium
- Lines: 11
- Digest: a6a31d7ed87534cf

SECTION: D00 T03 §16
PURPOSE: completion
CONTRACT: sha256:5e6708025c0f5965d37c1ad70535bba836b542da97fb052d674fa0e15f04b1c9

1. **[P2] extend: resolve the adoption boundary for existing §14 and §15 receipts.** Both lack `completion_rules`, so the proposed default classifies both as version 1, although §15 stamped with post-cutoff evidence under the hardened rules. Conversely, requiring version 2 literally “from §14 on” would reject §14's digest-free evidence. The plan therefore does not consistently preserve the rules each stored receipt actually met. Define the historical classification explicitly, including §14's bootstrap exception and §15's hardened evidence, without rewriting receipts or reviews. Test all four existing 33-round receipts and prove that §15 retains its applicable hardened checks.

2. **[P2] extend: prove that an ordinary new stamp cannot inherit the timestamp exemption.** Current `stamp` accepts digest-free evidence dated before `CONTRACT_REQUIRED_FROM`. The required re-stamp test can pass unchanged because reopening freshness already rejects the old record; it does not prove that version 2 removes the exemption for a first stamp. Explicitly require version 2 contract checks regardless of the evidence's run date, and add a first-stamp test using genuine pre-cutoff evidence: refuse it without writes, then accept a fresh matching review and read back `completion_rules: 2`.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
