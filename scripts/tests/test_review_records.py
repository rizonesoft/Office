# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Office's own additions to the imported review dispatcher: the rounds this repository recorded before the import
stay readable evidence."""
import importlib.util
import pathlib
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]


def load_dispatch():
    spec = importlib.util.spec_from_file_location("review_dispatch_records", REPO / "scripts" / "review-dispatch.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dispatch = load_dispatch()

ROUND = ("## Round 1: astra (`gpt-6-astra` via `codex`)\n\n- Writer: claude\n- Run: 2026-11-08T00:54:50Z\n"
         "- Effort: medium\n{extra}- Lines: 1\n\nOVERALL: approve\n")


class HistoricalRounds(unittest.TestCase):
    def test_a_round_recorded_with_its_review_type_is_read(self):
        # From 2026-11-08 to 2026-11-11 the pin had a `type` key and every round recorded it.
        rounds = dispatch.read_rounds(ROUND.format(extra="- Type: adversarial\n"))
        self.assertIsNotNone(rounds)
        self.assertEqual((rounds[0]["reviewer"], rounds[0]["type"], rounds[0]["review"]),
                         ("astra", "adversarial", "OVERALL: approve"))
        self.assertNotIn("type", dispatch.read_rounds(ROUND.format(extra=""))[0])

    def test_a_malformed_or_repeated_type_makes_the_file_unreadable(self):
        for extra in ("- Type: adversarial\n- Type: adversarial\n", "- Type: Not A Type\n"):
            with self.subTest(extra=extra):
                self.assertIsNone(dispatch.read_rounds(ROUND.format(extra=extra)))

    def test_a_new_round_records_no_type(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / "findings.md"
            dispatch.record(path, {"writer": "claude", "reviewer": "astra", "model": "gpt-6-astra", "cli": "codex",
                                   "effort": "medium", "failover": [], "review": "OVERALL: approve"},
                            "2026-11-11T00:00:00Z")
            self.assertNotIn("- Type:", path.read_text(encoding="utf-8"))

    def test_every_findings_file_in_the_repository_is_readable(self):
        unreadable = [path.relative_to(REPO).as_posix() for path in sorted((REPO / "docs" / "reviews").rglob("*.md"))
                      if dispatch.read_findings(path.read_bytes().decode("utf-8")) is None]
        self.assertEqual(unreadable, [])


if __name__ == "__main__":
    unittest.main()
