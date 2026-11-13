# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Word's Backstage view as inventory records (D02 T01 §6): what a capture records, what it never records, and the
checks the committed `design/inventory/word/backstage.json` must pass.

The capture (`scripts/capture-ui.py --app word --backstage`) walks the live view and calls `record_tree` on each page;
`validate` is what `scripts/check-inventory.py` runs on the committed file. Nothing here touches Office.

Three rules shape a record:

- An entry of the navigation list is a page (`backstagePage`) when selecting it shows content in the Backstage pane,
  and an action (`control`, `button`) when it acts on the document or leaves the view. Actions are recorded from the
  list and never invoked, so the capture cannot save or close a document or strand itself in a dialog.
- Only Word's own controls are recorded, by role and label. Values never are: a list's items (recent files, templates,
  places), a person's name, a date, a printer's name or a document property's contents are the owner's, not Word's,
  and the Microsoft-free rule (D02 T01 §21) keeps Word's own prose out too, so descriptive text is not recorded.
- A record that does something carries a `behaviour` sentence in our own words, written after the capture.
"""
from __future__ import annotations

import re

# The navigation entries that act rather than show a page: never invoked by the capture.
ACTIONS = {"Save": "word.backstage.save", "Close": "word.backstage.close", "Options": "word.backstage.options"}
# The shell's own back control (`shell.backstage.back`, D02 T01 §4): not a Word record.
BACK = "Back"
# Entries an add-in puts in the list (Adobe Acrobat's PDF entries): not Word's, as on the ribbon.
THIRD_PARTY = ("Adobe",)
# Each page's idMso in `design/inventory/word/baseline.json` (`placement` backstage, `controlType` tab).
PAGES = {"Home": "PlaceTabHome", "New": "TabOfficeStart", "Open": "TabRecent", "Info": "TabInfo",
         "Save As": "TabSave", "Print": "TabPrint", "Share": "TabShare", "Export": "TabPublish",
         "Account": "TabHelp", "Feedback": "TabOfficeFeedback"}
# UI Automation roles a record is made for, and the inventory control type each becomes.
CONTROL_TYPES = {"Button": "button", "Hyperlink": "button", "SplitButton": "splitButton", "MenuItem": "menu",
                 "ComboBox": "dropdown", "Spinner": "spinner", "Edit": "editBox", "Slider": "slider",
                 "List": "listBox", "CheckBox": "checkBox", "RadioButton": "radioButton", "Tree": "listBox",
                 "DataGrid": "listBox", "Table": "listBox"}
# A person's card (the author, the last editor): its name is the owner's data. A list's entries (recent files,
# templates, places) and a date are never walked, since a list is recorded as one control and text is not recorded.
PRIVATE_CLASSES = {"NetUIPersona"}
# Dropdowns whose items are this PC's environment (its printers, and the paper sizes the selected printer's driver
# offers, and the sensitivity labels an organisation defines), recorded without their items.
ENVIRONMENT_LISTS = {"Printer", "Which Printer", "Page Size", "Sensitivity"}
# Control types that open to a list of items: each must be recorded with its items, apart from ENVIRONMENT_LISTS.
OPENS = {"menu", "dropdown", "splitButton"}
# A people picker is named by the person it shows (the last editor, an author): it is recorded under its field's name.
PEOPLE = {"NetUIPeoplePicker", "NetUIPeoplePickerWell"}
# Roles that carry no record of their own and whose children are walked as if they were the parent's.
TRANSPARENT = {"Pane", "Image", "Text", "Separator", "Custom", "Document", "Menu"}
# A task entry with a pin button is a place the account visited or pinned (a SharePoint site): the owner's, not Word's.
PIN = "Pin this item"
# Roles skipped with everything under them: a scroll bar's arrows and thumb are the pane's, not Word's commands.
SKIPPED = {"ScrollBar", "Thumb"}
# An address in a label is the signed-in account's, never Word's: it is replaced by what it stands for.
ADDRESS = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")
ACCOUNT = "the signed-in account"
# A storage service named with the account's organisation ("OneDrive - Contoso") is recorded as the service alone.
SERVICE = re.compile(r"^(OneDrive|SharePoint|Sites)\s+-\s+.+$")
# The baseline's `taskFormGroup` groups: their list entries are Word's own tasks (Export's Create PDF/XPS, Share's
# e-mail), recorded as buttons, while every other list's entries are the owner's files, templates or places.
TASK_GROUPS = {"GroupOpenPlaces", "SaveGroup", "GroupShare", "PublishGroup"}
# The task groups whose entries only show a detail panel when selected (Share's and Export's tasks): the capture
# selects each and records the panel under it. Open's and Save As's entries open folders (the owner's) or dialogs
# (Browse, Add a Place) and are never selected.
DETAIL_TASK_GROUPS = {"GroupShare", "PublishGroup"}
ACTIONABLE = {"control", "menuItem", "backstagePage"}
# Every actionable behaviour ends with its availability (D02 T01 §6): its last sentence, or the clause after its last
# semicolon, opens with one of these. A word anywhere else in the sentence says nothing about availability.
AVAILABILITY = re.compile(r"(?:^|[.;]\s+)(Always available|Needs |Disabled |Unavailable |Shown only |Empty when |"
                          r"Read only|Available only )[^.;]*\.?$", re.IGNORECASE)
CONDITION = AVAILABILITY  # the name the capture scripts used

# Who captures what an absence reason leaves out, or None when the reason is final (D02 T01 §6, fresh plan review
# gap 3). REFERENCE.md names the same owner, or says "Final:", on the reason's own line.
REASON_OWNERS = {"document-state": "D02 T01 §36", "account-state": "D02 T01 §37", "layout-variant": "D02 T01 §37",
                 "not-offered": None, "not-exposed": None}
# Baseline Backstage ids that UI Automation shows without an automation id, matched by their page and label instead.
LABELS = {
    ("TabRecent", "Recent"): "ButtonTaskRecentDocuments", ("TabRecent", "Shared with Me"): "ButtonTaskSharedWithMe",
    ("TabRecent", "Browse"): "ButtonOpenBrowse", ("TabRecent", "OneDrive"): "ButtonTaskDynamicServiceProvider",
    ("TabSave", "OneDrive"): "ButtonTaskDynamicServiceProvider", ("TabRecent", "Recover Unsaved Documents"): "GroupRecoverUnsavedFiles",
    ("TabInfo", "Always Open Read-Only"): "FileMarkAsReadOnlyRecommended",
    ("TabInfo", "Encrypt with Password"): "FileDocumentEncrypt", ("TabInfo", "Restrict Access"): "UsagePermissions",
    ("TabInfo", "Add a Digital Signature"): "FileAddDigitalSignature", ("TabInfo", "Mark as Final"): "FileMarkAsFinal",
    ("TabInfo", "Properties"): "GroupDocumentProperties",
    ("TabShare", "Share with People"): "ShareWithPeopleFromSharePane", ("TabShare", "Email"): "SendUsingEmail",
    ("TabShare", "Present Online"): "BroadcastSlideShowBackstage",
    ("TabPublish", "Create PDF/XPS Document"): "FileSaveAsPdfOrXps", ("TabPublish", "Change File Type"): "FileTypeChange",
    ("TabPrint", "Print Preview"): "GroupPrintPreview", ("TabPrint", "Pages"): "FilePrintCustomRange",
    ("TabHelp", "Manage Settings"): "ManagePrivacy",
}


def apply_labels(records):
    """Give each record LABELS names its idMso, where UI Automation showed none. Changes the records in place."""
    page_of = {}
    for rec in records:
        if rec.get("kind") == "backstagePage":
            page_of[rec["id"]] = rec.get("idMso")
    for rec in records:
        if rec.get("idMso") or rec.get("kind") == "backstagePage":
            continue
        prefix = ".".join(rec["id"].split(".")[:3])
        page = page_of.get(prefix)
        mso = LABELS.get((page, rec.get("label")))
        if mso and not any(r.get("idMso") == mso and r["id"].startswith(prefix + ".") for r in records):
            rec["idMso"] = mso
    return records


# Baseline Backstage ids the reference capture does not show, each with the reason, documented under
# "Word Backstage absences" in design/inventory/REFERENCE.md. Filled from the capture's own reconciliation.
ABSENT: dict = {
    # document-state
    "AddinDisabledGroup": "document-state", "AllowPersonallyIdentifiableInformation": "document-state",
    "AppGuardTrustPromotion": "document-state", "FileCheckOutDiscard": "document-state",
    "GroupARMPreview": "document-state", "GroupAllAuthors": "document-state",
    "GroupBroadcastResumeWarning": "document-state", "GroupCachedOfflineMergeable": "document-state",
    "GroupCheckIn": "document-state", "GroupFileConvert": "document-state",
    "GroupPrintProtectedView": "document-state", "GroupProtectedView": "document-state",
    "GroupReadOnly": "document-state", "GroupReadOnlyCached": "document-state",
    "GroupReadOnlyCachedMergeable": "document-state", "GroupReadOnlyCheckOutRequired": "document-state",
    "GroupReadOnlyOffline": "document-state", "GroupReadOnlyServer": "document-state",
    "GroupSecurityInformation": "document-state", "GroupSecurityWarning": "document-state",
    "GroupSignatures": "document-state", "GroupThumbnail": "document-state",
    "GroupUpdatesAvailable": "document-state", "GroupUploadErrors": "document-state",
    "GroupWorkflows": "document-state", "GroupWorkflowsUnavailable": "document-state",
    "GrupPolicyWarning": "document-state", "OfficePolicyTips": "document-state", "UpgradeDocument": "document-state",
    "WorkflowsUnavailable": "document-state",
    # account-state
    "GroupBackstageSignIn": "account-state", "GroupBackstageSignInDisabled": "account-state",
    "GroupOfficeInsider": "account-state", "GroupOfficeInsiderAbout": "account-state",
    "GroupOfficeInsiderChannel": "account-state", "GroupOfficeInsiderHelp": "account-state",
    "GroupOfficeInsiderRegistration": "account-state", "GroupOfficeStart": "account-state",
    "GroupUpdateChannel": "account-state", "HomePlaceRecommendedDocuments": "account-state",
    "UpdateChannel": "account-state",
    # layout-variant
    "ButtonGroupCloudServices": "layout-variant", "ButtonGroupItemSaveCloudServices": "layout-variant",
    "ButtonGroupItemSaveLocalServices": "layout-variant", "ButtonGroupLocalServices": "layout-variant",
    "ButtonGroupRecentDocuments": "layout-variant", "ButtonGroupsSave": "layout-variant",
    "ButtonTaskFixItHub": "layout-variant", "CloudFixItHub": "layout-variant",
    "CloudSkyDriveUpsellGroup": "layout-variant", "FixItHub": "layout-variant", "GroupAddLocation": "layout-variant",
    "GroupAddLocationLocal": "layout-variant", "GroupCloudGettingStartedOpenMRUPlacesOrNavSlab": "layout-variant",
    "GroupDynamicSaveCloudServiceProvider": "layout-variant",
    "GroupDynamicSaveLocalServiceProvider": "layout-variant",
    "GroupDynamicSavePinnableCloudServiceProvider": "layout-variant", "GroupDynamicServiceProvider": "layout-variant",
    "GroupGettingStartedOpenMRUPlacesOrNavSlab": "layout-variant",
    "GroupGettingStartedSaveAsMRUCloudPlacesOrNavSlab": "layout-variant",
    "GroupGettingStartedSaveAsMRULocalPlacesOrNavSlab": "layout-variant",
    "GroupGettingStartedSaveAsMRUPlacesOrNavSlab": "layout-variant",
    "GroupLocalGettingStartedOpenMRUPlacesOrNavSlab": "layout-variant", "GroupModernOpenPlaces": "layout-variant",
    "GroupPinnableCloudSaveAsAccessibility": "layout-variant",
    "GroupPinnableGettingStartedSaveAsMRUCloudPlacesOrNav": "layout-variant",
    "GroupRecentCloudPlaces": "layout-variant", "GroupRecentDocumentsNew": "layout-variant",
    "GroupRecentLocalPlaces": "layout-variant", "GroupRecentPinnableCloudPlaces": "layout-variant",
    "GroupRecentPlaces": "layout-variant", "GroupSharedWithMeDocuments": "layout-variant",
    "GroupSharedWithMeDocumentsNew": "layout-variant", "LoadingCloudServicesGroup": "layout-variant",
    "LoadingServicesGroup": "layout-variant", "ModernSaveGroup": "layout-variant",
    "PinnableGroupCloudGettingStartedOpenMRUPlacesOrNavSlab": "layout-variant",
    "SkyDriveUpsellGroup": "layout-variant", "SlabCloudSaveAsAccessibility": "layout-variant",
    "SlabLocalSaveAsAccessibility": "layout-variant", "SlabSaveAsAccessibility": "layout-variant",
    # not-offered
    "FileNewBlogPost": "not-offered", "GroupSendByInstantMessage": "not-offered", "GroupSendToBlog": "not-offered",
    "GroupWorkflowStart": "not-offered", "SendByInstantMessage": "not-offered", "TabOfficeFeedback": "not-offered",
    "WorkflowStart": "not-offered",
    # not-exposed
    "ButtonCategoryCloudServices": "not-exposed", "ButtonCategoryLocalServices": "not-exposed",
    "ButtonCategoryRecentDocuments": "not-exposed", "FileTypes": "not-exposed", "GroupSendUsingEmail": "not-exposed",
    "LocalSave": "not-exposed", "NoTcid": "not-exposed", "Save": "not-exposed", "SaveCloudServices": "not-exposed",
    "Share": "not-exposed", "Workflow": "not-exposed",
}


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s or "unnamed"


def is_third_party(label: str) -> bool:
    return any(mark in (label or "") for mark in THIRD_PARTY)


def classify(label: str) -> str:
    """'skip', 'back', 'third-party', 'action' or 'page' for one navigation entry."""
    if label == BACK:
        return "back"
    if is_third_party(label):
        return "third-party"
    if label in ACTIONS:
        return "action"
    return "page"


def private(text: str) -> str:
    """A label with the owner's data taken out: an e-mail address becomes `the signed-in account`, and a service
    named with the account's organisation becomes the service alone."""
    text = ADDRESS.sub(ACCOUNT, text or "")
    match = SERVICE.match(text.strip())
    return match.group(1) if match else text


def label_of(node, previous_text: str) -> str:
    """A control's label: its own name, or the text just before it when it has none (Print's printer dropdown),
    with the owner's data taken out."""
    name = (node.get("name") or "").strip()
    return private(name if name else previous_text)


def record_tree(page_id: str, node: dict, base, expand=None) -> list:
    """Records for the content under one page. `node` is a plain tree (`role`, `name`, `automation_id`, `class_name`,
    `children`), `base(rid, kind, label, order, node, parent, **extra)` builds a record as the capture tool does, and
    `expand(node)` returns the children a menu or dropdown shows once opened (None when it cannot open)."""
    records, used = [], set()

    def rid(parent, label):
        candidate = f"{parent}.{slug(label)}"
        n = 2
        while candidate in used:
            candidate = f"{parent}.{slug(label)}-{n}"
            n += 1
        used.add(candidate)
        return candidate

    labels = {page_id: ""}
    orders = {}  # the next position under each recorded parent, kept across the containers walked through

    def next_order(parent):
        orders[parent] = orders.get(parent, -1) + 1
        return orders[parent]

    def walk(children, parent, depth, environment=False, tasks=False):
        previous_text = ""
        for child in children:
            role, cls = child.get("role"), child.get("class_name", "")
            task = tasks and role in ("ListItem", "TabItem")
            if task and any((k.get("name") or "").startswith(PIN) for k in child.get("children", [])):
                continue
            if (cls in PRIVATE_CLASSES and not task) or child.get("private") or is_third_party(child.get("name", "")):
                continue
            if role in SKIPPED:
                continue
            if role == "Text":
                previous_text = (child.get("name") or "").strip()
                continue
            if role in TRANSPARENT:
                walk(child.get("children", []), parent, depth, environment, tasks)
                continue
            label = label_of(child, previous_text)
            previous_text = ""
            if cls in PEOPLE:
                if role == "Group":  # the picker itself: its controls belong to the field it is in
                    walk(child.get("children", []), parent, depth, environment, tasks)
                    continue
                label = labels.get(parent, "") or label
            if role == "Group":
                if not label.strip():
                    walk(child.get("children", []), parent, depth, environment, tasks)
                    continue
                me = rid(parent, label)
                labels[me] = label
                extra = {"idMso": child["idMso"]} if child.get("idMso") else {}
                records.append(base(me, "group", label, next_order(parent), child, parent, **extra))
                walk(child.get("children", []), me, depth + 1, environment or label in ENVIRONMENT_LISTS,
                     tasks or child.get("automation_id") in TASK_GROUPS)
                continue
            if role == "List" and tasks:  # a task list is its entries, each a command
                walk(child.get("children", []), parent, depth, environment, tasks)
                continue
            ctype = "button" if task else CONTROL_TYPES.get(role)
            if ctype is None or not label.strip():
                continue
            me = rid(parent, label)
            extra = {"idMso": child["idMso"]} if child.get("idMso") else {}
            records.append(base(me, "control", label, next_order(parent), child, parent, controlType=ctype, **extra))
            if role in ("MenuItem", "ComboBox", "SplitButton") and expand is not None \
                    and label not in ENVIRONMENT_LISTS and not environment:
                items = expand(child)
                if items:
                    control = records[-1]
                    control["itemCount"] = menu_items(items, me)  # what the file must hold under it

    def menu_items(items, parent):
        order = 0
        for item in flatten(items):
            label = private((item.get("name") or "").strip())
            if not label or is_third_party(label) \
                    or item.get("role") not in ("MenuItem", "ListItem", "Button", "CheckBox", "RadioButton"):
                continue
            if label in ("Close", "Open") and item.get("role") == "Button":
                continue  # the dropdown's own open and close arrows
            records.append(base(rid(parent, label), "menuItem", label, order, item, parent))
            order += 1
        return order

    walk(node.get("children", []), page_id, 0)
    return records


def carry_behaviours(existing: list, captured: list) -> list:
    """The captured records, each with the behaviour sentence the committed record of the same id carries: the only
    hand-written field. A record the capture did not see is not kept, so an old record never stands in for a fresh one."""
    written = {r["id"]: r["behaviour"] for r in existing if isinstance(r, dict) and r.get("behaviour")}
    return [dict(r, behaviour=written[r["id"]]) if r["id"] in written and not r.get("behaviour") else r
            for r in captured]


def flatten(items):
    """A menu's or gallery's items in order, through the containers it nests them in, one level deep."""
    out = []
    for item in items:
        if item.get("role") in ("Menu", "Pane", "Group", "List"):
            out += flatten(item.get("children", []))
        else:
            out.append(item)
    return out


def baseline_rows(baseline: dict) -> list:
    """The baseline's Backstage rows as dicts keyed by its columns."""
    cols = baseline["columns"]
    return [dict(zip(cols, row)) for row in baseline["rows"] if dict(zip(cols, row)).get("placement") == "backstage"]


class Invalid(Exception):
    """The Backstage inventory breaks one of the rules above."""


def validate(records: list, baseline: dict, absent: dict, reference_text: str, require_behaviour: bool = True):
    """Refuse a Backstage inventory that is not complete: every baseline page captured as a page or absent for a
    documented reason; every baseline group or control idMso under a captured page captured or absent for a
    documented reason; every navigation action recorded; no third-party or private record; and, with
    `require_behaviour`, a behaviour sentence on every actionable record. Returns None; raises Invalid."""
    by_id, problems = {}, []
    for rec in records:
        if not isinstance(rec, dict) or not rec.get("id"):
            raise Invalid("a Backstage record has no id")
        if rec["id"] in by_id:
            problems.append(f"duplicate record id {rec['id']}")
        by_id[rec["id"]] = rec
        if rec.get("app") != "word":
            problems.append(f"{rec['id']}: app must be 'word'")
        if is_third_party(rec.get("label", "")):
            problems.append(f"{rec['id']}: a third-party entry ({rec.get('label')}) is not Word's")
        if ADDRESS.search(rec.get("label", "")) or ADDRESS.search(rec["id"]):
            problems.append(f"{rec['id']}: an e-mail address is the owner's data, never a label")
        if require_behaviour and rec.get("kind") in ACTIONABLE:
            text = str(rec.get("behaviour", "")).strip()
            if not text:
                problems.append(f"{rec['kind']} {rec['id']} has no behaviour")
            elif not AVAILABILITY.search(text):
                problems.append(f"{rec['kind']} {rec['id']}: its behaviour does not say when it is unavailable, "
                                f"or that it is always available")
    pages = {r["idMso"]: r for r in records if r.get("kind") == "backstagePage" and r.get("idMso")}
    for label, rid in ACTIONS.items():
        rec = by_id.get(rid)
        # Save is a page when it shows Save As (a document never saved), and an action otherwise.
        page = rec is not None and label == "Save" and rec.get("kind") == "backstagePage" \
            and rec.get("target") in by_id and by_id[rec["target"]].get("kind") == "backstagePage"
        if rec is None or not (rec.get("kind") == "control" or page):
            problems.append(f"the navigation action {label} is not recorded as {rid}")
    seen = {r.get("idMso") for r in records if r.get("idMso")}
    for reason in sorted(set(absent.values())):
        line = next((x for x in reference_text.splitlines() if x.startswith(f"- `{reason}`:")), None)
        if line is None:
            problems.append(f"the absence reason {reason} is not documented in design/inventory/REFERENCE.md")
        elif reason not in REASON_OWNERS:
            problems.append(f"the absence reason {reason} has no owning section and is not final")
        elif not (f"`{REASON_OWNERS[reason]}`" in line if REASON_OWNERS[reason] else "Final:" in line):
            problems.append(f"REFERENCE.md does not say {reason} is " +
                            (f"captured by {REASON_OWNERS[reason]}" if REASON_OWNERS[reason] else "final"))
    for row in baseline_rows(baseline):
        mso = row.get("idMso")
        if not mso:
            continue
        if row.get("controlType") == "tab":
            if mso not in pages and mso not in absent:
                problems.append(f"baseline Backstage page {mso} is neither captured nor listed absent")
            continue
        page = row.get("tab")
        if page in pages and mso not in seen and mso not in absent:
            problems.append(f"baseline {row.get('controlType')} {mso} on {page} is neither captured nor listed absent")
    with_items = {r.get("parent") for r in records if r.get("kind") == "menuItem"}
    item_counts = {}
    for rec in records:
        if rec.get("kind") == "menuItem":
            item_counts[rec.get("parent")] = item_counts.get(rec.get("parent"), 0) + 1
    for rec in records:
        if rec.get("controlType") in OPENS and rec["id"] in with_items:
            if not isinstance(rec.get("itemCount"), int):
                problems.append(f"{rec['id']}: {rec['label']} has items but no itemCount, so a lost item goes unseen")
            elif item_counts[rec["id"]] != rec["itemCount"]:
                problems.append(f"{rec['id']}: {rec['label']} holds {item_counts[rec['id']]} of the "
                                f"{rec['itemCount']} items the capture recorded under it")
        if rec.get("controlType") in OPENS:
            environment = rec.get("label") in ENVIRONMENT_LISTS
            if environment and rec["id"] in with_items:
                problems.append(f"{rec['id']}: {rec['label']} lists this PC's or organisation's data and is recorded "
                                f"without its items")
            elif not environment and rec["id"] not in with_items:
                problems.append(f"{rec['id']}: {rec['label']} opens to items, and none is recorded")
    stale = sorted(m for m in absent if m in seen)
    if stale:
        problems.append(f"listed absent but captured: {', '.join(stale)}")
    for rec in records:
        parent = rec.get("parent")
        if parent and parent not in by_id:
            problems.append(f"{rec['id']}: parent {parent} is not in the file")
    if problems:
        raise Invalid("; ".join(problems[:20]) + (f" (and {len(problems) - 20} more)" if len(problems) > 20 else ""))
