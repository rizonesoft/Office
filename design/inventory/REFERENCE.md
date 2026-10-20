# Inventory Reference

What the parity inventory is measured against: one fixed build, one capture profile and the owner's layout choices. Positions only mean something against this configuration.

## Builds

Read 2026-10-20 on the operator's host (Windows 11 Pro, Venom-PC) from the Click-to-Run configuration and each program's file version, the values the Account page reports.

| App | Version | Build | Channel | Platform |
| --- | ------- | ----- | ------- | -------- |
| Word | 16.0 | 16.0.20430.20182 | Current Channel | x64 |
| Excel | 16.0 | 16.0.20430.20182 | Current Channel | x64 |
| PowerPoint | 16.0 | 16.0.20430.20182 | Current Channel | x64 |
| Visio | 16.0 | 16.0.20430.20182 | Current Channel | x64 |
| Project | 16.0 | 16.0.20430.20182 | Current Channel | x64 |
| Outlook (classic) | 16.0 | 16.0.20430.20182 | Current Channel | x64 |

The channel is the update channel id `492350f6-3a01-4f97-b9c0-c7c6ddf67d60`, which is Current Channel. Every record captured live carries this build in `capturedFrom`, and a capture from any other build is a new reference, recorded here first.

## Capture profile

Profile `fhd-100`: display 1920 by 1080 pixels at 100 percent scaling, window maximised, Office theme White, Office display language en-US, ribbon set to Always show Ribbon. `captureProfile` fields name this id, and `bounds` are pixels at this profile relative to the window client area.

Confirmed on the host on 2026-10-20, read by a DPI-aware process: the primary display is 3840 by 2160 at 150 percent (system DPI 144) and does not match; the second display is 1920 by 1080 at 100 percent (96 DPI) and matches, so captures run there; Office's display language is en-us; Word's ribbon is set to Always show Ribbon; the Office theme does not match: the capture window's title bar reads Word blue (RGB 24, 90, 189), so the theme is not White (the stored theme value is 7). **Corrected 2026-10-20:** earlier reads of a white title bar were taken while the session was locked, when the screen shows no real window; the tool now refuses to read the theme on a locked desktop. Until the owner decides between switching Office to White for captures and dropping the theme from the profile (it changes colours, not positions), captures record no bounds. Windows' regional format is en-ZA, which the profile does not constrain. **Corrected 2026-10-20:** an earlier read without DPI awareness gave the primary display as 2560 by 1440 and left the second display's scaling and the theme unconfirmed.

The capture tool (`scripts/capture-ui.py`, D02 T01 §3) places its own window on the matching display, maximises it, checks every profile value (display size and DPI, the window on that display and maximised, display language, ribbon shown, theme by the title bar's colour) and records `bounds` and `size` only when all of them hold.

## Layout choices

Decisions, 2026-10-20 (owner): both the Classic and the Simplified Ribbon are inventoried and built from the start, with the switch between them; the Outlook reference is classic Outlook, not the new Outlook for Windows.

What the reference build offers, read 2026-10-20:

- Word: the Ribbon Display Options menu at the right end of the ribbon offers Full-screen mode, Show tabs only, Always show Ribbon and Hide Quick Access Toolbar; that menu has no Classic or Simplified switch. Whether the switch exists elsewhere in Word is not yet known. The baseline lists a `SingleLineRibbonToggle` for Word outside the ribbon, so the Word capture (D02 T01 §5) records whether this build exposes it anywhere.
- Outlook (classic): the baseline lists `SingleLineRibbonToggle` in every item window. The Outlook capture (D02 T01 §15) records where it sits and the steps that switch it; Outlook is not started unattended, because starting it sends whatever waits in the Outbox.
- Excel, PowerPoint, Visio and Project: the baseline lists no ribbon layout toggle. Each app's capture section records whether the build offers one, as the Visio section already states.

Where a reference app has no Simplified Ribbon, the Simplified layout of our app has no capture to match; how it is derived is an owner question, recorded in the phase 2 run file.

## Licensing

Read on 2026-10-20 from the Click-to-Run product list and the two licence stores (subscription entries under `LicensingNext`, and the classic licensing service through `OSPP.VBS /dstatus`, printing licence names and states only).

| App | Product | Installed | Licence found |
| --- | ------- | --------- | ------------- |
| Word, Excel, PowerPoint, Outlook | Microsoft 365 Apps for business | yes | subscription entry |
| Project | Project Professional | yes | subscription entry |
| Visio | Visio Professional | yes | none in either store |

A subscription entry shows a licence was issued, not that it is valid today: the entries' state was not read, because the licence tokens hold credentials. Word is in daily use on this host with its full ribbon. Requirement for the capture tool (D02 T01 §3): refuse to capture an app that shows a licence, activation or reduced-functionality notice. Visio's licence is unverified, so its capture sections (D02 T01 §11 and §12) wait on the owner (`owner-decision`): confirm how Visio is licensed on this host (subscription, retail key or trial) before it is captured, since an unlicensed Visio may show a reduced interface. The owner said on 2026-10-20 that Visio and Project are both on this host.

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

To refresh: download the six apps' Current Channel workbooks at a new commit into `R:\scratch\office-ui-ids\<full commit>\`, run `python scripts/import-office-ids.py R:/scratch/office-ui-ids/<full commit>`, and update this table and `THIRD-PARTY-NOTICES.md`. `--check` reports whether the committed files match a downloaded commit.
