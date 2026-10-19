"""The canonical TODO graph: parse todo/NN-domain/TODO-NN-*.md, validate it, order it, project the plan.

Adapted from swisshotelschool-coza's scripts/lib/todo_graph.py (itself a port of rizonetech-com's
scripts/lib/workflow.py), extended with the ScratchPad, Resolute, and Recto format rules:
Adjacency declarations, bidirectional XREFs, index coverage, frozen freeze checks, and durable
deferrals. Rules: todo/README.md.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PLAN = "todo/implementation-plan.md"
REF = re.compile(r"(?:D(?P<d>\d{2})\s+)?(?:T(?P<t>\d{2})\s+)?§(?P<s>[1-9]\d*)")
ROW = re.compile(r"^\|\s*([1-9]\d*)\s*\|\s*§([1-9]\d*)\s*\|\s*([^|]+)\|\s*([^|]*)\|\s*\[([ x])\]\s*\|$")
# What a section needs from outside the repository. The WAITING values are people, companies, or the
# operator's own hands: a section naming one stays blocked until the answer is recorded and the Need
# is removed from the section.
NEEDS = {"windows-host", "arm64-host", "display-session", "office", "libreoffice", "store-account",
         "attended", "owner-decision", "third-party", "operator"}
WAITING = {"owner-decision", "third-party", "operator"}
STATUSES = {"draft", "active", "blocked", "done", "superseded"}
VERDICTS = {"clean", "fixed", "stopped-at-3"}
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
    m = REF.search(text)
    if m is None:
        return None
    return f"D{m['d'] or domain} T{m['t'] or todo} §{m['s']}"


def extract_ref(text, rows):
    """Resolve whatever the caller had in front of them: a DNN TNN §N reference, a pasted plan row,
    or a '<path> §N' pair (POSIX or Windows path). Returns (ref_or_None, exit_code): 1 no such
    section, 2 no reference."""
    normalized = text.replace("\\", "/")
    m = re.search(r"D(\d{2})\s+T(\d{2})\s+§([1-9]\d*)", normalized)
    if m:
        ref = f"D{m[1]} T{m[2]} §{int(m[3])}"
        return (ref, 0) if ref in rows else (ref, 1)
    m = re.search(r"(\d{2})-[a-z0-9-]+/TODO-(\d{2})-[a-z0-9-]+\.md\s*§([1-9]\d*)", normalized)
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


def commit_ok(root, sha):
    kind = subprocess.run(["git", "-C", str(root), "cat-file", "-t", sha],
                          capture_output=True, text=True, timeout=30)
    require(kind.returncode == 0 and kind.stdout.strip() == "commit", "not a commit: " + sha)
    on_branch = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", sha, "HEAD"],
                               capture_output=True, timeout=30)
    require(on_branch.returncode == 0, "commit is not on this branch: " + sha)


def _head_commits(root):
    res = subprocess.run(["git", "-C", str(root), "rev-list", "HEAD"],
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


def receipt_data_ok(data, ref, stamp_sha, root=None):
    require(isinstance(data, dict), f"receipt is not an object: {ref}")
    require(data.get("ref") == ref and data.get("implementation_sha") == stamp_sha,
            f"receipt does not match its stamp: {ref}")
    rounds = data.get("reviews")
    require(isinstance(rounds, list) and rounds and all(
        isinstance(r, dict) and isinstance(r.get("round"), int)
        and isinstance(r.get("report"), str) and r["report"]
        and isinstance(r.get("verdict"), str) and r["verdict"] in VERDICTS for r in rounds),
        f"receipt has no valid review rounds (verdict one of {', '.join(sorted(VERDICTS))}): {ref}")
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
            cur = root_path
            for part in report.parts:
                cur = cur / part
                require(not cur.is_symlink(), f"invalid review report path ({raw_report}): {ref}")
            report_path = root_path / report
            require(report_path.is_file()
                    and report_path.resolve().is_relative_to(root_resolved)
                    and bool(read_text(report_path).strip()),
                    f"missing or empty review report ({raw_report}): {ref}")
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
        if "-> XREF:" not in line:
            continue
        ref = find_ref(line.split("-> XREF:", 1)[1], domain, todo)
        require(ref is not None, f"XREF line names no section: {line.strip()}")
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
                if re.match(r"^\s*[-*+]\s*\[(?![^\]]+\]\()", line):
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
        for marker in ("Deferred", "Resolved"):
            for line in re.findall(r"^> \*\*" + marker + r":\*\*\s*(.+)$", row.body, re.M):
                owner = find_ref(line.split("-> XREF:", 1)[1], row.ref[1:3], row.ref[5:7]) \
                    if "-> XREF:" in line else None
                require(owner is not None and owner in sections,
                        f"{marker} without a resolving owner: {row.ref}")
                if marker == "Deferred":
                    require(not sections[owner].done,
                            f"stale deferral, owner {owner} shipped; close it as Resolved: {row.ref}")
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
                require(not sections[ref].done or sections[dep].done,
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


def disposition(row, rows):
    """0 ready, 3 already verified, 4 waiting (inactive file, open prerequisite, or a person to answer)."""
    if row.done:
        return 3
    if row.status != "active" or set(row.needs) & WAITING \
            or any(not rows[d].done for d in row.depends):
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
        lines += markdown_table(
            ["Status", "Reference", "Deliverable", "Needs", "Items"],
            [[f"[{'x' if row.done else ' '}]", row.ref, row.title,
              ", ".join(row.needs) or "none", str(len(checks[row.ref]))] for row in phase_rows],
        )
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
            for line in re.findall(r"^> \*\*" + marker + r":\*\*\s*(.+)$", row.body, re.M):
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


def stamp(root, ref, sha, reviews, checks, date, sync_plan=False):
    """Close a section: write its receipt, tick its row and checklist, add the Verified and Review lines."""
    root = Path(root)
    rows = graph(root)
    require(ref in rows, "unresolved section: " + ref)
    row = rows[ref]
    require(not row.done, f"already verified: {ref}")
    require(all(rows[d].done for d in row.depends), f"open prerequisite: {ref}")
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
    data = {"ref": ref, "title": row.title, "implementation_sha": sha, "date": date,
            "reviews": reviews, "checks": checks}
    receipt_data_ok(data, ref, sha, root=root)  # every argument is checked before anything is written
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
    except Exception:
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

M_FLAG = re.M
