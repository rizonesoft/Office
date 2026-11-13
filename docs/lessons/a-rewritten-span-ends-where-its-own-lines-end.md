---
id: a-rewritten-span-ends-where-its-own-lines-end
applies: scripts/lib/*.py, scripts/*.py
topics: tooling, review
roles: main
source: docs/reviews/02-interface/D02-T01-s29.md#round-1/finding-1
fix: da1e8e0
added: 2026-11-13
status: active
---
A parser that looks ahead for a terminator swallows whatever follows when the terminator is missing: a layout block with its closing fence left out ran on to the next fence, and the rewrite replaced the instructions and the block between. Before a tool rewrites a span it parsed, bound the span by structure: end it at the first line its generator could not have written (a blank line, the next header, another fence) and refuse the unit. Test the rewrite on a file with each terminator missing and require every other byte unchanged.
