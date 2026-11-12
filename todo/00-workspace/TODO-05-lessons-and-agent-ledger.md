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
| 1 | §1 | Lesson files and their checker | -- | [ ] |
| 2 | §2 | Lesson index and query | §1 | [ ] |
| 3 | §3 | First lessons from the review records | §1, §2 | [ ] |
| 4 | §4 | Section runs read their lessons | §2, §3 | [ ] |
| 5 | §8 | Lesson upkeep at scale | §2, §3 | [ ] |

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

## 2. Lesson Index and Query

The files are the truth; the index is a cache that makes them findable. A query returns the same few lessons in the same order every time, so what a worker is told never depends on chance.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Build `build/lessons.sqlite` from `docs/lessons/`. Done when: the index holds one row per active lesson and is rebuilt when a lesson file changes.
2. Query it by path, role, topic and text. Done when: the fixture queries below return the stated lessons in the stated order.

- [ ] Write `build_index()` in `scripts/lib/lessons.py`: read every lesson through the §1 reader, and write `build/lessons.sqlite` (a table of lessons, a table of their globs, and an FTS5 table over the bodies) to a temporary file that replaces the old one with `os.replace`, with a digest of the lesson files stored in it. Done when: a test shows one row per active fixture lesson, none for a retired one, and no leftover temporary file. Cheaper substitute: writing the database in place, which leaves half an index after an interrupted run.
- [ ] Rebuild the index in `query` whenever the stored digest differs from the files' digest or the database is missing or unreadable. Done when: a test edits a lesson file, queries, and gets the new text without calling `build` itself.
- [ ] Add `query` to `scripts/lessons.py` with `--path` (repeatable), `--role`, `--topic` (repeatable), `--text` and `--limit` (default 5, at most 10): a lesson matches when its `roles` include the role or `all` and one of its globs matches a path, or one of its topics is asked for, or its body matches the text. Done when: a test over six fixture lessons returns exactly the expected ids for each of the four kinds of match. Cheaper substitute: returning every lesson, which rebuilds the large context the lessons are meant to save.
- [ ] Order the result in one function, `rank()` in `scripts/lib/lessons.py`, that every query goes through: a lesson whose glob matches a path first (the longest glob first, so the most specific lesson wins), then a topic match, then a text match by FTS5 rank; within each, a lesson with more findings behind it in the triage files (§3) before one with fewer, then the newer `added` date, then `id`; `applies: *` counts as the shortest glob. Done when: a test asserts the exact order twice in a row and across a rebuild, and a test with 5,000 generated fixture lessons of which 300 match one path returns the five most specific and best evidenced in under two seconds. Cheaper substitute: ordering by `id`, which is arbitrary once hundreds of lessons match one path.
- [ ] Print with `--why` the reason each returned lesson ranked where it did (the glob, the topic or the text that matched and its evidence count), and the number of matching lessons that were not returned. Done when: a test asserts both, so a lesson that exists and was not shown can be seen to have matched.
- [ ] Print each lesson as its id, its source and its body, and with `--json` as an array of objects. Done when: tests assert both forms.
- [ ] Refuse `--limit` above 10 and a `--role` outside the list with exit 2. Done when: tests show both.
- [ ] Commit: `lessons: index the lesson files and query them`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_lessons.py"` passes, and `python scripts/lessons.py query --path scripts/x.py --role main` exits 0.

## 3. First Lessons From the Review Records

The store starts with what the reviews already taught. A script lists the findings; the main loop, and nobody else, decides which of them are lessons, because that is judgment about what will recur.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. List the findings to triage. Done when: `python scripts/lessons.py candidates` prints every `P1` and `P2` finding of the chosen records.
2. Triage them and write the lessons. Done when: every listed finding has a disposition and `python scripts/lessons.py check` exits 0.

- [ ] Add `candidates` to `scripts/lessons.py`: for the review records given (or all under `docs/reviews/`), print each finding tagged `P1` or `P2` with its record, round, `file:line` and first sentence, and with `--untriaged` only those with no line in the record's triage file: the triage of `docs/reviews/<path>.md` is `docs/lessons/triage/<path>.md`, one file per review record, so no file grows with the project. Done when: a test over a fixture record with two tagged findings and one `P3` prints the two.
- [ ] Triage the findings of the ten sections with the most review rounds (`python scripts/todo-graph.py query rounds`) and of `docs/reviews/orchestration-2026-11-10.md` in their triage files under `docs/lessons/triage/`: one line per finding with its round and number and one disposition, `lesson:<id>` (it can recur and no check stops it), `enforced:<check or test>` (a check now stops it) or `one-off` with a reason. Done when: `python scripts/lessons.py candidates --untriaged <those records>` prints nothing. Cheaper substitute: writing lessons from memory of the reviews, which keeps the vivid findings and loses the frequent ones.
- [ ] Write one lesson file for each `lesson:<id>` in the triage, several findings of one kind sharing one lesson, each citing the record and round of its clearest finding. Done when: every `lesson:<id>` names a file in `docs/lessons/` and `python scripts/lessons.py check` exits 0.
- [ ] Make `python scripts/lessons.py check` refuse a `lesson:<id>` in any file under `docs/lessons/triage/` that names no lesson file, and a triage file whose review record does not exist. Done when: a test with such a line exits 1 naming it.
- [ ] Record in the commit body how many findings were triaged and how many became lessons, were already enforced, or were one-off. Done when: the three counts add up to the number `candidates` printed.
- [ ] Commit: `lessons: write the first lessons from the review records`

**Test checkpoint:** `python scripts/lessons.py check` exits 0 with at least one lesson in `docs/lessons/`, and `python scripts/lessons.py candidates --untriaged` over the triaged records prints nothing.

## 4. Section Runs Read Their Lessons

A lesson only helps if it is in front of whoever is about to repeat the mistake. The main loop reads the lessons for a section's paths before it builds, and turns every confirmed finding of the section's own review into a lesson, an enforced check or a one-off before the section stamps.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Add the read step to `process-todo-section`. Done when: step 2 names the command and what to do with its output.
2. Add the triage step to `review-todo-section`. Done when: the stamp step is preceded by it.

- [ ] Add to step 2 of `.claude/skills/process-todo-section/SKILL.md`: run `python scripts/lessons.py query --role main --path <each path the section names>` and read every lesson it prints before building. Done when: the step names the command, and `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` still passes.
- [ ] Add to `.claude/skills/review-todo-section/SKILL.md`, before the stamp: for every finding of the section's rounds that was confirmed and fixed, add a line to the record's triage file under `docs/lessons/triage/` with its disposition (§3), and write the lesson file where the disposition is `lesson:<id>`. Done when: the skill names the file, the three dispositions and `python scripts/lessons.py check`.
- [ ] Add to the same step: a lesson the section's own work made enforceable (it added the check or test) is retired with `retired_by` in the same commit. Done when: the skill says so.
- [ ] Add a test in `scripts/tests/test_skill_ci_gate.py` that both skills name `scripts/lessons.py`. Done when: the test fails when either mention is removed.
- [ ] Commit: `lessons: read them before a section and write them after its review`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_skill_ci_gate.py"` passes with the new test among them.

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

## Verification

- `python scripts/lessons.py check` exits 0 and CI runs it.
- `python scripts/lessons.py query --role main --path scripts/lib/todo_graph.py` prints at most five lessons, identical on two runs.
- `process-todo-section` and `review-todo-section` both name `scripts/lessons.py`.
- `python scripts/lessons.py report --check` exits 0, and the 5,000-lesson test of §2 passes inside its time limit.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
