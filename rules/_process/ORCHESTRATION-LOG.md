# Orchestration Log

How this ruleset was produced: waves, agents, and every plan adjustment made as results came in.
Plan of record: waves 1 (research) → 2 (architecture) → 3a (spine) → 3b (subsystems) →
4 (verification) → 5 (revision loop) → 6 (finalization).

## 2026-09-29 — Wave 1 launched (research, 7 parallel agents)
- R1 corpus distiller: DM craft + long-horizon benchmarks → research/R1-digest-dm-craft-and-long-horizon.md
- R2 corpus distiller: LitRPG + Mistborn/balance/AI-integration → research/R2-digest-litrpg-and-mistborn.md
- R3 corpus distiller: emergent power + WoW/PoE/MMO → research/R3-digest-emergent-power-and-mmo.md
- R4 web: AI capabilities → rule design → research/R4-ai-capabilities-for-rule-design.md
- R5 web: completeness taxonomy + solo/sandbox procedures → research/R5-completeness-and-solo-procedures.md
- R6 web: hidden-mechanics recognition, sandbox engines, telegraphed death, legacy → research/R6-sandbox-recognition-death-legacy.md
- R7 web: freeform-action adjudication ("try anything") → research/R7-freeform-adjudication.md
- Adjustment vs. plan: R7 added (not in the original plan) because goal 1 — player freedom to try
  creative ideas — had no dedicated research, and it is the owner's first-stated goal.

## 2026-09-29 — Wave 1 interrupted and resumed
- All 7 research agents were terminated mid-task by an API session rate limit (HTTP 429).
  Partial drafts survived in the scratchpad (R1 drafts, R2 part 1, R3 part 1, fetched sources).
- On the owner's instruction ("Try again"), each agent was resumed from its own transcript via
  SendMessage (context intact, no re-reading lost), rather than relaunched from scratch.

## R1 returned (35.1k words, 665 verified citations)
Adjustments queued for the post-Wave-1 BRIEF update:
- Ownership gaps: generic CLOCK primitive, in-world TIME/calendar model (→ 00-architecture as core
  primitives); COMPANIONS/allies/hirelings (solo action economy) — candidate new chapter;
  NPC knowledge & secret state, error correction/recaps (→ 12).
- Ch.01 must decide nat-20/nat-1 explicitly (current rule: DC 20 crit-fails 40% at +2, DC 25 65%).
- BRIEF §3 clarification: sequencing/defaults/fast-path arguments are legitimate goal-1 arguments
  (choice paralysis is game-halting); cutting rules remains forbidden.
- BRIEF: reinterpret multiplayer spotlight research for solo play (rotate facets/pillars/challenge types).
- Verification-in-the-turn-loop is a rule-of-play concern for ch.12 (largest measured win in sources).

## R2 returned (30.7k words, 298 verified citations)
Independently corroborates R1 on the nat-20/nat-1 + ±10 crit band problem (two agents, same math).
Adjustments queued:
- Recognition = deterministic trigger [D] + DM-chosen fictional VEHICLE from a closed vehicle table [J]
  (order seeks you, oath at crisis, mentor, trial, institution, title, awakening, revelation, place, patron).
  This is the concrete mechanism for "hidden mechanics" → ch.04 core design input.
- BRIEF must flag: constitution P5 body still says "calibrated classifier returning confidence";
  ch.04 must define "confidence" for whatever scorer it picks, or grant/offer/abstain has no input.
- New ownership gaps: condition/status stacking vocabulary (→ 00 defines schema, 06 owns list);
  Focus recovery vs rest (05 owns Focus, 07 owns rest — explicit interface); PC power band
  (→ 04 defines, 09 consumes); recognition vehicles' faction reactions (04 ↔ 11 interface).
- BRIEF §3 guardrail: "complexity not a constraint" ≠ narrate stat blocks; narration density stays
  fictional, crunch lives in the codex.
- Tier ladder must have a stated maximum; tier-ups restate ability text rather than append.
- Constitution evidence overstatements (P3 46-58%, P4 "tested", V's HWFWM/Underworld claims) →
  record in v1.8.0 amendment as evidence corrections.

## R5 returned (189-row completeness checklist, 46 solo/sandbox procedures)
The checklist (§1, stable row ids) becomes the completeness audit in Wave 4.
Chapter-map change now clearly warranted (to be finalized after R3/R4/R6/R7):
- Split overloaded ch.10 → 10 Exploration, Travel & Sites (hexcrawl, Delve-style site procedure,
  hazards, weather, traps) and a new 15 Social, Investigation & Downtime.
- New 16 Companions & Allies (flagged independently by R1 and R5).
- 00 gains: standard time ladder + boundary-event registry (advance_time), generic clock primitive,
  condition/status schema.
- 12 gains: DM oracle (d100 likelihood ladder + tension dial), NPC generation + reaction roll,
  rulings log (precedent consistency), session moves, error correction.
- 11 gains: threads/quest register, reputation/renown/titles, holdings & player-driven world
  change, season turn (also the VI boundary point for provisional content), calendar.
- 07 gains: poison/disease/curses, mental harm. 08 gains: encumbrance, supply, mounts/vehicles.
- 05 retitled to own MAGIC explicitly (rituals, research).
- 01 decides: player-spendable luck/fate currency (ties to last-chance choice before death).
- 13/14 gain: session zero + safety, first-session teaching arc, pregens + fast creation path.
- Appendix gains: index, DM quick-reference, credits for any CC-BY-derived tables.

## R3 returned (29k words, ~90 mechanics, ~150 numbers)
Adjustments queued:
- 00 owns the shared COMPOSITION SUBSTRATE: effect-definition table, closed trigger-hook list,
  single ordered modifier-evaluation pass, stacking families, proc-chain terminator, four
  combination regimes (additive / independent-trigger / priority-exclusive / named composite).
- One "gate → fill" generator for every emergent-content domain (loot, crafting, gifts, absorbed
  powers, item abilities): DM classifies onto closed lists, tool computes content.
- Positioning = discrete relationship-state (range bands + engagement + flags), tool-written only.
- Position-and-Effect layer (pre-roll risk declaration) = the lethal-risk telegraph: "no Desperate,
  no death on that roll". Converges with R1 #5. → ch.01 + 06 + 07.
- P9 vs P14 conflict (asymmetric cadence vs fixed action budget) → ch.06 must resolve in DL.
- BRIEF must: (a) restate that P3's background vs player-facing CLASSIFICATION still stands (only the
  budget is dropped); (b) scope VI "provisional" (rules content vs character grants vs both);
  (c) flag P5-body "calibrated classifier/confidence" vs tally scorer (also R2) — ch.04 defines
  confidence; (d) citation form for repo artifacts `[R: src/...]`, `[R: specs/...]`.
- Slot ceiling vs item-granted/absorbed abilities → 05↔08 cross-chapter decision in 00.

## R6 returned (18.9k words; recognition V1–V14, World Turn, Two-Key death, legacy)
Adjustments queued:
- Recognition = tally [D] × witness (gates PUBLIC recognition/reputation) × moment (vehicle V1–V14
  chosen by policy outcome + calling family + scene intensity). Converges with R2's vehicle table.
  Offer protocol: accept/decline/defer; deferred offers persist (standing_offers[]). Every calling
  has a SHADOW (corruption direction) and oath-callings list forbidden acts up front.
  Revocation = "the Fraying" (staged warning → atone-or-turn). Converges with R2 #6.
- Out-of-fiction one-line offer marker is the codex layer, NOT a diegetic System → 04 + 14 agree.
- Two-Key death rule (declared-lethal + already-Dying/chosen gamble), Warned→Staggered→Dying→
  Threshold ladder, last-chance MENU (never a roll to die), Yield/Retreat as always-available basic
  actions. Converges with R3 #9 ("no Desperate, no death").
- Living world: 8-step World Turn at downtime/travel boundaries; factions with tier/hold/ratings/
  goal clock/lifecycle/linchpins/status −3..+3; pacing director (L4D intensity cycle); hooks with
  ≥3 clue placements + a proactive fallback event; rumors with fixed truth values; chronicle.
- Capability tiers (from tally) kept separate from institutional ranks (seat-limited faction titles).
- 00 tool surface: deterministic table-roll tool, clock tools, status tools.

## R4 returned (15.2k words; 8 strengths / 17 weaknesses; style guide SG-01..SG-20)
Highest-impact new evidence: CoC-Seduce (arXiv 2607.02802): roll/no-roll errors are ~120× more often
lenient than strict (9.58% vs 0.08%); a player's plausible justification raises it 3.82%→17.30%;
not fixed by scale/reasoning. Our own F002 logs: 11% off-ladder DCs (F001: 30%), modifier 0 passed in
62% of calls, 25% of checks were critical failures. Yes/no judgments ~87% agreement; 5-rung ladder
exact-match 38–58% but 85–93% within one rung; nested exceptions fail systematically; secrets in the
narrator's context leak (private sealed state fixes it: 2–12% → 76–100%).
Adjustments (these reshape the architecture):
- The AI never picks a raw number: it picks a rung / yes-no flag / category; the tool computes.
  DC = obstacle tier (≤5 anchored rungs) + capped yes/no circumstance flags citing facts.
- "When in doubt, roll." Player text sets intent+method only, never facts/outcomes.
- Creativity pays in bounded currency (a step, a flag, a better approach) — never auto-success.
- Stakes declared in a structured field BEFORE the roll (converges with R1/R3/R6 telegraph).
- Consequences from degree × stakes tables; narrator picks the fictional form, not whether.
- Sealed secrets in state; write-on-mention; engine owns ALL randomness incl. DM "random" choices.
- No nested exceptions in rule text; precedence lives in engine (R3 composition substrate).
- Rule kinds refined: [D], [J:flag], [J:enum], [J:rung], [J:open], [T] trigger, [S] sealed, [N];
  every [J] rule states its worst-case cost of a wrong call.
- Substrate is retrievable RULE CARDS + anchor index + precedent log, not a prompt dump.
- 00 adopts R4 §4 as the rules style guide.

## R7 returned (17.6k words; 11-step pipeline; 13 worked examples)
- Adopted as ch.01's default pipeline. Levers (named established facts) as the ONLY creativity
  currency; closed 15-verb basic tier; licenses with crude_fallback + acquisition_paths; World-Fact
  Oracle; ruling ledger; seven-property anchor standard + two-change limit; P17 → graduated delivery.
- Fourth independent finding on the crit rule → converged default: PF2e one-step nat-20/nat-1 shift
  and DC-ladder recalibration (ch.01 makes final call).

## Wave 1 complete → BRIEF Addendum A written
All 7 digests in `research/` (~170k words total). BRIEF.md Addendum A:
- A1 revised chapter map: 00–16 (added 15 Social/Investigation/Downtime, 16 Companions; 10 narrowed
  to Exploration/Travel/Sites; 05 now explicitly owns magic; 00 gains time ladder, clocks, condition
  schema, composition substrate, gate→fill generator, license schema).
- A2 fifteen converged strong defaults (each backed by ≥2 digests).
- A3 clarifications: refined rule-kind taxonomy ([D] [J:flag] [J:enum] [J:rung] [J:open] [T] [S] [N]),
  fast paths legitimate, P3 classification stands, solo reinterpretation, leniency is the dominant AI
  failure, P5 confidence definition required, VI scope, P9/P14, P17 generalized, rule-card delivery.

## Wave 2 launched — architect (00-architecture.md)

- Architect hit the session rate limit mid-arithmetic (before writing); resumed from its transcript. Advised to write in chunks so an interruption cannot lose the whole document.

## Wave 2 complete — 00-architecture.md reviewed and ACCEPTED
31.3k words + 8 data files (tags.yaml: 10 facets / 87 branches / 339 level-2 tags; effects.yaml: 38
core effects; boundaries.yaml: 53 reserved handlers). Orchestrator review: read in full (rules
00.1–00.17, contracts, glossary). Accepted, including one override of BRIEF A2 #15: DC ladder KEPT
(10/15/20/25/30) with calibration targets CT-1..6, because the arithmetic shows harshness came from
missing competence, not the ladder. Nat-20/1 one-step shift adopted.
BRIEF Addendum B written (retires §7 default +2 / free-integer DC; ladder decision; levers replace DC
flags; fixed harm magnitudes; reserved ids; parallel-writing protocol).
AUTHOR-BRIEF.md written (shared author instructions + contrib-fragment protocol).

## Plan adjustment: Wave 3a/3b collapsed into one parallel wave
00's contracts (00.17) specify every cross-chapter interface precisely enough that chapters can be
written against them before their providers exist ("a chapter may rely on a consumed interface
exactly as specified here"). So 01–12, 15, 16 launch together (14 authors). 13 (starter setting)
waits for them — it consumes every chapter's content schema and data. 14 (player's guide) stays in
Wave 6. Concurrency protocol: shared-file additions → data/contrib/<file>.NN.yaml; DL entries →
appendix/fragments/DL-NN.md; traceability → appendix/fragments/trace-NN.md; orchestrator merges.
Special coordination given to 04 ↔ 05: callings never own ability lists (C:P5); 05 authors one shared,
tag-gated ability pool; 04 grants tier "picks" from the pool gated by the calling's tags.

## Wave 3 launched — 14 chapter authors in parallel
01 Resolution · 02 Character · 03 Tags & Evidence · 04 Recognition & Growth · 05 Abilities/Focus/Magic ·
06 Conflict · 07 Harm/Recovery/Death · 08 Items/Loot/Crafting · 09 Adversaries · 10 Exploration/Travel/Sites ·
11 Living World · 12 DM Procedures · 15 Social/Investigation/Downtime · 16 Companions & Allies.
(06 and 08 needed a retry after transient permission-classifier errors.) Each author was told to
simulate its own math in scratchpad scripts where numbers matter (01 CT enumeration, 03 tally growth,
04 recognition pacing, 05 Focus economy, 06 fight pacing, 07 lethality, 08 loot distributions,
09 advisory calibration) and to write in chunks to survive rate-limit interruptions.
Queued for after Wave 3: 13 Starter Setting (consumes every chapter's data), merge of contrib
fragments + DL/traceability fragments, then Wave 4 verification.

## Wave 3 interrupted and resumed
- All 14 authors hit the account usage limit during their reading phase (no chapter files written yet). After the owner reported the limit reset, all 14 were resumed from their transcripts (reading preserved).

## Plan adjustment: Wave 3 serialized (owner request)
All 14 parallel authors hit the account usage limit a second time, again before writing anything
(the reading phase alone of 14 simultaneous agents exhausted the window). At the owner's request,
authors now run ONE AT A TIME, resumed from their transcripts, in 00.1.3's dependency order:
01 → 12 → 03 → 04 → 05 → 06 → 07 → 02 → 08 → 09 → 10 → 15 → 16 → 11 → (13 new) → (14 in Wave 6).
Side benefit: each later author reads the finished earlier chapters, so interfaces are checked
against real text instead of only 00's contracts. Authors told to minimize further reading and to
start writing immediately, in chunks.

## Ch.01 returned (34.1k words; DL-01-01..25; CT-1..6 proven by exhaustive enumeration)
DC ladder 10/15/20/25/30 confirmed (324 of 3,125 ±2 ladders pass CT; reference is central). Nat-20/1
one-step shift confirmed. Fate starts 1, cap 3. Repetition 0/−2/−4. Oracle yes 26/51/76/91.
Four additive 00 amendments APPROVED and APPLIED (near-miss wording, engine snags outside two-snag
count, stored-DC key, new frame fields). New file `_process/INTERFACE-REQUESTS.md` collects every
cross-chapter request so serialized authors see what is asked of them.
Next: ch.12 (resumed).

## Ch.12 returned (31.2k words; DL-12-01..20; oracles.yaml 33 tables; pacing.yaml; anchors.yaml compile spec)
12-step turn loop (state before prose; check_claims over 13 claim classes); pronoun rolled at first
mention (fixes the probe's pronoun slip); tension 1–9; pacing director; lead injection at 3 inconclusive
beats; spotlight rotation ledger. 00 amended (tools log_turn/revert_writes; prefixes anc./scn./trg.).
Next: ch.03 (resumed).

## Ch.03 returned (23.8k words; 832 tags; evidence.yaml; DL-03-01..25; simulation in _process/simulation/)
Accepted departures: DL-03-01 (deed significance computed from pre-roll frame fields, not fresh
judgment — constitution P5 wording refinement, queued for the v1.8.0 amendment); DL-03-09 (witnesses
never weight capability; they feed a separate public tally → reputation). Anti-grind verified by
simulation (rat grinder 340 vs 1,033 honest; uncapped would be 2,196). Calibration table handed to 04.
Next: ch.04 (resumed).

## Ch.04 returned (29.0k words; 183 callings; 36 hybrid pairs decided; DL-04-01..24; sim in _process/simulation/)
Confidence = count (0–5) of five confirmations (Current, Rising, Central, Leading, Margin), validated
against later play in simulation (37→97% hold rate from score 0→5). Hybrid trigger tuned to balance ≥ 2/5
(03's suggested 1/3 over-offered). Tier pacing 4/9/19/34/56 sessions. Issue I-003 (MAJOR) opened:
non-combat callings too slow at tiers 3–5 — to be fixed in Wave 5, not shipped as a fallback.
Next: ch.05 (resumed) with 04's explicit pool requirements.

## Ch.05 returned (33.1k words; 251 abilities / 499 ranks; 81 training licenses; 24 rites; 22 composites; DL-05-01..30)
All 04 pool-coverage requests met and machine-checked (ids, grammar, banned words, budget, coverage).
Issues opened: I-006 (Focus-binary equal-band fights — verify with real 06/09), I-007 (dark-calling
tier-5 abilities missing). Next: ch.06 (resumed).

## Ch.06 returned (33.8k words; 27 conditions; conflict.yaml; DL-06-01..26; sim 20k runs/row)
I-006 resolved for martials (mastery rule; 3-vs-2 actions). I-009 opened (Spent caster helpless → 05
adds zero-cost attack workings). ORCHESTRATOR DECISION DL-00-04: PC max Vitality +2 per power band
above 1 (cap 24), binding on 07/02/04. 00 amendments approved. Next: ch.07 (resumed).

## Ch.07 returned (31.4k words; 216 injuries; 18 afflictions; 9-option last-chance menu; DL-07-01..21; sim)
Two-Key rule fully specified (no check/clock/hazard/affliction kills). Menu reached per 100 lethal
fights (fighting on): trivial 0 / easy 1 / fair 5 / hard 26 / lethal 80; exits at Staggered cut fair
to 2. Mental strain named "dread". Vitality-by-band decision (DL-00-04) implemented. Next: ch.02 (resumed).

## Ch.02 returned (32.4k words; 8 peoples / 9 upbringings / 21 livelihoods; 117 birth-pool entries; 30 kits; DL-02-01..23)
Fast path (5 answers) + full + ready-made; fixed attribute arrays (no point-buy, P11); P4 trade-off via
Free (+5) vs Typical (+7) rules audited over 16 concepts; the Bent = post-creation deferrable variance (P1).
I-009 acceptance criteria tightened with ch.02's creation numbers; I-015 opened. Weekly usage limit hit
once during this chapter (resumed). Next: ch.08 (resumed).

## Owner instruction: pause after ch.08
Owner asked not to start the next author after ch.08 finishes. Remaining authors (09, 10, 15, 16, 11) and 13 stay paused, transcripts intact, until the owner says to continue.

## Ch.08 returned (26.4k words; 185 base items; 210 properties; 59 materials; 159 item-ability entries; DL-08-01..29; 3 sims)
"What does a dropped item grant?" (constitution P5 deferral) answered: mundane / passive / license / item
ability, with license and item-ability properties limited to the signature slot (≤1 per item). Item share
caps keep gear below callings (1,000/1,000 compliant). Issues I-016..I-018 opened.

## PAUSED (owner instruction) — Wave 3 status
Done: 00, 01, 02, 03, 04, 05, 06, 07, 08, 12 (≈ 307k words of rules + data).
Waiting, transcripts intact, NOT started: 09 Adversaries (a2d420c6…), 10 Exploration (ae096582…),
15 Social (ad80c681…), 16 Companions (a9288d92…), 11 Living World (a0bf1f99…). Not yet commissioned: 13
Starter Setting. Then integration, Wave 4 verification, Wave 5 revision, Wave 6 finalization.

## Resumed (owner instruction): ch.09 Adversaries started, alone.

## Ch.09 returned (29.6k words; 63 archetypes; 123 statted adversaries; 40 behavior lists; DL-09-01..24; sims)
threat_advisory estimator 90.4% exact / 100% within one word vs Monte Carlo (586 encounters). Menu rates
at or below 07's targets. I-011, I-013 closed. I-005 → ORCHESTRATOR DECISION DL-00-05 (relative challenge
band). I-019, I-020 opened (minor). Next: ch.10 (resumed).

## Ch.10 returned (35.3k words; 47 hazards; 8×14 site themes×domains; 20 traps; 14 weather states; DL-10-01..25; sims)
World as a place graph; one meaningful d12 per watch/site check; omens before every hostile encounter;
lost-ness sealed; sites as racing progress/danger clocks (Delve-style). `travel_points` 00 amendment
approved. I-021..I-023 opened (minor). Next: ch.15 (resumed).

## Ch.15 returned (37.3k words; social/investigation/downtime data; DL-15-01..31; sim)
Anti-seduction core: request ceilings by standing (above-ceiling = refused, not rolled); only four term
kinds shrink a request; closed list of things that never move a number (eloquence, flattery, assertion);
hard refusals; lies recorded with sealed truth and an exposure clock. Three Clue Rule engine-enforced;
core clues free; deduction confirmed only by fictional evidence. 00 amendments approved. I-024 opened.
Next: ch.16 (resumed).

## Ch.16 returned (34.9k words; 40 companion templates; 15 knacks; DL-16-01..22; 3 sims)
Band rule (allies serve one band below the PC; higher-band NPCs refuse to follow) keeps the advisory
contract to one word gentler. Loyalty = standing with sensed regard/grievance clocks, counsel before
resented deeds, three warnings before departure; betrayal needs Hostile + ultimatum + opportunity and
never harms the PC directly. Compromises accepted. Next: ch.11 (resumed) — last of the original authors.

## Ch.11 returned (36.0k words; 18 faction templates; world_turn/calendar/legacy data; DL-11-01..26; 2-year world sim ×300 seeds)
World Turn weekly in 8 steps, never touching the PC directly (traces and bangs only). First draft ran away
(47% of factions to tier 5) → tuned (halved goal ticks, tier-relative DCs, weight-of-size check) to 8%.
Hook supply: PC register < 3 open matters in only 4 of 104 weeks; never > 10.
ALL ORIGINAL CHAPTER AUTHORS COMPLETE: 00–12, 15, 16 (≈ 480k words + data).

## Wave 3c launched — ch.13 Starter Setting (new agent, alone)
Consumes every chapter's schemas and "13" requests; first content the owner's father will play.

## Ch.13 returned (20.5k words; region_thallen.yaml 381 KB; 64 places; 44 NPCs; 4 full + 15 petty factions; 3 cases; 6 pregens; 95-entry regional bestiary; DL-13-01..17)
Setting: the Thallen Vale under the Hush; haven Tolling; West Marches rings; the opening = the Last Bell
misses a stroke (public 6-segment clock, four solutions). Generator 0 errors/0 warnings; PR-10-8,
15.9.4, 11.3.1, 08.4.8 audits pass; world sim 2.6–2.7 goals/faction/year, tier-5 0% with 11.3.4 applied.

## WAVE 3 COMPLETE — all rules chapters authored (00–13, 15, 16; 14 is Wave 6)
Next: INTEGRATION (single agent): apply approved 00 amendments; merge contrib fragments into canonical
data files; apply all "(integration edit)" items to chapters; assemble decision log and traceability;
recompile anchors; full cross-file validation; integration report. Then Wave 4 verification, one agent
at a time.

- Pre-integration snapshot of rules/ saved to scratchpad/rules-snapshot-pre-integration (rollback point; nothing committed yet).

## Owner question: is a starter setting required?
Answer recorded: rules are setting-agnostic and generate most content; a setting supplies ~4 canon decisions (impossible list, magic/faith canon, peoples/tongues, haven + factions). Ch.13 kept as an optional module (useful for the first newcomer session and as the playtest bed); I-028 opened to add a world-seed procedure for setting-free play. Integration resumed.

## INTEGRATION COMPLETE (Wave 3c, cloud continuation)
Report: `_process/integration-report.md`. Validator: 0 ERROR / 0 WARN / 78 INFO (expected illustrative ids).
All 42 contrib fragments merged (data/contrib/ removed); 379 decision-log entries, all 414 cited DL ids resolve;
DL-INT-11 added; anchors recompiled (129, deterministic). Ledger: I-023/I-024/I-026/I-027 and I-005 closed.
New rows: I-029 (MAJOR, generic encounter tables fail danger-word audit), I-030, I-031, I-032 (MINOR).
I-028 (world-seed procedure) stays open for Wave 5.
Next: Wave 4 verification, one agent at a time — (a) simulation re-run + campaign sim.

## Revision A returned (progression and magic): report `_process/reports/revision-A-report.md`
Closed I-003, I-004, I-007, I-008, I-009, I-015, I-020, all with seeded-simulation evidence.
- Branch workings (05.7.11): a new caster wins 93% vs one T2; a Spent tier-3 caster wins 81–91% vs one T3. Casters stay below the martial baseline.
- Recognition parity: the envoy, smith and scholar reach tier 3 by session 17–18 vs 19 for the combat calling, and tier 5 by session 45–46 vs 51.
- Generators for ch.02, 04, 05, 08 and 09 now reproduce `data/` exactly; they had drifted, and hard-coded Windows paths were removed.
- Opened I-033 (T-05-9 prices lingering conditions too high) and I-034 (ch.04's pacing tables and worked example use the old opposition model). Both go to Revision C.
- I-025 closed as wontfix: per owner direction, the setting is not used.
Validator: 0 ERROR / 0 WARN.

## Revision B returned (world, encounters, DM, items): report `_process/reports/revision-B-report.md`
Closed I-001, I-016, I-017, I-018, I-019, I-022, I-028, I-029, I-030, I-031 and I-032.
- World seed: section 12.16 and PR-12-9, with `data/world_seed.yaml`. Seed 1, a player-guided seed and 200 random seeds pass all 62 checks, and 2,600 regional tables pass PR-10-8.
- Generic encounter word audit: 55/55 cases pass (was 7/55).
- Denizen tables: 560/560 pass.
- Loot repeat worst case: 14.6%.
- Campaign wealth sim: magic items were routine; drop rates retuned.
- Rules defect found by the agenda fix: a friendly faction aided the PC every turn. Fixed in 11.3.7 (c).
New rows: I-035 (wontfix, Vale), and I-036 (P3 item count 13 vs 8–12; coin sinks not modelled), assigned to Revision C.
Validator: 0 ERROR / 0 WARN. All data YAML parses.

## Verification returned (lean, Sonnet, about 365k tokens): reports `_process/reports/verification-*.md`
- 7 mechanical fixes (V1-001 to V1-007).
- Completeness: of R5's 189 rows, 175 are covered, 7 belong to ch.14, 5 are partial and 2 are missing (FN-11, FN-12).
- Red team: of 10 exploits, 5 are stopped, 2 partly stopped and 3 have no stop.
- One paper playtest in the seed world.
- I-010, I-012, I-014 and I-021 accepted.
- New rows I-037 to I-062: 5 MAJOR (I-037 to I-041), 21 MINOR.
Next: Revision C (Sonnet): the MAJOR rows plus the cheap MINOR ones; the remainder becomes open empirical questions with defaults.

## RULESET FROZEN AS v1.0 RELEASE CANDIDATE (owner, 2026-10-06)
The owner set a $20 budget and asked to get the system verified and ready for build planning.
- Revision C and Completion (ch.14, the constitution amendment, the editor pass) are cut for now.
- The 29 open ledger rows (5 MAJOR) stay open as known issues. They are summarised in `rules/README.md` and none blocks building.
- `rules/README.md` written: layout, tooling, known issues and build notes.
Next: tech stack and build planning.

## V2a returned: report `_process/reports/verification-2a-report.md`, plus `verification-constitution.md`
- Read ch.04–08 in full, by section, using rq.py: 14 fixes, plus an rq.py bug where fenced headings broke section ends.
- Constitution: Principles I–VII compliant; P5 and P14 deviate with DL justifications.
- New rows: I-063, I-064, I-065 (all MINOR).
Cost: 149 tools; see the usage line below.
- V2a usage: 273 turns, average context 298k (peak 516k), 81M cache-read tokens. Lesson: full reads still accumulate, so V2b is split into two agents of three chapters each.

## V2b1 returned (ch.09–11 consistency read): report `_process/reports/verification-2b-report.md`
- 14 fixes (V2b-001 to V2b-014), including stale ch.13 dependencies in ch.10 and worked examples re-rolled on the new tables.
- New rows: I-066 (lone minions on the generic tables), I-067 (guardian not available at the site's band), I-068 (sim models the entrenched penalty too broadly).
- V2b1 usage: 310 turns, average context 244k (peak 444k), 76M cache-read tokens.

## V2b2 returned (ch.12, 15 and 16 consistency read): appended to `_process/reports/verification-2b-report.md`
- 13 fixes (V2b-015 to V2b-027). The world seed is consistent with its data and example.
- New rows: I-069 (seed year vs wound age), I-070 (petty-faith clocks), I-071 (social-contest scope), I-072 (Devoted through a bond).
- Usage: 292 turns, average context 247k, 72M cache-read tokens.

## Lean agent experiment (2026-10-07)
- Added `.claude/agents/rules-worker.md` (tools limited to Bash, Read, Edit, Write, Grep and Glob). It is not picked up mid-session; it becomes available in the next session.
- Measured starting context: general-purpose 49k, Explore (restricted tools) 37k. Tool definitions are about 12k of the base; the rest is the system prompt. Expected saving is about 25% of the per-turn floor.
- Rule adopted: each agent is scoped to about 100 turns, where per-agent startup cost balances quadratic context growth.

## V2c1 returned (adversarial playtest, 8 scenes): appended to `verification-playtest.md`
- 8 fixes (V2c-001 to V2c-008).
- New rows I-073 to I-081. Two are MAJOR: I-075 (one dropped object wipes a mob) and I-080 (planted rumors start wars without limit).
- I-082 opened by the orchestrator: the harm generator is broken. It goes into Revision C, not a separate task.
- Usage: within its ~100-turn scope.

## V2c2 returned (long-arc playtest: scholar, tier 1 to tier 5, retirement and successor)
- 3 fixes (V2c-009 to V2c-011).
- New rows I-083 to I-087. One is MAJOR: I-083, no band-4/5 social or lore opposition in a seeded world, so the non-combat path stalls at tier 4.

## V2c3 returned (citations): `verification-citations.md`
- 39 unique URLs on 25 hosts; all unreachable under this environment's network policy (WebFetch blocked).
- Local cross-check: 38 of 39 sit alongside a research-digest citation; #22 (OSE morale) does not.
- I-010, I-012, I-014 and I-021 updated with these counts. Finishing needs the hosts allowlisted; the report lists them.

## Revision C1 returned: `revision-C1-report.md`
Resolved all 12 rows: I-038 (Oracle lever cap; sim shows +3.7 down to +0.8 per roll), I-046, I-048, I-052, I-053, I-054, I-059, I-062, I-071, I-073, I-074 and I-085. I-088 wontfix (ch.13).

## Revision C2a returned: `revision-C2a-report.md`
- Resolved I-037 (power_band counts confirmed tiers only), I-039 (faction tier lent only through someone with authority; contest band capped at power_band + 2), I-083 (the seed places band-4/5 NPCs; parity sim tier 5 at session 48–49 vs the archer's 52), I-063 and I-064.
- I-034 handed off. New row I-089 (pacing targets missed after the fixes; NPCs generated on demand have no band). Both go to C2b.

## Revision C2b returned: `revision-C2b-report.md`
- Resolved I-089: thresholds retuned to 160/340/640/1200 and targets kept; archer tiers at sessions 5/10/18/32/54; parity within ±20%, keeping crafted works at one opposition per scene.
- Resolved I-034 (pacing tables refreshed) and I-047 (training competence cap).
- I-087 partial: 43 level-2 nodes lack tier-4/5 abilities. Authoring them goes to C2c.

## Revision C2c returned: `revision-C2c-report.md`
- Resolved I-087: 123 new tier-4/5 abilities written through the generator. All 81 level-2 nodes now have both tiers, and the generator enforces it. Ladder check passes for all 183 callings.

## Revision C2d returned: `revision-C2d-report.md`
- Resolved I-033: the sim now tracks burning and bleeding, now priced at 1 EU per stack. Flame Lance rank 2 now beats the free working plus a push.
- Resolved I-043, I-044 and I-058.
- New row I-090 (pricing of item-property conditions in ch.08 and ch.09's estimator) goes to C4.

## Revision C3 returned: `revision-C3-report.md`
- Resolved all 9 rows: I-075 (dropped objects capped by size; sim section L), I-076, I-078, I-042, I-057, I-060, I-072, I-077, I-082 (the harm generator is byte-equal again).
- C4 and C5a are running in parallel worktrees.

## Revision C6a merged (worktree): `revision-C6a-report.md`
- I-065, ch.04–07: 188 cards gained card-level basis tags, plus 2 new DL entries; DL-INT-13 rejects a section-level basis.
- New validator check BASIS covers 04–07. C6b covers ch.00–03 and 08–16, about 557 cards.

## Revision C5a merged (worktree; ledger conflict resolved by row): `revision-C5a-report.md`
- Resolved I-040 (weak-PC reference at band 1, and a lethal-fight warning in play, 10.10.4), I-080 (rumors floor at −2 and once a season; war in 0/300 runs, down from 276), I-066, I-067, I-055, I-056 and I-051.
- I-045 measured; its text fix moves to I-095 (ch.04/02).
- New rows: I-095, I-096 (stale numbers in ch.12), I-097 (ch.13, wontfix candidate).
- Appendix and anchors rebuilt after the merge; validator 0/0.

## Revision C6b merged: `revision-C6b-report.md`
- I-065, ch.00–03: 141 cards tagged, plus DL-00A-33 and DL-01-28. BASIS now covers 00–07 (699 cards, 0 untagged).
- Remaining: ch.08–12 and 15–16, about 416 cards.
- Added `_process/merge_ledger.py`, which resolves ledger merge conflicts row by row.

## Revision C6c merged: ch.09–10 basis tags (133 cards, plus DL-10-31). BASIS covers 879 cards. Remaining: 08, 11, 12, 15, 16.

## Revision C4 merged (conflicts in the ledger, DL-09, the decision log and anchors resolved; C4's DL-09-26 renumbered to DL-09-28): `revision-C4-report.md`
- Resolved I-041 (non-enemies count weekly; no repeat loot for a season), I-036 (wealth sim with real coin sinks; T3 drop 25%), I-086 (patron job fees by band), I-079 and I-090 (on-hit stacks and estimator riders).
- New rows I-091 (ch.11/15 should cite job fees) and I-092 (crude-repair limit text).
- Ch.09 data regenerated, then the integration merge, appendix and anchors rebuilt. Validator 0/0.

## Revision C6d merged: ch.15–16 basis tags (130 cards; DL-16-25, DL-16-26). BASIS covers 1084 cards. New row I-105 (renumbered from I-098): tamed beasts may leave before reaching Neutral.

## Revision C6e merged: ch.08 basis tags (46 cards; DL-08-39..41); I-092 resolved; I-091 done for ch.15, with ch.11 still open. BASIS covers every chapter except 11, 12 and 13.
