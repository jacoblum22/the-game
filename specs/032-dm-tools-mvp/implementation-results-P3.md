# Implementation results, P3 (tools make the DM's words real; lane T)

Base `5895c3a` (P1+P2). Edited `engine/dm/dm_tools.py`, `engine/dm/roles/prompts/dm.md`, `engine/resolve/types.py` (`Beat.title`),
`engine/dm/oof.py` (`goal_line`), `engine/dm/npc_layer.py` (`ANIMAL`), `engine/llm/offline.py` (`fail_cost: none`), tests, and the dm replay recording.

## P3.1 Trace: every REFUSED in the head-to-head dm-tools saves
The saves (`saves/*.db`) are not in the worktree; the evidence is `tests/fixtures/spec032_fighter_turns.json` (the fighter save's turns) and P1's
`h2h_before.txt` (refused prose-only tool calls: dm-tools 2, pipeline 0; talker 0, explorer 0). So the table is the complete list for the three saves.

| save, turn | tool | reason | cause | P3 fix |
|---|---|---|---|---|
| fighter t9 | propose_roll strike, target "the beast in the clearing" | `no one or nothing on record` | `_id` returned the raw words; nothing made the beast | `_party` makes a creature (ANIMAL test) at the scene's place |
| fighter t12 | propose_roll strike, target "the pale beast" | same | same; also a second phrase for the same beast | `_party` reuses a creature here by its head noun ("beast") |

Both retries dropped `target`, so the roll proceeded with `target=None`: no entity, no `conflict_start` (fixture: `conflict_start_boundaries == 0`).
Turn 11 had no tool call at all (the dead end; P4's G7 sentence). Talker/explorer: 0 refusals, so nothing else to fix in the resolver for them.

## What was built
- `_party(ctx, t, raw, person=)`: id, then a name/alias/role match (the one here first, a creature by head noun), then a match elsewhere (the caller
  refuses it as not here: R20), else made when `person` or the words are a creature: named people and creatures through `mentions.write_mentions`,
  described people and groups through `social.cast_described`. A tool result tells the DM "New on record, here now: X (id)".
  Used by `propose_roll` target (person verbs: talk, strike, grapple, help), `reveal_clue`, `mood`, and `change` `who`/`to`.
- `ANIMAL` gained beast/creature/monster/brute/animal/bear/boar and a `head` group (`mentions._npc` and `is_animal` use it; pipeline replay byte-equal).
- `change kind=fight` (CHANGES is 11): `conflict.start`, no foe action, nothing done to the PC.
- One revision, then drop: a second REFUSED of the same tool and kind in a turn, or a refusal on the sixth tool call, goes to `screen.dm_tools.dropped`
  and the result says DROPPED. `condition_add` on the PC refused (E7); `cond.wound_*` and `cond.unconscious` (harm-owned, 5) refused both ways.
- `propose_roll`: target that is dead or gone / not here is refused with the reason (a downed foe can still be struck); `fail_cost` (none + 9 cost ids,
  all required in the schema like every field) is tried first by `code_framer`, then the verb's plain risk, then the rules' default; `goal` becomes
  `Beat.title`, and `goal_line` returns it (`exclude_if None`, so pipeline beats dump unchanged).
- `new_item` echoes a same-named item a person already holds (NOTE in the result; still created: the DM may mean a second one).

## Deviations
- A prose-only target is made only for creatures (any verb) or for person verbs (talk, strike, grapple, help). "The locked door" with `force` is still
  refused, with the way out in the text (leave `target` empty). A `fact` subject is made only for a creature; a person in a `fact` must exist or come from `new_npc`.
- "the smith" while a roster smith exists elsewhere resolves to that smith and is refused as not here (spine). The DM gets the id back to reason from.
- `mood` still rolls and gives the T-12-19 ceiling and `_asks` still logs violations: the 2026-10-10 ruling (DM decides moods) is not in P3's tasks; it is P4/P5's.
- P3.7 live Haiku fighter run NOT run: no `claude` CLI or API key in this worktree. Substitute: the fixture's turn 9 and 12 calls replayed on the new code
  (`test_r16`): ROLL OFFERED, 0 refusals, one beast entity. The 5-sample context replay is still to do on a machine with the API.
- E5 (sealed secrets per incident kind) and I12 (log-only) stay xfail, phase P5 (they are not P3's code).

## Numbers
- New tests: `tests/engine/test_spec032_p3.py` 29 (R1-R34, fight, O1-O12 with 9 cost cases, I1-I11, E1-E4/E6-E8, K1-K33). xfail groups 14 to 11 (R, O, I, K gone; E split into E5 and I12 for P5).
- Replay: pipeline recording unchanged (byte-equal); `offline_seed11_dmtools.json` re-recorded (prompt and schema changed).
- Gates: see HANDOFF.md.
