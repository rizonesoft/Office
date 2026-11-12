# Contributor agreements

Rizonesoft Office is free software under the GNU General Public License, version 3 or later. So that Rizonesoft can also offer the suite under other terms (a commercial edition, for example) without asking every contributor again, an outside contributor signs a contributor licence agreement once. You keep the copyright in your work; the agreement gives Rizonesoft a licence to it.

## Which agreement applies

- You contribute your own work, in your own time and name: the [individual agreement](./rizonesoft-cla.md).
- You contribute for a company or other organisation, or your employer owns what you write: an authorised person signs the [entity agreement](./rizonesoft-cla-entity.md) for it, which then covers its employees' contributions.
- You are employed and unsure who owns the work: section 3(c) of the individual agreement asks that your employer approve it or sign the entity agreement. Ask before you sign.

## Signing

You sign once, electronically, on your first pull request. A check on the pull request (CLA Assistant) posts a comment with a link to the agreement and records your signature against your GitHub account; the pull request can be merged once the check passes. Later pull requests from the same account need no new signature unless the agreement's text changes.

Until that check is installed on the repository (the owner installs it), a pull request from an outside contributor is not merged. To sign for an organisation, or by another means, open an issue titled "Contributor agreement" and Rizonesoft will reply with how.

## Work you do not own

The agreements cover work whose copyright you own. If your contribution includes work you do not own:

- Say so in the pull request, naming each such file or part, its author and its licence.
- Third-party work is accepted only under a licence compatible with `GPL-3.0-or-later`, keeps its own notices, and is listed in [THIRD-PARTY-NOTICES.md](../../THIRD-PARTY-NOTICES.md) in the same pull request.
- Work written by someone else who has not signed an agreement is submitted by that person, not on their behalf.

## Where the text comes from

Both agreements are the Harmony Contributor License Agreements, version 1.0, of the Project Harmony community (harmonyagreements.org), kept as published in [`harmony/`](./harmony/) and licensed under the Creative Commons Attribution 3.0 Unported License. `python scripts/build-contributor-agreements.py` builds each agreement from its template by filling in the choices and changing nothing else: the recipient (Rizonesoft), the outbound licence (the template's Option Five: any licence, and always also the licence the project uses on the day of the contribution), and the governing law (the Republic of South Africa). `python scripts/build-contributor-agreements.py --check` fails if an agreement differs from that build, so no clause can be added, dropped or reworded by hand.

## Review status

The owner approved both agreements on 2026-11-13 in the form committed here. No lawyer has reviewed them yet: the owner chose to bring them into force on the templates' own wording and to have them reviewed later. Each agreement's `## Review` section records this, and will record the review's date and firm.
