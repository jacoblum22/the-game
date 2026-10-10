# Spec 025: made-up and edge cases (written and committed before implementing)

Owner rule (DL-00-08): "every fix must also pass made up cases, including cases specifically design to test edge
cases". Each case is labelled **made-up** (a plausible play situation not taken from a save), **edge** (a boundary of
the rule) or **playtest** (from the round-7 saves). C1-C9 are the R2-K checklist's seeds; C10 on are this spec's (the
brief's eight, then more). Each becomes a test in `tests/engine/test_spec025_cases.py`; the clue judgment's
model cases (C2, C4, C14, C16) are also items of the labelled set (`clue_set.yaml`), measured on Haiku.

| # | Label | Case | Pass when |
|---|---|---|---|
| C1 | made-up | "Reward for the missing ferryman" (a bounty hook). The PC asks the ferry-keeper how much, who posted it and where he was last seen. | The hook's pay (a job fee from `economy.yaml#job_fees`, never a model's figure), its issuer and its contact are written when the hook is made, as unsealed knowledge on the cards of those who would know; the keeper's speaker card shows them. "Where was he last seen" has no term: the keeper answers in words (testimony). |
| C2 | made-up | The widow holds the clue "he owed the toll-keeper money" and is asked "Did he have enemies?". | The clue judgment says yes (no shared word needed); code hands the clue to the narrator (a record line with the clue); the node is found. Offline: a scripted yes; live: an item of the labelled set. |
| C3 | made-up | A lead says "refugees came in"; the Director's next scene at the temple casts "the refugees". | A description in `next_scene.cast_described` casts a group present in the scene: the existing refugees group if there is one (moved there), else a new unnamed group with that label; never a random walk-on. |
| C4 | edge | The widow (same clue) is asked "Is the river high at the ferry this week?". | Judged no; nothing about the clue reaches the record; she answers within her willingness, in words. |
| C5 | edge | Everyone who would know a topic has already refused the PC on it. | The refusal's pointer names someone new (a cast person whose role knows the topic) or, when there is no one, no pointer at all (the stuck answer, 12.8.5); never someone who refused. |
| C6 | edge | A merchant says "ten silver for the map"; the PC pays (`player_quantity` 10, request R2). | The deal's typed price is settled from the band of what is priced (R2 -> band 1, 2-5 coins): 5 coins leave the PC's purse, a price record is written; the spoken "ten" never reaches the purse. |
| C7 | edge | A Guarded NPC; the PC pays a coin; then asks about a new topic; and the NPC has a recorded refusal about "his son". | The payment moves the band up one step (guarded -> willing); the new topic does not re-roll; a question about his son still refuses (that topic only). |
| C8 | edge | "Thanks, friend." (no question, no request) | No willingness line, no refusal voicing, no speaker card for that NPC. |
| C9 | edge | A Guarded holder of a core clue, no refusal covering telling, asked about it. | Delivered (willingness never blocks a delivery 15.9.5 allows). |
| C10 | made-up | Two NPCs asked the same improvised detail ("where was he last seen?"): the keeper answers first, then the widow. | The widow's speaker card shows what the keeper said on that topic ("others have said"), so she can agree or knowingly differ. |
| C11 | edge | A refusal that would loop: Morga refused on the refugees; Roswen now refuses on the refugees too. | Roswen's pointer never names Morga (or Roswen): a holder of a live placement on the topic, else someone new. |
| C12 | made-up | A hire notice says only "Good coin, no questions"; the PC asks the contact "what does it pay?". | The contact's card holds the typed pay (the job fee of the job's band) and the destination; same figure from anyone who holds the term. |
| C13 | made-up | An NPC says the refugees are "up at the healer's house", a place only mentioned in speech; the PC goes there. | The heard place is reachable from the settlement; on arrival it becomes a real site (a building of that settlement, with a parent and a kind); the move succeeds. |
| C14 | edge | A question that sounds like the clue but is not: the holder of "who leads the refugees" is asked "who leads the evening prayers at the temple?". | Judged no; no delivery, no pointer. |
| C15 | edge | An Unfriendly (standing -2) holder of a core clue, no refusal covering telling, asked about it. | Delivered; the willingness band is not consulted for the clue. A recorded refusal whose tags cover telling still blocks it. |
| C16 | playtest | Talker turn.9: the sellsword (no placement) is asked "Have you signed with Morri's Wolves?"; the omen case's subject is "a sign of the rite". | No case route: no pointer line "does not know what the omen shows, but Kerric would"; the question is ordinary. |
| C17 | playtest | Fighter: Magby, the offer's reporter, asked what the job is, what it pays and where. | His card holds the offer's terms: pay (a job fee), the job's destination and the task, as data; the issuer (the case's sealed subject) is not on it. |
| C18 | playtest | Explorer turn.8: Roswen refuses a question about the refugees. | His refusal carries one pointer to someone new who would know: a live placement holder of the refugees case (never Morga, who is only the person in the room). |
| C19 | made-up | "Let me buy you a cup" (pressure offer, no amount, no roll) and the NPC agrees. | A typed deal price: R1 -> band 0 -> 1 coin leaves the purse, a price record `{payer, payee, kind, amount, due}` is written; the NPC's willingness moves up; nothing is parsed from prose. |
| C20 | edge | The offer incident: its issuer is the case's sealed subject. The PC asks the reporter "who is paying?". | The reporter's card shows pay and destination but never the issuer; the question is judged about the clue they hold and delivered by the case, not by the card. |
| C21 | edge | A stated price inside the band ("I'll give you 3 coins" for an R2 favour). | 3 coins (the stated amount kept when inside the band). |
| C22 | edge | The same NPC asked two questions in one scene, the first answered unwilling by a d10; and the next scene, the same NPC again. | The second question in the scene reuses the band (no re-roll); a new scene decides it afresh. |
| C23 | edge | A won persuasion (a Talk frame on the NPC, success at a cost taken) after an unwilling answer in the same scene. | The band becomes willing and holds for the rest of the scene. |
