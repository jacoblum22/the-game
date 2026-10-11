# HANDOFF 032 (slice 2: P1 harness + labelled sets done; P2 runs beside it in another worktree)
Done (P1.1-P1.6 ticked): evals/npc_agency.py (arms pipeline, dm-tools; `--offline`), evals/h2h_score.py, heldout.yaml (24 items, body
hash in header, pinned by a test), tests/engine/test_spec032_cases.py (tables walked, 14 strict-xfail groups), tests/evals/test_spec032_harness.py,
fixture tests/fixtures/spec032_fighter_turns.json. Numbers and deviations: implementation-results-P1.md. Branch: this worktree's.
Before (Haiku, unfixed): npc_agency pushover dm-tools 2/20, pipeline 4/20 (gate 5%: both above); in-character refusals 10/10 vs 10/11; repeat caving
1/4 each. h2h saves: tokens-in ratio 0.32 and latency ratio 0.38 (C1/C2 already met); /fix 1 vs 5; fights 0 vs 2; prose-only refusals 2 vs 0;
hour/day moved 0 of 3 saves both arms; told rows 3 vs 27. Files: specs/032-dm-tools-mvp/{npc_agency_before.txt,h2h_before.txt}.
Next: P3 (needs P2) -> P4 -> P5; P6 after P3; P7 re-runs `npc_agency.py ab` both arms + `h2h_score.py` + heldout.yaml (only P7 reads it).
Traps for P3: (1) the DM calls `mood` in only 11/20 turns; the mood is also in the situation block, so do not make the tool mandatory.
(2) the leak check in npc_agency.py is a loose word overlap (1 false positive on "night/watch"); report it as an upper bound, or fix it with G9.
(3) P4 should log `screen.dm_tools.world.foe_turns` (a list) so h2h_score stops approximating foe turns from delivered text.
(4) flip the fixture asserts in test_fighter_save_prose_only_target_was_refused_and_no_fight_started in P3 (target accepted) and P4 (conflict_start).
(5) saves live in sibling worktrees (e.g. agent-ade910e9a063e6810/saves); a new live run writes to `saves/` of the worktree it runs in.
(6) npc_agency live: 4 threads x Haiku CLI, about 5 min per arm; Haiku is unseeded, so rerun once if a gate is within 1 reply of the line.
(7) ruff has 5 pre-existing errors in evals/orchestration and evals/precision_audit.py; pyright covers engine and play only.
