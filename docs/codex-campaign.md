# Codex campaign

Run `scripts/start-campaign.ps1 -Runner codex`, or open "Office Codex campaign" on the Windows Desktop. This starts Codex as writer using its configured model at medium reasoning effort and its existing account. Claude credentials are never required or passed to it.

Codex follows `.codex/skills/process-plan/SKILL.md`, using the existing plan, campaign guard and review dispatcher. Its Stop hook is `.codex/hooks.json`; approve this project's hook in Codex after changing it. Its reviewer route is `codex -> carbon`, preserving the project's review schedule. Only one writer may own the tree. A stopped or crashed campaign is not restarted by a background service.

The owner authorised Codex as an additional campaign writer on 2026-11-14. Existing Claude and Carbon launchers remain available. The Codex-specific session and timer rules in its process-plan skill take precedence over the Claude-specific examples in the shared workflow documents.
