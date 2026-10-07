# Data Model: Playable Prototype

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

The rules already define the canonical shapes: state types (00.6.1), object shapes (00.6.2), visibility
(00.6.4), sealing (00.6.5), the evidence event (00.6.8), the timestamp (00.7.1), the clock (00.8), the
condition (00.9), the frame (00.13), the rule card (00.15.2) and the ruling record (00.15.5). This
document does not restate them. It says how they are stored, which ones Milestone 1 uses, and the
records the engine adds (events, world seed, scene, turn record, model call).

## 1. Storage: one SQLite file per campaign

| Table | Purpose | Key columns |
|---|---|---|
| `events` | **Source of truth.** Append-only; never updated or deleted | `seq` (PK, monotone), `branch_id`, `turn_id`, `beat_id` null, `game_time` (00.7.1 timestamp as JSON), `type`, `payload` (JSON), `source` (frame id, handler id, oracle id, mention, player), `rule_id` (the rule that caused it), `schema_ver` |
| `rng_draws` | Every draw (FR-015) | `seq`, `stream`, `purpose`, `sides` or `table_id`, `result`, `event_seq` |
| `turns` | One row per player message (FR-024) | `turn_id`, `input_verbatim`, `parts` (JSON), `delivered_verbatim`, `pause` (JSON) null, `verdicts` (JSON), `fallback_used`, `cost_usd`, `latency_ms` |
| `model_calls` | Every model call, input and output, for replay | `call_id`, `turn_id`, `role`, `provider`, `model_id`, `schema_hash`, `request` (JSON), `response` (JSON), `tokens_in_cached`, `tokens_in`, `tokens_out`, `tokens_thinking`, `cost_usd`, `latency_ms`, `outcome` (ok, invalid_reasked, defaulted, refused, error) |
| `snapshots` | Projection checkpoints at each `scene_end` and on save | `seq`, `blob` (JSON), `hash` |
| `facts_idx` | Query index over fact events | `subject`, `predicate`, `value`, `valid_from_seq`, `valid_to_seq`, `source`, `certainty`, `visibility` |
| `rulings_idx` | Precedent lookup by signature (00.15.6) | `signature`, `ruling_id`, `event_seq` |
| `branches` | Save branches and rewinds | `branch_id`, `parent_id`, `fork_seq` |

The current state is a **projection**: replaying `events` in order through pure reducer functions yields
the `WorldState` object below. Index tables are rebuilt from events and can be dropped at any time.

## 2. Event types (Milestone 1)

Each 00.14.2 write tool produces one or more events. Names follow the tool.

| Event | From | Payload (beyond the common columns) |
|---|---|---|
| `entity_created` | `create_entity`, write-on-mention | entity record (00.6.2), visibility, sealed fields |
| `fact_set` | `set_fact`, Oracle answers | subject, predicate, value, certainty, visibility, supersedes |
| `quantity_changed` | `update_quantity`, cost application | entity, quantity, delta, new value, clamped, reason, frame id |
| `relationship_set` | `set_relationship` | a, b, kind, value or steps, reason |
| `position_set` | `set_position` | entity, location, flags ± |
| `knowledge_recorded` | `record_knowledge` | knower, fact id, how |
| `clock_created` / `clock_ticked` | clocks | clock fields / source ref, amount, stage, omen key, completed |
| `condition_applied` / `condition_removed` | conditions | instance (00.9) |
| `sealed` / `unsealed` | `seal` / `unseal` | item ref, gate / via |
| `frame_committed` | `frame_check` passed and the OFFER answered | the frame up to OFFER (immutable afterwards) |
| `frame_resolved` | roll → read → consequence | roll, degree, near miss, delivered reach, costs applied |
| `offer_logged` | OFFER shown or auto-committed | shown_at, choice (commit, change, withdraw, trade, auto) |
| `evidence_recorded` | `record_evidence` (00.6.8) | the evidence event; tallies are settled from Milestone 3 |
| `ruling_logged` | `log_ruling` | the ruling record (00.15.5) |
| `oracle_answered` | `oracle` | question, odds rung, d100, answer, extreme, twist, fact id |
| `table_rolled` | `roll_table` | table id, context, entry, recency |
| `time_advanced` | `advance_time` | from, to, boundaries crossed, interrupt, remainder |
| `boundary_marked` | `mark_boundary` and each crossed boundary | boundary, payload (rest payload where relevant) |
| `handler_ran` / `handler_skipped` | scheduler | handler id, phase, result summary / reason "not yet built" and the milestone that builds it |
| `writes_reverted` | `revert_writes` | reverted event seqs, compensating values, reason |
| `scene_started` / `scene_ended` | PR-12-7 | scene record / cut reason |
| `meta_set` | counters and preferences | key (tension, inconclusive streak, dead air, auto_commit…), value |

## 3. Projection: `WorldState` (state families in Milestone 1)

| Family (00.6.1) | Milestone 1 contents | Notes |
|---|---|---|
| entity | PC, 1–3 NPCs, the place, notable items, entities created on mention | NPCs carry name, pronouns and descriptors from creation (PR-12-5), so identity claims are checkable |
| quantity | PC Vitality, coin, a consumable or two | clamps from `data/` |
| flag / fact | scene facts, Oracle answers, mention writes | bi-temporal via `valid_from`/`valid_to` event seqs |
| relationship | NPC→PC standing | rung scale from `data/` |
| position | place-level location; no range bands (no conflict) | |
| knowledge | what the PC and each NPC know, and how | drives `knowledge` claims |
| clock | one visible scene clock | omens from the clock template |
| condition | only what cost forms apply | stacking per 00.9.2 |
| license | the PC's held licences | the GATE enum is built from these |
| commitment | method consequences that create promises | |
| ledger | rulings, oracle log, offer log, evidence | stored as events |
| time | the 00.7.1 timestamp plus beat counter; current mode | |
| frame | in-flight frames for the current turn | persisted on commit and resolution |
| meta | tension, inconclusive streak, dead-air count, table recency, preferences, Oracle calls this scene (I-038 cap) | |

Filled in later milestones: tally (M3), effect_instance (M2/M3), offer (04/11 offers, M3/M6). Their reducers exist only as stubs that raise if an event of that type appears.

**Views** (`get_state`, 00.14.2 #8): `narrator` (sealed fields replaced by permitted slices, INV-10),
`codex` (shown and available only), `audit` (everything). The packet builders read only the narrator view.

## 4. Records the engine adds

### Scene (PR-12-7 scene record)

`scene_id`, `place_id`, `mode` (00.7.3), `agenda`, `hoped_answer`, `pillar`, `challenge_type`,
`cast_present` [entity ids], `situation_tags` [tag], `question_answered` (bool), `started_at`, `ended_at`.

### Turn record (FR-024)

```yaml
TurnRecord:
  turn_id: str
  input_verbatim: str
  parts: [{text: str, class: SAFETY|SESSION|DISPUTE|PENDING_ANSWER|OOF_QUESTION|FICTION_QUESTION|DECLARATION|SPEECH}]
  beats: [frame_id]
  oracle_calls: [event_seq]
  pause: {kind: offer|clarify|redirect|near_miss, frame_id: str|null, options: [str]} | null
  writes: [event_seq]
  draft_versions: [{text: str, mentions: [..], claims: [Claim], verdicts: [Verdict]}]
  fallback_used: bool
  screen: {intent_acknowledged: bool, next_step: bool, safety_ok: bool, pc_agency_ok: bool,
           no_mechanics_in_fiction: bool, ends_correctly: bool}
  delivered_verbatim: str
  model_calls: [call_id]
  cost_usd: float
  latency_ms: int
```

### Claim and verdict (12.3.1–12.3.2)

```yaml
Claim:
  sentence: int
  subject: entity_id | "unknown"        # constrained to the scene's ids plus "unknown"
  class: existence|identity|quantity|harm_condition|position|possession|location_time|
         knowledge|capability|clock|attitude|outcome|action|sealed
  predicate: str
  value: str
  asserts_change: bool                  # "changed" vs "is"
  pc_words_or_feelings: bool            # gives the PC unstated words, choices or feelings
Verdict:
  claim: int
  verdict: supported|new_element|undetermined|contradicted|unsourced_change|overreach|leak|pc_agency
  store_value: str|null                 # for contradicted / overreach
  fix: write_on_mention|oracle|redraft_to_store|cut|replace_with_slice
```

`subject: unknown` never creates an entity; it becomes "cut the claim" (research.md: coreference risk).

### Model call (one per role invocation)

See `model_calls` above. `schema_hash` identifies the exact per-turn schema, so a replay can verify that
the same schema was built.

## 5. Validation rules

- Every event type has a Pydantic payload model; an event that fails validation is never appended.
- Every id in a payload must exist in the projection or be created by an earlier event in the same turn
  (RC-DATA: ids and enums from `data/` are validated at load).
- Numbers in events come only from engine computations or `data/`; model output schemas contain no
  numeric fields except the player's own stated quantities (INV-3).
- `frame_committed` is immutable; later frame events may only fill READ, DELIVER, CONSEQUENCE and RECORD
  fields (00.13.2).
- Writes and reverts are scoped: `writes_reverted` may only target events from the current scene (DL-12-04).

## 6. State transitions

**Frame:** `parsed → gated → (necessity: no roll → recorded) | anchored → framed → offered →
{withdrawn | changed → parsed | committed → rolled → read (→ near_miss_pause → read) → consequenced →
recorded}`. A G3/G4 gate goes `gated → redirected` (pause) or `gated → refused` (no pause).

**Turn:** `received → classified → adjudicating → (paused) → world → written → drafting → checking
(→ redrafting ×≤2 → fallback) → screened → delivered → recorded`. A pause delivers what is resolved so far
and resumes at `adjudicating` on the next PENDING_ANSWER.

**Scene:** `framed → active → (question answered or cut) → ended` (`scene_end` handlers run) `→ next scene
framed in the next response`.
