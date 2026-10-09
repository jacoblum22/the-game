# Spec 020: implementation results

Branch `worktree-agent-aecf2f5b7d82fd196`, from `milestone-1-playable` (f9d5221, R2-J merged). Haiku for every
engine call; the playtest player on Sonnet (the harness default). No Gemini, no API spend.

## After merging milestone-1-playable (spec 019, a65c306)
- Conflict only in the replay; re-recorded. `cards.json` rebuilt (unchanged). Suite on the combined code:
  **1792 passed, 4 skipped, 0 failed**. Long-horizon scripted 300: **0 engine errors**
  (`longhorizon_020_merged.txt`; line 50 narrator 6631, reader 3341, director 2287).
- 019's notes: `narrator.md`'s "CORE RULES" now reads GUIDANCE (the one sanctioned edit there). Identity lines reach
  the narrator packet through `view_for(Role.NARRATOR, …)`, which `narrator.draft` still calls. The OFFER leak
  ("the height citation (fact.73) is unverified"; "must be answered by the Oracle before any roll") came through
  "Whatever the roll:" and cost forms: `oof.player_words` now drops any Framer clause with an id or talk about the
  record (view, citation, unverified, Oracle, established, recorded, fact, lever, snag…); tested on both live strings.
- Still open (019's file): `narration.py:671` re-shows a paused OFFER with `then=` the raw `method`.

## Gates

| Gate | Result |
|---|---|
| Full suite | **1784 passed, 4 skipped, 0 failed** (replay re-recorded) |
| ruff / pyright (touched files) | clean / 0 errors |
| Rules validator (pacing comment edit) | 0 ERROR / 0 WARN |
| Long-horizon scripted, 300 lines, seed 7 | **0 engine errors**; same 381 turns / 308 narrated as before; `evals/baselines/longhorizon_020.txt` |
| Coercion messages (I3 §6), re-read in their recorded live packets | before **0/5** one goal beat; after **5/5** (one `learn` beat, G1, rolled under Grapple, `against_will`) |

### Reader on Haiku (one run each; one line ≈ 1.1 pt golden, 2.7 pt held-out)

"Before" = the current baseline answers (`reader_*_haiku_015c.jsonl`, the pre-020 Reader) scored against the new
labels; old-label scores in brackets. The goal-shape "before" is a fresh run of the pre-020 Reader.

| Set | verb | gate | goals | question_kind |
|---|---|---|---|---|
| golden 91, before | 90.1 (93.4) | 95.6 (96.7) | 79.1 | 89.0 |
| golden 91, **after** | **84.6** | **93.4** | **84.6** | 86.8 |
| held-out 37, before | 86.5 (94.6) | 86.5 (94.6) | 83.8 | 89.2 |
| held-out 37, **after** | **86.5** | **89.2** | **86.5** | 94.6 |
| goal-shape 35, before | 82.9 | 94.3 | 91.4 | 85.7 |
| goal-shape 35, **after** | **82.9** | **100.0** | **97.1** | 82.9 |
| goal-shape held-out 14, after (no before) | 85.7 | 92.9 | 85.7 | 100.0 |

- **Golden verb fell 5.5 points**, beyond noise (14 misses). About half are the goal-first reading disagreeing
  with an act-level verb label: force in service of movement read as Move (g062, g078 "push the old man aside and
  step through"), the wicket as the method of stepping out (g005), the climb as the method of the look (g091), the
  step through the gate folded into the demand (g002), a kept or gentle grip read as against the will, so Grapple
  (g055, g010). The rest look like ordinary misses (g071 knock read as Strike, g060, g080, g037, g033, g029, g034).
  The goal fields rose on every set; g004 ("…I'll make them. Strike!") is now read as a demand (a goals miss).
- **Discipline note.** Three post-change runs were made. 020a (first prompt) is the clean first shot; 020b and 020c
  were revised after reading 020a's misses on all sets (a persuade_to wording, "a weapon only pointed", bundled
  questions, and restoring the old §1/verb wording that the 800-word budget had cut). So golden, held-out and
  goal-shape are no longer strictly held-out for the final prompt. `reader_goalshape_heldout.jsonl` (14 lines) was
  labelled after 020a and before 020b/c ran. 020a: golden 85.7/94.5/84.6, held-out 94.6/94.6/89.2, goal-shape
  88.6/97.1/82.9 (verb/gate/goals). All files are in `evals/baselines/reader_*_020{a,b,}.*`.

### Per-role input tokens (same seeded scripted run, every call; `evals/role_tokens.py`, `role_tokens_020.txt`)

| role | before | after | |
|---|---|---|---|
| reader | 14929 | 3356 | −78% |
| director | 13862 | 2697 | −81% |
| world | 15266 | 2921 | −81% |
| narrator | 17659 | 6654 | −62% |
| framer | 12097 | 9417 | −22% |
| checker | 6078 | 3377 | −44% |
| interpret | 5591 | 3015 | −46% |
| **per turn, all calls** | **43263** | **15621** | **−63.9%** (I4 estimated −73%) |

The Framer's digest (its 12 cards' J blocks, ~4.4k tokens) and its anchor cards (~2.9k) are the remaining bulk;
the narrator and checker keep their old role cards as digests (assumption A5). View-token lines against the last
baseline (`longhorizon_final_overnight.txt`): line 50 director 14442 → 2287, narrator 17083 → 6692, reader 13382
→ 3349; line 300 framer 11060 → 9602.

### Live fighter playtest (`evals/playtests/20261009-143824-claude-fighter.md`, 15 turns)
- No coercion came up, so goal-versus-method was not exercised on a grip; every multi-beat turn (3) was two real
  goals (search the ditch, then follow the trail; look for bandits, then fight if found). No method was rolled
  in place of a goal; the coercion gate above covers that case.
- **"Then:" lines read cleanly** from the player's own words: "Then: follow the trail out of town", "Then: follow
  fresh tracks or a camp and pick a fight". Titles: "Learn about the pale splinters in the reeds.", "Learn about
  where the bandits might be: keep walking the road, hunting…". Two flaws found and one fixed: harm on a
  description read "Damage bandits…" (fixed: "Hurt"); Haiku once copied the prompt's gloss "people or things present
  with no id" into `description`, which the title printed ("Look over people or things present with no id: …";
  open: a model slip the title now exposes).
- Other player findings (rolls on unestablished bandits, hidden-odds screens, pre-narrated results, `/fix`
  vagueness, RESULT labels from the restatement) are outside this lane (pipeline, narration 019, `/fix` 022).

## What was built
- **F2.** Reader prompt §3 "one beat per goal" with `how`; `normalise._fold_methods` (an against-will method folds
  into its goal, carrying facets and words) and `_bundle` (several questions to one person are one beat); `verbatim`
  keeps `how` only when it is the player's words; `Beat.how`; `oof.goal_line` renders the OFFER title, "Then:" and
  the plan pause ("Still go on: …?") from kind and slots plus `how`.
- **F3.** `cards.guidance_digest` per role (J blocks; Reader adds change kinds and verb covers from data);
  `load_cards_for` returns only trigger and extra cards; `build_packet` puts the digest in the core slot (section
  GUIDANCE); Director 2 / World 1 exchanges from the turn log; identity lines (name, pronouns, `bond.` tie) in the
  narrator view and the testimony call; thread lead lines only when new or touched; Framer gets 15.3.2 on Talk.
- **Evals.** Policy B3'/B5'/D1'/E written and applied blind (11 labels changed, `goals` on all 128 lines);
  `reader_goalshape.jsonl` (35) and `reader_goalshape_heldout.jsonl` (14); `reader_coercion.py`; `role_tokens.py`.

## Retired, and what supersedes it
| Retired | Superseded by |
|---|---|
| Reader prompt "one beat per distinct act whose failure would not stop the other", "Two changes are two beats" | "One beat per goal" (01.2.2, DL-01-37) |
| `normalise`: "a beat against someone's will or using a power is always its own beat" | `_fold_methods` |
| Golden policy B5 and B3's "over to a person" Move | B5', B3' (blind relabel) |
| `pipeline._then` printing `method`; `offer_title` printing the restatement; the OFFER's "Taking: …" line | `oof.goal_line` (typed goal + verbatim `how`) |
| The 00.15.4 core in every packet (`render_core`, `core_cards`) | `guidance_digest` |
| Situation cards by tag sorted by id (`situation_cards`, `ROLE_CARDS` in the cap) | cards only where code knows they apply |
| Director and World with no conversation | last 2 / last 1 exchange |
| Every thread's lead line in every narrator packet | new or touched only (281 of 528 narrator packets) |

Anti-pattern check (handoff §3.3): atomisation reduced (no act split; questions bundled); code no longer prints a
model free-text field in the OFFER; wrong context removed (core, id-sorted cards) and missing context added
(conversation, identity lines). New risk: the goal-first reading can over-fold a wanted blow into a demand (g004);
code folds a blow only when the Reader marks it.

## Outside the lane (one line each)
- `engine/resolve/types.py`: one field, `Beat.how`, to carry the player's method words to the OFFER.
- `engine/llm/base.py`: the `core` section's title CORE RULES → GUIDANCE.
- `engine/dm/roles/prompts/__init__.py`: Reader word budget 800 → 1000 (the goal rule; ~10k tokens of cards left).
- Tests that pinned the old packet, titles or schema (`test_packet`, `test_retrieve`, `test_oof`, `test_pipeline`,
  `test_message_plan`, `test_intended_change`, `test_turn_adjudication`, `test_round4_fixes`, `test_llm_base`,
  `test_memory`, `test_harness`, offer snapshots); `evals/baselines/reader_golden.txt` regenerated for the new labels.

## Hand-off notes
- **019:** `narration.py:671` re-shows a paused OFFER with `then=[q["beat"]["method"] …]`: replace with
  `oof.goal_line(BeatPlan.model_validate(q).beat, ctx.state)`. `narration._for_beat` labels RESULT blocks with the
  restatement (turn.py:243 passes `entry.restatement`): use `goal_line` too. The narrator prompt's "write around
  names or kinship" line is yours to remove; the identity lines it worked around are now in the narrator view
  ("people here or named"). `GUIDANCE[Role.NARRATOR]` / `[Role.CHECKER]` in `cards.py` are your digests to set.
- **021:** the testimony call's view now carries identity lines (`packet.identity_lines`); `rests_on` and the
  Reader's TESTIMONY lines are untouched for you to retire.
- **022:** a folded hold leaves no hold state (the beat's change is the demand); "she stays held" needs the hold as
  a method consequence/condition.
- **Rules:** `resolution.yaml#intended_change.split` still says "two changes in one message are two beats (01.2.2)";
  it is stale against DL-01-37 (not read by code).

## Owner decision
None blocking. Sensible defaults taken: a move to another place stays its own goal (B3', so the place change is
written); a blow folds only when the Reader marks it. The golden verb drop is the one open measurement question;
revisit with DL-01-37's provisional conflict clause.
