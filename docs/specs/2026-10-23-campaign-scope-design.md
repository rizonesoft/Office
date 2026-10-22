# Campaign scope and unattended-run decisions

Recorded 2026-10-23 from the owner's answers of 2026-10-22, given in one session before the first unattended `process-plan` campaign so the run never has to stop and ask. Every TODO section these decisions touch cites this record. A later change of mind is a new dated decision here, never an edit of an old one.

## Context

The suite moved on 2026-10-22 from WinUI 3 in C# on .NET 11 to native C++ (C++23 on MSVC `/std:c++23preview`, moving to C++26 once MSVC ships a stable flag for it) with our own GUI toolkit on Win32, Direct2D and DirectWrite, Windows only (D03 T01 §1, §2). The owner wants to start one campaign and come back to a finished, production-ready suite after days, weeks or months. At the time of the record the plan held 95 sections, 36 stamped, and stopped at Phase 3: the platform, the six apps, interoperability and release (Phases 4 to 7) had no sections, and 22 open sections waited on an owner, an operator, Office captures or a display session.

The owner also asked that Outlook (classic), Visio and Project, whose interfaces look dated beside Word, Excel and PowerPoint, be brought up to the same standard.

## Options

Each question was asked with a recommended option first. The options weighed:

| Question | Options considered |
| --- | --- |
| Run host | This PC unlocked; this PC with captures parked; a dedicated VM |
| Keep-alive | Reinstate the keep-alive task; resume by hand |
| Sign-offs | Reviewer signs and the owner audits later; block until the owner signs |
| Outward actions | Push, merge and draft releases; also publish; local commits only |
| Modernisation | Same commands, Word-grade design; redesign to new Outlook and web; restyle only |
| Microsoft cloud | Own equivalents; Microsoft APIs where public; exclude all |
| Cloud scope | Graph files and mail without co-authoring; co-authoring too; local and IMAP only |
| Macros | Preserve now with a VBA runtime last; preserve only; VBA in each app |
| Minimum OS | Windows 11 24H2; Windows 11 22H2; Windows 10 22H2 and 11 |
| UI languages | English ready to translate; English plus 10; the full Office set |
| Signing | Cloud signing in CI; Store-signed MSIX only; unsigned for now |
| Updates | GitHub-hosted without telemetry; opt-in telemetry; no in-app updates |
| Cadence | A draft per app with 1.0 at the end; one draft at the end |
| Store | Store-ready with a manual listing; no Store |
| Toolchain | The owner runs one elevated install now; park until installed |

## Decision

Owner, 2026-10-22, in session:

1. **Run host:** this PC, signed in and unlocked, with sleep and screen lock off. Microsoft 365 Apps (Word, Excel, PowerPoint, Outlook classic), Visio and Project stay installed for the Phase 2 captures, and nobody uses the PC while a capture section runs.
2. **Keep-alive:** none. The owner resumes a stopped campaign by hand, which keeps the freedom to stop and start it at will. The run guard, Stop hook and in-session heartbeat stay as they are.
3. **Sign-offs:** the pinned independent reviewer signs off the icon review (D01 T02 §7) and the mockups (D02 T02 §14) against their briefs; each sign-off is recorded with its evidence, and the owner audits it later and may reopen it.
4. **Outward actions:** the campaign pushes to `main`, merges green dependency pull requests under the existing rule, and creates draft GitHub releases. It never publishes a release.
5. **Modernisation:** Outlook, Visio and Project keep every inventoried command in its tab and group, and take the Word, Excel and PowerPoint design: title bar with search, Fluent glyphs, rounded controls, Mica, dark mode, the Simplified Ribbon option, Backstage, panes, dialogs and status bar. A layout changes only where Word, Excel or PowerPoint has a newer pattern for the same job, and each change is recorded in `design/SPEC.md`.
6. **Microsoft cloud features:** each gets a working equivalent of our own: an Assistant pane on a provider the user configures (Anthropic, OpenAI or a local model, off by default), Windows speech for dictation, open image libraries, a local grammar engine. A feature with no possible equivalent is marked excluded in the inventory with its reason, never left as a dead control.
7. **Cloud scope for 1.0:** OneDrive and SharePoint open and save with AutoSave through Microsoft Graph; Mail on Microsoft 365 and Outlook.com (Graph), Gmail (Google OAuth), iCloud and any IMAP and SMTP server, with CalDAV and CardDAV. Real-time co-authoring comes after 1.0. The owner registers a Microsoft Entra application and a Google OAuth client; until then only the sections that need them wait.
8. **Macros:** VBA projects always survive save. A sandboxed VBA-compatible runtime and editor with Trust Center rules is the final milestone, after all six apps reach parity.
9. **Minimum OS:** Windows 11 24H2 and later, x64 and Arm64.
10. **UI languages:** English (United States) in 1.0, with every string externalised, right-to-left mirroring proven with a pseudo-locale, and translation files ready for contributors. Documents work in every language.
11. **Signing:** unsigned for now. Release sections that need a signature wait on an owner decision; everything else ships unsigned drafts.
12. **Updates and diagnostics:** the Inno Setup build checks GitHub Releases for updates; crash dumps stay on the user's PC, and the user may attach one to a pre-filled GitHub issue. No telemetry and no Rizonesoft service.
13. **Release cadence:** a draft preview release per app as its milestone passes (the first app first), and the suite's 1.0 draft when all six apps and the interoperability gates pass.
14. **Store:** no Microsoft Store. The MSIX package waits on signing (11); the Inno Setup installer is the channel.
15. **Toolchain:** the owner runs one elevated command before the campaign starts, adding the LLVM clang tools to Visual Studio 2026 18.11 (the C++ desktop workload, the Arm64 tools, CMake, vcpkg and the Windows SDK 10.0.26100 were already installed on 2026-10-23).

## Consequences

- The plan's acceptance bar names the modernised positions and recorded exclusions (`todo/plan.json`).
- D01 T02 §7 and D02 T02 §14 lose their `owner-decision` Need; D01 T03 §5 (an operator upload) moves to Phase 99; D01 T01 §9 records that there is no Store.
- D02 T02 §10, §11 and §12 specify the modernised Visio, Project and Outlook surfaces; D02 T01 §28 adds a disposition to inventory records, and D03 T01 §14 decides each cloud feature's equivalent or exclusion.
- D03 T01 §1, §7, §8 and §9 carry decisions 7 to 9, 11 and 14; §15 and §16 record decisions 10 and 12; §17 to §27 author the platform, engine, six app, interoperability, VBA and release domains to a written contract, and §13 proves every inventory record is owned.
- D00 T03 §12 adds a host readiness check the campaign runs before it starts and at each phase, so an unattended run parks with a reason instead of failing on a locked screen or a missing tool.
- Sections that need the Entra or Google registration carry the `operator` Need, and signing sections carry `owner-decision`; a campaign takes every other ready row and leaves those for the owner's return.
