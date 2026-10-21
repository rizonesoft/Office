---
schema_version: 1
id: tech-stack
domain: 03-architecture
status: active
title: "TODO-01 -- Tech Stack and Foundation Plan"
---

# TODO-01 -- Tech Stack and Foundation Plan

> **Goal:** Every expensive-to-reverse technical choice for the suite is decided in a dated design record backed by a measured prototype where a claim needs proof: platform targets, shell framework, text layout, graphics, file formats, spreadsheet calculation, mail protocols, storage and co-authoring, extensibility, fonts, and licensing. The decisions roll up into a foundation plan in `docs/plans/`, and the implementation TODO domains for the shared platform and the six apps are authored from it and from the parity inventory.

> **Current state:** Measured 2026-10-20. No code, no design records and no foundation plan exist; `docs/` holds only the Conclave-SDK workflow documents. On 2026-10-20 the owner first chose C++ with Qt 6 on Windows, macOS and Linux, then the same day replaced it with WinUI 3 (Windows App SDK) in C# on .NET 11, Windows only, shipped as an MSIX package and an Inno Setup installer (§1, §2); the product licence stays GPL-3.0-or-later (§11). The repository runs on a Windows 11 Pro host with WSL available.

## Inputs

- `design/SPEC.md` (D02 T02) and `design/inventory/**` (D02 T01): the surface every stack candidate must render and the parity bar it must reach.
- ECMA-376 and ISO/IEC 29500 (Office Open XML), and Microsoft Open Specifications ([MS-DOCX], [MS-XLSX], [MS-PPTX], [MS-VSDX], [MS-DOC], [MS-XLS], [MS-PPT], [MS-OXMSG], [MS-OXCMSG]), covered by the Microsoft Open Specification Promise: the file format sources for §5.
- IMAP4rev2 (RFC 9051), SMTP (RFC 5321), JMAP (RFC 8620, RFC 8621), CalDAV (RFC 4791), CardDAV (RFC 6352), iCalendar (RFC 5545), Microsoft Graph and Exchange Web Services documentation: the protocol sources for §7.
- Global rule: specs go to `docs/specs/YYYY-MM-DD-<topic>-design.md` and plans to `docs/plans/YYYY-MM-DD-<feature>.md`, dated on the day they are written.
- -> XREF: D02 T02 §4 -- the shell framework must render the ribbon component chapter, including its scaling rules
- -> XREF: D02 T01 §18 -- application TODO sections cite inventory ids so the coverage report can count implemented elements
- -> XREF: D02 T01 §22 -- the record-level ownership check that holds every inventory record to exactly one owning section
- -> XREF: D00 T02 §2 -- the dependency licence policy decided in §11 is enforced through the third-party notices file

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
| 2 | §2 | Shell framework decision with ribbon prototype | §1, D02 T02 §4 | [ ] |
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

Everything downstream depends on where the suite runs. Microsoft 365 ships native Windows and macOS apps, web apps and mobile apps; matching the Windows desktop first is the default implied by the inventory's reference build. Decision, 2026-10-20 (owner, revised the same day): Windows desktop only, x64 and Arm64, following the move to WinUI 3 in §2; macOS, Linux, web and mobile are out of scope. **Corrected 2026-10-20:** the first decision that day was Windows, macOS and Linux on C++ with Qt 6. Distribution, decided the same day: a signed MSIX package and an Inno Setup installer (Inno Setup 7.1.0, the latest release, is installed on the operator's host) for the unpackaged build.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-platform-targets-design.md` with the options and the owner's decision. Done when: the design-doc checker passes with `Decision`.

- [ ] List the candidate targets (Windows x64 and Arm64, macOS, Linux, web browser, iOS, Android) with the cost each adds in the design record. Done when: each target names one stack constraint it imposes. Cheaper substitute: "cross-platform" with no list.
- [ ] Record the owner's 2026-10-20 decision (Windows desktop only, x64 and Arm64) under `## Decision`, with the earlier same-day decision it replaced. Done when: the decision names the targets, the date and what it replaced. Cheaper substitute: leaving macOS and Linux as an unstated maybe. **Corrected 2026-10-20:** said Windows, macOS and Linux with a release order.
- [ ] Record the distribution channels under `## Decision`: a signed MSIX package (package identity, automatic updates, Store-ready) and an Inno Setup 7 installer of the unpackaged build with the Windows App SDK runtime self-contained, naming the signing certificate source and how each channel updates. Done when: both channels name signing and update. Cheaper substitute: one channel, which drops either the Store path or machines that block MSIX.
- [ ] Record minimum OS versions and hardware baseline (RAM, display scaling range) per chosen target. Done when: each target has a minimum version. Cheaper substitute: "modern systems".
- [ ] Commit: `arch: record platform targets decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-platform-targets-design.md --require Options --require Decision --require Consequences` exits 0.

## 2. Shell Framework Decision with Ribbon Prototype

Decision, 2026-10-20 (owner): WinUI 3 from the Windows App SDK (MIT), in C# on .NET 11 (the release candidate now, the release once it ships), replacing C++ with Qt 6 chosen earlier the same day. Pin: Windows App SDK 2.5.1, the latest stable release (16 September 2026), which fixes crashes in NavigationView and KeyboardAccelerator and a CommandBar overflow button that wrongly appeared at 175 percent scaling, all three used by the shell. Pin rule (owner, 2026-10-20): the pin is always the latest stable WinUI 3 release in the microsoft-ui-xaml repository's releases (tags `winui3/release/<version>`; `-experimental` releases excluded), moved forward as soon as a newer stable release appears. WinUI 3 has no ribbon, so the ribbon is our own control set built from WinUI primitives and the tokens in `design/SPEC.md`. Ink controls (InkCanvas, InkToolbar, InkPresenter) exist only in experimental releases (2.4.1-experimental, extended in 2.5.4-experimental): no section may depend on them until a stable release ships them. Speed (owner concern): WinUI 3 itself is native code in every language; C# drives it, cold start is handled by ReadyToRun or Native AOT, and any engine (text layout, recalculation, rendering) that misses its measured budget in C# is written in C++ and called from C#. Feasibility, measured 2026-10-20 in `R:\scratch\prototypes\winui3-feasibility\`: WinUI 3 from Windows App SDK 2.5.1 builds on .NET 11 release candidate 2 and runs unpackaged (window shown, .NET 11.0.0); median time to a visible window over five runs is 239 ms with ReadyToRun and 327 ms with plain JIT; a Native AOT publish fails on .NET 11 RC (the XAML compiler receives no references in the publish pass, error WMC1007), while the same app on .NET 10 publishes with Native AOT in 222 ms and no trim warnings. The same app packs into an unsigned MSIX package (98 MB) and into an Inno Setup 7.1.0 installer of the ReadyToRun publish (76 MB).

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Build the Word Home tab in WinUI 3 in `R:\scratch\prototypes\winui3-ribbon\`. Done when: it renders every `word.home.*` control.
2. Measure it and the engine benchmark, and record the decision in `docs/specs/YYYY-MM-DD-shell-framework-design.md`. Done when: the checker passes with Measurements and Decision. **Corrected 2026-10-20:** compared Qt Widgets with Qt Quick.

- [ ] Build the Word Home tab with the Classic Ribbon in WinUI 3 (C#) in `R:\scratch\prototypes\winui3-ribbon\`, driven by the `word.home.*` inventory records. Done when: every Home tab control renders at its inventoried size. Cheaper substitute: a stock `CommandBar`, which cannot express ribbon groups or scaling. **Corrected 2026-10-20:** was a Qt Widgets prototype.
- [ ] Benchmark one engine-shaped workload (laying out and breaking the text runs of a 100-page document) in C# and in a C++ library called from C#, in `R:\scratch\prototypes\engine-benchmark\`. Done when: both times are under `## Measurements` with the rule they set for when an engine goes native. Cheaper substitute: assuming C++ is faster. **Corrected 2026-10-20:** was a Qt Quick prototype.
- [ ] Give the prototype a custom title bar through `AppWindow.TitleBar` with content extended into it, keeping Windows 11 Snap Layouts and the Mica backdrop (`MicaBackdrop`). Done when: hovering maximise on Windows 11 shows the Snap Layouts flyout and Mica shows behind the title bar. Cheaper substitute: the default title bar, which breaks the Office title bar layout.
- [ ] Measure cold start (ReadyToRun, and Native AOT where the .NET 11 release publishes it), idle memory, resize frame time while the ribbon scales, and UIA tree correctness with `scripts/capture-ui.py`. Done when: the numbers are under `## Measurements`. Cheaper substitute: vendor claims.
- [x] Add `scripts/check-winui-pin.py`, which reads the pinned `Microsoft.WindowsAppSDK` version from the repository's package versions file and compares it with the newest stable `winui3/release/<version>` tag through `gh api`, exiting 1 when a newer stable release exists; CI and every phase start run it. Done when: a fixture pinned to 2.4.0 fails, the current pin passes, and an `-experimental` tag never counts as newer. Cheaper substitute: checking for new releases by hand. Done 2026-10-20: `Directory.Packages.props` holds the pin, and the daily `office-winui-pin` task (`.conclave/automations/`) proposes each newer stable release on a `winui/<version>` branch and emails the operator; `scripts/tests/test_check_winui_pin.py` covers the 2.4.0 fixture, the current pin and experimental releases.
- [ ] Record the pins (Windows App SDK 2.5.1, the .NET 11 release, ReadyToRun or Native AOT by the measurements) and the date under `## Decision`, with the owner's confirmation. Done when: the decision names framework, versions and date. Cheaper substitute: floating versions.
- [ ] Commit: `arch: record WinUI 3 shell decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-shell-framework-design.md --require Measurements --require Decision` exits 0.

## 3. Text Layout and Pagination Engine Decision

Word fidelity depends on line breaking, justification, hyphenation, complex scripts, bidi text, tables, floats with text wrap, widows and orphans, and pagination that matches Word closely enough that a `.docx` keeps its page count. This record decides whether to build a layout engine on HarfBuzz and ICU, adopt an existing engine, or combine them.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-text-layout-design.md`. Done when: the record passes the checker with Measurements.

- [ ] List the candidate approaches (own engine in C# on DirectWrite through the Windows App SDK's DWriteCore, with native code where §2's benchmark rule calls for it; the rich edit control behind `RichEditBox`; LibreOffice Writer core) with licence and fit. Done when: each has licence, language and maintenance status with dates. Cheaper substitute: `RichEditBox` by default, which cannot paginate like Word. **Corrected 2026-10-20:** listed HarfBuzz plus ICU in C++ and Qt's `QTextLayout`.
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

- [ ] List candidates (Win2D, Direct2D and Direct3D through a `SwapChainPanel`, SkiaSharp, the Windows composition layer) with licence and fit. Done when: each has licence and a note on DrawingML effect support. Cheaper substitute: the framework default without comparison. **Corrected 2026-10-20:** listed Qt's `QPainter`, Blend2D and per-platform renderers for macOS and Linux.
- [ ] Render a DrawingML effects test slide (shadow, glow, gradient, soft edges, picture crop) with the top two candidates in `R:\scratch\prototypes\graphics\`. Done when: per-effect support is recorded. Cheaper substitute: rendering rectangles only.
- [ ] Record PDF output strategy (same renderer to PDF, or separate PDF writer). Done when: the strategy names the library and its licence. Cheaper substitute: printing to the OS PDF printer.
- [ ] Record the decision under `## Decision`. Done when: renderer, version and date are named. Cheaper substitute: per-app renderer choices.
- [ ] Commit: `arch: record graphics decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-graphics-design.md --require Measurements --require Decision` exits 0.

## 5. File Format Strategy Decision

The suite reads and writes Microsoft's formats as first-class: `.docx`, `.xlsx`, `.pptx`, `.vsdx` (OOXML), legacy `.doc`, `.xls`, `.ppt`, `.vsd`, Project `.mpp` and `.xml`, Outlook `.msg`, `.eml`, `.pst` and `.ics`, plus ODF, CSV, RTF and PDF export. This record decides per format: own implementation from the open specifications, an existing library, or read-only support.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-file-formats-design.md` with a per-format decision table. Done when: every format in this section has a row.

- [ ] Write the format table: format, read, write, specification, candidate library, licence. Done when: every format named in this section has a row at most 100 characters. Cheaper substitute: OOXML only.
- [ ] Decide the in-memory document model per app and whether it mirrors OOXML parts. Done when: the record states how unknown OOXML elements are preserved on round-trip. Cheaper substitute: dropping unknown elements on save.
- [ ] Assemble round-trip corpora (20 files each for `.docx`, `.xlsx`, `.pptx`, `.vsdx`) in `R:\scratch\corpus\`. Done when: corpus lists are in the record. Cheaper substitute: files created by our own writer.
- [ ] Record the `.mpp` decision (MPXJ, LGPL, read-only versus own reader) and the `.pst` decision. Done when: each states read and write scope. Cheaper substitute: silently excluding Project and Outlook stores.
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
- [ ] List candidates (own engine in C#, native where §2's benchmark rule calls for it; LibreOffice Calc's formula core under MPL 2.0; IronCalc through its C interface) with licence, language and function coverage. Done when: each has a coverage percentage against the extracted list. Cheaper substitute: picking by stars.
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

The product's own licence decides which dependencies are allowed: a permissive or copyleft open-source licence, or proprietary. The dependency policy then lists allowed and refused licences and the notice process. Decision, 2026-10-20 (owner): GPL-3.0-or-later with a contributor licence agreement so Rizonesoft can still offer a commercial edition; chosen first to match Qt's open-source edition and kept the same day after the move to WinUI 3, whose MIT licence is compatible. `LICENSE` and the `README.md` notice landed the same day; enforcement is D00 T02.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-licensing-design.md` with the owner's choice. Done when: the record passes the checker with Decision.

- [ ] Compare licence options (MIT or Apache 2.0, MPL 2.0, GPL or AGPL, proprietary) with their effect on dependencies such as the Windows App SDK and WinUI 3 (MIT), the .NET runtime (MIT), Win2D (MIT), MPXJ (LGPL) and LibreOffice components (MPL). **Corrected 2026-10-20:** named Qt 6 (LGPLv3 or commercial) as the main dependency. Done when: each option lists allowed dependency licences. Cheaper substitute: choosing a licence without checking dependencies.
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
- [ ] Write the Toolchain section: languages, package managers, build, lint, test and CI matrix per target. Done when: each tool has a version policy. Cheaper substitute: "standard tooling".
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

- [ ] Author `todo/04-platform/` (shell, ribbon engine, command model, Backstage, settings, file I/O, fonts, rendering, accessibility) with `create-todo`. Done when: every chapter of `design/SPEC.md` shared by all apps is owned by a section. Cheaper substitute: one umbrella platform section.
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
