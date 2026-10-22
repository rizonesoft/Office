# Naming clearance

Per chosen name, the register searches (the knockout screen, D01 T01 §4) and the availability of its domain, GitHub and package identifiers (D01 T01 §5). It is a screen, not legal clearance; buying or reserving anything is the owner's call.

## Availability

Checked 2026-10-22. Each method was proven on a known-taken name first (`google.app` and `google.dev` by RDAP, the `firefox` Homebrew cask and LibreOffice's Flathub id each answered 200), so a 404 here means the registry holds no record of the name. That is not a promise it can be claimed: a registry may reserve or premium-price a name it has no record of, so each "not registered" below is confirmed only when the owner reserves it.

### Domains

Checked by RDAP, the registration data protocol that replaces `whois` (Verisign for `.com`, Google Registry for `.app` and `.dev`): HTTP 200 is a registered domain, 404 one with no registration record, which a registrar must still confirm (reserved and premium names exist).

| Domain | Result | Status |
| --- | --- | --- |
| `rizonesoft.com` | 200 | owned (the owner's site, published by Rizonetech (Pty) Ltd.) |
| `rizonesoftoffice.com` | 404 | not registered |
| `rizonesoft.app` | 404 | not registered |
| `rizonesoftoffice.app` | 404 | not registered |
| `rizonesoft.dev` | 404 | not registered |
| `rizonesoftoffice.dev` | 404 | not registered |

The suite already lives under the owned `rizonesoft.com`, which lists Rizonesoft Office among the owner's products.

### GitHub

Checked with `gh api <path>`, authenticated as `rizonesoft`, a user account, with a classic OAuth token whose scopes include `repo` (the `X-OAuth-Scopes` response header lists `delete_repo, gist, read:org, repo, workflow`). The `repo` scope covers every private repository the account owns, and the same token lists 4 of them (`gh api user/repos?visibility=private`), so a private `rizonesoft/rizonesoft-office` would answer 200, not 404.

| Name | Result | Status |
| --- | --- | --- |
| Account `rizonesoft` (a user account) | 200 | owned (hosts this repository) |
| Repository `rizonesoft/Office` | 200 | owned (this repository, a working codename) |
| Repository `rizonesoft/rizonesoft-office` | 404 | does not exist |
| Account or organisation `rizonesoft-office` | 404 | no account |

### Packages

The suite is Windows only (the owner's decision of 2026-10-20, recorded in D00 T02), so winget is the registry that matters; Homebrew and Flathub are recorded so the names stay known if that changes. Each app's ids follow one pattern per registry: winget `Rizonesoft.<App>`, Homebrew cask `rizonesoft-<app>`, Flathub `com.rizonesoft.<app>`, as in [NAMES.md](./NAMES.md).

| Name | winget | Homebrew cask | Flathub |
| --- | --- | --- | --- |
| Suite (`Rizonesoft.Office`) | not listed | no cask | no app |
| Write | not listed | no cask | no app |
| Grid | not listed | no cask | no app |
| Stage | not listed | no cask | no app |
| Flow | not listed | no cask | no app |
| Plan | not listed | no cask | no app |
| Mail | not listed | no cask | no app |

winget (v1.29): `winget search --id Rizonesoft. --source winget` lists one package under the owner's publisher name, `Rizonesoft.Notepad3`, so the `Rizonesoft` publisher prefix is the owner's and none of the seven ids above exists. Homebrew: `https://formulae.brew.sh/api/cask/<name>.json` answered 404 for each. Flathub: `https://flathub.org/api/v2/appstream/<id>` answered 404 for each.

Microsoft Store: not checked here. A Store name can be checked and reserved only in Partner Center, under the owner's developer account; D01 T01 §9 owns it.
