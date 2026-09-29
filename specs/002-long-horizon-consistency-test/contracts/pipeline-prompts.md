# Pipeline Call Contracts: Long-Horizon Consistency Stress Test

Feature 001's `contracts/tools.md` documented the boundary between narration and deterministic
mechanics. This feature has a different kind of boundary worth being equally precise about: the
line between each generation call's output and the structural validation that checks it before
it's trusted. Each call below is a plain `generate_content` request (no function-calling tools
involved) — the "contract" is the expected JSON output shape and what validates it.

**Amendment discovered during implementation (T013)**: FR-003 said Feature 001's
`roll_check`/`get_state`/`update_state` would be reused "without modification to those tools'
contracts." That held exactly for `roll_check` and `update_state` — `src/tools.py` is untouched,
and `world_state.WorldStateToolHandlers` reproduces their behavior byte-for-byte. But
`WorldState`'s extra categories (named resources beyond the character's one, possessions,
position, status flags) have no way to be *written* under the original three tools, since
Feature 001 never needed to write anything but one resource. Rather than overload
`update_state`'s signature to do something it wasn't designed for, two tools were added
additively in `src/world_state.py`: `update_resource(name, delta, reason)` (for the `resources`
dict) and `set_fact(category, key, value, reason)` (for possessions/status_flags/position). The
original three tools' contracts are unmodified; two new ones exist alongside them.

## 1. Trajectory extraction (`scenario_pipeline.extract_trajectory`)

**Input**: a short, original campaign outline (plain text).

**Output** (JSON array of `TrajectoryNode`, per data-model.md):
```json
[
  {
    "node_id": "n1",
    "trigger_event": "The caravan is ambushed at the ford.",
    "key_delta": "Three guards are captured; the cargo wagon is disabled.",
    "pov_note": "The player-character witnesses this directly.",
    "sequence_index": 0
  }
]
```

**Validated by**: `test_scenario_schema.py` checks `node_id` uniqueness and that
`sequence_index` values form a valid, gapless ordering. Content quality (is this a sensible
trajectory) is not validated here — that's the pipeline's own responsibility, checked only
indirectly by whether later stages can be built on it without contradiction.

## 2. Commitment extraction (`scenario_pipeline.extract_commitments`)

**Input**: the campaign outline plus the trajectory from step 1.

**Output** (JSON array of `Commitment`, per data-model.md):
```json
[
  {
    "commitment_id": "c1",
    "type": "invariant",
    "description": "The captured guards remain alive unless the player or an explicit story event kills them.",
    "satisfaction_condition": "At any check, all three guards' status_flags remain 'alive' unless a killing event was narrated.",
    "violation_condition": "A guard's status silently changes to dead/absent with no narrated cause.",
    "anchor_node_id": "n1",
    "status": "pending"
  }
]
```

**Validated by**: `test_scenario_schema.py` checks every `anchor_node_id` references a real
`node_id` from step 1, and that `type` is one of the three allowed values.

## 3. Initial-fact extraction (`scenario_pipeline.extract_initial_facts`)

**Input**: the campaign outline, the trajectory, and the commitment set from steps 1-2.

**Output**: a `WorldState` (per data-model.md), representing the state at `sequence_index: 0`
— i.e. before any trajectory node has triggered.

**Validated by**: `test_scenario_schema.py` checks every `resources`/`possessions`/
`status_flags` key referenced anywhere in the trajectory or commitment set exists in the
returned `WorldState` (or is a documented "not yet true" placeholder). The **isolation check**
(step 4, below) is the real content check here, not schema validation.

## 4. Isolation check (`scenario_pipeline.check_isolation`)

**Input**: the trajectory and the generated `WorldState` from step 3.

**Output**:
```json
{
  "isolated": true,
  "violations": []
}
```
or, on failure:
```json
{
  "isolated": false,
  "violations": [
    {"fact": "the guards are already freed", "leaked_from_node": "n3"}
  ]
}
```

**Contract**: `isolated: false` MUST block the scenario from being used in a real run (spec.md's
Edge Cases) — the calling code in `scenario_pipeline.py` treats this as a hard failure requiring
regeneration, not a warning to note and proceed past.

## 5. Player-persona turn (`player_agent.next_action`)

**Input**: the visible conversation history so far (same shape the DM sees), a `persona_mode`
of `adversarial` or `natural`.

**Output**: a single freeform action string (plain text, not JSON) — this is deliberately the
same shape a real human player's input would be, so it flows into Feature 001's existing
`run_turn` unmodified. Per NCP-Bench's own construction, both persona modes are capped at a
short length (roughly 50 words) and only see visible history, not the seeded `WorldState` or
`Commitment` set directly — the persona plays *as* the character, it does not get to see the
answer key.

## 6. Conflict audit (`auditor.check_turn`)

**Input**: the turn's narration (from `dm_agent.TurnResult`), the `WorldState` snapshot from
**before** this turn's tool calls ran, the `WorldState` **after** them, and the active
`Commitment` set.

**Amendment discovered during T021 verification**: the original contract only passed the
*current* (post-turn) `WorldState`, with no "before" reference. This was a real, confirmed
design flaw, not just a theoretical gap — it produced concrete, verifiable false positives:
narration describing an item being found, with that same turn's own tool call granting it, was
routinely flagged as "the world state shows this was already true," because the auditor had no
way to distinguish "already true before this action" from "became true because of this turn's
own tool call." A resource-delta conflict was also traced to the auditor fabricating an
incorrect "before" value it was never actually shown, rather than a real DM math error. Passing
the real pre-turn snapshot explicitly (`state_before`, an optional parameter defaulting to
`None` for any other caller) and revising the "fact" conflict criterion to explicitly exempt a
before→after change the narration itself explains, removed the guesswork.

**Output** (one `ConflictRecord`, or null if no conflict):
```json
{
  "turn_number": 14,
  "conflict_type": "fact",
  "state_category": "status_flags",
  "description": "Narration states the north door is open; status_flags['door_north_locked'] is still true in the AFTER state, and nothing in the narration or the BEFORE/AFTER diff explains an unlocking event."
}
```

**Contract**: this call extends `dm_agent.judge_consistency`'s pattern (a fresh-context,
bounded LLM call) rather than reusing it unchanged — `judge_consistency` only ever checked
narration against one computed degree; `auditor.check_turn` checks against an entire fact
ledger and commitment set, so its prompt and output shape are necessarily richer. It shares the
same documented limitation: it is not an independent-model-family judge per Pattern P13's
eventual requirement, only a same-family bounded check, same as Feature 001's implementation
already disclosed — and, per the amendment above, confirmed capable of its own false positives
even setting that limitation aside, which is exactly why this feature's numeric results should
be read as "what this specific auditor implementation detected," not a ground-truth measurement.
