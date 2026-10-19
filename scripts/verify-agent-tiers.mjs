#!/usr/bin/env node
// Enforce the delegation tier invariant on this project's agent definitions.
//
// The rule is in AGENTS.md: mechanical subtasks delegate to subagents on the
// Sonnet tier; an elevated tier is reserved for work whose verdict quality
// demands it; Haiku is allowed only for near-mechanical work (at least 90%
// mechanical) whose output a script or the main loop verifies; and no subagent
// writes: subagents read and run, and the main loop makes every change.
//
// A rule stated in prose is protected by discipline. This makes it protected by
// a check: an agent with no `model:` line, an agent that could edit files, or a
// Haiku agent that does not meet every Haiku condition below, fails here instead
// of passing every gate and being noticed later, or never.
//
// An absent `model:` is an error rather than a default, because an unpinned
// agent silently inherits the caller's model: mechanical work then runs on the
// expensive tier with no signal at all, which is the exact regression this
// exists to catch.
//
// No dependencies and no repository-specific paths, so a bootstrapped project
// can run it from day one. With no agents defined yet it passes with nothing
// checked, and starts enforcing the moment the first definition appears.
//
//   node scripts/verify-agent-tiers.mjs

import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { isAbsolute, join, normalize, sep } from "node:path";

/**
 * Tier vocabulary.
 *
 * Kept as substrings rather than exact model IDs so a version bump (sonnet-5
 * to a later sonnet) does not silently fail a project that is still obeying
 * the rule. The tier is the invariant; the exact pin is a routing decision that
 * belongs elsewhere. Haiku is the exception: it must be an exact, versioned pin.
 */
export const BASE_AGENT_MODEL_TOKENS = ["sonnet"];
export const ELEVATED_AGENT_MODEL_TOKENS = ["opus", "fable"];
export const RESTRICTED_AGENT_MODEL_TOKENS = ["haiku"];

/**
 * The Haiku allowance, every condition required.
 *
 * - An exact pin of Haiku 5.5 or later (`claude-haiku-5-5`, optionally with a
 *   date suffix). The bare `haiku` alias is refused because it is not a version.
 * - `mechanical_share:` of 90 or more: the share of the agent's work that is
 *   mechanical (lookups, inventories, structural checks), declared so a reviewer
 *   can challenge it.
 * - `haiku_replay:` naming a file in this repository that records a replay on
 *   known-answer inputs showing no loss against the base tier.
 * - No judgment work in its name or description: never review, audit,
 *   research, security, debugging, diagnosis, planning or design.
 */
export const HAIKU_MINIMUM_VERSION = [5, 5];
export const HAIKU_PIN = /^claude-haiku-(\d+)-(\d+)(?:-\d{8})?$/;
export const HAIKU_MECHANICAL_FIELD = "mechanical_share";
export const HAIKU_MINIMUM_MECHANICAL_SHARE = 90;
export const HAIKU_REPLAY_FIELD = "haiku_replay";
export const HAIKU_JUDGMENT_TERMS = /\b(review|audit|research|secur|debug|diagnos|plan|design|architect|judg|verdict)/i;

/** Where an elevated pin must record why it is elevated. */
export const ELEVATION_RATIONALE_FIELD = "model_rationale";

/** The one key whose value may be a nested block: Claude Code's per-agent hooks. */
export const HOOKS_FIELD = "hooks";

/**
 * Tools no subagent on any tier is given. A `*` grant includes them, and so
 * does a missing `tools:` list, because the agent then inherits every tool.
 */
export const EDIT_TOOLS = ["edit", "write", "multiedit", "notebookedit"];

/**
 * Read the opening frontmatter as a strict, closed subset of YAML.
 *
 * Three review rounds on 2026-09-15 each found another way a regex over this
 * block reads a value that is not the value: a body line outside the
 * frontmatter, a trailing `# comment`, a comment inside quotes, an alias
 * (`model: *sonnet` resolving to a Haiku anchor), a `model:` line inside a
 * multi-line quoted scalar, a duplicate key read from the wrong end, and a
 * block scalar whose indentation indicator makes its only line empty. Chasing
 * them one at a time is how this file got to three rounds.
 *
 * So the reader models a deliberately small language and REFUSES everything
 * else. An agent definition's frontmatter is a handful of flat scalar keys; a
 * file using anchors, flow collections, tags or multi-line quoting is refused
 * as unreadable rather than guessed at. Failing closed on an exotic definition
 * costs whoever wrote it one plain rewrite. Failing open costs a run on the
 * wrong tier, silently, for as long as nobody looks.
 *
 * One nested key is accepted: `hooks:`, Claude Code's per-agent hooks, written
 * alone on its line and followed by an indented block. The block's content is
 * skipped, not read, and `hooks` is recorded as present. This is safe because
 * the only thing the skip has to get right is where the block ends: at the
 * first non-blank line at column 0, which is read as a top-level key again, so
 * a `model:` or `tools:` inside the block is not a pin and a second `model:`
 * after it is still a duplicate. The two ways YAML can carry a column-0 line as
 * the block's content, a quoted scalar or a flow collection spanning lines, are
 * refused line by line, as are tabs in the indentation (where YAML and this
 * reader would disagree on the column), anchors, aliases and tags, and any line
 * that is not a key, a sequence entry, a scalar or a comment. A block scalar's
 * own content is opaque text and is skipped. Every other nested block stays
 * refused.
 *
 * Returns `{ fields, error }`: `error` is set when the block cannot be read
 * under these rules, and `fields` maps key to `{ value, isQuoted }`.
 */
export function readAgentFrontmatter(text) {
  const match = /^---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/.exec(text);
  if (!match) return { fields: null, error: "has no opening frontmatter block; the tier pin must be a machine-read field, not prose" };

  const lines = match[1].split(/\r?\n/);
  const fields = new Map();
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    index += 1;
    if (line.trim() === "" || /^[ \t]*#/.test(line)) continue;

    // YAML needs whitespace after the colon in a block mapping: `model:sonnet`
    // is the plain scalar "model:sonnet", not a pin, and reading it as one let
    // a definition with no model field through.
    const entry = /^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]+([^\r\n]*?))?[ \t]*$/.exec(line);
    if (!entry) {
      return { fields: null, error: `frontmatter line ${JSON.stringify(line)} is not a plain "key: value" pair; agent frontmatter is read as a closed subset of YAML and anything else is refused rather than guessed` };
    }

    const [, key, rest = ""] = entry;
    if (fields.has(key)) {
      // This reader takes the first, a YAML parser takes the last. Refuse the
      // ambiguity rather than pick a winner: `model: sonnet` above
      // `model: claude-haiku-4-5` read as Sonnet and ran as Haiku.
      return { fields: null, error: `declares "${key}:" more than once; a duplicate key is read from opposite ends by this check and by YAML` };
    }

    if (key === HOOKS_FIELD) {
      if (!/^(?:#.*)?$/.test(rest)) {
        return { fields: null, error: `"${key}:" takes no inline value (${JSON.stringify(rest)}); write "${key}:" alone followed by an indented block, the one nested form this check reads` };
      }
      const block = skipHooksBlock(lines, index);
      if (block.error) return { fields: null, error: block.error };
      index = block.index;
      fields.set(key, { value: "", isQuoted: false, isBlock: true });
      continue;
    }

    // A comment after the value is ordinary YAML, and rejecting it would fail
    // correct definitions. It is stripped here, outside the quoted region, so
    // `model: "sonnet # haiku"` still keeps its hash as content.
    const quotedWithComment = /^((["'])(?:[^\\]|\\.)*?\2)[ \t]+#[^\r\n]*$/.exec(rest);
    const scalarWithComment = /^([|>][-+0-9]*)[ \t]+#[^\r\n]*$/.exec(rest);
    const value = quotedWithComment?.[1] ?? scalarWithComment?.[1] ?? rest;

    if (/^[|>]$/.test(value)) {
      // A bare block scalar only. An indentation indicator (`|2`) changes what
      // counts as content, and this reader does not model that.
      const collected = [];
      while (index < lines.length && (lines[index].trim() === "" || /^[ \t]/.test(lines[index]))) {
        collected.push(lines[index].trim());
        index += 1;
      }
      fields.set(key, { value: collected.filter(Boolean).join(" "), isQuoted: true });
      continue;
    }

    if (/^[|>]/.test(value)) {
      return { fields: null, error: `"${key}:" uses a block scalar indicator (${JSON.stringify(value)}); write the value plainly so this check and YAML agree on where it ends` };
    }

    const quoted = /^(["'])((?:[^\\]|\\.)*?)\1[ \t]*$/.exec(value);
    if (quoted) {
      if (/\\/.test(quoted[2])) {
        return { fields: null, error: `"${key}:" contains a backslash escape; this check does not decode escapes, so write the value plainly` };
      }
      fields.set(key, { value: quoted[2].trim(), isQuoted: true });
      continue;
    }

    if (/^["']/.test(value)) {
      return { fields: null, error: `"${key}:" opens a quote that does not close on the same line; a multi-line quoted scalar can hide another key inside it` };
    }

    const plain = value.replace(/(?:^|[ \t])#.*$/, "").trim();
    if (/^[&*!]/.test(plain) || /^[[{]/.test(plain)) {
      return { fields: null, error: `"${key}:" uses YAML ${plain.startsWith("[") || plain.startsWith("{") ? "flow collection" : "anchor, alias or tag"} syntax (${JSON.stringify(plain)}); write the value plainly, because an alias resolves to something this check cannot see` };
    }
    fields.set(key, { value: plain, isQuoted: false });
  }

  return { fields, error: null };
}

/**
 * Skip the indented block under `hooks:`, starting at `start`, and return the
 * index of the first line after it. The block ends at the first non-blank line
 * at column 0. Each line inside is checked by `hooksLineProblem` so none of
 * them can make YAML read a later column-0 line as part of the block.
 */
function skipHooksBlock(lines, start) {
  let index = start;
  let content = 0;
  let scalarIndent = null;
  while (index < lines.length) {
    const line = lines[index];
    if (line.trim() === "") {
      index += 1;
      continue;
    }
    if (!/^[ \t]/.test(line)) break;

    const indentation = /^[ \t]*/.exec(line)[0];
    if (indentation.includes("\t")) {
      return { index, error: `"${HOOKS_FIELD}:" block line ${JSON.stringify(line)} is indented with a tab; YAML refuses tab indentation and this check would read a different column, so indent with spaces` };
    }
    index += 1;
    content += 1;

    // A block scalar's content is text, not structure, and ends at the first
    // line indented no deeper than the line that opened it.
    if (scalarIndent !== null && indentation.length > scalarIndent) continue;
    scalarIndent = null;

    const shape = hooksLineProblem(line.slice(indentation.length));
    if (shape === BLOCK_SCALAR) {
      scalarIndent = indentation.length;
    } else if (shape) {
      return { index, error: `"${HOOKS_FIELD}:" block line ${JSON.stringify(line)} ${shape}` };
    }
  }
  if (content === 0) {
    return { index, error: `"${HOOKS_FIELD}:" has no indented block under it; write "${HOOKS_FIELD}:" alone followed by an indented block, or leave the key out` };
  }
  return { index, error: null };
}

const BLOCK_SCALAR = Symbol("block scalar");

/**
 * Check one line of the `hooks:` block, indentation removed: sequence entries,
 * then any number of `key:` prefixes, then an empty value, a comment, a quoted
 * scalar that closes on this line, a block scalar header or a plain scalar.
 * Returns null when the line is one of those, `BLOCK_SCALAR` for a block
 * scalar header, or the reason it is refused.
 */
function hooksLineProblem(text) {
  let rest = text.replace(/^(?:-(?: +|$))*/, "");
  for (;;) {
    if (rest === "" || rest.startsWith("#")) return null;

    let node;
    if (rest.startsWith('"') || rest.startsWith("'")) {
      const closed = rest.startsWith('"') ? /^"(?:[^"\\]|\\.)*"/.exec(rest) : /^'(?:[^']|'')*'/.exec(rest);
      if (!closed) {
        return "opens a quote that does not close on the same line; a multi-line quoted scalar can carry a column-0 line that YAML reads as content and this check reads as a key";
      }
      node = closed[0];
    } else if (/^[|>]/.test(rest)) {
      if (/^[|>][-+1-9]{0,2}(?:[ \t]+#.*)?[ \t]*$/.test(rest)) return BLOCK_SCALAR;
      return "has a block scalar header this check does not read";
    } else if (/^[[{]/.test(rest)) {
      return "uses YAML flow collection syntax; one that spans lines can carry a column-0 line, so write the block in block style";
    } else if (/^[&*!]/.test(rest)) {
      return "uses a YAML anchor, alias or tag; write the value plainly";
    } else if (/^[\]},%@`?:]/.test(rest)) {
      return "starts with a YAML indicator this check does not read";
    } else {
      // A plain scalar runs to a mapping colon or a comment; quotes inside it are content.
      const stop = /:(?=[ \t]|$)|[ \t]#/.exec(rest);
      node = stop ? rest.slice(0, stop.index) : rest;
    }

    rest = rest.slice(node.length);
    const key = /^[ \t]*:(?:[ \t]+|$)/.exec(rest);
    if (key) {
      rest = rest.slice(key[0].length);
      continue;
    }
    if (/^[ \t]*$|^[ \t]+#/.test(rest)) return null;
    return "is not a key, a sequence entry, a scalar or a comment; the hooks block is read as a closed subset of YAML";
  }
}

/** A tier pin: one bare token, optionally quoted, and nothing else. */
export function tierPin(fields, field) {
  const entry = fields.get(field);
  if (!entry || entry.value === "") return null;
  return /^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(entry.value) ? entry.value : null;
}

/**
 * A recorded justification: prose that survives unquoting and trimming.
 *
 * An unquoted `null` or `~` is YAML's way of writing nothing, so it records
 * nothing. Quoted, it is a word someone chose to write, and stays content.
 */
export function recordedProse(fields, field) {
  const entry = fields.get(field);
  if (!entry) return null;
  const value = entry.value.trim();
  if (value === "") return null;
  if (!entry.isQuoted && /^(?:null|Null|NULL|~)$/.test(value)) return null;
  return value;
}

export function verifyAgentTiers(repoRoot = process.cwd(), relativeRoot = join(".claude", "agents")) {
  const errors = [];
  const absoluteRoot = join(repoRoot, relativeRoot);
  if (!existsSync(absoluteRoot)) return { checked: 0, elevated: 0, errors };

  const files = readdirSync(absoluteRoot, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => entry.name)
    .sort();

  let elevated = 0;
  let haiku = 0;
  for (const name of files) {
    const relative = join(relativeRoot, name);
    const text = readFileSync(join(absoluteRoot, name), "utf8");
    const { fields, error } = readAgentFrontmatter(text);

    if (error) {
      errors.push(`${relative} ${error}`);
      continue;
    }

    errors.push(...toolProblems(fields).map((problem) => `${relative} ${problem}`));

    const model = tierPin(fields, "model")?.toLowerCase() ?? null;

    if (!model) {
      errors.push(
        `${relative} must declare an explicit "model:" field in its frontmatter carrying one bare tier token; an unpinned or unparseable pin inherits the caller's model`,
      );
      continue;
    }

    if (RESTRICTED_AGENT_MODEL_TOKENS.some((token) => model.includes(token))) {
      const problems = haikuProblems(repoRoot, fields, model);
      if (problems.length > 0) {
        errors.push(...problems.map((problem) => `${relative} pins "${model}": ${problem}`));
      } else {
        haiku += 1;
      }
      continue;
    }

    const isBase = BASE_AGENT_MODEL_TOKENS.some((token) => model.includes(token));
    const isElevated = ELEVATED_AGENT_MODEL_TOKENS.some((token) => model.includes(token));
    if (!isBase && !isElevated) {
      errors.push(`${relative} pins unrecognized tier "${model}"; use the base tier, or an elevated tier with a recorded rationale`);
      continue;
    }

    if (isElevated) {
      elevated += 1;
      // An elevated pin has to be argued for. Without this the expensive tier
      // becomes the path of least resistance and drifts upward silently.
      if (!recordedProse(fields, ELEVATION_RATIONALE_FIELD)) {
        errors.push(
          `${relative} pins the elevated tier "${model}" without a non-empty "${ELEVATION_RATIONALE_FIELD}:" field; `
          + "an elevated agent must be a deliberate decision, not a default that drifted",
        );
      }
    }
  }

  return { checked: files.length, elevated, haiku, errors };
}

/**
 * A subagent reads and runs; the main loop writes. A grant such as
 * `Edit(src/**)` is still Edit, so the rule spec after the name is ignored.
 */
export function toolProblems(fields) {
  const tools = recordedProse(fields, "tools");
  if (!tools) {
    return ['needs an explicit "tools:" list; without one the agent inherits every tool, edit tools included'];
  }
  const names = tools.split(",").map((tool) => tool.replace(/\(.*$/, "").trim().toLowerCase());
  if (names.some((tool) => tool === "*" || EDIT_TOOLS.includes(tool))) {
    return ["grants edit tools (Edit, Write, MultiEdit, NotebookEdit or *); subagents read and run, and the main loop writes"];
  }
  return [];
}

/** Every unmet Haiku condition, so one run names them all. */
export function haikuProblems(repoRoot, fields, model) {
  const problems = [];
  const pin = HAIKU_PIN.exec(model);
  const [minMajor, minMinor] = HAIKU_MINIMUM_VERSION;
  if (!pin || Number(pin[1]) < minMajor || (Number(pin[1]) === minMajor && Number(pin[2]) < minMinor)) {
    problems.push("Haiku must be an exact pin of claude-haiku-5-5 or later, never the bare alias or an older version");
  }

  const share = recordedProse(fields, HAIKU_MECHANICAL_FIELD);
  if (!share || !/^\d{1,3}$/.test(share) || Number(share) < HAIKU_MINIMUM_MECHANICAL_SHARE || Number(share) > 100) {
    problems.push(
      `Haiku needs "${HAIKU_MECHANICAL_FIELD}:" as a whole percentage from ${HAIKU_MINIMUM_MECHANICAL_SHARE} to 100; `
      + "Haiku is only for near-mechanical work",
    );
  }

  const replay = recordedProse(fields, HAIKU_REPLAY_FIELD);
  const replayPath = replay ? normalize(replay) : null;
  const inside = replayPath && !isAbsolute(replayPath) && replayPath !== ".." && !replayPath.startsWith(`..${sep}`);
  if (!inside || !existsSync(join(repoRoot, replayPath)) || !statSync(join(repoRoot, replayPath)).isFile()) {
    problems.push(
      `Haiku needs "${HAIKU_REPLAY_FIELD}:" naming a file in this repository that records a known-answer replay `
      + "showing no loss against the base tier",
    );
  }

  const purpose = `${recordedProse(fields, "name") ?? ""} ${recordedProse(fields, "description") ?? ""}`;
  const judgment = HAIKU_JUDGMENT_TERMS.exec(purpose);
  if (judgment) {
    problems.push(
      `Haiku never does judgment work, and this agent's name or description says "${judgment[0]}"; `
      + "review, audit, research, security, debugging, diagnosis, planning and design stay on Sonnet or above",
    );
  }
  return problems;
}

if (process.argv[1]?.endsWith("verify-agent-tiers.mjs")) {
  const result = verifyAgentTiers();
  if (result.errors.length > 0) {
    process.stderr.write(`Agent tier invariant failed:\n${result.errors.map((line) => `  - ${line}`).join("\n")}\n`);
    process.exit(1);
  }
  process.stdout.write(
    `Agent tiers valid: ${result.checked} definition(s) checked, ${result.elevated} elevated with a recorded rationale, `
    + `${result.haiku} on Haiku under the mechanical-work allowance.\n`,
  );
}
