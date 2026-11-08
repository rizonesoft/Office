# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Shared pieces for scripts that drive a reference Office app: the pinned reference build, the one process a
script started (held by handle), the app's baseline identifiers, and writes that publish every file or none."""
import json
import os
from pathlib import Path
import re
import sys
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


def _ktm_apis(ktmw32=None, kernel32=None, open_osf=None, fdopen=None):
    import ctypes
    from ctypes import wintypes
    import msvcrt

    if ktmw32 is None:
        ktmw32 = ctypes.WinDLL("ktmw32", use_last_error=True)
        ktmw32.CreateTransaction.argtypes = [
            wintypes.LPVOID, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD,
            wintypes.DWORD, wintypes.DWORD, wintypes.LPCWSTR,
        ]
        ktmw32.CreateTransaction.restype = wintypes.HANDLE
        ktmw32.CommitTransaction.argtypes = [wintypes.HANDLE]
        ktmw32.CommitTransaction.restype = wintypes.BOOL
        ktmw32.RollbackTransaction.argtypes = [wintypes.HANDLE]
        ktmw32.RollbackTransaction.restype = wintypes.BOOL
    if kernel32 is None:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateFileTransactedW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
            wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE, wintypes.HANDLE,
            wintypes.PUSHORT, wintypes.LPVOID,
        ]
        kernel32.CreateFileTransactedW.restype = wintypes.HANDLE
        kernel32.CreateHardLinkTransactedW.argtypes = [
            wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPVOID, wintypes.HANDLE,
        ]
        kernel32.CreateHardLinkTransactedW.restype = wintypes.BOOL
        kernel32.MoveFileTransactedW.argtypes = [
            wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPVOID, wintypes.LPVOID,
            wintypes.DWORD, wintypes.HANDLE,
        ]
        kernel32.MoveFileTransactedW.restype = wintypes.BOOL
        kernel32.DeleteFileTransactedW.argtypes = [wintypes.LPCWSTR, wintypes.HANDLE]
        kernel32.DeleteFileTransactedW.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
    return ktmw32, kernel32, open_osf or msvcrt.open_osfhandle, fdopen or os.fdopen, wintypes.HANDLE(-1).value


def transacted_replace(src, dst, backup, expected_bytes, on_enlisted=None, ktmw32=None, kernel32=None, open_osf=None,
                       fdopen=None):
    """Verify dst still holds expected_bytes, hard-link dst to backup, and replace dst with src inside a single
    Windows KTM kernel transaction so no concurrent atomic save or write can interleave between check and replace."""
    import ctypes

    ktmw32, kernel32, open_osf, fdopen, invalid = _ktm_apis(ktmw32, kernel32, open_osf, fdopen)
    tx = ktmw32.CreateTransaction(None, None, 0, 0, 0, 0, None)
    if tx == invalid or not tx:
        raise OSError(ctypes.get_last_error(), "CreateTransaction failed")
    committed = False
    try:
        # Enlist dst in the transaction with GENERIC_READ | DELETE and FILE_SHARE_READ only, blocking any
        # concurrent non-transacted write or atomic replace (WinError 6800 ERROR_TRANSACTIONAL_CONFLICT).
        h = kernel32.CreateFileTransactedW(
            str(dst), 0x80000000 | 0x00010000, 1, None, 3, 0, None, tx, None, None
        )
        if h == invalid or not h:
            err = ctypes.get_last_error()
            if err in (2, 3):  # ERROR_FILE_NOT_FOUND, ERROR_PATH_NOT_FOUND
                raise Refused(f"{dst} was removed while it was being written")
            raise Refused(f"{dst} changed while it was being written (WinError {err})")
        fd = open_osf(h, os.O_RDONLY)
        with fdopen(fd, "rb") as f:
            actual = f.read()
        if actual != expected_bytes:
            raise Refused(f"{dst} changed while it was being written")
        if on_enlisted is not None:
            on_enlisted(dst)
        if not kernel32.CreateHardLinkTransactedW(str(backup), str(dst), None, tx):
            raise OSError(ctypes.get_last_error(), f"CreateHardLinkTransactedW failed for {backup}")
        if not kernel32.MoveFileTransactedW(str(src), str(dst), None, None, 1, tx):
            raise OSError(ctypes.get_last_error(), f"MoveFileTransactedW failed for {dst}")
        if not ktmw32.CommitTransaction(tx):
            raise OSError(ctypes.get_last_error(), f"CommitTransaction failed for {dst}")
        committed = True
    finally:
        if not committed:
            ktmw32.RollbackTransaction(tx)
        kernel32.CloseHandle(tx)


def transacted_unlink(dst, expected_bytes, on_enlisted=None, ktmw32=None, kernel32=None, open_osf=None, fdopen=None,
                      status_out=None):
    """Delete dst inside a Windows KTM kernel transaction only if dst still holds expected_bytes, so a concurrent
    save or edit to a newly created output is never deleted during rollback."""
    import ctypes

    ktmw32, kernel32, open_osf, fdopen, invalid = _ktm_apis(ktmw32, kernel32, open_osf, fdopen)
    tx = ktmw32.CreateTransaction(None, None, 0, 0, 0, 0, None)
    if tx == invalid or not tx:
        if status_out is not None:
            status_out.append("failed")
        return False
    committed = False
    try:
        h = kernel32.CreateFileTransactedW(
            str(dst), 0x80000000 | 0x00010000, 1, None, 3, 0, None, tx, None, None
        )
        if h == invalid or not h:
            err = ctypes.get_last_error()
            if err in (2, 3):  # ERROR_FILE_NOT_FOUND, ERROR_PATH_NOT_FOUND
                if status_out is not None:
                    status_out.append("absent")
                return True
            if status_out is not None:
                status_out.append("failed")
            return False
        fd = open_osf(h, os.O_RDONLY)
        with fdopen(fd, "rb") as f:
            actual = f.read()
        if actual != expected_bytes:
            if status_out is not None:
                status_out.append("superseded")
            return False
        if on_enlisted is not None:
            on_enlisted(dst)
        if not kernel32.DeleteFileTransactedW(str(dst), tx):
            if status_out is not None:
                status_out.append("failed")
            return False
        if not ktmw32.CommitTransaction(tx):
            if status_out is not None:
                status_out.append("failed")
            return False
        committed = True
        return True
    finally:
        if not committed:
            ktmw32.RollbackTransaction(tx)
        kernel32.CloseHandle(tx)


def transacted_restore(backup, dst, expected_bytes, placed_ok=True, on_enlisted=None, ktmw32=None, kernel32=None,
                       open_osf=None, fdopen=None):
    """Restore backup to dst inside a Windows KTM kernel transaction only if dst is missing or still holds
    expected_bytes (when placed_ok is True); if dst was concurrently modified, leave dst untouched and unlink backup.
    If restoration fails transiently (for example a sharing violation), keep backup on disk so recovery data is not
    destroyed."""
    import ctypes

    ktmw32, kernel32, open_osf, fdopen, invalid = _ktm_apis(ktmw32, kernel32, open_osf, fdopen)
    tx = ktmw32.CreateTransaction(None, None, 0, 0, 0, 0, None)
    if tx == invalid or not tx:
        return False
    committed = False
    superseded = False
    try:
        h = kernel32.CreateFileTransactedW(
            str(dst), 0x80000000 | 0x00010000, 1, None, 3, 0, None, tx, None, None
        )
        if h == invalid or not h:
            err = ctypes.get_last_error()
            if err in (2, 3):  # dst is missing; restore backup without overwrite flag (0)
                if kernel32.MoveFileTransactedW(str(backup), str(dst), None, None, 0, tx):
                    if ktmw32.CommitTransaction(tx):
                        committed = True
                        return True
            return False
        fd = open_osf(h, os.O_RDONLY)
        with fdopen(fd, "rb") as f:
            actual = f.read()
        if not placed_ok or actual != expected_bytes:
            superseded = True
            return False
        if on_enlisted is not None:
            on_enlisted(dst)
        if not kernel32.MoveFileTransactedW(str(backup), str(dst), None, None, 1, tx):
            return False
        if not ktmw32.CommitTransaction(tx):
            return False
        committed = True
        return True
    finally:
        if not committed:
            ktmw32.RollbackTransaction(tx)
        kernel32.CloseHandle(tx)
        if superseded:
            bp = backup if hasattr(backup, "unlink") else Path(backup)
            if bp.exists():
                try:
                    bp.unlink()
                except OSError:
                    pass


def publish(files, write=None, rename=os.replace, link=os.link, create_only=(), expected_bytes=None, on_enlisted=None):
    """Write every file or none, as far as a running process can promise. All new content is written to temporary
    files first, so a full disk fails before anything changes. Each original is then kept as a hard link (no data
    written, no moment without the file) and each new file replaces its destination in one atomic rename, so every
    destination always holds either its old or its new content, even if the process is killed. A failure that the
    process survives renames the kept originals back. With two or more files, a kill between their renames leaves
    some new and some old; rerunning the producing script repairs that."""
    write = write or (lambda path, data: path.write_bytes(data))
    no_overwrite = {Path(p) for p in create_only}
    expected = {Path(p): b for p, b in (expected_bytes or {}).items()}
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
            if path in no_overwrite or (path in expected and expected[path] is None):
                try:
                    link(staged[path], path)  # atomic no-overwrite creation
                except FileExistsError:
                    raise Refused(f"{path} exists; pass --merge to update it") from None
                staged[path].unlink()
                del staged[path]
                placed.append(path)
                continue
            if path in expected:
                backup = path.with_name(f"{path.name}.{os.getpid()}.{os.urandom(6).hex()}.old")
                transacted_replace(staged[path], path, backup, expected[path], on_enlisted=on_enlisted)
                aside[path] = backup
                del staged[path]
                placed.append(path)
                continue
            if path.is_file():
                backup = path.with_name(f"{path.name}.{os.getpid()}.{os.urandom(6).hex()}.old")
                link(path, backup)  # a second name for the original: the destination never goes missing
                aside[path] = backup  # registered only once it exists, so a rollback restores the original
            rename(staged[path], path)
            del staged[path]  # placed: no longer a leftover to clean up
            placed.append(path)
    except BaseException as exc:
        unremoved = []
        for path in placed:
            if path not in aside:
                status = []
                if not transacted_unlink(path, files[path].encode("utf-8"), status_out=status):
                    if "superseded" not in status:
                        unremoved.append(path)
        unrestored = []
        for path, old in aside.items():
            if not transacted_restore(old, path, files[path].encode("utf-8"), placed_ok=(path in placed)):
                bp = old if hasattr(old, "exists") else Path(old)
                if bp.exists():
                    unrestored.append((path, old))
        notes = []
        if unremoved:
            notes.append("rollback could not remove newly created " + ", ".join(str(p) for p in unremoved))
        if unrestored:
            kept = ", ".join(f"{p} (backup kept at {b})" for p, b in unrestored)
            notes.append(f"rollback could not restore {kept}")
        for msg in notes:
            print(f"publish: {msg}", file=sys.stderr)
            if hasattr(exc, "add_note"):
                exc.add_note(msg)
        raise
    finally:
        for tmp in staged.values():
            if tmp.exists():
                tmp.unlink()
    for old in aside.values():
        old.unlink()
