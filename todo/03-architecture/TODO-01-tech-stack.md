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
- -> XREF: D02 T02 §4 -- the GUI toolkit must render the ribbon component chapter, including its scaling rules
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
| 3 | §3 | Text layout and pagination engine decision | §2 | [ ] |
| 4 | §4 | Graphics and canvas rendering decision | §2 | [ ] |
| 5 | §5 | File format strategy decision | §1 | [ ] |
| 6 | §6 | Spreadsheet calculation engine decision | §5 | [ ] |
| 7 | §7 | Mail, calendar and contacts protocol decision | §1 | [ ] |
| 8 | §8 | Storage, autosave and co-authoring decision | §2, §5 | [ ] |
| 9 | §9 | Extensibility and macro decision | §2, §6 | [ ] |
| 10 | §10 | Font strategy decision | §3 | [ ] |
| 11 | §11 | Product licence and dependency policy | -- | [ ] |
| 12 | §12 | Foundation plan | §4, §7, §8, §9, §10, §11 | [ ] |
| 13 | §13 | Platform and app TODO domains | §12, D02 T01 §18, D02 T01 §22, D02 T02 §14 | [ ] |

## 1. Platform Targets Decision

Everything downstream depends on where the suite runs. Microsoft 365 ships native Windows and macOS apps, web apps and mobile apps; matching the Windows desktop first is the default implied by the inventory's reference build. Decision, 2026-10-20 (owner, revised the same day): Windows desktop only, x64 and Arm64, following the move to WinUI 3 in §2 and kept on 2026-10-22 with the move to native C++; macOS, Linux, web and mobile are out of scope. **Corrected 2026-10-20:** the first decision that day was Windows, macOS and Linux on C++ with Qt 6. Distribution, decided the same day: a signed MSIX package and an Inno Setup installer (Inno Setup 7.1.0, the latest release, is installed on the operator's host) for the unpackaged build.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-platform-targets-design.md` with the options and the owner's decision. Done when: the design-doc checker passes with `Decision`.

- [ ] List the candidate targets (Windows x64 and Arm64, macOS, Linux, web browser, iOS, Android) with the cost each adds in the design record. Done when: each target names one stack constraint it imposes. Cheaper substitute: "cross-platform" with no list.
- [ ] Record the owner's 2026-10-20 decision (Windows desktop only, x64 and Arm64) under `## Decision`, with the earlier same-day decision it replaced. Done when: the decision names the targets, the date and what it replaced. Cheaper substitute: leaving macOS and Linux as an unstated maybe. **Corrected 2026-10-20:** said Windows, macOS and Linux with a release order.
- [ ] Record the distribution channels under `## Decision`: a signed MSIX package (package identity, automatic updates, Store-ready) and an Inno Setup 7 installer of the same native build, carrying the MSVC runtime statically or app-local as §12 decides, naming the signing certificate source and how each channel updates. Done when: both channels name signing and update. Cheaper substitute: one channel, which drops either the Store path or machines that block MSIX. **Corrected 2026-10-22:** carried the Windows App SDK runtime self-contained.
- [ ] Record minimum OS versions and hardware baseline (RAM, display scaling range) per chosen target. Done when: each target has a minimum version. Cheaper substitute: "modern systems".
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

## 3. Text Layout and Pagination Engine Decision

Word fidelity depends on line breaking, justification, hyphenation, complex scripts, bidi text, tables, floats with text wrap, widows and orphans, and pagination that matches Word closely enough that a `.docx` keeps its page count. This record decides whether to build a layout engine on HarfBuzz and ICU, adopt an existing engine, or combine them.

**Phase:** 3
**Needs:** none
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

## 7. Mail, Calendar and Contacts Protocol Decision

The Outlook counterpart must talk to real mailboxes: IMAP and SMTP for any provider, JMAP where offered, CalDAV and CardDAV for calendars and contacts, and Microsoft Graph or Exchange Web Services for Microsoft 365 and Exchange accounts, plus Gmail through its API or IMAP with OAuth.

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

## 8. Storage, AutoSave and Co-Authoring Decision

The title bar's AutoSave toggle and the Share button imply cloud storage and real-time co-authoring. This record decides local-first storage, AutoSave semantics, version history, the cloud backend (own service, WebDAV, OneDrive and SharePoint through Graph, other providers), and the merge model (CRDT such as Yjs or Automerge, or operational transform). Decision, 2026-10-20 (owner): the first release works on local and network files with AutoSave and recovery; OneDrive and SharePoint through Microsoft Graph, and real-time co-authoring, come in a later milestone. No Rizonesoft cloud service is planned.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-storage-collab-design.md`. Done when: the record passes the checker with Decision.

- [ ] Specify local save semantics: atomic write, crash recovery files, AutoRecover interval and Document Recovery pane. Done when: each has a named mechanism. Cheaper substitute: overwrite in place.
- [ ] Compare CRDT and OT for each app's document model from §5. Done when: each app has a chosen merge model and its conflict cases. Cheaper substitute: last writer wins.
- [ ] Record the 2026-10-20 decision (local first; OneDrive and SharePoint plus co-authoring later; no own service) under `## Decision`, with the milestone that adds the cloud. Done when: the milestone and date are recorded. Cheaper substitute: designing the local model without the later merge model in mind.
- [ ] Commit: `arch: record storage and co-authoring decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-storage-collab-design.md --require Decision` exits 0.

## 9. Extensibility and Macro Decision

Microsoft 365 users depend on VBA macros in `.docm`, `.xlsm` and `.pptm`, and on Office Add-ins. This record decides macro preservation (always keep the `vbaProject.bin` part), execution (none, a VBA-compatible interpreter, or a different scripting language), the add-in model, and the security model for running code.

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

- [ ] Write the Architecture section with a component diagram `docs/plans/foundation-architecture.svg` naming each component's owning design record. Done when: every record from §1 to §11 is cited. Cheaper substitute: a list of libraries.
- [ ] Write the Repository layout section mapping components to directories. Done when: each top-level directory has a purpose line. Cheaper substitute: deciding layout while coding.
- [ ] Write the Toolchain section: the C++ standard flag and its C++26 rule, MSVC, the Windows SDK, CMake with presets, vcpkg in manifest mode, lint and format, the test framework, MSVC runtime linkage (static or app-local) and the CI matrix (x64 and Arm64). Done when: each tool has a version policy. Cheaper substitute: "standard tooling".
- [ ] Write the Milestones section ordering the shared platform and the six apps, with the parity bar per milestone as inventory coverage percentages. Done when: each milestone names its coverage target. Cheaper substitute: dates without a measurable bar.
- [ ] Update `AGENTS.md` with where the code lives and which commands verify it, from the Toolchain section. Done when: `AGENTS.md` lists the build, lint and test commands. Cheaper substitute: leaving the adaptation placeholder line.
- [ ] Add the application build and test commands from the Toolchain section to the Build and test section of `CONTRIBUTING.md`. Done when: every command listed there runs on a clean clone. Cheaper substitute: leaving the guide with the tooling commands only. (Deferred from D00 T02 §5 on 2026-10-21.)
- [ ] Commit: `arch: add foundation plan`

**Test checkpoint:** `python scripts/check-design-doc.py docs/plans/<dated>-foundation-plan.md --require Architecture --require "Repository layout" --require Toolchain --require Milestones` exits 0.

## 13. Platform and App TODO Domains

The plan becomes executable work: new domains for the shared platform and each app, authored with the `create-todo` skill, with every inventoried record (control, menu item, dialog, pane, view, Backstage page, Options setting, status bar item, command and shortcut) owned by exactly one section, 1:1 with Word, Excel, PowerPoint, Outlook, Visio and Project (owner request 2026-10-21).

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author the domains in the order of the foundation plan's Milestones. Done when: `python scripts/todo-graph.py validate` passes with all new domains.
2. Prove inventory ownership and keep it proven. Done when: `python scripts/inventory-report.py --owners --check` exits 0 and runs as a gate on every later TODO or inventory commit.

- [ ] Author `todo/04-platform/` (the GUI toolkit: windowing, controls, layout, focus, TSF text input, UI Automation providers and DPI; shell, ribbon engine, command model, Backstage, settings, file I/O, fonts, rendering, accessibility) with `create-todo`. Done when: every chapter of `design/SPEC.md` shared by all apps is owned by a section. Cheaper substitute: one umbrella platform section.
- [ ] Author one domain per app (`05-` onward, in Milestones order) with `create-todo`, each section listing every inventory record id it implements on its `> **Implements:**` lines (D02 T01 §22; a group's section lists each of its controls, menu items and dialog controls, not the group id alone). Done when: each app domain validates and `python scripts/inventory-report.py --owners --check --app <app>` exits 0 for that app. Cheaper substitute: one section per ribbon tab, or claiming only group ids.
- [ ] Author the interoperability domain (round-trip corpora, fidelity diffing against the reference apps) and the release domain (installers, signing, updates, store listings). Done when: both validate. Cheaper substitute: fidelity testing left to manual checks.
- [ ] Run `python scripts/inventory-report.py --owners --check` (D02 T01 §22) over all six apps and the shell. Done when: it exits 0 with no unowned, unknown or doubly owned id. Cheaper substitute: sampling a few ids by hand.
- [ ] Add `python scripts/inventory-report.py --owners --check` to `scripts/hooks/pre-commit` for commits that stage `todo/` or `design/inventory/`, with a test in `scripts/tests/test_pre_commit_hook.py`. Done when: staging a new inventory record with no citing section refuses the commit. Cheaper substitute: running the check only in this section.
- [ ] Add `python scripts/inventory-report.py --owners --check` to the audit commands of `process-plan` in `.claude/skills/`, `.agents/skills/` and `.codex/skills/`. Done when: all three mirrors list it and an unowned record is a refusal the audit fixes before shipping. Cheaper substitute: a note in `todo/README.md` only.
- [ ] Run `python scripts/todo-graph.py plan --sync` and commit the regenerated plan. Done when: `plan --check` exits 0. Cheaper substitute: editing `todo/implementation-plan.md` by hand.
- [ ] Commit: `todo: author platform and application domains`

**Test checkpoint:** `python scripts/inventory-report.py --owners --check` exits 0, `python -m unittest discover -s scripts/tests -p "test_pre_commit_hook.py"` passes and `python scripts/todo-graph.py validate` exits 0.

## Verification

- Every design record in `docs/specs/` named by §1 to §11 passes `scripts/check-design-doc.py` and carries a dated Decision.
- `docs/plans/<dated>-foundation-plan.md` passes the checker and `AGENTS.md` lists the real verify commands.
- `python scripts/inventory-report.py --owners` prints no unowned ids.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
