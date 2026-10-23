---
schema_version: 1
id: tech-stack
domain: 03-architecture
status: active
title: "TODO-01 -- Tech Stack and Foundation Plan"
---

# TODO-01 -- Tech Stack and Foundation Plan

> **Goal:** Every expensive-to-reverse technical choice for the suite is decided in a dated design record backed by a measured prototype where a claim needs proof: platform targets, GUI toolkit, text layout, graphics, file formats, spreadsheet calculation, mail protocols, storage and co-authoring, extensibility, fonts, and licensing. The decisions roll up into a foundation plan in `docs/plans/`, and the implementation TODO domains for the shared platform and the six apps are authored from it and from the parity inventory.

> **Current state:** Measured 2026-10-20. No code, no design records and no foundation plan exist; `docs/` holds only the Conclave-SDK workflow documents. On 2026-10-20 the owner first chose C++ with Qt 6 on Windows, macOS and Linux, then the same day replaced it with WinUI 3 (Windows App SDK) in C# on .NET 11, Windows only, shipped as an MSIX package and an Inno Setup installer (§1, §2); the product licence stays GPL-3.0-or-later (§11). **Revised 2026-10-22 (owner):** WinUI 3 and .NET are replaced by native C++ with our own GUI toolkit: C++23 (MSVC `/std:c++23preview`, moving to C++26 once MSVC ships a stable flag for it), Win32 windows custom-drawn with Direct2D on Direct3D 11 and DirectWrite, Windows only (x64 and Arm64), still shipped as MSIX and Inno Setup (§1, §2). Measured 2026-10-22: the host has Visual Studio 2026 18.11 with MSVC 14.51.36231, which accepts `/std:c++20`, `/std:c++23preview` and `/std:c++latest` but not `/std:c++23`, plus the CMake and vcpkg Visual Studio bundles; clang-cl is not installed. The WinUI 3 and .NET pin tooling still in the repository is retired by D00 T03 §10. The repository runs on a Windows 11 Pro host with WSL available.

## Inputs

- `design/SPEC.md` (D02 T02) and `design/inventory/**` (D02 T01): the surface every stack candidate must render and the parity bar it must reach.
- ECMA-376 and ISO/IEC 29500 (Office Open XML), and Microsoft Open Specifications ([MS-DOCX], [MS-XLSX], [MS-PPTX], [MS-VSDX], [MS-DOC], [MS-XLS], [MS-PPT], [MS-OXMSG], [MS-OXCMSG]), covered by the Microsoft Open Specification Promise: the file format sources for §5.
- IMAP4rev2 (RFC 9051), SMTP (RFC 5321), JMAP (RFC 8620, RFC 8621), CalDAV (RFC 4791), CardDAV (RFC 6352), iCalendar (RFC 5545), Microsoft Graph and Exchange Web Services documentation: the protocol sources for §7.
- Global rule: specs go to `docs/specs/YYYY-MM-DD-<topic>-design.md` and plans to `docs/plans/YYYY-MM-DD-<feature>.md`, dated on the day they are written.
- Microsoft Learn documentation for Direct2D, DirectWrite, the Text Services Framework, UI Automation providers, the Desktop Window Manager and per-monitor DPI awareness v2: the platform APIs the own GUI toolkit is built on (§2).
- Microsoft C/C++ language conformance by Visual Studio version (Microsoft Learn): which C++23 and C++26 features the pinned MSVC toolset implements (§2).
- `docs/specs/2026-10-23-campaign-scope-design.md`: the owner's scope and unattended-run decisions of 2026-10-22, cited by §1, §7, §8, §9 and §13 to §27.
- -> XREF: D02 T02 §4 -- the GUI toolkit must render the ribbon component chapter, including its scaling rules
- -> XREF: D02 T01 §28 -- the disposition field §14 sets on every cloud-backed inventory record
- -> XREF: D02 T01 §18 -- application TODO sections cite inventory ids so the coverage report can count implemented elements
- -> XREF: D02 T01 §22 -- the record-level ownership check that holds every inventory record to exactly one owning section
- -> XREF: D01 T01 §3 -- `docs/brand/NAMES.md` records Plan's own native format; §5 names its extension
- -> XREF: D00 T02 §2 -- the dependency licence policy decided in §11 is enforced through the third-party notices file
- -> XREF: D01 T02 §5 -- Plan's native file-type icon waits on the extension §5 names

## Outcome

- `docs/specs/` holds one dated design record per decision in §1 to §11, each with Context, Options, Measurements (where a prototype ran), Decision and Consequences, and each passing `scripts/check-design-doc.py`.
- `docs/plans/<date>-foundation-plan.md` names the architecture, repository layout, milestones and the order the six apps are built in.
- New TODO domains `04-platform` onward exist, validated, with every section citing inventory ids, so `process-plan` can run from the shared platform to the last app.

**Adjacency:** all=not-applicable (architecture decisions and plan authoring; the product surfaces they enable are owned by the domains §13 authors)

**Adjacency rationale:** This file decides how the product is built, not what a user sees. Each adjacency key (lists, documents, settings, reporting, notifications, permissions, audit, exchange, reverse) is declared by the platform and app TODO files that §13 authors, with owners resolved against this plan.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Platform targets decision | -- | [ ] |
| 2 | §2 | GUI toolkit decision with ribbon prototype | §1, D02 T02 §4 | [ ] |
| 3 | §3 | Text layout engine decision | §2 | [ ] |
| 4 | §4 | Graphics and canvas rendering decision | §2 | [ ] |
| 5 | §5 | File format strategy decision | §1 | [ ] |
| 6 | §6 | Spreadsheet calculation engine decision | §5 | [ ] |
| 7 | §7 | Mail and calendar protocol decision | §1 | [ ] |
| 8 | §8 | Storage and co-authoring decision | §2, §5 | [ ] |
| 9 | §9 | Extensibility and macro decision | §2, §6 | [ ] |
| 10 | §10 | Font strategy decision | §3 | [ ] |
| 11 | §11 | Product licence and dependency policy | -- | [ ] |
| 12 | §12 | Foundation plan | §4, §7, §8, §9, §10, §11, §14, §15, §16 | [ ] |
| 13 | §13 | Inventory ownership gate | §25, §26, §27, D02 T01 §22 | [ ] |
| 14 | §14 | Cloud feature equivalents decision | §2, D02 T01 §28 | [ ] |
| 15 | §15 | Localisation decision | §2 | [ ] |
| 16 | §16 | Updates and diagnostics decision | §1 | [ ] |
| 17 | §17 | Platform domain authoring | §12, §14, §15, §16, §28 | [ ] |
| 18 | §18 | Document engines domain authoring | §12 | [ ] |
| 19 | §19 | Write domain authoring | §17, §18, D02 T02 §14 | [ ] |
| 20 | §20 | Grid domain authoring | §17, §18, D02 T02 §14 | [ ] |
| 21 | §21 | Stage domain authoring | §17, §18, D02 T02 §14 | [ ] |
| 22 | §22 | Mail domain authoring | §17, §18, D02 T02 §14 | [ ] |
| 23 | §23 | Flow domain authoring | §17, §18, D02 T02 §14 | [ ] |
| 24 | §24 | Plan domain authoring | §17, §18, D02 T02 §14 | [ ] |
| 25 | §25 | Interoperability domain authoring | §19, §20, §21, §22, §23, §24 | [ ] |
| 26 | §26 | VBA domain authoring | §19, §20, §21, §22, §23, §24 | [ ] |
| 27 | §27 | Release domain authoring | §17, §28 | [ ] |
| 28 | §28 | Versioning and release identity decision | §1, §16 | [ ] |

## 1. Platform Targets Decision

Everything downstream depends on where the suite runs. Microsoft 365 ships native Windows and macOS apps, web apps and mobile apps; matching the Windows desktop first is the default implied by the inventory's reference build. Decision, 2026-10-20 (owner, revised the same day): Windows desktop only, x64 and Arm64, following the move to WinUI 3 in §2 and kept on 2026-10-22 with the move to native C++; macOS, Linux, web and mobile are out of scope. **Corrected 2026-10-20:** the first decision that day was Windows, macOS and Linux on C++ with Qt 6. Distribution, decided the same day: a signed MSIX package and an Inno Setup installer (Inno Setup 7.1.0, the latest release, is installed on the operator's host) for the unpackaged build. **Superseded 2026-10-22 (owner, `docs/specs/2026-10-23-campaign-scope-design.md`, decisions 11, 12 and 14):** no Microsoft Store and no signing for now, so the Inno Setup installer ships as draft GitHub releases and the MSIX package waits until the owner decides how to sign.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-platform-targets-design.md` with the options and the owner's decision. Done when: the design-doc checker passes with `Decision`.

- [ ] List the candidate targets (Windows x64 and Arm64, macOS, Linux, web browser, iOS, Android) with the cost each adds in the design record. Done when: each target names one stack constraint it imposes. Cheaper substitute: "cross-platform" with no list.
- [ ] Record the owner's 2026-10-20 decision (Windows desktop only, x64 and Arm64) under `## Decision`, with the earlier same-day decision it replaced. Done when: the decision names the targets, the date and what it replaced. Cheaper substitute: leaving macOS and Linux as an unstated maybe. **Corrected 2026-10-20:** said Windows, macOS and Linux with a release order.
- [ ] Record the distribution channels in `docs/specs/<dated>-platform-targets-design.md` under `## Decision`: an unsigned Inno Setup 7 installer of the native build (the MSVC runtime statically or app-local as §12 decides) published as draft GitHub releases and updated through GitHub Releases; no Microsoft Store; the MSIX package deferred until the owner decides signing, since Windows installs an MSIX only when it is signed (`docs/specs/2026-10-23-campaign-scope-design.md`, decisions 11, 12 and 14). Done when: the record names each channel, its update path and the deferred MSIX with its trigger. Cheaper substitute: listing a signed, Store-ready MSIX the owner has ruled out for now. **Corrected 2026-10-22:** carried the Windows App SDK runtime self-contained. **Corrected 2026-10-23:** recorded a signed, Store-ready MSIX and a signing certificate source.
- [ ] Record the minimum OS (Windows 11 24H2 and later, x64 and Arm64; owner decision 2026-10-22, `docs/specs/2026-10-23-campaign-scope-design.md`, decision 9) and the hardware baseline (RAM, display scaling range 100 to 500 percent) under `## Decision`. Done when: the record names the version, both architectures and the baseline. Cheaper substitute: "modern systems". **Corrected 2026-10-23:** left the minimum version open.
- [ ] Commit: `arch: record platform targets decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-platform-targets-design.md --require Options --require Decision --require Consequences` exits 0.

## 2. GUI Toolkit Decision with Ribbon Prototype

Decision, 2026-10-22 (owner): native C++ with our own GUI toolkit, replacing WinUI 3 in C# on .NET 11 (decided 2026-10-20, itself replacing C++ with Qt 6 chosen earlier that day). Language: C++23, compiled with MSVC `/std:c++23preview`, because MSVC 14.51 has no stable `/std:c++23` flag; the pin moves to C++26 (technically complete in March 2026, ISO publication pending) once MSVC ships a stable flag for it, the same latest-stable rule the WinUI 3 pin followed. Toolkit: Win32 top-level windows with per-monitor DPI awareness v2, and everything inside them custom-drawn with Direct2D on Direct3D 11 and DirectWrite; no XAML, no common controls and no third-party widget library. Owning the toolkit means owning what a framework gave for free: the ribbon and every control from the tokens in `design/SPEC.md`, layout, focus and keyboard navigation, text input through the Text Services Framework (TSF), accessibility through UI Automation providers, the custom title bar with Snap Layouts and Mica, and DPI scaling. The prototype below proves each of those before the record is written. The WinUI 3 feasibility run of 2026-10-20 (`R:\scratch\prototypes\winui3-feasibility\`: 239 ms median to a visible window with ReadyToRun, a Native AOT publish failing on .NET 11 RC with WMC1007, a 98 MB MSIX package) goes into the record under `## Options` as the rejected candidate.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Build the Word Home tab with the own toolkit (C++23, CMake, MSVC) in `R:\scratch\prototypes\native-ribbon\`. Done when: it renders every `word.home.*` control.
2. Measure it and the engine benchmark, and record the decision in `docs/specs/YYYY-MM-DD-gui-toolkit-design.md`. Done when: the checker passes with Measurements and Decision. **Corrected 2026-10-20:** compared Qt Widgets with Qt Quick. **Corrected 2026-10-22:** built a WinUI 3 prototype and wrote `shell-framework-design.md`.

- [ ] Build the Word Home tab with the Classic Ribbon in the own toolkit (Win32, Direct2D and DirectWrite) in `R:\scratch\prototypes\native-ribbon\`, driven by the `word.home.*` inventory records, with group scaling as the window narrows. Done when: every Home tab control renders at its inventoried size and the groups collapse in the order `design/SPEC.md` gives. Cheaper substitute: the Windows Ribbon Framework (`UIRibbon`), which cannot match Office's current ribbon layout or styling. **Corrected 2026-10-20:** was a Qt Widgets prototype. **Corrected 2026-10-22:** was a WinUI 3 (C#) prototype.
- [ ] Benchmark one engine-shaped workload (laying out and breaking the text runs of a 100-page document with DirectWrite) in `R:\scratch\prototypes\engine-benchmark\`. Done when: the time is under `## Measurements` with the budget it sets for §3. Cheaper substitute: assuming native code is fast enough. **Corrected 2026-10-20:** was a Qt Quick prototype. **Corrected 2026-10-22:** compared C# with a C++ library called from C# to set when an engine goes native.
- [ ] Draw a custom title bar: extend the frame with `DwmExtendFrameIntoClientArea`, remove the standard caption in `WM_NCCALCSIZE`, answer `WM_NCHITTEST` with `HTMAXBUTTON` over our maximise button, and set Mica with `DwmSetWindowAttribute` and `DWMWA_SYSTEMBACKDROP_TYPE`. Done when: hovering maximise on Windows 11 shows the Snap Layouts flyout and Mica shows behind the title bar. Cheaper substitute: the default title bar, which breaks the Office title bar layout. **Corrected 2026-10-22:** used `AppWindow.TitleBar` and `MicaBackdrop`.
- [ ] Add a custom text surface: DirectWrite text drawn with Direct2D, taking input through a TSF text store (`ITextStoreACP2`) and exposing its text and caret through a UI Automation `TextPattern` provider. Done when: typing Chinese (Microsoft Pinyin) and Japanese (Microsoft IME) composes in place with the candidate window at the caret, the touch keyboard and dictation (Win+H) insert text, and Narrator reads the text and caret. Cheaper substitute: a RichEdit window (`MSFTEDIT_CLASS`), which hides the input path the real editor must own. Owner request 2026-10-22. **Corrected 2026-10-22:** drew into a `SwapChainPanel` with input through `CoreTextEditContext`.
- [ ] Add a virtualized grid surface drawn with Direct2D with one million rows and 100 columns. Done when: scrolling and keyboard navigation hold 60 frames per second under `## Measurements`, and memory stays flat across a full scroll. Cheaper substitute: a list view (`WC_LISTVIEW`) in virtual mode, which has no cell editing or frozen panes. Owner request 2026-10-22. **Corrected 2026-10-22:** drew into a `SwapChainPanel` or Win2D `CanvasVirtualControl`.
- [ ] Open two prototype windows at once, each with its own ribbon, and move one between monitors with different scaling (`WM_DPICHANGED` under per-monitor DPI awareness v2). Done when: both windows stay responsive, keep their placement after a restart, and re-scale crisply on the second monitor. Cheaper substitute: one window. Owner request 2026-10-22.
- [ ] Add ribbon key tips (Alt, then the tab letter, then the control letters) driven by the `keytip` field of the `word.home.*` records. Done when: every Home tab key tip shows and runs its control from the keyboard alone. Cheaper substitute: accelerator tables alone, which show no key tips. Owner request 2026-10-22. **Corrected 2026-10-22:** named `KeyboardAccelerator`.
- [ ] Implement UI Automation providers (`IRawElementProviderSimple`, `IRawElementProviderFragment` and the control patterns each control type needs) for every prototype control. Done when: `scripts/capture-ui.py` reads each `word.home.*` control from the prototype at its inventoried name, control type and position, and Narrator announces every control. Cheaper substitute: MSAA `IAccessible` alone, which Narrator and the capture tool read poorly. Added 2026-10-22: a framework gave this for free, the own toolkit does not.
- [ ] Record every platform defect the prototype hits (Direct2D, DirectWrite, TSF, UI Automation, DWM) in `docs/specs/<dated>-gui-toolkit-design.md` under `## Known defects`, each with its upstream report, the `WORKAROUND:` it needs and the Windows build and MSVC toolset it was seen on, and define the smoke test (the text surface, grid, two windows, key tip and UI Automation steps above) that every MSVC toolset or Windows SDK upgrade must pass before its pin lands. Done when: the section lists each defect or states none was hit, and the smoke test is named in `## Decision`. Cheaper substitute: upgrading the toolset on release notes alone. Owner request 2026-10-22. **Corrected 2026-10-22:** tracked WinUI 3 defects and Windows App SDK upgrades.
- [ ] Measure cold start, idle memory, resize frame time while the ribbon scales, and the size of a Release build with the MSVC runtime linked statically and app-local. Done when: the numbers are under `## Measurements`. Cheaper substitute: vendor claims. **Corrected 2026-10-22:** measured ReadyToRun and Native AOT start-up and UIA tree correctness, which the UI Automation item above now owns.
- [x] Add `scripts/check-winui-pin.py`, which reads the pinned `Microsoft.WindowsAppSDK` version from the repository's package versions file and compares it with the newest stable `winui3/release/<version>` tag through `gh api`, exiting 1 when a newer stable release exists; CI and every phase start run it. Done when: a fixture pinned to 2.4.0 fails, the current pin passes, and an `-experimental` tag never counts as newer. Cheaper substitute: checking for new releases by hand. Done 2026-10-20: `Directory.Packages.props` holds the pin, and the daily `office-winui-pin` task (`.conclave/automations/`) proposes each newer stable release on a `winui/<version>` branch and emails the operator; `scripts/tests/test_check_winui_pin.py` covers the 2.4.0 fixture, the current pin and experimental releases. **Retired 2026-10-22:** the move to native C++ drops the WinUI 3 pin; D00 T03 §10 deletes the script, its tests and its task.
- [ ] Record the pins (the C++ standard flag, the MSVC toolset, the Windows SDK, CMake and the vcpkg baseline, each the latest stable release) and the date under `## Decision`, with the C++26 rule and the owner's confirmation. Done when: the decision names the toolkit, the language standard, every version and the date. Cheaper substitute: floating versions. **Corrected 2026-10-22:** pinned Windows App SDK 2.5.1, the .NET 11 release and ReadyToRun or Native AOT.
- [ ] Commit: `arch: record native C++ GUI toolkit decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-gui-toolkit-design.md --require Measurements --require Decision` exits 0.

## 3. Text Layout Engine Decision

Word fidelity depends on line breaking, justification, hyphenation, complex scripts, bidi text, tables, floats with text wrap, widows and orphans, and pagination that matches Word closely enough that a `.docx` keeps its page count. This record decides whether to build a layout engine on HarfBuzz and ICU, adopt an existing engine, or combine them. **Groomed 2026-10-23:** the page counts come from Word on this PC, so the section carries the `office` Need the campaign's readiness check reads.

**Phase:** 3
**Needs:** office, windows-host
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-text-layout-design.md`. Done when: the record passes the checker with Measurements.

- [ ] List the candidate approaches (own engine in C++ on DirectWrite, with `IDWriteTextAnalyzer` for shaping and our own line breaking, justification and pagination; own engine on HarfBuzz and ICU; LibreOffice Writer core) with licence and fit. Done when: each has licence, language and maintenance status with dates. Cheaper substitute: the RichEdit control (`MSFTEDIT_CLASS`) by default, which cannot paginate like Word. **Corrected 2026-10-20:** listed HarfBuzz plus ICU in C++ and Qt's `QTextLayout`. **Corrected 2026-10-22:** listed an own engine in C# on DWriteCore and the rich edit control behind `RichEditBox`.
- [ ] Assemble a 20-document `.docx` fidelity corpus in `R:\scratch\corpus\docx\` with page counts recorded from Word. Done when: the corpus list and page counts are in the record. Cheaper substitute: a single sample document.
- [ ] Measure page-count agreement for the top two approaches on the corpus. Done when: agreement percentages are under `## Measurements`. Cheaper substitute: visual impressions.
- [ ] Record the decision and its consequences for tables, floats and fields under `## Decision`. Done when: each of the three has a named owner component. Cheaper substitute: deciding text only.
- [ ] Commit: `arch: record text layout decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-text-layout-design.md --require Measurements --require Decision` exits 0.

## 4. Graphics and Canvas Rendering Decision

PowerPoint slides, Visio drawings, Excel charts, shapes in every app, and print and PDF output share one 2D rendering layer: paths, gradients, effects (shadow, glow, soft edges, reflection), text on shapes, images with crops and recolouring, and DrawingML fidelity.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-graphics-design.md`. Done when: the record passes the checker with Measurements.

- [ ] List candidates (Direct2D on Direct3D 11 with its built-in effects, the renderer the GUI toolkit already uses; Skia; Blend2D) with licence and fit. Done when: each has licence and a note on DrawingML effect support. Cheaper substitute: the toolkit's renderer without comparison. **Corrected 2026-10-20:** listed Qt's `QPainter`, Blend2D and per-platform renderers for macOS and Linux. **Corrected 2026-10-22:** listed Win2D, a `SwapChainPanel`, SkiaSharp and the Windows composition layer.
- [ ] Render a DrawingML effects test slide (shadow, glow, gradient, soft edges, picture crop) with the top two candidates in `R:\scratch\prototypes\graphics\`. Done when: per-effect support is recorded. Cheaper substitute: rendering rectangles only.
- [ ] Record PDF output strategy (same renderer to PDF, or separate PDF writer). Done when: the strategy names the library and its licence. Cheaper substitute: printing to the OS PDF printer.
- [ ] Record the decision under `## Decision`. Done when: renderer, version and date are named. Cheaper substitute: per-app renderer choices.
- [ ] Commit: `arch: record graphics decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-graphics-design.md --require Measurements --require Decision` exits 0.

## 5. File Format Strategy Decision

The suite reads and writes Microsoft's formats as first-class: `.docx`, `.xlsx`, `.pptx` (OOXML), `.vsdx` (Visio XML, OOXML packaging; **Corrected 2026-10-22:** was listed as OOXML), legacy `.doc`, `.xls`, `.ppt`, `.vsd`, Project `.mpp` and `.xml`, Outlook `.msg`, `.eml`, `.pst` and `.ics`, plus ODF, CSV, RTF and PDF export. This record decides per format: own implementation from the open specifications, an existing library, or read-only support.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-file-formats-design.md` with a per-format decision table. Done when: every format in this section has a row.

- [ ] Write the format table: format, read, write, specification, candidate library, licence. Done when: every format named in this section has a row at most 100 characters. Cheaper substitute: OOXML only.
- [ ] Decide the in-memory document model per app and whether it mirrors OOXML parts. Done when: the record states how unknown OOXML elements are preserved on round-trip. Cheaper substitute: dropping unknown elements on save.
- [ ] Assemble round-trip corpora (20 files each for `.docx`, `.xlsx`, `.pptx`, `.vsdx`) in `R:\scratch\corpus\`. Done when: corpus lists are in the record. Cheaper substitute: files created by our own writer.
- [ ] Record the `.mpp` decision (MPXJ, LGPL, read-only, which runs only on Java or .NET and so would run out of process beside a C++ build, versus an own reader) and the `.pst` decision. Done when: each states read and write scope. Cheaper substitute: silently excluding Project and Outlook stores. **Corrected 2026-10-22:** did not say MPXJ has no C++ build.
- [ ] Name Plan's native file extension and its format, and record it in `docs/brand/NAMES.md` under `## File formats`. Done when: the Plan row names the extension and `python scripts/check-design-doc.py docs/brand/NAMES.md` exits 0. Cheaper substitute: saving Plan's projects only as Project XML, which loses what Project XML cannot hold. (Deferred from D01 T01 §3 on 2026-10-22.)
- [ ] Add Plan's native extension to `TYPES` in `scripts/lib/filetype_design.py` (app `plan`, its MIME type) and run `python scripts/build-icons.py`, so its file-type icon is drawn (deferred from D01 T02 §5). Done when: `design/icons/files/<ext>-lg.svg` exists and passes `python scripts/check-image-asset.py <file> --format svg`, and the `FileTypes` test lists the extension. Cheaper substitute: reusing the `mpp` icon.
- [ ] Commit: `arch: record file format strategy`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-file-formats-design.md --require Decision --require "Round-trip"` exits 0.

## 6. Spreadsheet Calculation Engine Decision

Excel parity is mostly the calculation engine: the formula grammar, A1 and R1C1 references, structured references, dynamic arrays and spill, LAMBDA and LET, the dependency graph and recalculation modes, iterative calculation, roughly 500 worksheet functions, and number formatting.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-calc-engine-design.md`. Done when: the record passes the checker with Measurements.

- [ ] Extract the function list from `design/inventory/excel/ribbon.json` (Formulas tab function library) into the record with category counts. Done when: the total matches the inventory. Cheaper substitute: a function list from memory.
- [ ] List candidates (own engine in C++; LibreOffice Calc's formula core under MPL 2.0; IronCalc through its C interface) with licence, language and function coverage. Done when: each has a coverage percentage against the extracted list. Cheaper substitute: picking by stars. **Corrected 2026-10-22:** listed an own engine in C#, native where §2's benchmark rule called for it.
- [ ] Build a 200-formula conformance workbook from Microsoft function documentation examples in `R:\scratch\corpus\calc\` and measure the top two candidates. Done when: pass rates are under `## Measurements`. Cheaper substitute: testing SUM and VLOOKUP only.
- [ ] Record the decision, including recalculation strategy and floating-point compatibility rules (15 significant digits, Excel date serials, 1900 leap-year bug). Done when: each rule is stated. Cheaper substitute: IEEE behaviour without Excel's display rules.
- [ ] Commit: `arch: record calculation engine decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-calc-engine-design.md --require Measurements --require Decision` exits 0.

## 7. Mail and Calendar Protocol Decision

The Outlook counterpart must talk to real mailboxes: IMAP and SMTP for any provider, JMAP where offered, CalDAV and CardDAV for calendars and contacts, and Microsoft Graph or Exchange Web Services for Microsoft 365 and Exchange accounts, plus Gmail through its API or IMAP with OAuth. Decision, 2026-10-22 (owner, `docs/specs/2026-10-23-campaign-scope-design.md`, decision 7): 1.0 covers Microsoft 365 and Outlook.com through Microsoft Graph, Gmail through Google OAuth, iCloud through an app password, and any IMAP and SMTP server, with CalDAV and CardDAV; Exchange Web Services is not used, since Microsoft retires it for Exchange Online. The owner registers one Microsoft Entra application and one Google OAuth client; the sections that need them carry the `operator` Need.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-mail-protocols-design.md`. Done when: the record passes the checker with Decision.

- [ ] Write the account-type matrix: provider, mail protocol, calendar protocol, contacts protocol, authentication (OAuth 2.0 flows, app passwords). Done when: Microsoft 365, Outlook.com, Gmail, iCloud and generic IMAP each have a row. Cheaper substitute: IMAP only.
- [ ] Record the local store design: message cache format, offline mode, search index and sync state. Done when: the record names the store and its crash-safety guarantee. Cheaper substitute: online-only mail.
- [ ] Record the OAuth client registration needs per provider as owner actions. Done when: each provider lists what the owner must register. Cheaper substitute: embedding a client secret in the app.
- [ ] Record the decision under `## Decision`. Done when: libraries, versions and licences are named. Cheaper substitute: deciding per provider later.
- [ ] Commit: `arch: record mail protocol decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-mail-protocols-design.md --require Decision` exits 0.

## 8. Storage and Co-Authoring Decision

The title bar's AutoSave toggle and the Share button imply cloud storage and real-time co-authoring. This record decides local-first storage, AutoSave semantics, version history, the cloud backend (own service, WebDAV, OneDrive and SharePoint through Graph, other providers), and the merge model (CRDT such as Yjs or Automerge, or operational transform). Decision, 2026-10-20 (owner): the first release works on local and network files with AutoSave and recovery; OneDrive and SharePoint through Microsoft Graph, and real-time co-authoring, come in a later milestone. **Superseded 2026-10-22 (owner):** OneDrive and SharePoint move into 1.0; only co-authoring stays later (below). No Rizonesoft cloud service is planned. Confirmed 2026-10-22 (owner, `docs/specs/2026-10-23-campaign-scope-design.md`, decision 7): OneDrive and SharePoint open and save with AutoSave through Microsoft Graph are in 1.0; real-time co-authoring with Office users comes after 1.0.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-storage-collab-design.md`. Done when: the record passes the checker with Decision.

- [ ] Specify local save semantics: atomic write, crash recovery files, AutoRecover interval and Document Recovery pane. Done when: each has a named mechanism. Cheaper substitute: overwrite in place.
- [ ] Compare CRDT and OT for each app's document model from §5. Done when: each app has a chosen merge model and its conflict cases. Cheaper substitute: last writer wins.
- [ ] Record the 2026-10-22 decision in `docs/specs/<dated>-storage-collab-design.md` under `## Decision`: local and network files plus OneDrive and SharePoint through Microsoft Graph with AutoSave in 1.0, real-time co-authoring after 1.0, no own service (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 7), with the 2026-10-20 decision it replaced. Done when: the record names the 1.0 scope, the later co-authoring milestone and both dates. Cheaper substitute: designing the local model without the later merge model in mind. **Corrected 2026-10-23:** recorded OneDrive and SharePoint as a later milestone.
- [ ] Commit: `arch: record storage and co-authoring decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-storage-collab-design.md --require Decision` exits 0.

## 9. Extensibility and Macro Decision

Microsoft 365 users depend on VBA macros in `.docm`, `.xlsm` and `.pptm`, and on Office Add-ins. This record decides macro preservation (always keep the `vbaProject.bin` part), execution (none, a VBA-compatible interpreter, or a different scripting language), the add-in model, and the security model for running code. Decision, 2026-10-22 (owner, `docs/specs/2026-10-23-campaign-scope-design.md`, decision 8): VBA projects always survive save from the first app milestone; a sandboxed VBA-compatible runtime and editor with Trust Center rules is the final milestone, authored by §26 after all six apps. Office Add-ins from AppSource are a Microsoft service, decided in §14.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-extensibility-design.md`. Done when: the record passes the checker with Decision.

- [ ] Record macro preservation on round-trip as a hard requirement with its test. Done when: the record names the corpus file and check. Cheaper substitute: stripping macros on save.
- [ ] Compare macro execution options with security implications (Trust Center equivalents, signed macros, Mark of the Web). Done when: each option lists its security controls. Cheaper substitute: running macros without a trust prompt.
- [ ] Record the add-in and scripting decision under `## Decision`. Done when: the decision names the runtime and the security model. Cheaper substitute: no extensibility recorded at all.
- [ ] Commit: `arch: record extensibility decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-extensibility-design.md --require Decision --require Security` exits 0.

## 10. Font Strategy Decision

Documents name Calibri, Cambria, Aptos, Arial, Times New Roman and others. Microsoft fonts cannot be bundled, so layout must use installed fonts when present and metric-compatible open fonts otherwise (Carlito for Calibri, Caladea for Cambria, Liberation Sans, Serif and Mono for Arial, Times New Roman and Courier New), with a substitution table and embedded-font support.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-fonts-design.md`. Done when: the record passes the checker with the substitution table.

- [ ] Write the substitution table: requested font, metric-compatible substitute, licence, fallback. Done when: the 30 most common fonts in the §3 corpus each have a row. Cheaper substitute: one fallback font for everything.
- [ ] Record the bundled font set and its licences for `THIRD-PARTY-NOTICES.md`. Done when: every bundled font is OFL, Apache 2.0 or equivalent. Cheaper substitute: bundling a font without checking embedding rights.
- [ ] Record embedded-font handling in OOXML (obfuscated `odttf` read, embedding permission flags honoured on save). Done when: the record states read and write behaviour. Cheaper substitute: ignoring embedded fonts.
- [ ] Commit: `arch: record font strategy`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-fonts-design.md --require Substitution --require Decision` exits 0.

## 11. Product Licence and Dependency Policy

The product's own licence decides which dependencies are allowed: a permissive or copyleft open-source licence, or proprietary. The dependency policy then lists allowed and refused licences and the notice process. Decision, 2026-10-20 (owner): GPL-3.0-or-later with a contributor licence agreement so Rizonesoft can still offer a commercial edition; chosen first to match Qt's open-source edition and kept the same day after the move to WinUI 3, whose MIT licence is compatible, and again on 2026-10-22 after the move to native C++. `LICENSE` and the `README.md` notice landed the same day; enforcement is D00 T02.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-licensing-design.md` with the owner's choice. Done when: the record passes the checker with Decision.

- [ ] Compare licence options (MIT or Apache 2.0, MPL 2.0, GPL or AGPL, proprietary) with their effect on dependencies such as the MSVC runtime (Microsoft's redistribution terms), HarfBuzz (MIT), ICU (Unicode licence), Skia (BSD-3-Clause), MPXJ (LGPL) and LibreOffice components (MPL). **Corrected 2026-10-20:** named Qt 6 (LGPLv3 or commercial) as the main dependency. **Corrected 2026-10-22:** named the Windows App SDK and WinUI 3, the .NET runtime and Win2D. Done when: each option lists allowed dependency licences. Cheaper substitute: choosing a licence without checking dependencies.
- [ ] Record the 2026-10-20 decision (GPL-3.0-or-later, contributor agreement) under `## Decision`. Done when: the decision and date are recorded and `LICENSE` holds the GPLv3 text. Cheaper substitute: a licence named only in README.
- [ ] Write the dependency policy (allowed licences, refused licences, notice file process) in the record. Done when: the policy names `THIRD-PARTY-NOTICES.md` as the notice file. Cheaper substitute: case-by-case review with no written rule.
- [ ] Commit: `arch: record product licence and dependency policy`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-licensing-design.md --require Decision` exits 0 and `Test-Path LICENSE` returns `True`.

## 12. Foundation Plan

The foundation plan joins the decisions into one architecture: component diagram, repository layout, build and test toolchain, CI matrix, and the milestone order (shared platform, then the apps in an order the plan justifies).

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/plans/YYYY-MM-DD-foundation-plan.md`. Done when: the checker passes with Architecture, Repository layout, Toolchain and Milestones headings.

- [ ] Write the Architecture section with a component diagram `docs/plans/foundation-architecture.svg` naming each component's owning design record. Done when: every record from §1 to §11 and §14 to §16 is cited. **Corrected 2026-10-23:** cited §1 to §11 only. Cheaper substitute: a list of libraries.
- [ ] Write the Repository layout section mapping components to directories. Done when: each top-level directory has a purpose line. Cheaper substitute: deciding layout while coding.
- [ ] Write the Toolchain section: the C++ standard flag and its C++26 rule, MSVC, the Windows SDK, CMake with presets, vcpkg in manifest mode, lint and format, the test framework, MSVC runtime linkage (static or app-local) and the CI matrix (x64 and Arm64). Done when: each tool has a version policy. Cheaper substitute: "standard tooling".
- [ ] Write the Milestones section ordering the shared platform, the document engines, the six apps (each ending in a draft preview release), interoperability, VBA and the 1.0 draft release (`docs/specs/2026-10-23-campaign-scope-design.md`, decisions 8 and 13), with the parity bar per milestone as inventory coverage percentages and the domain each milestone maps to (`04-platform` to `14-release`, as §17 to §27 author them). Done when: each milestone names its domain, its coverage target and its draft release. Cheaper substitute: dates without a measurable bar. **Corrected 2026-10-23:** named only the platform and the six apps.
- [ ] Update `AGENTS.md` with where the code lives and which commands verify it, from the Toolchain section. Done when: `AGENTS.md` lists the build, lint and test commands. Cheaper substitute: leaving the adaptation placeholder line.
- [ ] Add the planned application build and test commands from the Toolchain section to the Build and test section of `CONTRIBUTING.md`, each marked planned until the `todo/04-platform/TODO-01-build-foundation.md` section that makes it run is stamped (§17). Done when: every command is listed with its owning platform section. **Corrected 2026-10-23:** required the commands to run on a clean clone, which no build configuration allows before Phase 4. Cheaper substitute: leaving the guide with the tooling commands only. (Deferred from D00 T02 §5 on 2026-10-21.)
- [ ] Commit: `arch: add foundation plan`

**Test checkpoint:** `python scripts/check-design-doc.py docs/plans/<dated>-foundation-plan.md --require Architecture --require "Repository layout" --require Toolchain --require Milestones` exits 0.

## 13. Inventory Ownership Gate

The plan becomes executable work in §17 to §27, which author the platform, engine, application, interoperability, VBA and release domains to a written contract. This section proves the result: every inventoried record (control, menu item, dialog, pane, view, Backstage page, Options setting, status bar item, command and shortcut) whose disposition is `build` or `equivalent` is owned by exactly one section, 1:1 with Word, Excel, PowerPoint, Outlook, Visio and Project (owner request 2026-10-21), and every `excluded` record carries its reason (D02 T01 §28). **Groomed 2026-10-23:** the domain authoring moved to §17 to §27 so each domain has its own contract; this section keeps the proof and the gates.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Prove inventory ownership over all six apps and the shell. Done when: `python scripts/inventory-report.py --owners --check` exits 0.
2. Keep it proven. Done when: the check gates every later TODO or inventory commit and every `process-plan` audit.

- [ ] Confirm §17 to §27 authored `todo/04-platform/` to `todo/14-release/` and each file validates. Done when: `python scripts/todo-graph.py validate` exits 0 and `todo/TODO-00-INDEX.md` lists all eleven domains. Cheaper substitute: one umbrella platform section. **Corrected 2026-10-23:** authored `todo/04-platform/` here.
- [ ] Confirm each app domain's sections list every inventory record id they implement on their `> **Implements:**` lines (D02 T01 §22; a group's section lists each of its controls, menu items and dialog controls, not the group id alone). Done when: `python scripts/inventory-report.py --owners --check --app <app>` exits 0 for each of the six apps. Cheaper substitute: one section per ribbon tab, or claiming only group ids. **Corrected 2026-10-23:** authored the app domains here.
- [ ] Run `python scripts/inventory-report.py --owners --check` (D02 T01 §22) over all six apps and the shell. Done when: it exits 0 with no unowned, unknown or doubly owned id, and no claimed `excluded` record. Cheaper substitute: sampling a few ids by hand.
- [ ] Add `python scripts/inventory-report.py --owners --check` to `scripts/hooks/pre-commit` for commits that stage `todo/` or `design/inventory/`, with a test in `scripts/tests/test_pre_commit_hook.py`. Done when: staging a new inventory record with no citing section refuses the commit. Cheaper substitute: running the check only in this section.
- [ ] Add `python scripts/inventory-report.py --owners --check` to the audit commands of `process-plan` in `.claude/skills/` (the only copy since D00 T03 §13; **Corrected 2026-10-23:** named the `.agents/` and `.codex/` mirrors too). Done when: the skill lists it and an unowned record is a refusal the audit fixes before shipping. Cheaper substitute: a note in `todo/README.md` only.
- [ ] Check every authored section's Needs against the §17 contract: run `python scripts/todo-graph.py build` to regenerate `build/todo-cache.json` from the TODO files, then from it list the sections whose `needs` include `operator`, `owner-decision`, `third-party`, `store-account` or `attended`. Done when: the list holds only Phase 99 sections, the Microsoft Entra and Google OAuth registration sections, and the signing and MSIX sections of `todo/14-release/`, and the result is recorded in this section's review findings. Cheaper substitute: reading `query blocked`, which also lists sections that only wait on prerequisites. **Corrected 2026-10-23:** used `query blocked` alone, which cannot pass while authored sections wait on unbuilt prerequisites.
- [ ] Run `python scripts/todo-graph.py plan --sync` and commit the regenerated plan. Done when: `plan --check` exits 0. Cheaper substitute: editing `todo/implementation-plan.md` by hand.
- [ ] Commit: `todo: prove inventory ownership across the authored domains`

**Test checkpoint:** `python scripts/inventory-report.py --owners --check` exits 0, `python -m unittest discover -s scripts/tests -p "test_pre_commit_hook.py"` passes and `python scripts/todo-graph.py validate` exits 0.

## 14. Cloud Feature Equivalents Decision

Owner decision 2026-10-22 (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 6): every inventoried control backed by a Microsoft cloud service gets a working equivalent of our own, or is excluded with a reason, never a dead control. This record decides each one and writes the disposition into the inventory (D02 T01 §28), so the app domains build exactly what it says.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-cloud-equivalents-design.md` with a row per cloud-backed record. Done when: the checker passes with Decision.
2. Set `disposition` and `dispositionReason` on each record in `design/inventory/`. Done when: `python scripts/inventory-report.py` counts match the record.

- [ ] List every inventory record whose behaviour needs a Microsoft cloud service (Copilot, Designer, Editor, Translator, cloud dictation and transcription, stock images, icons and 3D models, Loop, Teams meetings, Stocks and Geography data types, Researcher, Smart Lookup, Microsoft Search in the title bar, AppSource add-ins, Forms, Sway, Clipchamp, Planner, live captions and cloud fonts) in a table in `docs/specs/<dated>-cloud-equivalents-design.md`. Done when: each row cites its inventory id and the service. Cheaper substitute: deciding by product name without the ids.
- [ ] Decide the Assistant pane that replaces Copilot in `docs/specs/<dated>-cloud-equivalents-design.md`: a provider the user configures (Anthropic, OpenAI or a local model through an OpenAI-compatible endpoint), off by default, keys in Windows Credential Manager, document content sent only on an explicit user action with a preview. Done when: the record names the provider interface, the consent flow and the key storage. Cheaper substitute: a hard-wired provider or a key in a settings file.
- [ ] Decide dictation and read aloud in `docs/specs/<dated>-cloud-equivalents-design.md`: Windows speech recognition and Windows speech synthesis. Done when: the record names both APIs and their language coverage. Cheaper substitute: excluding them.
- [ ] Decide the grammar engine in `docs/specs/<dated>-cloud-equivalents-design.md`: a local engine whose licence passes §11. Done when: the record names the engine, its licence and its languages. Cheaper substitute: spelling only.
- [ ] Decide translation in `docs/specs/<dated>-cloud-equivalents-design.md`: through the Assistant provider, off until the user configures one. Done when: the record names the call and its consent. Cheaper substitute: excluding translation.
- [ ] Decide stock images, icons and 3D models in `docs/specs/<dated>-cloud-equivalents-design.md`: openly licensed libraries, with licence metadata kept on insert. Done when: the record names each source and its licence. Cheaper substitute: hot-linking images whose licence is unknown.
- [ ] Decide Designer's layout suggestions in `docs/specs/<dated>-cloud-equivalents-design.md`: our own rule engine over the slide's placeholders. Done when: the record names the rules' inputs and outputs. Cheaper substitute: excluding Designer.
- [ ] Decide the data types (Stocks, Geography) in `docs/specs/<dated>-cloud-equivalents-design.md`: an equivalent with a named open data source, or excluded with a reason. Done when: the record names the source or the reason. Cheaper substitute: leaving the gallery empty.
- [ ] Record each exclusion (for example Loop, Teams meeting creation, AppSource) in `docs/specs/<dated>-cloud-equivalents-design.md` with a one-sentence reason. Done when: every excluded row has a reason a reviewer can check. Cheaper substitute: an unexplained exclusion.
- [ ] Set `disposition` and `dispositionReason` on every listed record in `design/inventory/<app>/*.json`. Done when: `python scripts/check-inventory.py` exits 0 and `python scripts/inventory-report.py` reports the same `equivalent` and `excluded` counts as the record. Cheaper substitute: a disposition table in the record only, which no check reads.
- [ ] Commit: `arch: record cloud feature equivalents and dispositions`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-cloud-equivalents-design.md --require Decision` exits 0 and `python scripts/check-inventory.py` exits 0.

## 15. Localisation Decision

Owner decision 2026-10-22 (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 10): English (United States) user interface in 1.0, ready for translation; document content in every language. This record decides how strings, formats and mirroring work so the platform builds them once.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-localisation-design.md`. Done when: the checker passes with Decision.

- [ ] Decide the string resource format and lookup (an id per string, plural forms, translator comments) in `docs/specs/<dated>-localisation-design.md`. Done when: the record names the format and the fallback to English. Cheaper substitute: string literals in code.
- [ ] Decide the translation file format contributors edit in `docs/specs/<dated>-localisation-design.md`. Done when: the record names the format and the tool that round-trips it. Cheaper substitute: asking translators to edit resource files.
- [ ] Decide number, date, currency and sort formatting in `docs/specs/<dated>-localisation-design.md`: Windows NLS or ICU, per user locale, with a document's language overriding the user's. Done when: the record names the API for each. Cheaper substitute: formatting with the C++ default locale.
- [ ] Decide right-to-left mirroring of the shell and controls in `docs/specs/<dated>-localisation-design.md`. Done when: the record names what mirrors and what never does (for example media controls). Cheaper substitute: mirroring everything.
- [ ] Decide the pseudo-locale (lengthened, accented and mirrored strings) and the CI job that renders it in `docs/specs/<dated>-localisation-design.md`. Done when: the record names the pseudo-locale and the CI check. Cheaper substitute: testing English only.
- [ ] Commit: `arch: record localisation decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-localisation-design.md --require Decision` exits 0.

## 16. Updates and Diagnostics Decision

Owner decision 2026-10-22 (`docs/specs/2026-10-23-campaign-scope-design.md`, decisions 11, 12 and 14): no Rizonesoft service, no telemetry, no Store, unsigned builds until the owner decides signing. Updates come from GitHub Releases; crash dumps stay on the user's PC and can be attached to a pre-filled GitHub issue.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-updates-diagnostics-design.md`. Done when: the checker passes with Decision.

- [ ] Decide the update check in `docs/specs/<dated>-updates-diagnostics-design.md`: the GitHub Releases API for the newest non-draft release, how often, how the user is told, and how the installer applies it. Done when: the record names the endpoint, the cadence, the consent and the rollback. Cheaper substitute: no update notice.
- [ ] Decide crash capture in `docs/specs/<dated>-updates-diagnostics-design.md`: Windows Error Reporting `LocalDumps` or our own handler, where dumps are kept and for how long. Done when: the record names the mechanism, the folder and the retention. Cheaper substitute: silent crashes.
- [ ] Decide the problem report in `docs/specs/<dated>-updates-diagnostics-design.md`: a pre-filled GitHub issue opened in the browser, the dump attached by the user only. Done when: the record names what leaves the PC (nothing without the user). Cheaper substitute: uploading dumps automatically.
- [ ] Decide the local diagnostic log in `docs/specs/<dated>-updates-diagnostics-design.md`: what is logged, rotation, and the rule that no document content or secret is written. Done when: the record names the location, the size cap and the redaction rule. Cheaper substitute: logging everything.
- [ ] Commit: `arch: record updates and diagnostics decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-updates-diagnostics-design.md --require Decision` exits 0.

## 17. Platform Domain Authoring

The shared platform is the own GUI toolkit (§2), the application shell and every service the six apps share. It is Phase 4 and every app domain depends on it.

Authoring contract, shared by §17 to §27 (owner request 2026-10-22: a campaign started once must finish a production-ready suite unattended; `docs/specs/2026-10-23-campaign-scope-design.md`): author each TODO file with `create-todo` from the foundation plan, `design/SPEC.md` and the inventory, wire it into `todo/TODO-00-INDEX.md` and a domain `INDEX.md`, and run `python scripts/todo-graph.py validate` after each. Every file has single-responsibility sections of 4 to 15 five-part micro-steps (at most 55 sections a file; split by subject past that), a falsifiable `Test checkpoint` that runs unattended (a `ctest --preset` run, a UI Automation script, a corpus diff), and file-level `depends_on` for cross-domain order, except that a file holding any section with an `operator` or `owner-decision` Need is never a file-level prerequisite: its consumers name the sections they need in their `Depends On` cells, so a waiting registration or signing decision holds only the work that truly needs it. Every user-facing section is `Surface: yes` with `Fidelity:`, `Job:`, `Treatment:` and `Chrome:` lines and lists its inventory ids on `> **Implements:**` lines; Outlook, Visio and Project sections follow the `### Modernisation` tables of `design/SPEC.md`. Every engine section names its reverse and failure paths (undo, cancel, a damaged file, a wrong password, a partial write) and its round-trip or corpus test. Needs come from the closed list in `todo/README.md`: `operator` only where the owner's Microsoft Entra or Google OAuth registration is required, `owner-decision` only for signing, `office` where Office on this PC is the reference; nothing else may hold a row. Phases: 4 for `04-platform` and `05-engines`, 5 for the six apps, 6 for interoperability and VBA, 7 for release.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/04-platform/` with `create-todo`, one TODO file per subject below. Done when: `python scripts/todo-graph.py validate` passes and every subject below is owned by a section.
2. Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.

- [ ] Author `todo/04-platform/TODO-01-build-foundation.md`: a first section that creates `CMakePresets.json` (with a preset that configures and builds an empty target on x64 and Arm64), `vcpkg.json` and `vcpkg-configuration.json`, then the CMake presets (x64 and Arm64; Debug, Release and ASan), the vcpkg manifest, MSVC `/std:c++23preview /W4 /WX /permissive-`, clang-tidy and clang-format, the unit test framework, the CI jobs on x64 and Arm64 runners, and the process skeleton of one app. Done when: the file validates, a section owns each named piece, a last section makes the build, lint and test commands in `CONTRIBUTING.md` and `AGENTS.md` run on a clean clone, and the first section's reference is in the `Depends On` cell of D00 T03 §11 (the toolchain pins, which need those files), added by this section before it stamps. Cheaper substitute: one section for the whole build, or leaving D00 T03 §11 ready before its input files exist. **Corrected 2026-10-23:** left adding the D00 T03 §11 edge to the authored section, after §17 stamps.
- [ ] Author `todo/04-platform/TODO-02-windowing-and-rendering.md`: the Win32 window class, per-monitor DPI awareness v2, the Direct3D 11 device and flip-model swap chain, the Direct2D device context, device-loss recovery, DirectComposition for Mica, frame scheduling and invalidation, the custom title bar with Snap Layouts, several windows, and window placement. Done when: a section owns each named piece and cites the §2 prototype measurements as its budget. Cheaper substitute: rendering per app.
- [ ] Author `todo/04-platform/TODO-03-toolkit-core.md`: the element tree, layout (stack, grid, flow, virtualised lists), styling from the design tokens (light, dark, high contrast), DirectWrite text, input routing (mouse, pen, touch, keyboard), focus and keyboard navigation, hit testing and animation. Done when: a section owns each named piece. Cheaper substitute: styling with literal colours.
- [ ] Author `todo/04-platform/TODO-04-controls.md`: one section per control family the SPEC's component chapters name: buttons, split and toggle buttons, check boxes and radio buttons, edit and combo boxes, spinners, sliders, galleries, colour and font pickers, menus and context menus, tooltips and super tooltips, scroll bars, tabs, lists, trees, progress, the dialog framework, the task pane framework, notification bars and key tips. Done when: every control type in the inventory's `controlType` values is owned. Cheaper substitute: using common controls for some families.
- [ ] Author `todo/04-platform/TODO-05-text-input-and-accessibility.md`: the TSF text store, IME composition, the touch keyboard and dictation (§14), the UI Automation provider framework and each control's patterns, Narrator and NVDA verification, high contrast and text scaling. Done when: a section owns each named piece and the accessibility chapter of `design/SPEC.md` is cited. Cheaper substitute: MSAA only.
- [ ] Author `todo/04-platform/TODO-06-ribbon-and-shell.md`: the ribbon engine driven by the inventory (tabs, contextual tabs, groups, scaling, collapsed and Simplified Ribbon, the Quick Access Toolbar, the Customize Ribbon and Customize Quick Access Toolbar dialogs, key tips), the Backstage framework, the status bar and zoom, title bar command search, and the account area. Done when: every shell chrome record in `design/inventory/shell/chrome.json` is owned. Cheaper substitute: a hand-built ribbon per app.
- [ ] Author `todo/04-platform/TODO-07-commands-undo-settings.md`: the command model, the undo and redo stack with grouping, the settings store (per user, atomic temporary-file-then-replace), the Options dialog framework, recent files and pinning, templates and recent places. Done when: a section owns each named piece and each Options page the inventory lists has a consumer. Cheaper substitute: settings written in place.
- [ ] Author `todo/04-platform/TODO-08-files-recovery-printing.md`: the file dialogs, atomic save, AutoSave and AutoRecover, the Document Recovery pane, file locking and read-only opening, network paths, the clipboard formats, drag and drop, printing and print preview. Done when: a section owns each named piece and every failure path (full disk, lost network, locked file) has a test. Cheaper substitute: overwrite-in-place saving.
- [ ] Author `todo/04-platform/TODO-09-language-services.md`: spelling through the Windows Spell Checking API, grammar, thesaurus and read aloud per §14, language detection, proofing language settings, hyphenation and AutoCorrect. Done when: a section owns each named piece. Cheaper substitute: spelling only.
- [ ] Author `todo/04-platform/TODO-10-localisation.md`: string resources, the pseudo-locale, right-to-left mirroring and locale formatting per §15. Done when: a section owns each named piece and CI renders the pseudo-locale. Cheaper substitute: translating later by search and replace.
- [ ] Author `todo/04-platform/TODO-11-help-and-assistant.md`: the Help pane and F1 help framework with our own help content per command, the Tell Me equivalent, and the Assistant pane with its provider settings per §14. Done when: a section owns each named piece and every Help tab record is owned. Cheaper substitute: links to Microsoft's help.
- [ ] Author `todo/04-platform/TODO-13-microsoft-graph-files.md`: OneDrive and SharePoint open, save and AutoSave through Microsoft Graph, its sign-in, and its offline and conflict paths, the first section carrying the `operator` Need for the owner's Microsoft Entra registration (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 7). Done when: the file validates, no other platform file depends on it at file level, and every Graph failure path (expired token, lost network, conflicting save) has a test. Cheaper substitute: putting Graph in the file-saving file, which holds local saving on the registration.
- [ ] Author `todo/04-platform/TODO-12-install-update-diagnostics.md`: the unsigned Inno Setup installer, file associations and icons, the update check, crash dumps, the problem report and the diagnostic log per §16, versioning per §28 (the tag-driven version in CMake, `VERSIONINFO` in every binary, the About page, schema versions and migrations for the settings store and recovery files), and the script that builds an app's draft preview release with its notes, bump, SBOM, build attestation and checksums per §28. Done when: a section owns each named piece and the draft release script is the one every app domain's last section calls. Cheaper substitute: packaging only at the end.
- [ ] Commit: `todo: author the platform domain`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, `Test-Path todo/04-platform/INDEX.md, todo/04-platform/TODO-01-build-foundation.md, todo/04-platform/TODO-02-windowing-and-rendering.md, todo/04-platform/TODO-03-toolkit-core.md, todo/04-platform/TODO-04-controls.md, todo/04-platform/TODO-05-text-input-and-accessibility.md, todo/04-platform/TODO-06-ribbon-and-shell.md, todo/04-platform/TODO-07-commands-undo-settings.md, todo/04-platform/TODO-08-files-recovery-printing.md, todo/04-platform/TODO-09-language-services.md, todo/04-platform/TODO-10-localisation.md, todo/04-platform/TODO-11-help-and-assistant.md, todo/04-platform/TODO-12-install-update-diagnostics.md, todo/04-platform/TODO-13-microsoft-graph-files.md` returns `True` for every path, `todo/TODO-00-INDEX.md` lists `04-platform`. **Corrected 2026-10-23:** ran `validate` and `query stats` only, which pass before the domain exists.

## 18. Document Engines Domain Authoring

The document engines are shared by more than one app and decided in §3 to §6 and §10. They are Phase 4, beside the platform.

Follow the authoring contract in §17.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/05-engines/` with `create-todo`, one TODO file per subject below. Done when: `python scripts/todo-graph.py validate` passes and every subject below is owned by a section.
2. Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.

- [ ] Author `todo/05-engines/TODO-01-opc-and-ooxml-core.md`: the OPC package reader and writer, relationships and content types, unknown-part and unknown-element preservation, ECMA-376 agile and standard encryption with password refusal paths, digital signatures, and the compound file reader for the legacy formats. Done when: a section owns each named piece with a round-trip corpus test. Cheaper substitute: dropping unknown parts on save.
- [ ] Author `todo/05-engines/TODO-02-drawingml.md`: DrawingML shapes, geometry presets, fills, lines, effects (shadow, glow, soft edges, reflection, 3-D), text in shapes, pictures with crop and recolour, and theme resolution, on the §4 renderer. Done when: a section owns each named piece and the §4 effects slide renders. Cheaper substitute: rectangles only.
- [ ] Author `todo/05-engines/TODO-03-charts.md`: the chart model and renderer for every Office chart type, chart elements and formatting, and the chart data link shared by Grid, Stage and Write. Done when: every chart type the inventory's chart gallery lists is owned. Cheaper substitute: a subset of chart types.
- [ ] Author `todo/05-engines/TODO-04-smartart-and-equations.md`: SmartArt layouts and editing, and OMML equations with an equation editor and layout. Done when: each SmartArt layout family and the equation tools are owned. Cheaper substitute: pictures of SmartArt.
- [ ] Author `todo/05-engines/TODO-05-text-layout.md`: the text layout and pagination engine decided in §3 (shaping, bidirectional text, line breaking, justification, hyphenation, tables, floats and wrapping, widow and orphan control). Done when: the §3 corpus page-count agreement is the checkpoint. Cheaper substitute: line breaking without pagination.
- [ ] Author `todo/05-engines/TODO-06-fonts-and-pdf.md`: the font service and substitution table from §10, embedded fonts, and the PDF writer from §4 (tagged PDF, PDF/A, bookmarks, hyperlinks). Done when: a section owns each named piece. Cheaper substitute: printing to the operating system's PDF printer.
- [ ] Author `todo/05-engines/TODO-07-formula-engine.md`: the formula parser, dependency graph and recalculation engine decided in §6, shared by Grid, Flow's shape formulas and Plan's custom fields. Done when: the §6 conformance workbook is the checkpoint. Cheaper substitute: one engine per app.
- [ ] Commit: `todo: author the document engines domain`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, `Test-Path todo/05-engines/INDEX.md, todo/05-engines/TODO-01-opc-and-ooxml-core.md, todo/05-engines/TODO-02-drawingml.md, todo/05-engines/TODO-03-charts.md, todo/05-engines/TODO-04-smartart-and-equations.md, todo/05-engines/TODO-05-text-layout.md, todo/05-engines/TODO-06-fonts-and-pdf.md, todo/05-engines/TODO-07-formula-engine.md` returns `True` for every path, `todo/TODO-00-INDEX.md` lists `05-engines`. **Corrected 2026-10-23:** ran `validate` and `query stats` only, which pass before the domain exists.

## 19. Write Domain Authoring

Write is the Word counterpart; its domain is Phase 5, depends on `04-platform` and `05-engines`, and ends with its draft preview release (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 13). Every `word.*` inventory record with disposition `build` or `equivalent` is owned by exactly one of its sections.

Follow the authoring contract in §17.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/06-write/` with `create-todo`, one TODO file per subject below. Done when: `python scripts/todo-graph.py validate` passes and every subject below is owned by a section.
2. Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.

- [ ] Author `todo/06-write/TODO-01-document-model-and-formats.md`: the document model, `.docx`, `.dotx` and `.docm` read and write with round-trip and VBA preservation, `.doc`, `.rtf`, `.odt`, text and HTML, and PDF export. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `word.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/06-write/TODO-02-editing-and-formatting.md`: caret and selection, character and paragraph formatting, styles, themes and style sets, lists and numbering, tables, sections, columns, headers and footers, page numbering. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `word.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/06-write/TODO-03-fields-and-references.md`: fields, footnotes and endnotes, tables of contents, captions, citations and bibliography, index, table of authorities, bookmarks and cross-references. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `word.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/06-write/TODO-04-review-and-mailings.md`: comments, track changes, compare and combine, protection, restrict editing, encryption, the document inspector, the accessibility checker, word count, mail merge, envelopes and labels. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `word.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/06-write/TODO-05-insert-and-design.md`: pictures, shapes, icons, SmartArt, charts, equations, symbols, text boxes, WordArt, drop caps, cover pages, Quick Parts and building blocks, hyperlinks, watermark, page colour and borders. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `word.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/06-write/TODO-06-views-and-navigation.md`: Print Layout, Read Mode, Web Layout, Outline, Draft, Focus and Immersive Reader, the Navigation pane, zoom, split, side by side, and find and replace with wildcards. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `word.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/06-write/TODO-07-ribbon-backstage-dialogs.md`: one section per ribbon tab group, Backstage page, dialog, pane and status bar item, each citing every `word.*` id it implements. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `word.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/06-write/TODO-08-templates-help-release.md`: Write's bundled templates, its help content, and the draft preview release through the platform's release script. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `word.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Run `python scripts/inventory-report.py --owners --check --app word`. Done when: it exits 0. Cheaper substitute: checking a sample of ids.
- [ ] Commit: `todo: author the Write domain`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, `Test-Path todo/06-write/INDEX.md, todo/06-write/TODO-01-document-model-and-formats.md, todo/06-write/TODO-02-editing-and-formatting.md, todo/06-write/TODO-03-fields-and-references.md, todo/06-write/TODO-04-review-and-mailings.md, todo/06-write/TODO-05-insert-and-design.md, todo/06-write/TODO-06-views-and-navigation.md, todo/06-write/TODO-07-ribbon-backstage-dialogs.md, todo/06-write/TODO-08-templates-help-release.md` returns `True` for every path, `todo/TODO-00-INDEX.md` lists `06-write`, and `python scripts/inventory-report.py --owners --check --app word` exits 0. **Corrected 2026-10-23:** ran `validate` and `query stats` only, which pass before the domain exists.

## 20. Grid Domain Authoring

Grid is the Excel counterpart; its domain is Phase 5, depends on `04-platform` and `05-engines`, and ends with its draft preview release (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 13). Every `excel.*` inventory record with disposition `build` or `equivalent` is owned by exactly one of its sections.

Follow the authoring contract in §17.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/07-grid/` with `create-todo`, one TODO file per subject below. Done when: `python scripts/todo-graph.py validate` passes and every subject below is owned by a section.
2. Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.

- [ ] Author `todo/07-grid/TODO-01-workbook-model-and-formats.md`: the workbook model, `.xlsx`, `.xlsm`, `.xltx` and `.xlsb` read and write with round-trip and VBA preservation, `.xls`, `.csv`, `.ods`, and PDF export. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `excel.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/07-grid/TODO-02-functions.md`: every worksheet function on the §6 list, one section per function category, each against the conformance workbook. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `excel.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/07-grid/TODO-03-grid-and-editing.md`: the virtualised grid, selection, the formula bar, fill handle and Flash Fill, number formats, cell styles, conditional formatting, data validation, comments and notes. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `excel.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/07-grid/TODO-04-data-and-analysis.md`: sort and filter, advanced filter, tables, PivotTables and PivotCharts, slicers and timelines, outline, subtotals, what-if analysis, Solver, sparklines, the Get Data query engine for files and databases, and external connections. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `excel.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/07-grid/TODO-05-review-view-print.md`: protection, formula auditing, freeze panes, split, custom views, page layout, print titles, page break preview and printing. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `excel.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/07-grid/TODO-06-ribbon-backstage-dialogs.md`: one section per ribbon tab group, Backstage page, dialog, pane and status bar item, each citing every `excel.*` id it implements. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `excel.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/07-grid/TODO-07-templates-help-release.md`: Grid's bundled templates, its help content, and the draft preview release. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `excel.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Run `python scripts/inventory-report.py --owners --check --app excel`. Done when: it exits 0. Cheaper substitute: checking a sample of ids.
- [ ] Commit: `todo: author the Grid domain`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, `Test-Path todo/07-grid/INDEX.md, todo/07-grid/TODO-01-workbook-model-and-formats.md, todo/07-grid/TODO-02-functions.md, todo/07-grid/TODO-03-grid-and-editing.md, todo/07-grid/TODO-04-data-and-analysis.md, todo/07-grid/TODO-05-review-view-print.md, todo/07-grid/TODO-06-ribbon-backstage-dialogs.md, todo/07-grid/TODO-07-templates-help-release.md` returns `True` for every path, `todo/TODO-00-INDEX.md` lists `07-grid`, and `python scripts/inventory-report.py --owners --check --app excel` exits 0. **Corrected 2026-10-23:** ran `validate` and `query stats` only, which pass before the domain exists.

## 21. Stage Domain Authoring

Stage is the PowerPoint counterpart; its domain is Phase 5, depends on `04-platform` and `05-engines`, and ends with its draft preview release (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 13). Every `powerpoint.*` inventory record with disposition `build` or `equivalent` is owned by exactly one of its sections.

Follow the authoring contract in §17.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/08-stage/` with `create-todo`, one TODO file per subject below. Done when: `python scripts/todo-graph.py validate` passes and every subject below is owned by a section.
2. Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.

- [ ] Author `todo/08-stage/TODO-01-presentation-model-and-formats.md`: the presentation model, `.pptx`, `.potx` and `.pptm` read and write with round-trip and VBA preservation, `.ppt`, `.odp`, and PDF, image and video export. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `powerpoint.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/08-stage/TODO-02-slide-editing.md`: the slide canvas, placeholders, layouts, masters, themes and variants, sections, zoom links, comments and the outline. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `powerpoint.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/08-stage/TODO-03-animation-and-transitions.md`: the animation engine (entrance, emphasis, exit, motion paths, triggers, timing), transitions including Morph. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `powerpoint.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/08-stage/TODO-04-slide-show.md`: the slide show, presenter view on several monitors, rehearsed timings, recording, media playback through Media Foundation, and subtitles per §14. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `powerpoint.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/08-stage/TODO-05-views-and-print.md`: Normal, Outline, Slide Sorter, Notes Page and Reading views, handouts and printing. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `powerpoint.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/08-stage/TODO-06-ribbon-backstage-dialogs.md`: one section per ribbon tab group, Backstage page, dialog, pane and status bar item, each citing every `powerpoint.*` id it implements. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `powerpoint.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/08-stage/TODO-07-templates-help-release.md`: Stage's bundled themes and templates, its help content, and the draft preview release. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `powerpoint.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Run `python scripts/inventory-report.py --owners --check --app powerpoint`. Done when: it exits 0. Cheaper substitute: checking a sample of ids.
- [ ] Commit: `todo: author the Stage domain`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, `Test-Path todo/08-stage/INDEX.md, todo/08-stage/TODO-01-presentation-model-and-formats.md, todo/08-stage/TODO-02-slide-editing.md, todo/08-stage/TODO-03-animation-and-transitions.md, todo/08-stage/TODO-04-slide-show.md, todo/08-stage/TODO-05-views-and-print.md, todo/08-stage/TODO-06-ribbon-backstage-dialogs.md, todo/08-stage/TODO-07-templates-help-release.md` returns `True` for every path, `todo/TODO-00-INDEX.md` lists `08-stage`, and `python scripts/inventory-report.py --owners --check --app powerpoint` exits 0. **Corrected 2026-10-23:** ran `validate` and `query stats` only, which pass before the domain exists.

## 22. Mail Domain Authoring

Mail is the Outlook (classic) counterpart; its domain is Phase 5, depends on `04-platform` and `05-engines`, and ends with its draft preview release (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 13). Every `outlook.*` inventory record with disposition `build` or `equivalent` is owned by exactly one of its sections.

Follow the authoring contract in §17.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/09-mail/` with `create-todo`, one TODO file per subject below. Done when: `python scripts/todo-graph.py validate` passes and every subject below is owned by a section.
2. Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.

- [ ] Author `todo/09-mail/TODO-01-accounts-and-sync.md`: account setup for Microsoft 365 and Outlook.com through Microsoft Graph and Gmail through Google OAuth (both with the `operator` Need for the owner's registrations), iCloud and IMAP and SMTP with app passwords, CalDAV and CardDAV, the local store, sync, offline mode and the search index from §7. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `outlook.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/09-mail/TODO-02-mail.md`: the folder pane, message list, conversations, reading pane, compose on the Write editor, signatures, rules, Quick Steps, categories, flags, junk filtering, attachments, `.msg` and `.eml`, PST import and export, and S/MIME. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `outlook.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/09-mail/TODO-03-calendar.md`: calendar views, recurrence (RFC 5545), meetings and invitations (iTIP and iMIP), time zones, the Scheduling Assistant from free and busy data, reminders and notifications. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `outlook.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/09-mail/TODO-04-people-tasks-notes.md`: contacts and contact groups (vCard), Tasks and To Do, Notes, and printing. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `outlook.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/09-mail/TODO-05-ribbons-backstage-dialogs.md`: one section per module and item-window ribbon group, Backstage page, dialog, pane and status bar item, each citing every `outlook.*` id it implements and following the modernised Outlook chapter. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `outlook.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/09-mail/TODO-06-help-release.md`: Mail's help content and the draft preview release. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `outlook.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Run `python scripts/inventory-report.py --owners --check --app outlook`. Done when: it exits 0. Cheaper substitute: checking a sample of ids.
- [ ] Commit: `todo: author the Mail domain`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, `Test-Path todo/09-mail/INDEX.md, todo/09-mail/TODO-01-accounts-and-sync.md, todo/09-mail/TODO-02-mail.md, todo/09-mail/TODO-03-calendar.md, todo/09-mail/TODO-04-people-tasks-notes.md, todo/09-mail/TODO-05-ribbons-backstage-dialogs.md, todo/09-mail/TODO-06-help-release.md` returns `True` for every path, `todo/TODO-00-INDEX.md` lists `09-mail`, and `python scripts/inventory-report.py --owners --check --app outlook` exits 0. **Corrected 2026-10-23:** ran `validate` and `query stats` only, which pass before the domain exists.

## 23. Flow Domain Authoring

Flow is the Visio counterpart; its domain is Phase 5, depends on `04-platform` and `05-engines`, and ends with its draft preview release (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 13). Every `visio.*` inventory record with disposition `build` or `equivalent` is owned by exactly one of its sections.

Follow the authoring contract in §17.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/10-flow/` with `create-todo`, one TODO file per subject below. Done when: `python scripts/todo-graph.py validate` passes and every subject below is owned by a section.
2. Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.

- [ ] Author `todo/10-flow/TODO-01-drawing-model-and-formats.md`: the drawing model, `.vsdx`, `.vsdm` and `.vstx` read and write with round-trip and VBA preservation, `.vsd` reading, and PDF, SVG and PNG export. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `visio.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/10-flow/TODO-02-shapes-and-stencils.md`: shape formulas on the shared formula engine, masters and stencils with our own artwork for every stencil family the inventory lists, themes, layers, pages and backgrounds. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `visio.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/10-flow/TODO-03-connectors-and-layout.md`: connectors, glue and routing, line jumps, containers and callouts, auto align and space, and page re-layout. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `visio.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/10-flow/TODO-04-data-and-validation.md`: shape data, data graphics, linking to workbooks and CSV, and diagram validation rules. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `visio.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/10-flow/TODO-05-ribbon-backstage-dialogs.md`: one section per ribbon tab group, Backstage page, dialog, pane and status bar item, each citing every `visio.*` id it implements and following the modernised Visio chapter. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `visio.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/10-flow/TODO-06-templates-help-release.md`: Flow's bundled templates, its help content, and the draft preview release. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `visio.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Run `python scripts/inventory-report.py --owners --check --app visio`. Done when: it exits 0. Cheaper substitute: checking a sample of ids.
- [ ] Commit: `todo: author the Flow domain`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, `Test-Path todo/10-flow/INDEX.md, todo/10-flow/TODO-01-drawing-model-and-formats.md, todo/10-flow/TODO-02-shapes-and-stencils.md, todo/10-flow/TODO-03-connectors-and-layout.md, todo/10-flow/TODO-04-data-and-validation.md, todo/10-flow/TODO-05-ribbon-backstage-dialogs.md, todo/10-flow/TODO-06-templates-help-release.md` returns `True` for every path, `todo/TODO-00-INDEX.md` lists `10-flow`, and `python scripts/inventory-report.py --owners --check --app visio` exits 0. **Corrected 2026-10-23:** ran `validate` and `query stats` only, which pass before the domain exists.

## 24. Plan Domain Authoring

Plan is the Project counterpart; its domain is Phase 5, depends on `04-platform` and `05-engines`, and ends with its draft preview release (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 13). Every `project.*` inventory record with disposition `build` or `equivalent` is owned by exactly one of its sections.

Follow the authoring contract in §17.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/11-plan/` with `create-todo`, one TODO file per subject below. Done when: `python scripts/todo-graph.py validate` passes and every subject below is owned by a section.
2. Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.

- [ ] Author `todo/11-plan/TODO-01-project-model-and-formats.md`: the project model, Plan's native format (§5), Project XML read and write, `.mpp` reading per §5, workbook and CSV import and export. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `project.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/11-plan/TODO-02-scheduling-engine.md`: critical path scheduling, task types, constraints, dependencies with lag, calendars, effort-driven scheduling, manual and automatic tasks, and resource levelling. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `project.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/11-plan/TODO-03-resources-cost-tracking.md`: resources and assignments, costs, baselines, tracking, earned value, custom fields with formulas, and master projects. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `project.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/11-plan/TODO-04-views-and-reports.md`: the Gantt Chart, Tracking Gantt, Network Diagram, Calendar, Task Usage, Resource Sheet, Resource Usage, Resource Graph, Team Planner and Timeline views, tables, filters, groups, reports and printing. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `project.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/11-plan/TODO-05-ribbon-backstage-dialogs.md`: one section per ribbon tab group, Backstage page, dialog, pane and status bar item, each citing every `project.*` id it implements and following the modernised Project chapter. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `project.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Author `todo/11-plan/TODO-06-templates-help-release.md`: Plan's bundled templates, its help content, and the draft preview release. Done when: the file validates, a section owns each named piece, and each user-facing section lists its `project.*` ids. Cheaper substitute: one section for the whole subject.
- [ ] Run `python scripts/inventory-report.py --owners --check --app project`. Done when: it exits 0. Cheaper substitute: checking a sample of ids.
- [ ] Commit: `todo: author the Plan domain`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, `Test-Path todo/11-plan/INDEX.md, todo/11-plan/TODO-01-project-model-and-formats.md, todo/11-plan/TODO-02-scheduling-engine.md, todo/11-plan/TODO-03-resources-cost-tracking.md, todo/11-plan/TODO-04-views-and-reports.md, todo/11-plan/TODO-05-ribbon-backstage-dialogs.md, todo/11-plan/TODO-06-templates-help-release.md` returns `True` for every path, `todo/TODO-00-INDEX.md` lists `11-plan`, and `python scripts/inventory-report.py --owners --check --app project` exits 0. **Corrected 2026-10-23:** ran `validate` and `query stats` only, which pass before the domain exists.

## 25. Interoperability Domain Authoring

Interoperability proves the apps against Microsoft's: files written here open in Office as they were, and Office's files open here as they were. It is Phase 6 and needs Office on this PC as the reference (`office` Need).

Follow the authoring contract in §17.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/12-interop/` with `create-todo`, one TODO file per subject below. Done when: `python scripts/todo-graph.py validate` passes and every subject below is owned by a section.
2. Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.

- [ ] Author `todo/12-interop/TODO-01-corpora-and-diffing.md`: the round-trip corpora per format from §3, §5 and §6, and a fidelity diff that renders each file in Office and in our app to PDF and compares pages. Done when: a section owns each format and the diff reports per-page differences. Cheaper substitute: files created by our own writer.
- [ ] Author `todo/12-interop/TODO-02-agreement-gates.md`: page-count agreement for documents, recalculation agreement for workbooks, and opening our output in Office without repair prompts. Done when: each gate has a threshold and runs in CI or on this PC. Cheaper substitute: visual impressions.
- [ ] Author `todo/12-interop/TODO-03-hardening.md`: fuzzing of every file parser with ASan, a security review of the parsers and the Assistant's network calls, performance budgets per app, and a full accessibility audit. Done when: a section owns each named piece. Cheaper substitute: fuzzing one format.
- [ ] Commit: `todo: author the interoperability domain`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, `Test-Path todo/12-interop/INDEX.md, todo/12-interop/TODO-01-corpora-and-diffing.md, todo/12-interop/TODO-02-agreement-gates.md, todo/12-interop/TODO-03-hardening.md` returns `True` for every path, `todo/TODO-00-INDEX.md` lists `12-interop`. **Corrected 2026-10-23:** ran `validate` and `query stats` only, which pass before the domain exists.

## 26. VBA Domain Authoring

Owner decision 2026-10-22 (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 8): the VBA runtime is the final milestone, after all six apps. It is Phase 6.

Follow the authoring contract in §17.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/13-vba/` with `create-todo`, one TODO file per subject below. Done when: `python scripts/todo-graph.py validate` passes and every subject below is owned by a section.
2. Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.

- [ ] Author `todo/13-vba/TODO-01-language-runtime.md`: the VBA project format (MS-OVBA), the language parser and runtime, the standard library, events, and the sandbox. Done when: a section owns each named piece with a conformance suite. Cheaper substitute: running macros unsandboxed.
- [ ] Author `todo/13-vba/TODO-02-editor-and-forms.md`: the Visual Basic Editor (modules, debugger, Immediate and Watch windows) and UserForms (MS-OFORMS). Done when: a section owns each named piece. Cheaper substitute: a plain text editor.
- [ ] Author `todo/13-vba/TODO-03-object-models.md`: a first section that adds `design/inventory/object-model.schema.json` (one record per class and member: an id `vba.<app>.<Class>.<Member>`, kind, signature, no documentation text under the D02 T01 §21 Microsoft-free rule), teaches `scripts/check-inventory.py` to validate `object-model.json` files against it instead of the UI schema, and extends `python scripts/inventory-report.py --owners --check` to require every member id to be cited on exactly one `> **Implements:**` line; a second section (`office` Need) that captures each app's object model from the type libraries Office installs on this PC into `design/inventory/<app>/object-model.json` and commits it in the same commit as the authored sections that claim every member, so the standing ownership gate (§13) never sees an unowned member; then one section per app and object-model area so every captured member is implemented. Done when: every member in each `object-model.json` is cited by exactly one section and the corpus macros run. Cheaper substitute: the members the corpus macros happen to use, which leaves the rest of the object model unowned. **Corrected 2026-10-23:** covered only the members the corpora use.
- [ ] Author `todo/13-vba/TODO-04-trust-center.md`: macro security levels, signed macros, Mark of the Web, trusted locations and the trust prompts. Done when: a section owns each named piece with a refusal test for each. Cheaper substitute: running macros without a prompt.
- [ ] Commit: `todo: author the VBA domain`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, `Test-Path todo/13-vba/INDEX.md, todo/13-vba/TODO-01-language-runtime.md, todo/13-vba/TODO-02-editor-and-forms.md, todo/13-vba/TODO-03-object-models.md, todo/13-vba/TODO-04-trust-center.md` returns `True` for every path, `todo/TODO-00-INDEX.md` lists `13-vba`. **Corrected 2026-10-23:** ran `validate` and `query stats` only, which pass before the domain exists.

## 27. Release Domain Authoring

Release takes the suite from per-app drafts to the 1.0 draft (`docs/specs/2026-10-23-campaign-scope-design.md`, decisions 4, 11, 13 and 14): drafts only, never published by the campaign. It is Phase 7.

Follow the authoring contract in §17.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/14-release/` with `create-todo`, one TODO file per subject below. Done when: `python scripts/todo-graph.py validate` passes and every subject below is owned by a section.
2. Run `python scripts/todo-graph.py plan --sync`. Done when: `python scripts/todo-graph.py plan --check` exits 0.

- [ ] Author `todo/14-release/TODO-01-versioning-and-notes.md`: the release-notes and bump script from §28 (receipts since the last tag, grouped by app), the preview and stable channels, and the `1.0.0` tag rule. Done when: a section owns each named piece. Cheaper substitute: hand-written notes.
- [ ] Author `todo/14-release/TODO-02-suite-installer.md`: the suite installer (all six apps, shared runtime, file associations, uninstall and upgrade), first-run experience and the bundled notices from `THIRD-PARTY-NOTICES.md`. Done when: a section owns each named piece with an install, upgrade and uninstall test. Cheaper substitute: per-app installers only.
- [ ] Author `todo/14-release/TODO-03-signing-and-msix.md`: code signing and the MSIX package, both with the `owner-decision` Need until the owner chooses how to sign (decision 11). Done when: the sections exist and wait on the Need. Cheaper substitute: shipping an MSIX nobody can install.
- [ ] Author `todo/14-release/TODO-04-one-point-zero.md`: the 1.0 release gate (every section of Phases 0 to 7 stamped except the Phase 99 manual items, the `owner-decision` sections of `todo/14-release/TODO-03-signing-and-msix.md` and the gate file's own sections; inventory coverage 100 percent; interoperability gates green) and the unsigned 1.0 draft GitHub release. Done when: the gate lists each condition as a runnable check. Cheaper substitute: a release because the calendar says so.
- [ ] Commit: `todo: author the release domain`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, `Test-Path todo/14-release/INDEX.md, todo/14-release/TODO-01-versioning-and-notes.md, todo/14-release/TODO-02-suite-installer.md, todo/14-release/TODO-03-signing-and-msix.md, todo/14-release/TODO-04-one-point-zero.md` returns `True` for every path, `todo/TODO-00-INDEX.md` lists `14-release`. **Corrected 2026-10-23:** ran `validate` and `query stats` only, which pass before the domain exists.

## 28. Versioning and Release Identity Decision

Owner decisions 2026-10-23 (`docs/specs/2026-10-23-campaign-scope-design.md`, decisions 16 to 18): one SemVer 2.0 version for the whole suite, release notes and bumps generated from the stamped TODO sections, and an SBOM, a build attestation and checksums on every draft release. This record turns them into rules the platform's release script (§17) and the release domain (§27) implement, and adds the versioning of what the suite persists, so a newer file or settings store never meets an older reader unannounced.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-versioning-design.md`. Done when: the checker passes with Decision.

- [ ] Decide the source of truth for the version in `docs/specs/<dated>-versioning-design.md`: the release tag `vMAJOR.MINOR.PATCH[-PRERELEASE]` on the commit a release is built from, read by CMake at configure time, with a fallback for a source archive that has no git history. Done when: the record names the tag format, how CMake reads it and the fallback. Cheaper substitute: a version typed into a file by hand.
- [ ] Decide the Windows four-part mapping in `docs/specs/<dated>-versioning-design.md`: `FileVersion` `MAJOR.MINOR.PATCH.BUILD` with `BUILD` from the CI run number (each part at most 65535), and the full SemVer with the commit SHA as build metadata in `ProductVersion`. Done when: the record shows the mapping for a stable and a pre-release version and the overflow rule. Cheaper substitute: dropping the pre-release tag from the binaries.
- [ ] Decide where the version appears in `docs/specs/<dated>-versioning-design.md`: each binary's `VERSIONINFO` resource, the About page in Backstage, crash reports and problem reports, the update check's request, and the installer, with build timestamps taken from the commit time so a rebuild of the same commit is identical. Done when: the record names each place and the timestamp rule. Cheaper substitute: the version in the installer name only.
- [ ] Decide the bump and notes rules in `docs/specs/<dated>-versioning-design.md`: a script reads the receipts stamped since the last tag, groups them by app domain, and proposes minor for a new feature, patch for fixes only, major for a breaking change to a persisted format or the VBA object model (declared by the section, never inferred), and the pre-release counter for previews; below 1.0 a breaking change bumps minor. Done when: the record names the inputs, each rule and how a section declares a breaking change. Cheaper substitute: choosing each version by hand.
- [ ] Decide the release channels in `docs/specs/<dated>-versioning-design.md`: preview (pre-release tags, GitHub pre-release drafts) and stable, which channel the update check follows by default, how the user switches, and that the check never offers a lower version. Done when: the record names both channels, the default and the downgrade rule. Cheaper substitute: one channel that mixes previews into stable.
- [ ] Decide the schema versioning of every persisted format in `docs/specs/<dated>-versioning-design.md` (the settings store, recovery files, Plan's native format, the local mail store, the search index): each carries its schema version, an older one is migrated forward with a backup and a temporary-file-then-replace write, and a newer one is refused with a message naming the version that wrote it. Done when: the record lists each format with its version field, migration path and refusal. Cheaper substitute: reading whatever is on disk and hoping.
- [ ] Decide the provenance attached to each draft release in `docs/specs/<dated>-versioning-design.md`: an SPDX SBOM merged from the vcpkg port SBOMs and our own components, a GitHub build provenance attestation per artifact, and a SHA-256 checksums file, with how a user verifies each. Done when: the record names each artifact, the tool that makes it and the verification command. Cheaper substitute: checksums alone.
- [ ] Commit: `arch: record versioning and release identity decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-versioning-design.md --require Decision` exits 0.

## Verification

- Every design record in `docs/specs/` named by §1 to §11 passes `scripts/check-design-doc.py` and carries a dated Decision.
- `docs/plans/<dated>-foundation-plan.md` passes the checker and `AGENTS.md` lists the real verify commands.
- `python scripts/inventory-report.py --owners` prints no unowned ids.
- `todo/04-platform/` to `todo/14-release/` exist and validate, authored to the §17 contract.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
