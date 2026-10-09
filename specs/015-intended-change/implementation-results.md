# Implementation results: spec 015 (typed intended change, S4)

Scope: R2-H report, "Engine checklist → Spec 015" items 1-6, spec 016 item 3 (lift rubric), problem 13 (knockout
line). Branch: the worktree branch (see the final commit). Engine API: `engine/CONVENTIONS.md`, last section.

## What was built (by checklist item)
1. **Reader schema** `change {kind, what, whom}`: 13 kinds from data (`none` first), slot ids constrained to scope ids
   plus the things people in scope hold plus reachable places. One change per beat, so two changes are two beats.
   **Laya log**: `<save>.changes.jsonl` beside the game file, one line per beat with its short inputs (restatement,
   intent, method, verb, ids in scope) and output (kind, slots). The kind decision has 13 options (≤ 20).
2. **OFFER** shows the change in plain words ("Taking: the coin purse, from Murzak Red-Hand") and a "Then: <act>" line
   for the beats queued after it (the playtest's "the offer only covers the grab").
3. **RECORD** (`engine/resolve/change.py`) applies on success by kind and delivered reach. take: reach 1 contested,
   2+ `holder` = actor. give, open, close, persuade_to (reach 1: a smaller part), hide. A failure applies nothing. A
   success at a cost applies the change after the cost. An unapplicable change (item not with the named person,
   nothing on record, crafting) writes nothing, and the RESULT says `Not applied: …`. An applied change shows as
   `Now: …`. The holder fact wins over narrated `carried_on` and kit `owner` (claims, codex inventory).
4. **T-12-18 fold**: a hold is `restrain`'s face. A Grapple typed `take` writes only wariness, not "restrained" (the
   playtest's input 20). `restrain` on any verb takes the Grapple rows. `free` clears the hold. move_to, harm and
   learn keep their writers (PR-06-4, 06.3.5, ch.06/07, 01.10).
5. **Must-name**: a `change` record item (applied or refused) per beat. The narrator is told it is done, or why not.
   The possession claim check reads the holder the change wrote. `_beat_for` also matches the change words.
6. **Tests** `tests/engine/test_intended_change.py` (8): each kind by reach (0, 1, 2, 3, 4); refusals; failure
   applies nothing; OFFER/RESULT/must-name; two changes → two beats with "Then:"; **the purse from the save**
   (`tests/fixtures/fighter_purse_turn8.db.gz`, the fighter save truncated before turn 8, with Haiku's own Reader
   answer plus the typed change: the coin purse's holder becomes the PC and the sheet lists it; the Laya log line is
   checked); a take-Grapple holds no one; lift attribute; the knockout line.
7. **Lift rubric** (DL-01-35): for a `take` change, or Exert/Force/Handle/Sneak with lift/carry/palm words, the words
   pick (heave → Might; palm, quick and quiet → Agility; carry far → Endurance). Otherwise the best computed odds win,
   and the OFFER lists the other two ("Another way: with Endurance (40%) · with Might (40%)").
8. **Knockout line**: `[STATUS] STAGGERED … Load 0/3; a blow adds 1 to 4 by how hard it lands.` The foe's RESULT shows
   `wound load 0 → 3` when a heavy blow lands.

## Gates
- **Full suite**: 1751 passed, 4 skipped. ruff clean (engine, evals, tests). pyright clean on every touched file;
  two pre-existing errors in touched files were fixed.
- **Reader golden (Haiku, Claude CLI)**: before 92.3% verb, 97.8% gate. First run with the change field: 92.3 / 93.4
  (gate −4.4: three plain questions became Talk beats). After a prompt fix ("a plain question stays SPEECH";
  "words pressing someone to tell" is `learn`, not `persuade_to`), a second run gave 90.1 / 95.6, and the final run
  **93.4% / 96.7%**, change kind **91.0%** (61/67). The runs show the noise (±2-3 points).
  **Held-out**: before 91.9 / 91.9; final **94.6% / 94.6%**, change kind **100%** (22/22). Change-kind labels were set
  by 01.2.7 before any model answer was read. The prompt was adjusted on golden-set misses, so the held-out number
  is the honest one. Answers: `evals/baselines/reader_{golden,heldout}_haiku_015*.jsonl`.
- **Scripted long-horizon**: 0 engine errors. First draft delivered as drafted 59.5%.
- **Live** (`evals/playtests/20261008-185505-claude-fighter.md`, Haiku, 15 turns): restrains landed (`detail.held`
  "in a grip", posture "held fast by you", RESULT `Now: Betan Deepbrook held fast by you.`); the `free` on letting go
  cleared both slots; moves landed (bands, then travel to the gate). No take or give was attempted, so neither was
  exercised live. Changes typed in the Laya log: restrain, learn ×3, move_to ×5, harm, persuade_to ×4, free, none.
  Player notes: the "Then:" line read the queued beat's intent as a promise ("he tells me which way the thieves
  went"); fixed: it now shows the act (method). The other complaints are outside this spec: unrolled foe
  counterblows (8 and 5 damage) with no odds shown, a scene jump to the gate with a stale foe hit, the healing salve
  not raising Vitality, a hidden check with no odds, and canned /fix replies.

## Retired or folded
- T-12-18's Grapple rows are now `restrain`'s face, not every Grapple's. Claims' private holder lookup was replaced
  by `change.holder_of`. The Reader prompt budget is 800 words (was 700) for the one new field.

## Deferred
- An item named only by an Oracle fact ("carries a coin purse": no item entity yet, the playtest's turn 2) cannot be
  taken: the RESULT says nothing on record by that name. Creating the item from the fact needs a rule.
- `make` (crafting, ch.08) is refused as not built. move_to's reach scaling stays PR-06-4's one band step.
- The OFFER shows the change and the queued acts, but not the restatement's typed tail (01.2.6 "…, to take the purse").
  The restatement is still the Reader's prose.
