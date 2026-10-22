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


# Social preview (todo/01-brand/TODO-03-github-graphics.md section 2): 1280 by 640, everything inside a 40-unit
# margin, on one dark card that reads in light and dark feeds alike.
SOCIAL_W, SOCIAL_H, SOCIAL_MARGIN = 1280, 640, 40
SOCIAL_CARD = ("#16203a", "#0d1117")  # top, bottom


def _nested(icon, x, y, size, tier="lg"):
    src = d.icon_svg(icon, tier).strip()
    inner = src[src.index("</title>") + len("</title>"):-len("</svg>")]
    return f'<svg x="{d.n(x)}" y="{d.n(y)}" width="{d.n(size)}" height="{d.n(size)}" viewBox="0 0 128 128">{inner}</svg>'


def social_preview_svg():
    """The repository's social preview: suite lockup, tagline, and the six app icons with their names."""
    ink, sub = THEMES["dark"]
    o = outliner()
    mark, gap, word_gap, track = 112, 28, 22, TRACK * 2
    w1 = o.path("Rizonesoft", 88, 700, 0, 0, track)[1]
    w2 = o.path("Office", 88, 400, 0, 0, track)[1]
    x0 = (SOCIAL_W - (mark + gap + w1 + word_gap + w2)) / 2
    tx = x0 + mark + gap
    parts = [_nested(d.SUITE, x0, 108, mark),
             f'<path d="{o.path("Rizonesoft", 88, 700, tx, 196, track)[0]}" fill="{ink}"/>',
             f'<path d="{o.path("Office", 88, 400, tx + w1 + word_gap, 196, track)[0]}" fill="{sub}"/>']
    tag_w = o.path(TAGLINE, 36, 500)[1]
    parts.append(f'<path d="{o.path(TAGLINE, 36, 500, (SOCIAL_W - tag_w) / 2, 282)[0]}" fill="{ink}"/>')
    size, step = 128, 128 + 48
    left = (SOCIAL_W - (6 * size + 5 * 48)) / 2
    for i, key in enumerate(d.APPS):
        x = left + i * step
        parts.append(_nested(key, x, 350, size))
        name = d.APPS[key][0]
        nw = o.path(name, 26, 600)[1]
        parts.append(f'<path d="{o.path(name, 26, 600, x + (size - nw) / 2, 520)[0]}" fill="{sub}"/>')
    top, bottom = SOCIAL_CARD
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SOCIAL_W} {SOCIAL_H}" width="{SOCIAL_W}" '
            f'height="{SOCIAL_H}"><title>Rizonesoft Office</title><defs><linearGradient id="social-bg" x1="0" y1="0" '
            f'x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/>'
            f'</linearGradient></defs><rect id="card" width="{SOCIAL_W}" height="{SOCIAL_H}" fill="url(#social-bg)"/>'
            f'{"".join(parts)}</svg>\n')


# App lineup strip (todo/01-brand/TODO-03-github-graphics.md section 3): the six app icons with their names and the
# Microsoft app each stands in for, on a transparent ground so it sits on the README in either GitHub theme.
LINEUP_ICON, LINEUP_GAP, LINEUP_PAD = 96, 56, 24


def lineup_svg(theme):
    """The six apps in a row: icon, name, and "like <counterpart>" beneath, outlined, for one GitHub theme."""
    ink, sub = THEMES[theme]
    o = outliner()
    width = 2 * LINEUP_PAD + 6 * LINEUP_ICON + 5 * LINEUP_GAP
    height = LINEUP_PAD + LINEUP_ICON + 70
    parts = []
    for i, key in enumerate(d.APPS):
        x = LINEUP_PAD + i * (LINEUP_ICON + LINEUP_GAP)
        centre = x + LINEUP_ICON / 2
        name, counterpart = d.APPS[key][0], f"like {d.APPS[key][1]}"
        parts.append(_nested(key, x, LINEUP_PAD, LINEUP_ICON))
        nw, cw = o.path(name, 24, 600)[1], o.path(counterpart, 17, 400)[1]
        parts.append(f'<path d="{o.path(name, 24, 600, centre - nw / 2, LINEUP_PAD + LINEUP_ICON + 34)[0]}" fill="{ink}"/>')
        parts.append(f'<path d="{o.path(counterpart, 17, 400, centre - cw / 2, LINEUP_PAD + LINEUP_ICON + 60)[0]}" '
                     f'fill="{sub}"/>')
    canvas = GITHUB_CANVAS[theme]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">'
            f'<!-- Contrast on the GitHub {theme} canvas ({canvas}): names {d.contrast(ink, canvas):.2f}:1, '
            f'counterparts {d.contrast(sub, canvas):.2f}:1 --><title>Rizonesoft Office apps</title>'
            f'{"".join(parts)}</svg>\n')
