# Traceability — Chapter 05 (Abilities, Focus, and Magic)

| Clause | Requirement (short) | Satisfied by (rule ids) | Status |
|---|---|---|---|
| I | The AI DM executes all mechanical resolution through its instruments | 05.4.1 (`use_ability`), PR-05-1…PR-05-8; every cost, use, rank, budget, miscast and composition is `[D]` | satisfied |
| II | Custom ruleset exploiting AI capacity for complexity | 05.3 (30-field record), 05.10 (regimes, ranks, spread order), 05.11 (script-checked budget), `data/abilities.yaml` (251 entries, 499 ranks) | satisfied |
| III | Flexibility within bounds; no narrative override; judgment by default for exceptions | 05.5.2 Stretch, 05.5.4 Emulate, 05.7.6 Small working, 05.8.4 Rite design: each a `[J:flag]`/`[J:rung]` with a worst-case line and a fixed price; 05.5.3 the cannot list; 05.5.6 precedent | satisfied |
| IV | v1 single-player, text-only | allies' abilities act only through the PC's command action (05.4, Interface to 06/16); no party-economy rules | satisfied |
| V | Closed primitives: fixed slots × bounded pools | 05.2.1–05.2.2 (20 slots, closed), 05.3.2 (eight forms), 05.6.2 (five cost bands), 05.6.8 (six flares), 05.10.4 (five spread tags), 05.11.6 (pool sized by coverage), 05.8.1 (24 rites + bounded design) | satisfied |
| VI | Mandatory, telegraphed consolidation; provisional by default; a squish is not retirement | 05.3.9 (ranks restate), 05.2.5 (replace), 05.2.6 (shelve, forget), 05.2.10 (provisional abilities), 05.12.1–05.12.3 (eight moves; content lifecycle; fold into base); every data entry `lifecycle: provisional` | satisfied |
| VII | Default-deny capability gate; licensed or redirected, never narrated into existence | 05.1.1 (an ability is a license read literally), 05.5.2/05.5.4/05.5.5 (the three priced ways past scope; every license has explicit `principle`, `stretch`, `emulate`, `crude_fallback`), 05.9 (81 training licenses with fallbacks and paths), 05.7.9 | satisfied |
| P2 | History-gated power; a baseline floor before any calling | 05.2.4 (acquired slots open to all), 05.6.7 (the push: Focus matters with no ability), 05.9.2 (expert and master only from calling tiers), 05.6.1 (pool grows with tier) | satisfied |
| P3 | Every piece of state classified background vs player-facing | State touched: visibility of slots, uses, Focus (shown), witnessed and budgets (available), others' effect DCs (sealed) | satisfied (the comprehension wall itself is waived by BRIEF §3; DL-05-29) |
| P4 | Breadth of access is not day-one power | 05.2.4, 05.3.9 (acquired abilities are rank 1), 05.9.3–05.9.4 (training gives +2 and the lowest grade, at a month each); WE-05-2 | satisfied |
| P5 (pool) | A calling hands out no ability list; a hard total-slot ceiling | 05.1.1, 05.2.1, `data/abilities.yaml` (one pool, tag-gated; picks are 04.8.4's) | satisfied |
| P5 (passive / active) | Passive: no usage state; active: explicit recharge, mechanically tracked and enforced | 05.3.3, 05.3.4, 05.4.6 (seven recharge types, each with a registered handler), 05.4.2; `data/boundaries.yaml` owner-block 05 [verification: V2a-016] | satisfied |
| P5 (gate→fill) | Specific abilities from source and method go through the one generator | 05.2.1 (gift, absorbed), DL-05-05 (mirrors of `gen.absorb`); item abilities are 08's | satisfied (by reference) |
| P6 | Named composites for aligned pairs; priority-ordered behavioral tags for the rest | 05.10.6 (`composites.yaml`: 22 entries on three low-cardinality key kinds; 32 more are 04's), 05.10.3 (rank bands), 05.10.4 (ordered spread tags) | satisfied |
| P7 | Player-facing reference layer | Interface to 14: Abilities, Focus, Shelf and learning, Rites, Training views; 05.3.6 (verbatim text) | satisfied (rendering is 14's) |
| P8 | Deterministic degrees of success | 05.3.5 (aimed and resisted checks through the frame), 05.7.5 (miscast keyed to the degree), 05.8.2 (rite steps read by degree) | satisfied |
| P9 | Fixed action economy; one shared Focus pool for every active ability | 05.6 (one pool; five cost bands; no second resource), 05.6.10 (identity through generation), 05.4.3 (one rider per beat), 05.5.3 item 7, INV-11 honored throughout | satisfied |
| P10 | Precisely scoped permissions may carry core power; no vague triggers | 05.3.1–05.3.6 (form, literal positive text, fixed triggers), 05.3.3 (fiction clauses reduced to one flag, tie-break false) | satisfied |
| P11 | No unaudited shared point-buy | abilities are picked or learned, never bought with points; 05.11 audits every entry against one formula | satisfied (n/a to purchase) |
| P12 | Limitation / weakness / cost as independent levers | 05.3.1 (separate fields), 05.11.2 (each lever a separate allowance term), 05.7.2 (branch signatures in the three fields), 05.6.12 (the reserve's three fields) | satisfied |
| P13 | Tools own mechanics; external state; independent verification | State touched (all state in the store; `use_ability` validates); 05.3.6–05.3.7 (packet text and `narration_may_not_imply` for `check_claims`) | satisfied (architecture is 00/12's) |
| P14 | Cadence may differ by calling, never as extra actions | not used here; identity lives in Focus generation (DL-05-29 d) | deviation recorded |
| P15 | Time-gated breadth as an alternative to point audit | 05.8.5 (learning clocks), 05.9.4 (training clocks; no cap but time) | satisfied |
| P16 | Always an actionable next step | every refusal by `use_ability` names its reason and a path (05.4.1, 05.5.5, 05.7.4, PR-05-5 step 1) | satisfied |
| P17 | Graduated delivery | abilities that reveal use delivered reach and ch.01's DELIVER (`ab.read_sign`, `ab.reconstruct`, 05.7.7 sensing ladder) | satisfied (mechanism is 01's) |
| 00.17.1 Q1 | 05 owns Focus entirely; 07 owns rest and passes quality | 05.6.9, PR-05-4, `h.05.focus_recover` | satisfied |
| 00.17.1 Q2 | 05 owns the ceiling and three partitions (12–24) | 05.2.1–05.2.9 | satisfied |
| 00.17.1 Q20 | 05 owns magic as a subsystem; 13 owns canon | 05.7, 05.8; 05.7.10 lists what canon must supply | satisfied |
| 00.17.2 row 05 | slot system; template grammar; `abilities.yaml`, `rituals.yaml`, `composites.yaml`; `use_ability`; Focus; recharge types; magic; ability modifiers | 05.2; 05.3; the four data files; 05.4.1; 05.6; 05.4.6; 05.7–05.8; 05.6.8 flares and 05.10.4 spread tags (the modifier family) | satisfied |
| BRIEF A2 #6, #12, #13 | shared substrate; creativity in bounded currency; refusals are lookups | 05.10; 05.5.2, 05.6.7; 05.5.5, 05.9.4 | satisfied |
| R4 SG-15 | positive-scoped, literal effect text | 05.3.6; generator lint on every rank text | satisfied |
