#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Refuse a tracked source file that does not state its licence.

    python scripts/check-spdx.py                 # every tracked source file in this repository
    python scripts/check-spdx.py --allow MIT     # also accept MIT, which THIRD-PARTY-NOTICES.md must record

Source files are the tracked `.py`, `.mjs`, `.ps1`, `.sh`, `.cs` and `.xaml` files, and every tracked file under
`scripts/hooks/` (git hooks have no extension). Each must carry an SPDX licence identifier line in its first 10 lines.
Rizonesoft code is `GPL-3.0-or-later`. A vendored third-party file keeps its own identifier, accepted only when it is
named with `--allow` and `THIRD-PARTY-NOTICES.md` records that licence on a `- Licence: <identifier>` line, so a new
licence cannot slip in without its notice.

Exit 0 when every file passes, 1 with one line per refused file, 2 when the arguments are invalid or git cannot list
the files. Stdlib only.
"""
import argparse
from pathlib import Path
import re
import subprocess
import sys

OWN = "GPL-3.0-or-later"
EXTENSIONS = {".py", ".mjs", ".ps1", ".sh", ".cs", ".xaml"}
HOOKS = "scripts/hooks/"
HEAD_LINES = 10
NOTICES = "THIRD-PARTY-NOTICES.md"
# Built from parts so this file's own text is not read as a licence tag by REUSE tooling.
TAG = "SPDX-" + "License-Identifier:"
IDENTIFIER = re.compile(re.escape(TAG) + r"\s*([A-Za-z0-9.+-]+)")
NOTICE_LICENCE = re.compile(r"^- Licence: ([A-Za-z0-9.+-]+?)\.?(?:\s|$)", re.M)


def tracked(root):
    """Repository-relative paths of the tracked source files, in git's order."""
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True)
    if listed.returncode != 0:
        raise OSError(listed.stderr.decode(errors="replace").strip() or "git ls-files failed")
    paths = [p for p in listed.stdout.decode("utf-8").split("\0") if p]
    return [p for p in paths if Path(p).suffix.lower() in EXTENSIONS or p.startswith(HOOKS)]


def recorded_licences(root):
    """The identifiers THIRD-PARTY-NOTICES.md records on its `- Licence:` lines."""
    path = Path(root) / NOTICES
    if not path.is_file():
        return set()
    return set(NOTICE_LICENCE.findall(path.read_text(encoding="utf-8")))


def identifier(path):
    """The SPDX identifier in the file's first lines, or None."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        for _, line in zip(range(HEAD_LINES), handle):
            match = IDENTIFIER.search(line)
            if match:
                return match.group(1)
    return None


def problems(root, allow=()):
    accepted = {OWN, *allow}
    found = []
    for rel in tracked(root):
        path = Path(root) / rel
        if not path.is_file():  # tracked but deleted in the working tree: nothing to check
            continue
        ident = identifier(path)
        if ident is None:
            found.append(f"{rel}: no {TAG} line in its first {HEAD_LINES} lines")
        elif ident not in accepted:
            found.append(f"{rel}: {ident} is not {OWN} or an allowed third-party licence")
    return found


def main(argv=None, root=None):
    parser = argparse.ArgumentParser(description="Refuse a tracked source file without an SPDX licence identifier.")
    parser.add_argument("--allow", action="append", default=[], metavar="IDENTIFIER",
                        help="a third-party licence to accept; THIRD-PARTY-NOTICES.md must record it")
    args = parser.parse_args(argv)
    root = Path(root) if root else Path(__file__).resolve().parent.parent
    unrecorded = sorted(set(args.allow) - recorded_licences(root))
    if unrecorded:
        print(f"check-spdx: {', '.join(unrecorded)} not recorded on a '- Licence:' line in {NOTICES}", file=sys.stderr)
        return 2
    try:
        found = problems(root, args.allow)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"check-spdx: cannot list the tracked files: {exc}", file=sys.stderr)
        return 2
    for line in found:
        print(line)
    if found:
        return 1
    print(f"spdx: every tracked source file states its licence ({len(tracked(root))} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
