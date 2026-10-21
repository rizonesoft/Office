#!/usr/bin/env python3
"""Alert when Office's Conclave SDK kit files drift from the SDK, or the SDK's doctor reports a gap.

    python scripts/check-conclave-kits.py check     # exit 0 in step, 1 drift or a doctor gap, 2 cannot check
    python scripts/check-conclave-kits.py notify    # as check, but drift is emailed once per state, exit 0

The SDK is the checkout named by `CONCLAVE_SDK_ROOT`, or `R:\\GitHub\\Conclave-SDK` (this machine's default). Every
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

DEFAULT_SDK = r"R:\GitHub\Conclave-SDK"
KITS = ("base", "todo", "reviewer")
ALLOW = ".conclave/kit-drift-allow.txt"
MANAGED = tuple(f"{d}/{k}/" for d in (".agents", ".claude", ".codex") for k in ("skills", "rules")) + (
    ".claude/agents/", "scripts/")


def sdk_root():
    return Path(os.environ.get("CONCLAVE_SDK_ROOT") or DEFAULT_SDK)


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


def doctor(sdk, root=ROOT):
    gaps = []
    for kit in KITS:
        result = subprocess.run([sys.executable, str(sdk / "forge.py"), "doctor", str(root), kit], capture_output=True,
                                text=True, encoding="utf-8", creationflags=pin_proposal.NO_WINDOW)
        try:
            report = json.loads(result.stdout)
        except ValueError:
            gaps.append(f"forge.py doctor {kit} failed: {(result.stderr or result.stdout).strip()[:200]}")
            continue
        gaps += [f"doctor {kit}: {c['status']} {c['name']}" for c in report.get("checks", []) if c.get("status") != "ok"]
    return gaps


def main(argv=None, root=ROOT, sdk=None, mail=pin_proposal.notify):
    parser = argparse.ArgumentParser(description="Alert when Conclave kit files drift from the SDK.")
    parser.add_argument("mode", choices=("check", "notify"))
    args = parser.parse_args(argv)
    sdk = Path(sdk) if sdk else sdk_root()
    if not (sdk / "forge.py").is_file():
        print(f"check-conclave-kits: no Conclave SDK at {sdk} (set CONCLAVE_SDK_ROOT)", file=sys.stderr)
        return 2
    try:
        found = drift(sdk, root) + doctor(sdk, root)
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
