# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""How a `shortcut` record writes its keys, and the conflict rule every app's shortcut inventory keeps (D02 T01 §17).

A chord is keys pressed together, joined by `+`: modifiers first, then one key. A sequence is chords pressed one after
another, joined by `, ` (as the ribbon's KeyTips are). A key that is itself `+` or `,` is written `Plus` or `Comma`,
so neither separator is ever a key. Modifiers may be written in any order (Word's own table writes `Alt+Ctrl+V`); two
chords are the same when their modifiers and key are, so they are compared in one canonical form, Ctrl, Alt, Shift.
"""
MODIFIERS = ("Ctrl", "Alt", "Shift")
# Where focus is when a key does what its record says. Keys mean different things in each.
SCOPES = frozenset({"document", "table", "outline", "read-mode", "print-preview", "ribbon", "dialog", "backstage",
                    "task-pane", "window", "ime"})
SEQUENCE = ", "
LITERAL = {"+": "Plus", ",": "Comma"}  # keys that would read as a separator


class Malformed(ValueError):
    """A chord that cannot be read as modifiers and one key per step."""


def steps(chord: str) -> tuple:
    """The chord's steps, each (modifiers as a frozenset, key). Raises Malformed."""
    if not isinstance(chord, str) or not chord.strip():
        raise Malformed("an empty chord")
    out = []
    for step in chord.split(SEQUENCE):
        mods, rest = set(), step
        while True:
            m = next((m for m in MODIFIERS if rest.startswith(m + "+") and len(rest) > len(m) + 1), None)
            if m is None:
                break
            if m in mods:
                raise Malformed(f"{chord!r} names {m} twice in one step")
            mods.add(m)
            rest = rest[len(m) + 1:]
        if not rest or rest != rest.strip() or (rest.endswith("+") and rest != "Num +"):
            raise Malformed(f"{chord!r} has a step with no key, or spaces around one")
        if rest in LITERAL:
            raise Malformed(f"{chord!r} writes the key {rest!r}; write {LITERAL[rest]}")
        out.append((frozenset(mods), rest))
    return tuple(out)


def canonical(chord: str) -> str:
    """The chord in the one form two chords are compared in: each step's modifiers in the order Ctrl, Alt, Shift."""
    return SEQUENCE.join("+".join([m for m in MODIFIERS if m in mods] + [key]) for mods, key in steps(chord))


def conflicts(records: list) -> list:
    """(the later record's id, the earlier one's, the chord, the scope) for every chord two records give in one scope
    of one app; records `problems` reports as unreadable are left out."""
    out, seen = [], {}
    for rec in records:
        if not _readable(rec):
            continue
        scope = rec.get("scope", "document")
        try:
            key = (rec["app"], canonical(rec["shortcut"]), scope)
        except Malformed:
            continue
        if key in seen:
            out.append((rec["id"], seen[key], key[1], scope))
        else:
            seen[key] = rec["id"]
    return out


def _readable(rec):
    return isinstance(rec, dict) and rec.get("kind") == "shortcut" and \
        all(isinstance(rec.get(k), str) for k in ("id", "app", "shortcut")) and \
        isinstance(rec.get("scope", "document"), str) and rec.get("scope", "document") in SCOPES


def problems(records: list) -> list:
    """Every chord that cannot be read, every scope outside SCOPES, and every chord two records give in one scope of
    one app. A record without a scope is in `document`, as every key in an app's own key table is."""
    out = []
    for rec in records:
        if not isinstance(rec, dict) or rec.get("kind") != "shortcut":
            continue
        if not all(isinstance(rec.get(k), str) for k in ("id", "app", "shortcut")):
            out.append(f"{rec.get('id')!r}: a shortcut's id, app and chord are text")
            continue
        scope = rec.get("scope", "document")
        if not isinstance(scope, str) or scope not in SCOPES:
            out.append(f"{rec.get('id')}: scope {scope!r} is not one of {', '.join(sorted(SCOPES))}")
        try:
            canonical(rec["shortcut"])
        except Malformed as exc:
            out.append(f"{rec['id']}: {exc}")
    return out + [f"{later}: {chord} in {scope} is already {earlier}'s"
                  for later, earlier, chord, scope in conflicts(records)]
