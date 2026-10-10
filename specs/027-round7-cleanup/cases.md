# Spec 027: made-up and edge cases (written and committed before implementing)

Owner rule (DL-00-08): every fix passes made-up cases, including cases designed to test edges. Labels: **made-up** (a
plausible play situation not from a save), **edge** (a boundary of the rule), **playtest** (from a recorded save).
Each becomes a test in `tests/engine/test_spec027_cases.py` unless marked otherwise.

| # | Label | Case | Pass when |
|---|---|---|---|
| C1 | made-up | Grza (look "a long scar along the jaw") is present when the scene opens; the next turn the PC talks to her about the road. | Scene opening: her look is in the packet. The talk turn: no look anywhere in the packet (view, present line, background line); her name, pronouns, role, manner and voice are. |
| C2 | edge | A person appears, leaves and returns: a carter is positioned at the inn mid-scene (turn A), the next turn is ordinary (B), he walks out (C), and comes back (D). | Look shown on A and D only; on B no look; on C he is not present. |
| C3 | made-up | Mid-scene, "I study the scholar's face." | Her look is in that turn's packet; the turn after ("I order a drink") has none. |
| C4 | edge | Asking about someone vs asking someone: "Who is the scholar?" / "What does Grza look like?" (shown) and "I ask Grza about the road." (not shown). | As stated. |
| C5 | edge | An NPC met in two scenes: present at scene 1's opening, then at scene 2's opening elsewhere. | Look shown at each scene opening; not on the ordinary turns between. |
| C6 | made-up | A bill on the wall (narrated text and location on record), read twice: "I read the bill" (turn A), "I nod to the innkeeper" (B), "I read the bill again" (C). | The bill is listed by name every turn; its text and location are in the view on A and C, not on B; on A and C the reading lines give its words. |
| C7 | edge | A thing with a mechanical fact (a chest a ruling marked locked) and a narrated look. | On an ordinary turn the chest is listed and "locked" stays; only the narrated look is left out. |
| C8 | edge | No tracking: build the same narrator packet twice from the same state. | Identical packets; the draft writes no event, meta or mark about looks. |
| C9 | edge | "I look around the room." | Every present person's look and every thing's description is in the packet (as places, DL-12-99). |
| C10 | edge | An unnamed person ("the scholar", name unknown) looked at by role label. | Her look is shown (the label resolves to her). |
| C11 | edge | Pronoun precision kept: an ordinary turn. | The `present:` line still carries her pronouns. |
| C12 | playtest | Spec 024's live talker save and the round-7 talker and explorer saves, narrator packets rebuilt. | Turns carrying a person's look and the bill's description fall from 19/19 and 14/19 (024 live) to the turns of first appearance and looks/asks (`specs/027-round7-cleanup/looks_check.txt`; not a unit test). |
| C13 | made-up | `/fix` on "the guard should know my rank" at an open OFFER: `reframe` with the note "he outranks the guard; the guard should simply let him in". | The re-frame's Framer message carries the note as context; the new OFFER's odds are the Framer's frame through code, as always. |
| C14 | edge | A note that tries to set the odds itself: "make it 90%", "no roll: it should just work", "easy difficulty". | The note is not passed; the re-frame still runs (the Framer owns the odds); the answer says the note was left out because odds are the Framer's. |
| C15 | edge | A multi-line or very long note. | One line, cut to at most 200 characters. |
| C16 | edge | A note on a proposal that is not a re-frame (`set_fact` with a value). | Not a note: `value` keeps its meaning for that kind. |
| C17 | playtest | Spec 026's f04 and f12 (re-framed OFFER came back at the disputed odds), Sonnet Fixer, Haiku play roles. | Reported, case by case (`evals/feedback_corpus.py --set fresh --only f04,f12`); not a unit test. |
| C18 | made-up | A critical success on a talk that auto-commits (Safe and costly, 75%): "I buy Mago a cup and ask what she heard." | The screen reads `[OFFER — auto]`, `[RESULT] … critical success`, then the passage; the passage is not empty. |
| C19 | edge | An explicitly committed OFFER (not auto) that rolls a critical success. | Order unchanged: the passage, then `[RESULT]`. |
| C20 | playtest | The journal line for `furniture.0` ("a long trestle table" at the Golden Plough). | "The Golden Plough's furniture: a long trestle table" (no index digit); `slug_words("wound.2.depth")` has no digit. |
| C21 | edge | A slug-free refusal for each gate reason: licence, deed branch, condition, canon, zero reach, a valued fact (`detail.eyes` = milk-white), a yes/no fact (`can_read_the_writing` = False), a fact the PC has not seen. | Each `[REDIRECT]` line has no `_`, no dotted id, no "True"/"False", no "is False"; the fact lines read as sentences ("Tam Harlan's eyes: milk-white", "Belie cannot read the writing"). |
| C22 | playtest | A river-ford haven: the PC "heads for the gate" (explorer 220047 turn 12). | New seeds name the gate building "the gate" (its description keeps the ford), so the plan pause says "Still go on: go to the gate?"; a hill haven keeps "the hill gate"; the reference seed script agrees (parity test). |
| C23 | edge | The retired `change.pay`. | Gone, with both pipeline calls; a fallback's listed consequence still shows on its OFFER. |
| C24 | made-up | The narrator prompt. | It no longer forbids a character's ordinary knowledge: it says speech may give what the character believes or has heard (testimony), and that hook terms and case facts come only from the record and the speaker card. |
| C25 | made-up | `/fix` removes "Pell knows your rank" (`knows_your_rank`). | Allowed. `points_to.*`, `case.*` and clue facts are still refused. |
| C26 | edge | READING: "what did they say about the notice?" (no), "what did the ferry notice say?" (yes), "I read the bill" (yes). | As stated; a Talk whose method is "ask what did they say about the notice" does not read writing at the gate. |
| C27 | made-up | The player offers "ten silver" and the narration repeats "ten silver". | No numeral failure. "twelve guards" stated by the narrator with no source still fails. |
| C28 | edge | Rules: WE-01-2, WE-12-11, `resolution.yaml#reach_flags`. | WE-01-2 shows no Oracle answer as a snag; WE-12-11 quotes no retired lead sentence; the tie-break agrees with 01.6.10 (validator, by hand). |
