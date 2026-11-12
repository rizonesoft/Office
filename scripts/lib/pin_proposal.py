# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Propose a dependency pin bump on its own branch, or announce a machine update once, for the pin automations.

`propose` never touches the operator's checkout or main. It adds a temporary git worktree on a new branch from main,
applies the rewrite there, runs the caller's checks, commits, removes the worktree and records for the owner digest
which branch to merge. A proposal is finished only when the ref `refs/office-pin/<key>` exists, written after the checks passed,
the commit landed and the notice was recorded; a branch without it is an unfinished attempt that the next run discards and
redoes, and a branch that cannot be discarded fails the run.

`notice` records an "update available" message once per key (the key names the new version or state) and marks it
as the ref `refs/office-notice/<key>` once it is recorded; deleting the ref records it again.

Both queue their message for the weekly owner digest through `.conclave/automations/alert.py` (`record`; decision 32
of the campaign scope record: one weekly email and no other interruption, D00 T03 §53).
Ported from RectoPDF's `scripts/lib/pin_proposal.py` (2026-10-21); each caller supplies its own checks.

Stdlib only.
"""
from pathlib import Path
import subprocess
import sys
import tempfile

NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW: a scheduled run opens no console
PIN_REF = "refs/office-pin/{key}"
NOTICE_REF = "refs/office-notice/{key}"


def git(*args, cwd, check=True):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", creationflags=NO_WINDOW)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {(result.stderr or result.stdout).strip()}")
    return result


def main_file(root, rel):
    """A file's text on main: main is what a proposal changes, so main, never the checkout, is the baseline."""
    shown = git("show", f"main:{rel}", cwd=root, check=False)
    if shown.returncode != 0:
        raise ValueError(f"cannot read {rel} on main: {(shown.stderr or shown.stdout).strip()}")
    return shown.stdout


def record(root, subject, body, dry_run=False, alert_module=None, sender="pin automations"):
    """Queue the notice for the weekly owner digest through the automations' alert module (decision 32: one weekly
    email and no other interruption; D00 T03 §53). Raises when it cannot be recorded, so a caller's mark is never
    written for a notice that was not kept."""
    if dry_run:
        print(f"would record for the weekly digest: {subject}\n{body}")
        return
    if alert_module is None:
        import importlib.util
        path = Path(root) / ".conclave" / "automations" / "alert.py"
        spec = importlib.util.spec_from_file_location("office_alert", path)
        alert_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(alert_module)
    alert_module.record_notice(sender, subject, body, str(root))


def notice(*, root, key, subject, body, dry_run=False, mail=record):
    """Record an "update available" notice once per key; return 0, or 1 when it could not be recorded or marked."""
    root = Path(root)
    done = NOTICE_REF.format(key=key)
    if git("rev-parse", "--verify", "--quiet", done, cwd=root, check=False).returncode == 0:
        print(f"{key} was announced before ({done})")
        return 0
    try:
        mail(root, subject, body, dry_run)
    except Exception as exc:  # not recorded: the operator will not be told, so no mark, and the next run tries again
        print(f"could not record the notice ({type(exc).__name__}: {exc}); the next run will try again", file=sys.stderr)
        return 1
    if dry_run:
        return 0
    marked = git("update-ref", done, "main", cwd=root, check=False)
    if marked.returncode != 0:
        print(f"recorded {key}, but could not mark {done}: {(marked.stderr or marked.stdout).strip()}", file=sys.stderr)
        return 1
    print(f"recorded {key} for the weekly digest")
    return 0


def _worktrees_on(branch, root):
    """The paths of the worktrees that have the branch checked out."""
    listed = git("worktree", "list", "--porcelain", cwd=root, check=False).stdout
    paths, path = [], None
    for line in listed.splitlines():
        if line.startswith("worktree "):
            path = line[len("worktree "):]
        elif line == f"branch refs/heads/{branch}" and path:
            paths.append(path)
    return paths


def _drop(branch, root):
    """Delete an unfinished proposal branch; the problems, empty when it is gone.

    A worktree whose folder is gone (a killed run whose temporary folder was cleaned up) is pruned first. A worktree
    that still has the branch checked out is never removed here, whoever made it: it may hold someone's work, and no
    record can prove whose it is now. The run fails instead, naming the worktree and the commands that release it, so
    the failure alert asks the operator to look before anything is deleted."""
    git("worktree", "prune", cwd=root, check=False)
    held = _worktrees_on(branch, root)
    if held:
        return [f"{branch} is checked out at {path}; if nothing there is wanted, run: git worktree remove --force "
                f"\"{path}\" && git branch -D {branch}" for path in held]
    result = git("branch", "-D", branch, cwd=root, check=False)
    return [] if result.returncode == 0 else [f"could not delete {branch}: {(result.stderr or result.stdout).strip()}"]


def propose(*, root, key, branch, rewrite, checks, message, subject, body, dry_run=False, mail=record):
    """Propose a change; return the process exit code (0 proposed or already proposed, 1 failed or dry run).

    rewrite(tree) changes files in the worktree and returns the repository-relative paths it changed, or an empty
    list when main already holds the target (nothing to propose). checks(tree) returns problems; empty means commit.
    message is the commit message as a list of paragraphs, and body is a function of the commit id, so the notice can
    name it.
    """
    root = Path(root)
    done = PIN_REF.format(key=key)
    if git("rev-parse", "--verify", "--quiet", done, cwd=root, check=False).returncode == 0:
        print(f"{key} was proposed and recorded before ({done})")
        return 0
    leftover = git("rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", cwd=root, check=False).returncode == 0
    if dry_run:
        print((f"would discard the unfinished {branch}, then " if leftover else "would ")
              + f"create {branch} from main, apply the change, check it, commit, and record it for the owner digest")
        return 1
    if leftover:
        left = _drop(branch, root)
        if left:
            print("an unfinished proposal is in the way; repair by hand:\n- " + "\n- ".join(left), file=sys.stderr)
            return 1
        print(f"discarded the unfinished {branch} from an earlier run")
    outcome, commit, cleanup = None, None, []
    scratch = root / "build" if (root / "build").is_dir() else None
    with tempfile.TemporaryDirectory(prefix="office-pin-", dir=scratch) as tmp:
        tree = Path(tmp) / "tree"
        git("worktree", "add", "-b", branch, str(tree), "main", cwd=root)
        try:
            changed = rewrite(tree)
            if not changed:
                print(f"main already holds the target for {key}; nothing to propose")
                outcome = 0
            else:
                problems = checks(tree)
                if problems:
                    print("checks failed, nothing proposed:\n- " + "\n- ".join(problems), file=sys.stderr)
                    outcome = 1
                else:
                    git("add", *changed, cwd=tree)
                    git("commit", "-q", *sum((["-m", part] for part in message), []), cwd=tree)
                    commit = git("rev-parse", "HEAD", cwd=tree).stdout.strip()
        finally:
            removed = git("worktree", "remove", "--force", str(tree), cwd=root, check=False)
            if removed.returncode != 0:
                cleanup.append(f"could not remove the worktree {tree}: {(removed.stderr or removed.stdout).strip()}")
            if commit is None:
                cleanup += _drop(branch, root)
    if cleanup:
        # A leftover branch would be discarded and redone, but a leftover worktree blocks the next run.
        print("cleanup failed; repair by hand before the next run:\n- " + "\n- ".join(cleanup), file=sys.stderr)
        return 1
    if outcome is not None:
        return outcome
    try:
        mail(root, subject, body(commit), dry_run)
    except Exception as exc:  # any send failure: the operator was not told, so the proposal is not finished
        left = _drop(branch, root)
        print(f"could not record the proposal ({type(exc).__name__}: {exc}); "
              + (f"{branch} was removed so the next run proposes it again" if not left else "; ".join(left)),
              file=sys.stderr)
        return 1
    marked = git("update-ref", done, commit, cwd=root, check=False)
    if marked.returncode != 0:
        print(f"proposed and recorded {key}, but could not mark {done}: {(marked.stderr or marked.stdout).strip()}; "
              "the next run will propose it again", file=sys.stderr)
        return 1
    print(f"proposed {key} on {branch} ({commit[:12]}) and recorded it for the owner digest")
    return 0
