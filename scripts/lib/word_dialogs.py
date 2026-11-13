# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The rules of Word's dialog inventory, `design/inventory/word/dialogs.json` (D02 T01 §34).

Pure functions, shared by the capture (`scripts/capture-ui.py --dialogs`), the checker
(`scripts/check-inventory.py`) and the tests.

    word.dialogs.<dialog>                dialog     `openedBy` (the ribbon record whose command opens it) and
                                                    `itemCount` (every tab, heading and control under it)
    word.dialogs.<dialog>.<tab>          dialogTab  a tab, in order; `itemCount` is every heading and control under it
    word.dialogs.<...>.<heading>         group      a heading; its controls are its children
    word.dialogs.<...>.<control>         setting    a control, with `controlType`; `enabled` false when disabled;
                                                    `condition` `expanded` when it shows only in the expanded dialog
    word.dialogs.<...>.<choice>          menuItem   a fixed choice of a list or a menu

A dialog is opened by its own command over the capture's blank document and closed with its Cancel button, or its
Close button where it has no Cancel; no other button is pressed but one the list names as expanding the dialog.
Nothing typed or chosen is read, and no entry of a list of the document's or this PC's data. A control that every
tab of a dialog shows (its OK and Cancel) is recorded once, under the dialog.

Word has two kinds of dialog. A newer one (Track Changes Options) is built like Word Options, and a list of fixed
choices in it is opened, read and closed again with nothing chosen. An old one (`old` below; Font, Paragraph and
most others) offers UI Automation no way to open a list except to press it, and pressing is a toggle that Word
does not keep in step: on 2026-11-13 a list of the Paragraph dialog closed by itself, the second press opened it
again, and the capture's blank document came out changed. So the lists of an old dialog, and the buttons of Find
and Replace that open a menu, are recorded without their choices, by rule, and their choices are D02 T01 §40's.

What a capture reports about itself proves nothing, so `DIALOGS` is written by hand from the live dialogs of the
reference build, and the capture and the checker both hold a file against it.
"""
from word_backstage import ADDRESS, CONTROL_TYPES, slug

ROOT = "word.dialogs"
EXPANDED = "expanded"
# Controls whose own name carries what is chosen in them (a colour button names its colour): the caption before
# the control, and the label the control is recorded under. Such a control's name is never read.
VALUED = {"font color": "Font Color", "underline color": "Underline Color"}
# Each dialog: its id's last part, the title Word shows on it, the idMso of the command that opens it
# (design/inventory/word/baseline.json lists every one), the record of design/inventory/word/ribbon.json that
# command belongs to, and its tabs in order. What each tab must show is in REQUIRED, below.
#   `old` says the dialog is one of Word's old ones, whose lists stay closed (see above).
#   `expand` names the button that expands the dialog and the one that puts it back.
#   `environment` names the lists of a newer dialog whose choices are this PC's or the document's data.
#   `unnamed` gives labels, by role and in order, to controls Word gives no name.
#   `recipients` says the dialog needs a mail merge data source, for which the capture attaches its own fixture.
#   `valued` names the captions whose control names what is chosen in it; such a control's name is never read.
# Find and Replace is not modal and is taken after the modal dialogs; the one that needs a data source comes last.
DIALOGS = (
    {"slug": "font", "old": True, "title": "Font", "valued": VALUED,
     "command": "FontDialog", "openedBy": "word.home.font.font-fontdialog",
     "tabs": ("Font", "Advanced")},
    {"slug": "paragraph", "old": True, "title": "Paragraph", "command": "ParagraphDialog",
     "openedBy": "word.home.paragraph.paragraph", "tabs": ("Indents and Spacing", "Line and Page Breaks")},
    {"slug": "page-setup", "old": True, "title": "Page Setup", "command": "PageSetupDialog",
     "openedBy": "word.layout.page-setup.page-setup", "tabs": ("Margins", "Paper", "Layout")},
    {"slug": "footnote-and-endnote", "old": True, "title": "Footnote and Endnote", "command": "FootnoteEndnoteDialog",
     "openedBy": "word.references.footnotes.footnote-and-endnote-dialog", "tabs": (),
     "unnamed": {"ComboBox": ("Footnotes location", "Endnotes location")}},
    {"slug": "track-changes-options", "title": "Track Changes Options", "command": "ReviewChangeTrackingOptions",
     "openedBy": "word.review.markup.change-tracking-options", "tabs": ()},
    {"slug": "insert-table", "old": True, "title": "Insert Table", "command": "TableInsertDialogWord",
     "openedBy": "word.insert.tables.table.insert-table", "tabs": ()},
    {"slug": "symbol", "old": True, "title": "Symbol", "command": "SymbolsDialog",
     "openedBy": "word.insert.symbols.symbol.more-symbols", "tabs": ("Symbols", "Special Characters")},
    # Index and Table of Contents are one dialog of four tabs, of which each command enables its own alone: the
    # tab a command enables is that dialog's, and the tabs it shows disabled are the other commands'.
    {"slug": "index", "old": True, "title": "Index",
     "command": "IndexInsert", "openedBy": "word.references.index.insert-index",
     "tabs": ("Index",)},
    {"slug": "table-of-contents", "old": True, "title": "Table of Contents", "command": "TableOfContentsDialog",
     "openedBy": "word.references.table-of-contents.table-of-contents.custom-table-of-contents",
     "tabs": ("Table of Contents",)},
    {"slug": "bookmark", "old": True, "title": "Bookmark",
     "command": "BookmarkInsert", "openedBy": "word.insert.links.bookmark",
     "tabs": ()},
    {"slug": "find-and-replace", "old": True, "title": "Find and Replace", "command": "ReplaceDialog",
     "openedBy": "word.home.editing.replace", "tabs": ("Find", "Replace", "Go To"),
     "expand": ("More >>", "<< Less")},
    {"slug": "mail-merge-recipients", "old": True, "title": "Mail Merge Recipients",
     "command": "MailMergeRecipientsEditList",
     "openedBy": "word.mailings.start-mail-merge.edit-recipient-list", "tabs": (),
     "unnamed": {"List": ("Recipients",)},
     "recipients": True},
)
COMMANDS = frozenset(d["command"] for d in DIALOGS)
# What each dialog must show, by tab ("" for the dialog's own controls, which no tab holds): label, control
# type and, for a control of the expanded dialog, EXPANDED. Read from the live dialogs of the reference build
# on 2026-11-13 and reviewed record by record; a control this does not name is recorded and allowed.
REQUIRED = {
    "font": {
        "Font": (("Font", "editBox"), ("Font", "listBox"), ("Font style", "editBox"), ("Font style", "listBox"),
            ("Size", "editBox"), ("Size", "listBox"), ("Font Color", "button"), ("Underline style", "dropdown"),
            ("Underline Color", "button"), ("Effects", "label"), ("Strikethrough", "checkBox"),
            ("Double strikethrough", "checkBox"), ("Superscript", "checkBox"), ("Subscript", "checkBox"),
            ("Small caps", "checkBox"), ("All caps", "checkBox"), ("Hidden", "checkBox"), ("Preview", "label"),),
        "Advanced": (("Character Spacing", "label"), ("Scale", "editBox"), ("Spacing", "dropdown"),
            ("By", "spinner"), ("Position", "dropdown"), ("By", "spinner"), ("Kerning for fonts", "checkBox"),
            ("Points and above", "spinner"), ("OpenType Features", "label"), ("Ligatures", "dropdown"),
            ("Number spacing", "dropdown"), ("Number forms", "dropdown"), ("Stylistic sets", "dropdown"),
            ("Use Contextual Alternates", "checkBox"), ("Preview", "label"),),
        "": (("Set As Default", "button"), ("Text Effects...", "button"), ("OK", "button"), ("Cancel", "button"),),
    },
    "paragraph": {
        "Indents and Spacing": (("General", "label"), ("Alignment", "dropdown"), ("Outline level", "dropdown"),
            ("Collapsed by default", "checkBox"), ("Indentation", "label"), ("Left", "spinner"),
            ("Right", "spinner"), ("Special", "dropdown"), ("By", "spinner"), ("Mirror indents", "checkBox"),
            ("Spacing", "label"), ("Before", "spinner"), ("After", "spinner"), ("Line spacing", "dropdown"),
            ("At", "spinner"), ("Don't add space between paragraphs of the same style", "checkBox"),
            ("Preview", "label"),),
        "Line and Page Breaks": (("Pagination", "label"), ("Widow/Orphan control", "checkBox"),
            ("Keep with next", "checkBox"), ("Keep lines together", "checkBox"), ("Page break before", "checkBox"),
            ("Formatting exceptions", "label"), ("Suppress line numbers", "checkBox"),
            ("Don't hyphenate", "checkBox"), ("Textbox options", "label"), ("Tight wrap", "dropdown"),
            ("Preview", "label"),),
        "": (("Tabs...", "button"), ("Set As Default", "button"), ("OK", "button"), ("Cancel", "button"),),
    },
    "page-setup": {
        "Margins": (("Margins", "label"), ("Top", "spinner"), ("Bottom", "spinner"), ("Left", "spinner"),
            ("Right", "spinner"), ("Gutter", "spinner"), ("Gutter position", "dropdown"),
            ("Portrait", "radioButton"), ("Landscape", "radioButton"), ("Orientation", "label"),
            ("Multiple pages", "dropdown"), ("Apply to", "dropdown"), ("Preview", "label"),),
        "Paper": (("Paper size", "dropdown"), ("Width", "spinner"), ("Height", "spinner"), ("Paper source", "label"),
            ("First page", "listBox"), ("Other pages", "listBox"), ("Apply to", "dropdown"), ("Preview", "label"),
            ("Print Options...", "button"),),
        "Layout": (("Section", "label"), ("Section start", "dropdown"), ("Suppress endnotes", "checkBox"),
            ("Headers and footers", "label"), ("Different odd and even", "checkBox"),
            ("Different first page", "checkBox"), ("From edge", "label"), ("Header", "spinner"),
            ("Footer", "spinner"), ("Page", "label"), ("Vertical alignment", "dropdown"), ("Apply to", "dropdown"),
            ("Preview", "label"), ("Line Numbers...", "button"), ("Borders...", "button"),),
        "": (("Set As Default", "button"), ("OK", "button"), ("Cancel", "button"),),
    },
    "footnote-and-endnote": {
        "": (("Custom mark", "editBox"), ("Location", "label"), ("Footnotes", "radioButton"),
            ("Endnotes", "radioButton"), ("Footnotes location", "dropdown"), ("Endnotes location", "dropdown"),
            ("Convert...", "button"), ("Footnote layout", "label"), ("Columns", "dropdown"), ("Format", "label"),
            ("Number format", "dropdown"), ("Custom mark", "label"), ("Symbol...", "button"),
            ("Start at", "spinner"), ("Numbering", "dropdown"), ("Apply changes to", "dropdown"),
            ("Apply changes", "label"), ("Insert", "button"), ("Cancel", "button"), ("Apply", "button"),),
    },
    "track-changes-options": {
        "": (("Ink", "checkBox"), ("Insertions and Deletions", "checkBox"), ("Formatting", "checkBox"),
            ("Highlight Updates", "checkBox"), ("Other Authors", "checkBox"),
            ("Balloons in All Markup view show", "dropdown"), ("Reviewing Pane", "dropdown"),
            ("Advanced Options...", "button"), ("Change User Name...", "button"), ("OK", "button"),
            ("Cancel", "button"),),
    },
    "insert-table": {
        "": (("Table size", "label"), ("Number of columns", "spinner"), ("Number of rows", "spinner"),
            ("Fixed column width", "radioButton"), ("AutoFit to contents", "radioButton"),
            ("AutoFit to window", "radioButton"), ("AutoFit behavior", "spinner"),
            ("Remember dimensions for new tables", "checkBox"), ("OK", "button"), ("Cancel", "button"),),
    },
    "symbol": {
        "Symbols": (("Font", "editBox"), ("Subset", "dropdown"), ("Recently used symbols", "label"),
            ("Unicode name", "label"), ("Character code", "editBox"), ("from", "dropdown"),
            ("Shortcut key", "label"),),
        "Special Characters": (("Character", "label"), ("Character", "listBox"),),
        "": (("AutoCorrect...", "button"), ("Shortcut Key...", "button"), ("Insert", "button"), ("Cancel", "button"),),
    },
    "index": {
        "Index": (("Print Preview", "label"), ("Type", "label"), ("Indented", "radioButton"),
            ("Run-in", "radioButton"), ("Columns", "spinner"), ("Language", "dropdown"),
            ("Right align page numbers", "checkBox"), ("Tab leader", "dropdown"), ("Formats", "dropdown"),
            ("Mark Entry...", "button"), ("AutoMark...", "button"), ("Modify...", "button"), ("OK", "button"),
            ("Cancel", "button"),),
    },
    "table-of-contents": {
        "Table of Contents": (("General", "label"), ("Print Preview", "label"), ("Show page numbers", "checkBox"),
            ("Right align page numbers", "checkBox"), ("Tab leader", "dropdown"), ("Web Preview", "label"),
            ("Use hyperlinks instead of page numbers", "checkBox"), ("Formats", "dropdown"),
            ("Show levels", "spinner"), ("Options...", "button"), ("Modify...", "button"), ("OK", "button"),
            ("Cancel", "button"),),
    },
    "bookmark": {
        "": (("Bookmark name", "editBox"), ("Bookmark name", "listBox"), ("Add", "button"), ("Delete", "button"),
            ("Go To", "button"), ("Sort by", "label"), ("Name", "radioButton"), ("Location", "radioButton"),
            ("Hidden bookmarks", "checkBox"), ("Cancel", "button"),),
    },
    "find-and-replace": {
        "Find": (("Find In", "menu"), ("Reading Highlight", "menu"), ("Find what", "editBox"), ("More >>", "button"),
            ("Find Next", "button"), ("Cancel", "button"), ("Special", "menu", EXPANDED),
            ("Format", "menu", EXPANDED), ("Search", "dropdown", EXPANDED), ("Match case", "checkBox", EXPANDED),
            ("Find whole words only", "checkBox", EXPANDED), ("Use wildcards", "checkBox", EXPANDED),
            ("Sounds like (English)", "checkBox", EXPANDED), ("Find all word forms (English)", "checkBox", EXPANDED),
            ("Match prefix", "checkBox", EXPANDED), ("Match suffix", "checkBox", EXPANDED),
            ("Ignore punctuation characters", "checkBox", EXPANDED),
            ("Ignore white-space characters", "checkBox", EXPANDED), ("No Formatting", "button", EXPANDED),
            ("Find", "label", EXPANDED), ("Search Options", "label", EXPANDED),),
        "Replace": (("Find what", "editBox"), ("Replace with", "editBox"), ("More >>", "button"),
            ("Replace", "button"), ("Replace All", "button"), ("Find Next", "button"), ("Cancel", "button"),
            ("Special", "menu", EXPANDED), ("Format", "menu", EXPANDED), ("Search", "dropdown", EXPANDED),
            ("Match case", "checkBox", EXPANDED), ("Find whole words only", "checkBox", EXPANDED),
            ("Use wildcards", "checkBox", EXPANDED), ("Sounds like (English)", "checkBox", EXPANDED),
            ("Find all word forms (English)", "checkBox", EXPANDED), ("Match prefix", "checkBox", EXPANDED),
            ("Match suffix", "checkBox", EXPANDED), ("Ignore punctuation characters", "checkBox", EXPANDED),
            ("Ignore white-space characters", "checkBox", EXPANDED), ("No Formatting", "button", EXPANDED),
            ("Replace", "label", EXPANDED), ("Search Options", "label", EXPANDED),),
        "Go To": (("Go to what", "listBox"), ("Enter page number", "editBox"), ("Next", "button"),
            ("Previous", "button"), ("Close", "button"),),
    },
    "mail-merge-recipients": {
        "": (("Recipients", "listBox"), ("Data Source", "listBox"), ("Edit...", "button"), ("Refresh", "button"),
            ("Refine recipient list", "label"), ("Sort...", "button"), ("Filter...", "button"),
            ("Find duplicates...", "button"), ("Find recipient...", "button"), ("Validate addresses...", "button"),
            ("OK", "button"),),
    },
}
TYPES = dict(CONTROL_TYPES, Document="editBox")
SKIPPED = frozenset({"ScrollBar", "Thumb", "Image", "TitleBar", "Separator", "Tab"})
SKIPPED_CLASSES = frozenset({"RichEdit20W"})  # the old dialogs' own hidden edit controls
CONTAINERS = frozenset({"Group", "Pane", "Custom", "ToolBar"})  # walked into; a named group is a record
CLOSERS = ("Cancel", "Close")  # the only buttons the capture closes a dialog with, in this order
COUNTED = ("dialogTab", "group", "setting")


class Invalid(Exception):
    """A dialog's tree or the dialogs inventory breaks one of the rules above."""


def clean(text) -> str:
    """A control's name as a label: without the colon the dialog lays it out with."""
    return str(text or "").strip().rstrip(":").strip()


def dialog_id(spec) -> str:
    return f"{ROOT}.{spec['slug']}"


def tab_id(spec, tab) -> str:
    return f"{dialog_id(spec)}.{slug(tab)}"


def by_slug(name):
    return next((d for d in DIALOGS if d["slug"] == name), None)


def ignore(node) -> bool:
    """Whether a node is a part of the dialog's own machinery and no control: the old dialogs' hidden edit
    controls, and an edit box with no name."""
    return node.get("class_name") in SKIPPED_CLASSES or (node.get("role") == "Edit" and "name" in node
                                                         and not node.get("name"))


def is_environment(spec):
    """A test, for one dialog, of whether a list is recorded without its choices: every list of an old dialog, and
    in a newer one a list whose choices are this PC's or the document's data."""
    names = frozenset(spec.get("environment", ()))
    return lambda _rid, label: bool(spec.get("old")) or label in names


def key_of(node):
    """What tells one control of a dialog from another across two readings: its role, its name where it has one,
    and where it stands."""
    return (node.get("role"), node.get("name"), tuple(node.get("rect") or ()))


def named(node):
    """A node's name, fetched now when it carries a `read` in place of one."""
    if "name" not in node and callable(node.get("read")):
        node["name"] = node["read"]()
    return node.get("name")


def own_buttons(nodes: list, valued=None) -> list:
    """The buttons of a reading that are the dialog's own to press or to share between tabs: every button but one
    that stands straight after a caption `valued` names. That one names what is chosen in it (a colour button),
    and its name is never asked. Without `valued` a dialog has no such button, and no text is read to look for
    one (the text before a button can be what a caption names)."""
    if not valued:
        return [n for n in nodes if n.get("role") == "Button"]
    return [n for before, n in zip([None] + list(nodes), nodes) if n.get("role") == "Button"
            and not (before is not None and before.get("role") == "Text"
                     and str(named(before) or "").casefold() in valued)]


def split_common(reads: list, valued=None) -> tuple:
    """For the readings of a dialog's tabs (each a list of plain nodes), the buttons every tab shows, taken from
    the first reading, and each reading without them: a dialog's own OK and Cancel stand under every tab. They are
    told by name (two tabs can show different buttons in one place), among `own_buttons` only."""
    if len(reads) < 2:
        return [], [list(nodes) for nodes in reads]
    shared = set.intersection(*({named(n) for n in own_buttons(nodes, valued)} for nodes in reads)) - {None, ""}

    def split(nodes):
        mine = [n for n in own_buttons(nodes, valued) if named(n) in shared]
        return mine, [n for n in nodes if not any(n is m for m in mine)]
    return split(reads[0])[0], [split(nodes)[1] for nodes in reads]


def added(collapsed: list, expanded: list, collapse_label: str) -> list:
    """The nodes the expanded dialog shows that the collapsed one did not, without the button that puts it back."""
    seen = {key_of(n) for n in collapsed}
    return [n for n in expanded if key_of(n) not in seen
            and not (n.get("role") == "Button" and n.get("name") == collapse_label)]


def rules_for(spec, label, used, order, expanded=False):
    """The rules `word_options.record_category` records one part of a dialog by."""
    return {"types": TYPES, "skipped": SKIPPED, "ignore": ignore, "is_environment": is_environment(spec),
            "containers": CONTAINERS, "groups": frozenset({"Group"}), "valued": spec.get("valued"),
            "unnamed": None if expanded else spec.get("unnamed"),
            "extra": {"condition": EXPANDED} if expanded else None, "used": used, "order": order,
            "noun": "dialog", "label": label,
            "said": {"environment": "list(s) recorded without choices (the lists of an old dialog are not opened)"}
            if spec.get("old") else None}


def missing(spec, records: list) -> list:
    """What `DIALOGS` says the dialog must show that `records` do not hold: a tab, or a control of a tab (or of
    the dialog itself, under ""), by label, type and, for a control of the expanded dialog, its condition. Each
    is counted: a tab that must show two spinners labelled By holds two, and one does not stand for both."""
    from collections import Counter
    rid = dialog_id(spec)
    tabs = [r.get("label") for r in sorted((r for r in records if r.get("kind") == "dialogTab"
                                            and r.get("parent") == rid), key=lambda r: r.get("order", 0))]
    lacking = []
    if tabs != list(spec["tabs"]):
        lacking.append("the tabs " + ", ".join(spec["tabs"]) if spec["tabs"] else "no tabs")
    tab_prefixes = tuple(tab_id(spec, t) + "." for t in spec["tabs"])
    for tab, wanted in REQUIRED.get(spec["slug"], {}).items():
        prefix = (tab_id(spec, tab) if tab else rid) + "."
        held = Counter((r.get("label"), r.get("controlType"), r.get("condition")) for r in records
                       if r.get("kind") == "setting" and str(r.get("id", "")).startswith(prefix)
                       # the dialog's own controls are those no tab holds
                       and (tab or not str(r.get("id", "")).startswith(tab_prefixes)))
        need = Counter((tuple(entry) + (None,))[:3] for entry in wanted)
        for (label, ctype, condition), count in need.items():
            if held[(label, ctype, condition)] < count:
                where = f"on {tab}" if tab else "of its own"
                times = f" {count} times" if count > 1 else ""
                lacking.append(f"{label} ({ctype}{', ' + condition if condition else ''}){times} {where}")
    return lacking


def validate(records: list, ribbon_ids=None) -> None:
    """Refuse a dialogs inventory that is not whole: every dialog of `DIALOGS` there under its title, opened by the
    record the list names (a record of the ribbon inventory when `ribbon_ids` is given), with its tabs in order
    and every control the list requires; every count the capture recorded held; a list with the choices it was
    read with, and a list of this PC's data with none. Raises Invalid naming every problem."""
    problems, by_id, children = [], {}, {}
    for rec in records:
        if not isinstance(rec, dict) or not isinstance(rec.get("id"), str) or not rec["id"]:
            raise Invalid("a dialog record has no id")
        if rec["id"] in by_id:
            problems.append(f"duplicate record id {rec['id']}")
        by_id[rec["id"]] = rec
    for rec in records:
        rid, parent = rec["id"], rec.get("parent")
        if rec.get("app") != "word":
            problems.append(f"{rid}: app must be 'word'")
        if not rid.startswith(ROOT + "."):
            problems.append(f"{rid}: a dialog record's id starts with {ROOT}.")
        if rec.get("kind") == "dialog":
            if "parent" in rec:
                problems.append(f"{rid}: a dialog has no parent")
        elif parent not in by_id:
            problems.append(f"{rid}: its parent {parent} is not in the file")
        else:
            children.setdefault(parent, []).append(rec)
            if rec.get("kind") not in COUNTED + ("menuItem",):
                problems.append(f"{rid}: a {rec.get('kind')} is not a tab, a heading, a control or a choice")
        if ADDRESS.search(str(rec.get("label", ""))):
            problems.append(f"{rid}: an e-mail address is the owner's data, never a label")
        if "openedBy" in rec and rec.get("kind") != "dialog":
            problems.append(f"{rid}: `openedBy` belongs to the dialog")
        if "condition" in rec and rec["condition"] != EXPANDED:
            problems.append(f"{rid}: the only condition of a dialog's record is {EXPANDED}")

    def below(rid):
        for kid in children.get(rid, []):
            yield kid
            yield from below(kid["id"])

    def held(rec, count, many):
        if not isinstance(rec.get("itemCount"), int) or isinstance(rec.get("itemCount"), bool):
            problems.append(f"{rec['id']}: no itemCount, so a lost record goes unseen")
        elif rec["itemCount"] != count:
            problems.append(f"{rec['id']}: holds {count} of the {rec['itemCount']} {many} the capture recorded")

    known = {dialog_id(spec) for spec in DIALOGS}
    for rec in records:
        if rec.get("kind") == "dialog" and rec["id"] not in known:
            problems.append(f"{rec['id']}: not one of the dialogs scripts/lib/word_dialogs.py lists")
    for spec in DIALOGS:
        rid = dialog_id(spec)
        dialog = by_id.get(rid)
        if dialog is None or dialog.get("kind") != "dialog":
            problems.append(f"the {spec['title']} dialog ({rid}) is not recorded")
            continue
        if dialog.get("label") != spec["title"]:
            problems.append(f"{rid}: is titled {dialog.get('label')!r}, not {spec['title']}")
        if dialog.get("openedBy") != spec["openedBy"]:
            problems.append(f"{rid}: openedBy is {dialog.get('openedBy')!r}, not {spec['openedBy']}")
        elif ribbon_ids is not None and spec["openedBy"] not in ribbon_ids:
            problems.append(f"{rid}: its opener {spec['openedBy']} is not a record of the ribbon inventory")
        under = list(below(rid))
        held(dialog, sum(1 for r in under if r.get("kind") in COUNTED), "tabs, headings and controls")
        for lack in missing(spec, under):
            problems.append(f"{rid}: the {spec['title']} dialog must show {lack}")
        environment = is_environment(spec)
        for rec in under:
            items = children.get(rec["id"], [])
            choices = [k for k in items if k.get("kind") == "menuItem"]
            if rec.get("kind") == "dialogTab":
                held(rec, sum(1 for r in below(rec["id"]) if r.get("kind") in ("group", "setting")),
                     "headings and controls")
            if rec.get("kind") != "setting":
                continue
            ctype = rec.get("controlType")
            if not ctype:
                problems.append(f"{rec['id']}: a control has a controlType")
            opened = ctype in ("dropdown", "menu") or (ctype == "radioButton" and choices)
            closed = ctype in ("dropdown", "menu") and (environment(rec["id"], rec.get("label"))
                                                        or rec.get("enabled") is False)
            if closed and (choices or "itemCount" in rec):
                problems.append(f"{rec['id']}: {rec.get('label')} is recorded without choices (this PC's or the "
                                f"document's data, or a list that was disabled)")
            elif opened and not closed:
                if not choices:
                    problems.append(f"{rec['id']}: {rec.get('label')} opens to choices, and none is recorded")
                elif rec.get("itemCount") != len(choices):
                    problems.append(f"{rec['id']}: holds {len(choices)} of the {rec.get('itemCount')} choices the "
                                    f"capture recorded")
            elif choices:
                problems.append(f"{rec['id']}: a {ctype} has no choices, and {len(choices)} are recorded under it")
    if problems:
        raise Invalid("; ".join(problems))
