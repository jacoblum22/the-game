## Chapter 16 — Companions and Allies: traceability

| Clause | Requirement (short) | Satisfied by (rule ids) | Status |
|---|---|---|---|
| C:I | The AI DM executes mechanics through instruments | 16.4.2 (lines computed by PR-16-2), 16.5.4 (ticks by `tick_clock` with cited ids), 16.6.2 (departure clock), 16.7.7 (the engine rolls every ally beat), 16.7.12 (held line fortune checks), handlers in `boundaries.16.yaml` | satisfied |
| C:II | A custom ruleset exploiting AI capacity | per-ally drives, two loyalty clocks, contracts, memories, shared record, protégé callings, held lines — all background-resolved state (16.1.2) | satisfied |
| C:III | Bounded judgment; no blanket override | every `[J:*]` card carries a Worst case line (16.1.1, 16.2.6, 16.3.1–16.3.4, 16.3.7, 16.5.4, 16.5.7, 16.5.9, 16.6.4, 16.6.6, 16.7.12, 16.8.1, 16.8.3, 16.11.2, 16.15.4); 16.13.3 closes the "the ally would…" channel | satisfied |
| C:IV | Single-player | 16.2.4 (no peer follows as a second protagonist), 16.7.1 (allies have no turns), 16.13.4 (banter budget), 16.16.1 (allies as successors, not co-players) | satisfied |
| C:V | Closed primitives | seven kinds (T-16-1), five orders (06), fifteen knacks (T-16-6), seventeen loyalty sources (T-16-8) + eight beast sources, five hazard rungs (T-16-9), eleven departure causes (T-16-18), six betrayal rows (T-16-11), five journey roles (T-16-14), nine downtime duties (T-16-15), forty templates | satisfied |
| C:VI | Consolidation; provisional content | every data entry `lifecycle: provisional`; knacks and abilities capped at three and replaced, never stacked (16.4.7, 16.10.2, 16.10.4); growth on the season boundary (16.10.1) | satisfied |
| C:VII | Default-deny capability gate | 16.7.2 item 1 (an ally's commanded beat gates G1/G2 for the ally; unlicensed → crude fallback), 16.3.1 (the recruitment gate with redirects), knacks as licenses (T-16-6), 16.15.6 (bound beings only as their working allows) | satisfied |
| C:P2 | No levels; history-gated power | 16.10.1 (band rises by service, season-gated), 16.10.4 (protégé tiers via 04), no level anywhere | satisfied |
| C:P3 | Rich background state; classified visibility; reconciliation | 16.1.3 (every family classified: shown / available / sensed / sealed), 16.13.2–16.13.3 (memories and the consistency rule for the claim check) | satisfied |
| C:P5 | Emergent-by-history power for tracked actors | 16.10.4 (protégés evaluated by 04 on their own resolved evidence); 16.7.7 (allies' acts are their own evidence, tracked only for protégés) | satisfied |
| C:P7 | Player-facing reference | 16.1.3 (codex classes), Interface requests to 14 (Retinue, Offers, Departures views) | satisfied |
| C:P8 | Deterministic degrees | ally beats through the pipeline (16.7.7); held line steps by degree (16.7.12); hire and invite frames (16.3.3–16.3.4) | satisfied |
| C:P9 | Fixed action economy | 16.7.1 (0 actions, 1 reaction; Command costs the PC's action), 16.8.2 (no time multiplication in sites), 16.7.12 (no turns for independent allies), 16.4.4 (no summoning allies) | satisfied |
| C:P12 | Limitation / weakness / cost | contracts' hazard (limitation), a template's refusal and temperament (weakness), wages, keep and places (cost) | satisfied |
| C:P13 | Externalized state; verification | 16.4.6 (never-out-power check at every line build), `16-gen_data16.py` (data validation), 16.13.3 (claim-check class for ally acts) | satisfied |
| C:P16 | No silent dead ends | 16.3.1 (every recruitment failure redirects), 16.2.5 (full retinue redirects), 16.12.1 (personal threads with fallbacks), 16.6.2 (departure is a countdown the player can answer) | satisfied |
| INV-6 | No death without both keys | 16.9.1–16.9.2 (Key 1 for allies; the bleeding-out clock as Key 2), 16.6.6 (betrayal never lethal) | satisfied |
| INV-11 | No effect grants actions | 16.7.1, 16.7.3–16.7.5 (orders written by the engine, no actions), 16.4.7 (no knack adds an action), 16.7.12 (held lines instead of allied turns) | satisfied |
| INV-14 | Every tick of a sensed or hidden clock renders an omen | 16.5.8 (loyalty omens per tick, T-16-16) | satisfied |
