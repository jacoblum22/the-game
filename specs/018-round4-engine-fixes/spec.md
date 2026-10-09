# Feature spec 018: the round-4 engine fixes

**Input**: `rules/_process/reports/R2-I-report.md`, "Engine checklist: spec 018 (items 1-6)"; DL-12-96..100, DL-01-36;
`research_notes/Playtest round 2 solutions/ROUND4-ANALYSIS.md` (R1, R2, R3, R5, R6 setting, patches).
**Owner direction**: remove friction, don't add procedure; prefer deleting code to adding it. No clarify step.
**Parallel lane**: spec 017 owns the message plan (pipeline planning/queue/resume, turn pause/resume, the OFFER
title and "Then:" line). This spec touches `pipeline.py` and `oof.py` only in small separate functions.

## User stories

### US1 - NPCs speak plainly (P1; R1, DL-12-96)
The speaker card and the narrator's speech line stop asking for "hearsay or a guess, hedged". Beyond the card, an NPC
answers plainly with ordinary confidence; a hedge is only for a cautious or gossipy character. `guarded` keeps "a part
of it, short", without "hedged".
- **Accept**: no packet line the engine builds asks for hedging; the speaker card says "plainly".

### US2 - A target can be a description (P1; R2, DL-12-97)
"Persuade the refugees to show themselves" applies on success. The Reader may give a short `description` for a
change's person or thing that has no id. A change on a description writes a scene fact about it (on the scene's
place, cleared at scene end) and the result line names it ("Agreed by the refugees: ..."). If the description names
exactly one person in scope, that person is the slot. No group entity, no spokesperson.
- **Accept**: the fighter save's turn 7 persuade (with a description) applies: no "no one named to persuade".

### US3 - Approach, look, travel without friction (P1; R3, DL-12-98)
Outside a conflict, a Move toward a person or thing present is one beat, no roll unless a party would act on a
failure, and ends beside it (`band.engaged`, worded "beside"). Band steps are kept for a conflict and for a rolled
partial (reach 1). A Move whose place is the place the PC is already in is a look: no roll, no "still in X" line.
Travel to another place frames the arrival: the turn whose record starts a scene narrates with purpose
`scene_open`, and the scene line is must-name and comes after the beats that led there.
- **Accept**: replaying the fighter save's turns 4-7 gives one approach (no "a few strides" twice, no "still in");
  the travel turn narrates as a scene opening.

### US4 - Already true is certain; no roll with nothing to deliver (P1; R5, DL-01-36)
Before framing, a change already true in the store (the person already agreed to the same act, the actor already
holds the item, the thing already open/closed, the actor already beside the target) is necessity `trivial`: no roll,
no OFFER, and the record says it is already so. A change that needs a person or thing and has no id, no target and no
description is asked about ("who?") before framing, never rolled.
- **Accept**: the talker save's turn 5 "persuade Ivas" after her `agreed` fact for the same act gives no roll and no
  OFFER.

### US5 - Setting once (P2; DL-12-99)
The place's look, furniture and description reach the narrator when a scene opens (purpose `scene_open` or
`opening`, or the first narrated turn of a scene), then not again; later turns carry a one-line "already described"
note instead, unless the player looks around. People present, exits and time stay every turn (pronouns, P-056).
- **Accept**: five turns in one place carry the `- look:` line in the narrator packet once.

### US6 - Speech patches (P2; DL-12-100)
1. NPC speech never opens by reciting the speaker's own name or title unless asked (prompt line).
2. PC words inside a speech attribution ("'Fair enough,' you say") are checked by the PC-agency check even when the
   sentence's declared speaker is an NPC.
3. `persuade_to`'s plain words: the actor is never the persuaded person, and the result reads without verb agreement
   ("Agreed by Ivas Terier: ..."), fixing "You agrees to Ivas carries word...".
- **Accept**: the "Fair enough" sentence is caught when the player did not say it; the talker turn-5 result line is
  grammatical.

## Out of scope
Group entities, spokesperson rules, a find procedure or change kind, a new necessity reason (all rejected by the
owner); R4 (spec 017); R6's recent-phrase feedback (DL-12-99 revisit).

## Success criteria
- Full pytest passes with one test per story, from the two saves where possible.
- `evals/longhorizon.py --mode scripted`: 0 engine errors; novelty-4 reported.
- Live Haiku runs (talker, fighter; 15 turns): hedges per NPC line, walking-in-place loops, wasted successes, scenery
  repeats reported.
