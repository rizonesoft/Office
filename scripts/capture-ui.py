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

    def main_window(self, pid, class_name=None):
        """Visible top-level window of one process, matching class_name when given."""
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

    def __init__(self, key, dispatch=None, starter=None, owner=None, init_timeout=60.0):
        row, exe, progid, separate = APPS[key]
        self.key, self.row, self.exe = key, row, exe
        if key == "outlook":
            raise Unsafe("Outlook is not started by the capture tool: starting it sends the Outbox; capture it "
                         "attended (D02 T01 §15)")
        self.proc, self.created, self._created_meta, self.owned, self.started = None, [], [], False, None
        self.app, self.hwnd, self._cancelled = None, None, False
        self._marshaled_app, self.cleanup_errors = None, []
        if not separate:
            # One instance only: start the process ourselves, then use the app only if its window belongs to that
            # very process. An instance the operator opened in between (empty or not) is never touched.
            if self.running(exe):
                raise Unsafe(f"{exe} is running and allows one instance only, so the tool would drive the operator's "
                             f"own window; close {exe} first")
            if key == "project":
                raise Unsafe("Project shows no window before a project exists, so ownership cannot be proven before "
                             "the tool creates one; its capture is built in D02 T01 §13")
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
        return True

    def _emergency_close_com(self, target_tid=None):
        import gc
        failures = []
        self._emergency_quitted = False
        app, prev_tid, _kind = self._unmarshal_app(target_tid=target_tid)
        if app is None:
            failures.append(f"could not unmarshal {self.exe} application proxy for emergency cleanup")
            return failures
        docs, docs_col, count = None, None, None
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
                if count == 0:
                    docs = []
                else:
                    if hasattr(docs_col, "Item"):
                        try:
                            docs = [docs_col.Item(i) for i in range(1, count + 1)]
                        except Exception as exc1:
                            try:
                                docs = [docs_col.Item(i) for i in range(count)]
                            except Exception:
                                raise exc1 from None
                    elif hasattr(docs_col, "__iter__"):
                        docs = list(docs_col)
                    elif hasattr(app, "made"):
                        docs = [d for d in app.made if not getattr(d, "closed", False)]
                    else:
                        raise RuntimeError(f"collection of {count} document(s) is not enumerable")
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
                for doc in to_close:
                    if target_tid is not None and prev_tid is not None and getattr(doc, "_owner_tid", None) == prev_tid:
                        doc._owner_tid = target_tid
                    if getattr(doc, "closed", False):
                        continue
                    try:
                        if self.key == "word":
                            doc.Close(SaveChanges=0)
                        elif self.key == "excel":
                            doc.Close(SaveChanges=False)
                        else:
                            doc.Saved = True
                            doc.Close()
                    except Exception as exc:
                        failures.append(f"close document failed ({type(exc).__name__}: {exc})")
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
            doc = None
            docs = None
            docs_col = None
            owned_docs = None
            to_close = None
            can_quit = (not enum_failed) and (not failures) and (remaining == 0) and (unowned_count == 0)
            try:
                if can_quit:
                    if self.key == "word":
                        app.Quit(SaveChanges=0)
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
                    self.hwnd = Win().top(wh)
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
            proc = (owner or OwnProcess)(Win().top(self.window_handle()), exe)
            if proc.pid != self.started:
                proc.close()
                self.app = None
                raise Unsafe(f"the {exe} window belongs to process {proc.pid}, not the one this tool started")
            self.proc = proc
        elif self.open_documents():
            # Dispatch handed back an instance that already holds documents: someone else's. Touch nothing.
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
                self.hwnd = Win().top(wh)
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
        for attr in ("ActiveDocument", "ActiveWorkbook", "ActivePresentation"):
            active = getattr(app, attr, None)
            if active is not None and not any(self._same_doc(active, c) for c in self.created):
                raise Refused(f"the active {self.exe} document is not the one this tool created; stopping before the "
                              "ribbon acts on someone else's")

    def new_document(self):
        return {"word": lambda: self.app.Documents.Add(), "excel": lambda: self.app.Workbooks.Add(),
                "powerpoint": lambda: self.app.Presentations.Add(), "visio": lambda: self.app.Documents.Add(""),
                "project": lambda: self.app.FileNew()}[self.key]()

    def window_handle(self):
        if self.key == "powerpoint":
            raw = getattr(self.app, "HWND", None)
            if isinstance(raw, int) and not isinstance(raw, bool):
                return raw
            aw = getattr(self.app, "ActiveWindow", None)
            aw_hwnd = getattr(aw, "HWND", None) if aw is not None else None
            if isinstance(aw_hwnd, int) and not isinstance(aw_hwnd, bool):
                return aw_hwnd
            if self.started is not None:
                found = wait_for(lambda: Win().main_window(self.started, "PPTFrameClass"), seconds=10.0)
                if found is not None:
                    return found
            return raw
        return {"word": lambda: self.app.ActiveWindow.Hwnd, "excel": lambda: self.app.Hwnd,
                "visio": lambda: self.app.WindowHandle32,
                "project": lambda: self.app.ActiveWindow.Hwnd}[self.key]()

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

    def _close_impl(self, wait=60.0):
        others, failure = None, None  # unknown until counted: an instance whose contents are unknown is never quit
        try:
            metas = list(getattr(self, "_created_meta", ()))
            for idx, doc in enumerate(list(self.created)):
                if getattr(doc, "closed", False):
                    continue
                meta = metas[idx] if idx < len(metas) else None
                if meta is not None and (meta.get("name") is not None or meta.get("full_name") is not None):
                    if self._doc_meta(doc) != meta:
                        raise Refused(f"the {self.exe} document this tool created changed identity")
                if not self._is_unmodified_blank_doc(doc):
                    raise Refused(f"the {self.exe} document has unsaved changes or a file path")
                if self.key == "word":
                    doc.Close(SaveChanges=0)
                elif self.key == "excel":
                    doc.Close(SaveChanges=False)
                else:
                    doc.Saved = True
                    doc.Close()
            doc = None
            others = self.open_documents()
        except Exception as exc:  # reported below: the instance is left running and the run refuses
            failure = f"{type(exc).__name__}: {exc}"
        finally:
            doc = None
            self._release_marshaled_app()
            try:
                if others == 0:
                    self.app.Quit(SaveChanges=0) if self.key == "word" else self.app.Quit()
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
       shared children under `shell.<leaf>` have their `parent` remapped to `<prefix><leaf>` unless `<prefix><leaf>`
       defines its own override children) or appends to the container if new.
    6. Every retained record's `parent` is remapped to the active container id in the resolved graph so no record has
       an orphaned `parent`.
    """
    if app not in APPS and app != "shell":
        raise ValueError(f"unknown app {app!r}")
    shared = [dict(r) for r in records if r.get("app") == "shell" and str(r.get("id", "")).startswith("shell.")]
    if app in ("shell", "word"):
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

    # Identify container overrides: any shared path that has an override record AND at least one override child.
    overridden_containers = {
        sid for sid in ovr_by_shared if sid in ovr_children_of and len(ovr_children_of[sid]) > 0
    }
    excluded_shared_ids = set()
    for cid in overridden_containers:
        ovr_child_sids = {to_shared_id(c["id"]) for c in ovr_children_of.get(cid, ())}
        for shared_child in shared_children_of.get(cid, ()):
            if shared_child["id"] not in ovr_child_sids:
                excluded_shared_ids.add(shared_child["id"])
                tail = shared_child["id"].split(".", 2)[-1]
                excluded_shared_ids.add(f"shell.keytips.{tail}")

    # Walk from roots to build the active set of canonical shared paths and their resolved records.
    resolved = []
    active_id_for_shared = {}

    def emit_Record(rec, parent_shared_id):
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
        emit_Record(chosen, parent_sid)
        if sid in overridden_containers:
            for child_ovr in ovr_children_of.get(sid, ()):
                child_sid = to_shared_id(child_ovr["id"])
                walk_override_subtree(child_ovr, child_sid, sid)
        else:
            for child_shared in shared_children_of.get(sid, ()):
                if child_shared["id"] in excluded_shared_ids:
                    continue
                if chosen["id"].startswith(prefix) and child_shared.get("keytip") and chosen.get("keytip") == child_shared.get("keytip"):
                    continue
                walk_shared(child_shared["id"], sid)
            for child_ovr in ovr_children_of.get(sid, ()):
                child_sid = to_shared_id(child_ovr["id"])
                if child_sid not in shared_by_id:
                    walk_override_subtree(child_ovr, child_sid, sid)

    def walk_override_subtree(ovr_rec, sid, parent_sid):
        active_id_for_shared[sid] = ovr_rec["id"]
        emit_Record(ovr_rec, parent_sid)
        if sid in overridden_containers:
            for child_ovr in ovr_children_of.get(sid, ()):
                child_sid = to_shared_id(child_ovr["id"])
                walk_override_subtree(child_ovr, child_sid, sid)
        else:
            for child_shared in shared_children_of.get(sid, ()):
                walk_shared(child_shared["id"], sid)
            for child_ovr in ovr_children_of.get(sid, ()):
                child_sid = to_shared_id(child_ovr["id"])
                if child_sid not in shared_by_id:
                    walk_override_subtree(child_ovr, child_sid, sid)

    roots = [r for r in shared if not r.get("parent")]
    for root in roots:
        walk_shared(root["id"], None)
    for ovr in overrides:
        sid = to_shared_id(ovr["id"])
        if not ovr.get("parent") and sid not in active_id_for_shared:
            walk_override_subtree(ovr, sid, None)
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
        if not str(rec.get("behaviour", "")).strip():
            raise Refused(f"shell record {rid!r} is missing a non-blank behaviour sentence")
        if not str(rec.get("source", "")).strip():
            raise Refused(f"shell record {rid!r} is missing source")
        if rec.get("label") and _NO_CONTROL_RE.search(str(rec["label"])):
            raise Refused(f"shell record {rid!r} label contains control or bidi characters")
        if _EMAIL_RE.search(str(rec.get("label", ""))) or _EMAIL_RE.search(str(rec.get("behaviour", ""))):
            raise Refused(f"shell record {rid!r} contains an unsanitised email address")

    missing = [rid for rid in REQUIRED_SHELL_IDS if rid not in by_id]
    if missing:
        raise Refused(f"shell chrome inventory is missing required records: {missing}")

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
        eff_ids = {r["id"] for r in eff}
        for r in eff:
            p = r.get("parent")
            if p and p not in eff_ids:
                raise Refused(f"effective_shell({app!r}, {win_ctx!r}) left orphan parent {p!r} on {r['id']!r}")

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


def _shell_rec(rid, app, kind, label, behaviour, build, parent=None, order=None, bounds=None, control_type_val=None,
               id_mso=None, uia_id=None, keytip_val=None, baseline_missing=None, source_override=None):
    rec = {"id": rid, "app": app, "kind": kind, "label": sanitize_shell_label(label, uia_id or "", id_mso or "")}
    if parent is not None:
        rec["parent"] = parent
    if order is not None:
        rec["order"] = order
    if control_type_val is not None:
        rec["controlType"] = control_type_val
    if bounds is not None:
        x, y, w, h = bounds
        rec["bounds"] = {"x": x, "y": y, "width": w, "height": h}
        rec["captureProfile"] = PROFILE
        if kind == "control":
            rec["size"] = "large" if h >= LARGE_HEIGHT else "small"
    if keytip_val is not None:
        rec["keytip"] = keytip_val
    if id_mso is not None:
        rec["idMso"] = id_mso
    if uia_id is not None:
        rec["uiaId"] = uia_id
    if baseline_missing:
        rec["baselineMissing"] = True
    rec["behaviour"] = behaviour
    if source_override is not None:
        rec["source"] = source_override
    else:
        rec["source"] = f"uia:{build}"
        rec["capturedFrom"] = build
    return rec


def build_shell_chrome_records(build=None):
    """Build the full `design/inventory/shell/chrome.json` record set for the reference build."""
    b = build or reference_build()
    R = lambda rid, app, kind, label, beh, **kw: _shell_rec(rid, app, kind, label, beh, b, **kw)
    base_src = f"baseline:{BASELINE_COMMIT}"
    records = [
        # 1. Shared window frame regions (shell.region.*)
        R("shell.region.titlebar", "shell", "region", "Title Bar",
          "Spans the top 48 pixels of the maximised window frame, hosting the system menu, Quick Access Toolbar, document title, search box, account widget and window caption buttons.",
          order=0, bounds=(0, 0, 1920, 48)),
        R("shell.region.tabrow", "shell", "region", "Ribbon Tab Row",
          "Spans the 30-pixel strip beneath the title bar, hosting the File tab button, the main and contextual ribbon tabs, and the right-hand collaboration and mode controls.",
          order=1, bounds=(0, 48, 1920, 30)),
        R("shell.region.ribbon", "shell", "region", "Lower Ribbon",
          "Hosts the active ribbon tab's command groups and controls across a 100-pixel band beneath the tab row when Always show Ribbon is active.",
          order=2, bounds=(0, 78, 1920, 100)),
        R("shell.region.messageBar", "shell", "region", "Message Bar",
          "Appears directly below the ribbon as a 32-pixel banner when the document raises an information, warning, error or Protected View notice.",
          order=3, bounds=(0, 178, 1920, 32)),
        R("shell.region.documentArea", "shell", "region", "Document Area",
          "Occupies the central workspace between the ribbon (or message bar) and the status bar, shrinking horizontally when task panes dock on the left or right.",
          order=4, bounds=(0, 178, 1920, 832)),
        R("shell.region.taskPaneDock", "shell", "region", "Task Pane Dock",
          "Hosts docked side panes at the right edge of the workspace between the ribbon and the status bar, defaulting to 320 pixels wide.",
          order=5, bounds=(1600, 178, 320, 832)),
        R("shell.region.statusbar", "shell", "region", "Status Bar",
          "Spans the bottom 22 pixels of the window frame, showing document indicators on the left and view and zoom controls on the right.",
          order=6, bounds=(0, 1010, 1920, 22), uia_id="StatusBar"),

        # 2. Title bar elements (shell.titlebar.*)
        R("shell.titlebar.systemMenu", "shell", "control", "System",
          "Opens the window system menu with Restore, Move, Size, Minimize, Maximize and Close commands when clicked or triggered with Alt+Space.",
          parent="shell.region.titlebar", order=0, bounds=(0, 0, 22, 22), control_type_val="menu", uia_id="MenuBar",
          keytip_val="Space", baseline_missing=True),
        R("shell.titlebar.qat", "shell", "region", "Quick Access Toolbar",
          "Holds pinned one-click commands and the Customize Quick Access Toolbar drop-down on the left side of the title bar.",
          parent="shell.region.titlebar", order=1, bounds=(42, 0, 244, 48)),
        R("shell.titlebar.autosave", "shell", "control", "AutoSave",
          "Toggles automatic cloud saving for the active document when stored on a connected cloud drive.",
          parent="shell.region.titlebar", order=2, bounds=(42, 9, 118, 29), control_type_val="toggleButton",
          id_mso="AutoSaveSwitch", uia_id="AutoSaveSwitch", keytip_val="1"),
        R("shell.titlebar.documentTitle", "shell", "control", "Document Title",
          "Displays the active document name and save state and opens the rename and location flyout when clicked.",
          parent="shell.region.titlebar", order=3, bounds=(287, 0, 134, 48), control_type_val="button",
          keytip_val="B", baseline_missing=True),
        R("shell.titlebar.caption", "shell", "control", "Window Caption",
          "Displays the document title and application name across the draggable title bar area and toggles maximise on double-click.",
          parent="shell.region.titlebar", order=4, bounds=(287, 0, 497, 48), control_type_val="label",
          baseline_missing=True),
        R("shell.titlebar.search", "shell", "control", "Search",
          "Focuses the title bar command and content search box (Alt+Q) and opens the search suggestions flyout.",
          parent="shell.region.titlebar", order=5, bounds=(784, 8, 368, 32), control_type_val="menu",
          uia_id="TellMeControlAnchor", keytip_val="Q", baseline_missing=True),
        R("shell.titlebar.account", "shell", "control", "Account",
          "Opens the account flyout showing the signed-in profile, account settings and sign-out controls.",
          parent="shell.region.titlebar", order=6, bounds=(1726, 0, 50, 48), control_type_val="menu",
          uia_id="MeControlWidget", keytip_val="ZP", baseline_missing=True),
        R("shell.titlebar.minimize", "shell", "control", "Minimize",
          "Minimises the application window to the Windows taskbar.",
          parent="shell.region.titlebar", order=7, bounds=(1776, 0, 48, 48), control_type_val="button",
          baseline_missing=True),
        R("shell.titlebar.maximize", "shell", "control", "Restore Down",
          "Restores a maximised window to its previous floating bounds or maximises a floating window, and shows Windows Snap Layouts on hover.",
          parent="shell.region.titlebar", order=8, bounds=(1824, 0, 48, 48), control_type_val="button",
          baseline_missing=True),
        R("shell.titlebar.close", "shell", "control", "Close",
          "Closes the active application window, prompting to save unsaved changes before exiting.",
          parent="shell.region.titlebar", order=9, bounds=(1872, 0, 48, 48), control_type_val="button",
          baseline_missing=True),

        # 3. Quick Access Toolbar default commands and Customize menu (shell.qat.*)
        R("shell.qat.autosave", "shell", "control", "AutoSave",
          "Toggles continuous background saving of the active document in the Quick Access Toolbar.",
          parent="shell.titlebar.qat", order=0, bounds=(42, 9, 118, 29), control_type_val="toggleButton",
          id_mso="AutoSaveSwitch", uia_id="AutoSaveSwitch", keytip_val="1"),
        R("shell.qat.save", "shell", "control", "Save",
          "Saves the active document immediately or opens the Save As page when the document has not yet been saved to disk.",
          parent="shell.titlebar.qat", order=1, bounds=(161, 9, 28, 29), control_type_val="button",
          id_mso="FileSave", uia_id="FileSave", keytip_val="2"),
        R("shell.qat.undo", "shell", "control", "Undo",
          "Reverses the last editing action on click or opens the history of recent actions to undo several steps at once.",
          parent="shell.titlebar.qat", order=2, bounds=(190, 9, 38, 29), control_type_val="splitButton",
          id_mso="Undo", keytip_val="3"),
        R("shell.qat.undo.dropdown", "shell", "control", "More Options",
          "Opens the chronological list of recent editing actions so multiple actions can be undone together.",
          parent="shell.qat.undo", order=0, bounds=(215, 9, 13, 29), control_type_val="menu",
          uia_id="Undo_Dropdown", baseline_missing=True),
        R("shell.qat.redo", "shell", "control", "Repeat",
          "Repeats the last editing command or redoes the most recently undone action.",
          parent="shell.titlebar.qat", order=3, bounds=(229, 9, 28, 29), control_type_val="button",
          id_mso="RedoOrRepeat", uia_id="RedoOrRepeat", keytip_val="4"),
        R("shell.qat.customize", "shell", "control", "Customize Quick Access Toolbar",
          "Opens the menu to toggle common Quick Access Toolbar buttons, open the full command customiser, move the toolbar below the ribbon or hide it.",
          parent="shell.titlebar.qat", order=4, bounds=(258, 8, 28, 31), control_type_val="menu",
          baseline_missing=True),
        R("shell.qat.customize.automatically-save", "shell", "menuItem", "Automatically Save",
          "Shows or hides the AutoSave toggle switch on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=0, bounds=(261, 39, 234, 28), control_type_val="button",
          id_mso="AutoSaveSwitch", uia_id="AutoSaveSwitch"),
        R("shell.qat.customize.new", "shell", "menuItem", "New",
          "Shows or hides the New Blank Document button on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=1, bounds=(261, 67, 234, 28), control_type_val="button",
          id_mso="FileNewDefault", uia_id="FileNewDefault"),
        R("shell.qat.customize.open", "shell", "menuItem", "Open",
          "Shows or hides the Open button on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=2, bounds=(261, 95, 234, 28), control_type_val="button",
          id_mso="FileOpenUsingBackstage", uia_id="FileOpenUsingBackstage"),
        R("shell.qat.customize.save", "shell", "menuItem", "Save",
          "Shows or hides the Save button on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=3, bounds=(261, 123, 234, 28), control_type_val="button",
          id_mso="FileSave", uia_id="FileSave"),
        R("shell.qat.customize.email", "shell", "menuItem", "Email",
          "Shows or hides the Email attachment button on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=4, bounds=(261, 151, 234, 28), control_type_val="button",
          id_mso="FileSendAsAttachment", uia_id="FileSendAsAttachment"),
        R("shell.qat.customize.quick-print", "shell", "menuItem", "Quick Print",
          "Shows or hides the Quick Print button that sends the document directly to the default printer.",
          parent="shell.qat.customize", order=5, bounds=(261, 179, 234, 28), control_type_val="button",
          id_mso="FilePrintQuick", uia_id="FilePrintQuick"),
        R("shell.qat.customize.print-preview-and-print", "shell", "menuItem", "Print Preview and Print",
          "Shows or hides the Print Preview and Print button on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=6, bounds=(261, 207, 234, 28), control_type_val="button",
          id_mso="PrintPreviewAndPrint", uia_id="PrintPreviewAndPrint"),
        R("shell.qat.customize.editor-f7", "shell", "menuItem", "Editor (F7)",
          "Shows or hides the Editor proofing command on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=7, bounds=(261, 235, 234, 28), control_type_val="button",
          id_mso="WritingAssistanceCheckDocument", uia_id="WritingAssistanceCheckDocument"),
        R("shell.qat.customize.read-aloud", "shell", "menuItem", "Read Aloud",
          "Shows or hides the Read Aloud speech command on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=8, bounds=(261, 263, 234, 28), control_type_val="button",
          id_mso="ReadAloud", uia_id="ReadAloud"),
        R("shell.qat.customize.undo", "shell", "menuItem", "Undo",
          "Shows or hides the Undo split button on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=9, bounds=(261, 291, 234, 28), control_type_val="button",
          id_mso="Undo", uia_id="Undo"),
        R("shell.qat.customize.redo", "shell", "menuItem", "Redo",
          "Shows or hides the Redo or Repeat button on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=10, bounds=(261, 319, 234, 28), control_type_val="button",
          id_mso="RedoOrRepeat", uia_id="RedoOrRepeat"),
        R("shell.qat.customize.draw-table", "shell", "menuItem", "Draw Table",
          "Shows or hides the Draw Table pen tool on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=11, bounds=(261, 347, 234, 28), control_type_val="button",
          id_mso="TableDrawTable", uia_id="TableDrawTable"),
        R("shell.qat.customize.touch-mouse-mode", "shell", "menuItem", "Touch/Mouse Mode",
          "Shows or hides the Touch or Mouse Mode spacing selector on the Quick Access Toolbar.",
          parent="shell.qat.customize", order=12, bounds=(261, 375, 234, 28), control_type_val="button",
          id_mso="PointerModeOptions", uia_id="PointerModeOptions"),
        R("shell.qat.customize.more-commands", "shell", "menuItem", "More Commands...",
          "Opens the Options dialog to the Quick Access Toolbar page for adding, removing or reordering any command.",
          parent="shell.qat.customize", order=13, bounds=(261, 406, 234, 28), control_type_val="button",
          baseline_missing=True),
        R("shell.qat.customize.show-below-the-ribbon", "shell", "menuItem", "Show Below the Ribbon",
          "Moves the Quick Access Toolbar from the title bar to a dedicated strip directly below the ribbon.",
          parent="shell.qat.customize", order=14, bounds=(261, 434, 234, 28), control_type_val="button",
          baseline_missing=True),
        R("shell.qat.customize.hide-quick-access-toolbar", "shell", "menuItem", "Hide Quick Access Toolbar",
          "Hides the Quick Access Toolbar from the window frame until re-enabled from Ribbon Display Options or Options.",
          parent="shell.qat.customize", order=15, bounds=(261, 465, 234, 28), control_type_val="button",
          baseline_missing=True),

        # 4. Ribbon tab row controls (shell.tabrow.*)
        R("shell.tabrow.file", "shell", "control", "File Tab",
          "Opens the full-window Backstage view for file management, printing, sharing, account settings and application options.",
          parent="shell.region.tabrow", order=0, bounds=(4, 48, 54, 30), control_type_val="button",
          uia_id="FileTabButton", keytip_val="F", baseline_missing=True),
        R("shell.tabrow.tabs", "shell", "region", "Ribbon Tabs",
          "Contains the ordered core and contextual tab headers along the tab row.",
          parent="shell.region.tabrow", order=1, bounds=(58, 48, 1850, 30)),
        R("shell.tabrow.comments", "shell", "control", "Comments",
          "Toggles the document Comments pane for viewing, replying to and resolving review threads.",
          parent="shell.region.tabrow", order=2, bounds=(1655, 51, 88, 24), control_type_val="toggleButton",
          keytip_val="ZC", baseline_missing=True),
        R("shell.tabrow.editingMode", "shell", "control", "Editing",
          "Opens the document access mode selector to switch between Editing, Reviewing (track changes) and Viewing (read-only).",
          parent="shell.region.tabrow", order=3, bounds=(1751, 51, 80, 24), control_type_val="comboBox",
          keytip_val="ZM", baseline_missing=True),
        R("shell.tabrow.editingMode.editing", "shell", "menuItem", "Editing",
          "Allows direct changes to the document content and formatting without forcing tracked revisions.",
          parent="shell.tabrow.editingMode", order=0, bounds=(1753, 77, 150, 55), control_type_val="galleryItem",
          baseline_missing=True),
        R("shell.tabrow.editingMode.reviewing", "shell", "menuItem", "Reviewing",
          "Restricts edits to tracked insertions, deletions and comments so others can review suggested changes.",
          parent="shell.tabrow.editingMode", order=1, bounds=(1753, 132, 150, 55), control_type_val="galleryItem",
          baseline_missing=True),
        R("shell.tabrow.editingMode.viewing", "shell", "menuItem", "Viewing",
          "Locks the document against accidental edits so it can be read without modifying content.",
          parent="shell.tabrow.editingMode", order=2, bounds=(1753, 187, 150, 55), control_type_val="galleryItem",
          baseline_missing=True),
        R("shell.tabrow.share", "shell", "control", "Share",
          "Opens the sharing menu to invite collaborators, copy a sharing link or manage access permissions.",
          parent="shell.region.tabrow", order=4, bounds=(1839, 48, 69, 30), control_type_val="menu",
          keytip_val="ZS", baseline_missing=True),
        R("shell.tabrow.share.share", "shell", "menuItem", "Share...",
          "Opens the Share dialog to send the document or invite people to collaborate.",
          parent="shell.tabrow.share", order=0, bounds=(1718, 80, 188, 28), control_type_val="button",
          baseline_missing=True),
        R("shell.tabrow.share.copy-link", "shell", "menuItem", "Copy Link...",
          "Generates and copies a link to the document into the clipboard.",
          parent="shell.tabrow.share", order=1, bounds=(1718, 108, 188, 28), control_type_val="button",
          baseline_missing=True),
        R("shell.tabrow.share.manage-access", "shell", "menuItem", "Manage Access...",
          "Opens the permissions view to review or revoke who can view or edit the document.",
          parent="shell.tabrow.share", order=2, bounds=(1718, 136, 188, 28), control_type_val="button",
          baseline_missing=True),

        # 5. Ribbon display options (shell.ribbonDisplay.*)
        R("shell.ribbonDisplay.button", "shell", "control", "Ribbon Display Options",
          "Opens the menu at the bottom-right corner of the lower ribbon to control ribbon visibility and Quick Access Toolbar visibility.",
          parent="shell.region.ribbon", order=0, bounds=(1888, 154, 20, 20), control_type_val="menu",
          baseline_missing=True),
        R("shell.ribbonDisplay.full-screen-mode", "shell", "menuItem", "Full-screen mode",
          "Hides both the ribbon and the tab row to maximise document space, revealing them temporarily when the top of the window is clicked.",
          parent="shell.ribbonDisplay.button", order=0, bounds=(1712, 205, 202, 28), control_type_val="button",
          baseline_missing=True),
        R("shell.ribbonDisplay.show-tabs-only", "shell", "menuItem", "Show tabs only",
          "Collapses the lower ribbon so only the tab row stays visible, opening a tab's commands as a popup when clicked.",
          parent="shell.ribbonDisplay.button", order=1, bounds=(1712, 233, 202, 28), control_type_val="button",
          baseline_missing=True),
        R("shell.ribbonDisplay.always-show-ribbon", "shell", "menuItem", "Always show Ribbon",
          "Pins both the tab row and the full lower ribbon open above the document workspace.",
          parent="shell.ribbonDisplay.button", order=2, bounds=(1712, 261, 202, 28), control_type_val="button",
          baseline_missing=True),
        R("shell.ribbonDisplay.hide-quick-access-toolbar", "shell", "menuItem", "Hide Quick Access Toolbar",
          "Toggles visibility of the Quick Access Toolbar (reading Show Quick Access Toolbar when the toolbar is currently hidden).",
          parent="shell.ribbonDisplay.button", order=3, bounds=(1712, 292, 202, 28), control_type_val="button",
          baseline_missing=True),

        # 6. Search box and flyout categories (shell.search.*)
        R("shell.search.input", "shell", "control", "Search Input",
          "Accepts text queries (Alt+Q) to search commands, document text, help topics and connected files.",
          parent="shell.titlebar.search", order=0, bounds=(825, 16, 293, 18), control_type_val="editBox",
          uia_id="TellMeTextBoxAutomationId", keytip_val="Q", baseline_missing=True),
        R("shell.search.voice", "shell", "control", "Voice Search",
          "Starts microphone dictation into the search box to find commands or content by voice.",
          parent="shell.titlebar.search", order=1, bounds=(1121, 16, 18, 18), control_type_val="button",
          keytip_val="Q", baseline_missing=True),
        R("shell.search.flyout", "shell", "region", "Search Flyout",
          "Displays categorised command, document, people, file and help results beneath the title bar search box.",
          parent="shell.titlebar.search", order=2, bounds=(784, 40, 368, 339)),
        R("shell.search.recentActions", "shell", "group", "Recently Used Actions",
          "Lists the commands most recently invoked from the search box for one-click reuse.",
          parent="shell.search.flyout", order=0, bounds=(786, 42, 364, 67), baseline_missing=True),
        R("shell.search.suggestedActions", "shell", "group", "Suggested Actions",
          "Lists contextually relevant commands when the search box is first opened before typing a query.",
          parent="shell.search.flyout", order=1, bounds=(786, 109, 364, 137), baseline_missing=True),
        R("shell.search.suggestedActions.spelling-and-grammar", "shell", "menuItem", "Spelling and Grammar",
          "Runs the spelling and grammar checker on the active document from the default Suggested Actions list.",
          parent="shell.search.suggestedActions", order=0, bounds=(786, 144, 364, 34),
          control_type_val="galleryItem", baseline_missing=True),
        R("shell.search.suggestedActions.word-count", "shell", "menuItem", "Word Count",
          "Opens the Word Count statistics dialog from the default Suggested Actions list.",
          parent="shell.search.suggestedActions", order=1, bounds=(786, 178, 364, 34),
          control_type_val="galleryItem", baseline_missing=True),
        R("shell.search.suggestedActions.print", "shell", "menuItem", "Print",
          "Opens the Backstage Print page from the default Suggested Actions list.",
          parent="shell.search.suggestedActions", order=2, bounds=(786, 212, 364, 34),
          control_type_val="galleryItem", baseline_missing=True),
        R("shell.search.people", "shell", "group", "People",
          "Lists collaborators and contacts matching the search query without exposing personal identities in the static inventory.",
          parent="shell.search.flyout", order=2, bounds=(786, 246, 364, 131), baseline_missing=True),
        R("shell.search.actions", "shell", "group", "Actions",
          "Lists matching application commands and menus with direct execution and nested submenus as the user types.",
          parent="shell.search.flyout", order=3, bounds=(786, 42, 364, 169), baseline_missing=True),
        R("shell.search.findInDocument", "shell", "group", "Find in Document",
          "Searches the active document's text for the typed query and jumps to matching occurrences.",
          parent="shell.search.flyout", order=4, bounds=(786, 211, 364, 84), baseline_missing=True),
        R("shell.search.files", "shell", "group", "Files",
          "Lists recent and cloud documents whose titles or contents match the search query.",
          parent="shell.search.flyout", order=5, bounds=(786, 295, 364, 68), baseline_missing=True),
        R("shell.search.help", "shell", "group", "Help",
          "Lists documentation and help articles matching the search query.",
          parent="shell.search.flyout", order=6, bounds=(786, 363, 364, 68), baseline_missing=True),

        # 7. KeyTips layer (shell.keytips.*)
        R("shell.keytips.layer", "shell", "region", "KeyTips Layer",
          "Overlays alphanumeric keyboard access badges across the title bar and ribbon tab row when Alt or F10 is pressed and released.",
          parent="shell.region.titlebar", order=10, bounds=(0, 0, 1920, 78)),
        R("shell.keytips.autosave", "shell", "control", "AutoSave KeyTip",
          "Triggers the AutoSave toggle on the Quick Access Toolbar when 1 is pressed in KeyTip mode.",
          parent="shell.keytips.layer", order=0, bounds=(42, 9, 118, 29), control_type_val="label",
          keytip_val="1", baseline_missing=True),
        R("shell.keytips.save", "shell", "control", "Save KeyTip",
          "Triggers the Save command on the Quick Access Toolbar when 2 is pressed in KeyTip mode.",
          parent="shell.keytips.layer", order=1, bounds=(161, 9, 28, 29), control_type_val="label",
          keytip_val="2", baseline_missing=True),
        R("shell.keytips.undo", "shell", "control", "Undo KeyTip",
          "Triggers the Undo command on the Quick Access Toolbar when 3 is pressed in KeyTip mode.",
          parent="shell.keytips.layer", order=2, bounds=(190, 9, 38, 29), control_type_val="label",
          keytip_val="3", baseline_missing=True),
        R("shell.keytips.redo", "shell", "control", "Redo KeyTip",
          "Triggers the Repeat or Redo command on the Quick Access Toolbar when 4 is pressed in KeyTip mode.",
          parent="shell.keytips.layer", order=3, bounds=(229, 9, 28, 29), control_type_val="label",
          keytip_val="4", baseline_missing=True),
        R("shell.keytips.documentTitle", "shell", "control", "Document Title KeyTip",
          "Opens the document title and file location flyout when B is pressed in KeyTip mode.",
          parent="shell.keytips.layer", order=4, bounds=(287, 0, 134, 48), control_type_val="label",
          keytip_val="B", baseline_missing=True),
        R("shell.keytips.search", "shell", "control", "Search KeyTip",
          "Focuses the title bar search box when Q is pressed in KeyTip mode.",
          parent="shell.keytips.layer", order=5, bounds=(784, 8, 368, 32), control_type_val="label",
          keytip_val="Q", baseline_missing=True),
        R("shell.keytips.account", "shell", "control", "Account KeyTip",
          "Opens the Account flyout when Z then P is pressed in KeyTip mode.",
          parent="shell.keytips.layer", order=6, bounds=(1726, 0, 50, 48), control_type_val="label",
          keytip_val="ZP", baseline_missing=True),
        R("shell.keytips.file", "shell", "control", "File KeyTip",
          "Opens the Backstage view when F is pressed in KeyTip mode.",
          parent="shell.keytips.layer", order=7, bounds=(4, 48, 54, 30), control_type_val="label",
          keytip_val="F", baseline_missing=True),
        R("shell.keytips.comments", "shell", "control", "Comments KeyTip",
          "Toggles the Comments pane when Z then C is pressed in KeyTip mode.",
          parent="shell.keytips.layer", order=8, bounds=(1655, 51, 88, 24), control_type_val="label",
          keytip_val="ZC", baseline_missing=True),
        R("shell.keytips.editingMode", "shell", "control", "Editing Mode KeyTip",
          "Opens the Editing, Reviewing and Viewing mode menu when Z then M is pressed in KeyTip mode.",
          parent="shell.keytips.layer", order=9, bounds=(1751, 51, 80, 24), control_type_val="label",
          keytip_val="ZM", baseline_missing=True),
        R("shell.keytips.share", "shell", "control", "Share KeyTip",
          "Opens the Share menu when Z then S is pressed in KeyTip mode.",
          parent="shell.keytips.layer", order=10, bounds=(1839, 48, 69, 30), control_type_val="label",
          keytip_val="ZS", baseline_missing=True),

        # 8. Backstage frame (shell.backstage.*)
        R("shell.backstage.frame", "shell", "region", "Backstage Frame",
          "Replaces the ribbon and document workspace with the full-window File Backstage view when the File tab is activated.",
          order=7, bounds=(0, 0, 1920, 1032), uia_id="BackstageView"),
        R("shell.backstage.titlebar", "shell", "region", "Backstage Title Bar",
          "Spans the top 48 pixels of the Backstage view, keeping the document title and window caption buttons accessible.",
          parent="shell.backstage.frame", order=0, bounds=(42, 0, 939, 48)),
        R("shell.backstage.navBar", "shell", "region", "Backstage Navigation Bar",
          "Spans a 160-pixel vertical rail on the left side of the Backstage view, hosting the Back button and page navigation tabs.",
          parent="shell.backstage.frame", order=1, bounds=(0, 48, 160, 984), uia_id="OutSpaceNavBar"),
        R("shell.backstage.navList", "shell", "control", "File Navigation List",
          "Lists the Backstage pages (Home, New, Open, Info, Save, Print, Share, Export, Transform, Close, Account, Feedback, Options) in the left rail.",
          parent="shell.backstage.navBar", order=0, bounds=(0, 48, 160, 984), control_type_val="listBox",
          uia_id="NavBarMenu", baseline_missing=True),
        R("shell.backstage.back", "shell", "control", "Back",
          "Closes the Backstage view and returns focus to the active document and ribbon (also triggered by Escape).",
          parent="shell.backstage.navBar", order=1, bounds=(0, 48, 160, 45), control_type_val="button",
          uia_id="FileTabButton", keytip_val="B", baseline_missing=True),
        R("shell.backstage.contentPane", "shell", "region", "Backstage Content Area",
          "Occupies the 1760-pixel area to the right of the Backstage navigation rail, rendering the selected Backstage page.",
          parent="shell.backstage.frame", order=2, bounds=(160, 48, 1760, 984), uia_id="BackstageView"),

        # 9. Shared status bar frame (shell.statusbar.*)
        R("shell.statusbar.bar", "shell", "region", "Status Bar Frame",
          "Hosts the status bar controls across the bottom 22-pixel strip of the window frame.",
          parent="shell.region.statusbar", order=0, bounds=(0, 1010, 1920, 22)),
        R("shell.statusbar.leftZone", "shell", "region", "Status Bar Left Zone",
          "Hosts document-state indicators (page number, word count, proofing state, macro recording, accessibility status) aligned to the left edge.",
          parent="shell.statusbar.bar", order=0, bounds=(0, 1010, 1482, 22)),
        R("shell.statusbar.rightZone", "shell", "region", "Status Bar Right Zone",
          "Hosts display settings, view switchers and zoom controls aligned to the right edge of the status bar.",
          parent="shell.statusbar.bar", order=1, bounds=(1482, 1010, 438, 22)),
        R("shell.statusbar.displaySettings", "shell", "control", "Display Settings",
          "Opens display and multi-monitor rendering options from the right zone of the status bar when present.",
          parent="shell.statusbar.rightZone", order=0, bounds=(1482, 1011, 82, 21), control_type_val="button",
          baseline_missing=True),
        R("shell.statusbar.viewSwitcher", "shell", "region", "View Switcher",
          "Holds the quick view-mode toggle buttons (such as Read Mode, Print Layout and Web Layout) on the right side of the status bar.",
          parent="shell.statusbar.rightZone", order=1, bounds=(1620, 1011, 120, 21)),
        R("shell.statusbar.zoomOut", "shell", "control", "Zoom Out",
          "Decreases the active document zoom level in 10 percent steps.",
          parent="shell.statusbar.rightZone", order=2, bounds=(1741, 1011, 18, 21), control_type_val="button",
          baseline_missing=True),
        R("shell.statusbar.zoomSlider", "shell", "control", "Zoom",
          "Drags the document magnification continuously between the minimum and maximum zoom percentages.",
          parent="shell.statusbar.rightZone", order=3, bounds=(1759, 1011, 100, 21), control_type_val="slider",
          baseline_missing=True),
        R("shell.statusbar.zoomIn", "shell", "control", "Zoom In",
          "Increases the active document zoom level in 10 percent steps.",
          parent="shell.statusbar.rightZone", order=4, bounds=(1859, 1011, 18, 21), control_type_val="button",
          baseline_missing=True),
        R("shell.statusbar.zoomPercent", "shell", "control", "Zoom 100%",
          "Displays the current zoom percentage and opens the Zoom dialog when clicked.",
          parent="shell.statusbar.rightZone", order=5, bounds=(1877, 1011, 43, 21), control_type_val="button",
          baseline_missing=True),
        R("shell.statusbar.customizeMenu", "shell", "contextMenu", "Customize Status Bar",
          "Opens on right-clicking the status bar to toggle which indicators, aggregates, view buttons and zoom controls are shown.",
          parent="shell.statusbar.bar", order=2, bounds=(1482, 400, 320, 610)),

        # 10. Per-app overrides: Excel (excel.shell.*)
        R("excel.shell.titlebar.caption", "excel", "control", "Book1 - Excel",
          "Displays the active workbook name and Excel application title across the title bar caption area.",
          parent="shell.region.titlebar", order=4, bounds=(287, 0, 497, 48), control_type_val="label",
          baseline_missing=True),
        R("excel.shell.qat.redo", "excel", "control", "Redo",
          "Redoes the last undone workbook edit or opens the redo history list as a split button on Excel's Quick Access Toolbar.",
          parent="shell.titlebar.qat", order=3, bounds=(229, 9, 38, 29), control_type_val="splitButton",
          id_mso="Redo", uia_id="Redo", keytip_val="4"),
        R("excel.shell.region.tabrow", "excel", "region", "Excel Ribbon Tab Row",
          "Spans the 30-pixel tab row in Excel, hosting File, Ribbon Tabs, Comments and Share while omitting Word's Editing mode drop-down.",
          order=1, bounds=(0, 48, 1920, 30)),
        R("excel.shell.tabrow.file", "excel", "control", "File Tab",
          "Opens the Excel Backstage view for workbook management, printing, sharing and options.",
          parent="excel.shell.region.tabrow", order=0, bounds=(4, 48, 54, 30), control_type_val="button",
          uia_id="FileTabButton", keytip_val="F", baseline_missing=True),
        R("excel.shell.tabrow.tabs", "excel", "region", "Ribbon Tabs",
          "Contains Excel's core and contextual ribbon tabs along the tab row.",
          parent="excel.shell.region.tabrow", order=1, bounds=(58, 48, 1850, 30)),
        R("excel.shell.tabrow.comments", "excel", "control", "Comments",
          "Toggles the workbook Comments pane on the right side of the tab row.",
          parent="excel.shell.region.tabrow", order=2, bounds=(1743, 51, 88, 24), control_type_val="toggleButton",
          keytip_val="ZC", baseline_missing=True),
        R("excel.shell.tabrow.share", "excel", "control", "Share",
          "Opens the workbook Share menu on the right end of Excel's tab row.",
          parent="excel.shell.region.tabrow", order=3, bounds=(1839, 48, 69, 30), control_type_val="menu",
          keytip_val="ZS", baseline_missing=True),

        # 11. Per-app overrides: PowerPoint (powerpoint.shell.*)
        R("powerpoint.shell.titlebar.qat", "powerpoint", "region", "PowerPoint Quick Access Toolbar",
          "Holds AutoSave, Save, Undo, Repeat, Start From Beginning and Customize Quick Access Toolbar in PowerPoint's title bar.",
          parent="shell.region.titlebar", order=1, bounds=(42, 0, 273, 48)),
        R("powerpoint.shell.qat.autosave", "powerpoint", "control", "AutoSave",
          "Toggles automatic cloud saving for the active presentation on PowerPoint's Quick Access Toolbar.",
          parent="powerpoint.shell.titlebar.qat", order=0, bounds=(42, 9, 118, 29), control_type_val="toggleButton",
          id_mso="AutoSaveSwitch", uia_id="AutoSaveSwitch", keytip_val="1"),
        R("powerpoint.shell.qat.save", "powerpoint", "control", "Save",
          "Saves the active presentation from PowerPoint's Quick Access Toolbar.",
          parent="powerpoint.shell.titlebar.qat", order=1, bounds=(161, 9, 28, 29), control_type_val="button",
          id_mso="FileSave", uia_id="FileSave", keytip_val="2"),
        R("powerpoint.shell.qat.undo", "powerpoint", "control", "Undo",
          "Undoes the last presentation action or opens the undo history drop-down.",
          parent="powerpoint.shell.titlebar.qat", order=2, bounds=(190, 9, 38, 29), control_type_val="splitButton",
          id_mso="Undo", keytip_val="3"),
        R("powerpoint.shell.qat.redo", "powerpoint", "control", "Repeat",
          "Repeats or redoes the last presentation action.",
          parent="powerpoint.shell.titlebar.qat", order=3, bounds=(229, 9, 28, 29), control_type_val="button",
          id_mso="RedoOrRepeat", uia_id="RedoOrRepeat", keytip_val="4"),
        R("powerpoint.shell.qat.fromBeginning", "powerpoint", "control", "Start From Beginning",
          "Starts the slide show from the first slide in the presentation (F5) directly from PowerPoint's default Quick Access Toolbar.",
          parent="powerpoint.shell.titlebar.qat", order=4, bounds=(258, 9, 28, 29), control_type_val="button",
          id_mso="SlideShowFromBeginning", uia_id="SlideShowFromBeginning", keytip_val="5"),
        R("powerpoint.shell.qat.customize", "powerpoint", "control", "Customize Quick Access Toolbar",
          "Opens the Quick Access Toolbar customisation menu in PowerPoint.",
          parent="powerpoint.shell.titlebar.qat", order=5, bounds=(287, 8, 28, 31), control_type_val="menu",
          baseline_missing=True),
        R("powerpoint.shell.titlebar.caption", "powerpoint", "control", "Presentation1 - PowerPoint",
          "Displays the active presentation name and PowerPoint application title in the title bar.",
          parent="shell.region.titlebar", order=4, bounds=(316, 0, 468, 48), control_type_val="label",
          baseline_missing=True),
        R("powerpoint.shell.region.tabrow", "powerpoint", "region", "PowerPoint Ribbon Tab Row",
          "Spans the 30-pixel tab row in PowerPoint, hosting File, Ribbon Tabs, Comments, Present in Teams and Share.",
          order=1, bounds=(0, 48, 1920, 30)),
        R("powerpoint.shell.tabrow.file", "powerpoint", "control", "File Tab",
          "Opens the PowerPoint Backstage view.",
          parent="powerpoint.shell.region.tabrow", order=0, bounds=(4, 48, 54, 30), control_type_val="button",
          uia_id="FileTabButton", keytip_val="F", baseline_missing=True),
        R("powerpoint.shell.tabrow.tabs", "powerpoint", "region", "Ribbon Tabs",
          "Contains PowerPoint's core and contextual ribbon tabs.",
          parent="powerpoint.shell.region.tabrow", order=1, bounds=(58, 48, 1850, 30)),
        R("powerpoint.shell.tabrow.comments", "powerpoint", "control", "Comments",
          "Toggles the presentation Comments pane from PowerPoint's tab row.",
          parent="powerpoint.shell.region.tabrow", order=2, bounds=(1611, 51, 88, 24), control_type_val="toggleButton",
          keytip_val="ZC", baseline_missing=True),
        R("powerpoint.shell.tabrow.presentInTeams", "powerpoint", "control", "Present in Teams",
          "Shares the active presentation directly into a live Microsoft Teams meeting from PowerPoint's tab row.",
          parent="powerpoint.shell.region.tabrow", order=3, bounds=(1707, 51, 124, 24), control_type_val="toggleButton",
          keytip_val="ZP", baseline_missing=True),
        R("powerpoint.shell.tabrow.share", "powerpoint", "control", "Share",
          "Opens the presentation Share menu on the right end of PowerPoint's tab row.",
          parent="powerpoint.shell.region.tabrow", order=4, bounds=(1839, 48, 69, 30), control_type_val="menu",
          keytip_val="ZS", baseline_missing=True),

        # 12. Per-app overrides: Visio (visio.shell.*)
        R("visio.shell.region.titlebar", "visio", "region", "Visio Title Bar",
          "Spans the top 48 pixels of Visio's window frame without an AutoSave switch.",
          order=0, bounds=(0, 0, 1920, 48)),
        R("visio.shell.titlebar.systemMenu", "visio", "control", "System",
          "Opens Visio's window system menu.",
          parent="visio.shell.region.titlebar", order=0, bounds=(0, 0, 22, 22), control_type_val="menu",
          uia_id="MenuBar", keytip_val="Space", baseline_missing=True),
        R("visio.shell.titlebar.qat", "visio", "region", "Visio Quick Access Toolbar",
          "Holds Save, Undo, Redo and Customize Quick Access Toolbar in Visio's title bar without AutoSave.",
          parent="visio.shell.region.titlebar", order=1, bounds=(42, 0, 124, 48)),
        R("visio.shell.qat.save", "visio", "control", "Save",
          "Saves the active Visio drawing (Ctrl+S).",
          parent="visio.shell.titlebar.qat", order=0, bounds=(42, 9, 28, 29), control_type_val="button",
          id_mso="FileSave", uia_id="FileSave", keytip_val="1"),
        R("visio.shell.qat.undo", "visio", "control", "Undo",
          "Undoes the last drawing action or opens the undo history drop-down in Visio.",
          parent="visio.shell.titlebar.qat", order=1, bounds=(71, 9, 37, 29), control_type_val="splitButton",
          id_mso="Undo", keytip_val="2"),
        R("visio.shell.qat.redo", "visio", "control", "Redo",
          "Redoes the last undone drawing action in Visio.",
          parent="visio.shell.titlebar.qat", order=2, bounds=(109, 9, 28, 29), control_type_val="button",
          id_mso="RedoOrRepeat", uia_id="RedoOrRepeat", keytip_val="3"),
        R("visio.shell.qat.customize", "visio", "control", "Customize Quick Access Toolbar",
          "Opens the Quick Access Toolbar customisation menu in Visio.",
          parent="visio.shell.titlebar.qat", order=3, bounds=(138, 9, 28, 31), control_type_val="menu",
          baseline_missing=True),
        R("visio.shell.titlebar.caption", "visio", "control", "Drawing1 - Visio Professional",
          "Displays the active drawing name and Visio product title across the title bar.",
          parent="visio.shell.region.titlebar", order=2, bounds=(167, 0, 617, 48), control_type_val="label",
          baseline_missing=True),
        R("visio.shell.titlebar.search", "visio", "control", "Search",
          "Focuses Visio's title bar search box (Alt+Q).",
          parent="visio.shell.region.titlebar", order=3, bounds=(784, 8, 368, 32), control_type_val="menu",
          uia_id="TellMeControlAnchor", keytip_val="Q", baseline_missing=True),
        R("visio.shell.titlebar.account", "visio", "control", "Account",
          "Opens the Account flyout in Visio's title bar.",
          parent="visio.shell.region.titlebar", order=4, bounds=(1726, 0, 50, 48), control_type_val="menu",
          uia_id="MeControlWidget", keytip_val="ZP", baseline_missing=True),
        R("visio.shell.titlebar.minimize", "visio", "control", "Minimize",
          "Minimises the Visio window.",
          parent="visio.shell.region.titlebar", order=5, bounds=(1776, 0, 48, 48), control_type_val="button",
          baseline_missing=True),
        R("visio.shell.titlebar.maximize", "visio", "control", "Restore Down",
          "Restores or maximises the Visio window.",
          parent="visio.shell.region.titlebar", order=6, bounds=(1824, 0, 48, 48), control_type_val="button",
          baseline_missing=True),
        R("visio.shell.titlebar.close", "visio", "control", "Close",
          "Closes the Visio application window.",
          parent="visio.shell.region.titlebar", order=7, bounds=(1872, 0, 48, 48), control_type_val="button",
          baseline_missing=True),
        R("visio.shell.region.tabrow", "visio", "region", "Visio Ribbon Tab Row",
          "Spans the 30-pixel tab row in Visio, hosting File, Ribbon Tabs, Comments, a direct Share... button and an MDI Close Document button.",
          order=1, bounds=(0, 48, 1920, 30)),
        R("visio.shell.tabrow.file", "visio", "control", "File Tab",
          "Opens the Visio Backstage view.",
          parent="visio.shell.region.tabrow", order=0, bounds=(4, 48, 54, 30), control_type_val="button",
          uia_id="FileTabButton", keytip_val="F", baseline_missing=True),
        R("visio.shell.tabrow.tabs", "visio", "region", "Ribbon Tabs",
          "Contains Visio's core and contextual ribbon tabs.",
          parent="visio.shell.region.tabrow", order=1, bounds=(58, 48, 1804, 30)),
        R("visio.shell.tabrow.comments", "visio", "control", "Comments",
          "Toggles the diagram Comments pane in Visio.",
          parent="visio.shell.region.tabrow", order=2, bounds=(1708, 51, 88, 24), control_type_val="toggleButton",
          keytip_val="ZC", baseline_missing=True),
        R("visio.shell.tabrow.share", "visio", "control", "Share...",
          "Opens the Share dialog directly as a push button on Visio's tab row.",
          parent="visio.shell.region.tabrow", order=3, bounds=(1804, 51, 58, 24), control_type_val="button",
          keytip_val="ZS", baseline_missing=True),
        R("visio.shell.tabrow.closeDocument", "visio", "control", "Close",
          "Closes the active MDI drawing document window on the right end of Visio's tab row without exiting Visio.",
          parent="visio.shell.region.tabrow", order=4, bounds=(1874, 48, 46, 30), control_type_val="button",
          baseline_missing=True),

        # 13. Per-app overrides: Project (project.shell.*, live-measured from WINPROJ.EXE JWinproj-WhimperMainClass)
        R("project.shell.region.titlebar", "project", "region", "Project Title Bar",
          "Spans the top 48 pixels of Project's window frame without AutoSave and without the title bar search box (which sits on the tab row in Project).",
          order=0, bounds=(0, 0, 1920, 48)),
        R("project.shell.titlebar.systemMenu", "project", "control", "System",
          "Opens Project's window system menu.",
          parent="project.shell.region.titlebar", order=0, bounds=(0, 0, 22, 22), control_type_val="menu",
          uia_id="MenuBar", keytip_val="Space", baseline_missing=True),
        R("project.shell.titlebar.qat", "project", "region", "Project Quick Access Toolbar",
          "Holds Save, Undo, Redo and Customize Quick Access Toolbar on the left side of Project's title bar.",
          parent="project.shell.region.titlebar", order=1, bounds=(42, 0, 133, 48)),
        R("project.shell.qat.save", "project", "control", "Save",
          "Saves the active project schedule from Project's Quick Access Toolbar.",
          parent="project.shell.titlebar.qat", order=0, bounds=(42, 9, 28, 29), control_type_val="button",
          id_mso="FileSave", uia_id="FileSave", keytip_val="1"),
        R("project.shell.qat.undo", "project", "control", "Undo",
          "Undoes the last schedule edit or opens the undo history drop-down in Project.",
          parent="project.shell.titlebar.qat", order=1, bounds=(71, 9, 37, 29), control_type_val="splitButton",
          id_mso="Undo", keytip_val="2"),
        R("project.shell.qat.redo", "project", "control", "Redo",
          "Redoes the last undone schedule edit as a split button on Project's Quick Access Toolbar.",
          parent="project.shell.titlebar.qat", order=2, bounds=(109, 9, 37, 29), control_type_val="splitButton",
          id_mso="Redo", keytip_val="3"),
        R("project.shell.qat.customize", "project", "control", "Customize Quick Access Toolbar",
          "Opens the Quick Access Toolbar customisation menu in Project.",
          parent="project.shell.titlebar.qat", order=3, bounds=(147, 9, 28, 31), control_type_val="menu",
          baseline_missing=True),
        R("project.shell.titlebar.caption", "project", "control", "Project Professional",
          "Displays the active project name and Project Professional title across the title bar.",
          parent="project.shell.region.titlebar", order=2, bounds=(176, 0, 1550, 48), control_type_val="label",
          baseline_missing=True),
        R("project.shell.titlebar.account", "project", "control", "Account",
          "Opens the Account flyout in Project's title bar.",
          parent="project.shell.region.titlebar", order=3, bounds=(1726, 0, 50, 48), control_type_val="menu",
          uia_id="MeControlWidget", keytip_val="ZP", baseline_missing=True),
        R("project.shell.titlebar.minimize", "project", "control", "Minimize",
          "Minimises the Project window.",
          parent="project.shell.region.titlebar", order=4, bounds=(1776, 0, 48, 48), control_type_val="button",
          baseline_missing=True),
        R("project.shell.titlebar.maximize", "project", "control", "Restore Down",
          "Restores or maximises the Project window.",
          parent="project.shell.region.titlebar", order=5, bounds=(1824, 0, 48, 48), control_type_val="button",
          baseline_missing=True),
        R("project.shell.titlebar.close", "project", "control", "Close",
          "Closes the Project application window.",
          parent="project.shell.region.titlebar", order=6, bounds=(1872, 0, 48, 48), control_type_val="button",
          baseline_missing=True),
        R("project.shell.region.tabrow", "project", "region", "Project Ribbon Tab Row",
          "Spans the 30-pixel tab row in Project, hosting File, Ribbon Tabs and the inline Tell Me search box after the Help tab.",
          order=1, bounds=(0, 48, 1920, 30)),
        R("project.shell.tabrow.file", "project", "control", "File Tab",
          "Opens the Project Backstage view.",
          parent="project.shell.region.tabrow", order=0, bounds=(4, 48, 54, 30), control_type_val="button",
          uia_id="FileTabButton", keytip_val="F", baseline_missing=True),
        R("project.shell.tabrow.tabs", "project", "region", "Ribbon Tabs",
          "Contains Project's core and contextual ribbon tabs (Task, Resource, Report, Project, View, Help, Task Form).",
          parent="project.shell.region.tabrow", order=1, bounds=(58, 48, 1862, 30)),
        R("project.shell.tabrow.search", "project", "control", "Tell me what you want to do",
          "Focuses the Tell Me command search box placed inline on Project's tab row immediately to the right of the Help tab.",
          parent="project.shell.region.tabrow", order=2, bounds=(387, 48, 329, 30), control_type_val="menu",
          uia_id="TellMeControlAnchor", keytip_val="Q", baseline_missing=True),

        # 14. Per-app overrides: classic Outlook explorer window (outlook.explorer.shell.*, baseline-backed; live UIA in §15)
        R("outlook.explorer.shell.region.titlebar", "outlook", "region", "Outlook Explorer Title Bar",
          "Hosts the system menu, explorer Quick Access Toolbar, module caption, search box, account widget and window caption buttons in classic Outlook's main window.",
          order=0, source_override=base_src),
        R("outlook.explorer.shell.titlebar.qat", "outlook", "region", "Outlook Explorer Quick Access Toolbar",
          "Holds Send/Receive All Folders, Undo, Simplified Ribbon toggle, Minimize the Ribbon and Find a Contact in classic Outlook's explorer window.",
          parent="outlook.explorer.shell.region.titlebar", order=1, source_override=base_src),
        R("outlook.explorer.shell.qat.sendReceiveAll", "outlook", "control", "Send/Receive All Folders",
          "Synchronises all mail, calendar and contact folders with connected mail servers from Outlook's explorer Quick Access Toolbar.",
          parent="outlook.explorer.shell.titlebar.qat", order=0, control_type_val="button",
          id_mso="SendReceiveAll", source_override=base_src),
        R("outlook.explorer.shell.qat.undo", "outlook", "control", "Undo",
          "Reverses the last folder or item action in Outlook's explorer window.",
          parent="outlook.explorer.shell.titlebar.qat", order=1, control_type_val="splitButton",
          id_mso="Undo", source_override=base_src),
        R("outlook.explorer.shell.qat.singleLineRibbonToggle", "outlook", "control", "Simplified Ribbon",
          "Toggles the explorer ribbon between the three-row Classic layout and the single-line Simplified layout.",
          parent="outlook.explorer.shell.titlebar.qat", order=2, control_type_val="toggleButton",
          id_mso="SingleLineRibbonToggle", source_override=base_src),
        R("outlook.explorer.shell.qat.minimizeRibbon", "outlook", "control", "Minimize the Ribbon",
          "Collapses or expands the ribbon in Outlook's explorer window.",
          parent="outlook.explorer.shell.titlebar.qat", order=3, control_type_val="toggleButton",
          id_mso="MinimizeRibbon", source_override=base_src),
        R("outlook.explorer.shell.qat.findContactCombo", "outlook", "control", "Find a Contact",
          "Searches the address book for a contact directly from Outlook's explorer Quick Access Toolbar.",
          parent="outlook.explorer.shell.titlebar.qat", order=4, control_type_val="comboBox",
          id_mso="FindContactCombo", source_override=base_src),

        # 15. Per-app overrides: classic Outlook item/compose window (outlook.compose.shell.*, baseline-backed; live UIA in §15)
        R("outlook.compose.shell.region.titlebar", "outlook", "region", "Outlook Item Window Title Bar",
          "Hosts the system menu, item-window Quick Access Toolbar, item subject caption, search box and caption buttons in classic Outlook inspector windows.",
          order=0, source_override=base_src),
        R("outlook.compose.shell.titlebar.qat", "outlook", "region", "Outlook Item Window Quick Access Toolbar",
          "Holds Save, Undo, Redo, Simplified Ribbon toggle and Minimize the Ribbon in classic Outlook item windows.",
          parent="outlook.compose.shell.region.titlebar", order=1, source_override=base_src),
        R("outlook.compose.shell.qat.save", "outlook", "control", "Save",
          "Saves the open mail draft, appointment, contact or task in Outlook's item window.",
          parent="outlook.compose.shell.titlebar.qat", order=0, control_type_val="button",
          id_mso="FileSave", source_override=base_src),
        R("outlook.compose.shell.qat.undo", "outlook", "control", "Undo",
          "Undoes the last editing action inside the Outlook item window.",
          parent="outlook.compose.shell.titlebar.qat", order=1, control_type_val="splitButton",
          id_mso="Undo", source_override=base_src),
        R("outlook.compose.shell.qat.redo", "outlook", "control", "Redo",
          "Redoes the last undone editing action inside the Outlook item window.",
          parent="outlook.compose.shell.titlebar.qat", order=2, control_type_val="splitButton",
          id_mso="RedoOrRepeat", source_override=base_src),
        R("outlook.compose.shell.qat.singleLineRibbonToggle", "outlook", "control", "Simplified Ribbon",
          "Toggles the item window's ribbon between the Classic layout and the single-line Simplified layout.",
          parent="outlook.compose.shell.titlebar.qat", order=3, control_type_val="toggleButton",
          id_mso="SingleLineRibbonToggle", source_override=base_src),
        R("outlook.compose.shell.qat.minimizeRibbon", "outlook", "control", "Minimize the Ribbon",
          "Collapses or expands the ribbon inside the Outlook item window.",
          parent="outlook.compose.shell.titlebar.qat", order=4, control_type_val="toggleButton",
          id_mso="MinimizeRibbon", source_override=base_src),
    ]
    validate_shell_chrome(records)
    return records


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
        try:
            expected_build = reference_build()
            if installed_build() != expected_build:
                raise Refused(f"the installed build {installed_build()} is not the reference {expected_build}")
            records = build_shell_chrome_records(expected_build)
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
