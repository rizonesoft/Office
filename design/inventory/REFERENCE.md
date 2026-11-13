# Inventory Reference

What the parity inventory is measured against: one fixed build, one capture profile and the owner's layout choices. Positions only mean something against this configuration.

## Builds

Read 2026-10-20 (`16.0.20430.20182`) and 2026-11-08 (`16.0.20527.20150`) on the operator's host (Windows 11 Pro, Venom-PC) from the Click-to-Run configuration and each program's file version, the values the Account page reports.

| App | Version | Build | Channel | Platform |
| --- | ------- | ----- | ------- | -------- |
| Word | 16.0 | 16.0.20527.20150 | Current Channel | x64 |
| Excel | 16.0 | 16.0.20527.20150 | Current Channel | x64 |
| PowerPoint | 16.0 | 16.0.20527.20150 | Current Channel | x64 |
| Visio | 16.0 | 16.0.20527.20150 | Current Channel | x64 |
| Project | 16.0 | 16.0.20527.20150 | Current Channel | x64 |
| Outlook (classic) | 16.0 | 16.0.20527.20150 | Current Channel | x64 |
| All six apps (2026-10-20) | 16.0 | 16.0.20430.20182 | Current Channel | x64 |

The channel is the update channel id `492350f6-3a01-4f97-b9c0-c7c6ddf67d60`, which is Current Channel. Every record captured live carries this build in `capturedFrom`, and a capture from any other build is a new reference, recorded here first.

## Capture profile

Profile `fhd-100`: display 1920 by 1080 pixels at 100 percent scaling, window maximised, Office display language en-US, ribbon set to Always show Ribbon. Decision, 2026-10-20 (owner): the Office theme is not part of the profile, since it changes colours and not positions or sizes; captures run under the host's theme (Colorful). `captureProfile` fields name this id, and `bounds` are pixels at this profile relative to the window client area.

Confirmed on the host on 2026-10-20, read by a DPI-aware process: the primary display is 3840 by 2160 at 150 percent (system DPI 144) and does not match; the second display is 1920 by 1080 at 100 percent (96 DPI) and matches, so captures run there; Office's display language is en-us; Word's ribbon is set to Always show Ribbon; the Office theme is Colorful (the capture window's title bar reads Word blue, RGB 24, 90, 189; the stored theme value is 7), which the profile no longer constrains. **Corrected 2026-10-20:** an earlier note read the theme as White from pixels sampled while the session was locked. Windows' regional format is en-ZA, which the profile does not constrain. **Corrected 2026-10-20:** an earlier read without DPI awareness gave the primary display as 2560 by 1440 and left the second display's scaling and the theme unconfirmed.

The capture tool (`scripts/capture-ui.py`, D02 T01 §3) places its own window on the matching display, maximises it, checks every profile value (display size and DPI, the window on that display and maximised, display language, ribbon shown) and records `bounds` and `size` only when all of them hold.

## Layout choices

Decisions, 2026-10-20 (owner): both the Classic and the Simplified Ribbon are inventoried and built from the start, with the switch between them; the Outlook reference is classic Outlook, not the new Outlook for Windows.

What the reference build offers, read 2026-10-20 and verified 2026-11-09 (`16.0.20527.20150`):

- Word: the Ribbon Display Options menu at the right end of the ribbon offers `Full-screen mode`, `Show tabs only`, `Always show Ribbon` and `Hide Quick Access Toolbar`; that menu has no Classic or Simplified switch. Verified on 2026-11-09 (`D02 T01 §5`) in Word build `16.0.20527.20150`: `SingleLineRibbonToggle` does not exist anywhere in the desktop Word UI Automation tree (`find(root, lambda e: e.automation_id == "SingleLineRibbonToggle")` returns `None`), on the Quick Access Toolbar or its `Customize Quick Access Toolbar` menu, on the ribbon or tab-row right-click context menu (`Customize the Ribbon...`, `Collapse the Ribbon`), or in `Word Options` (`General`, `Customize Ribbon` under `All Commands`, and `Quick Access Toolbar` under `All Commands`). Running `python scripts/capture-ui.py --app word --all-tabs --layout simplified` exits 2 with `this build offers no Simplified Ribbon switch (SingleLineRibbonToggle not found)`, so no `design/inventory/word/ribbon-simplified.json` is written.
- Outlook (classic): the baseline lists `SingleLineRibbonToggle` in every item window. The Outlook capture (D02 T01 §15) records where it sits and the steps that switch it; Outlook is not started unattended, because starting it sends whatever waits in the Outbox.
- Excel, PowerPoint, Visio and Project: the baseline lists no ribbon layout toggle. Each app's capture section records whether the build offers one, as the Visio section already states.

Where a reference app has no Simplified Ribbon, the Simplified layout of our app has no capture to match; how it is derived is an owner question, recorded in the phase 2 run file.

## Licensing

Read on 2026-10-20 from the Click-to-Run product list and the two licence stores (subscription entries under `LicensingNext`, and the classic licensing service through `OSPP.VBS /dstatus`, printing licence names and states only).

| App | Product | Installed | Licence found |
| --- | ------- | --------- | ------------- |
| Word, Excel, PowerPoint, Outlook | Microsoft 365 Apps for business | yes | subscription entry |
| Project | Project Professional | yes | subscription entry |
| Visio | Visio Professional | yes | subscription entry (registered 2026-10-20) |

A subscription entry shows a licence was issued, not that it is valid today: the entries' state was not read, because the licence tokens hold credentials. Word is in daily use on this host with its full ribbon. Requirement for the capture tool (D02 T01 §3): refuse to capture an app that shows a licence, activation or reduced-functionality notice. Visio had no licence in either store when first read on 2026-10-20; the owner then registered it, and the subscription store holds `visioproretail`. **Corrected 2026-10-20:** Visio's capture sections no longer wait on the owner.

## Baseline

The control identifier baseline is a complete checklist of every tab, group and control each app publishes, so a live capture can be proven complete rather than assumed complete.

| Field | Value |
| ----- | ----- |
| Upstream | OfficeDev `office-fluent-ui-command-identifiers` |
| Folder | `Microsoft 365/Current Channel` |
| Commit | `b230a0df45036b2d5e8b49ebf368b3f90ada8d63` |
| Committed | 2024-03-18 |
| Licence | MIT (notice in `THIRD-PARTY-NOTICES.md`) |
| Imported | 2026-10-20, by `scripts/import-office-ids.py` |
| Files | `design/inventory/<app>/baseline.json` for the six apps |

`design/inventory/baseline-sources.json` holds the git blob id of every upstream workbook at the commit; the importer refuses any input that is missing, extra or not byte-identical to upstream, and `check-inventory.py` over the whole inventory requires all six baselines and every Outlook window it lists. Each baseline file records `baseline:<commit>` as its source, the columns, and one row per workbook row in workbook order, so a row's position is its order. Outlook's item-window workbooks merge into one file whose first column is the window, named as the workbook names it: `explorer`, `mailitem` (compose), `mailread`, `apptitem` (appointment), `addritem` (contact), `taskitem`, `dlstitem` (contact group), `logitem` (journal), `postitem`, `postread`, `reportitem`, `reqread`, `reqsend`, `resenditem`, `respcounter`, `responseread`, `responsesend`, `rssitem`, `shareitem`, `smsedit`, `smsread`, `mmsedit` and `mmsread`.

Rows with a null `idMso` are controls the workbooks list without an identifier; they keep their policy id and position. Anything newer than 2024-03-18 in the live build is found by the live capture and recorded on the inventory record as `baselineMissing`.

To refresh: download the six apps' Current Channel workbooks at a new commit into `R:\scratch\office-ui-ids\<full commit>\`, read the upstream commit's blob entries (`git ls-tree -r <full commit> -- "Microsoft 365/Current Channel"` from the root of a clone of `OfficeDev/office-fluent-ui-command-identifiers`) and verify each downloaded workbook's git blob id (`git hash-object <file>`), update `design/inventory/baseline-sources.json` with the new `commit` and `blobs` map before importing, run `python scripts/import-office-ids.py R:/scratch/office-ui-ids/<full commit>`, and update this table and `THIRD-PARTY-NOTICES.md`. `--check` reports whether the committed files match a downloaded commit.

## Word ribbon reconciliation

Verified on 2026-11-09 (`D02 T01 §5`) against Word `16.0.20527.20150` (`fhd-100`) and `design/inventory/word/baseline.json` (which contains 20 `coreTab` rows and 23 `contextualTab` rows):

- **Captured built-in `tab` records (11 of 20 `coreTab` rows)**: `TabHome` (`Home`), `TabInsert` (`Insert`), `TabDrawInk` (`Draw`), `TabWordDesign` (`Design`), `TabPageLayoutWord` (`Layout`), `TabReferences` (`References`), `TabMailings` (`Mailings`), `TabReviewWord` (`Review`), `TabView` (`View`), `TabDeveloper` (`Developer`) and `HelpTab` (`Help`). `File` (`FileTabButton`) is the shell tab-row Backstage button captured in `design/inventory/shell/chrome.json` (`shell.tabrow.file`, `D02 T01 §4`) and its `placement == "backstage"` pages in `design/inventory/word/backstage.json` (`D02 T01 §6`).
- **Captured `contextualTab` records (16 total: 13 of 23 `contextualTab` rows plus 3 mode-triggered `coreTab` rows)**:
  - Ten core object contextual tabs: `TabTableToolsDesign` (`Table Design`), `TabTableToolsLayout` (`Table Layout`), `TabPictureToolsFormat` (`Picture Format`), `TabDrawingToolsFormat` (`Shape Format`), `TabHeaderAndFooterToolsDesign` (`Header & Footer`), `TabEquationToolsDesign` (`Equation`), `TabChartToolsDesignNew` (`Chart Design`), `TabChartToolsFormatNew` (`Format` under `Chart Tools`), `TabSmartArtToolsDesign` (`SmartArt Design`) and `TabSmartArtToolsFormat` (`Format` under `SmartArt Tools`).
  - Two additional object contextual tabs: `TabGraphicsToolsFormat` (`Graphics Format` under `Graphics Tools`, triggered by selecting an inline SVG graphic `wdInlineShapeGraphic` type 17) and `Tab3DModelToolsFormat` (`3D Model` under `3D Model Tools`, triggered by selecting an inline 3D model `wdInlineShape3DModel` type 19).
  - Four mode-triggered tabs: `TabOutlining` (`Outlining`, `coreTab` in baseline, triggered by Outline view `View.Type = 2`), `TabPrintPreview` (`Print Preview`, `coreTab` in baseline, triggered by Print Preview edit mode `View.Type = 4`), `TabBackgroundRemoval` (`Background Removal`, `coreTab` in baseline, triggered by invoking `PictureBackgroundRemoval` on a selected picture) and `TabLearningTools` (`Immersive Reader`, `contextualTab` in baseline under `Immersive`, triggered by invoking `ToggleLearningTools` on `View`).
- **Reconciled absent baseline tab rows (16 total: 6 `coreTab` rows and 10 `contextualTab` rows)**:
  - Six environment- or mode-gated `coreTab` rows not shown in a normal `.docx` session: `TabAddIns` (legacy CommandBar add-in container tab; hidden when no legacy add-in registers custom CommandBar controls), `TabSyntex` (SharePoint Syntex enterprise content assembly tab; requires a Microsoft Syntex tenant service license and active Syntex template), `TabBlogPost` and `TabBlogInsert` (legacy Weblog post editing and insert tabs; only loaded when Word starts in the deprecated Blog Post template mode), `TabConflicts` (co-authoring server merge conflict resolution mode tab; only shown during an active SharePoint/OneDrive sync conflict) and `TabBroadcastPresentation` (retired Office Presentation Service broadcast mode tab).
  - Ten superseded legacy `.doc` (Word 97-2003 compatibility mode) and Tablet PC `contextualTab` rows replaced in `.docx` documents: `TabChartToolsDesign`, `TabChartToolsLayout` and `TabChartToolsFormat` (legacy Office 2007-2010 chart contextual tabs superseded by `TabChartToolsDesignNew` and `TabChartToolsFormatNew`), `TabDrawingToolsFormatClassic` (legacy VML drawing/AutoShape tab superseded by DrawingML `TabDrawingToolsFormat`), `TabPictureToolsFormatClassic` (legacy VML picture tab superseded by DrawingML `TabPictureToolsFormat`), `TabTextBoxToolsFormat` (legacy VML text box tab superseded by DrawingML `TabDrawingToolsFormat`), `TabWordArtToolsFormat` (legacy VML WordArt tab superseded by DrawingML `TabDrawingToolsFormat`), `TabDiagramToolsFormatClassic` and `TabOrganizationChartToolsFormat` (legacy Office 2003 diagram and organization chart tabs superseded by SmartArt `TabSmartArtToolsDesign` and `TabSmartArtToolsFormat`) and `TabInkToolsPens` (legacy contextual Ink Tools Pens tab superseded by the always-available `Draw` `TabDrawInk` tab).
- **Unverified-group and add-in reconciliation**:
  - Confirmed newer built-in Word groups lacking 2024 baseline `idMso`s are included in `design/inventory/word/ribbon.json` with `baselineMissing: true`: `word.draw.drawing-tools` (`Drawing Tools` on `Draw` `TabDrawInk`, containing the `Drawing Tools` pen-slot list and `Add` menu with `Pen`, `Highlighter`, `Fountain Pen`, `Brush Pen`, `Pencil` and `Text Pen`) and `word.review.onenote` (`OneNote` on `Review` `TabReviewWord`, containing `Linked Notes`).
  - Third-party COM add-in tabs and their groups remain excluded from `design/inventory/word/ribbon.json` and recorded in `build/capture-ui/word-unverified.json`: `word.acrobat` (`Acrobat` tab), `word.home.adobe-acrobat` (`Adobe Acrobat` group on `Home`) and `word.mailings.acrobat` (`Acrobat` group on `Mailings`), all registered by the host's Adobe Acrobat PDFMaker Office COM Addin.
- **KeyTip and expansion reconciliation**:
  - In Word `16.0.20527.20150`, UI Automation exposes `CurrentAccessKey` with either a comma-separated sequence (`"Alt, H, F, F"`) or an `ALT+` prefix (`"Alt, JB, ALT+E"` on `Header & Footer` controls); `keytip()` normalises both forms to uppercase alphanumeric badge sequences (`"FF"`, `"E"`).
  - Controls that genuinely expose an empty `CurrentAccessKey` in Word `16.0.20527.20150` omit `keytip`: the in-ribbon `List` and style galleries (`QuickStylesGallery`, `QuickStylesSets`, `TableStylesGalleryWord`, `PictureStylesGallery`, `ShapesInsertGallery`, `ShapeStylesGallery`, `TextStylesGallery`, `EquationSymbolsInsertGallery`, `ChartStylesGallery`, `SmartArtLayoutGallery`, `SmartArtStylesGallery`, `GraphicsStylesGallery`, `Gallery3DModelViewPresets`) and the paired `More` / `Less` increment sub-buttons inside numeric spinners on `Layout`, `Table Layout`, `Picture Format`, `Shape Format`, `Header & Footer`, `Format` (`Chart Tools`), `Format` (`SmartArt Tools`), `Graphics Format` and `3D Model`.
  - Menu items that genuinely expose an empty `CurrentAccessKey` in Word `16.0.20527.20150` omit `keytip`: `galleryItem` (`ListItem`) entries inside opened galleries (which are navigated by arrow keys rather than individual KeyTips), `Gallery Filter` category filter items (`All`, `Basic Math`), list-level and effect submenus without individual KeyTips (`Change List Level`, `Microsoft Office Signature Line...`, `Show Source Documents`, `3:4`, `4:5`, `5:4`, `Arrows`, `Shadow`, `Reflection`, `Glow`, `Bevel`, `3-D Rotation`, `Transform`, `Lines`, `Up/Down Bars`), `No Online Content Available` placeholder items under `More ... from Office.com`, and dynamic recipient column items under `word.mailings.write-insert-fields.insert-merge-field` (`FirstName`, `LastName`, `Title`, `City`).
  - State-dependent expandable controls whose expansion is genuinely unavailable on a local host or on the outer chart frame are recorded as `control` records with their enablement precondition documented in `behaviour` (6 total across the entire inventory): on built-in tabs, `word.home.sensitivity.sensitivity` (`ClassifyLabelProtect`, requires a Microsoft Purview / AIP tenant sensitivity-label policy), `word.review.comments.show-comments` (`ShowCommentsMenu`, whose split dropdown requires modern comment view switching), `word.review.protect.block-authors` and `word.developer.protect.block-authors` (`BlockAuthorsMenu`, requires an active SharePoint/OneDrive co-authoring session), plus `word.draw.drawing-tools.drawing-tools` (the in-ribbon pen-slot `List` surface paired with `word.draw.drawing-tools.add`); on contextual tabs, `Bring Forward` (`ObjectBringForwardMenu`), `Send Backward` (`ObjectSendBackwardMenu`), `Group` (`ObjectsGroupMenu`), `Rotate` (`ObjectRotateGallery`) and `Layout` (`SmartArtOrganizationChartMenu` on `SmartArt Design`) are all expanded across `Picture Format`, `Shape Format`, `SmartArt Design`, `Format` (`SmartArt Tools`), `Format` (`Chart Tools`), `Graphics Format` and `3D Model` by preparing floating wrapping, multi-object selections and an `Organization Chart` hierarchy node selection in `word-contextual.docx`, leaving only `word.format.insert-shapes.change-shape` (`ShapeChangeShapeGallery` on `TabChartToolsFormatNew`, which is disabled whenever the chart container or chart element is selected because selecting an inner drawing shape switches Word's active contextual tab from `TabChartToolsFormatNew` to `TabDrawingToolsFormat`).

## Word Backstage absences

Verified on 2026-11-13 (`D02 T01 §6`) against Word `16.0.20527.20150` (`fhd-100`) on a new blank document the capture opened itself, signed into a Microsoft 365 business account. `design/inventory/word/baseline.json` holds 318 `placement` `backstage` rows; `design/inventory/word/backstage.json` captures nine of its ten pages, every navigation action (`Close` and `Options` recorded and never pressed; `Save`, which on the capture's never-saved document only shows the Save As page, pressed after Word confirms the document has no path and recorded as that page, and on a saved document recorded as an action and never pressed) and each page's controls with their menus and dropdowns opened one level, and the panels of Share's and Export's tasks. `ABSENT` in `scripts/lib/word_backstage.py` lists each baseline id the capture does not show, with one of these reasons, which `scripts/check-inventory.py` requires to be documented here:

- `document-state`: Word shows the group or command only for a document in another state: read-only, in Protected View, checked out, on a server or cached offline, in an older format to convert, signed, under a policy, a workflow or a broadcast, with upload errors, an available update or a disabled add-in. A blank new document is in none of them. Capturing them needs a document fixture in each state, owned by the app domain's sections that implement these states.
- `account-state`: Word shows it only for another account or update state: signed out, sign-in disabled by policy, enrolled in Office Insider, on a selectable update channel, or with recommendations on Home.
- `layout-variant`: a container for another arrangement of the Open and Save As places (the getting-started, pinnable, cloud and local, loading and upsell layouts). This account's layout shows its places in the groups captured.
- `not-offered`: a task this installation does not offer to this account: blog posts, instant messages, workflows, and the Feedback page, which this build's navigation does not list.
- `not-exposed`: a grouping UI Automation does not expose as an element of its own (the category headings of Open, Save As, Share and Export, and the container of the Email task's choices, whose choices are captured).

Not recorded at all, by rule rather than absence: the shell's `Back` entry (`shell.backstage.back`, D02 T01 §4); the Adobe Acrobat entries (`Save as Adobe PDF`, `Share as Adobe PDF link`, `Create Adobe PDF`, the `Adobe PDF` printer), which are an add-in's; and the owner's data: the entries of recent-file, template, place and folder lists, pinned or visited SharePoint sites, people's names, dates, printers and document property values. An e-mail address in a label is recorded as `the signed-in account`, and a storage service named with the account's organisation as the service alone.
