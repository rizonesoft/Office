# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Fail when any NuGet package in the repository's solution, direct or transitive, has a known vulnerability.

    python scripts/check-vulnerable-packages.py [--report FILE]

It restores the solution, then reads `dotnet list package --vulnerable --include-transitive --format json`
(the advisories nuget.org publishes). `--report` reads a saved report instead of running dotnet.

The solution is the one `.slnx` file at the repository root. Until the foundation plan (D03 T01 §12) creates it
there is nothing to restore, and the run says so and passes; two solution files are refused.

Exit 0: no vulnerable package, or no solution yet. Exit 1: one or more, listed by project, package, version, and
severity. Exit 2: dotnet failed or reported a problem, or the solution is ambiguous, so nothing was verified.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NO_WINDOW = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW: a scheduled run opens no console


def findings(report: dict) -> list[str]:
    out = []
    for project in report.get("projects", []):
        name = os.path.basename(project.get("path", "").replace("\\", "/"))
        for framework in project.get("frameworks", []):
            for kind in ("topLevelPackages", "transitivePackages"):
                for package in framework.get(kind, []):
                    for vuln in package.get("vulnerabilities") or []:
                        out.append(f"{name} ({framework.get('framework')}): {package.get('id')} "
                                   f"{package.get('resolvedVersion')} {vuln.get('severity')} {vuln.get('advisoryurl')}"
                                   f"{' (transitive)' if kind == 'transitivePackages' else ''}")
    return sorted(set(out))


def verdict(report: dict) -> tuple[int, str]:
    if report.get("problems"):
        return 2, "dotnet reported problems, so nothing was verified: " + json.dumps(report["problems"])[:600]
    if not report.get("projects"):
        return 2, "the report lists no project, so nothing was verified"
    found = findings(report)
    if found:
        return 1, f"{len(found)} vulnerable package reference(s):\n" + "\n".join(found)
    return 0, f"no vulnerable package in {len(report['projects'])} project(s)"


def main(argv: list[str]) -> int:
    try:
        if argv[:1] == ["--report"] and len(argv) == 2:
            with open(argv[1], encoding="utf-8-sig") as fh:
                report = json.load(fh)
        elif argv:
            print(__doc__.split("\n\n")[0], file=sys.stderr)
            return 2
        else:
            solutions = sorted(name for name in os.listdir(REPO) if name.endswith(".slnx"))
            if not solutions:
                print("no solution in the repository yet (D03 T01 §12 creates it), so there is nothing to check")
                return 0
            if len(solutions) > 1:
                print(f"check-vulnerable-packages: more than one solution at the root: {solutions}", file=sys.stderr)
                return 2
            SOLUTION = solutions[0]
            restore = subprocess.run(["dotnet", "restore", SOLUTION, "-v", "q", "-nologo"], cwd=REPO,
                                     capture_output=True, text=True, timeout=1200, creationflags=NO_WINDOW)
            if restore.returncode:
                print("check-vulnerable-packages: restore failed:\n" + restore.stdout[-2000:] + restore.stderr[-2000:],
                      file=sys.stderr)
                return 2
            listed = subprocess.run(["dotnet", "list", SOLUTION, "package", "--vulnerable", "--include-transitive",
                                     "--format", "json"], cwd=REPO, capture_output=True, text=True, timeout=600,
                                    creationflags=NO_WINDOW)
            if listed.returncode:
                print("check-vulnerable-packages: dotnet list failed:\n" + listed.stderr[-2000:], file=sys.stderr)
                return 2
            report = json.loads(listed.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"check-vulnerable-packages: {exc}", file=sys.stderr)
        return 2
    code, line = verdict(report)
    print(line, file=sys.stdout if code == 0 else sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
