#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Check the lesson files of `docs/lessons/` against the rules of `docs/lessons/README.md` (D00 T05 §1).

    python scripts/lessons.py check

Every problem in every lesson is reported in one run, one line each naming the lesson; the exit is 0 when there is
none, 1 when there is one, 2 when the lesson folder or its README cannot be read.
"""
import argparse
from datetime import date
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import lessons  # found through scripts/lib, put on the path just above

ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ROLES = {"main", "reader"}  # and `all`; the removed writer roles (section-writer, principal-implementer) are refused
STATUSES = {"active", "retired"}
MAX_BODY = 600
DASHES = {"—": "em dash", "–": "en dash"}
REVIEW_SOURCE = re.compile(r"^(?P<record>[^#\s]+\.md)#round-(?P<round>[1-9][0-9]*)/finding-(?P<finding>[1-9][0-9]*)$")
DECISION_SOURCE = re.compile(r"^decision-(?P<number>[1-9][0-9]*)$")
SPEC = "docs/specs/2026-10-23-campaign-scope-design.md"
GIT_SECONDS = 60


def git(root, *args):
    """(exit code, standard output) of a short git command in `root`."""
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=GIT_SECONDS)
    return done.returncode, done.stdout


class Repository:
    """What the checks ask of the repository: its files, its commits and the decisions of the campaign spec."""

    def __init__(self, root):
        self.root = Path(root)
        code, out = git(self.root, "ls-files", "-z")
        listed = out.split("\0") if code == 0 else []
        # A tracked file must still be there: an unstaged deletion counts as gone.
        self.files = [f for f in listed if f and (self.root / f).is_file()]
        spec = self.root / SPEC
        text = spec.read_text(encoding="utf-8") if spec.is_file() else ""
        self.decisions = {int(m[1]) for m in re.finditer(r"(?m)^(\d+)\. \*\*", text)}

    def matches(self, glob):
        return any(PurePosixPath(f).full_match(glob) for f in self.files)

    def commit_on_head(self, ref):
        if not re.fullmatch(r"[0-9a-f]{7,40}", ref):
            return False
        code, _ = git(self.root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
        if code != 0:
            return False
        return git(self.root, "merge-base", "--is-ancestor", ref, "HEAD")[0] == 0


def finding_in(record_text, round_number, finding):
    """Whether the record has a `## Round N` heading with a finding numbered `finding` under it."""
    block = None
    for line in record_text.splitlines():
        if line.startswith("## "):
            if block is not None:
                break
            if re.match(rf"^## Round {round_number}\b", line):
                block = []
            continue
        if block is not None:
            block.append(line)
    if block is None:
        return None
    return any(re.match(rf"^\s*{finding}\.\s", line) for line in block)


def problems_of(lesson, repo, allowed_topics):
    """The rule problems of one read lesson, each naming the rule."""
    found = []
    name = lesson["id"]

    def say(rule, detail):
        found.append(f"{name}: {rule}: {detail}")
    for key, value in lesson.items():
        if key != "body" and not value:
            say("empty value", f"{key} is empty")
    if lesson["id"] and not ID.fullmatch(lesson["id"]):
        say("id", f"{lesson['id']!r} is not kebab-case")
    if lesson["status"] and lesson["status"] not in STATUSES:
        say("status", f"{lesson['status']!r} is neither active nor retired")
    if lesson["added"]:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", lesson["added"]):
                raise ValueError
            date.fromisoformat(lesson["added"])
        except ValueError:
            say("added", f"{lesson['added']!r} is not a YYYY-MM-DD date")
    if lesson["status"] == "retired" and not lesson.get("retired_by"):
        say("retired_by", "a retired lesson names what now enforces it")
    body = lesson["body"]
    if not body:
        say("body", "the body is empty")
    elif re.search(r"\n\s*\n", body):
        say("body", "the body is more than one paragraph")
    if len(body) > MAX_BODY:
        say("body length", f"{len(body)} characters, more than {MAX_BODY}")
    for char, label in DASHES.items():
        if any(char in value for value in lesson.values()):
            say("dash", f"an {label}")
    for word in lessons.items(lesson["topics"]):
        if word not in allowed_topics:
            say("topics", f"{word!r} is not in the README's Topics list")
    roles = lessons.items(lesson["roles"])
    for role in roles:
        if role != "all" and role not in ROLES:
            say("roles", f"{role!r} is not all, main or reader")
    if "all" in roles and len(roles) > 1:
        say("roles", "all stands alone")
    source = lesson["source"]
    review, decision = REVIEW_SOURCE.match(source), DECISION_SOURCE.match(source)
    if review:
        record = review["record"]
        path = repo.root / record
        if not record.startswith("docs/reviews/") or not path.is_file():
            say("source", f"{record} is not a review record in the repository")
        else:
            present = finding_in(path.read_text(encoding="utf-8"), review["round"], review["finding"])
            if present is None:
                say("source", f"{record} has no ## Round {review['round']} heading")
            elif not present:
                say("source", f"round {review['round']} of {record} has no finding {review['finding']}")
        fix = lesson.get("fix")
        if not fix:
            say("fix", "a review source names the commit that fixed the finding")
        elif not repo.commit_on_head(fix):
            say("fix", f"{fix!r} is not a commit in the history of HEAD")
    elif decision:
        if int(decision["number"]) not in repo.decisions:
            say("source", f"{SPEC} has no decision {decision['number']}")
        if lesson.get("fix"):
            say("fix", "only a review source takes a fix commit")
    elif source:
        say("source", f"{source!r} is neither <record>#round-N/finding-K nor decision-<N>")
    if lesson["status"] == "active":
        for glob in lessons.items(lesson["applies"]):
            if glob != "*" and not repo.matches(glob):
                say("applies", f"{glob!r} matches no file the repository holds")
    return found


def check(root=ROOT):
    """Every problem of every lesson under `root`, one line each."""
    root = Path(root)
    folder = root / "docs" / "lessons"
    readme = folder / "README.md"
    allowed = lessons.topics(readme)
    repo = Repository(root)
    found, seen = [], {}
    for path in lessons.lesson_files(folder):
        try:
            lesson = lessons.read(path)
        except lessons.LessonError as error:
            found.append(str(error))
            continue
        if lesson["id"] in seen:
            found.append(f"{lesson['id']}: duplicate id: also {seen[lesson['id']]}")
        seen[lesson["id"]] = path.name
        found.extend(problems_of(lesson, repo, allowed))
    return found


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="check every lesson against the README's rules")
    parser.parse_args(argv)
    readme = Path(root) / "docs" / "lessons" / "README.md"
    if not readme.is_file():
        print(f"lessons: {readme} cannot be read", file=sys.stderr)
        return 2
    found = check(root)
    for problem in found:
        print(problem)
    count = len(lessons.lesson_files(Path(root) / "docs" / "lessons"))
    print(f"{count} lesson(s), {len(found)} problem(s)" if found else f"{count} lesson(s), all valid")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
