# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The github.com repository a clone's `origin` points at, so every `gh` call can name it explicitly.

`gh` picks its repository from GH_REPO, GH_HOST or its own defaults before the working directory, so a script that
reads or changes this repository's GitHub state names `--repo github.com/<owner>/<name>` (or `--hostname` for
`gh api`) from `origin` itself. Shared by scripts/merge_prs.py, scripts/ci-status.py and scripts/check-campaign-host.py.
"""
import re

HOST = "github.com"
# The URL forms git writes for a github.com repository, matched whole: the host must be exactly github.com.
ORIGIN_FORMS = (re.compile(r"https://(?:[^@/]+@)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?"),
                re.compile(r"git@github\.com:([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?"),
                re.compile(r"ssh://git@github\.com(?::22)?/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?"))


def parse(url):
    """`owner/name` for a github.com remote URL, or None. Callers never print the URL: it can carry a token."""
    for form in ORIGIN_FORMS:
        match = form.fullmatch(url.strip())
        if match:
            return f"{match.group(1)}/{match.group(2)}"
    return None


def repo_flag(repo):
    """The `--repo` value that pins both host and repository, whatever GH_REPO or GH_HOST say."""
    return f"{HOST}/{repo}"
