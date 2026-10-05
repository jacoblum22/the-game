## Traceability — 08 Items, Loot, and Crafting

| Clause | Requirement (short) | Satisfied by (rule ids) | Status |
|---|---|---|---|
| C:I | The AI DM is the engine; tools compute | 08.3 (PR-08-1: generate computes every drop), 08.8 (prices from tables), 08.6.4 (clocks) | met |
| C:II | Custom ruleset exploiting AI capacity | 210-property pool, 185 base items, 59 materials, weekly economy handlers (08.1–08.10) | met |
| C:III | Bounded judgment, no blanket override | every [J:*] in 08 carries a Worst case line (08.1.11, 08.1.13, 08.3.2, 08.3.10, 08.5.3, 08.6.3, 08.7.2, 08.7.4, 08.8.7) | met |
| C:IV | Single-player, text | narration in one line (08.3.13); codex detail (14) | met |
| C:V | Closed primitives, bounded counts | fixed slot counts per rung (08.1.4), ≤ 3 properties per item (08.2.3), one active per item (08.4.1), attunement 5 (08.2.5), gen.item_ability reuses existing abilities (08.4.3) | met |
| C:VI | Consolidation; provisional content | every data entry lifecycle provisional; recipes and residuum as consolidation of surplus (08.6.8); revisit triggers on reward rates (08.2.7, OEQ-08-2) | met (content scale) |
| C:VII | Default-deny capability gate | relic licenses (08.4.4); crafting needs licenses with crude fallbacks (08.6.3); harvest of essences gated (08.3.10); transmutation G4 (08.8.9) | met |
| C:P1 | Player-controlled variance | chosen fills on mercy, crafting and gifts (08.3.8, 08.6.3, 08.7.2) | supports |
| C:P2 | History-gated power; no levels | items never change attributes, competence, maxima, tiers (08.2.1); math 08.2.6 | met |
| C:P3 | Granular state classified | visibility of every item field (State touched; sealed properties 08.5.3) | met |
| C:P4 | Breadth vs competence | relics give access without competence (08.4.4) | supports |
| C:P5 | Pool gate / fill quality; loot as default application; what items grant | 08.3 (loot), 08.6 (craft), 08.7 (gift), 08.4.3 (item ability); 08.4.1 answers the deferred question; harvest makes every resolved defeat yield (08.3.1) | met |
| C:P6 | Named composites | sets of storied items via composite_key licenses (08.4.8) | supports |
| C:P7 | Codex | item cards, rollups (Interface requests to 14) | requested |
| C:P8 | Degrees of success | Greater/Flawed degree effects (08.3.9, 08.6.6); haggle reach → notches (08.8.7) | met |
| C:P9 | One Focus pool; no extra actions | relic surcharge in Focus (08.4.4); items never add actions (08.2.1) | met |
| C:P10 | Deterministic trigger → outcome | properties as effect refs with fixed tiers and natural-range chances (08.4.2) | met |
| C:P11 | Audited budgets | the item share (08.2.2), per-item caps (08.2.3), generation-time compliance 1,000/1,000 (T-08-16) | met |
| C:P12 | Limitation / weakness / cost | relics: no competence, no growth, +1 Focus (08.4.4); armor's snags, load, sleep (08.1.6) | met |
| C:P13 | State externalized; independent checks | coin and items only through tools (08.1.13) | met |
| C:P15 | Time-gated specialization | crafting clocks and recipes (08.6.4, 08.6.9) | supports |
| C:P16 | Actionable next step | find-buyer clock, caches with rumors (08.1.9), redirects in edge cases | supports |
| C:P17 | Graduated reveal | identification by study (08.5.3) | met |
| BRIEF §8 | "What dropped items grant" resolved | 08.4.1 | met |
| BRIEF A1 (08 row) | loot, properties, relics, crafting, economy, encumbrance, supply, mounts, slot ceiling | 08.1–08.10 | met |
| 00.17.2 (08 row) | item schema; four domain configs; quality rungs; relics; crafting clocks; prices, wealth, encumbrance, supply, mounts, vehicles; item-layer budget | 08.1.1, gen_*.yaml, 08.1.4, 08.4.4, 08.6.4, 08.8, 08.9, 08.10, 08.2 | met |
| 00.17.1 Q2 | one item-bound active; no slots added; passives against item budget | 08.4.1, 08.2.1, 08.2.2 | met |
| 00.17.1 Q17 | kits by tag resolve to base items | 08.1.12, base_items.yaml#kit_resolution | met |
| R5 EQ-01…EQ-13 | equipment, encumbrance, currency, buying/selling, lifestyle, loot, crafting, durability, consumables/light/supply, mounts/vehicles, services/hirelings, holdings (prices), treasure calibration | 08.1, 08.9.1, 08.8.1, 08.8.4–5, 08.8.6, 08.3, 08.6, 08.1.9/08.6.7, 08.9.4–6, 08.10, 08.8.8, 08.8.8 (11 owns play), 08.8.10 | met |
