# Data Model: Action Resolution Probe

Derived from spec.md's Key Entities. All fields are placeholders per spec.md's Assumptions —
none of this is meant to survive into the real ruleset's data model unchanged.

## CharacterState

Held in the session's JSON file; the single source of truth the model must query/update via
tools rather than track in its own context.

| Field | Type | Notes |
|---|---|---|
| `name` | string | Placeholder character name. |
| `resource_name` | string | Name of the one tracked resource (e.g. "Vitality"). Not meant to be a final resource name for the real ruleset. |
| `resource_current` | integer | Current value. |
| `resource_max` | integer | Maximum value, set at session start. |

**Validation**: `0 <= resource_current <= resource_max`. No other fields exist for this feature
— no attributes, no inventory, no position.

## ActionAttempt

One per player action, whether or not it required resolution. This is the row that makes
SC-002/SC-003 checkable.

| Field | Type | Notes |
|---|---|---|
| `turn_number` | integer | Sequential within the session. |
| `action_description` | string | The player's freeform input, verbatim. |
| `requires_resolution` | boolean | Per FR-002. |
| `dc` | integer or null | Null when `requires_resolution` is false. |
| `roll` | integer or null | Raw d20 result; null when not resolved. |
| `modifier` | integer or null | Flat modifier applied this attempt. |
| `total` | integer or null | `roll + modifier`; null when not resolved. |
| `degree` | enum or null | One of `critical_success`, `success`, `failure`, `critical_failure`, or null. |
| `narration` | string | The DM's prose for this turn. |
| `state_before` | object | A snapshot of CharacterState immediately before this turn's tool calls. |
| `state_after` | object | A snapshot of CharacterState immediately after. |
| `timestamp` | string (ISO 8601) | For ordering/audit. |

**Validation**: `degree` must be non-null iff `requires_resolution` is true. `state_after` must
equal `state_before` unless the narration or degree logically implies a change (checked by the
scripted harness, not enforced at write time — enforcing it at write time would require the
harness to understand narrative intent, which is exactly the open problem this feature studies).

## SessionLog

The full JSON file for one session.

| Field | Type | Notes |
|---|---|---|
| `character` | CharacterState | The character's state at session end (current values). |
| `started_at` | string (ISO 8601) | |
| `turns` | array of ActionAttempt | Ordered by `turn_number`. |

**State transitions**: None beyond what's described above — this feature has no state machine,
just a linear log and a two-field resource that moves up or down.
