#!/usr/bin/env python3
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
baseline lists it), KeyTip, order and, under the profile, bounds relative to the client area. ScreenTip text (the
UI Automation help text and full description) is never read. Tabs without an identifier and groups with no control
the baseline knows are add-ins, not Office, and are skipped and listed.
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
LARGE_HEIGHT = 40  # pixels at 100 percent: large ribbon controls are about 66, small ones about 22


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
    """Ids unique within one capture: a parent id plus the label's slug, with -2, -3 for repeats."""

    def __init__(self):
        self.taken = set()

    def make(self, parent, label):
        base, n = f"{parent}.{slug(label)}", 1
        while (f"{base}-{n}" if n > 1 else base) in self.taken:
            n += 1
        final = f"{base}-{n}" if n > 1 else base
        self.taken.add(final)
        return final


class Context:
    def __init__(self, app, build, identifiers, origin=None):
        self.app, self.build, self.identifiers = app, build, identifiers
        self.origin = origin  # client-area origin on screen, only when the capture profile holds
        self.ids, self.skipped = Ids(), []

    def base(self, rid, kind, label, order, element, parent=None, **extra):
        rec = {"id": rid, "app": self.app, "kind": kind, "label": label}
        if parent:
            rec["parent"] = parent
        rec["order"] = order
        rec.update({k: v for k, v in extra.items() if v is not None})
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
    """Records for one selected tab: the tab, its groups and their controls."""
    if not tab.automation_id:
        ctx.skipped.append(f"tab {tab.name!r}: no identifier, an add-in")
        return []
    tab_id = ctx.ids.make(ctx.app, tab.name)
    records = [ctx.base(tab_id, "contextualTab" if contextual else "tab", tab.name, order, tab,
                        idMso=tab.automation_id if tab.automation_id in ctx.identifiers else None)]
    containers = [c for c in lower.children() if c.control_type == "Group"]
    groups = [g for c in containers for g in c.children() if g.control_type == "Group"]
    for g_order, group in enumerate(groups):
        members = [(el, frame) for el, frame in controls_of(group) if control_type(el)]
        ids = [identifier(el, ctx.identifiers) for el, _ in members]
        if members and not any(ids):
            ctx.skipped.append(f"group {group.name!r} on {tab.name!r}: no control the baseline knows, an add-in")
            continue
        group_id = ctx.ids.make(tab_id, group.name)
        records.append(ctx.base(group_id, "group", group.name, g_order, group, parent=tab_id))
        for c_order, ((el, frame), idmso) in enumerate(zip(members, ids)):
            label = el.name or frame or el.automation_id or "control"
            records.append(ctx.base(ctx.ids.make(group_id, label), "control", label, c_order, el, parent=group_id,
                                    controlType=control_type(el), idMso=idmso))
    return records


def expand_items(control_rec, element, popup_items, ctx):
    """Menu or gallery items, in order, as records under their control."""
    out = []
    for order, item in enumerate(popup_items):
        if not item.name:
            continue
        out.append(ctx.base(ctx.ids.make(control_rec["id"], item.name), "menuItem", item.name, order, item,
                            parent=control_rec["id"], controlType="galleryItem" if item.control_type == "ListItem"
                            else TYPES.get(item.control_type, "button"),
                            idMso=item.automation_id if item.automation_id in ctx.identifiers else None))
    return out


def merge(existing, captured):
    """Captured records refresh `bounds`, `order` and the profile they were taken under; every other field of an
    existing record (behaviour, source and anything written by hand) is kept, and records not captured stay."""
    refreshed = ("bounds", "order", "captureProfile", "size")
    by_id = {r["id"]: r for r in captured}
    out, seen = [], set()
    for rec in existing:
        new = by_id.get(rec.get("id"))
        if new is None:
            out.append(rec)
            continue
        kept = {k: v for k, v in rec.items() if k not in refreshed}
        kept.update({k: new[k] for k in refreshed if k in new})
        out.append(kept)
        seen.add(rec["id"])
    out += [r for r in captured if r["id"] not in seen]
    return out


def render(records):
    return "[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n]\n"


# ------------------------------------------------------------------------------------------- Windows side
class Element:
    """A UI Automation element, exposing only what a capture records. Help text is deliberately absent."""

    def __init__(self, uia, raw):
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
    """The few Win32 calls a capture needs: monitors, window placement, process windows and pixels."""

    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.ct, self.wt = ctypes, wintypes
        try:
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))  # per-monitor v2: real pixels
        except (AttributeError, OSError):
            pass  # an older Windows: the profile check below then fails on DPI and no bounds are recorded
        self.user32, self.gdi32 = ctypes.windll.user32, ctypes.windll.gdi32

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
            ct.windll.shcore.GetDpiForMonitor(handle, 0, ct.byref(x), ct.byref(y))
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
        self.user32.SetWindowPos(hwnd, 0, left + 40, top_ + 40, 1200, 800, 0x0014)
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

    def pixel(self, x, y):
        dc = self.user32.GetDC(0)
        try:
            value = self.gdi32.GetPixel(dc, x, y)
        finally:
            self.user32.ReleaseDC(0, dc)
        return value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF

    def raise_(self, hwnd, topmost):
        self.user32.SetWindowPos(hwnd, -1 if topmost else -2, 0, 0, 0, 0, 0x0013)

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


def profile_problems(state, monitor, language, ribbon_height, title_pixels):
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
    if not title_pixels or any(min(p) < 235 for p in title_pixels):
        problems.append("the Office theme is not White (the title bar is not white)")
    return problems


class Launched:
    """An app instance this tool started, with its top-level window and its process."""

    def __init__(self, key, dispatch=None):
        row, exe, progid, separate = APPS[key]
        self.key, self.row, self.exe = key, row, exe
        if key == "outlook":
            raise Unsafe("Outlook is not started by the capture tool: starting it sends the Outbox; capture it "
                         "attended (D02 T01 §15)")
        import win32com.client
        if not separate and self.running(exe):
            raise Unsafe(f"{exe} is running and allows one instance only, so the tool would drive the operator's "
                         f"own window; close {exe} first")
        self.app = (dispatch or (win32com.client.DispatchEx if separate else win32com.client.Dispatch))(progid)
        self.proc = None
        try:
            self.app.Visible = True
            self.document = self.new_document()
            self.hwnd = Win().top(self.window_handle())
            self.proc = OwnProcess(self.hwnd)
        except Exception:
            self.close()
            raise

    @staticmethod
    def running(exe):
        import subprocess
        out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {exe}", "/FO", "CSV", "/NH"], capture_output=True,
                             text=True, check=True).stdout
        return any(line.upper().startswith(f'"{exe.upper()}"') for line in out.splitlines())

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
        """Quit without saving and confirm the process this tool started has exited."""
        try:
            if self.key == "word":
                for doc in list(self.app.Documents):
                    doc.Close(SaveChanges=0)
            elif self.key == "excel":
                for book in list(self.app.Workbooks):
                    book.Close(SaveChanges=False)
            elif self.key == "powerpoint":
                for pres in list(self.app.Presentations):
                    pres.Saved = True
                    pres.Close()
        finally:
            try:
                self.app.Quit() if self.key != "word" else self.app.Quit(SaveChanges=0)
            finally:
                gone = self.proc is None or self.proc.exited(wait)
                if self.proc is not None:
                    self.proc.close()
        if not gone:
            raise Refused(f"the {self.exe} instance this tool started did not exit")


def wait_for(test, seconds=5.0, step=0.2):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = test()
        if value:
            return value
        time.sleep(step)
    return test()


def popup_items(root):
    """The items of the menu or gallery that just opened, once their count is stable. Office exposes an open menu as
    a Menu element in the app window's own tree (menus nest, so items are taken once each by runtime id)."""
    def read():
        # Word nests an empty Menu shell around the menus that hold the items, so every open Menu is read.
        menus = [e for e in descendants(root, 30) if e.control_type == "Menu"]
        seen, items = set(), []
        for e in (d for menu in menus for d in descendants(menu, 12)):
            if e.control_type in ITEM_TYPES and e.name and e.runtime_id() not in seen:
                seen.add(e.runtime_id())
                items.append(e)
        return items

    last, stable = None, 0
    deadline = time.monotonic() + 4.0
    while time.monotonic() < deadline and stable < 2:
        items = read() or []
        stable = stable + 1 if last is not None and len(items) == len(last) and items else 0
        last = items
        time.sleep(0.4)
    return last or []



def capture(args, launched, uia, win):
    row = APPS[args.app][0]
    expected = reference_build(app=row)
    if installed_build() != expected:
        raise Refused(f"the installed build {installed_build()} is not the reference {expected}")
    reported = str(getattr(launched.app, "Build", "") or getattr(launched.app, "Version", ""))
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
    if args.layout == "simplified":
        toggle = find(root, lambda e: e.automation_id == "SingleLineRibbonToggle", depth=20)
        if toggle is None:
            raise Unsafe("this build offers no Simplified Ribbon switch (SingleLineRibbonToggle not found)")
        raise Unsafe("the Simplified Ribbon switch exists but switching it is not yet captured; record its steps "
                     "in design/inventory/REFERENCE.md first (D02 T01 §2 Layout choices)")
    state = win.state(launched.hwnd)
    left, top, right, _ = state["window"]
    win.raise_(launched.hwnd, True)
    try:
        time.sleep(0.5)
        pixels = [win.pixel(left + int((right - left) * f), top + 14) for f in (0.35, 0.45, 0.55, 0.65)]
    finally:
        win.raise_(launched.hwnd, False)
    ribbon_h = lower.rect[3] - lower.rect[1] if lower.rect else 0
    problems = profile_problems(state, monitor, launched.language(), ribbon_h, pixels)
    identifiers = baseline_ids(args.app)
    ctx = Context(args.app, expected, identifiers, origin=None if problems else state["origin"])
    tab_elements = [t for t in tabs_bar.children() if t.control_type == "TabItem"]
    names = [t.name for t in tab_elements]
    wanted = names if args.all_tabs else [args.tab]
    unknown = [w for w in wanted if w not in names]
    if unknown:
        raise Refused(f"no tab named {unknown}; this window's tabs are {names}")
    records = []
    for order, tab in enumerate(tab_elements):
        if tab.name not in wanted:
            continue
        tab.select()
        if not wait_for(lambda: first_group_name(uia.element(launched.hwnd)) == tab.name):
            raise Refused(f"tab {tab.name!r} did not open")
        lower = find(uia.element(launched.hwnd), lambda e: e.name == "Lower Ribbon")
        tab_records = walk_tab(tab, order, lower, ctx)
        if args.expand:
            tab_records = expand_all(tab_records, lower, ctx, launched, uia, win)
        records += tab_records
    return records, problems, ctx.skipped


def first_group_name(root):
    lower = find(root, lambda e: e.name == "Lower Ribbon")
    first = next((c for c in lower.children() if c.control_type == "Group"), None) if lower else None
    return first.name if first else None


def expand_all(records, lower, ctx, launched, uia, win):
    """Open every menu, split-button menu and gallery once, record its items, and close it again."""
    by_label = {}
    for el in descendants(lower):
        by_label.setdefault((el.name, el.automation_id), el)
    out = []
    for rec in records:
        out.append(rec)
        if rec.get("kind") != "control" or rec.get("controlType") not in ("menu", "gallery", "splitButton"):
            continue
        element = next((el for (name, aid), el in by_label.items()
                        if rec.get("idMso") and aid in (rec["idMso"], rec["idMso"] + "_Dropdown")), None)
        element = element or by_label.get((rec["label"], ""))
        if element is None:
            continue
        target = next((p for p in element.children() if p.automation_id.endswith("_Dropdown")), element) \
            if element.control_type == "SplitButton" else element
        if target.expand_state() is None:
            continue
        before = win.popups(launched.proc.pid)
        target.expand()
        try:
            items = popup_items(uia.element(launched.hwnd))
        finally:
            close_popup(target, lambda: [h for h in win.popups(launched.proc.pid) if h not in before]
                        or find(uia.element(launched.hwnd), lambda e: e.control_type == "Menu", depth=30) is not None,
                        rec["label"])
        out += expand_items(rec, target, items, ctx)
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


def baseline_ids(app):
    data = json.loads((INVENTORY / app / "baseline.json").read_text(encoding="utf-8"))
    col = data["columns"].index("idMso")
    return {r[col] for r in data["rows"] if r[col]}


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
        records, problems, skipped = capture(args, launched, (uia_factory or Uia)(), (win_factory or Win)())
    except Unsafe as exc:
        print(f"capture-ui: {exc}", file=sys.stderr)
        launched.close()
        return 2
    except Refused as exc:
        print(f"capture-ui: {exc}", file=sys.stderr)
        launched.close()
        return 1
    except BaseException:
        launched.close()
        raise
    launched.close()
    if args.merge and out.exists():
        records = merge(json.loads(out.read_text(encoding="utf-8")), records)
    publish({out: render(records)})
    for line in skipped:
        print(f"skipped {line}")
    print(f"{out}: {len(records)} records" + ("; bounds recorded under " + PROFILE if not problems else
                                               "; no bounds: " + "; ".join(problems)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
