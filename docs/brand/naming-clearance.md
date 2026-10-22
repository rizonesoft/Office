# Naming clearance

Per chosen name, the register searches (the knockout screen, D01 T01 §4) and the availability of its domain, GitHub and package identifiers (D01 T01 §5). It is a screen, not legal clearance; buying or reserving anything is the owner's call.

## Availability

Checked 2026-10-22. Each check's method was proven on a known-taken name first (`google.app` and `google.dev` by RDAP, the `firefox` Homebrew cask and LibreOffice's Flathub id each answered 200), so a 404 here means the name is free in that registry.

### Domains

Checked by RDAP, the registration data protocol that replaces `whois` (Verisign for `.com`, Google Registry for `.app` and `.dev`): HTTP 200 is a registered domain, 404 an unregistered one.

| Domain | Result | Status |
| --- | --- | --- |
| `rizonesoft.com` | 200 | owned (the owner's site, published by Rizonetech (Pty) Ltd.) |
| `rizonesoftoffice.com` | 404 | available |
| `rizonesoft.app` | 404 | available |
| `rizonesoftoffice.app` | 404 | available |
| `rizonesoft.dev` | 404 | available |
| `rizonesoftoffice.dev` | 404 | available |

The suite already lives under the owned `rizonesoft.com`, which lists Rizonesoft Office among the owner's products.

### GitHub

Checked with `gh api <path>`.

| Name | Result | Status |
| --- | --- | --- |
| Organisation `rizonesoft` | 200 | owned (hosts this repository) |
| Repository `rizonesoft/Office` | 200 | owned (this repository, a working codename) |
| Repository `rizonesoft/rizonesoft-office` | 404 | available |
| Account or organisation `rizonesoft-office` | 404 | available |

### Packages

The suite is Windows only (the owner's decision of 2026-10-20, recorded in D00 T02), so winget is the registry that matters; Homebrew and Flathub are recorded so the names stay known if that changes. Each app's ids follow one pattern per registry: winget `Rizonesoft.<App>`, Homebrew cask `rizonesoft-<app>`, Flathub `com.rizonesoft.<app>`, as in [NAMES.md](./NAMES.md).

| Name | winget | Homebrew cask | Flathub |
| --- | --- | --- | --- |
| Suite (`Rizonesoft.Office`) | available | available | available |
| Write | available | available | available |
| Grid | available | available | available |
| Stage | available | available | available |
| Flow | available | available | available |
| Plan | available | available | available |
| Mail | available | available | available |

winget (v1.29): `winget search --id Rizonesoft. --source winget` lists one package under the owner's publisher name, `Rizonesoft.Notepad3`, so the `Rizonesoft` publisher prefix is the owner's and none of the seven ids above exists. Homebrew: `https://formulae.brew.sh/api/cask/<name>.json` answered 404 for each. Flathub: `https://flathub.org/api/v2/appstream/<id>` answered 404 for each.
