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

import json
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
# it is opened (`view`: among Documents, or in a Protected View window, which is not among them), whether Word
# itself shows the ribbon collapsed over it (`ribbon`), and what Word must say of it when it is opened again
# (`confirm`). Only the properties `confirm` names are asked: Word refuses to
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
     "file": "final.docx", "format": DOCX, "set": (("Final", True),), "view": "document", "ribbon": "collapsed",
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
     "ribbon": "collapsed",
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


# ------------------------------------------------------------------------------------------ the records of a state
BLANK_ROOT = "word.backstage"  # the ids of the blank-document capture (design/inventory/word/backstage.json)
ROOT = "word.backstage.states"  # the ids of every state's records (design/inventory/word/backstage-states.json)
# Where a record came from: not a fact about Backstage. A tuple, in the order a capture writes them: records are
# built by walking it, and a set walks in an order that changes from one process to the next.
PROVENANCE = ("source", "capturedFrom")
HAND = ("behaviour", "disposition", "dispositionReason")  # written by hand: carried by a recapture, never compared
UNPRODUCIBLE: dict = {}  # a state of STATES this PC cannot be captured in, with the reason the reference gives


FILE = "backstage-states.json"  # beside the blank-document capture, in design/inventory/word/


def captured_ids(folder) -> frozenset:
    """The idMso values the committed state captures add to Backstage, read from `FILE` in the Word inventory
    folder: those of the records that stand for no record of the blank-document capture (no `variantOf`). A record
    that does stand for one says nothing new: were it counted, a group lost from the blank capture would pass as
    captured. Empty when there is no such file yet. A file that is there and cannot be read raises (OSError,
    ValueError): what was captured is then unknown, and unknown is not nothing."""
    path = Path(folder) / FILE
    if not path.exists():
        return frozenset()
    data = json.loads(path.read_bytes().decode("utf-8"))
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise ValueError(f"{path} does not hold a list of records")
    return frozenset(r["idMso"] for r in data
                     if isinstance(r.get("idMso"), str) and r["idMso"] and "variantOf" not in r)


def root_id(state) -> str:
    return f"{ROOT}.{state['name']}"


def state_id(state, rid: str) -> str:
    """The id a record of the blank-document capture's naming has in a state: its state's prefix in place of
    `word.backstage`."""
    if not rid.startswith(BLANK_ROOT + ".") or rid.startswith(ROOT + "."):
        raise Invalid(f"{rid} is not an id of a Backstage capture")
    return f"{root_id(state)}.{rid[len(BLANK_ROOT) + 1:]}"


def facts(record, drop=()) -> dict:
    """What a record says about Backstage: everything but where it came from and what was written by hand."""
    return {k: v for k, v in record.items() if k not in PROVENANCE and k not in HAND and k not in drop}


def state_records(state, captured: list, blank: list) -> list:
    """The records of one state, from a whole Backstage capture made over its fixture (`captured`, ids as the
    blank-document capture names them) and the committed blank-document capture (`blank`).

    A root record names the state. Under it stands every navigation entry as the state shows it. A page whose
    records are the blank capture's, fact for fact, carries `unchanged` and no children; a page that differs in
    anything carries every record of it. A record whose counterpart the blank capture holds (the same idMso where
    that names one record of the blank capture, else the same id) carries `variantOf`. Raises Invalid when the
    capture is not one this can hold: an id outside Backstage, a parent that is not in it, or two records of the
    state that would name the same blank record."""
    by_id = {r["id"]: r for r in blank if isinstance(r, dict) and isinstance(r.get("id"), str)}
    by_mso, seen = {}, {}
    for rec in by_id.values():
        if rec.get("idMso"):
            seen[rec["idMso"]] = seen.get(rec["idMso"], 0) + 1
            by_mso[rec["idMso"]] = rec
    by_mso = {mso: rec for mso, rec in by_mso.items() if seen[mso] == 1}
    ids = {r.get("id") for r in captured}
    for rec in captured:
        if not isinstance(rec.get("id"), str) or not rec["id"].startswith(BLANK_ROOT + "."):
            raise Invalid(f"the {state['name']} capture holds {rec.get('id')!r}, which is not a Backstage record")
        if "parent" in rec and rec["parent"] not in ids:
            raise Invalid(f"{rec['id']} of the {state['name']} capture stands under {rec['parent']}, which the "
                          f"capture does not hold")
    top = [r for r in captured if "parent" not in r]

    def under(records, rid):
        return [r for r in records if r["id"].startswith(rid + ".")]
    provenance = {k: captured[0][k] for k in PROVENANCE if captured and k in captured[0]}
    root = {"id": root_id(state), "app": "word", "kind": "region", "label": state["title"],
            "order": NAMES.index(state["name"]), "condition": state["condition"], "captureState": state["name"],
            **provenance}
    out, claimed, twins = [root], {}, {}

    def variant(rec):
        # The counterpart: the one blank record of the same idMso; else the record of the same last step under
        # the counterpart of this record's parent (a group the state renames keeps its controls' counterparts);
        # else the record of the same id.
        twin = by_mso.get(rec.get("idMso")) if rec.get("idMso") else None
        if twin is None and rec.get("parent") in twins:
            twin = by_id.get(f"{twins[rec['parent']]}.{rec['id'].rsplit('.', 1)[1]}")
        twin = twin or by_id.get(rec["id"])
        if twin is None:
            return {}
        twins[rec["id"]] = twin["id"]
        if twin["id"] in claimed:
            raise Invalid(f"{rec['id']} and {claimed[twin['id']]} of the {state['name']} capture both stand for "
                          f"{twin['id']} of the blank-document capture")
        claimed[twin["id"]] = rec["id"]
        return {"variantOf": twin["id"]}

    def made(rec, **extra):
        new = dict(rec, id=state_id(state, rec["id"]), captureState=state["name"], **extra)
        new["parent"] = state_id(state, rec["parent"]) if "parent" in rec else root["id"]
        return new
    for entry in top:
        mine, theirs = under(captured, entry["id"]), under(blank, entry["id"])
        twin = by_id.get(entry["id"])
        same = (entry.get("kind") == "backstagePage" and twin is not None and facts(entry) == facts(twin)
                and [facts(r) for r in mine] == [facts(r) for r in theirs])
        if same:
            page = {k: entry[k] for k in ("id", "app", "kind", "label", "order") if k in entry}
            out.append(made(dict(page, **{k: entry[k] for k in PROVENANCE if k in entry}), unchanged=True,
                            **variant(entry)))
            continue
        out.append(made(entry, **variant(entry)))
        out += [made(rec, **variant(rec)) for rec in mine]
    root["itemCount"] = len(out) - 1
    return out


def merge_state(existing: list, fresh: list, state) -> list:
    """The file's records with one state's replaced by a fresh capture of it: every other state's records stay as
    they are, byte for byte, the fresh ones take over what was written by hand on the record of the same id, and
    the states stand in the order of `STATES`."""
    old = {r["id"]: r for r in existing if isinstance(r, dict) and r.get("captureState") == state["name"]
           and isinstance(r.get("id"), str)}
    mine = [dict(r, **{k: old[r["id"]][k] for k in HAND if r["id"] in old and k in old[r["id"]]}) for r in fresh]
    groups = {state["name"]: mine}
    for rec in existing:
        name = rec.get("captureState") if isinstance(rec, dict) else None
        if name != state["name"]:
            groups.setdefault(name, []).append(rec)
    order = [n for n in NAMES if n in groups] + [n for n in groups if n not in NAMES]
    return [rec for name in order for rec in groups[name]]


def validate_states(records: list, blank_ids, whole=False) -> None:
    """Refuse a file of state records that is not lawful: every record inside its state's prefix and naming its
    state, each state with its one root as the list names it, every parent the state's own, every `variantOf` a
    record of the blank-document capture and given once in a state, `unchanged` on a page with no children and a
    counterpart only. With `whole`, every state of `STATES` is there, but those of `UNPRODUCIBLE`, which are not.
    Raises Invalid naming every problem."""
    problems, by_id = [], {}
    for rec in records:
        if not isinstance(rec, dict) or not isinstance(rec.get("id"), str) or not rec["id"]:
            raise Invalid("a state record has no id")
        if rec["id"] in by_id:
            problems.append(f"duplicate record id {rec['id']}")
        by_id[rec["id"]] = rec
    roots, variants, kids = {}, {}, {}
    for rec in records:
        rid, name = rec["id"], rec.get("captureState")
        if name not in NAMES:
            problems.append(f"{rid}: its captureState {name!r} is not a state scripts/lib/word_states.py lists")
            continue
        state = by_name(name)
        if rec.get("app") != "word":
            problems.append(f"{rid}: app must be 'word'")
        if rid == root_id(state):
            roots[name] = rec
            if rec.get("kind") != "region" or "parent" in rec:
                problems.append(f"{rid}: the root of a state is a region with no parent")
            if rec.get("label") != state["title"]:
                problems.append(f"{rid}: is called {rec.get('label')!r}, not {state['title']}")
            if rec.get("condition") != state["condition"]:
                problems.append(f"{rid}: its condition is {rec.get('condition')!r}, not the document the list "
                                f"gives the state ({state['condition']})")
            continue
        if not rid.startswith(root_id(state) + "."):
            problems.append(f"{rid}: a record of the {name} state has an id under {root_id(state)}")
            continue
        parent = rec.get("parent")
        if parent != root_id(state) and not (isinstance(parent, str) and parent.startswith(root_id(state) + ".")
                                             and parent in by_id):
            problems.append(f"{rid}: its parent {parent!r} is not a record of the {name} state in the file")
        else:
            kids.setdefault(parent, []).append(rid)
        if "condition" in rec:
            problems.append(f"{rid}: `condition` belongs to the root of a state")
        if "variantOf" in rec:
            if rec["variantOf"] not in blank_ids:
                problems.append(f"{rid}: its variantOf {rec['variantOf']!r} is not a record of the blank-document "
                                f"capture")
            elif (name, rec["variantOf"]) in variants:
                problems.append(f"{rid}: {rec['variantOf']} is already the counterpart of "
                                f"{variants[(name, rec['variantOf'])]} in the {name} state")
            else:
                variants[(name, rec["variantOf"])] = rid
        if "unchanged" in rec:
            if rec["unchanged"] is not True or rec.get("kind") != "backstagePage" or parent != root_id(state):
                problems.append(f"{rid}: `unchanged` is true, on a page of a state only")
            elif "variantOf" not in rec:
                problems.append(f"{rid}: a page that is unchanged names the blank-document page it equals")
    for rid, rec in by_id.items():
        if rec.get("unchanged") is True and kids.get(rid):
            problems.append(f"{rid}: a page that is unchanged carries no records of its own, and {len(kids[rid])} "
                            f"stand under it")
    for name in sorted({r.get("captureState") for r in records if r.get("captureState") in NAMES}):
        state = by_name(name)
        if name not in roots:
            problems.append(f"the {name} state has records and no root ({root_id(state)})")
            continue
        count = sum(1 for r in records if r.get("captureState") == name) - 1
        if roots[name].get("itemCount") != count:
            problems.append(f"{root_id(state)}: holds {count} of the {roots[name].get('itemCount')} records the "
                            f"capture recorded")
        if name in UNPRODUCIBLE:
            problems.append(f"the {name} state is recorded, and scripts/lib/word_states.py says this PC cannot "
                            f"produce it")
    if whole:
        for name in NAMES:
            if name not in roots and name not in UNPRODUCIBLE:
                problems.append(f"the {name} state ({by_name(name)['title']}) is not recorded")
    if problems:
        raise Invalid("; ".join(problems))
