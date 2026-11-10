## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T19:30:48Z
- Effort: medium
- Type: adversarial
- Lines: 28
- Digest: 13a8f8b2fff9ad05

### adversarial: needs-attention

1. **[P1] Credential permissions fail open.** `scripts/lib/secret_store.py:105` ignores the `icacls` return code; `write_all` then writes credentials at line 123. If ACL changes fail while ordinary file writes remain permitted, import reports success with credentials under the original permissions. Reproduce by returning a nonzero `CompletedProcess` from the injected ACL runner. My read-only probe confirmed `restrict` returns normally. Permission enforcement must succeed before writing any value.

2. **[P2] Stop during restart backoff still launches another session.** `scripts/start-campaign.ps1:184` checks the request only after Claude exits. Request Stop during the sleep at line 201 or the readiness check at line 202: execution returns to line 183 and launches Claude without checking again. This is an ordinary operator action during the advertised restart window. Check cancellation immediately before every launch.

### consistency: needs-attention

3. **[P2] Runtime consumers still access the vault.** `.conclave/automations/alert.py:65` calls `vault_read` whenever the stored key is absent or rejected. `scripts/start-campaign.ps1:148` similarly runs the importer automatically when its token is missing, including during `-DryRun`. A new clone or malformed credential file therefore triggers runtime WSL/vault access, contrary to `AGENTS.md:33`. My mocked missing-key probe confirmed the mailer invokes the vault. Keep importing explicit and report missing local credentials from consumers.

4. **[P3] Launcher documentation describes the retired credential flow.** `.conclave/automations/README.md:33` still says the launcher reads its token from WSL at startup and never stores it locally. Following that paragraph gives the operator an incorrect account of both setup and persistent credential storage.

### integration: needs-attention

5. **[P2] A Stop issued during startup is erased.** `scripts/start-campaign.ps1:174` removes the request after host checking, possible handover input and credential importing. Start the launcher, then issue `-Stop -Now` while those steps are running: no launcher record exists yet, so Stop reports nothing running; startup subsequently deletes the new request, records itself and launches Claude. Register the launcher and distinguish an earlier stop from a cancellation of the current start before lengthy startup work.

### source-defect: needs-attention

Finding **3 [P2]** deviates from decision 34 at `docs/specs/2026-10-23-campaign-scope-design.md:92` and its explicit implementation rule in `AGENTS.md:33`. The runtime fallback is a deliberate exception in the code and tests, but neither governing document authorizes it.

### record: needs-attention

6. **[P3] The claimed restart and vault-isolation tests do not establish their named behavior.** `scripts/tests/test_start_campaign.py:108` merely checks that a stop check appears before the sleep; it passes despite finding 2. Line 126 searches only the launcher text for WSL names, so indirect vault access through the importer passes despite finding 3. I executed both assertion bodies without fixture writes; both passed. Replace these text assertions with behavioral checks for cancellation during backoff and missing-token startup.

Verification was limited to source inspection and read-only, in-memory probes. I did not run suites that create files or exercise live credentials and processes.

HIGHEST: P1
OVERALL: needs-attention

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T19:40:55Z
- Effort: medium
- Type: adversarial
- Lines: 24
- Digest: d734f15a9c81012c

### adversarial: needs-attention

1. **[P2] A second start makes the active launcher unreachable by Stop.** `scripts/start-campaign.ps1:110` overwrites the launcher record before checking the existing guard. Reproduce: start campaign A, open start window B, then close B as instructed at line 142. The record now identifies exited launcher B. `-Stop -Now` reports no running launcher and leaves A running. Registration needs exclusive ownership, and cleanup must remove only the caller’s record.

2. **[P2] Failed termination reports success.** `scripts/start-campaign.ps1:91` ignores `taskkill`’s exit code, prints “Stopped now” and exits zero. Reproduce with a launcher started elevated and Stop running normally: termination can fail with access denied. An in-memory probe substituting a failing native command confirmed the success message and zero exit despite termination exit code 5. Check termination results before claiming the tree ended.

### consistency: needs-attention

3. **[P2] Missing local credentials silently retain an inherited token.** `scripts/start-campaign.ps1:173` reports interactive sign-in without clearing `CLAUDE_CODE_OAUTH_TOKEN`. Start from a shell carrying an expired token with no local credential file: Claude inherits that token instead of using the advertised fallback. An in-memory probe confirmed `InheritedTokenRetained=True`. Clear the inherited value before selecting the repository credential or interactive fallback.

### integration: needs-attention

Finding **1** breaks the contract between the start and stop shortcuts during an ordinary second-window start, including when the operator follows the handover warning.

### source-defect: needs-attention

Finding **3** contradicts decision 34 in `docs/specs/2026-10-23-campaign-scope-design.md:92`: authentication can still depend on a machine environment credential instead of the repository’s credential store.

### record: advisory

Verification comprised source inspection, two in-memory probes and four passing read-only launcher tests. The filesystem-writing suites and live process-tree termination were not run under this read-only review. No files changed.

HIGHEST: P2
OVERALL: needs-attention
