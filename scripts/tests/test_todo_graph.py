# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Tests for scripts/lib/todo_graph.py and scripts/todo-graph.py: the graph refuses malformed work and stamps only real evidence."""
import dataclasses
import json
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
import todo_graph as tg  # noqa: E402

ADJACENCY = ("**Adjacency:** list=not-applicable (fixture); document=not-applicable (fixture); "
             "settings=not-applicable (fixture); reporting=not-applicable (fixture); "
             "notifications=not-applicable (fixture); permissions=not-applicable (fixture); "
             "audit=not-applicable (fixture); exchange=not-applicable (fixture); "
             "reverse=not-applicable (fixture)")


FIXTURE_ACTION = "**Owner action:** answer in the session; the session records it and removes the Need.\n"


def section(n, title, phase, needs, extra=""):
    # A section waiting on the owner carries an owner action (D00 T03 §35), so every fixture is valid as written.
    waits = bool({v.strip() for v in needs.split(",")} & tg.OWNER_NEEDS)
    action = FIXTURE_ACTION if waits else ""
    return (f"## {n}. {title}\n\n**Phase:** {phase}\n**Needs:** {needs}\n{action}**Surface:** no\n\n**Build order:**\n\n"
            f"1. Do it. Done when: it shows.\n\n- [ ] Work.\n- [ ] Commit: `x: {title.lower()}`\n\n"
            f"**Test checkpoint:** `true` exits 0.{extra}\n")


def envelope(n, reviewer="astra (`m` via `codex`)", overall="approve"):
    """One round as scripts/review-dispatch.py records it (without the optional Lines and Digest fields)."""
    return f"## Round {n}: {reviewer}\n\n- Writer: claude\n- Run: 2026-10-21T00:00:00Z\n\nReview text.\n\nOVERALL: {overall}\n\n"


def todo_file(rows, *, ident="alpha", domain="00-workspace", status="active", depends_on=None,
              table_override=None, inputs="- i"):
    """rows: (number, title, phase, needs, depends) tuples."""
    front = ["schema_version: 1", f"id: {ident}", f"domain: {domain}", f"status: {status}",
             'title: "TODO-01 -- A"']
    if depends_on is not None:
        front.append("depends_on: " + json.dumps(depends_on))
    table = table_override or "\n".join(
        f"| {i} | §{n} | {t} | {dep} | [ ] |" for i, (n, t, _, _, dep) in enumerate(rows, 1))
    bodies = "\n".join(section(n, t, ph, nd) for n, t, ph, nd, _ in rows)
    return ("---\n" + "\n".join(front) + "\n---\n\n# TODO-01 -- A\n\n> **Goal:** g.\n\n"
            "> **Current state:** c.\n\n## Inputs\n\n" + inputs + "\n\n## Outcome\n\n- o\n\n"
            + ADJACENCY + "\n\n"
            "## Implementation Order\n\n| Order | Section | Deliverable | Depends On | Status |\n"
            "| ----- | ------- | ----------- | ---------- | ------ |\n"
            + table + "\n\n" + bodies + "\n## Verification\n\n- v\n")


class Tree(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "todo/00-workspace").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, text, name="TODO-01-a.md", domain="00-workspace", index=True):
        d = self.root / "todo" / domain
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(text, encoding="utf-8")
        if index:
            self.index(name, domain)

    def index(self, name, domain="00-workspace"):
        domain_index = self.root / "todo" / domain / "INDEX.md"
        existing = domain_index.read_text(encoding="utf-8") if domain_index.exists() else "# Index\n"
        if name not in existing:
            domain_index.write_text(existing + f"- {name}\n", encoding="utf-8")
        root_index = self.root / "todo/TODO-00-INDEX.md"
        root_existing = root_index.read_text(encoding="utf-8") if root_index.exists() else "# Index\n"
        entry = f"{domain}/{name}"
        if entry not in root_existing:
            root_index.write_text(root_existing + f"- {entry}\n", encoding="utf-8")

    def refuses(self, fragment):
        with self.assertRaises(tg.Refused) as ctx:
            tg.graph(self.root)
        self.assertIn(fragment, str(ctx.exception))


class Graph(Tree):
    def test_valid_tree_orders_by_phase_and_dependency(self):
        self.write(todo_file([(1, "Late", 1, "none", "--"), (2, "Early", 0, "none", "--"),
                              (3, "After early", 0, "windows-host", "§2")]))
        rows = tg.graph(self.root)
        self.assertEqual([r.ref for r in tg.ordered(rows)],
                         ["D00 T01 §2", "D00 T01 §3", "D00 T01 §1"])
        self.assertEqual(tg.disposition(rows["D00 T01 §2"], rows), 0)
        self.assertEqual(tg.disposition(rows["D00 T01 §3"], rows), 4)

    def test_table_order_decides_among_ready_sections(self):
        table = "| 1 | §2 | B | -- | [ ] |\n| 2 | §1 | A | -- | [ ] |"
        self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "none", "--")],
                             table_override=table))
        self.assertEqual([r.ref for r in tg.ordered(tg.graph(self.root))],
                         ["D00 T01 §2", "D00 T01 §1"])

    def test_empty_tree_refuses(self):
        self.refuses("missing or empty")

    def test_malformed_row_is_not_empty_work(self):
        self.write(todo_file([(1, "A", 0, "none", "--")], table_override="| 1 | §1 | A | -- | [?] |"))
        self.refuses("malformed implementation row")

    def test_row_without_body_refuses(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace(
            "| 1 | §1 | A | -- | [ ] |", "| 1 | §1 | A | -- | [ ] |\n| 2 | §2 | B | -- | [ ] |")
        self.write(text)
        self.refuses("row/body mismatch")

    def test_cycle_refuses(self):
        self.write(todo_file([(1, "A", 0, "none", "§2"), (2, "B", 0, "none", "§1")]))
        self.refuses("dependency cycle")

    def test_prerequisite_in_a_later_phase_refuses(self):
        self.write(todo_file([(1, "A", 0, "none", "§2"), (2, "B", 1, "none", "--")]))
        self.refuses("prerequisite in later phase")

    def test_unknown_need_refuses(self):
        self.write(todo_file([(1, "A", 0, "novamira", "--")]))
        self.refuses("unknown/duplicate Needs")

    def test_commit_must_be_the_last_item(self):
        self.write(todo_file([(1, "A", 0, "none", "--")]).replace(
            "- [ ] Commit: `x: a`", "- [ ] Commit: `x: a`\n- [ ] After."))
        self.refuses("Commit last")

    def test_table_line_without_its_leading_pipe_refuses(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace(
            "| 1 | §1 | A | -- | [ ] |", "| 1 | §1 | A | -- | [ ] |\n | 2 | §999 | Orphan | -- | [ ] |")
        self.write(text)
        self.refuses("without a leading pipe")

    def test_unknown_level_two_heading_refuses(self):
        for bad in ("## Remaining work", "## Inputs ", "##\tNotes", "## Inputs", "## Verification", "## Outcome"):
            self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "none", "--")]).replace(
                "## 2. B\n", bad + "\n\n- [ ] Unfinished required work.\n\n## 2. B\n"))
            self.refuses("level-two headings must be")

    def test_deferral_marker_outside_a_blockquote_refuses(self):
        for bad in ("**Deferred:** Unimplemented required work.", ">**Resolved:** done -> XREF: §1",
                    "Note **Deferred:** later -> XREF: §2"):
            self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "none", "--")]).replace(
                "- [ ] Work.", "- [ ] Work.\n\n" + bad + "\n", 1))
            self.refuses("must open a blockquote line and say something")

    def test_checklist_item_in_another_spelling_refuses(self):
        for bad in ("1. [ ] Unfinished work.", "2) [x] Done elsewhere.", "> - [ ] Quoted work.", ">- [ ] Quoted.",
                    "  - [ ] Indented work.", "> 1. [ ] Quoted and numbered."):
            self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "none", "--")]).replace(
                "- [ ] Work.", "- [ ] Work.\n" + bad, 1))
            self.refuses("malformed checklist item")

    def test_two_deferral_markers_on_one_line_refuse(self):
        self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "none", "--")]).replace(
            "**Test checkpoint:** `true` exits 0.\n\n## 2. B",
            "**Test checkpoint:** `true` exits 0.\n> **Resolved:** old -> XREF: §2 **Deferred:** new unowned work.\n\n## 2. B"))
        self.refuses("one Deferred or Resolved marker per line")

    def test_reference_run_into_more_text_does_not_resolve(self):
        self.write(todo_file([(1, "A", 0, "none", "--")]))
        rows = tg.graph(self.root)
        for text in ("D00 T01 §1oops", "D00 T01 §1.5", "todo/00-workspace/TODO-01-a.md §1x"):
            self.assertEqual(tg.extract_ref(text, rows), (None, 2))
        for text in ("D00 T01 §1", "process D00 T01 §1.", "D00 T01 §1 (run file x)", "| 1 | D00 T01 §1 | A |"):
            self.assertEqual(tg.extract_ref(text, rows), ("D00 T01 §1", 0))

    def test_empty_deferral_marker_refuses(self):
        for bad in ("> **Deferred:**", "> **Resolved:**   "):
            self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "none", "--")]).replace(
                "**Test checkpoint:** `true` exits 0.\n\n## 2. B", "**Test checkpoint:** `true` exits 0.\n" + bad + "\n\n## 2. B"))
            self.refuses("must open a blockquote line and say something")

    def test_malformed_xref_does_not_resolve_to_another_section(self):
        for bad in ("-> XREF: D00 T999 §1", "-> XREF: §1x", "-> XREF: D00 T01 §1.5", "-> XREF:§1", "-> XREF: D00 T01 §1 -> XREF: D00 T99 §999",
                    "-> XREF: none yet"):
            self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "none", "--")], inputs="- i " + bad))
            with self.assertRaises(tg.Refused):
                tg.graph(self.root)
        self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "none", "--")],
                             inputs="- see §2 -> XREF: §2 (the second)"))
        tg.graph(self.root)

    def test_malformed_checklist_item_refuses(self):
        for bad in ("- [?] Work.", "- [] Work.", "- [X] Work.", "- Work without checkbox."):
            self.write(todo_file([(1, "A", 0, "none", "--")]).replace("- [ ] Work.", bad))
            self.refuses("malformed checklist item")

    def test_empty_build_order_refuses(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace(
            "1. Do it. Done when: it shows.\n\n- [ ] Work.",
            "- [ ] Work. Done when: it shows.")
        self.write(text)
        self.refuses("executable Build order required")
        missing_second = todo_file([(1, "A", 0, "none", "--")]).replace(
            "1. Do it. Done when: it shows.",
            "1. Do it. Done when: it shows.\n2. Second step without acceptance criterion.")
        self.write(missing_second)
        self.refuses("executable Build order required")

    def test_empty_field_does_not_borrow_next_line(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace(
            "**Test checkpoint:** `true` exits 0.",
            "**Test checkpoint:**\n> **Deferred:** `later` -> XREF: D00 T01 §1")
        self.write(text)
        self.refuses("missing Test checkpoint field")

    def test_missing_todo_heading_refuses(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace("# TODO-01 -- A\n\n", "")
        self.write(text)
        self.refuses("missing TODO heading")

    def test_section_zero_refuses(self):
        self.write(todo_file([(0, "Zero", 0, "none", "--")]))
        self.refuses("malformed implementation row")

    def test_waiting_needs_are_not_ready(self):
        self.write(todo_file([(1, "A", 0, "owner-decision, windows-host", "--")]))
        rows = tg.graph(self.root)
        self.assertEqual(tg.disposition(rows["D00 T01 §1"], rows), 4)

    def test_operator_needs_are_not_ready(self):
        self.write(todo_file([(1, "A", 99, "operator", "--")]))
        rows = tg.graph(self.root)
        self.assertEqual(tg.disposition(rows["D00 T01 §1"], rows), 4)

    def test_withdrawn_cloud_phase_98_refuses(self):
        # Phase 98 (Recto Cloud, foundation plan D20) was withdrawn on 2026-10-21; the closed list is the SDK's again.
        self.write(todo_file([(1, "Cloud", 98, "none", "--")]))
        self.refuses("invalid Phase")

    def test_phase_outside_the_closed_list_refuses(self):
        self.write(todo_file([(1, "A", 50, "none", "--")]))
        self.refuses("invalid Phase")

    def test_draft_file_is_not_ready(self):
        self.write(todo_file([(1, "A", 0, "none", "--")], status="draft"))
        rows = tg.graph(self.root)
        self.assertEqual(tg.disposition(rows["D00 T01 §1"], rows), 4)

    def test_file_dependency_reaches_every_section(self):
        self.write(todo_file([(1, "A", 0, "none", "--")], ident="first"))
        self.write(todo_file([(1, "B", 1, "none", "--"), (2, "C", 1, "none", "--")],
                             ident="second", depends_on=["first"]), name="TODO-02-b.md")
        rows = tg.graph(self.root)
        self.assertEqual(rows["D00 T02 §2"].depends, ["D00 T01 §1"])

    def test_checked_row_without_stamp_refuses(self):
        self.write(todo_file([(1, "A", 0, "none", "--")]).replace("| [ ] |", "| [x] |"))
        self.refuses("checkbox/stamp/receipt mismatch")

    def test_missing_from_index_refuses(self):
        self.write(todo_file([(1, "A", 0, "none", "--")]), index=False)
        (self.root / "todo/TODO-00-INDEX.md").write_text("# Index\n", encoding="utf-8")
        (self.root / "todo/00-workspace/INDEX.md").write_text("# Index\n", encoding="utf-8")
        self.refuses("missing from domain index")

    def test_root_index_requires_domain_qualified_entry(self):
        self.write(todo_file([(1, "A", 0, "none", "--")], ident="first"))
        self.write(todo_file([(1, "B", 1, "none", "--")], ident="second", domain="01-engine"),
                   name="TODO-01-a.md", domain="01-engine", index=False)
        (self.root / "todo/01-engine/INDEX.md").write_text("# Index\n- TODO-01-a.md\n", encoding="utf-8")
        self.refuses("missing from root index: 01-engine/TODO-01-a.md")

    def test_adjacency_missing_key_refuses(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace(
            "reverse=not-applicable (fixture)", "reverse=not-applicable")
        self.write(text)
        self.refuses("adjacency entry malformed")

    def test_adjacency_blanket_form_is_valid(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace(
            ADJACENCY, "**Adjacency:** all=not-applicable (fixture with no record of its own)")
        self.write(text)
        self.assertEqual(len(tg.graph(self.root)), 1)

    def test_adjacency_blanket_reason_may_contain_semicolons(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace(
            ADJACENCY, "**Adjacency:** all=not-applicable (tooling over files; its records are the "
                       "files themselves, owned by their own sections)")
        self.write(text)
        self.assertEqual(len(tg.graph(self.root)), 1)

    def test_one_sided_xref_refuses(self):
        self.write(todo_file([(1, "A", 0, "none", "--")], ident="first"))
        self.write(todo_file([(1, "B", 0, "none", "--")], ident="second",
                             inputs="- -> XREF: D00 T01 §1 -- consumes it"), name="TODO-02-b.md")
        self.refuses("one-sided XREF")

    def test_reciprocal_xref_is_valid(self):
        self.write(todo_file([(1, "A", 0, "none", "--")], ident="first",
                             inputs="- -> XREF: D00 T02 §1 -- feeds it"))
        self.write(todo_file([(1, "B", 0, "none", "--")], ident="second",
                             inputs="- -> XREF: D00 T01 §1 -- consumes it"), name="TODO-02-b.md")
        self.assertEqual(len(tg.graph(self.root)), 2)

    def test_surface_yes_without_fidelity_refuses(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace("**Surface:** no", "**Surface:** yes")
        self.write(text)
        self.refuses("missing Fidelity field")

    def test_freeze_check_without_frozen_refuses(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace(
            "**Test checkpoint:**", "**Freeze check:** fixtures hold.\n\n**Test checkpoint:**")
        self.write(text)
        self.refuses("Freeze check must match frozen")

    def test_deferral_without_owner_refuses(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace(
            "**Test checkpoint:**", "> **Deferred:** later, somehow\n\n**Test checkpoint:**")
        self.write(text)
        self.refuses("without a resolving owner")

    def test_max_sections_per_file_refuses(self):
        rows = [(n, f"S{n}", 0, "none", "--") for n in range(1, 57)]
        self.write(todo_file(rows))
        self.refuses("over 55 sections")

    def test_max_items_per_section_refuses(self):
        many = "\n".join(f"- [ ] Item {i}." for i in range(1, 31))
        text = todo_file([(1, "A", 0, "none", "--")]).replace("- [ ] Work.", many)
        self.write(text)
        self.refuses("2-30 items")

    def test_deliverable_or_title_over_max_len_refuses(self):
        self.write(todo_file([(1, "X" * 89, 0, "none", "--")]))
        self.refuses("deliverable/title over 88 chars (wraps raw md table): D00 T01 §1")
        # The limit is the title's, which the table shows; the "## N. " prefix appears in no table. An 88-character
        # title passes that rule, and is then refused only because its plan row is too wide (D00 T03 §32).
        self.write(todo_file([(1, "X" * 88, 0, "none", "--")]))
        self.refuses("plan table for phase 0 wraps raw md (130 > 120 chars)")

    def test_superseded_without_successor_refuses(self):
        self.write(todo_file([(1, "A", 0, "none", "--")], status="superseded"))
        self.refuses("superseded TODO must name its successor")

    def test_projection_check_detects_drift(self):
        self.write(todo_file([(1, "A", 0, "none", "--")]))
        tg.projections(self.root, sync=True)
        tg.projections(self.root)
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        path.write_text(path.read_text(encoding="utf-8").replace("**Phase:** 0", "**Phase:** 2"),
                        encoding="utf-8")
        with self.assertRaises(tg.Refused):
            tg.projections(self.root)

    def test_resolve_accepts_windows_and_posix_paths_and_plan_rows(self):
        self.write(todo_file([(1, "A", 0, "none", "--")]))
        rows = tg.graph(self.root)
        for query in (
            "D00 T01 §1",
            "| [ ] | D00 T01 §1 | A | none | 2 |",
            "todo/00-workspace/TODO-01-a.md §1",
            r"R:\GitHub\RectoPDF\todo\00-workspace\TODO-01-a.md §1",
        ):
            self.assertEqual(tg.extract_ref(query, rows), ("D00 T01 §1", 0))
        self.assertEqual(tg.extract_ref(r"R:\GitHub\RectoPDF\todo\00-workspace\TODO-01-a.md §9", rows),
                         ("D00 T01 §9", 1))
        self.assertEqual(tg.extract_ref("no reference here", rows), (None, 2))

    def test_deep_dependency_chain_validates_without_recursion_error(self):
        for file_num in range(1, 21):
            rows = []
            for sec_num in range(1, 56):
                if file_num == 20 and sec_num == 55:
                    dep = "--"
                elif sec_num < 55:
                    dep = f"D00 T{file_num:02d} §{sec_num + 1}"
                else:
                    dep = f"D00 T{file_num + 1:02d} §1"
                rows.append((sec_num, f"S{sec_num}", 0, "none", dep))
            self.write(todo_file(rows, ident=f"file-{file_num:02d}"),
                       name=f"TODO-{file_num:02d}-chain.md")
        parsed = tg.graph(self.root)
        self.assertEqual(len(parsed), 1100)
        ordered_refs = [r.ref for r in tg.ordered(parsed)]
        self.assertEqual(len(ordered_refs), 1100)
        self.assertEqual(ordered_refs[0], "D00 T20 §55")
        self.assertEqual(ordered_refs[-1], "D00 T01 §1")


# Stamping, the receipts it writes and the review evidence they are held to: scripts/tests/test_todo_stamp.py.


class StillToAuthor(Tree):
    """The plan lists the TODO files Author items name that are not on disk yet (D00 T03 §31)."""

    def authoring(self, items_by_section, *, extra_rows=()):
        """One file whose section N carries the given checklist lines in place of its work item."""
        rows = [(n, f"S{n}", 0, "none", "--") for n in sorted(items_by_section)] + list(extra_rows)
        text = todo_file(rows)
        for n, items in items_by_section.items():
            head = f"## {n}. S{n}\n"
            start = text.index(head)
            at = text.index("- [ ] Work.\n", start)
            text = text[:at] + "".join(f"{item}\n" for item in items) + text[at + len("- [ ] Work.\n"):]
        self.write(text)

    def authored(self, name="TODO-02-b.md", ident="beta"):
        self.write(todo_file([(1, "B", 0, "none", "--")], ident=ident), name=name)

    def test_a_missing_file_is_listed_with_its_section_and_an_existing_or_other_path_is_not(self):
        self.authored()
        self.authoring({1: ["- [ ] Author `todo/04-platform/TODO-01-build.md`: the build.",
                            "- [ ] Author `todo/00-workspace/TODO-02-b.md`: already written.",
                            "- [ ] Author `docs/specs/notes.md`: not a TODO file.",
                            "- [ ] Author `todo/README.md`: not a TODO file either."],
                        2: ["- [ ] Author `todo/05-engine/TODO-03-text.md`: the text engine."]})
        self.assertEqual(tg.to_author(self.root), [
            {"path": "todo/04-platform/TODO-01-build.md", "ref": "D00 T01 §1", "done": False},
            {"path": "todo/05-engine/TODO-03-text.md", "ref": "D00 T01 §2", "done": False}])

    def test_the_list_follows_plan_order(self):
        table = "| 1 | §2 | S2 | -- | [ ] |\n| 2 | §1 | S1 | -- | [ ] |"
        text = todo_file([(1, "S1", 0, "none", "--"), (2, "S2", 0, "none", "--")], table_override=table)
        # Section 1 is written first in the file, section 2 second; the table runs §2 first.
        for path in ("todo/04-platform/TODO-01-a.md", "todo/04-platform/TODO-02-b.md"):
            text = text.replace("- [ ] Work.\n", f"- [ ] Author `{path}`: it.\n", 1)
        self.write(text)
        self.assertEqual([item["ref"] for item in tg.to_author(self.root)], ["D00 T01 §2", "D00 T01 §1"])

    def test_one_path_named_by_two_sections_refuses_naming_both(self):
        self.authoring({1: ["- [ ] Author `todo/04-platform/TODO-01-build.md`: the build."],
                        2: ["- [ ] Author `todo/04-platform/TODO-01-build.md`: the build again."]})
        self.refuses("TODO file named by two Author items (D00 T01 §1 and D00 T01 §2): "
                     "todo/04-platform/TODO-01-build.md")

    def test_a_ticked_author_item_without_its_file_refuses_and_with_it_validates(self):
        self.authoring({1: ["- [x] Author `todo/00-workspace/TODO-02-b.md`: written."]})
        self.refuses("ticked Author item without its file (D00 T01 §1): todo/00-workspace/TODO-02-b.md")
        self.authored()
        tg.graph(self.root)
        self.assertEqual(tg.to_author(self.root), [])

    def block(self, plan):
        return plan.split(tg.NOT_IN_PLAN + "\n", 1)[1].split("\nProgress:", 1)[0]

    def section_rows(self, plan):
        """[status, reference, deliverable, count] of each row of the block's table."""
        return [[c.strip() for c in line.split("|")[1:5]] for line in self.block(plan).splitlines()
                if line.startswith("| [")]

    def test_the_plan_shows_the_authoring_sections_and_never_a_file(self):
        # D00 T03 §58 (owner, 2026-11-12): the plan lists sections, never TODO files.
        self.authoring({1: ["- [ ] Author `todo/04-platform/TODO-01-build.md`: the build.",
                            "- [ ] Author `todo/05-engine/TODO-03-text.md`: the text engine."],
                        2: ["- [ ] Author `todo/06-write/TODO-01-core.md`: Write."]})
        plan = tg.projection(self.root)
        self.assertEqual(self.section_rows(plan), [["[ ]", "D00 T01 §1", "S1", "2"], ["[ ]", "D00 T01 §2", "S2", "1"]])
        self.assertNotIn("todo/", self.block(plan))
        self.assertNotIn("| `todo/", plan)
        self.assertNotIn("Still to author", plan)
        self.assertIn("The sections of 3 TODO files are not written yet", self.block(plan))
        self.assertIn("| Status | Reference  | Deliverable | Files to write |", self.block(plan))
        # The block sits after the last phase table and before the progress line.
        self.assertLess(plan.index("### Phase 0"), plan.index(tg.NOT_IN_PLAN))
        self.assertIn("ready to run now, 3 TODO files still to author (not counted here).", plan)
        self.assertEqual(sum(int(row[3]) for row in self.section_rows(plan)), len(tg.to_author(self.root)))

    def test_the_rows_follow_plan_order(self):
        table = "| 1 | §2 | S2 | -- | [ ] |\n| 2 | §1 | S1 | -- | [ ] |"
        text = todo_file([(1, "S1", 0, "none", "--"), (2, "S2", 0, "none", "--")], table_override=table)
        for path in ("todo/04-platform/TODO-01-a.md", "todo/04-platform/TODO-02-b.md"):
            text = text.replace("- [ ] Work.\n", f"- [ ] Author `{path}`: it.\n", 1)
        self.write(text)
        self.assertEqual([row[1] for row in self.section_rows(tg.projection(self.root))], ["D00 T01 §2", "D00 T01 §1"])

    def test_a_count_drops_as_a_file_appears_and_a_finished_section_leaves_the_table(self):
        self.authoring({1: ["- [ ] Author `todo/00-workspace/TODO-02-b.md`: one.",
                            "- [ ] Author `todo/00-workspace/TODO-03-c.md`: two."],
                        2: ["- [ ] Author `todo/00-workspace/TODO-04-d.md`: three."]})
        self.assertEqual([row[1:] for row in self.section_rows(tg.projection(self.root))],
                         [["D00 T01 §1", "S1", "2"], ["D00 T01 §2", "S2", "1"]])
        self.authored()  # TODO-02-b.md now exists
        self.assertEqual([row[1:] for row in self.section_rows(tg.projection(self.root))],
                         [["D00 T01 §1", "S1", "1"], ["D00 T01 §2", "S2", "1"]])
        self.authored(name="TODO-03-c.md", ident="gamma")
        self.assertEqual([row[1:] for row in self.section_rows(tg.projection(self.root))], [["D00 T01 §2", "S2", "1"]])
    def test_one_file_reads_in_the_singular(self):
        self.authoring({1: ["- [ ] Author `todo/04-platform/TODO-01-build.md`: the build."]})
        self.assertIn("ready to run now, 1 TODO file still to author (not counted here).", tg.projection(self.root))

    def test_no_block_and_no_count_when_nothing_is_missing(self):
        self.authored()
        self.authoring({1: ["- [ ] Author `todo/00-workspace/TODO-02-b.md`: written."]})
        plan = tg.projection(self.root)
        self.assertNotIn("Still to author", plan)
        self.assertNotIn("Not in the plan yet", plan)
        self.assertNotIn("Files to write", plan)
        self.assertNotIn("still to author", plan)
        self.assertIn("ready to run now.", plan)

    def test_a_long_file_name_no_longer_refuses(self):
        path = "todo/04-platform/TODO-01-" + "x" * 80 + ".md"
        self.authoring({1: [f"- [ ] Author `{path}`: a long name."]})
        tg.graph(self.root)
        plan = tg.projections(self.root, sync=True)
        self.assertNotIn(path, (self.root / tg.PLAN).read_text(encoding="utf-8"))
        del plan

    def test_the_refusal_names_the_section_with_the_longest_title_not_the_first(self):
        # Round 1: rows are padded alike, so the first section was blamed for a later one's long title.
        def tree(length):
            for path in (self.root / "todo").rglob("TODO-*.md"):
                path.unlink()
            text = todo_file([(1, "Short", 0, "none", "--"), (2, "T" * length, 0, "none", "--")])
            for name in ("a", "b"):
                text = text.replace("- [ ] Work.\n", f"- [ ] Author `todo/04-platform/TODO-01-{name}.md`: it.\n", 1)
            self.write(text)
        for length in range(60, 120):
            tree(length)
            try:
                tg.graph(self.root)
            except tg.Refused as error:
                self.assertIn("sections still to be written wraps raw md", str(error))
                self.assertIn("shorten the title of D00 T01 §2", str(error))
                return
        self.fail("no title was refused")

    def test_a_title_that_fits_its_phase_row_but_not_this_table_refuses_naming_the_section(self):
        # A phase row and this table's row differ in their other columns, so each has its own longest title. The
        # longest one a phase row still takes is found, then shown to be refused here by validate and by the plan.
        def tree(length):
            for path in (self.root / "todo").rglob("*.md"):
                path.unlink()
            text = todo_file([(1, "T" * length, 0, "none", "--")])
            self.write(text.replace("- [ ] Work.\n", "- [ ] Author `todo/04-platform/TODO-01-a.md`: it.\n", 1))

        def refusal():
            try:
                tg.graph(self.root)
                tg.projection(self.root)
                return ""
            except tg.Refused as error:
                return str(error)
        seen = {}
        for length in range(60, 120):
            tree(length)
            seen[length] = refusal()
        ours = [n for n, text in seen.items() if "sections still to be written wraps raw md" in text]
        self.assertTrue(ours, "no title length is refused by the new table alone")
        self.assertIn("shorten the title of D00 T01 §1", seen[ours[0]])
        self.assertEqual(seen[ours[0] - 1], "")  # one character shorter is accepted by both tables
        tree(ours[0])
        with self.assertRaises(tg.Refused):
            tg.graph(self.root)  # validate refuses it
        with self.assertRaises(tg.Refused):
            tg.projection(self.root)  # and so does the plan
    def test_a_stale_block_fails_the_check(self):
        self.authoring({1: ["- [ ] Author `todo/00-workspace/TODO-02-b.md`: soon."]})
        tg.projections(self.root, sync=True)
        tg.projections(self.root)
        self.authored()
        with self.assertRaises(tg.Refused):
            tg.projections(self.root)

    def test_query_stats_counts_the_files_still_to_author(self):
        r = subprocess.run([sys.executable, str(REPO / "scripts/todo-graph.py"), "query", "stats"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        stats = json.loads(r.stdout)
        self.assertEqual(stats["to_author"], len(tg.to_author()))
        plan = (REPO / tg.PLAN).read_text(encoding="utf-8")
        self.assertEqual(plan.count("\n| `todo/"), 0)  # D00 T03 §58: never a file in the plan
        block = plan.split(tg.NOT_IN_PLAN + "\n", 1)[1].split("\nProgress:", 1)[0] if stats["to_author"] else ""
        counts = [int(line.split("|")[4]) for line in block.splitlines() if line.startswith("| [")]
        self.assertEqual(sum(counts), stats["to_author"])


class PlanWidthInValidate(Tree):
    """validate refuses what plan --sync cannot render, with the same message (D00 T03 §32)."""

    def cli(self, *args):
        """The real command, run on the fixture tree: its ROOT is the folder two above its library."""
        for name in ("todo-graph.py", "lib/todo_graph.py"):
            target = self.root / "scripts" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((REPO / "scripts" / name).read_bytes())
        r = subprocess.run([sys.executable, "-B", str(self.root / "scripts/todo-graph.py"), *args],
                           capture_output=True, text=True, encoding="utf-8", timeout=120)
        return r.returncode, r.stderr.strip()

    def test_a_legal_title_too_wide_for_its_phase_table_is_refused_by_both_commands_alike(self):
        # The longest legal title (88) is already 130 wide with Needs "none": the plan fits 78 at most.
        title = "T" * 88
        self.write(todo_file([(1, title, 0, "none", "--")]))
        message = ("plan table for phase 0 wraps raw md (130 > 120 chars); shorten the heading and Deliverable "
                   "of D00 T01 §1 (title 88 chars)")
        self.refuses(message)
        validate, sync = self.cli("validate"), self.cli("plan", "--sync")
        self.assertEqual(validate, (2, "TODO refused: " + message))
        self.assertEqual(sync, validate)
        self.assertFalse((self.root / tg.PLAN).exists())

    def test_a_title_that_fits_the_plan_validates_and_one_more_character_does_not(self):
        self.write(todo_file([(1, "T" * 78, 0, "none", "--")]))
        self.assertEqual(self.cli("validate"), (0, ""))
        self.write(todo_file([(1, "T" * 79, 0, "none", "--")]))
        self.assertEqual(self.cli("validate")[0], 2)
        self.write(todo_file([(1, "T" * 70, 0, "none", "--")]))
        self.assertEqual(self.cli("validate"), (0, ""))

    def test_a_long_author_path_passes_both_commands_and_a_wide_title_is_refused_by_both_alike(self):
        # D00 T03 §58: the plan renders no file name, so a long one is fine; the table of sections still to be
        # written has its own width, checked by validate and by the plan alike.
        path = "todo/04-platform/TODO-01-" + "x" * 80 + ".md"
        StillToAuthor.authoring(self, {1: [f"- [ ] Author `{path}`: a long name."]})
        self.assertEqual(self.cli("validate")[0], 0)
        self.assertEqual(self.cli("plan", "--sync")[0], 0)

        def tree(length):
            for old in (self.root / "todo").rglob("TODO-*.md"):
                old.unlink()
            text = todo_file([(1, "T" * length, 0, "none", "--")])
            self.write(text.replace("- [ ] Work.\n", "- [ ] Author `todo/04-platform/TODO-01-a.md`: it.\n", 1))
        for length in range(60, 120):
            tree(length)
            try:
                tg.graph(self.root)
            except tg.Refused as error:
                self.assertIn("sections still to be written wraps raw md", str(error), length)
                break
        else:
            self.fail("no title was refused")
        validate, sync = self.cli("validate"), self.cli("plan", "--sync")
        self.assertEqual(validate[0], 2)
        self.assertIn("shorten the title of D00 T01 §1", validate[1])
        self.assertEqual(sync, validate)

class JoinedItems(Tree):
    """A checklist box that does not start its own line is refused (D00 T04 §1, 2026-11-12: an edit ran two items
    together and hid a deliverable inside the item before it)."""

    def test_two_items_on_one_line_are_refused(self):
        text = todo_file([(1, "A", 0, "none", "--")]).replace("- [ ] Work.\n", "- [ ] Work one.- [ ] Work two.\n", 1)
        self.write(text)
        with self.assertRaises(tg.Refused) as caught:
            tg.graph(self.root)
        self.assertIn("does not start its own line", str(caught.exception))

    def test_a_box_after_prose_is_refused_and_a_quoted_one_is_not(self):
        joined = todo_file([(1, "A", 0, "none", "--")]).replace("- [ ] Work.\n", "- [ ] Work.\nSee also - [ ] this.\n", 1)
        self.write(joined)
        with self.assertRaises(tg.Refused):
            tg.graph(self.root)
        quoted = todo_file([(1, "A", 0, "none", "--")]).replace("- [ ] Work.\n", "- [ ] Work: write `- [ ] Commit:` last.\n", 1)
        self.write(quoted)
        tg.graph(self.root)


class PlanByDomain(Tree):
    """A phase that spans domains renders one block per domain; a single-domain phase renders as before (D00 T03
    §33)."""

    # projection() of the single-domain fixture below, captured before §33 changed the renderer.
    BEFORE = (
        "# Implementation plan\n\nGenerated by `python scripts/todo-graph.py plan --sync`; do not edit by hand. Edit "
        "the TODO sections (including their Phase and Needs fields) and regenerate. The boxes below are a projection "
        "of each file's Implementation Order table and flip in exactly one place: the stamp written by review.\n\n"
        "Format and rules: `todo/README.md`. Run sections with the `process-plan`, `process-phase` and "
        "`process-todo-section` skills; `python scripts/todo-graph.py query ready` lists what can run now. Pasting a "
        "whole row from a table below into `process todo section:` is a complete instruction.\n\n### Phase 0\n\n"
        "Sections: 2 | Checklist items: 4\n\n| Status | Reference  | Deliverable  | Needs | Items |\n"
        "| ------ | ---------- | ------------ | ----- | ----- |\n| [ ]    | D00 T01 §1 | First thing  | none  | 2     |\n"
        "| [ ]    | D00 T01 §2 | Second thing | none  | 2     |\n\nProgress: 0/2 verified sections, 1 ready to run "
        "now.\n\nChecklist: 0/4 items completed (includes Commit items).\n")

    def config(self, data):
        (self.root / tg.PLAN_CONFIG).write_text(json.dumps(data), encoding="utf-8")

    def two_domains(self, brand_title="Brand thing"):
        self.write(todo_file([(1, "First thing", 0, "none", "--"), (2, "Second thing", 0, "none", "§1")]))
        self.write(todo_file([(1, brand_title, 0, "none", "--")], ident="beta", domain="01-brand"),
                   domain="01-brand")

    def test_a_single_domain_phase_renders_byte_for_byte_as_before(self):
        self.write(todo_file([(1, "First thing", 0, "none", "--"), (2, "Second thing", 0, "none", "§1")]))
        self.assertEqual(tg.projection(self.root), self.BEFORE)

    def test_a_phase_with_two_domains_renders_a_block_per_domain(self):
        self.two_domains()
        plan = tg.projection(self.root)
        phase = plan.split("### Phase 0\n", 1)[1].split("\nProgress:", 1)[0]
        self.assertIn("Sections: 3 | Checklist items: 6\n", phase)
        workspace, brand = phase.split("#### 00-workspace\n", 1)[1].split("#### 01-brand\n", 1)
        self.assertIn("Sections: 2 | Checklist items: 4 | Verified: 0", workspace)
        self.assertIn("Sections: 1 | Checklist items: 2 | Verified: 0", brand)
        self.assertEqual([line.split("|")[2].strip() for line in workspace.splitlines() if line.startswith("| [")],
                         ["D00 T01 §1", "D00 T01 §2"])
        self.assertEqual([line.split("|")[2].strip() for line in brand.splitlines() if line.startswith("| [")],
                         ["D01 T01 §1"])
        self.assertLess(phase.index("#### 00-workspace"), phase.index("#### 01-brand"))

    def test_the_headings_take_the_names_in_plan_json(self):
        self.two_domains()
        self.config({"domains": {"00-workspace": "Workspace", "01-brand": "Brand"}})
        plan = tg.projection(self.root)
        self.assertIn("#### Workspace\n", plan)
        self.assertIn("#### Brand\n", plan)
        self.assertNotIn("#### 01-brand", plan)

    def test_a_tree_without_the_key_shows_folder_names(self):
        self.two_domains()
        self.config({"title": "T"})
        self.assertEqual(tg.plan_config(self.root)["domains"], {})
        self.assertIn("#### 01-brand\n", tg.projection(self.root))

    def test_a_key_that_is_no_domain_folder_and_an_empty_name_are_refused(self):
        self.two_domains()
        for domains, fragment in (({"06-write": "Write"}, "not a domain folder"),
                                  ({"templates": "T"}, "not a domain folder"),
                                  ({"01-brand": "  "}, "needs a name")):
            with self.subTest(domains):
                self.config({"domains": domains})
                with self.assertRaises(tg.Refused) as ctx:
                    tg.plan_config(self.root)
                self.assertIn(fragment, str(ctx.exception))

    def test_each_domain_table_is_checked_for_width_on_its_own(self):
        self.two_domains(brand_title="T" * 79)
        with self.assertRaises(tg.Refused) as ctx:
            tg.graph(self.root)
        self.assertIn("plan table for phase 0, domain 01-brand wraps raw md", str(ctx.exception))
        self.assertIn("D01 T01 §1", str(ctx.exception))

    def test_a_title_too_wide_for_one_table_does_not_widen_the_other(self):
        self.two_domains(brand_title="T" * 70)
        plan = tg.projection(self.root)
        workspace = plan.split("#### 00-workspace\n", 1)[1].split("#### 01-brand\n", 1)[0]
        widths = {len(line) for line in workspace.splitlines() if line.startswith("|")}
        self.assertEqual(len(widths), 1)
        self.assertLess(widths.pop(), 60)

    def test_every_row_once_in_its_domain_in_plan_order_with_exact_counts(self):
        # Three domains, rows given out of domain order, one verified row: graph() is replaced so the done state
        # needs no receipt, and projection() is what is under test.
        self.two_domains()
        self.write(todo_file([(1, "Arch one", 0, "none", "--"), (2, "Arch two", 0, "none", "§1")], ident="gamma",
                             domain="03-architecture"), domain="03-architecture")
        real = tg.graph(self.root)
        done = {"D00 T01 §2", "D03 T01 §1"}
        rows = {ref: dataclasses.replace(row, done=ref in done) for ref, row in reversed(list(real.items()))}
        with mock.patch.object(tg, "graph", return_value=rows):
            plan = tg.projection(self.root)
        phase = plan.split("### Phase 0\n", 1)[1].split("\nProgress:", 1)[0]
        headings = [line for line in phase.splitlines() if line.startswith("#### ")]
        self.assertEqual(headings, ["#### 00-workspace", "#### 01-brand", "#### 03-architecture"])
        blocks = dict(zip(["00", "01", "03"], phase.split("#### ")[1:]))
        refs = {key: [line.split("|")[2].strip() for line in text.splitlines() if line.startswith("| [")]
                for key, text in blocks.items()}
        self.assertEqual(refs, {"00": ["D00 T01 §1", "D00 T01 §2"], "01": ["D01 T01 §1"],
                                "03": ["D03 T01 §1", "D03 T01 §2"]})
        self.assertEqual(sum(len(r) for r in refs.values()), len(real))
        self.assertIn("Sections: 2 | Checklist items: 4 | Verified: 1", blocks["00"])
        self.assertIn("Sections: 1 | Checklist items: 2 | Verified: 0", blocks["01"])
        self.assertIn("Sections: 2 | Checklist items: 4 | Verified: 1", blocks["03"])
        self.assertIn("| [x]    | D00 T01 §2", blocks["00"])
        self.assertIn("Sections: 5 | Checklist items: 10\n", phase)

    def test_validate_and_sync_accept_domain_tables_that_fit_alone_but_not_together(self):
        # Each table fits only because its wide column is its own: a 78-wide title in one domain and a 40-wide Needs
        # cell in the other would make one shared table 120 + wide.
        self.write(todo_file([(1, "T" * 78, 0, "none", "--")]))
        self.write(todo_file([(1, "B", 0, "windows-host, display-session, office", "--")], ident="beta",
                             domain="01-brand"), domain="01-brand")
        tg.graph(self.root)
        tg.projections(self.root, sync=True)
        widths = [len(line) for line in (self.root / tg.PLAN).read_text(encoding="utf-8").splitlines()
                  if line.startswith("| ")]
        self.assertLessEqual(max(widths), tg.MAX_TABLE_ROW)
        rows = tg.ordered(tg.graph(self.root))
        whole = tg.markdown_table(["Status", "Reference", "Deliverable", "Needs", "Items"],
                                  [["[ ]", r.ref, r.title, ", ".join(r.needs), "2"] for r in rows])
        self.assertGreater(max(len(line) for line in whole), tg.MAX_TABLE_ROW)  # one shared table would wrap

    def test_an_over_wide_domain_table_is_refused_alike_by_validate_and_sync(self):
        self.two_domains(brand_title="T" * 79)
        with self.assertRaises(tg.Refused) as by_validate:
            tg.graph(self.root)
        with self.assertRaises(tg.Refused) as by_sync:
            tg.projections(self.root, sync=True)
        self.assertEqual(str(by_validate.exception), str(by_sync.exception))
        self.assertFalse((self.root / tg.PLAN).exists())

    def test_the_sections_still_to_be_written_are_one_table_with_no_domain_headings(self):
        # D00 T03 §58: the block lists sections, which are not grouped by the domains of the files they will write.
        StillToAuthor.authoring(self, {1: ["- [ ] Author `todo/06-write/TODO-01-core.md`: Write.",
                                           "- [ ] Author `todo/04-platform/TODO-01-build.md`: the build.",
                                           "- [ ] Author `todo/04-platform/TODO-02-shell.md`: the shell."]})
        block = tg.projection(self.root).split(tg.NOT_IN_PLAN + "\n", 1)[1].split("\nProgress:", 1)[0]
        self.assertNotIn("####", block)
        self.assertNotIn("todo/", block)
        self.assertEqual([[c.strip() for c in line.split("|")[1:5]] for line in block.splitlines()
                          if line.startswith("| [")], [["[ ]", "D00 T01 §1", "S1", "3"]])

class Removed(Tree):
    """A section an owner decision retired is deleted and listed in todo/removed.json (owner, 2026-11-11): the plan
    never shows a retired row, and a retired reference is never given to another section."""

    def removed(self, sections):
        (self.root / tg.REMOVED).write_text(json.dumps({"schema_version": 1, "sections": sections}), encoding="utf-8")

    def refused(self, fragment):
        with self.assertRaises(tg.Refused) as ctx:
            tg.graph(self.root)
        self.assertIn(fragment, str(ctx.exception))

    ENTRY = {"date": "2026-11-11", "by": "owner", "reason": "no consumer is left"}

    def test_a_listed_section_that_is_gone_validates(self):
        self.write(todo_file([(1, "Keep", 0, "none", "--")]))
        self.removed({"D00 T01 §2": self.ENTRY})
        self.assertEqual(list(tg.graph(self.root)), ["D00 T01 §1"])
        self.assertEqual(tg.removed_sections(self.root), {"D00 T01 §2": self.ENTRY})

    def test_a_removed_reference_is_never_reused(self):
        self.write(todo_file([(1, "Keep", 0, "none", "--"), (2, "Back again", 0, "none", "--")]))
        self.removed({"D00 T01 §2": self.ENTRY})
        self.refused("lists this section as removed")

    def test_a_malformed_list_refuses(self):
        self.write(todo_file([(1, "Keep", 0, "none", "--")]))
        for bad in ({"D00 T01 2": self.ENTRY}, {"D00 T01 §2": {"date": "2026-11-11", "by": "owner"}},
                    {"D00 T01 §2": {**self.ENTRY, "date": "11 November"}}, {"D00 T01 §2": {**self.ENTRY, "reason": " "}}):
            with self.subTest(bad=bad):
                self.removed(bad)
                self.refused(tg.REMOVED)
        (self.root / tg.REMOVED).write_text("{", encoding="utf-8")
        self.refused("is not JSON")

    def test_a_row_takes_no_third_state(self):
        text = todo_file([(1, "Keep", 0, "none", "--"), (2, "Gone", 0, "none", "--")])
        self.write(text.replace("| 2 | §2 | Gone | -- | [ ] |", "| 2 | §2 | Gone | -- | [-] |"))
        with self.assertRaises(tg.Refused):
            tg.graph(self.root)


class OwnerAction(Tree):
    """A section waiting on the owner says exactly what the owner does, for the weekly digest (D00 T03 §35)."""

    ACTION = "**Owner action:** approve the name and tell the session.\n"

    def one(self, needs, action=""):
        bare = todo_file([(1, "A", 0, needs, "--")]).replace(FIXTURE_ACTION, "")
        return bare.replace(f"**Needs:** {needs}\n", f"**Needs:** {needs}\n{action}")

    def test_a_waiting_section_needs_one(self):
        for needs in ("owner-decision", "third-party", "operator", "store-account", "windows-host, operator"):
            with self.subTest(needs=needs):
                self.write(self.one(needs))
                self.refuses("needs an Owner action line (the exact steps and where the answer is recorded): D00 T01 §1")
                self.write(self.one(needs, self.ACTION))
                tg.graph(self.root)

    def test_a_section_that_waits_on_no_one_may_not_carry_one(self):
        for needs in ("none", "windows-host, office"):
            with self.subTest(needs=needs):
                self.write(self.one(needs, self.ACTION))
                self.refuses("Owner action on a section that waits on no one: D00 T01 §1")


class Repository(unittest.TestCase):
    def test_the_authoring_template_copies_are_identical(self):
        # todo/README.md and create-todo name todo/templates/TODO-template.md and the skill copies as the same file.
        canonical = (tg.ROOT / "todo/templates/TODO-template.md").read_bytes()
        # One copy since Claude Code became the only writer (2026-10-23); the .codex and .agents copies went with them.
        for kit in (".claude",):
            self.assertEqual((tg.ROOT / kit / "skills/create-todo/todo-template.md").read_bytes(), canonical, kit)

    def test_the_repository_graph_validates_and_its_plan_is_current(self):
        r = subprocess.run([sys.executable, str(REPO / "scripts/todo-graph.py"), "plan", "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


class GitPath(unittest.TestCase):
    """git is found on the absolute PATH entries only, never in the working directory (D00 T03 §12 review round 7)."""

    def test_a_git_in_the_working_directory_is_never_chosen(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            planted = pathlib.Path(tmp) / ("git.exe" if os.name == "nt" else "git")
            planted.write_bytes(b"not git")
            planted.chmod(0o755)
            here = os.getcwd()
            os.chdir(tmp)
            try:
                found = tg.git()
            finally:
                os.chdir(here)
        self.assertTrue(pathlib.Path(found).is_absolute(), found)
        self.assertNotEqual(pathlib.Path(found).parent.resolve(), pathlib.Path(tmp).resolve())

    def test_every_git_launch_uses_the_resolved_path(self):
        source = (REPO / "scripts" / "lib" / "todo_graph.py").read_text(encoding="utf-8")
        self.assertNotIn('["git"', source)


def git_started(run):
    """The git subcommands started while `run()` runs (the word after `-C <root>`), in order, and what it returned."""
    started = []
    real = subprocess.Popen.__init__

    def counting(self, args, *rest, **kwargs):
        argv = [str(a) for a in args] if isinstance(args, (list, tuple)) else [str(args)]
        if pathlib.Path(argv[0]).stem.lower() == "git":
            started.append(argv[3] if len(argv) > 3 and argv[1] == "-C" else argv[1])
        return real(self, args, *rest, **kwargs)
    with unittest.mock.patch.object(subprocess.Popen, "__init__", counting):
        result = run()
    return started, result


class GitFactsReads(unittest.TestCase):
    """One graph read's git questions, answered by one batch process and one read of the history (D00 T03 §62)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "T")
        (self.root / "dir").mkdir()
        (self.root / "a.txt").write_bytes(b"one\ntwo\n")
        (self.root / "bare.txt").write_bytes(b"no final newline")
        (self.root / "bytes.bin").write_bytes(bytes(range(256)) * 3)
        (self.root / "dir" / "x.txt").write_bytes(b"x\n")
        self.first = self.commit("first")
        (self.root / "a.txt").write_bytes(b"one\ntwo\nthree\n")
        self.second = self.commit("second")
        self.git("checkout", "-q", "-b", "side", self.first)
        (self.root / "side.txt").write_bytes(b"side\n")
        self.side = self.commit("side")
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "merge", "side")
        self.merged = self.head()
        self.git("checkout", "-q", "-b", "apart", self.first)
        (self.root / "apart.txt").write_bytes(b"apart\n")
        self.apart = self.commit("apart")  # a commit HEAD's history does not hold
        self.git("checkout", "-q", "main")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def head(self):
        return self.git("rev-parse", "HEAD").stdout.decode().strip()

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.head()

    def direct(self, name):
        shown = tg._git_direct(self.root, "show", name)
        return shown.returncode == 0, shown.stdout

    def test_a_file_at_a_commit_is_read_as_git_show_reads_it_by_one_process(self):
        names = [f"{self.first}:a.txt", f"{self.second}:a.txt", f"{self.merged}:bare.txt", f"{self.merged}:bytes.bin",
                 f"{self.merged}:dir/x.txt", f"{self.apart}:apart.txt", f"{self.first}:a.txt"]
        expected = [self.direct(name) for name in names]

        def ask():
            with tg.GitFacts(self.root):
                return [tg._git(self.root, "show", name) for name in names]
        started, shown = git_started(ask)
        self.assertEqual([(s.returncode == 0, s.stdout) for s in shown], expected)
        self.assertTrue(all(ok for ok, _ in expected))
        self.assertEqual(started, ["cat-file"])  # seven questions, one process

    def test_what_is_not_there_is_absent_and_the_next_question_is_still_answered(self):
        absent = [f"{self.merged}:nowhere.txt", "0" * 40 + ":a.txt", "not a name at all", f"{self.first}:side.txt",
                  "x blob 12", ""]
        with tg.GitFacts(self.root):
            for name in absent:
                shown = tg._git(self.root, "show", name)
                self.assertNotEqual(shown.returncode, 0, name)
                self.assertFalse(self.direct(name)[0], name)  # git show refuses it too
                after = tg._git(self.root, "show", f"{self.second}:a.txt")
                self.assertEqual((after.returncode, after.stdout), (0, b"one\ntwo\nthree\n"), name)

    def test_what_the_batch_cannot_carry_is_asked_the_direct_way(self):
        folder, broken = f"{self.merged}:dir", f"{self.merged}:a.txt\n{self.merged}:bare.txt"
        expected = [tg._git_direct(self.root, "show", name) for name in (folder, broken)]
        self.assertEqual(expected[0].returncode, 0)  # git show lists a folder
        self.assertNotEqual(expected[1].returncode, 0)

        def ask():
            with tg.GitFacts(self.root):
                out = [tg._git(self.root, "show", name) for name in (folder, broken)]
                out.append(tg._git(self.root, "show", f"{self.merged}:bare.txt"))  # the answers are still in step
                return out
        started, shown = git_started(ask)
        self.assertEqual([(s.returncode, s.stdout) for s in shown[:2]], [(e.returncode, e.stdout) for e in expected])
        self.assertEqual((shown[2].returncode, shown[2].stdout), (0, b"no final newline"))
        self.assertEqual(started, ["cat-file", "show", "show"])  # the folder after the batch named it; the break at once

    def test_the_process_ends_with_the_read_and_a_refusal_leaves_none_behind(self):
        with tg.GitFacts(self.root) as read:
            tg._git(self.root, "show", f"{self.first}:a.txt")
            process = read._process
            self.assertIsNone(process.poll())
            self.assertEqual(tg._READS, [read])
        self.assertIsNotNone(process.poll())
        self.assertEqual(tg._READS, [])
        with self.assertRaises(tg.Refused):
            with tg.GitFacts(self.root) as read:
                tg._git(self.root, "show", f"{self.first}:a.txt")
                process = read._process
                tg.require(False, "refused in the middle of a read")
        self.assertIsNotNone(process.poll())
        self.assertEqual(tg._READS, [])
        # Outside a read, and for another repository, the question is the direct call it always was.
        started, shown = git_started(lambda: tg._git(self.root, "show", f"{self.first}:a.txt"))
        self.assertEqual((started, shown.stdout), (["show"], b"one\ntwo\n"))
        with tempfile.TemporaryDirectory() as other, tg.GitFacts(other):
            started, shown = git_started(lambda: tg._git(self.root, "show", f"{self.first}:a.txt"))
        self.assertEqual((started, shown.stdout), (["show"], b"one\ntwo\n"))

    def test_a_batch_process_that_never_answers_is_stopped_at_its_limit_and_the_question_still_answered(self):
        real = subprocess.Popen
        silent = []

        def popen(args, *rest, **kwargs):
            if "cat-file" in [str(a) for a in args]:  # stands in for git: reads its input and never answers
                silent.append(real([sys.executable, "-c", "import sys; sys.stdin.buffer.read()"], *rest, **kwargs))
                return silent[-1]
            return real(args, *rest, **kwargs)
        with unittest.mock.patch.object(tg.subprocess, "Popen", popen):
            with tg.GitFacts(self.root, seconds=1.0) as read:
                start = time.monotonic()
                first = tg._git(self.root, "show", f"{self.first}:a.txt")
                waited = time.monotonic() - start
                second = tg._git(self.root, "show", f"{self.second}:a.txt")
                self.assertTrue(read._failed)
                self.assertIsNone(read._process)
        self.assertEqual((first.returncode, first.stdout), (0, b"one\ntwo\n"))
        self.assertEqual((second.returncode, second.stdout), (0, b"one\ntwo\nthree\n"))
        self.assertGreaterEqual(waited, 1.0)
        self.assertLess(waited, 15.0)  # the read's own limit, not a longer one: mutation proof, 2026-11-13
        self.assertEqual(len(silent), 1)  # once it has failed, no second batch process is started
        self.assertIsNotNone(silent[0].poll())  # and the silent one was stopped, not left running

    def test_ancestry_is_answered_from_the_one_read_of_the_history(self):
        pairs = [(self.first, self.first), (self.first, self.second), (self.second, self.first),
                 (self.side, self.second), (self.second, self.side), (self.side, self.merged),
                 (self.second, self.merged), (self.merged, self.second), (self.first, self.merged)]
        outside = [(self.first, self.apart), (self.apart, self.merged), (self.apart, self.apart)]
        expected = [tg.is_ancestor(self.root, a, b) for a, b in pairs + outside]  # outside a read: git's own answers
        self.assertEqual(expected, [True, True, False, False, False, True, True, False, True, True, False, True])

        def ask():
            with tg.GitFacts(self.root) as read:
                commits = set(read.head_commits())
                return commits, [tg.is_ancestor(self.root, a, b) for a, b in (pairs + outside) * 2]
        started, (commits, answers) = git_started(ask)
        self.assertEqual(answers, expected * 2)
        self.assertEqual(commits, {self.first, self.second, self.side, self.merged})
        # One read of the history; only a commit outside it is asked about the direct way.
        self.assertEqual(started, ["rev-list"] + ["merge-base"] * (len(outside) * 2))


class SectionExists(Tree):
    """Whether a reference points at a section, asked without receipts or git (D02 T01 §22)."""

    def test_a_section_is_its_one_todo_file_and_its_heading(self):
        self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "none", "--")]))
        self.assertTrue(tg.section_exists(self.root, "D00 T01 §1"))
        self.assertTrue(tg.section_exists(self.root, "D00 T01 §2"))
        for absent in ("D00 T01 §3", "D00 T01 §12", "D00 T02 §1", "D07 T01 §1"):
            self.assertFalse(tg.section_exists(self.root, absent), absent)
        with tempfile.TemporaryDirectory() as bare:  # a copy with no TODO tree holds no section
            self.assertFalse(tg.section_exists(bare, "D00 T01 §1"))
        with self.assertRaises(tg.Refused) as ctx:
            tg.section_exists(self.root, "T01 §1")
        self.assertIn("not a full section reference", str(ctx.exception))

    def test_a_lookup_that_failed_refuses(self):
        self.write(todo_file([(1, "A", 0, "none", "--")]))
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        (path.parent / "TODO-01-b.md").write_bytes(path.read_bytes())
        with self.assertRaises(tg.Refused) as ctx:
            tg.section_exists(self.root, "D00 T01 §1")
        self.assertIn("more than one TODO file for D00 T01 §1", str(ctx.exception))
        (path.parent / "TODO-01-b.md").unlink()
        path.write_bytes(b"\xff\xfe not utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            tg.section_exists(self.root, "D00 T01 §1")
        self.assertIn("todo/00-workspace/TODO-01-a.md cannot be read", str(ctx.exception))


class Parked(Tree):
    """A parked section is neither ready nor in progress, and returns by itself when its wait is over (D00 T03 §59)."""

    STARTED = "> **Started:** 2026-11-12T00:00:00Z\n"
    BEFORE = tg.datetime.datetime(2026, 11, 16, 5, 29, 59, tzinfo=tg.datetime.timezone.utc)
    AFTER = tg.datetime.datetime(2026, 11, 16, 5, 30, 0, tzinfo=tg.datetime.timezone.utc)

    def park(self, line, rows=((1, "A", 0, "none", "--"), (2, "B", 0, "none", "--")), started=True):
        """Section 1 of the fixture with `line` under its Started line (or with no Started line)."""
        head = (self.STARTED if started else "") + (line + "\n" if line else "")
        self.write(todo_file(list(rows)).replace("## 1. A\n\n", "## 1. A\n\n" + head + "\n", 1))

    def test_a_wait_on_a_section_is_read_back_and_holds_until_that_section_is_stamped(self):
        self.park("> **Parked:** 2026-11-12T01:00:00Z until D00 T01 §2: the owner decides which risk to keep")
        rows = tg.graph(self.root)
        row = rows["D00 T01 §1"]
        self.assertEqual(row.parked, "until D00 T01 §2: the owner decides which risk to keep")
        self.assertEqual(tg.parked_wait(row), "D00 T01 §2")
        self.assertEqual(row.public()["parked"], row.parked)
        self.assertFalse(tg.wait_met(row, rows))
        self.assertEqual(tg.disposition(row, rows), 4)
        self.assertEqual(tg.disposition(rows["D00 T01 §2"], rows), 0)
        stamped = {**rows, "D00 T01 §2": dataclasses.replace(rows["D00 T01 §2"], done=True)}
        self.assertTrue(tg.wait_met(row, stamped))
        self.assertEqual(tg.disposition(row, stamped), 0)

    def test_a_wait_on_an_instant_holds_until_it_has_passed(self):
        self.park("> **Parked:** 2026-11-12T01:00:00Z until 2026-11-16T05:30:00Z: the first scheduled digest run")
        rows = tg.graph(self.root)
        row = rows["D00 T01 §1"]
        self.assertEqual(tg.parked_wait(row), "2026-11-16T05:30:00Z")
        self.assertEqual(tg.disposition(row, rows, self.BEFORE), 4)
        self.assertEqual(tg.disposition(row, rows, self.AFTER), 0)
        self.assertEqual(tg.disposition(row, rows, self.AFTER, static=True), 4)

    def test_a_section_is_ready_without_the_line_and_again_once_it_is_removed(self):
        self.park("")
        rows = tg.graph(self.root)
        self.assertEqual((rows["D00 T01 §1"].parked, tg.disposition(rows["D00 T01 §1"], rows)), ("", 0))
        self.park("> **Parked:** 2026-11-12T01:00:00Z until 2099-01-01T00:00:00Z: a far event")
        rows = tg.graph(self.root)
        self.assertEqual(tg.disposition(rows["D00 T01 §1"], rows), 4)
        self.park("")
        rows = tg.graph(self.root)
        self.assertEqual(tg.disposition(rows["D00 T01 §1"], rows), 0)

    def test_a_met_wait_does_not_lift_the_sections_other_waits(self):
        line = "> **Parked:** 2026-11-12T01:00:00Z until 2026-11-16T05:30:00Z: an event"
        self.park(line, rows=((1, "A", 0, "none", "§2"), (2, "B", 0, "none", "--")))
        rows = tg.graph(self.root)
        self.assertEqual(tg.disposition(rows["D00 T01 §1"], rows, self.AFTER), 4)  # §2 is still open
        self.park(line, rows=((1, "A", 0, "owner-decision", "--"), (2, "B", 0, "none", "--")))
        rows = tg.graph(self.root)
        self.assertEqual(tg.disposition(rows["D00 T01 §1"], rows, self.AFTER), 4)  # the owner has not answered

    def test_malformed_lines_refuse_with_the_section_named(self):
        when = "2026-11-12T01:00:00Z"
        for line, fragment in (
                (f"> **Parked:** {when}: no wait named", "a Parked line reads"),
                ("> **Parked:** until D00 T01 §2: no instant", "a Parked line reads"),
                (f"> **Parked:** {when} until D00 T01 §2:", "a Parked line reads"),
                (f"> **Parked:** {when} until D00 T01 §2:   ", "a Parked line reads"),
                (f"> **Parked:** {when} until next Monday: not an instant", "a Parked line reads"),
                (f"> **Parked:** {when} until 2026-13-45T05:30:00Z: no such day", "a Parked line reads"),
                (f"> **Parked:** {when} until D00 T01 §9: no such section", "does not exist, or on itself (D00 T01 §9)"),
                (f"> **Parked:** {when} until D00 T01 §1: itself", "does not exist, or on itself (D00 T01 §1)"),
                (f"> **Parked:** {when} until D00 T01 §2: one\n> **Parked:** {when} until D00 T01 §2: two",
                 "more than one Parked line")):
            self.park(line)
            with self.assertRaises(tg.Refused, msg=line) as ctx:
                tg.graph(self.root)
            self.assertIn(fragment, str(ctx.exception), line)
            self.assertIn("D00 T01 §1", str(ctx.exception), line)

    def test_a_wait_on_a_section_that_depends_on_the_parked_one_refuses(self):
        line = "> **Parked:** 2026-11-12T01:00:00Z until D00 T01 §3: a decision"
        self.park(line, rows=((1, "A", 0, "none", "--"), (2, "B", 0, "none", "§1"), (3, "C", 0, "none", "§2")))
        self.refuses("a Parked line waits on a section that depends on this one (D00 T01 §3): D00 T01 §1")
        self.park(line, rows=((1, "A", 0, "none", "--"), (2, "B", 0, "none", "--"), (3, "C", 0, "none", "§2")))
        self.assertEqual(tg.parked_wait(tg.graph(self.root)["D00 T01 §1"]), "D00 T01 §3")

    def test_a_line_on_work_that_was_never_started_refuses(self):
        self.park("> **Parked:** 2026-11-12T01:00:00Z until D00 T01 §2: nothing was started", started=False)
        self.refuses("a Parked line needs a Started line (only started work is parked): D00 T01 §1")

    def test_a_stamped_section_cannot_be_parked(self):
        with self.assertRaises(tg.Refused) as ctx:
            tg._parked("> **Started:** x\n> **Parked:** 2026-11-12T01:00:00Z until D00 T01 §2: done already", True,
                       "D00 T01 §1")
        self.assertIn("a stamped section cannot be parked: D00 T01 §1", str(ctx.exception))

    def test_parking_and_resuming_leave_the_contract_digest_as_it_was(self):
        self.park("")
        plain = tg.contract_digest(tg.graph(self.root)["D00 T01 §1"])
        self.park("> **Parked:** 2026-11-12T01:00:00Z until D00 T01 §2: a decision")
        self.assertEqual(tg.contract_digest(tg.graph(self.root)["D00 T01 §1"]), plain)
        self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "none", "--")]).replace("- [ ] Work.", "- [ ] Other."))
        self.assertNotEqual(tg.contract_digest(tg.graph(self.root)["D00 T01 §1"]), plain)

    def resolve(self, rows, ref="D00 T01 §1"):
        """What `python scripts/todo-graph.py resolve <ref>` prints and returns over the given rows."""
        import contextlib
        import importlib.util
        import io
        spec = importlib.util.spec_from_file_location("todo_graph_cli", REPO / "scripts" / "todo-graph.py")
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        out = io.StringIO()
        with mock.patch.object(cli, "graph", return_value=rows), \
                mock.patch.object(sys, "argv", ["todo-graph.py", "resolve", ref]), contextlib.redirect_stdout(out):
            code = cli.main()
        return code, json.loads(out.getvalue())

    def test_resolve_prints_the_wait_and_whether_it_is_met_for_a_wait_on_a_section(self):
        self.park("> **Parked:** 2026-11-12T01:00:00Z until D00 T01 §2: the owner decides which risk to keep")
        rows = tg.graph(self.root)
        code, shown = self.resolve(rows)
        self.assertEqual((code, shown["exit"], shown["wait_met"]), (4, 4, False))
        self.assertEqual(shown["parked"], "until D00 T01 §2: the owner decides which risk to keep")
        code, shown = self.resolve({**rows, "D00 T01 §2": dataclasses.replace(rows["D00 T01 §2"], done=True)})
        self.assertEqual((code, shown["exit"], shown["wait_met"]), (0, 0, True))
        self.assertEqual(shown["parked"], "until D00 T01 §2: the owner decides which risk to keep")

    def test_resolve_prints_the_wait_and_whether_it_is_met_for_a_wait_on_an_instant(self):
        self.park("> **Parked:** 2026-11-12T01:00:00Z until 2099-01-01T00:00:00Z: the first scheduled run")
        code, shown = self.resolve(tg.graph(self.root))
        self.assertEqual((code, shown["exit"], shown["wait_met"]), (4, 4, False))
        self.assertEqual(shown["parked"], "until 2099-01-01T00:00:00Z: the first scheduled run")
        self.park("> **Parked:** 2026-11-12T01:00:00Z until 2001-01-01T00:00:00Z: the first scheduled run")
        code, shown = self.resolve(tg.graph(self.root))
        self.assertEqual((code, shown["exit"], shown["wait_met"]), (0, 0, True))
        self.assertEqual(shown["parked"], "until 2001-01-01T00:00:00Z: the first scheduled run")

    def test_resolve_says_nothing_of_a_wait_for_a_section_that_is_not_parked(self):
        self.park("")
        code, shown = self.resolve(tg.graph(self.root))
        self.assertEqual((code, shown["parked"]), (0, ""))
        self.assertNotIn("wait_met", shown)

    def progress(self):
        return next(line for line in tg.projection(self.root).splitlines() if line.startswith("Progress:"))

    def test_stats_and_the_progress_line_count_a_parked_section_and_restore_when_it_resumes(self):
        self.park("")
        before = tg.stats(tg.graph(self.root), self.root)
        self.assertEqual(before, {"total": 2, "verified": 0, "ready": 2, "blocked": 0, "parked": 0, "to_author": 0})
        line_before = self.progress()
        self.assertEqual(line_before, "Progress: 0/2 verified sections, 2 ready to run now.")
        self.park("> **Parked:** 2026-11-12T01:00:00Z until 2026-11-16T05:30:00Z: an event")
        rows = tg.graph(self.root)
        self.assertEqual(tg.stats(rows, self.root, self.BEFORE),
                         {"total": 2, "verified": 0, "ready": 1, "blocked": 1, "parked": 1, "to_author": 0})
        self.assertEqual(self.progress(), "Progress: 0/2 verified sections, 1 ready to run now, 1 parked.")
        # Once the instant has passed the section is ready again for a run, and the committed plan still says parked.
        self.assertEqual(tg.stats(rows, self.root, self.AFTER),
                         {"total": 2, "verified": 0, "ready": 2, "blocked": 0, "parked": 1, "to_author": 0})
        with mock.patch.object(tg, "wait_met", return_value=True):
            self.assertEqual(self.progress(), "Progress: 0/2 verified sections, 1 ready to run now, 1 parked.")
        self.park("")
        self.assertEqual(tg.stats(tg.graph(self.root), self.root), before)
        self.assertEqual(self.progress(), line_before)


class PerAppAuthoring(unittest.TestCase):
    """This repository's own tree: an app's sections are authored when its own inventory is done (D03 T01 §30,
    decision 44 of docs/specs/2026-10-23-campaign-scope-design.md)."""

    # Word's inventory is the ribbon (§5) and, split on 2026-11-13, Backstage (§6), Options (§31), panes (§32), the
    # status bar (§33), dialogs (§34) and context menus (§35).
    INVENTORY = {"word": (5, 6, 31, 32, 33, 34, 35), "excel": (7, 8), "powerpoint": (9, 10), "visio": (11, 12), "project": (13, 14),
                 "outlook": (15, 16)}
    AUTHORING = {19: ("word", 7), 20: ("excel", 8), 21: ("powerpoint", 9), 22: ("outlook", 12), 23: ("visio", 10),
                 24: ("project", 11)}  # authoring section: (the app it writes, its surface chapter in D02 T02)

    @classmethod
    def setUpClass(cls):
        cls.rows = tg.graph(REPO)
        cls.place = {row.ref: i for i, row in enumerate(tg.ordered(cls.rows))}

    def reach(self, ref):
        """Every prerequisite of ref, however far back."""
        seen, stack = set(), list(self.rows[ref].depends)
        while stack:
            current = stack.pop()
            if current not in seen:
                seen.add(current)
                stack.extend(self.rows[current].depends)
        return seen

    def inventory(self, *apps):
        return {f"D02 T01 §{n}" for app in apps for n in self.INVENTORY[app]}

    def test_the_platform_and_write_wait_for_no_other_apps_inventory(self):
        others = self.inventory("excel", "powerpoint", "visio", "project", "outlook")
        for ref in ("D03 T01 §17", "D03 T01 §19"):
            self.assertEqual(self.reach(ref) & others, set(), ref)

    def test_each_later_app_reaches_its_own_inventory_and_words_and_no_other(self):
        for number, (app, _) in self.AUTHORING.items():
            reached = self.reach(f"D03 T01 §{number}") & self.inventory(*self.INVENTORY)
            if app == "word":
                self.assertEqual(reached, self.inventory("word"), f"D03 T01 §{number}")
            else:  # its own app's, and the parts of Word's the shared chapters are written from: no other app's
                self.assertEqual(reached - self.inventory("word"), self.inventory(app), f"D03 T01 §{number}")
                self.assertLessEqual({"D02 T01 §5", "D02 T01 §6"}, reached, f"D03 T01 §{number}")

    def test_the_platform_keeps_what_it_is_written_from(self):
        reached = self.reach("D03 T01 §17")
        needed = {"D02 T01 §4", "D02 T01 §5", "D02 T01 §6", "D02 T01 §31", "D02 T01 §33", "D02 T02 §3", "D02 T02 §4", "D02 T02 §5", "D02 T02 §6",
                  "D03 T01 §12", "D02 T01 §29", "D02 T01 §30"}
        self.assertEqual(needed - reached, set())

    def test_each_app_keeps_its_inventory_chapter_and_decisions(self):
        for number, (app, chapter) in self.AUTHORING.items():
            ref = f"D03 T01 §{number}"
            needed = self.inventory(app) | {f"D02 T02 §{chapter}", "D03 T01 §17", "D03 T01 §18", "D03 T01 §29",
                                            "D03 T01 §12"}
            self.assertEqual(needed - self.reach(ref), set(), ref)
            self.assertIn(f"D02 T02 §{chapter}", self.rows[ref].depends, ref)

    def test_each_chapter_draws_its_mock_up_from_the_glyph_decision(self):
        for _, chapter in self.AUTHORING.values():
            self.assertIn("D02 T02 §2", self.rows[f"D02 T02 §{chapter}"].depends, f"D02 T02 §{chapter}")

    def test_no_authoring_waits_for_the_check_across_the_six_mock_ups(self):
        for number in (17, *self.AUTHORING):
            self.assertNotIn("D02 T02 §14", self.reach(f"D03 T01 §{number}"), number)

    def test_the_gate_keeps_the_guarantees_that_span_the_six_apps(self):
        reached = self.reach("D03 T01 §13")
        needed = self.inventory(*self.INVENTORY) | {f"D03 T01 §{n}" for n in self.AUTHORING} | {
            "D02 T02 §14", "D02 T01 §18", "D02 T01 §22", "D02 T01 §28", "D02 T01 §29"}
        self.assertEqual(needed - reached, set())

    def test_the_path_to_the_platform_and_write_runs_before_the_other_apps_inventories(self):
        first_other = min(self.place[ref] for ref in
                          self.inventory("excel", "powerpoint", "visio", "project", "outlook"))
        self.assertEqual(first_other, self.place["D02 T01 §7"])
        path = self.reach("D03 T01 §17") | self.reach("D03 T01 §19") | {"D03 T01 §17", "D03 T01 §19"}
        late = sorted(ref for ref in path if self.place[ref] > first_other)
        self.assertEqual(late, [])

    def test_no_open_section_on_that_path_reads_another_apps_inventory_files(self):
        """The graph cannot see a checklist item that asks for a file of an inventory captured later."""
        path = self.reach("D03 T01 §17") | self.reach("D03 T01 §19") | {"D03 T01 §17", "D03 T01 §19"}
        asked = sorted((ref, app) for ref in path if not self.rows[ref].done
                       for app in ("excel", "powerpoint", "visio", "project", "outlook")
                       if f"design/inventory/{app}/" in self.rows[ref].body)
        self.assertEqual(asked, [])


if __name__ == "__main__":
    unittest.main()

