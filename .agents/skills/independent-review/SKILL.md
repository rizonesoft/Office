---
name: independent-review
description: Get an independent review of your own work from the reviewer pinned in .conclave/reviewers.toml (GPT-6 Astra, failing over to Gemini 4 then Sonnet 5.5) through scripts/review-dispatch.py, then verify and act on every finding. Use before calling a nontrivial change done, before a commit that ships, or when a TODO section needs its review round.
---

# Independent review

Your own review is not enough for a nontrivial change: a different model reviews it. `.conclave/reviewers.toml` names who reviews whose work, and `scripts/review-dispatch.py` runs the round and fails over when a reviewer is unavailable.

| Work written by | Reviewed by, in failover order |
| --- | --- |
| Claude or Gemini | GPT-6 Astra, then Gemini 4, then Sonnet 5.5 |
| Codex | Gemini 4, then Sonnet 5.5 (Astra never reviews Astra) |

## Steps

1. Review your own change first and fix what you find.
2. Write the review prompt to a scratch file, not the repository, from `docs/review-round-prompt.md`: name the candidate commit or range, the governing documents, and the lenses that apply.
3. Run the round, naming yourself as the writer (`claude`, `codex` or `gemini`):

   ```bash
   python3 scripts/review-dispatch.py --writer claude --prompt <scratch>/review-prompt.md --record docs/reviews/<topic>.md
   ```

   On Windows use `python` instead of `python3`; the command is otherwise the same.
4. Read the review. Verify every finding against the code before acting: fix what is real, and record why anything else is not.
5. Commit fixes as new commits and run another round on the new tip, up to 3 rounds. A unit that needs patching three rounds running gets re-thought, not patched again.

## Rules

- The dispatcher's JSON output and the `## Round N` section it appends are the evidence. A verdict with no record is an opinion.
- Exit 1 means no reviewer returned a review. That is never an approval: say so, and do not ship on it.
- Reviewers run read-only. Never pass a reviewer a secret, and never ask it to edit files.
- Change reviewers only in `.conclave/reviewers.toml`, never by calling a model directly.
