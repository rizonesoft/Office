## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T23:17:48Z
- Effort: medium
- Type: adversarial
- Lines: 24
- Digest: 271d73d7dd0b9589

### adversarial: approve

### consistency: needs-attention

1. **P3** `docs/specs/2026-10-23-campaign-scope-design.md:96`: The new decision duplicates number 38, already assigned to table-row limits immediately below. References to “decision 38” now identify two different instructions. Give the new decision a unique identifier and update its references.

### integration: needs-attention

2. **P3** `todo/00-workspace/TODO-03-automations-and-keep-alive.md:1075`: This open item still requires the launcher to select between working alone and orchestrating, with tests for both verdicts. The next line explicitly makes orchestration always false. Following §37 as written therefore requires implementing a mode the owner removed. Update the launcher requirement and acceptance test to select only the lead model.

### source-defect: approve

### design: advisory

No user-facing surface.

### excellence: approve

### record: needs-attention

3. **P3** `scripts/tests/test_start_campaign.py:30`: The stop regression verifies wording without proving that Claude receives it or stops. Reproduction: remove `$goal` from the real invocation at `scripts/start-campaign.ps1:234` in memory and run all five `StartCampaignModelTest` methods. All still pass, which I verified. Add an argument-delivery assertion and record a real operator-stop reproduction before treating the reported continuation bug as verified fixed.

HIGHEST: P3
OVERALL: needs-attention

## Outcome (round 1)

1. Real, fixed: the new decision is now number 40, after 39, and the four TODO references name decision 40.
2. Real, fixed: D00 T03 §37's verdict item no longer stores an orchestrates field and its launcher item selects only the lead model, each with a `**Corrected 2026-11-11:**` note.
3. Real in part, fixed in part: `test_the_real_start_passes_the_goal` now fails when the start line drops `$goal`. A real operator stop was not reproduced: that needs a live campaign session started from the launcher, which this change was not made in. The cause was read from the code (the repository's Stop hook allows the stop once the guard is ended, `scripts/campaign_guard.py` `stop_decision`; the goal text named only a park as met), and the next operator stop in a campaign is the proof.
