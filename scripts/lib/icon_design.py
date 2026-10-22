# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Rizonesoft Office icon design: the approved Glass drawings as SVG generators.

Approved 2026-10-20 (todo/01-brand/TODO-02-icon-system.md section 1):
- Apps at 48 px and up ("lg"): draft 3 Glass. A gradient orb and a dark block behind a frosted pane, deep-colour symbol.
- Apps below 48 px: draft 4 Variation A. Orb and pane only, flat tint instead of blur; "md" (32 to 40 px) uses two or
  three heavy strokes, "sm" (16 to 24 px) uses solid symbols.
- Suite logo at every size: Variation A with the orb split into the six app colours and one square per app on the glass.

Every function is pure and deterministic, so the same inputs always produce byte-identical SVG.
"""
import math
import re

APPS = {
    # key: (display name, Microsoft counterpart, [light, dark] gradient ends)
    "write": ("Write", "Word", ["#4f8df7", "#1e4fc2"]),
    "grid": ("Grid", "Excel", ["#34c27a", "#0f7a45"]),
    "stage": ("Stage", "PowerPoint", ["#ff8a4c", "#d4421b"]),
    "flow": ("Flow", "Visio", ["#9b7bf7", "#5b35c9"]),
    "plan": ("Plan", "Project", ["#2dc2b5", "#0b7f86"]),
    "mail": ("Mail", "Outlook", ["#3cc4f0", "#0b7cc0"]),
}
# Each app's single colour (taskbar badges, accents, the palette in docs/brand/icon-language.md): the point on its
# gradient nearest the middle that keeps 3:1 against both a white and a #1f1f1f background.
APP_COLOR = {"write": "#366edc", "grid": "#229e60", "stage": "#ea6634", "flow": "#7b58e0", "plan": "#1ca09e",
             "mail": "#229ed7"}
SUITE = "rizonesoft-office"
SUITE_TINT = "#7c8db5"
TIERS = ("lg", "md", "sm")


def tier_for(px):
    """The drawing used at a displayed size in pixels (points on high-density displays)."""
    if px >= 48:
        return "lg"
    if px >= 32:
        return "md"
    return "sm"


def mix(hex_color, other, t):
    a = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(v + (w - v) * t):02x}" for v, w in zip(a, b))


def contrast(c1, c2):
    """WCAG 2 contrast ratio of two #rrggbb colours."""
    def lum(c):
        lin = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
               for v in (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))]
        return .2126 * lin[0] + .7152 * lin[1] + .0722 * lin[2]
    hi, lo = sorted((lum(c1), lum(c2)), reverse=True)
    return (hi + .05) / (lo + .05)


def n(x):
    """Format a coordinate with at most three decimals and no trailing zeros."""
    text = f"{x:.3f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def rect(x, y, w, h, rx, fill, extra=""):
    tail = f" {extra}" if extra else ""
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(rx)}" fill="{fill}"{tail}/>'


def glyph(key, tier, col):
    """The app symbol in a 64-unit box centred on 0,0."""
    def st(w):
        return f'stroke="{col}" stroke-width="{n(w)}" stroke-linecap="round" stroke-linejoin="round" fill="none"'
    table = {
        "lg": {
            "write": f'<path {st(7)} d="M-22,-20 H22 M-22,-6 H22 M-22,8 H22 M-22,22 H6"/>',
            "grid": f'<rect {st(7)} x="-25" y="-21" width="50" height="42" rx="6"/>'
                    f'<path {st(4.9)} d="M-8,-21 V21 M9,-21 V21 M-25,-7 H25 M-25,7 H25"/>',
            "stage": f'<rect {st(7)} x="-27" y="-24" width="54" height="36" rx="5"/>'
                     f'<path {st(7)} d="M-12,4 V-2 M0,4 V-12 M12,4 V-6 M0,12 V24 M-11,24 H11"/>',
            "flow": f'<path {st(5.25)} d="M-8,-15 H8 M-15,-6 L-4,12 M15,-6 L4,12"/>'
                    f'<rect x="-26" y="-25" width="20" height="20" rx="5" fill="{col}"/>'
                    f'<circle cx="16" cy="-15" r="10" fill="{col}"/><circle cx="0" cy="20" r="10" fill="{col}"/>',
            "plan": f'<path stroke="{col}" stroke-width="9.1" stroke-linecap="round" fill="none" '
                    f'd="M-24,-17 H2 M-10,0 H18 M4,17 H25"/>',
            "mail": f'<rect {st(7)} x="-27" y="-19" width="54" height="38" rx="6"/>'
                    f'<path {st(7)} d="M-22,-13 L0,4 L22,-13"/>',
        },
        "md": {
            "write": f'<path {st(11)} d="M-22,-16 H22 M-22,0 H22 M-22,16 H6"/>',
            "grid": f'<rect {st(10)} x="-24" y="-20" width="48" height="40" rx="6"/>'
                    f'<path {st(8)} d="M0,-20 V20 M-24,0 H24"/>',
            "stage": f'<rect {st(10)} x="-26" y="-22" width="52" height="32" rx="5"/>'
                     f'<path {st(10)} d="M0,10 V24 M-12,24 H12"/>',
            "flow": f'<path {st(9)} d="M-12,-10 L12,12"/>'
                    f'<rect x="-27" y="-25" width="24" height="24" rx="6" fill="{col}"/>'
                    f'<circle cx="15" cy="14" r="12" fill="{col}"/>',
            "plan": f'<path {st(12)} d="M-24,-16 H0 M-10,0 H14 M2,16 H24"/>',
            "mail": f'<rect {st(10)} x="-26" y="-18" width="52" height="36" rx="6"/>'
                    f'<path {st(10)} d="M-19,-11 L0,4 L19,-11"/>',
        },
        "sm": {
            "write": f'<path {st(14)} d="M-21,-11 H21 M-21,13 H7"/>',
            "grid": "".join(rect(x, y, 21, 19, 4, col) for x, y in ((-23, -21), (2, -21), (-23, 2), (2, 2))),
            "stage": f'<rect x="-26" y="-25" width="52" height="34" rx="6" fill="{col}"/><path {st(12)} d="M0,10 V24"/>',
            "flow": f'<path {st(11)} d="M-12,-10 L12,12"/>'
                    f'<rect x="-27" y="-27" width="26" height="26" rx="6" fill="{col}"/>'
                    f'<circle cx="14" cy="14" r="14" fill="{col}"/>',
            "plan": f'<path {st(15)} d="M-22,-10 H6 M-4,12 H22"/>',
            "mail": f'<rect x="-27" y="-19" width="54" height="38" rx="6" fill="{col}"/>'
                    '<path stroke="#ffffff" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" '
                    'fill="none" d="M-17,-10 L0,4 L17,-10"/>',
        },
    }
    return table[tier][key]


# App icon geometry on the 128-unit canvas, per tier. The drawings and the keyline sheet both read these.
APP_ORB = {"lg": (80, 44, 38), "md": (82, 42, 36), "sm": (86, 40, 38)}  # cx, cy, r
APP_PANE = {"lg": (18, 30, 92, 80, 20), "md": (14, 34, 92, 80, 20), "sm": (8, 36, 96, 84, 22)}  # x, y, w, h, rx
APP_GLYPH_AT = {"lg": (64, 70, .95), "md": (60, 74, 1.12), "sm": (56, 78, 1.25)}  # centre x, y, scale of 64 box
APP_BLOCK = (10, 62, 58, 56, 16)  # the dark block behind the lg pane: x, y, w, h, rx
# The suite logo takes the md geometry at lg (Variation A at every size).
SUITE_ORB = {"lg": APP_ORB["md"], "md": APP_ORB["md"], "sm": APP_ORB["sm"]}
SUITE_PANE = {"lg": APP_PANE["md"], "md": APP_PANE["md"], "sm": APP_PANE["sm"]}
SUITE_SQUARES_SHARE = {"lg": .62, "md": .7, "sm": .78}  # the six squares' width as a share of the pane's
MONO_GAP = 5  # units of clear space between the one-colour mark's orb and pane


def _app_parts(key, tier, ids):
    a, b = APPS[key][2]
    orb, pane, at = APP_ORB[tier], APP_PANE[tier], APP_GLYPH_AT[tier]
    grad = ids("g")
    defs = (f'<linearGradient id="{grad}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')

    def back(mode):
        fill = f"url(#{grad})" if mode == "solid" else mix(a, "#ffffff", .5)
        s = f'<circle cx="{orb[0]}" cy="{orb[1]}" r="{orb[2]}" fill="{fill}"/>'
        if tier == "lg":
            s += rect(*APP_BLOCK, mix(b, "#000000", .1) if mode == "solid" else mix(b, "#ffffff", .42))
        return s

    deep = mix(b, "#000000", .15)
    content = f'<g transform="translate({n(at[0])},{n(at[1])}) scale({n(at[2])})">{glyph(key, tier, deep)}</g>'
    tint = mix(a, "#ffffff", .8 if tier == "sm" else .84)
    return defs, pane, tint, mix(a, "#000000", .1), back, content


def _six_square_boxes(cx, cy, width):
    """(x, y, side, corner radius) of the suite's six app squares, two rows of three, in APPS order."""
    g = width * .1
    s = (width - 2 * g) / 3
    h = 2 * s + g
    return [(cx - width / 2 + (i % 3) * (s + g), cy - h / 2 + (i // 3) * (s + g), s, s * .28) for i in range(len(APPS))]


def six_squares(cx, cy, width, color_of):
    return "".join(rect(x, y, s, s, r, color_of(k)) for (x, y, s, r), k in zip(_six_square_boxes(cx, cy, width), APPS))


def _suite_parts(tier, ids):
    orb, pane = SUITE_ORB[tier], SUITE_PANE[tier]
    clip = ids("o")
    defs = f'<clipPath id="{clip}"><circle cx="{orb[0]}" cy="{orb[1]}" r="{orb[2]}"/></clipPath>'

    def back(mode):
        out = []
        for i, k in enumerate(APPS):
            a0, a1 = math.radians(-120 + 60 * i), math.radians(-120 + 60 * (i + 1))
            fill = APPS[k][2][0] if mode == "solid" else mix(APPS[k][2][0], "#ffffff", .55)
            out.append(f'<path d="M{orb[0]},{orb[1]} L{n(orb[0] + 80 * math.cos(a0))},{n(orb[1] + 80 * math.sin(a0))} '
                       f'L{n(orb[0] + 80 * math.cos(a1))},{n(orb[1] + 80 * math.sin(a1))} Z" fill="{fill}"/>')
        return f'<g clip-path="url(#{clip})">{"".join(out)}</g>'

    share = SUITE_SQUARES_SHARE[tier]
    content = six_squares(pane[0] + pane[2] / 2, pane[1] + pane[3] / 2, pane[2] * share, lambda k: APPS[k][2][1])
    tint = mix(SUITE_TINT, "#ffffff", .8 if tier == "sm" else .84)
    return defs, pane, tint, mix(SUITE_TINT, "#000000", .1), back, content


def icon_svg(icon, tier):
    """Standalone SVG for an app key or SUITE at one tier, on a 128-unit canvas."""
    if tier not in TIERS:
        raise ValueError(f"unknown tier: {tier}")
    if icon != SUITE and icon not in APPS:
        raise ValueError(f"unknown icon: {icon}")
    counter = [0]

    def ids(prefix):
        counter[0] += 1
        return f"{icon}-{tier}-{prefix}{counter[0]}"

    parts = _suite_parts(tier, ids) if icon == SUITE else _app_parts(icon, tier, ids)
    defs, (px, py, pw, ph, prx), tint, rim, back, content = parts
    clip = ids("p")
    defs += f'<clipPath id="{clip}">{rect(px, py, pw, ph, prx, "#000")}</clipPath>'
    body = back("solid")
    if tier == "lg":
        blur, shadow = ids("b"), ids("s")
        defs += (f'<filter id="{blur}"><feGaussianBlur stdDeviation="7"/></filter>'
                 f'<filter id="{shadow}" x="-30%" y="-30%" width="160%" height="160%">'
                 '<feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#0b1530" flood-opacity=".2"/></filter>')
        # The pane has a solid tinted base under the frost, so the icon looks the same on any desktop colour.
        body += (f'<g filter="url(#{shadow})">{rect(px, py, pw, ph, prx, tint)}'
                 f'<g clip-path="url(#{clip})"><g filter="url(#{blur})">{back("solid")}</g>'
                 + rect(px, py, pw, ph, 0, "#ffffff", 'opacity=".42"') + '</g></g>'
                 + rect(px + .5, py + .5, pw - 1, ph - 1, prx - .5, "none",
                        'stroke="#ffffff" stroke-opacity=".85" stroke-width="2"'))
    else:
        body += (rect(px, py, pw, ph, prx, tint) + f'<g clip-path="url(#{clip})">{back("seen")}</g>'
                 + rect(px, py, pw, ph, prx, "none",
                        f'stroke="{rim}" stroke-opacity="{".6" if tier == "sm" else ".4"}" '
                        f'stroke-width="{6 if tier == "sm" else 3}"'))
    name = "Rizonesoft Office" if icon == SUITE else f"Rizonesoft {APPS[icon][0]}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">'
            f'<title>{name}</title><defs>{defs}</defs>{body}{content}</svg>\n')


def app_master_svg(key, tier):
    """An app master as committed in design/icons/apps/: the icon with its Microsoft counterpart noted in a comment,
    the only place the counterpart is named in the artwork (todo/01-brand/TODO-02-icon-system.md section 3)."""
    head, rest = icon_svg(key, tier).split(">", 1)
    return f"{head}><!-- Counterpart: Microsoft {APPS[key][1]} -->{rest}"


def keylines_svg():
    """The keyline sheet: each app tier's pane, orb, glyph box and (lg) block, drawn from the same constants as the
    icons, side by side on 128-unit cells (docs/brand/icon-language.md, Grid)."""
    colors = {"pane": "#1e4fc2", "orb": "#d4421b", "glyph": "#0f7a45", "block": "#5b35c9"}
    cells = []
    for i, tier in enumerate(TIERS):
        x0 = i * 144
        px, py, pw, ph, prx = APP_PANE[tier]
        cx, cy, r = APP_ORB[tier]
        gx, gy, gs = APP_GLYPH_AT[tier]
        half = 32 * gs
        parts = [rect(x0, 0, 128, 128, 0, "none", 'stroke="#9aa3b5" stroke-width="1" stroke-dasharray="4 4"'),
                 f'<circle cx="{n(x0 + cx)}" cy="{n(cy)}" r="{n(r)}" fill="none" stroke="{colors["orb"]}" '
                 'stroke-width="1.5"/>',
                 rect(x0 + px, py, pw, ph, prx, "none", f'stroke="{colors["pane"]}" stroke-width="1.5"'),
                 rect(x0 + gx - half, gy - half, 2 * half, 2 * half, 0, "none",
                      f'stroke="{colors["glyph"]}" stroke-width="1.5" stroke-dasharray="3 3"')]
        if tier == "lg":
            bx, by, bw, bh, brx = APP_BLOCK
            parts.append(rect(x0 + bx, by, bw, bh, brx, "none", f'stroke="{colors["block"]}" stroke-width="1.5"'))
        cells.append("".join(parts))
    width = 144 * len(TIERS) - 16
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 {width + 4} 132" width="{width + 4}" '
            f'height="132"><title>Rizonesoft Office icon keylines (lg, md, sm)</title>{"".join(cells)}</svg>\n')


def rounded_rect_path(x, y, w, h, r):
    """A rounded rectangle as path data, so it can join other subpaths under one fill rule."""
    return (f"M{n(x + r)},{n(y)} H{n(x + w - r)} A{n(r)},{n(r)} 0 0 1 {n(x + w)},{n(y + r)} V{n(y + h - r)} "
            f"A{n(r)},{n(r)} 0 0 1 {n(x + w - r)},{n(y + h)} H{n(x + r)} A{n(r)},{n(r)} 0 0 1 {n(x)},{n(y + h - r)} "
            f"V{n(y + r)} A{n(r)},{n(r)} 0 0 1 {n(x + r)},{n(y)} Z")


def suite_mono_svg():
    """The suite mark in one colour (currentColor) for single-colour use, on the md geometry: the orb cut clear of
    the pane by MONO_GAP units, and the pane with the six app squares knocked out."""
    cx, cy, r = SUITE_ORB["md"]
    px, py, pw, ph, prx = SUITE_PANE["md"]
    gap = MONO_GAP
    cut = f"M-1,-1 H129 V129 H-1 Z {rounded_rect_path(px - gap, py - gap, pw + 2 * gap, ph + 2 * gap, prx + gap)}"
    holes = " ".join(rounded_rect_path(x, y, s, s, rr)
                     for x, y, s, rr in _six_square_boxes(px + pw / 2, py + ph / 2, pw * SUITE_SQUARES_SHARE["md"]))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">'
            '<title>Rizonesoft Office</title>'
            f'<defs><clipPath id="mono-cut"><path clip-rule="evenodd" d="{cut}"/></clipPath></defs>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="currentColor" clip-path="url(#mono-cut)"/>'
            f'<path fill="currentColor" fill-rule="evenodd" d="{rounded_rect_path(px, py, pw, ph, prx)} {holes}"/>'
            '</svg>\n')


# Each pixel-aligned small variant and the tier whose design it redraws (todo/01-brand/TODO-02-icon-system.md
# section 4).
PIXEL_SIZES = {16: "sm", 24: "sm", 32: "md"}


def _on_grid(v, width):
    """A coordinate snapped so a stroke of a whole number of pixels covers whole pixels."""
    return math.floor(v) + .5 if width % 2 else round(v)


def _pixel_glyph(svg, at, k):
    """Redraw glyph SVG (the closed vocabulary: rect, circle, stroked path) on the pixel grid; at is the glyph's
    (centre x, centre y, scale) on the 128-unit canvas and k the pixels per canvas unit."""
    gx, gy, gs = at

    def X(v):
        return (gx + gs * v) * k

    def Y(v):
        return (gy + gs * v) * k

    out = []
    for name, attrs in re.findall(r"<(\w+)([^>]*)/>", svg):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))
        stroke = a.get("stroke", "none")
        width = max(1, round(float(a["stroke-width"]) * gs * k)) if stroke != "none" else 0
        keep = "".join(f' {key}="{a[key]}"' for key in ("stroke-linecap", "stroke-linejoin") if key in a)
        paint = f'fill="{a["fill"]}" stroke="{stroke}"' + (f' stroke-width="{width}"{keep}' if width else "")
        if name == "rect":
            x, y, w, h = (float(a[v]) for v in ("x", "y", "width", "height"))
            # The start snaps and the size rounds on its own, so equal shapes stay equal and the gaps between
            # them survive (rounding both edges closes a gap under a pixel, as between the Grid cells at 16 px).
            x0, y0 = (_on_grid(X(x), width), _on_grid(Y(y), width)) if width else (round(X(x)), round(Y(y)))
            x1, y1 = x0 + max(1, round(w * gs * k)), y0 + max(1, round(h * gs * k))
            rx = max(1, round(float(a.get("rx", 0)) * gs * k)) if float(a.get("rx", 0)) else 0
            out.append(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" rx="{rx}" {paint}/>')
        elif name == "circle":
            d = max(2, round(2 * float(a["r"]) * gs * k))
            cx, cy = (_on_grid(v, d) for v in (X(float(a["cx"])), Y(float(a["cy"]))))
            out.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(d / 2)}" {paint}/>')
        else:
            parts = []
            for cmd, args in re.findall(r"([MLHVZ])([^MLHVZ]*)", a["d"]):
                v = [float(t) for t in re.findall(r"-?[\d.]+", args)]
                if cmd in "ML":
                    parts.append(f"{cmd}{n(_on_grid(X(v[0]), width))},{n(_on_grid(Y(v[1]), width))}")
                elif cmd == "H":
                    parts.append(f"H{n(_on_grid(X(v[0]), width))}")
                elif cmd == "V":
                    parts.append(f"V{n(_on_grid(Y(v[0]), width))}")
                else:
                    parts.append("Z")
            out.append(f'<path {paint} d="{" ".join(parts)}"/>')
    return "".join(out)


def pixel_svg(key, size):
    """An app icon redrawn for one small size on a size-unit canvas with every edge on the pixel grid, following the
    design its tier uses at that size (PIXEL_SIZES). The Microsoft counterpart is noted in a comment, as on the
    other masters."""
    tier = PIXEL_SIZES[size]
    k = size / 128
    a, b = APPS[key][2]
    cx, cy, r = APP_ORB[tier]
    px, py, pw, ph, prx = APP_PANE[tier]
    d = max(2, round(2 * r * k))
    ocx, ocy, orr = _on_grid(cx * k, d), _on_grid(cy * k, d), d / 2
    x0, y0, x1, y1 = round(px * k), round(py * k), round((px + pw) * k), round((py + ph) * k)
    rr = max(1, round(prx * k))
    tint = mix(a, "#ffffff", .8 if tier == "sm" else .84)
    grad, clip = f"{key}-{size}-g", f"{key}-{size}-p"
    pane = f'x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{rr}"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
            f'<!-- Counterpart: Microsoft {APPS[key][1]} --><title>Rizonesoft {APPS[key][0]}</title>'
            f'<defs><linearGradient id="{grad}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/>'
            f'<stop offset="1" stop-color="{b}"/></linearGradient>'
            f'<clipPath id="{clip}"><rect {pane}/></clipPath></defs>'
            f'<circle cx="{n(ocx)}" cy="{n(ocy)}" r="{n(orr)}" fill="url(#{grad})"/>'
            f'<rect {pane} fill="{tint}"/>'
            f'<circle cx="{n(ocx)}" cy="{n(ocy)}" r="{n(orr)}" fill="{mix(a, "#ffffff", .5)}" '
            f'clip-path="url(#{clip})"/>'
            f'<rect x="{x0 + .5}" y="{y0 + .5}" width="{x1 - x0 - 1}" height="{y1 - y0 - 1}" rx="{n(rr - .5)}" '
            f'fill="none" stroke="{mix(a, "#000000", .1)}" stroke-opacity="{".6" if tier == "sm" else ".4"}" '
            f'stroke-width="1"/>'
            f'{_pixel_glyph(glyph(key, tier, mix(b, "#000000", .15)), APP_GLYPH_AT[tier], k)}</svg>\n')
