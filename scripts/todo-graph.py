#!/usr/bin/env python3
"""Validate, query, resolve and stamp the canonical TODO graph, and keep todo/implementation-plan.md current.

    python scripts/todo-graph.py validate
    python scripts/todo-graph.py build                       # todo/ -> build/todo-cache.json
    python scripts/todo-graph.py render                      # mermaid dependency graph
    python scripts/todo-graph.py plan --sync | --check
    python scripts/todo-graph.py query ready | blocked | stats | deferred | adjacency | plan
    python scripts/todo-graph.py resolve 'D02 T01 §1'        # exit 0 ready, 1 no such section,
                                                             # 2 no reference in input, 3 verified,
                                                             # 4 waiting; a pasted plan row works too
    python scripts/todo-graph.py classify 'D02 T01 §1' ...   # dispositions as JSON
    python scripts/todo-graph.py stamp 'D02 T01 §1' --sha <40-char commit> \
        --review '<round>:<report path>:<clean|fixed|stopped-at-3>' --check '<command> -> <result>'

Format and rules: todo/README.md. Stdlib only.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from todo_graph import (ROOT, Refused, adjacency_report, atomic, deferrals, disposition,  # noqa: E402
                        extract_ref, graph, ordered, plan_config, projections, require, stamp)


def review_round(value):
    parts = value.split(":")
    require(len(parts) == 3 and parts[0].isdigit() and parts[1],
            f"--review takes round:report:verdict, not {value!r}")
    return {"round": int(parts[0]), "report": parts[1], "verdict": parts[2]}


def plan_status(row, rows):
    """A section's state for readers of `query plan`: verified, deferred (its file is not active), ready or blocked."""
    if row.done:
        return "verified"
    if row.status != "active":
        return "deferred"
    return "ready" if disposition(row, rows) == 0 else "blocked"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("validate", "build", "render"):
        sub.add_parser(name)
    q = sub.add_parser("query")
    q.add_argument("kind", choices=["ready", "blocked", "stats", "deferred", "adjacency", "plan"])
    r = sub.add_parser("resolve")
    r.add_argument("ref")
    c = sub.add_parser("classify")
    c.add_argument("refs", nargs="+")
    plan = sub.add_parser("plan")
    mode = plan.add_mutually_exclusive_group(required=True)
    mode.add_argument("--sync", action="store_true")
    mode.add_argument("--check", action="store_true")
    s = sub.add_parser("stamp")
    s.add_argument("ref")
    s.add_argument("--sha", required=True)
    s.add_argument("--review", action="append", default=[], type=review_round)
    s.add_argument("--check", dest="checks", action="append", default=[])
    s.add_argument("--date", default=date.today().isoformat())
    args = p.parse_args()
    if args.command == "stamp":
        receipt = stamp(ROOT, args.ref, args.sha, args.review, args.checks, args.date, sync_plan=True)
        print(f"stamped {args.ref}; receipt {receipt}; plan synchronized")
        return 0
    rows = graph()
    if args.command == "plan":
        projections(sync=args.sync)
        print("plan synchronized" if args.sync else "plan current")
    elif args.command == "resolve":
        ref, code = extract_ref(args.ref, rows)
        if code == 2:
            print("TODO refused: no section reference in input: " + args.ref, file=sys.stderr)
            return 2
        if code == 1:
            print("TODO refused: no such section: " + ref, file=sys.stderr)
            return 1
        row = rows[ref]
        unmet = [d for d in row.depends if not rows[d].done]
        print(json.dumps({**row.public(), "body": row.body, "unmet_depends": unmet,
                          "skill_arg": ref, "exit": disposition(row, rows)},
                         indent=2, ensure_ascii=False))
        return disposition(row, rows)
    elif args.command == "classify":
        out = {}
        for item in args.refs:
            ref, code = extract_ref(item, rows)
            out[item] = disposition(rows[ref], rows) if code == 0 else code
        print(json.dumps(out, ensure_ascii=False))
    elif args.command == "query":
        if args.kind == "stats":
            result = {"total": len(rows), "verified": sum(r.done for r in rows.values()),
                      "ready": sum(disposition(r, rows) == 0 for r in rows.values()),
                      "blocked": sum(disposition(r, rows) == 4 for r in rows.values())}
        elif args.kind == "deferred":
            result = deferrals()
        elif args.kind == "adjacency":
            result = adjacency_report()
        elif args.kind == "plan":
            # The plan's names come from plan_config and every section from the graph, so a reader such as the
            # editor extension never parses todo/ itself (plan R34). graph() has already loaded todo/plan.json
            # strictly, so an unreadable one refused before this point.
            config = plan_config()
            result = {"title": config["title"], "acceptance": config["acceptance"],
                      "phases": {str(n): name for n, name in sorted(config["phases"].items())},
                      "sections": [{"ref": r.ref, "path": r.path, "title": r.title, "phase": r.phase,
                                    "status": plan_status(r, rows), "depends": r.depends} for r in ordered(rows)]}
        else:
            code = 0 if args.kind == "ready" else 4
            result = [r.public() for r in ordered(rows) if disposition(r, rows) == code]
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "build":
        atomic(ROOT / "build/todo-cache.json",
               json.dumps([r.public() for r in ordered(rows)], indent=2, ensure_ascii=False) + "\n")
        print(f"built {len(rows)} sections")
    elif args.command == "render":
        node = lambda ref: re.sub(r"[^A-Za-z0-9]", "", ref)  # noqa: E731
        lines = ["```mermaid", "flowchart LR"]
        for row in ordered(rows):
            lines.append(f'    {node(row.ref)}["{row.ref}: {row.title}"]')
            for dep in row.depends:
                lines.append(f"    {node(dep)} --> {node(row.ref)}")
        lines.append("```")
        print("\n".join(lines))
    else:
        print(f"valid: {len(rows)} sections")
    return 0


if __name__ == "__main__":
    # The output is a contract other programs parse; JSON is UTF-8, whatever the console's code page.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except (Refused, OSError, ValueError) as exc:
        print("TODO refused: " + str(exc), file=sys.stderr)
        sys.exit(2)
