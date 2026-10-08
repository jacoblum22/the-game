# Playtest issues

Triage list for the automated playtest loop (`evals/playtest.py`). One row per issue, deduplicated across runs.
Class: **bug** (engine, fix it) · **harness** (the test rig, not the game) · **rules** (logged to
`rules/_process/issue-ledger.md`, never edited here) · **claude-only** (may not happen with Gemini) · **polish**.
Status: open · fixing (round N) · fixed (commit) · logged (ledger id) · wontfix.

| ID | Class | Sev | Issue | Evidence | Status |
|---|---|---|---|---|---|
| P-001 | bug | high | Raw pydantic error "1 validation error for OracleResult … valid boolean, input_value=[items]" printed to the player as game text | run 20261007-155118 input 26 | fixed (merged in integrate-r1) |
| P-002 | bug | high | Claim check doesn't converge: 5/7 turns fell back. Redrafts re-extract all sentences and fail ones that passed; unnamed background figures' ambient acts cut as unsourced_change; Oracle "yes" still forces a redraft; elapsed-time and empty-reason contradictions | 20261007-155118 turns 1,2,4,6,7 | fixed (merged in integrate-r1) |
| P-003 | bug | high | Plain fallback text reads as debug output: "X? Yes. Y? No.", "No roll: trivial", "Possible now: …", "Time passes ( intervals)", infinitive restatements | 20261007-155118 turns 2,4,6,7 | fixed (merged in integrate-r1) |
| P-004 | bug | high | Hunter's sheet says "good at tracking", then tracking is redirected: "needs Tracking, which you have not learned" | 20261007-155118 input 27–29 | fixed (merged in integrate-r1) |
| P-005 | polish | med | OFFER block jargon: "Mode: fallback — DC +5, reach capped at limited", "time, S1", garbled stakes | 20261007-155118 input 28–29 | logged I-134 (follows 12.15.2) |
| P-006 | bug | low | Name step says "Add he, she or they", but "Branric Blackfield, she" then asks pronouns again | 20261007-155118 input 22 | fixed (0046d78) |
| P-007 | polish | low | "a hunter, half-elf" silently becomes human ("No elves live in this land" shown in passing only) | 20261007-155118 input 18–19 | open |
| P-008 | harness | — | Player never saw its own typed lines, so it reported "skipped" steps that weren't skipped; notes repeated old complaints | 20261007-155118 inputs 18–24 | fixed (harness echo, round 2 on) |
| P-009 | polish | med | World-seed summaries too vague to judge: "5 more" places, "the enemy and the prisoner", rumors/wilds as counts only; "3 more" powers unnamed; no way to see the rest | 155118 12–16; 161327-breaker 14–22 | fixed (0046d78) |
| P-010 | polish | low | Jargon in setup and sheet without explanation: keepers, haven, Kinspeech, dread, Resolve | 20261007-155118 inputs 8–13, 24 | fixed (0046d78) |
| P-011 | polish | low | Mixed setup: "step N of 14" titles don't match the question asked; 14 keep/re-roll screens feel long | 20261007-155118 inputs 5–10 | open |
| P-012 | bug | med | A critical failure is announced ("goes badly wrong") but the player never learns what happened | 20261007-155118 turn 6 | fixed (172b2b2: [RESULT] block); ledger I-147 |
| P-013 | bug | med | A question at a setup step ("what does haven mean?") prints "Here is a little more about each choice" with only the option labels, then the whole step again; repeated questions loop | 161327-breaker inputs 8–35 (25 notes) | fixed (0046d78) |
| P-014 | bug | low | Welcome + step 1 screen reprinted in full after each unparsed answer | 161327-breaker inputs 24–35 | fixed (0046d78) |
| P-015 | polish | low | Livelihood list shows 7 + "14 other ways of life", then all 21 on the next screen | 161327-breaker inputs 27–34 | open |
| P-016 | bug | med | Multi-part message ("what are my options? also, who's standing at the gate?") fails screen 12.2.7 "a part of the player's message is not answered" and falls back | 161327-breaker turn.5 | fixed (fd898d8: narrator/checker get only in-fiction parts) |
| P-017 | polish | low | [LEADS] block repeated on consecutive "what are my options?" | 161327-breaker inputs 38–39 | open |
| P-018 | bug | high | Beginner never got the scene described: mixed "I'm new / what are my options? / describe where I'm standing" got placeholder notes and repeated LEADS for 10+ turns. Root cause: redrafts failed, fallback had nothing for a question | 161329-newcomer turns 2–11 | fixed (fd898d8); ledger I-135 |
| P-019 | bug | med | "What do I know about the High Vale?" gets "Session move noted" / "Already knows… No." instead of an answer; loops | 161320-explorer 33–40; 172452-breaker 28–31; 170157-breaker 30–31 | fixed (03a9ba7); ledger I-141 |
| P-020 | bug | med | Same [OFFER] shown twice; a typed choice ignored; a persuasion result never shown | 161323-talker inputs 28–38 | partly: duplicate OFFER was two player messages; see P-025 |
| P-021 | bug | med | Raw NPC action-row text in fiction: "Tikka Mud-Walker escalates: threatens, calls for others", "asks the PC something" | 161323-talker inputs 26–28 | fixed (de1c13d) |
| P-022 | bug | med | Framer/Reader responses rejected (invalid_reasked → defaulted) with no reason logged. Causes: social anchors had no defense attribute (every opposed Talk frame failed); PENDING_ANSWER offered with no open pause | talker 2+2, explorer 1 | fixed (de1c13d); ledger I-137 |
| P-023 | bug | high | Intent substitution: "I shout at the travellers to state their names" became an OFFER to wound the nearest traveller; offers drift Talk(Presence) → Talk(Might) → Strike without the player asking | 161325-fighter inputs 29–40 | fixed (ea57355): anchors limited to the beat's verb family; conditional strikes logged I-146c |
| P-024 | polish | med | Trivial acts get a full odds screen (opening an unbarred wicket "easy obstacle"); a shout at 35% with 20% critical failure; a retry shows worse stakes but better odds | 161325-fighter inputs 29–32 | open |
| P-025 | bug | high | A successful Talk to learn something (the old enemy's name) never reveals it: narration fell back to "responds as the talk went: success", so the player asked again and got a second OFFER | 161323-talker turns 5, 9; 170157-breaker 24–28 | partly (d06505c delivers stored facts); recurring when the store has nothing: owner decision I-153 |
| P-026 | bug | high | An addressed NPC's reply is cut as "no source for this act" (Bixok repeats the question back); background figures' acts still cut by code when the Checker extracts them | 170157-breaker turns 6, 9, 10, 12; 170200-newcomer; 170207-talker (every conversation stalls) | fixed (d06505c); ledger I-140 |
| P-027 | bug | med | [OFFER] leaks internals: "source: fact.203", "target not yet chosen", "free OFFER", raw OOC text; wrong pronoun ("her" for a he/him NPC) | 170157-breaker inputs 19–26 | fixed (af1fdce) |
| P-028 | bug | med | A question at an open pause ("what does 'Go big' mean?") gets a generic note and the same OFFER reprinted; "Play it safe" unexplained; no Enter default shown | 170157-breaker inputs 19–28 | fixed (af1fdce + 172b2b2) |
| P-029 | bug | low | "What do I know about the stranger" folded into a Move roll offer; journal says "nothing yet" after learning things | 170157-breaker inputs 30–31 | fixed (03a9ba7) |
| P-030 | polish | low | Narration repeats the same scene details turn after turn (the wiped counter, wet wool, the murmur) | 170157-breaker 22–29; 172452-breaker 27–31; 174833-newcomer 28–36 | fixed (74f7749: freshness 12.14.11) |
| P-031 | bug | high | Basic talk refused: "talk to the person on the bridge" / "press him gently" → "[REDIRECT] needs Stonesense, which you have not learned" | 170200-newcomer turns 4–10 | fixed (1e3ec97); ledger I-139 |
| P-032 | bug | high | Declared movement ("I walk out along the bridge", "go closer", "head into Mossfield") writes no position, so arrival narration is cut as unsourced | 170200-newcomer turns 5–16; 170318-fighter turns 13, 16 | fixed (1e3ec97); ledger I-139 |
| P-033 | bug | low | NPC called both "they" and "him" in narration | 170200-newcomer turns 8–14 | fixed (1e3ec97) |
| P-034 | bug | med | Internal note in narration: "(Her claim about the ankle is context only)" | 170318-fighter input 28–30 | fixed (17eebe7) |
| P-035 | polish | med | A failed beat doesn't show what it cost or what happened ("the press holds you", an ankle "holds" you); "Go big" raises stakes with no stated gain | 170318-fighter inputs 19–27 | fixed (172b2b2: cost paid shown) |
| P-036 | bug | med | Narration says "Edda is not your friend" though the sheet lists Edda as the PC's friend (creation bond does not reach the NPC's standing?) | 170207-talker turns 13–15 | fixed (be20402); ledger I-142 |
| P-037 | polish | low | Named NPC drifts back to "a woman" / "stranger" after being named (Bixnik Quick-Fingers) | 170207-talker turns 10–15 | open |
| P-038 | bug | high | "What do I know about the land around Hawkstead?" read as a Mind sorcery attempt → REDIRECT for lacking the spell; plain "what do I know?" only repeats scene text (with P-019) | 170204-explorer inputs 20–23 | fixed (1e3ec97) |
| P-039 | bug | low | Garbled Oracle twist fragment in narration: "Can say it in answer to a question asked aloud, but lesser"; PC referred to in third person ("he asks") | 170204-explorer inputs 25–26 | fixed (17eebe7 + db07b1d: verbs after and/then in second person) |
| P-040 | bug | high | Fallback mangles restatements: "You try to gerella is pinned against the gatepost", "Knows where … can not be found"; "It works." before any roll | 172629-fighter inputs 19–31 | fixed (17eebe7) |
| P-041 | bug | med | Narration contradicts itself across turns: a notice reads "NO QUESTIONS ASKED", a later turn says it does not (mentioned object's text not stored or not shown back) | 172552-newcomer inputs 27–35 | fixed (be20402) |
| P-042 | polish | low | "What do I know" answers show raw Oracle predicates ("name — yes") | 03a9ba7 fixer report | fixed (44d181e) |
| P-043 | bug | low | Sheet shows a raw placeholder: "carries the fact teaches: <the gifted spell>" | 174833-newcomer input 23 | fixed (74f7749) |
| P-044 | polish | low | OFFER's Enter default is Withdraw; a newcomer pressing Enter backs out without noticing | 174833-newcomer inputs 26, 31 | fixed (172b2b2: Enter re-prompts) |
| P-045 | bug | med | Narration names the record: "…wound and ruin the record holds" | 174833-newcomer inputs 35–36 | fixed (74f7749 + verdict reasons reworded) |
| P-046 | rules | med | A newly arrived figure ("the arrival") can never become a person: Oracle settles yes/no only and 12.14.13 forbids creating a person by mention, so the scene stalls | 174833-newcomer inputs 33–38 | logged I-140(c) |
| P-047 | bug | med | Asking about Luck at an open OFFER silently reframed it (75% risky → 50% safe); Luck not spent; no explanation | 175045-breaker inputs 22–30 | fixed (01a3737): questions answered before the pause; Luck reroll has no play hook (I-144c) |
| P-048 | polish | low | [LEADS] entry truncated mid-sentence ("and…"); "open thread" label unclear | 175045-breaker inputs 18–19 | open |
| P-049 | bug | high | Framer offered every cost/tier option, then the engine rejected illegal ones (cost.time with no clock, exposure with no observer, trivial tier rolled, opposed without entity, lever established too late) → re-ask → default frame | 6 saves, 16 rejections | fixed (01a3737): 8/17 saved rejections now impossible by schema, 9 guarded by a packet note |
| P-050 | bug | high | "Go big" at an OFFER sometimes → "You cannot do it that way. What do you do?", offer lost; once "It works" twice then a new offer | 174829-fighter inputs 19–25 | fixed (01a3737) |
| P-051 | rules | med | Odds: 20% success vs 35% critical failure on "safe" stakes; hidden-roll offers show no odds despite the promise | 174829-fighter inputs 19–31 | logged I-143 |
| P-052 | polish | low | Walk-on NPC shares the PC's first name (Aldett Redley / Aldett Blackbrook) | 174829-fighter input 30 | logged I-142 |
| P-053 | bug | med | OFFER prints a raw dict: "bond.anchor: {'kind': 'friend', 'npc': …}" (fact-id-to-words replacement on a structured value) | 174825-explorer input 20 | fixed (01a3737) |
| P-054 | bug | med | Asking to see the sky omen / a notice's words gets a restated question ("has not visible colours, shapes and motion") or "The notice is a hire." with no detail | 174825-explorer inputs 21–31 | partly (44d181e); notice wording still stored yes/no only |
| P-056 | bug | med | An NPC (praying attendant) never answers across several turns, even after a Talk roll, and nothing tells the player he won't: a silent refusal reads as a stall | 175928-talker inputs 18–23 | fixed (44d181e: NPCs created mid-scene joined cast_present) |
| P-057 | bug | med | "Change approach" re-shows the offer with changed odds and never asks for the new approach; "ask nicely, no coins" still framed as offering coins; attribute switched to Intellect | 181158-breaker inputs 20–24 | fixed (172b2b2) |
| P-058 | bug | med | Learned facts rendered raw: "coin named none yet: yes", journal "Bixok Lucky: coin named none yet — yes (told)", entries truncated "one of…" (with P-042) | 181158-breaker inputs 23–28 | fixed (44d181e: one fact_sentence helper) |
| P-059 | bug | med | "Spend my Fate point" at an OFFER: no answer whether it was spent; no result shown | 181158-breaker inputs 29–31 | open (with P-047) |
| P-060 | bug | high | Condition-blocked moves: "[REDIRECT] Not as tried: 1 prevents it right now" (the condition's name replaced by "1"), printed twice; player never told what blocks them or how to clear it; same climb refused 4 times | 181737-fighter inputs 21–30 | fixed (172b2b2: condition named, cleanse implemented) |
| P-061 | bug | high | NPC speech never quoted: a storyteller only "begins/pauses" for 4 turns ending "Do you wait?"; an NPC's question is never printed so the player can't answer; a notice's words withheld for 4 tries | 181732-explorer 19–26; 181028-newcomer 25–39 | fixed (44d181e: narrator told to quote NPC words; open threads supplied as what locals tell); notice wording still yes/no only |
| P-062 | bug | low | Journal lists people and objects under "locations"; an entry cut mid-sentence | 181732-explorer 23–26 | fixed (44d181e) |
| P-063 | polish | low | Same-turn self-contradiction about an object (rings catch the light / no rings) | 181732-explorer 27–30 | open |
| P-064 | bug | high | Gentle talk framed as force: greeting a child → "Handle (Agility): turn the child's face" at 35% (recurrence of P-023); a bribe and a question bundled into one roll | 182337-talker inputs 22–30 | fixed (ea57355); ledger I-146 |
| P-065 | bug | med | NPC identity drift: "the child" became Falwen Underwort, a middle-aged man (roster/given-name reuse ignoring implied age) | 182337-talker inputs 23–26 | fixed (ea57355) |
| P-066 | bug | med | OFFER stakes text garbled and cut mid-word: "citing not no one is watching the cobbles where the folded paper lies w" | 183202-breaker inputs 27–28 | fixed (172b2b2) |
| P-067 | rules | high | Opening says "someone is missing" but never who; nothing in the store names them, so the hook stays empty for the whole session | 183858-fighter 18–30; 155118, 161320 (same) | fixed (00b6534: incident bound to a seed NPC with witnesses); ledger I-148 |
| P-068 | bug | med | NPC "answers" by repeating the player's own quoted line back as his dialogue | 183858-fighter inputs 20–25 | fixed (00b6534) |
| P-069 | bug | med | Narration names NPCs the PC was never introduced to ("Tikash" for "the figure") | 184224-explorer 27–30 | fixed (db07b1d, 4be967b); ledger I-149 |
| P-070 | bug | low | Journal "people you have met" lists NPCs not yet met | 185133-breaker 23 | fixed (db07b1d) |
| P-071 | bug | low | "what are my options?" answered with only "What do you do?" once (no LEADS) | 185133-breaker 18 | open (watch) |
| P-072 | bug | low | OFFER stakes "Source: pc s hand held" (raw predicate) | 185739-fighter 26–27 (on 0a0acdf, before 172b2b2) | fixed (3c6cbbf) |
| P-073 | bug | low | Possession contradicts itself across turns (pendant in her palm / not in her hand) | 185739-fighter 20, 31 | fixed (3c6cbbf: holder written on mention, checked) |
| P-074 | bug | med | Creation: "Wanderer?" at the way-of-life step became Soldier (the default) with no explanation | 190015-newcomer setup (10 notes) | fixed (036cd7f) |
| P-075 | bug | med | An NPC already agreed ("Yes" to meeting) yet the follow-up ask rolls at 50% with a closed-door risk | 185715-talker 28–31 | fixed (3c6cbbf: riding); ledger I-151 |
| P-076 | polish | low | Near-miss options 1 and 3 show the same cost text | 185715-talker 22 | fixed (3c6cbbf) |
| P-077 | bug | low | Garbled position text: "moved within Barrowburn… not in Barrowburn and can be found in the village" | 185715-talker 18 | fixed (3c6cbbf) |
| P-078 | polish | med | NPC repeats the same stock line every turn ("Mark me"); freshness covers images, not dialogue | 185715-talker 21–26 | fixed (3c6cbbf: freshness covers NPC lines) |
| P-079 | bug | high | Opening still falls back to one line in 7/27 runs; last reason always screen 12.2.7 "a part of the player's message is not answered" though the opening has no message; crowd reactions to the incident cut as unsourced | 7 runs (191540, 185715, 183858, 182337, 170207, 170200, 170157) | fixed (ec9470e): 7/7 recorded openings now narrate; ledger I-150 |
| P-080 | bug | low | A message with speech plus "what do I know so far?" handled only the speech | 191540-breaker 24 | open |
| P-081 | polish | low | NPC reply contains a stray quoted line that reads like a leaked hint ("Look at who's listening…") | 191540-breaker 23–26 | open |
| P-082 | bug | med | Repeated tracking loops with no progress ("the mist hides it, do you press on?"); an extended search never advances | 191941-fighter 24–29 | open (queued) |
| P-083 | polish | med | Cost form copied from the menu example, not fitted to the scene ("left on the far side, down the well, stuck in a beam" in a grassy field) | 191941-fighter 30–31 | open (queued) |
| P-084 | bug | critical | Crash loop: an Oracle answer stored as fact "wants" = True replaced an NPC's wants list; every later turn raised "'bool' object is not iterable" ("Sorry, something went wrong") until the run ended | 193315-breaker inputs 21–31 | fixed (Oracle never writes NPC list fields; readers skip non-lists) |
| P-085 | bug | low | Captain's name swapped to another NPC's ("Vesas de Morois") for one line; a horse appears from nowhere | 191535-explorer 29–31 | open |
| P-086 | polish | med | Three hidden Observe checks in a row give only vague results ("the shape does not come clearer"); the player learns nothing | 191535-explorer 19–26 | fixed (0c15da2) |
| P-087 | bug | med | REDIRECT option "Try it anyway" answered "You cannot do it that way" with no roll: dead end | 192159-newcomer 33 | fixed (0c15da2) |
| P-088 | polish | low | [CUT?] prompt appears after only a few exchanges, mid-conversation | 192340-talker 20 | fixed (0c15da2); ledger I-152 |
| P-089 | bug | med | At the near-miss menu Enter silently picked "Let it fail" (the OFFER re-prompt fix doesn't cover near-miss) | 192340-talker 28 | fixed (0c15da2) |
| P-090 | bug | high | PC's own kit not recognised: the sheet lists a rapier, drawing it → "your hand finds no blade", action rejected | 193420-fighter 24–30 | fixed (a31eabe) |
| P-091 | bug | low | Fallback "You try to garett's grip on her arm loosens" (possessive restatement) | 193420-fighter 27 | fixed (a31eabe) || P-092 | polish | low | "[CUT?] Move on or stay a while." doesn't say what Enter does | 194948-newcomer 35, 38 | open |
| P-093 | polish | low | Setup step 12 asks to keep/re-roll month names without showing them | 194948-newcomer 19 | open |
| P-094 | polish | low | A notice's lettering line repeats every turn (object text not covered by freshness) | 194948-newcomer 25–36 | open |
| P-095 | bug | med | Narrated cast not in the store: opening describes a herb-wife, officer, child, faction heads; engine treats only one NPC as present and they vanish; same NPC is "grieving old man" in prose but "the boatman" in OFFER/LEADS; LEADS say someone is "here with you" who never appeared | 195445-breaker 17–31 | fixing |
| P-096 | bug | low | "It works. Coming up the road agrees." (description phrase used as a name) | 194952-talker 20 | fixing |
| P-097 | bug | med | Journal/what-you-know garbled: "The poor quarter is at within Cornburn", "speech is said the journey's origin" | 194952-talker 31 | fixing |
