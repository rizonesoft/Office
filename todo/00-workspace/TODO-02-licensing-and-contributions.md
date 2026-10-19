---
schema_version: 1
id: licensing-and-contributions
domain: 00-workspace
status: active
title: "TODO-02 -- Licensing and Contributions"
---

# TODO-02 -- Licensing and Contributions

> **Goal:** Rizonesoft Office is cleanly licensed as GPL-3.0-or-later with a contributor agreement that keeps a commercial edition possible. Every source file carries an SPDX identifier and CI refuses one without it; every bundled third-party component has its licence and obligations recorded in one notices file and shipped with the app; outside pull requests cannot merge until the contributor agreement is signed.

> **Current state:** Measured 2026-10-20. On 2026-10-20 the owner chose GPL-3.0-or-later (matching Qt's open-source edition), a contributor licence agreement rather than a DCO sign-off, and Windows first with macOS and Linux following. `LICENSE` holds the verbatim GPLv3 text (SHA-256 `3972dc97...b36986`) and `README.md` states the "or later" grant. Not yet present: SPDX headers on `scripts/`, `THIRD-PARTY-NOTICES.md`, the agreement text, a CLA check on pull requests, and `CONTRIBUTING.md`. Bundled today: Plus Jakarta Sans (SIL OFL 1.1) in `design/fonts/plus-jakarta-sans/`. Planned: Qt 6 (LGPLv3 or GPLv3 parts), Fluent UI System Icons (MIT) for ribbon commands.

## Inputs

- GNU GPLv3 text https://www.gnu.org/licenses/gpl-3.0.txt and the FSF guidance "How to use GNU licenses for your own software" https://www.gnu.org/licenses/gpl-howto.html: the notice wording for README and file headers.
- SPDX License List https://spdx.org/licenses/ and REUSE specification 3.3 https://reuse.software/spec/: the per-file identifier convention.
- Qt licensing https://doc.qt.io/qt-6/licensing.html: which Qt modules are LGPLv3 and which are GPLv3 only, and what LGPL distribution requires.
- Project Harmony contributor agreement templates https://www.harmonyagreements.org/: a standard starting point for the agreement, reviewed by a lawyer before use.
- -> XREF: D03 T01 §11 -- the product licence decision and the dependency licence policy this file enforces

## Outcome

- `python scripts/check-spdx.py` exits 0 only when every tracked source file under `scripts/` and future code roots carries `SPDX-License-Identifier: GPL-3.0-or-later` (or its own third-party identifier), and CI runs it.
- `THIRD-PARTY-NOTICES.md` lists every bundled component with version, licence, source URL and obligations, and the installers ship it.
- `docs/legal/rizonesoft-cla.md` holds the lawyer-reviewed agreement, and a pull request from an unsigned contributor shows a failing CLA check.
- `CONTRIBUTING.md` explains how to build, test, sign the agreement and submit changes.

**Adjacency:** all=not-applicable (repository licensing and contribution process; no product records, settings or user documents)

**Adjacency rationale:** Licensing governs how the code is shared, not what users store. The About box that shows licence and notices to users is a product surface owned by the shell domain authored from D03 T01 §13.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | SPDX headers and checker | -- | [ ] |
| 2 | §2 | Third-party notices file | -- | [ ] |
| 3 | §3 | Contributor agreement text | -- | [ ] |
| 4 | §4 | Contributor agreement check on pull requests | §3 | [ ] |
| 5 | §5 | Contributing guide | §1 | [ ] |

## 1. SPDX Headers and Checker

Each file states its own licence so a copied file keeps its terms. Rizonesoft code carries `SPDX-License-Identifier: GPL-3.0-or-later` and a copyright line; vendored third-party files keep their own identifier. Generated assets are covered by a `REUSE.toml` annotation instead of per-file headers.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/check-spdx.py` with tests. Done when: it refuses a fixture source file without an identifier and passes one with it.
2. Add headers to every tracked file under `scripts/` and annotate generated assets in `REUSE.toml`. Done when: `python scripts/check-spdx.py` exits 0 on the repository.

- [ ] Write `scripts/check-spdx.py` listing tracked files with `git ls-files` and checking the first 10 lines of each `.py`, `.mjs`, `.cpp`, `.h`, `.qml` and `.cmake` file for `SPDX-License-Identifier:`. Done when: a fixture without the line exits 1 naming the file. Cheaper substitute: checking only files changed in the last commit.
- [ ] Add `--allow` handling in `scripts/check-spdx.py` for third-party identifiers recorded in `THIRD-PARTY-NOTICES.md`. Done when: a vendored MIT file with `SPDX-License-Identifier: MIT` passes and an unknown identifier fails. Cheaper substitute: accepting any identifier string.
- [ ] Write `scripts/tests/test_check_spdx.py` covering missing, valid, third-party and unknown identifiers. Done when: the suite passes and fails when the identifier check returns success unconditionally.
- [ ] Add `# SPDX-License-Identifier: GPL-3.0-or-later` and `# Copyright 2026 Rizonesoft` to every Rizonesoft-authored file under `scripts/`, leaving the Conclave-SDK kit files with the identifier their kit declares. Done when: `python scripts/check-spdx.py` exits 0. Cheaper substitute: one blanket statement in README instead of per-file identifiers.
- [ ] Write `REUSE.toml` annotating `assets/**` and `design/icons/**` as GPL-3.0-or-later generated output, and `design/fonts/**` as OFL-1.1. Done when: `reuse lint` reports no unlicensed files. Cheaper substitute: leaving generated files unannotated.
- [ ] Commit: `legal: add SPDX headers and checker`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_check_spdx.py"` passes and `python scripts/check-spdx.py` exits 0.

## 2. Third-Party Notices File

GPLv3 for our code does not remove the duties of the components we ship. Qt's LGPLv3 parts need their licence text and source availability; GPL-only Qt modules are allowed because the product is GPL; the OFL font and the MIT icon set need their notices.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `THIRD-PARTY-NOTICES.md` with one entry per bundled component. Done when: every component in Current state has an entry with all fields.

- [ ] Add the Plus Jakarta Sans entry (version 2.071, SIL OFL 1.1, https://github.com/tokotype/PlusJakartaSans, reserved font name rules) to `THIRD-PARTY-NOTICES.md`. Done when: the entry names version, licence, source and obligations. Cheaper substitute: a link without the licence text.
- [ ] Add the Fluent UI System Icons entry (MIT, https://github.com/microsoft/fluentui-system-icons, pinned version) with the MIT notice text. Done when: the entry carries the copyright line from the upstream LICENSE. Cheaper substitute: "MIT" with no copyright notice, which MIT requires.
- [ ] Add the Qt 6 entry listing each module the product links, its licence (LGPLv3 or GPLv3), and how source is offered. Done when: every module in the foundation plan's Toolchain section is listed. Cheaper substitute: one line saying "Qt is LGPL", which hides GPL-only modules.
- [ ] Add a "How this file is maintained" note in `THIRD-PARTY-NOTICES.md` naming D03 T01 §11's dependency policy as the gate for new entries. Done when: the note names the policy file. Cheaper substitute: adding entries only at release time.
- [ ] Commit: `legal: add third-party notices`

**Test checkpoint:** `python scripts/check-design-doc.py THIRD-PARTY-NOTICES.md --require "Plus Jakarta Sans" --require "Fluent UI System Icons" --require "Qt 6"` exits 0.

## 3. Contributor Agreement Text

The agreement lets Rizonesoft relicense contributions (for example a commercial edition) while contributors keep their copyright. It starts from a Project Harmony template and must be reviewed by a lawyer before it binds anyone.

**Phase:** 99
**Needs:** third-party, owner-decision
**Surface:** no

**Build order:**

1. Draft `docs/legal/rizonesoft-cla.md` for individuals and `docs/legal/rizonesoft-cla-entity.md` for companies from the Harmony templates. Done when: both drafts name Rizonesoft as the recipient and the outbound licence choice.
2. Record the lawyer's review and the owner's approval. Done when: both documents carry a `## Review` section with date and reviewer.

- [ ] Draft the individual agreement in `docs/legal/rizonesoft-cla.md` from the Harmony HA-CLA-I template with the "any licence" outbound option. Done when: the draft names Rizonesoft, the governing law the owner chooses and the outbound option. Cheaper substitute: a home-written agreement with no template.
- [ ] Draft the entity agreement in `docs/legal/rizonesoft-cla-entity.md` from HA-CLA-E with the same choices. Done when: the draft matches the individual one except for the entity clauses. Cheaper substitute: individual agreement only, which blocks company contributors.
- [ ] Record the lawyer's review in both files under `## Review` with date and firm. Done when: both files carry the review. Cheaper substitute: publishing an unreviewed agreement.
- [ ] Record the owner's approval and remove `owner-decision` and `third-party` from this section. Done when: the approval line carries the date. Cheaper substitute: treating the draft as final.
- [ ] Commit: `legal: add contributor agreements`

**Test checkpoint:** `python scripts/check-design-doc.py docs/legal/rizonesoft-cla.md --require Review` and the same for `docs/legal/rizonesoft-cla-entity.md` exit 0.

## 4. Contributor Agreement Check on Pull Requests

A GitHub check blocks merging until each pull request author has signed. CLA Assistant (a hosted GitHub app) or a self-hosted workflow such as `contributor-assistant/github-action` records signatures in the repository.

**Phase:** 99
**Needs:** operator
**Surface:** no

**Build order:**

1. Install the chosen CLA check on `rizonesoft/Office-2028` pointing at `docs/legal/rizonesoft-cla.md`. Done when: a test pull request from an unsigned account shows a failing check.
2. Make the check required in branch protection for `main`. Done when: the unsigned test pull request cannot merge.

- [ ] Choose between CLA Assistant and the self-hosted GitHub Action and record why in `docs/legal/README.md`. Done when: the choice names where signatures are stored. Cheaper substitute: collecting signatures by email.
- [ ] Install and configure the check to link `docs/legal/rizonesoft-cla.md` and `docs/legal/rizonesoft-cla-entity.md`. Done when: the check comment on a test pull request links both. Cheaper substitute: a README request to sign, with no enforcement.
- [ ] Mark the check as required on `main` in branch protection. Done when: `gh api repos/rizonesoft/Office-2028/branches/main/protection` lists the check. Cheaper substitute: an optional check that can be ignored.
- [ ] Commit: `legal: document contributor agreement check`

**Test checkpoint:** `gh api repos/rizonesoft/Office-2028/branches/main/protection --jq .required_status_checks.contexts` includes the CLA check name.

## 5. Contributing Guide

`CONTRIBUTING.md` tells a newcomer how to build, test, follow the TODO workflow, sign the agreement and open a pull request, and states the licence their work is released under.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `CONTRIBUTING.md`. Done when: the design-doc checker passes with the required headings.

- [ ] Write the Licence and agreement section of `CONTRIBUTING.md`: GPL-3.0-or-later, the agreement link, and the SPDX header to add. Done when: it links `docs/legal/rizonesoft-cla.md` and shows the header line. Cheaper substitute: "see LICENSE".
- [ ] Write the Build and test section from the foundation plan's Toolchain commands and `scripts/requirements.txt`. Done when: every command in it runs on a clean clone. Cheaper substitute: commands copied from memory.
- [ ] Write the Workflow section pointing at `docs/todo-workflow.md` and the commit rules in `AGENTS.md`. Done when: both links resolve. Cheaper substitute: restating the rules, which then drift.
- [ ] Commit: `docs: add contributing guide`

**Test checkpoint:** `python scripts/check-design-doc.py CONTRIBUTING.md --require "Licence and agreement" --require "Build and test" --require Workflow` exits 0.

## Verification

- `python scripts/check-spdx.py` and `reuse lint` pass on a fresh clone.
- `THIRD-PARTY-NOTICES.md` names every bundled component and the installers include it.
- An unsigned test pull request cannot merge into `main`.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
