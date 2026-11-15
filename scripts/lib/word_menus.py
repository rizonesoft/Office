# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Word's context menus and mini toolbars as records, and the rules that hold them (D02 T01 §35).

`python scripts/capture-ui.py --app word --menus` asks Word for the menu of each context of `CONTEXTS`, over content
the capture writes into a document of its own, and reads the menu and the mini toolbar beside it. This module is
the list written by hand that the capture and `scripts/check-inventory.py` are held against, and the rules that
turn what was read into records. It never touches Word.

What is never read, by rule and not by a filter afterwards: the inner button of a split button (it names the colour
last used on this PC), the edit of a combo box and the unnamed drop-downs of a toolbar (the font, a fill), the
entries of a gallery (Paste Options follows the clipboard), the choices of a submenu the list does not name as
fixed (spelling suggestions, synonyms, recent links) and every name in the comments pane. Such a control is
recorded under the label its place gives it (`unnamed`), or as a control without its entries.
"""
from __future__ import annotations

from collections import Counter

from word_backstage import ADDRESS, slug

ROOT = "word.menus"
MENU_CLASS = "NetUITWMenuContainer"  # the part of a menu's window that holds its items
GALLERY_CLASS = "NetUIGalleryContainer"  # a gallery in a menu (never walked into), or what holds a gallery submenu
CARD_MENU_CLASS = "NetUIReactSubView"  # what holds the items of the comment card's menu
FRAME_CLASS = "NetUIToolWindow"  # the frame of a menu, and of an open submenu beside or under its item
BOX_CLASSES = frozenset({MENU_CLASS, GALLERY_CLASS, CARD_MENU_CLASS})
PERSONA_CLASS = "NetUIPersona"  # the author's picture on a comment's card: never pressed, never read
IGNORED_WINDOWS = frozenset({"NUIDialog"})  # the Layout Options button a selected picture or shape brings
SEPARATOR = "Separator"
TOOLBAR = "Mini Toolbar"
FOLLOWS = frozenset({"Paste Options", "From Clipboard..."})  # available or not follows the clipboard: no state recorded
READINGS = 6  # how often one context is asked for at most, until two readings in a row agree

# Each context: its id's last part, what a builder calls it, what the capture selects (an action of the launcher),
# the selection in words (`condition`), whether a mini toolbar shows beside the menu, the submenus that hold fixed
# choices and are opened one level deep (every other submenu is recorded closed), and the labels of the toolbar's
# controls that have no name of their own, in order. `card` says the menu is the comment card's own, opened from
# the card's More thread actions button and not from the text.
TEXT_TOOLS = ("Font", "Font Size", "Styles")
CONTEXTS = (
    {"slug": "text-selected", "title": "Text, a word selected", "select": "text-selected",
     "condition": "a word of body text is selected", "toolbar": True, "submenus": (),
     "unnamed": TEXT_TOOLS},
    {"slug": "text-caret", "title": "Text, a caret in a word", "select": "text-caret",
     "condition": "the caret stands in a word of body text, nothing selected", "toolbar": True,
     "submenus": (), "unnamed": TEXT_TOOLS},
    {"slug": "table", "title": "Table cell", "select": "table",
     "condition": "the caret stands in a table cell", "toolbar": True, "submenus": ("Insert",),
     "unnamed": ("Font", "Font Size", "Insert", "Delete")},
    {"slug": "picture", "title": "Picture", "select": "picture",
     "condition": "an inline picture is selected", "toolbar": True,
     "submenus": ("Change Picture", "Wrap Text"), "unnamed": ("Style",)},
    {"slug": "shape", "title": "Shape", "select": "shape",
     "condition": "a drawn shape is selected", "toolbar": True,
     "submenus": ("Bring to Front", "Send to Back", "Wrap Text"), "unnamed": ("Style", "Fill", "Outline")},
    {"slug": "header", "title": "Header", "select": "header",
     "condition": "the caret stands in the page header", "toolbar": True, "submenus": (),
     "unnamed": TEXT_TOOLS},
    {"slug": "footer", "title": "Footer", "select": "footer",
     "condition": "the caret stands in the page footer", "toolbar": True, "submenus": (),
     "unnamed": TEXT_TOOLS},
    {"slug": "hyperlink", "title": "Hyperlink", "select": "hyperlink",
     "condition": "the caret stands in a hyperlink", "toolbar": True, "submenus": (),
     "unnamed": TEXT_TOOLS},
    {"slug": "spelling-error", "title": "Spelling error", "select": "spelling",
     "condition": "the caret stands in a word marked as misspelled", "toolbar": False, "submenus": (),
     "unnamed": ()},
    {"slug": "tracked-change", "title": "Tracked change", "select": "revision",
     "condition": "the caret stands in a tracked insertion", "toolbar": True, "submenus": (),
     "unnamed": TEXT_TOOLS},
    {"slug": "comment", "title": "Comment", "select": "comment", "card": True,
     "condition": "the More thread actions button of a comment's card", "toolbar": False, "submenus": (),
     "unnamed": ()},
)
SELECTIONS = frozenset(c["select"] for c in CONTEXTS)

# What each context must show, written from the live menus of Word 16.0.20527.20150 and reviewed entry by entry:
#   "menu": the items in the menu, each (label, controlType) followed by its states;
#   "toolbar": the controls of the mini toolbar, written the same way;
#   "submenus": for each fixed submenu of the context, its choices, written the same way.
# The states: "disabled" (it is available otherwise), and "checked" or "unchecked" for what carries a tick or is on
# or off (it carries none otherwise). A label of FOLLOWS has no state. Each entry is counted. An item the list does
# not name is recorded and allowed; a named one that is missing, has another type or another state is refused.
SEARCH = ("Type to search and use the up and down arrow keys to navigate", "editBox")  # the menu's search box
REQUIRED: dict = {
    "text-selected": {
        "menu": (
            SEARCH, ("Cut", "button"),
            ("Copy", "button"), ("Paste Options", "gallery"), ("Copy Link to Location...", "button"),
            ("Font...", "button"), ("Paragraph...", "button"), ("Synonyms", "menu"), ("Read Aloud", "button"),
            ("Translate", "button"), ("Link", "splitButton"), ("New Comment", "button"),
        ),
        "toolbar": (
            ("Edit with Copilot", "button"), ("Font", "comboBox"), ("Font Size", "comboBox"),
            ("Grow Font", "button"), ("Shrink Font", "button"), ("Format Painter", "toggleButton", "unchecked"),
            ("Bold", "toggleButton", "unchecked"), ("Italic", "toggleButton", "unchecked"),
            ("Underline", "toggleButton", "unchecked"), ("Text Highlight Color", "splitButton", "unchecked"),
            ("Font Color", "splitButton"), ("Bullets", "splitButton", "unchecked"),
            ("Numbering", "splitButton", "unchecked"), ("Styles", "menu"), ("New Comment", "button"),
        ),
    },
    "text-caret": {
        "menu": (
            SEARCH,
            ("Cut", "button", "disabled"), ("Copy", "button", "disabled"), ("Paste Options", "gallery"),
            ("Copy Link to Location...", "button"), ("Font...", "button"), ("Paragraph...", "button"),
            ("Synonyms", "menu"), ("Read Aloud", "button"), ("Translate", "button"), ("Link", "splitButton"),
            ("New Comment", "button"),
        ),
        "toolbar": (
            ("Edit with Copilot", "button", "disabled"), ("Font", "comboBox"), ("Font Size", "comboBox"),
            ("Grow Font", "button"), ("Shrink Font", "button"), ("Format Painter", "toggleButton", "unchecked"),
            ("Bold", "toggleButton", "unchecked"), ("Italic", "toggleButton", "unchecked"),
            ("Underline", "toggleButton", "unchecked"), ("Text Highlight Color", "splitButton", "unchecked"),
            ("Font Color", "splitButton"), ("Bullets", "splitButton", "unchecked"),
            ("Numbering", "splitButton", "unchecked"), ("Styles", "menu"), ("New Comment", "button"),
        ),
    },
    "table": {
        "menu": (
            SEARCH,
            ("Cut", "button", "disabled"), ("Copy", "button", "disabled"), ("Paste Options", "gallery"),
            ("Copy Link to Location...", "button"), ("Synonyms", "menu"), ("Read Aloud", "button"),
            ("Translate", "button"), ("Insert", "menu"), ("Delete Cells...", "button"),
            ("Split Cells...", "button"), ("Border Styles", "splitButton"), ("Text Direction...", "button"),
            ("Table Properties...", "button"), ("Link", "splitButton"), ("New Comment", "button"),
        ),
        "toolbar": (
            ("Edit with Copilot", "button", "disabled"), ("Font", "comboBox"), ("Font Size", "comboBox"),
            ("Grow Font", "button"), ("Shrink Font", "button"), ("Bullets", "splitButton", "unchecked"),
            ("Numbering", "splitButton", "unchecked"), ("Bold", "toggleButton", "unchecked"),
            ("Italic", "toggleButton", "unchecked"), ("Center", "toggleButton", "unchecked"),
            ("Text Highlight Color", "splitButton", "unchecked"), ("Font Color", "splitButton"),
            ("Shading", "splitButton"), ("Borders", "splitButton", "unchecked"),
            ("Format Painter", "toggleButton", "unchecked"), ("Insert", "menu"), ("Delete", "menu"),
            ("New Comment", "button"),
        ),
        "submenus": {
            "Insert": (
                ("Insert Columns to the Left", "button"), ("Insert Columns to the Right", "button"),
                ("Insert Rows Above", "button"), ("Insert Rows Below", "button"), ("Insert Cells...", "button"),
            ),
        },
    },
    "picture": {
        "menu": (
            SEARCH, ("Cut", "button"),
            ("Copy", "button"), ("Paste Options", "gallery"), ("Convert to Office Math", "button", "disabled"),
            ("Convert All to Office Math", "button", "disabled"), ("Edit Picture", "button", "disabled"),
            ("Change Picture", "menu"), ("Group", "menu", "disabled"),
            ("Bring to Front", "splitButton", "disabled"), ("Send to Back", "splitButton", "disabled"),
            ("Link", "splitButton"), ("Save as Picture...", "button"), ("Insert Caption...", "button"),
            ("Wrap Text", "menu"), ("View Alt Text...", "button"), ("Size and Position...", "button"),
            ("Format Picture...", "button"),
        ),
        "toolbar": (
            ("Style", "menu"), ("Crop", "toggleButton", "unchecked"),
        ),
        "submenus": {
            "Change Picture": (
                ("This Device...", "button"), ("From Stock Images...", "button"),
                ("From Online Sources...", "button"), ("From Icons...", "button"), ("From Clipboard...", "button"),
            ),
            "Wrap Text": (
                ("In Line with Text", "galleryItem"), ("Square", "galleryItem"), ("Tight", "galleryItem"),
                ("Through", "galleryItem"), ("Top and Bottom", "galleryItem"), ("Behind Text", "galleryItem"),
                ("In Front of Text", "galleryItem"), ("Edit Wrap Points", "galleryItem", "disabled"),
                ("Move with Text", "button", "disabled", "unchecked"),
                ("Fix Position on Page", "button", "disabled", "unchecked"), ("More Layout Options...", "button"),
                ("Set as Default Layout", "button"),
            ),
        },
    },
    "shape": {
        "menu": (
            SEARCH, ("Cut", "button"),
            ("Copy", "button"), ("Paste Options", "gallery"), ("Add Text", "button"),
            ("Edit Points", "button", "unchecked"), ("Group", "menu", "disabled"),
            ("Bring to Front", "splitButton"), ("Send to Back", "splitButton"), ("Link", "splitButton"),
            ("Save as Picture...", "button"), ("Insert Caption...", "button"), ("Wrap Text", "menu"),
            ("View Alt Text...", "button"), ("Set as Default Shape Style", "button"),
            ("More Layout Options...", "button"), ("Format Shape...", "button"),
        ),
        "toolbar": (
            ("Style", "menu"), ("Fill", "menu"), ("Outline", "menu"),
        ),
        "submenus": {
            "Bring to Front": (
                ("Bring to Front", "button"), ("Bring Forward", "button"), ("Bring in Front of Text", "button"),
            ),
            "Send to Back": (
                ("Send to Back", "button"), ("Send Backward", "button"), ("Send Behind Text", "button"),
            ),
            "Wrap Text": (
                ("In Line with Text", "galleryItem"), ("Square", "galleryItem"), ("Tight", "galleryItem"),
                ("Through", "galleryItem"), ("Top and Bottom", "galleryItem"), ("Behind Text", "galleryItem"),
                ("In Front of Text", "galleryItem"), ("Edit Wrap Points", "galleryItem"),
                ("Move with Text", "button", "checked"), ("Fix Position on Page", "button", "unchecked"),
                ("More Layout Options...", "button"), ("Set as Default Layout", "button", "disabled"),
            ),
        },
    },
    "header": {
        "menu": (
            SEARCH,
            ("Cut", "button", "disabled"), ("Copy", "button", "disabled"), ("Paste Options", "gallery"),
            ("Font...", "button"), ("Paragraph...", "button"), ("Synonyms", "menu"),
            ("Read Aloud", "button", "disabled"), ("Translate", "button"), ("Link", "splitButton"),
            ("New Comment", "button", "disabled"),
        ),
        "toolbar": (
            ("Edit with Copilot", "button", "disabled"), ("Font", "comboBox"), ("Font Size", "comboBox"),
            ("Grow Font", "button"), ("Shrink Font", "button"), ("Format Painter", "toggleButton", "unchecked"),
            ("Bold", "toggleButton", "unchecked"), ("Italic", "toggleButton", "unchecked"),
            ("Underline", "toggleButton", "unchecked"), ("Text Highlight Color", "splitButton", "unchecked"),
            ("Font Color", "splitButton"), ("Bullets", "splitButton", "unchecked"),
            ("Numbering", "splitButton", "unchecked"), ("Styles", "menu"), ("New Comment", "button", "disabled"),
        ),
    },
    "footer": {
        "menu": (
            SEARCH,
            ("Cut", "button", "disabled"), ("Copy", "button", "disabled"), ("Paste Options", "gallery"),
            ("Font...", "button"), ("Paragraph...", "button"), ("Synonyms", "menu"),
            ("Read Aloud", "button", "disabled"), ("Translate", "button"), ("Link", "splitButton"),
            ("New Comment", "button", "disabled"),
        ),
        "toolbar": (
            ("Edit with Copilot", "button", "disabled"), ("Font", "comboBox"), ("Font Size", "comboBox"),
            ("Grow Font", "button"), ("Shrink Font", "button"), ("Format Painter", "toggleButton", "unchecked"),
            ("Bold", "toggleButton", "unchecked"), ("Italic", "toggleButton", "unchecked"),
            ("Underline", "toggleButton", "unchecked"), ("Text Highlight Color", "splitButton", "unchecked"),
            ("Font Color", "splitButton"), ("Bullets", "splitButton", "unchecked"),
            ("Numbering", "splitButton", "unchecked"), ("Styles", "menu"), ("New Comment", "button", "disabled"),
        ),
    },
    "hyperlink": {
        "menu": (
            SEARCH,
            ("Cut", "button", "disabled"), ("Copy", "button", "disabled"), ("Paste Options", "gallery"),
            ("Copy Link to Location...", "button"), ("Edit Hyperlink...", "button"),
            ("Open Hyperlink", "button", "unchecked"), ("Copy Hyperlink", "button"),
            ("Remove Hyperlink", "button"), ("Font...", "button"), ("Paragraph...", "button"),
            ("Synonyms", "menu"), ("Read Aloud", "button"), ("Translate", "button"), ("New Comment", "button"),
        ),
        "toolbar": (
            ("Edit with Copilot", "button", "disabled"), ("Font", "comboBox"), ("Font Size", "comboBox"),
            ("Grow Font", "button"), ("Shrink Font", "button"), ("Format Painter", "toggleButton", "unchecked"),
            ("Bold", "toggleButton", "unchecked"), ("Italic", "toggleButton", "unchecked"),
            ("Underline", "toggleButton", "checked"), ("Text Highlight Color", "splitButton", "unchecked"),
            ("Font Color", "splitButton"), ("Bullets", "splitButton", "unchecked"),
            ("Numbering", "splitButton", "unchecked"), ("Styles", "menu"), ("New Comment", "button"),
        ),
    },
    "spelling-error": {
        "menu": (
            ("Spelling", "menu"), ("Cut", "button", "disabled"), ("Copy", "button", "disabled"),
            ("Paste Options", "gallery"), ("Copy Link to Location...", "button"), ("Read Aloud", "button"),
            ("Translate", "button"), ("Link", "splitButton"), ("New Comment", "button"),
        ),
    },
    "tracked-change": {
        "menu": (
            SEARCH,
            ("Cut", "button", "disabled"), ("Copy", "button", "disabled"), ("Paste Options", "gallery"),
            ("Copy Link to Location...", "button"), ("Accept Insertion", "button"), ("Reject Insertion", "button"),
            ("Track Changes", "button", "unchecked"), ("Link", "splitButton"), ("New Comment", "button"),
        ),
        "toolbar": (
            ("Edit with Copilot", "button", "disabled"), ("Font", "comboBox"), ("Font Size", "comboBox"),
            ("Grow Font", "button"), ("Shrink Font", "button"), ("Format Painter", "toggleButton", "unchecked"),
            ("Bold", "toggleButton", "unchecked"), ("Italic", "toggleButton", "unchecked"),
            ("Underline", "toggleButton", "unchecked"), ("Text Highlight Color", "splitButton", "unchecked"),
            ("Font Color", "splitButton"), ("Bullets", "splitButton", "unchecked"),
            ("Numbering", "splitButton", "unchecked"), ("Styles", "menu"), ("New Comment", "button"),
        ),
    },
    "comment": {
        "menu": (
            ("Link to comment", "button"), ("Resolve thread", "button"), ("Delete thread", "button"),
        ),
    },
}

TOOL_TYPES = {"Button": "button", "ComboBox": "comboBox", "SplitButton": "splitButton", "MenuItem": "menu"}
IDLE_SECONDS = 0.8  # Word is left alone this long after a selection, before its menu is asked for
TICKED, UNTICKED = 1, 0  # UI Automation's toggle states that count as read


class Invalid(Exception):
    """What was read, or a file, is not a whole and lawful menus inventory."""


def clean(text) -> str:
    return " ".join(str(text or "").split())


def by_slug(name):
    return next(c for c in CONTEXTS if c["slug"] == name)


def menu_id(spec) -> str:
    return f"{ROOT}.{spec['slug']}"


def toolbar_id(spec) -> str:
    return f"{menu_id(spec)}.mini-toolbar"


def named(node) -> str:
    """A node's name, fetched now when it carries a `read` in place of one. Called only where the rules allow."""
    if "name" not in node and callable(node.get("read")):
        node["name"] = clean(node["read"]())
    return clean(node.get("name"))


def _band(above, group):
    """Where the line between two groups of items is drawn: the strip between the end of the group above and the
    first item of this one. Word leaves it inside the group, above its first item (a menu), or between the two
    groups (a gallery submenu such as Wrap Text): either way it ends where the first item begins. A node that
    holds that place alone, or None when the two groups were not measured so."""
    kids = group.get("children") or []
    box, first, over = group.get("rect"), kids[0].get("rect") if kids else None, above.get("rect")
    if not box or not first or not over or not (over[3] <= box[1] <= first[1] and over[3] < first[1]):
        return None
    return {"rect": (box[0], over[3], box[2], first[1])}


def menu_items(nodes: list, spec, what="menu") -> list:
    """The items of a menu, from the children of its container (plain nodes: `role`, `class_name`, `enabled`,
    `expandable`, a lazy `read` for the name, `children` for a group). A group of items ends in a separator when
    another follows. An item's own children are never looked at: the inner button of a split button, the entries
    of a gallery and the choices of a submenu are not this function's to read."""
    items, above = [], None

    def one(node):
        role = node.get("role")
        if role == "Edit":  # the menu's own search box
            return {"label": named(node), "type": "editBox", "node": node}
        if role == "SplitButton":
            return {"label": named(node), "type": "splitButton", "node": node}
        if role == "Menu" and node.get("class_name") == GALLERY_CLASS:
            return {"label": named(node), "type": "gallery", "node": node}
        if role == "ListItem":  # a choice of a gallery submenu the list names as fixed (Wrap Text)
            return {"label": named(node), "type": "galleryItem", "node": node}
        if role == "MenuItem":
            item = {"label": named(node), "type": "menu" if node.get("expandable") else "button", "node": node}
            if "toggle" in node:  # an item that carries a tick (Track Changes, Edit Points)
                if node["toggle"] not in (TICKED, UNTICKED):
                    raise Invalid(f"whether {item['label']} of the {spec['title']} {what} is ticked could not be "
                                  f"read; it is not recorded as unticked")
                item["checked"] = node["toggle"] == TICKED
            return item
        raise Invalid(f"the {spec['title']} {what} holds a {role} ({node.get('class_name')}), which the rules of "
                      f"scripts/lib/word_menus.py do not know; it is not passed over")
    for node in nodes:
        if node.get("role") == "Group":
            if above is not None and items and items[-1]["type"] != "separator":
                items.append({"label": SEPARATOR, "type": "separator", "node": _band(above, node)})
            above = node
            items += [one(k) for k in node.get("children", [])]
        else:
            items.append(one(node))
    for item in items:
        if not item["label"]:
            raise Invalid(f"an item of the {spec['title']} {what} has no name")
        if item["type"] == "separator" or item["label"] in FOLLOWS:
            continue
        item["enabled"] = bool(item["node"].get("enabled", True))
    return items


def toolbar_items(nodes: list, spec) -> list:
    """The controls of a mini toolbar, from the children of its bar. A combo box and a drop-down standing straight
    in the bar have no name of their own, or one that carries what is chosen in them: they take the labels
    `unnamed` gives by position and nothing of theirs is read. A button that is a toggle carries its raw state."""
    items, labels = [], list(spec.get("unnamed", ()))
    for node in nodes:
        role = node.get("role")
        if role not in TOOL_TYPES:
            raise Invalid(f"the {spec['title']} mini toolbar holds a {role} ({node.get('class_name')}), which the "
                          f"rules of scripts/lib/word_menus.py do not know; it is not passed over")
        if role in ("ComboBox", "MenuItem"):
            if not labels:
                raise Invalid(f"the {spec['title']} mini toolbar shows more unnamed controls than "
                              f"scripts/lib/word_menus.py names for it")
            item = {"label": labels.pop(0), "type": TOOL_TYPES[role], "node": node}
        else:
            item = {"label": named(node), "type": TOOL_TYPES[role], "node": node}
            if "toggle" in node:  # a button that is on or off, and a split button that shows it is (Bullets)
                if node["toggle"] not in (TICKED, UNTICKED):
                    raise Invalid(f"whether {item['label']} of the {spec['title']} mini toolbar is on could not "
                                  f"be read; it is not recorded as off")
                item["checked"] = node["toggle"] == TICKED
                if role == "Button":
                    item["type"] = "toggleButton"
        if not item["label"]:
            raise Invalid(f"a control of the {spec['title']} mini toolbar has no name")
        item["enabled"] = bool(node.get("enabled", True))
        items.append(item)
    if labels:
        raise Invalid(f"the {spec['title']} mini toolbar shows fewer unnamed controls than "
                      f"scripts/lib/word_menus.py names for it ({', '.join(labels)} not seen)")
    return items


def signature(items: list) -> tuple:
    """What two readings of a menu or a toolbar must agree on."""
    return tuple((i["label"], i["type"], i.get("enabled"), i.get("checked"),
                  signature(i["choices"]) if "choices" in i else None) for i in items)


def records(spec, order: int, menu_node, items: list, bar_node, tools, base) -> list:
    """The records of one context: its `contextMenu`, the menu's items in order (a fixed submenu's choices under
    their item), and the `miniToolbar` with its controls when the context shows one. `base(rid, kind, label,
    order, node, parent, **extra)` makes a record; `node` is None for a separator."""
    rid = menu_id(spec)
    menu = base(rid, "contextMenu", spec["title"], order, menu_node, None, condition=spec["condition"])
    out, used = [menu], {rid}

    def fresh(parent, label):
        rid_, n = f"{parent}.{slug(label)}", 2
        while rid_ in used:
            rid_, n = f"{parent}.{slug(label)}-{n}", n + 1
        used.add(rid_)
        return rid_

    def state(item):
        extra = {}
        if item.get("enabled") is False:
            extra["enabled"] = False
        if "checked" in item:
            extra["checked"] = item["checked"]
        return extra

    def place(parent, entries):
        made = []
        for at, item in enumerate(entries):
            rec = base(fresh(parent, item["label"]), "menuItem", item["label"], at, item["node"], parent,
                       controlType=item["type"], **state(item))
            made.append(rec)
            if "choices" in item:
                below = place(rec["id"], item["choices"])
                rec["itemCount"] = len(below)
                made += below
        return made
    out += place(rid, items)
    if tools is not None:
        bar = base(toolbar_id(spec), "miniToolbar", TOOLBAR, len(items), bar_node, rid, itemCount=len(tools))
        used.add(bar["id"])
        out.append(bar)
        for at, item in enumerate(tools):
            out.append(base(fresh(bar["id"], item["label"]), "control", item["label"], at, item["node"], bar["id"],
                            controlType=item["type"], **state(item)))
    menu["itemCount"] = len(out) - 1
    return out


def missing(spec, under: list) -> list:
    """What `REQUIRED` says the context must show that the records under its menu do not: an item, a control of
    the toolbar or a choice of a fixed submenu (each counted), or the state the list gives it."""
    wanted = REQUIRED.get(spec["slug"])
    if wanted is None:
        return ["an entry in REQUIRED of scripts/lib/word_menus.py: nothing says what it must show"]
    rid, bar, lacking = menu_id(spec), toolbar_id(spec), []
    items = [r for r in under if r.get("kind") == "menuItem" and r.get("parent") == rid]
    tools = [r for r in under if r.get("kind") == "control" and r.get("parent") == bar]

    def hold(found, need, where):
        """Each entry of `need` against the records of its label and type, in order: how many there are, and the
        state the entry gives (the nth entry of a label holds the nth record of it)."""
        by_key = {}
        for rec in found:
            by_key.setdefault((rec.get("label"), rec.get("controlType")), []).append(rec)
        seen = Counter()
        for entry in need:
            key, flags = (entry[0], entry[1]), frozenset(entry[2:])
            at, seen[key] = seen[key], seen[key] + 1
            if at >= len(by_key.get(key, ())):
                total = sum(1 for e in need if (e[0], e[1]) == key)
                if at == len(by_key.get(key, ())):  # said once for a label, however many are short
                    lacking.append(f"{key[0]} ({key[1]}){f' {total} times' if total > 1 else ''} {where}")
                continue
            rec = by_key[key][at]
            if key[0] in FOLLOWS:
                if "enabled" in rec:
                    lacking.append(f"{key[0]} without a state {where}: whether it is available follows the "
                                   f"clipboard")
            elif ("disabled" in flags) != (rec.get("enabled") is False):
                lacking.append(f"{key[0]} {'disabled' if 'disabled' in flags else 'available'} {where}")
            ticked = True if "checked" in flags else False if "unchecked" in flags else None
            if rec.get("checked") is not ticked:
                lacking.append(f"{key[0]} {where} " + ("without `checked`: it carries no tick" if ticked is None
                                                         else f"{'ticked' if ticked else 'not ticked'} (`checked`)"))
    hold(items, wanted.get("menu", ()), "in its menu")
    hold(tools, wanted.get("toolbar", ()), "on its mini toolbar")
    fixed = wanted.get("submenus", {})
    for label in spec["submenus"]:
        if label not in fixed:
            lacking.append(f"an entry for the {label} submenu in REQUIRED of scripts/lib/word_menus.py")
            continue
        owners = [r for r in items if r.get("label") == label]
        below = [r for r in under if owners and r.get("parent") == owners[0]["id"]]
        hold(below, fixed[label], f"under {label}")
    return lacking


def validate(records_: list) -> None:
    """Refuse a menus inventory that is not whole: every context of `CONTEXTS` there under its title and its
    selection, with everything `REQUIRED` says it must show and the states it gives; a mini toolbar where the list
    says one shows and none where it says none; every count held; no submenu recorded open but those the list
    names as fixed. Raises Invalid naming every problem."""
    problems, by_id, children = [], {}, {}
    for rec in records_:
        if not isinstance(rec, dict) or not isinstance(rec.get("id"), str) or not rec["id"]:
            raise Invalid("a menus record has no id")
        if rec["id"] in by_id:
            problems.append(f"duplicate record id {rec['id']}")
        by_id[rec["id"]] = rec
    lawful = {"menuItem": ("contextMenu", "menuItem"), "miniToolbar": ("contextMenu",), "control": ("miniToolbar",)}
    for rec in records_:
        rid, kind, parent = rec["id"], rec.get("kind"), rec.get("parent")
        if rec.get("app") != "word":
            problems.append(f"{rid}: app must be 'word'")
        if not rid.startswith(ROOT + "."):
            problems.append(f"{rid}: a menus record's id starts with {ROOT}.")
        if ADDRESS.search(str(rec.get("label", ""))):
            problems.append(f"{rid}: an e-mail address is the owner's data, never a label")
        if kind == "contextMenu":
            if "parent" in rec:
                problems.append(f"{rid}: a context menu has no parent")
        elif kind not in lawful:
            problems.append(f"{rid}: a {kind} is not a menu, an item, a mini toolbar or a control of one")
        elif parent not in by_id:
            problems.append(f"{rid}: its parent {parent} is not in the file")
        elif by_id[parent].get("kind") not in lawful[kind]:
            problems.append(f"{rid}: a {kind} does not stand under a {by_id[parent].get('kind')}")
        else:
            children.setdefault(parent, []).append(rec)
        if not isinstance(rec.get("bounds"), dict):
            problems.append(f"{rid}: no bounds, so where it stands is not recorded (a capture outside the capture "
                            f"profile, or a place that could not be measured, is not published)")
        if "condition" in rec and kind != "contextMenu":
            problems.append(f"{rid}: `condition` belongs to the context menu")
        if "checked" in rec and not (
                (kind == "control" and rec.get("controlType") in ("toggleButton", "splitButton"))
                or (kind == "menuItem" and rec.get("controlType") == "button")):
            problems.append(f"{rid}: `checked` belongs to an item that carries a tick, or to a toggle or a split "
                            f"button of a mini toolbar")
        if rec.get("controlType") == "toggleButton" and not isinstance(rec.get("checked"), bool):
            problems.append(f"{rid}: a toggle is recorded with whether it is on (`checked`)")

    def below(rid):
        """Everything under `rid`, parents before their children, without recursion: a file is not trusted to be
        shallow, and a chain of a thousand parents is refused by the rules below, not by Python's stack."""
        found, stack = [], [iter(children.get(rid, []))]
        while stack:
            kid = next(stack[-1], None)
            if kid is None:
                stack.pop()
                continue
            found.append(kid)
            stack.append(iter(children.get(kid["id"], [])))
        return found

    def held(rec, count):
        if not isinstance(rec.get("itemCount"), int) or isinstance(rec.get("itemCount"), bool):
            problems.append(f"{rec['id']}: no itemCount, so a lost record goes unseen")
        elif rec["itemCount"] != count:
            problems.append(f"{rec['id']}: holds {count} of the {rec['itemCount']} records the capture recorded")
    known = {menu_id(spec) for spec in CONTEXTS}
    for rec in records_:
        if rec.get("kind") == "contextMenu" and rec["id"] not in known:
            problems.append(f"{rec['id']}: not one of the contexts scripts/lib/word_menus.py lists")
    for spec in CONTEXTS:
        rid = menu_id(spec)
        menu = by_id.get(rid)
        if menu is None or menu.get("kind") != "contextMenu":
            problems.append(f"the {spec['title']} context menu ({rid}) is not recorded")
            continue
        if menu.get("label") != spec["title"]:
            problems.append(f"{rid}: is called {menu.get('label')!r}, not {spec['title']}")
        if menu.get("condition") != spec["condition"]:
            problems.append(f"{rid}: its condition is {menu.get('condition')!r}, not the selection the list gives "
                            f"it ({spec['condition']})")
        under = list(below(rid))
        held(menu, len(under))
        bars = [r for r in under if r.get("kind") == "miniToolbar"]
        if spec["toolbar"] and len(bars) != 1:
            problems.append(f"{rid}: the {spec['title']} context shows a mini toolbar, and {len(bars)} are recorded")
        if not spec["toolbar"] and bars:
            problems.append(f"{rid}: the {spec['title']} context shows no mini toolbar, and one is recorded")
        for bar in bars:
            held(bar, len(list(below(bar["id"]))))
        for rec in under:
            if rec.get("kind") == "menuItem" and children.get(rec["id"]):
                held(rec, len(children[rec["id"]]))
                if rec.get("parent") != rid or rec.get("label") not in spec["submenus"]:
                    problems.append(f"{rec['id']}: a submenu is recorded open only where the list names it as "
                                    f"fixed, one level deep")
        for lack in missing(spec, under):
            problems.append(f"{rid}: the {spec['title']} context must show {lack}")
    if problems:
        raise Invalid("; ".join(problems))
