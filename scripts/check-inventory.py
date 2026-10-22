#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Validate the Microsoft 365 parity inventory against design/inventory/schema.json and across files.

    python scripts/check-inventory.py                                   # every file under design/inventory/
    python scripts/check-inventory.py design/inventory/word             # one app
    python scripts/check-inventory.py --require-behaviour design/inventory/word/ribbon.json
    python scripts/check-inventory.py R:\\scratch\\word-home.json        # a capture outside the repository

Rules: each file is a JSON array of records valid against the schema; ids are unique across the whole inventory and the
named files; every parent names an existing record (resolved across all of design/inventory/, so one file can be
checked alone) and no parent chain loops back; no string anywhere in a record holds a link (the schema's noLink rule),
since the inventory keeps facts and our own words, never web pages; captureProfile and capturedFrom name a profile and
a build that design/inventory/REFERENCE.md records, and a source stamped with a build matches capturedFrom. A file
that repeats a member inside one object is unreadable, since JSON would silently keep only the last value.
With --require-behaviour every control also needs a non-blank behaviour sentence. A file named
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
SOURCES = "baseline-sources.json"  # the upstream manifest the baselines were imported from
APPS = ("word", "excel", "powerpoint", "visio", "project", "outlook")
REFERENCE = "REFERENCE.md"  # the builds and capture profiles records are measured against
MAX_STRING = 1000  # the longest maxLength in schema.json (a behaviour sentence); longer strings are refused unsearched
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
# ECMA-262 whitespace and line terminators, which JSON Schema's \s and \S mean. Python's differ both ways: U+FEFF is
# whitespace to ECMA but not to Python, and U+001C to U+001F are whitespace to Python but not to ECMA.
ECMA_SPACE = ("\t\n\v\f\r \u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a"
              "\u2028\u2029\u202f\u205f\u3000\ufeff")
_SPACE_CLASS = "".join(f"\\u{ord(c):04x}" for c in ECMA_SPACE)


def ecma(pattern):
    """Compile a JSON Schema (ECMA-262) pattern for Python: an unescaped `$` outside a class means end of input there,
    while Python's `$` also matches before a final newline, so `uia:1.2.3.4` plus a newline would pass."""
    if pattern not in _PATTERNS:
        out, i, in_class = [], 0, False
        while i < len(pattern):
            c = pattern[i]
            if c == "\\":
                escape = pattern[i:i + 2]
                if escape in ("\\s", "\\S"):  # ECMA's whitespace, not Python's
                    if in_class:
                        if escape == "\\S":
                            raise ValueError(f"unsupported \\S inside a class in {pattern}")
                        out.append(_SPACE_CLASS)
                    else:
                        out.append(f"[{'^' if escape == '\\S' else ''}{_SPACE_CLASS}]")
                else:
                    out.append(escape)
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
        # re.ASCII gives \d, \w and \b their ECMA-262 meaning (ASCII only); \s and \S were made ECMA's above.
        _PATTERNS[pattern] = re.compile("".join(out), re.ASCII)
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
        if len(value) > schema.get("maxLength", len(value)):
            # Too long already; its patterns are not searched, which keeps their cost bounded by maxLength.
            return problems + [f"{path}: longer than {schema['maxLength']} characters"]
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


def links(value, path, link):
    """Problems for every string inside a record (nested values included) that holds a link. link is the schema's own
    noLink pattern (owner rule 2026-10-20: the repository holds no Microsoft text and no links), so the typed fields and
    every other string are held to one rule. Walked with an explicit stack, in document order, so no depth of nesting
    can exhaust the interpreter's recursion limit."""
    problems, stack = [], [(value, path)]
    while stack:
        item, where = stack.pop()
        if isinstance(item, str):
            if len(item) > MAX_STRING:  # longer than any field allows: refused by the schema, and not worth a search
                continue
            found = link.search(item)
            if found:
                problems.append(f"{where}: link {found.group(0)!r} in a record")
        elif isinstance(item, dict):
            stack.extend(reversed([(v, f"{where}.{k}") for k, v in item.items()]))
        elif isinstance(item, list):
            stack.extend(reversed([(v, f"{where}[{i}]") for i, v in enumerate(item)]))
    return problems


def reference(inventory):
    """The capture profiles and Office builds design/inventory/REFERENCE.md records, from the inventory's own copy or
    the repository's. Returns (profile ids, builds)."""
    path = Path(inventory) / REFERENCE
    path = path if path.is_file() else INVENTORY / REFERENCE
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise Unreadable(f"{path}: cannot read ({exc})") from None
    profiles = set(re.findall(r"Profile `([A-Za-z0-9-]+)`", text))
    builds = set(re.findall(r"^\| [^|]+ \| [^|]+ \| (\d+\.\d+\.\d+\.\d+) \|", text, flags=re.M))
    return profiles, builds


LOOP_SHOWN = 20  # ids a parent-loop diagnostic names before eliding the rest


def parent_loops(parents):
    """For every id whose parent chain loops: (the first ids of that chain, the id it repeats, the chain's length
    before the repeat), as in a -> b -> c -> b. Each id is walked once and each answer holds at most LOOP_SHOWN ids,
    so the whole inventory costs time linear in its size, however long the chains or cycles."""
    loops, settled = {}, set()
    for start in parents:
        if start in settled:
            continue
        path, index, node = [], {}, start
        while node in parents and node not in settled and node not in index:
            index[node] = len(path)
            path.append(node)
            node = parents[node]
        for i, n in enumerate(path):
            head = path[i:i + LOOP_SHOWN]
            if node in index and i >= index[node]:  # n is on the cycle: once round it and back to n
                c = index[node]
                head += path[c:c + min(LOOP_SHOWN - len(head), i - c)]
                loops[n] = (head, n, len(path) - c)
            elif node in index:  # n leads into the cycle
                loops[n] = (head, node, len(path) - i)
            elif node in loops:  # this walk runs into a chain already known to loop
                later, repeat, size = loops[node]
                loops[n] = (head + later[:LOOP_SHOWN - len(head)], repeat, len(path) - i + size)
        settled.update(path)
    return loops


def loop_text(loop):
    """a -> b -> c -> b, with the middle elided past LOOP_SHOWN ids."""
    head, repeat, size = loop
    return " -> ".join(head) + (" -> ..." if size > len(head) else "") + f" -> {repeat}"


def printable(text):
    """text with every character that is not printable (controls such as ESC, format characters such as bidi
    overrides, lone surrogates) written as an escape, so a record's own content cannot rewrite the terminal."""
    return "".join(ch if ch.isprintable() else ascii(ch)[1:-1] for ch in str(text))


def unique_pairs(pairs):
    """A JSON object hook that refuses a repeated member: json would keep the last value and silently drop the first."""
    seen, repeated = set(), set()
    for key, _ in pairs:  # one pass, so a large object costs linear time
        (repeated if key in seen else seen).add(key)
    if repeated:
        raise ValueError(f"repeated member {', '.join(sorted(repeated))}")
    return dict(pairs)


def no_constant(name):
    """A JSON parse_constant hook: NaN, Infinity and -Infinity are not JSON, though Python's decoder accepts them."""
    raise ValueError(f"{name} is not a JSON value")


def load(path):
    try:
        # Decimal keeps JSON numbers exact: 1.0000000000000001 stays non-integral and -1e-400 stays negative.
        data = json.loads(Path(path).read_text(encoding="utf-8"), parse_float=Decimal, object_pairs_hook=unique_pairs,
                          parse_constant=no_constant)
    # ValueError covers malformed JSON and integers past the conversion limit; RecursionError covers deep nesting.
    except (OSError, UnicodeDecodeError, ValueError, RecursionError, InvalidOperation) as exc:
        raise Unreadable(f"{path}: cannot read ({exc})") from None
    return data


def inventory_files(paths, manifest=INVENTORY / SOURCES):
    """Every inventory file under the named folders, and the named files. Only the source manifest itself (at the
    inventory's root) is left out; a file of that name anywhere else is checked like any other."""
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            skip = (SCHEMA.resolve(), BASELINE_SCHEMA.resolve(), Path(manifest).resolve())
            files += sorted(f for f in p.rglob("*.json") if f.resolve() not in skip)
        else:
            files.append(p)
    return files


def outlook_windows(sources):
    return sorted(n[len("outlook"):-len("controls.xlsx")] for n in sources.get("blobs", {}) if n.startswith("outlook"))


def check_baseline(f, data, schema, sources=None):
    """Problems in one baseline file: its envelope against the baseline schema, then every row's cells, and with the
    upstream manifest its commit and (for Outlook) its window names."""
    problems = [f"{f}: {p}" for p in validate(data, schema, schema)]
    if problems or not isinstance(data, dict):
        return problems
    if not data["rows"]:
        return [f"{f}: no rows"]
    if sources and data["source"] != f"baseline:{sources.get('commit')}":
        problems.append(f"{f}: source {data['source']} is not the manifest commit {sources.get('commit')}")
    defs = schema["$defs"]
    expected = defs["outlookColumns"]["const"] if f.parent.name == "outlook" else defs["columns"]["const"]
    if data["columns"] != expected:
        return [f"{f}: columns {data['columns']} are not {expected}"]
    kinds = {"placement": defs["placement"], "policyId": defs["policyId"]}
    windows = set(outlook_windows(sources or {}))
    for i, row in enumerate(data["rows"]):
        if len(row) != len(expected):
            problems.append(f"{f}: $.rows[{i}]: {len(row)} cells, expected {len(expected)}")
            continue
        for name, cell in zip(expected, row):
            if name == "window" and not isinstance(cell, str):  # checked before any set lookup, which needs a string
                problems.append(f"{f}: $.rows[{i}].window: {cell!r} is not a window name")
                continue
            if name == "window" and sources and cell not in windows:
                problems.append(f"{f}: $.rows[{i}].window: {cell!r} is not a window in the manifest")
                continue
            if cell is None and name not in ("controlType", "window"):
                continue
            problems += [f"{f}: {p}" for p in validate(cell, kinds.get(name, defs["identifier"]), schema,
                                                       f"$.rows[{i}].{name}")]
    return problems


def check(paths, require_behaviour=False, inventory=INVENTORY):
    """Return problems for the named files, resolving ids and parents across the whole inventory plus those files."""
    schema = load(SCHEMA)
    baseline_schema = None
    manifest = Path(inventory) / SOURCES
    named = [Path(f) for f in inventory_files(paths, manifest)]
    universe = {f.resolve(): f for f in inventory_files([inventory], manifest)} if Path(inventory).is_dir() else {}
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
    # A parent chain is followed only through ids defined once; an ambiguous parent is reported on its own.
    parents = {}
    for resolved, f in universe.items():
        for rec in records[resolved]:
            if isinstance(rec, dict) and isinstance(rec.get("id"), str) and isinstance(rec.get("parent"), str):
                if len(seen.get(rec["id"], [])) == 1:
                    parents[rec["id"]] = rec["parent"]
    link = ecma(schema["$defs"]["noLink"]["not"]["pattern"])
    loops = parent_loops(parents)
    profiles, builds = reference(inventory)
    inventory = Path(inventory)
    sources_path = inventory / SOURCES
    manifest = sources_path.is_file()
    sources = load(sources_path) if manifest else None
    # A manifest that exists is read as an object with a string commit and an object of blobs; anything else, JSON
    # null included, cannot be used, and must not pass for an absent manifest.
    if manifest and not (isinstance(sources, dict) and isinstance(sources.get("commit"), str)
                         and isinstance(sources.get("blobs"), dict)):
        raise Unreadable(f"{sources_path}: not a manifest (an object with a commit string and a blobs object)")
    # Each blob is a workbook name and the 40-hex Git blob id design/inventory/REFERENCE.md records for it, and the
    # commit is a 40-hex Git commit id: anything else cannot identify what the baselines were imported from.
    if manifest:
        hex40 = re.compile(r"[0-9a-f]{40}", re.ASCII)
        bad = [name for name, blob in sources["blobs"].items()
               if not (re.fullmatch(r"[a-z]+controls\.xlsx", name, re.ASCII) and isinstance(blob, str)
                       and hex40.fullmatch(blob))]
        if bad or not hex40.fullmatch(sources["commit"]):
            raise Unreadable(f"{sources_path}: not a manifest: commit or blob ids malformed ({', '.join(sorted(bad))})")
        # The upstream folder has one workbook per app and one per Outlook window: each of the five single-workbook
        # apps exactly once, at least one Outlook window, and nothing else.
        names = set(sources["blobs"])
        single = {f"{app}controls.xlsx" for app in APPS if app != "outlook"}
        windows = {n for n in names if re.fullmatch(r"outlook[a-z]+controls\.xlsx", n, re.ASCII)}
        missing, extra = sorted(single - names), sorted(names - single - windows)
        if missing or extra or not windows:
            raise Unreadable(f"{sources_path}: not the upstream workbook set (missing {missing or 'none'}, "
                             f"unexpected {extra or 'none'}, Outlook windows {len(windows)})")
    # The baseline every baseline: source must name: this inventory's manifest, or the repository's when it has none.
    baseline_commit = (sources if manifest else load(INVENTORY / SOURCES))["commit"]
    # A run over the whole inventory is the acceptance gate: once the manifest declares a baseline, every app's must
    # exist and Outlook's must hold every window it lists. Checking one file stays a check of that file alone.
    whole = inventory.is_dir() and inventory.resolve() in [Path(p).resolve() for p in paths]
    if whole and sources is not None:
        for app in APPS:
            path = inventory / app / BASELINE
            if not path.is_file():
                problems.append(f"{path}: missing baseline")
            elif app == "outlook" and sources:
                data = load(path)
                rows = data.get("rows") if isinstance(data, dict) else None
                rows = rows if isinstance(rows, list) else []  # a malformed envelope is reported by check_baseline
                windows_seen = {r[0] for r in rows if isinstance(r, list) and r and isinstance(r[0], str)}
                absent = [w for w in outlook_windows(sources) if w not in windows_seen]
                if absent:
                    problems.append(f"{path}: no rows for the windows {absent}")
    for resolved in named_resolved:
        f = universe[resolved]
        data = load(f)
        if f.name == BASELINE:
            baseline_schema = baseline_schema or load(BASELINE_SCHEMA)
            problems += check_baseline(f, data, baseline_schema, sources)
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
            problems += [f"{f}: {p}" for p in links(rec, f"$[{i}]", link) if p.split(": ", 1)[0] not in reported]
            rid = rec.get("id")
            if isinstance(rid, str):
                if len(seen.get(rid, [])) > 1:
                    problems.append(f"{where}: duplicate id {rid} (also {', '.join(x for x in seen[rid] if x != where)})")
                if isinstance(rec.get("app"), str) and rid.split(".", 1)[0] != rec["app"]:
                    problems.append(f"{where}: id {rid} does not start with its app {rec['app']}")
            if isinstance(rid, str) and rid in parents:
                loop = loops.get(rid)
                if loop:
                    problems.append(f"{where}: parent chain loops: {loop_text(loop)}")
            profile, build = rec.get("captureProfile"), rec.get("capturedFrom")
            if isinstance(profile, str) and profile not in profiles:
                problems.append(f"{where}: captureProfile {profile} is not a profile in {REFERENCE}")
            if isinstance(build, str) and build not in builds:
                problems.append(f"{where}: capturedFrom {build} is not a build in {REFERENCE}")
            source = rec.get("source")
            stamped = re.fullmatch(r"[a-z]+:(\d+\.\d+\.\d+\.\d+)", source) if isinstance(source, str) else None
            pinned = re.fullmatch(r"baseline:([0-9a-f]{7,40})", source) if isinstance(source, str) else None
            if pinned and not baseline_commit.startswith(pinned.group(1)):
                problems.append(f"{where}: source baseline:{pinned.group(1)} is not the pinned baseline "
                                f"{baseline_commit}")
            if stamped and stamped.group(1) not in builds:
                problems.append(f"{where}: source build {stamped.group(1)} is not a build in {REFERENCE}")
            if stamped and isinstance(build, str) and stamped.group(1) != build:
                problems.append(f"{where}: source build {stamped.group(1)} is not capturedFrom {build}")
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
                if not str(rec.get("behaviour", "")).strip(ECMA_SPACE):  # the schema's whitespace, not Python's
                    problems.append(f"{where}: control {rid} has no behaviour")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the parity inventory.")
    parser.add_argument("paths", nargs="*", default=[str(INVENTORY)], help="files or folders (default: design/inventory)")
    parser.add_argument("--require-behaviour", action="store_true",
                        help="every control must have a non-blank behaviour sentence")
    args = parser.parse_args(argv)
    # A record's own text appears in every diagnostic, the unreadable-file ones included: escape what the console
    # cannot encode (a lone surrogate, or anything outside a legacy code page) instead of crashing on the report.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    missing = [p for p in args.paths if not Path(p).exists()]
    if missing:
        print("\n".join(printable(f"{p}: no such file or folder") for p in missing), file=sys.stderr)
        return 2
    try:
        problems = check(args.paths, args.require_behaviour)
    except Unreadable as exc:
        print(printable(exc), file=sys.stderr)
        return 2
    for problem in problems:
        print(printable(problem))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
