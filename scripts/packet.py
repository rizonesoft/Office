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
reads, without touching the tree, checks that it gives every one of them back (below), stores it with
`git stash store` as `rejected packet: <name>`, and then returns each changed path to `HEAD`, checking right before
each write that the path still holds the bytes the stash captured: a path saved meanwhile is kept on disk and named,
and the index goes back to `HEAD` only while it is still the one the stash captured (an index staged after the
capture is kept and named). Removals run deepest first and writes after them, so a folder that took a tracked file's
name is emptied before the file returns.

`reject` reads the index once. Before it lists anything it reads the index file's bytes one time into a private
copy (`index_snapshot`), and every question it then asks about the index is put to that copy and never to the live
file: which paths are staged, changed, tracked or untracked, what mode a path has, and the tree the stash's index
commit records. So the stash is in git's standard shape for the one index it records, whatever is staged while
`reject` works: a path is in its working-tree commit or in its untracked parent, never in both, and
`git stash apply --index` brings back exactly the state the copy and the files held. A staging that lands after that
one read is in no stash: the live index then no longer holds the tree the stash recorded, so it is kept and named,
and the next `reject` sets it aside in a stash of its own.

`reject` writes the index in one place and as one step, under git's own lock (`return_index`). It makes
`.git/index.lock` itself, as a new file and never over an existing one, so while it decides no git command can stage
anything: git refuses, naming the lock. It reads the index file's bytes once, takes the tree those bytes hold from a
private copy (no git command of `reject`'s opens the live index before its last check), writes `HEAD`'s index
into the lock file and renames it over the index. A lock that is already there is never waited on and never removed:
`reject` refuses before it changes anything (exit 2), or, when the lock appears later, stops with the stash stored
(exit 3), naming the file both times, and the next `reject` carries on. Whatever fails, the lock `reject` made is
removed and the index file is byte for byte what it was. Should a program that ignores the lock write the index
during the step all the same, the bytes on disk no longer match the ones read and the index is kept and named.
`build/packet.json` notes the step under `rejection.index` before the rename (`replacing`, with the sha256 of the
bytes read and of the bytes about to land) and after it (`returned` or `kept`), so a `reject` that died at the
rename knows on its next call, from the bytes the index holds, that the new index landed and does not write it twice.

Every read, removal and write goes through one model of what occupies a name on disk (`occupant`: nothing, a file,
a link, a Windows folder link, a junction, a real folder, something git does not record, a path beyond a link or a
file, or a name held under another spelling), so each kind is handled the same way in every step. A link or a
junction is read, stashed and returned as a link (mode 120000) and is never followed: nothing is read, written or
removed through one, a path below one counts as absent, and the link itself is the changed path.

Whether git makes links at all in this repository is git's to say: its effective `core.symlinks`, asked of git
itself (`makes_links`; where no configuration sets it, git's own default, which is false on Windows and true
elsewhere). While it is false git checks a mode 120000 entry out as a plain file holding the target, unconverted,
and reads such a file, where its index has a link, as that link. Every place that asks what git will write goes
through the one function that knows (`checked_out`), and the place that asks what `git add` would record goes
through `mode_of`. So with `core.symlinks` false:

- `HEAD`'s link is returned as git's checkout would write it, a file holding the target, and git reads the tree
  as unchanged; `folder_links` is not consulted for it, because no link is made.
- A file standing for a link that the worker edited is staged and stashed as the link it is to git (mode 120000),
  and `git stash apply` writes it back as that file.
- A real link or junction on disk, tracked or not, is still read as a link, as git reads it. Its stash would give
  it back as a file, which is not the entry captured, so it has no form (below): `reject` names it, removes
  nothing and leaves the packet open until `core.symlinks` is true or the owner has moved the link out of the tree.
- `show` displays and digests what is on disk, and `show --stage` records what `git add` would.

Windows keeps three kinds of link apart and never turns one into another: a file link, a folder link (only this
one reaches into a folder) and a junction. git records a link's target and nothing else, so the kind is this
command's to keep: an entry read from disk carries it (`read_entry`), two entries are the same only when the kind
is too, and `show`'s digest covers it. What git itself does was measured on git 2.56.0.windows.1 in scratch
repositories (the probe numbers are in the functions and the tests that rest on them), not assumed:

- At `git stash apply` and at checkout git makes the kind its `symlink` attribute names for the path (`dir`,
  `file`), read from the tree it is writing; with no attribute it makes a file link and turns it into a folder
  link only when the target, opened from the link's folder, is a folder then or becomes one before that git
  process ends. A target that begins with a separator is never opened. `link_made` answers by that rule, from
  the stash's own trees and, for what no tree of the stash holds, the disk; `checked_out` gives the kind with
  the target. A captured link git would bring back as the other kind, or whose kind neither settles, has no
  form (below): a folder link to a folder no one has made yet comes back as a file link, so `reject` names it,
  removes nothing, and says what makes it storable (the attribute, or the target).
- git leaves a tracked path alone when the stash's entry for it is the one `HEAD` has, so there the stash gives
  back what `reject` itself returned (`stash_entry`). A tracked link that changed in kind alone is such a path,
  and a change though git lists none: `show` names it, and for `reject` it has no form.
- A junction is a folder to git: git records none, lists the files behind it as the tree's own and never makes
  one. This command records it as the link it is and never looks behind it, and since no stash under any
  setting brings a junction back, a junction among the changed paths always has no form: `reject` names it and
  removes nothing until the owner has taken it away (`rmdir` removes the junction alone).
- `HEAD`'s links come back as the kind each was at `begin`, which `build/packet.json` records (`folder_links`,
  `file_links`): `begin` saw a tree without changes, that tree is what `reject` promises, and git's rule for a
  fresh checkout cannot rebuild it (a folder link whose target is not there yet). A link `begin` has no record
  of is the kind git's checkout makes.
- An absolute target is recorded as git records it, without the prefix Windows reports it with
  (`git_link_target`).

Elsewhere a link has one kind and none of this applies.

A path is its exact spelling. Each name is looked up in its own folder's list of names, so on a file system that
ignores case `src/a.py` and `src/A.py` are two paths: the one the folder lists holds the file, the other is absent
and is never read, written or removed through the first. A rename that changes only the case of a file or a folder,
staged or made on disk alone (which git does not report), is therefore a removal of the old spelling and a new
file under the new one, in `begin`, `show`, the staged index and the stash alike; `reject` removes the new spelling
first and then writes `HEAD`'s, and holds `HEAD`'s back while a kept save still has the name.

Content is converted by the attributes of the tree it belongs to. A file `reject` returns is `HEAD`'s blob as
`HEAD`'s own `.gitattributes` check it out (`git --attr-source=<HEAD>`), never as the working tree's do: those may be
the very change being rejected, so a line-ending rule the worker changed or added has no say in what comes back.
`reject` refuses (exit 2, nothing changed) under a git that cannot read attributes from a commit. Working-tree bytes
staged by `show --stage` pass the working tree's attributes, as `git add` passes them; that verb removes and writes
no file of the tree, so the reviewed bytes stay in their files whatever the index holds.

`reject` removes and overwrites files, so it holds to one rule, checked on the stored objects after the stash is
built and before anything in the tree or the index is touched: every captured path comes back out of the stash as
it was captured. The check asks the stash alone: each path is checked out of the stash commit under the attributes
git itself will use for it at `git stash apply` (`git --attr-source=<the stash commit>` for a tracked path, and for
an untracked one the stash's tree together with its untracked parent's, since git writes untracked files after the
tracked ones are in place), a link is compared as its kind and its target, and no `.gitattributes` on disk is read
for it. So
whatever changes on disk between the moment a file is read and the moment its blob is made, a rule edited in
between included, either the stash is shown to give the captured entry back or nothing is removed. Each file is
stored in the first of these forms that passes, recorded per path under `rejection.forms` in `build/packet.json`:

- `filtered`: the blob `git add` makes of the bytes; checked out of the stash it is the captured bytes again.
- `unfiltered`: the captured bytes themselves as the blob, for a file the first form does not give back (mixed line
  endings git would normalise, a rule that changed after the read); checked out, it is the captured bytes again.
- `converted`: no blob checks out as the captured bytes, because the stash's own rules rewrite them on every
  checkout (a file saved with LF where `core.autocrlf` or `eol=crlf` checks it out with CRLF). The blob is the
  captured bytes themselves, so `git cat-file blob <stash>:<path>` (`<stash>^3:<path>` for an untracked file)
  prints them exactly, and what `git stash apply` writes is to git the same content: under the stash's rules both
  make one and the same blob, so `git status` and `git diff` read the applied tree as they read the captured one.
- `none`: neither holds (a filter that does not undo itself, say). `reject` then stores the stash it has, with the
  file's bytes as its blob, changes nothing in the tree or the index, names each such path and exits 1 with the
  packet open; the next `reject` reads the tree afresh, and stores no second stash while nothing has changed.
  A link or a junction has no form while `core.symlinks` is false: git would give it back as a file. A junction
  has none under any setting, nor has a link git would make as the other kind (above).

`link` and `absent` are recorded for a link (its target, unfiltered) and for a path with nothing on disk. Paths
stored `unfiltered` or `converted` are named in `reject`'s output.

`reject` records its progress in `build/packet.json`, so a
`reject` that stopped part way resumes on the next call with the same stash. It closes the packet once every path
is settled and the tree holds no change; kept saves are named, and a further `reject` sets them aside too.

Nothing is ever discarded or taken back out of a stash by this command: a changed path may be the owner's.

Exit 0 done, 1 the change is not acceptable as it stands or the rejection is not finished, 2 refused (a tree with
changes at `begin`, no open packet, a packet already open, a bad path, a missing or stale `--snapshot`, a git too
old for `reject`, an index another git command holds locked when `reject` starts), 3 git or the file system failed.
"""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import subprocess
import sys
import stat
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


# Variables this command never inherits: it names its attribute source itself, per call (`attributes_of`), and
# everywhere else the attributes are the working tree's. An inherited GIT_ATTR_SOURCE would redirect every
# conversion (`hash-object --path`, `cat-file --filters`) to a tree the caller's shell happened to name.
NOT_INHERITED = ("GIT_ATTR_SOURCE",)


def git_environment(extra=None):
    """The environment every git call runs in: the caller's, less NOT_INHERITED, plus this call's own `extra`."""
    kept = {name: value for name, value in os.environ.items() if name.upper() not in NOT_INHERITED}
    return {**kept, **(extra or {})}


def run_git(repo, *args, data=None, env=None):
    """git's output as bytes; `data` is fed to its standard input."""
    proc = subprocess.run([git_path(), "-C", str(repo), *args], input=data, capture_output=True,
                          env=git_environment(env))
    if proc.returncode != 0:
        raise GitFailed(f"git {' '.join(args)} failed: {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout


def text(repo, *args, env=None):
    return run_git(repo, *args, env=env).decode("utf-8", "replace")


def names(repo, *args, env=None):
    return [p for p in text(repo, *args, "-z", env=env).split("\0") if p]


def head(repo):
    return text(repo, "rev-parse", "HEAD").strip()


LINK_MODE = "120000"


def makes_links(repo):
    """Whether git makes a link of a mode 120000 entry in this repository, or a plain file holding the target:
    git's effective `core.symlinks`, read by git from every place it reads configuration (system, user, the
    repository, the command's environment). Where nothing sets it the answer is git's own default for the
    platform: git for Windows makes no links unless told to, every other git does. Asked each time it is needed
    and never remembered, so no answer outlives a change of the setting."""
    proc = subprocess.run([git_path(), "-C", str(repo), "config", "--type=bool", "--get", "core.symlinks"],
                          capture_output=True, env=git_environment())
    value = proc.stdout.decode("utf-8", "replace").strip()
    if proc.returncode == 0 and value in ("true", "false"):
        return value == "true"
    if proc.returncode == 1 and not value:  # git's way of saying that nothing sets it
        return os.name != "nt"
    raise GitFailed(f"git config core.symlinks failed: {proc.stderr.decode('utf-8', 'replace').strip() or value}")


def dirty(repo, env=None):
    """Every path `git status` reports, untracked files listed one by one, both sides of a rename. `env` names the
    index asked (`index_snapshot`); without it, the live one."""
    listing = text(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", env=env)
    parts, entries, i = listing.split("\0"), [], 0
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


def git_link_target(target):
    """A link target as git records it. git for Windows (compat/mingw.c, normalize_ntpath) takes the NT prefix
    off the absolute target Windows reports and reads `\\` as `/` (and writes `/` back as `\\`). Measured, probe
    20: a folder link made to `R:\\x\\outside` reads back from the system with `\\\\?\\` before it, git records
    `R:/x/outside`, and git checks that out as a folder link again; the prefixed spelling, were it recorded, is
    one git only ever writes as a file link (probes 13e and 13f)."""
    if os.name != "nt":
        return target
    if target.startswith("\\"):
        if target.startswith(("\\??\\", "\\\\?\\")):
            target = target[4:]
        elif target[:12].lower() == "\\dosdevices\\":
            target = target[12:]
        if target[:4].upper() == "UNC\\":
            target = "\\" + target[3:]
    return target.replace("\\", "/")


def disk_link_target(target):
    """A recorded link target as git writes it on this system: Windows resolves a relative link only with `\\`."""
    return target.replace("/", "\\") if os.name == "nt" else target


# What occupies a name in the working tree. Every read, removal and write below asks `occupant` (one `lstat` per
# name, never a call that follows a link) and acts on the answer, so no step holds a view of its own.
NOTHING = "nothing"          # no entry by that name, or one of its parent folders is missing
FILE = "file"                # a regular file
LINK = "link"                # a symbolic link (on Windows: a file link)
FOLDER_LINK = "folder link"  # Windows only: a symbolic link made as a folder link; it never becomes a file link
JUNCTION = "junction"        # Windows only: a junction or a mounted volume
FOLDER = "folder"            # a real folder of this tree
OTHER = "other"              # a pipe, a socket, a device: nothing git records, never read, written or removed
BEYOND = "beyond"            # a parent's name is held by something that is not a real folder: outside this tree
ALIAS = "alias"              # the name, or a parent's, is held under another spelling: that entry is a path of its own
LINKS = (LINK, FOLDER_LINK, JUNCTION)
JUNCTION_TAG = 0xA0000003    # IO_REPARSE_TAG_MOUNT_POINT


def kind_of(target):
    """What holds the name `target`, from one `lstat`: the name itself is looked at, never what it points to."""
    try:
        found = os.lstat(target)
    except (FileNotFoundError, NotADirectoryError):
        return NOTHING
    if stat.S_ISLNK(found.st_mode):
        as_folder = getattr(found, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_DIRECTORY", 0x10)
        return FOLDER_LINK if as_folder else LINK
    if getattr(found, "st_reparse_tag", 0) == JUNCTION_TAG:
        return JUNCTION
    if stat.S_ISDIR(found.st_mode):
        return FOLDER
    return FILE if stat.S_ISREG(found.st_mode) else OTHER


class Look:
    """One look at the working tree: each folder's own list of names and each name's kind, read once. A step that
    changes the tree never keeps one, so every answer it acts on is read fresh."""

    def __init__(self):
        self.listed, self.kinds = {}, {}

    def names(self, folder):
        """The names a real folder holds, exactly as it stores them."""
        if folder not in self.listed:
            try:
                self.listed[folder] = frozenset(os.listdir(folder))
            except (FileNotFoundError, NotADirectoryError):
                self.listed[folder] = frozenset()
        return self.listed[folder]

    def kind(self, target):
        if target not in self.kinds:
            self.kinds[target] = kind_of(target)
        return self.kinds[target]


def stored_name(folder, name, listed):
    """`name` is not among the names `folder` lists. The listed name of the entry that answers to it all the same
    (another case on a file system that ignores case, a short name), or None when nothing answers."""
    try:
        wanted = os.lstat(folder / name)
    except (FileNotFoundError, NotADirectoryError):
        return None
    for other in sorted(listed, key=lambda entry: (entry.casefold() != name.casefold(), entry)):
        try:
            if os.path.samestat(os.lstat(folder / other), wanted):
                return other
        except (FileNotFoundError, NotADirectoryError):
            continue
    raise OSError(f"{name} in {folder} answers under a spelling the folder does not list")


def trail(repo, path, look=None):
    """`path` walked down from the repository one name at a time: for each name something holds, (the path so far
    as the folders themselves spell it, the kind of what holds it, whether its folder lists the name exactly as
    `path` spells it). The walk goes on only through real folders, so nothing is looked at through a link, a
    junction or a file, and it ends at the first name nothing holds."""
    look = look or Look()
    here, spelled, found = repo, [], []
    for part in PurePosixPath(path).parts:
        listed = look.names(here)
        name = part if part in listed else stored_name(here, part, listed)
        if name is None:
            break
        spelled.append(name)
        here = here / name
        kind = look.kind(here)
        found.append(("/".join(spelled), kind, name == part))
        if kind != FOLDER:
            break
    return found


def occupant(repo, path, look=None):
    """What occupies `path`, spelled exactly so, in the working tree: ALIAS when the name or a parent's is held
    only under another spelling, BEYOND when a link, a junction or a file holds a parent's name."""
    found = trail(repo, path, look)
    if not all(exact for _, _, exact in found):
        return ALIAS
    if len(found) == len(PurePosixPath(path).parts):
        return found[-1][1]
    return BEYOND if found and found[-1][1] not in (FOLDER, NOTHING) else NOTHING


def read_entry(repo, path):
    """What a path holds in the working tree: (its kind, its target as git records one) for a link, the kind being
    the one the platform gives it (LINK, and on Windows FOLDER_LINK or JUNCTION, which Windows never turns into
    one another), never followed, so a link to a folder or to nothing is kept as a link; (FILE, its bytes) for a
    file; or None when neither is there (nothing, a real folder, something git does not record, a path beyond a
    link or a file, or a name held only under another spelling: that entry is read under its own). Two entries
    are the same only when kind and content both are: git records a link's target alone, so the kind is this
    command's to keep, and a link that would come back as another kind has not come back."""
    kind, target = occupant(repo, path), repo / path
    try:
        if kind in LINKS:
            return (kind, os.fsencode(git_link_target(os.readlink(target))))
        if kind == FILE:
            return (FILE, target.read_bytes())
    except FileNotFoundError:
        pass  # gone between the look and the read
    return None


def sha(entry):
    if entry is None:
        return None
    kind, raw = entry
    return hashlib.sha256(kind.encode() + b"\0" + raw).hexdigest()


def hollow(folder):
    """A real folder holding nothing but real folders that hold nothing: no byte and no link can be lost with it."""
    with os.scandir(folder) as found:
        children = [child.path for child in found]
    return all(kind_of(child) == FOLDER and hollow(child) for child in children)


def changed_paths(repo, base, env=None, kinds=None):
    """(every path changed since `base`, the untracked ones among them, the ones no diff of git's shows), as this
    command sees the tree: base to index, index to working tree with both sides of a rename, and untracked. All
    four listings ask the index `env` names (`index_snapshot`: one index behind the four, and behind whatever is
    built from them); without it, the live one. A link that `kinds` (`begun_kinds`: each tracked link's kind at
    `begin`) has as a file link and the disk now has as a folder link, or the reverse, is changed too: git
    records a link's target alone and reports nothing (probe 17). git
    for Windows looks through a junction and takes one spelling of a name for another; this command does
    neither. So a link or a junction above a listed or tracked path is itself a changed path, every tracked path
    below it is changed too (nothing of the tree is there any more), and an untracked file git lists behind it is
    left out: it is outside the tree and is never read or touched. And a tracked path held on disk only under
    another spelling is changed (it is absent), with the file or link that holds the name a path of its own,
    untracked unless the index has that spelling too."""
    staged = names(repo, "diff", "--cached", "--name-only", "--no-renames", base, env=env)
    unstaged = names(repo, "diff", "--name-only", "--no-renames", env=env)
    loose = set(names(repo, "ls-files", "--others", "--exclude-standard", env=env))
    indexed = set(names(repo, "ls-files", env=env))
    tracked, look = indexed | set(staged), Look()
    listed = set(staged) | set(unstaged)
    changed, untracked = set(listed), set()
    for path in tracked | loose:
        found = trail(repo, path, look)
        whole = len(found) == len(PurePosixPath(path).parts)
        at, kind, _ = found[-1] if found else (None, NOTHING, True)
        if not whole and kind in LINKS:  # a link or a junction holds a parent's name
            if path in tracked:
                changed.add(path)
            if at not in tracked:
                untracked.add(at)
        elif not all(exact for _, _, exact in found):  # the name, or a parent's, is held under another spelling
            if path in tracked:
                changed.add(path)
            if whole and kind in (FILE, *LINKS) and at not in indexed:
                untracked.add(at)
        elif path in loose:
            untracked.add(path)
    for path, was in (kinds or {}).items():
        if occupant(repo, path, look) in {LINK, FOLDER_LINK} - {was}:
            changed.add(path)
    changed |= untracked
    return sorted(changed), sorted(untracked), sorted(changed - listed - untracked)


def pending(repo, base, kinds=None):
    """git's own listing, and what this command lists as changed: a junction standing where tracked files were, a
    file renamed on disk to another case of its name, or a link that is no longer the kind `kinds` has for it,
    is a change here even when git for Windows reports none."""
    return list(dict.fromkeys(dirty(repo) + changed_paths(repo, base, kinds=kinds)[0]))


def capture(repo, paths):
    """Each path's working-tree entry, read once."""
    return {path: read_entry(repo, path) for path in paths}


def digest(captured):
    lines = "".join(f"{path}\0{sha(entry) or 'absent'}\n" for path, entry in sorted(captured.items()))
    return "sha256:" + hashlib.sha256(lines.encode("utf-8")).hexdigest()


def link_kinds(repo):
    """(the tracked links that are folder links on disk now, the ones that are file links). Windows records the
    kind on the link itself and a dangling link's target cannot tell it later, so `begin` notes both lists and
    reject returns each link as the kind it was. Under a git that makes no links (`makes_links`) a tracked link is
    a file on disk and is in neither list; a real link someone made there is listed, and the note goes unused
    while reject returns the file git would write."""
    found = {FOLDER_LINK: [], LINK: []}
    for line in text(repo, "ls-files", "-s", "-z").split("\0"):
        meta, _, path = line.partition("\t")
        if meta.startswith("120000 "):
            found.get(occupant(repo, path), []).append(path)
    return found[FOLDER_LINK], found[LINK]


def begun_kinds(data):
    """{tracked link: the kind it was on disk at `begin`}, from the packet's record. This, and not git's rule for
    a fresh checkout, says what kind `HEAD`'s link is here: `begin` saw a tree with no change in it, reject
    promises that tree back, and git's rule cannot rebuild it (a folder link whose target a build has yet to make
    is a file link to a fresh checkout, probe 17, and Windows never lets that one reach into the folder: review
    round 7). A link the record does not have (no link stood there at `begin`, or the record was written before
    file links were noted) is the kind git's own checkout would make (`link_made`)."""
    return {**{path: LINK for path in data.get("file_links", [])},
            **{path: FOLDER_LINK for path in data.get("folder_links", [])}}


def begin(repo, name, values):
    if (repo / STATE).exists():
        raise Refused(f"a packet is already open ({STATE}); show --stage or reject it first")
    if not name.strip():
        raise Refused("a packet needs a name")
    paths = list(dict.fromkeys(packet_path(v) for v in values))
    held = pending(repo, "HEAD")
    if held:
        raise Refused("the working tree holds changes; commit your own edits before the packet starts:\n"
                      + "\n".join(f"  {p}" for p in held))
    at = head(repo)
    as_folders, as_files = link_kinds(repo)
    save(repo, {"name": name.strip(), "paths": paths, "head": at, "folder_links": as_folders, "file_links": as_files})
    print(f"packet open: {name.strip()} ({len(paths)} path(s)) at {at}")
    return 0


FILE_MODES = ("100644", "100755")


def mode_of(repo, base, path, env=None):
    """The mode `git add` records for a file on disk at `path`: its entry's in the index being written (the one
    `env` names, else the live one), else its mode in `base`, when that is a file's mode. A file where that index
    has a link is the link itself to a git that makes no links (`makes_links`): it is how git checked the link
    out, so it keeps the link's mode, as `git add` keeps it. Otherwise (no entry, a folder's tree, a submodule, a
    link now a file under a git that makes links, a link only `base` has) a plain file's."""
    listings = ((True, text(repo, "ls-files", "-s", "--", path, env=env)),
                (False, text(repo, "ls-tree", base, "--", path)))
    for in_index, listing in listings:
        for line in listing.splitlines():
            meta, _, name = line.partition("\t")
            if name == path and meta:
                mode = meta.split()[0]
                if mode in FILE_MODES:
                    return mode
                return LINK_MODE if mode == LINK_MODE and in_index and not makes_links(repo) else "100644"
    return "100644"


def blob_of(repo, base, path, entry, env=None, filtered=True):
    """(mode, blob) for a captured entry, the blob written to git's object store. A link is stored as git stores
    one, mode 120000 with its target unfiltered. A file gets the mode `git add` gives it (`mode_of`, asked of the
    index `env` names: a file's, or the link's for a file that stands for a link under a git that makes none) and
    is stored `filtered`, the blob `git add` makes of the bytes under the attributes the working tree holds at
    this moment, or not: the bytes themselves."""
    kind, raw = entry
    if kind in LINKS:
        return LINK_MODE, run_git(repo, "hash-object", "-w", "--stdin", "--no-filters", data=raw).decode().strip()
    how = f"--path={path}" if filtered else "--no-filters"
    blob = run_git(repo, "hash-object", "-w", "--stdin", how, data=raw, env=env).decode().strip()
    return mode_of(repo, base, path, env), blob


def stage_bytes(repo, base, captured, env=None, blobs=None):
    """Put exactly the captured entries in the index (or remove a path captured as absent). Removals go first, so a
    file that took a folder's name is added only once the folder's entries are gone, and `--replace` lets an entry
    take a name a staged file or folder still holds. Each entry is the capture of its exact spelling, so of two
    spellings of one name only the one its folder lists is added and the other is removed.

    `blobs` gives each path's (mode, blob) when the caller has made them already (`build_stash`, which checks every
    one of them against the capture before `reject` goes on). Without it each is made here as `git add` makes it
    (`blob_of`), which is what `show --stage` is for: the index it writes is the one `git add` of the reviewed
    bytes would write, and it takes nothing off the disk."""
    for path in sorted((p for p, e in captured.items() if e is None), key=lambda p: (-p.count("/"), p)):
        run_git(repo, "update-index", "--force-remove", "--", path, env=env)
    for path, entry in sorted((p, e) for p, e in captured.items() if e is not None):
        mode, blob = blobs[path] if blobs is not None else blob_of(repo, base, path, entry, env)
        run_git(repo, "update-index", "--add", "--replace", "--cacheinfo", f"{mode},{blob},{path}", env=env)


def show(repo, stage=False, snapshot=None):
    data = load(repo)
    if stage and not snapshot:
        raise Refused("show --stage needs --snapshot <the digest the main loop reviewed>")
    base, paths = data["head"], data["paths"]
    changed, untracked, unseen = changed_paths(repo, base, kinds=begun_kinds(data))
    captured = capture(repo, changed)
    problems = []
    # One writer for everything up to the snapshot line, so the order holds whatever standard output is: text
    # written before is flushed first, and these bytes are flushed before anything is printed after them.
    sys.stdout.flush()
    out = sys.stdout.buffer
    out.write(f"packet: {data['name']}\n".encode("utf-8"))
    for path in changed:
        out.write(f"{'inside ' if inside(path, paths) else 'outside'} {path}\n".encode("utf-8"))
    outside = [p for p in changed if not inside(p, paths)]
    if outside:
        problems.append("outside the packet's paths: " + ", ".join(outside))
    now = head(repo)
    if now != base:
        problems.append(f"HEAD moved from {base} to {now}: a worker never commits")
    if not changed:
        problems.append("nothing changed since begin")
    out.write(f"--- staged ({base[:12]} to the index)\n".encode())
    out.write(run_git(repo, "diff", "--cached", "--no-renames", base))
    out.write(b"--- unstaged (the index to the working tree)\n")
    out.write(run_git(repo, "diff", "--no-renames"))
    for path in unseen:  # absent as this command reads the tree, where git reads through a junction or a spelling
        entry = captured.get(path)
        if entry is None:
            out.write(f"--- gone {path} (git shows no change: a link or another spelling holds the name)\n"
                      .encode("utf-8"))
        elif entry[0] in LINKS:
            out.write(f"--- now a {entry[0]}: {path} (git shows no change: it records a link's target alone)\n"
                      .encode("utf-8"))
    for path in untracked:
        entry = captured.get(path)
        if entry is None:
            continue
        kind, raw = entry
        if kind in LINKS:
            out.write(f"--- new {kind} {path} -> ".encode("utf-8") + raw + b"\n")
            continue
        out.write(f"--- new file {path} ({len(raw)} bytes)\n".encode("utf-8"))
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
        later = [p for p, entry in sorted(captured.items()) if read_entry(repo, p) != entry]
        for path in later:
            print(f"changed after the review, left unstaged: {path}")
        close(repo)
        print(f"staged {len(captured)} path(s) exactly as reviewed; packet closed")
    return 0


def index_file(repo):
    """The file git reads and writes as this repository's index."""
    return Path(repo, text(repo, "rev-parse", "--git-path", "index").strip())


def lock_of(index):
    """git's lock on an index file: whoever makes this file, as a new one, is the only writer until it is gone."""
    return index.with_name(index.name + ".lock")


def read_index(index):
    """(the index file's bytes, the time it was last written), both from one open of the file, or (None, None)
    when there is no index yet. Only a regular file is read: an index that is a link or anything else is refused,
    never read or replaced through."""
    kind = kind_of(index)
    if kind == NOTHING:
        return None, None
    if kind != FILE:
        raise Refused(f"{index} is a {kind}, not a file: the index is never read or replaced through one")
    with open(index, "rb") as handle:
        return handle.read(), os.fstat(handle.fileno()).st_mtime_ns


def index_bytes(index):
    """The index file's bytes, read once, or None when there is no index yet."""
    return read_index(index)[0]


@contextlib.contextmanager
def index_snapshot(repo):
    """The live index, read once, as a private index file: the environment that makes a git command ask that copy
    and never the live index. Whatever is staged after the one read is not in it, so every answer taken from it
    (staged, changed, tracked, untracked, modes, the tree) is about one and the same index.

    The copy keeps the time the live file was last written. git trusts a file's recorded size and times only when
    the index was written after them, and reads the content of a file saved in the index's own second: a copy
    stamped with a later time would pass such a save by, and the edit would be listed nowhere. git may write what
    it learns of the files into the copy, as it does into the live index; the live index is not opened at all.
    The copy and its folder are removed when the block ends, however it ends."""
    raw, written = read_index(index_file(repo))
    with tempfile.TemporaryDirectory(dir=repo / ".git") as tmp:
        copy = Path(tmp) / "index"
        if raw is not None and written is not None:
            copy.write_bytes(raw)
            os.utime(copy, ns=(written, written))
        yield {"GIT_INDEX_FILE": str(copy)}


def fingerprint(raw):
    return "absent" if raw is None else hashlib.sha256(raw).hexdigest()


def tree_of(repo, raw):
    """The tree an index file holding the bytes `raw` records, from a private copy: the live index is not opened,
    so this takes no lock on it and writes nothing to it."""
    with tempfile.TemporaryDirectory(dir=repo / ".git") as tmp:
        copy = Path(tmp) / "index"
        if raw is not None:
            copy.write_bytes(raw)
        return text(repo, "write-tree", env={"GIT_INDEX_FILE": str(copy)}).strip()


def index_from(repo, commit):
    """The bytes of an index file that holds exactly `commit`'s tree, made as a private file."""
    with tempfile.TemporaryDirectory(dir=repo / ".git") as tmp:
        made = Path(tmp) / "index"
        run_git(repo, "read-tree", commit, env={"GIT_INDEX_FILE": str(made)})
        return made.read_bytes()


def publish_index(lock, index):
    """The one step that changes the live index: the finished lock file takes its name."""
    os.replace(lock, index)


HELD = ("another git command holds the index ({lock} exists); {state}. Run reject again when that command has "
        "finished, or remove the file yourself if no git is running: this command never removes a lock it did not "
        "make")


def refuse_held_index(repo):
    """Refuse, before anything is changed, while another git command holds the index: its lock is never waited
    on and never removed here, and a stale one is the owner's to remove."""
    lock = lock_of(index_file(repo))
    if kind_of(lock) != NOTHING:
        raise Refused(HELD.format(lock=lock, state="nothing was changed"))


def return_index(repo, base, data):
    """Return the index to `base` (the packet's HEAD) while it is still the one the stash captured: "returned" when
    it holds HEAD's tree afterwards, "kept" when it holds anything that is in no stash (staged after the capture).

    The compare and the replace are one step under git's own lock. This makes the lock file itself, as a new file,
    so from then on no git command can write the index (git refuses, naming the lock) and what is decided here is
    decided about the very bytes that are replaced: they are read once, their tree is taken from a private copy,
    HEAD's index is written into the lock file and the lock file is renamed over the index. The record notes the
    step before the rename, so a run that died at the rename finds on its next call that the bytes it was about
    to land are the ones the index holds, and writes nothing twice. A program that writes the index without
    asking for the lock is caught as far as it can be: the index is read again right before the lock file is
    filled, and kept when it is no longer the bytes decided about.

    Whatever fails, the lock made here is removed and the index file is byte for byte what it was: nothing but
    the rename ever touches it. A lock that is already there is someone else's: it is named and left alone."""
    rejection = data["rejection"]
    index = index_file(repo)
    lock = lock_of(index)
    try:
        handle = open(lock, "xb")
    except FileExistsError:
        raise GitFailed(HELD.format(lock=lock, state="the index was not changed and the stash is stored")) from None
    ours = True  # the lock file is this run's own until the rename gives its name away
    try:
        with handle:
            live = index_bytes(index)
            noted = rejection.get("index") or {}
            tree = tree_of(repo, live)
            head_tree = text(repo, "rev-parse", f"{base}^{{tree}}").strip()
            captured_tree = text(repo, "rev-parse", f"{rejection['stash']}^2^{{tree}}").strip()
            if fingerprint(live) == noted.get("next") or (noted.get("state") == "returned" and tree == head_tree):
                outcome = "returned"  # an earlier run's rename landed: these are the bytes it wrote, or HEAD's tree
            elif tree == captured_tree:
                replacement = index_from(repo, base)
                if index_bytes(index) != live:
                    outcome = "kept"  # written past the lock since it was read: not the bytes decided about
                else:
                    rejection["index"] = {"state": "replacing", "was": fingerprint(live),
                                          "next": fingerprint(replacement)}
                    save(repo, data)
                    handle.write(replacement)
                    handle.flush()
                    os.fsync(handle.fileno())
                    handle.close()  # Windows renames no open file
                    ours = False
                    try:
                        publish_index(lock, index)
                    except OSError:
                        ours = True  # the rename did not happen: the lock file is still there and still this run's
                        raise
                    outcome = "returned"
            else:
                outcome = "returned" if tree == head_tree else "kept"
    finally:
        if ours:
            os.unlink(lock)
    rejection["index"] = {**(rejection.get("index") or {}), "state": outcome}
    save(repo, data)
    return outcome


# The form a captured path is stored in (`rejection.forms`; the module docstring says what each one promises).
FILTERED, UNFILTERED, CONVERTED, NO_FORM = "filtered", "unfiltered", "converted", "none"
LINKED, ABSENT = "link", "absent"


def stash_commit(repo, base, message, index_tree, index_commit, changed, untracked, captured, blobs):
    """(the commit `git stash push --include-untracked` would make, the tree whose attributes git applies to that
    commit's untracked files), built from `index_tree` and the blobs given for the captured paths: the working-tree
    commit is that tree with the captured tracked paths put in, and the untracked parent holds the paths the index
    does not track, so no path is in both. Nothing is read from the working tree or the live index.

    git writes a stash's untracked files once its tracked ones are in place and reads their attributes from both,
    so the second tree is the working-tree commit's with the untracked parent's entries added."""
    with tempfile.TemporaryDirectory(dir=repo / ".git") as tmp:
        work_index = {"GIT_INDEX_FILE": str(Path(tmp) / "work")}
        run_git(repo, "read-tree", index_tree, env=work_index)
        stage_bytes(repo, base, {p: captured[p] for p in changed if p not in untracked}, env=work_index, blobs=blobs)
        work_tree = text(repo, "write-tree", env=work_index).strip()
        loose_index = {"GIT_INDEX_FILE": str(Path(tmp) / "loose")}
        loose = {p: captured[p] for p in untracked if captured[p] is not None}
        stage_bytes(repo, base, loose, env=loose_index, blobs=blobs)
        loose_tree = text(repo, "write-tree", env=loose_index).strip()
        both = work_tree
        if loose:
            run_git(repo, "update-index", "--add", "--replace", "-z", "--index-info",
                    data=run_git(repo, "ls-tree", "-r", "-z", loose_tree), env=work_index)
            both = text(repo, "write-tree", env=work_index).strip()
    loose_commit = text(repo, "commit-tree", loose_tree, "-m", f"untracked files on {message}").strip()
    commit = text(repo, "commit-tree", work_tree, "-p", base, "-p", index_commit, "-p", loose_commit,
                  "-m", f"On main: {message}").strip()
    return commit, both


def stash_place(commit, both, loose):
    """(the commit of the stash `commit` that holds a path, the tree git has in place when it writes that path at
    `git stash apply`, whose attributes it applies to it, the other trees that put or take anything in the tree
    around that moment): for an untracked path (`loose`) the untracked parent and `both` (`stash_commit`), for
    any other the stash commit for both. git writes the tracked paths in one process and the untracked ones in
    another, later (probes 05b, 09e, 10c and 10d), so what the stash's untracked parent holds is not there yet
    for a tracked path; what `HEAD` holds and the stash does not is on its way out, and what only the stash's
    index commit holds is a path reject removes from the disk."""
    if loose:
        return f"{commit}^3", both, (f"{commit}^1", f"{commit}^2")
    return commit, commit, (both, f"{commit}^1", f"{commit}^2")


def stash_entry(repo, commit, both, path, loose, kinds=None):
    """What stands at `path` once `git stash apply` has put the stash `commit` on the tree reject leaves, as
    read_entry would read it then. git writes a tracked path only where the stash's entry differs from the one of
    the commit it stands on (probes 16 and 21: a link and a file with the same blob in both stay as they were,
    whatever rule the stash adds for them), so for an entry that does not differ the answer is what reject
    itself returns there (`head_entry`, with `kinds` from `begin`'s record). Everything else is what git checks
    out of the stash (`checked_out`)."""
    holder, source, others = stash_place(commit, both, loose)
    if not loose:
        stays = tree_entry(repo, f"{commit}^1", path)
        if stays is not None and stays == tree_entry(repo, commit, path):
            return head_entry(repo, f"{commit}^1", path, kinds)
    return checked_out(repo, holder, source, path, others)


def same_to_git(repo, commit, both, path, loose, entry, index, kinds=None):
    """True when the stash holds the captured file's very bytes as its blob at `path`, and what `git stash apply`
    leaves there (`stash_entry`) is, to git, the same content as the captured bytes: under the stash's own
    attributes `git add` makes one and the same blob of both, so git reads the applied file as it read the
    captured one."""
    if entry is None or entry[0] != FILE:
        return False
    holder, source, _ = stash_place(commit, both, loose)
    listed = tree_entry(repo, holder, path)
    if listed is None or listed[0] not in FILE_MODES or listed[1] != "blob":
        return False
    written = stash_entry(repo, commit, both, path, loose, kinds)
    if run_git(repo, "cat-file", "blob", listed[2]) != entry[1] or written is None or written[0] != FILE:
        return False
    try:
        added = [run_git(repo, attributes_of(source), "hash-object", "--stdin", f"--path={path}", data=raw, env=index)
                 for raw in (written[1], entry[1])]
    except GitFailed:  # git refuses to convert one of them: not something it reads as the same content
        return False
    return added[0] == added[1]


def build_stash(repo, base, message, changed, untracked, captured, index, kinds=None):
    """(the stash commit, the form each changed path is stored in). The commit is the one
    `git stash push --include-untracked` would make, built from the captured bytes and from `index`
    (`index_snapshot`), the same copy of the index that `changed` and `untracked` were listed against: the index
    commit is that copy's tree. The working tree and the live index are not touched, and the live index is not
    read.

    What it returns has been checked, on the stored objects alone: every path is read back out of the commit as
    git will check it out at `git stash apply` (`stash_entry`) and compared with the capture. Each blob is made
    once. A file first gets the blob `git add` makes of it, under whatever attributes the tree holds at that
    moment; those may no longer be the ones the capture was read under, and the check does not care which they
    were. A file that does not come back gets its bytes as its blob and the commit is built again; the last commit
    built is the one checked and returned. A file that still does not come back is CONVERTED when git reads what
    it writes as the same content (`same_to_git`), and has NO_FORM otherwise, as has a link or an absent path the
    commit does not give back: every link and junction under a git that makes no links, every junction under any
    git, and a link git would make as the other kind, or whose kind the stash does not settle (`checked_out`,
    `link_made`). `reject` removes nothing while any path has no form. `kinds` is `begin`'s record of the tracked
    links (`begun_kinds`), for the paths git leaves as reject returned them (`stash_entry`)."""
    index_tree = text(repo, "write-tree", env=index).strip()
    index_commit = text(repo, "commit-tree", index_tree, "-p", base, "-m", f"index on {message}").strip()
    loose = set(untracked)
    blobs, forms = {}, {path: ABSENT for path in changed}
    for path in changed:
        entry = captured[path]
        if entry is None:
            continue
        forms[path] = LINKED if entry[0] in LINKS else FILTERED
        try:
            blobs[path] = blob_of(repo, base, path, entry, index)
        except GitFailed:  # git refuses to convert these bytes (core.safecrlf, a filter that fails): as they are
            blobs[path] = blob_of(repo, base, path, entry, index, filtered=False)
            forms[path] = UNFILTERED
    while True:  # ends: each further round takes at least one path from FILTERED to UNFILTERED
        commit, both = stash_commit(repo, base, message, index_tree, index_commit, changed, loose, captured, blobs)
        differs = [p for p in changed if stash_entry(repo, commit, both, p, p in loose, kinds) != captured[p]]
        again = [p for p in differs if forms[p] == FILTERED]
        if not again:
            break
        for path in again:
            blobs[path] = blob_of(repo, base, path, captured[path], index, filtered=False)
            forms[path] = UNFILTERED
    for path in differs:
        same = same_to_git(repo, commit, both, path, path in loose, captured[path], index, kinds)
        forms[path] = CONVERTED if same else NO_FORM
    return commit, forms


def stash_shape(repo, commit):
    """Everything a stash commit holds but the moment it was made: its tree, the commit it stands on, its index
    commit's tree and its untracked parent's tree. None for a commit that is gone or is no such stash."""
    try:
        return text(repo, "rev-parse", f"{commit}^{{tree}}", f"{commit}^1", f"{commit}^2^{{tree}}",
                    f"{commit}^3^{{tree}}").split()
    except GitFailed:
        return None


def stash_listing(repo):
    """(name, commit, subject) for every stash entry."""
    return [tuple(line.split("\0")) for line in text(repo, "stash", "list", "--format=%gd%x00%H%x00%gs").splitlines()]


def stash_name(repo, commit):
    return next((name for name, found, _ in stash_listing(repo) if found == commit), "stash")


def store(repo, commit, message):
    run_git(repo, "stash", "store", "-m", message, commit)


def attributes_of(commit):
    """git's option that reads every attribute from `commit`'s tree and none from the working tree."""
    return f"--attr-source={commit}"


def require_commit_attributes(repo, commit):
    """Refuse, before anything is changed, under a git that does not know the option (older than 2.40): without it
    a file could only come back as the working tree's attributes convert it, and those may be the rejected ones."""
    try:
        run_git(repo, attributes_of(commit), "rev-parse", "--git-dir")
    except GitFailed as exc:
        raise Refused("this git cannot read attributes from a commit (git 2.40 or later does), so HEAD's files "
                      f"cannot be returned as HEAD checks them out; nothing was changed: {exc}") from None


def tree_entry(repo, tree, path):
    """(mode, type, object) of the entry the commit or tree `tree` has at exactly `path`, or None."""
    listed = text(repo, "ls-tree", tree, "--", path).split()
    return tuple(listed[:3]) if len(listed) >= 3 else None


def symlink_attribute(repo, source, path):
    """The kind of link the `symlink` attribute asks for at `path`, read from the commit or tree `source` (and
    from git's own attribute files, as git reads them): FOLDER_LINK for `dir` or `directory`, LINK for `file`,
    None when it says neither, which git takes as unset (probes 03, 03b, 03c, 11, 15 and 15b)."""
    answer = run_git(repo, attributes_of(source), "check-attr", "-z", "symlink", "--", path).split(b"\0")
    value = answer[2] if len(answer) > 2 else b""
    return {b"dir": FOLDER_LINK, b"directory": FOLDER_LINK, b"file": LINK}.get(value)


CHAIN = 40  # more links in a row than any system follows: such a chain leads nowhere


def resolves_to_folder(repo, tree, others, path, target, depth=0):
    """Whether the link at `path` with the recorded `target` leads to a folder at the moment git, having written
    `tree`, makes the link: True, False, or None when nothing this command holds settles it.

    git for Windows asks the system to open the target from the link's own folder, through every link and
    junction on the way (probes 12 and 12h), and counts a folder that comes into being later in the same git
    process (probes 06, 06b, 09c and 09d). A target that begins with a separator is never opened (probes 13c
    and 13g). So, in this order: such a target is no folder; a target with a drive, or one that leaves the
    repository, is what the disk holds now (probes 13, 13b and 13d); a target inside the repository is what
    `tree` has there, a folder for a tree, no folder for a file, and for a link whatever that link leads to
    (probes 12f, 12g, 12i and 12j) unless its attribute makes a file link of it, which never opens as a folder
    (probes 31 and 31c); and where `tree` has nothing there, what the disk holds now (an empty or an ignored
    folder, probes 02 and 09f; `os.path.isdir` answers as git's own open does, probes 12, 31 and 31b), unless
    one of `others` has something there: that is put there or taken away by another step than the one that
    writes the link (probe 09e), and the answer is None."""
    spelled = target.replace("\\", "/")
    if spelled.startswith("/"):
        return False
    if len(spelled) > 2 and spelled[0].isalpha() and spelled[1:3] == ":/":
        return os.path.isdir(spelled)
    where = posixpath.normpath(posixpath.join(posixpath.dirname(path), spelled))
    if where == ".":
        return True
    if where == ".." or where.startswith("../") or where == ".git" or where.startswith(".git/"):
        return os.path.isdir(repo / where)
    found = tree_entry(repo, tree, where)
    if found is None:
        if any(tree_entry(repo, other, where) is not None for other in others):
            return None
        return os.path.isdir(repo / where)
    if found[0] != LINK_MODE:
        return found[1] != "blob"  # a tree, or a submodule's folder
    if depth >= CHAIN or symlink_attribute(repo, tree, where) == LINK:
        return False
    onward = run_git(repo, "cat-file", "blob", found[2]).decode("utf-8", "replace")
    return resolves_to_folder(repo, tree, others, where, onward, depth + 1)


UNSETTLED = "a link of a kind the stash does not settle"  # equal to no kind an entry read from disk has


def link_made(repo, source, others, path, target):
    """The kind of link git makes at `path` for a mode 120000 entry holding `target`, once it has written the
    commit or tree `source`, by git for Windows's own rule (compat/mingw.c, mingw_create_symlink, measured on git
    2.56.0.windows.1 with the probes named here and in `resolves_to_folder`): the `symlink` attribute of
    `source` decides when it is set (`symlink_attribute`); else git makes a file link and turns it into a folder
    link only when the target leads to a folder (probes 01, 02, 07, 08, 09 and 09b). UNSETTLED when that cannot
    be told from the stash and the disk. Elsewhere a link has one kind."""
    if os.name != "nt":
        return LINK
    asked = symlink_attribute(repo, source, path)
    if asked is not None:
        return asked
    leads = resolves_to_folder(repo, source, others, path, target)
    return UNSETTLED if leads is None else FOLDER_LINK if leads else LINK


def checked_out(repo, commit, source, path, others=()):
    """What git checks out at `path` from `commit`, as read_entry reads it afterwards: the one place that says
    what git will write at a name, for the stash check (`stash_entry`, `same_to_git`) and for what `reject`
    returns (`head_entry`) alike. None when `commit` has no file there (no entry, or a folder or a submodule at
    that name, whose own files are paths of their own).

    A mode 120000 blob is what this repository's git makes of one. Where git makes no links (`makes_links`) it is
    (FILE, the target's bytes), the plain file git writes there, with no conversion. Where it makes them it is
    (the kind of link git makes, target): `link_made`, asked of `source`, the tree git has written by then, and
    of `others` (`stash_place`). git never makes a junction (probes 14, 14b and 14c: to git a junction is a
    folder, it records none, and a recorded link comes back as a symbolic link). So a link captured from disk is
    never equal to what a git that makes no links would give back, a junction is equal to nothing git gives
    back under any setting, and a folder link and a file link are each equal only to their own kind.

    Any other blob is (FILE, its bytes after git's checkout conversion). That conversion (line endings,
    filters, encoding) is decided by the attributes of the commit or tree `source` and never by the working
    tree's `.gitattributes`: the answer is the same whatever the tree holds and whenever it is asked."""
    entry = tree_entry(repo, commit, path)
    if entry is None or entry[1] != "blob":
        return None
    if entry[0] == LINK_MODE:
        raw = run_git(repo, "cat-file", "blob", entry[2])
        if not makes_links(repo):
            return (FILE, raw)
        return (link_made(repo, source, others, path, raw.decode("utf-8", "replace")), raw)
    return (FILE, run_git(repo, attributes_of(source), "cat-file", "--filters", f"{commit}:{path}"))


def head_entry(repo, base, path, kinds=None):
    """What reject puts at `path` for the commit `base` (the packet's HEAD): what git checks out there by
    `base`'s own attributes and this repository's `core.symlinks`, a link being the kind it was at `begin`
    where `kinds` (`begun_kinds`, which says why) has it, and the kind git's checkout makes where it has not."""
    entry = checked_out(repo, base, base, path)
    if entry is not None and entry[0] in LINKS and path in (kinds or {}):
        return (kinds[path], entry[1])
    return entry


def remove_occupant(target, kind):
    """Take the name `target` away, by what holds it: a file or a link is unlinked, a folder link or a junction is
    removed as the one name it is (never what it points to), a real folder only while it is hollow."""
    if kind in (FILE, LINK):
        os.unlink(target)
    elif kind in (FOLDER_LINK, JUNCTION):
        os.rmdir(target)
    elif kind == FOLDER:
        with os.scandir(target) as found:
            children = [child.path for child in found]
        for child in children:
            if kind_of(child) == FOLDER:
                remove_occupant(child, FOLDER)
        os.rmdir(target)  # refuses a folder that still holds anything, so nothing is lost with it


def remove_empty_parents(repo, path):
    """Remove each parent folder of `path` that is now empty, up to the repository, as git does after it removes
    a file. A parent already gone is passed over; one that holds anything, is not a real folder, or is there only
    under another spelling ends the walk."""
    for parent in list(PurePosixPath(path).parents)[:-1]:
        kind = occupant(repo, parent.as_posix())
        if kind == FOLDER:
            with os.scandir(repo / parent) as found:
                if next(found, None) is not None:
                    return
            os.rmdir(repo / parent)
        elif kind != NOTHING:
            return


def temporary_beside(target):
    """A name in `target`'s folder that nothing holds, for a write that is moved into place when it is whole."""
    return target.with_name(f".packet-{os.getpid()}-{os.urandom(6).hex()}.tmp")


def make_link(target, at, as_folder):
    """Make a link to `target` at the free name `at`, of exactly the kind asked for. On Windows that is the
    system's own call: `os.symlink` makes a folder link whenever the target is a folder at that moment, whatever
    it is asked for, and a link that was a file link has to come back as one."""
    if sys.platform != "win32":
        os.symlink(target, at)
        return
    import ctypes
    from ctypes import wintypes
    create = ctypes.WinDLL("kernel32", use_last_error=True).CreateSymbolicLinkW
    create.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD)
    create.restype = wintypes.BOOLEAN
    kind, unprivileged, not_known = (1 if as_folder else 0), 2, 87
    if create(str(at), target, kind | unprivileged):
        return
    failed = ctypes.get_last_error()
    if failed == not_known:  # a Windows from before a link could be made without the privilege: ask as it knows
        if create(str(at), target, kind):
            return
        failed = ctypes.get_last_error()
    raise ctypes.WinError(failed)


def write_entry(target, entry, here):
    """Put `entry` at `target`, whose name `here` holds now (NOTHING, FILE or a link of any kind). The new file or
    link is made under a temporary name beside it and moved into place. A file or a file link gives way to that
    move in one step. A folder link or a junction does not (Windows moves nothing onto a name a folder of any kind
    holds), so it steps aside under a second temporary name, the new entry takes the name, and only then is the
    old one removed; when the new entry cannot take the name, the old one goes back to it. Whatever fails, no
    temporary name is left behind, but for an old entry that could not go back either: that one is named."""
    kind, raw = entry
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = temporary_beside(target)
    try:
        if kind in LINKS:
            # Windows keeps a folder link and a file link apart and never changes one into the other: the entry
            # says which (`head_entry`), and nothing is looked up through the link to decide it here.
            make_link(disk_link_target(os.fsdecode(raw)), temporary, kind == FOLDER_LINK)
        else:
            with open(temporary, "xb") as handle:
                handle.write(raw)
        if here in (FOLDER_LINK, JUNCTION):
            aside = temporary_beside(target)
            os.rename(target, aside)
            try:
                os.rename(temporary, target)
            except BaseException:
                try:
                    os.rename(aside, target)
                except OSError as exc:  # it is whole, and in the stash, under the name this error gives
                    raise OSError(f"{target.name} could not go back to its name and is now {aside.name}") from exc
                raise
            remove_occupant(aside, here)
        else:
            os.replace(temporary, target)
    finally:
        left = kind_of(temporary)
        if left != NOTHING:
            remove_occupant(temporary, left)


def return_path(repo, path, entry):
    """Put `path` back as HEAD has it, by what occupies the name now; the caller has just checked that it still
    holds what the stash captured. True when the path is settled, False when it is kept because the name cannot
    take HEAD's entry without touching something that is in no stash.

    HEAD has nothing there: a file or a link of any kind is removed (the link itself, never its target), a hollow
    folder is removed, a folder holding anything stays (its files are paths of their own), and a path beyond a
    link or a file, or held under another spelling, is left alone (that entry is a path of its own, removed or
    kept under its own name). Then the parents this emptied go.

    HEAD has a file or a link there: it replaces a file or a link of any kind, takes a free name (its parent
    folders are made) or the name of a hollow folder (an empty folder is in no way a save); it is kept back when a
    folder holding anything, or something git does not record, has the name, when the path lies beyond a link,
    a junction or a file (a write there would land outside the tree), or while another spelling still holds the
    name or a parent's (a write there would land on that entry: it goes first, under its own name)."""
    target, here = repo / path, occupant(repo, path)
    if entry is None:
        if here in (FILE, *LINKS) or (here == FOLDER and hollow(target)):
            remove_occupant(target, here)
        if here not in (BEYOND, ALIAS):
            remove_empty_parents(repo, path)
        return True
    if here in (BEYOND, OTHER, ALIAS) or (here == FOLDER and not hollow(target)):
        return False
    if here == FOLDER:
        remove_occupant(target, FOLDER)
        here = NOTHING
    write_entry(target, entry, here)
    return True


def explain_formless_links(repo, stash, formless):
    """Say, for each captured link or junction the stash `stash` does not give back as it is (`formless`: path
    to kind), why not and what the owner can do, one line per cause."""
    def named(paths):
        return ", ".join(sorted(paths))

    junctions = {path for path, kind in formless.items() if kind == JUNCTION}
    same = {path for path in set(formless) - junctions
            if tree_entry(repo, stash, path) is not None
            and tree_entry(repo, stash, path) == tree_entry(repo, f"{stash}^1", path)}
    other = set(formless) - junctions - same
    if junctions:
        print("These are junctions. git records none and makes none: to git a junction is the folder it leads to, "
              "and a link it has recorded comes back as a symbolic link. So each stays where it is: "
              + named(junctions) + ". Remove each yourself (`rmdir <path>` takes the junction alone and nothing it "
              "leads to) or move it out of the tree, and run reject again.", file=sys.stderr)
    if same:
        print("These links have the target HEAD has and are now the other kind of link (a folder link where a "
              "file link was, or the reverse). git records a link's target alone, so no stash holds the kind and "
              "each stays as it is: " + named(same) + ". Make each the kind it was, and run reject again.",
              file=sys.stderr)
    if other:
        print("Windows keeps a folder link and a file link apart, and git would bring each of these back as the "
              "other kind, or the stash does not settle which: " + named(other) + ". git makes a folder link "
              "only for a path whose `symlink` attribute is `dir`, or whose target is a folder when it writes the "
              "link, and a file link otherwise. Name the kind in .gitattributes (`<path> symlink=dir` or "
              "`<path> symlink=file`), or move the link out of the tree, and run reject again.", file=sys.stderr)


def reject(repo):
    data = load(repo)
    base, message = data["head"], STASH_MESSAGE.format(name=data["name"])
    now = head(repo)
    if now != base:
        commits = text(repo, "log", "--oneline", f"{base}..{now}").strip()
        print(f"NOT REJECTED: HEAD moved from {base} to {now}; nothing was changed and the packet stays open. "
              f"Reconcile these commits first:\n{commits}", file=sys.stderr)
        return 1
    require_commit_attributes(repo, base)
    refuse_held_index(repo)
    rejection = data.get("rejection")
    # A stash an earlier run stored that does not give every path back: that run changed nothing, so this one
    # reads the tree afresh (the owner may have changed the file or its rule since).
    earlier = rejection if rejection is not None and NO_FORM in rejection.get("forms", {}).values() else None
    links = {}  # each link and junction this run captured, and its kind; a stash with a formless path is this run's
    kinds = begun_kinds(data)
    if rejection is None or earlier is not None:
        # One read of the index, and every answer about it from that read: the listing, each path's place among
        # the tracked or the untracked, and the stash's commits. return_index then compares the live index with
        # the tree recorded here, under the lock, before it replaces anything.
        with index_snapshot(repo) as index:
            changed, untracked, _ = changed_paths(repo, base, env=index, kinds=kinds)
            if not changed and not dirty(repo, env=index):
                close(repo)
                print("nothing to set aside; packet closed")
                return 0
            captured = capture(repo, changed)
            links = {path: entry[0] for path, entry in captured.items() if entry is not None and entry[0] in LINKS}
            commit, forms = build_stash(repo, base, message, changed, untracked, captured, index, kinds)
        stored = False
        if earlier is not None and stash_shape(repo, commit) == stash_shape(repo, earlier["stash"]):
            commit, stored = earlier["stash"], earlier["stored"]  # the same content: no second stash of it
        rejection = {"stash": commit, "stored": stored, "paths": {p: sha(captured[p]) for p in changed},
                     "settled": {}, "forms": forms}
        data["rejection"] = rejection
        save(repo, data)
    if not rejection["stored"]:
        if rejection["stash"] not in [c for _, c, _ in stash_listing(repo)]:
            store(repo, rejection["stash"], message)
        rejection["stored"] = True
        save(repo, data)
    # The rule everything below stands on: the stored stash gives back every captured path (build_stash checked
    # each one on the stored objects). While one does not, nothing in the tree or the index is touched.
    stored_as = {form: sorted(p for p, how in rejection.get("forms", {}).items() if how == form)
                 for form in (UNFILTERED, CONVERTED, NO_FORM)}
    if stored_as[NO_FORM]:
        print(f"set aside as {stash_name(repo, rejection['stash'])} ({rejection['stash']}): {message}")
        print("NOT REJECTED: git cannot check these paths out of the stash as they are on disk, in any form they "
              "can be stored in: " + ", ".join(stored_as[NO_FORM]) + ". Nothing in the tree or the index was "
              "changed and the packet stays open. The stash holds every other path whole and each file named here "
              f"as its exact bytes (`git cat-file blob {rejection['stash']}:<path>`, or `{rejection['stash']}^3:"
              "<path>` for a new file). Change the rule or the filter that rewrites them, or move them out of the "
              "tree, and run reject again.", file=sys.stderr)
        as_files = sorted(set(links).intersection(stored_as[NO_FORM]))
        if as_files and not makes_links(repo):
            print("These are links, and git makes no links in this repository (core.symlinks is false): it would "
                  "bring each back as a plain file holding the link's target, so each stays where it is: "
                  + ", ".join(as_files) + ". Set core.symlinks to true (`git config core.symlinks true`), or move "
                  "them out of the tree, and run reject again.", file=sys.stderr)
        elif as_files:
            explain_formless_links(repo, rejection["stash"], {path: links[path] for path in as_files})
        return 1
    # The index goes back to HEAD only while it is still the one the stash's index commit captured: an index staged
    # after the capture (by the owner, between an interrupted reject and its retry) is in no stash, so it is kept.
    index_kept = return_index(repo, base, data) == "kept"
    failed = []
    contents = {p: head_entry(repo, base, p, kinds) for p in rejection["paths"] if p not in rejection["settled"]}
    # Removals first, deepest first, then writes, shallowest first: a folder that took a tracked file's name is
    # emptied before the file is written back in its place, and another spelling of a name HEAD has (a rename that
    # changed only the case) is removed under its own name before HEAD's spelling is written.
    order = sorted(contents, key=lambda p: (contents[p] is not None,
                                            p.count("/") * (-1 if contents[p] is None else 1), p))
    for path in order:
        held = read_entry(repo, path)
        if sha(held) != rejection["paths"][path]:
            # Not what the stash captured. HEAD's own entry is a return an earlier run made and could not record;
            # anything else was saved after the capture and is in no stash, so it stays on disk.
            rejection["settled"][path] = "returned" if held == contents[path] else "kept"
        else:
            try:
                took = return_path(repo, path, contents[path])
            except OSError as exc:
                failed.append(f"{path} ({exc})")
                continue
            # Kept: a kept save (a folder, a file, a link, another spelling) still holds the name or one on its way.
            rejection["settled"][path] = "returned" if took else "kept"
        save(repo, data)
    print(f"set aside as {stash_name(repo, rejection['stash'])} ({rejection['stash']}): {message}")
    if stored_as[UNFILTERED]:
        print("stored as the bytes they are, which the stash gives back exactly (the blob git add makes of them "
              "would not): " + ", ".join(stored_as[UNFILTERED]))
    if stored_as[CONVERTED]:
        print("stored as the bytes they are; git stash apply writes them as the stash's own line-ending and filter "
              f"rules check them out, and `git cat-file blob {rejection['stash']}:<path>` (`{rejection['stash']}^3:"
              "<path>` for a new file) prints them exactly: " + ", ".join(stored_as[CONVERTED]))
    if failed:
        print("NOT FINISHED: these paths could not be returned; run reject again: " + ", ".join(failed),
              file=sys.stderr)
        return 1
    kept = [p for p, how in sorted(rejection["settled"].items()) if how == "kept"]
    del data["rejection"]
    left = pending(repo, base, kinds)
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
