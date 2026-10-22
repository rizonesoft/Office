# Contributing to Rizonesoft Office

Rizonesoft Office is built in the open. This guide covers the licence your work is released under, how to set up and test a clone, and how work is planned, reviewed and committed.

## Licence and agreement

Rizonesoft Office is licensed under the GNU General Public License, version 3 or (at your option) any later version (`GPL-3.0-or-later`); the full text is in [LICENSE](./LICENSE). By contributing, you release your work under the same licence.

Every source file states its licence in its first lines. Add these two lines at the top of each new `.py`, `.ps1`, `.sh`, `.cmake` or `CMakeLists.txt` file (after a `#!` line when there is one), with `//` in place of `#` for `.mjs` files and the C++ sources (`.cpp`, `.cppm`, `.ixx`, `.h`, `.hpp`, `.rc`, `.hlsl`), and an XML comment for `.manifest` files:

```text
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
```

`python scripts/check-spdx.py` refuses a source file without exactly one licence line, and CI runs it on every push; the copyright line is the convention every file follows, not a checked rule. Third-party material keeps its own licence and needs an entry in [THIRD-PARTY-NOTICES.md](./THIRD-PARTY-NOTICES.md) before it lands.

Outside contributions also need a signed contributor licence agreement, which keeps a commercial edition possible. Its text will live at `docs/legal/rizonesoft-cla.md` once it has been reviewed by a lawyer (D00 T02 §3); until then, a pull request from an outside contributor cannot be merged.

## Build and test

Rizonesoft Office runs on Windows. There is no application to build yet: the C++ projects arrive with the foundation plan. Today a clone carries the design tooling and its checks, and every pull request must pass them. From a clean clone, with Python 3.15, Git and PowerShell 7 (`pwsh`, which the automation installer tests need) on the path:

```powershell
git config core.hooksPath scripts/hooks          # the pre-commit hook refuses a TODO change with a stale plan
python -m pip install -r scripts/requirements.txt
python scripts/todo-graph.py validate
python scripts/todo-graph.py plan --check
python scripts/build-icons.py --check
python scripts/check-spdx.py
python -m reuse lint
python -m unittest discover -s scripts/tests
```

These are the steps CI runs in [.github/workflows/ci.yml](./.github/workflows/ci.yml). Read the test summary as well as its result: a test whose tool is missing (`pwsh`, for example) is skipped, not failed, so check the skip count before trusting a local pass.

## Workflow

Work is planned and built through the TODO system described in [docs/todo-workflow.md](./docs/todo-workflow.md): every change belongs to a section in `todo/`, and a section is marked done only by `scripts/todo-graph.py stamp` after an independent review. The working rules, including commit messages and writing style, are in [AGENTS.md](./AGENTS.md); line endings are set per path in [.gitattributes](./.gitattributes).

To propose a change, open a pull request against `main` that names the TODO section it implements.
