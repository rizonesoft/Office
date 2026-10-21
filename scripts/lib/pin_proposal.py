"""Propose a dependency pin bump on its own branch, or announce a machine update once, for the pin automations.

`propose` never touches the operator's checkout or main. It adds a temporary git worktree on a new branch from main,
applies the rewrite there, runs the caller's checks, commits, removes the worktree and emails the operator which branch
to merge. A proposal is finished only when the ref `refs/office-pin/<key>` exists, written after the checks passed,
the commit landed and the email went; a branch without it is an unfinished attempt that the next run discards and
redoes, and a branch that cannot be discarded fails the run.

`notice` emails an "update available" message once per key (the key names the new version or state) and records it
as the ref `refs/office-notice/<key>`; deleting the ref sends it again.

Both send through `.conclave/automations/alert.py` (the same vault key, SMTP2GO path and From line as the failure
alerts). Ported from RectoPDF's `scripts/lib/pin_proposal.py` (2026-10-21), with Office's solution build as the check.

Stdlib only.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW: a scheduled run opens no console
PIN_REF = "refs/office-pin/{key}"
NOTICE_REF = "refs/office-notice/{key}"
# Written beside each worktree before it is created: the only proof that a leftover worktree is this automation's.
OWNER = "office-pin-owner.json"


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


def solutions(tree):
    """The solution files a proposal builds: every .sln or .slnx outside build/."""
    tree = Path(tree)
    return sorted(p for p in tree.rglob("*.sln*")
                  if p.suffix in (".sln", ".slnx") and "build" not in p.relative_to(tree).parts)


def build_problems(tree, build=subprocess.run):
    """The problems from `dotnet build` of each solution in the worktree; empty when every one passed, or there is
    none yet (until D03 T01 §12 creates the solution)."""
    problems = []
    for solution in solutions(tree):
        result = build(["dotnet", "build", str(solution), "-c", "Release"], cwd=tree, capture_output=True, text=True,
                       creationflags=NO_WINDOW)
        if result.returncode != 0:
            problems.append(f"dotnet build {solution.relative_to(tree).as_posix()} failed: {(result.stdout or '')[-400:]}")
    return problems


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


def _claim(tree, branch):
    """Record, before the worktree exists, that this automation creates it for this branch."""
    marker = Path(tree).parent / OWNER
    tmp = marker.with_suffix(".tmp")
    tmp.write_text(json.dumps({"branch": branch, "worktree": str(Path(tree).resolve())}), encoding="utf-8")
    os.replace(tmp, marker)


def _ours(path, branch):
    """Whether this automation created the worktree at path for this branch: its owner record says exactly that."""
    try:
        doc = json.loads((Path(path).parent / OWNER).read_text(encoding="utf-8"))
        return (isinstance(doc, dict) and doc.get("branch") == branch
                and Path(str(doc.get("worktree"))).resolve() == Path(path).resolve())
    except (OSError, ValueError):
        return False


def _drop(branch, root):
    """Delete an unfinished proposal branch; the problems, empty when it is gone.

    A run killed mid-proposal leaves its worktree with the branch checked out, and git will not delete a checked-out
    branch, so that worktree is removed first, but only when its owner record (written before the worktree was
    created) names this branch and that path. Any other worktree is the operator's, and is never removed."""
    git("worktree", "prune", cwd=root, check=False)
    problems = []
    for path in _worktrees_on(branch, root):
        if not _ours(path, branch):
            problems.append(f"{branch} is checked out at {path}, which this automation did not create")
            continue
        removed = git("worktree", "remove", "--force", path, cwd=root, check=False)
        if removed.returncode != 0:
            problems.append(f"could not remove the abandoned worktree {path}: {(removed.stderr or removed.stdout).strip()}")
    if problems:
        return problems
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
        _claim(tree, branch)
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
