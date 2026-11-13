# Inventory Mutation Sweep

D02 T01 §27. Each rule of `scripts/check-inventory.py` and `design/inventory/schema.json` removed on its own and `scripts/tests/test_check_inventory.py` run against it, by `python -B scripts/mutation-sweep-inventory.py` on commit `4aa7102` (2026-11-13, run through `bosun`). Rules: every checker guard, every schema keyword the validator reads, every `properties` entry and every top-level pattern alternative. The 4,207 alternation bars nested inside noHost's top-level alternatives are not removed one by one (about ten hours of runs); they define each family's exemptions.

## First run

42 survivors and 7 removals whose tests only error, on commit `4aa7102`. The second run, below, is the same sweep after each of them was given its test.

```text
unmutated: 119 tests pass in 35 s; 271 rules
ERRORED      0 failing, 1 erroring    guard check-inventory.py:263 if i >= len(text)
KILLED       2 failing, 0 erroring    guard check-inventory.py:266 if c == '"'
SURVIVED     0 failing, 0 erroring    guard check-inventory.py:270 if i >= len(text)
KILLED       1 failing, 0 erroring    guard check-inventory.py:276 if depth and c in '")'
KILLED       1 failing, 0 erroring    guard check-inventory.py:281 if k < len(text) and text[k] not in AFTER_ARGUMENT and (not (c == ')' and spaced and (text[k]
KILLED       57 failing, 0 erroring   guard check-inventory.py:290 if '$ref' in schema
KILLED       1 failing, 0 erroring    guard check-inventory.py:292 if schema['$ref'] == '#/$defs/noHost' and isinstance(value, str) and (not problems)
KILLED       1 failing, 0 erroring    guard check-inventory.py:294 if call
KILLED       8 failing, 0 erroring    guard check-inventory.py:298 if 'type' in schema and (not type_ok(value, schema['type']))
KILLED       21 failing, 0 erroring   guard check-inventory.py:300 if 'const' in schema and value != schema['const']
KILLED       3 failing, 0 erroring    guard check-inventory.py:302 if 'enum' in schema and value not in schema['enum']
KILLED       33 failing, 0 erroring   guard check-inventory.py:304 if isinstance(value, str)
KILLED       2 failing, 0 erroring    guard check-inventory.py:305 if len(value) < schema.get('minLength', 0)
KILLED       2 failing, 0 erroring    guard check-inventory.py:307 if len(value) > schema.get('maxLength', len(value))
KILLED       30 failing, 1 erroring   guard check-inventory.py:310 if 'pattern' in schema and (not ecma(schema['pattern']).search(utf16(value)))
KILLED       2 failing, 0 erroring    guard check-inventory.py:312 if isinstance(value, (int, Decimal)) and (not isinstance(value, bool)) and (value < schema.ge
KILLED       57 failing, 0 erroring   guard check-inventory.py:314 if isinstance(value, list) and 'items' in schema
KILLED       56 failing, 0 erroring   guard check-inventory.py:317 if isinstance(value, dict)
KILLED       10 failing, 0 erroring   guard check-inventory.py:319 if key not in value
KILLED       61 failing, 0 erroring   guard check-inventory.py:323 if key in props
KILLED       4 failing, 0 erroring    guard check-inventory.py:325 if schema.get('additionalProperties', True) is False
KILLED       1 failing, 0 erroring    guard check-inventory.py:328 if key in value
KILLED       24 failing, 1 erroring   guard check-inventory.py:330 if 'not' in schema and (not validate(value, schema['not'], root, path))
KILLED       4 failing, 0 erroring    guard check-inventory.py:333 if 'if' in sub
KILLED       4 failing, 0 erroring    guard check-inventory.py:334 if not validate(value, sub['if'], root, path)
KILLED       3 failing, 0 erroring    guard check-inventory.py:362 if isinstance(item, str)
KILLED       3 failing, 0 erroring    guard check-inventory.py:366 if hit
KILLED       2 failing, 0 erroring    guard check-inventory.py:368 if found <= LINKS_SHOWN
KILLED       1 failing, 0 erroring    guard check-inventory.py:378 if found > LINKS_SHOWN
ERRORED      0 failing, 1 erroring    guard check-inventory.py:401 if own and len(pinned) != 1
KILLED       1 failing, 0 erroring    guard check-inventory.py:494 if entry.is_symlink() or (hasattr(entry, 'is_junction') and entry.is_junction())
KILLED       1 failing, 0 erroring    guard check-inventory.py:531 if not data['rows']
KILLED       1 failing, 0 erroring    guard check-inventory.py:533 if sources and data['source'] != f"baseline:{sources.get('commit')}"
KILLED       1 failing, 0 erroring    guard check-inventory.py:537 if data['columns'] != expected
KILLED       1 failing, 0 erroring    guard check-inventory.py:542 if len(row) != len(expected)
ERRORED      0 failing, 1 erroring    guard check-inventory.py:546 if name == 'window' and (not isinstance(cell, str))
KILLED       1 failing, 0 erroring    guard check-inventory.py:549 if name == 'window' and sources and (cell not in windows)
ERRORED      0 failing, 1 erroring    guard check-inventory.py:601 if manifest and (not (isinstance(sources, dict) and isinstance(sources.get('commit'), str) an
KILLED       5 failing, 0 erroring    guard check-inventory.py:606 if manifest
KILLED       2 failing, 0 erroring    guard check-inventory.py:611 if reference_commit and sources['commit'] != reference_commit
KILLED       2 failing, 0 erroring    guard check-inventory.py:616 if bad or not hex40.fullmatch(sources['commit'])
KILLED       1 failing, 0 erroring    guard check-inventory.py:624 if missing or extra or (not windows)
KILLED       1 failing, 0 erroring    guard check-inventory.py:634 if whole and sources is not None
ERRORED      0 failing, 2 erroring    guard check-inventory.py:637 if not path.is_file()
SURVIVED     0 failing, 0 erroring    guard check-inventory.py:639 if app == 'outlook' and sources
SURVIVED     0 failing, 0 erroring    guard check-inventory.py:648 if absent
KILLED       3 failing, 0 erroring    guard check-inventory.py:653 if is_baseline(f)
SURVIVED     0 failing, 0 erroring    guard check-inventory.py:661 if is_shell_chrome(f, data)
SURVIVED     0 failing, 0 erroring    guard check-inventory.py:663 if is_word_ribbon(f, inventory)
SURVIVED     0 failing, 0 erroring    guard check-inventory.py:665 if is_word_backstage(f, inventory)
SURVIVED     0 failing, 0 erroring    guard check-inventory.py:667 if is_word_shortcuts(f, inventory)
KILLED       3 failing, 0 erroring    guard check-inventory.py:678 if isinstance(rid, str)
KILLED       2 failing, 0 erroring    guard check-inventory.py:679 if len(seen.get(rid, [])) > 1
KILLED       1 failing, 0 erroring    guard check-inventory.py:684 if isinstance(rec.get('app'), str) and rid.split('.', 1)[0] != rec['app']
KILLED       2 failing, 0 erroring    guard check-inventory.py:686 if isinstance(rid, str) and rid in parents
KILLED       2 failing, 0 erroring    guard check-inventory.py:688 if loop
KILLED       4 failing, 0 erroring    guard check-inventory.py:691 if isinstance(profile, str) and profile not in profiles
KILLED       1 failing, 0 erroring    guard check-inventory.py:693 if isinstance(build, str) and build not in builds
KILLED       1 failing, 0 erroring    guard check-inventory.py:698 if pinned and (not baseline_commit.startswith(pinned.group(1)))
KILLED       1 failing, 0 erroring    guard check-inventory.py:701 if stamped and stamped.group(1) not in builds
KILLED       1 failing, 0 erroring    guard check-inventory.py:703 if stamped and isinstance(build, str) and (stamped.group(1) != build)
ERRORED      0 failing, 6 erroring    guard check-inventory.py:706 if isinstance(parent, str) and parent not in seen
KILLED       2 failing, 0 erroring    guard check-inventory.py:708 if isinstance(parent, str) and len(seen[parent]) > 1
KILLED       4 failing, 0 erroring    guard check-inventory.py:711 if isinstance(target, str)
ERRORED      0 failing, 6 erroring    guard check-inventory.py:712 if target not in kinds
KILLED       1 failing, 0 erroring    guard check-inventory.py:714 if len(seen[target]) > 1
KILLED       1 failing, 0 erroring    guard check-inventory.py:716 if kinds[target] not in TARGET_KINDS and (not (rec.get('kind') == 'backstagePage' and kinds[t
KILLED       2 failing, 0 erroring    guard check-inventory.py:720 if require_behaviour and rec.get('kind') in ('contextualTab', 'control', 'menuItem')
KILLED       2 failing, 0 erroring    guard check-inventory.py:721 if not str(rec.get('behaviour', '')).strip(ECMA_SPACE)
KILLED       1 failing, 0 erroring    schema / type
KILLED       57 failing, 0 erroring   schema / items
KILLED       57 failing, 0 erroring   schema /items $ref
KILLED       1 failing, 0 erroring    schema /$defs/record type
KILLED       4 failing, 0 erroring    schema /$defs/record required
KILLED       3 failing, 0 erroring    schema /$defs/record additionalProperties
KILLED       1 failing, 0 erroring    schema /$defs/record dependentRequired
KILLED       4 failing, 0 erroring    schema /$defs/record allOf
KILLED       29 failing, 1 erroring   schema /$defs/record properties.id
KILLED       24 failing, 2 erroring   schema /$defs/record properties.app
KILLED       25 failing, 1 erroring   schema /$defs/record properties.kind
KILLED       42 failing, 0 erroring   schema /$defs/record properties.label
KILLED       23 failing, 1 erroring   schema /$defs/record properties.parent
KILLED       28 failing, 1 erroring   schema /$defs/record properties.order
KILLED       16 failing, 1 erroring   schema /$defs/record properties.controlType
KILLED       17 failing, 1 erroring   schema /$defs/record properties.size
KILLED       19 failing, 1 erroring   schema /$defs/record properties.keytip
KILLED       20 failing, 1 erroring   schema /$defs/record properties.shortcut
KILLED       1 failing, 0 erroring    schema /$defs/record properties.scope
KILLED       1 failing, 0 erroring    schema /$defs/record properties.condition
KILLED       1 failing, 0 erroring    schema /$defs/record properties.itemCount
KILLED       6 failing, 0 erroring    schema /$defs/record properties.target
KILLED       6 failing, 0 erroring    schema /$defs/record properties.menuPath
KILLED       20 failing, 1 erroring   schema /$defs/record properties.bounds
KILLED       19 failing, 1 erroring   schema /$defs/record properties.captureProfile
KILLED       14 failing, 0 erroring   schema /$defs/record properties.behaviour
KILLED       20 failing, 1 erroring   schema /$defs/record properties.idMso
KILLED       8 failing, 0 erroring    schema /$defs/record properties.uiaId
KILLED       23 failing, 1 erroring   schema /$defs/record properties.source
KILLED       21 failing, 1 erroring   schema /$defs/record properties.capturedFrom
KILLED       2 failing, 0 erroring    schema /$defs/record properties.baselineMissing
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/id type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/id pattern
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id/allOf/0 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/id/allOf/1 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/id/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/app enum
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/kind enum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/label type
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/label minLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/label maxLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/label pattern
KILLED       22 failing, 0 erroring   schema /$defs/record/properties/label allOf
KILLED       4 failing, 0 erroring    schema /$defs/record/properties/label/allOf/0 $ref
KILLED       5 failing, 0 erroring    schema /$defs/record/properties/label/allOf/1 $ref
KILLED       15 failing, 0 erroring   schema /$defs/record/properties/label/allOf/2 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/parent type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/parent allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent/allOf/2 $ref
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/order type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/order minimum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/controlType enum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/size enum
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/keytip type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/keytip allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip/allOf/2 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/shortcut type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut pattern
KILLED       4 failing, 0 erroring    schema /$defs/record/properties/shortcut allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut/allOf/0 $ref
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/shortcut/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut/allOf/2 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/scope enum
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/condition type
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/condition minLength
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/condition pattern
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition/allOf/0 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/condition/allOf/1 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/condition/allOf/2 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/itemCount type
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/itemCount minimum
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/target type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/target allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target/allOf/2 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/menuPath type
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/menuPath minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath pattern
KILLED       4 failing, 0 erroring    schema /$defs/record/properties/menuPath allOf
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/menuPath/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/bounds required
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds additionalProperties
KILLED       15 failing, 1 erroring   schema /$defs/record/properties/bounds properties.x
KILLED       15 failing, 1 erroring   schema /$defs/record/properties/bounds properties.y
KILLED       17 failing, 1 erroring   schema /$defs/record/properties/bounds properties.width
KILLED       16 failing, 1 erroring   schema /$defs/record/properties/bounds properties.height
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/x type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/y type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/width type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/width minimum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/height type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/height minimum
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/captureProfile type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/captureProfile minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/captureProfile allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/behaviour type
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/behaviour minLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/behaviour maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/behaviour pattern
KILLED       5 failing, 1 erroring    schema /$defs/record/properties/behaviour allOf
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/behaviour/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/behaviour/allOf/1 $ref
KILLED       2 failing, 1 erroring    schema /$defs/record/properties/behaviour/allOf/2 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/idMso type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/idMso minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/idMso maxLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/idMso pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/idMso allOf
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/idMso/allOf/0 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/idMso/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/idMso/allOf/2 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/uiaId type
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/uiaId minLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/uiaId maxLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/uiaId pattern
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/uiaId allOf
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/uiaId/allOf/0 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/uiaId/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/uiaId/allOf/2 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/source type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/source maxLength
KILLED       6 failing, 0 erroring    schema /$defs/record/properties/source pattern
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/source allOf
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/source/allOf/0 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/source/allOf/1 $ref
SURVIVED     0 failing, 0 erroring    schema /$defs/record/properties/capturedFrom type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/capturedFrom minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/capturedFrom allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/baselineMissing type
KILLED       2 failing, 0 erroring    schema /$defs/record/allOf/0 if
KILLED       2 failing, 0 erroring    schema /$defs/record/allOf/0 then
SURVIVED     0 failing, 0 erroring    schema /$defs/record/allOf/0/if required
KILLED       21 failing, 0 erroring   schema /$defs/record/allOf/0/if properties.kind
KILLED       21 failing, 0 erroring   schema /$defs/record/allOf/0/if/properties/kind const
KILLED       2 failing, 0 erroring    schema /$defs/record/allOf/0/then required
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/1 if
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/1 then
SURVIVED     0 failing, 0 erroring    schema /$defs/record/allOf/1/if required
KILLED       21 failing, 0 erroring   schema /$defs/record/allOf/1/if properties.kind
KILLED       21 failing, 0 erroring   schema /$defs/record/allOf/1/if/properties/kind const
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/1/then required
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2 if
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2 then
KILLED       20 failing, 0 erroring   schema /$defs/record/allOf/2/if required
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2/if properties.source
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2/if/properties/source pattern
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2/then required
KILLED       1 failing, 95 erroring   schema /$defs/noLink not
KILLED       2 failing, 95 erroring   schema /$defs/noLink/not pattern
SURVIVED     0 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 1 of 7: [A-Za-z][A-Za-z0-9+.-]*://
SURVIVED     0 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 2 of 7: [Ww][Ww][Ww]\.
SURVIVED     0 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 3 of 7: [Mm][Aa][Ii][Ll][Tt][Oo]:
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 4 of 7: [A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+/
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 5 of 7: [A-Za-z0-9-]+\.([Cc][Oo][Mm]|[Oo][Rr][Gg]|[Nn][Ee][Tt]|[Gg][
KILLED       3 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 6 of 7: [\\/][\\/][^\s\\/]
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 7 of 7: [A-Za-z][A-Za-z0-9+.-]*:[\\/]
KILLED       5 failing, 1 erroring    schema /$defs/noControl not
KILLED       24 failing, 3 erroring   schema /$defs/noControl/not pattern
KILLED       6 failing, 0 erroring    schema /$defs/noControl/not pattern alternative 1 of 2: [\u0000-\u001F\u007F-\u009F\u00AD\u034F\u0600-\u0605\u061C\u
KILLED       1 failing, 0 erroring    schema /$defs/noControl/not pattern alternative 2 of 2: [^\u0000-\uFFFF]
KILLED       15 failing, 1 erroring   schema /$defs/noHost not
KILLED       22 failing, 5 erroring   schema /$defs/noHost/not pattern
KILLED       2 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 1 of 9: [\u00aa\u00b2-\u00b3\u00b9-\u00ba\u00bc-\u00be\u0132-\u0133\
SURVIVED     0 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 2 of 9: 0[xX][0-9A-Fa-f]*[.\u2024\u2025\u2026\u2488\u2489\u248a\u248
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 3 of 9: [.\u2024\u2025\u2026\u2488\u2489\u248a\u248b\u248c\u248d\u24
KILLED       9 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 4 of 9: (?:^(?:(?:^|(?<=[\s(\[\x22\x27\u201c\u2018]))=[ \t]*(?![ \t]
SURVIVED     0 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 5 of 9: (?<![0-9])[.\u2024\u2025\u2026\u2488\u2489\u248a\u248b\u248c
KILLED       2 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 6 of 9: \d+[.\u2024\u2025\u2026\u2488\u2489\u248a\u248b\u248c\u248d\
KILLED       3 failing, 1 erroring    schema /$defs/noHost/not pattern alternative 7 of 9: (?:^(?:(?:^|(?<=[\s(\[\x22\x27\u201c\u2018]))=[ \t]*(?![ \t]
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 8 of 9: [0-9A-Fa-f]{0,4}[:\u2a74\ufe13\ufe55\uff1a][:\u2a74\ufe13\uf
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 9 of 9: [0-9A-Fa-f]{1,4}([:\u2a74\ufe13\ufe55\uff1a][0-9A-Fa-f]{1,4}
KILLED       1 failing, 0 erroring    schema /$defs/noColon not
KILLED       24 failing, 1 erroring   schema /$defs/noColon/not pattern
rules: 271, killed: 222, other outcomes: 7
survivors: 42
```

## Second run

`python -B scripts/mutation-sweep-inventory.py` on commit `3dea566` (2026-11-13, through `bosun`, 57 minutes with four workers): every rule killed, no survivor and no other outcome; exit 0.

What changed between the runs (commits `d8cd2f3` and `3dea566`):

- Each of the 42 survivors and the 7 erroring removals has a test in `scripts/tests/test_check_inventory.py` that fails by assertion without the rule. A rule that stands before a lookup which raises without it (the end of the text inside an unfinished call, an orphan parent, a missing target) is held by a run of the checker as a program, whose printed lines the test reads; the two rules whose first test raised before reaching its assertion have tests of their own.
- Two rules of the first run are no longer rules, which is why 271 became 270 with one added. The guard for a string that never closes inside `unfinished_call` could decide nothing (the loop's own end-of-text guard refuses first), so it was removed; and with it gone, the `if` that skips a string no longer refuses anything itself, so the sweep no longer lists it (its two tests still hold it). The added rule is `condition`'s `maxLength`, which the schema lacked.
- `unfinished_call` now takes only a call whose hyphen is glued on both sides, after a name, a number, `)` or `]`. As first committed it refused 1,728 generated texts that noHost's pattern accepts (a hyphen with a space beside it) and missed a deep call after `)` or `]`; `test_nesting_depth_never_changes_the_address_verdict` holds both.

What the sweep does not prove: the alternation bars nested inside noHost's top-level alternatives are not removed one by one (see the top of this record), and a rule is one guard, keyword, `properties` entry or top-level alternative, so logic that refuses nothing by itself (a loop bound, the string skip above) is held by the tests that name it, not by this sweep.

```text
unmutated: 131 tests pass in 33 s; 270 rules
KILLED       1 failing, 3 erroring    guard check-inventory.py:267 if i >= len(text)
KILLED       1 failing, 0 erroring    guard check-inventory.py:279 if depth and c in '")'
KILLED       1 failing, 0 erroring    guard check-inventory.py:284 if k < len(text) and text[k] not in AFTER_ARGUMENT and (not (c == ')' and spaced and (text[k]
KILLED       63 failing, 0 erroring   guard check-inventory.py:293 if '$ref' in schema
KILLED       2 failing, 0 erroring    guard check-inventory.py:295 if schema['$ref'] == '#/$defs/noHost' and isinstance(value, str) and (not problems)
KILLED       2 failing, 0 erroring    guard check-inventory.py:297 if call
KILLED       9 failing, 0 erroring    guard check-inventory.py:301 if 'type' in schema and (not type_ok(value, schema['type']))
KILLED       23 failing, 0 erroring   guard check-inventory.py:303 if 'const' in schema and value != schema['const']
KILLED       3 failing, 0 erroring    guard check-inventory.py:305 if 'enum' in schema and value not in schema['enum']
KILLED       41 failing, 0 erroring   guard check-inventory.py:307 if isinstance(value, str)
KILLED       2 failing, 0 erroring    guard check-inventory.py:308 if len(value) < schema.get('minLength', 0)
KILLED       2 failing, 0 erroring    guard check-inventory.py:310 if len(value) > schema.get('maxLength', len(value))
KILLED       38 failing, 1 erroring   guard check-inventory.py:313 if 'pattern' in schema and (not ecma(schema['pattern']).search(utf16(value)))
KILLED       2 failing, 0 erroring    guard check-inventory.py:315 if isinstance(value, (int, Decimal)) and (not isinstance(value, bool)) and (value < schema.ge
KILLED       63 failing, 0 erroring   guard check-inventory.py:317 if isinstance(value, list) and 'items' in schema
KILLED       62 failing, 0 erroring   guard check-inventory.py:320 if isinstance(value, dict)
KILLED       11 failing, 0 erroring   guard check-inventory.py:322 if key not in value
KILLED       69 failing, 0 erroring   guard check-inventory.py:326 if key in props
KILLED       4 failing, 0 erroring    guard check-inventory.py:328 if schema.get('additionalProperties', True) is False
KILLED       1 failing, 0 erroring    guard check-inventory.py:331 if key in value
KILLED       27 failing, 1 erroring   guard check-inventory.py:333 if 'not' in schema and (not validate(value, schema['not'], root, path))
KILLED       4 failing, 0 erroring    guard check-inventory.py:336 if 'if' in sub
KILLED       4 failing, 0 erroring    guard check-inventory.py:337 if not validate(value, sub['if'], root, path)
KILLED       4 failing, 0 erroring    guard check-inventory.py:365 if isinstance(item, str)
KILLED       4 failing, 0 erroring    guard check-inventory.py:369 if hit
KILLED       3 failing, 0 erroring    guard check-inventory.py:371 if found <= LINKS_SHOWN
KILLED       1 failing, 0 erroring    guard check-inventory.py:381 if found > LINKS_SHOWN
KILLED       1 failing, 1 erroring    guard check-inventory.py:404 if own and len(pinned) != 1
KILLED       1 failing, 0 erroring    guard check-inventory.py:497 if entry.is_symlink() or (hasattr(entry, 'is_junction') and entry.is_junction())
KILLED       1 failing, 0 erroring    guard check-inventory.py:534 if not data['rows']
KILLED       1 failing, 0 erroring    guard check-inventory.py:536 if sources and data['source'] != f"baseline:{sources.get('commit')}"
KILLED       1 failing, 0 erroring    guard check-inventory.py:540 if data['columns'] != expected
KILLED       1 failing, 0 erroring    guard check-inventory.py:545 if len(row) != len(expected)
KILLED       1 failing, 1 erroring    guard check-inventory.py:549 if name == 'window' and (not isinstance(cell, str))
KILLED       1 failing, 0 erroring    guard check-inventory.py:552 if name == 'window' and sources and (cell not in windows)
KILLED       1 failing, 1 erroring    guard check-inventory.py:604 if manifest and (not (isinstance(sources, dict) and isinstance(sources.get('commit'), str) an
KILLED       5 failing, 0 erroring    guard check-inventory.py:609 if manifest
KILLED       2 failing, 0 erroring    guard check-inventory.py:614 if reference_commit and sources['commit'] != reference_commit
KILLED       2 failing, 0 erroring    guard check-inventory.py:619 if bad or not hex40.fullmatch(sources['commit'])
KILLED       1 failing, 0 erroring    guard check-inventory.py:627 if missing or extra or (not windows)
KILLED       2 failing, 0 erroring    guard check-inventory.py:637 if whole and sources is not None
KILLED       1 failing, 3 erroring    guard check-inventory.py:640 if not path.is_file()
KILLED       1 failing, 0 erroring    guard check-inventory.py:642 if app == 'outlook' and sources
KILLED       1 failing, 0 erroring    guard check-inventory.py:651 if absent
KILLED       3 failing, 0 erroring    guard check-inventory.py:656 if is_baseline(f)
KILLED       1 failing, 0 erroring    guard check-inventory.py:664 if is_shell_chrome(f, data)
KILLED       1 failing, 0 erroring    guard check-inventory.py:666 if is_word_ribbon(f, inventory)
KILLED       1 failing, 0 erroring    guard check-inventory.py:668 if is_word_backstage(f, inventory)
KILLED       1 failing, 0 erroring    guard check-inventory.py:670 if is_word_shortcuts(f, inventory)
KILLED       3 failing, 0 erroring    guard check-inventory.py:681 if isinstance(rid, str)
KILLED       2 failing, 0 erroring    guard check-inventory.py:682 if len(seen.get(rid, [])) > 1
KILLED       1 failing, 0 erroring    guard check-inventory.py:687 if isinstance(rec.get('app'), str) and rid.split('.', 1)[0] != rec['app']
KILLED       2 failing, 0 erroring    guard check-inventory.py:689 if isinstance(rid, str) and rid in parents
KILLED       2 failing, 0 erroring    guard check-inventory.py:691 if loop
KILLED       4 failing, 0 erroring    guard check-inventory.py:694 if isinstance(profile, str) and profile not in profiles
KILLED       1 failing, 0 erroring    guard check-inventory.py:696 if isinstance(build, str) and build not in builds
KILLED       1 failing, 0 erroring    guard check-inventory.py:701 if pinned and (not baseline_commit.startswith(pinned.group(1)))
KILLED       1 failing, 0 erroring    guard check-inventory.py:704 if stamped and stamped.group(1) not in builds
KILLED       1 failing, 0 erroring    guard check-inventory.py:706 if stamped and isinstance(build, str) and (stamped.group(1) != build)
KILLED       1 failing, 6 erroring    guard check-inventory.py:709 if isinstance(parent, str) and parent not in seen
KILLED       2 failing, 0 erroring    guard check-inventory.py:711 if isinstance(parent, str) and len(seen[parent]) > 1
KILLED       5 failing, 0 erroring    guard check-inventory.py:714 if isinstance(target, str)
KILLED       1 failing, 6 erroring    guard check-inventory.py:715 if target not in kinds
KILLED       1 failing, 0 erroring    guard check-inventory.py:717 if len(seen[target]) > 1
KILLED       1 failing, 0 erroring    guard check-inventory.py:719 if kinds[target] not in TARGET_KINDS and (not (rec.get('kind') == 'backstagePage' and kinds[t
KILLED       2 failing, 0 erroring    guard check-inventory.py:723 if require_behaviour and rec.get('kind') in ('contextualTab', 'control', 'menuItem')
KILLED       2 failing, 0 erroring    guard check-inventory.py:724 if not str(rec.get('behaviour', '')).strip(ECMA_SPACE)
KILLED       1 failing, 0 erroring    schema / type
KILLED       63 failing, 0 erroring   schema / items
KILLED       63 failing, 0 erroring   schema /items $ref
KILLED       1 failing, 0 erroring    schema /$defs/record type
KILLED       5 failing, 0 erroring    schema /$defs/record required
KILLED       3 failing, 0 erroring    schema /$defs/record additionalProperties
KILLED       1 failing, 0 erroring    schema /$defs/record dependentRequired
KILLED       4 failing, 0 erroring    schema /$defs/record allOf
KILLED       37 failing, 1 erroring   schema /$defs/record properties.id
KILLED       31 failing, 2 erroring   schema /$defs/record properties.app
KILLED       31 failing, 1 erroring   schema /$defs/record properties.kind
KILLED       50 failing, 0 erroring   schema /$defs/record properties.label
KILLED       28 failing, 1 erroring   schema /$defs/record properties.parent
KILLED       33 failing, 1 erroring   schema /$defs/record properties.order
KILLED       20 failing, 1 erroring   schema /$defs/record properties.controlType
KILLED       21 failing, 1 erroring   schema /$defs/record properties.size
KILLED       23 failing, 1 erroring   schema /$defs/record properties.keytip
KILLED       24 failing, 1 erroring   schema /$defs/record properties.shortcut
KILLED       2 failing, 0 erroring    schema /$defs/record properties.scope
KILLED       7 failing, 0 erroring    schema /$defs/record properties.condition
KILLED       3 failing, 0 erroring    schema /$defs/record properties.itemCount
KILLED       8 failing, 0 erroring    schema /$defs/record properties.target
KILLED       7 failing, 0 erroring    schema /$defs/record properties.menuPath
KILLED       23 failing, 1 erroring   schema /$defs/record properties.bounds
KILLED       23 failing, 1 erroring   schema /$defs/record properties.captureProfile
KILLED       15 failing, 0 erroring   schema /$defs/record properties.behaviour
KILLED       24 failing, 1 erroring   schema /$defs/record properties.idMso
KILLED       9 failing, 0 erroring    schema /$defs/record properties.uiaId
KILLED       27 failing, 1 erroring   schema /$defs/record properties.source
KILLED       25 failing, 1 erroring   schema /$defs/record properties.capturedFrom
KILLED       2 failing, 0 erroring    schema /$defs/record properties.baselineMissing
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/id pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/id allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/app enum
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/kind enum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/label type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/label minLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/label maxLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/label pattern
KILLED       24 failing, 0 erroring   schema /$defs/record/properties/label allOf
KILLED       5 failing, 0 erroring    schema /$defs/record/properties/label/allOf/0 $ref
KILLED       5 failing, 0 erroring    schema /$defs/record/properties/label/allOf/1 $ref
KILLED       16 failing, 0 erroring   schema /$defs/record/properties/label/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/parent allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent/allOf/2 $ref
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/order type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/order minimum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/controlType enum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/size enum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/keytip minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/keytip allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/shortcut minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut pattern
KILLED       4 failing, 0 erroring    schema /$defs/record/properties/shortcut allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut/allOf/0 $ref
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/shortcut/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/scope enum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/condition allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/itemCount type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/itemCount minimum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/target allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath pattern
KILLED       4 failing, 0 erroring    schema /$defs/record/properties/menuPath allOf
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/menuPath/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/bounds required
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds additionalProperties
KILLED       19 failing, 1 erroring   schema /$defs/record/properties/bounds properties.x
KILLED       19 failing, 1 erroring   schema /$defs/record/properties/bounds properties.y
KILLED       20 failing, 1 erroring   schema /$defs/record/properties/bounds properties.width
KILLED       19 failing, 1 erroring   schema /$defs/record/properties/bounds properties.height
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/x type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/y type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/width type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/width minimum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/height type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/height minimum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/captureProfile minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/captureProfile allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/behaviour type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/behaviour minLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/behaviour maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/behaviour pattern
KILLED       6 failing, 1 erroring    schema /$defs/record/properties/behaviour allOf
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/behaviour/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/behaviour/allOf/1 $ref
KILLED       3 failing, 1 erroring    schema /$defs/record/properties/behaviour/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/idMso type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/idMso minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/idMso maxLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/idMso pattern
KILLED       4 failing, 0 erroring    schema /$defs/record/properties/idMso allOf
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/idMso/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/idMso/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/idMso/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/uiaId type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/uiaId minLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/uiaId maxLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/uiaId pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/uiaId allOf
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/uiaId/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/uiaId/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/uiaId/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/source type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/source maxLength
KILLED       6 failing, 0 erroring    schema /$defs/record/properties/source pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/source allOf
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/source/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/source/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/capturedFrom minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/capturedFrom allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/baselineMissing type
KILLED       2 failing, 0 erroring    schema /$defs/record/allOf/0 if
KILLED       2 failing, 0 erroring    schema /$defs/record/allOf/0 then
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/0/if required
KILLED       23 failing, 0 erroring   schema /$defs/record/allOf/0/if properties.kind
KILLED       23 failing, 0 erroring   schema /$defs/record/allOf/0/if/properties/kind const
KILLED       2 failing, 0 erroring    schema /$defs/record/allOf/0/then required
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/1 if
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/1 then
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/1/if required
KILLED       23 failing, 0 erroring   schema /$defs/record/allOf/1/if properties.kind
KILLED       23 failing, 0 erroring   schema /$defs/record/allOf/1/if/properties/kind const
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/1/then required
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2 if
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2 then
KILLED       23 failing, 0 erroring   schema /$defs/record/allOf/2/if required
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2/if properties.source
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2/if/properties/source pattern
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2/then required
KILLED       3 failing, 99 erroring   schema /$defs/noLink not
KILLED       7 failing, 100 erroring  schema /$defs/noLink/not pattern
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 1 of 7: [A-Za-z][A-Za-z0-9+.-]*://
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 2 of 7: [Ww][Ww][Ww]\.
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 3 of 7: [Mm][Aa][Ii][Ll][Tt][Oo]:
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 4 of 7: [A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+/
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 5 of 7: [A-Za-z0-9-]+\.([Cc][Oo][Mm]|[Oo][Rr][Gg]|[Nn][Ee][Tt]|[Gg][
KILLED       3 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 6 of 7: [\\/][\\/][^\s\\/]
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 7 of 7: [A-Za-z][A-Za-z0-9+.-]*:[\\/]
KILLED       5 failing, 1 erroring    schema /$defs/noControl not
KILLED       31 failing, 3 erroring   schema /$defs/noControl/not pattern
KILLED       6 failing, 0 erroring    schema /$defs/noControl/not pattern alternative 1 of 2: [\u0000-\u001F\u007F-\u009F\u00AD\u034F\u0600-\u0605\u061C\u
KILLED       1 failing, 0 erroring    schema /$defs/noControl/not pattern alternative 2 of 2: [^\u0000-\uFFFF]
KILLED       17 failing, 2 erroring   schema /$defs/noHost not
KILLED       29 failing, 6 erroring   schema /$defs/noHost/not pattern
KILLED       2 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 1 of 9: [\u00aa\u00b2-\u00b3\u00b9-\u00ba\u00bc-\u00be\u0132-\u0133\
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 2 of 9: 0[xX][0-9A-Fa-f]*[.\u2024\u2025\u2026\u2488\u2489\u248a\u248
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 3 of 9: [.\u2024\u2025\u2026\u2488\u2489\u248a\u248b\u248c\u248d\u24
KILLED       11 failing, 0 erroring   schema /$defs/noHost/not pattern alternative 4 of 9: (?:^(?:(?:^|(?<=[\s(\[\x22\x27\u201c\u2018]))=[ \t]*(?![ \t]
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 5 of 9: (?<![0-9])[.\u2024\u2025\u2026\u2488\u2489\u248a\u248b\u248c
KILLED       2 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 6 of 9: \d+[.\u2024\u2025\u2026\u2488\u2489\u248a\u248b\u248c\u248d\
KILLED       3 failing, 1 erroring    schema /$defs/noHost/not pattern alternative 7 of 9: (?:^(?:(?:^|(?<=[\s(\[\x22\x27\u201c\u2018]))=[ \t]*(?![ \t]
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 8 of 9: [0-9A-Fa-f]{0,4}[:\u2a74\ufe13\ufe55\uff1a][:\u2a74\ufe13\uf
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 9 of 9: [0-9A-Fa-f]{1,4}([:\u2a74\ufe13\ufe55\uff1a][0-9A-Fa-f]{1,4}
KILLED       1 failing, 0 erroring    schema /$defs/noColon not
KILLED       31 failing, 1 erroring   schema /$defs/noColon/not pattern
rules: 270, killed: 270, other outcomes: 0
survivors: 0
```

## Third run

`python -B scripts/mutation-sweep-inventory.py` on commit `ee2e913` (2026-11-13, through `bosun`, 62 minutes with four workers), after the review round's fix: every rule killed, no survivor and no other outcome; exit 0. This is the run of the code the section ships.

What changed since the second run (commit `ee2e913`, round 1, finding 1): `unfinished_call` no longer judges what may follow an inner call with lists of its own, which refused a parenthesis inside a quoted sheet name. It requires the call to close (parentheses counted outside both kinds of quotes), measures on noHost's pattern the depth the pattern counts, and from that depth has the pattern read each level of the call. Its three refusing guards, and the guard in `validate` that hands it the pattern, are the rules that make 270 into 271.

```text
unmutated: 133 tests pass in 44 s; 271 rules
KILLED       1 failing, 3 erroring    guard check-inventory.py:335 if groups is None
KILLED       2 failing, 0 erroring    guard check-inventory.py:339 if depth >= counted_depth(name, host)
KILLED       2 failing, 0 erroring    guard check-inventory.py:345 if host.search(utf16(alone))
KILLED       64 failing, 0 erroring   guard check-inventory.py:354 if '$ref' in schema
KILLED       3 failing, 0 erroring    guard check-inventory.py:357 if schema['$ref'] == '#/$defs/noHost' and isinstance(value, str) and (not problems)
KILLED       3 failing, 0 erroring    guard check-inventory.py:359 if pattern
KILLED       3 failing, 0 erroring    guard check-inventory.py:361 if reason
KILLED       9 failing, 0 erroring    guard check-inventory.py:365 if 'type' in schema and (not type_ok(value, schema['type']))
KILLED       24 failing, 0 erroring   guard check-inventory.py:367 if 'const' in schema and value != schema['const']
KILLED       3 failing, 0 erroring    guard check-inventory.py:369 if 'enum' in schema and value not in schema['enum']
KILLED       44 failing, 0 erroring   guard check-inventory.py:371 if isinstance(value, str)
KILLED       2 failing, 0 erroring    guard check-inventory.py:372 if len(value) < schema.get('minLength', 0)
KILLED       2 failing, 0 erroring    guard check-inventory.py:374 if len(value) > schema.get('maxLength', len(value))
KILLED       41 failing, 1 erroring   guard check-inventory.py:377 if 'pattern' in schema and (not ecma(schema['pattern']).search(utf16(value)))
KILLED       2 failing, 0 erroring    guard check-inventory.py:379 if isinstance(value, (int, Decimal)) and (not isinstance(value, bool)) and (value < schema.ge
KILLED       64 failing, 0 erroring   guard check-inventory.py:381 if isinstance(value, list) and 'items' in schema
KILLED       63 failing, 0 erroring   guard check-inventory.py:384 if isinstance(value, dict)
KILLED       11 failing, 0 erroring   guard check-inventory.py:386 if key not in value
KILLED       72 failing, 0 erroring   guard check-inventory.py:390 if key in props
KILLED       4 failing, 0 erroring    guard check-inventory.py:392 if schema.get('additionalProperties', True) is False
KILLED       1 failing, 0 erroring    guard check-inventory.py:395 if key in value
KILLED       27 failing, 1 erroring   guard check-inventory.py:397 if 'not' in schema and (not validate(value, schema['not'], root, path))
KILLED       4 failing, 0 erroring    guard check-inventory.py:400 if 'if' in sub
KILLED       4 failing, 0 erroring    guard check-inventory.py:401 if not validate(value, sub['if'], root, path)
KILLED       4 failing, 0 erroring    guard check-inventory.py:429 if isinstance(item, str)
KILLED       4 failing, 0 erroring    guard check-inventory.py:433 if hit
KILLED       3 failing, 0 erroring    guard check-inventory.py:435 if found <= LINKS_SHOWN
KILLED       1 failing, 0 erroring    guard check-inventory.py:445 if found > LINKS_SHOWN
KILLED       1 failing, 1 erroring    guard check-inventory.py:468 if own and len(pinned) != 1
KILLED       1 failing, 0 erroring    guard check-inventory.py:561 if entry.is_symlink() or (hasattr(entry, 'is_junction') and entry.is_junction())
KILLED       1 failing, 0 erroring    guard check-inventory.py:598 if not data['rows']
KILLED       1 failing, 0 erroring    guard check-inventory.py:600 if sources and data['source'] != f"baseline:{sources.get('commit')}"
KILLED       1 failing, 0 erroring    guard check-inventory.py:604 if data['columns'] != expected
KILLED       1 failing, 0 erroring    guard check-inventory.py:609 if len(row) != len(expected)
KILLED       1 failing, 1 erroring    guard check-inventory.py:613 if name == 'window' and (not isinstance(cell, str))
KILLED       1 failing, 0 erroring    guard check-inventory.py:616 if name == 'window' and sources and (cell not in windows)
KILLED       1 failing, 1 erroring    guard check-inventory.py:668 if manifest and (not (isinstance(sources, dict) and isinstance(sources.get('commit'), str) an
KILLED       5 failing, 0 erroring    guard check-inventory.py:673 if manifest
KILLED       2 failing, 0 erroring    guard check-inventory.py:678 if reference_commit and sources['commit'] != reference_commit
KILLED       2 failing, 0 erroring    guard check-inventory.py:683 if bad or not hex40.fullmatch(sources['commit'])
KILLED       1 failing, 0 erroring    guard check-inventory.py:691 if missing or extra or (not windows)
KILLED       2 failing, 0 erroring    guard check-inventory.py:701 if whole and sources is not None
KILLED       1 failing, 3 erroring    guard check-inventory.py:704 if not path.is_file()
KILLED       1 failing, 0 erroring    guard check-inventory.py:706 if app == 'outlook' and sources
KILLED       1 failing, 0 erroring    guard check-inventory.py:715 if absent
KILLED       3 failing, 0 erroring    guard check-inventory.py:720 if is_baseline(f)
KILLED       1 failing, 0 erroring    guard check-inventory.py:728 if is_shell_chrome(f, data)
KILLED       1 failing, 0 erroring    guard check-inventory.py:730 if is_word_ribbon(f, inventory)
KILLED       1 failing, 0 erroring    guard check-inventory.py:732 if is_word_backstage(f, inventory)
KILLED       1 failing, 0 erroring    guard check-inventory.py:734 if is_word_shortcuts(f, inventory)
KILLED       3 failing, 0 erroring    guard check-inventory.py:745 if isinstance(rid, str)
KILLED       2 failing, 0 erroring    guard check-inventory.py:746 if len(seen.get(rid, [])) > 1
KILLED       1 failing, 0 erroring    guard check-inventory.py:751 if isinstance(rec.get('app'), str) and rid.split('.', 1)[0] != rec['app']
KILLED       2 failing, 0 erroring    guard check-inventory.py:753 if isinstance(rid, str) and rid in parents
KILLED       2 failing, 0 erroring    guard check-inventory.py:755 if loop
KILLED       4 failing, 0 erroring    guard check-inventory.py:758 if isinstance(profile, str) and profile not in profiles
KILLED       1 failing, 0 erroring    guard check-inventory.py:760 if isinstance(build, str) and build not in builds
KILLED       1 failing, 0 erroring    guard check-inventory.py:765 if pinned and (not baseline_commit.startswith(pinned.group(1)))
KILLED       1 failing, 0 erroring    guard check-inventory.py:768 if stamped and stamped.group(1) not in builds
KILLED       1 failing, 0 erroring    guard check-inventory.py:770 if stamped and isinstance(build, str) and (stamped.group(1) != build)
KILLED       1 failing, 6 erroring    guard check-inventory.py:773 if isinstance(parent, str) and parent not in seen
KILLED       2 failing, 0 erroring    guard check-inventory.py:775 if isinstance(parent, str) and len(seen[parent]) > 1
KILLED       5 failing, 0 erroring    guard check-inventory.py:778 if isinstance(target, str)
KILLED       1 failing, 6 erroring    guard check-inventory.py:779 if target not in kinds
KILLED       1 failing, 0 erroring    guard check-inventory.py:781 if len(seen[target]) > 1
KILLED       1 failing, 0 erroring    guard check-inventory.py:783 if kinds[target] not in TARGET_KINDS and (not (rec.get('kind') == 'backstagePage' and kinds[t
KILLED       2 failing, 0 erroring    guard check-inventory.py:787 if require_behaviour and rec.get('kind') in ('contextualTab', 'control', 'menuItem')
KILLED       2 failing, 0 erroring    guard check-inventory.py:788 if not str(rec.get('behaviour', '')).strip(ECMA_SPACE)
KILLED       1 failing, 0 erroring    schema / type
KILLED       64 failing, 0 erroring   schema / items
KILLED       64 failing, 0 erroring   schema /items $ref
KILLED       1 failing, 0 erroring    schema /$defs/record type
KILLED       5 failing, 0 erroring    schema /$defs/record required
KILLED       3 failing, 0 erroring    schema /$defs/record additionalProperties
KILLED       1 failing, 0 erroring    schema /$defs/record dependentRequired
KILLED       4 failing, 0 erroring    schema /$defs/record allOf
KILLED       40 failing, 1 erroring   schema /$defs/record properties.id
KILLED       34 failing, 2 erroring   schema /$defs/record properties.app
KILLED       34 failing, 1 erroring   schema /$defs/record properties.kind
KILLED       53 failing, 0 erroring   schema /$defs/record properties.label
KILLED       30 failing, 1 erroring   schema /$defs/record properties.parent
KILLED       35 failing, 1 erroring   schema /$defs/record properties.order
KILLED       22 failing, 1 erroring   schema /$defs/record properties.controlType
KILLED       23 failing, 1 erroring   schema /$defs/record properties.size
KILLED       25 failing, 1 erroring   schema /$defs/record properties.keytip
KILLED       26 failing, 1 erroring   schema /$defs/record properties.shortcut
KILLED       2 failing, 0 erroring    schema /$defs/record properties.scope
KILLED       7 failing, 0 erroring    schema /$defs/record properties.condition
KILLED       3 failing, 0 erroring    schema /$defs/record properties.itemCount
KILLED       8 failing, 0 erroring    schema /$defs/record properties.target
KILLED       7 failing, 0 erroring    schema /$defs/record properties.menuPath
KILLED       25 failing, 1 erroring   schema /$defs/record properties.bounds
KILLED       25 failing, 1 erroring   schema /$defs/record properties.captureProfile
KILLED       18 failing, 0 erroring   schema /$defs/record properties.behaviour
KILLED       26 failing, 1 erroring   schema /$defs/record properties.idMso
KILLED       9 failing, 0 erroring    schema /$defs/record properties.uiaId
KILLED       29 failing, 1 erroring   schema /$defs/record properties.source
KILLED       27 failing, 1 erroring   schema /$defs/record properties.capturedFrom
KILLED       2 failing, 0 erroring    schema /$defs/record properties.baselineMissing
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/id pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/id allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/id/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/app enum
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/kind enum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/label type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/label minLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/label maxLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/label pattern
KILLED       24 failing, 0 erroring   schema /$defs/record/properties/label allOf
KILLED       5 failing, 0 erroring    schema /$defs/record/properties/label/allOf/0 $ref
KILLED       5 failing, 0 erroring    schema /$defs/record/properties/label/allOf/1 $ref
KILLED       16 failing, 0 erroring   schema /$defs/record/properties/label/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/parent allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/parent/allOf/2 $ref
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/order type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/order minimum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/controlType enum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/size enum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/keytip minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/keytip allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/keytip/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/shortcut minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut pattern
KILLED       4 failing, 0 erroring    schema /$defs/record/properties/shortcut allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut/allOf/0 $ref
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/shortcut/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/shortcut/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/scope enum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/condition allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/condition/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/itemCount type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/itemCount minimum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/target allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/target/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath pattern
KILLED       4 failing, 0 erroring    schema /$defs/record/properties/menuPath allOf
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/menuPath/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/menuPath/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/bounds required
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds additionalProperties
KILLED       21 failing, 1 erroring   schema /$defs/record/properties/bounds properties.x
KILLED       21 failing, 1 erroring   schema /$defs/record/properties/bounds properties.y
KILLED       22 failing, 1 erroring   schema /$defs/record/properties/bounds properties.width
KILLED       21 failing, 1 erroring   schema /$defs/record/properties/bounds properties.height
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/x type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/y type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/width type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/width minimum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/height type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/bounds/properties/height minimum
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/captureProfile minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/captureProfile allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/captureProfile/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/behaviour type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/behaviour minLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/behaviour maxLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/behaviour pattern
KILLED       7 failing, 1 erroring    schema /$defs/record/properties/behaviour allOf
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/behaviour/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/behaviour/allOf/1 $ref
KILLED       4 failing, 1 erroring    schema /$defs/record/properties/behaviour/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/idMso type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/idMso minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/idMso maxLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/idMso pattern
KILLED       4 failing, 0 erroring    schema /$defs/record/properties/idMso allOf
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/idMso/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/idMso/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/idMso/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/uiaId type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/uiaId minLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/uiaId maxLength
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/uiaId pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/uiaId allOf
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/uiaId/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/uiaId/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/uiaId/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/source type
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/source maxLength
KILLED       6 failing, 0 erroring    schema /$defs/record/properties/source pattern
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/source allOf
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/source/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/source/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom type
KILLED       2 failing, 0 erroring    schema /$defs/record/properties/capturedFrom minLength
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom maxLength
KILLED       3 failing, 0 erroring    schema /$defs/record/properties/capturedFrom allOf
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom/allOf/0 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom/allOf/1 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/capturedFrom/allOf/2 $ref
KILLED       1 failing, 0 erroring    schema /$defs/record/properties/baselineMissing type
KILLED       2 failing, 0 erroring    schema /$defs/record/allOf/0 if
KILLED       2 failing, 0 erroring    schema /$defs/record/allOf/0 then
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/0/if required
KILLED       24 failing, 0 erroring   schema /$defs/record/allOf/0/if properties.kind
KILLED       24 failing, 0 erroring   schema /$defs/record/allOf/0/if/properties/kind const
KILLED       2 failing, 0 erroring    schema /$defs/record/allOf/0/then required
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/1 if
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/1 then
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/1/if required
KILLED       24 failing, 0 erroring   schema /$defs/record/allOf/1/if properties.kind
KILLED       24 failing, 0 erroring   schema /$defs/record/allOf/1/if/properties/kind const
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/1/then required
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2 if
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2 then
KILLED       24 failing, 0 erroring   schema /$defs/record/allOf/2/if required
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2/if properties.source
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2/if/properties/source pattern
KILLED       1 failing, 0 erroring    schema /$defs/record/allOf/2/then required
KILLED       3 failing, 99 erroring   schema /$defs/noLink not
KILLED       10 failing, 100 erroring schema /$defs/noLink/not pattern
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 1 of 7: [A-Za-z][A-Za-z0-9+.-]*://
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 2 of 7: [Ww][Ww][Ww]\.
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 3 of 7: [Mm][Aa][Ii][Ll][Tt][Oo]:
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 4 of 7: [A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+/
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 5 of 7: [A-Za-z0-9-]+\.([Cc][Oo][Mm]|[Oo][Rr][Gg]|[Nn][Ee][Tt]|[Gg][
KILLED       3 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 6 of 7: [\\/][\\/][^\s\\/]
KILLED       1 failing, 0 erroring    schema /$defs/noLink/not pattern alternative 7 of 7: [A-Za-z][A-Za-z0-9+.-]*:[\\/]
KILLED       5 failing, 1 erroring    schema /$defs/noControl not
KILLED       34 failing, 3 erroring   schema /$defs/noControl/not pattern
KILLED       6 failing, 0 erroring    schema /$defs/noControl/not pattern alternative 1 of 2: [\u0000-\u001F\u007F-\u009F\u00AD\u034F\u0600-\u0605\u061C\u
KILLED       1 failing, 0 erroring    schema /$defs/noControl/not pattern alternative 2 of 2: [^\u0000-\uFFFF]
KILLED       19 failing, 4 erroring   schema /$defs/noHost not
KILLED       30 failing, 8 erroring   schema /$defs/noHost/not pattern
KILLED       2 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 1 of 9: [\u00aa\u00b2-\u00b3\u00b9-\u00ba\u00bc-\u00be\u0132-\u0133\
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 2 of 9: 0[xX][0-9A-Fa-f]*[.\u2024\u2025\u2026\u2488\u2489\u248a\u248
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 3 of 9: [.\u2024\u2025\u2026\u2488\u2489\u248a\u248b\u248c\u248d\u24
KILLED       13 failing, 0 erroring   schema /$defs/noHost/not pattern alternative 4 of 9: (?:^(?:(?:^|(?<=[\s(\[\x22\x27\u201c\u2018]))=[ \t]*(?![ \t]
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 5 of 9: (?<![0-9])[.\u2024\u2025\u2026\u2488\u2489\u248a\u248b\u248c
KILLED       2 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 6 of 9: \d+[.\u2024\u2025\u2026\u2488\u2489\u248a\u248b\u248c\u248d\
KILLED       3 failing, 1 erroring    schema /$defs/noHost/not pattern alternative 7 of 9: (?:^(?:(?:^|(?<=[\s(\[\x22\x27\u201c\u2018]))=[ \t]*(?![ \t]
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 8 of 9: [0-9A-Fa-f]{0,4}[:\u2a74\ufe13\ufe55\uff1a][:\u2a74\ufe13\uf
KILLED       1 failing, 0 erroring    schema /$defs/noHost/not pattern alternative 9 of 9: [0-9A-Fa-f]{1,4}([:\u2a74\ufe13\ufe55\uff1a][0-9A-Fa-f]{1,4}
KILLED       1 failing, 0 erroring    schema /$defs/noColon not
KILLED       34 failing, 1 erroring   schema /$defs/noColon/not pattern
rules: 271, killed: 271, other outcomes: 0
survivors: 0
```
