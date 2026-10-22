# Audit findings: D02 T01 §1 Inventory Schema and Checker

Audit stance under the current review process (D02 T01 §23). Candidate: the stamped implementation `602f9dd` and every later change to the files it owns, up to `179ec01`: `scripts/check-inventory.py`, `scripts/tests/test_check_inventory.py`, `design/inventory/schema.json`.

## Checkpoint at the current tip

```text
python -m unittest discover -s scripts/tests -p "test_check_inventory.py"   -> Ran 37 tests ... OK
python scripts/check-inventory.py                                          -> exit 0
```

The section's checkpoint (at least 6 tests and OK) passes; no regression at the tip.

## Self-review

- The three round-3 fixes made after the old cap (huge exponent exits 2; isolated-constraint diagnostics; ambiguous duplicate ids) are present with their tests at the tip.
- Later changes to the owned files came from §3, §19, §20 and §21 and the SPDX headers; each was reviewed in its own section. This audit reviews the checker as it stands.

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-10-22T08:23:20Z
- Effort: medium
- Lines: 30
- Digest: 8eab2460ab5e2f0d

## source-defect: needs-attention

1. **P1: Cyclic containment passes.** `scripts/check-inventory.py:263` checks parent existence and ambiguity, but never cycles. Reproduce with `{"id":"word.home","app":"word","kind":"tab","label":"Home","parent":"word.home"}`. `check()` returns `[]`. Two records naming each other as parent also pass. These cannot represent the containing-record relationship.

2. **P1: A blank shortcut passes.** `design/inventory/schema.json:141` requires length, but not meaningful content. Reproduce with `{"id":"word.shortcut","app":"word","kind":"shortcut","label":"Example","shortcut":" "}`. `check()` returns `[]`, although no key chord is recorded.

3. **P1: Web addresses bypass the no-link rule.** `design/inventory/schema.json:334` and `scripts/check-inventory.py:34` recognize only HTTP(S) prefixes and `www.`. Set a valid record’s label to `support.microsoft.com/en-us/office`. Both schema validation and `check()` return no problems despite the explicit prohibition on web addresses.

## adversarial: needs-attention

4. **P1: Duplicate JSON members silently erase forbidden content.** `scripts/check-inventory.py:148` uses the decoder’s last-value-wins behavior. Reproduce with `[{"id":"word.home","app":"word","kind":"tab","label":"https://example.com","label":"Home"}]`. Loading followed by checking returns `[]`; the stored link disappears before validation. Reject duplicate members during decoding.

5. **P2: Malformed Outlook window cells crash validation.** `scripts/check-inventory.py:235` inserts window values into a set before validating their types; line 192 also performs unsafe set membership. Replace the first Outlook baseline row’s window cell with `{}`. Whole-inventory `main([])` raises uncaught `TypeError`; checking that baseline individually also crashes. Validate cell types before using them as set elements.

## consistency: needs-attention

6. **P1: Capture provenance need not match the reference.** `design/inventory/schema.json:205` accepts any nonempty profile, while line 270 accepts any nonempty `capturedFrom`; the checker never resolves either against `REFERENCE.md`. Reproductions that return `[]`:
   - A valid record with bounds and `captureProfile:"does-not-exist"`.
   - A control with `source:"uia:1.2.3.4"` and `capturedFrom:"not-a-build"`.

   `REFERENCE.md` requires the named capture profile and a recorded reference build. These accepted records provide neither trustworthy geometry provenance nor build provenance.

## record: needs-attention

7. **P3: The ticked every-rule test claim remains unsupported.** `todo/02-interface/TODO-01-parity-inventory.md:89` claims tests fail when any rule is disabled. `scripts/tests/test_check_inventory.py:246` tests ambiguous parents only; the shortcut tests at line 206 use unique targets. Removing the ambiguous-target branch at `scripts/check-inventory.py:272` is not exercised by any supplied fixture. Add an isolated duplicate-target test before retaining that claim.

Malformed-input results above were reproduced using in-memory fixtures without modifying files.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 1

All seven findings verified against the checker at the tip and fixed at their owning layer in the next commit. Each fix has a regression test; six of the tests fail against the stamped checker and schema (run with the fixes stashed), and the seventh fails when the branch it covers is removed:

1. P1 a parent chain that loops passed: the checker follows each record's parent chain through ids defined once and reports `parent chain loops: a -> ... -> a` (`test_a_record_cannot_contain_itself`, self and two-record loops).
2. P1 a blank shortcut passed: the schema's `shortcut` now needs a non-space character (`pattern: \S`), as `label` already did (`test_a_blank_shortcut_is_refused`, spaces and non-breaking spaces).
3. P1 web addresses without `http` passed: the schema's `noLink` rule now refuses a URL with any scheme, `mailto:`, `www.`, a dotted host followed by a path, and a name ending in `.com`, `.org`, `.net`, `.gov` or `.edu`. The checker's whole-record scan uses that same schema pattern instead of a second copy, so the two cannot drift. Endings that are also inventory words (`app`, `dev`, `io`, `info`) are left out, since `word.command.app-restore` and Backstage's Info page use them; the first broader draft flagged six real Word ids and was narrowed (`test_web_addresses_without_http_are_refused`, with the real words kept valid).
4. P1 a repeated member erased its first value: the loader refuses a repeated member in any object as unreadable, exit 2 (`test_a_repeated_member_is_unreadable`).
5. P2 a non-string Outlook window cell crashed: window cells are type-checked before any set lookup, in the row check and in the whole-inventory window gate (`test_a_malformed_outlook_window_cell_is_a_problem_not_a_crash`).
6. P1 provenance was not resolved: `captureProfile` must be a profile and `capturedFrom` a build that `design/inventory/REFERENCE.md` records, and a source stamped with a build must match `capturedFrom` (`test_capture_provenance_must_be_recorded_in_the_reference`).
7. P3 the ambiguous-target branch had no test: `test_a_target_defined_twice_is_ambiguous`.

`python scripts/check-inventory.py` over the committed inventory still exits 0; the checker tests run 44 and pass.

## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-10-22T08:33:22Z
- Effort: medium
- Lines: 24
- Digest: 458c0d0f5a37ea38

## source-defect: needs-attention

1. **P1: Web addresses still bypass the no-link rule.** `design/inventory/schema.json:336` recognizes only selected domain endings unless a slash follows the host. Set an otherwise valid record’s `label` to `"support.microsoft.co.uk"`. Both schema validation and `check()` accept it. This remains a Microsoft web address prohibited by the governing contract; documenting a narrower pattern does not satisfy that contract.

## adversarial: needs-attention

2. **P2: Malformed Outlook rows crash before schema validation.** `scripts/check-inventory.py:282` iterates `rows` without checking its type. Replace the Outlook baseline’s `rows` with `null` and run the whole-inventory check. `main([])` raises uncaught `TypeError: 'NoneType' object is not iterable` instead of reporting the schema violation. The round-1 fix guards individual window cells but leaves their enclosing collection unchecked.

## consistency: needs-attention

3. **P1: Omitting `capturedFrom` bypasses build provenance validation.** `scripts/check-inventory.py:321` compares the source build only when `capturedFrom` is a string. This record returns `[]`:

   ```json
   {"id":"word.probe","app":"word","kind":"control","label":"Probe","controlType":"button","source":"uia:1.2.3.4"}
   ```

   `design/inventory/REFERENCE.md:18` requires every live capture to carry `capturedFrom` and requires its build to be recorded. Neither requirement is enforced here. Require `capturedFrom` for live-source records and validate the source build even when that field is absent.

## record: approve

All three reproductions were verified using in-memory fixtures without modifying files.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 2

All three findings verified and fixed in the next commit, each with a test that fails against the round 1 checker (fixes stashed):

1. P1 a host name with an uncommon ending (`support.microsoft.co.uk`) passed. A new schema rule, `noHost`, refuses any dotted name ending in a label of two or more letters. It applies to the fields a person reads (`label`, `keytip`, `shortcut`, `menuPath`, `behaviour`). Identifier fields keep `noLink` only, because ids such as `word.command.about` are dotted names too and cannot be told from host names by their letters (`test_a_host_name_in_text_is_refused`; "e.g." and "Version 16.0" stay valid).
2. P2 an Outlook baseline whose `rows` is not a list crashed the whole-inventory window gate: the gate now reads rows only when they are a list, and the envelope problem is reported by `check_baseline` (`test_malformed_outlook_rows_are_a_problem_not_a_crash`).
3. P1 a live capture could omit `capturedFrom`: the schema requires `capturedFrom` whenever `source` is stamped with a build, and the checker requires that build to be recorded in `design/inventory/REFERENCE.md` whether or not `capturedFrom` is present (`test_a_live_capture_records_a_recorded_build`). The `PASTE` test fixture, a live capture without `capturedFrom`, broke exactly this rule and now records its build.

The committed inventory still checks clean (exit 0); the checker tests run 47 and pass.

## Round 3: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-10-22T08:42:36Z
- Effort: medium
- Lines: 26
- Digest: 0af31f37aa7a8af3

### source-defect: needs-attention

1. **P1: Sentence-ending punctuation bypasses the host prohibition.** `design/inventory/schema.json:382` excludes a following dot from the permitted boundary. This record returns `[]` from `check()`:

   ```json
   {"id":"word.probe","app":"word","kind":"tab","label":"Visit support.microsoft.co.uk."}
   ```

   The same address without the final period is rejected. Ordinary punctuation therefore defeats the round-2 fix and allows prohibited Microsoft links.

### adversarial: approve

No additional findings beyond the bypasses reported under the other lenses.

### consistency: needs-attention

2. **P1: Python whitespace semantics allow blank text that the schema forbids.** `scripts/check-inventory.py:93` compiles schema patterns with Python `re` without translating ECMAScript whitespace semantics. U+FEFF is whitespace in ECMAScript but matches Python’s `\S`. Set an otherwise valid record’s `label`, `shortcut` or `behaviour` to `"\ufeff"`: each returns `[]`. A control with that behaviour also passes `--require-behaviour`, because the additional check at `scripts/check-inventory.py:340` uses Python `strip()`. Thus invisible whitespace satisfies the required meaningful text and behaviour checks.

### record: approve

No additional receipt or checklist finding.

Both findings were reproduced with in-memory fixtures without modifying files. The committed inventory check returned no problems.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 3

Both findings verified and fixed in the next commit, each with tests that fail against the round 2 checker (fixes stashed). This round was the last by GPT-6 Astra at medium; from round 4 the reviewer is GPT-6.1 Sol at xhigh, the owner's change of 2026-10-22.

1. P1 a host followed by a sentence's full stop passed. `noHost` now ends at anything but a name character or a dot that continues a name, so "Visit support.microsoft.co.uk." is refused (`test_a_host_name_ending_a_sentence_is_refused`).
2. P1 Python's whitespace stood in for the schema's. `ecma()` now translates `\s` and `\S` to ECMA-262's whitespace and line terminators, which includes U+FEFF and excludes U+001C to U+001F, and refuses `\S` inside a class. The behaviour gate strips that same set (`ECMA_SPACE`), so a label, chord or behaviour of U+FEFF is blank, while a sentence padded with it still counts (`test_ecma_whitespace_is_blank_text`, `test_ecma_translates_whitespace_classes`).

The committed inventory still checks clean; the checker tests run 50 and pass.

## Round 4: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T09:14:31Z
- Effort: xhigh
- Lines: 22
- Digest: d53dafb0162bb875

## source-defect: needs-attention

1. **P1: Leading punctuation still bypasses the host prohibition.** `design/inventory/schema.json:382` prevents matching a host immediately after a dot. This record passes `check()` and makes `main()` return `0`:

   ```json
   {"id":"word.review-probe","app":"word","kind":"tab","label":"Visit ...support.microsoft.co.uk"}
   ```

   The prohibited address survives simply by following an ellipsis.

## adversarial: needs-attention

2. **P2: Parsed nested input crashes the recursive link scan.** `scripts/check-inventory.py:160` recursively scans values even after schema validation rejects their field. Add `"extra"` to an otherwise valid record, containing `2000` nested arrays around `0`. On Python 3.14.4, `load()` accepts this JSON, but `main()` raises uncaught `RecursionError` instead of returning a validation failure. The exception occurs outside the loader’s recursion handler.

## consistency: approve

## record: needs-attention

3. **P3: The ticked every-rule test claim remains unsupported.** `todo/02-interface/TODO-01-parity-inventory.md:89` claims disabling any rule fails the tests. Removing only `uiaId.minLength` at `design/inventory/schema.json:263` leaves all **50 tests passing**, while permitting an empty UI Automation identifier. Verified through an in-memory schema mutation with every temporary fixture operation intercepted, without filesystem writes.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 4

Round 4 was the first by GPT-6.1 Sol at xhigh (about eight and a half minutes). All three findings verified and fixed in the next commit, each with a test that fails against the round 3 checker (fixes stashed):

1. P1 a host after an ellipsis passed: `noHost` no longer needs a particular character before the host; any dotted name ending in a label of two or more letters is a host wherever it starts (`test_a_host_after_an_ellipsis_is_refused`, after "...", "(" and "-").
2. P2 deep nesting in an unknown field crashed the link scan with `RecursionError`: `links()` now walks with an explicit stack in document order, so any depth the loader accepts is scanned (`test_deep_nesting_is_a_problem_not_a_crash`, 5000 levels, with a link found at the bottom).
3. P3 removing a field's empty-value rule failed no test: `test_every_text_and_reference_field_refuses_an_empty_value` lists thirteen fields in the test itself (label, parent, keytip, shortcut, target, menuPath, captureProfile, behaviour, idMso, uiaId, source, capturedFrom, id), each required to refuse "" on its own. It found a gap the review had not: `menuPath` accepted an empty string, and the schema now requires a non-blank value there too.

## Round 5: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T09:28:16Z
- Effort: xhigh
- Lines: 18
- Digest: 3d8c31a3fc6ba992

## source-defect: needs-attention

1. **P1:** `design/inventory/schema.json:384` misses internationalized hostnames. An otherwise valid tab with `label: "xn--e1afmkfd.xn--p1ai"` passes both schema validation and `check()` with `[]`. This is a valid punycode hostname, so the no-web-address rule remains bypassable.

## adversarial: needs-attention

2. **P2:** `scripts/check-inventory.py:290` loads the source manifest without validating its structure; line 223 assumes an object containing iterable `blobs`. Supply `[1]` as `baseline-sources.json` and run the whole-inventory check: `main([])` raises uncaught `AttributeError`. Supplying the recorded commit with `"blobs": null` raises uncaught `TypeError`. Neither produces the documented controlled failure.

## consistency: needs-attention

3. **P1:** `design/inventory/schema.json:368` promises to prohibit URLs with any scheme, but the pattern at line 370 requires `://`, except for its special `mailto:` alternative. An otherwise valid tab with `label: "data:text/plain,hello"` passes schema validation and `check()`. This valid URL contradicts both the description and the no-links contract.

## record: needs-attention

4. **P3:** `scripts/tests/test_check_inventory.py:326` still does not support the every-rule claim ticked at `todo/02-interface/TODO-01-parity-inventory.md:89`. Remove only `menuPath.pattern` at `design/inventory/schema.json:192`: all **53 tests pass**, while `menuPath: " "` becomes valid. The new empty-value test is satisfied by `minLength` and never exercises whitespace-only menu paths. Verified through an in-memory schema mutation with fixture writes intercepted.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 5

All four findings verified. The link rule had been patched four rounds running, so it was re-thought rather than extended a fifth time. Every fix has a test that fails against the round 4 checker (fixes stashed):

1. P1 a punycode host and 3. P1 a `data:` URL passed. Instead of listing host and URL shapes, text a person reads (`label`, `keytip`, `shortcut`, `menuPath`, `behaviour`) now refuses the two marks every address has. One is a letter or digit joined to a letter by a dot: every host name has one, punycode included. The other is a word followed directly by a colon and a non-space character: every URI scheme has one (`data:`, `mailto:`, `javascript:`, `tel:`). No text in the committed inventory has either, checked before the change. The cost is that an abbreviation with inner dots, such as "e.g.", is refused in our own sentences; the schema says to write "for example". Identifier fields keep `noLink`, since ids are dotted and sources carry a colon (`test_any_address_in_text_is_refused`, four addresses in three fields, with "Zoom: sets 1.5 line spacing." still valid).
2. P2 a malformed source manifest crashed: the manifest must be an object with a commit string and a blobs object, else the run is unreadable, exit 2 (`test_a_malformed_manifest_is_unreadable_not_a_crash`, three malformed manifests).
4. P3 a field's whitespace rule could be removed unnoticed: `keytip`, `menuPath`, `idMso` and `uiaId` now need a visible character like the other text fields, and `test_every_text_and_reference_field_refuses_a_blank_value` requires each of thirteen fields, listed in the test, to refuse a value of spaces on its own.

## Round 6: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T09:40:53Z
- Effort: xhigh
- Lines: 22
- Digest: b1c6f596622ee9f6

## source-defect: needs-attention

1. **P1:** `design/inventory/schema.json:387` detects only ASCII hostname characters and literal dots. This record passes both schema validation and `check()`:

   ```json
   {"id":"word.probe","app":"word","kind":"tab","label":"support\u3002microsoft\u3002com"}
   ```

   IDNA normalization produces `support.microsoft.com`, so a prohibited Microsoft address passes. The Unicode hostname `пример.рф` also passes.

## adversarial: needs-attention

2. **P1:** `scripts/check-inventory.py:292` treats a manifest containing JSON `null` as an absent manifest. Reproduce by mocking `Path.read_text()` to return `"null"` for `baseline-sources.json`: whole-inventory `main([])` returns **0**, without diagnostics. The same override, with the Excel baseline omitted from discovery, still returns no problems. This bypasses manifest validation, baseline presence, commit matching and Outlook window checks.

## consistency: approve

## record: needs-attention

3. **P3:** `scripts/tests/test_check_inventory.py:163` leaves the every-rule sensitivity claim at `todo/02-interface/TODO-01-parity-inventory.md:89` unsupported. Remove only `bounds.properties.height.minimum` from the schema in memory: all **56 tests pass**, while an otherwise valid control with `height: -1` now validates successfully. Verified with all fixture writes intercepted in memory.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 6

All three findings verified and fixed in the next commit:

1. P1 Unicode host names passed. The text rule's name characters are now any letter or digit of any script (an ASCII letter or digit, or anything from U+00AA up), and its dots include the ideographic (U+3002), fullwidth (U+FF0E) and halfwidth (U+FF61) full stops that IDNA normalises to a dot. The scheme mark also takes the fullwidth colon (U+FF1A). The schema stores the pattern as ASCII escapes (`test_unicode_host_names_are_refused`: the reviewer's two cases plus fullwidth and halfwidth dots and a fullwidth-colon scheme; it fails against the round 5 rule).
2. P1 a manifest of JSON `null` passed for an absent one and skipped every baseline gate: a manifest file that exists is now always validated, so `null` is unreadable, exit 2 (`test_a_malformed_manifest_is_unreadable_not_a_crash` now includes `null`; it fails against the round 5 checker).
3. P3 a numeric minimum could be removed unnoticed: `test_every_numeric_minimum_holds` lists `order`, `bounds.width` and `bounds.height`, each required to refuse -1 on its own. Removing any one of the three minimums from the schema in memory fails it.
