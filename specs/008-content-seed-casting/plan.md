# Implementation Plan: Content seed, casting and the reduced case (008 part A)

**Branch**: `worktree-agent-a057e6ec4e10abb58` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

## Summary

Port the R2-D reference (`rules/_process/simulation/12-world-seed.py`: `seed_packs`, `reduced_case`,
`validate_case`, `check_packs`, `role_key`, `keyed`) into `engine/gen`, apply the packs inside
`WorldSeed.record()`, carry them into the store at `write_world`, add casting (`engine/gen/cast.py`) and the
reduced case builder (`engine/gen/case.py`), move `h.15.placement_audit` to M1, write I-149 name knowledge at
the opening, retire the opening binding, and make person names inexhaustible. Decisions: [research.md](research.md);
shapes: [data-model.md](data-model.md); part-B entry points: [contracts/api.md](contracts/api.md).

## Technical Context

**Language/Version**: Python 3.12 (`py -3.12`).
**Primary Dependencies**: the engine only (Pydantic, PyYAML via `engine/gen/_data`).
**Storage**: the event store; packs ride in entity data, cases in meta `world.cases`.
**Testing**: pytest (`tests/engine/`, `tests/golden/`); the replay games re-recorded.
**Target Platform**: Windows dev machine / cloud sessions, offline.
**Project Type**: library (engine package).
**Performance Goals**: packing adds < 0.5 s per seed; per-turn packet growth reported (target: present place only).
**Constraints**: lanes (spec brief): own `engine/gen/`, `engine/dm/incident.py`, `engine/dm/seed_flow.py`,
`engine/time/handlers/h15.py`, the opening's binding call. One-line call-site edits elsewhere are reported.
No `rules/` content edits beyond ledger rows.
**Scale/Scope**: ~34 places, ~21 cast, 3 documents, 1 case (~6 placements) per seed.

## Constitution Check

| Principle | Effect | Status |
|---|---|---|
| I. AI-driven mechanical resolution | Packs, casting, cases are `[D]` code over rules data; no model call | Pass |
| II. Custom ruleset | Implements R2-D rules as written; no rules edits | Pass |
| III. Bounded flexibility | Removes a uniform-random narrator-facing pick (I-148) in favour of the `cast` domain | Pass |
| IV. MVP scope | Reduced case only (D4); full PR-15-6 stays M6 | Pass |
| V. Closed primitives | Casting registers a domain config, no new generator (00.11.1) | Pass |
| VI. Consolidation | Retires `bind_incident`/`SUBJECTS` | Pass |
| VII. Default-deny gate | Not touched | Pass |
| Technology constraints | No new dependency | Pass |

Post-design re-check: unchanged.

## Project Structure

```text
specs/008-content-seed-casting/  spec.md plan.md research.md data-model.md quickstart.md contracts/api.md
                                 tasks.md implementation-results.md
engine/gen/_seed_packs.py   # NEW port: keyed, place_type, role_key, pack_places, pack_npcs, documents, seed_packs, check_packs
engine/gen/case.py          # NEW reduced_case, validate_case, pointer, case_for_question (on demand), write_case, audit
engine/gen/cast.py          # NEW cast(state, role, *, scope), pointer target, base pool (ex incident._people)
engine/gen/world_seed.py    # record() packs; run_check maps pack failures to step 13
engine/gen/_seed_check.py   # check_seed runs the 7 pack checks too
engine/gen/_seed_lib.py     # person_name: syllable fallback (names never run out)
engine/dm/seed_flow.py      # write_world: walk-ons, documents, cases into the store
engine/dm/incident.py       # retire bind_incident/SUBJECTS; incident_line over the case; start_knowledge (I-149); settle_who via case/cast
engine/dm/session.py        # call site only: start_knowledge instead of bind_incident
engine/dm/packet.py         # scene_setting: present place's look, furniture, exits (3 lines)
engine/world/places.py      # NPC_SEALED += knowledge (1 line)
engine/time/handlers/__init__.py, h15.py   # placement_audit M6 -> M1, registered
tests/engine/test_seed_packs.py, test_case.py, test_cast.py; tests/golden/test_world_seed_parity.py (packed parity)
```

**Structure Decision**: the reference keeps packs and the case in one file; the engine splits them so
`case.py` (seed time and on demand) and `cast.py` (part B's `who` questions) are importable on their own.

## Complexity Tracking

| Deviation | Why | Simpler alternative rejected |
|---|---|---|
| Edits outside the lane (`session.py`, `packet.py`, `places.py`, handler table) | The binding is called from `session.opening`, not `opening.py`; 12.4.3 needs the look rendered; knowledge must not reach the narrator view | Leaving them would keep the retired binding live or leak packs into packets |

---

## Part B plan: the answer ladder

- New `engine/dm/answer.py` (PR-12-10): `ask(ctx, knower, kind, topic, text, rungs, pc=)` -> `Answer(line, said,
  fact_id, pointer)`; `volunteer`; `deliver_count`; `who_answer` (the DM-side "who is X?", replacing
  `settle_who`); `deliver_placements` (15.9.5 for Observe at a holder).
- New role `proposer` (`engine/llm/base.Role`, schema in `engine/dm/schemas.py`, prompt
  `engine/dm/roles/prompts/proposer.md`, call in `engine/dm/roles/proposer.py`, offline heuristic in
  `engine/llm/offline.py`, Gemini output cap, card list, schema fixture).
- `world_step.deliver_learning` routes successful learning beats with questions (and SPEECH questions with no Talk
  beat) to the ladder; returns per-beat summaries (the harness's empty-success and ask-twice metrics).
- `npc_layer`: the Talk outcome is "answers what you asked" / T-15-5's yes by reach; SPEECH-answered NPCs are
  skipped.
- `turn._fiction_questions` calls `answer.who_answer` (one-line call site).
- Offline Reader: question kinds for declared asks ("I ask X what ..."), topic left null.
- `evals/longhorizon.py`: empty-success rate and ask-twice consistency; an `ask_twice` script line.
- Lanes: `claims.py` (009-B) gets one line (`_learning_success` unreachable).
