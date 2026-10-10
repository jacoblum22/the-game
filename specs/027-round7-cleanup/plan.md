# Plan 027

## Engine (one change per root)
| Req | Where | Change |
|---|---|---|
| R1 (B) | `engine/dm/roles/narrator.py` (`draft`) | Compute `shown`: `None` (everything) when the setting is given in full (scene opening, first opening, look-around); else the ids that came into the scene this turn (`entity_created` / `position_set` to the scene's place, in this turn's committed and staged events) plus the ids the player looks at or asks about (a look/ask word, then the name within a few words, by `resolve_names` or a thing's name word; the targets of Observe beats and `learn` goals). |
| R1 | `engine/dm/packet.py` | `view_ctx(..., shown=)` carries it; `view_for(NARRATOR)` drops, for entities not shown, a person's `detail` and a thing's `desc`/`look`/`detail`, and the description facts (`detail.*`, a thing's written words and narration-sourced facts). `scene_setting(full=False, shown=)` gives a shown person's look on their `present:` line. Nothing is stored. |
| R2 (C) | `engine/dm/dispute.py` (`_reframe`), `engine/resolve/pipeline.py` (`PipelineEnv.framer_note`, `_frame`), `engine/dm/roles/prompts/fixer.md` | `value` on a `reframe` is the note: one line, ≤ 200 chars; refused (not passed) when it states odds, a number or a roll; passed to the Framer as "a note from the review of the player's report (context, never a fact or odds)". |
| R3 (H1) | `engine/dm/response.py` (`Response.text`) | An `[OFFER — auto]` block and the RESULT right after it lead the passage. |
| H2 | `engine/text/render.py` (`slug_words`) | Drop numeric index segments (`furniture.0` → furniture); `codex._known`'s `what` uses `slug_words`. |
| H3 | `engine/dm/oof.py` (`_fact_line`) | The shared `fact_sentence`; with no sentence, the plain "something already settled stands against it". |
| H4 | `engine/gen/_seed_steps.py`, `rules/_process/simulation/12-world-seed.py` | The gate building: "the gate" (or the feature when it is a gate, "the hill gate"); its description keeps the feature ("the gate, by the ford"). |
| H5 | `engine/resolve/pipeline.py`, `engine/resolve/change.py`, the test that called it | Remove both calls and `pay`. |
| H6 | `engine/dm/roles/prompts/narrator.md` | Narrow the line (R7-R1). |
| H7 | `engine/dm/dispute.py` | `CASE_PREDICATES` without `knows_`. |
| H8 | `engine/retrieve/scene.py` (`READING`), `engine/audit/declare.py` (`SceneIndex.of(said=)`), `engine/dm/narration.py` | READING without "they", the noun phrase up to two words; the player's own numbers allowed for the PC. |

## Rules (rules-worker, R2-K tag)
DL-12-122 (B; 12.14.11, 12.2.4 Narrator row, 12.11.3; revisit lines on DL-12-99 and DL-12-113), DL-01-46 confirmed
(quote), DL-12-118 confirmed + "Revisit if", DL-12-123 + one line in PR-12-11 (C), DL-12-124 (12.15.2: auto OFFER and
RESULT above the passage), DL-12-125 (12.16.9: the gate's name), WE-01-2, WE-12-11, `resolution.yaml#reach_flags`
tie-break per 01.6.10; ledger I-220..I-226; re-assemble appendix, anchors; cards compiled last; validator 0/0.

## Gates
Full suite; replay re-recorded; ruff and pyright on touched files; validator 0/0; longhorizon scripted 0 engine
errors; cases C1-C28; packet check (`specs/027-round7-cleanup/looks_check.py`).
