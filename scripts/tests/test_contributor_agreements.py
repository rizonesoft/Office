# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""scripts/build-contributor-agreements.py: the agreements are the Harmony templates with only the recorded choices
filled in (D00 T02 §3), and the contributor guide leads to both."""
import contextlib
import importlib.util
import io
from pathlib import Path
import re
import shutil
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("build_agreements", REPO / "scripts" / "build-contributor-agreements.py")
agreements = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agreements)

INDIVIDUAL, ENTITY = "rizonesoft-cla.md", "rizonesoft-cla-entity.md"


def run(argv, root):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = agreements.main(argv, root=root)
    return code, out.getvalue() + err.getvalue()


class Agreements(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        shutil.copytree(REPO / "docs" / "legal", self.root / "docs" / "legal")

    def text(self, name):
        return (self.root / "docs" / "legal" / name).read_text(encoding="utf-8")

    def change(self, name, old, new):
        text = self.text(name)
        self.assertEqual(text.count(old), 1, old)
        (self.root / "docs" / "legal" / name).write_text(text.replace(old, new), encoding="utf-8", newline="\n")

    def test_the_committed_agreements_are_their_templates_with_the_choices_filled_in(self):
        self.assertEqual(run(["--check"], REPO), (0, "contributor agreements current\n"))

    def test_a_clause_dropped_reworded_or_added_fails_the_check_and_names_the_file(self):
        for name, old, new in (
                (INDIVIDUAL, "2.5 Our Rights. You acknowledge that We are not obligated to use Your Contribution as "
                             "part of the Material and may decide to include any Contribution We consider "
                             "appropriate.\n\n", ""),
                (ENTITY, "a perpetual, worldwide, non-exclusive, transferable, royalty-free, irrevocable patent license",
                 "a worldwide patent license"),
                (INDIVIDUAL, "## 4. Disclaimer", "2.7 You also assign every future work to Us.\n\n## 4. Disclaimer"),
                (ENTITY, "the Republic of South Africa excluding", "England and Wales excluding"),
                (INDIVIDUAL, "- **Lawyer's review (date, firm):** not yet reviewed.",
                 "- **Lawyer's review (date, firm):** 2026-11-13, a firm nobody engaged.")):
            with self.subTest(change=new or "dropped"):
                self.setUp()
                self.change(name, old, new)
                code, out = run(["--check"], self.root)
                self.assertEqual(code, 1, out)
                self.assertIn(f"docs/legal/{name} is not its template", out)
                self.assertNotIn("current", out)

    def test_a_build_restores_a_changed_agreement_from_its_template(self):
        self.change(INDIVIDUAL, "## 4. Disclaimer", "## 4. Promise")
        self.assertEqual(run([], self.root)[0], 0)
        self.assertEqual(self.text(INDIVIDUAL), (REPO / "docs" / "legal" / INDIVIDUAL).read_text(encoding="utf-8"))
        self.assertEqual(run(["--check"], self.root)[0], 0)
        self.assertEqual([p.name for p in (self.root / "docs" / "legal").glob(".tmp-*")], [])

    def test_a_template_that_is_not_the_recorded_version_is_refused(self):
        self.change("harmony/ha-cla-e-v1.txt", "irrevocable patent license", "revocable patent license")
        for argv in (["--check"], []):
            code, out = run(argv, self.root)
            self.assertEqual(code, 1, out)
            self.assertIn("docs/legal/harmony/ha-cla-e-v1.txt is not the Harmony version 1.0 text", out)
        self.assertEqual(self.text(ENTITY), (REPO / "docs" / "legal" / ENTITY).read_text(encoding="utf-8"))

    def test_every_clause_of_the_template_is_in_the_agreement_but_the_choices_left_out(self):
        for name, (template, kind, _) in agreements.TEMPLATES.items():
            blocks = [b for b in self.text(template).split("\n\n") if b.strip()]
            agreement = self.text(name)
            kept = [b for b in blocks[1:-1] if "[" not in b and not b.startswith("(Option ")
                    and not b.startswith(agreements.MEDIA)]
            self.assertGreater(len(kept), 40, kind)
            for block in kept:
                self.assertIn(block.replace("\t", " "), agreement, f"{kind}: {block[:50]}")
            self.assertEqual(re.findall(r"\[[A-Z_ ]+\]|\(Option ", agreement), [], kind)

    def test_the_choices_are_the_owners(self):
        for name in (INDIVIDUAL, ENTITY):
            text = self.text(name)
            self.assertIn('contributing to Rizonesoft ("We" or "Us")', text)
            self.assertIn("We may license the Contribution under any license, including copyleft, permissive, "
                          "commercial, or proprietary licenses. As a condition on the exercise of this right, We agree "
                          "to also license the Contribution under the terms of the license or licenses which We are "
                          "using for the Material on the Submission Date.", text)
            self.assertIn("in accordance with the laws of the Republic of South Africa excluding its conflicts of law",
                          text)
            self.assertNotIn("We agree to license the Contribution only under", text)  # options one to four
            self.assertNotIn("licenses for Media", text)
        self.assertIn("which You own, control or have the right to grant", self.text(INDIVIDUAL))
        self.assertIn("which You or Your Affiliates own, control or have the right to grant", self.text(ENTITY))
        self.assertNotIn("Affiliates", self.text(INDIVIDUAL).split("## Review")[0])

    def test_the_review_section_says_the_owner_approved_and_no_lawyer_has_reviewed(self):
        for name in (INDIVIDUAL, ENTITY):
            review = self.text(name).split("## Review", 1)[1]
            self.assertIn("**Approved:** by the owner of Rizonesoft on 2026-11-13", review)
            self.assertIn("No lawyer has reviewed this agreement.", review)
            self.assertIn("**Lawyer's review (date, firm):** not yet reviewed.", review)
            self.assertIn("Creative Commons Attribution 3.0 Unported License", review)


class Guide(unittest.TestCase):
    """The contributor guide is where a contributor starts: it leads to both agreements and to how to sign."""

    def test_the_guide_links_both_agreements_and_the_instructions_and_no_longer_says_pending(self):
        guide = (REPO / "CONTRIBUTING.md").read_text(encoding="utf-8")
        for target in ("docs/legal/rizonesoft-cla.md", "docs/legal/rizonesoft-cla-entity.md", "docs/legal/README.md"):
            self.assertIn(f"](./{target})", guide)
            self.assertTrue((REPO / target).is_file(), target)
        self.assertNotIn("once it has been reviewed by a lawyer", guide)
        self.assertNotIn("cannot be merged", guide)
        self.assertIn("not yet reviewed by a lawyer", guide)

    def test_the_instructions_the_agreements_point_to_exist(self):
        readme = (REPO / "docs" / "legal" / "README.md").read_text(encoding="utf-8")
        for heading in ("## Which agreement applies", "## Signing", "## Work you do not own", "## Review status"):
            self.assertIn(heading, readme)
        for name in (INDIVIDUAL, ENTITY):
            text = (REPO / "docs" / "legal" / name).read_text(encoding="utf-8")
            self.assertIn('`docs/legal/README.md` in the Rizonesoft Office repository ("Signing")', text)
            self.assertIn('`docs/legal/README.md` in the Rizonesoft Office repository ("Work you do not own")', text)
            self.assertIn(f"](./{name})", readme)


if __name__ == "__main__":
    unittest.main()
