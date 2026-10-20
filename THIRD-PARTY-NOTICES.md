# Third-Party Notices

Rizonesoft Office is licensed under GPL-3.0-or-later. This file lists the third-party material the repository carries, with the licence each one requires us to reproduce. D00 T02 owns this file and adds the bundled components.

## Data sources

### Office control identifier baseline

- What: the control identifier lists for Word, Excel, PowerPoint, Visio, Project and Outlook (Current Channel), converted by `scripts/import-office-ids.py` into `design/inventory/<app>/baseline.json`.
- Kept: identifiers, control types, positions (placement, tab set, tab, group, parents, row order) and policy ids. No labels or descriptions exist in the source, and none were added.
- Upstream: the OfficeDev `office-fluent-ui-command-identifiers` repository on GitHub, pinned at commit `b230a0df45036b2d5e8b49ebf368b3f90ada8d63` (committed 2024-03-18), imported 2026-10-20.
- Licence: MIT. The notice below is reproduced as the licence requires.

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
