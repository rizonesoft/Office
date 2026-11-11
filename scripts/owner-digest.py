#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The owner's one weekly email: what was built, where the plan stands, and what waits on the owner (D00 T03 §35).

    python scripts/owner-digest.py --dry-run    # print the email, attachment included; read no key, send nothing
    python scripts/owner-digest.py              # send it (the office-owner-digest task, Mondays)

The run never waits on the owner and never interrupts the owner (decision 32 of
docs/specs/2026-10-23-campaign-scope-design.md); this email is the one place the owner hears what only the owner can
do. It is built from the tree alone, so it costs no model and says the same thing whoever runs it:

- the run's state, from the run guard and the newest run file under docs/phase-runs/;
- CI for origin/main's head, from scripts/ci-status.py, as green, red (with the failing jobs), pending or unknown;
- the plan's totals, as `todo-graph.py query stats` counts them;
- every open section waiting on the owner (Needs operator, owner-decision, third-party or store-account) with its
  `**Owner action:**`, ordered by how many open sections wait behind it, largest first;
- the sections verified in the last seven days, from the dates in their receipts.

The body is plain text of at most BODY_LINES lines of at most WIDTH characters. When the waiting list does not fit,
the body keeps the first items and the whole list, every item with its owner action, goes in an attached text file
the last body line names. It goes through the transport of .conclave/automations/alert.py (the same sender and
recipient). Exit 0 sent or printed, 1 the send failed, 2 the tree cannot be read.
"""
from __future__ import annotations

import argparse
import datetime
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import textwrap

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import todo_graph  # noqa: E402  (the library sits beside this script, not on the path)

BODY_LINES = 120
WIDTH = 100
WINDOW_DAYS = 7
ATTACHMENT = "waiting-on-you.txt"
GUARD = "build/claude-campaign-guard.json"


def load_alert(root):
    """The automations' email transport, loaded from its file (it is not a package)."""
    spec = importlib.util.spec_from_file_location("office_alert", root / ".conclave" / "automations" / "alert.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wrap(text, indent=""):
    """`text` as lines of at most WIDTH characters, continued under `indent`."""
    return textwrap.wrap(text, WIDTH, initial_indent=indent, subsequent_indent=" " * len(indent),
                         break_long_words=True, break_on_hyphens=False) or [indent.rstrip()]


def git(root, *args):
    """git's output, or None when git fails, cannot start or outlives its minute: nothing here stops the email."""
    try:
        proc = subprocess.run([todo_graph.git(), "-C", str(root), *args], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


INSTANT = re.compile(r"\b(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z\b")


def reason(root, exc):
    """A failure as the email may say it: the error's kind and a repository-relative file, never a full path."""
    name = getattr(exc, "filename", None)
    try:
        where = Path(name).resolve().relative_to(root.resolve()).as_posix() if name else ""
    except ValueError:
        where = Path(name).name
    return f"{type(exc).__name__}{f' on {where}' if where else ''}"


# The plan


def totals(rows, root):
    """The counts `query stats` prints, from the same graph."""
    return {"total": sum(not r.withdrawn for r in rows.values()), "verified": sum(r.done for r in rows.values()),
            "ready": sum(todo_graph.disposition(r, rows) == 0 for r in rows.values()),
            "blocked": sum(todo_graph.disposition(r, rows) == 4 for r in rows.values()),
            "withdrawn": sum(r.withdrawn for r in rows.values()),
            "to_author": len(todo_graph.to_author(root, rows))}


def verified_since(root, rows, today):
    """(ref, title) of each section whose receipt is dated in the last WINDOW_DAYS days, newest first."""
    since = today - datetime.timedelta(days=WINDOW_DAYS - 1)
    found = []
    for row in rows.values():
        if not row.done or not row.receipt:
            continue
        try:
            data = json.loads((root / row.receipt).read_text(encoding="utf-8"))
            stamped = datetime.date.fromisoformat(data["date"])
        except (OSError, ValueError, KeyError, TypeError):
            continue
        if since <= stamped <= today:
            found.append((stamped, row.ref, row.title))
    return [(ref, title, stamped) for stamped, ref, title in sorted(found, reverse=True)]


def waiting(rows):
    """Each open, non-withdrawn section waiting on the owner, with its owner action and how many open sections wait
    behind it directly or through others, largest first, then in plan order."""
    open_rows = {ref: r for ref, r in rows.items() if not r.done and not r.withdrawn}
    behind = {ref: set() for ref in open_rows}
    for ref, row in open_rows.items():
        stack, seen = list(row.depends), set()
        while stack:
            dep = stack.pop()
            if dep in seen:
                continue
            seen.add(dep)
            if dep in behind:
                behind[dep].add(ref)
            if dep in rows:
                stack.extend(rows[dep].depends)
    order = {row.ref: i for i, row in enumerate(todo_graph.ordered(rows))}
    items = [{"ref": ref, "title": row.title, "needs": sorted(set(row.needs) & todo_graph.OWNER_NEEDS),
              "action": todo_graph.field(row.body, "Owner action", False), "behind": len(behind[ref])}
             for ref, row in open_rows.items() if set(row.needs) & todo_graph.OWNER_NEEDS]
    return sorted(items, key=lambda item: (-item["behind"], order[item["ref"]]))


# The run and CI


def run_state(root):
    """One line on the campaign: running, completed, parked, stopped by the operator, not running, or unknown."""
    try:
        guard_path = root / GUARD
        if guard_path.is_file():
            guard = json.loads(guard_path.read_text(encoding="utf-8"))
            return f"Running: run {guard.get('run_id', '?')}, phase {guard.get('phase', '?')}, {guard.get('run_file', '?')}"
        runs = [(latest_instant(path), path) for path in (root / "docs" / "phase-runs").glob("*.md")]
        if not runs:
            return "Not running: no campaign has run yet."
        newest = max(runs)[1]
        text = newest.read_text(encoding="utf-8")
        name = newest.relative_to(root).as_posix()
        ended = ending(text, name)
        if ended:
            return ended
        last = git(root, "log", "-1", "--format=%cs") or "unknown"
        return f"Not running: last commit {last}, newest run file {name}."
    except (OSError, ValueError) as exc:
        return f"Unknown: the run files cannot be read ({reason(root, exc)})."


def ending(text, name):
    """How a run file says its run ended, by the last of its ending events (a phase may close out and the campaign
    park after it, in the same file), or None when it records none."""
    events = []
    for m in re.finditer(r"^## Closeout run=", text, re.M):
        events.append((m.start(), f"Completed: {name} has its closeout."))
    for m in re.finditer(r"^PARKED (.*)$", text, re.M):
        events.append((m.start(), f"Parked: {m[1].strip()} ({name})"))
    for m in re.finditer(r"operator stop", text, re.I):
        events.append((m.start(), f"Stopped by the operator ({name})."))
    return max(events)[1] if events else None


def latest_instant(path):
    """When a run file was last written to, as the run itself records it: the latest UTC instant in it (every
    event carries one), else the file's own modification time. A phase chained later the same day sorts after."""
    found = INSTANT.findall(path.read_text(encoding="utf-8"))
    if found:
        return max(found)
    return datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def ci_state(root, runner=subprocess.run):
    """One line or more on CI for origin/main's head; never an exception, whatever the network does."""
    sha = git(root, "rev-parse", "origin/main")
    if not sha:
        return ["CI: unknown (origin/main cannot be read)."]
    try:
        proc = runner([sys.executable, str(root / "scripts" / "ci-status.py"), sha], capture_output=True, text=True,
                      timeout=300)
    except (OSError, subprocess.SubprocessError) as exc:
        return [f"CI: unknown for {sha[:7]} ({type(exc).__name__})."]
    lines = [line.strip() for line in (proc.stdout or "").splitlines() if line.strip()]
    if proc.returncode == 0:
        return [f"CI: green for {sha[:7]}."]
    if proc.returncode == 1:
        # Every detail line ci-status.py prints after its head line: failed, cancelled and timed-out jobs alike,
        # or its own word that the jobs could not be read.
        details = lines[1:]
        more = [f"  ... and {len(details) - 5} more"] if len(details) > 5 else []
        return [f"CI: red for {sha[:7]}.", *[f"  {line}" for line in details[:5]], *more]
    if proc.returncode == 3:
        return [f"CI: pending for {sha[:7]}."]
    reason = (lines[-1] if lines else (proc.stderr or "").strip().splitlines()[-1:] or ["no reason given"])
    return [f"CI: unknown for {sha[:7]} ({reason if isinstance(reason, str) else reason[0]})."]


# The email


def item_lines(item):
    head = f"- {item['ref']} {item['title']} [{', '.join(item['needs'])}]"
    if item["behind"]:
        many = item["behind"] != 1
        head += f", {item['behind']} open section{'s' if many else ''} wait{'' if many else 's'} behind it"
    return [*wrap(head), *wrap(item["action"] or "(no owner action written)", "  To do: ")]


def compose(root, rows, today, ci_lines, state):
    """(subject, body, attachments): the email, with the whole waiting list attached when the body cannot hold it."""
    count = totals(rows, root)
    items = waiting(rows)
    built = verified_since(root, rows, today)
    head = [f"Rizonesoft Office, week to {today.isoformat()}", "", *wrap(state),
            *[part for line in ci_lines for part in wrap(line.strip(), "  " if line.startswith("  ") else "")],
            *wrap(f"Plan: {count['verified']} of {count['total']} sections verified, {count['ready']} ready to run, "
                  f"{count['blocked']} blocked, {count['withdrawn']} withdrawn; {count['to_author']} TODO files still "
                  f"to author."), ""]
    if items:
        waiting_lines = [f"Waiting on you ({len(items)}):"]
        for item in items:
            waiting_lines += item_lines(item)
    else:
        waiting_lines = ["Nothing is waiting on you."]
    progress = ([f"Verified in the last {WINDOW_DAYS} days ({len(built)}):"]
                + [line for ref, title, stamped in built for line in wrap(f"- {ref} {title} ({stamped.isoformat()})")]
                if built else [f"Nothing was verified in the last {WINDOW_DAYS} days."])
    body = head + waiting_lines + [""] + progress
    attachments = []
    if len(body) > BODY_LINES:
        attachments = [(ATTACHMENT, "\n".join(waiting_lines) + "\n")]
        room = BODY_LINES - len(head) - 2
        kept, shown = [waiting_lines[0]], 0
        for item in items:
            lines = item_lines(item)
            if len(kept) + len(lines) > room // 2:
                break
            kept += lines
            shown += 1
        if items:
            kept.append(f"... and {len(items) - shown} more, every one with its steps, in the attached {ATTACHMENT}.")
        progress_room = BODY_LINES - len(head) - len(kept) - 1
        if len(progress) > progress_room:
            cut = progress[:max(progress_room - 1, 1)]
            cut.append(f"... and {len(built) - (len(cut) - 1)} more verified sections this week.")
            progress = cut
        body = head + kept + [""] + progress
    subject = f"Office weekly: {len(items)} waiting on you, {len(built)} verified this week"
    return subject, "\n".join(body) + "\n", attachments


def main(argv=None, root=ROOT, today=None, opener=None, runner=subprocess.run):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="print the email; read no key and send nothing")
    args = parser.parse_args(argv)
    try:
        rows = todo_graph.graph(root)
    except todo_graph.Refused as exc:
        print(f"owner-digest: the TODO tree cannot be read: {exc}", file=sys.stderr)
        return 2
    today = today or datetime.date.today()
    subject, body, attachments = compose(root, rows, today, ci_state(root, runner), run_state(root))
    alert = load_alert(root)
    if args.dry_run:
        print(f"To: {alert.TO}\nSubject: {subject}\n\n{body}", end="")
        for name, text in attachments:
            print(f"\n--- attachment {name} ---\n{text}", end="")
        return 0
    try:
        kwargs = {"attachments": attachments} if attachments else {}
        email_id = alert.send(alert.key(), subject, body, opener or alert.urllib.request.urlopen, **kwargs)
    except (alert.Refused, OSError, ValueError) as error:
        print(f"owner-digest not sent: {error}", file=sys.stderr)
        return 1
    print(f"owner digest sent to {alert.TO} (SMTP2GO email {email_id})")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
