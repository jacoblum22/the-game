# HANDOFF 033 P0 (guard census; lane `tests/guard/` plus this spec folder)
Done (T001-T006): `viii9.py` (DENY 71 entries, all `log`; WATCH census-only names; `Guard` patches functions and proxies
patterns/tables in every holder module, armed inside `dm_tools.play_turn/play_answer`; scope `shell` for `ending.is_retire`;
`only_from` for `conflict.start`<-`_fight`; env `VIII9_GUARD=log|raise`, JSONL via `jsonl=`); `census.py` (recorded game +
18-turn scripted probe; `python -m tests.guard.census table|reached|probe`); `scan.py` + `viii9_allow.py` + `reached.txt`
(static, 235 hits: 100 P, 55 F, 7 S, 73 pending); `test_viii9_static.py`, `test_viii9_runtime.py`; `reach-census.md`.
Gates: `pytest tests/guard` 83 passed 1 skipped (~19 s); ruff clean (run `ruff check --config "include=['tests/guard/**/*.py']"
tests/guard`: pyproject `include` omits tests/guard); pyright only "pytest unresolved" (env). Full suite: see commit msg/final report.
Nothing is xfail/skip-gated: tests pass because every entry is `log` and every hit is listed.
Traps for P6 and the phases:
1. A phase flips its DENY entries to `mode="raise"` and deletes its `pending:<phase>` rows in `viii9_allow.py`; stale rows FAIL
   the static test. Regenerate `reached.txt` (`census reached`) when a phase removes code. P6 sets `STRICT = True`.
2. Raised errors are swallowed by `dm_tools.tool`'s `except Exception`; the runtime test asserts `g.raised()`, not exceptions.
3. DENY is only for code a phase stops CALLING. `_fitted`, `lift_or_carry`, `reverses`, `plain_reading`, `certain_talk`,
   `looks_here`, `apply_change`, `typed_goal` stay called: guard them by the static rows or by their patterns only.
4. Not deniable, written down: A21 (`npc_leaves` default place, in `_change`), `_along` split, `scene_facts` id-overlap (S).
5. `retrieve.anchors._intent_hits` (D20) and `gen.npc.role_implies` (D33) are new finds; `certain_talk`/`looks_here` are not in plan R7.
6. Profile hook costs ~2x on the recorded game; hits are per access (thousands for `_STOP`); `classify_seed.py` is disposable.
