---
schema_version: 1
id: tech-stack
domain: 03-architecture
status: active
title: "TODO-01 -- Tech Stack and Foundation Plan"
---

# TODO-01 -- Tech Stack and Foundation Plan

> **Goal:** Every expensive-to-reverse technical choice for the suite is decided in a dated design record backed by a measured prototype where a claim needs proof: platform targets, shell framework, text layout, graphics, file formats, spreadsheet calculation, mail protocols, storage and co-authoring, extensibility, fonts, and licensing. The decisions roll up into a foundation plan in `docs/plans/`, and the implementation TODO domains for the shared platform and the six apps are authored from it and from the parity inventory.

> **Current state:** Measured 2026-10-20. No code, no design records and no foundation plan exist; `docs/` holds only the Conclave-SDK workflow documents. On 2026-10-20 the owner chose C++ with Qt 6 on Windows, macOS and Linux (§1, §2); the product licence is still open (§11). The repository runs on a Windows 11 Pro host with WSL available.

## Inputs

- `design/SPEC.md` (D02 T02) and `design/inventory/**` (D02 T01): the surface every stack candidate must render and the parity bar it must reach.
- ECMA-376 and ISO/IEC 29500 (Office Open XML), and Microsoft Open Specifications ([MS-DOCX], [MS-XLSX], [MS-PPTX], [MS-VSDX], [MS-DOC], [MS-XLS], [MS-PPT], [MS-OXMSG], [MS-OXCMSG]), covered by the Microsoft Open Specification Promise: the file format sources for §5.
- IMAP4rev2 (RFC 9051), SMTP (RFC 5321), JMAP (RFC 8620, RFC 8621), CalDAV (RFC 4791), CardDAV (RFC 6352), iCalendar (RFC 5545), Microsoft Graph and Exchange Web Services documentation: the protocol sources for §7.
- Global rule: specs go to `docs/specs/YYYY-MM-DD-<topic>-design.md` and plans to `docs/plans/YYYY-MM-DD-<feature>.md`, dated on the day they are written.
- -> XREF: D02 T02 §4 -- the shell framework must render the ribbon component chapter, including its scaling rules
- -> XREF: D02 T01 §18 -- application TODO sections cite inventory ids so the coverage report can count implemented elements

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
| 13 | §13 | Implementation TODO domains for platform and apps | §12, D02 T01 §18, D02 T02 §14 | [ ] |

## 1. Platform Targets Decision

Everything downstream depends on where the suite runs. Microsoft 365 ships native Windows and macOS apps, web apps and mobile apps; matching the Windows desktop first is the default implied by the inventory's reference build. Decision, 2026-10-20 (owner): Windows, macOS and Linux desktop, enabled by the C++ and Qt 6 choice in §2. Web and mobile are out of scope until the owner adds them.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-platform-targets-design.md` with the options and the owner's decision. Done when: the design-doc checker passes with `Decision`.

- [ ] List the candidate targets (Windows x64 and Arm64, macOS, Linux, web browser, iOS, Android) with the cost each adds in the design record. Done when: each target names one stack constraint it imposes. Cheaper substitute: "cross-platform" with no list.
- [ ] Record the owner's 2026-10-20 decision (Windows, macOS and Linux desktop) and the release order under `## Decision`. Done when: the decision names targets, order and date. Cheaper substitute: treating Windows as the only real target and porting later.
- [ ] Record minimum OS versions and hardware baseline (RAM, display scaling range) per chosen target. Done when: each target has a minimum version. Cheaper substitute: "modern systems".
- [ ] Commit: `arch: record platform targets decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-platform-targets-design.md --require Options --require Decision --require Consequences` exits 0.

## 2. Shell Framework Decision with Ribbon Prototype

Decision, 2026-10-20 (owner): C++ with Qt 6 on Windows, macOS and Linux. Qt can carry the Office look: WPS Office reproduces the Office ribbon on Qt, and every control is custom-painted from the tokens in `design/SPEC.md` rather than taken from a stock Qt style. Qt has no ribbon, so the ribbon is our own control set (an MIT-licensed Qt ribbon such as SARibbon may be studied but must match the Ribbon chapter's scaling rules). The prototype settles what the owner left open: Qt Widgets or Qt Quick (QML) for the shell, a frameless window whose custom title bar keeps Windows 11 Snap Layouts and the Mica backdrop, and UI Automation accessibility through `QAccessible`.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Build the Word Home tab in Qt Widgets and in Qt Quick in `R:\scratch\prototypes\`. Done when: both render every `word.home.*` control.
2. Measure both and record the module decision in `docs/specs/YYYY-MM-DD-shell-framework-design.md`. Done when: the checker passes with Measurements and Decision.

- [ ] Build the Word Home tab with the Classic Ribbon in Qt Widgets in `R:\scratch\prototypes\qt-widgets\`, driven by the `word.home.*` inventory records. Done when: every Home tab control renders at its inventoried size. Cheaper substitute: a stock `QToolBar`, which cannot express ribbon groups or scaling.
- [ ] Build the same tab in Qt Quick in `R:\scratch\prototypes\qt-quick\`. Done when: every Home tab control renders at its inventoried size. Cheaper substitute: prototyping only the module already preferred.
- [ ] Give each prototype a frameless window with a custom title bar that answers `WM_NCHITTEST` with `HTMAXBUTTON` over the maximise button. Done when: hovering maximise on Windows 11 shows the Snap Layouts flyout and the Mica backdrop shows behind the title bar. Cheaper substitute: the native title bar, which breaks the Office title bar layout, or a frameless window without snap.
- [ ] Measure cold start, idle memory, resize frame time while the ribbon scales, and UIA tree correctness with `scripts/capture-ui.py` for both prototypes. Done when: four numbers per prototype are under `## Measurements`. Cheaper substitute: vendor claims.
- [ ] Record the chosen module (Widgets or Quick), the Qt release (the current long-term-support release) and the date under `## Decision`, with the owner's confirmation. Done when: the decision names module, version and date. Cheaper substitute: choosing by familiarity.
- [ ] Commit: `arch: record Qt shell decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-shell-framework-design.md --require Measurements --require Decision` exits 0.

## 3. Text Layout and Pagination Engine Decision

Word fidelity depends on line breaking, justification, hyphenation, complex scripts, bidi text, tables, floats with text wrap, widows and orphans, and pagination that matches Word closely enough that a `.docx` keeps its page count. This record decides whether to build a layout engine on HarfBuzz and ICU, adopt an existing engine, or combine them.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-text-layout-design.md`. Done when: the record passes the checker with Measurements.

- [ ] List the candidate approaches (own C++ engine on HarfBuzz plus ICU, Qt's `QTextLayout`, LibreOffice Writer core) with licence and platform fit. Done when: each has licence, language and maintenance status with dates. Cheaper substitute: Qt's `QTextDocument` by default.
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

- [ ] List candidates (Skia, Qt's `QPainter` on the Qt rendering hardware interface, Blend2D, Direct2D and Core Graphics per platform) with licence and platform fit. Done when: each has licence and supported targets. Cheaper substitute: the framework default without comparison.
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
- [ ] List candidates (own C++ engine, LibreOffice Calc's formula core under MPL 2.0, IronCalc through its C interface) with licence, language and function coverage. Done when: each has a coverage percentage against the extracted list. Cheaper substitute: picking by stars.
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

The title bar's AutoSave toggle and the Share button imply cloud storage and real-time co-authoring. This record decides local-first storage, AutoSave semantics, version history, the cloud backend (own service, WebDAV, OneDrive and SharePoint through Graph, other providers), and the merge model (CRDT such as Yjs or Automerge, or operational transform).

**Phase:** 3
**Needs:** owner-decision
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-storage-collab-design.md`. Done when: the record passes the checker with Decision.

- [ ] Specify local save semantics: atomic write, crash recovery files, AutoRecover interval and Document Recovery pane. Done when: each has a named mechanism. Cheaper substitute: overwrite in place.
- [ ] Compare CRDT and OT for each app's document model from §5. Done when: each app has a chosen merge model and its conflict cases. Cheaper substitute: last writer wins.
- [ ] Record which cloud backends the first release supports and whether the project runs its own service, as an owner decision under `## Decision`, then remove `owner-decision`. Done when: backends and date are recorded. Cheaper substitute: assuming a hosted service with no owner or budget.
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

The product's own licence decides which dependencies are allowed: a permissive or copyleft open-source licence, or proprietary. The dependency policy then lists allowed and refused licences and the notice process.

**Phase:** 3
**Needs:** owner-decision
**Surface:** no

**Build order:**

1. Write `docs/specs/YYYY-MM-DD-licensing-design.md` with the owner's choice. Done when: the record passes the checker with Decision.

- [ ] Compare licence options (MIT or Apache 2.0, MPL 2.0, GPL or AGPL, proprietary) with their effect on dependencies such as Qt 6 (LGPLv3 with dynamic linking, or a commercial Qt licence), MPXJ (LGPL) and LibreOffice components (MPL). Done when: each option lists allowed dependency licences. Cheaper substitute: choosing a licence without checking dependencies.
- [ ] Record the owner's product licence under `## Decision`, then remove `owner-decision`. Done when: the decision and date are recorded and `LICENSE` exists at the repository root. Cheaper substitute: no `LICENSE` file.
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
- [ ] Update `AGENTS.md` with where the code lives and which commands verify it, from the Toolchain section. Done when: `AGENTS.md` lists the build, lint and test commands. Cheaper substitute: leaving the Conclave-SDK placeholder line.
- [ ] Commit: `arch: add foundation plan`

**Test checkpoint:** `python scripts/check-design-doc.py docs/plans/<dated>-foundation-plan.md --require Architecture --require "Repository layout" --require Toolchain --require Milestones` exits 0.

## 13. Implementation TODO Domains for Platform and Apps

The plan becomes executable work: new domains for the shared platform and each app, authored with the `create-todo` skill, with sections sized one inventory group at a time so every inventoried element has an owning section.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Author the domains in the order of the foundation plan's Milestones. Done when: `python scripts/todo-graph.py validate` passes with all new domains.
2. Prove inventory ownership. Done when: a script check shows every inventory group id cited by at least one section.

- [ ] Author `todo/04-platform/` (shell, ribbon engine, command model, Backstage, settings, file I/O, fonts, rendering, accessibility) with `create-todo`. Done when: every chapter of `design/SPEC.md` shared by all apps is owned by a section. Cheaper substitute: one umbrella platform section.
- [ ] Author one domain per app (`05-` onward, in Milestones order) with `create-todo`, one section per inventory group. Done when: each app domain validates. Cheaper substitute: one section per ribbon tab.
- [ ] Author the interoperability domain (round-trip corpora, fidelity diffing against the reference apps) and the release domain (installers, signing, updates, store listings). Done when: both validate. Cheaper substitute: fidelity testing left to manual checks.
- [ ] Add `--owners` to `scripts/inventory-report.py` listing inventory `group`, `dialog`, `pane` and `view` ids with no citing TODO section. Done when: the command prints an empty list. Cheaper substitute: sampling a few ids by hand.
- [ ] Run `python scripts/todo-graph.py plan --sync` and commit the regenerated plan. Done when: `plan --check` exits 0. Cheaper substitute: editing `todo/implementation-plan.md` by hand.
- [ ] Commit: `todo: author platform and application domains`

**Test checkpoint:** `python scripts/inventory-report.py --owners` prints no unowned ids and `python scripts/todo-graph.py validate` exits 0.

## Verification

- Every design record in `docs/specs/` named by §1 to §11 passes `scripts/check-design-doc.py` and carries a dated Decision.
- `docs/plans/<dated>-foundation-plan.md` passes the checker and `AGENTS.md` lists the real verify commands.
- `python scripts/inventory-report.py --owners` prints no unowned ids.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
