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
import base64
import json
from pathlib import Path
import re
import sys
import time
import zlib

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
    return _NO_CONTROL_RE.sub("", (text or "").replace("\u2013", "-").replace("\u2014", "-"))


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
    """The last step of a KeyTip path: "Alt, H, F P" is FP, "Alt, H" is H, "Alt, JB, ALT+E" is E."""
    if not access_key:
        return None
    step = access_key.split(",")[-1].replace(" ", "")
    step = re.sub(r"^(?:alt\+)+", "", step, flags=re.IGNORECASE).upper()
    return step or None


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
    if element.control_type == "MenuItem" and (
        element.automation_id.endswith("Gallery")
        or element.automation_id in ("TableStylesGalleryWord", "QuickStylesSets")
    ):
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
            try:
                self._restore_saved_clipboard()
            except Exception as exc:
                failures.append(f"restore clipboard failed ({type(exc).__name__}: {exc})")
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
        fdoc = getattr(self, "_fixture_doc", None)
        fmeta = getattr(self, "_fixture_meta", None)
        has_fdoc = fdoc is not None and not getattr(fdoc, "closed", False)
        expected_docs = list(self.created) + ([fdoc] if has_fdoc else [])
        base_metas = getattr(self, "_created_meta", None) or [self._doc_meta(d) for d in self.created]
        expected_metas = list(base_metas) + ([fmeta or self._doc_meta(fdoc)] if has_fdoc else [])
        count = self.open_documents()
        if count != len(expected_docs):
            raise Refused(f"the {self.exe} instance now holds {count} documents, not only the tool's own; stopping "
                          "before the ribbon acts on someone else's")
        for doc, meta in zip(expected_docs, expected_metas):
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
            if len(live) != len(expected_docs) or any(
                getattr(d, "closed", False) or not any(self._same_doc(d, c) for c in expected_docs) for d in live
            ):
                raise Refused(f"the {self.exe} instance now holds a document this tool did not create; stopping before "
                              "the ribbon acts on someone else's")
        for attr in ("ActiveDocument", "ActiveWorkbook", "ActivePresentation", "ActiveProject"):
            active = getattr(app, attr, None)
            if active is not None and not any(self._same_doc(active, c) for c in expected_docs):
                raise Refused(f"the active {self.exe} document is not the one this tool created; stopping before the "
                              "ribbon acts on someone else's")

    def _free_clipboard_snapshot(self, snapshot):
        if not snapshot or callable(getattr(self, "_clipboard_restorer", None)):
            return
        try:
            import ctypes
            win32 = getattr(self, "_clipboard_win32", None)
            gdi32 = win32.gdi32 if win32 is not None else ctypes.windll.gdi32
            gdi32.DeleteObject.argtypes = [ctypes.c_void_p]
            gdi32.DeleteEnhMetaFile.argtypes = [ctypes.c_void_p]
        except Exception:
            return
        for _fmt, kind, payload in snapshot:
            if not payload or not isinstance(payload, int):
                continue
            try:
                if kind == "bitmap":
                    gdi32.DeleteObject(payload)
                elif kind == "emf":
                    gdi32.DeleteEnhMetaFile(payload)
            except Exception:
                pass

    def _get_clipboard_seq(self, u32):
        import ctypes
        fn = getattr(u32, "GetClipboardSequenceNumber", None)
        if not callable(fn):
            return None
        try:
            fn.restype = ctypes.c_uint
            fn.argtypes = []
        except Exception:
            pass
        return int(fn() or 0)

    def _is_clipboard_owned_by_instance(self, u32):
        import ctypes
        fn = getattr(u32, "GetClipboardOwner", None)
        if not callable(fn):
            return False
        try:
            fn.restype = ctypes.c_void_p
            fn.argtypes = []
        except Exception:
            pass
        owner_hwnd = int(fn() or 0)
        if owner_hwnd <= 0:
            return False
        instance_hwnd = int(getattr(self, "hwnd", 0) or 0)
        clip_owner_hwnd = int(getattr(self, "_clipboard_owner_hwnd", 0) or 0)
        if owner_hwnd in (instance_hwnd, clip_owner_hwnd) and owner_hwnd > 0:
            return True
        instance_pid = int(getattr(getattr(self, "proc", None), "pid", 0) or 0)
        pid_fn = getattr(u32, "GetWindowThreadProcessId", None)
        if instance_pid > 0 and callable(pid_fn):
            try:
                pid_fn.restype = ctypes.c_ulong
                pid_fn.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
            except Exception:
                pass
            owner_pid = ctypes.c_ulong(0)
            pid_fn(ctypes.c_void_p(owner_hwnd), ctypes.byref(owner_pid))
            if int(owner_pid.value or 0) == instance_pid:
                return True
        return False

    def _is_valid_seeded_sig(self, sig):
        if not isinstance(sig, tuple) or len(sig) != 2:
            return False
        fmts, text_payload = sig
        if not fmts:
            return False
        saved_handles = getattr(self, "_saved_clipboard_handles", ())
        if saved_handles and fmts == saved_handles:
            return False
        sample_payloads = (
            "Sample\x00".encode("utf-16-le"),
            "Sample\r\x00".encode("utf-16-le"),
            b"Sample\x00",
            b"Sample\r\x00",
        )
        return text_payload in sample_payloads

    def _peek_clipboard_sig_while_open(self, u32, k32):
        import ctypes
        u32.GetClipboardData.restype = ctypes.c_void_p
        u32.GetClipboardData.argtypes = [ctypes.c_uint]
        k32.GlobalLock.restype = ctypes.c_void_p
        k32.GlobalLock.argtypes = [ctypes.c_void_p]
        k32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        k32.GlobalSize.restype = ctypes.c_size_t
        k32.GlobalSize.argtypes = [ctypes.c_void_p]
        fmts = []
        text_payload = None
        fmt = int(u32.EnumClipboardFormats(0) or 0)
        while fmt:
            h_raw = u32.GetClipboardData(fmt)
            h = int(h_raw or 0)
            fmts.append((fmt, h))
            if fmt in (13, 1) and h and text_payload is None:
                sz = int(k32.GlobalSize(h) or 0)
                ptr = k32.GlobalLock(h) if sz > 0 else None
                if ptr:
                    try:
                        text_payload = ctypes.string_at(ptr, sz)
                    finally:
                        k32.GlobalUnlock(h)
            fmt = int(u32.EnumClipboardFormats(fmt) or 0)
        return (tuple(fmts), text_payload)

    def _record_seeded_clipboard_state(self):
        if callable(getattr(self, "_clipboard_saver", None)) or callable(getattr(self, "_clipboard_restorer", None)):
            return
        import ctypes
        win32 = getattr(self, "_clipboard_win32", None)
        u32 = win32.user32 if win32 is not None else ctypes.windll.user32
        k32 = win32.kernel32 if win32 is not None else ctypes.windll.kernel32
        opened = False
        for _ in range(25):
            if u32.OpenClipboard(0):
                opened = True
                break
            time.sleep(0.02)
        if not opened:
            raise Refused("could not open the system clipboard to verify seeded Home clipboard state")
        try:
            sig = self._peek_clipboard_sig_while_open(u32, k32)
            seq = self._get_clipboard_seq(u32)
            saved_seq = getattr(self, "_saved_clipboard_seq", None)
            seq_advanced = saved_seq is None or seq is None or seq != saved_seq
            if self._is_clipboard_owned_by_instance(u32) and self._is_valid_seeded_sig(sig) and seq_advanced:
                self._clipboard_externally_modified = False
                self._seeded_clipboard_sig = sig
                self._seeded_clipboard_seq = seq
            else:
                self._clipboard_externally_modified = True
                self._seeded_clipboard_sig = None
                self._seeded_clipboard_seq = None
        finally:
            u32.CloseClipboard()

    def _save_clipboard(self):
        saver = getattr(self, "_clipboard_saver", None)
        if callable(saver):
            return saver()
        import ctypes

        class _METAFILEPICT(ctypes.Structure):
            _fields_ = [
                ("mm", ctypes.c_long),
                ("xExt", ctypes.c_long),
                ("yExt", ctypes.c_long),
                ("hMF", ctypes.c_void_p),
            ]

        win32 = getattr(self, "_clipboard_win32", None)
        u32 = win32.user32 if win32 is not None else ctypes.windll.user32
        k32 = win32.kernel32 if win32 is not None else ctypes.windll.kernel32
        gdi32 = win32.gdi32 if win32 is not None else ctypes.windll.gdi32
        u32.GetClipboardData.restype = ctypes.c_void_p
        u32.GetClipboardData.argtypes = [ctypes.c_uint]
        u32.CopyImage.restype = ctypes.c_void_p
        u32.CopyImage.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
        gdi32.CopyEnhMetaFileW.restype = ctypes.c_void_p
        gdi32.CopyEnhMetaFileW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        gdi32.GetPaletteEntries.restype = ctypes.c_uint
        gdi32.GetPaletteEntries.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p]
        gdi32.GetMetaFileBitsEx.restype = ctypes.c_uint
        gdi32.GetMetaFileBitsEx.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p]
        k32.GlobalLock.restype = ctypes.c_void_p
        k32.GlobalLock.argtypes = [ctypes.c_void_p]
        k32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        k32.GlobalSize.restype = ctypes.c_size_t
        k32.GlobalSize.argtypes = [ctypes.c_void_p]
        opened = False
        for _ in range(25):
            if u32.OpenClipboard(0):
                opened = True
                break
            time.sleep(0.02)
        if not opened:
            raise Refused("could not open the system clipboard to preserve operator clipboard state")
        items = []
        raw_handles = []
        try:
            fmt = u32.EnumClipboardFormats(0)
            while fmt:
                if fmt == 0x0080 or (0x0084 <= fmt <= 0x008D) or (0x0200 <= fmt <= 0x03FF):
                    raise Refused(
                        f"clipboard contains non-preservable format 0x{fmt:04x}; refusing to overwrite operator clipboard"
                    )
                h = u32.GetClipboardData(fmt)
                if not h:
                    raise Refused(
                        f"clipboard format 0x{fmt:04x} returned no data handle; refusing to overwrite operator clipboard"
                    )
                raw_handles.append((int(fmt), int(h)))
                if fmt in (2, 0x0082):
                    dup_bmp = u32.CopyImage(h, 0, 0, 0, 0)
                    if not dup_bmp:
                        raise Refused(
                            f"clipboard bitmap format 0x{fmt:04x} could not be duplicated; refusing to overwrite operator clipboard"
                        )
                    items.append((fmt, "bitmap", dup_bmp))
                elif fmt in (14, 0x008E):
                    dup_emf = gdi32.CopyEnhMetaFileW(h, None)
                    if not dup_emf:
                        raise Refused(
                            f"clipboard enhanced metafile format 0x{fmt:04x} could not be duplicated; refusing to overwrite operator clipboard"
                        )
                    items.append((fmt, "emf", dup_emf))
                elif fmt == 9:
                    entry_count = int(gdi32.GetPaletteEntries(h, 0, 0, None) or 0)
                    if entry_count <= 0:
                        raise Refused(
                            "clipboard palette format CF_PALETTE has no readable entries; refusing to overwrite operator clipboard"
                        )
                    pal_buf = ctypes.create_string_buffer(entry_count * 4)
                    read_count = int(
                        gdi32.GetPaletteEntries(h, 0, entry_count, ctypes.cast(pal_buf, ctypes.c_void_p)) or 0
                    )
                    if read_count != entry_count:
                        raise Refused(
                            "clipboard palette format CF_PALETTE entries could not be read; refusing to overwrite operator clipboard"
                        )
                    items.append((fmt, "palette", pal_buf.raw))
                elif fmt in (3, 0x0083):
                    sz = int(k32.GlobalSize(h) or 0)
                    ptr = k32.GlobalLock(h) if sz >= ctypes.sizeof(_METAFILEPICT) else None
                    if not ptr:
                        raise Refused(
                            f"clipboard metafile-picture format 0x{fmt:04x} could not be locked; refusing to overwrite operator clipboard"
                        )
                    try:
                        mfp = _METAFILEPICT.from_address(ptr)
                        if not mfp.hMF:
                            raise Refused(
                                f"clipboard metafile-picture format 0x{fmt:04x} has no metafile handle; refusing to overwrite operator clipboard"
                            )
                        mf_size = int(gdi32.GetMetaFileBitsEx(mfp.hMF, 0, None) or 0)
                        if mf_size <= 0:
                            raise Refused(
                                f"clipboard metafile-picture format 0x{fmt:04x} bits could not be sized; refusing to overwrite operator clipboard"
                            )
                        mf_buf = ctypes.create_string_buffer(mf_size)
                        if int(gdi32.GetMetaFileBitsEx(mfp.hMF, mf_size, ctypes.cast(mf_buf, ctypes.c_void_p)) or 0) != mf_size:
                            raise Refused(
                                f"clipboard metafile-picture format 0x{fmt:04x} bits could not be read; refusing to overwrite operator clipboard"
                            )
                        mfp_payload = (int(mfp.mm), int(mfp.xExt), int(mfp.yExt), mf_buf.raw)
                    finally:
                        k32.GlobalUnlock(h)
                    items.append((fmt, "mfpict", mfp_payload))
                else:
                    sz = int(k32.GlobalSize(h) or 0)
                    ptr = k32.GlobalLock(h) if sz > 0 else None
                    if not ptr:
                        raise Refused(
                            f"clipboard format 0x{fmt:04x} could not be locked as HGLOBAL; refusing to overwrite operator clipboard"
                        )
                    try:
                        raw_bytes = ctypes.string_at(ptr, sz)
                    finally:
                        k32.GlobalUnlock(h)
                    items.append((fmt, "hglobal", raw_bytes))
                fmt = u32.EnumClipboardFormats(fmt)
            saved_seq = self._get_clipboard_seq(u32)
        except BaseException:
            self._free_clipboard_snapshot(items)
            raise
        finally:
            u32.CloseClipboard()
        self._saved_clipboard_handles = tuple(raw_handles)
        self._saved_clipboard_seq = saved_seq
        self._seeded_clipboard_seq = None
        self._seeded_clipboard_sig = None
        self._clipboard_externally_modified = False
        self._partial_restore_in_progress = False
        return items

    def _restore_clipboard(self, snapshot):
        restorer = getattr(self, "_clipboard_restorer", None)
        if callable(restorer):
            return restorer(snapshot)
        import ctypes
        import struct

        class _METAFILEPICT(ctypes.Structure):
            _fields_ = [
                ("mm", ctypes.c_long),
                ("xExt", ctypes.c_long),
                ("yExt", ctypes.c_long),
                ("hMF", ctypes.c_void_p),
            ]

        win32 = getattr(self, "_clipboard_win32", None)
        u32 = win32.user32 if win32 is not None else ctypes.windll.user32
        k32 = win32.kernel32 if win32 is not None else ctypes.windll.kernel32
        gdi32 = win32.gdi32 if win32 is not None else ctypes.windll.gdi32
        u32.SetClipboardData.restype = ctypes.c_void_p
        u32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        u32.CopyImage.restype = ctypes.c_void_p
        u32.CopyImage.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
        k32.GlobalAlloc.restype = ctypes.c_void_p
        k32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
        k32.GlobalFree.argtypes = [ctypes.c_void_p]
        k32.GlobalLock.restype = ctypes.c_void_p
        k32.GlobalLock.argtypes = [ctypes.c_void_p]
        k32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        gdi32.CopyEnhMetaFileW.restype = ctypes.c_void_p
        gdi32.CopyEnhMetaFileW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        gdi32.CreatePalette.restype = ctypes.c_void_p
        gdi32.CreatePalette.argtypes = [ctypes.c_void_p]
        gdi32.SetMetaFileBitsEx.restype = ctypes.c_void_p
        gdi32.SetMetaFileBitsEx.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        gdi32.DeleteObject.argtypes = [ctypes.c_void_p]
        gdi32.DeleteEnhMetaFile.argtypes = [ctypes.c_void_p]
        gdi32.DeleteMetaFile.argtypes = [ctypes.c_void_p]
        u32.OpenClipboard.restype = ctypes.c_int
        u32.OpenClipboard.argtypes = [ctypes.c_void_p]
        owner_hwnd = int(getattr(self, "_clipboard_owner_hwnd", 0) or 0)
        temp_owner_hwnd = 0
        if owner_hwnd <= 0 and hasattr(u32, "CreateWindowExW"):
            u32.CreateWindowExW.restype = ctypes.c_void_p
            u32.CreateWindowExW.argtypes = [
                ctypes.c_uint,
                ctypes.c_wchar_p,
                ctypes.c_wchar_p,
                ctypes.c_uint,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
            ]
            temp_owner_hwnd = int(
                u32.CreateWindowExW(
                    0,
                    "STATIC",
                    "OfficeCaptureClipboardOwner",
                    0,
                    0,
                    0,
                    0,
                    0,
                    ctypes.c_void_p(-3),
                    None,
                    None,
                    None,
                )
                or 0
            )
            owner_hwnd = temp_owner_hwnd
        if owner_hwnd <= 0:
            owner_hwnd = int(getattr(self, "hwnd", 0) or 0)
        if owner_hwnd <= 0:
            raise Refused("could not obtain a valid window handle to take clipboard ownership for restoration")
        opened = False
        try:
            for _ in range(25):
                if u32.OpenClipboard(owner_hwnd):
                    opened = True
                    break
                time.sleep(0.02)
            if not opened:
                raise Refused("could not open the system clipboard to restore operator clipboard state")
            emptied_by_us = False
            try:
                cur_sig = self._peek_clipboard_sig_while_open(u32, k32)
                cur_seq = self._get_clipboard_seq(u32)
                seeded_seq = getattr(self, "_seeded_clipboard_seq", None)
                seeded_sig = getattr(self, "_seeded_clipboard_sig", None)
                partial_retry = bool(getattr(self, "_partial_restore_in_progress", False))
                external_change = bool(getattr(self, "_clipboard_externally_modified", False))
                if not external_change:
                    if not partial_retry and not self._is_clipboard_owned_by_instance(u32):
                        external_change = True
                    elif seeded_seq is not None and cur_seq is not None and cur_seq != seeded_seq:
                        external_change = True
                    elif seeded_sig is not None and cur_sig != seeded_sig:
                        external_change = True
                    elif not partial_retry and seeded_seq is None and seeded_sig is None:
                        if not self._is_valid_seeded_sig(cur_sig):
                            external_change = True
                if external_change:
                    self._seeded_clipboard_seq = None
                    self._seeded_clipboard_sig = None
                    self._clipboard_externally_modified = False
                    self._partial_restore_in_progress = False
                    return False
                if not u32.EmptyClipboard():
                    raise Refused("could not empty the system clipboard to restore operator clipboard state")
                emptied_by_us = True
                for fmt, kind, payload in snapshot or ():
                    if kind == "hglobal":
                        if not isinstance(payload, (bytes, bytearray)):
                            raise Refused(f"invalid clipboard hglobal payload for format 0x{fmt:04x}")
                        n = len(payload)
                        hmem = k32.GlobalAlloc(0x0042, max(1, n))
                        if not hmem:
                            raise Refused(f"GlobalAlloc failed while restoring clipboard format 0x{fmt:04x}")
                        ptr = k32.GlobalLock(hmem)
                        if not ptr:
                            k32.GlobalFree(hmem)
                            raise Refused(f"GlobalLock failed while restoring clipboard format 0x{fmt:04x}")
                        try:
                            if n > 0:
                                ctypes.memmove(ptr, bytes(payload), n)
                        finally:
                            k32.GlobalUnlock(hmem)
                        if not u32.SetClipboardData(fmt, hmem):
                            k32.GlobalFree(hmem)
                            raise Refused(f"SetClipboardData failed while restoring clipboard format 0x{fmt:04x}")
                    elif kind == "bitmap":
                        if not payload:
                            raise Refused(f"missing bitmap handle while restoring clipboard format 0x{fmt:04x}")
                        dup_bmp = u32.CopyImage(payload, 0, 0, 0, 0)
                        if not dup_bmp:
                            raise Refused(f"CopyImage failed while restoring clipboard format 0x{fmt:04x}")
                        if not u32.SetClipboardData(fmt, dup_bmp):
                            gdi32.DeleteObject(dup_bmp)
                            raise Refused(f"SetClipboardData failed while restoring clipboard format 0x{fmt:04x}")
                    elif kind == "emf":
                        if not payload:
                            raise Refused(f"missing enhanced metafile handle while restoring clipboard format 0x{fmt:04x}")
                        dup_emf = gdi32.CopyEnhMetaFileW(payload, None)
                        if not dup_emf:
                            raise Refused(f"CopyEnhMetaFileW failed while restoring clipboard format 0x{fmt:04x}")
                        if not u32.SetClipboardData(fmt, dup_emf):
                            gdi32.DeleteEnhMetaFile(dup_emf)
                            raise Refused(f"SetClipboardData failed while restoring clipboard format 0x{fmt:04x}")
                    elif kind == "palette":
                        if not isinstance(payload, (bytes, bytearray)) or len(payload) == 0 or len(payload) % 4 != 0:
                            raise Refused(f"invalid palette payload while restoring clipboard format 0x{fmt:04x}")
                        count = len(payload) // 4
                        logpal = ctypes.create_string_buffer(4 + len(payload))
                        struct.pack_into("<HH", logpal, 0, 0x0300, count)
                        ctypes.memmove(ctypes.addressof(logpal) + 4, bytes(payload), len(payload))
                        hpal = gdi32.CreatePalette(ctypes.cast(logpal, ctypes.c_void_p))
                        if not hpal:
                            raise Refused(f"CreatePalette failed while restoring clipboard format 0x{fmt:04x}")
                        if not u32.SetClipboardData(fmt, hpal):
                            gdi32.DeleteObject(hpal)
                            raise Refused(f"SetClipboardData failed while restoring clipboard format 0x{fmt:04x}")
                    elif kind == "mfpict":
                        if not isinstance(payload, tuple) or len(payload) != 4:
                            raise Refused(f"invalid metafile-picture payload while restoring clipboard format 0x{fmt:04x}")
                        mm, x_ext, y_ext, mf_bytes = payload
                        if not isinstance(mf_bytes, (bytes, bytearray)) or len(mf_bytes) == 0:
                            raise Refused(f"empty metafile-picture bits while restoring clipboard format 0x{fmt:04x}")
                        mf_buf = ctypes.create_string_buffer(bytes(mf_bytes), len(mf_bytes))
                        hmf = gdi32.SetMetaFileBitsEx(len(mf_bytes), ctypes.cast(mf_buf, ctypes.c_void_p))
                        if not hmf:
                            raise Refused(f"SetMetaFileBitsEx failed while restoring clipboard format 0x{fmt:04x}")
                        hmem = k32.GlobalAlloc(0x0042, ctypes.sizeof(_METAFILEPICT))
                        if not hmem:
                            gdi32.DeleteMetaFile(hmf)
                            raise Refused(f"GlobalAlloc failed while restoring clipboard format 0x{fmt:04x}")
                        ptr = k32.GlobalLock(hmem)
                        if not ptr:
                            gdi32.DeleteMetaFile(hmf)
                            k32.GlobalFree(hmem)
                            raise Refused(f"GlobalLock failed while restoring clipboard format 0x{fmt:04x}")
                        try:
                            mfp_struct = _METAFILEPICT(mm=int(mm), xExt=int(x_ext), yExt=int(y_ext), hMF=hmf)
                            ctypes.memmove(ptr, ctypes.byref(mfp_struct), ctypes.sizeof(_METAFILEPICT))
                        finally:
                            k32.GlobalUnlock(hmem)
                        if not u32.SetClipboardData(fmt, hmem):
                            gdi32.DeleteMetaFile(hmf)
                            k32.GlobalFree(hmem)
                            raise Refused(f"SetClipboardData failed while restoring clipboard format 0x{fmt:04x}")
                    else:
                        raise Refused(f"unsupported clipboard snapshot kind {kind!r} for format 0x{fmt:04x}")
                self._seeded_clipboard_seq = None
                self._seeded_clipboard_sig = None
                self._clipboard_externally_modified = False
                self._partial_restore_in_progress = False
                return True
            except BaseException:
                if emptied_by_us:
                    self._seeded_clipboard_sig = self._peek_clipboard_sig_while_open(u32, k32)
                    self._seeded_clipboard_seq = self._get_clipboard_seq(u32)
                    self._partial_restore_in_progress = True
                raise
            finally:
                u32.CloseClipboard()
        finally:
            if temp_owner_hwnd > 0 and hasattr(u32, "DestroyWindow"):
                u32.DestroyWindow.argtypes = [ctypes.c_void_p]
                u32.DestroyWindow.restype = ctypes.c_int
                u32.DestroyWindow(temp_owner_hwnd)

    def _restore_saved_clipboard(self):
        if hasattr(self, "_saved_clipboard") and self._saved_clipboard is not None:
            saved = self._saved_clipboard
            self._restore_clipboard(saved)
            self._free_clipboard_snapshot(saved)
            self._saved_clipboard = None

    def word_action(self, action, timeout=None, **kwargs):
        return self._call_com(lambda: self._word_action_impl(action, **kwargs), timeout=timeout)

    def _word_action_impl(self, action, **kwargs):
        import hashlib
        if getattr(self, "key", None) != "word":
            raise Refused(f"word_action is only valid for Word, not {getattr(self, 'key', None)!r}")
        if action == "restore_clipboard":
            self._restore_saved_clipboard()
            return {"hwnd": int(self.hwnd or 0)}
        self._check_alone_impl()
        app = self.app
        if action == "open_fixture":
            self._restore_saved_clipboard()
            path = Path(kwargs.get("path") or WORD_DEFAULT_FIXTURE)
            if not path.is_file():
                raise Refused(f"Word contextual fixture {path} does not exist")
            self._fixture_path = path
            self._fixture_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            try:
                doc = app.Documents.Open(str(path), ReadOnly=True)
            except TypeError:
                doc = app.Documents.Open(str(path))
            self._fixture_doc = doc
            self._fixture_meta = self._doc_meta(doc)
            wh = self.window_handle()
            if wh is not None:
                self.hwnd = self._get_win().top(wh)
            return {"hwnd": int(self.hwnd or 0)}
        if action == "close_fixture":
            self._restore_saved_clipboard()
            fdoc = getattr(self, "_fixture_doc", None)
            if fdoc is not None and not getattr(fdoc, "closed", False):
                try:
                    if bool(getattr(app, "PrintPreview", False)):
                        app.PrintPreview = False
                except Exception:
                    pass
                try:
                    app.ActiveWindow.View.SeekView = 0
                    app.ActiveWindow.View.Type = 3
                except Exception:
                    pass
                try:
                    fdoc.Close(0)
                except TypeError:
                    fdoc.Close()
            self._fixture_doc = None
            self._fixture_meta = None
            fpath = getattr(self, "_fixture_path", None)
            fsha = getattr(self, "_fixture_sha256", None)
            if fpath is not None and fpath.is_file() and fsha is not None:
                after_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
                if after_sha != fsha:
                    raise Refused(f"Word contextual fixture {fpath} was modified during capture")
            if self.created and not getattr(self.created[0], "closed", False):
                try:
                    wh = self.window_handle()
                    if wh is not None:
                        self.hwnd = self._get_win().top(wh)
                except Exception:
                    pass
            return {"hwnd": int(self.hwnd or 0)}
        if action == "prepare_core_tab":
            tab_name = kwargs.get("tab_name", "")
            if tab_name != "Home":
                self._restore_saved_clipboard()
            doc = self.created[0] if self.created else None
            if doc is not None:
                if tab_name == "Layout":
                    shapes_col = getattr(doc, "Shapes", None)
                    if shapes_col is not None:
                        for idx_s, (sname, left) in enumerate((("PrepLayoutShape1", 50), ("PrepLayoutShape2", 130)), 1):
                            found_s = None
                            try:
                                found_s = shapes_col(sname) if callable(shapes_col) else shapes_col.Item(sname)
                            except Exception:
                                found_s = None
                            if found_s is None and hasattr(shapes_col, "AddShape"):
                                created_s = shapes_col.AddShape(1, left, 50, 60, 40)
                                try:
                                    created_s.Name = sname
                                except Exception:
                                    pass
                        if hasattr(shapes_col, "Range"):
                            shapes_col.Range(["PrepLayoutShape1", "PrepLayoutShape2"]).Select()
                else:
                    shapes_col = getattr(doc, "Shapes", None)
                    if shapes_col is not None:
                        for sname in ("PrepLayoutShape1", "PrepLayoutShape2"):
                            try:
                                sh_obj = shapes_col(sname) if callable(shapes_col) else shapes_col.Item(sname)
                                if sh_obj is not None and hasattr(sh_obj, "Delete"):
                                    sh_obj.Delete()
                            except Exception:
                                pass
                    if tab_name == "Home":
                        if getattr(self, "_saved_clipboard", None) is None:
                            self._saved_clipboard = self._save_clipboard()
                        rng = doc.Range(0, 0) if hasattr(doc, "Range") else None
                        if rng is None or not hasattr(rng, "Copy"):
                            self._restore_saved_clipboard()
                            raise Refused("Word document Range does not support Copy() to seed Home clipboard state")
                        if not callable(getattr(doc, "UndoClear", None)):
                            self._restore_saved_clipboard()
                            raise Refused("Word document does not support UndoClear() to reset undo history after Home preparation")
                        try:
                            rng.Text = "Sample"
                            rng.Copy()
                            self._record_seeded_clipboard_state()
                            rng.Text = ""
                            if hasattr(rng, "Select"):
                                rng.Select()
                            doc.UndoClear()
                        except Exception as exc:
                            try:
                                if callable(getattr(doc, "UndoClear", None)):
                                    doc.UndoClear()
                            except Exception:
                                pass
                            self._restore_saved_clipboard()
                            raise Refused(f"failed to seed Home clipboard state ({type(exc).__name__}: {exc})") from None
                    else:
                        try:
                            if hasattr(doc, "Range"):
                                doc.Range(0, 0).Select()
                        except Exception:
                            pass
                        if tab_name == "Draw":
                            if not callable(getattr(doc, "UndoClear", None)):
                                raise Refused("Word document does not support UndoClear() to reset undo history before Draw capture")
                            try:
                                doc.UndoClear()
                            except Exception as exc:
                                raise Refused(
                                    f"failed to clear Word undo history before Draw capture ({type(exc).__name__}: {exc})"
                                ) from None
                        elif callable(getattr(doc, "UndoClear", None)):
                            try:
                                doc.UndoClear()
                            except Exception:
                                pass
                if tab_name == "Mailings":
                    csv_path = Path(kwargs.get("recipients_path") or WORD_DEFAULT_RECIPIENTS)
                    if not csv_path.is_file():
                        raise Refused(f"Word mail-merge recipients fixture {csv_path} does not exist")
                    if hasattr(doc, "MailMerge"):
                        doc.MailMerge.MainDocumentType = 0
                        doc.MailMerge.OpenDataSource(Name=str(csv_path))
                try:
                    doc.Saved = True
                except Exception:
                    pass
            return {"hwnd": int(self.hwnd or 0)}
        if action == "trigger_contextual":
            target = kwargs.get("target", "")
            doc = getattr(self, "_fixture_doc", None) or (self.created[0] if self.created else None)
            if doc is None or getattr(doc, "closed", False):
                raise Refused("no open Word document is available to trigger contextual tabs")
            try:
                if bool(getattr(app, "PrintPreview", False)):
                    app.PrintPreview = False
            except Exception:
                pass
            try:
                app.ActiveWindow.View.SeekView = 0
                app.ActiveWindow.View.Type = 3
            except Exception:
                pass
            if target == "table":
                doc.Tables(1).Cell(1, 1).Range.Select()
            elif target in ("picture", "background_removal"):
                selected = False
                try:
                    doc.Shapes.Range(["FixturePic1", "FixturePic2"]).Select()
                    selected = True
                except Exception:
                    pass
                if not selected:
                    shapes = getattr(doc, "InlineShapes", None)
                    cnt = int(getattr(shapes, "Count", 0)) if shapes is not None else 0
                    for idx in range(1, cnt + 1):
                        ish = shapes.Item(idx) if hasattr(shapes, "Item") else shapes(idx)
                        if int(getattr(ish, "Type", 0)) == 3:
                            ish.Select()
                            selected = True
                            break
                if not selected:
                    raise Refused("Word contextual fixture has no inline picture (wdInlineShapePicture)")
            elif target == "shape":
                selected = False
                try:
                    doc.Shapes.Range(["FixtureShape1", "FixtureShape2"]).Select()
                    selected = True
                except Exception:
                    pass
                if not selected:
                    sh = doc.Shapes(1) if callable(getattr(doc, "Shapes", None)) else doc.Shapes.Item(1)
                    sh.Select()
                    try:
                        if hasattr(sh, "TextFrame") and sh.TextFrame.HasText:
                            sh.TextFrame.TextRange.Select()
                    except Exception:
                        pass
            elif target == "header_footer":
                app.ActiveWindow.View.SeekView = 1
            elif target == "equation":
                om = doc.OMaths(1) if callable(getattr(doc, "OMaths", None)) else doc.OMaths.Item(1)
                om.Range.Select()
            elif target == "chart":
                selected = False
                try:
                    doc.Shapes.Range(["FixtureChart1", "FixtureChart2"]).Select()
                    selected = True
                except Exception:
                    pass
                if not selected:
                    shapes = getattr(doc, "InlineShapes", None)
                    cnt = int(getattr(shapes, "Count", 0)) if shapes is not None else 0
                    for idx in range(1, cnt + 1):
                        ish = shapes.Item(idx) if hasattr(shapes, "Item") else shapes(idx)
                        if bool(getattr(ish, "HasChart", False)) or int(getattr(ish, "Type", 0)) == 12:
                            ish.Select()
                            selected = True
                            break
                if not selected:
                    raise Refused("Word contextual fixture has no inline chart")
            elif target == "smartart":
                selected = False
                try:
                    sa_sh = doc.Shapes("FixtureSmartArt1")
                    sa_sh.Select()
                    sa_sh.SmartArt.AllNodes(1).Shapes.Select()
                    selected = True
                except Exception:
                    pass
                if not selected:
                    shapes = getattr(doc, "InlineShapes", None)
                    cnt = int(getattr(shapes, "Count", 0)) if shapes is not None else 0
                    for idx in range(1, cnt + 1):
                        ish = shapes.Item(idx) if hasattr(shapes, "Item") else shapes(idx)
                        if bool(getattr(ish, "HasSmartArt", False)) or int(getattr(ish, "Type", 0)) == 15:
                            ish.Select()
                            try:
                                ish.SmartArt.AllNodes(1).Shapes.Select()
                            except Exception:
                                pass
                            selected = True
                            break
                if not selected:
                    raise Refused("Word contextual fixture has no inline SmartArt")
            elif target == "smartart_multi":
                try:
                    doc.Shapes.Range(["FixtureSmartArt1", "FixtureSmartArt2"]).Select()
                except Exception:
                    pass
            elif target == "svg":
                selected = False
                try:
                    doc.Shapes("FixtureSvg1").Select()
                    selected = True
                except Exception:
                    pass
                if not selected:
                    shapes = getattr(doc, "InlineShapes", None)
                    cnt = int(getattr(shapes, "Count", 0)) if shapes is not None else 0
                    for idx in range(1, cnt + 1):
                        ish = shapes.Item(idx) if hasattr(shapes, "Item") else shapes(idx)
                        if int(getattr(ish, "Type", 0)) in (17, 18):
                            ish.Select()
                            selected = True
                            break
                if not selected:
                    raise Refused("Word contextual fixture has no inline SVG graphic (wdInlineShapeGraphic)")
            elif target == "model3d":
                selected = False
                try:
                    doc.Shapes.Range(["Fixture3D1", "Fixture3D2"]).Select()
                    selected = True
                except Exception:
                    pass
                if not selected:
                    shapes = getattr(doc, "InlineShapes", None)
                    cnt = int(getattr(shapes, "Count", 0)) if shapes is not None else 0
                    for idx in range(1, cnt + 1):
                        ish = shapes.Item(idx) if hasattr(shapes, "Item") else shapes(idx)
                        if int(getattr(ish, "Type", 0)) in (19, 20):
                            ish.Select()
                            selected = True
                            break
                if not selected:
                    raise Refused("Word contextual fixture has no inline 3D model (wdInlineShape3DModel)")
            elif target == "outlining":
                app.ActiveWindow.View.Type = 2
            elif target == "print_preview":
                app.ActiveWindow.View.Type = 4
            elif target == "immersive_reader":
                app.ActiveWindow.View.Type = 3
            elif target == "reset":
                try:
                    doc.Range(0, 0).Select()
                except Exception:
                    pass
            else:
                raise Refused(f"unknown Word contextual trigger target {target!r}")
            try:
                wh = self.window_handle()
                if wh is not None:
                    self.hwnd = self._get_win().top(wh)
            except Exception:
                pass
            return {"hwnd": int(self.hwnd or 0)}
        raise Refused(f"unknown word_action {action!r}")

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
        others, failure, clipboard_failure = None, None, None  # unknown until counted: an instance whose contents are unknown is never quit
        metas = list(getattr(self, "_created_meta", ()))
        try:
            try:
                self._restore_saved_clipboard()
            except Exception as exc:
                clipboard_failure = f"{type(exc).__name__}: {exc}"
            fdoc = getattr(self, "_fixture_doc", None)
            if fdoc is not None and not getattr(fdoc, "closed", False):
                self._word_action_impl("close_fixture")
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
                if getattr(self, "_saved_clipboard", None) is not None:
                    try:
                        self._restore_saved_clipboard()
                        clipboard_failure = None
                    except Exception as exc:
                        clipboard_failure = f"{type(exc).__name__}: {exc}"
        if others:
            raise Refused(f"the {self.exe} instance holds {others} document(s) this tool did not create, so it was "
                          "left running")
        if others is None:
            raise Refused(f"the {self.exe} instance's documents could not be closed and counted ({failure}), so it "
                          "was left running")
        if not gone:
            raise Refused(f"the {self.exe} instance this tool started did not exit")
        if clipboard_failure is not None:
            raise Refused(f"the operator clipboard could not be restored ({clipboard_failure})")


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


def _dock_menus(root):
    out = []
    for top_child in root.children():
        if top_child.control_type == "Menu":
            out.append(top_child)
        elif getattr(top_child, "class_name", "") == "MsoDockTop":
            for c1 in top_child.children():
                if c1.control_type == "Menu":
                    out.append(c1)
                elif c1.name not in ("Ribbon Tabs", "Lower Ribbon"):
                    for c2 in descendants(c1, 3):
                        if c2.control_type == "Menu":
                            out.append(c2)
    return out


def _iter_unique_menu_items(menus, depth=10):
    visited_containers = set()
    seen_items = set()

    def walk(el, d):
        for c in el.children():
            ct = c.control_type
            if ct in ITEM_TYPES and c.name:
                rid = c.runtime_id()
                if rid not in seen_items:
                    seen_items.add(rid)
                    yield c
            if d > 0 and ct in ("Menu", "Group", "Pane", "List", "Custom", "Window"):
                crid = c.runtime_id()
                if crid not in visited_containers:
                    visited_containers.add(crid)
                    yield from walk(c, d - 1)

    for m in menus:
        mrid = m.runtime_id()
        if mrid not in visited_containers:
            visited_containers.add(mrid)
            yield from walk(m, depth)


def popup_items(root, popup_roots=(), label="popup", target=None, exclude_rids=frozenset()):
    """The items of the menu or gallery that just opened, once their reading is stable. Office exposes an open menu as
    a Menu element in the app window's own tree (menus nest, so items are taken once each by runtime id)."""
    is_live = target is not None and hasattr(target, "raw")

    def read():
        if is_live:
            target_menus = [c for c in target.children() if c.control_type == "Menu"]
            if not target_menus:
                target_menus = [e for e in descendants(target, 3) if e.control_type == "Menu"]
            if target_menus:
                menus = target_menus + list(popup_roots)
            elif popup_roots:
                menus = list(popup_roots)
            else:
                menus = _dock_menus(root)
            return [e for e in _iter_unique_menu_items(menus, 10) if e.runtime_id() not in exclude_rids]
        # Word nests an empty Menu shell around the menus that hold the items, so every open Menu is read.
        menus = [e for e in descendants(root, 30) if e.control_type == "Menu"] + list(popup_roots)
        seen, items = set(), []
        for e in (d for menu in menus for d in descendants(menu, 12)):
            if (
                e.control_type in ITEM_TYPES
                and e.name
                and e.runtime_id() not in seen
                and e.runtime_id() not in exclude_rids
            ):
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

    if is_live:
        last, last_sig, stable, saw_unstable = None, None, 0, False
        deadline = time.monotonic() + 4.0
        while time.monotonic() < deadline and stable < 1:
            items = attempt()
            if items is None:
                saw_unstable = True
                stable, last, last_sig = 0, None, None
                time.sleep(0.05)
                continue
            if not items and not saw_unstable:
                time.sleep(0.06)
                items = attempt() or []
                if not items:
                    return []
            sig = signature(items)
            if last_sig is not None and sig == last_sig and items:
                stable += 1
            else:
                if last_sig is not None and sig != last_sig:
                    saw_unstable = True
                stable = 0
            last, last_sig = items, sig
            if stable < 1:
                time.sleep(0.05)
        if stable < 1 and (last or saw_unstable):
            raise Refused(f"{label!r} items did not stabilise before timeout")
        return last or []

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
    try:
        for order, tab in enumerate(tab_elements):
            if tab.name not in wanted:
                continue
            launched.check_alone()
            if args.app == "word" and callable(getattr(launched, "word_action", None)):
                launched.word_action("prepare_core_tab", tab_name=tab.name)
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
    finally:
        if args.app == "word":
            if getattr(launched, "_saved_clipboard", None) is not None and callable(
                getattr(launched, "_restore_saved_clipboard", None)
            ):
                launched._restore_saved_clipboard()
            elif isinstance(launched, Proxy) and callable(getattr(launched, "word_action", None)):
                launched.word_action("restore_clipboard")
    if args.app == "word" and args.all_tabs and getattr(args, "layout", "classic") == "classic" and callable(getattr(launched, "word_action", None)):
        fixture_path = Path(getattr(args, "fixture", None) or WORD_DEFAULT_FIXTURE)
        records += capture_word_contextual_tabs(
            args, launched, uia, win, ctx, state, check_licensing,
            order_start=len(tab_elements), fixture_path=fixture_path,
        )
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


def lower_for_tab(uia, hwnd, tab_name, seconds=None):
    """The Lower Ribbon element for tab_name once its groups and controls are populated and stable."""
    if seconds is None:
        seconds = 12.0 if hasattr(uia, "client") else 5.0
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
    deadline = time.monotonic() + seconds
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


def _expand_submenus(parent_rec, items, ctx, launched, uia, win, seen_rids, depth=1, max_depth=2):
    out = []
    sub_pairs = []
    for order, item in enumerate(items):
        if not item.name:
            continue
        if parent_rec["id"].endswith(".show-markup.specific-people") and item.name != "All Reviewers":
            continue
        idmso = item.automation_id if item.automation_id in ctx.identifiers else None
        item_rec = ctx.base(
            ctx.ids.make(parent_rec["id"], item.name, item.automation_id),
            "menuItem",
            item.name,
            order,
            item,
            parent=parent_rec["id"],
            controlType="galleryItem" if item.control_type == "ListItem" else TYPES.get(item.control_type, "button"),
            idMso=idmso,
            baselineMissing=True if parent_rec.get("baselineMissing") or idmso is None else None,
        )
        out.append(item_rec)
        sub_pairs.append((item_rec, item))
    if depth <= max_depth:
        for item_rec, item_el in sub_pairs:
            try:
                if item_el.control_type != "MenuItem" or item_el.expand_state() is None:
                    continue
                if not bool(getattr(getattr(item_el, "raw", None), "CurrentIsEnabled", True)):
                    continue
            except Exception:
                continue
            if item_rec["label"] == "Gallery Filter":
                continue
            is_live_sub = hasattr(item_el, "raw")
            sub_items = []
            try:
                launched.check_alone()
                before_sub = win.popups(launched.proc.pid)
                item_el.expand()
                time.sleep(0.06 if is_live_sub else 0.1)
                opened_sub = [h for h in win.popups(launched.proc.pid) if h not in before_sub]
                sub_items = popup_items(
                    uia.element(launched.hwnd),
                    [uia.element(h) for h in opened_sub],
                    label=item_rec["label"],
                    target=item_el,
                    exclude_rids=seen_rids,
                )
            except Refused:
                raise
            except Exception as exc:
                raise Refused(f"failed to expand submenu {item_rec['id']!r} ({item_rec['label']!r}): {exc}") from exc
            if not sub_items:
                raise Refused(f"submenu {item_rec['id']!r} ({item_rec['label']!r}) opened no child menu items")
            next_seen = seen_rids | {x.runtime_id() for x in sub_items}
            out.extend(
                _expand_submenus(
                    item_rec, sub_items, ctx, launched, uia, win, next_seen, depth=depth + 1, max_depth=max_depth
                )
            )
            if not is_live_sub:
                try:
                    item_el.collapse()
                except Exception:
                    pass
    return out


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
                if rec.get("controlType") == "gallery" and getattr(element, "control_type", "") == "List":
                    list_items = [c for c in element.children() if c.control_type in ITEM_TYPES and c.name]
                    if list_items:
                        seen_rids = {x.runtime_id() for x in list_items}
                        out += _expand_submenus(rec, list_items, ctx, launched, uia, win, seen_rids, depth=1, max_depth=2)
                continue
            if rec.get("controlType") == "comboBox":
                combos += 1  # fonts, sizes: the machine's and the document's data, not the app's interface
                continue
            is_live = hasattr(target, "raw")
            if is_live and not bool(getattr(target.raw, "CurrentIsEnabled", True)):
                continue
            launched.check_alone()
            before = win.popups(launched.proc.pid)
            target.expand()
            items = []
            try:
                time.sleep(0.08 if is_live else 0.3)
                opened = [h for h in win.popups(launched.proc.pid) if h not in before]
                items = popup_items(
                    uia.element(launched.hwnd),
                    [uia.element(h) for h in opened],
                    label=rec["label"],
                    target=element if is_live else None,
                )
                if not items:
                    ctx.notes.append(f"{rec['label']!r} opened but no item was read from it")
                else:
                    seen_rids = {x.runtime_id() for x in items}
                    out += _expand_submenus(rec, items, ctx, launched, uia, win, seen_rids, depth=1, max_depth=2)
            finally:
                close_popup(
                    target,
                    lambda: [h for h in win.popups(launched.proc.pid) if h not in before]
                    or (
                        find(element, lambda e: e.control_type == "Menu", depth=3) is not None
                        if is_live
                        else find(uia.element(launched.hwnd), lambda e: e.control_type == "Menu", depth=30) is not None
                    ),
                    rec["label"],
                    check_alone=launched.check_alone,
                )
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
    is_live = hasattr(target, "raw")
    if check_alone is not None:
        check_alone()
    target.collapse()
    for _ in range(attempts):
        if wait_for(lambda: not still_open(), 0.4 if is_live else 1.5, 0.05 if is_live else 0.2):
            return
        if check_alone is not None:
            check_alone()
        target.expand()
        time.sleep(0.15 if is_live else 0.4)
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

    def word_action(self, action, **kwargs):
        answer = self.ask({"word_action": action, "kwargs": kwargs})
        if isinstance(answer, dict) and "ok" in answer:
            res = answer["ok"]
            if isinstance(res, dict) and res.get("hwnd"):
                self.hwnd = res["hwnd"]
            return res
        raise Refused(str(answer))


def converse(lines, reply, launched):
    """Serve a worker's requests until it reports its outcome; returns that outcome message."""
    for line in lines:
        message = json.loads(line)
        ask_val = message.get("ask")
        if ask_val == "check_alone":
            try:
                launched.check_alone()
                reply("ok")
            except Refused as exc:
                reply(str(exc))
            continue
        if isinstance(ask_val, dict) and "word_action" in ask_val:
            try:
                res = launched.word_action(ask_val["word_action"], **(ask_val.get("kwargs") or {}))
                reply({"ok": res})
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

            def timed_word_action(action, **kwargs):
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError(f"the capture worker timed out after {timeout}s")
                fn = getattr(launched, "word_action", None)
                if not callable(fn):
                    raise Refused("launched instance does not support word_action")
                try:
                    return apt.call(lambda: fn(action, **kwargs), timeout=remaining)
                except TimeoutError:
                    raise TimeoutError(f"the capture worker timed out after {timeout}s") from None

            timed_launched = types.SimpleNamespace(check_alone=timed_check_alone, word_action=timed_word_action)
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


WORD_DEFAULT_FIXTURE = Path(r"R:\scratch\fixtures\word-contextual.docx")
WORD_DEFAULT_RECIPIENTS = Path(r"R:\scratch\fixtures\word-recipients.csv")

WORD_CONTEXTUAL_TRIGGERS = (
    ("table", ("TabTableToolsDesign", "TabTableToolsLayout")),
    ("picture", ("TabPictureToolsFormat",)),
    ("shape", ("TabDrawingToolsFormat",)),
    ("header_footer", ("TabHeaderAndFooterToolsDesign",)),
    ("equation", ("TabEquationToolsDesign",)),
    ("chart", ("TabChartToolsDesignNew", "TabChartToolsFormatNew")),
    ("smartart", ("TabSmartArtToolsDesign", "TabSmartArtToolsFormat")),
    ("svg", ("TabGraphicsToolsFormat",)),
    ("model3d", ("Tab3DModelToolsFormat",)),
    ("outlining", ("TabOutlining",)),
    ("print_preview", ("TabPrintPreview",)),
    ("background_removal", ("TabBackgroundRemoval",)),
    ("immersive_reader", ("TabLearningTools",)),
)

WORD_REQUIRED_CORE_TABS = (
    "TabHome",
    "TabInsert",
    "TabDrawInk",
    "TabWordDesign",
    "TabPageLayoutWord",
    "TabReferences",
    "TabMailings",
    "TabReviewWord",
    "TabView",
    "TabDeveloper",
    "HelpTab",
)

WORD_REQUIRED_CONTEXTUAL_TABS = (
    "TabTableToolsDesign",
    "TabTableToolsLayout",
    "TabPictureToolsFormat",
    "TabDrawingToolsFormat",
    "TabHeaderAndFooterToolsDesign",
    "TabEquationToolsDesign",
    "TabChartToolsDesignNew",
    "TabChartToolsFormatNew",
    "TabSmartArtToolsDesign",
    "TabSmartArtToolsFormat",
    "TabGraphicsToolsFormat",
    "Tab3DModelToolsFormat",
    "TabOutlining",
    "TabPrintPreview",
    "TabBackgroundRemoval",
    "TabLearningTools",
)

WORD_RECONCILED_ABSENT_TABS = {
    "TabAddIns": "legacy CommandBar add-in container tab; hidden when no legacy add-in registers custom CommandBar controls",
    "TabSyntex": "SharePoint Syntex enterprise content assembly tab; requires a Microsoft Syntex tenant service license",
    "TabBlogPost": "legacy Weblog post editing tab; only loaded when Word starts in the deprecated Blog Post template mode",
    "TabBlogInsert": "legacy Weblog insert tab; only loaded when Word starts in the deprecated Blog Post template mode",
    "TabConflicts": "co-authoring server merge conflict resolution mode tab; only shown during an active sync conflict",
    "TabBroadcastPresentation": "retired Office Presentation Service broadcast mode tab",
    "TabChartToolsDesign": "legacy Office 2007-2010 chart contextual tab superseded by TabChartToolsDesignNew",
    "TabChartToolsLayout": "legacy Office 2007-2010 chart layout tab superseded by TabChartToolsDesignNew and TabChartToolsFormatNew",
    "TabChartToolsFormat": "legacy Office 2007-2010 chart format tab superseded by TabChartToolsFormatNew",
    "TabDrawingToolsFormatClassic": "legacy VML drawing/AutoShape tab superseded by DrawingML TabDrawingToolsFormat",
    "TabPictureToolsFormatClassic": "legacy VML picture tab superseded by DrawingML TabPictureToolsFormat",
    "TabTextBoxToolsFormat": "legacy VML text box tab superseded by DrawingML TabDrawingToolsFormat",
    "TabWordArtToolsFormat": "legacy VML WordArt tab superseded by DrawingML TabDrawingToolsFormat",
    "TabDiagramToolsFormatClassic": "legacy Office 2003 diagram tab superseded by SmartArt TabSmartArtToolsDesign and TabSmartArtToolsFormat",
    "TabOrganizationChartToolsFormat": "legacy Office 2003 organization chart tab superseded by SmartArt TabSmartArtToolsDesign and TabSmartArtToolsFormat",
    "TabInkToolsPens": "legacy contextual Ink Tools Pens tab superseded by the always-available Draw TabDrawInk tab",
}

WORD_EXPECTED_TAB_KEYTIPS = {
    "TabHome": "H",
    "TabInsert": "N",
    "TabDrawInk": "JI",
    "TabWordDesign": "G",
    "TabPageLayoutWord": "P",
    "TabReferences": "S",
    "TabMailings": "M",
    "TabReviewWord": "R",
    "TabView": "W",
    "TabDeveloper": "L",
    "HelpTab": "Y1",
    "TabTableToolsDesign": "JT",
    "TabTableToolsLayout": "JL",
    "TabPictureToolsFormat": "JP",
    "TabDrawingToolsFormat": "JD",
    "TabHeaderAndFooterToolsDesign": "JH",
    "TabEquationToolsDesign": "JE",
    "TabChartToolsDesignNew": "JC",
    "TabChartToolsFormatNew": "JA",
    "TabSmartArtToolsDesign": "JS",
    "TabSmartArtToolsFormat": "JO",
    "TabGraphicsToolsFormat": "JG",
    "Tab3DModelToolsFormat": "TI",
    "TabOutlining": "U",
    "TabPrintPreview": "P",
    "TabBackgroundRemoval": "B2",
    "TabLearningTools": "Y3",
}

WORD_EXPECTED_CONTROL_KEYTIPS = {
    "word.home.clipboard.paste": "V",
    "word.home.font.font": "FF",
    "word.home.font.bold": "1",
    "word.home.paragraph.borders": "B",
    "word.home.font.text-effects-and-typography": "FT",
    "word.home.font.text-effects-and-typography.outline": "O",
    "word.home.font.text-effects-and-typography.outline.weight": "W",
    "word.mailings.write-insert-fields.insert-merge-field": "I",
    "word.mailings.write-insert-fields.rules": "U",
    "word.mailings.finish.finish-merge": "F",
    "word.header-footer.close.close-header-and-footer": "C",
}

WORD_RECONCILED_UNKEYED_CONTROL_UIA_IDS = frozenset({
    "QuickStylesGallery",
    "QuickStylesSets",
    "TableStylesGalleryWord",
    "PictureStylesGallery",
    "ShapesInsertGallery",
    "ShapeStylesGallery",
    "TextStylesGallery",
    "EquationSymbolsInsertGallery",
    "ChartStylesGallery",
    "SmartArtLayoutGallery",
    "SmartArtStylesGallery",
    "GraphicsStylesGallery",
    "Gallery3DModelViewPresets",
})

WORD_RECONCILED_UNKEYED_MENU_LABELS = frozenset({
    "Gallery Filter",
    "Change List Level",
    "All",
    "No Online Content Available",
    "Microsoft Office Signature Line...",
    "Show Source Documents",
    "FirstName",
    "LastName",
    "Title",
    "City",
    "3:4",
    "4:5",
    "5:4",
    "Arrows",
    "Shadow",
    "Reflection",
    "Glow",
    "Bevel",
    "3-D Rotation",
    "Transform",
    "Basic Math",
    "Lines",
    "Up/Down Bars",
})

WORD_RECONCILED_UNEXPANDED_CONTROLS = frozenset({
    "word.home.sensitivity.sensitivity",
    "word.draw.drawing-tools.drawing-tools",
    "word.review.comments.show-comments",
    "word.review.protect.block-authors",
    "word.developer.protect.block-authors",
    "word.format.insert-shapes.change-shape",
})

WORD_SELECTION_FORMAT_SPLIT_BUTTON_IDS = frozenset({
    "word.home.font.underline",
    "word.home.paragraph.bullets",
    "word.home.paragraph.numbering",
    "word.home.paragraph.borders",
    "word.table-design.borders.borders",
})

WORD_BINARY_TOGGLE_SPLIT_BUTTON_IDS = frozenset({
    "word.home.voice.dictate",
    "word.review.markup.reviewing-pane",
    "word.review.tracking.track-changes",
    "word.review.ink.hide-ink",
    "word.picture-format.size.crop",
    "word.graphics-format.size.crop",
})

WORD_TOGGLE_SPLIT_BUTTON_IDS = WORD_SELECTION_FORMAT_SPLIT_BUTTON_IDS | WORD_BINARY_TOGGLE_SPLIT_BUTTON_IDS

WORD_SELECTION_FORMAT_TOGGLE_IDS = frozenset({
    "word.home.font.bold",
    "word.home.font.italic",
    "word.home.font.strikethrough",
    "word.home.font.subscript",
    "word.home.font.superscript",
    "word.home.paragraph.align-left",
    "word.home.paragraph.center",
    "word.home.paragraph.align-right",
    "word.home.paragraph.justify",
    "word.table-layout.alignment.align-top-left",
    "word.table-layout.alignment.align-top-center",
    "word.table-layout.alignment.align-top-right",
    "word.table-layout.alignment.align-center-left",
    "word.table-layout.alignment.align-center",
    "word.table-layout.alignment.align-center-right",
    "word.table-layout.alignment.align-bottom-left",
    "word.table-layout.alignment.align-bottom-center",
    "word.table-layout.alignment.align-bottom-right",
    "word.table-layout.data.repeat-header-rows",
    "word.equation.conversions.text",
})

WORD_VIEW_MODE_TOGGLE_IDS = frozenset({
    "word.view.views.read-mode",
    "word.view.views.print-layout",
    "word.view.views.web-layout",
    "word.view.views.outline",
    "word.view.views.draft",
    "word.view.immersive.focus",
    "word.view.immersive.immersive-reader",
    "word.view.page-movement.vertical",
    "word.view.page-movement.side-to-side",
    "word.immersive-reader.immersive-reader.text-spacing",
    "word.immersive-reader.immersive-reader.syllables",
})

WORD_PANE_TOGGLE_IDS = frozenset({
    "word.home.add-ins.add-ins",
    "word.layout.arrange.selection-pane",
    "word.review.protect.restrict-editing",
    "word.view.show.navigation-pane",
    "word.view.sharepoint.properties",
    "word.developer.protect.restrict-editing",
    "word.picture-format.accessibility.alt-text",
    "word.picture-format.arrange.selection-pane",
    "word.shape-format.accessibility.alt-text",
    "word.shape-format.arrange.selection-pane",
    "word.format.accessibility.alt-text",
    "word.format.arrange.selection-pane",
    "word.smartart-design.create-graphic.text-pane",
    "word.format-tabsmartarttoolsformat.accessibility.alt-text",
    "word.format-tabsmartarttoolsformat.arrange.selection-pane",
    "word.graphics-format.accessibility.alt-text",
    "word.graphics-format.arrange.selection-pane",
    "word.3d-model.accessibility.alt-text",
    "word.3d-model.arrange.selection-pane",
})

WORD_VISIBILITY_TOGGLE_IDS = frozenset({
    "word.home.paragraph.show-all",
    "word.draw.stencils.ruler",
    "word.view.show.ruler",
    "word.view.show.gridlines",
    "word.table-layout.table.view-gridlines",
    "word.outlining.outline-tools.show-text-formatting",
    "word.outlining.outline-tools.show-first-line-only",
    "word.outlining.master-document.show-document",
    "word.outlining.master-document.collapse-subdocuments",
    "word.print-preview.preview.show-ruler",
    "word.print-preview.preview.magnifier",
})

WORD_TOOL_MODE_TOGGLE_IDS = frozenset({
    "word.home.clipboard.format-painter",
    "word.draw.convert.ink-to-shape",
    "word.draw.replay.ink-replay",
    "word.developer.controls.design-mode",
    "word.table-design.borders.border-painter",
    "word.table-layout.draw.draw-table",
    "word.table-layout.draw.eraser",
    "word.picture-format.adjust.remove-background",
    "word.format-tabsmartarttoolsformat.shapes.edit-in-2-d",
    "word.3d-model.size.pan-zoom",
    "word.background-removal.refine.mark-areas-to-keep",
    "word.background-removal.refine.mark-areas-to-remove",
})

WORD_INSERTION_GALLERY_IDS = frozenset({
    "word.home.font.change-case",
    "word.insert.pages.cover-page",
    "word.insert.tables.table",
    "word.insert.illustrations.shapes",
    "word.insert.illustrations.screenshot",
    "word.insert.header-footer.header",
    "word.insert.header-footer.footer",
    "word.insert.text.text-box",
    "word.insert.text.quick-parts",
    "word.insert.text.wordart",
    "word.insert.symbols.symbol",
    "word.layout.page-setup.breaks",
    "word.layout.arrange.rotate",
    "word.references.table-of-contents.table-of-contents",
    "word.references.citations-bibliography.bibliography",
    "word.picture-format.arrange.rotate",
    "word.shape-format.insert-shapes.shapes",
    "word.shape-format.arrange.rotate",
    "word.header-footer.header-footer.header",
    "word.header-footer.header-footer.footer",
    "word.header-footer.insert.quick-parts",
    "word.equation.tools.equation",
    "word.equation.symbols.equation-symbols",
    "word.equation.structures.fraction",
    "word.equation.structures.script",
    "word.equation.structures.radical",
    "word.equation.structures.integral",
    "word.equation.structures.large-operator",
    "word.equation.structures.bracket",
    "word.equation.structures.function",
    "word.equation.structures.accent",
    "word.equation.structures.limit-and-log",
    "word.equation.structures.operator",
    "word.equation.structures.matrix",
    "word.format.insert-shapes.shapes",
    "word.format.insert-shapes.change-shape",
    "word.format.arrange.rotate",
    "word.format-tabsmartarttoolsformat.shapes.change-shape",
    "word.format-tabsmartarttoolsformat.arrange.rotate",
    "word.graphics-format.arrange.rotate",
})

WORD_DOCUMENT_GALLERY_IDS = frozenset({
    "word.design.document-formatting.themes",
    "word.design.document-formatting.style-set",
    "word.design.document-formatting.colors",
    "word.design.document-formatting.fonts",
    "word.design.document-formatting.paragraph-spacing",
    "word.design.document-formatting.effects",
    "word.design.page-background.watermark",
    "word.design.page-background.page-color",
    "word.draw.edit.format-background",
    "word.immersive-reader.immersive-reader.page-color",
    "word.references.citations-bibliography.change-provider",
})

WORD_SINGLE_CONTAINER_GALLERY_IDS = frozenset({
    "word.insert.text.drop-cap",
    "word.table-design.table-styles.table-styles",
    "word.table-design.borders.border-styles",
    "word.table-design.borders.pen-color",
    "word.picture-format.adjust.corrections",
    "word.picture-format.adjust.color",
    "word.picture-format.adjust.artistic-effects",
    "word.picture-format.adjust.transparency",
    "word.picture-format.picture-styles.picture-layout",
    "word.picture-format.size.crop",
    "word.shape-format.text.text-direction",
    "word.shape-format.text.align-text",
    "word.chart-design.chart-layouts.add-chart-element",
    "word.chart-design.chart-layouts.quick-layout",
    "word.chart-design.chart-styles.change-colors",
    "word.chart-design.chart-styles.quick-styles",
    "word.smartart-design.layouts.change-layout",
    "word.smartart-design.smartart-styles.change-colors",
    "word.smartart-design.smartart-styles.quick-styles",
    "word.graphics-format.size.crop",
    "word.3d-model.3d-model-views.views",
    "word.layout.arrange.position",
    "word.layout.arrange.wrap-text",
    "word.picture-format.arrange.position",
    "word.picture-format.arrange.wrap-text",
    "word.shape-format.arrange.position",
    "word.shape-format.arrange.wrap-text",
    "word.format.arrange.position",
    "word.format.arrange.wrap-text",
    "word.format-tabsmartarttoolsformat.arrange.position",
    "word.format-tabsmartarttoolsformat.arrange.wrap-text",
    "word.graphics-format.arrange.position",
    "word.graphics-format.arrange.wrap-text",
    "word.3d-model.arrange.position",
    "word.3d-model.arrange.wrap-text",
})

WORD_SECTION_GALLERY_IDS = frozenset({
    "word.layout.page-setup.margins",
    "word.layout.page-setup.orientation",
    "word.layout.page-setup.size",
    "word.layout.page-setup.columns",
    "word.print-preview.page-setup.margins",
    "word.print-preview.page-setup.orientation",
    "word.print-preview.page-setup.size",
})

WORD_NO_MIXED_GALLERY_IDS = (
    WORD_INSERTION_GALLERY_IDS
    | WORD_DOCUMENT_GALLERY_IDS
    | WORD_SINGLE_CONTAINER_GALLERY_IDS
    | frozenset({
        "word.home.clipboard.paste",
        "word.draw.drawing-tools.drawing-tools",
        "word.insert.header-footer.page-number",
        "word.header-footer.header-footer.page-number",
        "word.header-footer.insert.document-info",
        "word.insert.symbols.equation",
        "word.developer.controls.legacy-tools",
        "word.shape-format.insert-shapes.edit-shape",
    })
)

WORD_NO_MIXED_GALLERY_PREFIXES = tuple(f"{g}." for g in WORD_NO_MIXED_GALLERY_IDS)

WORD_NO_MIXED_SPINNER_IDS = frozenset({
    "word.header-footer.position.header-position-from-top",
    "word.header-footer.position.footer-position-from-bottom",
})

WORD_REQUIRED_GROUP_IDS = (
    "word.home.clipboard",
    "word.home.font",
    "word.home.paragraph",
    "word.home.styles",
    "word.home.editing",
    "word.home.voice",
    "word.home.sensitivity",
    "word.home.editor",
    "word.home.add-ins",
    "word.insert.pages",
    "word.insert.tables",
    "word.insert.illustrations",
    "word.insert.media",
    "word.insert.links",
    "word.insert.comments",
    "word.insert.header-footer",
    "word.insert.text",
    "word.insert.symbols",
    "word.insert.esignature",
    "word.draw.drawing-tools",
    "word.draw.undo",
    "word.draw.stencils",
    "word.draw.edit",
    "word.draw.convert",
    "word.draw.insert",
    "word.draw.replay",
    "word.draw.help",
    "word.design.document-formatting",
    "word.design.page-background",
    "word.layout.page-setup",
    "word.layout.paragraph",
    "word.layout.arrange",
    "word.references.table-of-contents",
    "word.references.footnotes",
    "word.references.citations-bibliography",
    "word.references.captions",
    "word.references.index",
    "word.references.table-of-authorities",
    "word.mailings.create",
    "word.mailings.start-mail-merge",
    "word.mailings.write-insert-fields",
    "word.mailings.preview-results",
    "word.mailings.finish",
    "word.review.proofing",
    "word.review.speech",
    "word.review.accessibility",
    "word.review.language",
    "word.review.comments",
    "word.review.markup",
    "word.review.tracking",
    "word.review.compare",
    "word.review.protect",
    "word.review.ink",
    "word.review.onenote",
    "word.view.views",
    "word.view.immersive",
    "word.view.page-movement",
    "word.view.show",
    "word.view.zoom",
    "word.view.window",
    "word.view.macros",
    "word.view.sharepoint",
    "word.developer.code",
    "word.developer.add-ins",
    "word.developer.controls",
    "word.developer.mapping",
    "word.developer.protect",
    "word.developer.templates",
    "word.help.help",
    "word.table-design.table-style-options",
    "word.table-design.table-styles",
    "word.table-design.borders",
    "word.table-layout.table",
    "word.table-layout.draw",
    "word.table-layout.rows-columns",
    "word.table-layout.merge",
    "word.table-layout.cell-size",
    "word.table-layout.alignment",
    "word.table-layout.data",
    "word.picture-format.adjust",
    "word.picture-format.picture-styles",
    "word.picture-format.accessibility",
    "word.picture-format.arrange",
    "word.picture-format.size",
    "word.shape-format.insert-shapes",
    "word.shape-format.shape-styles",
    "word.shape-format.wordart-styles",
    "word.shape-format.text",
    "word.shape-format.accessibility",
    "word.shape-format.arrange",
    "word.shape-format.size",
    "word.header-footer.header-footer",
    "word.header-footer.insert",
    "word.header-footer.navigation",
    "word.header-footer.options",
    "word.header-footer.position",
    "word.header-footer.close",
    "word.equation.tools",
    "word.equation.conversions",
    "word.equation.symbols",
    "word.equation.structures",
    "word.chart-design.chart-layouts",
    "word.chart-design.chart-styles",
    "word.chart-design.data",
    "word.chart-design.type",
    "word.format.current-selection",
    "word.format.insert-shapes",
    "word.format.shape-styles",
    "word.format.wordart-styles",
    "word.format.accessibility",
    "word.format.arrange",
    "word.format.size",
    "word.smartart-design.create-graphic",
    "word.smartart-design.layouts",
    "word.smartart-design.smartart-styles",
    "word.smartart-design.reset",
    "word.format-tabsmartarttoolsformat.shapes",
    "word.format-tabsmartarttoolsformat.shape-styles",
    "word.format-tabsmartarttoolsformat.wordart-styles",
    "word.format-tabsmartarttoolsformat.accessibility",
    "word.format-tabsmartarttoolsformat.arrange",
    "word.format-tabsmartarttoolsformat.size",
    "word.graphics-format.change",
    "word.graphics-format.graphics-styles",
    "word.graphics-format.accessibility",
    "word.graphics-format.arrange",
    "word.graphics-format.size",
    "word.3d-model.adjust",
    "word.3d-model.3d-model-views",
    "word.3d-model.accessibility",
    "word.3d-model.arrange",
    "word.3d-model.size",
    "word.outlining.outline-tools",
    "word.outlining.master-document",
    "word.outlining.close",
    "word.print-preview.print",
    "word.print-preview.page-setup",
    "word.print-preview.zoom",
    "word.print-preview.preview",
    "word.background-removal.refine",
    "word.background-removal.close",
    "word.immersive-reader.immersive-reader",
    "word.immersive-reader.close",
)

WORD_REQUIRED_CONTROL_IDS = (
    "word.home.clipboard.paste",
    "word.home.clipboard.cut",
    "word.home.clipboard.copy",
    "word.home.clipboard.format-painter",
    "word.home.clipboard.office-clipboard",
    "word.home.font.font",
    "word.home.font.font-size",
    "word.home.font.grow-font",
    "word.home.font.shrink-font",
    "word.home.font.change-case",
    "word.home.font.clear-formatting",
    "word.home.font.bold",
    "word.home.font.italic",
    "word.home.font.underline",
    "word.home.font.strikethrough",
    "word.home.font.subscript",
    "word.home.font.superscript",
    "word.home.font.text-effects-and-typography",
    "word.home.font.text-highlight-color",
    "word.home.font.font-color",
    "word.home.font.font-fontdialog",
    "word.home.paragraph.bullets",
    "word.home.paragraph.numbering",
    "word.home.paragraph.multilevel-list",
    "word.home.paragraph.decrease-indent",
    "word.home.paragraph.increase-indent",
    "word.home.paragraph.sort",
    "word.home.paragraph.show-all",
    "word.home.paragraph.align-left",
    "word.home.paragraph.center",
    "word.home.paragraph.align-right",
    "word.home.paragraph.justify",
    "word.home.paragraph.line-and-paragraph-spacing",
    "word.home.paragraph.shading",
    "word.home.paragraph.borders",
    "word.home.paragraph.paragraph",
    "word.home.styles.styles",
    "word.home.styles.styles-stylespane",
    "word.home.editing.find",
    "word.home.editing.replace",
    "word.home.editing.select",
    "word.home.voice.dictate",
    "word.home.sensitivity.sensitivity",
    "word.home.editor.editor",
    "word.home.add-ins.add-ins",
    "word.insert.pages.cover-page",
    "word.insert.pages.blank-page",
    "word.insert.pages.page-break",
    "word.insert.tables.table",
    "word.insert.illustrations.pictures",
    "word.insert.illustrations.shapes",
    "word.insert.illustrations.icons",
    "word.insert.illustrations.3d-models",
    "word.insert.illustrations.smartart",
    "word.insert.illustrations.chart",
    "word.insert.illustrations.screenshot",
    "word.insert.media.online-videos",
    "word.insert.links.link",
    "word.insert.links.bookmark",
    "word.insert.links.cross-reference",
    "word.insert.comments.comment",
    "word.insert.header-footer.header",
    "word.insert.header-footer.footer",
    "word.insert.header-footer.page-number",
    "word.insert.text.text-box",
    "word.insert.text.quick-parts",
    "word.insert.text.wordart",
    "word.insert.text.drop-cap",
    "word.insert.text.signature-line",
    "word.insert.text.date-time",
    "word.insert.text.object",
    "word.insert.symbols.equation",
    "word.insert.symbols.symbol",
    "word.insert.esignature.esignature-fields",
    "word.draw.drawing-tools.drawing-tools",
    "word.draw.drawing-tools.add",
    "word.draw.undo.can-t-undo",
    "word.draw.undo.can-t-repeat",
    "word.draw.stencils.ruler",
    "word.draw.edit.format-background",
    "word.draw.convert.ink-to-shape",
    "word.draw.convert.ink-to-math",
    "word.draw.insert.drawing-canvas",
    "word.draw.replay.ink-replay",
    "word.draw.help.ink-help",
    "word.design.document-formatting.themes",
    "word.design.document-formatting.style-set",
    "word.design.document-formatting.colors",
    "word.design.document-formatting.fonts",
    "word.design.document-formatting.paragraph-spacing",
    "word.design.document-formatting.effects",
    "word.design.document-formatting.set-as-default",
    "word.design.page-background.watermark",
    "word.design.page-background.page-color",
    "word.design.page-background.page-borders",
    "word.layout.page-setup.margins",
    "word.layout.page-setup.orientation",
    "word.layout.page-setup.size",
    "word.layout.page-setup.columns",
    "word.layout.page-setup.breaks",
    "word.layout.page-setup.line-numbers",
    "word.layout.page-setup.hyphenation",
    "word.layout.page-setup.page-setup",
    "word.layout.paragraph.indent-left",
    "word.layout.paragraph.more",
    "word.layout.paragraph.less",
    "word.layout.paragraph.indent-right",
    "word.layout.paragraph.more-2",
    "word.layout.paragraph.less-2",
    "word.layout.paragraph.spacing-before",
    "word.layout.paragraph.more-3",
    "word.layout.paragraph.less-3",
    "word.layout.paragraph.spacing-after",
    "word.layout.paragraph.more-4",
    "word.layout.paragraph.less-4",
    "word.layout.paragraph.paragraph",
    "word.layout.arrange.position",
    "word.layout.arrange.wrap-text",
    "word.layout.arrange.bring-forward",
    "word.layout.arrange.send-backward",
    "word.layout.arrange.selection-pane",
    "word.layout.arrange.align",
    "word.layout.arrange.group",
    "word.layout.arrange.rotate",
    "word.references.table-of-contents.table-of-contents",
    "word.references.table-of-contents.add-text",
    "word.references.table-of-contents.update-table",
    "word.references.footnotes.insert-footnote",
    "word.references.footnotes.insert-endnote",
    "word.references.footnotes.next-footnote",
    "word.references.footnotes.show-notes",
    "word.references.footnotes.footnote-and-endnote-dialog",
    "word.references.citations-bibliography.insert-citation",
    "word.references.citations-bibliography.manage-sources",
    "word.references.citations-bibliography.style",
    "word.references.citations-bibliography.bibliography",
    "word.references.citations-bibliography.change-provider",
    "word.references.captions.insert-caption",
    "word.references.captions.insert-table-of-figures",
    "word.references.captions.update-table",
    "word.references.captions.cross-reference",
    "word.references.index.mark-entry",
    "word.references.index.insert-index",
    "word.references.index.update-index",
    "word.references.table-of-authorities.mark-citation",
    "word.references.table-of-authorities.insert-table-of-authorities",
    "word.references.table-of-authorities.update-table",
    "word.mailings.create.envelopes",
    "word.mailings.create.labels",
    "word.mailings.start-mail-merge.start-mail-merge",
    "word.mailings.start-mail-merge.select-recipients",
    "word.mailings.start-mail-merge.edit-recipient-list",
    "word.mailings.write-insert-fields.highlight-merge-fields",
    "word.mailings.write-insert-fields.address-block",
    "word.mailings.write-insert-fields.greeting-line",
    "word.mailings.write-insert-fields.insert-merge-field",
    "word.mailings.write-insert-fields.rules",
    "word.mailings.write-insert-fields.match-fields",
    "word.mailings.write-insert-fields.update-labels",
    "word.mailings.preview-results.preview-results",
    "word.mailings.preview-results.first",
    "word.mailings.preview-results.previous",
    "word.mailings.preview-results.record",
    "word.mailings.preview-results.next",
    "word.mailings.preview-results.last",
    "word.mailings.preview-results.find-recipient",
    "word.mailings.preview-results.check-for-errors",
    "word.mailings.finish.finish-merge",
    "word.review.proofing.editor",
    "word.review.proofing.spelling-and-grammar",
    "word.review.proofing.thesaurus",
    "word.review.proofing.word-count",
    "word.review.speech.read-aloud",
    "word.review.accessibility.check-accessibility",
    "word.review.language.translate",
    "word.review.language.language",
    "word.review.comments.new-comment",
    "word.review.comments.delete",
    "word.review.comments.previous",
    "word.review.comments.next",
    "word.review.comments.show-comments",
    "word.review.markup.filter-all-markup",
    "word.review.markup.display-for-review",
    "word.review.markup.show-markup",
    "word.review.markup.reviewing-pane",
    "word.review.markup.change-tracking-options",
    "word.review.tracking.track-changes",
    "word.review.tracking.accept",
    "word.review.tracking.reject",
    "word.review.tracking.previous",
    "word.review.tracking.next",
    "word.review.compare.compare",
    "word.review.protect.block-authors",
    "word.review.protect.restrict-editing",
    "word.review.ink.hide-ink",
    "word.review.onenote.linked-notes",
    "word.view.views.read-mode",
    "word.view.views.print-layout",
    "word.view.views.web-layout",
    "word.view.views.outline",
    "word.view.views.draft",
    "word.view.immersive.focus",
    "word.view.immersive.immersive-reader",
    "word.view.page-movement.vertical",
    "word.view.page-movement.side-to-side",
    "word.view.show.ruler",
    "word.view.show.gridlines",
    "word.view.show.navigation-pane",
    "word.view.zoom.zoom",
    "word.view.zoom.100",
    "word.view.zoom.one-page",
    "word.view.zoom.multiple-pages",
    "word.view.zoom.page-width",
    "word.view.window.new-window",
    "word.view.window.arrange-all",
    "word.view.window.split",
    "word.view.window.view-side-by-side",
    "word.view.window.synchronous-scrolling",
    "word.view.window.reset-window-position",
    "word.view.window.switch-windows",
    "word.view.macros.macros",
    "word.view.sharepoint.properties",
    "word.developer.code.visual-basic",
    "word.developer.code.macros",
    "word.developer.code.record-macro",
    "word.developer.code.pause-recording",
    "word.developer.code.macro-security",
    "word.developer.add-ins.add-ins",
    "word.developer.add-ins.word-add-ins",
    "word.developer.add-ins.com-add-ins",
    "word.developer.controls.rich-text-content-control",
    "word.developer.controls.plain-text-content-control",
    "word.developer.controls.picture-content-control",
    "word.developer.controls.building-block-gallery-content-control",
    "word.developer.controls.check-box-content-control",
    "word.developer.controls.combo-box-content-control",
    "word.developer.controls.drop-down-list-content-control",
    "word.developer.controls.date-picker-content-control",
    "word.developer.controls.repeating-section-content-control",
    "word.developer.controls.legacy-tools",
    "word.developer.controls.design-mode",
    "word.developer.controls.properties",
    "word.developer.controls.group",
    "word.developer.mapping.xml-mapping-pane",
    "word.developer.protect.block-authors",
    "word.developer.protect.restrict-editing",
    "word.developer.templates.document-template",
    "word.help.help.help",
    "word.help.help.contact-support",
    "word.help.help.feedback",
    "word.help.help.show-training",
    "word.help.help.what-s-new",
    "word.table-design.table-style-options.header-row",
    "word.table-design.table-style-options.total-row",
    "word.table-design.table-style-options.banded-rows",
    "word.table-design.table-style-options.first-column",
    "word.table-design.table-style-options.last-column",
    "word.table-design.table-style-options.banded-columns",
    "word.table-design.table-styles.table-styles",
    "word.table-design.table-styles.shading",
    "word.table-design.borders.border-styles",
    "word.table-design.borders.pen-style",
    "word.table-design.borders.pen-weight",
    "word.table-design.borders.pen-color",
    "word.table-design.borders.borders",
    "word.table-design.borders.border-painter",
    "word.table-design.borders.borders-and-shading",
    "word.table-layout.table.select",
    "word.table-layout.table.view-gridlines",
    "word.table-layout.table.properties",
    "word.table-layout.draw.draw-table",
    "word.table-layout.draw.eraser",
    "word.table-layout.rows-columns.delete",
    "word.table-layout.rows-columns.insert-row-above",
    "word.table-layout.rows-columns.insert-row-below",
    "word.table-layout.rows-columns.insert-column-left",
    "word.table-layout.rows-columns.insert-column-right",
    "word.table-layout.rows-columns.insert-cells",
    "word.table-layout.merge.merge-cells",
    "word.table-layout.merge.split-cells",
    "word.table-layout.merge.split-table",
    "word.table-layout.cell-size.autofit",
    "word.table-layout.cell-size.table-row-height",
    "word.table-layout.cell-size.more",
    "word.table-layout.cell-size.less",
    "word.table-layout.cell-size.table-column-width",
    "word.table-layout.cell-size.more-2",
    "word.table-layout.cell-size.less-2",
    "word.table-layout.cell-size.distribute-rows",
    "word.table-layout.cell-size.distribute-columns",
    "word.table-layout.cell-size.properties",
    "word.table-layout.alignment.align-top-left",
    "word.table-layout.alignment.align-top-center",
    "word.table-layout.alignment.align-top-right",
    "word.table-layout.alignment.align-center-left",
    "word.table-layout.alignment.align-center",
    "word.table-layout.alignment.align-center-right",
    "word.table-layout.alignment.align-bottom-left",
    "word.table-layout.alignment.align-bottom-center",
    "word.table-layout.alignment.align-bottom-right",
    "word.table-layout.alignment.text-direction",
    "word.table-layout.alignment.cell-margins",
    "word.table-layout.data.sort",
    "word.table-layout.data.repeat-header-rows",
    "word.table-layout.data.convert-to-text",
    "word.table-layout.data.formula",
    "word.picture-format.adjust.remove-background",
    "word.picture-format.adjust.corrections",
    "word.picture-format.adjust.color",
    "word.picture-format.adjust.artistic-effects",
    "word.picture-format.adjust.transparency",
    "word.picture-format.adjust.compress-pictures",
    "word.picture-format.adjust.change-picture",
    "word.picture-format.adjust.reset-picture",
    "word.picture-format.picture-styles.quick-styles",
    "word.picture-format.picture-styles.picture-border",
    "word.picture-format.picture-styles.picture-effects",
    "word.picture-format.picture-styles.picture-layout",
    "word.picture-format.picture-styles.picture",
    "word.picture-format.accessibility.alt-text",
    "word.picture-format.arrange.position",
    "word.picture-format.arrange.wrap-text",
    "word.picture-format.arrange.bring-forward",
    "word.picture-format.arrange.send-backward",
    "word.picture-format.arrange.selection-pane",
    "word.picture-format.arrange.align",
    "word.picture-format.arrange.group",
    "word.picture-format.arrange.rotate",
    "word.picture-format.size.crop",
    "word.picture-format.size.shape-height",
    "word.picture-format.size.more",
    "word.picture-format.size.less",
    "word.picture-format.size.shape-width",
    "word.picture-format.size.more-2",
    "word.picture-format.size.less-2",
    "word.picture-format.size.size-and-position",
    "word.shape-format.insert-shapes.shapes",
    "word.shape-format.insert-shapes.edit-shape",
    "word.shape-format.insert-shapes.draw-text-box",
    "word.shape-format.shape-styles.quick-styles",
    "word.shape-format.shape-styles.shape-fill",
    "word.shape-format.shape-styles.shape-outline",
    "word.shape-format.shape-styles.shape-effects",
    "word.shape-format.shape-styles.format-object",
    "word.shape-format.wordart-styles.quick-styles",
    "word.shape-format.wordart-styles.text-fill",
    "word.shape-format.wordart-styles.text-outline",
    "word.shape-format.wordart-styles.text-effects",
    "word.shape-format.wordart-styles.format-text-effects",
    "word.shape-format.text.text-direction",
    "word.shape-format.text.align-text",
    "word.shape-format.text.create-link",
    "word.shape-format.accessibility.alt-text",
    "word.shape-format.arrange.position",
    "word.shape-format.arrange.wrap-text",
    "word.shape-format.arrange.bring-forward",
    "word.shape-format.arrange.send-backward",
    "word.shape-format.arrange.selection-pane",
    "word.shape-format.arrange.align",
    "word.shape-format.arrange.group",
    "word.shape-format.arrange.rotate",
    "word.shape-format.size.shape-height",
    "word.shape-format.size.more",
    "word.shape-format.size.less",
    "word.shape-format.size.shape-width",
    "word.shape-format.size.more-2",
    "word.shape-format.size.less-2",
    "word.shape-format.size.size-and-position",
    "word.header-footer.header-footer.header",
    "word.header-footer.header-footer.footer",
    "word.header-footer.header-footer.page-number",
    "word.header-footer.insert.date-time",
    "word.header-footer.insert.document-info",
    "word.header-footer.insert.quick-parts",
    "word.header-footer.insert.pictures",
    "word.header-footer.insert.online-pictures",
    "word.header-footer.navigation.go-to-header",
    "word.header-footer.navigation.go-to-footer",
    "word.header-footer.navigation.previous",
    "word.header-footer.navigation.next",
    "word.header-footer.navigation.link-to-previous",
    "word.header-footer.options.different-first-page",
    "word.header-footer.options.different-odd-even-pages",
    "word.header-footer.options.show-document-text",
    "word.header-footer.position.header-position-from-top",
    "word.header-footer.position.more",
    "word.header-footer.position.less",
    "word.header-footer.position.footer-position-from-bottom",
    "word.header-footer.position.more-2",
    "word.header-footer.position.less-2",
    "word.header-footer.position.insert-alignment-tab",
    "word.header-footer.close.close-header-and-footer",
    "word.equation.tools.equation",
    "word.equation.tools.ink-equation",
    "word.equation.conversions.unicode",
    "word.equation.conversions.latex",
    "word.equation.conversions.text",
    "word.equation.conversions.convert",
    "word.equation.conversions.equation-options",
    "word.equation.symbols.equation-symbols",
    "word.equation.structures.fraction",
    "word.equation.structures.script",
    "word.equation.structures.radical",
    "word.equation.structures.integral",
    "word.equation.structures.large-operator",
    "word.equation.structures.bracket",
    "word.equation.structures.function",
    "word.equation.structures.accent",
    "word.equation.structures.limit-and-log",
    "word.equation.structures.operator",
    "word.equation.structures.matrix",
    "word.chart-design.chart-layouts.add-chart-element",
    "word.chart-design.chart-layouts.quick-layout",
    "word.chart-design.chart-styles.change-colors",
    "word.chart-design.chart-styles.quick-styles",
    "word.chart-design.data.switch-row-column",
    "word.chart-design.data.select-data",
    "word.chart-design.data.edit-data",
    "word.chart-design.data.refresh-data",
    "word.chart-design.type.change-chart-type",
    "word.format.current-selection.chart-elements",
    "word.format.current-selection.format-selection",
    "word.format.current-selection.reset-to-match-style",
    "word.format.insert-shapes.shapes",
    "word.format.insert-shapes.change-shape",
    "word.format.shape-styles.quick-styles",
    "word.format.shape-styles.shape-fill",
    "word.format.shape-styles.shape-outline",
    "word.format.shape-styles.shape-effects",
    "word.format.shape-styles.format-object",
    "word.format.wordart-styles.quick-styles",
    "word.format.wordart-styles.text-fill",
    "word.format.wordart-styles.text-outline",
    "word.format.wordart-styles.text-effects",
    "word.format.wordart-styles.format-text-effects",
    "word.format.accessibility.alt-text",
    "word.format.arrange.position",
    "word.format.arrange.wrap-text",
    "word.format.arrange.bring-forward",
    "word.format.arrange.send-backward",
    "word.format.arrange.selection-pane",
    "word.format.arrange.align",
    "word.format.arrange.group",
    "word.format.arrange.rotate",
    "word.format.size.shape-height",
    "word.format.size.more",
    "word.format.size.less",
    "word.format.size.shape-width",
    "word.format.size.more-2",
    "word.format.size.less-2",
    "word.format.size.size-and-position",
    "word.smartart-design.create-graphic.add-shape",
    "word.smartart-design.create-graphic.add-bullet",
    "word.smartart-design.create-graphic.text-pane",
    "word.smartart-design.create-graphic.promote",
    "word.smartart-design.create-graphic.demote",
    "word.smartart-design.create-graphic.right-to-left",
    "word.smartart-design.create-graphic.move-before",
    "word.smartart-design.create-graphic.move-after",
    "word.smartart-design.create-graphic.layout",
    "word.smartart-design.layouts.change-layout",
    "word.smartart-design.smartart-styles.change-colors",
    "word.smartart-design.smartart-styles.quick-styles",
    "word.smartart-design.reset.reset-graphic",
    "word.format-tabsmartarttoolsformat.shapes.edit-in-2-d",
    "word.format-tabsmartarttoolsformat.shapes.change-shape",
    "word.format-tabsmartarttoolsformat.shapes.larger",
    "word.format-tabsmartarttoolsformat.shapes.smaller",
    "word.format-tabsmartarttoolsformat.shape-styles.quick-styles",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-fill",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-outline",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-effects",
    "word.format-tabsmartarttoolsformat.shape-styles.format-object",
    "word.format-tabsmartarttoolsformat.wordart-styles.quick-styles",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-fill",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-outline",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-effects",
    "word.format-tabsmartarttoolsformat.wordart-styles.format-text-effects",
    "word.format-tabsmartarttoolsformat.accessibility.alt-text",
    "word.format-tabsmartarttoolsformat.arrange.position",
    "word.format-tabsmartarttoolsformat.arrange.wrap-text",
    "word.format-tabsmartarttoolsformat.arrange.bring-forward",
    "word.format-tabsmartarttoolsformat.arrange.send-backward",
    "word.format-tabsmartarttoolsformat.arrange.selection-pane",
    "word.format-tabsmartarttoolsformat.arrange.align",
    "word.format-tabsmartarttoolsformat.arrange.group",
    "word.format-tabsmartarttoolsformat.arrange.rotate",
    "word.format-tabsmartarttoolsformat.size.shape-height",
    "word.format-tabsmartarttoolsformat.size.more",
    "word.format-tabsmartarttoolsformat.size.less",
    "word.format-tabsmartarttoolsformat.size.shape-width",
    "word.format-tabsmartarttoolsformat.size.more-2",
    "word.format-tabsmartarttoolsformat.size.less-2",
    "word.format-tabsmartarttoolsformat.size.size-and-position",
    "word.graphics-format.change.change-graphic",
    "word.graphics-format.change.convert-to-shape",
    "word.graphics-format.graphics-styles.graphics-styles",
    "word.graphics-format.graphics-styles.graphics-fill",
    "word.graphics-format.graphics-styles.graphics-outline",
    "word.graphics-format.graphics-styles.graphics-effects",
    "word.graphics-format.graphics-styles.format-graphic",
    "word.graphics-format.accessibility.alt-text",
    "word.graphics-format.arrange.position",
    "word.graphics-format.arrange.wrap-text",
    "word.graphics-format.arrange.bring-forward",
    "word.graphics-format.arrange.send-backward",
    "word.graphics-format.arrange.selection-pane",
    "word.graphics-format.arrange.align",
    "word.graphics-format.arrange.group",
    "word.graphics-format.arrange.rotate",
    "word.graphics-format.size.crop",
    "word.graphics-format.size.shape-height",
    "word.graphics-format.size.more",
    "word.graphics-format.size.less",
    "word.graphics-format.size.shape-width",
    "word.graphics-format.size.more-2",
    "word.graphics-format.size.less-2",
    "word.graphics-format.size.size-and-position",
    "word.3d-model.adjust.3d-models",
    "word.3d-model.adjust.reset-3d-model",
    "word.3d-model.3d-model-views.views",
    "word.3d-model.3d-model-views.format-3d-model",
    "word.3d-model.accessibility.alt-text",
    "word.3d-model.arrange.position",
    "word.3d-model.arrange.wrap-text",
    "word.3d-model.arrange.bring-forward",
    "word.3d-model.arrange.send-backward",
    "word.3d-model.arrange.selection-pane",
    "word.3d-model.arrange.align",
    "word.3d-model.arrange.group",
    "word.3d-model.size.pan-zoom",
    "word.3d-model.size.shape-height",
    "word.3d-model.size.more",
    "word.3d-model.size.less",
    "word.3d-model.size.shape-width",
    "word.3d-model.size.more-2",
    "word.3d-model.size.less-2",
    "word.3d-model.size.size-and-position",
    "word.outlining.outline-tools.promote-to-heading-1",
    "word.outlining.outline-tools.promote",
    "word.outlining.outline-tools.outline-level",
    "word.outlining.outline-tools.demote",
    "word.outlining.outline-tools.demote-to-body-text",
    "word.outlining.outline-tools.move-up",
    "word.outlining.outline-tools.move-down",
    "word.outlining.outline-tools.expand",
    "word.outlining.outline-tools.collapse",
    "word.outlining.outline-tools.show-level",
    "word.outlining.outline-tools.show-text-formatting",
    "word.outlining.outline-tools.show-first-line-only",
    "word.outlining.master-document.show-document",
    "word.outlining.master-document.collapse-subdocuments",
    "word.outlining.close.close-outline-view",
    "word.print-preview.print.print-preview-and-print",
    "word.print-preview.print.options",
    "word.print-preview.page-setup.margins",
    "word.print-preview.page-setup.orientation",
    "word.print-preview.page-setup.size",
    "word.print-preview.page-setup.page-setup",
    "word.print-preview.zoom.zoom",
    "word.print-preview.zoom.100",
    "word.print-preview.zoom.one-page",
    "word.print-preview.zoom.multiple-pages",
    "word.print-preview.zoom.page-width",
    "word.print-preview.preview.show-ruler",
    "word.print-preview.preview.magnifier",
    "word.print-preview.preview.shrink-one-page",
    "word.print-preview.preview.next-page",
    "word.print-preview.preview.previous-page",
    "word.print-preview.preview.close-print-preview",
    "word.background-removal.refine.mark-areas-to-keep",
    "word.background-removal.refine.mark-areas-to-remove",
    "word.background-removal.close.discard-all-changes",
    "word.background-removal.close.keep-changes",
    "word.immersive-reader.immersive-reader.column-width",
    "word.immersive-reader.immersive-reader.page-color",
    "word.immersive-reader.immersive-reader.line-focus",
    "word.immersive-reader.immersive-reader.text-spacing",
    "word.immersive-reader.immersive-reader.syllables",
    "word.immersive-reader.immersive-reader.read-aloud",
    "word.immersive-reader.close.close-immersive-reader",
)

WORD_SELECTION_COMBOBOX_IDS = frozenset({
    "word.home.font.font",
    "word.home.font.font-size",
    "word.outlining.outline-tools.outline-level",
})

WORD_REQUIRED_SUBMENU_PARENTS = (
    "word.home.font.underline.underline-color",
    "word.home.font.text-effects-and-typography.outline",
    "word.home.font.text-effects-and-typography.shadow",
    "word.home.font.text-effects-and-typography.reflection",
    "word.home.font.text-effects-and-typography.glow",
    "word.home.font.text-effects-and-typography.number-styles",
    "word.home.font.text-effects-and-typography.ligatures",
    "word.home.font.text-effects-and-typography.outline.weight",
    "word.home.font.text-effects-and-typography.outline.dashes",
    "word.home.font.text-effects-and-typography.glow.more-glow-colors",
    "word.home.font.font-color.gradient",
    "word.home.paragraph.multilevel-list.all",
    "word.insert.pages.cover-page.more-cover-pages-from-office-online",
    "word.insert.tables.table.quick-tables",
    "word.insert.header-footer.header.more-headers-from-office-online",
    "word.insert.header-footer.footer.more-footers-from-office-online",
    "word.insert.header-footer.page-number.top-of-page",
    "word.insert.header-footer.page-number.bottom-of-page",
    "word.insert.header-footer.page-number.page-margins",
    "word.insert.header-footer.page-number.current-position",
    "word.insert.header-footer.page-number.top-of-page.more-page-numbers-from-office-online",
    "word.insert.header-footer.page-number.bottom-of-page.more-page-numbers-from-office-online",
    "word.insert.header-footer.page-number.page-margins.more-page-numbers-from-office-online",
    "word.insert.header-footer.page-number.current-position.more-page-numbers-from-office-online",
    "word.insert.text.text-box.more-text-boxes-from-office-online",
    "word.insert.text.quick-parts.autotext",
    "word.insert.text.quick-parts.document-property",
    "word.insert.symbols.equation.more-equations-from-office-online",
    "word.draw.edit.format-background.page-color",
    "word.design.page-background.watermark.more-watermarks-from-office-online",
    "word.references.table-of-contents.table-of-contents.more-tables-of-contents-from-office-online",
    "word.review.markup.show-markup.balloons",
    "word.review.markup.show-markup.specific-people",
    "word.picture-format.adjust.color.more-variations",
    "word.picture-format.picture-styles.picture-border.weight",
    "word.picture-format.picture-styles.picture-border.sketched",
    "word.picture-format.picture-styles.picture-border.dashes",
    "word.picture-format.picture-styles.picture-effects.preset",
    "word.picture-format.picture-styles.picture-effects.shadow",
    "word.picture-format.picture-styles.picture-effects.reflection",
    "word.picture-format.picture-styles.picture-effects.glow",
    "word.picture-format.picture-styles.picture-effects.soft-edges",
    "word.picture-format.picture-styles.picture-effects.bevel",
    "word.picture-format.picture-styles.picture-effects.3-d-rotation",
    "word.picture-format.picture-styles.picture-effects.glow.more-glow-colors",
    "word.picture-format.size.crop.crop-to-shape",
    "word.picture-format.size.crop.aspect-ratio",
    "word.shape-format.insert-shapes.edit-shape.change-shape",
    "word.shape-format.shape-styles.quick-styles.all",
    "word.shape-format.shape-styles.quick-styles.other-theme-fills",
    "word.shape-format.shape-styles.shape-fill.gradient",
    "word.shape-format.shape-styles.shape-fill.texture",
    "word.shape-format.shape-styles.shape-outline.weight",
    "word.shape-format.shape-styles.shape-outline.sketched",
    "word.shape-format.shape-styles.shape-outline.dashes",
    "word.shape-format.shape-styles.shape-effects.preset",
    "word.shape-format.shape-styles.shape-effects.shadow",
    "word.shape-format.shape-styles.shape-effects.reflection",
    "word.shape-format.shape-styles.shape-effects.glow",
    "word.shape-format.shape-styles.shape-effects.soft-edges",
    "word.shape-format.shape-styles.shape-effects.bevel",
    "word.shape-format.shape-styles.shape-effects.3-d-rotation",
    "word.shape-format.shape-styles.shape-effects.glow.more-glow-colors",
    "word.shape-format.wordart-styles.text-fill.gradient",
    "word.shape-format.wordart-styles.text-outline.weight",
    "word.shape-format.wordart-styles.text-outline.dashes",
    "word.shape-format.wordart-styles.text-effects.shadow",
    "word.shape-format.wordart-styles.text-effects.reflection",
    "word.shape-format.wordart-styles.text-effects.glow",
    "word.shape-format.wordart-styles.text-effects.bevel",
    "word.shape-format.wordart-styles.text-effects.3-d-rotation",
    "word.shape-format.wordart-styles.text-effects.transform",
    "word.shape-format.wordart-styles.text-effects.glow.more-glow-colors",
    "word.header-footer.header-footer.header.more-headers-from-office-online",
    "word.header-footer.header-footer.footer.more-footers-from-office-online",
    "word.header-footer.header-footer.page-number.top-of-page",
    "word.header-footer.header-footer.page-number.bottom-of-page",
    "word.header-footer.header-footer.page-number.page-margins",
    "word.header-footer.header-footer.page-number.current-position",
    "word.header-footer.header-footer.page-number.top-of-page.more-page-numbers-from-office-online",
    "word.header-footer.header-footer.page-number.bottom-of-page.more-page-numbers-from-office-online",
    "word.header-footer.header-footer.page-number.page-margins.more-page-numbers-from-office-online",
    "word.header-footer.header-footer.page-number.current-position.more-page-numbers-from-office-online",
    "word.header-footer.insert.document-info.document-property",
    "word.header-footer.insert.quick-parts.autotext",
    "word.header-footer.insert.quick-parts.document-property",
    "word.equation.tools.equation.more-equations-from-office-online",
    "word.equation.symbols.equation-symbols.basic-math",
    "word.chart-design.chart-layouts.add-chart-element.axes",
    "word.chart-design.chart-layouts.add-chart-element.axis-titles",
    "word.chart-design.chart-layouts.add-chart-element.chart-title",
    "word.chart-design.chart-layouts.add-chart-element.data-labels",
    "word.chart-design.chart-layouts.add-chart-element.data-table",
    "word.chart-design.chart-layouts.add-chart-element.error-bars",
    "word.chart-design.chart-layouts.add-chart-element.gridlines",
    "word.chart-design.chart-layouts.add-chart-element.legend",
    "word.chart-design.chart-layouts.add-chart-element.trendline",
    "word.format.shape-styles.quick-styles.all",
    "word.format.shape-styles.shape-fill.gradient",
    "word.format.shape-styles.shape-fill.texture",
    "word.format.shape-styles.shape-outline.weight",
    "word.format.shape-styles.shape-outline.dashes",
    "word.format.shape-styles.shape-effects.preset",
    "word.format.shape-styles.shape-effects.shadow",
    "word.format.shape-styles.shape-effects.glow",
    "word.format.shape-styles.shape-effects.soft-edges",
    "word.format.shape-styles.shape-effects.bevel",
    "word.format.shape-styles.shape-effects.3-d-rotation",
    "word.format.shape-styles.shape-effects.glow.more-glow-colors",
    "word.format.wordart-styles.text-fill.gradient",
    "word.format.wordart-styles.text-fill.texture",
    "word.format.wordart-styles.text-outline.weight",
    "word.format.wordart-styles.text-outline.dashes",
    "word.format.wordart-styles.text-effects.shadow",
    "word.format.wordart-styles.text-effects.reflection",
    "word.format.wordart-styles.text-effects.glow",
    "word.format.wordart-styles.text-effects.glow.more-glow-colors",
    "word.format-tabsmartarttoolsformat.shape-styles.quick-styles.all",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-fill.gradient",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-fill.texture",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-outline.weight",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-outline.sketched",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-outline.dashes",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-effects.preset",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-effects.shadow",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-effects.reflection",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-effects.glow",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-effects.soft-edges",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-effects.bevel",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-effects.3-d-rotation",
    "word.format-tabsmartarttoolsformat.shape-styles.shape-effects.glow.more-glow-colors",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-fill.gradient",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-fill.texture",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-outline.weight",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-outline.dashes",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-effects.shadow",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-effects.reflection",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-effects.glow",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-effects.bevel",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-effects.3-d-rotation",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-effects.transform",
    "word.format-tabsmartarttoolsformat.wordart-styles.text-effects.glow.more-glow-colors",
    "word.graphics-format.graphics-styles.graphics-outline.weight",
    "word.graphics-format.graphics-styles.graphics-outline.dashes",
    "word.graphics-format.graphics-styles.graphics-effects.preset",
    "word.graphics-format.graphics-styles.graphics-effects.shadow",
    "word.graphics-format.graphics-styles.graphics-effects.reflection",
    "word.graphics-format.graphics-styles.graphics-effects.glow",
    "word.graphics-format.graphics-styles.graphics-effects.soft-edges",
    "word.graphics-format.graphics-styles.graphics-effects.bevel",
    "word.graphics-format.graphics-styles.graphics-effects.3-d-rotation",
    "word.graphics-format.graphics-styles.graphics-effects.glow.more-glow-colors",
    "word.graphics-format.size.crop.crop-to-shape",
    "word.graphics-format.size.crop.aspect-ratio",
)

WORD_REQUIRED_EXPANDED_PARENTS = (
    "word.home.clipboard.paste",
    "word.home.paragraph.bullets",
    "word.home.paragraph.numbering",
    "word.home.paragraph.multilevel-list",
    "word.home.paragraph.line-and-paragraph-spacing",
    "word.home.paragraph.shading",
    "word.home.paragraph.borders",
    "word.home.styles.styles",
    "word.home.font.underline.underline-color",
    "word.home.font.text-effects-and-typography",
    "word.home.font.text-effects-and-typography.outline",
    "word.home.font.text-effects-and-typography.outline.weight",
    "word.home.font.text-effects-and-typography.shadow",
    "word.home.font.text-effects-and-typography.reflection",
    "word.home.font.text-effects-and-typography.glow",
    "word.home.editing.find",
    "word.home.editing.select",
    "word.insert.tables.table",
    "word.insert.illustrations.pictures",
    "word.insert.illustrations.shapes",
    "word.insert.header-footer.header",
    "word.insert.header-footer.footer",
    "word.insert.header-footer.page-number",
    "word.insert.text.text-box",
    "word.insert.text.quick-parts",
    "word.insert.text.wordart",
    "word.insert.text.drop-cap",
    "word.insert.symbols.equation",
    "word.insert.symbols.symbol",
    "word.draw.drawing-tools.add",
    "word.draw.edit.format-background",
    "word.draw.edit.format-background.page-color",
    "word.design.document-formatting.themes",
    "word.design.document-formatting.style-set",
    "word.design.document-formatting.colors",
    "word.design.document-formatting.fonts",
    "word.design.document-formatting.paragraph-spacing",
    "word.design.document-formatting.effects",
    "word.design.page-background.watermark",
    "word.design.page-background.page-color",
    "word.layout.page-setup.margins",
    "word.layout.page-setup.orientation",
    "word.layout.page-setup.size",
    "word.layout.page-setup.columns",
    "word.layout.page-setup.breaks",
    "word.layout.page-setup.line-numbers",
    "word.layout.page-setup.hyphenation",
    "word.layout.arrange.position",
    "word.layout.arrange.wrap-text",
    "word.layout.arrange.bring-forward",
    "word.layout.arrange.send-backward",
    "word.layout.arrange.align",
    "word.layout.arrange.group",
    "word.layout.arrange.rotate",
    "word.references.table-of-contents.table-of-contents",
    "word.mailings.start-mail-merge.start-mail-merge",
    "word.mailings.start-mail-merge.select-recipients",
    "word.mailings.write-insert-fields.insert-merge-field",
    "word.mailings.write-insert-fields.rules",
    "word.mailings.finish.finish-merge",
    "word.review.comments.delete",
    "word.review.tracking.track-changes",
    "word.review.tracking.accept",
    "word.review.tracking.reject",
    "word.review.markup.show-markup",
    "word.review.markup.show-markup.balloons",
    "word.developer.controls.group",
    "word.table-design.table-styles.table-styles",
    "word.table-design.borders.borders",
    "word.picture-format.picture-styles.quick-styles",
    "word.picture-format.arrange.bring-forward",
    "word.picture-format.arrange.send-backward",
    "word.picture-format.arrange.group",
    "word.shape-format.shape-styles.quick-styles",
    "word.shape-format.shape-styles.shape-effects",
    "word.shape-format.wordart-styles.quick-styles",
    "word.shape-format.wordart-styles.text-fill",
    "word.shape-format.wordart-styles.text-outline",
    "word.shape-format.wordart-styles.text-effects",
    "word.shape-format.text.text-direction",
    "word.shape-format.arrange.group",
    "word.equation.tools.equation",
    "word.equation.symbols.equation-symbols",
    "word.equation.structures.fraction",
    "word.chart-design.chart-styles.quick-styles",
    "word.format.arrange.bring-forward",
    "word.format.arrange.send-backward",
    "word.format.arrange.group",
    "word.format.arrange.rotate",
    "word.smartart-design.create-graphic.layout",
    "word.smartart-design.layouts.change-layout",
    "word.smartart-design.smartart-styles.quick-styles",
    "word.format-tabsmartarttoolsformat.arrange.bring-forward",
    "word.format-tabsmartarttoolsformat.arrange.send-backward",
    "word.format-tabsmartarttoolsformat.arrange.group",
    "word.graphics-format.graphics-styles.graphics-styles",
    "word.graphics-format.arrange.bring-forward",
    "word.graphics-format.arrange.send-backward",
    "word.3d-model.3d-model-views.views",
    "word.3d-model.arrange.bring-forward",
    "word.3d-model.arrange.send-backward",
    "word.3d-model.arrange.group",
)

CONTEXTUAL_TAB_BEHAVIOURS = {
    "TabTableToolsDesign": "Appears under Table Tools when the insertion point or selection is inside a document table; hosts table style options, table style gallery presets, shading and border formatting.",
    "TabTableToolsLayout": "Appears under Table Tools when the insertion point or selection is inside a document table; hosts table selection, row and column insertion/deletion, cell merging/splitting, cell size, alignment and table data sorting/formulas.",
    "TabPictureToolsFormat": "Appears under Picture Tools when an inline or floating raster picture is selected; hosts background removal, image corrections, artistic effects, picture styles, alt text, arrangement and cropping.",
    "TabDrawingToolsFormat": "Appears under Drawing Tools when an AutoShape, text box, WordArt object or drawing canvas is selected; hosts shape insertion, shape styles, WordArt text styles, text direction, arrangement and size.",
    "TabHeaderAndFooterToolsDesign": "Appears under Header & Footer Tools when the active window's SeekView is inside a section header or footer story; hosts header/footer galleries, page numbers, date/time fields, header/footer navigation, section linking and position offsets.",
    "TabEquationToolsDesign": "Appears under Equation Tools when the insertion point or selection is inside an OMath equation zone; hosts equation templates, TeX/Unicode conversion, math symbol gallery and structural math templates (fractions, scripts, radicals, integrals, operators, brackets, functions, accents, limits and matrices).",
    "TabChartToolsDesignNew": "Appears under Chart Tools when an embedded DrawingML chart is selected; hosts chart element insertion, quick layouts, chart color palettes, chart style gallery presets, data source editing and chart type switching.",
    "TabChartToolsFormatNew": "Appears under Chart Tools when an embedded DrawingML chart or chart element is selected; hosts chart element target selection, format pane opening, shape insertion, shape styles, WordArt styles, arrangement and chart dimensions.",
    "TabSmartArtToolsDesign": "Appears under SmartArt Tools when a SmartArt diagram or diagram node is selected; hosts node creation and hierarchy promotion/demotion, diagram layout gallery, SmartArt style presets and diagram reset.",
    "TabSmartArtToolsFormat": "Appears under SmartArt Tools when a SmartArt diagram or diagram node is selected; hosts 2-D editing, shape geometry changes, shape styles, WordArt text styles, arrangement and diagram/node sizing.",
    "TabGraphicsToolsFormat": "Appears under Graphics Tools when an inline or floating scalable vector graphic (SVG, wdInlineShapeGraphic) is selected; hosts convert-to-shape, graphics styles, graphics fill/outline/effects, alt text, arrangement and cropping/sizing.",
    "Tab3DModelToolsFormat": "Appears under 3D Model Tools when an inline or floating 3D model (wdInlineShape3DModel) is selected; hosts 3D model insertion, 3D camera view presets, alternative text, arrangement and pan/zoom/size controls.",
    "TabOutlining": "Appears as a mode tab at the left of the ribbon when the active document window switches to Outline view (View Type wdOutlineView); hosts heading level promotion/demotion, paragraph movement, outline expansion/collapse, level filtering and master/subdocument management.",
    "TabPrintPreview": "Appears as a mode tab when Print Preview Edit Mode (View Type wdPrintPreview) is active; hosts page setup, zoom, page movement, ruler/magnifier toggles, shrink-one-page and Close Print Preview.",
    "TabBackgroundRemoval": "Appears as a modal editing tab when Remove Background is invoked on a selected picture; hosts foreground mark-to-keep and background mark-to-remove brushes, mark deletion, discard changes and keep changes.",
    "TabLearningTools": "Appears under Immersive when Immersive Reader mode is active from the View tab; hosts column width, page colour, line focus, text spacing, syllable splitting and Read Aloud playback.",
}


def normalize_word_label(text):
    import unicodedata
    t = strip_control_chars(text or "")
    t = re.sub(r"(\d)([\u00bc\u00bd\u00be])", r"\1 \2", t)
    t = t.replace("\u00bc", "1/4").replace("\u00bd", "1/2").replace("\u00be", "3/4")
    t = re.sub(r"\bOffice\.com\b", "Office Online", t, flags=re.IGNORECASE)
    t = t.replace("(Q.E.D.)", "(QED)")
    out = []
    for ch in t:
        if ord(ch) >= 0x80 and ch != "\u2026":
            nfkc = unicodedata.normalize("NFKC", ch).replace("\u2044", "/")
            if nfkc != ch and any(0x21 <= ord(x) < 0x7F for x in nfkc):
                out.append(nfkc)
                continue
        out.append(ch)
    t = "".join(out)
    t = re.sub(r",\s*\u2026\s*,", " ...", t)
    t = re.sub(r"([.\u2026])\s*[,;:]", r"\1", t)
    t = re.sub(r"(\.\.\.|\u2026)(?=[A-Za-z0-9])", r"\1 ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > 110:
        cut = t[:105].rsplit(" ", 1)[0].rstrip(" ,;:.…-")
        t = f"{cut}..."
    return t


def _normalize_record_tree(records):
    ids = Ids()
    id_map = {}
    out = []
    for rec in records:
        r = dict(rec)
        old_id = r["id"]
        old_label = r["label"]
        new_label = normalize_word_label(old_label)
        r["label"] = new_label
        parent = r.get("parent")
        if parent:
            parent = id_map.get(parent, parent)
            r["parent"] = parent
        if old_label != new_label or len(old_id) > 190:
            prefix = parent if parent else r["app"]
            disc = r.get("uiaId") or r.get("idMso") or ""
            new_id = ids.make(prefix, new_label, disc)
            while len(new_id) > 195:
                short_lbl = new_label[:60].rsplit(" ", 1)[0]
                new_id = ids.make(prefix, short_lbl, disc)
        else:
            new_id = old_id
            ids.taken.add(new_id)
        id_map[old_id] = new_id
        r["id"] = new_id
        out.append(r)
    by_parent = {}
    for r in out:
        p = r.get("parent")
        if p is not None and r.get("kind") != "group":
            by_parent.setdefault(p, []).append(r)
    for siblings in by_parent.values():
        for idx, s in enumerate(siblings):
            s["order"] = idx
    return out


def _invoke_or_toggle_uia_button(el):
    if el is None:
        return False
    if callable(getattr(el, "invoke", None)):
        el.invoke()
        return True
    if callable(getattr(el, "toggle", None)):
        el.toggle()
        return True
    if el.can_toggle() and hasattr(el, "pattern"):
        p = el.pattern("toggle")
        if p is not None:
            p.Toggle()
            return True
    raw = getattr(el, "raw", None)
    u = getattr(getattr(el, "uia", None), "U", None)
    if raw is not None and u is not None:
        inv = raw.GetCurrentPattern(u.UIA_InvokePatternId)
        if inv:
            inv.QueryInterface(u.IUIAutomationInvokePattern).Invoke()
            return True
    return False


WORD_CONTEXTUAL_TAB_GROUPS = {
    "TabTableToolsDesign": ("Table Tools", "Table Design"),
    "TabTableToolsLayout": ("Table Tools", "Layout"),
    "TabPictureToolsFormat": ("Picture Tools", "Picture Format"),
    "TabDrawingToolsFormat": ("Drawing Tools", "Shape Format"),
    "TabHeaderAndFooterToolsDesign": ("Header & Footer Tools", "Header & Footer"),
    "TabEquationToolsDesign": ("Equation Tools", "Equation"),
    "TabChartToolsDesignNew": ("Chart Tools", "Chart Design"),
    "TabChartToolsFormatNew": ("Chart Tools", "Format"),
    "TabSmartArtToolsDesign": ("SmartArt Tools", "SmartArt Design"),
    "TabSmartArtToolsFormat": ("SmartArt Tools", "Format"),
    "TabGraphicsToolsFormat": ("Graphics Tools", "Graphics Format"),
    "Tab3DModelToolsFormat": ("3D Model Tools", "3D Model"),
    "TabOutlining": (None, "Outlining"),
    "TabPrintPreview": (None, "Print Preview"),
    "TabBackgroundRemoval": (None, "Background Removal"),
    "TabLearningTools": ("Immersive", "Immersive Reader"),
}


def _find_word_contextual_tab(tabs_bar, expected_aid):
    grp_name, tab_name = WORD_CONTEXTUAL_TAB_GROUPS.get(expected_aid, (None, None))
    for child in tabs_bar.children():
        if child.control_type == "TabItem" and child.automation_id == expected_aid:
            return child
        if child.control_type == "Group":
            for sub in child.children():
                if sub.control_type == "TabItem" and sub.automation_id == expected_aid:
                    return sub
    for child in tabs_bar.children():
        if grp_name is None and child.control_type == "TabItem" and tab_name and child.name == tab_name:
            child.automation_id = expected_aid
            return child
        if child.control_type == "Group" and (grp_name is None or child.name == grp_name):
            for sub in child.children():
                if sub.control_type == "TabItem" and tab_name and sub.name == tab_name:
                    sub.automation_id = expected_aid
                    return sub
    return None


def _select_word_tab(tab_el, uia, hwnd):
    try:
        tab_el.select()
    except Exception:
        pass
    raw = getattr(tab_el, "raw", None)
    if raw is not None and first_group_name(uia.element(hwnd)) != tab_el.name:
        if not wait_for(lambda: first_group_name(uia.element(hwnd)) == tab_el.name, 1.0, 0.15):
            try:
                u = uia.U
                leg = raw.GetCurrentPattern(u.UIA_LegacyIAccessiblePatternId)
                if leg:
                    leg.QueryInterface(u.IUIAutomationLegacyIAccessiblePattern).DoDefaultAction()
            except Exception:
                pass


def capture_word_contextual_tabs(args, launched, uia, win, ctx, state, check_licensing, order_start=11, fixture_path=None):
    """Open `fixture_path` (defaulting to `R:\\scratch\\fixtures\\word-contextual.docx`), trigger each contextual and
    mode tab via Word's object model and commands, capture every resulting `contextualTab` record, and close the
    fixture without modifying it."""
    fpath = Path(fixture_path or WORD_DEFAULT_FIXTURE)
    launched.word_action("open_fixture", path=str(fpath))
    out = []
    captured_idmsos = set()
    next_order = order_start
    try:
        for target, expected_tab_ids in WORD_CONTEXTUAL_TRIGGERS:
            launched.check_alone()
            launched.word_action("trigger_contextual", target=target)
            time.sleep(0.2)
            root = uia.element(launched.hwnd)
            tabs_bar = wait_for(lambda: find(uia.element(launched.hwnd), lambda e: e.control_type == "Tab" and e.name == "Ribbon Tabs"))
            if not tabs_bar:
                raise Refused(f"Ribbon Tabs not found after triggering Word contextual target {target!r}")
            if target == "background_removal":
                if _find_word_contextual_tab(tabs_bar, "TabBackgroundRemoval") is None:
                    pic_tab = _find_word_contextual_tab(tabs_bar, "TabPictureToolsFormat")
                    if pic_tab is None:
                        raise Refused("Picture Format tab (TabPictureToolsFormat) not found before entering Background Removal")
                    _select_word_tab(pic_tab, uia, launched.hwnd)
                    lower_pic = lower_for_tab(uia, launched.hwnd, pic_tab.name)
                    rm_btn = find(
                        lower_pic,
                        lambda e: e.automation_id == "PictureBackgroundRemoval"
                        or (e.control_type in ("Button", "CheckBox") and e.name == "Remove Background"),
                    )
                    if rm_btn is None:
                        raise Refused("Remove Background button (PictureBackgroundRemoval) not found on Picture Format tab")
                    _invoke_or_toggle_uia_button(rm_btn)
                    time.sleep(0.3)
                    tabs_bar = wait_for(
                        lambda: find(uia.element(launched.hwnd), lambda e: e.control_type == "Tab" and e.name == "Ribbon Tabs")
                    )
            elif target == "immersive_reader":
                if _find_word_contextual_tab(tabs_bar, "TabLearningTools") is None:
                    cur_tabs = ribbon_tabs(tabs_bar)
                    view_tab = next((t for t in cur_tabs if t.automation_id == "TabView"), None)
                    if view_tab is None:
                        raise Refused("View tab (TabView) not found before entering Immersive Reader")
                    _select_word_tab(view_tab, uia, launched.hwnd)
                    lower_view = lower_for_tab(uia, launched.hwnd, view_tab.name)
                    ir_btn = find(
                        lower_view,
                        lambda e: e.automation_id in ("ToggleLearningTools", "ImmersiveReader")
                        or (e.control_type in ("Button", "CheckBox") and e.name == "Immersive Reader"),
                    )
                    if ir_btn is None:
                        raise Refused("Immersive Reader button (ToggleLearningTools) not found on View tab")
                    _invoke_or_toggle_uia_button(ir_btn)
                    time.sleep(0.3)
                    tabs_bar = wait_for(
                        lambda: find(uia.element(launched.hwnd), lambda e: e.control_type == "Tab" and e.name == "Ribbon Tabs")
                    )
            for expected_aid in expected_tab_ids:
                if expected_aid in captured_idmsos:
                    continue
                if expected_aid == "TabSmartArtToolsFormat":
                    launched.word_action("trigger_contextual", target="smartart_multi")
                    time.sleep(0.2)
                    tabs_bar = wait_for(
                        lambda: find(uia.element(launched.hwnd), lambda e: e.control_type == "Tab" and e.name == "Ribbon Tabs")
                    )
                tab_el = _find_word_contextual_tab(tabs_bar, expected_aid) if tabs_bar else None
                if tab_el is None:
                    raise Refused(f"Word contextual target {target!r} did not expose expected tab {expected_aid!r}")
                launched.check_alone()
                if ctx.origin is not None and not same_geometry(state, win.state(launched.hwnd)):
                    ctx.drop_geometry(f"the window moved or changed size before contextual tab {tab_el.name!r}")
                _select_word_tab(tab_el, uia, launched.hwnd)
                lower = lower_for_tab(uia, launched.hwnd, tab_el.name)
                launched.check_alone()
                check_licensing()
                before_unverified = len(ctx.unverified)
                tab_records = walk_tab(tab_el, next_order, lower, ctx, contextual=True)
                next_order += 1
                if not any(r.get("kind") == "control" for r in tab_records + ctx.unverified[before_unverified:]):
                    raise Refused(f"contextual tab {tab_el.name!r} ({expected_aid}) produced no control records")
                if args.expand:
                    tab_records = expand_all(
                        tab_records, lower, ctx, launched, uia, win, unverified_start=before_unverified
                    )
                    check_licensing()
                out.extend(tab_records)
                captured_idmsos.add(expected_aid)
                tabs_bar = wait_for(
                    lambda: find(uia.element(launched.hwnd), lambda e: e.control_type == "Tab" and e.name == "Ribbon Tabs")
                )
            if target == "background_removal":
                lower_cur = find(uia.element(launched.hwnd), lambda e: e.name == "Lower Ribbon")
                if lower_cur is not None:
                    disc = find(
                        lower_cur,
                        lambda e: e.automation_id in ("BackgroundRemovalClose", "BackgroundRemovalDiscard")
                        or (e.control_type == "Button" and e.name == "Discard All Changes"),
                    )
                    _invoke_or_toggle_uia_button(disc)
            elif target == "immersive_reader":
                lower_cur = find(uia.element(launched.hwnd), lambda e: e.name == "Lower Ribbon")
                if lower_cur is not None:
                    cls_btn = find(
                        lower_cur,
                        lambda e: e.automation_id == "CloseLearningTools"
                        or (e.control_type == "Button" and e.name == "Close Immersive Reader"),
                    )
                    _invoke_or_toggle_uia_button(cls_btn)
    finally:
        launched.word_action("close_fixture")
    return out


def reconcile_word_unverified(records, unverified):
    promoted_prefixes = ("word.draw.drawing-tools", "word.review.onenote")
    promoted_by_tab = {"word.draw": [], "word.review": []}
    remaining_unverified = []
    for rec in unverified:
        rid = rec.get("id", "")
        if rid.startswith("word.draw.drawing-tools"):
            rec = dict(rec, baselineMissing=True)
            promoted_by_tab["word.draw"].append(rec)
        elif rid.startswith("word.review.onenote"):
            rec = dict(rec, baselineMissing=True)
            promoted_by_tab["word.review"].append(rec)
        else:
            remaining_unverified.append(rec)

    if not any(r.get("id", "").startswith(promoted_prefixes) for r in records):
        out = []
        i = 0
        n = len(records)
        while i < n:
            rec = records[i]
            out.append(rec)
            i += 1
            if rec.get("kind") == "tab" and rec.get("id") in promoted_by_tab and promoted_by_tab[rec["id"]]:
                tab_id = rec["id"]
                tab_slice = []
                while i < n and records[i].get("kind") not in ("tab", "contextualTab"):
                    tab_slice.append(records[i])
                    i += 1
                if tab_id == "word.draw":
                    out.extend(promoted_by_tab[tab_id])
                    out.extend(tab_slice)
                else:
                    out.extend(tab_slice)
                    out.extend(promoted_by_tab[tab_id])
        records = out

    records = [
        r for r in records
        if not (
            (r.get("parent") == "word.review.markup.show-markup.specific-people" and r.get("label") != "All Reviewers")
            or (r.get("parent") == "word.insert.links.link" and r.get("label") != "Insert Link...")
            or (r.get("parent") == "word.references.citations-bibliography.change-provider" and r.get("controlType") == "galleryItem")
        )
    ]

    records = _normalize_record_tree(records)
    remaining_unverified = _normalize_record_tree(remaining_unverified)

    by_parent_groups = {}
    for rec in records:
        if rec.get("kind") == "group":
            by_parent_groups.setdefault(rec.get("parent"), []).append(rec)
    for grp_list in by_parent_groups.values():
        grp_list.sort(key=lambda g: (g.get("bounds", {}).get("x", 0), g.get("order", 0)))
        for idx, g in enumerate(grp_list):
            g["order"] = idx

    return records, remaining_unverified


_WORD_REQUIRED_MENU_CHILDREN_B85 = (
    'c-rlK>2l*Z(%`%F@21u|eAK?m#`lAgD2roB)R2^q-q?5Fyl@f#DN9w|Q-cVHMF5Eekhl|h{NF!5nsz%|Zi{2Htq%'
    'I5c(1FEZbtwA_}~BMk8QOpFNdC@|M>HdL$&MSr*F>ie_d|g;HRx$_ZYcu`o1~BN4aj^t76wSCyK5P&4&(gn&jjp3'
    '0S!bh0>0bq74EMilQ7KC!lLdWl9nUIO%`>^hi=}|8?nl9VT-0`?@Q()qB0EAbZz0P^JNhp=hhF>NOnV@nZh;B8u{'
    '~ExP)zDuA+W%hPK$D-ZSS2~p99ZYu>g)v2#q9n^H95ceH_AM5S*Q0buV!EN33ZN0wqRk3f{`Y)h=c{qHzDeqO=*B'
    'gmfxQlc7TG`=a*}m2%9n)2ZYSUNSqFMh7J~~LabX7r#N2qr3da1V+M&pPpUfX(ms81Au-;lrW>(gr&C(OEq^kUbv'
    'A7#5m0=W@?N*Jo9M<_+qCmCqXuIQ`JK3>9W+g#3wnLnTfC;p1&I5%D0*A4X-l!GlQKI(qY1^xMlO2<k-|4?r-K=<'
    '!U*;WKse6;2H3{?$e;2ys!3yq4&Ie4U8S24+RW!)s#b=BjMdtLP;&z04aT;tU{HV}CzznTjSsWWCz4BD=O36Cq78'
    'nkZ2pB#oUD~ly3SNj@clY<p&#2}He$JNJ0U6zS{4}<x2&&xcmM0#DYOZ@YX!HoIyk7`>p5sGtDpJ;j?arLze+|{3'
    'jrYQW$iV>n0HncBFTyl9E;&k2G&Ax1VNbF$skN`t;u=H*Vj)4^iR~A|;KWQZ?KVcQ`>;6C?hN2)YaAjWtk~Oa966'
    '(t}B~@+Pw9o^sT8-4obf{jTKk!2$`WC_%z{TNQY@3f0=lf2@XH;vb{kg4SHT|-dWE`6ksa9h}Nou1%?yfA>Q0ZHx'
    'Q{LO^VD}Bw;nWaGc}J%->_3{oxTQcX0F|o49g4RHgDGBbul1>e&8pzOm%zI05C##NG{S>hB@SMxp22;GI`R-TRiy'
    'dG!?Jj*zHm&Q8ZW}sf^y$h3u|teT68_E9<Y8Dl#0WpYLR$6;dLsWr%Ku$rBVjjZIv=})Ed9X@?U^FIEp#R8p}GNK'
    '1K6Tl0W`c$+y*C))hlgb&}&VoI1p+)tOgN?&F)vHOrSN8iOVFVfA^2m{VU<YdIQESJkHMcyPbtajFE8SPQ#Gc}>m'
    '!eW~$G&uczZMRtcdmdl?D^SLyiEA#niKA+6zv-x~6pFhm!{K5L3r|R1EU$8)80CwAA(;OO}0`#@J9AJApz?rq8S`'
    'Q)@p~z(@az&IpH5=HSk1$&{4&rdiBAT*{ro_v6jHWzAQ=X$KFVU1A@s>Wslj2mE$H_2XPUu=5g&d%x8GaGf`D>xS'
    'milX@zaI71lm2?vUoZOWhyJ2g%BLx1Zi<<ka^|aW18`ZN(P0d~u+}E<r}@SMZS}c<8>qsf@;93cUB_Tz1Ih5pH8W'
    '$o+3olO%pb+#VZMZai-jHa@Qm>fbW|$8I#?Vr$NF%A(_q;i<y%G7wfcH(tLj9#tl#3Rg3S{-5Z*`8&@mSac0UR@5'
    'zxJQYd}oYd)>eYpj)Q%!Sy%-fl4g<T%Kv8hn4={mx?y6Lw$xDa8(kcqdUVL7H2Em@|z>v*VO_rft=NDM;G8AJq_`'
    '?%Nma{U2~|n9Wh-_TWCPF<vsM+z;0f=9?FgmrAQG;dTlRA20V0M=zI@n^$u^|3K&oK-M-usHR1F^WH{D`Hw^(7eI'
    '`y@?eN;pTQneSVV^L0q13MXn$qT7bFy1p?5lFimvewC&wT?Y{kl8D!V7nf?UxlF7;J8C7+*D9<l%mU7c-Mv;seC>'
    '^B)1M4CYk0g9U~%lz{2rwT_~!R<*o=ZkiU4fG%o|voKQx)dY`BrC$?{v}-~!)am8v4ffsQwE^DM#?9y_;<&#YEj&'
    'KJx@q3z0DOV7PY9=%X4T0_!14EiamBHB5twL`SH}?vxT8jUk796m0wrMi$Ep8XHNcH3ttNDvebXFNyQE7^UhcKNK'
    '2}|E0)7;3ASVlwN81L@GjN#g9n3-i*lJ+Q!NWKF>%Y#G)AAM=h##<!(e>LY#2O$9d9*tKqJb%kr_gPAGWA{`kSD4'
    'TDLUX;Y<=16tNuu9MtwLGU3u!5yl$dd*m&wrnB!+C23GttFh<Vh26-Wdjm*~&7lLk7%@MwOiwV)3Y4LBX1KfV;3e'
    '{Zr7S2^FhQ&;%8*iGp(qWwhfELvb$O*^a*U}1i_3_M`76&17-R)_gLb`tJYdAt|%5x1j0wB@WPr+4`M!Fq)x*XS4'
    'I{?O-)6zzRtGjU5%gt7C7I1NdcECdXUg<bpO9|>)!p#J(C=ehn4=mP%2n&)QTnd-wo3<Of9?X*lrc=MKGzZ3z5Rk'
    '$lAGtFn4O^2kp(g<4u}U8%3WC8k3<gP01Nd;L+ArFz`U*N9X~cUHvXa&fTqfIwu0k-)%M;PQt$Nt^WS@rJd&Ae`?'
    'yUDx>0sJifq_8G>P_8lE_F{=_hZ?;5$F3IF7$kzZ<{l3j4&gqic&Q`ahG_idgqY^jikQ7TAX1I@8w(pm4}hdpBq}'
    '*ftb{k4%Q1q`CgvkV%fK4eGqOqbx#BHmsb(Hdye!<a)jL;1_S3`x6Ma~^R_L7*wSH}OWR^^FnPVcLS`H>8IhxX+H'
    '#l<HP}~sn4P%VL9IIA(w&I)&jZ-xp`$U6ZQ_a2b&b|ZJP6u=3!-oPR?xwZfOS+~!2(upa0(CxIn_yw2IJGA#NwcZ'
    'wfEnbrtUN-9>vcG*w!TcsLzxV@f2)Bf#`uR{OC1?mwZfkh__2+rYYsOP-FP<5NxbYe|Z?T+f59Rzy%mm!%cSx<0i'
    'Q@a?|4Enn&rid>p6O;xR?9=f^a?o>KIB8l%_K2)&--^m<Cr>nTmIMU-BP3G{kQj<3g&@wH0PYc)o%)d;;-aeA#1^'
    'jf9qwT#khK7n4($?>&_j4!*Zd~yv2u1769JwPlw*`<}8;*rWuN-SIt(UohQP(P9bYyOZV)Z;^(P>&C3LOnht3HA6'
    '8Bh=$Vlu)Kj%>c0Z1)8IvXyWo8<U(n96*gtCHkX#qUvRSJjZ#>i!V16#FF0YV>;A}o`vIFb9Fp2M<{_STc;-M}tM'
    'Cu42-*Xi0&W#h)cK15>@cOb<&O7H{vsw)i3dhzVDaaIcp30$H&-7Rb7^1I<}05I)ihnpj*lI3bb|u{zj?_S-82S?'
    '&JTfB6rDy`AOO#AaFWrfg*xj^CD&|1y?~<s>vm*tSD8UqGfp}TA!*8YIH%DgjH&TENS6TrXhsL7=Fp7`4g~Vxon-'
    'R`#A)~qig<VH=93;SE12B!-5l4Ae5*rgw@1O7x;ku$SHsWJd}_p#I44;nvMoR8AB#s|;qWv-PbV}H@bD)q02Try>'
    '+z(^iR<>#?d2Q(Z|KlU%Lc|dMPLhNd=;>$Z#^}f;O!d4axMp&s4$Q4QA3CIyOE0cz=t-S3Rj*3y}t+}57r6^9Y7S'
    'NQh|3ot~)XCa)0<Dxsc1@pkAe|^Y4U4<l}NaF6ZNNJ}&3uay~BS<MKU^%N0ne;VBUhMzD2vC_*6L#LQJpt#jM#st'
    '%KxgDTNldI1jy9t=iF`k*v;>bq?4{S3}RL?$|dNot`}LBflq-$Dt<wvMNRFzq>&zAqyQbodJ=m75E300T)dg5M)a'
    '>$Zv|_4Q#J%f&Jw(T1Z;RuqO3TYdrvB*PR-rqkIO53Bg}4bKNKc1bd9GBk;QhoMon21PG{xlM=B1Y#1(nFvb)sw_'
    'J?36{}9h0hJ7O{>HNXt*c9Logm+FNczaGl6ZqsrC(YbUP(a^;ycZL#$t8ozA@)OMQn~4;<?<GP2hju5Ge}&*BqMe'
    '7TURsf}aot%}WU;LyXw-^0DB3zsJXz=9<L1S=8TE@(7IAYgqxjA7Xw8kCF^80hN5Zmis@KH#X=c|e?n?yc>qYP(n'
    '`ur!;Jb&XH&36R#nf(h4u;Fi;WG&~j3b&qA`36#!T)7AhZHVr22NCRowvAlPM&o_P3CZH=Hc1o9jI}6fetX4#BJ('
    'N*4n6IO;wPYf!-HW3r$Kf=(Y7(+)43$HzQIu1m3AHm7M^R6OCe+@X9YsDJp3vKqb`<wSU_u;N6h`r1m&Yz<Ds?7<'
    '!@E1oTbxXAu-w*41tAW(hcoXeEU>HKPQmI<;}9s3H@e}-=3D5bOGgKrGMZxz!Y4;$8gH5k*_buIPEUlyN_o3eYCG'
    'NG@k+FvV$H>)gaQi_<*oV{1ya(-X-vcsOv8ZG5FQkY?PsjRL5rh0fW)K#nutga=tSbu3%m+OpdH+4yfp(Y(p_*lC'
    'A$ER02(IT;${L+k9R^8>=;7@!r`M}lYlnOv@&V??<TcWflg|%0=}*m6Dgo8eGTwbitIsZq+Npu%4P~tEa*vevEZ+'
    '+&P3|i4Y(5i+EH^Itpd5O8cSExE?nR>gXUUV21}e)*{+T+3&rAdWMSd!W^%35!eHUG&XN^Nr1C-fP#^2~g~EnZn^'
    '-D`96Zt$@PNka5zH{9I>Ks7SH}YyuTC(-l<MHSSaWGd>f=L=S16ogN{zZpi=u`jHS(dxYZT5grAF@!@NUN{<N=M>'
    'CzxT<fUbcn+lu(X=LDFqahT-P=J#2A5T^@q<S=tN9?Qh~qmrj|lmiN?7u^PiHwe96pbGMR1p?qM!by!XTv^~~PT*'
    'm0FPn7Yc!M3l>znJAGqK87Hx-0gQjOKgQ<jDs8|;@gx$0Lp`f`d6Xi6GytOa&`L+vsqRrTry;_3q@isYHYKup`7U'
    'Fhpu9VqddW?W5!L-R^Jj~K7dq>s1XhrPb_gVLr~|JyAuNuE9pFum;>`1_4F<z3N)tDA4ueY(rPp#=>v+XJddaK?T'
    'c%R|y=HF19q#a~t1pwQCj?x&bW%qv1J7nt&>qpuNa;YvRA@YGiz$(<aDL9_z8MK*Fs0bQkje`I=sDntLJ>?w?cpP'
    'CeGye~*i=5mZAf+34&;;Dom=mK4lMA>ONN->it3EkP&pAizyKNmtb0Sgwl_?%CGntv`QKrJWXT1>3hv=SGSpr+tD'
    'ikSv@e~)oaVN8vHXx?=k1oVktQQRN_f+S+uUR`G%*f_(l%>#lgCtOu_rex4EI&^VbU0ZZC&viv}7cGi4{u4BlSm5'
    'D&>32LQ)3!qK-uhI=IN^~ZroViGVj}WPu4vUD$0UCH$o&WfYfijdL>fvPNdf>Qh`LldP%#a_C7}7LFH|Ii6*qqDJ'
    '653nh&uY~uN1Fbq5S3I8#ZV{fMkGnlCX&ku4^hiHA|$BX-$}#<y!d`2X-3XYuX#ik|^bi1>#dLG_J^eXg0PWX}^h'
    'bBSlsO)Knv@j%4SxbX%cVT~g`<F^vOnE^A=fCQ2nb?b+-kNYlf46o5d|9j&D(ChTZ6AXh07TV6EQDwrf0ADg4>9e'
    'sk29dXx_lE*R8khuc>(*pj|Ee)@LN{^b?N_fOOf?`JzN1Q_TrD|&KHYdOGs7f)U`4?!3fL@2e$q{5Gla$<H>)AVn'
    '5&(B5RXvbcpJ+w@3M38p1dc}~rQizA$)JkSHgF^c4V*&=EeyvV*v>FfI2KKz4xvzEyGx`4Qx<m3I#|Ios%y7B$%u'
    'yQ2-bj51fV<x>$lk_0br)0c2P3_2#iLL_wNKPZ8RgGJT|ef$ND7Md50qynlXER3GraU1y_<FJf9*rF?6WFULHbyg'
    'jOTOwqu|J<-y(IH4nkmavK>Uux<txYgMsJ3(IaKb;!U|lO@9Uk_khHPByPFXp(I`Z!p+t_3z>-Fx)|2<+QKrJ^=('
    'r^{$T0@=Y5f_6aoK%0N6UcqFa@HYmDi^0q;{C%7PdvaN~%O}LX`dkGE#QbX&|4#lxT+Zw^SvXetbsHe`+B<pk%q8'
    'Xa?j3xS~n^^PFa$aP?jm^-=dKwwR<>9;!^$iGAhN53fU>F4l$RP+{oxA!F9?G0jyrTh{;IIJ#^kpnQk?(j3QLGMi'
    ';6AjZ0HuO$?8_kHeF!t{-yw2?jjgus-ps32fb^hXh>~b=2z|SRn==?3tHWb~c^AekWeWPDEI#X7c><V5_H=MC?Y0'
    'Y#u+XqT>y$g(VDXR{JQ+q#DKqPc;vZOW^+NOSea}+O`~|$Xw@M#!$f}T*k)>HlhEbs-QBW9d4QaE(bcpKMWE2{2`'
    '5IP}Rb*9=%nQR-i)};eF>E+U3Dd!dhIxKu^O<04iCDjMS|;WqZY4ETw}YWWYxwyKw(D2O0(-W}8#<Er<<|jsb%mB'
    'pIMuI)H!~l^Xf<wC_lOqvP(NGuh_9X<A<AsL7_F534HT$~jcPdu?9~b_U(2p~6Gl8%ka`zw)fH_?HzC~BEvo;vD8'
    '^2&2Dc)7Eia(HRGw_XfSVAa$#AIJ=8X;E-v?<60z&ubk8%yx&B)<E$tq+wVbcx_YV;6Me%z;X0TIq;WgEA<4_3T{'
    'z((+esO6w~J7$rCEkL)wzDM_Hgzly6UTAUWxffN{E6`0yXuH6{qpEc)LNE*VCEJ9(ir<J6Um$6Rq0c+w169+$zDK'
    'j=fl+OP^f;()Ynz+rIb5;O*5SP;CYW+Kq3eQo=6BpS97|Mi;&mJZ%0XL+7Ik96o%c6WK%GWPl+h#c{hMhjf@}se*'
    '0a4CuLz{w5#y!=4hr0(@3xr%FR4N!I1n`Fu^TsWxM<n3v$u6k4~Brdd(};ZI?-q|s8<;AtJ`{+RXf!&`}TGCqsO~'
    '}n&PP1T=(}yZ5EN6S358U3f+y?jahsB<}TuMzrHctHoCz$Q~i$2@;i<o>&CIXFFIrNTrBW_0}G&T+ruB><>>4y%k'
    'z~rjaqkipf#=7QR7(C&}3Iz+0~ZqUS!&+p}Q(EBlt@SCA%&XLk*^g9WcUdk1rH<oWoFs)cyCHRl1u?uxZ8p)_%g$'
    'Bmm=h=PKsygP)$rI1R4Em!1g2hJwhh%{-7CG|A=z4NbHK(F{zs`A|U<Za$E2(#=mFn0QkFWQ`}%TuMu}l_25`H3*'
    '`uB#>ki2_n`$N*pwfjTFsw>r;(Q!Uh|k%rPX!cmV_AB(nsGmCWH2F9|##rg$h}i%mZD+{7TcT#zAs0w@LqabbcKa'
    '6$YgyQzaVB7+op%#l|5$-#E|K*N>>(G1$^Lj_yw1NrUs(+4fai!=Cyi8R<t4Yt>V88$bBWYAg<DA-sJ#&4^aJZLK'
    'MbXYdiZ>OCUY@`h^Y~djL(Eg?c5p0_c;5W=pOSWoc`$~b1wt9S98%3X_%B1Zsl_5p7(QUA+fMpyRAE<I583T|3gM'
    'UeQ-vZz`a?d1SGDE;dU=rRn8khw2tOz==(Tz0$Hb%JAb~=VOMY54iGy$9-R$}XP0blWfhg9Cvq;lcLXyrmDi4{Pc'
    'qLvFjMlKgRK`$3DPOuwK_A@-z>(f0uP?0k~y7ojH+1+=_;DF`Yjd6(s9+Cobe5t*%EOOVt-4gw_u@jniatH%PKJ^'
    '{)=DN%rY{u4h-H~_$h!luvrH_*n%lBa7$CyaG?|D&jSC{;#{Xs5(=Ze{8#V8h=6~%lu9kCeXS`2e7Bp32i(Y+5o$'
    'ti}E9Ve*lD22<8Q)1zEoRThg^0G&&LLH!pqZa`1VwDweWRwMJWG9De2lMNM%K6wwV2u-*f|qj`hI`BgYSxGP-)NR'
    'r*j-+frmVzS44z@E0=9?Kl?;x=AmyQN`MV{{@Y)Snp}Z7sKrN|bUrE&8>UE3ek;+8YVaYcBrDwm(@Q6dQn%b}7o}'
    '3f2zeG0at21E(@76Aw=B8QXrty(kAHyY_whTIEIdJac%|MGFGH2Cfz@-m3Sg;vx<-^%aHG@3*Ac5kZ6wJ%SM!rmG'
    '<jd4XzD#W7%XlMSCNy$BpV&$bm~5ttF4ayAIo41Om}senNj7zAht4PU=zMaQ&ZqY2d_t$rM|zcAcq61XN=>1=t_Q'
    'P0DcNI0_85^pMr4l>*<(cZ7?C|j3_V8JZX#~pg5_dv4&@v{TcLa|%;(a4uFU77`Ft{;&*t;ReEzVCc(A^$^5%<s-'
    '#aW`gJ~$e-xekbE`cB{$1mw*P(GYQUa`VS1B@$m_}lF|xoEj~2LL|y0l=V)m$5Ql#>yA~SZR0b0^$1@@^fkaecFi'
    '~KpA!jMtXU)1e1haVCROfqug}K0k><^{SL;s$qJ!FxzM^k683=ICOMG<pb#tMaz3LT#gK=>2~&AHVxwt@h7%MT?!'
    'G$?2gB(zLqcv|@U>94YWOx^^9KW9rJGoT_4b+~<27GJ@>L{XMe<c7Uq$j&Bwt0s&g*EOluHRcR%%}1xh69$)@!Et'
    '!o|p&_T`yINQZ~Q!Y{5cw7RyIZAJ-E_cWzI`K>OLQQnXm@32Nv`HoaByOHve*oTcu5&Wuf0@O!DNwo2s@?GS*K|W'
    '?(bGvx7wqqSs1(cq{BH47Ct@H0xqKX`!CaV)3BP;>ONIOWhNMM&@s$mh>25?LAiR`9C$`~cI4SYGLvJQxCl+x9hz'
    'VQe<Qxgs!;mh+^OLjBB)xmp-AD~K7<9*`;UU*MvL;%0ZPR<sTZVzli5b~ktv68O8HTbvQ!LuWIw(i()Ew4dPsWq('
    '%yg=*Vy2YWOgU~Rrl0>UV_0gSMKDxKn<_nAkfW0g%j0$Zxd$F_9@dGPr+Vgq@@48)gsSI!pwif+3TBN`jN{6!9>*'
    'fN_xAbV*kk|E(@^GTp(58GdF0wzGW~+KYD0f2#C@GD6jmX!Ce2vK0h<uI6*NA+L2wo$M=p*gDj>-j|K|U(Qi3B^q'
    ';PiP*xVn91*)Y0wpPmUqR5AnKPFpPv#cruZ>y85mDnAkfHojg9iPqnK8ipl~6}U)I_2!Ceq8Mf>INE(DD(#>*_Iy'
    'r5b585Ec|^KX>C!h)_8cE9h*b;Y_RIouI!1nU(xTAdOa57z#3%mwUNylb`kv+xg-D$dxXwyCPJgqAT(z~l05|WXx'
    'M)DoOTa<-2`;)*4czsu13}8Lj3Ah9%zr0<Y$VWsx@M?Oh~ZEkw`!6jiZzrzsG0!+k=70^N_Do?47skD2=uiJ7O=p'
    'YQ(GQcr{G-u)zH)d<j3a30-$KEkpzABVA@}OomFJBQD0kd!X{sh`BpY8wLLNL5J9S+u!gpHPoYs>9xL_wr2+>T08'
    '|-nDXOAVjFO!Miv<6s)oAkt<BZ*Yqq$3mP$ZB^bYbJkT0NdZN|BxdbhqYD;Vc*+FCW|u9T2o@7J#==uK7YF`AOE*'
    '&Edh?VO|luI!L6`1c@7Fb!y9$^znfOMqG%zSZf3b!hQALQW&iPpbo2RBT~gWwk1`hW5!ZNTIMSqxG-KMwT_f3!RP'
    '{8a@hay2v&jR+4Th%%feneA}Oq}JDf!>xGXOH9`%KL6}y27ZS7i%#)Jf^7ri*;$~TZ?^p#~VXZP>}YzY`2djixXq'
    'uUWO?G`UA1QISQ1Zh$^iI&DGZ5#s+S0R?mbomY)vTqF=j%-7V@lm!QtO7wR%^|DIWY$dEgvL73iU&&da?ZjutTws'
    '?W^;~ovI2{BFqqMvUU#ey)fbv{ro|A}$6g)8PUIT9InYt&LKSOx2Fd^g-`pRtZ?<G`4IJWhPFx9s^z8{%B}1vOSl'
    '43C#fmJ+tf`H+BDV*~<_RDnLxa3X!x58Cm=>~Ta}josi6qhnQ^ctSn-z6xK>p$VsvgS|nrW_2=Sv?-V2hc4F5u^!'
    '$eNE6i>eu@q#sG%u-O8uPGI{8m&~5GDwBXti?GxFWsD<PrFd9jh?KpTziHjZz+D8*$+-<gdroe)o>a94y$7am%P$'
    'ua#;LeC#7P2%xI;a6EMHF*TI&QuFmEo#8mCh#FB%HsQo(fDq3JAnmClKruS_hk3){jEKYHOOFZ}F<U%apqJ}?mrK'
    'f*`3@awR&vfxP^#fK~f6*o#YTZxn%7}ujfmSL*oh7&&w4BJYF#5i_3K1$N>k(H1_(@xt6!b2u#G{Vy1qkFIj#}`@'
    '&EUdg21`A5iN7QYNd_865tA0okRwUxRqGH1J1qqla#WY_>kA`Vn!%r3ED!!%F2UWRIrC%fUA82Tluq17tP+f?qK8'
    'h{^601FHGQ>Jr)ndSBQ2?ZMB!WdTpnKsDYe7W&=w7(p{s@m?8&z@?hZ#=_O?{#ZDv#rD&0eCerL&n-)eLH9ic&eE'
    'zr6}sRWqw<{zFtXQ={}hT30jGu&k_^l{K@n=6{*8=GcOewKcPBLzZpGvJF|bA<H&o*@mB^t(n?`vnJ!O(PT{ZK~`'
    'n_?^9(=jR(W?GD8A|m*q!sn2a~H3!pyPrldRW4kcK@JP;jH`T5D56IDPz5|H6}B(w?v`#^$J2{4v@76AqwQn@9hD'
    '=1-IPkLRDa_Q5`$I<kqV{HhP(Ry3pNBu#pk%j<Ay7HC<uZ8j@ahAV<%8O7COiPtK2o(cNDniV_+pvx`?_FsPeF`X'
    'j4g99|(3g68K}HWp^QY>^68wp%3@Sir-ye!eWz`aRNk?>-mv3eHR+evN`Bs*1W%*W?CC-1U;%aP@&YG*gR&(`Rs+'
    '7^r%es`mNS89y17pgR`IwuJx%rrzkGc7nn~%Bqn0viqr6@n%yg~oNwJ1|H|2q^Jvv<~@ch;ZnhV@#1tJ$$?cC4Ck'
    'tonC)Q2kl1QvaKLqRvoE7k33#ALk!zE)9is^C@fx`O&JQwr=P^cYLT`9@MJVYGOroShJR@8{;Xex~jFp1VSx;Y>L'
    ')+HW5bYpLGQ34G$ZF<8a-wsvr+j74kKv6cy-_YZ|ynHJ4J6CLUPUsMjyMi>y<>RWoYgOf5gi55<A0v4~BVV2ZpqY'
    'i)3ytgU7EQBl|dE_xYX45p$NC6ke2VLCF`NHmaP^1TsT&5Cd)DyN#M%3(8)tpR1i)}mpBQ#K1cuxzy;TP?^|3$oR'
    'MY_%X;Eyz|2{vN9Z>;XR8Ex6KdLEQ7L@p?Pr6nv5+@Nwtg(;R+Ja`HXq*n8BOchnp8xC`nLzta<(O^<t+PP&y&`;'
    'ykY@wv<Bjx;t28*F?s$B-D~1q_Ij%n~G4GKWvRB=FGf`(@o9l-CxYdTwHnTrS9vJ^>U1g19h23b-JClik!o8<kpo'
    'q?LYhu$?~8u%$sXgSPrm!PfdfetZ4&L5uOk0_?6xgT2&Xdp($8b3;f5t@VI{jrCyswtC5frjl$voSo<>?6%WR3O3'
    'RP7`AYbeJJ)}K?K`o1NaTI(~_+k*}hVsqpcp_)<)4MsWNH1OJzt=ZFC##s$(4+ABFRB>O%(JnUnDT!}B<D?<G2!A'
    '@DSvgm>Snlc3(?wF4X7SQB7lgiCFwV`x((8`(q?zzJd{woVt&HS!cEl?yjUD;GLRtN`K^wML9mty0hldinOUVg#F'
    'dgrAkH^uovZeqS9GnD!;vC6PHU=}4%Ponii&HhpCIu8Y_~np|kMag=Qw{bCzOsnPf!VasUDp?tPklx-Gen?=8&&7'
    '!f1pKTLm^?<A%kktdSdO%hW$m#*N*(OTuwQ@@~$83(EJx@Lt=5uL2SLXB4d_I}aXY=`DK7Uw6JXqgWdGp1$uMF9m'
    '&+lu^C)w|Yi(~p;j^?D(@u<JemwHS`04v?Z8mw1TDQUeWpH=f&HJ?@USv8+k^I0`pY`NWHOVm+%w#@QNEwfA|s@4'
    'P%vO3{0!iw@mn6!gLiv)HlrWzK3Z2-3<pU7@Xq>NEQ+rXeSu(*QQB7c-HgcF?;+2GBc4c;W&=;j+hz5(PLK)wOw8'
    '$iAR<Qu?!jM<2m<Q2Q{Kg4=Xs)m1ym7477Gkf~Xo<9HSo<4u2OV8{)Fbm>kLA?J;LA>lGF!MGtZzJ<IGH)aEHZpJ'
    'HCrjdGcYwdn9boqR_unchn7yjyQ*1uP=2L7w#pY9NKE?jsGJ4s4+JAuiwCpGC*NKf~hiLhPnop?tgqlyN`GlHJsD'
    'GnFwEqClXa67<XE1ip`+CzA+1FXn*IA4{cXxUgD`?dFSuA6AgO=T(*=+RKIQgai&|;Oin`5+C0l&3}G{4c{;{e;t'
    'KZT@{ue5!QNZ#vBrI;4r9RbcZH8@kCRgmJ~dWz)fnoGMevGs=Q!u%2F_;rJQ6RU&{%O<D8Khd1$wROnWJ+pPsUuN'
    'C&>cROBH}-jTd$P!J7CFu$$G@G(@we82EP$LD<C!s@8RMBTo*CnrG5%cv<g2&d|0K(xS2r%pTHj07`fAc=$?M-y^'
    '7{H=@T*O>POf3L;F_-(`HGRR82O5kuNe7?alLf-)f;ZMnV9$7yyxaUH}AQ5&&_-8Pmy=Mb}#<hrC+bE@ZT#78?Bz'
    'Ps>t0uw~k7_dv$Y;i9lJWl__wGiEzt_aI1-Mj}zgZg08<)Uc@Ij8lT`{e1co?3C_eP_z|DrYh9WwKV!|F1h$w4ww'
    'wmGng;eb4eV(MX1l15PKy+fH7h27EvA7jr-7}efjv$Gdy1|vUHumbX@W*2t|atJvRr4Bb0veaD9c40+oDC0GBG|$'
    'Km9n?nUj~+&^axROI|(c|06AqkMzBu?<Fy3`9H$UpXe0_eqaM1FVt-SN)<yLlth~TX0fztE2^@%%Qf#LKWsp{nts'
    'F;LwBly^SyN-ND7@11k<$wZ3@Un0t{<iGnDwna43&kHOUdh8cH8j%>aS;Xtx19hOPh^QcXFQUo;Ug=s-6DSpLuzM'
    ';?ji>aT`&bwGY>PAqH*V%e`GOuMf>_19TNHXHS|tv2ebG2c*1Ut=xnc0<K(K-harYT+O($U}Aq6{ysUlnNa52-Yn'
    '{%?^rD@`~p}`ENQ5ZN6Z_Z0R*+b6L9sg@ho9E@UX$Xq!+->7`JB#5(y?ByJ6mmk%6tI3RHJ*#_Wklxx;Hmi#1F>g'
    'MoZ?eON(zAGVAKhkM}#0|4LwPi~B_)bl~*$-l^5g-Wn)q6`}RIWiWb8af7TCwEH#gC+h`jJ4)AY2$Pl3GVfm0)yT'
    '4kh+KELqiNU#u_dHLeoY+7U@%nfl=@a=~SB>Gvqo->cXSRA_70TJ|^zQZIUO+vc*SQ8`R9Dh0Cguc<`?YzY`2dji'
    'xXpU?<GE7K=jSO_FsRtVChauO|#Q`$HN9<D+xm+A6db1-`cU+rLRM};*w*ViX20Ll{e`2fl)^vo@>AoyH&R=9#8d'
    'Fbda2Jeg*z&g^32f8hC&BHXT_6HQ)eI3`$fi8BaJOMTdaKIhwL-kecO46;^!}{2(Bl8Ib*dYhqvMyAyhG(D*z#ZT'
    'PZ4J-}Jhu&~Ty#!c2}0}b2^Dcdsjyg6Yuw1PFFm{!D38=A3LipJpQs32q~V537hDTjv$=@P1rtf64W<Al=!6mw`8'
    'B{jtM{vVEKfjjsKNQthZ34|703nb<P(esuMAX!Ks}mB@`iPZtU6szv}E?YRhfkDay(+E{R;pFW&2oRh?KpTziHjZ'
    '04t;|H(mp))}u619~XPS_qHJM|K&o$I0eGj!bs`5V9$Y8&#3}kEjVs;Z!X3fr&B5~WI1!G)#v%pbe0TB=S0p|CKh'
    'aRw1ppj^ukYG_}L4;cwr?VU?LWNgpYFJ*I{X80fmP(iu72@Aa0awwh}2jFs?^|EW=dE-N7*j?nsuhoWwZlavvq>('
    '#T3kA$7)vB?Q;OUDLpf@<RMWdZ(cD@y0wmw05!w{u7SK%aL@o$_r}GU~(z@BCby`9MQ0gXq<6Ov)$^58dfd9BTBI'
    '(uhLg=&cq61kK+waJ`Zx(I5xDx+IS_(LfnE@R6~~%QfWKF9ikzfJCufz-LyNfavJLA9^t(R+UyX_inmA$49)JW->'
    'rx^UBS9+yB#1Dl{TfCC*;E#kzSq-chCW%M9flOl2p9nVH+&XOz)i8SY4p={@2a8HqCJc)s;o~KKM{N343))TRHUG'
    '4n(>!^Vh-|eEyhYI;6&&P)d(E9UhK3A@Mb1jzhDtx=b2#W4Nvzb5rnLGv;WAKV6P%9(Z`wZg#3`MW)U~5Hy<!AR|'
    '|ombf)qJsyS`@h}PtZD+d4iM_IRGp{nJ@p>phUzn3w>eh}}_z}p4F^6EvU<DU$&;zC?>{q9(SGyoMkZx7W`1Re67'
    '(gt^h5@|#fcY;5R{?rfZ)j_UOWZ3@8va`7FQXY{hy8To(3NZE`@t_U_V(z>NHG@oqP)!-+LhwrqsZ)mEjy58C*CI'
    'Jc7QN_paQwHRtIQe%T}V9ck@u>Lf=^D`itrGS=6vSAwz8Lg%|oRK~#DzD!R-Zo34a&+1z|C%qLPozXI_+WIl{q45'
    'OA7AB~PD>WK&00{Z$i55_Knu}gh!F)u`O^SLmeOFnABkl<yON#VvU<TytBs@l{>2eczpd)kE;Rd3k@?RYDX61BZ;'
    '!p<gDWzw4Z?Lu&I#FvJXya~bv2=lvqFY7~zrt_|C;b8sq7Nu(!9CwAWR}5>3h%XQ{?R7{d4UI&&{#o<any~g<=Lr'
    ')Ux!)d0Vq`|O>Y7bBMdzP1maZ)3-lNIcT+v#P861kQX<`&(Qm?B5qQeS6I6#stA#Es=MvC%LO@RbYSS85<DQObY8'
    'UyXRHW~#KX!UXO4vUc(DY}KYKWX?}QN+E6j(u$V83&`Ecf7H;dN*dFRxa6N@yo<5?Ul<+0v<urPaqKaRZzM1(c<='
    'P{w_lum1u4l2|sC=PcPwnqZ}=9wEax6LxGvOqZd~&@VaMiA@GKa6F-g7_qpszzDDKf>t0TX5&>LVV0`w(^{cDH_K'
    'K2cLnK(2b*EU6x>~>&uU;E6pbHH@R?HuR&vSYDGG9fx-L}j!Rx!A0kg;DCu`55V5ZtF}u)I}YSZUg-%M%ctZSaEi'
    '6qFTWt|{8_CHuqOg^ae*Ea}H+&HhdCeX<iuH)2>RPC}T}7npy<jYrNsJovV+V0ZYh$UWSYF>(wT)@i0Igwj?6%qs'
    'PIyuVxDf~lmLHYNp=wqsjlZ&k(ix|F;)r4-1sshOEt_1YX3=W<XY%LV#*22UPac7IFn;pO(dJZ(sRg>6)$G3{_p?'
    'k~1Qb|79k-+?$_><gMyF~>&s*=l$VDq9hcAOl9Qst8}-j0B*kSMMFHILdI>rtB)Qg$Aq8Mj}w!4s`eAo74g2dsCi'
    'iBl@d?OD4R1e#ldO^Gd=B2sA7U|H&ylo2kxX`&n#1i|uEz{VcYh#rCIL<FNdtr1sbB8s#718pU*t?K_Yk@W0LtNw'
    '$9RkumJ-UfU`)vfcp`a2{CL-+a;=eb{k*z@VE~RLnM9L3R|B{ZvI5mgL5@VGtQA%C*nxfJe(!RZkeL3p6xJSTY)y'
    'u)JrwC1gquiPfGp8DgERYB5-H6#yB_6uTKQpnKsD8}W<w(Y<iH{Sh9)Hmc+(4(~w<O?@I6Z#9mMB0<tHu<)Ej9fw'
    'x$lAZJ5%@c%*JCuFus%vL|wp5xem1aw&zn`Vj>61U3C(R6z%n->8k<1Xu43W$b`L21=Y5T1?wVM++yc?aic(ssSR'
    ')<UWN<dyX=^Y4!a6x&29?3Bcv=%lX-3!}(*|Os(x_XqZ&(3KTbFUXrIeBj)+ojDJR6J_pLBLf-EQ6M7RAVy{4j4)'
    's5H1VS#9ddl>{&FQQ1S^SpHT7%C7)383FW6-TDode{@cwgU02&*Yh!6z-LfV3ds%XyM(=FC{dY9q?)5!h6b|w>n-'
    'cfZ>+QOA7F@mRV_j;|^}JMi!L}D&+;^-s`n_)0#hkUu)2A+rb~@Q3;L9Alc;QxRA{}<DZV1leVPjFYxmC9#6VOW5'
    'b`<NDxj;Rsc-v99o^O39UWf;gp#)Uxb|Rofc97Od9YIcuRX|#vXywd@&3D3lC(L)kd?(Cz!h9#pcfxOSt<h8w9gb'
    '(Len{6jIq+!%S$G)H0g_zPAwD|kplwzQS<(tAiMq&PQpM=gr59n$pcq_|r1ivff)<b?Gj7A^i&b+Au{z1L<p&r=S'
    '|5}pmICc>sKbfWj4ly)^c)<+EaJh{rRr_YKF6RDExa2W!-6`VEp7!8ID_`ney%sj)Gt)J4Y~u*<wbWyN{cPTE>MI'
    'rLZ{=w7S!hL$Tmep2Lok@-~i6TVr)UHH~~F4PpsK&|MP@u?-B)?E9C|WMfdCnzDqyS&m-NYAJ{(<U8f&J&{1Ww9K'
    'nOO4#nbqVaJ+mQi3sA!Rh4=r@cvzRF&*_Q3I*1q)kMME{ZwAuOMisaBjZwroRN87cihk%1AW$<-J7AY0NnpZ6o!?'
    'L-DjMHb<HXe8Idg_6@kFhhs1a)BY^fj==>Rd1~0ja2c8uhlM?cleMpl8vp8a1JGtCsyEk8;Xjiy%llNk_VM4L&M='
    'S9wEqQgkIZp@YB-6MDe!a`omsPzJ&^J2QhNJ>n5$5O&atfv=;Gsc$r_@4tBrTsL@*lOfqvqh%<CvziHdcx85xKZ!'
    'Pu_E6u{*bb!5{k=`MD%h*qJda{-oAF468)J6{$I%UA4t#m-mke8tXJ?0m%zKD#RJee||14pxk$)d@G`1LsyZCo-x'
    '`#vA6=_d=T#AR`0zCmeyR<9T0pH5sfmpJ+uAEGyWlU_YUuGJwKlxj@0Fupoq|HaK~nHa3VIw{Ds@ZOnsC9rgtcMA'
    'OiWbE)OP;F#`M3BYsE`F!|NLT3(@-W#w`GTXwvw`3y;>QnqsY{2H5Ij+=T^P%nVv8ZMHi-QQZ&Itw!wqT0{(2-%8'
    'le!h_k0ba4Xt@{wy`}&<xbMJVh0Op!p9(<(emi>Da$bwaix6wisdo=4w?0Ap=<%wn&UNWbc6y?xwDJtHgpIb`UFh'
    'k+L2FVRtHIm=uMO}JXJ&`Ig4qve64kwZsfprDqyxMZi6?}ng=gxmd20jX)hA^KJ2a8RR!FuJ{ExB|oamM527<qZB'
    'xI%a+lYMgtU*NC7VxjL1)S)B=|+IRg=F%$`i|M(AfmtD-tSnovZ3E>=r<es{U;duy>g~rX>ahp*r(bW94$55^u5i'
    'd@6`mp_ptd%R(wax&E|W*VZQe&s@{8~`~-u&qh)4Gy}!Gq-fM=yy+`!@ZSzWzV0Gq#W>HCWVz%5C$jCa-ItPc#4y'
    '=d1GYbKPis9U80Frn_>?DBZwK@@>3<N)l`pB0NMol3S_Tj2)9LbVUkrnuh`-Y8>Qm8;vsb^c@CY%+0Z*mopMGePP'
    'ktk7uC5pFaZ><9dtV18ILD!_(*IH2>*6ixhjq$uay34&7GTTAx@Ls0fhMEXuYqBH~JK7_UTUy|%Wq*4jZzUn$?U<'
    'qh&nb6?#hS~<ZlH+=mfg}ihxqK6_7A<@o2lgoS@j?=H5Rey5=;>d2JKQ+C$ks2KvWcVfD2>UT$eKyy(pQCazoz8m'
    'dkEDc^h^koQcY*W~y@7%wuannXt8JSmBi8Uk@z1{>`p`v+LjN`Zv4&&8~m5>)*e}^{-|KXXn3Z=fAMpfLJQ(U*H('
    'rl&AM{a7~2u@~xx)c*En!f`T3(@!~<u<DC=%n0pg>e7)&~^{Q7?!NLKBC;pgfY9HZp$h)0lp<1mCv4Kr;j0@}&Z8'
    'oJEKD*;OB#9^0>k-M5DlwJrglgf_h<CwmhC8Nua3E|dBGOkfR&j{ytQh-d2Zx=e5@TKFS7$a}7r(=<L4l;f)$>5?'
    '9%LIy&2Pep?sZ7okT&G1>u*K4t6LO;VqSdnN>3^`A$*0kqpOj-W!8n85F)>=z;hI?b@xKrHhp=I{s5m!Ah7}`FV+'
    'IM5gTl&aC2K<*m^_xai7iwM94dZ4H;NMyuaN6tMV*`sL{gvhL6a%Va6j6aiO={`X1e*5xNKcd!dEH)!nEHvV!%^v'
    '-wnk5knk2s#>=qJU550Q**4jr64|f2kM>4EC~#ovY^j9;zK#y`X0@0o9zW1cp=gbC8o)0<j#oj-h{rZ;Qq0_`@|&'
    'qUYIxUHMz69Z8(;2xZm(Pj`yOzqD7swdC&WsDF7lOB~#a83g1T4OS>bDR*f0!+1`xz9VHU0dt%&_U|R}=x9_%@0l'
    'xxois<~U-&X*8ynPct9?N29F1NRJP2arXi@<&AhP+LD#()h6Zf!DCZ|-I0dbe<ozDJAU?Ajy$NKJ9*Wtf!rMQs+5'
    'n^(I-3Hr!%p+~v-+w0huUnsr@dF$%tRc#AbxB4AG?m2?sB#Ao7uu#%l`5n=%V)qVV3c{VDy0nerE%Iqz0$-KpIc}'
    'Qs7xTv@qOD$Qy!uue8kYMliFv$fWXR`q7@V48i5@KR6{SNe!a|O(MJE20R8HDZlFtkcvrNIGESNK<ZRc2TO!JUc@'
    'Fv>spuCP{ln2nK2`8<qK9X`qW#VRk)a`<G{)@P9YEmI91a*D7;(4Xm0z!JfN62PH$3J9h;d8F-SS+mXrS-kCz8|g'
    'cC+qv!`ksF-ESw7q=fc9duy8IcoC^!*!os<<a4s#JOAF`H!nw3?E-jo(3+Kwhxw3GsESxI~=gPvlvT&{}oR1dHM+'
    '@hph4azE`Do#Mv~WIJIG-$>PZrK63+I!C^U1>bWZ^X5!e~%I$DRqSt?!hGLILP9Oya9gxYENx05yxi;2ZJ8*z+!r'
    's?=DUIe;+mU<<3zVmYy4bYNizmUdue_<*WDF#g;6(=jVfOaXQ<ds(AM4U0CpF^hyRW3FI~kAf7L;o~_R3(uCy7Dl'
    'nG0h|~`8jfQTaA0@P#>Ref5m%!f03+RLrA1HJ!CZf{bLU7^zU$LDhVD0W<!m<-*K)GCUnp)H?H%NSPWD$1L`>W0N'
    'Wg`1RpC*krJArK>LVT+EkP${acj*@2_hq!UlW=0t<xoF(pmRNC38qpwX;JfQoBbK4!X&!A`Eh5t?P6Om^5{3C~PH'
    'Eim+fBX_?KA=Lp42=gpg|Huu5{qXVT1k)SEU@bWc`6=mQwo8KtO>KF@39smrGim+j*4>bh64Y(oI0O$EY_sZZI!K'
    'Kk4K9IrGhTb1^@f<R#bo@}GE%qqE8;%*0!_`8Iq@`911vHybsL#=!j=*|;(5=1$Dnqgxkf|q#JJd^|QuPWE93$}c'
    'KD+<S?mx5p&%ek0r<#`_fdGXAKaudx$l4Pd(1H&wJ4XR+&6|T-430u<7@WV4^>)jm#1zyPz4h~qZDx_I2UscUHJ`'
    '013vTt)ti$?z%rU&^!})^GzhvAQr+~Iy^?IpA&%n2{$ftvf3`2A=vaHEc6$od3po9zRUON$gN*FcNLG-WJ5pW`+2'
    ';^bWnKptSdy4J?{DG#a`6~i%>!67SC(Cxp0bZqJ1+-UazQC}0A<dHy5E?#<4<#=H_w`j-nA<Wn2al2KDkgcZtefP'
    'zu6nkk>?`wJSv|+Mb}AG5d7yDHxD0y3gI;Ipu)<%0oeb+p47H3RcA)HF%g|8Rk)WZH)r;>~*&ST9Y4uT4#f|ur!{'
    '|7j?ap&@1&YYq<P<?l6zX0W8uQv_X)g;CC^Vxqs^~)E%Zpx#?DFWo?aop$AV5WGnI;l|u?yVQpIVm?&WFbM!LXm$'
    '=3R+;Eacow(*3rQ#0)@Q&amQC<s0401ua{4P&a#PT%0hhfq;p6x-@i!v@J4dQw;GEmFWoNA}F;{r4}v%<VtYdGLA'
    'x7;z;*j@Z@tUJtrf!k$jdyM2SuV8XIF4V#{2mZTH3@0LpieY+wn3%GwZx71!xgRtGL4@K%pYx|VXXjS5-i*|uWi6'
    '|@vS+0K$>E`hE7SP{zlj}?VhfNY2wvLN%?M9Hap@$j(J<H|P4(BZnGBH|T=nT{gtTBR8zE8DVW#Zj=Wx<S#+c<v5'
    'ZKbTGU%r9^>`UI!R3*gzlkonI8JgFZfeueSNCyFoe2vp*^bp1$vZGf>jfB2j~QYt_{7js}BGm;m``~WTeTyQcV{P'
    '8(oJRdQzIDoh!@Q$BfC@9M(V0a`9OUkh?U(2@|N`N9(3@A|xq@a$hfNgmIMiE|S*w&bi*^;R&$OJM1U?dX`-Or2S'
    '^9S2P)A1`vd4$%y6c5k%BmqkhM}y~{r3P2gPXPV$gpFOju=yc0gf@RJfW`a>M0@=FF{gR~O`(Ow;`v7b?BwOVfa='
    'm49&rpY!(vgafI|$_HSy)r`Nj&&e-uk#PQTb->y`CwWdWK4m7&I;%Lf}CIua|h1P1ofju*|sGhOumve-(<AH(z23'
    '|~3Az5IxPF23mCatkXmyp?P(WKWx!cBCiNk}qs4hPI3faRP>}BelOlNj%L3sHKew&xoklP@ikUgqnL_XS5WiY|W~'
    '3Bbc-KM8Ebh(<K@-pTKsNTzBELjuyypu_-tGq{6)jGi7L{F5JeLLC0FQ>xyK9Sf-d+l(ME^v9|m;Fj?T<g_h0W*A'
    'xf))?c{$4l4T5;`Kuq`NZPw<f<+ine9tAb&y&*iF#M5Ka~}>4L)8?Lf>A5dtb81G+tcjC|~dJff7i6AR}H}KD3xs'
    '&N#?o*_%r3dpg+)74=RwT(lD>md3j`IMtYRRa0f(oUPT&%I&`{XhaweLmi5Bizg>*gE^8}Kh~|=)O@L@@o%C!(74'
    '*@Jwv37*-Gx=&7_`79M@<P?~S^d!|V1!Udi|Z4iYmk9=B}#uhn+USWT5=n_&d;{jLKc7-hrhh}Ei3#smuM<FL#2l'
    '6luk5SE<0w!**%#j~y>1-$}mDW_Fr-5uab6qG9ZJ!|d}b?^{EJ5Aq^Y5_1MK@%4qURC|8EstiOo`dZ(+znz@SQ3Z'
    '2z%&^><zJqltO4ACrSOf31(S0p9Y7V|bz{$oNF9{byAC<#d^&j`UZV~!mu~p!$qmDv<3=p}h@~H~qKF<$C*rXHYq'
    'ffQcqrby$j4<U@<$-@=`j%bya+_TyaXcWa|H_eOE`<z_J}?BmA$_Y@XN%*fjKgG?q(*3Wp36)T9!ghWXM#i;$jH1'
    'Im)?`^e`vI&KzW12|$$1Cg~xLkR%1rKB=@cf99awB1W2a(55&-ZF8~*8>b+mty2J@=Bcz``wsT4;JpNqH2dB|a&>'
    'T+);TQ45{zNudVsJqzl>}eJevm3roppm@N619n+DIO!KZoOitVp$%N#NBs|?PKPFzj-roN@ey-JS3^6eyW7Za!Og'
    'gmv?gV~%{UfLp&_E5+zcVcd~VihYlmAXjaU5wT$ojYA_Dpi#f#~y|l)^IweDfJm?(K1Pm<v2Bc{2qo?vh-DQ3@nr'
    '5XE{FpQgvI6mA-NgzIw7vJpKZI8V=LeZP<<Y(+v{`ZUmz_m~Tid&JNS`b|Ppeb7GbQn8!iP(;(N&0OrS|MHnY#j5'
    '7Jz+IhB)kmv5t*O78YpRptP@^f~6&Ym#Kf9bP!qz-p`-j3k^t)IEQHtU^=9n)xEqii23^K~*`C-ZeOUnlc*GG8b2'
    'b%HM6L~K~?#@c-aGkc)7Dmf$YqchcG3-5DP_pL2?CV7cBbRgqZ+>hJFoJ=Hupz<Rz2Y8<@BwBy_X&9C`K43VW%C4'
    '%cZnGsFrVO~Esa1Gf-m=LsW%>Bl5{2C4d>pK!_2LtlK9(j%esmJZ`>4bv|Ex^n6aRd>YL*1UnfL?Dr`w8QYFp8OM'
    '<ppRsE2zc!4LCApOn8>ftiECbO{(dK7!g4$Oh2ST`aqqSj$YTiNu4h7bW)&$&YplOOW8fRY*J*m>BKRz(g?{Ku0V'
    'Fxfa7*3(18#|ERNtW@FU#*^U!bc9g<p$AOFw(cg|M*Ufw7=LHiBpB0-?N0C7~69)jiSapgfk)~md?Br1G&>FAU(s'
    'fMq1z^NhwFT6GisQd8mA<-rQJS(6XI)l@u?pB8PGfhsk&(%R+zd%t(`a@urBQsTw+vTzAQwp-BxN`kXN<~3de5J>'
    'R165UH7q#`t4vRFhaiK5Gfc0aIuo|)w#LvbHf<p>9I+3X(&usDVmc;6WFavFA26Yj<iLfMWE_x??16%Lnb^peDUE'
    '!Y+Q^rQjeHqz<jaIcf)wbqR%*axGhKA4c52A6hHAh>OEpZgsZ%?2KB-6Nle=_2wNK|0I(0tMtF*5Zq&~D!==McmH'
    'b9*jDw&~@87i5fk{K$Qp^_OY-x8D=*>~lJZI0g@!T#I$b74N0=5u8}AI;~J`Fu8?FXr=yRm6k!ZIw4)+~rzfaSBZ'
    '9=mpBMRsgrTi&7dOcR=B!-32s0!bt;+D|NQp?K-(Uxp)TvKK22?pp2KXGG4~Y7ywvlx6xf#HHPL~gnt`$Vh2!$nS'
    'qgB9xWarVHeoBpX(?$U2>r1k8Kr>ag!B7iE^QJeI)DwyG?Q;2S6c42IzSjubIPyshpVu*~|@~;RJ<78Ev?23>c1_'
    '83%HOBKF~<{x)CAqXPn1=_b}-{bu##ZC5)qMb9T%6iIm;($YxclExN*DydkdVAq|>GrHl^IaK_)M%zplYR+ehV@B'
    'nPjFNfC11VrVsdh9H<eA%tWAkQl)T(}@0Jj}xQxW3jK?Rk^9UqKbPLZyZIHL*Hr3B}2Zfyjg@i`O9&%Sm#Ra=Y1r'
    ';6ElegrvkW61%F^x{Mgl&3D@MM4}sd3`3neN^ne22N!QHhU3;mcSTf(yH5jigx=s7B9q*<aL--k~%5Yko8#MYPZL'
    'u6gk{;!piZ@Fw&MlaZ{DYEYfWv1241|;`<FMszs7WE1dmaPMfW43XcPpAvfw@*0xe?e$p)mjZ_^AoOPhBa_L8g2x'
    'UF9-G<3lhm7BVCuzOPII&`bkt;z*T<w^itDxeX+NwxZTXGwzBDG@&7gj6QyU`-l6l#t%!t>FniGm&>qlsQ=Dw<`J'
    'wmNL@7q)dHi|1^E=%O_(W$X|koZ54YmD%Z_&=bTUhX{%3`l!qds0irCyJIHkQ=C$$=8=($0;{tPdX+@ep6p!`e^8'
    'oAxsxo}JRYe@it;f1^rJ{;PF8xOo73*O<kva+&z1-t>3c!nOWIZWKf-_?q#yhPC+^WQ-RhIbu03<&K41rKVzWb3%'
    'g}vxhZ^+qn{wBgopokso!MDucGj7lb!KOs*;(g5z*%Q@)j7#kr#@nn6)2cCs0sBSU}r5_-)qdRMUiByYuW1BxYae'
    'dq_e*@a7ZfNle%IJVrX?kW(~h)c7XH(?J(W)1;HPL65KriBJoi{Hod$ILksLSz`zRocm<USsI~#iaI6&6fu(<HGP'
    '*Lbr`$L;skBNZ-ZdaW>u+o;N*p9$1iEjl_IS2xLnZ9M78aa>;EODesUR&wP6WNgz1PUrwBiT`_>(?}iVBoSUPVxM'
    '3mK(ozix(ARjOj!2CqDD&xG|3H5h$hS`&~{GuK}W{k5D{-Vmv{4Ix{eQs&&Y?<sK$ZRgYYT_HR2>?p;;7&i1TYiy'
    '`d;+Qy;6mSRNL#0OKg!a#_XodD1@Dqw4zh;dxdnO=7`3`3Ih}@=iw2|;Rr(T1Rz8<Gog~xU~ju>!(XnI{x4<;vY$'
    '@a=u32<{l$0axb(}v0KNnU2J63WL4_$Py1jOZg@f652mFbV}mBl{Fdg8^?HzAXrN9BK~lbUPA{F2h>jGm!eFhRY}'
    'Ml-J@^8>ba75tb!N4;Oe?p6!W0&pyNTw^Jqb!)({rLjs3@*9-cMRv*0N(Osz7k@U7opc4aq;t@fw)G>tg=5-JSS{'
    '*PGL@DJ{tVK>0*|e!*&@LhzOm=wcYpJ0eW9$@Q94GU8%83UFF~~}0J&Qo1?llUB3*rzx@02HDt=cj6QPWGYj+|lK'
    ')Z3=|yle1?Mr9Z5OHp@ahHuZp3v0X)iyADjnroPvz;J3<xCA9H55h%5Uq3WY;4!Ez*a1;DUYD6J0Efh$9xnLqPBX'
    'wR9us-|8-Rl~l##H7sl1bYydHk*$nF9cR(({%rl_Hd84qX}l<0`8T0lsRk$9%u5X8fWmq+wwO$*ssKS7^+%EbEtY'
    '=^u|NeWqx<kN(Sq(y|{%=$7+3d55pS7dCf+C*#FR?0gUe}!r(DY}9RGEl)`QW$=E1?fX0LtC%t!Vo6V7t0!;tq^p'
    'JNJ|d#cm^1Wy`7D6gpG0piF0?89KljX4RQo?Wpf<a9EZIV1P944HO3LF!QD)81hN0thB%xS%dME=z-uqoM88+d{a'
    'Za>QleoUR?y(y;xBjC6)<zK=hyN4I-Xz0^Xqti9nY`h`E@+Mj_23${5qar$EUrHCyv|vLp)#ODOt87T1eIYYHy%}'
    '1NQI?9z1&Lxdcvp*1VOwG2U+Oo<D>dXq*R|qK}0p!r1EJg_I~N&gsB)4zH(tmQW#oSZSBg3#WmLRC6hn#LXA^+7a'
    'w~CQQC~(2QC*Q_BzX{0&TvMQpkRQ)C&?M`oR@ja>OrQP=@4jAgIF&Q$cGWHM4LOh>lqAjdRh5R)dP72!-&PBl}N!'
    ')6{^1ImQ0MZ*fGE_NPRzS`xhUB24ot6jd@<*Qx3+WkFOJKB=-<?fr8I}SvYdrQ)WBoik1el6x;*@g_6JedcQgVwr'
    'yprQ4yAew<SFCQvs-OC5^t$q3F1M6Q3fPBeDnoDWPwh~0Vp$0*;l?0M(B0<F3M~Q>RvDDDqweA~fY!Wuu_+*YDF~'
    '$oR5GR=>NUUTIpLj{&0WrJF8Vw+@X$_xxZeoyJF36BR0Tcs*xG+HqxFCL$-PA!FwUR@)m40%toj%a8r9m`<w)#-P'
    '*7`txd;Ro5i}Bn7Os`0Tz0_cPJ(yv0Lr4a#^?-tn^<ezAddY*P+LlYacG^k7M%n<w77nrxO*7h7Q$lUC0sMy9X~|'
    'ZNY+otR(N>RdYoq9sRGGBhr81<bHo6U>X`9&iC>(R~K4icaToT?l4mXb6vlf@k5HKH?gm>-9B|$v{a}I2DV@-gK5'
    'iYfzj-gGFY-AHn04Io**g9Q6VCQa8i*1ZlF5DQcT<9dR0*F)8a>2*Q<w7Uu<pQP%#**If53Ir<aChb5eugJ|eZXf'
    'ta_m=@{;ozjtP_gRVH%%w=xd?BmilX@zaI71lm2?vUoZOWhyEhnKKV4IfRV!S%5&f+`ZJhVboOMBJsJEmPX<%R<U'
    'ibp!PI7C?*-X=LH1to+j%dzX8LEp1=(*w_FIts7G%E#*>6GiTku`K1ygt2|0ItEQ`?k%72L~L!BmQ8F9pA&mx9T?'
    '|Ev8Ij8%-RLg!mUzBS}qL%ucSTSLAz<Xc0~eY|*2p!)+oVQMa(arvU&I7M>`Bd^(pXF5L}4GIe#K8=DvrdGYtmSo'
    'UkhkG<qp!_5j$|z4Yjd$`QBYBPu6fG@oCsDCFMewV_2~eN+B+<ri%6F0L2KktE&F$jRJfU^!6i|9~ie%GmwhpsXi'
    'K>;7gse_@jIg2y6ejH;(ISCeim8T0U>m?K$tSX#5-DSp&^9pWuPm-0wg|zIhbJD>*Bwx2YC7Rdc6t74$#mkTJiV7'
    '4sk)u&BUxR2hcyE5kc=>r2sPRc6$vo2(bsiJH`Th^Ly=%_kwlD3ddcGz1`J%W#u+caI=F7J=XDU;ajL~S=|@Mlhg'
    'sj^YeOEcurOA)+w4W$zvE|1w4lkW4ZN0i-K8?XXztLDqa_IB-aE9Fvu-Z%D9R3?+Ba(D;Y5#)O-UYnz+Mb2pdU@6'
    'ZQTmxrqf#qV&pqPz7ym-LB12@J3+n^<U2v|PGDpfX{&X#D#!|arI?1Gv5i`Dgsa=LnN-x{y?R@oNq!VRYz|}`fct'
    'XW7(06sKv4OSm_q}CUJ|Xp{WJ_q9GlA{gPqsbQ#aYLIkmDqs>Sd5&}CVvxS=p1G&!n+cLCy=!XP}e$e50iADskl3'
    '{>Khe^w^(iGRjwg>z*l=267}B6G*JF;-z^$8*zkW9>qDhjFys#6TpPt0hR=YNU=_JU=LV9U4=b7mP8iKp9kzv!s>'
    'Tw<e3?6k2{XET$X=3(D(66bp<r4`t;QFC_9W@;6>lF;Sj^c;rf^)t5#lrOmi3vntA!nN15yt8%024MxT&(9kGhN!'
    'TYLC>0U%7Re_hR(sZDh;_26#bCQp03_0AyW<Q1-3xzM<|^7p_rmS=M|cF=sFI^Ny#FdR_35M?tWKJ&L`+M%J1Nv1'
    'l;aj{8AN||iCL&S3w8fJLfxrB`JW`!ooYuG>&{}`S*-i_7V93H|5>g(b7M0%HgjV$H#T!)GdK1wa^0ydHw!`k6d~'
    'vo$+HynZ!ZO%>VCs~G9v&*CFDo(ezcWh@KDwh*GfAQ>X`c4rt-xJsr+oXl@nD!8>%A@VMtdMf}6essS@BB=`0>nb'
    'V%ivkglMFbv@ZEFqcc8Rz8lVFCA+`sEn3<JC-{d#2TBt^=T&-6~Shud`X<;2d?rW6a>>!B@aTy0F#Okk6t#c<I8D'
    'RS|gnTN*D~ksXg?i%>N-zhNJmY^<xPRoK*%DptQ*&FDd7)eemWRRlZT>8&$qh<r`JLQDym-xXim2O}}dY%>wSfR='
    '|CV#C52z#zcVgaVZ~{@^L92m-2BbAD8lR>3VTsk>R~|KmKRQ{-!GWi{)`aE30RpALyQDwrMM5M#1nt@9WL1+-{B6'
    'Y#k`d9iQP$%o=@lRZf(W+OmOoxL`~P3S^+wWgmmnRT0nPWIGo4Wb9i74sd(r&I^5f^J4*@=Tta`pAmM-Ik>^UE<2'
    'Q@BWF7Ys3g`{eBvOdQ+&r+>Z{=Cg_yYt`aq6vB%u6p0Dlu))b+z?a1l6&V@G8=zHGm+<d1p_4vQqRFW2hRh&+3R$'
    'gq}aEs?6yZY+33+F}{uR3JH2XxOH5W4F6LVV|K#Kw<7$&VSCe9oklXSsxtlK)8^eO%Ya`RFxzJPt@RbsR6%BUWy8'
    'm!?Mn<rw3?vr%Iy!4rX#m(bqjyJeX*D&>lTHR<Y5CWDFt^Z*Nkr@@c3dU>I+t)11=k4SI=T`X5S|bJmDCXcBbQE9'
    'zD{U0~`dzT$+eU*N~klnZm{)eNzH4dR!;<Nq2qR;pkZuA${+0JdQ17@mD<jpC^pow_<K3#d$CBkv<d!p*Ki5sP7j'
    'T+=BhJl;7nN}ZiB6t7~@SL2r@2DL<})fm(Yp&rMe9uev(;HoC(X2y!wGWQN*C*{!KBShGxK|Fh;E{jNA7SXyaVs%'
    '+es>>o?mt~|b%V=GevAQfL)nys4%PLZrRkSXvSY1|=>avR0<uOv1$7o$1V|96)RF}tiU7jL!d5YHMDOQ)KNp*Q*t'
    '#cAbl;ymG=ek0#E^_pkybSqzKwW)A1$0?s9Hj`~yUx)2%)mzruEcP3?N}F1i)2Ij?A`C&e6S<MbxYNNHnNMgveyC'
    '75&*R)INhiS@DGSj_A0opQ7NOSzAA}QP3PrX+RZK#JNb1Q%szqfgv~A%^$|3d<TyPVfmuv|Sx$giO@Miv0P_@qNj'
    '7>~v!^wDTGOXBep>T~1dum%1J#-KN7L-)j{+^G04=8gt)>7yP62wN%Lfnt5@&fkWvb955vH^Ddx}hF9bm`ADkOf1'
    'RnYd9irR|`DO|}}`ofCQQZHVFeOFMpB+0sxNP=dRlL*By`eN1GLadHhZTV3UHSkziS0AvT)?2=RD(ZD4^ME2T_Ej'
    'xNLU1k2$Dqtx&%E`_ThF}p%v;aA^~_uUhH$sDy>h^qhM<i&t4!rxHSel<SIxU>-c|Fi8ho+ltLU{GtQ{bGM-;|;v'
    '3?`L0F$5EUjj#x6Xsrc;f0r8c;$t8cmZ-jrwbWIx~~JV)I~CNnM_?JQy-J5Pj0GLjYXvLi%7K>kqR#&Rb50XxrkK'
    'HL%WPrZyBlHGE%)|q<YIp^_G$9dD&Ny>a8NxTScn3id1hEsopA5J)ZQTxJX6a#6>D`nMz!x5+75EUJITI^`sYzkF'
    ';b6uoweajsdL303OExyw*KOTK7EGy63UhJ&(2Sd8~EMW377*whmvc2W#Xo(r#Bgb&*V6CR10*)W>A1*ATB7i%8`c'
    'k!mj@6<$QDx`<SA5viVsb{VPOGE%)|q<YIp^_G$9EhE+Qvacf5TScn3id1hEsopA5y;Y=odW{^!MJhU6BcqASRN^'
    'X?_?SxcTHvga!T3l^!fRv_U^xb`8UuJ71Mph+9BJM2SnHn0TK7EGy63UhJ&(06yhg%fb-nv4tm7=cMIS)Bg3Y=+D'
    'ekeDg?nZjIEoit{Z}=^XPaG3qIdF1d?(Vo_)|xH)F)-C5>1jpr7p)4i^PQsKohY7*3GsRh{cf<BYzcGJWHZ+kl{='
    'O8JN`}e#HtFLxEXWp;|w^fzub^CowAy5qcAD*=0NjT;%vrHanJRYE6C+D?Oh{kfj#jp`OBIDgV-;!8?q!pV0^v({'
    '0v$)IDlqQ>bI{(rvT3pb*&nkN^39{~ukopHT'
)
WORD_REQUIRED_MENU_CHILDREN = {
    parent_id: tuple(
        tok[1:] if tok.startswith("/") else f"{parent_id}.{tok}"
        for tok in child_tokens
    )
    for parent_id, child_tokens in json.loads(
        zlib.decompress(base64.b85decode(_WORD_REQUIRED_MENU_CHILDREN_B85)).decode("utf-8")
    ).items()
}


WORD_FORBIDDEN_CIRCULAR_BEHAVIOUR_PHRASES = (
    "to apply its action",
    "supports the command",
    "on the active selection or document.",
    "is active for the selected object or mode in an editable document region",
    "Opens the modal dialog or task pane associated with the",
    "state or formatting attribute in the",
)


def validate_word_ribbon(records, *, require_behaviour=True, full_capture=True, require_expanded=True):
    """Validate `design/inventory/word/ribbon.json` against D02 T01 §5 completeness, KeyTip, expansion and behaviour invariants."""
    if not isinstance(records, list) or not records:
        raise Refused("Word ribbon inventory is empty or not a list")
    expected_build = reference_build(app="Word")
    by_id = {}
    children_of = {}
    for rec in records:
        if not isinstance(rec, dict) or not rec.get("id"):
            raise Refused("Word ribbon record is missing 'id'")
        rid = rec["id"]
        if rid in by_id:
            raise Refused(f"duplicate Word ribbon record id {rid!r}")
        if rec.get("app") != "word":
            raise Refused(f"{rid}: app must be 'word', got {rec.get('app')!r}")
        if "acrobat" in rid:
            raise Refused(f"{rid}: third-party add-in record must not be in design/inventory/word/ribbon.json")
        by_id[rid] = rec
        p = rec.get("parent")
        if p is not None:
            children_of.setdefault(p, []).append(rec)

    tabs = [r for r in records if r.get("kind") == "tab"]
    ctx_tabs = [r for r in records if r.get("kind") == "contextualTab"]
    tab_idmsos = [r.get("idMso") for r in tabs]
    ctx_idmsos = [r.get("idMso") for r in ctx_tabs]
    if full_capture:
        captured_tab_ids = None
        if tuple(tab_idmsos) != WORD_REQUIRED_CORE_TABS:
            raise Refused(
                f"Word built-in tabs {tab_idmsos} do not match required {list(WORD_REQUIRED_CORE_TABS)}"
            )
        missing_ctx = [t for t in WORD_REQUIRED_CONTEXTUAL_TABS if t not in ctx_idmsos]
        if missing_ctx or len(ctx_tabs) != len(set(ctx_idmsos)):
            raise Refused(
                f"Word contextual tabs {ctx_idmsos} are missing required {missing_ctx} or contain duplicates"
            )

        baseline_path = INVENTORY / "word" / "baseline.json"
        if baseline_path.is_file():
            bdata = json.loads(baseline_path.read_text(encoding="utf-8"))
            cols = bdata["columns"]
            idx_ct = cols.index("controlType")
            idx_pl = cols.index("placement")
            idx_id = cols.index("idMso")
            baseline_tabs = {
                row[idx_id]
                for row in bdata["rows"]
                if row[idx_ct] == "tab" and row[idx_pl] in ("coreTab", "contextualTab") and row[idx_id]
            }
            accounted = set(tab_idmsos) | set(ctx_idmsos) | set(WORD_RECONCILED_ABSENT_TABS)
            unreconciled = sorted(baseline_tabs - accounted)
            if unreconciled:
                raise Refused(f"unreconciled Word baseline tab idMso(s): {unreconciled}")
            ref_path = INVENTORY / "REFERENCE.md"
            if ref_path.is_file():
                ref_text = ref_path.read_text(encoding="utf-8")
                missing_in_ref = [tid for tid in WORD_RECONCILED_ABSENT_TABS if tid not in ref_text]
                if missing_in_ref:
                    raise Refused(f"reconciled absent Word baseline tab(s) not documented in REFERENCE.md: {missing_in_ref}")
    else:
        captured_tab_ids = {r["id"] for r in tabs + ctx_tabs if r.get("id")}
        if not captured_tab_ids:
            raise Refused("Word ribbon partial capture has no tab or contextualTab records")
        for rec in records:
            rid = rec["id"]
            if rid not in captured_tab_ids and not any(rid.startswith(f"{t}.") for t in captured_tab_ids):
                raise Refused(f"{rid}: record does not belong to captured tab(s) {sorted(captured_tab_ids)}")

    def _in_scope(rec_id):
        return full_capture or any(rec_id == t or rec_id.startswith(f"{t}.") for t in captured_tab_ids)

    for promoted_grp in ("word.draw.drawing-tools", "word.review.onenote"):
        if not _in_scope(promoted_grp):
            continue
        g_rec = by_id.get(promoted_grp)
        if g_rec is None or g_rec.get("kind") != "group" or not g_rec.get("baselineMissing"):
            raise Refused(f"missing promoted built-in group {promoted_grp!r} with baselineMissing: true")
        if not any(c.get("kind") == "control" for c in children_of.get(promoted_grp, ())):
            raise Refused(f"promoted built-in group {promoted_grp!r} has no child control records")

    for req_grp in WORD_REQUIRED_GROUP_IDS:
        if not _in_scope(req_grp):
            continue
        g_rec = by_id.get(req_grp)
        if g_rec is None or g_rec.get("kind") != "group":
            raise Refused(f"missing required Word group {req_grp!r}")

    for req_ctrl in WORD_REQUIRED_CONTROL_IDS:
        if not _in_scope(req_ctrl):
            continue
        c_rec = by_id.get(req_ctrl)
        if c_rec is None or c_rec.get("kind") != "control":
            raise Refused(f"missing required Word control {req_ctrl!r}")

    keytip_re = re.compile(r"^[A-Z0-9:]+$")
    for rec in records:
        rid = rec["id"]
        kind = rec.get("kind")
        b = rec.get("bounds")
        if (
            not isinstance(b, dict)
            or b.get("width", 0) <= 0
            or b.get("height", 0) <= 0
            or b.get("x", -1) < 0
            or b.get("y", -1) < 0
        ):
            raise Refused(f"{rid}: missing positive bounds")
        if rec.get("captureProfile") != PROFILE:
            raise Refused(f"{rid}: captureProfile {rec.get('captureProfile')!r} != {PROFILE!r}")
        if rec.get("capturedFrom") != expected_build:
            raise Refused(f"{rid}: capturedFrom {rec.get('capturedFrom')!r} != {expected_build!r}")
        if rec.get("source") != f"uia:{expected_build}":
            raise Refused(f"{rid}: source {rec.get('source')!r} != 'uia:{expected_build}'")

        kt = rec.get("keytip")
        if kt is not None and (not keytip_re.match(str(kt)) or "ALT+" in str(kt).upper()):
            raise Refused(f"{rid}: invalid un-normalized keytip {kt!r}")

        if kind in ("tab", "contextualTab"):
            idmso = rec.get("idMso")
            exp_kt = WORD_EXPECTED_TAB_KEYTIPS.get(idmso)
            if not kt or (exp_kt and kt != exp_kt):
                raise Refused(f"{rid} ({idmso}): keytip {kt!r} != expected {exp_kt!r}")
            grps = [c for c in children_of.get(rid, ()) if c.get("kind") == "group"]
            if not grps:
                raise Refused(f"{rid}: tab has no child group records")
            if kind == "contextualTab" and require_behaviour:
                beh = (rec.get("behaviour") or "").strip() if isinstance(rec.get("behaviour"), str) else ""
                if not beh or beh.casefold() == str(rec.get("label", "")).strip().casefold() or "Appears" not in beh:
                    raise Refused(f"{rid}: contextualTab is missing trigger behaviour")
        elif kind == "group":
            parent = by_id.get(rec.get("parent"))
            if parent is None or parent.get("kind") not in ("tab", "contextualTab"):
                raise Refused(f"{rid}: group parent must be a tab or contextualTab")
            ctrls = [c for c in children_of.get(rid, ()) if c.get("kind") == "control"]
            if not ctrls:
                raise Refused(f"{rid}: group has no child control records")
            if not kt:
                raise Refused(f"{rid}: group is missing keytip")
        elif kind == "control":
            parent = by_id.get(rec.get("parent"))
            if parent is None or parent.get("kind") != "group":
                raise Refused(f"{rid}: control parent must be a group")
            if rec.get("size") not in ("large", "small"):
                raise Refused(f"{rid}: control is missing valid size ('large' or 'small')")
            ctype = rec.get("controlType")
            if not ctype:
                raise Refused(f"{rid}: control is missing controlType")
            if not kt:
                uia_id = rec.get("uiaId") or rec.get("idMso") or ""
                is_spinner_btn = rec.get("label") in ("More", "Less") and not uia_id
                if uia_id not in WORD_RECONCILED_UNKEYED_CONTROL_UIA_IDS and not is_spinner_btn:
                    raise Refused(f"{rid}: control is missing keytip and is not in reconciled unkeyed controls")
            if require_behaviour:
                beh = (rec.get("behaviour") or "").strip() if isinstance(rec.get("behaviour"), str) else ""
                if not beh or beh.casefold() == str(rec.get("label", "")).strip().casefold():
                    raise Refused(f"{rid}: control is missing distinct behaviour sentence")
                if "Enabled" not in beh:
                    raise Refused(f"{rid}: control behaviour is missing enablement precondition")
                for bad_phrase in WORD_FORBIDDEN_CIRCULAR_BEHAVIOUR_PHRASES:
                    if bad_phrase in beh:
                        raise Refused(f"{rid}: control behaviour contains circular placeholder phrase {bad_phrase!r}")
                if rid == "word.print-preview.preview.magnifier" or rec.get("idMso") == "Magnifier":
                    if (
                        "zoom" not in beh.casefold()
                        or "pointer" not in beh.casefold()
                        or "visual guides or non-printing formatting marks" in beh
                    ):
                        raise Refused(
                            f"{rid}: Magnifier must describe switching the Print Preview pointer between the Magnifier zoom cursor and the editing insertion pointer"
                        )
                if rid == "word.developer.controls.legacy-tools" or rec.get("idMso") == "ControlsGalleryClassic":
                    if "97-2003" not in beh or "saved in OpenXML format" in beh:
                        raise Refused(
                            f"{rid}: Legacy Tools must record that it is enabled in legacy Word 97-2003 (DOC/DOT) compatibility-mode documents as well as OpenXML documents"
                        )
                if rid == "word.references.citations-bibliography.manage-sources" or rec.get("idMso") == "BibliographyManageSources":
                    if "Source Manager" not in beh or "Master List" not in beh:
                        raise Refused(f"{rid}: Manage Sources must describe opening the Source Manager dialog and accessing the Master List")
                if rid == "word.table-layout.merge.merge-cells" or rec.get("idMso") == "MergeCells":
                    if (
                        "two or more adjacent cells" not in beh
                        or "disabled when the insertion point is inside a single table cell" not in beh
                        or "Enabled when Table Layout is active for the selected object or mode" in beh
                    ):
                        raise Refused(
                            f"{rid}: Merge Cells must specify that two or more adjacent cells are required and that it is disabled inside a single table cell"
                        )
                if rid == "word.mailings.write-insert-fields.update-labels" or rec.get("idMso") == "MailMergeUpdateLabels":
                    if (
                        "Labels mail-merge main document" not in beh
                        or "first label" not in beh
                        or "with or without an attached recipient data source" not in beh
                        or "Enabled when a mail-merge main document has an attached recipient data source" in beh
                    ):
                        raise Refused(
                            f"{rid}: Update Labels must describe copying the first label's layout across the sheet and require a Labels mail-merge main document (with or without attached recipients)"
                        )
                if rec.get("label") == "Less" and not (rec.get("uiaId") or rec.get("idMso")) and "Decrements (Less)" not in beh:
                    raise Refused(f"{rid}: Less spinner button must describe decrementing, got {beh!r}")
                if ctype in ("toggleButton", "checkBox", "radioButton", "gallery", "comboBox", "spinner") or (
                    ctype == "splitButton" and rid in WORD_TOGGLE_SPLIT_BUTTON_IDS
                ):
                    if "State rule:" not in beh or "on" not in beh or "off" not in beh or "mixed" not in beh:
                        raise Refused(f"{rid}: stateful {ctype} behaviour is missing on/off/mixed state rule")
                    if ctype in ("toggleButton", "checkBox", "radioButton"):
                        if rid in WORD_SELECTION_FORMAT_TOGGLE_IDS:
                            if "mixed state is not used" in beh:
                                raise Refused(f"{rid}: selection-formatting toggle must describe its mixed state")
                        else:
                            if "mixed state is not used" not in beh or "spans both formatted and unformatted content" in beh or "spans mixed formatting" in beh:
                                raise Refused(f"{rid}: binary {ctype} must state that mixed state is not used and must not claim mixed formatting state")
                    elif ctype == "splitButton":
                        if rid in WORD_BINARY_TOGGLE_SPLIT_BUTTON_IDS:
                            if "mixed state is not used" not in beh or "spans mixed formatting" in beh:
                                raise Refused(f"{rid}: binary toggle splitButton must state that mixed state is not used")
                    elif ctype == "gallery":
                        if rid in WORD_NO_MIXED_GALLERY_IDS:
                            if (
                                "mixed state is not used" not in beh
                                or "multi-section or multi-object selection" in beh
                                or "spans multiple conflicting styles" in beh
                                or "spans multiple presets" in beh
                            ):
                                raise Refused(f"{rid}: single-scope or document-scope gallery must state that mixed state is not used")
                        else:
                            if "mixed state is not used" in beh:
                                raise Refused(f"{rid}: multi-target gallery must describe its mixed state")
                            if rid in WORD_SECTION_GALLERY_IDS and "multi-object" in beh:
                                raise Refused(f"{rid}: section-scoped gallery must not claim multi-object mixed state")
                    elif ctype == "spinner":
                        if rid in WORD_NO_MIXED_SPINNER_IDS:
                            if "mixed state is not used" not in beh:
                                raise Refused(f"{rid}: single-section spinner must state that mixed state is not used")
                        else:
                            if "mixed state is not used" in beh:
                                raise Refused(f"{rid}: multi-target spinner must describe its mixed state")
                elif ctype == "splitButton" and "State rule:" in beh:
                    raise Refused(f"{rid}: non-toggle splitButton must not fabricate a checked/mixed state rule")
                if ctype == "gallery":
                    if "expand" not in beh and "dropdown" not in beh and "More" not in beh:
                        raise Refused(f"{rid}: gallery behaviour is missing expand control description")
            if require_expanded and ctype in ("menu", "splitButton", "gallery") and rid not in WORD_RECONCILED_UNEXPANDED_CONTROLS:
                items = [c for c in children_of.get(rid, ()) if c.get("kind") == "menuItem"]
                if not items:
                    raise Refused(f"{rid}: expandable {ctype} has no child menuItem records")
        elif kind == "menuItem":
            parent = by_id.get(rec.get("parent"))
            if parent is None or parent.get("kind") not in ("control", "menuItem"):
                raise Refused(f"{rid}: menuItem parent must be a control or menuItem")
            ctype = rec.get("controlType")
            if not ctype:
                raise Refused(f"{rid}: menuItem is missing controlType")
            if not kt and ctype != "galleryItem":
                if rec.get("label") not in WORD_RECONCILED_UNKEYED_MENU_LABELS:
                    raise Refused(f"{rid}: menuItem {rec.get('label')!r} is missing keytip and is not reconciled")
            beh = (rec.get("behaviour") or "").strip() if isinstance(rec.get("behaviour"), str) else ""
            if require_behaviour:
                if not beh or beh.casefold() == str(rec.get("label", "")).strip().casefold():
                    raise Refused(f"{rid}: menuItem is missing distinct behaviour sentence")
                if "Enabled" not in beh:
                    raise Refused(f"{rid}: menuItem behaviour is missing enablement precondition")
                for bad_phrase in WORD_FORBIDDEN_CIRCULAR_BEHAVIOUR_PHRASES:
                    if bad_phrase in beh:
                        raise Refused(f"{rid}: menuItem behaviour contains circular placeholder phrase {bad_phrase!r}")
                if rid.startswith("word.developer.controls.legacy-tools."):
                    if "97-2003" not in beh or "saved in OpenXML format" in beh:
                        raise Refused(
                            f"{rid}: Legacy Tools item must record that it is enabled in legacy Word 97-2003 (DOC/DOT) compatibility-mode documents as well as OpenXML documents"
                        )
                if "State rule:" not in beh or "on" not in beh or "off" not in beh or "mixed" not in beh:
                    raise Refused(f"{rid}: menuItem behaviour is missing on/off/mixed state rule")
                if ctype == "galleryItem":
                    parent_id = rec.get("parent") or ""
                    if parent_id == "word.insert.pages.cover-page" or parent_id.startswith("word.insert.pages.cover-page."):
                        if (
                            "beginning of the document" not in beh
                            or "replaces the existing cover page" not in beh
                            or "at the active insertion point or selection" in beh
                        ):
                            raise Refused(
                                f"{rid}: cover-page galleryItem must describe inserting at the beginning of the document "
                                "and replacing an existing cover page, not inserting at the active insertion point"
                            )
                    if parent_id in WORD_NO_MIXED_GALLERY_IDS or parent_id.startswith(WORD_NO_MIXED_GALLERY_PREFIXES):
                        if "mixed state is not used" not in beh or "spans multiple presets" in beh:
                            raise Refused(f"{rid}: galleryItem under single-scope/document-scope gallery must state that mixed state is not used")
                    else:
                        if "mixed state is not used" in beh:
                            raise Refused(f"{rid}: galleryItem under multi-target gallery must describe its mixed state")
            if require_expanded and ("Selects or expands" in beh or rid in WORD_REQUIRED_SUBMENU_PARENTS):
                sub_items = [c for c in children_of.get(rid, ()) if c.get("kind") == "menuItem"]
                if not sub_items:
                    raise Refused(f"{rid}: submenu menuItem has no child menuItem records")
        else:
            raise Refused(f"{rid}: unexpected record kind {kind!r} in Word ribbon inventory")

    for req_id, exp_kt in WORD_EXPECTED_CONTROL_KEYTIPS.items():
        if not _in_scope(req_id):
            continue
        if not require_expanded and req_id not in WORD_REQUIRED_CONTROL_IDS:
            continue
        r = by_id.get(req_id)
        if r is None:
            raise Refused(f"missing required Word control/menuItem {req_id!r}")
        if r.get("keytip") != exp_kt:
            raise Refused(f"{req_id}: keytip {r.get('keytip')!r} != expected {exp_kt!r}")

    for req_parent in tuple(WORD_REQUIRED_EXPANDED_PARENTS) + tuple(WORD_REQUIRED_SUBMENU_PARENTS):
        if not _in_scope(req_parent):
            continue
        if not require_expanded and req_parent in WORD_REQUIRED_SUBMENU_PARENTS:
            continue
        if req_parent not in by_id:
            raise Refused(f"missing required expandable parent {req_parent!r}")
        if require_expanded and not any(c.get("kind") == "menuItem" for c in children_of.get(req_parent, ())):
            raise Refused(f"required expandable parent {req_parent!r} has no child menuItem records")

    if require_expanded:
        for req_parent, req_children in WORD_REQUIRED_MENU_CHILDREN.items():
            if not _in_scope(req_parent):
                continue
            if req_parent not in by_id:
                raise Refused(f"missing required expandable parent {req_parent!r}")
            for req_child_id in req_children:
                c_rec = by_id.get(req_child_id)
                if c_rec is None or c_rec.get("kind") != "menuItem" or c_rec.get("parent") != req_parent:
                    raise Refused(f"missing required Word menuItem {req_child_id!r} under {req_parent!r}")

    return True


def merge_word_ribbon(existing, fresh, unverified=(), *, full_capture=True, require_expanded=True):
    """Merge fresh Word ribbon records into existing records, validating fresh completeness (across all tabs when
    `full_capture=True`, or within the captured tab(s) when `full_capture=False`) before merging so old records in
    `existing` cannot conceal missing tabs, contextual tabs, groups, controls, or menu items."""
    validate_word_ribbon(
        fresh, require_behaviour=False, full_capture=full_capture, require_expanded=require_expanded
    )
    fresh_ids = {r.get("id") for r in fresh if isinstance(r, dict) and r.get("id")}
    if full_capture:
        missing_existing = [
            r["id"]
            for r in existing
            if isinstance(r, dict)
            and r.get("id")
            and (require_expanded or r.get("kind") != "menuItem")
            and r["id"] not in fresh_ids
        ]
    else:
        captured_tabs = {
            r["id"] for r in fresh if isinstance(r, dict) and r.get("kind") in ("tab", "contextualTab") and r.get("id")
        }
        missing_existing = [
            r["id"]
            for r in existing
            if isinstance(r, dict)
            and r.get("id")
            and (r["id"] in captured_tabs or any(r["id"].startswith(f"{t}.") for t in captured_tabs))
            and (require_expanded or r.get("kind") != "menuItem")
            and r["id"] not in fresh_ids
        ]
    if missing_existing:
        raise Refused(
            f"fresh Word ribbon capture is missing {len(missing_existing)} existing record(s), "
            f"including {missing_existing[0]!r}"
        )
    merged = merge(existing, fresh, unverified)
    merged_is_full = full_capture or (
        len([r for r in merged if isinstance(r, dict) and r.get("kind") == "tab"]) == len(WORD_REQUIRED_CORE_TABS)
    )
    validate_word_ribbon(merged, require_behaviour=True, full_capture=merged_is_full, require_expanded=True)
    return merged


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
    parser.add_argument("--fixture", help="contextual fixture document path (default R:\\scratch\\fixtures\\word-contextual.docx)")
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
        is_canonical_word_ribbon = False
        if args.app == "word":
            records, unverified_records = reconcile_word_unverified(records, unverified_records)
            try:
                is_canonical_word_ribbon = out.resolve() == (INVENTORY / "word" / "ribbon.json").resolve()
            except OSError:
                is_canonical_word_ribbon = False
            if is_canonical_word_ribbon:
                validate_word_ribbon(
                    records,
                    require_behaviour=False,
                    full_capture=bool(args.all_tabs),
                    require_expanded=bool(args.expand),
                )
        if args.merge:
            current_bytes = out.read_bytes() if out.exists() else None
            if current_bytes != initial_bytes:
                raise Refused(f"{out} changed during the capture; re-run to merge cleanly")
            if current_bytes is not None:
                existing_records = _load_existing_records(out, current_bytes)
                if args.app == "word" and is_canonical_word_ribbon:
                    records = merge_word_ribbon(
                        existing_records,
                        records,
                        unverified_records,
                        full_capture=bool(args.all_tabs),
                        require_expanded=bool(args.expand),
                    )
                else:
                    records = merge(existing_records, records, unverified_records)
        if args.merge or unverified_records:
            current_unverified = unverified_path.read_bytes() if unverified_path.exists() else None
            if current_unverified != initial_unverified:
                raise Refused(f"{unverified_path} changed during the capture; re-run to merge cleanly")
            if unverified_records and current_unverified is not None:
                unverified_records = merge(
                    _load_existing_records(unverified_path, current_unverified),
                    unverified_records,
                )
        if args.app == "word" and is_canonical_word_ribbon:
            validate_word_ribbon(records, require_behaviour=True)
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
