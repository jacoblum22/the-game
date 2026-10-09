# Feature spec 020: goal-first Reader (F2) and context per role (F3)

**Input**: `rules/_process/reports/R2-J-report.md`, "Engine checklist: Spec 020"; rules 01.2.2, 01.2.6, 01.2.7 item 1,
12.2.2 decision 3, 12.13.3, 12.15.2 (*Title*), 12.2.4 items 1-3 and the role table, 00.15.4, 12.14.2; DL-01-37,
DL-01-39, DL-12-104, DL-00-07; `pacing.yaml#packet` (`guidance_digest`, `situation_cards_by_tag`, `identity_lines`,
`lead_line`). Evidence: `round6-investigation/I4-context-and-model.md` (all), I3 §6, I1 §3 and §5.
**Owner direction** (constitution VIII; handoff §2): whole over parts; better context, not more rules; prefer
deleting machinery to adding it; fixes are not sacred. No clarify step: assumptions are recorded below.
**Parallel lane**: spec 019 (holistic narration) owns `narration.py`, `roles/narrator.py`, `prompts/narrator.md`,
`checker.py`, `prompts/checker.md`, `engine/audit/`, `handles.py`, `change.py`. This spec changes what the narrator
and checker *packets* carry only through the shared builder (`packet.py`, `cards.py`).

## User stories

### US1 - The goal is what gets rolled (P1; F2; 01.2.2, DL-01-37)
"I twist her arm up behind her back: the word, Dunwen" is one beat: the goal `learn` from Dunwen, its method force
against her will (`against_will` on the goal beat). The Reader reads the whole message and returns one beat per goal
(what is to be different, toward whom, how), plus the out-of-character parts (question, `/fix`, safety, pending
answer) it already classifies. It splits only on different goals. All three layers that enforced the act split
change together: the Reader prompt, `reader.normalise` (an against-will act folds into the goal it serves) and the
golden-set policy B5 (relabelled blind, by rule, before any answer was run).
- **Accept**: on Haiku, each of the five single-goal coercion messages of I3 §6 yields one now-beat, the goal
  (`learn`), with `against_will` set, so it is the beat that rolls; golden and held-out verb and gate hold within
  noise of the baseline; the goal-shape set scores better than the old Reader on it.

### US2 - Titles and "Then:" from the typed goal (P1; F2; 01.2.6, 12.15.2, DL-01-39)
The OFFER title and every "Then:" line are rendered by code from the beat's kind and slots, then the method in the
player's own words ("Learn from Dunwen Redmore: twist her arm up behind her back."). The Reader's `method` field and
the restatement are never printed. The method words are a span the code finds verbatim in the message, so they
cannot garble.
- **Accept**: the I1 §3 garble ("Then: demand she tell the word, saying she will be pursued after...") cannot be
  produced: `pipeline._then` no longer reads `method`.

### US3 - Each role gets the situation plus its own guidance (P1; F3; 12.2.4, 00.15.4, DL-12-104, DL-00-07)
No model packet carries the 00.15.4 core or situation cards picked by tag and sorted by id. Each role gets a short
guidance digest for its own judgment, generated from its cards' `[J*]` decision blocks (and, for the Reader, the
change kinds and verb covers from data), identical from call to call. Cards still reach a call where code knows they
apply: a fired trigger's, the anchor candidates', a Talk frame's 15.3.2.
- **Accept**: per-role input tokens on the same seeded scripted run fall by roughly I4's estimate; 0 engine errors.

### US4 - Conversation for the roles that judge it (P1; F3; 12.2.4 role table)
The Director gets the last two exchanges; the World gets the last exchange. (The Checker's conversation is spec 019's.)
- **Accept**: the Director and World packets carry RECENT EXCHANGES once a game has history.

### US5 - Who people are, present or absent (P1; F3; 12.2.4 item 3)
For everyone present, in the spotlight, or named in the player's message or the recent exchanges, the narrator's
view and the testimony call's input carry one identity line: the name as the PC knows it, pronouns, and the PC's bond
to them (`bond.` facts).
- **Accept**: an absent anchor-bond NPC named by the player shows "she/her; your <kind>" in the narrator packet.

### US6 - The lead line only when new or relevant (P2; F3; 12.2.4 item 3)
The narrator's and the World's views list an open thread only when it is new this turn or the turn touches it (its
entity or place is in focus or the spotlight, or the message shares its words). The Director keeps every thread.
- **Accept**: a turn that does not touch the levy thread shows no "open threads" line to the narrator.

## Assumptions (no clarify step)
- A1. "Goals per target" keeps the Reader's existing beat schema (intent, change kind and slots, target, verb,
  facets) as the goal record and adds one field, `how`; it does not replace `parts` (the OOF flags are its classes).
  Callers in `turn.py` stay unchanged.
- A2. `normalise` folds structurally only an against-will **hold** (`restrain` or no change) before a Talk beat to
  the same person; a take or a blow folds only when the model marks it `serves_another_act`. Code cannot tell a
  wanted blow from a coercive one; the prompt asks the model.
- A3. A move to someone present that serves words or an act is that act's method (01.2.2 example, 01.4.1 approach);
  a move to **another place** stays its own goal, because the place change must be written (coarse position is
  judged, DL-12-77). Recorded as policy B3'.
- A4. The Reader keeps its four exchanges (the 12.2.4 role table says two; I4 recommends more). Not in this brief.
- A5. The narrator's and checker's digests are their current role cards (spec 019 is rewriting those roles); only
  the core and the situation cards leave their packets here.
- A6. The method consequence of a folded hold (she stays held whatever the roll) is spec 022's (holds as conditions).

## Out of scope
The narrator prompt line "write around names or kinship" (spec 019's file; hand-off note); the Checker's
conversation (019); `rests_on` and testimony settlement (021); hold conditions and method consequences (022);
ch.06's action economy for in-conflict moves (DL-01-37's provisional clause, owner).

## Success criteria
- SC-1: 5/5 coercion messages give one rolled goal beat on Haiku.
- SC-2: golden/held-out verb and gate within ~3 points of the baseline; goal accuracy reported on all three sets.
- SC-3: per-role input tokens before/after measured on one seeded scripted run; total falls by well over half.
- SC-4: full suite green; ruff and pyright clean on touched files; long-horizon scripted 0 engine errors.
- SC-5: one Haiku fighter playtest (≤15 turns): goal-versus-method rolls and "Then:" quality reported.
