# Feature Specification: A message is a plan of beats that survives pauses (spec 017; R4)

**Feature Branch**: worktree branch (spec dir `017-message-plan`)

**Created**: 2026-10-08

**Status**: Implemented

**Input**: `research_notes/Playtest round 2 solutions/ROUND4-ANALYSIS.md` R4. Rules implemented (look up with
`rules/tools/rq.py`; not restated, no rule text changed): 01.2.2 (beats, shapes `conditional` / `queued`), 01.2.3
(at most three a turn, the rest confirmed), 01.2.7 (one change per beat), 01.14.1 / 01.14.4 (a later beat after an
earlier result), 12.2.6 (pause points, defaults), PR-01-1, PR-12-1.

Evidence: `evals/playtests/20261008-192946-claude-fighter.md` (save `playtest-20261008-192946-fighter.db`) and
`evals/playtests/20261008-192926-claude-talker.md` (save `playtest-20261008-192926-talker.db`).

- Fighter input 19 (turn.4): "… If I find them, I walk straight up and demand they tell me their story." The Reader
  marked the Talk beat `conditional`; it became a "queued for the next declaration" note and was never resolved.
- Fighter input 26 (turn.11): "I sheathe my sword, then head for the reeve's cell and try to force my way in." The
  sheathe (free activity) and the walk (a step serving the Force) folded into one Force beat; the beat's line was
  cut from the restatement's head, "Sheathe the sword.", so the OFFER was titled that while it framed the door.
- Talker input 29 (turn.14): "… ask the other carters at the table if any of them have actually seen the barrels
  loaded. Then I head for the gate to find Ivas." The move resolved in T4, the NPC step (T5) ran at the gate, and the
  carters never answered.

## Root cause

1. Only "now" beats became `BeatPlan`s; `conditional` / `queued` beats and beats past the third were strings in a
   note. A pause stored only the "now" remainder, and a withdrawn beat dropped the rest.
2. A single kept beat took the restatement's first clause as its line, whatever beat that clause described.
3. SPEECH is answered by the NPC step (T5), which a pause skips and which runs after every beat, so speech said
   before a move out of the scene, or alongside a paused beat, had no one left (or no step) to answer it.

## Requirements

- **FR-001 Keep the plan.** Every Reader beat of a message is a `BeatPlan` (`when`: now / conditional / queued), in
  the player's order. A pause stores the rest of the plan; after it resolves the plan continues with the next beat.
- **FR-002 Re-check.** Before the next beat the pipeline asks the player in one line, "<why> Still go on to <act>?"
  (a `plan` pause, kind `offer`, choices `continue` / `withdraw`, default withdraw), instead of running or dropping
  it, when: three beats already resolved this turn (01.2.3); the PC is down; the beat's target was here and is now
  down or gone; the previous beat was withdrawn or refused; a conditional beat follows a beat that did not succeed
  (01.14.4), or a queued (Ready) beat is reached; the beat takes the PC to another place while speech said before it
  still waits for its answer. A Threshold (07.5) voids the rest: the last-chance menu is the question.
- **FR-003 Answer every part.** A `plan` pause does not skip T5 (it falls between beats; everything before it is
  resolved), so speech said before a move is answered where it was said. Any other pause carries the message's SPEECH
  parts in its detail; the turn that resolves or closes it adds them to its record, so T5 answers them.
- **FR-004 One beat per OFFER.** A beat's line is the restatement clause that matches the beat's own act (content
  word overlap with its method and intent; a tie to the first; with no shared word, or a one-clause restatement
  over several beats, the beat's intent). The OFFER's title, change, odds and "Then:" line (the plan's remaining
  acts) all come from that beat.

## Success criteria

- Fighter turn.11 from the real save: the OFFER is titled by the Force, not "Sheathe the sword"; the plan continues
  after the pause.
- Fighter turn.4: "demand their story" is resolved after the move's OFFER resolves.
- A plan stops and asks when the PC goes down mid-plan.
- Talker turn.14: the carters' question is answered in the inn before the move to the gate is asked about.
- Full suite passes; `evals/longhorizon.py --mode scripted` shows 0 engine errors; one live fighter run (Haiku, 15
  turns) reports no dropped parts and no mismatched OFFER titles.
