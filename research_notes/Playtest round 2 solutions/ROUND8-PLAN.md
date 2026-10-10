# Round 8 plan: approved fixes

Written 2026-10-10. Based on [ROUND8-ANALYSIS.md](ROUND8-ANALYSIS.md) and [ROUND8-PROPOSAL.md](ROUND8-PROPOSAL.md). The
evidence is in `round8-investigation/`:
- the traces I1–I3;
- the inventory D1 of code's orders to the narrator;
- the research R1 on NPC agency.

## Owner rulings (quote these in DL entries)
- On the analysis: "A lot of these problems seem to go back to the code forcing an incorrect view on the narrator."
  Then: "I think you're right about the deeper solution, I think it might be necessary. Let's think about it more,
  and potentially look for solutions for the trade-off."
- On the proposal: "I approve of A. I don't like the code telling us exactly what someone should say or how they
  should react if they're often wrong. And I really don't like the forced texture either."
- T2, T4, T5 and the patches follow earlier rulings (Principle VIII; ROUND7-PLAN). The owner was told they would
  proceed.

## 1. Fixes

**F-A. Facts, not orders (the proposal, option A).** This also covers T1, T3 and the forced texture.
- **Code tells the narrator only facts it owns:**
  - the roll and what it achieved;
  - state changes (coin, conditions, positions);
  - who is present and where (only those present and able: the dead, the unconscious and the departed are not
    listed);
  - clue deliveries;
  - each NPC's **mood** toward the PC, rolled once per scene (D3) and moved only by an event: payment, threat, insult
    or a won persuasion;
  - for a request, the **ceiling**: the most this person will do. It is looked up in the grid of mood × cost to them.

  | Mood \ cost to them | none | small | real | big |
  |---|---|---|---|---|
  | open | will help | will help | helps for a price | partial or refuses |
  | guarded | will help | helps for a price | partial or refuses | refuses |
  | closed | partial | refuses | refuses | refuses, may escalate |
- **The Reader adds two typed fields:**
  - the **addressee** of each speech or question part (an id, or none);
  - the **cost to the NPC** of an ask (none, small, real or big).
- **The narrator decides:**
  - who answers (the Reader's addressee, or its own judgment when none is given);
  - each NPC's reaction, at or below the ceiling;
  - the price, taken from the NPC's want;
  - the words;
  - whom a refusal points to, chosen from a list of real people code supplies.
- **Forced texture is retired:**
  - example gesture lists in refusal orders;
  - "quote exactly";
  - the mandatory closing line ("end by handing the moment back", P6);
  - activity lines that say nothing;
  - the unconditional "(answered)".
- **Code stops re-guessing:**
  - the addressee by word overlap and the "last spoke with" fallback;
  - the Talk → Grapple rewrite (`gate.covering_verb`): talk with menace stays talk (01.18.7);
  - the reading line guessing which written thing is read: it follows the beat's target;
  - casting by description.
- **State before reactions (T3):** payments are a consequence of the action, not a step on the reaction checklist.
- **Retires:**
  - `tbl.npc_action` as prose orders, and the practice clamp;
  - the "X acts: …" MUST lines;
  - T-12-18's response-row scene writes (one wrote "pointedly ignoring you" as a fact);
  - code-written refusals;
  - `npc_layer.addressed`'s heuristics.
- **Measurement and fallback.** Measure offline from logs, with a hand-checked judge:
  - the grant rate by mood and cost;
  - ceiling violations;
  - mood flips with no event;
  - repeat-ask consistency;
  - refusals that stay in character;
  - voice distinctness;
  - secret leaks.

  Baseline these on the round-8 saves first, then run the same seeded scenes three ways: today's code, dial and
  ceiling, and judgment only. If ceiling violations exceed 5%, add one small NPC-intent call before narration
  (research option 3).

**T2. Every lead and incident kind gets its terms when it is made.**
- The terms are held by the people and documents who would know.
- The incident's actor is the person on stage.
- The journal shows "what you were told", attributed to who said it.
- **P9:** one clue judgment per message, before the question cap. Clue delivery is a fact (the `learned` channel), not
  an NPC "acts:" line.
- **Retires:** one-sentence leads; the false "answered"; the journal's name-only lookup; per-part clue calls.

**T4. `/fix` can change how the message was read.**
- A rebuild may re-run the Reader with the Fixer's note.
- An undo re-shows the scene.
- The tools mark code-forced lines.
- The digest adds goal-first (01.2.2), the attribute knob (01.18.7) and licence glosses ("Push: spend Focus for
  reach").
- **Retires:** the odds-only rebuild.

**T5. Only precise checks block.** A check without a measured precision only logs, and code enforces that. The pronoun
check (0 of 3) and the repeat check (0–1 of 2) are demoted.

**Patches:**
- **P1:** a name leaked in RESULT (`oof.changed_line` skips `name_known`).
- **P2:** take the time charges minutes in free play, not intervals.
- **P3:** OFFER titles come from the act.
- **P4:** only mechanical costs make a frame "costly".
- **P5:** the lead injection takes the Director's pick.
- **P7:** "setting once" also applies on a scene cut at the same place.
- **P8:** RESULT and Fate wording.
- **P10:** the harness persona sees only new output (round 6's F7, never built).

## 2. Order and lanes
1. **Rules wave R2-L** covering all of the above.
2. **Engine specs**, at most two in parallel:

| Spec | Covers | Lane |
|---|---|---|
| **028** | F-A (incl. T1, T3, forced texture) + the agreeableness measures + baseline + 3-arm A/B | `npc_layer.py`, `roles/narrator.py`, `narration.py`, `handles.py`, `packet.py` (people card fields), the Reader (addressee, cost), `gate.covering_verb`, `world/social.py` (casting), `scene_state.py`, an eval script |
| **029** | T2 + P9 | `engine/gen/`, `answer.py` (clue routing, `learned` delivery), the journal, `world_seed.yaml` |
| **030** | T4 + T5 + P1–P5, P7, P8, P10 | `fixer.py`, `dispute.py`, `audit/` checks, `oof.py`, `necessity.py`, the time code, `evals/playtest.py` |

Specs 028 and 029 run first, then 030.
