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
import http.client
import json
import os
import re
from pathlib import Path, PurePosixPath
import secrets
import shutil
import socket
import stat
import sys
import tarfile
import tempfile
import threading
import time
import urllib.parse
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import process_tree  # found through scripts/lib, put on the path just above
import tool_lock

LOCK = ROOT / "tools.lock.json"
TOOLS = ROOT / ".tools"
RECEIPT = tool_lock.RECEIPT
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


REDIRECTS = 5


class Expired(OSError):
    """The overall deadline passed while the connection was still being read."""


class Bounded:
    """One download's connection, shut by a watchdog at the deadline whatever is being read: headers, a chunk-size
    line or the body (round 2 of the second cycle: a server trickling inside one of those would otherwise hold the
    bootstrap past its deadline, since the socket timeout counts only silence)."""

    def __init__(self, url, timeout, deadline, scheme_ok=("https",)):
        self.expired = False
        self.connection = None
        self.response = None
        self.lock = threading.Lock()
        left = max(0.0, deadline - time.monotonic())
        self.timer = threading.Timer(left, self.expire)
        self.timer.daemon = True
        self.timer.start()
        try:
            for _ in range(REDIRECTS + 1):
                parts = urllib.parse.urlsplit(url)
                if parts.scheme not in scheme_ok:
                    raise OSError(f"refusing a {parts.scheme or 'schemeless'} URL: {url}")
                kind = http.client.HTTPSConnection if parts.scheme == "https" else http.client.HTTPConnection
                with self.lock:
                    if self.expired:
                        raise Expired("the deadline passed")
                    self.connection = kind(parts.hostname, parts.port, timeout=timeout)
                path = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
                self.connection.request("GET", path, headers={"User-Agent": "office-bootstrap-tools"})
                self.response = self.connection.getresponse()
                if self.response.status in (301, 302, 303, 307, 308) and self.response.getheader("Location"):
                    url = urllib.parse.urljoin(url, self.response.getheader("Location"))
                    self.response.close()
                    self.connection.close()
                    continue
                if self.response.status != 200:
                    raise OSError(f"HTTP {self.response.status} {self.response.reason}")
                return
            raise OSError(f"more than {REDIRECTS} redirects")
        except BaseException as error:
            self.close()
            if self.expired:
                raise Expired("the deadline passed") from None
            raise error

    def expire(self):
        with self.lock:
            self.expired = True
            connection = self.connection
        if connection is not None and connection.sock is not None:
            try:
                connection.sock.shutdown(socket.SHUT_RDWR)  # wakes a read blocked in any phase
            except OSError:
                pass  # already closed
            connection.close()

    def read1(self, n):
        try:
            return self.response.read1(n)
        except (OSError, http.client.HTTPException):
            if self.expired:
                raise Expired("the deadline passed") from None
            raise

    def close(self):
        self.timer.cancel()
        if self.response is not None:
            self.response.close()
        if self.connection is not None:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def bounded_open(url, timeout=READ_SECONDS, deadline=None):
    """The default opener: an https GET bounded by the socket timeout and by `deadline` (a time.monotonic())."""
    return Bounded(url, timeout, deadline if deadline is not None else time.monotonic() + 3600)


def fetch(name, entry, folder, opener, deadline_seconds):
    """Download `entry` into a temporary file in `folder`, bounded in bytes and time, and verify it; the file's path.
    Any failure removes the temporary file and raises Failed."""
    fd, tmp = tempfile.mkstemp(prefix=f"download-{name}-", suffix=".tmp", dir=folder)
    started = time.monotonic()
    deadline = started + deadline_seconds
    digest, got = hashlib.sha256(), 0
    late = f"{name}: the download passed its deadline of {deadline_seconds:.0f} s"
    try:
        with os.fdopen(fd, "wb") as out:
            try:
                with opener(entry["url"], timeout=READ_SECONDS, deadline=deadline) as response:
                    while True:
                        if time.monotonic() > deadline:
                            raise Failed(late)
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
            except Expired:
                raise Failed(late) from None
            except (OSError, ValueError, http.client.HTTPException) as error:  # a timeout, a cut connection
                raise Failed(f"{name}: the download failed: {type(error).__name__}: {error}") from None
        if got != entry["size"]:
            raise Failed(f"{name}: {got} of the pinned {entry['size']} bytes arrived")
        if digest.hexdigest() != entry["sha256"]:
            raise Failed(f"{name}: the archive's SHA-256 is {digest.hexdigest()}, not the pinned {entry['sha256']}")
        return Path(tmp)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise

def kept(member, keep):
    """The `keep` path or prefix that keeps an archive member (the exact path, or a folder above it), or None."""
    return next((k for k in keep if member == k or member.startswith(k.rstrip("/") + "/")), None)


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
    """Unpack the kept members of `archive` into `staging`, refusing a member or link that leaves it, and a `keep`
    path or prefix that produced no file (a wrong prefix would otherwise leave, say, the LLVM headers out)."""
    keep, fmt = entry["keep"], entry["format"]
    used = set()
    _unpack(name, entry, archive, staging, used)
    unused = [k for k in keep if k not in used]
    if fmt != "exe" and unused:
        raise Failed(f"{name}: the archive has nothing under the kept path {unused[0]!r}")


def _unpack(name, entry, archive, staging, used):
    keep, fmt = entry["keep"], entry["format"]
    if fmt == "exe":  # installed under its tool's name, one name on every architecture (vcpkg-arm64.exe is vcpkg.exe)
        program = f"{name}.exe"
        with open(archive, "rb") as source:
            write_member(staging, checked_member(name, program), source)
        return
    if fmt == "zip":
        with zipfile.ZipFile(archive) as bundle:
            for info in bundle.infolist():
                member = checked_member(name, info.filename)
                selector = None if info.is_dir() else kept(member, keep)
                if selector is None:
                    continue
                if stat.S_ISLNK(info.external_attr >> 16):
                    raise Failed(f"{name}: the archive holds a link, {member!r}, which a zip cannot keep safely")
                with bundle.open(info) as source:
                    write_member(staging, member, source)
                used.add(selector)
        return
    with tarfile.open(archive, mode="r:xz") as bundle:
        for info in bundle:
            member = checked_member(name, info.name)
            selector = None if info.isdir() else kept(member, keep)
            if selector is None:
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
            used.add(selector)


def manifest(folder):
    """{relative path: [size, sha256]} of every file in `folder` but the receipt."""
    files = {}
    for path in sorted(p for p in folder.rglob("*") if p.is_file() and p.name != RECEIPT):
        files[path.relative_to(folder).as_posix()] = [path.stat().st_size, sha256_file(path)]
    return files


def receipt_ok(folder, entry, name):
    """Whether `folder` holds a receipt for exactly this lock entry, in the current layout, and every file it records,
    unchanged."""
    files = tool_lock.receipt(folder, entry, name)
    if files is None:
        return False
    for relative, (size, digest) in files.items():
        path = folder / relative
        try:
            if path.stat().st_size != size or sha256_file(path) != digest:
                return False
        except OSError:
            return False
    return True

def promote(staging, destination):
    """Move `staging` into place; a damaged destination is set aside first and then removed."""
    if destination.exists():
        aside = destination.with_name(f"{destination.name}.stale-{secrets.token_hex(4)}")
        destination.rename(aside)
        try:
            staging.rename(destination)
        except OSError:
            aside.rename(destination)  # the earlier installation goes back where it was
            raise
        try:
            shutil.rmtree(aside)
        except OSError as error:  # installed and complete; the set-aside folder is a failure the run reports
            return f"cleanup of {aside.name} failed after the new installation was promoted: {error}"
    else:
        staging.rename(destination)
    return None


def install(name, version, entry, tools, opener, deadline_seconds):
    """Install one tool's archive for this host, unless an unchanged installation is already there."""
    destination = tools / f"{name}-{version}"
    if destination.is_dir() and receipt_ok(destination, entry, name):
        return False
    staging = tools / f"{name}-{version}.partial"
    if staging.exists():
        try:
            shutil.rmtree(staging)
        except OSError as error:  # held by another process: this tool fails, the others go on
            raise Failed(f"{name}: an earlier staging folder cannot be removed ({error}); close what holds it and "
                         f"run the bootstrap again") from None
    archive = fetch(name, entry, tools, opener, deadline_seconds)
    step = "unpacking"
    try:
        staging.mkdir()
        unpack(name, entry, archive, staging)
        missing = [b for b in entry["bin"] if not (staging / b).is_dir()]
        if missing:
            raise Failed(f"{name}: the archive has no {', '.join(missing)} folder")
        step = "writing the receipt"
        files = manifest(staging)
        if not files:
            raise Failed(f"{name}: nothing the lock keeps is in the archive")
        receipt = {"sha256": entry["sha256"], "entry": entry, "files": files}
        fd, tmp = tempfile.mkstemp(dir=staging, prefix=".installed.", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(receipt, out, indent=1)
        os.replace(tmp, staging / RECEIPT)
        step = "promotion"
        leftover = promote(staging, destination)
    except OSError as error:  # a full disk, a denied write, a file another process holds
        shutil.rmtree(staging, ignore_errors=True)
        raise Failed(f"{name}: {step} failed: {error}; any earlier installation is untouched, and running the "
                     f"bootstrap again once that is fixed installs it") from None
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    finally:
        archive.unlink(missing_ok=True)
    if leftover:
        raise Failed(f"{name}: {leftover}; the next run removes it")
    return True


def drop_older(name, version, tools, names=()):
    """Remove the folders of `name`'s other versions, once `version` is installed (never before: an upgrade that
    fails must leave the earlier version in place). Returns the problems, one per folder that could not go."""
    problems = []
    others = [n for n in names if n != name and n.startswith(f"{name}-")]  # vcpkg-registry is not a vcpkg version
    for path in tools.iterdir():
        if any(path.name.startswith(f"{other}-") for other in others):
            continue
        if path.is_dir() and path.name.startswith(f"{name}-") and path.name != f"{name}-{version}" \
                and not path.name.endswith(".partial") and ".stale-" not in path.name \
                and re.fullmatch(rf"{re.escape(name)}-[A-Za-z0-9][A-Za-z0-9._-]*", path.name):
            try:
                shutil.rmtree(path)
            except OSError as error:
                problems.append(f"cleanup of {path.name} failed: {error}")
    return problems


def clean(lock, tools):
    """Remove staging and set-aside folders and leftover downloads; the problems, one per entry that could not go."""
    problems = []
    for path in tools.iterdir():
        if path.name == RUN_LOCK:
            continue
        # Older versions are not removed here: drop_older removes each only once its replacement is installed.
        if path.name.endswith(".partial") or ".stale-" in path.name or path.name.startswith("download-"):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
            except OSError as error:  # a file another process holds: left for the next run, and said
                problems.append(f"cleanup of {path.name} failed: {error}")
    return problems


def status(lock, tools, arch):
    """{name: problem or None} for every tool: installed as pinned, with every tool it requires installed too."""
    own = {name: None if receipt_ok(tools / f"{name}-{tool['version']}", tool["archives"][arch], name)
           else "missing or damaged" for name, tool in lock.items()}
    result = {}
    for name, tool in lock.items():
        broken = [r for r in tool.get("requires", []) if own[r]]
        result[name] = own[name] or (f"requires {', '.join(broken)}, which is missing or damaged" if broken else None)
    return result


# Each installed program and the arguments that print its version (D00 T04 §3). vcpkg-registry is source data with
# no program: --check proves it, its receipt for the pinned entry with every file re-hashed.
PROBES = (("cmake", ["--version"]), ("ninja", ["--version"]), ("sccache", ["--version"]), ("vcpkg", ["version"]),
          ("clangd", ["--version"]), ("clang-tidy", ["--version"]), ("clang-format", ["--version"]))
PROBE_SECONDS = 60
PROBE_BYTES = 1 << 20


def probe(path, flags):
    """What `path flags` prints (its output and errors together), run in a process tree bounded in time and bytes."""
    fd, out = tempfile.mkstemp(prefix="probe-", suffix=".txt")
    os.close(fd)
    try:
        outcome = process_tree.run([str(path), *flags], stdout_path=out, stderr_path=out, timeout=PROBE_SECONDS,
                                   max_bytes=PROBE_BYTES)
        text = Path(out).read_text(encoding="utf-8", errors="replace")
        if outcome.stopped:
            raise Failed(f"{path.name} was stopped ({outcome.stopped})")
        if outcome.exit != 0:
            raise Failed(f"{path.name} exited {outcome.exit}: {text.strip()[:200]}")
        return text
    finally:
        Path(out).unlink(missing_ok=True)


def reports(text, pin):
    """Whether `text` names version `pin` as a whole token: `4.4.5` but not `4.4.50` or `14.4.5`; a suffix after a
    dash stays allowed (vcpkg prints `2026-09-26-<commit>`)."""
    return re.search(rf"(?<![0-9A-Za-z.])v?{re.escape(pin)}(?![0-9A-Za-z]|\.[0-9])", text) is not None


def versions(installed, run=probe):
    """Print each program's version line; the problems, one per program missing or not at its tool's pin."""
    problems = []
    for program, flags in PROBES:
        try:
            owner, path = installed.locate(program)
            pin = installed.lock[owner]["version"]
            text = run(path, flags)
        except (tool_lock.ToolMissing, Failed, process_tree.TreeError, OSError) as error:
            problems.append(f"{program}: {error}")
            continue
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        shown = next((line for line in lines if reports(line, pin)), lines[0] if lines else "(no output)")
        print(f"{program} ({owner} {pin}): {shown}")
        if not reports(text, pin):
            problems.append(f"{program}: reports {shown!r}, not {owner}'s pinned {pin}")
    return problems


def main(argv=None, opener=bounded_open, lock_path=LOCK, tools=TOOLS, arch=None, run=probe):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="download nothing; exit 1 unless every tool is installed")
    parser.add_argument("--only", action="append", metavar="NAME", help="install only this tool (repeatable)")
    parser.add_argument("--deadline", type=float, default=30, help="minutes one download may take (default 30)")
    parser.add_argument("--where", metavar="PROGRAM", help="print the path of an installed program, or refuse")
    parser.add_argument("--bin-dirs", action="store_true",
                        help="print the program folders of every tool installed as pinned, one per line")
    parser.add_argument("--versions", action="store_true",
                        help="run each program's version flag; exit 1 unless every one reports its pin")
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
    if args.where or args.bin_dirs or args.versions:
        installed = tool_lock.Tools(lock_path, tools, arch)
        if args.versions:
            problems = versions(installed, run)
            for problem in problems:
                print(f"bootstrap-tools: {problem}", file=sys.stderr)
            return 1 if problems else 0
        if args.where:
            try:
                print(installed.path(args.where))
            except tool_lock.ToolMissing as error:
                print(f"bootstrap-tools: {error}", file=sys.stderr)
                return 1
            return 0
        dirs, problems = installed.bin_dirs()
        for folder in dirs:
            print(folder)
        for problem in problems:
            print(f"bootstrap-tools: {problem}", file=sys.stderr)
        return 1 if problems else 0
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
            for problem in clean(lock, tools):
                print(f"bootstrap-tools: {problem}", file=sys.stderr)
                failed += 1
            for name in wanted:
                tool = lock[name]
                try:
                    changed = install(name, tool["version"], tool["archives"][arch], tools, opener,
                                      args.deadline * 60)
                    print(f"{name} {tool['version']}: {'installed' if changed else 'already installed'}")
                    for problem in drop_older(name, tool["version"], tools, list(lock)):
                        print(f"bootstrap-tools: {name}: {problem}", file=sys.stderr)
                        failed += 1
                except Failed as error:
                    print(f"bootstrap-tools: {error}", file=sys.stderr)
                    failed += 1
    except Failed as error:  # another run holds the folder
        print(f"bootstrap-tools: {error}", file=sys.stderr)
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
