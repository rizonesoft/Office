# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Tests for scripts/lib/todo_graph.py and scripts/todo-graph.py: the graph refuses malformed work and stamps only real evidence."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
import todo_graph as tg  # noqa: E402

ADJACENCY = ("**Adjacency:** list=not-applicable (fixture); document=not-applicable (fixture); "
             "settings=not-applicable (fixture); reporting=not-applicable (fixture); "
             "notifications=not-applicable (fixture); permissions=not-applicable (fixture); "
             "audit=not-applicable (fixture); exchange=not-applicable (fixture); "
             "reverse=not-applicable (fixture)")


def section(n, title, phase, needs, extra=""):
    return (f"## {n}. {title}\n\n**Phase:** {phase}\n**Needs:** {needs}\n**Surface:** no\n\n**Build order:**\n\n"
            f"1. Do it. Done when: it shows.\n\n- [ ] Work.\n- [ ] Commit: `x: {title.lower()}`\n\n"
            f"**Test checkpoint:** `true` exits 0.{extra}\n")


def envelope(n, reviewer="astra (`m` via `codex`)", overall="approve"):
    """One round as scripts/review-dispatch.py records it (without the optional Lines and Digest fields)."""
    return f"## Round {n}: {reviewer}\n\n- Writer: claude\n- Run: 2026-10-21T00:00:00Z\n\nReview text.\n\nOVERALL: {overall}\n\n"


COMPLETE_YES = "SECTION: D00 T01 §1\nPURPOSE: completion\n\nNo gap.\n\nCOMPLETE: yes\nHIGHEST: none\nOVERALL: approve"
GAPS = ("SECTION: D00 T01 §1\nPURPOSE: completion\n\n1. **[P2] extend: the cancel path.** Missing.\n"
        "2. **[P2] new section: the export dialog.** Missing.\n\nCOMPLETE: no\nHIGHEST: P2\nOVERALL: needs-attention")


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
        # The limit is the title's, which the table shows; the "## N. " prefix appears in no table.
        self.write(todo_file([(1, "X" * 88, 0, "none", "--")]))
        tg.graph(self.root)

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


class Stamp(Tree):
    def setUp(self):
        super().setUp()
        self.write(todo_file([(1, "A", 0, "none", "--"), (2, "B", 0, "owner-decision", "--")]))
        report_path = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("# Review findings\n\n" + envelope(1), encoding="utf-8")
        self.completion = "docs/reviews/00-workspace/D00-T01-s1-completion.md"
        self.write_completion(COMPLETE_YES)
        (self.root / ".conclave").mkdir(exist_ok=True)
        (self.root / ".conclave/reviewers.toml").write_text(
            'schema_version = 1\n\n[reviewers.astra]\ncli = "codex"\nmodel = "m"\neffort = "medium"\n\n'
            '[routes]\nclaude = ["astra"]\n', encoding="utf-8")
        for args in (["init", "-q"], ["config", "user.email", "t@example.com"],
                     ["config", "user.name", "T"], ["add", "-A"], ["commit", "-qm", "x"]):
            subprocess.run(["git", "-C", str(self.root), *args], check=True)
        self.sha = subprocess.run(["git", "-C", str(self.root), "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
        self.reviews = [{"round": 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md",
                         "verdict": "clean"}]

    def stamp(self, root, ref, *args, **kwargs):
        """tg.stamp with the section's own approving completion record unless a test names another (or None)."""
        if "completion" not in kwargs:
            path = f"docs/reviews/00-workspace/{tg.completion_name(ref)}"
            if not (self.root / path).exists():
                self.write_completion(COMPLETE_YES.replace("D00 T01 §1", ref), path=path, ref=ref)
            kwargs["completion"] = path
        return tg.stamp(root, ref, *args, **kwargs)

    def write_completion(self, *reviews, path=None, ref="D00 T01 §1", outcome="", when="2026-10-21T00:00:00Z",
                         reviewer=("astra", "m", "medium")):
        """A completion record as process-todo-section leaves it: the heading, the dispatcher's rounds, an outcome."""
        target = self.root / (path or self.completion)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# Completion review: {ref}\n", encoding="utf-8")
        dispatch = tg.review_dispatch()
        for review in reviews:
            if review is None:  # a round no reviewer returned
                result = {"writer": "claude", "reviewer": None, "model": None, "cli": None, "effort": None,
                          "failover": [{"reviewer": "astra", "reason": "exited 1"}], "review": None}
            else:
                result = {"writer": "claude", "reviewer": reviewer[0], "model": reviewer[1], "cli": "codex",
                          "effort": reviewer[2], "failover": [], "review": review}
            dispatch.record(target, result, when)
        if outcome:
            target.write_text(target.read_text(encoding="utf-8") + "\n" + outcome, encoding="utf-8")

    def refused(self, *, completion=None, contains):
        """Stamping §1 with the given completion record is refused, naming `contains`, and changes nothing."""
        before = self.snapshot()
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13",
                       completion=completion)
        self.assertIn(contains, str(ctx.exception))
        self.assertEqual(self.snapshot(), before)

    def test_a_stamp_needs_the_sections_completion_record(self):
        # D00 T03 §13: the completion review runs before the build, and stamp refuses a section without its record.
        self.tick_work()
        self.refused(completion=None, contains="--completion is required")
        self.refused(completion="docs/reviews/00-workspace/D00-T01-s2-completion.md",
                     contains="is not the completion record of D00 T01 §1")
        (self.root / self.completion).unlink()
        self.refused(completion=self.completion, contains="missing completion record")

    def test_a_completion_record_must_be_a_completion_review_of_this_section(self):
        self.tick_work()
        # A code review saved under the completion record's name: no SECTION and PURPOSE lines.
        self.write_completion("Looks fine.\n\nHIGHEST: none\nOVERALL: approve")
        self.refused(completion=self.completion, contains="is not a completion review of D00 T01 §1")
        # Another section's review copied under this name.
        self.write_completion(COMPLETE_YES.replace("D00 T01 §1", "D00 T01 §2"))
        self.refused(completion=self.completion, contains="is not a completion review of D00 T01 §1")
        # The right review in a file headed for another section.
        self.write_completion(COMPLETE_YES, ref="D00 T01 §2")
        self.refused(completion=self.completion, contains="must open with '# Completion review: D00 T01 §1'")
        # Only an outage: no reviewer returned a review.
        self.write_completion(None)
        self.refused(completion=self.completion, contains="holds no completion review returned")

    def test_a_completion_verdict_must_agree_with_its_overall_line(self):
        self.tick_work()
        self.write_completion(COMPLETE_YES.replace("OVERALL: approve", "OVERALL: needs-attention"))
        self.refused(completion=self.completion, contains="pairs COMPLETE: yes with OVERALL: needs-attention")
        self.write_completion(GAPS.replace("OVERALL: needs-attention", "OVERALL: approve"))
        self.refused(completion=self.completion, contains="pairs COMPLETE: no with OVERALL: approve")
        self.write_completion(COMPLETE_YES.replace("COMPLETE: yes", "Complete enough."))
        self.refused(completion=self.completion, contains="must say COMPLETE: yes or COMPLETE: no exactly once")

    def test_every_gap_needs_a_disposition_that_resolves(self):
        self.tick_work()
        self.write_completion(GAPS)
        self.refused(completion=self.completion, contains="has no '## Outcome (round 1)'")
        self.write_completion(GAPS, outcome="## Outcome (round 1)\n\n1. extended\n")
        self.refused(completion=self.completion, contains="gap 2 of round 1")
        self.write_completion(GAPS, outcome="## Outcome (round 1)\n\n1. extended\n2. filed -> D09 T09 §9\n")
        self.refused(completion=self.completion, contains="filed to D09 T09 §9, which is no section")
        # An outcome written for another round does not answer this one.
        self.write_completion(GAPS, outcome="## Outcome (round 2)\n\n1. extended\n2. filed -> D00 T01 §2\n")
        self.refused(completion=self.completion, contains="has no '## Outcome (round 1)'")
        self.write_completion(GAPS, outcome="## Outcome (round 1)\n\n1. filed -> D00 T01 §2\n2. filed -> D00 T01 §2\n")
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))["completion"], self.completion)
        tg.graph(self.root)  # and the receipt validates

    def test_the_completion_review_is_the_pinned_reviewers(self):
        # Review round 1 of D00 T03 §13, finding 1: another family alone could be anyone.
        self.tick_work()
        for who in (("impostor", "m", "medium"), ("astra", "other-model", "medium"), ("astra", "m", "low")):
            with self.subTest(who=who):
                self.write_completion(COMPLETE_YES, reviewer=who)
                self.refused(completion=self.completion, contains="not the reviewer the pin names")

    def test_every_numbered_gap_counts_however_it_is_written(self):
        # Review round 1 of D00 T03 §13, finding 2: an indented `2.` and a `2)` escaped the disposition check.
        self.tick_work()
        for second in ("  2. **[P2] new section: the export dialog.** Missing.",
                       "2) **[P2] new section: the export dialog.** Missing."):
            with self.subTest(second=second):
                review = GAPS.replace("2. **[P2] new section: the export dialog.** Missing.", second)
                self.write_completion(review, outcome="## Outcome (round 1)\n\n1. filed -> D00 T01 §2\n")
                self.refused(completion=self.completion, contains="gap 2 of round 1")

    def test_a_gap_number_used_twice_is_refused(self):
        # Review round 2 of D00 T03 §13, finding 1: two `1.` lines needed only one disposition.
        self.tick_work()
        for twice in (GAPS.replace("2. **[P2] new section", "1. **[P2] new section"),
                      GAPS.replace("2. **[P2] new section: the export dialog.** Missing.",
                                   "2. **[P2] new section: the export dialog.** Missing.\n  1) A nested step.")):
            with self.subTest(twice=twice[-60:]):
                self.write_completion(twice, outcome="## Outcome (round 1)\n\n1. extended\n2. filed -> D00 T01 §2\n")
                self.refused(completion=self.completion, contains="each gap needs its own number")

    def test_completion_rounds_never_count_in_an_implementation_review_loop(self):
        # Review round 2 of D00 T03 §13, finding 2: unclaimed completion approvals counted toward the cap and the
        # severity cutoff of the implementation review.
        self.tick_work()
        completion_reply = envelope(1).replace("Review text.", "SECTION: D00 T01 §1\nPURPOSE: completion\n\n"
                                               "COMPLETE: yes\nHIGHEST: none")
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        report.write_text("# Review findings\n\n" + completion_reply + envelope(2), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha,
                       [{"round": 2, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "clean"}],
                       ["true -> ok"], "2026-10-13")
        self.assertIn("holds completion review round(s) [1]", str(ctx.exception))

    def test_a_completion_record_is_never_the_implementation_review(self):
        # Review round 1 of D00 T03 §13, finding 3: an approving completion record stood in for the code review.
        self.tick_work()
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha, [{"round": 1, "report": self.completion, "verdict": "clean"}],
                       ["true -> ok"], "2026-10-13")
        self.assertIn("is a completion record, not a review of the implementation", str(ctx.exception))
        # The same reply copied into an ordinary findings file is still not a review of the implementation.
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        report.write_text("# Review findings\n\n" + envelope(1).replace("Review text.", "SECTION: D00 T01 §1\n"
                          "PURPOSE: completion\n\nCOMPLETE: yes\nHIGHEST: none"), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("holds completion review round(s) [1]", str(ctx.exception))

    def test_a_stamped_completion_records_filed_sections_still_resolve(self):
        # Review round 1 of D00 T03 §13, finding 4: receipt validation skipped the filed-reference check.
        self.tick_work()
        self.write_completion(GAPS, outcome="## Outcome (round 1)\n\n1. filed -> D00 T01 §2\n2. filed -> D00 T01 §2\n")
        self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        tg.graph(self.root)
        record = self.root / self.completion
        record.write_text(record.read_text(encoding="utf-8").replace("filed -> D00 T01 §2", "filed -> D99 T99 §99"),
                          encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            tg.graph(self.root)
        self.assertIn("filed to D99 T99 §99, which is no section", str(ctx.exception))

    def test_the_last_returned_round_decides_and_earlier_rounds_are_history(self):
        self.tick_work()
        # Round 1 found gaps and predates the reply format; round 2, the re-check, approved; round 3 was an outage.
        self.write_completion("1. Something old.\n\nOVERALL: needs-attention", COMPLETE_YES, None)
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertTrue((self.root / receipt).is_file())

    def test_a_reopened_section_needs_a_completion_review_run_since(self):
        # D00 T03 §14: reopening is recorded to the second, so a review earlier the same day no longer counts.
        self.tick_work()
        self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        tg.unstamp(self.root, "D00 T01 §1", "checkpoint fails at abc1234; repair -> XREF: §2", "2026-10-22T08:00:00Z")
        self.refused(completion=self.completion, contains="not after the section was reopened at 2026-10-22T08:00:00Z")
        self.write_completion(COMPLETE_YES, when="2026-10-22T07:59:59Z")  # the same day, before the reopening
        self.refused(completion=self.completion, contains="not after the section was reopened")
        self.write_completion(COMPLETE_YES, when="2026-10-22T08:00:00Z")  # the very second of the reopening
        self.refused(completion=self.completion, contains="not after the section was reopened")
        self.write_completion(COMPLETE_YES, when="2026-10-22T08:00:01Z")
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-22")
        self.assertTrue((self.root / receipt).is_file())

    def test_the_latest_of_two_reopenings_counts(self):
        self.tick_work()
        self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        tg.unstamp(self.root, "D00 T01 §1", "first regression", "2026-10-20T08:00:00Z")
        self.write_completion(COMPLETE_YES, when="2026-10-20T09:00:00Z")
        self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-20")
        tg.unstamp(self.root, "D00 T01 §1", "second regression", "2026-10-21T08:00:00Z")
        self.refused(completion=self.completion, contains="reopened at 2026-10-21T08:00:00Z")
        self.write_completion(COMPLETE_YES, when="2026-10-21T08:30:00Z")
        self.assertTrue((self.root / self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                                                "2026-10-21")).is_file())

    def test_a_legacy_date_only_reopening_counts_as_the_end_of_its_day(self):
        self.tick_work()
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("- [ ] Commit:", "> **Unstamped:** 2026-10-22: before D00 T03 §14\n\n- [ ] Commit:",
                                     1), encoding="utf-8")
        self.write_completion(COMPLETE_YES, when="2026-10-22T23:00:00Z")
        self.refused(completion=self.completion, contains="reopened at 2026-10-22")
        self.write_completion(COMPLETE_YES, when="2026-10-23T00:00:01Z")
        self.assertTrue((self.root / self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                                                "2026-10-23")).is_file())

    def contract(self, ref="D00 T01 §1"):
        return tg.contract_digest(tg.graph(self.root)[ref])

    def reply(self, digest, verdict=COMPLETE_YES):
        return verdict.replace("PURPOSE: completion\n", f"PURPOSE: completion\nCONTRACT: {digest}\n", 1)

    def test_the_contract_digest_ignores_ticks_and_stamps_but_not_wording(self):
        before = self.contract()
        self.tick_work()
        self.assertEqual(self.contract(), before)
        self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertEqual(self.contract(), before)  # the Verified and Review lines and the ticked Commit item
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        path.write_text(path.read_text(encoding="utf-8").replace("Work.", "Different work.", 1), encoding="utf-8")
        self.assertNotEqual(tg.contract_digest(tg.graph(self.root)["D00 T01 §1"]), before)

    def test_a_round_from_the_cutoff_must_echo_the_current_contract(self):
        after = "2026-10-23T10:00:00Z"
        self.tick_work()
        self.write_completion(COMPLETE_YES, when=after)  # no CONTRACT line
        self.refused(completion=self.completion, contains="'CONTRACT: sha256:<digest>' copied from its prompt")
        self.write_completion(self.reply("sha256:" + "0" * 64), when=after)  # the section changed after dispatch
        self.refused(completion=self.completion, contains="it changed after its completion review")
        self.write_completion(self.reply(self.contract()), when=after)
        self.assertTrue((self.root / self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                                                "2026-10-23")).is_file())

    def test_a_section_extended_after_its_approving_round_needs_a_new_one(self):
        self.tick_work()
        self.write_completion(self.reply(self.contract()), when="2026-10-23T10:00:00Z")
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        path.write_text(path.read_text(encoding="utf-8").replace("- [x] Work.", "- [x] Work.\n- [x] More work.", 1),
                        encoding="utf-8")
        self.refused(completion=self.completion, contains="it changed after its completion review")
        self.write_completion(self.reply(self.contract()), when="2026-10-23T11:00:00Z")
        self.assertTrue((self.root / self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                                                "2026-10-23")).is_file())

    def test_a_digest_free_round_before_the_cutoff_still_stamps(self):
        self.tick_work()
        self.write_completion(COMPLETE_YES, when="2026-10-23T09:39:59Z")
        self.assertTrue((self.root / self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                                                "2026-10-23")).is_file())

    def test_an_extended_gap_waits_for_its_returned_re_check(self):
        self.tick_work()
        extended = "## Outcome (round 1)\n\n1. extended\n2. filed -> D00 T01 §2\n"
        # The session died after recording `extended`.
        self.write_completion(GAPS, outcome=extended)
        self.refused(completion=self.completion, contains="its re-check has not returned")
        # The re-check was an outage.
        self.write_completion(GAPS, None, outcome=extended)
        self.refused(completion=self.completion, contains="its re-check has not returned")
        # Its one retry after the outage returned and approved.
        self.write_completion(GAPS, None, COMPLETE_YES, outcome=extended)
        self.assertTrue((self.root / self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                                                "2026-10-13")).is_file())

    def test_a_re_checks_own_gaps_are_filed(self):
        self.tick_work()
        outcomes = ("## Outcome (round 1)\n\n1. extended\n2. extended\n\n"
                    "## Outcome (round 2)\n\n1. filed -> D00 T01 §2\n2. filed -> D00 T01 §2\n")
        self.write_completion(GAPS, GAPS, outcome=outcomes)
        self.assertTrue((self.root / self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                                                "2026-10-13")).is_file())

    def test_a_receipt_under_the_current_cap_must_name_its_completion_record(self):
        self.tick_work()
        receipt = self.root / self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        data = json.loads(receipt.read_text(encoding="utf-8"))
        del data["completion"]
        receipt.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            tg.graph(self.root)
        self.assertIn("must name its completion record", str(ctx.exception))
        # A receipt from the 22-round cap predates completion records and carries none.
        data["round_cap"], data["completion"] = 22, self.completion
        receipt.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            tg.graph(self.root)
        self.assertIn("predates completion records", str(ctx.exception))
        del data["completion"]
        receipt.write_text(json.dumps(data), encoding="utf-8")
        tg.graph(self.root)

    def tick_work(self):
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        path.write_text(path.read_text(encoding="utf-8").replace("- [ ] Work.", "- [x] Work.", 1),
                        encoding="utf-8")

    def test_stamp_writes_receipt_and_validates(self):
        self.tick_work()
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        rows = tg.graph(self.root)
        self.assertTrue(rows["D00 T01 §1"].done)
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))
                         ["implementation_sha"], self.sha)

    def test_receipt_records_rounds_spent_against_the_cap(self):
        self.tick_work()
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        report.write_text("# Review findings\n\n" + envelope(1, "none") + envelope(2, overall="needs-attention")
                          + envelope(3), encoding="utf-8")
        reviews = [{"round": 2, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "fixed"},
                   {"round": 3, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "clean"}]
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, reviews, ["true -> ok"], "2026-10-13")
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        self.assertEqual((data["rounds_spent"], data["round_cap"]), (3, tg.REVIEW_ROUND_CAP))
        self.assertNotIn("cap_outcome", data)
        summary = tg.review_rounds(self.root)
        self.assertEqual(summary["sections"][0]["rounds_spent"], 3)
        self.assertEqual(summary["summary"]["stopped_at_cap"], 0)

    def record_rounds(self, last, report="docs/reviews/00-workspace/D00-T01-s1.md"):
        (self.root / report).write_text("".join(envelope(n, overall="needs-attention") for n in range(1, last + 1)),
                                        encoding="utf-8")

    def test_a_stopped_review_must_say_what_was_done(self):
        self.tick_work()
        cap = tg.REVIEW_ROUND_CAP
        self.record_rounds(cap)
        stopped = [{"round": cap, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": f"stopped-at-{cap}"}]
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha, stopped, ["true -> ok"], "2026-10-13")
        self.assertIn("--cap-outcome", str(ctx.exception))
        with self.assertRaises(tg.Refused):
            self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13",
                     cap_outcome="nothing stopped")
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, stopped, ["true -> ok"], "2026-10-13",
                           cap_outcome="filed two leftovers as D00 T01 §2")
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        self.assertEqual((data["rounds_spent"], data["cap_outcome"]), (cap, "filed two leftovers as D00 T01 §2"))
        self.assertEqual(tg.review_rounds(self.root)["summary"]["stopped_at_cap"], 1)
        # A receipt that drops the outcome no longer validates.
        del data["cap_outcome"]
        (self.root / receipt).write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused):
            tg.graph(self.root)

    def test_a_receipt_without_rounds_spent_holds_only_what_the_old_process_wrote(self):
        self.tick_work()
        receipt = self.root / self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        data = json.loads(receipt.read_text(encoding="utf-8"))
        del data["rounds_spent"], data["round_cap"]
        receipt.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:  # the old shape alone does not make a receipt old
            tg.graph(self.root)
        self.assertIn(tg.LEGACY_RECEIPTS, str(ctx.exception))
        legacy = self.root / tg.LEGACY_RECEIPTS
        legacy.write_text(json.dumps({"schema_version": 1, "receipts": {"D00 T01 §1": tg.receipt_digest(data)}}),
                          encoding="utf-8")
        tg.graph(self.root)  # a frozen old receipt still validates
        data["date"] = "2026-10-22"
        receipt.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused):  # and any change to it is no longer the frozen receipt
            tg.graph(self.root)
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        for rounds in ([{"round": 9, "report": report, "verdict": "stopped-low-severity"}],
                       [{"round": 1, "report": report, "verdict": "stopped-at-22"}],
                       [{"round": 4, "report": report, "verdict": "clean"}]):
            data["reviews"] = rounds
            receipt.write_text(json.dumps(data), encoding="utf-8")
            with self.subTest(rounds=rounds), self.assertRaises(tg.Refused) as ctx:
                tg.graph(self.root)
            self.assertIn("without rounds_spent", str(ctx.exception))

    def test_a_loop_past_the_cap_refuses_even_when_it_ends_clean(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        last = tg.REVIEW_ROUND_CAP + 1
        (self.root / report).write_text("".join(envelope(n, overall="needs-attention") for n in range(1, last))
                                        + envelope(last), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha, [{"round": last, "report": report, "verdict": "clean"}],
                     ["true -> ok"], "2026-10-13")
        self.assertIn(f"over the {tg.REVIEW_ROUND_CAP}-round cap", str(ctx.exception))

    def test_a_repeated_round_number_refuses(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        (self.root / report).write_text("".join(envelope(1, overall="needs-attention") for _ in range(3))
                                        + envelope(1), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("must number its rounds 1 to 4 in order", str(ctx.exception))

    def test_a_loop_whose_last_round_returned_no_review_refuses(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        (self.root / report).write_text(envelope(1) + envelope(2, "none", overall="blocked"), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:  # round 2 ran after the approval and returned nothing
            self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("ends with round 2, which returned no review", str(ctx.exception))

    def test_rounds_spent_must_be_what_the_findings_files_record(self):
        self.tick_work()
        receipt = self.root / self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        data = json.loads(receipt.read_text(encoding="utf-8"))
        data["rounds_spent"] = 999
        receipt.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            tg.graph(self.root)
        self.assertIn("receipt rounds_spent 999 is not the 1 rounds", str(ctx.exception))

    def test_a_receipt_names_a_cap_the_process_has_used(self):
        self.tick_work()
        receipt = self.root / self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        data = json.loads(receipt.read_text(encoding="utf-8"))
        data["round_cap"] = 50
        receipt.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            tg.graph(self.root)
        self.assertIn("round_cap is invalid", str(ctx.exception))

    def test_a_review_with_carriage_returns_is_read_as_the_dispatcher_wrote_it(self):
        self.tick_work()
        dispatch = tg.review_dispatch()
        review = ["Captured progress: 10%\rCaptured progress: 100%", "Example heading:", "## Round 999: none",
                  "OVERALL: approve"]
        text = ("## Round 1: astra (`m` via `codex`)\n\n- Writer: claude\n- Run: 2026-10-21T00:00:00Z\n"
                f"- Lines: 4\n- Digest: {dispatch.digest(review)}\n\n" + "\n".join(review) + "\n")
        (self.root / "docs/reviews/00-workspace/D00-T01-s1.md").write_bytes(text.encode("utf-8"))
        self.assertIsNotNone(dispatch.read_rounds(text))
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))["rounds_spent"], 1)
        tg.graph(self.root)

    def test_a_round_verdict_must_match_its_review(self):
        self.tick_work()
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        before = self.snapshot()
        report.write_text(envelope(1, overall="needs-attention"), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:  # a rejecting review claimed as clean
            self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("verdict matching clean", str(ctx.exception))
        fixed_only = [{"round": 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "fixed"}]
        with self.assertRaises(tg.Refused) as ctx:  # fixed, but no later round saw the fixes
            self.stamp(self.root, "D00 T01 §1", self.sha, fixed_only, ["true -> ok"], "2026-10-13")
        self.assertIn("must end at its last reviewed round", str(ctx.exception))
        report.write_text(envelope(1), encoding="utf-8")
        with self.assertRaises(tg.Refused):  # an approving review claimed as fixed
            self.stamp(self.root, "D00 T01 §1", self.sha,
                     fixed_only + [{"round": 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "clean"}],
                     ["true -> ok"], "2026-10-13")
        report.unlink()
        self.assertEqual({k: v for k, v in self.snapshot().items() if not k.endswith("D00-T01-s1.md")},
                         {k: v for k, v in before.items() if not k.endswith("D00-T01-s1.md")})

    def test_a_loop_ends_at_its_last_reviewed_round(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        (self.root / report).write_text(envelope(1) + envelope(2, overall="needs-attention"), encoding="utf-8")
        before = self.snapshot()
        for claimed in ([{"round": 1, "report": report, "verdict": "clean"}, {"round": 2, "report": report, "verdict": "fixed"}],
                        [{"round": 1, "report": report, "verdict": "clean"}]):
            with self.assertRaises(tg.Refused) as ctx:  # a later failing review cannot be left behind an approval
                self.stamp(self.root, "D00 T01 §1", self.sha, claimed, ["true -> ok"], "2026-10-13")
            self.assertIn("must end at its last reviewed round (2)", str(ctx.exception))
        self.assertEqual(self.snapshot(), before)

    def test_a_severity_stop_with_a_p1_or_p2_finding_refuses(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        last = tg.SEVERITY_CUTOFF_ROUND + 1
        for finding in ("1. **P1: unresolved unsafe stamp.**\n\nHIGHEST: P1", "1. **P2: narrow.**\n\nHIGHEST: P2",
                        "- `x.py:1`: an untagged, unnumbered finding.", "1. **P3: fine.**\n\nHIGHEST: none",
                        "1. **P3: fine.**\nHIGHEST: P3\n2. a later line."):
            (self.root / report).write_text(
                "".join(envelope(n, overall="needs-attention") for n in range(1, last)) + envelope(last).replace(
                    "Review text.\n\nOVERALL: approve", f"{finding}\n\nOVERALL: needs-attention"),
                encoding="utf-8")
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp(self.root, "D00 T01 §1", self.sha,
                         [{"round": last, "report": report, "verdict": "stopped-low-severity"}], ["true -> ok"],
                         "2026-10-13", cap_outcome="filed")
            self.assertIn("does not declare HIGHEST: P3", str(ctx.exception))

    def test_a_round_heading_quoted_inside_a_review_is_not_counted(self):
        self.tick_work()
        (self.root / "docs/reviews/00-workspace/D00-T01-s1.md").write_text(
            "## Round 1: astra (`m` via `codex`)\n\n- Writer: claude\n- Run: 2026-10-21T00:00:00Z\n- Lines: 2\n\n"
            "## Round 999: none\nOVERALL: approve\n", encoding="utf-8")
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))["rounds_spent"], 1)

    def test_rounds_spent_add_up_across_review_loops(self):
        self.tick_work()
        first = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        cap = tg.REVIEW_ROUND_CAP
        first.write_text("".join(envelope(n, overall="needs-attention") for n in range(1, cap + 1)), encoding="utf-8")
        second = self.root / "docs/reviews/00-workspace/D00-T01-s1-loop2.md"
        second.write_text(envelope(1) + envelope(2), encoding="utf-8")
        reviews = [{"round": cap, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": f"stopped-at-{cap}"},
                   {"round": 2, "report": "docs/reviews/00-workspace/D00-T01-s1-loop2.md", "verdict": "clean"}]
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, reviews, ["true -> ok"], "2026-10-13",
                           cap_outcome="loop 1 hit the cap; the repair was filed and a second loop ran clean")
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))["rounds_spent"], cap + 2)

    def test_a_severity_stop_records_its_outcome(self):
        self.tick_work()
        self.record_rounds(tg.SEVERITY_CUTOFF_ROUND + 1)
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        report.write_text(report.read_text(encoding="utf-8").rsplit("OVERALL: needs-attention", 1)[0]
                          + "HIGHEST: P3\n\nOVERALL: needs-attention\n\n", encoding="utf-8")
        low =[{"round": tg.SEVERITY_CUTOFF_ROUND + 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md",
                "verdict": "stopped-low-severity"}]
        with self.assertRaises(tg.Refused):
            self.stamp(self.root, "D00 T01 §1", self.sha, low, ["true -> ok"], "2026-10-13")
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, low, ["true -> ok"], "2026-10-13",
                           cap_outcome="round 9 had two P3 findings, filed as D00 T01 §2")
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        self.assertEqual(data["cap_outcome"], "round 9 had two P3 findings, filed as D00 T01 §2")
        summary = tg.review_rounds(self.root)["summary"]
        self.assertEqual((summary["stopped_low_severity"], summary["stopped_at_cap"]), (1, 0))

    def test_a_cap_stop_must_be_the_current_cap_reached(self):
        self.tick_work()
        self.record_rounds(tg.REVIEW_ROUND_CAP)
        before = self.snapshot()
        for n, verdict in ((1, f"stopped-at-{tg.REVIEW_ROUND_CAP}"), (3, "stopped-at-3"), (13, "stopped-at-13")):
            early = [{"round": n, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": verdict}]
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp(self.root, "D00 T01 §1", self.sha, early, ["true -> ok"], "2026-10-13", cap_outcome="filed")
            self.assertRegex(str(ctx.exception), f"must be stopped-at-{tg.REVIEW_ROUND_CAP}|"
                                                 f"a cap stop is the round that returns review {tg.REVIEW_ROUND_CAP}")
        self.assertEqual(self.snapshot(), before)

    def test_a_severity_stop_with_only_p3_findings_stamps(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        last = tg.SEVERITY_CUTOFF_ROUND + 1
        (self.root / report).write_text(
            "".join(envelope(n, overall="needs-attention") for n in range(1, last)) + envelope(last).replace(
                "Review text.\n\nOVERALL: approve", "1. **P3: wording.**\n2. **P3: the comment describing P1 findings.**\n\nHIGHEST: P3\n\nOVERALL: needs-attention"),
            encoding="utf-8")
        self.stamp(self.root, "D00 T01 §1", self.sha, [{"round": last, "report": report, "verdict": "stopped-low-severity"}],
                 ["true -> ok"], "2026-10-13", cap_outcome="two P3 findings filed")

    def test_outage_rounds_do_not_earn_a_stop(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        last = tg.SEVERITY_CUTOFF_ROUND + 1
        (self.root / report).write_text(
            "".join(envelope(n, "none") for n in range(1, last)) + envelope(last).replace(
                "Review text.\n\nOVERALL: approve", "1. **P3: wording.**\n\nHIGHEST: P3\n\nOVERALL: needs-attention"), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha, [{"round": last, "report": report, "verdict": "stopped-low-severity"}],
                     ["true -> ok"], "2026-10-13", cap_outcome="filed")
        self.assertIn("follows only 1 returned reviews", str(ctx.exception))
        cap = tg.REVIEW_ROUND_CAP
        (self.root / report).write_text(envelope(1, "none") + "".join(
            envelope(n, overall="needs-attention") for n in range(2, cap + 1)), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha, [{"round": cap, "report": report, "verdict": f"stopped-at-{cap}"}],
                     ["true -> ok"], "2026-10-13", cap_outcome="filed")
        self.assertIn("a cap stop is the round that returns review", str(ctx.exception))
        # Blocked or empty replies are not returned reviews either.
        for filler in (envelope(1).replace("OVERALL: approve", "OVERALL: blocked"), envelope(1).replace("OVERALL: approve", ""),
                       envelope(1, "claude (`claude-opus-5` via `claude`)", overall="needs-attention")):
            (self.root / report).write_text("".join(filler.replace("## Round 1:", f"## Round {n}:") for n in range(1, last))
                                            + envelope(last).replace("Review text.\n\nOVERALL: approve",
                                                                     "1. **P3: wording.**\n\nHIGHEST: P3\n\nOVERALL: needs-attention"),
                                            encoding="utf-8")
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp(self.root, "D00 T01 §1", self.sha,
                         [{"round": last, "report": report, "verdict": "stopped-low-severity"}],
                         ["true -> ok"], "2026-10-13", cap_outcome="filed")
            self.assertIn("follows only 1 returned reviews", str(ctx.exception))
        # An outage before the cap moves the cap stop to the round that returns the cap's last review.
        (self.root / report).write_text(envelope(1, "none") + "".join(
            envelope(n, overall="needs-attention") for n in range(2, cap + 2)), encoding="utf-8")
        self.stamp(self.root, "D00 T01 §1", self.sha, [{"round": cap + 1, "report": report, "verdict": f"stopped-at-{cap}"}],
                 ["true -> ok"], "2026-10-13", cap_outcome="filed")

    def test_a_severity_stop_before_the_cutoff_refuses(self):
        self.tick_work()
        self.record_rounds(tg.SEVERITY_CUTOFF_ROUND)
        before = self.snapshot()
        for n in (1, tg.SEVERITY_CUTOFF_ROUND):
            early = [{"round": n, "report": "docs/reviews/00-workspace/D00-T01-s1.md",
                      "verdict": "stopped-low-severity"}]
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp(self.root, "D00 T01 §1", self.sha, early, ["true -> ok"], "2026-10-13", cap_outcome="filed")
            self.assertIn(f"only after round {tg.SEVERITY_CUTOFF_ROUND}", str(ctx.exception))
        self.assertEqual(self.snapshot(), before)

    def test_a_claimed_round_must_be_a_reviewed_round_in_its_report(self):
        self.tick_work()
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        before = self.snapshot()
        for text in ("# No independent review has run\n", envelope(1, "none"), envelope(2),
                     envelope(1, "claude (`claude-opus-5` via `claude`)"),
                     envelope(1).replace("- Writer: claude", "- Writer: codex"),
                     envelope(1).replace("- Writer: claude", "- Writer: someone"),
                     envelope(1).replace("OVERALL: approve", "OVERALL: blocked"),
                     envelope(1).replace("OVERALL: approve", ""),
                     "## Round 1: astra (`m` via `codex`)\n\n- Writer: claude\n- Run: 2026-10-21T00:00:00Z\n- Lines: 0\n",
                     "## Round 1: fake\n\nNo reviewer returned a review.\n",
                     "## Round 1: astra (`m` via `codex`)\n\nNo metadata block.\n"):
            report.write_text(text, encoding="utf-8")
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
            self.assertRegex(str(ctx.exception), "is not a review returned by another model family|"
                                                 "is not a findings file the dispatcher can read|holds no returned review|"
                                                 "must number its rounds")
        for bad in (0, -1, True):
            with self.assertRaises(tg.Refused):
                self.stamp(self.root, "D00 T01 §1", self.sha,
                         [{"round": bad, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "clean"}],
                         ["true -> ok"], "2026-10-13")
        report.write_text("# Review findings\n\n" + envelope(1), encoding="utf-8")
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        # A receipt edited to claim a round its report never recorded no longer validates.
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        data["reviews"][0]["round"] = 999
        data["rounds_spent"] = 999
        (self.root / receipt).write_text(json.dumps(data), encoding="utf-8")
        self.refuses("round 999 is not a review returned by another model family")

    def test_a_stamped_section_with_a_waiting_need_refuses(self):
        self.tick_work()
        self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        path.write_text(path.read_text(encoding="utf-8").replace("**Needs:** none", "**Needs:** owner-decision", 1),
                        encoding="utf-8")
        self.refuses("stamped section has a waiting Need")

    def test_stale_deferral_refuses_when_owner_stamps(self):
        self.tick_work()
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        text = path.read_text(encoding="utf-8")
        target = "## 2. B\n"
        path.write_text(text.replace(target, target + "\n> **Deferred:** wait on 1 -> XREF: §1\n"),
                        encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("stale deferral", str(ctx.exception))

    def test_unticked_items_refuse(self):
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("unticked", str(ctx.exception))

    def test_waiting_section_cannot_be_stamped(self):
        with self.assertRaises(tg.Refused):
            self.stamp(self.root, "D00 T01 §2", self.sha, self.reviews, ["true -> ok"], "2026-10-13")

    def test_unknown_commit_refuses(self):
        self.tick_work()
        with self.assertRaises(tg.Refused):
            self.stamp(self.root, "D00 T01 §1", "0" * 40, self.reviews, ["true -> ok"], "2026-10-13")

    def test_no_review_round_refuses(self):
        self.tick_work()
        with self.assertRaises(tg.Refused):
            self.stamp(self.root, "D00 T01 §1", self.sha, [], ["true -> ok"], "2026-10-13")

    def test_missing_review_report_refuses(self):
        self.tick_work()
        for bad_path in (r"\Users\outside.md", "../outside.md", "docs/reviews/../outside.md", "outside.md"):
            bad_round = [{"round": 1, "report": bad_path, "verdict": "clean"}]
            with self.assertRaises(tg.Refused) as ctx:
                self.stamp(self.root, "D00 T01 §1", self.sha, bad_round, ["true -> ok"], "2026-10-13")
            self.assertIn("invalid review report path", str(ctx.exception))
        missing = [{"round": 1, "report": "docs/reviews/00-workspace/missing.md", "verdict": "clean"}]
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T01 §1", self.sha, missing, ["true -> ok"], "2026-10-13")
        self.assertIn("missing or empty review report", str(ctx.exception))
        self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        (self.root / "docs/reviews/00-workspace/D00-T01-s1.md").unlink()
        self.refuses("missing or empty review report")

    def test_receipt_for_another_commit_refuses(self):
        self.tick_work()
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        data["implementation_sha"] = "f" * 40
        (self.root / receipt).write_text(json.dumps(data), encoding="utf-8")
        self.refuses("receipt does not match its stamp")

    def test_matching_fabricated_sha_in_stamp_and_receipt_refuses(self):
        self.tick_work()
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        fake_sha = "0" * 40
        todo_path = self.root / "todo/00-workspace/TODO-01-a.md"
        todo_path.write_text(todo_path.read_text(encoding="utf-8").replace(self.sha, fake_sha),
                             encoding="utf-8")
        receipt_path = self.root / receipt
        receipt_path.write_text(receipt_path.read_text(encoding="utf-8").replace(self.sha, fake_sha),
                                encoding="utf-8")
        self.refuses("not a commit")

    def snapshot(self):
        return {str(f.relative_to(self.root)): f.read_bytes()
                for f in self.root.rglob("*") if f.is_file() and ".git" not in f.parts}

    def test_bad_verdict_writes_nothing(self):
        self.tick_work()
        before = self.snapshot()
        bad = [{"round": 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "cleen"}]
        with self.assertRaises(tg.Refused):
            self.stamp(self.root, "D00 T01 §1", self.sha, bad, ["true -> ok"], "2026-10-13")
        self.assertEqual(self.snapshot(), before)
        tg.graph(self.root)

    def test_bad_date_writes_nothing(self):
        self.tick_work()
        before = self.snapshot()
        with self.assertRaises(tg.Refused):
            self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "13 Oct")
        self.assertEqual(self.snapshot(), before)

    def test_failed_stamp_write_rolls_back_receipt_and_allows_retry(self):
        self.tick_work()
        tg.projections(self.root, sync=True)
        before = self.snapshot()
        real_atomic = tg.atomic
        for fail_at in (2, 3):
            calls = []

            def fail_on_nth_write(path, data, target=fail_at):
                calls.append(path)
                if len(calls) == target:
                    raise OSError("simulated disk write failure")
                return real_atomic(path, data)

            tg.atomic = fail_on_nth_write
            try:
                with self.assertRaises(OSError):
                    self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                             "2026-10-13", sync_plan=True)
            finally:
                tg.atomic = real_atomic
            self.assertEqual(len(calls), 4 if fail_at == 3 else 2)
            self.assertFalse((self.root / "docs/reviews/d00-t01-s1.json").exists())
            self.assertEqual(self.snapshot(), before)
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                           "2026-10-13", sync_plan=True)
        self.assertTrue((self.root / receipt).is_file())
        tg.projections(self.root)

    def test_an_interrupted_stamp_rolls_back_and_allows_retry(self):
        self.tick_work()
        tg.projections(self.root, sync=True)
        before = self.snapshot()
        real_atomic = tg.atomic
        calls = []

        def interrupt_on_second_write(path, data):
            calls.append(path)
            if len(calls) == 2:
                raise KeyboardInterrupt
            return real_atomic(path, data)

        tg.atomic = interrupt_on_second_write
        try:
            with self.assertRaises(KeyboardInterrupt):
                self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
        finally:
            tg.atomic = real_atomic
        self.assertEqual(self.snapshot(), before)
        self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)

    def test_unstamp_reopens_a_regressed_section_and_allows_a_restamp(self):
        self.tick_work()
        tg.projections(self.root, sync=True)
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
        before = self.snapshot()
        for bad in (("D00 T01 §2", "x"), ("D00 T01 §1", ""), ("D00 T01 §1", "two\nlines")):
            with self.assertRaises(tg.Refused):
                tg.unstamp(self.root, bad[0], bad[1], "2026-10-20T12:00:00Z")
        self.assertEqual(self.snapshot(), before)
        revoked = tg.unstamp(self.root, "D00 T01 §1", "checkpoint fails at abc1234; repair -> XREF: §2",
                             "2026-10-20T12:00:00Z")
        rows = tg.graph(self.root)
        self.assertFalse(rows["D00 T01 §1"].done)
        self.assertEqual(tg.disposition(rows["D00 T01 §1"], rows), 0)
        self.assertFalse((self.root / receipt).exists())
        self.assertEqual((self.root / revoked).read_bytes(), before[str(pathlib.Path(receipt))])
        text = (self.root / "todo/00-workspace/TODO-01-a.md").read_text(encoding="utf-8")
        self.assertIn("> **Unstamped:** 2026-10-20T12:00:00Z: checkpoint fails", text)
        self.assertIn("- [ ] Commit:", text)
        tg.projections(self.root)  # the plan was synced
        self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-22", sync_plan=True)
        self.assertTrue(tg.graph(self.root)["D00 T01 §1"].done)

    def test_unstamping_a_prerequisite_leaves_its_consumers_stamped_and_suspect(self):
        path = self.root / "todo/00-workspace/TODO-02-b.md"
        path.write_text(todo_file([(1, "Base", 0, "none", "--"), (2, "Mid", 0, "none", "§1"), (3, "Top", 0, "none", "§2")],
                                  ident="bravo").replace("- [ ] Work.", "- [x] Work."), encoding="utf-8")
        self.index("TODO-02-b.md")
        for n in (1, 2, 3):
            self.stamp(self.root, f"D00 T02 §{n}", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        tg.unstamp(self.root, "D00 T02 §1", "checkpoint fails", "2026-10-21T00:00:00Z")
        rows = tg.graph(self.root)
        self.assertEqual([rows[f"D00 T02 §{n}"].done for n in (1, 2, 3)], [False, True, True])
        self.assertEqual(tg.suspects(self.root, "D00 T02 §1"), ["D00 T02 §2", "D00 T02 §3"])
        # New work on a suspect stamp waits, and cannot stamp, until the reopened ancestor re-stamps.
        extra = self.root / "todo/00-workspace/TODO-03-c.md"
        extra.write_text(todo_file([(1, "On top", 0, "none", "D00 T02 §3")], ident="charlie")
                         .replace("- [ ] Work.", "- [x] Work."), encoding="utf-8")
        self.index("TODO-03-c.md")
        rows = tg.graph(self.root)
        self.assertEqual(tg.disposition(rows["D00 T03 §1"], rows), 4)
        with self.assertRaises(tg.Refused) as ctx:
            self.stamp(self.root, "D00 T03 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-21")
        self.assertIn("resting on a reopened section", str(ctx.exception))
        extra.unlink()
        # Without the Unstamped note, a stamped consumer of an open section still refuses.
        path.write_text(path.read_text(encoding="utf-8").replace("> **Unstamped:** ", "> **Note:** "), encoding="utf-8")
        self.refuses("stamped section has open dependency")

    def test_an_interrupted_unstamp_rolls_back(self):
        self.tick_work()
        tg.projections(self.root, sync=True)
        self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
        before = self.snapshot()
        real_atomic = tg.atomic
        calls = []

        def interrupt_on_second_write(path, data):
            calls.append(path)
            if len(calls) == 2:
                raise KeyboardInterrupt
            return real_atomic(path, data)

        tg.atomic = interrupt_on_second_write
        try:
            with self.assertRaises(KeyboardInterrupt):
                tg.unstamp(self.root, "D00 T01 §1", "regressed", "2026-10-21T00:00:00Z")
        finally:
            tg.atomic = real_atomic
        self.assertEqual(self.snapshot(), before)
        tg.graph(self.root)

    def test_stamping_the_last_section_marks_the_file_done(self):
        path = self.root / "todo/00-workspace/TODO-02-b.md"
        path.write_text(todo_file([(1, "Only", 0, "none", "--")], ident="bravo")
                        .replace("- [ ] Work.", "- [x] Work."), encoding="utf-8")
        self.index("TODO-02-b.md")
        self.stamp(self.root, "D00 T02 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("status: done", path.read_text(encoding="utf-8"))
        self.assertTrue(tg.graph(self.root)["D00 T02 §1"].done)

    def test_malformed_receipt_refuses_instead_of_crashing(self):
        self.tick_work()
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        unhashable = json.dumps({"ref": "D00 T01 §1", "implementation_sha": self.sha,
                                 "reviews": [{"round": 1, "report": "r", "verdict": []}],
                                 "checks": ["x"], "date": "2026-10-13"})
        for bad in ("[]", json.dumps({"ref": "D00 T01 §1", "implementation_sha": self.sha,
                                      "reviews": [None], "checks": ["x"], "date": "2026-10-13"}),
                    "not json", unhashable):
            (self.root / receipt).write_text(bad, encoding="utf-8")
            self.refuses("receipt")

    def test_missing_receipt_refuses(self):
        self.tick_work()
        receipt = self.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        (self.root / receipt).unlink()
        self.refuses("missing receipt")


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


if __name__ == "__main__":
    unittest.main()

