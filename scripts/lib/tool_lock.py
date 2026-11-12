# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Load `tools.lock.json`, the pins of the build tools the clone carries (D00 T04 §1), strictly.

The file is an object keyed by tool name. Each tool has a `version`, an `archives` object with exactly one entry per
host architecture (`x64`, `arm64`), an optional `requires` list (tools that must be installed with it: `vcpkg` needs
`vcpkg-registry`) and an optional `note`. Each archive has `url` (https only), `sha256` (64 lowercase hex), `size`
(bytes), `format` (`zip`, `tar.xz` or `exe`), `keep` (the member paths or path prefixes to unpack; empty for an `exe`),
`bin` (the folders, relative to the tool's folder, that hold its programs) and an optional `note`. Anything else is
refused with the tool's name, so a typo can never become a download from the wrong place.

It also answers where an installed program is (D00 T04 §2): `tool_path`, `tool_env` and `bin_dirs` look in the
clone's `.tools/` folder only, never on `PATH`, so a machine's own Ninja or CMake is never used by accident.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import re

ARCHES = ("x64", "arm64")
FORMATS = ("zip", "tar.xz", "exe")
TOOL_KEYS = {"version", "archives", "requires", "note"}
ARCHIVE_KEYS = {"url", "sha256", "size", "format", "keep", "bin", "note"}
NAME = re.compile(r"[a-z0-9][a-z0-9-]{0,39}")
SHA256 = re.compile(r"[0-9a-f]{64}")
ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "tools.lock.json"
TOOLS = ROOT / ".tools"
RECEIPT = ".installed.json"  # what bootstrap-tools.py writes in a tool's folder once it is installed whole
BOOTSTRAP = "python scripts/bootstrap-tools.py"
ENV = {"VCPKG_ROOT": "vcpkg-registry"}  # a variable a build tool needs, and the tool whose folder it names


class LockError(Exception):
    """The lock file is not valid; the message names the tool and the fault."""


def _relative(value, where):
    """A relative POSIX path with no `..`, as the lock file writes member paths and bin folders."""
    if not isinstance(value, str) or not value:
        raise LockError(f"{where} must be a non-empty path")
    path = PurePosixPath(value)
    if path.is_absolute() or "\\" in value or re.match(r"[A-Za-z]:", value) or ".." in path.parts:
        raise LockError(f"{where} must be a relative path inside the tool's folder: {value!r}")
    return value


def _archive(name, arch, entry):
    where = f"{name}: archives.{arch}"
    if not isinstance(entry, dict):
        raise LockError(f"{where} must be an object")
    unknown = set(entry) - ARCHIVE_KEYS
    missing = ARCHIVE_KEYS - {"note"} - set(entry)
    if unknown:
        raise LockError(f"{where}: unknown key(s) {', '.join(sorted(unknown))}")
    if missing:
        raise LockError(f"{where}: missing key(s) {', '.join(sorted(missing))}")
    if not isinstance(entry["url"], str) or not entry["url"].startswith("https://"):
        raise LockError(f"{where}: url must be https: {entry['url']!r}")
    if not isinstance(entry["sha256"], str) or not SHA256.fullmatch(entry["sha256"]):
        raise LockError(f"{where}: sha256 must be 64 lowercase hex characters")
    if type(entry["size"]) is not int or entry["size"] <= 0:
        raise LockError(f"{where}: size must be a positive number of bytes")
    if entry["format"] not in FORMATS:
        raise LockError(f"{where}: format must be one of {', '.join(FORMATS)}")
    for key in ("keep", "bin"):
        if not isinstance(entry[key], list):
            raise LockError(f"{where}: {key} must be a list")
        for value in entry[key]:
            _relative(value, f"{where}: {key}")
    if entry["format"] != "exe" and not entry["keep"]:
        raise LockError(f"{where}: keep must name what to unpack")
    if "note" in entry and not isinstance(entry["note"], str):
        raise LockError(f"{where}: note must be text")
    return entry


def parse(data):
    """The checked lock, from its decoded JSON."""
    if not isinstance(data, dict) or not data:
        raise LockError("tools.lock.json must be an object naming at least one tool")
    for name, tool in data.items():
        if not NAME.fullmatch(name):
            raise LockError(f"{name!r}: a tool name is lowercase letters, digits and dashes")
        if not isinstance(tool, dict):
            raise LockError(f"{name}: must be an object")
        unknown = set(tool) - TOOL_KEYS
        if unknown:
            raise LockError(f"{name}: unknown key(s) {', '.join(sorted(unknown))}")
        if not isinstance(tool.get("version"), str) or not tool["version"].strip():
            raise LockError(f"{name}: version must be text")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", tool["version"]):
            raise LockError(f"{name}: version {tool['version']!r} cannot name a folder")
        archives = tool.get("archives")
        if not isinstance(archives, dict):
            raise LockError(f"{name}: archives must be an object keyed by architecture")
        for arch in ARCHES:
            if arch not in archives:
                raise LockError(f"{name}: archives has no {arch} entry")
        extra = set(archives) - set(ARCHES)
        if extra:
            raise LockError(f"{name}: archives names unknown architecture(s) {', '.join(sorted(extra))}")
        for arch in ARCHES:
            _archive(name, arch, archives[arch])
        requires = tool.get("requires", [])
        if not isinstance(requires, list) or not all(isinstance(r, str) for r in requires):
            raise LockError(f"{name}: requires must be a list of tool names")
        if "note" in tool and not isinstance(tool["note"], str):
            raise LockError(f"{name}: note must be text")
    for name, tool in data.items():
        for needed in tool.get("requires", []):
            if needed not in data or needed == name:
                raise LockError(f"{name}: requires {needed!r}, which is not another tool of tools.lock.json")
    return data


def load(path):
    """The checked lock at `path`; LockError when it cannot be read or is not valid."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as error:
        raise LockError(f"{path} cannot be read: {error}") from None
    except ValueError as error:
        raise LockError(f"{path} is not JSON: {error}") from None
    return parse(data)


def host_arch():
    """`arm64` on an Arm64 Windows host, `x64` otherwise (the two architectures the suite builds for)."""
    return "arm64" if platform.machine().lower() in ("arm64", "aarch64") else "x64"


class ToolMissing(Exception):
    """A program's tool is not installed as the lock pins it; the message names the tool and the bootstrap command."""


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _bins(entry):
    """The tool's program folders, relative to its folder, as POSIX paths ('' for the folder itself)."""
    return ["" if b in (".", "./") else b.rstrip("/") for b in (entry["bin"] or ["."])]


def receipt(folder, entry):
    """The receipt's recorded files ({relative path: [size, sha256]}) when `folder` was installed from exactly this
    lock entry, or None. A lookup checks only this and the programs it hands out; `bootstrap-tools.py --check`
    re-hashes every file."""
    try:
        data = json.loads((folder / RECEIPT).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("entry") != entry or data.get("sha256") != entry["sha256"]:
        return None
    files = data.get("files")
    if not isinstance(files, dict) or not files or not all(
            isinstance(v, list) and len(v) == 2 and type(v[0]) is int and isinstance(v[1], str) for v in files.values()):
        return None
    if not all((folder / b).is_dir() for b in _bins(entry)):
        return None
    return files


def _unchanged(path, recorded):
    try:
        return path.is_file() and path.stat().st_size == recorded[0] and _sha256(path) == recorded[1]
    except OSError:
        return False


class Tools:
    """The installed tools of one clone, for one architecture."""

    def __init__(self, lock=None, tools=None, arch=None):
        self.lock = load(lock or LOCK)
        self.tools = Path(tools or TOOLS)
        self.arch = arch or host_arch()

    def folder(self, name):
        return self.tools / f"{name}-{self.lock[name]['version']}"

    def entry(self, name):
        return self.lock[name]["archives"][self.arch]

    def refusal(self, name, problem):
        return ToolMissing(f"{name} {self.lock[name]['version']} {problem}; run `{BOOTSTRAP}` to install it")

    def installed(self, name, seen=()):
        """The receipt's files of `name`, with every tool it requires installed too; ToolMissing otherwise."""
        files = receipt(self.folder(name), self.entry(name))
        if files is None:
            raise self.refusal(name, "is not installed as tools.lock.json pins it (missing, older or damaged)")
        for needed in self.lock[name].get("requires", []):
            if needed not in seen:
                try:
                    self.installed(needed, seen + (name,))
                except ToolMissing as error:
                    raise ToolMissing(f"{name} requires {error}") from None
        return files

    def owners(self, program):
        """The tools whose lock entry would provide `program` (a file name), installed or not."""
        found = []
        for name in self.lock:
            entry = self.entry(name)
            if entry["format"] == "exe":
                if program.lower() == f"{name}.exe":
                    found.append(name)
                continue
            for b in _bins(entry):
                relative = f"{b}/{program}" if b else program
                if any(relative.lower() == k.lower() or relative.lower().startswith(k.rstrip("/").lower() + "/")
                       for k in entry["keep"]):
                    found.append(name)
                    break
        return found

    def path(self, program):
        """The absolute path of `program` (`ninja` or `ninja.exe`) inside the tool folder; ToolMissing otherwise."""
        file = program if program.lower().endswith(".exe") else f"{program}.exe"
        if not file or "/" in file or "\\" in file:
            raise ToolMissing(f"{program!r} is not a program name")
        owners = self.owners(file)
        if not owners:
            raise ToolMissing(f"no tool of tools.lock.json provides {file}; run `{BOOTSTRAP}` after adding one")
        problem = None
        for name in owners:
            try:
                files = self.installed(name)
            except ToolMissing as error:
                problem = problem or error
                continue
            for b in _bins(self.entry(name)):
                relative = f"{b}/{file}" if b else file
                recorded = next((v for k, v in files.items() if k.lower() == relative.lower()), None)
                if recorded is None:
                    continue
                path = self.folder(name) / relative
                if not _unchanged(path, recorded):
                    raise self.refusal(name, f"has a missing or changed {file}")
                return path.resolve()
            # installed whole without it: a kept folder that does not hold this program, so not its owner
        raise problem or ToolMissing(f"no tool of tools.lock.json provides {file}")

    def env(self):
        """{variable: folder} a build tool needs beside its path; ToolMissing when the folder's tool is not
        installed as pinned."""
        out = {}
        for variable, name in ENV.items():
            if name not in self.lock:
                continue
            self.installed(name)
            out[variable] = str((self.folder(name) / _bins(self.entry(name))[0]).resolve())
        return out

    def bin_dirs(self):
        """([folder, ...], [problem, ...]): the program folders of each tool that passes the `path` checks (its
        receipt, the tools it requires and every program its folders hold, unchanged), and one problem per tool
        that does not."""
        dirs, problems = [], []
        for name in self.lock:
            try:
                files = self.installed(name)
                entry = self.entry(name)
                for b in _bins(entry):
                    for relative, recorded in files.items():
                        parent = relative.rpartition("/")[0]
                        if parent == b and relative.lower().endswith(".exe") and \
                                not _unchanged(self.folder(name) / relative, recorded):
                            raise self.refusal(name, f"has a missing or changed {relative}")
            except ToolMissing as error:
                problems.append(str(error))
                continue
            dirs.extend(str((self.folder(name) / b).resolve()) for b in _bins(entry))
        return dirs, problems


def tool_path(program, lock=None, tools=None, arch=None):
    """The absolute path of `program` in the clone's tool folder (never `PATH`); ToolMissing when its tool is not
    installed as pinned."""
    return Tools(lock, tools, arch).path(program)


def tool_env(lock=None, tools=None, arch=None):
    """The variables a build tool needs beside its path (`VCPKG_ROOT`); ToolMissing when their tool is missing."""
    return Tools(lock, tools, arch).env()