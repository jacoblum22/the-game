# Implementation Plan: Typed intended change (spec 015)

**Spec**: [spec.md](spec.md) · **Scope**: R2-H report, "Engine checklist → Spec 015" items 1-6; spec 016 item 3;
problem 13 (knockout status line).

## Technical Context

Python 3.12, Pydantic v2, the existing engine; offline/scripted models in tests; Haiku through the Claude CLI for
the golden sets and the one live run. No new dependency. Constitution v2.0.0 Principle I: the kind and slots are one
`[J:enum]` Reader judgment; applying, scaling, refusing and citing the change are `[D]` code. Gate: pass.

## Design (research folded in; one row per item)

| # | Decision | Files |
|---|---|---|
| 1 | `Change(kind="none", what=None, whom=None)` in `engine/resolve/types.py`; `Beat.change: Change \| None` (None = untyped, an old save). Reader beat schema gains `change {kind, what, whom}`: `kind` enum = `resolution.yaml#intended_change.kinds` (13, `none` first); `what` = scope ids + the PC's and present people's things + reachable places; `whom` = scope ids (`none` first). `SchemaContext.change_kinds`, `.change_ids`. `ReaderBeat.change` → `Beat.change` in `plans`. `what`/`whom` are the kind's first/second data slot. Prompt: one short section; two changes are two beats. Offline reader types a change by verb (Grapple/Handle with an item target → take, Strike → harm, Move → move_to, else none). | types.py, schemas.py, reader.py, prompts/reader.md, llm/offline.py |
| 2 | Laya log: `reader.log_changes(ctx, plans, scope)` appends one JSON line per beat to `<save>.changes.jsonl` (beside the game file, as the disputes log): turn, restatement, verb, ids_in_scope, kind, slots, defaulted. Never in the event log (wall clock-free state); an OSError never fails the turn. | reader.py (called in `read_message`, which holds the scope ids) |
| 3 | New `engine/resolve/change.py`: `holder_of(state, item)` (current `holder` fact, then `carried_on`/`held_by`/`carried_by` facts, then data keys); `apply_change(env, beat, reach) -> ChangeResult(words, refused, events)`. take: item must exist, be held by `whom` when both are known, not by the actor; reach 1 → fact `contested_by` = actor, reach ≥2 → `holder` = actor. give: actor holds it, `whom` a present person → `holder` = whom. open/close → fact `open` true/false. persuade_to → `agreed` = intent (reach 1: "a smaller part"). hide → `hidden_from` = whom or "everyone". restrain/free → scene_state (row 6). move_to/harm/learn → their writers already ran (PR-06-4, 06.3.5, ch.06/07, 01.10); words only. make → refused "crafting is not built yet". Called from `pipeline._finish` when resolved (success or success at cost, after the cost) and `_no_roll` (reach 2); failure: never called. `BeatEntry.change` (plain words of the typed change), `.changed` (applied words), `.change_refused` (why not). RESULT gains `Changed:`/`Not changed:` words. | change.py, pipeline.py, adjudication.py, oof.py |
| 4 | OFFER: `oof.change_line(state, beat)` ("Taking: the coin purse, from Murzak Red-Hand") under the title; `_offer` passes the queued beats' restatements → "Then: …" line. Separate functions; one call each in `offer_block`. | oof.py, pipeline.py |
| 5 | Must-name: `handles.items` adds kind `change` per beat with `changed` or `change_refused` (must-name); narrator words "the change (say it plainly): …". Claims: `_Ctx.holder` reads the current `holder` fact before data keys (a given or taken kit item); `_beat_for` overlaps the change words; codex inventory likewise reads the holder fact first. | handles.py, roles/narrator.py, claims.py, codex.py |
| 6 | T-12-18 fold: `scene_state.beat_writes` reads the beat's change: Grapple rows apply only when the change is `restrain` or untyped (a `take` Grapple writes only the target's manner, the failure row); a `restrain` typed on another verb uses the Grapple rows; `free` (success) clears the hold on `what` (or the actor) via the `release_holds` writer. `BeatEntry.change_kind` carries the kind to the world step. | scene_state.py, adjudication.py |
| 7 | Rubric (DL-01-35) in `frame._frame_check` step 4: `lift_attribute(rules, state, beat, actor, ...)` when the change is `take` or the method lifts/carries/palms (data words + lift/carry/palm/pick up): data words pick; else best `min(cap, attr+comp+edge)+status` among might/agility/endurance (ties keep the proposed). `alternatives(..., attrs=)` lists the other two with odds. | frame.py |
| 8 | Knockout: `harm.apply.status_block` Staggered line adds "a blow adds 1 to 4 by how hard it lands"; `world_step._foe_turn` RESULT adds "wound load a → b" when a blow added load. | harm/apply.py, world_step.py |
| 9 | Tests `tests/engine/test_intended_change.py`; golden `change_kind` labels (01.2.7, before reading answers) + scorer field; replay re-recorded. | tests/, evals/ |

## Constitution Check (post-design)

Principle I holds: one closed-enum judgment (kind, two slot ids), everything else `[D]`. INV-3: no numeric field
added. Old saves: beats without `change` keep the per-verb behaviour. Pass.

## Validation

`py -3.12 -m pytest -q -p no:cacheprovider`; `uvx ruff check` / `uvx pyright` on touched files;
`py -3.12 evals/reader_live.py --model haiku [--set heldout] --cache <new>`; `py -3.12 evals/longhorizon.py --mode
scripted`; the live fighter run in the brief.
