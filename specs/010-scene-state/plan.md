# Plan: Scene state written by code (spec 010)

**Spec**: [spec.md](spec.md). **Tasks**: [tasks.md](tasks.md).

## Design

- **Data, not code.** T-12-18 lives in `pacing.yaml#details.scene_writes`: `beats` (verb → degree band → rows
  with `reach_min` / `down`, values for `actor` / `target` with `{actor}` / `{target}` names) and `responses`
  (`talk`, `refusal`, `want`, generic `rows`, `by_practice` rows that replace the generic row whole).
- **`engine/dm/scene_state.py`** (new, ~120 lines): `beat_writes` (after resolution, in `world_step` before
  the NPC layer), `response_values` + `write` (called from `npc_layer.respond` per response), `lines` (the
  record's scene-state lines). Every write is `write_detail(..., source="ruling", because=<frame/beat or response
  source>)`.
- **Record shape.** `ActivityEntry` gains `slot` (activity | posture | held | manner | position); the existing
  `activity` record item kind, handle and claim paths carry every slot, so no new item kind.
- **NPC layer.** The rolled activity is written as the `activity` detail (it expires with the other scene slots);
  `ensure_activities` rebuilds `record.activities` from the store for whoever is present now, so a scene cut
  mid-turn drops the old scene's people.
- **Bands.** `PositionSet.band_drop` (new optional field); `details.expire_events` also clears every band at scene
  end (12.4.8 step 8).
- **Judge.** Scene-slot writes back no change by themselves (`_SCENE_STATE_KEYS`): the cited line is the source.
  Freshness ("details stated lately") skips scene slots: they are owed state, not imagery.
- **Fix found on the way.** `write_detail` on a slot whose value expired to `None` now supersedes the cleared fact.

## Not done

- A disarm clearing `held` (no disarm outcome in M1; DL-12-77 "Revisit if").
- Momentary (`beat`-persistence) postures: off balance and the like are ch.07 conditions or the beat line's.
- Bands for NPC-to-NPC positions are cleared but never shown (only the band to the PC is a line).
