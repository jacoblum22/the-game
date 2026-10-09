# Feature spec 021: testimony and answer lines (F4), pronouns and bonds for speakers, the seeded stance (F7)

**Input**: `rules/_process/reports/R2-J-report.md`, "Spec 021" checklist; rules PR-12-12, 12.3.1b item 1, 12.2.2
(`rests_on` retired), 01.6.8, T-12-18, PR-12-10, 12.10.8, 12.14.12 item 3, 12.2.4 item 3, 12.11.2, 15.1.4; DL-12-102,
DL-12-103, DL-01-38, DL-12-107; `pacing.yaml#testimony`. Evidence: `round6-investigation/I2-npc-testimony.md` (all),
I1 §5-6; spec 019's hand-off (the pay figure / speaker-card leak).
**Owner direction** (constitution VIII.1, VIII.3; handoff §2): code owns the spine, the model owns language; what a
character says is testimony, settled only when the player acts on it; prefer deleting machinery to adding it.
**Parallel lane**: spec 022 owns `engine/resolve/`, `dispute.py`, `understand.py`, `change.py`, `engine/harm/`.

## Traced causes (confirmed on the round-6 saves before any change)
| Case | Save, turn | What the record shows |
|---|---|---|
| Garbled odds line from a refusal | 233000 t7-t14 | testimony call returned `{npc.dunwen, "will give no word out while", "pc.evine_oakwell has a hand on him"}` from "You'll get no word out of me with your hand on me"; written as fact.103; Framer snags cite fact.103 on t8, t12, t14 |
| Friend as a stranger | 232941 t8 | Lilett's SPEAKER CARD: three "knows:" lines, trade, news; no bond, no pronouns (`bond.` skipped; the bond fact's subject is the PC) |
| The wall | 232941 t6, 192926 t10 | `R2 MUST: ... tells you who is keeps the gate at The Red Warren: no one you know` (`cast_who` -> `NO_ONE`, written as `who_is_*` fact.110) |
| Found clue re-delivered | 232941 t5 | `R1 MUST: Lilett ... tells you the way on: toward The Red Warren`; the node was found at t3 (`R2 ... You make out the way on`) |
| Card leaks | 232941 t13 | Sevella's card: `knows: Sevella de Belac correction 1 Lilett said she knew no one ...` (fact.114, source correction); fact.103/133 `agreed` = the player's goal |

## User stories

### US1 - Testimony settles only when the player acts on a specific claim (P1; PR-12-12 step 1, DL-12-102)
Triggers, all found by code from the beat and the open `said` records: (a) travel to, or (c) a beat target that the
PC knows only from testimony (a person whose name they only heard, a place no record of theirs is about), and (b) a
beat whose stated premise (`assertion`) restates a said claim. The Reader's `rests_on` is retired (field, schema,
the Reader packet's TESTIMONY block).
- **Accept**: offline re-run of the triggers over the recorded turns of the six round-6 saves fires on far fewer
  turns than 64%; hearing, repeating or arguing with testimony settles nothing.

### US2 - The claim call states world claims only (P1; PR-12-12 steps 2, 4; DL-12-102)
The call sees the speaker (identity line), the exchange the words were said in, and the identity lines of everyone
named; the view carries names, not ids. It returns `kind`: `claim` or `none` (a refusal, opinion, want, feeling,
intention, or a question). `none` writes nothing and the record is closed (`settled: "none"`). `settle()` also never
accepts a claim whose subject is the speaker and whose predicate is their own will ("will", "won't", "refuses"...).
A true claim is written with its own predicate (no `said.` prefix, no value in the slug); the `said` record keeps
the speaker and turn and points to the fact, and the odds line attributes it ("Dunwen said: ...").
- **Accept**: the 233000 t7 refusal writes no fact; the five recorded fighter claims re-run on Haiku give 0 facts
  that are refusals or intentions.

### US3 - Answer lines carry a fact or a clue, or are not written (P1; PR-12-10, DL-12-103)
A failed cast writes nothing (no `who_is_*` "no one you know" fact, no line); the NPC answers in words within their
willingness; a DM-side "who is X?" with no one cast gets no Oracle line. `_from_case` never re-delivers or points at a
node the PC has already found. "Who are they?" is not the knower's own name.
- **Accept**: the 232941 t6 gate question gets a willingness line, not "no one you know"; t5's found node is not
  re-delivered.

### US4 - The speaker card shows who the speaker is to the PC and never the player's own words (P1; 12.2.4 item 3)
The card header carries the speaker's pronouns and the PC's bond to them ("she/her; your friend"), and the people the
card's lines name get identity lines. "knows:" never shows a correction (`source: correction`, `correction.*`), an
`agreed` fact, or a settled testimony fact (those are what someone *said*).
- **Accept**: Lilett's card (232941 t8) says "your friend"; Sevella's (t13) has no correction line.

### US5 - Only mechanical facts are lever or snag candidates (P1; 01.6.8, DL-01-38)
The Framer's lever/snag enum excludes scene slots (`detail.activity|posture|held|manner`), legacy unattributed
`said.*` facts and dispute words (`source: correction`).
- **Accept**: on the 233000 state at t8, fact.103 is not in the Framer's lever enum.

### US6 - A seeded stance bounds the first reaction roll (P2; 12.11.2, 15.1.4, DL-12-107)
`helps` never starts below Neutral; `hinders` never above Wary.
- **Accept**: Belby (helps) can no longer start Unfriendly.

### US7 - Two leftover patches (P3)
The re-shown OFFER's "Then:" renders from the typed goal (`oof.goal_line`), never the Reader's `method`;
`resolution.yaml#intended_change.split` matches 01.2.2 / 01.2.7 after the goal-first split.

## Assumptions (no clarify step)
- A1. PR-12-12 step 4's `said_by`/`said_turn` are kept on the `said` record (which points to the fact) instead of new
  event-schema fields: one source of provenance, no store migration.
- A2. Trigger (b) "cited in a roll" is read from the beat: the Reader's `assertion` (the player's stated premise)
  covers most of a said record's content words. The Framer never sees said records (01.6.8), so it cannot cite one.
- A3. Trigger (c)'s frame-input reading other than "a target known only through testimony" is not derived (no field
  carries it); revisit per DL-12-102's "revisit if".
- A4. The willingness line stays (PR-12-10 step 2 is code's): it is guidance about how the NPC answers, not content.
- A5. The kin-question case misroute (I2 §3, "Is Rrakaa kin of yours?" -> the way on) and the `agreed` fact's
  content (`change.py`) are out of this lane; hand-off notes.
