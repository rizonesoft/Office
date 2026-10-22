#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Merge green dependency pull requests, one at a time, only when the clone is safe to merge into (D00 T03 §9).

    python scripts/merge_prs.py --session <id>   # at a campaign section boundary (process-plan runs it)
    python scripts/merge_prs.py --skip-unsafe    # the office-pr-merge task: an unsafe moment is a skip, not a failure
    python scripts/merge_prs.py --dry-run        # say what would merge, change nothing

It runs only when: the working tree is clean (untracked files included); after a fetch, `HEAD` is `origin/main` on
branch `main`; no open TODO section carries a `Started:` line (a section in progress); and no campaign is open, unless
`--session` names the session that owns its run guard (`build/claude-campaign-guard.json`).

A pull request is eligible when it is open, not a draft, based on `main`, by Dependabot or the GitHub Actions bot,
labelled `dependencies` or `pins`, mergeable with a clean merge state, every check green (at least one), and none of
its files (all of them, read page by page from the API, both sides of a rename) is a C++ toolchain pin file
(`PIN_FILES`: those pins move only through their own proposals, D00 T03 §11).

Pull requests merge one at a time. Each one is handled under the run guard's lock, so no campaign starts mid-merge:
the clone's safety is checked again, the files are read, the pull request is read again and judged from that fresh
read (a label removed, a base retargeted or a check re-run since the listing stops it), the local checks run once
more, then `gh pr merge --rebase --match-head-commit <sha>` merges exactly the head that was judged, and
`git pull --ff-only` and `python scripts/todo-graph.py validate` follow. Every gh call names the repository `origin`
points at on github.com, so neither GH_REPO nor GH_HOST can aim a merge elsewhere. The first failure stops the run
and leaves the rest open; a pull request already merged when a later step failed is reported as merged. GitHub
has no merge conditional on labels or checks, so a change in the moment between the last read and the merge is not
seen; making one needs write access to the repository, which could merge directly.

Exit 0 when the run finished (merging some, or none being eligible), 1 when a merge, pull or validate failed, 2 when
the clone or campaign state made it unsafe (0 with `--skip-unsafe`, so a scheduled run alerts only on real failures),
3 when git or gh could not be run or read.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))  # todo_graph
sys.path.insert(0, str(ROOT / "scripts"))  # campaign_guard

AUTHORS = {"dependabot[bot]", "app/dependabot", "github-actions[bot]", "app/github-actions"}
LABELS = {"dependencies", "pins"}
GREEN = {"SUCCESS", "NEUTRAL", "SKIPPED"}
PR_FIELDS = ("number,author,labels,isDraft,baseRefName,headRefOid,mergeable,mergeStateStatus,statusCheckRollup,"
             "changedFiles,title")
NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW: a scheduled run opens no console


class Unsafe(Exception):
    """The clone or the campaign is not in a state to merge into."""


class Unreadable(Exception):
    """git or gh could not be run, or failed, so the state could not be read."""


def run(args, root):
    """Run one command in the clone; returns (exit code, stdout, stderr). A command that cannot start is exit 127."""
    try:
        proc = subprocess.run(args, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              creationflags=NO_WINDOW)
    except OSError as exc:
        return 127, "", f"cannot run {args[0]}: {exc}"
    return proc.returncode, proc.stdout, proc.stderr


# The userinfo of any URL in command output (https://user:token@host/...): masked before it is printed, since the
# output reaches the run log and the failure email.
CREDENTIALS = re.compile(r"(\w+://)[^/@\s]+@")


def said(text):
    """A command's output, short and with any credentials in a URL masked, fit to print."""
    return CREDENTIALS.sub(r"\1***@", text.strip())[:200]


def checked(runner, root, args, what):
    code, out, err = runner(args, root)
    if code != 0:
        raise Unreadable(f"{what} failed: {said(err or out)}")
    return out


def in_progress_sections(root):
    """Open TODO sections that carry a `Started:` line: work a merge must not land under."""
    import todo_graph
    return sorted(ref for ref, row in todo_graph.graph(root).items()
                  if not row.done and "> **Started:**" in row.body)


def campaign_owner(root):
    """The session that owns an open campaign run, or None when no run is open."""
    import campaign_guard
    guard = campaign_guard.read_guard(str(root))
    return str(guard.get("session_id", "")) if guard else None


def guard_lock(root):
    """The run guard's own interprocess lock: while it is held, no campaign can start, re-point or end."""
    import campaign_guard
    return campaign_guard._Lock(str(root))


HOST = "github.com"
# The URL forms git writes for a github.com repository, matched whole: the host must be exactly github.com.
ORIGIN_FORMS = (re.compile(r"https://(?:[^@/]+@)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?"),
                re.compile(r"git@github\.com:([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?"),
                re.compile(r"ssh://git@github\.com(?::22)?/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?"))


def origin_repo(runner, root):
    """`owner/name` of the github.com repository `origin` points at. Every gh call names that host and repository,
    so neither GH_REPO, GH_HOST nor another default can aim a merge anywhere but the repository whose clone was
    checked."""
    url = checked(runner, root, ["git", "remote", "get-url", "origin"], "git remote get-url").strip()
    for form in ORIGIN_FORMS:
        match = form.fullmatch(url)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
    # The URL itself is never printed: it can carry a token (https://user:token@host/...), and this message reaches
    # the run log and the failure email.
    raise Unreadable(f"origin is not a {HOST} repository (its URL is not shown, as it may hold credentials)")


def local_safety(runner, root, session, refs=True):
    """Every check that needs no network: the campaign, the working tree, a section in progress, the branch and,
    with `refs`, HEAD against the last fetched origin/main. Run again just before each merge, after the slow reads,
    because an editor, a checkout or a second session does not take the guard lock."""
    owner = campaign_owner(root)
    if owner is not None and owner != session:
        raise Unsafe(f"a campaign run is open for session {owner}; only that session merges, at a section boundary")
    if checked(runner, root, ["git", "status", "--porcelain"], "git status").strip():
        raise Unsafe("the working tree has uncommitted or untracked changes")
    started = in_progress_sections(root)
    if started:
        raise Unsafe(f"a section is in progress: {', '.join(started)}")
    branch = checked(runner, root, ["git", "rev-parse", "--abbrev-ref", "HEAD"], "git rev-parse").strip()
    if branch != "main":
        raise Unsafe(f"the clone is on branch {branch}, not main")
    if not refs:
        return
    head = checked(runner, root, ["git", "rev-parse", "HEAD"], "git rev-parse").strip()
    upstream = checked(runner, root, ["git", "rev-parse", "origin/main"], "git rev-parse").strip()
    if head != upstream:
        raise Unsafe(f"HEAD {head[:12]} is not origin/main {upstream[:12]}; push or pull first")


def safety(runner, root, session):
    """Raise Unsafe naming the first state that forbids merging. The local checks come first, so an open campaign or
    a busy checkout is a skip even when GitHub cannot be reached; then origin/main is fetched and every local check,
    branch and HEAD included, runs against it."""
    local_safety(runner, root, session, refs=False)
    checked(runner, root, ["git", "fetch", "--quiet", "origin", "main"], "git fetch")
    local_safety(runner, root, session)


def ineligibility(pr):
    """Why `pr` (one `gh pr` JSON object) may not merge by itself, from its own fields, or None when they allow it."""
    login = (pr.get("author") or {}).get("login", "")
    if login not in AUTHORS:
        return f"author {login or 'unknown'} is not Dependabot or the GitHub Actions bot"
    if not LABELS & {label.get("name") for label in pr.get("labels") or []}:
        return "not labelled dependencies or pins"
    if pr.get("isDraft"):
        return "a draft"
    if pr.get("baseRefName") != "main":
        return f"based on {pr.get('baseRefName')}, not main"
    if pr.get("mergeable") != "MERGEABLE" or pr.get("mergeStateStatus") != "CLEAN":
        return f"not cleanly mergeable ({pr.get('mergeable')}, {pr.get('mergeStateStatus')})"
    checks = pr.get("statusCheckRollup") or []
    if not checks:
        return "no checks ran"
    red = [c.get("name") or c.get("context") or "?" for c in checks
           if (c.get("conclusion") or c.get("state")) not in GREEN]
    if red:
        return f"checks not green: {', '.join(red)}"
    return None


PIN_FILES = {"vcpkg.json", "vcpkg-configuration.json", "CMakePresets.json"}  # the C++ toolchain pins (D03 T01 §12)


def file_problem(runner, root, repo, number, changed):
    """Why the pull request's files forbid it, read in full (the API pages them; `gh pr list` stops at 100). A rename
    counts on both sides, so moving a pin file away is a change to it."""
    out = checked(runner, root, ["gh", "api", "--hostname", HOST, "--paginate",
                                 f"repos/{repo}/pulls/{number}/files",
                                 "--jq", ".[] | [.filename, (.previous_filename // \"\")] | @json"],
                  "gh api pulls/files")
    try:
        files = [json.loads(line) for line in out.splitlines() if line.strip()]
    except ValueError:
        raise Unreadable(f"gh api pulls/{number}/files gave no JSON lines") from None
    if len(files) != changed:
        return f"the API listed {len(files)} of its {changed} changed files"
    pinned = sorted({Path(name).name for pair in files for name in pair if name and Path(name).name in PIN_FILES})
    if pinned:
        return f"changes {', '.join(pinned)} (a C++ toolchain pin moves only through its own proposal)"
    return None


def candidates(runner, root, repo):
    """The open pull requests whose listed fields allow them, lowest number first, and the rest with a reason."""
    out = checked(runner, root, ["gh", "pr", "list", "--repo", f"{HOST}/{repo}", "--state", "open", "--base", "main",
                                 "--limit", "100", "--json", PR_FIELDS], "gh pr list")
    try:
        prs = json.loads(out)
    except ValueError:
        raise Unreadable("gh pr list gave no JSON") from None
    chosen, skipped = [], []
    for pr in sorted(prs, key=lambda p: p.get("number", 0)):
        why = ineligibility(pr)
        (skipped.append((pr.get("number"), why)) if why else chosen.append(pr["number"]))
    return chosen, skipped


def fresh(runner, root, repo, number):
    """The pull request read again, just before its merge."""
    out = checked(runner, root, ["gh", "pr", "view", str(number), "--repo", f"{HOST}/{repo}",
                                 "--json", PR_FIELDS + ",state"], "gh pr view")
    try:
        return json.loads(out)
    except ValueError:
        raise Unreadable(f"gh pr view {number} gave no JSON") from None


def merge_one(runner, root, repo, number, session, dry_run):
    """Judge and merge one pull request under the guard lock. Returns (outcome, detail): "merged", "skipped",
    "would", "failed" (nothing merged) or "merged-then-failed"; raises Unsafe or Unreadable."""
    import campaign_guard
    try:
        lock = guard_lock(root)
        lock.__enter__()
    except campaign_guard.GuardError as exc:
        raise Unsafe(f"the run guard is busy ({exc})") from None
    try:
        safety(runner, root, session)
        # Slow reads first, then the fresh judgement and a last local check, so the moment between the last read
        # and the merge is as short as it can be. GitHub has no merge conditional on labels or checks: what remains
        # is that moment, and changing a label or re-running a check needs write access, which could merge anyway.
        listed = fresh(runner, root, repo, number)
        problem = file_problem(runner, root, repo, number, listed.get("changedFiles"))
        pr = fresh(runner, root, repo, number)
        if pr.get("headRefOid") != listed.get("headRefOid") or pr.get("changedFiles") != listed.get("changedFiles"):
            return "skipped", f"#{number}: changed while it was being read"
        if pr.get("state") != "OPEN":
            return "skipped", f"#{number}: no longer open"
        why = ineligibility(pr) or problem
        if why:
            return "skipped", f"#{number}: {why}"
        local_safety(runner, root, session)
        if dry_run:
            return "would", f"#{number}"
        code, out, err = runner(["gh", "pr", "merge", str(number), "--repo", f"{HOST}/{repo}", "--rebase",
                                 "--match-head-commit", pr["headRefOid"]], root)
        if code != 0:
            return "failed", f"#{number}: gh pr merge failed: {said(err or out)}"
        for step, what in ((["git", "pull", "--ff-only", "--quiet", "origin", "main"], "git pull"),
                           ([sys.executable, str(Path(root) / "scripts" / "todo-graph.py"), "validate"], "validate")):
            code, out, err = runner(step, root)
            if code != 0:
                return "merged-then-failed", f"#{number} merged, then {what} failed: {said(err or out)}"
        return "merged", f"#{number}"
    finally:
        lock.__exit__(None, None, None)


def main(argv=None, root=ROOT, runner=run):
    parser = argparse.ArgumentParser(description="Merge green dependency pull requests at a safe moment.")
    parser.add_argument("--session", help="the campaign session that owns the run guard (at a section boundary)")
    parser.add_argument("--dry-run", action="store_true", help="report what would merge and change nothing")
    parser.add_argument("--skip-unsafe", action="store_true",
                        help="exit 0 when the moment is unsafe (the scheduled task), so only real failures alert")
    args = parser.parse_args(argv)
    merged, would = [], []
    try:
        safety(runner, root, args.session)
        repo = origin_repo(runner, root)
        chosen, skipped = candidates(runner, root, repo)
        for number, why in skipped:
            print(f"merge-prs: skipping #{number}: {why}")
        for number in chosen:
            outcome, detail = merge_one(runner, root, repo, number, args.session, args.dry_run)
            if outcome == "skipped":
                print(f"merge-prs: skipping {detail}")
            elif outcome == "would":
                would.append(detail)
            elif outcome == "merged":
                merged.append(detail)
            else:
                if outcome == "merged-then-failed":
                    merged.append(f"#{number}")
                print(f"merge-prs: merged {', '.join(merged) or 'nothing'}")
                print(f"merge-prs: stopped: {detail}; the rest stay open for the owner", file=sys.stderr)
                return 1
    except Unsafe as exc:
        print(f"merge-prs: merged {', '.join(merged) or 'nothing'}; not merging further: {exc}", file=sys.stderr)
        return 0 if args.skip_unsafe else 2
    except Unreadable as exc:
        print(f"merge-prs: merged {', '.join(merged) or 'nothing'}; cannot read the state: {exc}", file=sys.stderr)
        return 3
    if args.dry_run:
        print(f"merge-prs: would merge {', '.join(would) or 'nothing'}")
    else:
        print(f"merge-prs: merged {', '.join(merged) or 'nothing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
