#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Capture a reference Office app's ribbon through UI Automation into draft inventory records.

    python scripts/capture-ui.py --app word --tab Home --out R:/scratch/word-home.json
    python scripts/capture-ui.py --app word --all-tabs                       # design/inventory/word/ribbon.json
    python scripts/capture-ui.py --app word --all-tabs --expand --merge      # keep hand-written fields
    python scripts/capture-ui.py --app word --all-tabs --layout simplified   # ribbon-simplified.json

The tool acts only on a window it opened itself. Word and Excel run as a separate instance of their own (COM
DispatchEx), so the operator's open documents are never touched; an app that allows one instance only is launched
only when it is not running, and Outlook is never started unattended (starting it sends the Outbox). The tool's
window is placed on a display that matches capture profile fhd-100 (design/inventory/REFERENCE.md) and maximised;
every profile value is checked, and `bounds` and `size` are recorded only when all of them hold.

Records carry facts only: a control's name (its label, without control characters), control type, UI Automation id (as `idMso` when the app's
baseline lists it, and always as `uiaId`), KeyTip, order and, under the profile, bounds relative to the client
area. ScreenTip text (the UI Automation help text and full description) is never read. A tab whose identifier is not
in the app's baseline, or a group with no control the baseline knows, may be an add-in or may be new in this build:
it is not written to the inventory but to build/capture-ui/<app>-unverified.json, marked `baselineMissing`, and
listed for review. The run reports which of the baseline's core tabs the window did not show, and that File
(Backstage) is not a ribbon tab. Combo box lists (fonts, sizes) are system and document data, so they are not
expanded; the run counts them.
All UI Automation reading runs in a child process of this script, which exits before the app is quit: Excel keeps
running after Quit for as long as the process that read its window through UI Automation is alive. The child asks
this process for every check that needs the app's object model (whether the instance still holds only the tool's
own document) over its standard input and output.
Exit 0 written; 1 when a capture step fails (a menu that will not close, an unknown tab, an existing file without
--merge); 2 when the app cannot be launched safely or the requested layout does not exist in this build.
"""
import argparse
import json
from pathlib import Path
import re
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from office_com import (INVENTORY, OwnProcess, Refused, installed_build, publish, reference_build,  # noqa: E402
                        same_build, transacted_replace, transacted_restore, transacted_unlink)

PROFILE = "fhd-100"
PROFILE_SIZE, PROFILE_DPI, UI_LANGUAGE = (1920, 1080), 96, 1033  # en-US
UNVERIFIED = INVENTORY.parents[1] / "build" / "capture-ui"
LARGE_HEIGHT = 40  # pixels at 100 percent: large ribbon controls are about 66, small ones about 22
BASELINE_COMMIT = "b230a0df45036b2d5e8b49ebf368b3f90ada8d63"
_NO_CONTROL_RE = re.compile(
    r"[\u0000-\u001F\u007F-\u009F\u00AD\u034F\u0600-\u0605\u061C\u06DD\u070F\u0890-\u0891\u08E2"
    r"\u115F-\u1160\u17B4-\u17B5\u180B-\u180F\u200B-\u200F\u202A-\u202E\u2060-\u206F\u3164"
    r"\uFE00-\uFE0F\uFEFF\uFFA0\uFFF0-\uFFFB\uD800-\uDFFF]|[^\u0000-\uFFFF]"
)
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+")


def strip_control_chars(text):
    """Drop Unicode control (Cc), format (Cf, including bidi marks U+202A..U+202E) and default-ignorable characters."""
    return _NO_CONTROL_RE.sub("", text or "")


def sanitize_shell_label(text, uia_id="", id_mso=""):
    """Strip bidi/control characters and replace signed-in operator names or emails on shell account controls."""
    cleaned = strip_control_chars(text).strip()
    if uia_id == "MeControlWidget" or id_mso == "MeControl":
        return "Account"
    if _EMAIL_RE.search(cleaned):
        return "Account"
    return cleaned


class Gone(Exception):
    """A UI Automation element vanished while it was read (a menu rebuilding, a popup closing)."""


class Unsafe(Exception):
    """The app cannot be launched without touching the operator's own windows, or the layout does not exist."""


APPS = {
    # key: (REFERENCE.md row, process, COM ProgID, runs as a separate instance)
    "word": ("Word", "WINWORD.EXE", "Word.Application", True),
    "excel": ("Excel", "EXCEL.EXE", "Excel.Application", True),
    "powerpoint": ("PowerPoint", "POWERPNT.EXE", "PowerPoint.Application", False),
    "visio": ("Visio", "VISIO.EXE", "Visio.Application", False),
    "project": ("Project", "WINPROJ.EXE", "MSProject.Application", False),
    "outlook": ("Outlook (classic)", "OUTLOOK.EXE", "Outlook.Application", False),
}

# UI Automation control type to schema controlType; parts inside split buttons and combo boxes are not controls.
TYPES = {"SplitButton": "splitButton", "Button": "button", "ComboBox": "comboBox", "CheckBox": "checkBox",
         "RadioButton": "radioButton", "Edit": "editBox", "Spinner": "spinner", "Slider": "slider", "Text": "label",
         "List": "gallery", "ListItem": "galleryItem", "MenuItem": "menu"}
LAUNCHER_CLASS = "NetUISimpleButton"  # the small arrow or ellipsis button that opens a group's dialog or pane
ITEM_TYPES = ("MenuItem", "ListItem", "Button", "CheckBox", "RadioButton")


def slug(text):
    return "-".join(w.lower() for w in re.findall(r"[A-Za-z0-9]+", text or "")) or "item"


def keytip(access_key):
    """The last step of a KeyTip path: "Alt, H, F P" is FP, "Alt, H" is H."""
    if not access_key:
        return None
    return access_key.split(",")[-1].replace(" ", "") or None


class Ids:
    """Ids unique within one capture: a parent id plus the label's slug; a repeated label is told apart by its UI
    Automation id, and only an element with neither a free label nor an id of its own gets -2, -3."""

    def __init__(self):
        self.taken = set()

    def make(self, parent, label, discriminator=""):
        base = f"{parent}.{slug(label)}"
        if base in self.taken and discriminator:
            base = f"{base}-{slug(discriminator)}"
        n = 1
        while (f"{base}-{n}" if n > 1 else base) in self.taken:
            n += 1
        final = f"{base}-{n}" if n > 1 else base
        self.taken.add(final)
        return final


class Context:
    def __init__(self, app, build, identifiers, origin=None):
        self.app, self.build, self.identifiers = app, build, identifiers
        self.origin = origin  # client-area origin on screen, only when the capture profile holds
        self.ids, self.skipped, self.unverified, self.notes = Ids(), [], [], []
        self.dropped_reasons = []
        self.elements = {}  # record id -> the element it was read from, for expansion

    def drop_geometry(self, why):
        """Geometry from a window that moved is no longer under the profile: none is kept for this capture."""
        self.origin = None
        self.dropped_reasons.append(why)
        self.notes.append(f"no bounds: {why}")

    def base(self, rid, kind, label, order, element, parent=None, **extra):
        rec = {"id": rid, "app": self.app, "kind": kind, "label": label}
        if parent:
            rec["parent"] = parent
        rec["order"] = order
        rec.update({k: v for k, v in extra.items() if v is not None})
        if element.automation_id:
            rec["uiaId"] = element.automation_id
        self.elements[rid] = element
        tip = keytip(element.access_key)
        if tip:
            rec["keytip"] = tip
        if self.origin is not None and element.rect:
            left, top, right, bottom = element.rect
            rec["bounds"] = {"x": left - self.origin[0], "y": top - self.origin[1], "width": right - left,
                             "height": bottom - top}
            rec["captureProfile"] = PROFILE
            if kind == "control":
                rec["size"] = "large" if bottom - top >= LARGE_HEIGHT else "small"
        rec["source"] = f"uia:{self.build}"
        rec["capturedFrom"] = self.build
        return rec


def identifier(element, identifiers):
    """The control's idMso: its own UI Automation id, its drop-down part's id, or its first part's id, whichever the
    baseline lists first; nothing when the baseline lists none of them."""
    candidates = [element.automation_id]
    if element.control_type == "SplitButton":
        parts = getattr(element, "_validated_children", None)
        if parts is None:
            parts = list(element.children())
    else:
        parts = []
    candidates += [p.automation_id[:-len("_Dropdown")] for p in parts if p.automation_id.endswith("_Dropdown")]
    candidates += [p.automation_id for p in parts]
    return next((c for c in candidates if c and c in identifiers), None)


def control_type(element, use_cached=True):
    if use_cached:
        validated = getattr(element, "_validated_control_type", None)
        if validated is not None:
            return validated
    if element.control_type == "Button":
        if element.class_name == LAUNCHER_CLASS:
            return "dialogLauncher"
        return "toggleButton" if element.can_toggle() else "button"
    if element.control_type == "MenuItem" and element.automation_id.endswith("Gallery"):
        return "gallery"
    return TYPES.get(element.control_type)


def controls_of(group):
    """A group's controls in order; a nested group (an in-ribbon gallery's frame) gives its own controls."""
    for child in group.children():
        if child.control_type == "Group":
            for inner in child.children():
                yield inner, child.name
        else:
            yield child, None


def walk_tab(tab, order, lower, ctx, contextual=False):
    """Records for one selected tab: the tab, its groups and their controls. Content the baseline cannot vouch for
    (a tab whose identifier is not in the baseline, a group with no known control) goes to ctx.unverified, marked
    baselineMissing."""
    tab_unverified = not tab.automation_id or tab.automation_id not in ctx.identifiers
    tab_id = ctx.ids.make(ctx.app, tab.name, tab.automation_id)
    tab_rec = ctx.base(tab_id, "contextualTab" if contextual else "tab", tab.name, order, tab,
                       idMso=tab.automation_id if tab.automation_id in ctx.identifiers else None,
                       baselineMissing=True if tab_unverified else None)
    records, aside = ([], [tab_rec]) if tab_unverified else ([tab_rec], [])
    if tab_unverified:
        why = "no identifier" if not tab.automation_id else f"identifier {tab.automation_id!r} is not in the baseline"
        ctx.skipped.append(f"tab {tab.name!r}: {why}, so its provenance is unverified")
    validated = getattr(lower, "_validated_groups", None)
    if validated is None:
        containers = [c for c in lower.children() if c.control_type == "Group"]
        groups = [
            (g, [(el, frame) for el, frame in controls_of(g) if control_type(el)])
            for c in containers for g in c.children() if g.control_type == "Group"
        ]
    else:
        groups = validated
    for g_order, (group, members) in enumerate(groups):
        ids = [identifier(el, ctx.identifiers) for el, _ in members]
        unverified = tab_unverified or (not any(ids) and (not group.automation_id or group.automation_id not in ctx.identifiers))
        if unverified and not tab_unverified:
            ctx.skipped.append(f"group {group.name!r} on {tab.name!r}: no control the baseline knows, so its "
                               "provenance is unverified")
        target = aside if unverified else records
        group_id = ctx.ids.make(tab_id, group.name)
        target.append(ctx.base(group_id, "group", group.name, g_order, group, parent=tab_id,
                               baselineMissing=True if unverified else None))
        for c_order, ((el, frame), idmso) in enumerate(zip(members, ids)):
            label = el.name or frame or el.automation_id or "control"
            target.append(ctx.base(ctx.ids.make(group_id, label, el.automation_id or idmso or ""), "control", label,
                                   c_order, el,
                                   parent=group_id, controlType=control_type(el), idMso=idmso,
                                   baselineMissing=True if unverified or idmso is None else None))
    ctx.unverified += aside
    return records


def expand_items(control_rec, element, popup_items, ctx):
    """Menu or gallery items, in order, as records under their control."""
    out = []
    for order, item in enumerate(popup_items):
        if not item.name:
            continue
        idmso = item.automation_id if item.automation_id in ctx.identifiers else None
        out.append(ctx.base(ctx.ids.make(control_rec["id"], item.name, item.automation_id), "menuItem", item.name,
                            order, item,
                            parent=control_rec["id"], controlType="galleryItem" if item.control_type == "ListItem"
                            else TYPES.get(item.control_type, "button"),
                            idMso=idmso,
                            baselineMissing=True if control_rec.get("baselineMissing") or idmso is None else None))
    return out


def merge(existing, captured, unverified=None):
    """Captured records refresh `bounds`, `order` and the profile they were taken under; every other field of an
    existing record (behaviour, source and anything written by hand) is kept, and records not captured stay."""
    refreshed = ("bounds", "order", "captureProfile", "size", "capturedFrom")
    keep = {r.get("id"): r for r in existing}
    mapping, matched, out_by_id = {}, set(), {}
    for new in captured:  # parents come before their children, so a parent's mapping is known first
        parent = mapping.get(new.get("parent"), new.get("parent"))
        old = next((r for r in existing if new.get("uiaId") and r.get("uiaId") == new["uiaId"]
                    and r.get("parent") == parent and r["id"] not in matched), None)
        if old is None and new.get("idMso") and not new.get("uiaId"):
            old = next((r for r in existing if r.get("idMso") == new["idMso"] and not r.get("uiaId")
                        and r.get("parent") == parent and r["id"] not in matched), None)
        if old is None:
            same = keep.get(new["id"])
            if same is not None and same["id"] not in matched and same.get("parent") == parent \
                    and not (same.get("uiaId") and new.get("uiaId") and same["uiaId"] != new["uiaId"]) \
                    and not (same.get("idMso") and new.get("idMso") and same["idMso"] != new["idMso"]):
                old = same  # the same id still names the same control
        if old is not None:
            matched.add(old["id"])
            mapping[new["id"]] = old["id"]
            kept = {k: v for k, v in old.items() if k not in refreshed}
            kept.update({k: new[k] for k in refreshed if k in new})
            if "capturedFrom" in new and old.get("capturedFrom") and old.get("source") == f"uia:{old['capturedFrom']}" \
                    and "source" in new:
                kept["source"] = new["source"]
            out_by_id[old["id"]] = kept
            continue
        rid, n = new["id"], 1
        while rid in keep or rid in out_by_id:  # a different control holds this id: give the new one its own
            n += 1
            rid = f"{new['id']}-{n}"
        mapping[new["id"]] = rid
        out_by_id[rid] = dict(new, id=rid, **({"parent": parent} if parent else {}))
    if unverified:
        for u in unverified:
            if u.get("parent") in mapping:
                u["parent"] = mapping[u["parent"]]
                mapping[u["id"]] = u["id"]
    out = [out_by_id.get(r["id"], r) for r in existing]
    out += [r for rid, r in out_by_id.items() if rid not in keep]
    return out


def render(records):
    return "[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n]\n"


# ------------------------------------------------------------------------------------------- Windows side
class Element:
    """A UI Automation element, exposing only what a capture records. Help text is deliberately absent."""

    def __init__(self, uia, raw):
        try:
            self._read(uia, raw)
        except Exception as exc:  # comtypes raises COMError for an element that no longer exists
            if type(exc).__name__ == "COMError":
                raise Gone(str(exc)) from None
            raise

    def _read(self, uia, raw):
        self.uia, self.raw = uia, raw
        # Word embeds an unseen level-number placeholder (U+0001) in numbering gallery names and bidi format marks
        # (U+202A..U+202C) around some item labels; control and format characters are dropped from the name.
        self.name = strip_control_chars(raw.CurrentName or "")
        self.automation_id = raw.CurrentAutomationId or ""
        self.access_key = raw.CurrentAccessKey or ""
        self.class_name = raw.CurrentClassName or ""
        self.control_type = uia.type_name(raw.CurrentControlType)
        self.is_offscreen = bool(getattr(raw, "CurrentIsOffscreen", False))
        r = raw.CurrentBoundingRectangle
        self.rect = (r.left, r.top, r.right, r.bottom) if r.right > r.left and r.bottom > r.top else None

    def runtime_id(self):
        return tuple(self.raw.GetRuntimeId())

    def children(self):
        child = self.uia.walker.GetFirstChildElement(self.raw)
        while child:
            yield Element(self.uia, child)
            child = self.uia.walker.GetNextSiblingElement(child)

    def pattern(self, name):
        u = self.uia.U
        pid, iface = {"toggle": (u.UIA_TogglePatternId, u.IUIAutomationTogglePattern),
                      "select": (u.UIA_SelectionItemPatternId, u.IUIAutomationSelectionItemPattern),
                      "expand": (u.UIA_ExpandCollapsePatternId, u.IUIAutomationExpandCollapsePattern)}[name]
        raw = self.raw.GetCurrentPattern(pid)
        return raw.QueryInterface(iface) if raw else None

    def can_toggle(self):
        return self.pattern("toggle") is not None

    def toggle_state(self):
        p = self.pattern("toggle")
        return None if p is None else p.CurrentToggleState

    def select(self):
        self.pattern("select").Select()

    def expand_state(self):
        p = self.pattern("expand")
        return None if p is None else p.CurrentExpandCollapseState

    def expand(self):
        self.pattern("expand").Expand()

    def collapse(self):
        self.pattern("expand").Collapse()


class Uia:
    def __init__(self):
        import comtypes.client
        comtypes.client.GetModule("UIAutomationCore.dll")
        from comtypes.gen import UIAutomationClient as U
        self.U = U
        self.client = comtypes.client.CreateObject(U.CUIAutomation, interface=U.IUIAutomation)
        self.walker = self.client.RawViewWalker
        self.types = {getattr(U, n): n[len("UIA_"):-len("ControlTypeId")] for n in dir(U)
                      if n.startswith("UIA_") and n.endswith("ControlTypeId")}

    def type_name(self, type_id):
        return self.types.get(type_id, str(type_id))

    def element(self, hwnd):
        return Element(self, self.client.ElementFromHandle(hwnd))


def find(element, test, depth=16):
    for child in element.children():
        if test(child):
            return child
        if depth:
            hit = find(child, test, depth - 1)
            if hit:
                return hit
    return None


def descendants(element, depth=25):
    for child in element.children():
        yield child
        if depth:
            yield from descendants(child, depth - 1)


class Win:
    """The few Win32 calls a capture needs: monitors, window placement and process windows."""

    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.ct, self.wt = ctypes, wintypes
        try:
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))  # per-monitor v2: real pixels
        except (AttributeError, OSError):
            pass  # an older Windows: the profile check below then fails on DPI and no bounds are recorded
        # Private DLL objects with full prototypes: handles are pointer-sized and must never pass as 32-bit ints.
        u = self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.shcore = ctypes.WinDLL("shcore", use_last_error=True)
        HW, HM = wintypes.HWND, wintypes.HMONITOR
        protos = {
            (u, "GetMonitorInfoW"): ([HM, ctypes.c_void_p], wintypes.BOOL),
            (u, "MonitorFromWindow"): ([HW, wintypes.DWORD], HM),
            (u, "GetAncestor"): ([HW, wintypes.UINT], HW),
            (u, "SetWindowPos"): ([HW, HW, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT],
                                  wintypes.BOOL),
            (u, "ShowWindow"): ([HW, ctypes.c_int], wintypes.BOOL),
            (u, "GetWindowRect"): ([HW, ctypes.POINTER(wintypes.RECT)], wintypes.BOOL),
            (u, "ClientToScreen"): ([HW, ctypes.POINTER(wintypes.POINT)], wintypes.BOOL),
            (u, "IsZoomed"): ([HW], wintypes.BOOL), (u, "GetDpiForWindow"): ([HW], wintypes.UINT),
            (u, "IsWindowVisible"): ([HW], wintypes.BOOL),
            (u, "GetWindowThreadProcessId"): ([HW, ctypes.POINTER(wintypes.DWORD)], wintypes.DWORD),
            (u, "GetClassNameW"): ([HW, wintypes.LPWSTR, ctypes.c_int], ctypes.c_int),
            (u, "PostMessageW"): ([HW, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM], wintypes.BOOL),
            (self.shcore, "GetDpiForMonitor"): ([HM, ctypes.c_int, ctypes.POINTER(ctypes.c_uint),
                                                 ctypes.POINTER(ctypes.c_uint)], ctypes.c_long),
        }
        for (dll, name), (args, res) in protos.items():
            fn = getattr(dll, name)
            fn.argtypes, fn.restype = args, res

    def monitors(self):
        ct, wt, found = self.ct, self.wt, []

        class Info(ct.Structure):
            _fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT), ("rcWork", wt.RECT), ("dwFlags", wt.DWORD)]

        proc = ct.WINFUNCTYPE(ct.c_int, wt.HMONITOR, wt.HDC, ct.POINTER(wt.RECT), wt.LPARAM)

        def each(handle, _dc, _rect, _data):
            info = Info()
            info.cbSize = ct.sizeof(Info)
            self.user32.GetMonitorInfoW(handle, ct.byref(info))
            x, y = ct.c_uint(), ct.c_uint()
            self.shcore.GetDpiForMonitor(handle, 0, ct.byref(x), ct.byref(y))
            r = info.rcMonitor
            found.append({"rect": (r.left, r.top, r.right, r.bottom), "dpi": x.value})
            return 1

        self.user32.EnumDisplayMonitors(None, None, proc(each), 0)
        return found

    def top(self, hwnd):
        return self.user32.GetAncestor(hwnd, 2) or hwnd  # GA_ROOT

    def place(self, hwnd, monitor):
        left, top_, _, _ = monitor["rect"]
        self.user32.ShowWindow(hwnd, 9)  # restore first, so the move lands on that monitor
        self.user32.SetWindowPos(hwnd, None, left + 40, top_ + 40, 1200, 800, 0x0014)
        self.user32.ShowWindow(hwnd, 3)  # maximise

    def state(self, hwnd):
        wt = self.wt
        rect, origin = wt.RECT(), wt.POINT(0, 0)
        self.user32.GetWindowRect(hwnd, self.ct.byref(rect))
        self.user32.ClientToScreen(hwnd, self.ct.byref(origin))
        monitor = self.user32.MonitorFromWindow(hwnd, 2)
        return {"zoomed": bool(self.user32.IsZoomed(hwnd)), "dpi": self.user32.GetDpiForWindow(hwnd),
                "window": (rect.left, rect.top, rect.right, rect.bottom), "origin": (origin.x, origin.y),
                "monitor": monitor}

    def windows_of(self, pid, class_name=None):
        """All visible top-level windows of one process, matching class_name when given."""
        ct, wt, found = self.ct, self.wt, []
        proc = ct.WINFUNCTYPE(ct.c_bool, wt.HWND, wt.LPARAM)

        def each(hwnd, _data):
            owner = wt.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ct.byref(owner))
            if owner.value == pid and self.user32.IsWindowVisible(hwnd):
                buf = ct.create_unicode_buffer(256)
                self.user32.GetClassNameW(hwnd, buf, 256)
                if class_name is None or buf.value == class_name:
                    found.append(hwnd)
            return True

        self.user32.EnumWindows(proc(each), 0)
        return found

    def main_window(self, pid, class_name=None):
        """Visible top-level window of one process, matching class_name when given."""
        found = self.windows_of(pid, class_name)
        return found[0] if found else None

    def popups(self, pid):
        """Visible top-level popup windows of one process (menus and galleries open in these)."""
        ct, wt, found = self.ct, self.wt, []
        proc = ct.WINFUNCTYPE(ct.c_bool, wt.HWND, wt.LPARAM)

        def each(hwnd, _data):
            owner = wt.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ct.byref(owner))
            if owner.value == pid and self.user32.IsWindowVisible(hwnd):
                buf = ct.create_unicode_buffer(256)
                self.user32.GetClassNameW(hwnd, buf, 256)
                if buf.value == "Net UI Tool Window":
                    found.append(hwnd)
            return True

        self.user32.EnumWindows(proc(each), 0)
        return found

    def open_context_menu(self, hwnd, element):
        """Open a control's right-click context menu on `hwnd` at `element.rect`'s centre."""
        rect = getattr(element, "rect", None)
        cx = (rect[0] + rect[2]) // 2 if rect else 0
        cy = (rect[1] + rect[3]) // 2 if rect else 0
        lparam = ((cy & 0xFFFF) << 16) | (cx & 0xFFFF)
        self.user32.PostMessageW(hwnd, 0x007B, hwnd, lparam)  # WM_CONTEXTMENU
        hook = getattr(element, "on_context_menu", None)
        if callable(hook):
            hook()

    def activate_keytips(self, hwnd, root=None):
        """Send Alt (VK_MENU) to `hwnd` to activate the window's KeyTips overlay."""
        self.user32.PostMessageW(hwnd, 0x0104, 0x12, 0x20380001)  # WM_SYSKEYDOWN VK_MENU
        self.user32.PostMessageW(hwnd, 0x0105, 0x12, 0xE0380001)  # WM_SYSKEYUP VK_MENU
        hook = getattr(root, "on_keytips", None) if root is not None else None
        if callable(hook):
            hook(True)

    def deactivate_keytips(self, hwnd, root=None):
        """Send Escape (VK_ESCAPE) to `hwnd` to dismiss the window's KeyTips overlay."""
        self.user32.PostMessageW(hwnd, 0x0100, 0x1B, 0)  # WM_KEYDOWN VK_ESCAPE
        self.user32.PostMessageW(hwnd, 0x0101, 0x1B, 0)  # WM_KEYUP VK_ESCAPE
        hook = getattr(root, "on_keytips", None) if root is not None else None
        if callable(hook):
            hook(False)

    def dismiss_surface(self, hwnd, element=None):
        """Send Escape (VK_ESCAPE) to `hwnd` to dismiss an open context menu, flyout or Backstage view."""
        self.user32.PostMessageW(hwnd, 0x0100, 0x1B, 0)  # WM_KEYDOWN VK_ESCAPE
        self.user32.PostMessageW(hwnd, 0x0101, 0x1B, 0)  # WM_KEYUP VK_ESCAPE
        hook = getattr(element, "on_dismiss", None) if element is not None else None
        if callable(hook):
            hook()

    def close_window(self, hwnd, expected_pid=None, expected_class=None):
        """Post WM_CLOSE (0x0010) to a specific top-level window handle so only that window closes (prompting if dirty)."""
        if not isinstance(hwnd, int) or isinstance(hwnd, bool) or hwnd == 0:
            raise Refused("cannot close window without a bound top-level window handle")
        if not self.user32.IsWindow(hwnd):
            raise Refused(f"window handle {hwnd} is no longer a valid window")
        if expected_pid is not None:
            owner = self.wt.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, self.ct.byref(owner))
            if owner.value != expected_pid:
                raise Refused(f"window handle {hwnd} belongs to process {owner.value}, not {expected_pid}")
        if expected_class is not None:
            buf = self.ct.create_unicode_buffer(256)
            self.user32.GetClassNameW(hwnd, buf, 256)
            if buf.value != expected_class:
                raise Refused(f"window handle {hwnd} has class {buf.value!r}, not {expected_class!r}")
        if not self.user32.PostMessageW(hwnd, 0x0010, 0, 0):
            raise OSError(f"PostMessageW(WM_CLOSE) failed for hwnd {hwnd}")
        return True


def profile_monitor(monitors):
    for m in monitors:
        left, top, right, bottom = m["rect"]
        if (right - left, bottom - top) == PROFILE_SIZE and m["dpi"] == PROFILE_DPI:
            return m
    return None


def profile_problems(state, monitor, language, ribbon_height):
    """Every capture-profile value that does not hold; an empty list means bounds may be recorded."""
    problems = []
    if monitor is None:
        problems.append("no display is 1920 by 1080 at 100 percent")
    else:
        left, top, right, bottom = monitor["rect"]
        wl, wt_, wr, wb = state["window"]
        if not (left - 16 <= wl and wr <= right + 16 and top - 16 <= wt_ and wb <= bottom + 16):
            problems.append("the window is not on the profile display")
    if state["dpi"] != PROFILE_DPI:
        problems.append(f"the window runs at {state['dpi']} DPI, not {PROFILE_DPI}")
    if not state["zoomed"]:
        problems.append("the window is not maximised")
    if language != UI_LANGUAGE:
        problems.append(f"the Office display language is {language}, not en-US ({UI_LANGUAGE})")
    if ribbon_height < 60:
        problems.append("the ribbon is not always shown")
    return problems


class _Apartment:
    """A single-threaded COM apartment (STA) so every COM proxy is created, queried and closed on the same
    CoInitialize-d thread while allowing the caller to bound any call with a timeout."""

    def __init__(self, daemon=True, shutdown_timeout=1.5):
        import queue
        import threading
        self._q = queue.Queue()
        self._ready = queue.Queue()
        self.ident = None
        self._closed = False
        self._atexit_registered = False
        self._shutdown_timeout = shutdown_timeout
        self._on_abandoned = None
        self._thread = threading.Thread(target=self._loop, daemon=daemon)
        self._thread.start()
        self._ready.get()

    def _loop(self):
        import ctypes
        import threading
        ole32 = ctypes.windll.ole32
        ole32.CoInitialize(None)
        self.ident = threading.get_ident()
        self._ready.put(True)
        try:
            while True:
                item = self._q.get()
                if item is None:
                    break
                fn, box = item
                try:
                    box.put(("ok", fn()))
                except BaseException as exc:
                    box.put(("err", exc))
        finally:
            ole32.CoUninitialize()

    def call(self, fn, timeout=None):
        import queue
        import threading
        if threading.get_ident() == self.ident:
            return fn()
        box = queue.Queue()
        self._q.put((fn, box))
        try:
            kind, val = box.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError("COM apartment call timed out") from None
        if kind == "err":
            raise val
        return val

    def close(self, join_timeout=5.0, shutdown_timeout=None, on_abandoned=None):
        import atexit
        import threading
        if shutdown_timeout is not None:
            self._shutdown_timeout = shutdown_timeout
        if on_abandoned is not None:
            self._on_abandoned = on_abandoned
        if not self._closed:
            self._closed = True
            self._q.put(None)
        if threading.get_ident() != self.ident and self._thread.is_alive():
            if join_timeout:
                self._thread.join(timeout=join_timeout)
            if self._thread.is_alive() and not self._atexit_registered:
                self._atexit_registered = True
                atexit.register(self._join_at_exit)

    def _join_at_exit(self):
        if self._thread.is_alive() and self._shutdown_timeout:
            self._thread.join(timeout=self._shutdown_timeout)
        if self._thread.is_alive() and self._on_abandoned is not None:
            try:
                self._on_abandoned()
            except Exception:
                pass


class Launched:
    """An app instance this tool started, with its top-level window and its process."""

    def __init__(self, key, dispatch=None, starter=None, owner=None, init_timeout=60.0, win=None):
        row, exe, progid, separate = APPS[key]
        self.key, self.row, self.exe = key, row, exe
        if key == "outlook":
            raise Unsafe("Outlook is not started by the capture tool: starting it sends the Outbox; capture it "
                         "attended (D02 T01 §15)")
        self.proc, self.created, self._created_meta, self.owned, self.started = None, [], [], False, None
        self.app, self.hwnd, self._owned_window_hwnd, self._cancelled = None, None, None, False
        self._win = win
        self.closed_window_hwnds = []
        self._marshaled_app, self.cleanup_errors = None, []
        if not separate:
            # One instance only: start the process ourselves, then use the app only if its window belongs to that
            # very process. An instance the operator opened in between (empty or not) is never touched.
            if self.running(exe):
                raise Unsafe(f"{exe} is running and allows one instance only, so the tool would drive the operator's "
                             f"own window; close {exe} first")
            self.started = (starter or start_process)(exe)
        self._apartment = _Apartment(
            daemon=True,
            shutdown_timeout=min(2.0, max(1.5, init_timeout * 5.0)),
        )
        try:
            self._apartment.call(
                lambda: self._init_com(progid, separate, dispatch, owner),
                timeout=init_timeout,
            )
        except TimeoutError:
            self._recover_hung_launch(
                join_timeout=min(0.05, max(0.01, init_timeout * 0.1)),
                shutdown_timeout=min(2.0, max(1.5, init_timeout * 5.0)),
            )
            raise Refused(f"{exe} did not finish starting within {init_timeout}s") from None
        except BaseException:
            self._apartment.close()
            raise

    def _recover_hung_launch(self, join_timeout=0.05, shutdown_timeout=1.5):
        self._cancelled = True
        self._apartment.close(
            join_timeout=join_timeout,
            shutdown_timeout=shutdown_timeout,
            on_abandoned=self._abandon_hung_launch,
        )

    def _marshal_app(self, app):
        self._marshaled_app = None
        ole = getattr(app, "_oleobj_", None)
        if ole is not None:
            try:
                import pythoncom
                stream = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, ole)
                self._marshaled_app = ("stream", stream)
                return
            except Exception:
                pass
        marshal_fn = getattr(app, "__com_marshal__", None)
        if callable(marshal_fn):
            self._marshaled_app = ("custom", marshal_fn())
            return
        self._marshaled_app = ("direct", app, getattr(getattr(self, "_apartment", None), "ident", None))

    def _marshal_doc(self, doc):
        if not hasattr(self, "_marshaled_docs") or self._marshaled_docs is None:
            self._marshaled_docs = []
        ole = getattr(doc, "_oleobj_", None)
        if ole is not None:
            try:
                import pythoncom
                stream = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, ole)
                self._marshaled_docs.append(("stream", stream))
                return
            except Exception:
                pass
        marshal_fn = getattr(doc, "__com_marshal__", None)
        if callable(marshal_fn):
            self._marshaled_docs.append(("custom", marshal_fn()))
            return
        self._marshaled_docs.append(("direct", doc, getattr(getattr(self, "_apartment", None), "ident", None)))

    def _release_marshaled_app(self):
        token = getattr(self, "_marshaled_app", None)
        self._marshaled_app = None
        if token and token[0] == "stream":
            try:
                import pythoncom
                token[1].Seek(0, 0)
                pythoncom.CoReleaseMarshalData(token[1])
            except Exception:
                pass
        doc_tokens = getattr(self, "_marshaled_docs", None) or []
        self._marshaled_docs = []
        for dtoken in doc_tokens:
            if dtoken and dtoken[0] == "stream":
                try:
                    import pythoncom
                    dtoken[1].Seek(0, 0)
                    pythoncom.CoReleaseMarshalData(dtoken[1])
                except Exception:
                    pass

    def _unmarshal_app(self, target_tid=None):
        token = getattr(self, "_marshaled_app", None)
        self._marshaled_app = None
        if not token:
            app = getattr(self, "app", None)
            if app is not None and getattr(app, "_oleobj_", None) is None and getattr(app, "__com_marshal__", None) is None:
                token = ("direct", app, getattr(app, "_owner_tid", None))
            else:
                return None, None, None
        kind = token[0]
        if kind == "stream":
            import pythoncom
            import win32com.client
            disp = pythoncom.CoGetInterfaceAndReleaseStream(token[1], pythoncom.IID_IDispatch)
            return win32com.client.Dispatch(disp), None, kind
        if kind == "custom":
            return token[1](), None, kind
        if kind == "direct":
            app, prev_tid = token[1], token[2]
            if target_tid is not None and prev_tid is not None and getattr(app, "_owner_tid", None) == prev_tid:
                app._owner_tid = target_tid
            return app, prev_tid, kind
        return None, None, None

    def _unmarshal_docs(self, target_tid=None):
        doc_tokens = getattr(self, "_marshaled_docs", None)
        self._marshaled_docs = []
        if not doc_tokens:
            return list(getattr(self, "created", ()))
        out = []
        for token in doc_tokens:
            kind = token[0]
            if kind == "stream":
                import pythoncom
                import win32com.client
                disp = pythoncom.CoGetInterfaceAndReleaseStream(token[1], pythoncom.IID_IDispatch)
                out.append(win32com.client.Dispatch(disp))
            elif kind == "custom":
                out.append(token[1]())
            elif kind == "direct":
                doc, prev_tid = token[1], token[2]
                if target_tid is not None and prev_tid is not None and getattr(doc, "_owner_tid", None) == prev_tid:
                    doc._owner_tid = target_tid
                out.append(doc)
        return out

    @staticmethod
    def _is_unmodified_blank_doc(doc):
        if getattr(doc, "closed", False):
            return False
        saved = getattr(doc, "Saved", True)
        if saved is None or not bool(saved):
            return False
        if getattr(doc, "Path", ""):
            return False
        full_name = str(getattr(doc, "FullName", "") or "")
        if "\\" in full_name or "/" in full_name:
            return False
        name = str(getattr(doc, "Name", "") or "")
        if "." in name:
            return False
        saved_after = getattr(doc, "Saved", True)
        if saved_after is None or not bool(saved_after):
            return False
        return True

    @staticmethod
    def _enumerate_collection(docs_col, count, app):
        if count == 0:
            return []
        live = None
        last_exc = None
        if hasattr(docs_col, "Item"):
            try:
                live = [docs_col.Item(i) for i in range(1, count + 1)]
            except Exception as exc1:
                try:
                    live = [docs_col.Item(i) for i in range(count)]
                except Exception:
                    last_exc = exc1
        if live is None and hasattr(docs_col, "__iter__"):
            try:
                live = list(docs_col)
            except Exception as exc2:
                last_exc = last_exc or exc2
        if live is None and last_exc is None and hasattr(app, "made"):
            live = [d for d in app.made if not getattr(d, "closed", False)]
        if live is None:
            if last_exc is not None:
                raise last_exc
            raise RuntimeError(f"collection of {count} document(s) is not enumerable")
        return live

    def _get_win(self):
        w = getattr(self, "_win", None)
        return w if w is not None else Win()

    def _verify_powerpoint_window_ownership(self, app, docs=()):
        owned_hwnd = getattr(self, "_owned_window_hwnd", None)
        if not isinstance(owned_hwnd, int) or isinstance(owned_hwnd, bool) or owned_hwnd == 0:
            raise Refused(f"the {self.exe} owned window handle is not bound, so window-bound close was refused")
        win = self._get_win()
        top_fn = getattr(win, "top", lambda h: h)
        cur_self_hwnd = getattr(self, "hwnd", None)
        if cur_self_hwnd is not None:
            if (
                not isinstance(cur_self_hwnd, int)
                or isinstance(cur_self_hwnd, bool)
                or cur_self_hwnd == 0
                or top_fn(cur_self_hwnd) != owned_hwnd
            ):
                raise Refused(
                    f"the {self.exe} current window handle {cur_self_hwnd!r} no longer matches bound window {owned_hwnd}"
                )
        for d in docs:
            wins = getattr(d, "Windows", None)
            if wins is not None:
                try:
                    w_cnt = int(wins.Count)
                except Exception as exc:
                    raise Refused(f"the {self.exe} presentation window count could not be read ({exc})") from None
                if w_cnt != 1:
                    raise Refused(f"the {self.exe} presentation has {w_cnt} windows, not 1")
                if hasattr(wins, "Item"):
                    try:
                        w_item = wins.Item(1)
                        w_hwnd = getattr(w_item, "Hwnd", None)
                        if w_hwnd is None:
                            w_hwnd = getattr(w_item, "HWND", None)
                    except Exception as exc:
                        raise Refused(f"the {self.exe} presentation window handle could not be read ({exc})") from None
                    if isinstance(w_hwnd, int) and not isinstance(w_hwnd, bool):
                        if w_hwnd == 0 or top_fn(w_hwnd) != owned_hwnd:
                            raise Refused(
                                f"the {self.exe} presentation window handle {w_hwnd} does not match bound window {owned_hwnd}"
                            )
        aw_hwnd = None
        try:
            aw = getattr(app, "ActiveWindow", None)
        except Exception as exc:
            raise Refused(f"the {self.exe} ActiveWindow could not be read ({exc})") from None
        if hasattr(app, "ActiveWindow") and aw is None:
            raise Refused(f"the {self.exe} ActiveWindow is no longer available")
        if aw is not None:
            try:
                cand_h = getattr(aw, "Hwnd", None)
                if cand_h is None:
                    cand_h = getattr(aw, "HWND", None)
            except Exception as exc:
                raise Refused(f"the {self.exe} ActiveWindow handle could not be read ({exc})") from None
            if (hasattr(aw, "Hwnd") or hasattr(aw, "HWND")) and cand_h is None:
                raise Refused(f"the {self.exe} ActiveWindow handle is None")
            if isinstance(cand_h, int) and not isinstance(cand_h, bool):
                if cand_h == 0 or top_fn(cand_h) != owned_hwnd:
                    raise Refused(
                        f"the {self.exe} ActiveWindow handle {cand_h} does not match bound window {owned_hwnd}"
                    )
                aw_hwnd = cand_h
        app_hwnd = None
        try:
            raw_h = getattr(app, "HWND", None)
            if raw_h is None:
                raw_h = getattr(app, "Hwnd", None)
        except Exception as exc:
            raise Refused(f"the {self.exe} application HWND could not be read ({exc})") from None
        if (hasattr(app, "HWND") or hasattr(app, "Hwnd")) and raw_h is None and aw_hwnd is None:
            raise Refused(f"the {self.exe} application HWND is None")
        if isinstance(raw_h, int) and not isinstance(raw_h, bool):
            if raw_h == 0 or top_fn(raw_h) != owned_hwnd:
                raise Refused(
                    f"the {self.exe} application HWND {raw_h} does not match bound window {owned_hwnd}"
                )
            app_hwnd = raw_h
        expected_pid = getattr(self, "started", None) or getattr(getattr(self, "proc", None), "pid", None)
        proc_wins = None
        if expected_pid is not None and hasattr(win, "windows_of"):
            proc_wins = [top_fn(h) for h in win.windows_of(expected_pid, "PPTFrameClass")]
            if proc_wins != [owned_hwnd]:
                raise Refused(
                    f"the {self.exe} process windows {proc_wins} do not match sole bound window [{owned_hwnd}]"
                )
        cur_wh = aw_hwnd or app_hwnd or (proc_wins[0] if proc_wins == [owned_hwnd] else None)
        if not isinstance(cur_wh, int) or isinstance(cur_wh, bool) or cur_wh == 0 or top_fn(cur_wh) != owned_hwnd:
            raise Refused(
                f"the {self.exe} current window handle {cur_wh!r} could not be verified against bound window {owned_hwnd}"
            )
        return owned_hwnd

    def _post_close_owned_window(self):
        hwnd = getattr(self, "_owned_window_hwnd", None)
        if not isinstance(hwnd, int) or isinstance(hwnd, bool) or hwnd == 0:
            raise Refused(f"the {self.exe} window handle is not bound, so target-bound window close was refused")
        cur_hwnd = getattr(self, "hwnd", None)
        if cur_hwnd is not None and cur_hwnd != hwnd:
            raise Refused(f"the {self.exe} current window handle {cur_hwnd!r} does not match bound window {hwnd}")
        expected_pid = getattr(self, "started", None) or getattr(getattr(self, "proc", None), "pid", None)
        expected_cls = "PPTFrameClass" if self.key == "powerpoint" else None
        win = self._get_win()
        close_fn = getattr(win, "close_window", None)
        if not callable(close_fn):
            raise Refused(f"Win() exposes no close_window method for {self.exe} hwnd {hwnd}")
        if not close_fn(hwnd, expected_pid=expected_pid, expected_class=expected_cls):
            raise Refused(f"close_window did not post WM_CLOSE for {self.exe} hwnd {hwnd}")
        if not hasattr(self, "closed_window_hwnds") or self.closed_window_hwnds is None:
            self.closed_window_hwnds = []
        self.closed_window_hwnds.append(hwnd)

    def _emergency_close_com(self, target_tid=None):
        import gc
        failures = []
        self._emergency_quitted = False
        app, prev_tid, _kind = self._unmarshal_app(target_tid=target_tid)
        if app is None:
            failures.append(f"could not unmarshal {self.exe} application proxy for emergency cleanup")
            return failures
        docs, docs_col, count = None, None, None
        post_docs, post_count = None, None
        owned_docs = None
        to_close = []
        enum_failed = False
        unowned_count = 0
        remaining = None
        quitted = False
        try:
            try:
                owned_docs = self._unmarshal_docs(target_tid=target_tid)
                docs_col = self._documents_of(app)
                count = int(docs_col.Count)
                docs = self._enumerate_collection(docs_col, count, app)
            except Exception as exc:
                enum_failed = True
                failures.append(f"enumerate documents failed ({type(exc).__name__}: {exc})")
                docs = None
            if not enum_failed:
                if len(docs) < count:
                    unowned_count += count - len(docs)
                metas = list(getattr(self, "_created_meta", ()))
                if owned_docs:
                    matched_ids = set()
                    for idx, created_doc in enumerate(owned_docs):
                        meta = metas[idx] if idx < len(metas) else None
                        match = None
                        for d in docs:
                            if id(d) in matched_ids:
                                continue
                            if self._same_doc(d, created_doc):
                                match = d
                                break
                        if match is None:
                            if not getattr(created_doc, "closed", False):
                                failures.append(
                                    f"the {self.exe} document this tool created is not among open documents, so the instance was left running"
                                )
                            continue
                        matched_ids.add(id(match))
                        if meta is not None and (meta.get("name") is not None or meta.get("full_name") is not None):
                            if self._doc_meta(match) != meta:
                                failures.append(
                                    f"the {self.exe} document this tool created changed identity, so it was left open"
                                )
                                unowned_count += 1
                                continue
                        if not self._is_unmodified_blank_doc(match):
                            failures.append(
                                f"the {self.exe} document has unsaved changes or a file path, so it was left open"
                            )
                            unowned_count += 1
                            continue
                        to_close.append(match)
                    for d in docs:
                        if id(d) not in matched_ids and not getattr(d, "closed", False):
                            unowned_count += 1
                else:
                    unowned_count += sum(1 for d in docs if not getattr(d, "closed", False))
                if self.key == "powerpoint":
                    # PowerPoint's Presentation.Close() and DocumentWindow.Close() discard unsaved changes without
                    # prompting, and Application.Quit() closes unrelated saved presentations without prompting.
                    # Re-verify the Presentations collection after property reads and close only the bound top-level
                    # PPTFrameClass window via WM_CLOSE after releasing COM references.
                    all_clean = (
                        unowned_count == 0
                        and not failures
                        and bool(to_close)
                        and all(self._is_unmodified_blank_doc(d) for d in to_close)
                    )
                    if all_clean:
                        try:
                            post_count = int(docs_col.Count)
                            post_docs = self._enumerate_collection(docs_col, post_count, app)
                        except Exception as exc:
                            enum_failed = True
                            failures.append(f"enumerate documents failed ({type(exc).__name__}: {exc})")
                            post_count, post_docs = count, []
                        if not enum_failed:
                            if post_count != len(to_close) or len(post_docs) != len(to_close):
                                unowned_count += max(1, abs(post_count - len(to_close)), abs(len(post_docs) - len(to_close)))
                            else:
                                post_matched = set()
                                for d in post_docs:
                                    if getattr(d, "closed", False):
                                        unowned_count += 1
                                        continue
                                    m_doc = next(
                                        (tc for tc in to_close if id(tc) not in post_matched and self._same_doc(d, tc)),
                                        None,
                                    )
                                    if m_doc is None:
                                        unowned_count += 1
                                    else:
                                        post_matched.add(id(m_doc))
                    if all_clean and not enum_failed and unowned_count == 0 and not failures:
                        try:
                            self._verify_powerpoint_window_ownership(app, post_docs)
                        except Exception as exc:
                            failures.append(f"verify window ownership failed ({type(exc).__name__}: {exc})")
                    if all_clean and not enum_failed and unowned_count == 0 and not failures:
                        remaining = 0
                    else:
                        remaining = max(count or 0, post_count or 0, len(to_close) + unowned_count, 1)
                else:
                    for doc in to_close:
                        if target_tid is not None and prev_tid is not None and getattr(doc, "_owner_tid", None) == prev_tid:
                            doc._owner_tid = target_tid
                        if getattr(doc, "closed", False):
                            continue
                        try:
                            self._close_owned_doc(doc, app=app)
                        except Exception as exc:
                            failures.append(f"close document failed ({type(exc).__name__}: {exc})")
                            unowned_count += 1
                    try:
                        remaining = int(self._documents_of(app).Count)
                    except Exception as exc:
                        failures.append(f"count open documents failed ({type(exc).__name__}: {exc})")
                still_open = max(remaining or 0, unowned_count)
                if still_open and not any("left running" in f or "left open" in f for f in failures):
                    failures.append(
                        f"the {self.exe} instance holds {still_open} document(s) this tool did not create, so it was left running"
                    )
        finally:
            d = None
            m_doc = None
            doc = None
            docs = None
            post_docs = None
            docs_col = None
            owned_docs = None
            to_close = None
            can_quit = (not enum_failed) and (not failures) and (remaining == 0) and (unowned_count == 0)
            try:
                if can_quit:
                    if self.key == "powerpoint":
                        app = None
                        self.created, self._created_meta, self.app = [], [], None
                        gc.collect()
                        self._post_close_owned_window()
                        quitted = True
                    else:
                        app.Quit()
                        quitted = True
            except Exception as exc:
                failures.append(f"quit failed ({type(exc).__name__}: {exc})")
            finally:
                app = None
                if quitted:
                    self.created, self._created_meta, self.app = [], [], None
                gc.collect()
        self._emergency_quitted = quitted
        return failures

    def _abandon_hung_launch(self):
        failures = []
        self._emergency_quitted = False
        if self.owned and (getattr(self, "_marshaled_app", None) is not None or self.app is not None):
            cleanup_apt = _Apartment(daemon=True, shutdown_timeout=0)
            try:
                failures.extend(
                    cleanup_apt.call(
                        lambda: self._emergency_close_com(cleanup_apt.ident),
                        timeout=0.5,
                    )
                )
            except TimeoutError:
                failures.append(f"{self.exe} emergency COM cleanup timed out")
            except Exception as exc:
                failures.append(f"emergency COM cleanup failed ({type(exc).__name__}: {exc})")
            finally:
                cleanup_apt.close(join_timeout=0.05, shutdown_timeout=0)
        if self.proc is not None:
            try:
                if getattr(self, "_emergency_quitted", False) and not self.proc.exited(0.5):
                    failures.append(f"the {self.exe} instance this tool started did not exit")
            except Exception as exc:
                failures.append(f"waiting for {self.exe} process exit failed ({type(exc).__name__}: {exc})")
            finally:
                try:
                    self.proc.close()
                except Exception as exc:
                    failures.append(f"closing {self.exe} process handle failed ({type(exc).__name__}: {exc})")
                self.proc = None
        if failures:
            self.cleanup_errors.extend(failures)
            print(
                f"capture-ui: {self.exe} emergency shutdown incomplete: {'; '.join(failures)}",
                file=sys.stderr,
                flush=True,
            )

    def _try_bind_window(self, owner):
        if self.hwnd is None:
            try:
                wh = self.window_handle()
                if wh is not None:
                    self.hwnd = self._get_win().top(wh)
                    if self._owned_window_hwnd is None:
                        self._owned_window_hwnd = self.hwnd
            except Exception:
                pass
        if self.proc is None and self.hwnd is not None:
            try:
                self.proc = (owner or OwnProcess)(self.hwnd, self.exe)
            except Exception:
                pass

    def _init_com(self, progid, separate, dispatch, owner):
        exe = self.exe
        if dispatch is None:
            import win32com.client
            dispatch = win32com.client.DispatchEx if separate else win32com.client.Dispatch
        self.app = dispatch(progid)
        if self.started is not None:
            wh = self.window_handle()
            if not isinstance(wh, int) or isinstance(wh, bool) or wh == 0:
                self.app = None
                raise Unsafe(f"{exe} shows no window for process {self.started}, so ownership cannot be proven")
            proc = (owner or OwnProcess)(self._get_win().top(wh), exe)
            if proc.pid != self.started:
                proc.close()
                self.app = None
                raise Unsafe(f"the {exe} window belongs to process {proc.pid}, not the one this tool started")
            self.proc = proc
        if self.open_documents():
            # Dispatch handed back an instance that already holds documents: someone else's. Touch nothing.
            if self.proc is not None:
                self.proc.close()
                self.proc = None
            self.app = None
            raise Unsafe(f"{exe} already holds documents, so it is not an instance this tool started")
        self.owned = True
        try:
            if getattr(self, "_cancelled", False):
                raise Refused(f"{exe} startup was cancelled after timeout")
            self._marshal_app(self.app)
            self.app.Visible = True
            self._try_bind_window(owner)
            if getattr(self, "_cancelled", False):
                raise Refused(f"{exe} startup was cancelled after timeout")
            doc = self.new_document()
            self.created.append(doc)
            self._created_meta.append(self._doc_meta(doc))
            self._marshal_doc(doc)
            doc = None
            if getattr(self, "_cancelled", False):
                raise Refused(f"{exe} startup was cancelled after timeout")
            wh = self.window_handle()
            if wh is not None:
                self.hwnd = self._get_win().top(wh)
                self._owned_window_hwnd = self.hwnd
            if self.proc is None and self.hwnd is not None:
                self.proc = (owner or OwnProcess)(self.hwnd, exe)
            if getattr(self, "_cancelled", False):
                raise Refused(f"{exe} startup was cancelled after timeout")
            self._release_marshaled_app()
        except BaseException:
            self.close()
            raise

    def _call_com(self, fn, timeout=None):
        apt = getattr(self, "_apartment", None)
        return apt.call(fn, timeout=timeout) if apt is not None else fn()

    @staticmethod
    def _doc_meta(doc):
        return {
            "name": getattr(doc, "Name", None),
            "full_name": getattr(doc, "FullName", None),
        }

    @staticmethod
    def _same_doc(a, b):
        if a is b:
            return True
        ole_a, ole_b = getattr(a, "_oleobj_", None), getattr(b, "_oleobj_", None)
        if ole_a is not None and ole_b is not None:
            if ole_a == ole_b:
                return True
            try:
                import pythoncom
                return ole_a.QueryInterface(pythoncom.IID_IUnknown) == ole_b.QueryInterface(pythoncom.IID_IUnknown)
            except Exception:
                return False
        tok_a, tok_b = getattr(a, "_doc_token", None), getattr(b, "_doc_token", None)
        return tok_a is not None and tok_a == tok_b

    @staticmethod
    def running(exe):
        import subprocess
        out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {exe}", "/FO", "CSV", "/NH"], capture_output=True,
                             text=True, check=True).stdout
        return any(line.upper().startswith(f'"{exe.upper()}"') for line in out.splitlines())

    def _documents_of(self, app):
        return {"word": lambda: app.Documents, "excel": lambda: app.Workbooks,
                "powerpoint": lambda: app.Presentations, "visio": lambda: app.Documents,
                "project": lambda: app.Projects}[self.key]()

    def documents(self):
        return self._documents_of(self.app)

    def open_documents(self):
        return self._call_com(lambda: int(self.documents().Count))

    def check_alone(self, timeout=None):
        """The instance must still hold only the tool's own document: one the operator opened in a shared instance
        would be the one the ribbon acts on."""
        return self._call_com(self._check_alone_impl, timeout=timeout)

    def _check_alone_impl(self):
        count = self.open_documents()
        if count != len(self.created):
            raise Refused(f"the {self.exe} instance now holds {count} documents, not only the tool's own; stopping "
                          "before the ribbon acts on someone else's")
        metas = getattr(self, "_created_meta", None) or [self._doc_meta(d) for d in self.created]
        for doc, meta in zip(self.created, metas):
            if getattr(doc, "closed", False):
                raise Refused(f"the {self.exe} document this tool created was closed; stopping before the ribbon acts "
                              "on someone else's")
            try:
                cur_name, cur_full = getattr(doc, "Name", None), getattr(doc, "FullName", None)
            except Exception as exc:
                raise Refused(f"the {self.exe} document this tool created is no longer open ({exc}); stopping before "
                              "the ribbon acts on someone else's") from None
            if (cur_name, cur_full) != (meta["name"], meta["full_name"]):
                raise Refused(f"the {self.exe} document this tool created changed identity; stopping before the ribbon "
                              "acts on someone else's")
        app = getattr(self, "app", None)
        docs = self.documents() if app is not None and hasattr(self, "key") else None
        live = None
        if docs is not None and hasattr(docs, "Item"):
            try:
                live = [docs.Item(i) for i in range(1, count + 1)]
            except Exception:
                try:
                    live = [docs.Item(i) for i in range(count)]
                except Exception:
                    live = None
        if live is None and docs is not None and hasattr(docs, "__iter__"):
            try:
                live = list(docs)
            except Exception:
                live = None
        if live is None and hasattr(app, "made"):
            live = [d for d in app.made if not getattr(d, "closed", False)]
        if live is not None:
            if len(live) != len(self.created) or any(
                getattr(d, "closed", False) or not any(self._same_doc(d, c) for c in self.created) for d in live
            ):
                raise Refused(f"the {self.exe} instance now holds a document this tool did not create; stopping before "
                              "the ribbon acts on someone else's")
        for attr in ("ActiveDocument", "ActiveWorkbook", "ActivePresentation", "ActiveProject"):
            active = getattr(app, attr, None)
            if active is not None and not any(self._same_doc(active, c) for c in self.created):
                raise Refused(f"the active {self.exe} document is not the one this tool created; stopping before the "
                              "ribbon acts on someone else's")

    def _new_project(self):
        projs = getattr(self.app, "Projects", None)
        if projs is not None and hasattr(projs, "Add"):
            proj = projs.Add()
            if proj is not None and not isinstance(proj, bool):
                return proj
        res = self.app.FileNew()
        if res is None or isinstance(res, bool):
            try:
                proj = getattr(self.app, "ActiveProject", None)
                if proj is not None:
                    return proj
            except Exception:
                pass
            try:
                projs = self.documents()
                if int(projs.Count) >= 1 and hasattr(projs, "Item"):
                    return projs.Item(1)
            except Exception:
                pass
        return res

    def _close_owned_doc(self, doc, app=None):
        if not self._is_unmodified_blank_doc(doc):
            raise Refused(f"the {self.exe} document has unsaved changes or a file path")
        if self.key == "powerpoint":
            raise Refused(
                "PowerPoint Presentation.Close and DocumentWindow.Close discard unsaved changes without prompting, "
                "so per-presentation close was refused"
            )
        if self.key == "project":
            # Project items expose no target-bound Close(): close via the project's own window collection,
            # which targets that project's window without silently discarding post-check edits.
            wins = getattr(doc, "Windows2", None) or getattr(doc, "Windows", None)
            if wins is not None:
                w_count = int(wins.Count)
                if w_count > 0:
                    closed_any = False
                    for i in range(w_count, 0, -1):
                        w = wins.Item(i) if hasattr(wins, "Item") else wins(i)
                        if hasattr(w, "Close"):
                            if not self._is_unmodified_blank_doc(doc):
                                raise Refused(f"the {self.exe} document has unsaved changes or a file path")
                            w.Close()
                            closed_any = True
                    if closed_any:
                        return
            raise Refused(
                f"the {self.exe} document exposes no target-bound window Close method, "
                "so active-target close was refused"
            )
        if hasattr(doc, "Close"):
            doc.Close()
            return
        raise Refused(
            f"the {self.exe} document exposes no target-bound Close method, "
            "so application-level active-target close was refused"
        )

    def new_document(self):
        return {"word": lambda: self.app.Documents.Add(), "excel": lambda: self.app.Workbooks.Add(),
                "powerpoint": lambda: self.app.Presentations.Add(), "visio": lambda: self.app.Documents.Add(""),
                "project": self._new_project}[self.key]()

    def window_handle(self):
        if self.key in ("powerpoint", "project"):
            win_cls = "PPTFrameClass" if self.key == "powerpoint" else "JWinproj-WhimperMainClass"
            try:
                aw = getattr(self.app, "ActiveWindow", None)
                aw_hwnd = (getattr(aw, "Hwnd", None) or getattr(aw, "HWND", None)) if aw is not None else None
            except Exception:
                aw_hwnd = None
            if isinstance(aw_hwnd, int) and not isinstance(aw_hwnd, bool) and aw_hwnd != 0:
                return aw_hwnd
            try:
                raw = getattr(self.app, "HWND", None) or getattr(self.app, "Hwnd", None)
            except Exception:
                raw = None
            if isinstance(raw, int) and not isinstance(raw, bool) and raw != 0:
                return raw
            if self.started is not None:
                found = wait_for(lambda: self._get_win().main_window(self.started, win_cls), seconds=10.0)
                if found is not None:
                    return found
            return aw_hwnd if aw_hwnd is not None else raw
        return {"word": lambda: self.app.ActiveWindow.Hwnd, "excel": lambda: self.app.Hwnd,
                "visio": lambda: self.app.WindowHandle32}[self.key]()

    def language(self):
        return self._call_com(self._language_impl)

    def _language_impl(self):
        try:
            return int(self.app.LanguageSettings.LanguageID(2))  # msoLanguageIDUI
        except Exception:  # an app without LanguageSettings: the profile check reports it
            return None

    def close(self, wait=60.0):
        """Close only the documents this tool created, without saving; quit only an instance this tool started that
        holds nothing else; and confirm its process has exited."""
        if not self.owned:
            return
        apt = getattr(self, "_apartment", None)
        try:
            return self._call_com(lambda: self._close_impl(wait), timeout=wait + 10.0 if apt is not None else None)
        except TimeoutError:
            if self.proc is not None:
                self.proc.close()
            raise Refused(f"the {self.exe} instance did not respond while closing") from None
        finally:
            if apt is not None:
                apt.close()

    def _check_powerpoint_only_owned_blank(self, metas):
        for idx, doc in enumerate(list(self.created)):
            if getattr(doc, "closed", False):
                continue
            meta = metas[idx] if idx < len(metas) else None
            if meta is not None and (meta.get("name") is not None or meta.get("full_name") is not None):
                if self._doc_meta(doc) != meta:
                    raise Refused(f"the {self.exe} document this tool created changed identity")
            if not self._is_unmodified_blank_doc(doc):
                raise Refused(f"the {self.exe} document has unsaved changes or a file path")
        doc = None
        total = self.open_documents()
        open_created = [d for d in self.created if not getattr(d, "closed", False)]
        if total != len(open_created):
            return max(1, abs(total - len(open_created)))
        if total == 0:
            return 0
        docs_col = self.documents()
        live = self._enumerate_collection(docs_col, total, self.app)
        post_live = None
        m_doc = None
        try:
            if len(live) != len(open_created):
                return max(1, abs(len(live) - len(open_created)))
            matched_ids = set()
            for idx, created_doc in enumerate(self.created):
                if getattr(created_doc, "closed", False):
                    continue
                meta = metas[idx] if idx < len(metas) else None
                match = None
                for d in live:
                    if id(d) in matched_ids:
                        continue
                    if self._same_doc(d, created_doc):
                        match = d
                        break
                if match is None:
                    return 1
                matched_ids.add(id(match))
                if meta is not None and (meta.get("name") is not None or meta.get("full_name") is not None):
                    if self._doc_meta(match) != meta:
                        raise Refused(f"the {self.exe} document this tool created changed identity")
                if not self._is_unmodified_blank_doc(match):
                    raise Refused(f"the {self.exe} document has unsaved changes or a file path")
            post_total = self.open_documents()
            if post_total != len(open_created):
                return max(1, abs(post_total - len(open_created)))
            post_live = self._enumerate_collection(docs_col, post_total, self.app)
            if len(post_live) != len(open_created):
                return max(1, abs(len(post_live) - len(open_created)))
            post_matched = set()
            for d in post_live:
                if getattr(d, "closed", False):
                    return 1
                m_doc = next(
                    (c for c in open_created if id(c) not in post_matched and self._same_doc(d, c)),
                    None,
                )
                if m_doc is None:
                    return 1
                post_matched.add(id(m_doc))
            self._verify_powerpoint_window_ownership(self.app, post_live)
            return 0
        finally:
            d = None
            m_doc = None
            match = None
            created_doc = None
            live = None
            post_live = None
            docs_col = None
            open_created = None

    def _close_impl(self, wait=60.0):
        others, failure = None, None  # unknown until counted: an instance whose contents are unknown is never quit
        metas = list(getattr(self, "_created_meta", ()))
        try:
            if self.key == "powerpoint":
                others = self._check_powerpoint_only_owned_blank(metas)
            else:
                for idx, doc in enumerate(list(self.created)):
                    if getattr(doc, "closed", False):
                        continue
                    meta = metas[idx] if idx < len(metas) else None
                    if meta is not None and (meta.get("name") is not None or meta.get("full_name") is not None):
                        if self._doc_meta(doc) != meta:
                            raise Refused(f"the {self.exe} document this tool created changed identity")
                    if not self._is_unmodified_blank_doc(doc):
                        raise Refused(f"the {self.exe} document has unsaved changes or a file path")
                    self._close_owned_doc(doc, app=self.app)
                doc = None
                others = self.open_documents()
        except Exception as exc:  # reported below: the instance is left running and the run refuses
            failure = f"{type(exc).__name__}: {exc}"
        finally:
            doc = None
            self._release_marshaled_app()
            if others == 0:
                try:
                    if self.key == "powerpoint":
                        others = self._check_powerpoint_only_owned_blank(metas)
                    else:
                        others = self.open_documents()
                except Exception as exc:
                    others = None
                    failure = f"{type(exc).__name__}: {exc}"
            try:
                if others == 0:
                    if self.key == "powerpoint":
                        import gc
                        self.created, self._created_meta, self.document_refs, self.app = [], [], None, None
                        gc.collect()
                        try:
                            self._post_close_owned_window()
                        except Exception as exc:
                            others = None
                            failure = f"{type(exc).__name__}: {exc}"
                    else:
                        self.app.Quit()
            finally:
                if others == 0:
                    # Excel and PowerPoint stay alive while a COM reference to them is held, so every one is
                    # released before waiting for the process to end.
                    import gc
                    self.created, self._created_meta, self.document_refs, self.app = [], [], None, None
                    gc.collect()
                gone = self.proc is None or (others == 0 and self.proc.exited(wait))
                if self.proc is not None:
                    self.proc.close()
        if others:
            raise Refused(f"the {self.exe} instance holds {others} document(s) this tool did not create, so it was "
                          "left running")
        if others is None:
            raise Refused(f"the {self.exe} instance's documents could not be closed and counted ({failure}), so it "
                          "was left running")
        if not gone:
            raise Refused(f"the {self.exe} instance this tool started did not exit")


def start_process(exe):
    """Start one Office program from the installed build's folder and return its process id."""
    import subprocess
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Office\ClickToRun\Configuration") as key:
        root = winreg.QueryValueEx(key, "InstallationPath")[0]
    child = subprocess.Popen([str(Path(root) / "root" / "Office16" / exe)])
    if exe.upper() == "WINPROJ.EXE":
        win = Win()
        for _ in range(16):
            time.sleep(0.5)
            dlg = win.main_window(child.pid, "#32770")
            if dlg:
                win.user32.PostMessageW(dlg, 0x0100, 0x0D, 0)  # VK_RETURN to dismiss startup separator notice
                win.user32.PostMessageW(dlg, 0x0101, 0x0D, 0)
            if win.main_window(child.pid, "JWinproj-WhimperMainClass"):
                break
    else:
        time.sleep(8)  # the program registers its COM server once it is up
    return child.pid


def wait_for(test, seconds=5.0, step=0.2):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = test()
        if value:
            return value
        time.sleep(step)
    return test()


def popup_items(root, popup_roots=(), label="popup"):
    """The items of the menu or gallery that just opened, once their reading is stable. Office exposes an open menu as
    a Menu element in the app window's own tree (menus nest, so items are taken once each by runtime id)."""
    def read():
        # Word nests an empty Menu shell around the menus that hold the items, so every open Menu is read.
        menus = [e for e in descendants(root, 30) if e.control_type == "Menu"] + list(popup_roots)
        seen, items = set(), []
        for e in (d for menu in menus for d in descendants(menu, 12)):
            if e.control_type in ITEM_TYPES and e.name and e.runtime_id() not in seen:
                seen.add(e.runtime_id())
                items.append(e)
        return items

    def attempt():
        try:
            return read()
        except Gone:
            return None  # the menu is still rebuilding: not a reading yet

    def signature(items):
        return tuple((e.runtime_id(), e.control_type, e.name, getattr(e, "automation_id", "")) for e in items)

    last, last_sig, stable, saw_unstable = None, None, 0, False
    deadline = time.monotonic() + 4.0
    while time.monotonic() < deadline and stable < 2:
        items = attempt()
        if items is None:
            saw_unstable = True
            stable, last, last_sig = 0, None, None
            time.sleep(0.4)
            continue
        sig = signature(items)
        if last_sig is not None and sig == last_sig and items:
            stable += 1
        else:
            if last_sig is not None and sig != last_sig:
                saw_unstable = True
            stable = 0
        last, last_sig = items, sig
        time.sleep(0.4)
    if stable < 2 and (last or saw_unstable):
        raise Refused(f"{label!r} items did not stabilise before timeout")
    return last or []



def capture(args, launched, uia, win):
    row = APPS[args.app][0]
    expected = reference_build(app=row)
    if installed_build() != expected:
        raise Refused(f"the installed build {installed_build()} is not the reference {expected}")
    reported = reported_build(launched.app)
    if reported and not same_build(reported, expected):
        raise Refused(f"{row} reports build {reported}, not the reference {expected}")
    monitor = profile_monitor(win.monitors())
    if monitor:
        win.place(launched.hwnd, monitor)
        time.sleep(2)
    root = uia.element(launched.hwnd)

    def check_licensing():
        current = uia.element(launched.hwnd)
        for candidate in (current,) if current is root else (current, root):
            notice = licensing_problem(candidate)
            if notice:
                raise Refused(notice)

    check_licensing()
    tabs_bar = wait_for(lambda: find(root, lambda e: e.control_type == "Tab" and e.name == "Ribbon Tabs"))
    lower = wait_for(lambda: find(root, lambda e: e.name == "Lower Ribbon"))
    check_licensing()
    if not tabs_bar or not lower:
        raise Refused("the ribbon was not found in the app's window")
    problem = layout_problem(root, args.layout)
    if problem:
        raise Unsafe(problem)
    state = win.state(launched.hwnd)
    ribbon_h = lower.rect[3] - lower.rect[1] if lower.rect else 0
    problems = profile_problems(state, monitor, launched.language(), ribbon_h)
    identifiers = baseline_ids(args.app)
    ctx = Context(args.app, expected, identifiers, origin=None if problems else state["origin"])
    if getattr(args, "shell", False):
        launched.check_alone()
        check_licensing()
        records = build_shell_chrome_records(expected, app_name=args.app)
        measure_origin = ctx.origin if ctx.origin is not None else (0, 0)
        apply_live_shell_measurements(
            records, args.app, root, tabs_bar, lower, measure_origin, expected,
            uia=uia, win=win, launched=launched,
        )
        check_licensing()
        if ctx.origin is not None and not same_geometry(state, win.state(launched.hwnd)):
            ctx.drop_geometry("the window moved or changed size during the capture")
        if ctx.origin is None:
            for rec in records:
                if rec.get("app") != "outlook":
                    for key in ("bounds", "captureProfile", "size"):
                        rec.pop(key, None)
            for why in ctx.dropped_reasons:
                if why not in problems:
                    problems.append(why)
        return records, problems, ctx
    tab_elements = ribbon_tabs(tabs_bar)
    names = [t.name for t in tab_elements]
    wanted = names if args.all_tabs else [args.tab]
    unknown = [w for w in wanted if w not in names]
    if unknown:
        raise Refused(f"no tab named {unknown}; this window's tabs are {names}")
    core = baseline_core_tabs(args.app)
    shown = {t.automation_id for t in tab_elements if t.automation_id}
    ctx.notes.append(f"baseline core tabs not shown in this window: {sorted(core - shown) or 'none'}")
    ctx.notes.append("File (Backstage) is not a ribbon tab; its pages are captured by the app's Backstage section")
    records = []
    for order, tab in enumerate(tab_elements):
        if tab.name not in wanted:
            continue
        launched.check_alone()
        if ctx.origin is not None and not same_geometry(state, win.state(launched.hwnd)):
            ctx.drop_geometry(f"the window moved or changed size before tab {tab.name!r}")
        tab.select()
        lower = lower_for_tab(uia, launched.hwnd, tab.name)
        launched.check_alone()
        check_licensing()
        before_unverified = len(ctx.unverified)
        tab_records = walk_tab(tab, order, lower, ctx)
        if not any(r.get("kind") == "control" for r in tab_records + ctx.unverified[before_unverified:]):
            raise Refused(f"tab {tab.name!r} produced no control records")
        if args.expand:
            tab_records = expand_all(
                tab_records, lower, ctx, launched, uia, win, unverified_start=before_unverified
            )
            check_licensing()
        records += tab_records
    check_licensing()
    if not any(r.get("kind") == "control" for r in records + ctx.unverified):
        raise Refused("no ribbon controls were captured")
    if ctx.origin is not None and not same_geometry(state, win.state(launched.hwnd)):
        ctx.drop_geometry("the window moved or changed size during the capture")
    if ctx.origin is None:
        for rec in records + ctx.unverified:
            for key in ("bounds", "captureProfile", "size"):
                rec.pop(key, None)
        for why in ctx.dropped_reasons:
            if why not in problems:
                problems.append(why)
    return records, problems, ctx


def same_geometry(before, after):
    return all(before[k] == after[k] for k in ("window", "origin", "dpi", "zoomed"))


LICENSING_PHRASES = (
    "unlicensed product",
    "product activation failed",
    "activation required",
    "activate office",
    "reduced functionality",
    "subscription expired",
    "sign in to set up office",
    "most features are disabled",
)


def licensing_problem(root):
    """Why the window shows a licence, activation or reduced-functionality notice, or None."""
    for el in [root] + list(descendants(root)):
        text = (el.name or "").strip()
        lower = text.casefold()
        if any(phrase in lower for phrase in LICENSING_PHRASES):
            return f"the window shows a licence or activation notice ({text!r})"
    return None


def reported_build(app):
    """The build an app reports, as dotted components: Word gives "16.0.20430"; Excel gives the build alone as a
    number (20430) beside Version "16.0"."""
    raw = getattr(app, "Build", "") or ""
    version = str(getattr(app, "Version", "") or "").strip()
    if isinstance(raw, (int, float)) and not isinstance(raw, bool) and float(raw).is_integer():
        raw = int(raw)  # Excel's Build is a number, 20430.0 through COM
    build = str(raw).strip()
    if build.isdigit() and version:
        return f"{version}.{build}"
    return build or version


def layout_problem(root, layout):
    """Why the window cannot be captured as this layout, or None. A Classic capture needs the Simplified Ribbon off."""
    toggle = find(root, lambda e: e.automation_id == "SingleLineRibbonToggle", depth=20)
    if layout == "simplified":
        return "this build offers no Simplified Ribbon switch (SingleLineRibbonToggle not found)" if toggle is None \
            else ("the Simplified Ribbon switch exists here, but driving it is built in D02 T01 §15, the first app "
                  "that offers it; until then no Simplified capture is written")
    if toggle is not None and toggle.toggle_state() == 1:
        return "the ribbon is in its Simplified layout, so a Classic capture would record the wrong layout"
    return None


def first_group_name(root):
    lower = find(root, lambda e: e.name == "Lower Ribbon")
    first = next((c for c in lower.children() if c.control_type == "Group"), None) if lower else None
    return first.name if first else None


def ribbon_tabs(tabs_bar):
    """The TabItem children of Ribbon Tabs once populated and stable across consecutive readings."""
    def attempt():
        try:
            return [t for t in tabs_bar.children() if t.control_type == "TabItem" and t.name]
        except Gone:
            return None

    def signature(items):
        return tuple((t.runtime_id(), t.name, getattr(t, "automation_id", "")) for t in items)

    last, last_sig, stable = None, None, 0
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and stable < 2:
        items = attempt()
        if not items:
            stable, last, last_sig = 0, None, None
            time.sleep(0.2)
            continue
        sig = signature(items)
        if last_sig is not None and sig == last_sig:
            stable += 1
        else:
            stable = 0
        last, last_sig = items, sig
        time.sleep(0.2)
    if not last or stable < 2:
        raise Refused("the ribbon tabs did not populate or stabilise in the app's window")
    return last


def lower_for_tab(uia, hwnd, tab_name):
    """The Lower Ribbon element for tab_name once its groups and controls are populated and stable."""
    def attempt():
        try:
            root = uia.element(hwnd)
            if first_group_name(root) != tab_name:
                return None
            lower = find(root, lambda e: e.name == "Lower Ribbon")
            if not lower:
                return None
            containers = [c for c in lower.children() if c.control_type == "Group"]
            groups = [g for c in containers for g in c.children() if g.control_type == "Group"]
            if not groups:
                return None
            sig = []
            snapshot = []
            total_controls = 0
            for g in groups:
                members = []
                member_sig = []
                for el, frame in controls_of(g):
                    ct = control_type(el, use_cached=False)
                    if not ct:
                        continue
                    el._validated_control_type = ct
                    if el.control_type == "SplitButton":
                        parts = list(el.children())
                        el._validated_children = parts
                    else:
                        parts = ()
                    members.append((el, frame))
                    member_sig.append((
                        el.runtime_id(), el.control_type, ct, el.name, getattr(el, "automation_id", ""),
                        tuple((p.runtime_id(), getattr(p, "automation_id", "")) for p in parts),
                    ))
                total_controls += len(members)
                snapshot.append((g, members))
                sig.append((g.runtime_id(), g.name, getattr(g, "automation_id", ""), tuple(member_sig)))
            if total_controls == 0:
                return None
            lower._validated_groups = snapshot
            return lower, tuple(sig)
        except Gone:
            return None

    last_lower, last_sig, stable = None, None, 0
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and stable < 2:
        res = attempt()
        if res is None:
            stable, last_lower, last_sig = 0, None, None
            time.sleep(0.2)
            continue
        lower, sig = res
        if last_sig is not None and sig == last_sig:
            stable += 1
        else:
            stable = 0
        last_lower, last_sig = lower, sig
        time.sleep(0.2)
    if last_lower is None or stable < 2:
        try:
            notice = licensing_problem(uia.element(hwnd))
        except Gone:
            notice = None
        if notice:
            raise Refused(notice)
        raise Refused(f"tab {tab_name!r} did not open or its controls did not stabilise")
    return last_lower


def expand_all(records, lower, ctx, launched, uia, win, unverified_start=None):
    """Open every control that can expand (by its own pattern) once, record its items, and close it again."""
    combos = 0

    def expand_list(batch):
        nonlocal combos
        out = []
        for rec in batch:
            out.append(rec)
            element = ctx.elements.get(rec["id"])
            if rec.get("kind") != "control" or element is None:
                continue
            target = next((p for p in element.children() if p.automation_id.endswith("_Dropdown")), element) \
                if element.control_type == "SplitButton" else element
            if target.expand_state() is None:
                continue
            if rec.get("controlType") == "comboBox":
                combos += 1  # fonts, sizes: the machine's and the document's data, not the app's interface
                continue
            launched.check_alone()
            before = win.popups(launched.proc.pid)
            target.expand()
            try:
                time.sleep(0.3)
                opened = [h for h in win.popups(launched.proc.pid) if h not in before]
                items = popup_items(uia.element(launched.hwnd), [uia.element(h) for h in opened], label=rec["label"])
                if not items:
                    ctx.notes.append(f"{rec['label']!r} opened but no item was read from it")
            finally:
                close_popup(target, lambda: [h for h in win.popups(launched.proc.pid) if h not in before]
                            or find(uia.element(launched.hwnd), lambda e: e.control_type == "Menu", depth=30) is not None,
                            rec["label"], check_alone=launched.check_alone)
            out += expand_items(rec, target, items, ctx)
        return out

    out = expand_list(records)
    if unverified_start is not None and len(ctx.unverified) > unverified_start:
        ctx.unverified[unverified_start:] = expand_list(ctx.unverified[unverified_start:])
    if combos:
        ctx.notes.append(f"{combos} combo box list(s) on this tab not expanded (system or document data)")
    return out


def close_popup(target, still_open, label, attempts=3, check_alone=None):
    """Collapse a menu and confirm its popup is gone. The control's own expand state is not trusted: Word reports
    some drop-downs collapsed while open and others expanded while closed, so "gone" means no popup window and no
    open menu remain. A drop-down that ignores Collapse closes when opened and collapsed again; one that stays open
    stops the capture rather than leaving it behind."""
    if check_alone is not None:
        check_alone()
    target.collapse()
    for _ in range(attempts):
        if wait_for(lambda: not still_open(), 1.5):
            return
        if check_alone is not None:
            check_alone()
        target.expand()
        time.sleep(0.4)
        if check_alone is not None:
            check_alone()
        target.collapse()
    raise Refused(f"{label!r} did not close after being opened")


def baseline_core_tabs(app):
    data = json.loads((INVENTORY / app / "baseline.json").read_text(encoding="utf-8"))
    c = data["columns"]
    return {r[c.index("idMso")] for r in data["rows"]
            if r[c.index("controlType")] == "tab" and r[c.index("placement")] == "coreTab" and r[c.index("idMso")]}


def baseline_ids(app):
    data = json.loads((INVENTORY / app / "baseline.json").read_text(encoding="utf-8"))
    col = data["columns"].index("idMso")
    return {r[col] for r in data["rows"] if r[col]}


class Proxy:
    """The launched app as the worker process sees it: its window, its process id and the object-model facts the
    parent read, with every later object-model check asked of the parent."""

    def __init__(self, spec, ask):
        self.hwnd, self._language, self.ask = spec["hwnd"], spec["language"], ask
        self.proc = type("Pid", (), {"pid": spec["pid"]})()
        self.app = type("App", (), {"Build": spec["build"], "Version": ""})()

    def language(self):
        return self._language

    def check_alone(self):
        answer = self.ask("check_alone")
        if answer != "ok":
            raise Refused(answer)


def converse(lines, reply, launched):
    """Serve a worker's requests until it reports its outcome; returns that outcome message."""
    for line in lines:
        message = json.loads(line)
        if message.get("ask") == "check_alone":
            try:
                launched.check_alone()
                reply("ok")
            except Refused as exc:
                reply(str(exc))
            continue
        return message
    return {"refused": "the capture worker ended without reporting an outcome"}


def capture_in_worker(args, launched, timeout=3600, worker_cmd=None):
    """Run capture() in a child process and return its records, profile problems and notes."""
    import queue
    import subprocess
    import threading
    import types
    deadline = time.monotonic() + timeout
    own_apt = getattr(launched, "_apartment", None)
    apt = own_apt or _Apartment(daemon=True)
    try:
        try:
            build_str, lang_id = apt.call(
                lambda: (reported_build(launched.app), launched.language()),
                timeout=max(0.01, deadline - time.monotonic()),
            )
        except TimeoutError:
            raise Refused(f"the capture worker timed out after {timeout}s") from None
        spec = {"args": vars(args), "hwnd": int(launched.hwnd), "pid": int(launched.proc.pid),
                "build": build_str, "language": lang_id}
        cmd = worker_cmd or [sys.executable, str(Path(__file__).resolve()), "--worker"]
        child = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True, encoding="utf-8")
        q = queue.Queue()

        def reader():
            try:
                for line in iter(child.stdout.readline, ""):
                    q.put(line)
            finally:
                q.put(None)

        threading.Thread(target=reader, daemon=True).start()

        def timed_lines():
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise Refused(f"the capture worker timed out after {timeout}s")
                try:
                    line = q.get(timeout=min(remaining, 0.2))
                except queue.Empty:
                    continue
                if line is None:
                    return
                yield line

        err_lines = []
        try:
            child.stdin.write(json.dumps(spec) + "\n")
            child.stdin.flush()

            def reply(text):
                child.stdin.write(json.dumps({"answer": text}) + "\n")
                child.stdin.flush()

            def timed_check_alone(_self=None):
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError(f"the capture worker timed out after {timeout}s")
                try:
                    apt.call(launched.check_alone, timeout=remaining)
                except TimeoutError:
                    raise TimeoutError(f"the capture worker timed out after {timeout}s") from None

            timed_launched = types.SimpleNamespace(check_alone=timed_check_alone)
            try:
                outcome = converse(timed_lines(), reply, timed_launched)
            except TimeoutError as exc:
                raise Refused(str(exc)) from None
            remaining = max(0.0, deadline - time.monotonic())
            try:
                child.wait(timeout=min(60.0, remaining))
            except subprocess.TimeoutExpired:
                raise Refused(f"the capture worker timed out after {timeout}s") from None
            if "refused" in outcome and child.stderr:
                err_lines = child.stderr.read().strip().splitlines()[-1:]
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
            for pipe in (child.stdin, child.stdout, child.stderr):
                if pipe is not None:
                    try:
                        pipe.close()
                    except OSError:
                        pass
    finally:
        if own_apt is None:
            apt.close(join_timeout=0)
    if "unsafe" in outcome:
        raise Unsafe(outcome["unsafe"])
    if "refused" in outcome:
        raise Refused(outcome["refused"] + (f" ({err_lines[0]})" if err_lines else ""))
    result = outcome["result"]
    ctx = types.SimpleNamespace(skipped=result["skipped"], notes=result["notes"], unverified=result["unverified"])
    return result["records"], result["problems"], ctx


def worker():
    """The child side: read the spec, capture, and report the outcome as one JSON line on standard output."""
    spec = json.loads(sys.stdin.readline())

    def ask(question):
        print(json.dumps({"ask": question}), flush=True)
        return json.loads(sys.stdin.readline())["answer"]

    args = argparse.Namespace(**spec["args"])
    try:
        records, problems, ctx = capture(args, Proxy(spec, ask), Uia(), Win())
    except Unsafe as exc:
        print(json.dumps({"unsafe": str(exc)}), flush=True)
        return 2
    except Gone as exc:
        print(json.dumps({"refused": f"an element vanished while it was read: {exc}"}), flush=True)
        return 1
    except Refused as exc:
        print(json.dumps({"refused": str(exc)}), flush=True)
        return 1
    print(json.dumps({"result": {"records": records, "problems": problems, "skipped": ctx.skipped,
                                 "notes": ctx.notes, "unverified": ctx.unverified}}), flush=True)
    return 0


def _load_existing_records(path, raw):
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Refused(f"{path} is not valid UTF-8 JSON ({exc})") from None
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise Refused(f"{path} does not hold a JSON list of record objects")
    return data


REQUIRED_SHELL_IDS = (
    "shell.region.titlebar",
    "shell.region.tabrow",
    "shell.region.ribbon",
    "shell.region.messageBar",
    "shell.region.documentArea",
    "shell.region.taskPaneDock",
    "shell.region.statusbar",
    "shell.titlebar.systemMenu",
    "shell.titlebar.qat",
    "shell.titlebar.autosave",
    "shell.titlebar.documentTitle",
    "shell.titlebar.caption",
    "shell.titlebar.search",
    "shell.titlebar.account",
    "shell.titlebar.minimize",
    "shell.titlebar.maximize",
    "shell.titlebar.close",
    "shell.qat.autosave",
    "shell.qat.save",
    "shell.qat.undo",
    "shell.qat.undo.dropdown",
    "shell.qat.redo",
    "shell.qat.customize",
    "shell.qat.customize.automatically-save",
    "shell.qat.customize.new",
    "shell.qat.customize.open",
    "shell.qat.customize.save",
    "shell.qat.customize.email",
    "shell.qat.customize.quick-print",
    "shell.qat.customize.print-preview-and-print",
    "shell.qat.customize.editor-f7",
    "shell.qat.customize.read-aloud",
    "shell.qat.customize.undo",
    "shell.qat.customize.redo",
    "shell.qat.customize.draw-table",
    "shell.qat.customize.touch-mouse-mode",
    "shell.qat.customize.more-commands",
    "shell.qat.customize.show-below-the-ribbon",
    "shell.qat.customize.hide-quick-access-toolbar",
    "shell.tabrow.file",
    "shell.tabrow.tabs",
    "shell.tabrow.comments",
    "shell.tabrow.editingMode",
    "shell.tabrow.editingMode.editing",
    "shell.tabrow.editingMode.reviewing",
    "shell.tabrow.editingMode.viewing",
    "shell.tabrow.share",
    "shell.tabrow.share.share",
    "shell.tabrow.share.copy-link",
    "shell.tabrow.share.manage-access",
    "shell.ribbonDisplay.button",
    "shell.ribbonDisplay.full-screen-mode",
    "shell.ribbonDisplay.show-tabs-only",
    "shell.ribbonDisplay.always-show-ribbon",
    "shell.ribbonDisplay.hide-quick-access-toolbar",
    "shell.search.input",
    "shell.search.voice",
    "shell.search.flyout",
    "shell.search.recentActions",
    "shell.search.suggestedActions",
    "shell.search.suggestedActions.spelling-and-grammar",
    "shell.search.suggestedActions.word-count",
    "shell.search.suggestedActions.print",
    "shell.search.people",
    "shell.search.actions",
    "shell.search.findInDocument",
    "shell.search.files",
    "shell.search.help",
    "shell.keytips.layer",
    "shell.keytips.autosave",
    "shell.keytips.save",
    "shell.keytips.undo",
    "shell.keytips.redo",
    "shell.keytips.documentTitle",
    "shell.keytips.search",
    "shell.keytips.account",
    "shell.keytips.file",
    "shell.keytips.comments",
    "shell.keytips.editingMode",
    "shell.keytips.share",
    "shell.backstage.frame",
    "shell.backstage.titlebar",
    "shell.backstage.navBar",
    "shell.backstage.navList",
    "shell.backstage.back",
    "shell.backstage.contentPane",
    "shell.statusbar.bar",
    "shell.statusbar.leftZone",
    "shell.statusbar.rightZone",
    "shell.statusbar.displaySettings",
    "shell.statusbar.viewSwitcher",
    "shell.statusbar.zoomOut",
    "shell.statusbar.zoomSlider",
    "shell.statusbar.zoomIn",
    "shell.statusbar.zoomPercent",
    "shell.statusbar.customizeMenu",
)

REQUIRED_SHELL_IDENTIFIERS = {
    "shell.titlebar.systemMenu": ("uiaId", "MenuBar"),
    "shell.titlebar.autosave": ("idMso", "AutoSaveSwitch"),
    "shell.titlebar.search": ("uiaId", "TellMeControlAnchor"),
    "shell.titlebar.account": ("uiaId", "MeControlWidget"),
    "shell.qat.autosave": ("idMso", "AutoSaveSwitch"),
    "shell.qat.save": ("idMso", "FileSave"),
    "shell.qat.undo": ("idMso", "Undo"),
    "shell.qat.undo.dropdown": ("uiaId", "Undo_Dropdown"),
    "shell.qat.redo": ("idMso", "RedoOrRepeat"),
    "shell.tabrow.file": ("uiaId", "FileTabButton"),
    "shell.search.input": ("uiaId", "TellMeTextBoxAutomationId"),
    "shell.backstage.navBar": ("uiaId", "OutSpaceNavBar"),
    "shell.backstage.navList": ("uiaId", "NavBarMenu"),
    "shell.backstage.back": ("uiaId", "FileTabButton"),
    "shell.backstage.contentPane": ("uiaId", "BackstageView"),
    "excel.shell.qat.redo": ("idMso", "Redo"),
    "powerpoint.shell.qat.fromBeginning": ("idMso", "SlideShowFromBeginning"),
    "project.shell.qat.save": ("idMso", "FileSave"),
    "project.shell.qat.undo": ("idMso", "Undo"),
    "project.shell.qat.redo": ("idMso", "Redo"),
    "project.shell.tabrow.search": ("uiaId", "TellMeControlAnchor"),
    "outlook.explorer.shell.qat.sendReceiveAll": ("idMso", "SendReceiveAll"),
    "outlook.explorer.shell.qat.singleLineRibbonToggle": ("idMso", "SingleLineRibbonToggle"),
    "outlook.explorer.shell.qat.minimizeRibbon": ("idMso", "MinimizeRibbon"),
    "outlook.explorer.shell.qat.findContactCombo": ("idMso", "FindContactCombo"),
    "outlook.compose.shell.qat.save": ("idMso", "FileSave"),
    "outlook.compose.shell.qat.redo": ("idMso", "RedoOrRepeat"),
    "outlook.compose.shell.qat.singleLineRibbonToggle": ("idMso", "SingleLineRibbonToggle"),
    "outlook.compose.shell.qat.minimizeRibbon": ("idMso", "MinimizeRibbon"),
}


def _can_inherit_shared_children(ovr_rec, shared_rec):
    if shared_rec is None:
        return False
    if ovr_rec.get("kind") != shared_rec.get("kind"):
        return False
    if ovr_rec.get("controlType") != shared_rec.get("controlType"):
        return False
    if ovr_rec.get("controlType") in (
        "button", "toggleButton", "checkBox", "editBox", "label", "slider", "spinner", "dialogLauncher"
    ):
        return False
    return True


def effective_shell(records, app, window=None):
    """Resolve the effective shell record list for `app` (and `window` for Outlook: 'explorer' or 'compose').

    Rules:
    1. Start from all shared `shell.*` records (`r["app"] == "shell"`).
    2. Select the override prefix `<prefix>` (`word.shell.`, `excel.shell.`, `powerpoint.shell.`, `visio.shell.`,
       `project.shell.`, or `outlook.<window>.shell.` where `window` defaults to `'explorer'` for Outlook).
    3. Every override record `<prefix><path>` corresponds to shared id `shell.<path>`.
    4. If an override record `<prefix><container>` has direct override children (`r["parent"] == "<prefix><container>"`),
       it is a container override: the shared container's direct children (`r["parent"] == "shell.<container>"`) are
       replaced by those override children, and the entire descendant subtree of any excluded shared child (such as
       `shell.tabrow.editingMode`'s mode items in Excel or `shell.qat.customize`'s menu items when not overridden) is
       recursively pruned unless explicitly overridden under `<prefix>`.
    5. A leaf override `<prefix><leaf>` inside a non-overridden container replaces `shell.<leaf>` if present (and any
       shared children under `shell.<leaf>` have their `parent` remapped to `<prefix><leaf>` only when `<prefix><leaf>`
       has the same `kind` and compatible container `controlType` and defines no override children of its own) or
       appends to the container if new.
    6. `shell.keytips.layer` is a root overlay region retained in every app; each KeyTip badge child is retained (or
       replaced by `<prefix>keytips.<name>`) if and only if its corresponding target control on the title bar, QAT or
       tab row is present in the resolved shell.
    7. Every retained record's `parent` is remapped to the active container id in the resolved graph so no record has
       an orphaned `parent`.
    """
    if app not in APPS and app != "shell":
        raise ValueError(f"unknown app {app!r}")
    shared = [dict(r) for r in records if r.get("app") == "shell" and str(r.get("id", "")).startswith("shell.")]
    if app in ("shell", "word"):
        if window is not None:
            raise ValueError(f"window context {window!r} is only valid for outlook, not {app!r}")
        return shared
    if app == "outlook":
        win_ctx = window or "explorer"
        if win_ctx not in ("explorer", "compose"):
            raise ValueError(f"unknown Outlook window context {win_ctx!r}; expected 'explorer' or 'compose'")
        prefix = f"outlook.{win_ctx}.shell."
    else:
        if window is not None:
            raise ValueError(f"window context {window!r} is only valid for outlook, not {app!r}")
        prefix = f"{app}.shell."

    overrides = [dict(r) for r in records if r.get("app") == app and str(r.get("id", "")).startswith(prefix)]
    if not overrides:
        return shared

    def to_shared_id(oid):
        if isinstance(oid, str) and oid.startswith(prefix):
            return "shell." + oid[len(prefix):]
        return oid

    ovr_by_shared = {to_shared_id(r["id"]): r for r in overrides}
    ovr_children_of = {}
    for r in overrides:
        parent = r.get("parent")
        if parent:
            ovr_children_of.setdefault(to_shared_id(parent), []).append(r)

    shared_by_id = {r["id"]: r for r in shared}
    shared_children_of = {}
    for r in shared:
        parent = r.get("parent")
        if parent:
            shared_children_of.setdefault(parent, []).append(r)

    overridden_containers = {
        sid for sid in ovr_by_shared
        if sid != "shell.keytips.layer" and sid in ovr_children_of and len(ovr_children_of[sid]) > 0
    }
    excluded_shared_ids = set()
    for cid in overridden_containers:
        ovr_child_sids = {to_shared_id(c["id"]) for c in ovr_children_of.get(cid, ())}
        for shared_child in shared_children_of.get(cid, ()):
            if shared_child["id"] not in ovr_child_sids:
                excluded_shared_ids.add(shared_child["id"])

    resolved = []
    active_id_for_shared = {}

    def emit_record(rec, parent_shared_id):
        out = dict(rec)
        if parent_shared_id is not None:
            out["parent"] = active_id_for_shared.get(parent_shared_id, parent_shared_id)
        resolved.append(out)

    def walk_shared(sid, parent_sid):
        if sid in excluded_shared_ids:
            return
        ovr = ovr_by_shared.get(sid)
        chosen = ovr if ovr is not None else shared_by_id[sid]
        active_id_for_shared[sid] = chosen["id"]
        emit_record(chosen, parent_sid)
        if sid in overridden_containers:
            for child_ovr in ovr_children_of.get(sid, ()):
                child_sid = to_shared_id(child_ovr["id"])
                walk_override_subtree(child_ovr, child_sid, sid)
        else:
            if ovr is None or _can_inherit_shared_children(ovr, shared_by_id.get(sid)):
                for child_shared in shared_children_of.get(sid, ()):
                    if child_shared["id"] in excluded_shared_ids:
                        continue
                    walk_shared(child_shared["id"], sid)
            for child_ovr in ovr_children_of.get(sid, ()):
                child_sid = to_shared_id(child_ovr["id"])
                if child_sid not in shared_by_id:
                    walk_override_subtree(child_ovr, child_sid, sid)

    def walk_override_subtree(ovr_rec, sid, parent_sid):
        active_id_for_shared[sid] = ovr_rec["id"]
        emit_record(ovr_rec, parent_sid)
        if sid in overridden_containers:
            for child_ovr in ovr_children_of.get(sid, ()):
                child_sid = to_shared_id(child_ovr["id"])
                walk_override_subtree(child_ovr, child_sid, sid)
        else:
            if _can_inherit_shared_children(ovr_rec, shared_by_id.get(sid)):
                for child_shared in shared_children_of.get(sid, ()):
                    if child_shared["id"] in excluded_shared_ids:
                        continue
                    walk_shared(child_shared["id"], sid)
            for child_ovr in ovr_children_of.get(sid, ()):
                child_sid = to_shared_id(child_ovr["id"])
                if child_sid not in shared_by_id:
                    walk_override_subtree(child_ovr, child_sid, sid)

    roots = [r for r in shared if not r.get("parent") and r["id"] != "shell.keytips.layer"]
    for root in roots:
        walk_shared(root["id"], None)
    for ovr in overrides:
        sid = to_shared_id(ovr["id"])
        if not ovr.get("parent") and sid != "shell.keytips.layer" and sid not in active_id_for_shared:
            walk_override_subtree(ovr, sid, None)

    # Resolve KeyTips layer based on the controls active in the resolved title bar, QAT and tab row.
    if "shell.keytips.layer" in shared_by_id:
        active_targets = set()
        for r in resolved:
            sid = to_shared_id(r["id"])
            for seg in ("shell.titlebar.", "shell.qat.", "shell.tabrow."):
                if sid.startswith(seg):
                    tail = sid[len(seg):]
                    if "." not in tail:
                        active_targets.add(tail)
        layer_rec = ovr_by_shared.get("shell.keytips.layer", shared_by_id["shell.keytips.layer"])
        active_id_for_shared["shell.keytips.layer"] = layer_rec["id"]
        emit_record(layer_rec, None)
        emitted_kt_sids = set()
        for kt_shared in shared_children_of.get("shell.keytips.layer", ()):
            kt_sid = kt_shared["id"]
            target_name = kt_sid.split(".")[-1]
            if target_name not in active_targets:
                continue
            chosen_kt = ovr_by_shared.get(kt_sid, kt_shared)
            active_id_for_shared[kt_sid] = chosen_kt["id"]
            emit_record(chosen_kt, "shell.keytips.layer")
            emitted_kt_sids.add(kt_sid)
        for kt_ovr in ovr_children_of.get("shell.keytips.layer", ()):
            kt_sid = to_shared_id(kt_ovr["id"])
            if kt_sid in emitted_kt_sids:
                continue
            target_name = kt_sid.split(".")[-1]
            if target_name in active_targets:
                active_id_for_shared[kt_sid] = kt_ovr["id"]
                emit_record(kt_ovr, "shell.keytips.layer")
                emitted_kt_sids.add(kt_sid)

    return resolved


def validate_shell_chrome(records):
    """Validate `design/inventory/shell/chrome.json` records, geometry, identifiers and per-app effective shells."""
    if not isinstance(records, list) or len(records) < 110:
        raise Refused(f"shell chrome inventory holds {len(records) if isinstance(records, list) else 0} records; "
                      "expected at least 110")
    by_id = {}
    for rec in records:
        if not isinstance(rec, dict) or not isinstance(rec.get("id"), str):
            raise Refused("shell chrome inventory contains a malformed record without a string id")
        rid = rec["id"]
        if rid in by_id:
            raise Refused(f"duplicate shell record id {rid!r}")
        by_id[rid] = rec
        if not isinstance(rec.get("label"), str) or not rec["label"].strip():
            raise Refused(f"shell record {rid!r} is missing a non-blank string label")
        if not isinstance(rec.get("behaviour"), str) or not rec["behaviour"].strip():
            raise Refused(f"shell record {rid!r} is missing a non-blank behaviour sentence")
        if not isinstance(rec.get("source"), str) or not rec["source"].strip():
            raise Refused(f"shell record {rid!r} is missing source")
        if _NO_CONTROL_RE.search(rec["label"]):
            raise Refused(f"shell record {rid!r} label contains control or bidi characters")
        if _EMAIL_RE.search(rec["label"]) or _EMAIL_RE.search(rec["behaviour"]):
            raise Refused(f"shell record {rid!r} contains an unsanitised email address")

    spec_by_id = {item["id"]: item for item in _SHELL_SPEC}
    missing = [rid for rid in REQUIRED_SHELL_IDS if rid not in by_id] + [
        rid for rid in spec_by_id if rid not in by_id and rid not in REQUIRED_SHELL_IDS
    ]
    if missing:
        raise Refused(f"shell chrome inventory is missing required records: {missing}")

    for rid, rec in by_id.items():
        spec = spec_by_id.get(rid)
        if spec is not None:
            for field in ("kind", "controlType", "app", "window", "parent", "keytip", "idMso", "uiaId"):
                if rec.get(field) != spec.get(field):
                    raise Refused(
                        f"shell record {rid!r} has {field}={rec.get(field)!r}, expected {spec.get(field)!r}"
                    )

    for rid, (field, expected_val) in REQUIRED_SHELL_IDENTIFIERS.items():
        rec = by_id.get(rid)
        if rec is None:
            raise Refused(f"shell chrome inventory is missing required record {rid!r}")
        if rec.get(field) != expected_val:
            raise Refused(f"shell record {rid!r} has {field}={rec.get(field)!r}, expected {expected_val!r}")

    for rec in records:
        rid = rec["id"]
        app = rec.get("app")
        parent = rec.get("parent")
        if parent and parent not in by_id:
            raise Refused(f"shell record {rid!r} has orphan parent {parent!r}")
        if app in ("shell", "excel", "powerpoint", "visio", "project"):
            source = str(rec.get("source", ""))
            if not source.startswith("uia:"):
                raise Refused(f"live-captured shell record {rid!r} has source {source!r}, expected uia:<build>")
            if rec.get("captureProfile") != PROFILE:
                raise Refused(f"live-captured shell record {rid!r} is missing captureProfile {PROFILE!r}")
            bounds = rec.get("bounds")
            if not isinstance(bounds, dict) or bounds.get("width", 0) <= 0 or bounds.get("height", 0) <= 0:
                raise Refused(f"live-captured shell record {rid!r} is missing positive bounds")
        elif app == "outlook":
            source = str(rec.get("source", ""))
            if not (source.startswith("baseline:") or source.startswith("uia:")):
                raise Refused(f"outlook shell record {rid!r} has invalid source {source!r}")

    # Verify effective_shell resolution and invariants across all apps and Outlook window contexts.
    leaf_control_types = (
        "button", "toggleButton", "checkBox", "editBox", "label", "slider", "spinner", "dialogLauncher"
    )
    required_titlebar_tails = ("systemMenu", "qat", "caption", "account", "minimize", "maximize", "close")
    contexts = [
        ("word", None),
        ("excel", None),
        ("powerpoint", None),
        ("visio", None),
        ("project", None),
        ("outlook", "explorer"),
        ("outlook", "compose"),
    ]
    for app, win_ctx in contexts:
        eff = effective_shell(records, app, window=win_ctx)
        eff_by_id = {r["id"]: r for r in eff}
        children_count = {}
        for r in eff:
            p = r.get("parent")
            if p:
                if p not in eff_by_id:
                    raise Refused(f"effective_shell({app!r}, {win_ctx!r}) left orphan parent {p!r} on {r['id']!r}")
                children_count[p] = children_count.get(p, 0) + 1
        for r in eff:
            if r.get("kind") == "control" and r.get("controlType") in leaf_control_types:
                if children_count.get(r["id"], 0) > 0:
                    raise Refused(
                        f"effective_shell({app!r}, {win_ctx!r}) attached child records under non-container "
                        f"{r.get('controlType')} {r['id']!r}"
                    )
        # Every resolved shell must retain full title bar controls and an active KeyTips layer.
        for tail in required_titlebar_tails:
            if not any(rid.endswith(f".titlebar.{tail}") for rid in eff_by_id):
                raise Refused(f"effective_shell({app!r}, {win_ctx!r}) is missing titlebar.{tail}")
        if not any(rid.endswith(".titlebar.search") or rid.endswith(".tabrow.search") for rid in eff_by_id):
            raise Refused(f"effective_shell({app!r}, {win_ctx!r}) is missing search")
        kt_layers = [rid for rid in eff_by_id if rid == "shell.keytips.layer" or rid.endswith(".shell.keytips.layer")]
        if not kt_layers or children_count.get(kt_layers[0], 0) < 5:
            raise Refused(f"effective_shell({app!r}, {win_ctx!r}) is missing KeyTips layer or its active badges")
        if app != "outlook":
            # Verify that search and QAT customize controls retain their descendant subtrees and that every inline
            # child record's bounds lies inside its parent's bounds.
            search_anchors = [
                rid for rid in eff_by_id if rid.endswith(".titlebar.search") or rid.endswith(".tabrow.search")
            ]
            if not search_anchors or children_count.get(search_anchors[0], 0) < 2:
                raise Refused(f"effective_shell({app!r}) search control {search_anchors!r} is missing its children")
            qat_cust = [rid for rid in eff_by_id if rid.endswith(".qat.customize")]
            if not qat_cust or children_count.get(qat_cust[0], 0) < 10:
                raise Refused(f"effective_shell({app!r}) QAT customize control {qat_cust!r} is missing its menu items")
            for r in eff:
                p = eff_by_id.get(r.get("parent"))
                if not p or "bounds" not in r or "bounds" not in p:
                    continue
                if r["id"].endswith(".customizeMenu"):
                    continue
                if ".keytips." in r["id"] and not r["id"].endswith(".layer"):
                    rb = r["bounds"]
                    if rb["width"] > 36 or rb["height"] > 24:
                        raise Refused(
                            f"effective_shell({app!r}) KeyTip badge {r['id']!r} bounds {rb} exceeds badge dimensions"
                        )
                    target_tail = "." + r["id"].split(".")[-1]
                    targets = [
                        t for t in eff
                        if t["id"].endswith(target_tail)
                        and ".keytips." not in t["id"]
                        and t.get("kind") != "menuItem"
                        and "bounds" in t
                    ]
                    if targets:
                        tb = targets[0]["bounds"]
                        if (
                            rb == tb
                            or rb["x"] > tb["x"] + tb["width"]
                            or rb["x"] + rb["width"] < tb["x"]
                            or rb["y"] > tb["y"] + tb["height"]
                            or rb["y"] + rb["height"] < tb["y"]
                        ):
                            raise Refused(
                                f"effective_shell({app!r}) KeyTip badge {r['id']!r} bounds {rb} is not a badge "
                                f"overlay on target {targets[0]['id']!r} bounds {tb}"
                            )
                if r.get("kind") == "menuItem" or r["id"].endswith(".flyout"):
                    rb, pb = r["bounds"], p["bounds"]
                    if not (
                        rb["x"] <= pb["x"] + pb["width"]
                        and rb["x"] + rb["width"] >= pb["x"]
                        and rb["y"] >= pb["y"]
                    ):
                        raise Refused(
                            f"effective_shell({app!r}) menu surface item {r['id']!r} bounds {rb} is not aligned "
                            f"with parent {p['id']!r} bounds {pb}"
                        )
                    continue
                container = p
                if (
                    r.get("app") != p.get("app")
                    and p.get("kind") == "region"
                    and p.get("parent") in eff_by_id
                    and "bounds" in eff_by_id[p["parent"]]
                ):
                    container = eff_by_id[p["parent"]]
                rb, pb = r["bounds"], container["bounds"]
                if not (
                    rb["x"] >= pb["x"]
                    and rb["y"] >= pb["y"]
                    and rb["x"] + rb["width"] <= pb["x"] + pb["width"]
                    and rb["y"] + rb["height"] <= pb["y"] + pb["height"]
                ):
                    raise Refused(
                        f"effective_shell({app!r}) inline child {r['id']!r} bounds {rb} falls outside "
                        f"parent {container['id']!r} bounds {pb}"
                    )

    word_ids = {r["id"] for r in effective_shell(records, "word")}
    if "shell.tabrow.editingMode" not in word_ids or "shell.tabrow.editingMode.editing" not in word_ids:
        raise Refused("Word effective shell is missing editingMode or its child items")
    if "shell.titlebar.autosave" not in word_ids or "shell.qat.autosave" not in word_ids:
        raise Refused("Word effective shell is missing autosave")

    excel_ids = {r["id"] for r in effective_shell(records, "excel")}
    if any("editingMode" in rid for rid in excel_ids):
        raise Refused("Excel effective shell must exclude editingMode and its mode items")
    if "excel.shell.qat.redo" not in excel_ids or "shell.qat.redo" in excel_ids:
        raise Refused("Excel effective shell must replace shell.qat.redo with excel.shell.qat.redo")

    ppt_ids = {r["id"] for r in effective_shell(records, "powerpoint")}
    if "powerpoint.shell.qat.fromBeginning" not in ppt_ids or "powerpoint.shell.tabrow.presentInTeams" not in ppt_ids:
        raise Refused("PowerPoint effective shell is missing fromBeginning or presentInTeams")
    if any("editingMode" in rid for rid in ppt_ids):
        raise Refused("PowerPoint effective shell must exclude editingMode and its mode items")

    visio_ids = {r["id"] for r in effective_shell(records, "visio")}
    if "shell.titlebar.autosave" in visio_ids or "shell.qat.autosave" in visio_ids:
        raise Refused("Visio effective shell must exclude autosave")
    if "visio.shell.tabrow.closeDocument" not in visio_ids:
        raise Refused("Visio effective shell is missing closeDocument")
    if any(rid.startswith("shell.tabrow.share.") for rid in visio_ids):
        raise Refused("Visio effective shell must prune menu items under direct button visio.shell.tabrow.share")

    proj_ids = {r["id"] for r in effective_shell(records, "project")}
    if "shell.titlebar.autosave" in proj_ids or "shell.qat.autosave" in proj_ids:
        raise Refused("Project effective shell must exclude autosave")
    if "project.shell.tabrow.search" not in proj_ids or "shell.titlebar.search" in proj_ids:
        raise Refused("Project effective shell must move search from the title bar to the tab row")

    ol_exp_ids = {r["id"] for r in effective_shell(records, "outlook", window="explorer")}
    ol_cmp_ids = {r["id"] for r in effective_shell(records, "outlook", window="compose")}
    if "outlook.explorer.shell.qat.sendReceiveAll" not in ol_exp_ids:
        raise Refused("Outlook explorer effective shell is missing sendReceiveAll")
    if "outlook.compose.shell.qat.save" in ol_exp_ids:
        raise Refused("Outlook explorer effective shell must exclude compose-only save")
    if "outlook.compose.shell.qat.save" not in ol_cmp_ids:
        raise Refused("Outlook compose effective shell is missing save")
    if "outlook.explorer.shell.qat.sendReceiveAll" in ol_cmp_ids:
        raise Refused("Outlook compose effective shell must exclude explorer-only sendReceiveAll")
    return True


_SHELL_SPEC = (
    {'id': 'shell.region.titlebar', 'app': 'shell', 'kind': 'region', 'label': 'Title Bar', 'behaviour': 'Spans the top 48 pixels of the maximised window frame, hosting the system menu, Quick Access Toolbar, document title, search box, account widget and window caption buttons.', 'order': 0},
    {'id': 'shell.region.tabrow', 'app': 'shell', 'kind': 'region', 'label': 'Ribbon Tab Row', 'behaviour': 'Spans the 30-pixel strip beneath the title bar, hosting the File tab button, the main and contextual ribbon tabs, and the right-hand collaboration and mode controls.', 'order': 1},
    {'id': 'shell.region.ribbon', 'app': 'shell', 'kind': 'region', 'label': 'Lower Ribbon', 'behaviour': "Hosts the active ribbon tab's command groups and controls across a 100-pixel band beneath the tab row when Always show Ribbon is active.", 'order': 2},
    {'id': 'shell.region.messageBar', 'app': 'shell', 'kind': 'region', 'label': 'Message Bar', 'behaviour': 'Appears directly below the ribbon as a 32-pixel banner when the document raises an information, warning, error or Protected View notice.', 'order': 3},
    {'id': 'shell.region.documentArea', 'app': 'shell', 'kind': 'region', 'label': 'Document Area', 'behaviour': 'Occupies the central workspace between the ribbon (or message bar) and the status bar, shrinking horizontally when task panes dock on the left or right.', 'order': 4},
    {'id': 'shell.region.taskPaneDock', 'app': 'shell', 'kind': 'region', 'label': 'Task Pane Dock', 'behaviour': 'Hosts docked side panes at the right edge of the workspace between the ribbon and the status bar, defaulting to 320 pixels wide.', 'order': 5},
    {'id': 'shell.region.statusbar', 'app': 'shell', 'kind': 'region', 'label': 'Status Bar', 'behaviour': 'Spans the bottom 22 pixels of the window frame, showing document indicators on the left and view and zoom controls on the right.', 'order': 6, 'uiaId': 'StatusBar'},
    {'id': 'shell.titlebar.systemMenu', 'app': 'shell', 'kind': 'control', 'label': 'System', 'behaviour': 'Opens the window system menu with Restore, Move, Size, Minimize, Maximize and Close commands when clicked or triggered with Alt+Space.', 'parent': 'shell.region.titlebar', 'order': 0, 'controlType': 'menu', 'keytip': 'Space', 'uiaId': 'MenuBar', 'baselineMissing': True},
    {'id': 'shell.titlebar.qat', 'app': 'shell', 'kind': 'region', 'label': 'Quick Access Toolbar', 'behaviour': 'Holds pinned one-click commands and the Customize Quick Access Toolbar drop-down on the left side of the title bar.', 'parent': 'shell.region.titlebar', 'order': 1},
    {'id': 'shell.titlebar.autosave', 'app': 'shell', 'kind': 'control', 'label': 'AutoSave', 'behaviour': 'Toggles automatic cloud saving for the active document when stored on a connected cloud drive.', 'parent': 'shell.region.titlebar', 'order': 2, 'controlType': 'toggleButton', 'keytip': '1', 'idMso': 'AutoSaveSwitch', 'uiaId': 'AutoSaveSwitch'},
    {'id': 'shell.titlebar.documentTitle', 'app': 'shell', 'kind': 'control', 'label': 'Document Title', 'behaviour': 'Displays the active document name and save state and opens the rename and location flyout when clicked.', 'parent': 'shell.region.titlebar', 'order': 3, 'controlType': 'button', 'keytip': 'B', 'baselineMissing': True},
    {'id': 'shell.titlebar.caption', 'app': 'shell', 'kind': 'control', 'label': 'Window Caption', 'behaviour': 'Displays the document title and application name across the draggable title bar area and toggles maximise on double-click.', 'parent': 'shell.region.titlebar', 'order': 4, 'controlType': 'label', 'baselineMissing': True},
    {'id': 'shell.titlebar.search', 'app': 'shell', 'kind': 'control', 'label': 'Search', 'behaviour': 'Focuses the title bar command and content search box (Alt+Q) and opens the search suggestions flyout.', 'parent': 'shell.region.titlebar', 'order': 5, 'controlType': 'menu', 'keytip': 'Q', 'uiaId': 'TellMeControlAnchor', 'baselineMissing': True},
    {'id': 'shell.titlebar.account', 'app': 'shell', 'kind': 'control', 'label': 'Account', 'behaviour': 'Opens the account flyout showing the signed-in profile, account settings and sign-out controls.', 'parent': 'shell.region.titlebar', 'order': 6, 'controlType': 'menu', 'keytip': 'ZP', 'uiaId': 'MeControlWidget', 'baselineMissing': True},
    {'id': 'shell.titlebar.minimize', 'app': 'shell', 'kind': 'control', 'label': 'Minimize', 'behaviour': 'Minimises the application window to the Windows taskbar.', 'parent': 'shell.region.titlebar', 'order': 7, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.titlebar.maximize', 'app': 'shell', 'kind': 'control', 'label': 'Restore Down', 'behaviour': 'Restores a maximised window to its previous floating bounds or maximises a floating window, and shows Windows Snap Layouts on hover.', 'parent': 'shell.region.titlebar', 'order': 8, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.titlebar.close', 'app': 'shell', 'kind': 'control', 'label': 'Close', 'behaviour': 'Closes the active application window, prompting to save unsaved changes before exiting.', 'parent': 'shell.region.titlebar', 'order': 9, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.qat.autosave', 'app': 'shell', 'kind': 'control', 'label': 'AutoSave', 'behaviour': 'Toggles continuous background saving of the active document in the Quick Access Toolbar.', 'parent': 'shell.titlebar.qat', 'order': 0, 'controlType': 'toggleButton', 'keytip': '1', 'idMso': 'AutoSaveSwitch', 'uiaId': 'AutoSaveSwitch'},
    {'id': 'shell.qat.save', 'app': 'shell', 'kind': 'control', 'label': 'Save', 'behaviour': 'Saves the active document immediately or opens the Save As page when the document has not yet been saved to disk.', 'parent': 'shell.titlebar.qat', 'order': 1, 'controlType': 'button', 'keytip': '2', 'idMso': 'FileSave', 'uiaId': 'FileSave'},
    {'id': 'shell.qat.undo', 'app': 'shell', 'kind': 'control', 'label': 'Undo', 'behaviour': 'Reverses the last editing action on click or opens the history of recent actions to undo several steps at once.', 'parent': 'shell.titlebar.qat', 'order': 2, 'controlType': 'splitButton', 'keytip': '3', 'idMso': 'Undo'},
    {'id': 'shell.qat.undo.dropdown', 'app': 'shell', 'kind': 'control', 'label': 'More Options', 'behaviour': 'Opens the chronological list of recent editing actions so multiple actions can be undone together.', 'parent': 'shell.qat.undo', 'order': 0, 'controlType': 'menu', 'uiaId': 'Undo_Dropdown', 'baselineMissing': True},
    {'id': 'shell.qat.redo', 'app': 'shell', 'kind': 'control', 'label': 'Repeat', 'behaviour': 'Repeats the last editing command or redoes the most recently undone action.', 'parent': 'shell.titlebar.qat', 'order': 3, 'controlType': 'button', 'keytip': '4', 'idMso': 'RedoOrRepeat', 'uiaId': 'RedoOrRepeat'},
    {'id': 'shell.qat.customize', 'app': 'shell', 'kind': 'control', 'label': 'Customize Quick Access Toolbar', 'behaviour': 'Opens the menu to toggle common Quick Access Toolbar buttons, open the full command customiser, move the toolbar below the ribbon or hide it.', 'parent': 'shell.titlebar.qat', 'order': 4, 'controlType': 'menu', 'baselineMissing': True},
    {'id': 'shell.qat.customize.automatically-save', 'app': 'shell', 'kind': 'menuItem', 'label': 'Automatically Save', 'behaviour': 'Shows or hides the AutoSave toggle switch on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 0, 'controlType': 'button', 'idMso': 'AutoSaveSwitch', 'uiaId': 'AutoSaveSwitch'},
    {'id': 'shell.qat.customize.new', 'app': 'shell', 'kind': 'menuItem', 'label': 'New', 'behaviour': 'Shows or hides the New Blank Document button on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 1, 'controlType': 'button', 'idMso': 'FileNewDefault', 'uiaId': 'FileNewDefault'},
    {'id': 'shell.qat.customize.open', 'app': 'shell', 'kind': 'menuItem', 'label': 'Open', 'behaviour': 'Shows or hides the Open button on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 2, 'controlType': 'button', 'idMso': 'FileOpenUsingBackstage', 'uiaId': 'FileOpenUsingBackstage'},
    {'id': 'shell.qat.customize.save', 'app': 'shell', 'kind': 'menuItem', 'label': 'Save', 'behaviour': 'Shows or hides the Save button on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 3, 'controlType': 'button', 'idMso': 'FileSave', 'uiaId': 'FileSave'},
    {'id': 'shell.qat.customize.email', 'app': 'shell', 'kind': 'menuItem', 'label': 'Email', 'behaviour': 'Shows or hides the Email attachment button on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 4, 'controlType': 'button', 'idMso': 'FileSendAsAttachment', 'uiaId': 'FileSendAsAttachment'},
    {'id': 'shell.qat.customize.quick-print', 'app': 'shell', 'kind': 'menuItem', 'label': 'Quick Print', 'behaviour': 'Shows or hides the Quick Print button that sends the document directly to the default printer.', 'parent': 'shell.qat.customize', 'order': 5, 'controlType': 'button', 'idMso': 'FilePrintQuick', 'uiaId': 'FilePrintQuick'},
    {'id': 'shell.qat.customize.print-preview-and-print', 'app': 'shell', 'kind': 'menuItem', 'label': 'Print Preview and Print', 'behaviour': 'Shows or hides the Print Preview and Print button on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 6, 'controlType': 'button', 'idMso': 'PrintPreviewAndPrint', 'uiaId': 'PrintPreviewAndPrint'},
    {'id': 'shell.qat.customize.editor-f7', 'app': 'shell', 'kind': 'menuItem', 'label': 'Editor (F7)', 'behaviour': 'Shows or hides the Editor proofing command on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 7, 'controlType': 'button', 'idMso': 'WritingAssistanceCheckDocument', 'uiaId': 'WritingAssistanceCheckDocument'},
    {'id': 'shell.qat.customize.read-aloud', 'app': 'shell', 'kind': 'menuItem', 'label': 'Read Aloud', 'behaviour': 'Shows or hides the Read Aloud speech command on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 8, 'controlType': 'button', 'idMso': 'ReadAloud', 'uiaId': 'ReadAloud'},
    {'id': 'shell.qat.customize.undo', 'app': 'shell', 'kind': 'menuItem', 'label': 'Undo', 'behaviour': 'Shows or hides the Undo split button on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 9, 'controlType': 'button', 'idMso': 'Undo', 'uiaId': 'Undo'},
    {'id': 'shell.qat.customize.redo', 'app': 'shell', 'kind': 'menuItem', 'label': 'Redo', 'behaviour': 'Shows or hides the Redo or Repeat button on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 10, 'controlType': 'button', 'idMso': 'RedoOrRepeat', 'uiaId': 'RedoOrRepeat'},
    {'id': 'shell.qat.customize.draw-table', 'app': 'shell', 'kind': 'menuItem', 'label': 'Draw Table', 'behaviour': 'Shows or hides the Draw Table pen tool on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 11, 'controlType': 'button', 'idMso': 'TableDrawTable', 'uiaId': 'TableDrawTable'},
    {'id': 'shell.qat.customize.touch-mouse-mode', 'app': 'shell', 'kind': 'menuItem', 'label': 'Touch/Mouse Mode', 'behaviour': 'Shows or hides the Touch or Mouse Mode spacing selector on the Quick Access Toolbar.', 'parent': 'shell.qat.customize', 'order': 12, 'controlType': 'button', 'idMso': 'PointerModeOptions', 'uiaId': 'PointerModeOptions'},
    {'id': 'shell.qat.customize.more-commands', 'app': 'shell', 'kind': 'menuItem', 'label': 'More Commands...', 'behaviour': 'Opens the Options dialog to the Quick Access Toolbar page for adding, removing or reordering any command.', 'parent': 'shell.qat.customize', 'order': 13, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.qat.customize.show-below-the-ribbon', 'app': 'shell', 'kind': 'menuItem', 'label': 'Show Below the Ribbon', 'behaviour': 'Moves the Quick Access Toolbar from the title bar to a dedicated strip directly below the ribbon.', 'parent': 'shell.qat.customize', 'order': 14, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.qat.customize.hide-quick-access-toolbar', 'app': 'shell', 'kind': 'menuItem', 'label': 'Hide Quick Access Toolbar', 'behaviour': 'Hides the Quick Access Toolbar from the window frame until re-enabled from Ribbon Display Options or Options.', 'parent': 'shell.qat.customize', 'order': 15, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.tabrow.file', 'app': 'shell', 'kind': 'control', 'label': 'File Tab', 'behaviour': 'Opens the full-window Backstage view for file management, printing, sharing, account settings and application options.', 'parent': 'shell.region.tabrow', 'order': 0, 'controlType': 'button', 'keytip': 'F', 'uiaId': 'FileTabButton', 'baselineMissing': True},
    {'id': 'shell.tabrow.tabs', 'app': 'shell', 'kind': 'region', 'label': 'Ribbon Tabs', 'behaviour': 'Contains the ordered core and contextual tab headers along the tab row.', 'parent': 'shell.region.tabrow', 'order': 1},
    {'id': 'shell.tabrow.comments', 'app': 'shell', 'kind': 'control', 'label': 'Comments', 'behaviour': 'Toggles the document Comments pane for viewing, replying to and resolving review threads.', 'parent': 'shell.region.tabrow', 'order': 2, 'controlType': 'toggleButton', 'keytip': 'ZC', 'baselineMissing': True},
    {'id': 'shell.tabrow.editingMode', 'app': 'shell', 'kind': 'control', 'label': 'Editing', 'behaviour': 'Opens the document access mode selector to switch between Editing, Reviewing (track changes) and Viewing (read-only).', 'parent': 'shell.region.tabrow', 'order': 3, 'controlType': 'comboBox', 'keytip': 'ZM', 'baselineMissing': True},
    {'id': 'shell.tabrow.editingMode.editing', 'app': 'shell', 'kind': 'menuItem', 'label': 'Editing', 'behaviour': 'Allows direct changes to the document content and formatting without forcing tracked revisions.', 'parent': 'shell.tabrow.editingMode', 'order': 0, 'controlType': 'galleryItem', 'baselineMissing': True},
    {'id': 'shell.tabrow.editingMode.reviewing', 'app': 'shell', 'kind': 'menuItem', 'label': 'Reviewing', 'behaviour': 'Restricts edits to tracked insertions, deletions and comments so others can review suggested changes.', 'parent': 'shell.tabrow.editingMode', 'order': 1, 'controlType': 'galleryItem', 'baselineMissing': True},
    {'id': 'shell.tabrow.editingMode.viewing', 'app': 'shell', 'kind': 'menuItem', 'label': 'Viewing', 'behaviour': 'Locks the document against accidental edits so it can be read without modifying content.', 'parent': 'shell.tabrow.editingMode', 'order': 2, 'controlType': 'galleryItem', 'baselineMissing': True},
    {'id': 'shell.tabrow.share', 'app': 'shell', 'kind': 'control', 'label': 'Share', 'behaviour': 'Opens the sharing menu to invite collaborators, copy a sharing link or manage access permissions.', 'parent': 'shell.region.tabrow', 'order': 4, 'controlType': 'menu', 'keytip': 'ZS', 'baselineMissing': True},
    {'id': 'shell.tabrow.share.share', 'app': 'shell', 'kind': 'menuItem', 'label': 'Share...', 'behaviour': 'Opens the Share dialog to send the document or invite people to collaborate.', 'parent': 'shell.tabrow.share', 'order': 0, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.tabrow.share.copy-link', 'app': 'shell', 'kind': 'menuItem', 'label': 'Copy Link...', 'behaviour': 'Generates and copies a link to the document into the clipboard.', 'parent': 'shell.tabrow.share', 'order': 1, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.tabrow.share.manage-access', 'app': 'shell', 'kind': 'menuItem', 'label': 'Manage Access...', 'behaviour': 'Opens the permissions view to review or revoke who can view or edit the document.', 'parent': 'shell.tabrow.share', 'order': 2, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.ribbonDisplay.button', 'app': 'shell', 'kind': 'control', 'label': 'Ribbon Display Options', 'behaviour': 'Opens the menu at the bottom-right corner of the lower ribbon to control ribbon visibility and Quick Access Toolbar visibility.', 'parent': 'shell.region.ribbon', 'order': 0, 'controlType': 'menu', 'baselineMissing': True},
    {'id': 'shell.ribbonDisplay.full-screen-mode', 'app': 'shell', 'kind': 'menuItem', 'label': 'Full-screen mode', 'behaviour': 'Hides both the ribbon and the tab row to maximise document space, revealing them temporarily when the top of the window is clicked.', 'parent': 'shell.ribbonDisplay.button', 'order': 0, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.ribbonDisplay.show-tabs-only', 'app': 'shell', 'kind': 'menuItem', 'label': 'Show tabs only', 'behaviour': "Collapses the lower ribbon so only the tab row stays visible, opening a tab's commands as a popup when clicked.", 'parent': 'shell.ribbonDisplay.button', 'order': 1, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.ribbonDisplay.always-show-ribbon', 'app': 'shell', 'kind': 'menuItem', 'label': 'Always show Ribbon', 'behaviour': 'Pins both the tab row and the full lower ribbon open above the document workspace.', 'parent': 'shell.ribbonDisplay.button', 'order': 2, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.ribbonDisplay.hide-quick-access-toolbar', 'app': 'shell', 'kind': 'menuItem', 'label': 'Hide Quick Access Toolbar', 'behaviour': 'Toggles visibility of the Quick Access Toolbar (reading Show Quick Access Toolbar when the toolbar is currently hidden).', 'parent': 'shell.ribbonDisplay.button', 'order': 3, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.search.input', 'app': 'shell', 'kind': 'control', 'label': 'Search Input', 'behaviour': 'Accepts text queries (Alt+Q) to search commands, document text, help topics and connected files.', 'parent': 'shell.titlebar.search', 'order': 0, 'controlType': 'editBox', 'keytip': 'Q', 'uiaId': 'TellMeTextBoxAutomationId', 'baselineMissing': True},
    {'id': 'shell.search.voice', 'app': 'shell', 'kind': 'control', 'label': 'Voice Search', 'behaviour': 'Starts microphone dictation into the search box to find commands or content by voice.', 'parent': 'shell.titlebar.search', 'order': 1, 'controlType': 'button', 'keytip': 'Q', 'baselineMissing': True},
    {'id': 'shell.search.flyout', 'app': 'shell', 'kind': 'region', 'label': 'Search Flyout', 'behaviour': 'Displays categorised command, document, people, file and help results beneath the title bar search box.', 'parent': 'shell.titlebar.search', 'order': 2},
    {'id': 'shell.search.recentActions', 'app': 'shell', 'kind': 'group', 'label': 'Recently Used Actions', 'behaviour': 'Lists the commands most recently invoked from the search box for one-click reuse.', 'parent': 'shell.search.flyout', 'order': 0, 'baselineMissing': True},
    {'id': 'shell.search.suggestedActions', 'app': 'shell', 'kind': 'group', 'label': 'Suggested Actions', 'behaviour': 'Lists contextually relevant commands when the search box is first opened before typing a query.', 'parent': 'shell.search.flyout', 'order': 1, 'baselineMissing': True},
    {'id': 'shell.search.suggestedActions.spelling-and-grammar', 'app': 'shell', 'kind': 'menuItem', 'label': 'Spelling and Grammar', 'behaviour': 'Runs the spelling and grammar checker on the active document from the default Suggested Actions list.', 'parent': 'shell.search.suggestedActions', 'order': 0, 'controlType': 'galleryItem', 'baselineMissing': True},
    {'id': 'shell.search.suggestedActions.word-count', 'app': 'shell', 'kind': 'menuItem', 'label': 'Word Count', 'behaviour': 'Opens the Word Count statistics dialog from the default Suggested Actions list.', 'parent': 'shell.search.suggestedActions', 'order': 1, 'controlType': 'galleryItem', 'baselineMissing': True},
    {'id': 'shell.search.suggestedActions.print', 'app': 'shell', 'kind': 'menuItem', 'label': 'Print', 'behaviour': 'Opens the Backstage Print page from the default Suggested Actions list.', 'parent': 'shell.search.suggestedActions', 'order': 2, 'controlType': 'galleryItem', 'baselineMissing': True},
    {'id': 'shell.search.people', 'app': 'shell', 'kind': 'group', 'label': 'People', 'behaviour': 'Lists collaborators and contacts matching the search query without exposing personal identities in the static inventory.', 'parent': 'shell.search.flyout', 'order': 2, 'baselineMissing': True},
    {'id': 'shell.search.actions', 'app': 'shell', 'kind': 'group', 'label': 'Actions', 'behaviour': 'Lists matching application commands and menus with direct execution and nested submenus as the user types.', 'parent': 'shell.search.flyout', 'order': 3, 'baselineMissing': True},
    {'id': 'shell.search.findInDocument', 'app': 'shell', 'kind': 'group', 'label': 'Find in Document', 'behaviour': "Searches the active document's text for the typed query and jumps to matching occurrences.", 'parent': 'shell.search.flyout', 'order': 4, 'baselineMissing': True},
    {'id': 'shell.search.files', 'app': 'shell', 'kind': 'group', 'label': 'Files', 'behaviour': 'Lists recent and cloud documents whose titles or contents match the search query.', 'parent': 'shell.search.flyout', 'order': 5, 'baselineMissing': True},
    {'id': 'shell.search.help', 'app': 'shell', 'kind': 'group', 'label': 'Help', 'behaviour': 'Lists documentation and help articles matching the search query.', 'parent': 'shell.search.flyout', 'order': 6, 'baselineMissing': True},
    {'id': 'shell.keytips.layer', 'app': 'shell', 'kind': 'region', 'label': 'KeyTips Layer', 'behaviour': 'Overlays alphanumeric keyboard access badges across the title bar and ribbon tab row when Alt or F10 is pressed and released.', 'order': 7},
    {'id': 'shell.keytips.autosave', 'app': 'shell', 'kind': 'control', 'label': 'AutoSave KeyTip', 'behaviour': 'Triggers the AutoSave toggle on the Quick Access Toolbar when 1 is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 0, 'controlType': 'label', 'keytip': '1', 'baselineMissing': True},
    {'id': 'shell.keytips.save', 'app': 'shell', 'kind': 'control', 'label': 'Save KeyTip', 'behaviour': 'Triggers the Save command on the Quick Access Toolbar when 2 is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 1, 'controlType': 'label', 'keytip': '2', 'baselineMissing': True},
    {'id': 'shell.keytips.undo', 'app': 'shell', 'kind': 'control', 'label': 'Undo KeyTip', 'behaviour': 'Triggers the Undo command on the Quick Access Toolbar when 3 is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 2, 'controlType': 'label', 'keytip': '3', 'baselineMissing': True},
    {'id': 'shell.keytips.redo', 'app': 'shell', 'kind': 'control', 'label': 'Redo KeyTip', 'behaviour': 'Triggers the Repeat or Redo command on the Quick Access Toolbar when 4 is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 3, 'controlType': 'label', 'keytip': '4', 'baselineMissing': True},
    {'id': 'shell.keytips.documentTitle', 'app': 'shell', 'kind': 'control', 'label': 'Document Title KeyTip', 'behaviour': 'Opens the document title and file location flyout when B is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 4, 'controlType': 'label', 'keytip': 'B', 'baselineMissing': True},
    {'id': 'shell.keytips.search', 'app': 'shell', 'kind': 'control', 'label': 'Search KeyTip', 'behaviour': 'Focuses the title bar search box when Q is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 5, 'controlType': 'label', 'keytip': 'Q', 'baselineMissing': True},
    {'id': 'shell.keytips.account', 'app': 'shell', 'kind': 'control', 'label': 'Account KeyTip', 'behaviour': 'Opens the Account flyout when Z then P is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 6, 'controlType': 'label', 'keytip': 'ZP', 'baselineMissing': True},
    {'id': 'shell.keytips.file', 'app': 'shell', 'kind': 'control', 'label': 'File KeyTip', 'behaviour': 'Opens the Backstage view when F is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 7, 'controlType': 'label', 'keytip': 'F', 'baselineMissing': True},
    {'id': 'shell.keytips.comments', 'app': 'shell', 'kind': 'control', 'label': 'Comments KeyTip', 'behaviour': 'Toggles the Comments pane when Z then C is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 8, 'controlType': 'label', 'keytip': 'ZC', 'baselineMissing': True},
    {'id': 'shell.keytips.editingMode', 'app': 'shell', 'kind': 'control', 'label': 'Editing Mode KeyTip', 'behaviour': 'Opens the Editing, Reviewing and Viewing mode menu when Z then M is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 9, 'controlType': 'label', 'keytip': 'ZM', 'baselineMissing': True},
    {'id': 'shell.keytips.share', 'app': 'shell', 'kind': 'control', 'label': 'Share KeyTip', 'behaviour': 'Opens the Share menu when Z then S is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 10, 'controlType': 'label', 'keytip': 'ZS', 'baselineMissing': True},
    {'id': 'shell.backstage.frame', 'app': 'shell', 'kind': 'region', 'label': 'Backstage Frame', 'behaviour': 'Replaces the ribbon and document workspace with the full-window File Backstage view when the File tab is activated.', 'order': 8, 'uiaId': 'BackstageView'},
    {'id': 'shell.backstage.titlebar', 'app': 'shell', 'kind': 'region', 'label': 'Backstage Title Bar', 'behaviour': 'Spans the top 48 pixels of the Backstage view, keeping the document title and window caption buttons accessible.', 'parent': 'shell.backstage.frame', 'order': 0},
    {'id': 'shell.backstage.navBar', 'app': 'shell', 'kind': 'region', 'label': 'Backstage Navigation Bar', 'behaviour': 'Spans a 160-pixel vertical rail on the left side of the Backstage view, hosting the Back button and page navigation tabs.', 'parent': 'shell.backstage.frame', 'order': 1, 'uiaId': 'OutSpaceNavBar'},
    {'id': 'shell.backstage.navList', 'app': 'shell', 'kind': 'control', 'label': 'File Navigation List', 'behaviour': 'Lists the Backstage pages (Home, New, Open, Info, Save, Print, Share, Export, Transform, Close, Account, Feedback, Options) in the left rail.', 'parent': 'shell.backstage.navBar', 'order': 0, 'controlType': 'listBox', 'uiaId': 'NavBarMenu', 'baselineMissing': True},
    {'id': 'shell.backstage.back', 'app': 'shell', 'kind': 'control', 'label': 'Back', 'behaviour': 'Closes the Backstage view and returns focus to the active document and ribbon (also triggered by Escape).', 'parent': 'shell.backstage.navBar', 'order': 1, 'controlType': 'button', 'keytip': 'B', 'uiaId': 'FileTabButton', 'baselineMissing': True},
    {'id': 'shell.backstage.contentPane', 'app': 'shell', 'kind': 'region', 'label': 'Backstage Content Area', 'behaviour': 'Occupies the 1760-pixel area to the right of the Backstage navigation rail, rendering the selected Backstage page.', 'parent': 'shell.backstage.frame', 'order': 2, 'uiaId': 'BackstageView'},
    {'id': 'shell.statusbar.bar', 'app': 'shell', 'kind': 'region', 'label': 'Status Bar Frame', 'behaviour': 'Hosts the status bar controls across the bottom 22-pixel strip of the window frame.', 'parent': 'shell.region.statusbar', 'order': 0},
    {'id': 'shell.statusbar.leftZone', 'app': 'shell', 'kind': 'region', 'label': 'Status Bar Left Zone', 'behaviour': 'Hosts document-state indicators (page number, word count, proofing state, macro recording, accessibility status) aligned to the left edge.', 'parent': 'shell.statusbar.bar', 'order': 0},
    {'id': 'shell.statusbar.rightZone', 'app': 'shell', 'kind': 'region', 'label': 'Status Bar Right Zone', 'behaviour': 'Hosts display settings, view switchers and zoom controls aligned to the right edge of the status bar.', 'parent': 'shell.statusbar.bar', 'order': 1},
    {'id': 'shell.statusbar.displaySettings', 'app': 'shell', 'kind': 'control', 'label': 'Display Settings', 'behaviour': 'Opens display and multi-monitor rendering options from the right zone of the status bar when present.', 'parent': 'shell.statusbar.rightZone', 'order': 0, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.statusbar.viewSwitcher', 'app': 'shell', 'kind': 'region', 'label': 'View Switcher', 'behaviour': 'Holds the quick view-mode toggle buttons (such as Read Mode, Print Layout and Web Layout) on the right side of the status bar.', 'parent': 'shell.statusbar.rightZone', 'order': 1},
    {'id': 'shell.statusbar.zoomOut', 'app': 'shell', 'kind': 'control', 'label': 'Zoom Out', 'behaviour': 'Decreases the active document zoom level in 10 percent steps.', 'parent': 'shell.statusbar.rightZone', 'order': 2, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.statusbar.zoomSlider', 'app': 'shell', 'kind': 'control', 'label': 'Zoom', 'behaviour': 'Drags the document magnification continuously between the minimum and maximum zoom percentages.', 'parent': 'shell.statusbar.rightZone', 'order': 3, 'controlType': 'slider', 'baselineMissing': True},
    {'id': 'shell.statusbar.zoomIn', 'app': 'shell', 'kind': 'control', 'label': 'Zoom In', 'behaviour': 'Increases the active document zoom level in 10 percent steps.', 'parent': 'shell.statusbar.rightZone', 'order': 4, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.statusbar.zoomPercent', 'app': 'shell', 'kind': 'control', 'label': 'Zoom 100%', 'behaviour': 'Displays the current zoom percentage and opens the Zoom dialog when clicked.', 'parent': 'shell.statusbar.rightZone', 'order': 5, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'shell.statusbar.customizeMenu', 'app': 'shell', 'kind': 'contextMenu', 'label': 'Customize Status Bar', 'behaviour': 'Opens on right-clicking the status bar to toggle which indicators, aggregates, view buttons and zoom controls are shown.', 'parent': 'shell.statusbar.bar', 'order': 2},
    {'id': 'excel.shell.titlebar.caption', 'app': 'excel', 'kind': 'control', 'label': 'Book1 - Excel', 'behaviour': 'Displays the active workbook name and Excel application title across the title bar caption area.', 'parent': 'shell.region.titlebar', 'order': 4, 'controlType': 'label', 'baselineMissing': True},
    {'id': 'excel.shell.qat.redo', 'app': 'excel', 'kind': 'control', 'label': 'Redo', 'behaviour': "Redoes the last undone workbook edit or opens the redo history list as a split button on Excel's Quick Access Toolbar.", 'parent': 'shell.titlebar.qat', 'order': 3, 'controlType': 'splitButton', 'keytip': '4', 'idMso': 'Redo', 'uiaId': 'Redo'},
    {'id': 'excel.shell.region.tabrow', 'app': 'excel', 'kind': 'region', 'label': 'Excel Ribbon Tab Row', 'behaviour': "Spans the 30-pixel tab row in Excel, hosting File, Ribbon Tabs, Comments and Share while omitting Word's Editing mode drop-down.", 'order': 1},
    {'id': 'excel.shell.tabrow.file', 'app': 'excel', 'kind': 'control', 'label': 'File Tab', 'behaviour': 'Opens the Excel Backstage view for workbook management, printing, sharing and options.', 'parent': 'excel.shell.region.tabrow', 'order': 0, 'controlType': 'button', 'keytip': 'F', 'uiaId': 'FileTabButton', 'baselineMissing': True},
    {'id': 'excel.shell.tabrow.tabs', 'app': 'excel', 'kind': 'region', 'label': 'Ribbon Tabs', 'behaviour': "Contains Excel's core and contextual ribbon tabs along the tab row.", 'parent': 'excel.shell.region.tabrow', 'order': 1},
    {'id': 'excel.shell.tabrow.comments', 'app': 'excel', 'kind': 'control', 'label': 'Comments', 'behaviour': 'Toggles the workbook Comments pane on the right side of the tab row.', 'parent': 'excel.shell.region.tabrow', 'order': 2, 'controlType': 'toggleButton', 'keytip': 'ZC', 'baselineMissing': True},
    {'id': 'excel.shell.tabrow.share', 'app': 'excel', 'kind': 'control', 'label': 'Share', 'behaviour': "Opens the workbook Share menu on the right end of Excel's tab row.", 'parent': 'excel.shell.region.tabrow', 'order': 3, 'controlType': 'menu', 'keytip': 'ZS', 'baselineMissing': True},
    {'id': 'powerpoint.shell.titlebar.qat', 'app': 'powerpoint', 'kind': 'region', 'label': 'PowerPoint Quick Access Toolbar', 'behaviour': "Holds AutoSave, Save, Undo, Repeat, Start From Beginning and Customize Quick Access Toolbar in PowerPoint's title bar.", 'parent': 'shell.region.titlebar', 'order': 1},
    {'id': 'powerpoint.shell.qat.autosave', 'app': 'powerpoint', 'kind': 'control', 'label': 'AutoSave', 'behaviour': "Toggles automatic cloud saving for the active presentation on PowerPoint's Quick Access Toolbar.", 'parent': 'powerpoint.shell.titlebar.qat', 'order': 0, 'controlType': 'toggleButton', 'keytip': '1', 'idMso': 'AutoSaveSwitch', 'uiaId': 'AutoSaveSwitch'},
    {'id': 'powerpoint.shell.qat.save', 'app': 'powerpoint', 'kind': 'control', 'label': 'Save', 'behaviour': "Saves the active presentation from PowerPoint's Quick Access Toolbar.", 'parent': 'powerpoint.shell.titlebar.qat', 'order': 1, 'controlType': 'button', 'keytip': '2', 'idMso': 'FileSave', 'uiaId': 'FileSave'},
    {'id': 'powerpoint.shell.qat.undo', 'app': 'powerpoint', 'kind': 'control', 'label': 'Undo', 'behaviour': 'Undoes the last presentation action or opens the undo history drop-down.', 'parent': 'powerpoint.shell.titlebar.qat', 'order': 2, 'controlType': 'splitButton', 'keytip': '3', 'idMso': 'Undo'},
    {'id': 'powerpoint.shell.qat.redo', 'app': 'powerpoint', 'kind': 'control', 'label': 'Repeat', 'behaviour': 'Repeats or redoes the last presentation action.', 'parent': 'powerpoint.shell.titlebar.qat', 'order': 3, 'controlType': 'button', 'keytip': '4', 'idMso': 'RedoOrRepeat', 'uiaId': 'RedoOrRepeat'},
    {'id': 'powerpoint.shell.qat.fromBeginning', 'app': 'powerpoint', 'kind': 'control', 'label': 'Start From Beginning', 'behaviour': "Starts the slide show from the first slide in the presentation (F5) directly from PowerPoint's default Quick Access Toolbar.", 'parent': 'powerpoint.shell.titlebar.qat', 'order': 4, 'controlType': 'button', 'keytip': '5', 'idMso': 'SlideShowFromBeginning', 'uiaId': 'SlideShowFromBeginning'},
    {'id': 'powerpoint.shell.qat.customize', 'app': 'powerpoint', 'kind': 'control', 'label': 'Customize Quick Access Toolbar', 'behaviour': 'Opens the Quick Access Toolbar customisation menu in PowerPoint.', 'parent': 'powerpoint.shell.titlebar.qat', 'order': 5, 'controlType': 'menu', 'baselineMissing': True},
    {'id': 'powerpoint.shell.qat.customize.automatically-save', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Automatically Save', 'behaviour': 'Shows or hides the AutoSave toggle switch on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 0, 'controlType': 'button', 'idMso': 'AutoSaveSwitch', 'uiaId': 'AutoSaveSwitch'},
    {'id': 'powerpoint.shell.qat.customize.new', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'New', 'behaviour': 'Shows or hides the New Blank Document button on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 1, 'controlType': 'button', 'idMso': 'FileNewDefault', 'uiaId': 'FileNewDefault'},
    {'id': 'powerpoint.shell.qat.customize.open', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Open', 'behaviour': 'Shows or hides the Open button on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 2, 'controlType': 'button', 'idMso': 'FileOpenUsingBackstage', 'uiaId': 'FileOpenUsingBackstage'},
    {'id': 'powerpoint.shell.qat.customize.save', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Save', 'behaviour': 'Shows or hides the Save button on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 3, 'controlType': 'button', 'idMso': 'FileSave', 'uiaId': 'FileSave'},
    {'id': 'powerpoint.shell.qat.customize.email', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Email', 'behaviour': 'Shows or hides the Email attachment button on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 4, 'controlType': 'button', 'idMso': 'FileSendAsAttachment', 'uiaId': 'FileSendAsAttachment'},
    {'id': 'powerpoint.shell.qat.customize.quick-print', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Quick Print', 'behaviour': 'Shows or hides the Quick Print button that sends the document directly to the default printer.', 'parent': 'powerpoint.shell.qat.customize', 'order': 5, 'controlType': 'button', 'idMso': 'FilePrintQuick', 'uiaId': 'FilePrintQuick'},
    {'id': 'powerpoint.shell.qat.customize.print-preview-and-print', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Print Preview and Print', 'behaviour': 'Shows or hides the Print Preview and Print button on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 6, 'controlType': 'button', 'idMso': 'PrintPreviewAndPrint', 'uiaId': 'PrintPreviewAndPrint'},
    {'id': 'powerpoint.shell.qat.customize.editor-f7', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Editor (F7)', 'behaviour': 'Shows or hides the Editor proofing command on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 7, 'controlType': 'button', 'idMso': 'WritingAssistanceCheckDocument', 'uiaId': 'WritingAssistanceCheckDocument'},
    {'id': 'powerpoint.shell.qat.customize.read-aloud', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Read Aloud', 'behaviour': 'Shows or hides the Read Aloud speech command on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 8, 'controlType': 'button', 'idMso': 'ReadAloud', 'uiaId': 'ReadAloud'},
    {'id': 'powerpoint.shell.qat.customize.undo', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Undo', 'behaviour': 'Shows or hides the Undo split button on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 9, 'controlType': 'button', 'idMso': 'Undo', 'uiaId': 'Undo'},
    {'id': 'powerpoint.shell.qat.customize.redo', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Redo', 'behaviour': 'Shows or hides the Redo or Repeat button on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 10, 'controlType': 'button', 'idMso': 'RedoOrRepeat', 'uiaId': 'RedoOrRepeat'},
    {'id': 'powerpoint.shell.qat.customize.draw-table', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Draw Table', 'behaviour': 'Shows or hides the Draw Table pen tool on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 11, 'controlType': 'button', 'idMso': 'TableDrawTable', 'uiaId': 'TableDrawTable'},
    {'id': 'powerpoint.shell.qat.customize.touch-mouse-mode', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Touch/Mouse Mode', 'behaviour': 'Shows or hides the Touch or Mouse Mode spacing selector on the Quick Access Toolbar.', 'parent': 'powerpoint.shell.qat.customize', 'order': 12, 'controlType': 'button', 'idMso': 'PointerModeOptions', 'uiaId': 'PointerModeOptions'},
    {'id': 'powerpoint.shell.qat.customize.more-commands', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'More Commands...', 'behaviour': 'Opens the Options dialog to the Quick Access Toolbar page for adding, removing or reordering any command.', 'parent': 'powerpoint.shell.qat.customize', 'order': 13, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'powerpoint.shell.qat.customize.show-below-the-ribbon', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Show Below the Ribbon', 'behaviour': 'Moves the Quick Access Toolbar from the title bar to a dedicated strip directly below the ribbon.', 'parent': 'powerpoint.shell.qat.customize', 'order': 14, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'powerpoint.shell.qat.customize.hide-quick-access-toolbar', 'app': 'powerpoint', 'kind': 'menuItem', 'label': 'Hide Quick Access Toolbar', 'behaviour': 'Hides the Quick Access Toolbar from the window frame until re-enabled from Ribbon Display Options or Options.', 'parent': 'powerpoint.shell.qat.customize', 'order': 15, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'powerpoint.shell.titlebar.caption', 'app': 'powerpoint', 'kind': 'control', 'label': 'Presentation1 - PowerPoint', 'behaviour': 'Displays the active presentation name and PowerPoint application title in the title bar.', 'parent': 'shell.region.titlebar', 'order': 4, 'controlType': 'label', 'baselineMissing': True},
    {'id': 'powerpoint.shell.region.tabrow', 'app': 'powerpoint', 'kind': 'region', 'label': 'PowerPoint Ribbon Tab Row', 'behaviour': 'Spans the 30-pixel tab row in PowerPoint, hosting File, Ribbon Tabs, Comments, Present in Teams and Share.', 'order': 1},
    {'id': 'powerpoint.shell.tabrow.file', 'app': 'powerpoint', 'kind': 'control', 'label': 'File Tab', 'behaviour': 'Opens the PowerPoint Backstage view.', 'parent': 'powerpoint.shell.region.tabrow', 'order': 0, 'controlType': 'button', 'keytip': 'F', 'uiaId': 'FileTabButton', 'baselineMissing': True},
    {'id': 'powerpoint.shell.tabrow.tabs', 'app': 'powerpoint', 'kind': 'region', 'label': 'Ribbon Tabs', 'behaviour': "Contains PowerPoint's core and contextual ribbon tabs.", 'parent': 'powerpoint.shell.region.tabrow', 'order': 1},
    {'id': 'powerpoint.shell.tabrow.comments', 'app': 'powerpoint', 'kind': 'control', 'label': 'Comments', 'behaviour': "Toggles the presentation Comments pane from PowerPoint's tab row.", 'parent': 'powerpoint.shell.region.tabrow', 'order': 2, 'controlType': 'toggleButton', 'keytip': 'ZC', 'baselineMissing': True},
    {'id': 'powerpoint.shell.tabrow.presentInTeams', 'app': 'powerpoint', 'kind': 'control', 'label': 'Present in Teams', 'behaviour': "Shares the active presentation directly into a live Microsoft Teams meeting from PowerPoint's tab row.", 'parent': 'powerpoint.shell.region.tabrow', 'order': 3, 'controlType': 'toggleButton', 'keytip': 'ZT', 'baselineMissing': True},
    {'id': 'powerpoint.shell.tabrow.share', 'app': 'powerpoint', 'kind': 'control', 'label': 'Share', 'behaviour': "Opens the presentation Share menu on the right end of PowerPoint's tab row.", 'parent': 'powerpoint.shell.region.tabrow', 'order': 4, 'controlType': 'menu', 'keytip': 'ZS', 'baselineMissing': True},
    {'id': 'powerpoint.shell.keytips.fromBeginning', 'app': 'powerpoint', 'kind': 'control', 'label': 'Start From Beginning KeyTip', 'behaviour': "Triggers Start From Beginning on PowerPoint's Quick Access Toolbar when 5 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 4, 'controlType': 'label', 'keytip': '5', 'baselineMissing': True},
    {'id': 'powerpoint.shell.keytips.presentInTeams', 'app': 'powerpoint', 'kind': 'control', 'label': 'Present in Teams KeyTip', 'behaviour': "Triggers Present in Teams on PowerPoint's tab row when Z then T is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 9, 'controlType': 'label', 'keytip': 'ZT', 'baselineMissing': True},
    {'id': 'visio.shell.region.titlebar', 'app': 'visio', 'kind': 'region', 'label': 'Visio Title Bar', 'behaviour': "Spans the top 48 pixels of Visio's window frame without an AutoSave switch.", 'order': 0},
    {'id': 'visio.shell.titlebar.systemMenu', 'app': 'visio', 'kind': 'control', 'label': 'System', 'behaviour': "Opens Visio's window system menu.", 'parent': 'visio.shell.region.titlebar', 'order': 0, 'controlType': 'menu', 'keytip': 'Space', 'uiaId': 'MenuBar', 'baselineMissing': True},
    {'id': 'visio.shell.titlebar.qat', 'app': 'visio', 'kind': 'region', 'label': 'Visio Quick Access Toolbar', 'behaviour': "Holds Save, Undo, Redo and Customize Quick Access Toolbar in Visio's title bar without AutoSave.", 'parent': 'visio.shell.region.titlebar', 'order': 1},
    {'id': 'visio.shell.qat.save', 'app': 'visio', 'kind': 'control', 'label': 'Save', 'behaviour': 'Saves the active Visio drawing (Ctrl+S).', 'parent': 'visio.shell.titlebar.qat', 'order': 0, 'controlType': 'button', 'keytip': '1', 'idMso': 'FileSave', 'uiaId': 'FileSave'},
    {'id': 'visio.shell.qat.undo', 'app': 'visio', 'kind': 'control', 'label': 'Undo', 'behaviour': 'Undoes the last drawing action or opens the undo history drop-down in Visio.', 'parent': 'visio.shell.titlebar.qat', 'order': 1, 'controlType': 'splitButton', 'keytip': '2', 'idMso': 'Undo'},
    {'id': 'visio.shell.qat.undo.dropdown', 'app': 'visio', 'kind': 'control', 'label': 'More Options', 'behaviour': 'Opens the chronological list of recent editing actions so multiple actions can be undone together.', 'parent': 'visio.shell.qat.undo', 'order': 0, 'controlType': 'menu', 'uiaId': 'Undo_Dropdown', 'baselineMissing': True},
    {'id': 'visio.shell.qat.redo', 'app': 'visio', 'kind': 'control', 'label': 'Redo', 'behaviour': 'Redoes the last undone drawing action in Visio.', 'parent': 'visio.shell.titlebar.qat', 'order': 2, 'controlType': 'button', 'keytip': '3', 'idMso': 'RedoOrRepeat', 'uiaId': 'RedoOrRepeat'},
    {'id': 'visio.shell.qat.customize', 'app': 'visio', 'kind': 'control', 'label': 'Customize Quick Access Toolbar', 'behaviour': 'Opens the Quick Access Toolbar customisation menu in Visio.', 'parent': 'visio.shell.titlebar.qat', 'order': 3, 'controlType': 'menu', 'baselineMissing': True},
    {'id': 'visio.shell.qat.customize.automatically-save', 'app': 'visio', 'kind': 'menuItem', 'label': 'Automatically Save', 'behaviour': 'Shows or hides the AutoSave toggle switch on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 0, 'controlType': 'button', 'idMso': 'AutoSaveSwitch', 'uiaId': 'AutoSaveSwitch'},
    {'id': 'visio.shell.qat.customize.new', 'app': 'visio', 'kind': 'menuItem', 'label': 'New', 'behaviour': 'Shows or hides the New Blank Document button on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 1, 'controlType': 'button', 'idMso': 'FileNewDefault', 'uiaId': 'FileNewDefault'},
    {'id': 'visio.shell.qat.customize.open', 'app': 'visio', 'kind': 'menuItem', 'label': 'Open', 'behaviour': 'Shows or hides the Open button on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 2, 'controlType': 'button', 'idMso': 'FileOpenUsingBackstage', 'uiaId': 'FileOpenUsingBackstage'},
    {'id': 'visio.shell.qat.customize.save', 'app': 'visio', 'kind': 'menuItem', 'label': 'Save', 'behaviour': 'Shows or hides the Save button on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 3, 'controlType': 'button', 'idMso': 'FileSave', 'uiaId': 'FileSave'},
    {'id': 'visio.shell.qat.customize.email', 'app': 'visio', 'kind': 'menuItem', 'label': 'Email', 'behaviour': 'Shows or hides the Email attachment button on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 4, 'controlType': 'button', 'idMso': 'FileSendAsAttachment', 'uiaId': 'FileSendAsAttachment'},
    {'id': 'visio.shell.qat.customize.quick-print', 'app': 'visio', 'kind': 'menuItem', 'label': 'Quick Print', 'behaviour': 'Shows or hides the Quick Print button that sends the document directly to the default printer.', 'parent': 'visio.shell.qat.customize', 'order': 5, 'controlType': 'button', 'idMso': 'FilePrintQuick', 'uiaId': 'FilePrintQuick'},
    {'id': 'visio.shell.qat.customize.print-preview-and-print', 'app': 'visio', 'kind': 'menuItem', 'label': 'Print Preview and Print', 'behaviour': 'Shows or hides the Print Preview and Print button on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 6, 'controlType': 'button', 'idMso': 'PrintPreviewAndPrint', 'uiaId': 'PrintPreviewAndPrint'},
    {'id': 'visio.shell.qat.customize.editor-f7', 'app': 'visio', 'kind': 'menuItem', 'label': 'Editor (F7)', 'behaviour': 'Shows or hides the Editor proofing command on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 7, 'controlType': 'button', 'idMso': 'WritingAssistanceCheckDocument', 'uiaId': 'WritingAssistanceCheckDocument'},
    {'id': 'visio.shell.qat.customize.read-aloud', 'app': 'visio', 'kind': 'menuItem', 'label': 'Read Aloud', 'behaviour': 'Shows or hides the Read Aloud speech command on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 8, 'controlType': 'button', 'idMso': 'ReadAloud', 'uiaId': 'ReadAloud'},
    {'id': 'visio.shell.qat.customize.undo', 'app': 'visio', 'kind': 'menuItem', 'label': 'Undo', 'behaviour': 'Shows or hides the Undo split button on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 9, 'controlType': 'button', 'idMso': 'Undo', 'uiaId': 'Undo'},
    {'id': 'visio.shell.qat.customize.redo', 'app': 'visio', 'kind': 'menuItem', 'label': 'Redo', 'behaviour': 'Shows or hides the Redo or Repeat button on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 10, 'controlType': 'button', 'idMso': 'RedoOrRepeat', 'uiaId': 'RedoOrRepeat'},
    {'id': 'visio.shell.qat.customize.draw-table', 'app': 'visio', 'kind': 'menuItem', 'label': 'Draw Table', 'behaviour': 'Shows or hides the Draw Table pen tool on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 11, 'controlType': 'button', 'idMso': 'TableDrawTable', 'uiaId': 'TableDrawTable'},
    {'id': 'visio.shell.qat.customize.touch-mouse-mode', 'app': 'visio', 'kind': 'menuItem', 'label': 'Touch/Mouse Mode', 'behaviour': 'Shows or hides the Touch or Mouse Mode spacing selector on the Quick Access Toolbar.', 'parent': 'visio.shell.qat.customize', 'order': 12, 'controlType': 'button', 'idMso': 'PointerModeOptions', 'uiaId': 'PointerModeOptions'},
    {'id': 'visio.shell.qat.customize.more-commands', 'app': 'visio', 'kind': 'menuItem', 'label': 'More Commands...', 'behaviour': 'Opens the Options dialog to the Quick Access Toolbar page for adding, removing or reordering any command.', 'parent': 'visio.shell.qat.customize', 'order': 13, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'visio.shell.qat.customize.show-below-the-ribbon', 'app': 'visio', 'kind': 'menuItem', 'label': 'Show Below the Ribbon', 'behaviour': 'Moves the Quick Access Toolbar from the title bar to a dedicated strip directly below the ribbon.', 'parent': 'visio.shell.qat.customize', 'order': 14, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'visio.shell.qat.customize.hide-quick-access-toolbar', 'app': 'visio', 'kind': 'menuItem', 'label': 'Hide Quick Access Toolbar', 'behaviour': 'Hides the Quick Access Toolbar from the window frame until re-enabled from Ribbon Display Options or Options.', 'parent': 'visio.shell.qat.customize', 'order': 15, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'visio.shell.titlebar.caption', 'app': 'visio', 'kind': 'control', 'label': 'Drawing1 - Visio Professional', 'behaviour': 'Displays the active drawing name and Visio product title across the title bar.', 'parent': 'visio.shell.region.titlebar', 'order': 2, 'controlType': 'label', 'baselineMissing': True},
    {'id': 'visio.shell.titlebar.search', 'app': 'visio', 'kind': 'control', 'label': 'Search', 'behaviour': "Focuses Visio's title bar search box (Alt+Q).", 'parent': 'visio.shell.region.titlebar', 'order': 3, 'controlType': 'menu', 'keytip': 'Q', 'uiaId': 'TellMeControlAnchor', 'baselineMissing': True},
    {'id': 'visio.shell.titlebar.account', 'app': 'visio', 'kind': 'control', 'label': 'Account', 'behaviour': "Opens the Account flyout in Visio's title bar.", 'parent': 'visio.shell.region.titlebar', 'order': 4, 'controlType': 'menu', 'keytip': 'ZP', 'uiaId': 'MeControlWidget', 'baselineMissing': True},
    {'id': 'visio.shell.titlebar.minimize', 'app': 'visio', 'kind': 'control', 'label': 'Minimize', 'behaviour': 'Minimises the Visio window.', 'parent': 'visio.shell.region.titlebar', 'order': 5, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'visio.shell.titlebar.maximize', 'app': 'visio', 'kind': 'control', 'label': 'Restore Down', 'behaviour': 'Restores or maximises the Visio window.', 'parent': 'visio.shell.region.titlebar', 'order': 6, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'visio.shell.titlebar.close', 'app': 'visio', 'kind': 'control', 'label': 'Close', 'behaviour': 'Closes the Visio application window.', 'parent': 'visio.shell.region.titlebar', 'order': 7, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'visio.shell.region.tabrow', 'app': 'visio', 'kind': 'region', 'label': 'Visio Ribbon Tab Row', 'behaviour': 'Spans the 30-pixel tab row in Visio, hosting File, Ribbon Tabs, Comments, a direct Share... button and an MDI Close Document button.', 'order': 1},
    {'id': 'visio.shell.tabrow.file', 'app': 'visio', 'kind': 'control', 'label': 'File Tab', 'behaviour': 'Opens the Visio Backstage view.', 'parent': 'visio.shell.region.tabrow', 'order': 0, 'controlType': 'button', 'keytip': 'F', 'uiaId': 'FileTabButton', 'baselineMissing': True},
    {'id': 'visio.shell.tabrow.tabs', 'app': 'visio', 'kind': 'region', 'label': 'Ribbon Tabs', 'behaviour': "Contains Visio's core and contextual ribbon tabs.", 'parent': 'visio.shell.region.tabrow', 'order': 1},
    {'id': 'visio.shell.tabrow.comments', 'app': 'visio', 'kind': 'control', 'label': 'Comments', 'behaviour': 'Toggles the diagram Comments pane in Visio.', 'parent': 'visio.shell.region.tabrow', 'order': 2, 'controlType': 'toggleButton', 'keytip': 'ZC', 'baselineMissing': True},
    {'id': 'visio.shell.tabrow.share', 'app': 'visio', 'kind': 'control', 'label': 'Share...', 'behaviour': "Opens the Share dialog directly as a push button on Visio's tab row.", 'parent': 'visio.shell.region.tabrow', 'order': 3, 'controlType': 'button', 'keytip': 'ZS', 'baselineMissing': True},
    {'id': 'visio.shell.tabrow.closeDocument', 'app': 'visio', 'kind': 'control', 'label': 'Close', 'behaviour': "Closes the active MDI drawing document window on the right end of Visio's tab row without exiting Visio.", 'parent': 'visio.shell.region.tabrow', 'order': 4, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'visio.shell.keytips.save', 'app': 'visio', 'kind': 'control', 'label': 'Save KeyTip', 'behaviour': "Triggers Save on Visio's Quick Access Toolbar when 1 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 1, 'controlType': 'label', 'keytip': '1', 'baselineMissing': True},
    {'id': 'visio.shell.keytips.undo', 'app': 'visio', 'kind': 'control', 'label': 'Undo KeyTip', 'behaviour': "Triggers Undo on Visio's Quick Access Toolbar when 2 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 2, 'controlType': 'label', 'keytip': '2', 'baselineMissing': True},
    {'id': 'visio.shell.keytips.redo', 'app': 'visio', 'kind': 'control', 'label': 'Redo KeyTip', 'behaviour': "Triggers Redo on Visio's Quick Access Toolbar when 3 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 3, 'controlType': 'label', 'keytip': '3', 'baselineMissing': True},
    {'id': 'project.shell.region.titlebar', 'app': 'project', 'kind': 'region', 'label': 'Project Title Bar', 'behaviour': "Spans the top 48 pixels of Project's window frame without AutoSave and without the title bar search box (which sits on the tab row in Project).", 'order': 0},
    {'id': 'project.shell.titlebar.systemMenu', 'app': 'project', 'kind': 'control', 'label': 'System', 'behaviour': "Opens Project's window system menu.", 'parent': 'project.shell.region.titlebar', 'order': 0, 'controlType': 'menu', 'keytip': 'Space', 'uiaId': 'MenuBar', 'baselineMissing': True},
    {'id': 'project.shell.titlebar.qat', 'app': 'project', 'kind': 'region', 'label': 'Project Quick Access Toolbar', 'behaviour': "Holds Save, Undo, Redo and Customize Quick Access Toolbar on the left side of Project's title bar.", 'parent': 'project.shell.region.titlebar', 'order': 1},
    {'id': 'project.shell.qat.save', 'app': 'project', 'kind': 'control', 'label': 'Save', 'behaviour': "Saves the active project schedule from Project's Quick Access Toolbar.", 'parent': 'project.shell.titlebar.qat', 'order': 0, 'controlType': 'button', 'keytip': '1', 'idMso': 'FileSave', 'uiaId': 'FileSave'},
    {'id': 'project.shell.qat.undo', 'app': 'project', 'kind': 'control', 'label': 'Undo', 'behaviour': 'Undoes the last schedule edit or opens the undo history drop-down in Project.', 'parent': 'project.shell.titlebar.qat', 'order': 1, 'controlType': 'splitButton', 'keytip': '2', 'idMso': 'Undo'},
    {'id': 'project.shell.qat.undo.dropdown', 'app': 'project', 'kind': 'control', 'label': 'More Options', 'behaviour': 'Opens the chronological list of recent editing actions so multiple actions can be undone together.', 'parent': 'project.shell.qat.undo', 'order': 0, 'controlType': 'menu', 'uiaId': 'Undo_Dropdown', 'baselineMissing': True},
    {'id': 'project.shell.qat.redo', 'app': 'project', 'kind': 'control', 'label': 'Redo', 'behaviour': "Redoes the last undone schedule edit as a split button on Project's Quick Access Toolbar.", 'parent': 'project.shell.titlebar.qat', 'order': 2, 'controlType': 'splitButton', 'keytip': '3', 'idMso': 'Redo'},
    {'id': 'project.shell.qat.customize', 'app': 'project', 'kind': 'control', 'label': 'Customize Quick Access Toolbar', 'behaviour': 'Opens the Quick Access Toolbar customisation menu in Project.', 'parent': 'project.shell.titlebar.qat', 'order': 3, 'controlType': 'menu', 'baselineMissing': True},
    {'id': 'project.shell.qat.customize.automatically-save', 'app': 'project', 'kind': 'menuItem', 'label': 'Automatically Save', 'behaviour': 'Shows or hides the AutoSave toggle switch on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 0, 'controlType': 'button', 'idMso': 'AutoSaveSwitch', 'uiaId': 'AutoSaveSwitch'},
    {'id': 'project.shell.qat.customize.new', 'app': 'project', 'kind': 'menuItem', 'label': 'New', 'behaviour': 'Shows or hides the New Blank Document button on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 1, 'controlType': 'button', 'idMso': 'FileNewDefault', 'uiaId': 'FileNewDefault'},
    {'id': 'project.shell.qat.customize.open', 'app': 'project', 'kind': 'menuItem', 'label': 'Open', 'behaviour': 'Shows or hides the Open button on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 2, 'controlType': 'button', 'idMso': 'FileOpenUsingBackstage', 'uiaId': 'FileOpenUsingBackstage'},
    {'id': 'project.shell.qat.customize.save', 'app': 'project', 'kind': 'menuItem', 'label': 'Save', 'behaviour': 'Shows or hides the Save button on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 3, 'controlType': 'button', 'idMso': 'FileSave', 'uiaId': 'FileSave'},
    {'id': 'project.shell.qat.customize.email', 'app': 'project', 'kind': 'menuItem', 'label': 'Email', 'behaviour': 'Shows or hides the Email attachment button on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 4, 'controlType': 'button', 'idMso': 'FileSendAsAttachment', 'uiaId': 'FileSendAsAttachment'},
    {'id': 'project.shell.qat.customize.quick-print', 'app': 'project', 'kind': 'menuItem', 'label': 'Quick Print', 'behaviour': 'Shows or hides the Quick Print button that sends the document directly to the default printer.', 'parent': 'project.shell.qat.customize', 'order': 5, 'controlType': 'button', 'idMso': 'FilePrintQuick', 'uiaId': 'FilePrintQuick'},
    {'id': 'project.shell.qat.customize.print-preview-and-print', 'app': 'project', 'kind': 'menuItem', 'label': 'Print Preview and Print', 'behaviour': 'Shows or hides the Print Preview and Print button on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 6, 'controlType': 'button', 'idMso': 'PrintPreviewAndPrint', 'uiaId': 'PrintPreviewAndPrint'},
    {'id': 'project.shell.qat.customize.editor-f7', 'app': 'project', 'kind': 'menuItem', 'label': 'Editor (F7)', 'behaviour': 'Shows or hides the Editor proofing command on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 7, 'controlType': 'button', 'idMso': 'WritingAssistanceCheckDocument', 'uiaId': 'WritingAssistanceCheckDocument'},
    {'id': 'project.shell.qat.customize.read-aloud', 'app': 'project', 'kind': 'menuItem', 'label': 'Read Aloud', 'behaviour': 'Shows or hides the Read Aloud speech command on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 8, 'controlType': 'button', 'idMso': 'ReadAloud', 'uiaId': 'ReadAloud'},
    {'id': 'project.shell.qat.customize.undo', 'app': 'project', 'kind': 'menuItem', 'label': 'Undo', 'behaviour': 'Shows or hides the Undo split button on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 9, 'controlType': 'button', 'idMso': 'Undo', 'uiaId': 'Undo'},
    {'id': 'project.shell.qat.customize.redo', 'app': 'project', 'kind': 'menuItem', 'label': 'Redo', 'behaviour': 'Shows or hides the Redo or Repeat button on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 10, 'controlType': 'button', 'idMso': 'RedoOrRepeat', 'uiaId': 'RedoOrRepeat'},
    {'id': 'project.shell.qat.customize.draw-table', 'app': 'project', 'kind': 'menuItem', 'label': 'Draw Table', 'behaviour': 'Shows or hides the Draw Table pen tool on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 11, 'controlType': 'button', 'idMso': 'TableDrawTable', 'uiaId': 'TableDrawTable'},
    {'id': 'project.shell.qat.customize.touch-mouse-mode', 'app': 'project', 'kind': 'menuItem', 'label': 'Touch/Mouse Mode', 'behaviour': 'Shows or hides the Touch or Mouse Mode spacing selector on the Quick Access Toolbar.', 'parent': 'project.shell.qat.customize', 'order': 12, 'controlType': 'button', 'idMso': 'PointerModeOptions', 'uiaId': 'PointerModeOptions'},
    {'id': 'project.shell.qat.customize.more-commands', 'app': 'project', 'kind': 'menuItem', 'label': 'More Commands...', 'behaviour': 'Opens the Options dialog to the Quick Access Toolbar page for adding, removing or reordering any command.', 'parent': 'project.shell.qat.customize', 'order': 13, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'project.shell.qat.customize.show-below-the-ribbon', 'app': 'project', 'kind': 'menuItem', 'label': 'Show Below the Ribbon', 'behaviour': 'Moves the Quick Access Toolbar from the title bar to a dedicated strip directly below the ribbon.', 'parent': 'project.shell.qat.customize', 'order': 14, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'project.shell.qat.customize.hide-quick-access-toolbar', 'app': 'project', 'kind': 'menuItem', 'label': 'Hide Quick Access Toolbar', 'behaviour': 'Hides the Quick Access Toolbar from the window frame until re-enabled from Ribbon Display Options or Options.', 'parent': 'project.shell.qat.customize', 'order': 15, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'project.shell.titlebar.caption', 'app': 'project', 'kind': 'control', 'label': 'Project Professional', 'behaviour': 'Displays the active project name and Project Professional title across the title bar.', 'parent': 'project.shell.region.titlebar', 'order': 2, 'controlType': 'label', 'baselineMissing': True},
    {'id': 'project.shell.titlebar.account', 'app': 'project', 'kind': 'control', 'label': 'Account', 'behaviour': "Opens the Account flyout in Project's title bar.", 'parent': 'project.shell.region.titlebar', 'order': 3, 'controlType': 'menu', 'keytip': 'ZP', 'uiaId': 'MeControlWidget', 'baselineMissing': True},
    {'id': 'project.shell.titlebar.minimize', 'app': 'project', 'kind': 'control', 'label': 'Minimize', 'behaviour': 'Minimises the Project window.', 'parent': 'project.shell.region.titlebar', 'order': 4, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'project.shell.titlebar.maximize', 'app': 'project', 'kind': 'control', 'label': 'Restore Down', 'behaviour': 'Restores or maximises the Project window.', 'parent': 'project.shell.region.titlebar', 'order': 5, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'project.shell.titlebar.close', 'app': 'project', 'kind': 'control', 'label': 'Close', 'behaviour': 'Closes the Project application window.', 'parent': 'project.shell.region.titlebar', 'order': 6, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'project.shell.region.tabrow', 'app': 'project', 'kind': 'region', 'label': 'Project Ribbon Tab Row', 'behaviour': 'Spans the 30-pixel tab row in Project, hosting File, Ribbon Tabs and the inline Tell Me search box after the Help tab.', 'order': 1},
    {'id': 'project.shell.tabrow.file', 'app': 'project', 'kind': 'control', 'label': 'File Tab', 'behaviour': 'Opens the Project Backstage view.', 'parent': 'project.shell.region.tabrow', 'order': 0, 'controlType': 'button', 'keytip': 'F', 'uiaId': 'FileTabButton', 'baselineMissing': True},
    {'id': 'project.shell.tabrow.tabs', 'app': 'project', 'kind': 'region', 'label': 'Ribbon Tabs', 'behaviour': "Contains Project's core and contextual ribbon tabs (Task, Resource, Report, Project, View, Help, Task Form).", 'parent': 'project.shell.region.tabrow', 'order': 1},
    {'id': 'project.shell.tabrow.search', 'app': 'project', 'kind': 'control', 'label': 'Tell me what you want to do', 'behaviour': "Focuses the Tell Me command search box placed inline on Project's tab row immediately to the right of the Help tab.", 'parent': 'project.shell.region.tabrow', 'order': 2, 'controlType': 'menu', 'keytip': 'Q', 'uiaId': 'TellMeControlAnchor', 'baselineMissing': True},
    {'id': 'project.shell.search.input', 'app': 'project', 'kind': 'control', 'label': 'Search Input', 'behaviour': 'Accepts text queries (Alt+Q) to search commands, document text, help topics and connected files.', 'parent': 'project.shell.tabrow.search', 'order': 0, 'controlType': 'editBox', 'keytip': 'Q', 'uiaId': 'TellMeTextBoxAutomationId', 'baselineMissing': True},
    {'id': 'project.shell.search.voice', 'app': 'project', 'kind': 'control', 'label': 'Voice Search', 'behaviour': 'Starts microphone dictation into the search box to find commands or content by voice.', 'parent': 'project.shell.tabrow.search', 'order': 1, 'controlType': 'button', 'keytip': 'Q', 'baselineMissing': True},
    {'id': 'project.shell.search.flyout', 'app': 'project', 'kind': 'region', 'label': 'Search Flyout', 'behaviour': 'Displays categorised command, document, people, file and help results beneath the title bar search box.', 'parent': 'project.shell.tabrow.search', 'order': 2},
    {'id': 'project.shell.search.recentActions', 'app': 'project', 'kind': 'group', 'label': 'Recently Used Actions', 'behaviour': 'Lists the commands most recently invoked from the search box for one-click reuse.', 'parent': 'project.shell.search.flyout', 'order': 0, 'baselineMissing': True},
    {'id': 'project.shell.search.suggestedActions', 'app': 'project', 'kind': 'group', 'label': 'Suggested Actions', 'behaviour': 'Lists contextually relevant commands when the search box is first opened before typing a query.', 'parent': 'project.shell.search.flyout', 'order': 1, 'baselineMissing': True},
    {'id': 'project.shell.search.suggestedActions.spelling-and-grammar', 'app': 'project', 'kind': 'menuItem', 'label': 'Spelling and Grammar', 'behaviour': 'Runs the spelling and grammar checker on the active document from the default Suggested Actions list.', 'parent': 'project.shell.search.suggestedActions', 'order': 0, 'controlType': 'galleryItem', 'baselineMissing': True},
    {'id': 'project.shell.search.suggestedActions.word-count', 'app': 'project', 'kind': 'menuItem', 'label': 'Word Count', 'behaviour': 'Opens the Word Count statistics dialog from the default Suggested Actions list.', 'parent': 'project.shell.search.suggestedActions', 'order': 1, 'controlType': 'galleryItem', 'baselineMissing': True},
    {'id': 'project.shell.search.suggestedActions.print', 'app': 'project', 'kind': 'menuItem', 'label': 'Print', 'behaviour': 'Opens the Backstage Print page from the default Suggested Actions list.', 'parent': 'project.shell.search.suggestedActions', 'order': 2, 'controlType': 'galleryItem', 'baselineMissing': True},
    {'id': 'project.shell.search.people', 'app': 'project', 'kind': 'group', 'label': 'People', 'behaviour': 'Lists collaborators and contacts matching the search query without exposing personal identities in the static inventory.', 'parent': 'project.shell.search.flyout', 'order': 2, 'baselineMissing': True},
    {'id': 'project.shell.search.actions', 'app': 'project', 'kind': 'group', 'label': 'Actions', 'behaviour': 'Lists matching application commands and menus with direct execution and nested submenus as the user types.', 'parent': 'project.shell.search.flyout', 'order': 3, 'baselineMissing': True},
    {'id': 'project.shell.search.findInDocument', 'app': 'project', 'kind': 'group', 'label': 'Find in Document', 'behaviour': "Searches the active document's text for the typed query and jumps to matching occurrences.", 'parent': 'project.shell.search.flyout', 'order': 4, 'baselineMissing': True},
    {'id': 'project.shell.search.files', 'app': 'project', 'kind': 'group', 'label': 'Files', 'behaviour': 'Lists recent and cloud documents whose titles or contents match the search query.', 'parent': 'project.shell.search.flyout', 'order': 5, 'baselineMissing': True},
    {'id': 'project.shell.search.help', 'app': 'project', 'kind': 'group', 'label': 'Help', 'behaviour': 'Lists documentation and help articles matching the search query.', 'parent': 'project.shell.search.flyout', 'order': 6, 'baselineMissing': True},
    {'id': 'project.shell.keytips.save', 'app': 'project', 'kind': 'control', 'label': 'Save KeyTip', 'behaviour': "Triggers Save on Project's Quick Access Toolbar when 1 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 1, 'controlType': 'label', 'keytip': '1', 'baselineMissing': True},
    {'id': 'project.shell.keytips.undo', 'app': 'project', 'kind': 'control', 'label': 'Undo KeyTip', 'behaviour': "Triggers Undo on Project's Quick Access Toolbar when 2 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 2, 'controlType': 'label', 'keytip': '2', 'baselineMissing': True},
    {'id': 'project.shell.keytips.redo', 'app': 'project', 'kind': 'control', 'label': 'Redo KeyTip', 'behaviour': "Triggers Redo on Project's Quick Access Toolbar when 3 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 3, 'controlType': 'label', 'keytip': '3', 'baselineMissing': True},
    {'id': 'project.shell.keytips.search', 'app': 'project', 'kind': 'control', 'label': 'Search KeyTip', 'behaviour': "Focuses Project's tab-row Tell Me search box when Q is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 5, 'controlType': 'label', 'keytip': 'Q', 'baselineMissing': True},
    {'id': 'outlook.explorer.shell.region.titlebar', 'app': 'outlook', 'kind': 'region', 'label': 'Outlook Explorer Title Bar', 'behaviour': "Hosts the system menu, explorer Quick Access Toolbar, module caption, search box, account widget and window caption buttons in classic Outlook's main window.", 'order': 0},
    {'id': 'outlook.explorer.shell.titlebar.systemMenu', 'app': 'outlook', 'kind': 'control', 'label': 'System', 'behaviour': "Opens classic Outlook's explorer window system menu.", 'parent': 'outlook.explorer.shell.region.titlebar', 'order': 0, 'controlType': 'menu', 'keytip': 'Space', 'uiaId': 'MenuBar', 'baselineMissing': True},
    {'id': 'outlook.explorer.shell.titlebar.qat', 'app': 'outlook', 'kind': 'region', 'label': 'Outlook Explorer Quick Access Toolbar', 'behaviour': "Holds Send/Receive All Folders, Undo, Simplified Ribbon toggle, Minimize the Ribbon and Find a Contact in classic Outlook's explorer window.", 'parent': 'outlook.explorer.shell.region.titlebar', 'order': 1},
    {'id': 'outlook.explorer.shell.qat.sendReceiveAll', 'app': 'outlook', 'kind': 'control', 'label': 'Send/Receive All Folders', 'behaviour': "Synchronises all mail, calendar and contact folders with connected mail servers from Outlook's explorer Quick Access Toolbar.", 'parent': 'outlook.explorer.shell.titlebar.qat', 'order': 0, 'controlType': 'button', 'keytip': '1', 'idMso': 'SendReceiveAll'},
    {'id': 'outlook.explorer.shell.qat.undo', 'app': 'outlook', 'kind': 'control', 'label': 'Undo', 'behaviour': "Reverses the last folder or item action in Outlook's explorer window.", 'parent': 'outlook.explorer.shell.titlebar.qat', 'order': 1, 'controlType': 'splitButton', 'keytip': '2', 'idMso': 'Undo'},
    {'id': 'outlook.explorer.shell.qat.singleLineRibbonToggle', 'app': 'outlook', 'kind': 'control', 'label': 'Simplified Ribbon', 'behaviour': 'Toggles the explorer ribbon between the three-row Classic layout and the single-line Simplified layout.', 'parent': 'outlook.explorer.shell.titlebar.qat', 'order': 2, 'controlType': 'toggleButton', 'idMso': 'SingleLineRibbonToggle'},
    {'id': 'outlook.explorer.shell.qat.minimizeRibbon', 'app': 'outlook', 'kind': 'control', 'label': 'Minimize the Ribbon', 'behaviour': "Collapses or expands the ribbon in Outlook's explorer window.", 'parent': 'outlook.explorer.shell.titlebar.qat', 'order': 3, 'controlType': 'toggleButton', 'idMso': 'MinimizeRibbon'},
    {'id': 'outlook.explorer.shell.qat.findContactCombo', 'app': 'outlook', 'kind': 'control', 'label': 'Find a Contact', 'behaviour': "Searches the address book for a contact directly from Outlook's explorer Quick Access Toolbar.", 'parent': 'outlook.explorer.shell.titlebar.qat', 'order': 4, 'controlType': 'comboBox', 'idMso': 'FindContactCombo'},
    {'id': 'outlook.explorer.shell.titlebar.caption', 'app': 'outlook', 'kind': 'control', 'label': 'Inbox - Outlook', 'behaviour': 'Displays the active folder name and Outlook title across the explorer title bar.', 'parent': 'outlook.explorer.shell.region.titlebar', 'order': 2, 'controlType': 'label', 'baselineMissing': True},
    {'id': 'outlook.explorer.shell.titlebar.search', 'app': 'outlook', 'kind': 'control', 'label': 'Search', 'behaviour': "Focuses classic Outlook's title bar search box for mail, calendar, contacts and commands.", 'parent': 'outlook.explorer.shell.region.titlebar', 'order': 3, 'controlType': 'menu', 'keytip': 'Q', 'uiaId': 'TellMeControlAnchor', 'baselineMissing': True},
    {'id': 'outlook.explorer.shell.titlebar.account', 'app': 'outlook', 'kind': 'control', 'label': 'Account', 'behaviour': "Opens the Account flyout in classic Outlook's explorer title bar.", 'parent': 'outlook.explorer.shell.region.titlebar', 'order': 4, 'controlType': 'menu', 'keytip': 'ZP', 'uiaId': 'MeControlWidget', 'baselineMissing': True},
    {'id': 'outlook.explorer.shell.titlebar.minimize', 'app': 'outlook', 'kind': 'control', 'label': 'Minimize', 'behaviour': 'Minimises the classic Outlook explorer window.', 'parent': 'outlook.explorer.shell.region.titlebar', 'order': 5, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'outlook.explorer.shell.titlebar.maximize', 'app': 'outlook', 'kind': 'control', 'label': 'Restore Down', 'behaviour': 'Restores or maximises the classic Outlook explorer window.', 'parent': 'outlook.explorer.shell.region.titlebar', 'order': 6, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'outlook.explorer.shell.titlebar.close', 'app': 'outlook', 'kind': 'control', 'label': 'Close', 'behaviour': 'Closes the classic Outlook explorer window.', 'parent': 'outlook.explorer.shell.region.titlebar', 'order': 7, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'outlook.explorer.shell.region.tabrow', 'app': 'outlook', 'kind': 'region', 'label': 'Outlook Explorer Ribbon Tab Row', 'behaviour': "Hosts the File tab and module ribbon tabs across classic Outlook's explorer tab row.", 'order': 1},
    {'id': 'outlook.explorer.shell.tabrow.file', 'app': 'outlook', 'kind': 'control', 'label': 'File Tab', 'behaviour': 'Opens the classic Outlook Backstage view.', 'parent': 'outlook.explorer.shell.region.tabrow', 'order': 0, 'controlType': 'button', 'keytip': 'F', 'uiaId': 'FileTabButton', 'baselineMissing': True},
    {'id': 'outlook.explorer.shell.tabrow.tabs', 'app': 'outlook', 'kind': 'region', 'label': 'Ribbon Tabs', 'behaviour': "Contains classic Outlook's explorer module and contextual ribbon tabs.", 'parent': 'outlook.explorer.shell.region.tabrow', 'order': 1},
    {'id': 'outlook.explorer.shell.keytips.sendReceiveAll', 'app': 'outlook', 'kind': 'control', 'label': 'Send/Receive All Folders KeyTip', 'behaviour': "Triggers Send/Receive All Folders on Outlook's explorer Quick Access Toolbar when 1 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 0, 'controlType': 'label', 'keytip': '1', 'baselineMissing': True},
    {'id': 'outlook.explorer.shell.keytips.undo', 'app': 'outlook', 'kind': 'control', 'label': 'Undo KeyTip', 'behaviour': "Triggers Undo on Outlook's explorer Quick Access Toolbar when 2 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 1, 'controlType': 'label', 'keytip': '2', 'baselineMissing': True},
    {'id': 'outlook.compose.shell.region.titlebar', 'app': 'outlook', 'kind': 'region', 'label': 'Outlook Item Window Title Bar', 'behaviour': 'Hosts the system menu, item-window Quick Access Toolbar, item subject caption, search box, account widget and caption buttons in classic Outlook inspector windows.', 'order': 0},
    {'id': 'outlook.compose.shell.titlebar.systemMenu', 'app': 'outlook', 'kind': 'control', 'label': 'System', 'behaviour': 'Opens the classic Outlook item window system menu.', 'parent': 'outlook.compose.shell.region.titlebar', 'order': 0, 'controlType': 'menu', 'keytip': 'Space', 'uiaId': 'MenuBar', 'baselineMissing': True},
    {'id': 'outlook.compose.shell.titlebar.qat', 'app': 'outlook', 'kind': 'region', 'label': 'Outlook Item Window Quick Access Toolbar', 'behaviour': 'Holds Save, Undo, Redo, Simplified Ribbon toggle and Minimize the Ribbon in classic Outlook item windows.', 'parent': 'outlook.compose.shell.region.titlebar', 'order': 1},
    {'id': 'outlook.compose.shell.qat.save', 'app': 'outlook', 'kind': 'control', 'label': 'Save', 'behaviour': "Saves the open mail draft, appointment, contact or task in Outlook's item window.", 'parent': 'outlook.compose.shell.titlebar.qat', 'order': 0, 'controlType': 'button', 'keytip': '1', 'idMso': 'FileSave'},
    {'id': 'outlook.compose.shell.qat.undo', 'app': 'outlook', 'kind': 'control', 'label': 'Undo', 'behaviour': 'Undoes the last editing action inside the Outlook item window.', 'parent': 'outlook.compose.shell.titlebar.qat', 'order': 1, 'controlType': 'splitButton', 'keytip': '2', 'idMso': 'Undo'},
    {'id': 'outlook.compose.shell.qat.redo', 'app': 'outlook', 'kind': 'control', 'label': 'Redo', 'behaviour': 'Redoes the last undone editing action inside the Outlook item window.', 'parent': 'outlook.compose.shell.titlebar.qat', 'order': 2, 'controlType': 'splitButton', 'keytip': '3', 'idMso': 'RedoOrRepeat'},
    {'id': 'outlook.compose.shell.qat.singleLineRibbonToggle', 'app': 'outlook', 'kind': 'control', 'label': 'Simplified Ribbon', 'behaviour': "Toggles the item window's ribbon between the Classic layout and the single-line Simplified layout.", 'parent': 'outlook.compose.shell.titlebar.qat', 'order': 3, 'controlType': 'toggleButton', 'idMso': 'SingleLineRibbonToggle'},
    {'id': 'outlook.compose.shell.qat.minimizeRibbon', 'app': 'outlook', 'kind': 'control', 'label': 'Minimize the Ribbon', 'behaviour': 'Collapses or expands the ribbon inside the Outlook item window.', 'parent': 'outlook.compose.shell.titlebar.qat', 'order': 4, 'controlType': 'toggleButton', 'idMso': 'MinimizeRibbon'},
    {'id': 'outlook.compose.shell.titlebar.caption', 'app': 'outlook', 'kind': 'control', 'label': 'Untitled - Message (HTML)', 'behaviour': 'Displays the active item subject and message format across the Outlook inspector title bar.', 'parent': 'outlook.compose.shell.region.titlebar', 'order': 2, 'controlType': 'label', 'baselineMissing': True},
    {'id': 'outlook.compose.shell.titlebar.search', 'app': 'outlook', 'kind': 'control', 'label': 'Search', 'behaviour': 'Focuses the search box inside the classic Outlook item window.', 'parent': 'outlook.compose.shell.region.titlebar', 'order': 3, 'controlType': 'menu', 'keytip': 'Q', 'uiaId': 'TellMeControlAnchor', 'baselineMissing': True},
    {'id': 'outlook.compose.shell.titlebar.account', 'app': 'outlook', 'kind': 'control', 'label': 'Account', 'behaviour': 'Opens the Account flyout in the classic Outlook item window title bar.', 'parent': 'outlook.compose.shell.region.titlebar', 'order': 4, 'controlType': 'menu', 'keytip': 'ZP', 'uiaId': 'MeControlWidget', 'baselineMissing': True},
    {'id': 'outlook.compose.shell.titlebar.minimize', 'app': 'outlook', 'kind': 'control', 'label': 'Minimize', 'behaviour': 'Minimises the classic Outlook item window.', 'parent': 'outlook.compose.shell.region.titlebar', 'order': 5, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'outlook.compose.shell.titlebar.maximize', 'app': 'outlook', 'kind': 'control', 'label': 'Restore Down', 'behaviour': 'Restores or maximises the classic Outlook item window.', 'parent': 'outlook.compose.shell.region.titlebar', 'order': 6, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'outlook.compose.shell.titlebar.close', 'app': 'outlook', 'kind': 'control', 'label': 'Close', 'behaviour': 'Closes the classic Outlook item window.', 'parent': 'outlook.compose.shell.region.titlebar', 'order': 7, 'controlType': 'button', 'baselineMissing': True},
    {'id': 'outlook.compose.shell.region.tabrow', 'app': 'outlook', 'kind': 'region', 'label': 'Outlook Item Window Ribbon Tab Row', 'behaviour': "Hosts the File tab and inspector ribbon tabs across classic Outlook's item window tab row.", 'order': 1},
    {'id': 'outlook.compose.shell.tabrow.file', 'app': 'outlook', 'kind': 'control', 'label': 'File Tab', 'behaviour': 'Opens the classic Outlook item window Backstage view.', 'parent': 'outlook.compose.shell.region.tabrow', 'order': 0, 'controlType': 'button', 'keytip': 'F', 'uiaId': 'FileTabButton', 'baselineMissing': True},
    {'id': 'outlook.compose.shell.tabrow.tabs', 'app': 'outlook', 'kind': 'region', 'label': 'Ribbon Tabs', 'behaviour': "Contains classic Outlook's item window core and contextual ribbon tabs.", 'parent': 'outlook.compose.shell.region.tabrow', 'order': 1},
    {'id': 'outlook.compose.shell.keytips.save', 'app': 'outlook', 'kind': 'control', 'label': 'Save KeyTip', 'behaviour': "Triggers Save on Outlook's item window Quick Access Toolbar when 1 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 1, 'controlType': 'label', 'keytip': '1', 'baselineMissing': True},
    {'id': 'outlook.compose.shell.keytips.undo', 'app': 'outlook', 'kind': 'control', 'label': 'Undo KeyTip', 'behaviour': "Triggers Undo on Outlook's item window Quick Access Toolbar when 2 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 2, 'controlType': 'label', 'keytip': '2', 'baselineMissing': True},
    {'id': 'outlook.compose.shell.keytips.redo', 'app': 'outlook', 'kind': 'control', 'label': 'Redo KeyTip', 'behaviour': "Triggers Redo on Outlook's item window Quick Access Toolbar when 3 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 3, 'controlType': 'label', 'keytip': '3', 'baselineMissing': True},
    {'id': 'excel.shell.keytips.redo', 'app': 'excel', 'kind': 'control', 'label': 'Redo KeyTip', 'behaviour': "Triggers Redo on Excel's Quick Access Toolbar when 4 is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 3, 'controlType': 'label', 'keytip': '4', 'baselineMissing': True},
    {'id': 'excel.shell.keytips.documentTitle', 'app': 'excel', 'kind': 'control', 'label': 'Document Title KeyTip', 'behaviour': "Opens the workbook title and file location flyout in Excel's title bar when B is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 4, 'controlType': 'label', 'keytip': 'B', 'baselineMissing': True},
    {'id': 'excel.shell.keytips.comments', 'app': 'excel', 'kind': 'control', 'label': 'Comments KeyTip', 'behaviour': 'Toggles the workbook Comments pane when Z then C is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 8, 'controlType': 'label', 'keytip': 'ZC', 'baselineMissing': True},
    {'id': 'powerpoint.shell.keytips.comments', 'app': 'powerpoint', 'kind': 'control', 'label': 'Comments KeyTip', 'behaviour': 'Toggles the presentation Comments pane when Z then C is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 8, 'controlType': 'label', 'keytip': 'ZC', 'baselineMissing': True},
    {'id': 'visio.shell.keytips.search', 'app': 'visio', 'kind': 'control', 'label': 'Search KeyTip', 'behaviour': "Focuses Visio's title bar search box when Q is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 5, 'controlType': 'label', 'keytip': 'Q', 'baselineMissing': True},
    {'id': 'visio.shell.keytips.account', 'app': 'visio', 'kind': 'control', 'label': 'Account KeyTip', 'behaviour': "Opens the Account flyout in Visio's title bar when Z then P is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 6, 'controlType': 'label', 'keytip': 'ZP', 'baselineMissing': True},
    {'id': 'visio.shell.keytips.file', 'app': 'visio', 'kind': 'control', 'label': 'File KeyTip', 'behaviour': 'Opens the Visio Backstage view when F is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 7, 'controlType': 'label', 'keytip': 'F', 'baselineMissing': True},
    {'id': 'visio.shell.keytips.comments', 'app': 'visio', 'kind': 'control', 'label': 'Comments KeyTip', 'behaviour': 'Toggles the drawing Comments pane when Z then C is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 8, 'controlType': 'label', 'keytip': 'ZC', 'baselineMissing': True},
    {'id': 'visio.shell.keytips.share', 'app': 'visio', 'kind': 'control', 'label': 'Share KeyTip', 'behaviour': "Triggers the Share command on Visio's tab row when Z then S is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 10, 'controlType': 'label', 'keytip': 'ZS', 'baselineMissing': True},
    {'id': 'project.shell.keytips.account', 'app': 'project', 'kind': 'control', 'label': 'Account KeyTip', 'behaviour': "Opens the Account flyout in Project's title bar when Z then P is pressed in KeyTip mode.", 'parent': 'shell.keytips.layer', 'order': 6, 'controlType': 'label', 'keytip': 'ZP', 'baselineMissing': True},
    {'id': 'project.shell.keytips.file', 'app': 'project', 'kind': 'control', 'label': 'File KeyTip', 'behaviour': 'Opens the Project Backstage view when F is pressed in KeyTip mode.', 'parent': 'shell.keytips.layer', 'order': 7, 'controlType': 'label', 'keytip': 'F', 'baselineMissing': True},
)


def build_shell_chrome_records(build=None, app_name=None):
    """Build unmeasured shell chrome record templates from `_SHELL_SPEC` (filtered by `app_name` when given)."""
    _ = build or reference_build()
    base_src = f"baseline:{BASELINE_COMMIT}"
    target_app = ("shell" if app_name == "word" else app_name) if app_name is not None else None
    out = []
    for item in _SHELL_SPEC:
        if target_app is not None and item["app"] != target_app:
            continue
        rec = dict(item)
        rec["label"] = sanitize_shell_label(rec["label"], rec.get("uiaId", ""), rec.get("idMso", ""))
        rec["source"] = base_src
        out.append(rec)
    return out


def _is_offscreen(el):
    off = getattr(el, "is_offscreen", False)
    return bool(off() if callable(off) else off)


def _live_rect_bounds(el, ox, oy):
    if _is_offscreen(el):
        return None
    rect = getattr(el, "rect", None)
    if not rect or len(rect) != 4 or rect == (0, 0, 10, 10):
        return None
    l, t, r, b = rect
    if r <= l or b <= t:
        return None
    return {"x": l - ox, "y": t - oy, "width": r - l, "height": b - t}


def _find_in(elements, pred):
    for e in elements:
        try:
            if _is_offscreen(e):
                continue
            if pred(e):
                return e
        except Exception:
            continue
    return None


def _shell_surface_key(sid):
    if sid.startswith("shell.qat.customize."):
        return "qat.customize"
    if sid.startswith("shell.tabrow.editingMode."):
        return "tabrow.editingMode"
    if sid.startswith("shell.tabrow.share."):
        return "tabrow.share"
    if sid.startswith("shell.ribbonDisplay.") and sid != "shell.ribbonDisplay.button":
        return "ribbonDisplay"
    if sid.startswith("shell.search.") and sid not in ("shell.search.input", "shell.search.voice"):
        return "search"
    if sid == "shell.statusbar.customizeMenu":
        return "statusbar.customizeMenu"
    if sid.startswith("shell.backstage."):
        return "backstage"
    if sid.startswith("shell.keytips."):
        return "keytips"
    return "base"


def _element_identity(el):
    if hasattr(el, "runtime_id"):
        try:
            rid = el.runtime_id()
            if rid:
                return ("rid", tuple(rid))
        except Exception:
            pass
    return (
        "sig",
        getattr(el, "control_type", ""),
        getattr(el, "automation_id", ""),
        getattr(el, "name", ""),
        getattr(el, "rect", None),
    )


def _visible_rect_tuple(el):
    b = _live_rect_bounds(el, 0, 0)
    return None if b is None else (b["x"], b["y"], b["width"], b["height"])


_ABSENT = object()


def _walk_with_ancestors(element, depth=25, ancestors=()):
    yield element, ancestors
    if depth <= 0:
        return
    next_anc = ancestors + (element,)
    for child in element.children():
        yield from _walk_with_ancestors(child, depth - 1, next_anc)


def _is_surface_candidate(surface_key, el, ancestors=()):
    ctype = getattr(el, "control_type", "")
    aid = getattr(el, "automation_id", "") or ""
    name = (getattr(el, "name", "") or "").strip()
    if surface_key != "statusbar.customizeMenu":
        if ctype == "StatusBar" or aid.startswith("StatusBar"):
            return False
        if any(
            getattr(a, "control_type", "") == "StatusBar"
            or (getattr(a, "automation_id", "") or "").startswith("StatusBar")
            for a in ancestors
        ):
            return False
        if re.match(r"^(Page \d+ of \d+|\d+ of \d+|Words:?\s*\d+|Character.*|\d+\s*%)$", name, re.I):
            return False
    if surface_key == "keytips":
        if ctype not in ("Pane", "Text", "ToolTip", "Custom"):
            return False
        if not name:
            vrect = _visible_rect_tuple(el)
            return bool(
                keytip(getattr(el, "access_key", ""))
                and vrect is not None
                and vrect[2] <= 36
                and vrect[3] <= 24
            )
        if "keytip" in name.casefold():
            return True
        if re.fullmatch(r"[A-Z0-9]{1,4}", name):
            return True
        if keytip(getattr(el, "access_key", "")):
            return True
        return False
    if surface_key == "statusbar.customizeMenu":
        if ctype in ("Menu", "MenuItem", "ListItem", "CheckBox", "RadioButton"):
            return True
        return any(getattr(a, "control_type", "") == "Menu" for a in ancestors)
    if surface_key in ("qat.customize", "tabrow.editingMode", "tabrow.share", "ribbonDisplay"):
        if ctype in ("Menu", "MenuItem", "ListItem", "CheckBox", "RadioButton", "Pane", "Group", "List"):
            return True
        if any(getattr(a, "control_type", "") == "Menu" for a in ancestors):
            return True
        return ctype in ITEM_TYPES
    return True


def _open_and_collect_shell_surface(surface_key, target, root, uia, win, launched):
    if launched is not None and hasattr(launched, "check_alone"):
        launched.check_alone()
    hwnd = getattr(launched, "hwnd", None)
    pid = getattr(getattr(launched, "proc", None), "pid", None)
    has_popups = win is not None and hasattr(win, "popups") and pid is not None
    before_root = uia.element(hwnd) if (uia is not None and hwnd is not None) else root
    before_pairs = list(_walk_with_ancestors(before_root, 25))
    before_nodes = [el for el, _anc in before_pairs]
    before_state = {
        _element_identity(el): _visible_rect_tuple(el)
        for el in before_nodes
    }
    before_sig_counts = {}
    before_key_counts = {}
    before_rect_counts = {}
    before_aid_counts = {}
    before_anchor_by_eid = {}
    for el in before_nodes:
        eid = _element_identity(el)
        vrect = _visible_rect_tuple(el)
        if vrect is not None:
            ctype = getattr(el, "control_type", "")
            aid = getattr(el, "automation_id", "") or ""
            kt = keytip(getattr(el, "access_key", ""))
            sig = (ctype, aid, getattr(el, "name", ""), kt, vrect)
            key = (ctype, aid, getattr(el, "name", ""), kt)
            rkey = (ctype, vrect)
            anchor = (ctype, vrect[0], vrect[1], vrect[3])
            before_sig_counts[sig] = before_sig_counts.get(sig, 0) + 1
            before_key_counts[key] = before_key_counts.get(key, 0) + 1
            before_rect_counts[rkey] = before_rect_counts.get(rkey, 0) + 1
            if aid:
                before_aid_counts[(ctype, aid)] = before_aid_counts.get((ctype, aid), 0) + 1
            before_anchor_by_eid[eid] = anchor
    before_popups = list(win.popups(pid)) if has_popups else []
    can_expand = False
    can_select = False
    if surface_key == "keytips":
        if win is None or not hasattr(win, "activate_keytips") or not hasattr(win, "deactivate_keytips"):
            raise Refused("cannot activate or deactivate KeyTips without window keyboard support")
        win.activate_keytips(hwnd, root)
    elif surface_key == "statusbar.customizeMenu":
        if target is None:
            raise Refused("cannot open status bar context menu without status bar element")
        if win is None or not hasattr(win, "open_context_menu") or not hasattr(win, "dismiss_surface"):
            raise Refused("cannot open or dismiss status bar context menu without window support")
        win.open_context_menu(hwnd, target)
    else:
        if target is None:
            raise Refused(f"shell trigger for surface {surface_key!r} was not found in the window")
        can_expand = getattr(target, "expand_state", lambda: None)() is not None
        if not can_expand:
            try:
                can_select = target.pattern("select") is not None
            except Exception:
                can_select = False
        if not can_expand and not can_select:
            raise Refused(
                f"shell trigger {getattr(target, 'name', surface_key)!r} for surface {surface_key!r} "
                "does not support ExpandCollapse or SelectionItem"
            )
        if can_expand:
            if not callable(getattr(target, "collapse", None)):
                raise Refused(f"shell trigger {getattr(target, 'name', surface_key)!r} is missing collapse support")
            target.expand()
        else:
            if win is None or not hasattr(win, "dismiss_surface"):
                raise Refused(f"cannot dismiss shell surface {surface_key!r} without window dismissal support")
            target.select()
    surface_collected = []
    opened_state = {}
    opened_sigs = set()
    opened_keys = set()
    cleanup_err = None
    try:
        time.sleep(0.1)
        live_root = uia.element(hwnd) if (uia is not None and hwnd is not None) else root
        live_pairs = list(_walk_with_ancestors(live_root, 25))
        live_nodes = [el for el, _anc in live_pairs]
        live_eids = {_element_identity(el) for el in live_nodes if _visible_rect_tuple(el) is not None}
        disappeared_anchors = {}
        for eid, anchor in before_anchor_by_eid.items():
            if eid not in live_eids:
                disappeared_anchors[anchor] = disappeared_anchors.get(anchor, 0) + 1
        kept_sig_counts = {}
        kept_rect_counts = {}
        kept_aid_counts = {}
        used_disappeared_anchors = {}
        for el in live_nodes:
            eid = _element_identity(el)
            vrect = _visible_rect_tuple(el)
            if vrect is not None and eid in before_state and before_state[eid] is not None:
                ctype = getattr(el, "control_type", "")
                aid = getattr(el, "automation_id", "") or ""
                if aid:
                    kept_aid_counts[(ctype, aid)] = kept_aid_counts.get((ctype, aid), 0) + 1
            if vrect is not None and before_state.get(eid, _ABSENT) == vrect:
                ctype = getattr(el, "control_type", "")
                kt = keytip(getattr(el, "access_key", ""))
                sig = (ctype, getattr(el, "automation_id", ""), getattr(el, "name", ""), kt, vrect)
                rkey = (ctype, vrect)
                kept_sig_counts[sig] = kept_sig_counts.get(sig, 0) + 1
                kept_rect_counts[rkey] = kept_rect_counts.get(rkey, 0) + 1
        for el, ancestors in live_pairs:
            eid = _element_identity(el)
            vrect = _visible_rect_tuple(el)
            prev_vrect = before_state.get(eid, _ABSENT)
            if vrect is not None and (prev_vrect is _ABSENT or vrect != prev_vrect):
                if not _is_surface_candidate(surface_key, el, ancestors):
                    continue
                ctype = getattr(el, "control_type", "")
                aid = getattr(el, "automation_id", "") or ""
                name = getattr(el, "name", "") or ""
                kt = keytip(getattr(el, "access_key", ""))
                sig = (ctype, aid, name, kt, vrect)
                rkey = (ctype, vrect)
                anchor = (ctype, vrect[0], vrect[1], vrect[3])
                if prev_vrect is _ABSENT and (
                    kept_sig_counts.get(sig, 0) < before_sig_counts.get(sig, 0)
                    or kept_rect_counts.get(rkey, 0) < before_rect_counts.get(rkey, 0)
                    or (aid and kept_aid_counts.get((ctype, aid), 0) < before_aid_counts.get((ctype, aid), 0))
                    or (
                        not name
                        and not kt
                        and used_disappeared_anchors.get(anchor, 0) < disappeared_anchors.get(anchor, 0)
                    )
                ):
                    if kept_sig_counts.get(sig, 0) < before_sig_counts.get(sig, 0):
                        kept_sig_counts[sig] = kept_sig_counts.get(sig, 0) + 1
                    if kept_rect_counts.get(rkey, 0) < before_rect_counts.get(rkey, 0):
                        kept_rect_counts[rkey] = kept_rect_counts.get(rkey, 0) + 1
                    if aid and kept_aid_counts.get((ctype, aid), 0) < before_aid_counts.get((ctype, aid), 0):
                        kept_aid_counts[(ctype, aid)] = kept_aid_counts.get((ctype, aid), 0) + 1
                    if not name and not kt and used_disappeared_anchors.get(anchor, 0) < disappeared_anchors.get(anchor, 0):
                        used_disappeared_anchors[anchor] = used_disappeared_anchors.get(anchor, 0) + 1
                    continue
                surface_collected.append(el)
                opened_state[eid] = (prev_vrect, vrect)
                key = (ctype, aid, getattr(el, "name", ""), kt)
                opened_sigs.add(sig)
                opened_keys.add(key)
        if has_popups and uia is not None:
            for h in win.popups(pid):
                if h not in before_popups:
                    p_root = uia.element(h)
                    for el in [p_root] + list(descendants(p_root, 25)):
                        eid = _element_identity(el)
                        vrect = _visible_rect_tuple(el)
                        if vrect is not None:
                            surface_collected.append(el)
                            opened_state[eid] = (_ABSENT, vrect)
                            kt = keytip(getattr(el, "access_key", ""))
                            sig = (
                                getattr(el, "control_type", ""),
                                getattr(el, "automation_id", ""),
                                getattr(el, "name", ""),
                                kt,
                                vrect,
                            )
                            key = (
                                getattr(el, "control_type", ""),
                                getattr(el, "automation_id", ""),
                                getattr(el, "name", ""),
                                kt,
                            )
                            opened_sigs.add(sig)
                            opened_keys.add(key)
    finally:
        try:
            if surface_key == "keytips":
                win.deactivate_keytips(hwnd, root)
            elif surface_key == "statusbar.customizeMenu":
                win.dismiss_surface(hwnd, target)
            elif surface_key == "backstage":
                if can_expand:
                    target.collapse()
                else:
                    win.dismiss_surface(hwnd, target)
            elif can_expand:
                target.collapse()
            else:
                win.dismiss_surface(hwnd, target)
        except Exception as exc:
            cleanup_err = Refused(f"failed to close shell surface {surface_key!r}: {exc}")
    if cleanup_err is not None:
        raise cleanup_err

    expand_closed = False
    tree_closed = False
    popups_closed = False
    for attempt in range(10):
        expand_closed = not can_expand or getattr(target, "expand_state", lambda: 0)() in (0, None)
        after_root = uia.element(hwnd) if (uia is not None and hwnd is not None) else root
        after_pairs = list(_walk_with_ancestors(after_root, 25))
        after_nodes = [el for el, _anc in after_pairs]
        after_sig_counts = {}
        after_key_counts = {}
        for el in after_nodes:
            vrect = _visible_rect_tuple(el)
            if vrect is not None:
                kt = keytip(getattr(el, "access_key", ""))
                sig = (getattr(el, "control_type", ""), getattr(el, "automation_id", ""), getattr(el, "name", ""), kt, vrect)
                key = (getattr(el, "control_type", ""), getattr(el, "automation_id", ""), getattr(el, "name", ""), kt)
                after_sig_counts[sig] = after_sig_counts.get(sig, 0) + 1
                after_key_counts[key] = after_key_counts.get(key, 0) + 1
        still_open = False
        for el, ancestors in after_pairs:
            eid = _element_identity(el)
            cur_vrect = _visible_rect_tuple(el)
            if cur_vrect is None:
                continue
            if not _is_surface_candidate(surface_key, el, ancestors):
                continue
            kt = keytip(getattr(el, "access_key", ""))
            sig = (
                getattr(el, "control_type", ""),
                getattr(el, "automation_id", ""),
                getattr(el, "name", ""),
                kt,
                cur_vrect,
            )
            key = (
                getattr(el, "control_type", ""),
                getattr(el, "automation_id", ""),
                getattr(el, "name", ""),
                kt,
            )
            sig_excess = after_sig_counts.get(sig, 0) > before_sig_counts.get(sig, 0)
            key_excess = after_key_counts.get(key, 0) > before_key_counts.get(key, 0)
            if eid in opened_state:
                prev_vrect, _open_vrect = opened_state[eid]
                if prev_vrect is _ABSENT or prev_vrect is None:
                    if sig_excess or key_excess:
                        still_open = True
                        break
                elif cur_vrect != prev_vrect:
                    still_open = True
                    break
            elif (sig in opened_sigs and sig_excess) or (key in opened_keys and key_excess):
                still_open = True
                break
        tree_closed = not still_open
        popups_closed = not has_popups or not [h for h in win.popups(pid) if h not in before_popups]
        if expand_closed and tree_closed and popups_closed:
            break
        if attempt < 9:
            time.sleep(0.05)

    if not expand_closed:
        raise Refused(f"shell surface {surface_key!r} remained expanded after collapse")
    if not tree_closed:
        raise Refused(f"shell surface {surface_key!r} remained open after cleanup")
    if not popups_closed:
        raise Refused(f"shell surface {surface_key!r} popup window remained open after cleanup")
    return surface_collected


def _match_shell_element(rec, collected, tabs_bar, lower, origin, prefix):
    rid = rec["id"]
    sid = "shell." + rid[len(prefix):] if rid.startswith(prefix) else rid
    is_record_id = lambda aid: aid.startswith("shell.") or ".shell." in aid
    if sid == "shell.region.ribbon":
        return lower
    if sid == "shell.tabrow.tabs":
        return tabs_bar
    if sid == "shell.titlebar.caption":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type in ("Text", "TitleBar", "Pane", "Custom")
            and (not e.rect or (e.rect[1] - origin[1] < 48 and e.rect[3] - e.rect[1] <= 48))
            and (e.name == rec["label"] or getattr(e, "automation_id", "") in ("TitleBar", "WindowTitle", "AppTitle")),
        )
    if sid == "shell.titlebar.systemMenu":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and getattr(e, "automation_id", "") == "MenuBar",
        )
    if sid == "shell.titlebar.qat":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type == "ToolBar"
            and "Quick Access" in (e.name or ""),
        )
    if sid in ("shell.titlebar.autosave", "shell.qat.autosave"):
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and getattr(e, "automation_id", "") == "AutoSaveSwitch",
        )
    if sid == "shell.qat.save":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and getattr(e, "automation_id", "") == "FileSave"
            and e.control_type == "Button",
        )
    if sid == "shell.qat.undo":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and (getattr(e, "automation_id", "") == "Undo" or (e.name or "").startswith("Undo"))
            and e.control_type in ("SplitButton", "Button"),
        )
    if sid == "shell.qat.undo.dropdown":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and getattr(e, "automation_id", "") == "Undo_Dropdown",
        )
    if sid == "shell.qat.redo":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and getattr(e, "automation_id", "") in ("RedoOrRepeat", "Redo")
            and e.control_type in ("Button", "SplitButton"),
        )
    if sid == "shell.qat.fromBeginning":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and getattr(e, "automation_id", "") == "SlideShowFromBeginning",
        )
    if sid == "shell.qat.customize":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.name == "Customize Quick Access Toolbar",
        )
    if sid == "shell.titlebar.search":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and getattr(e, "automation_id", "") == "TellMeControlAnchor"
            and (not e.rect or e.rect[1] - origin[1] < 48),
        )
    if sid == "shell.tabrow.search":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and getattr(e, "automation_id", "") == "TellMeControlAnchor"
            and (not e.rect or e.rect[1] - origin[1] >= 48),
        )
    if sid == "shell.search.voice":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.name == "Voice Search"
            and (not e.rect or (e.rect[1] - origin[1] >= 48 if prefix == "project.shell." else e.rect[1] - origin[1] < 48)),
        )
    if sid == "shell.search.input":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and getattr(e, "automation_id", "") == "TellMeTextBoxAutomationId"
            and (not e.rect or (e.rect[1] - origin[1] >= 48 if prefix == "project.shell." else e.rect[1] - origin[1] < 48)),
        )
    if sid == "shell.titlebar.account":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and getattr(e, "automation_id", "") == "MeControlWidget",
        )
    if sid == "shell.titlebar.minimize":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type == "Button"
            and e.name == "Minimize",
        )
    if sid == "shell.titlebar.maximize":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type == "Button"
            and e.name in ("Restore Down", "Maximize"),
        )
    if sid == "shell.titlebar.close":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type == "Button"
            and e.name == "Close"
            and (not e.rect or e.rect[1] - origin[1] < 48),
        )
    if sid == "shell.tabrow.file":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and getattr(e, "automation_id", "") == "FileTabButton"
            and (not e.rect or e.rect[3] - e.rect[1] <= 36),
        )
    if sid == "shell.tabrow.comments":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.name == "Comments"
            and e.control_type in ("Button", "CheckBox"),
        )
    if sid == "shell.tabrow.editingMode":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.name in ("Editing", "Reviewing", "Viewing")
            and e.control_type in ("ComboBox", "MenuItem", "Button"),
        )
    if sid == "shell.tabrow.presentInTeams":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", "")) and e.name == "Present in Teams",
        )
    if sid == "shell.tabrow.share":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.name in ("Share", "Share...")
            and e.control_type in ("MenuItem", "Button", "SplitButton")
            and (not e.rect or e.rect[1] - origin[1] < 78),
        )
    if sid == "shell.tabrow.closeDocument":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type == "Button"
            and e.name == "Close"
            and e.rect
            and e.rect[1] - origin[1] >= 48,
        )
    if sid == "shell.ribbonDisplay.button":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", "")) and e.name == "Ribbon Display Options",
        )
    if sid == "shell.statusbar.bar":
        frame = _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", "")) and e.name == "Status Bar Frame",
        )
        if frame is not None:
            return frame
    if sid in ("shell.region.statusbar", "shell.statusbar.bar"):
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and (getattr(e, "automation_id", "") == "StatusBar" or e.control_type == "StatusBar"),
        )
    if sid == "shell.statusbar.displaySettings":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", "")) and e.name == "Display Settings",
        )
    if sid == "shell.statusbar.zoomOut":
        return _find_in(
            collected, lambda e: not is_record_id(getattr(e, "automation_id", "")) and e.name == "Zoom Out"
        )
    if sid == "shell.statusbar.zoomSlider":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type == "Slider"
            and "Zoom" in (e.name or ""),
        )
    if sid == "shell.statusbar.zoomIn":
        return _find_in(
            collected, lambda e: not is_record_id(getattr(e, "automation_id", "")) and e.name == "Zoom In"
        )
    if sid.startswith("shell.qat.customize."):
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type in ITEM_TYPES
            and ((rec.get("uiaId") and getattr(e, "automation_id", "") == rec["uiaId"]) or e.name == rec["label"]),
        )
    if sid.startswith(("shell.tabrow.editingMode.", "shell.tabrow.share.", "shell.ribbonDisplay.")):
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type in ITEM_TYPES
            and e.name == rec["label"],
        )
    if sid == "shell.keytips.layer":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type in ("Pane", "ToolTip", "Custom")
            and e.name == rec["label"],
        )
    if sid.startswith("shell.keytips.") and sid != "shell.keytips.layer":
        return _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type in ("Pane", "Text", "ToolTip", "Custom")
            and e.rect is not None
            and (e.rect[2] - e.rect[0]) <= 36
            and (e.rect[3] - e.rect[1]) <= 24
            and (
                (rec.get("keytip") and keytip(getattr(e, "access_key", "")) == rec["keytip"])
                or e.name in (rec["label"], rec.get("keytip"))
            ),
        )
    if rec.get("uiaId"):
        by_uia = _find_in(
            collected,
            lambda e: not is_record_id(getattr(e, "automation_id", ""))
            and e.control_type != "Window"
            and getattr(e, "automation_id", "") == rec["uiaId"]
            and e.name == rec["label"],
        )
        if by_uia is not None:
            return by_uia
    return _find_in(
        collected,
        lambda e: not is_record_id(getattr(e, "automation_id", ""))
        and e.control_type != "Window"
        and e.name == rec["label"],
    )


def apply_live_shell_measurements(records, app_name, root, tabs_bar, lower, origin, expected_build,
                                  uia=None, win=None, launched=None):
    """Observe shell chrome elements in `root` (and opened menus, Backstage and KeyTips) and assign live geometry."""
    ox, oy = origin
    prefix = "shell." if app_name == "word" else f"{app_name}.shell."
    base_elements = list(descendants(root, 25))
    surface_triggers = (
        ("qat.customize", "shell.qat.customize"),
        ("tabrow.editingMode", "shell.tabrow.editingMode"),
        ("tabrow.share", "shell.tabrow.share"),
        ("ribbonDisplay", "shell.ribbonDisplay.button"),
        ("search", "shell.tabrow.search" if app_name == "project" else "shell.titlebar.search"),
        ("statusbar.customizeMenu", "shell.statusbar.bar"),
        ("backstage", "shell.tabrow.file"),
        ("keytips", None),
    )
    by_id = {r["id"]: r for r in records}
    surface_elements = {}
    for surface_key, trigger_sid in surface_triggers:
        dependent_recs = [
            r for r in records
            if _shell_surface_key("shell." + r["id"][len(prefix):] if r["id"].startswith(prefix) else r["id"])
            == surface_key
        ]
        if not dependent_recs:
            continue
        trigger_el = None
        if trigger_sid is not None:
            trigger_id = prefix + trigger_sid[len("shell."):]
            trigger_rec = by_id.get(trigger_id) or {"id": trigger_id, "label": ""}
            trigger_el = _match_shell_element(trigger_rec, base_elements, tabs_bar, lower, origin, prefix)
            if trigger_el is None and trigger_id != trigger_sid:
                trigger_el = _match_shell_element(
                    {"id": trigger_sid, "label": ""}, base_elements, tabs_bar, lower, origin, "shell."
                )
        surface_elements[surface_key] = _open_and_collect_shell_surface(
            surface_key, trigger_el, root, uia, win, launched
        )

    for rec in records:
        if rec.get("app") == "outlook":
            continue
        sid = "shell." + rec["id"][len(prefix):] if rec["id"].startswith(prefix) else rec["id"]
        skey = _shell_surface_key(sid)
        pool = base_elements if skey == "base" else surface_elements.get(skey, ())
        el = _match_shell_element(rec, pool, tabs_bar, lower, origin, prefix)
        if el is None:
            continue
        b = _live_rect_bounds(el, ox, oy)
        if b is None:
            continue
        rec["bounds"] = b
        rec["captureProfile"] = PROFILE
        if rec.get("kind") == "control":
            rec["size"] = "large" if b["height"] >= LARGE_HEIGHT else "small"
        if getattr(el, "name", "") and not sid.startswith("shell.keytips."):
            rec["label"] = sanitize_shell_label(el.name, rec.get("uiaId", ""), rec.get("idMso", ""))
        rec["source"] = f"uia:{expected_build}"
        rec["capturedFrom"] = expected_build

    for rec in records:
        if rec.get("app") == "outlook" or "bounds" in rec:
            continue
        sid = "shell." + rec["id"][len(prefix):] if rec["id"].startswith(prefix) else rec["id"]
        if sid == "shell.keytips.layer":
            badge_recs = [
                r for r in records
                if r.get("app") != "outlook"
                and ("shell." + r["id"][len(prefix):] if r["id"].startswith(prefix) else r["id"]).startswith("shell.keytips.")
                and ("shell." + r["id"][len(prefix):] if r["id"].startswith(prefix) else r["id"]) != "shell.keytips.layer"
            ]
            if badge_recs and all("bounds" in r for r in badge_recs):
                max_bottom = max(r["bounds"]["y"] + r["bounds"]["height"] for r in badge_recs)
                rec["bounds"] = {"x": 0, "y": 0, "width": PROFILE_SIZE[0], "height": max(92, max_bottom)}
                rec["captureProfile"] = PROFILE
                rec["source"] = f"uia:{expected_build}"
                rec["capturedFrom"] = expected_build

    unobserved = [r["id"] for r in records if r.get("app") != "outlook" and "bounds" not in r]
    if unobserved:
        raise Refused(
            f"incomplete shell chrome capture for {app_name}: "
            f"{len(unobserved)} element(s) were not observed in UIA ({', '.join(unobserved[:5])})"
        )


def main(argv=None, launcher=Launched, uia_factory=None, win_factory=None):
    parser = argparse.ArgumentParser(description="Capture an Office app's ribbon or shared shell chrome through UI Automation.")
    parser.add_argument("--app", choices=sorted(APPS), help="reference app to capture (required for tab captures)")
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument("--tab", help="one tab, by its name as the ribbon shows it")
    which.add_argument("--all-tabs", action="store_true", help="every built-in tab the ribbon lists")
    which.add_argument("--shell", action="store_true", help="shared shell chrome and per-app shell overrides")
    parser.add_argument("--expand", action="store_true", help="open each menu and gallery and record its items")
    parser.add_argument("--layout", choices=("classic", "simplified"), default="classic")
    parser.add_argument("--merge", action="store_true", help="update an existing file, keeping hand-written fields")
    parser.add_argument("--out", help="output file (default design/inventory/<app>/ribbon[-simplified].json or shell/chrome.json)")
    args = parser.parse_args(argv)
    if args.shell:
        out = Path(args.out) if args.out else INVENTORY / "shell" / "chrome.json"
        if out.exists() and not args.merge:
            print(f"capture-ui: {out} exists; pass --merge to update it", file=sys.stderr)
            return 1
        initial_bytes = out.read_bytes() if args.merge and out.exists() else None
        shell_apps = (args.app,) if args.app else (
            "word", "excel", "powerpoint", "visio", "project"
        )
        records = []
        for app_name in shell_apps:
            app_args = argparse.Namespace(**dict(vars(args), app=app_name))
            try:
                launched = launcher(app_name)
            except Unsafe as exc:
                print(f"capture-ui: {exc}", file=sys.stderr)
                return 2
            except Exception as exc:
                print(f"capture-ui: {APPS[app_name][1]} could not be started ({type(exc).__name__}: {exc})",
                      file=sys.stderr)
                return 2
            try:
                if uia_factory or win_factory:
                    app_records, app_problems, _ctx = capture(
                        app_args, launched, (uia_factory or Uia)(), (win_factory or Win)()
                    )
                else:
                    app_records, app_problems, _ctx = capture_in_worker(app_args, launched)
            except Unsafe as exc:
                print(f"capture-ui: {exc}", file=sys.stderr)
                launched.close()
                return 2
            except (Refused, Gone) as exc:
                msg = exc if isinstance(exc, Refused) else "an element vanished while it was read: " + str(exc)
                print(f"capture-ui: {msg}", file=sys.stderr)
                launched.close()
                return 1
            except BaseException:
                launched.close()
                raise
            launched.close()
            if app_problems:
                print(f"capture-ui: no bounds under {PROFILE}: {'; '.join(app_problems)}", file=sys.stderr)
                return 1
            records.extend(app_records)
        if not args.app:
            records.extend(build_shell_chrome_records(reference_build(), app_name="outlook"))
        try:
            if args.merge:
                current_bytes = out.read_bytes() if out.exists() else None
                if current_bytes != initial_bytes:
                    raise Refused(f"{out} changed during the capture; re-run to merge cleanly")
                if current_bytes is not None:
                    records = merge(_load_existing_records(out, current_bytes), records)
            validate_shell_chrome(records)
            publish(
                {out: render(records)},
                create_only=() if args.merge else (out,),
                expected_bytes={out: initial_bytes} if args.merge else None,
            )
        except Refused as exc:
            print(f"capture-ui: {exc}", file=sys.stderr)
            return 1
        print(f"{out}: {len(records)} records; bounds recorded under {PROFILE}")
        return 0
    if not args.app:
        parser.error("the following arguments are required: --app")
    out = Path(args.out) if args.out else INVENTORY / args.app / (
        "ribbon-simplified.json" if args.layout == "simplified" else "ribbon.json")
    if out.exists() and not args.merge:
        print(f"capture-ui: {out} exists; pass --merge to update it", file=sys.stderr)
        return 1
    unverified_path = UNVERIFIED / f"{args.app}-unverified.json"
    initial_bytes = out.read_bytes() if args.merge and out.exists() else None
    initial_unverified = unverified_path.read_bytes() if unverified_path.exists() else None
    try:
        launched = launcher(args.app)
    except Unsafe as exc:
        print(f"capture-ui: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # COM raises its own error types; any of them means the app did not start for us
        print(f"capture-ui: {APPS[args.app][1]} could not be started ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2
    try:
        if uia_factory or win_factory:  # tests drive capture() in this process with fakes
            records, problems, ctx = capture(args, launched, (uia_factory or Uia)(), (win_factory or Win)())
        else:
            records, problems, ctx = capture_in_worker(args, launched)
    except Unsafe as exc:
        print(f"capture-ui: {exc}", file=sys.stderr)
        launched.close()
        return 2
    except (Refused, Gone) as exc:
        print(f"capture-ui: {exc if isinstance(exc, Refused) else 'an element vanished while it was read: ' + str(exc)}",
              file=sys.stderr)
        launched.close()
        return 1
    except BaseException:
        launched.close()
        raise
    launched.close()
    try:
        unverified_records = list(ctx.unverified)
        if args.merge:
            current_bytes = out.read_bytes() if out.exists() else None
            if current_bytes != initial_bytes:
                raise Refused(f"{out} changed during the capture; re-run to merge cleanly")
            if current_bytes is not None:
                records = merge(_load_existing_records(out, current_bytes), records, unverified_records)
        if args.merge or unverified_records:
            current_unverified = unverified_path.read_bytes() if unverified_path.exists() else None
            if current_unverified != initial_unverified:
                raise Refused(f"{unverified_path} changed during the capture; re-run to merge cleanly")
            if unverified_records and current_unverified is not None:
                unverified_records = merge(
                    _load_existing_records(unverified_path, current_unverified),
                    unverified_records,
                )
        files = {out: render(records)}
        expected = {out: initial_bytes} if args.merge else {}
        create_only = [] if args.merge else [out]
        if unverified_records:
            files[unverified_path] = render(unverified_records)
            if initial_unverified is not None:
                expected[unverified_path] = initial_unverified
            else:
                create_only.append(unverified_path)
        publish(files, create_only=tuple(create_only), expected_bytes=expected or None)
    except Refused as exc:
        print(f"capture-ui: {exc}", file=sys.stderr)
        return 1
    for line in ctx.skipped + ctx.notes:
        print(line)
    if unverified_records:
        print(f"{len(unverified_records)} unverified records in {unverified_path}")
    print(f"{out}: {len(records)} records" + ("; bounds recorded under " + PROFILE if not problems else
                                               "; no bounds: " + "; ".join(problems)))
    return 0


if __name__ == "__main__":
    sys.exit(worker() if sys.argv[1:] == ["--worker"] else main(sys.argv[1:]))
