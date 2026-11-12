# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Load `tools.lock.json`, the pins of the build tools the clone carries (D00 T04 §1), strictly.

The file is an object keyed by tool name. Each tool has a `version`, an `archives` object with exactly one entry per
host architecture (`x64`, `arm64`), an optional `requires` list (tools that must be installed with it: `vcpkg` needs
`vcpkg-registry`) and an optional `note`. Each archive has `url` (https only), `sha256` (64 lowercase hex), `size`
(bytes), `format` (`zip`, `tar.xz` or `exe`), `keep` (the member paths or path prefixes to unpack; empty for an `exe`),
`bin` (the folders, relative to the tool's folder, that hold its programs) and an optional `note`. Anything else is
refused with the tool's name, so a typo can never become a download from the wrong place.
"""
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
