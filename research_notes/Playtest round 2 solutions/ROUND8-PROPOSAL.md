# Round 8 proposal: code gives the narrator facts, not orders

Written 2026-10-10, after the owner asked to explore the deeper fix behind round 8's T1 and T3. Evidence:
- `round8-investigation/R8-D1-narrator-orders-inventory.md`: every instruction code gives the narrator, checked
  against 85 narrator calls from rounds 7 and 8;
- `R8-R1-npc-agency-research.md`: how tabletop and AI-NPC designs keep characters from becoming pushovers, with
  sources.

## 1. What the inventory found
- Code gives the narrator **46 kinds** of instruction. 15 are pure facts code owns (dice results, state changes,
  presence, clue deliveries), and 5 more are facts with an order tacked on. **19 are code's guesses about judgment**:
  who reacts, and how. 6 are forced texture or style.
- **The guesses about how NPCs react are right only 8 of 24 times (33%):**
  - table rows: 1 of 4;
  - recorded refusal or want: 0 of 2;
  - clue and pointer answers: 2 of 5;
  - bystander reactions: 0 of 5;
  - "quote exactly": 0 of 6.
- **The narrator obeys every order.** All 145 must-say lines were covered, and every wrong one was narrated as ordered.
- **Left to itself, the narrator chose well:** when code gave no NPC order, it picked the right speaker 14 of 14
  times, including a turn where code found nobody.
- **Who-is-addressed is better than thought,** at 40 of 45 (89%). The damage comes from the reaction orders.
- **Forced texture:**
  - every refusal order carried an example gesture list, so all 8 refusals used the same hand gesture;
  - 64% of activity lines say nothing;
  - "(answered)" is stamped on every question.
- **Unmeasured:** how agreeable NPCs are when the model decides. A hostile NPC with no order never came up.

## 2. What the research found
- No study measures NPC agreeableness in an AI game master. The nearest ones (persona sycophancy, multi-turn caving,
  simulated customers, negotiation bots) all point the same way: models cave and over-agree, especially under repeated
  pressure. A prompt saying "you may refuse" fixes the average, but not *who* should refuse. So some of the stance
  must live outside the model.
- Tabletop agrees on three points:
  - a disposition is rolled once and moves only on an in-fiction event;
  - how big the ask is *for the NPC* matters;
  - the NPC's want supplies both a price and a reason to refuse.

## 3. The proposal (research option 1, "dial and ceiling")
**Code tells the narrator facts:**
- the roll and what it achieved;
- what changed (coin, conditions, positions);
- who is present and where;
- clue deliveries;
- each NPC's **mood toward you**, rolled once per scene by dice (the existing D3 ruling) and moved only by an event:
  payment, threat, insult or a won persuasion;
- for a request, **the most this person will do**: a ceiling from a small grid of mood × how big the ask is for them.

| Mood \ cost to them | none | small | real | big |
|---|---|---|---|---|
| open | will help | will help | helps for a price | partial or refuses |
| guarded | will help | helps for a price | partial or refuses | refuses |
| closed | partial | refuses | refuses | refuses, may escalate |

**The Reader** (already running) adds one field: how big the ask is for the NPC (none, small, real, big).

**The narrator decides:**
- who answers;
- how each NPC reacts, at or below the ceiling;
- the price they name, from what they want;
- their words, and who they point you to when they refuse (from a list of real people code supplies).

**Examples:**
- *A wary dockhand asked to watch your cart overnight* (guarded, real cost). Ceiling: partial or refuses. "After the
  bell the dock master walks it himself. Come at first light and I'll tell you what the night watch says."
- *A friend asked to lie to the watch for you* (open, real cost). Ceiling: helps for a price. "I'll say it. You'll owe
  me, and you'll tell me why." If her card says she never lies to the watch, she refuses, in her own voice.
- *A hostile guard offered a bribe* (closed). The payment is an event, so his mood moves one step, and the bribe now
  reaches "partial". He pockets the coin and looks away for a count of a hundred, no longer. Code moves the coin; the
  narrator writes the scene.

**Cost:** no extra model calls.

**Retires:**
- NPC reaction tables as orders;
- "X acts: answers…" must-say lines;
- code-written refusals and gesture lists;
- word-matched addressees;
- "quote exactly";
- the unconditional "(answered)";
- empty activity lines.

This also replaces most of round 8's T1 and T3 patching: a dead NPC simply isn't in the scene's "present" list, and
nobody is ordered to flee.

## 4. Guarding against pushovers, and how we'll know
Measured offline from logs, with a hand-checked judge:
- how often asks are granted, by mood and size;
- how often the narrator goes over the ceiling;
- mood flips with no event;
- the same ask repeated, to check consistency;
- refusals that stay in character;
- voices that stay distinct;
- secret leaks.

**Plan:**
1. Baseline these on the round-8 saves.
2. Run the same seeded scenes three ways:
   - today's code;
   - dial and ceiling;
   - judgment only, as the comparison.
3. **Fallback:** if the narrator goes over the ceiling more than 5% of the time, add one small "what does this NPC
   intend" call before narration (research option 3).

## 5. What this changes in the rules
This revises 12.11.4 and 12.11.9 (the default NPC layer: today code decides reactions), so it needs the owner's
approval.
