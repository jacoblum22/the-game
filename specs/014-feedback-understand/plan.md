# Plan: The feedback loop, understand first, then verify (spec 014)

**Spec**: [spec.md](spec.md). **Tasks**: [tasks.md](tasks.md). Items cite `R2-H-report.md` "Spec 014" (C1-C5).
Lean by request: no separate research/data-model/contracts files; decisions and the data shape are below.

## Constitution check
- I (code resolves, the model judges only what it must): the understanding call reads the report; code verifies and
  picks the row. The model never decides a write: a written correction needs a code-side row (store, provenance,
  incidental slot), INV-9 kept.
- IV (scope): no new subsystem. `dispute.py` loses its pinner; one new module (`engine/dm/understand.py`) and
  prompt. Lanes: `schemas.py` gets only the role's builder/default entries (two map lines; listed in the results).

## Design

- **Understand (C2)** `engine/dm/understand.py`:
  - `transcript(store, current, words, budget)`: every play turn oldest first, one block each: `turn.N | player:
    "…" | game: "…"` plus `rolled: frame.K "<restatement>" (verb) → <degree>, reach <r>` for a frame committed in
    it. Past `pacing.yaml#feedback.understand_call.transcript_budget_tokens` (chars/4): the current scene's turns
    plus the turns holding the report's words, newest first, until the budget.
  - `people(state, turns)`: the PC and every entity named in the delivered text, `id: name (pronouns)`; names as
    the PC knows them (`display_name`), sealed entities never.
  - Calendar line: `Now: <season>, <when_words>` (season 1-4 = spring..winter).
  - `understand_schema(turn_ids, subject_ids)`: `{complaints: [1..3 × {believes, happened, category, turn, quote,
    subject, about, key, value}]}`; `category` = `pacing.yaml#feedback.categories`; `turn` and `subject` enums plus
    `none`; `about` closed (spec assumptions).
  - `understand(ctx, text) -> list[dict]`: one `call_role(Role.UNDERSTAND, …)` per report; default = one complaint
    with `turn: none` (→ not found).
  - New `Role.UNDERSTAND` replaces `Role.LOCATOR` (`base.py`, `gemini.py` output cap, `offline.py` stand-in,
    `schemas.py` map entries, `prompts/understand.md`; `locator.md` deleted). The offline stand-in reads the
    report's words against the packet (names, numbers, key words): a test double, not engine logic.
- **Verify (C3)**, `dispute.py`: `locate(ctx, text) -> list[DisputedClaim]` turns each complaint into a claim: the
  turn kept only if it is a transcript turn; the quote only if the turn holds it (else the turn holding the quote);
  `about`/`key`/`value` → kind and key: quantity (the subject's quantity named by `key`), possession (`carries`),
  name, pronoun (`pronouns`), season (`season`), look/activity/fact (`detail.<slot_of(key)>` or a stored predicate),
  roll_or_outcome (ruling), action_reading (beat). Retired: `_pins`, `_number`, `_named`, `_value_near`, `_slot`,
  `_claim_from`, `_candidates`, `_ask_locator`; `default_identify` = `locate` with no model (one empty complaint).
- **Decide (C3)**, first row that fits, per complaint:
  1. no passage (no turn, no subject, no frame) → **not found**: "I can't find that; did you mean turn N, "…"?"
     (the turn sharing most words with the report and `believes`); outcome `not_found`.
  2. rule_wrong / ruling_question / roll_or_outcome → `_ruling`: the passage's committed frame, recomputed (spec
     012); differs → ruling error + CHOICE; same → **explain**: what was rolled (restatement, verb), the roll and
     degree, the reach, and what it changed in the record (`_changes`: shown facts, quantities, conditions the beat
     wrote); no committed frame but an open OFFER → its levers with their facts and provenance (INV-9: explained,
     logged for review); neither → quote the turn: nothing was rolled there.
  3. misread → `_misread` (spec 012).
  4. pronoun / season → the store's value (entity `pronouns`; the calendar): agrees with the player → "You're right:
     …; the narration slipped" (`correct`); else explain with the record.
  5. a stored key → `_fact` (spec 012's rows); an incidental slot (look slots + `activity`) whose earlier version
     held the player's value → corrected to it, pinned (continuity of incidental fiction).
  6. no key, incidental (`who_said_what`, `look_or_activity`, `other` with a subject or passage) → the player's
     reading wins: a pinned `correction.<n>` fact on the subject (or `world`) holding `believes` (`player_reading_wins`).
  7. otherwise → explain what the record holds; logged for review (INV-9).
- **Restate and deliver (C3, C4)**: `_done` puts "You're saying <believes>." first in the first block of each
  answer. Bare "Logged." tails removed; INV-9 answers keep "logged for review" after an explanation. A report with
  several complaints answers each (blocks in order, one record each); at most one CHOICE (later ones answer
  forward).
- **Record (C5)**: dispute record + review-log block gain `believes`; `located_by` = `model` | `caller`.
- **Corpus (C5)**: `tests/fixtures/feedback_corpus/` (corpus.json + 3 slim gzipped saves), `evals/feedback_corpus.py`
  (cuts a save back to the report's turn; scores understanding and outcome). Before scores committed from spec 012
  code (offline and Haiku); after likewise. `tests/engine/test_feedback_corpus.py`: offline, with the Haiku
  understanding replayed from the after run's cache, asserts the outcome per item (code's half, deterministic).
- **CLI (C4)**: `/fix` with the Reader fallback unchanged; nothing else needed (the garble came from the pinner).

## Files
Mine: `engine/dm/dispute.py`, new `engine/dm/understand.py`, new `engine/dm/roles/prompts/understand.md` (delete
`locator.md`), `engine/llm/base.py` / `offline.py` / `gemini.py` (the role), `evals/feedback_corpus.py`,
`evals/gemini_smoke.py` (role sample), `engine/CONVENTIONS.md` (the feedback-loop section), tests, fixtures.
Spec 013's: `engine/dm/schemas.py` (delete `locator_schema`/`LOCATE_CATEGORIES`; two map entries point to
`understand.py`). `turn.py` untouched (`_dispute_choice` re-uses the saved claim via `DisputedClaim(**saved)`).

## Not done (deferred)
- Typed intended change (spec 015): explanations name the verb, intent, reach and writes instead.
- A stale lever in an open OFFER is explained and logged, not re-framed.
- Rules data follow-up (rules lane): `pacing.yaml#feedback.record` lacks `believes` and `#feedback.outcomes` lacks
  `not_found` (12.3.6 item 6 and `answers` have them) [analyze I2].
