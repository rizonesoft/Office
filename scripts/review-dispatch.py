#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Run one independent review round with the reviewer pinned in .conclave/reviewers.toml.

    python3 scripts/review-dispatch.py --writer claude --prompt review-prompt.md --record docs/reviews/x.md
    python3 scripts/review-dispatch.py --kind completion --candidate <40-char SHA> --writer claude \
        --prompt completion-prompt.md --record docs/reviews/x.md     the one-pass completion and excellence review
    python3 scripts/review-dispatch.py --check-pin [--json] [--pin <path>]     the pin's verdict; runs no reviewer
    python3 scripts/review-dispatch.py --list-rounds [--json] [--records <dir>]  recorded rounds; runs no reviewer

`--writer` is the agent whose work is under review (claude, codex or agy, with gemini as another name for agy, so a
route under either name serves both); its route in the pin names exactly one
reviewer, of a different model family, with no fallback. A reviewer that is not installed, exits non-zero, times out,
returns nothing, or ends its reply `OVERALL: blocked` (it could not reach the candidate, for example a sandbox that
cannot read the repository) returned no review, and the reason is recorded under `failover`: exit 1, which never
counts as approval, and no other reviewer runs. A review that finds problems is still a review (exit 0).

`--check-pin` loads the pin with `load_pin`, the only place the rules live, and reports without running anything:
with `--json`, `{"ok": true, "schema_version", "reviewers", "routes", "schedule", "clis": {cli: on PATH}}` (the
`schedule` key only when the pin has one) and exit 0, or `{"ok": false, "error": "<the Refused message>"}` and exit 2;
without `--json`, `ok` or `refused: <message>`.

Reviewers run read-only in the repository root: Codex in its read-only sandbox, Antigravity in plan mode inside its
sandbox, Claude Code in plan mode. The script prints a JSON summary; `--record` also appends a `## Round N` section to
the findings file with an atomic write, and writes nothing (exit 2, the summary still printed) to a findings file it
cannot read back. Works the same from PowerShell and from WSL. Stdlib only.

`--kind completion` runs the one-pass completion and excellence review (`docs/completion-review-prompt.md`) on the
built section before its regular rounds. With `--record` it appends a `## Completion review` section naming the
reviewer, its model and the `--candidate` commit instead of a `## Round N` section, and it is not counted as a round.
A findings file holds one returned completion review: a second is refused (exit 2) and nothing is appended, while a
pass that returned no review (`## Completion review: none`) may be followed by another.

`--kind plan` runs the one-pass plan review (`docs/plan-review-prompt.md`) on the section as written, before the build:
it asks whether building the section exactly as planned produces a 100% complete feature. It is recorded as a
`## Plan review` section with the same one-pass rule, and it is not counted as a round.

When the pin has a `[schedule]`, the dispatcher owns each pass's effort and lenses: the
plan and completion passes take their scheduled effort, and a round's place in `[[schedule.rounds]]` comes from the
rounds that returned a review already recorded in the `--record` file. Rounds past that list rotate one lens per round
through `[schedule.rotation]` (the design lens only with `--surface`), and a low-effort round whose review reads
`HIGHEST: P1` is followed by the `[schedule.escalation]` step. The scheduled lenses are appended to the prompt and
recorded on an `- Lenses:` line. The JSON summary carries `position`, `escalated` and `severity_stop` (true when a
returned round past `severity_stop_after` reads `HIGHEST: P3`: the loop may stop there; with 0, from round 1).

With `policy = "three-pass"` in the pin's `[schedule]` a section takes one plan review before the build, one round
after it, one completion review of the final candidate, and then `--kind reconciliation`
(`docs/reconciliation-review-prompt.md`) only after a completion that returned gaps, again after each reconciliation
that returned gaps. For a findings file named for a section (`docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md`) that
order is checked before a reviewer runs, each candidate must be a commit descending from the pass before, and a
reconciliation is refused once the section has spent its `pass_cap` returned passes, after `no_progress_cap`
reconciliations in a row with no less severe a worst finding, and after a pass whose worst finding is below the
pin's `blocking` levels. A three-pass section runs under the pin committed at its plan review's candidate, schedule
and route both; when that three-pass pin no longer loads the pass is refused, never run under the working tree's,
and a plan review is refused while the working tree's three-pass pin is not committed at its candidate. A rotation
section follows the working tree's pin as it always did, with one exception that keeps it on the rules it began
under: once the working tree's pin has become three-pass, it finishes under the rotation pin committed at its plan
review's candidate, and is refused when that commit holds no pin.

Under three-pass every scheduled lens is appended with its question and owes one line `LENS <name>: clean` or
`LENS <name>: findings`. A reply missing a lens line, its `HIGHEST:` line or the final verdict lines of its kind, or
one that ends complete while declaring a severity that holds the stamp, is recorded with no
reviewer (`## Round N: none`, the reason on its `- Skipped:` line, its text kept), exits 1 and never counts as a pass;
the JSON summary names the lenses in `incomplete`. A `[[schedule.conditional]]` entry's lenses join a pass when a file
changed between the plan review's candidate and the pass's candidate starts with one of its paths; a plan review, and
a review outside a section, take the files from `--paths`. The summary of a returned three-pass review carries
`highest` and `blocking` (whether that severity holds the stamp).
"""
import argparse
import atexit
import ctypes
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]


def _load_review_pin():
    """scripts/review_pin.py, the one place the pin's rules live, loaded from this file's own folder by path: the
    dispatcher is itself loaded by path (its name is not importable), and nothing on sys.path decides which copy runs."""
    path = Path(__file__).resolve().with_name("review_pin.py")
    if not path.is_file():
        sys.exit(f"review-dispatch: {path} is missing; the reviewer kit installs it beside this script")
    spec = importlib.util.spec_from_file_location("review_pin", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


review_pin = _load_review_pin()
# The pin's rules, under the names this module has always offered them by (the todo kit's stamp reads them here).
Refused, load_pin, PIN = review_pin.Refused, review_pin.load_pin, review_pin.PIN
WRITERS, CLIS, FAMILY, WRITER_FAMILY = review_pin.WRITERS, review_pin.CLIS, review_pin.FAMILY, review_pin.WRITER_FAMILY
EFFORTS, LENSES, THREE_PASS = review_pin.EFFORTS, review_pin.LENSES, review_pin.THREE_PASS
highest, returned_review, scheduled = review_pin.highest, review_pin.returned_review, review_pin.scheduled
lens_block, check_schedule, check_step = review_pin.lens_block, review_pin.check_schedule, review_pin.check_step
declared_highest, pass_cap = review_pin.declared_highest, review_pin.pass_cap
# Antigravity takes the prompt only as the -p value. Past this size it gets a pointer to the prompt file instead.
# Windows caps a whole command line at 32,767 characters; Linux caps one argument at 128 KiB.
ARGV_PROMPT_LIMIT = 24_000 if os.name == "nt" else 100_000
# A review is prose. Output past this size is a runaway reviewer, not a review.
MAX_OUTPUT_BYTES = 2_000_000
# The prompt's reply format ends with an OVERALL line; `blocked` means the reviewer never saw the work.
BLOCKED = re.compile(r"^\s*(?:OVERALL|COMPLETION):\s*blocked\b", re.IGNORECASE)
POLL_SECONDS = 0.2
CLEANUP_SECONDS = 10
# The last lines each one-pass review owes, by --kind: what makes a reply a returned review of that kind.
FOOTERS = {"completion": ("COMPLETION: complete", "COMPLETION: gaps"),
           "reconciliation": ("RECONCILIATION: complete", "RECONCILIATION: gaps")}
OVERALL = ("OVERALL: approve", "OVERALL: needs-attention")


def valid_one_pass_footer(text, kind):
    """True when a one-pass reply (`completion`, `reconciliation` or `plan`) ends with the verdict lines its prompt
    asks for. The todo kit's stamp requires the same lines."""
    lines = [x.strip() for x in (text or "").splitlines() if x.strip()]
    if kind == "plan":
        return len(lines) >= 2 and lines[-2] in ("PLAN: complete", "PLAN: gaps") and lines[-1] in OVERALL
    return bool(lines) and lines[-1] in FOOTERS.get(kind, ())


def returned_one_pass(entry, kind):
    """A recorded completion, reconciliation or plan pass that is a review: returned by a reviewer of another model
    family than the writer and ending in that kind's verdict lines. The todo kit's stamp uses this same predicate."""
    return bool(entry.get("reviewer")) and entry.get("writer") in WRITER_FAMILY \
        and FAMILY.get(entry.get("cli")) not in (None, WRITER_FAMILY[entry["writer"]]) \
        and valid_one_pass_footer(entry.get("review"), kind)


def ended_gaps(entry):
    """True for a completion or reconciliation whose final line is its `gaps` verdict."""
    lines = [x.strip() for x in (entry.get("review") or "").splitlines() if x.strip()]
    return bool(lines) and lines[-1] in ("COMPLETION: gaps", "RECONCILIATION: gaps")


def decode_reply(data):
    """A reviewer's reply as text: strict UTF-8 when it is, otherwise Windows-1252, the code page a CLI on Windows
    may write its file in, so a curly quote is kept instead of becoming a replacement character. The same on every
    platform, and it never raises: the five bytes Windows-1252 leaves undefined become replacement characters."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


EXTENSION = re.compile(r"\.[A-Za-z0-9]+")


def find_cli(name):
    """A reviewer CLI's path, from the absolute directories on PATH only, or None.

    Reviews run from the reviewed repository's root, and Windows `shutil.which` looks in the working directory first
    (always on Python 3.11, and on later ones unless NoDefaultCurrentDirectoryInExePath is set), so a `codex.cmd`
    committed to that repository would be reported as installed and run as the reviewer. Relative PATH entries are
    dropped for the same reason. On Windows the search is done here, by PATHEXT, so no Python version adds the directory.
    """
    directories = [d for d in os.environ.get("PATH", "").split(os.pathsep) if fully_qualified(d)]
    if os.name != "nt":
        return shutil.which(name, path=os.pathsep.join(directories))
    # An empty PATHEXT gets the defaults too, as shutil.which does. The bare name is the last candidate in each
    # directory: npm puts an extensionless shell script beside codex.cmd, and Windows can run only the .cmd.
    # Only entries shaped like an extension: one that holds a separator or ".." would lead out of the PATH directory.
    extensions = [e for e in os.environ.get("PATHEXT", "").split(os.pathsep) if EXTENSION.fullmatch(e)] \
        or [".COM", ".EXE", ".BAT", ".CMD"]
    for directory in directories:
        for candidate in [os.path.join(directory, name + e) for e in extensions] + [os.path.join(directory, name)]:
            if os.path.isfile(candidate):
                return candidate
    return None


def fully_qualified(directory):
    """True for a PATH entry that names one place whatever the working directory: on Windows a drive and a root
    (`C:\\x`) or a UNC share, never `\\x` (the current drive's) or `C:x` (that drive's current directory), which
    os.path.isabs accepts on Python 3.11 and 3.12."""
    if os.name != "nt":
        return os.path.isabs(directory)
    drive, rest = os.path.splitdrive(directory)
    return drive.startswith(("\\\\", "//")) or (len(drive) == 2 and rest[:1] in ("\\", "/"))


def command(reviewer, executable, prompt, prompt_path, output_path, timeout, effort=None):
    """The argv and stdin for one read-only review. The model comes only from the pin, and the effort from the pin's
    reviewer or, when the pin has a [schedule], from the step it schedules for this pass (Antigravity takes none).
    When neither sets one, no effort argument is passed and the CLI's own configuration decides."""
    cli, model = reviewer["cli"], reviewer["model"]
    if cli == "codex":
        return [executable, "exec", "-m", model, *(["-c", f"model_reasoning_effort={effort}"] if effort else []),
                "--sandbox", "read-only", "--ephemeral", "--skip-git-repo-check", "-o", str(output_path), "-"], prompt
    if cli == "claude":
        return [executable, "-p", "--model", model, *(["--effort", effort] if effort else []),
                "--permission-mode", "plan"], prompt
    text = prompt
    # A Windows .cmd or .bat shim re-parses its arguments through cmd.exe, so prose there could become commands:
    # it only ever gets a pointer to the prompt file. So does a prompt too long for a command line.
    shim = Path(executable).suffix.lower() in (".cmd", ".bat")
    if shim or len(prompt.encode()) > ARGV_PROMPT_LIMIT or len(prompt) > ARGV_PROMPT_LIMIT:
        text = f"Follow the review instructions in the file {prompt_path} exactly. Do not modify any file."
    return [executable, "--model", model, "--mode", "plan", "--sandbox", "--print-timeout", f"{timeout}s",
            f"-p={text}"], None


# Win32 job objects, by ctypes (standard library): a reviewer started suspended and assigned to a job set to kill on
# close has every descendant it starts in the job, so ending the job ends the whole tree, even a child that outlives
# a reviewer which exited by itself.
CREATE_NEW_PROCESS_GROUP = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
CREATE_SUSPENDED = 0x00000004
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS = 9
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000


class _IO_COUNTERS(ctypes.Structure):
    _fields_ = [("ReadOperationCount", ctypes.c_uint64), ("WriteOperationCount", ctypes.c_uint64),
                ("OtherOperationCount", ctypes.c_uint64), ("ReadTransferCount", ctypes.c_uint64),
                ("WriteTransferCount", ctypes.c_uint64), ("OtherTransferCount", ctypes.c_uint64)]


class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", ctypes.c_uint32), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", ctypes.c_uint32),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", ctypes.c_uint32),
                ("SchedulingClass", ctypes.c_uint32)]


class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION), ("IoInfo", _IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]


_WIN32 = None


def _win32_apis():
    """kernel32 and ntdll with every function this module calls declared, loaded once (Windows only)."""
    global _WIN32
    if _WIN32 is None:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        kernel32.CreateJobObjectW.restype = ctypes.c_void_p
        kernel32.SetInformationJobObject.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
        kernel32.SetInformationJobObject.restype = ctypes.c_int
        kernel32.AssignProcessToJobObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        kernel32.AssignProcessToJobObject.restype = ctypes.c_int
        kernel32.TerminateJobObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        kernel32.TerminateJobObject.restype = ctypes.c_int
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel32.CloseHandle.restype = ctypes.c_int
        ntdll = ctypes.WinDLL("ntdll")
        ntdll.NtResumeProcess.argtypes = [ctypes.c_void_p]
        ntdll.NtResumeProcess.restype = ctypes.c_int32
        _WIN32 = kernel32, ntdll
    return _WIN32


def create_windows_job():
    """A new, unconfigured Win32 job object handle; raises OSError."""
    kernel32, _ = _win32_apis()
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    return job


def configure_windows_job(job):
    """Set JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE on `job`, so every process in it ends when the job ends or its last
    handle closes; raises OSError."""
    kernel32, _ = _win32_apis()
    info = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not kernel32.SetInformationJobObject(job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS, ctypes.byref(info),
                                            ctypes.sizeof(info)):
        raise ctypes.WinError(ctypes.get_last_error())


def assign_windows_job(job, process):
    """Put the suspended `process` in `job`, before it has run an instruction; raises OSError."""
    kernel32, _ = _win32_apis()
    if not kernel32.AssignProcessToJobObject(job, ctypes.c_void_p(int(process._handle))):
        raise ctypes.WinError(ctypes.get_last_error())


def resume_windows_process(process):
    """Let the suspended, already assigned `process` run; raises OSError."""
    _, ntdll = _win32_apis()
    status = ntdll.NtResumeProcess(ctypes.c_void_p(int(process._handle)))
    if status != 0:
        raise OSError(f"NtResumeProcess returned 0x{status & 0xFFFFFFFF:08x}")


def close_windows_job(job):
    """Terminate every process in `job` and close its handle. Called once per job."""
    kernel32, _ = _win32_apis()
    kernel32.TerminateJobObject(job, 1)
    kernel32.CloseHandle(job)


def kill_tree(process, job=None):
    """End a reviewer and everything it started, whether it is still running or has already exited. On Windows that is
    the job the reviewer was started in (see `run`), ended here and its handle closed; on Linux and WSL it is the
    reviewer's whole session. `process` is None when the reviewer never started."""
    if os.name == "nt":
        if job is not None:
            close_windows_job(job)
        if process is not None:
            try:
                process.kill()
            except OSError:
                pass  # already exited
    elif process is not None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass  # nothing in the group is left to kill


def remove_scratch(path):
    """Remove a reviewer's scratch directory. The reviewer's whole process tree has ended by now, but on Windows a
    file lock can lag a moment behind a process's exit, so a failed removal is retried for a bounded time. A directory
    that still cannot be removed is left behind with a note: the round's outcome is already decided."""
    deadline = time.monotonic() + CLEANUP_SECONDS
    while True:
        try:
            shutil.rmtree(path)
            return
        except FileNotFoundError:
            return
        except OSError as exc:
            if time.monotonic() > deadline:
                print(f"review-dispatch: left {path} behind ({exc.strerror or type(exc).__name__})", file=sys.stderr)
                return
            time.sleep(POLL_SECONDS)


def feed(pipe, text):
    try:
        pipe.write(text.encode("utf-8"))
        pipe.close()
    except (BrokenPipeError, OSError):
        pass  # the reviewer stopped reading or exited; its exit code and output decide the round


def run(argv, stdin_text, timeout, watched):
    """Run one reviewer in its own process group (on Windows, suspended inside a kill-on-close job object and resumed
    once it is in the job), watching the size of every file it writes while it runs, so neither a hang nor a flood of
    output can take the dispatcher or the disk down. The group or job, with every descendant, is ended afterwards
    whatever happened. Returns (exit code, None) or (None, the reason it returned no review)."""
    windows = os.name == "nt"
    group = {"creationflags": CREATE_NEW_PROCESS_GROUP | CREATE_SUSPENDED} if windows else {"start_new_session": True}
    stdout_path = watched[0]
    with open(stdout_path, "wb") as output:
        job = process = None
        step = "create job"
        try:
            try:
                if windows:
                    job = create_windows_job()
                    step = "configure job"
                    configure_windows_job(job)
                step = "start"
                process = subprocess.Popen(argv, cwd=ROOT,
                                           stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
                                           stdout=output, stderr=subprocess.DEVNULL, **group)
                if windows:
                    step = "assign to job"
                    assign_windows_job(job, process)
                    step = "resume"
                    resume_windows_process(process)
            except (OSError, ValueError) as exc:
                why = getattr(exc, "strerror", None) or str(exc) or type(exc).__name__
                return None, f"could not start: {why}" if step == "start" else f"could not start: {step}: {why}"
            if stdin_text is not None:
                # Fed from a thread: a reviewer that never reads would otherwise block this write past any timeout.
                threading.Thread(target=feed, args=(process.stdin, stdin_text), daemon=True).start()
            deadline = time.monotonic() + timeout
            while process.poll() is None:
                if any(path.is_file() and path.stat().st_size > MAX_OUTPUT_BYTES for path in watched):
                    return None, f"returned more than {MAX_OUTPUT_BYTES} bytes"
                if time.monotonic() > deadline:
                    return None, "timed out"
                try:
                    # Wakes the moment the reviewer exits, and otherwise after one poll interval.
                    process.wait(timeout=POLL_SECONDS)
                except subprocess.TimeoutExpired:
                    continue
        finally:
            # The job is ended and closed here exactly once, on every path, then the reviewer itself is reaped.
            kill_tree(process, job)
            if process is not None:
                process.wait()
                if process.stdin is not None:
                    try:
                        process.stdin.close()
                    except OSError:
                        pass
    if process.returncode != 0:
        return None, f"exited {process.returncode}"
    if any(path.is_file() and path.stat().st_size > MAX_OUTPUT_BYTES for path in watched):
        return None, f"returned more than {MAX_OUTPUT_BYTES} bytes"
    return process.returncode, None


def review(pin, writer, prompt_path, timeout, plan=None, kind="round"):
    """Run the writer's one reviewer. Returns the summary dict: `reviewer` is None when no review came back, and
    `failover` then names the reviewer and why (there is no fallback). `plan` is the scheduled step (see `scheduled`):
    its effort replaces the reviewer's, and its lenses are appended to the prompt and recorded.

    Under the three-pass policy a reply is a review only when it is complete: it ends with the verdict lines of its
    kind and carries one `LENS <name>:` line per scheduled lens. An incomplete reply is returned with `reviewer` None
    like an outage, the reason in `failover`, the missing lenses in `incomplete` and its text kept in `review`, so it
    is recorded and can be read but never counts as a pass."""
    name = review_pin.route_for(pin, writer)
    if name is None:
        raise Refused(f"the reviewer pin has no route for writer {writer!r}")
    try:
        prompt = Path(prompt_path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise Refused(f"the review prompt {prompt_path} is not UTF-8 text; save it as UTF-8 and run again") from None
    if not prompt.strip():
        raise Refused("the review prompt is empty")
    if "\0" in prompt:
        raise Refused("the review prompt contains a NUL byte; no reviewer can be given it")
    reviewer = pin["reviewers"][name]
    # With a schedule the step alone decides, so the record always shows what the schedule says and the stamp can
    # replay it: a step without an effort passes none, whatever the reviewer's own. Without a schedule the reviewer's
    # effort runs. With neither, no effort is passed and the CLI's own configuration decides.
    effort = plan["effort"] if plan else reviewer.get("effort")
    if reviewer["cli"] == "agy":
        # Antigravity takes no effort argument: it runs at the effort its model name carries. That is the scheduled
        # effort whenever the name ends with it (a three-pass pin loads only so), and then the record says so, as the
        # stamp's replay of the schedule expects; otherwise nothing is claimed.
        effort = effort if effort and reviewer["model"].endswith(f"-{effort}") else None
    lenses = plan["lenses"] if plan else []
    schedule = pin.get("schedule", {})
    three_pass = schedule.get("policy") == THREE_PASS
    # Under three-pass every scheduled pass gets the block, also one with no lenses: it asks for the HIGHEST line.
    appended = bool(lenses) or (three_pass and plan is not None)
    if appended:
        prompt = prompt.rstrip("\n") + lens_block(plan, schedule)
    scheduled_fields = {"effort": effort, "lenses": lenses} if plan else {}

    def none(reason):
        return {"writer": writer, "reviewer": None, "failover": [{"reviewer": name, "reason": reason}], "review": None,
                **scheduled_fields}

    # The resolved path, not the bare name: on Windows a CLI is often a .cmd shim that Popen cannot find by name.
    executable = find_cli(reviewer["cli"])
    if executable is None:
        return none(f"{reviewer['cli']} is not installed")
    text = None
    tmp = Path(tempfile.mkdtemp())
    try:
        stdout_path, message_path = tmp / "stdout.txt", tmp / "last-message.md"
        prompt_file = Path(prompt_path).resolve()
        if appended:
            # The pointer an Antigravity shim gets must name the prompt with what the dispatcher appended to it.
            prompt_file = tmp / "prompt.md"
            prompt_file.write_text(prompt, encoding="utf-8", newline="\n")
        argv, stdin_text = command(reviewer, executable, prompt, prompt_file, message_path, timeout, effort)
        _, problem = run(argv, stdin_text, timeout, [stdout_path, message_path])
        if problem is None:
            # Codex writes its final message to the -o file; stdout carries its progress, not the review.
            source = message_path if reviewer["cli"] == "codex" else stdout_path
            text = decode_reply(source.read_bytes()) if source.is_file() else ""
    finally:
        remove_scratch(tmp)
    if problem is None and not (text or "").strip():
        problem = "returned no review"
    if problem is None:
        problem = blocked(text)
    if problem:
        return none(problem)
    if three_pass:
        final = valid_one_pass_footer(text, kind) if kind in PASSES else \
            ([x.strip() for x in text.splitlines() if x.strip()] or [""])[-1] in OVERALL
        missing = review_pin.missing_lens_verdicts(lenses, text)
        # A completion or reconciliation that ends complete while declaring a finding that holds the stamp
        # contradicts itself: it is not a verdict the section can be closed on.
        worst = declared_highest(text)
        contradicts = kind in FOOTERS and final and not ended_gaps({"review": text}) \
            and worst in review_pin.SEVERITIES and review_pin.blocks(schedule, worst)
        # The severity line is what blocking levels, the no-progress count and the stamp read: without it the reply
        # says nothing they can act on.
        undeclared = worst is None
        if not final or missing or contradicts or undeclared:
            why = ([f"no final {kind} verdict line"] if not final else []) \
                + ([f"no LENS verdict line for {', '.join(missing)}"] if missing else []) \
                + (["no HIGHEST line"] if undeclared else []) \
                + ([f"it ends {kind.upper()}: complete but declares HIGHEST: {worst}, which holds the stamp"]
                   if contradicts else [])
            return {**none(f"incomplete: {' and '.join(why)}"), "review": text.strip(), "incomplete": missing}
    return {"writer": writer, "reviewer": name, "cli": reviewer["cli"], "model": reviewer["model"],
            "effort": effort, "failover": [], "review": text.strip(), **({"lenses": lenses} if plan else {})}


def blocked(text):
    """Why a reply is not a review, when its last line is `OVERALL: blocked` (or `COMPLETION: blocked`); None for a
    review."""
    lines = [line for line in text.strip().splitlines() if line.strip()]
    if not lines or not BLOCKED.match(lines[-1]):
        return None
    reason = next((line.strip() for line in lines[:-1] if not line.lstrip().startswith("#")), "no reason given")
    return f"could not review: {reason[:300]}"


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        # newline="": the text is written as given, so a review's own "\r" bytes are stored and nothing is translated.
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


# A findings file is read back by `list_rounds`, so the envelope `record` writes around each review is unambiguous:
# the metadata states how many lines the review has (`- Lines: N`, lines split on "\n" only) and a digest of them
# (`- Digest:`, the first 16 hex digits of the SHA-256 of the canonical lines joined with "\n"). The reader skips
# exactly N lines and checks the digest, so neither a quoted heading nor an edit of the same length passes for a round.
# The review is stored byte for byte; a line's trailing "\r" is dropped only to compare, so a CRLF checkout reads the
# same. Rounds recorded before the count have no Lines field and run to the next round heading; rounds recorded
# before the digest have Lines without Digest and are read by their count alone.
# Numbers are ASCII digits of bounded length, so the reader's int() can never raise (`\d` also takes "²", and a number
# past Python's digit limit raises). A review is at most MAX_OUTPUT_BYTES, so it has at most MAX_OUTPUT_BYTES + 1 lines,
# and the count's width follows from that: whatever `record` writes, the reader reads.
ROUND_HEADING = re.compile(r"^## Round ([0-9]{1,6}): (none|([a-z0-9][a-z0-9-]*) \(`([^`]+)` via `([a-z]+)`\))$")
# Office: `Type` is the review type this repository's rounds recorded from 2026-11-08 until the pin's `type` key was
# retired with the move to this dispatcher. The reader takes it so those rounds stay evidence; `record` never writes it.
ROUND_LINE = re.compile(r"^- (Writer|Run|Candidate|Effort|Lenses|Lines|Digest|Skipped|Type): (\S.*)$")
# The one-pass completion review, recorded beside the rounds and never counted as one. It always carries Lines, Digest
# and the Candidate commit it reviewed; the writer's notes after it (its `- Filed:` lines) run to the next `## ` line.
COMPLETION_HEADING = re.compile(r"^## Completion review: (none|([a-z0-9][a-z0-9-]*) \(`([^`]+)` via `([a-z]+)`\))$")
PLAN_HEADING = re.compile(r"^## Plan review: (none|([a-z0-9][a-z0-9-]*) \(`([^`]+)` via `([a-z]+)`\))$")
RECONCILIATION_HEADING = re.compile(
    r"^## Reconciliation review: (none|([a-z0-9][a-z0-9-]*) \(`([^`]+)` via `([a-z]+)`\))$")
COMPLETION_LINE = re.compile(r"^- (Writer|Run|Candidate|Effort|Lenses|Lines|Digest|Skipped): (\S.*)$")
# The one-pass reviews, by --kind: the heading each is recorded under and the key read_findings lists them under.
PASSES = {"completion": ("## Completion review", COMPLETION_HEADING, "completions"),
          "plan": ("## Plan review", PLAN_HEADING, "plans"),
          "reconciliation": ("## Reconciliation review", RECONCILIATION_HEADING, "reconciliations")}
RESERVED = ("## Round", *(prefix for prefix, _, _ in PASSES.values()))
RESERVED_NAMES = ("headings starting `## Round`, `## Completion review`, `## Plan review` or "
                  "`## Reconciliation review` are reserved for --record")
LENS_NAME = re.compile(r"[a-z0-9][a-z0-9-]*")
CANDIDATE = re.compile(r"[0-9a-f]{40}")
SKIPPED = re.compile(r"^([a-z0-9][a-z0-9-]*) \((.*)\)$")
COUNT = re.compile(r"[0-9]{1,%d}" % len(str(MAX_OUTPUT_BYTES + 1)))
DIGEST = re.compile(r"[0-9a-f]{16}")


def raw_lines(text):
    """Lines split on "\n" alone, the one boundary `record` and the reader share, every other byte kept. `str.splitlines`
    also splits on "\r", U+2028, U+0085 and others, which a review may contain."""
    return text.split("\n")


def canonical(line):
    """A line as compared and digested: a CRLF checkout's trailing "\r" dropped."""
    return line[:-1] if line.endswith("\r") else line


def digest(lines):
    return hashlib.sha256("\n".join(canonical(line) for line in lines).encode("utf-8")).hexdigest()[:16]


def _read_findings(text):
    """The rounds and completion reviews `record` and `record_completion` wrote in one findings file, as
    `{"rounds": [...], "completions": [...]}`, or None when anything they write is not as they write it.

    A round is a `## Round` heading, a blank line, and a metadata block to the next blank line in which every line is
    one of `record`'s fields (Writer and Run exactly once, Effort, Lines and Digest at most once, any number of Skipped;
    Digest only with Lines). With Lines, the next N lines are the review, skipped unread, and a blank line or the end of
    the file must follow them; with Digest, they must also hash to it, so a hand edit inside a review shows as
    unreadable even when it keeps the count. Without Lines (a round recorded before the count), the round runs to the
    next reserved heading. A round may carry the Candidate commit it reviewed. A completion review, a plan review
    (`## Plan review`) and a reconciliation review (`## Reconciliation review`) are read the same way, with
    Writer, Run, Candidate, Lines and Digest required; the lines after it up to the next `## ` line are its `notes`,
    the writer's own record of what was done with each gap. Lenses, when present, is the comma-separated list the
    schedule gave the pass. Anything else makes the file unreadable rather than losing a field."""
    found = {"rounds": [], "completions": [], "plans": [], "reconciliations": []}
    raw = raw_lines(text)
    lines = [canonical(line) for line in raw]
    i = 0
    while i < len(lines):
        kind = next((k for k, (prefix, _, _) in PASSES.items() if lines[i].startswith(prefix)), None)
        completion = kind is not None
        if not lines[i].startswith("## Round") and not completion:
            i += 1
            continue
        head = i
        heading = (PASSES[kind][1] if completion else ROUND_HEADING).match(lines[i])
        if not heading or i + 1 >= len(lines) or lines[i + 1] != "":
            return None, head
        if completion:
            entry = {"reviewer": heading.group(2), "model": heading.group(3), "cli": heading.group(4), "writer": None,
                     "run": None, "candidate": None, "effort": None, "lenses": None, "skipped": []}
        else:
            entry = {"number": int(heading.group(1)), "reviewer": heading.group(3), "model": heading.group(4),
                     "cli": heading.group(5), "writer": None, "run": None, "candidate": None, "effort": None,
                     "lenses": None, "skipped": []}
        count = sealed = None
        i += 2
        while i < len(lines) and lines[i] != "":
            field = (COMPLETION_LINE if completion else ROUND_LINE).match(lines[i])
            if not field:
                return None, head
            key, value = field.group(1).lower(), field.group(2)
            if key == "skipped":
                skipped = SKIPPED.match(value)
                if not skipped:
                    return None, head
                entry["skipped"].append({"reviewer": skipped.group(1), "reason": skipped.group(2)})
            elif key == "lines":
                # ASCII digits only: "²" passes str.isdigit and int() raises on it.
                if count is not None or not COUNT.fullmatch(value):
                    return None, head
                count = int(value)
            elif key == "digest":
                if sealed is not None or not DIGEST.fullmatch(value):
                    return None, head
                sealed = value
            elif key == "type":
                if "type" in entry or not LENS_NAME.fullmatch(value):
                    return None, head
                entry["type"] = value
            elif entry[key] is not None or (key == "candidate" and not CANDIDATE.fullmatch(value)):
                return None, head
            elif key == "lenses":
                names = value.split(", ")
                # Any well-formed name: a pin may declare lenses of its own, and the reader has no pin. Whether
                # the names are the scheduled ones is the stamp's check.
                if not all(LENS_NAME.fullmatch(name) for name in names) or len(set(names)) != len(names):
                    return None, head
                entry[key] = names
            else:
                entry[key] = value
            i += 1
        if entry["writer"] is None or entry["run"] is None or (sealed is not None and count is None):
            return None, head
        if completion and (entry["candidate"] is None or sealed is None):
            return None, head
        if count is not None:
            start = i + 1  # the blank line after the metadata, then the review, unread
            i = start + count
            if i > len(lines) or (i < len(lines) and lines[i] != ""):
                return None, head
            if sealed is not None and digest(raw[start:i]) != sealed:
                return None, head
            entry["review"] = "\n".join(lines[start:i])
        else:
            end = next((j for j in range(i, len(lines)) if lines[j].startswith(RESERVED)), len(lines))
            entry["review"] = "\n".join(lines[i:end])
            i = end
        if completion:
            end = next((j for j in range(i, len(lines)) if lines[j].startswith("## ")), len(lines))
            entry["notes"] = [line for line in lines[i:end] if line.strip()]
            i = end
            found[PASSES[kind][2]].append(entry)
        else:
            found["rounds"].append(entry)
    return found, None


def read_findings(text):
    """See `_read_findings`: the parsed rounds, completion and plan reviews, or None when the file cannot be read."""
    return _read_findings(text)[0]


def unreadable_heading(text):
    """The line where a findings file stops being readable, as `line N: <text>`, so a refusal can name it. A writer's
    own note under a heading that starts `## Round`, `## Completion review` or `## Plan review` is the usual cause:
    those prefixes are reserved for what `--record` writes."""
    found, head = _read_findings(text)
    if found is not None or head is None:
        return ""
    lines = raw_lines(text)
    return f"; the first unreadable record starts at line {head + 1}: {canonical(lines[head])!r}" if head < len(lines) else ""


def read_rounds(text):
    """The rounds `record` wrote in one findings file (completion reviews are not rounds), or None when the file is not
    as `record` and `record_completion` write it (see read_findings)."""
    found = read_findings(text)
    return None if found is None else found["rounds"]


def read_completions(text):
    """The completion reviews `record_completion` wrote in one findings file, or None when it cannot be read back."""
    found = read_findings(text)
    return None if found is None else found["completions"]


def read_plans(text):
    """The plan reviews `--kind plan` recorded in one findings file, or None when it cannot be read back."""
    found = read_findings(text)
    return None if found is None else found["plans"]


class Unrecorded(Exception):
    """The findings file cannot be read back, so a round is not appended to it."""


def existing_findings(path, what):
    """A findings file's text as stored, or `Unrecorded` when it cannot be read."""
    try:
        # Bytes, not read_text: universal newlines would turn a stored lone "\r" into a line break and move the
        # line count of an earlier round.
        return path.read_bytes().decode("utf-8") if path.exists() else ""
    except (OSError, UnicodeDecodeError) as exc:
        raise Unrecorded(f"{path} cannot be read back ({exc}), so the {what} was not recorded") from None


def append_findings(path, existing, lines):
    # Always one blank line before the heading, even when the file already ends in one: a review whose last line is
    # empty also ends the file in "\n\n", and the reader needs a blank line after the review's own lines.
    separator = "" if not existing else ("\n" if existing.endswith("\n") else "\n\n")
    atomic_write(path, existing + separator + "\n".join(lines))


def record(path, result, when, candidate=None):
    """Append one round and return its number, with the `candidate` commit it reviewed when one was named. A findings file the reader cannot read back gets nothing appended:
    numbering it would have to guess (counting headings counts quoted ones), so `Unrecorded` is raised instead."""
    existing = existing_findings(path, "round")
    known = read_rounds(existing)
    if known is None:
        raise Unrecorded(f"{path} cannot be read back (a round heading or line is not in the format --record writes"
                         f"{unreadable_heading(existing)}; {RESERVED_NAMES}), so the round was not recorded")
    number = len(known) + 1
    who = f"{result['reviewer']} (`{result['model']}` via `{result['cli']}`)" if result["reviewer"] else "none"
    review = raw_lines(result["review"] or "No reviewer returned a review. This round is not an approval.")
    if not COUNT.fullmatch(str(len(review))) or not ROUND_HEADING.match(f"## Round {number}: none"):
        raise Unrecorded(f"the review or the round number is past what {path} can be read back with, "
                         f"so the round was not recorded")
    lines = [f"## Round {number}: {who}", "", f"- Writer: {result['writer']}", f"- Run: {when}"]
    lines += [f"- Candidate: {candidate}"] if candidate else []
    lines += metadata(result)
    lines += [f"- Lines: {len(review)}", f"- Digest: {digest(review)}", "", *review, ""]
    append_findings(path, existing, lines)
    return number


def metadata(result):
    lines = [f"- Effort: {result['effort']}"] if result.get("effort") else []
    if result.get("lenses"):
        lines.append(f"- Lenses: {', '.join(result['lenses'])}")
    return lines + [f"- Skipped: {f['reviewer']} ({f['reason']})" for f in result["failover"]]


def record_completion(path, result, when, candidate, kind="completion"):
    """Append the completion review (or, by kind, the plan or a reconciliation review). The plan and completion
    reviews are one pass each: a findings file that already holds a returned one gets nothing appended (`Unrecorded`),
    and neither does one the reader cannot read. Reconciliations repeat; `check_three_pass_order` bounds them."""
    prefix, _, key = PASSES[kind]
    what = f"{kind} review"
    existing = existing_findings(path, what)
    found = read_findings(existing)
    if found is None:
        raise Unrecorded(f"{path} cannot be read back (a heading or line is not in the format --record writes"
                         f"{unreadable_heading(existing)}; {RESERVED_NAMES}), so the {what} was not recorded")
    if kind != "reconciliation" and any(returned_one_pass(entry, kind) for entry in found[key]):
        raise Unrecorded(f"{path} already holds a {what}; it is one pass, so this one was not recorded")
    who = f"{result['reviewer']} (`{result['model']}` via `{result['cli']}`)" if result["reviewer"] else "none"
    review = raw_lines(result["review"] or f"No reviewer returned a {what}. This pass is not an approval.")
    if not COUNT.fullmatch(str(len(review))):
        raise Unrecorded(f"the review is past what {path} can be read back with, so it was not recorded")
    lines = [f"{prefix}: {who}", "", f"- Writer: {result['writer']}", f"- Run: {when}", f"- Candidate: {candidate}"]
    lines += metadata(result)
    lines += [f"- Lines: {len(review)}", f"- Digest: {digest(review)}", "", *review, ""]
    append_findings(path, existing, lines)


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, timeout=60)


def descends(older, newer):
    """True when commit `older` is `newer` or an ancestor of it."""
    return git("merge-base", "--is-ancestor", older, newer).returncode == 0


# Windows opens `DOCS/Reviews/...` as the same file, so there the name is matched without regard to case: a section's
# rules cannot be stepped around by respelling its findings file.
SECTION_FINDINGS = re.compile(r"(?:^|/)docs/reviews/[0-9]{2}-[A-Za-z0-9_-]+/D[0-9]{2}-T[0-9]{2}-s[1-9][0-9]*\.md$",
                              re.IGNORECASE if os.name == "nt" else 0)


def section_record(record_path):
    """True for a findings file named for a TODO section, `docs/reviews/<NN-domain>/D<NN>-T<NN>-s<N>.md`: the file
    whose passes have an order. Any other findings file is a standalone review."""
    return bool(record_path) and bool(SECTION_FINDINGS.search(Path(os.path.abspath(record_path)).as_posix()))


def returned_plan(record_path):
    """The one returned plan review recorded in a findings file, or None."""
    if not record_path or not Path(record_path).exists():
        return None
    found = read_findings(existing_findings(Path(record_path), "review"))
    plans = [e for e in (found or {"plans": []})["plans"] if returned_one_pass(e, "plan")]
    return plans[0] if len(plans) == 1 else None


def is_three_pass(pin):
    return pin is not None and pin.get("schedule", {}).get("policy") == THREE_PASS


def committed_pin(sha):
    """The pin committed at `sha`, or None when that commit holds none (or holds an earlier pin that no longer loads
    and was never three-pass). A three-pass pin there that does not load is a refusal naming the commit."""
    shown = git("show", f"{sha}:.conclave/reviewers.toml")
    if shown.returncode != 0:
        return None
    try:
        return load_pin(data=shown.stdout)
    except Refused as exc:
        if THREE_PASS.encode() not in shown.stdout:
            return None
        raise Refused(f"the reviewer pin at {sha} does not load: {exc}") from None


def section_pin(pin_path, record_path, kind, candidate):
    """The pin a pass runs under.

    A three-pass section keeps the pin its plan review read: the plan review runs under the three-pass pin committed
    at its own candidate, and every later pass under the one at its returned plan review's candidate, schedule and
    route both, so a pin change (or a broken working-tree pin) never moves a section already under review. That pin
    is never replaced by the working tree's: when the working tree's pin is three-pass but the plan review's
    candidate does not hold it, the plan review is refused until the pin is committed, so no section starts unfrozen.

    Everything else takes the pin at `pin_path`, as it always did: a findings file not named for a section, a section
    with no returned plan review, and a rotation section. One exception keeps a section on the rules it began under:
    when the working tree's pin has since become three-pass, a section whose plan candidate holds a rotation pin
    finishes under that committed pin. The todo kit's stamp replays the same rule."""
    if not section_record(record_path):
        return load_pin(pin_path)
    plan = returned_plan(record_path)
    sha = candidate if kind == "plan" else plan["candidate"] if plan else None
    held = committed_pin(sha) if sha else None
    if is_three_pass(held):
        return held
    working = load_pin(pin_path)
    if not is_three_pass(working) or sha is None:
        return working
    if kind == "plan":
        raise Refused(f"the pin is three-pass, but the plan review's candidate {sha} does not hold it: commit "
                      f".conclave/reviewers.toml first, so the section keeps the pin its plan review read")
    if held is None:
        raise Refused(f"this section's plan review ran at {sha}, which holds no reviewer pin, and the pin has since "
                      f"become three-pass: there is no pin for the section to finish under")
    return held


def changed_paths(base, candidate):
    """The files that differ between two commits, as repository-relative paths with forward slashes. Renames are
    listed as the file removed and the file added, so a file moved out of a watched folder still counts for it."""
    shown = git("-c", "core.quotepath=false", "diff", "--name-only", "--no-renames", "-z", base, candidate)
    if shown.returncode != 0:
        raise Refused(f"cannot list the files changed between {base} and {candidate}")
    return [name for name in shown.stdout.decode("utf-8", errors="replace").split("\0") if name]


SEVERITY_RANK = {"P1": 3, "P2": 2, "P3": 1, "none": 0, None: 3}
# How long past its owner's own timeout a section lock is believed: a run that was killed cannot hold it for ever.
LOCK_GRACE_SECONDS = 300
# How long a takeover of an expired lock may itself take before it is treated as abandoned.
TAKEOVER_SECONDS = 60


def section_lock_path(record_path):
    """Where the lock of one section's findings file lives: the system's temporary folder, never the repository, so
    a run that is killed leaves nothing in the working tree."""
    name = os.path.normcase(os.path.abspath(record_path)).encode("utf-8")
    return Path(tempfile.gettempdir()) / f"review-dispatch-{hashlib.sha256(name).hexdigest()[:16]}.lock"


def _create_exclusive(path, text):
    """Create `path` holding `text` only if it does not exist: True when this process created it."""
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    try:
        os.write(fd, text.encode("ascii"))
    finally:
        os.close(fd)
    return True


def _lock_expiry(path):
    """When the lock at `path` stops being believed, from what its owner wrote in it (`<pid> <expiry> <token>`), or
    None when there is no lock. A lock that cannot be read (half written, or not ours) is believed for the grace
    period from its last change."""
    try:
        return float(path.read_text(encoding="ascii", errors="replace").split()[1])
    except FileNotFoundError:
        return None
    except (IndexError, ValueError, OSError):
        try:
            return path.stat().st_mtime + LOCK_GRACE_SECONDS
        except OSError:
            return None


def release_section(path, owned):
    """Remove the lock at `path` only while it still holds what this process wrote: never another run's lock."""
    try:
        if path.read_text(encoding="ascii", errors="replace") == owned:
            path.unlink()
    except FileNotFoundError:
        return  # already gone: there is nothing of ours left to release
    except OSError as exc:
        # The lock then stands until the expiry written in it; say so rather than leave it unexplained.
        print(f"review-dispatch: left the lock {path} behind ({exc.strerror or type(exc).__name__})", file=sys.stderr)


def lock_section(record_path, timeout):
    """Take a three-pass section's lock for the rest of this run: the order check, the review and the record happen
    under it, so a second launch of the same pass sees the first one's record instead of spending another review.

    The owner writes its own expiry into the lock (its start, its own `--timeout` and a grace period), so a later
    launch with a shorter timeout cannot decide a live review is dead. Only a lock past the expiry its owner wrote
    is taken over, by one process at a time (a second, exclusive takeover file), and a process releases only the
    lock it wrote, when it exits."""
    path = section_lock_path(record_path)
    owned = f"{os.getpid()} {time.time() + timeout + LOCK_GRACE_SECONDS:.0f} {os.urandom(8).hex()}"
    busy = Refused(f"another review of {record_path} is already running (lock {path}); a section takes one pass at "
                   f"a time")
    if not _create_exclusive(path, owned):
        expiry = _lock_expiry(path)
        if expiry is not None and time.time() <= expiry:
            raise busy
        takeover = path.with_name(path.name + ".takeover")
        if not _create_exclusive(takeover, owned):
            # Someone else is taking the expired lock over; an abandoned takeover is cleared for the next launch.
            try:
                if time.time() - takeover.stat().st_mtime > TAKEOVER_SECONDS:
                    takeover.unlink()
            except FileNotFoundError:
                raise busy from None  # the other launch finished its takeover just now
            raise busy
        try:
            # Looked at again under the takeover: the lock may have been replaced since it was first read.
            expiry = _lock_expiry(path)
            if expiry is not None and time.time() <= expiry:
                raise busy
            path.unlink(missing_ok=True)
            if not _create_exclusive(path, owned):
                raise busy
        finally:
            release_section(takeover, owned)
    atexit.register(release_section, path, owned)


def check_three_pass_order(kind, record_path, candidate, schedule):
    """The order of a three-pass section's passes: the plan review, one round on a candidate descending from it, one
    completion review, then reconciliations only after a completion that returned gaps, each on a candidate
    descending from the pass before, until one returns complete. A reconciliation is also refused once the section
    has spent its `pass_cap` returned passes, after `no_progress_cap` reconciliations in a row whose worst finding is
    no less severe than the pass before, and after a pass whose worst finding is below the pin's `blocking` levels
    (those findings are filed, not reviewed again). Refused here so that a pass out of order never spends a review;
    the stamp holds the receipt to the same order. A findings file not named for a section has no order."""
    if not section_record(record_path):
        return
    found = read_findings(existing_findings(Path(record_path), f"{kind} review"))
    if found is None:
        raise Unrecorded(f"{record_path} cannot be read back ({RESERVED_NAMES}), so no {kind} review was run")
    plans = [e for e in found["plans"] if returned_one_pass(e, "plan")]
    rounds = [e for e in found["rounds"] if returned_review(e)]
    completions = [e for e in found["completions"] if returned_one_pass(e, "completion")]
    reconciled = [e for e in found["reconciliations"] if returned_one_pass(e, "reconciliation")]
    if candidate and git("cat-file", "-e", f"{candidate}^{{commit}}").returncode != 0:
        raise Refused(f"--candidate {candidate} is not a commit in this repository")
    if kind == "plan":
        if plans or rounds or completions:
            raise Refused("the plan review runs once, before the build and every other pass")
        return
    if len(plans) != 1:
        raise Refused(f"the {kind} pass needs the section's returned plan review first")
    if kind == "round":
        if rounds or completions:
            raise Refused("the three-pass policy allows one round, before the completion review")
        if not candidate:
            raise Refused("a section's round needs --candidate, the commit under review")
        if not descends(plans[0]["candidate"], candidate):
            raise Refused(f"the round's candidate does not descend from the plan review's {plans[0]['candidate']}")
    elif kind == "completion":
        if len(rounds) != 1 or completions:
            raise Refused("the completion review runs once, after the section's returned round")
        if rounds[0]["candidate"] is None or not descends(rounds[0]["candidate"], candidate):
            raise Refused(f"the completion's candidate does not descend from the round's {rounds[0]['candidate']}")
    elif kind == "reconciliation":
        if len(rounds) != 1 or len(completions) != 1 or not ended_gaps(completions[0]):
            raise Refused("a reconciliation follows one round and a completion review that returned gaps")
        chain = [completions[0], *reconciled]
        if not ended_gaps(chain[-1]):
            raise Refused("the section's reconciliation already returned complete; it needs no further pass")
        worst = [declared_highest(e["review"]) for e in chain]
        # Only a pin that names its blocking levels ends the loop this way; without the key every gap is repaired.
        if "blocking" in schedule and not review_pin.blocks(schedule, worst[-1]):
            raise Refused(f"the last pass's worst finding is {worst[-1]}, below the pin's blocking levels "
                          f"({', '.join(schedule['blocking'])}): file its findings and stamp; it takes no further pass")
        cap = pass_cap(schedule)
        if len(plans) + len(rounds) + len(chain) >= cap:
            raise Refused(f"the section has spent its {cap} review passes (pass_cap); it stays blocked")
        stall = review_pin.no_progress_cap(schedule)
        if stall is not None:
            run = 0
            for before, after in reversed(list(zip(worst, worst[1:]))):
                if SEVERITY_RANK[after] < SEVERITY_RANK[before]:
                    break
                run += 1
            if run >= stall:
                raise Refused(f"the section's last {run} reconciliations made no progress (no_progress_cap {stall}); "
                              f"it stays blocked")
        if not descends(chain[-1]["candidate"], candidate):
            raise Refused(f"the reconciliation's candidate does not descend from the last pass's "
                          f"{chain[-1]['candidate']}")


def list_rounds(records_dir):
    """Every findings file under records_dir that holds rounds, with each round as `record` wrote it. A file
    whose round headings or lines are not `record`'s is named in `unreadable`, never dropped."""
    records_dir = Path(records_dir)
    records, unreadable = [], []

    def shown(path):
        # Never resolve: a path being reported as unreadable may be a symlink loop, which resolve() raises on.
        path = Path(os.path.abspath(path))
        return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()

    try:
        paths = sorted(records_dir.rglob("*.md")) if records_dir.is_dir() else []
    except OSError:  # a folder that cannot be walked is reported, like a file that cannot be read
        return {"records": [], "unreadable": [shown(records_dir)]}
    for path in paths:
        # One file that cannot be read, or is not UTF-8, is named in `unreadable`; the others are still listed.
        try:
            found = read_findings(path.read_bytes().decode("utf-8"))
        # RuntimeError: a symlink loop on older Pythons. ValueError: anything read_findings meets that int() or the
        # digest cannot take, so one bad file never aborts the listing.
        except (OSError, UnicodeDecodeError, RuntimeError, ValueError):
            found = None
        if found is None:
            unreadable.append(shown(path))
        elif found["rounds"] or found["completions"] or found["plans"] or found["reconciliations"]:
            records.append({"path": shown(path), "rounds": found["rounds"],
                            **({"completions": found["completions"]} if found["completions"] else {}),
                            **({"plans": found["plans"]} if found["plans"] else {}),
                            **({"reconciliations": found["reconciliations"]} if found["reconciliations"] else {})})
    return {"records": records, **({"unreadable": unreadable} if unreadable else {})}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--writer", choices=WRITERS, help="The agent whose work is under review")
    parser.add_argument("--prompt", help="File holding the review prompt")
    parser.add_argument("--record", help="Findings file to append this round (or completion review) to")
    parser.add_argument("--kind", choices=("round", "completion", "plan", "reconciliation"), default="round",
                        help="round (default): one review round; completion: the one-pass completion and excellence "
                             "review, recorded as a ## Completion review section and not counted as a round; plan: "
                             "the one-pass plan review before the build, recorded as a ## Plan review section; "
                             "reconciliation (three-pass pins): the pass after a completion that returned gaps")
    parser.add_argument("--candidate", help="The full 40-character commit under review: required with --kind "
                                            "completion, plan or reconciliation (for a plan review, the commit "
                                            "holding the section as reviewed) and for a three-pass section's round; "
                                            "optional for any other round, recorded as its Candidate line")
    parser.add_argument("--paths", nargs="*", default=[], metavar="FILE",
                        help="Three-pass pins with [[schedule.conditional]]: the files the section changes, for a "
                             "plan review or a review outside a section. A section's later passes take their changed "
                             "files from the candidate instead")
    parser.add_argument("--surface", action="store_true",
                        help="The section has Surface: yes, so the design lens applies: a rotation schedule includes "
                             "it in its rotation, and a three-pass round keeps it")
    parser.add_argument("--timeout", type=int, default=1800,
                        help="Seconds before the reviewer is stopped and the round records no review")
    parser.add_argument("--pin", default=str(PIN), help=argparse.SUPPRESS)
    parser.add_argument("--check-pin", action="store_true",
                        help="Report whether the pin loads, and each CLI's presence, instead of running a review; "
                             "no reviewer runs (exit 0 loads, 2 refused)")
    parser.add_argument("--list-rounds", action="store_true",
                        help="List the recorded review rounds instead of running one; no reviewer runs")
    parser.add_argument("--json", action="store_true", help="With --list-rounds, print the listing as JSON")
    parser.add_argument("--records", default=str(ROOT / "docs" / "reviews"),
                        help="With --list-rounds, the folder of findings files (default docs/reviews)")
    args = parser.parse_args(argv)
    if args.check_pin:
        # load_pin stays the only place the rules live: this reports its verdict and runs nothing.
        try:
            pin = load_pin(args.pin)
        except Refused as exc:
            print(json.dumps({"ok": False, "error": str(exc)}) if args.json else f"refused: {exc}")
            return 2
        clis = {cli: find_cli(cli) is not None for cli in CLIS}
        report = {"ok": True, "schema_version": pin["schema_version"], "reviewers": pin["reviewers"],
                  "routes": pin["routes"], **({"schedule": pin["schedule"]} if "schedule" in pin else {}), "clis": clis}
        print(json.dumps(report) if args.json else "ok")
        return 0
    if args.list_rounds:
        listing = list_rounds(args.records)
        if args.json:
            print(json.dumps(listing, indent=2))
        else:
            for entry in listing["records"]:
                for p in entry.get("plans", []):
                    who = f"{p['reviewer']} ({p['model']} via {p['cli']})" if p["reviewer"] else "no review"
                    print(f"{entry['path']}  Plan review: {who}, candidate {p['candidate']}, {p['run']}")
                for c in entry.get("completions", []):
                    who = f"{c['reviewer']} ({c['model']} via {c['cli']})" if c["reviewer"] else "no review"
                    print(f"{entry['path']}  Completion review: {who}, candidate {c['candidate']}, {c['run']}")
                for c in entry.get("reconciliations", []):
                    who = f"{c['reviewer']} ({c['model']} via {c['cli']})" if c["reviewer"] else "no review"
                    print(f"{entry['path']}  Reconciliation review: {who}, candidate {c['candidate']}, {c['run']}")
                for r in entry["rounds"]:
                    who = f"{r['reviewer']} ({r['model']} via {r['cli']})" if r["reviewer"] else "no review"
                    print(f"{entry['path']}  Round {r['number']}: {who}, writer {r['writer']}, {r['run']}")
            for path in listing.get("unreadable", []):
                print(f"{path}  unreadable: a round heading or line is not in the record format")
        return 0
    if not args.writer or not args.prompt:
        parser.error("--writer and --prompt are required unless --check-pin or --list-rounds is given")
    one_pass = args.kind in PASSES
    if one_pass and not (args.candidate and CANDIDATE.fullmatch(args.candidate)):
        parser.error(f"--kind {args.kind} needs --candidate, the full 40-character commit under review")
    if args.kind == "round" and args.candidate and not CANDIDATE.fullmatch(args.candidate):
        parser.error("--candidate must be the full 40-character commit under review")
    try:
        # A section keeps the pin its plan review read, schedule and route both.
        pin = section_pin(args.pin, args.record, args.kind, args.candidate)
        schedule = pin.get("schedule", {})
        three_pass = schedule.get("policy") == THREE_PASS
        paths = [p.replace("\\", "/") for p in args.paths]
        if three_pass:
            if section_record(args.record):
                lock_section(args.record, args.timeout)
            check_three_pass_order(args.kind, args.record, args.candidate, schedule)
            if args.kind != "plan" and section_record(args.record):
                if paths:
                    raise Refused("--paths goes with a plan review or a review outside a section; this pass takes "
                                  "its changed files from its candidate")
                paths = changed_paths(returned_plan(args.record)["candidate"], args.candidate)
        elif args.kind == "reconciliation":
            raise Refused("this section's pin has no reconciliation pass; only policy = \"three-pass\" takes one")
        elif paths:
            raise Refused("--paths goes with a three-pass pin; this pin's schedule has no conditional lenses")
        plan = None
        if "schedule" in pin:
            rounds = []
            if args.record and args.kind == "round":
                # The position in the schedule comes from the rounds already recorded; a file that cannot be read
                # back is refused here, before a review is spent that could not be recorded.
                existing = existing_findings(Path(args.record), "round")
                rounds = read_rounds(existing)
                if rounds is None:
                    raise Unrecorded(f"{args.record} cannot be read back (a round heading or line is not in the "
                                     f"format --record writes{unreadable_heading(existing)}; {RESERVED_NAMES}), so "
                                     f"no round was run")
            plan = scheduled(schedule, args.kind, rounds, args.surface, paths)
        result = review(pin, args.writer, args.prompt, args.timeout, plan, args.kind)
    except (Refused, Unrecorded, OSError) as exc:
        print("review-dispatch refused: " + str(exc), file=sys.stderr)
        return 2
    when = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if one_pass or args.candidate:
        result.update(kind=args.kind, candidate=args.candidate)
    if three_pass and result["reviewer"]:
        # What the review's worst finding means under the pin: only a blocking level holds the stamp or earns
        # another pass.
        worst = declared_highest(result["review"])
        result.update(highest=worst, blocking=review_pin.blocks(schedule, worst))
    if plan and plan["position"] and three_pass:
        result.update(position=plan["position"], escalated=False, severity_stop=False)
    elif plan and plan["position"]:
        result.update(position=plan["position"], escalated=plan["escalated"])
        stop_after = pin["schedule"]["severity_stop_after"]
        # The severity stop: a returned round past `severity_stop_after` whose worst finding is P3 ends the loop (0:
        # from round 1; todo_graph.SEVERITY_CUTOFF_ROUND is the same number, and `stamp`
        # re-checks it).
        result["severity_stop"] = bool(result["reviewer"]) and plan["position"] > stop_after \
            and highest(result["review"]) == "P3"
    if args.record:
        try:
            if one_pass:
                record_completion(Path(args.record), result, when, args.candidate, args.kind)
                result["recorded"] = True
            else:
                result["round"] = record(Path(args.record), result, when, args.candidate)
        except (Unrecorded, OSError) as exc:
            # The review still reaches stdout; only the findings file is left as it was. A write that fails (a full
            # disk, a folder that may not be written) is the same: the writes are atomic, so the file is whole, and a
            # review that was paid for is never lost with it.
            unrecorded = {"recorded": False} if one_pass else {"round": None}
            print(json.dumps({**result, **unrecorded, "run": when}, indent=2))
            why = str(exc) if isinstance(exc, Unrecorded) else \
                f"{args.record} could not be written ({exc.strerror or exc}), so the review was not recorded"
            print("review-dispatch refused: " + why, file=sys.stderr)
            return 2
    print(json.dumps({**result, "run": when}, indent=2))
    return 0 if result["reviewer"] else 1


if __name__ == "__main__":
    sys.exit(main())
