---
schema_version: 1
id: lessons-and-agent-ledger
domain: 00-workspace
status: active
title: "TODO-05 -- Lessons"
---

# TODO-05 -- Lessons

> **Goal:** What this project has already learned reaches whoever does the next piece of work. Every lesson is a small reviewed file in git, taken only from a verified source (a review finding that was confirmed and fixed, or an owner decision), found through a derived SQLite index, and handed to the main loop as the few lessons that match the paths and the kind of work in front of it. Agents read lessons and never write them.

> **Current state:** Measured 2026-11-10. Nothing is carried from one piece of work to the next except what `AGENTS.md`, the skills and the TODO sections say: every agent, and every new session, starts knowing none of what earlier reviews found. The raw material exists: `docs/reviews/` holds 91 review records with 728 findings tagged `P1` or `P2`, and the same faults return (five rounds on 2026-11-10 found five faults in one hand-written git procedure, `docs/reviews/orchestration-2026-11-10.md`). No lesson file, index or ledger exists, and `docs/lessons/` does not exist. Claude Code's own per-agent memory is refused by `scripts/verify-agent-tiers.mjs` because it gives an agent Write and Edit, and because notes an agent writes for itself are reviewed by nobody. Python's `sqlite3` on this PC is SQLite 3.50.4 with FTS5. The owner chose files in git with a SQLite index over a vector database with embeddings on 2026-11-10; embeddings are not part of this file and are added later only if a lesson that exists is shown not to be found. **Scale (owner, 2026-11-10: it must still work on day 300):** the plan will hold thousands of sections, each with several review rounds, so this file is built for tens of thousands of findings, thousands of lessons and tens of thousands of packets: no file grows without bound (triage is one file per review record, the ledger one file per month), a query stays a few lessons however many match (ranked by how specific and how proven a lesson is, §2), the number of active lessons per area has a ceiling that forces them to be merged or turned into checks (§8), a lesson whose paths no longer exist is refused (§1), and the ranking step is one function so a second ranker can be added without changing the store.

## Inputs

- `docs/reviews/**/*.md`: the review records the first lessons are taken from (§3), in the form `scripts/review-dispatch.py` writes (`## Round N`, findings tagged `P1`, `P2` or `P3` with `file:line`).
- `AGENTS.md`, Subagents: the reader fleet and the rule that an agent that errs is removed.
- `scripts/lib/todo_graph.py`: the pattern for a derived, ignored cache under `build/` rebuilt from Markdown, which §2 follows.

## Outcome

- `python scripts/lessons.py check` exits 0 over `docs/lessons/`, and refuses a lesson with no source, an unknown field or a source file that does not exist.
- `python scripts/lessons.py query --path <path> --role <role>` prints at most five lessons, the same ones in the same order on every run, from `build/lessons.sqlite`.
- A section run reads the lessons for its paths before it builds.

**Adjacency:** all=not-applicable (developer tooling for the people and agents building the suite; no product records, settings or user documents)

**Adjacency rationale:** Lessons describe how this repository is built. They hold no user data, so none of the nine product keys applies.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Lesson files and their checker | -- | [x] |
| 2 | §2 | Lesson index and query | §1 | [x] |
| 3 | §3 | First lessons from the review records | §1, §2 | [x] |
| 4 | §4 | Section runs read their lessons | §2, §3 | [x] |
| 5 | §8 | Lesson upkeep at scale | §2, §3 | [ ] |
| 6 | §9 | Triage covers every review pass | §3 | [ ] |

## 1. Lesson Files and Their Checker

> **Started:** 2026-11-12T07:29:55Z

A lesson is one small Markdown file a person can read and a reviewer can refuse. The checker is what keeps the store trustworthy: nothing enters without a source, and nothing an agent wrote for itself is a lesson.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Define the lesson file in `docs/lessons/README.md`. Done when: the README states every field and the rules below.
2. Write `scripts/lessons.py check`. Done when: each rule below has a fixture test that fails without it.

- [x] Write `docs/lessons/README.md`: a lesson is `docs/lessons/<id>.md` with frontmatter holding `id` (kebab-case, equal to the file name), `applies` (one or more path globs, comma separated, or `*`), `topics` (comma-separated words from a list the README keeps), `roles` (`all`, or any of `main`, `principal-implementer`; **Corrected 2026-11-11:** this also listed `section-writer`, removed that day by decision 40; **Corrected 2026-11-12** (plan review gap 3, P2): `principal-implementer` is gone too, since no agent writes, so the roles are `all`, `main` and `reader` (the Sonnet readers), and a test refuses both removed writer roles), `source` (a repository path to a review record with `#round-N`, or `owner:<date>`; **Corrected 2026-11-12:** the forms are `<record>#round-N/finding-K` with a `fix` commit, or `decision-<N>`, as the source item below states), `added` (a date) and `status` (`active` or `retired`), and with `retired_by` (the check, test or script that now enforces it) required when retired; the body is one paragraph of at most 600 characters saying what goes wrong and what to do instead. Done when: `python scripts/check-design-doc.py docs/lessons/README.md --require Fields --require Rules` exits 0. Cheaper substitute: free-form notes, which no check can read and no query can match.
- [x] State the rules in the same README: a lesson comes only from a review finding that was confirmed and fixed or from an owner decision; the main loop writes it and commits it like any other change; no agent writes or edits a lesson; a lesson that a check, a test or a script can enforce is retired with `retired_by` once that exists; a lesson shown to be wrong is deleted in a commit that says why. Done when: the README holds each rule.
- [x] Write the reader in `scripts/lib/lessons.py`: parse a lesson file's frontmatter as flat `key: value` lines and its body, refusing an unknown key, a duplicate key, a missing required key and an `id` that differs from the file name. Done when: tests in `scripts/tests/test_lessons.py` show each refusal naming the file and the key. Cheaper substitute: a YAML library, which accepts shapes this file does not allow.
- [x] Refuse in `scripts/lessons.py check` a `source` whose review record is not a file in the repository or whose `#round-N` heading is not in it, and an `owner:` source without a date. Done when: tests show a missing file, a missing round and a bare `owner:` each exiting 1 with the lesson's id. Cheaper substitute: accepting any text as a source, which lets an invented lesson in.
- [x] Refuse a body over 600 characters, an em dash or en dash, a `topics` word that is not in the README's list, a `roles` value outside the list, and a retired lesson without `retired_by`. Done when: one test per rule shows exit 1 and the rule's name.
- [x] Refuse an active lesson with an `applies` glob (other than `*`) that matches no file `git ls-files` lists, naming the glob (**Corrected 2026-11-12**, plan review gap 4, P2: a listed file must also exist in the working tree, so an unstaged deletion counts as gone, tested beside a committed deletion), so a lesson about code that moved or was deleted is updated or retired instead of lingering. Done when: a test with a glob matching nothing exits 1 and the same lesson with `status: retired` passes. Cheaper substitute: keeping every lesson forever, which fills the store with advice about files that are gone.
- [x] Refuse two lessons with the same `id`, and report every problem in one run. Done when: a fixture folder with three faults in two files prints all three and exits 1.
- [x] Refuse every value the README does not allow: an empty value, an `id` that is not kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`), a `status` other than `active` or `retired`, an `added` that is not a real `YYYY-MM-DD` date, an empty `retired_by` on a retired lesson, and a body that is empty or more than one paragraph. Done when: one fixture per value exits 1 naming the lesson and the key. **Corrected 2026-11-12:** added after the plan review (gap 1, P1).
- [x] Make a source point at evidence, not just a file: a review source is `<record>#round-N/finding-K` with a `fix` key holding the commit that fixed it, and the checker requires the record's `## Round N` heading, a finding numbered `K` under it, and `fix` naming a commit that is an ancestor of `HEAD`; an owner source is `decision-<N>`, a numbered decision of `docs/specs/2026-10-23-campaign-scope-design.md` that the checker finds. Whether the finding was confirmed and the lesson follows from it is the reviewer's judgment, which the checker does not attempt. Done when: fixtures with a missing finding, a `fix` that is not a commit, a commit off `HEAD`'s history and a decision number the spec does not hold each exit 1, and one of each form passes. **Corrected 2026-11-12:** replaces the bare `#round-N` and `owner:<date>` forms after the plan review (gap 2, P1).
- [x] Prove acceptance as well as refusal: active fixtures of both source forms pass, the reader returns every field and the body exactly, and `check` over a folder mixing valid lessons, `README.md` and a `triage/` folder reads only the lessons (neither of the other two is a lesson) and exits 0. Done when: those tests pass, and fail with the reader dropping a value. **Corrected 2026-11-12:** added after the plan review (gap 5, P2).
- [x] Add `python scripts/lessons.py check` to the `gates` job of `.github/workflows/ci.yml` and to the verification commands in `AGENTS.md`. Done when: both name the command and the pushed run shows it passing.
- [x] Commit: `lessons: define lesson files and check them`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_lessons.py"` passes with the tests named above among them, and `python scripts/lessons.py check` exits 0 on the repository.

> **Verified:** 2026-11-12 | §1 | 204922d7b08bad0e558e205dd2218d641f72e9de
> **Review:** `docs/reviews/d00-t05-s1.json`

## 2. Lesson Index and Query

> **Started:** 2026-11-12T11:55:52Z

The files are the truth; the index is a cache that makes them findable. A query returns the same few lessons in the same order every time, so what a worker is told never depends on chance.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Build `build/lessons.sqlite` from `docs/lessons/`. Done when: the index holds one row per active lesson and is rebuilt when a lesson file changes.
2. Query it by path, role, topic and text. Done when: the fixture queries below return the stated lessons in the stated order.

- [x] Write `build_index()` in `scripts/lib/lessons.py`: read every lesson through the §1 reader, and write `build/lessons.sqlite` (a table of lessons, a table of their globs, and an FTS5 table over the bodies) to a temporary file that replaces the old one with `os.replace`, with a digest of the lesson files stored in it. Done when: a test shows one row per active fixture lesson, none for a retired one, and no leftover temporary file. Cheaper substitute: writing the database in place, which leaves half an index after an interrupted run.
- [x] Rebuild the index in `query` whenever the stored digest differs from the files' digest or the database is missing or unreadable. Done when: a test edits a lesson file, queries, and gets the new text without calling `build` itself.
- [x] Add `query` to `scripts/lessons.py` with `--path` (repeatable), `--role`, `--topic` (repeatable), `--text` and `--limit` (default 5, at most 10): a lesson matches when its `roles` include the role or `all` and one of its globs matches a path, or one of its topics is asked for, or its body matches the text. Done when: a test over six fixture lessons returns exactly the expected ids for each of the four kinds of match. Cheaper substitute: returning every lesson, which rebuilds the large context the lessons are meant to save.
- [x] Order the result in one function, `rank()` in `scripts/lib/lessons.py`, that every query goes through: a lesson whose glob matches a path first (the longest glob first, so the most specific lesson wins), then a topic match, then a text match by FTS5 rank; within each, a lesson with more findings behind it in the triage files (§3) before one with fewer, then the newer `added` date, then `id`; `applies: *` counts as the shortest glob. **Corrected 2026-11-12:** raw length misranks patterns (`scripts/*.py` is as long as `scripts/a.py`, and `scripts/**/*.py` longer than both), so the measure is `specificity()`: a glob's literal characters less its wildcard characters, which puts an exact path above any pattern over it and `*` last. Done when: a test asserts the exact order twice in a row and across a rebuild, and a test with 5,000 generated fixture lessons of which 300 match one path returns the five most specific and best evidenced in under two seconds. Cheaper substitute: ordering by `id`, which is arbitrary once hundreds of lessons match one path.
- [x] Print with `--why` the reason each returned lesson ranked where it did (the glob, the topic or the text that matched and its evidence count), and the number of matching lessons that were not returned. Done when: a test asserts both, so a lesson that exists and was not shown can be seen to have matched.
- [x] Print each lesson as its id, its source and its body, and with `--json` as an array of objects. Done when: tests assert both forms.
- [x] Refuse `--limit` above 10 and a `--role` outside the list with exit 2. Done when: tests show both.
- [x] Make the match exactly `(the role is in the lesson's roles, or they are all) AND (a glob matches a path OR a topic is asked for OR the body matches the text)`, with each lesson returned once however many ways it matched, counted before the limit. Done when: tests show a wrong-role lesson left out on each of the three routes, combined selectors, repeated `--path` and `--topic`, and one lesson matching three ways returned once. **Corrected 2026-11-12:** the query item's wording let a topic or text match skip the role (plan review gap 1, P1).
- [x] Build the index only from a store that passes every rule of `check` (§1): the rules move into `scripts/lib/lessons.py` so `check` and the index share them, and a store with any problem makes `query` print the problems and exit 1 with the earlier index file left as it was and no results shown. Done when: tests with a structurally broken lesson and with a well-formed lesson breaking a value rule both show exit 1, the problem, and the index file unchanged. **Corrected 2026-11-12:** added after the plan review (gap 2, P1).
- [x] Define the evidence behind a lesson here, since §3 writes the triage files later: it is the number of lines, in the files under `docs/lessons/triage/`, whose disposition is `lesson:<id>` for that lesson, and zero when there is no such file. The digest the index stores covers the triage files as well as the lessons, so a changed disposition rebuilds it. Done when: a test changes only a triage line and the next query's order and `--why` count change with no rebuild called. **Corrected 2026-11-12:** added after the plan review (gap 3, P1).
- [x] Prove the replacement and the recovery: a missing or corrupt database is rebuilt; a lesson added, deleted or retired changes the next query; and a failed write or replace leaves the earlier database, no temporary file, and exit 1 with the reason. Done when: tests cover each. **Corrected 2026-11-12:** added after the plan review (gap 4, P2).
- [x] Settle the command line's edges: `--role` defaults to `main`; a query with no `--path`, `--topic` or `--text` is refused with exit 2; `--limit` is 1 to 10; `--text` is literal words (each word must appear; punctuation and FTS syntax in it are text, never an expression); no match prints nothing and exits 0, and `[]` with `--json`. Done when: tests cover each, including text holding quotes, `*` and `NEAR`. **Corrected 2026-11-12:** added after the plan review (gap 5, P2).
- [x] With `--why --json` keep standard output one JSON array: each object gains a `why` field, and the count of matching lessons not returned goes to standard error. Done when: a test parses standard output as JSON and reads the count from standard error. **Corrected 2026-11-12:** added after the plan review (gap 6, P2).
- [x] Prove the command end to end: a test runs `scripts/lessons.py query` as a process over a fixture store with known matches and asserts the exact ids, order, bodies and the limit, then again from the stored index, and a separate test shows an empty store exiting 0 with no output. Done when: both pass. **Corrected 2026-11-12:** the checkpoint's bare exit 0 would pass an empty stub (plan review gap 7, P2).
- [x] Commit: `lessons: index the lesson files and query them`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_lessons.py"` passes, and `python scripts/lessons.py query --path scripts/x.py --role main` exits 0.

> **Verified:** 2026-11-12 | §2 | 05ced2b9606dd58c6d2239dc157ab75b575f10b3
> **Review:** `docs/reviews/d00-t05-s2.json`

## 3. First Lessons From the Review Records

> **Started:** 2026-11-12T12:18:10Z

The store starts with what the reviews already taught. A script lists the findings; the main loop, and nobody else, decides which of them are lessons, because that is judgment about what will recur.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. List the findings to triage. Done when: `python scripts/lessons.py candidates` prints every `P1` and `P2` finding of the chosen records.
2. Triage them and write the lessons. Done when: every listed finding has a disposition and `python scripts/lessons.py check` exits 0.

- [x] Add `candidates` to `scripts/lessons.py`: for the review records given (or all under `docs/reviews/`), print each finding tagged `P1` or `P2` with its record, round, `file:line` and first sentence, and with `--untriaged` only those with no line in the record's triage file: the triage of `docs/reviews/<path>.md` is `docs/lessons/triage/<path>.md`, one file per review record, so no file grows with the project. Done when: a test over a fixture record with two tagged findings and one `P3` prints the two. **Corrected 2026-11-12:** a finding is identified by its place among its round's findings, not its printed number, because older records restart the numbers under each lens (82 of the first 1,003 findings share a printed number within their round); the writer's notes after a round's `OVERALL:` line repeat findings and are not counted.
- [x] Triage the findings of the ten sections with the most review rounds (`python scripts/todo-graph.py query rounds`) and of `docs/reviews/orchestration-2026-11-10.md` in their triage files under `docs/lessons/triage/`: one line per finding with its round and number and one disposition, `lesson:<id>` (it can recur and no check stops it), `enforced:<check or test>` (a check now stops it) or `one-off` with a reason. **Corrected 2026-11-12:** the line's form is the one §2's evidence count reads, `round N finding K: <disposition> [reason]` (the word after the first colon is the disposition), and a lesson written from a finding cites it as §1 requires: `source: <record>#round-N/finding-K` with `fix` naming the commit that fixed it. Done when: `python scripts/lessons.py candidates --untriaged <those records>` prints nothing. Cheaper substitute: writing lessons from memory of the reviews, which keeps the vivid findings and loses the frequent ones.
- [x] Write one lesson file for each `lesson:<id>` in the triage, several findings of one kind sharing one lesson, each citing the record and round of its clearest finding. Done when: every `lesson:<id>` names a file in `docs/lessons/` and `python scripts/lessons.py check` exits 0.
- [x] Make `python scripts/lessons.py check` refuse a `lesson:<id>` in any file under `docs/lessons/triage/` that names no lesson file, and a triage file whose review record does not exist. Done when: a test with such a line exits 1 naming it.
- [x] Record in the commit body how many findings were triaged and how many became lessons, were already enforced, or were one-off. Done when: the three counts add up to the number `candidates` printed.
- [x] Prove `--untriaged` keeps what is outstanding: a fixture with two records, each with findings numbered alike in two rounds, part of them triaged, prints exactly the rest (record, round and number); removing a disposition makes its finding reappear; and the extraction reads the three tag forms the records use, `**[P1] ...**`, `**P1, ...**` and `**P1** ...`. Done when: those tests pass. **Corrected 2026-11-12:** added after the plan review (gap 1, P1).
- [x] Check every triage line in `check`, and let `--untriaged` count only a valid one: the finding must exist in the record at that round and number; a finding has one line (a second, or a conflicting one, is refused); the disposition is `lesson:<id>` naming a lesson file, `enforced:<path>` naming a file the repository holds, or `one-off` followed by a reason; anything else is refused. Done when: one refusal test per rule exits 1 naming the triage file and line, and an invalid line leaves its finding in `--untriaged`. **Corrected 2026-11-12:** added after the plan review (gap 2, P2).
- [x] Fail loudly on input that cannot be read: a record named on the command line that is missing, unreadable or holds no review pass, and a triage file that cannot be read, each give a line naming the file and exit 1, so empty output never hides skipped input; the checkpoint is exit 0 and empty output together. Done when: tests cover each. **Corrected 2026-11-12:** added after the plan review (gap 3, P2).
- [x] Commit: `lessons: write the first lessons from the review records`

**Test checkpoint:** `python scripts/lessons.py check` exits 0 with at least one lesson in `docs/lessons/`, and `python scripts/lessons.py candidates --untriaged` over the triaged records prints nothing.

> **Verified:** 2026-11-12 | §3 | 2253a4440569adcb093ff44322aceebac68121e2
> **Review:** `docs/reviews/d00-t05-s3.json`

## 4. Section Runs Read Their Lessons

> **Started:** 2026-11-12T12:52:19Z

A lesson only helps if it is in front of whoever is about to repeat the mistake. The main loop reads the lessons for a section's paths before it builds, and turns every confirmed finding of the section's own review into a lesson, an enforced check or a one-off before the section stamps.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Add the read step to `process-todo-section`. Done when: step 2 names the command and what to do with its output.
2. Add the triage step to `review-todo-section`. Done when: the stamp step is preceded by it.

- [x] Add to step 2 of `.claude/skills/process-todo-section/SKILL.md`: run `python scripts/lessons.py query --role main --path <each path the section names>` and read every lesson it prints before building. Done when: the step names the command, and `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` still passes.
- [x] Add to `.claude/skills/review-todo-section/SKILL.md`, before the stamp: for every finding of the section's rounds that was confirmed and fixed, add a line to the record's triage file under `docs/lessons/triage/` with its disposition (§3), and write the lesson file where the disposition is `lesson:<id>`. Done when: the skill names the file, the three dispositions and `python scripts/lessons.py check`.
- [x] Add to the same step: a lesson the section's own work made enforceable (it added the check or test) is retired with `retired_by` in the same commit. Done when: the skill says so.
- [x] Add a test in `scripts/tests/test_skill_ci_gate.py` that both skills name `scripts/lessons.py`. Done when: the test fails when either mention is removed.
- [x] Hold the obligations, not the mention: tests in `scripts/tests/test_skill_ci_gate.py` fail when the read step, its handling of a failed query, the triage step, its place before the completion review, or the retirement rule is removed from the skills or moved after the pass that reviews the candidate; and a walkthrough test in `scripts/tests/test_lessons.py` writes dispositions for a fixture record as the skill says, shows `check` passing, the new lesson returned by the next query, and a lesson retired with `retired_by` no longer returned. Done when: those tests pass and each fails with its sentence removed. **Corrected 2026-11-12:** added after the plan review (gap 1, P1); the test item above alone would pass on a bare mention.
- [x] Say what each outcome of the read means: exit 0 with lessons is read; exit 0 with none means no lesson applies, which the section's plan-review note records; exit 1 (the store breaks a rule, or the index cannot be written) is repaired first (`python scripts/lessons.py check`, fix what it names) and the query run again until it exits 0, since a failed query has read nothing; exit 2 is a mistake in the command, corrected and rerun. Done when: the skill states the four outcomes and the test holds them. **Corrected 2026-11-12:** added after the plan review (gap 3, P2).
- [x] Put the triage and its lessons in the candidate the last pass reviews: after the round's findings are fixed and before the completion review is dispatched, with `python scripts/lessons.py check` passing and the lines committed; a later pass's fixes are triaged before the next reconciliation; a resumed section runs `candidates --untriaged` on its record and writes only what that prints, never a second line for a finding. Done when: the skill says so and the ordering test holds it. **Corrected 2026-11-12:** replaces the first wording's before the stamp, which could land after the last reviewed candidate (plan review gap 4, P2).
- [x] Triage the findings a round raises; the findings of a plan review, a completion review and a reconciliation are triaged once §9 gives those passes an identity, and the skill says which passes it covers today. Done when: the skill names rounds and points at §9 for the rest. **Corrected 2026-11-12:** every confirmed finding in the first wording reached further than §3's reader does (plan review gap 2, P1); the missing coverage is owned by §9, filed with this correction.
- [x] Commit: `lessons: read them before a section and write them after its review`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` passes with the new test among them.

> **Verified:** 2026-11-12 | §4 | 76899623565bfbb541414b146ae3b1fda6e1d7e0
> **Review:** `docs/reviews/d00-t05-s4.json`

## 8. Lesson Upkeep at Scale

A store that only grows stops working: once hundreds of lessons match one path, the five a worker sees are a small sample and the rest are noise nobody reads. This section keeps the store small enough to stay true on day 300 (owner, 2026-11-10). Each area has a ceiling on active lessons; passing it is not an error to suppress but work to do: lessons about one thing are merged into one, and a lesson a check can enforce becomes that check and retires.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `python scripts/lessons.py report`. Done when: it prints, per area, the active lessons, their evidence and the ceiling.
2. Make upkeep part of closing a phase. Done when: `process-phase` runs the report and acts on it before its closeout.

- [ ] Write `report` in `scripts/lessons.py`: group active lessons by the first two folders of each `applies` glob (`*` is its own group), and print per group the number of active lessons, the number retired, and the lessons sorted by evidence count. Done when: a test over a fixture of three areas prints the three groups with the expected counts.
- [ ] Add `report --check` with a ceiling of 40 active lessons per group (`LESSON_CEILING` in `scripts/lib/lessons.py`): exit 1 naming each group over it. Done when: a fixture group of 41 exits 1 and one of 40 exits 0. Cheaper substitute: raising the query limit as lessons pile up, which hands every worker a longer list and a larger context.
- [ ] List in `report` the lessons that could be merged: two or more active lessons of one group that share a topic and whose globs are equal or nested. Done when: a fixture with two such lessons prints the pair and one with different topics does not.
- [ ] List in `report` the lessons that still failed: an active lesson named by a triage line whose round ran after the lesson's `added` date (the round's `Run:` line in the review record gives the date), which means the same fault was found again although the lesson existed. Done when: a fixture with such a line prints the lesson and the later finding. Such a lesson is rewritten, turned into a check, or deleted as useless; it is never left as it is.
- [ ] Add to the closeout of `.claude/skills/process-phase/SKILL.md`: run `python scripts/lessons.py report --check`; for each group over the ceiling, and for each lesson listed as mergeable or as still failing, merge, retire with `retired_by`, rewrite or delete until the check exits 0, in a commit of its own. Done when: the skill names the command and the four remedies, and a test in `scripts/tests/test_skill_ci_gate.py` fails when the mention is removed.
- [ ] State the ceiling and the four remedies in `docs/lessons/README.md` under a `## Upkeep` heading. Done when: `python scripts/check-design-doc.py docs/lessons/README.md --require Upkeep` exits 0.
- [ ] Commit: `lessons: keep the store small enough to stay true`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_lessons.py"` passes with the report tests among them, and `python scripts/lessons.py report --check` exits 0.

## 9. Triage Covers Every Review Pass

> **Started:** 2026-11-12T13:12:29Z

Filed 2026-11-12 from the plan review of §4 (`docs/reviews/00-workspace/D00-T05-s4.md`, gap 2, P1). §3 identifies a finding by its round, and §1's lesson source by `#round-N/finding-K`. Under the three-pass schedule (owner decision 2026-11-11) a section has one round, and most of its findings come from the plan review, the completion review and the reconciliations, which `round_findings` in `scripts/lib/lessons.py` deliberately leaves out. So a confirmed and fixed finding of those passes cannot be triaged or cited by a lesson today. This section gives every pass an identity.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Read the findings of every pass. Done when: `candidates` lists plan, completion and reconciliation findings beside round findings.
2. Let triage lines and lesson sources name them. Done when: `check` validates both.

- [ ] Extend the reader in `scripts/lib/lessons.py` to every pass of a record: a plan review's findings, a completion review's gap list, and the new findings a reconciliation raises (its `closed` and `open` lines report on earlier gaps and are not findings), each with its place in its pass. Done when: tests over fixture records of each pass, and over three real records of this repository, list exactly the tagged findings.
- [ ] Give each pass an identity in triage lines and lesson sources: `plan finding K`, `round N finding K`, `completion finding K` and `reconciliation N finding K` in a triage file, and `#plan/finding-K`, `#round-N/finding-K`, `#completion/finding-K` and `#reconciliation-N/finding-K` in a lesson's `source`; existing `round` lines and sources stay valid. Done when: `check` accepts each form for a finding that exists and refuses one that does not, and `docs/lessons/README.md` states the forms.
- [ ] List them in `candidates` and `candidates --untriaged`, so a section's own record shows every finding still to triage. Done when: a test over a record holding all four passes prints each pass's findings and drops each as its line is written.
- [ ] Extend `review-todo-section`'s triage step (§4) from the round's findings to every pass's. Done when: the skill names all four passes and `scripts/tests/test_skill_ci_gate.py` holds it.
- [ ] Discover a record by any pass it holds, not only a round: `candidates` with no record named lists a section that so far has only its plan review. Done when: tests show a plan-only record listed both when named and when discovered. **Corrected 2026-11-12:** added after the plan review (gap 1, P2).
- [ ] Number the passes by their place in the record: `reconciliation N` is the Nth `## Reconciliation review` heading from the top, counted whether or not it raised a finding, so a pass appended later never renumbers an earlier one; a plan or completion review is `plan` or `completion` when the record has one and takes the same count (`plan 2`) when a record holds more. Done when: a test with three reconciliations whose findings share numbers shows that triaging one leaves the others outstanding, and that appending a fourth leaves every existing line and lesson source valid. **Corrected 2026-11-12:** added after the plan review (gap 2, P2).
- [ ] Commit: `lessons: triage the findings of every review pass`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_lessons.py"` passes with the pass tests among them, and `python scripts/lessons.py candidates docs/reviews/00-workspace/D00-T05-s4.md` lists that record's plan review findings.
## Verification

- `python scripts/lessons.py check` exits 0 and CI runs it.
- `python scripts/lessons.py query --role main --path scripts/lib/todo_graph.py` prints at most five lessons, identical on two runs.
- `process-todo-section` and `review-todo-section` both name `scripts/lessons.py`.
- `python scripts/lessons.py report --check` exits 0, and the 5,000-lesson test of §2 passes inside its time limit.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
