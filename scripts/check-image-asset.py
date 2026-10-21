#!/usr/bin/env python3
"""Refuse an image asset that is not what it claims: wrong format, wrong dimensions, over its byte budget, corrupt, or
an SVG that pulls in content from outside itself.

    python scripts/check-image-asset.py docs/assets/github/social-preview.png --size 1280x640 --max-bytes 1000000
    python scripts/check-image-asset.py design/brand/suite-mark.svg --format svg
    python scripts/check-image-asset.py assets/icons/windows/word.ico --size 16x16 --size 32x32 --size 256x256

The format comes from the content, never the file name: a PNG by its signature, an ICO by its header, an SVG by an
`svg` root element. `--format` refuses any other. Dimensions are read from the file itself: a PNG's IHDR chunk, an
SVG's root `viewBox`, an ICO's directory entries (0 meaning 256, each entry's image checked against its entry). For a
PNG or SVG, `--size` must name the one size it has; for an ICO, each `--size` must be one of its entries. A PNG is
walked chunk by chunk with every CRC checked through IEND, so a corrupted file is refused. An SVG may not embed a
raster (`<image>`), run script (`<script>`, `on*` attributes), embed HTML (`<foreignObject>`), declare a DOCTYPE or
entities, or reference anything but its own fragments (`href`, or `url()` in a style or any attribute, not
starting with `#`).

Exit 0 when the asset passes (printing its format, size and bytes), 1 with one line per problem, 2 when the file
cannot be read or the arguments are invalid. Stdlib only.
"""
import argparse
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
FORBIDDEN = {"image": "embedded raster <image>", "script": "script element", "foreignObject": "embedded HTML <foreignObject>"}


def detect(data):
    """The format the content is, or None."""
    if data.startswith(PNG_SIGNATURE):
        return "png"
    if len(data) >= 6 and data[:4] == b"\x00\x00\x01\x00":
        return "ico"
    head = data[:4096].lstrip(b"\xef\xbb\xbf").lstrip()
    if head.startswith(b"<") and re.search(rb"<svg[\s>]", data[:65536]):
        return "svg"
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


def png_size(data):
    """(width, height) from the IHDR chunk, which must come first; ValueError when the PNG is corrupt."""
    chunks = png_chunks(data)
    kind, body = chunks[0]
    if kind != b"IHDR" or len(body) != 13:
        raise ValueError("corrupt PNG: the first chunk is not a 13-byte IHDR")
    width, height = struct.unpack(">II", body[:8])
    if not width or not height:
        raise ValueError("corrupt PNG: zero width or height")
    return width, height


def _local(name):
    return name.rsplit("}", 1)[-1]


def svg_check(data):
    """(width, height) from the root viewBox, and the problems with the SVG's content."""
    problems = []
    text = data.decode("utf-8-sig", errors="strict")
    if re.search(r"<!DOCTYPE|<!ENTITY", text, re.IGNORECASE):
        return None, ["DOCTYPE or entity declaration"]
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return None, [f"not well-formed XML: {exc}"]
    if root.tag not in (f"{{{SVG_NS}}}svg", "svg"):
        return None, [f"root element is {_local(root.tag)}, not svg"]
    size = None
    box = (root.get("viewBox") or "").replace(",", " ").split()
    try:
        x, y, width, height = (float(v) for v in box)
        if width <= 0 or height <= 0:
            raise ValueError
        size = (width, height)
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
            else:  # style="fill:url(...)" and presentation attributes such as fill="url(...)" alike
                problems += _style_urls(value, f"{name} {attr_name}")
        if name == "style" and element.text:
            problems += _style_urls(element.text, name)
            if re.search(r"@import", element.text, re.IGNORECASE):
                problems.append("@import in <style>")
    return size, problems


def _style_urls(css, where):
    return [f"external url({url[:60]!r}) in <{where}>" for _q, url in STYLE_URL.findall(css)
            if not url.strip().startswith("#")]


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
        if image.startswith(PNG_SIGNATURE):
            actual = png_size(image)
        elif len(image) >= 12 and struct.unpack("<I", image[:4])[0] == 40:
            bmp_width, bmp_height = struct.unpack("<ii", image[4:12])
            actual = (bmp_width, bmp_height // 2)  # an icon bitmap stacks the colour and mask halves
        else:
            raise ValueError(f"corrupt ICO: image {index + 1} is neither PNG nor a bitmap")
        if actual != (width, height):
            raise ValueError(f"corrupt ICO: entry {index + 1} says {width}x{height}, its image is {actual[0]}x{actual[1]}")
        sizes.append((width, height))
    return sizes


def text_size(size):
    return "x".join(f"{v:g}" if isinstance(v, float) else str(v) for v in size)


def check(path, fmt=None, sizes=(), max_bytes=None):
    """(summary, problems) for one asset; OSError when it cannot be read."""
    data = Path(path).read_bytes()
    problems = []
    if max_bytes is not None and len(data) > max_bytes:
        problems.append(f"over budget: {len(data)} bytes > {max_bytes}")
    found = detect(data)
    if found is None:
        return None, problems + ["not a PNG, SVG or ICO"]
    if fmt and found != fmt:
        return None, problems + [f"format is {found}, expected {fmt}"]
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
    except (ValueError, struct.error, UnicodeDecodeError) as exc:
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
    if args.format in ("png", "svg") and len(args.size) > 1:
        parser.error(f"a {args.format.upper()} has one size; give --size once")
    try:
        summary, problems = check(args.path, args.format, args.size, args.max_bytes)
    except OSError as exc:
        print(f"check-image-asset: cannot read {args.path}: {exc.strerror or exc}", file=sys.stderr)
        return 2
    if summary and len(args.size) > 1 and not summary.startswith("ico"):
        problems.append(f"a {summary.split()[0].upper()} has one size; give --size once")
    if problems:
        print("\n".join(f"{args.path}: {p}" for p in problems))
        return 1
    print(f"{args.path}: ok, {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
