#!/usr/bin/env python3
"""Keep the WinUI 3 pin on the latest stable release (owner rule, 2026-10-20).

    python scripts/check-winui-pin.py check              # exit 1 when a newer stable release exists
    python scripts/check-winui-pin.py update             # propose it: branch winui/<version>, then email
    python scripts/check-winui-pin.py update --dry-run   # say what update would do; change and send nothing

The pin is the `Microsoft.WindowsAppSDK` version in `Directory.Packages.props`. A stable release is a GitHub release
of the microsoft-ui-xaml repository tagged `winui3/release/<major>.<minor>.<patch>`, not marked a prerelease and
without "experimental" in its tag or name. The newest such release must also be published on NuGet under the same version.

`update` never touches the operator's checkout or main. It adds a temporary git worktree on a new branch
`winui/<version>` from main, rewrites only the pinned version there, runs the checks (the file parses, NuGet has the
version, and, once a solution exists, `dotnet build` passes), commits, removes the worktree and emails the operator
which branch to merge. A failed check removes the branch and exits 1, so the scheduled run reports the failure
through the automations alert. A branch that already exists means the release was proposed before: nothing is redone.
Exit 0 current or proposed, 1 newer release pending or a check failed, 2 the releases or NuGet could not be read.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "Directory.Packages.props"
PACKAGE = "Microsoft.WindowsAppSDK"
REPOSITORY = "microsoft/microsoft-ui-xaml"
RELEASES = f"https://api.github.com/repos/{REPOSITORY}/releases?per_page=100"
NUGET = f"https://api.nuget.org/v3-flatcontainer/{PACKAGE.lower()}/index.json"
TAG = re.compile(r"^winui3/release/(\d+)\.(\d+)\.(\d+)$")
BRANCH = "winui/{version}"
NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW: a scheduled run opens no console


class Unreadable(Exception):
    pass


def fetch_json(url, opener=urllib.request.urlopen):
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "office-2028-winui-pin"})
    try:
        with opener(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # any network or decode failure means the source could not be read
        raise Unreadable(f"{url.split('?')[0]}: {type(exc).__name__}: {exc}") from None


def latest_stable(releases):
    """The newest stable release as (version text, release), or None. Experimental and prerelease tags never count."""
    best = None
    for release in releases:
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


def pinned(props_path=PROPS):
    root = ET.parse(props_path).getroot()
    hits = [e for e in root.iter("PackageVersion") if e.get("Include") == PACKAGE]
    if len(hits) != 1 or not hits[0].get("Version"):
        raise ValueError(f"{props_path}: needs exactly one PackageVersion for {PACKAGE} with a Version")
    return hits[0].get("Version")


def repinned(text, old, new):
    """The props text with only the pinned version changed, so formatting and comments survive."""
    pattern = re.compile(r'(<PackageVersion\s+Include="' + re.escape(PACKAGE) + r'"\s+Version=")' + re.escape(old) + '"')
    out, count = pattern.subn(lambda m: m.group(1) + new + '"', text)
    if count != 1:
        raise ValueError(f"the {PACKAGE} pin {old} was not found exactly once")
    return out


def newer(version, than):
    return tuple(int(n) for n in version.split(".")) > tuple(int(n) for n in than.split("."))


def git(*args, cwd=ROOT, check=True):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                            creationflags=NO_WINDOW)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {(result.stderr or result.stdout).strip()}")
    return result


def checks(tree, version, nuget_versions, build=subprocess.run):
    """Problems with the proposed pin; an empty list means it may be committed."""
    problems = []
    try:
        if pinned(tree / "Directory.Packages.props") != version:
            problems.append("the rewritten file does not pin the new version")
    except (ET.ParseError, ValueError) as exc:
        problems.append(f"Directory.Packages.props: {exc}")
    if version not in nuget_versions:
        problems.append(f"NuGet has no {PACKAGE} {version}")
    solutions = sorted(p for p in tree.rglob("*.sln*") if p.suffix in (".sln", ".slnx") and "build" not in p.parts)
    for solution in solutions:
        result = build(["dotnet", "build", str(solution), "-c", "Release"], cwd=tree, capture_output=True, text=True,
                       creationflags=NO_WINDOW)
        if result.returncode != 0:
            problems.append(f"dotnet build {solution.relative_to(tree)} failed: {(result.stdout or '')[-400:]}")
    return problems


def notify(subject, body, dry_run=False):
    """Email the operator through the automations' sender (the same vault key and SMTP2GO path as the alerts)."""
    if dry_run:
        print(f"would email: {subject}\n{body}")
        return
    sys.path.insert(0, str(ROOT / ".conclave" / "automations"))
    import alert
    alert.send(alert.key(), subject, body)


def update(version, release, nuget_versions, root=ROOT, dry_run=False, build=subprocess.run, mail=notify):
    branch = BRANCH.format(version=version)
    if git("rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", cwd=root, check=False).returncode == 0:
        print(f"{branch} already exists: release {version} was proposed before")
        return 0
    if dry_run:
        print(f"would create {branch} from main with {PACKAGE} {version}, check it, commit, and email the operator")
        return 1
    with tempfile.TemporaryDirectory(prefix="winui-pin-", dir=root / "build" if (root / "build").is_dir() else None) as tmp:
        tree = Path(tmp) / "tree"
        git("worktree", "add", "-b", branch, str(tree), "main", cwd=root)
        committed = False
        try:
            props = tree / "Directory.Packages.props"
            old = pinned(props)
            props.write_text(repinned(props.read_text(encoding="utf-8"), old, version), encoding="utf-8", newline="")
            problems = checks(tree, version, nuget_versions, build)
            if problems:
                print("checks failed, nothing proposed:\n- " + "\n- ".join(problems), file=sys.stderr)
                return 1
            git("add", "Directory.Packages.props", cwd=tree)
            git("commit", "-q", "-m", f"deps: pin WinUI 3 (Windows App SDK) {version}",
                "-m", f"Newest stable release {release.get('tag_name')} published {release.get('published_at', '')[:10]}; "
                      f"was {old}. Proposed by the office-2028-winui-pin task.", cwd=tree)
            commit = git("rev-parse", "HEAD", cwd=tree).stdout.strip()
            committed = True
        finally:
            git("worktree", "remove", "--force", str(tree), cwd=root, check=False)
            if not committed:
                git("branch", "-D", branch, cwd=root, check=False)
    mail(f"Office-2028: WinUI 3 {version} is ready to merge",
         "\n".join([f"A newer stable WinUI 3 release is out: {release.get('tag_name')} "
                    f"(published {release.get('published_at', '')[:10]}).",
                    "", f"Branch {branch} (commit {commit[:12]}) moves the pin from {old} to {version}; its checks passed.",
                    "", "Merge it in the repository with:", f"    git merge {branch}",
                    "", f"Release notes: {release.get('html_url', '')}"]), dry_run)
    print(f"proposed {version} on {branch} ({commit[:12]}) and emailed the operator")
    return 0


def main(argv=None, fetch=fetch_json, root=ROOT, build=subprocess.run, mail=notify):
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
        current = pinned(Path(root) / "Directory.Packages.props")
        if not newer(version, current):
            print(f"{PACKAGE} {current} is the latest stable WinUI 3 release ({release.get('tag_name')})")
            return 0
        if args.mode == "check":
            print(f"newer stable WinUI 3 release {version} ({release.get('tag_name')}); the pin is {current}")
            return 1
        nuget = fetch(NUGET).get("versions", [])
    except Unreadable as exc:
        print(f"check-winui-pin: could not read {exc}", file=sys.stderr)
        return 2
    return update(version, release, set(nuget), Path(root), args.dry_run, build, mail)


if __name__ == "__main__":
    sys.exit(main())
