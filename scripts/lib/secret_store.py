# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The repository's own credentials: an untracked env file filled from the Conclave vault.

Owner, 2026-11-10: the repository is self-contained. `python scripts/import-secrets.py` copies each credential in
`SECRETS` from 1Password into `.secrets/office.env` inside the clone, and everything that needs a credential reads
it from there, so a run needs neither WSL nor the vault. The folder is ignored by git, the file is closed to every other user
account, and no function here prints, logs or returns a value to anything but its caller.

A value is accepted only when it has its credential's known shape, both when it is imported and when it is read, so
a truncated or pasted-over file is treated as missing instead of being sent to a service.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ".secrets"
FILE = "office.env"
LINUX_SECONDS = 75  # with LINUX_STOP_SECONDS, under the 90 second Windows-side timeout
LINUX_STOP_SECONDS = 5
LINUX_MEMORY = "1G"

# name -> where it lives in the vault and the shape a real value has. Shapes are anchored and ASCII only.
SECRETS = {
    "SMTP2GO_API_KEY": {
        "item": "op://Conclave/jq2q47sqbpdwacivbjead5rrku/credential",
        "shape": r"api-[A-Za-z0-9]{32}",
        "use": "the automations' email sender (.conclave/automations/alert.py)",
    },
    "CLAUDE_CODE_OAUTH_TOKEN": {
        "item": "op://Conclave/pm5vqgypmvjok23xwlaacbwlji/credential",
        "shape": r"sk-ant-oat[0-9]{2}-[A-Za-z0-9_-]{40,}",
        "use": "the campaign launcher's one-year sign-in (scripts/start-campaign.ps1)",
    },
}


def env_path(root=ROOT) -> Path:
    return Path(root) / FOLDER / FILE


def well_formed(name: str, value: str) -> bool:
    return name in SECRETS and value.isascii() and re.fullmatch(SECRETS[name]["shape"], value) is not None


def wsl() -> str:
    """wsl.exe by its full System32 path: a bare name is searched for in the working directory first, where a
    repository could hold its own wsl.exe."""
    return os.path.join(os.environ.get("SystemRoot") or r"C:\Windows", "System32", "wsl.exe")


def vault_read(item: str, run=subprocess.run) -> str | None:
    """One vault field through `conclave-op` in WSL, or None when it cannot be read. Never echoed.

    Bounded inside Linux too: ending wsl.exe on Windows does not end the Linux processes it started. The read runs as
    a transient systemd user service, started by wsl.exe directly (no shell or profile before it): the login profile
    runs inside the unit, every process it starts is in the unit's cgroup and is killed when the read exits (a
    service's default KillMode), and RuntimeMaxSec and MemoryMax bound the whole unit. TimeoutStopSec bounds the
    SIGTERM-to-SIGKILL wait, so even a reader that ignores SIGTERM is gone within the Windows-side 90 seconds.
    """
    try:
        result = run([wsl(), "-e", "systemd-run", "--user", "--pipe", "--wait", "--quiet", "--collect",
                      "-p", f"RuntimeMaxSec={LINUX_SECONDS}", "-p", f"TimeoutStopSec={LINUX_STOP_SECONDS}",
                      "-p", f"MemoryMax={LINUX_MEMORY}",
                      "--", "bash", "-lc", f'conclave-op read "{item}"'],
                     capture_output=True, text=True, timeout=90,
                     creationflags=0x08000000 if os.name == "nt" else 0)  # CREATE_NO_WINDOW: callers have no console
    except (OSError, subprocess.SubprocessError):
        return None
    value = (result.stdout or "").strip()
    return value if result.returncode == 0 and value else None


def read_all(root=ROOT) -> dict[str, str]:
    """Every well-formed credential in the env file. A missing file, an unknown name or a malformed value is absent."""
    try:
        text = env_path(root).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}
    found = {}
    for line in text.splitlines():
        name, separator, value = line.partition("=")
        name, value = name.strip(), value.strip()
        if separator and well_formed(name, value):
            found[name] = value
    return found


def get(name: str, root=ROOT) -> str | None:
    return read_all(root).get(name)


def restrict(path: Path, run=subprocess.run) -> None:
    """Leave the path closed to every other user account."""
    if os.name == "nt":
        user = os.environ.get("USERNAME")
        if user:
            icacls = os.path.join(os.environ.get("SystemRoot") or r"C:\Windows", "System32", "icacls.exe")
            run([icacls, str(path), "/inheritance:r", "/grant:r", f"{user}:F"], capture_output=True, timeout=30,
                creationflags=0x08000000)
    else:
        os.chmod(path, 0o700 if path.is_dir() else 0o600)


def write_all(values: dict[str, str], root=ROOT, run=subprocess.run) -> None:
    """Write the env file whole through a temporary file in the same folder, restricted before it holds a value."""
    target = env_path(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    restrict(target.parent, run)
    handle, name = tempfile.mkstemp(dir=target.parent, prefix=".office-env-")
    temporary = Path(name)
    try:
        os.close(handle)
        restrict(temporary, run)
        lines = ["# Written by scripts/import-secrets.py from the Conclave vault. Never commit, print or copy this file."]
        lines += [f"{key}={values[key]}" for key in sorted(values)]
        temporary.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    if read_all(root) != values:
        raise OSError(f"{FOLDER}/{FILE} did not read back as written")


def import_all(root=ROOT, run=subprocess.run, names=None) -> dict[str, str]:
    """Copy each credential from the vault into the env file. Returns name -> 'imported', 'kept' or 'unavailable'.

    A credential the vault cannot give, or gives in the wrong shape, keeps the value the file already has, so a vault
    that is locked today never removes a credential that worked yesterday.
    """
    current = read_all(root)
    outcome = {}
    for name in names or sorted(SECRETS):
        value = vault_read(SECRETS[name]["item"], run)
        if value is not None and well_formed(name, value):
            current[name] = value
            outcome[name] = "imported"
        else:
            outcome[name] = "kept" if name in current else "unavailable"
    if current:
        write_all(current, root, run)
    return outcome
