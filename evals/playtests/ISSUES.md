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
| P-012 | bug | med | A critical failure is announced ("goes badly wrong") but the player never learns what happened | 20261007-155118 turn 6 | fixing (OFFER/roll fixer) |
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
| P-023 | bug | high | Intent substitution: "I shout at the travellers to state their names" became an OFFER to wound the nearest traveller; offers drift Talk(Presence) → Talk(Might) → Strike without the player asking | 161325-fighter inputs 29–40 | not seen on 12f51f2 (watching); one Talk offer for a climb (170318 input 22) |
| P-024 | polish | med | Trivial acts get a full odds screen (opening an unbarred wicket "easy obstacle"); a shout at 35% with 20% critical failure; a retry shows worse stakes but better odds | 161325-fighter inputs 29–32 | open |
| P-025 | bug | high | A successful Talk to learn something (the old enemy's name) never reveals it: narration fell back to "responds as the talk went: success", so the player asked again and got a second OFFER | 161323-talker turns 5, 9; 170157-breaker 24–28 | fixed (d06505c); naming a new person still needs a rules path (I-140c) |
| P-026 | bug | high | An addressed NPC's reply is cut as "no source for this act" (Bixok repeats the question back); background figures' acts still cut by code when the Checker extracts them | 170157-breaker turns 6, 9, 10, 12; 170200-newcomer; 170207-talker (every conversation stalls) | fixed (d06505c); ledger I-140 |
| P-027 | bug | med | [OFFER] leaks internals: "source: fact.203", "target not yet chosen", "free OFFER", raw OOC text; wrong pronoun ("her" for a he/him NPC) | 170157-breaker inputs 19–26 | fixed (af1fdce) |
| P-028 | bug | med | A question at an open pause ("what does 'Go big' mean?") gets a generic note and the same OFFER reprinted; "Play it safe" unexplained; no Enter default shown | 170157-breaker inputs 19–28 | partly fixed (af1fdce); rest fixing (OFFER/roll fixer) |
| P-029 | bug | low | "What do I know about the stranger" folded into a Move roll offer; journal says "nothing yet" after learning things | 170157-breaker inputs 30–31 | fixed (03a9ba7) |
| P-030 | polish | low | Narration repeats the same scene details turn after turn (the wiped counter, wet wool, the murmur) | 170157-breaker 22–29; 172452-breaker 27–31; 174833-newcomer 28–36 | fixed (74f7749: freshness 12.14.11) |
| P-031 | bug | high | Basic talk refused: "talk to the person on the bridge" / "press him gently" → "[REDIRECT] needs Stonesense, which you have not learned" | 170200-newcomer turns 4–10 | fixed (1e3ec97); ledger I-139 |
| P-032 | bug | high | Declared movement ("I walk out along the bridge", "go closer", "head into Mossfield") writes no position, so arrival narration is cut as unsourced | 170200-newcomer turns 5–16; 170318-fighter turns 13, 16 | fixed (1e3ec97); ledger I-139 |
| P-033 | bug | low | NPC called both "they" and "him" in narration | 170200-newcomer turns 8–14 | fixed (1e3ec97) |
| P-034 | bug | med | Internal note in narration: "(Her claim about the ankle is context only)" | 170318-fighter input 28–30 | fixed (17eebe7) |
| P-035 | polish | med | A failed beat doesn't show what it cost or what happened ("the press holds you", an ankle "holds" you); "Go big" raises stakes with no stated gain | 170318-fighter inputs 19–27 | open (with P-012, P-028) |
| P-036 | bug | med | Narration says "Edda is not your friend" though the sheet lists Edda as the PC's friend (creation bond does not reach the NPC's standing?) | 170207-talker turns 13–15 | fixed (be20402); ledger I-142 |
| P-037 | polish | low | Named NPC drifts back to "a woman" / "stranger" after being named (Bixnik Quick-Fingers) | 170207-talker turns 10–15 | open |
| P-038 | bug | high | "What do I know about the land around Hawkstead?" read as a Mind sorcery attempt → REDIRECT for lacking the spell; plain "what do I know?" only repeats scene text (with P-019) | 170204-explorer inputs 20–23 | fixed (1e3ec97) |
| P-039 | bug | low | Garbled Oracle twist fragment in narration: "Can say it in answer to a question asked aloud, but lesser"; PC referred to in third person ("he asks") | 170204-explorer inputs 25–26 | fixed (17eebe7), except PC as "he" after a You-sentence |
| P-040 | bug | high | Fallback mangles restatements: "You try to gerella is pinned against the gatepost", "Knows where … can not be found"; "It works." before any roll | 172629-fighter inputs 19–31 | fixed (17eebe7) |
| P-041 | bug | med | Narration contradicts itself across turns: a notice reads "NO QUESTIONS ASKED", a later turn says it does not (mentioned object's text not stored or not shown back) | 172552-newcomer inputs 27–35 | fixed (be20402) |
| P-042 | polish | low | "What do I know" answers show raw Oracle predicates ("name — yes") | 03a9ba7 fixer report | fixed (44d181e) |
| P-043 | bug | low | Sheet shows a raw placeholder: "carries the fact teaches: <the gifted spell>" | 174833-newcomer input 23 | fixed (74f7749) |
| P-044 | polish | low | OFFER's Enter default is Withdraw; a newcomer pressing Enter backs out without noticing | 174833-newcomer inputs 26, 31 | fixing (OFFER/roll fixer) |
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
| P-057 | bug | med | "Change approach" re-shows the offer with changed odds and never asks for the new approach; "ask nicely, no coins" still framed as offering coins; attribute switched to Intellect | 181158-breaker inputs 20–24 | fixing (OFFER/roll fixer) |
| P-058 | bug | med | Learned facts rendered raw: "coin named none yet: yes", journal "Bixok Lucky: coin named none yet — yes (told)", entries truncated "one of…" (with P-042) | 181158-breaker inputs 23–28 | fixed (44d181e: one fact_sentence helper) |
| P-059 | bug | med | "Spend my Fate point" at an OFFER: no answer whether it was spent; no result shown | 181158-breaker inputs 29–31 | open (with P-047) |
| P-060 | bug | high | Condition-blocked moves: "[REDIRECT] Not as tried: 1 prevents it right now" (the condition's name replaced by "1"), printed twice; player never told what blocks them or how to clear it; same climb refused 4 times | 181737-fighter inputs 21–30 | fixing (OFFER/roll fixer) |
| P-061 | bug | high | NPC speech never quoted: a storyteller only "begins/pauses" for 4 turns ending "Do you wait?"; an NPC's question is never printed so the player can't answer; a notice's words withheld for 4 tries | 181732-explorer 19–26; 181028-newcomer 25–39 | fixed (44d181e: narrator told to quote NPC words; open threads supplied as what locals tell); notice wording still yes/no only |
| P-062 | bug | low | Journal lists people and objects under "locations"; an entry cut mid-sentence | 181732-explorer 23–26 | fixed (44d181e) |
| P-063 | polish | low | Same-turn self-contradiction about an object (rings catch the light / no rings) | 181732-explorer 27–30 | open |
| P-064 | bug | high | Gentle talk framed as force: greeting a child → "Handle (Agility): turn the child's face" at 35% (recurrence of P-023); a bribe and a question bundled into one roll | 182337-talker inputs 22–30 | fixing |
| P-065 | bug | med | NPC identity drift: "the child" became Falwen Underwort, a middle-aged man (roster/given-name reuse ignoring implied age) | 182337-talker inputs 23–26 | fixing |
| P-066 | bug | med | OFFER stakes text garbled and cut mid-word: "citing not no one is watching the cobbles where the folded paper lies w" | 183202-breaker inputs 27–28 | fixing (OFFER/roll fixer) |
| P-067 | rules | high | Opening says "someone is missing" but never who; nothing in the store names them, so the hook stays empty for the whole session | 183858-fighter 18–30; 155118, 161320 (same) | logged I-145; fixing (bind to existing seed NPCs) |
| P-068 | bug | med | NPC "answers" by repeating the player's own quoted line back as his dialogue | 183858-fighter inputs 20–25 | fixing (with P-067) |
