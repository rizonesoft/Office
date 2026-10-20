"""Report when .NET ships the GA SDK of the channel global.json pins, while the pin is still a prerelease.

    python scripts/check-sdk-ga.py [--feed FILE]

Exit 0: no GA SDK yet, or the pin is already GA (a newer prerelease than the pin is printed as information).
Exit 1: a GA SDK is out and global.json still pins a prerelease, so `D03 T01 §2` (move the pin to GA) is ready.
Exit 2: the release feed or global.json could not be read.

The feed is the release metadata for the channel (major.minor of the pinned version), the same index `dotnet-install`
reads, taken from the .NET repository on GitHub; `--feed` reads a saved copy instead.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
# The release metadata `dotnet-install` reads, as the .NET repository on GitHub publishes it.
FEED = "https://raw.githubusercontent.com/dotnet/core/main/release-notes/{channel}/releases.json"


def sdk_versions(feed: dict) -> list[str]:
    """Every SDK version the channel feed lists, newest release first."""
    out = []
    for release in feed.get("releases", []):
        for sdk in [release.get("sdk") or {}] + list(release.get("sdks") or []):
            version = sdk.get("version")
            if version and version not in out:
                out.append(version)
    return out


def verdict(pin: str, feed: dict) -> tuple[int, str]:
    versions = sdk_versions(feed)
    if not versions:
        return 2, "the release feed lists no SDK"
    ga = [v for v in versions if "-" not in v]
    if "-" not in pin:
        return 0, f"global.json pins GA SDK {pin}; nothing to move"
    if ga:
        return 1, (f".NET {feed.get('channel-version', '')} GA SDK {ga[0]} is out and global.json still pins {pin}: "
                   "D03 T01 §2 (move the SDK pin to GA) is ready")
    newest = versions[0]
    extra = f"; newer prerelease {newest} is available" if newest != pin else ""
    return 0, f"no GA SDK yet (pin {pin}{extra})"


def main(argv: list[str]) -> int:
    try:
        with open(os.path.join(REPO, "global.json"), encoding="utf-8") as fh:
            pin = json.load(fh)["sdk"]["version"]
        channel = ".".join(pin.split(".")[:2])
        if argv[:1] == ["--feed"] and len(argv) == 2:
            with open(argv[1], encoding="utf-8") as fh:
                feed = json.load(fh)
        elif argv:
            print(__doc__.split("\n\n")[0], file=sys.stderr)
            return 2
        else:
            with urllib.request.urlopen(FEED.format(channel=channel), timeout=60) as response:
                feed = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, KeyError) as exc:
        print(f"check-sdk-ga: could not read the pin or the feed: {exc}", file=sys.stderr)
        return 2
    code, line = verdict(pin, feed)
    print(line, file=sys.stdout if code == 0 else sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
