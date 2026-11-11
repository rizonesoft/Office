#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Accept or reject a worker's change as one complete step that never loses a byte (D00 T03 §34).

    python scripts/packet.py begin --name "<ref>, <packet>" --path <file or folder> [--path ...]
    python scripts/packet.py show                         # every changed path, marked, the whole change, its digest
    python scripts/packet.py show --stage --snapshot <d>  # stage exactly the reviewed bytes and close the packet
    python scripts/packet.py reject                       # set the whole tree aside in a named stash, then close

`begin` refuses (exit 2) while the working tree holds any change, untracked files included, so the main loop commits
its own edits first and what `show` reads afterwards is the worker's, or an edit the owner saved meanwhile, which
`show` marks as outside. It records the packet's name, paths and `HEAD` in `build/packet.json`.

`show` lists every path changed since `begin` (staged, unstaged and untracked, each new file by itself, both sides of
a rename) with an `inside` or `outside` mark, then prints the change in three parts: staged (`begin`'s `HEAD` to the
index), unstaged (the index to the working tree) and the full text of every untracked file, and last a
`snapshot: sha256:<digest>` line over the bytes each changed path holds in the working tree. It exits 0 only when
every changed path is inside the packet's paths and `HEAD` is still the commit `begin` recorded; 1 naming each
outside path, a moved `HEAD` (a worker committed) or an empty change.

`show --stage --snapshot <digest>` stages, only when `show` would exit 0 and the tree still holds the reviewed
snapshot, exactly the bytes it read and hashed (`git hash-object --stdin --path`, `git update-index --cacheinfo`), so
a save landing after the review is never staged; a path whose file changed after that read is named and left
unstaged. Then it closes the packet. Otherwise the index is left as it was.

`reject` refuses (exit 1, nothing changed) when `HEAD` moved, naming the commits. Otherwise it builds a stash of the
whole tree (index, tracked and untracked files, in `git stash push --include-untracked`'s shape) from the bytes it
reads, without touching the tree, stores it with `git stash store` as `rejected packet: <name>`, and then returns
each changed path to `HEAD`, checking right before each write that the path still holds the bytes the stash
captured: a path saved meanwhile is kept on disk and named, and the index goes back to `HEAD` only while it is still
the one the stash captured (an index staged after the capture is kept and named). Removals run deepest first and
writes after them, so a folder that took a tracked file's name is emptied before the file returns. Its progress is recorded in `build/packet.json`, so a
`reject` that stopped part way resumes on the next call with the same stash. It closes the packet once every path
is settled and the tree holds no change; kept saves are named, and a further `reject` sets them aside too.

Nothing is ever discarded or taken back out of a stash by this command: a changed path may be the owner's.

Exit 0 done, 1 the change is not acceptable as it stands or the rejection is not finished, 2 refused (a tree with
changes at `begin`, no open packet, a packet already open, a bad path, a missing or stale `--snapshot`), 3 git or
the file system failed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from todo_graph import git as git_path  # noqa: E402  the absolute git, never one in the working directory

STATE = "build/packet.json"
STASH_MESSAGE = "rejected packet: {name}"


class Refused(Exception):
    """Exit 2: the command cannot run in this state."""


class GitFailed(Exception):
    """Exit 3: git or the file system failed."""


def run_git(repo, *args, data=None, env=None):
    """git's output as bytes; `data` is fed to its standard input."""
    proc = subprocess.run([git_path(), "-C", str(repo), *args], input=data, capture_output=True,
                          env={**os.environ, **env} if env else None)
    if proc.returncode != 0:
        raise GitFailed(f"git {' '.join(args)} failed: {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout


def text(repo, *args, env=None):
    return run_git(repo, *args, env=env).decode("utf-8", "replace")


def names(repo, *args, env=None):
    return [p for p in text(repo, *args, "-z", env=env).split("\0") if p]


def head(repo):
    return text(repo, "rev-parse", "HEAD").strip()


def dirty(repo):
    """Every path `git status` reports, untracked files listed one by one, both sides of a rename."""
    parts, entries, i = text(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0"), [], 0
    while i < len(parts):
        entry = parts[i]
        i += 1
        if not entry:
            continue
        entries.append(entry[3:])
        if entry[0] in "RC":  # a rename or copy carries its source as the next field
            entries.append(parts[i])
            i += 1
    return entries


def packet_path(value):
    """A packet path as a normalised repository-relative POSIX path; refuse one that leaves the repository."""
    raw = value.replace("\\", "/").strip()
    if not raw or raw.startswith("/") or (len(raw) > 1 and raw[1] == ":"):
        raise Refused(f"packet path must be relative to the repository: {value!r}")
    parts = [p for p in PurePosixPath(raw).parts if p != "."]
    if not parts or ".." in parts:
        raise Refused(f"packet path must name a file or folder inside the repository: {value!r}")
    normal = PurePosixPath(*parts).as_posix()
    if normal == ".git" or normal.startswith(".git/"):
        raise Refused(f"packet path may not be git's own folder: {value!r}")
    return normal


def inside(path, paths):
    return any(path == p or path.startswith(p + "/") for p in paths)


def load(repo):
    state = repo / STATE
    if not state.is_file():
        raise Refused(f"no packet is open ({STATE} is missing); run begin first")
    try:
        data = json.loads(state.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise Refused(f"{STATE} is unreadable: {exc}") from None
    if not (isinstance(data, dict) and isinstance(data.get("name"), str) and isinstance(data.get("head"), str)
            and isinstance(data.get("paths"), list) and data["paths"]):
        raise Refused(f"{STATE} is malformed")
    return data


def atomic_write(target, raw):
    """Temporary file in the destination folder, then os.replace: a reader never sees half a file."""
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".packet-", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
        os.replace(tmp, target)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def save(repo, data):
    atomic_write(repo / STATE, (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def close(repo):
    (repo / STATE).unlink()


def read_bytes(repo, path):
    """A path's working-tree bytes, or None when no file is there (absent, or a folder now holds the name)."""
    target = repo / path
    if target.is_dir():
        return None
    try:
        return target.read_bytes()
    except (FileNotFoundError, NotADirectoryError):  # absent, or a file holds one of its parents' names
        return None


def sha(raw):
    return None if raw is None else hashlib.sha256(raw).hexdigest()


def changed_paths(repo, base):
    """Every path changed since `base`: base to index, index to working tree (both sides of a rename), untracked."""
    staged = names(repo, "diff", "--cached", "--name-only", "--no-renames", base)
    unstaged = names(repo, "diff", "--name-only", "--no-renames")
    untracked = names(repo, "ls-files", "--others", "--exclude-standard")
    return sorted(set(staged + unstaged + untracked)), untracked


def capture(repo, paths):
    """Each path's working-tree bytes, read once."""
    return {path: read_bytes(repo, path) for path in paths}


def digest(captured):
    lines = "".join(f"{path}\0{sha(raw) or 'absent'}\n" for path, raw in sorted(captured.items()))
    return "sha256:" + hashlib.sha256(lines.encode("utf-8")).hexdigest()


def begin(repo, name, values):
    if (repo / STATE).exists():
        raise Refused(f"a packet is already open ({STATE}); show --stage or reject it first")
    if not name.strip():
        raise Refused("a packet needs a name")
    paths = list(dict.fromkeys(packet_path(v) for v in values))
    pending = dirty(repo)
    if pending:
        raise Refused("the working tree holds changes; commit your own edits before the packet starts:\n"
                      + "\n".join(f"  {p}" for p in pending))
    at = head(repo)
    save(repo, {"name": name.strip(), "paths": paths, "head": at})
    print(f"packet open: {name.strip()} ({len(paths)} path(s)) at {at}")
    return 0


def mode_of(repo, base, path):
    """The mode a staged path keeps: its index entry's, else its mode in `base`, else a plain file's."""
    for listing in (text(repo, "ls-files", "-s", "--", path), text(repo, "ls-tree", base, "--", path)):
        if listing.strip():
            return listing.split()[0]
    return "100644"


def stage_bytes(repo, base, captured, env=None):
    """Put exactly the captured bytes in the index (or remove a path captured as absent)."""
    for path, raw in sorted(captured.items()):
        if raw is None:
            run_git(repo, "update-index", "--force-remove", "--", path, env=env)
            continue
        blob = run_git(repo, "hash-object", "-w", "--stdin", f"--path={path}", data=raw).decode().strip()
        run_git(repo, "update-index", "--add", "--cacheinfo", f"{mode_of(repo, base, path)},{blob},{path}", env=env)


def show(repo, stage=False, snapshot=None):
    data = load(repo)
    if stage and not snapshot:
        raise Refused("show --stage needs --snapshot <the digest the main loop reviewed>")
    base, paths = data["head"], data["paths"]
    changed, untracked = changed_paths(repo, base)
    captured = capture(repo, changed)
    problems = []
    print(f"packet: {data['name']}")
    for path in changed:
        print(f"{'inside ' if inside(path, paths) else 'outside'} {path}")
    outside = [p for p in changed if not inside(p, paths)]
    if outside:
        problems.append("outside the packet's paths: " + ", ".join(outside))
    now = head(repo)
    if now != base:
        problems.append(f"HEAD moved from {base} to {now}: a worker never commits")
    if not changed:
        problems.append("nothing changed since begin")
    out = sys.stdout.buffer
    out.write(f"--- staged ({base[:12]} to the index)\n".encode())
    out.write(run_git(repo, "diff", "--cached", "--no-renames", base))
    out.write(b"--- unstaged (the index to the working tree)\n")
    out.write(run_git(repo, "diff", "--no-renames"))
    for path in untracked:
        raw = captured.get(path)
        if raw is None:
            continue
        out.write(f"--- new file {path} ({len(raw)} bytes)\n".encode())
        out.write(b"(binary)\n" if b"\0" in raw else raw + (b"" if raw.endswith(b"\n") or not raw else b"\n"))
    reviewed = digest(captured)
    out.write(f"snapshot: {reviewed}\n".encode())
    out.flush()
    if problems:
        for problem in problems:
            print("NOT ACCEPTABLE: " + problem, file=sys.stderr)
        return 1
    if stage:
        if reviewed != snapshot:
            print(f"NOT ACCEPTABLE: the tree no longer holds the reviewed snapshot ({snapshot}); it holds {reviewed}."
                  " Read the change again.", file=sys.stderr)
            return 1
        stage_bytes(repo, base, captured)
        later = [p for p, raw in sorted(captured.items()) if read_bytes(repo, p) != raw]
        for path in later:
            print(f"changed after the review, left unstaged: {path}")
        close(repo)
        print(f"staged {len(captured)} path(s) exactly as reviewed; packet closed")
    return 0


def build_stash(repo, base, message, changed, untracked, captured):
    """The commit `git stash push --include-untracked` would make, built from the captured bytes; the tree and the
    live index are not touched."""
    index_tree = text(repo, "write-tree").strip()
    index_commit = text(repo, "commit-tree", index_tree, "-p", base, "-m", f"index on {message}").strip()
    with tempfile.TemporaryDirectory(dir=repo / ".git") as tmp:
        work_index = {"GIT_INDEX_FILE": str(Path(tmp) / "work")}
        run_git(repo, "read-tree", index_tree, env=work_index)
        stage_bytes(repo, base, {p: captured[p] for p in changed if p not in untracked}, env=work_index)
        work_tree = text(repo, "write-tree", env=work_index).strip()
        loose_index = {"GIT_INDEX_FILE": str(Path(tmp) / "loose")}
        stage_bytes(repo, base, {p: captured[p] for p in untracked if captured[p] is not None}, env=loose_index)
        loose_tree = text(repo, "write-tree", env=loose_index).strip()
    loose_commit = text(repo, "commit-tree", loose_tree, "-m", f"untracked files on {message}").strip()
    return text(repo, "commit-tree", work_tree, "-p", base, "-p", index_commit, "-p", loose_commit,
                "-m", f"On main: {message}").strip()


def stash_listing(repo):
    """(name, commit, subject) for every stash entry."""
    return [tuple(line.split("\0")) for line in text(repo, "stash", "list", "--format=%gd%x00%H%x00%gs").splitlines()]


def store(repo, commit, message):
    run_git(repo, "stash", "store", "-m", message, commit)


def head_content(repo, path):
    """The bytes git would check out for `path` at HEAD (smudged), or None when HEAD has no file there: no entry, or
    a folder (a tree) or a submodule (a commit) at that name, whose own files are paths of their own."""
    entry = text(repo, "ls-tree", "HEAD", "--", path).split()
    if len(entry) < 2 or entry[1] != "blob":
        return None
    return run_git(repo, "cat-file", "--filters", f"HEAD:{path}")


def blocked(repo, path):
    """A path that cannot take a file now: a folder holds its name, or a file holds one of its parents' names."""
    target = repo / path
    if target.is_dir():
        return True
    parent = target.parent
    while parent != repo:
        if parent.exists() and not parent.is_dir():
            return True
        parent = parent.parent
    return False


def return_path(repo, path, raw):
    """Write `path` back to its HEAD bytes (or remove it when HEAD lacks it; a file already gone is settled)."""
    target = repo / path
    if raw is None:
        if target.is_file() or target.is_symlink():
            os.unlink(target)
        parent = target.parent
        while parent != repo:  # remove the folders this emptied; one already gone is passed over
            if parent.is_dir():
                if any(parent.iterdir()):
                    break
                parent.rmdir()
            parent = parent.parent
    else:
        atomic_write(target, raw)


def reject(repo):
    data = load(repo)
    base, message = data["head"], STASH_MESSAGE.format(name=data["name"])
    now = head(repo)
    if now != base:
        commits = text(repo, "log", "--oneline", f"{base}..{now}").strip()
        print(f"NOT REJECTED: HEAD moved from {base} to {now}; nothing was changed and the packet stays open. "
              f"Reconcile these commits first:\n{commits}", file=sys.stderr)
        return 1
    rejection = data.get("rejection")
    if rejection is None:
        changed, untracked = changed_paths(repo, base)
        if not changed and not dirty(repo):
            close(repo)
            print("nothing to set aside; packet closed")
            return 0
        captured = capture(repo, changed)
        commit = build_stash(repo, base, message, changed, untracked, captured)
        rejection = {"stash": commit, "stored": False, "paths": {p: sha(captured[p]) for p in changed},
                     "settled": {}}
        data["rejection"] = rejection
        save(repo, data)
    if not rejection["stored"]:
        if rejection["stash"] not in [c for _, c, _ in stash_listing(repo)]:
            store(repo, rejection["stash"], message)
        rejection["stored"] = True
        save(repo, data)
    # The index goes back to HEAD only while it is still the one the stash's index commit captured: an index staged
    # after the capture (by the owner, between an interrupted reject and its retry) is in no stash, so it is kept.
    index_now = text(repo, "write-tree").strip()
    captured_index = text(repo, "rev-parse", f"{rejection['stash']}^2^{{tree}}").strip()
    index_kept = False
    if index_now == captured_index:
        run_git(repo, "read-tree", base)
    elif index_now != text(repo, "rev-parse", f"{base}^{{tree}}").strip():
        index_kept = True
    failed = []
    contents = {p: head_content(repo, p) for p in rejection["paths"] if p not in rejection["settled"]}
    # Removals first, deepest first, then writes, shallowest first: a folder that took a tracked file's name is
    # emptied before the file is written back in its place.
    order = sorted(contents, key=lambda p: (contents[p] is not None,
                                            p.count("/") * (-1 if contents[p] is None else 1), p))
    for path in order:
        recorded = rejection["paths"][path]
        if sha(read_bytes(repo, path)) != recorded:
            rejection["settled"][path] = "kept"  # saved after the capture: in no stash, so it stays on disk
        elif contents[path] is not None and blocked(repo, path):
            rejection["settled"][path] = "kept"  # a kept save (a folder or a file) still holds a name on its way
        else:
            try:
                return_path(repo, path, contents[path])
            except OSError as exc:
                failed.append(f"{path} ({exc})")
                continue
            rejection["settled"][path] = "returned"
        save(repo, data)
    name = next((n for n, c, _ in stash_listing(repo) if c == rejection["stash"]), "stash")
    print(f"set aside as {name} ({rejection['stash']}): {message}")
    if failed:
        print("NOT FINISHED: these paths could not be returned; run reject again: " + ", ".join(failed),
              file=sys.stderr)
        return 1
    kept = [p for p, how in sorted(rejection["settled"].items()) if how == "kept"]
    del data["rejection"]
    left = dirty(repo)
    if kept or left or index_kept:
        save(repo, data)
        for path in kept:
            print(f"kept on disk, saved after the capture and not in the stash: {path}")
        if index_kept:
            print("kept the index: it was staged after the capture and is not in the stash")
        print("NOT FINISHED: the tree still holds changes saved during the rejection "
              f"({', '.join(sorted(set(kept + left)))}); run reject again to set them aside too", file=sys.stderr)
        return 1
    close(repo)
    print("tree returned to HEAD; packet closed")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=ROOT, help=argparse.SUPPRESS)  # the tests' fixture repository
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("begin")
    b.add_argument("--name", required=True)
    b.add_argument("--path", dest="paths", action="append", required=True)
    s = sub.add_parser("show")
    s.add_argument("--stage", action="store_true")
    s.add_argument("--snapshot", help="with --stage: the snapshot digest of the change the main loop read")
    sub.add_parser("reject")
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    try:
        if args.command == "begin":
            return begin(repo, args.name, args.paths)
        if args.command == "show":
            return show(repo, stage=args.stage, snapshot=args.snapshot)
        return reject(repo)
    except Refused as exc:
        print("packet refused: " + str(exc), file=sys.stderr)
        return 2
    except (GitFailed, OSError) as exc:
        print("packet failed: " + str(exc), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
