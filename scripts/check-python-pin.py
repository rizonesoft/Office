#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Alert when this machine's Python, which runs the automations and `scripts/`, falls behind the latest stable release.

    python scripts/check-python-pin.py check     # exit 0 current, 1 behind, 2 cannot check
    python scripts/check-python-pin.py notify    # as check, but being behind is emailed once per finding, exit 0

The interpreter running this script must be the newest stable CPython minor on python.org (published, not a
pre-release), at its newest patch. The tooling is stdlib only, so moving is a Python install followed by
`python -m unittest discover -s scripts/tests`. Office has no CI workflow yet, so only this machine is checked. Ported
from RectoPDF's `--scope local` (2026-10-21).
"""
import argparse
import hashlib
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import pin_proposal
from pin_sources import Unreadable, fetch_json, version_key

RELEASES = "https://www.python.org/api/v2/downloads/release/?is_published=true&pre_release=false"
NAME = re.compile(r"^Python (\d+\.\d+\.\d+)$")


def latest_releases(releases):
    """Newest stable version overall and the newest patch of each minor, as key tuples."""
    versions = [version_key(NAME.match(str(r.get("name", "")))[1]) for r in releases
                if isinstance(r, dict) and NAME.match(str(r.get("name", "")))]
    if not versions:
        raise Unreadable(f"{RELEASES}: no stable CPython releases")
    by_minor = {}
    for v in versions:
        by_minor[v[:2]] = max(by_minor.get(v[:2], v), v)
    return max(versions), by_minor


def text(key):
    return ".".join(map(str, key))


def findings(newest, by_minor, local):
    if local[:2] < newest[:2]:
        return [f"this machine's Python {text(local)} is behind the newest stable minor {text(newest[:2])} "
                f"(latest {text(newest)})"]
    if local < by_minor.get(local[:2], local):
        return [f"this machine's Python {text(local)} is behind its latest patch {text(by_minor[local[:2]])}"]
    return []


def main(argv=None, fetch=fetch_json, root=ROOT, local=tuple(sys.version_info[:3]), mail=pin_proposal.notify):
    parser = argparse.ArgumentParser(description="Alert when this machine's Python falls behind the latest stable.")
    parser.add_argument("mode", choices=("check", "notify"))
    args = parser.parse_args(argv)
    try:
        releases = fetch(RELEASES)
        newest, by_minor = latest_releases(releases if isinstance(releases, list) else [])
    except Unreadable as exc:
        print(f"check-python-pin: could not read {exc}", file=sys.stderr)
        return 2
    found = findings(newest, by_minor, tuple(local))
    if not found:
        print(f"this machine runs the newest stable Python ({text(tuple(local))})")
        return 0
    print("\n".join(found))
    if args.mode == "check":
        return 1
    key = "python-" + hashlib.sha256("\n".join(found).encode()).hexdigest()[:12]
    return pin_proposal.notice(root=root, key=key, subject="Office: a newer Python is available",
                               body="\n".join(found + ["", "Install the newer Python on this machine, then run "
                                                           "python -m unittest discover -s scripts/tests."]),
                               mail=mail)


if __name__ == "__main__":
    sys.exit(main())
