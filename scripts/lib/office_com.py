"""Shared pieces for scripts that drive a reference Office app: the pinned reference build, the one process a
script started (held by handle), the app's baseline identifiers, and writes that publish every file or none."""
import json
import os
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "design" / "inventory"
REFERENCE = INVENTORY / "REFERENCE.md"


class Refused(Exception):
    pass


def baseline_identifiers(path=INVENTORY / "word" / "baseline.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    col = data["columns"].index("idMso")
    return {r[col] for r in data["rows"] if r[col]}


def reference_build(path=REFERENCE, app="Word"):
    """The pinned build of one app: the Build cell of its row under ## Builds in design/inventory/REFERENCE.md."""
    text = Path(path).read_text(encoding="utf-8")
    section = text[text.index("## Builds"):]
    match = re.search(r"^\| " + re.escape(app) + r" \| [^|]+ \| ([0-9]+(?:\.[0-9]+){3}) \|", section, re.MULTILINE)
    if not match:
        raise Refused(f"{path}: no {app} row with a four-part build under ## Builds")
    return match[1]


def installed_build():
    """The installed build, from the Click-to-Run configuration."""
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Office\ClickToRun\Configuration") as key:
        return winreg.QueryValueEx(key, "VersionToReport")[0]


def same_build(reported, reference):
    """Word reports a build as a prefix of components (16.0.20430); it must equal the reference's leading ones."""
    have, want = str(reported).split("."), reference.split(".")
    return 2 <= len(have) <= len(want) and have == want[:len(have)]


def is_executable(image_path, exe):
    """Whether a process image path names exactly this executable, compared case-insensitively."""
    return image_path.replace("\\", "/").rsplit("/", 1)[-1].upper() == exe.upper()


class OwnProcess:
    """The process behind one app instance's window, held by handle so its id cannot be reused under us, and
    checked to be the executable the caller expects."""

    SYNCHRONIZE, QUERY_LIMITED = 0x00100000, 0x1000

    def __init__(self, hwnd, exe="WINWORD.EXE"):
        import ctypes
        from ctypes import wintypes
        self.k32, user32 = ctypes.WinDLL("kernel32", use_last_error=True), ctypes.WinDLL("user32", use_last_error=True)
        user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        self.k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.k32.OpenProcess.restype = wintypes.HANDLE
        self.k32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                                        ctypes.POINTER(wintypes.DWORD)]
        self.k32.QueryFullProcessImageNameW.restype = wintypes.BOOL
        self.k32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.k32.WaitForSingleObject.restype = wintypes.DWORD
        self.k32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.k32.CloseHandle.restype = wintypes.BOOL
        pid = wintypes.DWORD()
        if not user32.GetWindowThreadProcessId(wintypes.HWND(int(hwnd)), ctypes.byref(pid)) or not pid.value:
            raise Refused(f"the {exe} instance's window has no process")
        self.pid = pid.value
        self.handle = self.k32.OpenProcess(self.SYNCHRONIZE | self.QUERY_LIMITED, False, self.pid)
        if not self.handle:
            raise Refused(f"cannot open the {exe} instance's process {self.pid}")
        size = wintypes.DWORD(32768)
        buf = ctypes.create_unicode_buffer(size.value)
        if not self.k32.QueryFullProcessImageNameW(self.handle, 0, buf, ctypes.byref(size)) \
                or not is_executable(buf.value, exe):
            self.close()
            raise Refused(f"process {self.pid} behind the instance's window is not {exe}")

    def exited(self, seconds):
        return self.k32.WaitForSingleObject(self.handle, int(seconds * 1000)) == 0  # WAIT_OBJECT_0

    def close(self):
        if self.handle:
            self.k32.CloseHandle(self.handle)
            self.handle = None


def own_process(app, hwnd=None):
    return OwnProcess(hwnd if hwnd is not None else app.ActiveWindow.Hwnd)


def write_atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(text.encode("utf-8"))
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    if path.read_bytes() != text.encode("utf-8"):
        raise OSError(f"{path}: read-back differs from what was written")


def publish(files, write=None, rename=os.replace, link=os.link):
    """Write every file or none, as far as a running process can promise. All new content is written to temporary
    files first, so a full disk fails before anything changes. Each original is then kept as a hard link (no data
    written, no moment without the file) and each new file replaces its destination in one atomic rename, so every
    destination always holds either its old or its new content, even if the process is killed. A failure that the
    process survives renames the kept originals back. With two or more files, a kill between their renames leaves
    some new and some old; rerunning the producing script repairs that."""
    write = write or (lambda path, data: path.write_bytes(data))
    staged, aside, placed = {}, {}, []
    try:
        for path, text in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".new")
            os.close(fd)
            staged[path] = Path(tmp)
            write(staged[path], text.encode("utf-8"))
            if staged[path].read_bytes() != text.encode("utf-8"):
                raise OSError(f"{tmp}: read-back differs from what was written")
        for path in files:
            if path.is_file():
                backup = path.with_name(f"{path.name}.{os.getpid()}.{os.urandom(6).hex()}.old")
                link(path, backup)  # a second name for the original: the destination never goes missing
                aside[path] = backup  # registered only once it exists, so a rollback restores the original
            rename(staged[path], path)
            del staged[path]  # placed: no longer a leftover to clean up
            placed.append(path)
    except BaseException:
        for path in placed:
            if path not in aside:
                path.unlink()
        for path, old in aside.items():
            rename(old, path)
        raise
    finally:
        for tmp in staged.values():
            if tmp.exists():
                tmp.unlink()
    for old in aside.values():
        old.unlink()
