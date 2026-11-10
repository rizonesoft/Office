# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Copy this repository's credentials from the Conclave vault into its untracked env file.

    python scripts/import-secrets.py            import every credential, report each by name
    python scripts/import-secrets.py --check    say which credentials the file holds; import nothing

The file is `.secrets/office.env` in the clone (ignored by git, closed to every other user account). Run this once on
a new clone, and again after a credential is replaced in the vault. It reads the vault through `conclave-op` in WSL;
nothing else in the repository needs WSL or the vault afterwards. It prints names and states only, never a value.
Exit 0 when every credential is in the file, 1 when one is missing.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import secret_store  # noqa: E402


def main(argv=None, run=subprocess.run, root=secret_store.ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report what the file holds; read no vault")
    args = parser.parse_args(argv)
    if args.check:
        present = secret_store.read_all(root)
        states = {name: "present" if name in present else "missing" for name in sorted(secret_store.SECRETS)}
    else:
        states = secret_store.import_all(root, run)
    for name, state in states.items():
        print(f"{state:<12}{name}  ({secret_store.SECRETS[name]['use']})")
    missing = [name for name, state in states.items() if state in ("missing", "unavailable")]
    if missing:
        print(f"{len(missing)} credential(s) not in {secret_store.FOLDER}/{secret_store.FILE}: unlock the vault "
              f"(conclave-op in WSL) and run python scripts/import-secrets.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
