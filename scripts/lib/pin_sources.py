# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Read release metadata for the pin automations: JSON over HTTPS, with a typed failure for "could not check".

A GitHub API request carries `GITHUB_TOKEN` from the environment when it is set (the unauthenticated limit is 60
requests an hour); the token is sent only to api.github.com and never printed. Ported from RectoPDF (2026-10-21).

Stdlib only.
"""
import json
import os
import re
import urllib.request


class Unreadable(Exception):
    """A source could not be read; the check exits 2 (cannot check) rather than reporting a stale pin."""


def fetch_json(url, opener=urllib.request.urlopen, agent="office-pins"):
    headers = {"Accept": "application/json", "User-Agent": agent}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with opener(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # any network or decode failure means the source could not be read
        raise Unreadable(f"{url.split('?')[0]}: {type(exc).__name__}: {exc}") from None


def version_key(text):
    """A numeric sort key for a dotted version ("v7.0.1", "3.15.0"); None when it is not purely numeric."""
    match = re.fullmatch(r"v?(\d+(?:\.\d+)*)", str(text).strip())
    return tuple(int(part) for part in match[1].split(".")) if match else None

