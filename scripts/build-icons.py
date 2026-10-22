#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Build every Rizonesoft Office icon and brand asset from the design modules in scripts/lib/.

    python scripts/build-icons.py           # write design/icons/ masters and assets/ outputs, then verify
    python scripts/build-icons.py --contact-sheet build/icons/contact-sheet.png   # review sheet, nothing else
    python scripts/build-icons.py --check   # rebuild in memory and fail if any committed file differs or is missing

Outputs:
    design/icons/apps/<app>-<tier>.svg, design/icons/suite/rizonesoft-office-<tier>.svg   app and suite SVG masters
    design/icons/apps/<app>-{16,24,32}.svg      app icons redrawn on the pixel grid for those sizes
    design/icons/files/<ext>-<variant>.svg      file-type SVG masters (lg, lg-badge-md, lg-badge-sm, md, sm)
    assets/icons/png/<icon>/<icon>-<px>.png     app and suite PNGs 16 to 1024, each size drawn with its tier
    assets/icons/windows/<icon>.ico             16, 20, 24, 32, 40, 48, 64, 96, 128, 256 (PNG-compressed entries)
    assets/icons/macos/<icon>.icns              16 to 1024 including @2x slots
    assets/icons/files/{png,windows,macos}/     the same for the 26 document file types (PNG up to 512)
    assets/icons/linux/hicolor/...              apps/ by app id and mimetypes/ by MIME type, plus scalable SVGs
    assets/icons/web/                           favicon.ico, favicon.svg, apple-touch-icon.png, icon-192.png, icon-512.png
    assets/icons/palette.json                   app colours for the interface
    assets/brand/{svg,png}/                     wordmark and suite and app lockups, light and dark
    design/github/banner-{light,dark}.svg, docs/assets/github/banner-{light,dark}.png (2560x640)   README banner
    design/github/social-preview.svg, docs/assets/github/social-preview.png (1280x640)   social preview
    design/github/lineup-{light,dark}.svg, docs/assets/github/lineup-{light,dark}.png (2x)   app lineup strip

Requires the packages pinned in scripts/requirements.txt: resvg_py (rasteriser), uharfbuzz and fontTools (text
outlines), Pillow (verification).
"""
import argparse
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import icon_design as d
import filetype_design as ft
import brand_design as bd

PNG_SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256, 512, 1024)
FILE_PNG_SIZES = PNG_SIZES[:-1]
ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256)
HICOLOR_SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
# ICNS slot type -> (pixel size, displayed size that picks the drawing). @2x slots draw for their point size.
ICNS_SLOTS = (("icp4", 16, 16), ("ic11", 32, 16), ("icp5", 32, 32), ("ic12", 64, 32), ("icp6", 64, 64),
              ("ic07", 128, 128), ("ic13", 256, 128), ("ic08", 256, 256), ("ic14", 512, 256),
              ("ic09", 512, 512), ("ic10", 1024, 512))
MANAGED = (Path("design/icons/apps"), Path("design/icons/suite"), Path("design/icons/files"), Path("assets/icons/png"),
           Path("assets/icons/windows"), Path("assets/icons/macos"), Path("assets/icons/files"),
           Path("assets/icons/linux"), Path("assets/icons/web"), Path("assets/brand"), Path("design/github"),
           Path("docs/assets/github"))
LINUX_ID = {d.SUITE: "com.rizonesoft.Office", **{k: f"com.rizonesoft.{v[0]}" for k, v in d.APPS.items()}}


class SetupRequired(RuntimeError):
    pass


def rasteriser():
    try:
        import resvg_py
    except ImportError:
        raise SetupRequired("resvg_py is not installed; run: python -m pip install -r scripts/requirements.txt") from None
    return resvg_py


def render(svg, width, height=None, background=None):
    height = height or width
    kwargs = {"svg_string": svg, "width": width, "height": height}
    if background:
        kwargs["background"] = background
    data = bytes(rasteriser().svg_to_bytes(**kwargs))
    if data[:8] != b"\x89PNG\r\n\x1a\n" or png_size(data) != (width, height):
        raise RuntimeError(f"rasteriser returned a bad PNG for {width}x{height}")
    return data


def png_size(data):
    return struct.unpack(">II", data[16:24])


def pack_ico(images):
    """images: list of (px, png bytes), ascending. Each entry stores the PNG as is (Windows Vista and later)."""
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries, blobs = b"", b""
    for px, data in images:
        side = 0 if px >= 256 else px
        entries += struct.pack("<BBBBHHII", side, side, 0, 0, 1, 32, len(data), offset)
        blobs += data
        offset += len(data)
    return header + entries + blobs


def pack_icns(slots):
    """slots: list of (4-character type, png bytes)."""
    body = b"".join(kind.encode("ascii") + struct.pack(">I", 8 + len(data)) + data for kind, data in slots)
    return b"icns" + struct.pack(">I", 8 + len(body)) + body


def icons():
    return [d.SUITE, *d.APPS]


def build():
    """Return {relative path: bytes} for every output. Pure apart from the rasteriser."""
    out = {}
    cache = {}

    def raster(svg_for, px, shown=None, background=None):
        """svg_for(displayed px) -> svg text; rendered at px pixels."""
        text = svg_for(shown or px)
        key = (text, px, background)
        if key not in cache:
            cache[key] = render(text, px, background=background)
        return cache[key]

    # App and suite icons.
    svg = {(i, t): d.icon_svg(i, t) for i in icons() for t in d.TIERS}
    for (icon, tier), text in svg.items():
        master = text if icon == d.SUITE else d.app_master_svg(icon, tier)
        out[f"design/icons/{'suite' if icon == d.SUITE else 'apps'}/{icon}-{tier}.svg"] = master.encode("utf-8")
    out["design/icons/keylines.svg"] = d.keylines_svg().encode("utf-8")
    for key in d.APPS:  # the pixel-aligned small variants, which the app rasters below use at those sizes
        for size in d.PIXEL_SIZES:
            out[f"design/icons/apps/{key}-{size}.svg"] = d.pixel_svg(key, size).encode("utf-8")
    out["design/icons/suite/rizonesoft-office-mono.svg"] = d.suite_mono_svg().encode("utf-8")
    for icon in icons():
        # An app shown at 16, 24 or 32 px (or points, on a @2x slot) uses its pixel-grid variant; otherwise its tier.
        draw = lambda shown, icon=icon: d.drawing_for(icon, shown)
        for px in PNG_SIZES:
            out[f"assets/icons/png/{icon}/{icon}-{px}.png"] = raster(draw, px)
        out[f"assets/icons/windows/{icon}.ico"] = pack_ico([(px, raster(draw, px)) for px in ICO_SIZES])
        out[f"assets/icons/macos/{icon}.icns"] = pack_icns([(k, raster(draw, px, shown)) for k, px, shown in ICNS_SLOTS])
        for px in HICOLOR_SIZES:
            out[f"assets/icons/linux/hicolor/{px}x{px}/apps/{LINUX_ID[icon]}.png"] = raster(draw, px)
        out[f"assets/icons/linux/hicolor/scalable/apps/{LINUX_ID[icon]}.svg"] = svg[(icon, "lg")].encode("utf-8")
    suite = lambda shown: svg[(d.SUITE, d.tier_for(shown))]
    out["assets/icons/web/favicon.ico"] = pack_ico([(px, raster(suite, px)) for px in (16, 32, 48)])
    out["assets/icons/web/favicon.svg"] = svg[(d.SUITE, "sm")].encode("utf-8")
    out["assets/icons/web/apple-touch-icon.png"] = raster(suite, 180, background="#ffffff")
    out["assets/icons/web/icon-192.png"] = raster(suite, 192)
    out["assets/icons/web/icon-512.png"] = raster(suite, 512)

    # Document file types.
    linux_mimes = set()
    for ext, (key, kind, mime) in ft.TYPES.items():
        fsvg = {v: ft.filetype_svg(ext, v) for v in ft.VARIANTS}
        for v, text in fsvg.items():
            out[f"design/icons/files/{ext}-{v}.svg"] = text.encode("utf-8")
        draw = lambda shown, fsvg=fsvg: fsvg[ft.variant_for(shown)]
        for px in FILE_PNG_SIZES:
            out[f"assets/icons/files/png/{ext}/{ext}-{px}.png"] = raster(draw, px)
        out[f"assets/icons/files/windows/{ext}.ico"] = pack_ico([(px, raster(draw, px)) for px in ICO_SIZES])
        out[f"assets/icons/files/macos/{ext}.icns"] = pack_icns([(k, raster(draw, px, shown)) for k, px, shown in ICNS_SLOTS])
        name = mime.replace("/", "-")
        if name in linux_mimes:  # a template that shares its document's MIME type (mpt) uses that icon on Linux
            continue
        linux_mimes.add(name)
        for px in HICOLOR_SIZES:
            out[f"assets/icons/linux/hicolor/{px}x{px}/mimetypes/{name}.png"] = raster(draw, px)
        out[f"assets/icons/linux/hicolor/scalable/mimetypes/{name}.svg"] = fsvg["lg"].encode("utf-8")

    # Wordmark and lockups.
    brand = {}
    for theme in bd.THEMES:
        brand[f"rizonesoft-office-wordmark-{theme}"] = bd.wordmark_svg(theme)
        for icon in icons():
            name = "rizonesoft-office" if icon == d.SUITE else f"rizonesoft-{icon}"
            brand[f"{name}-lockup-{theme}"] = bd.lockup_svg(icon, theme)
    for name, text in brand.items():
        out[f"assets/brand/svg/{name}.svg"] = text.encode("utf-8")
        vb = text.split('viewBox="0 0 ', 1)[1].split('"', 1)[0].split()
        w, h = float(vb[0]), float(vb[1])
        for scale in (1, 2):
            height = round(h * scale)
            out[f"assets/brand/png/{name}-{height}.png"] = render(text, round(w * scale), height)

    # README banner, light and dark: the SVG and a 2x PNG for the README.
    for theme in bd.THEMES:
        text = bd.banner_svg(theme)
        out[f"design/github/banner-{theme}.svg"] = text.encode("utf-8")
        out[f"docs/assets/github/banner-{theme}.png"] = render(text, bd.BANNER_W * 2, bd.BANNER_H * 2)
    # App lineup strip, light and dark: the SVG and a 2x PNG for the README.
    for theme in bd.THEMES:
        text = bd.lineup_svg(theme)
        w, h = (int(v) for v in text.split('viewBox="0 0 ', 1)[1].split('"', 1)[0].split())
        out[f"design/github/lineup-{theme}.svg"] = text.encode("utf-8")
        out[f"docs/assets/github/lineup-{theme}.png"] = render(text, 2 * w, 2 * h)
    # Social preview: GitHub shows it when the repository link is shared (uploaded by hand in the repository settings).
    social = bd.social_preview_svg()
    out["design/github/social-preview.svg"] = social.encode("utf-8")
    out["docs/assets/github/social-preview.png"] = render(social, bd.SOCIAL_W, bd.SOCIAL_H)

    palette = {"apps": {k: {"name": f"Rizonesoft {v[0]}", "counterpart": v[1], "accent": d.APP_COLOR[k],
                            "light": v[2][0], "dark": v[2][1], "linuxId": LINUX_ID[k]} for k, v in d.APPS.items()},
               "suite": {"name": "Rizonesoft Office", "tint": d.SUITE_TINT, "linuxId": LINUX_ID[d.SUITE]},
               "fileTypes": {ext: {"app": k, "mime": m} for ext, (k, _, m) in ft.TYPES.items()}}
    out["assets/icons/palette.json"] = (json.dumps(palette, indent=2) + "\n").encode("utf-8")
    return out


def contact_sheet():
    """PNG of the six app icons in a row at 256, 48 and 32 pixels, each drawn with the tier its size uses."""
    from PIL import Image
    sizes, pad = (256, 48, 32), 16
    sheet = Image.new("RGBA", (pad + len(d.APPS) * (256 + pad), pad + sum(s + pad for s in sizes)), "white")
    y = pad
    for size in sizes:
        for i, key in enumerate(d.APPS):
            icon = Image.open(io.BytesIO(render(d.drawing_for(key, size), size))).convert("RGBA")
            sheet.alpha_composite(icon, (pad + i * (256 + pad), y))
        y += size + pad
    buf = io.BytesIO()
    sheet.save(buf, "PNG")
    return buf.getvalue()


def verify(files):
    """Read every output back with an independent decoder. Returns a list of problems."""
    from PIL import Image
    problems = []
    for rel, data in sorted(files.items()):
        try:
            if rel.endswith(".png"):
                img = Image.open(io.BytesIO(data))
                img.load()
                if "/brand/" in rel:
                    want_h = int(Path(rel).stem.rsplit("-", 1)[-1])
                    if img.height != want_h:
                        problems.append(f"{rel}: height {img.height} is not {want_h}")
                else:
                    want = int(Path(rel).stem.rsplit("-", 1)[-1]) if "/png/" in rel else None
                    if "/hicolor/" in rel:
                        want = int(rel.split("/hicolor/")[1].split("x")[0])
                    if want and img.size != (want, want):
                        problems.append(f"{rel}: {img.size} is not {want}x{want}")
                if img.mode != "RGBA":
                    problems.append(f"{rel}: mode {img.mode}, want RGBA")
                elif not rel.endswith("apple-touch-icon.png") and img.getchannel("A").getextrema()[1] == 0:
                    problems.append(f"{rel}: fully transparent")
            elif rel.endswith(".ico"):
                img = Image.open(io.BytesIO(data))
                want = {(16, 16), (32, 32), (48, 48)} if "favicon" in rel else {(p, p) for p in ICO_SIZES}
                if set(img.info.get("sizes", ())) != want:
                    problems.append(f"{rel}: sizes {sorted(img.info.get('sizes', ()))}")
                count = struct.unpack("<H", data[4:6])[0]
                for i in range(count):  # decode every entry, not only the one Pillow opens
                    side, _, _, _, _, _, size, offset = struct.unpack("<BBBBHHII", data[6 + 16 * i:22 + 16 * i])
                    entry = Image.open(io.BytesIO(data[offset:offset + size]))
                    entry.load()
                    if entry.size != (side or 256, side or 256):
                        problems.append(f"{rel}: entry {i} is {entry.size}, its directory says {side or 256}")
            elif rel.endswith(".icns"):
                img = Image.open(io.BytesIO(data))
                img.load()
                if img.size not in ((1024, 1024), (512, 512)):
                    problems.append(f"{rel}: largest image {img.size}")
                if struct.unpack(">I", data[4:8])[0] != len(data):
                    problems.append(f"{rel}: header length mismatch")
                at = 8
                while at < len(data):  # decode every slot's PNG
                    kind, length = data[at:at + 4].decode("ascii"), struct.unpack(">I", data[at + 4:at + 8])[0]
                    if length < 8:
                        raise ValueError(f"slot {kind} has length {length}")
                    Image.open(io.BytesIO(data[at + 8:at + length])).load()
                    at += length
            elif rel.endswith(".svg"):
                text = data.decode("utf-8")
                if ET.fromstring(text).tag != "{http://www.w3.org/2000/svg}svg":
                    problems.append(f"{rel}: not an SVG document")
                if "<image" in text or "<script" in text or "href=\"http" in text or "<text" in text:
                    problems.append(f"{rel}: forbidden content (raster, script, remote link or live text)")
        except Exception as exc:  # a decoder failure is a finding, not a crash
            problems.append(f"{rel}: unreadable ({exc})")
    return problems


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def existing_managed(root):
    found = set()
    for folder in MANAGED:
        base = root / folder
        if base.exists():
            found |= {p.relative_to(root).as_posix() for p in base.rglob("*") if p.is_file() and p.name != "README.md"}
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail if committed outputs differ from a fresh build")
    mode.add_argument("--contact-sheet", type=Path, metavar="PNG",
                      help="write a review sheet of the six app icons at 256, 48 and 32 px and stop")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.contact_sheet:
            atomic_write(args.contact_sheet, contact_sheet())
            print(f"contact sheet: {args.contact_sheet}")
            return 0
        files = build()
    except SetupRequired as exc:
        print(f"setup required: {exc}", file=sys.stderr)
        return 2
    problems = verify(files)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    root = args.root
    stale = existing_managed(root) - set(files)
    if args.check:
        drift = [rel for rel, data in files.items() if not (root / rel).is_file() or (root / rel).read_bytes() != data]
        for rel in sorted(drift):
            print(f"out of date: {rel}", file=sys.stderr)
        for rel in sorted(stale):
            print(f"not produced by the build: {rel}", file=sys.stderr)
        if drift or stale:
            return 1
        print(f"icons current: {len(files)} files")
        return 0
    for rel, data in files.items():
        target = root / rel
        if not target.is_file() or target.read_bytes() != data:
            atomic_write(target, data)
    for rel in stale:
        (root / rel).unlink()
    print(f"icons built: {len(files)} files verified, {len(stale)} stale removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
