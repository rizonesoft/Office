# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The canonical TODO graph: parse todo/NN-domain/TODO-NN-*.md, validate it, order it, project the plan.

Adapted from swisshotelschool-coza's scripts/lib/todo_graph.py (itself a port of rizonetech-com's
scripts/lib/workflow.py), extended with the ScratchPad, Resolute, and Recto format rules:
Adjacency declarations, bidirectional XREFs, index coverage, frozen freeze checks, and durable
deferrals. Rules: todo/README.md.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PLAN = "todo/implementation-plan.md"
# What follows each "-> XREF:": one space and exactly one well-formed reference, nothing run into it.
XREF_TARGET = re.compile(r" (?:D(?P<d>\d{2}) )?(?:T(?P<t>\d{2}) )?§(?P<s>[1-9]\d*)(?![\w§]|\.\d)")
REF = re.compile(r"(?:D(?P<d>\d{2})\s+)?(?:T(?P<t>\d{2})\s+)?§(?P<s>[1-9]\d*)")
ROW = re.compile(r"^\|\s*([1-9]\d*)\s*\|\s*§([1-9]\d*)\s*\|\s*([^|]+)\|\s*([^|]*)\|\s*\[([ x])\]\s*\|$")
# What a section needs from outside the repository. The WAITING values are people, companies, or the
# operator's own hands: a section naming one stays blocked until the answer is recorded and the Need
# is removed from the section.
NEEDS = {"windows-host", "arm64-host", "display-session", "office", "libreoffice", "store-account",
         "attended", "owner-decision", "third-party", "operator"}
WAITING = {"owner-decision", "third-party", "operator"}
STATUSES = {"draft", "active", "blocked", "done", "superseded"}
# stopped-at-33 is the current review-round cap (owner decision 2026-10-23); stopped-at-22, -13, -8 and -3 stay valid
# on earlier receipts.
# stopped-low-severity: after SEVERITY_CUTOFF_ROUND, a round whose findings are all P3 or advisory ends the loop and
# its findings are filed as leftovers (review-todo-section).
VERDICTS = {"clean", "fixed", "stopped-at-33", "stopped-at-22", "stopped-at-13", "stopped-at-8", "stopped-at-3",
            "stopped-low-severity"}
REVIEW_ROUND_CAP = 33
# Caps a receipt that records round_cap may name: the current one, this repository's 22 (to 2026-10-23), and those
# Recto's receipts were written under. A receipt under the current cap also names its completion record.
EARLIER_CAPS = {8, 13, 22}
# Receipts older than the rounds_spent field were written under a three-round cap, before severity stops existed.
# Each is frozen by the digest of its content in LEGACY_RECEIPTS, so a new receipt cannot pass by dropping the field.
LEGACY_RECEIPTS = "docs/reviews/legacy-receipts.json"
LEGACY_VERDICTS = {"clean", "fixed", "stopped-at-3"}
SEVERITY_CUTOFF_ROUND = 8
# A round scripts/review-dispatch.py recorded in a findings file, reviewed or not ("## Round 2: none").
ROUND_RECORD = re.compile(r"^## Round ([0-9]+): ", re.M)
ADJACENCY_KEYS = ["list", "document", "settings", "reporting", "notifications", "permissions",
                  "audit", "exchange", "reverse"]
# The closed phase list. A project names its phases (and the plan's title and acceptance bar) in
# todo/plan.json; without it the plan shows bare phase numbers.
PHASES = (0, 1, 2, 3, 4, 5, 6, 7, 99)
PLAN_CONFIG = "todo/plan.json"
PLAN_DEFAULTS = {"title": "Implementation plan", "acceptance": None, "phases": {99: "Manual, operator only"}}
MAX_SECTIONS_PER_FILE = 55
MAX_ITEMS_PER_SECTION = 30
MAX_DELIVERABLE_LEN = 88
# Every Markdown table row at or under this many characters, so rows never wrap in raw view (AGENTS.md).
MAX_TABLE_ROW = 100


class Refused(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Refused(message)


def read_text(path):
    return Path(path).read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = data if isinstance(data, bytes) else data.encode("utf-8")
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def normalize(value, domain, todo):
    m = REF.fullmatch(value.strip().strip("`"))
    require(m is not None, f"invalid section reference: {value}")
    return f"D{m['d'] or domain} T{m['t'] or todo} §{m['s']}"


def find_ref(text, domain, todo):
    """The section the whole text names (surrounding spaces and backticks aside), or None: a reference with anything
    run into it does not parse, so a malformed one is never read as a neighbouring section."""
    m = REF.fullmatch(text.strip().strip("`"))
    if m is None:
        return None
    return f"D{m['d'] or domain} T{m['t'] or todo} §{m['s']}"


def xref_target(text, domain, todo):
    """The section the text right after one "-> XREF:" names, or None when it is not exactly one reference."""
    m = XREF_TARGET.match(text)
    return f"D{m['d'] or domain} T{m['t'] or todo} §{m['s']}" if m else None


def extract_ref(text, rows):
    """Resolve whatever the caller had in front of them: a DNN TNN §N reference, a pasted plan row,
    or a '<path> §N' pair (POSIX or Windows path). Returns (ref_or_None, exit_code): 1 no such
    section, 2 no reference."""
    normalized = text.replace("\\", "/")
    # A reference run into more text ("§1oops", "§1.5") is not a reference to §1.
    m = re.search(r"D(\d{2})\s+T(\d{2})\s+§([1-9]\d*)(?![\w§]|\.\d)", normalized)
    if m:
        ref = f"D{m[1]} T{m[2]} §{int(m[3])}"
        return (ref, 0) if ref in rows else (ref, 1)
    m = re.search(r"(\d{2})-[a-z0-9-]+/TODO-(\d{2})-[a-z0-9-]+\.md\s*§([1-9]\d*)(?![\w§]|\.\d)", normalized)
    if m:
        ref = f"D{m[1]} T{m[2]} §{int(m[3])}"
        return (ref, 0) if ref in rows else (ref, 1)
    return None, 2


def field(body, name, required=True):
    empty = re.findall(r"^(?:> )?\*\*" + re.escape(name) + r":\*\*[ \t]*$", body, re.M)
    require(not empty, f"missing {name} field")
    values = re.findall(r"^(?:> )?\*\*" + re.escape(name) + r":\*\*[ \t]*(.+)$", body, re.M)
    require(len(values) <= 1, f"duplicate {name} field")
    require(values or not required, f"missing {name} field")
    return values[0].strip() if values else ""


@dataclass
class Section:
    ref: str
    path: str
    number: int
    title: str
    phase: int
    depends: list
    needs: list
    done: bool
    status: str
    body: str
    receipt: str
    order: int = 0

    def public(self):
        return {k: v for k, v in asdict(self).items() if k != "body"}


def front_matter(text, relative):
    parts = text.split("---\n", 2)
    require(len(parts) == 3 and not parts[0], f"missing frontmatter: {relative}")
    front = {}
    for line in parts[1].splitlines():
        m = re.fullmatch(r"([a-z_]+):\s*(.+)", line)
        require(m is not None and m[1] not in front, f"invalid or duplicate frontmatter: {relative}")
        front[m[1]] = m[2].strip().strip('"')
    return front, parts[2]


def git():
    """git from the absolute PATH entries only (review-dispatch's find_cli): a bare name is searched for in the working
    directory first on Windows, where a repository could hold its own git.exe."""
    found = review_dispatch().find_cli("git")
    require(found is not None, "git is not on PATH")
    return found


def commit_ok(root, sha):
    kind = subprocess.run([git(), "-C", str(root), "cat-file", "-t", sha],
                          capture_output=True, text=True, timeout=30)
    require(kind.returncode == 0 and kind.stdout.strip() == "commit", "not a commit: " + sha)
    on_branch = subprocess.run([git(), "-C", str(root), "merge-base", "--is-ancestor", sha, "HEAD"],
                               capture_output=True, timeout=30)
    require(on_branch.returncode == 0, "commit is not on this branch: " + sha)


def _head_commits(root):
    res = subprocess.run([git(), "-C", str(root), "rev-list", "HEAD"],
                         capture_output=True, text=True, timeout=30)
    require(res.returncode == 0, f"git repository with HEAD commit required for stamped sections: {root}")
    return set(res.stdout.splitlines())


def receipt_ok(root, receipt, ref, stamp_sha, commits=None):
    require(re.fullmatch(r"docs/reviews/[a-z0-9][a-z0-9.-]*\.json", receipt or "") is not None,
            f"invalid receipt path: {ref}")
    path = Path(root) / receipt
    require(path.is_file() and not path.is_symlink(), f"missing receipt: {ref}")
    try:
        data = json.loads(read_text(path))
    except ValueError:
        raise Refused(f"receipt is not JSON: {ref}") from None
    receipt_data_ok(data, ref, stamp_sha, root=root)
    if commits is None or stamp_sha not in commits:
        commit_ok(root, stamp_sha)


_REVIEW_DISPATCH = []


def review_dispatch():
    """scripts/review-dispatch.py as a module (its file name is not importable), loaded once."""
    if not _REVIEW_DISPATCH:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "review_dispatch", Path(__file__).resolve().parents[1] / "review-dispatch.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _REVIEW_DISPATCH.append(module)
    return _REVIEW_DISPATCH[0]


def receipt_digest(data):
    """The SHA-256 of a receipt's content, independent of key order, spacing and line endings."""
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def legacy_receipts(root):
    """ref -> digest of every receipt written before rounds_spent existed; empty when the file is absent."""
    path = Path(root) / LEGACY_RECEIPTS
    if not path.is_file():
        return {}
    try:
        data = json.loads(read_text(path))
    except ValueError:
        raise Refused(f"{LEGACY_RECEIPTS} is not JSON") from None
    receipts = data.get("receipts") if isinstance(data, dict) and data.get("schema_version") == 1 else None
    require(isinstance(receipts, dict) and all(isinstance(k, str) and isinstance(v, str)
                                               and re.fullmatch(r"[0-9a-f]{64}", v) for k, v in receipts.items()),
            f"{LEGACY_RECEIPTS} needs schema_version 1 and receipts mapping each ref to a SHA-256 digest")
    return receipts


def receipt_data_ok(data, ref, stamp_sha, root=None, building=False):
    """building: stamp's first pass over its arguments, before it adds rounds_spent and round_cap."""
    require(isinstance(data, dict), f"receipt is not an object: {ref}")
    require(data.get("ref") == ref and data.get("implementation_sha") == stamp_sha,
            f"receipt does not match its stamp: {ref}")
    rounds = data.get("reviews")
    require(isinstance(rounds, list) and rounds and all(
        isinstance(r, dict) and type(r.get("round")) is int and r["round"] >= 1
        and isinstance(r.get("report"), str) and r["report"]
        and isinstance(r.get("verdict"), str) and r["verdict"] in VERDICTS for r in rounds),
        f"receipt has no valid review rounds (verdict one of {', '.join(sorted(VERDICTS))}): {ref}")
    require(all(r["round"] > SEVERITY_CUTOFF_ROUND for r in rounds if r["verdict"] == "stopped-low-severity"),
            f"stopped-low-severity is allowed only after round {SEVERITY_CUTOFF_ROUND}: {ref}")
    if root is not None:
        root_path = Path(root)
        root_resolved = root_path.resolve()
        for r in rounds:
            raw_report = r["report"]
            report = Path(raw_report)
            require(re.fullmatch(r"docs/reviews/[A-Za-z0-9_./-]+\.md", raw_report) is not None
                    and not report.is_absolute() and not report.drive and not report.root
                    and ".." not in report.parts,
                    f"invalid review report path ({raw_report}): {ref}")
            # A completion review judges the plan before the build, never the implementation (D00 T03 §13).
            require(not raw_report.endswith("-completion.md"),
                    f"{raw_report} is a completion record, not a review of the implementation: {ref}")
            cur = root_path
            for part in report.parts:
                cur = cur / part
                require(not cur.is_symlink(), f"invalid review report path ({raw_report}): {ref}")
            report_path = root_path / report
            require(report_path.is_file()
                    and report_path.resolve().is_relative_to(root_resolved)
                    and bool(read_text(report_path).strip()),
                    f"missing or empty review report ({raw_report}): {ref}")
    # Receipts written since 2026-10-21 record the rounds spent against the cap, and what was done when a review
    # stopped at the cap; earlier receipts carry neither field.
    if "rounds_spent" not in data and not building:
        # Dropping the field must not dodge the checks below: an old receipt holds only what the old process wrote.
        require(all(r["verdict"] in LEGACY_VERDICTS for r in rounds) and max(r["round"] for r in rounds) <= 3
                and "round_cap" not in data and "cap_outcome" not in data,
                f"a receipt without rounds_spent may only hold rounds 1 to 3 with verdicts "
                f"{', '.join(sorted(LEGACY_VERDICTS))}: {ref}")
        require(root is not None and legacy_receipts(root).get(ref) == receipt_digest(data),
                f"a receipt without rounds_spent must be one of the old receipts {LEGACY_RECEIPTS} freezes: {ref}")
    if "rounds_spent" in data:
        spent, cap = data.get("rounds_spent"), data.get("round_cap")
        require(type(spent) is int and spent >= max(r["round"] for r in rounds)
                and type(cap) is int and cap in EARLIER_CAPS | {REVIEW_ROUND_CAP},
                f"receipt rounds_spent or round_cap is invalid: {ref}")
        # A cap stop is the current cap, reached: stopped-at-3, -8 and -13 belong to receipts older than this field.
        require(all(r["verdict"] == f"stopped-at-{cap}" for r in rounds if r["verdict"].startswith("stopped-at-")),
                f"a stopped-at verdict must be stopped-at-{cap}: {ref}")
        if root is not None:
            # A claimed round is one scripts/review-dispatch.py recorded with a reviewer, read by the dispatcher's own
            # reader, so a report it would refuse is no evidence here either.
            # The reviewer must also be of another model family than the writer (a self-review is not a round), and
            # must have returned a review: one ending in the prompt's OVERALL approve or needs-attention line, not an
            # empty or blocked reply. Reports are read as the dispatcher wrote them, "\r" bytes and all.
            dispatch = review_dispatch()
            for report in dict.fromkeys(r["report"] for r in rounds):
                recorded = dispatch.read_rounds((Path(root) / report).read_bytes().decode("utf-8"))
                require(recorded is not None, f"{report} is not a findings file the dispatcher can read: {ref}")
                # The dispatcher numbers rounds 1, 2, 3 in order; a repeated or reordered number would let one round
                # stand in for others when they are keyed by number below.
                numbers = [e["number"] for e in recorded]
                require(numbers == list(range(1, len(numbers) + 1)),
                        f"{report} must number its rounds 1 to {len(numbers)} in order, once each: {ref}")
                # A returned review: a reviewer of another model family than the writer ran and replied with the
                # prompt's OVERALL approve or needs-attention line. Outages, self-reviews, empty and blocked replies are
                # recorded rounds but not reviews: they earn no stop and end no loop.
                reviewed = {e["number"]: e for e in recorded if e["reviewer"]
                            and e["writer"] in dispatch.WRITER_FAMILY
                            and dispatch.FAMILY.get(e["cli"]) not in (None, dispatch.WRITER_FAMILY[e["writer"]])
                            and ([x.strip() for x in e["review"].splitlines() if x.strip()] or [""])[-1]
                            in ("OVERALL: approve", "OVERALL: needs-attention")}
                # A findings file is one implementation review loop: a completion review (D00 T03 §13) recorded in it
                # would count toward the cap and the severity cutoff without reviewing the implementation.
                mixed = [e["number"] for e in recorded if "PURPOSE: completion"
                         in [x.strip() for x in (e["review"] or "").splitlines() if x.strip()][:2]]
                require(not mixed, f"{report} holds completion review round(s) {mixed}; completion reviews belong in "
                                   f"the section's -completion.md record, not an implementation review loop: {ref}")
                require(reviewed, f"{report} holds no returned review: {ref}")
                # The cap bounds every loop, however it ends: a clean round after review 22 is past the cap.
                require(len(reviewed) <= cap,
                        f"{report} holds {len(reviewed)} returned reviews, over the {cap}-round cap: {ref}")
                claimed = sorted((r for r in rounds if r["report"] == report), key=lambda r: r["round"])
                for r in claimed:
                    e = reviewed.get(r["round"])
                    last = ([x.strip() for x in e["review"].splitlines() if x.strip()] or [""])[-1] if e else ""
                    require(e is not None and e["writer"] in dispatch.WRITER_FAMILY
                            and dispatch.FAMILY.get(e["cli"]) not in (None, dispatch.WRITER_FAMILY[e["writer"]])
                            and last == ("OVERALL: approve" if r["verdict"] == "clean" else "OVERALL: needs-attention"),
                            f"round {r['round']} is not a review returned by another model family with a verdict "
                            f"matching {r['verdict']} (clean needs OVERALL: approve, any other needs-attention) in "
                            f"{report}: {ref}")
                    # A severity stop is for a round whose findings are all P3 or advisory. The reviewer, who tags each
                    # finding (an untagged one counts as P1), declares the highest on the line before OVERALL; reading
                    # severities back out of free prose would guess where the reviewer already said.
                    lines = [x.strip() for x in e["review"].splitlines() if x.strip()]
                    require(r["verdict"] != "stopped-low-severity" or (len(lines) >= 2 and lines[-2] == "HIGHEST: P3"),
                            f"round {r['round']} does not declare HIGHEST: P3 before its OVERALL line, so it cannot "
                            f"stop on severity: {ref}")
                    # Stopping is earned by reviews returned: a round that returned no review (an outage) does not
                    # count toward the severity cutoff or the cap.
                    returned = sum(1 for n in reviewed if n <= r["round"])
                    require(r["verdict"] != "stopped-low-severity" or returned > SEVERITY_CUTOFF_ROUND,
                            f"round {r['round']} follows only {returned} returned reviews, so it cannot stop on "
                            f"severity before {SEVERITY_CUTOFF_ROUND + 1}: {ref}")
                    require(not r["verdict"].startswith("stopped-at-") or returned == cap,
                            f"round {r['round']} follows {returned} returned reviews; a cap stop is the round that "
                            f"returns review {cap}: {ref}")
                # Each findings file is one review loop, and the loop's end is its last reviewed round: the receipt
                # must name it, and it must be clean or a stop, so no later failing review can be left out. Nothing may
                # be recorded after it either: a round run later (even one that returned no review) was run on work
                # the earlier verdict does not cover, so an outage at the end means no stamp until a review returns.
                require(max(reviewed) == len(recorded),
                        f"the review loop in {report} ends with round {len(recorded)}, which returned no review; "
                        f"run another round before stamping: {ref}")
                require(claimed[-1]["round"] == max(reviewed)
                        and (claimed[-1]["verdict"] == "clean" or claimed[-1]["verdict"].startswith("stopped-")),
                        f"the review loop in {report} must end at its last reviewed round ({max(reviewed)}), clean or "
                        f"stopped, and the receipt must name that round: {ref}")
            # The count the receipt reports is the count the findings files hold, so query rounds sums real rounds.
            require(spent == rounds_recorded(root, rounds),
                    f"receipt rounds_spent {spent} is not the {rounds_recorded(root, rounds)} rounds its findings files "
                    f"record: {ref}")
        stopped = any(r["verdict"].startswith("stopped-") for r in rounds)
        outcome = data.get("cap_outcome")
        require((isinstance(outcome, str) and bool(outcome.strip())) == stopped,
                f"receipt needs cap_outcome exactly when a review stopped (at the cap or on severity): {ref}")
        # Receipts written under the 33-round cap name the completion record the section was built from (D00 T03 §13);
        # earlier receipts predate the completion review and carry none.
        if cap == REVIEW_ROUND_CAP:
            require(isinstance(data.get("completion"), str),
                    f"a receipt under the {REVIEW_ROUND_CAP}-round cap must name its completion record: {ref}")
            if root is not None:
                completion_ok(root, ref, data["completion"])
        else:
            require("completion" not in data, f"a receipt under the {cap}-round cap predates completion records: {ref}")
    checks = data.get("checks")
    require(isinstance(checks, list) and checks and all(isinstance(c, str) and c.strip() for c in checks),
            f"receipt has no checks: {ref}")
    require(isinstance(data.get("date"), str)
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}", data["date"]) is not None,
            f"receipt has no valid date: {ref}")


def adjacency_of(body, relative, domain, todo):
    """Parse the one **Adjacency:** line inside ## Outcome. Returns {key: (state, owner_ref_or_None)}."""
    require("## Outcome\n" in body, f"missing Outcome: {relative}")
    outcome = body.split("## Outcome\n", 1)[1].split("\n## ", 1)[0]
    lines = re.findall(r"^\*\*Adjacency:\*\*\s*(.+)$", outcome, re.M)
    require(len(lines) == 1, f"exactly one Adjacency line inside Outcome required: {relative}")
    result = {}
    blanket = re.fullmatch(r"all=not-applicable\s*\((.+)\)", lines[0].strip())
    if blanket:
        require(blanket[1].strip(), f"adjacency blanket needs a reason: {relative}")
        return {key: ("not-applicable", None) for key in ADJACENCY_KEYS}
    entries = [e.strip() for e in re.split(r";\s*(?=[a-z]+=)", lines[0]) if e.strip()]
    for entry in entries:
        m = re.fullmatch(r"([a-z]+)=applicable(?:\s*@\s*(.+))?", entry)
        if m:
            key, owner = m[1], None
            require(key in ADJACENCY_KEYS and key not in result,
                    f"adjacency key unknown or duplicated ({key}): {relative}")
            if m[2]:
                owner = find_ref(m[2], domain, todo)
                require(owner is not None, f"adjacency owner does not parse ({entry}): {relative}")
            result[key] = ("applicable", owner)
            continue
        m = re.fullmatch(r"([a-z]+)=not-applicable\s*\(([^)]+)\)", entry)
        require(m is not None, f"adjacency entry malformed ({entry}): {relative}")
        key = m[1]
        require(key in ADJACENCY_KEYS and key not in result,
                f"adjacency key unknown or duplicated ({key}): {relative}")
        require(m[2].strip(), f"adjacency not-applicable needs a reason ({key}): {relative}")
        result[key] = ("not-applicable", None)
    require(set(result) == set(ADJACENCY_KEYS),
            f"adjacency must declare every key exactly once (missing "
            f"{', '.join(sorted(set(ADJACENCY_KEYS) - set(result)))}): {relative}")
    return result


def xrefs_of(body, domain, todo):
    refs = []
    for line in body.splitlines():
        # Every XREF on the line, each read strictly: a malformed one refuses instead of resolving to whatever
        # reference text happens to follow it.
        for tail in line.split("-> XREF:")[1:]:
            ref = xref_target(tail, domain, todo)
            require(ref is not None, f"XREF must name exactly one well-formed section: {line.strip()}")
            refs.append(ref)
    return refs


def graph(root=ROOT):
    """Parse every TODO file strictly; a malformed row or section refuses, it is never read as empty."""
    root = Path(root)
    plan_config(root)
    sections, ids, files = {}, {}, {}
    head_commits = None
    paths = sorted((root / "todo").glob("[0-9][0-9]-*/TODO-*.md"))
    require(bool(paths), "canonical TODO tree is missing or empty")
    for path in paths:
        require(not path.is_symlink(), f"symlink TODO: {path}")
        relative = path.relative_to(root).as_posix()
        name = re.fullmatch(r"TODO-(\d{2})-[a-z0-9-]+\.md", path.name)
        require(name is not None, f"invalid TODO filename: {relative}")
        d, t = path.parent.name[:2], name[1]
        front, body = front_matter(read_text(path), relative)
        required = {"schema_version", "id", "domain", "status", "title"}
        optional = {"depends_on", "frozen", "track", "superseded_by"}
        require(required <= front.keys() and not front.keys() - required - optional,
                f"frontmatter fields: {relative}")
        require(front["schema_version"] == "1" and front["domain"] == path.parent.name,
                f"schema/domain mismatch: {relative}")
        require(re.fullmatch(r"[a-z][a-z0-9-]{0,58}[a-z0-9]", front["id"])
                and front["id"] not in ids, f"invalid/duplicate id: {relative}")
        require(front["status"] in STATUSES, f"unknown status: {relative}")
        frozen = front.get("frozen", "false")
        require(frozen in {"true", "false"}, f"frozen must be true or false: {relative}")
        file_deps = json.loads(front.get("depends_on", "[]"))
        require(isinstance(file_deps, list) and all(isinstance(x, str) for x in file_deps),
                "depends_on must be a JSON string array")
        require(re.search(r"\A\n*# TODO-\d{2} -- .+\n", body) is not None,
                f"missing TODO heading: {relative}")
        ids[front["id"]] = relative
        files[relative] = (front, file_deps, [], xrefs_of(body, d, t),
                           adjacency_of(body, relative, d, t))
        for label in ("Goal", "Current state"):
            field(body, label)
        for label in ("Inputs", "Outcome", "Implementation Order", "Verification"):
            require(f"## {label}\n" in body, f"missing {label}: {relative}")
        table = body.split("## Implementation Order\n", 1)[1].split("\n## ", 1)[0]
        rows, orders = {}, []
        for line in table.splitlines():
            if not line.startswith("|"):
                # A row written without its leading pipe would otherwise vanish from the graph.
                require("|" not in line, f"implementation table line without a leading pipe: {relative}")
                continue
            m = ROW.fullmatch(line)
            if not m:
                require("§" not in line and "[" not in line,
                        f"malformed implementation row: {relative}")
                continue
            order, n = int(m[1]), int(m[2])
            require(n not in rows, f"duplicate section row: {relative} §{n}")
            orders.append(order)
            rows[n] = m
        require(rows and orders == list(range(1, len(rows) + 1)),
                f"invalid implementation order: {relative}")
        require(len(rows) <= MAX_SECTIONS_PER_FILE,
                f"over {MAX_SECTIONS_PER_FILE} sections; split into a new file: {relative}")
        headings = list(re.finditer(r"^## (\d+)\. (.+)$", body, re.M))
        numbers = [int(m[1]) for m in headings]
        require(all(n >= 1 for n in numbers) and numbers == sorted(set(numbers)) and set(numbers) == set(rows),
                f"row/body mismatch: {relative}")
        require(body.rfind("## Verification\n") > headings[-1].start(),
                f"Verification must follow numbered sections: {relative}")
        # The level-two headings are exactly the format's, once each and in order: any other, or a repeat, would end
        # the section above it early and hide what follows from the graph.
        level_two = re.findall(r"^##(?:[ \t].*)?$", body, re.M)
        numbered = [line for line in level_two if re.fullmatch(r"## \d+\. \S.*", line)]
        require(level_two == ["## Inputs", "## Outcome", "## Implementation Order", *numbered, "## Verification"],
                f"level-two headings must be Inputs, Outcome, Implementation Order, the sections and Verification, "
                f"once each and in that order: {relative}")
        for h in headings:
            n = int(h[1])
            section_body = body[h.end():].split("\n## ", 1)[0].strip()
            ref = f"D{d} T{t} §{n}"
            require(ref not in sections, f"duplicate address: {ref}")
            deliverable, title = rows[n][3].strip(), h[2].strip()
            require(len(deliverable) <= MAX_DELIVERABLE_LEN and len(title) <= MAX_DELIVERABLE_LEN,
                    f"deliverable/title over {MAX_DELIVERABLE_LEN} chars (wraps raw md table): {ref}")
            phase = field(section_body, "Phase")
            require(phase.isdigit() and int(phase) in PHASES, f"invalid Phase: {ref}")
            raw = field(section_body, "Needs")
            needs = [] if raw == "none" else [v.strip() for v in raw.split(",")]
            require(len(needs) == len(set(needs)) and set(needs) <= NEEDS,
                    f"unknown/duplicate Needs: {ref}")
            dep = rows[n][4].strip()
            deps = [] if dep == "--" else [normalize(v, d, t) for v in dep.split(",")]
            require(len(deps) == len(set(deps)), f"duplicate dependency: {ref}")
            for line in section_body.splitlines():
                # Every checklist-shaped line (a list marker and a box, quoted, numbered or indented) must be the one
                # form the graph counts, so no item can hide in another spelling.
                if re.match(r"^[\s>]*(?:[-*+]|\d+[.)])[ \t]*\[[^\]\n]*\](?!\()", line):
                    require(re.fullmatch(r"- \[([ x])\] \S.*", line) is not None,
                            f"malformed checklist item: {ref}")
            require("**Build order:**\n" in section_body and "\n- [" in section_body,
                    f"executable Build order required: {ref}")
            after_bo = section_body.split("**Build order:**\n", 1)[1]
            for line in after_bo.splitlines():
                if re.match(r"^\s*[-*+](\s|$)", line):
                    require(re.fullmatch(r"- \[([ x])\] \S.*", line) is not None,
                            f"malformed checklist item: {ref}")
            build_block = after_bo.split("\n- [", 1)[0]
            non_empty_bo = [line for line in build_block.splitlines() if line.strip()]
            build_matches = list(re.finditer(r"^(\d+)\. (\S.+)$", build_block, re.M))
            build_steps = [int(m[1]) for m in build_matches]
            require(build_steps and len(build_steps) == len(non_empty_bo)
                    and build_steps == list(range(1, len(build_steps) + 1))
                    and all("Done when:" in m[2] for m in build_matches),
                    f"executable Build order required: {ref}")
            checks = re.findall(r"^- \[([ x])\] (.+)$", section_body, re.M)
            require(2 <= len(checks) <= MAX_ITEMS_PER_SECTION
                    and checks[-1][1].startswith("Commit:")
                    and not any(c[1].startswith("Commit:") for c in checks[:-1]),
                    f"2-{MAX_ITEMS_PER_SECTION} items (at least one work item, Commit last) required: {ref}")
            require("`" in field(section_body, "Test checkpoint"),
                    f"runnable Test checkpoint required: {ref}")
            surface = field(section_body, "Surface")
            require(surface in {"yes", "no"}, f"Surface must be yes/no: {ref}")
            if surface == "yes":
                for label in ("Fidelity", "Job", "Treatment", "Chrome"):
                    field(section_body, label)
            freeze_check = field(section_body, "Freeze check", False)
            require(bool(freeze_check) == (frozen == "true"),
                    f"Freeze check must match frozen frontmatter: {ref}")
            done = rows[n][5] == "x"
            stamp_line = field(section_body, "Verified", False)
            receipt = field(section_body, "Review", False).strip("`")
            require(done == bool(stamp_line) == bool(receipt),
                    f"checkbox/stamp/receipt mismatch: {ref}")
            if done:
                require(all(x[0] == "x" for x in checks), f"unfinished stamped checklist: {ref}")
                require(not set(needs) & WAITING, f"stamped section has a waiting Need: {ref}")
                m = re.fullmatch(r"\d{4}-\d{2}-\d{2} \| §" + str(n) + r" \| ([0-9a-f]{40})", stamp_line)
                require(m is not None, f"invalid stamp: {ref}")
                if head_commits is None:
                    head_commits = _head_commits(root)
                receipt_ok(root, receipt, ref, m[1], head_commits)
            sections[ref] = Section(ref, relative, n, h[2], int(phase), deps, needs, done,
                                    front["status"], section_body, receipt, int(rows[n][1]))
            files[relative][2].append(ref)
    for relative, (front, file_deps, refs, xrefs, adjacency) in files.items():
        require(len(set(file_deps)) == len(file_deps), f"duplicate file dependencies: {relative}")
        for dep in file_deps:
            require(dep in ids and ids[dep] != relative,
                    f"unresolved/self file dependency: {relative}")
            for ref in refs:
                sections[ref].depends = list(dict.fromkeys(
                    sections[ref].depends + files[ids[dep]][2]))
        if front["status"] == "superseded":
            successor = front.get("superseded_by", "")
            require(successor in ids and ids[successor] != relative,
                    f"superseded TODO must name its successor: {relative}")
        else:
            require((front["status"] == "done") == all(sections[r].done for r in refs),
                    f"file status disagrees with stamps: {relative}")
        for key, (state, owner) in adjacency.items():
            if owner is not None:
                require(owner in sections, f"adjacency owner unresolved ({key} @ {owner}): {relative}")
        for target in xrefs:
            require(target in sections, f"unresolved XREF target {target}: {relative}")
            target_file = sections[target].path
            if target_file == relative:
                continue
            back = files[target_file][3]
            require(any(sections[b].path == relative for b in back if b in sections),
                    f"one-sided XREF {target} has no pointer back: {relative}")
    # Deferrals carry an owner or they are abandonments; a shipped owner makes a live deferral stale.
    for row in sections.values():
        # Only a blockquoted marker is read below; any other spelling would drop the deferral from every check.
        for line in row.body.splitlines():
            require(len(re.findall(r"\*\*(?:Deferred|Resolved):\*\*", line)) <= 1,
                    f"one Deferred or Resolved marker per line: {row.ref}")
            if re.search(r"\*\*(?:Deferred|Resolved):\*\*", line):
                require(re.match(r"> \*\*(?:Deferred|Resolved):\*\*[ \t]*\S", line) is not None,
                        f"a Deferred or Resolved marker must open a blockquote line and say something: {row.ref}")
        for marker in ("Deferred", "Resolved"):
            for line in re.findall(r"^> \*\*" + marker + r":\*\*[ \t]*(\S.*)$", row.body, re.M):
                owner = xref_target(line.split("-> XREF:", 1)[1], row.ref[1:3], row.ref[5:7]) \
                    if "-> XREF:" in line else None
                require(owner is not None and owner in sections,
                        f"{marker} without a resolving owner: {row.ref}")
                if marker == "Deferred":
                    require(not sections[owner].done,
                            f"stale deferral, owner {owner} shipped; close it as Resolved: {row.ref}")
    # A stamped completion record's filed references resolve against the whole graph, known only now (D00 T03 §13).
    for sec in sections.values():
        if sec.done and sec.receipt:
            data = json.loads(read_text(Path(root) / sec.receipt))
            if isinstance(data, dict) and isinstance(data.get("completion"), str):
                completion_ok(root, sec.ref, data["completion"], rows=sections)
    _index_coverage(root, files)
    visiting, visited = set(), set()
    for start in sections:
        if start in visited:
            continue
        stack = [(start, 0)]
        visiting.add(start)
        while stack:
            ref, idx = stack[-1]
            deps = sections[ref].depends
            if idx < len(deps):
                dep = deps[idx]
                stack[-1] = (ref, idx + 1)
                require(dep in sections, f"unresolved dependency: {dep}")
                require(dep not in visiting, f"dependency cycle: {dep}")
                require(sections[dep].phase <= sections[ref].phase,
                        f"prerequisite in later phase: {ref} -> {dep}")
                # A stamped section may sit on an open prerequisite only when an audit reopened that prerequisite
                # (its Unstamped note): the consumer is then suspect until the prerequisite re-stamps, not unstamped.
                require(not sections[ref].done or sections[dep].done
                        or re.search(r"^> \*\*Unstamped:\*\* ", sections[dep].body, re.M) is not None,
                        f"stamped section has open dependency: {ref}")
                if dep not in visited:
                    visiting.add(dep)
                    stack.append((dep, 0))
            else:
                stack.pop()
                visiting.remove(ref)
                visited.add(ref)
    return sections


def _index_coverage(root, files):
    root_index = root / "todo/TODO-00-INDEX.md"
    require(root_index.is_file(), "missing todo/TODO-00-INDEX.md")
    root_text = read_text(root_index)
    by_domain = {}
    for relative in files:
        by_domain.setdefault(Path(relative).parent.name, []).append(Path(relative).name)
    for domain, names in by_domain.items():
        index = root / "todo" / domain / "INDEX.md"
        require(index.is_file(), f"missing domain index: todo/{domain}/INDEX.md")
        text = read_text(index)
        for filename in names:
            require(filename in text, f"missing from domain index: {domain}/{filename}")
            require(f"{domain}/{filename}" in root_text, f"missing from root index: {domain}/{filename}")


def settled(ref, rows):
    """A prerequisite that holds: it and every section it depends on, however far back, are stamped. A stamp on top of
    an ancestor an audit reopened is suspect, so new work may not build on it."""
    stack, seen = [ref], set()
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        if not rows[current].done:
            return False
        stack.extend(rows[current].depends)
    return True


def disposition(row, rows):
    """0 ready, 3 already verified, 4 waiting (inactive file, open or suspect prerequisite, or a person to answer)."""
    if row.done:
        return 3
    if row.status != "active" or set(row.needs) & WAITING \
            or any(not settled(d, rows) for d in row.depends):
        return 4
    return 0


def ordered(sections):
    result, placed, pending = [], set(), sorted(
        sections, key=lambda r: (sections[r].phase, sections[r].path, sections[r].order))
    while pending:
        ref = next(r for r in pending if all(d in placed for d in sections[r].depends))
        result.append(ref)
        placed.add(ref)
        pending.remove(ref)
    return [sections[r] for r in result]


def markdown_table(headers, rows):
    cells = [headers, *rows]
    widths = [max(3, *(len(row[i]) for row in cells)) for i in range(len(headers))]

    def render(row):
        return "| " + " | ".join(cell.ljust(width) for cell, width in zip(row, widths)) + " |"

    return [render(headers), render(["-" * width for width in widths]),
            *(render(row) for row in rows)]


def plan_config(root=ROOT):
    """The project's plan title, acceptance bar and phase names from todo/plan.json, loaded strictly."""
    path = Path(root) / PLAN_CONFIG
    if not path.is_file():
        return {**PLAN_DEFAULTS, "phases": dict(PLAN_DEFAULTS["phases"])}
    try:
        data = json.loads(read_text(path))
    except ValueError as exc:
        raise Refused(f"unreadable {PLAN_CONFIG}: {exc}") from None
    require(isinstance(data, dict) and set(data) <= {"title", "acceptance", "phases"},
            f"{PLAN_CONFIG} may only hold title, acceptance and phases")
    title = data.get("title", PLAN_DEFAULTS["title"])
    acceptance = data.get("acceptance")
    phases = data.get("phases", {})
    require(isinstance(title, str) and title.strip() != "", f"{PLAN_CONFIG}: title must be text")
    require(acceptance is None or (isinstance(acceptance, str) and acceptance.strip() != ""),
            f"{PLAN_CONFIG}: acceptance must be text or null")
    require(isinstance(phases, dict), f"{PLAN_CONFIG}: phases must map a phase number to its name")
    names = dict(PLAN_DEFAULTS["phases"])
    for key, name in phases.items():
        require(key.isdigit() and int(key) in PHASES, f"{PLAN_CONFIG}: unknown phase {key!r}")
        require(isinstance(name, str) and name.strip() != "", f"{PLAN_CONFIG}: phase {key} needs a name")
        names[int(key)] = name.strip()
    return {"title": title.strip(), "acceptance": acceptance.strip() if acceptance else None, "phases": names}


def projection(root=ROOT):
    all_rows = graph(root)
    rows = ordered(all_rows)
    config = plan_config(root)
    lines = [f"# {config['title']}", "",
             "Generated by `python scripts/todo-graph.py plan --sync`; do not edit by hand. Edit the "
             "TODO sections (including their Phase and Needs fields) and regenerate. The boxes below "
             "are a projection of each file's Implementation Order table and flip in exactly one "
             "place: the stamp written by review.", ""]
    if config["acceptance"]:
        lines += [f"The acceptance bar is {config['acceptance']}", ""]
    lines += ["Format and rules: `todo/README.md`. Run sections with the `process-plan`, "
              "`process-phase` and `process-todo-section` skills; "
              "`python scripts/todo-graph.py query ready` lists what can run now. Pasting a whole "
              "row from a table below into `process todo section:` is a complete instruction.", ""]
    checks = {row.ref: re.findall(r"^- \[([ x])\] (.+)$", row.body, re.M) for row in rows}
    for phase in sorted({row.phase for row in rows}):
        phase_rows = [row for row in rows if row.phase == phase]
        item_count = sum(len(checks[row.ref]) for row in phase_rows)
        name = config["phases"].get(phase)
        title = f"Phase {phase}: {name}" if name else f"Phase {phase}"
        lines += [f"### {title}", "", f"Sections: {len(phase_rows)} | Checklist items: {item_count}", ""]
        table = markdown_table(
            ["Status", "Reference", "Deliverable", "Needs", "Items"],
            [[f"[{'x' if row.done else ' '}]", row.ref, row.title,
              ", ".join(row.needs) or "none", str(len(checks[row.ref]))] for row in phase_rows],
        )
        # Every row is padded to the widest cell, so one long title wraps the whole table: name the widest section.
        widest = max(phase_rows, key=lambda row: len(row.title) + len(", ".join(row.needs)))
        require(all(len(line) <= MAX_TABLE_ROW for line in table),
                f"plan table for phase {phase} wraps raw md ({max(len(line) for line in table)} > {MAX_TABLE_ROW} "
                f"chars); shorten the heading and Deliverable of {widest.ref} (title {len(widest.title)} chars)")
        lines += table
        lines.append("")
    total_items = sum(len(items) for items in checks.values())
    completed_items = sum(state == "x" for items in checks.values() for state, _ in items)
    ready = sum(disposition(r, all_rows) == 0 for r in rows)
    lines += [f"Progress: {sum(r.done for r in rows)}/{len(rows)} verified sections, "
              f"{ready} ready to run now.", "",
              f"Checklist: {completed_items}/{total_items} items completed (includes Commit items).", ""]
    return "\n".join(lines)


def projections(root=ROOT, sync=False):
    expected = projection(root)
    target = Path(root) / PLAN
    if sync:
        atomic(target, expected)
    else:
        require(target.is_file() and read_text(target) == expected,
                f"stale projection: {PLAN}; run plan --sync")


def deferrals(root=ROOT):
    rows = graph(root)
    found = []
    for row in ordered(rows):
        for marker in ("Deferred", "Resolved"):
            for line in re.findall(r"^> \*\*" + marker + r":\*\*[ \t]*(\S.*)$", row.body, re.M):
                found.append({"ref": row.ref, "state": marker.lower(), "text": line.strip()})
    return found


def adjacency_report(root=ROOT):
    graph(root)  # validation is what makes the declarations trustworthy
    report = {}
    for path in sorted((Path(root) / "todo").glob("[0-9][0-9]-*/TODO-*.md")):
        relative = path.relative_to(root).as_posix()
        _, body = front_matter(read_text(path), relative)
        parsed = adjacency_of(body, relative, path.parent.name[:2],
                              re.fullmatch(r"TODO-(\d{2})-[a-z0-9-]+\.md", path.name)[1])
        report[relative] = {key: (state if owner is None else f"{state} @ {owner}")
                             for key, (state, owner) in parsed.items()}
    return report


def rounds_recorded(root, reviews):
    """Review rounds spent on a section, summed over its findings files (one per review loop): in each, the highest
    round the dispatcher recorded (an outage round that returned no review counts) or the highest round named for
    that file on the command line, whichever is higher."""
    spent = 0
    for report in dict.fromkeys(r["report"] for r in reviews):
        named = max(r["round"] for r in reviews if r["report"] == report)
        path = Path(root) / report
        text = path.read_bytes().decode("utf-8") if path.is_file() else ""  # as written: the dispatcher keeps "\r"
        # The dispatcher's reader, so a round heading quoted inside a review is not counted; a report it cannot read
        # (one older than its format) falls back to the headings, and a new receipt refuses such a report anyway.
        parsed = review_dispatch().read_rounds(text)
        recorded = [e["number"] for e in parsed] if parsed is not None else [int(n) for n in ROUND_RECORD.findall(text)]
        spent += max([named, *recorded])
    return spent


def review_rounds(root=ROOT):
    """Rounds spent per stamped section, from each receipt (or its findings files, for receipts older than the
    rounds_spent field), and a summary for tuning the cap."""
    root = Path(root)
    sections = []
    for row in ordered(graph(root)):
        if not row.done or not row.receipt:
            continue
        data = json.loads(read_text(root / row.receipt))
        spent = data.get("rounds_spent") or rounds_recorded(root, data["reviews"])
        sections.append({"ref": row.ref, "rounds_spent": spent, "round_cap": data.get("round_cap"),
                         "verdicts": [r["verdict"] for r in data["reviews"]],
                         "cap_outcome": data.get("cap_outcome")})
    spent = [s["rounds_spent"] for s in sections]
    return {"cap": REVIEW_ROUND_CAP, "sections": sections,
            "summary": {"stamped": len(sections), "rounds": sum(spent),
                        "mean": round(sum(spent) / len(spent), 2) if spent else None,
                        "max": max(spent, default=None),
                        "stopped_at_cap": sum(any(v.startswith("stopped-at-") for v in s["verdicts"])
                                              for s in sections),
                        "stopped_low_severity": sum("stopped-low-severity" in s["verdicts"] for s in sections)}}


def completion_name(ref):
    """The completion record's file name for a section: D00 T03 §13 -> D00-T03-s13-completion.md."""
    m = re.fullmatch(r"D(\d+) T(\d+) §(\d+)", ref)
    require(m is not None, f"not a section reference: {ref}")
    return f"D{m[1]}-T{m[2]}-s{m[3]}-completion.md"


def outside_rounds(text, dispatch):
    """The lines of a findings file the dispatcher's rounds do not hold: its heading and the outcome blocks written
    between rounds. Read only after read_rounds accepted the file, so every round is in the format record writes."""
    lines = [dispatch.canonical(line) for line in dispatch.raw_lines(text)]
    out, i = [], 0
    while i < len(lines):
        if not dispatch.ROUND_HEADING.match(lines[i]):
            out.append(lines[i])
            i += 1
            continue
        i += 2
        count = None
        while i < len(lines) and lines[i] != "":
            field = dispatch.ROUND_LINE.match(lines[i])
            if field and field.group(1).lower() == "lines":
                count = int(field.group(2))
            i += 1
        if count is not None:
            i += 1 + count
        else:
            while i < len(lines) and not lines[i].startswith("## Round"):
                i += 1
    return out


# D00 T03 §14: from this instant, when docs/completion-review-prompt.md first carried the `Contract:` line, a completion
# round must echo the digest of the contract it was given; earlier rounds are judged by the D00 T03 §13 rules.
CONTRACT_REQUIRED_FROM = "2026-10-23T09:40:00Z"
CONTRACT_LINE = re.compile(r"CONTRACT: (sha256:[0-9a-f]{64})")
INSTANT = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")


def contract_digest(row):
    """`sha256:<hex>` of a section's contract: its heading and body with every checkbox unticked and the Verified,
    Review, Started and Duration lines removed, so ticking, timing and stamping leave it unchanged and editing any
    wording changes it. A Deferred line counts: it moves scope to another section."""
    body = row.body.replace("\r\n", "\n")
    body = re.sub(r"^- \[x\] ", "- [ ] ", body, flags=re.M)
    body = re.sub(r"^> \*\*(?:Verified|Review|Started|Duration):\*\* .*(?:\n|$)", "", body, flags=re.M)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    text = f"## {row.number}. {row.title}\n\n{body}\n"
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _instant(text):
    """An ISO 8601 UTC instant (`YYYY-MM-DDTHH:MM:SSZ`) as a comparable tuple, or None."""
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z", (text or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None


def completion_ok(root, ref, path, rows=None):
    """The section's completion record (D00 T03 §13), or Refused. It is the dispatcher-written file named for the
    section, opening `# Completion review: <ref>`; its last returned round is a review by another model family that
    opens `SECTION: <ref>` and `PURPOSE: completion` and pairs `COMPLETE: yes` with `OVERALL: approve` (or
    `COMPLETE: no` with `needs-attention`); after `COMPLETE: no`, its `## Outcome (round N)` block gives every
    numbered gap `N. extended` or `N. filed -> DNN TNN §N`, and with `rows` each filed reference must be a section.
    Earlier rounds are history. Returns the last returned round as the dispatcher reads it."""
    root_path = Path(root)
    report = Path(path) if isinstance(path, str) else None
    require(report is not None and re.fullmatch(r"docs/reviews/[A-Za-z0-9_./-]+-completion\.md", path) is not None
            and not report.is_absolute() and ".." not in report.parts,
            f"invalid completion record path ({path}): {ref}")
    require(report.name == completion_name(ref),
            f"{path} is not the completion record of {ref} ({completion_name(ref)}): {ref}")
    cur = root_path
    for part in report.parts:
        cur = cur / part
        require(not cur.is_symlink(), f"invalid completion record path ({path}): {ref}")
    file = root_path / report
    require(file.is_file(), f"missing completion record ({path}): {ref}")
    text = file.read_bytes().decode("utf-8")
    dispatch = review_dispatch()
    recorded = dispatch.read_rounds(text)
    require(recorded is not None, f"{path} is not a findings file the dispatcher can read: {ref}")
    outside = outside_rounds(text, dispatch)
    heading = next((line.strip() for line in outside if line.strip()), "")
    require(heading == f"# Completion review: {ref}", f"{path} must open with '# Completion review: {ref}': {ref}")

    def last_line(entry):
        return ([x.strip() for x in entry["review"].splitlines() if x.strip()] or [""])[-1]

    returned = [e for e in recorded if e["reviewer"] and e["writer"] in dispatch.WRITER_FAMILY
                and dispatch.FAMILY.get(e["cli"]) not in (None, dispatch.WRITER_FAMILY[e["writer"]])
                and last_line(e) in ("OVERALL: approve", "OVERALL: needs-attention")]
    require(returned, f"{path} holds no completion review returned by another model family: {ref}")
    last = returned[-1]
    n = last["number"]
    lines = [x.strip() for x in last["review"].splitlines() if x.strip()]
    require(lines[:2] == [f"SECTION: {ref}", "PURPOSE: completion"],
            f"round {n} of {path} is not a completion review of {ref}: it must open with 'SECTION: {ref}' and "
            f"'PURPOSE: completion': {ref}")
    verdicts = [line for line in lines if line in ("COMPLETE: yes", "COMPLETE: no")]
    require(len(verdicts) == 1, f"round {n} of {path} must say COMPLETE: yes or COMPLETE: no exactly once: {ref}")
    complete = verdicts[0] == "COMPLETE: yes"
    require(complete == (lines[-1] == "OVERALL: approve"),
            f"round {n} of {path} pairs {verdicts[0]} with {lines[-1]}; COMPLETE: yes goes with OVERALL: approve and "
            f"COMPLETE: no with OVERALL: needs-attention: {ref}")
    if not complete:
        # Any numbered line counts, indented or not, `N.` or `N)`: a nested list asks for more dispositions, never
        # fewer, so no gap slips through on its formatting.
        numbers = [int(m.group(1)) for m in re.finditer(r"^\s*(\d+)[.)]\s", last["review"], re.M)]
        # A number used twice (two findings both `1.`, or a nested list restarting at `1)`) would let one disposition
        # answer two gaps, so the gaps must be numbered once each.
        seen, repeated = set(), set()
        for number in numbers:  # one pass: counting each number again would be quadratic on a long reply
            (repeated if number in seen else seen).add(number)
        require(not repeated, f"round {n} of {path} numbers more than one line {sorted(repeated)}; "
                              f"each gap needs its own number: {ref}")
        gaps = sorted(numbers)
        require(gaps, f"round {n} of {path} says COMPLETE: no but numbers no gap: {ref}")
        title = f"## Outcome (round {n})"
        require(title in [line.strip() for line in outside],
                f"{path} has no '{title}' giving the gaps of its last round a disposition: {ref}")
        start = [line.strip() for line in outside].index(title) + 1
        block = []
        for line in outside[start:]:
            if line.startswith("## "):
                break
            block.append(line.strip())
        dispositions = {}
        for line in block:
            m = re.fullmatch(r"(\d+)\. (?:extended|filed -> (D\d+ T\d+ §\d+))", line)
            if m:
                dispositions[int(m.group(1))] = m.group(2)
        missing = [g for g in gaps if g not in dispositions]
        require(not missing, f"gap {', '.join(map(str, missing))} of round {n} in {path} has no disposition "
                             f"('N. extended' or 'N. filed -> DNN TNN §N'): {ref}")
        if rows is not None:
            for gap, target in sorted(dispositions.items()):
                require(target is None or target in rows,
                        f"gap {gap} of round {n} in {path} is filed to {target}, which is no section: {ref}")
        last["dispositions"] = dispositions  # gap -> filed section, or None for `extended`
    return last


def stamp(root, ref, sha, reviews, checks, date, sync_plan=False, cap_outcome=None, completion=None):
    """Close a section: write its receipt, tick its row and checklist, add the Verified and Review lines. The receipt
    records the review rounds spent against the cap and, when a review stopped at the cap, what was done about it."""
    root = Path(root)
    rows = graph(root)
    require(ref in rows, "unresolved section: " + ref)
    row = rows[ref]
    require(not row.done, f"already verified: {ref}")
    require(all(settled(d, rows) for d in row.depends),
            f"open prerequisite, or one resting on a reopened section: {ref}")
    require(not set(row.needs) & WAITING,
            f"still waiting on {', '.join(sorted(set(row.needs) & WAITING))}: {ref}")
    require(re.fullmatch(r"[0-9a-f]{40}", sha) is not None,
            "the implementation SHA must be a full 40-character commit")
    commit_ok(root, sha)
    open_items = re.findall(r"^- \[ \] (?!Commit:)(.+)$", row.body, re.M)
    require(not open_items,
            f"unticked checklist items in {ref}: {open_items[0] if open_items else ''}")
    slug = re.sub(r"[^a-z0-9]+", "-", ref.lower().replace("§", "s")).strip("-")
    receipt = f"docs/reviews/{slug}.json"
    stopped = any(isinstance(r, dict) and str(r.get("verdict", "")).startswith("stopped-") for r in reviews)
    require(stopped == bool((cap_outcome or "").strip()),
            "--cap-outcome is required with a stopped verdict (what was done when the review stopped at the cap or on "
            "severity), and only then")
    data = {"ref": ref, "title": row.title, "implementation_sha": sha, "date": date,
            "reviews": reviews, "checks": checks}
    # Every argument is checked before anything is read or written.
    receipt_data_ok(data, ref, sha, root=root, building=True)
    data["rounds_spent"] = rounds_recorded(root, reviews)
    data["round_cap"] = REVIEW_ROUND_CAP
    # The completion review ran before the build (D00 T03 §13); after a reopen it must have run again since.
    require(isinstance(completion, str) and completion.strip(),
            f"--completion is required: the section's completion record, docs/reviews/<domain>/{completion_name(ref)}")
    last = completion_ok(root, ref, completion, rows)
    run = last["run"]
    # The completion review is the pinned reviewer's, as pinned now: its name, model and effort (a reviewer of another
    # family alone could be anyone).
    dispatch = review_dispatch()
    try:
        pin = dispatch.load_pin(Path(root) / ".conclave" / "reviewers.toml")
    except dispatch.Refused as exc:
        raise Refused(f"cannot read the reviewer pin to check {completion}: {exc}: {ref}") from None
    route = pin["routes"].get(last["writer"]) or []
    pinned = pin["reviewers"].get(route[0]) if route else None
    require(pinned is not None and last["reviewer"] == route[0] and last["model"] == pinned["model"]
            and last["effort"] == pinned.get("effort"),
            f"the completion review in {completion} was run by {last['reviewer']} ({last['model']}, {last['effort']}), "
            f"not the reviewer the pin names for {last['writer']}: {ref}")
    # D00 T03 §14: reopening is recorded to the second; a date-only note from before counts as the end of its day.
    reopened = [(_instant(x) or _instant(f"{x[:10]}T23:59:59Z"), x) for x in
                re.findall(r"^> \*\*Unstamped:\*\* (\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z)?)", row.body, re.M)]
    if reopened:
        latest = max(reopened)
        require(_instant(run) is not None and _instant(run) > latest[0],
                f"the completion review in {completion} ran {run}, not after the section was reopened at {latest[1]}; "
                f"run a fresh one: {ref}")
    # D00 T03 §14: a round from CONTRACT_REQUIRED_FROM on echoes the digest of the contract it was given, and that
    # must still be this section's contract: an edit after dispatch, or an extension after approval, needs a new round.
    if _instant(run) is not None and _instant(run) >= _instant(CONTRACT_REQUIRED_FROM):
        lines = [x.strip() for x in last["review"].splitlines() if x.strip()]
        echoed = CONTRACT_LINE.fullmatch(lines[2]) if len(lines) > 2 else None
        require(echoed is not None,
                f"round {last['number']} of {completion} must open with 'SECTION: {ref}', 'PURPOSE: completion' and "
                f"'CONTRACT: sha256:<digest>' copied from its prompt: {ref}")
        require(echoed[1] == contract_digest(row),
                f"round {last['number']} of {completion} reviewed contract {echoed[1]}, but the section is now "
                f"{contract_digest(row)}; it changed after its completion review, so run a fresh one: {ref}")
    # D00 T03 §14: an `extended` gap in the last returned round's outcome means its re-check has not returned yet,
    # whatever outage rounds came after it.
    pending = sorted(g for g, target in (last.get("dispositions") or {}).items() if target is None)
    require(not pending, f"round {last['number']} of {completion} extended gap {', '.join(map(str, pending))}, and its "
                         f"re-check has not returned; run it before the stamp: {ref}")
    data["completion"] = completion
    if stopped:
        data["cap_outcome"] = cap_outcome.strip()
    receipt_data_ok(data, ref, sha, root=root)
    receipt_path = root / receipt
    require(not receipt_path.exists(), f"receipt already exists: {receipt}")
    path = root / row.path
    original_bytes = path.read_bytes()
    original = read_text(path)
    text = original
    body = row.body
    new_body = re.sub(r"^- \[ \] (Commit:.+)$", r"- [x] \1", body, flags=M_FLAG)
    new_body += f"\n\n> **Verified:** {date} | §{row.number} | {sha}\n> **Review:** `{receipt}`"
    require(text.count(body) == 1, f"section body is not unique in {row.path}")
    text = text.replace(body, new_body)
    line = re.compile(r"^(\|\s*\d+\s*\|\s*§" + str(row.number) + r"\s*\|[^\n]*\|\s*)\[ \](\s*\|)$", re.M)
    require(len(line.findall(text)) == 1, f"implementation row not found: {ref}")
    text = line.sub(r"\1[x]\2", text)
    siblings = [r for r in rows.values() if r.path == row.path and r.ref != ref]
    if all(r.done for r in siblings):
        text, n = re.subn(r"\A(---\n(?:.*\n)*?)status: [a-z]+\n", r"\1status: done\n", text, count=1)
        require(n == 1, f"frontmatter status not found: {row.path}")
    plan_path = root / PLAN
    original_plan_bytes = plan_path.read_bytes() if plan_path.is_file() else None
    try:
        atomic(receipt_path, json.dumps(data, indent=2) + "\n")
        atomic(path, text)
        graph(root)
        if sync_plan or original_plan_bytes is not None:
            projections(root, sync=True)
    except BaseException:  # an interrupt between writes must roll back as an error does
        receipt_path.unlink(missing_ok=True)
        try:
            if not path.is_file() or path.read_bytes() != original_bytes:
                atomic(path, original_bytes)
        finally:
            if original_plan_bytes is not None:
                if not plan_path.is_file() or plan_path.read_bytes() != original_plan_bytes:
                    atomic(plan_path, original_plan_bytes)
            elif plan_path.exists():
                plan_path.unlink(missing_ok=True)
        raise
    return receipt


def unstamp(root, ref, reason, when):
    """Flip a stamped section back to open when an audit finds it regressed: remove its Verified and Review lines,
    untick its Commit item and row, reopen its file, and keep the receipt as evidence under a revoked name, with a dated
    Unstamped note in the section saying why. Re-stamping later writes a fresh receipt."""
    root = Path(root)
    rows = graph(root)
    require(ref in rows, "unresolved section: " + ref)
    row = rows[ref]
    require(row.done, f"not stamped: {ref}")
    require(bool(reason.strip()) and "\n" not in reason, "--reason must be one line saying what regressed")
    require(_instant(when) is not None, f"invalid instant (YYYY-MM-DDTHH:MM:SSZ): {when}")
    date = when[:10]
    stamp_lines = re.compile(r"\n\n> \*\*Verified:\*\* [^\n]*\n> \*\*Review:\*\* `[^`\n]*`")
    require(len(stamp_lines.findall(row.body)) == 1, f"stamp lines not found: {ref}")
    receipt_path = root / row.receipt
    revoked_path = receipt_path.with_name(f"{receipt_path.stem}.revoked-{date}.json")
    n = 2
    while revoked_path.exists():
        revoked_path = receipt_path.with_name(f"{receipt_path.stem}.revoked-{date}-{n}.json")
        n += 1
    revoked = revoked_path.relative_to(root).as_posix()
    body = stamp_lines.sub("", row.body)
    body = re.sub(r"^- \[x\] (Commit:.+)$", r"- [ ] \1", body, flags=re.M)
    body += f"\n\n> **Unstamped:** {when}: {reason.strip()} (revoked receipt `{revoked}`)"
    path = root / row.path
    original_bytes = path.read_bytes()
    text = read_text(path)
    require(text.count(row.body) == 1, f"section body is not unique in {row.path}")
    text = text.replace(row.body, body)
    line = re.compile(r"^(\|\s*\d+\s*\|\s*§" + str(row.number) + r"\s*\|[^\n]*\|\s*)\[x\](\s*\|)$", re.M)
    require(len(line.findall(text)) == 1, f"implementation row not found: {ref}")
    text = line.sub(r"\1[ ]\2", text)
    text = re.sub(r"\A(---\n(?:.*\n)*?)status: done\n", r"\1status: active\n", text, count=1)
    receipt_bytes = receipt_path.read_bytes()
    plan_path = root / PLAN
    original_plan_bytes = plan_path.read_bytes() if plan_path.is_file() else None
    try:
        atomic(revoked_path, receipt_bytes)
        atomic(path, text)
        receipt_path.unlink()
        graph(root)
        if original_plan_bytes is not None:
            projections(root, sync=True)
    except BaseException:  # an interrupt between writes must roll back as an error does
        try:
            if not receipt_path.is_file():
                atomic(receipt_path, receipt_bytes)
            revoked_path.unlink(missing_ok=True)
            if not path.is_file() or path.read_bytes() != original_bytes:
                atomic(path, original_bytes)
        finally:
            if original_plan_bytes is not None and (not plan_path.is_file()
                                                    or plan_path.read_bytes() != original_plan_bytes):
                atomic(plan_path, original_plan_bytes)
        raise
    return revoked


def suspects(root, ref):
    """Stamped sections that depend on ref, directly or through other sections: suspect while ref is open."""
    rows = graph(root)
    found, frontier = [], [ref]
    while frontier:
        current = frontier.pop()
        for row in ordered(rows):
            if current in row.depends and row.ref not in found:
                found.append(row.ref)
                frontier.append(row.ref)
    return [r for r in found if rows[r].done]

M_FLAG = re.M
