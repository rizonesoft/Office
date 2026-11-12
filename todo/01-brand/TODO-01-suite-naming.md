---
schema_version: 1
id: suite-naming
domain: 01-brand
status: active
title: "TODO-01 -- Suite and App Naming"
---

# TODO-01 -- Suite and App Naming

> **Goal:** The suite and its six apps (the counterparts of Word, Excel, PowerPoint, Visio, Project and Outlook) have names that use no Microsoft trademark (the generic word "Office" appears only behind the Rizonesoft house brand, as competitors do with WPS Office, SoftMaker Office and ONLYOFFICE), pass a knockout trademark screen in Nice classes 9 and 42, have their domain, GitHub and package names reserved or confirmed available, are recorded once in `docs/brand/NAMES.md`, and are applied across the repository.

> **Current state:** Measured 2026-10-19. No brand documents exist (`docs/brand/` is absent). The repository is `rizonesoft/Office`, a working codename; the year form mirrors Microsoft's own version names (Office 2021, Office 2024) and is not used for the product. A brainstorm was held on 2026-10-19 and the owner decided on 2026-10-20: suite "Rizonesoft Office", apps "Rizonesoft Write", "Rizonesoft Grid", "Rizonesoft Stage", "Rizonesoft Flow", "Rizonesoft Plan" and "Rizonesoft Mail" (§3).

## Inputs

- Microsoft's published Trademark and Brand Guidelines (read, not linked: the repository holds no Microsoft links) (Word, Excel, PowerPoint, Visio, Outlook, Microsoft 365, Microsoft Office and Office 365 are registered marks and are excluded; "Office" is used only inside "Rizonesoft Office", never alone, never with a Microsoft-style version year, and never with Microsoft's logo styling).
- USPTO trademark search https://tmsearch.uspto.gov, EUIPO eSearch plus, and WIPO Global Brand Database: the registers a knockout screen would search (not pursued: owner, 2026-10-22; the section was removed on 2026-11-13).
- Nice classes 9 (downloadable software) and 42 (software as a service): the classes every candidate is screened in.
- -> XREF: D00 T01 §1 -- `scripts/check-design-doc.py` verifies every document this file writes
- -> XREF: D01 T02 §1 -- the icon language takes the chosen names and the suite motif
- -> XREF: D01 T03 §4 -- the README brand section displays the recorded names

## Outcome

- `docs/brand/NAMES.md` records the suite name, the six app names, the Microsoft app each one maps to, the file-name and identifier forms (`kebab-case`, `PascalCase`, reverse-DNS bundle id), and the date the owner chose them.
- `docs/brand/naming-clearance.md` records, per chosen name, the register searches run, live conflicts found, and domain, GitHub and package availability with dates.
- No product-facing file in the repository uses "Word", "Excel", "PowerPoint", "Visio", "Project" or "Outlook" as a product name, or "Office" other than in "Rizonesoft Office".

**Adjacency:** all=not-applicable (a brand decision record; it creates no user records, settings, documents or permissions)

**Adjacency rationale:** Naming produces documents for contributors and the owner only. The product's own document, settings and exchange surfaces are owned by the application domains authored from D03 T01 §13.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Naming brief and constraints | D00 T01 §1 | [x] |
| 2 | §2 | Collision screen for the chosen names | §1 | [x] |
| 3 | §3 | Owner selection of suite and app names | §2 | [x] |
| 4 | §5 | Domain, GitHub and package availability | §3 | [x] |
| 5 | §6 | Apply names across the repository | §5 | [x] |
| 6 | §9 | Microsoft Store name reservation | §3 | [ ] |

## 1. Naming Brief and Constraints

> **Started:** 2026-10-21T23:55:00Z

The brief fixes what a good name must do before anyone argues about taste. It states the exclusions (every Microsoft mark, names of direct competitors and their apps: LibreOffice Writer, Calc, Impress, Draw; OnlyOffice; WPS Office; Google Docs, Sheets, Slides; Apple Pages, Numbers, Keynote; Zoho Writer, Sheet, Show; SoftMaker TextMaker, PlanMaker; Calligra Words, Sheets, Stage, Plan), the structure options (house brand plus descriptive app names, or six standalone names), and the scoring criteria.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/brand/naming-brief.md` with Purpose, Exclusions, Structure options, Criteria and Scoring headings. Done when: `python scripts/check-design-doc.py docs/brand/naming-brief.md --require Exclusions --require Criteria` exits 0.

- [x] Write the Exclusions list in `docs/brand/naming-brief.md` citing Microsoft's Trademark and Brand Guidelines by name (Inputs). **Corrected 2026-10-22:** said citing the list's URL, which the Inputs' no-Microsoft-links rule forbids. Done when: every Microsoft app named in the Goal and every competitor app named in this section appears in the list. Cheaper substitute: "avoid Microsoft names" with no enumerated list.
- [x] Write the Structure options in `docs/brand/naming-brief.md`: house brand plus descriptive app names versus standalone app names, each with its clearance cost. Done when: both options carry one advantage and one cost. Cheaper substitute: presenting only the option already preferred.
- [x] Write the Criteria in `docs/brand/naming-brief.md`: pronounceable in English, at most 3 syllables per app name, no negative meaning in the 10 most spoken languages, available `.com` or `.app` for the suite, icon motif potential. Done when: each criterion is a yes or no test. Cheaper substitute: subjective adjectives such as "modern" or "catchy".
- [x] Write the Scoring rubric in `docs/brand/naming-brief.md` as a table with weights summing to 100. Done when: the weights sum to 100 and every row is at most 100 characters. Cheaper substitute: unweighted gut ranking.
- [x] Commit: `brand: add naming brief`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/naming-brief.md --require Exclusions --require "Structure options" --require Criteria --require Scoring` exits 0.

> **Verified:** 2026-10-22 | §1 | 559951e458dc31e5f2000e062a5a312e92cdcfa8
> **Review:** `docs/reviews/d01-t01-s1.json`

## 2. Collision Screen for the Chosen Names

> **Started:** 2026-10-22T00:25:00Z

The owner chose on 2026-10-20, ahead of a longlist: the suite is Rizonesoft Office and the apps are Write, Grid, Stage, Flow, Plan and Mail, known in full as "Rizonesoft Write" and so on (the same model as "Microsoft Word"). Rizonetech and Tesserac were considered the same day and dropped. This section records the brainstorm concepts as alternatives considered and runs an obvious-collision web search on the chosen names before the register searches in §4. Seed concepts from the 2026-10-19 brainstorm, kept as alternatives:

- Tessera (mosaic tile; every icon is one tile of a shared mosaic): Tessera Write, Tessera Grid, Tessera Stage, Tessera Flow, Tessera Plan, Tessera Mail. Known: Tessera Technologies (semiconductor IP, now Adeia), Tessera Therapeutics.
- Rizone (house brand of the `rizonesoft` organisation): Rizone Write, Rizone Grid, Rizone Stage, Rizone Flow, Rizone Plan, Rizone Mail. Known: none from memory; the owner already holds the Rizonesoft brand.
- Kestrel (bird motif; icons as feather and wing forms): Kestrel Write, Kestrel Grid, Kestrel Show, Kestrel Draw, Kestrel Plan, Kestrel Mail. Known: Kestrel weather meters (Nielsen-Kellerman).
- Atelier (six standalone names, like Apple's Pages, Numbers, Keynote): Inkwell, Abacus, Lectern, Blueprint, Milestone, Courier. Known: each of the six needs its own clearance; Abacus and Blueprint are crowded software names.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/brand/naming-candidates.md` with the chosen names and the alternatives considered. Done when: the file has `## Chosen`, `## Alternatives considered` and `## Collisions` headings.
2. Run the collision web search on each chosen name. Done when: every chosen name has a Collisions row with sources and the search date.

- [x] Record the chosen names in `docs/brand/naming-candidates.md` under `## Chosen`: Rizonesoft Office, and Write, Grid, Stage, Flow, Plan, Mail with their full "Rizonesoft <App>" forms. Done when: seven names appear with their Microsoft counterparts. Cheaper substitute: recording the app names without the house brand.
- [x] Copy the four seed concepts from this section into `docs/brand/naming-candidates.md` under `## Alternatives considered`, with the reason each was not chosen. Done when: Tessera, Rizone, Kestrel, Atelier, Rizonetech and Tesserac (one letter from the Tesseract OCR engine; search engines autocorrect it) each carry a reason. Cheaper substitute: dropping the alternatives, which loses the fallback list if a chosen name is blocked.
- [x] Web-search "Rizonesoft" and record other companies, products and domains using it in `docs/brand/naming-candidates.md` under `## Collisions`. Done when: the row names sources or `none found` with the search date. Cheaper substitute: assuming the owner's own brand is clear everywhere.
- [x] Record precedent for "<house brand> Office" suite names (WPS Office, SoftMaker Office, ONLYOFFICE, Polaris Office, LibreOffice) with their register entries under `## Collisions`. Done when: at least three precedents name a register record or source URL. Cheaper substitute: assuming "Office" is free to use without precedent.
- [x] Web-search each app name as a software product (for example "Grid spreadsheet", "Flow diagram app", "Stage presentation app") and record prominent conflicts, including Microsoft Flow (renamed Power Automate in 2019) and Microsoft Planner. Done when: six rows each name sources or `none found` with the date. Cheaper substitute: relying on memory, as the seeds in this section did.
- [x] Commit: `brand: record chosen names and collision screen`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/naming-candidates.md --require Chosen --require "Alternatives considered" --require Collisions --require "Rizonesoft Office"` exits 0.

> **Verified:** 2026-10-22 | §2 | c2f121ad413b05ba56a296a4b16be56c062edd03
> **Review:** `docs/reviews/d01-t01-s2.json`

## 3. Owner Selection of Suite and App Names

> **Started:** 2026-10-22T00:55:00Z

The owner picks the concept, can swap individual app names, and the choice is recorded once in `docs/brand/NAMES.md`. Every other file reads names from there. Remove the `owner-decision` Need when the choice is recorded in this section as `Decision: <concept>, <date>`.

Decision: Rizonesoft Office, 2026-10-20. House brand Rizonesoft; suite "Rizonesoft Office"; apps Write (Word), Grid (Excel), Stage (PowerPoint), Flow (Visio), Plan (Project) and Mail (Outlook); in-app names are the bare app names and full names are "Rizonesoft Write" and so on. The house brand carries the trademark protection, because the bare app names and "Office" are generic words and "Flow" was Microsoft's product name until 2019.

> **Deferred:** the name of Plan's native file extension (Plan saves its own format, as Project's `.mpp` is closed) -> XREF: D03 T01 §5

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Confirm the decision line in this section matches `## Chosen` in `docs/brand/naming-candidates.md`. Done when: both name the same suite and six apps.
2. Write `docs/brand/NAMES.md`. Done when: the design-doc checker passes with the required headings.

- [x] Record the owner's chosen concept and any per-app swaps in `docs/brand/NAMES.md` under `## Suite` and `## Apps`. Done when: six app rows each name the Microsoft counterpart. Cheaper substitute: recording only the suite name and leaving app names implied.
- [x] Add the identifier forms to `docs/brand/NAMES.md` under `## Identifiers`: display name, `kebab-case`, `PascalCase`, and reverse-DNS bundle id under the owner's domain. Done when: all four forms exist for the suite and each app. Cheaper substitute: deriving identifiers ad hoc in each later file.
- [x] Add the file extension policy to `docs/brand/NAMES.md` under `## File formats`: the documented XML formats (OOXML `.docx`, `.xlsx`, `.pptx`, and Visio's `.vsdx`) are kept, and any native project format gets its own extension. **Corrected 2026-10-22:** called `.vsdx` OOXML; it shares OOXML's packaging but its schema is Visio's, outside ECMA-376. Done when: each app lists its default save format (Plan's as its own native format, the extension's name owned by D03 T01 §5, which decides the `.mpp` scope). Cheaper substitute: inventing proprietary formats for apps whose OOXML format is standard.
- [x] Commit: `brand: record chosen suite and app names`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/NAMES.md --require Suite --require Apps --require Identifiers --require "File formats"` exits 0.

> **Verified:** 2026-10-22 | §3 | 831b35c0536a55845ef4bd1092b854f437fe244c
> **Review:** `docs/reviews/d01-t01-s3.json`

## 5. Domain, GitHub and Package Availability

> **Started:** 2026-10-22T01:30:00Z

The product needs a home domain, a GitHub repository or organisation name, and package identifiers (winget, Microsoft Store, Homebrew cask, Flathub, npm scope if the stack uses one). This section checks and records availability; buying anything is the owner's call.

> **Deferred:** the Microsoft Store name check, which only Partner Center under the owner's account can make -> XREF: D01 T01 §9

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Check availability for each identifier and record it in `docs/brand/naming-clearance.md` under `## Availability`. Done when: every identifier row records what its registry showed with the date (owned, registered or taken, or no record), and the file says a name with no record is claimable only once the owner reserves it. **Corrected 2026-10-22:** asked for `available`, which no lookup can establish: registries reserve and premium-price names they hold no record of.

- [x] Check `.com`, `.app` and `.dev` availability for the suite name by RDAP and record it in `docs/brand/naming-clearance.md`. Done when: three rows exist with dates. **Corrected 2026-10-22:** said `whois`, which Windows does not ship; RDAP is the registries' successor protocol and answers per domain. Cheaper substitute: a registrar search page that hides premium pricing.
- [x] Check the GitHub organisation and repository names with `gh api users/<name>` and record the result. Done when: the row shows the HTTP status. Cheaper substitute: assuming availability because the name is unusual.
- [x] Check winget (`winget search`), Homebrew (`brew search` or formulae.brew.sh) and Flathub for each app identifier and record results. Done when: each app has a row per registry. Cheaper substitute: checking the suite name only.
- [x] Commit: `brand: record name availability`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/naming-clearance.md --require Availability` exits 0.

> **Verified:** 2026-10-22 | §5 | caa3ef4c79635d1add15ab7de7e118c3c65904b4
> **Review:** `docs/reviews/d01-t01-s5.json`

## 6. Apply Names Across the Repository

> **Started:** 2026-10-22T12:20:00Z

Once names are clear, contributor-facing documents stop calling the product "Office 2028". The repository folder and remote keep their codename until §8.

**Corrected 2026-10-22:** the owner dropped the trademark screen (§4) and the repository rename (§8), so this section waits only on §5, and the repository stays `rizonesoft/Office` for good rather than until §8.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Update `AGENTS.md` and create `README.md` with the product name from `docs/brand/NAMES.md`. Done when: `rg -n "Office 2028" README.md AGENTS.md` returns only the codename note.

- [x] Replace the first paragraph placeholder in `AGENTS.md` with what the project is, using the suite name from `docs/brand/NAMES.md`. Done when: `AGENTS.md` names the suite and its six apps. Cheaper substitute: leaving the adaptation placeholder in place.
- [x] Update `README.md` (created 2026-10-20 with the licence notice) so the suite name, one line per app with its Microsoft counterpart, and the codename note match `docs/brand/NAMES.md`. Done when: `python scripts/check-design-doc.py README.md --require "Rizonesoft Office"` exits 0 (**Corrected 2026-10-20:** the command had no value after `--require`, which the checker refuses). Cheaper substitute: a README that only says "Office clone".
- [x] Update `todo/plan.json` `title` to the suite name. Done when: `python scripts/todo-graph.py plan --sync` writes the new title into `todo/implementation-plan.md`. Cheaper substitute: editing the generated plan by hand.
- [x] Commit: `brand: apply suite and app names`

**Test checkpoint:** `rg -n -i "microsoft (word|excel|powerpoint|visio|project|outlook)" README.md` lists only lines that describe the Microsoft counterpart, and `python scripts/todo-graph.py plan --check` exits 0.

> **Verified:** 2026-10-22 | §6 | 13ad86f30241299507b83fbbb1ed1dfd1ee0e8c8
> **Review:** `docs/reviews/d01-t01-s6.json`

## 9. Microsoft Store Name Reservation

The Microsoft Store is where a Windows-only suite is found, and an app's Store name is checked and reserved only in Partner Center, under the publisher's developer account, so no unattended run can check it. Filed 2026-10-22 from §5, whose context names the Store among the package identifiers but whose checks could not reach it.

**Owner decision 2026-10-22:** no Store for now; the name check moves to the release phase, and winget is the Windows channel until then. **Owner decision 2026-10-22 (later the same day):** no Microsoft Store at all; the Inno Setup installer is the channel and the MSIX package waits on signing (`docs/specs/2026-10-23-campaign-scope-design.md`, decisions 11 and 14). **Groomed 2026-10-23:** the section now records that decision instead of checking names in Partner Center.

**Phase:** 7
**Needs:** none
**Surface:** no

**Build order:**

1. Record the no-Store decision. Done when: `docs/brand/naming-clearance.md` has a `### Microsoft Store` subsection saying no name is checked or reserved, with the date and the record it comes from.

- [ ] Write `### Microsoft Store` in `docs/brand/naming-clearance.md`: no Store listing (owner decision 2026-10-22), so no Partner Center check or reservation is made, citing `docs/specs/2026-10-23-campaign-scope-design.md`. Done when: the subsection names the decision, the date and the record. Cheaper substitute: deleting the Store row silently. **Corrected 2026-10-23:** checked and reserved the seven names in Partner Center.
- [ ] Record in `docs/brand/NAMES.md` under `## Channels` that releases ship as the Inno Setup installer on GitHub Releases and that a Store listing would need a new owner decision. Done when: `python scripts/check-design-doc.py docs/brand/NAMES.md --require Channels` exits 0. Cheaper substitute: leaving the channel to the release notes. **Corrected 2026-10-23:** reserved the names the owner chose.
- [ ] Commit: `brand: record that there is no Microsoft Store listing`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/naming-clearance.md --require "Microsoft Store"` exits 0 and `python scripts/check-design-doc.py docs/brand/NAMES.md --require Channels` exits 0.

## Verification

- `docs/brand/NAMES.md`, `docs/brand/naming-brief.md`, `docs/brand/naming-candidates.md` and `docs/brand/naming-clearance.md` all pass `python scripts/check-design-doc.py`.
- No chosen name has a `blocked` verdict in `docs/brand/naming-clearance.md`.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
