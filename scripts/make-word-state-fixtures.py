#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""Make the fixture documents the inventory is captured over in each document state (D02 T01 §36).

    python scripts/make-word-state-fixtures.py [--state <name> ...]

For each state of scripts/lib/word_states.py (all of them by default) the script makes one small document in a
hidden Word of its own, saves it under fixtures/word-states/ of the scratch folder (OFFICE_SCRATCH), brings it into
its state, opens it again and asks Word whether it is in that state. A fixture Word does not confirm is deleted and
fails the run. It writes nowhere else, changes no setting of Word, adds nothing to Word's list of recent files, and
quits only the Word it started: when that instance holds a document the script did not make, it is left running and
the run fails. Exit 0: every fixture asked for is made and confirmed. Exit 1: one was not, or the run was refused.
Exit 2: wrong arguments, or Word could not be driven.
"""
from __future__ import annotations

import argparse
import os
import stat
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import word_states  # noqa: E402  (scripts/lib, on the path above)
from office_com import Refused, installed_build, own_process, reference_build  # noqa: E402

NAME = "make-word-state-fixtures"
NO_ALERTS, DISCARD = 0, 0  # wdAlertsNone; wdDoNotSaveChanges


def remove(path):
    """Delete a fixture of an earlier run. A read-only one is made writable first; a missing one is no fault."""
    try:
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)
    except FileNotFoundError:
        pass


def mark_from_internet(path, zone):
    """Give the file the zone mark a download carries: its own Zone.Identifier stream."""
    with open(f"{path}:Zone.Identifier", "w", encoding="ascii", newline="") as stream:
        stream.write(f"[ZoneTransfer]\r\nZoneId={int(zone)}\r\n")


def make(app, state, path, made, mark=mark_from_internet):
    """Make the state's fixture at `path`: a new document of the script's own, saved, brought into its state and
    closed. While a document or a window of the script's is open, the call that closes it stands in `made`, so
    whatever a failure leaves open can be closed and the instance is known to hold nothing else."""
    doc = app.Documents.Add()

    def close():
        doc.Close(SaveChanges=DISCARD)
    made.append(close)
    try:
        doc.Content.InsertAfter(word_states.TEXT)
        doc.SaveAs2(str(path), FileFormat=state["format"], AddToRecentFiles=False)
        for name, value in state["set"]:
            setattr(doc, name, value)
        if state["set"] and not doc.Saved:  # marking as final saves by itself; the other properties do not
            doc.Save()
    finally:
        close()
        made.remove(close)
    if state.get("attribute") == "read-only":
        os.chmod(path, stat.S_IREAD)
    if state.get("zone") is not None:
        mark(path, state["zone"])


def confirm(app, state, path, made):
    """What Word says of the fixture, opened as its state is opened, that is not what the state needs (a list of
    lines, empty when it is confirmed). The fixture is closed again without saving."""
    before = int(app.Documents.Count)
    if state["view"] == "protected":
        if int(app.ProtectedViewWindows.Count):
            return ["a Protected View window was open before the fixture was"]
        window = app.ProtectedViewWindows.Open(str(path), AddToRecentFiles=False)

        def close_window():
            window.Close()
        made.append(close_window)
        try:
            wrong = []
            if int(app.Documents.Count) != before:
                wrong.append("it opened among the documents, not in Protected View")
            if int(app.ProtectedViewWindows.Count) != 1:
                wrong.append(f"{int(app.ProtectedViewWindows.Count)} Protected View windows are open, not one")
            return wrong
        finally:
            close_window()
            made.remove(close_window)
    doc = app.Documents.Open(str(path), AddToRecentFiles=False, ConfirmConversions=False)

    def close():
        doc.Close(SaveChanges=DISCARD)
    made.append(close)
    try:
        wrong = word_states.unconfirmed(state, lambda name: getattr(doc, name))
        if int(app.Documents.Count) != before + 1:
            wrong.append(f"the instance holds {int(app.Documents.Count)} documents with it open, not {before + 1}")
        return wrong
    finally:
        close()
        made.remove(close)


def run(states, root=None, dispatch=None, owner=own_process, wait=60.0, mark=mark_from_internet, say=print):
    """Make and confirm each state's fixture, under the scratch folder `root`, in a hidden Word of our own. Returns
    the names of the states that were not made or not confirmed. Raises Refused when the instance cannot be left
    as it must be."""
    if dispatch is None:
        import win32com.client
        dispatch = win32com.client.DispatchEx
    word_states.folder(root).mkdir(parents=True, exist_ok=True)
    app = dispatch("Word.Application")
    proc, failed, made, foreign, failure, gone = None, [], [], None, None, False
    try:  # from here on the instance is ours to quit, whatever fails
        app.Visible = False
        app.DisplayAlerts = NO_ALERTS
        first = app.Documents.Add()  # the instance's first window, whose process is the one to watch

        def close_first():
            first.Close(SaveChanges=DISCARD)
        made.append(close_first)
        proc = owner(app)
        close_first()
        made.remove(close_first)
        for state in states:
            path = word_states.inside(word_states.fixture(state, root), root)
            remove(path)
            try:
                make(app, state, path, made, mark)
                wrong = confirm(app, state, path, made)
            except Refused:
                raise
            except Exception as exc:  # COM raises its own error types: the state was not made
                wrong = [f"Word could not make it ({type(exc).__name__}: {exc})"]
            if wrong:
                remove(path)
                failed.append(state["name"])
                say(f"{NAME}: {state['name']} is not a fixture of its state and was deleted: " + "; ".join(wrong),
                    file=sys.stderr)
            else:
                say(f"{state['name']}: {path}")
    except Exception as exc:  # kept until the instance is seen to: what is left running is said first
        failure = exc
    finally:
        try:
            for close in list(made):  # what a failure left open: the script's own, and nothing else
                try:
                    close()
                except Exception:
                    pass  # counted just below: an instance that still holds anything is not quit
            try:
                foreign = int(app.Documents.Count) + int(app.ProtectedViewWindows.Count)
            except Exception:
                foreign = None  # unknown is not none: an instance whose contents are unknown is not quit
        finally:
            try:
                if foreign == 0:
                    app.Quit(SaveChanges=DISCARD)
            finally:
                try:
                    gone = foreign == 0 and proc is not None and proc.exited(wait)
                finally:
                    if proc is not None:
                        proc.close()
    after = f" (after {type(failure).__name__}: {failure})" if failure is not None else ""
    if foreign != 0:
        raise Refused((f"the Word instance the script started still holds {foreign} document(s) or Protected View "
                       "window(s) it could not close or did not make" if foreign
                       else "the script could not see what its Word instance still holds")
                      + f"; it is left running and is not quit{after}")
    if failure is not None:
        raise failure
    if proc is None:
        raise Refused("the Word instance's process was never identified, so its exit cannot be confirmed")
    if not gone:
        raise Refused(f"the Word instance the script started (pid {proc.pid}) did not exit")
    return failed


def main(argv=None, runner=run, build=reference_build, installed=installed_build, root=None):
    parser = argparse.ArgumentParser(prog=NAME, description=__doc__.split("\n\n")[0])
    parser.add_argument("--state", action="append", choices=word_states.NAMES,
                        help="a state to make (default: every state)")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    wanted = [s for s in word_states.STATES if not args.state or s["name"] in args.state]
    try:
        expected = build()
    except (OSError, ValueError, Refused) as exc:
        print(f"{NAME}: no reference build ({exc})", file=sys.stderr)
        return 1
    if installed() != expected:  # asked before Word is started: a fixture is of the reference build
        print(f"{NAME}: the installed build {installed()} is not the reference {expected}; record a new reference "
              "first", file=sys.stderr)
        return 1
    try:
        failed = runner(wanted, root)
    except (Refused, word_states.Invalid) as exc:
        print(f"{NAME}: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # COM raises its own error types; any of them means Word did not run for us
        print(f"{NAME}: Word could not be driven ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2
    if failed:
        print(f"{NAME}: {len(failed)} of {len(wanted)} fixtures were not made: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"{len(wanted)} fixtures made and confirmed in {word_states.folder(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
