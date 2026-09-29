# Tool Contracts: Ability Acquisition Probe

Extends Feature 001's [contracts/tools.md](../../001-action-resolution-probe/contracts/tools.md)
and Feature 002's `update_resource`/`set_fact` additions — same boundary, one more tool. The
model decides *when* to call `grant_ability` and supplies which source archetype and
acquisition method a narrated event implies; it never supplies, and never narrates into
existence, *which effect template* results — that's computed entirely by
`ability_pool.resolve_ability_grant`.

## `grant_ability`

Called when, and only when, a turn's narration describes defeating, surviving, or otherwise
acquiring something from one of this probe's fixed source archetypes (FR-003). Not called
otherwise — same discipline as `update_state`: an action that doesn't imply an acquisition
simply doesn't call this tool, and the auditor's new `ability_grant` check (contract below)
is what catches a narrated grant with no corresponding call.

**Input**:
```json
{
  "source_archetype": "beast",
  "acquisition_method": "narrow_survival",
  "reason": "barely survived the dire wolf's ambush, using its own momentum against it"
}
```

`source_archetype` MUST be one of the probe's fixed `SourceArchetype.name` values;
`acquisition_method` MUST be one of the fixed `AcquisitionMethod.name` values. The model
supplies both by mapping what it just narrated onto these fixed categories — this is the one
genuinely judgment-driven step in this feature (per Principle III's base-model-judgment
default, not a new judge-gate) — but the categories themselves are closed, so this is a
classification onto a known set, not open invention.

**Output** (computed entirely in `ability_pool.resolve_ability_grant`; the model never sees or
supplies which specific template results):
```json
{
  "template_id": "beast_thick_hide",
  "name": "Thick Hide",
  "description": "Your skin toughens where the beast's claws couldn't find purchase — reduce incoming damage from a single hit per encounter, but only against attacks you can see coming.",
  "flavor_bias": "defensive"
}
```

If `source_archetype` is not one of the fixed set, the tool call fails validation the same way
an out-of-range `roll_check` argument would — the harness records this as a scenario-generation
or DM error, not a silent fallback to an invented archetype (per spec.md's first Edge Case).

## `check_turn` (extended)

Feature 002's `auditor.check_turn` gains one new optional parameter.

**Input** (in addition to Feature 002's existing parameters): `ability_grant: AbilityGrant |
None` — the `AbilityGrant` record produced by this turn's `grant_ability` call, if any; `None`
if the turn didn't grant anything.

**Contract**: when `ability_grant` is not `None`, `check_turn` additionally checks whether the
turn's narration is consistent with the granted `EffectTemplate`'s `name` and `description`
(including any stated limitation) — a mismatch is reported the same way any other conflict is,
with `conflict_type: "fact"` and the new `state_category: "abilities"` value (per
data-model.md). This reuses the same narration-versus-structured-state comparison `check_turn`
already does for ordinary state changes; it is not a separate mechanism.

## What is deliberately NOT a tool

There is no tool for deciding *whether* a narrated event counts as an acquisition at all —
that stays the model's own judgment, same as Feature 001's resolution-need decision. Only the
part that must be deterministic (which effect template results, given the model's own
classification) is a tool call.
