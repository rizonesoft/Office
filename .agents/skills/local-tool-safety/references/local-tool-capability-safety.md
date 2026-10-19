# Local Tool Capability Safety Rules

Conclave local tool integrations follow these rules:

1. Never assume a tool path; discover the capability.
2. Prefer global/user-level tool installs and keep repo-scoped assets only when they encode Conclave-specific behavior or reproducible commands.
3. Run safe local workflows and normal user-requested development edits inside the repository without repeated confirmation.
4. Ask the operator once before anything that sends, deletes or changes something outside the repository: mail, production, Azure/M365, SQL writes, dropping data, credentials.
5. Hand sudo commands to the operator as `! sudo ...`. Never configure blanket `NOPASSWD: ALL` and never store the OS sudo password.
6. Replace mock/sample/demo data with real data when the real source exists.

## Capability Resolution

- [ ] Prefer global/user-level installed tools for vendor CLIs, desktop apps, package managers, language runtimes, cloud tools, database clients, and third-party servers.
- [ ] Keep repo-scoped assets limited to Conclave-specific scripts, wrappers, schemas, config templates, hooks, tests, and docs.
- [ ] Do not vendor bulky tool binaries into git unless a documented reproducibility or compatibility exception exists.
- [ ] Prefer explicit config, then platform discovery, then a setup-required state.
- [ ] Store discovered paths only in ignored local config.
- [ ] Never hardcode user-specific absolute paths in app logic.

## Health States

`available`, `missing`, `degraded`, `auth-required`, `blocked`.

## Real Data

- [ ] Treat fixtures, seeds, mocks, and samples as demo/test data only, and label them clearly when rendered.
- [ ] Replace demo/test data with live data when available.
- [ ] Never show raw secret or credential values in the galaxy or anywhere else.

## Safe Direct Actions

- [ ] Open VS Code workspace, file, or diff.
- [ ] Open Windows Terminal or WSL shell.
- [ ] Read Obsidian vault files.
- [ ] Run connector health checks and read scoped inventory.
- [ ] Tail local logs.

## Ask Once First

- [ ] Install or upgrade tools through WinGet.
- [ ] Send email.
- [ ] Publish output.
- [ ] Write outside the repository and the vault.
- [ ] Change Azure resources, NSGs, firewall rules, reservations, or deployments.
- [ ] Change MS365, Exchange, Entra, users, mailboxes, groups, or licenses.
- [ ] Run SQL writes.
- [ ] Change DNS, billing, accounting, production hosting, or credentials.
- [ ] Drop or delete data outside the repository.

When asking, state the target, the exact command or API operation, the blast radius and the rollback.

## Host Network

- [ ] Host LAN TCP on `conclave-srv` matches `scripts/conclave-srv-lan-ingress.json`. Probe `pnpm test:conclave-srv-lan`. Never iptables-only, never WAN, never `ufw reset` or `ufw enable` without that set.
