---
name: local-tool-safety
description: Use when adding, reviewing, or invoking Conclave local tools, Windows/Linux/WSL integrations, connector-backed workflows, automation launchers, CLI wrappers, or any operation that might send outbound data, delete data, change infrastructure, modify accounts, run SQL writes, install tools, or use discovered executable paths.
---

# Local Tool Safety

## Rule

Local, reversible work proceeds without asking. Ask the operator once before anything that sends, deletes or changes something outside the repository: mail, production, Azure/M365, SQL writes, dropping data, credentials. Sudo commands are handed to the operator as `! sudo ...`; never store or guess the sudo password.

Detailed checklist: `references/local-tool-capability-safety.md`.

## Required Pattern

When implementing or using a local tool integration:

1. Resolve capability, not path.
2. Keep discovery output bounded: resolve the executable, inspect its version, and query only the relevant subcommand help or needed flags. Do not dump an entire help manual when a targeted query is sufficient.
3. Prefer explicit config, then discovery, then setup-required state.
4. Prefer global/user-level installs for vendor tools, CLIs, runtimes, package managers, database clients, and desktop apps.
5. Keep only Conclave-specific scripts, wrappers, schemas, config templates, hooks, tests, and docs in the repo.
6. Store discovered paths only in local ignored config.
7. Report health plainly: available, missing, degraded, auth-required, or blocked.
8. Run safe read/open/inspect workflows directly.
9. For work that sends, deletes or changes something outside the repository, show the exact operation and ask the operator once.
10. If a privileged step is needed, hand the operator the `! sudo ...` command and continue independent work.

## Risk Guide

- Low: open a repo in VS Code, open a local terminal, read a vault, read connector inventory, tail logs.
- Medium: create local notes, generate drafts, create non-public local files.
- High: send email, publish output, write outside the repository or vault, update tickets, change tool configuration.
- Critical: SQL writes, DNS changes, Azure firewall/NSG/resource changes, MS365/Entra user or license changes, credential handling, billing/accounting changes, production deploys.

## Implementation Checks

- No hardcoded `/home/<user>/...`, `/mnt/c/Users/<user>/...`, or `C:\Users\<user>\...` paths in app logic.
- No secret values in logs, UI or test snapshots.
- No OS sudo password in `.secrets`, environment files, logs, or memory notes.
- Missing optional tools produce setup guidance, not crashes.
- Host LAN ports on `conclave-srv` stay in `scripts/conclave-srv-lan-ingress.json`. Probe with `pnpm test:conclave-srv-lan`. Never iptables-only, never a WAN allow, never `ufw reset` or `ufw enable` without that set.
