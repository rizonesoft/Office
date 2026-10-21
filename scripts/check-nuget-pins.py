#!/usr/bin/env python3
"""Keep every NuGet pin in `Directory.Packages.props` on its latest stable release (owner rule, 2026-10-21).

    python scripts/check-nuget-pins.py check              # exit 1 when any pin is behind
    python scripts/check-nuget-pins.py update             # propose them all on one pins/nuget-<key> branch, then email
    python scripts/check-nuget-pins.py update --dry-run   # say what update would do; change and send nothing

Every live `PackageVersion` is checked except `Microsoft.WindowsAppSDK`, which follows the WinUI 3 release rule in
`check-winui-pin.py`. A pin must be an exact stable version (three or four numeric parts); its target is the newest
stable version nuget.org publishes for the package (no prerelease). main, not the checkout, is the baseline; a pin
that is not an exact stable version or is not on nuget.org fails the run. `update` proposes every bump together through
`scripts/lib/pin_proposal.py`: a temporary worktree on `pins/nuget-<key>` from main, only those versions rewritten,
the checks (the file parses and pins them, and every solution builds once one exists), a commit, and an email naming
the branch to merge. The key is a digest of the bumps, so each new set is proposed once.
Exit 0 current or proposed, 1 a pin is behind or a check failed, 2 nuget.org could not be read.
"""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import package_versions
import pin_proposal
from pin_sources import Unreadable, fetch_json, nuget_versions

PROPS = package_versions.PROPS
OWNED_ELSEWHERE = {"Microsoft.WindowsAppSDK": "scripts/check-winui-pin.py"}


def bumps(current, fetch=fetch_json):
    """The bumps as [(package, old, new)] and the problems with pins that cannot be compared."""
    out, problems = [], []
    for package, version in sorted(current.items()):
        if package in OWNED_ELSEWHERE:
            continue
        if package_versions.stable_key(version) is None:
            problems.append(f"{package} {version} is not an exact stable version")
            continue
        versions = nuget_versions(package, fetch)
        if not package_versions.published(version, versions):
            problems.append(f"{package} {version} is not published on nuget.org")
            continue
        newest = package_versions.latest_stable(versions)
        if newest and package_versions.stable_key(newest) > package_versions.stable_key(version):
            out.append((package, version, newest))
    return out, problems


def checks(tree, wanted, build=subprocess.run):
    problems = []
    try:
        have = package_versions.pins((Path(tree) / PROPS).read_text(encoding="utf-8"))
        problems += [f"the rewritten file does not pin {p} {new}" for p, _old, new in wanted if have.get(p) != new]
    except ValueError as exc:
        problems.append(str(exc))
    return problems + pin_proposal.build_problems(tree, build)


def update(wanted, root=ROOT, dry_run=False, build=subprocess.run, mail=pin_proposal.notify):
    lines = [f"{package} {old} -> {new}" for package, old, new in wanted]
    key = "nuget-" + hashlib.sha256("\n".join(lines).encode()).hexdigest()[:12]
    branch = f"pins/{key}"

    def rewrite(tree):
        path = Path(tree) / PROPS
        text = path.read_text(encoding="utf-8")
        for package, old, new in wanted:
            text = package_versions.repinned(text, package, old, new)
        path.write_text(text, encoding="utf-8", newline="")
        return [PROPS]

    return pin_proposal.propose(
        root=root, key=key, branch=branch, rewrite=rewrite, checks=lambda tree: checks(tree, wanted, build),
        message=["deps: move NuGet pins to their latest stable releases",
                 "; ".join(lines) + ". Proposed by the office-nuget-pins task."],
        subject=f"Office: {len(wanted)} NuGet pin update(s) ready to merge",
        body=lambda commit: "\n".join(
            ["Newer stable NuGet releases are out:", ""] + [f"    {line}" for line in lines]
            + ["", f"Branch {branch} (commit {commit[:12]}) moves the pins; its checks passed.",
               "", "Merge it in the repository with:", f"    git merge {branch}"]),
        dry_run=dry_run, mail=mail)


def main(argv=None, fetch=fetch_json, root=ROOT, build=subprocess.run, mail=pin_proposal.notify):
    parser = argparse.ArgumentParser(description="Keep every NuGet pin on its latest stable release.")
    parser.add_argument("mode", choices=("check", "update"))
    parser.add_argument("--dry-run", action="store_true", help="say what update would do; change and send nothing")
    args = parser.parse_args(argv)
    try:
        current = package_versions.pins(pin_proposal.main_file(Path(root), PROPS), f"main:{PROPS}")
        wanted, problems = bumps(current, fetch)
    except Unreadable as exc:
        print(f"check-nuget-pins: could not read {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"check-nuget-pins: {exc}", file=sys.stderr)
        return 1
    if problems:
        print("\n".join(problems))
        return 1
    checked = len([p for p in current if p not in OWNED_ELSEWHERE])
    if not wanted:
        print(f"every NuGet pin is on its latest stable release ({checked} checked; "
              + ", ".join(f"{p} by {s}" for p, s in OWNED_ELSEWHERE.items()) + ")")
        return 0
    print("\n".join(f"{package} {old} is behind {new}" for package, old, new in wanted))
    if args.mode == "check":
        return 1
    try:
        return update(wanted, Path(root), args.dry_run, build, mail)
    except (RuntimeError, ValueError) as exc:  # a git step or the rewrite failed; the worktree is already gone
        print(f"check-nuget-pins: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
