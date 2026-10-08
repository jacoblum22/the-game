# Data model: Adjudication

Changes only. Every new field is optional with a default, so stored pauses and frames from older saves load.

## Reader output (schema `reader_schema`, 12.2.2 / DL-12-50)
- `parts[]`: `text`, `class`, **`question_kind`** (`none`, `who_is`, `where_is`, `what_happened`, `what_like`,
  `what_want`, `who_knows`), **`topic`** (string or null).
- `beats[]`: `intent`, `method`, `assertion`, **`shape`** (`now` | `queued` | `conditional`), `target`, `verb`,
  **`against_will`**, **`uses_power`**, **`speech`** (booleans), `g4_fact`, `intent_verbs`.
- Removed: `gate`, `license`, `would_be_license`, `necessity`.

## `Beat` (engine/resolve/types.py)
- Added: `against_will`, `uses_power`, `speech` (bool, default False), `asks` (bool: a Talk beat asking a plain
  question).
- Removed: `gate`, `would_be_license`, `g4_test`. `license` stays for engine-set paths (stretch/emulate, fallback).
- `necessity` is now written by `engine.resolve.necessity`, never by a role.

## Framer output (`framer_schema`)
- `obstacle`: `{kind: "tier", obstacle_class, tier}` | `{kind: "opposed", entity}` | `{kind: "entity_defense",
  entity}`; then `nudge_why`, `nudge` ("-1"/"0"/"+1"), `nudge_fact`, and `request_size` (R1–R5, social only).

## `Obstacle` / `Frame`
- `Obstacle`: **`obstacle_class`**, **`nudge`** (int), **`nudge_fact`**, **`nudge_why`**, **`request_size`**.
- `Frame`: **`obstacle_class`**, **`nudge`**, **`long_shot`** (bool), **`alternatives`**
  (`[{label, attribute, verb, chance}]`), **`guard`** (a note when the guard converted a snag).
- `OfferPreview`: **`long_shot`**.

## Validation (frame_check, PR-01-2)
- Step 6: class known for the verb; `other` needs a rolling tier; nudge needs a usable fact and a why, never with
  `other`, never across the trivial line, never the same fact as a snag; a social/opposed beat must be opposed.
- Step 7: at most one Precision snag (the rest Protective).
- Step 10: costs narrowed by `resolution.yaml#stakes_cost_menus`; harm under the observer source needs a cited
  source fact.
- Step 12: the guard (01.6.13).
