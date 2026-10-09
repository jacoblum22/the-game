# Implementation results 022: mechanics as state (F5) + the Fixer on Sonnet (F6)

Branch `worktree-agent-a3bafb13703d6c8e1`, built on `milestone-1-playable` 3e660b3, with spec 020 (cb5e20d) merged in
mid-work. Real numbers below; nothing faked.

## Trace (before design)
I3's causes confirmed on the save records: 233000 has no `condition_applied` on Dunwen, grapple frames typed
`restrain`, foe hits on turns 4/6/10/14 while `posture = held fast by you`; turn 14 is `ruling_logged g4` (583) then
the strike 1 → 0 (584), staggered (585) and a round (587); 192926 turn 7 declares "The coin for the round is spent
whatever the answer" with no coin write, although the PC has a `coin` quantity; 233000 turn 15's take-back reverted
578-586 with no line saying Vitality came back. The 15 disputes are seven reports (2-3 complaints each).

## What was built
- **The hold is a condition** (06.5.2, DL-06-31): `change.hold`/`LADDER` apply `cond.grabbed` S1/S2,
  `cond.restrained` or `cond.pinned` by delivered reach (tightening one rung), source the holder. An untyped Grapple on
  a person keeps hold (06.5.2's Decision). T-12-18's posture rows write only while the condition stands;
  `conflict.end_hold` removes the conditions and the posture/held face together (break free, `free`, holder down or
  moved away). The text-matched `scene_state._holds` is deleted.
- **`foe_beat` row 2 first** (06.9.4): a held foe breaks free (its line's attack vs the holder's Might defense; a
  critical leaves the holder off balance) and never strikes that turn.
- **Folded grip** (spec 020 hand-off): `_fold_methods` marks the goal beat `holds: <target>` when it folds a hold;
  `pipeline._folded_hold` applies the hold at the goal's delivered reach on success, none on failure. The narrator
  sees the condition in the view; no posture row is written for a folded grip (the goal's verb has no Grapple row).
- **A refused turn spends nothing** (01.3.6-7): `world_step` gives no foe a beat when every beat was refused, so no
  round passes either.
- **Payments are writes** (01.11.2, DL-01-40): `change.price`/`pay` deduct the coin a declared method consequence
  hands over, at RECORD, whatever the degree; `Changed:` shows coin.
- **The Fixer** (`engine/dm/fixer.py`, `prompts/fixer.md`, `Role.FIXER`): six read-only tools (turn record with every
  write and REVERTED marks, entity state with provenance and facts naming it, transcript search, recompute, ledger,
  said vs record), 3-6 calls (up to 3 per answer; the last answer is forced to decide), then complaints with
  verdict, `found` and proposals.
- **`dispute.py` rewritten** (1289 + 167 lines → 575 + 477): validates each proposal (mechanical changes cite record
  ids the tools returned, INV-9; sealed and clue-trail facts and identity fields refused; quantity bounds; 12.5.8's
  take-back limit), applies all valid ones on one snapshot (take-backs first), answers found → Done/Not done → one
  `Now:` line, logs one ledger record per complaint under one report id and one review-log block per report.
- **Model**: `Routed` in `engine/llm/base.py` sends `Role.FIXER` to its own model; `evals/playtest.py --fixer-model`
  (default `sonnet`); the Gemini path's slot is `GameConfig.models["fixer"]` (exists via `ROLE_IDS`; not run).
- `pacing.yaml#feedback.understand_call` and `feedback.outcomes` deleted. Validator 0 ERROR / 0 WARN.

## Retired, and what supersedes it
| Retired | Superseded by |
|---|---|
| The hold as scene text (`restrain` words in `change.py` as its only record) | the 06.5.2 condition; posture is its face |
| `foe_beat` striking while held | `beh.default_melee` row 2, break free first |
| Coin spent only as text | `change.pay` at RECORD |
| The silent take-back | every Fixer restore ends with `Now:` (12.5.8, DL-12-106) |
| The one-shot `understand` call, `Role.UNDERSTAND`, its prompt, `_claim`'s fixed branches and outcome table | the Fixer's tool investigation + code validation |
| Pinning complaint text (`correction.N`) | typed values only; report text is refused as a value |
| Settling complaints one by one (and the old reliance CHOICE pause) | one snapshot, all proposals applied together; a take-back is proposed and applied |

## Gates
| Gate | Result |
|---|---|
| Full suite (after the final merge; milestone unchanged since cb5e20d) | **1794 passed, 4 skipped, 0 failed** (baseline before 022: 1786 passed) |
| ruff on touched files / whole tree | clean / 4 pre-existing E741 in `evals/orchestration/resolve_rules_merge.py` |
| pyright on touched files | only pre-existing env errors (pydantic/pytest unresolved under uvx; `playtest.py` lines 78, 287) |
| `longhorizon.py --mode scripted` | **0 engine errors** (382 turns, 308 narrated) |
| `validate_ruleset.py` | 0 ERROR / 0 WARN |
| Held foe, from saves (`test_mechanics_state.py`) | **9/9** foe beats that hit while held (135049 t7, t10; 145430 t9, t11, t15; 233000 t4, t6, t10, t14), re-run with the hold RECORD now writes: a break-free attempt, no blow, Vitality unchanged |
| Refused turn (233000 t14) | no foe action, Vitality and round unchanged |
| Silent take-back (233000 t15 report) | now ends `Now: Vitality 1/12 (was 0/12) · state bloodied (was staggered)` |
| Payment (192926 t7) | 1 coin deducted; 0 of the 4 offers in the saves deduct |
| **Round-6 15 disputes, Fixer on Sonnet** (hand-graded by I3's standard; was 1 right / 6 unclear / 8 wrong) | **10 right / 3 unclear / 2 wrong** on the first run. Unclear: 192926-d3 (coin taken, but 2 coins, an amount the record does not give), 232941-d2 (keeps the friend bond, but excuses Lilett's line instead of calling it a slip), 233000-d4 (says the threat was refused, not what was counted against it). Wrong: 192926-d5 (removed the carter's clue pointer to Ivas), 232941-d3 (wrote she/her over the record's he/him). Code now refuses both of those edits (identity fields and the clue trail), replayed in `test_feedback_corpus.py`; the model's own words still claim them, so with the fix: 10 / 4 / 1 (tuned on this set; not a clean number) |
| **Held-out 7 complaints** (labelled and committed in 636a9f1 before any run) | **4 right / 1 unclear / 2 wrong**. Wrong: h1 (a held foe's crutch blow: the Fixer accepted the old Framer's "she can still act while held") and h7 (the "straining against you" self-snag: it defended the snag). Both are rule knowledge the Fixer is not given. Unclear: h2 (right numbers, invented reason for the crit). The prompt was **not** tuned on them |
| `feedback_corpus.py` (spec-014 corpus, 11) | before 014: 1/11 outcome; 014 after (Haiku, tuned on this corpus): 11/11; **022 Fixer on Sonnet: 7/11 outcome class, 6/11 category+turn**. Three of the four misses are the 145430 purse "lift" whose frame was a misread grapple: the Fixer took the turn back where the 014 labels say explain; I read the Fixer as defensible there. short-nero: took back the turn instead of accepting the reading |
| Fixer investigation size | 3-6 tool calls per report (corpus/round-6/held-out: 3-6), 2-3 Sonnet calls per report, about 20-40 s each |
| **Live fighter run** (Haiku engine, Sonnet player, `--turns 15`, quick setup; `evals/playtests/20261009-153754-claude-fighter.md`) | 33 inputs, exit 0, 17 findings. Models: play roles all `haiku` (29 calls), **`fixer` 3 calls on `sonnet`**. **Holds: 0** (the player never grappled; no hold to test live). Foe hits: 1 (turn 14, not held). **Foe hits while held: 0** (none possible). `/fix` 1: the Reader picked an unnamed "challenger"; the Fixer took turn 4 back with `Now:`; the player's next note: "The fix was accepted and the turn was undone cleanly. Good. The correction text was a bit wordy, but clear." |

## Out-of-lane edits (one line each)
- `engine/dm/scene_state.py`: the posture is the condition's face, so its writer and the release must read the condition.
- `engine/dm/world_step.py`: the free strike after a refused turn happens here (`foes_act`).
- `engine/dm/roles/reader.py` (one line in `_fold_methods`, two in `ReaderBeat`/`plans`): spec 020's hand-off.
- `engine/dm/oof.py`: `coin` in `_SHOWN_QTY`, so a payment shows in `Changed:`.
- `engine/dm/schemas.py`, `engine/dm/roles/prompts/__init__.py`: the role registry and the prompt budget (800 words).
- `evals/playtest.py`: `--fixer-model` for the live gate; `evals/gemini_smoke.py`: role list.
- Tests touched for the new shape: scene state, intended change, combat, e2e, schema contract, offline model.

## Hand-off notes
- **021**: testimony settlement still writes refusals as facts (233000 `fact.103/.108`); the Fixer can undo one
  (`correct_testimony`), but the cause is yours. The Fixer's held-out misses (h1, h7) were rule knowledge the prompt
  lacks; a short mechanics digest (holds, scene labels never snags, refusals never facts, Stagger) belongs with the
  guidance digests, measured on a fresh held-out set.
- **Framer**: the payment is read from the declared consequence words (`change.price`, 3/3 payments and 0/4 offers on
  the saves). A typed `price` field on the Framer schema is the upgrade when that schema is next opened.
- The turn tool cannot show a foe's natural d20 (the Fixer explained h2's crit as "dire stakes"); add the rng draw if
  that recurs.
