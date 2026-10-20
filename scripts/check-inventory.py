#!/usr/bin/env python3
"""Validate the Microsoft 365 parity inventory against design/inventory/schema.json and across files.

    python scripts/check-inventory.py                                   # every file under design/inventory/
    python scripts/check-inventory.py design/inventory/word             # one app
    python scripts/check-inventory.py --require-behaviour design/inventory/word/ribbon.json
    python scripts/check-inventory.py R:\\scratch\\word-home.json        # a capture outside the repository

Rules: each file is a JSON array of records valid against the schema; ids are unique across the whole inventory and the
named files; every parent names an existing record (resolved across all of design/inventory/, so one file can be
checked alone). With --require-behaviour every control also needs a behaviour sentence and a web source.
Exit 0 clean, 1 with one line per problem, 2 when a file cannot be read or parsed. Stdlib only.
"""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "design" / "inventory"
SCHEMA = INVENTORY / "schema.json"


class Unreadable(Exception):
    pass


def resolve_ref(schema_root, ref):
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported $ref {ref}")
    node = schema_root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def type_ok(value, expected):
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        # JSON Schema counts any number with no fractional part as an integer (1.0 and 1e0 included).
        "integer": (isinstance(value, int) and not isinstance(value, bool))
                   or (isinstance(value, float) and value.is_integer()),
        "boolean": isinstance(value, bool),
    }[expected]


def validate(value, schema, root, path="$"):
    """The subset of JSON Schema 2020-12 that schema.json uses. Returns a list of problems."""
    if "$ref" in schema:
        return validate(value, resolve_ref(root, schema["$ref"]), root, path)
    problems = []
    if "type" in schema and not type_ok(value, schema["type"]):
        return [f"{path}: expected {schema['type']}"]
    if "const" in schema and value != schema["const"]:
        problems.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        problems.append(f"{path}: {value!r} is not one of the allowed values")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            problems.append(f"{path}: empty")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            problems.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool) and value < schema.get("minimum", value):
        problems.append(f"{path}: below {schema['minimum']}")
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            problems += validate(item, schema["items"], root, f"{path}[{i}]")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                problems.append(f"{path}: missing {key}")
        props = schema.get("properties", {})
        for key, item in value.items():
            if key in props:
                problems += validate(item, props[key], root, f"{path}.{key}")
            elif schema.get("additionalProperties", True) is False:
                problems.append(f"{path}: unknown field {key}")
        for key, needed in schema.get("dependentRequired", {}).items():
            if key in value:
                problems += [f"{path}: {key} requires {n}" for n in needed if n not in value]
    for sub in schema.get("allOf", []):
        if "if" in sub:
            if not validate(value, sub["if"], root, path):
                problems += validate(value, sub.get("then", {}), root, path)
        else:
            problems += validate(value, sub, root, path)
    return problems


def load(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    # ValueError covers malformed JSON and integers past the conversion limit; RecursionError covers deep nesting.
    except (OSError, UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise Unreadable(f"{path}: cannot read ({exc})") from None
    return data


def inventory_files(paths):
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            files += sorted(f for f in p.rglob("*.json") if f.resolve() != SCHEMA.resolve())
        else:
            files.append(p)
    return files


def check(paths, require_behaviour=False, inventory=INVENTORY):
    """Return problems for the named files, resolving ids and parents across the whole inventory plus those files."""
    schema = load(SCHEMA)
    named = [Path(f) for f in inventory_files(paths)]
    universe = {f.resolve(): f for f in inventory_files([inventory])} if Path(inventory).is_dir() else {}
    universe.update({f.resolve(): f for f in named})
    records = {}
    for resolved, f in universe.items():
        data = load(f)
        records[resolved] = data if isinstance(data, list) else []
    problems = []
    seen = {}
    for resolved, f in universe.items():
        for i, rec in enumerate(records[resolved]):
            if isinstance(rec, dict) and isinstance(rec.get("id"), str):
                seen.setdefault(rec["id"], []).append(f"{f}[{i}]")
    named_resolved = [f.resolve() for f in named]
    for resolved in named_resolved:
        f = universe[resolved]
        data = load(f)
        problems += [f"{f}: {p}" for p in validate(data, schema, schema)]
        if not isinstance(data, list):
            continue
        for i, rec in enumerate(data):
            if not isinstance(rec, dict):
                continue
            where = f"{f}[{i}]"
            rid = rec.get("id")
            if isinstance(rid, str):
                if len(seen.get(rid, [])) > 1:
                    problems.append(f"{where}: duplicate id {rid} (also {', '.join(x for x in seen[rid] if x != where)})")
                if isinstance(rec.get("app"), str) and rid.split(".", 1)[0] != rec["app"]:
                    problems.append(f"{where}: id {rid} does not start with its app {rec['app']}")
            parent = rec.get("parent")
            if isinstance(parent, str) and parent not in seen:
                problems.append(f"{where}: orphan, parent {parent} names no record")
            target = rec.get("target")
            if isinstance(target, str) and target not in seen:
                problems.append(f"{where}: target {target} names no record")
            if require_behaviour and rec.get("kind") == "control":
                if not str(rec.get("behaviour", "")).strip():
                    problems.append(f"{where}: control {rid} has no behaviour")
                if not re.match(r"^https?://[^\s/]+", str(rec.get("source", ""))):
                    problems.append(f"{where}: control {rid} has no web source for its behaviour")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the parity inventory.")
    parser.add_argument("paths", nargs="*", default=[str(INVENTORY)], help="files or folders (default: design/inventory)")
    parser.add_argument("--require-behaviour", action="store_true",
                        help="every control must have a behaviour sentence and a web source")
    args = parser.parse_args(argv)
    missing = [p for p in args.paths if not Path(p).exists()]
    if missing:
        print("\n".join(f"{p}: no such file or folder" for p in missing), file=sys.stderr)
        return 2
    try:
        problems = check(args.paths, args.require_behaviour)
    except Unreadable as exc:
        print(exc, file=sys.stderr)
        return 2
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
