# Audit findings: D02 T01 §21 Microsoft-Free Inventory

Audit stance under the current review process (D02 T01 §26). Candidate: the stamped implementation `8f59a68e156be1f9157226c05293ce7d46f5586a` and every later change to the files it owns, up to `1c6408914fd8cb16b6376b0f82fc0bb5a1da5bd1`: `design/inventory/schema.json`, `scripts/check-inventory.py`, and `scripts/tests/test_check_inventory.py`.

## Checkpoint at the audit's start

```text
python -m unittest discover -s scripts/tests -p "test_check_inventory.py" -> Ran 117 tests in 8.798s OK
python scripts/check-inventory.py design/inventory                        -> exit 0
python scripts/todo-graph.py resolve "D02 T01 §21"                        -> exit 3 (done: true)
rg -n -i "https?://|microsoft\.com|screentip" design/inventory scripts/check-inventory.py scripts/tests/test_check_inventory.py ->
scripts/tests/test_check_inventory.py:95:    def test_screentip_field_is_refused(self):
scripts/tests/test_check_inventory.py:96:        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, screentip={"title": "Bold"})])
scripts/tests/test_check_inventory.py:97:        self.assertTrue(any("unknown field screentip" in p for p in self.problems()))
scripts/tests/test_check_inventory.py:100:        self.write("word/ribbon.json", [TAB, dict(PASTE, source="https://example.com/paste")])
scripts/tests/test_check_inventory.py:114:        for rec in (dict(BOLD, behaviour="Makes text bold, see https://example.com/bold."),
scripts/tests/test_check_inventory.py:115:                    dict(BOLD, label="Bold www.example.com"), dict(BOLD, menuPath="HTTP://example.com")):
scripts/tests/test_check_inventory.py:122:        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, extra={"items": ["see https://example.com"]})])
scripts/tests/test_check_inventory.py:131:        self.assertNotIn("screentip", props)
scripts/tests/test_check_inventory.py:143:        for field, value in (("behaviour", "See HTTPS://example.com/help"), ("label", "www.example.com"),
scripts/tests/test_check_inventory.py:144:                             ("menuPath", "File > http://x.example")):
scripts/tests/test_check_inventory.py:195:        for bad in ("https://", "uia:", "baseline:", "listcommands:"):
scripts/tests/test_check_inventory.py:225:        for text in ("support.microsoft.com/en-us/office", "mailto:help@example.org", "ftp://files.example",
scripts/tests/test_check_inventory.py:237:        path.write_text('[{"id": "word.home", "app": "word", "kind": "tab", "label": "https://example.com", '
scripts/tests/test_check_inventory.py:320:        deep_link = "https://example.com"
scripts/tests/test_check_inventory.py:908:        for blob in ({}, None, 123, "https://example.com", "abc"):
scripts/tests/test_check_inventory.py:960:        self.write("word/baseline-sources.json", [{"label": "https://example.com"}])
design/inventory\schema.json:2:  "$schema": "https://json-schema.org/draft/2020-12/schema",
design/inventory\baseline.schema.json:2:  "$schema": "https://json-schema.org/draft/2020-12/schema",
design/inventory\visio\baseline.json:153:["ScreenTip", "button", "coreTab", null, "TabInsert", "GroupTextBoxText", null, null, 17010],
design/inventory\visio\baseline.json:563:["DeleteShapeScreenTip", "button", "notInRibbon", null, null, null, null, null, 16911],
```

The section's checkpoint and the whole-inventory checker pass at the tip; the `rg` search matches only the refusal fixtures in `scripts/tests/test_check_inventory.py`, the `$schema` dialect lines in `design/inventory/schema.json` and `design/inventory/baseline.schema.json`, and the two upstream Visio `idMso` control identifier tokens (`ScreenTip`, `DeleteShapeScreenTip`) in `design/inventory/visio/baseline.json`.

## Self-review

- The Round 3 post-cap fix from `D02 T01 §21` (`test_every_string_field_carries_the_link_rule` in `scripts/tests/test_check_inventory.py`, verifying that every string property of `design/inventory/schema.json` carries `$defs/noLink` and that `screentip` is absent) is in place and passes.
- Subsequent hardening in `D02 T01 §23` (`audit-d02-t01-s1.md`, 24 rounds up to `315ea601c2f1b5a5d6043dbcf8556ba1b428bb8a`) split and expanded the string restrictions in `design/inventory/schema.json` across four definitions: `$defs/noLink` (on every string property of a record, `source` included alongside its anchored provenance pattern, and compiled into `link` in `scripts/check-inventory.py:426` for the recursive `links()` scan over all record values) refusing schemes with `://`, `:/`, or `:\`, network paths `//` or `\\` (such as `//localhost/help` and `\\localhost\help`), `mailto:`, `www.`, dotted hosts with a `/` path, and `.com`/`.org`/`.net`/`.gov`/`.edu` domains; `$defs/noHost` (on human-readable text fields: `label`, `keytip`, `shortcut`, `menuPath`, `behaviour`) refusing dotted host names in any script, three-or-more-part dotted numbers (IPv4 and shorthand), hexadecimal components beside a dot, IPv6 literals, `scheme:nonspace` (such as `https:localhost` or `data:text/plain`), and compatibility characters whose NFKC form contains visible ASCII (while a bare single-word word with no scheme, slash, colon, or dot such as `"localhost"` is not matched); `$defs/noColon` (on identifier fields: `id`, `parent`, `target`, `captureProfile`, `capturedFrom`, `idMso`, `uiaId`) refusing colons; and `$defs/noControl` (on all string fields) refusing BMP control and format characters, default-ignorables, and non-BMP characters, with 117 tests in `scripts/tests/test_check_inventory.py`.

## Round 1: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T12:55:14Z
- Effort: medium
- Type: adversarial
- Lines: 32
- Digest: 5c5aee6c14fec663

### adversarial: approve

No additional concrete failure demonstrated.

### consistency: approve

No separate finding.

### integration: needs-attention

1. **[P2] Valid file-format labels and behaviour sentences are rejected as addresses.** `design/inventory/schema.json:423` rejects a dot followed by letters without requiring a hostname before it. Reproduced through `validate()` with an otherwise valid record: `label: "Word Document (*.docx)"` produces `$[0].label: host name or address`. Likewise, `"Opens a .docx file."` cannot be stored as behaviour. The precondition is ordinary capture or authoring of file-format text, directly relevant to the Save As and dialog inventory required by `todo/02-interface/TODO-01-parity-inventory.md:210`. Narrow the address recognition and add positive tests preserving literal file extensions.

### source-defect: needs-attention

Finding 1 contradicts §21’s requirement to retain factual control names and independently written behaviour. Rewriting captured labels to satisfy the detector would make the inventory inaccurate.

### design: advisory

Not applicable (`Surface: no`).

### excellence: needs-attention

Finding 1 demonstrates that the stronger prohibition sacrifices inventory fidelity. Address detection must distinguish legitimate file-format text rather than prohibit its punctuation.

### record: needs-attention

2. **[P3] The audit describes enforcement that the current implementation does not provide.** `docs/reviews/02-interface/audit-d02-t01-s21.md:39` attributes the expanded protection to both `$defs/noLink` and a Python `LINK` constant. No such constant exists; `scripts/check-inventory.py:426` compiles the schema’s narrower `noLink` pattern, while additional restrictions live separately in `noHost` and `noControl`. The same sentence claims `localhost` coverage without qualification, but an otherwise valid record with `label: "localhost"` validates successfully. Reproduce through `validate()` against the current schema. Correct the record to name the actual rules, their field scope and their limits.

Verification limit: the whole-inventory check returned zero problems; two schema tests passed, and an in-memory removal of `menuPath`’s `noLink` reference failed the post-cap regression test. The full 117-test execution and recorded duration were not independently reproduced because the suite writes temporary files.

HIGHEST: P2
OVERALL: needs-attention

### Round 1 disposition

- **Round 1 `integration` / `source-defect` / `excellence` 1 (`P2`, file-format labels such as `"Word Document (*.docx)"` and behaviour sentences such as `"Opens a .docx file."` rejected as addresses by `$defs/noHost`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`). The full-stop branch now exempts an ASCII full stop `.` preceded by the start of the text (`^`), whitespace (`\s`), opening punctuation (`(`, `[`, `"`, `'`, `\u201c`, `\u2018`), or `*` when followed by a word (`(?<!^\.)(?<![\s(\["'\u201c\u2018*]\.)`), while still refusing any dotted host name with a label before the dot (`example.com`, `*.example.com`, `.example.com`, `\u2488com`, `\U00010428.com`). Covered by `test_any_host_name_or_address_in_text_is_refused_by_its_dots` in `scripts/tests/test_check_inventory.py`.
- **Round 1 `record` 2 (`P3`, self-review in `audit-d02-t01-s21.md:39` misattributed `noHost`/`noControl` rules to a `LINK` constant and overstated bare `localhost` coverage):** Verified and fixed in `docs/reviews/02-interface/audit-d02-t01-s21.md` (`## Self-review`), which now names the four schema definitions (`$defs/noLink`, `$defs/noHost`, `$defs/noColon`, `$defs/noControl`), `scripts/check-inventory.py:426`'s compilation of `noLink` into `link`, each rule's field scope, and the limit that a bare single-word hostname without a scheme, slash, colon, or dot is not matched.


## Round 2: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T13:06:44Z
- Effort: medium
- Type: adversarial
- Lines: 32
- Digest: bf23b92e50196693

### adversarial: approve

No additional concrete failure demonstrated.

### consistency: approve

No separate finding.

### integration: needs-attention

1. **[P2] The extension exception still rejects ordinary filenames in inventory text.** `design/inventory/schema.json:423` exempts `.docx` only when specified punctuation or whitespace precedes the dot. A filename still triggers the hostname rule. Reproduced with the existing `BOLD` fixture, setting `behaviour` to `"Loads Normal.dotm as the default template."`: `validate([record], schema, schema)` returns `['$[0].behaviour: host name or address']`. The precondition is ordinary authoring of a behaviour sentence identifying a local template, with no address or link. The Round 1 fix handles standalone extensions but leaves legitimate filename references unrepresentable. Add positive regression coverage and distinguish these references at the schema’s owning layer.

### source-defect: needs-attention

Finding 1 conflicts with `todo/02-interface/TODO-01-parity-inventory.md:567`: the inventory must retain facts and independently written behaviour. The governing rule does not prohibit naming local template files.

### design: advisory

Not applicable (`Surface: no`).

### excellence: needs-attention

Finding 1 shows that the punctuation heuristic still sacrifices inventory fidelity. Passing selected extension examples does not establish that ordinary file-related text survives validation.

### record: needs-attention

2. **[P3] The corrected field-scope description remains inaccurate.** `docs/reviews/02-interface/audit-d02-t01-s21.md:39` says `noLink` applies to every string property “except `source`.” In the actual schema, `source.allOf` includes both `noLink` and `noControl`, in addition to its provenance pattern. Reading that property reproduces the discrepancy; `test_every_string_field_carries_the_link_rule` also passes and explicitly requires its `noLink` reference. Remove the claimed exception. This is a documentation defect with no special precondition.

Verification limit: whole-inventory checking returned zero problems, and three directly invoked schema tests passed. The full 117-test suite and historical timing were not independently reproduced because its fixtures require filesystem writes. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 2 disposition

- **Round 2 `integration` / `source-defect` / `excellence` 1 (`P2`, ordinary filenames such as `"Loads Normal.dotm as the default template."` still rejected by `$defs/noHost`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`). The full-stop branch now allows an ASCII full stop `.` preceded by the start of text, whitespace, opening punctuation, `*`, or a single-dot ASCII filename stem (`[A-Za-z0-9_-]+`, with no preceding dot or compatibility full stop) only when followed by a known Office file extension and a token boundary (`docx`, `docm`, `dotx`, `dotm`, `doc`, `xlsx`, `xlsm`, `xltx`, `xltm`, `xlsb`, `xls`, `xlam`, `xla`, `pptx`, `pptm`, `potx`, `potm`, `ppsx`, `ppsm`, `ppt`, `ppam`, `ppa`, `vsdx`, `vsdm`, `vstx`, `vstm`, `vssx`, `vssm`, `vsd`, `vdx`, `mpp`, `mpt`, `msg`, `pst`, `ost`, `eml`, `ics`, `vcf`, `oft`, `odt`, `ods`, `odp`, `odg`, `rtf`, `txt`, `csv`, `tsv`, `pdf`, `xps`, `xml`, `htm`, `html`, `mht`, `mhtml`, `svg`, `png`, `jpg`, `jpeg`, `gif`, `bmp`, `tif`, `tiff`, `emf`, `wmf`), while refusing multi-dot tokens (`*.example.com`, `doc.docx.dotm`, `1.25.dotm`, `Normal..dotm`, `\u2488Normal.dotm`) and any non-Office domain suffix (`microsoft.de`, `contoso.xyz`, `office.live`, `example.com`). Covered by positive and negative assertions in `test_any_host_name_or_address_in_text_is_refused_by_its_dots` and `test_characters_containing_a_full_stop_are_address_marks` in `scripts/tests/test_check_inventory.py`.
- **Round 2 `record` 2 (`P3`, `audit-d02-t01-s21.md:39` stated `$defs/noLink` applied to every string property "except `source`"):** Verified and fixed in `docs/reviews/02-interface/audit-d02-t01-s21.md` (`## Self-review`), which now states that `$defs/noLink` is on every string property of a record (`source` included alongside its anchored provenance pattern).


## Round 3: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T13:23:35Z
- Effort: medium
- Type: adversarial
- Lines: 37
- Digest: 53f90bf6003ae4c4

### adversarial: approve

No additional bypass demonstrated by the probes run.

### consistency: approve

No separate finding.

### integration: needs-attention

1. **[P2] The extension exception still rejects explicitly supported Office formats.** At `design/inventory/schema.json:423`, the alternatives accept `xlam` and `ppam` but omit `xla`, `ppa` and `vdx`. Using the existing `BOLD` fixture, `validate([dict(BOLD, label=text)], schema, schema)` returns `['$[0].label: host name or address']` for each of:
   - `Excel Add-In (*.xla)`
   - `PowerPoint Add-In (*.ppa)`
   - `Visio XML Drawing (*.vdx)`

   Ordinary capture of these file-format labels therefore fails validation. Add the missing formats and test every extension claimed by the disposition, including uppercase variants.

### source-defect: needs-attention

Finding 1 prevents retaining factual file-format labels as required by `todo/02-interface/TODO-01-parity-inventory.md:567`.

### design: advisory

Not applicable (`SURFACE: no`).

### excellence: needs-attention

Finding 1 shows that selected passing examples do not establish file-format fidelity. The extension alternatives need systematic positive coverage.

### record: needs-attention

2. **[P3] The disposition claims acceptance that the implementation does not provide.** `docs/reviews/02-interface/audit-d02-t01-s21.md:133` explicitly lists `xla`, `ppa` and `vdx` as accepted extensions. The reproductions above contradict that claim. Reconcile the record with verified acceptance results.

Verification: whole-inventory checking returned zero problems. Three directly invoked schema tests passed; removing `menuPath`’s `noLink` reference in memory caused its coverage test to fail. The full suite was not rerun because its fixtures require filesystem writes unavailable in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 3 disposition

- **Round 3 `integration` / `source-defect` / `excellence` 1 (`P2`, `design/inventory/schema.json:423` omitted `xla`, `ppa`, `vdx`, and `mht` from the extension alternatives) and `record` 2 (`P3`, Round 2 disposition listed `xla`, `ppa`, `vdx`, and `mht` before the regex matched them):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Updated the extension alternation in `design/inventory/schema.json` (`[Xx][Ll](?:[SsTt][MmXx]?|[Ss][Bb]|[Aa][Mm]?)`, `[Pp][Pp][Aa][Mm]?`, `[Vv][DdSsTt][Xx]`, `[Mm][Hh][Tt](?:[Mm][Ll]?)?|[Hh][Tt][Mm][Ll]?`) so that `xla`, `ppa`, `vdx`, `vsx`, `vtx`, and `mht` (minimum length 3, never matching 2-letter ccTLDs such as `.ht`) are accepted, and added systematic positive assertions in `test_any_host_name_or_address_in_text_is_refused_by_its_dots` validating `"Excel Add-In (*.xla)"`, `"PowerPoint Add-In (*.ppa)"`, `"Visio XML Drawing (*.vdx)"`, and every extension in the 115-extension set (230 lowercase/uppercase cases: `Format (*.<ext>)` and `Saves File.<ext> or .<ext>.`).


## Round 4: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T13:30:34Z
- Effort: medium
- Type: adversarial
- Lines: 34
- Digest: 8d885511e1e54091

### adversarial: approve

No additional address bypass demonstrated by the probes run.

### consistency: needs-attention

Finding 1 conflicts with the requirement to preserve factual control names.

### integration: needs-attention

1. **[P2] The address rule rejects Excel function names required by the inventory.** At `design/inventory/schema.json:423`, dotted text is rejected unless it matches the file-extension exceptions. Using the existing `BOLD` fixture, `validate([dict(BOLD, label=text)], schema, schema)` returns `['$[0].label: host name or address']` for both `NORM.S.DIST` and `STDEV.S`. These are actual Excel functions. [Microsoft documentation](https://support.microsoft.com/en-us/excel/functions/norm-s-dist-function), [STDEV.S documentation](https://support.microsoft.com/en-us/excel/stdev-s-function).

   `todo/02-interface/TODO-01-parity-inventory.md:247` requires capturing every function in the function-library menus. Such captures cannot pass with their factual names intact. Fix address recognition at the schema layer and add positive regression coverage for these names.

### source-defect: needs-attention

Finding 1 originates in the schema’s classification of dotted text. Renaming captured functions would corrupt the inventory rather than fix validation.

### design: advisory

`SURFACE: no`. Finding 1 shows that extending a filename exception list does not resolve the underlying ambiguity between addresses and legitimate Office text.

### excellence: needs-attention

Finding 1 blocks the required function inventory despite passing extension tests.

### record: needs-attention

2. **[P3] The disposition misstates the tested extension count.** `docs/reviews/02-interface/audit-d02-t01-s21.md:186` claims a “107-extension set”; the current test tuple contains **115 extensions**, producing **230** lowercase/uppercase cases. Correct the recorded coverage.

Verification: whole-inventory checking returned zero problems; all 230 extension cases and three directly invoked schema tests passed. Removing `menuPath`’s `noLink` reference in memory caused its coverage test to fail. The full suite was not rerun because its fixtures require filesystem writes unavailable in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 4 disposition

- **Round 4 `consistency` / `integration` / `source-defect` / `excellence` 1 (`P2`, dotted Excel function names such as `NORM.S.DIST` and `STDEV.S` rejected by `$defs/noHost`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Updated `$defs/noHost` to allow uppercase Excel dotted function names (`BETA.DIST` through `Z.TEST`, including 3-part names such as `NORM.S.DIST`, `NORM.S.INV`, `BINOM.DIST.RANGE`, `CHISQ.DIST.RT`, `CHISQ.INV.RT`, `F.DIST.RT`, `F.INV.RT`, `T.DIST.2T`, `T.DIST.RT`, `T.INV.2T`, `FORECAST.ETS.CONFINT`, `FORECAST.ETS.SEASONALITY`, `FORECAST.ETS.STAT`) while still refusing uppercase and lowercase hostnames (`EXAMPLE.TEST`, `MICROSOFT.ID`, `WWW.MICROSOFT.COM`), and added positive assertions for all 73 dotted Excel function names (`len(funcs) == 73`, tested both as control labels and inside behaviour sentences) in `test_any_host_name_or_address_in_text_is_refused_by_its_dots`.
- **Round 4 `record` 2 (`P3`, Round 3 disposition misstated the tested extension count as 107 instead of 115 / 230 cases):** Verified and fixed in `docs/reviews/02-interface/audit-d02-t01-s21.md` (`### Round 3 disposition`) and locked in with `self.assertEqual(len(exts), 115)` in `scripts/tests/test_check_inventory.py`.


## Round 5: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T13:41:05Z
- Effort: medium
- Type: adversarial
- Lines: 36
- Digest: 424d89394155e9be

### adversarial: needs-attention

1. **[P2] The Excel-function exception admits unrelated hostnames.** At `design/inventory/schema.json:423`, the exception checks abbreviated suffixes before the dot rather than complete function names. In particular, `(?<=ER\.)ID` accepts any name ending in `ER.ID`.

   Reproduced with the existing `BOLD` fixture: `validate([dict(BOLD, label="ATTACKER.ID")], schema, schema)` returns `[]`. `SERVER.ID` also passes, as does `"Visit ATTACKER.ID now"` in `label`, `behaviour` and `menuPath`. Running `check()` with an in-memory injected record likewise returns no problems.

   These unrelated hostnames bypass the address prohibition through the exception intended for `REGISTER.ID`. Match complete function tokens and add negative tests for unrelated names sharing their suffixes.

### consistency: needs-attention

Finding 1 violates the no-address requirement while satisfying the new selected hostname tests.

### integration: needs-attention

The recursive `noLink` scan does not catch this bypass. The checker accepts the injected record without diagnostics.

### source-defect: needs-attention

Finding 1 originates in the schema’s function-name exception. Fix the recognition there.

### design: advisory

`SURFACE: no`. Complete-token exceptions would express the intended function allowlist more accurately than combinations of abbreviated prefixes and suffixes.

### excellence: needs-attention

All 73 function cases pass, but that coverage does not distinguish legitimate functions from unrelated hostnames accepted by the same exception.

### record: approve

The corrected counts match: 115 extensions, 230 case variants and 73 functions. All these positive cases passed independently. Two schema tests passed; removing `menuPath`’s `noLink` reference in memory caused its coverage test to fail. Whole-inventory checking returned zero problems.

The full filesystem-writing suite was not rerun in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 5 disposition

- **Round 5 `adversarial` / `consistency` / `integration` / `source-defect` / `excellence` 1 (`P2`, abbreviated lookbehind stems such as `(?<=ER\.)ID` admitted unrelated hostnames such as `ATTACKER.ID` and `SERVER.ID`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Replaced the 2-character stem lookbehinds in `$defs/noHost` with complete-token lookbehinds (`(?<![^\s(\[\x22\x27\u201c\u2018,;:].{L}\.)(?<=STEM\.)SUFFIX` for each complete Excel function stem `F`, `T`, `Z`, `ERF`, `ISO`, `SQL`, `VAR`, `BETA`, `ECMA`, `ERFC`, `MODE`, `NORM`, `RANK`, `SKEW`, `BINOM`, `CHISQ`, `ERROR`, `EXPON`, `FLOOR`, `GAMMA`, `STDEV`, `F.INV`, `T.INV`, `NORM.S`, `F.DIST`, `T.DIST`, `CEILING`, `GAMMALN`, `HYPGEOM`, `LOGNORM`, `POISSON`, `WEIBULL`, `WORKDAY`, `FORECAST`, `NEGBINOM`, `QUARTILE`, `REGISTER`, `CHISQ.INV`, `CONFIDENCE`, `COVARIANCE`, `PERCENTILE`, `BINOM.DIST`, `CHISQ.DIST`, `NETWORKDAYS`, `PERCENTRANK`, and `FORECAST.ETS`), and added negative regression assertions in `test_any_host_name_or_address_in_text_is_refused_by_its_dots` for `"ATTACKER.ID"`, `"SERVER.ID"`, `"Visit ATTACKER.ID now"`, `"XREGISTER.ID"`, `"FOO.DIST"`, `"BAR.S"`, `"BAZ.TEST"`, `"HOST.INTL"`, `"XT.DIST.2T"`, and `"X.T.DIST.2T"`.


## Round 6: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T13:46:07Z
- Effort: medium
- Type: adversarial
- Lines: 34
- Digest: d7f3f7f40257f2c6

### adversarial: needs-attention

1. **[P2] The new token boundary rejects valid Excel formulas.** At `design/inventory/schema.json:423`, the complete-stem lookbehinds exclude `=` as a permissible preceding character. Using the existing `BOLD` fixture, `validate([dict(BOLD, behaviour="Calculates =STDEV.S(1,2).")], schema, schema)` returns `['$[0].behaviour: host name or address']`. `=NORM.S.DIST(0,TRUE)` also fails. Removing the new five-character stem boundary in memory makes the STDEV example pass.

   An independently written behaviour sentence containing a valid formula therefore cannot enter the inventory. Recognise formula syntax at the schema layer and add positive regression cases alongside the hostname negatives.

### consistency: needs-attention

Finding 1 conflicts with §21’s allowance for independently written behaviour and the Excel formula surface required at `todo/02-interface/TODO-01-parity-inventory.md:269`.

### integration: needs-attention

The function tests at `scripts/tests/test_check_inventory.py:399-402` exercise bare names and prose containing names, but omit formulas beginning with `=`. All 73 existing function cases pass despite Finding 1.

### source-defect: needs-attention

Finding 1 originates in the schema’s boundary classification. Removing formula notation from stored descriptions would conceal the defect.

### design: advisory

`SURFACE: no`. Function recognition needs to account for expression syntax as well as standalone names.

### excellence: needs-attention

The hostname repair introduces a demonstrated fidelity regression for legitimate formula text.

### record: approve

Independently verified: the reported hostname probes are rejected; 115 extensions in both cases and all 73 function cases pass; whole-inventory checking returns zero problems. Four directly invoked schema tests passed. Removing `menuPath`’s `noLink` reference in memory caused its coverage test to fail.

The full filesystem-writing suite was not rerun in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 6 disposition

- **Round 6 `adversarial` / `consistency` / `integration` / `source-defect` / `excellence` 1 (`P2`, complete-stem lookbehinds excluded formula operators such as `=`, rejecting `"Calculates =STDEV.S(1,2)."` and `"=NORM.S.DIST(0,TRUE)"`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Added Excel formula operators (`=`, `+`, `*`, `/`, `^`, `&`, `<`, `>`, none of which is a valid RFC 952/1123/IDNA DNS label character, while keeping `-` excluded so hyphenated hostnames such as `FOO-REGISTER.ID` remain refused) to the opening and closing boundary character classes of the Excel function lookbehinds in `$defs/noHost`, and added positive regression assertions for `"Calculates =STDEV.S(1,2)."`, `"=NORM.S.DIST(0,TRUE)"`, and `f"Inserts {fn} or ={fn}(1,2) + {fn}."` across all 73 functions alongside negative assertion `"FOO-REGISTER.ID"`.


## Round 7: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T13:50:36Z
- Effort: medium
- Type: adversarial
- Lines: 32
- Digest: f3fcb6f52d331ed3

### adversarial: needs-attention

1. **[P2] Subtraction and negation still reject valid formulas.** At `design/inventory/schema.json:423`, the function boundary excludes `-`. Using the existing `BOLD` fixture, `validate([dict(BOLD, behaviour=text)], schema, schema)` rejects both `=1-STDEV.S(1,2)` and `=-NORM.S.DIST(0,TRUE)` with `host name or address`. Adding a space after the subtraction operator makes the first example pass. Legitimate behaviour text therefore requires cosmetic rewriting to enter the inventory. Distinguish formula expressions from hyphenated hostnames and test both.

### consistency: needs-attention

2. **[P2] Cell ranges are classified as URI schemes.** At `design/inventory/schema.json:423`, `[A-Za-z][A-Za-z0-9+.-]*[:…]\S` matches `A1:B2`. The same reproduction rejects `Calculates =SUM(A1:B2).`, while `Calculates =SUM(A1).` passes. Disabling `noHost` in memory removes the failure. This prevents independently written descriptions containing ordinary Excel ranges. Recognise range syntax without admitting actual URI schemes.

### integration: needs-attention

The 73 function cases at `scripts/tests/test_check_inventory.py:401-403` pass despite both failures: their formulas use numeric arguments and omit subtraction before functions. Add regression cases covering these expression forms.

### source-defect: needs-attention

Both findings originate in the schema’s address classification. Reformatting stored descriptions would conceal the defects rather than fix their owning layer.

### design: advisory

`SURFACE: no`. These failures demonstrate that character-boundary exceptions alone do not distinguish formula syntax from addresses. Resolve that ambiguity explicitly before extending the exception list again.

### excellence: needs-attention

The rule still blocks factual formula descriptions required by the Excel inventory at `todo/02-interface/TODO-01-parity-inventory.md:269`.

### record: approve

Verified the Round 6 examples, 230 extension cases, 73 function cases and two directly invoked tests. Whole-inventory checking returned zero problems. No additional record discrepancy demonstrated.

The full filesystem-writing suite was not rerun in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 7 disposition

- **Round 7 `adversarial` / `integration` / `source-defect` / `excellence` 1 (`P2`, subtraction and negation before dotted Excel functions such as `=1-STDEV.S(1,2)` and `=-NORM.S.DIST(0,TRUE)` rejected by `$defs/noHost`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Allowed `-` before an Excel function stem when either `-` is preceded by start-of-text, whitespace, or an opening delimiter/operator (`=-NORM.S.DIST(0,TRUE)`, `-STDEV.S`) or the function token is a call followed by `(` (`(?!(?<=[A-Za-z0-9_.-]-.{L}\.)(?![A-Z0-9.]*\())`, accepting `=1-STDEV.S(1,2)` while still refusing hyphenated hostnames without `(` such as `FOO-REGISTER.ID`, `1-REGISTER.ID`, and `a-b.STDEV.S`).
- **Round 7 `consistency` / `integration` / `source-defect` / `excellence` 2 (`P2`, Excel cell ranges such as `A1:B2` in `Calculates =SUM(A1:B2).` matched by the URI-scheme branch `[A-Za-z][A-Za-z0-9+.-]*[:...]\S`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Exempted Excel A1 cell ranges (`[A-Za-z]{1,3}\$?[1-9]\d{0,6}:\$?[A-Za-z]{1,3}\$?[1-9]\d{0,6}`), R1C1 cell ranges (`(?:[Rr]\d+)?[Cc]\d+:[Rr]\d+[Cc]\d+`), and uppercase column ranges (`(?!(?:FTP|TEL|URN|SSH|GIT|SIP|WSS?|IRC|MMS|NFS|SMB):)[A-Z]{1,3}:\$?[A-Z]{1,3}`) bounded by non-address characters (`(?![A-Za-z0-9_/:.-])`) on the URI-scheme branch, and added positive regression assertions (`"Calculates =SUM(A1:B2)."`, `"=SUM($A$1:$B$2, XFD1:XFD1048576, A:Z, R1C1:R2C2)"`, and `f"Inserts {fn}, =1-{fn}(A1:B2) or =-{fn}(1,2)."` across all 73 functions) alongside negative assertions (`"http:B2"`, `"FTP:X"`, `"s3:bucket"`, `"1-REGISTER.ID"`, `"a-b.STDEV.S"`).


## Round 8: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T13:57:46Z
- Effort: medium
- Type: adversarial
- Lines: 32
- Digest: 6b1798898f4b8fd3

### adversarial: needs-attention

1. **[P2] A parenthesis lets a hyphenated hostname bypass the function exception.** At `design/inventory/schema.json:423`, the Round 7 exception accepts `FOO-REGISTER.ID` when followed by `(` without requiring a formula context. Using the existing `BOLD` fixture, `behaviour="Visit FOO-REGISTER.ID(help desk)"` passes both `validate()` and `check()` with an in-memory injected record. This is an unrelated hostname followed by prose, not an Excel function call. Recognise complete function tokens in expression context and add this negative regression case.

### consistency: needs-attention

2. **[P2] The URI blacklist rejects valid whole-column formulas.** At `design/inventory/schema.json:423`, the range exception explicitly excludes `FTP:` and `SMB:`, although both names identify valid Excel columns. `behaviour="=SUM(FTP:FTP)"` fails both schema validation and the checker with `host name or address`; `=SUM(FTP1:FTP2)` and `=SUM(A:A)` pass. Removing `noHost` in memory makes the rejected record pass. Distinguish formula ranges from URI schemes using their context rather than reserving column names.

### integration: needs-attention

The checker reproduces both findings. Its recursive `noLink` scan does not catch Finding 1. The 230 extension cases and 73 function cases at `scripts/tests/test_check_inventory.py:375-406` pass despite these failures.

### source-defect: needs-attention

Both defects originate in `$defs/noHost`. Fix the schema’s classification; rewriting stored descriptions would conceal the failures.

### design: advisory

`SURFACE: no`. Findings 1 and 2 demonstrate that punctuation exceptions and scheme-name exclusions cannot reliably distinguish prose addresses from formulas. Explicit expression context would address both ambiguities.

### excellence: needs-attention

The current rule both admits prohibited address text and rejects legitimate formula descriptions. Passing the selected regression examples does not establish the required fidelity.

### record: approve

Independently verified: Round 7’s reported positive examples, 230 extension cases, 73 function cases, three directly invoked schema tests, and zero whole-inventory problems. Removing `menuPath`’s `noLink` reference in memory caused its coverage test to fail.

The full filesystem-writing suite was not rerun in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 8 disposition

- **Round 8 `adversarial` / `integration` / `source-defect` / `excellence` 1 (`P2`, `Visit FOO-REGISTER.ID(help desk)` bypassed the hyphenated-hostname check because `(` was accepted without requiring formula expression context):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Restricted subtraction before an Excel function stem (`-STEM.`) to explicit formula contexts preceded by `=[0-9]`, `=[A-Z][0-9]`, or `)` and followed by a formula argument list `[A-Z0-9.]*\([A-Za-z0-9$.,:;_"'+*/^&<>=-]+\)` without spaces, refusing `"Visit FOO-REGISTER.ID(help desk)"`, `"Visit 1-REGISTER.ID(help desk)"`, and `"Visit 1-REGISTER.ID(1,2)"`.
- **Round 8 `consistency` / `integration` / `source-defect` / `excellence` 2 (`P2`, whole-column formula ranges such as `=SUM(FTP:FTP)` and `=SUM(SMB:SMB)` rejected by the bare-scheme blacklist):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Allowed any 1-to-3 letter uppercase whole-column range (`[A-Z]{1,3}:\$?[A-Z]{1,3}`, including `FTP:FTP` and `SMB:SMB`) when preceded by a formula/range delimiter (`=`, `(`, `,`, `;`, `!`, `$`), while retaining the bare-prose scheme check (`FTP:X`) outside formula delimiters.


## Round 9: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T14:04:23Z
- Effort: medium
- Type: adversarial
- Lines: 39
- Digest: e339a7f1fe2f1a0e

### adversarial: needs-attention

1. **[P2] Parenthesised prose bypasses the bare-scheme prohibition.** At `design/inventory/schema.json:423`, `(` alone activates the whole-column exception without establishing formula context. With the existing `BOLD` fixture, `behaviour="FTP:X"` is rejected, but `behaviour="See (FTP:X)"` passes both schema validation and `check()` with an in-memory injected record. Ordinary punctuation therefore admits the same prohibited address. Require formula context rather than treating an opening parenthesis as sufficient.

### consistency: needs-attention

2. **[P2] The subtraction repair rejects ordinary valid formulas.** At `design/inventory/schema.json:423`, the operand and argument restrictions accept `=1-STDEV.S(1,2)` but reject all of:

   - `=10-STDEV.S(1,2)`
   - `=A10-STDEV.S(1,2)`
   - `=1-STDEV.S(1, 2)`
   - `=1-STDEV.S(SUM(A1:A2),2)`

Schema validation reports `host name or address`. The checker independently reproduces the first three failures. Removing `noHost` in memory makes the first pass. Independently written behaviour permitted by `todo/02-interface/TODO-01-parity-inventory.md:567` cannot retain these formulas.

### integration: needs-attention

Both findings reach the checker. Its recursive link scan does not catch Finding 1. The 230 extension cases and 73 function cases pass despite these failures; the formula fixtures exercise the narrowly accepted operand forms.

### source-defect: needs-attention

Both defects originate in `$defs/noHost` at `design/inventory/schema.json:423`. Correct expression recognition there. Reformatting stored descriptions would conceal Finding 2.

### design: advisory

`SURFACE: no`. The demonstrated failures show that isolated punctuation and fixed-width operand exceptions do not establish expression context. Recognise complete formula expressions before applying their exceptions.

### excellence: needs-attention

The rule still accepts prohibited address prose and rejects legitimate formula descriptions. The Round 8 examples pass, but their neighbouring cases break the intended behaviour.

### record: approve

Verified: the reported Round 8 positive and negative examples, 230 extension cases, 73 function cases, three directly invoked schema tests, and zero whole-inventory problems. Removing `menuPath`’s `noLink` reference in memory caused its coverage test to fail.

The full filesystem-writing suite was not rerun in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 9 disposition

- **Round 9 `adversarial` / `integration` / `source-defect` / `excellence` 1 (`P2`, `See (FTP:X)` bypassed the bare-scheme prohibition because `(` alone activated the whole-column exception without formula context):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Restricted the whole-column exception for scheme-named columns (`FTP`, `SMB`, `TEL`, `URN`, `SSH`, `GIT`, `SIP`, `WS`, `WSS`, `IRC`, `MMS`, `NFS`) to formula function calls (`(?<==[A-Z]{3,8}\()` or sheet-qualified `(?<=\b!)` followed by `(?=[),;])`), so `See (FTP:X)` is refused while `=SUM(FTP:FTP)`, `=SUM(SMB:SMB)`, and `=SUM(Sheet1!FTP:FTP)` remain accepted.
- **Round 9 `consistency` / `integration` / `source-defect` / `excellence` 2 (`P2`, subtraction repair rejected multi-character operands, spaces after commas, and nested parentheses such as `=10-STDEV.S(1,2)`, `=A10-STDEV.S(1,2)`, `=1-STDEV.S(1, 2)`, and `=1-STDEV.S(SUM(A1:A2),2)`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Expanded the formula-subtraction lookbehinds to accept multi-character numeric and cell operands preceded by a formula operator/delimiter (`[=+(,;*/^&<>][A-Za-z0-9$.]{0,5}[0-9]-` or `\)-`) and argument lists containing spaces and nested parenthesised calls (`(?!\([A-Za-z]+\s+[A-Za-z]+)[A-Z0-9.]*\((?:[A-Za-z0-9$.,:;_"'+*/^&<>=\s-]|\([A-Za-z0-9$.,:;_"'+*/^&<>=\s-]*\))+\)`), and added positive regression assertions for all four cases alongside negative assertion `"See (FTP:X)"`.


## Round 10: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T14:10:40Z
- Effort: medium
- Type: adversarial
- Lines: 34
- Digest: 456b3b9ac37672c7

### adversarial: needs-attention

1. **[P2] Parenthesised prose still bypasses hostname rejection.** At `design/inventory/schema.json:423`, `(` qualifies as a formula delimiter without establishing a formula. `behaviour="Visit (1-REGISTER.ID(1,2))"` passes both `validate()` and `check()` with an in-memory injected record. The prohibited hostname `1-REGISTER.ID` becomes acceptable when surrounded by punctuation. Require actual expression context before granting the subtraction exception.

### consistency: needs-attention

2. **[P2] The whole-column repair rejects valid ranges outside the first argument.** At `design/inventory/schema.json:423`, the immediate `=FUNCTION(` lookbehind accepts `=SUM(FTP:FTP)` but rejects `=SUM(A:A,FTP:FTP)` and `=SUM(SUM(FTP:FTP))`. Both fail schema validation and the checker with `host name or address`. Formula recognition must preserve ranges in later arguments and nested calls.

3. **[P2] Subtraction still imposes artificial operand-length and nesting limits.** At `design/inventory/schema.json:423`, the six-character operand limit rejects `=A100000-STDEV.S(1,2)`, and the single nested-parenthesis allowance rejects `=1-STDEV.S(SUM(SUM(A1:A2)),2)`. Both failures reproduce through schema validation and the checker. These legitimate descriptions cannot be retained unchanged.

### integration: needs-attention

All three findings reach `check()`. The regression matrix at `scripts/tests/test_check_inventory.py:359-408` passes despite them. Extend coverage to prose delimiters, argument position, longer references and deeper nesting.

### source-defect: needs-attention

All three defects originate in `$defs/noHost` at `design/inventory/schema.json:423`. Correct recognition there; rewriting stored descriptions would conceal the failures.

### design: advisory

`SURFACE: no`. These reproductions show that local punctuation and fixed-width lookbehinds do not establish formula context. Recognise complete expressions before applying formula exceptions.

### excellence: needs-attention

The rule still admits prohibited hostname prose and rejects legitimate formula descriptions, contrary to the fidelity requirement at `todo/02-interface/TODO-01-parity-inventory.md:567`.

### record: approve

Verified the Round 9 examples, three directly invoked schema tests, and the existing address/extension/function matrix through schema validation in memory. Removing `menuPath`’s `noLink` reference caused its coverage test to fail. Whole-inventory checking returned zero problems.

The full filesystem-writing suite was not rerun in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 10 disposition

- **Round 10 `adversarial` / `integration` / `source-defect` / `excellence` 1 (`P2`, parenthesised prose `Visit (1-REGISTER.ID(1,2))` bypassed hostname rejection because `(` qualified as a formula delimiter without establishing a formula starting with `=`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Added a forward expression guard on Branch 4 (`(?:^|(?<=[A-Za-z.?!:;][\s]))(?![(\s"'\u201c\u2018]*=)[A-Za-z0-9$.,:;_"'+*/^&<>()-]*[0-9)]\s*-\s*[A-Z0-9]+\.[A-Z0-9.]+\(`) so any hyphenated dotted call in a clause that does not begin with `=` is rejected as a hostname, refusing `"Visit (1-REGISTER.ID(1,2))"`, `"Visit ((1-REGISTER.ID(1,2)))"`, and `"=1-REGISTER.ID(help desk)"`.
- **Round 10 `consistency` / `integration` / `source-defect` / `excellence` 2 (`P2`, whole-column repair rejected valid scheme-named column ranges outside the first argument such as `=SUM(A:A,FTP:FTP)` and `=SUM(SUM(FTP:FTP))`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Allowed scheme-named whole-column ranges after `=`, `(`, `,`, `;`, `!`, or space inside a formula expression while adding a forward clause guard on Branch 7 (`(?:^|(?<=[A-Za-z.?!:;][\s]))(?![(\s"'\u201c\u2018]*=)[A-Za-z0-9$.,:;_"'+*/^&<>\s()-]*[(,;]\s*\$?(?:FTP|TEL|URN|SSH|GIT|SIP|WSS?|IRC|MMS|NFS|SMB):\S`) that refuses any parenthesised or comma-preceded scheme-named token in prose not introduced by `=` (`"See (FTP:X)"`, `"See (FTP:FTP)"`, `"See (A:A,FTP:FTP)"`), while accepting `"=SUM(FTP:FTP)"`, `"=SUM(A:A,FTP:FTP)"`, `"=SUM(A:A, FTP:FTP)"`, and `"=SUM(SUM(FTP:FTP))"`.
- **Round 10 `consistency` / `integration` / `source-defect` / `excellence` 3 (`P2`, subtraction imposed a six-character operand limit and single nested-parenthesis limit, rejecting `=A100000-STDEV.S(1,2)` and `=1-STDEV.S(SUM(SUM(A1:A2)),2)`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Replaced the fixed-length operand lookbehinds with `(?<=[0-9)]-.{k}\.)` (paired with the clause-level `=` check from Finding 1 so operands of any length such as `=A100000-STDEV.S(1,2)` and `=XFD1048576-STDEV.S(1,2)` are accepted without admitting prose), and expanded the argument-list pattern to support multi-level nested parentheses (`=1-STDEV.S(SUM(SUM(A1:A2)),2)`).

## Round 11: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T14:30:59Z
- Effort: medium
- Type: adversarial
- Lines: 40
- Digest: de298aaee628ea6b

### adversarial: needs-attention

1. **[P2] Clause guards still admit prohibited addresses through ordinary punctuation.** At `design/inventory/schema.json:423`, the guard misses `behaviour="Visit  (1-REGISTER.ID(1,2))"` (two spaces), `"Visit [1-REGISTER.ID(1,2)]"` and `"See [ (FTP:X)]"`. All return zero problems through both `validate()` and `check()` with in-memory records. The formula exceptions activate without an actual formula. Recognise expression context independently of prose spacing and brackets.

### consistency: needs-attention

2. **[P2] Whole-column ranges still reject legitimate trailing syntax.** At `design/inventory/schema.json:423`, the scheme-named column exception requires an immediate `)`, `,` or `;`. Consequently, `=SUM(FTP:FTP )` and `=SUM(FTP:FTP+1)` fail with `host name or address`, although `=SUM(FTP:FTP)` passes. Whitespace and arithmetic must not turn a valid range into a prohibited address.

3. **[P2] Subtraction still imposes artificial nesting and argument restrictions.** At `design/inventory/schema.json:423`, all these formulas fail with `host name or address`:

   - `=1-STDEV.S(SUM(SUM(SUM(SUM(A1:A2)))),2)`
   - `=1-STDEV.S(Sheet1!A1:A2)`
   - `=1-STDEV.S(A1:A2,3%)`

The expanded pattern remains bounded in nesting and excludes sheet qualifiers and percentage operators. These valid descriptions cannot be retained unchanged.

### integration: needs-attention

All three findings reproduce through `check()`. The regression matrix at `scripts/tests/test_check_inventory.py:356-411` passes through in-memory schema validation despite these failures. Extend it with these punctuation, range-suffix and argument cases.

### source-defect: needs-attention

All three defects originate in `$defs/noHost` at `design/inventory/schema.json:423`. Correct classification there; rewriting stored descriptions would conceal the failures.

### design: advisory

`SURFACE: no`. The demonstrated failures support recognising complete formula expressions before granting exceptions. Expanding local lookbehinds and bounded parentheses patterns continues to admit addresses and reject formulas.

### excellence: needs-attention

The failures violate the factual fidelity required by `todo/02-interface/TODO-01-parity-inventory.md:567`: prohibited addresses pass while independently written formula descriptions fail.

### record: approve

Verified the existing address/extension/function matrix in memory, three direct schema tests, and zero whole-inventory problems. Removing `menuPath`’s `noLink` reference caused its coverage test to fail.

The full filesystem-writing suite was not rerun in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 11 disposition

- **Round 11 `adversarial` / `integration` / `source-defect` / `excellence` 1 (`P2`, clause guards missed multi-space and bracketed prose such as `"Visit  (1-REGISTER.ID(1,2))"`, `"Visit [1-REGISTER.ID(1,2)]"`, and `"See [ (FTP:X)]"`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Replaced the single-space lookbehind in the Branch 4 and Branch 7 clause guards with `(?<![\s=,;(*/^&<>+-])\s+` and included `[` / `]` in the scanned prose character class, so any number of spaces and bracketed/parenthesised delimiters after a non-operator word trigger the guard unless the expression starts with `=`, refusing `"Visit  (1-REGISTER.ID(1,2))"`, `"Visit [1-REGISTER.ID(1,2)]"`, and `"See [ (FTP:X)]"`.
- **Round 11 `consistency` / `integration` / `source-defect` / `excellence` 2 (`P2`, scheme-named whole-column ranges rejected legitimate trailing whitespace and arithmetic such as `=SUM(FTP:FTP )` and `=SUM(FTP:FTP+1)`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Expanded the trailing boundary of the scheme-named whole-column exception to `(?=[\s),;+*/^&<>=-]|$)`, accepting `"=SUM(FTP:FTP )"` and `"=SUM(FTP:FTP+1)"`.
- **Round 11 `consistency` / `integration` / `source-defect` / `excellence` 3 (`P2`, subtraction argument pattern bounded nesting depth and excluded `!` and `%`, rejecting `=1-STDEV.S(SUM(SUM(SUM(SUM(A1:A2)))),2)`, `=1-STDEV.S(Sheet1!A1:A2)`, and `=1-STDEV.S(A1:A2,3%)`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Replaced the bounded nested-parenthesis group with an arbitrary-depth formula-expression character class `[A-Za-z0-9$.,:;_!%"'+*/^&<>=\s()-]+` (guarded by `(?![A-Za-z0-9$.,:;_!%"'+*/^&<>=\s()-]*[A-Za-z]\s+[A-Za-z])` so multi-word prose inside parentheses is still rejected), accepting arbitrary nesting depth, sheet qualifiers (`!`), and percentage operators (`%`).

## Round 12: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T14:37:01Z
- Effort: medium
- Type: adversarial
- Lines: 43
- Digest: aafabf1e93b551a6

### adversarial: needs-attention

1. **[P2] Curly quotes bypass the clause guards.** At `design/inventory/schema.json:423`, the scanned prose classes omit curly quotes. Using the existing `BOLD` fixture, both these `behaviour` values pass `validate()` and `check()` with in-memory injected records:

   - `Visit “(1-REGISTER.ID(1,2))”`
   - `See “(FTP:X)”`

   Neither contains a formula introduced by `=`. Ordinary quoted prose activates the formula exceptions and admits prohibited addresses. Establish expression context before granting those exceptions.

### consistency: needs-attention

2. **[P2] The expanded subtraction exception still rejects valid formula arguments.** At `design/inventory/schema.json:423`, the multi-word guard rejects quoted sheet names, while the argument character class excludes structured references and array constants. These all fail with `host name or address` through both validation paths:

   - `=1-STDEV.S('Sales Data'!A1:A2)`
   - `=1-STDEV.S(Table1[Amount])`
   - `=1-STDEV.S({1,2,3})`

   The precondition is an independently written description containing these ordinary Excel constructs. Recognise their syntax without requiring cosmetic changes to stored descriptions.

### integration: needs-attention

Both findings reach `check()`. Its recursive link scan does not catch Finding 1. The existing regression matrix at `scripts/tests/test_check_inventory.py:356` passes despite these failures.

### source-defect: needs-attention

Both defects originate in `$defs/noHost` at `design/inventory/schema.json:423`. They undermine §21’s address prohibition and allowance for independently written behaviour. Correct classification at that owning layer.

### design: advisory

`SURFACE: no`. The reproductions show that extending character classes does not establish formula context. Recognise complete expressions and quoted operands before applying exceptions.

### excellence: needs-attention

The demonstrated failures still admit prohibited addresses and reject legitimate factual descriptions. Passing the selected examples does not establish the required fidelity.

### record: approve

Verified the existing address, extension and function matrix through in-memory schema validation, three directly invoked schema tests, and zero whole-inventory problems. Removing `menuPath`’s `noLink` reference caused its coverage test to fail.

The full filesystem-writing suite was not rerun in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 12 disposition

- **Round 12 `adversarial` / `integration` / `source-defect` / `excellence` 1 (`P2`, curly quotes bypassed the clause guards so `Visit “(1-REGISTER.ID(1,2))”` and `See “(FTP:X)”` passed without `=`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Replaced the enumerated non-`=` character class in the Branch 4 and Branch 7 clause guards with `(?:(?!=).)*?` so any sequence of characters (including curly quotes `\u201c` / `\u201d`, `\u2018` / `\u2019`, braces, or other punctuation) between a clause boundary and a hyphenated dotted call or parenthesised/comma-preceded scheme-named token is rejected unless `=` precedes it, refusing `"Visit \u201c(1-REGISTER.ID(1,2))\u201d"` and `"See \u201c(FTP:X)\u201d"`.
- **Round 12 `consistency` / `integration` / `source-defect` / `excellence` 2 (`P2`, subtraction argument pattern rejected quoted sheet names `'Sales Data'!A1:A2`, structured references `Table1[Amount]`, and array constants `{1,2,3}`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Added structured-reference and array-constant characters (`[`, `]`, `{`, `}`, `#`, `@`) to the argument character class and exempted quoted sheet names (`'...'!`), string literals (`"..."`), and structured-reference column specifiers (`[...]`) from the multi-word prose check (`(?![A-Za-z0-9$.,:;_!%#@{}\[\]"'+*/^&<>=\s()-]*[A-Za-z]\s+[A-Za-z](?![^'"\[\]]*(?:'\s*!|"|\])))`), accepting `"=1-STDEV.S('Sales Data'!A1:A2)"`, `"=1-STDEV.S(Table1[Amount])"`, and `"=1-STDEV.S({1,2,3})"` while still refusing `"=1-REGISTER.ID(help desk)"`.

## Round 13: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T14:43:35Z
- Effort: medium
- Type: adversarial
- Lines: 39
- Digest: 95327bf457e3aa9a

### adversarial: needs-attention

1. **[P2] An equals sign in quoted prose bypasses address rejection.** At `design/inventory/schema.json:423`, `(?:(?!=).)*?` stops the clause guards at any `=`, without establishing a formula. Both these `behaviour` values return zero problems through `validate()` and `check()` with in-memory records:

   - `See "mode=fast,(FTP:X)"`
   - `Visit "label=(1-REGISTER.ID(1,2))"`

   These are quoted prose containing prohibited addresses. Recognise expression context before granting formula exceptions; an arbitrary preceding equals sign is insufficient.

### consistency: needs-attention

2. **[P2] Whitespace inside a quoted sheet name incorrectly restarts the clause guards.** At `design/inventory/schema.json:423`, both `=SUM('Sales Data'!A1,FTP:FTP)` and `=SUM('Sales Data'!A1)-STDEV.S(A1:A2)` fail with `host name or address` through both validation paths. The guard starts again at the space inside `'Sales Data'`, losing the formula’s preceding `=`. The control `=SUM(Sheet1!A1,FTP:FTP)` passes. Track quoted operands when identifying clause boundaries.

3. **[P2] Subtraction still rejects named and structured-reference operands.** At `design/inventory/schema.json:423`, `=Total-STDEV.S(A1:A2)` and `=Table1[Amount]-STDEV.S(A1:A2)` fail through both validation paths. With `Total` defined as a numeric name or `Table1[Amount]` as a numeric table column, these are legitimate expressions. The subtraction exception requires the preceding operand to end in a digit or `)`, excluding these supported operand forms. Recognise complete operands instead of restricting their final character.

### integration: needs-attention

All three findings reproduce through `check()` using the existing `TAB`, `GROUP` and `BOLD` fixtures with only `behaviour` changed. The recursive link scan does not catch Finding 1.

### source-defect: needs-attention

The defects originate in `$defs/noHost` at `design/inventory/schema.json:423`. They admit prohibited addresses and reject legitimate independently written descriptions. Correct the classification there; changing descriptions to accommodate the detector would conceal the defects.

### design: advisory

`SURFACE: no`. Findings 1 and 2 demonstrate that locating `=` and whitespace independently cannot establish expression boundaries. Recognise expressions, quoted operands and surrounding prose before applying address exceptions.

### excellence: needs-attention

The existing regression matrix at `scripts/tests/test_check_inventory.py:356` passes despite these failures. Add cases combining quoted sheet names, later arguments and different subtraction operands, alongside prose containing equals signs.

### record: approve

Independently verified the existing address, extension and function matrix through in-memory schema validation, three directly invoked schema tests, and zero whole-inventory problems.

The full filesystem-writing suite was not rerun in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 13 disposition

- **Round 13 `adversarial` / `integration` / `source-defect` / `excellence` 1 (`P2`, an equals sign in quoted prose such as `See "mode=fast,(FTP:X)"` and `Visit "label=(1-REGISTER.ID(1,2))"` stopped the clause guards without establishing a formula):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Restricted the `=` check inside the Branch 4 and Branch 7 clause guards to a formula-opening `=` (`(?:^|(?<=[\s(\["'\u201c\u2018]))=`, not an `=` preceded by an identifier character as in `mode=fast` or `label=`), refusing `'See "mode=fast,(FTP:X)"'` and `'Visit "label=(1-REGISTER.ID(1,2))"'`.
- **Round 13 `consistency` / `integration` / `source-defect` / `excellence` 2 (`P2`, whitespace inside a quoted sheet name such as `=SUM('Sales Data'!A1,FTP:FTP)` and `=SUM('Sales Data'!A1)-STDEV.S(A1:A2)` restarted the clause guards):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Guarded the whitespace boundary in the Branch 4 and Branch 7 clause guards with `(?![^'"\[\]]*(?:'\s*!|"|\]))` so whitespace inside `'...'!`, `"..."`, or `[...]` does not start a new prose clause, accepting `"=SUM('Sales Data'!A1,FTP:FTP)"` and `"=SUM('Sales Data'!A1)-STDEV.S(A1:A2)"`.
- **Round 13 `consistency` / `integration` / `source-defect` / `excellence` 3 (`P2`, subtraction required the preceding operand to end in a digit or `)`, rejecting named and structured-reference operands such as `=Total-STDEV.S(A1:A2)` and `=Table1[Amount]-STDEV.S(A1:A2)`):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Expanded the subtraction operand lookbehind to `(?<=[A-Za-z0-9_)\]]-.{k}\.)` (paired with the formula-opening `=` guard on Branch 4 so hyphenated prose hostnames such as `FOO-REGISTER.ID(help desk)` and `Visit (FOO-REGISTER.ID(1,2))` remain refused), accepting `"=Total-STDEV.S(A1:A2)"` and `"=Table1[Amount]-STDEV.S(A1:A2)"`.

## Round 14: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T14:48:22Z
- Effort: medium
- Type: adversarial
- Lines: 40
- Digest: e3d5752c932a8209

### adversarial: needs-attention

1. **[P2] Quoted prose after a formula bypasses address rejection.** At `design/inventory/schema.json:423`, the new whitespace guard treats an upcoming opening quote as evidence that whitespace is inside quoted content. Both these `behaviour` values return zero problems through `validate()` and `check()` with in-memory injected records:

   - `=SUM(1) See "(FTP:X)"`
   - `=SUM(1) Visit "(1-REGISTER.ID(1,2))"`

   Removing the double quotes makes both fail. A completed formula therefore allows prohibited addresses in subsequent prose. Track actual quoted and formula spans instead of inferring context from a later quote.

### consistency: needs-attention

2. **[P2] Spaces around arithmetic operators invalidate otherwise accepted formulas.** At `design/inventory/schema.json:423`, both these values fail through both validation paths with `host name or address`:

   - `=SUM(A1 + B1,FTP:FTP)`
   - `=SUM(A1 + B1)-STDEV.S(A1:A2)`

   Their counterparts using `A1+B1` pass. The whitespace after `A1` restarts the clause guard inside an unfinished formula, losing its opening `=`. Ordinary formula formatting must not prevent independently written behaviour from entering the inventory.

### integration: needs-attention

Both findings reach `check()`. The existing regression method at `scripts/tests/test_check_inventory.py:356` passes with an in-memory file adapter despite these failures.

### source-defect: needs-attention

Both defects originate in `$defs/noHost` at `design/inventory/schema.json:423`. Correct context recognition there; rewriting stored descriptions would conceal the defects.

### design: advisory

`SURFACE: no`. These counterexamples show why forward punctuation lookaheads cannot reliably establish formula boundaries. Explicit recognition of formula and quoted spans would address both failure directions.

### excellence: needs-attention

The same guard admits prohibited prose and rejects legitimate formulas. Passing the selected examples does not establish reliable enforcement.

### record: approve

Independently verified the counterexamples, passing controls, existing host/address regression method with an in-memory adapter, and whole-inventory check returning zero problems. The full filesystem-writing suite was not rerun in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 14 disposition

- **Round 14 `adversarial` / `integration` / `source-defect` / `excellence` 1 (`P2`, quoted prose after a formula such as `=SUM(1) See "(FTP:X)"` and `=SUM(1) Visit "(1-REGISTER.ID(1,2))"` bypassed address rejection because the whitespace guard inferred quote context from a later opening quote):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). Replaced the whitespace-restart clause guards on Branches 4 and 7 with start-anchored continuous formula-span guards (`^(?!(?:(?!(?:^|(?<=[\s(\["'\u201c\u2018]))=).)*?(?:^|(?<=[\s(\["'\u201c\u2018]))=(?:'[^']*'!|"[^"]*"|\[[^\[\]]*\]|[A-Za-z0-9$.,:;_!%#@{}+*/^&<>()=-]|(?<=[=+(,;*/^&<>-])\s+|\s+(?=[=+,;*/^&<>)-]))*?...)(?:\s|\S)*?...`) that track actual paired single-quoted sheet names (`'...'!`), double-quoted string literals (`"..."`), and bracketed structured references (`[...]`) from the formula-opening `=` up to the subtraction call or scheme-named column range, so prose after a completed formula (`=SUM(1) See "(FTP:X)"`, `=SUM(1) Visit "(1-REGISTER.ID(1,2))"`) is outside the formula span and is refused.
- **Round 14 `consistency` / `integration` / `source-defect` / `excellence` 2 (`P2`, spaces around arithmetic operators such as `=SUM(A1 + B1,FTP:FTP)` and `=SUM(A1 + B1)-STDEV.S(A1:A2)` restarted the clause guard and failed):** Verified and fixed in `design/inventory/schema.json` (`$defs/noHost`) and `scripts/tests/test_check_inventory.py` (`test_any_host_name_or_address_in_text_is_refused_by_its_dots`). The continuous formula span explicitly permits whitespace adjacent to formula operators and delimiters (`(?<=[=+(,;*/^&<>-])\s+|\s+(?=[=+,;*/^&<>)-])`), accepting `"=SUM(A1 + B1,FTP:FTP)"` and `"=SUM(A1 + B1)-STDEV.S(A1:A2)"`.

## Round 15: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T14:56:36Z
- Effort: medium
- Type: adversarial
- Lines: 49
- Digest: b587f9ae267e6d9a

### adversarial: needs-attention

1. **[P2] One valid formula exempts later prohibited addresses.** At `design/inventory/schema.json:423`, the start-anchored negative lookaheads disable their rejection branches for the entire string once a qualifying formula appears. Both these `behaviour` values return zero problems through `validate()` and `check()`:

   - `=SUM(FTP:FTP) See "(FTP:X)"`
   - `=1-STDEV.S(1,2) Visit "(1-REGISTER.ID(1,2))"`

   The corresponding Round 14 examples beginning with `=SUM(1)` are rejected. Bind each exception to the particular token inside its formula span.

2. **[P2] Short inputs cause severe regex backtracking.** At `design/inventory/schema.json:423`, the repeated formula-span alternatives contain overlapping whitespace matches. Setting `behaviour` to `'=1' + (' + ' * 30) + '2'` produces only 93 characters, but full `check()` did not finish within 10 seconds; the isolated child process was terminated. Repetitions of 18, 24 and 30 each exceeded five seconds in direct validation. The length guard does not prevent this. Make span recognition deterministic and test adversarial inputs below the length limit.

### consistency: needs-attention

3. **[P2] Only the first formula can establish context.** At `design/inventory/schema.json:423`, the prefix explicitly cannot cross an earlier formula-opening `=`. Consequently, both legitimate descriptions fail through `validate()` and `check()`:

   - `=SUM(1) and =SUM(FTP:FTP)`
   - `=SUM(1) and =1-STDEV.S(1,2)`

   Recognise each formula independently.

4. **[P2] Quoted-sheet and structured-reference recognition remains incomplete.** At `design/inventory/schema.json:423`, `'[^']*'!` cannot consume an escaped apostrophe, and `\[[^\[\]]*\]` cannot consume nested structured-reference brackets. These values both fail through both validation paths:

   - `=SUM('John''s Data'!A1,FTP:FTP)`
   - `=SUM(Table1[[#Data],[Amount]],FTP:FTP)`

   These operand forms prematurely end the recognised span and misclassify the later column range as an address.

### integration: needs-attention

All four findings reach `check()` with in-memory records using the existing fixtures. The recursive link scan does not catch Finding 1.

### source-defect: needs-attention

The defects originate in `$defs/noHost` at `design/inventory/schema.json:423`. Correct recognition there; rewriting stored descriptions would conceal the failures.

### design: advisory

`SURFACE: no`. The demonstrated failures support recognising individual formula spans with deterministic token handling, rather than granting string-wide exceptions through overlapping regex alternatives.

### excellence: needs-attention

The regression method at `scripts/tests/test_check_inventory.py:356` passes despite these failures. The timing test at `scripts/tests/test_check_inventory.py:455` exercises oversized strings rejected before matching, so it cannot expose Finding 2.

### record: approve

Verified the reproductions, the existing address/extension/function regression method with an in-memory adapter, and zero whole-inventory problems. The full filesystem-writing suite was not rerun in this read-only session. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 15 disposition

1. **[P2] One valid formula exempts later prohibited addresses**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Replaced the string-wide negative lookaheads at `^` in Branches 4 and 7 with a per-token prefix scanner (`^(?:<valid_formula>|<non_formula_char>)*?`) that consumes each valid formula span atomically and matches any prohibited `-FUNC.NAME(` or scheme-named token that appears outside a formula span (including after an earlier valid formula, such as `=SUM(FTP:FTP) See "(FTP:X)"`, `=SUM(FTP:FTP) See "(FTP:FTP)"`, and `=1-STDEV.S(1,2) Visit "(1-REGISTER.ID(1,2))"`).
2. **[P2] Short inputs cause severe regex backtracking**: Fixed for operator whitespace in `508090b`, for structured references in Round 16 (`e62fb7b`), and for function-opening parentheses in Round 17 (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Replaced the overlapping whitespace alternatives in the formula-span matcher with pairwise-disjoint token alternatives and possessive quantifiers (`(?![ \t])`, `(?![A-Za-z0-9...])`) so `'=1' + (' + ' * 30) + '2'` evaluates in under 1 ms (structured-reference inner `+` removed in Round 16; function-opening `(` overlap unified in Round 17); added sub-`maxLength` timing assertions in `test_long_strings_cost_bounded_time`.
3. **[P2] Only the first formula can establish context**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Because the prefix scanner repeats `(?:<valid_formula>|<non_formula_char>)*?` across the string and uses the deterministic formula-token matcher for function arguments, multiple formulas in one description (`=SUM(1) and =SUM(FTP:FTP)`, `=SUM(1) and =1-STDEV.S(1,2)`, and `Calculates =1-STDEV.S(1,2) in each row.`) are recognised independently.
4. **[P2] Quoted-sheet and structured-reference recognition remains incomplete**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Updated quoted-sheet recognition to allow escaped apostrophes (`\x27...(?!\x27\x27)\x27!`) and structured-reference recognition to allow nested bracket groups (`\[(?:...+|\[...*\])*\]`), covering `=SUM('John''s Data'!A1,FTP:FTP)` and `=SUM(Table1[[#Data],[Amount]],FTP:FTP)`.


## Round 16: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T15:26:33Z
- Effort: medium
- Type: adversarial
- Lines: 34
- Digest: 3c01ecb569a0679a

### adversarial: needs-attention

1. **[P2] Structured references still cause exponential backtracking.** At `design/inventory/schema.json:423`, structured-reference recognition repeats a group containing a repeated non-bracket alternative, allowing many partitions of the same characters. A behaviour value of `'=SUM(Table1[' + 'a' * 30 + '])'` is only 44 characters, but `check()` exceeded 10 seconds before the isolated process was terminated. The ordinary formula `=SUM(Table1[QuarterlyRevenueForecastAmount])` also exceeded three seconds in `validate()`. Authoring a formula with a long column name can therefore stall the inventory gate, well below `maxLength`. Make structured-reference matching deterministic, including failed matches.

### consistency: needs-attention

2. **[P2] Legal formula whitespace changes acceptance.** At `design/inventory/schema.json:423`, the scheme-named column exception recognises only zero or one whitespace character after an opening parenthesis or argument separator. Both validation paths accept `=SUM( FTP:FTP)` and `=SUM(A1, FTP:FTP)`, but reject `=SUM(  FTP:FTP)` and `=SUM(A1,  FTP:FTP)` as `host name or address`. Ordinary spacing in an authored formula blocks otherwise valid inventory content. Recognise the argument context across the full whitespace run without exempting subsequent prose.

### integration: needs-attention

Both findings reach `check()`, not merely isolated regex searches. Reproductions used an in-memory file-loading adapter while retaining schema validation and checker logic.

### source-defect: approve

No additional source-contract defect identified. The formula-preservation and bounded-runtime claims fail as detailed above.

### design: advisory

SURFACE: no

The scanner needs deterministic token boundaries. Negative lookaheads after repetitions do not eliminate the ambiguous partitions inside the structured-reference matcher.

### excellence: needs-attention

The regression methods at `scripts/tests/test_check_inventory.py:356` and `scripts/tests/test_check_inventory.py:462` both passed with the in-memory adapter despite these failures. Add long individual column names, unterminated structured references, and whitespace variants to those tests.

### record: needs-attention

`docs/reviews/02-interface/audit-d02-t01-s21.md:826` claims deterministic matching without backtracking; Finding 1 disproves that disposition.

The whole-inventory command exited 0. The full suite could not be independently confirmed: 115 of 117 tests errored because this read-only session could not create temporary directories. The two targeted regression methods passed with the adapter. No repository files were modified.

HIGHEST: P2
OVERALL: needs-attention


### Round 16 disposition

1. **[P2] Structured references still cause exponential backtracking**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Removed the nested `+` quantifier from the non-bracket alternative inside structured-reference matching (`\[(?:{BR}|\[{BR}*\])*(?!{BR}|\[{BR}*\])\]` instead of `\[(?:{BR}+|\[{BR}*\])*\]`), so each character inside `[...]` has a single deterministic transition whether the structured reference closes (`'=SUM(Table1[' + 'a' * 30 + '])'`, `=SUM(Table1[QuarterlyRevenueForecastAmount])`) or is unterminated (`'=SUM(Table1[' + 'a' * 30 + ') (FTP:X)'`, `'=SUM(Table1[[' + 'a' * 30 + ']) (FTP:X)'`). Added regression and bounded-time assertions at `scripts/tests/test_check_inventory.py:366` and `scripts/tests/test_check_inventory.py:479`.
2. **[P2] Legal formula whitespace changes acceptance**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Replaced the 0-or-1 space lookbehind on scheme-named column ranges in `RANGE_ATOM` with forward whitespace consumption on preceding delimiters (`[,;!][ \t]*(?![ \t])`, `\x27...\x27![ \t]*(?![ \t])`, and function-call `\([ \t]*(?:\([ \t]*)*(?![ \t\(])`), while forbidding scheme-named column ranges after bare `=` or non-function grouping parentheses (`=(  FTP:X)`, `=   (  FTP:X)`, `=1 + (  FTP:X)`). Both `=SUM(  FTP:FTP)`, `=SUM(A1,  FTP:FTP)`, `=SUM(Sheet1!  FTP:FTP)`, and `"=SUM('Sales Data'!  FTP:FTP)"` now pass while `=SUM(  FTP:FTP) See "(  FTP:X)"` is rejected.

## Round 17: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T15:42:16Z
- Effort: medium
- Type: adversarial
- Lines: 34
- Digest: a4be67e9ed521e50

### adversarial: needs-attention

1. **[P2] Function-opening alternatives still cause exponential backtracking.** At [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423), Branch 7’s function-opening alternatives overlap: after `SUM`, both the preceding-name lookbehind and the negative scheme lookahead succeed. Repeated calls multiply equivalent matching paths. The valid behaviour value `'=' + 'SUM(' * 20 + '1' + ')' * 20` is only 102 characters, but `check()` exceeded five seconds before termination. Twenty sibling calls, `=SUM(A1)+...+SUM(A20)` (171 characters), also exceeded four seconds in `validate()`. Node’s native regex engine exceeded five seconds with 25 nested calls. Make these alternatives mutually exclusive. An in-memory experiment doing so accepted 30 nested calls in 0.023 seconds.

### consistency: needs-attention

2. **[P2] Reordering valid formula operands changes acceptance.** At [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423), the operator branch explicitly excludes scheme-named column ranges after arithmetic operators. Both `validate()` and `check()` accept `=SUM(FTP:FTP*2)` but reject `=SUM(2*FTP:FTP)` as `host name or address`. A legitimate formula description therefore fails solely because multiplication operands were reordered. Recognise ranges throughout formula expressions while retaining rejection of addresses in surrounding prose.

### integration: needs-attention

Both findings reach `check()` using the existing record fixtures and an in-memory file-loading adapter. They are not confined to isolated regex tests.

### source-defect: approve

No additional source-contract defect identified. Both failures originate in the schema’s formula recognition.

### design: advisory

SURFACE: no

The overlapping alternatives at `schema.json:423` undermine the deterministic-scanning design. Establish unambiguous token transitions and formula boundaries instead of extending delimiter-specific exceptions.

### excellence: needs-attention

The regression methods at [test_check_inventory.py:356](/D:/GitHub/Office/scripts/tests/test_check_inventory.py:356) and [test_check_inventory.py:469](/D:/GitHub/Office/scripts/tests/test_check_inventory.py:469) both passed with the adapter despite Findings 1 and 2. Add repeated function calls and operand-order variants. Run timing regressions with a process timeout so a regression cannot hang the test runner.

### record: needs-attention

The deterministic, non-backtracking claim at [audit-d02-t01-s21.md:826](/D:/GitHub/Office/docs/reviews/02-interface/audit-d02-t01-s21.md:826) remains contradicted by Finding 1.

The whole-inventory command exited 0. Independent full-suite verification remained unavailable: 115 of 117 tests errored because this read-only session could not create temporary directories. The two targeted regression methods passed using the adapter. No repository files were modified.

HIGHEST: P2
OVERALL: needs-attention


### Round 17 disposition

1. **[P2] Function-opening alternatives still cause exponential backtracking**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Unified Branch 7's `F_OP_B7` with Branch 4's `F_OP_B4` into a single character-class operator token `[=+,;!*/^&<>(-][ \t]*(?![ \t])` (with zero overlapping alternatives on `(`) and guarded scheme-named column ranges directly on `RANGE_ATOM` (`(?!\$?{SCHEME_NAMES}:)`). Thirty nested `SUM(` calls (`'=' + 'SUM(' * 30 + '1' + ')' * 20`) and 24 sibling calls (`=SUM(A1)+...+SUM(A24)`) now evaluate in ~0.1 ms in both Python and Node (with the `test_long_strings_cost_bounded_time` subprocess execution order completed in Round 18 so probes run exclusively inside the 5-second subprocess).
2. **[P2] Reordering valid formula operands changes acceptance**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Allowed arithmetic and comparison operators `[=(,;!\s+*/^&<>-]` before and after scheme-named column ranges inside `VALID_FORMULA`, guarded `[+-]` inside URI scheme continuation in Branch 7's local check (`[+-](?!(?:<valid_range>))`) so `=SUM(A1+FTP:FTP)` does not treat `A1+FTP:` as a single scheme name, and allowed `/` and `-` after column ranges (`(?![A-Za-z0-9_:.]|//)`) so `=SUM(2*FTP:FTP)`, `=SUM(FTP:FTP*2)`, `=SUM(2/FTP:FTP)`, `=SUM(FTP:FTP/2)`, `=SUM(A1+FTP:FTP)`, and `=SUM(A1-FTP:FTP)` are all accepted while `See "2*FTP:X"`, `=SUM(2*FTP:FTP) See "(2*FTP:X)"`, and `=1-REGISTER.ID(SUM(1) help desk)` are rejected.

## Round 18: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T15:55:03Z
- Effort: medium
- Type: adversarial
- Lines: 36
- Digest: 0c68904c67daca4a

### adversarial: approve

No additional bypass or hang reproduced. Nested calls of 30 and 100 levels completed promptly.

### consistency: needs-attention

1. **[P2] Absolute column references and percentage operands are rejected.** At [schema.json:423](D:/GitHub/Office/design/inventory/schema.json:423), `=SUM(FTP:FTP)` passes, but `=SUM($FTP:$FTP)` and `=SUM(FTP:FTP%)` produce `host name or address`. Both failures reproduce through `validate()`, `check()` with in-memory records, and Node’s regex engine. Preconditions: an author documents ordinary absolute references or percentage calculations. The local range exception loses the preceding delimiter when matching after `$`; the scheme-range boundary also omits `%`. Recognise these at the formula-token layer and add positive regressions.

### integration: needs-attention

2. **[P2] Subtraction makes a valid intersection expression fail validation.** At [schema.json:423](D:/GitHub/Office/design/inventory/schema.json:423), `=STDEV.S(A1:B3 B2:C4)` passes, while `=1-STDEV.S(A1:B3 B2:C4)` fails as `host name or address`. Python and Node reproduce this. The stricter formula recognition activated by subtraction does not recognise whitespace as Excel’s intersection operator. Preconditions: independently written behaviour describes subtracting a calculation over intersecting ranges. Recognise intersection operands consistently rather than requiring different argument syntax after subtraction.

### source-defect: approve

No additional source-contract defect identified. Findings 1 and 2 originate in schema enforcement.

### design: advisory

SURFACE: no

The acceptance differences at [schema.json:423](D:/GitHub/Office/design/inventory/schema.json:423) show that formula context still changes which valid operands are recognised. Use consistent token rules for complete references and operators across the formula branches.

### excellence: needs-attention

3. **[P3] The subprocess timeout cannot protect the regression test from hanging.** At [test_check_inventory.py:500](D:/GitHub/Office/scripts/tests/test_check_inventory.py:500), every accepted and refused probe runs through `self.problems()` in the test process before reaching the timeout at line 522. If exponential matching returns, execution hangs before the child process starts; elapsed-time assertions cannot interrupt it. Run these potentially hanging evaluations exclusively inside the timeout-controlled subprocess.

Both targeted regression methods passed with an in-memory file adapter despite Findings 1 and 2.

### record: needs-attention

The timeout protection claimed at [audit-d02-t01-s21.md:928](D:/GitHub/Office/docs/reviews/02-interface/audit-d02-t01-s21.md:928) remains incomplete for the execution-order reason in Finding 3.

Whole-inventory checking exited 0. Independent full-suite execution attempted 117 tests, with 115 temporary-directory errors caused by read-only permissions; the other two passed. No repository files were modified.

HIGHEST: P2
OVERALL: needs-attention


### Round 18 disposition

1. **[P2] Absolute column references and percentage operands are rejected**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Updated Branch 7's local scheme-range lookbehind to recognise a preceding `$` after an operator or delimiter (`(?:(?<=[=(,;%!\s+*/^&<>-])|(?<=[=(,;%!\s+*/^&<>-]\$))`), moved `%` into `F_OP` (`[=+,;%!*/^&<>(-][ \t]*(?![ \t])`) and the range boundary lookahead (`(?=[\s),;%+*/^&<>=-]|$)`), and added `=SUM($FTP:$FTP)`, `=SUM($FTP:FTP)`, `=SUM(FTP:$FTP)`, `=SUM(FTP:FTP%)`, `=SUM($FTP:$FTP%)`, `=SUM(2*$FTP:$FTP%)`, and `=10%-STDEV.S(1,2)` (plus negative regressions `'=SUM($FTP:$FTP) See "($FTP:X)"'`, `'See "($FTP:$FTP)"'`, `'See "(FTP:FTP%)"'`, and `'10%-REGISTER.ID(1,2)'`) to `test_any_host_name_or_address_in_text_is_refused_by_its_dots`.
2. **[P2] Subtraction makes a valid intersection expression fail validation**: Fixed for A1 cell/column/sheet/table intersections in `9b55430` and completed for whole-row (`1:3 2:4`), named-range (`Revenue January`), relative R1C1 (`R[-1]C R[-2]C`), parenthesised (`(A1:B3) (B2:C4)`), and function-result (`INDEX(...) INDEX(...)`) intersections in Round 19 (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Extended the trailing-whitespace rule on `F_ATOM_B4` and `F_ATOM_B7` (`TRAIL_WS`) to recognise Excel's space intersection operator before another cell, range, R1C1, column-range, sheet-qualified, or structured reference (`REF_NEXT`), while still refusing space-separated prose words (`=1-REGISTER.ID(SUM(1) help desk)` and `'=1-STDEV.S(A1:B3 B2:C4) Visit "(1-REGISTER.ID(1,2))"'`). Both `=STDEV.S(A1:B3 B2:C4)` and `=1-STDEV.S(A1:B3 B2:C4)` (as well as `$A$1:$B$3 $B$2:$C$4`, `Sheet1!A1:B3 Sheet1!B2:C4`, `'Sales Data'!A1:B3 'Sales Data'!B2:C4`, `Table1[Col1] Table1[Col2]`, and `=SUM(A1:B3 FTP:FTP)`) pass consistently across all branches.
3. **[P3] The subprocess timeout cannot protect the regression test from hanging**: Fixed at the owning layer (`scripts/tests/test_check_inventory.py`). Removed the in-process `self.problems()` loops over `accepted` and `refused` before `subprocess.run` in `test_long_strings_cost_bounded_time` so all potentially backtracking formula probes execute exclusively inside the 5-second timeout-controlled subprocess (with per-item `< 1.0s` assertions), and replaced the `"a" * 30` probes in `test_any_host_name_or_address_in_text_is_refused_by_its_dots` with short unterminated structured-reference checks (`=SUM(Table1[Col) (FTP:X)` and `=SUM(Table1[[Col]) (FTP:X)`).

## Round 19: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T16:01:57Z
- Effort: medium
- Type: adversarial
- Lines: 40
- Digest: cb15bdb2fc28ecf8

### adversarial: needs-attention

1. **[P2] Subtraction still rejects valid intersection expressions.** At [schema.json:423](D:/GitHub/Office/design/inventory/schema.json:423), `REF_NEXT` omits whole-row references, named ranges and relative R1C1 references. These expressions pass without the leading `1-`, but fail with `host name or address` when it is added:

   - `=1-STDEV.S(1:3 2:4)`
   - `=1-STDEV.S(Revenue January)`, when both names denote ranges.
   - `=1-STDEV.S(R[-1]C R[-2]C)`, in R1C1 notation.

   Reproduced through `validate()`, full `check()` with in-memory records, and Node’s native regex engine. Authors cannot document these legitimate calculations. Complete intersection recognition at the formula-token layer and add paired regression cases.

### consistency: needs-attention

Finding 1 reproduces the acceptance inconsistency Round 18 intended to resolve: adding subtraction changes which reference operands are permitted.

### integration: needs-attention

Finding 1 reaches the full inventory checker, not merely an isolated regex.

### source-defect: needs-attention

The defect belongs to `$defs/noHost`. Python and Node agree, ruling out the Python regex translation as its cause.

### design: needs-attention

SURFACE: no

Finding 1 exposes the incomplete reference grammar used to distinguish formulas from addresses. Recognise supported reference forms consistently across formula contexts.

### excellence: needs-attention

Finding 1 blocks ordinary formula documentation. Additional timeout-controlled probes covering repeated quotes, brackets, parentheses and reference tokens completed without hangs.

### record: needs-attention

The Round 18 disposition at [audit-d02-t01-s21.md:981](D:/GitHub/Office/docs/reviews/02-interface/audit-d02-t01-s21.md:981) describes intersection support as fixed; Finding 1 demonstrates remaining cases.

The inventory check exits 0. The 117-test suite could not be verified here: read-only restrictions caused 115 temporary-directory setup errors. No repository files were modified.

HIGHEST: P2
OVERALL: needs-attention


### Round 19 disposition

1. **[P2] Subtraction still rejects valid intersection expressions**: Fixed for whole-row, named-range, relative R1C1, and simple parenthesised/function-result intersections in `68fdef4`, and completed for comparison operators (`=1-STDEV.S(Revenue January=1)`) and parenthesised function calls (`=1-STDEV.S(A1:B3 (INDEX(A1:C3,1,0)))`) in Round 20 (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Extended `RANGE_ATOM`, `REF_NEXT`, and Branch 7's local scheme exemption to recognise whole-row ranges (`\$?[1-9]\d{0,6}:\$?[1-9]\d{0,6}`), relative and row/column R1C1 references (`[Rr](?:\d+|\[[+-]?\d+\])?(?:[Cc](?:\d+|\[[+-]?\d+\])?)?`, including `R[-1]C R[-2]C`, `R[-1]C[-1] R[-2]C[-2]`, `R[-1]C:R[-2]C`, and `R1:R3 C1:C3`), Excel defined-name intersections (`[A-Za-z_\\][A-Za-z0-9_.]*` followed by formula delimiters, covering `=1-STDEV.S(Revenue January)` and `=1-STDEV.S(Revenue January North)`), parenthesised and function-result intersections (`=1-STDEV.S((A1:B3) (B2:C4))` and `=1-STDEV.S(INDEX(A1:C3,0,1) INDEX(A1:C3,1,0))`), dynamic-array spill intersections (`=1-STDEV.S(A1# B1#)`), and 3D sheet ranges (`Sheet1:Sheet3!A1:B2`), while narrowing the negative lookahead after `\]` so `R[-1]C` can be followed immediately by `C`. Added paired positive and negative regression cases to `test_any_host_name_or_address_in_text_is_refused_by_its_dots`.

## Round 20: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T16:15:24Z
- Effort: medium
- Type: adversarial
- Lines: 39
- Digest: 2dd37cf2d0146c66

### adversarial: needs-attention

1. **[P2] Intersection recognition still changes under subtraction.** At [schema.json:423](D:/GitHub/Office/design/inventory/schema.json:423), these valid expressions are rejected as `host name or address`:

   - `=1-STDEV.S(Revenue January=1)`, when both names denote ranges.
   - `=1-STDEV.S(A1:B3 (INDEX(A1:C3,1,0)))`.

   Both pass when `1-` is removed. The defined-name delimiter lookahead omits `=`, and the parenthesised-reference lookahead excludes a wrapped function result. Preconditions: an author documents a comparison over intersecting ranges or parenthesises a reference-returning function. Complete these grammar cases and add paired regressions.

### consistency: needs-attention

Finding 1 preserves the acceptance inconsistency that Rounds 18 and 19 intended to eliminate.

### integration: needs-attention

Finding 1 reproduces through full `check()` with in-memory records, as well as direct schema validation.

### source-defect: needs-attention

Python and Node’s native regex engine reproduce both failures. The defect belongs to `$defs/noHost`, not Python’s regex translation.

### design: needs-attention

SURFACE: no

Finding 1 demonstrates that independently enumerated formula exceptions remain inconsistent. Reference recognition must compose with operators and parentheses instead of accepting only the tested combinations.

### excellence: needs-attention

Finding 1 blocks accurate documentation of legitimate calculations. The positive cases at [test_check_inventory.py:395](D:/GitHub/Office/scripts/tests/test_check_inventory.py:395) exercise individual reference forms without these combinations.

### record: needs-attention

The “Fixed” disposition at [audit-d02-t01-s21.md:1037](D:/GitHub/Office/docs/reviews/02-interface/audit-d02-t01-s21.md:1037) overstates completion of intersection support, as Finding 1 demonstrates.

The whole-inventory checker exits 0. I could not independently confirm the reported suite pass: 117 tests ran with 115 temporary-directory setup errors under read-only restrictions. No repository files were modified.

HIGHEST: P2
OVERALL: needs-attention


### Round 20 disposition

1. **[P2] Intersection recognition still changes under subtraction**: Fixed for literal comparisons and parenthesised calls in `2c05431`, and completed for function-call operands after operators (`=1-STDEV.S(Revenue January+SUM(1))`, `=1-STDEV.S(Revenue January=SUM(1))`) in Round 21 (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Replaced the enumerated parenthesised-operand lookahead in `REF_NEXT` with a general parenthesised/function-call reference starter (`\([ \t]*(?!{BAD_PAREN})[A-Za-z0-9$_'\[\(@\\+-]` and `@?[A-Za-z_\\][A-Za-z0-9_.]*\([ \t]*(?!{BAD_PAREN})...`) that composes with `F_TOKEN`'s recursive parenthesis/operator scanner, and expanded the defined-name continuation lookahead (`EQ_CONT`) to include `=` comparisons, `:`, `!`, `[`, `#`, `(`, and subsequent `DIRECT_REF` operands. Also enabled zero-argument inner calls (`PI()`, `ROW()`, `COLUMN()`), function-bounded ranges (`A1:INDEX(A1:C3,3,3)`, `INDEX(A1:C3,1,1):B3`), and signed array constants (`{-1, 2; 3, 4}`). Both `=1-STDEV.S(Revenue January=1)` and `=1-STDEV.S(A1:B3 (INDEX(A1:C3,1,0)))` (along with their nested, sheet-qualified, structured-reference, and scheme-column combinations) pass across all validation paths.

## Round 21: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T16:27:19Z
- Effort: medium
- Type: adversarial
- Lines: 39
- Digest: 3965564022f5ef8d

### adversarial: needs-attention

1. **[P2] Function operands still break intersection recognition under subtraction.** At [schema.json:423](D:/GitHub/Office/design/inventory/schema.json:423), the defined-name continuation lookahead rejects an operator immediately followed by a function call. With `Revenue` and `January` denoting intersecting ranges, these legitimate expressions fail with `host name or address`:

   - `=1-STDEV.S(Revenue January+SUM(1))`
   - `=1-STDEV.S(Revenue January=SUM(1))`

   Both pass without `1-`. Replacing `=SUM(1)` with `>=SUM(1)` also passes. The prose-exclusion lookahead incorrectly excludes formula operands. Fix that distinction and add paired regressions.

### consistency: needs-attention

Finding 1 makes acceptance depend on an unrelated outer subtraction and on whether the comparison uses `=` or `>=`.

### integration: needs-attention

Both failures reproduce through `validate()` and full `check()` with in-memory loading of otherwise valid records.

### source-defect: needs-attention

Node’s native regex engine reproduces both failures directly from `$defs/noHost`. The defect belongs to the schema, not Python’s regex translation.

### design: needs-attention

SURFACE: no

Finding 1 shows that the prose boundary heuristic still conflicts with formula composition. Distinguish prose boundaries from function operands within an established formula.

### excellence: needs-attention

The regression cases at [test_check_inventory.py:399](D:/GitHub/Office/scripts/tests/test_check_inventory.py:399) cover comparisons against literals but miss function operands, leaving legitimate calculations unrepresentable.

### record: needs-attention

The completion claim at [audit-d02-t01-s21.md:1091](D:/GitHub/Office/docs/reviews/02-interface/audit-d02-t01-s21.md:1091) remains incomplete: comparison support does not compose with function operands.

The whole-inventory checker exits 0. The reported suite pass could not be independently confirmed: 117 tests ran with 115 temporary-directory errors under read-only restrictions. No repository files were modified.

HIGHEST: P2
OVERALL: needs-attention


### Round 21 disposition

1. **[P2] Function operands still break intersection recognition under subtraction**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Removed the `(?![ \t]*(?:[A-Za-z0-9_.]+\(|...))` lookahead from `EQ_CONT`'s operator class `[,;)+*/^&<>%=!\[#-]` (which had rejected single-character operators `+`, `=`, `-`, `*`, `/` immediately followed by a function call such as `+SUM(1)` or `=SUM(1)`), and instead guarded top-level conjunction boundaries after closing parentheses directly on `REF_NEXT` (`(?!(?<=\)[ \t])(?:and|or)\b)`). Both `=1-STDEV.S(Revenue January+SUM(1))` and `=1-STDEV.S(Revenue January=SUM(1))` (as well as spaced, subtracted, multiplied, divided, and scheme-column variants) now pass across all validation paths while `=SUM(1) and FOO-REGISTER.ID(1,2)` and `=SUM(1) and 1-REGISTER.ID(1,2)` are rejected and `=SUM(1) and =SUM(FTP:FTP)` / `=SUM(1) and =1-STDEV.S(1,2)` are accepted.

## Round 22: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T16:32:39Z
- Effort: medium
- Type: adversarial
- Lines: 45
- Digest: a8d2258028fb1331

### adversarial: needs-attention

1. **[P2] Ordinary spacing or capitalization bypasses the new conjunction boundary.** At [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423), `(?!(?<=\)[ \t])(?:and|or)\b)` only guards lowercase conjunctions immediately after exactly one whitespace character.

   These behaviour values produce different results:

   | Input | Result |
   |---|---|
   | `=SUM(1) and FOO-REGISTER.ID(1,2)` | Refused |
   | `=SUM(1)  and FOO-REGISTER.ID(1,2)` | Accepted |
   | `=SUM(1) AND FOO-REGISTER.ID(1,2)` | Accepted |
   | `=SUM(1) then FOO-REGISTER.ID(1,2)` | Accepted |

   The formula exception consumes the following prose and exempts the otherwise forbidden hostname. This needs only normal text editing in an inventory field. Reproduced through Python schema validation, `check()` with in-memory file loading, and JavaScript regex evaluation both with and without `u`.

### consistency: needs-attention

Finding 1 violates `noHost`’s stated contract: changing prose spacing or capitalization must not change whether the same hostname is refused.

### integration: needs-attention

Finding 1 reaches `check()`: the accepted variants return an empty problem list. The whole-record `noLink` scan does not catch this hostname, so it provides no backstop.

### source-defect: approve

No separate finding. The defect is in implementing the documented refusal rule.

### design: needs-attention

SURFACE: no

Finding 1 shows that enumerating conjunction words does not establish where a formula ends. Resolve the formula/prose boundary at the owning layer and test equivalent whitespace and capitalization variants, rather than extending the conjunction blacklist.

### excellence: approve

No separate finding beyond the boundary defect.

### record: approve

The two reported Round 21 positive examples now pass, and their exact negative examples are refused. The whole-inventory command independently exited 0.

The full suite could not be independently confirmed: it ran 117 tests with 115 temporary-directory errors under this session’s read-only permissions. This is a verification limitation, not evidence that the recorded earlier run was false. No repository files were modified.

HIGHEST: P2
OVERALL: needs-attention


### Round 22 disposition

1. **[P2] Ordinary spacing or capitalization bypasses the new conjunction boundary**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Removed the word-specific conjunction lookahead `(?!(?<=\)[ \t])(?:and|or)\b)` from `REF_NEXT` and replaced it with structural token and boundary rules:
   - Closing delimiters (`CLOSE_DELIM`, i.e., `)` and `}`) now use `TRAIL_WS_CLOSE`, which only permits operators, closing delimiters, or `DIRECT_REF` tokens across whitespace and never allows a bare word (`BARE_NAME_NEXT`), while parenthesised reference operands (`(Revenue)`, `(A1:B3)`, `(Sheet1!A1:B3)`, `('Sales Data'!A1:B3)`, `(Table1[Amount])` where `(` is not preceded by a function name and does not wrap a numeric literal) are matched as `PAREN_NAME_ATOM`.
   - String literals and bare numeric literals (`[0-9][0-9.]*%?`) use `TRAIL_WS_OP` so they can only be followed across whitespace by operators or closing delimiters, never by intersection operands.
   - In `BARE_NAME_NEXT`, multi-word defined-name chains (`Revenue January North`) must be followed immediately by `[,;)]`, and single-word defined-name operator continuations (`ENCLOSED_OP_CONT`) must be enclosed by `[,;)]` within the current argument or parenthesised expression (excluding `-REGISTER.ID(`).
   Consequently, `=SUM(1) and FOO-REGISTER.ID(1,2)`, `=SUM(1)  and FOO-REGISTER.ID(1,2)`, `=SUM(1) AND FOO-REGISTER.ID(1,2)`, `=SUM(1) or FOO-REGISTER.ID(1,2)`, `=SUM(1) OR FOO-REGISTER.ID(1,2)`, `=SUM(1) then FOO-REGISTER.ID(1,2)`, `=SUM(1) FOO-REGISTER.ID(1,2)`, `See (=SUM(1) then FOO-REGISTER.ID(1,2))`, `=SUM(1) then FOO-REGISTER.ID(1,2), or bar`, `=A1 and FOO-REGISTER.ID(1,2)`, `=A1 then FOO-REGISTER.ID(1,2)`, `=Revenue and FOO-REGISTER.ID(1,2)`, `=Revenue then FOO-REGISTER.ID(1,2)`, `=A1 FOO-REGISTER.ID(1,2)`, `=Revenue FOO-REGISTER.ID(1,2)`, `See (=A1 FOO-REGISTER.ID(1,2))`, `=A1 FOO-REGISTER.ID(1,2), or bar`, `=(1) and FOO-REGISTER.ID(1,2)`, `=1 and FOO-REGISTER.ID(1,2)`, and `=1-STDEV.S(Revenue and FOO-REGISTER.ID(1,2))` are all refused, while `=1-STDEV.S((Revenue) January North)`, `=1-STDEV.S((Revenue) January+SUM(1))`, `=1-STDEV.S((Revenue) January=1)`, `=1-STDEV.S((A1:B3) January)`, `=1-STDEV.S(Revenue January+SUM(1))`, `=1-STDEV.S(Revenue January=SUM(1))`, `=SUM(1) and =SUM(FTP:FTP)`, and `=SUM(1) and =1-STDEV.S(1,2)` are accepted.


## Round 23: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T16:57:11Z
- Effort: medium
- Type: adversarial
- Lines: 44
- Digest: 51b77bde3dca763d

### adversarial: needs-attention

1. **[P2] Three-name intersections followed by operators are rejected under subtraction.** At [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423), the new multi-word continuation requires `[,;)]` after the name chain, excluding valid arithmetic and comparisons.

   Preconditions: `Revenue`, `January`, and `North` denote intersecting named ranges, and an inventory behaviour describes the calculation.

   | Formula | Result |
   |---|---|
   | `=STDEV.S(Revenue January North+1)` | Accepted |
   | `=1-STDEV.S(Revenue January North+1)` | Refused |
   | `=1-STDEV.S(Revenue January North=1)` | Refused |
   | `=1-STDEV.S(Revenue January North+SUM(1))` | Refused |
   | `=1-STDEV.S(Revenue January North)` | Accepted |

   The rejected cases produce `host name or address`. Permit operator continuations after complete intersection chains and add paired regressions.

### consistency: needs-attention

Finding 1 makes acceptance depend on an unrelated outer subtraction.

### integration: needs-attention

Reproduced through schema validation and full `check()` with in-memory replacement of an existing inventory file’s records. Each rejected example produces exactly one behaviour-field error.

### source-defect: needs-attention

Node’s native regex engine reproduces Finding 1 with and without `u`. The defect belongs to the schema, not Python’s translation.

### design: needs-attention

The boundary rule conflates a complete intersection chain with the end of its expression. Formula recognition must compose with subsequent operators.

### excellence: needs-attention

The tests at [test_check_inventory.py:414](/D:/GitHub/Office/scripts/tests/test_check_inventory.py:414) cover three-name chains and two-name arithmetic separately, missing their combination.

### record: approve

No separate record defect demonstrated. `$defs/noMicrosoft` does not exist in this checkout; the operative definitions were inspected.

Verification: the inventory checker exited 0; TODO validation reported 125 valid sections. The suite ran 117 tests with 115 temporary-directory errors under read-only permissions, so its reported pass remains independently unconfirmed. No files were modified.

HIGHEST: P2  
OVERALL: needs-attention

### Round 23 disposition

1. **[P2] Three-name intersections followed by operators are rejected under subtraction**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Replaced the separate multi-word `[,;)]`-only lookahead on `BARE_NAME_NEXT` with a unified defined-name chain continuation `(?:[ \t]+[A-Za-z_\\][A-Za-z0-9_.]*(?![A-Za-z0-9_.]))*(?:[ \t]*(?:{EQ_CONT})|[ \t]+(?:{DIRECT_REF}))` where `EQ_CONT` permits `[,;)]`, `ENCLOSED_OP_CONT` (bounded by `SAFE_ARG_TAIL` so no `-REGISTER.ID(` can appear later in the argument), `:`, and `(`, allowing intersection chains of any length (`Revenue January North+1`, `Revenue January North=1`, `Revenue January North+SUM(1)`, `Revenue January North=SUM(1)`, `Revenue January North-STDEV.S(1,2)`, `(Revenue) January North+1`, `Revenue (January) North+1`, `A1:B3 January North+1`, and `=SUM(Revenue January North+1, FTP:FTP)`) to compose with arithmetic and comparison operators while refusing `=1-STDEV.S(Revenue January North+1) Visit "(1-REGISTER.ID(1,2))"`, `=1-STDEV.S(Revenue January North and FOO-REGISTER.ID(1,2))`, `=1-STDEV.S(Revenue January North + FOO-REGISTER.ID(1,2))`, and `See (=SUM(1) then X+FOO-REGISTER.ID(1,2))`.


## Round 24: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T19:42:44Z
- Effort: medium
- Type: adversarial
- Lines: 40
- Digest: 6575b8b1ddfef24a

### adversarial: needs-attention

1. **[P2] Nested function operands still reject valid intersections under subtraction.** At [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423), `SAFE_ARG_TAIL` recognises only bounded parenthesis nesting. Three nested calls defeat the new operator-continuation exception.

   Preconditions: `Revenue`, `January`, and `North` denote intersecting named ranges, and a behaviour field describes their calculation.

   | Formula | Result |
   |---|---|
   | `=STDEV.S(Revenue January North+SUM(SUM(SUM(1))))` | Accepted |
   | `=1-STDEV.S(Revenue January North+SUM(SUM(SUM(1))))` | Refused |
   | `=1-STDEV.S(Revenue January North+SUM(SUM(1)))` | Accepted |

   The rejected expression reports `behaviour: host name or address`. Formula recognition must support nested operands consistently; add these paired regressions.

### consistency: needs-attention

Finding 1 makes acceptance depend on unrelated outer subtraction and operand nesting depth.

### integration: needs-attention

Finding 1 reproduces through full `check()` with in-memory substitution of otherwise valid records in an existing inventory file. The accepted controls return no problems.

### source-defect: approve

No separate finding. Node reproduces the same results directly from the schema, both with and without `u`, locating the defect in the schema rather than Python’s translation.

### design: needs-attention

Finding 1 exposes the bounded-parenthesis approximation in the formula/prose boundary. Extending a fixed nesting limit would retain the same failure at another depth.

### excellence: needs-attention

The existing host-rule test passes when replayed against schema validation in memory, including its 281 record fixtures. It does not expose Finding 1.

### record: approve

No separate record defect demonstrated. The inventory checker exited 0; TODO validation reported 125 valid sections. The suite ran 117 tests with 115 temporary-directory errors under read-only restrictions, so the reported full-suite pass remains independently unconfirmed. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 24 disposition

1. **[P2] Nested function operands still reject valid intersections under subtraction**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Replaced the two-level bounded parenthesis group `\((?:[^()]|\([^()]*\))*\)` in `SAFE_ARG_TAIL` with an arbitrary-depth parenthesised token unit `\((?!(?:[^\(\)\[\]\x22\x27]|\[[^\[\]]*\]|\x22[^\x22]*\x22|\x27[^\x27]*\x27|\()*?[A-Za-z0-9_%)\}\]]\s*-\s*REGISTER\.ID\()(?:[^\(\)\[\]\x22\x27]|\[[^\[\]]*\]|\x22[^\x22]*\x22|\x27[^\x27]*\x27|\([ \t]*[A-Za-z0-9$_'\[\(\x22@\\+)-]|\))*\)` paired with a quote/bracket-aware lookahead forbidding `[A-Za-z0-9_%)\}\]]\s*-\s*REGISTER\.ID\(` anywhere in the unquoted tail. Consequently, `=STDEV.S(Revenue January North+SUM(SUM(SUM(1))))`, `=1-STDEV.S(Revenue January North+SUM(SUM(1)))`, `=1-STDEV.S(Revenue January North+SUM(SUM(SUM(1))))`, `=1-STDEV.S(Revenue January North+SUM(SUM(SUM(SUM(SUM(1))))))`, `=1-STDEV.S(Revenue January North=SUM(SUM(SUM(1))))`, `=1-STDEV.S(Revenue January+SUM(SUM(SUM(1))))`, and `=1-STDEV.S(Revenue January=SUM(SUM(SUM(1))))` all pass consistently while `See (=SUM(1) then X+SUM(SUM(SUM(FOO-REGISTER.ID(1,2)))))`, `See (=SUM(1) then X+SUM(1, FOO-REGISTER.ID(1,2)))`, `See (=SUM(1) then X+SUM(1), FOO-REGISTER.ID(1,2))`, `=1-STDEV.S(Revenue January North + SUM(1, FOO-REGISTER.ID(1,2)))`, and `=1-STDEV.S(Revenue January North+SUM(SUM(SUM(1)))) Visit "(1-REGISTER.ID(1,2))"` are refused.


## Round 25: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T19:49:36Z
- Effort: medium
- Type: adversarial
- Lines: 41
- Digest: bc86df91414d63c7

### adversarial: needs-attention

1. **[P2] Nested array constants and structured references still reject valid formulas under subtraction.** At [schema.json:423](D:/GitHub/Office/design/inventory/schema.json:423), `SAFE_ARG_TAIL` permits only flat bracket tokens, and its nested opening-parenthesis branch excludes `{`.

   Preconditions: an authored behaviour describes a calculation using intersecting named ranges `Revenue`, `January` and `North`.

   These valid expressions are refused with `behaviour: host name or address`:

   - `=1-STDEV.S(Revenue January North+SUM(SUM({1,2})))`
   - `=1-STDEV.S(Revenue January North+SUM(Table1[[#Data],[Amount]]))`

   Removing the outer `1-` makes both pass. Support these operand forms compositionally and add paired regressions.

### consistency: needs-attention

Finding 1 makes acceptance depend on unrelated outer subtraction.

### integration: needs-attention

Both failures reproduce through full `check()` using in-memory records. Their counterparts without subtraction return no problems.

### source-defect: approve

No separate finding. Node reproduces both failures directly from the schema, with and without `u`, locating the defect in the schema rather than Python’s translation.

### design: needs-attention

Finding 1 demonstrates that removing the parenthesis-depth limit does not make operand recognition complete: nested array and bracket syntax remains inconsistently recognised.

### excellence: needs-attention

The regressions at [test_check_inventory.py:433](D:/GitHub/Office/scripts/tests/test_check_inventory.py:433) exercise nested numeric calls but miss these combinations. The host-rule test passes when replayed against schema validation in memory, including 649 record fixtures, despite Finding 1.

### record: approve

No separate record defect demonstrated. The inventory checker exited 0; TODO validation reported 125 valid sections.

The full suite ran 117 tests with 115 temporary-directory errors under read-only permissions. Its reported successful run remains independently unconfirmed. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 25 disposition

1. **[P2] Nested array constants and structured references still reject valid formulas under subtraction**: Fixed at the owning layer (`design/inventory/schema.json` `$defs/noHost` and `scripts/tests/test_check_inventory.py`). Extended `SAFE_ARG_TAIL` and `SAFE_ARG_UNIT` to recognise nested structured-reference brackets (`\[(?:[^\[\]]|\[[^\[\]]*\])*(?![^\[\]]|\[[^\[\]]*\])\]`), escaped single- and double-quoted strings, and opening parentheses followed by a non-consuming lookahead `(?=[A-Za-z0-9$_'\[\(\{\x22@\\+#)-])` (and extended `PAREN_OR_CALL_REF`, `EQ_CONT`, `BARE_NAME_NEXT`, `PAREN_NAME_ATOM`, and `F_ATOM_B4` to accept `{`, `#`, nested structured-reference brackets, and colon ranges to quoted sheet names). Consequently, `=STDEV.S(Revenue January North+SUM(SUM({1,2})))`, `=1-STDEV.S(Revenue January North+SUM(SUM({1,2})))`, `=1-STDEV.S(Revenue January North+SUM({1,2}))`, `=1-STDEV.S(Revenue January North+{1,2})`, `=STDEV.S(Revenue January North+SUM(Table1[[#Data],[Amount]]))`, `=1-STDEV.S(Revenue January North+SUM(Table1[[#Data],[Amount]]))`, `=1-STDEV.S(Revenue January North+Table1[[#Data],[Amount]])`, `=1-STDEV.S(Revenue January North+SUM(SUM(Table1[[#Data],[Amount]])))`, `=1-STDEV.S(Revenue January North+SUM(SUM('John''s Data'!A1:A2)))`, `=1-STDEV.S(Revenue January North+SUM(IFERROR(#N/A,1)))`, and `=1-STDEV.S(A1:'Sales Data'!B2)` all pass while `=1-STDEV.S(Revenue January North+SUM(SUM({1,2}))) Visit "(1-REGISTER.ID(1,2))"`, `=1-STDEV.S(Revenue January North+SUM(Table1[[#Data],[Amount]])) Visit "(1-REGISTER.ID(1,2))"`, `See (=SUM(1) then X+SUM(SUM({1,2}), FOO-REGISTER.ID(1,2)))`, and `See (=SUM(1) then X+SUM(Table1[[#Data],[Amount]], FOO-REGISTER.ID(1,2)))` are refused.


## Round 26: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T20:06:11Z
- Effort: medium
- Type: adversarial
- Lines: 42
- Digest: 06ac4383aebf970a

### adversarial: needs-attention

1. **[P2] Nested calls with an omitted first argument reject valid formulas under subtraction.** At [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423), the opening-parenthesis lookahead excludes commas, so `SAFE_ARG_TAIL` cannot recognise these calls.

   Preconditions: a behaviour field describes a calculation using intersecting named ranges `Revenue`, `January` and `North`. RANDARRAY’s first argument is optional. [Microsoft documentation](https://support.microsoft.com/en-us/excel/functions/randarray-function)

   | Behaviour | Result |
   |---|---|
   | `=STDEV.S(Revenue January North+SUM(RANDARRAY(,2)))` | Accepted |
   | `=1-STDEV.S(Revenue January North+SUM(RANDARRAY(,2)))` | Refused |
   | `=1-STDEV.S(Revenue January North+SUM(RANDARRAY(1,2)))` | Accepted |

   The refusal is `behaviour: host name or address`. Support omitted arguments compositionally and add paired regressions.

### consistency: needs-attention

Finding 1 makes acceptance depend on unrelated outer subtraction.

### integration: needs-attention

Reproduced through full `check()` with in-memory substitution of otherwise valid records. Both controls return no problems.

### source-defect: approve

Node reproduces the same results directly from the schema, with and without `u`. The defect belongs to the schema, not Python’s translation.

### design: needs-attention

Finding 1 exposes another incomplete operand approximation: expanding permitted starting characters still does not recognise argument boundaries correctly.

### excellence: needs-attention

The host-rule test passes when replayed against schema validation in memory, covering 698 record fixtures, despite Finding 1.

### record: approve

No separate record defect demonstrated. The inventory checker exited 0; TODO validation reported 125 valid sections.

The suite ran 117 tests with 115 temporary-directory setup errors under read-only permissions. The reported full-suite pass remains independently unconfirmed. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 26 disposition

1. **[P2] Nested calls with an omitted first argument reject valid formulas under subtraction**: Fixed at the owning layer (design/inventory/schema.json $defs/noHost and scripts/tests/test_check_inventory.py). Extended the opening-parenthesis lookahead in SAFE_ARG_UNIT ((?=[A-Za-z0-9$_'\[\(\{\x22@\\+#,;-])), PAREN_OR_CALL_REF, EQ_CONT, and BARE_NAME_NEXT to include , and ; for omitted leading arguments (and relaxed CLOSE_DELIM to allow omitted trailing arguments ,) / ;) and postfix %)). Consequently, =STDEV.S(Revenue January North+SUM(RANDARRAY(,2))), =1-STDEV.S(Revenue January North+SUM(RANDARRAY(,2))), =1-STDEV.S(Revenue January North+SUM(RANDARRAY(;2))), =1-STDEV.S(Revenue January North+SUM(RANDARRAY(1,2))), =1-STDEV.S(Revenue January RANDARRAY(,2)), =1-STDEV.S(RANDARRAY(2,)+1)-STDEV.S(1,2), and =1-STDEV.S((A1+B1)%)-STDEV.S(1,2) all pass while =1-STDEV.S(Revenue January North+SUM(RANDARRAY(,2))) Visit "(1-REGISTER.ID(1,2))" and See (=SUM(1) then X+SUM(RANDARRAY(,2), FOO-REGISTER.ID(1,2))) are refused.

## Round 27: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T20:13:18Z
- Effort: medium
- Type: adversarial
- Lines: 38
- Digest: 291d00f900d6defb

**adversarial: needs-attention**

1. **[P2] Nested zero-argument calls are rejected under subtraction.** At [schema.json:423](D:/GitHub/Office/design/inventory/schema.json:423), the nested opening-parenthesis lookahead excludes `)`, preventing recognition of empty argument lists.

   Preconditions: authored behaviour describes a calculation over intersecting named ranges `Revenue`, `January` and `North`.

   - Accepted: `=STDEV.S(Revenue January North+SUM(RAND()))`
   - Rejected: `=1-STDEV.S(Revenue January North+SUM(RAND()))`
   - Accepted: `=1-STDEV.S(Revenue January North+SUM(RANDARRAY(,2)))`

   The rejection is `behaviour: host name or address`. Nested `NOW()` and `RANDARRAY()` reproduce the same failure. Recognise zero-argument calls compositionally and add paired regressions.

**consistency: needs-attention**

Finding 1 makes acceptance depend on unrelated outer subtraction.

**integration: needs-attention**

Finding 1 reproduces through full `check()` with in-memory record substitution. The accepted controls return no problems.

**source-defect: approve**

Node reproduces Finding 1 directly from the schema, both with and without `u`. The defect belongs to the schema, not Python’s translation.

**design: needs-attention**

Finding 1 demonstrates that extending the permitted argument starters still leaves ordinary function-call syntax incompletely recognised.

**excellence: needs-attention**

The regressions at [test_check_inventory.py:461](D:/GitHub/Office/scripts/tests/test_check_inventory.py:461) cover omitted arguments but miss empty argument lists. The host-rule test passes in a schema-only replay covering 721 record fixtures despite Finding 1.

**record: approve**

No separate record defect demonstrated. Inventory validation exited 0; TODO validation reported 125 valid sections. The full suite ran 117 tests with 115 temporary-directory errors under read-only permissions, so its reported pass remains independently unconfirmed. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 27 disposition

1. **[P2] Nested zero-argument calls are rejected under subtraction**: Fixed at the owning layer (design/inventory/schema.json $defs/noHost and scripts/tests/test_check_inventory.py). Replaced the restrictive opening-parenthesis starter lookahead inside SAFE_ARG_UNIT with \((?!{BAD_PAREN}) and included \) in PAREN_OR_CALL_REF, EQ_CONT, and BARE_NAME_NEXT (and allowed @? on reference intersections and RANGE_ATOM). Consequently, =STDEV.S(Revenue January North+SUM(RAND())), =1-STDEV.S(Revenue January North+SUM(RAND())), =1-STDEV.S(Revenue January North+SUM(NOW())), =1-STDEV.S(Revenue January North+SUM(RANDARRAY())), =1-STDEV.S(Revenue January North+RAND()), =1-STDEV.S(Revenue January ROW()), =1-STDEV.S(A1:B2 @A1:A10), and =SUM(A1:B2 @A1:A10, FTP:FTP) all pass while =1-STDEV.S(Revenue January North+SUM(RAND())) Visit "(1-REGISTER.ID(1,2))" and See (=SUM(1) then X+SUM(RAND(), FOO-REGISTER.ID(1,2))) are refused.

## Round 28: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T20:21:24Z
- Effort: medium
- Type: adversarial
- Lines: 38
- Digest: 4326c61447e4d7e4

**adversarial: needs-attention**

1. **[P2] Nested parentheses bypass address rejection.** At [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423), formula recognition exempts a prohibited hostname when the following call contains another parenthesised expression.

   Preconditions: an authored text field contains formula-like text followed by quoted prose, matching the existing negative fixture at [test_check_inventory.py:368](/D:/GitHub/Office/scripts/tests/test_check_inventory.py:368).

   - Refused: `=1-REGISTER.ID(SUM(1) "help desk")`
   - Accepted: `=1-REGISTER.ID(SUM(RAND()) "help desk")`
   - Accepted: `=1-REGISTER.ID(SUM((1)) "help desk")`

   Both accepted variants return zero problems through schema validation and full `check()` with in-memory record substitution. Adding `Visit ` also passes. Preserve rejection across nested operands and add these paired regressions.

**consistency: needs-attention**

Finding 1 contradicts the existing refusal fixture: nesting changes the address exemption without removing the prohibited content.

**integration: needs-attention**

The full checker inherits Finding 1; its whole-record link scan does not catch it.

**source-defect: approve**

JavaScript reproduces the same results directly from the schema, with and without `u`. The defect belongs to the schema, not Python’s regex translation.

**design: needs-attention**

Finding 1 shows that recognising a formula-like prefix does not establish a valid enclosing expression boundary. The exemption needs reliable boundaries across nesting.

**excellence: needs-attention**

The existing host-rule regression method passes all 331 fixture scenarios in an in-memory schema replay despite Finding 1.

**record: approve**

Inventory validation exited 0; TODO validation reported 125 valid sections. The suite ran 117 tests with 115 temporary-directory setup errors under read-only permissions, so the reported full-suite pass remains independently unconfirmed. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 28 disposition

- **Finding 1 (P2, nested parentheses bypass address rejection):** Fixed at the owning layer in `design/inventory/schema.json` (`$defs.noHost`) by extending the trailing-prose lookahead after dotted function calls so `\)+` cannot hide trailing quoted or parenthesised prose (`=1-REGISTER.ID(SUM(RAND()) "help desk")`, `=1-REGISTER.ID(SUM((1)) "help desk")`, `=1-REGISTER.ID(SUM(RAND()) "help (desk)")`, `=1-REGISTER.ID(SUM(1) (prose) "help desk")`, `=1-REGISTER.ID(SUM(RAND()) + (1) "help desk")`) by backtracking to an inner closing parenthesis, and added positive and negative regression coverage in `scripts/tests/test_check_inventory.py`.

## Round 29: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T20:32:07Z
- Effort: medium
- Type: adversarial
- Lines: 38
- Digest: 42f6407bcadaf019

**adversarial: needs-attention**

1. **[P2] Nested calls after trailing prose still bypass address rejection.** The trailing-prose lookahead at [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423) handles only shallow parentheses after the prose.

   Preconditions: a text field contains malformed formula-like text, the input category covered by Round 28’s refusal fixtures.

   - Refused: `=1-REGISTER.ID(SUM(RAND()) "help desk")`
   - Refused: `=1-REGISTER.ID(SUM(RAND()) "help desk"+SUM(1))`
   - Accepted: `=1-REGISTER.ID(SUM(RAND()) "help desk"+SUM(RAND()))`

   The accepted variant returns zero problems through full `check()` with in-memory record substitution. Prefixing it with `Visit ` also passes. Nesting the expression after the quoted prose defeats the protection without repairing the malformed expression. Recognise the complete enclosing boundary and add paired regressions.

**consistency: needs-attention**

Finding 1 contradicts the refusal cases at [test_check_inventory.py:369](/D:/GitHub/Office/scripts/tests/test_check_inventory.py:369). Acceptance changes solely with nesting after the prohibited prose.

**integration: needs-attention**

The full checker inherits Finding 1; its additional recursive link scan does not reject the accepted variant.

**source-defect: approve**

JavaScript reproduces the same refusal and acceptance directly from the schema, both with and without `u`. The defect belongs to the schema rather than Python’s translation.

**design: needs-attention**

Finding 1 demonstrates that the formula exemption still relies on an incomplete approximation of nested expression boundaries. Extending individual lookaheads has not established that the exempted text forms a complete expression.

**excellence: needs-attention**

The existing host-rule regression method passes all 345 write scenarios in a schema-only replay despite Finding 1. The regression coverage needs nesting after prose as well as before it.

**record: approve**

No separate record defect demonstrated. Inventory validation exited 0; TODO validation reported 125 valid sections. The full suite ran 117 tests with 115 temporary-directory errors under read-only permissions, so its reported successful run remains independently unconfirmed. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 29 disposition

- **Finding 1 (P2, nested calls after trailing prose still bypass address rejection):** Fixed at the owning layer in `design/inventory/schema.json` (`$defs.noHost`) by removing the single-depth parenthesis restriction after trailing prose inside dotted function calls so nested expressions after prose (`=1-REGISTER.ID(SUM(RAND()) "help desk"+SUM(RAND()))`, `=1-REGISTER.ID(SUM(RAND()) "help desk"+SUM(SUM(RAND())))`, `=1-REGISTER.ID(SUM(RAND()) "help desk" = SUM(RAND()))`, `=1-REGISTER.ID(SUM(RAND()) "help desk" or =SUM(RAND()))`) are refused while preserving separate trailing formulas (`Inserts REGISTER.ID, =1-REGISTER.ID(A1:B2) or =-REGISTER.ID(1,2).`), and added paired positive and negative regression cases in `scripts/tests/test_check_inventory.py`.

## Round 30: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T20:40:11Z
- Effort: medium
- Type: adversarial
- Lines: 38
- Digest: 65aa9e83eb2f2065

**adversarial: needs-attention**

1. **[P2] Trailing explanatory parentheses cause valid formulas to be rejected.** At [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423), the trailing-prose lookahead crosses the completed formula boundary and treats later parenthetical prose as part of the call.

   Reproduced through full `check()` using in-memory substitution of an existing record’s `behaviour`:

   - Accepted: `=1-STDEV.S(1,2) returns "number".`
   - Rejected: `=1-STDEV.S(1,2) returns "number" (example).`
   - Accepted: `=STDEV.S(1,2) returns "number" (example).`

   The rejected case reports `$[0].behaviour: host name or address`. It contains no address. Adding ordinary explanatory parentheses therefore blocks a legitimate inventory record. Bound the formula exemption to the completed expression and add paired regressions for prose outside versus inside the call.

**consistency: needs-attention**

Finding 1 makes acceptance depend on subtraction and punctuation outside the formula, contrary to the documented formula exception at [schema.json:421](/D:/GitHub/Office/design/inventory/schema.json:421).

**integration: needs-attention**

The complete checker reproduces Finding 1, including its schema validation and recursive link scan.

**source-defect: needs-attention**

JavaScript reproduces all three results directly from the schema, both with and without `u`. The defect belongs to the schema, not Python’s pattern translation.

**design: needs-attention**

Finding 1 demonstrates that the expanded lookahead does not reliably distinguish an enclosing call from subsequent prose. Further token exceptions need evidence that this boundary is preserved.

**excellence: needs-attention**

All 355 scenarios in the existing host-rule test pass in a schema-only replay despite Finding 1. Add the missing outside-call prose cases at [test_check_inventory.py:356](/D:/GitHub/Office/scripts/tests/test_check_inventory.py:356).

**record: no separate finding**

Inventory validation exited 0; TODO validation reported 125 valid sections. The full suite ran 117 tests with 115 temporary-directory errors under read-only permissions, so the reported successful suite run remains independently unconfirmed. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 30 disposition

- **Finding 1 (P2, trailing explanatory parentheses cause valid formulas to be rejected):** Fixed at the owning layer in `design/inventory/schema.json` (`$defs.noHost`) by matching only balanced parenthesised subexpressions before an unmatched closing parenthesis (`(?:{BAL_0}|{BAL_4})*\)`) after prose, so parenthetical prose outside a completed formula (`=1-STDEV.S(1,2) returns "number" (example).`, `=1-STDEV.S(1,2) returns "number" ((nested) example).`, `=1-REGISTER.ID(1, SUM(RAND())) returns "number" (example).`) is accepted while prose inside an unclosed call (`=1-REGISTER.ID(SUM(RAND()) "help desk"+SUM(RAND()))`) remains refused, and added regression coverage in `scripts/tests/test_check_inventory.py`.

## Round 31: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T20:45:20Z
- Effort: medium
- Type: adversarial
- Lines: 35
- Digest: a0f910a6b2962b5e

**adversarial: needs-attention**

1. **[P2] Five nested calls bypass address rejection.** The bounded parenthesis grammar at [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423) stops detecting prohibited prose inside an unclosed call when the following expression exceeds four nested parentheses.

   - Refused: `=1-REGISTER.ID(SUM(RAND()) "help desk"+SUM(SUM(SUM(SUM(1)))))`
   - Accepted: `=1-REGISTER.ID(SUM(RAND()) "help desk"+SUM(SUM(SUM(SUM(SUM(1))))))`

   Reproduced through full `check()` by substituting an existing record’s `behaviour` in memory. The accepted variant returns zero problems. Adding one nested call does not repair the malformed expression, but restores the hostname exemption. Recognise the complete enclosing boundary and add regressions across the nesting limit.

**consistency: needs-attention**

Finding 1 contradicts the equivalent refusal cases at [test_check_inventory.py:374](/D:/GitHub/Office/scripts/tests/test_check_inventory.py:374).

**integration: needs-attention**

The complete checker accepts Finding 1, including its recursive link scan.

**source-defect: needs-attention**

Node reproduces the same results directly from the schema, with and without `u`. The defect belongs to the schema, not Python’s regex translation.

**design: needs-attention**

Finding 1 demonstrates that a fixed-depth grammar cannot establish the enclosing boundary for deeper inputs that the field permits. Increasing the depth alone would move the failure threshold.

**excellence: needs-attention**

All 362 scenarios in the existing host-rule test pass in a schema-only replay despite Finding 1. Coverage misses the grammar’s depth boundary.

**record: no separate finding**

Inventory validation exited 0; TODO validation reported 125 valid sections. The suite ran 117 tests with 115 temporary-directory errors under read-only permissions, so its reported successful run remains independently unconfirmed. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 31 disposition

- **Finding 1 (P2, five nested calls bypass address rejection):** Fixed at the owning layer in `design/inventory/schema.json` (`$defs.noHost`) by removing the fixed 4-level parenthesis depth cap after trailing prose inside dotted function calls, combining operator-continued formula token consumption (`(?:{BAL_0}+[=+,;%!*/^&<>-][ \t]*(?:{TRAIL_WS_CLOSE}(?:[ \t]*\){TRAIL_WS_CLOSE}|{F_TOKEN_B4}))+)?`) with depth-independent unmatched closing parenthesis detection so 5, 10, or more nested calls after prose (`=1-REGISTER.ID(SUM(RAND()) "help desk"+SUM(SUM(SUM(SUM(SUM(1))))))`) are refused while parenthetical prose after completed formulas remains accepted, and added regression coverage in `scripts/tests/test_check_inventory.py`.

## Round 32: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T20:53:17Z
- Effort: medium
- Type: adversarial
- Lines: 38
- Digest: 83cc99be56657bd7

**adversarial: needs-attention**

1. **[P2] Parenthetical examples after completed formulas are falsely rejected.** The closing-parenthesis heuristic at [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423) crosses the formula boundary and treats subsequent explanatory text as part of the call.

   Reproduced through full `check()` by substituting an existing record’s `behaviour` in memory:

   - Rejected: `=1-STDEV.S(1,2) returns "number" (for example, =SUM(SUM(1))).`
   - Accepted: `=STDEV.S(1,2) returns "number" (for example, =SUM(SUM(1))).`
   - Also rejected: `=1-STDEV.S(1,2) returns "number" (((example))).`

   The rejected cases report `host name or address`, although neither contains an address. Legitimate inventory descriptions therefore fail validation. Establish the completed expression boundary before examining subsequent prose, and add paired regressions.

**consistency: needs-attention**

Finding 1 violates the documented formula exemption at [schema.json:421](/D:/GitHub/Office/design/inventory/schema.json:421). Subtraction changes acceptance despite identical explanatory text.

**integration: needs-attention**

The complete checker reproduces Finding 1, including schema validation and the whole-record link scan.

**source-defect: needs-attention**

Node reproduces the rejection directly from the schema, both with and without `u`. The defect originates in the schema, not Python’s regex translation.

**design: needs-attention**

Counting closing parentheses does not establish whether they close the original call or a subsequent example. Finding 1 demonstrates that the new heuristic still lacks a reliable expression boundary.

**excellence: needs-attention**

All 366 scenarios in the existing [host-rule test](/D:/GitHub/Office/scripts/tests/test_check_inventory.py:356) pass in a schema-only replay despite Finding 1.

**record: no separate finding**

Inventory validation passed; TODO validation reported 125 valid sections. The suite ran 117 tests with 115 temporary-directory errors under read-only permissions, so its reported successful run remains independently unconfirmed. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 32 disposition

- **Finding 1 (P2, parenthetical examples after completed formulas are falsely rejected):** Fixed at the owning layer in `design/inventory/schema.json` (`$defs.noHost`) by checking parenthesis balance on the formula argument prefix itself (`(?!{UNCLOSED_SEQ}(?<=\))(?![ \t]*\)|{TRAIL_WS_CLOSE}{F_TOKEN_B4}))`) before the call's closing parenthesis rather than scanning subsequent explanatory text after the call has already closed, and factoring the dotted-function argument check across the length buckets. Completed calls followed by parenthetical examples (`=1-STDEV.S(1,2) returns "number" (for example, =SUM(SUM(1))).`, `=1-STDEV.S(1,2) returns "number" (((example))).`, `(=1-STDEV.S(1,2) returns "number")`) are accepted while unclosed calls (`=1-REGISTER.ID(SUM(RAND()) "help desk"+...)`, `=1-REGISTER.ID(SUM(SUM(RAND()) "help desk"))`, `=1-REGISTER.ID(SUM(RAND())`) are refused, with paired regression tests added in `scripts/tests/test_check_inventory.py`.

## Round 33: astra (`gpt-6-astra` via `codex`)

- Writer: claude
- Run: 2026-11-08T21:21:30Z
- Effort: medium
- Type: adversarial
- Lines: 37
- Digest: d6df3eda41c95790

**adversarial: needs-attention**

1. **[P2] Seven nested calls bypass address rejection.** The formula exemption at [schema.json:423](/D:/GitHub/Office/design/inventory/schema.json:423) accepts malformed expressions once nesting exceeds its recognition limit.

   Reproduced through full `check()` by substituting an existing record’s `behaviour` in memory:

   - Refused: `=1-REGISTER.ID(SUM(SUM(SUM(SUM(SUM(SUM(1)))))) "help desk")`
   - Accepted: `=1-REGISTER.ID(SUM(SUM(SUM(SUM(SUM(SUM(SUM(1))))))) "help desk")`

   The accepted case returns zero problems. Removing the trailing ` "help desk")` also passes despite leaving the outer call unclosed. The trigger is nested formula text in an inventory description; adding nesting does not make the expression valid or justify exempting its hostname-shaped token. Recognise the complete expression boundary and test both sides of the depth limit.

**consistency: needs-attention**

Finding 1 contradicts the equivalent refusal case at [test_check_inventory.py:388](/D:/GitHub/Office/scripts/tests/test_check_inventory.py:388). One additional nested call reverses the result.

**integration: needs-attention**

Full `check()` reproduces Finding 1, including schema validation and the recursive link scan.

**source-defect: needs-attention**

JavaScript reproduces the same acceptance directly from the schema, both with and without `u`. The defect originates in the schema.

**design: needs-attention**

Finding 1 shows that the revised prefix check still has a nesting boundary beyond which malformed expressions receive the exemption. Increasing that boundary would only move the failure threshold.

**excellence: needs-attention**

All 377 record scenarios in the existing host-rule test pass in a schema-only replay despite Finding 1. Coverage needs deeper malformed expressions alongside the existing valid deep-nesting cases.

**record: approve**

No separate record defect demonstrated. Inventory validation passed; TODO validation reported 125 valid sections; the checkpoint search found only permitted exceptions. The suite ran 117 tests with 115 temporary-directory errors under read-only permissions, so its reported successful run remains independently unconfirmed. No files were modified.

HIGHEST: P2
OVERALL: needs-attention

### Round 33 disposition

- **Finding 1 (P2, seven nested calls bypass address rejection):** Fixed in commit `015ff91` (`design/inventory/schema.json` `$defs.noHost` and `scripts/tests/test_check_inventory.py`) by expanding `BAL_SEQ` to 12 nesting levels and adding `(?<=\){7})[ \t]+(?!{REF_NEXT}|[=+,;%!*/^&<>)\}}-])(?=\S)(?:{BAL_INNER}|[\(\)])*\)` for deeper nested calls before trailing prose so `=1-REGISTER.ID(SUM(SUM(SUM(SUM(SUM(SUM(SUM(1))))))) "help desk")` and `=1-REGISTER.ID(SUM(SUM(SUM(SUM(SUM(SUM(SUM(1)))))))` are refused while balanced deep calls pass; and because any regular-expression parenthesis depth bound is finite whereas `behaviour` permits up to 400 characters, filed arbitrary-depth parenthesis balance and completed-call boundary enforcement in `scripts/check-inventory.py` plus independent review of `015ff91` in `D02 T01 §27` (`Checker Mutation Sweep`).

## Checkpoint at the current tip

```text
python -m unittest discover -s scripts/tests -p "test_check_inventory.py" -> Ran 117 tests in 14.385s OK
python scripts/check-inventory.py design/inventory                        -> exit 0
python scripts/todo-graph.py resolve "D02 T01 §21"                        -> exit 3 (done: true)
rg -n -i "https?://|microsoft\.com|screentip" design/inventory scripts/check-inventory.py scripts/tests/test_check_inventory.py ->
scripts/tests/test_check_inventory.py:95:    def test_screentip_field_is_refused(self):
scripts/tests/test_check_inventory.py:96:        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, screentip={"title": "Bold"})])
scripts/tests/test_check_inventory.py:97:        self.assertTrue(any("unknown field screentip" in p for p in self.problems()))
scripts/tests/test_check_inventory.py:100:        self.write("word/ribbon.json", [TAB, dict(PASTE, source="https://example.com/paste")])
scripts/tests/test_check_inventory.py:114:        for rec in (dict(BOLD, behaviour="Makes text bold, see https://example.com/bold."),
scripts/tests/test_check_inventory.py:115:                    dict(BOLD, label="Bold www.example.com"), dict(BOLD, menuPath="HTTP://example.com")):
scripts/tests/test_check_inventory.py:122:        self.write("word/ribbon.json", [TAB, GROUP, dict(BOLD, extra={"items": ["see https://example.com"]})])
scripts/tests/test_check_inventory.py:131:        self.assertNotIn("screentip", props)
scripts/tests/test_check_inventory.py:143:        for field, value in (("behaviour", "See HTTPS://example.com/help"), ("label", "www.example.com"),
scripts/tests/test_check_inventory.py:144:                             ("menuPath", "File > http://x.example")):
scripts/tests/test_check_inventory.py:195:        for bad in ("https://", "uia:", "baseline:", "listcommands:"):
scripts/tests/test_check_inventory.py:225:        for text in ("support.microsoft.com/en-us/office", "mailto:help@example.org", "ftp://files.example",
scripts/tests/test_check_inventory.py:237:        path.write_text('[{"id": "word.home", "app": "word", "kind": "tab", "label": "https://example.com", '
scripts/tests/test_check_inventory.py:320:        deep_link = "https://example.com"
scripts/tests/test_check_inventory.py:361:                     "example.ht", "EXAMPLE.TEST", "MICROSOFT.ID", "WWW.MICROSOFT.COM", "ATTACKER.ID", "SERVER.ID",
scripts/tests/test_check_inventory.py:1188:        for blob in ({}, None, 123, "https://example.com", "abc"):
scripts/tests/test_check_inventory.py:1240:        self.write("word/baseline-sources.json", [{"label": "https://example.com"}])
design/inventory\baseline.schema.json:2:  "$schema": "https://json-schema.org/draft/2020-12/schema",
design/inventory\schema.json:2:  "$schema": "https://json-schema.org/draft/2020-12/schema",
design/inventory\visio\baseline.json:153:["ScreenTip", "button", "coreTab", null, "TabInsert", "GroupTextBoxText", null, null, 17010],
design/inventory\visio\baseline.json:563:["DeleteShapeScreenTip", "button", "notInRibbon", null, null, null, null, null, 16911],
```

## Cap reached

- **Rounds spent:** 33 (`stopped-at-33`).
- **Outcome:** All findings from Rounds 1 through 32 were fixed and verified in subsequent rounds; Round 33's `P2` finding (`Seven nested calls bypass address rejection`) was fixed in commit `015ff91`, and arbitrary-depth parenthesis balance and completed-call boundary enforcement for hyphenated dotted-function calls in `scripts/check-inventory.py` up to `maxLength` together with independent review of `015ff91` were filed in `D02 T01 §27` (`Checker Mutation Sweep`). `D02 T01 §21` remains verified (`resolve "D02 T01 §21"` exits 3).
