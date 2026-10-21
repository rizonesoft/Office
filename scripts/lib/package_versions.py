"""Read and rewrite the central NuGet pins in `Directory.Packages.props`, keeping its formatting and comments.

Shared by `check-winui-pin.py` (the `Microsoft.WindowsAppSDK` pin) and `check-nuget-pins.py` (every other pin).

Stdlib only.
"""
import re
import xml.etree.ElementTree as ET

PROPS = "Directory.Packages.props"
STABLE = re.compile(r"^\d+\.\d+\.\d+(?:\.\d+)?$")


def pins(text, where=PROPS):
    """Every live PackageVersion as {package: version}; a package pinned twice or without a Version is refused."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ValueError(f"{where}: {exc}") from None
    out = {}
    # MSBuild elements may carry the msbuild/2003 namespace, so match the local name.
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "PackageVersion":
            continue
        package, version = element.get("Include"), element.get("Version")
        if not package or not version:
            raise ValueError(f"{where}: every PackageVersion needs an Include and a Version")
        if package in out:
            raise ValueError(f"{where}: {package} is pinned more than once")
        out[package] = version
    return out


def repinned(text, package, old, new):
    """The props text with only one package's version changed.

    It rewrites the one live (uncommented) PackageVersion whose Include names the package, in either attribute order
    or quote style."""
    comments = [m.span() for m in re.finditer(r"<!--.*?-->", text, re.S)]
    include = re.compile(r"\bInclude\s*=\s*([\"'])" + re.escape(package) + r"\1")
    tags = [m for m in re.finditer(r"<PackageVersion\b[^>]*>", text)
            if include.search(m.group(0)) and not any(a <= m.start() < b for a, b in comments)]
    if len(tags) != 1:
        raise ValueError(f"needs exactly one live PackageVersion for {package}, found {len(tags)}")
    tag = tags[0]
    version = re.compile(r"(\bVersion\s*=\s*([\"']))" + re.escape(old) + r"\2")
    changed, count = version.subn(lambda m: m.group(1) + new + m.group(2), tag.group(0))
    if count != 1:
        raise ValueError(f"the {package} pin {old} was not found on its PackageVersion")
    return text[:tag.start()] + changed + text[tag.end():]


def stable_key(version):
    """A numeric sort key for an exact stable NuGet version (three or four parts); None for anything else.

    NuGet normalizes a zero fourth part away (4.3.0.0 is 4.3.0), so the key does too, and equal versions compare equal."""
    if not STABLE.match(version):
        return None
    parts = tuple(int(n) for n in version.split("."))
    return parts[:3] if len(parts) == 4 and parts[3] == 0 else parts


def published(version, versions):
    """Whether a stable version is among the published ones, compared as NuGet normalizes them."""
    key = stable_key(version)
    return key is not None and key in {stable_key(v) for v in versions}


def latest_stable(versions):
    """The newest exact stable version in a NuGet version list, or None."""
    keyed = [(stable_key(v), v) for v in versions if stable_key(v)]
    return max(keyed)[1] if keyed else None
