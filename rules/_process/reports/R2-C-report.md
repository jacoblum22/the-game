# R2-C report: adjudication and difficulty (rules half of spec 007)

Scope: lane D (`research_notes/Playtest round 2 solutions/D_adjudication_difficulty.md`) P1-P5 plus the §5 sim;
owner rulings D3 (accepted), D6 and D7 (assumed, owner to confirm). Rule edits are tagged `[revision: R2-C]`.
Appended after every step.

## Step 0: setup (2026-10-08)
- Worktree reset to `milestone-1-playable` (16b92c2). Read CLAUDE.md, the synthesis (incl. §4 rulings) and lane D.
- DL entries go in `appendix/fragments/DL-01.md` (no DL-00 fragment exists; DL-12 is left to R2-B to avoid id
  collisions).
- 01.6.12 already exists ("Frame computation", cited by the engine), so the new critical-failure guard is
  **01.6.13**, not 01.6.12.

## Step 1: data (hand-written files, no generator)
- `rules/data/basic_verbs.yaml`: `anchor.obstacle_classes` (id, base tier, examples from T-00-5, T-01-2 and the
  01.18 cards) on Move 5, Observe 6, Recall 4, Talk 1 (`be_heard`; any resisting listener is 15.3.3), Strike 3
  (objects), Force 3 (objects), Exert 6, Evade 2 (cover), Handle 3, Setup 2. Grapple, Sneak, Endure, Help and Ready
  carry none (always opposed, effect or none). 12-compile_anchors ignores the extra key.
- `rules/data/resolution.yaml`: `dc_tier_rules.tie_break: class_base` (+ `nudge`, `no_class_fits`);
  `auto_commit` (default true, Safe only, `never: [risky, dire, lethal]`); `frame_guards` (one cited Precision
  snag; the critical-failure guard); `stakes_cost_menus` (stakes source -> cost menus; goodwill never harm).
  `stakes_flags.source.sources` is unchanged (the engine reads it).

## Step 2: sim `rules/_process/simulation/01-difficulty_rubric_sim.py` (seed 158; output committed beside it)
- Exhaustive d20 through `engine.resolve.odds.odds` / `roll.degree` (the T-01-3 enumerator; odds01.py was a
  scratchpad script, not in the repo). 72 acts (32 everyday, 17 T-00-5 anchor rows); PCs at 00.3.17's
  calibration modifiers (-1, 0, +2, +5, +9; lane D's draft +3/+7 replaced by the canonical P1 +5 / P3 +9).
- Acceptance (B): untrained on everyday Easy acts worst 45/10 pass; 0 unlabelled non-Dire unopposed CF>S pass
  (35 frames labelled long shot); P1 at Moderate 55% pass; CT-1..CT-6 pass; fights >= 3 distinct odds 73.1% pass
  (untrained alone 27%); class `other` 8.6% pass. **FAIL: worst success drop under injected errors is 35 points
  when a wrong nudge and a wrong snag coincide** (single error 25; rubric rows as authored 10). Not tuned.
- Design point found by the sim: a nudge must not cross the trivial line (a trivial class never rolls; a rolled
  class never nudges to trivial); otherwise one wrong nudge turns a no-roll into a 45% roll.
- Output is reproducible (re-run byte-identical).

## Step 3: rules (all tagged `[revision: R2-C]`)
- ch.00: 00.12.3 (`[D]`, computed gate, knack = edge); 00.3.8 (DC order stored → opposed/social 15.3.3 → rubric
  tier); 00.3.9(b) (one cited Precision snag); T-00-5 (rubric-class column generated from the data + everyday
  rows: crowd, unbarred door, carry, ordinary question); T-00-6 note.
- ch.01: 01.3.1 note (computed); 01.4.1 (UNCERTAIN reads the class base; COSTLY only for a party who would act;
  social-certain Talk does not roll); 01.6.4 (social always 15.3.3, cites T-15-3; item 4 = rubric tier); 01.6.5
  (CLASS + NUDGE decisions; "HIGHER" retired); T-01-2 (column + everyday rows); 01.6.8 (snag cap); 01.6.9
  (source = a party who would act; source fixes cost menus); 01.6.11 (source → menu table; I-155); 01.6.12
  (refuses a second Precision snag or an off-menu cost; then the guard); **new 01.6.13** (critical-failure
  guard); 01.7.1 (odds or the reason they're hidden; template words); 01.7.4 (D7); 01.8.1 and T-01-3 notes;
  PR-01-5 step 1 (code looks up the would-be licence).
- ch.12: 12.2.2 (decision 3: verb, target, 3 facets, question_kind + topic, shape; social-certain DECLARATION
  resolves without a roll; worst case extended); 12.15.2 rewritten as a template (word maps, one-line trades,
  mode wording, secret and long-shot variants, one menu convention for every pause).
- ch.14: 14.2.3 sentence; new 14.2.7 glossary card; T-14-1 `auto_commit` default on (Safe only).
- `data/SCHEMAS.md`: the new keys documented.

## Step 4: decisions, appendix, anchors, ledger
- DL-01-29 (I-158, D3 rubric + guardrails; cites the sim and its failed target), DL-01-30 (computed gate),
  DL-01-31 (cost follows source; I-155), DL-01-32 (D7, assumed, owner to confirm), DL-12-50 (Reader beat
  decisions), DL-12-51 (OFFER template, D6 assumed, owner to confirm). DL-12 ids start at 50 per the
  orchestrator's numbering note (39 is R2-A2's, 40-49 R2-B's); no DL-00 entries added.
- Appendix re-assembled; anchors compiled (0 errors, 0 warnings; three anchor hashes changed); validator
  0 ERROR / 0 WARN.
- Ledger: I-158, I-143, I-155, I-134, I-138 resolved (revision R2-C); I-146 (a, c) resolved, (b) left open.
  Not closed but touched: I-157(a) is answered by Observe / in plain view = trivial (its b, c are not R2-C's).

## Notes for the engine spec (spec 007)
- `reader_schema`: drop `gate`, `license`, `would_be_license`, `necessity`; add `against_will`, `uses_power`,
  `speech`, `question_kind` (6), `topic`, `shape` (now / queued / conditional).
- `check_gate` becomes a pure function (00.12.3); delete the G1-before-G3 and `_plain_form_of` overrides.
- `framer_schema`: `obstacle_class` (verb-scoped enum from `anchor.obstacle_classes`, plus `other`), `nudge_why`
  before `nudge` (−1/0/+1) and `nudge_fact`; no nudge across the trivial line; `frame_check` enforces one cited
  Precision snag and 01.6.13 (convert, then `long_shot`), and narrows threatened/alternate costs by
  `resolution.yaml#stakes_cost_menus` (`harm_only_when` for the observer source).
- Social beats never call the Framer for a tier; 15.3.10-certain beats skip it entirely.
- `auto_commit`: default on, Safe frames only (frame.py `auto_commit_allowed` currently allows Risky;
  `TurnContext.auto_commit` defaults False). Long-shot frames never auto-commit.
- `oof.offer_block`: render 12.15.2's template; menu convention at every pause; glossary 14.2.7 behind `?`.
- New rule id 01.6.13; 01.6.12 keeps its id. `engine/build/cards.json` was not rebuilt (engine/ is out of scope).
- The sim imports `engine.resolve.odds` / `roll.degree`; if those move, update the sim's import.
