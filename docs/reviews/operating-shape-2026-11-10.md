## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T20:12:49Z
- Effort: medium
- Type: adversarial
- Lines: 24
- Digest: da919358d3e2c6ce

### adversarial: needs-attention

1. **[P2] The lock can survive the launcher script.** `scripts/start-campaign.ps1:125` opens a `FileStream` that is never disposed; cleanup at line 254 removes only the launcher record. The installed shortcut uses `-NoExit` (line 49). Reproduce by letting a campaign finish normally while leaving its window open, then opening Start again. PowerShell remains alive, and release of the undisposed handle depends on garbage collection. The new start can be refused despite no campaign running; Stop cannot identify the previous launcher after its record was removed. Dispose the lock deterministically on completion, cancellation and startup failures.

### consistency: needs-attention

2. **[P3] The old escalation route contradicts the restricted Fable policy.** `AGENTS.md:52` and `.claude/skills/process-todo-section/SKILL.md:58` send a twice-blocked packet to `principal-implementer`. Reproduce with an ordinary implementation packet that fails again after correction, before any review. Neither permitted trigger at `AGENTS.md:48` applies: it is neither a review takeover nor an architecture decision record. Reconcile these instructions so routing does not depend on which paragraph the lead follows.

### integration: needs-attention

Finding **1 [P2]** affects the actual desktop shortcut. `scripts/tests/test_start_campaign.py:156` launches PowerShell without `-NoExit`, so process termination releases the handle and conceals the shortcut’s lifecycle defect.

### source-defect: needs-attention

Finding **2 [P3]** retains an additional Fable escalation trigger outside decision 35 in `docs/specs/2026-10-23-campaign-scope-design.md:93`.

### record: needs-attention

3. **[P3] The per-section cost conclusion contradicts the measurements.** `docs/reviews/operating-mode-2026-11-10.md:46` claims Opus cost less than half of Fable on every section. Lines 17 and 18 report $1.04 versus $2.05: approximately 50.73%, not less than half. The aggregate claim holds; the universal claim does not.

Verification: four read-only launcher tests passed, the fleet verifier passed, and 60 in-memory verifier cases matched expected acceptance/refusal. No files changed. Filesystem-writing suites were not run; restricted PowerShell blocked the lock probe, so finding 1 is source-derived.

HIGHEST: P2
OVERALL: needs-attention

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T20:21:12Z
- Effort: medium
- Type: adversarial
- Lines: 24
- Digest: f0dded6e31718007

### adversarial: needs-attention

1. **[P2] Startup cancellation still bypasses lock disposal.** `scripts/start-campaign.ps1:124` acquires the lock, but cleanup protection begins only at line 232. Reproduce through the installed `-NoExit` shortcut with an existing campaign guard: press Ctrl+C at the handover prompt at line 180, leave that window open, then start again. The cancelled script never calls `Remove-OwnRecord`; the retained handle can refuse the next launcher. Protect everything after acquisition with `try/finally`. This finding is source-derived, not live-tested.

### consistency: needs-attention

2. **[P3] The old escalation instruction remains.** `AGENTS.md:54` still sends a packet “one tier up” when its changes leave the allowed paths. An ordinary `section-writer` returning an out-of-scope change therefore encounters contradictory instructions: line 54 retains escalation, while line 52 requires packet correction and retry, then lead takeover. Remove the obsolete route.

### integration: needs-attention

Finding **1 [P2]** affects the installed shortcut. `scripts/tests/test_start_campaign.py:261` exercises `-NoExit` after normal completion, but does not exercise cancellation before the cleanup block begins.

### source-defect: needs-attention

Finding **2 [P3]** retains a routing instruction outside the two Fable cases established by `docs/specs/2026-10-23-campaign-scope-design.md:93`.

### record: needs-attention

3. **[P3] The coordination-cost conclusion contradicts the table.** `docs/reviews/operating-mode-2026-11-10.md:45` says Fable coordination cost more than Fable building alone on both smaller sections. For D00 T03 §29, line 32 reports **$2.05** coordinating, while line 22 reports **$2.70** building alone. Even the entire routed run costs only **$2.31**. The comparison holds for only one smaller section.

Verification: four read-only launcher tests, the fleet verifier and 76 in-memory verifier cases passed. Filesystem-writing and live launcher tests were not run under the read-only restriction. No files changed.

HIGHEST: P2
OVERALL: needs-attention

## Round 3: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T20:36:05Z
- Effort: medium
- Type: adversarial
- Lines: 22
- Digest: 9d3e439d5756871d

### adversarial: needs-attention

1. **[P2] Record creation still bypasses lock cleanup.** `scripts/start-campaign.ps1:135` writes the launcher record after acquiring the exclusive lock, but the cleanup-protected `try` starts at line 155. If that write fails, for example because the volume fills while an existing lock file can still be opened, execution never reaches the `finally`. The installed `-NoExit` shortcut leaves PowerShell alive, so the undisposed handle can refuse subsequent starts after the storage problem is resolved. Protect record creation immediately after acquisition. This finding is source-derived; live reproduction was not run.

### consistency: needs-attention

2. **[P3] The verifier still prescribes the removed escalation route.** `scripts/verify-agent-tiers.mjs:585` tells callers that work requiring more effort “goes one tier up”; line 568 documents the same rule. Reproduce by checking an Opus agent with `effort: high`: the emitted diagnostic directs escalation, although `AGENTS.md:52` requires correcting the packet, retrying once, then lead takeover. I reproduced that diagnostic in memory. Replace the obsolete routing instruction.

### integration: needs-attention

3. **[P3] The startup-failure regression test can pass without exercising cleanup.** `scripts/tests/test_start_campaign.py:295` waits two seconds before starting the competing launcher, without establishing that the first launcher acquired its lock. If the first process is delayed beyond that interval, the second can acquire the lock first, encounter the malformed guard and exit. Its process exit releases the handle even with disposal removed; the assertions then pass while the first process remains alive. Synchronize on evidence that the first launcher acquired the lock and reached the injected failure before testing admission of its successor.

### source-defect: needs-attention

Finding **2 [P3]** preserves an escalation instruction outside the two permitted Fable cases in `docs/specs/2026-10-23-campaign-scope-design.md:93`.

### record: approve

Verification performed: four read-only launcher tests passed, the fleet verifier passed, and 51 in-memory policy cases matched expected acceptance or refusal. Filesystem-writing suites and live launcher tests were not run under the read-only restriction. No files changed.

HIGHEST: P2  
OVERALL: needs-attention
