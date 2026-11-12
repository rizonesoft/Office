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
| `source` | yes | `<record>#round-N/finding-K` (a review finding) or `decision-<N>` (an owner decision) |
| `fix` | with a review source | the commit that fixed the finding, a full or short SHA in the history of `HEAD` |
| `added` | yes | the date the lesson was written, `YYYY-MM-DD` |
| `status` | yes | `active` or `retired` |
| `retired_by` | when retired | the check, test or script that now enforces the lesson, as a repository path |

A glob is read as Python's `PurePath.full_match` reads it, against repository paths with forward slashes: `*` stays within one folder and `**` crosses folders, so `scripts/**/*.py` is every Python file under `scripts/`.

The body is one paragraph of at most 600 characters: what goes wrong, and what to do instead. No key may be empty, unknown or given twice.

A review source names a record under `docs/reviews/`, the `## Round N` heading in it and the finding numbered `K` under that heading. An owner source names decision `N` of `docs/specs/2026-10-23-campaign-scope-design.md`. The checker proves the record, the round, the finding, the commit and the decision exist; whether the finding was confirmed and the lesson follows from it is the reviewer's judgment.

## Rules

- A lesson comes only from a review finding that was confirmed and fixed, or from an owner decision. Nothing an agent noticed about itself is a lesson.
- The main session writes a lesson and commits it like any other change. No agent writes or edits a lesson.
- A lesson that a check, a test or a script can enforce is retired once that exists: `status: retired` and `retired_by` naming it. A retired lesson stays as the record of why the check exists.
- An active lesson's globs must each match a file the repository tracks and still holds. A lesson about code that moved is updated; one about code that is gone is retired or deleted.
- A lesson shown to be wrong is deleted in a commit that says why.
- No em dash or en dash appears in a lesson, as anywhere else in the repository.

## Finding lessons

`python scripts/lessons.py query --path <file> [--role main|reader] [--topic <word>] [--text "<words>"] [--limit N] [--why] [--json]` returns the few lessons that apply, in the same order every time (D00 T05 §2). A lesson matches when its roles include the role (`main` when not given) or are `all`, and one of its globs matches a path, or one of its topics is asked for, or its body holds every word of the text. Lessons whose glob matches come first, the most specific glob first (an exact path before a pattern, `*` last), then topic matches, then text matches; within each, the lesson with more findings behind it in the triage files, then the newer one. `--why` says what matched and how many matching lessons were not returned. The query reads `build/lessons.sqlite`, a cache it rebuilds by itself whenever a lesson or triage file changes, and it shows nothing while the store breaks a rule.

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
