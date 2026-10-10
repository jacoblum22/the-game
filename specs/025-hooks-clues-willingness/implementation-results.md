# Implementation results 025: hook terms (T2), clues by judgment (D2 A), willingness held for the scene (D3 A), P3

Branch `worktree-agent-ad128472db2850290`, built on `milestone-1-playable` f661721 (R2-K, specs 023 and 024 merged).
Cases and the labelled clue set committed first (c4b2fc4), implementation 00161db, results after. Real numbers;
nothing faked.

## Trace (before design; round-7 saves, read-only)
- Fighter turn.2-4: Magby holds the core placement "who makes the offer: Tobby Applefoot"; nothing authored the job,
  pay or place. His speaker card held three seed-pack items and nothing about the offer.
- Talker turn.9: `case_about` matched "sign" in "signed" against the omen's subject "a sign of the rite" and wrote a
  pointer line for a non-holder.
- Explorer turn.2: Branine (core holder) asked about the refugees; `case_about` needed two incident words and had one.
  Turn.3: the Director's `new_npc` cast a random labourer (Roswen); the refugees were no entity. Turn.8: Roswen's
  dice refusal was voiced with the model's redirect to Morga, the only other person present.
- Talker turn.10/11: per-topic willingness re-roll (refused, then answered in full one turn later).
- No deal had a price; the only coin moved came from a regex on Framer prose.

## What was built
| Fix | Where | What |
|---|---|---|
| T2 hook terms | `engine/gen/hooks.py` (new), `gen/case.py` | At the seed's store write (and for a case built in play) each hook's terms are decided in code: offer (task, destination site, pay = job fee of the site's ring band), missing (bounty pay = band-1 job fee, issuer the rulers), refugees (a group entity "the refugees" at the place they arrived), the hire lead (task from its notice, destination, pay, issuer, contact = the faction head), a seeded bounty notice (pay, contact). Written as meta `world.hook_terms` (typed) and one data fact per hook known by its knowers, so it is on their speaker cards: `the offer of work: work: escorting a cart; pay: 85 coins (a job fee); where: The Tower of Falmouth`. A term the case seals (the offer's issuer) is never written. |
| T2 data, not sentences | `_seed_steps.py` + reference `12-world-seed.py` (parity kept; example regenerated) | Lead "X is hiring" (no "and asks no questions"); the situation rumor/lead without "folk say it is only the beginning"; officers' role `officer` (faction in `member_of`). `tbl.12.seed.document` reward rows coin-free `[revision: R2-K]`: the figure is the typed term. |
| D2 A | `engine/dm/roles/clue.py`, `prompts/clue.md` (new), `Role.CLUE` (base, schema `{about: none\|1-4}`, default none, offline stub, token cap, no cards) | `answer.clue_case`: one small call over the question, the last exchange and the about lines of each case's open node (held ones marked `*`, never the answer); held -> code delivers the clue; not held -> the non-holder's pointer to the holder. Asked about the subject by id: no call. Replaces `case_about` in asking and in the Recall look (`world_step.py`, one line). `case.about_line` derives the line (node question + the matter), or uses a placement's authored `about`. |
| D3 A | `engine/dm/answer.py` | `willingness()` decides the band at the first ask in a scene and holds it (meta `answers.willingness`); a resolved Talk on the NPC (won persuasion, accepted payment, a threat that worked) holds `willing`; a standing change this turn (insult, threat, harm) re-decides; a recorded refusal refuses its topic only. An unwilling answer carries one pointer (`refusal_pointer`: a cast person whose role or pack knows the topic, never the asked or anyone who refused on it; none when nobody is left). The index no longer stores a band per topic. |
| Typed deal price | `resolve/change.py`, `npc_layer.py` | `deal_price(rules, size, stated)`: the stated amount kept inside the price band of the request (R1..R5 -> bands 0..4), else the band floor; `pay_deal` writes the price record `{payer, payee, kind, amount, due, paid}` and the coin change. An accepted offer pays it in `respond`. `change.pay` (the regex on Framer prose) is a no-op shim. The Reader's `player_quantity` reaches the record (`adjudication.py` field, one line in `turn.py`). |
| Guards | `narrator.py` (record lines), `testimony.py`, `places.py`, `social.py`, `director.py`, schema + prompt | "others have said on this" after each speaker card; a coin figure in a claim never settles as a fact (route `price_band`); a true settled claim that a person/group is at a known place moves them there; a place known only by name is a passage away from town and becomes a building of that settlement on arrival; Director `next_scene.cast_described` casts the named person or group present (existing first, else a new group for a plural, else a walk-on with that role), and `new_npc` is not used when a description is given. |
| P3 | `npc_layer.py` | A greeting or thanks only (a narrow pattern) gets no willingness line, no refusal voicing, no speaker card. |

## Retired
`case_about` (word-overlap case routing); per-topic willingness re-rolls; the regex price from Framer prose
(`change.price`, `_PAID`, `_COIN`); random walk-ons for a stated purpose; the willingness line on a greeting; the lead
sentences "…, and asks no questions" and "folk say it is only the beginning"; the role string "officer of {faction}".

## Gates
| Gate | Result |
|---|---|
| Full suite | **1887 passed, 4 skipped** (after the last change) |
| Replay | re-recorded (`offline_seed11`); passes |
| ruff / pyright (touched files) | 0 / 0 (pyright with the project interpreter; `turn.py:579` has a pre-existing optional-access error, not touched) |
| Validator | **0 ERROR / 0 WARN** (INFO only) |
| Seed parity (`test_world_seed_parity`) | passes (reference script mirrored; example regenerated, output text unchanged) |
| `longhorizon.py --mode scripted` | **0 engine errors** (384 turns; `longhorizon_scripted.txt`) |
| Clue judgment, Haiku, 36 labelled items (18/18, labelled before the run; prompt examples disjoint from the set) | **precision 0.94 (17/18), recall 0.94 (17/18)**, accuracy 0.94 (`clue_eval_haiku.txt`). Misses: "Which way did they come from?" (way on) judged no; "Do you trust the captain of the gate?" judged yes. |
| Round-7: Magby (fighter) | card before: 3 pack items, no job; after: `the offer of work: work: escorting a cart; pay: 85 coins (a job fee); where: The Tower of Falmouth`; "who is really making this offer?" delivers node 1 (Tobby). **Pass** |
| Round-7: explorer | turn.2 Branine asked about the refugees: **clue delivered** (round 7: not routed). Turn.8 Roswen: Haiku judged it about the refugees case, so the non-holder points to Branine, the core holder (**never Morga**). The refugees exist as a group at the gate; `cast_described: ["the refugees"]` puts them in the scene. **Pass** |
| Round-7: talker "signed"/"sign" | judged none; an ordinary willing answer, **no case pointer**. **Pass** |

Round-7 gates: `replay_r7.txt` (Haiku). Cases: `tests/engine/test_spec025_cases.py`, 22 tests.

## Made-up and edge cases, one by one (labels in `cases.md`)
C1 bounty terms + last seen improvised, pass (plus a seeded bounty notice, pass) · C2 "Did he have enemies?" delivered,
pass (live: Haiku yes) · C3 Director casts the refugees, and a new "carters" group, pass · C4 weather judged no, pass ·
C5 everyone refused: no pointer, pass · C6 "ten silver for the map" -> 5 (band 1), pass · C7 payment moves guarded to
willing, no re-roll, refusal stays on its topic, pass · C8 "Thanks, friend": no line, pass · C9 Guarded holder
delivers, pass · C10 others' testimony on the card, pass · C11 no loop back to a refuser, pass · C12 hire with no stated
pay has a job fee on every knower's card, pass · C13 heard place reachable and realised as a building on arrival;
settled location moves the group, pass · C14 "evening prayers" judged no, pass (live: Haiku no) · C15 Unfriendly holder
delivers, pass · C16 "signed" not routed, pass (live: Haiku no) · C17 Magby pay and place, pass · C18 Roswen points
onward, pass · C19 "buy you a cup": 1 coin, price record, willing, pass · C20 the offer's issuer never on a card, pass ·
C21 3 inside the band stays 3, pass · C22 band held in a scene (one roll), new scene rolls again, pass · C23 won
persuasion holds willing, pass.

## Live (Haiku engine, Sonnet player, 15 turns, `--quick-setup`; `measure_live.txt`)
| | Talker (`playtest-20261009-220039-talker`) | Explorer (`playtest-20261009-220047-explorer`) | Round 7 (same personas) |
|---|---|---|---|
| Clue judgment calls / judged about a clue | 5 / 0 (none of the questions was about "who leads the refugees") | 5 / 4 | (word overlap) |
| Clues delivered (case nodes found) | 0 | **2** (both nodes of the missing-child case) | 0 and 0 (0 of 38 questions in 3 runs) |
| NPC answer lines; walls (refusals) | 4; **4** (the refugees group, Wary, unwilling held for the scene) | 6; **0** | talker 11, 1 wall; explorer 8, 1 wall |
| Refusal loops | **0** (pointers: Yipoo the Patient, Maga Tumbottle; new people) | **0** | 1 (Roswen -> Morga) |
| Unpriced deals | **0** (1 accepted offer, a typed 1-coin price paid) | 0 (no offer) | 3 of 3 unpriced |
| Contradicting improvised details | 0 topics with 2+ speakers | 1 topic, read: Zzioo "couldn't put a name to" the child and sent the PC to Kerbert, who named him; consistent | — |

Read by hand: the talker's four walls came from one group asked four times in one scene, held unwilling (D3 as
ruled), each refusal pointing to someone new. The player found the pointer gave a name but not where: the pointer now
also says where the person is found (`found at …`, after the run). Other complaints in the runs are outside this lane
(below).

## Anti-pattern check (handoff §3.3)
- Code authoring narrative truth: the card line is the hook's typed terms rendered as fields (owner-approved T2); the
  refusal pointer is the rule's one code pointer (DL-12-119). No sentence is pushed into every packet.
- Over-triggering: one CLUE call per question while a case has an open node (5 per 15-turn run).
- Low-precision checks that block: none block. Two word patterns decide small things and are named: the greeting
  pattern (only drops a willingness line) and the coin-figure pattern (only keeps a figure out of a settled fact).
- Blind calls: the CLUE call sees the question, the last exchange and the about lines.
- Mechanics as text: the regex price is retired; deals are typed records and quantity changes.
- Test traps: the labelled set was written and committed before the prompt was run; the prompt's examples are not in
  the set; nothing was tuned after the measurement.

## Hand-offs
- **Pipeline (023's lane)**: `resolve/pipeline.py:415, 846` still call `change.pay(…)`, now a no-op: remove both calls.
  The move OFFER/plan prompt said "go to the ford" for a move to the gate (live explorer, `/fix` twice).
- **Narrator prompt**: R1's narrowing of "Do not invent … what someone knows" to "a character may say what they
  believe" is not in this lane.
- **Spec 026 (people card / `packet.py`)**: the speaker card shows hook terms through the existing knowledge-fact
  path (`topic.hook.terms.*`); the "others have said on this" block is added in `narrator.speaker_cards`. If the
  shared renderer replaces `speaker_card`, keep both.
- **Rules (ch.12)**: WE-12-11 quotes the old lead "a savaged ewe; folk say it is only the beginning".
- `WILL_WORDS` "from what they know" keeps a plural "they" (024's pronoun fill covers their/them only).
- `engine/dm/turn.py` (1 line) and `adjudication.py` (1 field), `world_step.py` (1 line), `base.py`/`gemini.py`/
  `offline.py`/`cards.py`/`evals/gemini_smoke.py` (the role entry) were touched outside the listed lane, minimally.

## Assumptions
As recorded in `spec.md` A1-A8.
