#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The reviewer pin: who reviews whose work, in which passes, through which lenses, and how many passes a section may
spend. `.conclave/reviewers.toml` is the one copy of those rules, and this module is the one place they are checked:
scripts/review-dispatch.py and the todo kit's stamp both read the pin through it. It names no project path or rule
beyond the pin's conventional place beside this file's folder, so a project can copy this one file.

    python3 scripts/review_pin.py --check [--pin <path>]            ok, or the refusal (exit 2)
    python3 scripts/review_pin.py --check --all [--pin <path>]      every independent fault, one line each (exit 2)
    python3 scripts/review_pin.py --lenses <kind> [--paths <file> ...] [--pin <path>]
                                                                    that pass's lenses, one `name: question` per line;
                                                                    the conditional ones only for the files given
    python3 scripts/review_pin.py --caps [--pin <path>]             pass_cap and no_progress_cap

The pin (`schema_version = 1`) holds `[reviewers.<name>]` (`cli`, `model`, optional `effort`), `[routes]` (one reviewer
per writer, never of the writer's own model family; the writers are `claude`, `codex` and `agy`, with `gemini` as
another name for `agy`) and an optional `[schedule]` in one of two shapes.

Rotation (no `policy` key): `plan`, `completion`, `rounds`, `rotation`, `escalation` and `severity_stop_after`. Fixed
rounds, then one lens per round in rotation, until a round has no P1 or P2 finding.

Three-pass (`policy = "three-pass"`): `plan`, exactly one `[[schedule.rounds]]` entry, `completion` and
`reconciliation`, run in that order, the reconciliation only after a completion that returned gaps. It may add:

    pass_cap = 33                  the most returned passes a section may take in all (3 to 999; absent reads as 33)
    no_progress_cap = 3            the most passes in a row that return gaps no less severe than the pass before
    blocking = ["P1", "P2"]        the severities that hold the stamp; absent, every finding does
    [schedule.lenses]              extra lens names, each with the question the reviewer is given
    [[schedule.conditional]]       lenses, passes, paths: the lenses join those passes only for a section whose
                                   changed files fall under one of the repository-relative path prefixes

Under three-pass a lens belongs to one of plan, the round and completion (reconciliation may repeat lenses). A
conditional entry may not hand one of those owned lenses to another of the three; a lens that exists only in a
conditional entry joins exactly the passes that entry names. An Antigravity reviewer's model name must end with
every effort the schedule sets. `effort` is optional everywhere: with a schedule, the step alone decides, and a step
without one passes no effort to the reviewer's CLI, whose own configuration then decides; without a schedule the
reviewer's `effort` does, or the CLI's configuration when it has none. Standard library only.
"""
import argparse
from pathlib import Path
import re
import sys
import tomllib

PIN = Path(__file__).resolve().parents[1] / ".conclave" / "reviewers.toml"
# `agy` is the Antigravity CLI and `gemini` the model family it runs: one writer under two names. A pin routes it
# under either name, never both, and a review asked for under one name finds the route under the other.
WRITERS = ("claude", "codex", "agy", "gemini")
ALIASES = {"agy": "gemini", "gemini": "agy"}
CLIS = ("codex", "agy", "claude")
# A reviewer is never of the writer's own model family: its CLI names the family, and so does the writer.
FAMILY = {"codex": "openai", "agy": "google", "claude": "anthropic"}
WRITER_FAMILY = {"claude": "anthropic", "codex": "openai", "agy": "google", "gemini": "google"}
# Antigravity carries the effort in its model name, so it takes none.
EFFORTS = {"codex": ("low", "medium", "high", "xhigh"), "claude": ("low", "medium", "high", "xhigh", "max")}
MODEL = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
THREE_PASS = "three-pass"
# The passes of a three-pass section, in the order they run.
SECTION_KINDS = ("plan", "round", "completion", "reconciliation")
SEVERITIES = ("P1", "P2", "P3")
# What a three-pass pin without `pass_cap` means: the cap the loop had before the key existed.
DEFAULT_PASS_CAP = 33
# Plan, round and completion always run, so a cap below three could never stamp a section.
MIN_PASS_CAP = 3
MAX_PASS_CAP = 999


class Refused(Exception):
    """The pin or the arguments are wrong; nothing ran."""


def _read(path, data):
    """The pin's TOML as a dict, or the refusal for a pin that cannot be read at all."""
    try:
        if data is None:
            with open(path, "rb") as handle:
                data = handle.read()
        return tomllib.loads(data.decode("utf-8"))
    except FileNotFoundError:
        raise Refused(f"no reviewer pin at {path}") from None
    except tomllib.TOMLDecodeError as exc:
        raise Refused(f"unreadable reviewer pin: {exc}") from None
    # A directory, a file it may not read, bytes that are not UTF-8, an integer past Python's digit limit, or nesting
    # deep enough to exhaust the parser's recursion: each is a pin that cannot be read, so it is a refusal (exit 2,
    # one JSON object), never a traceback. ValueError comes after its subclasses TOMLDecodeError and UnicodeDecodeError.
    except OSError as exc:
        raise Refused(f"unreadable reviewer pin: {exc.strerror or exc}: {path}") from None
    except UnicodeDecodeError:
        raise Refused("unreadable reviewer pin: not UTF-8 text") from None
    except ValueError as exc:
        raise Refused(f"unreadable reviewer pin: {exc}") from None
    except RecursionError:
        raise Refused("unreadable reviewer pin: nested too deeply to read") from None


def check_shape(pin):
    # `type(...) is int`: TOML true is Python True (an int subclass) and 1.0 == 1, so `!= 1` alone let both load.
    # The optional [schedule] is checked separately; this refusal text is part of the --check-pin contract.
    if not {"schema_version", "reviewers", "routes"} <= set(pin) <= {"schema_version", "reviewers", "routes",
                                                                     "schedule"} \
            or type(pin["schema_version"]) is not int or pin["schema_version"] != 1:
        raise Refused("the reviewer pin needs exactly schema_version = 1, [reviewers.*] and [routes]")


def check_reviewers_table(reviewers):
    if not isinstance(reviewers, dict) or not reviewers:
        raise Refused("the reviewer pin defines no reviewers")


def check_reviewer_entry(name, entry):
    # fullmatch: `$` alone also matches before a trailing newline, which would then break the round heading.
    if not NAME.fullmatch(name) or not isinstance(entry, dict):
        raise Refused(f"invalid reviewer {name!r}")


def check_reviewer_keys(name, entry):
    unknown = set(entry) - {"cli", "model", "effort"}
    if unknown:
        raise Refused(f"reviewer {name!r} has unknown keys: {', '.join(sorted(unknown))}")


def check_reviewer_cli(name, entry):
    if not _one_of(entry.get("cli"), CLIS):
        raise Refused(f"reviewer {name!r} needs cli = one of {', '.join(CLIS)}")


def check_reviewer_model(name, entry):
    model = entry.get("model")
    if not isinstance(model, str) or not MODEL.fullmatch(model):
        raise Refused(f"reviewer {name!r} has a malformed model")


def check_reviewer_effort(name, entry):
    """Rests on a sound `cli`: which efforts it takes, and whether it takes one at all."""
    cli = entry["cli"]
    if cli == "agy":
        if "effort" in entry:
            raise Refused(f"reviewer {name!r}: Antigravity carries the effort in the model name, so set no effort")
    # Optional: the reviewer's effort is what a pin without a [schedule] runs at; without one, its CLI decides.
    elif "effort" in entry and not _one_of(entry["effort"], EFFORTS[cli]):
        raise Refused(f"reviewer {name!r} needs effort = one of {', '.join(EFFORTS[cli])}")


def check_reviewer(name, entry):
    check_reviewer_entry(name, entry)
    check_reviewer_keys(name, entry)
    check_reviewer_cli(name, entry)
    check_reviewer_model(name, entry)
    check_reviewer_effort(name, entry)


def check_writers(routes):
    if not isinstance(routes, dict) or set(routes) - set(WRITERS):
        raise Refused(f"[routes] may only name the writers {', '.join(WRITERS)}")
    doubled = sorted(name for name in routes if ALIASES.get(name) in routes)
    if doubled:
        raise Refused(f"[routes] names both {' and '.join(doubled)}, which are one writer; keep one of them")


def check_route(writer, chain, reviewers):
    if not isinstance(chain, list) or len(chain) != 1 or not isinstance(chain[0], str):
        raise Refused(f"route {writer!r} must list exactly one reviewer")
    if chain[0] not in reviewers:
        raise Refused(f"route {writer!r} must list a defined reviewer")
    if FAMILY[reviewers[chain[0]]["cli"]] == WRITER_FAMILY[writer]:
        raise Refused(f"route {writer!r} names {chain[0]}, of the writer's own family; "
                      f"a review comes from a different family")


def load_pin(path=PIN, data=None):
    """The checked pin at `path`, or, given `data`, the pin in those bytes (a committed pin read with `git show`), so
    a read-only caller needs no temporary file. It raises the first fault in its own fixed order; `faults` lists
    every independent one."""
    pin = _read(path, data)
    check_shape(pin)
    reviewers = pin["reviewers"]
    check_reviewers_table(reviewers)
    for name, entry in reviewers.items():
        check_reviewer(name, entry)
    routes = pin["routes"]
    check_writers(routes)
    for writer, chain in routes.items():
        check_route(writer, chain, reviewers)
    if "schedule" in pin:
        routed = list(dict.fromkeys(chain[0] for chain in routes.values()))
        check_schedule(pin["schedule"], {reviewers[name]["cli"] for name in routed})
        if pin["schedule"].get("policy") == THREE_PASS:
            for name in routed:
                if reviewers[name]["cli"] == "agy":
                    check_agy_effort(name, reviewers[name]["model"], pin["schedule"])
    return pin


def step_holds(holds, where, step, efforts, table, lenses):
    """One step's checks run one by one through `holds`, so its effort and its lenses are each reported: True when
    the step is sound. A step whose keys are wrong is still looked at for the fields it does have."""
    keys = holds(check_step_keys, where, step, lenses)
    if not isinstance(step, dict):
        return False
    effort = holds(check_step_effort, where, step, efforts)
    names = holds(check_step_lenses, where, step, table)
    return keys and effort and names


def faults(path=PIN, data=None):
    """Every independent fault of the pin, as the messages `load_pin` would refuse with one at a time, in the order of
    the pin's tables: the reviewers, the routes, then the schedule's keys as the file gives them. Empty for a pin
    that loads. A pin that cannot be read is its one fault.

    A check that rests on a part already reported is skipped, so nothing is reported twice and nothing is invented:
    a route to a reviewer whose own entry is at fault, everything under a schedule whose key set or policy is wrong,
    the one-owner rule and a conditional entry's overlap when a step they read is at fault, `no_progress_cap`'s
    upper bound when `pass_cap` is at fault, and an Antigravity reviewer's effort when a step is."""
    try:
        pin = _read(path, data)
    except Refused as exc:
        return [str(exc)]
    found = []

    def holds(check, *args):
        try:
            check(*args)
            return True
        except Refused as exc:
            if str(exc) not in found:
                found.append(str(exc))
            return False

    if not isinstance(pin, dict):
        return ["the reviewer pin needs exactly schema_version = 1, [reviewers.*] and [routes]"]
    holds(check_shape, pin)
    reviewers = pin.get("reviewers")
    good = {}
    if "reviewers" in pin and holds(check_reviewers_table, reviewers):
        for name, entry in reviewers.items():
            if not holds(check_reviewer_entry, name, entry):
                continue
            # Each field on its own; the effort only when the cli it depends on is sound.
            sound_fields = [holds(check_reviewer_keys, name, entry), holds(check_reviewer_cli, name, entry),
                            holds(check_reviewer_model, name, entry)]
            if sound_fields[1]:
                sound_fields.append(holds(check_reviewer_effort, name, entry))
            if all(sound_fields):
                good[name] = entry
    routes = pin.get("routes")
    routed = []
    if "routes" in pin and holds(check_writers, routes):
        for writer, chain in routes.items():
            named = chain[0] if isinstance(chain, list) and len(chain) == 1 and isinstance(chain[0], str) else None
            if named is not None and isinstance(reviewers, dict) and named in reviewers and named not in good:
                continue  # its reviewer's own entry is already reported
            if holds(check_route, writer, chain, good) and named not in routed:
                routed.append(named)
    if "schedule" not in pin:
        return found
    schedule = pin["schedule"]
    efforts = [e for e in EFFORTS["claude"]
               if all(e in EFFORTS[good[name]["cli"]] for name in routed if good[name]["cli"] in EFFORTS)]
    if not isinstance(schedule, dict) or "policy" not in schedule:
        if not isinstance(schedule, dict) or set(schedule) != ROTATION_KEYS:
            holds(check_schedule, schedule, set())
            return found
        for key, step in schedule.items():
            if key == "rounds":
                if isinstance(step, list) and step:
                    for n, entry in enumerate(step, 1):
                        step_holds(holds, f"round {n}", entry, efforts, LENSES, "required")
                else:
                    found.append("[schedule] rounds needs at least one round")
            elif key == "severity_stop_after":
                if type(step) is not int or not 0 <= step <= 33:
                    found.append("[schedule] severity_stop_after needs a whole number of rounds from 0 to 33")
            else:
                step_holds(holds, key, step, efforts, LENSES, "none" if key == "completion" else "required")
        return found
    if schedule["policy"] != THREE_PASS or not holds(check_three_pass_keys, schedule):
        if schedule["policy"] != THREE_PASS:
            found.append(f"[schedule] policy must be \"{THREE_PASS}\"; a schedule without the key rotates")
        return found
    # Collected per key, then given in the order the file has the schedule's keys.
    per = {key: [] for key in schedule}
    late = []

    def into(bucket, check, *args):
        try:
            check(*args)
            return True
        except Refused as exc:
            if str(exc) not in bucket:
                bucket.append(str(exc))
            return False

    extra = schedule.get("lenses", {})
    table = dict(LENSES)
    if into(per.get("lenses", late), check_extra_lenses_table, extra):
        for name, question in extra.items():
            into(per["lenses"], check_extra_lens_name, name)
            into(per["lenses"], check_extra_lens_question, name, question)
            # Declared, whatever is wrong with its entry: a step or a conditional entry that names it is not at
            # fault for that, so the fault is reported once, where the lens is declared.
            table.setdefault(name, "")
    sound = {kind: step_holds(lambda check, *args, k=kind: into(per[k], check, *args), kind, schedule[kind],
                              efforts, table, "optional" if kind == "completion" else "required")
             for kind in ("plan", "completion", "reconciliation")}
    sound["round"] = into(per["rounds"], check_one_round, schedule["rounds"]) \
        and step_holds(lambda check, *args: into(per["rounds"], check, *args), "round 1", schedule["rounds"][0],
                       efforts, table, "required")
    cap_sound = "pass_cap" not in schedule or into(per["pass_cap"], check_pass_cap, schedule)
    if "no_progress_cap" in schedule:
        stall = schedule["no_progress_cap"]
        if cap_sound:
            into(per["no_progress_cap"], check_no_progress_cap, schedule)
        elif type(stall) is not int or stall < 1:
            # pass_cap is already reported, so only what does not rest on it is said here.
            per["no_progress_cap"].append("[schedule] no_progress_cap needs a whole number of passes from 1 to pass_cap")
    if "blocking" in schedule:
        into(per["blocking"], check_blocking, schedule)
    # The one-owner rule and a conditional entry's overlap read the steps' lens lists, not their efforts: a step
    # whose effort is at fault still has lenses to hold to the rule.

    def lenses_sound(step, required):
        return isinstance(step, dict) and (("lenses" in step and _lens_list(step["lenses"], table))
                                           or ("lenses" not in step and not required))
    rounds = schedule["rounds"]
    listed = {"plan": lenses_sound(schedule["plan"], True), "completion": lenses_sound(schedule["completion"], False),
              "reconciliation": lenses_sound(schedule["reconciliation"], True),
              "round": isinstance(rounds, list) and len(rounds) == 1 and lenses_sound(rounds[0], True)}
    owners = None
    if all(listed[kind] for kind in ("plan", "round", "completion")):
        owners, conflicts = lens_ownership(schedule)
        late.extend(conflicts)
    if "conditional" in schedule and into(per["conditional"], check_conditional_table, schedule["conditional"]):
        for n, entry in enumerate(schedule["conditional"], 1):
            if not into(per["conditional"], check_conditional_keys, n, entry):
                continue
            fields = [into(per["conditional"], check_conditional_lenses, n, entry, table),
                      into(per["conditional"], check_conditional_passes, n, entry),
                      into(per["conditional"], check_conditional_paths, n, entry)]
            if all(fields) and owners is not None and listed["reconciliation"]:
                into(per["conditional"], check_conditional_overlap, n, entry, schedule, owners)
    if all(sound.values()):
        for name in routed:
            if good[name]["cli"] == "agy":
                into(late, check_agy_effort, name, good[name]["model"], schedule)
    return found + [message for key in schedule for message in per[key]] + late


def route_for(pin, writer):
    """The one reviewer name the pin routes `writer` to, under that name or its alias, or None."""
    chain = pin["routes"].get(writer) or pin["routes"].get(ALIASES.get(writer))
    return chain[0] if chain else None


def _one_of(value, allowed):
    """`value in allowed` for a value that may be unhashable or of another type (a TOML table, a number)."""
    return isinstance(value, str) and value in allowed


# The lenses every schedule may name, each with the question the reviewer is given for it. `plan` and `plan-delivery`
# read the section's plan: before the build (is it a complete feature?) and after it (did the build deliver it?). A
# project adds its own under [schedule.lenses].
LENSES = {
    "plan": "Will this section, built exactly as written, produce a 100% complete feature? Name every missing "
            "control, state, setting consumer, error or refusal path, undo or reverse path, Ctrl+K reach, persistence "
            "read-back and test, and every `Done when:` that cannot fail.",
    "plan-delivery": "Did the build deliver every checklist item and `Done when:` of the section, with nothing "
                     "partial, stubbed or quietly narrowed?",
    "adversarial": "How does this fail on hostile input, races, aborts, cancellation, automation or links?",
    "integration": "Do callers and consumers still hold, with every contract (threads, ownership, errors) kept?",
    "source-defect": "Is the upstream specification or design/SPEC.md read accurately, with deviations noted?",
    "consistency": "Does it match the module rules, naming, shared components, settings and sibling code?",
    "quality": "Is the code clear, minimal and maintainable: dead code, duplication, misleading names or comments, "
               "tests that pass without exercising the behaviour?",
    "design": "Does the rendered UI match design/SPEC.md and its tokens: roles, radii, icons, states, accessibility?",
    "optimization": "Where does it waste time, memory, allocations, I/O or redraws on the paths users hit, and what "
                    "measured target does it miss?",
    "record": "Does the evidence match what ran, with owned deferrals and an earned flip of every item?",
}
STEP_KEYS = {"effort", "lenses"}
ROTATION_KEYS = {"plan", "completion", "rounds", "rotation", "escalation", "severity_stop_after"}
THREE_PASS_KEYS = {"policy", "plan", "completion", "rounds", "reconciliation"}
THREE_PASS_OPTIONAL = {"pass_cap", "no_progress_cap", "blocking", "lenses", "conditional"}
CONDITIONAL_KEYS = {"lenses", "passes", "paths"}


def lens_table(schedule):
    """Every lens a schedule may name with its question: the built-in ones, then the pin's own [schedule.lenses]."""
    extra = schedule.get("lenses") if isinstance(schedule, dict) else None
    return {**LENSES, **extra} if isinstance(extra, dict) else dict(LENSES)


def _lens_list(names, table):
    return isinstance(names, list) and bool(names) and all(isinstance(n, str) and n in table for n in names) \
        and len(set(names)) == len(names)


def check_step_keys(where, step, lenses="required"):
    need = {"required": "lenses, and may set effort", "optional": "only effort and lenses",
            "none": "only effort"}[lenses]
    if not isinstance(step, dict) or set(step) - STEP_KEYS or (lenses == "required" and "lenses" not in step) \
            or (lenses == "none" and "lenses" in step):
        allowed = STEP_KEYS - ({"lenses"} if lenses == "none" else set())
        raise Refused(f"[schedule] {where} needs {need}"
                      + (_keys(step, {"lenses"} if lenses == "required" else (), allowed)
                         if isinstance(step, dict) else ""))


def check_step_effort(where, step, efforts):
    if "effort" in step and not _one_of(step["effort"], efforts):
        raise Refused(f"[schedule] {where} needs effort = one of {', '.join(efforts)}")


def check_step_lenses(where, step, table):
    if "lenses" in step and not _lens_list(step["lenses"], table):
        raise Refused(f"[schedule] {where} needs lenses = a list of distinct lenses from {', '.join(table)}")


def check_step(where, step, efforts, table=LENSES, lenses="required"):
    """One schedule step. `lenses` is "required", "optional" or "none"; `effort` is always optional."""
    check_step_keys(where, step, lenses)
    check_step_effort(where, step, efforts)
    check_step_lenses(where, step, table)


def check_agy_effort(name, model, schedule):
    """An Antigravity reviewer runs at its model name's effort whatever the schedule says, so under three-pass the two
    must agree, or a pass would be recorded at an effort it did not run at."""
    steps = [schedule[k] for k in ("plan", "completion", "reconciliation")] + list(schedule["rounds"])
    for effort in dict.fromkeys(step["effort"] for step in steps if "effort" in step):
        if not model.endswith(f"-{effort}"):
            raise Refused(f"reviewer {name!r} runs at the effort in its model name {model}, but the schedule has a "
                          f"pass at effort = {effort}")


def check_schedule(schedule, clis):
    """The review schedule, as strictly as the reviewers: every effort valid for every routed CLI that takes one (an
    Antigravity reviewer keeps the effort its model name carries), every lens known, every key of the right type."""
    efforts = [e for e in EFFORTS["claude"] if all(e in EFFORTS[cli] for cli in clis if cli in EFFORTS)]
    if not isinstance(schedule, dict):
        raise Refused(f"[schedule] needs exactly {', '.join(sorted(ROTATION_KEYS))}")
    if "policy" in schedule:
        if schedule["policy"] != THREE_PASS:
            raise Refused(f"[schedule] policy must be \"{THREE_PASS}\"; a schedule without the key rotates")
        check_three_pass(schedule, efforts)
        return
    # The rotation schedule, as it has always loaded: the three-pass keys are refused here, so a rotation pin means
    # what it meant.
    if set(schedule) != ROTATION_KEYS:
        raise Refused(f"[schedule] needs exactly {', '.join(sorted(ROTATION_KEYS))}"
                      + _keys(schedule, ROTATION_KEYS))
    check_step("plan", schedule["plan"], efforts)
    check_step("completion", schedule["completion"], efforts, lenses="none")
    check_step("escalation", schedule["escalation"], efforts)
    check_step("rotation", schedule["rotation"], efforts)
    rounds = schedule["rounds"]
    if not isinstance(rounds, list) or not rounds:
        raise Refused("[schedule] rounds needs at least one round")
    for n, step in enumerate(rounds, 1):
        check_step(f"round {n}", step, efforts)
    stop = schedule["severity_stop_after"]
    if type(stop) is not int or not 0 <= stop <= 33:
        raise Refused("[schedule] severity_stop_after needs a whole number of rounds from 0 to 33")


def check_three_pass_keys(schedule):
    if not THREE_PASS_KEYS <= set(schedule) <= THREE_PASS_KEYS | THREE_PASS_OPTIONAL:
        raise Refused(f"[schedule] with policy = \"{THREE_PASS}\" needs exactly {', '.join(sorted(THREE_PASS_KEYS))}, "
                      f"and may add {', '.join(sorted(THREE_PASS_OPTIONAL))}"
                      + _keys(schedule, THREE_PASS_KEYS, THREE_PASS_OPTIONAL))


def check_extra_lenses_table(extra):
    if not isinstance(extra, dict):
        raise Refused("[schedule.lenses] must be a table of lens name = \"question\"")


def check_extra_lens_name(name):
    if not NAME.fullmatch(name):
        raise Refused(f"[schedule.lenses] {name!r} is not a lens name (lowercase letters, digits and dashes)")
    if name in LENSES:
        raise Refused(f"[schedule.lenses] {name!r} is already a built-in lens; a pin adds lenses, it does not "
                      f"redefine them")


def check_extra_lens_question(name, question):
    if not isinstance(question, str) or not question.strip() or "\n" in question or "\r" in question:
        raise Refused(f"[schedule.lenses] {name!r} needs its question as one line of text")


def check_extra_lens(name, question):
    check_extra_lens_name(name)
    check_extra_lens_question(name, question)


def check_one_round(rounds):
    if not isinstance(rounds, list) or len(rounds) != 1:
        raise Refused(f"[schedule] with policy = \"{THREE_PASS}\" needs exactly one round in rounds")


def lens_owners(schedule):
    """lens -> the one of plan, round and completion that always has it. One owner per lens: plan, the round and
    completion each ask their own questions. Reconciliation rechecks a repaired candidate, so it may repeat lenses."""
    seen, conflicts = lens_ownership(schedule)
    if conflicts:
        raise Refused(conflicts[0])
    return seen


def lens_ownership(schedule):
    """(lens -> its first owner among plan, round and completion, every conflict as its refusal message): what
    `lens_owners` raises the first of and `faults` lists all of."""
    owned = {"plan": schedule["plan"]["lenses"], "round": schedule["rounds"][0]["lenses"],
             "completion": schedule["completion"].get("lenses", [])}
    seen, conflicts = {}, []
    for kind, names in owned.items():
        for name in names:
            if name in seen:
                conflicts.append(f"[schedule] the lens {name} is listed in both {seen[name]} and {kind}; a lens "
                                 f"belongs to one of plan, the round and completion")
            else:
                seen[name] = kind
    return seen, conflicts


def check_pass_cap(schedule):
    cap = schedule["pass_cap"]
    if type(cap) is not int or not MIN_PASS_CAP <= cap <= MAX_PASS_CAP:
        raise Refused(f"[schedule] pass_cap needs a whole number of review passes from {MIN_PASS_CAP} to "
                      f"{MAX_PASS_CAP}")


def check_no_progress_cap(schedule):
    stall = schedule["no_progress_cap"]
    if type(stall) is not int or not 1 <= stall <= pass_cap(schedule):
        raise Refused(f"[schedule] no_progress_cap needs a whole number of passes from 1 to pass_cap "
                      f"({pass_cap(schedule)})")


def check_blocking(schedule):
    levels = schedule["blocking"]
    if not isinstance(levels, list) or not all(_one_of(level, SEVERITIES) for level in levels) \
            or len(set(levels)) != len(levels) or "P1" not in levels:
        raise Refused(f"[schedule] blocking needs a list of distinct levels from {', '.join(SEVERITIES)}, with P1 "
                      f"among them")


def check_conditional_table(entries):
    if not isinstance(entries, list):
        raise Refused("[[schedule.conditional]] must be an array of tables")


def check_conditional_keys(n, entry):
    if not isinstance(entry, dict) or set(entry) != CONDITIONAL_KEYS:
        raise Refused(f"[[schedule.conditional]] entry {n} needs exactly {', '.join(sorted(CONDITIONAL_KEYS))}"
                      + (_keys(entry, CONDITIONAL_KEYS) if isinstance(entry, dict) else ""))


def check_conditional_lenses(n, entry, table):
    if not _lens_list(entry["lenses"], table):
        raise Refused(f"[[schedule.conditional]] entry {n} needs lenses = a list of distinct lenses from "
                      f"{', '.join(table)}")


def check_conditional_passes(n, entry):
    passes = entry["passes"]
    if not isinstance(passes, list) or not passes or not all(_one_of(p, SECTION_KINDS) for p in passes) \
            or len(set(passes)) != len(passes):
        raise Refused(f"[[schedule.conditional]] entry {n} needs passes = a list of distinct passes from "
                      f"{', '.join(SECTION_KINDS)}")


def check_conditional_paths(n, entry):
    paths = entry["paths"]
    if not isinstance(paths, list) or not paths or not all(_relative_prefix(p) for p in paths) \
            or len(set(paths)) != len(paths):
        raise Refused(f"[[schedule.conditional]] entry {n} needs paths = a list of distinct repository-relative path "
                      f"prefixes with forward slashes (no leading /, no empty, . or .. part, no drive)")


def check_conditional_entry(n, entry, table):
    check_conditional_keys(n, entry)
    check_conditional_lenses(n, entry, table)
    check_conditional_passes(n, entry)
    check_conditional_paths(n, entry)


def check_conditional_overlap(n, entry, schedule, owners):
    where = f"[[schedule.conditional]] entry {n}"
    for kind in entry["passes"]:
        always = schedule["rounds"][0] if kind == "round" else schedule[kind]
        repeated = [name for name in entry["lenses"] if name in always.get("lenses", [])]
        if repeated:
            raise Refused(f"{where} repeats the lens {repeated[0]}, which the {kind} pass always has")
        # The one-owner rule holds for conditional lenses too: a lens plan, the round or completion always has
        # cannot be handed to another of them by path. Reconciliation may repeat lenses, here as in its own list.
        taken = [name for name in entry["lenses"] if kind != "reconciliation" and name in owners]
        if taken:
            raise Refused(f"{where} gives the {kind} pass the lens {taken[0]}, which belongs to {owners[taken[0]]}; "
                          f"a lens belongs to one of plan, the round and completion")


def check_three_pass(schedule, efforts):
    """The three-pass schedule, in the order `load_pin` has always refused in."""
    check_three_pass_keys(schedule)
    extra = schedule.get("lenses", {})
    check_extra_lenses_table(extra)
    for name, question in extra.items():
        check_extra_lens(name, question)
    table = lens_table(schedule)
    check_step("plan", schedule["plan"], efforts, table)
    # Optional on completion: a pin written before completion had lenses of its own gives it none.
    check_step("completion", schedule["completion"], efforts, table, lenses="optional")
    check_step("reconciliation", schedule["reconciliation"], efforts, table)
    check_one_round(schedule["rounds"])
    check_step("round 1", schedule["rounds"][0], efforts, table)
    owners = lens_owners(schedule)
    if "pass_cap" in schedule:
        check_pass_cap(schedule)
    if "no_progress_cap" in schedule:
        check_no_progress_cap(schedule)
    if "blocking" in schedule:
        check_blocking(schedule)
    entries = schedule.get("conditional", [])
    check_conditional_table(entries)
    for n, entry in enumerate(entries, 1):
        check_conditional_entry(n, entry, table)
        check_conditional_overlap(n, entry, schedule, owners)


def _relative_prefix(path):
    """A path prefix as `git diff --name-only` spells paths: forward slashes, no drive, no leading slash, and no
    empty, `.` or `..` part (a trailing slash aside), so a prefix that loads is one a changed file can start with.
    A hidden folder such as `.github/` is an ordinary part."""
    if not isinstance(path, str) or not path or path != path.strip() or "\\" in path or ":" in path:
        return False
    parts = path.split("/")
    return all(part not in ("", ".", "..") for part in (parts[:-1] if parts[-1] == "" else parts)) and parts != [""]


def _keys(found, required, optional=()):
    """What is wrong with a table's keys, for a refusal: ` (unknown: a, b; missing: c)`."""
    unknown = sorted(str(k) for k in set(found) - set(required) - set(optional))
    missing = sorted(set(required) - set(found))
    said = [f"unknown: {', '.join(unknown)}"] if unknown else []
    said += [f"missing: {', '.join(missing)}"] if missing else []
    return f" ({'; '.join(said)})" if said else ""


def pass_cap(schedule):
    """The most returned review passes a three-pass section may take: plan, round, completion and every
    reconciliation together."""
    return schedule.get("pass_cap", DEFAULT_PASS_CAP)


def no_progress_cap(schedule):
    """The most passes in a row that may return gaps without the worst finding getting less severe, or None when the
    pin sets no such limit."""
    return schedule.get("no_progress_cap")


def blocks(schedule, highest_declared):
    """Whether a review whose worst finding is `highest_declared` holds the stamp. `P1`, `P2`, `P3`, "none", or None
    for a review that declared no HIGHEST line, which counts as P1. A pin without `blocking` blocks on every finding."""
    if highest_declared == "none":
        return False
    return (highest_declared or "P1") in schedule.get("blocking", SEVERITIES)


HIGHEST = re.compile(r"^\s*HIGHEST:\s*(P[123])\b", re.IGNORECASE | re.MULTILINE)
DECLARED = re.compile(r"^\s*HIGHEST:\s*(P[123]|none)\b", re.IGNORECASE | re.MULTILINE)


def highest(review):
    """The `HIGHEST:` severity a review declares (`P1`, `P2`, `P3`), or None."""
    found = HIGHEST.findall(review or "")
    return found[-1].upper() if found else None


def declared_highest(review):
    """The last `HIGHEST:` line of a review: `P1`, `P2`, `P3`, "none", or None when it has no such line."""
    found = DECLARED.findall(review or "")
    if not found:
        return None
    return "none" if found[-1].lower() == "none" else found[-1].upper()


def returned_review(entry):
    """A recorded round that is a review: a reviewer of another model family than the writer ran and replied with the
    prompt's final `OVERALL: approve` or `OVERALL: needs-attention` line. An outage, a self-review (a reviewer of the
    writer's own family, or of no known family) and a reply without that line are recorded rounds, not reviews. The
    todo kit's stamp uses this same predicate, so the schedule and the receipt count the same rounds."""
    lines = [x.strip() for x in (entry.get("review") or "").splitlines() if x.strip()]
    return bool(entry.get("reviewer")) and entry.get("writer") in WRITER_FAMILY \
        and FAMILY.get(entry.get("cli")) not in (None, WRITER_FAMILY[entry["writer"]]) \
        and bool(lines) and lines[-1] in ("OVERALL: approve", "OVERALL: needs-attention")


def lenses_for(schedule, kind, changed_paths=(), surface=True):
    """The lenses of one three-pass pass for a section that changed these files: the pass's own (the round's `design`
    only for a section with a surface), then each conditional entry that names the pass and has a path prefix one of
    the changed files starts with."""
    step = schedule["rounds"][0] if kind == "round" else schedule[kind]
    names = [n for n in step.get("lenses", []) if surface or kind != "round" or n != "design"]
    for entry in schedule.get("conditional", []):
        if kind in entry["passes"] and any(path.startswith(tuple(entry["paths"])) for path in changed_paths):
            names += [name for name in entry["lenses"] if name not in names]
    return names


def scheduled(schedule, kind, rounds, surface, changed_paths=()):
    """The effort and lenses for the next pass, from the pin's schedule and the rounds already recorded. `effort` is
    None for a step that sets none.

    Three-pass: the pass's lenses with its conditional ones (`lenses_for`); the one round's position is 1.

    Rotation: the position counts returned reviews only (`returned_review`): an outage, a self-review and a reply
    without the final OVERALL line do not move it. Rounds past the fixed list rotate through `rotation`'s lenses, one
    per round, skipping `design` when the section has no surface. After a low-effort round that declared
    `HIGHEST: P1`, the next round is the `escalation` step instead. The todo kit's stamp replays this to check every
    recorded pass, so it is the one copy of the schedule rule."""
    three_pass = schedule.get("policy") == THREE_PASS
    if kind != "round":
        step = schedule[kind]
        names = lenses_for(schedule, kind, changed_paths, surface) if three_pass else list(step.get("lenses", []))
        return {"position": None, "effort": step.get("effort"), "lenses": names, "escalated": False}
    returned = [r for r in rounds if returned_review(r)]
    position = len(returned) + 1
    if three_pass:
        return {"position": position, "effort": schedule["rounds"][0].get("effort"),
                "lenses": lenses_for(schedule, "round", changed_paths, surface), "escalated": False}
    last = returned[-1] if returned else None
    if last is not None and last.get("effort") == "low" and highest(last.get("review")) == "P1":
        step, escalated = schedule["escalation"], True
    elif position <= len(schedule["rounds"]):
        step, escalated = schedule["rounds"][position - 1], False
    else:
        rotation = [n for n in schedule["rotation"]["lenses"] if surface or n != "design"] \
            or schedule["rotation"]["lenses"]
        step = {"effort": schedule["rotation"].get("effort"),
                "lenses": [rotation[(position - len(schedule["rounds"]) - 1) % len(rotation)]]}
        escalated = False
    return {"position": position, "effort": step.get("effort"), "lenses": list(step["lenses"]),
            "escalated": escalated}


def lens_block(plan, schedule=None):
    """The prompt section naming this pass's scheduled lenses and effort, appended after the writer's prompt. Under
    three-pass it also asks for one `LENS <name>:` verdict line per lens and a `HIGHEST:` line, which the dispatcher
    checks (`missing_lens_verdicts`) before it records the reply as a review."""
    table = lens_table(schedule or {})
    if not plan["lenses"]:
        # A three-pass pass with no lenses of its own (a completion step in a pin written before completion had any)
        # still owes the severity line the blocking levels and the stamp read.
        return "\n".join(["", "", "## Verdict line for this pass (asked for by scripts/review-dispatch.py)", "",
                          "Before the final verdict line the prompt above asks for, write one line `HIGHEST: P1`, "
                          "`HIGHEST: P2`, `HIGHEST: P3` or `HIGHEST: none` for the worst finding of the whole review. "
                          "A reply without it is recorded as incomplete, not as a review."]) + "\n"
    where = f"Round {plan['position']}" if plan["position"] else "This pass"
    ran = f"{where} runs at {plan['effort']} reasoning effort" if plan["effort"] else f"{where} has these lenses"
    lines = ["", "", "## Lenses for this pass (scheduled by scripts/review-dispatch.py)", "",
             ran + (", escalated after a low-effort round found a P1" if plan["escalated"] else "")
             + ". Review through these lenses only, each as its own verdict, and ignore any other lens list above:",
             ""]
    lines += [f"- `{name}`: {table[name]}" for name in plan["lenses"]]
    if (schedule or {}).get("policy") == THREE_PASS:
        lines += ["", "Before the final verdict lines the prompt above asks for, write one line per lens, exactly "
                      "`LENS <name>: clean` or `LENS <name>: findings`, and then one line `HIGHEST: P1`, "
                      "`HIGHEST: P2`, `HIGHEST: P3` or `HIGHEST: none` for the worst finding of the whole review. A "
                      "reply that leaves out a lens line is recorded as incomplete, not as a review:", ""]
        lines += [f"LENS {name}: <clean|findings>" for name in plan["lenses"]]
    return "\n".join(lines) + "\n"


LENS_LINE = re.compile(r"^`?LENS ([a-z0-9][a-z0-9-]*): (clean|findings)`?$")


def missing_lens_verdicts(lenses, review):
    """The scheduled lenses a reply gave no `LENS <name>: clean` or `LENS <name>: findings` line for, in schedule
    order. Empty means every lens has its verdict."""
    seen = {m[1] for m in (LENS_LINE.match(line.strip()) for line in (review or "").splitlines()) if m}
    return [name for name in lenses if name not in seen]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Load the pin: ok, or the refusal (exit 2)")
    parser.add_argument("--all", action="store_true",
                        help="With --check: list every independent fault, one line each, instead of the first")
    group.add_argument("--lenses", metavar="KIND", choices=SECTION_KINDS,
                       help="Print that pass's lenses with their questions (three-pass pins)")
    group.add_argument("--caps", action="store_true", help="Print pass_cap and no_progress_cap (three-pass pins)")
    parser.add_argument("--paths", nargs="*", default=[], metavar="FILE",
                        help="With --lenses: the section's changed files, repository-relative with forward slashes, "
                             "so the conditional lenses that apply to them are listed too")
    parser.add_argument("--pin", default=str(PIN), help="The pin to read (default .conclave/reviewers.toml)")
    args = parser.parse_args(argv)
    if args.all and not args.check:
        parser.error("--all goes with --check")
    if args.all:
        found = faults(args.pin)
        for message in found:
            print(f"review-pin refused: {message}", file=sys.stderr)
        if not found:
            print("ok")
        return 2 if found else 0
    try:
        pin = load_pin(args.pin)
        schedule = pin.get("schedule", {})
        if not args.check and schedule.get("policy") != THREE_PASS:
            raise Refused(f"the pin's [schedule] is not policy = \"{THREE_PASS}\"")
        if args.check:
            print("ok")
        elif args.lenses:
            table = lens_table(schedule)
            for name in lenses_for(schedule, args.lenses, args.paths):
                print(f"{name}: {table[name]}")
        else:
            print(f"pass_cap {pass_cap(schedule)}")
            print(f"no_progress_cap {no_progress_cap(schedule) or 'none'}")
    except Refused as exc:
        print(f"review-pin refused: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
