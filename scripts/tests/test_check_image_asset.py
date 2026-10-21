"""scripts/check-image-asset.py: format, dimensions, budget, corruption and SVG content, on generated fixtures."""
import contextlib
import importlib.util
import io
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_image_asset", SCRIPTS / "check-image-asset.py")
ia = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ia)


def chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def png(width, height):
    """A valid greyscale PNG of the given size."""
    rows = b"".join(b"\x00" + b"\x80" * width for _ in range(height))
    return (ia.PNG_SIGNATURE + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def bmp(size):
    """An icon bitmap: BITMAPINFOHEADER with the doubled height, then empty pixels."""
    return struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, 32, 0, 0, 0, 0, 0, 0) + b"\x00" * 16


def ico(*images):
    """An ICO from (entry width, entry height, image bytes), 256 written as 0."""
    head = struct.pack("<HHH", 0, 1, len(images))
    offset, directory, body = 6 + 16 * len(images), b"", b""
    for width, height, image in images:
        directory += struct.pack("<BBBBHHII", width % 256, height % 256, 0, 0, 1, 32, len(image), offset)
        offset += len(image)
        body += image
    return head + directory + body


SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><defs><linearGradient id="g"/></defs>' \
      '<rect width="48" height="48" fill="url(#g)"/><use href="#g"/>{extra}</svg>'


class Fixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, name, data, *argv):
        path = self.dir / name
        path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                code = ia.main([str(path), *argv])
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue()


class Png(Fixtures):
    def test_png_size_reads_ihdr(self):
        self.assertEqual(ia.png_size(png(1280, 640)), (1280, 640))
        code, out = self.run_check("social.png", png(1280, 640), "--size", "1280x640", "--max-bytes", "1000000")
        self.assertEqual(code, 0, out)
        self.assertIn("png 1280x640", out)

    def test_a_wrong_size_is_refused(self):
        code, out = self.run_check("social.png", png(1280, 641), "--size", "1280x640")
        self.assertEqual(code, 1)
        self.assertIn("size is 1280x641, expected 1280x640", out)

    def test_the_name_never_decides_the_format(self):
        code, out = self.run_check("really-a-png.svg", png(4, 4), "--format", "svg")
        self.assertEqual(code, 1)
        self.assertIn("format is png, expected svg", out)
        self.assertIn("not a PNG, SVG or ICO", self.run_check("x.png", b"GIF89a....")[1])

    def test_a_corrupt_or_truncated_png_is_refused(self):
        good = bytearray(png(8, 8))
        good[-20] ^= 0xFF  # a byte inside IDAT, so its CRC fails
        self.assertIn("fails its CRC", self.run_check("bad.png", bytes(good))[1])
        self.assertIn("no IEND", self.run_check("short.png", png(8, 8)[:-12])[1])


class Budget(Fixtures):
    def test_one_byte_over_budget_fails(self):
        data = png(16, 16)
        self.assertEqual(self.run_check("a.png", data, "--max-bytes", str(len(data)))[0], 0)
        code, out = self.run_check("a.png", data, "--max-bytes", str(len(data) - 1))
        self.assertEqual(code, 1)
        self.assertIn(f"over budget: {len(data)} bytes > {len(data) - 1}", out)


class Svg(Fixtures):
    def test_a_clean_svg_passes_with_its_viewbox_size(self):
        code, out = self.run_check("mark.svg", SVG.format(extra=""), "--format", "svg", "--size", "48x48")
        self.assertEqual(code, 0, out)
        self.assertIn("svg 48x48", out)

    def test_an_embedded_raster_is_refused(self):
        raster = '<image href="data:image/png;base64,iVBORw0KGgo=" width="4" height="4"/>'
        code, out = self.run_check("mark.svg", SVG.format(extra=raster), "--format", "svg")
        self.assertEqual(code, 1)
        self.assertIn("embedded raster", out)

    def test_script_html_handlers_and_external_references_are_refused(self):
        cases = {
            "<script>alert(1)</script>": "script element",
            '<foreignObject><p xmlns="http://www.w3.org/1999/xhtml">x</p></foreignObject>': "embedded HTML",
            '<rect onclick="x()" width="1" height="1"/>': "event handler attribute onclick",
            '<use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="other.svg#a"/>': "external href",
            '<rect style="fill:url(https://example.invalid/a.svg#p)" width="1" height="1"/>': "external url",
            '<style>@import "https://example.invalid/a.css";</style>': "@import",
        }
        for extra, reason in cases.items():
            with self.subTest(reason=reason):
                code, out = self.run_check("mark.svg", SVG.format(extra=extra))
                self.assertEqual(code, 1, out)
                self.assertIn(reason, out)

    def test_a_doctype_missing_viewbox_or_wrong_root_is_refused(self):
        doctype = '<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY a "x">]>' + SVG.format(extra="")
        self.assertIn("DOCTYPE or entity", self.run_check("a.svg", doctype)[1])
        self.assertIn("viewBox is missing", self.run_check("a.svg", SVG.format(extra="").replace(' viewBox="0 0 48 48"', ""))[1])
        self.assertIn("not well-formed", self.run_check("a.svg", "<svg><g></svg>")[1])


class Ico(Fixtures):
    ICON = ico((16, 16, png(16, 16)), (32, 32, bmp(32)), (256, 256, png(256, 256)))

    def test_ico_sizes_lists_every_entry(self):
        self.assertEqual(ia.ico_sizes(self.ICON), [(16, 16), (32, 32), (256, 256)])
        code, out = self.run_check("app.ico", self.ICON, "--size", "16x16", "--size", "32x32", "--size", "256x256")
        self.assertEqual(code, 0, out)

    def test_a_missing_entry_is_refused(self):
        partial = ico((16, 16, png(16, 16)), (256, 256, png(256, 256)))
        code, out = self.run_check("app.ico", partial, "--size", "16x16", "--size", "32x32", "--size", "256x256")
        self.assertEqual(code, 1)
        self.assertIn("no 32x32 image", out)

    def test_an_entry_that_lies_about_its_image_is_refused(self):
        lying = ico((32, 32, png(16, 16)))
        self.assertIn("entry 1 says 32x32, its image is 16x16", self.run_check("app.ico", lying)[1])
        self.assertIn("truncated ICO", self.run_check("app.ico", self.ICON[:-40])[1])


class Arguments(Fixtures):
    def test_bad_arguments_and_unreadable_files_exit_2(self):
        self.assertEqual(self.run_check("a.png", png(4, 4), "--size", "4by4")[0], 2)
        self.assertEqual(self.run_check("a.png", png(4, 4), "--format", "png", "--size", "4x4", "--size", "8x8")[0], 2)
        out = io.StringIO()
        with contextlib.redirect_stderr(out):
            self.assertEqual(ia.main([str(self.dir / "missing.png")]), 2)


if __name__ == "__main__":
    unittest.main()
