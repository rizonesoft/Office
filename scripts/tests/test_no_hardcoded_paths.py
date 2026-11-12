# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""No tool writes one machine's folder layout into its code (AGENTS.md, Working rules).

A drive-letter path, a home folder or a WSL mount in a script works on the PC it was written on and nowhere else.
Tools resolve such places instead: the repository from their own location, scratch from OFFICE_SCRATCH, a program
through PATH, vswhere or an environment variable. The only literals allowed are the standard Windows locations used
as the fallback of an environment lookup on the same line.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
FOLDERS = ("scripts", ".conclave/automations", ".claude/agents", ".github")
SUFFIXES = {".py", ".ps1", ".mjs", ".sh", ".json", ".toml", ".yml", ".yaml", ".md"}
MACHINE_PATH = re.compile(r"""(?<![A-Za-z])[A-Za-z]:[\\/]{1,2}[A-Za-z]{2}|/home/[a-z]|/mnt/[a-z]/|/Users/[A-Za-z]""")
# A standard Windows location given as the default of an environment lookup, on one line.
ENV_FALLBACK = re.compile(r"""environ\.get\(\s*["'](?:SystemRoot|ProgramFiles(?:\(x86\))?)["']\s*(?:\)\s*or|,)\s*r?["']"""
                          r"""C:\\{1,2}(?:Windows|Program Files(?: \(x86\))?)["']""")


def scanned(root=ROOT):
    """(relative path, path) of every file the scan reads."""
    for folder in FOLDERS:
        base = root / folder
        for path in sorted(base.rglob("*")) if base.is_dir() else ():
            rel = path.relative_to(root).as_posix()
            if (not path.is_file() or path.suffix.lower() not in SUFFIXES or "__pycache__" in path.parts
                    or rel.startswith("scripts/tests/")):  # tests hold fixture strings, which nothing opens
                continue
            yield rel, path


def offenders(root=ROOT):
    found = []
    for rel, path in scanned(root):
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if MACHINE_PATH.search(ENV_FALLBACK.sub("", line)):
                found.append(f"{rel}:{number}: {line.strip()[:120]}")
    return found


class NoHardcodedPaths(unittest.TestCase):
    def test_no_tool_names_a_machine_path(self):
        self.assertEqual(offenders(), [])

    def test_the_scan_sees_a_drive_path_a_home_folder_and_a_mount(self):
        for line in ('LOG = Path(r"R:\\scratch\\x.log")', "out = 'D:/GitHub/Office/build'", 'cd /home/someone/work',
                     "open('/mnt/c/Users/x')", 'p = "C:\\\\Users\\\\someone\\\\file"'):
            self.assertTrue(MACHINE_PATH.search(ENV_FALLBACK.sub("", line)), line)

    def test_the_tool_resolver_is_scanned_and_a_drive_path_in_it_fails(self):
        """D00 T04 §2: the resolver and the bootstrap are among the files scanned."""
        import shutil
        import tempfile
        files = ("scripts/bootstrap-tools.py", "scripts/lib/tool_lock.py")
        names = {rel for rel, _ in scanned()}
        for rel in files:
            self.assertIn(rel, names)
        for rel in files:
            with self.subTest(rel), tempfile.TemporaryDirectory() as tmp:
                copy = Path(tmp) / rel
                copy.parent.mkdir(parents=True)
                shutil.copyfile(ROOT / rel, copy)
                self.assertEqual(offenders(Path(tmp)), [])
                with open(copy, "a", encoding="utf-8") as out:
                    out.write('\nNINJA = r"D:\\Tools\\ninja.exe"\n')
                self.assertEqual(len(offenders(Path(tmp))), 1)

    def test_an_environment_fallback_and_ordinary_text_pass(self):
        for line in ('os.path.join(os.environ.get("SystemRoot") or r"C:\\Windows", "System32", "taskkill.exe")',
                     'Path(os.environ.get("ProgramFiles(x86)", r"C:\\Program Files (x86)")) / "Microsoft Visual Studio"',
                     "ratio = a:b", "see https://example.com/x", "HKLM:\\SOFTWARE\\Microsoft", "time 12:30"):
            self.assertIsNone(MACHINE_PATH.search(ENV_FALLBACK.sub("", line)), line)


if __name__ == "__main__":
    unittest.main()
