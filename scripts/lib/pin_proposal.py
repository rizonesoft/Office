# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Propose a dependency pin bump on its own branch, or announce a machine update once, for the pin automations.

`propose` never touches the operator's checkout or main. It adds a temporary git worktree on a new branch from main,
applies the rewrite there, runs the caller's checks, commits, removes the worktree and emails the operator which branch
to merge. A proposal is finished only when the ref `refs/office-pin/<key>` exists, written after the checks passed,
the commit landed and the email went; a branch without it is an unfinished attempt that the next run discards and
redoes, and a branch that cannot be discarded fails the run.

`notice` emails an "update available" message once per key (the key names the new version or state) and records it
as the ref `refs/office-notice/<key>`; deleting the ref sends it again.

Both send through `.conclave/automations/alert.py` (the same vault key, SMTP2GO path and From line as the failure
alerts). Ported from RectoPDF's `scripts/lib/pin_proposal.py` (2026-10-21); each caller supplies its own checks.

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


def notify(root, subject, body, dry_run=False, alert_module=None):
    """Email the operator through the automations' sender."""
    if dry_run:
        print(f"would email: {subject}\n{body}")
        return
    if alert_module is None:
        sys.path.insert(0, str(Path(root) / ".conclave" / "automations"))
        import alert as alert_module
    alert_module.send(alert_module.key(), subject, body)


def notice(*, root, key, subject, body, dry_run=False, mail=notify):
    """Email an "update available" notice once per key; return 0, or 1 when it could not be sent or recorded."""
    root = Path(root)
    done = NOTICE_REF.format(key=key)
    if git("rev-parse", "--verify", "--quiet", done, cwd=root, check=False).returncode == 0:
        print(f"{key} was announced before ({done})")
        return 0
    try:
        mail(root, subject, body, dry_run)
    except Exception as exc:  # any send failure: the operator was not told, so the next run tries again
        print(f"could not email the notice ({type(exc).__name__}: {exc}); the next run will try again", file=sys.stderr)
        return 1
    if dry_run:
        return 0
    marked = git("update-ref", done, "main", cwd=root, check=False)
    if marked.returncode != 0:
        print(f"emailed {key}, but could not record {done}: {(marked.stderr or marked.stdout).strip()}", file=sys.stderr)
        return 1
    print(f"announced {key} to the operator")
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


def propose(*, root, key, branch, rewrite, checks, message, subject, body, dry_run=False, mail=notify):
    """Propose a change; return the process exit code (0 proposed or already proposed, 1 failed or dry run).

    rewrite(tree) changes files in the worktree and returns the repository-relative paths it changed, or an empty
    list when main already holds the target (nothing to propose). checks(tree) returns problems; empty means commit.
    message is the commit message as a list of paragraphs, and body is a function of the commit id, so the email can
    name it.
    """
    root = Path(root)
    done = PIN_REF.format(key=key)
    if git("rev-parse", "--verify", "--quiet", done, cwd=root, check=False).returncode == 0:
        print(f"{key} was proposed and emailed before ({done})")
        return 0
    leftover = git("rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", cwd=root, check=False).returncode == 0
    if dry_run:
        print((f"would discard the unfinished {branch}, then " if leftover else "would ")
              + f"create {branch} from main, apply the change, check it, commit, and email the operator")
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
        print(f"could not email the proposal ({type(exc).__name__}: {exc}); "
              + (f"{branch} was removed so the next run proposes it again" if not left else "; ".join(left)),
              file=sys.stderr)
        return 1
    marked = git("update-ref", done, commit, cwd=root, check=False)
    if marked.returncode != 0:
        print(f"proposed and emailed {key}, but could not record {done}: {(marked.stderr or marked.stdout).strip()}; "
              "the next run will propose it again", file=sys.stderr)
        return 1
    print(f"proposed {key} on {branch} ({commit[:12]}) and emailed the operator")
    return 0
