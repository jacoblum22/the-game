# Tasks: Adjudication (spec 007)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md),
[contracts/offer.md](contracts/offer.md). Tests are requested by the brief (gate table, OFFER snapshots,
forbidden tokens, golden set, odds audit).

## Phase 1: Setup

- [X] T001 Rebuild the stale compiled cards (`engine/build/compile_cards.py`; baseline failure
  `tests/engine/test_build.py::test_committed_cards_are_current` after the R2-C rule edits) in engine/build/cards.json

## Phase 2: Foundational (blocking)

- [X] T002 Add `against_will`, `uses_power`, `speech`, `asks` to `Beat`; remove `gate`, `would_be_license`,
  `g4_test`; add `obstacle_class`, `nudge`, `nudge_fact`, `nudge_why`, `request_size` to `Obstacle`; add
  `obstacle_class`, `nudge`, `long_shot`, `alternatives`, `guard` to `Frame` and `long_shot` to `OfferPreview` in
  engine/resolve/types.py

## Phase 3: User Story 1 — computed gate (P1)

**Independent test**: gate table test; golden set (verb ≥ 95%, gate ≥ 98%).

- [X] T003 [US1] Rewrite engine/resolve/gate.py: pure `covering_verb()`, `compute_gate()` (R1 order), `check_gate()`
  wrapper reading conditions, licences, literacy and the G4 fact from state; `would_be_license` without the Reader
  field; delete the "G1 before G3" override, the "G2 before G3" cited-licence pass and `_plain_form_of`
- [X] T004 [US1] Reader schema in engine/dm/schemas.py: parts gain `question_kind` (`none` first, then `who_is`,
  `where_is`, `what_happened`, `what_like`, `what_want`, `who_knows`) and nullable `topic`; beats drop `gate`,
  `license`, `would_be_license`, `necessity`, gain `shape` (`now`, `queued`, `conditional`), `against_will`,
  `uses_power`, `speech`
- [X] T005 [US1] engine/dm/roles/reader.py: code pre-router for "what do I know?" before the call; delete
  `reader_check`'s G2 rule and `_plain_reading`; map facets and shape into `Beat` (queued/conditional beats are
  restated as queued, not run); `asks` from parts' `question_kind`
- [X] T006 [US1] Rewrite engine/dm/roles/prompts/reader.md: drop gate, would-be licence, necessity and gentle-touch
  lines; add facets, question kind, shape; stay under the current word count
- [X] T007 [US1] Offline Reader in engine/llm/offline.py: emit the new fields
- [X] T008 [P] [US1] tests/engine/test_gate_table.py: every verb × facet combination × {no licence, a held covering
  licence, a held power licence}; knack never gates; excluded methods; literacy
- [X] T009 [US1] Update tests that build beats with `gate=` / `would_be_license=` (tests/engine/test_resolve_gate.py,
  test_pipeline.py, test_creation.py, test_play_bugs_p115_p118.py, test_reading.py, others found by pytest)

## Phase 4: User Story 2 — necessity and rubric (P1)

**Independent test**: tests/engine/test_necessity.py; frame_check unit tests; odds audit.

- [X] T010 [US2] New engine/resolve/necessity.py: `necessity()` (fallback roll, plain reading trivial, certain social
  trivial), `trivial_class()`, `parties_who_would_act()`
- [X] T011 [US2] engine/resolve/pipeline.py: necessity from code before framing (skips the Framer); trivial class
  after framing → no roll
- [X] T012 [US2] engine/resolve/costs.py: `established_stakes_sources` uses `parties_who_would_act` (retire the
  ponytail); `stakes_cost_menus` narrowing in `uncited_candidates` and `check_cost_decl`, harm under the observer
  source only with a cited source fact
- [X] T013 [US2] Framer schema in engine/dm/schemas.py: class / other+tier / opposed branches, `nudge_why` before
  `nudge` ("-1","0","+1"), `nudge_fact`, `request_size` for social beats; default frame `other` at Easy (or the
  opposed target); drop the Moderate default
- [X] T014 [US2] engine/dm/roles/framer.py: `to_proposed` reads the new obstacle fields; default frame
- [X] T015 [US2] engine/resolve/frame.py `_dc`: class base + nudge (refusals per data-model.md step 6), social DC
  (defense + standing `dc_mod` + request `dc_mod`), forced opposed for social/attack beats on a creature
- [X] T016 [US2] engine/resolve/frame.py: snag cap (first Precision, rest Protective), the 01.6.13 guard and
  `long_shot`, `alternatives()` (attributes; sibling attack verbs)
- [X] T017 [US2] Rewrite engine/dm/roles/prompts/framer.md obstacle/snag lines (no HIGHER tie-break, no snag
  tie-break), within budget
- [X] T018 [US2] Offline Framer in engine/llm/offline.py: new obstacle shape
- [X] T019 [P] [US2] tests/engine/test_necessity.py and frame_check cases (snag cap, guard, nudge refusals,
  cost menus) in tests/engine/test_rubric.py

## Phase 5: User Story 3 — OFFER and menu (P2)

**Independent test**: tests/engine/test_offer_snapshots.py; play tests of the menu.

- [X] T020 [US3] engine/dm/oof.py: OFFER template per contracts/offer.md, word maps, `GLOSSARY`; delete
  `_difficulty_phrase`; severity words in near-miss and RESULT lines
- [X] T021 [US3] engine/resolve/frame.py: delete `plain_offer_words`, `_fix_pronouns`, `_fact_words`;
  `auto_commit_allowed` Safe only and not long shot; engine/resolve/pipeline.py: delete TRADE_LABELS and
  `offer_text`, plain choice labels, the rendered block as the pause prompt and the auto OFFER
- [X] T022 [US3] engine/dm/context.py: `auto_commit()` defaults to `resolution.yaml#auto_commit.default`
- [X] T023 [US3] play/render.py + play/cli.py: menu line (`[Enter] …`, letter keys, `[?] Explain`), Enter rules,
  `?` glossary
- [X] T024 [P] [US3] tests/engine/test_offer_snapshots.py: ~20 canonical frames + forbidden-token test; update
  tests/engine/test_oof.py and play tests

## Phase 6: Polish

- [X] T025 evals/reader_golden.py: `haiku` and `cached` plugs, computed gate, negation pairs, `--audit` (frames each
  rolled golden beat with `frame_check` in the dock fixture, tests/fixtures/scene_dock.py, over every obstacle class
  of its verb and 0-2 hindering facts)
- [X] T026 Run the golden set on Haiku; record the baseline in evals/baselines/
- [X] T027 Ledger row for the double-error bound in rules/_process/issue-ledger.md
- [X] T028 Re-record replays (`py -3.12 -m tests.replay.record_games`); full suite, ruff, pyright
- [X] T029 engine/CONVENTIONS.md API notes; specs/007-adjudication/implementation-results.md with the gate table

## Dependencies

T002 → everything. US1 (T003–T009) before US2 (pipeline uses the computed gate). US3 depends on T016 (long shot,
alternatives). T025–T026 need T003–T006. Parallel: T008, T019, T024 (test files).

## Implementation strategy

MVP = US1 (the gate, measurable on the golden set). Then US2, then US3; commit after each phase with the suite green.
