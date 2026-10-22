---
schema_version: 1
id: icon-system
domain: 01-brand
status: active
title: "TODO-02 -- Suite and App Icon System"
---

# TODO-02 -- Suite and App Icon System

> **Goal:** The suite has an original icon family: a suite mark and wordmark, six app icons, small-size variants, and document file-type icons, all as SVG masters with a reproducible export to PNG, ICO and ICNS. No icon reuses Microsoft's composition (a letter tile overlapping a document or grid card), Microsoft's artwork, or the Fluent app-icon style, and the owner signs off a side-by-side distinctness review.

> **Current state:** Measured 2026-10-20. The owner-approved designs are generated in code, not hand-drawn. `scripts/lib/icon_design.py` draws the suite and app icons (`lg`, `md`, `sm`), `scripts/lib/filetype_design.py` the 26 document file types (Labelled direction), and `scripts/lib/brand_design.py` the wordmark and lockups in Plus Jakarta Sans, outlined through `scripts/lib/text_outline.py` (HarfBuzz shaping, font in `design/fonts/plus-jakarta-sans/` with its OFL). `scripts/build-icons.py` writes SVG masters to `design/icons/` and 961 verified files to `assets/icons/` and `assets/brand/` (PNG, ICO, ICNS, Linux hicolor apps and mimetypes, web favicons, lockups, `palette.json`), with `--check` for drift and tests in `scripts/tests/test_build_icons.py`. The rasteriser is the `resvg_py` binding pinned in `scripts/requirements.txt`, not the `resvg` CLI. Still missing: the brief `docs/brand/icon-language.md` (§1), the monochrome suite mark (§2), the distinctness review (§7), and stamps for the shipped work. `scripts/check-image-asset.py` (D00 T01 §2) does not exist; `build-icons.py` verifies its own outputs with Pillow.

## Inputs

- `docs/brand/NAMES.md` (from D01 T01 §3): suite Rizonesoft Office and the app names Write, Grid, Stage, Flow, Plan and Mail (decided 2026-10-20). The names carry no visual motif, so §1 chooses one.
- Microsoft 365 app icons (2019 and 2025 redesigns) as a reference for what to avoid only; never copied, traced or committed. Reference screenshots stay in `R:\scratch`.
- Platform icon requirements: Windows app icons (ICO with 16, 24, 32, 48, 64, 256), macOS ICNS (16 to 1024 at 1x and 2x), Linux hicolor PNG sizes (16 to 512), and favicon sizes for any web build.
- -> XREF: D01 T01 §3 -- names and motif come from the recorded naming decision
- -> XREF: D00 T01 §2 -- every exported asset is verified by `scripts/check-image-asset.py`
- -> XREF: D01 T03 §2 -- the social preview and README lineup use the masters from §2 and §3
- -> XREF: D02 T02 §2 -- the command glyph library must sit visually with the app icons defined in §1
- -> XREF: D03 T01 §5 -- names Plan's native extension, whose file-type icon §5 defers to it

## Outcome

- `design/icons/suite/` holds the suite mark (`rizonesoft-office-lg.svg`, `-md`, `-sm`, `-mono`) and `assets/brand/svg/` the outlined wordmark and lockups (corrected 2026-10-22 from `design/brand/`); `design/icons/apps/` holds one master SVG per app plus 16, 24 and 32 pixel variants; `design/icons/files/` holds one SVG per supported file type.
- `python scripts/build-icons.py` regenerates `build/icons/` (PNG sets, `.ico`, `.icns`) from the masters, and every output passes `scripts/check-image-asset.py`.
- `docs/brand/icon-distinctness.md` records the side-by-side review against Microsoft's icons and the owner's sign-off.

**Adjacency:** all=not-applicable (brand artwork and its build script; no user records, settings or permissions)

**Adjacency rationale:** Icons are static assets. The product surfaces that display them (taskbar, title bar, Backstage, file associations) are owned by the shared platform domain authored from D03 T01 §13.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Icon design language brief | D01 T01 §3 | [x] |
| 2 | §2 | Suite mark and wordmark masters | §1 | [x] |
| 3 | §3 | Six app icon masters | §1 | [x] |
| 4 | §4 | Small-size app icon variants | §3 | [x] |
| 5 | §5 | Document file-type icons | §3 | [x] |
| 6 | §6 | Icon export pipeline | §2, §4, §5, D00 T01 §2 | [ ] |
| 7 | §7 | Distinctness review and owner sign-off | §6 | [ ] |

## 1. Icon Design Language Brief

> **Started:** 2026-10-22T02:20:00Z

The brief fixes grid, keylines, corner radius, palette and the motif before any icon is drawn, so six icons drawn on different days still read as one family. It also writes down the distinctness rules that keep the family clear of Microsoft's look.

Motif status, 2026-10-20: the owner rejected the interlocking-tile drafts (five renderings of pentomino tiles). A second round (folded paper, orbit discs, Bauhaus blocks, isometric objects, die-cut stickers) was also rejected, and the owner asked for a style closer to Microsoft 365. Third round: layered cards, glass, folded corner, app tile and Fluent-style objects, using the industry category colours (documents blue, spreadsheets green, presentations orange) and never a letter tile. The owner chose Glass on 2026-10-20 and asked for simpler 16 and 32 pixel drawings and a reworked suite logo. Decision, 2026-10-20: app icons use the draft 3 Glass drawing (orb, dark block, frosted pane, deep-colour symbol) at 48 pixels and up, and the draft 4 Variation A drawing (orb and pane, flat tint, heavier symbol at 32 and 40, solid symbol at 16 to 24) below 48; the suite logo is Variation A at every size (six-colour orb behind glass, one square per app on the glass). §4 draws the small variants to this split. The concept sheet is the private artifact https://claude.ai/artifact/UFcUNAwH9LCsf57YfCesUS.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/brand/icon-language.md` with Grid, Palette, Motif, Distinctness rules and Accessibility headings. Done when: the design-doc checker passes with those headings.

- [x] Define the master grid in `docs/brand/icon-language.md`: 128 unit canvas, keyline shapes, safe area and corner radius. Done when: the numbers are stated and a keyline SVG `design/icons/keylines.svg` exists. **Corrected 2026-10-22:** said a 256 unit canvas; the approved drawings in `scripts/lib/icon_design.py` are on 128 units, rasterised to every size. The keyline SVG is generated by `keylines_svg()` from the icons' own constants. Cheaper substitute: "consistent rounded squares" with no numbers.
- [x] Define the per-app palette in `docs/brand/icon-language.md` with hex values and a contrast check against white and `#1f1f1f` backgrounds. Done when: each app colour reaches at least 3:1 against both backgrounds. Cheaper substitute: reusing Microsoft's blue, green, orange, teal and purple app colours one for one.
- [x] Record the owner's chosen concept from the review in this section in `docs/brand/icon-language.md`: the concept, how the suite logo is built, and each app's object or glyph. Done when: the concept and date are recorded and each of the six apps has one sentence naming its glyph. Cheaper substitute: a letter on a tile.
- [x] Write the Distinctness rules in `docs/brand/icon-language.md`: no single letter as the main glyph, no letter tile, no Microsoft app or file icon artwork in any form (the MIT-licensed Fluent UI System Icons chosen for ribbon commands on 2026-10-20 are allowed). Done when: the rules are a numbered list the §7 review can tick. Cheaper substitute: "make it look different".
- [x] Commit: `brand: add icon design language`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/icon-language.md --require Grid --require Palette --require Motif --require "Distinctness rules" --require Accessibility` exits 0.

> **Verified:** 2026-10-22 | §1 | bc9d6f4a1f394f90eeaa657328537735d11a9ff4
> **Review:** `docs/reviews/d01-t02-s1.json`

## 2. Suite Mark and Wordmark Masters

> **Started:** 2026-10-22T05:45:00Z

The suite mark appears on the splash screen, the Backstage account page, the website and GitHub graphics. The wordmark uses an open-licensed typeface whose licence permits logo use (SIL OFL 1.1 or equivalent), converted to outlines. Decision, 2026-10-20 (owner): Plus Jakarta Sans, "Rizonesoft" in weight 700 and the product name in weight 400 in a quieter colour; lockups pair it with the suite or app icon, in light and dark versions.

**Corrected 2026-10-22:** the plan named hand-drawn files in `design/brand/`. The owner-approved marks are generated (`scripts/lib/icon_design.py`, `scripts/lib/brand_design.py`) by `python scripts/build-icons.py`, which writes the suite mark with the other icon masters in `design/icons/suite/` and the wordmark and lockups in `assets/brand/svg/`; the paths below follow it rather than adding copies.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Generate the suite mark on the grid from `docs/brand/icon-language.md` as `design/icons/suite/rizonesoft-office-lg.svg`. Done when: `python scripts/check-image-asset.py design/icons/suite/rizonesoft-office-lg.svg --format svg` exits 0.
2. Generate the outlined wordmark `assets/brand/svg/rizonesoft-office-wordmark-light.svg` (and `-dark.svg`). Done when: the file contains no `<text>` element.

- [x] Draw the suite mark in `design/icons/suite/rizonesoft-office-lg.svg` with a `viewBox="0 0 128 128"`. **Corrected 2026-10-22:** said 256; every icon master is on the 128-unit grid that §1 records in `docs/brand/icon-language.md`. Done when: it renders legibly at 32 pixels in a resvg rendering (the rasteriser every exported icon uses; the browser extension was not connected). **Corrected 2026-10-22:** said a browser preview, and `design/brand/suite-mark.svg`. Cheaper substitute: a recoloured app icon.
- [x] Choose the wordmark typeface and record its name and licence in `docs/brand/icon-language.md` under `## Wordmark`. Done when: the licence is OFL 1.1 or another licence permitting logo use. Cheaper substitute: Segoe UI or any Microsoft font.
- [x] Outline the suite name in `assets/brand/svg/rizonesoft-office-wordmark-light.svg` and `-dark.svg`. Done when: `Select-String -Path assets/brand/svg/*.svg -Pattern "<text"` finds nothing. **Corrected 2026-10-22:** said `design/brand/wordmark.svg`. Cheaper substitute: live text that renders differently without the font installed.
- [x] Add a monochrome variant `design/icons/suite/rizonesoft-office-mono.svg` for single-colour contexts, generated by `suite_mono_svg()`. Done when: the file uses one fill colour. **Corrected 2026-10-22:** said `design/brand/suite-mark-mono.svg`. Cheaper substitute: a CSS filter at render time.
- [x] Commit: `brand: add suite mark and wordmark`

**Test checkpoint:** `python scripts/check-image-asset.py design/icons/suite/rizonesoft-office-lg.svg --format svg`, the same for `design/icons/suite/rizonesoft-office-mono.svg` and for `assets/brand/svg/rizonesoft-office-wordmark-light.svg` all exit 0. **Corrected 2026-10-22:** named the `design/brand/` paths.

> **Verified:** 2026-10-22 | §2 | 5e4ba4113a05be7238807957bf0ea85aeca1398d
> **Review:** `docs/reviews/d01-t02-s2.json`

## 3. Six App Icon Masters

> **Started:** 2026-10-22T06:50:00Z

One master SVG per app, drawn on the shared grid with the motif from §1. File names use the `kebab-case` identifiers from `docs/brand/NAMES.md`; the Microsoft counterpart is noted in a comment inside each file only.

**Corrected 2026-10-22:** the masters are generated by `python scripts/build-icons.py` from `scripts/lib/icon_design.py` as `design/icons/apps/<app>-<tier>.svg`, one per tier (`lg`, `md`, `sm`), 18 files. File names use the app key (`write`, `grid`, `stage`, `flow`, `plan`, `mail`), the bare word `docs/brand/NAMES.md` gives as the in-app label, as the PNG, ICO and ICNS outputs under `assets/icons/` do; the Linux files use the app id (`com.rizonesoft.Write`) and the lockups the full `rizonesoft-<app>` form. The counterpart comment is added to the masters only (`app_master_svg`); shipped icons carry none.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Generate the six masters, three tiers each, in `design/icons/apps/`. Done when: 18 SVGs exist and each passes the image-asset checker.
2. Render a contact sheet `build/icons/contact-sheet.png` at 256, 48 and 32 pixels with `python scripts/build-icons.py --contact-sheet build/icons/contact-sheet.png`. Done when: the sheet shows all six in a row at each size.

- [x] Draw the word-processor icon (counterpart of Word) in `design/icons/apps/write-<tier>.svg`. Done when: it follows the grid and palette in `docs/brand/icon-language.md`. Cheaper substitute: a page with a large letter.
- [x] Draw the spreadsheet icon (counterpart of Excel) in `design/icons/apps/grid-<tier>.svg`. Done when: it follows the grid and palette. Cheaper substitute: a plain green grid.
- [x] Draw the presentation icon (counterpart of PowerPoint) in `design/icons/apps/stage-<tier>.svg`. Done when: it follows the grid and palette. Cheaper substitute: an orange pie chart.
- [x] Draw the diagram icon (counterpart of Visio) in `design/icons/apps/flow-<tier>.svg`. Done when: it follows the grid and palette. Cheaper substitute: three connected boxes in Visio blue.
- [x] Draw the project-scheduling icon (counterpart of Project) in `design/icons/apps/plan-<tier>.svg`. Done when: it follows the grid and palette. Cheaper substitute: three stacked green bars.
- [x] Draw the mail and calendar icon (counterpart of Outlook) in `design/icons/apps/mail-<tier>.svg`. Done when: it follows the grid and palette. Cheaper substitute: a blue envelope with a letter tile.
- [x] Render `build/icons/contact-sheet.png` with `resvg` (the rasteriser §6 adopts) and review it at 32 pixels. Done when: each icon is distinguishable from the other five at 32 pixels. Cheaper substitute: reviewing only at 256 pixels.
- [x] Commit: `brand: add six app icon masters`

**Test checkpoint:** `Get-ChildItem design/icons/apps/*.svg | ForEach-Object { python scripts/check-image-asset.py $_.FullName --format svg }` exits 0 for 18 files. **Corrected 2026-10-22:** said six files; each app has three tier masters.

> **Verified:** 2026-10-22 | §3 | 84e31a1a6f1b068ac12bb3eaaab50b9bffdcdf32
> **Review:** `docs/reviews/d01-t02-s3.json`

## 4. Small-Size App Icon Variants

> **Started:** 2026-10-22T07:40:00Z

Detail that reads at 256 pixels turns to mud at 16. Each app gets hand-simplified 16, 24 and 32 pixel variants aligned to the pixel grid instead of relying on downscaling.

**Corrected 2026-10-22:** the variants are generated, as every other master is: `pixel_svg()` in `scripts/lib/icon_design.py` redraws each app's approved small design (`sm` for 16 and 24, `md` for 32, the split the owner chose on 2026-10-20) on the pixel grid, and `python scripts/build-icons.py` writes them. File names use the app key, as the §3 masters do.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Draw `<app-id>-16.svg`, `<app-id>-24.svg` and `<app-id>-32.svg` for each app in `design/icons/apps/`. Done when: 18 variant files exist with integer-aligned coordinates.

- [x] Draw the 32 pixel variant for each app with `viewBox="0 0 32 32"` and integer-aligned edges. Done when: six `-32.svg` files exist. Cheaper substitute: the master with a smaller `width`.
- [x] Draw the 24 pixel variant for each app with `viewBox="0 0 24 24"`. Done when: six `-24.svg` files exist. Cheaper substitute: downscaling the 32 pixel variant.
- [x] Draw the 16 pixel variant for each app with `viewBox="0 0 16 16"`, keeping only the primary glyph. Done when: six `-16.svg` files exist. Cheaper substitute: downscaling the master.
- [x] Commit: `brand: add small-size app icon variants`

**Test checkpoint:** `(Get-ChildItem design/icons/apps/*-16.svg, design/icons/apps/*-24.svg, design/icons/apps/*-32.svg).Count` returns 18 and each passes `python scripts/check-image-asset.py <file> --format svg`.

> **Verified:** 2026-10-22 | §4 | b34a0e85d225b3d8d26871b39d5f39107cbe8d80
> **Review:** `docs/reviews/d01-t02-s4.json`

## 5. Document File-Type Icons

> **Started:** 2026-10-22T08:30:00Z

File Explorer, Finder and the Backstage recent list show file-type icons. Decision, 2026-10-20 (owner): the Office composition in the "Labelled" direction. A white page with a folded corner, a content hint in the app colour, an extension tag from 48 px, and the app's glass icon over the lower-left edge; templates dashed, macro files with an amber mark, CSV and RTF in plain grey. The badge uses the app icon drawing for its own displayed size: the large drawing only from 40 px, below that the 32 px drawing, below 32 px the 16 px drawing.

**Corrected 2026-10-22:** the icons are generated by `scripts/lib/filetype_design.py` through `python scripts/build-icons.py`, five drawings per type (`<ext>-lg.svg`, `-lg-badge-md`, `-lg-badge-sm`, `-md`, `-sm`, picked by displayed size), so the files are `<ext>-<variant>.svg`, not `<ext>.svg`. Plan's native format has no extension yet (`docs/brand/NAMES.md` leaves it to D03 T01 §5), so its icon cannot be drawn here: 26 types are drawn and the 27th is deferred.

> **Deferred:** Plan's native file-type icon, drawn once D03 T01 §5 names the extension -> XREF: D03 T01 §5

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Generate the drawings for every type in `design/icons/files/`. Done when: every type in the list below has its five drawings and each passes the checker.

- [x] Draw the word-processing types `docx`, `docm`, `dotx`, `doc`, `rtf` and `odt` in `design/icons/files/`. Done when: six types' drawings exist and the macro variant carries a visible macro badge. Cheaper substitute: one icon for every word type.
- [x] Draw the spreadsheet types `xlsx`, `xlsm`, `xltx`, `xls`, `csv` and `ods`. Done when: six types' drawings exist. Cheaper substitute: reusing the app icon unchanged.
- [x] Draw the presentation types `pptx`, `pptm`, `potx`, `ppt` and `odp`. Done when: five types' drawings exist. Cheaper substitute: one icon for every presentation type.
- [x] Draw the diagram types `vsdx`, `vsdm` and `vstx`. Done when: three types' drawings exist. Cheaper substitute: reusing the app icon unchanged.
- [x] Draw the project types `mpp` and `mpt`; the native project format icon is deferred to D03 T01 §5, which names its extension. Done when: two types' drawings exist and the deferral names its owner. **Corrected 2026-10-22:** asked for three, including the native format, which has no extension yet. Cheaper substitute: reusing the app icon unchanged.
- [x] Draw the mail types `eml`, `msg`, `ics` and `vcf`. Done when: four types' drawings exist. Cheaper substitute: one envelope for all four.
- [x] Commit: `brand: add document file-type icons`

**Test checkpoint:** `(Get-ChildItem design/icons/files/*.svg).Count` returns 130 (26 types, five drawings each) and each passes `python scripts/check-image-asset.py <file> --format svg`. **Corrected 2026-10-22:** said at least 27 files, one per type.

> **Verified:** 2026-10-22 | §5 | 3223a272eb18958337d574f287554ebfffa79acd
> **Review:** `docs/reviews/d01-t02-s5.json`

## 6. Icon Export Pipeline

> **Started:** 2026-10-22T09:20:00Z

One command turns the SVG masters into every platform format, so icons are never exported by hand. The rasteriser is `resvg` (deterministic, no browser), installed per AGENTS.md tool rules: global install preferred, discovered by capability, never a hardcoded path.

**Corrected 2026-10-22:** the pipeline was built before this section ran, to a different shape that stays: `scripts/build-icons.py` rasterises with the `resvg_py` binding pinned in `scripts/requirements.txt` (discovered by import, so no PATH or `RESVG` lookup), writes committed outputs to `assets/icons/` and `assets/brand/` rather than `build/`, so a checkout has the icons without the toolchain, and `python scripts/build-icons.py --check` in CI refuses any committed output that differs from a fresh build. Every output is checked before anything is written: each PNG, every ICO entry and every ICNS slot decoded with Pillow, and each SVG parsed as XML with an `svg` root. The paths and checks below follow it; this section added the pixel-grid variants (§4) to the app rasters at 16, 24 and 32 px.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. `scripts/build-icons.py` rasterises masters and size variants into `assets/icons/`. Done when: a run produces every output listed in the micro-steps.
2. Verify every output by decoding it back, and refuse drift with `--check`. Done when: the script exits non-zero on any failed check.

- [x] Add discovery for the rasteriser in `scripts/build-icons.py` (`rasteriser()` imports the pinned `resvg_py`, else a setup-required error). Done when: running without it prints a setup message and exits 2 (`test_missing_rasteriser_is_a_setup_error`). **Corrected 2026-10-22:** named a `resvg` executable on PATH or in `RESVG`. Cheaper substitute: a hardcoded `C:\Tools\resvg.exe` path.
- [x] Rasterise each app icon to 16, 20, 24, 32, 40, 48, 64, 96, 128, 256, 512 and 1024 PNGs in `scripts/build-icons.py`, using the hand-drawn variant for 16, 24 and 32. Done when: `assets/icons/png/<app>/` holds 12 PNGs and the 16, 24 and 32 px ones are the variants (`test_app_rasters_use_the_variant_at_its_size`). **Corrected 2026-10-22:** said `build/icons/apps/<app-id>/`. Cheaper substitute: rasterising the master at every size.
- [x] Pack Windows `.ico` files (16, 20, 24, 32, 40, 48, 64, 96, 128, 256) in `scripts/build-icons.py` with the standard library `struct` module. Done when: `python scripts/check-image-asset.py assets/icons/windows/<app>.ico --size 16x16 --size 256x256` exits 0. **Corrected 2026-10-22:** said `build/icons/apps/<app-id>.ico` and six sizes; the ICO holds ten. Cheaper substitute: a single 256 pixel ICO entry.
- [x] Pack macOS `.icns` files in `scripts/build-icons.py` from the 16 to 1024 PNGs. Done when: the file starts with the `icns` magic and lists the `ic07` to `ic10` types. Cheaper substitute: shipping PNGs and skipping macOS.
- [x] Rasterise the file-type icons to PNGs from 16 to 512 and ICOs in `scripts/build-icons.py`. Done when: `assets/icons/files/windows/` holds one ICO per type in `design/icons/files/`. **Corrected 2026-10-22:** said `build/icons/files/` and one ICO per SVG; each type has five drawings and one ICO. Cheaper substitute: exporting only 256 pixels.
- [x] Verify every output in `scripts/build-icons.py` (`verify()` decodes each PNG, ICO, ICNS and SVG back) and refuse drift with `--check`. Done when: corrupting one committed PNG makes `--check` exit 1 naming the file. **Corrected 2026-10-22:** named `scripts/check-image-asset.py` and the plain build, which rewrites a corrupted file. Cheaper substitute: checking only that files exist.
- [x] Add `build/` to `.gitignore` if it is not already ignored. Done when: `git check-ignore build/icons/apps` prints the path. Cheaper substitute: committing generated rasters with no drift gate. **Corrected 2026-10-22:** the rasters are committed on purpose, under the `--check` gate in CI; `build/` holds only the contact sheet.
- [ ] Commit: `brand: add icon export pipeline`

**Test checkpoint:** `python scripts/build-icons.py --check` exits 0 on a clean checkout, and exits 1 naming the file after `Set-Content assets/icons/png/<app>/<app>-32.png "x"` (run on a scratch copy with `--root`). **Corrected 2026-10-22:** named `build/` and the plain build.

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
- [ ] Put the measured `lg` symbol contrast from `docs/brand/icon-language.md` (Accessibility: 46% to 100% of symbol pixels at 3:1 or more) to the owner with a darker-symbol variant beside the approved one, and record the choice in `docs/brand/icon-distinctness.md`. Done when: the choice and date are recorded, and a darker symbol, if chosen, is built and the `Palette` test extended to `lg`. Cheaper substitute: leaving the measured contrast unmentioned at sign-off.
- [ ] Record the owner's sign-off with date in `docs/brand/icon-distinctness.md` under `## Sign-off`, then remove the `owner-decision` Need. Done when: the section names the date and the decision. Cheaper substitute: treating silence as approval.
- [ ] Commit: `brand: record icon distinctness review`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/icon-distinctness.md --require Sign-off` exits 0 and `Select-String -Path docs/brand/icon-distinctness.md -Pattern "\| fail \|"` finds nothing.

## Verification

- `python scripts/build-icons.py` regenerates every asset from a clean `build/` and exits 0.
- `docs/brand/icon-distinctness.md` carries the owner's dated sign-off.
- `git ls-files design/ | Select-String -Pattern "microsoft" ` finds nothing.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
