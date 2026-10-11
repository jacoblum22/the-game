# Tasks 032: dm-tools MVP

Seven phases, each sized for one fresh agent (about 15-60 turns; the cap is 100). Each phase starts with
`git reset --hard <previous phase's branch>`, reads `HANDOFF.md`, `spec.md` (its FRs), `cases.md` (its sections) and
`plan.md` (its section) only, and ends by ticking its tasks, writing a 15-line `HANDOFF.md`, and committing (never
push). Every phase's tests use the **offline scripted DM model**; live (Haiku/Sonnet) numbers are reported, never
faked. Every phase ends with: `ruff check .`, `pyright`, `python -m pytest -q -p no:cacheprovider` (`PYTHONUTF8=1`),
and the validator if a rules file changed. A phase writes `specs/032-dm-tools-mvp/implementation-results-P<n>.md`
(numbers, failures, deviations).

**Lanes** (files a phase may edit; two phases may run in parallel only if their lanes do not overlap):
`E` evals/harness; `R` role plumbing (`engine/llm/*`, `engine/dm/schemas.py`, prompts); `G` game plumbing
(`engine/game.py`, `play/`); `T` tools (`dm_tools.py` tool functions and prompt); `W` world (`dm_world.py`, new);
`C` context and records (`dm_tools.situation/_audit`, said); `F` fix (`dispute.py`, `fixer.py`).
`dm_tools.py` is shared by T, W, C: those phases run **in order** (P3 -> P4 -> P5).

Parallel plan: `P1 || P2`, then `P3 -> P4 -> P5`, with `P6` free to start after P3 and to run beside P4/P5 (it must not edit
`dm_tools.py`, only import `code_framer`), then `P7`.

---

## P0 - Design (this slice; Sonnet)
- [x] P0.1 spec.md (gaps, FRs, gates, assumptions), trace of the fighter save (no `conflict_start`; the dead-end turn)
- [x] P0.2 cases.md (data-enumerated: 15 verbs, 11 change kinds, 33 conditions, 9 cost ids, 6 foe outcomes, 7 cut triggers,
      12 cells, 4 pronoun sets, 7 question kinds)
- [x] P0.3 plan.md (reuse map, new turn, per-gap design, analysis section)
- [x] P0.4 tasks.md (this file), HANDOFF.md, checklists/requirements.md

## P1 - Harness and labelled sets (lane E; Sonnet; about 30-45 turns; parallel with P2)

Goal: the measuring tools exist and the held-out set is labelled **before any fix**. Edits only `evals/`, `specs/032-dm-tools-mvp/`, `tests/evals/`.
- [x] P1.1 Port `evals/npc_agency.py` and `evals/baselines/npc_agency_round8.json` from `3e94efe` (`git show`); add the
      `dm-tools` arm (real `dm_tools.play_turn`, Haiku through `ask_claude`) and keep `pipeline` as the file's `old` arm;
      drop `ceiling`/`judgment` arms and `ceiling_lines`. Cost per cell is fixed by the cell (`cases.md` N).
- [x] P1.2 Run both arms once on the **unfixed** code (12 cells + 4 repeats each): save the tables under
      `specs/032-dm-tools-mvp/npc_agency_before.txt`. This is the "before" for C5/C6.
- [x] P1.3 `evals/h2h_score.py`: reads saves (`model_calls`, `turns.record.screen.dm_tools`, `findings.jsonl`) and prints
      the headline table (spec gates C1-C10 inputs) in under 40 lines. A test over a tiny fixture save.
- [x] P1.4 Write `heldout.yaml` (24 items, `cases.md` rule) with labels, **no model run**. Commit it with its hash
      in the file header.
- [x] P1.5 Write the cases-as-tests skeletons `tests/engine/test_spec032_cases.py` that walk the data tables
      (verbs 15, change kinds 10/11, conditions 33, cost ids 9, foe outcomes 6, cut triggers 7, cells 12, pronoun sets 4,
      question kinds 7) and assert the lengths. Cases for later phases are `xfail(strict=True)` with the case id.
- [x] P1.6 Re-run the two traced facts as a test fixture: copy the fighter save's turn 9 and 12 tool logs and assert
      "no conflict_start" so P3's fix flips it (the save it came from).
Gate: the harness runs end to end with `--offline` stand-ins in a test; the before-table exists; the held-out file has a
hash and is not read again until P7.

## P2 - Role.DM and the engine stored in the save (lanes R + G; Sonnet; about 30-50 turns; parallel with P1)

Edits `engine/llm/base.py`, `engine/game.py`, `engine/dm/schemas.py`, `engine/llm/offline.py`, a new `engine/dm/prompts/dm.md`
(or wherever the pipeline keeps role prompts: find it), `tests/contract/`, `play/cli.py`; one line in `dm_tools.py` (`DM_ROLE`).
- [x] P2.1 `Role.DM` + prompt file + schema registration + packet; `DM_ROLE = Role.DM`; per-role model config works
      (`GameConfig.models`), calls recorded under `dm`. Move `PROMPT` text out of the code. (FR-13)
- [x] P2.2 Offline heuristic for the DM role: a deterministic plan (talk passage; `propose_roll` when the message has an
      attack verb) so offline games and `tests/e2e` run dm-tools turns. Contract test for the role.
- [x] P2.3 `Game.open` reads the stored `engine`/`dm_secrets` (missing -> pipeline/hidden); `--engine` on `play new`
      (new game only). Cases S1-S12 as tests (including the 3x3 matrix and the open-OFFER resume). (FR-11)
- [x] P2.4 Update harness readers that look at `role='narrator'` for dm-tools (`evals/playtest.py`, `longhorizon.py`,
      `tests/e2e/driver.py`); one dm-tools game recorded into `tests/replay/` (new recording; the pipeline ones stay).
- [x] P2.5 Gates: suite, replay for the existing recordings unchanged (pipeline packets untouched), ruff, pyright.
Trap: the stored config of old saves has no `engine` key; never read `GameConfig().engine` when opening a store.

## P3 - Tools make the DM's words real (lane T; Sonnet; about 40-60 turns)

Edits `engine/dm/dm_tools.py` (tools, schema, prompt text), `engine/resolve/types.py` (`Beat.title`), `engine/dm/oof.py`
(`goal_line` reads `title`), tests. Trace first, then fix.
- [ ] P3.1 **Trace** in the fighter save and the talker/explorer scripted saves every `REFUSED` (list them by reason);
      tabulate into `implementation-results-P3.md` before coding. Confirm the conflict never started (P1.6 fixture).
- [ ] P3.2 The resolver `_party` (plan G4) used by propose_roll, mood, reveal_clue, change; reuse
      `mentions.write_mentions` / `cast_described`; creature vs person by the ANIMAL test. Cases R1-R33.
- [ ] P3.3 `change kind=fight` (an NPC turns on the PC): `conflict.start`; no foe action here (P4 runs it). F16 minimal.
- [ ] P3.4 One revision then drop (E1-E8): the tool loop already returns `REFUSED`; add `screen.dm_tools.dropped` when a
      call fails twice; `condition_add` on the PC outside a roll/foe turn is refused (E7); harm-owned conditions refused.
      Conditions K1-K33 walked.
- [ ] P3.5 OFFER words: `fail_cost` enum in the `propose_roll` schema; `code_framer` honours it when `frame_check` accepts;
      `Beat.title` + `oof.goal_line` (the pipeline never sets it). O1-O12. Replay: check pipeline packets are byte-equal.
- [ ] P3.6 Items (G5): `new_item` echo of a same-named held item; `give_item` cases I1-I11.
- [ ] P3.7 Live check on Haiku: re-run the fighter persona 15 turns; report refusals (expect 0 prose-only), `conflict_start`
      present, OFFER titles. The fighter save's turn 9/12 contexts replayed (5 samples) for target resolution.
Gate: R/O/I/E/K cases green; suite green; live fighter run shows a `conflict_start`.

## P4 - The world step: fights, time, clocks, leads, cuts, the dead end (lane W; Sonnet, Opus if the re-ask ordering fights the pause logic; about 45-70 turns)

New `engine/dm/dm_world.py`; small hooks in `dm_tools._run/_dm_loop` and the situation's FIGHT block (agreed with lane C: the FIGHT block is P4's, the rest of `situation()` is P5's).
- [ ] P4.1 **Trace** what scene mode the pipeline's Director gives place scenes and what `beat_cost` returns for it; decide the
      dm-tools scene mode (assumption A1); write the finding into `implementation-results-P4.md`.
- [ ] P4.2 `world_step(ctx, t)` per plan: foes (`foes_act`), time (`beat_cost`, `beat_end`, `note_turn`), omens, triggers,
      lead (`inject_lead`), cut (`cut_due` in {time_jump, interrupt, conflict_end, dead_air}); facts returned as plain words.
      Cases F1-F26, T1-T12, C1-C7.
- [ ] P4.3 Wire it: after `_resume` on an answer turn; after the tool phase on a free turn; re-ask once only when a fact exists;
      never on an open pause (F17). Zero extra calls when no conflict and no fact (F20).
- [ ] P4.4 FIGHT block in `situation()`: foes, `state_words`, bands, PC harm state; prompt sentence for G7 (plan G7 wording).
- [ ] P4.5 Replay the fighter save's turns 9-15 on the code (offline scripted DM): F11. 5 live Haiku samples of the turn-11
      context: report k/5 proposing the roll (F12).
- [ ] P4.6 Live: fighter + talker personas 15 turns each on Haiku. Report foe turns per exchange (target 1.0), hours advanced,
      extra calls per turn, tokens/turn (C1/C2 trend).
Gate: F/T/C cases green; suite; live fighter shows a foe strike each fight exchange; talker clock advances.

## P5 - Records and context: told, presence, pronouns, items, leak audit (lane C; Sonnet; about 35-55 turns)

Edits `dm_tools.py` (`situation`, `_audit`, final schema `said`, `_told`), `tests`. No change to `codex.py`/`testimony.py`
(reused as is).
- [ ] P5.1 `said` in the final-answer schema (cap 6) + `_told` -> `testimony.add_said`; drop-and-log for bad speakers.
      Cases J1-J14 (question kinds 7 walked); the journal shows them (J12 on the talker save).
- [ ] P5.2 `situation()`: `carries:` per person, `Not here:` line; token delta measured before/after (report).
      Cases Q1-Q8.
- [ ] P5.3 Log-only checks `pronoun`, `absent_named`, `item_unbacked` into `screen.dm_tools.log_only`; never block (grep
      proves no return path alters the passage). Label 40 passages by hand from the three round saves for precision;
      write the table. Cases Q9-Q14, I12.
- [ ] P5.4 Leak audit: drop all entity name tokens (display name, aliases). Cases L1-L6 including the 10 false flags
      from the head-to-head saves (copy the two flagged passages as fixtures).
- [ ] P5.5 Live: talker + explorer 15 turns on Haiku; report told rows per run, log-only counts, leaks, tokens/turn.
Gate: J/P/L/I cases green; no check blocks; tokens in per turn within +10% of P4's.

## P6 - `/fix` on dm-tools turns (lane F; **Opus**: it is design-heavy; about 40-70 turns; starts after P3, parallel with P4/P5)

Edits `engine/dm/dispute.py`, `engine/dm/fixer.py`, `engine/game.py` (`_dispute` only), tests. Does not edit `dm_tools.py`
(imports `code_framer`).
- [ ] P6.1 **Trace** `/fix` on a dm-tools save for each of the 5 turn states (X1-X5): what the Fixer sees, what `preview`
      and `reframe` do, what the correction turn records. Write what breaks (not what might).
- [ ] P6.2 Smallest change per plan G11: DM tool log as Fixer evidence; `reframe` env from the code framer for dm-tools; the
      dispute turn marked in `screen.dm_tools`; fall back to rendering the answer without a Narrator call if needed.
- [ ] P6.3 Cases X1-X22 (20-cell matrix offline; X21 no Framer call; X22 no clue delivered).
- [ ] P6.4 Live (Sonnet Fixer): the 4 saved head-to-head complaints and 4 new made-up complaints on dm-tools saves; report k/8
      repaired-or-explained and the pipeline's number for the same kinds from `evals/baselines/fixer_*`.
Gate: matrix green; suite; live k/8 reported honestly (target at least the pipeline's rate).

## P7 - The confirming head-to-head and the default switch (lanes E + G; Sonnet; about 40-70 turns, long background runs; **owner decision gate**)

Runs only after P1-P6 are merged into one branch. Edits `evals/`, `specs/`, and (only if the gates pass) `engine/game.py`,
`play/cli.py`, tests that assume the default.
- [ ] P7.1 Re-run the P1.2 NPC-agency arms on the fixed code (12 cells + 4 repeats, both arms, Haiku): the "after" tables.
- [ ] P7.2 Persona runs, 15 turns, `--quick-setup`, Haiku engine, Sonnet player: talker, fighter, explorer x {pipeline,
      dm-tools} (6 runs, in parallel). Use the commands in `specs/031-dm-with-tools/implementation-results.md`.
- [ ] P7.3 `evals/longhorizon.py --mode scripted --lines 60 --model claude --engine dm-tools` (dm-tools only; skip the pipeline
      run). Report engine errors, refused tool calls, leak flags, told rows.
- [ ] P7.4 Run `heldout.yaml` once; report k/24 by family; no tuning afterwards.
- [ ] P7.5 `h2h_score.py` headline table first (gates C1-C11), then hand-counted contradictions by the results note's rules
      (3 saves per arm), then the one-paragraph read. Write `implementation-results.md` with the table on top.
- [ ] P7.6 If **all** gates pass: flip `GameConfig.engine = "dm-tools"`, add `engine="pipeline"` where tests test the pipeline,
      run the suite both ways, re-record replays that change, update `CLAUDE.md`/docs one line, `OVERNIGHT-LOG` line.
      If a gate fails: do **not** flip; list the failed gates, the likely cause by trace, and 2-3 options for the owner.
- [ ] P7.7 Full gates: ruff, pyright, pytest, validator 0/0; write `HANDOFF.md`; commit.

## Dependencies and slice sizing

| Phase | Needs | Lane | Model | Turns | Parallel with |
|---|---|---|---|---|---|
| P1 | none | E | Sonnet | 30-45 | P2 |
| P2 | none | R+G | Sonnet | 30-50 | P1 |
| P3 | P2 | T | Sonnet | 40-60 | P1 |
| P4 | P3 | W | Sonnet (Opus fallback) | 45-70 | P6 |
| P5 | P4 | C | Sonnet | 35-55 | P6 |
| P6 | P3 | F | **Opus** | 40-70 | P4, P5 |
| P7 | P1-P6 | E+G | Sonnet | 40-70 | none |
