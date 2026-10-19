"""Rizonesoft Office wordmark and lockups, set in Plus Jakarta Sans (SIL OFL 1.1) and outlined.

Approved 2026-10-20 (todo/01-brand/TODO-02-icon-system.md section 2): "Rizonesoft" in weight 700 and the product name
in weight 400 in a quieter colour, beside the suite or app icon.
"""
import math

import icon_design as d
from text_outline import Outliner

THEMES = {"light": ("#1f2a44", "#5b6780"), "dark": ("#f2f4f8", "#aab4c8")}
SIZE, GAP_WORD, TRACK = 40, 10.0, -0.6
_outliner = None


def outliner():
    global _outliner
    if _outliner is None:
        _outliner = Outliner()
    return _outliner


def _words(product, x, baseline, theme):
    ink, sub = THEMES[theme]
    o = outliner()
    first, w1 = o.path("Rizonesoft", SIZE, 700, x, baseline, TRACK)
    second, w2 = o.path(product, SIZE, 400, x + w1 + GAP_WORD, baseline, TRACK)
    return f'<path d="{first}" fill="{ink}"/><path d="{second}" fill="{sub}"/>', w1 + GAP_WORD + w2


def wordmark_svg(theme):
    """Text only: "Rizonesoft Office" on a 40-unit-high canvas."""
    paths, width = _words("Office", 0, 33, theme)
    w = math.ceil(width + 1)  # whole units, so every raster scale keeps the exact aspect ratio
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 42" width="{w}" height="42">'
            f'<title>Rizonesoft Office</title>{paths}</svg>\n')


def lockup_svg(icon, theme):
    """Icon and words side by side on a 96-unit-high canvas. icon is d.SUITE or an app key."""
    product = "Office" if icon == d.SUITE else d.APPS[icon][0]
    src = d.icon_svg(icon, "lg").strip()
    head = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">'
    inner = src[len(head):]
    inner = inner[inner.index("</title>") + len("</title>"):]
    paths, width = _words(product, 108, 63, theme)
    w = math.ceil(108 + width + 4)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 96" width="{w}" height="96">'
            f'<title>Rizonesoft {product}</title>'
            f'<svg x="0" y="0" width="96" height="96" viewBox="0 0 128 128">{inner}{paths}</svg>\n')
