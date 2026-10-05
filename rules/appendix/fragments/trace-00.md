# Traceability — 00 Architecture (the original matrix's rows, kept as 00's fragment at integration)

| Clause | Requirement (short) | Satisfied by (rule ids) | Status |
|---|---|---|---|
| I | The AI DM executes all mechanical resolution | 00 Design intent ("Principle I, stated precisely"); 00.14 (tools are the DM's instruments; DM supplies ids/rungs/flags, INV-3); 00.13 (the frame is the DM's adjudication step) | Satisfied (architecture) |
| II | Custom ruleset exploiting AI capacity for complexity | 00.10 (composition substrate), 00.11 (generator), 00.5 (426-tag vocabulary), 00.7 (boundary registry), 00.15 (rule cards + retrieval) | Satisfied (architecture) |
| III | Flexibility within bounds; base-model judgment by default; no blanket override | 00.2.1–00.2.3 (P-A, P-B, worst-case line), 00.2.6–00.2.7 (anchors, two-change limit), 00.15.5–00.15.6 (ruling ledger incl. `review_flag` as the revisit-trigger record), 00.1.4 (precedence) | Satisfied (architecture) |
| IV | v1 single-player, text-only | 00.7.1 (no real time), 00.7.9 (session boundaries), 00.17 Q8 (companions without separate turns) | Satisfied (architecture) |
| V | Build diversity from closed primitives | 00.12.5 (closed 15-verb tier), 00.10.2–00.10.3 (closed hooks and operations), 00.10.7 (closed regimes/slots), 00.17 Q2 (one hard ceiling in three partitions), 00.11.3 (fixed slot counts), 00.5.2 (nine deed branches) | Satisfied (architecture; numbers in 05) |
| VI | Mandatory, telegraphed consolidation; provisional by default; squish ≠ retirement | 00.16.3 (content lifecycle provisional/permanent/retired), 00.17 Q12 (character-scale provisional, season boundary), T-00-9 `h.04.season_consolidation`, 00.2.4 SG-25 | Satisfied (architecture; mechanics in 04) |
| VII | Default-deny capability gate with redirect | 00.12.1–00.12.5 (license schema, literal reading, gate classes G0–G4, crude fallback, acquisition paths, basic verbs), INV-7, INV-8 | Satisfied (architecture; procedure in 01) |
| P1 | Birth variance; player-controlled deferred reroll | 00.11.1 (`gen.birth` domain), 00.4.3(a) (deferred reroll is the only post-creation attribute change besides the two listed) | Satisfied (frame; content in 02) |
| P2 | History-gated tiers, no levels; baseline floor | 00.3.6 (floor = competence +1 at `deed`), 00.3.7 (power bands derived from tiers), T-00-22 (word "level" banned), 00.17 Q5 | Satisfied (frame; tiers in 04) |
| P3 | Granular state; classify background vs player-facing; reconciliation | 00.6.1–00.6.4 (typed state, ownership table, four visibility classes), 00.6.5 (sealed), 00.6.6 (write-on-mention), 00.14 `check_claims` | Satisfied (architecture) |
| P4 | Creation trade-offs locked; breadth ≠ competence | 00.4.3 (creation ranges, sum band for trade-offs, attributes mostly fixed), 00.3.6 (competence separate from access) | Satisfied (frame; creation in 02) |
| P5 | Emergent-by-history power: pool gate + fill; hierarchical tags; derived callings | 00.11 (gate→fill, one algorithm, no third axis), 00.5.1–00.5.4 (hierarchy, cascade), 00.5.2 (hybrid keys on branch pairs), 00.6.8 (evidence core shape), 00.10.9 (recharge enforced) | Satisfied (architecture; content in 03/04/08) |
| P6 | Named composites + priority-ordered behavioral tags | 00.10.7 (named_composite and priority_exclusive regimes), T-00-14 (behavioral slots) | Satisfied (architecture; content in 05) |
| P7 | Player-facing codex | 00.6.4 (visibility classes the codex renders), 00.1.7 (out-of-fiction layer), 00.14 `codex` | Satisfied (frame; spec in 14) |
| P8 | Deterministic degrees of success | 00.3.10 (four fixed degree ids, margin bands), 00.13 (frame) | Satisfied (frame; rule in 01) |
| P9 | Fixed action economy; one shared Focus pool | INV-11 (no effect grants actions), 00.3.13 (one Focus pool, not attribute-derived), 00.17 Q21 | Satisfied (constraint; numbers in 05/06) |
| P10 | Determinism of trigger→outcome decides what may carry core power | 00.10.1 (effects as literal definitions), 00.10.2 (closed hooks), SG-15 | Satisfied (architecture) |
| P11 | No naive point-buy | 00.4.3 (bounded creation ranges and sum; no post-creation arbitrage) | Satisfied (constraint; method in 02) |
| P12 | Limitation / weakness / cost as separate levers | 00.12.1 (scope/excludes), `data/SCHEMAS.md#abilitiesyaml` (separate limitation, weakness, cost fields) | Satisfied (schema; content in 05) |
| P13 | Tools own mechanics; external store owns state; verification | 00.6 (external typed store), 00.14 (tool surface, RC list), 00.14 `check_claims` | Satisfied (architecture; judge-gate remains per C:III) |
| P16 | Always an actionable next step | T-00-9 `h.12.inconclusive_streak`; 00.12.3 (G3/G4 always redirect); 00.12.7 (a "no" is followed by what is there) | Satisfied (hooks; procedure in 12) |
| P17 | Graduated reveal | 00.13 (`deliver` in the frame), 00.3.15 (delivered reach feeds delivery counts), 00.14 `deliver` | Satisfied (frame; counts in 01) |
