"""scripts/build-icons.py and scripts/lib/icon_design.py: tiers, packers, verification and the glass pane base."""
import importlib.util
import io
from pathlib import Path
import struct
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import icon_design as d

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


class GlassPane(unittest.TestCase):
    def pane_pixel(self, icon, background):
        data = build_icons.render(d.icon_svg(icon, "lg"), 128, background)
        return Image.open(io.BytesIO(data)).convert("RGB").getpixel((100, 96))

    def test_large_pane_looks_the_same_on_any_background(self):
        # (100, 96) is inside the pane of every icon and clear of the orb, the dark block, the symbol and the corners.
        for icon in [d.SUITE, *d.APPS]:
            on_black, on_white = self.pane_pixel(icon, "#000000"), self.pane_pixel(icon, "#ffffff")
            self.assertLessEqual(max(abs(a - b) for a, b in zip(on_black, on_white)), 6, icon)


if __name__ == "__main__":
    unittest.main()
