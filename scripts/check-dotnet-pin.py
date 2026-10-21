#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Keep the .NET SDK pin on the newest .NET 11 SDK, and this machine able to build with it (owner rule, 2026-10-21).

    python scripts/check-dotnet-pin.py check              # exit 1 when a newer .NET 11 SDK is out
    python scripts/check-dotnet-pin.py update             # propose it: branch dotnet/<version>, then email
    python scripts/check-dotnet-pin.py update --dry-run   # say what update would do; change and send nothing
    python scripts/check-dotnet-pin.py local              # email once when this machine lacks the pinned SDK

The pin is `sdk.version` in `global.json` (`rollForward: disable`, so the build uses exactly that SDK). The target is
the newest .NET 11 SDK at any stage: the release feed's `latest-sdk` for channel 11.0 (a preview or release candidate
before the release ships, then the release, then each later patch or feature band). The feed is the release metadata
`dotnet-install` reads, from builds.dotnet.microsoft.com.

main, not the checkout, is the baseline. A pin on main that is not a .NET 11 SDK, is not in the feed, or is ahead of
`latest-sdk` fails the run. `update` proposes through `scripts/lib/pin_proposal.py`: a temporary worktree on branch
`dotnet/<version>` from main, only `sdk.version` rewritten, the checks (the file parses and pins the version, the feed
lists it, and once a solution exists the SDK is installed here and every solution builds), a commit, and an email
naming the branch to merge. A proposal is finished when `refs/office-pin/dotnet-<version>` exists.

`local` reads the checkout's pin (what this machine builds) and `dotnet --list-sdks`. A missing SDK is emailed once per
version through `pin_proposal.notice`, with the download page; it never installs anything.
Exit 0 current, proposed or announced, 1 newer SDK pending or a check failed, 2 the feed or dotnet could not be read.
"""
import argparse
import json
from pathlib import Path
import re
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import pin_proposal
from pin_sources import Unreadable, fetch_json

CHANNEL = "11.0"
FEED = f"https://builds.dotnet.microsoft.com/dotnet/release-metadata/{CHANNEL}/releases.json"
DOWNLOAD = f"https://dotnet.microsoft.com/download/dotnet/{CHANNEL[:-2]}"
PIN_FILE = "global.json"
BRANCH = "dotnet/{version}"
KEY = "dotnet-{version}"
SDK = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-(preview|rc)\.(\d+)(?:\.(\d+)\.(\d+))?)?$")
STAGES = {"preview": 0, "rc": 1, None: 2}  # a release sorts after every preview and release candidate of its band
NO_WINDOW = pin_proposal.NO_WINDOW


def sdk_key(version):
    """A sort key for an SDK version (11.0.100-preview.7.26381.103 < 11.0.100-rc.2.26504.105 < 11.0.100 < 11.0.101);
    None for anything else."""
    match = SDK.match(str(version))
    if not match:
        return None
    major, minor, patch, stage, number, build_a, build_b = match.groups()
    return (int(major), int(minor), int(patch), STAGES[stage], int(number or 0), int(build_a or 0), int(build_b or 0))


def feed_sdks(feed):
    """Every SDK version the channel feed lists, and its release (for the notes link), by version."""
    out = {}
    for release in feed.get("releases", []) if isinstance(feed, dict) else []:
        if not isinstance(release, dict):
            continue
        for sdk in [release.get("sdk") or {}] + list(release.get("sdks") or []):
            version = sdk.get("version") if isinstance(sdk, dict) else None
            if isinstance(version, str) and version not in out:
                out[version] = release
    return out


def latest(feed):
    """The channel's newest SDK as (version, release); the feed's latest-sdk, which it must also list."""
    sdks = feed_sdks(feed)
    version = feed.get("latest-sdk") if isinstance(feed, dict) else None
    if not isinstance(version, str) or version not in sdks or sdk_key(version) is None:
        raise Unreadable(f"{FEED}: latest-sdk {version!r} is not an SDK the feed lists")
    if not in_channel(version):
        raise Unreadable(f"{FEED}: latest-sdk {version} is not a .NET {CHANNEL} SDK")
    return version, sdks[version], sdks


def in_channel(version):
    return sdk_key(version) is not None and ".".join(version.split(".")[:2]) == CHANNEL


def pinned_text(text, where=PIN_FILE):
    """The pinned SDK version; refused unless global.json also disables roll-forward, so the pin is the SDK used."""
    try:
        sdk = json.loads(text)["sdk"]
        version, roll = sdk["version"], sdk.get("rollForward")
    except (ValueError, KeyError, TypeError, AttributeError):
        raise ValueError(f"{where}: needs sdk.version") from None
    if not isinstance(version, str):
        raise ValueError(f"{where}: sdk.version must be text")
    if roll != "disable":
        raise ValueError(f'{where}: sdk.rollForward must be "disable", so every build uses exactly the pinned SDK')
    return version


def repinned(text, old, new):
    """The global.json text with only sdk.version changed, so formatting survives."""
    pattern = re.compile(r'("version"\s*:\s*")' + re.escape(old) + '"')
    out, count = pattern.subn(lambda m: m.group(1) + new + '"', text)
    if count != 1 or pinned_text(out) != new:
        raise ValueError(f"the SDK pin {old} was not found exactly once as sdk.version")
    return out


def installed_sdks(run=subprocess.run):
    """The SDK versions `dotnet --list-sdks` reports on this machine."""
    try:
        result = run(["dotnet", "--list-sdks"], capture_output=True, text=True, encoding="utf-8",
                     creationflags=NO_WINDOW)
    except OSError:
        raise Unreadable("dotnet is not on PATH") from None
    if result.returncode != 0:
        raise Unreadable(f"dotnet --list-sdks failed: {(result.stderr or result.stdout).strip()}")
    return {line.split()[0] for line in result.stdout.splitlines() if line.strip()}


def checks(tree, version, sdks, build=subprocess.run, run=subprocess.run):
    """Problems with the proposed pin; an empty list means it may be committed."""
    problems = []
    try:
        if pinned_text((Path(tree) / PIN_FILE).read_text(encoding="utf-8")) != version:
            problems.append("the rewritten file does not pin the new version")
    except ValueError as exc:
        problems.append(str(exc))
    if version not in sdks:
        problems.append(f"the .NET {CHANNEL} release feed does not list SDK {version}")
    if pin_proposal.solutions(tree):
        try:
            if version not in installed_sdks(run):
                problems.append(f".NET SDK {version} is not installed on this machine, so the solution cannot be "
                                f"built; install it from {DOWNLOAD}")
        except Unreadable as exc:
            problems.append(str(exc))
        if not problems:
            problems += pin_proposal.build_problems(tree, build)
    return problems


def update(version, release, old, sdks, root=ROOT, dry_run=False, build=subprocess.run, run=subprocess.run,
           mail=pin_proposal.notify):
    branch = BRANCH.format(version=version)

    def rewrite(tree):
        path = Path(tree) / PIN_FILE
        path.write_text(repinned(path.read_text(encoding="utf-8"), old, version), encoding="utf-8", newline="")
        return [PIN_FILE]

    runtime, date = release.get("release-version", ""), release.get("release-date", "")
    return pin_proposal.propose(
        root=root, key=KEY.format(version=version), branch=branch, rewrite=rewrite,
        checks=lambda tree: checks(tree, version, sdks, build, run),
        message=[f"deps: pin .NET SDK {version}",
                 f"Newest .NET {CHANNEL} SDK, release {runtime} of {date}; was {old}. Proposed by the office-dotnet-pin task."],
        subject=f"Office: .NET SDK {version} is ready to merge",
        body=lambda commit: "\n".join([
            f"A newer .NET {CHANNEL} SDK is out: {version} (.NET {runtime}, released {date}).",
            "", f"Branch {branch} (commit {commit[:12]}) moves global.json from {old} to {version}; its checks passed.",
            "", "Install the SDK on every machine that builds Office (global.json disables roll-forward):",
            f"    {DOWNLOAD}", "", "Then merge it in the repository with:", f"    git merge {branch}",
            "", f"Release notes: {release.get('release-notes', '')}"]),
        dry_run=dry_run, mail=mail)


def local(root=ROOT, run=subprocess.run, mail=pin_proposal.notify, host=None):
    """Announce once when this machine lacks the SDK its checkout pins."""
    try:
        version = pinned_text((Path(root) / PIN_FILE).read_text(encoding="utf-8"))
        have = installed_sdks(run)
    except Unreadable as exc:
        print(f"check-dotnet-pin: could not read {exc}", file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print(f"check-dotnet-pin: {exc}", file=sys.stderr)
        return 1
    if version in have:
        print(f".NET SDK {version}, the one global.json pins, is installed on this machine")
        return 0
    host = host or socket.gethostname()
    line = f".NET SDK {version}, the one global.json pins, is not installed on {host} (it has {', '.join(sorted(have)) or 'none'})"
    print(line)
    return pin_proposal.notice(root=root, key=f"dotnet-local-{version}-{host.lower()}",
                               subject=f"Office: install .NET SDK {version} on {host}",
                               body="\n".join([line, "", "global.json disables roll-forward, so builds fail until it is "
                                               f"installed. Download it from {DOWNLOAD}"]),
                               mail=mail)


def main(argv=None, fetch=fetch_json, root=ROOT, build=subprocess.run, run=subprocess.run, mail=pin_proposal.notify):
    parser = argparse.ArgumentParser(description="Keep the .NET SDK pin on the newest .NET 11 SDK.")
    parser.add_argument("mode", choices=("check", "update", "local"))
    parser.add_argument("--dry-run", action="store_true", help="say what update would do; change and send nothing")
    args = parser.parse_args(argv)
    if args.mode == "local":
        return local(Path(root), run, mail)
    try:
        version, release, sdks = latest(fetch(FEED))
        current = pinned_text(pin_proposal.main_file(Path(root), PIN_FILE), f"main:{PIN_FILE}")
    except Unreadable as exc:
        print(f"check-dotnet-pin: could not read {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"check-dotnet-pin: {exc}", file=sys.stderr)
        return 1
    if not in_channel(current):
        print(f"global.json on main pins {current}, which is not a .NET {CHANNEL} SDK")
        return 1
    if current not in sdks:
        print(f"global.json on main pins {current}, which the .NET {CHANNEL} release feed does not list")
        return 1
    if sdk_key(current) > sdk_key(version):
        print(f"global.json on main pins {current}, ahead of the newest .NET {CHANNEL} SDK {version}")
        return 1
    if sdk_key(current) == sdk_key(version):
        print(f".NET SDK {current} is the newest .NET {CHANNEL} SDK (.NET {release.get('release-version')})")
        return 0
    if args.mode == "check":
        print(f"newer .NET {CHANNEL} SDK {version} (.NET {release.get('release-version')}); the pin is {current}")
        return 1
    try:
        return update(version, release, current, sdks, Path(root), args.dry_run, build, run, mail)
    except (RuntimeError, ValueError) as exc:  # a git step or the rewrite failed; the worktree is already gone
        print(f"check-dotnet-pin: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
