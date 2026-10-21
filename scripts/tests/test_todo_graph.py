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
        for args in (["init", "-q"], ["config", "user.email", "t@example.com"],
                     ["config", "user.name", "T"], ["add", "-A"], ["commit", "-qm", "x"]):
            subprocess.run(["git", "-C", str(self.root), *args], check=True)
        self.sha = subprocess.run(["git", "-C", str(self.root), "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
        self.reviews = [{"round": 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md",
                         "verdict": "clean"}]

    def tick_work(self):
        path = self.root / "todo/00-workspace/TODO-01-a.md"
        path.write_text(path.read_text(encoding="utf-8").replace("- [ ] Work.", "- [x] Work.", 1),
                        encoding="utf-8")

    def test_stamp_writes_receipt_and_validates(self):
        self.tick_work()
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
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
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, reviews, ["true -> ok"], "2026-10-13")
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
        self.record_rounds(22)
        stopped = [{"round": 22, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "stopped-at-22"}]
        with self.assertRaises(tg.Refused) as ctx:
            tg.stamp(self.root, "D00 T01 §1", self.sha, stopped, ["true -> ok"], "2026-10-13")
        self.assertIn("--cap-outcome", str(ctx.exception))
        with self.assertRaises(tg.Refused):
            tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13",
                     cap_outcome="nothing stopped")
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, stopped, ["true -> ok"], "2026-10-13",
                           cap_outcome="filed two leftovers as D00 T01 §2")
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        self.assertEqual((data["rounds_spent"], data["cap_outcome"]), (22, "filed two leftovers as D00 T01 §2"))
        self.assertEqual(tg.review_rounds(self.root)["summary"]["stopped_at_cap"], 1)
        # A receipt that drops the outcome no longer validates.
        del data["cap_outcome"]
        (self.root / receipt).write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(tg.Refused):
            tg.graph(self.root)

    def test_a_review_with_carriage_returns_is_read_as_the_dispatcher_wrote_it(self):
        self.tick_work()
        dispatch = tg.review_dispatch()
        review = ["Captured progress: 10%\rCaptured progress: 100%", "Example heading:", "## Round 999: none",
                  "OVERALL: approve"]
        text = ("## Round 1: astra (`m` via `codex`)\n\n- Writer: claude\n- Run: 2026-10-21T00:00:00Z\n"
                f"- Lines: 4\n- Digest: {dispatch.digest(review)}\n\n" + "\n".join(review) + "\n")
        (self.root / "docs/reviews/00-workspace/D00-T01-s1.md").write_bytes(text.encode("utf-8"))
        self.assertIsNotNone(dispatch.read_rounds(text))
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))["rounds_spent"], 1)
        tg.graph(self.root)

    def test_a_round_verdict_must_match_its_review(self):
        self.tick_work()
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        before = self.snapshot()
        report.write_text(envelope(1, overall="needs-attention"), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:  # a rejecting review claimed as clean
            tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("verdict matching clean", str(ctx.exception))
        fixed_only = [{"round": 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "fixed"}]
        with self.assertRaises(tg.Refused) as ctx:  # fixed, but no later round saw the fixes
            tg.stamp(self.root, "D00 T01 §1", self.sha, fixed_only, ["true -> ok"], "2026-10-13")
        self.assertIn("must end at its last reviewed round", str(ctx.exception))
        report.write_text(envelope(1), encoding="utf-8")
        with self.assertRaises(tg.Refused):  # an approving review claimed as fixed
            tg.stamp(self.root, "D00 T01 §1", self.sha,
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
                tg.stamp(self.root, "D00 T01 §1", self.sha, claimed, ["true -> ok"], "2026-10-13")
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
                tg.stamp(self.root, "D00 T01 §1", self.sha,
                         [{"round": last, "report": report, "verdict": "stopped-low-severity"}], ["true -> ok"],
                         "2026-10-13", cap_outcome="filed")
            self.assertIn("does not declare HIGHEST: P3", str(ctx.exception))

    def test_a_round_heading_quoted_inside_a_review_is_not_counted(self):
        self.tick_work()
        (self.root / "docs/reviews/00-workspace/D00-T01-s1.md").write_text(
            "## Round 1: astra (`m` via `codex`)\n\n- Writer: claude\n- Run: 2026-10-21T00:00:00Z\n- Lines: 2\n\n"
            "## Round 999: none\nOVERALL: approve\n", encoding="utf-8")
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))["rounds_spent"], 1)

    def test_rounds_spent_add_up_across_review_loops(self):
        self.tick_work()
        first = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        first.write_text("".join(envelope(n, overall="needs-attention") for n in range(1, 23)), encoding="utf-8")
        second = self.root / "docs/reviews/00-workspace/D00-T01-s1-loop2.md"
        second.write_text(envelope(1) + envelope(2), encoding="utf-8")
        reviews = [{"round": 22, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "stopped-at-22"},
                   {"round": 2, "report": "docs/reviews/00-workspace/D00-T01-s1-loop2.md", "verdict": "clean"}]
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, reviews, ["true -> ok"], "2026-10-13",
                           cap_outcome="loop 1 hit the cap; the repair was filed and a second loop ran clean")
        self.assertEqual(json.loads((self.root / receipt).read_text(encoding="utf-8"))["rounds_spent"], 24)

    def test_a_severity_stop_records_its_outcome(self):
        self.tick_work()
        self.record_rounds(tg.SEVERITY_CUTOFF_ROUND + 1)
        report = self.root / "docs/reviews/00-workspace/D00-T01-s1.md"
        report.write_text(report.read_text(encoding="utf-8").rsplit("OVERALL: needs-attention", 1)[0]
                          + "HIGHEST: P3\n\nOVERALL: needs-attention\n\n", encoding="utf-8")
        low =[{"round": tg.SEVERITY_CUTOFF_ROUND + 1, "report": "docs/reviews/00-workspace/D00-T01-s1.md",
                "verdict": "stopped-low-severity"}]
        with self.assertRaises(tg.Refused):
            tg.stamp(self.root, "D00 T01 §1", self.sha, low, ["true -> ok"], "2026-10-13")
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, low, ["true -> ok"], "2026-10-13",
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
                tg.stamp(self.root, "D00 T01 §1", self.sha, early, ["true -> ok"], "2026-10-13", cap_outcome="filed")
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
        tg.stamp(self.root, "D00 T01 §1", self.sha, [{"round": last, "report": report, "verdict": "stopped-low-severity"}],
                 ["true -> ok"], "2026-10-13", cap_outcome="two P3 findings filed")

    def test_outage_rounds_do_not_earn_a_stop(self):
        self.tick_work()
        report = "docs/reviews/00-workspace/D00-T01-s1.md"
        last = tg.SEVERITY_CUTOFF_ROUND + 1
        (self.root / report).write_text(
            "".join(envelope(n, "none") for n in range(1, last)) + envelope(last).replace(
                "Review text.\n\nOVERALL: approve", "1. **P3: wording.**\n\nHIGHEST: P3\n\nOVERALL: needs-attention"), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            tg.stamp(self.root, "D00 T01 §1", self.sha, [{"round": last, "report": report, "verdict": "stopped-low-severity"}],
                     ["true -> ok"], "2026-10-13", cap_outcome="filed")
        self.assertIn("follows only 1 returned reviews", str(ctx.exception))
        cap = tg.REVIEW_ROUND_CAP
        (self.root / report).write_text(envelope(1, "none") + "".join(
            envelope(n, overall="needs-attention") for n in range(2, cap + 1)), encoding="utf-8")
        with self.assertRaises(tg.Refused) as ctx:
            tg.stamp(self.root, "D00 T01 §1", self.sha, [{"round": cap, "report": report, "verdict": f"stopped-at-{cap}"}],
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
                tg.stamp(self.root, "D00 T01 §1", self.sha,
                         [{"round": last, "report": report, "verdict": "stopped-low-severity"}],
                         ["true -> ok"], "2026-10-13", cap_outcome="filed")
            self.assertIn("follows only 1 returned reviews", str(ctx.exception))
        # An outage before the cap moves the cap stop to the round that returns review 22.
        (self.root / report).write_text(envelope(1, "none") + "".join(
            envelope(n, overall="needs-attention") for n in range(2, cap + 2)), encoding="utf-8")
        tg.stamp(self.root, "D00 T01 §1", self.sha, [{"round": cap + 1, "report": report, "verdict": f"stopped-at-{cap}"}],
                 ["true -> ok"], "2026-10-13", cap_outcome="filed")

    def test_a_severity_stop_before_the_cutoff_refuses(self):
        self.tick_work()
        self.record_rounds(tg.SEVERITY_CUTOFF_ROUND)
        before = self.snapshot()
        for n in (1, tg.SEVERITY_CUTOFF_ROUND):
            early = [{"round": n, "report": "docs/reviews/00-workspace/D00-T01-s1.md",
                      "verdict": "stopped-low-severity"}]
            with self.assertRaises(tg.Refused) as ctx:
                tg.stamp(self.root, "D00 T01 §1", self.sha, early, ["true -> ok"], "2026-10-13", cap_outcome="filed")
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
                tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
            self.assertRegex(str(ctx.exception), "is not a review returned by another model family|"
                                                 "is not a findings file the dispatcher can read|holds no returned review")
        for bad in (0, -1, True):
            with self.assertRaises(tg.Refused):
                tg.stamp(self.root, "D00 T01 §1", self.sha,
                         [{"round": bad, "report": "docs/reviews/00-workspace/D00-T01-s1.md", "verdict": "clean"}],
                         ["true -> ok"], "2026-10-13")
        report.write_text("# Review findings\n\n" + envelope(1), encoding="utf-8")
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        # A receipt edited to claim a round its report never recorded no longer validates.
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        data["reviews"][0]["round"] = 999
        data["rounds_spent"] = 999
        (self.root / receipt).write_text(json.dumps(data), encoding="utf-8")
        self.refuses("round 999 is not a review returned by another model family")

    def test_a_stamped_section_with_a_waiting_need_refuses(self):
        self.tick_work()
        tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
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
            tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("stale deferral", str(ctx.exception))

    def test_unticked_items_refuse(self):
        with self.assertRaises(tg.Refused) as ctx:
            tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("unticked", str(ctx.exception))

    def test_waiting_section_cannot_be_stamped(self):
        with self.assertRaises(tg.Refused):
            tg.stamp(self.root, "D00 T01 §2", self.sha, self.reviews, ["true -> ok"], "2026-10-13")

    def test_unknown_commit_refuses(self):
        self.tick_work()
        with self.assertRaises(tg.Refused):
            tg.stamp(self.root, "D00 T01 §1", "0" * 40, self.reviews, ["true -> ok"], "2026-10-13")

    def test_no_review_round_refuses(self):
        self.tick_work()
        with self.assertRaises(tg.Refused):
            tg.stamp(self.root, "D00 T01 §1", self.sha, [], ["true -> ok"], "2026-10-13")

    def test_missing_review_report_refuses(self):
        self.tick_work()
        for bad_path in (r"\Users\outside.md", "../outside.md", "docs/reviews/../outside.md", "outside.md"):
            bad_round = [{"round": 1, "report": bad_path, "verdict": "clean"}]
            with self.assertRaises(tg.Refused) as ctx:
                tg.stamp(self.root, "D00 T01 §1", self.sha, bad_round, ["true -> ok"], "2026-10-13")
            self.assertIn("invalid review report path", str(ctx.exception))
        missing = [{"round": 1, "report": "docs/reviews/00-workspace/missing.md", "verdict": "clean"}]
        with self.assertRaises(tg.Refused) as ctx:
            tg.stamp(self.root, "D00 T01 §1", self.sha, missing, ["true -> ok"], "2026-10-13")
        self.assertIn("missing or empty review report", str(ctx.exception))
        tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        (self.root / "docs/reviews/00-workspace/D00-T01-s1.md").unlink()
        self.refuses("missing or empty review report")

    def test_receipt_for_another_commit_refuses(self):
        self.tick_work()
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        data = json.loads((self.root / receipt).read_text(encoding="utf-8"))
        data["implementation_sha"] = "f" * 40
        (self.root / receipt).write_text(json.dumps(data), encoding="utf-8")
        self.refuses("receipt does not match its stamp")

    def test_matching_fabricated_sha_in_stamp_and_receipt_refuses(self):
        self.tick_work()
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
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
            tg.stamp(self.root, "D00 T01 §1", self.sha, bad, ["true -> ok"], "2026-10-13")
        self.assertEqual(self.snapshot(), before)
        tg.graph(self.root)

    def test_bad_date_writes_nothing(self):
        self.tick_work()
        before = self.snapshot()
        with self.assertRaises(tg.Refused):
            tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "13 Oct")
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
                    tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
                             "2026-10-13", sync_plan=True)
            finally:
                tg.atomic = real_atomic
            self.assertEqual(len(calls), 4 if fail_at == 3 else 2)
            self.assertFalse((self.root / "docs/reviews/d00-t01-s1.json").exists())
            self.assertEqual(self.snapshot(), before)
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"],
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
                tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
        finally:
            tg.atomic = real_atomic
        self.assertEqual(self.snapshot(), before)
        tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)

    def test_unstamp_reopens_a_regressed_section_and_allows_a_restamp(self):
        self.tick_work()
        tg.projections(self.root, sync=True)
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
        before = self.snapshot()
        for bad in (("D00 T01 §2", "x"), ("D00 T01 §1", ""), ("D00 T01 §1", "two\nlines")):
            with self.assertRaises(tg.Refused):
                tg.unstamp(self.root, bad[0], bad[1], "2026-10-21")
        self.assertEqual(self.snapshot(), before)
        revoked = tg.unstamp(self.root, "D00 T01 §1", "checkpoint fails at abc1234; repair -> XREF: §2", "2026-10-21")
        rows = tg.graph(self.root)
        self.assertFalse(rows["D00 T01 §1"].done)
        self.assertEqual(tg.disposition(rows["D00 T01 §1"], rows), 0)
        self.assertFalse((self.root / receipt).exists())
        self.assertEqual((self.root / revoked).read_bytes(), before[str(pathlib.Path(receipt))])
        text = (self.root / "todo/00-workspace/TODO-01-a.md").read_text(encoding="utf-8")
        self.assertIn("> **Unstamped:** 2026-10-21: checkpoint fails", text)
        self.assertIn("- [ ] Commit:", text)
        tg.projections(self.root)  # the plan was synced
        tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-22", sync_plan=True)
        self.assertTrue(tg.graph(self.root)["D00 T01 §1"].done)

    def test_unstamping_a_prerequisite_leaves_its_consumers_stamped_and_suspect(self):
        path = self.root / "todo/00-workspace/TODO-02-b.md"
        path.write_text(todo_file([(1, "Base", 0, "none", "--"), (2, "Mid", 0, "none", "§1"), (3, "Top", 0, "none", "§2")],
                                  ident="bravo").replace("- [ ] Work.", "- [x] Work."), encoding="utf-8")
        self.index("TODO-02-b.md")
        for n in (1, 2, 3):
            tg.stamp(self.root, f"D00 T02 §{n}", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        tg.unstamp(self.root, "D00 T02 §1", "checkpoint fails", "2026-10-21")
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
            tg.stamp(self.root, "D00 T03 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-21")
        self.assertIn("resting on a reopened section", str(ctx.exception))
        extra.unlink()
        # Without the Unstamped note, a stamped consumer of an open section still refuses.
        path.write_text(path.read_text(encoding="utf-8").replace("> **Unstamped:** ", "> **Note:** "), encoding="utf-8")
        self.refuses("stamped section has open dependency")

    def test_an_interrupted_unstamp_rolls_back(self):
        self.tick_work()
        tg.projections(self.root, sync=True)
        tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13", sync_plan=True)
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
                tg.unstamp(self.root, "D00 T01 §1", "regressed", "2026-10-21")
        finally:
            tg.atomic = real_atomic
        self.assertEqual(self.snapshot(), before)
        tg.graph(self.root)

    def test_stamping_the_last_section_marks_the_file_done(self):
        path = self.root / "todo/00-workspace/TODO-02-b.md"
        path.write_text(todo_file([(1, "Only", 0, "none", "--")], ident="bravo")
                        .replace("- [ ] Work.", "- [x] Work."), encoding="utf-8")
        self.index("TODO-02-b.md")
        tg.stamp(self.root, "D00 T02 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        self.assertIn("status: done", path.read_text(encoding="utf-8"))
        self.assertTrue(tg.graph(self.root)["D00 T02 §1"].done)

    def test_malformed_receipt_refuses_instead_of_crashing(self):
        self.tick_work()
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
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
        receipt = tg.stamp(self.root, "D00 T01 §1", self.sha, self.reviews, ["true -> ok"], "2026-10-13")
        (self.root / receipt).unlink()
        self.refuses("missing receipt")


class Repository(unittest.TestCase):
    def test_the_authoring_template_copies_are_identical(self):
        # todo/README.md and create-todo name todo/templates/TODO-template.md and the skill copies as the same file.
        canonical = (tg.ROOT / "todo/templates/TODO-template.md").read_bytes()
        for kit in (".claude", ".codex", ".agents"):
            self.assertEqual((tg.ROOT / kit / "skills/create-todo/todo-template.md").read_bytes(), canonical, kit)

    def test_the_repository_graph_validates_and_its_plan_is_current(self):
        r = subprocess.run([sys.executable, str(REPO / "scripts/todo-graph.py"), "plan", "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()

