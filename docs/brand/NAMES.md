# Names

The single record of the suite's and the apps' names. Every other file takes names from here. The owner chose them on 2026-10-20 (D01 T01 §3); the alternatives and the collision screen are in [naming-candidates.md](./naming-candidates.md), the rules in [naming-brief.md](./naming-brief.md).

## Suite

**Rizonesoft Office**, the suite's name everywhere. "Office" never stands alone and never carries a version year. The house brand Rizonesoft carries the trademark protection, because the app words and "Office" are generic words.

## Apps

Each app's full name is "Rizonesoft <App>", used everywhere outside the app; inside the app, the bare word is its label. No app swaps were made.

| App | Full name | Microsoft counterpart |
| --- | --- | --- |
| Write | Rizonesoft Write | Word |
| Grid | Rizonesoft Grid | Excel |
| Stage | Rizonesoft Stage | PowerPoint |
| Flow | Rizonesoft Flow | Visio |
| Plan | Rizonesoft Plan | Project |
| Mail | Rizonesoft Mail | Outlook |

## Identifiers

The bundle ids sit under the owner's domain, rizonesoft.com, reversed.

| Display name | kebab-case | PascalCase | Bundle id |
| --- | --- | --- | --- |
| Rizonesoft Office | `rizonesoft-office` | `RizonesoftOffice` | `com.rizonesoft.office` |
| Rizonesoft Write | `rizonesoft-write` | `RizonesoftWrite` | `com.rizonesoft.write` |
| Rizonesoft Grid | `rizonesoft-grid` | `RizonesoftGrid` | `com.rizonesoft.grid` |
| Rizonesoft Stage | `rizonesoft-stage` | `RizonesoftStage` | `com.rizonesoft.stage` |
| Rizonesoft Flow | `rizonesoft-flow` | `RizonesoftFlow` | `com.rizonesoft.flow` |
| Rizonesoft Plan | `rizonesoft-plan` | `RizonesoftPlan` | `com.rizonesoft.plan` |
| Rizonesoft Mail | `rizonesoft-mail` | `RizonesoftMail` | `com.rizonesoft.mail` |

## File formats

Where Microsoft's app saves an open, standardised format, the app keeps it as its default: no proprietary format replaces OOXML. Where the counterpart's own format is closed, the app saves its own native format under its own extension, and reads and writes Microsoft's format for exchange. The read and write scope of every format is decided in D03 T01 §5.

| App | Default save format | Exchange formats |
| --- | --- | --- |
| Write | `.docx` (OOXML) | `.doc`, `.rtf`, `.odt`, PDF export |
| Grid | `.xlsx` (OOXML) | `.xls`, `.csv`, `.ods`, PDF export |
| Stage | `.pptx` (OOXML) | `.ppt`, `.odp`, PDF export |
| Flow | `.vsdx` (OOXML) | `.vsd`, SVG and PDF export |
| Plan | Its own native format; extension named in D03 T01 §5 | `.mpp`, Project XML (`.xml`) |
| Mail | `.eml` (RFC 5322) for a saved message | `.msg`, `.pst`, `.ics` |

Plan takes its own format because Project's `.mpp` is closed, as the open-source planners do beside Project: ProjectLibre saves `.pod` (https://www.nationalarchives.gov.uk/PRONOM/fmt/522) and GanttProject an XML `.gan` file (https://help.ganttproject.biz/t/export-to-project-libre/235/4), both exchanging through Project XML.
