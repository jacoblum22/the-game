# Traceability — Chapter 06 (Conflict)

| Clause | Requirement (short) | Satisfied by (rule ids) | Status |
|---|---|---|---|
| I | The AI DM executes all mechanical resolution through its instruments | 06.1.1, 06.2.2, 06.4.3, 06.4.6, 06.9.2, PR-06-1…PR-06-10: budget, order, bands, attacks, harm, morale and chases are `[D]` tool operations; adversary rolls are engine fortune checks | satisfied |
| II | Custom ruleset exploiting AI capacity for complexity | 06.3 (bands, links, groups, ten flags, eight feature kinds), 06.7 (27 conditions with three voices), 06.8 (six shapes), 06.9 (behavior evaluation, attention), T-06-9 (forty anchors), `data/conflict.yaml` (44 keys) | satisfied |
| III | Flexibility within bounds; no narrative override; judgment by default for exceptions | 06.5.10 (environment use: `[J:enum]` anchor choice, two-knob limit, logged ruling), 06.3.8 (feature classification), 06.4.10 (called shots), every `[J]` with a worst-case line; 06.9.7 (no hidden adjustment) | satisfied |
| IV | v1 single-player, text-only | 06.1.1 (one PC's budget; companions have no turn), 06.3.1 (position as named relations in words, no map), 06.10 (the solo curve), T-06-13 | satisfied |
| V | Closed primitives | T-06-1 (one cost table), T-06-4 (ten flags), T-06-6/T-06-7 (six weights, twelve properties, two per item), T-06-10 (27 conditions), T-06-15 (six shapes), 06.4.10 (six calls), 06.14.4 (five standing orders), 06.13.2 (ten objectives) | satisfied |
| VI | Consolidation; provisional by default | every entry of `data/conditions.yaml` and `data/conflict.yaml` ships `lifecycle: provisional`; 06.13.4 (conflict state is cleared, never accumulated); 06.7.4 (control counter resets) | satisfied (content scale) |
| VII | Default-deny capability gate | 06.4.3 decision 1 (out of reach → G4 with a redirect), 06.15.2 (mounted combat licensed; the license's crude fallback), 06.3.7 (hiding gated on cover or a veil), 06.3.10 (size → G4 with redirects), 06.5.10 (unestablished features go to the Oracle, never granted), 06.11.7 (a foe that will never yield: G4 with what it would accept) | satisfied |
| P3 | Rich background state; every piece classified | 06.3.1 (bands, flags: shown), 06.9.3 (attention score: background), 06.9.6 (stat blocks sealed; tells), 06.11.1 (morale clock: sensed), 06.12.2 (chase clocks: public), State touched | satisfied |
| P6 | Named composites and priority-ordered behavioral tags | 06.8.1 / T-06-15 (one fixed order of shapes), 06.6.4 (`slot.defense_reaction`: Fend at rank 0, replaced by higher claims) | satisfied |
| P8 | Deterministic degrees of success | 06.4.3, 06.4.6 (critical = one more reach rung = one severity rung), 06.5.2–06.5.3 (reach ladders), 06.12.3 (ticks = delivered reach) | satisfied |
| P9 | Fixed action economy; same budget regardless of build; Focus companion | 06.1.1, 06.1.2 (nothing adds actions; INV-11), 06.1.3 / T-06-1 (variable costs), 06.1.6 (repetition), 06.14 (companions act only from the PC's budget); Focus is 05's and buys reach, never actions (06.1.2) | satisfied |
| P10 | Deterministic trigger-to-outcome for core power | 06.6.2–06.6.3 (basic reactions with fixed triggers and effects), 06.9.5 (windup), T-06-10 (conditions as effect references) | satisfied |
| P12 | Limitation / weakness / cost vocabulary | T-06-6 (weight: cost and hands as limits), T-06-7 properties, 06.4.10 (a call's snag is its cost) | satisfied |
| P13 | Tools own mechanics; state externalized | State touched; 06.3.1 (only `set_position` writes position; claim class `position`); 06.7.3 (engine-counted durations surfaced by `get_active_triggers`) | satisfied |
| P14 | Asymmetric cadence | 06.1.7 (three channels: what one action contains, tempo, reactions), DL-06-02 | satisfied without extra actions (deviation from the literal pattern recorded) |
| P16 | Always an actionable next step | 06.4.3 (out-of-reach redirect), 06.11.7 (refusals name what would be accepted), 06.12.1 (three ways out), 06.13.4 (aftermath names what the PC can do), 06.9.5 (a turn to answer) | satisfied |
| P17 | Graduated delivery | 06.9.6 (studying a foe delivers ranked items by reach) | satisfied |
| BRIEF §4 | Death real but telegraphed; no single unlucky roll | 06.9.5 (heavy blows announced), 06.2.4 (surprise survivable), 06.7.4 (no lock-down), 06.11.7 / 06.12 (Yield, Retreat, chase); death itself: 07 (INV-6) | satisfied (conflict half) |
| A2 #1 | The AI chooses categories, never numbers | every `[J]` here is a flag, an enum or a rung; DCs, harm, ticks and costs are computed | satisfied |
| A2 #7 | Positioning is discrete relationship-state | 06.3 | satisfied |
| A2 #10 | The engine owns all randomness, including the DM's choices | 06.9.1, 06.9.3 (ties rolled), 06.12.3 (ground drawn by `roll_table`) | satisfied |
| A2 #12 | Creativity pays through levers | 06.3.6 (flags as engine-cited levers and snags), 06.5.5, 06.5.10 | satisfied |
| INV-11 | No effect grants actions | 06.1.2; `eff.06.fewer_actions` only removes | satisfied |
| INV-14 | Every tick of a sensed clock renders an omen | 06.11.4 | satisfied |
| 00.17.2 (06 row) | action economy; turn order and tempo; bands and flags; attack and defense; weapon base severities; `conditions.yaml`; reactions; multi-target; morale; surrender; escape and chases; mobs and swarms; repetition; command | 06.1; 06.2; 06.3; 06.4; T-06-6; 06.7 + data; 06.6; 06.8; 06.11; 06.11.7; 06.12; 06.10; 06.1.6; 06.14 | satisfied |
| R5 CF-01…CF-16 | completeness rows owned by 06 | CF-01 06.2 · CF-02 06.1 · CF-03 06.3 · CF-04 06.4 · CF-05 06.4.1, T-06-11 · CF-06 06.7 · CF-07 06.6 · CF-08 06.11 · CF-09 06.12 · CF-10 06.4.8, 06.11.7 · CF-11 06.3.7 · CF-12 06.5.8–06.5.10, T-06-9 · CF-13 06.14 · CF-14 06.15 · CF-16 Edge cases (duel) | satisfied (CF-15 mass battle: anchor only; 11 owns) |
| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 06 (99); 77 tagged at revision C6a, 06.3.10 by the new DL-06-30; validator BASIS (DL-INT-13) | satisfied |
