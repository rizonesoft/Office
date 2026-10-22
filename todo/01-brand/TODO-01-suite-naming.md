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
- USPTO trademark search https://tmsearch.uspto.gov, EUIPO eSearch plus, and WIPO Global Brand Database: the registers for the §4 knockout screen.
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
| 3 | §3 | Owner selection of suite and app names | §2 | [ ] |
| 4 | §4 | Knockout trademark screen for chosen names | §3 | [ ] |
| 5 | §5 | Domain, GitHub and package name availability | §3 | [ ] |
| 6 | §6 | Apply names across the repository | §4, §5 | [ ] |
| 7 | §7 | Attorney clearance and filing | §4 | [ ] |
| 8 | §8 | GitHub repository rename | §6 | [ ] |

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
- [ ] Commit: `brand: record chosen suite and app names`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/NAMES.md --require Suite --require Apps --require Identifiers --require "File formats"` exits 0.

## 4. Knockout Trademark Screen for Chosen Names

A knockout screen catches identical or near-identical live marks in classes 9 and 42 before money is spent on graphics. It is not legal clearance; §7 owns that.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Search USPTO, EUIPO and WIPO for the suite name and each app name in classes 9 and 42. Done when: `docs/brand/naming-clearance.md` has one row per name per register with result counts and the search date.

- [ ] Search the USPTO register for each chosen name and record live marks in classes 9 and 42 in `docs/brand/naming-clearance.md`. Done when: each name has a USPTO row with the query string and date. Cheaper substitute: searching the suite name only.
- [ ] Search EUIPO eSearch plus for each chosen name and record live marks in `docs/brand/naming-clearance.md`. Done when: each name has an EUIPO row. Cheaper substitute: treating the US result as global.
- [ ] Search the WIPO Global Brand Database for each chosen name and record live marks in `docs/brand/naming-clearance.md`. Done when: each name has a WIPO row. Cheaper substitute: skipping WIPO because the first two were clean.
- [ ] Write a Verdict line per name in `docs/brand/naming-clearance.md`: `clear`, `risk` (with the conflicting mark) or `blocked`. Done when: no name is left without a verdict, and any `blocked` name returns to §3 as a recorded swap. Cheaper substitute: a single verdict for the whole suite.
- [ ] Commit: `brand: record knockout trademark screen`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/naming-clearance.md --require USPTO --require EUIPO --require WIPO --require Verdicts` exits 0.

## 5. Domain, GitHub and Package Name Availability

The product needs a home domain, a GitHub repository or organisation name, and package identifiers (winget, Microsoft Store, Homebrew cask, Flathub, npm scope if the stack uses one). This section checks and records availability; buying anything is the owner's call.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Check availability for each identifier and record it in `docs/brand/naming-clearance.md` under `## Availability`. Done when: every identifier row has `available`, `taken` or `owned` with the date.

- [ ] Check `.com`, `.app` and `.dev` availability for the suite name with `whois` and record it in `docs/brand/naming-clearance.md`. Done when: three rows exist with dates. Cheaper substitute: a registrar search page that hides premium pricing.
- [ ] Check the GitHub organisation and repository names with `gh api users/<name>` and record the result. Done when: the row shows the HTTP status. Cheaper substitute: assuming availability because the name is unusual.
- [ ] Check winget (`winget search`), Homebrew (`brew search` or formulae.brew.sh) and Flathub for each app identifier and record results. Done when: each app has a row per registry. Cheaper substitute: checking the suite name only.
- [ ] Commit: `brand: record name availability`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/naming-clearance.md --require Availability` exits 0.

## 6. Apply Names Across the Repository

Once names are clear, contributor-facing documents stop calling the product "Office 2028". The repository folder and remote keep their codename until §8.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Update `AGENTS.md` and create `README.md` with the product name from `docs/brand/NAMES.md`. Done when: `rg -n "Office 2028" README.md AGENTS.md` returns only the codename note.

- [ ] Replace the first paragraph placeholder in `AGENTS.md` with what the project is, using the suite name from `docs/brand/NAMES.md`. Done when: `AGENTS.md` names the suite and its six apps. Cheaper substitute: leaving the adaptation placeholder in place.
- [ ] Update `README.md` (created 2026-10-20 with the licence notice) so the suite name, one line per app with its Microsoft counterpart, and the codename note match `docs/brand/NAMES.md`. Done when: `python scripts/check-design-doc.py README.md --require "Rizonesoft Office"` exits 0 (**Corrected 2026-10-20:** the command had no value after `--require`, which the checker refuses). Cheaper substitute: a README that only says "Office clone".
- [ ] Update `todo/plan.json` `title` to the suite name. Done when: `python scripts/todo-graph.py plan --sync` writes the new title into `todo/implementation-plan.md`. Cheaper substitute: editing the generated plan by hand.
- [ ] Commit: `brand: apply suite and app names`

**Test checkpoint:** `rg -n -i "microsoft (word|excel|powerpoint|visio|project|outlook)" README.md` lists only lines that describe the Microsoft counterpart, and `python scripts/todo-graph.py plan --check` exits 0.

## 7. Attorney Clearance and Filing

A full clearance opinion and any trademark filing need a trademark attorney and money, so this is operator work. It does not block engineering, but it must close before the first public release.

**Phase:** 99
**Needs:** third-party, owner-decision
**Surface:** no

**Build order:**

1. Send `docs/brand/naming-clearance.md` to a trademark attorney and record the opinion. Done when: `docs/brand/naming-clearance.md` has a `## Attorney opinion` section with date and firm.

- [ ] Record the attorney's opinion per name in `docs/brand/naming-clearance.md` under `## Attorney opinion`. Done when: every chosen name has `proceed`, `proceed with changes` or `do not use`. Cheaper substitute: treating the knockout screen in §4 as clearance.
- [ ] Record the owner's filing decision (jurisdictions, classes, budget) in `docs/brand/naming-clearance.md` under `## Filing`. Done when: the decision and date are recorded. Cheaper substitute: filing without recording jurisdictions.
- [ ] Commit: `brand: record attorney clearance and filing decision`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/naming-clearance.md --require "Attorney opinion" --require Filing` exits 0.

## 8. GitHub Repository Rename

Renaming `rizonesoft/Office` changes a public URL. GitHub redirects the old URL, but local clones, CI badges and links need updating. The owner performs or approves the rename.

**Phase:** 1
**Needs:** operator
**Surface:** no

**Build order:**

1. Rename the repository in GitHub settings to the `kebab-case` suite identifier from `docs/brand/NAMES.md`. Done when: `gh repo view --json name` prints the new name.
2. Update the local remote and every in-repo URL. Done when: `rg -n "Office" --glob "!todo/**"` returns nothing.

- [ ] Rename the repository with `gh repo rename <kebab-case-name>` after owner approval. Done when: `gh repo view --json name` prints the new name. Cheaper substitute: creating a second repository and abandoning history.
- [ ] Update `origin` with `git remote set-url origin <new url>`. Done when: `git remote -v` shows the new URL and `git fetch` succeeds. Cheaper substitute: relying on GitHub's redirect forever.
- [ ] Update in-repo URLs (README badges, workflow references) to the new name. Done when: `rg -n "Office" --glob "!todo/**"` returns nothing. Cheaper substitute: leaving stale links to resolve by redirect.
- [ ] Commit: `brand: update repository URLs after rename`

**Test checkpoint:** `gh repo view --json name,url` prints the new name and `git ls-remote origin HEAD` exits 0.

## Verification

- `docs/brand/NAMES.md`, `docs/brand/naming-brief.md`, `docs/brand/naming-candidates.md` and `docs/brand/naming-clearance.md` all pass `python scripts/check-design-doc.py`.
- No chosen name has a `blocked` verdict in `docs/brand/naming-clearance.md`.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
