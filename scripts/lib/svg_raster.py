# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The one call into the SVG rasteriser, in a module a process pool's worker can import.

`scripts/build-icons.py` has a hyphen in its name, so a worker process cannot import a function from it; the pool
draws through `svg_to_png` here instead (D01 T02 §8). Threads gain nothing: the rasteriser holds the interpreter lock.
"""


def svg_to_png(request):
    """Draw one raster. `request` is `(svg text, width, height, background or None)`; returns the PNG's bytes.

    The caller checks what comes back (signature and size), in the parent, so a bad raster is reported once."""
    svg, width, height, background = request
    import resvg_py
    kwargs = {"svg_string": svg, "width": width, "height": height}
    if background:
        kwargs["background"] = background
    return bytes(resvg_py.svg_to_bytes(**kwargs))
