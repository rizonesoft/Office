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

A pull request is eligible when it is open, not a draft, by Dependabot or the GitHub Actions bot, labelled
`dependencies` or `pins`, mergeable with a clean merge state, every check green (at least one), and it changes no
`global.json` (the .NET SDK pin moves only through its own proposal, scripts/check-dotnet-pin.py). Eligible pull
requests merge one at a time with `gh pr merge --rebase --match-head-commit <sha>`, then `git pull --ff-only`, then
`python scripts/todo-graph.py validate`; the first failure stops the run and leaves the rest open.

Exit 0 when the run finished (merging some, or none being eligible), 1 when a merge, pull or validate failed, 2 when
the clone or campaign state made it unsafe to start (0 with `--skip-unsafe`, so a scheduled run alerts only on real
failures), 3 when git or gh could not be read.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))  # todo_graph
sys.path.insert(0, str(ROOT / "scripts"))  # campaign_guard

AUTHORS = {"dependabot[bot]", "app/dependabot", "github-actions[bot]", "app/github-actions"}
LABELS = {"dependencies", "pins"}
GREEN = {"SUCCESS", "NEUTRAL", "SKIPPED"}
PR_FIELDS = "number,author,labels,isDraft,headRefOid,mergeable,mergeStateStatus,statusCheckRollup,files,title"


class Unsafe(Exception):
    """The clone or the campaign is not in a state to merge into."""


class Unreadable(Exception):
    """git or gh failed, so the state could not be read at all."""


def run(args, root):
    """Run one command in the clone; returns (exit code, stdout, stderr)."""
    proc = subprocess.run(args, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout, proc.stderr


def checked(runner, root, args, what):
    code, out, err = runner(args, root)
    if code != 0:
        raise Unreadable(f"{what} failed: {(err or out).strip()[:200]}")
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


def safety(runner, root, session):
    """Raise Unsafe naming the first state that forbids merging."""
    owner = campaign_owner(root)
    if owner is not None and owner != session:
        raise Unsafe(f"a campaign run is open for session {owner}; only that session merges, at a section boundary")
    if checked(runner, root, ["git", "status", "--porcelain"], "git status").strip():
        raise Unsafe("the working tree has uncommitted or untracked changes")
    checked(runner, root, ["git", "fetch", "--quiet", "origin", "main"], "git fetch")
    branch = checked(runner, root, ["git", "rev-parse", "--abbrev-ref", "HEAD"], "git rev-parse").strip()
    if branch != "main":
        raise Unsafe(f"the clone is on branch {branch}, not main")
    head = checked(runner, root, ["git", "rev-parse", "HEAD"], "git rev-parse").strip()
    upstream = checked(runner, root, ["git", "rev-parse", "origin/main"], "git rev-parse").strip()
    if head != upstream:
        raise Unsafe(f"HEAD {head[:12]} is not origin/main {upstream[:12]}; push or pull first")
    started = in_progress_sections(root)
    if started:
        raise Unsafe(f"a section is in progress: {', '.join(started)}")


def ineligibility(pr):
    """Why `pr` (one object of `gh pr list --json`) may not merge by itself, or None when it may."""
    login = (pr.get("author") or {}).get("login", "")
    if login not in AUTHORS:
        return f"author {login or 'unknown'} is not Dependabot or the GitHub Actions bot"
    if not LABELS & {label.get("name") for label in pr.get("labels") or []}:
        return "not labelled dependencies or pins"
    if pr.get("isDraft"):
        return "a draft"
    if pr.get("mergeable") != "MERGEABLE" or pr.get("mergeStateStatus") != "CLEAN":
        return f"not cleanly mergeable ({pr.get('mergeable')}, {pr.get('mergeStateStatus')})"
    checks = pr.get("statusCheckRollup") or []
    if not checks:
        return "no checks ran"
    red = [c.get("name") or c.get("context") or "?" for c in checks
           if (c.get("conclusion") or c.get("state")) not in GREEN]
    if red:
        return f"checks not green: {', '.join(red)}"
    if any(Path(f.get("path", "")).name == "global.json" for f in pr.get("files") or []):
        return "changes global.json (the .NET SDK pin moves only through its own proposal)"
    return None


def eligible(runner, root):
    out = checked(runner, root, ["gh", "pr", "list", "--state", "open", "--base", "main", "--limit", "100",
                                 "--json", PR_FIELDS], "gh pr list")
    try:
        prs = json.loads(out)
    except ValueError:
        raise Unreadable("gh pr list gave no JSON") from None
    chosen, skipped = [], []
    for pr in sorted(prs, key=lambda p: p.get("number", 0)):
        why = ineligibility(pr)
        (skipped.append((pr.get("number"), why)) if why else chosen.append(pr))
    return chosen, skipped


def merge_all(runner, root, prs, dry_run=False):
    """Merge `prs` in order; returns (merged numbers, the failure message or None)."""
    merged = []
    for pr in prs:
        number, sha = pr["number"], pr["headRefOid"]
        if dry_run:
            merged.append(number)
            continue
        steps = (["gh", "pr", "merge", str(number), "--rebase", "--match-head-commit", sha],
                 ["git", "pull", "--ff-only", "--quiet", "origin", "main"],
                 [sys.executable, str(Path(root) / "scripts" / "todo-graph.py"), "validate"])
        for step in steps:
            code, out, err = runner(step, root)
            if code != 0:
                return merged, f"#{number}: {' '.join(step[:3])} failed: {(err or out).strip()[:200]}"
        merged.append(number)
    return merged, None


def main(argv=None, root=ROOT, runner=run):
    parser = argparse.ArgumentParser(description="Merge green dependency pull requests at a safe moment.")
    parser.add_argument("--session", help="the campaign session that owns the run guard (at a section boundary)")
    parser.add_argument("--dry-run", action="store_true", help="report what would merge and change nothing")
    parser.add_argument("--skip-unsafe", action="store_true",
                        help="exit 0 when the moment is unsafe (the scheduled task), so only real failures alert")
    args = parser.parse_args(argv)
    try:
        safety(runner, root, args.session)
        chosen, skipped = eligible(runner, root)
    except Unsafe as exc:
        print(f"merge-prs: not merging: {exc}", file=sys.stderr)
        return 0 if args.skip_unsafe else 2
    except Unreadable as exc:
        print(f"merge-prs: cannot read the state: {exc}", file=sys.stderr)
        return 3
    for number, why in skipped:
        print(f"merge-prs: skipping #{number}: {why}")
    merged, failure = merge_all(runner, root, chosen, args.dry_run)
    verb = "would merge" if args.dry_run else "merged"
    print(f"merge-prs: {verb} {', '.join(f'#{n}' for n in merged) if merged else 'nothing'}")
    if failure:
        print(f"merge-prs: stopped at {failure}; the rest stay open for the owner", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
