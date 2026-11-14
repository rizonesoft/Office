# Codex campaign

Run `scripts/start-campaign.ps1 -Runner codex`, or open "Office Codex campaign" on the Windows Desktop. This starts Codex as writer using its configured model at medium reasoning effort and its existing account. Claude credentials are never required or passed to it.

Codex follows `.codex/skills/process-plan/SKILL.md`, using the existing plan, campaign guard and review dispatcher. Its Stop hook is `.codex/hooks.json`; approve this project's hook in Codex after changing it. Its reviewer route is `codex -> carbon`, preserving the project's review schedule. Only one writer may own the tree. A stopped or crashed campaign is not restarted by a background service.

The owner authorised Codex as an additional campaign writer on 2026-11-14. Existing Claude and Carbon launchers remain available. The Codex-specific session and timer rules in its process-plan skill take precedence over the Claude-specific examples in the shared workflow documents.

Codex's independent reviewer is Orchestrator (Carbon), pinned as `reviewers.carbon` with `cli = "agy"` and `model = "gemini-pro-orchestrator"`. The `claude` and `agy` writer routes still use Astra. The shared three-pass schedule retains every lens, `blocking = ["P1", "P2"]` and `pass_cap = 33`, but sets no effort on any pass because Orchestrator rejects scheduled effort overrides. This also means scheduled Astra reviews use the Codex CLI's configured effort, not forced `medium`: with a schedule, an absent step effort does not inherit `reviewers.astra.effort`. That entry remains `medium` for use without a schedule.

Validate with `python scripts/review_pin.py --check` and `python scripts/review-dispatch.py --check-pin`. Run live checks through the dispatcher with `--writer codex` and a bounded `--timeout`. A timeout, empty response, blocked response or malformed verdict is no review and never approval. Reverting the model and restoring the four scheduled effort entries reverses this pin change; historical section receipts keep their candidate's pin.
