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
area. ScreenTip text (the UI Automation help text and full description) is never read. A tab without an identifier,
or a group with no control the baseline knows, may be an add-in or may be new in this build: it is not written to
the inventory but to build/capture-ui/<app>-unverified.json, marked `baselineMissing`, and listed for review. The run
reports which of the baseline's core tabs the window did not show, and that File (Backstage) is not a ribbon tab.
Combo box lists (fonts, sizes) are system and document data, so they are not expanded; the run counts them.
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
                        same_build)

PROFILE = "fhd-100"
PROFILE_SIZE, PROFILE_DPI, UI_LANGUAGE = (1920, 1080), 96, 1033  # en-US
UNVERIFIED = INVENTORY.parents[1] / "build" / "capture-ui"
LARGE_HEIGHT = 40  # pixels at 100 percent: large ribbon controls are about 66, small ones about 22


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
        self.elements = {}  # record id -> the element it was read from, for expansion

    def drop_geometry(self, why):
        """Geometry from a window that moved is no longer under the profile: none is kept for this capture."""
        self.origin = None
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
    parts = list(element.children()) if element.control_type == "SplitButton" else []
    candidates += [p.automation_id[:-len("_Dropdown")] for p in parts if p.automation_id.endswith("_Dropdown")]
    candidates += [p.automation_id for p in parts]
    return next((c for c in candidates if c and c in identifiers), None)


def control_type(element):
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
    (a tab without an identifier, a group with no known control) goes to ctx.unverified, marked baselineMissing."""
    tab_unverified = not tab.automation_id
    tab_id = ctx.ids.make(ctx.app, tab.name, tab.automation_id)
    tab_rec = ctx.base(tab_id, "contextualTab" if contextual else "tab", tab.name, order, tab,
                       idMso=tab.automation_id if tab.automation_id in ctx.identifiers else None,
                       baselineMissing=True if tab_unverified else None)
    records, aside = ([], [tab_rec]) if tab_unverified else ([tab_rec], [])
    if tab_unverified:
        ctx.skipped.append(f"tab {tab.name!r}: no identifier, so its provenance is unverified")
    containers = [c for c in lower.children() if c.control_type == "Group"]
    groups = [g for c in containers for g in c.children() if g.control_type == "Group"]
    for g_order, group in enumerate(groups):
        members = [(el, frame) for el, frame in controls_of(group) if control_type(el)]
        ids = [identifier(el, ctx.identifiers) for el, _ in members]
        unverified = tab_unverified or (members and not any(ids))
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
                                   baselineMissing=True if unverified else None))
    ctx.unverified += aside
    return records


def expand_items(control_rec, element, popup_items, ctx):
    """Menu or gallery items, in order, as records under their control."""
    out = []
    for order, item in enumerate(popup_items):
        if not item.name:
            continue
        out.append(ctx.base(ctx.ids.make(control_rec["id"], item.name, item.automation_id), "menuItem", item.name,
                            order, item,
                            parent=control_rec["id"], controlType="galleryItem" if item.control_type == "ListItem"
                            else TYPES.get(item.control_type, "button"),
                            idMso=item.automation_id if item.automation_id in ctx.identifiers else None))
    return out


def merge(existing, captured):
    """Captured records refresh `bounds`, `order` and the profile they were taken under; every other field of an
    existing record (behaviour, source and anything written by hand) is kept, and records not captured stay."""
    refreshed = ("bounds", "order", "captureProfile", "size")
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
            out_by_id[old["id"]] = kept
            continue
        rid, n = new["id"], 1
        while rid in keep or rid in out_by_id:  # a different control holds this id: give the new one its own
            n += 1
            rid = f"{new['id']}-{n}"
        mapping[new["id"]] = rid
        out_by_id[rid] = dict(new, id=rid, **({"parent": parent} if parent else {}))
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
        # Word embeds an unseen level-number placeholder (U+0001) in numbering gallery names; control characters
        # are never displayed, so they are dropped from the name.
        self.name = "".join(ch for ch in (raw.CurrentName or "") if ord(ch) >= 32)
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


class Launched:
    """An app instance this tool started, with its top-level window and its process."""

    def __init__(self, key, dispatch=None, starter=None, owner=None):
        row, exe, progid, separate = APPS[key]
        self.key, self.row, self.exe = key, row, exe
        if key == "outlook":
            raise Unsafe("Outlook is not started by the capture tool: starting it sends the Outbox; capture it "
                         "attended (D02 T01 §15)")
        import win32com.client
        self.proc, self.created, self.owned, self.started = None, [], False, None
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
        self.app = (dispatch or (win32com.client.DispatchEx if separate else win32com.client.Dispatch))(progid)
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
            self.app.Visible = True
            self.created.append(self.new_document())
            self.hwnd = Win().top(self.window_handle())
            if self.proc is None:
                self.proc = (owner or OwnProcess)(self.hwnd, exe)
        except Exception:
            self.close()
            raise

    @staticmethod
    def running(exe):
        import subprocess
        out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {exe}", "/FO", "CSV", "/NH"], capture_output=True,
                             text=True, check=True).stdout
        return any(line.upper().startswith(f'"{exe.upper()}"') for line in out.splitlines())

    def documents(self):
        return {"word": lambda: self.app.Documents, "excel": lambda: self.app.Workbooks,
                "powerpoint": lambda: self.app.Presentations, "visio": lambda: self.app.Documents,
                "project": lambda: self.app.Projects}[self.key]()

    def open_documents(self):
        return int(self.documents().Count)

    def check_alone(self):
        """The instance must still hold only the tool's own document: one the operator opened in a shared instance
        would be the one the ribbon acts on."""
        count = self.open_documents()
        if count != len(self.created):
            raise Refused(f"the {self.exe} instance now holds {count} documents, not only the tool's own; stopping "
                          "before the ribbon acts on someone else's")

    def new_document(self):
        return {"word": lambda: self.app.Documents.Add(), "excel": lambda: self.app.Workbooks.Add(),
                "powerpoint": lambda: self.app.Presentations.Add(), "visio": lambda: self.app.Documents.Add(""),
                "project": lambda: self.app.FileNew()}[self.key]()

    def window_handle(self):
        return {"word": lambda: self.app.ActiveWindow.Hwnd, "excel": lambda: self.app.Hwnd,
                "powerpoint": lambda: self.app.HWND, "visio": lambda: self.app.WindowHandle32,
                "project": lambda: self.app.ActiveWindow.Hwnd}[self.key]()

    def language(self):
        try:
            return int(self.app.LanguageSettings.LanguageID(2))  # msoLanguageIDUI
        except Exception:  # an app without LanguageSettings: the profile check reports it
            return None

    def close(self, wait=60.0):
        """Close only the documents this tool created, without saving; quit only an instance this tool started that
        holds nothing else; and confirm its process has exited."""
        if not self.owned:
            return
        others, failure = None, None  # unknown until counted: an instance whose contents are unknown is never quit
        try:
            for doc in self.created:
                if self.key == "word":
                    doc.Close(SaveChanges=0)
                elif self.key == "excel":
                    doc.Close(SaveChanges=False)
                else:
                    doc.Saved = True
                    doc.Close()
            others = self.open_documents()
        except Exception as exc:  # reported below: the instance is left running and the run refuses
            failure = f"{type(exc).__name__}: {exc}"
        finally:
            try:
                if others == 0:
                    self.app.Quit(SaveChanges=0) if self.key == "word" else self.app.Quit()
            finally:
                if others == 0:
                    # Excel and PowerPoint stay alive while a COM reference to them is held, so every one is
                    # released before waiting for the process to end.
                    import gc
                    self.created, self.document_refs, self.app = [], None, None
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


def popup_items(root, popup_roots=()):
    """The items of the menu or gallery that just opened, once their count is stable. Office exposes an open menu as
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

    last, stable = None, 0
    deadline = time.monotonic() + 4.0
    while time.monotonic() < deadline and stable < 2:
        items = attempt()
        if items is None:
            stable, last = 0, None
            time.sleep(0.4)
            continue
        stable = stable + 1 if last is not None and len(items) == len(last) and items else 0
        last = items
        time.sleep(0.4)
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
    tabs_bar = wait_for(lambda: find(root, lambda e: e.control_type == "Tab" and e.name == "Ribbon Tabs"))
    lower = wait_for(lambda: find(root, lambda e: e.name == "Lower Ribbon"))
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
    tab_elements = [t for t in tabs_bar.children() if t.control_type == "TabItem"]
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
        if not wait_for(lambda: first_group_name(uia.element(launched.hwnd)) == tab.name):
            raise Refused(f"tab {tab.name!r} did not open")
        lower = find(uia.element(launched.hwnd), lambda e: e.name == "Lower Ribbon")
        tab_records = walk_tab(tab, order, lower, ctx)
        if args.expand:
            tab_records = expand_all(tab_records, lower, ctx, launched, uia, win)
        records += tab_records
    if ctx.origin is not None and not same_geometry(state, win.state(launched.hwnd)):
        ctx.drop_geometry("the window moved or changed size during the capture")
    if ctx.origin is None:
        for rec in records:
            for key in ("bounds", "captureProfile", "size"):
                rec.pop(key, None)
    return records, problems, ctx


def same_geometry(before, after):
    return all(before[k] == after[k] for k in ("window", "origin", "dpi", "zoomed"))


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


def expand_all(records, lower, ctx, launched, uia, win):
    """Open every control that can expand (by its own pattern) once, record its items, and close it again."""
    out, combos = [], 0
    for rec in records:
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
        before = win.popups(launched.proc.pid)
        target.expand()
        try:
            time.sleep(0.3)
            opened = [h for h in win.popups(launched.proc.pid) if h not in before]
            items = popup_items(uia.element(launched.hwnd), [uia.element(h) for h in opened])
            if not items:
                ctx.notes.append(f"{rec['label']!r} opened but no item was read from it")
        finally:
            close_popup(target, lambda: [h for h in win.popups(launched.proc.pid) if h not in before]
                        or find(uia.element(launched.hwnd), lambda e: e.control_type == "Menu", depth=30) is not None,
                        rec["label"])
        out += expand_items(rec, target, items, ctx)
    if combos:
        ctx.notes.append(f"{combos} combo box list(s) on this tab not expanded (system or document data)")
    return out


def close_popup(target, still_open, label, attempts=3):
    """Collapse a menu and confirm its popup is gone. The control's own expand state is not trusted: Word reports
    some drop-downs collapsed while open and others expanded while closed, so "gone" means no popup window and no
    open menu remain. A drop-down that ignores Collapse closes when opened and collapsed again; one that stays open
    stops the capture rather than leaving it behind."""
    target.collapse()
    for _ in range(attempts):
        if wait_for(lambda: not still_open(), 1.5):
            return
        target.expand()
        time.sleep(0.4)
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


def capture_in_worker(args, launched, timeout=3600):
    """Run capture() in a child process and return its records, profile problems and notes."""
    import subprocess
    import types
    spec = {"args": vars(args), "hwnd": int(launched.hwnd), "pid": int(launched.proc.pid),
            "build": reported_build(launched.app), "language": launched.language()}
    child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker"], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    try:
        child.stdin.write(json.dumps(spec) + "\n")
        child.stdin.flush()

        def reply(text):
            child.stdin.write(json.dumps({"answer": text}) + "\n")
            child.stdin.flush()

        outcome = converse(iter(child.stdout.readline, ""), reply, launched)
        child.wait(timeout=60)
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
    if "unsafe" in outcome:
        raise Unsafe(outcome["unsafe"])
    if "refused" in outcome:
        detail = child.stderr.read().strip().splitlines()[-1:] if child.stderr else []
        raise Refused(outcome["refused"] + (f" ({detail[0]})" if detail else ""))
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


def main(argv=None, launcher=Launched, uia_factory=None, win_factory=None):
    parser = argparse.ArgumentParser(description="Capture an Office app's ribbon through UI Automation.")
    parser.add_argument("--app", required=True, choices=sorted(APPS))
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument("--tab", help="one tab, by its name as the ribbon shows it")
    which.add_argument("--all-tabs", action="store_true", help="every built-in tab the ribbon lists")
    parser.add_argument("--expand", action="store_true", help="open each menu and gallery and record its items")
    parser.add_argument("--layout", choices=("classic", "simplified"), default="classic")
    parser.add_argument("--merge", action="store_true", help="update an existing file, keeping hand-written fields")
    parser.add_argument("--out", help="output file (default design/inventory/<app>/ribbon[-simplified].json)")
    args = parser.parse_args(argv)
    out = Path(args.out) if args.out else INVENTORY / args.app / (
        "ribbon-simplified.json" if args.layout == "simplified" else "ribbon.json")
    if out.exists() and not args.merge:
        print(f"capture-ui: {out} exists; pass --merge to update it", file=sys.stderr)
        return 1
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
    if args.merge and out.exists():
        records = merge(json.loads(out.read_text(encoding="utf-8")), records)
    files = {out: render(records)}
    if ctx.unverified:
        files[UNVERIFIED / f"{args.app}-unverified.json"] = render(ctx.unverified)
    publish(files)
    for line in ctx.skipped + ctx.notes:
        print(line)
    if ctx.unverified:
        print(f"{len(ctx.unverified)} unverified records in {UNVERIFIED / (args.app + '-unverified.json')}")
    print(f"{out}: {len(records)} records" + ("; bounds recorded under " + PROFILE if not problems else
                                               "; no bounds: " + "; ".join(problems)))
    return 0


if __name__ == "__main__":
    sys.exit(worker() if sys.argv[1:] == ["--worker"] else main(sys.argv[1:]))
