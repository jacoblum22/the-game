# Implementation results: the player feedback loop (spec 012)

Scope: R2-G engine checklist, Spec 012 items 1-9 (`rules/_process/reports/R2-G-report.md`). Spec-kit: spec, plan,
tasks, analyze (1 medium, 3 low findings, all fixed in plan/spec), implement.

## What the player sees

- Command: **`/fix <what is wrong>`** (also plain words: "that's wrong", "she already told me her name").
- Hint, verbatim (`pacing.yaml#feedback.hint`, `engine.dm.oof.FIX_HINT`): **`Something wrong? Type /fix and say
  what.`** Shown once per sitting after the first play screen (new game: when the story begins; resume: after the
  recap), as the last line of `?` (the glossary, with 14.2.7's one-line explanation; `? fix` shows it too), in
  `/help`, and as a NOTE after a fiction message that may also be a dispute (`reader.possible_dispute`).
- Answers are `[CORRECTION]` (upheld: fixed, taken back, or the record agrees) or `[FIX]` (the record stands, with
  the quoted turn or what the record holds). A take-back is offered as a CHOICE (accept forward / take it back).

## Review log

Every report: a dispute record in the corrections ledger (meta `corrections`, `type: dispute`) and a markdown block
in **`saves/<campaign>.disputes.md`**, beside the save file (`engine.dm.dispute.review_log_path(store)` =
`<save stem>.disputes.md`). Each block: id, turn, wall-clock time and game time, the player's words, category and
who located it (code or model), the passage, the evidence (fact ids with provenance: source kind, event seq, source
event, turn; the frame and its recomputation; the turns naming the subject; claim-log entries), the outcome
(upheld or not), writes and reverted seqs, and the answer as shown. Documented in `engine/CONVENTIONS.md` ("The
player feedback loop").

## Gates

- **Suite**: 1679 passed, 4 skipped (`py -3.12 -m pytest -q -p no:cacheprovider`, 241 s), the replay test included
  after re-recording. `ruff check .` clean. `pyright` on the touched files: 0 new errors (1 pre-existing at
  `engine/dm/turn.py:516`, `_cost_words`, untouched; `evals/playtest.py` keeps its 2 pre-existing errors).
- **Scenario tests** (`tests/engine/test_feedback_loop.py`, 12 tests, ~22 s): one real offline game (seed 11, the
  recorded game's Driver recipe, 30 turns of play), copied per test, with one planted error each:
  | Scenario | Outcome |
  |---|---|
  | remembered wrong (a generation value slipped to a narration write) | record error: pinned `source: correction` write; still `a grey coat`, pinned and in the narrator view after 20 more turns |
  | rule applied wrong (tier DC +5 bug), then travel to a new scene | recompute differs: ruling error, CHOICE; take back crosses the scene start (scene, place, time restored); redo frame DC 5 lower |
  | contradiction with a turn in the first scene (more than 50 turns back) | whole-transcript search quotes turn 2; store agrees; passage = the contradicting turn |
  | action misread (Reader patched to read another act; auto-committed) | taken back: writes reverted, roll void, "Declare again"; redo works |
  | player mistaken ("vitality should be N+6") | `[FIX]` quoting the turn that set it; nothing written |
  | incidental fiction, nothing on record ("cloak was green") | player's reading wins: pinned `green cloak` |
  | mechanical claim with no record ("I still have my silver lantern") | INV-9: what the record holds, logged, nothing written |
  | take-back blocked (session boundary; a Dying fact) | no rewind offered; corrected forward, with the reason |
  Plus: the possible-dispute hint, dispute stats and the review log. `tests/engine/test_dispute.py` (7 tests) updated
  to the new table and labels.
- **Discoverability** (`tests/engine/test_cli.py`): the hint equals `pacing.yaml#feedback.hint`, is printed once
  after the resumed game's recap, ends the `?` glossary, and `/fix the guard was dead` calls `Game.dispute`.
- **Harness**: `evals/longhorizon.py` reports "disputes per 100 narrated turns: all (upheld) (by category)" for the
  scripted run (baseline: 0.0 (upheld 0.0), no planted reports); `--fix-every N` plants reports (tested: 10 lines
  with every 4th a /fix, non-zero rate, 0 engine errors). `evals/playtest.py` persona: "If something the game says
  seems wrong, type /fix and say what, as a real player would."
- **Live check** (Claude CLI, Haiku as the engine model, owner's subscription, no API spend): 8 turns on a copy of
  the offline seed-11 game (3 play turns, 5 `/fix` reports; 25 model calls). Outcomes:
  | Report | Located by | Outcome |
  |---|---|---|
  | "Nedwin Greenbrook's coat was grey before, now you say blue" (planted slip) | code | **first run: wrong**, the value parsed as "grey before", answered `[FIX]` "never said"; parser fixed (stops at before/earlier/then/...), unit-tested; re-run: `[CORRECTION]` record error, pinned `a grey coat` (contradiction) |
  | "My vitality should be 20" | model (category) | `[FIX]` quoting turn 38's rest; nothing written |
  | "I still have my silver lantern" | code | `[FIX]` INV-9: nothing on record, lists the 11 carried items, logged |
  | "That's not what I meant, I only told a joke" (no actual misread: Haiku read it right) | model: misread | `[FIX]` "It stands: your words then match the reading" |
  | "Wait, you said earlier that the gate was open." (plain words, through `submit`) | the live Reader classified DISPUTE; model located | `[FIX]` INV-9 (a gate's state is mechanical; nothing on record); the answer now adds "and no turn says open" |
  Every report wrote a review-log block and a ledger record (`dsp.1`..`dsp.7`).

## Files touched

Mine: `engine/dm/dispute.py` (extended: locate, recompute, PR-12-11's table, take-backs, review log),
`engine/dm/turn.py` (`_dispute` wiring, the hint NOTE, a dispute CHOICE answer is OOF), `engine/dm/roles/reader.py`
(`possible_dispute` only), `engine/dm/roles/prompts/reader.md` (the DISPUTE line only), new
`engine/dm/roles/prompts/locator.md`, `engine/dm/packet.py` (pinned facts in `scene_view` / `render_view` /
`spot_lines`), `engine/dm/oof.py` (`FIX_HINT`, glossary line, `FIX` label), `engine/dm/schemas.py`
(`locator_schema`, the role's builder and default), `engine/store/events.py` / `projection.py` (`pinned`,
`source: correction`, `WritesReverted.take_back`), `engine/store/db.py` (the take-back revert), `engine/llm/base.py`
/ `gemini.py` / `offline.py` (`Role.LOCATOR`), `play/cli.py`, `evals/longhorizon.py` (+ baseline line),
`evals/playtest.py` (one persona line), `evals/gemini_smoke.py`, tests, `tests/replay/games/offline_seed11.json`
(re-recorded: R2-G's rule text and the Reader prompt line changed packets).

Spec 011's files: none edited. Call sites only: `engine.store.details.slot_of` (read), `engine.resolve.frame`
helpers (`attribute_value`, `competence`, `status`, `fact_usable`, `stored_dc_key`) and `engine.resolve.odds.odds`
(read, for the recomputation); meta `claim_log` is read when spec 011 writes it (absent = no entries).

## Deferred

- Make-whole refunds for spends before the current scene (12.3.4 step 3): the M1 "coarse" note stands.
- The in-fiction reconciliation form (12.3.4 step 2): dispute answers are always OOF.
- The `[J:flag]` "an established fact that changes the frame was omitted" is checked only for a fact the player
  names (`fact.N`); recompute covers DC, modifier, cited facts and odds; opposed DCs are not recomputed.
- Narration-error reliance CHOICEs stay within the scene (frames of earlier scenes are not in the projection);
  ruling errors and misreads use the widened take-back limit.
- The locator call also restates the player's claim (`subject`, `key`, `value`): reading the report, not judging
  it (disclosed in the spec's assumptions).
