# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Shape text with HarfBuzz and emit it as SVG path data, so brand artwork never depends on installed fonts."""
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parents[2]
BRAND_FONT = ROOT / "design" / "fonts" / "plus-jakarta-sans" / "PlusJakartaSans[wght].ttf"


def _num(v):
    text = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


class Outliner:
    def __init__(self, font_path=BRAND_FONT):
        self.face = hb.Face(hb.Blob.from_file_path(str(font_path)))
        self.upem = self.face.upem

    def path(self, text, size, weight, x=0.0, baseline=0.0, tracking=0.0):
        """Return (svg path data, advance width) for text set at size (px) and weight, starting at x on baseline.

        tracking is extra space in px added after every glyph except the last. Kerning and ligatures come from the font.
        """
        font = hb.Font(self.face)
        font.set_variations({"wght": weight})
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, {"kern": True, "liga": True})
        scale = size / self.upem
        pen = SVGPathPen(None, ntos=_num)
        cursor = 0.0
        count = len(buf.glyph_infos)
        for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
            ox = x + cursor + pos.x_offset * scale
            oy = baseline - pos.y_offset * scale
            font.draw_glyph_with_pen(info.codepoint, TransformPen(pen, (scale, 0, 0, -scale, ox, oy)))
            cursor += pos.x_advance * scale + (tracking if i < count - 1 else 0)
        return pen.getCommands(), cursor
