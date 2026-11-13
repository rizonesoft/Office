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
- the sections verified since the same weekday a week ago, inclusive, from the dates in their receipts.

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
import posixpath
import re
import subprocess
import sys
import textwrap
import time
import uuid

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import todo_graph  # noqa: E402  (the library sits beside this script, not on the path)
import digest_state  # noqa: E402  (beside it too: the digest's delivery record, D00 T07 §3)
sys.path.insert(0, str(ROOT / "scripts"))
import campaign_guard  # noqa: E402  (beside this script: the run guard's own reader decides whether a run lives)

BODY_LINES = 120
WIDTH = 100
WINDOW_DAYS = 7
ATTACHMENT = "waiting-on-you.txt"
NOTICES_ATTACHMENT = "notices.txt"
PROGRESS_ATTACHMENT = "verified-this-week.txt"
PROGRESS_MIN = 8  # body lines the progress list keeps when both lists overflow (its header and a few sections)
NOTICE_LINES = 10  # summary lines of notices in the body; every notice is in full in the attachment
MARK_TRIES, MARK_PAUSE = 3, 2.0  # a delivered batch's mark is retried before it is left to the next settlement
# CREATE_NO_WINDOW on every launch, as .conclave/automations/run.py says every nested launch of a task carries it, so
# the Monday run opens no console on the owner's desktop.
NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


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
        proc = subprocess.run([todo_graph.git(), "-C", str(root), *args], capture_output=True, text=True, timeout=60,
                              creationflags=NO_WINDOW)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


# An absolute path of this machine: a drive or a share on Windows, a home, a mount or a system folder elsewhere. The
# email names none (D00 T03 §35: "no secret or path outside the repository"), whoever wrote the text: a run file, git,
# gh's error through ci-status.py.
# A path may hold spaces (a folder named in two words), so a match runs to the end of its clause: a quote, a closing
# bracket, a comma followed by a space, or the end of the line. Losing the rest of an error's clause is the price of
# never sending half a path.
OUTSIDE = re.compile(r"""(?ix)
    (?:\\\\\?\\)?[a-z]:[\\/](?:[^'"`)\r\n,]|,(?!\s))*                  # a drive path, with or without the long-path prefix
  | \\\\[^\s\\/'"`]+[\\/](?:[^'"`)\r\n,]|,(?!\s))*                      # a share path
  | (?<![\w.])/(?:home|Users|mnt|root|tmp|var|etc|opt|private)/(?:[^'"`)\r\n,]|,(?!\s))*
""")


def without_paths(text, root):
    """`text` with this repository's own absolute path made relative and every other absolute path named only as
    `<path outside the repository>`: the email's one guard for the class, applied to every line it sends."""
    def inside(m):
        # Only at a folder boundary, and only when the rest stays in the tree once `..` is resolved: a sibling such as
        # `<root>-backup` or `<root>\..\Private` is a path outside (D00 T03 §35 review round 7).
        rest = posixpath.normpath(m[1].replace("\\", "/"))
        return "<path outside the repository>" if rest == ".." or rest.startswith("../") else m[1]

    for spelling in {str(root), str(root).replace("\\", "/")}:
        text = re.sub(re.escape(spelling) + r"[\\/]((?:[^'\"`)\r\n,]|,(?!\s))*)", inside, text, flags=re.I)
    return OUTSIDE.sub("<path outside the repository>", text)


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
    return {"total": len(rows), "verified": sum(r.done for r in rows.values()),
            "ready": sum(todo_graph.disposition(r, rows) == 0 for r in rows.values()),
            "blocked": sum(todo_graph.disposition(r, rows) == 4 for r in rows.values()),
            "to_author": len(todo_graph.to_author(root, rows))}


def verified_since(root, rows, today, since=None):
    """(ref, title, date) of each section whose receipt is dated from `since` (inclusive; WINDOW_DAYS before today
    when not given) to today, newest first."""
    # From the same weekday a week ago, inclusive: a receipt records only its day, so a section stamped on a Monday
    # after that Monday's digest is in the next one. A Monday stamp before the digest can show twice, never not at all
    # (D00 T03 §35 review round 3; D00 T07 §3 reports exact periods from the last delivered digest).
    since = since or today - datetime.timedelta(days=WINDOW_DAYS)
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
    """Each open section waiting on the owner, with its owner action and how many open sections wait
    behind it directly or through others, largest first, then in plan order."""
    open_rows = {ref: r for ref, r in rows.items() if not r.done}
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


def run_state(root, config_dir=None):
    """One line on the campaign: running, completed, parked, stopped by the operator, not running, or unknown."""
    try:
        # A guard alone is not a live run: a crashed session leaves its guard for the launcher's handover. The guard's
        # own module says whether its session still shows life (D00 T07 §1).
        live = campaign_guard.liveness(str(root), config_dir=config_dir)
        if live is not None:
            kind, detail, guard = live  # one snapshot: the guard judged is the guard named
            if kind == "unknown":
                return f"Unknown: {detail}."
            run = f"run {guard.get('run_id', '?')}, phase {guard.get('phase', '?')}, {guard.get('run_file', '?')}"
            if kind == "running":
                return f"Running: {run} (last sign of life {detail})."
            return (f"Stalled since {detail}: {run}; its session shows no sign of life, and the next start of the "
                    f"campaign launcher takes the run over.")
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
    # A stop recorded as an event (`- <UTC> operator stop ...` in Critical events), never a mention in prose.
    for m in re.finditer(r"^- \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z operator stop\b", text, re.M | re.I):
        events.append((m.start(), f"Stopped by the operator ({name})."))
    return max(events)[1] if events else None


def latest_instant(path):
    """When a run file was last written to, as the run itself records it: the latest UTC instant in it (every
    event carries one), else the file's own modification time. A phase chained later the same day sorts after."""
    found = INSTANT.findall(path.read_text(encoding="utf-8"))
    if found:
        return max(found)
    return datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


# Task Scheduler's own success statuses: none of them is a failure (D00 T07 §4). 0x41301 is the digest's own task
# while it composes this email; 0x41303 is a task that has not run yet.
TASK_FINE = {0x0, 0x41300, 0x41301, 0x41302, 0x41303, 0x41325}
TASK_QUERY = ("$ErrorActionPreference = 'Stop'; @(Get-ScheduledTask | Where-Object TaskPath -eq '{folder}' | "
              "ForEach-Object {{ $i = $_ | Get-ScheduledTaskInfo; [pscustomobject]@{{ name = $_.TaskName; "
              "result = [uint32]$i.LastTaskResult; last = $i.LastRunTime.ToString('yyyy-MM-dd') }} }}) | "
              "ConvertTo-Json -Compress -AsArray")
TASK_SECONDS = 60


def task_state(root, runner=subprocess.run):
    """Lines on the scheduled tasks of `.conclave/automations/tasks.json`, asked of Task Scheduler itself and never
    of the task logs, since a task that fails to start writes none: one line for each task whose last result is a
    failure, one for each listed task that is not installed, and one saying the state is unknown when the query
    cannot be made or read. A healthy set gives no line."""
    try:
        manifest = json.loads((root / ".conclave" / "automations" / "tasks.json").read_text(encoding="utf-8"))
        folder, listed = str(manifest["folder"]), [str(task["name"]) for task in manifest["tasks"]]
        if not re.fullmatch(r"\\[A-Za-z0-9 _\\-]*\\", folder):
            raise ValueError("the task folder is not a Task Scheduler path")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"Scheduled tasks: unknown (tasks.json cannot be read: {reason(root, exc)})."]
    if not listed:
        return []
    try:
        done = runner(["pwsh", "-NoProfile", "-NonInteractive", "-Command", TASK_QUERY.format(folder=folder)],
                      capture_output=True, text=True, timeout=TASK_SECONDS, creationflags=NO_WINDOW)
    except (OSError, subprocess.SubprocessError) as exc:
        return [f"Scheduled tasks: unknown (Task Scheduler could not be asked: {type(exc).__name__})."]
    if done.returncode != 0:
        return [f"Scheduled tasks: unknown (the Task Scheduler query exited {done.returncode})."]
    try:
        rows = json.loads(done.stdout or "[]")
        found = {str(row["name"]): (int(row["result"]), str(row["last"])) for row in rows}
    except (ValueError, KeyError, TypeError):
        return ["Scheduled tasks: unknown (the Task Scheduler query's answer cannot be read)."]
    lines = []
    for name in listed:
        if name not in found:
            lines.append(f"Scheduled tasks: {name} is listed in tasks.json and is not installed; run "
                         f".conclave/automations/install.ps1.")
            continue
        result, last = found[name]
        if result not in TASK_FINE:
            lines.append(f"Scheduled tasks: {name} last ended with 0x{result:08X} on {last}; a result like this "
                         f"with no log under build/automations means it never reached its runner.")
    return lines

def ci_state(root, runner=subprocess.run):
    """One line or more on CI for origin/main's head; never an exception, whatever the network does."""
    # The head GitHub has now, not the one this clone last fetched: another clone may have pushed since.
    if git(root, "fetch", "--quiet", "origin", "main") is None:
        return ["CI: unknown (origin/main cannot be fetched)."]
    sha = git(root, "rev-parse", "origin/main")
    if not sha:
        return ["CI: unknown (origin/main cannot be read)."]
    try:
        proc = runner([sys.executable, str(root / "scripts" / "ci-status.py"), sha], capture_output=True, text=True,
                      timeout=300, creationflags=NO_WINDOW)
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


def item_lines(item, root):
    """An item as wrapped lines; every text is cleared of paths before it is wrapped (`without_paths`)."""
    head = f"- {item['ref']} {without_paths(item['title'], root)} [{', '.join(item['needs'])}]"
    if item["behind"]:
        many = item["behind"] != 1
        head += f", {item['behind']} open section{'s' if many else ''} wait{'' if many else 's'} behind it"
    action = without_paths(item["action"], root) if item["action"] else "(no owner action written)"
    return [*wrap(head), *wrap(action, "  To do: ")]


def notices_part(notices, root):
    """The body lines for the queued notices (D00 T03 §53) and the full text of each for the attachment. `notices` is
    the captured batch, or a string saying why the queue could not be read."""
    if isinstance(notices, str):
        return [*wrap(f"Notices: the queue could not be read ({without_paths(notices, root)}); none were marked "
                      f"reported."), ""], None
    if not notices:
        return [], None
    lines = [f"Notices since the last digest ({len(notices)}):"]
    shown = 0
    for notice in notices:
        repeat = " (an earlier digest did not deliver it)" if notice.get("attempts") else ""
        summary = wrap(f"- {notice.get('at', '?')} {without_paths(str(notice.get('sender', '?')), root)}: "
                       f"{without_paths(str(notice.get('subject', '')), root)}{repeat}")
        if len(lines) - 1 + len(summary) > NOTICE_LINES:
            break
        lines += summary
        shown += 1
    if shown < len(notices):
        lines += wrap(f"... and {len(notices) - shown} more; every notice in full is in the attached "
                      f"{NOTICES_ATTACHMENT}.")
    else:
        lines += wrap(f"Each notice in full is in the attached {NOTICES_ATTACHMENT}.")
    full = "\n\n".join(f"{n.get('at', '?')} {without_paths(str(n.get('sender', '?')), root)}: "
                       f"{without_paths(str(n.get('subject', '')), root)}\n\n"
                       f"{without_paths(str(n.get('body', '')), root)}" for n in notices) + "\n"
    return lines + [""], (NOTICES_ATTACHMENT, full)


def fit(head, blocks, room, noun, attachment):
    """(lines, cut): `head` and as many whole `blocks` as fit in `room` lines; when some do not, the shown blocks
    end with one line counting the rest and naming `attachment`."""
    whole = [head] + [line for block in blocks for line in block]
    if len(whole) <= room:
        return whole, False
    shown, used = [head], 1
    for count, block in enumerate(blocks):
        tail = wrap(f"... and {len(blocks) - count} more {noun}, in the attached {attachment}.")
        rest = blocks[count + 1:]
        if used + len(block) + (len(wrap(f"... and {len(rest)} more {noun}, in the attached {attachment}."))
                                if rest else 0) > room:
            return shown + tail, True
        shown += block
        used += len(block)
    return shown, False


def compose(root, rows, today, ci_lines, state, notices=(), token=None, unconfirmed=(), since=None, previous="",
            tasks=()):
    """(subject, body, attachments): the email, with the whole waiting list attached when the body cannot hold it,
    and the queued notices summarised after it with each one in full in an attachment (D00 T03 §53)."""
    count = totals(rows, root)
    items = waiting(rows)
    since_day = since or today - datetime.timedelta(days=WINDOW_DAYS)
    built = verified_since(root, rows, today, since_day)
    # Every text that came from outside this script is cleared of paths first, then wrapped and counted, so a path
    # is never split across lines and a placeholder never pushes a line past WIDTH (D00 T03 §35 review round 6).
    state, ci_lines = without_paths(state, root), [without_paths(line, root) for line in ci_lines]
    head = [f"Rizonesoft Office, week to {today.isoformat()}", "", *wrap(state),
            *[part for line in ci_lines for part in wrap(line.strip(), "  " if line.startswith("  ") else "")],
            *wrap(f"Plan: {count['verified']} of {count['total']} sections verified, {count['ready']} ready to run, "
                  f"{count['blocked']} blocked; {count['to_author']} TODO files still "
                  f"to author."), *(wrap(without_paths(previous, root)) if previous else []),
            *[part for line in tasks for part in wrap(without_paths(line, root))], ""]
    # Each list is a header and whole items (an item is every wrapped line of one entry), so a cut never splits an
    # entry and its count is of items, never lines (D00 T07 §2).
    waiting_blocks = [item_lines(item, root) for item in items]
    waiting_head = f"Waiting on you ({len(items)}):" if items else "Nothing is waiting on you."
    since = since_day.isoformat()
    progress_blocks = [wrap(f"- {ref} {without_paths(title, root)} ({stamped.isoformat()})") for ref, title, stamped in built]
    progress_head = f"Verified since {since} ({len(built)}):" if built else f"Nothing was verified since {since}."
    notice_lines, notice_file = notices_part(notices, root)
    if unconfirmed:
        # Claimed by an earlier digest whose delivery SMTP2GO can no longer confirm or deny (its history has passed):
        # their full text goes in the attachment, said to be possibly already received, so none is lost and the one
        # possible repeat is labelled (D00 T03 §53, reconciliation review 5).
        dates = sorted({str((n.get("claimed") or {}).get("at", "?"))[:10] for n in unconfirmed})
        notice_lines = notice_lines + wrap(
            f"{len(unconfirmed)} notice(s) of the digest of {', '.join(dates)} could not be confirmed delivered "
            f"(SMTP2GO no longer holds its record); each is in full in the attached {NOTICES_ATTACHMENT}, and may "
            f"already have reached you.") + [""]
        earlier = ("Could not be confirmed delivered by an earlier digest; it may already have reached you:\n\n"
                   + "\n\n".join(f"{n.get('at', '?')} {without_paths(str(n.get('sender', '?')), root)}: "
                                 f"{without_paths(str(n.get('subject', '')), root)}\n\n"
                                 f"{without_paths(str(n.get('body', '')), root)}" for n in unconfirmed) + "\n")
        notice_file = (NOTICES_ATTACHMENT, (notice_file[1] + "\n" if notice_file else "") + earlier)
    waiting_full = [waiting_head] + [line for block in waiting_blocks for line in block]
    progress_full = [progress_head] + [line for block in progress_blocks for line in block]
    body = head + waiting_full + [""] + notice_lines + progress_full
    attachments = []
    if len(body) > BODY_LINES:
        # The head and the notices part keep their room; the lists share the rest, the waiting list first (it is what
        # asks for the owner's action) but leaving the progress list PROGRESS_MIN lines. A cut list ends with a line
        # counting what its attachment adds, and the body's last line names every attachment.
        room = BODY_LINES - len(head) - 1 - len(notice_lines) - 2  # the blank line, and the closing pointer (2)
        progress_room = min(len(progress_full), PROGRESS_MIN)
        waiting_shown, waiting_cut = fit(waiting_head, waiting_blocks, room - progress_room,
                                         "waiting on you, every one with its steps", ATTACHMENT)
        progress_shown, progress_cut = fit(progress_head, progress_blocks, room - len(waiting_shown),
                                           "verified sections this week", PROGRESS_ATTACHMENT)
        named = []
        if waiting_cut:
            attachments.append((ATTACHMENT, "\n".join(waiting_full) + "\n"))
            named.append(ATTACHMENT)
        if progress_cut:
            attachments.append((PROGRESS_ATTACHMENT, "\n".join(progress_full) + "\n"))
            named.append(PROGRESS_ATTACHMENT)
        pointer = wrap(f"Every item is in full in the attached {' and '.join(named)}.") if named else []
        body = head + waiting_shown + [""] + notice_lines + progress_shown + ([""] if pointer else []) + pointer
    if notice_file:
        attachments.append(notice_file)    # The digest's own short id ends its subject, so SMTP2GO's activity log identifies this one email and no other
    # digest can stand as its delivery evidence (D00 T03 §53, reconciliation review 4).
    subject = (f"Office weekly: {len(items)} waiting on you, {len(built)} verified this week"
               + (f" ({token})" if token else ""))
    return subject, "\n".join(body) + "\n", attachments


def main(argv=None, root=ROOT, today=None, opener=None, runner=subprocess.run, sent=None, now=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="print the email; read no key and send nothing")
    parser.add_argument("--retry", action="store_true",
                        help="send again a digest that did not go out (the retry task); nothing else to do exits 0")
    args = parser.parse_args(argv)
    try:
        rows = todo_graph.graph(root)
    except todo_graph.Refused as exc:
        print(f"owner-digest: the TODO tree cannot be read: {exc}", file=sys.stderr)
        return 2
    today = today or datetime.date.today()
    alert = load_alert(root)
    if args.dry_run:
        try:
            since = digest_state.period_start(digest_state.load(root), today)
        except digest_state.StateError:
            since = None
        try:
            batch = alert.pending_notices(str(root)) + alert.claimed_notices(str(root))
            unconfirmed = alert.unconfirmed_notices(str(root))
        except alert.Refused as error:
            batch, unconfirmed = str(error), []
        subject, body, attachments = compose(root, rows, today, ci_state(root, runner), run_state(root), batch,
                                             uuid.uuid4().hex[:8], unconfirmed, since=since,
                                             tasks=task_state(root, runner))
        print(f"To: {alert.TO}\nSubject: {subject}\n\n{body}", end="")
        for name, text in attachments:
            print(f"\n--- attachment {name} ---\n{text}", end="")
        return 0
    # One digest run at a time: the weekly run and the retry share this lock, and a run that finds it held sends
    # nothing (D00 T07 §3).
    lock = digest_state.Lock(root)
    if not lock.acquire():
        print("owner-digest: another digest run holds the lock; nothing sent")
        return 0
    try:
        return deliver(args, root, rows, today, alert, opener, runner, sent,
                       now or datetime.datetime.now(datetime.timezone.utc))
    finally:
        lock.release()


def deliver(args, root, rows, today, alert, opener, runner, sent, now):
    """Under the lock: settle the attempt in flight, then send the digest when one is due, recording the attempt
    before the send and the delivery after it (D00 T07 §3)."""
    try:
        state = digest_state.load(root)
    except digest_state.StateError as error:
        print(f"owner-digest: the delivery record is broken, so nothing is sent: {error}", file=sys.stderr)
        return 2

    def asked(subject, since):  # the same opener as the send, so a test's fake answers both
        return alert.delivery(alert.key(), subject, since, opener or alert.urllib.request.urlopen)
    ask = sent or asked

    def stored():
        try:
            digest_state.save(root, state)
            return True
        except OSError as error:
            print(f"owner-digest: the delivery record cannot be written: {error}", file=sys.stderr)
            return False
    def asked_with_id(subject, since):  # the digest's own settlement keeps SMTP2GO's id of a confirmed delivery
        return alert.delivery(alert.key(), subject, since, opener or alert.urllib.request.urlopen, with_id=True)
    settled = digest_state.settle(state, sent or asked_with_id, now, alert.YOUNG_MINUTES, alert.SETTLE_DAYS,
                                  alert.Refused)
    for line in settled:
        print(f"owner-digest: {line}")
    if settled and not stored():
        return 1
    attempt = state["attempt"]
    unsettled = bool(attempt and attempt["stage"] in ("sending", "unsure"))
    owed = bool(attempt and attempt["stage"] == "failed") or bool(state["missed_from"]) or state["due"]
    if args.retry and not owed:
        # Nothing failed: a delivered digest, or one still being settled (its period is never sent again; the log
        # decides it at the next run). Nothing is sent and nothing changed.
        return 0
    if not args.retry and not state["due"]:
        if digest_state.sent_today(state, today):
            # A relaunch of the weekly run whose digest already went out today, or may have (the scheduler restarts
            # a task that exited non-zero): one email a week, so nothing new is due. A failed attempt is still owed.
            if not owed:
                print("owner-digest: today's digest already went out or is being settled; nothing is sent again")
                return 0
        else:
            # Owed from here until it is sent, so any failure before the send leaves the retry a digest to send.
            state["due"] = True
            if not stored():
                return 1
    if unsettled:
        digest_state.supersede(state)  # the weekly digest goes out; the unsettled one is settled on its own
    if digest_state.tries_today(state, today) >= digest_state.MAX_TRIES:
        print(f"owner-digest: {digest_state.MAX_TRIES} sends today already; the retry sends it tomorrow")
        return 0
    # The batch is captured here, before the email is composed, and claimed before it is sent: only these are marked
    # reported, once the send succeeded, so a notice recorded meanwhile, a dry run and a refused send leave notices
    # pending, and a delivered digest that then cannot mark its batch is not sent again while SMTP2GO's log can
    # still confirm it (D00 T03 §53); past the log's history it is repeated once, labelled (D00 T03 §56).
    try:
        # A claim no digest confirmed: SMTP2GO's log says whether that digest went out. Sent, it is marked; not
        # sent, or the log cannot be read, it is sent again, marked as a possible repeat (D00 T03 §53).
        claims = alert.settle_claims(str(root), ask)
        if any(claims.values()):
            print(f"earlier claims: {claims['confirmed']} confirmed sent, {claims['released']} not sent, "
                  f"{claims['kept']} kept to ask again, {claims['expired']} past the log (sent again in full, labelled)")
        batch = alert.pending_notices(str(root))
        unconfirmed = alert.unconfirmed_notices(str(root))
    except alert.Refused as error:
        batch, unconfirmed = str(error), []
    since = digest_state.period_start(state, today)
    doubtful = list(state["unconfirmed"])
    previous = ("" if not doubtful else
                f"The digest{'s' if len(doubtful) > 1 else ''} of "
                f"{', '.join(sorted({u['at'][:10] for u in doubtful}))} could not be confirmed delivered: SMTP2GO "
                f"no longer holds {'their records' if len(doubtful) > 1 else 'its record'}, so "
                f"{'they' if len(doubtful) > 1 else 'it'} may not have reached you (covering "
                f"{'; '.join(f'{u['start']} to {u['end']}' for u in doubtful)}).")
    digest_id = uuid.uuid4().hex
    subject, body, attachments = compose(root, rows, today, ci_state(root, runner), run_state(root), batch,
                                         digest_id[:8], unconfirmed, since=since, previous=previous,
                                         tasks=task_state(root, runner))
    ids = ([n["id"] for n in batch] if isinstance(batch, list) else []) + [n["id"] for n in unconfirmed]
    if ids:
        try:
            alert.claim_notices(ids, digest_id, str(root), subject)
        except alert.Refused as error:  # the queue cannot be written, so the batch could never be marked: not sent
            print(f"owner-digest not sent: the notices cannot be claimed: {error}", file=sys.stderr)
            return 1
    # Recorded before the send: a run killed after it leaves `sending`, which the next run settles by the log.
    state["attempt"] = {"token": digest_id[:8], "subject": subject, "start": since.isoformat(),
                        "end": today.isoformat(), "at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "stage": "sending"}
    state["due"] = False
    digest_state.count_try(state, today)
    if not stored():
        if ids:
            release(alert, digest_id, root)
        print("owner-digest not sent: the attempt could not be recorded first", file=sys.stderr)
        return 1
    try:
        kwargs = {"attachments": attachments} if attachments else {}
        email_id = alert.send(alert.key(), subject, body, opener or alert.urllib.request.urlopen, **kwargs)
    except (alert.Refused, OSError, ValueError) as error:
        if digest_state.definite(error, alert.Refused):
            state["attempt"]["stage"] = "failed"
            print(f"owner-digest not sent: {error}; the retry sends it again", file=sys.stderr)
            if ids:
                release(alert, digest_id, root)
        else:  # it may have gone out: SMTP2GO's log settles it, and its notices stay claimed for §53's settlement
            state["attempt"]["stage"] = "unsure"
            print(f"owner-digest: the send may have gone out ({type(error).__name__}: {error}); SMTP2GO's log "
                  f"settles it before anything is sent again", file=sys.stderr)
        stored()
        return 1
    print(f"owner digest sent to {alert.TO} (SMTP2GO email {email_id})")
    digest_state.deliver(state, email_id or "", True, state["attempt"]["at"])
    if previous:
        state["unconfirmed"] = [u for u in state["unconfirmed"] if u not in doubtful]  # named in a delivered digest
    stored()  # a failed write leaves `sending`, which the next run settles by the log: never a second send
    if ids:
        try:  # first the proof of delivery, in a second store, so a mark that fails cannot cause a repeat
            alert.record_sent(digest_id, email_id or "")
        except OSError as error:
            print(f"owner-digest: the delivery evidence could not be written: {error}", file=sys.stderr)
        try:
            for attempt_no in range(MARK_TRIES):  # a transient refusal (a lock, a scanner holding the file) passes
                try:
                    marked = alert.mark_reported(ids, str(root))
                    break
                except alert.Refused:
                    if attempt_no == MARK_TRIES - 1:
                        raise
                    time.sleep(MARK_PAUSE)
            alert.clear_sent(digest_id)
            print(f"marked {marked} notice(s) reported")
        except alert.Refused as error:  # delivered but unconfirmed: the next digest sends them again, so marked
            print(f"owner-digest: the delivered notices could not be marked; the next digest repeats them, marked as "
                  f"possible repeats: {error}", file=sys.stderr)
            return 1
    return 0


def release(alert, digest_id, root):
    try:
        alert.release_claim(digest_id, str(root))
    except alert.Refused as error:  # they stay claimed; the next digest releases and sends them
        print(f"owner-digest: the notices stay claimed until the next digest: {error}", file=sys.stderr)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
