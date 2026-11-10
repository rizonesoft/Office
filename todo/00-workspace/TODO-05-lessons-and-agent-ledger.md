---
schema_version: 1
id: lessons-and-agent-ledger
domain: 00-workspace
status: active
title: "TODO-05 -- Lessons and Agent Ledger"
---

# TODO-05 -- Lessons and Agent Ledger

> **Goal:** What this project has already learned reaches whoever does the next piece of work. Every lesson is a small reviewed file in git, taken only from a verified source (a review finding that was confirmed and fixed, or an owner decision), found through a derived SQLite index, and handed to the main loop and to each worker as the few lessons that match the paths and the kind of work in front of them. Agents read lessons and never write them. A ledger records how each worker's packets ended, and a score built from it tells the main loop which tier to route a kind of work to.

> **Current state:** Measured 2026-11-10. Nothing is carried from one piece of work to the next except what `AGENTS.md`, the skills and the TODO sections say: every agent, and every new session, starts knowing none of what earlier reviews found. The raw material exists: `docs/reviews/` holds 91 review records with 728 findings tagged `P1` or `P2`, and the same faults return (five rounds on 2026-11-10 found five faults in one hand-written git procedure, `docs/reviews/orchestration-2026-11-10.md`). No lesson file, index or ledger exists, and `docs/lessons/` does not exist. Claude Code's own per-agent memory is refused by `scripts/verify-agent-tiers.mjs` because it gives an agent Write and Edit, and because notes an agent writes for itself are reviewed by nobody. Python's `sqlite3` on this PC is SQLite 3.50.4 with FTS5. The owner chose files in git with a SQLite index over a vector database with embeddings on 2026-11-10; embeddings are not part of this file and are added later only if a lesson that exists is shown not to be found. **Scale (owner, 2026-11-10: it must still work on day 300):** the plan will hold thousands of sections, each with several review rounds, so this file is built for tens of thousands of findings, thousands of lessons and tens of thousands of packets: no file grows without bound (triage is one file per review record, the ledger one file per month), a query stays a few lessons however many match (ranked by how specific and how proven a lesson is, §2), the number of active lessons per area has a ceiling that forces them to be merged or turned into checks (§8), a lesson whose paths no longer exist is refused (§1), and the ranking step is one function so a second ranker can be added without changing the store.

## Inputs

- `docs/reviews/**/*.md`: the review records the first lessons are taken from (§3), in the form `scripts/review-dispatch.py` writes (`## Round N`, findings tagged `P1`, `P2` or `P3` with `file:line`).
- `AGENTS.md`, Subagents: the tiers, the work packet and the rule that an agent that errs is removed; §6 and §7 give that rule its evidence.
- `docs/specs/2026-10-23-campaign-scope-design.md`, decisions 25, 27 and 28: workers, the routing ladder, and the three-way measurement whose result decides whether §6 and §7 are built.
- `scripts/lib/todo_graph.py`: the pattern for a derived, ignored cache under `build/` rebuilt from Markdown, which §2 follows.
- -> XREF: T03 §34 -- `scripts/packet.py`, the command §5 extends to attach lessons and §6 extends to record outcomes

## Outcome

- `python scripts/lessons.py check` exits 0 over `docs/lessons/`, and refuses a lesson with no source, an unknown field or a source file that does not exist.
- `python scripts/lessons.py query --path <path> --role <role>` prints at most five lessons, the same ones in the same order on every run, from `build/lessons.sqlite`.
- A section run reads the lessons for its paths before it builds, and a work packet carries the lessons for its paths and its worker's role.
- `python scripts/ledger.py score` prints, per agent, model and kind of work, how many packets were accepted the first time, blocked or rejected.

**Adjacency:** all=not-applicable (developer tooling for the people and agents building the suite; no product records, settings or user documents)

**Adjacency rationale:** Lessons and the ledger describe how this repository is built. They hold no user data, so none of the nine product keys applies.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Lesson files and their checker | -- | [ ] |
| 2 | §2 | Lesson index and query | §1 | [ ] |
| 3 | §3 | First lessons from the review records | §1, §2 | [ ] |
| 4 | §4 | Section runs read their lessons | §2, §3 | [ ] |
| 5 | §5 | Work packets carry their lessons | §2, T03 §34 | [ ] |
| 6 | §6 | Packet outcome ledger | T03 §34 | [ ] |
| 7 | §7 | Agent score from the ledger | §6 | [ ] |
| 8 | §8 | Lesson upkeep at scale | §2, §3 | [ ] |

## 1. Lesson Files and Their Checker

A lesson is one small Markdown file a person can read and a reviewer can refuse. The checker is what keeps the store trustworthy: nothing enters without a source, and nothing an agent wrote for itself is a lesson.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Define the lesson file in `docs/lessons/README.md`. Done when: the README states every field and the rules below.
2. Write `scripts/lessons.py check`. Done when: each rule below has a fixture test that fails without it.

- [ ] Write `docs/lessons/README.md`: a lesson is `docs/lessons/<id>.md` with frontmatter holding `id` (kebab-case, equal to the file name), `applies` (one or more path globs, comma separated, or `*`), `topics` (comma-separated words from a list the README keeps), `roles` (`all`, or any of `main`, `implementer`, `senior-implementer`, `principal-implementer`), `source` (a repository path to a review record with `#round-N`, or `owner:<date>`), `added` (a date) and `status` (`active` or `retired`), and with `retired_by` (the check, test or script that now enforces it) required when retired; the body is one paragraph of at most 600 characters saying what goes wrong and what to do instead. Done when: `python scripts/check-design-doc.py docs/lessons/README.md --require Fields --require Rules` exits 0. Cheaper substitute: free-form notes, which no check can read and no query can match.
- [ ] State the rules in the same README: a lesson comes only from a review finding that was confirmed and fixed or from an owner decision; the main loop writes it and commits it like any other change; no agent writes or edits a lesson; a lesson that a check, a test or a script can enforce is retired with `retired_by` once that exists; a lesson shown to be wrong is deleted in a commit that says why. Done when: the README holds each rule.
- [ ] Write the reader in `scripts/lib/lessons.py`: parse a lesson file's frontmatter as flat `key: value` lines and its body, refusing an unknown key, a duplicate key, a missing required key and an `id` that differs from the file name. Done when: tests in `scripts/tests/test_lessons.py` show each refusal naming the file and the key. Cheaper substitute: a YAML library, which accepts shapes this file does not allow.
- [ ] Refuse in `scripts/lessons.py check` a `source` whose review record is not a file in the repository or whose `#round-N` heading is not in it, and an `owner:` source without a date. Done when: tests show a missing file, a missing round and a bare `owner:` each exiting 1 with the lesson's id. Cheaper substitute: accepting any text as a source, which lets an invented lesson in.
- [ ] Refuse a body over 600 characters, an em dash or en dash, a `topics` word that is not in the README's list, a `roles` value outside the list, and a retired lesson without `retired_by`. Done when: one test per rule shows exit 1 and the rule's name.
- [ ] Refuse an active lesson with an `applies` glob (other than `*`) that matches no file `git ls-files` lists, naming the glob, so a lesson about code that moved or was deleted is updated or retired instead of lingering. Done when: a test with a glob matching nothing exits 1 and the same lesson with `status: retired` passes. Cheaper substitute: keeping every lesson forever, which fills the store with advice about files that are gone.
- [ ] Refuse two lessons with the same `id`, and report every problem in one run. Done when: a fixture folder with three faults in two files prints all three and exits 1.
- [ ] Add `python scripts/lessons.py check` to the `gates` job of `.github/workflows/ci.yml` and to the verification commands in `AGENTS.md`. Done when: both name the command and the pushed run shows it passing.
- [ ] Commit: `lessons: define lesson files and check them`

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

## 5. Work Packets Carry Their Lessons

A worker starts every packet knowing nothing. The packet command attaches the lessons for the packet's paths and the worker's role, so the brief the main loop writes always includes them and the main loop does not have to remember to look.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Make `scripts/packet.py begin` write the packet's lessons. Done when: `begin` with a role and paths writes the matching lessons to a file and prints its path.
2. Tell the workers and the skill. Done when: each worker definition says to read the lessons in its packet first.

- [ ] Add `--role` to `begin` in `scripts/packet.py` and write `build/packet-lessons.md`: the output of the §2 query for the packet's paths and that role, at most five lessons, or the one line `No lessons match this packet.` Done when: tests in `scripts/tests/test_packet.py` show the file with the expected fixture lessons and the one-line form.
- [ ] Record the ids of the attached lessons in `build/packet.json`. Done when: a test reads them back.
- [ ] State in the build step of the Delegation section of `.claude/skills/process-todo-section/SKILL.md` that every worker brief includes the text of `build/packet-lessons.md`. Done when: the step says so and the skill test still passes.
- [ ] Add to each worker definition (`.claude/agents/implementer.md`, `senior-implementer.md`, `principal-implementer.md`): read the lessons in your packet before you change anything, and say in your reply which one applied; never write or edit a file under `docs/lessons/`. Done when: all three hold both sentences and `node scripts/verify-agent-tiers.mjs` passes.
- [ ] Commit: `lessons: attach matching lessons to every work packet`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_packet.py"` passes with the lesson tests among them.

## 6. Packet Outcome Ledger

Whether a tier is good at a kind of work should be read from what happened, not remembered. The packet command already knows how each packet ends; this section makes it write that down. Built only if the three-way measurement keeps the orchestrated way of working (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 28): with no workers there are no packets to record.

**Phase:** 0
**Needs:** owner-decision
**Surface:** no

**Build order:**

1. Append one record per packet outcome to the month's file, `docs/agents/ledger/<YYYY-MM>.jsonl`. Done when: accept, reject and block each write one line, and a packet in a new month starts a new file.

- [ ] Add `--agent`, `--model`, `--effort` and `--kind` (`code`, `test`, `doc` or `fixture`) to `begin` in `scripts/packet.py`, stored in `build/packet.json`; refuse an effort above the tier's ceiling in `AGENTS.md` with exit 2. Done when: tests show the stored values and the refusal for `opus` with `high`.
- [ ] Add `accept` to `scripts/packet.py`: when `show` would exit 0, append one JSON line to `docs/agents/ledger/<YYYY-MM>.jsonl`, the file of the current UTC month, so no ledger file grows past a month and an append never rewrites the project's whole history (the UTC time, the section reference given with `--section`, the packet's name, agent, model, effort, kind, paths, the attached lesson ids and `"outcome": "accepted"` with the attempt number) through a temporary file and `os.replace`, read it back, and stage the ledger with the packet's paths. Done when: a test shows the line and the staged ledger.
- [ ] Make `reject` append the same record with `"outcome": "rejected"` and its `--reason` (`out-of-scope`, `gate-failed`, `wrong` or `blocked`). Done when: tests show one line per reason and exit 2 for a reason outside the list.
- [ ] Count attempts: a packet begun again under the same name and section has the next attempt number. Done when: a test with a rejection then an acceptance shows attempts 1 and 2.
- [ ] Add `python scripts/ledger.py check`, which refuses a ledger line that is not JSON, lacks a field or names an unknown outcome, and add it to the `gates` job of `.github/workflows/ci.yml`. Done when: tests show each refusal with the line number.
- [ ] Commit: `agents: record how every work packet ends`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_packet.py"` passes with the ledger tests among them, and `python scripts/ledger.py check` exits 0.

## 7. Agent Score From the Ledger

The score turns the ledger into a routing aid: which tier finishes which kind of work the first time. It changes where work is sent first. It never changes what is checked: the main loop reads every change, runs every gate and keeps the independent review whatever a score says. Built only if §6 is.

**Phase:** 0
**Needs:** owner-decision
**Surface:** no

**Build order:**

1. Write `scripts/ledger.py score`. Done when: it prints the table below from a fixture ledger.
2. Tell the main loop how to use it. Done when: `AGENTS.md` states the rule.

- [ ] Write `score` in `scripts/ledger.py`: per agent, exact model id and kind, the number of packets, the share accepted on the first attempt, and the counts rejected per reason. Done when: a test over a twelve-line fixture ledger prints the expected numbers. Cheaper substitute: one number per agent, which hides that a tier is good at tests and poor at parsers.
- [ ] Keep model versions apart: a row is keyed by the exact model id, so a new model release starts with no history. Done when: a fixture with two ids for one agent prints two rows.
- [ ] Mark a row `too few` below ten packets and give no share for it. Done when: a fixture row of nine packets prints the mark.
- [ ] Add `advise --kind <kind>`, printing the cheapest tier whose row for that kind has at least ten packets and a first-attempt share of at least 0.8, or `no advice` when none has. Done when: tests show both outcomes and the tier order of `AGENTS.md`.
- [ ] State in the Subagents section of `AGENTS.md`: the main loop may read `python scripts/ledger.py advise` when routing a packet; the score never reduces the reading of a change, a gate or the independent review; no brief, packet or worker definition ever contains a score. Done when: the section holds the three statements.
- [ ] Add a test in `scripts/tests/test_packet.py` that `scripts/packet.py` opens no file under `docs/agents/ledger/` for reading while it writes `build/packet-lessons.md`, so no score can reach a worker's brief. Done when: the test fails when such a read is added.
- [ ] Read the ledger in `score` one month file at a time and accept `--since <YYYY-MM>`, defaulting to the last twelve months. Done when: a test with 40,000 generated lines over 14 months prints the table in under five seconds and ignores the two oldest months by default.
- [ ] Commit: `agents: score each tier by kind of work from the ledger`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_ledger.py"` passes, and `python scripts/ledger.py score` exits 0.

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
- `python scripts/lessons.py report --check` exits 0, and the 5,000-lesson and 40,000-line tests of §2 and §7 pass inside their time limits.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
