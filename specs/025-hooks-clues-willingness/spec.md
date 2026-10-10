# Feature spec 025: hook terms authored, everything else improvised (T2); clues by judgment (D2 A); willingness that holds for the scene (D3 A); P3

**Input**: `research_notes/Playtest round 2 solutions/ROUND7-PLAN.md` (T2, D2, D3, P3, owner rulings); ROUND7-ANALYSIS
§2 T2 and §6; `round7-investigation/R7-I2-npcs.md` §1, §3-5, §7 A-E, I; `R7-R1-improvised-details.md` (Option 2,
owner-approved); constitution VIII; `rules/_process/reports/R2-K-report.md` "Spec 025" checklist; spec 024's hand-offs
(the seed's lead sentences, "officer of {faction}"). Rules: 11.5.6, PR-11-5, 12.16.16, PR-12-12, T-12-4, 12.2.4
(Director row), 15.7.1; 12.10.8, PR-12-10 steps 1-3, 15.9.5, PR-15-6; 12.11.4, 12.11.9 steps 3-4. DL-12-109, -110,
-112, -118, -119, -120, DL-15-40, DL-15-42. Data: `pacing.yaml#answer_ladder`, `#testimony.guards`;
`investigation.yaml` placement `about`; `economy.yaml#job_fees`, `#price_bands`.

**Owner rulings (binding)**:
- T2: "we could just let the LLM have people make up the amount, who posted it, where he was seen, etc. if it's not
  decided by a pre-existing fact"; after the research the split was approved: code decides a hook's pay, destination,
  issuer and people when it is made; everything else is improvised in character as testimony.
- D2 A and D3 A: "Yup, I approve of A for both of these."

**Parallel lane**: spec 026 (`/fix`, a shared people-card renderer in `packet.py`). Not ours: `packet.py`'s people
card, `fixer.py`, `dispute.py`.

## User stories

### US1 - A hook's terms exist when it is made (T2; 11.5.6, PR-11-5, 12.16.16)
When the seed writes its hooks (the incident, the three leads, the seeded notices) and when a case is built in play,
code decides the hook's **terms**: the pay (a job fee from `economy.yaml#job_fees` by the job's band; AI-6: never a
figure a model picks), the destination (a place), the issuer, the contact and the people involved. They are written
as unsealed knowledge (facts plus knowledge records) of the people who would know, so their speaker cards carry them
as data. A term the case seals (the offer's issuer is node 1's answer) is never written as a term. The seed's code
sentences become data: lead text "<faction> is hiring" without "asks no questions"; the situation lead without
"folk say it is only the beginning"; an officer's role is "officer" with `member_of` (the faction is data).
- **Accept**: C1, C12, C17, C20; on a re-seed of the round-7 fighter world, Magby's speaker card carries the offer's
  pay and place.

### US2 - Everything else is improvised, with guards (T2; PR-12-12 guards)
- A speaker's card shows what *others* said on the same topic (C10).
- A price spoken outside a hook settles from the price band of what is priced (C6, C21).
- A place first heard in speech becomes a real site when the PC travels there (C13).
- The Director can cast a **description** ("the carters", "the refugees") present in a scene (C3); the refugees of
  a refugees incident exist as a group from the seed on.
- **Accept**: C3, C6, C10, C13, C21; the explorer's refugees can be cast.

### US3 - Clues delivered by judgment (D2 A; PR-12-10 step 1, 15.9.5)
When an NPC is asked a question and a case has an open node, one small model call (`Role.CLUE`) reads the question,
the exchange and the about lines of the open nodes (marking the one this person holds) and names the node the
question is about, or none. A held node is delivered by code (the record line the narrator must say; the node found);
a node the person does not hold gets the non-holder's pointer to its holder. Uncertain between a held node and none
-> the held node (P16). The call never sees a node's answer. `case_about`'s word overlap is retired, everywhere it
was read (asking, the Recall look).
- **Accept**: C2, C4, C9, C14, C15, C16; precision and recall on the 36-item labelled set on Haiku.

### US4 - Willingness holds for the scene (D3 A; PR-12-10 step 2)
An NPC's band is decided when the conversation starts (the first question or request to them in the scene) and held
for the scene; it changes only on an event: a payment, a threat or insult (a standing change this turn), or a won
persuasion (a Talk on them, success by the effective degree). A recorded refusal matching a topic refuses that topic
only. An unwilling answer carries one pointer to someone new who would know (a live placement holder on the topic,
else a cast person whose role knows it), never anyone who already refused the PC on it. Willingness never blocks a
delivery 15.9.5 allows. Per-topic re-rolls are retired.
- **Accept**: C5, C7, C11, C18, C22, C23.

### US5 - A deal carries a typed price (15.7.1 item 3)
A Talk with pressure `offer` that the NPC accepts writes a price record `{payer, payee, kind, amount, due}` and pays
it as a typed quantity change: the amount is the player's stated quantity kept inside the price band of the request
(R1..R5 -> bands 0..4), else the band's floor. The regex price parsed from the Framer's prose is retired.
- **Accept**: C6, C19, C21.

### US6 - P3: no willingness line on a greeting or thanks (PR-12-10 step 3)
Plain speech that asks nothing gets no willingness line (no refusal voicing, no speaker card).
- **Accept**: C8.

## Assumptions (recorded; no clarify step)
- A1. Terms are written at the store write of the seed (`write_seeded`), not inside the seed record: the record must
  stay draw-for-draw equal to `12-world-seed.py` (the parity test). The terms are computed from the record only,
  on keyed streams, so they are the same on every load. The seed record's lead text changes are mirrored in the
  reference script (parity).
- A2. The job's band is the destination's ring (1-5), the bounty's band 1: the "work's type-tier" of 08.8.8 by the
  nearest typed proxy. ponytail: a job-kind table if bands prove off.
- A3. The about line of a seeded placement is derived from the node's question part (before ":") and the incident's
  text, never the answer; a placement with an authored `about` uses it.
- A4. The clue judgment runs for any asked NPC while a case has an open node (non-holders get the pointer on a yes):
  one owner per question; R7's only false hit (a non-holder) is a case in the labelled set.
- A5. "Insult" and "threat" are read as typed events: a Talk with pressure `threat` on the NPC (resolved by its
  frame), and any standing change of the NPC this turn (re-decided from the new standing).
- A6. A group ("the refugees") is one NPC entity with `group: true`, an unnamed label, answering through one voice.
- A7. A heard place is a place entity with no `place_kind`; it is reachable by an implicit passage from inside a
  settlement and becomes a building of that settlement on arrival. ponytail: no distant heard places.
- A8. Request size -> price band: R1..R5 -> band 0..4 (the names match: trifle, cheap, modest, costly, precious).
