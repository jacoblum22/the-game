# HANDOFF 033 slice 1 (design only; no code changed)
Base: `spec032-base` at 8a8bcb8 (53875ef + one OVERNIGHT-LOG commit, no code difference).
Done: `spec.md` (R1-R13 = the owner's 13 rulings, assumptions A1-A11, SC1-SC5), `plan.md` (the DM contract table,
design per requirement, rules phase, phases with lanes, hand-done analyze), `cases.md` (C1-C12 from the data: 15 verbs,
9 foe acts x 6 states, 9 costs, footing S1-S5 options, leads, witnesses, walk-ons, testimony, retire, guard),
`tasks.md` (T001-T097 by phase), `contracts/dm.md.draft` (786 words; now 798; budget 800).
Core mechanism: `Beat.stated` (resolve/types.py). Set by dm-tools, it makes every guessing helper skip; the pipeline
(stated None) is untouched (R13).
Next: W1 in parallel: P0 guard census (Sonnet), P1 contract (Sonnet), R rules (Opus), E measures (Sonnet). Then W2
P2a, P2b, P4; W3 P3 with P5; W4 P6 strict guard and gates; W5 P7 live (orchestrator).
OWNER RULINGS 2026-10-10 (override spec/plan/tasks where they differ; tag edits [owner ruling 2026-10-10]):
- D1 = (a): the DM sees only the foe acts legal now; P7 measures passivity (strike share while engaged, waits/yields
  while unhurt). R rewrites 06.9.1 accordingly (the DM chooses for adversaries; the old research rationale noted).
- D2 = (b): foe acts are picked AFTER the PC's result is known, one extra DM call per settled fight exchange. Owner:
  "what if you grapple them on your turn and make their move impossible? Or push them off a ledge? ... we have to
  decide what the enemy does on their turn, even if it costs an extra Haiku call." Retires A1 (declare-with-move) and
  the lapse logic; the foe call runs in the world step after the exchange settles.
- D3 = default everything the DM omits, but LOG each default as `not_chosen:{field}` (screen.dm_tools.defaults) so P7
  can count them. No refusals for omitted details (retires A3's refusals: Force push/prone, fight `to`, fail_on).
  Defaults must be simple, documented in the contract table, and never read prose (e.g. fight to=near, Force=push,
  weapon=the wielded item else unarmed, as=they for people slots, foe act=the 06.9.4 row only as the logged default).

Traps:
1. 06.9.1 says "the DM never chooses for an adversary" (research-backed): R must rewrite it before P3 merges.
2. Footing forms depend on the severity, known only after the roll: pick on the answer turn (A4), never at propose.
3. Most `excludes` entries name no licence id ("a license"): R adds `covered_by`, or P2b has nothing exact to grant.
4. `dm_tools.py` is touched by P1, P4, P3, P5: stay inside the function lanes in plan 5; merge order is fixed there.
5. Re-record only `offline_seed11_dmtools`, never from two parallel phases. Files are CRLF in the working copy.
6. P0's census may find word matchers the inventories missed: assign each to a lane, else P6.

DONE W1 so far (orchestrator fold):
- E (07d05ea): `evals/turn_judge.py` replaces the keyword measures (leak, ask, mood, pronoun, absent), Haiku per sampled
  turn; precision from hand verdicts in `evals/baselines/turn_judge_hand.yaml` (not created; "unmeasured" under 20 per
  measure). npc_agency M10 and h2h_score read the judge cache. Nothing in evals reads `_audit`/`_log_only` any more.
- P0 (3e710a6): `tests/guard/` (viii9.py DENY 71, all `log`; scan.py + viii9_allow.py 235 hits: 100 P, 55 F, 7 S,
  73 `pending:<phase>`; census.py; reach-census.md). Full pytest 2498 passed, 5 skipped, 2 xfailed. Ruff on tests/guard needs
  `ruff check --config "include=['tests/guard/**/*.py']" tests/guard`.
Guard traps for every phase:
7. A phase that removes code deletes its `pending:<phase>` rows in `tests/guard/viii9_allow.py` and flips its DENY entries
   to `mode="raise"`; stale rows FAIL the static test. New word-reading code must be listed or (better) not exist.
   Regenerate `tests/guard/reached.txt` with `py -3.12 -m tests.guard.census reached`. P6 sets `STRICT = True`.
8. `dm_tools.tool` swallows exceptions: the runtime test asserts `g.raised()`. Deny only code a phase stops calling
   (`_fitted`, `lift_or_carry`, `reverses`, `plain_reading`, `certain_talk`, `looks_here`, `apply_change`, `typed_goal`
   stay called; P2b settles `certain_talk`/`looks_here`, not in plan R7).
9. New finds: `anchors._intent_hits` (D20) -> P2b; `gen.npc.role_implies` (role words imply age/pronouns) -> P4.
   A21 (`npc_leaves` default place in `_change`) has no function to deny: P4 deletes it. `classify_seed.py` dies after P6.
- R (R2-M, report `rules/_process/reports/R2-M-report.md` has the engine checklist per phase): DL-06-40 foe acts picked by
  the DM after the result from new T-06-16 (omitted/outside = first legal behavior-list row, target PC, logged
  `not_chosen:foes.<id>`); DL-06-41 start band default near (`not_chosen:fight.to`), Force default push
  (`not_chosen:force`); DL-01-60 footing form picked after the roll among options that can land, default first that can
  land (`not_chosen:cost_form`); DL-01-61 `resolution.yaml#reverses_goal`; DL-01-62 `basic_verbs.yaml` `target_kinds`,
  `covered_by` (+ `covered_by_effect` for flight); DL-12-160 leads/witnesses told never spawned; DL-12-161 no deduction
  from words; DL-12-162 retire by `/retire` or `end_game`. Both replays re-recorded at the merge (GUIDANCE size only).
10. Plan contract cells REFUSED (force, fight `to`) and re-ask (`cost_form`) are superseded by D3 in the rules.
11. P3: behavior lists hold rows outside T-06-16 (Windup, Flank, Reload): skip them, else `wait`. A Dying PC is a legal
    target only for a `kill` side. An IDLE exchange makes no foe call.
12. P5: 12.8.4's stalled-thread fallback is code-fired; check the tools path never reaches it.
- P1 (c07a2ed): `Stated`/`Beat.stated` (None on the pipeline, excluded from dumps); schema fields per the final contract
  table in P1's report (copied in tasks.md P1 notes if present): as/force/weapon/nonlethal/reads/approach/fail_on/
  move_to+change_whom; `change position` wired (`_position`); `end_game` stub; `cost_form` schema only; `foe_schema(legal)`
  for P3 (unused yet). `schemas.SchemaContext.approaches` = the 13 whole `excludes.what` strings. dm.md 780 words.
  Full pytest 2517 passed.
13. Every schema object is all-required: "omitted" arrives as "", "none", "plain" or false. `ScriptedModel._dm_defaults`
    fills missing DM keys so old scripted tests stay valid.
14. P2a: `_VERB_GOAL` is gone (untyped beat -> Change None). `_propose_roll` still appends " (nonlethal)" to the method:
    P2a removes it and switches harm to `stated.nonlethal/weapon/force`. Nothing reads `stated` yet. `_position` has no
    reach refusal.
15. P4: `_party`, `_walk_on`, `new_npc`, `new_item`, `_fight` ignore `as`/`name`/`knows`; P4 logs `not_chosen:as`.
    P2b: nothing reads `stated.reads`/`stated.approach` yet; approach values are whole `excludes.what` strings.
- P2b (764dbbd): gate checks `stated.approach` vs every verb's `excludes` (G2 if a `covered_by` licence is held or a
  `covered_by_effect` active, else G3 naming `needs`); reading = `stated.reads`; necessity `certain_talk`/`looks_here`
  structural (stay called); frame lift/attribute/reversal by typed fields and `reverses_goal` (`reverses(cost, beat,
  state, rules)` now needs `rules`); anchors keyed by exact `intent_verbs` ids; `scene.focus_of(beat)`. Word paths kept
  in `_*_by_words` helpers that only the pipeline calls. `resolve_names`/`_PROPER_RUN` are WATCH class S (recall search).
16. `words:re:findall` and `words:_STOP` rows are `pending:P2a` (only `pipeline._moved` reaches `gate.words`): P2a's
    merge must delete them if it removes that call. `code_framer` has `focus=focus_of(beat)` (P4 merge touch); P4 still
    owes anchors `[verb_anchor(verb, rules)]`.
17. Open for rules/P7: `covered_by_effect` sees only condition-carried effects (`eff.movement_mode` also covers climb and
    swim); `reverses_goal` has no `restrain` row; the tools path never sets `asks`, so plain questions always roll.
- P2a (29cb7aa): positions only from `stated.position` (`pipeline._stated_position`); Strike/Grapple write no band; Force
  ladder by reach (C2) from `stated.force`; no code-started fight for a stated beat; untyped Grapple holds nothing;
  `change_kind=free` ends holds (`end_hold`); weapon/nonlethal from `stated` (`strike_harm_by_words` pipeline-only);
  costs: `fail_on` for exposure/gear/closed_door (default target or wielded item, `env.defaults` gets
  `not_chosen:fail_on`); footing deferred: `costs.footing_options`/`pending_footing` (meta `footing_pending`)/
  `apply_footing(tx, rules, pending, cost_form)` -> (option, defaulted). Stated `change_kind=none` rolls (no GOAL_ASK).
18. P3: show `footing_pending` options on COST TO SHAPE, call `apply_footing`, log `not_chosen:cost_form` when defaulted.
    Drain `PipelineEnv.env.defaults` into `screen.dm_tools.defaults` on the propose and answer turns (not done yet).
19. Footing with no opponent: `restrained`/`trapped` write a hold with no holder entity (source = frame) and S3's default
    is `restrained`: watch in P7. `lower:` options need `data["lower"]` on a place; none generated today.
20. Guard rows found only by reach flicker: `oof.price_line` COST/SEVERITY_WORDS and `redirect_block:_LEARN` (F) were
    removed as unreached at this merge; re-add as F when P3's foe path reaches them again.

