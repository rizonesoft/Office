# Audit findings: D02 T01 §1 Inventory Schema and Checker

Audit stance under the current review process (D02 T01 §23). Candidate: the stamped implementation `602f9dd` and every later change to the files it owns, up to `179ec01`: `scripts/check-inventory.py`, `scripts/tests/test_check_inventory.py`, `design/inventory/schema.json`.

## Checkpoint at the audit's start

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

## Round 7: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T09:52:25Z
- Effort: xhigh
- Lines: 24
- Digest: 74717af1efc0244b

## source-defect: needs-attention

1. **P1:** `design/inventory/schema.json:387` still permits prohibited addresses. This record passes `check()` and makes `main()` return `0`:

   ```json
   {"id":"word.probe","app":"word","kind":"tab","label":"\ud801\udc28.com"}
   ```

   Its hostname normalizes through IDNA to `xn--hj8c.com`. The character ranges stop at U+FFFF, so supplementary-plane letters escape detection. Changing the label to `"8.8.8.8"` also passes because numeric addresses match neither address rule.

## adversarial: needs-attention

2. **P2:** `scripts/check-inventory.py:343` embeds untrusted Unicode directly in diagnostics, which `:387` prints without escaping. Add `"captureProfile":"\ud800"` to an otherwise valid tab record and invoke `main()` with UTF-8 stdout. It raises uncaught `UnicodeEncodeError` instead of returning validation exit code `1`. Reproduced against the current interpreter.

## consistency: needs-attention

3. **P2:** `design/inventory/schema.json:387` treats Unicode spaces and punctuation as hostname letters, contradicting its description at `:385`. Give an otherwise valid control `"behaviour":"Opens the dialog.\u2002"`. Validation reports `host name or address`: the trailing EN SPACE falls inside the broad character range. This rejects ordinary whitespace padding that the checker explicitly recognizes as whitespace.

## record: needs-attention

4. **P3:** `scripts/tests/test_check_inventory.py:171` tests missing `kind` but leaves other base requirements unprotected, contradicting the ticked every-rule claim at `todo/02-interface/TODO-01-parity-inventory.md:89`. Remove `app`, `id` or `label` individually from the schema’s record-level `required` array: all **58 tests still pass**, while a record missing that field becomes valid. Verified with schema mutations and fixture writes intercepted entirely in memory.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 7

All four findings verified and fixed in the next commit. Classifying characters as "letters" failed in both directions: supplementary-plane letters were missed, and an en space was taken for a letter. So the text rule was inverted rather than widened again.

1. P1 a supplementary-plane host and an IPv4 address passed. 3. P2 an en space after a sentence was refused. In readable text, a full stop (any of the four forms) may now be followed only by whitespace (ECMA's, through `ecma()`), another full stop, closing punctuation, the end of the text, or a digit when a digit precedes it (decimals such as Word's "1.5" line spacing). That refuses every host name in any script without naming letters. Four dotted numbers and the scheme colon stay refused. Checked first against every text value in the committed inventory: no hits, including "Ctrl+Shift+." and "Save As..." (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`; it fails against the round 6 rule).
2. P2 a lone surrogate in a record crashed the report: `main` sets both output streams to escape what they cannot encode, which also covers the Windows console's legacy code page (`test_unencodable_record_text_is_reported_not_a_crash`, printing to cp1252; it fails against the round 6 checker).
4. P3 a base field could leave `required` unnoticed: `test_every_base_field_is_required` lists `id`, `app`, `kind` and `label`; removing any one from the schema's `required` in memory fails it.

## Round 8: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T10:05:05Z
- Effort: xhigh
- Lines: 20
- Digest: cb6f602f20f81d86

### source-defect: needs-attention

1. **P1: IPv6 addresses bypass the address prohibition.** `design/inventory/schema.json:387` detects dots and letter-led URI schemes, but misses numeric IPv6 addresses. Give an otherwise valid tab `label: "[2001:4860:4860::8888]"` or `label: "::1"`. Schema validation and `check()` return `[]`; `main()` returns **0**.

### adversarial: needs-attention

2. **P1: A nested filename bypasses validation entirely.** `scripts/check-inventory.py:216` excludes every file named `baseline-sources.json`, although the manifest is loaded only from the inventory root. Reproduce with `design/inventory/word/baseline-sources.json` containing `[{"label":"https://example.com"}]`. The whole-inventory check never reads it and returns **0**, despite missing required fields and prohibited content. Verified through in-memory directory discovery and read overrides.

3. **P2: Unreadable-input diagnostics still crash on unencodable content.** `scripts/check-inventory.py:384` prints the exception before stream reconfiguration at line 388. Supply an otherwise valid JSON record containing duplicate keys `"\ud800":1,"\ud800":2`, then invoke `main()` with strict UTF-8 or CP1252 stderr. Duplicate detection raises `Unreadable`, but reporting it raises uncaught **`UnicodeEncodeError`** instead of returning **2**. The round-7 fix covers validation diagnostics only.

### consistency: needs-attention

4. **P1: Python digit semantics admit values the schema rejects.** `scripts/check-inventory.py:89` preserves `\d` unchanged, so the new pattern at `design/inventory/schema.json:387` uses Python Unicode digits instead of ECMAScript ASCII digits. Set a valid tab’s label to `"1.\u0665"` or `"1.\uff15"`. The checker returns `[]` and `main()` returns **0**; the schema’s ECMAScript pattern rejects both because the character after the dot is outside `[0-9]`.

### record: needs-attention

5. **P3: The every-rule test claim remains unsupported.** `scripts/tests/test_check_inventory.py:190` tests only missing `bounds.height`, leaving other required bounds members unprotected. Remove `"x"` from `bounds.required` in the schema **in memory**: all **61 tests still pass**, while bounds lacking `x` become accepted. This contradicts the ticked rule-disable requirement at `todo/02-interface/TODO-01-parity-inventory.md:89`. Verified with fixture writes intercepted in memory.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 8

All five findings verified and fixed in the next commit; four tests fail against the round 7 checker (fixes stashed), and the fifth fails when any bounds member leaves `required`:

1. P1 IPv6 addresses passed: three or more hexadecimal groups joined by colons, `::` included, are refused in readable text, while "Ratio 1:2" stays valid (`test_ipv6_addresses_in_text_are_refused`).
2. P1 any file named `baseline-sources.json` was skipped: only the manifest at the inventory's root is left out now, so a file of that name elsewhere is checked like any other (`test_a_file_named_like_the_manifest_elsewhere_is_checked`).
3. P2 unreadable-file diagnostics could still crash: the output streams take their escaping at the start of `main`, before any report (`test_unreadable_diagnostics_do_not_crash_on_unencodable_text`).
4. P1 `\d` matched any script's digits: patterns compile with `re.ASCII`, so `\d`, `\w` and `\b` mean what ECMA-262 means (ASCII), while `\s` and `\S` keep the explicit ECMA whitespace class (`test_patterns_use_ecma_ascii_digits`).
5. P3 `bounds` members could leave `required` unnoticed: `test_every_bounds_member_is_required` lists `x`, `y`, `width` and `height`.

## Round 9: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T10:17:44Z
- Effort: xhigh
- Lines: 18
- Digest: 93f3e0d98f88f0e5

### source-defect: needs-attention

1. **P1: Fabricated baseline provenance passes.** `scripts/check-inventory.py:351` validates live-source builds but never resolves record-level `baseline:` sources against the pinned baseline. Append an otherwise valid control with `source="baseline:" + "0"*40`. The whole-inventory check returns **0**, although this null revision cannot identify the baseline recorded in `design/inventory/REFERENCE.md:60`.

### adversarial: needs-attention

2. **P2: Rejected metadata reaches the terminal unescaped.** `scripts/check-inventory.py:347` interpolates `captureProfile` directly, and `:396` prints it. Set an otherwise valid record’s `captureProfile` to `"\u001b[2JFORGED"`. The checker returns **1**, but stdout contains the literal screen-clearing escape sequence. The encoding error handler does not escape representable control characters, so malformed input can corrupt displayed diagnostics.

### consistency: needs-attention

3. **P2: The IPv6 rule rejects ordinary time values.** `design/inventory/schema.json:387` treats any three colon-separated hexadecimal groups as an IPv6 address. An otherwise valid tab with `label:"12:30:45"` makes the whole-inventory check return **1**, reporting `host name or address`. This is ordinary time text and is not a valid IPv6 address. The description at `:385` repeats the same incorrect classification.

### record: needs-attention

4. **P3: The ticked every-rule test claim remains unsupported.** `scripts/tests/test_check_inventory.py:336` exercises address rejection for label, behaviour and menuPath, but leaves keytip’s independent address constraint unprotected. Remove only `{"$ref":"#/$defs/noHost"}` from `keytip.allOf` in memory: all **66 tests pass**, while `keytip:"data:text/plain,hello"` becomes accepted. This contradicts `todo/02-interface/TODO-01-parity-inventory.md:89`. Verified with all fixture writes intercepted in memory.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 9

Round 9 declared HIGHEST P1, so it cannot stop the loop on severity. All four findings verified and fixed in the next commit:

1. P1 a fabricated `baseline:` source passed: a record's `baseline:` source must now be a prefix of the commit the manifest pins (this inventory's manifest, or the repository's when it has none). The test fixtures that used an invented `baseline:4f1c2ab` now name the pinned commit (`test_a_baseline_source_names_the_pinned_baseline`, an all-zero and two near-miss commits refused).
2. P2 a record's control characters reached the terminal: every diagnostic is printed through `printable()`, which writes any non-printable character (ESC, bidi overrides, surrogates) as an escape (`test_diagnostics_escape_control_characters`).
3. P2 a time such as 12:30:45 was taken for IPv6: the rule now needs `::` between hexadecimal groups, or four or more groups (`test_a_time_is_not_an_ipv6_address`; IPv6 cases still refused).
4. P3 a text field's address rule could be removed unnoticed: `test_any_address_in_text_is_refused` now covers all five text fields; removing `noHost` from any one of them in memory fails it.

The three tests for findings 1 to 3 fail against the round 8 checker (fixes stashed).

## Round 10: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T10:35:00Z
- Effort: xhigh
- Lines: 20
- Digest: 503cebd0ea82a316

### source-defect: needs-attention

1. **P1: Network-path links bypass the address prohibition.** `design/inventory/schema.json:373` and `:387` miss authorities without dots or schemes. Append `{"id":"word.review-probe","app":"word","kind":"tab","label":"//localhost/help"}` to an inventory file. Schema validation returns `[]`; whole-inventory `main([])` returns **0**. This is a web reference resolving to `https://localhost/help` against an HTTPS base.

### adversarial: needs-attention

2. **P1: Invalid JSON constants pass through the source manifest.** `scripts/check-inventory.py:210` leaves Python’s permissive `parse_constant` behavior enabled. Add `"extra": NaN` to the otherwise unchanged root `baseline-sources.json`. The whole-inventory check returns `[]`, although `NaN` is not JSON. Reproduced with an in-memory read override.

3. **P2: Duplicate-member detection takes quadratic time.** `scripts/check-inventory.py:201` calls `keys.count(k)` for every key. Reproduce by decoding objects containing 4,000, 8,000 and 16,000 distinct `field{i}` members with `object_pairs_hook=ci.unique_pairs`. Measured decoding times were **0.152, 0.652 and 2.469 seconds**. Large malformed objects consume minutes before schema rejection; the loader needs linear duplicate detection.

### consistency: needs-attention

4. **P1: Malformed workbook blob IDs pass as trusted sources.** `scripts/check-inventory.py:304` validates only that `blobs` is an object. Replace `blobs["wordcontrols.xlsx"]` with `{}`, `null`, `123` or `"https://example.com"`, preserving everything else. Each whole-inventory run returns **0** without diagnostics. These values cannot be the Git blob IDs required by `design/inventory/REFERENCE.md:66`.

### record: needs-attention

5. **P3: The every-rule test claim remains unsupported.** `todo/02-interface/TODO-01-parity-inventory.md:89` claims disabling any rule fails the suite. Remove only the `noControl` reference from `uiaId.allOf` at `design/inventory/schema.json:274`: all **69 tests still pass**, while `uiaId:"\u0001"` becomes accepted. Verified using an in-memory schema mutation and virtual fixture I/O. The test at `scripts/tests/test_check_inventory.py:135` exercises control characters only in `label`.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 10

All five findings verified and fixed in the next commit; the four tests for findings 1 to 4 fail against the round 9 checker (fixes stashed), and the fifth fails when `noControl` is removed from any of the fields tried:

1. P1 a network-path link (`//localhost/help`) passed: `noLink` now also refuses `//` followed by a host, in every string field (`test_a_network_path_is_refused`; no string in the committed inventory holds `//`).
2. P1 `NaN` and `Infinity` were accepted: the loader refuses JSON's non-constants in every file it reads, the manifest included (`test_non_json_constants_are_unreadable`).
3. P2 repeated-member detection was quadratic: one pass with a set (`test_repeated_member_detection_is_linear`, 30000 members under 3 seconds).
4. P1 malformed blob ids passed: the manifest's commit must be a 40-hex Git id, and every blob a workbook name with a 40-hex blob id, or the manifest is unreadable (`test_manifest_blob_ids_are_git_ids`, five malformed values).
5. P3 a field's control-character rule could be removed unnoticed: `test_every_string_field_refuses_a_control_character` lists all thirteen string fields.

## Round 11: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T10:55:15Z
- Effort: xhigh
- Lines: 20
- Digest: 2733f485b14e4082

### source-defect: needs-attention

1. **P1: Incomplete or invented workbook provenance passes.** `scripts/check-inventory.py:318` validates entry syntax without checking which workbooks must exist. Remove `blobs["wordcontrols.xlsx"]` from the otherwise unchanged manifest, or rename it to `notepadcontrols.xlsx` while retaining its hash. Both whole-inventory runs return **0**, without diagnostics. This accepts missing or extra source workbooks despite `design/inventory/REFERENCE.md:66` requiring the manifest to identify every upstream workbook. Reproduced with in-memory read overrides.

### adversarial: needs-attention

2. **P2: Unreadable reference metadata crashes the CLI.** `scripts/check-inventory.py:175` reads `REFERENCE.md` outside the loader’s exception handling; `main()` catches only `Unreadable`. Override that read to raise `UnicodeDecodeError`, equivalent to invalid UTF-8 on disk, then call `main([])`. The exception escapes instead of producing the documented diagnostic and exit **2**. File-access errors escape through the same path.

3. **P2: Link detection remains quadratic.** `design/inventory/schema.json:373` contains unanchored, greedy alternatives that repeatedly scan long strings without finding a delimiter. Reproduce with `ci.ecma(schema["$defs"]["noLink"]["not"]["pattern"]).search("a" * n)`. For **4,000, 8,000 and 16,000** characters, single searches took **0.19, 0.76 and 3.67 seconds**. The checker repeats this scan during schema validation and whole-record scanning, with no string-length limit.

4. **P2: Parent-cycle detection scales cubically across a chain.** `scripts/check-inventory.py:185` searches the growing `chain` list on every step, and `:366` repeats traversal for every record. Build an acyclic parent chain and call `parent_loop()` for each ID. Chains of **300, 600 and 1,200** records took **0.058, 0.528 and 3.185 seconds** respectively. Hostile deep containment can stall validation even without a cycle.

### consistency: approve

### record: needs-attention

5. **P3: The ticked every-rule sensitivity claim remains unsupported.** `scripts/tests/test_check_inventory.py:163` does not exercise invalid coordinate types, despite `todo/02-interface/TODO-01-parity-inventory.md:89` claiming disabling any rule fails the suite. Remove only `bounds.properties.x.type` at `design/inventory/schema.json:207` in memory: all **74 tests pass**, while bounds containing `"x": "not pixels"` become accepted. Verified with fixture operations redirected into memory and no filesystem writes.

HIGHEST: P1  
OVERALL: needs-attention

## Dispositions after audit round 11

All five findings verified and fixed in the next commit; the four tests for findings 1 to 4 fail against the round 10 checker (fixes stashed), and the fifth fails when any bounds member's type is removed:

1. P1 a manifest missing a workbook or naming an invented one passed: the manifest must list exactly one workbook for each of Word, Excel, PowerPoint, Visio and Project, at least one Outlook window workbook, and nothing else, or it is unreadable. A dropped Outlook window is already caught, since the Outlook baseline's rows name windows the manifest must list (`test_the_manifest_lists_the_upstream_workbook_set`).
2. P2 an unreadable `REFERENCE.md` crashed the run: its read raises `Unreadable`, exit 2 (`test_an_unreadable_reference_exits_2`).
3. P2 the link patterns took quadratic time on long strings: lookbehind guards cannot make every alternative linear in ECMA-262, which has no possessive quantifiers. So every string field now has a `maxLength`, set from the real data (the longest committed value is 72 characters; a behaviour sentence may take 1000). The checker does not search a string's patterns once it is over its field's limit, nor any string over 1000 in the whole-record scan (`test_long_strings_cost_bounded_time`, 40000-character values in three fields).
4. P2 parent-loop detection was cubic on a long chain: `parent_loops()` walks each id once and keeps every answer, and a diagnostic names at most 20 ids before eliding the rest; small loops print exactly as before (`test_parent_loops_cost_linear_time`, a 20000-record chain and cycle).
5. P3 bounds member types could be removed unnoticed: `test_every_bounds_member_is_an_integer` lists `x`, `y`, `width` and `height`.

The round 5 address test now uses addresses short enough for a keytip (16 characters), so the address rule, not the new length rule, is what refuses them.

## Round 12: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T11:10:21Z
- Effort: xhigh
- Lines: 14
- Digest: f8808d7e9e6551a0

### source-defect: approve

### adversarial: needs-attention

1. **P2:** `scripts/check-inventory.py:402` rebuilds the set of all schema-error locations for every record, making malformed-file validation quadratic. Reproduce with an array of uniquely identified records containing valid `id`, `app` and `kind` fields but omitting `label`. In-memory checks of 2,000, 4,000 and 8,000 records took **0.89, 2.95 and 14.21 seconds** respectively. Large malformed captures stall before diagnostics appear. Compute `reported` once outside the record loop.

### consistency: approve

### record: needs-attention

2. **P3:** `scripts/tests/test_check_inventory.py:400` tests excessive lengths only for `label`, `behaviour` and `uiaId`, leaving the every-rule sensitivity claim at `todo/02-interface/TODO-01-parity-inventory.md:89` unsupported. Remove only `idMso.maxLength` at `design/inventory/schema.json:273` in memory: all **79 tests still pass**, while a 201-character `idMso` becomes accepted. Verified with fixture operations intercepted in memory and no filesystem writes.

HIGHEST: P2
OVERALL: needs-attention

## Dispositions after audit round 12

Round 12 is the first with no P1 (HIGHEST P2; source-defect and consistency approve). Both findings verified and fixed in the next commit:

1. P2 every record rebuilt the set of locations the schema had reported, so a large malformed file took quadratic time: the set is gathered once per file (`test_many_malformed_records_cost_linear_time`, 8000 records each missing a label; it fails against the round 11 checker).
2. P3 a field's length limit could be removed unnoticed: `test_every_string_field_has_its_length_limit` lists all thirteen string fields with their limits; removing the limit from any field tried in memory fails it.

## Round 13: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T11:22:56Z
- Effort: xhigh
- Lines: 22
- Digest: ac01f838108ff1ef

### source-defect: needs-attention

1. **[P1] IPv4 shorthand bypasses the address prohibition.** `design/inventory/schema.json:401` recognizes only four dotted numbers. This record passes schema validation and `check()`; `main()` returns **0**:

   ```json
   {"id":"word.probe","app":"word","kind":"tab","label":"Visit 127.0.1"}
   ```

   Windows `socket.inet_aton("127.0.1")` resolves it to `127.0.0.1`. A prohibited address therefore survives in readable text.

### adversarial: needs-attention

2. **[P2] Duplicate-ID diagnostics still grow quadratically.** `scripts/check-inventory.py:408` lists every other occurrence for every duplicate. Reproduce with arrays containing 200, 400 and 800 copies of `{"id":"word.home","app":"word","kind":"tab","label":"Home"}`. In-memory checks generated **2,663,600**, **10,687,200** and **42,814,400** diagnostic characters respectively. Small malformed inputs cause disproportionate memory use and terminal output. The round 12 performance test uses unique IDs and misses this path.

### consistency: approve

### record: needs-attention

3. **[P3] Fundamental type constraints remain unprotected by tests.** `scripts/tests/test_check_inventory.py:630` leaves the ticked rule-disable claim at `todo/02-interface/TODO-01-parity-inventory.md:89` unsupported. Remove either `schema["type"]` or `schema["$defs"]["record"]["type"]` in memory: **all 81 tests still pass**. The respective mutants accept `{}` or `[null]` as clean inventory files. Verified with fixture writes redirected entirely to memory.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 13

All three findings verified and fixed in the next commit; the first two tests fail against the round 12 checker (fixes stashed), and the third fails when either type rule is removed:

1. P1 IPv4 shorthand passed: three or more dotted numbers are refused in readable text, so `127.0.1` (127.0.0.1 to a resolver) and `10.1.1` are caught (`test_ipv4_shorthand_in_text_is_refused`). A limit, recorded: a two-part number such as `127.1` is also shorthand to a resolver, but it cannot be told from a decimal such as Word's "1.5" line spacing, so two-part numbers stay valid. The same holds for a bare integer. Neither is a link a reader could follow without knowing the convention.
2. P2 duplicate-id diagnostics grew quadratically: each names at most five other places and counts the rest ("and 794 more"), so 800 copies produce 800 bounded lines (`test_duplicate_id_diagnostics_are_bounded`).
3. P3 the file and record types could be removed unnoticed: `test_the_file_and_record_types_hold` refuses `{}`, `[null]`, `[1]` and a bare string.

## Round 14: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T11:38:12Z
- Effort: xhigh
- Lines: 22
- Digest: 60e1157c92ce66b4

## source-defect: needs-attention

1. **[P1] Noncanonical web links bypass rejection.** `design/inventory/schema.json:387` and `:401` accept this inventory array:

   ```json
   [{"id":"word.probe","app":"word","kind":"tab","label":"\\\\localhost\\help"}]
   ```

   Schema validation and `check()` return `[]`; the CLI returns **0**. Node’s URL parser resolves the label against an HTTPS base to `https://localhost/help`. Separately, `uiaId:"https:/localhost/help"` passes every check, while `new URL("https:/localhost/help").href` produces that same absolute URL. The no-link contract remains bypassable.

## adversarial: needs-attention

2. **[P2] Ambiguous-reference diagnostics still grow quadratically.** `scripts/check-inventory.py:438` prints every duplicate parent location for every referring record; `:444` does likewise for targets. Reproduce with N copies of one valid tab and N uniquely identified children naming it as parent. For N = **100, 200, 400**, checks produced approximately **670,790, 2,601,890, 10,243,890** diagnostic characters. Bounding duplicate-ID messages at `:409` leaves these paths unbounded.

## consistency: approve

## record: needs-attention

3. **[P3] Cycle-propagation coverage does not support the ticked rule-disable claim.** `scripts/tests/test_check_inventory.py:452` checks traversal timing without checking its result. Remove only the propagation branch at `scripts/check-inventory.py:215` through `:217` in memory: **all 84 tests still pass**, contradicting `todo/02-interface/TODO-01-parity-inventory.md:89`. The mutant then accepts a single named file whose child points into an existing two-record cycle defined in another inventory file. The current implementation correctly rejects that fixture. Verified with all fixture writes intercepted in memory.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 14

All three findings verified and fixed in the next commit; the first two tests fail against the round 13 checker (fixes stashed), and the third fails when the loop-propagation branch is removed:

1. P1 a backslash network path (`\localhost\help`) and a single-slash scheme (`https:/localhost/help`), which URL parsers still resolve, passed. `noLink`, which every string field carries, now refuses two slashes or backslashes followed by a host, and any scheme followed by a slash or backslash. Sources keep their colon, which no slash follows (`test_noncanonical_links_are_refused`, in a label, `uiaId` and `idMso`).
2. P2 ambiguous-parent and ambiguous-target diagnostics grew quadratically: they name at most five places and count the rest, like duplicate ids (`test_ambiguous_reference_diagnostics_are_bounded`, 400 copies and 400 children).
3. P3 loop propagation across walks was untested: `test_a_chain_into_a_loop_in_another_file_is_reported` names a file whose child leads into a two-record cycle in another file. The cycle's file sorts first, so the child's answer must come from the known loop. A first draft passed with the branch removed (the child sorted first and found the cycle itself), and the file order was fixed so the test fails without it.

## Round 15: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T11:54:06Z
- Effort: xhigh
- Lines: 27
- Digest: 6b93a826c3b7a888

## source-defect: needs-attention

1. **[P1] Schemes without slashes bypass link rejection.** `design/inventory/schema.json:387` accepts this array:

   ```json
   [{"id":"word.probe","app":"word","kind":"tab","label":"Probe","uiaId":"https:localhost"}]
   ```

   Schema validation and `check()` return `[]`; `main()` returns **0**. Node’s `new URL("https:localhost").href` returns `https://localhost/`. Identifier fields therefore still admit prohibited web addresses.

## adversarial: needs-attention

2. **[P2] Long property names cause quadratic diagnostic amplification.** `scripts/check-inventory.py:170` and `:172` copy the complete property path into every descendant; `:168` retains it in every link diagnostic. Add an unknown property whose name is `"x" * (10*n)` and value is `["//x"] * n` to an otherwise valid tab. For **n = 100, 200, 400**, full checks produced **109,764**, **419,564**, and **1,639,164** diagnostic characters from inputs of **1,783**, **3,483**, and **6,883** bytes. Schema rejection does not stop this traversal. Small malformed files can consume disproportionate memory before reporting failure.

## consistency: approve

## record: needs-attention

3. **[P3] The ticked every-rule sensitivity claim remains unsupported.** `todo/02-interface/TODO-01-parity-inventory.md:89` claims disabling any rule fails the suite. Two independent in-memory mutations each leave **all 87 tests passing**:

   - Remove boolean exclusion from integer validation at `scripts/check-inventory.py:60`. The mutant accepts an otherwise valid tab with `order: true`.
   - Remove the final, uncompressed IPv6 alternative at `design/inventory/schema.json:401`. The mutant accepts `label: "2001:4860:4860:0000:0000:0000:0000:8888"`.

   Both mutant records return `[]` from `check()`. Relevant coverage at `scripts/tests/test_check_inventory.py:157` and `:567` misses these cases. All fixture operations were redirected to memory.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 15

All three findings verified and fixed in the next commit; the first two tests fail against the round 14 checker (fixes stashed), and each of the two P3 tests fails when its rule is removed in memory:

1. P1 a scheme with no slashes (`https:localhost`, which URL parsers resolve) passed in an identifier field. Patching address shapes one at a time keeps losing, so the class is closed instead: a new `noColon` rule gives the identifier fields (`id`, `parent`, `target`, `captureProfile`, `capturedFrom`, `idMso`, `uiaId`) no colon at all, fullwidth included. Every address begins with a scheme and a colon. None of these fields holds a colon in the committed inventory, and `source` keeps its own anchored pattern, whose colon is part of the format (`test_identifier_fields_hold_no_colon`).
2. P2 long keys multiplied into every descendant's diagnostic: the whole-record scan keeps only each node's parent and its own label, truncates a key past 40 characters, and spells a path out only for a reported link, at most 20 per record, then counts the rest at its own location (`$[i].*`) so a schema problem at the record does not hide it (`test_long_keys_do_not_amplify_the_report`: a 4000-character key over 400 links now reports under 20000 characters).
3. P3 two rules could be removed unnoticed: `test_a_boolean_is_not_an_integer` (`order: true`) and `test_an_uncompressed_ipv6_address_is_refused` (the full eight-group form).

## Round 16: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T12:11:44Z
- Effort: xhigh
- Lines: 18
- Digest: 553f24b6498901ee

### source-defect: needs-attention

1. **[P1] Unicode whitespace conceals prohibited links.** `design/inventory/schema.json:422` permits U+FEFF after colons and dots, while `:408` misses the resulting address. Set a valid tab’s `label` to `"https:\ufeffsupport.\ufeffmicrosoft.\ufeffcom/en-us/office"`. Schema validation and `check()` return `[]`; the CLI exits **0**. Node’s `new URL(label).href` resolves it to `https://support.microsoft.com/en-us/office`.

### adversarial: needs-attention

2. **[P1] Checking an ancestor directory bypasses baseline completeness.** `scripts/check-inventory.py:402` enables completeness checks only when an argument resolves exactly to the inventory root. With `design/inventory/excel/baseline.json` absent, `python scripts/check-inventory.py design` exits **0**, although it scans the whole inventory. Checking `design/inventory` instead exits **1** with `missing baseline`. Reproduced using read-only discovery overrides. This violates `design/inventory/REFERENCE.md:66`.

### consistency: needs-attention

3. **[P3] Identifier documentation contradicts the new constraint.** `design/inventory/schema.json:420` says identifier fields carry “noLink only”, but they now also carry `noColon`. Reproduce with `uiaId:"https:localhost"`: `noLink` permits it, while the property rejects it specifically for its colon.

### record: needs-attention

4. **[P3] The every-rule test claim remains unsupported.** `scripts/tests/test_check_inventory.py:550` tests malformed blob IDs but leaves the commit-format guard unprotected. Remove only `or not hex40.fullmatch(sources["commit"])` at `scripts/check-inventory.py:387` in memory: **all 91 tests pass**. The mutant then accepts a valid tab checked individually against a manifest whose commit is `"not-a-git-id"`; the original raises `Unreadable`. This contradicts the ticked rule-disable claim at `todo/02-interface/TODO-01-parity-inventory.md:89`.

HIGHEST: P1  
OVERALL: needs-attention

## Dispositions after audit round 16

All four findings verified and fixed in the next commit; the tests for findings 1 and 2 fail against the round 15 checker (fixes stashed), and the test for finding 4 fails when the commit guard is removed:

1. P1 U+FEFF between an address's parts hid it, since URL and IDNA processing drop it: `noControl`, which every string field carries, now refuses C1 controls and Unicode's default-ignorable code points too (zero-width spaces and joiners, the byte order mark, the soft hyphen, bidi controls, variation selectors) (`test_invisible_characters_cannot_hide_an_address`). Two earlier tests used U+FEFF as valid padding or blank text; a sentence padded with U+3000, a real space, still counts. The test file's invisible literals, left by earlier edits, are now written as escapes.
2. P1 naming a folder above the inventory (`design`, the repository) skipped the whole-inventory gate: the gate runs when any named path is the inventory root or one of its ancestors (`test_naming_a_folder_above_the_inventory_runs_the_whole_inventory_gate`; `python scripts/check-inventory.py design` checks clean on the committed inventory).
3. P3 the `noHost` description still said identifier fields carry `noLink` only: it now names `noColon` too.
4. P3 the manifest commit guard was untested: `test_a_malformed_manifest_commit_is_unreadable`.

## Round 17: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T12:28:09Z
- Effort: xhigh
- Lines: 18
- Digest: e623367ed5f0ed9b

### source-defect: needs-attention

1. **[P1] Supplementary invisible characters bypass text validation.** `design/inventory/schema.json:415` omits supplementary default-ignorable characters, including U+E0100 (a variation selector). Set a valid tab’s `label` or shortcut’s `shortcut` to `chr(0xE0100)`: schema validation and `check()` return `[]`. A control’s `behaviour` containing only that character also passes `require_behaviour=True`. Invisible content therefore satisfies required readable text.

### adversarial: needs-attention

2. **[P1] Unreadable directories silently pass.** `scripts/check-inventory.py:297` uses `rglob()`, which suppresses directory traversal errors. On Python 3.14.4, intercept `os.scandir` to raise `PermissionError` only for `design/inventory/word`, delegating other calls normally. Both `main([])` and `main([str(INVENTORY / "word")])` return **0**, without diagnostics. All three Word JSON files escape validation. Discovery failures must produce an error rather than appear as empty directories.

### consistency: needs-attention

Finding **1** also contradicts `design/inventory/schema.json:413`: its description promises to reject Unicode default-ignorable code points, while its pattern covers only BMP ranges. The U+E0100 reproduction demonstrates the mismatch.

### record: needs-attention

3. **[P3] The every-rule test claim remains unsupported.** `todo/02-interface/TODO-01-parity-inventory.md:89` claims disabling any rule fails the suite. Remove only the empty-row rejection at `scripts/check-inventory.py:313-314` in memory: **all 94 tests still pass**. Clone the committed Word baseline envelope and set `rows=[]`: the original reports `no rows`; the mutant returns `[]`. Verification redirected fixture mutations entirely into memory.

HIGHEST: P1  
OVERALL: needs-attention

## Dispositions after audit round 17

All three findings verified and fixed in the next commit; the first two tests fail against the round 16 checker (fixes stashed), and the third fails when the empty-row rule is removed:

1. P1 supplementary-plane invisible characters (U+E0100 and the like) passed, because `noControl`'s class covered the BMP only. A JSON Schema pattern without the `u` flag sees a character outside the BMP as two surrogate code units, so `noControl` now refuses any surrogate code unit. That means any character outside the BMP, emoji included; no Office text needs one. The checker searches every pattern over the UTF-16 view of the string (`utf16()`), so it agrees with an ECMA validator (`test_characters_outside_the_bmp_are_refused`).
2. P1 a folder that could not be listed passed as empty, since `rglob` swallows the error: discovery walks with `os.walk`, whose error hook raises `Unreadable`, exit 2 (`test_an_unreadable_folder_is_unreadable_not_empty`).
3. P3 the empty-row rule was untested: `test_a_baseline_with_no_rows_is_refused`.

## Round 18: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T12:46:31Z
- Effort: xhigh
- Lines: 20
- Digest: 7ba8a21c313ab643

## source-defect: needs-attention

1. **[P1] Invisible annotation controls satisfy required readable text.** `design/inventory/schema.json:415` omits U+FFF9, U+FFFA and U+FFFB. Set an otherwise valid control’s `label` and `behaviour` to `"\ufff9"`. Schema validation and `check(..., require_behaviour=True)` return `[]`; the CLI returns **0**. The other two characters also pass. Formatting controls alone therefore count as a label and behaviour sentence.

## adversarial: needs-attention

2. **[P1] Directory metadata errors still silently bypass validation.** `scripts/check-inventory.py:319` relies on `os.walk`’s error callback, but `os.walk` suppresses errors from `DirEntry.is_dir()`. Reproduce by wrapping `os.scandir` entries so only `is_dir()` for `design/inventory/word` raises `PermissionError`, delegating everything else normally. Discovery omits all Word JSON files, and `main([])` returns **0** without diagnostics. The round-17 regression test covers opening a directory, not classifying its entries.

## consistency: needs-attention

3. **[P1] The supplementary-character fix disagrees with Unicode-mode schema evaluation.** `design/inventory/schema.json:415` matches surrogate code units, while `scripts/check-inventory.py:141` manufactures those units with `utf16()`. JSON Schema 2020-12 recommends Unicode-mode regular expressions. In Node, `new RegExp(schema.$defs.noControl.not.pattern, "u").test(String.fromCodePoint(0xE0100))` returns **false**. A valid tab whose label is U+E0100 consequently satisfies every label constraint under that evaluation, while the checker rejects it. The schema’s claimed supplementary-character prohibition remains ineffective for Unicode-mode consumers. See [Draft 2020-12 §6.4](https://json-schema.org/draft/2020-12/json-schema-core#section-6.4).

## record: needs-attention

4. **[P3] The ticked rule-disable claim remains unsupported.** `todo/02-interface/TODO-01-parity-inventory.md:89` claims disabling any rule fails the suite. Disable only the baseline source comparison at `scripts/check-inventory.py:339`: **all 97 tests still pass**. Clone the committed Word baseline, set `source` to `"baseline:" + "0"*40`, and call `check_baseline` with the real manifest. The original reports a source mismatch; the mutant returns `[]`. Both suite runs used fixture I/O redirected entirely to memory.

5. **[P3] The quoted current checkpoint is stale.** `docs/reviews/02-interface/audit-d02-t01-s1.md:8` reports **37 tests** under “Checkpoint at the current tip”; the current suite runs **97**. The quoted evidence does not describe this candidate’s checkpoint.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 18

All five findings verified and fixed in the next commit; the first three tests fail against the round 17 checker (fixes stashed), and the fourth fails when the baseline source comparison is removed:

1. P1 the interlinear annotation controls (U+FFF9 to U+FFFB) passed as text. Rather than another hand-written list, `noControl`'s class is now generated from Unicode's own data: every BMP character classed Cc or Cf, plus the other default-ignorable code points. A test checks the class against this Python's Unicode data, so no format character can be left out (`test_every_format_character_is_refused`).
2. P1 `os.walk` skipped an entry whose kind could not be read: discovery now walks with `os.scandir` itself, and any error listing a folder or classifying an entry raises `Unreadable` (`test_an_unclassifiable_entry_is_unreadable`).
3. P1 a JSON Schema consumer in Unicode mode does not see the surrogate class match an astral character: `noControl` adds a negated class of the whole BMP, which matches any character outside it as a code point. Without the `u` flag the surrogate range still catches it as code units, so both modes refuse it (`test_astral_characters_are_refused_in_both_regex_modes`).
4. P3 the baseline envelope's source comparison was untested: `test_a_baseline_source_must_name_the_manifest_commit`.
5. P3 the quoted checkpoint described the start of the audit: it is now labelled so, and the current one follows.

## Checkpoint after round 18

```text
python -m unittest discover -s scripts/tests -p "test_check_inventory.py"   -> Ran 101 tests in 10.409s OK
python scripts/check-inventory.py                                          -> exit 0
```

## Round 19: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T13:04:24Z
- Effort: xhigh
- Lines: 18
- Digest: 29c368e9c40f2ff2

## source-defect: needs-attention

1. **[P1] Compatibility full stops bypass address rejection.** `design/inventory/schema.json:422` misses U+2024 and U+FE52. Set a valid tab’s `label` to `"support\u2024microsoft\u2024com"` or `"support\ufe52microsoft\ufe52com"`: schema validation returns `[]`, and the CLI exits **0**. Python’s `label.encode("idna")` produces `support.microsoft.com`; its standard HTTP client likewise generates `Host: support.microsoft.com`. Prohibited addresses therefore survive normalization.

## adversarial: needs-attention

2. **[P1] Directory symlinks silently hide inventory files.** `scripts/check-inventory.py:315` excludes directory symlinks through `follow_symlinks=False`, without rejecting them. If `word` is a directory symlink, its captures disappear from discovery, while baseline presence checks still follow the link. Reproduced through read-only metadata overrides modeling that symlink, with a malformed Word command file: `main([])` returns **0** without diagnostics; checking the file explicitly returns **1**.

## consistency: needs-attention

3. **[P1] Baseline provenance is checked against itself, without enforcing the recorded reference commit.** `scripts/check-inventory.py:435` trusts the manifest’s syntactically valid commit without comparing it with `design/inventory/REFERENCE.md:60`. Override the manifest commit to `"0"*40` and all six baseline envelope sources to `"baseline:" + "0"*40`, leaving `REFERENCE.md` unchanged: `main([])` returns **0**. Agreement among the modified files passes despite contradicting the pinned reference.

## record: needs-attention

4. **[P3] The ticked every-rule sensitivity claim remains unsupported.** `todo/02-interface/TODO-01-parity-inventory.md:89` requires tests to fail when any rule is disabled. Disable only the unknown-Outlook-window guard at `scripts/check-inventory.py:367`: **all 101 tests still pass**. Change the first committed Outlook baseline row’s window to `"inventedwindow"`: the original reports an invalid window; the mutant returns `[]`. Both checks used in-memory changes, with fixture writes redirected to memory.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 19

All four findings verified and fixed in the next commit; four tests fail against the round 18 checker (fixes stashed), and the fifth fails when the window guard is removed:

1. P1 compatibility full stops (U+2024, U+FE52) passed, though IDNA normalises them to a dot. The text rule's dot and colon classes are now generated from Unicode's compatibility mappings: every character whose NFKC form is a full stop or a colon, plus the ideographic and halfwidth full stops IDNA treats as separators. A test checks the classes against this Python's Unicode data (`test_compatibility_full_stops_and_colons_are_address_marks`). On the identifier side, `idMso` is now ASCII letters, digits and underscores (all 219 committed values are), and `uiaId` printable ASCII with single spaces, so no look-alike reaches either (`test_identifier_fields_are_ascii`).
2. P1 a directory symlink hid its files from discovery: the inventory holds only plain files and folders, so a symbolic link or Windows junction anywhere in it makes the run unreadable (`test_a_link_in_the_inventory_is_unreadable`).
3. P1 the manifest's commit was only checked against the baselines, not the reference: it must equal the commit `design/inventory/REFERENCE.md`'s Baseline table pins (`test_the_manifest_commit_is_the_reference_commit`).
4. P3 the unknown-Outlook-window guard was untested: `test_an_unknown_outlook_window_is_refused`.

CI on the round 19 fix commit failed: three `test_import_office_ids` tests build a scratch inventory with its own manifest at an invented commit and no `REFERENCE.md`. The checker borrowed the repository's reference and compared that inventory's commit with the repository's. The pinned commit now binds only an inventory's own `REFERENCE.md`; a scratch inventory without one still borrows the repository's profiles and builds. The round 19 commit test gives its inventory a copy of the reference. The full tooling suite (613 tests) now passes locally; it was not run before the failing push, and is run before every push from here on.

## Round 20: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T13:31:36Z
- Effort: xhigh
- Lines: 18
- Digest: c1485d3ef0eed432

## source-defect: needs-attention

1. **P1:** `design/inventory/schema.json:423` misses compatibility characters that normalize to text containing a dot. Append `{"id":"word.reviewprobe","app":"word","kind":"tab","label":"\u2488com"}` to an inventory array. Schema validation accepts it and the whole-inventory CLI exits **0**, although `label.encode("idna")` produces `b"1.com"`. The round-19 test checks only characters whose entire normalized form equals `"."`.

## adversarial: needs-attention

2. **P1:** `scripts/check-inventory.py:229` fails open when the reference commit row has different Markdown spacing. Change `| Commit | ` to `| Commit |  `, preserving its recorded hash. Set the manifest commit and all six baseline sources to `"0"*40`. The whole-inventory CLI exits **0**, without diagnostics. With the original spacing, the same contradictory sources exit **2**. Line 230 silently returns `None`, disabling the comparison at line 432.

## consistency: needs-attention

2. **P1:** The reproduction above leaves the commit recorded at `design/inventory/REFERENCE.md:60` semantically unchanged, yet permits a different baseline revision. The checker therefore does not reliably enforce agreement with its governing reference.

## record: needs-attention

3. **P3:** `scripts/tests/test_check_inventory.py:492` and the other baseline fixtures leave the exact-column-layout guard unprotected, contrary to the ticked rule-disable claim at `todo/02-interface/TODO-01-parity-inventory.md:89`. Disable only the comparison at `scripts/check-inventory.py:364`: **all 106 tests still pass**. Then replace the Word baseline’s `columns[0]` with `"tab"`: the original reports incorrect columns, while the mutant returns `[]`. Verified with fixture writes redirected entirely to memory.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 20

All three findings verified and fixed in the next commit; the first two tests fail against the round 19 checker (fixes stashed), and the third fails when the column guard is removed:

1. P1 a character whose compatibility form only contains a full stop (U+2488 is "1.", so "<U+2488>com" is 1.com to IDNA) passed. The dot and colon classes now take every character whose NFKC form contains a full stop or a colon (31 dot forms and 5 colon forms in the BMP, the ellipsis U+2026 among them, which still ends a label validly since it is followed by nothing). A test checks the class against this Python's Unicode data (`test_characters_containing_a_full_stop_are_address_marks`).
2. P1 extra spaces in the reference's Commit row switched the commit comparison off: the row is read in any spacing, and an inventory's own reference that does not pin exactly one commit makes the run unreadable instead of skipping the comparison (`test_the_reference_commit_row_is_read_in_any_spacing_and_required`).
3. P3 the column-layout guard was untested: `test_a_baseline_with_the_wrong_columns_is_refused`.

The full tooling suite (616 tests) passes locally before the push.

## Round 21: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T13:53:50Z
- Effort: xhigh
- Lines: 26
- Digest: 63b337f183c6fb43

## source-defect: needs-attention

1. **P1: Compatibility expansions still conceal hostnames.** `design/inventory/schema.json:423` treats each compatibility character as one dot, missing letters and dots inside its expansion. Append this record to an inventory array:

   ```json
   {"id":"word.round21probe","app":"word","kind":"tab","label":"\u33c2\u33c7"}
   ```

   Schema validation returns `[]`; the whole-inventory CLI exits **0** without diagnostics. NFKC produces `a.m.Co.`, and Python IDNA produces `a.m.co.`. Without connecting, `HTTPConnection(label).putrequest("GET", "/")` prepares `Host: a.m.co.`. The normalized label is correctly rejected, demonstrating that the raw spelling bypasses the prohibition.

## adversarial: needs-attention

Finding **1** permits an address through ordinary escaped JSON, without malformed syntax or unknown fields.

## consistency: needs-attention

Finding **1** contradicts `design/inventory/schema.json:421`, which promises to refuse every hostname and abbreviations containing inner dots. The pattern checks neighboring raw characters while ignoring content inside their compatibility expansions.

## record: needs-attention

2. **P3: The ticked rule-disable claim remains unsupported.** `scripts/tests/test_check_inventory.py:223` does not independently exercise the dotted-host/path alternative, contrary to `todo/02-interface/TODO-01-parity-inventory.md:89`.

   Remove only `[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+/|` from `$defs.noLink.not.pattern` in memory: **all 109 tests still pass**, while an otherwise valid record with `uiaId:"microsoft.de/help"` becomes accepted. The original rejects it with `.uiaId: link`. Both suite runs intercepted fixture writes entirely in memory.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 21

Both findings verified and fixed in the next commit; the first test fails against the round 20 schema (fix stashed), and the second fails when the host-and-path alternative is removed:

1. P1 compatibility characters whose expansion holds several characters (U+33C2 U+33C7 is a.m.Co. once normalised) could spell an address their raw neighbours do not show. In readable text, every compatibility character whose normalised form holds a full stop or a colon (33 in the BMP) is now refused outright. The plain full stop, the plain colon and the ellipsis U+2026 stay, under the dot and colon rules. A test checks the set against this Python's Unicode data and confirms that "Save As..." and "Save As" followed by U+2026 are still valid (`test_compatibility_expansions_cannot_spell_an_address`).
2. P3 noLink's dotted-host-with-path alternative was untested on its own: `test_a_dotted_host_with_a_path_is_a_link_in_identifier_fields` (`uiaId: microsoft.de/help`).

The full tooling suite (618 tests) passes locally before the push.

## Round 22: sol (`gpt-6.1-sol` via `codex`)

- Writer: claude
- Run: 2026-10-22T14:20:06Z
- Effort: xhigh
- Lines: 24
- Digest: b9a601a5ae5d5de2

### source-defect: needs-attention

1. **[P1] Hexadecimal IPv4 components bypass address rejection.** `design/inventory/schema.json:423` accepts a valid tab with `label:"127.0x0.1"`. Schema validation and `check()` return `[]`; the CLI returns **0**. On Windows, `socket.inet_ntoa(socket.inet_aton("127.0x0.1"))` returns `"127.0.0.1"`. This three-part address falls outside the documented two-part decimal exception.

### adversarial: needs-attention

2. **[P1] Filename casing bypasses baseline validation on Windows.** `scripts/check-inventory.py:475` selects the baseline schema using a case-sensitive filename comparison. Using in-memory content overrides, place this array in Word’s baseline:

   ```json
   [{"id":"word.round22probe","app":"word","kind":"tab","label":"Probe"}]
   ```

   Checking `design/inventory/word/baseline.json` returns **1**, reporting `expected object`. Checking the same file as `design/inventory/word/BASELINE.JSON` returns **0**. Modeling its directory entry as `BASELINE.JSON` also makes the whole-inventory check return **0**, bypassing baseline envelope, source, columns and row validation.

### consistency: needs-attention

1. **[P1, shared with source-defect]** `design/inventory/schema.json:421` promises rejection of three or more dotted numbers, including IPv4 shorthand. The `127.0x0.1` reproduction passes despite being a three-part IPv4 address. The pattern does not enforce its stated address prohibition.

### record: needs-attention

3. **[P3] The ticked every-rule sensitivity claim remains unsupported.** `todo/02-interface/TODO-01-parity-inventory.md:89` requires disabling any rule to fail the suite. Remove only the row-length guard at `scripts/check-inventory.py:373` in memory: **all 111 tests still pass**. Then remove the last cell from the first committed Word baseline row. The original reports `8 cells, expected 9`; the mutant returns `[]`. Both suite runs redirected fixture writes entirely to memory.

HIGHEST: P1
OVERALL: needs-attention

## Dispositions after audit round 22

Round 22 is the last the 22-round cap allows. All three findings were verified and fixed in the next commit, with regression tests: three fail against the round 21 checker (fixes stashed), and the fourth fails when the row-length guard is removed. No independent round reviews these fixes under this audit's cap; that review is owned by `D02 T01 §27` (below).

1. P1 a hexadecimal IPv4 component (`127.0x0.1`, `0x7f.1`) passed. A hexadecimal number beside a full stop is now refused (`test_a_hexadecimal_number_beside_a_full_stop_is_an_address`). The text rule had been patched in rounds 18 to 21 one look-alike family at a time, so it was re-thought rather than patched again: readable text now refuses every compatibility character whose normalised form holds a visible ASCII character (778 BMP characters, generated from Unicode's data: fullwidth letters and digits, circled and superscript numbers, ligatures, the round 20 and 21 characters among them). Only the ellipsis U+2026 stays, under the full stop rules. Characters with no compatibility form (accented letters, dashes) and those whose form is only a space (no-break space) are untouched. No committed inventory text holds any non-ASCII character, and a test checks the class against this Python's Unicode data (`test_compatibility_characters_with_an_ascii_form_are_refused_in_text`). Trade-off: a future label that needs a character such as the trade mark sign U+2122 (normalised TM) is refused and needs a deliberate exception.
2. P1 a baseline spelled `BASELINE.JSON` skipped the baseline checks on a case-insensitive file system: `is_baseline()` compares the case-folded name, used by both discovery and validation (`test_a_baseline_in_any_case_takes_the_baseline_checks`).
3. P3 the row-length guard was untested on its own: `test_a_baseline_row_of_the_wrong_length_is_refused`.

## Cap reached

Rounds spent: 22 (Astra 6 medium rounds 1 to 3, GPT-6.1 Sol xhigh rounds 4 to 22; no outage rounds). Every round found real defects, all fixed in their own commits with regression tests proven against the code before the fix. Leftovers:

- The round 22 fixes have no independent review round: owned by `D02 T01 §27`.
- The record lens found an untested guard in each of rounds 18 to 22, so the ticked claim that every rule's removal fails a test (`D02 T01 §1`) is proven rule by rule rather than systematically: `D02 T01 §27` runs a mutation sweep over every rule in `scripts/check-inventory.py` and every pattern in `design/inventory/schema.json`.

No leftover is a safety, data-integrity or stamp-invalidating defect: the checker refuses more than before at every round, the committed inventory passes it unchanged, and no finding was a regression of `D02 T01 §1`'s stamped behaviour, so the audit confirms its stamp.

## Checkpoint after round 22

```text
python -m unittest discover -s scripts/tests -p "test_check_inventory.py"   -> Ran 115 tests in 8.186s OK
python scripts/check-inventory.py                                          -> exit 0
python -m unittest discover -s scripts/tests                               -> Ran 622 tests, OK (skipped=2)
```

CI on the round 22 fix commit failed: CI pins Python 3.15 (Unicode 17.0), whose data adds U+A7F1, a compatibility character with an ASCII form that the class generated under the local Python 3.14 (Unicode 16.0) lacked. The class is now generated from the CI pin's Unicode 17.0 data (779 characters), its description names the version, and the checker tests pass under both 3.14 and 3.15. The full suite now runs under the CI pin before every push.
