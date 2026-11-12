---
id: gate-results-go-in-the-findings-record
applies: *
topics: review, process
roles: main
source: docs/reviews/00-workspace/D00-T05-s9.md#completion/finding-1
fix: 073c056
added: 2026-11-12
status: active
---
After a review's findings are repaired, the gates run again and their commands and results are written into the section's findings file, tied to the candidate they ran on; a commit message alone is not the record the next pass reads. Run them before writing the lines, and write what they printed: the one time the block was written first, a gate had failed and the text was false.
