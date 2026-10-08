# Implementation results: memory infrastructure (009 part A)

Branch `worktree-agent-abb25593185a07ed6`, base 9fc29e0. Offline model throughout; numbers measure the pipeline,
not the writing.

## Analyze (speckit-analyze) findings, fixed before implementing
- C1 (medium): FR-002's `details_used` had no test -> T007 covers a usage mark keeping a detail active.
- E1 (medium): SC-002 needs the spotlight on, but the aged probe ("I look around.") names nobody -> T024a: the
  harness also plays "I ask around about <absent NPC>." at each checkpoint.
- F1 (medium): "outside the verbatim window" was undefined -> read as "an ended scene" (spec Assumptions).
- Edge case on mapping seed `detail` text to a slot was unimplementable without a slot declaration -> deferred to
  part B (spec Edge Cases).

## What landed (see contracts/api.md, engine/CONVENTIONS.md "Memory")
- Store: `narrated` certainty, `persistence` on facts, `WorldState.details` index with `last_used`, `details_used`
  event, `engine/store/details.py` (writer, cap/archive computed on read, expiry, usage marks); `end_scene` stages
  expiry before `scene_ended`.
- Scene cards folded by the projection (`WorldState.scene_cards`); `store.rebuild()` regenerates them (tested).
  `cards_for`, `card_lines` (`engine/retrieve/episodes.py`); `recap_summary` lists cards since the last recap.
- Recency reads `scene_starts` (stored card starts): between scenes it now sees the scene before last (R2-A gap).
- Alias index (`alias_index`, `resolve_names`): PC-known names only, full names first, a lone given/family name only
  when unique and not inside a longer proper name. The journal uses it ("Joss Fenn" no longer lists Joss Dunmere
  and Pell Fenn; tested).
- `spotlight()` in the 12.2.4 order, K = 4, seals respected; rendered indented "as the character knows them" within
  `view_budget.spotlight`; up to 2 cards within `view_budget.scene_cards`.
- `view_for(role, state, ctx)`; `build_packet` uses it for every `WorldState` view (packet order and cached core
  unchanged). Leak test over every Narrator packet of a 12-turn seeded game.
- `promises()` + routing in `turn.oof_answer` / `_oof_shaped`.

## Gates
- Full suite: 1208 passed, 4 skipped, 0 failed (final run, after the re-record). ruff clean on touched files;
  pyright clean on touched files except a pre-existing `turn.py:496` optional-access error (not in my lines).
- `engine/build/cards.json` was stale at base (meta hash only): recompiled. Validator 0 ERROR / 0 WARN.
- New tests (`tests/engine/test_memory.py`, 11): slot writer (new / same / superseded-with-event / contradiction /
  refused), cap + archive + usage mark, expiry with history, cards regenerated from the log + `cards_for` order +
  recap, alias index, spotlight order/cap/seals, journal full-name match, per-role views, leak test, promises.

### `evals/longhorizon.py --mode aged` (seed 7, 300 scenes)
| | baseline (9fc29e0) | after |
|---|---|---|
| Narrator view tokens, scene 50 / 200 / 300 ("I look around.") | 1212 / 1284 / 1380 (+13.9%) | 1337 / 1473 / 1576 (+17.9%) |
| Narrator view, absent NPC named (spotlight + cards on) | n/a | 1380 / 1466 / 1553 (+12.5%; 200->300 +5.9%) |
| Reader view tokens at 300 | 1380 | 308 |
| Recall probes: precision / coverage | 0.46 / 0.67 | 1.00 / 1.00 |
| Promise probes: coverage | 0.00 | 1.00 |

**The ≤ 10% gate (scene 50 -> 300, spotlight on) is not met: +12.5%.** The spotlight and card sections are flat
(~70 tokens each at every checkpoint); the growth is the existing ranked-facts section filling its 500-token cap
(13 lines at scene 50, 24 at 300) and the `also here:` line filling its 80-token cap as residents gather, both
R2-A caps that stop growth (200 -> 300 is +5.9%). The "look" view grew more than before because cards (~70 tokens)
appear only once there are ended scenes about present people. Closing the gate means retuning the budget split
(OEQ-12-22), which is a rules decision, not done here.

### `--mode scripted` (seed 7, 300 lines)
307 turns, 252 narrated, **0 engine errors** (baseline: 7, the since-fixed name exhaustion), 0.0 contradictions /
100 narrated turns, novelty-4 0.30. Cached-prefix share: checker 0.94, director 0.85 (0.43), framer 0.90 (0.72),
narrator 0.91, reader 0.98 (0.96), world 0.93 (0.73). The scripted recall probe still scores 0 of 25 (its name
lookup predates this spec; not changed).

### Per-role sizes on the replay game (offline_seed11 recipe; median tokens)
| Role | packet before -> after | view before -> after |
|---|---|---|
| Reader | 14162 -> 13270 | 1274 -> 352 (-72%) |
| Framer | 11790 -> 11468 | 1444 -> 1134 (-21%) |
| Director | 9686 -> 9112 | 915 -> 318 (-65%) |
| Narrator | 16319 -> 16434 | 1274 -> 1270 |
| World | 14720 -> 14863 | 1082 -> 1225 (string view, unchanged code; the game path differs) |
| Checker, Interpret | unchanged | unchanged |

Replay game re-recorded (`py -3.12 -m tests.replay.record_games`).

## Changes outside the lane (each small)
- `engine/dm/turn.py`: import + 2 lines routing "what did I promise X?" out of fiction.
- `tests/e2e/driver.py::packet_sizes`: the growth check leaves out the RULE CARDS section. With per-role views the
  game path changed and the Director's 10 calls put a 40k-char conflict card set in the last quarter (1.35x); rule
  cards are capped at 12 by construction and vary with the situation, not the game's length. **Owner: confirm.**
- `rules/_process/issue-ledger.md`: row I-170b.

## Part B hookups (exact call sites, not edited: spec 006 / 007 files)
- `engine/dm/roles/world.py::world_view` line `lines = [render_view(scene_view(state))]` ->
  `view_for(Role.WORLD, state, view_ctx(...))` (then append the motives as now).
- `engine/dm/roles/checker.py::checker_ids` -> add `spotlight(state, message, last_delivery, beat)` ids.
- `engine/dm/mentions.py::_one`, reuse branch -> `write_detail(tx.state, tx.mint, eid, slot, value,
  because=<record ref>)` per implied property; `contradiction` -> the claim check.
- RECORD (T12, `engine/dm/narration.py`) -> `tx.add(used_event(fact_ids))` for details the delivery stated;
  `roles/narrator.py::_freshness` reads `last_used`.
- `engine/dm/roles/framer.py::framer_for` -> optionally pass `beat=beat` to `build_packet` (today `focus[0]`, the
  beat target, is used).
- `engine/dm/roles/reader.py::KNOW_QUESTION` could also accept promise questions (today `turn._oof_shaped` catches
  them when the Reader calls them FICTION_QUESTION).

## Deferred
- Salience from "cited in a record line or as a lever" (part B; part A uses source only).
- Seed `detail`/`appearance` text -> slot migration (needs part B's slot declaration).
- Code-written scene details from resolved beats (needs the per-verb outcome table, a rules item).
- The Reader's schema still offers scene fact ids for G4 while its view no longer lists facts (spec 007's
  computed gate).
- The aged ≤ 10% gate (budget split, OEQ-12-22).
