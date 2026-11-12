# Lessons

A lesson is one small Markdown file that says what went wrong once and what to do instead, so the next session does not repeat it. A person can read it in a minute, a reviewer can refuse it, and `python scripts/lessons.py check` refuses one that breaks the rules below (D00 T05 §1). Every `*.md` file in this folder except this README is a lesson; the `triage/` folder holds candidates that are not lessons yet and is never read as one.

## Fields

A lesson is `docs/lessons/<id>.md`: frontmatter between two `---` lines, written as flat `key: value` lines (no nesting, no lists, no quotes needed), then the body.

| Key | Required | Value |
| --- | --- | --- |
| `id` | yes | kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`), equal to the file name without `.md` |
| `applies` | yes | one or more path globs, comma separated, or `*` for every file |
| `topics` | yes | one or more words from the Topics list below, comma separated |
| `roles` | yes | `all`, or `main` (the lead session), `reader` (the Sonnet readers) or both, comma separated |
| `source` | yes | `<record>#<pass>/finding-K` (a review finding; passes below) or `decision-<N>` (an owner decision) |
| `fix` | with a review source | the commit that fixed the finding, a full or short SHA in the history of `HEAD` |
| `added` | yes | the date the lesson was written, `YYYY-MM-DD` |
| `status` | yes | `active` or `retired` |
| `retired_by` | when retired | the check, test or script that now enforces the lesson, as a repository path |
| `revised` | no | the date the lesson was last rewritten, `YYYY-MM-DD`, on or after `added` |
| `apart` | no | ids of lessons this one is deliberately kept separate from, comma separated |

A glob is read as Python's `PurePath.full_match` reads it, against repository paths with forward slashes: `*` stays within one folder and `**` crosses folders, so `scripts/**/*.py` is every Python file under `scripts/`.

The body is one paragraph of at most 600 characters: what goes wrong, and what to do instead. No key may be empty, unknown or given twice.

A review source names a record under `docs/reviews/`, a pass in it and the finding `K` of that pass. The pass is `round-N` (the `## Round N` heading), `plan` (the plan review), `completion` (the completion review) or `reconciliation-N` (the Nth `## Reconciliation review` heading from the top of the record, counted whether or not it raised a finding, so a pass appended later never renumbers an earlier one); a record holding a second plan or completion review names it `plan-2` or `completion-2`. `K` is the finding's place among the findings of its pass (D00 T05 §9). An owner source names decision `N` of `docs/specs/2026-10-23-campaign-scope-design.md`. The checker proves the record, the round, the finding, the commit and the decision exist; whether the finding was confirmed and the lesson follows from it is the reviewer's judgment.

## Rules

- A lesson comes only from a review finding that was confirmed and fixed, or from an owner decision. Nothing an agent noticed about itself is a lesson.
- The main session writes a lesson and commits it like any other change. No agent writes or edits a lesson.
- A lesson that a check, a test or a script can enforce is retired once that exists: `status: retired` and `retired_by` naming it. A retired lesson stays as the record of why the check exists.
- An active lesson's globs must each match a file the repository tracks and still holds. A lesson about code that moved is updated; one about code that is gone is retired or deleted.
- A lesson shown to be wrong is deleted in a commit that says why.
- No em dash or en dash appears in a lesson, as anywhere else in the repository.

## Triage

`python scripts/lessons.py candidates [--untriaged] [<record> ...]` lists the `P1` and `P2` findings of review records, from every pass (D00 T05 §3 and §9; `--p3` adds the `P3` ones). The main session decides what each one teaches and writes it in the record's triage file, `triage/<path>.md` for `docs/reviews/<path>.md`: a heading, then one line per finding, `<pass> finding K: <disposition> [reason]`, the pass written `plan`, `round N`, `completion` or `reconciliation N` (`plan 2` for a record's second plan review). `K` is the finding's place among its pass's findings (its printed number, except in older rounds that restart the numbers under each lens). In a reconciliation only a new finding counts: a line saying an earlier gap is `closed` or `open` reports on that gap. The disposition is `lesson:<id>` (the kind can recur and no check stops it; several findings of one kind share one lesson), `enforced:<path>` (a check or test in the repository now stops it) or `one-off` with a reason. `check` refuses a line whose finding, lesson or enforcing file does not exist, a second line for one finding, and a triage file with no record; `candidates --untriaged` shows what is still to decide.

## Finding lessons

`python scripts/lessons.py query --path <file> [--role main|reader] [--topic <word>] [--text "<words>"] [--limit N] [--why] [--json]` returns the few lessons that apply, in the same order every time (D00 T05 §2). A lesson matches when its roles include the role (`main` when not given) or are `all`, and one of its globs matches a path, or one of its topics is asked for, or its body holds every word of the text. Lessons whose glob matches come first, the most specific glob first (an exact path before a pattern, `*` last), then topic matches, then text matches; within each, the lesson with more findings behind it, then the newer one. The findings behind a lesson are the lines of the files under `triage/` whose disposition is that lesson, written `<finding>: lesson:<id>`: the word after the line's first colon is its disposition, so a lesson named in the reason of another disposition is not counted. `--why` says what matched and how many matching lessons were not returned. The query reads `build/lessons.sqlite`, a cache it rebuilds by itself whenever anything `check` depends on changes (a lesson, a triage file, this README, a cited review record, the campaign spec, the commit at `HEAD` or the files the repository holds), and it shows nothing while the store breaks a rule.

## Upkeep

`python scripts/lessons.py report` prints the store by area, the leading folders of each lesson's globs that hold no wildcard, at most two (`scripts/*.py` is `scripts`, `scripts/lib/*.py` is `scripts/lib`, `*` is its own area): the active lessons with the findings behind each, most first, and the number retired. A store that only grows stops working, so an area holds at most 40 active lessons, and `report --check` exits 1 while any of three things stands (D00 T05 §8; a phase's closeout runs it):

- An area over the ceiling.
- Two lessons that could be one: the same area, a shared topic, globs matching the same tracked files or one's within the other's, and texts that share at least 30 percent of their words.
- A lesson that still failed: a triage line names it for a review pass run on a later day than the later of its `added` and `revised` dates, so the fault came back although the lesson existed.
 four remedies: merge lessons about one thing into one (`python scripts/lessons.py reassign <id> --to lesson:<other> --delete` moves the triage lines to the survivor; an `apart` key records two that teach different things); retire a lesson a check or test now enforces, with `retired_by`; rewrite one that did not stop its fault and set `revised`; delete one that taught nothing (`reassign <id> --to one-off <reason> --delete`). A listed lesson is never left as it is.

## Topics

The words a lesson's `topics` may use. A new word is added here in the same commit as the first lesson that needs it.

- `build`: compiling, linking, the toolchain and the pinned tools
- `ci`: the GitHub workflow and its runs
- `docs`: documents, specifications and their checkers
- `git`: commits, history and the working tree
- `process`: the campaign, its skills, sections and stamps
- `review`: the reviewer, findings and their records
- `security`: credentials, permissions and anything outward
- `tests`: test suites, fixtures and bounded child processes
- `tooling`: the scripts under `scripts/` and their libraries
- `ui`: the product's interface, controls and layout
- `windows`: Windows and WSL behaviour, shells and paths
