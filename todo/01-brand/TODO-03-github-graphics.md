---
schema_version: 1
id: github-graphics
domain: 01-brand
status: active
title: "TODO-03 -- GitHub Graphics"
---

# TODO-03 -- GitHub Graphics

> **Goal:** The GitHub repository presents the suite properly: a README hero banner in light and dark variants, an app lineup strip, a social preview image that GitHub shows when the repository link is shared, and an organisation or repository avatar, all built from the icon masters and set in the repository settings.

> **Current state:** Measured 2026-10-19. `rizonesoft/Office-2028` has no `README.md`, no social preview and no graphics. The icon masters come from D01 T02 §2 and §3; the names from D01 T01 §3.

## Inputs

- `design/brand/suite-mark.svg`, `design/brand/wordmark.svg` and `design/icons/apps/*.svg` from D01 T02.
- GitHub social preview: 1280 by 640 pixels recommended (minimum 640 by 320), PNG, JPG or GIF under 1 MB, uploaded only through repository Settings (no API).
- GitHub README `<picture>` with `prefers-color-scheme` sources for light and dark themes.
- -> XREF: D01 T02 §3 -- the lineup strip and social preview use the app icon masters
- -> XREF: D01 T01 §6 -- the README written here extends the README created when names are applied

## Outcome

- `design/github/` holds `banner-light.svg`, `banner-dark.svg`, `lineup-light.svg`, `lineup-dark.svg` and `social-preview.svg`, with PNG exports in `docs/assets/github/`.
- `README.md` shows the banner and lineup through `<picture>` elements that switch with the GitHub theme.
- The repository's social preview and the organisation avatar are set, confirmed by `gh repo view --json openGraphImageUrl`.

**Adjacency:** all=not-applicable (repository presentation graphics; no product records, settings or permissions)

**Adjacency rationale:** These graphics live on GitHub and in the README only. Product-facing marketing pages, if any, would be owned by the release domain authored from D03 T01 §13.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | README hero banner in light and dark | D01 T02 §2 | [ ] |
| 2 | §2 | Social preview image | D01 T02 §3 | [ ] |
| 3 | §3 | App lineup strip in light and dark | D01 T02 §3 | [ ] |
| 4 | §4 | README brand presentation | §1, §3, D01 T01 §6 | [ ] |
| 5 | §5 | Upload social preview and avatar | §2 | [ ] |

## 1. README Hero Banner in Light and Dark

The banner is the first thing a visitor sees: suite mark, wordmark and a one-line description on a background tuned for each GitHub theme.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Compose `design/github/banner-light.svg` and `design/github/banner-dark.svg` at 1280 by 320. Done when: both pass the image-asset checker.
2. Export PNGs to `docs/assets/github/`. Done when: each PNG is 2560 by 640 (2x) and under 500 KB.

- [ ] Compose `design/github/banner-light.svg` with the suite mark, wordmark and tagline, text outlined. Done when: `python scripts/check-image-asset.py design/github/banner-light.svg --format svg` exits 0. Cheaper substitute: a screenshot of a slide.
- [ ] Compose `design/github/banner-dark.svg` with colours from `docs/brand/icon-language.md` that hold 4.5:1 text contrast on `#0d1117`. Done when: the tagline contrast ratio is recorded in the SVG comment and is at least 4.5. Cheaper substitute: the light banner with inverted colours.
- [ ] Add banner targets to `scripts/build-icons.py` exporting `docs/assets/github/banner-light.png` and `banner-dark.png` at 2560x640. Done when: `python scripts/check-image-asset.py docs/assets/github/banner-light.png --size 2560x640 --max-bytes 500000` exits 0. Cheaper substitute: hand-exported PNGs that drift from the SVG.
- [ ] Commit: `brand: add README banner`

**Test checkpoint:** `python scripts/check-image-asset.py docs/assets/github/banner-dark.png --size 2560x640 --max-bytes 500000` exits 0.

## 2. Social Preview Image

The social preview is what shows on X, LinkedIn, Slack and Discord when the repository link is shared. It must read at thumbnail size and keep important content inside a 40 pixel safe margin.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Compose `design/github/social-preview.svg` at 1280 by 640. Done when: the checker passes on the SVG.
2. Export `docs/assets/github/social-preview.png`. Done when: it is exactly 1280x640 and under 1 MB.

- [ ] Compose `design/github/social-preview.svg` with the wordmark, the six app icons and the tagline inside a 40 pixel safe margin. Done when: no element's bounding box crosses the margin. Cheaper substitute: the README banner stretched to 2:1.
- [ ] Add a social preview target to `scripts/build-icons.py` exporting `docs/assets/github/social-preview.png`. Done when: `python scripts/check-image-asset.py docs/assets/github/social-preview.png --size 1280x640 --max-bytes 1000000` exits 0. Cheaper substitute: a JPEG with visible compression artefacts.
- [ ] Review the PNG at 400 by 200 pixels in `R:\scratch`. Done when: the suite name is legible at that size. Cheaper substitute: reviewing only at full size.
- [ ] Commit: `brand: add social preview image`

**Test checkpoint:** `python scripts/check-image-asset.py docs/assets/github/social-preview.png --size 1280x640 --max-bytes 1000000` exits 0.

## 3. App Lineup Strip in Light and Dark

A strip of the six app icons with their names, so a visitor sees the whole suite and which Microsoft app each one replaces.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Compose `design/github/lineup-light.svg` and `lineup-dark.svg`. Done when: both pass the checker.
2. Export both to `docs/assets/github/`. Done when: each PNG passes the size check.

- [ ] Compose `design/github/lineup-light.svg` with six icons at 96 pixels and outlined names beneath. Done when: the six names match `docs/brand/NAMES.md` exactly. Cheaper substitute: names typed from memory.
- [ ] Compose `design/github/lineup-dark.svg` with name colours holding 4.5:1 on `#0d1117`. Done when: the contrast ratio is recorded in the SVG comment. Cheaper substitute: one strip used on both themes.
- [ ] Add lineup targets to `scripts/build-icons.py` exporting 2x PNGs to `docs/assets/github/`. Done when: `python scripts/check-image-asset.py docs/assets/github/lineup-light.png --max-bytes 300000` exits 0. Cheaper substitute: hand-exported PNGs.
- [ ] Commit: `brand: add app lineup strip`

**Test checkpoint:** `python scripts/check-image-asset.py docs/assets/github/lineup-dark.png --max-bytes 300000` exits 0.

## 4. README Brand Presentation

The README shows the banner and lineup with `<picture>` so they match the visitor's GitHub theme, then lists each app with its Microsoft counterpart and current status.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Add the banner and lineup `<picture>` blocks to `README.md`. Done when: both render on github.com in light and dark themes.

- [ ] Add a `<picture>` block to `README.md` with `prefers-color-scheme: dark` and light `source` elements for the banner and an `alt` naming the suite. Done when: the rendered README on github.com switches banner with the theme. Cheaper substitute: one image with a transparent background.
- [ ] Add the lineup `<picture>` block and an app table (name, Microsoft counterpart, status) to `README.md`, rows at most 100 characters. Done when: the table lists six apps matching `docs/brand/NAMES.md`. Cheaper substitute: an image-only lineup with no text for screen readers.
- [ ] Add a CI status badge for `.github/workflows/ci.yml` to `README.md`. Done when: the badge renders the current run state. Cheaper substitute: a static "passing" badge.
- [ ] Commit: `docs: present suite branding in README`

**Test checkpoint:** `python scripts/check-design-doc.py README.md --require "Rizonesoft Office"` exits 0 (**Corrected 2026-10-20:** the command had no value after `--require`, which the checker refuses), and `(Select-String -Path README.md -Pattern "prefers-color-scheme").Count` is at least 2.

## 5. Upload Social Preview and Avatar

GitHub accepts the social preview only through repository Settings, and the organisation avatar through organisation Settings. Both are owner actions on a public profile.

**Phase:** 1
**Needs:** operator
**Surface:** no

**Build order:**

1. Upload `docs/assets/github/social-preview.png` in repository Settings. Done when: `gh repo view --json openGraphImageUrl` returns a `repository-images` URL.
2. Decide and upload the organisation avatar. Done when: the decision is recorded in `docs/brand/NAMES.md` under `## GitHub`.

- [ ] Upload `docs/assets/github/social-preview.png` at Settings, General, Social preview for the repository. Done when: `gh repo view --json openGraphImageUrl` returns a `repository-images.githubusercontent.com` URL. Cheaper substitute: relying on GitHub's auto-generated card.
- [ ] Record whether the `rizonesoft` organisation avatar changes to the suite mark or stays the company mark in `docs/brand/NAMES.md` under `## GitHub`. Done when: the decision and date are recorded. Cheaper substitute: replacing the company avatar without asking.
- [ ] Commit: `brand: record GitHub avatar decision`

**Test checkpoint:** `gh repo view --json openGraphImageUrl --jq .openGraphImageUrl` prints a URL containing `repository-images`.

## Verification

- The README on github.com shows the correct banner and lineup in both light and dark themes.
- Pasting the repository URL into a link-preview tool shows the social preview image.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
