#!/usr/bin/env python3
"""Build every Rizonesoft Office icon asset from scripts/lib/icon_design.py.

    python scripts/build-icons.py           # write design/icons/ masters and assets/icons/ outputs, then verify
    python scripts/build-icons.py --check   # rebuild in memory and fail if any committed file differs or is missing

Outputs:
    design/icons/apps/<app>-<tier>.svg, design/icons/suite/rizonesoft-office-<tier>.svg   SVG masters (lg, md, sm)
    assets/icons/png/<icon>/<icon>-<px>.png       16 to 1024, each size drawn with its tier
    assets/icons/windows/<icon>.ico               16, 20, 24, 32, 40, 48, 64, 96, 128, 256 (PNG-compressed entries)
    assets/icons/macos/<icon>.icns                16 to 1024 including @2x slots
    assets/icons/linux/hicolor/...                freedesktop hicolor PNGs plus scalable SVG, named by app id
    assets/icons/web/                             favicon.ico, favicon.svg, apple-touch-icon.png, icon-192.png, icon-512.png
    assets/icons/palette.json                     app colours for the interface

Requires the resvg_py rasteriser (pip install resvg_py) and Pillow (verification only).
"""
import argparse
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import icon_design as d

PNG_SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256, 512, 1024)
ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256)
HICOLOR_SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
# ICNS slot type -> (pixel size, displayed size that picks the tier). @2x slots draw the tier of their point size.
ICNS_SLOTS = (("icp4", 16, 16), ("ic11", 32, 16), ("icp5", 32, 32), ("ic12", 64, 32), ("icp6", 64, 64),
              ("ic07", 128, 128), ("ic13", 256, 128), ("ic08", 256, 256), ("ic14", 512, 256),
              ("ic09", 512, 512), ("ic10", 1024, 512))
MANAGED = (Path("design/icons/apps"), Path("design/icons/suite"), Path("assets/icons/png"), Path("assets/icons/windows"),
           Path("assets/icons/macos"), Path("assets/icons/linux"), Path("assets/icons/web"))
LINUX_ID = {d.SUITE: "com.rizonesoft.Office", **{k: f"com.rizonesoft.{v[0]}" for k, v in d.APPS.items()}}


class SetupRequired(RuntimeError):
    pass


def rasteriser():
    try:
        import resvg_py
    except ImportError:
        raise SetupRequired("resvg_py is not installed; run: python -m pip install resvg_py") from None
    return resvg_py


def render(svg, px, background=None):
    kwargs = {"svg_string": svg, "width": px, "height": px}
    if background:
        kwargs["background"] = background
    data = bytes(rasteriser().svg_to_bytes(**kwargs))
    if data[:8] != b"\x89PNG\r\n\x1a\n" or png_size(data) != (px, px):
        raise RuntimeError(f"rasteriser returned a bad PNG for {px} px")
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
    svg = {(i, t): d.icon_svg(i, t) for i in icons() for t in d.TIERS}
    for (icon, tier), text in svg.items():
        folder = "suite" if icon == d.SUITE else "apps"
        out[f"design/icons/{folder}/{icon}-{tier}.svg"] = text.encode("utf-8")
    cache = {}

    def raster(icon, px, shown=None, background=None):
        key = (icon, px, shown, background)
        if key not in cache:
            cache[key] = render(svg[(icon, d.tier_for(shown or px))], px, background)
        return cache[key]

    for icon in icons():
        for px in PNG_SIZES:
            out[f"assets/icons/png/{icon}/{icon}-{px}.png"] = raster(icon, px)
        out[f"assets/icons/windows/{icon}.ico"] = pack_ico([(px, raster(icon, px)) for px in ICO_SIZES])
        out[f"assets/icons/macos/{icon}.icns"] = pack_icns([(k, raster(icon, px, shown)) for k, px, shown in ICNS_SLOTS])
        for px in HICOLOR_SIZES:
            out[f"assets/icons/linux/hicolor/{px}x{px}/apps/{LINUX_ID[icon]}.png"] = raster(icon, px)
        out[f"assets/icons/linux/hicolor/scalable/apps/{LINUX_ID[icon]}.svg"] = svg[(icon, "lg")].encode("utf-8")
    s = d.SUITE
    out["assets/icons/web/favicon.ico"] = pack_ico([(px, raster(s, px)) for px in (16, 32, 48)])
    out["assets/icons/web/favicon.svg"] = svg[(s, "sm")].encode("utf-8")
    out["assets/icons/web/apple-touch-icon.png"] = raster(s, 180, background="#ffffff")
    out["assets/icons/web/icon-192.png"] = raster(s, 192)
    out["assets/icons/web/icon-512.png"] = raster(s, 512)
    palette = {"apps": {k: {"name": f"Rizonesoft {v[0]}", "counterpart": v[1], "accent": v[2][1], "light": v[2][0],
                            "linuxId": LINUX_ID[k]} for k, v in d.APPS.items()},
               "suite": {"name": "Rizonesoft Office", "tint": d.SUITE_TINT, "linuxId": LINUX_ID[d.SUITE]}}
    out["assets/icons/palette.json"] = (json.dumps(palette, indent=2) + "\n").encode("utf-8")
    return out


def verify(files):
    """Read every output back with an independent decoder. Returns a list of problems."""
    from PIL import Image
    problems = []
    for rel, data in sorted(files.items()):
        try:
            if rel.endswith(".png"):
                img = Image.open(io.BytesIO(data))
                img.load()
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
            elif rel.endswith(".icns"):
                img = Image.open(io.BytesIO(data))
                img.load()
                if img.size != (1024, 1024) and img.size != (512, 512):
                    problems.append(f"{rel}: largest image {img.size}")
                if struct.unpack(">I", data[4:8])[0] != len(data):
                    problems.append(f"{rel}: header length mismatch")
            elif rel.endswith(".svg"):
                text = data.decode("utf-8")
                if "<image" in text or "<script" in text or "href=\"http" in text:
                    problems.append(f"{rel}: forbidden content")
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
            found |= {p.relative_to(root).as_posix() for p in base.rglob("*") if p.is_file()}
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if committed outputs differ from a fresh build")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
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
