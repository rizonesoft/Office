# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The rules of Word's status bar inventory, `design/inventory/word/statusbar.json` (D02 T01 §33).

Pure functions, shared by the capture (`scripts/capture-ui.py --statusbar`), the checker
(`scripts/check-inventory.py`) and the tests.

    word.statusbar                     region       the bar
    word.statusbar.left / .right       region       its two zones; the widest gap between two items divides them
    word.statusbar.<zone>.<item>       statusItem   an item standing on the bar, in order, with `controlType`
    word.statusbar.customize           contextMenu  the Customize Status Bar menu; `itemCount` is its items
    word.statusbar.customize.<item>    menuItem     an item of the menu, in order, with `checked`

Word gives an item one name made of its label and its value (`Page Number Page 1 of 1`), on the bar and in the menu
alike, and no other identity: an item has no automation id. The capture reads those names only while its own blank
document is the one open, so the value is a blank document's, and the value is cut here, by `label_of`, before a
record is built: no record, note or message holds one.

`checked` is whether the item was ticked on this PC when it was captured. It is Word's default only where the owner
never changed it, and the capture cannot tell the two apart (D02 T01 §39 records the defaults).

A count the capture reports about itself proves nothing, so `MENU` and `BAR` are written by hand from the live bar
of the reference build, and the capture and the checker both hold a file against them.
"""
import re

from word_backstage import ADDRESS, slug

ROOT = "word.statusbar"
MENU_ID = f"{ROOT}.customize"
ZONES = ("left", "right")
# The Customize Status Bar menu, in the order and the groups it shows them (a line divides two groups).
MENU = (
    ("Formatted Page Number", "Section", "Page Number", "Vertical Page Position", "Line Number", "Column"),
    ("Word Count", "Character Count (with spaces)"),
    ("Coauthoring Mode",),
    ("Spelling and Grammar Check", "Language"),
    ("Label", "Signatures", "Information Management Policy", "Permissions", "Track Changes", "Text Predictions"),
    ("Caps Lock", "Overtype", "Selection Mode", "Macro Recording", "Accessibility Checker"),
    ("Upload Status", "Document Updates Available"),
    ("Focus", "View Shortcuts", "Zoom Slider", "Zoom"),
)
LABELS = tuple(label for group in MENU for label in group)
# What stands on the bar for a blank document on the reference build, in order: label, zone, control type. An item
# that shows only now and then (the spelling check's result) or only for a document in some state is not listed;
# one the list does not name is recorded and allowed.
BAR = (
    ("Page Number", "left", "button"), ("Word Count", "left", "label"), ("Coauthoring Mode", "left", "button"),
    ("Language", "left", "button"), ("Text Predictions", "left", "button"), ("Macro Recording", "left", "button"),
    ("Accessibility Checker", "left", "button"),
    ("Display Settings", "right", "button"), ("Focus", "right", "button"), ("Read Mode", "right", "button"),
    ("Print Layout", "right", "button"), ("Web Layout", "right", "button"), ("Zoom Out", "right", "button"),
    ("Zoom", "right", "slider"), ("Zoom In", "right", "button"), ("Zoom", "right", "button"),
)
PATIENCE = 6  # how many times the usual wait the bar is given to show every item of BAR
IDLE_SECONDS = 6.0  # how long the window is left alone before the bar is read, so Word's idle work can run
# Every label an item can begin with: the menu's, and those of the bar's items the menu does not list one by one
# (the zoom buttons, the view buttons). The longest that fits is the item's, so `Zoom Out` is not read as `Zoom`.
KNOWN = tuple(dict.fromkeys(LABELS + tuple(label for label, _zone, _type in BAR)))
TYPES = {"Button": "button", "Text": "label", "Slider": "slider", "SplitButton": "splitButton",
         "MenuItem": "menu", "CheckBox": "checkBox"}
HINT = re.compile(r"\s*\((?:Ctrl|Alt|Shift)[^)]*\)\s*$")  # the keys a zoom button names after its label


class Invalid(Exception):
    """A status bar tree or the status bar inventory breaks one of the rules above."""


def label_of(name, labels=KNOWN):
    """An item's label from the one name Word gives it: the longest known label the name begins with, and
    otherwise the name without the keys it names. Whatever follows the label is the item's value and is dropped.
    Returns (label, known): `known` says the label is one of `labels`."""
    text = " ".join(str(name or "").split())
    for label in sorted(labels, key=len, reverse=True):
        if text == label or text.startswith(label + " "):
            return label, True
    return HINT.sub("", text).strip(), False


def zones_of(rects):
    """For items given by their left and right edges, in order, the zone of each: the widest gap between two
    neighbours divides left from right; with one item or none, everything is left."""
    if len(rects) < 2:
        return ["left"] * len(rects)
    gaps = [(rects[i + 1][0] - rects[i][1], i) for i in range(len(rects) - 1)]
    _width, at = max(gaps)
    return ["left"] * (at + 1) + ["right"] * (len(rects) - at - 1)


def records(bar, items, menu_items, base):
    """The records of the bar and its menu. `bar` is the bar's plain node; `items` are the bar's items in order,
    each a plain node with `role`, `name` and `rect`; `menu_items` are the menu's in order, each with `name`,
    `checked` and `group` (which run of the menu it stands in). `base(rid, kind, label, order, node, parent,
    **extra)` builds a record. Raises Invalid for a menu that is not `MENU` or an item with no rule."""
    listed = [(label_of(item.get("name"), LABELS)[0], item.get("group")) for item in menu_items]
    expected = [(label, at) for at, group in enumerate(MENU) for label in group]
    runs = {group: n for n, group in enumerate(dict.fromkeys(g for _l, g in listed))}
    if [(label, runs[group]) for label, group in listed] != expected:
        unknown = [label for label, _g in listed if label not in LABELS]
        raise Invalid("the Customize Status Bar menu is not the one scripts/lib/word_statusbar.py lists" +
                      (f" (it also shows: {', '.join(unknown)})" if unknown else
                       " (its items, their order or their groups differ)"))
    out, used = [base(ROOT, "region", "Status Bar", 0, bar, None)], {ROOT}

    def unique(parent, label):
        rid, n = f"{parent}.{slug(label)}", 1
        while rid in used:
            n += 1
            rid = f"{parent}.{slug(label)}-{n}"
        used.add(rid)
        return rid
    zones = zones_of([(item["rect"][0], item["rect"][2]) for item in items])
    for at, zone in enumerate(ZONES):
        out.append(base(unique(ROOT, zone), "region", f"{zone.title()} zone", at, None, ROOT))
    order = dict.fromkeys(ZONES, 0)
    for item, zone in zip(items, zones):
        ctype = TYPES.get(item.get("role"))
        if ctype is None:
            raise Invalid(f"an item of the status bar is a {item.get('role')}, which the capture has no rule for; "
                          f"teach scripts/lib/word_statusbar.py what it is")
        label, _known = label_of(item.get("name"))
        if not label:
            raise Invalid("an item of the status bar has no name")
        parent = f"{ROOT}.{zone}"
        out.append(base(unique(parent, label), "statusItem", label, order[zone], item, parent, controlType=ctype))
        order[zone] += 1
    out.append(base(MENU_ID, "contextMenu", "Customize Status Bar", len(ZONES), None, ROOT,
                    itemCount=len(menu_items)))
    used.add(MENU_ID)
    for at, item in enumerate(menu_items):
        label = label_of(item.get("name"), LABELS)[0]
        out.append(base(unique(MENU_ID, label), "menuItem", label, at, None, MENU_ID,
                        checked=bool(item.get("checked"))))
    return out


def missing(found: list) -> list:
    """The items `BAR` says the bar shows for a blank document that are not in `found`, a list of (label, zone,
    controlType) in order: each must be there, and those that are must stand in `BAR`'s order."""
    lacking = [f"{label} ({zone}, {ctype})" for label, zone, ctype in BAR if (label, zone, ctype) not in found]
    if lacking:
        return lacking
    places, at = [], 0
    for wanted in BAR:
        try:
            at = found.index(wanted, at) + 1
        except ValueError:
            places.append(f"{wanted[0]} ({wanted[1]}) out of its place")
    return places


def ticks(menu_records: list) -> dict:
    return {r.get("label"): r.get("checked") for r in menu_records}


def validate(recs: list) -> None:
    """Refuse a status bar inventory that is not whole: the bar and its two zones; every item of `BAR` in its zone,
    with its type, in order; the menu with every item of `MENU` in order, each with `checked`, and the `itemCount`
    that says so; nothing of the owner's. Raises Invalid naming every problem."""
    problems, by_id = [], {}
    for rec in recs:
        if not isinstance(rec, dict) or not isinstance(rec.get("id"), str) or not rec["id"]:
            raise Invalid("a status bar record has no id")
        if rec["id"] in by_id:
            problems.append(f"duplicate record id {rec['id']}")
        by_id[rec["id"]] = rec
    for rec in recs:
        rid = rec["id"]
        if rec.get("app") != "word":
            problems.append(f"{rid}: app must be 'word'")
        if rid != ROOT and not rid.startswith(ROOT + "."):
            problems.append(f"{rid}: a status bar record's id starts with {ROOT}")
        if rid != ROOT and rec.get("parent") not in by_id:
            problems.append(f"{rid}: its parent {rec.get('parent')} is not in the file")
        if ADDRESS.search(str(rec.get("label", ""))):
            problems.append(f"{rid}: an e-mail address is the owner's data, never a label")
        if "checked" in rec and (rec.get("kind") != "menuItem" or not isinstance(rec["checked"], bool)):
            problems.append(f"{rid}: `checked` is true or false, on an item of the menu")
    for rid, kind in ((ROOT, "region"), (f"{ROOT}.left", "region"), (f"{ROOT}.right", "region"),
                      (MENU_ID, "contextMenu")):
        if by_id.get(rid, {}).get("kind") != kind:
            problems.append(f"the {kind} {rid} is not recorded")
    on_bar = sorted((r for r in recs if r.get("kind") == "statusItem"),
                    key=lambda r: (ZONES.index(r["parent"].rsplit(".", 1)[-1])
                                   if str(r.get("parent", "")).rsplit(".", 1)[-1] in ZONES else 9,
                                   r.get("order", 0)))
    for rec in on_bar:
        if rec.get("parent") not in (f"{ROOT}.left", f"{ROOT}.right"):
            problems.append(f"{rec['id']}: an item of the bar stands in one of its two zones")
        if not rec.get("controlType"):
            problems.append(f"{rec['id']}: an item of the bar has a controlType")
    found = [(r.get("label"), str(r.get("parent", "")).rsplit(".", 1)[-1], r.get("controlType")) for r in on_bar]
    for lack in missing(found):
        problems.append(f"the status bar must show {lack}")
    menu = sorted((r for r in recs if r.get("kind") == "menuItem"), key=lambda r: r.get("order", 0))
    for rec in menu:
        if rec.get("parent") != MENU_ID:
            problems.append(f"{rec['id']}: an item of the menu sits under {MENU_ID}")
        if not isinstance(rec.get("checked"), bool):
            problems.append(f"{rec['id']}: no `checked`, so whether the bar shows it is not recorded")
    labels = [r.get("label") for r in menu]
    if labels != list(LABELS):
        gone = [label for label in LABELS if label not in labels]
        more = [label for label in labels if label not in LABELS]
        problems.append("the Customize Status Bar menu is not the one scripts/lib/word_statusbar.py lists" +
                        (f": it lacks {', '.join(gone)}" if gone else "") +
                        (f": it also holds {', '.join(str(m) for m in more)}" if more else "") +
                        ("" if gone or more else ": its items are out of order"))
    count = by_id.get(MENU_ID, {}).get("itemCount")
    if count != len(menu):
        problems.append(f"{MENU_ID}: holds {len(menu)} of the {count} items the capture recorded")
    if problems:
        raise Invalid("; ".join(problems))
