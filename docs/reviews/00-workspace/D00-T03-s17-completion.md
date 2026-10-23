# Completion review: D00 T03 §17

## Round 1: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-23T11:42:50Z
- Effort: medium
- Lines: 17
- Digest: 373c00ed63581e52

SECTION: D00 T03 §17
PURPOSE: completion
CONTRACT: sha256:a93affb451087afe92e54174dff91f93e1c36da8f26c9e16cdc422de7147e6b3

1. **P2: Reconciliation does not require fresh remote history.** `origin/main` is a local tracking ref. A dependency merge followed by a failed pull or session death can leave it behind GitHub, precisely when reconciliation is needed. **Remedy: extend** §17 to fetch `main` before enumeration, bound the operation, and route fetch failure through `ci-unknown`. Add a fixture where the remote has advanced beyond the local tracking ref.

2. **P2: The first-run baseline is undefined.** “After the newest head recorded `ci-green`” supplies no starting point when no run file contains that record. A fresh campaign could fail, return nothing, or traverse unrelated historical runs. **Remedy: extend** §17 with an explicit bootstrap policy, including the historical coverage it establishes, and fixtures for absent and empty run files with no green marker.

3. **P2: Discovery failure has no defined campaign outcome.** §15 handles failure to read the status of a known SHA. It does not define what happens when §17 cannot discover the SHAs, read a prior run file, or finish enumerating workflow runs. “Act on each listed commit” permits an empty or partial result to let work continue. **Remedy: extend** §17 to distinguish successful empty enumeration from incomplete discovery, require complete pagination over the selected history, and return a failure that invokes §15’s retry and park rules before any row is claimed. Test unavailable discovery, unreadable records, partial pagination and successful empty results.

4. **P2: The newest green record can conceal an unchecked earlier push head.** Suppose A and B were separate pushes, and B received a `ci-green` record through a direct `HEAD` gate while A was never reconciled. Starting strictly after B permanently omits A. B covers implementation commits beneath it, but does not prove that A’s separate push run was checked. **Remedy: extend** §17 to advance reconciliation coverage only across push heads with recorded outcomes or an explicit repair resolution. Test an unchecked A followed by a recorded-green B, while retaining the existing test that ordinary implementation commits receive no separate checks.

§15 owns individual status handling and repair, §18 owns the persistent recovery budget, and §19 owns guard and skill gate checks. Those responsibilities do not resolve the discovery gaps above.

COMPLETE: no
HIGHEST: P2
OVERALL: needs-attention

## Outcome (round 1)

1. extended
2. extended
3. extended
4. extended
