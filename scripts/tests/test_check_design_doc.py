"""scripts/check-design-doc.py: headings, placeholders, dashes and table width, each with a refusal fixture."""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_design_doc", SCRIPTS / "check-design-doc.py")
cdd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cdd)

GOOD = """# Naming brief

## Exclusions

Microsoft marks, listed one per line.

## Status bar and zoom

| Column | Value |
| ------ | ----- |
| a | b |

```text
A quoted dash \u2014 stays byte-exact inside a fence, as does TODO: here.
```
"""


def run(text, *required):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "doc.md"
        path.write_text(text, encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cdd.main([str(path), *[a for r in required for a in ("--require", r)]])
        return code, out.getvalue()


class Headings(unittest.TestCase):
    def test_conforming_document_passes(self):
        self.assertEqual(run(GOOD, "Exclusions", "Status bar", "status BAR AND ZOOM")[0], 0)

    def test_missing_heading_is_named(self):
        code, out = run(GOOD, "Constraints")
        self.assertEqual(code, 1)
        self.assertIn("missing heading: Constraints", out)

    def test_paragraph_text_does_not_satisfy_a_heading(self):
        self.assertEqual(run(GOOD, "Microsoft marks")[0], 1)

    def test_prefix_must_end_at_a_word_boundary(self):
        self.assertEqual(run(GOOD, "Status b")[0], 1)


    def test_trailing_hash_kept_unless_after_space(self):
        self.assertEqual(run("# T\n\n## C#\n", "C#")[0], 0)
        self.assertEqual(run("# T\n\n## Closing ##\n", "Closing")[0], 0)

    def test_empty_requirement_refused(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            run(GOOD, "")
        self.assertEqual(raised.exception.code, 2)


class Fences(unittest.TestCase):
    def test_unclosed_fence_is_reported(self):
        code, out = run("# T\n\n```\nhidden — dash\n")
        self.assertEqual(code, 1)
        self.assertIn("line 3: code fence is never closed", out)


class Placeholders(unittest.TestCase):
    def test_each_placeholder_reported_with_line(self):
        code, out = run("# T\n\nCHANGEME here\n\nstill tbd\n\nTODO: x\n\nLorem ipsum dolor\n")
        self.assertEqual(code, 1)
        for token in ("line 3", "line 5", "line 7", "line 9"):
            self.assertIn(token, out)


class Dashes(unittest.TestCase):
    def test_em_and_en_dash_in_prose_fail(self):
        code, out = run("# T\n\nOne \u2014 two\n\nPages 3\u20134\n")
        self.assertEqual(code, 1)
        self.assertIn("line 3: em dash", out)
        self.assertIn("line 5: en dash", out)

    def test_dash_inside_fence_passes(self):
        self.assertEqual(run("# T\n\n```\na \u2014 b\n```\n")[0], 0)


class WideRows(unittest.TestCase):
    def test_101_characters_fail_and_100_pass(self):
        row100 = "| " + "\u00a7" * 96 + " |"
        self.assertEqual(len(row100), 100)
        self.assertEqual(run(f"# T\n\n{row100}\n")[0], 0)
        row101 = row100[:-2] + "x |"
        self.assertEqual(len(row101), 101)
        code, out = run(f"# T\n\n{row101}\n")
        self.assertEqual(code, 1)
        self.assertIn("101 characters", out)


class Unreadable(unittest.TestCase):
    def test_missing_file_exits_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cdd.main(["Z:/no/such/file.md"]), 2)


if __name__ == "__main__":
    unittest.main()
