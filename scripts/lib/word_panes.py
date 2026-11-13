# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The rules of Word's task pane inventory, `design/inventory/word/panes.json` (D02 T01 §32).

Pure functions over plain trees, shared by the capture (`scripts/capture-ui.py --panes`), the checker
(`scripts/check-inventory.py`) and the tests. A record is a fact about a pane: where it docks, how large it opens,
the command that opens it and the controls at its top level. A pane shows the owner's data (the clipboard's
entries, the document's headings, its tracked changes, its shapes): a list, tree, grid or document view is one
control whose entries are never walked into, and no text in a pane is read at all.

    word.panes.<pane>            pane      `dock`, `bounds`, `openedBy` (the ribbon record whose command opens it),
                                           `itemCount` (every heading and control recorded under it)
    word.panes.<pane>.<...>      group     a heading inside the pane; its controls are its children
    word.panes.<pane>.<...>      control   a control, with `controlType`
    word.panes.<...>.<choice>    menuItem  a fixed choice of one of the pane's menus

What a capture reports about itself proves nothing, so `PANES` is written by hand from the live panes of the
reference build: for each pane its command, its opener, where it may dock and the controls it must show. The capture
and the checker both hold a file against it; a control the list does not name is recorded and allowed.
"""
import re

from word_backstage import ADDRESS, CONTROL_TYPES, is_third_party, slug

ROOT = "word.panes"
DOCKS = ("left", "right", "top", "bottom", "floating")
SIDES = ("left", "right")
# Each pane: its id's last part, the title Word shows on it, the idMso of the command that opens it, the record of
# design/inventory/word/ribbon.json that command belongs to, where it may dock, whether a shape must be selected
# first, and the (label, controlType) pairs it must show. Styles opens floating or docked at the right, as it was
# last left; the others dock where Word puts them.
PANES = (
    {"slug": "navigation", "title": "Navigation", "command": "NavigationPaneShowHide",
     "openedBy": "word.view.show.navigation-pane", "docks": SIDES,
     "required": (("Search document", "editBox"), ("Search", "splitButton"), ("Headings", "tab"), ("Pages", "tab"),
                  ("Results", "tab"))},
    {"slug": "styles", "title": "Styles", "command": "StylesPane",
     "openedBy": "word.home.styles.styles-stylespane", "docks": ("floating", "right", "left"),
     "required": (("Styles", "listBox"), ("Show Preview", "checkBox"), ("Disable Linked Styles", "checkBox"),
                  ("New Style", "button"), ("Style Inspector", "button"), ("Manage Styles", "button"),
                  ("Options...", "button"))},
    {"slug": "clipboard", "title": "Clipboard", "command": "ShowClipboard",
     "openedBy": "word.home.clipboard.office-clipboard", "docks": SIDES,
     "required": (("Paste All", "button"), ("Clear All", "button"), ("Clipboard items", "listBox"),
                  ("Options", "menu"))},
    {"slug": "reviewing-vertical", "title": "Revisions", "command": "ReviewReviewingPaneVertical",
     "openedBy": "word.review.markup.reviewing-pane.reviewing-pane-vertical", "docks": SIDES,
     "required": (("Show Detailed Summary", "button"), ("Refresh Reviewing Pane", "button"),
                  ("Revisions", "listBox"))},
    {"slug": "reviewing-horizontal", "title": "Revisions", "command": "ReviewReviewingPaneHorizontal",
     "openedBy": "word.review.markup.reviewing-pane.reviewing-pane-horizontal", "docks": ("bottom", "top"),
     "required": (("Show Detailed Summary", "button"), ("Refresh Reviewing Pane", "button"),
                  ("Revisions", "listBox"))},
    {"slug": "editor", "title": "Editor", "command": "WritingAssistanceCheckDocument",
     "openedBy": "word.home.editor.editor", "docks": SIDES,
     # Editor asks its service and redraws: it can show its statistics alone before its checks are there.
     # `settle` is how many seconds apart two reads must agree, and the pane is read until it also shows every
     # control below, so that what is recorded is the pane at rest, whole, and the same on every run. They are its
     # checks for the capture's blank document; a document with text can show more, which this capture never
     # sends to the service.
     "settle": 5.0,
     "required": (("Spelling", "button"), ("Grammar", "button"), ("Conciseness", "button"),
                  ("Document statistics", "button"), ("Tell us what you think about Editor", "button"))},
    {"slug": "selection", "title": "Selection", "command": "SelectionPane",
     "openedBy": "word.layout.arrange.selection-pane", "docks": SIDES,
     "required": (("Show All", "button"), ("Hide All", "button"), ("Bring Forward", "button"),
                  ("Send Backward", "button"), ("Objects", "listBox"))},
    {"slug": "format-shape", "title": "Format Shape", "command": "ObjectFormatDialog",
     "openedBy": "word.shape-format.shape-styles.format-object", "docks": SIDES, "shape": True,
     "required": (("Fill", "button"), ("Line", "button"))},
)
COMMANDS = frozenset(p["command"] for p in PANES)
CHROME = (("Task Pane Options", "menu"), ("Close pane", "button"))  # every pane's own title bar
# Menus recorded without their choices: the title bar's menu shows its items (move, size, close) in a window of
# its own that gives none of them to UI Automation. Every other menu of a pane is opened and must show choices.
CLOSED_MENUS = frozenset({"Task Pane Options"})
# Controls Word gives no name: their labels, by pane and role, in the order the pane shows them. Written by hand
# (what each does on the reference build); a nameless control with no entry here refuses the capture.
UNNAMED = {
    "styles": {"List": ("Styles",), "Button": ("New Style", "Style Inspector", "Manage Styles")},
    "clipboard": {"List": ("Clipboard items",)},
    "selection": {"Tree": ("Objects",)},
}
TYPES = dict(CONTROL_TYPES, TabItem="tab", ListItem="galleryItem", Document="listBox")
SKIPPED = frozenset({"ScrollBar", "Thumb", "Image", "TitleBar", "Separator"})
SKIPPED_CLASSES = frozenset({"NUIScrollbar"})
CONTAINERS = frozenset({"Group", "Pane", "Custom", "Tab", "Menu"})  # walked into; only a named group is a record
DATA = "listBox"
COUNTED = ("group", "control")
# A button of the Editor pane names what it counted in the document after its label: the label is the fact.
STATE = re.compile(r",\s*\d+\s+\w+.*$")


class Invalid(Exception):
    """A pane's tree or the panes inventory breaks one of the rules above."""


def clean(text) -> str:
    return STATE.sub("", str(text or "").strip()).rstrip(":").strip()


def pane_id(spec) -> str:
    return f"{ROOT}.{spec['slug']}"


def by_slug(name):
    return next((p for p in PANES if p["slug"] == name), None)


def dock_of(name) -> str:
    """The side a pane docks at, from the name of the dock that holds it (`MsoDockLeft`); floating with none."""
    side = str(name or "")[len("MsoDock"):].lower() if str(name or "").startswith("MsoDock") else ""
    return side if side in DOCKS else "floating"


def record_pane(spec, pane, chrome: list, content: list, base, choices, notes: list) -> list:
    """The records of one pane: `pane` is its own record (already built, with `dock`, `openedBy` and its bounds),
    `chrome` the plain nodes of its title bar and `content` those of its body. `base(rid, kind, label, order, node,
    parent, **extra)` builds a record; `choices(node)` opens a menu and returns its choice nodes, leaving it
    closed. Sets the pane's `itemCount`. Raises Invalid for a control it cannot name or has no rule for, or a menu
    that shows no choices."""
    records, used = [pane], {pane["id"]}
    unnamed = {role: list(labels) for role, labels in UNNAMED.get(spec["slug"], {}).items()}
    counts = {"text": 0, "data": 0, "closed": 0}

    def unique(parent, label):
        rid, n = f"{parent}.{slug(label)}", 1
        while rid in used:
            n += 1
            rid = f"{parent}.{slug(label)}-{n}"
        used.add(rid)
        return rid

    def walk(nodes, parent, order):
        for node in nodes:
            role, name = node.get("role"), clean(node.get("name"))
            if role in SKIPPED or node.get("class_name") in SKIPPED_CLASSES:
                continue
            if role == "Text":  # a pane's texts are its data and its state (what was copied, how many changes)
                counts["text"] += 1
                continue
            if role in CONTAINERS:
                if role == "Group" and name:
                    rec = base(unique(parent, name), "group", name, order[0], node, parent)
                    order[0] += 1
                    records.append(rec)
                    walk(node.get("children", []), rec["id"], [0])
                else:
                    walk(node.get("children", []), parent, order)
                continue
            ctype = TYPES.get(role)
            if ctype is None:
                raise Invalid(f"{name or role!r} in the {spec['title']} pane is a {role}, which the pane capture has "
                              f"no rule for; teach scripts/lib/word_panes.py what it is")
            if not name:
                if not unnamed.get(role):
                    raise Invalid(f"a {role} in the {spec['title']} pane has no name, and scripts/lib/word_panes.py "
                                  f"holds no label for it")
                name = unnamed[role].pop(0)
            rec = base(unique(parent, name), "control", name, order[0], node, parent, controlType=ctype)
            order[0] += 1
            records.append(rec)
            if ctype == DATA:
                counts["data"] += 1
            elif ctype == "menu" and name in CLOSED_MENUS:
                counts["closed"] += 1
            elif ctype == "menu":
                items = choices(node)
                if not items:
                    raise Invalid(f"the menu {name!r} of the {spec['title']} pane opened to no choices")
                seen = 0
                for item in items:
                    label = clean(item.get("name"))
                    if not label or slug(label) == "unnamed":
                        continue
                    records.append(base(unique(rec["id"], label), "menuItem", label, seen, item, rec["id"]))
                    seen += 1
                if not seen:
                    raise Invalid(f"the menu {name!r} of the {spec['title']} pane opened to choices with no names")
                rec["itemCount"] = seen

    order = [0]
    walk(chrome, pane["id"], order)
    walk(content, pane["id"], order)
    left = {role: labels for role, labels in unnamed.items() if labels}
    if left:
        raise Invalid(f"the {spec['title']} pane did not show the nameless controls scripts/lib/word_panes.py "
                      f"names: {left}")
    pane["itemCount"] = sum(1 for r in records if r["kind"] in COUNTED)
    for key, said in (("text", "text(s) not read (a pane's texts are its data and its state)"),
                      ("data", "list(s) recorded without entries"),
                      ("closed", "title bar menu recorded without its choices")):
        if counts[key]:
            notes.append(f"{spec['title']} pane ({spec['slug']}): {counts[key]} {said}")
    return records


def missing(spec, records: list) -> list:
    """The controls `PANES` says the pane must show that are not among `records` (label and type), chrome included."""
    under = {(r.get("label"), r.get("controlType")) for r in records
             if r.get("kind") == "control" and str(r.get("id", "")).startswith(pane_id(spec) + ".")}
    return [f"{label} ({ctype})" for label, ctype in CHROME + tuple(spec["required"]) if (label, ctype) not in under]


def validate(records: list, ribbon_ids=None) -> None:
    """Refuse a panes inventory that is not whole: every pane of `PANES` there, docked where it may dock, with
    `bounds`, the opener the list names (a record of the ribbon inventory when `ribbon_ids` is given), every control
    the list requires, and the number of headings and controls its `itemCount` says. Raises Invalid naming every
    problem."""
    problems, by_id, children = [], {}, {}
    for rec in records:
        if not isinstance(rec, dict) or not isinstance(rec.get("id"), str) or not rec["id"]:
            raise Invalid("a pane record has no id")
        if rec["id"] in by_id:
            problems.append(f"duplicate record id {rec['id']}")
        by_id[rec["id"]] = rec
    for rec in records:
        rid, parent = rec["id"], rec.get("parent")
        if rec.get("app") != "word":
            problems.append(f"{rid}: app must be 'word'")
        if not rid.startswith(ROOT + "."):
            problems.append(f"{rid}: a pane record's id starts with {ROOT}.")
        if rec.get("kind") == "pane":
            if "parent" in rec:
                problems.append(f"{rid}: a pane has no parent")
        elif parent not in by_id:
            problems.append(f"{rid}: its parent {parent} is not in the file")
        else:
            children.setdefault(parent, []).append(rec)
            if rec.get("kind") not in COUNTED + ("menuItem",):
                problems.append(f"{rid}: a {rec.get('kind')} is not a heading, a control or a choice")
        if ADDRESS.search(str(rec.get("label", ""))) or is_third_party(str(rec.get("label", ""))):
            problems.append(f"{rid}: {rec.get('label')!r} is the owner's or a third party's, never a label")
        if ("dock" in rec or "openedBy" in rec) and rec.get("kind") != "pane":
            problems.append(f"{rid}: `dock` and `openedBy` belong to a pane")

    def below(rid):
        for kid in children.get(rid, []):
            yield kid
            yield from below(kid["id"])

    known = {pane_id(spec) for spec in PANES}
    for rec in records:
        if rec.get("kind") == "pane" and rec["id"] not in known:
            problems.append(f"{rec['id']}: not one of the panes scripts/lib/word_panes.py lists")
    for spec in PANES:
        rid = pane_id(spec)
        pane = by_id.get(rid)
        if pane is None or pane.get("kind") != "pane":
            problems.append(f"the {spec['title']} pane ({rid}) is not recorded")
            continue
        if pane.get("dock") not in spec["docks"]:
            problems.append(f"{rid}: docks {pane.get('dock')!r}, and the {spec['title']} pane opened by "
                            f"{spec['command']} docks {' or '.join(spec['docks'])}")
        if not isinstance(pane.get("bounds"), dict):
            problems.append(f"{rid}: no bounds, so its width and height are not recorded")
        if pane.get("openedBy") != spec["openedBy"]:
            problems.append(f"{rid}: openedBy is {pane.get('openedBy')!r}, not {spec['openedBy']}")
        elif ribbon_ids is not None and spec["openedBy"] not in ribbon_ids:
            problems.append(f"{rid}: its opener {spec['openedBy']} is not a record of the ribbon inventory")
        under = list(below(rid))
        count = sum(1 for r in under if r.get("kind") in COUNTED)
        if not isinstance(pane.get("itemCount"), int) or isinstance(pane.get("itemCount"), bool):
            problems.append(f"{rid}: no itemCount, so a lost control goes unseen")
        elif pane["itemCount"] != count:
            problems.append(f"{rid}: holds {count} of the {pane['itemCount']} headings and controls the capture "
                            f"recorded")
        lacking = missing(spec, under)
        if lacking:
            problems.append(f"{rid}: the {spec['title']} pane must show " + ", ".join(lacking))
        for rec in under:
            items = children.get(rec["id"], [])
            choices = [k for k in items if k.get("kind") == "menuItem"]
            if rec.get("kind") == "control" and not rec.get("controlType"):
                problems.append(f"{rec['id']}: a control has a controlType")
            if choices and rec.get("controlType") != "menu":
                problems.append(f"{rec['id']}: only a menu has choices")
            if rec.get("controlType") == "menu":
                closed = rec.get("label") in CLOSED_MENUS
                if closed and (choices or "itemCount" in rec):
                    problems.append(f"{rec['id']}: {rec.get('label')} is recorded without choices")
                elif not closed and not choices:
                    problems.append(f"{rec['id']}: {rec.get('label')} opens to choices, and none is recorded")
            if "itemCount" in rec or choices:
                if rec.get("itemCount") != len(choices):
                    problems.append(f"{rec['id']}: holds {len(choices)} of the {rec.get('itemCount')} choices the "
                                    f"capture recorded")
            if rec.get("controlType") == DATA and items:
                problems.append(f"{rec['id']}: a list of the owner's data is recorded without entries")
    if problems:
        raise Invalid("; ".join(problems))
