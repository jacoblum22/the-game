# Plan 022: mechanics as state + the Fixer

## Trace first (done before design; I3 confirmed on the saves)
- 233000: no `condition_applied` on Dunwen in the whole save; grapple frames typed `restrain` (frame.1-3); foe hits on
  turns 4, 6, 10, 14 while `detail.posture = held fast by you`. 135049/145430 grapples untyped (older Reader).
- 233000 turn 14: `ruling_logged` g4 (seq 583), then `quantity_changed` 1 → 0 (584), staggered (585), round (587).
- 192926 turn 7: frame.2 `method_consequences: ["The coin for the round is spent whatever the answer."]`, no coin
  write; the PC's `coin` quantity exists (creation).
- 233000 turn 15's take-back reverted 578-580 and 584-586 with no line saying Vitality came back.
- The seven round-6 reports hold the 15 disputes (several complaints per report, settled one by one by the old code).

## Design (code owns the spine; the model owns judgment)
| Piece | Where | What |
|---|---|---|
| Hold ladder | `resolve/change.py` | `LADDER`, `current_hold`, `hold_level`, `hold()`; `restrain` applies the condition; an untyped Grapple on a person is `restrain` (06.5.2's Decision) |
| Hold lifecycle | `resolve/conflict.py` | `holds(st)` from conditions; `end_hold` removes conditions and clears posture/held; `_break_free`; `foe_beat` row 2 first |
| Face | `dm/scene_state.py` (one-line justification: it writes T-12-18's face) | posture rows only while the condition stands; `_free`/`release_holds` call `end_hold`; text-matched `_holds` deleted |
| Folded grip | `resolve/types.py` `Beat.holds`; `dm/roles/reader.py` `_fold_methods` (one line); `resolve/pipeline.py` `_folded_hold` | the goal's success applies the hold |
| Refused turn | `dm/world_step.py` (justification: the free strike happens there) | no foe beat when every beat was refused |
| Payment | `resolve/change.py` `price`/`pay`; `pipeline._finish` | coin write at RECORD; `oof._SHOWN_QTY` gains coin (justification: the `Changed:` line) |
| Fixer | `dm/fixer.py`, `prompts/fixer.md` | tools, step schema, bounded loop, offline double in `llm/offline.py` |
| Validate/apply/answer | `dm/dispute.py` (rewritten) | proposal validation, one snapshot, `now_line`, ledger and review log |
| Model slot | `llm/base.py` `Role.FIXER`, `Routed`; `llm/gemini.py` output budget; `evals/playtest.py` `--fixer-model` (justification: the live gate) | Sonnet for the Fixer |
| Data | `pacing.yaml#feedback` | `understand_call` and `outcomes` deleted |

## Gates
Full suite; ruff/pyright on touched files; `longhorizon --mode scripted` 0 engine errors; F5 tests from the saves;
`feedback_corpus.py` corpus before/after; round-6 (15) and held-out (7) on Sonnet; live fighter run on Haiku ≤15
turns with the Fixer on Sonnet.

## Anti-pattern check (handoff §3.3)
- Code authoring narrative truth: the Fixer's `found` is model text shown OOF only; code writes only typed values,
  never the report; testimony settlements can be undone. The `Done:` lines are code's description of its own writes.
- Mechanics stored as text: the hold, the coin and the restore are all writes now.
- Atomisation: complaints are handled as one report on one snapshot.
- Low-precision blocking checks: validation blocks only what INV-9/INV-10/T-00-1 require (record ids seen, bounds).
- Test traps: the round-6 and held-out sets were labelled and committed (636a9f1) before any Fixer run.
