# Data model: memory infrastructure (009 part A)

## Fact (00.6.2) changes
- `certainty`: `established | rumored | believed | narrated`.
- `persistence`: `lasting | scene | beat | None` (details only). Carried on `FactSet` and `FactRecord`.

## Details index (`WorldState.details`)
`{entity_id: {slot: DetailRef}}`, `DetailRef = {fact_id, last_used: int}`.
- Updated by `fact_set` on a `detail.<slot>` predicate: a non-None value sets the entry (`last_used` = the turn
  number of the writing event, else 0); `None` removes it.
- `details_used {fact_ids}` sets `last_used` for each listed current detail.
- Slots are validated by the writer against `pacing.yaml#details.slots` (reducers read no rules data).

## Scene card (`WorldState.scene_cards[scene_id]`)
```
{scene, place, agenda, answer, started_at, ended_at, started_seq,
 cast: [id], beats: [{frame, actor, verb, target, degree}], facts: [fact_id], memories: [fact_id],
 threads: [thread_id]}
```
- Opened at `scene_started` (place, agenda, cast, start), filled per event while the scene is open: `frame_committed`
  (beat), `frame_resolved` (degree), `fact_set` (facts / memories / threads by subject; trigger flags, expiry
  writes and chronicle lines excluded), `clock_ticked` on a thread-owned clock (threads), `position_set` (cast),
  `meta_set scene_agenda` (answer). Closed at `scene_ended` (`ended_at`, final cast).
- A reopened scene keeps its card and continues it.

## Detail write outcome
`DetailWrite{outcome: new | same | superseded | contradiction | refused, events, fact_id, prior, reason}`.

## Spotlight
`list[str]` of at most `packet.spotlight_k` entity ids, never in scope, never sealed without a slice.
