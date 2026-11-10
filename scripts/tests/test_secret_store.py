# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The repository's own credentials: the untracked env file and its importer (owner, 2026-11-10)."""

import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
REPO = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS / "lib"))
import secret_store  # noqa: E402

SMTP = "api-" + "A" * 32
TOKEN = "sk-ant-oat01-" + "t" * 48


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


importer = load("office_import_secrets", SCRIPTS / "import-secrets.py")


def vault(values, calls=None):
    """A fake `run`: answers a vault read from `values` (item -> text, or None for a failed read); icacls succeeds."""
    def run(argv, **kw):
        if calls is not None:
            calls.append(argv)
        if Path(argv[0]).name.lower() == "icacls.exe":
            return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
        item = next((item for item in values if item in argv[-1]), None)
        value = values.get(item)
        return subprocess.CompletedProcess(argv, 0 if value is not None else 1, stdout=value or "", stderr="")
    return run


ITEMS = {name: spec["item"] for name, spec in secret_store.SECRETS.items()}


class Store(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.both = vault({ITEMS["SMTP2GO_API_KEY"]: SMTP + "\n", ITEMS["CLAUDE_CODE_OAUTH_TOKEN"]: TOKEN})

    def test_an_import_writes_both_credentials_and_they_read_back(self):
        outcome = secret_store.import_all(self.root, self.both)
        self.assertEqual(outcome, {"SMTP2GO_API_KEY": "imported", "CLAUDE_CODE_OAUTH_TOKEN": "imported"})
        self.assertEqual(secret_store.read_all(self.root), {"SMTP2GO_API_KEY": SMTP, "CLAUDE_CODE_OAUTH_TOKEN": TOKEN})
        self.assertEqual(secret_store.get("SMTP2GO_API_KEY", self.root), SMTP)
        folder = self.root / ".secrets"
        self.assertEqual(sorted(path.name for path in folder.iterdir()), ["office.env"])  # no temporary file left

    def test_a_value_of_the_wrong_shape_is_never_stored(self):
        bad = vault({ITEMS["SMTP2GO_API_KEY"]: "api-short", ITEMS["CLAUDE_CODE_OAUTH_TOKEN"]: "not a token"})
        outcome = secret_store.import_all(self.root, bad)
        self.assertEqual(set(outcome.values()), {"unavailable"})
        self.assertFalse(secret_store.env_path(self.root).exists())

    def test_a_vault_that_cannot_be_read_keeps_what_the_file_has(self):
        secret_store.import_all(self.root, self.both)
        locked = vault({ITEMS["SMTP2GO_API_KEY"]: None, ITEMS["CLAUDE_CODE_OAUTH_TOKEN"]: None})
        outcome = secret_store.import_all(self.root, locked)
        self.assertEqual(set(outcome.values()), {"kept"})
        self.assertEqual(secret_store.get("CLAUDE_CODE_OAUTH_TOKEN", self.root), TOKEN)

    def test_a_vault_read_that_cannot_start_is_unavailable_not_a_crash(self):
        def broken(argv, **kw):
            raise FileNotFoundError(argv[0])
        self.assertIsNone(secret_store.vault_read("op://x/y/z", broken))

    def test_a_malformed_or_unknown_line_in_the_file_is_absent(self):
        path = secret_store.env_path(self.root)
        path.parent.mkdir()
        path.write_text(f"SMTP2GO_API_KEY=api-truncated\nUNKNOWN={SMTP}\nCLAUDE_CODE_OAUTH_TOKEN={TOKEN}\n",
                        encoding="utf-8")
        self.assertEqual(secret_store.read_all(self.root), {"CLAUDE_CODE_OAUTH_TOKEN": TOKEN})

    def test_a_missing_or_undecodable_file_holds_nothing(self):
        self.assertEqual(secret_store.read_all(self.root), {})
        path = secret_store.env_path(self.root)
        path.parent.mkdir()
        path.write_bytes(b"\xff\xfe\x00bad")
        self.assertEqual(secret_store.read_all(self.root), {})

    def test_the_file_and_folder_are_restricted_to_the_current_user(self):
        calls = []
        secret_store.import_all(self.root, vault({ITEMS["SMTP2GO_API_KEY"]: SMTP,
                                                  ITEMS["CLAUDE_CODE_OAUTH_TOKEN"]: TOKEN}, calls))
        restricted = [argv for argv in calls if Path(argv[0]).name.lower() == "icacls.exe"]
        if sys.platform == "win32":
            self.assertGreaterEqual(len(restricted), 2)  # the folder and the file, before a value is written
            for argv in restricted:
                self.assertTrue(Path(argv[0]).is_absolute())
                self.assertIn("/inheritance:r", argv)

    def test_a_permission_change_that_fails_writes_no_credential(self):
        if sys.platform != "win32":
            self.skipTest("the permission change goes through icacls on Windows only")

        def failing_acl(argv, **kw):
            if Path(argv[0]).name.lower() == "icacls.exe":
                return subprocess.CompletedProcess(argv, 5, stdout="", stderr="Access is denied.")
            return self.both(argv, **kw)
        with self.assertRaises(OSError):
            secret_store.import_all(self.root, failing_acl)
        folder = self.root / ".secrets"
        self.assertEqual([path.name for path in folder.iterdir()] if folder.exists() else [], [])
        for path in self.root.rglob("*"):
            if path.is_file():
                self.assertNotIn(SMTP, path.read_text(encoding="utf-8", errors="replace"))

    def test_the_vault_is_read_through_wsl_inside_a_bounded_unit(self):
        calls = []
        secret_store.vault_read(ITEMS["SMTP2GO_API_KEY"], vault({ITEMS["SMTP2GO_API_KEY"]: SMTP}, calls))
        argv = calls[0]
        self.assertEqual(Path(argv[0]).parts[-2:], ("System32", "wsl.exe"))
        # wsl.exe starts systemd-run itself, so nothing (no profile) runs before the bounded unit exists.
        self.assertEqual(argv[1:4], ["-e", "systemd-run", "--user"])
        for flag in ("--pipe", "--wait", "--collect", f"RuntimeMaxSec={secret_store.LINUX_SECONDS}",
                     f"TimeoutStopSec={secret_store.LINUX_STOP_SECONDS}", f"MemoryMax={secret_store.LINUX_MEMORY}"):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index("--") + 1:argv.index("--") + 3], ["bash", "-lc"])
        self.assertLess(secret_store.LINUX_SECONDS + secret_store.LINUX_STOP_SECONDS, 90)


class Importer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def run_main(self, argv, run):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = importer.main(argv, run=run, root=self.root)
        return code, out.getvalue()

    def test_an_import_prints_names_and_states_and_never_a_value(self):
        code, text = self.run_main([], vault({ITEMS["SMTP2GO_API_KEY"]: SMTP, ITEMS["CLAUDE_CODE_OAUTH_TOKEN"]: TOKEN}))
        self.assertEqual(code, 0)
        self.assertIn("imported", text)
        self.assertIn("SMTP2GO_API_KEY", text)
        self.assertNotIn(SMTP, text)
        self.assertNotIn(TOKEN, text)

    def test_a_failed_permission_change_exits_1_and_prints_no_value(self):
        if sys.platform != "win32":
            self.skipTest("the permission change goes through icacls on Windows only")
        good = vault({ITEMS["SMTP2GO_API_KEY"]: SMTP, ITEMS["CLAUDE_CODE_OAUTH_TOKEN"]: TOKEN})

        def failing_acl(argv, **kw):
            if Path(argv[0]).name.lower() == "icacls.exe":
                return subprocess.CompletedProcess(argv, 5, stdout="", stderr="")
            return good(argv, **kw)
        code, text = self.run_main([], failing_acl)
        self.assertEqual(code, 1)
        self.assertIn("not imported", text)
        self.assertNotIn(SMTP, text)
        self.assertNotIn(TOKEN, text)

    def test_a_missing_credential_exits_1_and_says_what_to_run(self):
        code, text = self.run_main([], vault({ITEMS["SMTP2GO_API_KEY"]: SMTP, ITEMS["CLAUDE_CODE_OAUTH_TOKEN"]: None}))
        self.assertEqual(code, 1)
        self.assertIn("unavailable", text)
        self.assertIn("python scripts/import-secrets.py", text)
        self.assertEqual(secret_store.get("SMTP2GO_API_KEY", self.root), SMTP)  # the one that was read is kept

    def test_check_reads_no_vault(self):
        def no_vault(argv, **kw):
            raise AssertionError("--check must not read the vault")
        code, text = self.run_main(["--check"], no_vault)
        self.assertEqual(code, 1)
        self.assertIn("missing", text)


class Ignored(unittest.TestCase):
    def test_the_secrets_folder_is_ignored_by_git(self):
        result = subprocess.run(["git", "check-ignore", ".secrets/office.env"], cwd=REPO, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "the .secrets folder must be in .gitignore")

    def test_the_mailer_reads_an_imported_key_and_refuses_without_one(self):
        alert = load("office_alert_for_secrets", REPO / ".conclave" / "automations" / "alert.py")
        with tempfile.TemporaryDirectory() as tmp:
            alert.SECRETS_ROOT = tmp
            with self.assertRaises(alert.Refused):
                alert.key()  # nothing imported yet: refused, and no vault is read to make up for it
            secret_store.import_all(tmp, vault({ITEMS["SMTP2GO_API_KEY"]: SMTP, ITEMS["CLAUDE_CODE_OAUTH_TOKEN"]: TOKEN}))
            self.assertEqual(alert.key(), SMTP)


if __name__ == "__main__":
    unittest.main()
