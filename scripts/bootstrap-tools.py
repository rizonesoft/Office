#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Fetch the pinned build tools of `tools.lock.json` into `.tools/` in the clone (D00 T04 §1).

    python scripts/bootstrap-tools.py                 # install or repair every tool for this host's architecture
    python scripts/bootstrap-tools.py --only cmake    # one tool (repeatable)
    python scripts/bootstrap-tools.py --check         # exit 0 only when every tool is installed as pinned

This script is the only thing that downloads a build tool. Each archive is fetched into a temporary file inside
`.tools/`, stopped when more than its pinned `size` arrives, when a read stalls for 60 seconds or when its deadline
passes, and compared with its pinned SHA-256 before anything is unpacked. Only the `keep` members are unpacked, into
`.tools/<name>-<version>.partial/`; a member with an absolute path, a `..` part, or a link leaving the tool's folder
refuses the archive. The receipt `.installed.json` (the archive's hash, the lock entry, and the path, size and
SHA-256 of every kept file) is written inside the staging folder, which is then promoted to `.tools/<name>-<version>/`,
so a promoted folder always carries its receipt. An installed tool counts only when every recorded file is present
with its size and hash and every tool it requires is installed too: anything else is repaired. Leftover staging
folders, set-aside folders and folders of versions the lock no longer names are removed.

Exit 0 when every tool is installed (or, with --check, when every one is), 1 when one could not be installed (or is
missing or damaged), 2 when the lock file or an argument is refused.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import shutil
import stat
import sys
import tarfile
import tempfile
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import tool_lock  # found through scripts/lib, put on the path just above

LOCK = ROOT / "tools.lock.json"
TOOLS = ROOT / ".tools"
RECEIPT = ".installed.json"
RUN_LOCK = "bootstrap.lock"  # held by the one run that may change .tools/
READ_SECONDS = 60
LOCK_SECONDS = 60  # a second run waits this long for the first, then refuses
CHUNK = 1 << 20


class RunLock:
    """An exclusive lock on `.tools/bootstrap.lock` for the whole run, so two bootstraps never delete or promote each
    other's work (round 1); the system releases it when the holder dies."""

    def __init__(self, tools):
        self.path = Path(tools) / RUN_LOCK
        self.handle = None

    def __enter__(self):
        self.handle = open(self.path, "a+b")
        deadline = time.monotonic() + LOCK_SECONDS
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    self.handle.seek(0)
                    msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError:
                if time.monotonic() > deadline:
                    self.handle.close()
                    raise Failed(f"another bootstrap still holds {self.path} after {LOCK_SECONDS} s") from None
                time.sleep(0.2)

    def __exit__(self, *exc):
        try:
            if os.name == "nt":
                import msvcrt
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()
        return False


class Failed(Exception):
    """A tool could not be installed: exit 1 with the reason."""


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(name, entry, folder, opener, deadline_seconds):
    """Download `entry` into a temporary file in `folder`, bounded in bytes and time, and verify it; the file's path.
    Any failure removes the temporary file and raises Failed."""
    fd, tmp = tempfile.mkstemp(prefix=f"download-{name}-", suffix=".tmp", dir=folder)
    started = time.monotonic()
    digest, got = hashlib.sha256(), 0
    try:
        with os.fdopen(fd, "wb") as out:
            try:
                with opener(entry["url"], timeout=READ_SECONDS) as response:
                    while True:
                        if time.monotonic() - started > deadline_seconds:
                            raise Failed(f"{name}: the download passed its deadline of {deadline_seconds:.0f} s")
                        # read1 returns what has arrived (at most CHUNK) instead of waiting for a full CHUNK, so a
                        # server sending a little at a time cannot hold one read past the deadline (round 1).
                        block = response.read1(CHUNK)
                        if not block:
                            break
                        got += len(block)
                        if got > entry["size"]:
                            raise Failed(f"{name}: more than the pinned {entry['size']} bytes arrived")
                        digest.update(block)
                        out.write(block)
            except (OSError, ValueError) as error:  # a socket timeout is an OSError
                raise Failed(f"{name}: the download failed: {error}") from None
        if got != entry["size"]:
            raise Failed(f"{name}: {got} of the pinned {entry['size']} bytes arrived")
        if digest.hexdigest() != entry["sha256"]:
            raise Failed(f"{name}: the archive's SHA-256 is {digest.hexdigest()}, not the pinned {entry['sha256']}")
        return Path(tmp)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def kept(member, keep):
    """Whether an archive member is one the lock keeps: the exact path, or under a kept folder."""
    return any(member == k or member.startswith(k.rstrip("/") + "/") for k in keep)


def checked_member(name, member):
    """The member's relative path, refused when it is absolute or climbs out of the tool's folder."""
    clean = member.replace("\\", "/")
    path = PurePosixPath(clean)
    if path.is_absolute() or clean.startswith("/") or (len(clean) > 1 and clean[1] == ":") or ".." in path.parts:
        raise Failed(f"{name}: the archive holds a member outside the tool's folder: {member!r}")
    return clean


def write_member(staging, relative, source):
    target = staging / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "wb") as out:
        shutil.copyfileobj(source, out, CHUNK)


def unpack(name, entry, archive, staging):
    """Unpack the kept members of `archive` into `staging`, refusing a member or link that leaves it."""
    keep, fmt = entry["keep"], entry["format"]
    if fmt == "exe":
        program = PurePosixPath(entry["url"].split("?")[0]).name
        with open(archive, "rb") as source:
            write_member(staging, checked_member(name, program), source)
        return
    if fmt == "zip":
        with zipfile.ZipFile(archive) as bundle:
            for info in bundle.infolist():
                member = checked_member(name, info.filename)
                if info.is_dir() or not kept(member, keep):
                    continue
                if stat.S_ISLNK(info.external_attr >> 16):
                    raise Failed(f"{name}: the archive holds a link, {member!r}, which a zip cannot keep safely")
                with bundle.open(info) as source:
                    write_member(staging, member, source)
        return
    with tarfile.open(archive, mode="r:xz") as bundle:
        for info in bundle:
            member = checked_member(name, info.name)
            if info.isdir() or not kept(member, keep):
                continue
            if info.issym() or info.islnk():
                base = PurePosixPath(member).parent if info.issym() else PurePosixPath(".")
                target = PurePosixPath(os.path.normpath(str(base / info.linkname.replace("\\", "/")))).as_posix()
                if PurePosixPath(info.linkname).is_absolute() or target.startswith("..") or ".." in \
                        PurePosixPath(target).parts:
                    raise Failed(f"{name}: the archive's link {member!r} leaves the tool's folder")
                raise Failed(f"{name}: the archive's link {member!r} is not carried; pin the file it names instead")
            if not info.isfile():
                continue
            source = bundle.extractfile(info)
            if source is None:
                continue
            with source:
                write_member(staging, member, source)


def manifest(folder):
    """{relative path: [size, sha256]} of every file in `folder` but the receipt."""
    files = {}
    for path in sorted(p for p in folder.rglob("*") if p.is_file() and p.name != RECEIPT):
        files[path.relative_to(folder).as_posix()] = [path.stat().st_size, sha256_file(path)]
    return files


def receipt_ok(folder, entry):
    """Whether `folder` holds a receipt for exactly this lock entry and every file it records, unchanged."""
    try:
        receipt = json.loads((folder / RECEIPT).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(receipt, dict) or receipt.get("entry") != entry or receipt.get("sha256") != entry["sha256"]:
        return False
    files = receipt.get("files")
    if not isinstance(files, dict) or not files:
        return False
    for relative, (size, digest) in files.items():
        path = folder / relative
        try:
            if path.stat().st_size != size or sha256_file(path) != digest:
                return False
        except OSError:
            return False
    return all((folder / b).is_dir() for b in entry["bin"])


def promote(staging, destination):
    """Move `staging` into place; a damaged destination is set aside first and then removed."""
    if destination.exists():
        aside = destination.with_name(f"{destination.name}.stale-{secrets.token_hex(4)}")
        destination.rename(aside)
        staging.rename(destination)
        shutil.rmtree(aside, ignore_errors=False)
    else:
        staging.rename(destination)


def install(name, version, entry, tools, opener, deadline_seconds):
    """Install one tool's archive for this host, unless an unchanged installation is already there."""
    destination = tools / f"{name}-{version}"
    if destination.is_dir() and receipt_ok(destination, entry):
        return False
    staging = tools / f"{name}-{version}.partial"
    if staging.exists():
        shutil.rmtree(staging)
    archive = fetch(name, entry, tools, opener, deadline_seconds)
    try:
        staging.mkdir()
        unpack(name, entry, archive, staging)
        missing = [b for b in entry["bin"] if not (staging / b).is_dir()]
        if missing:
            raise Failed(f"{name}: the archive has no {', '.join(missing)} folder")
        files = manifest(staging)
        if not files:
            raise Failed(f"{name}: nothing the lock keeps is in the archive")
        receipt = {"sha256": entry["sha256"], "entry": entry, "files": files}
        fd, tmp = tempfile.mkstemp(dir=staging, prefix=".installed.", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(receipt, out, indent=1)
        os.replace(tmp, staging / RECEIPT)
        promote(staging, destination)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    finally:
        archive.unlink(missing_ok=True)
    return True


def clean(lock, tools):
    """Remove staging and set-aside folders, leftover downloads, and folders of versions the lock no longer names."""
    current = {f"{name}-{tool['version']}" for name, tool in lock.items()}
    for path in tools.iterdir():
        if path.name == RUN_LOCK:
            continue
        stale = path.name.endswith(".partial") or ".stale-" in path.name or path.name.startswith("download-")
        older = path.is_dir() and path.name not in current and any(
            path.name.startswith(f"{name}-") for name in lock)
        if stale or older:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def status(lock, tools, arch):
    """{name: problem or None} for every tool: installed as pinned, with every tool it requires installed too."""
    own = {name: None if receipt_ok(tools / f"{name}-{tool['version']}", tool["archives"][arch])
           else "missing or damaged" for name, tool in lock.items()}
    result = {}
    for name, tool in lock.items():
        broken = [r for r in tool.get("requires", []) if own[r]]
        result[name] = own[name] or (f"requires {', '.join(broken)}, which is missing or damaged" if broken else None)
    return result


def main(argv=None, opener=urllib.request.urlopen, lock_path=LOCK, tools=TOOLS, arch=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="download nothing; exit 1 unless every tool is installed")
    parser.add_argument("--only", action="append", metavar="NAME", help="install only this tool (repeatable)")
    parser.add_argument("--deadline", type=float, default=30, help="minutes one download may take (default 30)")
    args = parser.parse_args(argv)
    arch = arch or tool_lock.host_arch()
    try:
        lock = tool_lock.load(lock_path)
    except tool_lock.LockError as error:
        print(f"bootstrap-tools refused: {error}", file=sys.stderr)
        return 2
    if args.only:
        unknown = [n for n in args.only if n not in lock]
        if unknown:
            print(f"bootstrap-tools refused: no tool named {', '.join(unknown)} in tools.lock.json", file=sys.stderr)
            return 2
    if args.deadline <= 0:
        print("bootstrap-tools refused: --deadline must be above 0", file=sys.stderr)
        return 2
    tools = Path(tools)
    if args.check:
        problems = {n: p for n, p in status(lock, tools, arch).items() if p}
        for name, problem in problems.items():
            print(f"{name} {lock[name]['version']}: {problem}")
        print("every tool is installed as pinned" if not problems else f"{len(problems)} tool(s) need the bootstrap")
        return 1 if problems else 0
    tools.mkdir(exist_ok=True)
    wanted = list(lock) if not args.only else [n for n in lock if n in args.only or any(
        n in lock[o].get("requires", []) for o in args.only)]
    failed = 0
    try:
        with RunLock(tools):
            clean(lock, tools)
            for name in wanted:
                tool = lock[name]
                try:
                    changed = install(name, tool["version"], tool["archives"][arch], tools, opener,
                                      args.deadline * 60)
                    print(f"{name} {tool['version']}: {'installed' if changed else 'already installed'}")
                except Failed as error:
                    print(f"bootstrap-tools: {error}", file=sys.stderr)
                    failed += 1
    except Failed as error:  # another run holds the folder
        print(f"bootstrap-tools: {error}", file=sys.stderr)
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
