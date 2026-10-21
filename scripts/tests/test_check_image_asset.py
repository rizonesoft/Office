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


def bmp(size, bits=32):
    """A complete icon bitmap: BITMAPINFOHEADER with the doubled height, the palette, colour pixels, then the mask."""
    palette = (1 << bits) * 4 if bits <= 8 else 0
    rows = ((size * bits + 31) // 32) * 4 + ((size + 31) // 32) * 4
    return (struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, bits, 0, 0, 0, 0, 0, 0)
            + bytes(palette + rows * size))


def png_raw(width, height, idat, depth=8, colour=0, interlace=0, plte=b"", compression=0, method=0):
    """A PNG with the given IHDR fields and raw IDAT bodies, every CRC correct."""
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, depth, colour, compression, method, interlace))
    return ia.PNG_SIGNATURE + ihdr + plte + b"".join(chunk(b"IDAT", d) for d in idat) + chunk(b"IEND", b"")


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

    def test_a_well_framed_but_undecodable_png_is_refused(self):
        two_rows = zlib.compress(bytes(8))  # rows of 5 bytes for 4 pixels: 8 bytes is short, filters all 0
        one_pixel = zlib.compress(bytes(2))
        palette = chunk(b"PLTE", bytes(3))
        cases = {
            "no image data (IDAT)": png_raw(4, 4, []),
            "does not inflate": png_raw(4, 4, [b"not zlib"]),
            "bit depth 3 is not allowed": png_raw(4, 4, [two_rows], depth=3),
            "invalid dimensions 0x4": png_raw(0, 4, [two_rows]),
            "image data is 8 bytes, 4x4 needs 20": png_raw(4, 4, [two_rows]),
            "scanline filter type 255": png_raw(1, 1, [zlib.compress(bytes([255, 0]))]),
            "unknown compression, filter or interlace method": png_raw(1, 1, [one_pixel], compression=1),
            "unknown compression, filter or interlace method ": png_raw(1, 1, [one_pixel], method=1),
            "unknown compression, filter or interlace method  ": png_raw(1, 1, [one_pixel], interlace=2),
            "invalid PLTE (0 bytes": png_raw(1, 1, [one_pixel], colour=3, plte=chunk(b"PLTE", b"")),
            "invalid PLTE (4 bytes": png_raw(1, 1, [one_pixel], colour=3, plte=chunk(b"PLTE", bytes(4))),
            "invalid PLTE (3 bytes for colour type 0)": png_raw(1, 1, [one_pixel], plte=palette),
            "more image data than 1x1 needs": png_raw(1, 1, [zlib.compress(bytes(100))]),
            "no PLTE": png_raw(1, 1, [zlib.compress(bytes(2))], colour=3),
        }
        for reason, data in cases.items():
            with self.subTest(reason=reason):
                code, out = self.run_check("bad.png", data)
                self.assertEqual(code, 1, out)
                self.assertIn(reason.strip(), out)  # trailing spaces only keep the dictionary keys apart

    def test_an_interlaced_png_and_split_idat_pass(self):
        size = ia.png_data_size(5, 3, 8, 6, 1)
        split = zlib.compress(bytes(size))
        data = png_raw(5, 3, [split[:7], split[7:]], colour=6, interlace=1)
        self.assertEqual(self.run_check("i.png", data, "--size", "5x3")[0], 0)

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
            '<rect fill="url(other.svg#p)" width="1" height="1"/>': "external url() reference in <rect fill>",
            '<style>rect { fill: url("https://example.invalid/a\'b.svg#p"); }</style>': "external url() reference in <style>",
            '<style>rect { fill: url("https://example.invalid/(a).svg#p"); }</style>': "external url() reference",
            '<g xml:base="https://example.invalid/external.svg"><use href="#shape"/></g>': "xml:base on <g>",
        }
        for extra, reason in cases.items():
            with self.subTest(reason=reason):
                code, out = self.run_check("mark.svg", SVG.format(extra=extra))
                self.assertEqual(code, 1, out)
                self.assertIn(reason, out)

    def test_css_escapes_stylesheets_and_image_functions_are_refused(self):
        backslash = chr(92)
        cases = {
            f"<style>rect {{ fill: u{backslash}72l(https://example.invalid/a.svg#p) }}</style>": "CSS escape in <style>",
            f'<style>@impor{backslash}74 "https://example.invalid/a.css";</style>': "CSS escape in <style>",
            '<rect style="fill:image-set(&quot;a.png&quot; 1x)" width="1" height="1"/>': "CSS image function",
        }
        for extra, reason in cases.items():
            with self.subTest(reason=reason):
                code, out = self.run_check("mark.svg", SVG.format(extra=extra))
                self.assertEqual(code, 1, out)
                self.assertIn(reason, out)
        pi = '<?xml version="1.0"?><?xml-stylesheet type="text/css" href="https://example.invalid/a.css"?>'
        code, out = self.run_check("mark.svg", pi + SVG.format(extra=""))
        self.assertEqual(code, 1, out)
        self.assertIn("processing instruction <?xml-stylesheet?>", out)

    def test_a_non_finite_or_empty_viewbox_is_refused(self):
        for box in ("nan 0 48 48", "0 0 nan inf", "0 0 0 48", "0 0 48 -1", "0 0 48", "0 0 4_8 48", "0 0 0x30 48"):
            with self.subTest(box=box):
                code, out = self.run_check("a.svg", SVG.format(extra="").replace("0 0 48 48", box))
                self.assertEqual(code, 1, out)
                self.assertIn("viewBox is missing or invalid", out)

    def test_an_unknown_encoding_is_refused_without_a_traceback(self):
        odd = '<?xml version="1.0" encoding="x-not-a-real-encoding"?>' + SVG.format(extra="")
        code, out = self.run_check("odd.svg", odd)
        self.assertEqual(code, 1, out)
        self.assertNotIn("Traceback", out)

    def test_a_prefixed_or_utf16_svg_is_detected(self):
        prefixed = ('<s:svg xmlns:s="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
                    '<s:rect width="1" height="1"/></s:svg>')
        self.assertEqual(self.run_check("p.svg", prefixed, "--format", "svg", "--size", "48x48")[0], 0)
        utf16 = SVG.format(extra="").encode("utf-16")
        self.assertEqual(self.run_check("u.svg", utf16, "--format", "svg", "--size", "48x48")[0], 0)

    def test_a_doctype_missing_viewbox_or_wrong_root_is_refused(self):
        doctype = '<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY a "x">]>' + SVG.format(extra="")
        self.assertIn("DOCTYPE or entity", self.run_check("a.svg", doctype)[1])
        self.assertIn("viewBox is missing", self.run_check("a.svg", SVG.format(extra="").replace(' viewBox="0 0 48 48"', ""))[1])
        self.assertIn("not well-formed", self.run_check("a.svg", "<svg><g></svg>")[1])


class Ico(Fixtures):
    ICON = ico((16, 16, png(16, 16)), (32, 32, bmp(32)), (48, 48, bmp(48, bits=8)), (256, 256, png(256, 256)))

    def test_ico_sizes_lists_every_entry(self):
        self.assertEqual(ia.ico_sizes(self.ICON), [(16, 16), (32, 32), (48, 48), (256, 256)])
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

    def test_a_truncated_or_unsupported_bitmap_is_refused(self):
        complete = bmp(32)
        cases = {
            "truncated bitmap header": struct.pack("<Iii", 40, 32, 64),
            "truncated bitmap: ": complete[:-1],
            "unsupported bitmap": complete[:14] + struct.pack("<H", 7) + complete[16:],
        }
        for reason, image in cases.items():
            with self.subTest(reason=reason):
                code, out = self.run_check("app.ico", ico((32, 32, image)), "--size", "32x32")
                self.assertEqual(code, 1, out)
                self.assertIn(reason, out)


class Arguments(Fixtures):
    def test_bad_arguments_and_unreadable_files_exit_2(self):
        self.assertEqual(self.run_check("a.png", png(4, 4), "--size", "4by4")[0], 2)
        self.assertEqual(self.run_check("a.png", png(4, 4), "--format", "png", "--size", "4x4", "--size", "8x8")[0], 2)
        self.assertEqual(self.run_check("a.png", png(4, 4), "--size", "4x4", "--size", "8x8")[0], 2)  # no --format
        out = io.StringIO()
        with contextlib.redirect_stderr(out):
            self.assertEqual(ia.main([str(self.dir / "missing.png")]), 2)


if __name__ == "__main__":
    unittest.main()
