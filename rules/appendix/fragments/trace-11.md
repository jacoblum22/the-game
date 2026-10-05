## Chapter 11 — The Living World: traceability

| Clause | Requirement (short) | Satisfied by (rule ids) | Status |
|---|---|---|---|
| C:I | The AI DM executes mechanics through instruments; nothing bypasses them | 11.2 (World Turn as a handler), 11.3.5–11.3.7 (faction checks and agenda rolled by the engine), 11.4.6 (reactions by table and weight), 11.6.3 (rumor truth rolled), 11.9.4 (yields by check), 11.13.5 (ledger rolls); PR-11-1…PR-11-8; `data/boundaries.yaml owner-block 11` | satisfied |
| C:II | A custom ruleset exploiting AI capacity | factions with tiers, holds, ratings, stages, linchpin fates, relations, attention; sealed situation timelines; per-scope reputation with valence; rumor truth and spread; chronicle; legacy ledgers — all background-resolved and engine-run | satisfied |
| C:III | Bounded judgment; no blanket override | every `[J:*]` card (11.3.3, 11.3.11, 11.3.15, 11.4.6, 11.5.2, 11.5.3, 11.5.4, 11.5.6, 11.9.7, 11.13.9, 11.3.18) carries a Worst case line; 11.2.4 forbids World Turn writes to the PC; 11.3.7 removes the DM from faction decisions | satisfied |
| C:IV | Single-player, text-only | one PC; successors are one at a time (11.13); traces are text (11.6) | satisfied |
| C:V | Closed primitives | closed lists: 6 temperaments, 9 faction actions, 5 stages, 4 ratings, 6 tiers, 4 trace kinds, 7 rumor sources, 6 distortions, 8 epithet forms, 5 thread ranks, 9 thread statuses, 10 world changes, 9 improvements, 5 endings, 3 ledgers, 8 inheritance channels, 6 festival effects | satisfied |
| C:VI | Telegraphed, bundled consolidation; provisional by default; no squish | 11.11.1–11.11.4 (the season boundary as the boundary point; herald a week ahead; world phenomena provisional, confirmed or retired); 11.8.6 (provisional ranks); 11.5.5, 11.5.9, 11.7.9, 11.4.3, 11.2.8 (lifecycles, caps, folding); 11.13.7 (retirement as structural retirement); every data entry `lifecycle: provisional` | satisfied (world, character-seat and content scales) |
| C:VII | Default-deny capability gate | 11.5.11 and 11.8.4 (threads and ranks never grant licenses); 04.11.3 respected (no conferral of capability); 11.13.10 (nothing of power inherited) | satisfied |
| C:P1 | Layered variance; player-controlled reroll | successor's fresh birth draw via 02.2.7 (11.13.9); the player chooses among three candidates with visible trade-offs | satisfied |
| C:P2 | No levels; power from history | 11.13.7/11.13.10 (successor at the floor); ranks are not tiers (11.8.2); renown is not power (11.7.7) | satisfied |
| C:P3 | Granular state; classify visibility | State touched (visibility per record); 11.1.1 table; 11.1.5 narrator view | satisfied |
| C:P5 | Gate→fill for emergent content | gifts through 08's `gen.gift` with faction `boon_base`/`boon_signature` (11.9.9) | satisfied (consumer) |
| C:P7 | Player-facing reference | codex views requested of 14 (Interface requests); `[SEASON]` and `[RETIRE]` blocks | satisfied (spec) |
| C:P8 | Deterministic degrees | faction checks, yields, aging, Train-a-Successor on 00.3.10 degrees | satisfied |
| C:P13 | Externalized state; reconciliation | change log, chronicle, rumor and reputation records; 11.12.4 continuity checks; claim check reads them | satisfied |
| C:P16 | No silent dead ends | 11.5.6 (≥ 3 placements), 11.5.7 (fallbacks), 11.5.10 (hook supply), 11.6.4 (every rumor leads somewhere), 11.4.5 (kickers) | satisfied |
| C:P17 | Graduated reveal | scheme critical success unseals one fact (11.3.6); rumors partial/false with real `points_to` | partial (11 consumes 15's delivery) |
| INV-2 | Narration restates state | 11.2.7 (narrate the returned list only); 11.1.5 | satisfied |
| INV-4 | Engine randomness | every roll in this chapter is a tool roll | satisfied |
| INV-6 | No death without two keys | 11.10.5 (age never kills a PC); 11.2.4 | satisfied |
| INV-10 | Sealed state stays sealed | goals, fates, timelines, rumor truth, bang queue sealed (11.1.5) | satisfied |
| INV-12 | Triggered effects do not trigger | 11.4.7 (immediate reactions at depth 1; one link per week) | satisfied |
| INV-14 | Omens on hidden ticks | 11.3.6 (goal clocks), 11.3.12 (attention), 11.4.2 (traces) | satisfied |
| INV-15 | Every boundary runs | 11.2.1, 11.13.8 (timeskips run every boundary) | satisfied |
| BRIEF §4 | Open-ended sandbox; finish = retirement/legacy | 11.2–11.12 (indefinite engine); 11.13 | satisfied |
| R5 LW-01…LW-14, TM-07, TM-08, AD-06, AD-07, HR-10, HR-11, EQ-12, SO-05, SO-06, SO-07 | living-world checklist rows owned by 11 | 11.3; 11.3.12; 11.5; 11.6; 11.4; 11.3.18; 11.4.3; 11.9.7; 11.9.8; 11.13; 11.5 register; 11.3.12; 11.10; 11.11; 11.5.11; 11.7; 11.10.5; 11.13; 11.9; 11.3.12; 11.6; 11.4.9 | satisfied |
