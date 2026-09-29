# Tool Contracts: Action Resolution Probe

This is the actual interface boundary the constitution's Principle I and Pattern P13 care
about: the line between what the model narrates freely and what deterministic code computes.
The model can only affect mechanics and state by calling these tools — it cannot narrate a
change into existence.

## `roll_check`

Called when, and only when, an action requires resolution (FR-002, FR-003).

**Input**:
```json
{
  "dc": 15,
  "modifier": 2
}
```

**Output** (computed entirely in `resolution.py`; the model never sees or supplies `roll` or
`degree` — it only supplies `dc` and `modifier`):
```json
{
  "roll": 14,
  "modifier": 2,
  "total": 16,
  "degree": "success"
}
```

`degree` is one of `"critical_success"`, `"success"`, `"failure"`, `"critical_failure"`, per the
thresholds fixed in [research.md](../research.md).

## `get_state`

Called before narrating any turn where current state might matter, so the model queries truth
rather than relying on its own conversational memory of what it said last turn.

**Input**: none.

**Output**:
```json
{
  "name": "Kess",
  "resource_name": "Vitality",
  "resource_current": 12,
  "resource_max": 12
}
```

## `update_state`

Called whenever a turn's outcome implies a change to the tracked resource (FR-005, FR-006).
Not called otherwise — an unchanged turn simply doesn't call this tool, which is itself part of
what the scripted harness checks (a narrated change with no corresponding call is a detected
inconsistency, per SC-002/SC-003).

**Input**:
```json
{
  "delta": -2,
  "reason": "fell from the canopy while escaping"
}
```

**Output**:
```json
{
  "resource_current": 10,
  "resource_max": 12
}
```

`reason` is logged alongside the change (feeds `ActionAttempt` in data-model.md) but has no
mechanical effect — it exists purely so a reviewer can audit *why* a change happened without
re-reading the narration prose, which is the actual point of FR-007/FR-008.

## What is deliberately NOT a tool

There is no `narrate` tool and no tool for "decide whether this needs resolution" — those stay
as the model's own free-form judgment, per Principle III's resolved default (base-model
judgment, no gate) and per FR-002. Only the parts that must be deterministic are tools; making
narration or the resolution-need decision into tool calls would misapply P13, which reserves
tool-calling for "hard mechanics," not for judgment calls this project has explicitly decided
not to gate yet.
