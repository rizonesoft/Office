#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Check the lesson files of `docs/lessons/` and query them (D00 T05 §1 and §2; `docs/lessons/README.md`).

    python scripts/lessons.py check
    python scripts/lessons.py candidates [--untriaged] [--p3] [docs/reviews/<record>.md ...]
    python scripts/lessons.py query --path scripts/lib/tool_lock.py [--role main] [--topic tests] [--text "gate"]
                                    [--limit 5] [--why] [--json]

`check` reports every problem in every lesson in one run, one line each naming the lesson: exit 0 when there is none,
1 when there is one, 2 when the lesson folder or its README cannot be read.

`candidates` lists the `P1` and `P2` findings of review records (every record under `docs/reviews/` when none is
named) as `<record> round N finding K [P1] <file:line>: <first sentence>` (`--p3` adds the `P3` ones, for a section
triaging every finding its own round fixed), and with `--untriaged` only those with no
valid line in the record's triage file `docs/lessons/triage/<path>.md` (D00 T05 §3). Exit 0, or 1 naming the file
when a named record or a triage file cannot be read or holds no review round, so skipped input never looks like
nothing left to do.

`query` returns the few lessons that apply, in one fixed order (`rank` in `scripts/lib/lessons.py`): a lesson matches
when its roles include `--role` (default `main`) or are `all`, AND one of its globs matches a `--path`, or one of
its topics is a `--topic`, or its body holds every word of `--text` (literal words, never an expression). It reads
`build/lessons.sqlite`, rebuilt by itself whenever a lesson or triage file changed. Exit 0 with the lessons (none is
not an error), 1 when the store breaks a rule or the index cannot be written (nothing is shown), 2 for arguments it
refuses: no `--path`, `--topic` or `--text`, a `--limit` outside 1 to 10, a `--role` that is not `main` or `reader`.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import lessons  # found through scripts/lib, put on the path just above

SPEC = lessons.SPEC
finding_in = lessons.finding_in


def check(root=ROOT):
    """Every problem of every lesson under `root`, one line each."""
    return lessons.check_store(root)[0]


def cmd_check(root):
    found = check(root)
    for problem in found:
        print(problem)
    count = len(lessons.lesson_files(Path(root) / "docs" / "lessons"))
    print(f"{count} lesson(s), {len(found)} problem(s)" if found else f"{count} lesson(s), all valid")
    return 1 if found else 0


def cmd_query(args, root):
    if not (args.path or args.topic or args.text):
        print("lessons: query needs a --path, a --topic or --text", file=sys.stderr)
        return 2
    if not 1 <= args.limit <= lessons.MAX_LIMIT:
        print(f"lessons: --limit is 1 to {lessons.MAX_LIMIT}", file=sys.stderr)
        return 2
    if args.role not in lessons.ROLES:
        print(f"lessons: --role is one of {', '.join(sorted(lessons.ROLES))}", file=sys.stderr)
        return 2
    try:
        shown, more = lessons.query(root, args.path or (), args.role, args.topic or (), args.text or "", args.limit)
    except lessons.StoreInvalid as error:
        for problem in error.problems:
            print(problem, file=sys.stderr)
        print(f"lessons: the store has {len(error.problems)} problem(s), so no lesson is shown; "
              f"run python scripts/lessons.py check", file=sys.stderr)
        return 1
    except lessons.IndexError_ as error:
        print(f"lessons: {error}", file=sys.stderr)
        return 1
    if args.json:
        fields = ("id", "source", "body", "why") if args.why else ("id", "source", "body")
        print(json.dumps([{key: lesson[key] for key in fields} for lesson in shown], indent=1))
        if args.why:  # standard output stays one JSON array
            print(f"{more} more matching lesson(s) not returned", file=sys.stderr)
        return 0
    for lesson in shown:
        print(f"{lesson['id']}  ({lesson['source']})")
        if args.why:
            print(f"  why: {lesson['why']}")
        print(f"  {lesson['body']}")
    if args.why:
        print(f"{more} more matching lesson(s) not returned")
    return 0


def cmd_candidates(args, root):
    try:
        severities = ("P1", "P2", "P3") if args.p3 else ("P1", "P2")
        found = lessons.candidates(root, args.records, args.untriaged, severities)
    except lessons.RecordError as error:
        print(f"lessons: {error}", file=sys.stderr)
        return 1
    for item in found:
        where = f" {item['location']}" if item["location"] else ""
        print(f"{item['record']} round {item['round']} finding {item['k']} [{item['severity']}]{where}: "
              f"{item['sentence']}")
    return 0


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="check every lesson against the README's rules")
    query = sub.add_parser("query", help="the lessons that apply to a path, a topic or a text, in rank order")
    query.add_argument("--path", action="append", help="a repository path the work touches (repeatable)")
    query.add_argument("--role", default="main", help="who asks: main (the default) or reader")
    query.add_argument("--topic", action="append", help="a topic of the README's list (repeatable)")
    query.add_argument("--text", help="words every returned lesson's body holds")
    query.add_argument("--limit", type=int, default=5, help="how many to return, 1 to 10 (default 5)")
    query.add_argument("--why", action="store_true", help="say why each ranked where it did, and how many more matched")
    query.add_argument("--json", action="store_true", help="print a JSON array")
    listing = sub.add_parser("candidates", help="the P1 and P2 findings of review records, to triage into lessons")
    listing.add_argument("records", nargs="*", help="review records (default: every record under docs/reviews/)")
    listing.add_argument("--untriaged", action="store_true",
                         help="only findings with no valid line in the record's triage file")
    listing.add_argument("--p3", action="store_true",
                         help="list P3 findings too (a section triages every finding its round fixed)")
    args = parser.parse_args(argv)
    if args.command == "candidates":
        return cmd_candidates(args, root)
    readme = Path(root) / "docs" / "lessons" / "README.md"
    if not readme.is_file():
        print(f"lessons: {readme} cannot be read", file=sys.stderr)
        return 2
    return cmd_check(root) if args.command == "check" else cmd_query(args, root)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
