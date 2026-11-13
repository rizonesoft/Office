# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The rules of Word's Options inventory, `design/inventory/word/options.json` (D02 T01 §31).

Pure functions over plain trees, so the capture (`scripts/capture-ui.py --options`), the checker
(`scripts/check-inventory.py`) and the tests share one copy. A record is a fact about the dialog: a category, a
heading, a control with its type, a fixed choice of a list. Nothing a person typed or chose is ever read: no value,
no state, no entry of a list that shows this PC's or the owner's data.

    word.options                      dialog     the dialog; `itemCount` is the number of categories it lists
    word.options.<category>           dialogTab  one per category; `itemCount` is every heading and control under it
    word.options.<category>.<...>     group      a heading; its controls are its children
    word.options.<category>.<...>     setting    a control, with `controlType`; `enabled` false when it was disabled
    word.options.<...>.<choice>       menuItem   a fixed choice of a list, a menu or a set of radio buttons
    word.options.ok / .cancel         control    the dialog's own buttons
"""
from word_backstage import ADDRESS, CONTROL_TYPES, is_third_party, slug

ROOT = "word.options"
# What the capture reads before the dialog opens and after it closes, to prove nothing changed: properties of the
# `Options` object of the tool's own Word instance. None is a path, a name or any other text of the owner's.
SAMPLE = ("CheckSpellingAsYouType", "CheckGrammarAsYouType", "CheckGrammarWithSpelling", "AllowDragAndDrop",
          "AutoWordSelection", "ReplaceSelection", "Overtype", "SmartCutPaste", "BackgroundSave", "CreateBackup",
          "SaveInterval", "MeasurementUnit", "UpdateLinksAtOpen", "ConfirmConversions", "PrintBackground",
          "Pagination")
# Dropdowns whose choices are this PC's or the open documents' data, never recorded: the open documents and
# templates, the printer's trays, the styles of the template, the installed fonts and sound schemes. An entry with
# a slash names one category's list only: the Quick Access Toolbar's `Choose commands from` lists every tab of
# this PC's ribbon, add-ins' tabs included, after the fixed entries that Customize Ribbon's list of the same name
# records.
ENVIRONMENT_LISTS = frozenset({
    "Exceptions for", "Preserve fidelity when sharing this document", "When printing this document",
    "Current document", "Layout options for", "Compatibility options for", "Default tray",
    "Default paragraph style", "Name", "Size", "Sound Scheme", "Customize Quick Access Toolbar",
    "quick-access-toolbar/Choose commands from"})
SKIPPED = frozenset({"ScrollBar", "Thumb", "Image", "TitleBar", "Separator"})  # furniture, never a setting
CONTAINERS = frozenset({"Group", "Pane"})
RADIO_GROUP = "NetUIRadioGroup"
DATA_LISTS = "listBox"   # a list box, tree or grid shows data (commands, languages, add-ins): never its entries
OPENED = ("dropdown", "menu")  # what the capture opens to read fixed choices
PROSE_LENGTH = 80
COUNTED = ("group", "setting")  # what a category's itemCount counts


class Invalid(Exception):
    """The Options tree or inventory breaks one of the rules above."""


def clean(text) -> str:
    """A name as a label: without the space and the colon the dialog lays it out with."""
    return str(text or "").strip().rstrip(":").strip()


def is_prose(text: str) -> bool:
    """Whether a text is a sentence of explanation and not a caption. Captions are facts about the layout and are
    recorded; Microsoft's sentences are its own writing and are not (the product explains itself in its own words)."""
    return len(text) > PROSE_LENGTH or text.endswith((".", "!", "?")) or ". " in text


def category_id(label: str) -> str:
    return f"{ROOT}.{slug(clean(label))}"


def environment(rid: str, label: str) -> bool:
    """Whether the list `label`, in the category the id `rid` lies in, shows this PC's or the open documents' data."""
    category = rid[len(ROOT) + 1:].split(".")[0]
    return label in ENVIRONMENT_LISTS or f"{category}/{label}" in ENVIRONMENT_LISTS


def record_category(cat_id: str, nodes: list, base, choices, notes: list, rules=None) -> list:
    """The records under one category from its content tree. `nodes` are plain nodes (`role`, `name`, `class_name`,
    `enabled`, `children`); `base(rid, kind, label, order, node, parent, **extra)` builds a record; `choices(node)`
    opens a list or menu and returns its choice nodes, leaving it closed. Raises Invalid for a control it has no
    rule for or cannot name, so nothing is dropped without a word.

    A text node may carry `read`, a function that fetches its name, in place of `name`. It is called only for a
    text the rules need to read: the text after a caption is what the caption names (an add-in's publisher, its
    folder), this PC's data, and when another text or nothing follows it, it is never read at all.

    `rules` lets another surface built of the same parts (a dialog) use these rules with its own lists: `types`
    (role to control type), `skipped` (roles that are furniture), `ignore` (a test for a node to pass over),
    `containers` (roles that are walked into) and `groups` (those of them that are a heading when named),
    `is_environment` (whether a list shows this PC's data), `unnamed` (labels for controls Word gives no name, by
    role, in order), `extra` (fields every record gets, such as a condition), `used` (the ids already taken) and
    `order` (where numbering goes on from), and `noun`, `label` and `said` (its own wording for a count) for the
    notes. Without it the rules are Word Options' own."""
    rules = rules or {}
    types, skipped = rules.get("types", CONTROL_TYPES), rules.get("skipped", SKIPPED)
    ignore, is_environment = rules.get("ignore", lambda node: False), rules.get("is_environment", environment)
    unnamed = {role: list(labels) for role, labels in (rules.get("unnamed") or {}).items()}
    more = dict(rules.get("extra") or {})
    containers = rules.get("containers", CONTAINERS)
    groups = rules.get("groups", containers)
    records, used = [], rules.get("used", set())
    used.add(cat_id)
    counts = {"prose": 0, "value": 0, "environment": 0, "data": 0, "disabled": 0}

    def name_of(node):
        if "name" not in node and callable(node.get("read")):
            node["name"] = node["read"]()
        return clean(node.get("name"))

    def unique(parent, label):
        rid, n = f"{parent}.{slug(label)}", 1
        while rid in used:
            n += 1
            rid = f"{parent}.{slug(label)}-{n}"
        used.add(rid)
        return rid

    def add_choices(rec, items):
        if not items:
            raise Invalid(f"{rec['id']}: {rec['label']!r} opened to no choices")
        seen = 0
        for item in items:
            label = clean(item.get("name"))
            if not label or slug(label) == "unnamed":  # a line that separates two runs of choices
                continue
            extra = dict(more) if item.get("enabled", True) else dict(more, enabled=False)
            records.append(base(unique(rec["id"], label), "menuItem", label, seen, item, rec["id"], **extra))
            seen += 1
        if not seen:
            raise Invalid(f"{rec['id']}: {rec['label']!r} opened to choices with no names")
        rec["itemCount"] = seen

    def walk(siblings, parent, order, heading=""):
        shown = [n for n in siblings if n.get("role") not in skipped and not ignore(n)]
        last_text, caption = "", [None]  # caption: the node of the last recorded caption
        for at, node in enumerate(shown):
            role = node.get("role")
            if role == "Text":
                after = shown[at + 1] if at + 1 < len(shown) else None
                # The text straight after a caption is what the caption names: this PC's data, never a label. With
                # another text or nothing after it, it is not even read. Two captions never stand in a row.
                # Straight after means next to it among everything the pane shows: a caption with a picture after
                # it (a grid of symbols) names the picture, and the text after the picture is a caption again.
                before = siblings[siblings.index(node) - 1] if siblings.index(node) else None
                follows = caption[0] is not None and before is caption[0]
                if follows and (after is None or after.get("role") == "Text"):
                    counts["value"] += 1
                    continue
                # With a control or a group after it, it may be that one's label or heading: it is read to tell.
                name = name_of(node)
                # A text names the control beside it, or the heading whose controls follow (a list may stand
                # between the heading's text and its group).
                beside = {clean(n.get("name")).casefold() for n in shown[max(at - 1, 0):at + 3] if n is not node
                          and n.get("role") != "Text"}
                if name:
                    last_text = name
                # The label of the control or the heading beside it, or the heading of the group it stands in.
                if not name or name.casefold() in beside or name.casefold() == heading.casefold():
                    continue
                if follows:
                    counts["value"] += 1
                    continue
                if is_prose(name):
                    counts["prose"] += 1
                    continue
                records.append(base(unique(parent, name), "setting", name, order[0], node, parent,
                                    controlType="label", **more))
                order[0] += 1
                caption[0] = node
                continue
            name = clean(node.get("name"))
            disabled = not node.get("enabled", True)
            enabled = dict(more, enabled=False) if disabled else dict(more)
            if role in containers and node.get("class_name") == RADIO_GROUP:
                label = name or last_text
                if not label:
                    raise Invalid(f"a set of radio buttons under {parent} has no name and no text before it")
                rec = base(unique(parent, label), "setting", label, order[0], node, parent,
                           controlType="radioButton", **enabled)
                order[0] += 1
                records.append(rec)
                add_choices(rec, [k for k in node.get("children", []) if k.get("role") == "RadioButton"])
                continue
            if role in containers:
                if not name or role not in groups:  # it holds its controls for the layout only
                    walk(node.get("children", []), parent, order, heading)
                    continue
                rec = base(unique(parent, name), "group", name, order[0], node, parent, **more)
                order[0] += 1
                records.append(rec)
                walk(node.get("children", []), rec["id"], [0], name)
                continue
            ctype = types.get(role)
            if ctype is None:
                raise Invalid(f"{name or role!r} under {parent} is a {role}, which the Options capture has no rule "
                              f"for; teach scripts/lib/word_options.py what it is")
            label = name or (unnamed[role].pop(0) if unnamed.get(role) else last_text)
            if not label:
                raise Invalid(f"a {role} under {parent} has no name and no text before it")
            rec = base(unique(parent, label), "setting", label, order[0], node, parent, controlType=ctype, **enabled)
            order[0] += 1
            records.append(rec)
            if ctype == DATA_LISTS:
                counts["data"] += 1
            elif ctype in OPENED and is_environment(rec["id"], label):
                counts["environment"] += 1
            elif ctype in OPENED and disabled:  # a list that cannot be opened is recorded as it stands
                counts["disabled"] += 1
            elif ctype in OPENED:
                add_choices(rec, choices(node))

    walk(nodes, cat_id, rules.get("order", [0]))
    left = {role: labels for role, labels in unnamed.items() if labels}
    if left:
        raise Invalid(f"{cat_id} did not show the nameless controls its hand-written list names: {left}")
    noun, label = rules.get("noun", "Options category"), rules.get("label", cat_id[len(ROOT) + 1:])
    worded = rules.get("said") or {}
    for key, said in (("prose", "sentence(s) of explanation not recorded"),
                      ("value", "text(s) after a caption not recorded (what the caption names is this PC's data)"),
                      ("environment", "list(s) of this PC's or the open documents' data recorded without choices"),
                      ("data", "list box(es) recorded without entries"),
                      ("disabled", "disabled list(s) recorded without choices")):
        if counts[key]:
            notes.append(f"{noun} {label}: {counts[key]} {worded.get(key, said)}")
    return records


def validate(records: list) -> None:
    """Refuse an Options inventory that is not whole: the dialog with the number of categories it listed; every
    category with the number of headings and controls the capture saw under it, and at least one setting; every
    list with the choices the capture read, a list of this PC's data with none; nothing of the owner's. Returns
    None; raises Invalid naming every problem."""
    problems, by_id, children = [], {}, {}
    for rec in records:
        if not isinstance(rec, dict) or not isinstance(rec.get("id"), str) or not rec["id"]:
            raise Invalid("an Options record has no id")
        if rec["id"] in by_id:
            problems.append(f"duplicate record id {rec['id']}")
        by_id[rec["id"]] = rec
    for rec in records:
        rid, parent = rec["id"], rec.get("parent")
        if rec.get("app") != "word":
            problems.append(f"{rid}: app must be 'word'")
        if rid != ROOT and not rid.startswith(ROOT + "."):
            problems.append(f"{rid}: an Options record's id starts with {ROOT}")
        if rid == ROOT:
            if "parent" in rec:
                problems.append(f"{rid}: the dialog has no parent")
        elif parent not in by_id:
            problems.append(f"{rid}: its parent {parent} is not in the file")
        else:
            children.setdefault(parent, []).append(rec)
        for field in ("label", "id"):
            if ADDRESS.search(str(rec.get(field, ""))):
                problems.append(f"{rid}: an e-mail address is the owner's data, never a label")
        if is_third_party(str(rec.get("label", ""))):
            problems.append(f"{rid}: a third-party entry ({rec.get('label')}) is not Word's")
        if "enabled" in rec and (rec["enabled"] is not False or rec.get("kind") not in ("setting", "menuItem")):
            problems.append(f"{rid}: `enabled` is written only as false, on a setting or a choice")
    dialog = by_id.get(ROOT)
    if dialog is None or dialog.get("kind") != "dialog":
        raise Invalid("; ".join(problems + [f"the dialog record {ROOT} is missing"]))

    def below(rid):
        for kid in children.get(rid, []):
            yield kid
            yield from below(kid["id"])

    def held(rec, count, one, many):
        if not isinstance(rec.get("itemCount"), int) or isinstance(rec.get("itemCount"), bool):
            problems.append(f"{rec['id']}: no itemCount, so a lost {one} goes unseen")
        elif rec["itemCount"] != count:
            problems.append(f"{rec['id']}: holds {count} of the {rec['itemCount']} {many} the capture recorded")

    tabs = [r for r in children.get(ROOT, []) if r.get("kind") == "dialogTab"]
    held(dialog, len(tabs), "category", "categories")
    for rec in children.get(ROOT, []):
        if rec.get("kind") not in ("dialogTab", "control"):
            problems.append(f"{rec['id']}: only a category or one of the dialog's own buttons sits under {ROOT}")
    for tab in tabs:
        under = [r for r in below(tab["id"])]
        held(tab, sum(1 for r in under if r.get("kind") in COUNTED), "heading or control",
             "headings and controls")
        if not any(r.get("kind") == "setting" for r in under):
            problems.append(f"{tab['id']}: the category holds no setting")
        for rec in under:
            if rec.get("kind") not in COUNTED + ("menuItem",):
                problems.append(f"{rec['id']}: a {rec.get('kind')} is not a heading, a setting or a choice")
            if rec.get("kind") == "menuItem" and by_id[rec["parent"]].get("kind") != "setting":
                problems.append(f"{rec['id']}: a choice belongs to a setting")
            if rec.get("kind") == "group" and by_id[rec["parent"]].get("kind") not in ("dialogTab", "group"):
                problems.append(f"{rec['id']}: a heading sits under a category or another heading")
            if rec.get("kind") != "setting":
                continue
            if by_id[rec["parent"]].get("kind") not in ("dialogTab", "group"):
                problems.append(f"{rec['id']}: a setting sits under a category or a heading")
            ctype, items = rec.get("controlType"), [k for k in children.get(rec["id"], [])]
            if not ctype:
                problems.append(f"{rec['id']}: a setting has a controlType")
            radios = ctype == "radioButton" and bool(items)
            if ctype in OPENED or radios or "itemCount" in rec:
                closed = ctype in OPENED and (environment(rec["id"], rec.get("label"))
                                              or rec.get("enabled") is False)
                if closed and (items or "itemCount" in rec):
                    problems.append(f"{rec['id']}: {rec.get('label')} is recorded without choices (this PC's data, "
                                    f"or a list that was disabled)")
                elif not closed:
                    held(rec, len(items), "choice", "choices")
                    if not items:
                        problems.append(f"{rec['id']}: {rec.get('label')} opens to choices, and none is recorded")
            elif items:
                problems.append(f"{rec['id']}: a {ctype} has no choices, and {len(items)} are recorded under it")
    if problems:
        raise Invalid("; ".join(problems))


def changed(before: dict, after: dict) -> list:
    """The names of the sampled options whose value differs between two samples, or is in one only. Names only:
    a value is never printed."""
    return sorted(name for name in set(before) | set(after) if before.get(name, Invalid) != after.get(name, Invalid))
