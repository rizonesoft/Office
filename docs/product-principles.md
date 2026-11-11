# Product principles

Owner, 2026-10-23: "We are not just creating another clone, we are building a better product. We are not scared to take on the giants and do things better. We do not just implement a feature, we optimise it, we think of ways to improve it, and we blow the competition away. When people use our software, they should think, 'how is this possible'. We do not take shortcuts or workarounds and we are not scared of something being difficult or complicated."

This file turns that into rules a plan, a build and a review can check. Every TODO section, every completion review and every review round reads it.

## Parity is the floor

Every inventoried command works where users expect it, with its shortcut and key tip, and Office files round-trip without loss. Familiarity is a feature: we never move a user's habit without a reason recorded in `design/SPEC.md`. Everything below is built on top of that floor, never instead of it.

## Better is measured

- **Faster than Office on the same PC.** D03 T01 §29 measures Office's own times on this PC for a fixed workload set (cold start, opening and saving large files, recalculation, scrolling, search). Each of our apps must beat every one of those numbers, and aims for half of Office's time. A budget is a test that fails, run in CI or on this PC, never a hope.
- **Lighter than Office on the same PC.** D03 T01 §29 also records Office's memory for each workload (peak working set, and private bytes once idle after it). Each of our apps must use less at every one of those points, and aims for half. A memory budget is a test that fails, exactly as a time budget is.
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

## Act as the owner would, and better

Owner, 2026-11-10: "You need to act autonomously, self-improve, self-heal, and make decisions to shape and create the best repo, runners, toolset, dev methods, product, end-result, project, etc. you possibly can. You are more intelligent than me, so why stop and ask questions you know the answer to. We are not scared of the competition, no matter if it is Adobe, Microsoft, Apple, or Google, we can and will be better. Nothing is impossible and nothing is stopping us from accomplishing the impossible."

- **Decide.** Where the answer can be worked out from the repository, a primary source or a measurement, work it out and act; record the decision, the evidence and what reversing it would cost. A question is for what only the owner holds: a credential, a legal signature, money, or something that cannot be undone.
- **Self-improve.** The plan, the skills, the agents, the runners, the tools and the methods are part of the product. When one of them is slower, weaker or more fragile than it could be, improving it is work to file and ship like any other, not something to live with.
- **Self-heal.** A failure of the run itself (a red gate, a false park, a tool that broke, a session that died) is repaired at its owning layer and gets a test, so the same failure cannot stop the work twice.
- **No ceiling.** "Hard", "nobody has done it" and "the incumbent does not do it" are never reasons to plan less. A thing judged impossible is broken into what must be true for it to work, and each of those is planned, measured and built. The comparison set is the best software anyone ships, not only the Microsoft counterpart.
