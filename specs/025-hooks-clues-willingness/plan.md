# Plan 025

## Trace (round-7 saves, before design)
- Fighter turn.2-4 (R7-I2 §1a): Magby holds the core placement "who makes the offer: Tobby Applefoot"; no step
  authored the job, pay or place. `world.cases` has no terms; the lead text is "… is hiring, and asks no questions".
- Talker turn.9 (§1b): `case_about` hit "sign" in "signed" against "a sign of the rite" and wrote a pointer line for a
  non-holder.
- Explorer turn.2-8 (§1c): Branine (core holder) asked about the refugees; `case_about` needed 2 incident words and got
  1, so no delivery. The refugees were no entity; the Director's `new_npc` cast a random labourer (Roswen); Roswen's
  refusal (d10 at Unfriendly) was voiced with a model redirect to Morga, the only other person present.
- Talker turn.10/11: willingness re-rolled per topic: unwilling, then fully willing one turn later.
- Fighter turn.15, talker turn.9-13: no deal price; the only coin moved was a regex hit on Framer prose.

## Design (files)
| Area | File | Change |
|---|---|---|
| Hook terms | `engine/gen/hooks.py` (new) | `terms_for(state)`: the incident's and each lead's terms from the store (keyed dice); `write_terms(tx)`: thread data `terms`, facts `terms.<field>` on the thread, knowledge records of those who would know; the refugees group entity |
| | `engine/gen/case.py` | `write_seeded` calls `write_terms`; `case_for_question` too; `about_line(case, node, placement)`; placement `about` honoured |
| | `engine/gen/_seed_steps.py` + `rules/_process/simulation/12-world-seed.py` | lead sentences as data; officer role "officer" (parity kept) |
| | `rules/data/world_seed.yaml` | `tbl.12.seed.document` `reward` rows coin-free (the amount is the typed term) `[revision: R2-K]` |
| Clue judgment | `engine/dm/answer.py` | `clue_case()` replaces `case_about`; `_route` and Recall use it |
| | `engine/dm/roles/clue.py` + `prompts/clue.md` (new) | `judge(ctx, knower, text, items)` -> node or None |
| | `engine/llm/base.py`, `schemas.py`, `offline.py`, `gemini.py`, `retrieve/cards.py` | the `CLUE` role entry (schema `{about: enum[none,1..4]}`, default none, offline stub, token cap, no cards) |
| Willingness | `engine/dm/answer.py` | `willingness()` held per scene (meta `answers.willingness`), events, refusal pointer |
| | `engine/dm/npc_layer.py` | P3; deal price on an accepted offer |
| Deal price | `engine/resolve/change.py` | `deal_price()`, `pay_deal()`; `pay()`'s regex retired (no-op shim, hand-off) |
| Guards | `engine/dm/roles/narrator.py` | "others have said on this" block after each speaker card |
| | `engine/dm/testimony.py` | `said_by_others()`; price claims settle from the band; a settled location of a person moves them |
| | `engine/world/places.py` | heard places reachable by an implicit passage; realised on arrival |
| | `engine/dm/roles/director.py`, `schemas.py` (director), `prompts/director.md` | `cast_described`: a description cast present |

## Retires
`case_about` (word-overlap case routing); `meet_npc(role=None)` for a stated purpose (a description is cast instead);
`change.price`'s regex on Framer prose; per-topic willingness re-rolls (the index no longer holds the band); the
greeting willingness line; the lead sentences and the "officer of {faction}" role string.

## Measurement
- `specs/025-hooks-clues-willingness/clue_eval.py`: precision and recall on `clue_set.yaml` (labelled first) on Haiku.
- `specs/025-hooks-clues-willingness/replay_r7.py`: the three round-7 gates on scratch copies.
