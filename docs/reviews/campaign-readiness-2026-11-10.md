## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-10T00:39:42Z
- Effort: medium
- Type: adversarial
- Lines: 28
- Digest: 25a64726a9571333

### adversarial: needs-attention

1. **P2, `scripts/run-tests.py:97-104`: a test subprocess can leave descendants running after the runner reports completion.** Cleanup runs only on timeout or cancellation. Reproduce with a test that starts a sleeping subprocess and then raises an assertion before cleanup: unittest exits unsuccessfully, the runner removes it from `self.live`, and the descendant survives. Even calling `stop_tree` afterwards would return immediately once the parent has exited (`:50-51`). This is an ordinary failed-cleanup scenario during testing, and contradicts the explicit “No child outlives this process” contract. Track and contain descendants independently of the test process’s lifetime, and test parent-exits-first cleanup.

### consistency: needs-attention

2. **P2, `scripts/run-tests.py:81`: the runner drops the mutation workflow’s bytecode protection.** `.claude/agents/mutation-tester.md` explicitly permits `python -B` to prevent stale bytecode from hiding mutations. Running `python -B scripts/run-tests.py` does not propagate `-B` to the unittest subprocesses. The baseline therefore creates caches; a same-size mutation within the cache timestamp’s resolution can execute the baseline bytecode instead of the mutated source. Reproduce by running the baseline through this runner, making a same-size mutation within the same timestamp interval, and rerunning it with `-B`. Propagate the interpreter’s bytecode setting to children and cover this case.

### integration: needs-attention

3. **P2, `.github/workflows/ci.yml:46`: the replacement full-suite gate lacks an integrated run in the supplied evidence.** The evidence lists individual test-file runs, but never the complete suite through the new parallel runner. Passing each file alone does not establish concurrent independence: separate processes still share filesystem paths, external tools and machine resources. This changes the execution contract for every existing test file. Run the complete replacement command on the intended host and CI, inspect failures and skips, and reconcile its test count with serial discovery before replacing the gate.

### source-defect: advisory

The governing campaign-scope decisions are referenced but their contents are not supplied. The diff alone cannot establish that the new outward-action permissions and takeover instructions accurately reproduce those decisions.

### design: approve

### excellence: advisory

`scripts/run-tests.py:10-13` claims runtime falls to approximately the slowest file, but supplies no parallel-suite measurement. With at most four workers, total work divided by four is also a lower bound. Record the actual full-suite timing before making that performance claim.

### record: needs-attention

Finding 3 also applies here: the supplied isolated runs and five mutation results do not establish that the replacement full-suite gate works end to end.

HIGHEST: P2
OVERALL: needs-attention

### Outcome (round 1)

1. Real, fixed: `scripts/run-tests.py` runs each file in a job object closed when the file ends (its process group is signalled elsewhere), so a child a test left running ends with its file whether the file passed or failed; `test_a_child_left_by_a_file_that_ended_is_stopped` covers both.
2. Real, fixed: `-B` is passed on to every file when the runner itself runs without bytecode; `test_no_bytecode_is_passed_on_to_every_file` covers it.
3. Real, closed by evidence: the complete suite was run through the runner on this PC and its count reconciled with the serial run (recorded below with the timings), and the CI run of the commit is the integrated proof on the runner image.
4. Advisory (source-defect): the outward actions and the takeover wording restate decisions 2 and 4 of `docs/specs/2026-10-23-campaign-scope-design.md`, which the prompt named but did not inline.
5. Advisory (excellence): the docstring's claim is replaced by the measured figures below.

Measured 2026-11-10 on this PC: `python -m unittest discover -s scripts/tests` ran 946 tests in 394.6 s (OK, 2 skipped) before the change; `bosun run -- python scripts/run-tests.py` ran 958 tests in 22 files in 176.2 s, four at a time, OK with the same 2 skipped (946 plus the 9 of `test_run_tests.py` and the 3 of `test_no_hardcoded_paths.py`), while another job was running. A mutation run killed `-B` not passed on and the file order; leftover cleanup removed survived the first version of its test, because closing the runner ends every job anyway, so `test_a_left_child_ends_with_its_file_not_with_the_run` was added and fails against that mutation (`test_watch.py` FAIL after 30 s).
