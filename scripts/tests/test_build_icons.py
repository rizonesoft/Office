# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/build-icons.py and scripts/lib/icon_design.py: tiers, packers, verification and the glass pane base."""
import importlib.util
import io
import json
from pathlib import Path
import re
import struct
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import icon_design as d
import filetype_design as ft
import brand_design as bd

spec = importlib.util.spec_from_file_location("build_icons", SCRIPTS / "build-icons.py")
build_icons = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_icons)

from PIL import Image


def png(px, color=(10, 20, 30, 255)):
    buf = io.BytesIO()
    Image.new("RGBA", (px, px), color).save(buf, "PNG")
    return buf.getvalue()


class Tiers(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual([d.tier_for(p) for p in (16, 24, 31, 32, 40, 47, 48, 1024)],
                         ["sm", "sm", "sm", "md", "md", "md", "lg", "lg"])

    def test_svg_is_deterministic_and_self_contained(self):
        for icon in [d.SUITE, *d.APPS]:
            for tier in d.TIERS:
                a, b = d.icon_svg(icon, tier), d.icon_svg(icon, tier)
                self.assertEqual(a, b)
                self.assertNotIn("<image", a)
                self.assertNotIn("<script", a)
                self.assertNotIn('href="http', a)

    def test_unknown_inputs_refused(self):
        with self.assertRaises(ValueError):
            d.icon_svg("word", "lg")
        with self.assertRaises(ValueError):
            d.icon_svg("write", "xl")


class Packers(unittest.TestCase):
    def test_ico_round_trip(self):
        data = build_icons.pack_ico([(16, png(16)), (32, png(32)), (256, png(256))])
        self.assertEqual(data[:6], struct.pack("<HHH", 0, 1, 3))
        self.assertEqual(data[6 + 32], 0)  # 256 px is stored as 0 in the directory
        self.assertEqual(set(Image.open(io.BytesIO(data)).info["sizes"]), {(16, 16), (32, 32), (256, 256)})

    def test_icns_header_and_largest_image(self):
        data = build_icons.pack_icns([("icp4", png(16)), ("ic08", png(256))])
        self.assertEqual(data[:4], b"icns")
        self.assertEqual(struct.unpack(">I", data[4:8])[0], len(data))
        img = Image.open(io.BytesIO(data))
        img.load()
        self.assertEqual(img.size, (256, 256))

    def test_verify_reports_wrong_size_and_bad_ico(self):
        problems = build_icons.verify({"assets/icons/png/write/write-16.png": png(32),
                                       "assets/icons/windows/write.ico": build_icons.pack_ico([(16, png(16))])})
        self.assertTrue(any("write-16.png" in p and "is not 16x16" in p for p in problems))
        self.assertTrue(any("write.ico" in p and "sizes" in p for p in problems))


class FileTypes(unittest.TestCase):
    def test_badge_uses_large_drawing_only_from_40_px(self):
        # The badge is 68/128 of a large file icon: 40 px at 75.3 px, 32 px at 60.2 px.
        self.assertEqual([ft.variant_for(p) for p in (16, 31, 32, 47, 48, 60, 61, 75, 76, 256)],
                         ["sm", "sm", "md", "md", "lg-badge-sm", "lg-badge-sm", "lg-badge-md", "lg-badge-md", "lg", "lg"])

    def test_variant_embeds_matching_app_drawing(self):
        self.assertIn("write-md-", ft.filetype_svg("docx", "lg-badge-md"))
        self.assertIn("write-sm-", ft.filetype_svg("docx", "lg-badge-sm"))
        self.assertIn("write-lg-", ft.filetype_svg("docx", "lg"))

    def test_labels_are_outlined_and_types_marked(self):
        docm = ft.filetype_svg("docm", "lg")
        self.assertNotIn("<text", docm)
        self.assertIn("#f59f0b", docm)  # macro mark
        self.assertIn("stroke-dasharray", ft.filetype_svg("dotx", "lg"))
        self.assertNotIn("#f59f0b", ft.filetype_svg("docx", "lg"))

    def test_verify_refuses_live_text(self):
        problems = build_icons.verify({"design/icons/files/x-lg.svg": b'<svg><text>DOCX</text></svg>'})
        self.assertTrue(any("live text" in p for p in problems))


class Brand(unittest.TestCase):
    def test_wordmark_and_lockups_are_outlined_whole_unit_canvases(self):
        for text in [bd.wordmark_svg("light"), bd.lockup_svg(d.SUITE, "dark"), bd.lockup_svg("grid", "light")]:
            self.assertNotIn("<text", text)
            width = text.split('viewBox="0 0 ', 1)[1].split()[0]
            self.assertTrue(width.isdigit(), width)

    def test_kerning_is_applied(self):
        from text_outline import Outliner
        o = Outliner()
        self.assertNotAlmostEqual(o.path("AV", 40, 700)[1], o.path("A", 40, 700)[1] + o.path("V", 40, 700)[1], places=2)


class GlassPane(unittest.TestCase):
    def pane_pixel(self, icon, background):
        data = build_icons.render(d.icon_svg(icon, "lg"), 128, background=background)
        return Image.open(io.BytesIO(data)).convert("RGB").getpixel((100, 96))

    def test_large_pane_looks_the_same_on_any_background(self):
        # (100, 96) is inside the pane of every icon and clear of the orb, the dark block, the symbol and the corners.
        for icon in [d.SUITE, *d.APPS]:
            on_black, on_white = self.pane_pixel(icon, "#000000"), self.pane_pixel(icon, "#ffffff")
            self.assertLessEqual(max(abs(a - b) for a, b in zip(on_black, on_white)), 6, icon)


STROKE_WEIGHT = {"lg": (4.9, 9.1), "md": (8, 12), "sm": (11, 15)}  # symbol stroke widths per tier, in units


def render_rgb(svg):
    return Image.open(io.BytesIO(build_icons.render(svg, 128, background="#ffffff"))).convert("RGB")


class Palette(unittest.TestCase):
    def test_contrast_matches_wcag_reference_values(self):
        self.assertAlmostEqual(d.contrast("#000000", "#ffffff"), 21.0, places=6)
        self.assertAlmostEqual(d.contrast("#767676", "#ffffff"), 4.54, places=2)

    def test_app_colours_reach_3_to_1_on_light_and_dark(self):
        self.assertEqual(set(d.APP_COLOR), set(d.APPS))
        for key, color in [*d.APP_COLOR.items(), (d.SUITE, d.SUITE_TINT)]:
            for background in ("#ffffff", "#1f1f1f"):
                self.assertGreaterEqual(d.contrast(color, background), 3, (key, background))

    def test_exported_accent_is_the_app_colour(self):
        exported = json.loads((SCRIPTS.parent / "assets/icons/palette.json").read_text(encoding="utf-8"))["apps"]
        for key, (_, _, (light, dark)) in d.APPS.items():
            self.assertEqual((exported[key]["accent"], exported[key]["light"], exported[key]["dark"]),
                             (d.APP_COLOR[key], light, dark), key)

    def test_app_colour_lies_on_its_gradient(self):
        for key, color in d.APP_COLOR.items():
            light, dark = d.APPS[key][2]
            self.assertIn(color, {d.mix(light, dark, i / 100) for i in range(101)}, key)

    def test_symbols_use_a_closed_vocabulary(self):
        # What lets the rendered tests sample by colour and trust the box: a symbol is plain rects, circles and paths
        # with absolute coordinates inside its 64-unit box, painted only in the symbol colour, with nothing that could
        # fade, move or hide a part (no opacity, transform, style, filter, clip or mask). The one other paint is the
        # white flap on Mail's solid small envelope, held to 3:1 against the envelope.
        col = "#123456"
        allowed = {"rect": {"x", "y", "width", "height", "rx"}, "circle": {"cx", "cy", "r"}, "path": {"d"}}
        paint = {"fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin"}
        for key in d.APPS:
            for tier in d.TIERS:
                svg = d.glyph(key, tier, col)
                elements = re.findall(r"<(\w+)((?:\s+[\w-]+=\"[^\"]*\")*)\s*/>", svg)
                self.assertEqual("".join(f"<{n}{a}/>" for n, a in elements).replace(" ", ""), svg.replace(" ", ""),
                                 (key, tier))
                flaps = 0
                for name, attrs in elements:
                    pairs = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))
                    self.assertLessEqual(set(pairs), allowed.get(name, set()) | paint, (key, tier, name))
                    self.assertIn("fill", pairs, (key, tier, name))  # an unstated fill would paint black
                    paints = (pairs.get("fill", "none"), pairs.get("stroke", "none"))
                    if (key, tier) == ("mail", "sm") and paints == ("none", "#ffffff") and name == "path":
                        # The flap: one white stroked path, whose surface test_mail_flap_sits_on_the_envelope checks.
                        flaps += 1
                        symbol = d.mix(d.APPS[key][2][1], "#000000", .15)
                        self.assertGreaterEqual(d.contrast("#ffffff", symbol), 3)
                    else:
                        self.assertLessEqual(set(paints), {col, "none"}, (key, tier, name))
                    if paints[1] != "none":
                        # The documented weights (docs/brand/icon-language.md, Accessibility); the flap is 8.
                        low, high = (8, 8) if paints[1] == "#ffffff" else STROKE_WEIGHT[tier]
                        self.assertTrue(low <= float(pairs["stroke-width"]) <= high, (key, tier, name, pairs))
                    if name == "rect":
                        x, y, w, h = (float(pairs[a]) for a in ("x", "y", "width", "height"))
                        edges = [x, y, x + w, y + h]
                        if paints[0] != "none":
                            self.assertGreaterEqual(min(w, h), 16, (key, tier, name, pairs))
                    elif name == "circle":
                        cx, cy, r = (float(pairs[a]) for a in ("cx", "cy", "r"))
                        edges = [cx - r, cy - r, cx + r, cy + r]
                        if paints[0] != "none":
                            self.assertGreaterEqual(r, 8, (key, tier, name, pairs))
                    else:
                        # Paths are strokes only, so the stroke weights above bound them; a filled shape is a rect or
                        # circle, whose minimum size is checked.
                        self.assertEqual(paints[0], "none", (key, tier, pairs))
                        self.assertRegex(pairs["d"], r"^[MLHVZ0-9.,\s-]+$", (key, tier))
                        edges = [float(v) for v in re.findall(r"-?[\d.]+", pairs["d"])]
                    self.assertTrue(all(-32 <= v <= 32 for v in edges), (key, tier, name, edges))
                self.assertEqual(flaps, 1 if (key, tier) == ("mail", "sm") else 0, (key, tier))

    def test_mail_flap_sits_on_the_envelope(self):
        # The flap is held to 3:1 against the envelope, so every pixel it changes must have the envelope under it.
        real = d.glyph
        symbol = d.mix(d.APPS["mail"][2][1], "#000000", .15)
        rgb = tuple(int(symbol[i:i + 2], 16) for i in (1, 3, 5))
        drawn = render_rgb(d.icon_svg("mail", "sm"))
        try:
            d.glyph = lambda *a: re.sub(r'<path stroke="#ffffff"[^>]*/>', "", real(*a))
            plain = render_rgb(d.icon_svg("mail", "sm"))
        finally:
            d.glyph = real
        grid = [(x, y) for y in range(128) for x in range(128)]
        flap = [xy for xy in grid if drawn.getpixel(xy) != plain.getpixel(xy)]
        self.assertGreater(len(flap), 100)
        self.assertEqual({plain.getpixel(xy) for xy in flap}, {rgb})

    def test_every_symbol_part_shows(self):
        # Each part of each symbol rendered on its own, so a part made too thin or small to see cannot hide behind the
        # rest: at least 100 pixels fully in the symbol colour (the smallest real part has 254), each at 3:1 or more
        # against the icon without its symbol at md and sm. Mail's flap has its own test.
        real = d.glyph
        for key in d.APPS:
            symbol = d.mix(d.APPS[key][2][1], "#000000", .15)
            rgb = tuple(int(symbol[i:i + 2], 16) for i in (1, 3, 5))
            for tier in d.TIERS:
                try:
                    d.glyph = lambda *_: ""
                    bare = render_rgb(d.icon_svg(key, tier))
                    parts = re.findall(r"<\w+[^>]*/>", real(key, tier, symbol))
                    for part in (p for p in parts if 'stroke="#ffffff"' not in p):
                        d.glyph = lambda *_, part=part: part
                        alone = render_rgb(d.icon_svg(key, tier))
                        painted = [xy for xy in ((x, y) for y in range(128) for x in range(128))
                                   if alone.getpixel(xy) == rgb]
                        self.assertGreaterEqual(len(painted), 100, (key, tier, part))
                        if tier != "lg":
                            worst = min(d.contrast(symbol, "#%02x%02x%02x" % bare.getpixel(xy)) for xy in painted)
                            self.assertGreaterEqual(worst, 3, (key, tier, part))
                finally:
                    d.glyph = real

    def test_small_symbols_reach_3_to_1_on_what_is_behind_them(self):
        # Rendered, not computed: each pixel drawn fully in the symbol colour (antialiased edges excluded) against the
        # same pixel with the symbol left out. The lg symbols cross the blurred orb and block; their contrast is the
        # owner's call at D01 T02 section 7.
        real = d.glyph
        for key in d.APPS:
            symbol = d.mix(d.APPS[key][2][1], "#000000", .15)
            rgb = tuple(int(symbol[i:i + 2], 16) for i in (1, 3, 5))
            for tier in ("md", "sm"):
                drawn = render_rgb(d.icon_svg(key, tier))
                try:
                    d.glyph = lambda *_: ""
                    bare = render_rgb(d.icon_svg(key, tier))
                finally:
                    d.glyph = real
                grid = [(x, y) for y in range(128) for x in range(128)]
                pairs = [(drawn.getpixel(xy), bare.getpixel(xy)) for xy in grid]
                pairs = [(s, b) for s, b in pairs if s != b]
                self.assertGreater(len(pairs), 500, (key, tier))
                self.assertIn(rgb, {s for s, _ in pairs}, (key, tier))
                worst = min(d.contrast("#%02x%02x%02x" % s, "#%02x%02x%02x" % b) for s, b in pairs if s == rgb)
                self.assertGreaterEqual(worst, 3, (key, tier))


class Keylines(unittest.TestCase):
    def test_sheet_draws_the_icon_constants(self):
        svg = d.keylines_svg()
        for i, tier in enumerate(d.TIERS):
            px, py, pw, ph, prx = d.APP_PANE[tier]
            self.assertIn(f'x="{d.n(i * 144 + px)}" y="{d.n(py)}" width="{d.n(pw)}" height="{d.n(ph)}" '
                          f'rx="{d.n(prx)}"', svg, tier)
            cx, cy, r = d.APP_ORB[tier]
            self.assertIn(f'cx="{d.n(i * 144 + cx)}" cy="{d.n(cy)}" r="{d.n(r)}"', svg, tier)

    def test_every_shape_is_placed_on_the_canvas(self):
        # The geometry itself, so a shape moved far enough to miss the rendered check below still fails.
        def inside(x0, y0, x1, y1):
            return 0 <= x0 <= x1 <= 128 and 0 <= y0 <= y1 <= 128
        for tier in d.TIERS:
            px, py, pw, ph, _ = d.APP_PANE[tier]
            cx, cy, r = d.APP_ORB[tier]
            gx, gy, gs = d.APP_GLYPH_AT[tier]
            self.assertTrue(inside(px, py, px + pw, py + ph), ("pane", tier))
            self.assertTrue(inside(cx - r, cy - r, cx + r, cy + r), ("orb", tier))
            self.assertTrue(inside(gx - 32 * gs, gy - 32 * gs, gx + 32 * gs, gy + 32 * gs), ("symbol box", tier))
        bx, by, bw, bh, _ = d.APP_BLOCK
        self.assertTrue(inside(bx, by, bx + bw, by + bh), "block")

    def test_every_symbol_stays_in_its_box(self):
        # Each symbol rendered alone: finely, inside its 64-unit box, and coarsely on a canvas 128 times as wide, so a
        # part moved anywhere off the icon still shows.
        for key in d.APPS:
            for tier in d.TIERS:
                for half, px in ((64, 512), (4096, 1024)):
                    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-half} {-half} {2 * half} {2 * half}" '
                           f'width="{px}" height="{px}">{d.glyph(key, tier, "#000000")}</svg>')
                    alpha = Image.open(io.BytesIO(build_icons.render(svg, px))).getchannel("A")
                    box = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
                    self.assertIsNotNone(box, (key, tier))
                    unit = 2 * half / px
                    x0, y0, x1, y1 = (v * unit - half for v in box)
                    self.assertTrue(-32 - unit <= min(x0, y0) and max(x1, y1) <= 32 + unit, (key, tier, half, box))

    def test_every_drawing_fits_the_canvas(self):
        # Rendered on a canvas three times the size, so a shape, stroke or shadow past the edge shows, not clipped.
        for icon in [d.SUITE, *d.APPS]:
            for tier in d.TIERS:
                svg = d.icon_svg(icon, tier).replace('viewBox="0 0 128 128" width="128" height="128"',
                                                     'viewBox="-128 -128 384 384" width="384" height="384"', 1)
                alpha = Image.open(io.BytesIO(build_icons.render(svg, 384))).getchannel("A")
                x0, y0, x1, y1 = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
                self.assertTrue(128 <= x0 and 128 <= y0 and x1 <= 256 and y1 <= 256, (icon, tier, x0, y0, x1, y1))

    def test_committed_sheet_is_current(self):
        # A full build takes most of a minute; build-icons --check in CI covers the registration, this the content.
        committed = (SCRIPTS.parent / "design/icons/keylines.svg").read_text(encoding="utf-8")
        self.assertEqual(committed, d.keylines_svg())


if __name__ == "__main__":
    unittest.main()
