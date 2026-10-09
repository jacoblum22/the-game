# Tasks 022

- [x] T1 Trace I3 §1-§5 on the round-6 saves (plan "Trace first").
- [x] T2 [US1] Hold ladder condition in `change.py`; untyped Grapple keeps hold; tightening.
- [x] T3 [US1] `conflict.holds`/`end_hold`/`_break_free`; `foe_beat` row 2 first.
- [x] T4 [US1] `scene_state`: posture only while held; `_free`/`release_holds` end the condition; delete `_holds`.
- [x] T5 [US1] Folded grip (spec 020 hand-off): `Beat.holds`, `_fold_methods`, `pipeline._folded_hold`.
- [x] T6 [US2] `world_step`: no foe beat on an all-refused turn.
- [x] T7 [US3] `price`/`pay` at RECORD; coin in `Changed:`.
- [x] T8 [US4] `engine/dm/fixer.py` tools + loop + `prompts/fixer.md`; offline double.
- [x] T9 [US4] `dispute.py` rewritten: validate, apply on one snapshot, found → did → Now:, log; delete
      `understand.py`, its prompt, `Role.UNDERSTAND`, `_claim`, the CHOICE path's producer.
- [x] T10 [US5] `Role.FIXER`, `Routed`, `--fixer-model sonnet`; Gemini slot via `GameConfig.models`.
- [x] T11 Delete `feedback.understand_call` and `feedback.outcomes` from `pacing.yaml`.
- [x] T12 Tests: `test_mechanics_state.py` (9 held hits from saves, break-free, refused turn, payment, folded grip),
      `test_fixer.py` (G4 take-back with Now:, evidence validation, no report text pinned, tools read-only and
      sealed-safe, bounded loop, routing); updated scene/intended-change/combat/e2e/schema tests.
- [x] T13 Label round-6 (15) and held-out (7) sets before running; commit.
- [x] T14 Sonnet runs: round-6, held-out, corpus; hand-grade by I3's standard.
- [x] T15 Live fighter playtest (Haiku, Fixer on Sonnet).
- [x] T16 Merge milestone-1-playable, regenerate, full suite; `implementation-results.md`.

## Analyze (consistency check, done by hand)
- Every R2-J "Spec 022" build item maps to a task: hold condition (T2-T4), break-free (T3), payments (T7), Now: (T9),
  Fixer tools/steps/proposals/validation/snapshot/reply/model (T8-T10). Retire list → spec "Retired".
- Spec US1's "posture written from it" is met by rows gated on the condition (T4), not a second writer.
- No task touches spec 020's or 021's lanes beyond the one-line justifications in plan.md.
