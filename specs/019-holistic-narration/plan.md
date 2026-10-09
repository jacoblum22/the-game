# Plan: spec 019 (holistic narration)

**Spec**: [spec.md](spec.md). Python 3.12, existing modules only; no new engine files. Tests in
`tests/engine/test_holistic_narration.py` with a fixture cut from the real round-6 talker save
(`tests/fixtures/round6_narration.json`, by `extract_fixture.py`), plus the existing narration tests moved to the
passage shape. Measurements: `metrics.py` (I1's measures over saves), `measure_checks.py` (first-person and
passage-level outcome words), `evals/precision_audit.py` (season words; the pronoun check on speech).

## Design (smallest change per item)

1. **Schema and parsing** (`engine/dm/schemas.py`, `engine/audit/declare.py`): `narrator_schema` is
   `{passage, speech[{speaker, words, form}], new[], covers[]}`; the repair and "fiction" shapes go. `declare` gets
   `Speech`, `Passage`, `Sentence` (code's split, replaces `DeclaredSentence`), `parse_output -> Passage`,
   `sentences_of` (speaker from the side list, new elements on the sentence that names them), `coverage(passage)`,
   `unquoted`, `quote`, `first_person`.
2. **Narrator role** (`roles/narrator.py`, `prompts/narrator.md`): `Revision{draft, failed}` replaces `Repair`;
   `draft(revision=)` sends the same packet plus "A REVISION", the whole draft and what failed. `narrator_mode`
   goes. The prompt asks for one passage, one speech per quote run, quote marks on speech, never restating the
   player; "write around it" is removed.
3. **The loop** (`narration.py`): `_draft` (parse, split, judge, record a version) → at most
   `claim_check.max_revisions` revisions while `_Draft.failed()` is non-empty (a cut alone is not) → `_deliver`
   (cut what fails, quote what is unquoted, render uncovered must-name lines before the closing question, the
   prompt restored only if a cut removed it, the fallback when nothing survives). `_said` stores each side-list
   speech whole. `_mark_used` finds stated details by a code scan. Removed: `MAX_REDRAFTS`, `_max_redrafts`,
   `_unanswered`, `_polarity`, `_snapshot`, the add/replace bookkeeping.
4. **Checks** (`audit/claims.py`, `audit/screen.py`, `pacing.yaml`): the outcome-word scan becomes a precision check
   (`outcome_words`, judged against `passage_beat`); `season_words` and `outcome_words` get measured `precision`;
   `screen._acknowledged` goes; `max_redrafts` and `sentence_declaration` go from data.
5. **F4 narration side** (`handles.py`, `roles/narrator.py`): `AGREED` reads "Agreed by X:" so the narrator line is
   "X agrees to what was asked" and the rendered line "X agrees."; a refused change is not must-name; "say it plainly"
   wording leaves the learned and change lines.
6. **Checker** (`roles/checker.py`, `prompts/checker.md`, checker schema): numbered sentences of the delivered
   passage, its side list in words (`side_list_words`), the last exchange only; `unexpressed` is passage-level.
7. **Evals**: `narration_plug` judges passages and runs at most one revision; `replay_bench` counts revisions;
   `precision_audit` reads either draft shape and measures the pronoun check on speech.

## Outside the lane (one line each)
- `engine/llm/offline.py`: the offline narrator must answer the new schema (passage + side list; a revision drops
  the sentences it is told to remove) and write second person, which the new first-person check would flag.
- `evals/precision_audit.py`: the measuring tool the checklist's "measure" items need (both draft shapes; the
  speech pronoun measurement; the two new judged hits).
- Tests outside `tests/engine/test_holistic_narration.py`: existing tests of the retired shapes, moved to the passage.

## What is deleted or simplified
The sentence array and its per-sentence declarations; the narrow repair schema and loop (two rounds, add/replace,
`cited_before`, `replaced`); the "fiction" fallback shape; `_unanswered` and `screen._acknowledged`; per-sentence
`declaration_words` in the Checker; `max_redrafts` / `sentence_declaration` in data; the "say it plainly" record
wording; the change line handed to the narrator as done.

## Risks
- Haiku may still stack quotes from habit: measured live, not assumed.
- Side-list `words` that do not match the passage weaken speaker attribution (a quote with no speaker is logged,
  as before) and `said` (a speech not found in the delivered text is not stored).
