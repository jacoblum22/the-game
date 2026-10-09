# Feature spec 019: holistic narration (F1, plus F4's narration side)

**Input**: `rules/_process/reports/R2-J-report.md`, "Engine checklist per spec: Spec 019"; DL-12-101, DL-01-39,
DL-12-103; rules 12.3.1, 12.3.1a, 12.3.1b (items 1, 2.7, 4), 12.3.3, PR-12-2, 12.2.7, 12.14.12, 01.2.7 item 3.
**Evidence**: `research_notes/Playtest round 2 solutions/round6-investigation/I1-narration-text.md` (all of it);
ROUND6-PLAN.md F1 and F4; constitution Principle VIII.
**Owner direction**: whole over parts; check by measured precision; remove friction before adding procedure; code
must not author narrative truth. No clarify step: assumptions are recorded below.
**Parallel lane**: spec 020 owns the Reader, `packet.py`, `cards.py`, other role prompts and `pipeline.py`.

## User stories

### US1 - One passage, written as a person writes (P1; 12.3.1, DL-12-101)
The narrator returns one passage and a passage-level side list: `speech` (`{speaker, words, direct | reported}`),
`new` (typed new elements), `covers` (record handles). Code splits the passage into sentences only to locate a
failure and to cut; the model never writes sentence by sentence.
- **Accept**: the narrator schema has no `sentences`, `refs`, `about`, `atmosphere` or per-sentence `speaker`; a
  speech broken by its tag is one quote run and one `said` record.

### US2 - Only precise checks block, over the whole passage (P1; 12.3.1b, VIII.2)
The code scans (names, numerals, mechanics, sealed strings), the speech checks, the tiers and the precision checks run
over the whole passage. A check whose measured precision is below `min_precision` logs only.
- **Accept**: `season_words` and the outcome-word scan carry a measured `precision` in `pacing.yaml` and log; the
  pronoun check on speech is measured and stays off.

### US3 - At most one revision, which sees the whole draft (P1; 12.3.3, PR-12-2)
A blocking failure, an uncovered must-name line or unquoted speech sends the passage to one revision call that sees
the whole draft and each failure in words. After it, code cuts what still fails, quotes what is still unquoted, and
states each still-uncovered must-name item by its rendered line (the last resort, never an instruction). A cut alone
needs no revision.
- **Accept**: narrator calls per turn are at most 2; no call is a blind add; the revision message holds the whole
  draft and never a rendered line.

### US4 - Speech goes inside quote marks (P1; 12.3.1a item 2)
A direct speech whose words stand outside quote marks, or a first-person sentence in the narrator's voice, goes to
the revision; left so, code quotes the exact words.
- **Accept**: round-6 talker turn.16's three unquoted speech sentences are found and quoted.

### US5 - No answered-question bookkeeping (P1; 12.2.7 item 1)
The answered-question check (`screen._acknowledged`, word overlap, about 6% precise) and "every part answered"
bookkeeping are retired: speech and questions are not tracked part by part.
- **Accept**: the round-6 turns whose blind add-repairs stacked quotes (turn.2), duplicated an answer (turn.13) and
  echoed the player's statement (turn.14) pass as first drafts.

### US6 - Code stops telling the narrator what is true in its own words (P1; F4 narration side; 01.2.7 item 3)
No record line says "say it plainly; it is done". A `persuade_to` change reaches the narrator as who agreed, never as
"Agreed by X: <the player's goal>" (that line stays in RESULT). A change that was not applied is citable, not
must-name. The narrator prompt's "write around it" line about names and kinship is removed.
- **Accept**: turn.14's record line becomes "Sevella de Belac agrees to what was asked".

### US7 - The Checker's sampled audit reads the passage (P2; 12.3.1, 12.2.4)
The audit (1 turn in 10, logs only) reads the passage's numbered sentences, its side list in words, and the last
exchange as conversation.

## Assumptions (no clarify step)
- A1. Code still splits the passage into sentences (the existing quote-aware splitter) to locate failures and cuts;
  12.3.1 says a cut removes the offending sentence. This is code's bookkeeping, not atomised writing.
- A2. With several beats whose results differ, the outcome-word scan has no way to tie a sentence to its beat (no
  per-sentence refs), so it does not run; with one result it runs on the narrator's voice. Its measured precision
  (1 of 10) keeps it logging regardless.
- A3. Must-name coverage trusts the side list (`covers`), as 12.3.1a item 1 says (never failed in 106 turns).
- A4. Detail usage marks (12.14.11), which read cited `detail.*` fact ids, now come from a code scan: a stated
  detail value of someone the passage names.
- A5. The PC-echo blocking check I1 suggests is not added: the prompt now says "never restate the player's words",
  the blind add that caused the echo is gone, and the existing echo log keeps measuring it.
- A6. The `pc_agency` check compares quoted PC words with the player's message plus the parts a pause carried (I1
  §2 patch).
- A7. `said` records store each side-list speech whole, when its words were delivered (covered at 0.8).

## Out of scope
Answer lines, testimony and pronouns in packets (spec 021); the Reader, packets, cards and OFFER "Then:" (spec 020);
the lead line in every packet (020).

## Success criteria
- Full suite green; ruff and pyright clean on touched files; offline long-horizon (scripted) 0 engine errors.
- Live talker on Haiku (15 turns) against round-6 baselines (I1): stacked quotes, echoed player lines, duplicated
  answers, first draft delivered, revision rate, narrator calls per turn, cut or fallback turns.
