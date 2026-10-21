#!/usr/bin/env python3
"""Refuse an image asset that is not what it claims: wrong format, wrong dimensions, over its byte budget, corrupt, or
an SVG that pulls in content from outside itself.

    python scripts/check-image-asset.py docs/assets/github/social-preview.png --size 1280x640 --max-bytes 1000000
    python scripts/check-image-asset.py design/brand/suite-mark.svg --format svg
    python scripts/check-image-asset.py assets/icons/windows/word.ico --size 16x16 --size 32x32 --size 256x256

The format comes from the content, never the file name: a PNG by its signature, an ICO by its header, an SVG by its
root element's expanded name (UTF-8 or UTF-16). `--format` refuses any other. Dimensions are read from the file itself:
a PNG's IHDR chunk, an SVG's root `viewBox` (four finite numbers, positive width and height), an ICO's directory
entries (0 meaning 256). For a PNG or SVG, `--size` must name the one size it has; for an ICO, each `--size` must be one
of its entries.

A PNG must be decodable, not only well framed: every chunk's CRC through IEND, a valid IHDR (a legal bit depth and
colour type pair, compression and filter method 0, interlace 0 or 1), PLTE before the data of a palette image,
consecutive IDAT chunks, and image data that inflates, without being held in memory, to exactly the byte count its
dimensions need. An ICO entry must hold a PNG that passes the same checks, or a complete bitmap (a BITMAPINFOHEADER,
one plane, 1, 4, 8, 24 or 32 bits, no compression, and every byte of its palette, pixels and mask), whose size matches
its entry. An SVG may not embed a raster (`<image>`), run script (`<script>`, `on*` attributes), embed HTML
(`<foreignObject>`), declare a DOCTYPE or entities, carry a processing instruction other than the XML declaration
(such as `<?xml-stylesheet?>`), use a CSS escape in a style or attribute (which could spell `url` or `@import`), use a
CSS image function or `@import`, or reference anything but its own fragments (`href`, or `url()` in a style or any
attribute, not starting with `#`).

Exit 0 when the asset passes (printing its format, size and bytes), 1 with one line per problem, 2 when the file
cannot be read or the arguments are invalid (including more than one `--size` for a PNG or SVG). Stdlib only.
"""
import argparse
import io
import math
from pathlib import Path
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SVG_NS = "http://www.w3.org/2000/svg"
SIZE = re.compile(r"^([1-9]\d{0,5})x([1-9]\d{0,5})$")
STYLE_URL = re.compile(r"url\(\s*(['\"]?)([^)'\"]*)\1\s*\)", re.IGNORECASE)
CSS_IMAGE = re.compile(r"(?:-webkit-)?image-set\(|\bimage\(|cross-fade\(|element\(", re.IGNORECASE)
FORBIDDEN = {"image": "embedded raster <image>", "script": "script element", "foreignObject": "embedded HTML <foreignObject>"}
# Legal PNG bit depths per colour type, and the samples per pixel each type carries (PNG 3, IHDR).
PNG_DEPTHS = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
PNG_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
ADAM7 = ((0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2))
BMP_BITS = {1, 4, 8, 24, 32}


class ArgumentProblem(Exception):
    """The arguments do not fit the asset (exit 2, like any other invalid argument)."""


def svg_text(data):
    """The SVG's text, from a UTF-16 byte order mark or as UTF-8; UnicodeDecodeError otherwise."""
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    return data.decode("utf-8-sig")


def svg_root_name(data):
    """The expanded name of the document's root element, or None when it is not XML."""
    try:
        for _event, element in ET.iterparse(io.BytesIO(data), events=("start",)):
            return element.tag
    except ET.ParseError:
        return None
    return None


def detect(data):
    """The format the content is, or None."""
    if data.startswith(PNG_SIGNATURE):
        return "png"
    if len(data) >= 6 and data[:4] == b"\x00\x00\x01\x00":
        return "ico"
    if svg_root_name(data) in (f"{{{SVG_NS}}}svg", "svg"):
        return "svg"
    try:  # malformed XML that is plainly meant as an SVG, so svg_check names what is wrong with it
        if re.match(r"\s*<", svg_text(data)) and re.search(r"<(?:\w+:)?svg[\s>/]", svg_text(data)[:65536]):
            return "svg"
    except UnicodeDecodeError:
        pass
    return None


def png_chunks(data):
    """The PNG's chunks as (type, body) after checking every length and CRC through IEND; ValueError when corrupt."""
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG signature")
    chunks, at = [], len(PNG_SIGNATURE)
    while True:
        if at + 12 > len(data):
            raise ValueError("truncated PNG: no IEND chunk")
        length, kind = struct.unpack(">I4s", data[at:at + 8])
        end = at + 12 + length
        if end > len(data):
            raise ValueError(f"truncated PNG: chunk {kind!r} runs past the end of the file")
        body = data[at + 8:at + 8 + length]
        (crc,) = struct.unpack(">I", data[at + 8 + length:end])
        if zlib.crc32(kind + body) & 0xFFFFFFFF != crc:
            raise ValueError(f"corrupt PNG: chunk {kind.decode('latin-1')} fails its CRC")
        chunks.append((kind, body))
        at = end
        if kind == b"IEND":
            return chunks


def png_data_size(width, height, depth, colour, interlace):
    """The inflated image data byte count: one filter byte per row, rows packed to whole bytes, per Adam7 pass."""
    bits = depth * PNG_CHANNELS[colour]
    if not interlace:
        return height * (1 + (width * bits + 7) // 8)
    total = 0
    for x0, y0, dx, dy in ADAM7:
        cols = (width - x0 + dx - 1) // dx if width > x0 else 0
        rows = (height - y0 + dy - 1) // dy if height > y0 else 0
        if cols and rows:
            total += rows * (1 + (cols * bits + 7) // 8)
    return total


def png_size(data):
    """(width, height) of a decodable PNG; ValueError naming what is wrong otherwise."""
    chunks = png_chunks(data)
    kind, body = chunks[0]
    if kind != b"IHDR" or len(body) != 13:
        raise ValueError("corrupt PNG: the first chunk is not a 13-byte IHDR")
    width, height, depth, colour, compression, method, interlace = struct.unpack(">IIBBBBB", body)
    if not width or not height or width > 2**31 - 1 or height > 2**31 - 1:
        raise ValueError(f"corrupt PNG: invalid dimensions {width}x{height}")
    if depth not in PNG_DEPTHS.get(colour, ()):
        raise ValueError(f"corrupt PNG: bit depth {depth} is not allowed for colour type {colour}")
    if compression != 0 or method != 0 or interlace not in (0, 1):
        raise ValueError("corrupt PNG: unknown compression, filter or interlace method")
    kinds = [k for k, _ in chunks]
    if b"IDAT" not in kinds:
        raise ValueError("corrupt PNG: no image data (IDAT)")
    first, last = kinds.index(b"IDAT"), len(kinds) - 1 - kinds[::-1].index(b"IDAT")
    if any(k != b"IDAT" for k in kinds[first:last + 1]):
        raise ValueError("corrupt PNG: IDAT chunks are not consecutive")
    if colour == 3 and b"PLTE" not in kinds[:first]:
        raise ValueError("corrupt PNG: a palette image has no PLTE before its data")
    expected = png_data_size(width, height, depth, colour, interlace)
    inflater, produced = zlib.decompressobj(), 0
    try:
        for _kind, part in chunks[first:last + 1]:
            pending = part
            while pending:  # inflate in bounded steps, counting bytes, never holding the image
                out = inflater.decompress(pending, 1 << 20)
                produced += len(out)
                if produced > expected:
                    raise ValueError(f"corrupt PNG: more image data than {width}x{height} needs")
                pending = inflater.unconsumed_tail
        while not inflater.eof:
            out = inflater.decompress(b"", 1 << 20)
            if not out:
                break
            produced += len(out)
            if produced > expected:
                raise ValueError(f"corrupt PNG: more image data than {width}x{height} needs")
    except zlib.error as exc:
        raise ValueError(f"corrupt PNG: image data does not inflate ({exc})") from None
    if not inflater.eof or produced != expected:
        raise ValueError(f"corrupt PNG: image data is {produced} bytes, {width}x{height} needs {expected}")
    return width, height


def _local(name):
    return name.rsplit("}", 1)[-1]


def svg_check(data):
    """(width, height) from the root viewBox, and the problems with the SVG's content."""
    problems = []
    try:
        text = svg_text(data)
    except UnicodeDecodeError:
        return None, ["not UTF-8 or UTF-16 text"]
    if re.search(r"<!DOCTYPE|<!ENTITY", text, re.IGNORECASE):
        return None, ["DOCTYPE or entity declaration"]
    for instruction in re.findall(r"<\?([^\s?]*)", text):
        if instruction != "xml":
            problems.append(f"processing instruction <?{instruction}?>")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        return None, problems + [f"not well-formed XML: {exc}"]
    if root.tag not in (f"{{{SVG_NS}}}svg", "svg"):
        return None, problems + [f"root element is {_local(root.tag)}, not svg"]
    size = None
    box = (root.get("viewBox") or "").replace(",", " ").split()
    try:
        values = [float(v) for v in box]
        if len(values) != 4 or not all(math.isfinite(v) for v in values) or values[2] <= 0 or values[3] <= 0:
            raise ValueError
        size = (values[2], values[3])
    except ValueError:
        problems.append(f"root viewBox is missing or invalid: {root.get('viewBox')!r}")
    for element in root.iter():
        name = _local(element.tag) if isinstance(element.tag, str) else ""
        if name in FORBIDDEN:
            problems.append(FORBIDDEN[name])
        for attr, value in element.attrib.items():
            attr_name = _local(attr)
            if attr_name.lower().startswith("on"):
                problems.append(f"event handler attribute {attr_name} on <{name}>")
            elif attr_name == "href" and not value.strip().startswith("#"):
                problems.append(f"external href {value[:60]!r} on <{name}>")
            else:  # style="fill:url(...)" and presentation attributes such as fill="url(...)" are both CSS
                problems += _css_problems(value, f"{name} {attr_name}")
        if name == "style" and element.text:
            problems += _css_problems(element.text, name)
    return size, problems


def _css_problems(css, where):
    """A backslash escape could spell `url` or `@import` past any text match, so CSS here may not use one."""
    if "\\" in css:
        return [f"CSS escape in <{where}>"]
    problems = [f"external url({url[:60]!r}) in <{where}>" for _q, url in STYLE_URL.findall(css)
                if not url.strip().startswith("#")]
    if re.search(r"@import", css, re.IGNORECASE):
        problems.append(f"@import in <{where}>")
    if CSS_IMAGE.search(css):
        problems.append(f"CSS image function in <{where}>")
    return problems


def bmp_size(image):
    """(width, height) of a complete icon bitmap: colour pixels then the 1-bit mask, both bottom-up; ValueError
    otherwise."""
    if len(image) < 40:
        raise ValueError("truncated bitmap header")
    header, width, double_height, planes, bits, compression = struct.unpack("<IiiHHI", image[:20])
    (colours,) = struct.unpack("<I", image[32:36])
    if header < 40 or header > len(image):
        raise ValueError(f"bitmap header of {header} bytes")
    if width <= 0 or double_height <= 0 or double_height % 2 or planes != 1 or bits not in BMP_BITS or compression != 0:
        raise ValueError(f"unsupported bitmap ({width}x{double_height}, {planes} planes, {bits} bits, compression {compression})")
    height = double_height // 2
    palette = (colours or (1 << bits)) * 4 if bits <= 8 else colours * 4
    needed = header + palette + (((width * bits + 31) // 32) * 4 + ((width + 31) // 32) * 4) * height
    if len(image) < needed:
        raise ValueError(f"truncated bitmap: {len(image)} bytes, {width}x{height} at {bits} bits needs {needed}")
    return width, height


def ico_sizes(data):
    """Every directory entry as (width, height), each checked against the image it points at; ValueError when the
    directory or an image is corrupt."""
    reserved, kind, count = struct.unpack("<HHH", data[:6])
    if reserved != 0 or kind != 1 or count == 0:
        raise ValueError("corrupt ICO: bad header or no images")
    if 6 + 16 * count > len(data):
        raise ValueError("truncated ICO: directory runs past the end of the file")
    sizes = []
    for index in range(count):
        entry = data[6 + 16 * index:22 + 16 * index]
        width, height = entry[0] or 256, entry[1] or 256
        length, offset = struct.unpack("<II", entry[8:16])
        if not length or offset + length > len(data):
            raise ValueError(f"truncated ICO: image {index + 1} runs past the end of the file")
        image = data[offset:offset + length]
        try:
            actual = png_size(image) if image.startswith(PNG_SIGNATURE) else bmp_size(image)
        except ValueError as exc:
            raise ValueError(f"corrupt ICO: image {index + 1}: {exc}") from None
        if actual != (width, height):
            raise ValueError(f"corrupt ICO: entry {index + 1} says {width}x{height}, its image is {actual[0]}x{actual[1]}")
        sizes.append((width, height))
    return sizes


def text_size(size):
    return "x".join(f"{v:g}" if isinstance(v, float) else str(v) for v in size)


def check(path, fmt=None, sizes=(), max_bytes=None):
    """(summary, problems) for one asset; OSError when it cannot be read, ArgumentProblem when the arguments do not
    fit it."""
    data = Path(path).read_bytes()
    problems = []
    if max_bytes is not None and len(data) > max_bytes:
        problems.append(f"over budget: {len(data)} bytes > {max_bytes}")
    found = detect(data)
    if found is None:
        return None, problems + ["not a PNG, SVG or ICO"]
    if fmt and found != fmt:
        return None, problems + [f"format is {found}, expected {fmt}"]
    if found in ("png", "svg") and len(sizes) > 1:
        raise ArgumentProblem(f"a {found.upper()} has one size; give --size once")
    have = []
    try:
        if found == "png":
            have = [png_size(data)]
        elif found == "ico":
            have = ico_sizes(data)
        else:
            size, svg_problems = svg_check(data)
            problems += svg_problems
            have = [size] if size else []
    except (ValueError, struct.error) as exc:
        return None, problems + [str(exc)]
    wanted = [tuple(int(v) for v in s.split("x")) for s in sizes]
    if found in ("png", "svg") and wanted and have and have[0] != wanted[0]:
        problems.append(f"size is {text_size(have[0])}, expected {text_size(wanted[0])}")
    for size in wanted if found == "ico" else ():
        if size not in have:
            problems.append(f"no {text_size(size)} image (has {', '.join(text_size(s) for s in have)})")
    return f"{found} {', '.join(text_size(s) for s in have)} {len(data)} bytes", problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Refuse an image asset with the wrong format, size, budget or content.")
    parser.add_argument("path")
    parser.add_argument("--format", choices=("png", "svg", "ico"))
    parser.add_argument("--size", action="append", default=[], metavar="WxH",
                        help="expected size; repeat for each ICO entry")
    parser.add_argument("--max-bytes", type=int, metavar="N")
    args = parser.parse_args(argv)
    if any(not SIZE.match(s) for s in args.size):
        parser.error("--size takes WxH with positive whole numbers, like 1280x640")
    if args.max_bytes is not None and args.max_bytes < 1:
        parser.error("--max-bytes must be positive")
    try:
        summary, problems = check(args.path, args.format, args.size, args.max_bytes)
    except OSError as exc:
        print(f"check-image-asset: cannot read {args.path}: {exc.strerror or exc}", file=sys.stderr)
        return 2
    except ArgumentProblem as exc:
        print(f"check-image-asset: {exc}", file=sys.stderr)
        return 2
    if problems:
        print("\n".join(f"{args.path}: {p}" for p in problems))
        return 1
    print(f"{args.path}: ok, {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
