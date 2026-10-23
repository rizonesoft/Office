# Product principles

Owner, 2026-10-23: "We are not just creating another clone, we are building a better product. We are not scared to take on the giants and do things better. We do not just implement a feature, we optimise it, we think of ways to improve it, and we blow the competition away. When people use our software, they should think, 'how is this possible'. We do not take shortcuts or workarounds and we are not scared of something being difficult or complicated."

This file turns that into rules a plan, a build and a review can check. Every TODO section, every completion review and every review round reads it.

## Parity is the floor

Every inventoried command works where users expect it, with its shortcut and key tip, and Office files round-trip without loss. Familiarity is a feature: we never move a user's habit without a reason recorded in `design/SPEC.md`. Everything below is built on top of that floor, never instead of it.

## Better is measured

- **Faster than Office on the same PC.** D03 T01 §29 measures Office's own times on this PC for a fixed workload set (cold start, opening and saving large files, recalculation, scrolling, search). Each of our apps must beat every one of those numbers, and aims for half of Office's time. A budget is a test that fails, run in CI or on this PC, never a hope.
- **Instant feels instant.** Typing, scrolling, selection and resizing never drop a frame at 60 frames per second on the reference hardware, whatever the document size.
- **Never lose work.** Every write is atomic, recovery is automatic, and undo reaches as far back as the user needs.

## Every feature asks what better looks like

Before a section is built, its completion review asks two questions: is the feature whole, and does it merely copy Office where a better result is in reach? Better means one or more of:

- fewer steps for the same result, and smarter defaults;
- clearer feedback: errors that say what went wrong and how to fix it, previews before commitment;
- more capability at no cost in familiarity (a better algorithm, a richer option, no artificial limit);
- higher fidelity and reliability (files that open exactly as they were, operations that cannot corrupt);
- speed and responsiveness beyond the budget.

Each app domain also plans its signature improvements: features Office lacks or does poorly, found from what its users complain about most, each with an acceptance test that proves the improvement.

## No shortcuts

The hard version is the plan. A workaround, a filter that hides a problem, a stub, a disabled control or a "good enough" algorithm where a better one is known is not done. When something is genuinely blocked, it is filed with its owner, never papered over.
