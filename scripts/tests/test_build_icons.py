# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/build-icons.py and scripts/lib/icon_design.py: tiers, packers, verification and the glass pane base."""
import contextlib
import importlib.util
import io
import json
import math
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

    def test_verify_decodes_every_entry_and_parses_svg(self):
        # Same-length damage to the first entry, which Pillow does not open (it opens the largest), so only the
        # per-entry decoding can catch it.
        signature = b"\x89PNG\r\n\x1a\n"
        ico = build_icons.pack_ico([(px, png(px)) for px in build_icons.ICO_SIZES])
        broken_ico = ico.replace(signature, b"BROKEN!!", 1)
        icns = build_icons.pack_icns([("ic07", png(128)), ("ic10", png(1024))])
        broken_icns = icns.replace(signature, b"BROKEN!!", 1)
        self.assertEqual((len(broken_ico), len(broken_icns)), (len(ico), len(icns)))
        self.assertEqual(build_icons.verify({"assets/icons/windows/write.ico": ico}), [])
        for rel, data in (("assets/icons/windows/write.ico", broken_ico),
                          ("assets/icons/macos/write.icns", broken_icns),
                          ("design/icons/apps/write-lg.svg", b"not an SVG"),
                          ("design/icons/apps/write-sm.svg", b'<html xmlns="http://www.w3.org/1999/xhtml"/>')):
            self.assertTrue(build_icons.verify({rel: data}), rel)

    def test_build_rasterises_apps_from_the_selected_drawing(self):
        # The real build() with a stand-in renderer that tags each output with the drawing and size it was given.
        real = build_icons.render
        tags = {}

        def fake(svg, width, height=None, background=None):
            tag = tags.setdefault((svg, width), len(tags))
            return png(1) + f"tag{tag}".encode()
        build_icons.render = fake
        try:
            out = build_icons.build()
        finally:
            build_icons.render = real
        for key in d.APPS:
            for px in (16, 24, 32):
                want = png(1) + f"tag{tags[(d.pixel_svg(key, px), px)]}".encode()
                self.assertEqual(out[f"assets/icons/png/{key}/{key}-{px}.png"], want, (key, px))
                self.assertIn(want, out[f"assets/icons/windows/{key}.ico"], (key, px))
            at_2x = png(1) + f"tag{tags[(d.pixel_svg(key, 16), 32)]}".encode()  # the 16 pt @2x slot
            self.assertIn(b"ic11" + struct.pack(">I", len(at_2x) + 8) + at_2x, out[f"assets/icons/macos/{key}.icns"])
            tier = png(1) + f"tag{tags[(d.icon_svg(key, 'sm'), 20)]}".encode()
            self.assertEqual(out[f"assets/icons/png/{key}/{key}-20.png"], tier, key)

    def test_drawing_for_picks_the_variant_only_at_its_sizes(self):
        for key in d.APPS:
            for px in (16, 24, 32):
                self.assertEqual(d.drawing_for(key, px), d.pixel_svg(key, px))
            for px in (20, 22, 40, 48, 256):
                self.assertEqual(d.drawing_for(key, px), d.icon_svg(key, d.tier_for(px)))
        self.assertEqual(d.drawing_for(d.SUITE, 16), d.icon_svg(d.SUITE, "sm"))  # the suite has no variants


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

    def test_every_type_the_plan_names_is_drawn_and_marked_by_kind(self):
        # The 26 types of todo/01-brand/TODO-02-icon-system.md section 5; Plan's native format waits on its extension
        # (D03 T01 section 5).
        named = ("docx docm dotx doc rtf odt xlsx xlsm xltx xls csv ods pptx pptm potx ppt odp vsdx vsdm vstx mpp mpt "
                 "eml msg ics vcf").split()
        self.assertEqual(list(ft.TYPES), named)
        # The kinds as the owner decided them (the section's context), written out here rather than read from TYPES,
        # so a wrong classification in the generator cannot pass.
        macro, template = {"docm", "xlsm", "pptm", "vsdm"}, {"dotx", "xltx", "potx", "vstx", "mpt"}
        plain = {"rtf", "csv"}
        for ext in named:
            for variant in ("lg", "lg-badge-md", "lg-badge-sm", "md", "sm"):
                svg = ft.filetype_svg(ext, variant)
                committed = (SCRIPTS.parent / f"design/icons/files/{ext}-{variant}.svg").read_text(encoding="utf-8")
                self.assertEqual(committed, svg, (ext, variant))
                self.assertEqual("#f59f0b" in svg, ext in macro, (ext, variant))  # the amber macro mark
                self.assertEqual("stroke-dasharray" in svg, ext in template, (ext, variant))  # the dashed page
                if variant != "sm":  # the 16 px page has no content hint
                    self.assertEqual("#c3cad6" in svg, ext in plain, (ext, variant))  # the grey hint

    def test_macro_mark_shows_at_every_size(self):
        # Rendered at the size each drawing is shown, so a mark moved off the page or hidden still fails.
        def amber_pixels(svg, px):
            rgb = Image.open(io.BytesIO(build_icons.render(svg, px, background="#ffffff"))).convert("RGB").tobytes()
            return sum(1 for i in range(0, len(rgb), 3)
                       if abs(rgb[i] - 245) < 30 and abs(rgb[i + 1] - 159) < 30 and rgb[i + 2] < 60)
        # Each drawing's shown size and the mark radius it must keep, in 128-unit canvas units; at least half the
        # mark's area must render amber (the rest is the white exclamation and antialiasing).
        for variant, px, radius in (("lg", 128, 10), ("lg-badge-md", 64, 10), ("lg-badge-sm", 48, 10), ("md", 32, 16),
                                    ("sm", 16, 22)):
            least = math.pi * (radius * px / 128) ** 2 / 2
            for ext in ("docm", "xlsm", "pptm", "vsdm"):
                self.assertGreaterEqual(amber_pixels(ft.filetype_svg(ext, variant), px), least, (ext, variant))
            self.assertEqual(amber_pixels(ft.filetype_svg("docx", variant), px), 0, variant)

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


class Checkout(unittest.TestCase):
    def test_every_managed_folder_keeps_lf_on_checkout(self):
        # --check compares bytes, so a folder Git may rewrite to CRLF on a Windows checkout fails CI.
        import subprocess
        probes = [f"{folder.as_posix()}/probe.svg" for folder in build_icons.MANAGED]
        attrs = subprocess.run(["git", "check-attr", "eol", "--", *probes], cwd=SCRIPTS.parent, capture_output=True,
                               text=True, check=True).stdout.splitlines()
        self.assertEqual(attrs, [f"{p}: eol: lf" for p in probes])


class Banner(unittest.TestCase):
    def test_banners_are_current_outlined_and_within_budget(self):
        root = SCRIPTS.parent
        for theme in ("light", "dark"):
            svg = bd.banner_svg(theme)
            self.assertEqual((root / f"design/github/banner-{theme}.svg").read_text(encoding="utf-8"), svg)
            self.assertIn('viewBox="0 0 1280 320"', svg)
            self.assertNotIn("<text", svg)
            data = (root / f"docs/assets/github/banner-{theme}.png").read_bytes()
            self.assertEqual(Image.open(io.BytesIO(data)).size, (2560, 640), theme)
            self.assertLess(len(data), 500_000, theme)

    def test_text_reads_on_what_is_rendered_behind_it(self):
        # Rendered, so any layer between the card and the text counts: each text line drawn alone over the banner
        # without its text, on GitHub's canvas, and every pixel fully in the line's colour held to 4.5:1 against
        # the same pixel with no text.
        for theme, canvas in (("light", "#ffffff"), ("dark", "#0d1117")):
            svg = bd.banner_svg(theme)
            # The text lines are the paths after the mark's closing tag; everything else stays where it is, so a
            # layer anywhere (under the text or over it) is rendered in both images.
            tail = svg.rpartition("</svg>")[0].rpartition("</svg>")[2]
            lines = re.findall(r'<path d="[^"]*" fill="[^"]*"/>', tail)
            self.assertEqual(len(lines), 4, theme)  # wordmark, product name, tagline, app names
            for line, glyphs, worst in text_contrast(svg, lines, canvas, 1280, 320):
                self.assertGreater(glyphs, 200, (theme, line[-30:]))
                self.assertGreaterEqual(worst, 4.5, (theme, line[-30:]))

    def test_tagline_contrast_is_recorded_and_holds(self):
        # Read from the drawn file itself: the four text paths after the mark (wordmark, product, tagline, app line)
        # and the card's gradient stops, against GitHub's canvas, written out here (white, and #0d1117 for dark).
        for theme, canvas in (("light", "#ffffff"), ("dark", "#0d1117")):
            svg = bd.banner_svg(theme)
            gradient = re.findall(r'<linearGradient id="([^"]+)"', svg.split("</defs>")[0])
            grounds = re.findall(r'<stop offset="[01]" stop-color="(#[0-9a-f]{6})"/>', svg.split("</defs>")[0])
            self.assertEqual((len(gradient), len(grounds)), (1, 2), theme)
            # The card, the first shape after the definitions and under all the text, is painted with that gradient.
            card = re.match(r'<rect [^>]*fill="([^"]+)"', svg.split("</defs>", 1)[1])
            self.assertEqual(card and card.group(1), f"url(#{gradient[0]})", theme)
            grounds.append(canvas)
            fills = re.findall(r'<path d="[^"]*" fill="([^"]*)"/>', svg.rsplit("</svg>", 2)[1])
            self.assertEqual(len(fills), 4, theme)
            self.assertTrue(all(re.fullmatch(r"#[0-9a-f]{6}", f) for f in fills), fills)
            tagline = min(d.contrast(fills[2], g) for g in grounds)
            worst = min(d.contrast(f, g) for f in fills for g in grounds)
            self.assertGreaterEqual(worst, 4.5, theme)
            recorded = [float(v) for v in re.findall(r"at least ([\d.]+):1", svg)]
            self.assertEqual(recorded, [round(tagline, 2), round(worst, 2)], theme)


class SocialPreview(unittest.TestCase):
    def test_current_and_within_budget(self):
        root = SCRIPTS.parent
        svg = bd.social_preview_svg()
        self.assertEqual((root / "design/github/social-preview.svg").read_text(encoding="utf-8"), svg)
        self.assertNotIn("<text", svg)
        data = (root / "docs/assets/github/social-preview.png").read_bytes()
        self.assertEqual(Image.open(io.BytesIO(data)).size, (1280, 640))
        self.assertLess(len(data), 1_000_000)

    def test_content_stays_inside_the_40_pixel_margin(self):
        # Rendered with the card made empty, on a canvas three times the size, so anything near or past an edge
        # shows instead of being clipped.
        svg = bd.social_preview_svg()
        card = re.search(r'<rect id="card"[^>]*/>', svg).group(0)
        bare = svg.replace(card, "").replace('viewBox="0 0 1280 640" width="1280" height="640"',
                                             'viewBox="-1280 -640 3840 1920" width="3840" height="1920"', 1)
        alpha = Image.open(io.BytesIO(build_icons.render(bare, 3840, 1920))).getchannel("A")
        x0, y0, x1, y1 = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
        self.assertTrue(1280 + 40 <= x0 and 640 + 40 <= y0 and x1 <= 2560 - 40 and y1 <= 1280 - 40, (x0, y0, x1, y1))

    def test_every_app_and_the_suite_name_are_shown(self):
        svg = bd.social_preview_svg()
        for key in d.APPS:
            self.assertIn(f'id="{key}-lg-g1"', svg, key)  # each app's large icon
        self.assertIn('id="rizonesoft-office-lg-o1"', svg)  # the suite mark
        # The outlined text, written out here: each top-level path (outside the nested icons) rendered alone must be
        # as wide as its text set in the brand face, in this order.
        texts = [("Rizonesoft", 88, 700, bd.TRACK * 2), ("Office", 88, 400, bd.TRACK * 2),
                 ("The open-source office suite for Windows.", 36, 500, 0)]
        texts += [(name, 26, 600, 0) for name in ("Write", "Grid", "Stage", "Flow", "Plan", "Mail")]
        top = re.sub(r"<svg x=.*?</svg>", "", svg.split("</defs>", 1)[1], flags=re.S)
        paths = re.findall(r'<path d="[^"]+" fill="#[0-9a-f]{6}"/>', top)
        self.assertEqual(len(paths), len(texts))
        for path, (text, size, weight, track) in zip(paths, texts):
            # The glyph outlines must be the literal text's, up to where the line was placed.
            self.assertTrue(same_outline(re.search(r'd="([^"]+)"', path).group(1), text, size, weight, track), text)


class Lineup(unittest.TestCase):
    def names_from_the_record(self):
        # The six full names and counterparts as docs/brand/NAMES.md's Apps table records them, read from the file.
        text = (SCRIPTS.parent / "docs/brand/NAMES.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| (\w+) \| Rizonesoft \1 \| (\w+) \|$", text, flags=re.M)
        self.assertEqual(len(rows), 6)
        return rows

    def test_current_and_within_budget(self):
        root = SCRIPTS.parent
        for theme in ("light", "dark"):
            svg = bd.lineup_svg(theme)
            self.assertEqual((root / f"design/github/lineup-{theme}.svg").read_text(encoding="utf-8"), svg)
            self.assertNotIn("<text", svg)
            data = (root / f"docs/assets/github/lineup-{theme}.png").read_bytes()
            w, h = (int(v) for v in svg.split('viewBox="0 0 ', 1)[1].split('"', 1)[0].split())
            self.assertEqual(Image.open(io.BytesIO(data)).size, (2 * w, 2 * h), theme)
            self.assertLess(len(data), 300_000, theme)

    def test_names_and_counterparts_match_the_record(self):
        rows = self.names_from_the_record()
        for theme in ("light", "dark"):
            svg = bd.lineup_svg(theme)
            top = re.sub(r"<svg x=.*?</svg>", "", svg.split("</title>", 1)[1], flags=re.S)
            paths = re.findall(r'<path d="([^"]+)" fill="#[0-9a-f]{6}"/>', top)
            self.assertEqual(len(paths), 12, theme)
            for (name, counterpart), shown, under in zip(rows, paths[0::2], paths[1::2]):
                self.assertTrue(same_outline(shown, name, 24, 600), (theme, name))
                self.assertTrue(same_outline(under, f"like {counterpart}", 17, 400), (theme, counterpart))

    def test_six_icons_in_order_at_96_units_and_visible(self):
        rows = self.names_from_the_record()
        for theme in ("light", "dark"):
            svg = bd.lineup_svg(theme)
            icons = re.findall(r'<svg x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" '
                               r'viewBox="0 0 128 128">(.*?)</svg>', svg, flags=re.S)
            self.assertEqual(len(icons), 6, theme)
            w, h = (int(v) for v in svg.split('viewBox="0 0 ', 1)[1].split('"', 1)[0].split())
            alpha = Image.open(io.BytesIO(build_icons.render(svg, w, h))).getchannel("A")
            for (name, _), (x, y, iw, ih, inner) in zip(rows, icons):
                self.assertEqual((float(iw), float(ih)), (96, 96), (theme, name))
                self.assertIn(f'id="{name.lower()}-lg-g1"', inner, (theme, name))  # that app's large drawing
                box = alpha.crop((int(float(x)), int(float(y)), int(float(x)) + 96, int(float(y)) + 96))
                covered = sum(1 for a in box.tobytes() if a > 200)
                self.assertGreater(covered, 96 * 96 // 2, (theme, name))  # it is drawn, not merely present
            # Laid out left to right without overlap, each icon centred over its own name.
            lefts = [float(x) for x, *_ in icons]
            self.assertTrue(all(b - a >= 96 for a, b in zip(lefts, lefts[1:])), (theme, lefts))
            top = re.sub(r"<svg x=.*?</svg>", "", svg.split("</title>", 1)[1], flags=re.S)
            names = re.findall(r'<path d="[^"]+" fill="#[0-9a-f]{6}"/>', top)[0::2]
            for (name, _), left, label in zip(rows, lefts, names):
                alone = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
                         f'height="{h}">{label}</svg>')
                x0, _, x1, _ = Image.open(io.BytesIO(build_icons.render(alone, w, h))).getchannel("A").getbbox()
                self.assertLess(abs((x0 + x1) / 2 - (left + 48)), 3, (theme, name))

    def test_text_reads_on_each_github_canvas(self):
        for theme, canvas in (("light", "#ffffff"), ("dark", "#0d1117")):
            svg = bd.lineup_svg(theme)
            w, h = (int(v) for v in svg.split('viewBox="0 0 ', 1)[1].split('"', 1)[0].split())
            top = re.sub(r"<svg x=.*?</svg>", "", svg.split("</title>", 1)[1], flags=re.S)
            lines = re.findall(r'<path d="[^"]+" fill="#[0-9a-f]{6}"/>', top)
            self.assertEqual(len(lines), 12, theme)
            results = text_contrast(svg, lines, canvas, w, h)
            for line, glyphs, worst in results:
                self.assertGreater(glyphs, 40, (theme, line[-30:]))
                self.assertGreaterEqual(worst, 4.5, (theme, line[-30:]))
            # The comment records the names' and counterparts' ratios on that canvas, recomputed here.
            recorded = [float(v) for v in re.findall(r"([\d.]+):1", svg.split("-->", 1)[0])]
            names = min(r for i, (_, _, r) in enumerate(results) if i % 2 == 0)
            unders = min(r for i, (_, _, r) in enumerate(results) if i % 2 == 1)
            self.assertEqual(recorded, [round(names, 2), round(unders, 2)], theme)


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


# Each tier's symbol shade as decided (docs/brand/icon-language.md, Palette), written out here rather than read from
# icon_design so a changed shade fails the tests.
SYMBOL_SHADE = {"lg": .35, "md": .15, "sm": .15}


def text_contrast(svg, lines, canvas, width, height):
    """The lowest contrast of each text line, rendered: every pixel the line alone covers fully (found on a
    transparent canvas, whatever its colour) in the finished image against the same pixel with no text, on the given
    canvas, so a layer under or over the text counts. Returns [(line, glyph pixels, lowest ratio)]."""
    def without(*drop):
        kept = svg
        for line in drop:
            kept = kept.replace(line, "", 1)
        return kept

    def rendered(text):
        data = build_icons.render(text, width, height, background=canvas)
        return Image.open(io.BytesIO(data)).convert("RGB").tobytes()
    bare, final, out = rendered(without(*lines)), rendered(svg), []
    for line in lines:
        alone = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" '
                 f'height="{height}">{line}</svg>')
        alpha = Image.open(io.BytesIO(build_icons.render(alone, width, height))).getchannel("A").tobytes()
        glyphs = [i for i, a in enumerate(alpha) if a == 255]
        worst = min((d.contrast("#" + final[3 * i:3 * i + 3].hex(), "#" + bare[3 * i:3 * i + 3].hex())
                     for i in glyphs), default=0)
        out.append((line, len(glyphs), worst))
    return out


def outline_points(path_data):
    """Every point an outline visits as (command, x, y), following M, L, Q, C, H and V, with each Z (a contour's
    end) kept as its own entry, so a changed command or contour fails as surely as a moved point."""
    out, x, y, cmd = [], 0.0, 0.0, None
    tokens = re.findall(r"[MLQCHVZ]|-?\d+(?:\.\d+)?", path_data)
    i = 0
    while i < len(tokens):
        if tokens[i].isalpha():
            cmd, i = tokens[i], i + 1
            if cmd == "Z":
                out.append(("Z", x, y))
            continue
        if cmd == "H":
            x, i = float(tokens[i]), i + 1
        elif cmd == "V":
            y, i = float(tokens[i]), i + 1
        else:
            x, y, i = float(tokens[i]), float(tokens[i + 1]), i + 2
        out.append((cmd, x, y))
    return out


def same_outline(path_data, text, size, weight, track=0.0):
    """True when an outlined line is the literal text set in the brand face, up to where it was placed."""
    got, want = outline_points(path_data), outline_points(bd.outliner().path(text, size, weight, 0, 0, track)[0])
    if [c for c, _, _ in got] != [c for c, _, _ in want]:
        return False
    dx, dy = got[0][1] - want[0][1], got[0][2] - want[0][2]
    return all(abs(gx - wx - dx) < .05 and abs(gy - wy - dy) < .05 for (_, gx, gy), (_, wx, wy) in zip(got, want))


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
                        symbol = d.mix(d.APPS[key][2][1], "#000000", SYMBOL_SHADE[tier])
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
        # against the icon without its symbol. Mail's flap has its own test.
        real = d.glyph
        for key in d.APPS:
            for tier in d.TIERS:
                symbol = d.mix(d.APPS[key][2][1], "#000000", SYMBOL_SHADE[tier])
                rgb = tuple(int(symbol[i:i + 2], 16) for i in (1, 3, 5))
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
                        worst = min(d.contrast(symbol, "#%02x%02x%02x" % bare.getpixel(xy)) for xy in painted)
                        self.assertGreaterEqual(worst, 3, (key, tier, part))
                finally:
                    d.glyph = real

    def test_symbols_reach_3_to_1_on_what_is_behind_them(self):
        # Rendered, not computed: each pixel drawn fully in the symbol colour (antialiased edges excluded) against the
        # same pixel with the symbol left out, at every tier (lg included since the owner's choice of 2026-10-22).
        real = d.glyph
        for key in d.APPS:
            for tier in d.TIERS:
                symbol = d.mix(d.APPS[key][2][1], "#000000", SYMBOL_SHADE[tier])
                rgb = tuple(int(symbol[i:i + 2], 16) for i in (1, 3, 5))
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


class AppMasters(unittest.TestCase):
    def test_counterpart_is_named_only_in_the_master_comment(self):
        for key, (_, counterpart, _) in d.APPS.items():
            for tier in d.TIERS:
                master = (SCRIPTS.parent / f"design/icons/apps/{key}-{tier}.svg").read_text(encoding="utf-8")
                self.assertEqual(master, d.app_master_svg(key, tier))
                self.assertEqual(re.findall(r"<!--(.*?)-->", master), [f" Counterpart: Microsoft {counterpart} "])
                self.assertNotIn("Microsoft", re.sub(r"<!--.*?-->", "", master), (key, tier))
                self.assertNotIn("Microsoft", d.icon_svg(key, tier), (key, tier))  # shipped icons never name it

    def test_contact_sheet_shows_each_app_at_each_size(self):
        sheet = Image.open(io.BytesIO(build_icons.contact_sheet())).convert("RGB")
        self.assertEqual(sheet.size, (16 + 6 * (256 + 16), 16 + (256 + 16) + (48 + 16) + (32 + 16)))
        y = 16
        for size in (256, 48, 32):
            for i, key in enumerate(d.APPS):
                cell = sheet.crop((16 + i * 272, y, 16 + i * 272 + size, y + size))
                want = Image.new("RGBA", (size, size), "white")
                # The committed raster at that size, so the sheet shows what ships.
                shipped = SCRIPTS.parent / f"assets/icons/png/{key}/{key}-{size}.png"
                want.alpha_composite(Image.open(shipped).convert("RGBA"))
                self.assertEqual(cell.tobytes(), want.convert("RGB").tobytes(), (size, key))
            y += size + 16

    def test_missing_rasteriser_is_a_setup_error(self):
        # The import itself fails, as it does where the package is not installed.
        saved = sys.modules.get("resvg_py")
        sys.modules["resvg_py"] = None
        try:
            with self.assertRaises(build_icons.SetupRequired):
                build_icons.rasteriser()
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(build_icons.main(["--check"]), 2)
            self.assertIn("setup required: resvg_py is not installed", err.getvalue())
        finally:
            if saved is None:
                sys.modules.pop("resvg_py", None)
            else:
                sys.modules["resvg_py"] = saved

    def test_contact_sheet_is_its_own_mode(self):
        with self.assertRaises(SystemExit) as refused, contextlib.redirect_stderr(io.StringIO()):
            build_icons.main(["--check", "--contact-sheet", "unused.png"])
        self.assertEqual(refused.exception.code, 2)  # argparse's usage error, not a success


class PixelVariants(unittest.TestCase):
    def shapes(self, svg):
        return [(name, dict(re.findall(r'([\w-]+)="([^"]*)"', attrs)))
                for name, attrs in re.findall(r"<(rect|circle|path)\b([^>]*)/>", svg.split("</defs>", 1)[1])]

    def test_app_rasters_use_the_variant_at_its_size(self):
        assets = SCRIPTS.parent / "assets/icons"
        for key in d.APPS:
            for px in (16, 24, 32):
                committed = (assets / f"png/{key}/{key}-{px}.png").read_bytes()
                self.assertEqual(committed, build_icons.render(d.pixel_svg(key, px), px), (key, px))
            # Sizes with no variant keep their tier's drawing.
            for px in (20, 40):
                committed = (assets / f"png/{key}/{key}-{px}.png").read_bytes()
                self.assertEqual(committed, build_icons.render(d.icon_svg(key, d.tier_for(px)), px), (key, px))
            # The macOS 16 pt @2x slot is the 16 px variant at 32 pixels.
            icns = (assets / f"macos/{key}.icns").read_bytes()
            want = build_icons.render(d.pixel_svg(key, 16), 32)
            self.assertIn(b"ic11" + struct.pack(">I", len(want) + 8) + want, icns, key)

    def test_committed_and_named(self):
        for key, (_, counterpart, _) in d.APPS.items():
            for size in (16, 24, 32):
                svg = d.pixel_svg(key, size)
                path = SCRIPTS.parent / f"design/icons/apps/{key}-{size}.svg"
                self.assertEqual(path.read_text(encoding="utf-8"), svg, (key, size))
                self.assertIn(f'viewBox="0 0 {size} {size}" width="{size}" height="{size}"', svg)
                self.assertEqual(re.findall(r"<!--(.*?)-->", svg), [f" Counterpart: Microsoft {counterpart} "])

    def test_every_edge_is_on_the_pixel_grid(self):
        # A stroke of odd width is centred on a half pixel, anything else lies on whole pixels.
        for key in d.APPS:
            for size in (16, 24, 32):
                shapes = self.shapes(d.pixel_svg(key, size))
                self.assertGreaterEqual(len(shapes), 5, (key, size))  # orb, pane, seen orb, rim and the symbol
                for name, a in shapes:
                    width = float(a.get("stroke-width", 0)) if a.get("stroke", "none") != "none" else 0
                    self.assertEqual(width, int(width), (key, size, a))
                    offset = .5 if int(width) % 2 else 0
                    if name == "rect":
                        x, y, w, h = (float(a[v]) for v in ("x", "y", "width", "height"))
                        values = [x - offset, y - offset, w, h]
                        extent = [x, y, x + w, y + h]
                        self.assertTrue(w > 0 and h > 0, (key, size, a))
                    elif name == "circle":
                        cx, cy, r = (float(a[v]) for v in ("cx", "cy", "r"))
                        values = [cx - r, cy - r, 2 * r]
                        extent = [cx - r, cy - r, cx + r, cy + r]
                        self.assertGreater(r, 0, (key, size, a))
                    else:
                        points = [float(v) for v in re.findall(r"-?[\d.]+", a["d"])]
                        values = [v - offset for v in points]
                        extent = points
                    self.assertTrue(all(v == int(v) for v in values), (key, size, name, a))
                    # Every edge, with half the stroke on either side, lies on the canvas.
                    self.assertTrue(all(width / 2 <= v <= size - width / 2 for v in extent), (key, size, name, a))

    def test_separate_shapes_stay_separate(self):
        # Filled shapes apart on the 128-unit drawing keep at least a pixel between them.
        for key in d.APPS:
            for size, tier in d.PIXEL_SIZES.items():
                filled = [a for name, a in self.shapes(d.pixel_svg(key, size)) if name == "rect" and a["fill"] != "none"
                          and "clip-path" not in a][1:]  # the first filled rect is the pane
                glyph = d.glyph(key, tier, "#000000")
                drawn = [a for name, a in re.findall(r"<(rect)\b([^>]*)/>", glyph)]
                self.assertEqual(len(filled), len([g for g in drawn if 'fill="#000000"' in g]), (key, size))
                boxes = [(float(a["x"]), float(a["y"]), float(a["x"]) + float(a["width"]),
                          float(a["y"]) + float(a["height"])) for a in filled]
                for i, p in enumerate(boxes):
                    for q in boxes[i + 1:]:
                        apart = p[2] < q[0] or q[2] < p[0] or p[3] < q[1] or q[3] < p[1]
                        self.assertTrue(apart, (key, size, p, q))


class MonoMark(unittest.TestCase):
    def test_one_paint_and_no_live_text(self):
        svg = d.suite_mono_svg()
        self.assertEqual(set(re.findall(r'fill="([^"]*)"', svg)), {"currentColor"})
        for paint in ("stroke", "style", "<style", "<text", "<image", "opacity"):  # no paint outside the fills
            self.assertNotIn(paint, svg)
        self.assertEqual(re.findall(r"<(\w+)", svg), ["svg", "title", "defs", "clipPath", "path", "circle", "path"])
        self.assertEqual((SCRIPTS.parent / "design/icons/suite/rizonesoft-office-mono.svg").read_text(encoding="utf-8"),
                         svg)

    def test_squares_are_knocked_out_and_orb_stands_clear_of_the_pane(self):
        # Rendered with no background, so a hole or the gap is see-through, not painted white.
        img = Image.open(io.BytesIO(build_icons.render(d.suite_mono_svg(), 128))).convert("RGBA")
        clear, solid = 0, (0, 0, 0, 255)
        px, py, pw, ph, _ = d.SUITE_PANE["md"]
        for x, y, s, _ in d._six_square_boxes(px + pw / 2, py + ph / 2, pw * d.SUITE_SQUARES_SHARE["md"]):
            self.assertEqual(img.getpixel((int(x + s / 2), int(y + s / 2)))[3], clear)  # each square is a hole
        self.assertEqual(img.getpixel((px + pw // 2, py + ph - 4)), solid)  # the pane is solid below the squares
        cx, cy, r = d.SUITE_ORB["md"]
        self.assertEqual(img.getpixel((cx, cy - r + 6)), solid)  # the orb above the pane
        self.assertEqual(img.getpixel((cx, py - d.MONO_GAP // 2 - 1))[3], clear)  # the gap between orb and pane
        self.assertEqual(img.getpixel((2, 126))[3], clear)  # and nothing behind the mark

    def test_every_shape_takes_the_given_colour(self):
        # An unset fill would paint black whatever colour the mark is given.
        svg = d.suite_mono_svg().replace("<svg ", '<svg color="#ff0000" ', 1)
        img = Image.open(io.BytesIO(build_icons.render(svg, 128))).convert("RGBA")
        px, py, pw, ph, _ = d.SUITE_PANE["md"]
        cx, cy, r = d.SUITE_ORB["md"]
        for xy in ((px + pw // 2, py + ph - 4), (cx, cy - r + 6)):  # the pane, then the orb
            self.assertEqual(img.getpixel(xy), (255, 0, 0, 255), xy)

if __name__ == "__main__":
    unittest.main()
