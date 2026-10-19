---
schema_version: 1
id: suite-naming
domain: 01-brand
status: active
title: "TODO-01 -- Suite and App Naming"
---

# TODO-01 -- Suite and App Naming

> **Goal:** The suite and its six apps (the counterparts of Word, Excel, PowerPoint, Visio, Project and Outlook) have names that use no Microsoft trademark, pass a knockout trademark screen in Nice classes 9 and 42, have their domain, GitHub and package names reserved or confirmed available, are recorded once in `docs/brand/NAMES.md`, and are applied across the repository.

> **Current state:** Measured 2026-10-19. No brand documents exist (`docs/brand/` is absent). The repository is `rizonesoft/Office-2028`, a working codename that contains the Microsoft trademark "Office"; it must not become a product-facing name. A first brainstorm was held in the Claude Code session on 2026-10-19 and its concepts are seeded in §2.

## Inputs

- Microsoft Trademark and Brand Guidelines: https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks (Word, Excel, PowerPoint, Visio, Outlook, Microsoft 365 and Office are registered marks and are excluded from every candidate).
- USPTO trademark search https://tmsearch.uspto.gov, EUIPO eSearch plus, and WIPO Global Brand Database: the registers for the §4 knockout screen.
- Nice classes 9 (downloadable software) and 42 (software as a service): the classes every candidate is screened in.
- -> XREF: D00 T01 §1 -- `scripts/check-design-doc.py` verifies every document this file writes
- -> XREF: D01 T02 §1 -- the icon language takes the chosen names and the suite motif
- -> XREF: D01 T03 §4 -- the README brand section displays the recorded names

## Outcome

- `docs/brand/NAMES.md` records the suite name, the six app names, the Microsoft app each one maps to, the file-name and identifier forms (`kebab-case`, `PascalCase`, reverse-DNS bundle id), and the date the owner chose them.
- `docs/brand/naming-clearance.md` records, per chosen name, the register searches run, live conflicts found, and domain, GitHub and package availability with dates.
- No product-facing file in the repository uses "Office", "Word", "Excel", "PowerPoint", "Visio", "Project" or "Outlook" as a product name.

**Adjacency:** all=not-applicable (a brand decision record; it creates no user records, settings, documents or permissions)

**Adjacency rationale:** Naming produces documents for contributors and the owner only. The product's own document, settings and exchange surfaces are owned by the application domains authored from D03 T01 §13.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Naming brief and constraints | D00 T01 §1 | [ ] |
| 2 | §2 | Collision screen for the chosen names | §1 | [ ] |
| 3 | §3 | Owner selection of suite and app names | §2 | [ ] |
| 4 | §4 | Knockout trademark screen for chosen names | §3 | [ ] |
| 5 | §5 | Domain, GitHub and package name availability | §3 | [ ] |
| 6 | §6 | Apply names across the repository | §4, §5 | [ ] |
| 7 | §7 | Attorney clearance and filing decision | §4 | [ ] |
| 8 | §8 | GitHub repository rename | §6 | [ ] |

## 1. Naming Brief and Constraints

The brief fixes what a good name must do before anyone argues about taste. It states the exclusions (every Microsoft mark, names of direct competitors and their apps: LibreOffice Writer, Calc, Impress, Draw; OnlyOffice; WPS Office; Google Docs, Sheets, Slides; Apple Pages, Numbers, Keynote; Zoho Writer, Sheet, Show; SoftMaker TextMaker, PlanMaker; Calligra Words, Sheets, Stage, Plan), the structure options (house brand plus descriptive app names, or six standalone names), and the scoring criteria.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Write `docs/brand/naming-brief.md` with Purpose, Exclusions, Structure options, Criteria and Scoring headings. Done when: `python scripts/check-design-doc.py docs/brand/naming-brief.md --require Exclusions --require Criteria` exits 0.

- [ ] Write the Exclusions list in `docs/brand/naming-brief.md` citing the Microsoft trademark list URL in Inputs. Done when: every Microsoft app named in the Goal and every competitor app named in this section appears in the list. Cheaper substitute: "avoid Microsoft names" with no enumerated list.
- [ ] Write the Structure options in `docs/brand/naming-brief.md`: house brand plus descriptive app names versus standalone app names, each with its clearance cost. Done when: both options carry one advantage and one cost. Cheaper substitute: presenting only the option already preferred.
- [ ] Write the Criteria in `docs/brand/naming-brief.md`: pronounceable in English, at most 3 syllables per app name, no negative meaning in the 10 most spoken languages, available `.com` or `.app` for the suite, icon motif potential. Done when: each criterion is a yes or no test. Cheaper substitute: subjective adjectives such as "modern" or "catchy".
- [ ] Write the Scoring rubric in `docs/brand/naming-brief.md` as a table with weights summing to 100. Done when: the weights sum to 100 and every row is at most 100 characters. Cheaper substitute: unweighted gut ranking.
- [ ] Commit: `brand: add naming brief`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/naming-brief.md --require Exclusions --require "Structure options" --require Criteria --require Scoring` exits 0.

## 2. Collision Screen for the Chosen Names

The owner chose on 2026-10-20, ahead of a longlist: the house brand is Rizonetech and the apps are Write, Grid, Stage, Flow, Plan and Mail, known in full as "Rizonetech Write" and so on (the same model as "Microsoft Word"). This section records the brainstorm concepts as alternatives considered and runs an obvious-collision web search on the chosen names before the register searches in §4. Seed concepts from the 2026-10-19 brainstorm, kept as alternatives:

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

- [ ] Record the chosen names in `docs/brand/naming-candidates.md` under `## Chosen`: Rizonetech, and Write, Grid, Stage, Flow, Plan, Mail with their full "Rizonetech <App>" forms. Done when: seven names appear with their Microsoft counterparts. Cheaper substitute: recording the app names without the house brand.
- [ ] Copy the four seed concepts from this section into `docs/brand/naming-candidates.md` under `## Alternatives considered`, with the reason each was not chosen. Done when: Tessera, Rizone, Kestrel and Atelier each carry a reason. Cheaper substitute: dropping the alternatives, which loses the fallback list if a chosen name is blocked.
- [ ] Web-search "Rizonetech" and record live companies, products and domains using it in `docs/brand/naming-candidates.md` under `## Collisions`. Done when: the row names sources or `none found` with the search date. Cheaper substitute: assuming the owner's own brand is clear everywhere.
- [ ] Web-search the proposed collective name "Tesserac" (raised by the owner 2026-10-20) and record conflicts under `## Collisions`, including how far search engines autocorrect it to "Tesseract" and the Tesseract OCR engine (https://github.com/tesseract-ocr/tesseract, document software in class 9). Done when: the row names sources, the autocorrect result and the search date. Cheaper substitute: an exact-match search only, which hides the near-identical mark.
- [ ] Web-search each app name as a software product (for example "Grid spreadsheet", "Flow diagram app", "Stage presentation app") and record prominent conflicts, including Microsoft Flow (renamed Power Automate in 2019) and Microsoft Planner. Done when: six rows each name sources or `none found` with the date. Cheaper substitute: relying on memory, as the seeds in this section did.
- [ ] Commit: `brand: record chosen names and collision screen`

**Test checkpoint:** `python scripts/check-design-doc.py docs/brand/naming-candidates.md --require Chosen --require "Alternatives considered" --require Collisions --require Rizonetech` exits 0.

## 3. Owner Selection of Suite and App Names

The owner picks the concept, can swap individual app names, and the choice is recorded once in `docs/brand/NAMES.md`. Every other file reads names from there. Remove the `owner-decision` Need when the choice is recorded in this section as `Decision: <concept>, <date>`.

Decision, 2026-10-20: house brand Rizonetech; apps Write (Word), Grid (Excel), Stage (PowerPoint), Flow (Visio), Plan (Project) and Mail (Outlook); in-app names are the bare app names and full names are "Rizonetech Write" and so on. The house brand carries the trademark protection, because the bare app names are generic words and "Flow" was Microsoft's product name until 2019. Still open, so `owner-decision` stays: a collective name for the six apps together, used by the installer, the website, §5 domain checks and the §8 repository rename (the default is "Rizonetech" alone).

**Phase:** 1
**Needs:** owner-decision
**Surface:** no

**Build order:**

1. Present the scored shortlist from `docs/brand/naming-candidates.md` to the owner with `AskUserQuestion`. Done when: the owner's choice is recorded in this section.
2. Write `docs/brand/NAMES.md`. Done when: the design-doc checker passes with the required headings.

- [ ] Record the owner's chosen concept and any per-app swaps in `docs/brand/NAMES.md` under `## Suite` and `## Apps`. Done when: six app rows each name the Microsoft counterpart. Cheaper substitute: recording only the suite name and leaving app names implied.
- [ ] Add the identifier forms to `docs/brand/NAMES.md` under `## Identifiers`: display name, `kebab-case`, `PascalCase`, and reverse-DNS bundle id under the owner's domain. Done when: all four forms exist for the suite and each app. Cheaper substitute: deriving identifiers ad hoc in each later file.
- [ ] Add the file extension policy to `docs/brand/NAMES.md` under `## File formats`: native OOXML extensions (`.docx`, `.xlsx`, `.pptx`, `.vsdx`) are kept, and any native project format gets its own extension. Done when: each app lists its default save format. Cheaper substitute: inventing proprietary formats for apps whose OOXML format is standard.
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

- [ ] Replace the first paragraph placeholder in `AGENTS.md` with what the project is, using the suite name from `docs/brand/NAMES.md`. Done when: `AGENTS.md` names the suite and its six apps. Cheaper substitute: leaving the Conclave-SDK adaptation note in place.
- [ ] Create `README.md` with the suite name, one line per app with its Microsoft counterpart, and a codename note. Done when: `python scripts/check-design-doc.py README.md --require` with the suite name exits 0. Cheaper substitute: a README that only says "Office clone".
- [ ] Update `todo/plan.json` `title` to the suite name. Done when: `python scripts/todo-graph.py plan --sync` writes the new title into `todo/implementation-plan.md`. Cheaper substitute: editing the generated plan by hand.
- [ ] Commit: `brand: apply suite and app names`

**Test checkpoint:** `rg -n -i "microsoft (word|excel|powerpoint|visio|project|outlook)" README.md` lists only lines that describe the Microsoft counterpart, and `python scripts/todo-graph.py plan --check` exits 0.

## 7. Attorney Clearance and Filing Decision

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

Renaming `rizonesoft/Office-2028` changes a public URL. GitHub redirects the old URL, but local clones, CI badges and links need updating. The owner performs or approves the rename.

**Phase:** 1
**Needs:** operator
**Surface:** no

**Build order:**

1. Rename the repository in GitHub settings to the `kebab-case` suite identifier from `docs/brand/NAMES.md`. Done when: `gh repo view --json name` prints the new name.
2. Update the local remote and every in-repo URL. Done when: `rg -n "Office-2028" --glob "!todo/**"` returns nothing.

- [ ] Rename the repository with `gh repo rename <kebab-case-name>` after owner approval. Done when: `gh repo view --json name` prints the new name. Cheaper substitute: creating a second repository and abandoning history.
- [ ] Update `origin` with `git remote set-url origin <new url>`. Done when: `git remote -v` shows the new URL and `git fetch` succeeds. Cheaper substitute: relying on GitHub's redirect forever.
- [ ] Update in-repo URLs (README badges, workflow references) to the new name. Done when: `rg -n "Office-2028" --glob "!todo/**"` returns nothing. Cheaper substitute: leaving stale links to resolve by redirect.
- [ ] Commit: `brand: update repository URLs after rename`

**Test checkpoint:** `gh repo view --json name,url` prints the new name and `git ls-remote origin HEAD` exits 0.

## Verification

- `docs/brand/NAMES.md`, `docs/brand/naming-brief.md`, `docs/brand/naming-candidates.md` and `docs/brand/naming-clearance.md` all pass `python scripts/check-design-doc.py`.
- No chosen name has a `blocked` verdict in `docs/brand/naming-clearance.md`.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
