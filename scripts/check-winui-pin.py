#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Keep the WinUI 3 pin on the latest stable release (owner rule, 2026-10-20).

    python scripts/check-winui-pin.py check              # exit 1 when a newer stable release exists
    python scripts/check-winui-pin.py update             # propose it: branch winui/<version>, then email
    python scripts/check-winui-pin.py update --dry-run   # say what update would do; change and send nothing

The pin is the `Microsoft.WindowsAppSDK` version in `Directory.Packages.props`. A stable release is a GitHub release
of the microsoft-ui-xaml repository tagged `winui3/release/<major>.<minor>.<patch>`, not marked a prerelease or draft,
and without "experimental" in its tag or name. The newest such release must also be published on NuGet under the same
version.

main, not the checkout, is the baseline: when main already pins the release, nothing is proposed. A pin on main that is
not an exact stable version, is ahead of the newest stable release, or is not on NuGet fails the run. `update` proposes
through `scripts/lib/pin_proposal.py`: a temporary worktree on branch `winui/<version>` from main, only the pin
rewritten, the checks (the file parses, NuGet has the version, and every solution builds once one exists), a commit,
and an email naming the branch to merge. A proposal is finished when `refs/office-pin/winui-<version>` exists; a
finished release is never proposed again, even after its branch is deleted. A failed check leaves no branch and exits 1,
so the scheduled run reports it through the automations alert.
Exit 0 current or proposed, 1 newer release pending or a check failed, 2 the releases or NuGet could not be read.
"""
import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import package_versions
import pin_proposal
from pin_sources import Unreadable, fetch_json, nuget_versions

PROPS = package_versions.PROPS
PACKAGE = "Microsoft.WindowsAppSDK"
REPOSITORY = "microsoft/microsoft-ui-xaml"
RELEASES = f"https://api.github.com/repos/{REPOSITORY}/releases?per_page=100"
TAG = re.compile(r"^winui3/release/(\d+)\.(\d+)\.(\d+)$")
STABLE = re.compile(r"^\d+\.\d+\.\d+$")
BRANCH = "winui/{version}"
KEY = "winui-{version}"
NO_WINDOW = pin_proposal.NO_WINDOW


def latest_stable(releases):
    """The newest stable release as (version text, release), or None. Experimental and prerelease tags never count."""
    best = None
    for release in releases:
        if not isinstance(release, dict):
            continue
        tag = str(release.get("tag_name", ""))
        match = TAG.match(tag)
        name = str(release.get("name") or "")
        # The tag pattern already refuses a "-experimental" suffix; the name catches a release labelled experimental
        # under a plain version tag.
        if not match or release.get("prerelease") or release.get("draft") or "experimental" in name.lower():
            continue
        key = tuple(int(n) for n in match.groups())
        if best is None or key > best[0]:
            best = (key, release)
    return (".".join(map(str, best[0])), best[1]) if best else None


def pinned_text(text, where=PROPS):
    version = package_versions.pins(text, where).get(PACKAGE)
    if not version:
        raise ValueError(f"{where}: needs a PackageVersion for {PACKAGE} with a Version")
    return version


def pinned(props_path=ROOT / PROPS):
    return pinned_text(Path(props_path).read_text(encoding="utf-8"), props_path)


def main_pin(root=ROOT):
    return pinned_text(pin_proposal.main_file(root, PROPS), f"main:{PROPS}")


def newer(version, than):
    return tuple(int(n) for n in version.split(".")) > tuple(int(n) for n in than.split("."))


def git(*args, cwd=ROOT, check=True):
    return pin_proposal.git(*args, cwd=cwd, check=check)


def checks(tree, version, nuget, build=subprocess.run):
    """Problems with the proposed pin; an empty list means it may be committed."""
    problems = []
    try:
        if pinned(Path(tree) / PROPS) != version:
            problems.append("the rewritten file does not pin the new version")
    except ValueError as exc:
        problems.append(str(exc))
    if version not in nuget:
        problems.append(f"NuGet has no {PACKAGE} {version}")
    return problems + pin_proposal.build_problems(tree, build)


def update(version, release, old, nuget, root=ROOT, dry_run=False, build=subprocess.run, mail=pin_proposal.notify):
    branch = BRANCH.format(version=version)

    def rewrite(tree):
        props = Path(tree) / PROPS
        text = props.read_text(encoding="utf-8")
        props.write_text(package_versions.repinned(text, PACKAGE, old, version), encoding="utf-8", newline="")
        return [PROPS]

    published = str(release.get("published_at", ""))[:10]
    return pin_proposal.propose(
        root=root, key=KEY.format(version=version), branch=branch, rewrite=rewrite,
        checks=lambda tree: checks(tree, version, nuget, build),
        message=[f"deps: pin WinUI 3 (Windows App SDK) {version}",
                 f"Newest stable release {release.get('tag_name')} published {published}; was {old}. "
                 "Proposed by the office-winui-pin task."],
        subject=f"Office: WinUI 3 {version} is ready to merge",
        body=lambda commit: "\n".join([
            f"A newer stable WinUI 3 release is out: {release.get('tag_name')} (published {published}).",
            "", f"Branch {branch} (commit {commit[:12]}) moves the pin from {old} to {version}; its checks passed.",
            "", "Merge it in the repository with:", f"    git merge {branch}",
            "", f"Release notes: {release.get('html_url', '')}"]),
        dry_run=dry_run, mail=mail)


def main(argv=None, fetch=fetch_json, root=ROOT, build=subprocess.run, mail=pin_proposal.notify):
    parser = argparse.ArgumentParser(description="Keep the WinUI 3 pin on the latest stable release.")
    parser.add_argument("mode", choices=("check", "update"))
    parser.add_argument("--dry-run", action="store_true", help="say what update would do; change and send nothing")
    args = parser.parse_args(argv)
    try:
        releases = fetch(RELEASES)
        latest = latest_stable(releases if isinstance(releases, list) else [])
        if latest is None:
            raise Unreadable("no stable winui3/release tag was found")
        version, release = latest
        current = main_pin(Path(root))
        nuget = set(nuget_versions(PACKAGE, fetch))
    except Unreadable as exc:
        print(f"check-winui-pin: could not read {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"check-winui-pin: {exc}", file=sys.stderr)
        return 1
    if not STABLE.match(current):
        print(f"{PACKAGE} {current} on main is not an exact stable version; pin a stable WinUI 3 release")
        return 1
    if newer(current, version):
        print(f"{PACKAGE} {current} on main is ahead of the newest stable WinUI 3 release {version}")
        return 1
    if current not in nuget:
        print(f"{PACKAGE} {current} on main is not published on NuGet")
        return 1
    if not newer(version, current):
        print(f"{PACKAGE} {current} is the latest stable WinUI 3 release ({release.get('tag_name')})")
        return 0
    if args.mode == "check":
        print(f"newer stable WinUI 3 release {version} ({release.get('tag_name')}); the pin is {current}")
        return 1
    try:
        return update(version, release, current, nuget, Path(root), args.dry_run, build, mail)
    except (RuntimeError, ValueError) as exc:  # a git step or the rewrite failed; the worktree is already gone
        print(f"check-winui-pin: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
