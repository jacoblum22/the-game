# Implementation results: spec 013 (dialogue and texture, S1 + S2)

Scope: R2-H report, "Engine checklist → Spec 013", items 1-9. Branch: the worktree branch (see the final commit).

## What was built (by checklist item)
1. **Retired**: R2-D's ladder as a speech source (`rungs_for`, `store_hit`, `pack_hit`, `ratify`, `point`,
   `_walk_on`, `_kept_at`, `_chain_logged`, `_pointer_said`, `_can_answer`, `_touches`, `ladder_owns`, `odds_for`,
   `public_local`, `_whereabouts`, the rung loop); `engine/dm/roles/proposer.py`, its prompt, `proposer_schema`,
   `Role.PROPOSER` (now `Role.TESTIMONY`); `pacing.yaml#answer_ladder.repeat_pointer_limit` and
   `social.yaml#delivery.information.ladder_depth` (validator 0 ERROR / 0 WARN). Kept: the case route, casting,
   `volunteer`. `turn.speech_owns` keeps the old filter for "does the person I talk to know X?".
2. **Willingness** (`answer.willingness`): refusal tags → talk frame → certainty test → `tbl.npc_action` band; one
   must-name line `{npc, question, willingness, reason}` per NPC per turn (identical lines collapse).
3. **Speaker card** (`packet.speaker_card`, in the narrator's message): knowledge records and own facts, pack items,
   role topics, open threads, said lines; nothing sealed, no motive, no case data. Narrator guidance rewritten.
4. **`said` records** (`engine/dm/testimony.py`, meta `npc.said`), filed under the asked-and-answered index;
   `not_a_repeat` in `narration._speech` (against the speaker's said lines and their earlier lines in the draft).
5. **PR-12-12**: triggers (a) Reader `rests_on` / a target known only from testimony, and (c) travel; one
   `Role.TESTIMONY` claim call; routes case / Oracle at Likely / accepted; fact `source: testimony` (new enum value)
   or `wrong_about`; settled once.
6. **Must-name diet**: activities and bystander reactions have no handle (OPTIONAL MATERIAL section);
   `hide_stale`, `_set_aside` and the `_mark_used` activity branch retired.
7. **Activities**: rolled once per scene (`npc.activity_rolled`), own role cell (the "of"/"the" fuzzy match that
   made guild officers beat rugs is gone), ended on engagement (slot cleared, so never a lever); an unchanged line is
   offered only when written that turn or at a scene opening.
8. **Who responds**: one addressee (Talk target, a name after a movement verb or opening the quote, a described
   person, else the last spoken with unless the words turn to someone no one here matches); responders = addressed
   ∪ targets ∪ concerned (`concerns_self` added); bystanders' rows are `optional`; speech gets willingness only.
9. **Tests**: `tests/engine/test_dialogue_texture.py` (15): said fed back, repeat redrafted, no code runaround,
   settlement once / target trigger / case route with no clue, consequential questions via the case, namesake not
   the case, diet, ended activity not a lever, own role cell, bystander silent unless concerned, addressee
   resolution, offline turns. Ladder tests retired or rewritten (test_answer, test_talk_cluster_c,
   test_npc_layer, test_npc_response_and_learning, test_check_less, test_turn_adjudication, test_incident).

## Gates
- Full suite: **1729 passed, 4 skipped** (baseline 1726 + replay before the change); replay re-recorded.
- ruff clean on touched files; pyright clean on touched files except one pre-existing error
  (`engine/dm/turn.py` `cost_terms`, `rules.get` on an Optional; untouched) and one pre-existing in
  `tests/engine/test_turn_adjudication.py:187`.
- Offline `evals/longhorizon.py --mode scripted` (seed 7, 300 lines): **0 engine errors**; contradictions
  **0.0** per 100 narrated turns; novelty-4 **0.68**; ask-twice 22/22; 88 willingness lines, 1 case pointer.
  (The offline narrator declares no speakers, so OEQ-12-25's NPC-line counts are 0 offline; `dialogue_lines` reads
  them from live turn records.) "Empty successes" 11/103 are Observe/Recall "nothing more" answers (never-empty
  was retired with the pointer).

## Live (talker persona, 15 turns, Haiku engine via the Claude CLI)
Counts by `scratchpad/stats.py` over the transcript (player notes excluded): "I don't know" turns; quoted NPC
lines repeated verbatim; near-repeat quote pairs (content overlap > 0.6).

| run | "I don't know" turns | verbatim repeats | near-repeat pairs | interjections |
|---|---|---|---|---|
| baseline re-run 20261008-145410 | 2/15 | 2 | 6 | Ysrion (back turned), Nibwen (2nd cup) |
| 170802 (b084308) | 0/14 | 0 | 3 | innkeeper answered a question put to "the old woman" |
| 173008 (fa87cf1) | 4/14 | 0 | 12 | none; but "someone at the Barrow of Calton would know" ×4 (case route) |
| 175000 (1495520) | 0/17 | 0 | 1 | Hoba answered questions put to people in a queue |

Each run exposed a bug that was then fixed and tested offline: (1) a described addressee fell back to the last
one spoken with; (2) a namesake (Kerda Coldbrook) matched Calda Coldbrook's case, so every NPC pointed at the
barrow, and an unchanged activity was offered every turn; (3) the words turning to someone no one present matches
still fell back to the last one spoken with, and several questions produced stacked, overlapping answers. The fix
for (3) is not yet verified live (no fourth run).

**Players' main complaints in the last run**: an NPC's several stacked, overlapping answers in one turn (fixed
after the run: one willingness line per NPC); Hoba "butting in" (fixed after the run); /fix replies (spec 014);
pronoun slips and "adult"/stat-block wording (spec 016); rolls for trivial acts and the OFFER's "grudging −2".

## Deferred
- PR-12-12 triggers (b) a lever/snag/term citing a `said` id and (d) a frame input reading the claim: the Framer's
  candidates (spec 016) and typed frame inputs (spec 015) own them; an unsettled said id is never a fact, so it
  cannot be cited as a lever.
- Paraphrased repeats within a turn ("I watched the sun" / "I was watching the light") pass `not_a_repeat`
  (content overlap below 0.6): measure with OEQ-12-25 live before tightening.
- A concerned bystander's optional row can still be a speech row ("asks the PC something"); the narrator may
  use or skip it.
