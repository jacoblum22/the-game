# Implementation results: 008 part A (seed packs, casting, reduced case)

Branch `worktree-agent-a057e6ec4e10abb58`, from 1de755a. Spec-kit: specify, plan, tasks, analyze (2 findings fixed:
pack determinism added to T009; I-149 tests moved to `test_incident.py`), implement. Clarify skipped; assumptions
are in [spec.md](spec.md#assumptions).

## Gates

| Gate | Result |
|---|---|
| Full suite (`pytest -q -p no:cacheprovider`) | 1197 passed, 4 skipped (base 1de755a: 1176 passed, 1 failed: stale `cards.json` meta, fixed here by recompiling; cards unchanged, only the tree hash) |
| ruff / pyright on touched files | clean / 0 errors (repo-wide ruff: 10 pre-existing findings in other lanes' files) |
| Engine = reference, packed | `tests/golden/test_world_seed_parity.py`: 10 rolled seeds + the guided run equal `ref.seed_packs(ref.build_seed(s), s)`; check rows equal `check_seed + check_packs` (13 passed) |
| Seed-check unit tests | `tests/engine/test_seed_packs.py` (7): 71 of 71 rows on seeds 1, 21, 26; each pack check fails on its own breakage |
| PR-15-6 validity as unit tests | `tests/engine/test_case.py` (8): each 15.9.4 rule (placements, reserve, methods, nodes, fallbacks, core at the opening place) |
| Determinism | same seed -> identical places' packs, NPC packs, documents, walk-ons, case (seed 21; `reduced_case` seed 5) |
| 30 seeded openings | 30 of 30 incident cases valid; core placement at the opening place, its holder positioned there in the store (seeds 1-30: 6 duel, 5 theft, 4 alarm, 4 dying_messenger, 3 offer, 3 refugees, 3 omen, 2 missing) |
| `evals/longhorizon.py --mode scripted --lines 320` | 320 lines, 337 turns, **0 engine errors** (before: 7, "names exhausted" from line 224) |
| Placement audit in M1 | `runnable("h.15.placement_audit", 1)`; reserve placed when 2 holders die, PR-15-7 generic when the reserve leaves |

## Packet size (per turn, offline, 60 scripted lines x seeds 7, 11, 23; scratch `packet_mean.py`)

| Role | before | after | change |
|---|---|---|---|
| narrator | 16343 | 16450 | +107 (+0.7%): view +59, THIS MESSAGE (scene setting) +49 |
| reader | 14105 | 14165 | +60 |
| world | 14914 | 14981 | +67 |
| director | 13803 | 13853 | +50 |
| checker | 5548 | 5554 | +6 |

Only the present place's look, furniture and exits render (`scene_setting`), plus a notice's text when the PC stands
where it is posted (pinned written words). NPC knowledge packs are a sealed data field; stances and other places'
packs are past the 12-key view cap; case records (meta) are never rendered. Far below C §4.5's 300-600 estimate.

## What changed

- New: `engine/gen/_seed_packs.py` (port), `engine/gen/case.py`, `engine/gen/cast.py`, `tests/fixtures/seeded.py`,
  tests `test_seed_packs.py`, `test_case.py`, `test_cast.py`.
- `world_seed.record()` packs; `_seed_check.check_seed` runs the 7 pack rows on a packed record; pack failures re-run
  from step 13. `seed_flow.write_world` -> `case.write_seeded`.
- `_seed_lib.person_name`: when a table's 20 given names are spent, compose from the people's syllables.
- `h.15.placement_audit` moved to M1 (`handlers/__init__.py`, 35 M1 handlers), registered in `h15.py`.
- Retired: `incident.bind_incident`, `SUBJECTS`, `INCIDENT` meta (`incident.subject`), the opening's binding call
  (I-148, P-067 fix 00b6534) and `name_known`'s read of it (views.py, 3 lines; DL-12-63 replaces it with I-149).
  Kept: `settle_who`, `STORY_ROLES`, `WHO`, `world_step`'s regexes (part B); `_people` is now an alias of
  `cast.base_pool` (world_step imports it).
- Outside the lane (each minimal): `session.opening` (the call site: `start_knowledge` replaces `bind_incident`; 3
  lines), `packet.scene_setting` (+7 lines: look, furniture, exits), `places.NPC_SEALED` (+`knowledge`),
  `views.name_known` (-3 lines), `engine/build/cards.json` (meta hash only), `tests/replay/games/offline_seed11.json`
  re-recorded (the world changed), `test_scheduler` (34 -> 35). `world_step.py` and `claims.py` untouched.
- Ledger rows I-130, I-145, I-148, I-149: engine notes appended. Validator: 0 ERROR / 0 WARN.

## Part-B entry points

See [contracts/api.md](contracts/api.md): `cast(state, role, *, scope, topic=None, asker=None, exclude=(),
faction=None, gate=True)`, `pointer_target(state, topic, *, scope, asker=None)`, `case_for_question(tx, role_words,
place, *, lead_target=None)`, `case_covering(state, role_words)`, `pointer(case, node_id=None, *, asked=None,
state=None)`, `mark_found(...)`, `validate_case`, `incident_line`, `start_knowledge`.

## Deferred

- The answer ladder (PR-12-10): per-holder delivery, "does not know", the pointer chain; until then `settle_who`
  answers a story role straight from the case (as the retired binding did) and other roles by casting.
- Pack facts as store facts with knowledge records (`how: seed`) and the tie written for both NPCs: kept in data.
- `KnowledgeRecorded.how` has no `common`; I-149 uses `recalled`.
- Node 2 ("the way on") is never marked found yet (no delivery path until part B); the audit keeps it live.
- In-play casting and on-demand cases draw from keyed `random.Random` streams (pure in seed + question), not the
  logged game RNG.
- Step 8's headline people stay named at setup (places.py); DL-12-63 would fold them into I-149.
