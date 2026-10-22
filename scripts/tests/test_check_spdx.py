# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/check-spdx.py: every tracked source file states its licence, and third-party ones only with their notice."""
import codecs
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_spdx", SCRIPTS / "check-spdx.py")
spdx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spdx)

TAG = "SPDX-" + "License-Identifier:"  # in parts, so this file's own licence is the only tag REUSE reads here


SLASH_KINDS = (".mjs", ".cpp", ".cppm", ".ixx", ".h", ".hpp", ".rc", ".hlsl")

class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        subprocess.run(["git", "-C", str(self.root), "add", rel], check=True)

    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = spdx.main(list(argv), root=self.root)
        return code, out.getvalue() + err.getvalue()


class Identifiers(Repo):
    def test_a_file_with_the_project_licence_passes(self):
        self.add("scripts/ok.py", f"#!/usr/bin/env python3\n# {TAG} GPL-3.0-or-later\n# Copyright 2026 Rizonesoft\n")
        self.assertEqual(self.run_main()[0], 0)

    def test_a_file_without_the_line_is_refused_by_name(self):
        self.add("scripts/ok.py", f"# {TAG} GPL-3.0-or-later\n")
        self.add("scripts/bare.py", "print('no licence')\n")
        code, out = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("scripts/bare.py: no", out)
        self.assertNotIn("scripts/ok.py", out)

    def test_the_line_must_be_in_the_first_ten_lines(self):
        self.add("scripts/late.py", "\n" * 10 + f"# {TAG} GPL-3.0-or-later\n")
        self.assertEqual(self.run_main()[0], 1)

    def test_every_source_kind_and_extensionless_hooks_are_checked(self):
        kinds = ("a.mjs", "b.ps1", "c.sh", "d.cpp", "e.cppm", "f.ixx", "g.h", "h.hpp", "i.rc", "j.hlsl",
                 "k.manifest", "l.cmake", "src/CMakeLists.txt", "lib/cmakelists.txt", "scripts/hooks/pre-commit")
        for rel in kinds:
            self.add(rel, "nothing\n")
        self.add("notes.md", "prose is not source\n")
        self.add("CMakeLists.txt.bak", "a backup is not source\n")
        code, out = self.run_main()
        self.assertEqual(code, 1)
        for rel in kinds:
            self.assertIn(f"{rel}: no", out)
        self.assertNotIn("notes.md", out)
        self.assertNotIn("CMakeLists.txt.bak", out)
        for rel in kinds:
            marker = "<!--" if rel.endswith(".manifest") else "//" if rel.endswith(SLASH_KINDS) else "#"
            closing = " -->" if marker == "<!--" else ""
            self.add(rel, f"{marker} {TAG} GPL-3.0-or-later{closing}\n")
        code, out = self.run_main()
        self.assertEqual(code, 0, out)

    def test_only_a_whole_single_declaration_counts(self):
        cases = {"compound.py": f"# {TAG} GPL-3.0-or-later AND Apache-2.0\n",
                 "prefixed.py": f"# Not{TAG} GPL-3.0-or-later\n",
                 "underscored.py": f"# Not_{TAG} GPL-3.0-or-later\n",
                 "accented.py": f"# é{TAG} GPL-3.0-or-later\n",
                 "trailing.py": f"x = 1  # {TAG} GPL-3.0-or-later\n",
                 "twice.py": f"# {TAG} GPL-3.0-or-later\n# {TAG} Apache-2.0\n"}
        for rel, text in cases.items():
            self.add(rel, text)
        self.add("app.manifest", f"<!-- {TAG} GPL-3.0-or-later -->\n")
        self.add("main.cpp", f"// {TAG} GPL-3.0-or-later\n")
        code, out = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("compound.py: 'GPL-3.0-or-later AND Apache-2.0' is not a single licence identifier", out)
        for rel in ("prefixed.py", "underscored.py", "accented.py", "trailing.py"):
            self.assertIn(f"{rel}: no", out)
        self.assertIn("twice.py: 2 ", out)
        self.assertNotIn("app.manifest", out)
        self.assertNotIn("main.cpp", out)

    def test_a_header_after_a_byte_order_mark_and_with_crlf_passes(self):
        path = self.root / "tools/install.ps1"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"\xef\xbb\xbf# " + TAG.encode() + b" GPL-3.0-or-later\r\n# Copyright 2026 Rizonesoft\r\n")
        subprocess.run(["git", "-C", str(self.root), "add", "tools/install.ps1"], check=True)
        self.assertEqual(self.run_main()[0], 0)

    def test_a_header_in_any_unicode_encoding_with_its_mark_passes(self):
        header = f"# {TAG} GPL-3.0-or-later\r\n# Copyright 2026 Rizonesoft\r\n"
        for n, codec in enumerate(("utf-16", "utf-16-be", "utf-32", "utf-32-be")):
            data = header.encode(codec)
            if codec.endswith("-be"):  # the explicit-endian codecs write no mark; add the big-endian one
                data = {"utf-16-be": codecs.BOM_UTF16_BE, "utf-32-be": codecs.BOM_UTF32_BE}[codec] + data
            rel = f"tools/h{n}.ps1"
            (self.root / "tools").mkdir(exist_ok=True)
            (self.root / rel).write_bytes(data)
            subprocess.run(["git", "-C", str(self.root), "add", rel], check=True)
        code, out = self.run_main()
        self.assertEqual(code, 0, out)

    def test_a_tracked_file_missing_from_the_working_tree_is_refused(self):
        self.add("scripts/ok.py", f"# {TAG} GPL-3.0-or-later\n")
        self.add("scripts/bad.py", "print()\n")
        (self.root / "scripts/bad.py").unlink()  # deleted, deletion not staged: the index still holds it
        code, out = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("scripts/bad.py: tracked but missing", out)

    def test_an_untracked_file_is_not_checked(self):
        (self.root / "loose.py").write_text("print()\n", encoding="utf-8")
        self.assertEqual(self.run_main()[0], 0)


class ThirdParty(Repo):
    NOTICES = "# Third-Party Notices\n\n### Vendored lib\n\n- Licence: MIT. The notice below.\n"

    def test_a_vendored_mit_file_passes_when_allowed_and_recorded(self):
        self.add("THIRD-PARTY-NOTICES.md", self.NOTICES)
        self.add("vendor/lib.py", f"# {TAG} MIT\n")
        self.assertEqual(self.run_main()[0], 1)  # not allowed: refused
        self.assertEqual(self.run_main("--allow", "MIT")[0], 0)

    def test_an_unknown_identifier_is_refused(self):
        self.add("THIRD-PARTY-NOTICES.md", self.NOTICES)
        self.add("vendor/lib.py", f"# {TAG} Apache-2.0\n")
        code, out = self.run_main("--allow", "MIT")
        self.assertEqual(code, 1)
        self.assertIn("vendor/lib.py: Apache-2.0 is not", out)

    def test_allowing_a_licence_the_notices_do_not_record_is_refused(self):
        self.add("THIRD-PARTY-NOTICES.md", self.NOTICES)
        code, out = self.run_main("--allow", "Apache-2.0")
        self.assertEqual(code, 2)
        self.assertIn("Apache-2.0 not recorded", out)


class Repository(unittest.TestCase):
    def test_this_repository_passes(self):
        self.assertEqual(spdx.main([], root=SCRIPTS.parent), 0)


if __name__ == "__main__":
    unittest.main()
