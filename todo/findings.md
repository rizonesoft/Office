# Findings

Unscheduled defects noticed while working on another section. Record each entry with `file:line` and strike it with its `DNN TNN §N` reference once scheduled via `add-todo`.

- 2026-10-23: bare program names (git, gh, 	askkill) are launched with the repository as the working directory, where Windows searches first, so a planted git.exe would run: .conclave/automations/run.py:105, scripts/campaign_guard.py:622, scripts/check-spdx.py:46, scripts/lib/pin_proposal.py:30, scripts/merge_prs.py:118 and its other git/gh calls. Fixed for 	odo_graph, eview-dispatch kill_tree and lert.py in D00 T03 §12 (review rounds 2, 6, 7); the rest should resolve each tool through ind_cli or its System32 path.
