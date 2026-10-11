# HANDOFF 032 (P1 + P2 done, merged on branch spec032-base)
Owner rulings, 2026-10-10 (they override spec.md, plan.md and tasks.md wherever those disagree; P3 updates the docs first):
- **Scene ends are the DM's call.** It uses an `end_scene` tool. Code only does the bookkeeping: time, per-scene resets and the new scene record. No code cut rules (no dead air or interrupt heuristics) and no Director call. Travel and time jumps still open a scene.
- **Moods are decided by the DM**, not rolled. The DM records them with the `mood` tool (memory, not a rule; it can change them). No mood roll and no ceiling grid. Retire T-12-19 use in dm-tools.
- **Pushover is observed, not gated.** Costly-ask grants and mood changes with no event are listed for the owner to read. Principle: fix only what is seen in play.
P2 (R+G): Role.DM (prompt engine/dm/roles/prompts/dm.md; `dm_tools.schema_for` is the one schema builder; offline `_dm`); `saved_engine()` in
game.py (the save's engine wins; missing = pipeline); `play new --engine`; recording offline_seed11_dmtools.json; S1-S12 tests. pytest 2071+4 skipped.
P1 (E): evals/npc_agency.py (pipeline, dm-tools; --offline), evals/h2h_score.py, heldout.yaml (24, hash pinned; only P7 reads it),
test_spec032_cases.py (14 strict-xfail groups by phase), test_spec032_harness.py. Before: h2h tokens 0.32x, latency 0.38x; /fix 1 vs 5; fights 0 vs 2;
prose-only refusals 2 vs 0; hour/day moved 0/3 both; told rows 3 vs 27. Files: npc_agency_before.txt, h2h_before.txt, implementation-results-P1/P2.md.
Next: P3 (lane T) -> P4 -> P5 (dm_tools.py shared, in order); P6 after P3; P7 last.
Traps: (1) new Role needs prompt .md, WORD_BUDGET, BUILDERS+DEFAULTS, gemini OUTPUT_TOKENS, cards GUIDANCE, offline heuristic, gemini fixture,
contract MESSAGES, test_llm_offline SCHEMAS, gemini_smoke. (2) DM packet/prompt change: re-record only the dm recording (`python -m tests.replay.record_games`).
(3) only `amount` is exempt from INV-3; any other number in the DM schema fails the contract. (4) Game._answer routes disputes to the pipeline (P6).
(5) `mood` was called in 11/20 turns; don't make tools mandatory. (6) flip the fighter fixture asserts in P3 (target accepted) and P4 (conflict_start).
(7) the npc_agency leak check is a loose overlap (upper bound). (8) use the Edit tool for strings with escapes; Python heredocs corrupt `\n`.
