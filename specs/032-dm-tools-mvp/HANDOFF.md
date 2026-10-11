# HANDOFF 032 (P1-P6 done, P7 scored on branch spec032-base + this commit; default NOT flipped)
Owner rulings, 2026-10-10 (they override the spec docs; tagged `[owner ruling 2026-10-10]`):
- **Scene ends are the DM's call** (the `end_scene` tool; code only does the bookkeeping; travel and time jumps still open a scene).
- **Moods are decided by the DM** (the `mood` tool records them as memory; no roll and no ceiling grid).
- **Pushover is observed, not gated.** Principle: fix only what is seen in play.
P7 done (report: `implementation-results-P7.md`, verdict + gate table first): h2h on the six saves C1 0.40, C2 0.46, C3 5 vs 8 by hand,
C4 1 vs 6 /fix, C7 0 leaks, C8 foe turns 3 per 3 settled exchanges (the scorer's "10 exchanges" counts every input), C10 0 engine errors.
**C9 FAILS (strict)**: 28 told lines dropped vs 22 written. Trace A: a said speaker the DM described but never made (explorer: the Longbridge man, the
carter) is dropped by `_told`. Trace B: `travel` moves only the PC, so a companion who walks along (talker: Dunbert) stays "not here": 18 lines dropped,
3 `reveal_clue` refused. **C11 not run**: `evals/heldout_032.py` is built (test `tests/evals/test_spec032_heldout.py`, offline); live command:
`PYTHONUTF8=1 py -3.12 evals/heldout_032.py --out specs/032-dm-tools-mvp/heldout_run` (about 15-25 min, run once, no tuning).
Predicted H03/H04 fail: `PERSON_VERBS` lacks sneak/observe (the live talker had the same refusal at turn.13). Recommendation: do not flip yet.
Next (owner decides): run the held-out set; then fix A and B (+ widen `PERSON_VERBS` only AFTER the held-out run), re-run the six personas, re-score.
P7.6 (the flip) and P7.7 (full gates + validator) are still open; pytest (full) and ruff/pyright on the new files are in the report's tail section.
Traps:
1. `h2h_score.py` counts every input inside a conflict as an exchange and every `npc.said` event as a told row; read `round` boundaries and `screen.dm_tools.said`.
2. The foe is seeded `near` (06.3.9) even when the prose has the PC at arm's length: the first two foe acts are band moves.
3. `npc_agency.leaked` is word overlap: A9's "night"+"watch" flag is false; the voice test scores only the first quoted line (2 of 5 cells had none).
4. Held-out J items score the speaker and a topic word, not the exact words; the walk-ons (H14, H18) are made in setup. The set is spent if anything is tuned on it.
5. Working-copy files are CRLF; edit with the Edit tool or a Python rewrite with `newline=""`; `pytest -q -q` hides the summary line.
6. dm.md or schema change means re-recording ONLY `offline_seed11_dmtools`. Name-token leak audit cannot see name-only secrets (L3).
P8 (merged by the orchestrator):
- **P8a:** no name matching in code. A non-id target or speaker becomes a walk-on with a returned id, listed in the situation. Verb target kinds come from `basic_verbs.yaml`; an object target is text, never refused. `travel who=` lists the ids who come along.
- **P8b:** the full cost menu goes to `code_framer` (the 0-foe-turn cause). The DM's `fail_cost` wins; the fallback is `resolution.yaml#cost_selection.verb_costs` (DL-01-54, provisional). `change fight to=<range>` sets the start band. `changed_line` "is".
- **Owner ruling 2026-10-10:** code never infers story state from actions or names. P8b's melee-trait inference (a Strike writes the contact band) is removed, with its M tests. Inventory: `research_notes/.../spec032-investigation/fiction-inference-inventory.md`.
- Left: ANIMAL compound matching still sets a walk-on's `mind: animal` from its words (P8a). Exact-name resolution in `_id` is kept.
