# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
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


# README banner (todo/01-brand/TODO-03-github-graphics.md section 1): a 1280 by 320 card for each GitHub theme.
BANNER_W, BANNER_H = 1280, 320
BANNER_CARD = {"light": ("#f7f9fc", "#edf1f8", "#dfe5ef"), "dark": ("#161b22", "#0d1117", "#30363d")}  # top, bottom, rim
GITHUB_CANVAS = {"light": "#ffffff", "dark": "#0d1117"}
TAGLINE = "The open-source office suite for Windows."
APP_LINE = "Write, Grid, Stage, Flow, Plan and Mail"


def banner_svg(theme):
    """The README hero banner for one GitHub theme: suite mark, wordmark, tagline and the app names, outlined."""
    ink, sub = THEMES[theme]
    top, bottom, rim = BANNER_CARD[theme]
    o = outliner()
    mark, gap = 208, 40
    first, w1 = o.path("Rizonesoft", 72, 700, 0, 0, TRACK * 1.8)
    second, w2 = o.path("Office", 72, 400, 0, 0, TRACK * 1.8)
    text_w = max(w1 + 18 + w2, o.path(TAGLINE, 30, 500)[1], o.path(APP_LINE, 24, 400)[1])
    x0 = round((BANNER_W - (mark + gap + text_w)) / 2)
    tx = x0 + mark + gap
    words = (f'<path d="{o.path("Rizonesoft", 72, 700, tx, 148, TRACK * 1.8)[0]}" fill="{ink}"/>'
             f'<path d="{o.path("Office", 72, 400, tx + w1 + 18, 148, TRACK * 1.8)[0]}" fill="{sub}"/>'
             f'<path d="{o.path(TAGLINE, 30, 500, tx, 206)[0]}" fill="{ink}"/>'
             f'<path d="{o.path(APP_LINE, 24, 400, tx, 248)[0]}" fill="{sub}"/>')
    src = d.icon_svg(d.SUITE, "lg").strip()
    inner = src[src.index("</title>") + len("</title>"):-len("</svg>")]
    # The tagline's contrast and the weakest of any text, on either card stop and on GitHub's canvas, recorded for
    # review in the file itself.
    grounds = (top, bottom, GITHUB_CANVAS[theme])
    tagline = min(d.contrast(ink, bg) for bg in grounds)
    worst = min(d.contrast(c, bg) for c in (ink, sub) for bg in grounds)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BANNER_W} {BANNER_H}" width="{BANNER_W}" '
            f'height="{BANNER_H}"><!-- Contrast on the card and on the GitHub {theme} canvas: tagline at least '
            f'{tagline:.2f}:1, any text at least {worst:.2f}:1 --><title>Rizonesoft Office</title>'
            f'<defs><linearGradient id="banner-{theme}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="1" stop-color="{bottom}"/></linearGradient></defs>'
            f'<rect x="1" y="1" width="{BANNER_W - 2}" height="{BANNER_H - 2}" rx="28" fill="url(#banner-{theme})" '
            f'stroke="{rim}" stroke-width="2"/>'
            f'<svg x="{x0}" y="{(BANNER_H - mark) // 2}" width="{mark}" height="{mark}" viewBox="0 0 128 128">{inner}</svg>'
            f'{words}</svg>\n')
