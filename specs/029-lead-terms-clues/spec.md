# Feature spec 029: every lead and incident gets its terms when it is made (T2); one clue judgment per message (P9)

**Input**: `research_notes/Playtest round 2 solutions/ROUND8-PLAN.md` (T2, P9, the process fix); `ROUND8-ANALYSIS.md` §2 T2
("Why it recurred"); `round8-investigation/R8-I2-npcs.md` §2, §3, §6 X2, §11 B and C; `R8-I1-narration.md` §5-6;
`rules/_process/reports/R2-L-report.md` ("Spec 029" checklist); spec 025's `implementation-results.md`; constitution
VIII. Rules: 11.5.6 (terms for **every kind**), 12.16.16 (the incident's actor on stage), PR-15-6 step 7, 15.9.5,
PR-12-10 step 1 (one judgment per message), T-15-5 (questions), 12.10.8 item 1, 12.14.12 item 3, 15.9.16 (the
journal), T-15-15. DL-12-135, DL-15-43, DL-15-44, DL-15-45, DL-15-46; DL-15-39 as amended; DL-12-103, DL-12-109,
DL-12-119 revisited. Data: `investigation.yaml#journal` (`journal.told`, `lookup`), `social.yaml#delivery.information.
clue_judgment_first`, `pacing.yaml#answer_ladder.clue_judgment`.

**Owner rule after round 8 (binding)**: breadth cases are **enumerated from every kind the game's data has**, not
imagined. Round 7's fix covered the kinds round 7 happened to show and the cases we made up were the same kinds.

**Parallel lane**: spec 028 (facts, not orders: `npc_layer.py`, `narrator.py`, `narration.py`, `handles.py`,
`packet.py`, the Reader, `social.py`). Spec 030 comes after (`fixer.py`, `audit/`, `oof.py`). Not ours; hand-offs in
`implementation-results.md`.

## The kinds the data has (the enumeration the tests walk)

| Family | Source in the data | Kinds |
|---|---|---|
| Incident | `world_seed.yaml#tbl.12.seed.inciting` | 8: alarm, dying_messenger, missing, offer, theft, omen, refugees, duel |
| Opening lead: the situation's trace | `world_turn.yaml#situation_templates` (lead 2 is a step-1 trace) | 16: feud, sickness, road_of_knives, succession, hunger, hunting_ground, the_rite, war_comes, flood_and_fire, the_debt, the_missing, festival_trouble, cursed_ground, the_prisoner, scandal, the_enemy |
| Opening lead: the hire lead | `step13_opening` (the fourth faction) | 1 |
| Document | `world_seed.yaml#tbl.12.seed.document` | 4: hire, warning, charter, bounty |
| Lead-injection form | `oracles.yaml#tbl.lead_injection` (d12) | 12 |
| Rumor (`points_to`) | `step11_rumors` | 4: a faction's goal, a situation's trace, a site (true, partial, false words), the keeper's dream |
| Creation hook | `origins.yaml` micro-format, 02.9.7 | 7: thread, rumor, npc, place, debt, enemy, question |

**52 kinds** (8 + 16 + 1 + 4 + 12 + 4 + 7). `engine/gen/hooks.py` keeps one data entry per kind
(`world_seed.yaml#terms`), and a test walks the families above against the data so that a kind added to any table
without terms fails.

## User stories

### US1 - Every lead and incident kind gets its terms when it is made (T2; 11.5.6, 12.16.16)
When the seed makes its hooks (the incident, the three opening leads, the seeded notices) and when a lead is
injected, code decides the **terms** by kind: **who** (people by id, bound or cast or created), **what** (the act or
event, as data), **where** (a place bound or created), the **words** of any document or message (a `text` fact on a
document entity made at the same time; a spoken message as a field), and the **pay** where one is offered. They are
written as unsealed knowledge on the cards of the people who would know, and as the text of the documents that would
hold them. A term the case seals (a node's answer) is never written. Reading a document delivers its words because the
words exist when the document is made. One-sentence leads and reporter-only incidents are retired.
- **Accept**: K1-K52 (one per kind), P1-P3 (the gate log, the closed cart, the banners).

### US2 - The incident's actor is the person on stage (12.16.16; DL-15-43)
When the opening shows the incident's actor (the challenger, the one making the offer, the refugees' leader, the
rider), that person is the case's subject entity, cast into the opening **by id** in the incident's role with the
identity sealed (the scene knows them as "the challenger", never by name). The Director and the narrator no longer
invent the actor.
- **Accept**: P4 (the fighter's challenger), K-duel, K-offer, K-refugees, K-dying_messenger.

### US3 - The journal shows what you were told (15.9.16; DL-15-46)
"What do I know about X?" gains a **what you were told** section: the `said` records spoken to the PC, each attributed
("Betric told you: ..."), never as fact. The lookup searches thread text, said records and knowledge records, and
splits "X and Y". The name-only short-circuit and thread-name matching are retired.
- **Accept**: P5 (the winter and the banners), J1-J4.

### US4 - One clue judgment per message (P9; PR-12-10 step 1; DL-15-45)
One judgment reads **all** the message's question parts together and runs before the question cap. A clue it finds is
delivered **outside** the count, as a `learned` fact the narrator conveys (never an NPC "acts:" line, whoever of the
knowers is present); `deliver_count` then caps ordinary answers only. Per-part clue calls and first-question-wins
routing are retired. A question is marked answered only when a fact was actually delivered.
- **Accept**: P6 (Betric), C1-C10; precision and recall on the spec-025 set plus 20 new multi-part messages, Haiku.

## Out of scope / hand-offs
`npc_layer.py` (the "acts:" lines; `answer_line` still renders ordinary willingness), `narrator.py` (`_reading_lines`
of the target; the single-written-thing fallback), `handles.py` (renders `record.learned`; three lines added),
`turn.py` (the unconditional "(answered)" stamp is spec 028's), the audit's `b.learned` coverage (spec 030).

## Assumptions
- A1: The terms of the 52 kinds are authored as short data templates in `world_seed.yaml#terms` (tagged
  `[revision: R2-L]`); filled in code from ids and names; never a verbatim sentence to repeat (R2-K, 12.16.16).
- A2: The incident's node answers stay sealed. A term states what anyone present perceived, never the case's answer.
- A3: Lead injection and rumors made in play are written by the same function (`hooks.write_injection`), called from
  `pacing.inject_lead` (one line outside the lane).
- A4: The clue judgment's output gains `part` (which question the clue is about), so the other parts are still
  answered ordinarily; when it is `none` every part stays ordinary.
- A5: Creation hooks (02.9.7) bind to the PC's bond NPCs; with no bond they are the PC's own notes (no knowers).
