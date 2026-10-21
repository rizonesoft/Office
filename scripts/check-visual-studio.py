#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Alert when this machine's Visual Studio 2026 is behind its latest servicing release.

    python scripts/check-visual-studio.py check     # exit 0 current, 1 behind or missing, 2 cannot check
    python scripts/check-visual-studio.py notify    # as check, but being behind is emailed once per release, exit 0

Office builds WinUI 3 in C# on .NET 11, which needs Visual Studio 2026 (version 18). The installed versions come from
`vswhere.exe`; the latest servicing release comes from version 18's stable release channel manifest
(`https://aka.ms/vs/18/stable/channel`). Visual Studio is installed per machine, not pinned in the repository, so this
check alerts and never changes anything: the Visual Studio Installer applies the update. Ported from RectoPDF
(2026-10-21), which reads the major from its C++ toolset instead.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import pin_proposal
from pin_sources import Unreadable, fetch_json, version_key

MAJOR = 18  # Visual Studio 2026, the first that builds .NET 11
CHANNEL = "https://aka.ms/vs/{major}/stable/channel"
VSWHERE = (Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Microsoft Visual Studio"
           / "Installer" / "vswhere.exe")


def installed(major=MAJOR, run=subprocess.run, vswhere=VSWHERE):
    """Installed (display version, product name) for that major, newest first; empty when none."""
    if not Path(vswhere).is_file():
        raise Unreadable(f"{vswhere} not found")
    result = run([str(vswhere), "-all", "-format", "json", "-utf8", "-version", f"[{major}.0,{major + 1}.0)"],
                 capture_output=True, text=True, encoding="utf-8", creationflags=pin_proposal.NO_WINDOW)
    if result.returncode != 0:
        raise Unreadable(f"vswhere failed: {result.stderr.strip()}")
    try:
        rows = [(i.get("catalog", {}).get("productDisplayVersion", ""), i.get("displayName", ""))
                for i in json.loads(result.stdout or "[]") if not i.get("isPrerelease")]
    except (ValueError, AttributeError) as exc:
        raise Unreadable(f"vswhere output: {exc}") from None
    return sorted((r for r in rows if version_key(r[0])), key=lambda r: version_key(r[0]), reverse=True)


def latest(major=MAJOR, fetch=fetch_json):
    channel = fetch(CHANNEL.format(major=major))
    version = str((channel.get("info") or {}).get("productDisplayVersion", "")) if isinstance(channel, dict) else ""
    if version_key(version) is None:
        raise Unreadable(f"{CHANNEL.format(major=major)}: no productDisplayVersion")
    return version


def main(argv=None, fetch=fetch_json, root=ROOT, run=subprocess.run, vswhere=VSWHERE, mail=pin_proposal.notify):
    parser = argparse.ArgumentParser(description="Alert when Visual Studio 2026 is behind its latest servicing release.")
    parser.add_argument("mode", choices=("check", "notify"))
    args = parser.parse_args(argv)
    try:
        have = installed(MAJOR, run, vswhere)
        newest = latest(MAJOR, fetch)
    except Unreadable as exc:
        print(f"check-visual-studio: could not read {exc}", file=sys.stderr)
        return 2
    if not have:
        print(f"no stable Visual Studio {MAJOR} (2026) is installed, but .NET 11 needs it")
        return 1
    behind = [(v, name) for v, name in have if version_key(v) < version_key(newest)]
    if not behind:
        print(f"{have[0][1]} {have[0][0]} is the latest servicing release")
        return 0
    lines = [f"{name} {v} is behind {newest}" for v, name in behind]
    print("\n".join(lines))
    if args.mode == "check":
        return 1
    return pin_proposal.notice(root=root, key=f"vs-{newest}", subject=f"Office: Visual Studio {newest} is available",
                               body="\n".join(lines + ["", "Update it from the Visual Studio Installer."]), mail=mail)


if __name__ == "__main__":
    sys.exit(main())
