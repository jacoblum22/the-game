# Spec 021: implementation results

Branch `worktree-agent-ac7f90ec762e04c01`, from `milestone-1-playable` (cb5e20d: R2-J, 019 and 020 merged). Haiku for
every engine call; the playtest player on Sonnet (the harness default). No Gemini, no API spend.

## Trace first (read-only, the round-6 saves)
All four I2 causes confirmed before any change (table in `spec.md`): the refusal said.5 → fact.103 → Framer snag
(233000 t8, t12, t14); Lilett's card without the bond (232941 t8); `cast_who` → "no one you know" as a MUST line
(232941 t6, 192926 t10); the found node re-delivered (232941 t5); and the card leaks (Sevella's `correction.1`,
Belby's `agreed`).

## Gates

| Gate | Result |
|---|---|
| Full suite | **1802 passed, 4 skipped, 0 failed** (replay re-recorded; `milestone-1-playable` unchanged at cb5e20d at finish, so no merge was needed) |
| ruff / pyright (touched engine and test files) | clean / 0 new errors (one pre-existing pyright error at `turn.py:553`, untouched) |
| Rules validator | 0 ERROR / 0 WARN |
| Long-horizon scripted, 300 lines, seed 7 | **0 engine errors**; same 381 turns / 308 narrated; `evals/baselines/longhorizon_021.txt` |
| Tests from the real saves (`tests/engine/test_testimony_answers.py`, 3 cut fixtures) | refusal → nothing written (even Haiku's recorded claim); the threat settles nothing; fact.99-102 (held, posture, manner, `said.*`) out of the Framer enum; Lilett's card "(she/her; your friend)"; the gate question writes no "no one you know"; the found way-on is not re-delivered; Sevella's / Belby's cards show no correction or `agreed` |

### Measured on the six round-6 saves (`measure.py`; `measure-output*.txt`)

| Measure | Before | After |
|---|---|---|
| Settlement per offered turn (offline re-run of the triggers over the recorded Reader beats) | 27/45 (60%; I2: 64%) | **6/45 (13%)**: 4 travel targets, 2 premises |
| Claims written (31 recorded testimony calls; after = the new call on Haiku, same record and state) | 31/31 | 23/31 (4 refusal, 2 question, 1 intention, 1 none) |
| Claims that lose their subject (`world`) | 21/31 (I2: 17/26 facts) | **7/23**, each a group or description no entity carries (strangers, the refugees ×2, the cold, the sky, someone, the locked-up man) |
| Garbled claims (an id in the claim, a question, a flipped pronoun) | 4/31 (I2: 4/30) | **0/23** |
| Refusals or intentions stored as facts | 4 | **0** (the model's `kind`; the `_OWN_WILL` guard never had to fire) |
| Absent people named on a speaker card, pronouns in the packet | 2/93 | **71/93** (new card alone) |
| Bonded NPC's card shows the bond | 1/7 | **7/7** |
| Pronoun flips on checkable speech lines (`analyze_live.py`) | 232941: 4/5; 192926: 0/1 (I2: 5/9) | live: **0/6** |

### Live: talker, Haiku engine, Sonnet player, 15 turns
`evals/playtests/20261009-154128-claude-talker.md`; save `saves/playtest-20261009-154128-talker.db`;
`live-output.txt` (same analyzer on the two round-6 talker saves for comparison).

| | round-6 talker 232941 | **021 live** |
|---|---|---|
| "Wall"/dodge-pattern speech lines | 6/40 | **1/26** ("The Wolves are not mine to weigh. Ask the ale-sellers": a redirect, in character) |
| "No one you know" facts / lines | 1 | **0** |
| Refusals or intentions stored as facts | 1 refusal-shaped fact (+ 3 in 233000) | **0** (0 settlements: the player never travelled on testimony) |
| Pronoun flips on checkable lines | 4/5 | **0/6** |
| Found-clue repeats on MUST lines | 3 | **0** |

The player's two `/fix` reports (inputs 26, 31) were both "Valine says something unrelated" (the Weeping Grassland
lane; the Perwin meetings). Traced: both lines are her speaker card's seeded `knows:` items, voiced because a
willingness MUST line ("Valine acts: replies, willingly") was written when the PC only greeted her (turn 10) and only
thanked her (turn 15); the card says "answer from this first", so with no question she recited it. Not introduced
here (the card's pack lines and `_speech_answers` predate 021); hand-off below. The same card showed
`knows: Valine Varault is at the inn and can be found there False` (an Oracle yes/no fact about her): fixed here, the
card now skips yes/no facts.

## What was retired, and what supersedes it
- **`rests_on` settlement** (the Reader field, its schema enum, `SchemaContext.said_ids`, the Reader packet's
  TESTIMONY block, `testimony.open_records`): superseded by `testimony.triggered(state, beats)`: a beat target known
  only from testimony (travel, a target), or a beat premise (`assertion`) restating a record.
- **`settle()` accepting a refusal**: the claim call returns `kind`; anything but `claim` writes nothing
  (`settled: "none"`); a speaker-subject predicate of their own will is refused by code too.
- **The slugged `said.<predicate value>` predicate and the id view**: the claim's own predicate; names and identity
  lines, never ids; the exchange the words were said in. Attribution (`said_by` / `said_turn`) is the `said` record
  (`said_for`), and the odds line reads "<Speaker> said: …".
- **"No one you know"** (`answer.NO_ONE`, the `who_is_*` fact, the MUST line, the DM-side Oracle line): a failed cast
  writes nothing; the NPC answers within their willingness.
- **Re-delivered found clues**: `_from_case` returns None for a found node (the PC recalling it on the DM side is
  unchanged).
- **The speaker card's "knows:" leaks**: `agreed`, `correction.*`, pinned facts and `source: correction | testimony`
  are skipped; the card's header carries the speaker's pronouns and the PC's bond; the people it names get identity
  lines.
- **Scene labels as Framer candidates**: `schemas.lever_candidate` drops `detail.activity|posture|held|manner`,
  pre-021 `said.*` facts and `source: correction` from the lever/snag enum.
- **`first_interaction` ignoring stance**: `helps` never below Neutral, `hinders` never above Wary (DL-12-107).
- **"Then:" from `method` on a re-shown OFFER**: `oof.goal_line` (as `pipeline._then`).
- **`_SELF` matching "they"**: "who are they?" no longer answers with the knower's own name.

## Lane exceptions (all minimal)
- `engine/dm/schemas.py`: the testimony schema's `kind`, `rests_on` and `said_ids` removed, `lever_candidate` (the
  Framer's enum lives here, not in `engine/resolve/`; nothing in `engine/resolve/` changed).
- `engine/dm/roles/reader.py`: the `rests_on` field. `engine/dm/packet.py`: the Reader TESTIMONY block (deleted)
  and `speaker_card` / `_card_fact`. `engine/dm/turn.py`: one guard (no Oracle line for a failed cast).
  `engine/dm/oof.py`: `fact_short`'s testimony branch. `engine/llm/offline.py`: the offline testimony stub.
- `rules/data/social.yaml#cast.empty_pool.who_is_role`: still said "'no one you know', written as a fact"; now
  matches DL-12-103, tagged `[revision: R2-J]`. `engine/gen/cast.py`: docstring only.

## Anti-pattern check (handoff §3.3)
- *Code authoring narrative truth*: refusals no longer facts; no "no one you know"; no re-delivered clue; no complaint
  or goal text as "knows:"; scene labels never snags. Still present, out of lane: `volunteer`'s "lets slip where they
  stand" line and `change.py`'s `agreed` text (022's file; the card no longer shows it).
- *Over-triggering*: settlement 60% → 13% of offered turns.
- *Low-precision checks that block*: `_OWN_WILL` blocks a write only for a speaker-subject predicate that starts with
  will / won't / refuses…; it fired 0 times in 31 Haiku claims (the model's `kind` did the work), so it is a
  backstop, not a filter.
- *Blind model calls*: the claim call now sees the exchange, the speaker and identity lines.
- *Wrong context*: pronouns and bonds on the speaker card for the speaker and everyone it names.

## Hand-off notes
- `rules/00-architecture.md` (00.11.1, line ~1514) still says casting may answer "no one you know"; a rules wave
  should align it with DL-12-103 (not edited here: rules prose is the rules worker's).
- PR-12-12 step 4 says the fact carries `said_by` / `said_turn`; the engine keeps them on the `said` record (A1). If
  the owner wants them on the fact itself, that is an event-schema field (store migration).
- **Next cause to fix (live 021)**: a willingness MUST line is written for an addressed NPC when the PC asked nothing
  (a greeting, a thanks), and the narrator then voices the card's seeded items as non-sequiturs. Likely fix: no
  willingness line without a question part (`world_step._speech_answers` / `addressed`), and the card's header says
  the items are background, not things to recite.
- Still open from I2: the kin question routed to the case ("Is Rrakaa kin of yours?" → the way on); the `agreed`
  fact's content (`change.py`, spec 022's lane); the narrator-voice/speech pronoun check that strips quotes.
