# Tasks 029

- [x] T1 Spec, cases (`cases.md`) and the labelled multi-part clue set (`clue_set_multi.yaml`) committed before implementing.
- [x] T2 Data: `world_seed.yaml#terms` for the 52 kinds `[revision: R2-L]`; `investigation.yaml#journal` row restored
  (`journal.rumors` was swallowed by a comment); validator 0/0.
- [x] T3 `engine/gen/hooks.py`: terms by kind (incidents, situation traces, hire, documents, rumors), people by id,
  documents with text, walk-ons, `write_terms`, `kinds()` for the enumeration test; card lines inside the 160-character cut.
- [x] T4 Lead injection (`write_injection`, called from `pacing.inject_lead`) and creation hooks (`write_creation`,
  called from `creation.py`): the same builder.
- [x] T5 The actor on stage: `incident.stage_info/stage_actor`, `session.opening` casts the subject by id, the note names
  the role; the dead rider is an entity.
- [x] T6 P9: clue prompt/schema/stub for several parts; `answer.ask_message`; `deliver_learning` and `_speech_answers`;
  `record.learned` and its `learned` handle; a part answered only when a fact was delivered; Recall one call; learning
  keyed on the typed verb (R8-I2 cause D).
- [x] T7 Journal: said records carry place and day; `codex.what_you_know` splits, searches thread text, said records and
  knowledge, and shows "what you were told" attributed; the general journal lists it too.
- [x] T8 Tests `tests/engine/test_spec029_cases.py` (K1-K52 walked from the data, P1-P6, C1-C10, J1-J5, S1); retired
  behaviour updated in spec 025's tests.
- [x] T9 Gates: suite, replay re-record, ruff/pyright, validator, longhorizon scripted, round-8 saves replay, clue eval
  (025 set + multi set) on Haiku, live explorer on Haiku.
- [ ] T10 `implementation-results.md`; merge `milestone-1-playable`; commit.
