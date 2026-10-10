# Spec 024: made-up and edge cases (written and committed before implementing)

Owner rule (DL-00-08): "every fix must also pass made up cases, including cases specifically design to test edge
cases". Each case is labelled **made-up** (a plausible play situation not taken from a save), **edge** (a boundary
of the rule) or **playtest** (from the round-7 saves, the held-in set). Seeds C1-C7 are the R2-K checklist's; C8 on
are this spec's. Each becomes a test in `tests/engine/test_spec024_cases.py` (or the replay script for playtest ones).

| # | Label | Case | Pass when |
|---|---|---|---|
| C1 | made-up | An innkeeper whose habit is "wipes the bar with a rag", over ten turns of talk, the tenth while the inn is on fire. | No packet line requires or quotes back the habit: it appears only in her view block's one background line (worded "now and then", her pronouns), never in a MUST line, a SCENE SETTING `present:` line after framing, a refusal line or a FRESHNESS block, on all ten turns, fire or no fire. |
| C2 | made-up | An unnamed officer whose role is "officer of The Order of the Grey Hand", mentioned every turn. | No "call them", no "as every other screen does", no "the words every other screen uses" in any packet; the role and faction reach the narrator as data (`role:`), and the packet says only that the name is unknown. |
| C3 | made-up | A lock barely missed; the player takes "succeed, but the guard hears you". | `effective_degree` is `success`; the narrator's beat line says success at a cost, the claim check counts it a success, scene state takes the success row; nothing reads it as a failure. |
| C4 | edge | An unnamed he/him walk-on (age "young (in their teens)", activity "going about their morning work"). | Every code template about him says he/him/his: the view's background line, the age, the activity line, the refusal line, the willingness line, the name-unknown line. No "call them". |
| C5 | edge | A near-miss pause, then the player declares something new instead of choosing. | While the pause is open the beat line has no degree, no "near miss", no result words and is not owed; once the default failure applies (pause gone), the beat line says failure. |
| C6 | edge | "What did the notice say again?" with the notice in view. | The reading line is given (its words quoted), exactly as on the first reading: a player's own repeat request is honoured, nothing calls it repetition. |
| C7 | edge | The narrator uses an NPC's habit twice in one scene, knowingly. | The draft is delivered as written: no failure, no redraft, and the next turn's packet carries no freshness, usage or quote-back line about it. |
| C8 | made-up | The innkeeper's tenth turn: the inn is burning and she is asked to help carry water. | Same as C1 (the habit is not pushed into an emergency); her response line carries no habit. |
| C9 | edge | A she/her NPC whose name the PC does not know (`the hedge-mage`). | View: "does not know her name"; SCENE SETTING: no "call them"; refusal and willingness lines: "her own". |
| C10 | playtest | Talker inputs 27-28: a round offered, a near miss, "succeed and pay" taken; then a question to the same sellsword. | The talk's NPC response is an agreement (no `refuses`), `answer.willingness` is `willing` ("the talk moved him"), scene state takes the talk-success row. |
| C11 | edge | A paused beat at an OFFER and at a near miss, both talking to the NPC present. | The record has no result for the paused beat; the answer line says the addressed person has not answered the paused ask yet and the turn stops before it; the code-rendered fallback line has no result words. |
| C12 | made-up | A two-paragraph passage: paragraph 1 narration and a speech by the innkeeper; paragraph 2 a speech by the guard, tagged. One sentence in paragraph 2 is cut by a check, and one speech is quoted by code. | The delivered text keeps the paragraph break; the cut sentence goes with its own space; the quote is applied in place; both speakers' `said` records are kept. |
| C13 | made-up | An NPC with a habit met in three scenes (gate, inn, temple). | In every scene's packets the habit is only in the view's background line; at each scene opening the `present:` line has the look, later turns do not; no MUST line ever names it. |
| C14 | edge | An illiterate PC at an opening with a lead and no named notice; and with a named notice too. | "the character cannot read any posted notice" / "the character cannot read the hire notice or any posted notice": never "the any". |
| C15 | edge | A seeded hire or bounty notice. | Its text ends "… Posted by <issuer>.", never "… at the market square. The Mereham Wolves". |
| C16 | edge | `"That one's the worst of the lot," she says` right after "Magby's back is still turned" (Magby he/him), the speech's declared speaker a she/her. And `"Go," he says` whose declared speaker is she/her. | The first is no hit (a tag is judged against its speaker); the second is a hit. A tag with no declared speaker is no verdict. |
| C17 | edge | "Who did you ask, and what did they say?" with two notices in scope and no reading beat. | No reading line (no notice is named or acted on). "I read the notice" with one notice in scope still gets it. |
| C18 | edge | An addressed NPC whose row is "carries on with their own business" (not a refusal), and one who refuses. | P4: only the refusal carries the "they do not give the PC what was asked" suffix. |
| C19 | made-up | Every turn of a seeded game's first scene, and the opening. | No SCENE SETTING has "brought the word" or "the matter at hand"; the opening's incident note has the reporter as a data field ("reported by: X"). |
| C20 | edge | A cut sentence that opens paragraph 2. | The next kept sentence still starts a new paragraph. |
| C21 | edge | Degree readers on: a critical failure; a near miss defaulted to failure (no pause); a critical success; no roll. | `effective_degree`: `critical_failure`, `failure`, `critical_success`, `None`. |
| C22 | edge | A they/them NPC and a person with no recorded pronouns. | Template text keeps "their"; nothing is guessed. |
| C23 | edge | Pronoun fill on free text (a knowledge line "the Wolves pay their men"). | Never changed: only template-derived text is filled. |
| C24 | playtest | Explorer inputs 20-21 (turn.4, turn.5) delivered from their recorded passages. | `\n\n` kept: Morga's speech stays its own paragraph. |
| C25 | playtest | The round-7 talker and explorer narrator packets rebuilt. | 0 habit outside the background line, 0 "brought the word", 0 FRESHNESS / quote-back, 0 "call them", 0 pronoun-neutral template words for a person with stored pronouns. |
