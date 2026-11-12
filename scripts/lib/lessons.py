# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Read the lesson files of `docs/lessons/` (D00 T05 §1; the format is `docs/lessons/README.md`).

A lesson is frontmatter of flat `key: value` lines between two `---` lines, then a one-paragraph body. `read` refuses
what makes a file unreadable as a lesson: no frontmatter, a line that is not `key: value`, an unknown or duplicate
key, a missing required key, and an `id` that differs from the file name. The value rules (dates, roles, sources and
the rest) are `check_store`'s, which `scripts/lessons.py check` prints in one run and the index (D00 T05 §2:
`build_index`, `query`, `rank`) requires to be clean. Stdlib only.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import subprocess
import tempfile

REQUIRED = ("id", "applies", "topics", "roles", "source", "added", "status")
OPTIONAL = ("fix", "retired_by")
KEYS = REQUIRED + OPTIONAL
LINE = re.compile(r"^([a-z_]+):(?:[ \t]+(.*?))?\s*$")


class LessonError(Exception):
    """A file that cannot be read as a lesson. `problems` holds every structural fault found in it, each naming the
    file and the key, so one run reports them all; the message is the first."""

    def __init__(self, problems):
        self.problems = list(problems) if isinstance(problems, (list, tuple)) else [problems]
        super().__init__("; ".join(self.problems))


def lesson_files(folder):
    """The lesson files of `folder`: every `*.md` in it but the README; `triage/` and other folders are not read."""
    return sorted(p for p in Path(folder).glob("*.md") if p.is_file() and p.name.lower() != "readme.md")


def read(path):
    """{key: value, ..., "body": text} of the lesson at `path`; LessonError when it cannot be read as one."""
    path = Path(path)
    name = path.name
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise LessonError(f"{name}: cannot be read ({error})") from None
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        raise LessonError(f"{name}: no frontmatter (the first line must be ---)")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise LessonError(f"{name}: the frontmatter is not closed by a --- line") from None
    fields, problems = {}, []
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip():
            continue
        match = LINE.match(line)
        if not match:
            problems.append(f"{name}: line {number} is not a flat key: value line")
            continue
        key, value = match[1], (match[2] or "").strip()
        if key not in KEYS:
            problems.append(f"{name}: unknown key {key!r}")
        elif key in fields:
            problems.append(f"{name}: duplicate key {key!r}")
        else:
            fields[key] = value
    problems += [f"{name}: missing key {k!r}" for k in REQUIRED if k not in fields]
    if "id" in fields and fields["id"] != path.stem:
        problems.append(f"{name}: id {fields['id']!r} differs from the file name {path.stem!r}")
    if problems:
        raise LessonError(problems)
    fields["body"] = "\n".join(lines[end + 1:]).strip()
    return fields


def items(value):
    """The comma-separated items of a field value, stripped, empty ones dropped."""
    return [part.strip() for part in value.split(",") if part.strip()]


def topics(readme):
    """The words the README's Topics list allows: each `- \\`word\\`` item under its `## Topics` heading."""
    words, inside = set(), False
    for line in Path(readme).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line.strip().lower() == "## topics"
            continue
        match = re.match(r"^- `([a-z0-9-]+)`", line)
        if inside and match:
            words.add(match[1])
    return words


# The rules of docs/lessons/README.md (D00 T05 §1), shared by `scripts/lessons.py check` and the index (§2).

ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ROLES = {"main", "reader"}  # and `all`; the removed writer roles (section-writer, principal-implementer) are refused
STATUSES = {"active", "retired"}
MAX_BODY = 600
DASHES = {"—": "em dash", "–": "en dash"}
REVIEW_SOURCE = re.compile(r"^(?P<record>[^#\s]+\.md)#round-(?P<round>[1-9][0-9]{0,3})/finding-(?P<finding>[1-9][0-9]{0,3})$")
DECISION_SOURCE = re.compile(r"^decision-(?P<number>[1-9][0-9]{0,5})$")  # bounded, so int() never fails
SPEC = "docs/specs/2026-10-23-campaign-scope-design.md"
GIT_SECONDS = 60
# A review pass's heading: `## Round 3: astra (...)`, `## Completion review: ...`; the reviewer is always named.
PASS_HEADING = re.compile(r"^## [A-Z][^:]*: [a-z0-9-]+ \(")


def git(root, *args):
    """(exit code, standard output) of a short git command in `root`."""
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=GIT_SECONDS)
    return done.returncode, done.stdout


class Repository:
    """What the checks ask of the repository: its files, its commits and the decisions of the campaign spec. Each
    answer is remembered, so a store of thousands of lessons asks git once per distinct commit and glob."""

    def __init__(self, root):
        self.root = Path(root)
        code, out = git(self.root, "ls-files", "-z")
        listed = out.split("\0") if code == 0 else []
        # A tracked file must still be there: an unstaged deletion counts as gone.
        self.files = [PurePosixPath(f) for f in listed if f and (self.root / f).is_file()]
        spec = self.root / SPEC
        text = spec.read_text(encoding="utf-8") if spec.is_file() else ""
        self.decisions = {int(m[1]) for m in re.finditer(r"(?m)^(\d+)\. \*\*", text)}
        self._globs, self._commits = {}, {}

    def matches(self, glob):
        if glob not in self._globs:
            self._globs[glob] = any(f.full_match(glob) for f in self.files)
        return self._globs[glob]

    def commit_on_head(self, ref):
        if ref not in self._commits:
            ok = bool(re.fullmatch(r"[0-9a-f]{7,40}", ref))
            ok = ok and git(self.root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")[0] == 0
            self._commits[ref] = ok and git(self.root, "merge-base", "--is-ancestor", ref, "HEAD")[0] == 0
        return self._commits[ref]


# A finding in a review round: a numbered item whose text opens with its severity, in any form the records use:
# `**P1, ...`, `**P1: ...`, `**P1:** ...`, `**[P1] ...`, `**P1** ...`, `**P1**, ...`.
FINDING = re.compile(r"^\s*(\d+)\.\s+\*\*\[?(P[123])\]?(\*\*)?[,:]?(\*\*)?\s+(.*)$")
LOCATION = re.compile(r"`([^`\s]+:\d+(?:-\d+)?)`")
# The one other form: the location first, the severity in brackets: `` **`path:line` (P2): ...``.
FINDING_BY_PLACE = re.compile(r"^\s*(\d+)\.\s+\*\*((?:`[^`]+`(?:\s*(?:,|and)\s*)?)+)\s*\((P[123])\)[:,]?\s+(.*)$")
# A numbered item whose bold opening names a severity: a finding, in a known form or not.
LOOKS_LIKE_A_FINDING = re.compile(r"^\s*\d+\.\s+\*\*[^*]{0,200}\bP[123]\b")


def round_findings(record_text):
    """{round number: [finding, ...]} of a review record, each finding `{"k", "severity", "location", "sentence"}`.
    A round's text runs from its `## Round N` heading to its `OVERALL:` line or the next pass heading, so lens
    headings inside it (older records put `## adversarial` at the same level) stay part of it and a heading the writer
    adds after it does not. `k` is the finding's place among the round's findings, from 1: the printed number where a
    round numbers its findings once through, and a count through the round where an older record restarts the numbers
    under each lens (82 of the first 1,003 findings share a printed number with another in their round)."""
    rounds, current = {}, None
    for line in record_text.splitlines():
        match = re.match(r"^## Round (\d+)\b", line)
        if match:
            current = rounds.setdefault(int(match[1]), [])
            continue
        if current is None:
            continue
        if PASS_HEADING.match(line):
            current = None  # another pass (a plan, completion or reconciliation review) begins
            continue
        found, placed = FINDING.match(line), FINDING_BY_PLACE.match(line)
        if placed and not found:
            rest = placed[4].replace("**", "")
            where = LOCATION.search(placed[2])
            sentence = re.split(r"(?<=[.!?])\s", rest, maxsplit=1)[0].strip()
            current.append({"k": len(current) + 1, "severity": placed[3], "location": where[1] if where else "",
                            "sentence": sentence[:200]})
        elif not found and LOOKS_LIKE_A_FINDING.match(line):
            # A severity in a form this reader does not know: kept, marked, so the caller refuses the record
            # instead of dropping the finding.
            current.append({"k": len(current) + 1, "severity": "?", "location": "", "sentence": line.strip()[:200]})
        if found:
            rest = found[5].replace("**", "")
            where = LOCATION.search(rest)
            told = re.sub(r"^`[^`]+`[:,]?\s*", "", rest)  # a finding that opens with its location says it once
            sentence = re.split(r"(?<=[.!?])\s", told, maxsplit=1)[0].strip()
            current.append({"k": len(current) + 1, "severity": found[2], "location": where[1] if where else "",
                            "sentence": sentence[:200]})
        if line.startswith("OVERALL:"):
            current = None
    return rounds


def finding_in(record_text, round_number, finding):
    """None when the record has no `## Round N`; else whether that round has a finding `finding` (its place among the
    round's findings, as `round_findings` counts them)."""
    rounds = round_findings(record_text)
    if int(round_number) not in rounds:
        return None
    return 1 <= int(finding) <= len(rounds[int(round_number)])

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
            datetime.date.fromisoformat(lesson["added"])
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
    for key in ("applies", "topics", "roles"):
        if lesson[key] and not items(lesson[key]):
            say("empty value", f"{key} names nothing")
    for word in items(lesson["topics"]):
        if word not in allowed_topics:
            say("topics", f"{word!r} is not in the README's Topics list")
    roles = items(lesson["roles"])
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
        for glob in items(lesson["applies"]):
            if glob != "*" and not repo.matches(glob):
                say("applies", f"{glob!r} matches no file the repository holds")
    return found


def check_store(root):
    """(problems, lessons): every problem of every lesson under `root`, one line each, and the lessons that read."""
    root = Path(root)
    folder = root / "docs" / "lessons"
    allowed = topics(folder / "README.md")
    repo = Repository(root)
    found, seen, good = [], {}, []
    for path in lesson_files(folder):
        try:
            lesson = read(path)
        except LessonError as error:
            found.extend(error.problems)
            continue
        if lesson["id"] in seen:
            found.append(f"{lesson['id']}: duplicate id: also {seen[lesson['id']]}")
        seen[lesson["id"]] = path.name
        found.extend(problems_of(lesson, repo, allowed))
        good.append(lesson)
    found.extend(triage_problems(root))
    return found, good


# Triage (D00 T05 §3): `docs/lessons/triage/<path>.md` holds the dispositions of the findings of the review record
# `docs/reviews/<path>.md`, one file per record, one line per finding: `round N finding K: <disposition> [reason]`.

REVIEWS = "docs/reviews"
TRIAGE_LINE = re.compile(r"^\s*(?:[-*]\s+)?round (\d+) finding (\d+):\s+(\S+)(?:\s+(.*))?$")


class RecordError(Exception):
    """A review record or a triage file that cannot be used; the message names the file."""


def triage_path(root, record):
    """The triage file of the review record `record` (a repository path under docs/reviews/)."""
    return Path(root) / "docs" / "lessons" / TRIAGE / PurePosixPath(record).relative_to(REVIEWS)


def read_triage(root, record, repo=None):
    """({(round, k): disposition} of the valid lines, [problem, ...]) of a record's triage file; both empty when
    there is none. A line is valid when its finding exists in the record, no earlier line triaged it, and its
    disposition is `lesson:<id>` naming a lesson file, `enforced:<path>` naming a file the repository holds, or
    `one-off` followed by a reason. RecordError when the triage file or its record cannot be read."""
    root = Path(root)
    path = triage_path(root, record)
    name = path.relative_to(root).as_posix()
    if not path.is_file():
        return {}, []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise RecordError(f"{name}: cannot be read ({type(error).__name__})") from None
    try:
        rounds = round_findings((root / record).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return {}, [f"{name}: its review record {record} does not exist or cannot be read"]
    valid, problems, seen = {}, [], set()
    for number, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        where = f"{name}:{number}"
        match = TRIAGE_LINE.match(line)
        if not match:
            problems.append(f"{where}: not a triage line (round N finding K: <disposition> [reason])")
            continue
        key, word, reason = (int(match[1]), int(match[2])), match[3], (match[4] or "").strip()
        if key[0] not in rounds or not 1 <= key[1] <= len(rounds[key[0]]):
            problems.append(f"{where}: {record} has no round {key[0]} finding {key[1]}")
            continue
        if key in seen:
            # Two lines for one finding, whatever each says and whichever came first: neither stands, so the
            # finding stays outstanding until one is removed.
            problems.append(f"{where}: round {key[0]} finding {key[1]} already has a disposition"
                            + (f" ({valid[key]})" if key in valid else ""))
            valid.pop(key, None)
            continue
        seen.add(key)
        if word.startswith("lesson:"):
            lesson_id = word[len("lesson:"):].rstrip(",.;")
            if not ID.fullmatch(lesson_id) or not (root / "docs" / "lessons" / f"{lesson_id}.md").is_file():
                problems.append(f"{where}: lesson:{lesson_id} names no lesson file")
            else:
                valid[key] = f"lesson:{lesson_id}"
        elif word.startswith("enforced:"):
            target = word[len("enforced:"):].rstrip(",.;")
            held = (root / target).is_file() if repo is None else PurePosixPath(target) in repo.files
            if not target or ".." in PurePosixPath(target).parts or not held:
                problems.append(f"{where}: enforced:{target} names no file the repository holds")
            else:
                valid[key] = f"enforced:{target}"
        elif word.rstrip(",.;:") == "one-off":
            if not reason:
                problems.append(f"{where}: one-off needs a reason")
            else:
                valid[key] = "one-off"
        else:
            problems.append(f"{where}: {word!r} is not lesson:<id>, enforced:<path> or one-off")
    return valid, problems


def triage_problems(root, repo=None):
    """Every problem of every triage file under `root`, for `check`."""
    root = Path(root)
    base = root / "docs" / "lessons" / TRIAGE
    found = []
    for path in sorted(base.rglob("*.md")) if base.is_dir() else ():
        record = (PurePosixPath(REVIEWS) / path.relative_to(base).as_posix()).as_posix()
        try:
            found.extend(read_triage(root, record, repo)[1])
        except RecordError as error:
            found.append(str(error))
    return found


def review_records(root):
    """Every review record under docs/reviews/ that holds a round, as repository paths."""
    base = Path(root) / REVIEWS
    return [path.relative_to(root).as_posix() for path in sorted(base.rglob("*.md"))
            if re.search(r"(?m)^## Round \d+\b", path.read_text(encoding="utf-8", errors="replace"))]


def candidates(root, records=None, untriaged=False):
    """The `P1` and `P2` findings of the review `records` (all under docs/reviews/ when none is named), each
    `{"record", "round", "k", "severity", "location", "sentence"}`; with `untriaged`, only those with no valid line in
    the record's triage file. RecordError naming the file when a named record is missing, unreadable or holds no
    review round, or a triage file cannot be read: an input that was skipped must never look like nothing to do."""
    root = Path(root)
    named = records is not None and len(records) > 0
    out = []
    for record in (records if named else review_records(root)):
        record = PurePosixPath(str(record).replace("\\", "/")).as_posix()
        try:
            text = (root / record).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise RecordError(f"{record}: cannot be read ({type(error).__name__})") from None
        rounds = round_findings(text)
        if not rounds:
            raise RecordError(f"{record}: holds no review round")
        unread = [(number, f) for number in sorted(rounds) for f in rounds[number] if f["severity"] == "?"]
        if unread:
            number, finding = unread[0]
            raise RecordError(f"{record}: round {number} finding {finding['k']} names a severity in a form this "
                              f"reader does not know ({finding['sentence'][:80]}); teach round_findings the form")
        done = {}
        if untriaged:
            if not record.startswith(REVIEWS + "/"):
                raise RecordError(f"{record}: is not under {REVIEWS}/, so it has no triage file")
            done = read_triage(root, record)[0]
        for number in sorted(rounds):
            for finding in rounds[number]:
                if finding["severity"] in ("P1", "P2") and (number, finding["k"]) not in done:
                    out.append({"record": record, "round": number, **finding})
    return out

# The index (D00 T05 §2): `build/lessons.sqlite`, a cache of the active lessons that makes them findable. The files
# are the truth; the index is rebuilt whenever they, or the triage files that count a lesson's evidence, change.

INDEX = os.path.join("build", "lessons.sqlite")
TRIAGE = "triage"
# A triage line is `<finding>: <disposition> [reason]`; its disposition is the first word after the first colon.
DISPOSITION = re.compile(r"^\s*(?:[-*]\s+)?[^:\n]+:\s+lesson:([a-z0-9]+(?:-[a-z0-9]+)*)(?=[\s,.;]|$)")
MAX_LIMIT = 10


class StoreInvalid(Exception):
    """The lesson store breaks a rule, so no index is built from it; `problems` holds every line of `check`."""

    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__(f"{len(self.problems)} problem(s) in the lesson store")


class IndexError_(Exception):
    """The index could not be written; the earlier one, if any, is still in place."""


def _store_files(root):
    folder = Path(root) / "docs" / "lessons"
    triage = sorted(p for p in (folder / TRIAGE).rglob("*.md") if p.is_file()) if (folder / TRIAGE).is_dir() else []
    readme = [folder / "README.md"] if (folder / "README.md").is_file() else []
    return lesson_files(folder), triage, readme


def cited_records(lessons):
    """The review records the lessons cite, sorted: part of what the index's digest covers."""
    found = set()
    for lesson in lessons:
        match = REVIEW_SOURCE.match(lesson.get("source", ""))
        if match:
            found.add(match["record"])
    return sorted(found)


def store_digest(root, records=()):
    """A digest of everything a valid index depends on, so a query never serves a store that `check` would now
    refuse: the lesson files, the triage files and the README by name, size and modification time; the campaign
    spec (its decisions) and the cited review `records` the same way; the commit at HEAD (a `fix` must be in its
    history); and git's list of tracked files with those deleted from the working tree (an `applies` glob must match
    a file that is still there). No file's content is read, so a query over thousands of lessons stays quick."""
    root = Path(root)
    digest = hashlib.sha256()

    def stamp(path):
        try:
            stat = path.stat()
            digest.update(f"{path.relative_to(root).as_posix()}\0{stat.st_size}\0{stat.st_mtime_ns}\n".encode())
        except OSError:
            digest.update(f"{path}\0gone\n".encode())
    for group in _store_files(root):
        for path in group:
            stamp(path)
    for name in (SPEC, *records):
        stamp(root / name)
    for args in (("rev-parse", "HEAD"), ("ls-files", "-z"), ("ls-files", "-d", "-z")):
        code, out = git(root, *args)
        digest.update(f"{' '.join(args)}\0{code}\0".encode() + hashlib.sha256(out.encode()).digest())
    return digest.hexdigest()

def evidence(root):
    """{lesson id: findings behind it}: the lines of the files under `docs/lessons/triage/` whose disposition is
    `lesson:<id>` (§3 writes those files; with none, every count is zero). Each line counts once, by the word that
    follows its first colon; a lesson mentioned in the reason of another disposition is not counted."""
    counts = {}
    for path in _store_files(root)[1]:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = DISPOSITION.match(line)  # the line's own disposition, once: a lesson named in a reason is not one
            if match:
                counts[match[1]] = counts.get(match[1], 0) + 1
    return counts


def build_index(root):
    """Write `build/lessons.sqlite` from a store that passes every rule: a temporary file beside it, then a replace,
    so an interrupted or failed build leaves the earlier index whole. StoreInvalid when a rule is broken;
    IndexError_ when the file cannot be written. Returns the number of active lessons indexed."""
    root = Path(root)
    problems, lessons = check_store(root)
    if problems:
        raise StoreInvalid(problems)
    records = cited_records(lessons)
    digest = store_digest(root, records)
    counts = evidence(root)
    target = root / INDEX
    tmp = None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".lessons.", suffix=".tmp", dir=target.parent)
        os.close(fd)
        db = sqlite3.connect(tmp)
        try:
            db.executescript(
                "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);"
                "CREATE TABLE lessons (id TEXT PRIMARY KEY, roles TEXT, topics TEXT, source TEXT, added TEXT,"
                " body TEXT, evidence INTEGER);"
                "CREATE TABLE globs (id TEXT, glob TEXT);"
                "CREATE VIRTUAL TABLE bodies USING fts5(id UNINDEXED, body);")
            active = [lesson for lesson in lessons if lesson["status"] == "active"]
            db.execute("INSERT INTO meta VALUES ('digest', ?)", (digest,))
            db.execute("INSERT INTO meta VALUES ('records', ?)", (json.dumps(records),))
            db.executemany("INSERT INTO lessons VALUES (?, ?, ?, ?, ?, ?, ?)", [
                (l["id"], ",".join(items(l["roles"])), ",".join(items(l["topics"])), l["source"], l["added"],
                 l["body"], counts.get(l["id"], 0)) for l in active])
            db.executemany("INSERT INTO globs VALUES (?, ?)",
                           [(l["id"], glob) for l in active for glob in items(l["applies"])])
            db.executemany("INSERT INTO bodies VALUES (?, ?)", [(l["id"], l["body"]) for l in active])
            db.commit()
        finally:
            db.close()
        os.replace(tmp, target)
        tmp = None
        return len(active)
    except (OSError, sqlite3.Error) as error:
        raise IndexError_(f"the lesson index could not be written ({type(error).__name__}: {error})") from None
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass  # the temporary file is already gone


def open_index(root):
    """An open connection to a current index, rebuilding it first when it is missing, unreadable or stale."""
    root = Path(root)
    target = root / INDEX
    current = False
    if target.is_file():
        try:
            db = sqlite3.connect(target)
            try:
                meta = dict(db.execute("SELECT key, value FROM meta"))
                records = json.loads(meta.get("records", "[]"))
                current = meta.get("digest") == store_digest(root, records)
            finally:
                db.close()
        except (sqlite3.Error, ValueError, TypeError):
            current = False  # not a database, or not this one: rebuilt
    if not current:
        build_index(root)
    return sqlite3.connect(target)


def specificity(glob):
    """How specific a glob is, as a pair that sorts: (1 for an exact path with no wildcard, else 0; its literal
    characters less its wildcards). An exact path therefore outranks every pattern that also matches it, whatever
    their lengths; among patterns `scripts/*.py` (10) outranks `scripts/**/*.py` (9); a bracket class is one wildcard,
    so the characters inside it earn nothing; and `*`, which applies to everything, is the least specific of all."""
    plain = re.sub(r"\[[^\]]*\]", "?", glob)
    wild = sum(plain.count(char) for char in "*?")
    return (0 if wild else 1, len(plain) - 2 * wild)

def rank(found):
    """The one order every query result takes. `found` is {id: lesson} where each lesson holds `tier` (0 a glob
    matched a path, 1 a topic was asked for, 2 the text matched), `specific` (the `specificity` of its most specific
    matching glob), `text_rank` (FTS5's rank, smaller is better), `evidence`, `added` and `id`. A path match comes first, the
    most specific glob first; then a topic match; then a text match by FTS5's rank; within each, more evidence, then
    the newer date, then the id."""
    def key(lesson):
        exact, literal = lesson["specific"]
        within = (-exact, -literal) if lesson["tier"] == 0 else (0, lesson["text_rank"] if lesson["tier"] == 2 else 0)
        newer = -datetime.date.fromisoformat(lesson["added"]).toordinal()
        return (lesson["tier"], within, -lesson["evidence"], newer, lesson["id"])
    return sorted(found.values(), key=key)


def query(root, paths=(), role="main", topics_asked=(), text="", limit=5):
    """(the first `limit` matching lessons in rank order, how many more matched). A lesson matches when its roles
    include `role` or are `all`, AND a glob of it matches one of `paths`, or one of its topics is asked for, or its
    body holds every word of `text` (literal words: punctuation and FTS syntax in it are never an expression). Each
    lesson is returned once, with `why` saying what matched."""
    db = open_index(root)
    try:
        lessons = {row[0]: {"id": row[0], "roles": row[1].split(","), "topics": row[2].split(","), "source": row[3],
                            "added": row[4], "body": row[5], "evidence": row[6]}
                   for row in db.execute("SELECT id, roles, topics, source, added, body, evidence FROM lessons")}
        globs = {}
        for lesson_id, glob in db.execute("SELECT id, glob FROM globs"):
            globs.setdefault(lesson_id, []).append(glob)
        words = re.findall(r"\w+", text or "")
        ranks = {}
        if words:
            phrase = " ".join('"' + word.replace('"', '""') + '"' for word in words)
            ranks = dict(db.execute("SELECT id, rank FROM bodies WHERE bodies MATCH ? ORDER BY rank", (phrase,)))
    finally:
        db.close()
    targets = [PurePosixPath(str(path).replace("\\", "/")) for path in paths]
    found = {}
    for lesson_id, lesson in lessons.items():
        if role not in lesson["roles"] and "all" not in lesson["roles"]:
            continue
        matched = [glob for glob in globs.get(lesson_id, [])
                   if any(glob == "*" or target.full_match(glob) for target in targets)]
        asked = [topic for topic in topics_asked if topic in lesson["topics"]]
        if matched:
            best = max(matched, key=specificity)
            lesson.update(tier=0, specific=specificity(best), text_rank=0.0, why=f"glob {best}")
        elif asked:
            lesson.update(tier=1, specific=(0, 0), text_rank=0.0, why=f"topic {asked[0]}")
        elif lesson_id in ranks:
            lesson.update(tier=2, specific=(0, 0), text_rank=ranks[lesson_id], why=f"text {' '.join(words)}")
        else:
            continue
        lesson["why"] += f"; evidence {lesson['evidence']}"
        found[lesson_id] = lesson
    ordered = rank(found)
    return ordered[:limit], max(0, len(ordered) - limit)
