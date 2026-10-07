# Constitution audit (V2a, Wave 4)

Agent V2a, 2026-10-07. Constitution: `.specify/memory/constitution.md` (v1.7.0). Matrix: `rules/appendix/traceability.md`.
Method: for each Core Principle (MUST), each Adopted Pattern (SHOULD) and each further non-negotiable of
`rules/_process/BRIEF.md` §6, take the rules the matrix lists and spot-check at least three of them by id with
`rules/tools/rq.py` (most from ch.04-08, which V2a read in full the same day; the rest looked up). Verdicts:
**compliant**, **deviating** (with the DL that justifies it) or **violating**. Ledger rows that bear on a clause
are named; they do not by themselves change a verdict.

## Core Principles (MUST)

| Clause | Spot-checked rules (what each does for the clause) | Verdict |
|---|---|---|
| I. AI DM executes all mechanical resolution | 04.4.6 `evaluate_recognition` is a tool returning packets with no numbers; PR-05-1 `use_ability` validates, prices and applies in a fixed order; 06.9.1 / PR-06-6 the engine runs the adversary's behavior list, the DM never chooses; 07.2.1 / PR-07-1 `apply_harm` is the one writer of Vitality; 00.14.1 tools name their runtime capabilities | compliant |
| II. Custom ruleset exploiting AI capacity for complexity | 05.10 composition through one substrate (regimes, priority ranks, spread tags, composites); 06.7 27 conditions in three channels; 07.2.4-07.2.6 wound buckets and load; 08.3 two-axis loot generator | compliant |
| III. Flexibility within bounds; base-model judgment by default | 01.5.3 anchors move at most two knobs, each a cited fact; 05.5.2 stretch is a `[J:flag]` with stated worst case and fixed prices; 06.5.10 environment anchor index with two knobs; 07.10.2 unlisted hazard `[J:rung]` that errs safe | compliant |
| IV. v1 single-player, text-only | 06.1.1 one PC, three actions; 06.14.1 companions have no turn; 07.3.4 / 07.3.7 out-of-fiction text blocks; 04.7.2 one CHOICE block per response | compliant |
| V. Closed primitives (fixed slots x bounded pools) | 05.2.1-05.2.2 twenty slots in three partitions, closed ceiling; 04.8.1 three deed seats and one oath seat; 05.11.6 pool sized by coverage (266, data-checked); 08.2.5 five attunements | compliant (I-033, I-037 open) |
| VI. Telegraphed consolidation; provisional by default; no squish | 04.8.5 consolidation keeps everything and retires ladders (WE-04-1 traced); 04.8.2 / PR-04-6 provisional grants never lapse without a warning; 05.12.1-05.12.3 restate, replace, shelve, provisional content; 08.6.10 one worked property per item life | compliant (I-043: nobody yet promotes content to permanent; I-049) |
| VII. Default-deny capability gate | 05.5.4 emulate needs the training license (G3 otherwise); 04.10.1 a Taking without the license is G3 with harvest as fallback; 06.15.2 mounted attacks need `martial_mounted`; 08.4.4 a relic makes an attempt legal without competence | compliant |

## Adopted Patterns (SHOULD)

| Pattern | Spot-checked rules | Verdict |
|---|---|---|
| P1 Layered variance, player-controlled reroll | 02.6.5 the Bent is never applied without the player's yes; 04.8.4 a pick may be kept (defer and gamble); 07.7.3 / 07.11.4 brink marks and haunts are a choice of three; 07.5.2 a maim's exact price is computed before the player picks the option | compliant (I-060 open). Note: 11.10.5 aging is post-creation variance resolved by a check; fate may reroll it and the player picks the attribute, which meets P1's "reroll" reading |
| P2 History-gated tiers, no level | 04.3.1 dual thresholds on sealed tallies; 04.5.6 `power_band` from tiers only; 05.6.1 Focus maximum from tiers; 07.1.2 Vitality growth from band | compliant (I-037: band counts provisional tiers in 04, confirmed only in 07; I-039, I-045) |
| P3 Granular state; ambiguity is the risk | 06.3.1 position written only by `set_position`, named in fixed words; 07.1.1 four descriptors are the only words for PC state; 08.1.13 every usable object gets an id before narration | compliant |
| P4 Creation trade-offs locked; breadth decoupled from competence | 02.3.2 Free rule vs Fixed rule set once; 04.2.3 broad callings +2/+5 against narrow +3/+6; 05.9.4 a training license gives +2 and the lowest grade, breadth is not power | compliant (I-047 open) |
| P5 Emergent-by-history acquisition | 04.4.3 three-valued policy over a defined confidence; 08.3.2 loot circumstance (decisive/costly/merciful/scavenged) is the fill axis; 04.10 the Taking is calling-gated, never combat's default reward | deviating, justified by DL-04-10 (deterministic tally scorer in place of a calibrated classifier; amendment candidate in 04's Interface requests) |
| P6 Named composites | 05.10.6 22 authored + 32 hybrid composites, exactly two keys, at most 4 EU (counts data-checked); 04.5.4 hybrid composites by rank; 08.4.8 storied sets as composites | compliant (ch.13-local partial only) |
| P7 Player-facing reference layer (codex) | 04.6.5 Leanings view; 04.7.2 CHOICE block lists every gain and price; 12.14.4 no numbers in fiction, the codex carries them; 08.3.13 codex shows rung, sealed slots, price | compliant (the codex spec itself is ch.14, pending) |
| P8 Deterministic degrees as default | 06.4.6 a critical is one reach rung, no crit table; 07.2.7 dying check by degree table; 07.9.3 stage checks by degree | compliant |
| P9 Fixed action-economy pool | 06.1.1-06.1.2 three actions, nothing adds actions; 05.6 one Focus pool for every calling; 06.14.2 a command spends the PC's action | compliant (I-033 open) |
| P10 Determinism decides what carries core power | 05.3.1-05.3.2 eight closed forms, literal rank text; 06.9.5 heavy blows always announced (fixed trigger); 07.2.3 the Stagger rule (fixed outcome) | compliant |
| P11 No naive point-buy without audited guardrails | 05.11.1-05.11.5 allowance/value budget, script-refused outside the band (arithmetic rechecked); 05.9.4 "nothing is bought with points"; 08.2.2 item share | compliant |
| P12 Limitation / weakness / cost as separate levers | 05.3.1 four separate fields, no implied weakness; 04.10.4 the Taking's three costs; 08.4.4 a relic's surcharge, missing competence and missing growth | compliant (I-038 open) |
| P13 Three-layer split | 00.14 deterministic tools; 08.1.13 / 06.3.1 state lives in the store, narration restates; 12.3.7 corrections and moderation kept apart | compliant |
| P14 Asymmetric base cadence (MAY) | 06.1.7 cadence lives in what one action holds, tempo and reactions, not a per-class speed; 06.4.4 weapon weight as cadence; 05.3.4 timing field | deviating, justified by DL-06-02 and DL-05-29 (P9's fixed pool kept; asymmetry expressed through three channels) |
| P15 Time-gated specialization | 05.8.5 learning clocks (2 weeks with a mentor, 6 emulations alone); 05.9.4 a license is a month with a teacher; 04.3.4 each tier asks for a new kind of evidence | compliant |
| P16 Always an actionable next step | 07.6.2 / PR-07-7 step 7 a defeat cannot finish without a lead; PR-06-10 the end of a fight names a next step; 07.6.3 captivity gives three openings | compliant |
| P17 Graduated information reveal | 08.5.3 study reveals properties by delivered reach, no free repeat; 04.6.4 readings give a band and one lacking kind; 06.9.6 an Observe unseals a foe's items in ranked order | compliant (ch.11-local partial only) |

## Further non-negotiables of BRIEF §6

| Non-negotiable | Spot-checks | Verdict |
|---|---|---|
| Focus is the TTRPG; ch.12 as rules of play | 12.14.4 and 12.3.7 are written as rules of play (what may be said, what counts as an error), not as model plumbing; ch.04-08 mention LLM concerns only where they shape a rule (06.9.1 adversary choice, 08.1.13 coin totals) | compliant |
| Traceability: every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) | Script over ch.04-08: 424 rule cards, 216 carry no `[C:]`/`[R]`/`[DL-]` tag of their own; 179 of those cite the rules they derive from, and many sit under a section whose first card or intro cites the DL; 37 cite nothing at card level (for example 06.3.4, 06.11.2, 07.5.9, 08.8.3) | deviating without a recorded justification: ledger **I-065** (MINOR). The basis is recoverable at section level, so no rule is unsourced in substance, but the card-level rule of BRIEF §6 is not met as written |

## Summary

- Core Principles I-VII: **all compliant**. No violation found.
- Patterns: 15 compliant, 2 deviating with DL justification (P5: DL-04-10; P14: DL-06-02, DL-05-29). None violating.
- BRIEF §6: Focus non-negotiable compliant; the card-level traceability requirement is a deviation with no DL yet (I-065).
- Mechanical fixes made during the audit: V2a-016 (stale `*.04.yaml` / `boundaries.05.yaml` contrib file names in `appendix/fragments/trace-04.md` and `trace-05.md`; appendix re-assembled).
- The matrix's statuses agree with what the spot-checks found, except that it has no row for BRIEF §6's card-level traceability.
