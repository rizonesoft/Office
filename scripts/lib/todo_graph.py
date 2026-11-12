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
import datetime
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
# Sections an owner decision retired (owner, 2026-11-11: a retired section is deleted, never kept as a `[-]` row). The
# list names each with its date, who decided and why, so a review record that filed a gap to one still resolves and
# the reference is never given to a different section.
REMOVED = "todo/removed.json"
SECTION_REF = re.compile(r"D\d{2} T\d{2} §[1-9]\d*")
# What a section needs from outside the repository. The WAITING values are people, companies, or the
# operator's own hands: a section naming one stays blocked until the answer is recorded and the Need
# is removed from the section.
NEEDS = {"windows-host", "arm64-host", "display-session", "office", "libreoffice", "store-account",
         "attended", "owner-decision", "third-party", "operator"}
WAITING = {"owner-decision", "third-party", "operator"}
# The Needs that put a section in the owner's weekly digest (D00 T03 §35): the waiting ones and the store account.
OWNER_NEEDS = WAITING | {"store-account"}
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
# Until 2026-11-11 the cutoff was round 8. Lowering it only loosens the rule, and every receipt written under it is
# frozen by digest (`before_plan` in LEGACY_RECEIPTS), so those receipts hold and no new one can take their shape.
SEVERITY_CUTOFF_ROUND = 0
# The completion review of a section stamped from 2026-11-11 on (scripts/review-dispatch.py --kind completion):
# complete (no gaps), completed (every gap implemented in the section, rotation pins only), filed (gaps filed as new
# sections, each listed under the review as "- Filed: DNN TNN §N") or reconciled (three-pass: it returned gaps and the
# last reconciliation ended RECONCILIATION: complete).
COMPLETION_VERDICTS = ("complete", "completed", "filed", "reconciled")
FILED = re.compile(r"^- Filed: (D\d{2} T\d{2} §[1-9]\d*)(?![\w§]|\.\d)")
# The one-pass plan review before the build and the review schedule: every receipt stamped from 2026-11-11 on records
# the plan review (`plan`) and the pin's [schedule] (`schedule`), and stamp replays the schedule over every recorded
# pass through scripts/review-dispatch.py's own `scheduled`. A receipt without them predates the requirement and is
# frozen by digest in LEGACY_RECEIPTS, so dropping the fields from a new receipt does not dodge the checks.
PIN = ".conclave/reviewers.toml"
PLAN_KEYS = {"report", "candidate", "reviewer", "model", "effort", "lenses"}
STARTED = re.compile(r"^> \*\*Started:\*\* .+$", re.M)
# A round scripts/review-dispatch.py recorded in a findings file, reviewed or not ("## Round 2: none").
ROUND_RECORD = re.compile(r"^## Round ([0-9]+): ", re.M)
ADJACENCY_KEYS = ["list", "document", "settings", "reporting", "notifications", "permissions",
                  "audit", "exchange", "reverse"]
# The closed phase list. A project names its phases (and the plan's title and acceptance bar) in
# todo/plan.json; without it the plan shows bare phase numbers.
PHASES = (0, 1, 2, 3, 4, 5, 6, 7, 99)
PLAN_CONFIG = "todo/plan.json"
DOMAIN_FOLDER = re.compile(r"\d{2}-[a-z0-9][a-z0-9-]*")  # a domain folder under todo/, `06-write`
PLAN_DEFAULTS = {"title": "Implementation plan", "acceptance": None, "phases": {99: "Manual, operator only"}}
MAX_SECTIONS_PER_FILE = 55
MAX_ITEMS_PER_SECTION = 30
MAX_DELIVERABLE_LEN = 88
# Every Markdown table row at or under this many characters, so rows never wrap in raw view (AGENTS.md).
MAX_TABLE_ROW = 120
# A checklist item that writes a whole TODO file into the tree (D00 T03 §31): `Author` and the file's backticked path.
AUTHOR_ITEM = re.compile(r"^- \[([ x])\] Author `([^`\n]+)`", re.M)
AUTHOR_PATH = re.compile(r"todo/\d{2}-[a-z0-9-]+/TODO-\d{2}-[a-z0-9-]+\.md")
# A checklist item as the graph and the plan count it: its box and its text.
CHECKLIST = re.compile(r"^- \[([ x])\] (.+)$", re.M)


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


def receipt_ok(root, receipt, ref, stamp_sha, commits=None, surface=None):
    """Check one receipt against its stamp and return it. `surface`: the section's Surface field is yes."""
    require(re.fullmatch(r"docs/reviews/[a-z0-9][a-z0-9.-]*\.json", receipt or "") is not None,
            f"invalid receipt path: {ref}")
    path = Path(root) / receipt
    require(path.is_file() and not path.is_symlink(), f"missing receipt: {ref}")
    try:
        data = json.loads(read_text(path))
    except ValueError:
        raise Refused(f"receipt is not JSON: {ref}") from None
    # The stamped commit first: a fabricated SHA is named as such before anything the receipt says is compared.
    if commits is None or stamp_sha not in commits:
        commit_ok(root, stamp_sha)
    receipt_data_ok(data, ref, stamp_sha, root=root, commits=commits, surface=surface)
    return data


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


def _git(root, *args):
    return subprocess.run([git(), "-C", str(root), *args], capture_output=True, timeout=60)


def is_ancestor(root, older, newer):
    """True when commit `older` is `newer` or an ancestor of it."""
    return _git(root, "merge-base", "--is-ancestor", older, newer).returncode == 0


def changed_paths(root, base, candidate, ref):
    """The files that differ between two commits, repository-relative with forward slashes: what the dispatcher gave
    a three-pass pass's conditional lenses."""
    shown = _git(root, "-c", "core.quotepath=false", "diff", "--name-only", "--no-renames", "-z", base, candidate)
    require(shown.returncode == 0, f"cannot list the files changed between {base} and {candidate}: {ref}")
    return [name for name in shown.stdout.decode("utf-8", errors="replace").split("\0") if name]


def removed_sections(root):
    """ref -> {"date", "by", "reason"} for every section REMOVED lists; empty when the file is absent."""
    path = Path(root) / REMOVED
    if not path.is_file():
        return {}
    try:
        data = json.loads(read_text(path))
    except ValueError:
        raise Refused(f"{REMOVED} is not JSON") from None
    listed = data.get("sections") if isinstance(data, dict) and data.get("schema_version") == 1 else None
    require(isinstance(listed, dict) and all(
        isinstance(ref, str) and SECTION_REF.fullmatch(ref) and isinstance(entry, dict)
        and set(entry) == {"date", "by", "reason"}
        and isinstance(entry["date"], str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry["date"])
        and all(isinstance(entry[key], str) and entry[key].strip() for key in ("by", "reason"))
        for ref, entry in listed.items()),
        f"{REMOVED} needs schema_version 1 and sections mapping each 'DNN TNN §N' to its date (YYYY-MM-DD), by and "
        f"reason")
    return listed


def receipt_digest(data):
    """The SHA-256 of a receipt's content, independent of key order, spacing and line endings."""
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _frozen(root, key):
    """ref -> digest under `key` in LEGACY_RECEIPTS ("receipts" or "before_plan"); empty when the file or key is absent."""
    path = Path(root) / LEGACY_RECEIPTS
    if not path.is_file():
        return {}
    try:
        data = json.loads(read_text(path))
    except ValueError:
        raise Refused(f"{LEGACY_RECEIPTS} is not JSON") from None
    ok = isinstance(data, dict) and data.get("schema_version") == 1 and "receipts" in data
    maps = {name: data.get(name, {}) for name in ("receipts", "before_plan")} if ok else {}
    require(ok and all(isinstance(m, dict) and all(
        isinstance(k, str) and isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v) for k, v in m.items())
        for m in maps.values()),
            f"{LEGACY_RECEIPTS} needs schema_version 1 and receipts (and any before_plan) mapping each ref to a "
            f"SHA-256 digest")
    return maps[key]


def legacy_receipts(root):
    """ref -> digest of every receipt written before rounds_spent existed; empty when the file is absent."""
    return _frozen(root, "receipts")


def receipts_before_plan(root):
    """ref -> digest of every receipt written since rounds_spent but before the plan and schedule fields existed."""
    return _frozen(root, "before_plan")


def report_ok(root, raw_report, ref):
    """A findings file path inside docs/reviews/, reached through no symlink, holding text."""
    root_path = Path(root)
    report = Path(raw_report)
    require(isinstance(raw_report, str) and re.fullmatch(r"docs/reviews/[A-Za-z0-9_./-]+\.md", raw_report) is not None
            and not report.is_absolute() and not report.drive and not report.root and ".." not in report.parts,
            f"invalid review report path ({raw_report}): {ref}")
    cur = root_path
    for part in report.parts:
        cur = cur / part
        require(not cur.is_symlink(), f"invalid review report path ({raw_report}): {ref}")
    report_path = root_path / report
    require(report_path.is_file() and report_path.resolve().is_relative_to(root_path.resolve())
            and bool(read_text(report_path).strip()),
            f"missing or empty review report ({raw_report}): {ref}")
    return report_path


def completion_record(root, completion, ref, stamp_sha, commits=None):
    """The receipt's record of the section's completion review, from `--completion <findings file>:<verdict>`: the
    findings file holds exactly one completion review returned by a reviewer of another model family, its last line
    `COMPLETION: complete` (verdict complete) or `COMPLETION: gaps` (completed or filed), its candidate a commit at or
    before the stamped one, and, for filed, the `- Filed: DNN TNN §N` lines the writer added under it. Whether each
    filed section resolves is checked against the whole graph by the caller."""
    require(isinstance(completion, dict) and isinstance(completion.get("report"), str)
            and isinstance(completion.get("verdict"), str), f"receipt completion is malformed: {ref}")
    report, verdict = completion["report"], completion["verdict"]
    require(verdict in COMPLETION_VERDICTS,
            f"--completion verdict must be one of {', '.join(COMPLETION_VERDICTS)}, not {verdict!r}: {ref}")
    path = report_ok(root, report, ref)
    dispatch = review_dispatch()
    found = dispatch.read_completions(path.read_bytes().decode("utf-8"))
    require(found is not None, f"{report} is not a findings file the dispatcher can read: {ref}")
    require(bool(found), f"{report} holds no ## Completion review; run review-dispatch.py --kind completion: {ref}")
    returned = [e for e in found if dispatch.returned_one_pass(e, "completion")]
    require(len(returned) == 1, f"{report} must hold exactly one completion review returned by another model family "
                                f"and ending COMPLETION: complete or COMPLETION: gaps, not {len(returned)}: {ref}")
    (entry,) = returned

    def ending(e):
        return [x.strip() for x in e["review"].splitlines() if x.strip()][-1]
    last = ending(entry)
    # The reconciliations the three-pass policy records after a completion with gaps. The last returned pass is the
    # one the receipt names: its candidate, and the writer's `- Filed:` lines under it.
    passed = [e for e in dispatch.read_findings(path.read_bytes().decode("utf-8"))["reconciliations"]
              if dispatch.returned_one_pass(e, "reconciliation")]
    final = passed[-1] if passed else entry
    for earlier in passed[:-1]:
        require(ending(earlier) == "RECONCILIATION: gaps",
                f"only the last reconciliation in {report} may end RECONCILIATION: complete: {ref}")
    if verdict == "reconciled":
        require(bool(passed), f"completion verdict reconciled needs a returned ## Reconciliation review in {report}: {ref}")
        require(last == "COMPLETION: gaps" and ending(final) == "RECONCILIATION: complete",
                f"completion verdict reconciled needs a completion ending COMPLETION: gaps and a last reconciliation "
                f"ending RECONCILIATION: complete, and {report} ends {ending(final)}: {ref}")
    else:
        expected = "COMPLETION: complete" if verdict == "complete" else "COMPLETION: gaps"
        require(last == expected, f"completion verdict {verdict} needs a review ending {expected}, and {report} ends "
                                  f"{last}: {ref}")
        require(not passed or ending(final) == "RECONCILIATION: gaps",
                f"{report} holds a reconciliation ending RECONCILIATION: complete, so the verdict is reconciled, not "
                f"{verdict}: {ref}")
    filed = list(dict.fromkeys(m[1] for m in (FILED.match(line) for line in final["notes"]) if m))
    require(bool(filed) == (verdict == "filed"),
            f"completion verdict filed needs each filed section listed as '- Filed: DNN TNN §N' under the last "
            f"returned completion or reconciliation review in {report}, and only filed lists any: {ref}")
    require(ref not in filed, f"{ref} cannot file a completion gap to itself: {ref}")
    candidate = final["candidate"]
    if commits is None or candidate not in commits:
        commit_ok(root, candidate)
    if commits is None:  # stamping: the candidate is the stamped commit or one before it
        require(is_ancestor(root, candidate, stamp_sha),
                f"the completion review's candidate {candidate} is not the stamped commit or an ancestor of it: {ref}")
    return {"report": report, "verdict": verdict, "candidate": candidate, "reviewer": entry["reviewer"],
            "model": entry["model"], "filed": filed}


def _other_family(dispatch, entry):
    """A review returned by a reviewer of another model family than the writer: not an outage, not a self-review."""
    return bool(entry["reviewer"]) and entry["writer"] in dispatch.WRITER_FAMILY \
        and dispatch.FAMILY.get(entry["cli"]) not in (None, dispatch.WRITER_FAMILY[entry["writer"]])


def section_text(text, number):
    """Section `number`'s text in a TODO file's text, from its `## N.` heading to the next level-two heading, or None."""
    head = re.search(rf"^## {number}\. ", text, re.M)
    if head is None:
        return None
    end = re.search(r"^##(?:[ \t]|$)", text[head.end():], re.M)
    return text[head.start():head.end() + end.start() if end else len(text)]


def build_start(root, path, body, ref):
    """The commit the section's build began at: the first commit of its TODO file in which the section's own text
    holds its whole `> **Started:**` line (another section's identical or longer Started line does not count), or,
    for a section that never recorded one, the first commit naming the section outside todo/ and docs/."""
    started = STARTED.search(body or "")
    first = None
    if started:
        line = started[0].rstrip("\r")
        number = ref.rsplit("§", 1)[1]
        out = subprocess.run([git(), "-C", str(root), "log", "--reverse", "--format=%H", "--", path],
                             capture_output=True, text=True, timeout=60)
        for sha in out.stdout.split() if out.returncode == 0 else []:
            shown = subprocess.run([git(), "-C", str(root), "show", f"{sha}:{path}"], capture_output=True, timeout=30)
            section = section_text(shown.stdout.decode("utf-8", "replace"), number) if shown.returncode == 0 else None
            if section is not None and line in section.splitlines():
                first = sha
                break
    else:
        # The whole reference, so `D01 T02 §2` does not match a commit that names only §22 or §23.
        out = subprocess.run([git(), "-C", str(root), "log", "--reverse", "--format=%H", "-E",
                              f"--grep={ref}([^0-9]|$)", "--", ".", ":(exclude)todo", ":(exclude)docs"],
                             capture_output=True, text=True, timeout=60)
        first = out.stdout.split()[0] if out.returncode == 0 and out.stdout.split() else None
    require(first is not None, f"cannot find the commit the build began at: record '> **Started:**' in the section "
                               f"before the build: {ref}")
    return first


def section_findings(root, ref):
    """The section's own findings file, `docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md`, the domain being the one
    `todo/<NN-domain>/` folder its domain number names."""
    m = re.fullmatch(r"D(\d{2}) T(\d{2}) §([1-9]\d*)", ref)
    require(m is not None, f"not a full section reference: {ref}")
    domains = sorted(d.name for d in (Path(root) / "todo").iterdir() if d.is_dir() and d.name.startswith(f"{m[1]}-"))
    require(len(domains) == 1, f"no single todo/{m[1]}-<domain> folder for: {ref}")
    return f"docs/reviews/{domains[0]}/D{m[1]}-T{m[2]}-s{m[3]}.md"


def plan_record(root, report, ref, commits=None, start=None):
    """The receipt's record of the section's one-pass plan review, from `--plan <findings file>`: the file is the
    section's own findings file (so another section's plan review cannot stand in for it), holds exactly one plan
    review returned by a reviewer of another model family, ending in the plan prompt's `PLAN:` and `OVERALL:` verdict
    lines, and its candidate is the commit the build began at (`start`) or one before it."""
    require(isinstance(report, str), f"receipt plan is malformed: {ref}")
    expected = section_findings(root, ref)
    require(report == expected,
            f"--plan must be the section's own findings file {expected}, not {report}: {ref}")
    path = report_ok(root, report, ref)
    dispatch = review_dispatch()
    found = dispatch.read_plans(path.read_bytes().decode("utf-8"))
    require(found is not None, f"{report} is not a findings file the dispatcher can read: {ref}")
    require(bool(found), f"{report} holds no ## Plan review; run review-dispatch.py --kind plan: {ref}")

    def verdict(entry):
        lines = [x.strip() for x in entry["review"].splitlines() if x.strip()]
        return len(lines) >= 2 and lines[-2] in ("PLAN: complete", "PLAN: gaps") \
            and lines[-1] in ("OVERALL: approve", "OVERALL: needs-attention")
    returned = [e for e in found if _other_family(dispatch, e) and verdict(e)]
    require(len(returned) == 1, f"{report} must hold exactly one plan review returned by another model family and "
                                f"ending PLAN: complete or gaps, then OVERALL: approve or needs-attention, not "
                                f"{len(returned)}: {ref}")
    (entry,) = returned
    candidate = entry["candidate"]
    if commits is None or candidate not in commits:
        commit_ok(root, candidate)
    if start is not None:  # stamping: the plan was reviewed before the build began
        ancestor = subprocess.run([git(), "-C", str(root), "merge-base", "--is-ancestor", candidate, start],
                                  capture_output=True, timeout=30)
        require(ancestor.returncode == 0, f"the plan review's candidate {candidate} is not the commit the build began "
                                          f"at ({start}) or an ancestor of it: review the plan before the build: {ref}")
    return {"report": report, "candidate": candidate, "reviewer": entry["reviewer"], "model": entry["model"],
            "effort": entry["effort"], "lenses": entry["lenses"] or []}


def committed_pin(root, sha, ref):
    """The reviewer pin committed at `sha`, loaded by the reviewer kit's own `load_pin`."""
    shown = _git(root, "show", f"{sha}:{PIN}")
    require(shown.returncode == 0, f"no reviewer pin {PIN} at {sha}: {ref}")
    dispatch = review_dispatch()
    try:
        pin = dispatch.load_pin(PIN, data=shown.stdout)
    except dispatch.Refused as exc:
        raise Refused(f"the reviewer pin at {sha} does not load: {exc}: {ref}") from None
    require("schedule" in pin, f"the reviewer pin at {sha} has no [schedule] to check the reviews against: {ref}")
    return pin


def pin_schedule(root, sha, ref):
    """The [schedule] of the reviewer pin committed at `sha`."""
    return committed_pin(root, sha, ref)["schedule"]


def section_pin_sha(root, plan_candidate, stamp_sha):
    """The commit whose pin a section's receipt is held to. Under the three-pass policy that is its plan review's
    candidate, the pin the dispatcher ran every pass under. A section whose plan candidate holds a rotation pin, or
    none, is held to the stamped commit's pin, as it always was."""
    dispatch = review_dispatch()

    def policy(sha):
        """ "three-pass", "other" (a pin that is not three-pass) or None (no pin at that commit)."""
        shown = _git(root, "show", f"{sha}:{PIN}")
        if shown.returncode != 0:
            return None
        try:
            pin = dispatch.load_pin(PIN, data=shown.stdout)
        except dispatch.Refused:
            return dispatch.THREE_PASS if dispatch.THREE_PASS.encode() in shown.stdout else None
        return dispatch.THREE_PASS if pin.get("schedule", {}).get("policy") == dispatch.THREE_PASS else "other"
    began = policy(plan_candidate)
    if began == dispatch.THREE_PASS:
        return plan_candidate
    # A section that began under a rotation pin finishes under it even when the pin has since become three-pass.
    return plan_candidate if began == "other" and policy(stamp_sha) == dispatch.THREE_PASS else stamp_sha


def schedule_ok(root, data, ref, surface):
    """Every pass the receipt names ran at the effort and lenses the section's pin gave it: every attempt at the plan,
    completion and reconciliation reviews, and each round in each findings file, replayed through the reviewer kit's
    own `scheduled` over the rounds recorded before it (outages, self-reviews and replies without the OVERALL line do
    not advance the position). Under the three-pass policy a pass's conditional lenses are replayed from the files
    changed between the plan review's candidate and its own, the returned passes were reviewed by the reviewer the
    pin routes their writer to, and the chain itself is checked by `three_pass_ok`."""
    require(isinstance(surface, bool), f"the section's Surface is needed to check the review schedule: {ref}")
    dispatch = review_dispatch()
    schedule = data["schedule"]
    three_pass = schedule.get("policy") == dispatch.THREE_PASS
    base = data["plan"]["candidate"]

    def changed(entry):
        return changed_paths(root, base, entry["candidate"], ref) if three_pass and entry.get("candidate") else []

    def check(where, recorded, expected, optional=()):
        lenses = list(recorded["lenses"] or [])
        fixed = expected["lenses"]
        # A plan review's conditional lenses came from the paths the writer named before the build, so any of the
        # entries naming plan may follow the plan's own lenses; every other pass's are replayed exactly.
        same = lenses == fixed or (bool(optional) and lenses[:len(fixed)] == fixed
                                   and all(name in optional for name in lenses[len(fixed):]))
        position = f" (position {expected['position']}{', escalated' if expected['escalated'] else ''})" \
            if expected["position"] else ""
        require(recorded["effort"] == expected["effort"] and same,
                f"{where} ran at {recorded['effort']} with lenses {lenses}; the schedule expects "
                f"{expected['effort']} with {fixed}{position}: {ref}")
    # Every attempt the one-pass files record, outages and self-reviews included, ran at that pass's scheduled step.
    plan_report = data["plan"]["report"]
    plan_optional = [name for entry in schedule.get("conditional", []) if "plan" in entry["passes"]
                     for name in entry["lenses"]] if three_pass else []
    for entry in dispatch.read_plans((Path(root) / plan_report).read_bytes().decode("utf-8")):
        attempt, optional = schedule, plan_optional
        if three_pass and entry["candidate"] != base:
            # An attempt that returned no review, on another candidate than the plan review that did: the dispatcher
            # ran it under the three-pass pin at its own candidate, so that is the schedule it is held to. One whose
            # candidate holds no such pin ran under a working tree's, which is not on record.
            shown = _git(root, "show", f"{entry['candidate']}:{PIN}")
            try:
                own = dispatch.load_pin(PIN, data=shown.stdout) if shown.returncode == 0 else None
            except dispatch.Refused:
                own = None
            if own is None or own.get("schedule", {}).get("policy") != dispatch.THREE_PASS:
                continue
            attempt = own["schedule"]
            optional = [name for item in attempt.get("conditional", []) if "plan" in item["passes"]
                        for name in item["lenses"]]
        check(f"the plan review in {plan_report}", entry, dispatch.scheduled(attempt, "plan", [], surface), optional)
    completion = data["completion"]["report"]
    found = dispatch.read_findings((Path(root) / completion).read_bytes().decode("utf-8"))
    final_kind = "reconciliation" if any(dispatch.returned_one_pass(e, "reconciliation")
                                         for e in found["reconciliations"]) else "completion"
    final = [e for e in found[final_kind + "s"] if dispatch.returned_one_pass(e, final_kind)]
    require((len(final) == 1 or final_kind == "reconciliation") and bool(final)
            and final[-1]["candidate"] == data["completion"]["candidate"],
            f"{completion} must end with one returned {final_kind} review of the receipt's candidate: {ref}")
    for entry in found["completions"]:
        check(f"the completion review in {completion}", entry,
              dispatch.scheduled(schedule, "completion", [], surface, changed(entry)))
    if three_pass:
        for entry in found["reconciliations"]:
            check(f"the reconciliation review in {completion}", entry,
                  dispatch.scheduled(schedule, "reconciliation", [], surface, changed(entry)))
    else:
        require(not found["reconciliations"],
                f"{completion} holds a reconciliation review, which only the three-pass policy takes: {ref}")
    for report in dict.fromkeys(r["report"] for r in data["reviews"]):
        recorded = dispatch.read_rounds((Path(root) / report).read_bytes().decode("utf-8"))
        for i, entry in enumerate(recorded):
            check(f"{report} round {entry['number']}", entry,
                  dispatch.scheduled(schedule, "round", recorded[:i], surface, changed(entry)))
    if three_pass:
        three_pass_ok(root, data, ref, found)


def section_contract(root, sha, ref):
    """The section's text at a commit with its ticks, stamp lines and quoted evidence neutral, so a reconciliation can
    tell a build that ticked boxes and recorded results from one that changed what the section promised."""
    m = re.fullmatch(r"D(\d{2}) T(\d{2}) §([1-9]\d*)", ref)
    require(m is not None, f"not a full section reference: {ref}")
    paths = sorted((Path(root) / "todo").glob(f"{m[1]}-*/TODO-{m[2]}-*.md"))
    require(len(paths) == 1, f"no single TODO file for: {ref}")
    rel = paths[0].relative_to(root).as_posix()
    shown = _git(root, "show", f"{sha}:{rel}")
    require(shown.returncode == 0, f"{rel} is not in {sha}: {ref}")
    body = section_text(shown.stdout.decode("utf-8").replace("\r\n", "\n"), int(m[3]))
    require(body is not None, f"the section is not in {rel} at {sha}: {ref}")
    body = re.sub(r"^(\s*- )\[[xX ]\](?= )", r"\1[ ]", body, flags=re.M)
    body = re.sub(r"^> \*\*(?:Verified|Review|Started|Duration|Deferred|Resolved):\*\*[^\n]*(?:\n|$)", "", body,
                  flags=re.M)
    # Dated correction and completion notes record what happened; the promise is the text before them.
    body = re.sub(r" \*\*Corrected \d{4}-\d{2}-\d{2}[^*]*\*\*.*$", "", body, flags=re.M)
    body = re.sub(r" Completed \d{4}-\d{2}-\d{2}:.*$", "", body, flags=re.M)
    return re.sub(r"\n{3,}", "\n\n", body).rstrip()


def three_pass_ok(root, data, ref, found):
    """The three-pass chain: one plan review, exactly one returned round naming its candidate, one completion review,
    then reconciliations up to the section pin's `pass_cap` returned passes in all, each run after the pass before on
    a candidate at or after it, the last on the stamped commit. The receipt's completion verdict is `complete`,
    `reconciled`, or, when the pin sets `blocking` and the last pass ended gaps below those levels, `filed`. The
    section's promise is the same at every reconciliation as at the completion review that failed."""
    dispatch = review_dispatch()
    schedule, sha = data["schedule"], data["implementation_sha"]
    pin = committed_pin(root, data.get("schedule_sha", sha), ref)
    returned = [e for e in found["rounds"] if dispatch.returned_review(e)]
    require(len(returned) == 1, f"the three-pass policy needs exactly one returned round, not {len(returned)}: {ref}")
    (round_entry,) = returned
    claimed = data["reviews"]
    require(len(claimed) == 1 and claimed[0]["round"] == round_entry["number"]
            and claimed[0]["verdict"] in ("clean", "fixed"),
            f"the three-pass receipt names its one round, clean or fixed: {ref}")
    require(round_entry.get("candidate") is not None, f"the three-pass round recorded no --candidate: {ref}")
    (plan,) = [e for e in found["plans"] if dispatch.returned_one_pass(e, "plan")]
    (completion,) = [e for e in found["completions"] if dispatch.returned_one_pass(e, "completion")]
    passed = [e for e in found["reconciliations"] if dispatch.returned_one_pass(e, "reconciliation")]
    cap = dispatch.review_pin.pass_cap(schedule)
    require(3 + len(passed) <= cap,
            f"the section's pin allows {cap} review passes (pass_cap), not {3 + len(passed)}: {ref}")
    require(data.get("pass_cap") == cap and data.get("passes_spent") == 3 + len(passed),
            f"receipt passes_spent or pass_cap is not what the findings file and the section's pin hold "
            f"({3 + len(passed)} of {cap}): {ref}")
    require(data["completion"]["report"] == data["plan"]["report"]
            and all(r["report"] == data["plan"]["report"] for r in claimed),
            f"a three-pass receipt names one findings file, the section's own, for every pass: {ref}")
    # Each reconciliation was one the dispatcher would have run: after a pass that returned gaps, whose worst finding
    # blocks when the pin names blocking levels, and before the chain had stalled.

    def ended_gaps(entry):
        return [x.strip() for x in entry["review"].splitlines() if x.strip()][-1].endswith(": gaps")
    tail = [completion, *passed]
    worst = [dispatch.review_pin.declared_highest(e["review"]) for e in tail]
    stall = dispatch.review_pin.no_progress_cap(schedule)
    for i in range(len(passed)):
        require(ended_gaps(tail[i]), f"a reconciliation follows a pass that returned gaps, not one that was complete: {ref}")
        require("blocking" not in schedule or dispatch.review_pin.blocks(schedule, worst[i]),
                f"a reconciliation followed a pass whose worst finding ({worst[i]}) is below the pin's blocking "
                f"levels; its findings are filed, not reviewed again: {ref}")
        if stall is not None:
            run = 0
            for before, after in reversed(list(zip(worst[:i + 1], worst[1:i + 1]))):
                if dispatch.SEVERITY_RANK[after] < dispatch.SEVERITY_RANK[before]:
                    break
                run += 1
            require(run < stall, f"a reconciliation ran after {run} in a row made no progress, past the pin's "
                                 f"no_progress_cap of {stall}: {ref}")
    chain = [("plan review", plan), ("round", round_entry), ("completion review", completion),
             *[("reconciliation", e) for e in passed]]
    for name, entry in chain:
        writer = entry["writer"]
        routed = dispatch.review_pin.route_for(pin, writer)
        require(routed is not None, f"the {name} names writer {writer!r}, which the section's pin does not route: {ref}")
        want = (routed, pin["reviewers"][routed]["cli"], pin["reviewers"][routed]["model"])
        got = (entry["reviewer"], entry["cli"], entry["model"])
        require(got == want, f"the {name} was reviewed by {got[0]} ({got[2]} via {got[1]}), not the reviewer "
                             f"{want[0]} ({want[2]} via {want[1]}) the section's pin routes {writer!r} to: {ref}")
    verdict = data["completion"]["verdict"]
    worst = dispatch.review_pin.declared_highest(chain[-1][1]["review"])
    below = "blocking" in schedule and not dispatch.review_pin.blocks(schedule, worst)
    require(verdict in ("complete", "reconciled") or (verdict == "filed" and below),
            f"the three-pass policy takes completion verdict complete or reconciled, or filed when the last pass's "
            f"worst finding ({worst}) is below the pin's blocking levels, not {verdict}: {ref}")
    # A last pass that ends complete while declaring a finding that holds the stamp contradicts itself: the severity
    # it declared decides, so a `complete` footer never overrides a blocking level.
    # A reply with no HIGHEST line counts as P1 under a pin that names blocking levels (the dispatcher that reads
    # such a pin records no reply without the line); a pin without the key predates the line and is not held to it.
    holds = dispatch.review_pin.blocks(schedule, worst) if worst is not None else "blocking" in schedule
    require(verdict == "filed" or worst == "none" or not holds,
            f"the last review ({chain[-1][0]}) ends complete but "
            f"{'declares HIGHEST: ' + worst if worst else 'declares no HIGHEST line, which counts as P1'}, which holds "
            f"the stamp under the section's pin: {ref}")
    for (older_name, older), (newer_name, newer) in zip(chain, chain[1:]):
        require(older["run"] <= newer["run"] and is_ancestor(root, older["candidate"], newer["candidate"]),
                f"the {newer_name} must run after the {older_name}, on a candidate at or after it: {ref}")
    require(chain[-1][1]["candidate"] == sha,
            f"the last review ({chain[-1][0]}) reviewed {chain[-1][1]['candidate']}, not the stamped commit {sha}: {ref}")
    promised = section_contract(root, completion["candidate"], ref)
    for entry in passed:
        require(section_contract(root, entry["candidate"], ref) == promised,
                f"the section's contract changed between the failed completion and its reconciliation: {ref}")


def receipt_data_ok(data, ref, stamp_sha, root=None, building=False, commits=None, surface=None):
    """building: stamp's first pass over its arguments, before it adds rounds_spent and round_cap.

    Three shapes are valid. A receipt stamped from 2026-11-11 on records its plan review, its completion review and the
    pin's schedule, and every pass is replayed against that schedule. The two older shapes (before `rounds_spent`, and
    with it but before the plan review, whose `completion` is the path of a `-completion.md` record) are held to the
    rules they were written under and must be frozen by digest in LEGACY_RECEIPTS."""
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
    # The shape written before the plan review existed: no plan, no schedule, and any completion a record's path.
    before_plan = not building and "plan" not in data and "schedule" not in data \
        and not isinstance(data.get("completion"), dict)
    if root is not None:
        for r in rounds:
            # A pre-build completion record (D00 T03 §13) judged the plan, never the implementation.
            require(isinstance(r["report"], str) and not r["report"].endswith("-completion.md"),
                    f"{r['report']} is a completion record, not a review of the implementation: {ref}")
            report_ok(root, r["report"], ref)
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
                # The three-pass policy's one round may end fixed: the completion review after it checks the fixes.
                three_pass = (data.get("schedule") or {}).get("policy") == dispatch.THREE_PASS
                require(claimed[-1]["round"] == max(reviewed)
                        and (claimed[-1]["verdict"] == "clean" or claimed[-1]["verdict"].startswith("stopped-")
                             or (three_pass and claimed[-1]["verdict"] == "fixed")),
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
        # A receipt stamped before 2026-11-11 under the 33-round cap names the pre-build completion record its section
        # was built from (D00 T03 §13), a `-completion.md` path; receipts under earlier caps carry none.
        if before_plan:
            if cap == REVIEW_ROUND_CAP:
                require(isinstance(data.get("completion"), str),
                        f"a receipt under the {REVIEW_ROUND_CAP}-round cap must name its completion record: {ref}")
                require("completion_rules" not in data or (type(data["completion_rules"]) is int
                                                           and data["completion_rules"] in COMPLETION_RULES),
                        f"completion_rules must be one of {', '.join(map(str, COMPLETION_RULES))}: {ref}")
                if root is not None:
                    completion_ok(root, ref, data["completion"])
            else:
                require("completion" not in data and "completion_rules" not in data,
                        f"a receipt under the {cap}-round cap predates completion records: {ref}")
    # Newer receipts record the completion review; a receipt without the field predates it. The
    # record must be what the findings file still says, so an edit to either refuses.
    if "completion" in data and not before_plan:
        recorded = data["completion"]
        require(isinstance(recorded, dict) and set(recorded) == {"report", "verdict", "candidate", "reviewer", "model",
                                                                 "filed"},
                f"receipt completion is malformed: {ref}")
        if root is not None:
            require(completion_record(root, recorded, ref, stamp_sha, commits if commits is not None else set())
                    == recorded, f"receipt completion does not match its findings file {recorded['report']}: {ref}")
    # Newer receipts record the plan review and the pin's schedule, and every pass is replayed
    # against that schedule. A receipt without them predates the requirement and must be frozen by digest, so
    # dropping both fields from a new receipt does not dodge the checks.
    require(("plan" in data) == ("schedule" in data), f"receipt records plan and schedule together or neither: {ref}")
    if "plan" in data and not building:
        recorded = data["plan"]
        require(isinstance(recorded, dict) and set(recorded) == PLAN_KEYS,
                f"receipt plan is malformed: {ref}")
        require("completion" in data and "rounds_spent" in data,
                f"a receipt with a plan review also records its completion review and rounds_spent: {ref}")
        require(isinstance(data["schedule"], dict), f"receipt schedule is malformed: {ref}")
        if root is not None:
            require(plan_record(root, recorded["report"], ref, commits if commits is not None else set()) == recorded,
                    f"receipt plan does not match its findings file {recorded['report']}: {ref}")
            # Every receipt is held to the schedule of the commit the section pin rule selects (the stamped commit
            # for a rotation section, as always). A receipt names that commit as `schedule_sha`; one from before the
            # field is valid only when that commit is the stamped one, so dropping the field moves nothing.
            pinned = section_pin_sha(root, recorded["candidate"], stamp_sha)
            require(data.get("schedule_sha", pinned) == pinned,
                    f"receipt schedule_sha is not {pinned}, the commit whose pin the section ran under: {ref}")
            require("schedule_sha" in data or pinned == stamp_sha,
                    f"receipt names no schedule_sha, and the section ran under the pin at {pinned}, not the stamped "
                    f"commit's: {ref}")
            require(pin_schedule(root, pinned, ref) == data["schedule"],
                    f"receipt schedule is not the [schedule] in {PIN} at "
                    f"{'the stamped commit' if pinned == stamp_sha else pinned + ', the commit whose pin the section ran under'}"
                    f": {ref}")
            three_pass = data["schedule"].get("policy") == review_dispatch().THREE_PASS
            require(three_pass == ("passes_spent" in data) and three_pass == ("pass_cap" in data),
                    f"a three-pass receipt records passes_spent and pass_cap, and only a three-pass receipt: {ref}")
            schedule_ok(root, data, ref, surface)
    elif not building:
        frozen = root is not None and (legacy_receipts(root).get(ref) == receipt_digest(data)
                                       or receipts_before_plan(root).get(ref) == receipt_digest(data))
        require(frozen, f"a receipt without a plan review must be one of the old receipts {LEGACY_RECEIPTS} freezes: "
                        f"{ref}")
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
    legacy_receipts(root)  # a malformed freeze list refuses even before any old receipt is read against it
    removed = removed_sections(root)
    sections, ids, files = {}, {}, {}
    head_commits = None
    filed_gaps = {}
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
            # A checkbox that does not start its own line is no item: the plan cannot count it or tick it, and an edit
            # that ran two items together once hid a deliverable inside the item before it (D00 T04 §1, 2026-11-12).
            prose = [re.sub(r"`[^`]*`", "", line) for line in section_body.splitlines()]  # quoted boxes are text
            joined = [line for line in prose if re.search(r"\S.*?- \[[ x]\] ", line)
                      and not re.match(r"- \[[ x]\] ", line) or re.match(r"- \[[ x]\] .*\S- \[[ x]\] ", line)]
            require(not joined, f"a checklist item does not start its own line ({joined[0][:60]}...): {ref}"
                    if joined else "")
            require("`" in field(section_body, "Test checkpoint"),
                    f"runnable Test checkpoint required: {ref}")
            surface = field(section_body, "Surface")
            require(surface in {"yes", "no"}, f"Surface must be yes/no: {ref}")
            if surface == "yes":
                for label in ("Fidelity", "Job", "Treatment", "Chrome"):
                    field(section_body, label)
            # D00 T03 §35: a section waiting on the owner says exactly what the owner does, for the weekly digest.
            owner_action = field(section_body, "Owner action", False)
            if not set(needs) & OWNER_NEEDS:
                require(not owner_action, f"Owner action on a section that waits on no one: {ref}")
            elif rows[n][5] == " ":
                require(bool(owner_action), f"a section waiting on {', '.join(sorted(set(needs) & OWNER_NEEDS))} "
                        f"needs an Owner action line (the exact steps and where the answer is recorded): {ref}")
            freeze_check = field(section_body, "Freeze check", False)
            require(bool(freeze_check) == (frozen == "true"),
                    f"Freeze check must match frozen frontmatter: {ref}")
            done = rows[n][5] == "x"
            stamp_line = field(section_body, "Verified", False)
            receipt = field(section_body, "Review", False).strip("`")
            require(ref not in removed, f"{REMOVED} lists this section as removed, so its reference is retired: {ref}")
            require(done == bool(stamp_line) == bool(receipt),
                    f"checkbox/stamp/receipt mismatch: {ref}")
            if done:
                require(all(x[0] == "x" for x in checks), f"unfinished stamped checklist: {ref}")
                require(not set(needs) & WAITING, f"stamped section has a waiting Need: {ref}")
                m = re.fullmatch(r"\d{4}-\d{2}-\d{2} \| §" + str(n) + r" \| ([0-9a-f]{40})", stamp_line)
                require(m is not None, f"invalid stamp: {ref}")
                if head_commits is None:
                    head_commits = _head_commits(root)
                data = receipt_ok(root, receipt, ref, m[1], head_commits, surface=surface == "yes")
                if isinstance(data.get("completion"), dict):
                    filed_gaps[ref] = data["completion"]["filed"]
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
    for ref, filed in filed_gaps.items():
        for target in filed:
            require(target in sections or target in removed,
                    f"completion gap filed as {target}, which does not resolve: {ref}")
    # A stamped completion record's filed references resolve against the whole graph, known only now (D00 T03 §13).
    for sec in sections.values():
        if sec.done and sec.receipt:
            data = json.loads(read_text(Path(root) / sec.receipt))
            if isinstance(data, dict) and isinstance(data.get("completion"), str):
                last = completion_ok(root, sec.ref, data["completion"], rows=sections)
                # D00 T03 §16: a receipt that met completion rules 2 stays bound to the contract it was reviewed on.
                if completion_rules(data, last) == 2:
                    contract_ok(last, sec, data["completion"])
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
    # After the cycle check: author_items walks the plan order, which needs an acyclic, resolved graph.
    _author_items_ok(root, sections)
    _plan_tables_ok(root, sections)
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


def author_items(rows):
    """Every `Author` item naming a TODO file path, as (ref, path, ticked), sections in plan order and items in the
    order they are written. An item whose backticked text is not a `todo/<NN-domain>/TODO-NN-<name>.md` path is no
    authoring item and is left out (D00 T03 §31)."""
    found = []
    for row in ordered(rows):
        for m in AUTHOR_ITEM.finditer(row.body):
            if AUTHOR_PATH.fullmatch(m[2]):
                found.append((row.ref, m[2], m[1] == "x"))
    return found


def _author_items_ok(root, rows):
    """One section authors each file, and a ticked `Author` item has its file on disk (D00 T03 §31)."""
    owners = {}
    for ref, path, ticked in author_items(rows):
        require(path not in owners,
                f"TODO file named by two Author items ({owners.get(path)} and {ref}): {path}")
        owners[path] = ref
        require(not ticked or (Path(root) / path).is_file(),
                f"ticked Author item without its file ({ref}): {path}")


def to_author(root=ROOT, rows=None):
    """The TODO files `Author` items name that are not on disk yet, each with the section that authors it, in plan
    order (D00 T03 §31)."""
    rows = graph(root) if rows is None else rows
    return [{"path": path, "ref": ref, "done": rows[ref].done}
            for ref, path, _ in author_items(rows) if not (Path(root) / path).is_file()]


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
        return {**PLAN_DEFAULTS, "phases": dict(PLAN_DEFAULTS["phases"]), "domains": {}}
    try:
        data = json.loads(read_text(path))
    except ValueError as exc:
        raise Refused(f"unreadable {PLAN_CONFIG}: {exc}") from None
    require(isinstance(data, dict) and set(data) <= {"title", "acceptance", "phases", "domains"},
            f"{PLAN_CONFIG} may only hold title, acceptance, phases and domains")
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
    # The display name of each domain folder (D00 T03 §33): a key must be a folder under todo/, so a typo or a
    # renamed folder is refused instead of silently falling back to the folder name.
    domains = data.get("domains", {})
    require(isinstance(domains, dict), f"{PLAN_CONFIG}: domains must map a domain folder to its name")
    for folder, name in domains.items():
        require(isinstance(folder, str) and DOMAIN_FOLDER.fullmatch(folder) is not None
                and (Path(root) / "todo" / folder).is_dir(),
                f"{PLAN_CONFIG}: domains names {folder!r}, which is not a domain folder under todo/")
        require(isinstance(name, str) and name.strip() != "", f"{PLAN_CONFIG}: domain {folder} needs a name")
    return {"title": title.strip(), "acceptance": acceptance.strip() if acceptance else None, "phases": names,
            "domains": {folder: name.strip() for folder, name in domains.items()}}


def domain_of(path):
    """The domain folder of a TODO path (`todo/06-write/TODO-01-x.md` -> `06-write`)."""
    parts = Path(path).as_posix().split("/")
    return parts[1] if len(parts) > 2 and parts[0] == "todo" else ""


def by_domain(items, path_of):
    """`items` split by the domain folder of each one's path, in domain-number order, each keeping its order: one
    group (domain None) when every item is in one domain, so a single-domain block renders as it always did."""
    folders = sorted({domain_of(path_of(item)) for item in items})
    if len(folders) <= 1:
        return [(None, list(items))]
    return [(folder, [item for item in items if domain_of(path_of(item)) == folder]) for folder in folders]


def phase_table(phase, phase_rows, domain=None):
    """One phase's plan table (or, in a phase that spans domains, one domain's table: D00 T03 §33), refused when a
    row would pass MAX_TABLE_ROW. `graph()` (so `validate`) and `projection()` both build it here, so validate
    refuses exactly what plan --sync cannot render (D00 T03 §32)."""
    where = f"phase {phase}" + (f", domain {domain}" if domain else "")
    table = markdown_table(
        ["Status", "Reference", "Deliverable", "Needs", "Items"],
        [[f"[{'x' if row.done else ' '}]", row.ref, row.title,
          ", ".join(row.needs) or "none", str(len(CHECKLIST.findall(row.body)))] for row in phase_rows],
    )
    # Every row is padded to the widest cell, so one long title wraps the whole table: name the widest section.
    widest = max(phase_rows, key=lambda row: len(row.title) + len(", ".join(row.needs)))
    require(all(len(line) <= MAX_TABLE_ROW for line in table),
            f"plan table for {where} wraps raw md ({max(len(line) for line in table)} > {MAX_TABLE_ROW} "
            f"chars); shorten the heading and Deliverable of {widest.ref} (title {len(widest.title)} chars)")
    return table


NOT_IN_PLAN = "### Not in the plan yet: sections still to be written"


def author_sections(missing, rows):
    """The table of the sections that still have TODO files to write, in plan order, each with how many (D00 T03
    §58: the plan lists sections, never TODO files). `missing` is `to_author()`. A row over the table limit is
    refused naming its section, as a phase table's is (D00 T03 §32); `validate` and `projection` both build it."""
    counts = {}
    for item in missing:
        counts[item["ref"]] = counts.get(item["ref"], 0) + 1
    table = markdown_table(["Status", "Reference", "Deliverable", "Files to write"],
                           [[f"[{'x' if rows[ref].done else ' '}]", ref, rows[ref].title, str(count)]
                            for ref, count in counts.items()])
    # Every row is padded to the widest, so the one to shorten is the section with the longest title.
    widest = max(counts, key=lambda ref: len(rows[ref].title))
    require(all(len(line) <= MAX_TABLE_ROW for line in table),
            f"the plan's table of sections still to be written wraps raw md ({max(len(line) for line in table)} > "
            f"{MAX_TABLE_ROW} chars); shorten the title of {widest}")
    return table

def _plan_tables_ok(root, rows):
    """Build every table the plan renders, grouped as projection() groups them, so a tree validate accepts always
    syncs (D00 T03 §32, §33)."""
    plan_rows = ordered(rows)
    for phase in sorted({row.phase for row in plan_rows}):
        for folder, group in by_domain([row for row in plan_rows if row.phase == phase], lambda row: row.path):
            phase_table(phase, group, folder)
    missing = to_author(root, rows)
    if missing:
        author_sections(missing, rows)


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
    checks = {row.ref: CHECKLIST.findall(row.body) for row in rows}
    for phase in sorted({row.phase for row in rows}):
        phase_rows = [row for row in rows if row.phase == phase]
        item_count = sum(len(checks[row.ref]) for row in phase_rows)
        name = config["phases"].get(phase)
        title = f"Phase {phase}: {name}" if name else f"Phase {phase}"
        lines += [f"### {title}", "", f"Sections: {len(phase_rows)} | Checklist items: {item_count}", ""]
        # A phase that spans domains reads one domain at a time, so all of one app is one contiguous part of the
        # plan with its own progress (D00 T03 §33); a single-domain phase renders exactly as before.
        for folder, group in by_domain(phase_rows, lambda row: row.path):
            if folder is not None:
                group_items = sum(len(checks[row.ref]) for row in group)
                lines += [f"#### {config['domains'].get(folder, folder)}", "",
                          f"Sections: {len(group)} | Checklist items: {group_items} | "
                          f"Verified: {sum(row.done for row in group)}", ""]
            lines += phase_table(phase, group, folder)
            lines.append("")
    missing = to_author(root, all_rows)
    if missing:
        files = f"{len(missing)} TODO {'file is' if len(missing) == 1 else 'files are'}"
        lines += [NOT_IN_PLAN, "",
                  f"The sections of {files} not written yet, so they are in no phase above and in no total. They "
                  f"join the phase tables as each file is written by the section named here, in plan order.", ""]
        lines += author_sections(missing, all_rows)
        lines.append("")
    total_items = sum(len(items) for items in checks.values())
    completed_items = sum(state == "x" for items in checks.values() for state, _ in items)
    ready = sum(disposition(r, all_rows) == 0 for r in rows)
    still = (f", {len(missing)} TODO {'file' if len(missing) == 1 else 'files'} still to author (not counted here)"
             if missing else "")
    lines += [f"Progress: {sum(r.done for r in rows)}/{len(rows)} verified sections, "
              f"{ready} ready to run now{still}.", "",
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
                         "cap_outcome": data.get("cap_outcome"),
                         # The verdict of a completion review; a receipt from before the plan review names a
                         # pre-build record's path there instead, which is no verdict.
                         "completion": data["completion"].get("verdict")
                         if isinstance(data.get("completion"), dict) else None})
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
    wording changes it. A Deferred line counts: it moves scope to another section. Closing it as Resolved once its owner
    ships (changing only the marker) is the same contract, so a stamped section's receipt survives the closing."""
    body = row.body.replace("\r\n", "\n")
    body = re.sub(r"^- \[x\] ", "- [ ] ", body, flags=re.M)
    body = re.sub(r"^> \*\*(?:Verified|Review|Started|Duration):\*\* .*(?:\n|$)", "", body, flags=re.M)
    body = re.sub(r"^> \*\*Resolved:\*\*", "> **Deferred:**", body, flags=re.M)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    text = f"## {row.number}. {row.title}\n\n{body}\n"
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _instant(text):
    """An ISO 8601 UTC instant (`YYYY-MM-DDTHH:MM:SSZ`) as a comparable tuple, or None, also for a shape that names
    no real instant (`2026-02-30`, `25:70:90`; D00 T03 §50 review round 1)."""
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z", (text or "").strip())
    if not m:
        return None
    try:
        datetime.datetime(*(int(x) for x in m.groups()))
    except ValueError:
        return None
    return tuple(int(x) for x in m.groups())


def contract_ok(last, row, completion):
    """The last returned completion round echoes `CONTRACT: sha256:<digest>` and it is still the section's contract
    (D00 T03 §14): an edit after dispatch, or an extension after approval, needs a fresh round."""
    ref = row.ref
    lines = [x.strip() for x in last["review"].splitlines() if x.strip()]
    echoed = CONTRACT_LINE.fullmatch(lines[2]) if len(lines) > 2 else None
    require(echoed is not None,
            f"round {last['number']} of {completion} must open with 'SECTION: {ref}', 'PURPOSE: completion' and "
            f"'CONTRACT: sha256:<digest>' copied from its prompt: {ref}")
    require(echoed[1] == contract_digest(row),
            f"round {last['number']} of {completion} reviewed contract {echoed[1]}, but the section is now "
            f"{contract_digest(row)}; it changed after its completion review, so run a fresh one: {ref}")


COMPLETION_RULES = (1, 2)


def completion_rules(data, last):
    """The completion rules a receipt met (D00 T03 §16): the `completion_rules` it records, or, for a receipt written
    before the field existed, 2 when its completion review ran from CONTRACT_REQUIRED_FROM on and 1 before."""
    if "completion_rules" in data:
        return data["completion_rules"]
    run = _instant(last.get("run"))
    return 2 if run is not None and run >= _instant(CONTRACT_REQUIRED_FROM) else 1


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
                require(target is None or target in rows or target in removed_sections(root),
                        f"gap {gap} of round {n} in {path} is filed to {target}, which is no section: {ref}")
        last["dispositions"] = dispositions  # gap -> filed section, or None for `extended`
    return last


def same_request(persisted, data):
    """What a receipt on disk (its bytes, or None) records differently from the receipt a stamp request builds: the
    implementation commit, the reviews, the plan review and the completion review. Empty when it is the same request."""
    try:
        held = json.loads(persisted.decode("utf-8"))
    except (AttributeError, ValueError):
        return ["content (it is not readable)"]
    held = held if isinstance(held, dict) else {}
    names = {"implementation_sha": "commit", "reviews": "reviews", "plan": "plan review",
             "completion": "completion review"}
    return [label for key, label in names.items()
            if held.get(key) != json.loads(json.dumps(data.get(key)))]


def stamp(root, ref, sha, reviews, checks, date, sync_plan=False, cap_outcome=None, completion=None, plan=None):
    """Close a section: write its receipt, tick its row and checklist, add the Verified and Review lines. The receipt
    records the plan review (`plan`: its findings file, required), the completion review (`completion`: {"report",
    "verdict"}, required), the pin's review schedule every pass is checked against, the review rounds spent against
    the cap and, when a review stopped at the cap, what was done about it."""
    root = Path(root)
    rows = graph(root)
    require(ref in rows, "unresolved section: " + ref)
    row = rows[ref]
    # A stamped section is only ever a retry (a stamp cut short before the plan was written): the request is compared
    # with its persisted receipt below, before anything is written.
    stamped = row.done
    if not stamped:
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
    require(completion is not None,
            f"--completion '<findings file>:<{'|'.join(COMPLETION_VERDICTS)}>' is required: run the completion review "
            f"(scripts/review-dispatch.py --kind completion; under a three-pass pin after the round, under a rotation "
            f"pin before the rounds) and name its verdict: {ref}")
    require(plan is not None,
            f"--plan '<findings file>' is required: run the one-pass plan review (scripts/review-dispatch.py --kind "
            f"plan) before the build: {ref}")
    stopped = any(isinstance(r, dict) and str(r.get("verdict", "")).startswith("stopped-") for r in reviews)
    require(stopped == bool((cap_outcome or "").strip()),
            "--cap-outcome is required with a stopped verdict (what was done when the review stopped at the cap or on "
            "severity), and only then")
    data = {"ref": ref, "title": row.title, "implementation_sha": sha, "date": date,
            "reviews": reviews, "checks": checks}
    # Every argument is checked before anything is read or written.
    receipt_data_ok(data, ref, sha, root=root, building=True)
    data["completion"] = completion_record(root, completion, ref, sha)
    for target in data["completion"]["filed"]:
        require(target in rows, f"completion gap filed as {target}, which does not resolve: {ref}")
    data["rounds_spent"] = rounds_recorded(root, reviews)
    data["round_cap"] = REVIEW_ROUND_CAP
    if stopped:
        data["cap_outcome"] = cap_outcome.strip()
    data["plan"] = plan_record(root, plan, ref, start=build_start(root, row.path, row.body, ref))
    # The section's pin is the one at its plan review's candidate: the dispatcher ran every pass under it.
    data["schedule_sha"] = section_pin_sha(root, data["plan"]["candidate"], sha)
    data["schedule"] = pin_schedule(root, data["schedule_sha"], ref)
    dispatch = review_dispatch()
    if data["schedule"].get("policy") == dispatch.THREE_PASS:
        # A three-pass section's cap counts every returned pass: plan, round, completion and each reconciliation.
        held = dispatch.read_findings((root / data["plan"]["report"]).read_bytes().decode("utf-8"))
        data["passes_spent"] = 3 + sum(1 for e in held["reconciliations"]
                                       if dispatch.returned_one_pass(e, "reconciliation"))
        data["pass_cap"] = dispatch.review_pin.pass_cap(data["schedule"])
    receipt_data_ok(data, ref, sha, root=root, surface=field(row.body, "Surface") == "yes")
    receipt_path = root / receipt
    plan_path = root / PLAN
    # A receipt already on disk is what a stamp killed between its writes leaves. It is replaced (or, once the TODO
    # file carries the stamp, accepted) only when it records this same request; any other is refused untouched.
    receipt_before = receipt_path.read_bytes() if receipt_path.is_file() else None
    if stamped or receipt_before is not None:
        differs = same_request(receipt_before, data)
        if stamped:
            require(receipt_before is not None and not differs, f"already verified: {ref}"
                    + (f" (receipt {receipt} " + ("is missing)" if receipt_before is None
                                                  else "records a different " + ", ".join(differs) + ")")))
            fresh = plan_path.is_file() and read_text(plan_path) == projection(root)
            if (sync_plan or plan_path.is_file()) and not fresh:
                projections(root, sync=True)  # the retry of a stamp that was cut short before its plan write
            return receipt
        require(not differs, f"receipt already exists: {receipt} (a leftover that records a different "
                             + ", ".join(differs) + "); nothing was written")
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
    original_plan_bytes = plan_path.read_bytes() if plan_path.is_file() else None
    try:
        atomic(receipt_path, json.dumps(data, indent=2) + "\n")
        atomic(path, text)
        graph(root)
        if sync_plan or original_plan_bytes is not None:
            projections(root, sync=True)
    except BaseException:  # an interrupt between writes must roll back as an error does
        if receipt_before is None:
            receipt_path.unlink(missing_ok=True)
        elif not receipt_path.is_file() or receipt_path.read_bytes() != receipt_before:
            atomic(receipt_path, receipt_before)  # the leftover this call replaced goes back as it was
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
    Unstamped note in the section saying why. The section's own findings file is kept under a revoked name too, and a
    `Started:` line it still carries becomes a `Duration:` note: the reopened section takes a fresh review cycle (a new
    `Started:` line, plan review, round and completion review), which the dispatcher refuses while the old cycle's
    records sit in the findings file. Re-stamping later writes a fresh receipt."""
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
    findings_path = root / section_findings(root, ref)
    kept_path = None
    if findings_path.is_file():
        kept_path = findings_path.with_name(f"{findings_path.stem}.revoked-{date}.md")
        n = 2
        while kept_path.exists():
            kept_path = findings_path.with_name(f"{findings_path.stem}.revoked-{date}-{n}.md")
            n += 1
    body = stamp_lines.sub("", row.body)
    body = re.sub(r"^- \[x\] (Commit:.+)$", r"- [ ] \1", body, flags=re.M)
    body = re.sub(r"^> \*\*Started:\*\* (.+)$", lambda m: f"> **Duration:** started {m[1]}, reopened {when}", body,
                  flags=re.M)
    kept = f"; review record kept as `{kept_path.relative_to(root).as_posix()}`" if kept_path else ""
    body += f"\n\n> **Unstamped:** {when}: {reason.strip()} (revoked receipt `{revoked}`{kept})"
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
        if kept_path is not None:
            os.replace(findings_path, kept_path)
        graph(root)
        if original_plan_bytes is not None:
            projections(root, sync=True)
    except BaseException:  # an interrupt between writes must roll back as an error does
        try:
            if kept_path is not None and kept_path.is_file() and not findings_path.exists():
                os.replace(kept_path, findings_path)
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
