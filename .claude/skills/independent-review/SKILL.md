---
name: independent-review
description: Get an independent review of your own work from the reviewer pinned in .conclave/reviewers.toml (one reviewer of a different model family from yours, no fallback) through scripts/review-dispatch.py, then verify and act on every finding. Use before calling a nontrivial change done, before a commit that ships, or when a TODO section needs its review round.
---

# Independent review

Your own review is not enough for a nontrivial change: a different model reviews it. `.conclave/reviewers.toml` names the reviewer, and `scripts/review-dispatch.py` runs the round. When that reviewer is unavailable there is no review this round: no other reviewer runs.

Claude Code (Opus 5.5) is the only writer, and its work is reviewed by GPT-6.1 Sol through the Codex CLI at xhigh effort (owner decisions 2026-10-22 and 2026-10-23). The pin accepts only that one route, a reviewer of another model family with no fallback, and `scripts/tests/test_review_dispatch.py` holds it there.

## Steps

1. Review your own change first and fix what you find.
2. Write the review prompt to a scratch file, not the repository, from `docs/review-round-prompt.md`: name the candidate commit or range, the governing documents, and the lenses that apply.
3. Run the round; the writer is always `claude`:

   ```bash
   python3 scripts/review-dispatch.py --writer claude --prompt <scratch>/review-prompt.md --record docs/reviews/<topic>.md
   ```

   On Windows use `python` instead of `python3`; the command is otherwise the same.
4. Read the review. Verify every finding against the code before acting: fix what is real, and record why anything else is not.
5. Commit fixes as new commits and run another round on the new tip, up to 33 rounds (22 before 2026-10-23); from round 9 on, a round whose findings are all `P3` or advisory ends the loop and its findings are filed as follow-up work. A unit that needs patching three rounds running gets re-thought, not patched again.

## Rules

- The dispatcher's JSON output and the `## Round N` section it appends are the evidence. A verdict with no record is an opinion.
- Exit 1 means no reviewer returned a review. That is never an approval: say so, and do not ship on it.
- A reviewer that could not reach the work (its sandbox could not read the repository) replies `OVERALL: blocked`, and the round records no review. If its sandbox keeps failing, put the diff in the prompt.
- Reviewers run read-only. Never pass a reviewer a secret, and never ask it to edit files.
- Change reviewers only in `.conclave/reviewers.toml`, never by calling a model directly.
