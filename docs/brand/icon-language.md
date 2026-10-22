# Icon design language

The rules every Rizonesoft Office icon is drawn to, so the suite logo and six app icons drawn on different days still read as one family and stay clear of Microsoft's look. The drawings themselves are generated, not hand-drawn: `scripts/lib/icon_design.py` holds every number below, and `python scripts/build-icons.py` writes the SVG masters to `design/icons/` and every raster from them. This document records the decisions; the code is where they live.

## Grid

Every icon is drawn on a 128-unit square canvas, `viewBox="0 0 128 128"`. The largest raster, 256 pixels in a Windows `.ico` and 1024 in a macOS `.icns`, is an exact 2x or 8x of it, so every edge lands on a whole pixel at every size the platforms ask for.

Three drawings share the canvas, picked by the size the icon is shown at (`tier_for` in `icon_design.py`):

| Tier | Shown at | Drawing |
| --- | --- | --- |
| `lg` | 48 px and up | Glass: gradient orb and dark block behind a frosted pane |
| `md` | 32 to 40 px | Orb and pane in flat tints, symbol in two or three heavy strokes |
| `sm` | 16 to 24 px | Orb and pane in flat tints, solid symbol |

Keyline shapes, in canvas units (`APP_PANE`, `APP_ORB`, `APP_GLYPH_AT`, `APP_BLOCK`):

| Shape | `lg` | `md` | `sm` |
| --- | --- | --- | --- |
| Pane (x, y, width, height) | 18, 30, 92, 80 | 14, 34, 92, 80 | 8, 36, 96, 84 |
| Pane corner radius | 20 | 20 | 22 |
| Orb (centre x, centre y, radius) | 80, 44, 38 | 82, 42, 36 | 86, 40, 38 |
| Symbol box (centre x, y; side) | 64, 70; 60.8 | 60, 74; 71.7 | 56, 78; 80 |
| Dark block (x, y, width, height, radius) | 10, 62, 58, 56, 16 | none | none |

The symbol is drawn in a 64-unit box centred on 0,0 and scaled into its tier's symbol box.

Safe area: every shape stays inside the canvas. The `lg` drawing spans 10 to 118 across and 6 to 118 down, `md` 14 to 118 and 6 to 114, and `sm`, which spends its margins on size, 8 to 124 and 2 to 120.

Corner radius: the pane's radius is 20 units (22 at `sm`, where the pane is larger), about a fifth of its width, and the dark block's is 16.

The keyline sheet, `design/icons/keylines.svg`, draws the three tiers side by side from these same constants (pane blue, orb orange, symbol box dashed green, block purple), so it cannot drift from the icons.

## Palette

Each app has a gradient (light end to dark end) for its orb, a single app colour for everything that is not the icon (taskbar badges, accents, the app's colour in the suite's own interface), and a symbol colour.

| App | Gradient light | Gradient dark | App colour | On white | On `#1f1f1f` |
| --- | --- | --- | --- | --- | --- |
| Write | `#4f8df7` | `#1e4fc2` | `#366edc` | 4.75:1 | 3.47:1 |
| Grid | `#34c27a` | `#0f7a45` | `#229e60` | 3.43:1 | 4.81:1 |
| Stage | `#ff8a4c` | `#d4421b` | `#ea6634` | 3.26:1 | 5.06:1 |
| Flow | `#9b7bf7` | `#5b35c9` | `#7b58e0` | 4.87:1 | 3.39:1 |
| Plan | `#2dc2b5` | `#0b7f86` | `#1ca09e` | 3.20:1 | 5.16:1 |
| Mail | `#3cc4f0` | `#0b7cc0` | `#229ed7` | 3.03:1 | 5.45:1 |
| Suite | six-colour orb | | `#7c8db5` | 3.32:1 | 4.97:1 |

Contrast is the WCAG 2 ratio, computed by `contrast()` in `icon_design.py`. Every app colour reaches the 3:1 that WCAG 2.2 asks of graphical objects (success criterion 1.4.11) against both a white and a `#1f1f1f` background. No gradient end does: the light ends fall below 3:1 on white and the dark ends below it on `#1f1f1f`. So each app colour is the point on its own gradient nearest the middle that passes both (the exact middle for five apps; 53% of the way to the dark end for Mail). `APP_COLOR` holds them, and the tests in `scripts/tests/test_build_icons.py` (`Palette`) refuse any app colour that is off its gradient or below 3:1.

The symbol colour is the gradient's dark end with 15% black, drawn on a pane tinted 84% (80% at `sm`) towards white from the light end.

The colours follow the category conventions people already read (documents blue, spreadsheets green, presentations orange). They are not Microsoft's app colours: every hex differs, and Flow and Plan take violet and teal where Visio and Project sit on blue and green.

## Motif

Glass, chosen by the owner on 2026-10-20 after two rejected rounds (interlocking tiles; then folded paper, orbit discs, Bauhaus blocks, isometric objects and die-cut stickers) and a third round of five styles closer to Microsoft 365 (layered cards, glass, folded corner, app tile and Fluent-style objects). The owner then asked for simpler 16 and 32 pixel drawings and a reworked suite logo, which gave the tier split in Grid above.

Every app icon is a coloured orb rising behind a frosted glass pane, with the app's symbol on the glass in a deep tone of the app's colour. At `lg` a dark block sits behind the pane's lower left corner, the pane blurs what is behind it, and a white rim and soft shadow lift it; the pane has a solid tinted base under the frost, so the icon reads the same on any desktop colour. At `md` and `sm` the blur gives way to flat tints, which stay crisp at a few pixels.

The suite logo is the `md` and `sm` construction at every size: the orb is split into six wedges in the six app colours, and the glass carries six rounded squares, one per app in its dark colour, in two rows of three.

Each app's symbol:

- **Write**: lines of text, the last one short, like a paragraph's ragged end.
- **Grid**: a table, a rounded frame with two inner rules each way (one each way at `md`, four solid cells at `sm`).
- **Stage**: a slide on a stand, with a rising bar chart on the slide at `lg`.
- **Flow**: a diagram, a square and two circles joined by connectors (one square and one circle at `md` and `sm`).
- **Plan**: a Gantt chart, three staggered bars (two at `sm`).
- **Mail**: an envelope with its flap drawn as a V.

## Distinctness rules

Each rule is one line the D01 T02 §7 review can tick:

1. No single letter is any icon's main symbol.
2. No letter on a tile, and no letter on a document sheet, in the way Microsoft's app icons pair a letter tile with an object.
3. No Microsoft app or file icon artwork in any form, traced, redrawn or recoloured. The MIT-licensed Fluent UI System Icons, chosen on 2026-10-20 for ribbon commands, are allowed in the interface; they are not app or file icons.
4. No app colour is one of Microsoft's app colours, and the six are compared against them in the §7 review.
5. Every app symbol is an object or diagram of the app's work (text lines, table, slide, diagram, bars, envelope), not a brand mark.
6. Every icon is built from the shared construction (orb, pane, symbol) in Motif above, so no single icon can drift towards another vendor's look.
7. The suite logo carries no text and no letter; the wordmark stands beside it in the lockups, never inside it.

## Accessibility

- Every app colour reaches 3:1 against white and `#1f1f1f` (Palette), and every symbol reaches at least 5.0:1 against its pane (the `Palette` tests require 4.5:1), so the symbol reads on the glass in any theme.
- Colour is never the only thing that tells the apps apart: each has its own symbol shape, so the icons stay distinct in greyscale and for people with a colour vision deficiency.
- Small sizes trade detail for weight: `md` symbols use strokes of 8 to 12 units and `sm` symbols are solid or 11 to 15 units (the white flap on Mail's solid envelope is 8), before the tier's 1.12 or 1.25 scale, so no stroke is thinner than about 1 pixel at 16 pixels.
- Every SVG master carries a `<title>` with the product's full name ("Rizonesoft Write"), which screen readers announce when the SVG is shown inline.
- The icons are images, so Windows high-contrast themes do not recolour them; inside the apps, every place an app icon appears also shows the app's name.
