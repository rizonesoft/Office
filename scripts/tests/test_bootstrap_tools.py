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

    def __call__(self, url, timeout=None):
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
