# Icon distinctness review

The side-by-side distinctness review of the Rizonesoft Office icon family against Microsoft Office (`16.0.20527.20150`) and the delegated sign-off for D01 T02 §7. All comparison sheets containing Microsoft artwork live outside the repository in `R:/scratch/icon-review/` and are never committed.

## Symbol contrast

Decided 2026-10-22 by the owner. At the approved 15% darkening, the large (`lg`) app symbols crossed the blurred orb and dark block with too little contrast: the share of symbol pixels at 3:1 or more was Stage 46%, Mail 64%, Grid 75%, Plan 82%, Write 84% and Flow 100%, and the lowest pixel was 2.29:1.

The owner compared three versions on light and dark backgrounds, at 128 and 48 pixels:

| Version | Change | Lowest symbol pixel |
| --- | --- | --- |
| A | Approved: symbol 15% toward black, frost 42% white | 2.29:1 |
| B | Symbol 35% toward black | 3.31:1 |
| C | Frost 60% white | 3.17:1 |

The owner chose B. Every `lg` symbol pixel now reaches 3:1 or more (Stage lowest at 3.31:1), and the glass is unchanged. The `md` and `sm` drawings and the pixel-grid variants keep the 15% shade, which already met 3:1. The `Palette` tests in `scripts/tests/test_build_icons.py` now hold the `lg` tier to 3:1 too.

## Distinctness rules

The seven rules from `docs/brand/icon-language.md` (`## Distinctness rules`), checked across every drawing tier and size variant:

| Rule | Requirement from `docs/brand/icon-language.md` |
| --- | --- |
| `R1` | No single letter is any icon's main symbol. |
| `R2` | No letter on a tile or document sheet pairing a letter badge with an object. |
| `R3` | No Microsoft app or file icon artwork traced, redrawn or recoloured. |
| `R4` | No app colour matches a Microsoft app colour across all six counterparts. |
| `R5` | Every app symbol is an object or diagram of the app's work, not a brand mark. |
| `R6` | Every icon is built from the shared glass construction (orb, pane, symbol). |
| `R7` | The suite logo carries no text or letter inside the mark. |

Palette comparison for `R4` between `scripts/lib/icon_design.py` (`APPS`, `APP_COLOR`) and the primary colours sampled from Microsoft Office `16.0.20527.20150` (`WINWORD.EXE`, `EXCEL.EXE`, `POWERPNT.EXE`, `VISIO.EXE`, `WINPROJ.EXE`, `OUTLOOK.EXE`):

| App | Our light/dark/accent | MS EXE (`16.0.20527.20150`) | Sampled MS hexes |
| --- | --- | --- | --- |
| `write` | `#4f8df7`/`#1e4fc2`/`#366edc` | `WINWORD.EXE` | `#3bd5ff`/`#1657f4`/`#0036c4` |
| `grid` | `#34c27a`/`#0f7a45`/`#229e60` | `EXCEL.EXE` | `#79e96d`/`#4aa647`/`#15561c` |
| `stage` | `#ff8a4c`/`#d4421b`/`#ea6634` | `POWERPNT.EXE` | `#fdbb6e`/`#ff8d13`/`#b40c23` |
| `flow` | `#9b7bf7`/`#5b35c9`/`#7b58e0` | `VISIO.EXE` | `#41a5ee`/`#2b7cd3`/`#103f91` |
| `plan` | `#2dc2b5`/`#0b7f86`/`#1ca09e` | `WINPROJ.EXE` | `#33c481`/`#21a366`/`#185c37` |
| `mail` | `#3cc4f0`/`#0b7cc0`/`#229ed7` | `OUTLOOK.EXE` | `#1480d7`/`#127dd6`/`#0f78d4` |

Every hex in `APPS` and `APP_COLOR` is distinct from Microsoft's palette, and `flow` (violet `#9b7bf7` / `#5b35c9`) and `plan` (teal `#2dc2b5` / `#0b7f86`) depart completely in hue from Visio (blue) and Project (green).

## Suite and app icons

Side-by-side inspection on `R:/scratch/icon-review/suite-and-apps-comparison.png` across every distinct drawing (`lg` at 256 and 48 px, `md` at 40 px, pixel-grid `32` at 32 px, pixel-grid `24` at 24 px, `sm` at 20 px, and pixel-grid `16` at 16 px):

| Icon | Drawings | R1 | R2 | R3 | R4 | R5 | R6 | R7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rizonesoft-office` | `lg`, `md`, `sm` | pass | pass | pass | n/a | n/a | pass | pass |
| `rizonesoft-office-mono` | `md` knockout | pass | pass | pass | n/a | n/a | pass | pass |
| `write` | `lg`, `md`, `sm`, `32`, `24`, `16` | pass | pass | pass | pass | pass | pass | n/a |
| `grid` | `lg`, `md`, `sm`, `32`, `24`, `16` | pass | pass | pass | pass | pass | pass | n/a |
| `stage` | `lg`, `md`, `sm`, `32`, `24`, `16` | pass | pass | pass | pass | pass | pass | n/a |
| `flow` | `lg`, `md`, `sm`, `32`, `24`, `16` | pass | pass | pass | pass | pass | pass | n/a |
| `plan` | `lg`, `md`, `sm`, `32`, `24`, `16` | pass | pass | pass | pass | pass | pass | n/a |
| `mail` | `lg`, `md`, `sm`, `32`, `24`, `16` | pass | pass | pass | pass | pass | pass | n/a |

Visual comparison notes per icon:

- `rizonesoft-office` and `rizonesoft-office-mono`: a six-wedge colour orb rising upper-right behind a frosted rounded square pane holding a 2x3 grid of six rounded app squares (knocked out with a 5-unit gap in `rizonesoft-office-mono.svg`), with no letter or ribbon loop; Microsoft's suite icon (`misc.exe` group 2 and `FirstRunLogo.contrast-white_scale-100.png`) is a vertical lined sheet or an isometric hollow ribbon frame.
- `write` vs Microsoft Word (`WINWORD.EXE` group 0): Word pairs a left `W` letter tile over a tall four-band blue sheet; `write` uses a top-right blue orb (`#4f8df7` to `#1e4fc2`) behind a centred frosted glass pane with ragged-right horizontal text lines (four at `lg`, three at `md`/`32`, two at `sm`/`24`/`16`) and no letter tile.
- `grid` vs Microsoft Excel (`EXCEL.EXE` group 0): Excel pairs a left `X` letter tile over a multi-shade green quadrant sheet; `grid` uses a top-right emerald orb (`#34c27a` to `#0f7a45`) behind a centred glass pane containing a single-hue rounded table frame (`3x3` cells at `lg`, `2x2` stroked cells at `md`/`32`, four solid cells at `sm`/`24`/`16`) and no letter tile.
- `stage` vs Microsoft PowerPoint (`POWERPNT.EXE` group 0): PowerPoint pairs a left `P` letter tile over a circular pie chart disc; `stage` uses a top-right orange orb (`#ff8a4c` to `#d4421b`) behind a centred glass pane containing a rectangular presentation screen on a stand (with three vertical rising bar columns inside the screen at `lg`, an open screen on a stand at `md`/`32`, and a solid screen on a stand at `sm`/`24`/`16`) and never uses a circular pie chart or letter tile.
- `flow` vs Microsoft Visio (`VISIO.EXE` group 0): Visio pairs a blue `V` letter tile with overlapping blue diamond, square and circle slabs; `flow` shifts hue to violet (`#9b7bf7` to `#5b35c9`) and places a node-link diagram (a rounded square and two circles joined by three straight connectors at `lg`, one square and one circle joined by a diagonal connector at `md`/`32`/`sm`/`24`/`16`) inside the centred glass pane.
- `plan` vs Microsoft Project (`WINPROJ.EXE` group 0): Project pairs a green `P` letter tile with three wide overlapping green horizontal slabs; `plan` shifts hue to teal (`#2dc2b5` to `#0b7f86`) and places staggered capsule Gantt bars inside the centred glass pane (three bars at `lg`/`md`/`32`, two bars at `sm`/`24`/`16`) with no letter tile.
- `mail` vs Microsoft Outlook (`OUTLOOK.EXE` group 0): Outlook pairs a left `O` letter tile with an open blue envelope from which a calendar/document card emerges upward; `mail` uses a top-right sky-blue orb (`#3cc4f0` to `#0b7cc0`) behind a centred glass pane holding a closed rectangular envelope with a V-flap (`lg`/`md`/`32` stroked, `sm`/`24`/`16` solid with a white V-flap) and no emerging card or letter tile.

## File-type icons

Side-by-side inspection on `R:/scratch/icon-review/file-types-comparison.png` across all 26 document file types in `scripts/lib/filetype_design.py` (`TYPES`) and all five distinct drawings per type (`lg` at 128 px, `lg-badge-md` at 64 px, `lg-badge-sm` at 48 px, `md` at 32 px, and `sm` at 16 px) against Microsoft's installer icon libraries (`wordicon.exe`, `xlicons.exe`, `pptico.exe`, `visicon.exe`, `pj11icon.exe`, `outicon.exe`):

| Type | App | Kind | Drawings | R1 | R2 | R3 | R4 | R5 | R6 | R7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `docx` | `write` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `docm` | `write` | macro | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `dotx` | `write` | template | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `doc` | `write` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `rtf` | `write` | plain | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `odt` | `write` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `xlsx` | `grid` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `xlsm` | `grid` | macro | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `xltx` | `grid` | template | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `xls` | `grid` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `csv` | `grid` | plain | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `ods` | `grid` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `pptx` | `stage` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `pptm` | `stage` | macro | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `potx` | `stage` | template | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `ppt` | `stage` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `odp` | `stage` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `vsdx` | `flow` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `vsdm` | `flow` | macro | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `vstx` | `flow` | template | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `mpp` | `plan` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `mpt` | `plan` | template | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `eml` | `mail` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `msg` | `mail` | normal | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `ics` | `mail` | calendar | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |
| `vcf` | `mail` | contact | 5 (`lg`..`sm`) | pass | pass | pass | pass | pass | pass | n/a |

Visual comparison notes across the file-type families:

- Composition (`R1`, `R2`, `R6`): Microsoft's document icons (`wordicon.exe`, `xlicons.exe`, `pptico.exe`, `visicon.exe`, `pj11icon.exe`) place a solid `W`, `X`, `P` or `V` letter tile on the left edge of the sheet with no extension pill, and `outicon.exe` uses bare monochrome outline drawings (`eml`/`msg` envelope, `ics` calendar, `vcf` contact card) with no app badge at all. Every Rizonesoft Office file icon uses the white folded-corner page (`PAGE` / `FOLD`), an app-coloured content hint (or `#c3cad6` plain-grey hint on `rtf` and `csv`), the complete orb-and-glass app icon badge at the lower-left edge (`BADGE`, using `lg`, `md` or `sm` to match the badge's own displayed size), and at `>= 48 px` an outlined uppercase extension pill (`DOCX`, `XLSX`, `PPTX`, etc., which is the multi-letter format tag on the bottom-right of the page, never a single-letter app symbol).
- Kind markers (`R3`, `R5`): macro-enabled formats (`docm`, `xlsm`, `pptm`, `vsdm`) carry a circular amber (`#f59f0b`) exclamation mark at the lower right (whereas Microsoft overlays an exclamation scroll shield onto the document graphic), and templates (`dotx`, `xltx`, `potx`, `vstx`, `mpt`) combine a full-perimeter dashed page border (`stroke-dasharray`) with the lower-left glass app badge and lower-right outlined extension pill (`DOTX`, `XLTX`, `POTX`, `VSTX`, `MPT`), whereas Microsoft's `dotx`, `xltx` and `potx` pair a dashed sheet with a left-edge `W`, `X` or `P` letter tile and no extension pill, and Microsoft's `vstx` and `mpt` use a solid top header band with a left-edge `V` or `P` letter tile.

## Sign-off

- **Date:** 2026-11-08
- **Delegated authority:** Per `docs/specs/2026-10-23-campaign-scope-design.md` (decision 3), the owner delegated the D01 T02 §7 distinctness sign-off to the pinned independent reviewer, recorded here with full reference and digest evidence so the owner can audit it later.
- **Reviewer:** Pinned independent reviewer entry `astra` from `.conclave/reviewers.toml` (routed for writer `claude` via `codex` at `medium` reasoning effort, `adversarial` review type).
- **Verdict:** `pass` across all seven distinctness rules (`R1` to `R7`) for `rizonesoft-office` (`lg`, `md`, `sm`), `rizonesoft-office-mono` (`md` knockout), all six apps (`write`, `grid`, `stage`, `flow`, `plan`, `mail` across `lg`, `md`, `sm` and pixel-grid `32`, `24`, `16`), and all 26 file types (`docx`, `docm`, `dotx`, `doc`, `rtf`, `odt`, `xlsx`, `xlsm`, `xltx`, `xls`, `csv`, `ods`, `pptx`, `pptm`, `potx`, `ppt`, `odp`, `vsdx`, `vsdm`, `vstx`, `mpp`, `mpt`, `eml`, `msg`, `ics`, `vcf` across `lg`, `lg-badge-md`, `lg-badge-sm`, `md`, `sm`), with zero failed cells and zero redraws required.
- **Independent verification status:** Round 1 in `docs/reviews/01-brand/D01-T02-s7.md` (`2026-11-08T11:19:28Z`, digest `77828b64d456e3b8`) verified the 991 generated assets and both retained comparison sheets in `R:/scratch/icon-review/` against their dimensions, byte counts and SHA-256 digests; section sign-off is authoritative once `docs/reviews/01-brand/D01-T02-s7.md` records `OVERALL: approve` and `python scripts/todo-graph.py stamp` writes `docs/reviews/d01-t02-s7.json`.
- **Review records:** `docs/reviews/01-brand/D01-T02-s7-completion.md` (completion review), `docs/reviews/01-brand/D01-T02-s7.md` (independent code and distinctness review), and `docs/reviews/d01-t02-s7.json` (stamped verification receipt).
- **Audited icon asset revision and generator SHA-256 digests:**
  - Icon export pipeline baseline commit: `c68c65f8bff1a1d8a3bea86c2b652821cc191231` (`D01 T02 §6`, verified unchanged by `python scripts/build-icons.py --check`)
  - `scripts/lib/icon_design.py`: `6094e3b092fdcdbe133533bcadec34df809b6d5b730eb81d4326d894c491a61a`
  - `scripts/lib/filetype_design.py`: `07c65072f0af32145f6c49e3cd07632c316f845038deba08d0291d65fde0d7e1`
  - `scripts/lib/brand_design.py`: `9a919997e601ec529a2b2d6d41acd6b8194fddca9d1869b50338b5a62212b5cf`
  - `scripts/build-icons.py`: `a8b4e103f2e17aa21294fb967ea1841f93bfe7f7e45adacb36f26910d014a074`
- **Microsoft Office reference sources (`16.0.20527.20150`):**
  - App icons: `C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE`, `EXCEL.EXE`, `POWERPNT.EXE`, `VISIO.EXE`, `WINPROJ.EXE`, `OUTLOOK.EXE` (RT_GROUP_ICON index 0), and `LogoImages/FirstRunLogo.contrast-white_scale-100.png`.
  - Suite and file-type icons: `C:/Program Files/Microsoft Office/Root/VFS/Windows/Installer/{90160000-000F-0000-1000-0000000FF1CE}/misc.exe` (group 2), `wordicon.exe` (groups 1, 13, 14, 15, 17), `xlicons.exe` (groups 1, 4, 9, 28, 30, 32), `pptico.exe` (groups 10, 11, 17, 19, 20), `visicon.exe` (groups 1, 3, 13), `pj11icon.exe` (groups 1, 6), and `outicon.exe` (groups 1, 2, 3).
- **Retained comparison sheets in `R:/scratch/icon-review/` (untracked outside the repository):**
  - `R:/scratch/icon-review/suite-and-apps-comparison.png`: `2210x2460` px, `569102` bytes, `sha256:f8c168c821b99078cb4212b8a9cf28994dede9ce7156d95f890c5f56ca6e26e8`
  - `R:/scratch/icon-review/file-types-comparison.png`: `1500x4428` px, `923531` bytes, `sha256:71e7278bbee01f29981124be54b91e2c676b2d287751e668661869b6e421215e`
  - `R:/scratch/icon-review/manifest.json`: machine-readable manifest of the comparison run.
