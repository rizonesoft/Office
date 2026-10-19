---
schema_version: 1
id: design-doc-tooling
domain: 00-workspace
status: active
title: "TODO-01 -- Design Document Tooling"
---

# TODO-01 -- Design Document Tooling

> **Goal:** Design work (brand, interface, architecture) is checked by scripts, not by eye. A design-document checker refuses missing headings, placeholder text, dash characters and over-wide table rows; an image-asset checker refuses wrong dimensions, formats or byte budgets; CI runs both test suites plus the TODO validator on every push and pull request.

> **Current state:** Measured 2026-10-19. The repository holds only the Conclave-SDK kits: `scripts/todo-graph.py`, `scripts/lib/todo_graph.py`, `scripts/review-dispatch.py`, `scripts/verify-agent-tiers.mjs` and `scripts/tests/test_review_dispatch.py`. There is no application code, no `design/` directory, no `docs/plans/`, no `.github/workflows/`, and no checker for design documents or image assets. Python 3.14 is on the Windows host.

## Inputs

- `todo/README.md`: the section contract; every later Test checkpoint in domains 01 to 03 calls the checkers built here.
- `AGENTS.md` working rules: no em or en dashes, one line per paragraph, table rows at most 100 characters. §1 enforces them on design documents.
- GitHub social preview guidance (Settings, General, Social preview): 1280 by 640 pixels recommended, under 1 MB. §2 enforces sizes and budgets.
- -> XREF: D01 T01 §1 -- the naming brief is the first document checked by `scripts/check-design-doc.py`
- -> XREF: D01 T02 §6 -- the icon export pipeline verifies its output with `scripts/check-image-asset.py`

## Outcome

- `python scripts/check-design-doc.py <file> --require "<heading>"` exits 0 on a conforming document and 1 with a named reason on each refusal.
- `python scripts/check-image-asset.py <file> --size 1280x640 --max-bytes 1000000` exits 0 on a conforming PNG, SVG or ICO and 1 with a named reason otherwise.
- `.github/workflows/ci.yml` runs `todo-graph.py validate`, `plan --check` and every suite in `scripts/tests/` on push and pull request, and the latest run on `main` is green.

**Adjacency:** all=not-applicable (developer tooling with no user records, settings, documents or permissions)

**Adjacency rationale:** These are repository gates used only by contributors and CI. They hold no user data, so list, document, settings, reporting, notifications, permissions, audit, exchange and reverse have nothing to attach to.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Design document checker | -- | [ ] |
| 2 | §2 | Image asset checker | -- | [ ] |
| 3 | §3 | Continuous integration workflow | §1, §2 | [ ] |

## 1. Design Document Checker

Every design deliverable in domains 01 to 03 is a Markdown document whose Test checkpoint calls this checker. It refuses a document that lacks a required heading, still carries placeholder text (`CHANGEME`, `TBD`, `TODO:`, `lorem ipsum`), contains U+2014 or U+2013 outside fenced code, or has a table row over 100 characters. Standard library only, so it runs on any host with Python 3.11 or later.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/check-design-doc.py` with a path argument and repeatable `--require`. Done when: it exits 0 on a conforming fixture and 1 on every refusal fixture, printing the reason.
2. Write `scripts/tests/test_check_design_doc.py`. Done when: the suite passes and fails when any rule is disabled.

- [ ] Create the argparse CLI in `scripts/check-design-doc.py` taking one path and repeatable `--require "<heading text>"`. Done when: `python scripts/check-design-doc.py --help` lists both. Cheaper substitute: an inline shell grep per Test checkpoint that cannot be unit tested.
- [ ] Add `missing_headings()` in `scripts/check-design-doc.py` matching `#`-prefixed heading lines exactly. Done when: a fixture lacking `## Constraints` run with `--require "Constraints"` exits 1 printing `missing heading: Constraints`. Cheaper substitute: a substring match that a word inside a paragraph satisfies.
- [ ] Add `placeholders()` in `scripts/check-design-doc.py` for `CHANGEME`, `TBD`, `TODO:` and `lorem ipsum`, case-insensitive. Done when: each token in a fixture is reported with its line number. Cheaper substitute: checking only the first match and stopping.
- [ ] Add `dashes()` in `scripts/check-design-doc.py` reporting U+2014 and U+2013 outside fenced code blocks (source: `AGENTS.md` working rules). Done when: a fixture with an em dash in prose fails and the same dash inside a code fence passes. Cheaper substitute: scanning code fences too, which breaks quoted byte-exact content.
- [ ] Add `wide_rows()` in `scripts/check-design-doc.py` refusing `|` table rows longer than 100 characters (source: `AGENTS.md`). Done when: a 101-character row fails and a 100-character row passes. Cheaper substitute: measuring bytes instead of characters, which miscounts `§`.
- [ ] Write `scripts/tests/test_check_design_doc.py` with one conforming fixture and one fixture per rule. Done when: `python -m unittest discover -s scripts/tests -p "test_check_design_doc.py"` passes, and fails when any rule function is replaced by `return []`.
- [ ] Commit: `tooling: add design document checker`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_check_design_doc.py"` reports at least 5 tests run and `OK`.

## 2. Image Asset Checker

Icons, banners and the social preview are verified by a script before they are committed. It reads PNG dimensions from the IHDR chunk, SVG `viewBox` and forbidden content (embedded raster `<image>`, external `href`, `<script>`), ICO directory entries, and the byte size, using only the standard library.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `scripts/check-image-asset.py` with `--size WxH` (repeatable for ICO), `--max-bytes` and `--format`. Done when: each refusal fixture exits 1 with a reason and the conforming fixtures exit 0.
2. Write `scripts/tests/test_check_image_asset.py` with generated fixtures. Done when: the suite passes and fails when a rule is disabled.

- [ ] Add `png_size()` in `scripts/check-image-asset.py` reading width and height from the IHDR chunk. Done when: a generated 1280x640 PNG reports `1280x640`. Cheaper substitute: trusting the file name or extension.
- [ ] Add `svg_check()` in `scripts/check-image-asset.py` reading the root `viewBox` and refusing `<image>`, `<script>` and non-fragment `href` values. Done when: a fixture embedding a base64 PNG fails with `embedded raster`. Cheaper substitute: accepting any file that parses as XML.
- [ ] Add `ico_sizes()` in `scripts/check-image-asset.py` listing every directory entry size. Done when: an ICO built with 16, 32 and 256 entries passes `--size 16x16 --size 32x32 --size 256x256` and fails when one is missing. Cheaper substitute: checking only the first entry.
- [ ] Add the `--max-bytes` budget check in `scripts/check-image-asset.py`. Done when: a file one byte over the budget fails with `over budget`. Cheaper substitute: rounding to kilobytes so near misses pass.
- [ ] Write `scripts/tests/test_check_image_asset.py` generating PNG, SVG and ICO fixtures in a temporary directory with `zlib` and `struct`. Done when: the suite passes and fails when any check returns success unconditionally.
- [ ] Commit: `tooling: add image asset checker`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_check_image_asset.py"` reports at least 6 tests run and `OK`.

## 3. Continuous Integration Workflow

One workflow keeps the TODO tree, the generated plan and the tooling tests honest on every push. It runs on `ubuntu-latest` with Python 3.12 so it also proves the scripts are not Windows-only.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `.github/workflows/ci.yml` triggered on `push` and `pull_request`. Done when: the file passes `actionlint` locally or in the run.
2. Push to `main` and read the run result. Done when: `gh run list --workflow ci.yml --limit 1` shows `success`.

- [ ] Add the checkout and `actions/setup-python` steps pinned to a release tag in `.github/workflows/ci.yml`. Done when: the workflow file names Python `3.12`. Cheaper substitute: relying on the runner's default Python, which drifts.
- [ ] Add a step running `python scripts/todo-graph.py validate` in `.github/workflows/ci.yml`. Done when: a deliberately malformed TODO row on a scratch branch makes the run fail. Cheaper substitute: `continue-on-error: true`.
- [ ] Add a step running `python scripts/todo-graph.py plan --check` in `.github/workflows/ci.yml`. Done when: an unsynced plan on a scratch branch makes the run fail. Cheaper substitute: running `plan --sync` in CI, which hides staleness.
- [ ] Add a step running `python -m unittest discover -s scripts/tests` in `.github/workflows/ci.yml`. Done when: the run log lists the design-doc and image-asset suites. Cheaper substitute: listing test files by name so new suites are skipped.
- [ ] Commit: `ci: validate todo tree and run tooling tests`

**Test checkpoint:** `gh run list --workflow ci.yml --branch main --limit 1 --json conclusion` prints `"conclusion":"success"`.

## Verification

- `python -m unittest discover -s scripts/tests` passes on Windows and in CI.
- `python scripts/check-design-doc.py todo/README.md` exits 0 or names a real defect that is then filed in `todo/findings.md`.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
