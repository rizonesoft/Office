---
schema_version: 1
id: portable-build-tools
domain: 00-workspace
status: active
title: "TODO-04 -- Portable Build Tools"
---

# TODO-04 -- Portable Build Tools

> **Goal:** A fresh clone gets every build tool the repository can carry (CMake, Ninja, sccache, vcpkg, and the LLVM tools clangd, clang-tidy and clang-format) with one command, at a version and SHA-256 pinned in a lock file, inside an ignored folder in the clone. Scripts, CI, the campaign launcher and the C++ language server use the tools from that folder and never from a machine install or `PATH`. Only what cannot be redistributed, Visual Studio's MSVC toolset and the Windows SDK, stays a host prerequisite.

> **Current state:** Measured 2026-11-10. No lock file, bootstrap script or tool folder exists. The owner decided on 2026-11-10 that build tools are repo scoped and portable and that Ninja and the tools that make the build fast are adopted (`docs/specs/2026-10-23-campaign-scope-design.md`, decision 23; `AGENTS.md`, Working rules), but the work existed only as notes inside two Phase 3 sections (D03 T01 §12 and §17), so it had no row in `todo/implementation-plan.md` and could not run before the first C++ code (the D03 T01 §2 prototype) needed it. On this PC `ninja` resolves to a WinGet install, `cmake` and `clangd` to the copies inside Visual Studio 2026, and `sccache` is not installed; none is pinned. `.gitignore` ignores `build/` and `scratch/` only. `scripts/start-campaign.ps1` and the `clangd-lsp` plugin (`.claude/settings.json`) take `clangd` from `PATH`. The build settings that need C++ code to measure (generator job pools, the compiler cache configuration, precompiled headers, link settings, build-time budgets) stay with D03 T01 §12 and the build foundation file D03 T01 §17 authors.

## Inputs

- `docs/specs/2026-10-23-campaign-scope-design.md`, decisions 23 (portable build tools) and 24 (no machine paths): the rules every section here implements.
- `AGENTS.md`, Working rules (build tools are repo scoped and portable) and Code intelligence (where `clangd` comes from): §4 updates both.
- The release pages of each tool, read when §1 runs, for the newest stable version, its download URL and its published checksum: Kitware CMake, `ninja-build/ninja`, `mozilla/sccache`, `microsoft/vcpkg` with the `vcpkg-tool` release its `scripts/vcpkg-tool-metadata.txt` names, and `llvm/llvm-project`.
- `scripts/tests/test_no_hardcoded_paths.py`: no tool written here names a drive, home or mount path.
- -> XREF: D03 T01 §2 -- the native prototype is the first consumer and builds with the tools from this folder
- -> XREF: D03 T01 §17 -- the build foundation file consumes this bootstrap instead of creating it
- -> XREF: T03 §11 -- the daily latest-stable checks cover the lock file this file creates

## Outcome

- `python scripts/bootstrap-tools.py` on a clone with an empty tool folder fetches every tool in `tools.lock.json`, verifies each SHA-256 before unpacking, and a second run downloads nothing.
- `python scripts/bootstrap-tools.py --check` exits 0 only when every installed tool matches the lock file, and a tampered archive is refused with nothing unpacked.
- CI and the campaign launcher run the same bootstrap, and `clangd` for the language server comes from the tool folder.

**Adjacency:** all=not-applicable (developer build tooling for this repository; no product records, settings or user documents)

**Adjacency rationale:** These sections fetch and locate build tools for the people and agents building the suite. They hold no user data, so none of the nine product keys applies.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Tool lock file and bootstrap script | -- | [ ] |
| 2 | §2 | Tool folder resolver | §1 | [ ] |
| 3 | §3 | Tool bootstrap in CI | §1 | [ ] |
| 4 | §4 | Launcher and clangd use the tool folder | §1, §2 | [ ] |

## 1. Tool Lock File and Bootstrap Script

> **Started:** 2026-11-12T02:45:00Z

One lock file names every carried tool, and one script turns it into a working tool folder. The script is the only thing that downloads: it is bounded, verifies before it unpacks, and leaves either a complete tool or nothing.

**Corrected 2026-11-12** (validation against the projects' release pages, read 2026-11-12 through the GitHub releases API): the newest stable releases are CMake 4.4.5 (`cmake-4.4.5-windows-x86_64.zip`, `-arm64.zip`), Ninja 1.13.2 (`ninja-win.zip`, `ninja-winarm64.zip`; no published checksum), sccache 0.19.0 (`sccache-v0.19.0-{x86_64,aarch64}-pc-windows-msvc.zip`, with published `.sha256` files), vcpkg registry tag 2026.10.16, whose `scripts/vcpkg-tool-metadata.txt` names vcpkg-tool 2026-09-26 (`vcpkg.exe`, `vcpkg-arm64.exe`), and LLVM 23.1.5 (`clang+llvm-23.1.5-{x86_64,aarch64}-pc-windows-msvc.tar.xz`). The vcpkg registry publishes no release asset, so its archive is GitHub's source zip of the tag, its hash computed from the download like every other. Unpacked members keep their paths inside the archive (`cmake-4.4.5-windows-x86_64/bin/cmake.exe`), and `bin` names folders relative to the tool's folder on that basis; an `exe` archive is placed as the single file it is.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `tools.lock.json` and its loader. Done when: a malformed lock file is refused with the reason.
2. Write `scripts/bootstrap-tools.py`. Done when: an empty tool folder is filled from fixture archives, a second run downloads nothing, and a wrong hash is refused.
3. Fill the lock file with the real pins and run it on this PC. Done when: every tool prints its pinned version from the tool folder.

- [ ] Add `.tools/` to `.gitignore`. Done when: `git check-ignore .tools/x` prints the path. Cheaper substitute: a tool folder outside the clone, which is a machine install by another name.
- [ ] Write the lock loader in `scripts/lib/tool_lock.py`: `tools.lock.json` at the repository root is an object keyed by tool name, each with `version` and an `archives` object keyed by host architecture (`x64`, `arm64`), each archive holding `url` (https only), `sha256` (64 lowercase hex), `size` (bytes), `format` (`zip`, `tar.xz` or `exe`), `keep` (the member paths or prefixes to unpack) and `bin` (the folders, relative to the tool's folder, that hold its programs). Done when: tests in `scripts/tests/test_bootstrap_tools.py` show an unknown key, a non-https URL, a malformed hash and a missing architecture each refused with exit 2 and the tool's name. Cheaper substitute: reading the file with no validation, which lets a typo become a download from the wrong place.
- [ ] Write the fetch step of `scripts/bootstrap-tools.py`: download an archive to a temporary file inside `.tools/` through an opener the tests replace, stop and refuse when more than `size` bytes arrive, and compare its SHA-256 with the lock file before anything is unpacked. Done when: a fixture archive with one changed byte is refused with exit 1, the temporary file is gone and the tool's folder does not exist. Cheaper substitute: verifying after unpacking, which runs the damage before the check.
- [ ] Write the unpack step: unpack only the `keep` members into `.tools/<name>-<version>.partial/`, refuse a member whose path is absolute, holds `..` or is a link pointing outside the folder, then rename the folder to `.tools/<name>-<version>/` and write `.tools/<name>-<version>/.installed.json` (the archive's SHA-256 and the lock entry it came from) through a temporary file and `os.replace`. Done when: a fixture archive holding `../escape.txt` is refused with nothing written outside `.tools/`, and a run interrupted before the rename leaves no folder that `--check` accepts. Cheaper substitute: unpacking in place, which leaves half a tool after a crash.
- [ ] Make the run idempotent and self-cleaning: a tool whose `.installed.json` matches the lock entry is skipped without a download, and a `.partial` folder or a folder for a version the lock file no longer names is removed. Done when: a test counts zero opener calls on a second run, and a folder for an old version is gone after a run on a newer lock entry. Cheaper substitute: downloading everything on every run.
- [ ] Add `--check` to `scripts/bootstrap-tools.py`: exit 0 only when every tool in the lock file has a folder whose `.installed.json` matches its entry and whose `bin` folders exist; otherwise exit 1 naming each tool that is missing or stale, and download nothing. Done when: tests show exit 1 after one `.installed.json` is deleted and exit 0 after the bootstrap runs again.
- [ ] Add `--only <name>` (repeatable) so one tool can be fetched alone. Done when: a test with two fixture tools and `--only` naming one installs only that one, and an unknown name exits 2.
- [ ] Pin vcpkg as two tools of the lock file, `vcpkg-registry` (the tag's source zip) and `vcpkg` (the `vcpkg.exe` the tag's `scripts/vcpkg-tool-metadata.txt` names), each with its own `version`, and add a `requires` key (`"vcpkg": ["vcpkg-registry"]`) that the loader checks names a tool of the file; a tool counts as installed only when every tool it requires is installed too, and the tool folder resolver (§2) sets `VCPKG_ROOT` to the registry's folder. Done when: tests show both installed together by one run, `--check` failing when either is missing or stale, and an unknown `requires` name refused with exit 2. **Corrected 2026-11-12:** added after the plan review (gap 1, P1): one archive per tool could not hold the registry and its separately versioned tool.
- [ ] Record in `.installed.json` the relative path, size and SHA-256 of every file the tool kept, and accept an installed tool (to skip it, or for `--check`) only when every recorded file is present with that size and hash; a tool whose payload is damaged or incomplete is removed and installed again. Done when: tests show `--check` exit 1 naming the tool after one program or one kept header is deleted or changed, and the next run repairing it. Cheaper substitute: trusting the receipt and the `bin` folders, which passes with a program deleted. **Corrected 2026-11-12:** added after the plan review (gap 2, P1).
- [ ] Write `.installed.json` inside the `.partial` folder before the rename, so a promoted folder always carries its receipt, and treat a destination that exists with a missing, malformed or stale receipt as damaged: rename it aside to `.tools/<name>-<version>.stale-<random>/`, promote the new folder, then remove the stale one. Done when: tests show a run interrupted after the rename (simulated by a destination with no receipt) and a lock entry changed at the same version each end with a correct installation. **Corrected 2026-11-12:** added after the plan review (gap 3, P2).
- [ ] Bound every download in time: a 60-second socket timeout for the connection and each read, and an overall deadline per archive (`--deadline`, default 30 minutes), after which the fetch stops with exit 1 naming the tool, the temporary file is removed and a later run starts again. Done when: fixture tests with an opener that stalls, one that ends early and one that passes the deadline each exit 1 with no temporary file left, and a second run with a good opener succeeds. **Corrected 2026-11-12:** added after the plan review (gap 4, P2).
- [ ] Refuse, with fixtures for each format (`zip`, `tar.xz`, `exe`): an archive larger than its `size` (stopped while it arrives), a member with an absolute path, a member holding `..`, and a link (symbolic or hard) whose target leaves the tool's folder; an `exe` archive is installed as its single file under its own name. Done when: each case exits 1 with nothing written outside `.tools/` and no folder `--check` accepts, and the good fixture of each format installs. **Corrected 2026-11-12:** added after the plan review (gap 5, P2): the named checkpoints did not prove these refusals.- [ ] Fill `tools.lock.json` with the newest stable release of CMake, Ninja, sccache, vcpkg (the registry at its release tag and the `vcpkg.exe` that tag's `scripts/vcpkg-tool-metadata.txt` names) and LLVM (`keep` limited to `clangd`, `clang-tidy`, `clang-format`, the libraries they load and `lib/clang/<version>/include`), for `x64` and `arm64`, each hash computed from the downloaded file and compared with the checksum the project publishes where it publishes one. Done when: `python scripts/bootstrap-tools.py` on this PC ends with every tool installed and `python scripts/bootstrap-tools.py --check` exits 0. Where a project ships no Arm64 Windows build, the `arm64` entry is the x64 archive and the entry says so in a `note` key. Cheaper substitute: copying hashes from a web page without downloading the file.
- [ ] Run each fetched program once from `.tools/` with its version flag (`cmake --version`, `ninja --version`, `sccache --version`, `vcpkg version`, `clangd --version`, `clang-tidy --version`, `clang-format --version`) and record the output lines in the commit body. Done when: each printed version equals the lock file's `version`.
- [ ] Add `python scripts/bootstrap-tools.py`, `tools.lock.json` and `.tools/` to the Build and test section of `CONTRIBUTING.md`. Done when: the section names all three and says the folder is ignored.
- [ ] Name the command in the build tools bullet of the Working rules in `AGENTS.md`. Done when: the bullet says the tools are fetched by `python scripts/bootstrap-tools.py` into `.tools/`.
- [ ] Commit: `tools: add the pinned build tool bootstrap`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_bootstrap_tools.py"` passes (the tests use fixture archives and never the network), and `python scripts/bootstrap-tools.py --check` exits 0 on this PC after one bootstrap run.

## 2. Tool Folder Resolver

Every script that starts a build tool asks one function where it is, and that function answers from the tool folder only. This is what keeps a machine's own Ninja or CMake from being used by accident.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write the resolver in `scripts/lib/tool_lock.py`. Done when: it returns a program's path inside `.tools/` and refuses when the tool is not installed.
2. Expose it on the command line. Done when: `python scripts/bootstrap-tools.py --where ninja` prints the path.

- [ ] Add `tool_path(program)` to `scripts/lib/tool_lock.py`: find the program in the `bin` folders of the installed tools the lock file names and return its absolute path, found from the repository's own location. Done when: a test with a fixture tool folder returns the fixture path while a different program of the same name sits first on `PATH`. Cheaper substitute: `shutil.which`, which returns whatever the machine has.
- [ ] Refuse in `tool_path` a program whose tool is missing or stale, with a message that names the tool and the command `python scripts/bootstrap-tools.py`. Done when: a test with an empty tool folder shows the refusal and the command in its text, and no fallback to `PATH`.
- [ ] Add `--where <program>` to `scripts/bootstrap-tools.py`, printing the path and exiting 0, or the refusal and exiting 1. Done when: a test shows both outcomes.
- [ ] Add `--bin-dirs` to `scripts/bootstrap-tools.py`, printing one installed `bin` folder per line for a caller that must prepend them to a child process's `PATH` (the launcher in §4, the CMake presets D03 T01 §17 authors). Done when: a test with two fixture tools prints both folders and nothing else.
- [ ] Extend `scripts/tests/test_no_hardcoded_paths.py` to cover `scripts/bootstrap-tools.py` and `scripts/lib/tool_lock.py` if its file list does not already include them. Done when: the test names both files among those it scanned, and a drive path added to either makes it fail.
- [ ] Commit: `tools: resolve build tools from the tool folder only`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_bootstrap_tools.py"` passes with the resolver tests among them, and `python scripts/bootstrap-tools.py --where ninja` prints a path under `.tools`.

## 3. Tool Bootstrap in CI

CI builds with the same pinned tools as this PC. A cache keyed on the lock file keeps a run from downloading them again, and the cache can never stand in for the check.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Add the cache and the bootstrap to `.github/workflows/ci.yml`. Done when: a pushed run shows the bootstrap step and `--check` passing.
2. Prove the cache is used. Done when: a second run on the same lock file restores the cache and the bootstrap step downloads nothing.

- [ ] Add to the `gates` job of `.github/workflows/ci.yml` an `actions/cache` step for `.tools/` keyed on the runner's operating system and architecture and the hash of `tools.lock.json`, with the action pinned to a commit SHA like the workflow's other actions. Done when: the step is in the file and the key holds all three parts. Cheaper substitute: a key without the lock file's hash, which serves old tools after a pin moves.
- [ ] Add a step that runs `python scripts/bootstrap-tools.py` and then `python scripts/bootstrap-tools.py --check` after the cache step. Done when: the pushed run shows both commands and exit 0. Cheaper substitute: skipping the bootstrap on a cache hit, which trusts a cache nobody verified.
- [ ] Add a step that prints each tool's version through `python scripts/bootstrap-tools.py --where <program>` and the program's version flag. Done when: the run log shows every version in `tools.lock.json`.
- [ ] Push and read the run with `python scripts/ci-status.py`. Done when: the run on the pushed HEAD is green and its log shows the bootstrap downloading each tool.
- [ ] Read the bootstrap step of the next push's run on the same `tools.lock.json` (the review record's commit will do). Done when: that log shows the cache restored and no download line, quoted in the section's findings file. Cheaper substitute: assuming the cache works because the step exists.
- [ ] Commit: `ci: bootstrap the pinned build tools behind a cache`

**Test checkpoint:** `python scripts/ci-status.py` reports the `ci.yml` run on the pushed HEAD green, and that run's log holds the `--check` step with exit 0.

## 4. Launcher and clangd Use the Tool Folder

The campaign starts with the tools in place, and the C++ language server is the pinned `clangd`, not whichever one a machine has. A failed bootstrap never stops a start: the sections that need a tool run the bootstrap themselves and fail at their own gate.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Run the bootstrap from `scripts/start-campaign.ps1` and put the tool folders first on the session's `PATH`. Done when: `-DryRun` names the `clangd` the session would use.
2. Update the documents that say where `clangd` comes from. Done when: `AGENTS.md` names the tool folder.

- [ ] Run `python scripts/bootstrap-tools.py` in `scripts/start-campaign.ps1` before the host readiness check; when it fails, print one yellow line naming the failure and carry on. Done when: a test in `scripts/tests/test_start_campaign.py` shows the call before the host check and no `exit` on its failure path. Cheaper substitute: stopping the start on a failed download, which blocks every section that needs no tool.
- [ ] Prepend each line of `python scripts/bootstrap-tools.py --bin-dirs` to `$env:PATH` for the launcher's process, so the `clangd-lsp` plugin and every command the session starts find the pinned tools first. Done when: `pwsh scripts/start-campaign.ps1 -DryRun` prints a `clangd:` line whose path is under `.tools`, and a test asserts the line is printed. Cheaper substitute: editing the user's `PATH`, which changes the machine.
- [ ] Print in the same place, when the tool folder holds no `clangd`, the `clangd` that `PATH` gives or `clangd: none`, without failing. Done when: the test covers the line for an empty tool folder.
- [ ] Rewrite the second bullet of Code intelligence in `AGENTS.md`: `clangd` comes from `.tools/` after `python scripts/bootstrap-tools.py`, the launcher puts it on the session's `PATH`, and a session started any other way runs `python scripts/bootstrap-tools.py --bin-dirs` and prepends the result. Done when: the bullet no longer names Visual Studio's LLVM component as the source.
- [ ] Update decision 23 in `docs/specs/2026-10-23-campaign-scope-design.md` to cite this file's sections in place of "D03 T01 §12 and §17" for the bootstrap, keeping §12 and §17 for the build settings. Done when: the decision names `D00 T04 §1 to §4`.
- [ ] Commit: `campaign: start with the pinned tools and the pinned clangd`

**Test checkpoint:** `python -m unittest discover -s scripts/tests -p "test_start_campaign.py"` passes, and `pwsh scripts/start-campaign.ps1 -DryRun` prints a `clangd:` line with a path under `.tools`.

## Verification

- On a clone with an empty `.tools/` folder, `python scripts/bootstrap-tools.py` followed by `python scripts/bootstrap-tools.py --check` exits 0, and a second bootstrap run downloads nothing.
- The `ci.yml` run on the pushed HEAD is green with the bootstrap and `--check` steps in its log.
- `pwsh scripts/start-campaign.ps1 -DryRun` names a `clangd` under `.tools`.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
