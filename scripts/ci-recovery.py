#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""One bounded recovery budget per red `main`, kept across sessions, resumes and run files (D00 T03 §18).

    python scripts/ci-recovery.py open <sha>        # start the recovery for this red head, or attach it to the open one
    python scripts/ci-recovery.py attach <head>     # a repair head pushed during the recovery
    python scripts/ci-recovery.py reserve <kind>    # repair | rerun | wait | unreadable, before the action runs
    python scripts/ci-recovery.py result <outcome>  # green | red | pending | unreadable, for the last attempt
    python scripts/ci-recovery.py close <head>      # a green head that descends from the first: the recovery ends
    python scripts/ci-recovery.py show              # the open recovery and its attempts

The state lives in build/ci-recovery.json (gitignored, written temp-then-replace), so it survives a session's death,
a resume and a new run file without dirtying the tree. Every attempt is reserved before its action runs: a reserved
attempt with no result after a resume counts as spent and is never repeated, and a reserved rerun is never run again.
At most four attempts per recovery, any mix of kinds; a fifth is refused with `exhausted` (exit 1), and the campaign
then files, emails and parks with `ci-red`. One flake rerun per head. Only `close <green head>` ends a recovery, and
only for a head that descends from its first head, so no green result for an unrelated head can reset the budget.

Exit 0 done, 1 refused (exhausted, a second rerun, no open recovery, a head that does not descend), 2 unreadable state.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import todo_graph

STATE = ROOT / "build" / "ci-recovery.json"
BUDGET = 4
KINDS = ("repair", "rerun", "wait", "unreadable")
OUTCOMES = ("green", "red", "pending", "unreadable")
SHA_LENGTH = 40


class Refused(Exception):
    """The request is refused; nothing changed (exit 1)."""


class Unreadable(Exception):
    """The state file cannot be read; it is never silently reset (exit 2)."""


def load(path):
    if not path.exists():
        return {"recovery": None}
    try:
        state = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise Unreadable(f"{path} cannot be read ({exc}); fix or remove it by hand") from None
    recovery = state.get("recovery") if isinstance(state, dict) else "invalid"
    if recovery is not None and not (isinstance(recovery, dict) and isinstance(recovery.get("first"), str)
                                     and isinstance(recovery.get("heads"), list)
                                     and isinstance(recovery.get("attempts"), list)
                                     and isinstance(recovery.get("reruns"), list)):
        raise Unreadable(f"{path} does not hold a recovery in the expected shape; fix or remove it by hand")
    return state


def save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def full_sha(value):
    if len(value) != SHA_LENGTH or any(c not in "0123456789abcdef" for c in value):
        raise Refused(f"{value!r} is not a full 40-character commit SHA")
    return value


def descends(first, head, run):
    """Whether `head` is `first` or has it as an ancestor (git merge-base --is-ancestor)."""
    if head == first:
        return True
    git = todo_graph.review_dispatch().find_cli("git")
    if git is None:
        raise Unreadable("git is not on PATH")
    result = run([git, "-C", str(ROOT), "merge-base", "--is-ancestor", first, head])
    if result.returncode not in (0, 1):
        raise Unreadable(f"git merge-base failed for {first[:7]} and {head[:7]}")
    return result.returncode == 0


def open_recovery(state, sha):
    if state["recovery"]:
        # On a resume the current red head may be a repair pushed just before the session died, never attached: it
        # joins the open recovery as its newest head, so its own one rerun is still available.
        recovery = state["recovery"]
        if full_sha(sha) not in recovery["heads"]:
            recovery["heads"].append(sha)
        return (f"open: recovery {recovery['first'][:7]} already open, {sha[:7]} is its newest head, "
                f"{len(recovery['attempts'])} of {BUDGET} attempts spent")
    state["recovery"] = {"first": full_sha(sha), "opened": now(), "heads": [sha], "attempts": [], "reruns": []}
    return f"open: recovery {sha[:7]} opened, 0 of {BUDGET} attempts spent"


def need_open(state):
    if not state["recovery"]:
        raise Refused("no recovery is open")
    return state["recovery"]


def attach(state, head):
    recovery = need_open(state)
    if full_sha(head) not in recovery["heads"]:
        recovery["heads"].append(head)
    return f"attach: {head[:7]} is part of recovery {recovery['first'][:7]}"


def reserve(state, kind, head=None):
    recovery = need_open(state)
    if kind not in KINDS:
        raise Refused(f"kind must be one of {', '.join(KINDS)}")
    if len(recovery["attempts"]) >= BUDGET:
        raise Refused(f"exhausted: {BUDGET} of {BUDGET} attempts spent on recovery {recovery['first'][:7]}")
    target = full_sha(head) if head else recovery["heads"][-1]
    if kind == "rerun":
        if target in recovery["reruns"]:
            raise Refused(f"the one flake rerun for {target[:7]} was already used")
        recovery["reruns"].append(target)
    n = len(recovery["attempts"]) + 1
    recovery["attempts"].append({"n": n, "kind": kind, "head": target, "reserved": now(), "result": None})
    return f"attempt {n} of {BUDGET}: {kind} on {target[:7]}"


def result(state, outcome):
    recovery = need_open(state)
    if outcome not in OUTCOMES:
        raise Refused(f"outcome must be one of {', '.join(OUTCOMES)}")
    if not recovery["attempts"] or recovery["attempts"][-1]["result"] is not None:
        raise Refused("no reserved attempt waits for a result")
    attempt = recovery["attempts"][-1]
    attempt["result"] = outcome
    if outcome == "green":
        return (f"result: attempt {attempt['n']} green; close the recovery with "
                f"`ci-recovery.py close {attempt['head'][:7]}...` (the full SHA)")
    left = BUDGET - len(recovery["attempts"])
    return f"result: attempt {attempt['n']} {outcome}; {left} attempt(s) left" + ("" if left else ", exhausted")


def close(state, head, run):
    recovery = need_open(state)
    if not descends(recovery["first"], full_sha(head), run):
        raise Refused(f"{head[:7]} does not descend from the recovery's first head {recovery['first'][:7]}")
    state["recovery"] = None
    return f"close: recovery {recovery['first'][:7]} closed on green {head[:7]}"


def show(state):
    recovery = state["recovery"]
    if not recovery:
        return "show: no open recovery"
    lines = [f"show: recovery {recovery['first'][:7]} opened {recovery['opened']}, "
             f"{len(recovery['attempts'])} of {BUDGET} attempts spent, heads "
             + ", ".join(h[:7] for h in recovery["heads"])]
    for a in recovery["attempts"]:
        lines.append(f"  {a['n']}. {a['kind']} on {a['head'][:7]} reserved {a['reserved']}: "
                     f"{a['result'] or 'no result (spent)'}")
    return "\n".join(lines)


def main(argv=None, state_path=None, run=subprocess.run):
    parser = argparse.ArgumentParser(description="One bounded CI recovery budget per red main.")
    parser.add_argument("--state", help=f"the state file (default {STATE.relative_to(ROOT).as_posix()})")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, arg in (("open", "sha"), ("attach", "head"), ("result", "outcome"), ("close", "head")):
        sub.add_parser(name).add_argument(arg)
    r = sub.add_parser("reserve")
    r.add_argument("kind", choices=KINDS)
    r.add_argument("--head", help="the head the attempt acts on (default: the newest attached head)")
    sub.add_parser("show")
    args = parser.parse_args(argv)
    path = Path(state_path or args.state or STATE)
    try:
        state = load(path)
        if args.command == "open":
            message = open_recovery(state, args.sha)
        elif args.command == "attach":
            message = attach(state, args.head)
        elif args.command == "reserve":
            message = reserve(state, args.kind, args.head)
        elif args.command == "result":
            message = result(state, args.outcome)
        elif args.command == "close":
            message = close(state, args.head, run)
        else:
            print(show(state))
            return 0
    except Refused as exc:
        print(f"refused: {exc}")
        return 1
    except Unreadable as exc:
        print(f"unreadable: {exc}")
        return 2
    save(path, state)  # only a request that succeeded changes the state
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
