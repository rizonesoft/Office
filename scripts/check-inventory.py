#!/usr/bin/env python3
"""Validate the Microsoft 365 parity inventory against design/inventory/schema.json and across files.

    python scripts/check-inventory.py                                   # every file under design/inventory/
    python scripts/check-inventory.py design/inventory/word             # one app
    python scripts/check-inventory.py --require-behaviour design/inventory/word/ribbon.json
    python scripts/check-inventory.py R:\\scratch\\word-home.json        # a capture outside the repository

Rules: each file is a JSON array of records valid against the schema; ids are unique across the whole inventory and the
named files; every parent names an existing record (resolved across all of design/inventory/, so one file can be
checked alone); no string anywhere in a record holds a link, since the inventory keeps facts and our own words, never
web pages. With --require-behaviour every control also needs a non-blank behaviour sentence. A file named
baseline.json is the imported control identifier baseline (scripts/import-office-ids.py) and is checked against
baseline.schema.json instead: its columns, and every cell's type (identifier, placement, policy id or null).
Exit 0 clean, 1 with one line per problem, 2 when a file cannot be read or parsed. Stdlib only.
"""
import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "design" / "inventory"
SCHEMA = INVENTORY / "schema.json"
BASELINE_SCHEMA = INVENTORY / "baseline.schema.json"
BASELINE = "baseline.json"
# Owner rule 2026-10-20: the repository holds no Microsoft text and no Microsoft links, so no record holds a link at all.
LINK = re.compile(r"https?://|www\.", re.IGNORECASE)
TARGET_KINDS = ("command", "control")


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
                   or (isinstance(value, Decimal) and value.is_finite() and value == value.to_integral_value()),
        "boolean": isinstance(value, bool),
    }[expected]


_PATTERNS = {}


def ecma(pattern):
    """Compile a JSON Schema (ECMA-262) pattern for Python: an unescaped `$` outside a class means end of input there,
    while Python's `$` also matches before a final newline, so `uia:1.2.3.4` plus a newline would pass."""
    if pattern not in _PATTERNS:
        out, i, in_class = [], 0, False
        while i < len(pattern):
            c = pattern[i]
            if c == "\\":
                out.append(pattern[i:i + 2])
                i += 2
                continue
            if in_class:
                in_class = c != "]"
            elif c == "[":
                in_class = True
            elif c == "$":
                c = "\\Z"
            out.append(c)
            i += 1
        _PATTERNS[pattern] = re.compile("".join(out))
    return _PATTERNS[pattern]


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
        if "pattern" in schema and not ecma(schema["pattern"]).search(value):
            problems.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, (int, Decimal)) and not isinstance(value, bool) and value < schema.get("minimum", value):
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
    if "not" in schema and not validate(value, schema["not"], root, path):
        problems.append(f"{path}: {schema['not'].get('description', 'refused value')}")
    for sub in schema.get("allOf", []):
        if "if" in sub:
            if not validate(value, sub["if"], root, path):
                problems += validate(value, sub.get("then", {}), root, path)
        else:
            problems += validate(value, sub, root, path)
    return problems


def links(value, path):
    """Problems for every string inside a record (nested values included) that holds a link."""
    if isinstance(value, str):
        return [f"{path}: link {LINK.search(value).group(0)!r} in a record"] if LINK.search(value) else []
    if isinstance(value, dict):
        return [p for key, item in value.items() for p in links(item, f"{path}.{key}")]
    if isinstance(value, list):
        return [p for i, item in enumerate(value) for p in links(item, f"{path}[{i}]")]
    return []


def load(path):
    try:
        # Decimal keeps JSON numbers exact: 1.0000000000000001 stays non-integral and -1e-400 stays negative.
        data = json.loads(Path(path).read_text(encoding="utf-8"), parse_float=Decimal)
    # ValueError covers malformed JSON and integers past the conversion limit; RecursionError covers deep nesting.
    except (OSError, UnicodeDecodeError, ValueError, RecursionError, InvalidOperation) as exc:
        raise Unreadable(f"{path}: cannot read ({exc})") from None
    return data


def inventory_files(paths):
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            files += sorted(f for f in p.rglob("*.json") if f.resolve() not in (SCHEMA.resolve(), BASELINE_SCHEMA.resolve()))
        else:
            files.append(p)
    return files


def check_baseline(f, data, schema):
    """Problems in one baseline file: its envelope against the baseline schema, then every row's cells."""
    problems = [f"{f}: {p}" for p in validate(data, schema, schema)]
    if problems or not isinstance(data, dict):
        return problems
    defs = schema["$defs"]
    expected = defs["outlookColumns"]["const"] if f.parent.name == "outlook" else defs["columns"]["const"]
    if data["columns"] != expected:
        return [f"{f}: columns {data['columns']} are not {expected}"]
    kinds = {"placement": defs["placement"], "policyId": defs["policyId"]}
    for i, row in enumerate(data["rows"]):
        if len(row) != len(expected):
            problems.append(f"{f}: $.rows[{i}]: {len(row)} cells, expected {len(expected)}")
            continue
        for name, cell in zip(expected, row):
            if cell is None and name not in ("controlType", "window"):
                continue
            problems += [f"{f}: {p}" for p in validate(cell, kinds.get(name, defs["identifier"]), schema,
                                                       f"$.rows[{i}].{name}")]
    return problems


def check(paths, require_behaviour=False, inventory=INVENTORY):
    """Return problems for the named files, resolving ids and parents across the whole inventory plus those files."""
    schema = load(SCHEMA)
    baseline_schema = None
    named = [Path(f) for f in inventory_files(paths)]
    universe = {f.resolve(): f for f in inventory_files([inventory])} if Path(inventory).is_dir() else {}
    universe.update({f.resolve(): f for f in named})
    records = {}
    for resolved, f in universe.items():
        data = None if f.name == BASELINE else load(f)  # a baseline holds no records
        records[resolved] = data if isinstance(data, list) else []
    problems = []
    seen, kinds = {}, {}
    for resolved, f in universe.items():
        for i, rec in enumerate(records[resolved]):
            if isinstance(rec, dict) and isinstance(rec.get("id"), str):
                seen.setdefault(rec["id"], []).append(f"{f}[{i}]")
                kinds[rec["id"]] = rec.get("kind")
    named_resolved = [f.resolve() for f in named]
    for resolved in named_resolved:
        f = universe[resolved]
        data = load(f)
        if f.name == BASELINE:
            baseline_schema = baseline_schema or load(BASELINE_SCHEMA)
            problems += check_baseline(f, data, baseline_schema)
            continue
        schema_problems = validate(data, schema, schema)
        problems += [f"{f}: {p}" for p in schema_problems]
        if not isinstance(data, list):
            continue
        for i, rec in enumerate(data):
            if not isinstance(rec, dict):
                continue
            where = f"{f}[{i}]"
            # The schema refuses links in its typed fields; links() covers every other string and reports once.
            reported = {p.split(": ", 1)[0] for p in schema_problems}
            problems += [f"{f}: {p}" for p in links(rec, f"$[{i}]") if p.split(": ", 1)[0] not in reported]
            rid = rec.get("id")
            if isinstance(rid, str):
                if len(seen.get(rid, [])) > 1:
                    problems.append(f"{where}: duplicate id {rid} (also {', '.join(x for x in seen[rid] if x != where)})")
                if isinstance(rec.get("app"), str) and rid.split(".", 1)[0] != rec["app"]:
                    problems.append(f"{where}: id {rid} does not start with its app {rec['app']}")
            parent = rec.get("parent")
            if isinstance(parent, str) and parent not in seen:
                problems.append(f"{where}: orphan, parent {parent} names no record")
            elif isinstance(parent, str) and len(seen[parent]) > 1:
                problems.append(f"{where}: parent {parent} is ambiguous, defined at {', '.join(seen[parent])}")
            target = rec.get("target")
            if isinstance(target, str):
                if target not in kinds:
                    problems.append(f"{where}: target {target} names no record")
                elif len(seen[target]) > 1:
                    problems.append(f"{where}: target {target} is ambiguous, defined at {', '.join(seen[target])}")
                elif kinds[target] not in TARGET_KINDS:
                    problems.append(f"{where}: target {target} is a {kinds[target]}, not a command or control")
            if require_behaviour and rec.get("kind") == "control":
                if not str(rec.get("behaviour", "")).strip():
                    problems.append(f"{where}: control {rid} has no behaviour")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the parity inventory.")
    parser.add_argument("paths", nargs="*", default=[str(INVENTORY)], help="files or folders (default: design/inventory)")
    parser.add_argument("--require-behaviour", action="store_true",
                        help="every control must have a non-blank behaviour sentence")
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
