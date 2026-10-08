# Research and design decisions: Adjudication

Background is lane D (P1–P5) and the R2-C report; nothing here re-argues them. Each entry is a decision the rules
left to the engine.

## R1. Computed gate inputs (00.12.3, PR-01-5)
- **Decision**: `compute_gate(verb, facets, method_text, held, rules, *, reading_known, forbidden, g4_fact)` is pure.
  Order: condition forbids → G4; cited G4 fact on record → G4; accepted crude fallback → G3 fallback; the covering
  verb (`grapple` without `against_will` → Talk if `speech` else Handle; `strike` with `speech` and not
  `against_will` → Talk); a *need*: a literal match of any verb's `excludes` in the method (Force lists "picking a
  lock"), reading writing with literacy on record (Observe + the reading words; needs `lic.lang.letters`), or
  `uses_power`. Need + held covering licence → G2; need without → G3 with the would-be licence (the licence id
  named in `excludes[].needs`, else letters, else the existing word match over licence data). No need: a held
  licence whose `crude_fallback.verb` is the verb (lowest `dc_shift` first) → G2, else G1.
- **Rationale**: the golden labels (P-122 threat G1, persuasion holder G2, lockpicking G3, witch-sight G3).
- **Alternatives**: keep the Reader's gate (rejected, DL-01-30); two-stage Reader (fallback if facets fail).

## R2. Necessity (01.4.1, 15.3.10)
- **Decision**: before framing, code decides: accepted fallback → roll; reading words on record the PC can read →
  trivial; a Talk beat to a present NPC at Neutral or warmer (unknown standing counts Neutral) that asks a plain
  question (a part with `question_kind` ≠ none), is not `against_will` and whose NPC has no recorded refusal → trivial (certain, no evidence). Both
  skip the Framer. After the Framer: a class whose base is `trivial` → trivial, no roll. Everything else rolls.
- **"Would act on a failure"** (01.4.1, 01.6.9): `parties_who_would_act(state, beat)` = present adversaries, NPCs
  Unfriendly or Hostile toward the PC, everyone in a running fight, and the beat's target when `against_will`.
  `established_stakes_sources` offers `aware_opponent_or_observer` only when that list is non-empty (replacing the
  costs.py ponytail).
- **Alternatives**: computing COSTLY fully before framing (rejected for now: height and other hazards are framed
  facts the Framer cites; a too-eager no-roll grants unearned successes).

## R3. Rubric in the Framer schema (00.3.8, 01.6.5)
- **Decision**: for an unopposed beat the obstacle is `{kind: "tier", obstacle_class, tier}`: `obstacle_class` is
  the covering verb's classes with a tier base (a `by_hazard` base is left to `other`) plus `other`; `tier` is
  null except with `other`. Then `nudge_why` (string, before), `nudge` ("-1" / "0" / "+1", a string enum: INV-3),
  `nudge_fact`. Social and opposed beats (Talk, Strike, Grapple, Force or Setup aimed at a creature) get only the
  opposed branch naming the target, plus `request_size` (R1–R5) for Talk.
- `frame_check` refuses: a nudge without a fact or a why; a nudge with class `other`; a nudge across the trivial
  line; a nudge citing the same fact as a cited snag (the sim finding, see R6). Default frame: `other` at Easy
  (lane D: "the class base for `other`, otherwise Easy"), or the opposed target.

## R4. Snag cap and guard (00.3.9(b), 01.6.8, 01.6.13)
- **Decision**: the Framer's snags are bare fact ids; code types the first as Precision (−2) and any second as
  Protective (stakes +1). The guard then runs on frames not Dire, not opposed/effect and not secret: convert the
  Precision snag to Protective (the rung added never sets lethal); if critical failure still exceeds
  max(5, success), set `long_shot`.

## R5. Alternatives (12.15.2 "Another way")
- **Decision**: computed in `frame_check`: the same DC with each other attribute the verb allows (`attribute` +
  `alt_attributes`); for an attack on a creature, the sibling verbs Strike / Grapple / Force / Setup against that
  defender's defense for each verb's `against`. At most three, best first; zero model calls.

## R6. The open sim finding (wrong nudge + wrong snag = 35 points)
- **Decision**: within the rules, `frame_check` refuses a nudge and a snag that cite the same fact (01.6.5: an
  intrinsic fact nudges, a situational one is a snag; one fact cannot be both). This removes the double count of
  one fact but not two different wrong facts, so the bound stays 35. A stricter bound ("one model-chosen modifier
  per beat", DL-01-29's revisit clause) is a rule change: ledger row, not made here.

## R7. OFFER template and menu (12.15.2, 14.2.7)
- **Decision**: `oof.offer_block` renders the 12.15.2 lines from the Frame only. Levers and snags are named
  generically ("a help +2", "a hindrance −2") because fact words would need string munging of predicates (the
  retired `_fact_words`); a typed fact label is a later improvement. The block is also the pause prompt.
- **Menu**: play-phase pauses print `[Enter] <label>` then `[x] label` per choice (commit d, go big b, play safe s,
  change c, withdraw w; other choices take the first free letter) and `[?] Explain`. Enter: an OFFER commits,
  except Dire, lethal or long-shot frames and every other waiting pause (near miss, redirect, last chance), where
  it shows the block again. Digits still pick (harness compatibility). Setup and creation menus are ch.02's, not
  12.2.6 pause points, and keep their numbers.

## R8. Golden-set measurement
- **Decision**: `evals/reader_golden.py --reader evals.reader_golden:haiku` builds the Reader packet from the line
  and its context string, calls `ask_claude(..., model="haiku")`, and scores the covering verb and the computed gate
  (`compute_gate` with licences parsed from the context). Necessity is not scored (it needs state the contexts do
  not carry). Answers are cached in `evals/baselines/reader_golden_haiku.jsonl` so the score re-runs offline.
