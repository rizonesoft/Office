"""Rizonesoft Office icon design: the approved Glass drawings as SVG generators.

Approved 2026-10-20 (todo/01-brand/TODO-02-icon-system.md section 1):
- Apps at 48 px and up ("lg"): draft 3 Glass. A gradient orb and a dark block behind a frosted pane, deep-colour symbol.
- Apps below 48 px: draft 4 Variation A. Orb and pane only, flat tint instead of blur; "md" (32 to 40 px) uses two or
  three heavy strokes, "sm" (16 to 24 px) uses solid symbols.
- Suite logo at every size: Variation A with the orb split into the six app colours and one square per app on the glass.

Every function is pure and deterministic, so the same inputs always produce byte-identical SVG.
"""
import math

APPS = {
    # key: (display name, Microsoft counterpart, [light, dark] gradient ends)
    "write": ("Write", "Word", ["#4f8df7", "#1e4fc2"]),
    "grid": ("Grid", "Excel", ["#34c27a", "#0f7a45"]),
    "stage": ("Stage", "PowerPoint", ["#ff8a4c", "#d4421b"]),
    "flow": ("Flow", "Visio", ["#9b7bf7", "#5b35c9"]),
    "plan": ("Plan", "Project", ["#2dc2b5", "#0b7f86"]),
    "mail": ("Mail", "Outlook", ["#3cc4f0", "#0b7cc0"]),
}
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


def _app_parts(key, tier, ids):
    a, b = APPS[key][2]
    orb = {"lg": (80, 44, 38), "md": (82, 42, 36), "sm": (86, 40, 38)}[tier]
    pane = {"lg": (18, 30, 92, 80, 20), "md": (14, 34, 92, 80, 20), "sm": (8, 36, 96, 84, 22)}[tier]
    at = {"lg": (64, 70, .95), "md": (60, 74, 1.12), "sm": (56, 78, 1.25)}[tier]
    grad = ids("g")
    defs = (f'<linearGradient id="{grad}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')

    def back(mode):
        fill = f"url(#{grad})" if mode == "solid" else mix(a, "#ffffff", .5)
        s = f'<circle cx="{orb[0]}" cy="{orb[1]}" r="{orb[2]}" fill="{fill}"/>'
        if tier == "lg":
            s += rect(10, 62, 58, 56, 16, mix(b, "#000000", .1) if mode == "solid" else mix(b, "#ffffff", .42))
        return s

    deep = mix(b, "#000000", .15)
    content = f'<g transform="translate({n(at[0])},{n(at[1])}) scale({n(at[2])})">{glyph(key, tier, deep)}</g>'
    tint = mix(a, "#ffffff", .8 if tier == "sm" else .84)
    return defs, pane, tint, mix(a, "#000000", .1), back, content


def six_squares(cx, cy, width, color_of):
    g = width * .1
    s = (width - 2 * g) / 3
    h = 2 * s + g
    return "".join(rect(cx - width / 2 + (i % 3) * (s + g), cy - h / 2 + (i // 3) * (s + g), s, s, s * .28, color_of(k))
                   for i, k in enumerate(APPS))


def _suite_parts(tier, ids):
    orb = (86, 40, 38) if tier == "sm" else (82, 42, 36)
    pane = (8, 36, 96, 84, 22) if tier == "sm" else (14, 34, 92, 80, 20)
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

    share = {"lg": .62, "md": .7, "sm": .78}[tier]
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
