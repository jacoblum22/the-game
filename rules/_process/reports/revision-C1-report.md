# Revision C1 report

Agent C1. Rows: I-038 (MAJOR), I-073, I-062, I-048, I-074, I-054, I-059, I-053, I-052, I-085, I-071, I-046.
Chapters touched: 00 (T-00-20, 00.3.9 pointers), 01, 03, 05, 12, 15, data, generators. ch.13 untouched. Nothing committed.

## I-038 (MAJOR) free Oracle lever-fishing (done)
- Design. The ledger default dropped the odds one rung per Oracle lever used. Rejected: 01.15.2 sets odds from the
  world only ("never from what the player wants") and 12.6.3 keeps the dial off player questions; shifting odds to
  punish fishing would make the world less likely to hold a ledge because the player asked, and would also bend
  honest world questions. Chosen instead: odds stay honest, the *conversion* of a free answer into a lever is capped.
- 01.15.8: a **free fact** (an Oracle answer to a player's question; 01.15.5 now logs the asker) is (a) at most one
  lever per roll, (b) a lever on at most two rolls per character per scene, (c) never the Protective lever that takes a
  lethal frame below Dire. Past a cap the fact is true and still makes methods possible; it becomes a lever only when
  *worked* by a Setup (01.14.9), which costs the action and risks a roll. Narrated, generated, observed or DM-asked
  facts are not free (WE-01-3's trough was write-on-mention, so it stands). The OFFER names free-fact levers and the count.
- Sim: `_process/simulation/01-oracle-fishing.py` (seed 38, 20,000 scenes a cell; output committed alongside). Old rule:
  +3.66 a roll at three questions a roll, +3.99 at six, on every roll. New, cap 2: +1.33 / +0.80 / +0.50 a roll over
  3 / 5 / 8-roll scenes, identical at 1, 3 or 6 questions a roll: fishing harder buys nothing. Cap 1 (+0.40 at 5 rolls)
  was judged too stingy for honest environment play; cap 3 lets a 3-roll scene run at +2 a roll.
- Refs checked: PR-01-4 step 8 (logs asker), 01 edge cases "argues for a lever" and "Fishing with the Oracle", 00.3.9(a)
  (pointer), 12.6.2 (DM questions; unchanged, consistent), 01.15.7 (unchanged). DL-01-26.

## I-073 G4 zero reach with a total potency (done)
- Ledger fix adopted as proposed. 01.3.7 test 3 gains a `[D]` counting rule: a **total** POTENCY (the target cannot be
  affected by this kind of method at all: no mind for Talk or Handle, no body for Grapple or Strike) counts as two
  factors, so alone it is G4 unless an offset cancels one; partial potency is one; **one reason supplies one factor**
  (the "no mind" fact cannot be cited again as QUALITY). Inside example added: "I shout the barred gate open" → G4,
  redirect to the bar (Exert) or whoever is behind it (Talk); outside: shouting at the guard (G1). A listener behind the
  gate is a different target: re-PARSE.
- Refs checked: 01.6.10 test 2 (now cites the count), PR text at 01:227, 15.2.3 and 15.3.4 (cite test 1 only:
  unaffected), 12.16 canon rows (test 2: unaffected). No number. DL-01-27.

## I-062 one knob for a feature's duration and growth (done)
- Ledger fix adopted with one change: no new knob name. T-00-20's `duration` is redefined as a feature's whole
  behavior over time (length and growth, spreading, fading: one knob); a new knob would have broken every
  `anchors.yaml` card and the compile's closed-list check for no gain. Where a created feature sits is the beat's
  target, not a knob. Text in T-00-20, 00.6's anchor property 2 list, 01.5.3's knob bullets and 12.13.3.
- 12.13.3 now works the playtest's case: `anc.06_t9_31` lists only `reach_unit`, so a stationary doorway fire
  re-anchors to `anc.10_12_9` (hazard no one listed) with one knob (`duration`), not a split; outside example: severity
  + spread + action cost = three knobs → re-anchor or split. Checked against `anchors.yaml` (knob lists read by script).
- Refs of T-00-20 checked (01.5.3, 01.18 intro, 02/06/09/16 anchor tables, 12.13.5 compile): knob names unchanged, so
  anchors recompile identically. DL-12-27.

## I-048 terms make requests certain (done)
- Measured first: new seeded sim `_process/simulation/15-certainty-sim.py` (seed 48, 200,000 requests; output
  committed). `15-social-sim.py` does not model certainty, so the new sim states its request mix openly.
- Design: the ledger default ("original size R2 or less") is right for Neutral but would break Friendly and Devoted,
  whose certain ranges reach R2 and R3 with no terms. Generalised: the **certainty size** = size minus *at most one*
  term; terms still lower the effective size for the DC and the ceiling. Neutral: R2 + one term is certain, R3 + two
  terms rolls at R1's +0. The ledger's second half kept: an Obligation term counts toward certainty only while the PC
  owes this NPC no undelivered commitment.
- Result: certain beats 37.7% → 32.0% (honest player), 53.6% → 38.8% (always two terms); certain R3+ requests
  39.6% → 8.2% (optimizer). 15.3.10, 15.3.4 (pointer), `social.yaml#request_rules` (`certain_when`, `certainty_size`).
- Refs checked: 15.3.x PR-15-1 step 10, 15.4.x certain cases (no terms: unchanged), 16.3.3 hires (wage terms), 16.14.2
  renewal (WE-16-2: R2 − one term = R1 at Warm: still certain), **WE-16-1 Oda** (R3 with two terms was certain: now a roll
  at DC 10, 60%, success; boundary pair unchanged). DL-15-33.

## I-074 requests that defeat a want; fear as term and snag (done)
- Ledger fix adopted. 15.3.2: a request whose granting defeats a recorded want counts one rung higher (cap R5),
  `[J:flag]` with a want id, uncertain → true (grant-side); never certain. 15.3.10's hesitation test names "a recorded
  want the request defeats". 15.2.2 item 6 added. 15.2.5 item 3 does not apply when the request's Leverage term is the
  same fear (one fact is one term or one lever, never also a snag); 15.3.5's one-fact rule states it.
  `social.yaml#request_rules.defeats_want`. Sim: want-defeating requests certain 37.8% → 0%. DL-15-34.

## I-054 refusal coverage by whose act; certain beats show "no evidence" (done)
- (a) Ledger default ("covered only when granting requires the NPC to do the refused act") sharpened, because a
  conduct-only reading would let a PC ask a "will not harm an innocent" NPC to tell a killer where the child sleeps.
  Each refusal kind now carries `reads: conduct | outcome` (`social.yaml#refusal_kinds`, all 17 kinds; T-15-6 header).
  Conduct kinds (open_law, wilds, bribe, past, place, magic, lend, oath, fight) cover only the NPC's own doing; asking
  them to let, send, equip or advise someone else is an ordinary sized request. Outcome kinds (family, innocent,
  master, closed-door, archetype, oath- and duty-sourced) cover any act of theirs that knowingly brings it about,
  including helping another. 15.2.3 COVERS states it with the ferryman's punt and the killer examples.
- (b) 12.15.3 RESULT gains the no-roll line: `[RESULT] no roll (certain: Neutral, R1) · granted · no evidence`, and
  `evidence as a no-roll success` for 03.3.2 D1's no-roll bases. 15.3.10 states that a certain beat's necessity reason
  is `trivial` (03.2.6), `social.yaml#request_rules.certain_yields_evidence: false`. DL-15-35.

## I-071 which Talk beats are a social contest (done)
- Ledger fix adopted, with debate added: 03.4.3's list is the narrower one and is now closed and named by method id
  (`smethod.request`, `bargain`, `deceive`, `intimidate`, `interrogate`, and every beat of a campaign or a debate);
  never win over, provoke, perform, command or read. Debate is added because 15.3.11 already names a council's patience
  as a contest clock and a debate moves a party's decision. 15.3.11 now cites 03.4.3's list; `evidence.yaml#
  challenge_band_source` names it. `04-recog-parity.py`'s envoy plays requests only, so its medians stand unchanged
  (no re-run needed: no input it reads changed). Note for I-039 (open, another agent): this edit changed only the
  method clause of 15.3.11 and 03.4.3; the "speaks for a faction" target clause is untouched. DL-03-28.

## I-046 two meanings of "brink" (done)
- Ledger default adopted: chapter 07 keeps "brink". The contest flag is renamed **one from full** in 03.4.5 (flag
  and crisis line), 03's frame schema (`contest.one_from_full`), 15.3.11, 15.9.20, 08.6.4, 04.3 parity note and OEQ-04-10,
  and `evidence.yaml` (flag key, crisis formula, frame field). A grep for "brink" outside ch.07/07's data, 11's
  legacy lines and 12's dying row (all 07's sense) is now empty in rules and data. `04-recog-parity.py`'s internal
  variable `brink` is left (process code, no rule text; output unchanged). DL-03-29.

## I-052 keeper schools gate priests; keeper nature (done)
- Ledger fix adopted in full. 05.7.4: a keeper grants only what it keeps (PC, pregen or NPC priest); a school no
  regional keeper keeps has no divine path (G3 redirect); the keeper record carries `nature: sacred | profane`, read by
  every "sacred/profane keeper" effect (Rebuke, 05.7.11; T-05 branch-working row points at it). 02's Acolyte row
  (keeps the chosen school), 12.16.6 (nature; main keeper = first not profane), 12.16.16 (the Acolyte pregen trains a
  school of the main keeper: healing if kept, else the first, with the matching suggested technique).
- Data and generator: `world_seed.yaml#tbl.12.seed.keeper_form` rows carry `nature` (pact: profane; `dark: true`
  removed). `12-world-seed.py`: keeper `nature` replaces `dark`; `make_pregens` picks the school from the keeper;
  cast NPCs' divine licenses are filtered to their faith's keeper's schools; seed check `keepers` requires a nature,
  `pregens` requires the pregen's divine schools in its keeper's, `npcs` requires every NPC divine license in its
  faith's keeper's schools. Seed 1's acolyte is now `deed.divine.smiting` / `ab.smite` under Oswen (was healing).
- `abilities.yaml` `ab.rebuke` text already says "sacred/profane keeper": now defined, unchanged. DL-05-35.

## I-053 nonsense wants; officers who will not fight (done)
- Ledger fix adopted at the source, not in `world_seed.yaml`: the generic tables (`oracles.yaml`, owner 12) are the
  ones 12.11.1 rolls for every NPC at runtime, so constraining only the seed would leave live play broken. Each
  `tbl.npc_want_verb` row has `takes` (the object rows it can govern); a misfit steps down the verb table (wrapping):
  deterministic, still rolled. Four objects reworded so outcome-shaped objects have verbs: "a debt cleared" → "a
  debt", "an enemy's downfall" → "an old enemy", "a rival's ruin" → "a rival", "a child's future" → "a child". Every
  object has at least two verbs (asserted in the edit script). `tbl.npc_refusal` row 12 (fight) gains
  `not_for: [deed.martial]`, same stepping. 12.11.1 states both ("Rolls that must fit"); 15.3.5's and WE-15-x's
  examples now read "repay a debt" / "escape × a debt".
- Generator `roll_want`/`roll_refusal` + seed check `npcs` (every want fits, no `not_for` refusal). Seed 1 now: "punish
  a rival", "earn a cure", "escape a debt", "find peace and quiet"; no martial officer carries `refusal.fight`
  (the council's officer and the innkeeper still may). DL-12-28.

## I-059 seed NPCs carry competence and licenses (done)
- Ledger fix adopted. 12.16.11: every cast NPC is written with `competence` (each role tag at its band's `c_b`,
  T-09-2) and `licenses` (each level-2 role tag's domain training license at trained; a teacher's target at expert, a
  tongue or letters held), so 15.11.1's MENTOR test reads the record. `world_seed.yaml#defaults.npc_competence`.
  Seed check `teachers` now fails a teacher whose record does not hold its target; `npcs` fails missing fields.
- Re-verified: `12-world-seed.py` RESULT PASS; 62/62 on seed 1, guided run 0 fails, 200 oracle seeds 0 fails. Output
  and example regenerated and committed in place. `10-word-audit.py` output byte-identical (imports the builder).
- ch.13's pre-made region (informational, unmaintained) now shows 54 of 62: four new gaps (keepers lack `nature`,
  twice through `02_keepers`/`04_keeper_axes`; cast lacks competence/licenses; teachers' records do not hold their
  targets). Logged as **I-088, wontfix (owner: setting not used)**, like I-035; ch.13 untouched. DL-12-29.

## I-085 world time against play time (done)
- Ledger proposal adopted with the sim it asked for: `_process/simulation/12-time-pacing.py` (seed 85; output committed)
  imports `04-recog04.py` (200 seeds × 60 sessions, archer and swordsman, unchanged engine) and lays each career on a
  reference schedule (adventures of 2–4 sessions at 2–10 world days a session, 1–6 weeks of downtime after each,
  optionally one season-long downtime a year), then joins it to `11-world-sim.py`'s weekly throughput.
- Results: 1.94 weeks a session (no long downtime) / 2.37 (with); tier 5 at 2.1 / 2.6 world years (archer), 1.3 / 1.5
  (swordsman); a season every 5–7 sessions; 11-world-sim's 19 threads per 104 weeks → 2.8 / 2.3 sessions a thread,
  inside the 2–4-session adventure assumed, so the two sims agree. Aging within 60 sessions: only PCs who start old
  (about three checks, any people with aging ≤ 55); grown humans, orcs, halflings: none.
- Decision: the reference is a **calibration and review target**, not a constraint (sessions are not time, 00.7.9).
  New 12.7.7 states it and what it implies; aging is a long-campaign rule by design (old PCs, timeskips, successions),
  stated in 11.10.5; 15.10.1 cites the downtime the calibration assumes. `pacing.yaml#world_time` holds the numbers
  and a review band: `h.12.session_close` flags two seasons in a row outside 3–10 sessions a season (12.12.4 extended).
  T-12-14 names the key. Season-paced growth checks out: ally growth (one band a season, 16.10.1) can track a PC's
  tiers (1–3 seasons a tier). DL-12-30.

## Close-out (done)
- DL entries: DL-01-26..27, DL-03-28..29, DL-05-35, DL-12-27..30, DL-15-33..35. `appendix/decision-log.md` and
  `traceability.md` re-assembled with `_process/simulation/integration-assemble-appendix.py` (no trace fragment
  changed, so the matrix is unchanged).
- `12-compile_anchors.py`: 129 anchors, 0 errors, 0 warnings (only source hashes moved).
- New sims, seeded and reproducible (re-run, byte-identical): `01-oracle-fishing.py` (seed 38), `15-certainty-sim.py`
  (seed 48), `12-time-pacing.py` (seed 85); outputs committed beside them. `12-world-seed.py` output and example
  regenerated (RESULT PASS; 62/62; guided 0 fails; 200 oracle seeds 0 fails). `10-word-audit.py` byte-identical.
- Ledger: the 12 rows resolved with evidence. New row **I-088** (ch.13's pre-made region fails the four tightened
  seed checks), wontfix, owner: setting not used.
- Validator: 0 ERROR / 0 WARN. Nothing committed. ch.13 untouched.
- Overlap note for whoever holds I-039: 15.3.11 and 03.4.3's *method* clause changed (I-071); the *target* clause
  ("a principal or someone who speaks for a faction") was left untouched for I-039's binding-party fix.
