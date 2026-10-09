# Plan: spec 018 (round-4 engine fixes)

**Spec**: [spec.md](spec.md). Python 3.12, existing modules only; no new files in `engine/`. Tests in
`tests/engine/test_round4_fixes.py` with two truncated save fixtures in `tests/fixtures/` (the 015 pattern:
`*.db.gz`, events after the cut removed, model calls dropped).

## Design (smallest change per item)

1. **Plain speech**: wording only in `engine/dm/packet.py` (`speaker_card` header and empty-card line),
   `engine/dm/roles/narrator.py` (`_speech_line`), `engine/dm/answer.py` (`WILL_WORDS["guarded"]`). The same lines
   carry the self-introduction rule (US6.1).
2. **Description slot**: `Change.description: str | None` (`engine/resolve/types.py`); Reader schema adds
   `description` (string or null) to `change` (`engine/dm/schemas.py`), prompt line in `prompts/reader.md`, the Laya
   log records it (`reader.log_changes`). `engine/resolve/change.py`:
   - `_person(state, beat)`: the persuaded person is the first of what/whom/target that is a person and **not the
     actor**; else the one person in scope the description names (`resolve_names`); else None.
   - `persuade_to` on a description (no person): a scene fact on the scene's place, predicate `agreed.<slug>`,
     `persistence="scene"`; `open`/`close` likewise (`open.<slug>`). `details.expire_events` clears every scene
     fact (it now clears `crowd_response` by persistence, not by name: one loop instead of a special case).
   - Words: "Agreed by <who>: <act>" (no verb agreement to get wrong). `plain()` shows the description.
3. **Movement**: `engine/resolve/necessity.py` `necessity()`: a Move whose target is the place the PC is in (no
   party who would act) is `trivial`. (Implement note: an approach to someone present already gets the Move
   rubric's `trivial` open-ground base from the Framer, and an obstacle a rolled class, so no necessity code.) `pipeline._moved` (small
   edit): outside a conflict toward a target → `engaged` (reach 2+); reach 1 keeps the one-band step; a target that
   is the place here writes no "still in" words. New `pipeline.band_words(state, band)` → "beside" for `engaged`
   outside a conflict (also used by `scene_state.lines`). Travel: `narration.narrate_turn` passes purpose
   `scene_open` when the record started a scene; `handles.items` puts a mid-turn cut's scene line after the beats
   and makes it must-name; `PURPOSE_LINES["scene_open"]` says "narrate the beats, then the arrival".
4. **Already true / no target**: `change.already_true(state, beat) -> str` (words, "" when not) for take (holder is
   actor), persuade_to (an `agreed` fact on that person covering the act, `audit.text.covers` 0.6), open/close (the
   `open` fact); move_to dropped at implement (an approach is already no-roll and ends beside). `necessity()` returns `trivial` when it holds; `apply_change` returns
   those words (no events, not refused). `change.needs_target(state, beat) -> str` (the "who?" words): kinds
   persuade_to/take/give/restrain/open/close with no usable slot, no target, no description. `pipeline._start` asks
   it before NECESSITY and returns status `question` (gate G0), which the narrator words as "not done: ..." and asks.
5. **Setting once**: `packet.scene_setting(state, full=True)`: `full=False` drops the place description, look,
   furniture, landmarks and terrain, and adds "already described" (people, exits, time stay). `narrator.draft`
   passes `full` for `scene_open`/`opening` or a look-around message.
6. **Patches**: self-introduction in the speech lines (1); `declare.pc_quotes` also returns the quote(s) adjacent to
   a "you say" clause in a sentence with an NPC speaker, and `_speech` removes them from the NPC's spans (2); the
   plain-words fix is item 2's `_person` + "Agreed by" words (3).

## What is deleted or simplified
- The hedging instructions (three prompt strings).
- Band-by-band approach outside a conflict (`_moved`'s floor at `close` that never reached engaged).
- The "still in X" position line for a Move to the place the PC is in.
- `crowd_response`'s special case in `expire_events` (generalised to scene persistence).
- The look/furniture in every turn's packet.
- `take`'s "already have" refusal (now an already-true line, no roll).

## Risks
- Replay recordings change (packets): re-record with `py -3.12 -m tests.replay.record_games`.
- `necessity` trivial for approaches could skip a roll the Framer would have made for an obstacle: guarded by
  `parties_who_would_act`; DL-12-98's revisit condition covers it.
- Lane 017 conflicts in `pipeline.py` (`_start`, `_moved`) and `narration.py`: kept to a few lines.
