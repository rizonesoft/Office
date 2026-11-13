---
id: an-ambiguity-is-counted-on-both-sides
applies: scripts/lib/*.py, scripts/*.py
topics: tooling, review
roles: main
source: docs/reviews/02-interface/D02-T01-s30.md#round-1/finding-2
fix: 54eb9ce
added: 2026-11-13
status: active
---
An ambiguity guard that looks at one side misses the other: the layout check refused two groups of one label in the inventory against one in the capture, and silently took the first of two in the capture against one in the inventory, hiding a lost control. When a tool pairs by a key that can repeat, compare the counts on both sides and refuse any mismatch other than absence. Test it in both directions.
