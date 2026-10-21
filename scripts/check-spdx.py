#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Refuse a tracked source file that does not state its licence.

    python scripts/check-spdx.py                 # every tracked source file in this repository
    python scripts/check-spdx.py --allow MIT     # also accept MIT, which THIRD-PARTY-NOTICES.md must record

Source files are the tracked `.py`, `.mjs`, `.ps1`, `.sh`, `.cs` and `.xaml` files, and every tracked file under
`scripts/hooks/` (git hooks have no extension). Each must carry exactly one SPDX licence identifier line in its first
10 lines, naming one licence (a compound expression such as `A AND B` is refused), and must exist in the working tree.
Rizonesoft code is `GPL-3.0-or-later`. A vendored third-party file keeps its own identifier, accepted only when it is
named with `--allow` and `THIRD-PARTY-NOTICES.md` records that licence on a `- Licence: <identifier>` line, so a new
licence cannot slip in without its notice.

Exit 0 when every file passes, 1 with one line per refused file, 2 when the arguments are invalid or git cannot list
the files. Stdlib only.
"""
import argparse
import codecs
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
# The tag opens the line, after at most a comment marker (so "NotSPDX-..." or "x_SPDX-..." is no declaration), and
# the declaration runs to the end of the line, less a closing comment marker, so a compound expression is read whole
# rather than by its first identifier.
DECLARATION = re.compile(r"^[ \t]*(?:#|//|<!--|/\*|\*)?[ \t]*" + re.escape(TAG) + r"[ \t]*(.*?)[ \t]*(?:-->|\*/)?[ \t]*$")
SINGLE = re.compile(r"[A-Za-z0-9.+-]+")
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


def encoding(path):
    """The file's encoding from its byte-order mark (PowerShell may write UTF-8, UTF-16 or UTF-32 with one), else
    UTF-8. The codec named drops the mark, so the anchored match reads line one as written."""
    with open(path, "rb") as handle:
        head = handle.read(4)
    for bom, codec in ((codecs.BOM_UTF32_LE, "utf-32"), (codecs.BOM_UTF32_BE, "utf-32"),
                       (codecs.BOM_UTF8, "utf-8-sig"), (codecs.BOM_UTF16_LE, "utf-16"),
                       (codecs.BOM_UTF16_BE, "utf-16")):
        if head.startswith(bom):  # UTF-32 LE is tried before UTF-16 LE, whose mark is its prefix
            return codec
    return "utf-8"


def declarations(path):
    """Every SPDX licence declaration in the file's first lines, as written."""
    found = []
    with open(path, encoding=encoding(path), errors="replace") as handle:
        for _, line in zip(range(HEAD_LINES), handle):
            match = DECLARATION.search(line.rstrip("\r\n"))
            if match:
                found.append(match.group(1))
    return found


def identifier(path):
    """The file's one SPDX identifier, or None when it has no declaration or more than one."""
    found = declarations(path)
    return found[0] if len(found) == 1 else None


def problems(root, allow=()):
    accepted = {OWN, *allow}
    found = []
    for rel in tracked(root):
        path = Path(root) / rel
        if not path.is_file():  # the index still holds it, so it cannot be certified from the working tree
            found.append(f"{rel}: tracked but missing from the working tree, so its licence cannot be read")
            continue
        declared = declarations(path)
        if not declared:
            found.append(f"{rel}: no {TAG} line in its first {HEAD_LINES} lines")
        elif len(declared) > 1:
            found.append(f"{rel}: {len(declared)} {TAG} lines; a file declares its licence once")
        elif not SINGLE.fullmatch(declared[0]):
            found.append(f"{rel}: '{declared[0]}' is not a single licence identifier")
        elif declared[0] not in accepted:
            found.append(f"{rel}: {declared[0]} is not {OWN} or an allowed third-party licence")
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
