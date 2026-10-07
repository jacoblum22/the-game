# Data Model: Ability Acquisition Probe

Extends Feature 002's `world_state.py` rather than replacing it. `SourceArchetype`,
`AcquisitionMethod`, and `EffectTemplate` are plain Python constants (see research.md's first
decision), not runtime-constructed dataclasses generated per scenario the way Feature 002's
`TrajectoryNode`/`Commitment` are — so they're documented here as fixed data shapes, not as
extraction-pipeline outputs.

## SourceArchetype (fixed constant)

One of the probe's 3-4 categories a defeated/encountered source can belong to.

| Field | Type | Notes |
|---|---|---|
| `name` | string | Unique, e.g. `"beast"`, `"elemental_fire"`, `"undead"`, `"construct"`. |
| `pool` | list[EffectTemplate] | This archetype's own bounded set (target: ~3) — never shared with another archetype. |

## AcquisitionMethod (fixed constant)

One of the probe's 3 categories describing how a source was defeated or acquired.

| Field | Type | Notes |
|---|---|---|
| `name` | string | One of `"decisive_kill"`, `"narrow_survival"`, `"non_lethal_subdual"`. |
| `fill_mechanism` | enum | `"guaranteed"` (decisive_kill) or `"weighted"` (the other two, each with its own weighting bias per research.md). |

## EffectTemplate (fixed constant)

One concrete, nameable grantable effect.

| Field | Type | Notes |
|---|---|---|
| `template_id` | string | Unique within its archetype's pool. |
| `source_archetype` | string | The one `SourceArchetype.name` this belongs to — an `EffectTemplate` never appears in more than one archetype's pool. |
| `name` | string | Player-facing name. |
| `description` | string | What it does, including any explicit limitation (per Pattern P12's design vocabulary). |
| `is_signature` | boolean | True for exactly one template per archetype — the one `decisive_kill`'s guaranteed pick always returns. |
| `flavor_bias` | enum | `"defensive"`, `"utility"`, or `"offensive"` — used by the weighted acquisition methods' bias, per research.md. |

**Validation**: within one archetype's pool, exactly one template has `is_signature: true`; no
`template_id` collides across archetypes.

## AbilityGrant

One granted `EffectTemplate`, recorded on `WorldState`.

| Field | Type | Notes |
|---|---|---|
| `turn_number` | integer | When the grant happened. |
| `source_archetype` | string | The `SourceArchetype.name` supplied by the `grant_ability` tool call. |
| `acquisition_method` | string | The `AcquisitionMethod.name` supplied by the same call. |
| `template_id` | string | The specific `EffectTemplate` `resolve_ability_grant` returned. |
| `reason` | string | Short justification, same convention as Feature 001/002's other tool calls. |

## WorldState (extended)

One new additive field, alongside Feature 002's existing `resources`/`possessions`/
`position`/`status_flags`:

| Field | Type | Notes |
|---|---|---|
| `ability_grants` | list[AbilityGrant] | New. Append-only; this probe never removes a grant. Empty list is the default for a freshly-seeded `WorldState`. |

**Validation**: unchanged rules apply to the existing fields; no new cross-reference validation
is needed for `ability_grants` since its contents are produced entirely by the deterministic
`resolve_ability_grant` function, never by a generation pipeline that could drift or leak.

## ConflictRecord (extended)

| Field | Type | Notes |
|---|---|---|
| `state_category` | enum | Gains one new value: `"abilities"`, alongside Feature 002's existing `character_resource`/`resources`/`possessions`/`position`/`status_flags`. Used when `check_turn`'s new `ability_grant` check finds the narration contradicting the actual granted `EffectTemplate`. |

**State transitions**: none new — `AbilityGrant` records are immutable once appended, matching
`ConflictRecord`'s own already-established append-only convention from Feature 002.
