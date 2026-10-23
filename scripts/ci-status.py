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
SAVE_SECONDS = 5  # settled heads are saved at least this often; a deadline saves on its way out


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
    keys = {"inputs", "runs", "next_page", "total", "results", "progress", "pass"}
    return data if isinstance(data, dict) and set(data) == keys and isinstance(data["runs"], dict) \
        and isinstance(data["results"], dict) else None


def save_checkpoint(path, cp):
    """Write the checkpoint temp-then-replace; a failure is Unknown, so a local write error never reads as red CI."""
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".tmp")
        temp.write_text(json.dumps(cp), encoding="utf-8")
        os.replace(temp, path)
    except OSError as exc:
        raise Unknown(f"cannot save the checkpoint {path.name}: {exc.strerror or exc}") from None


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


def read_run(tools, owner_name, run_id, seconds):
    """One workflow run, read by its id, or Unknown."""
    result = tools.call("gh", ["api", "--hostname", github_origin.HOST, f"repos/{owner_name}/actions/runs/{run_id}"],
                        seconds)
    if result.returncode != 0:
        raise Unknown(f"gh api run {run_id} failed: {(result.stderr.strip().splitlines() or ['no message'])[-1]}")
    try:
        run = json.loads(result.stdout)
    except ValueError:
        raise Unknown(f"gh api run {run_id} is not JSON") from None
    if not (isinstance(run, dict) and str(run.get("id")) == str(run_id)):
        raise Unknown(f"gh api run {run_id} is not that workflow run")
    return run


def keep(cp, runs):
    """Store runs as read, a fresher read replacing an older one (a rerun changes a run's attempt and conclusion).
    Returns how many runs were new or changed."""
    changed = 0
    for r in runs:
        entry = {"headSha": r.get("head_sha"), "event": r.get("event"), "headBranch": r.get("head_branch"),
                 "status": r.get("status"), "conclusion": r.get("conclusion") or "",
                 "createdAt": r.get("created_at", ""), "attempt": r.get("run_attempt", 1)}
        if cp["runs"].get(str(r["id"])) != entry:
            cp["runs"][str(r["id"])] = entry
            changed += 1
    return changed


class Pages:
    """One try's reads of the workflow's runs. The forward scan reads each page once, to the last page, continuing
    where an earlier try stopped. Every try reads the newest pages again until one brings nothing new or changed, so
    runs created since are found; and before a report, every run the report relies on is read again in that same try,
    so a rerun at any depth is seen (D00 T03 §22)."""

    def __init__(self, tools, repo, cp, left, save):
        self.tools, self.owner_name, self.cp, self.left, self.save = tools, repo.split("/", 1)[1], cp, left, save
        self.now, self.pages, self.last = set(), set(), None  # run ids and page numbers read in this try; last page

    def read(self, page):
        total, runs = read_page(self.tools, self.owner_name, page, self.left())
        changed = keep(self.cp, runs)
        self.now |= {str(r["id"]) for r in runs}
        self.pages.add(page)
        if len(runs) < PER_PAGE:
            self.last = page if self.last is None else min(self.last, page)
        self.cp["total"] = total
        return runs, changed

    def newest(self):
        """Read from the first page until a page brings nothing new or changed, or the pages end. A page that changed
        nothing is not progress."""
        page = 0
        while True:
            page += 1
            runs, changed = self.read(page)
            self.cp["progress"] += 1 if changed else 0
            self.save(self.cp)
            if not changed or len(runs) < PER_PAGE:
                return

    def confirm(self, needed):
        """Read again in this try every run in `needed`: page by page from the newest while the runs still missing
        outnumber the pages left, then each remaining run by its id, so a few runs deep in a long history (an old red
        head once the greens are recorded) cost one call each. These reads are not progress: they hold only for this
        try."""
        page, read = 0, False
        pages_total = -(-(self.cp["total"] or 0) // PER_PAGE)
        while not needed <= self.now:
            missing = needed - self.now
            if len(missing) <= pages_total - page or (self.last is not None and page >= self.last) \
                    or page >= pages_total:
                for run_id in sorted(missing, key=int):
                    keep(self.cp, [read_run(self.tools, self.owner_name, run_id, self.left())])
                    self.now.add(run_id)
                    read = True
                break
            page += 1
            if page not in self.pages:
                self.read(page)
                read = True
        if read:
            self.save(self.cp)

    def forward(self):
        """Continue the scan to the workflow's last page, saving every page as it is read. Runs created while the
        pages were read push older runs down a page; reading the newest pages again then finds them."""
        while self.cp["next_page"] is not None:
            page = self.cp["next_page"]
            runs, _ = self.read(page)
            self.cp["next_page"] = None if len(runs) < PER_PAGE else page + 1
            self.cp["progress"] += 1
            self.save(self.cp)
        if len(self.cp["runs"]) < self.cp["total"]:
            self.newest()
        if len(self.cp["runs"]) < self.cp["total"]:
            raise Unknown(f"gh api returned {len(self.cp['runs'])} of {self.cp['total']} runs, so the history may be "
                          f"cut off")


def unchecked_heads(tools, run_file, left, cp, save):
    """(the try's reader, and a function returning the baseline, the push heads on the fetched origin/main with no
    recorded outcome after it (oldest first), each listed head's governing run id, and a first-run baseline's run id,
    as the runs read so far show them).

    A push head is a commit with a ci-pending or outcome record, the head of a ci.yml push run on main, or origin/main
    itself; a commit that is not one is covered by the first push head after it. The baseline is the oldest head with
    a recorded outcome (history before the records began is covered), or, only when no run file holds any outcome, the
    newest head whose governing push run is green. After it, a head is listed unless it has an outcome of its own: a
    later green head never covers it. The whole first-parent history is read (D00 T03 §20); the runs come from the
    checkpoint (D00 T03 §22)."""
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
    if not cp or cp["inputs"].get("repo") != repo:  # another repository's runs are no use
        cp.clear()
        cp.update({"inputs": inputs, "runs": {}, "next_page": 1, "total": None, "results": {}, "progress": 0,
                   "pass": None})
    cp["inputs"] = inputs
    if cp["pass"] is None:  # a new reconciliation: the heads it has settled, so a later try goes on past them
        cp["pass"] = {"checked": []}
    pages = Pages(tools, repo, cp, left, save)
    if cp["runs"]:  # runs held from an earlier try: find what is new before going on
        pages.newest()
    pages.forward()

    def listing():
        governing = {}  # each head's newest push run decides it, as for a single commit
        for i, r in cp["runs"].items():
            if r["event"] == "push" and r["headBranch"] == BRANCH and isinstance(r["headSha"], str) and (
                    r["headSha"] not in governing or str(r["createdAt"]) > str(governing[r["headSha"]][1]["createdAt"])):
                governing[r["headSha"]] = (i, r)
        heads = [c for c in history if c in governing or recorded(pendings, c) or recorded(outcomes, c)
                 or c == history[0]]  # newest first
        base_run = None
        if outcomes:
            with_outcome = [c for c in heads if recorded(outcomes, c)]
            if not with_outcome:  # outcomes are recorded, but none is on the history of origin/main
                raise Unknown("no recorded outcome is on origin/main's history")
            baseline = with_outcome[-1]
        else:
            baseline = next((c for c in heads if c in governing and governing[c][1]["status"] == "completed"
                             and governing[c][1]["conclusion"] == "success"), None)
            base_run = governing[baseline][0] if baseline else None  # the report rests on it as on a listed head
        newer = heads[:heads.index(baseline)] if baseline else heads
        listed = [c for c in reversed(newer) if not recorded(outcomes, c)]
        return baseline, listed, {c: governing[c][0] for c in listed if c in governing}, base_run
    return pages, listing


def current(stored, run_id, runs):
    """Whether a stored completed result still holds: the head's governing run, as last read, is the run it was
    settled on, on the same attempt (a page read before the run finished still names that attempt, and an attempt
    that finished never runs again)."""
    return bool(stored and stored["code"] in (GREEN, RED) and stored.get("run") and run_id
                and [int(run_id), runs[run_id]["attempt"]] == stored["run"])


def look_up(tools, sha, now, deadline, clock):
    """(code, lines, run identity) for one head, from its governing run as GitHub reports it now."""
    code, lines = status(tools, sha, now, deadline, None, clock)
    run = None
    if code in (GREEN, RED):
        found = re.search(r" run (\d+) attempt (\d+)", lines[0])
        run = [int(found[1]), int(found[2])] if found else None
    return code, lines, run


def pending_main(args, tools, clock, now, checkpoint):
    """--pending: report every unchecked push head's CI. Exit 2 if discovery is incomplete, any head is unknown or the
    checkpoint cannot be kept, else 1 if any is red, 3 if any is pending, 0 when every listed head is green (or none is
    listed); exit 4 when this try ran out of time but saved progress (D00 T03 §22): run it again, and it continues
    where it stopped."""
    try:
        return reconcile(args, tools, clock, now, checkpoint)
    except Unknown as exc:
        print(f"unknown: {exc}")
        return UNKNOWN


def reconcile(args, tools, clock, now, checkpoint):
    path = Path(checkpoint)
    if args.ack:
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            raise Unknown(f"cannot delete the checkpoint {path.name}: {exc.strerror or exc}") from None
        print("acknowledged: the reconciliation's checkpoint is deleted")
        return GREEN
    cp = load_checkpoint(path) or {}
    before = cp.get("progress", 0)
    deadline = clock() + PENDING_SECONDS

    def left():
        remaining = deadline - clock()
        if remaining <= 0:
            raise DeadlinePassed("the deadline passed before the pushed history could be read")
        return min(CALL_SECONDS, remaining)

    def save(c):
        save_checkpoint(path, c)

    def moment():
        return now() if now else datetime.now(timezone.utc)

    looked = set()  # heads looked up in this try: their results are as current as a read in this try
    confirming, listing, pages = False, None, None

    def settle(sha):
        code, lines, run = look_up(tools, sha, moment(), deadline, clock)
        cp["results"][sha] = {"code": code, "lines": lines, "run": run}
        looked.add(sha)
        if run and str(run[0]) in cp["runs"]:  # the page copy takes the attempt read now; a later page read wins
            cp["runs"][str(run[0])]["attempt"] = run[1]

    def confirmed():
        """Lines for the heads whose green rests on reads made in this try: what the campaign may record now, so a
        backlog whose reads do not fit in one try still finishes. Once any outcome is recorded the baseline is the
        oldest recorded head, so a record for a later head never covers an earlier one; with none recorded yet, the
        first record would become that baseline, so the first-run baseline itself comes first, and only when it too
        was read green in this try."""
        if listing is None:
            return []
        baseline, listed, runs_of, base_run = listing()
        lines = []
        if base_run:
            if base_run not in pages.now:
                return []
            run = cp["runs"][base_run]
            lines.append(f"green {baseline[:7]} run {base_run} attempt {run['attempt']}")
        for s in listed:
            result = cp["results"].get(s)
            if result and result["code"] == GREEN and current(result, runs_of.get(s), cp["runs"]) \
                    and (s in looked or runs_of[s] in pages.now):
                lines += result["lines"]
        return lines

    try:
        pages, listing = unchecked_heads(tools, args.pending, left, cp, save)
        baseline, heads, runs_of, base_run = listing()
        # Each head is settled once in a pass, so a try goes on past the heads an earlier try reached, and every head
        # settled is progress. A stored result reused on a run read in an earlier try is confirmed below.
        checked, saved = cp["pass"]["checked"], clock()
        while True:
            for sha in [s for s in heads if s not in checked]:
                if not current(cp["results"].get(sha), runs_of.get(sha), cp["runs"]):
                    settle(sha)
                checked.append(sha)
                cp["progress"] += 1
                if clock() - saved >= SAVE_SECONDS:  # the whole checkpoint is written, so not after every head
                    save(cp)
                    saved = clock()
            # What the report rests on is read again in this try, unless this try looked it up: every green result's
            # run (a green is never reported on an older read), a first-run baseline's, and the newest head's, whose
            # result decides what the campaign does. An earlier red may rest on an earlier try's read: reporting it
            # red errs toward caution, and the campaign supersedes it once the newest head settles. A rerun since
            # changes a result and a changed baseline changes the heads listed; either is settled again first.
            relied = {runs_of[s] for s in heads if s in runs_of and s not in looked and (
                cp["results"][s]["code"] == GREEN or (s == heads[-1] and cp["results"][s]["code"] == RED))} \
                | ({base_run} if base_run else set())
            confirming = True
            pages.confirm(relied)
            confirming = False
            latest = listing()
            stale = [s for s in latest[1] if s in checked and s in latest[2] and cp["results"][s]["code"] in (GREEN, RED)
                     and not current(cp["results"][s], latest[2][s], cp["runs"])]
            if latest[:2] == (baseline, heads) and not stale:
                break
            baseline, heads, runs_of, base_run = latest
            for s in stale:
                checked.remove(s)
    except DeadlinePassed:
        ready = confirmed()
        if cp and (cp["progress"] > before or ready):
            save(cp)
            print(f"progressing: {cp['progress'] - before} step(s) saved this try; run again to continue")
            if ready:  # record these now: the next try then rests on fewer runs
                print("\n".join(f"confirmed {line}" for line in ready))
            return PROGRESSING
        if confirming:  # a report rests only on reads made in its own try, and these do not fit in one
            print("unknown: the runs the report rests on cannot all be read again within one try")
        else:
            print("unknown: this try made no progress before its deadline")
        return UNKNOWN
    # Heads still pending or unknown are looked up again while the try has time; a deadline here reports them as they
    # stand (a pending head is never reported green).
    for sha in [s for s in heads if cp["results"][s]["code"] in (PENDING, UNKNOWN) and s not in looked]:
        try:
            settle(sha)
        except DeadlinePassed:
            break
    codes = [cp["results"][s]["code"] for s in heads]
    cp["pass"] = None  # reported: the next reconciliation settles every head again
    save(cp)
    print(f"{len(heads)} unchecked push head(s) after {'baseline ' + baseline[:7] if baseline else 'no baseline'}")
    print("\n".join(line for s in heads for line in cp["results"][s]["lines"]))
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
