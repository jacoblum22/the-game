# Tasks 029

- [x] T1 Spec, cases (`cases.md`) and the labelled multi-part clue set (`clue_set_multi.yaml`) committed before implementing.
- [ ] T2 Data: `world_seed.yaml#terms` for the 52 kinds `[revision: R2-L]`; `investigation.yaml#journal` row fix; validator 0/0.
- [ ] T3 `engine/gen/hooks.py`: terms by kind (incidents, situation traces, hire, documents), people by id, documents with
  text, walk-ons, `write_terms`; `kinds()` for the enumeration test.
- [ ] T4 Lead injection, rumors and creation hooks: `write_injection`, `rumor_terms`, `creation_terms` (same builder).
- [ ] T5 The actor on stage: `incident.actor_on_stage`, `session.opening`, `case.py` (subject alias, sealed name), the rider.
- [ ] T6 P9: clue prompt/schema/stub for several parts; `answer.ask_message`; `deliver_learning` and `_speech_answers`;
  `record.learned` and its handle; answered only when a fact was delivered; `_look` (Recall) one call.
- [ ] T7 Journal: `testimony.told_to_pc`, `codex.what_you_know` (split, thread text, said records, attribution).
- [ ] T8 Tests `tests/engine/test_spec029_cases.py` (K1-K52 walked from the data, P1-P6, C1-C10, J1-J5, S1); update the
  retired-behaviour tests.
- [ ] T9 Gates: suite, replay re-record, ruff/pyright, validator, longhorizon scripted, round-8 saves replay, clue eval
  (025 set + multi set) on Haiku, live explorer on Haiku.
- [ ] T10 `implementation-results.md`; merge `milestone-1-playable`; commit.
