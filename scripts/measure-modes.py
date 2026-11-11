#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Measure the ways of working: build the same TODO sections with each arm, gate and review every result blind, and
fix it with its own arm until a review approves it (D00 T03 §36; owner decision 30: the lead model is chosen by
measurement, never by opinion).

    python scripts/measure-modes.py run --section "D00 T03 §32" --section "D00 T03 §29" --section "D02 T01 §30"
    python scripts/measure-modes.py run --section "D00 T03 §32" --base 402351a --work <folder> --budget 40
    python scripts/measure-modes.py clean --work <folder>

`run` clones the repository once per arm and section into the work folder (default: `measure-modes` under the scratch
folder `OFFICE_SCRATCH` names, else the system temporary folder), at the base commit, with no remote and under folder
names (`run-1`, `run-2`, ...) that do not reveal the arm; only `results.json` maps a run to its arm. Each section is
resolved with `scripts/todo-graph.py resolve` in a clone at the base, so every arm gets the section as that commit has
it. Each arm then runs as a headless Claude Code session (`claude -p`) with the task on standard input, a spending
limit and a time limit, at most `--parallel` at a time, each in its own process tree (`scripts/lib/process_tree.py`),
which is stopped when it passes the time limit or its output passes 50 MB and always when it ends.

The harness, never the measured session, then judges the result: it records the clone's `HEAD` as the candidate, fails
the `clean-tree` gate when the session left uncommitted or untracked files (it never commits for the arm), runs
`validate`, `plan --check` and `run-tests.py`, and has the pinned reviewer review the range blind through the clone's
own `scripts/review-dispatch.py` with one fixed prompt that names only the range and the section. A pass counts as a
review only when the dispatcher exits 0 with a reviewer and a `HIGHEST:` line; anything else is `unreviewed`, is tried
once more and is never approval. A result is approved when every gate passes and the review of that same candidate
has no `P1` or `P2`; until then the same arm fixes it in the same clone (the review and the failed gates on standard
input), up to `--fix-rounds` rounds.

`results.json` is written after every stage through a temporary file and `os.replace`, with the measurement's
identity. A second `run` on the same work folder resumes stage by stage: a session that recorded its exit is never run
again, a stage that started and recorded nothing runs again from the clone's last recorded candidate, and a `run`
whose identity differs is refused. `run` holds `measure.lock` in the work folder for its whole life; `clean` refuses
while the lock is held and removes only the clones `results.json` lists, keeping the results and the logs.

Exit 0 when every run reached an end, 1 when a run could not (a clone or a session could not start), 2 on a refusal
(an argument, a section that is not ready, another run holding the folder, an identity mismatch), 130 when interrupted
(every running tree is stopped and the interrupted stages run again on the next call).
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_EXCEPTION
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import process_tree

SCHEMA = 1
MAX_OUTPUT_BYTES = 50 * 1024 * 1024  # a session's output files together; past this the session is stopped
REVIEW_SECONDS = 2400  # the dispatcher's own reviewer timeout is 1800 s; this bounds the dispatcher around it
GIT_SECONDS = 600
TAIL_LINES = 3
APPROVING = ("none", "P3")  # a review whose worst finding is one of these approves, as the stamp's severity stop does
HIGHEST = re.compile(r"^HIGHEST:\s*(P[123]|none)\s*$", re.MULTILINE | re.IGNORECASE)
OVERALL = re.compile(r"^OVERALL:\s*(approve|needs-attention)\s*$", re.MULTILINE)
FINDING = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+\**\s*(P[123])\b")  # a numbered or bulleted finding opening with its tag
PURPOSE = "Implements the TODO section named here."  # the one fixed purpose every blind review is given


@dataclass(frozen=True)
class Arm:
    name: str
    model: str  # a Claude Code model alias, so the latest model of the family is measured
    subagents: bool  # whether the session may start the read-only agents of .claude/agents
    instruction: str  # added to the task after the section text


LEAD = ("Work as this repository's lead (AGENTS.md, Subagents): build everything yourself. The read-only Sonnet agents "
        "in .claude/agents may find facts and run suites for you; no agent writes.")
# The packet-routing arm measured on 2026-11-10 (`orchestrated`) lost on cost and quality and is not kept, and since
# the owner made the main session the writer (decision 40) every arm works alone; the arms differ in the model.
ARMS = (
    Arm("opus-alone", "opus", True, LEAD),
    Arm("fable-alone", "fable", True, LEAD),
)

TASK = """You are building one TODO section of this repository in a measurement. Process it with the \
process-todo-section skill (.claude/skills/process-todo-section/SKILL.md): validate it against the repository, correct \
the plan where it is wrong, build it, run its Test checkpoint and commit the work on main. This run is measured, so \
skip the plan review (step 3a), and do not run review-todo-section, a stamp, a push or any campaign step: there is no \
remote, and the harness gates and reviews what you commit. Leave nothing uncommitted.

Section {ref}, {title} ({path}):

{body}
"""

FIX = """The harness gated and reviewed your work on TODO section {ref} (commits {base}..{candidate}) and it is not \
approved yet. Verify each finding and each failed gate below against the code, fix the real ones at their owning layer \
with a test, and commit on main. The same rules hold: no plan review, review, stamp, push or campaign step, and leave \
nothing uncommitted.

Failed gates:
{gates}

Review ({review_path}):
{review}
"""


class Refused(Exception):
    """A refusal: exit 2 with the message."""


class Cancelled(Exception):
    """The measurement was interrupted; the stage that was running records nothing and runs again on resume."""


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_arms(rows):
    """The arm table, checked: at least one arm, names unique and non-empty, every field of its type."""
    arms = tuple(rows)
    if not arms:
        raise Refused("the arm table is empty")
    seen = set()
    for arm in arms:
        if not isinstance(arm, Arm) or not arm.name or not arm.model or not isinstance(arm.subagents, bool) \
                or not isinstance(arm.instruction, str):
            raise Refused(f"arm {arm!r} is not a complete row (name, model, subagents, instruction)")
        if arm.name in seen:
            raise Refused(f"the arm table names {arm.name} twice")
        seen.add(arm.name)
    return arms


def scratch():
    return Path(os.environ.get("OFFICE_SCRATCH") or tempfile.gettempdir())


def atomic_json(path, data):
    """Write `data` to `path` through a temporary file in the same folder and os.replace, then read it back."""
    path = Path(path)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, indent=1, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    json.loads(path.read_text(encoding="utf-8"))  # read back: a file that does not parse is a failed write


class Lock:
    """`measure.lock` in the work folder, held for the life of one `run`: an exclusive lock on the open file, so it is
    released by the system when the process dies and a second run or a `clean` sees it while it is held."""

    def __init__(self, work):
        self.path = Path(work) / "measure.lock"
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = open(self.path, "a+b")
        try:
            if os.name == "nt":
                import msvcrt
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            handle.close()
            raise Refused(f"another measurement holds {self.path}; wait for it to end") from None
        self.handle = handle
        return self

    def __exit__(self, *exc):
        if self.handle is not None:
            try:
                if os.name == "nt":
                    import msvcrt
                    self.handle.seek(0)
                    msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            finally:
                self.handle.close()
                self.handle = None
        return False


def git(cwd, *args, check=True):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=GIT_SECONDS)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {cwd}: {result.stderr.strip()[:500]}")
    return result.stdout.strip()


def tail(path, lines=TAIL_LINES):
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return [line for line in text.splitlines() if line.strip()][-lines:]


def remove_tree(path):
    """Remove a folder and everything in it. Git writes its object files read-only, which Windows refuses to delete,
    so a refused entry is made writable and removed again; anything still refused raises."""
    def writable(function, name, _exc):
        os.chmod(name, 0o700)
        function(name)

    if Path(path).exists():
        shutil.rmtree(path, onexc=writable)


def clone(repo, base, dest, owned=False):
    """A clone of `repo` at `base` on a `main` branch, with no remote and this repository's hooks enabled. An existing
    `dest` is removed only when `owned` (the results file lists it as this measurement's); otherwise it is refused, so
    a folder the measurement did not make is never deleted."""
    if dest.exists():
        if not owned:
            raise Refused(f"{dest} already exists and is not a clone this measurement recorded; move it or choose "
                          f"another --work folder")
        remove_tree(dest)
    subprocess.run(["git", "clone", "-q", "--no-checkout", "--no-hardlinks", str(repo), str(dest)], check=True,
                   capture_output=True, timeout=GIT_SECONDS)
    git(dest, "checkout", "-q", "-B", "main", base)
    git(dest, "remote", "remove", "origin")
    git(dest, "config", "core.hooksPath", "scripts/hooks")


def resolve(clone_dir, ref):
    """The section as the clone's commit has it: (task text, title, path); Refused when it is not open and ready."""
    # Decoded as UTF-8, so the child is asked for UTF-8: without it Python writes in the console's code page.
    result = subprocess.run([sys.executable, "scripts/todo-graph.py", "resolve", ref], cwd=clone_dir,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=GIT_SECONDS,
                            env={**os.environ, "PYTHONUTF8": "1"})
    why = {1: "no such section", 2: "not a section reference", 3: "already stamped",
           4: "waiting on a dependency, its file's status or a Need"}
    if result.returncode != 0:
        raise Refused(f"{ref}: {why.get(result.returncode, f'resolve exited {result.returncode}')}")
    try:
        found = json.loads(result.stdout)
        return TASK.format(ref=found["skill_arg"], title=found["title"], path=found["path"], body=found["body"])
    except (ValueError, KeyError) as exc:
        raise Refused(f"{ref}: resolve printed no section ({exc})") from None


def usage(reply):
    """The per-model token and cost figures of a `claude -p --output-format json` reply, subagents included."""
    models = {}
    for model, figures in (reply.get("modelUsage") or {}).items():
        models[model] = {key: figures.get(key) for key in ("inputTokens", "outputTokens", "cacheReadInputTokens",
                                                           "cacheCreationInputTokens", "costUSD")}
    return models


def parse_reply(path):
    """The figures of a session's JSON reply, or an `error` naming why there are none."""
    try:
        reply = json.loads(Path(path).read_text(encoding="utf-8", errors="replace"))
        if not isinstance(reply, dict):
            raise ValueError("not an object")
    except (OSError, ValueError) as exc:
        return {"cost_usd": None, "error": f"no JSON reply ({exc})"}
    return {"cost_usd": reply.get("total_cost_usd"), "turns": reply.get("num_turns"),
            "duration_ms": reply.get("duration_ms"), "is_error": reply.get("is_error"),
            "subtype": reply.get("subtype"), "models": usage(reply)}


def parse_review(exit_code, stopped, output_path):
    """A dispatcher's outcome as a review, or as `unreviewed` with the reason. Counts are of the numbered findings
    by their severity tag; `highest` is the reply's own `HIGHEST:` line."""
    if stopped:
        return {"reviewed": False, "reason": f"the dispatcher was stopped ({stopped})"}
    try:
        data = json.loads(Path(output_path).read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return {"reviewed": False, "reason": f"the dispatcher exited {exit_code} with no JSON result"}
    if not isinstance(data, dict):
        return {"reviewed": False, "reason": "the dispatcher's result is not an object"}
    if exit_code != 0 or not data.get("reviewer"):
        why = data.get("failover") or data.get("error") or "no reviewer"
        return {"reviewed": False, "reason": f"the dispatcher exited {exit_code}: {why}"}
    text = data.get("review") or ""
    found = HIGHEST.findall(text)
    if not found:
        return {"reviewed": False, "reason": "the reply has no HIGHEST line"}
    counts = {"P1": 0, "P2": 0, "P3": 0}
    for line in text.splitlines():
        tag = FINDING.match(line)
        if tag:
            counts[tag.group(1)] += 1
    overall = OVERALL.findall(text)
    highest = "none" if found[-1].lower() == "none" else found[-1].upper()
    return {"reviewed": True, "reviewer": data.get("reviewer"), "highest": highest, "p1": counts["P1"],
            "p2": counts["P2"], "p3": counts["P3"], "overall": overall[-1] if overall else None}


class Measurement:
    def __init__(self, args, arms, repo):
        self.args = args
        self.arms = {arm.name: arm for arm in arms}
        self.repo = Path(repo)
        self.work = Path(args.work)
        self.logs = self.work / "logs"
        self.results_path = self.work / "results.json"
        self.lock = threading.Lock()
        self.cancel = threading.Event()
        self.claude = shutil.which("claude")
        self.doc = None

    # Identity and the results file

    def identity(self, base):
        return {"base": base, "sections": list(self.args.section), "arms": [asdict(a) for a in self.arms.values()],
                "budget": self.args.budget, "minutes": self.args.minutes, "gate_minutes": self.args.gate_minutes,
                "fix_rounds": self.args.fix_rounds,
                # Concurrency is a condition of the measurement: sessions side by side contend for the PC, which
                # changes wall times and can change what fits in the time limit.
                "parallel": self.args.parallel}

    def save(self):
        with self.lock:
            atomic_json(self.results_path, self.doc)

    def open(self):
        """Load or create the results file. A new measurement resolves every section in a base clone first, so a
        section that is not ready is refused before any clone or session is made for the runs."""
        base = git(self.repo, "rev-parse", "--verify", f"{self.args.base}^{{commit}}")
        identity = self.identity(base)
        if self.results_path.is_file():
            try:
                doc = json.loads(self.results_path.read_text(encoding="utf-8"))
            except ValueError as exc:
                raise Refused(f"{self.results_path} cannot be read ({exc}); move it aside to start again") from None
            if doc.get("identity") != identity:
                differs = sorted(k for k in identity if (doc.get("identity") or {}).get(k) != identity[k])
                raise Refused(f"{self.results_path} is another measurement (differs in {', '.join(differs)}); use "
                              f"another --work folder or clean this one")
            self.doc = doc
            return
        pairs = [(ref, arm) for ref in self.args.section for arm in self.arms]
        taken = [f"run-{n}" for n in range(1, len(pairs) + 1) if (self.work / f"run-{n}").exists()]
        if taken:
            raise Refused(f"{self.work} already holds {', '.join(taken)}, which no results file records; move them or "
                          f"choose another --work folder")
        self.work.mkdir(parents=True, exist_ok=True)
        probe = Path(tempfile.mkdtemp(prefix="base-", dir=self.work))  # a fresh name, so it can be no one else's
        try:
            clone(self.repo, base, probe, owned=True)
            tasks = {ref: resolve(probe, ref) for ref in self.args.section}
        finally:
            remove_tree(probe)
        secrets.SystemRandom().shuffle(pairs)  # run numbers in a random order, so a number says nothing of its arm
        runs = {f"run-{n}": {"section": ref, "arm": arm, "clone": f"run-{n}", "stages": [], "end": None}
                for n, (ref, arm) in enumerate(pairs, 1)}
        self.doc = {"schema": SCHEMA, "identity": identity, "created": utc(), "tasks": tasks, "runs": runs,
                    "clones": sorted(r["clone"] for r in runs.values())}
        self.save()

    # One run, stage by stage

    def session(self, name, run, stage, stdin_text):
        """Run the arm's headless session for `stage` in the run's clone and record its figures."""
        arm = self.arms[run["arm"]]
        number = len(run["stages"]) - 1  # the stage is already in the record
        logs = self.logs / name
        logs.mkdir(parents=True, exist_ok=True)
        stdin_path = logs / f"stage-{number}.task.txt"
        stdin_path.write_text(stdin_text, encoding="utf-8", newline="\n")
        out, err = logs / f"stage-{number}.reply.json", logs / f"stage-{number}.err.txt"
        argv = [self.claude, "-p", "--model", arm.model, "--output-format", "json", "--max-budget-usd",
                str(self.args.budget), "--permission-mode", "bypassPermissions", "--no-session-persistence"]
        if not arm.subagents:
            argv += ["--disallowedTools", "Agent"]
        outcome = process_tree.run(argv, cwd=self.work / run["clone"], stdin_path=stdin_path, stdout_path=out,
                                   stderr_path=err, timeout=self.args.minutes * 60, max_bytes=MAX_OUTPUT_BYTES,
                                   cancel=self.cancel)
        if outcome.stopped == "cancelled":
            raise Cancelled()
        stage["session"] = {"exit": outcome.exit, "stopped": outcome.stopped, "wall_seconds": outcome.seconds,
                            "strays_stopped": outcome.strays, **parse_reply(out)}

    def bind(self, run, stage):
        """Record the candidate the gates and the review judge, and what the run has changed since the base."""
        clone_dir = self.work / run["clone"]
        base = self.doc["identity"]["base"]
        stage["candidate"] = git(clone_dir, "rev-parse", "HEAD")
        stage["commits"] = int(git(clone_dir, "rev-list", "--count", f"{base}..HEAD") or 0)
        stage["shortstat"] = git(clone_dir, "diff", "--shortstat", base, "HEAD")
        left = git(clone_dir, "status", "--porcelain", "--untracked-files=all")
        stage["uncommitted"] = len(left.splitlines()) if left else 0

    def gates(self, name, run, stage):
        clone_dir = self.work / run["clone"]
        number = len(run["stages"]) - 1
        results = {"clean-tree": {"exit": 0 if stage["uncommitted"] == 0 else 1,
                                  "tail": [] if stage["uncommitted"] == 0 else
                                  [f"{stage['uncommitted']} uncommitted or untracked paths left by the session"]}}
        for gate, argv in (("validate", ["scripts/todo-graph.py", "validate"]),
                           ("plan-check", ["scripts/todo-graph.py", "plan", "--check"]),
                           ("tests", ["scripts/run-tests.py"])):
            log = self.logs / name / f"stage-{number}.{gate}.log"
            outcome = process_tree.run([sys.executable, *argv], cwd=clone_dir, stdout_path=log,
                                       stderr_path=log.with_suffix(".err.log"), timeout=self.args.gate_minutes * 60,
                                       max_bytes=MAX_OUTPUT_BYTES, cancel=self.cancel)
            if outcome.stopped == "cancelled":
                raise Cancelled()
            results[gate] = {"exit": outcome.exit, "stopped": outcome.stopped, "seconds": outcome.seconds,
                             "tail": tail(log) + tail(log.with_suffix(".err.log"))}
        stage["gates"] = results

    def review(self, name, run, stage):
        """The blind review of the whole range, tried twice before it is recorded as unreviewed."""
        clone_dir = self.work / run["clone"]
        number = len(run["stages"]) - 1
        base = self.doc["identity"]["base"]
        prompt = self.logs / name / f"stage-{number}.review-prompt.md"
        attempts = []
        for attempt in (1, 2):
            built = process_tree.run([sys.executable, "scripts/review-prompt.py", "--kind", "round", "--candidate",
                                      stage["candidate"], "--base", base, "--ref", run["section"], "--purpose",
                                      PURPOSE, "--out", str(prompt)], cwd=clone_dir, timeout=GIT_SECONDS,
                                     stdout_path=prompt.with_suffix(".out.txt"),
                                     stderr_path=prompt.with_suffix(".err.txt"), cancel=self.cancel)
            if built.stopped == "cancelled":
                raise Cancelled()
            if built.exit != 0 or not prompt.is_file():
                attempts.append({"reviewed": False, "reason": f"review-prompt.py exited {built.exit} "
                                 f"({' '.join(tail(prompt.with_suffix('.err.txt'), 1))})"})
                continue
            out = self.logs / name / f"stage-{number}.review-{attempt}.json"
            outcome = process_tree.run([sys.executable, "scripts/review-dispatch.py", "--writer", "claude", "--prompt",
                                        str(prompt), "--kind", "round", "--candidate", stage["candidate"]],
                                       cwd=clone_dir, stdout_path=out, stderr_path=out.with_suffix(".err.txt"),
                                       timeout=REVIEW_SECONDS, max_bytes=MAX_OUTPUT_BYTES, cancel=self.cancel)
            if outcome.stopped == "cancelled":
                raise Cancelled()
            verdict = parse_review(outcome.exit, outcome.stopped, out)
            verdict["file"] = str(out)
            attempts.append(verdict)
            if verdict["reviewed"]:
                break
        stage["review"] = {**attempts[-1], "attempts": len(attempts)}

    @staticmethod
    def approved(stage):
        gates_pass = all(g["exit"] == 0 and not g.get("stopped") for g in stage["gates"].values())
        review = stage["review"]
        return gates_pass and review["reviewed"] and review["highest"] in APPROVING

    def fix_text(self, run, stage):
        failed = [f"- {gate}: exit {g['exit']}{', stopped (' + g['stopped'] + ')' if g.get('stopped') else ''}; "
                  + " | ".join(g["tail"]) for gate, g in stage["gates"].items()
                  if g["exit"] != 0 or g.get("stopped")]
        review = stage["review"]
        if review["reviewed"]:
            try:
                text = json.loads(Path(review["file"]).read_text(encoding="utf-8"))["review"]
            except (OSError, ValueError, KeyError):
                text = "(the review file could not be read)"
        else:
            text = f"(no review: {review['reason']})"
        return FIX.format(ref=run["section"], base=self.doc["identity"]["base"][:12], candidate=stage["candidate"][:12],
                          gates="\n".join(failed) or "(none)", review_path=review.get("file", "none"), review=text)

    def reset(self, run):
        """Put the clone back at its last recorded candidate (the base before the first), so a stage that started and
        recorded nothing runs again from the tree the record describes."""
        clone_dir = self.work / run["clone"]
        done = [s for s in run["stages"] if s.get("candidate")]
        target = done[-1]["candidate"] if done else self.doc["identity"]["base"]
        if not (clone_dir / ".git").exists():
            clone(self.repo, self.doc["identity"]["base"], clone_dir, owned=True)  # listed in the results file
        # Discard what the interrupted session left first: a checkout refuses to overwrite local edits to a file that
        # differs between HEAD and the target, which would make every resume fail at the same point.
        git(clone_dir, "reset", "-q", "--hard")
        git(clone_dir, "clean", "-q", "-fdx")
        git(clone_dir, "checkout", "-q", "-f", "-B", "main", target)
        git(clone_dir, "reset", "-q", "--hard", target)

    def advance(self, name):
        """Take one run from wherever its record stops to its end."""
        run = self.doc["runs"][name]
        while run["end"] is None:
            self.check_cancel()
            stage = run["stages"][-1] if run["stages"] else None
            if stage is None:
                stage = {"kind": "build", "started": utc()}
                self.start_stage(run, stage)
                self.save()
            if "session" not in stage:
                self.reset(run)
                stdin_text = self.doc["tasks"][run["section"]] + "\n" + self.arms[run["arm"]].instruction + "\n" \
                    if stage["kind"] == "build" else stage["task"]
                self.session(name, run, stage, stdin_text)
                self.save()
            if "candidate" not in stage:
                self.bind(run, stage)
                self.save()
            if "gates" not in stage:
                self.gates(name, run, stage)
                self.save()
            if "review" not in stage:
                self.review(name, run, stage)
                self.save()
            if self.approved(stage):
                run["end"] = "approved"
            elif not stage["review"]["reviewed"] and self.gates_pass(stage):
                run["end"] = "unreviewed"  # nothing to fix and no verdict: never counted as approval
            elif len(run["stages"]) - 1 >= self.args.fix_rounds:
                run["end"] = "fix-rounds-exhausted"
            else:
                fix = {"kind": "fix", "started": utc(), "task": self.fix_text(run, stage)}
                self.start_stage(run, fix)
            self.save()

    @staticmethod
    def gates_pass(stage):
        return all(g["exit"] == 0 and not g.get("stopped") for g in stage["gates"].values())

    @staticmethod
    def start_stage(run, stage):
        run["stages"].append(stage)

    def check_cancel(self):
        if self.cancel.is_set():
            raise Cancelled()

    def go(self):
        if not self.claude:
            raise Refused("claude is not on PATH")
        pending = [name for name, run in self.doc["runs"].items() if run["end"] is None]
        failed = []
        pool = ThreadPoolExecutor(max_workers=self.args.parallel)
        futures = {pool.submit(self.advance, name): name for name in pending}
        try:
            while True:
                done, waiting = wait(futures, timeout=0.5, return_when=FIRST_EXCEPTION)
                for future in done:
                    error = future.exception()
                    if error is not None and not isinstance(error, Cancelled):
                        failed.append(f"{futures[future]}: {error}")
                if not waiting:
                    break
                futures = {f: n for f, n in futures.items() if f in waiting}
        except KeyboardInterrupt:
            self.cancel.set()  # each running tree is stopped by its own poll; the stage records nothing
            pool.shutdown(wait=True, cancel_futures=True)
            raise
        pool.shutdown(wait=True)
        if self.cancel.is_set():
            raise KeyboardInterrupt  # a stage was cancelled from inside; the record is saved and resumes
        for line in failed:
            print(f"measure-modes: {line}", file=sys.stderr)
        return 1 if failed else 0


# The rule (D00 T03 §37; owner decisions 30 and 36): the cost to reach an approved review decides.

VERDICT = ROOT / ".conclave" / "operating-mode.json"
RECORDS = ROOT / "docs" / "reviews"
MIN_SECTIONS = 3
REMEASURE_STAMPS = 300


REQUIRED_GATES = ("clean-tree", "validate", "plan-check", "tests")  # every gate §36 runs; a missing one never passes


def _approved_old(stage):
    """A 2026-11-10 stage (the build or a fix round): reviewed with no P1 or P2, and each of the three gates that
    measurement ran present and 0 (it kept the clean tree as the run's `uncommitted` count instead)."""
    review = stage.get("review") or {}
    gates = stage.get("gates") or {}
    exits = {name: g["exit"] if isinstance(g, dict) else g for name, g in gates.items()}
    return review.get("exit") == 0 and review.get("highest") in APPROVING \
        and set(REQUIRED_GATES[1:]) <= set(exits) and all(code == 0 for code in exits.values())


def _models(sessions):
    """Cost per full model name over the sessions' `modelUsage`, subagents included."""
    costs = {}
    for usage in sessions:
        for model, figures in (usage or {}).items():
            costs[model] = costs.get(model, 0.0) + float((figures or {}).get("costUSD") or 0)
    return costs


def normalise(doc):
    """One row per run, from either results layout: §36's (`stages`) or the 2026-11-10 measurement's (a run's build
    and its `fix_rounds`). Refused when a run is unfinished or its cost or review evidence is missing."""
    rows = []
    for name, run in (doc.get("runs") or {}).items():
        if "stages" in run:
            stages = run["stages"]
            if run.get("end") is None or not stages:
                raise Refused(f"{name} has not ended; finish the measurement before deciding")
            sessions = [s.get("session") or {} for s in stages]
            if any(s.get("cost_usd") is None for s in sessions) or any("review" not in s for s in stages):
                raise Refused(f"{name} lacks the cost or the review of a stage")
            last = stages[-1]
            # Approval is re-read from the last stage, not trusted from `end`: a reviewed candidate with no P1 or P2
            # and every gate passing, clean-tree included (the same test as Measurement.approved).
            earned = run["end"] == "approved" and set(REQUIRED_GATES) <= set(last.get("gates") or {}) \
                and Measurement.gates_pass(last) \
                and last["review"].get("reviewed") is True and last["review"].get("highest") in APPROVING
            rows.append({"run": name, "arm": run["arm"], "section": run["section"],
                         "end": "approved" if earned else (run["end"] if run["end"] != "approved" else "not-earned"),
                         "cost": sum(s["cost_usd"] for s in sessions),
                         "reviews": sum(1 for s in stages if s["review"].get("reviewed")),
                         "wall": sum(s.get("wall_seconds") or 0 for s in sessions),
                         "models": _models({m: {"costUSD": f.get("costUSD")} for m, f in (s.get("models") or {}).items()}
                                           for s in sessions)})
        else:  # the 2026-11-10 layout
            stages = [run, *run.get("fix_rounds", [])]
            if any(s.get("total_cost_usd") is None for s in stages) or any(not s.get("review") for s in stages):
                raise Refused(f"{name} lacks the cost or the review of a stage")
            clean = (run.get("uncommitted") or 0) == 0
            rows.append({"run": name, "arm": run["arm"], "section": run["section"],
                         "end": "approved" if clean and _approved_old(stages[-1]) else "not-approved",
                         "cost": sum(s["total_cost_usd"] for s in stages),
                         "reviews": sum(1 for s in stages if s["review"].get("exit") == 0),
                         "wall": sum(s.get("wall_seconds") or 0 for s in stages),
                         "models": _models(s.get("modelUsage") for s in stages)})
    if not rows:
        raise Refused("the results file holds no runs")
    return rows


def judge(rows):
    """The verdict of the rule over normalised rows: (winner arm, branch, totals per arm). Refused when the arms do
    not hold the same distinct sections, an arm has fewer than three, or no arm is eligible."""
    arms = {}
    for row in rows:
        arms.setdefault(row["arm"], []).append(row)
    sections = {arm: [r["section"] for r in runs] for arm, runs in arms.items()}
    for arm, names in sections.items():
        if len(set(names)) != len(names):
            raise Refused(f"arm {arm} measured a section twice")
        if len(names) < MIN_SECTIONS:
            raise Refused(f"arm {arm} measured {len(names)} section(s); the rule needs at least {MIN_SECTIONS}")
    if len({frozenset(names) for names in sections.values()}) != 1:
        raise Refused("the arms did not measure the same sections, so their totals do not compare")
    totals = {arm: {"cost_usd": round(sum(r["cost"] for r in runs), 6), "reviews": sum(r["reviews"] for r in runs),
                    "wall_seconds": round(sum(r["wall"] for r in runs), 1),
                    "eligible": all(r["end"] == "approved" for r in runs)} for arm, runs in arms.items()}
    eligible = sorted((arm for arm, t in totals.items() if t["eligible"]),
                      key=lambda a: (totals[a]["cost_usd"], totals[a]["reviews"], totals[a]["wall_seconds"], a))
    if not eligible:
        raise Refused("no arm reached an approved review on every section")
    winner = eligible[0]
    if len(eligible) == 1:
        branch = "the only eligible arm"
    else:
        first, second = totals[eligible[0]], totals[eligible[1]]
        if first["cost_usd"] < second["cost_usd"]:
            branch = "the lowest cost to an approved review"
        elif first["reviews"] < second["reviews"]:
            branch = "a tie on cost, broken by fewer reviews"
        elif first["wall_seconds"] < second["wall_seconds"]:
            branch = "a tie on cost and reviews, broken by the shorter wall time"
        else:
            branch = "a tie on cost, reviews and wall time, broken by the arm's name"
    return winner, branch, totals


def verified_count(root=ROOT):
    """`query stats`' verified count; Refused when it cannot be read."""
    result = subprocess.run([sys.executable, str(Path(root) / "scripts" / "todo-graph.py"), "query", "stats"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=GIT_SECONDS,
                            env={**os.environ, "PYTHONUTF8": "1"})
    try:
        return int(json.loads(result.stdout)["verified"])
    except (ValueError, KeyError, TypeError):
        raise Refused(f"query stats could not be read (exit {result.returncode})") from None


def record_text(when, source, rows, winner, branch, totals, model):
    lines = [f"# Operating mode measurement, {when}", "",
             f"Decided by `python scripts/measure-modes.py decide` from `{source}` under the rule of D00 T03 §37: the "
             "lowest cost to an approved review among the arms that reached one on every section.", "",
             "## Runs", "", "| Run | Section | Arm | Cost | Reviews | Seconds | End |",
             "| --- | ------- | --- | ---- | ------- | ------- | --- |"]
    for row in sorted(rows, key=lambda r: (r["section"], r["arm"])):
        lines.append(f"| {row['run']} | {row['section']} | {row['arm']} | ${row['cost']:.2f} | {row['reviews']} | "
                     f"{round(row['wall'])} | {row['end']} |")
    lines += ["", "## Totals", "", "| Arm | Cost | Reviews | Seconds | Eligible |", "| --- | ---- | ------- | ------- | -------- |"]
    for arm in sorted(totals):
        t = totals[arm]
        lines.append(f"| {arm} | ${t['cost_usd']:.2f} | {t['reviews']} | {round(t['wall_seconds'])} | "
                     f"{'yes' if t['eligible'] else 'no'} |")
    lines += ["", "## Verdict", "", f"{winner}, by {branch}. The launcher starts the lead on `{model}`.", ""]
    return "\n".join(lines)


def cmd_decide(args, arms):
    source = Path(args.results)
    try:
        doc = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Refused(f"{source} cannot be read ({exc})") from None
    rows = normalise(doc)
    winner, branch, totals = judge(rows)
    table = {arm.name: arm for arm in arms}
    if winner not in table:
        raise Refused(f"the winner, {winner}, is not in the arm table, so there is no model to start")
    # The lead's own model: of the winner's models, the one of its alias's family (`claude-opus-5-5` for `opus`), so
    # the readers' Sonnet usage, however large, is never taken for the lead.
    alias = table[winner].model
    models = {}
    for row in rows:
        if row["arm"] == winner:
            for model, cost in row["models"].items():
                if alias in model.split("-"):
                    models[model] = models.get(model, 0.0) + cost
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    records = Path(args.records)
    root = Path(args.root).resolve()

    def shown(path):
        """A path as the verdict stores it: relative to the repository when inside it, so no machine path is kept."""
        path = Path(path).resolve()
        return path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()

    record = records / f"operating-mode-{when}.md"
    n = 2
    while record.exists():
        record = records / f"operating-mode-{when}-{n}.md"
        n += 1
    verdict = {"schema": SCHEMA, "arm": winner, "model": table[winner].model,
               "resolved_model": max(models, key=models.get) if models else None, "date": when,
               "base": (doc.get("identity") or {}).get("base") or doc.get("base"), "branch": branch,
               "totals": totals, "verified_at_decision": verified_count(args.root),
               "results": shown(source), "record": shown(record)}
    records.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=record.name + ".", suffix=".tmp", dir=records)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(record_text(when, shown(source), rows, winner, branch, totals, table[winner].model))
    os.replace(tmp, record)
    Path(args.verdict).parent.mkdir(parents=True, exist_ok=True)
    atomic_json(args.verdict, verdict)
    print(f"verdict: {winner} ({table[winner].model}), by {branch}; record {record}")
    return 0


def cmd_due(args):
    """Exit 0 with the reason when a measurement is due, 1 when not, 2 (Refused) when it cannot be told."""
    try:
        verdict = json.loads(Path(args.verdict).read_text(encoding="utf-8"))
        then, recorded, alias = int(verdict["verified_at_decision"]), verdict.get("resolved_model"), verdict["model"]
    except (OSError, ValueError, KeyError, TypeError):
        raise Refused(f"{args.verdict} cannot be read, so whether a measurement is due cannot be told") from None
    now = verified_count(args.root)
    if now - then >= REMEASURE_STAMPS:
        print(f"due: {now - then} sections stamped since the verdict ({then} then, {now} now)")
        return 0
    if alias not in args.model.split("-"):
        # The verdict chose another family than this session's: the switch happens at the launcher's next start,
        # and measuring again from the old session would only repeat the measurement that chose it.
        print(f"not due: the verdict switches the lead to {alias} at the next start; this session runs {args.model}")
        return 1
    if args.model != recorded:
        print(f"due: the {alias} alias now resolves to {args.model}, the verdict was measured on {recorded}")
        return 0
    print(f"not due: {now - then} of {REMEASURE_STAMPS} stamps since the verdict, and the lead model is unchanged")
    return 1


def summary(doc):
    lines = []
    for name, run in sorted(doc["runs"].items(), key=lambda kv: int(kv[0].split("-")[1])):
        cost = sum((s.get("session") or {}).get("cost_usd") or 0 for s in run["stages"])
        lines.append(f"{name}  {run['section']}  {run['arm']}  stages {len(run['stages'])}  ${cost:.2f}  "
                     f"{run['end'] or 'open'}")
    return "\n".join(lines)


def cmd_run(args, arms, repo):
    if args.parallel < 1 or args.fix_rounds < 0 or args.budget <= 0 or args.minutes <= 0 or args.gate_minutes <= 0:
        raise Refused("--parallel must be at least 1, --fix-rounds 0 or more, and the limits above 0")
    measurement = Measurement(args, arms, repo)
    with Lock(args.work):
        measurement.open()
        code = measurement.go()
    print(summary(measurement.doc))
    print(f"results: {measurement.results_path}")
    return code


def cmd_clean(args):
    work = Path(args.work)
    results = work / "results.json"
    if not results.is_file():
        raise Refused(f"{results} does not exist: nothing is recorded, so nothing is removed")
    with Lock(work):
        doc = json.loads(results.read_text(encoding="utf-8"))
        removed = []
        for name in doc.get("clones", []):
            target = (work / name).resolve()
            if target.parent != work.resolve() or not re.fullmatch(r"run-\d+", name):
                raise Refused(f"{results} lists {name!r}, which is not a clone of this work folder")
            if target.exists():
                remove_tree(target)
                removed.append(name)
    print(f"removed {len(removed)} clone(s) from {work}; kept {results.name} and logs")
    return 0


def parser():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawTextHelpFormatter,
                                epilog='example:\n  python scripts/measure-modes.py run --section "D00 T03 §32" '
                                       '--section "D00 T03 §29" --section "D02 T01 §30" --base HEAD')
    sub = p.add_subparsers(dest="command", required=True)
    default_work = str(scratch() / "measure-modes")
    run = sub.add_parser("run", help="build, gate, review and fix each section with each arm")
    run.add_argument("--section", action="append", required=True, metavar="REF",
                     help='a ready TODO section, "DNN TNN §N"; repeat for each section')
    run.add_argument("--base", default="HEAD", help="the commit every arm starts from (default HEAD)")
    run.add_argument("--work", default=default_work, help=f"the work folder (default {default_work})")
    run.add_argument("--budget", type=float, default=40, help="US dollars one session may spend (default 40)")
    run.add_argument("--minutes", type=float, default=75, help="minutes one session may run (default 75)")
    run.add_argument("--gate-minutes", type=float, default=45, help="minutes one gate may run (default 45)")
    run.add_argument("--fix-rounds", type=int, default=6, help="fix rounds per run at most (default 6)")
    run.add_argument("--parallel", type=int, default=3, help="sessions at a time at most (default 3)")
    run.add_argument("--repo", default=str(ROOT), help=argparse.SUPPRESS)
    clean = sub.add_parser("clean", help="remove the clones a finished measurement lists")
    clean.add_argument("--work", default=default_work, help=f"the work folder (default {default_work})")
    decide = sub.add_parser("decide", help="apply the rule to one results file and store the verdict")
    decide.add_argument("--results", required=True, help="a measurement's results.json (or the 2026-11-10 file)")
    decide.add_argument("--verdict", default=str(VERDICT), help=argparse.SUPPRESS)
    decide.add_argument("--records", default=str(RECORDS), help=argparse.SUPPRESS)
    decide.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    due = sub.add_parser("due", help="exit 0 when a measurement is due, 1 when not")
    due.add_argument("--model", required=True, help="the full model id the lead session runs on")
    due.add_argument("--verdict", default=str(VERDICT), help=argparse.SUPPRESS)
    due.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    return p


def main(argv=None, arms=ARMS):
    args = parser().parse_args(argv)
    if hasattr(args, "work"):
        # Absolute from here on: the prompt builder and the dispatcher run inside a clone, so a relative path to a
        # log would name a file under the clone instead.
        args.work = str(Path(args.work).resolve())
    try:
        arms = load_arms(arms)
        if args.command == "clean":
            return cmd_clean(args)
        if args.command == "decide":
            return cmd_decide(args, arms)
        if args.command == "due":
            return cmd_due(args)
        if len(set(args.section)) != len(args.section):
            raise Refused("a section is named twice")
        return cmd_run(args, arms, args.repo)
    except Refused as exc:
        print(f"measure-modes refused: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("measure-modes: interrupted; every running tree was stopped and the next run resumes", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
