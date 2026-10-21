#!/usr/bin/env python3
"""Alert when Office's Conclave SDK kit files drift from the SDK, or the SDK's doctor reports a gap.

    python scripts/check-conclave-kits.py check     # exit 0 in step, 1 drift or a doctor gap, 2 cannot check
    python scripts/check-conclave-kits.py notify    # as check, but drift is emailed once per state, exit 0

The SDK is the checkout `CONCLAVE_SDK_ROOT` names (explicit config), else a `Conclave-SDK` folder beside this
repository (discovery); with neither, the check reports setup required and exits 2 (AGENTS.md: config, then discovery,
then setup required, never a hardcoded path). Every
SDK-managed file of the kits Office installs (base, todo and reviewer: skills, rules and subagents for each agent, and
the kit's `scripts/`) is compared with the SDK's committed `HEAD`, never its working tree, so an SDK change in progress
is not reported; line endings are normalized. Project files (`AGENTS.md`, `docs/`, `todo/`, pins, the reviewer pin)
are not compared, and neither is `.conclave/automations/`, which is Office's own runner, not the kit's (operator,
2026-10-21). A deliberate local difference is listed in `.conclave/kit-drift-allow.txt` as `<path> | <reason>`.
`forge.py doctor` runs for each kit as well. The fix is `forge.py sync <repo> --include-scripts` and a review of the
diff, so this check never changes anything itself. Ported from RectoPDF (2026-10-21).
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import pin_proposal

KITS = ("base", "todo", "reviewer")
ALLOW = ".conclave/kit-drift-allow.txt"
MANAGED = tuple(f"{d}/{k}/" for d in (".agents", ".claude", ".codex") for k in ("skills", "rules")) + (
    ".claude/agents/", "scripts/")


def sdk_root(root=ROOT, environ=os.environ):
    """The SDK checkout from config, else discovered beside this repository; None when neither has forge.py."""
    for candidate in (environ.get("CONCLAVE_SDK_ROOT"), Path(root).resolve().parent / "Conclave-SDK"):
        if candidate and (Path(candidate) / "forge.py").is_file():
            return Path(candidate)
    return None


def git(sdk, *args):
    return subprocess.run(["git", "-C", str(sdk), *args], capture_output=True, creationflags=pin_proposal.NO_WINDOW)


def allowed(root=ROOT):
    path = Path(root) / ALLOW
    if not path.is_file():
        return {}
    entries = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            rel, _, reason = line.partition("|")
            if not reason.strip():
                raise ValueError(f"{ALLOW}: '{line.strip()}' needs a reason after '|'")
            entries[rel.strip()] = reason.strip()
    return entries


def drift(sdk, root=ROOT, allow=None):
    """Repository-relative paths whose content differs from the SDK's committed kit template, or that are missing."""
    allow = allowed(root) if allow is None else allow
    out = []
    for kit in KITS:
        prefix = f"kits/{kit}/templates/"
        listed = git(sdk, "ls-tree", "-r", "--name-only", "HEAD", prefix)
        if listed.returncode != 0:
            raise RuntimeError(f"cannot list {prefix} at the SDK's HEAD: {listed.stderr.decode(errors='replace').strip()}")
        for name in listed.stdout.decode("utf-8").splitlines():
            rel = name[len(prefix):]
            if "__pycache__" in rel or not rel.startswith(MANAGED) or rel in allow:
                continue
            local = Path(root) / rel
            if not local.is_file():
                out.append(f"{rel} is missing (kit {kit})")
                continue
            theirs = git(sdk, "show", f"HEAD:{name}").stdout.replace(b"\r\n", b"\n")
            if local.read_bytes().replace(b"\r\n", b"\n") != theirs:
                out.append(f"{rel} differs from the SDK (kit {kit})")
    return out


def doctor(sdk, root=ROOT, run=subprocess.run):
    """The gaps forge.py doctor reports for each kit. A doctor that fails without naming a gap, or whose report is not
    a list of named checks, could not check, which is never read as healthy."""
    gaps = []
    for kit in KITS:
        result = run([sys.executable, str(Path(sdk) / "forge.py"), "doctor", str(root), kit], capture_output=True,
                     text=True, encoding="utf-8", creationflags=pin_proposal.NO_WINDOW)
        try:
            checks = json.loads(result.stdout)["checks"]
            found = [f"doctor {kit}: {c['status']} {c['name']}" for c in checks if c["status"] != "ok"]
        except (ValueError, KeyError, TypeError):
            raise RuntimeError(f"forge.py doctor {kit} gave no report: {(result.stderr or result.stdout).strip()[:200]}") from None
        if not isinstance(checks, list) or not checks:
            raise RuntimeError(f"forge.py doctor {kit} reported no checks")
        if result.returncode != 0 and not found:
            raise RuntimeError(f"forge.py doctor {kit} exited {result.returncode}: {(result.stderr or '').strip()[:200]}")
        gaps += found
    return gaps


def main(argv=None, root=ROOT, sdk=None, run=subprocess.run, mail=pin_proposal.notify):
    parser = argparse.ArgumentParser(description="Alert when Conclave kit files drift from the SDK.")
    parser.add_argument("mode", choices=("check", "notify"))
    args = parser.parse_args(argv)
    sdk = Path(sdk) if sdk else sdk_root(root)
    if sdk is None or not (sdk / "forge.py").is_file():
        print("check-conclave-kits: setup required: no Conclave SDK checkout found; set CONCLAVE_SDK_ROOT, or clone it "
              f"beside this repository as {Path(root).resolve().parent / 'Conclave-SDK'}", file=sys.stderr)
        return 2
    try:
        found = drift(sdk, root) + doctor(sdk, root, run)
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"check-conclave-kits: {exc}", file=sys.stderr)
        return 2
    if not found:
        print("Office's Conclave kit files match the SDK and the doctor reports no gap")
        return 0
    print("\n".join(found))
    if args.mode == "check":
        return 1
    head = git(sdk, "rev-parse", "--short=12", "HEAD").stdout.decode().strip()
    key = "kits-" + hashlib.sha256((head + "\n" + "\n".join(found)).encode()).hexdigest()[:12]
    return pin_proposal.notice(root=root, key=key, subject="Office: Conclave SDK kits have drifted",
                               body="\n".join([f"Conclave SDK HEAD {head}:"] + found + [
                                   "", f"Review and sync: python {sdk / 'forge.py'} sync {root} --include-scripts",
                                   f"A deliberate difference belongs in {ALLOW} with its reason."]), mail=mail)


if __name__ == "__main__":
    sys.exit(main())
