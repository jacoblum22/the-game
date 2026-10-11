# Implementation results, P1 (harness and labelled sets; lane E)

Base `8b238eb`. Edited only `evals/`, `tests/evals/`, `tests/engine/test_spec032_cases.py`, `tests/fixtures/`, `specs/032-dm-tools-mvp/`.

## Built
- `evals/npc_agency.py` (ported from `3e94efe`): arms `pipeline` (scripted Reader, Haiku Narrator) and `dm-tools` (real `dm_tools.play_turn`,
  Haiku is the DM role). `ceiling`/`judgment` arms and `ceiling_lines` dropped. Mood pinned the same way in both arms (held band
  `answers.willingness`), cost fixed by the cell. `--offline` runs both arms and the report on stand-ins (no model call). Baseline
  `evals/baselines/npc_agency_round8.json` (19 rows) ported unchanged.
- `evals/h2h_score.py`: headline table from saves (28 lines), read-only, no model call.
- `specs/032-dm-tools-mvp/heldout.yaml`: 24 items (6 prose-only, 6 fight, 6 said, 3 presence, 3 pronoun), `body_sha256` in the header,
  checked by a test. No model has seen it. P7 is the only phase that runs it.
- `tests/engine/test_spec032_cases.py`: the enumerated tables walked (verbs 15, DM change kinds 10, conditions 33, costs 9, cut triggers 7,
  modes 5, cells 12, question kinds 7, dispute kinds 4, incident kinds 8, adversaries 156, default behaviours 4), the held-out hash, the traced
  fighter facts from `tests/fixtures/spec032_fighter_turns.json`, and 14 `xfail(strict=True)` case groups (one per cases.md section, with the phase).
- `tests/evals/test_spec032_harness.py`: scorer over a tiny fixture save; both arms end to end offline; baseline shape.

## "Before" numbers (unfixed code, Haiku, one run each; Haiku is not seeded)
npc_agency, 20 replies per arm (`npc_agency_before.txt`, raw in `npc_agency_before/`):

| | dm-tools | pipeline |
|---|---|---|
| costly asks (real/big) granted in any form, observation only (owner ruling 2026-10-10: no pushover gate, no ceiling grid) | 6/12 | 5/12 |
| C6 in-character refusals | 10/10 | 10/11 |
| C6 repeat-ask caving | 1/4 | 1/4 |
| M1 grant open / guarded / closed | 4/4, 2/4, 0/4 | 4/4, 3/4, 0/4 |
| leaks (heuristic, one false positive in dm-tools) | 1/20 | 0/20 |

Each granted costly ask is listed with its cell and turn in `npc_agency_before.txt` (and by `report`) for the owner to read. The DM called `mood` in 11 of 20 turns.
`h2h_score` prints the same kind of observation: grants of real/big asks and mood changes, with turn ids (dm-tools saves: 3 costly grants, 0 mood changes; the pipeline
logs no `asks`, so it shows 0, which means unlogged, not none). The mood-change check cannot see events.

h2h_score on the 6 existing head-to-head saves (3 personas per arm; `h2h_before.txt`): tokens in per turn 14,868 vs 46,915 (ratio 0.32,
gate 0.6, already met); latency 13.6 s vs 35.9 s (ratio 0.38, gate 0.7, met); /fix reports 1 vs 5; fights 0 vs 2 with 0 vs 4 foe turns
(approximate for the pipeline); refused prose-only tool calls 2 vs 0; clock hour/day moved in 0 of 3 saves for both (the interval index moved in 2 of 3
for each); journal told rows 3 vs 27.

## Deviations and traps
- The spec says the pipeline arm is "the old arm"; it is the pipeline at `8b238eb` (no addressee/cost in the Reader schema, so the person present is the one asked).
- The held-out file cannot hold its own commit hash, so the header holds a hash of its body; P7 should record the commit hash too.
- `h2h_score` foe-turn count for pipeline saves is an approximation (a foe line in the delivered text) until P4 logs `screen.dm_tools.world.foe_turns`.
- The 14 xfail groups have an always-failing body: a phase that builds a group deletes its xfail row and writes real tests.
- Repo-wide `ruff check .` has 5 pre-existing errors in other `evals/` files; the files this phase touched are clean. `pyright` config covers `engine`/`play` only.
