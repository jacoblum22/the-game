# Plan: spec 021 (testimony and answer lines, speaker card, seeded stance)

## Technical context
Python 3.12, Pydantic v2, pytest, ruff, pyright. Testimony: `engine/dm/testimony.py` (+ prompt, schema in
`engine/dm/schemas.py`, offline stub in `engine/llm/offline.py`). Answers: `engine/dm/answer.py`, called from
`engine/dm/world_step.py` and (DM-side "who is") `engine/dm/turn.py::_fiction_questions`. Speaker card and identity
lines: `engine/dm/packet.py`. Framer enum: `engine/dm/schemas.py::schema_context` (`lever_fact_ids`), not
`engine/resolve/`. Reaction roll: `engine/world/social.py::first_interaction`.

## Constitution check
- VIII.1 code must not author narrative truth: no "no one you know" fact, no re-delivered clue, no refusal as a fact,
  no complaint or goal text shown as what an NPC knows. Pass.
- VIII.3 truth only when it matters: settlement only on travel, a premise or a testimony-only target. Pass.
- VIII.5 remove friction before adding procedure: `rests_on` (field, schema, packet block) and `NO_ONE` deleted; the
  new code is a `kind` enum and three filters. Pass.
- VIII.6 better context: pronouns and bond on the speaker card; names, not ids, in the claim view. Pass.
- I (code owns the spine): willingness, case delivery, casting stay code's. Pass.

## Design
1. **Triggers** (`testimony.triggered(state, beats)`): over open records; (a)/(c) a beat target known only from
   testimony and named by a record (unchanged logic); (b) a beat `assertion` with >= 2 content words that covers
   >= 0.6 of a record's words or vice versa. `settle_triggered` passes the Reader's beats. Delete `rests_on` from
   `ReaderOutput`, `reader_schema`, `SchemaContext.said_ids`, and the Reader packet's TESTIMONY block.
2. **Claim call** (`testimony._claim`): view = identity lines for the speaker and everyone named (names, pronouns,
   bond), no `<id>:` lines; the exchange = that turn's player input and delivered text; message = "<name> said: ...".
   Schema adds `kind` (`claim`, `refusal`, `opinion`, `want`, `feeling`, `intention`, `question`) first; subject is a
   name. Code maps a subject name back to an id (`resolve_names`), else `world`. Default (call failed): `none`.
3. **settle()**: `kind != claim` or a speaker-subject predicate of will (`_OWN_WILL`) -> nothing written, record
   `settled: "none"`. Else route as before; write `predicate = slug(predicate)`; record keeps `fact`.
   `testimony.said_for(state, fid)` returns the record; `oof.fact_short` renders "<Speaker> said: <claim>" (one branch).
4. **Answers** (`answer.py`): `cast_who` returns None on no match and writes nothing; `_who` falls to the ordinary
   route; `who_answer` returns ("", "") and `turn._fiction_questions` writes nothing for it. `_from_case` returns None
   for a found node unless the PC is the knower (recall). `_SELF` matches only "you" / "your name". `NO_ONE` deleted.
5. **Speaker card** (`packet.speaker_card`): header adds `identity_lines(state, [npc])`; "knows:" skips
   `source in (correction, testimony)`, `agreed`, `correction.`; a "people they speak of" block of identity lines for
   names in the card's knows and said lines.
6. **Framer enum** (`schemas.schema_context`): `usable` filtered by `lever_candidate` (not a scene slot, not
   `said.*`, not `source: correction`).
7. **Stance** (`social.first_interaction`): bound the rolled standing by `npc_field(npc, "stance").stance` when not a
   faction roll.
8. **Patches**: `narration.pause_blocks` uses `oof.goal_line(BeatPlan(...).beat)`; `resolution.yaml#intended_change.split`.

## Measurement (offline, read-only on the saves)
`specs/021-testimony-answers/measure.py`: projects each save's state at every Reader call and re-runs the triggers;
reports old vs new settlement per offered turn. The claim call is re-run on Haiku over the 30 recorded settled
records (old vs new: lost subject, garbled, refusal/intention stored). Pronouns: for the 9 checkable speech lines,
whether the rebuilt narrator packet carries the absent person's pronouns. Output committed next to it.
