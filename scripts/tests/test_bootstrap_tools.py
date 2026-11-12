# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/bootstrap-tools.py and scripts/lib/tool_lock.py: pinned tools fetched, verified before unpacking, and
installed whole or not at all (D00 T04 §1). Every archive is a fixture built here; no test touches the network."""
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import tarfile
import tempfile
import threading
import time
import unittest
from unittest import mock
import zipfile

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import tool_lock

spec = importlib.util.spec_from_file_location("bootstrap_tools", SCRIPTS / "bootstrap-tools.py")
boot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boot)


def zip_bytes(files, links=()):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as bundle:
        for name, data in files.items():
            bundle.writestr(name, data)
        for name, target in links:
            info = zipfile.ZipInfo(name)
            info.external_attr = (0o120777 << 16)
            bundle.writestr(info, target)
    return out.getvalue()


def tar_xz_bytes(files, links=()):
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode="w:xz") as bundle:
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            bundle.addfile(info, io.BytesIO(data))
        for name, target, kind in links:
            info = tarfile.TarInfo(name)
            info.type = kind
            info.linkname = target
            bundle.addfile(info)
    return out.getvalue()


def entry(url, data, fmt, keep, bin_):
    return {"url": url, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data), "format": fmt,
            "keep": keep, "bin": bin_}


class Server:
    """A fake opener serving fixture archives by URL; `mode` makes one URL stall, end early or trickle."""

    def __init__(self):
        self.files, self.calls, self.mode = {}, [], {}

    def __call__(self, url, timeout=None, deadline=None):
        self.calls.append(url)
        data, mode = self.files[url], self.mode.get(url)
        server = self

        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self, n=-1):
                if mode == "stall":
                    raise socket.timeout("timed out")
                if mode == "trickle":  # a buffered read waits for all n bytes of a server sending 16 at a time
                    time.sleep(min(5.0, 0.05 * max(n, 16) / 16))
                    return super().read(16)
                return super().read(n)

            def read1(self, n=-1):
                if mode == "stall":
                    raise socket.timeout("timed out")
                if mode == "incomplete":
                    import http.client
                    raise http.client.IncompleteRead(b"ab", 6)
                if mode == "trickle":  # what has arrived: 16 bytes after a short wait
                    time.sleep(0.05)
                    return super().read(16)
                return super().read(n)
        if mode == "short":
            return Response(data[: len(data) // 2])
        return Response(data)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.tools = self.tmp / ".tools"
        self.server = Server()
        cmake = zip_bytes({"cmake-1/bin/cmake.exe": b"cmake", "cmake-1/share/cmake-1/m.cmake": b"m",
                           "cmake-1/doc/readme.txt": b"skip me"})
        llvm = tar_xz_bytes({"llvm-1/bin/clangd.exe": b"clangd", "llvm-1/bin/clang.exe": b"skip",
                             "llvm-1/lib/clang/1/include/stddef.h": b"h"})
        vcpkg = b"MZ vcpkg"
        registry = zip_bytes({"vcpkg-2026/ports/zlib/portfile.cmake": b"p", "vcpkg-2026/scripts/x.cmake": b"x"})
        self.archives = {
            "cmake": ("https://x.invalid/cmake.zip", cmake, "zip", ["cmake-1/bin", "cmake-1/share"], ["cmake-1/bin"]),
            "llvm": ("https://x.invalid/llvm.tar.xz", llvm, "tar.xz",
                     ["llvm-1/bin/clangd.exe", "llvm-1/lib/clang/1/include"], ["llvm-1/bin"]),
            "vcpkg": ("https://x.invalid/vcpkg.exe", vcpkg, "exe", [], []),
            "vcpkg-registry": ("https://x.invalid/registry.zip", registry, "zip", ["vcpkg-2026"], ["vcpkg-2026"]),
        }
        self.lock = {}
        for name, (url, data, fmt, keep, bin_) in self.archives.items():
            self.server.files[url] = data
            one = entry(url, data, fmt, keep, bin_)
            self.lock[name] = {"version": "1.0", "archives": {"x64": one, "arm64": copy.deepcopy(one)}}
        self.lock["vcpkg"]["requires"] = ["vcpkg-registry"]
        self.write_lock()

    def write_lock(self, lock=None):
        self.lock_path = self.tmp / "tools.lock.json"
        self.lock_path.write_text(json.dumps(lock if lock is not None else self.lock), encoding="utf-8")

    def boot(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        from contextlib import redirect_stderr, redirect_stdout
        with redirect_stdout(out), redirect_stderr(err):
            code = boot.main(list(argv), opener=self.server, lock_path=self.lock_path, tools=self.tools, arch="x64")
        return code, out.getvalue() + err.getvalue()

    def leftovers(self):
        return sorted(p.name for p in self.tools.iterdir() if p.name.endswith(".partial") or ".stale-" in p.name
                      or p.name.startswith("download-")) if self.tools.exists() else []

    def entries(self, folder=None):
        """The names in a folder of `.tools/`, the run lock aside."""
        return sorted(p.name for p in (folder or self.tools).iterdir() if p.name != boot.RUN_LOCK)


class Lock(unittest.TestCase):
    def good(self):
        one = {"url": "https://a.invalid/t.zip", "sha256": "a" * 64, "size": 3, "format": "zip", "keep": ["t"],
               "bin": ["t"]}
        return {"t": {"version": "1.0", "archives": {"x64": one, "arm64": dict(one)}}}

    def refused(self, mutate, fragment):
        data = self.good()
        mutate(data)
        with self.assertRaises(tool_lock.LockError) as caught:
            tool_lock.parse(data)
        self.assertIn(fragment, str(caught.exception))
        self.assertIn("t", str(caught.exception))

    def test_a_good_lock_loads(self):
        self.assertEqual(tool_lock.parse(self.good())["t"]["version"], "1.0")

    def test_each_fault_is_refused_naming_the_tool(self):
        cases = [
            (lambda d: d["t"].update(colour="red"), "unknown key"),
            (lambda d: d["t"]["archives"]["x64"].update(url="http://a.invalid/t.zip"), "https"),
            (lambda d: d["t"]["archives"]["x64"].update(sha256="ABC"), "sha256"),
            (lambda d: d["t"]["archives"].pop("arm64"), "no arm64"),
            (lambda d: d["t"]["archives"]["x64"].update(size=0), "size"),
            (lambda d: d["t"]["archives"]["x64"].update(format="rar"), "format"),
            (lambda d: d["t"]["archives"]["x64"].update(bin=["../bin"]), "inside the tool's folder"),
            (lambda d: d["t"].update(requires=["ghost"]), "requires"),
        ]
        for mutate, fragment in cases:
            with self.subTest(fragment):
                self.refused(mutate, fragment)

    def test_the_cli_refuses_each_named_fault_with_exit_2_and_the_tool(self):
        # Completion review gap 2: the four faults the section names, through the command line.
        faults = {"unknown key": lambda d: d["t"].update(colour="red"),
                  "https": lambda d: d["t"]["archives"]["x64"].update(url="http://a.invalid/t.zip"),
                  "sha256": lambda d: d["t"]["archives"]["x64"].update(sha256="ABC"),
                  "no arm64": lambda d: d["t"]["archives"].pop("arm64")}
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        from contextlib import redirect_stderr
        for fragment, mutate in faults.items():
            with self.subTest(fragment):
                data = self.good()
                mutate(data)
                (tmp / "tools.lock.json").write_text(json.dumps(data), encoding="utf-8")
                err = io.StringIO()
                with redirect_stderr(err):
                    code = boot.main([], lock_path=tmp / "tools.lock.json", tools=tmp / ".tools", arch="x64")
                self.assertEqual(code, 2)
                self.assertIn(fragment, err.getvalue())
                self.assertIn("t:", err.getvalue())
                self.assertFalse((tmp / ".tools").exists())

    def test_the_cli_refuses_a_bad_lock_with_exit_2(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "tools.lock.json").write_text('{"t": {"version": "1"}}', encoding="utf-8")
        self.assertEqual(boot.main([], lock_path=tmp / "tools.lock.json", tools=tmp / ".tools", arch="x64"), 2)


class Install(Fixture):
    def test_an_empty_folder_is_filled_and_a_second_run_downloads_nothing(self):
        code, out = self.boot()
        self.assertEqual(code, 0, out)
        self.assertTrue((self.tools / "cmake-1.0" / "cmake-1" / "bin" / "cmake.exe").is_file())
        self.assertFalse((self.tools / "cmake-1.0" / "cmake-1" / "doc").exists())  # not kept
        self.assertTrue((self.tools / "llvm-1.0" / "llvm-1" / "lib/clang/1/include/stddef.h").is_file())
        self.assertFalse((self.tools / "llvm-1.0" / "llvm-1" / "bin" / "clang.exe").exists())
        self.assertTrue((self.tools / "vcpkg-1.0" / "vcpkg.exe").is_file())
        calls = len(self.server.calls)
        self.assertEqual(self.boot("--check")[0], 0)
        self.assertEqual(self.boot()[0], 0)
        self.assertEqual(len(self.server.calls), calls)
        self.assertEqual(self.leftovers(), [])

    def test_a_changed_byte_is_refused_before_anything_is_unpacked(self):
        url = self.archives["cmake"][0]
        data = bytearray(self.server.files[url])
        data[-1] ^= 1
        self.server.files[url] = bytes(data)
        code, out = self.boot("--only", "cmake")
        self.assertEqual(code, 1)
        self.assertIn("SHA-256", out)
        self.assertFalse((self.tools / "cmake-1.0").exists())
        self.assertEqual(self.leftovers(), [])

    def test_more_than_the_pinned_size_is_stopped_while_it_arrives(self):
        url = self.archives["cmake"][0]
        self.server.files[url] = self.server.files[url] + b"x" * (boot.CHUNK * 2)
        code, out = self.boot("--only", "cmake")
        self.assertEqual(code, 1)
        self.assertIn("more than the pinned", out)
        self.assertEqual(self.leftovers(), [])

    def test_stalled_short_and_slow_downloads_fail_cleanly_and_a_rerun_succeeds(self):
        url = self.archives["cmake"][0]
        for mode, argv, fragment in (("stall", [], "timed out"), ("short", [], "of the pinned"),
                                     ("trickle", ["--deadline", "0.002"], "deadline")):
            with self.subTest(mode):
                self.server.mode = {url: mode}
                code, out = self.boot("--only", "cmake", *argv)
                self.assertEqual(code, 1)
                self.assertIn(fragment, out)
                self.assertEqual(self.leftovers(), [])
                self.assertFalse((self.tools / "cmake-1.0").exists())
        self.server.mode = {}
        self.assertEqual(self.boot("--only", "cmake")[0], 0)

    def test_check_names_a_missing_or_damaged_tool_and_the_next_run_repairs_it(self):
        self.assertEqual(self.boot()[0], 0)
        for damage in (lambda: (self.tools / "cmake-1.0" / "cmake-1" / "bin" / "cmake.exe").unlink(),
                       lambda: (self.tools / "llvm-1.0" / "llvm-1" / "lib/clang/1/include/stddef.h").write_bytes(b"x"),
                       lambda: (self.tools / "cmake-1.0" / boot.RECEIPT).unlink()):
            with self.subTest(damage=damage):
                damage()
                code, out = self.boot("--check")
                self.assertEqual(code, 1)
                self.assertIn("missing or damaged", out)
                self.assertEqual(self.boot()[0], 0)
                self.assertEqual(self.boot("--check")[0], 0)

    def test_vcpkg_counts_only_with_its_registry(self):
        self.assertEqual(self.boot("--only", "vcpkg")[0], 0)  # its registry comes with it
        self.assertTrue((self.tools / "vcpkg-registry-1.0").is_dir())
        shutil.rmtree(self.tools / "vcpkg-registry-1.0")
        code, out = self.boot("--check")
        self.assertEqual(code, 1)
        self.assertIn("vcpkg 1.0: requires vcpkg-registry", out)

    def test_an_interrupted_promotion_and_a_changed_entry_at_the_same_version_are_repaired(self):
        self.assertEqual(self.boot()[0], 0)
        (self.tools / "cmake-1.0" / boot.RECEIPT).unlink()  # as if stopped after the rename, before a receipt
        self.assertEqual(self.boot()[0], 0)
        self.assertEqual(self.boot("--check")[0], 0)
        url, data, fmt, keep, bin_ = self.archives["cmake"]
        newer = zip_bytes({"cmake-1/bin/cmake.exe": b"cmake rebuilt", "cmake-1/share/cmake-1/m.cmake": b"m"})
        self.server.files[url] = newer
        self.lock["cmake"]["archives"]["x64"] = entry(url, newer, fmt, keep, bin_)
        self.write_lock()
        self.assertEqual(self.boot()[0], 0)
        self.assertEqual((self.tools / "cmake-1.0" / "cmake-1" / "bin" / "cmake.exe").read_bytes(), b"cmake rebuilt")
        self.assertEqual(self.leftovers(), [])

    def test_a_folder_for_a_version_no_longer_pinned_is_removed(self):
        self.assertEqual(self.boot()[0], 0)
        old = self.tools / "cmake-0.9"
        old.mkdir()
        (self.tools / "cmake-1.0.partial").mkdir()
        self.assertEqual(self.boot()[0], 0)
        self.assertFalse(old.exists())
        self.assertEqual(self.leftovers(), [])

    def test_a_slow_server_cannot_hold_a_read_past_the_deadline(self):
        # Round 1, findings 1 and 4: the deadline is checked between arrivals, not after a full buffered chunk.
        url = self.archives["cmake"][0]
        self.server.mode = {url: "trickle"}
        started = time.monotonic()
        code, out = self.boot("--only", "cmake", "--deadline", "0.002")
        self.assertEqual(code, 1)
        self.assertIn("deadline", out)
        self.assertLess(time.monotonic() - started, 3)

    def test_a_second_run_waits_for_the_first_and_then_refuses(self):
        # Round 1, finding 2: two runs never change .tools/ at once.
        self.tools.mkdir()
        with mock.patch.object(boot, "LOCK_SECONDS", 0.3), boot.RunLock(self.tools):
            code, out = self.boot()
        self.assertEqual(code, 1)
        self.assertIn("another bootstrap still holds", out)
        self.assertEqual(self.entries(), [])
        self.assertEqual(self.boot()[0], 0)  # once the first is gone, the next run proceeds

    def test_only_installs_the_named_tool_and_an_unknown_name_exits_2(self):
        self.assertEqual(self.boot("--only", "cmake")[0], 0)
        self.assertEqual(self.entries(), ["cmake-1.0"])
        self.assertEqual(self.boot("--only", "ghost")[0], 2)


class FreshPlanGaps(Fixture):
    """D00 T04 §1, the fresh plan review: every kept path produces a file, and file-system failures are refusals."""

    def test_a_kept_path_that_produced_nothing_refuses_the_archive(self):
        url, _, fmt, keep, bin_ = self.archives["llvm"]
        without = tar_xz_bytes({"llvm-1/bin/clangd.exe": b"clangd"})  # the programs, but no header folder
        self.server.files[url] = without
        self.lock["llvm"]["archives"]["x64"] = entry(url, without, fmt, keep, bin_)
        self.write_lock()
        code, out = self.boot("--only", "llvm")
        self.assertEqual(code, 1)
        self.assertIn("nothing under the kept path 'llvm-1/lib/clang/1/include'", out)
        self.assertFalse((self.tools / "llvm-1.0").exists())
        self.assertEqual(self.leftovers(), [])

    def test_a_failure_while_unpacking_or_writing_the_receipt_is_a_refusal_and_a_rerun_succeeds(self):
        for target, step in (("write_member", "unpacking"), ("manifest", "writing the receipt")):
            with self.subTest(step):
                with mock.patch.object(boot, target, side_effect=OSError(28, "No space left on device")):
                    code, out = self.boot("--only", "cmake")
                self.assertEqual(code, 1)
                self.assertIn(f"cmake: {step} failed", out)
                self.assertIn("No space left on device", out)
                self.assertFalse((self.tools / "cmake-1.0").exists())
                self.assertEqual(self.leftovers(), [])
        self.assertEqual(self.boot("--only", "cmake")[0], 0)

    def test_a_failed_promotion_puts_the_earlier_installation_back(self):
        self.assertEqual(self.boot("--only", "cmake")[0], 0)
        before = (self.tools / "cmake-1.0" / "cmake-1" / "bin" / "cmake.exe").read_bytes()
        url, _, fmt, keep, bin_ = self.archives["cmake"]
        newer = zip_bytes({"cmake-1/bin/cmake.exe": b"cmake rebuilt", "cmake-1/share/cmake-1/m.cmake": b"m"})
        self.server.files[url] = newer
        self.lock["cmake"]["archives"]["x64"] = entry(url, newer, fmt, keep, bin_)
        self.write_lock()
        real = Path.rename

        def held(self_, target):
            if self_.name.endswith(".partial"):
                raise PermissionError(32, "The process cannot access the file because it is being used")
            return real(self_, target)
        with mock.patch.object(Path, "rename", held):
            code, out = self.boot("--only", "cmake")
        self.assertEqual(code, 1)
        self.assertIn("cmake: promotion failed", out)
        self.assertEqual((self.tools / "cmake-1.0" / "cmake-1" / "bin" / "cmake.exe").read_bytes(), before)
        self.assertEqual(self.leftovers(), [])
        self.assertEqual(self.boot("--only", "cmake")[0], 0)
        self.assertEqual((self.tools / "cmake-1.0" / "cmake-1" / "bin" / "cmake.exe").read_bytes(), b"cmake rebuilt")

    def test_a_leftover_that_cannot_be_removed_is_said_and_the_rest_installs(self):
        self.tools.mkdir()
        held_folder = self.tools / "cmake-0.9"
        held_folder.mkdir()
        real = shutil.rmtree

        def refuse(path, *a, **kw):
            if Path(path).name == "cmake-0.9":
                raise PermissionError(32, "being used by another process")
            return real(path, *a, **kw)
        with mock.patch.object(boot.shutil, "rmtree", refuse):
            code, out = self.boot("--only", "cmake")
        self.assertEqual(code, 1)
        self.assertIn("cleanup of cmake-0.9 failed", out)
        self.assertTrue((self.tools / "cmake-1.0").is_dir())  # the install went on
        self.assertEqual(self.boot("--only", "cmake")[0], 0)  # the fault removed, the next run cleans it
        self.assertFalse(held_folder.exists())


class Trickler:
    """A local HTTP server (127.0.0.1) whose paths misbehave on purpose; every loop it runs is bounded."""

    BODY = b"payload!"

    def __init__(self):
        import socketserver
        outer = self

        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                request = b""
                while b"\r\n\r\n" not in request and len(request) < 65536:
                    piece = self.request.recv(4096)
                    if not piece:
                        return
                    request += piece
                path = request.split(b" ")[1].decode()
                send = self.request.sendall
                try:
                    if path == "/header":  # a header line that never ends, one byte at a time (at most 20 s)
                        send(b"HTTP/1.1 200 OK\r\nX-Slow: ")
                        for _ in range(100):
                            send(b"x")
                            time.sleep(0.2)
                    elif path == "/chunk":  # a chunk-size line that never ends (at most 20 s)
                        send(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n")
                        for _ in range(100):
                            send(b"0")
                            time.sleep(0.2)
                    elif path == "/cut":  # a chunk promised as 8 bytes, 2 sent, then the connection ends
                        send(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n8\r\nab")
                    elif path == "/moved":
                        send(b"HTTP/1.1 302 Found\r\nLocation: /file\r\nContent-Length: 0\r\n\r\n")
                    elif path == "/file":
                        send(b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n" % len(outer.BODY) + outer.BODY)
                except OSError:
                    pass  # the client shut the connection: the point of the test

        self.server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class SecondCycleRound(unittest.TestCase):
    """D00 T04 §1, the round of the second cycle: the deadline bounds every read, a cut download fails one tool, and
    a held staging folder fails one tool, never the run."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.web = Trickler()
        self.addCleanup(self.web.close)

    def opener(self, url, timeout=None, deadline=None):
        return boot.Bounded(url, 5, deadline, scheme_ok=("http",))

    def fetch(self, path, seconds, data=Trickler.BODY):
        url = self.web.base + path
        one = entry(url, data, "zip", ["x"], [])
        return boot.fetch("t", one, self.tmp, self.opener, seconds)

    def test_a_trickled_header_or_chunk_line_is_cut_at_the_deadline(self):
        for path in ("/header", "/chunk"):
            with self.subTest(path):
                started = time.monotonic()
                with self.assertRaises(boot.Failed) as caught:
                    self.fetch(path, 1.0)
                self.assertLess(time.monotonic() - started, 4)
                self.assertIn("deadline", str(caught.exception))
                self.assertEqual(list(self.tmp.glob("download-*")), [])

    def test_a_cut_chunked_download_fails_cleanly(self):
        with self.assertRaises(boot.Failed) as caught:
            self.fetch("/cut", 30)
        self.assertIn("IncompleteRead", str(caught.exception))
        self.assertEqual(list(self.tmp.glob("download-*")), [])

    def test_a_redirect_is_followed(self):
        path = self.fetch("/moved", 30)
        self.assertEqual(path.read_bytes(), Trickler.BODY)
        path.unlink()

    def test_the_default_opener_refuses_plain_http(self):
        with self.assertRaises(OSError):
            boot.bounded_open(self.web.base + "/file", deadline=time.monotonic() + 5)


class OneToolFails(Fixture):
    """A cut download or a held staging folder fails that tool; the others still install."""

    def test_an_incomplete_read_fails_one_tool_and_the_rest_install(self):
        url = self.archives["cmake"][0]
        self.server.mode = {url: "incomplete"}
        code, out = self.boot()
        self.assertEqual(code, 1)
        self.assertIn("cmake: the download failed: IncompleteRead", out)
        self.assertTrue((self.tools / "llvm-1.0").is_dir())
        self.assertFalse((self.tools / "cmake-1.0").exists())

    def test_a_held_staging_folder_fails_one_tool_and_the_rest_install(self):
        self.tools.mkdir()
        (self.tools / "cmake-1.0.partial").mkdir()
        real = shutil.rmtree

        def held(path, *a, **kw):
            if Path(path).name == "cmake-1.0.partial":
                raise PermissionError(32, "being used by another process")
            return real(path, *a, **kw)
        with mock.patch.object(boot.shutil, "rmtree", held):
            code, out = self.boot()
        self.assertEqual(code, 1)
        self.assertIn("cmake: an earlier staging folder cannot be removed", out)
        self.assertTrue((self.tools / "llvm-1.0").is_dir())
        self.assertEqual(self.boot()[0], 0)


class SecondCycleCompletion(Fixture):
    """D00 T04 §1, the completion review of the second cycle."""

    def upgrade_cmake(self):
        url, _, fmt, keep, bin_ = self.archives["cmake"]
        newer = zip_bytes({"cmake-1/bin/cmake.exe": b"cmake 2", "cmake-1/share/cmake-1/m.cmake": b"m"})
        self.server.files[url] = newer
        self.lock["cmake"]["version"] = "2.0"
        self.lock["cmake"]["archives"]["x64"] = entry(url, newer, fmt, keep, bin_)
        self.write_lock()

    def test_a_failed_upgrade_keeps_the_earlier_version_and_the_retry_replaces_it(self):
        self.assertEqual(self.boot()[0], 0)
        self.upgrade_cmake()
        with mock.patch.object(boot, "write_member", side_effect=OSError(28, "No space left on device")):
            code, out = self.boot("--only", "cmake")
        self.assertEqual(code, 1)
        self.assertEqual((self.tools / "cmake-1.0" / "cmake-1" / "bin" / "cmake.exe").read_bytes(), b"cmake")
        self.assertFalse((self.tools / "cmake-2.0").exists())
        self.assertEqual(self.boot("--only", "cmake")[0], 0)
        self.assertEqual((self.tools / "cmake-2.0" / "cmake-1" / "bin" / "cmake.exe").read_bytes(), b"cmake 2")
        self.assertFalse((self.tools / "cmake-1.0").exists())  # removed only once its replacement is in place

    def test_a_set_aside_folder_that_cannot_go_is_exit_1_with_the_new_installation_in_place(self):
        self.assertEqual(self.boot()[0], 0)
        url, _, fmt, keep, bin_ = self.archives["cmake"]
        rebuilt = zip_bytes({"cmake-1/bin/cmake.exe": b"cmake rebuilt", "cmake-1/share/cmake-1/m.cmake": b"m"})
        self.server.files[url] = rebuilt
        self.lock["cmake"]["archives"]["x64"] = entry(url, rebuilt, fmt, keep, bin_)
        self.write_lock()
        real = shutil.rmtree

        def held(path, *a, **kw):
            if ".stale-" in Path(path).name:
                raise PermissionError(32, "being used by another process")
            return real(path, *a, **kw)
        with mock.patch.object(boot.shutil, "rmtree", held):
            code, out = self.boot("--only", "cmake")
        self.assertEqual(code, 1)
        self.assertIn("cmake: cleanup of cmake-1.0.stale-", out)
        self.assertEqual((self.tools / "cmake-1.0" / "cmake-1" / "bin" / "cmake.exe").read_bytes(), b"cmake rebuilt")
        self.assertEqual(self.boot("--check")[0], 0)
        self.assertEqual(self.boot()[0], 0)  # the next run removes the set-aside folder
        self.assertEqual(self.leftovers(), [])

    def test_a_tool_whose_name_begins_another_keeps_the_other_tools_folder(self):
        self.assertEqual(self.boot()[0], 0)
        self.assertEqual(self.boot("--only", "vcpkg")[0], 0)
        self.assertTrue((self.tools / "vcpkg-registry-1.0").is_dir())


class Resolver(Fixture):
    """D00 T04 §2: programs are found in the tool folder only, and every way a tool can be missing is refused."""

    def setUp(self):
        super().setUp()
        self.assertEqual(self.boot()[0], 0)
        # A program of the same name first on PATH, which the resolver must never return.
        self.decoys = self.tmp / "decoys"
        self.decoys.mkdir()
        for program in ("cmake.exe", "clangd.exe", "vcpkg.exe"):
            (self.decoys / program).write_bytes(b"machine copy")
        patcher = mock.patch.dict(os.environ, {"PATH": str(self.decoys) + os.pathsep + os.environ.get("PATH", "")})
        patcher.start()
        self.addCleanup(patcher.stop)

    def tools_(self, arch="x64"):
        return tool_lock.Tools(self.lock_path, self.tools, arch)

    def refused(self, program, *fragments):
        with self.assertRaises(tool_lock.ToolMissing) as caught:
            self.tools_().path(program)
        text = str(caught.exception)
        for fragment in fragments + ("python scripts/bootstrap-tools.py",):
            self.assertIn(fragment, text)
        self.assertNotIn(str(self.decoys), text)
        return text

    def test_a_program_is_found_in_the_tool_folder_not_on_path(self):
        self.assertEqual(str(shutil.which("cmake")).lower(), str(self.decoys / "cmake.exe").lower())  # the decoy is first
        for program, inside in (("cmake", "cmake-1.0/cmake-1/bin/cmake.exe"), ("clangd.exe", "llvm-1.0/llvm-1/bin/clangd.exe"),
                                ("vcpkg", "vcpkg-1.0/vcpkg.exe")):
            with self.subTest(program):
                self.assertEqual(self.tools_().path(program), (self.tools / inside).resolve())
                self.assertEqual(tool_lock.tool_path(program, self.lock_path, self.tools, "x64"),
                                 (self.tools / inside).resolve())

    def test_an_empty_tool_folder_refuses_with_no_fallback(self):
        shutil.rmtree(self.tools)
        self.refused("cmake", "cmake 1.0", "not installed")

    def test_each_way_a_tool_is_missing_is_refused(self):
        folder = self.tools / "cmake-1.0"
        program = folder / "cmake-1" / "bin" / "cmake.exe"
        receipt = folder / tool_lock.RECEIPT
        original = receipt.read_text(encoding="utf-8")

        def newer_lock():
            self.lock["cmake"]["archives"]["x64"]["sha256"] = "b" * 64
            self.write_lock()

        def restore_lock():
            self.lock["cmake"]["archives"]["x64"] = entry(*self.archives["cmake"][:2], *self.archives["cmake"][2:])
            self.write_lock()
        cases = [
            ("a newer lock entry", newer_lock, restore_lock, "not installed"),
            ("a missing receipt", receipt.unlink, lambda: receipt.write_text(original, encoding="utf-8"), "not installed"),
            ("a malformed receipt", lambda: receipt.write_text("{not json", encoding="utf-8"),
             lambda: receipt.write_text(original, encoding="utf-8"), "not installed"),
            ("a deleted program", program.unlink, lambda: program.write_bytes(b"cmake"), "missing or changed cmake.exe"),
            ("a same-size change", lambda: program.write_bytes(b"CMAKE"), lambda: program.write_bytes(b"cmake"),
             "missing or changed cmake.exe"),
        ]
        for label, break_, mend, fragment in cases:
            with self.subTest(label):
                break_()
                self.refused("cmake", "cmake 1.0", fragment)
                mend()
                self.assertEqual(self.tools_().path("cmake"), program.resolve())

    def test_a_missing_or_stale_required_tool_is_refused(self):
        registry = self.tools / "vcpkg-registry-1.0"
        aside = self.tmp / "registry-aside"
        registry.rename(aside)
        self.refused("vcpkg", "vcpkg requires vcpkg-registry 1.0", "not installed")
        aside.rename(registry)
        self.lock["vcpkg-registry"]["version"] = "2.0"  # the lock moved on; 1.0 is stale
        self.write_lock()
        self.refused("vcpkg", "vcpkg requires vcpkg-registry 2.0")

    def test_a_program_no_tool_provides_is_refused_as_such(self):
        with self.assertRaises(tool_lock.ToolMissing) as caught:
            self.tools_().path("nmake")
        self.assertIn("no tool of tools.lock.json provides nmake.exe", str(caught.exception))

    def test_one_name_on_every_architecture(self):
        url = "https://x.invalid/vcpkg-arm64.exe"
        data = b"MZ vcpkg arm64"
        self.server.files[url] = data
        self.lock["vcpkg"]["archives"]["arm64"] = entry(url, data, "exe", [], [])
        self.write_lock()
        arm = self.tmp / "arm-tools"
        out, err = io.StringIO(), io.StringIO()
        from contextlib import redirect_stderr, redirect_stdout
        with redirect_stdout(out), redirect_stderr(err):
            self.assertEqual(boot.main([], opener=self.server, lock_path=self.lock_path, tools=arm, arch="arm64"), 0)
            self.assertEqual(boot.main(["--where", "vcpkg"], lock_path=self.lock_path, tools=arm, arch="arm64"), 0)
        self.assertTrue((arm / "vcpkg-1.0" / "vcpkg.exe").is_file())
        self.assertFalse((arm / "vcpkg-1.0" / "vcpkg-arm64.exe").exists())
        self.assertEqual(self.tools_("arm64").__class__(self.lock_path, arm, "arm64").path("vcpkg"),
                         (arm / "vcpkg-1.0" / "vcpkg.exe").resolve())
        self.assertIn(str((arm / "vcpkg-1.0" / "vcpkg.exe").resolve()), out.getvalue())
        self.assertEqual(self.tools_("x64").path("vcpkg"), (self.tools / "vcpkg-1.0" / "vcpkg.exe").resolve())

    def test_tool_env_checks_the_registry_itself(self):
        folder = (self.tools / "vcpkg-registry-1.0" / "vcpkg-2026").resolve()
        self.assertEqual(tool_lock.tool_env(self.lock_path, self.tools, "x64"), {"VCPKG_ROOT": str(folder)})
        shutil.rmtree(self.tools / "vcpkg-registry-1.0")
        with self.assertRaises(tool_lock.ToolMissing) as caught:
            tool_lock.tool_env(self.lock_path, self.tools, "x64")
        self.assertIn("vcpkg-registry 1.0 is not installed", str(caught.exception))
        self.assertIn("python scripts/bootstrap-tools.py", str(caught.exception))
        self.lock["vcpkg-registry"]["archives"]["x64"]["sha256"] = "c" * 64  # stale against the lock as well
        self.write_lock()
        with self.assertRaises(tool_lock.ToolMissing):
            tool_lock.tool_env(self.lock_path, self.tools, "x64")
        self.lock["vcpkg-registry"]["archives"]["x64"] = entry(*self.archives["vcpkg-registry"])
        self.write_lock()
        self.assertEqual(self.boot()[0], 0)  # the bootstrap repairs it
        self.assertEqual(tool_lock.tool_env(self.lock_path, self.tools, "x64"), {"VCPKG_ROOT": str(folder)})

    def test_where_prints_the_path_or_refuses(self):
        code, out = self.boot("--where", "ninja")
        self.assertEqual(code, 1)
        self.assertIn("no tool of tools.lock.json provides ninja.exe", out)
        code, out = self.boot("--where", "cmake")
        self.assertEqual((code, out.strip()), (0, str((self.tools / "cmake-1.0/cmake-1/bin/cmake.exe").resolve())))
        shutil.rmtree(self.tools / "cmake-1.0")
        code, out = self.boot("--where", "cmake")
        self.assertEqual(code, 1)
        self.assertIn("cmake 1.0 is not installed", out)
        self.assertNotIn(str(self.decoys), out)

    def bin_dirs(self):
        out, err = io.StringIO(), io.StringIO()
        from contextlib import redirect_stderr, redirect_stdout
        with redirect_stdout(out), redirect_stderr(err):
            code = boot.main(["--bin-dirs"], lock_path=self.lock_path, tools=self.tools, arch="x64")
        return code, out.getvalue().splitlines(), err.getvalue()

    def test_bin_dirs_prints_only_usable_folders(self):
        every = [str((self.tools / f).resolve()) for f in
                 ("cmake-1.0/cmake-1/bin", "llvm-1.0/llvm-1/bin", "vcpkg-1.0", "vcpkg-registry-1.0/vcpkg-2026")]
        code, lines, err = self.bin_dirs()
        self.assertEqual((code, lines, err), (0, every, ""))
        # Partial: llvm is gone. Its folder is left out and named, the rest printed, exit 1.
        shutil.rmtree(self.tools / "llvm-1.0")
        code, lines, err = self.bin_dirs()
        self.assertEqual(code, 1)
        self.assertEqual(lines, [every[0], every[2], every[3]])
        self.assertIn("llvm 1.0 is not installed", err)
        self.assertIn("python scripts/bootstrap-tools.py", err)
        # Stale: cmake's program changed. Left out too.
        (self.tools / "cmake-1.0" / "cmake-1" / "bin" / "cmake.exe").write_bytes(b"CMAKE")
        code, lines, err = self.bin_dirs()
        self.assertEqual((code, lines), (1, [every[2], every[3]]))
        self.assertIn("cmake 1.0 has a missing or changed cmake-1/bin/cmake.exe", err)
        # Empty: nothing on stdout.
        shutil.rmtree(self.tools)
        code, lines, err = self.bin_dirs()
        self.assertEqual((code, lines), (1, []))
        self.assertEqual(err.count("is not installed"), 4)


class Refusals(Fixture):
    """An archive that would write outside the tool's folder is refused in each format (gap 5 of the plan review)."""

    def serve(self, name, data, fmt, keep):
        url = f"https://x.invalid/{name}.{fmt}"
        self.server.files[url] = data
        one = entry(url, data, fmt, keep, [])
        self.write_lock({name: {"version": "1.0", "archives": {"x64": one, "arm64": one}}})

    def refuses(self, fragment):
        code, out = self.boot()
        self.assertEqual(code, 1, out)
        self.assertIn(fragment, out)
        self.assertEqual(self.entries(), [])
        self.assertFalse((self.tmp / "escape.txt").exists())

    def test_a_climbing_member_is_refused_in_zip_and_tar_xz(self):
        for fmt, data in (("zip", zip_bytes({"../escape.txt": b"x"})),
                          ("tar.xz", tar_xz_bytes({"../escape.txt": b"x"}))):
            with self.subTest(fmt):
                self.serve("bad", data, fmt, ["t"])  # refused whatever keep says: every member is checked
                self.refuses("outside the tool's folder")

    def test_an_absolute_member_is_refused_in_zip_and_tar_xz(self):
        for fmt, data in (("zip", zip_bytes({"/escape.txt": b"x"})), ("tar.xz", tar_xz_bytes({"/escape.txt": b"x"}))):
            with self.subTest(fmt):
                self.serve("bad", data, fmt, ["escape.txt"])
                self.refuses("outside the tool's folder")

    def test_a_link_leaving_the_folder_is_refused(self):
        for fmt, data in (("zip", zip_bytes({}, links=[("t/link", "../../escape.txt")])),
                          ("tar.xz", tar_xz_bytes({}, links=[("t/link", "../../escape.txt", tarfile.SYMTYPE)])),
                          ("tar.xz", tar_xz_bytes({}, links=[("t/hard", "../escape.txt", tarfile.LNKTYPE)]))):
            with self.subTest(fmt):
                self.serve("bad", data, fmt, ["t"])
                self.refuses("link")

    def test_more_than_the_pinned_size_is_refused_in_every_format(self):
        # Completion review gap 2: the size refusal for zip, tar.xz and exe alike.
        for fmt, data in (("zip", zip_bytes({"t/a.txt": b"a"})), ("tar.xz", tar_xz_bytes({"t/a.txt": b"a"})),
                          ("exe", b"MZ")):
            with self.subTest(fmt):
                self.serve("big", data, fmt, [] if fmt == "exe" else ["t"])
                url = f"https://x.invalid/big.{fmt}"
                self.server.files[url] = data + b"x" * (boot.CHUNK * 2)
                self.refuses("more than the pinned")

    def test_an_exe_installs_as_its_single_file(self):
        self.serve("tool", b"MZ", "exe", [])
        self.assertEqual(self.boot()[0], 0)
        self.assertEqual(self.entries(self.tools / "tool-1.0"), [boot.RECEIPT, "tool.exe"])


class Repository(unittest.TestCase):
    def test_the_repository_lock_loads(self):
        lock = tool_lock.load(SCRIPTS.parent / "tools.lock.json")
        self.assertEqual(sorted(lock), ["cmake", "llvm", "ninja", "sccache", "vcpkg", "vcpkg-registry"])
        self.assertEqual(lock["vcpkg"]["requires"], ["vcpkg-registry"])

    def test_the_tool_folder_is_ignored(self):
        import subprocess
        done = subprocess.run(["git", "check-ignore", ".tools/x"], cwd=SCRIPTS.parent, capture_output=True, text=True)
        self.assertEqual(done.stdout.strip(), ".tools/x")


if __name__ == "__main__":
    unittest.main()
