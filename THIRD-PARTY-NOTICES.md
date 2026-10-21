# Third-Party Notices

Rizonesoft Office is licensed under GPL-3.0-or-later. This file lists the third-party material the repository carries, with the licence each one requires us to reproduce. D00 T02 owns this file and adds the bundled components.

## Fonts

### Plus Jakarta Sans

- What: the Plus Jakarta Sans variable font, `design/fonts/plus-jakarta-sans/PlusJakartaSans[wght].ttf`, the suite's brand and interface typeface, bundled unmodified.
- Version: 2.071 (the font's own version string, `Version 2.071;gftools[0.9.30]`).
- Upstream: https://github.com/tokotype/PlusJakartaSans.
- Copyright: Copyright 2020 The Plus Jakarta Sans Project Authors (https://github.com/tokotype/PlusJakartaSans).
- Licence: OFL-1.1. The full licence text ships beside the font as `design/fonts/plus-jakarta-sans/OFL.txt` (also `LICENSES/OFL-1.1.txt`).
- Obligations: every copy of the font, in the repository and in each installer and MSIX package, carries the copyright line above and the OFL text; the font is never sold on its own; a modified version must be renamed and stays under OFL-1.1. The font declares no Reserved Font Name.

## Data sources

### Office control identifier baseline

- What: the control identifier lists for Word, Excel, PowerPoint, Visio, Project and Outlook (Current Channel), converted by `scripts/import-office-ids.py` into `design/inventory/<app>/baseline.json`.
- Kept: identifiers, control types, positions (placement, tab set, tab, group, parents, row order) and policy ids. No labels or descriptions exist in the source, and none were added.
- Upstream: the OfficeDev `office-fluent-ui-command-identifiers` repository on GitHub, pinned at commit `b230a0df45036b2d5e8b49ebf368b3f90ada8d63` (committed 2024-03-18), imported 2026-10-20.
- Licence: MIT. The notice below is the pinned commit's `LICENSE` file, reproduced exactly (its four-space indent included, line endings as LF), as the licence requires.

```text
    MIT License

    Copyright (c) Microsoft Corporation. All rights reserved.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE
```

## How this file is maintained

- Every component the repository carries or the product redistributes has one entry here before it lands, with what it is, its pinned version or commit, upstream, copyright, licence (as an SPDX identifier on a `- Licence:` line, which `scripts/check-spdx.py --allow` reads) and obligations.
- The gate for a new entry is the dependency licence policy D03 T01 §11 writes in `docs/specs/<date>-licensing-design.md`: a component whose licence that policy does not allow does not land.
- The Fluent UI System Icons, Windows App SDK and .NET runtime entries arrive with D00 T02 §6, once each is pinned and redistributed.
