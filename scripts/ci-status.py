#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Report the GitHub Actions CI result of one pushed commit, so the campaign never builds on a red `main` (D00 T03 §15).

    python scripts/ci-status.py <ref>                                # exit 0 green, 1 red, 3 pending, 2 unknown
    python scripts/ci-status.py <ref> --wait --timeout 3600          # poll every 30 s until the run ends
    python scripts/ci-status.py <ref> --log R:\\scratch\\ci-<sha>.log  # with red: the failed steps' log, last 400 lines
    python scripts/ci-status.py --pending docs/phase-runs/<run file>  # every pushed head with no recorded outcome;
                                                                     # exit 4: progress saved, run it again
    python scripts/ci-status.py --pending <run file> --ack           # the records are written: drop the checkpoint

The governing run of a commit is the `ci.yml` run with event `push` on branch `main` whose head is that commit (pull
request and manual runs never count), the newest by creation when there are several, at its latest attempt. `success`
is green; every other conclusion is red and named. No push run 10 minutes after the commit's committer date, or a `gh`
that cannot be read, is unknown. Every `gh` and `git` call has a deadline of 60 seconds or what is left of the
timeout, whichever is shorter, and none starts after it. With --wait, looks keep starting until a second before the
timeout; a look the timeout cuts short leaves the last result standing (still pending), never a guess.
"""
import argparse
from datetime import datetime, timezone
import hashlib
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


# D00 T03 §22: the unfiltered workflow-runs endpoint, read page by page to its end (the filtered search stops at 1,000
# results), with the progress of a reconciliation kept between tries in a checkpoint bound to its inputs.
CHECKPOINT = ROOT / "build" / "ci-reconcile.json"
PER_PAGE = 100
PROGRESSING = 4


def records_digest(outcomes, pendings):
    return hashlib.sha256(json.dumps([sorted(outcomes), sorted(pendings)]).encode("utf-8")).hexdigest()


def load_checkpoint(path):
    """The saved reconciliation, or None. It is a cache of reads that can always be repeated, so a damaged one is
    rebuilt rather than trusted."""
    try:
        data = json.loads(Path(path).read_bytes().decode("utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError, ValueError):
        return None  # rebuilt from GitHub and git on this try
    keys = {"inputs", "runs", "next_page", "refresh_page", "total", "results", "progress"}
    return data if isinstance(data, dict) and set(data) == keys and isinstance(data["runs"], dict) \
        and isinstance(data["results"], dict) else None


def save_checkpoint(path, cp):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(cp), encoding="utf-8")
    os.replace(temp, path)


def read_page(tools, owner_name, page, seconds):
    """(total_count, runs) of one page of the unfiltered workflow-runs endpoint, or Unknown."""
    result = tools.call("gh", ["api", "--hostname", github_origin.HOST,
                               f"repos/{owner_name}/actions/workflows/{WORKFLOW}/runs?per_page={PER_PAGE}&page={page}"],
                        seconds)
    if result.returncode != 0:
        raise Unknown(f"gh api page {page} failed: {(result.stderr.strip().splitlines() or ['no message'])[-1]}")
    try:
        data = json.loads(result.stdout)
    except ValueError:
        raise Unknown(f"gh api page {page} is not JSON") from None
    if not (isinstance(data, dict) and type(data.get("total_count")) is int and isinstance(data.get("workflow_runs"), list)
            and all(isinstance(r, dict) and r.get("id") is not None for r in data["workflow_runs"])):
        raise Unknown(f"gh api page {page} does not hold workflow runs")
    return data["total_count"], data["workflow_runs"]


def keep(cp, runs):
    for r in runs:
        cp["runs"].setdefault(str(r["id"]), {"headSha": r.get("head_sha"), "event": r.get("event"),
                                             "headBranch": r.get("head_branch"), "status": r.get("status"),
                                             "conclusion": r.get("conclusion") or "",
                                             "createdAt": r.get("created_at", "")})


def enumerate_runs(tools, repo, cp, left, save):
    """Read the workflow's runs into the checkpoint: forward to the last page, and, after the inputs changed or when
    runs arrived meanwhile, from the first page until a run already held, so nothing is read twice on an unchanged
    try and nothing new is missed. Every page is saved as it is read."""
    owner_name = repo.split("/", 1)[1]  # github.com/<owner>/<name> -> <owner>/<name>
    refreshed_at_end = False
    while True:
        if cp["refresh_page"] is not None:
            page = cp["refresh_page"]
            total, runs = read_page(tools, owner_name, page, left())
            met = any(str(r["id"]) in cp["runs"] for r in runs)
            keep(cp, runs)
            cp["total"], cp["progress"] = total, cp["progress"] + 1
            cp["refresh_page"] = None if met or len(runs) < PER_PAGE else page + 1
        elif cp["next_page"] is not None:
            page = cp["next_page"]
            total, runs = read_page(tools, owner_name, page, left())
            keep(cp, runs)
            cp["total"], cp["progress"] = total, cp["progress"] + 1
            cp["next_page"] = None if len(runs) < PER_PAGE else page + 1
        elif cp["total"] is not None and len(cp["runs"]) < cp["total"]:
            if refreshed_at_end:
                raise Unknown(f"gh api returned {len(cp['runs'])} of {cp['total']} runs, so the history may be cut off")
            cp["refresh_page"], refreshed_at_end = 1, True  # runs were created while the pages were read
            continue
        else:
            return
        save(cp)


def unchecked_heads(tools, run_file, left, cp, save):
    """(baseline, the push heads on the fetched origin/main with no recorded outcome after it, oldest first).

    A push head is a commit with a ci-pending or outcome record, the head of a ci.yml push run on main, or origin/main
    itself; a commit that is not one is covered by the first push head after it. The baseline is the oldest head with
    a recorded outcome (history before the records began is covered), or, only when no run file holds any outcome, the
    newest head whose push run is green. After it, a head is listed unless it has an outcome of its own: a later green
    head never covers it. The whole first-parent history is read (D00 T03 §20), and the runs come from the checkpoint,
    refreshed when the repository, the fetched head or the records changed since it was saved (D00 T03 §22)."""
    fetched = tools.call("git", ["fetch", "--quiet", "origin", BRANCH], left())
    if fetched.returncode != 0:
        raise Unknown("git fetch origin main failed")
    listed = tools.call("git", ["rev-list", "--first-parent", f"origin/{BRANCH}"], left())  # the whole history
    history = listed.stdout.split()
    if listed.returncode != 0 or not history or not all(len(c) == 40 for c in history):
        raise Unknown("cannot read the history of origin/main")
    # The clone must be exactly the fetched origin/main: its run files are then the records of the history checked,
    # and the head checked is the one the next row builds on. Ahead: push first; behind: fast-forward first.
    local = tools.call("git", ["rev-parse", "--verify", "HEAD^{commit}"], left())
    if local.returncode != 0 or len(local.stdout.strip()) != 40:
        raise Unknown("cannot read HEAD")
    if local.stdout.strip() != history[0]:
        ahead = tools.call("git", ["rev-list", "--count", f"origin/{BRANCH}..HEAD"], left())
        count = int(ahead.stdout) if ahead.returncode == 0 and ahead.stdout.strip().isdigit() else 0
        if count:
            raise Unknown(f"HEAD has {count} commit(s) origin/main lacks; push them, then reconcile again")
        raise Unknown("HEAD is not origin/main; fast-forward (git pull --ff-only origin main), then reconcile again")
    repo = origin(tools, left())
    outcomes, pendings = records(run_file)
    inputs = {"repo": repo, "head": history[0], "records": records_digest(outcomes, pendings)}
    if not cp:
        cp.update({"inputs": inputs, "runs": {}, "next_page": 1, "refresh_page": None, "total": None, "results": {},
                   "progress": 0})
    elif cp["inputs"] != inputs:
        if cp["inputs"].get("repo") != repo:  # another repository's runs are no use
            cp.update({"runs": {}, "next_page": 1, "refresh_page": None, "total": None, "results": {}})
        else:
            cp["refresh_page"] = 1  # keep what was read; find what is new
        cp["inputs"] = inputs
        save(cp)
    enumerate_runs(tools, repo, cp, left, save)
    runs = [r for r in cp["runs"].values() if r["event"] == "push" and r["headBranch"] == BRANCH
            and isinstance(r["headSha"], str)]
    run_heads = {r["headSha"] for r in runs}
    heads = [c for c in history if c in run_heads or recorded(pendings, c) or recorded(outcomes, c)
             or c == history[0]]  # newest first
    with_outcome = [c for c in heads if recorded(outcomes, c)]
    if outcomes:
        if not with_outcome:  # outcomes are recorded, but none is on the history of origin/main
            raise Unknown("no recorded outcome is on origin/main's history")
        baseline = with_outcome[-1]
    else:
        governing = {}  # each head's newest push run decides it, as for a single commit
        for r in runs:
            if r["headSha"] not in governing or str(r["createdAt"]) > str(governing[r["headSha"]]["createdAt"]):
                governing[r["headSha"]] = r
        green = {h for h, r in governing.items() if r["status"] == "completed" and r["conclusion"] == "success"}
        baseline = next((c for c in heads if c in green), None)
    newer = heads[:heads.index(baseline)] if baseline else heads
    return baseline, [c for c in reversed(newer) if not recorded(outcomes, c)]


def settle_head(tools, sha, stored, now, deadline, clock):
    """(code, lines, run identity, newly settled) for one head. A stored completed result already confirmed in this
    reconciliation is reused without a call; one not yet confirmed is reused after one look shows its governing run's id
    and attempt unchanged (a rerun replaces it); a pending or unknown head, or one never settled, is checked again."""
    if stored and stored["code"] in (GREEN, RED):
        if stored.get("confirmed"):
            return stored["code"], stored["lines"], stored["run"], False
        remaining = deadline - clock()
        if remaining <= 0:
            raise DeadlinePassed("the deadline passed before the stored results could be confirmed")
        run = governing_run(tools, sha, min(CALL_SECONDS, remaining), origin(tools, min(CALL_SECONDS, remaining)))
        if run and run.get("status") == "completed" and [run.get("databaseId"), run.get("attempt", 1)] == stored["run"]:
            return stored["code"], stored["lines"], stored["run"], True
    code, lines = status(tools, sha, now, deadline, None, clock)
    run = None
    if code in (GREEN, RED):
        found = re.search(r" run (\d+) attempt (\d+)", lines[0])
        run = [int(found[1]), int(found[2])] if found else None
    return code, lines, run, code in (GREEN, RED)


def pending_main(args, tools, clock, now, checkpoint):
    """--pending: report every unchecked push head's CI. Exit 2 if discovery is incomplete or any head is unknown,
    else 1 if any is red, 3 if any is pending, 0 when every listed head is green (or none is listed); exit 4 when this
    try ran out of time but saved progress (D00 T03 §22): run it again, and it continues where it stopped."""
    path = Path(checkpoint)
    if args.ack:
        path.unlink(missing_ok=True)
        print("acknowledged: the reconciliation's checkpoint is deleted")
        return GREEN
    cp = load_checkpoint(path) or {}
    before = cp.get("progress", 0) if cp else 0
    deadline = clock() + PENDING_SECONDS

    def left():
        remaining = deadline - clock()
        if remaining <= 0:
            raise DeadlinePassed("the deadline passed before the pushed history could be read")
        return min(CALL_SECONDS, remaining)

    def save(c):
        save_checkpoint(path, c)

    def out_of_time():
        if cp and cp["progress"] > before:
            save(cp)
            print(f"progressing: {cp['progress'] - before} step(s) saved this try; run again to continue")
            return PROGRESSING
        print("unknown: this try made no progress before its deadline")
        return UNKNOWN
    try:
        baseline, heads = unchecked_heads(tools, args.pending, left, cp, save)
    except DeadlinePassed:
        return out_of_time()
    except Unknown as exc:
        print(f"unknown: {exc}")
        return UNKNOWN
    report, codes = [], []
    for sha in heads:
        moment = now() if now else datetime.now(timezone.utc)
        stored = cp["results"].get(sha)
        try:
            code, lines, run, settled = settle_head(tools, sha, stored, moment, deadline, clock)
        except DeadlinePassed:
            return out_of_time()
        cp["progress"] += settled
        cp["results"][sha] = {"code": code, "lines": lines, "run": run, "confirmed": code in (GREEN, RED)}
        save(cp)
        codes.append(code)
        report += lines
    print(f"{len(heads)} unchecked push head(s) after {'baseline ' + baseline[:7] if baseline else 'no baseline'}")
    print("\n".join(report))
    for result in cp["results"].values():  # the report is complete: the next reconciliation confirms each again
        result["confirmed"] = False
    save(cp)
    for worst in (UNKNOWN, RED, PENDING):
        if worst in codes:
            return worst
    return GREEN


def main(argv=None, tools=None, clock=time.monotonic, sleep=time.sleep, now=None, checkpoint=CHECKPOINT):
    parser = argparse.ArgumentParser(description="Report the CI result of one pushed commit.")
    parser.add_argument("ref", nargs="?", help="the commit, as a SHA or a ref such as HEAD")
    parser.add_argument("--pending", metavar="RUN_FILE",
                        help="list and check every pushed head of main with no ci-green or ci-superseded record")
    parser.add_argument("--ack", action="store_true",
                        help="with --pending: the records are written, so delete the reconciliation's checkpoint")
    parser.add_argument("--wait", action="store_true", help="poll until the run ends or the timeout passes")
    parser.add_argument("--timeout", type=int, default=3600, help="with --wait: seconds before giving up (exit 3)")
    parser.add_argument("--log", help="with a red run: write the failed steps' log here, outside the repository")
    args = parser.parse_args(argv)
    tools = tools or Tools()
    if args.pending:
        return pending_main(args, tools, clock, now, checkpoint)
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
