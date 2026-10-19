#!/usr/bin/env python3
"""Run one independent review round with the reviewers pinned in .conclave/reviewers.toml, failing over in order.

    python3 scripts/review-dispatch.py --writer claude --prompt review-prompt.md --record docs/reviews/x.md

`--writer` is the agent whose work is under review (claude, codex or gemini); its route in the pin lists reviewers in
failover order. The first reviewer that runs and returns a review is the round. One that is not installed, exits
non-zero, times out or returns nothing is skipped and the reason recorded. When every reviewer fails there is no
review: exit 1, which never counts as approval. A review that finds problems is still a review (exit 0).

Reviewers run read-only in the repository root: Codex in its read-only sandbox, Antigravity in plan mode inside its
sandbox, Claude Code in plan mode. The script prints a JSON summary; `--record` also appends a `## Round N` section to
the findings file with an atomic write. Works the same from PowerShell and from WSL. Stdlib only.
"""
import argparse
from datetime import datetime, timezone
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
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PIN = ROOT / ".conclave" / "reviewers.toml"
WRITERS = ("claude", "codex", "gemini")
CLIS = ("codex", "agy", "claude")
EFFORTS = {"codex": ("low", "medium", "high", "xhigh"), "claude": ("low", "medium", "high", "xhigh", "max")}
MODEL = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# Antigravity takes the prompt only as the -p value. Past this size it gets a pointer to the prompt file instead.
# Windows caps a whole command line at 32,767 characters; Linux caps one argument at 128 KiB.
ARGV_PROMPT_LIMIT = 24_000 if os.name == "nt" else 100_000
# A review is prose. Output past this size is a runaway reviewer, not a review.
MAX_OUTPUT_BYTES = 2_000_000
POLL_SECONDS = 0.2
CLEANUP_SECONDS = 10


class Refused(Exception):
    """The pin or the arguments are wrong; nothing ran."""


def load_pin(path=PIN):
    try:
        with open(path, "rb") as handle:
            pin = tomllib.load(handle)
    except FileNotFoundError:
        raise Refused(f"no reviewer pin at {path}") from None
    except tomllib.TOMLDecodeError as exc:
        raise Refused(f"unreadable reviewer pin: {exc}") from None
    if set(pin) != {"schema_version", "reviewers", "routes"} or pin["schema_version"] != 1:
        raise Refused("the reviewer pin needs exactly schema_version = 1, [reviewers.*] and [routes]")
    reviewers = pin["reviewers"]
    if not isinstance(reviewers, dict) or not reviewers:
        raise Refused("the reviewer pin defines no reviewers")
    for name, entry in reviewers.items():
        if not NAME.match(name) or not isinstance(entry, dict):
            raise Refused(f"invalid reviewer {name!r}")
        unknown = set(entry) - {"cli", "model", "effort"}
        if unknown:
            raise Refused(f"reviewer {name!r} has unknown keys: {', '.join(sorted(unknown))}")
        cli, model, effort = entry.get("cli"), entry.get("model"), entry.get("effort")
        if cli not in CLIS:
            raise Refused(f"reviewer {name!r} needs cli = one of {', '.join(CLIS)}")
        if not isinstance(model, str) or not MODEL.match(model):
            raise Refused(f"reviewer {name!r} has a malformed model")
        if cli == "agy":
            if effort is not None:
                raise Refused(f"reviewer {name!r}: Antigravity carries the effort in the model name, so set no effort")
        elif effort not in EFFORTS[cli]:
            raise Refused(f"reviewer {name!r} needs effort = one of {', '.join(EFFORTS[cli])}")
    routes = pin["routes"]
    if not isinstance(routes, dict) or set(routes) - set(WRITERS):
        raise Refused(f"[routes] may only name the writers {', '.join(WRITERS)}")
    for writer, chain in routes.items():
        if not isinstance(chain, list) or not chain or not all(isinstance(r, str) for r in chain):
            raise Refused(f"route {writer!r} must be a non-empty list of reviewer names")
        if any(r not in reviewers for r in chain) or len(set(chain)) != len(chain):
            raise Refused(f"route {writer!r} must list defined reviewers, each once")
    return pin


def command(reviewer, executable, prompt, prompt_path, output_path, timeout):
    """The argv and stdin for one read-only review. The model and effort come only from the pin."""
    cli, model, effort = reviewer["cli"], reviewer["model"], reviewer.get("effort")
    if cli == "codex":
        return [executable, "exec", "-m", model, "-c", f"model_reasoning_effort={effort}", "--sandbox", "read-only",
                "--ephemeral", "--skip-git-repo-check", "-o", str(output_path), "-"], prompt
    if cli == "claude":
        return [executable, "-p", "--model", model, "--effort", effort, "--permission-mode", "plan"], prompt
    text = prompt
    # A Windows .cmd or .bat shim re-parses its arguments through cmd.exe, so prose there could become commands:
    # it only ever gets a pointer to the prompt file. So does a prompt too long for a command line.
    shim = Path(executable).suffix.lower() in (".cmd", ".bat")
    if shim or len(prompt.encode()) > ARGV_PROMPT_LIMIT or len(prompt) > ARGV_PROMPT_LIMIT:
        text = f"Follow the review instructions in the file {prompt_path} exactly. Do not modify any file."
    return [executable, "--model", model, "--mode", "plan", "--sandbox", "--print-timeout", f"{timeout}s", f"-p={text}"], None


def kill_tree(process):
    """End a reviewer and everything it started, whether it is still running or has already exited."""
    if os.name == "nt":
        # WORKAROUND: Windows offers no process-group kill without job objects, so taskkill /T reaches the reviewer's
        # children only while the reviewer itself is alive. A child that outlives a reviewer which exited by itself
        # is not reached on Windows; on Linux and WSL the whole session is killed below.
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(process.pid)], capture_output=True)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass  # nothing in the group is left to kill


def remove_scratch(path):
    """Remove a reviewer's scratch directory. On Windows a file stays locked until every process holding it has
    exited, and a reviewer's helper can outlive the reviewer (see kill_tree) and keep writing into it, so a failed
    removal is retried for a bounded time. A directory that still cannot be removed is left behind with a note: the
    round's outcome is already decided."""
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
    """Run one reviewer in its own process group, watching the size of every file it writes while it runs, so neither
    a hang nor a flood of output can take the dispatcher or the disk down. The group is ended afterwards whatever
    happened. Returns (exit code, None) or (None, reason to fail over)."""
    group = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    stdout_path = watched[0]
    with open(stdout_path, "wb") as output:
        try:
            process = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
                                       stdout=output, stderr=subprocess.DEVNULL, **group)
        except (OSError, ValueError) as exc:
            return None, f"could not start: {getattr(exc, 'strerror', None) or type(exc).__name__}"
        try:
            if stdin_text is not None:
                # Fed from a thread: a reviewer that never reads would otherwise block this write past any timeout.
                threading.Thread(target=feed, args=(process.stdin, stdin_text), daemon=True).start()
            deadline = time.monotonic() + timeout
            while process.poll() is None:
                if any(path.is_file() and path.stat().st_size > MAX_OUTPUT_BYTES for path in watched):
                    return None, f"returned more than {MAX_OUTPUT_BYTES} bytes"
                if time.monotonic() > deadline:
                    return None, "timed out"
                time.sleep(POLL_SECONDS)
        finally:
            kill_tree(process)
            process.wait()
    if process.returncode != 0:
        return None, f"exited {process.returncode}"
    if any(path.is_file() and path.stat().st_size > MAX_OUTPUT_BYTES for path in watched):
        return None, f"returned more than {MAX_OUTPUT_BYTES} bytes"
    return process.returncode, None


def review(pin, writer, prompt_path, timeout):
    """Walk the writer's route until one reviewer returns a review. Returns the summary dict."""
    if writer not in pin["routes"]:
        raise Refused(f"the reviewer pin has no route for writer {writer!r}")
    prompt = Path(prompt_path).read_text(encoding="utf-8")
    if not prompt.strip():
        raise Refused("the review prompt is empty")
    if "\0" in prompt:
        raise Refused("the review prompt contains a NUL byte; no command line can carry it")
    failover = []
    for name in pin["routes"][writer]:
        reviewer = pin["reviewers"][name]
        # The resolved path, not the bare name: on Windows a CLI is often a .cmd shim that Popen cannot find by name.
        executable = shutil.which(reviewer["cli"])
        if executable is None:
            failover.append({"reviewer": name, "reason": f"{reviewer['cli']} is not installed"})
            continue
        stdout = None
        tmp = Path(tempfile.mkdtemp())
        try:
            stdout_path, message_path = tmp / "stdout.txt", tmp / "last-message.md"
            argv, stdin_text = command(reviewer, executable, prompt, Path(prompt_path).resolve(), message_path, timeout)
            _, problem = run(argv, stdin_text, timeout, [stdout_path, message_path])
            if problem is None:
                source = message_path if reviewer["cli"] == "codex" else stdout_path
                stdout = source.read_text(encoding="utf-8", errors="replace") if source.is_file() else ""
        finally:
            remove_scratch(tmp)
        if problem is None and not (stdout or "").strip():
            problem = "returned no review"
        if problem:
            failover.append({"reviewer": name, "reason": problem})
            continue
        return {"writer": writer, "reviewer": name, "cli": reviewer["cli"], "model": reviewer["model"],
                "effort": reviewer.get("effort"), "failover": failover, "review": stdout.strip()}
    return {"writer": writer, "reviewer": None, "failover": failover, "review": None}


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def record(path, result, when):
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    number = len(re.findall(r"^## Round \d+", existing, flags=re.M)) + 1
    who = f"{result['reviewer']} (`{result['model']}` via `{result['cli']}`)" if result["reviewer"] else "none"
    lines = [f"## Round {number}: {who}", "", f"- Writer: {result['writer']}", f"- Run: {when}"]
    if result.get("effort"):
        lines.append(f"- Effort: {result['effort']}")
    lines += [f"- Skipped: {f['reviewer']} ({f['reason']})" for f in result["failover"]]
    lines += ["", result["review"] if result["review"] else "No reviewer returned a review. This round is not an approval.", ""]
    separator = "" if not existing or existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
    atomic_write(path, existing + separator + "\n".join(lines))
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--writer", required=True, choices=WRITERS, help="The agent whose work is under review")
    parser.add_argument("--prompt", required=True, help="File holding the review prompt")
    parser.add_argument("--record", help="Findings file to append this round to")
    parser.add_argument("--timeout", type=int, default=1800, help="Seconds per reviewer before failing over")
    parser.add_argument("--pin", default=str(PIN), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        result = review(load_pin(args.pin), args.writer, args.prompt, args.timeout)
    except (Refused, OSError) as exc:
        print("review-dispatch refused: " + str(exc), file=sys.stderr)
        return 2
    when = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if args.record:
        result["round"] = record(Path(args.record), result, when)
    print(json.dumps({**result, "run": when}, indent=2))
    return 0 if result["reviewer"] else 1


if __name__ == "__main__":
    sys.exit(main())
