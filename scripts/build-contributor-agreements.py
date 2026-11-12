#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Build Rizonesoft's contributor agreements from the Project Harmony templates, changing nothing but the choices.

    python scripts/build-contributor-agreements.py           # write docs/legal/rizonesoft-cla.md and -entity.md
    python scripts/build-contributor-agreements.py --check   # fail if a committed agreement differs from a fresh build

The agreements are the Harmony Individual and Entity Contributor License Agreements, version 1.0, kept as fetched in
docs/legal/harmony/ (D00 T02 §3; owner decision 46 of docs/specs/2026-10-23-campaign-scope-design.md). An agreement
is its template with the bracketed placeholders filled in, the one outbound licence option the owner chose kept and
the others left out, Markdown headings, and a Review section. Nothing else may differ: this script is the whole list
of differences, and --check (which the tests run) refuses an agreement in which a clause was added, dropped or
reworded by hand.

Exit 0 when the agreements are written or current, 1 when --check finds a difference or a template is not the
version recorded here, 2 on a usage error.
"""
import argparse
import hashlib
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LEGAL = Path("docs/legal")
# The templates as published at harmonyagreements.org (docs/ha-cla-i-v1.odt and ha-cla-e-v1.odt, fetched 2026-11-13),
# one paragraph per block. The digests pin the version: a changed template is a new decision, not an edit.
TEMPLATES = {
    "rizonesoft-cla.md": ("harmony/ha-cla-i-v1.txt", "Individual",
                          "33977b91edab71c4b1cc14587fdaed7706487cc5fd799ef891c168468ec4e553"),
    "rizonesoft-cla-entity.md": ("harmony/ha-cla-e-v1.txt", "Entity",
                                 "74eab1d12b00b4db558f365f7554eab11a8c7f8cf91d07335be9c6490aeca363"),
}
RECIPIENT = "Rizonesoft"
JURISDICTION = "the Republic of South Africa"
INSTRUCTIONS = "`docs/legal/README.md` in the Rizonesoft Office repository (\"Signing\")"
NONOWNER = "`docs/legal/README.md` in the Rizonesoft Office repository (\"Work you do not own\")"
KEPT_OPTION = "(Option Five) "  # any licence, on condition that the Material's own licence is always among them
MEDIA = "In addition, We may use the following licenses for Media in the Contribution:"
TEMPLATE_LICENCE = "This work is licensed under a Creative Commons Attribution 3.0 Unported License."
APPROVED = "2026-11-13"


class Refused(Exception):
    pass


def agreement(template, kind):
    """The agreement's Markdown for one template's text."""
    blocks = [block for block in template.replace("\r\n", "\n").split("\n\n") if block.strip()]
    if blocks[0] != f"Harmony {kind} Contributor License Agreement" or blocks[-1].strip() != TEMPLATE_LICENCE:
        raise Refused(f"the {kind} template does not begin and end as Harmony version 1.0 does")
    options = [block for block in blocks if block.startswith("(Option ")]
    if len(options) != 5 or sum(block.startswith(KEPT_OPTION) for block in options) != 1 \
            or sum(block.startswith(MEDIA) for block in blocks) != 1:
        raise Refused(f"the {kind} template does not hold the five outbound options and the Media clause")
    out = [f"# Rizonesoft {kind} Contributor License Agreement"]
    for block in blocks[1:-1]:
        if block.startswith("(Option ") and not block.startswith(KEPT_OPTION):
            continue  # the four outbound options the owner did not choose
        if block.startswith(MEDIA):
            continue  # optional in the template: no separate licences are named for Media
        block = block.removeprefix(KEPT_OPTION)
        block = block.replace("[PROJECT_NAME]", RECIPIENT).replace("[SUBMISSION_INSTRUCTIONS]", INSTRUCTIONS)
        block = block.replace("[NONOWNER_INSTRUCTIONS]", NONOWNER).replace("[JURISDICTION]", JURISDICTION)
        block = block.replace(" [or Your Affiliates]", " or Your Affiliates" if kind == "Entity" else "")
        block = block.replace("\t", " ")
        if re.fullmatch(r"\d\. [A-Z][A-Za-z ]+", block):
            block = "## " + block
        elif re.fullmatch(r"\d\.\d [A-Z][A-Za-z ]+", block):
            block = "### " + block
        out.append(block)
    text = "\n\n".join(out)
    left = re.findall(r"\[[A-Z_ ]+\]|\(Option ", text)
    if left:
        raise Refused(f"the {kind} agreement still holds {', '.join(sorted(set(left)))}")
    return text + "\n\n" + review(kind)


def review(kind):
    """The Review section: what the text is, who approved it, and that no lawyer has reviewed it yet."""
    return "\n\n".join([
        "## Review",
        f"- **Text:** the Harmony {kind} Contributor License Agreement, version 1.0, as published at "
        f"harmonyagreements.org and kept in `{(LEGAL / TEMPLATES[file_of(kind)][0]).as_posix()}`, with its choices "
        f"filled in and nothing reworded: the recipient is {RECIPIENT}, the outbound licence is the template's Option "
        f"Five (any licence, and always also the licence of the Material on the Submission Date), the governing law "
        f"is that of {JURISDICTION}, and the template's optional clause naming separate licences for Media is left "
        f"out. `python scripts/build-contributor-agreements.py --check` proves it against the template.",
        f"- **Approved:** by the owner of {RECIPIENT} on {APPROVED}, in the form committed here "
        f"(decision 46 of `docs/specs/2026-10-23-campaign-scope-design.md`).",
        "- **Legal review:** none yet. No lawyer has reviewed this agreement. The owner chose to bring it into force "
        "on the template's own wording and to have it reviewed later; the review's date and firm are recorded on the "
        "next line when it happens, and until then the line says so.",
        "- **Lawyer's review (date, firm):** not yet reviewed.",
        f"- **Open point for that review:** the agreement names {RECIPIENT} as it trades; the registered name of the "
        "legal person behind it is to be confirmed and written into the first sentence.",
        "- **Licence of this text:** like the template it is made from, this agreement is licensed under a Creative "
        "Commons Attribution 3.0 Unported License; it is based on the Harmony agreements of the Project Harmony "
        "community.",
    ]) + "\n"


def file_of(kind):
    return next(name for name, (_, k, _) in TEMPLATES.items() if k == kind)


def built(root=ROOT):
    """{file name: agreement text} for both agreements, each template first held to its recorded version."""
    out = {}
    for name, (template, kind, digest) in TEMPLATES.items():
        path = Path(root) / LEGAL / template
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise Refused(f"cannot read {path}: {error}") from None
        if hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest() != digest:
            raise Refused(f"{(LEGAL / template).as_posix()} is not the Harmony version 1.0 text recorded in this script")
        out[name] = agreement(raw.decode("utf-8"), kind)
    return out


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as out:
            out.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if a committed agreement differs from a fresh build")
    args = parser.parse_args(argv)
    try:
        files = built(root)
    except Refused as error:
        print(f"contributor agreements: {error}", file=sys.stderr)
        return 1
    stale = []
    for name, text in files.items():
        path = Path(root) / LEGAL / name
        current = path.read_text(encoding="utf-8").replace("\r\n", "\n") if path.is_file() else None
        if current != text:
            stale.append(name)
            if not args.check:
                write(path, text)
    if args.check and stale:
        for name in stale:
            print(f"contributor agreements: {(LEGAL / name).as_posix()} is not its template with only the recorded "
                  f"choices filled in; run python scripts/build-contributor-agreements.py", file=sys.stderr)
        return 1
    print("contributor agreements current" if not stale else f"contributor agreements written: {', '.join(stale)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
