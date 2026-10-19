"""Rizonesoft Office document file-type icons: the approved "Labelled" direction as SVG generators.

Approved 2026-10-20 (todo/01-brand/TODO-02-icon-system.md section 5): the Office composition. A white page with a
folded corner, a content hint in the app colour, an extension tag at the bottom right, and the app's glass icon over
the lower-left edge. Templates have a dashed page, macro-enabled files an amber mark, CSV and RTF a plain grey hint.
The app badge uses the app icon drawing made for its own displayed size: the large drawing from 40 px, below that the
32 px drawing, below 32 px the 16 px drawing.
"""
import icon_design as d
from text_outline import Outliner

# ext: (app key, kind, MIME type). kind: "" normal, macro, template, plain, calendar, contact.
TYPES = {
    "docx": ("write", "", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    "docm": ("write", "macro", "application/vnd.ms-word.document.macroEnabled.12"),
    "dotx": ("write", "template", "application/vnd.openxmlformats-officedocument.wordprocessingml.template"),
    "doc": ("write", "", "application/msword"),
    "rtf": ("write", "plain", "application/rtf"),
    "odt": ("write", "", "application/vnd.oasis.opendocument.text"),
    "xlsx": ("grid", "", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    "xlsm": ("grid", "macro", "application/vnd.ms-excel.sheet.macroEnabled.12"),
    "xltx": ("grid", "template", "application/vnd.openxmlformats-officedocument.spreadsheetml.template"),
    "xls": ("grid", "", "application/vnd.ms-excel"),
    "csv": ("grid", "plain", "text/csv"),
    "ods": ("grid", "", "application/vnd.oasis.opendocument.spreadsheet"),
    "pptx": ("stage", "", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
    "pptm": ("stage", "macro", "application/vnd.ms-powerpoint.presentation.macroEnabled.12"),
    "potx": ("stage", "template", "application/vnd.openxmlformats-officedocument.presentationml.template"),
    "ppt": ("stage", "", "application/vnd.ms-powerpoint"),
    "odp": ("stage", "", "application/vnd.oasis.opendocument.presentation"),
    "vsdx": ("flow", "", "application/vnd.ms-visio.drawing.main+xml"),
    "vsdm": ("flow", "macro", "application/vnd.ms-visio.drawing.macroEnabled.main+xml"),
    "vstx": ("flow", "template", "application/vnd.ms-visio.template.main+xml"),
    "mpp": ("plan", "", "application/vnd.ms-project"),
    "mpt": ("plan", "template", "application/vnd.ms-project"),
    "eml": ("mail", "", "message/rfc822"),
    "msg": ("mail", "", "application/vnd.ms-outlook"),
    "ics": ("mail", "calendar", "text/calendar"),
    "vcf": ("mail", "contact", "text/vcard"),
}
PAGE = "M36,6 H90 L114,30 V116 Q114,122 108,122 H36 Q30,122 30,116 V12 Q30,6 36,6 Z"
FOLD = "M90,6 V24 Q90,30 96,30 H114 Z"
# Badge placement per page tier: x, y, size on the 128-unit canvas.
BADGE = {"lg": (0, 56, 68), "md": (0, 50, 74), "sm": (-2, 40, 86)}
# Variant name -> (page tier, badge tier).
VARIANTS = {"lg": ("lg", "lg"), "lg-badge-md": ("lg", "md"), "lg-badge-sm": ("lg", "sm"), "md": ("md", "sm"), "sm": ("sm", "sm")}
_outliner = None


def outliner():
    global _outliner
    if _outliner is None:
        _outliner = Outliner()
    return _outliner


def variant_for(px):
    """The drawing for a file icon displayed at px: page tier from px, badge tier from the badge's own displayed size."""
    page = d.tier_for(px)
    badge_px = px * BADGE[page][2] / 128
    badge = "lg" if badge_px >= 40 else "md" if badge_px >= 32 else "sm"
    name = page if page != "lg" else ("lg" if badge == "lg" else f"lg-badge-{badge}")
    if VARIANTS[name] != (page, badge):
        raise AssertionError(f"no variant for page {page} with badge {badge}")
    return name


def _badge(key, tier, x, y, size):
    src = d.icon_svg(key, tier).strip()
    head = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">'
    body = src[len(head):]
    body = body[body.index("</title>") + len("</title>"):]
    return f'<svg x="{d.n(x)}" y="{d.n(y)}" width="{d.n(size)}" height="{d.n(size)}" viewBox="0 0 128 128">{body}'


def _hint(key, kind, page_tier):
    a, b = d.APPS[key][2]
    soft, mid = d.mix(a, "#ffffff", .55), d.mix(b, "#ffffff", .25)
    if page_tier == "md":
        return f'<path d="M66,42 H104 M76,54 H104" stroke="{mid}" stroke-width="6" stroke-linecap="round"/>'

    def line(y, x1, x2, c=soft, w=5):
        return f'<path d="M{x1},{y} H{x2}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'
    if kind == "plain":
        grey = "#c3cad6"
        if key == "grid":
            return (f'<path d="M44,40 H106 M44,52 H106 M44,64 H106 M44,76 H106 M44,88 H106 M65,40 V88 M86,40 V88" '
                    f'stroke="{grey}" stroke-width="2"/>')
        return "".join(line(y, 44, x2, grey) for y, x2 in ((40, 84), (52, 104), (64, 104), (76, 104), (88, 96)))
    if kind == "calendar":
        dots = "".join(f'<circle cx="{d.n(50 + c * 12.5)}" cy="{60 + r * 11}" r="3" fill="{b if (r, c) == (1, 2) else soft}"/>'
                       for r in range(3) for c in range(5))
        return f'<rect x="44" y="38" width="62" height="12" rx="3" fill="{mid}"/>' + dots
    if kind == "contact":
        return (f'<circle cx="86" cy="50" r="10" fill="{soft}"/><path d="M70,80 Q70,64 86,64 Q102,64 102,80 Z" fill="{soft}"/>'
                + line(44, 44, 64, mid) + line(56, 44, 60))
    if key == "write":
        return "".join(line(y, 44, x2, mid if i == 0 else soft)
                       for i, (y, x2) in enumerate(((40, 82), (52, 104), (62, 104), (72, 104), (82, 104), (92, 92))))
    if key == "grid":
        return (f'<rect x="44" y="38" width="62" height="12" rx="2" fill="{mid}"/>'
                f'<path d="M44,62 H106 M44,74 H106 M44,86 H106 M65,50 V92 M86,50 V92" stroke="{soft}" stroke-width="2"/>'
                f'<rect x="66" y="63" width="19" height="10" fill="{soft}"/>')
    if key == "stage":
        return (f'<rect x="42" y="38" width="64" height="42" rx="4" fill="{d.mix(a, "#ffffff", .82)}" stroke="{soft}" '
                f'stroke-width="2"/>' + line(47, 50, 80, mid, 4)
                + f'<rect x="56" y="58" width="7" height="14" rx="1.5" fill="{soft}"/>'
                f'<rect x="69" y="52" width="7" height="20" rx="1.5" fill="{mid}"/>'
                f'<rect x="82" y="62" width="7" height="10" rx="1.5" fill="{soft}"/>')
    if key == "flow":
        return (f'<path d="M62,46 H84 M56,52 L66,74 M92,52 L80,74" stroke="{soft}" stroke-width="2.5"/>'
                f'<rect x="44" y="38" width="18" height="16" rx="3" fill="{mid}"/><circle cx="92" cy="46" r="8" fill="{soft}"/>'
                f'<rect x="66" y="70" width="14" height="14" fill="{mid}" transform="rotate(45 73 77)"/>')
    if key == "plan":
        return "".join(f'<rect x="{x}" y="{y}" width="{w}" height="7" rx="3.5" fill="{c}"/>'
                       for x, y, w, c in ((44, 40, 30, mid), (58, 52, 34, soft), (72, 64, 32, soft), (86, 76, 20, mid)))
    return (f'<circle cx="50" cy="44" r="6" fill="{soft}"/>' + line(41, 62, 96, mid, 4) + line(49, 62, 84, soft, 4)
            + "".join(line(y, 44, x2, soft) for y, x2 in ((62, 104), (72, 104), (82, 90))))


def _label(ext, kind, color):
    text, width = outliner().path(ext.upper(), 10, 800, tracking=.4)
    w = width + 9
    x, y = 108 - w, 76 if kind == "macro" else 100
    return (f'<rect x="{d.n(x)}" y="{y}" width="{d.n(w)}" height="16" rx="4" fill="{color}"/>'
            f'<g transform="translate({d.n(x + 4.5)},{y + 11.6})"><path d="{text}" fill="#ffffff"/></g>')


def filetype_svg(ext, variant):
    if ext not in TYPES:
        raise ValueError(f"unknown file type: {ext}")
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")
    key, kind, _ = TYPES[ext]
    page_tier, badge_tier = VARIANTS[variant]
    a, b = d.APPS[key][2]
    pid = f"{ext}-{variant}"
    template = kind == "template"
    if page_tier == "sm":
        edge = d.mix(b, "#ffffff", .1) if template else "#9aa5b8"
        body = (f'<path d="{PAGE}" fill="#ffffff" stroke="{edge}" stroke-width="5"/><path d="{FOLD}" fill="#dfe4ec"/>')
    else:
        stroke = (f'stroke="{d.mix(b, "#ffffff", .2)}" stroke-width="2.5" stroke-dasharray="6 4"' if template
                  else 'stroke="#cdd4df" stroke-width="1.5"')
        body = (f'<defs><linearGradient id="{pid}-pg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/>'
                f'<stop offset="1" stop-color="#f2f4f8"/></linearGradient>'
                f'<linearGradient id="{pid}-fd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/>'
                f'<stop offset="1" stop-color="#d9dfe8"/></linearGradient>'
                f'<filter id="{pid}-sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="2" '
                f'stdDeviation="2.5" flood-color="#0b1530" flood-opacity=".18"/></filter></defs>'
                f'<path d="{PAGE}" fill="url(#{pid}-pg)" {stroke} filter="url(#{pid}-sh)"/>'
                f'<path d="{FOLD}" fill="url(#{pid}-fd)"/>'
                '<path d="M90,6 V24 Q90,30 96,30 H114" fill="none" stroke="#c2cad6" stroke-width="1"/>'
                + _hint(key, kind, page_tier))
        if page_tier == "lg":
            if kind == "macro":
                body += ('<circle cx="100" cy="102" r="10" fill="#f59f0b"/><path d="M100,96 V103" stroke="#ffffff" '
                         'stroke-width="3.2" stroke-linecap="round"/><circle cx="100" cy="108" r="1.9" fill="#ffffff"/>')
            body += _label(ext, kind, b)
    bx, by, bs = BADGE[page_tier]
    body += _badge(key, badge_tier, bx, by, bs)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">'
            f'<title>{ext.upper()} file</title>{body}</svg>\n')
