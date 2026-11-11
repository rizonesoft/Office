# Operating mode measurement, 2026-11-11

Decided by `python scripts/measure-modes.py decide` from `docs/experiments/operating-mode-2026-11-10.json` under the rule of D00 T03 §37: the lowest cost to an approved review among the arms that reached one on every section.

## Runs

| Run | Section | Arm | Cost | Reviews | Seconds | End |
| --- | ------- | --- | ---- | ------- | ------- | --- |
| run-6 | D00 T03 §29 | fable-alone | $2.70 | 1 | 856 | approved |
| run-4 | D00 T03 §29 | opus-alone | $1.98 | 2 | 655 | approved |
| run-5 | D00 T03 §29 | orchestrated | $4.25 | 2 | 1019 | approved |
| run-1 | D00 T03 §32 | fable-alone | $2.05 | 1 | 321 | approved |
| run-2 | D00 T03 §32 | opus-alone | $1.04 | 1 | 303 | approved |
| run-3 | D00 T03 §32 | orchestrated | $2.52 | 1 | 826 | approved |
| run-8 | D02 T01 §30 | fable-alone | $3.94 | 1 | 499 | approved |
| run-9 | D02 T01 §30 | opus-alone | $3.74 | 3 | 997 | approved |
| run-7 | D02 T01 §30 | orchestrated | $16.20 | 4 | 2625 | not-approved |

## Totals

| Arm | Cost | Reviews | Seconds | Eligible |
| --- | ---- | ------- | ------- | -------- |
| fable-alone | $8.69 | 3 | 1676 | yes |
| opus-alone | $6.76 | 6 | 1955 | yes |
| orchestrated | $22.97 | 7 | 4470 | no |

## Verdict

opus-alone, by the lowest cost to an approved review. The launcher starts the lead on `opus`.
