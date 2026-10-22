---
schema_version: 1
id: interface-spec
domain: 02-interface
status: active
title: "TODO-02 -- Interface Specification"
---

# TODO-02 -- Interface Specification

> **Goal:** `design/SPEC.md` is the governing interface document for the suite: design tokens, the shared shell, the ribbon component model, Backstage, status bar, accessibility, and one surface chapter per app. Every region and control is placed where the parity inventory measured it, cites inventory ids, and uses the suite's own visual language (tokens, open fonts, original command glyphs), so the layout matches Microsoft 365 while nothing copies Microsoft artwork. Static mockups per app carry the owner's sign-off.

> **Current state:** Measured 2026-10-19. `design/SPEC.md` does not exist; `todo/README.md` already names it as the governing interface document. The parity inventory (D02 T01) and icon language (D01 T02 §1) are not yet written.

## Inputs

- `design/inventory/**` from D02 T01: element ids, order, size and `bounds` at the reference capture profile.
- `docs/brand/icon-language.md` and `docs/brand/NAMES.md` from D01: palette, motif and names.
- Fluent UI System Icons (MIT licence, published by Microsoft on GitHub), Lucide (ISC), Phosphor (MIT) and Tabler (MIT): candidate command glyph sources for §2.
- Selawik (SIL OFL 1.1, Microsoft's open fallback metric-compatible with Segoe UI), Inter (OFL) and Noto Sans (OFL): candidate UI fonts for §1. Segoe UI, Aptos and Calibri are Microsoft-licensed and never bundled.
- WCAG 2.2 level AA: the accessibility bar for §13.
- -> XREF: D02 T01 §4 -- the shell layout is measured from the shell chrome inventory
- -> XREF: D01 T02 §1 -- command glyphs must sit visually with the app icon language
- -> XREF: D03 T01 §2 -- the GUI toolkit is chosen against the ribbon component spec in §4

## Outcome

- `design/tokens/tokens.json` defines colour, type, spacing, radius, elevation and motion tokens for the light, dark and high-contrast themes, with one accent per app.
- `design/SPEC.md` has chapters for Tokens, Shell, Ribbon, Backstage, Status bar, Accessibility and one per app, each citing inventory ids, and passes `scripts/check-design-doc.py`.
- `design/mockups/<app>.svg` exists for all six apps and `design/SPEC.md` records the owner's sign-off per app.

**Adjacency:** list=applicable @ D02 T02 §5; document=applicable @ D02 T02 §5; settings=applicable @ D02 T02 §5; reporting=not-applicable (specification only; report surfaces are specified per app in §7 to §12); notifications=applicable @ D02 T02 §3; permissions=not-applicable (no access control in the shell specification); audit=not-applicable (specification only); exchange=applicable @ D02 T02 §5; reverse=applicable @ D02 T02 §4

**Adjacency rationale:** The spec decides where product-wide surfaces live: the recent and pinned file list, Print and Export, Options and Account all sit in Backstage (§5); notifications (AutoSave state, co-authoring presence, message bars under the ribbon) sit in the shell (§3); undo and redo live in the Quick Access Toolbar and ribbon command model (§4). Implementation of each is owned by the platform and app domains authored from D03 T01 §13.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Design tokens and themes | D01 T02 §1 | [ ] |
| 2 | §2 | Command glyph decision | §1 | [ ] |
| 3 | §3 | Shell layout chapter | §1, D02 T01 §4 | [ ] |
| 4 | §4 | Ribbon component chapter | §3, D02 T01 §5 | [ ] |
| 5 | §5 | Backstage chapter | §3, D02 T01 §6 | [ ] |
| 6 | §6 | Status bar chapter | §3, D02 T01 §6 | [ ] |
| 7 | §7 | Word surface chapter | §4, §5, §6, D02 T01 §6 | [ ] |
| 8 | §8 | Excel surface chapter | §4, §5, §6, D02 T01 §8 | [ ] |
| 9 | §9 | PowerPoint chapter | §4, §5, §6, D02 T01 §10 | [ ] |
| 10 | §10 | Visio surface chapter | §4, §5, §6, D02 T01 §12 | [ ] |
| 11 | §11 | Project surface chapter | §4, §5, §6, D02 T01 §14 | [ ] |
| 12 | §12 | Outlook surface chapter | §4, §5, §6, D02 T01 §16 | [ ] |
| 13 | §13 | Accessibility chapter | §4, D02 T01 §17 | [ ] |
| 14 | §14 | Mockups and sign-off | §2, §7, §8, §9, §10, §11, §12 | [ ] |

## 1. Design Tokens and Themes

Tokens are the single source for every colour, size and font the interface uses, so later code never hardcodes a value. Themes follow the reference app's choices (light, dark, and a system-following mode) plus Windows high-contrast support.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write `design/tokens/tokens.json` in the W3C Design Tokens Community Group format. Done when: it parses as JSON and defines every group in the micro-steps.
2. Write the Tokens chapter of `design/SPEC.md`. Done when: the design-doc checker passes with `Tokens`.

- [ ] Define neutral and surface colour tokens for light and dark themes in `design/tokens/tokens.json`. Done when: body text on every surface reaches 4.5:1, recorded in the Tokens chapter. Cheaper substitute: sampling Microsoft's hex values from screenshots.
- [ ] Define one accent token per app from `docs/brand/icon-language.md` in `design/tokens/tokens.json`. Done when: six accents exist and each reaches 3:1 against the title bar surface. Cheaper substitute: one accent for the whole suite.
- [ ] Choose the UI font from the candidates in Inputs and record the choice and licence in the Tokens chapter of `design/SPEC.md`. Done when: the font is OFL or equivalent and its metrics are compared with Segoe UI at 9 pt. Cheaper substitute: depending on Segoe UI being installed.
- [ ] Define type ramp, spacing scale, corner radius, elevation and motion duration tokens in `design/tokens/tokens.json`, measured against inventory `bounds`. Done when: the ribbon control heights in D02 T01 records are expressible with the spacing scale. Cheaper substitute: arbitrary round numbers.
- [ ] Define high-contrast mappings to Windows system colours in `design/tokens/tokens.json`. Done when: each surface token maps to a CSS system colour keyword or platform equivalent. Cheaper substitute: ignoring forced-colours mode.
- [ ] Commit: `spec: add design tokens and themes`

**Test checkpoint:** `python -c "import json; json.load(open('design/tokens/tokens.json'))"` exits 0 and `python scripts/check-design-doc.py design/SPEC.md --require Tokens` exits 0.

## 2. Command Glyph Decision

The ribbon needs roughly two thousand small command glyphs across six apps. Decision, 2026-10-20 (owner): Fluent UI System Icons (MIT, published by Microsoft on GitHub), the closest set to Office and compatible with the product's GPL-3.0-or-later licence; original glyphs are drawn in the same style only where the set has no match.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Map every inventory command to a Fluent UI System Icons glyph in `docs/specs/YYYY-MM-DD-command-glyphs-design.md` (dated when written). Done when: every `control` record has a glyph or is listed as a gap.
2. Pin the set's version and record the notice. Done when: the version is pinned and the notice exists.

- [ ] Map each inventory `control` record to a Fluent UI System Icons glyph name and size (16, 20, 24 or 32) in `docs/specs/YYYY-MM-DD-command-glyphs-design.md`. Done when: the coverage percentage and the gap list are recorded. Cheaper substitute: picking glyphs per control while coding, which drifts between apps.
- [ ] Record the regular versus filled usage rule and the colour treatment for glyphs on the ribbon in the same document. Done when: both rules cite the Ribbon chapter's states. Cheaper substitute: mixing regular and filled glyphs at random.
- [ ] Record the 2026-10-20 decision, the pinned version and the rule for drawing gap glyphs in the document under `## Decision`. Done when: the decision names the set, the version and the date. Cheaper substitute: mixing sets ad hoc per app.
- [ ] Add the chosen set's licence text to `THIRD-PARTY-NOTICES.md`. Done when: the notice names the set, version and licence. Cheaper substitute: a link instead of the licence text.
- [ ] Commit: `spec: record command glyph library decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/specs/<dated>-command-glyphs-design.md --require Decision` exits 0 and `Select-String -Path THIRD-PARTY-NOTICES.md -Pattern "License"` finds the chosen set.

## 3. Shell Layout Chapter

The Shell chapter fixes the window frame every app shares: title bar, Quick Access Toolbar, search, account, tab row, ribbon area, message bar, document area, task pane docking and status bar, with sizes at 100 percent scaling and behaviour on resize, as measured in `design/inventory/shell/chrome.json`.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write the Shell chapter of `design/SPEC.md` with a region diagram and a region table citing `shell.*` ids. Done when: every `shell.*` record is cited at least once.

- [ ] Draw the region diagram as an SVG `design/spec/shell-regions.svg` with dimensions from inventory `bounds`. Done when: every region carries its height in pixels. Cheaper substitute: a screenshot of Microsoft's window.
- [ ] Write the region table in the Shell chapter of `design/SPEC.md`: region, height, contents, inventory ids. Done when: rows are at most 100 characters and cite ids. Cheaper substitute: prose without ids.
- [ ] Specify title bar behaviour (drag, double-click maximise, snap layouts, caption buttons, AutoSave toggle states) in the Shell chapter. Done when: each behaviour cites a `shell.titlebar.*` id. Cheaper substitute: "standard window behaviour".
- [ ] Specify the message bar (information, warning, error, protected view) in the Shell chapter with its dismiss and action buttons. Done when: each variant has colour tokens and an action. Cheaper substitute: modal dialogs for every notice.
- [ ] Specify task pane docking, resizing, minimum widths and stacking in the Shell chapter. Done when: the pane rules cite pane widths from the app inventories. Cheaper substitute: fixed-width panes.
- [ ] Commit: `spec: add shell layout chapter`

**Test checkpoint:** `python scripts/check-design-doc.py design/SPEC.md --require Shell` exits 0 and `python scripts/check-image-asset.py design/spec/shell-regions.svg --format svg` exits 0.

## 4. Ribbon Component Chapter

The ribbon is the hardest shared component: control types and sizes, groups and dialog launchers, galleries with in-ribbon rows and expansion, split buttons, contextual tab sets with their colour band, KeyTips, Classic versus Simplified mode (per D02 T01 §2), and the scaling rules that collapse groups as the window narrows.

**Phase:** 2
**Needs:** office, windows-host, display-session
**Surface:** no

**Build order:**

1. Write the Ribbon chapter of `design/SPEC.md`. Done when: every `controlType` value in `design/inventory/schema.json` has a specification.
2. Specify group scaling with a measured collapse sequence. Done when: the Word Home tab collapse order at 1920, 1366, 1024 and 800 pixels is recorded.

- [ ] Specify each control type (button, splitButton, dropdown, gallery, comboBox, checkBox, toggleButton, spinner, dialogLauncher, menu, colorPicker, editBox) in large, medium and small sizes in the Ribbon chapter. Done when: each type has dimensions, states (rest, hover, pressed, checked, disabled, focus) and tokens. Cheaper substitute: one generic button spec.
- [ ] Specify galleries: in-ribbon row count, scroll arrows, expand drop-down, live preview on hover. Done when: the Styles gallery behaviour cites its inventory id. Cheaper substitute: galleries as drop-down lists.
- [ ] Measure the Word Home tab group collapse order at 1920, 1366, 1024 and 800 pixel widths with `scripts/capture-ui.py` and record it in the Ribbon chapter. Done when: each width lists each group's state (large, medium, small, collapsed). Cheaper substitute: an assumed right-to-left collapse.
- [ ] Specify the general scaling algorithm (per-group scale policies and priority) that reproduces the measured order. Done when: applying the algorithm by hand to the Excel Home tab matches a measurement at 1024 pixels. Cheaper substitute: horizontal scrolling of the ribbon.
- [ ] Specify contextual tab sets (colour band, label above the tab, activation on selection) and KeyTips (Alt layers, badge placement, sequences). Done when: both cite inventory ids. Cheaper substitute: contextual commands in a floating toolbar.
- [ ] Specify the Simplified Ribbon (single row, overflow menu, which commands each tab keeps) and Office's switch between Classic and Simplified, per the D02 T01 §2 decision. Done when: every app tab cites both its `ribbon.json` and `ribbon-simplified.json` records. Cheaper substitute: Classic only, with Simplified left for later.
- [ ] Specify the command model behind controls: command id, enabled and checked state, undo unit, and Quick Access Toolbar pinning. Done when: Undo and Redo specify their split-button history list. Cheaper substitute: controls that call handlers directly with no shared command state.
- [ ] Commit: `spec: add ribbon component chapter`

**Test checkpoint:** `python scripts/check-design-doc.py design/SPEC.md --require Ribbon` exits 0, and `python scripts/inventory-report.py --cited-in design/SPEC.md --control-types` reports every control type cited.

## 5. Backstage Chapter

Backstage (the File tab) holds the product-wide document lifecycle: Home, New, Open, Info, Save, Save As, Print, Share, Export, Close, Account and Options. It is shared across apps with per-app differences recorded in the inventories.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write the Backstage chapter of `design/SPEC.md` with one subsection per page. Done when: each page cites the shared and per-app inventory ids.

- [ ] Specify the Backstage frame (left navigation, back button, content area widths) in the Backstage chapter. Done when: the frame cites `shell.*` and per-app backstage ids. Cheaper substitute: a modal dialog for File.
- [ ] Specify Home, New and Open pages with the recent list, pinned list, search and template gallery. Done when: list sort, pin, remove-from-list and open-location actions are specified. Cheaper substitute: an OS file dialog only.
- [ ] Specify Info, Save, Save As and Close, including document properties, protection, inspection and version history entries. Done when: each action names its refusal path (read-only location, name conflict, unsaved changes prompt). Cheaper substitute: happy paths only.
- [ ] Specify Print and Export with print preview, printer and page settings, PDF and XPS export, and change file type. Done when: each per-app variant (for example Excel print area, PowerPoint handouts) is listed. Cheaper substitute: the OS print dialog only.
- [ ] Specify Account and Options: theme, account, product information, and the Options dialog frame with per-app categories from the inventories. Done when: every Options category of every app is listed with its owner chapter. Cheaper substitute: a settings JSON file instead of an Options dialog.
- [ ] Commit: `spec: add Backstage chapter`

**Test checkpoint:** `python scripts/check-design-doc.py design/SPEC.md --require Backstage --require Print --require Options` exits 0.

## 6. Status Bar Chapter

The status bar shows document state on the left and view and zoom controls on the right, and each app customises it through a right-click menu.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write the Status bar chapter of `design/SPEC.md`. Done when: each app's status bar items and customise menu are specified with inventory ids.

- [ ] Specify the shared status bar frame (height, left and right zones, overflow) in the Status bar chapter. Done when: the frame cites `shell.*` ids and height. Cheaper substitute: a per-app status bar with no shared frame.
- [ ] Specify the customise menu behaviour (checked items, live values, persistence per user). Done when: persistence is stated as a user setting with its owner. Cheaper substitute: a fixed set of items.
- [ ] Specify the zoom slider, zoom percentage button and zoom dialog with steps and limits per app. Done when: Word 10 to 500 percent and Excel 10 to 400 percent are stated from the inventories. Cheaper substitute: one zoom range for every app.
- [ ] Commit: `spec: add status bar and zoom chapter`

**Test checkpoint:** `python scripts/check-design-doc.py design/SPEC.md --require "Status bar"` exits 0.

## 7. Word Surface Chapter

The Word chapter specifies the word processor's surface: every tab and contextual tab with groups and controls in inventory order, the document canvas (page view, margins, rulers, navigation pane, comments margin, track-changes balloons), views, panes and dialogs.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write the Word chapter of `design/SPEC.md` citing `word.*` ids. Done when: every `word.*` tab and dialog id is cited.

- [ ] Specify each Word tab as a table of groups with control ids, sizes and the behaviour owner in the Word chapter. Done when: `python scripts/inventory-report.py --cited-in design/SPEC.md --app word --kind tab` reports 100 percent. Cheaper substitute: a tab list without groups.
- [ ] Specify the document canvas: page shadows, page gap, rulers, margins, text boundaries, selection colours, comment margin and change balloons. Done when: each element has tokens and dimensions. Cheaper substitute: a plain scrolling text area.
- [ ] Specify Word views (Read Mode, Print Layout, Web Layout, Outline, Draft, Focus, Immersive Reader) and their chrome changes. Done when: each view lists hidden and shown regions. Cheaper substitute: Print Layout only.
- [ ] Specify every Word dialog in `design/inventory/word/dialogs.json` as layout and fields, citing ids. Done when: dialog citations reach 100 percent in the report. Cheaper substitute: dialogs listed by name.
- [ ] Commit: `spec: add Word surface chapter`

**Test checkpoint:** `python scripts/inventory-report.py --cited-in design/SPEC.md --app word` reports 100 percent of `tab`, `contextualTab` and `dialog` records cited.

## 8. Excel Surface Chapter

The Excel chapter specifies the spreadsheet surface: tabs and contextual tabs, Name Box and formula bar, grid (headers, gridlines, selection, fill handle, freeze panes, split), sheet tabs, Excel views, panes and dialogs.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write the Excel chapter of `design/SPEC.md` citing `excel.*` ids. Done when: every `excel.*` tab and dialog id is cited.

- [ ] Specify each Excel tab as a table of groups with control ids in the Excel chapter. Done when: the report shows 100 percent of Excel `tab` records cited. Cheaper substitute: a tab list without groups.
- [ ] Specify the grid: default column width and row height, header styles, gridline colour token, active cell border, selection fill, fill handle, marching ants, freeze and split lines. Done when: each element has tokens and pixel sizes from the inventory. Cheaper substitute: an HTML table look.
- [ ] Specify the Name Box, formula bar expand behaviour, sheet tab strip (navigation arrows, new sheet, colours, context menu) and Normal, Page Break Preview and Page Layout views. Done when: each cites its ids. Cheaper substitute: Normal view only.
- [ ] Specify every Excel dialog in `design/inventory/excel/dialogs.json`. Done when: dialog citations reach 100 percent. Cheaper substitute: names only.
- [ ] Commit: `spec: add Excel surface chapter`

**Test checkpoint:** `python scripts/inventory-report.py --cited-in design/SPEC.md --app excel` reports 100 percent of `tab`, `contextualTab` and `dialog` records cited.

## 9. PowerPoint Chapter

The PowerPoint chapter specifies the presentation surface: tabs and contextual tabs, thumbnail pane, slide canvas with guides and smart guides, notes pane, the master views, Slide Show and Presenter View, panes and dialogs.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write the PowerPoint chapter of `design/SPEC.md` citing `powerpoint.*` ids. Done when: every tab, view and dialog id is cited.

- [ ] Specify each PowerPoint tab as a table of groups with control ids. Done when: the report shows 100 percent of PowerPoint `tab` records cited. Cheaper substitute: a tab list without groups.
- [ ] Specify the Normal view layout: thumbnail pane, slide canvas centring and scaling, guides, smart guides, notes pane and resize splitters. Done when: each element has tokens and sizes. Cheaper substitute: a fixed-size canvas.
- [ ] Specify Slide Show and Presenter View chrome and controls. Done when: Presenter View regions cite the inventory `view` record. Cheaper substitute: full-screen canvas without presenter tools.
- [ ] Specify every PowerPoint dialog and master view. Done when: dialog and view citations reach 100 percent. Cheaper substitute: names only.
- [ ] Commit: `spec: add PowerPoint surface chapter`

**Test checkpoint:** `python scripts/inventory-report.py --cited-in design/SPEC.md --app powerpoint` reports 100 percent of `tab`, `view` and `dialog` records cited.

## 10. Visio Surface Chapter

The Visio chapter specifies the diagramming surface: tabs and contextual tabs, Shapes pane and stencils, drawing page with rulers and grid, page tabs, connectors and glue feedback, Pan and Zoom, Shape Data and Size and Position panes, and dialogs.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write the Visio chapter of `design/SPEC.md` citing `visio.*` ids. Done when: every tab, pane and dialog id is cited.

- [ ] Specify each Visio tab as a table of groups with control ids. Done when: the report shows 100 percent of Visio `tab` records cited. Cheaper substitute: a tab list without groups.
- [ ] Specify the Shapes pane and the drag-to-canvas interaction (drop preview, AutoConnect arrows, Quick Shapes mini toolbar). Done when: each interaction state has tokens. Cheaper substitute: a click-to-insert list.
- [ ] Specify the drawing page chrome: rulers, grid, guides, page tabs, connection point and glue highlights. Done when: each element has tokens and sizes. Cheaper substitute: a blank canvas.
- [ ] Specify every Visio pane and dialog. Done when: pane and dialog citations reach 100 percent. Cheaper substitute: names only.
- [ ] Specify the modernised Visio surface under `### Modernisation` in its chapter of `design/SPEC.md`: every inventoried tab, group and command keeps its place, drawn with the Word, Excel and PowerPoint shell (title bar with search, Fluent glyphs, rounded controls, Mica, light and dark themes, the Simplified Ribbon option, Backstage, task panes, dialogs and status bar), and a table lists each layout change from the classic app (for example the Shapes window as a task pane, the ruler and grid colours, and the status bar page tabs) with the Word, Excel or PowerPoint pattern it follows and the inventory ids it moves. Done when: the table has a row per changed region and `python scripts/inventory-report.py --cited-in design/SPEC.md --app visio` still reports 100 percent. Cheaper substitute: copying the classic app's dated layout, or redesigning beyond patterns Word, Excel and PowerPoint already use. Owner request 2026-10-22 (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 5).
- [ ] Commit: `spec: add Visio surface chapter`

**Test checkpoint:** `python scripts/inventory-report.py --cited-in design/SPEC.md --app visio` reports 100 percent of `tab`, `pane` and `dialog` records cited.

## 11. Project Surface Chapter

The Project chapter specifies the scheduling surface: tabs and contextual Format tabs, the Timeline band, the split Gantt view (sheet plus chart with a draggable divider), every built-in view, the view bar, task and resource forms, and dialogs.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write the Project chapter of `design/SPEC.md` citing `project.*` ids. Done when: every tab, view and dialog id is cited.

- [ ] Specify each Project tab as a table of groups with control ids. Done when: the report shows 100 percent of Project `tab` records cited. Cheaper substitute: a tab list without groups.
- [ ] Specify the Gantt view: sheet columns, chart timescale tiers, bar styles, link lines, today line, progress, critical path colouring and divider behaviour. Done when: each element has tokens. Cheaper substitute: a static bar chart.
- [ ] Specify the other built-in views from `design/inventory/project/panes.json`. Done when: view citations reach 100 percent. Cheaper substitute: Gantt only.
- [ ] Specify every Project dialog. Done when: dialog citations reach 100 percent. Cheaper substitute: names only.
- [ ] Specify the modernised Project surface under `### Modernisation` in its chapter of `design/SPEC.md`: every inventoried tab, group and command keeps its place, drawn with the Word, Excel and PowerPoint shell (title bar with search, Fluent glyphs, rounded controls, Mica, light and dark themes, the Simplified Ribbon option, Backstage, task panes, dialogs and status bar), and a table lists each layout change from the classic app (for example the Gantt bar styles, the timeline, the view bar, and grid headers matching Excel's) with the Word, Excel or PowerPoint pattern it follows and the inventory ids it moves. Done when: the table has a row per changed region and `python scripts/inventory-report.py --cited-in design/SPEC.md --app project` still reports 100 percent. Cheaper substitute: copying the classic app's dated layout, or redesigning beyond patterns Word, Excel and PowerPoint already use. Owner request 2026-10-22 (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 5).
- [ ] Commit: `spec: add Project surface chapter`

**Test checkpoint:** `python scripts/inventory-report.py --cited-in design/SPEC.md --app project` reports 100 percent of `tab`, `view` and `dialog` records cited.

## 12. Outlook Surface Chapter

The Outlook chapter specifies the mail and calendar surface for the client chosen in D02 T01 §2: module ribbons, navigation bar, folder pane, message list, reading pane, compose window, calendar views, People, Tasks, search, panes and dialogs.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write the Outlook chapter of `design/SPEC.md` citing `outlook.*` ids. Done when: every module, view and dialog id is cited.

- [ ] Specify each module ribbon and item window ribbon as tables of groups with control ids. Done when: the report shows 100 percent of Outlook `tab` records cited. Cheaper substitute: the Mail Home tab only.
- [ ] Specify the Mail layout: navigation bar, folder pane, message list rows (single and compact), conversation threading, reading pane positions, unread and flagged states. Done when: each element has tokens and sizes. Cheaper substitute: a two-column list and preview.
- [ ] Specify the compose and read windows, including inline replies in the reading pane. Done when: both cite their ids. Cheaper substitute: compose as a modal dialog only.
- [ ] Specify calendar, People and Tasks views and every Outlook dialog. Done when: view and dialog citations reach 100 percent. Cheaper substitute: Month view only.
- [ ] Specify the modernised Outlook surface under `### Modernisation` in its chapter of `design/SPEC.md`: every inventoried tab, group and command keeps its place, drawn with the Word, Excel and PowerPoint shell (title bar with search, Fluent glyphs, rounded controls, Mica, light and dark themes, the Simplified Ribbon option, Backstage, task panes, dialogs and status bar), and a table lists each layout change from the classic app (for example the navigation bar, folder pane, message list density, reading pane and compose window) with the Word, Excel or PowerPoint pattern it follows and the inventory ids it moves. Done when: the table has a row per changed region and `python scripts/inventory-report.py --cited-in design/SPEC.md --app outlook` still reports 100 percent. Cheaper substitute: copying the classic app's dated layout, or redesigning beyond patterns Word, Excel and PowerPoint already use. Owner request 2026-10-22 (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 5).
- [ ] Commit: `spec: add Outlook surface chapter`

**Test checkpoint:** `python scripts/inventory-report.py --cited-in design/SPEC.md --app outlook` reports 100 percent of `tab`, `view` and `dialog` records cited.

## 13. Accessibility Chapter

Parity includes keyboard and assistive technology: KeyTips, F6 region cycling, shortcuts from D02 T01 §17, screen reader names and roles, focus order, high contrast and text scaling, meeting WCAG 2.2 AA.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Write the Accessibility chapter of `design/SPEC.md`. Done when: every rule in the micro-steps is specified with its test method.

- [ ] Specify focus order and F6 region cycling across title bar, ribbon, document, panes and status bar in the Accessibility chapter. Done when: the cycle order is listed per app. Cheaper substitute: browser default tab order.
- [ ] Specify accessible names and roles for each ribbon control type, mapped to UIA control types and ARIA roles. Done when: every `controlType` has a role mapping. Cheaper substitute: labels only.
- [ ] Specify the shortcut system: binding table source (`design/inventory/<app>/shortcuts.json`), scope rules, conflict resolution and user remapping. Done when: the rules cite the inventory files. Cheaper substitute: hardcoded shortcuts per handler.
- [ ] Specify high contrast and text scaling behaviour at 100, 150 and 200 percent. Done when: ribbon reflow at 200 percent is defined by the §4 scaling rules. Cheaper substitute: clipping at large scales.
- [ ] Commit: `spec: add accessibility and keyboard chapter`

**Test checkpoint:** `python scripts/check-design-doc.py design/SPEC.md --require Accessibility --require "F6" --require "High contrast"` exits 0.

## 14. Mockups and Sign-Off

A static mockup per app, built from the tokens, glyph set and chapters, lets the owner judge "same place, different look" before code exists. Mockups contain no Microsoft artwork. **Groomed 2026-10-23:** the pinned independent reviewer signs off each mockup and the owner audits later (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 3); the `owner-decision` Need is removed.

**Phase:** 2
**Needs:** none
**Surface:** no

**Build order:**

1. Draw `design/mockups/<app-id>.svg` for each app at 1920 by 1080. Done when: six mockups pass the image-asset checker.
2. Record the reviewer's sign-off per app in `design/SPEC.md` under `## Sign-off`. Done when: six dated rows exist. **Corrected 2026-10-23:** was the owner's sign-off.

- [ ] Draw the word-processor mockup in `design/mockups/<writer-id>.svg` with the Home tab, a page and the status bar. Done when: region sizes match the Shell chapter within 1 pixel. Cheaper substitute: a traced screenshot of Word.
- [ ] Draw the spreadsheet, presentation, diagram, project and mail mockups in `design/mockups/`. Done when: five more SVGs exist at 1920x1080. Cheaper substitute: one mockup with swapped titles.
- [ ] Overlay each mockup on its Microsoft reference capture in `R:\scratch\mockup-overlay\` and record region offsets in `design/SPEC.md` under `## Mockup review`. Done when: every region the `### Modernisation` tables leave unchanged is within 2 pixels of the capture, and every region they change matches its row's specified position and size within 2 pixels. Cheaper substitute: committing the overlay with Microsoft pixels in it, or holding a modernised region to the classic capture. **Corrected 2026-10-23:** held every region to the capture, which a modernised Outlook, Visio or Project region cannot meet.
- [ ] Record the independent reviewer's per-app sign-off in `design/SPEC.md` under `## Sign-off`: date, reviewer and model, verdict against the chapter (and, for Outlook, Visio and Project, against its `### Modernisation` table), and the review record path, with a line that the owner audits it later (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 3). Done when: six rows carry a date, reviewer, verdict and record. Cheaper substitute: one blanket approval, or the writer signing its own mockups. **Corrected 2026-10-23:** was the owner's sign-off.
- [ ] Commit: `spec: add app mockups and record sign-off`

**Test checkpoint:** `Get-ChildItem design/mockups/*.svg | ForEach-Object { python scripts/check-image-asset.py $_.FullName --format svg }` exits 0 for six files and `python scripts/check-design-doc.py design/SPEC.md --require Sign-off` exits 0.

## Verification

- `python scripts/check-design-doc.py design/SPEC.md` passes with every chapter heading named in this file.
- `python scripts/inventory-report.py --cited-in design/SPEC.md` reports 100 percent of `tab`, `contextualTab`, `view`, `pane` and `dialog` records cited.
- `design/SPEC.md` carries six dated sign-off rows.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
