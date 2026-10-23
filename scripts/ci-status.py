#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Report the GitHub Actions CI result of one pushed commit, so the campaign never builds on a red `main` (D00 T03 §15).

    python scripts/ci-status.py <ref>                                # exit 0 green, 1 red, 3 pending, 2 unknown
    python scripts/ci-status.py <ref> --wait --timeout 3600          # poll every 30 s until the run ends
    python scripts/ci-status.py <ref> --log R:\\scratch\\ci-<sha>.log  # with red: the failed steps' log, last 400 lines
    python scripts/ci-status.py --pending docs/phase-runs/<run file>  # every pushed head with no recorded outcome

The governing run of a commit is the `ci.yml` run with event `push` on branch `main` whose head is that commit (pull
request and manual runs never count), the newest by creation when there are several, at its latest attempt. `success`
is green; every other conclusion is red and named. No push run 10 minutes after the commit's committer date, or a `gh`
that cannot be read, is unknown. Every `gh` and `git` call has a deadline of 60 seconds or what is left of the
timeout, whichever is shorter, and none starts after it. With --wait, looks keep starting until a second before the
timeout; a look the timeout cuts short leaves the last result standing (still pending), never a guess.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import github_origin
import todo_graph

WORKFLOW = "ci.yml"
BRANCH = "main"
GRACE_SECONDS = 600  # GitHub creates the push run within seconds; ten minutes without one is not a delay
CALL_SECONDS = 60
POLL_SECONDS = 30
RESERVE = 1  # looks keep starting until this long before the timeout
LOG_LINES = 400
GREEN, RED, UNKNOWN, PENDING = 0, 1, 2, 3


class Unknown(Exception):
    """CI cannot be read for this commit: exit 2."""


class DeadlinePassed(Unknown):
    """The timeout ended a look before it finished; with --wait the previous result stands."""


class Tools:
    """The real `git` and `gh`, found on the absolute PATH entries only, each call bounded by a deadline."""

    def __init__(self, root=ROOT):
        self.root = Path(root)

    def call(self, name, args, seconds):
        if seconds <= 0:
            raise DeadlinePassed(f"the wait's deadline passed before {name} {args[0]}")
        program = todo_graph.review_dispatch().find_cli(name)
        if program is None:
            raise Unknown(f"{name} is not on PATH")
        try:
            result = subprocess.run([program, *args], cwd=self.root, capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", stdin=subprocess.DEVNULL, timeout=seconds)
        except subprocess.TimeoutExpired:
            if seconds < CALL_SECONDS:  # cut short by the wait's deadline, not by its own allowance
                raise DeadlinePassed(f"the wait's deadline ended {name} {args[0]}") from None
            raise Unknown(f"{name} {args[0]} did not answer within {int(seconds)} seconds") from None
        except OSError as exc:
            raise Unknown(f"{name} could not start: {exc.strerror or exc}") from None
        return result


def resolve(tools, ref, left):
    """The full SHA and the committer time (UTC) of a ref. `left()` is the time each call may take."""
    result = tools.call("git", ["rev-parse", "--verify", f"{ref}^{{commit}}"], left())
    sha = result.stdout.strip()
    if result.returncode != 0 or len(sha) != 40:
        raise Unknown(f"{ref} is not a commit here")
    shown = tools.call("git", ["show", "-s", "--format=%cI", sha], left())
    try:
        committed = datetime.fromisoformat(shown.stdout.strip()).astimezone(timezone.utc)
    except ValueError:
        raise Unknown(f"cannot read the committer date of {sha[:7]}") from None
    return sha, committed


def origin(tools, seconds):
    """The `--repo` value for `origin`, so GH_REPO or GH_HOST can never point a query at another repository."""
    result = tools.call("git", ["remote", "get-url", "origin"], seconds)
    repo = github_origin.parse(result.stdout) if result.returncode == 0 else None
    if repo is None:  # the URL is never printed: it can carry a token
        raise Unknown(f"origin is not a {github_origin.HOST} repository")
    return github_origin.repo_flag(repo)


def governing_run(tools, sha, seconds, repo):
    """The push run on main for this exact commit (the newest when there are several), or None."""
    result = tools.call("gh", ["run", "list", "--repo", repo, "--workflow", WORKFLOW, "--commit", sha, "--event", "push",
                               "--branch", BRANCH, "--limit", "50", "--json",
                               "databaseId,status,conclusion,url,createdAt,headSha,event,headBranch,attempt"], seconds)
    if result.returncode != 0:
        raise Unknown(f"gh run list failed: {(result.stderr.strip().splitlines() or ['no message'])[-1]}")
    try:
        runs = json.loads(result.stdout or "[]")
    except ValueError:
        raise Unknown("gh run list did not print JSON") from None
    if not isinstance(runs, list) or not all(isinstance(r, dict) for r in runs):
        raise Unknown("gh run list did not print a list of runs")
    # The filters are applied again here: the governing run is the push run on main for this exact commit.
    runs = [r for r in runs if r.get("event") == "push" and r.get("headBranch") == BRANCH and r.get("headSha") == sha]
    return max(runs, key=lambda r: str(r.get("createdAt", ""))) if runs else None


def failing_steps(tools, run_id, seconds, repo):
    """`job: step (conclusion)` for every job that did not succeed, or a note when the jobs cannot be read."""
    try:
        result = tools.call("gh", ["run", "view", str(run_id), "--repo", repo, "--json", "jobs"], seconds)
        jobs = json.loads(result.stdout)["jobs"] if result.returncode == 0 else None
    except (Unknown, ValueError, KeyError, TypeError):
        jobs = None
    if not isinstance(jobs, list):
        return ["  (the failing jobs could not be read)"]
    lines = []
    for job in jobs:
        if not isinstance(job, dict) or job.get("conclusion") in ("success", "skipped", None):
            continue
        steps = [s for s in job.get("steps") or [] if isinstance(s, dict) and s.get("conclusion") not in
                 ("success", "skipped", None)]
        where = ", ".join(f"{s.get('name')} ({s.get('conclusion')})" for s in steps) or "no failing step reported"
        lines.append(f"  {job.get('name')} ({job.get('conclusion')}): {where}")
    return lines or ["  (no failing job reported)"]


def write_log(tools, run_id, path, seconds, repo):
    """The failed steps' log, its last LOG_LINES lines, to `path` outside the repository. Returns a note."""
    target = Path(path).resolve()
    if target == ROOT or ROOT in target.parents:
        return f"log not written: {path} is inside the repository"
    try:
        result = tools.call("gh", ["run", "view", str(run_id), "--repo", repo, "--log-failed"], seconds)
    except Unknown as exc:
        return f"log not written: {exc}"
    if result.returncode != 0:
        return "log not written: gh run view --log-failed failed"
    tail = "\n".join(result.stdout.splitlines()[-LOG_LINES:])
    temp = target.with_name(target.name + ".tmp")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        temp.write_text(tail + "\n", encoding="utf-8")
        os.replace(temp, target)
    except OSError as exc:  # a full or locked scratch folder loses the log, never the CI result
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass  # best-effort cleanup; the failure itself is the note returned below
        return f"log not written: {exc.strerror or exc}: {target}"
    return f"log: {target} (last {LOG_LINES} lines)"


def status(tools, ref, now, deadline, log=None, clock=time.monotonic):
    """(exit code, lines) for one look at the commit's CI."""
    def left():
        """The time the next call may take: 60 seconds or what is left, and none at all past the deadline."""
        remaining = deadline - clock()
        if remaining <= 0:
            raise DeadlinePassed("the wait's deadline passed before CI could be read")
        return min(CALL_SECONDS, remaining)
    try:
        sha, committed = resolve(tools, ref, left)
        repo = origin(tools, left())
        run = governing_run(tools, sha, left(), repo)
    except DeadlinePassed:
        raise
    except Unknown as exc:
        return UNKNOWN, [f"unknown {ref}: {exc}"]
    short = sha[:7]
    if run is None:
        waited = (now - committed).total_seconds()
        if waited < GRACE_SECONDS:
            return PENDING, [f"pending {short}: no push run yet ({int(waited)} s after the commit)"]
        return UNKNOWN, [f"unknown {short}: no {WORKFLOW} push run on {BRANCH} {int(waited)} s after the commit"]
    head = f"{short} run {run.get('databaseId')} attempt {run.get('attempt', 1)} {run.get('url', '')}".rstrip()
    if run.get("status") != "completed":
        return PENDING, [f"pending {head} ({run.get('status')})"]
    if run.get("conclusion") == "success":
        return GREEN, [f"green {head}"]
    lines = [f"red {head} ({run.get('conclusion') or 'no conclusion'})"]
    try:
        lines += failing_steps(tools, run.get("databaseId"), left(), repo)
        if log:
            lines.append(write_log(tools, run.get("databaseId"), log, left(), repo))
    except Unknown as exc:  # the run is red either way; only its details ran out of time
        lines.append(f"  ({exc})")
    return RED, lines


# D00 T03 §17: the pushed heads of main whose CI nobody has recorded, rebuilt from the pushed history.
OUTCOME = re.compile(r"\bci-(?:green|superseded) ([0-9a-f]{7,40})\b")
PENDING_RECORD = re.compile(r"\bci-pending ([0-9a-f]{7,40})\b")
RUN_LIMIT = 500  # one gh page; a full page may mean a cut-off history, which is unknown, never complete
HISTORY_LIMIT = 5000
PENDING_SECONDS = 600


def records(run_file):
    """(outcome SHAs, pending SHAs) recorded in the run file and every run file beside it (D00 T03 §15 and §17)."""
    target = Path(run_file).resolve()
    files = sorted(set(target.parent.glob("*.md")) | ({target} if target.exists() else set()))
    outcomes, pendings = set(), set()
    for path in files:
        try:
            text = path.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise Unknown(f"cannot read the run file {path.name}: {getattr(exc, 'strerror', None) or exc}") from None
        outcomes |= set(OUTCOME.findall(text))
        pendings |= set(PENDING_RECORD.findall(text))
    return outcomes, pendings


def recorded(prefixes, sha):
    return any(sha.startswith(p) for p in prefixes)


def push_runs(tools, repo, seconds):
    """Every ci.yml push run on main as gh lists it, or Unknown when the list cannot be read or may be cut off."""
    result = tools.call("gh", ["run", "list", "--repo", repo, "--workflow", WORKFLOW, "--event", "push",
                               "--branch", BRANCH, "--limit", str(RUN_LIMIT), "--json",
                               "databaseId,status,conclusion,createdAt,headSha,event,headBranch"], seconds)
    if result.returncode != 0:
        raise Unknown(f"gh run list failed: {(result.stderr.strip().splitlines() or ['no message'])[-1]}")
    try:
        runs = json.loads(result.stdout or "[]")
    except ValueError:
        raise Unknown("gh run list did not print JSON") from None
    if not isinstance(runs, list) or not all(isinstance(r, dict) for r in runs):
        raise Unknown("gh run list did not print a list of runs")
    if len(runs) >= RUN_LIMIT:
        raise Unknown(f"gh listed {RUN_LIMIT} push runs, so the history may be cut off")
    return [r for r in runs if r.get("event") == "push" and r.get("headBranch") == BRANCH
            and isinstance(r.get("headSha"), str)]


def unchecked_heads(tools, run_file, left):
    """(baseline, the push heads on the fetched origin/main with no recorded outcome after it, oldest first).

    A push head is a commit recorded `ci-pending`, the head of a ci.yml push run on main, or origin/main itself; a
    commit that is not one is covered by the first push head after it. The baseline is the oldest head with a recorded
    outcome (history before the records began is covered), or, with none recorded, the newest head whose push run is
    green. After it, a head is listed unless it has an outcome of its own: a later green head never covers it."""
    fetched = tools.call("git", ["fetch", "--quiet", "origin", BRANCH], left())
    if fetched.returncode != 0:
        raise Unknown("git fetch origin main failed")
    listed = tools.call("git", ["rev-list", "--first-parent", f"--max-count={HISTORY_LIMIT}", f"origin/{BRANCH}"],
                        left())
    history = listed.stdout.split()
    if listed.returncode != 0 or not history or not all(len(c) == 40 for c in history):
        raise Unknown("cannot read the history of origin/main")
    repo = origin(tools, left())
    runs = push_runs(tools, repo, left())
    outcomes, pendings = records(run_file)
    run_heads = {r["headSha"] for r in runs}
    heads = [c for c in history if c in run_heads or recorded(pendings, c) or c == history[0]]  # newest first
    with_outcome = [c for c in heads if recorded(outcomes, c)]
    if with_outcome:
        baseline = with_outcome[-1]
    else:
        green = {r["headSha"] for r in runs if r.get("status") == "completed" and r.get("conclusion") == "success"}
        baseline = next((c for c in heads if c in green), None)
    newer = heads[:heads.index(baseline)] if baseline else heads
    return baseline, [c for c in reversed(newer) if not recorded(outcomes, c)]


def pending_main(args, tools, clock, now):
    """--pending: report every unchecked push head's CI; exit 2 if discovery is incomplete or any head is unknown,
    else 1 if any is red, 3 if any is pending, 0 when every listed head is green (or none is listed)."""
    deadline = clock() + PENDING_SECONDS

    def left():
        remaining = deadline - clock()
        if remaining <= 0:
            raise DeadlinePassed("the deadline passed before the pushed history could be read")
        return min(CALL_SECONDS, remaining)
    try:
        baseline, heads = unchecked_heads(tools, args.pending, left)
    except Unknown as exc:
        print(f"unknown: {exc}")
        return UNKNOWN
    print(f"{len(heads)} unchecked push head(s) after {'baseline ' + baseline[:7] if baseline else 'no baseline'}")
    codes = []
    for sha in heads:
        moment = now() if now else datetime.now(timezone.utc)
        try:
            code, lines = status(tools, sha, moment, deadline, None, clock)
        except DeadlinePassed as exc:
            code, lines = UNKNOWN, [f"unknown {sha[:7]}: {exc}"]
        codes.append(code)
        print("\n".join(lines))
    for worst in (UNKNOWN, RED, PENDING):
        if worst in codes:
            return worst
    return GREEN


def main(argv=None, tools=None, clock=time.monotonic, sleep=time.sleep, now=None):
    parser = argparse.ArgumentParser(description="Report the CI result of one pushed commit.")
    parser.add_argument("ref", nargs="?", help="the commit, as a SHA or a ref such as HEAD")
    parser.add_argument("--pending", metavar="RUN_FILE",
                        help="list and check every pushed head of main with no ci-green or ci-superseded record")
    parser.add_argument("--wait", action="store_true", help="poll until the run ends or the timeout passes")
    parser.add_argument("--timeout", type=int, default=3600, help="with --wait: seconds before giving up (exit 3)")
    parser.add_argument("--log", help="with a red run: write the failed steps' log here, outside the repository")
    args = parser.parse_args(argv)
    tools = tools or Tools()
    if args.pending:
        return pending_main(args, tools, clock, now)
    if not args.ref:
        parser.error("a ref, or --pending RUN_FILE")
    started = clock()
    deadline = started + (args.timeout if args.wait else CALL_SECONDS * 4)
    last = None
    while True:
        moment = now() if now else datetime.now(timezone.utc)
        try:
            code, lines = status(tools, args.ref, moment, deadline, args.log, clock)
        except DeadlinePassed as exc:
            # The timeout ended this look: the previous look's result stands; with none, CI could not be read.
            code, lines = last if last else (UNKNOWN, [f"unknown {args.ref}: {exc}"])
            break
        last = (code, lines)
        remaining = deadline - clock()
        if code != PENDING or not args.wait or remaining <= RESERVE:
            break
        sleep(min(POLL_SECONDS, remaining - RESERVE))
    if code == PENDING and args.wait:
        lines.append(f"still pending at the {args.timeout} s timeout")
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
