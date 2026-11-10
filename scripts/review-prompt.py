#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Build the prompt for a completion review or for a code review round, from a TODO section reference (D00 T03 §27).

    python scripts/review-prompt.py completion 'D02 T01 §6' --purpose "<what the feature is for the user>"
        (--context <file> | --no-context "<reason>") --out <scratch file>
    python scripts/review-prompt.py round 'D02 T01 §6' <base> <tip> --purpose "<what the candidate is meant to do>"
        --governing "<the documents that apply>" [--note <file>] [--path <path> ...] --out <scratch file>

Then pass `--out` to `python scripts/review-dispatch.py --writer claude --prompt <scratch file> --record <findings file>`.

Exit 0: the prompt is written, and one line of JSON says what it holds. Exit 2: refused, with the reason on standard
error and `--out` untouched. Nothing else is written, and no reviewer runs.

completion fills `docs/completion-review-prompt.md` (the part below its `---` line): the reference and title, the
section text, its contract digest, the purpose, the file's Implementation Order table, and the context. Exactly one of
`--context` and `--no-context` is given; a section that says `**Surface:** yes`, has an `> **Implements:**` line or
names `design/SPEC.md` needs `--context` (a file holding the SPEC and inventory excerpts it cites, inlined).

round fills `docs/review-round-prompt.md` the same way: both commits as full SHAs, the purpose, the section as
`resolve` prints it, a Scope block and the diff. `<base>` must be an ancestor of `<tip>` and a different commit, so a
reversed, divergent or empty range is refused. The inlined diff may be at most MAX_DIFF_BYTES; a larger candidate is
reviewed in parts with `--path`: the Scope block and the JSON `omitted` list name the changed paths this part leaves
out, and the round is complete only when every changed path has been in one part.

The prompt is a scratch file: `--out` inside the repository is refused. Stdlib only.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import todo_graph

MAX_DIFF_BYTES = 400_000  # a round prompt above this is split with --path, never cut short
GIT_SECONDS = 120
TEMPLATES = {"completion": "docs/completion-review-prompt.md", "round": "docs/review-round-prompt.md"}
# What each command replaces in its template, in the order the template has it: the exact text, then the key of the
# value that takes its place.
FILLS = {
    "completion": (
        ("`<DNN TNN §N> <title>`", "heading"),
        ("`<inline the section from its heading to its Test checkpoint>`", "section"),
        ("`<the line python scripts/todo-graph.py contract-digest '<DNN TNN §N>' prints for that same text, "
         "sha256:...>`", "contract"),
        ("`<one or two sentences>`", "purpose"),
        ("`<inline the excerpts>`", "excerpts"),
        ("`<inline them, or name the paths to read>`", "neighbours"),
    ),
    "round": (
        ("`<FULL_SHA>` or `<BASE_SHA>..<TIP_SHA>` (inspect it with `git show` or `git diff`)", "range"),
        ("`<one or two sentences>`", "purpose"),
        ("`<DNN TNN §N>` (its contract: `python3 scripts/todo-graph.py resolve \"<DNN TNN §N>\"`)", "section"),
        ("`<the spec, plan or design file that applies>`", "governing"),
    ),
}
# Every backticked span holding `<` that each template has below its `---` line, in order: the ones filled above and
# the ones that stay as the reviewer's reply format. A template whose spans differ from this list has changed, and the
# command refuses it rather than send a placeholder nobody filled (or drop a field somebody added).
PLACEHOLDERS = {
    "completion": (
        "<DNN TNN §N> <title>",
        "<inline the section from its heading to its Test checkpoint>",
        "<the line python scripts/todo-graph.py contract-digest '<DNN TNN §N>' prints for that same text, sha256:...>",
        "<one or two sentences>",
        "<inline the excerpts>",
        "<inline them, or name the paths to read>",
        "SECTION: <DNN TNN §N>",
        "CONTRACT: sha256:<digest>",
    ),
    "round": (
        "<FULL_SHA>",
        "<BASE_SHA>..<TIP_SHA>",
        "<one or two sentences>",
        "<DNN TNN §N>",
        "python3 scripts/todo-graph.py resolve \"<DNN TNN §N>\"",
        "<the spec, plan or design file that applies>",
    ),
}
NEEDS_CONTEXT = (
    (re.compile(r"^\*\*Surface:\*\* yes\s*$", re.M), "it says `**Surface:** yes`"),
    (re.compile(r"^> \*\*Implements:\*\*", re.M), "it has an `> **Implements:**` line"),
    (re.compile(r"design/SPEC\.md"), "it names `design/SPEC.md`"),
)


class Refused(Exception):
    """The prompt cannot be built as asked; the message is the one-line reason."""


def spans(text):
    """Every backticked span of `text` that holds `<`, in order. Backticks pair off in order within a line."""
    found = []
    for line in text.splitlines():
        found += [span for span in re.findall(r"`([^`]*)`", line) if "<" in span]
    return found


def template(root, kind):
    """The prompt part of a template (below its `---` line), checked against PLACEHOLDERS before anything is filled."""
    path = Path(root) / TEMPLATES[kind]
    try:
        text = todo_graph.read_text(path)
    except OSError as exc:
        raise Refused(f"cannot read {TEMPLATES[kind]}: {exc}") from None
    _, rule, body = text.partition("\n---\n")
    if not rule:
        raise Refused(f"{TEMPLATES[kind]} has no `---` line, so where its prompt starts is unknown")
    found, expected = spans(body), list(PLACEHOLDERS[kind])
    if found != expected:
        for index in range(max(len(found), len(expected))):
            have = found[index] if index < len(found) else None
            want = expected[index] if index < len(expected) else None
            if have != want:
                raise Refused(f"{TEMPLATES[kind]} changed: placeholder {index + 1} is {have!r}, expected {want!r}; "
                              "update FILLS and PLACEHOLDERS in scripts/review-prompt.py to match the template")
    for old, _ in FILLS[kind]:
        if body.count(old) != 1:
            raise Refused(f"{TEMPLATES[kind]} changed: {old!r} appears {body.count(old)} times, expected once")
    return body.lstrip("\n")


def fill(body, kind, values):
    """Replace every FILLS text in one pass, so text that a value brings in is never itself replaced."""
    by_text = {old: values[key] for old, key in FILLS[kind]}
    pattern = re.compile("|".join(re.escape(old) for old in sorted(by_text, key=len, reverse=True)))
    return pattern.sub(lambda m: by_text[m.group(0)], body)


def fenced(text, language):
    """`text` in a code fence longer than any run of backticks inside it."""
    fence = "`" * max(4, max((len(run) for run in re.findall(r"`+", text)), default=0) + 1)
    return f"\n\n{fence}{language}\n{text.rstrip()}\n{fence}\n"


def section_row(root, reference):
    try:
        rows = todo_graph.graph(Path(root))
    except todo_graph.Refused as exc:
        raise Refused(f"the TODO tree does not validate: {exc}") from None
    ref, code = todo_graph.extract_ref(reference, rows)
    if code == 2:
        raise Refused(f"no section reference in {reference!r} (write it as 'DNN TNN §N')")
    if code == 1:
        raise Refused(f"no such section: {ref}")
    return ref, rows[ref]


def section_text(row):
    return f"## {row.number}. {row.title}\n\n{row.body.strip()}\n"


def scratch_path(root, out):
    """`--out` as an absolute path, refused when it lies inside the repository."""
    path = Path(out).resolve()
    if path == Path(root).resolve() or Path(root).resolve() in path.parents:
        raise Refused(f"--out {out} is inside the repository; a prompt is a scratch file (the folder OFFICE_SCRATCH "
                      "names, or the session scratchpad)")
    return path


def one_line(text, what):
    text = " ".join(text.split())
    if not text:
        raise Refused(f"{what} is empty")
    return text


def read_option(path, option):
    try:
        text = todo_graph.read_text(path).strip()
    except OSError as exc:
        raise Refused(f"cannot read {option} {path}: {exc}") from None
    if not text:
        raise Refused(f"{option} {path} is empty")
    return text


def completion(root, args):
    ref, row = section_row(root, args.ref)
    if (args.context is None) == (args.no_context is None):
        raise Refused("give exactly one of --context <file> and --no-context <reason>")
    if args.no_context is not None:
        for pattern, why in NEEDS_CONTEXT:
            if pattern.search(row.body):
                raise Refused(f"{ref} needs --context, not --no-context: {why}, so the SPEC and inventory excerpts it "
                              "cites must be inlined in a context file")
        context = "No further context: " + one_line(args.no_context, "--no-context")
        excerpts = "none: " + one_line(args.no_context, "--no-context")
    else:
        context = read_option(args.context, "--context")
        excerpts = "inlined with the neighbouring sections, below"
    out = scratch_path(root, args.out)
    body = template(root, "completion")
    table = re.search(r"(?ms)^## Implementation Order\n.*?(?=^## )", todo_graph.read_text(Path(root) / row.path))
    if table is None:
        raise Refused(f"{row.path} has no Implementation Order table")
    contract = todo_graph.contract_digest(row)
    prompt = fill(body, "completion", {
        "heading": f"`{ref} {row.title}`",
        "section": fenced(section_text(row), "markdown"),
        "contract": f"`{contract}`",
        "purpose": one_line(args.purpose, "--purpose"),
        "excerpts": excerpts,
        "neighbours": f"\n\n{table.group(0).rstrip()}\n\n{context}\n",
    })
    todo_graph.atomic(out, prompt)
    return {"kind": "completion", "ref": ref, "contract": contract, "out": str(out)}


def git(root, *args, check=True):
    """One git command in the repository: its output, or Refused. git comes from the absolute PATH entries only."""
    try:
        done = subprocess.run([todo_graph.git(), *args], cwd=root, capture_output=True, timeout=GIT_SECONDS)
    except todo_graph.Refused as exc:
        raise Refused(str(exc)) from None
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Refused(f"git {args[0]} could not run: {exc}") from None
    if check and done.returncode != 0:
        raise Refused(f"git {args[0]} failed: " + " ".join(done.stderr.decode("utf-8", "replace").split())[:300])
    return done


def commit(root, name):
    done = git(root, "rev-parse", "--verify", "--quiet", "--end-of-options", name + "^{commit}", check=False)
    sha = done.stdout.decode("ascii", "replace").strip()
    if done.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise Refused(f"git does not know the commit {name!r}")
    return sha


def names(root, base, tip, paths=()):
    done = git(root, "diff", "--name-only", "-z", f"{base}..{tip}", "--", *paths)
    return [name for name in done.stdout.decode("utf-8", "replace").split("\0") if name]


def review_round(root, args):
    ref, row = section_row(root, args.ref)
    base, tip = commit(root, args.base), commit(root, args.tip)
    if base == tip:
        raise Refused(f"the base and the tip are the same commit ({base[:12]}), so there is nothing to review; give "
                      "the commit before the candidate's first commit, then its last commit")
    if git(root, "merge-base", "--is-ancestor", base, tip, check=False).returncode != 0:
        if git(root, "merge-base", "--is-ancestor", tip, base, check=False).returncode == 0:
            raise Refused(f"the range is reversed: {tip[:12]} comes before {base[:12]}; give the older commit first")
        raise Refused(f"the range is divergent: {base[:12]} is not an ancestor of {tip[:12]}")
    changed = names(root, base, tip)
    if not changed:
        raise Refused(f"{base[:12]}..{tip[:12]} changes no file (an empty diff)")
    included = names(root, base, tip, args.path) if args.path else changed
    if not included:
        raise Refused("--path selects no changed file; the changed paths are: " + ", ".join(changed))
    omitted = [name for name in changed if name not in included]
    diff = git(root, "diff", f"{base}..{tip}", "--", *args.path).stdout
    if len(diff) > MAX_DIFF_BYTES:
        raise Refused(f"the diff to inline is {len(diff)} bytes, over the limit of {MAX_DIFF_BYTES}; review it in "
                      "parts by giving --path <path> ... for some of the changed paths, then the rest")
    out = scratch_path(root, args.out)
    note = read_option(args.note, "--note") if args.note else ""
    body = template(root, "round")
    prompt = fill(body, "round", {
        "range": f"`{base}..{tip}` (the diff is inlined below under \"Diff\", because your sandbox may not run git; "
                 "the files in the working tree are at or after the tip)",
        "purpose": one_line(args.purpose, "--purpose"),
        "section": f"`{ref}` (its contract is inlined below under \"Section contract\")",
        "governing": one_line(args.governing, "--governing"),
    }).rstrip() + "\n"
    if note:
        prompt += f"\n## Note from the writer\n\n{note}\n"
    scope = ["## Scope", "", f"The candidate `{base}..{tip}` changes {len(changed)} path(s).", "",
             "Included in this prompt:", ""] + [f"- `{name}`" for name in included]
    if omitted:
        scope += ["", "Not in this prompt (review them in another round part):", ""]
        scope += [f"- `{name}`" for name in omitted]
        scope += ["", "This prompt covers only the included paths."]
    prompt += "\n" + "\n".join(scope) + "\n"
    resolved = json.dumps({**row.public(), "body": row.body}, indent=2, ensure_ascii=False)
    prompt += f"\n## Section contract ({ref}, as `resolve` prints it){fenced(resolved, 'json')}"
    prompt += f"\n## Diff{fenced(diff.decode('utf-8', 'replace'), 'diff')}"
    todo_graph.atomic(out, prompt)
    return {"kind": "round", "ref": ref, "base": base, "tip": tip, "included": included, "omitted": omitted,
            "out": str(out)}


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description="Build a completion or round review prompt for a TODO section.")
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("completion", help="the completion review's prompt, before a section is built")
    c.add_argument("ref", help="the section, as 'DNN TNN §N'")
    c.add_argument("--purpose", required=True, help="what the feature is for the user, one or two sentences")
    c.add_argument("--context", help="a file with the SPEC and inventory excerpts and the neighbouring sections")
    c.add_argument("--no-context", help="why no further context applies (tooling sections only)")
    c.add_argument("--out", required=True, help="the scratch file to write")
    r = sub.add_parser("round", help="one code review round's prompt, after a section is built")
    r.add_argument("ref", help="the section, as 'DNN TNN §N'")
    r.add_argument("base", help="the commit before the candidate's first commit")
    r.add_argument("tip", help="the candidate's last commit")
    r.add_argument("--purpose", required=True, help="what the candidate is meant to do, one or two sentences")
    r.add_argument("--governing", required=True, help="the spec, plan or design files that apply")
    r.add_argument("--note", help="a file with anything else the reviewer must know (earlier rounds, owned gaps)")
    r.add_argument("--path", nargs="+", default=[], help="review only these changed paths in this part")
    r.add_argument("--out", required=True, help="the scratch file to write")
    args = parser.parse_args(argv)
    try:
        result = completion(root, args) if args.command == "completion" else review_round(root, args)
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
