# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""design/inventory/authoring.json: for each app folder of the inventory, the TODO section that authors that app's
domain (D02 T01 §22). The ownership check (`scripts/inventory-report.py --owners`) holds an app's records to their
owners from the stamp of that section, and the checker (`scripts/check-inventory.py`) refuses a file that names no
section for an app. Both read the file here, so neither can accept what the other refuses.

The file is one JSON object: every app folder is a key, no key is anything else, and every value is a section
reference (`DNN TNN §N`) the TODO tree holds.
"""
import json
from pathlib import Path
import re

FILE = "authoring.json"
REFERENCE = re.compile(r"D\d{2} T\d{2} §[1-9]\d*")


def app_folders(inventory):
    """The inventory's app folders (the shell counts as one): every folder directly under it."""
    return sorted(p.name for p in Path(inventory).iterdir() if p.is_dir())


def _pairs(pairs):
    keys = [key for key, _ in pairs]
    repeated = sorted({key for key in keys if keys.count(key) > 1})
    if repeated:
        raise ValueError(f"repeated key {', '.join(repeated)}")
    return dict(pairs)


def read(inventory, section_exists):
    """(the mapping of app folder to section reference, problems). `section_exists(ref)` says whether the TODO tree
    holds a section. With any problem the mapping is None: a file that is wrong in one place is not relied on in
    another. Each problem is one line that starts with the file's path."""
    inventory = Path(inventory)
    path = inventory / FILE
    if not path.is_file():
        return None, [f"{path}: missing: it names, for each app folder, the section that authors that app's domain"]
    try:
        data = json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=_pairs)
    except (OSError, UnicodeDecodeError, ValueError, RecursionError) as exc:
        return None, [f"{path}: cannot be read ({exc})"]
    if not isinstance(data, dict):
        return None, [f"{path}: not a JSON object of app folder to section reference"]
    apps, problems = app_folders(inventory), []
    for app in apps:
        if app not in data:
            problems.append(f"{path}: no section named for the app folder {app}")
    for key, value in data.items():
        if key not in apps:
            problems.append(f"{path}: {key!r} is not an app folder of the inventory ({', '.join(apps)})")
        elif not isinstance(value, str) or not REFERENCE.fullmatch(value):
            problems.append(f"{path}: {key}: {value!r} is not a section reference (DNN TNN §N)")
        elif not section_exists(value):
            problems.append(f"{path}: {key}: {value} is not a section of the TODO tree")
    return (None, problems) if problems else (data, [])
