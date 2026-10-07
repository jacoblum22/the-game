## Chapter 09 — Adversaries: traceability

| Clause | Requirement (short) | Satisfied by (rule ids) | Status |
|---|---|---|---|
| C:I | The AI DM executes mechanics through instruments; nothing bypasses them | 09.1.4, 09.4.1, 09.6.2, PR-09-1, PR-09-3, PR-09-4 (every adversary number, turn and advisory computed by the engine) | satisfied |
| C:II | Custom ruleset exploiting AI capacity | 09.4.4 (Vitality solve), 09.6.2 (closed-form estimator), 63 archetypes / 123 adversaries generated and validated | satisfied |
| C:III | Bounded judgment, no blanket override | every `[J:*]` (09.2.4, 09.3.1, 09.4.2, 09.4.8, 09.7.4, 09.7.6, 09.9.2, 09.10.2, 09.8.5, 09.8.7) carries a Worst case line; 09.1.4 no mid-fight adjustment | satisfied |
| C:IV | Single-player, text-only | 09.8 (solo encounter budget), 09.6 (advisory for one PC), 09.10.1 (tells in text) | satisfied |
| C:V | Closed primitives | closed archetype library, closed power library (`pow.*`), closed predicate and macro vocabularies (T-09-8), four variants, nine roles | satisfied |
| C:VI | Consolidation; provisional content; squish ≠ retirement | every entry `lifecycle: provisional`; variants and Nemesis never change a band (09.9.3); new creatures reuse archetypes (09.2.3) | satisfied (content scale) |
| C:VII | Default-deny capability gate | 09.2.5 (`cannot` → G4 with a redirect), 09.10.2 (lore licensed or common knowledge, G3 redirect to Observe), 09.7.6 (parley G4 outside `parley_when`) | satisfied |
| C:P2 | No levels; power from history | 09.3 (threat bands read against `power_band`), 09.6.1 (PC's actual line) | satisfied |
| C:P3 | Rich background state, classified visibility | 09.1.2 (sealed stat blocks; permitted slices), State touched (visibility), T-09-14 | satisfied |
| C:P5 | Source gates pool, method fills | 09.2.1, 09.11.1 (loot contract), 09.11.3 (absorbable pools, cannot_absorb, signature) | satisfied |
| C:P8 | Deterministic degrees | adversary beats are fortune checks (09.1.3, PR-09-3); degree tables for resisted powers (T-09-7) | satisfied |
| C:P9 | Fixed action economy; one Focus pool | 09.1.3 (two actions every band, no added actions), 09.5.3 (adversary Focus pays every power) | satisfied |
| C:P12 | Limitation / weakness / cost separate | archetype `cannot` (limitation), `weak_spot` and resistances' counters (weakness), Focus costs and limits (cost) as separate fields | satisfied |
| C:P13 | Engine-owned state; sealed secrets | 09.1.2, 09.5.4 (witnessed facts), 09.10.4 (knowledge records) | satisfied |
| C:P16 | Always an actionable next step | 09.6.6 (warning lists exits), 09.7.6 (parley, yield, retreat conditions), 09.9.1–2 with 07.6 (defeat writes openings), 09.6.4 (counters named) | satisfied |
| C:P17 | Graduated reveal for compound queries | 09.10.2 (ranked six-item lore list via deliver_count), 09.10.3 | satisfied |
| BRIEF §4 | Death real but telegraphed; defeat changes the situation | 09.6.5–6, 09.9.1–2, 09.5.6 (no kill-outright effect), 09.3.5 (windups), 09.9.5 (menu rates by word) | satisfied |
| 00.17.2 (09 row) | archetypes as manufacturers; T1–T5 templates; threat_advisory; solo budgets; behavior lists and morale; lethal_context and defeat_disposition; tells; bestiary | 09.2, 09.3–09.4, 09.6, 09.8, 09.7, 09.9, 09.10, 09.12 | satisfied |
| 00.17.1 Q5 | `threat_advisory(encounter, pc)` from bands, count and power band; lethal feeds 07 | 09.6.1–09.6.5, PR-09-4 | satisfied |
| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 09 (76); 50 tagged at revision C6c; validator BASIS (DL-INT-13) | satisfied |
