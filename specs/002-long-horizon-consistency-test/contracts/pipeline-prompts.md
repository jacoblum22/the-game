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

## 3. State-at-cutoff extraction (`scenario_pipeline.extract_state_at_cutoff`)

**Input**: the campaign outline, the trajectory, and the commitment set from steps 1-2, plus a
`cutoff_index` (default `-1`, meaning "before any node" — the original t=0 case).

**Output**: a `WorldState` (per data-model.md), representing the state immediately *after* the
node at `cutoff_index` has triggered and *before* any later node has (or, at the default, the
state at `sequence_index: 0`, before any node has triggered at all).

**Amendment (fast-forward seeding)**: this was originally `extract_initial_facts`, hardcoded to
the t=0 case. Generalized to an arbitrary `cutoff_index` so a session can be seeded partway
through its trajectory instead of always at the very start — see the new §7 below.
`extract_initial_facts(outline, trajectory, commitments)` still exists as a thin wrapper calling
this with `cutoff_index=-1`, so its existing contract (and every other caller) is unchanged.

**Validated by**: `test_scenario_schema.py` checks every `resources`/`possessions`/
`status_flags` key referenced anywhere in the trajectory or commitment set exists in the
returned `WorldState` (or is a documented "not yet true" placeholder). The **isolation check**
(step 4, below) is the real content check here, not schema validation.

## 4. Isolation check (`scenario_pipeline.check_isolation`)

**Input**: the trajectory, the generated `WorldState` from step 3, and the same `cutoff_index`
(default `-1`) — generalized the same way as step 3, checking for leakage from nodes with
`sequence_index > cutoff_index` instead of always `>= 1`.

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
regeneration, not a warning to note and proceed past. Unchanged by the cutoff generalization.

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

## 7. Fast-forward seeding (`scenario_pipeline.generate_fast_forward_scenario`)

**Added after T021**: this feature's own initial research brief proposed synthetically
generating prior context plus a pre-populated state, specifically to avoid paying for 80+ real
sequential turns just to reach a "long session" state. What actually got built for T021 instead
played every turn live from `sequence_index 0`, at up to ~3 API calls per turn — research.md's
Decision log records why a *freehand* recap was set aside (no isolation discipline, easy to leak
future knowledge into the seed), but that objection was about the lack of discipline, not the
fast-forward idea itself. This capability restores the original idea, built on the SAME
isolation-checked pipeline as steps 1-4 above, just at a configurable cutoff instead of always 0.

**Revised once more before any real batch used it**: the first version of this generated a
short (3-6 sentence) prose recap, injected into the DM's system prompt. That was rejected during
review as too thin — a short summary doesn't replicate what "long-horizon" is actually about:
does a genuinely *large volume* of accumulated turn content in the model's context cause
degradation, not just "can it follow an accurate briefing." Replaced with a full synthetic
multi-turn transcript, spliced directly into the real conversation history as literal prior
turns, so the model contends with actual bulk context, not a compressed stand-in for it.

**`generate_synthetic_transcript(outline, trajectory, commitments, cutoff_index, target_turn_count=30, chunk_size=10)`**

**Input**: the campaign outline, the trajectory nodes with `sequence_index <= cutoff_index`
only (nodes after the cutoff are never shown to this call, so there is nothing later for it to
leak), and a target turn count.

**Output**: a `list[tuple[str, str]]` of `(player_action, dm_narration)` pairs — granular enough
to total roughly `target_turn_count` turns, not one turn per plot beat; real sessions have many
ordinary investigative/conversational turns between beats too. Generated in `chunk_size`-turn
batches (passing the transcript-so-far forward each time) rather than one shot, since asking for
30 turns of coherent content in a single completion risks truncation or degrading quality toward
the end.

**`check_transcript(trajectory, commitments, transcript, world_state_at_cutoff, cutoff_index)`**

**Input**: the trajectory, the active commitments, the generated transcript, and the
independently-generated `world_state_at_cutoff` (from `extract_state_at_cutoff` — a *separate*
call, so nothing guarantees the two already agree with each other).

**Output**:
```json
{
  "valid": true,
  "issues": []
}
```
or, on failure, `issues` lists each problem found. Checks four things in one pass: (1) isolation
— nothing implies knowledge of a node past the cutoff; (2) internal inconsistency — the
transcript doesn't contradict itself turn to turn; (3) state disagreement — the independently-
computed `world_state_at_cutoff` actually agrees with what the transcript narrates (e.g. an item
the state marks as possessed must actually be shown being acquired somewhere in the transcript,
not just asserted with no corresponding event); (4) commitment violation — does any line satisfy
a commitment's `violation_condition`. `generate_fast_forward_scenario` treats `valid: false` as a
hard failure requiring both the state and the transcript to be regenerated together, same
discipline as `check_isolation`'s `isolated: false`.

**`generate_fast_forward_scenario(outline, cutoff_fraction, target_turn_count=30, max_isolation_retries=2)`**

**Input**: the campaign outline and a `cutoff_fraction` in `[0.0, 1.0)` — a fraction of the
trajectory's length, not a raw node index. The trajectory only exists (and only has a known
length) after `extract_trajectory` runs inside this call; resolving the fraction to a concrete
`cutoff_index` beforehand would mean generating the trajectory twice, wasting a call and —
since generation is stochastic — silently using a different trajectory than the one actually
returned. This function generates the trajectory exactly once and resolves the cutoff from it.

**Output**: `(trajectory, commitments, world_state_at_cutoff, transcript, cutoff_index)`.
`trajectory` and `commitments` are the full-story versions, unchanged from `generate_scenario` —
the DM's own "prep notes" still cover the whole planned story either way; only the seeded state
and the transcript are cutoff-specific. `cutoff_index` is returned so callers can report exactly
where the fast-forward landed.

**Contract**: same hard-failure-on-leak discipline as `generate_scenario` — a `check_transcript`
failure at the cutoff raises `IsolationViolationError` after `max_isolation_retries` regeneration
attempts (of both the state and the transcript together, since they must agree), never silently
proceeds with an invalid seed.

**Runtime wiring**: `tests/probe/run_long_horizon_test.py --fast-forward FRACTION
[--fast-forward-turns N]` uses this instead of `generate_scenario` for every scenario in the
batch. `run_session`'s new optional `transcript` parameter (default `None`, so
non-fast-forwarded callers are unaffected) splices the transcript directly into `conversation`
as real alternating `Content(role="user"/"model", ...)` entries before any live turn runs, and
frames the opening turn as *resuming* the session rather than starting it. A pre-existing,
unrelated bug was also fixed while wiring this: `world_state` was previously passed by reference
to both persona runs of a scenario, so the second persona's session silently inherited whatever
mutations the first persona's session left behind instead of starting from the actual seeded
state. Each persona now gets its own `WorldState.from_dict(world_state.to_dict())` copy.
