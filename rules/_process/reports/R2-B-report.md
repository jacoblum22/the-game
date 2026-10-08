# R2-B report: narration contract and NPC layer

Revision R2-B (rules half of spec 006). Worktree reset to milestone-1-playable (16b92c2).

## Progress
- Setup: worktree reset to 16b92c2; baseline validator 0 ERROR / 0 WARN. Read synthesis, B P1/P3/P5/§4, C §4.1/§4.4/§6.
- Step 1: 12.3.1 (two claim sources; continuing activity is `position`), new 12.3.1a (sentence coverage), 12.3.2 (`undetermined` split by tier; support/contradiction scope, D5), 12.3.3 (per-sentence repair; plain fallback as its extreme case) edited.
- Step 2: 12.2.9 step 2 (default layer; addressed NPC always answers), 12.2.10 (stated values cite the view id), 12.6.1 (proposing is not choosing; T1a carve-out), new 12.11.9 (default NPC layer), 12.14.12 (FICTION_QUESTION answer is must-name; handles; coverage), 12.14.13 (tier table, closed `element_kind`), PR-12-1 T5/T7/T8/T9, PR-12-2 (declarations, coverage, per-sentence repair), 12.2.7 flag 1 evidence (coverage), T-12-17 index row; ch.00: 00.6.6 (undetermined split), PR-00-7 steps 1-3.
- Step 3 (data): `oracles.yaml` gains `tbl.npc_activity` (21 roles from `tbl.npc_role` incl. `other` x 4 watches x 3 activities, d6 pairs) and `tbl.npc_practice` (lookup; fight, trade, greeting, conversation, crowd, work; allowed `tbl.npc_action` rows + gist per row; row 5 legal everywhere, row 1 legal at Hostile). Hand-authored file (no generator; `12-world-seed.py` and `13-gen_region.py` only read it). `pacing.yaml#claim_check`: `on_exhausted: cut_and_render`, `sentence_declaration`, `element_tiers`. Parse and consistency check run inline (every cell has 3 entries; responses keys equal action_rows).
- Step 4 (consistency): 12.12.4 review flag (rendered line), ch.10 PR step 4 (consequential property only).
- Step 5 (DL): DL-12-40 (D1 tiers), DL-12-41 (declarations, coverage, per-sentence repair), DL-12-42 (D5, assumed, owner to confirm), DL-12-43 (default NPC layer), DL-12-44 (D2, I-153; procedure deferred to R2-D), DL-15-37 (D4, PR-15-6; procedure deferred to R2-D). Renumbered from 39-43 on the orchestrator's note (DL-12-39 taken by R2-A2; R2-B owns DL-12-40..49).
- Step 6 (ledger): resolved I-128, I-129, I-131, I-132, I-133, I-135, I-136, I-150. I-140 stays open with (a) resolved; I-153 stays open with D2 recorded.
- Close-out: appendix re-assembled (`integration-assemble-appendix.py`), anchors recompiled (129, 0 errors, 0 warnings), validator 0 ERROR / 0 WARN.

## For the engine spec (006)
- `engine/build/cards.json` is stale after these rule edits (`tests/engine/test_build.py::test_committed_cards_are_current` fails): run `python engine/build/compile_cards.py`. Not run here (engine/ is out of scope).
- T-12-1 (the always-loaded checklist, mirrored in `pacing.yaml#packet.core_checklist`) was left unchanged to avoid churning the cached prefix and replay fixtures; its T8 "roll what is unsettled" should become "ask the Oracle only for a consequential unsettled property" when the narrator prompt changes.
- Narrator schema: `sentences[]` of {text, refs (enum of record handles R1.. + view fact ids), about, new [{..., element_kind}], atmosphere}. Coverage: must-name items (12.14.12, now incl. the FICTION_QUESTION answer) each need a handle in `record_text`.
- Repair: per-sentence; `rule_conflict` ruling only when a rendered line was used; scene header in fallback only when a scene opened.
- Support scope (DL-12-42): support = packet + record; contradiction = whole store; off-packet support passes and is logged as a retrieval miss.
- NPC layer: roll `tbl.npc_activity` at scene entry and write as scene-state `activity` (overwrite); pick practice by `tbl.npc_practice.select_order`; clamp `tbl.npc_action` row to the practice's `action_rows` (nearest, toward 5); addressed NPC always answers; roll voice for a walk-on on first answer. The want/refusal match keeps 12.2.9's `[J:flag]` (no tags on wants or refusals yet).
- Not written (R2-D): the answering procedure (PR-12-x), the reduced case builder text, 12.2.9's "answer" source, 12.13.4, 00.12.7's proposal form.
