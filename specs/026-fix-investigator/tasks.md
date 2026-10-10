# Tasks 026

- [x] T1 Trace R7-I3 §3 / R7-H2 T7 in code (plan "Trace first"); find the take-back-leaves-the-OFFER bug.
- [x] T2 Write and label the fresh held-out complaints (13, `fresh.json`) and their made-up saves
      (`evals/fix_scenarios.py` → `fresh-*.db.gz`); label `round7.json`; screen label on round-6 233000-t9. Commit
      before implementing.
- [ ] T3 [US1] `packet.people_card`; cards in the Reader, Framer and Narrator views; delete `framer.target_record`.
- [ ] T4 [US2] Fixer tools: people card in `entity` and the opening; `plain_fact` everywhere; `calls`; effective
      degree in `turn`.
- [ ] T5 [US3] `reframe` in `dispute._apply`; `_take_back` closes the pending OFFER; delete `rerender`/`_rerender`;
      `DisputeResult.outcomes`; `turn._dispute` takes them.
- [ ] T6 [US4] `sandbox`/`preview`; `try` and `replay` tools; the check-screen loop in `fixer.investigate`.
- [ ] T7 [US2] `fixer.md`: tools, re-frame, pending take-back, mechanics digest, sheet over Oracle; budget.
- [ ] T8 [US5] Validation review: the spine guards only (conjured coin, sealed, evidence, identity, take-back limit).
- [ ] T9 `pacing.yaml#feedback.investigate` keys; validator 0/0.
- [ ] T10 [US6] `feedback_corpus.py`: whole-turn run, screen scoring, `fresh`/`round7` sets, cached replay of Fixer and
      Framer answers.
- [ ] T11 Tests: people card (Belie in all three roles + the Fixer), plain facts, `calls`, re-frame (Belie, Tam),
      pending take-back, dry run leaves the store untouched, check-screen revision, spine guards; update tests that
      used `rerender`, `target_record`, the old replay baselines.
- [ ] T12 Re-record the replay; full suite; ruff and pyright on touched files; validator; longhorizon scripted.
- [ ] T13 Sonnet runs: `fresh` (headline, once), `round7`, `round6` (after; before from the 022 baseline), `heldout`.
- [ ] T14 Live fighter playtest on Haiku (Fixer on Sonnet), at most 15 turns; grade every `/fix`.
- [ ] T15 Merge milestone-1-playable, regenerate, full suite; `implementation-results.md`; anti-pattern check.

## Analyze (consistency check, done by hand)
- R2-K "Spec 026" build list → tasks: shared people card (T3, T4), plain facts (T4), model I/O (T4), dry run (T6),
  reframe (T5), pending take-back (T5), check screen + iterate (T6), digest (T7), spine-only validation (T8), scoring on
  fresh held-out by screen (T2, T10, T13). Retire list → spec "Retired" (rerender T5; explain-only T5/T7; entity tool
  T4; outcome-class scoring T10).
- R2-K cases → labelled: Belie at the open OFFER (round7 r7-fighter-dsp2), the guard and my rank (f04), the effective
  degree case ("I paid for the round, why did he refuse") is covered by the turn tool's effective degree (T4, unit
  test) rather than a labelled report (no save holds that exact state after spec 023's 01.9.3 change), 50 gold (f10),
  re-frame still showing the complaint (T11 scripted test), sealed culprit (f11).
- No task touches spec 025's lane. turn.py and framer.py edits are one function each, justified in plan.md.
- Coverage gap noted: "Stagger" and "holds" in the digest have no fresh case (no fresh complaint about a hold); the
  round-6 and spec-022 held-out sets (h1, h7) exercise them.
