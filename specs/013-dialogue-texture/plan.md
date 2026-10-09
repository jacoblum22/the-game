# Implementation Plan: Dialogue and texture (spec 013)

**Spec**: [spec.md](spec.md) · **Scope**: R2-H report, "Engine checklist → Spec 013", items 1-9.

## Technical Context

Python 3.12, Pydantic v2, the existing engine (`engine/`), offline/scripted models for tests, Haiku via the Claude
CLI for the one live run. No new dependency. Constitution v2.0.0 Principle I: willingness, routing, settlement
routes and activity rolls are `[D]` code; words and the one claim statement are model judgments. Gate: pass.

## Design (one decision per checklist item; research folded in)

| # | Decision | Files |
|---|---|---|
| 1 | `answer.ask` = index memory → who/own name/casting → case route → **willingness** (no rungs). Delete `rungs_for`, `store_hit`, `pack_hit`, `ratify`, `point`, `_walk_on`, `_kept_at`, `_chain_logged`, `_pointer_said`, `_can_answer`, `_touches`, `ladder_owns`, `odds_for`, `public_local`, `_whereabouts`. `volunteer` keeps a private pack write. Delete `roles/proposer.py`, `prompts/proposer.md`, `proposer_schema`, `Role.PROPOSER` (replaced by `Role.TESTIMONY`). Remove `answer_ladder.repeat_pointer_limit`, `delivery.information.ladder_depth`. `world_step._look` loses ratify/point (a plain "nothing more"). turn.py keeps the "what does the person I'm talking to know" Oracle filter as a local helper (speech owns it now, not the ladder). | answer.py, world_step.py, turn.py, schemas.py, llm/base.py, llm/offline.py, rules data |
| 2 | `answer.willingness(ctx, npc, record, beats)` → `(band, reason)`: matching refusal tags (`npc_layer.event_tags` × `motive_tags`) → unwilling; a resolved Talk frame on the NPC → willing/unwilling by degree; certainty test (standing ≥ 0 and no hesitation) → willing; else `tbl.npc_action` by standing read through `willingness_by_row`. Record line = `NpcActionEntry(source=talk_outcome, source_ref=PR-12-10, tags=[willingness:<band>, question:<kind>|<topic>])`, must-name. | answer.py, world_step.py, npc_layer.py |
| 3 | `packet.speaker_card(state, npc, question, topic, about, rules)`: question + willingness, knowledge records and pack items on the topic (nothing sealed; pack slots are trade/local/tie only), role topics' gists, open threads (public news), `said_shown` (6) recent said + every one on the topic. Appended to the narrator's THIS MESSAGE by `narrator.draft` for each willingness line (it needs the record's willingness line; the view is built from state alone, so the card rides in the same narrator packet, after the record) [analyze: I1]. `_speech_line` rewritten: hearsay hedged, "I don't know" rare with a natural redirect, never contradict or repeat own said lines. | packet.py, narrator.py |
| 4 | New `engine/dm/testimony.py`: said records in meta `npc.said` `{id: said.N, speaker, turn, words, about, question, settled, fact}` (capped per speaker), index meta `answers.index` `(npc|kind|topic) → {willingness, reason, said: [ids]}`. `narration._said` writes them (question from the turn's willingness lines for that speaker). `narration._speech` adds `not_a_repeat` (content-word overlap with one of the speaker's said lines > `said_overlap`) → redraft. | testimony.py, narration.py |
| 5 | `testimony.settle_triggered(ctx, reader, rec)` in `turn._adjudicate` before plans: (a) Reader `rests_on` (schema field only when unsettled said ids are in view; Reader view shows them), or a beat target named in an unsettled said record whose name the PC knows only `how: heard`; (c) a Move/travel target place named only in testimony. One `Role.TESTIMONY` call `{subject, predicate, value}`; routes: consequential (touches a case subject/node words or a sealed fact) → true iff the case holds it (no clue), beyond ordinary (12.14.13's question: the claim names a hidden or valuable thing — a secret, weakness, hidden way, treasure, cure — or a place beyond the PC's settlement; ponytail: a word list) [analyze: U1] → Oracle at Likely, else accept. Writes fact `source: testimony|oracle` (events.py Literal gains `testimony`) or `wrong_about`. Triggers (b), (d) deferred (spec assumption). | testimony.py, turn.py, schemas.py, packet.py, reader.py (2 lines), events.py (1 word) |
| 6 | `handles.items`: activities are no longer items; NPC actions tagged `optional` are not must-name and not items. `record_text` renders an `OPTIONAL MATERIAL` section (no handles): activities/postures and optional reactions. `hide_stale`, `_set_aside`, `ActivityEntry.hidden`'s use and `_mark_used`'s activity-line branch retired. | handles.py, narrator.py, npc_layer.py, narration.py |
| 7 | `ensure_activities`: roll only for an NPC not in meta `npc.activity_rolled {scene, npcs}`; `role_key` = exact role, first word, or head noun, else `other` (the `tbl.npc_role` fuzzy fallback dropped: "of"/"the" matched any row → officers beating rugs). On engagement (`respond`) the activity slot is cleared (`write_detail(None, because=…)`) unless the response writes a new activity; never re-rolled that scene. A cleared slot has no current fact, so it is never a Framer lever candidate. | npc_layer.py |
| 8 | `addressed`: Talk targets, else the first NPC `named_in` ranks (address verb or first mention), else the one last spoken with — one addressee, not everyone named. `respond` responders = addressed ∪ beat targets ∪ concerned (present NPCs whose `event_tags` ∩ `event_tags.concerns` ≠ ∅; `concerns_self` = the words name them) ∪ fight. A concerned non-addressed NPC's response is tagged `optional` (a deed, no words). An addressed NPC with speech/question gets a willingness line (no talk wording). | npc_layer.py |
| 9 | Tests in `tests/engine/test_dialogue_texture.py`; delete or rewrite ladder tests (`test_answer.py`, `test_talk_cluster_c.py`, parts of `test_incident.py`, `test_npc_response_and_learning.py`). `evals/longhorizon.py` reports OEQ-12-25 counts (self-contradiction proxy, repeats, "I don't know", runarounds per 100 NPC lines). Replay re-recorded. | tests/, evals/longhorizon.py |

## Constitution Check (post-design)

Principle I holds: every decision that sets something in motion is code (`[D]`) or one typed judgment
(`[J:enum]` claim statement). INV-10: the speaker card filters seals and placements. Pass.

## Validation

See spec success criteria; commands in [quickstart.md](quickstart.md).
