# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The states of a Word document the inventory is captured in, beside the new blank one (D02 T01 §36).

Word shows some of Backstage only for a document in another state: saved to a file, read-only, marked as final, in
an older format, in Protected View. This module is the list written by hand that names each state, how
`scripts/make-word-state-fixtures.py` makes a fixture document in it, and what Word must say of that document
before anything is captured over it. The script, the capture (`scripts/capture-ui.py --backstage --state`) and
`scripts/check-inventory.py` share it. It never touches Word.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

FOLDER = ("fixtures", "word-states")  # under the scratch root: fixtures never land in the repository
TEXT = "A fixture document of the Rizonesoft Office inventory capture."  # all a fixture holds
DOCX, DOC97 = 16, 0  # wdFormatDocumentDefault, wdFormatDocument97
INTERNET_ZONE = 3  # the zone a file from the internet carries in its Zone.Identifier stream
CURRENT_MODE = 15  # Document.CompatibilityMode of a document in the current format

# Each state: its name (the file's stem, the value of `captureState`, a part of every record id of the state), what
# a builder calls it, the document in words (`condition`), the format it is saved in, the properties set on the
# document before its last save (`set`), what is done to the file once Word has closed it (`attribute`, `zone`), how
# it is opened (`view`: among Documents, or in a Protected View window, which is not among them), and what Word
# must say of it when it is opened again (`confirm`). Only the properties `confirm` names are asked: Word refuses to
# say whether a document marked as final recommends read-only, and whether one that recommends it is final.
STATES = (
    {"name": "saved", "title": "Saved document", "condition": "an ordinary document saved to a file",
     "file": "saved.docx", "format": DOCX, "set": (), "view": "document",
     "confirm": {"ReadOnly": False, "ReadOnlyRecommended": False, "Final": False,
                 "CompatibilityMode": CURRENT_MODE, "RemovePersonalInformation": False}},
    {"name": "read-only", "title": "Read-only file", "condition": "a document whose file is read-only",
     "file": "read-only.docx", "format": DOCX, "set": (), "attribute": "read-only", "view": "document",
     "confirm": {"ReadOnly": True, "ReadOnlyRecommended": False}},
    {"name": "read-only-recommended", "title": "Read-only recommended",
     "condition": "a document saved to always open read-only",
     "file": "read-only-recommended.docx", "format": DOCX, "set": (("ReadOnlyRecommended", True),),
     "view": "document", "confirm": {"ReadOnly": True, "ReadOnlyRecommended": True}},
    {"name": "final", "title": "Marked as final", "condition": "a document marked as final",
     "file": "final.docx", "format": DOCX, "set": (("Final", True),), "view": "document",
     "confirm": {"ReadOnly": True, "Final": True}},
    {"name": "compatibility", "title": "Compatibility mode",
     "condition": "a document in the Word 97-2003 format",
     "file": "compatibility.doc", "format": DOC97, "set": (), "view": "document",
     "confirm": {"ReadOnly": False, "CompatibilityMode": 11}},
    {"name": "personal-information-removed", "title": "Personal information removed",
     "condition": "a document set to remove personal information when it is saved",
     "file": "personal-information-removed.docx", "format": DOCX, "set": (("RemovePersonalInformation", True),),
     "view": "document", "confirm": {"ReadOnly": False, "RemovePersonalInformation": True}},
    {"name": "protected-view", "title": "Protected View", "condition": "a document from the internet, in Protected View",
     "file": "protected-view.docx", "format": DOCX, "set": (), "zone": INTERNET_ZONE, "view": "protected",
     "confirm": {}},
)
NAMES = tuple(s["name"] for s in STATES)
VIEWS = ("document", "protected")


class Invalid(Exception):
    """A state, a fixture or a file of state records that the rules refuse."""


def scratch_root() -> Path:
    """The folder for files that must never land in the repository: the one OFFICE_SCRATCH names, else a folder of
    our own in the system temporary directory (the rule of scripts/capture-ui.py)."""
    return Path(os.environ.get("OFFICE_SCRATCH") or Path(tempfile.gettempdir()) / "rizonesoft-office")


def folder(root=None) -> Path:
    return Path(root if root is not None else scratch_root()).joinpath(*FOLDER)


def by_name(name):
    for state in STATES:
        if state["name"] == name:
            return state
    raise Invalid(f"{name!r} is not a document state scripts/lib/word_states.py lists ({', '.join(NAMES)})")


def fixture(state, root=None) -> Path:
    """Where the state's fixture stands. The file name is the list's own, never a caller's."""
    return folder(root) / state["file"]


def inside(path, root=None) -> Path:
    """`path` resolved, when it is a fixture of the list standing in the fixtures folder itself; Invalid otherwise.
    A path that leaves the folder through `..` or a link resolves elsewhere and is refused, and so is a file the
    list does not name."""
    home = folder(root).resolve()
    real = Path(path).resolve()
    if real.parent != home or real.name not in {s["file"] for s in STATES}:
        raise Invalid(f"{path} is not a fixture of scripts/lib/word_states.py in {home}")
    return real


def unconfirmed(state, read) -> list:
    """What Word says of an opened fixture that is not what its state needs: one line for each property of
    `confirm`. `read(name)` gives the property's value, or raises when Word cannot say. A property that cannot be
    read, or that is neither true nor false nor a number, is unconfirmed: it is never taken as its expected value."""
    wrong = []
    for name, expected in state["confirm"].items():
        try:
            got = read(name)
        except Exception as exc:
            wrong.append(f"{name} could not be read ({type(exc).__name__})")
            continue
        if isinstance(expected, bool):
            if got not in (True, False, 0, 1, -1):
                wrong.append(f"{name} is {got!r}, which is neither true nor false")
            elif bool(got) != expected:
                wrong.append(f"{name} is {bool(got)}, not {expected}")
        elif isinstance(got, bool) or not isinstance(got, int) or got != expected:
            wrong.append(f"{name} is {got!r}, not {expected}")
    return wrong
