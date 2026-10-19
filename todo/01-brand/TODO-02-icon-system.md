---
schema_version: 1
id: icon-system
domain: 01-brand
status: active
title: "TODO-02 -- Suite and App Icon System"
---

# TODO-02 -- Suite and App Icon System

> **Goal:** The suite has an original icon family: a suite mark and wordmark, six app icons, small-size variants, and document file-type icons, all as SVG masters with a reproducible export to PNG, ICO and ICNS. No icon reuses Microsoft's composition (a letter tile overlapping a document or grid card), Microsoft's artwork, or the Fluent app-icon style, and the owner signs off a side-by-side distinctness review.

> **Current state:** Measured 2026-10-19. No icon or brand artwork exists: `design/` is absent. Names are not chosen yet; they arrive from D01 T01 §3. `scripts/check-image-asset.py` is planned in D00 T01 §2 and does not exist yet.

## Inputs

- `docs/brand/NAMES.md` (from D01 T01 §3): suite Rizonesoft Office and the app names Write, Grid, Stage, Flow, Plan and Mail (decided 2026-10-20). The names carry no visual motif, so §1 chooses one.
- Microsoft 365 app icons (2019 and 2025 redesigns) as a reference for what to avoid only; never copied, traced or committed. Reference screenshots stay in `R:\scratch`.
- Platform icon requirements: Windows app icons (ICO with 16, 24, 32, 48, 64, 256), macOS ICNS (16 to 1024 at 1x and 2x), Linux hicolor PNG sizes (16 to 512), and favicon sizes for any web build.
- -> XREF: D01 T01 §3 -- names and motif come from the recorded naming decision
- -> XREF: D00 T01 §2 -- every exported asset is verified by `scripts/check-image-asset.py`
- -> XREF: D01 T03 §2 -- the social preview and README lineup use the masters from §2 and §3
- -> XREF: D02 T02 §2 -- the command glyph library must sit visually with the app icons defined in §1

## Outcome

- `design/brand/` holds `suite-mark.svg` and `wordmark.svg`; `design/icons/apps/` holds one master SVG per app plus 16, 24 and 32 pixel variants; `design/icons/files/` holds one SVG per supported file type.
- `python scripts/build-icons.py` regenerates `build/icons/` (PNG sets, `.ico`, `.icns`) from the masters, and every output passes `scripts/check-image-asset.py`.
- `docs/brand/icon-distinctness.md` records the side-by-side review against Microsoft's icons and the owner's sign-off.

**Adjacency:** all=not-applicable (brand artwork and its build script; no user records, settings or permissions)

**Adjacency rationale:** Icons are static assets. The product surfaces that display them (taskbar, title bar, Backstage, file associations) are owned by the shared platform domain authored from D03 T01 §13.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Icon design language brief | D01 T01 §3 | [ ] |
| 2 | §2 | Suite mark and wordmark masters | §1 | [ ] |
| 3 | §3 | Six app icon masters | §1 | [ ] |
| 4 | §4 | Small-size app icon variants | §3 | [ ] |
| 5 | §5 | Document file-type icons | §3 | [ ] |
| 6 | §6 | Icon export pipeline | §2, §4, §5, D00 T01 §2 | [ ] |
| 7 | §7 | Distinctness review and owner sign-off | §6 | [ ] |

## 1. Icon Design Language Brief

The brief fixes grid, keylines, corner radius, palette and the motif before any icon is drawn, so six icons drawn on different days still read as one family. It also writes down the distinctness rules that keep the family clear of Microsoft's look.

Motif status, 2026-10-20: the owner rejected the interlocking-tile drafts (five renderings of pentomino tiles). A second round (folded paper, orbit discs, Bauhaus blocks, isometric objects, die-cut stickers) was also rejected, and the owner asked for a style closer to Microsoft 365. Third round: layered cards, glass, folded corner, app tile and Fluent-style objects, using the industry category colours (documents blue, spreadsheets green, presentations orange) and never a letter tile. The owner chose Glass on 2026-10-20 and asked for simpler 16 and 32 pixel drawings and a reworked suite logo; three refined Glass variations are under review. The concept sheet is the private artifact https://claude.ai/artifact/UFcUNAwH9LCsf57YfCesUS.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/brand/icon-language.md` with Grid, Palette, Motif, Distinctness rules and Accessibility headings. Done when: the design-doc checker passes with those headings.

- [ ] Define the master grid in `docs/brand/icon-language.md`: 256 unit canvas, keyline shapes, safe area and corner radius. Done when: the numbers are stated and a keyline SVG `design/icons/keylines.svg` exists. Cheaper substitute: "consistent rounded squares" with no numbers.
- [ ] Define the per-app palette in `docs/brand/icon-language.md` with hex values and a contrast check against white and `#1f1f1f` backgrounds. Done when: each app colour reaches at least 3:1 against both backgrounds. Cheaper substitute: reusing Microsoft's blue, green, orange, teal and purple app colours one for one.
- [ ] Record the owner's chosen concept from the review in this section in `docs/brand/icon-language.md`: the concept, how the suite logo is built, and each app's object or glyph. Done when: the concept and date are recorded and each of the six apps has one sentence naming its glyph. Cheaper substitute: a letter on a tile.
- [ ] Write the Distinctness rules in `docs/brand/icon-language.md`: no single letter as the main glyph, no tile overlapping a document card, no Fluent gradients copied, no Microsoft artwork in any form. Done when: the rules are a numbered list the §7 review can tick. Cheaper substitute: "make it look different".
- [ ] Commit: `brand: add icon design language`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/icon-language.md --require Grid --require Palette --require Motif --require "Distinctness rules" --require Accessibility` exits 0.

## 2. Suite Mark and Wordmark Masters

The suite mark appears on the splash screen, the Backstage account page, the website and GitHub graphics. The wordmark uses an open-licensed typeface whose licence permits logo use (SIL OFL 1.1 or equivalent), converted to outlines.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Draw `design/brand/suite-mark.svg` on the grid from `docs/brand/icon-language.md`. Done when: `python scripts/check-image-asset.py design/brand/suite-mark.svg --format svg` exits 0.
2. Build `design/brand/wordmark.svg` with outlined text. Done when: the file contains no `<text>` element.

- [ ] Draw the suite mark in `design/brand/suite-mark.svg` with a `viewBox="0 0 256 256"`. Done when: it renders legibly at 32 pixels in a browser preview. Cheaper substitute: a recoloured app icon.
- [ ] Choose the wordmark typeface and record its name and licence in `docs/brand/icon-language.md` under `## Wordmark`. Done when: the licence is OFL 1.1 or another licence permitting logo use. Cheaper substitute: Segoe UI or any Microsoft font.
- [ ] Outline the suite name in `design/brand/wordmark.svg`. Done when: `Select-String -Path design/brand/wordmark.svg -Pattern "<text"` finds nothing. Cheaper substitute: live text that renders differently without the font installed.
- [ ] Add a monochrome variant `design/brand/suite-mark-mono.svg` for single-colour contexts. Done when: the file uses one fill colour. Cheaper substitute: a CSS filter at render time.
- [ ] Commit: `brand: add suite mark and wordmark`

**Test checkpoint:** `python scripts/check-image-asset.py design/brand/suite-mark.svg --format svg` and the same for `design/brand/wordmark.svg` both exit 0.

## 3. Six App Icon Masters

One master SVG per app, drawn on the shared grid with the motif from §1. File names use the `kebab-case` identifiers from `docs/brand/NAMES.md`; the Microsoft counterpart is noted in a comment inside each file only.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Draw the six masters in `design/icons/apps/`. Done when: six SVGs exist and each passes the image-asset checker.
2. Render a contact sheet `build/icons/contact-sheet.png` at 256, 48 and 32 pixels. Done when: the sheet shows all six in a row at each size.

- [ ] Draw the word-processor icon (counterpart of Word) in `design/icons/apps/<writer-id>.svg`. Done when: it follows the grid and palette in `docs/brand/icon-language.md`. Cheaper substitute: a page with a large letter.
- [ ] Draw the spreadsheet icon (counterpart of Excel) in `design/icons/apps/<sheet-id>.svg`. Done when: it follows the grid and palette. Cheaper substitute: a plain green grid.
- [ ] Draw the presentation icon (counterpart of PowerPoint) in `design/icons/apps/<slides-id>.svg`. Done when: it follows the grid and palette. Cheaper substitute: an orange pie chart.
- [ ] Draw the diagram icon (counterpart of Visio) in `design/icons/apps/<diagram-id>.svg`. Done when: it follows the grid and palette. Cheaper substitute: three connected boxes in Visio blue.
- [ ] Draw the project-scheduling icon (counterpart of Project) in `design/icons/apps/<plan-id>.svg`. Done when: it follows the grid and palette. Cheaper substitute: three stacked green bars.
- [ ] Draw the mail and calendar icon (counterpart of Outlook) in `design/icons/apps/<mail-id>.svg`. Done when: it follows the grid and palette. Cheaper substitute: a blue envelope with a letter tile.
- [ ] Render `build/icons/contact-sheet.png` with `resvg` (the rasteriser §6 adopts) and review it at 32 pixels. Done when: each icon is distinguishable from the other five at 32 pixels. Cheaper substitute: reviewing only at 256 pixels.
- [ ] Commit: `brand: add six app icon masters`

**Test checkpoint:** `Get-ChildItem design/icons/apps/*.svg | ForEach-Object { python scripts/check-image-asset.py $_.FullName --format svg }` exits 0 for six files.

## 4. Small-Size App Icon Variants

Detail that reads at 256 pixels turns to mud at 16. Each app gets hand-simplified 16, 24 and 32 pixel variants aligned to the pixel grid instead of relying on downscaling.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Draw `<app-id>-16.svg`, `<app-id>-24.svg` and `<app-id>-32.svg` for each app in `design/icons/apps/`. Done when: 18 variant files exist with integer-aligned coordinates.

- [ ] Draw the 32 pixel variant for each app with `viewBox="0 0 32 32"` and integer-aligned edges. Done when: six `-32.svg` files exist. Cheaper substitute: the master with a smaller `width`.
- [ ] Draw the 24 pixel variant for each app with `viewBox="0 0 24 24"`. Done when: six `-24.svg` files exist. Cheaper substitute: downscaling the 32 pixel variant.
- [ ] Draw the 16 pixel variant for each app with `viewBox="0 0 16 16"`, keeping only the primary glyph. Done when: six `-16.svg` files exist. Cheaper substitute: downscaling the master.
- [ ] Commit: `brand: add small-size app icon variants`

**Test checkpoint:** `(Get-ChildItem design/icons/apps/*-16.svg, design/icons/apps/*-24.svg, design/icons/apps/*-32.svg).Count` returns 18 and each passes `python scripts/check-image-asset.py <file> --format svg`.

## 5. Document File-Type Icons

File Explorer, Finder and the Backstage recent list show file-type icons. Each type gets the owning app's glyph on a document shape distinct from Microsoft's file icons.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Draw one SVG per type in `design/icons/files/`. Done when: every type in the list below exists and passes the checker.

- [ ] Draw the word-processing types `docx.svg`, `docm.svg`, `dotx.svg`, `doc.svg`, `rtf.svg` and `odt.svg` in `design/icons/files/`. Done when: six files exist and the macro variant carries a visible macro badge. Cheaper substitute: one icon for every word type.
- [ ] Draw the spreadsheet types `xlsx.svg`, `xlsm.svg`, `xltx.svg`, `xls.svg`, `csv.svg` and `ods.svg`. Done when: six files exist. Cheaper substitute: reusing the app icon unchanged.
- [ ] Draw the presentation types `pptx.svg`, `pptm.svg`, `potx.svg`, `ppt.svg` and `odp.svg`. Done when: five files exist. Cheaper substitute: one icon for every presentation type.
- [ ] Draw the diagram types `vsdx.svg`, `vsdm.svg` and `vstx.svg`. Done when: three files exist. Cheaper substitute: reusing the app icon unchanged.
- [ ] Draw the project types `mpp.svg`, `mpt.svg` and the native project format icon named in `docs/brand/NAMES.md`. Done when: three files exist. Cheaper substitute: reusing the app icon unchanged.
- [ ] Draw the mail types `eml.svg`, `msg.svg`, `ics.svg` and `vcf.svg`. Done when: four files exist. Cheaper substitute: one envelope for all four.
- [ ] Commit: `brand: add document file-type icons`

**Test checkpoint:** `(Get-ChildItem design/icons/files/*.svg).Count` returns at least 27 and each passes `python scripts/check-image-asset.py <file> --format svg`.

## 6. Icon Export Pipeline

One command turns the SVG masters into every platform format, so icons are never exported by hand. The rasteriser is `resvg` (deterministic, no browser), installed per AGENTS.md tool rules: global install preferred, discovered by capability, never a hardcoded path.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/build-icons.py` that rasterises masters and size variants into `build/icons/`. Done when: a clean run produces every output listed in the micro-steps.
2. Verify every output with `scripts/check-image-asset.py`. Done when: the script exits non-zero on any failed check.

- [ ] Add tool discovery for `resvg` in `scripts/build-icons.py` (PATH lookup, then `RESVG` env var, then a setup-required error). Done when: running without `resvg` prints a setup message and exits 2. Cheaper substitute: a hardcoded `C:\Tools\resvg.exe` path.
- [ ] Rasterise each app icon to 16, 20, 24, 32, 40, 48, 64, 96, 128, 256, 512 and 1024 PNGs in `scripts/build-icons.py`, using the hand-drawn variant for 16, 24 and 32. Done when: `build/icons/apps/<app-id>/` holds 12 PNGs. Cheaper substitute: rasterising the master at every size.
- [ ] Pack Windows `.ico` files (16, 24, 32, 48, 64, 256) in `scripts/build-icons.py` with the standard library `struct` module. Done when: `python scripts/check-image-asset.py build/icons/apps/<app-id>.ico --size 16x16 --size 256x256` exits 0. Cheaper substitute: a single 256 pixel ICO entry.
- [ ] Pack macOS `.icns` files in `scripts/build-icons.py` from the 16 to 1024 PNGs. Done when: the file starts with the `icns` magic and lists the `ic07` to `ic10` types. Cheaper substitute: shipping PNGs and skipping macOS.
- [ ] Rasterise the file-type icons to 16, 32, 48 and 256 PNGs and ICOs in `scripts/build-icons.py`. Done when: `build/icons/files/` holds one ICO per SVG in `design/icons/files/`. Cheaper substitute: exporting only 256 pixels.
- [ ] Run `scripts/check-image-asset.py` on every output at the end of `scripts/build-icons.py`. Done when: corrupting one PNG makes the build exit 1 naming the file. Cheaper substitute: checking only that files exist.
- [ ] Add `build/` to `.gitignore` if it is not already ignored. Done when: `git check-ignore build/icons/apps` prints the path. Cheaper substitute: committing generated rasters.
- [ ] Commit: `brand: add icon export pipeline`

**Test checkpoint:** `python scripts/build-icons.py` exits 0 on a clean `build/`, and exits 1 after `Set-Content build/icons/apps/<app-id>/32.png "x"` followed by the verification pass.

## 7. Distinctness Review and Owner Sign-Off

The family is compared side by side with Microsoft's current app and file icons so the owner can confirm nothing could be mistaken for Microsoft's. The comparison sheet is built in `R:\scratch` and never committed, because it contains Microsoft artwork.

**Phase:** 1
**Needs:** owner-decision
**Surface:** no

**Build order:**

1. Build the comparison sheet in `R:\scratch` and tick each Distinctness rule from `docs/brand/icon-language.md`. Done when: `docs/brand/icon-distinctness.md` records a pass or fail per rule per icon.
2. Record the owner's sign-off. Done when: `docs/brand/icon-distinctness.md` has `## Sign-off` with the date.

- [ ] Build the side-by-side comparison sheet in `R:\scratch\icon-review\` from `build/icons/` and Microsoft's icons. Done when: the sheet exists outside the repository and `git status --short` shows no image from it. Cheaper substitute: committing Microsoft icons for reference.
- [ ] Record a pass or fail per Distinctness rule per icon in `docs/brand/icon-distinctness.md`. Done when: every app and file icon has a row and no cell is empty. Cheaper substitute: one overall verdict.
- [ ] Redraw any failed icon in its §3, §4 or §5 file and re-run `python scripts/build-icons.py`. Done when: every row in `docs/brand/icon-distinctness.md` reads pass. Cheaper substitute: changing only the colour of a failed icon.
- [ ] Record the owner's sign-off with date in `docs/brand/icon-distinctness.md` under `## Sign-off`, then remove the `owner-decision` Need. Done when: the section names the date and the decision. Cheaper substitute: treating silence as approval.
- [ ] Commit: `brand: record icon distinctness review`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/icon-distinctness.md --require Sign-off` exits 0 and `Select-String -Path docs/brand/icon-distinctness.md -Pattern "\| fail \|"` finds nothing.

## Verification

- `python scripts/build-icons.py` regenerates every asset from a clean `build/` and exits 0.
- `docs/brand/icon-distinctness.md` carries the owner's dated sign-off.
- `git ls-files design/ | Select-String -Pattern "microsoft" ` finds nothing.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
