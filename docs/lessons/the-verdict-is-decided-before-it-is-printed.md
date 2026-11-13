---
id: the-verdict-is-decided-before-it-is-printed
applies: scripts/*.py
topics: tooling, review
roles: main
source: docs/reviews/02-interface/D02-T01-s22.md#round-1/finding-1
fix: 2676bcd
added: 2026-11-13
status: active
---
An exit code is the answer and printing is only its report. A handler added so a report piped to head would end quietly returned success from a failing check once the reader closed the pipe. Decide the verdict into a value before writing a line, send refusals to stderr first, and let no output error improve the code: a reader that stopped listening ends the writing, any other write failure can only add a failure. Test a failing check with its output pipe closed, as a real process, on each platform it runs on.
