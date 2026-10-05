## Traceability — 12 DM Procedures

| Clause | Requirement (short) | Satisfied by (rule ids) | Status |
|---|---|---|---|
| C:I | The AI DM executes all mechanics; it is the engine, via its instruments | 12.2.8 (adjudication before prose), PR-12-1 T4–T6, 12.1.3 (a)(b), 12.6.1 (no chosen facts) | satisfied |
| C:II | Custom ruleset exploiting AI capacity | 12.9 (rotation ledger over facets/pillars/challenges), 12.7 (pacing director), 12.11 (NPC depths and memory), 12.13.6 (compiled anchor index) | satisfied |
| C:III | Flexibility within bounds; base-model judgment by default; revisit only on a recorded failure | 12.12.4 (review flags; Principle III candidate threshold), 12.3.3–12.3.4 (flagged fallbacks and corrections), 12.13.3–12.13.4 (two-change limit for actions and content), 12.12.6; no judge gate adopted (DL-12-01) | satisfied |
| C:IV | Single player, text only | 12.9 (spotlight for one player), 12.14.6 (positions in text), 12.15 (text OOF formats) | satisfied |
| C:V | Closed primitives | 12.2.2 (closed input kinds), 12.2.6 (closed pause points), 12.3.1–12.3.2 (closed claim classes and verdicts), T-12-7 (nine challenge types), 12.11.3 (eight registers), 12.11.7 (twelve valences), 12.13.4 (content only from existing primitives) | satisfied |
| C:VI | Consolidation; provisional by default | every entry in oracles.yaml, pacing.yaml, anchors.yaml, data/boundaries.yaml owner-block 12 `lifecycle: provisional`; 12.12.6 (recurring precedents proposed as provisional rules); 12.13.6 step 6 (retired anchors kept with superseded_by) | satisfied |
| C:VII | Capability gate before quality; redirect, never narrate into existence | PR-12-1 T4 (pipeline incl. GATE), 12.3.2 `overreach`, 12.14.13 (narration cannot create capabilities or valuable items), 12.8.6 / 01.3.6 (redirects leave a path) | satisfied |
| C:P3 | Rich substrate; background vs player-facing classified | 12.2.4 (substrate retrieved by situation, not dumped), 12.13 (reach and adapt), State touched (visibility of every 12 state) | satisfied |
| C:P7 | Player-facing reference separate from narration | 12.14.4 (numbers only in OOF), 12.15 (formats), 12.5.10 (codex and rules questions) | satisfied |
| C:P8 | Deterministic degrees | 12.2.8, 12.14.8 (narration follows the computed degree exactly) | satisfied (via 01) |
| C:P13 | Tools own mechanics; external store owns state; independent verification; moderation separate | 12.2.4 (state, not context), 12.3 (claim check against the store with a tool, not self-report), 12.3.7 (safety separate from consistency), 12.11.1 pronoun rule (the probe's recorded failure) | satisfied (gate model: deferred per C:III, DL-12-01) |
| C:P16 | Always an actionable next step; inject a lead after ~3 inconclusive results | 12.8.1 (engine counter, threshold 3), 12.8.2 (lead injection), 12.8.3, 12.8.4 (live-lead audit, Three Clue Rule), 12.8.5 (stuck answer), 12.7.2 (flatline guard) | satisfied |
| C:P17 | Graduated reveal by degree | 12.10.4 (which permitted item answers; undelivered items stay open; misleading only when misleadable) | satisfied (count: 01.10) |
| BRIEF §4 | Hidden mechanics, no diegetic System; sandbox; telegraphed death | 12.14.5 (recognition without an announcer), 12.14.4, 12.10.7 (tells), 12.7.5 (no second blow after a setback), 12.4.9 (venture loop) | satisfied |
| BRIEF A2 #10 | The engine owns all randomness incl. the DM's own choices | 12.6.1, T-12-4, 12.11.1–12.11.5 (NPC fields, reactions, actions rolled), 12.6.5 | satisfied |
| BRIEF A2 #14 | Precedent is state | 12.12 | satisfied |
| R5 DM-01…DM-10 | Agenda; turn loop; complication menu; improvising; rulings log; narration standards; off-screen; continuity audit; OOF talk; situations not plots | 12.1, PR-12-1, 01.13 + T-12-13, 12.13, 12.12, 12.14, 12.11.8 / 12.4.6, 12.3 / 12.4.8, 12.5.10, 12.1.2 P11 | satisfied |
| R5 TM-03, TM-04, TM-05, TM-09, TM-10 | Mode transitions; scene framing; session open/close; pacing controls; time skips | 12.4.5, 12.4.1–12.4.4, 12.5.2–12.5.4, 12.6–12.8, 12.4.6–12.4.7 | satisfied |
| R5 NP-01, NP-02, NP-06, AV-07 | NPC generation; roster; voice; reaction roll | 12.11.1, 12.6.6, 12.11.3, 12.11.2 | satisfied |
| R5 RS-14, RS-15 | DM oracle; twist/complication injection rate | 12.6 (tension: T% random events per Oracle question; scene test) | satisfied |
| R5 SC-01, SC-02, SC-05, SC-06 | Lines/veils (DM side); in-play adjust; moderation boundary; undo policy | 12.5.6, 12.5.7, 12.3.7, 12.5.8 | satisfied (player side: 14) |
| R5 EX-14 | Spatial description in text | 12.14.6, T-12-11 | satisfied |
| R5 LW-08 | Random world events | 12.6.5 (with ch.11's World Turn) | satisfied |
| R5 OB-05 | Progressive disclosure | 12.5.10 (rules answers on demand), 12.15.2 (the OFFER teaches the frame) | satisfied (with 14) |
| R5 X-01, X-03 | Spotlight between players excluded; diegetic UI excluded | 12.9 (solo reinterpretation), 12.14.5 | satisfied |
| 00.17.2 row 12 | turn loop; mode transitions; scene framing; DM Oracle + tension; pacing director; P16 counter + lead table; P17 in practice; NPC generation + reaction roll; oracles.yaml; anchors.yaml; ruling ledger use; session moves; spotlight rotation; twist table; OFFER script | PR-12-1 / 12.2; 12.4.5; 12.4.3; 12.6; 12.7; 12.8; 12.10.4; 12.11.1–12.11.2; data/oracles.yaml; data/anchors.yaml + 12.13.6; 12.12; 12.5; 12.9; tbl.twist_s1…s5; 12.15.2 | satisfied |
| 00.17.1 Q6 | 12 owns the DM's Oracle use, tension (≤ 1 rung), meaning tables | 12.6.1–12.6.7, tbl.meaning | satisfied |
| 00.15.3–00.15.6 | Anchor index compiled by 12; always-loaded core; precedent rule | 12.13.6 + anchors.yaml; 12.2.4 + T-12-1; 12.12 | satisfied |
| INTERFACE-REQUESTS (from 01) | tbl.twist S1–S5 and tbl.meaning; 15 anchor cards compiled; 01.11.4's definition; tension ≤ 1 rung; OFFER renders 01.7.1 | oracles.yaml; anchors.yaml; 12.8.1; 12.6.4; 12.15.2 | satisfied |
