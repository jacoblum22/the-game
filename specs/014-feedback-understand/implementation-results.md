# Implementation results: the feedback loop, understand first, then verify (spec 014)

Scope: R2-H engine checklist "Spec 014" items 1-5 (`rules/_process/reports/R2-H-report.md`); PR-12-11, 12.3.6,
12.15.9, DL-12-94. Spec-kit: specify, plan, tasks, analyze (3 medium + 1 low finding; fixed in tasks/plan, the rules
data gap deferred to the rules lane), implement.

## What changed

- **Retired** (`engine/dm/dispute.py`): `_pins`, `_number`, `_NUMBER_WORDS`, `_named`, `_slot`, `_value_near`,
  `_claim_from`, `_QUOTED`, `_STOP`, `_candidates`, `_ask_locator`, `_relevant_exchange`, the "Which statement, and
  when?" and "Say which fact or roll is wrong … Logged." answers; `Role.LOCATOR`, `schemas.locator_schema`,
  `LOCATE_CATEGORIES`, `prompts/locator.md`. Code no longer reads a number or a name out of the report.
- **Understand** (new `engine/dm/understand.py`, `prompts/understand.md`, `Role.UNDERSTAND`): one call per report with
  the whole transcript (every turn oldest first, each committed roll under its turn), the people seen, the calendar;
  past `transcript_budget_tokens` (30000) the scene's turns plus search hits. Returns up to 3 complaints
  `{believes, happened, category (+ruling_question), turn, quote, subject, about, key, value}`.
- **Verify** (`dispute.locate` → `_claim`): the turn kept only if it is a transcript turn, the quote only if the turn
  holds it; `about/key/value` mapped to a quantity, a stored predicate, `carries`, `name`, `pronouns`, `season`.
- **Decide**, new rows: not found ("I can't find that; did you mean turn N, "…"?"); `ruling_question` / a roll →
  the frame recomputed and explained in plain words (what was rolled and as what, d20, degree, reach, what it wrote on
  record, its aim); an open OFFER → its cited facts with provenance; season (calendar) and pronouns (entity data) →
  "You're right: …; the narration slipped"; incidental continuity (`activity` added to the incidental slots; an NPC's
  unrecorded possession, who said or did what) → the player's reading wins as a pinned correction; the misread row
  reads the declaring turn's words (an OFFER's commit turn holds only "commit").
- **Deliver**: every answer opens `[LABEL] You're saying <believes>.`; each complaint gets its own answer and record
  (one CHOICE at most); no bare "Logged."; the "your face is turned face" garble is gone with the pinner.
- **Record**: dispute record and review-log block gain `believes` ("Understood:"); outcome `not_found`.

## Corpus (tests/fixtures/feedback_corpus: 8 real `/fix` lines + 3 round-3 short forms, on their saves)

| Run | Understood (category and turn) | Right outcome, plain answer |
|---|---|---|
| Before, spec 012 code, Haiku (`feedback_corpus_before_haiku.json`) | 5/11 | 1/11 |
| Before, offline stand-in | 2/11 | 1/11 |
| After, Haiku, first prompt and first routing (not kept) | 9/11 | 6/11 |
| After, Haiku, prompt v2 (misread wording), routing fixes (not kept) | 6/11 | 11/11 |
| **After, final prompt, Haiku** (`feedback_corpus_after_haiku.json`) | **11/11** | **11/11** |
| After, final prompt, Haiku, fresh re-run (`…_after_haiku_rerun.json`) | 11/11 | 11/11 |
| After, offline stand-in | 5/11 | 9/11 |

Restatements (OEQ-12-26, target 9 in 10): 11/11 judged right on the re-run. Category labels were noisy before the
prompt said a roll complaint is `rule_wrong`/`ruling_question` even when the text contradicts it, and "I succeeded but
didn't get X" is not `misread`; turns were right in every Haiku run. Outcomes do not depend on the label alone: code
routes by `about` too. `tests/engine/test_feedback_corpus.py` replays the recorded understanding offline (11 tests).

## Live check (Haiku via the Claude CLI, owner's subscription, no API spend)

`evals/feedback_live.py`: 4 turns on corpus saves (3 `/fix`, 1 plain words through the live Reader), 9 model calls;
run twice (8 turns total), the second after wording fixes (sentence cut on closing quotes, "as a grapple", "It's"
lower-cased). Replies verbatim in `evals/baselines/feedback_live_haiku.txt`.

## Gates

- Full suite: 1743 passed, 4 skipped (`py -3.12 -m pytest -q -p no:cacheprovider`, 228 s). `ruff check .` clean;
  `pyright` on the touched files: 0 errors.
- Spec 012's 12 scenario tests kept: same outcomes; assertions read the answer after its restatement; "That's wrong"
  is now `not_found` with a "did you mean" instead of a logged non-answer.
- `tests/replay/games/offline_seed11.json` re-recorded (the e2e dispute now calls `understand`).

## Files

Mine: `engine/dm/dispute.py`, new `engine/dm/understand.py`, new `engine/dm/roles/prompts/understand.md` (deleted
`locator.md`), `engine/llm/base.py`, `gemini.py`, `offline.py` (the role and its offline double), `engine/CONVENTIONS.md`,
`evals/feedback_corpus.py`, `evals/feedback_live.py`, `evals/gemini_smoke.py`, `evals/baselines/feedback_*`, tests and
fixtures (`tests/fixtures/feedback_corpus/`, `tests/engine/fixtures_gemini_schemas/understand.json`).
Spec 013's: `engine/dm/schemas.py`, the role's two map entries only (`locator_schema`/`LOCATE_CATEGORIES` deleted,
`BUILDERS`/`DEFAULTS[Role.UNDERSTAND]` call `understand.py`). `turn.py` untouched. `play/cli.py` and `oof.py` needed no
change (the garble came from the pinner; the dispute blocks are built in `dispute.py`).

## Deferred

- Typed intended change (spec 015): the purse explanation names the verb (grapple), the writes and the aim; it cannot
  yet say "reach 1, the purse is contested". The grapple reading of "lift his purse" is itself a Reader error the loop
  now exposes but does not fix.
- A stale lever in an open OFFER (fighter-19) is explained and logged, not struck and re-framed.
- Rules data (rules lane): `pacing.yaml#feedback.record` lacks `believes`, `#feedback.outcomes` lacks `not_found`.
- The CLI shows a bare prompt after a `/fix` answer with no open pause (talker note 19); not changed.
- Harm-rule complaints (fighter-31, Down at load 0/3) are explained from the record, not recomputed by the harm rules.
