# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The campaign launchers' icons: the suite icon with the runner's badge in the corner (owner, 2026-11-12)."""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1]
SCRIPT = SCRIPTS / "campaign-icon.py"
spec = importlib.util.spec_from_file_location("campaign_icon", SCRIPT)
icon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(icon)

MARK = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
        '<rect x="3" y="3" width="4" height="4" fill="#000"/></svg>')


class CampaignIcon(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def render(self, *argv):
        return subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True, text=True, timeout=120)

    def badge_centre(self, size):
        full = size * icon.OVERSAMPLE
        radius = round(full * 0.24)
        return round((full - radius - max(1, round(full * 0.01))) / icon.OVERSAMPLE)

    def test_the_icon_holds_every_size_and_leaves_no_partial_file(self):
        target = self.dir / "a.ico"
        done = self.render(str(target), "#D97757")
        self.assertEqual(done.returncode, 0, done.stderr)
        with Image.open(target) as image:
            self.assertEqual(sorted(image.info["sizes"]), [(n, n) for n in icon.SIZES])
        self.assertEqual([p.name for p in self.dir.iterdir()], ["a.ico"])

    def test_the_badge_is_the_runners_colour_in_the_corner_and_the_rest_is_the_suite_icon(self):
        for size in (16, 48, 256):
            with self.subTest(size):
                plain = Image.open(icon.SOURCE / f"rizonesoft-office-{size}.png").convert("RGBA")
                badged = icon.frame(size, "#4C8DF6", "")
                c = self.badge_centre(size)
                r, g, b, a = badged.getpixel((c, c))
                self.assertEqual(a, 255)
                self.assertTrue(abs(r - 0x4C) <= 2 and abs(g - 0x8D) <= 2 and abs(b - 0xF6) <= 2, (r, g, b))
                quarter = size // 4  # the top left quarter is nowhere near the badge
                self.assertEqual(badged.crop((0, 0, quarter, quarter)).tobytes(),
                                 plain.crop((0, 0, quarter, quarter)).tobytes())

    def test_a_mark_file_is_drawn_white_from_32_pixels_up_and_never_below(self):
        mark = self.dir / "mark.svg"
        mark.write_text(MARK, encoding="utf-8")
        c = self.badge_centre(256)
        self.assertEqual(icon.frame(256, "#D97757", str(mark)).getpixel((c, c)), (255, 255, 255, 255))
        self.assertNotEqual(icon.frame(256, "#D97757", "").getpixel((c, c)), (255, 255, 255, 255))
        self.assertEqual(icon.frame(16, "#D97757", str(mark)).tobytes(), icon.frame(16, "#D97757", "").tobytes())

    def test_a_missing_mark_file_still_renders_the_badge(self):
        target = self.dir / "b.ico"
        done = self.render(str(target), "#4C8DF6", str(self.dir / "absent.svg"))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue(target.exists())

    def test_a_colour_that_is_not_a_colour_is_refused(self):
        done = self.render(str(self.dir / "c.ico"), "blue")
        self.assertEqual(done.returncode, 2)
        self.assertFalse((self.dir / "c.ico").exists())

    def test_no_runner_mark_is_kept_in_the_repository(self):
        # A runner's mark is its company's trademark: the script reads it from a file on the PC, and holds none.
        text = SCRIPT.read_text(encoding="utf-8") + (SCRIPTS / "start-campaign.ps1").read_text(encoding="utf-8")
        self.assertNotRegex(text, r"<path|viewBox|\bd=\"[Mm]")


if __name__ == "__main__":
    unittest.main()
