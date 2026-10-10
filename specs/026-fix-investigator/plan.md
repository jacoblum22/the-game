# Plan 026: `/fix` as an investigating engineer

## Trace first (done before design; R7-I3 §3, R7-H2 T7 confirmed in code)
- `fixer._entity_tool` prints `sheet()` (quantities, harm word, conditions, held items) and raw fact lines
  (`fact_line`: `predicate = value`): no role, licences, competence, stance. Belie's Letters are invisible.
- `dispute._rerender` scans `frame_committed` only; an OFFER is a `pause_opened`. Even on a committed frame it calls
  the same `_breakdown → fact_short` on the same fact: it cannot change what the player saw.
- `PROPOSALS` has no kind that touches the open pause; `settle_dispute` leaves it, so `narrate_turn` re-shows it
  (`pause_blocks`).
- `take_back` reverts `REVERTIBLE` writes; `pause_opened` is not one, so a take-back of the pending turn leaves the
  OFFER open (found while tracing: not in I3).
- `packet.view_for`: the Reader sees `_slim` entities (role, aliases, pronouns); the Framer sees the target's raw data
  (with `licenses: grade=…, id=…` dicts, cut at 12 keys) plus 023's `target's record`; the Narrator sees raw data keys,
  alphabetical, cut at 12: Belie's `licenses` falls inside the cut, her `stance` outside.
- The scorer (`feedback_corpus.score`) checks only the outcome class and the applied kinds; `run_item` calls
  `settle_dispute` directly and never renders the next screen.

## Design
- **`packet.people_card(state, eid, *, rules=None, hidden=False) -> list[str]`**: the one renderer. Read from the
  entity (data, `state.licenses` or `data.licenses`), the rules (licence and origin names), standing
  (`relationships`), bonds (`bond.*` facts on the PC), station facts (`rank`, `title`, `office`, `member_of`).
  Sealed entities: slice only. `hidden=False` skips `sealed_fields`; `hidden=True` (the Fixer) adds refusals marked
  hidden. In `view_for`, each person entity in the role's view gets a `card` list that `_entity_lines` prints in
  place of the raw data dump (keeping the `<id>: <name>` and `name:` lines the offline model reads). Reader: every
  full profile; Framer: the target; Narrator: every full profile. `framer.target_record` is deleted.
- **Fixer tools** (`fixer.py`): `entity` = people card + sheet + position + plain facts; `turn` events with plain
  facts and the effective degree; `calls` (model inputs/outputs of a turn, from `store.model_calls`); `try` (a dry run
  of proposals on a copy: returns the previewed screen); `replay` (take back turn N on a copy and run its words
  through `run_turn`; returns the beats as read and framed). `plain_fact(state, f)`.
- **Loop**: tool steps as before (3-6 calls); then the decision is previewed on a copy (`dispute.preview`) and shown
  as `THE SCREEN AFTER YOUR REPAIR`; the Fixer answers again (same schema, final); a changed decision is previewed again,
  at most `CHECKS = 2`; the last decision is applied for real.
- **`dispute.py`**: `_settle(ctx, tx, text, inv, log=True)` holds steps 4-6 and is used by both the real application
  and the preview; `sandbox(ctx)` = a TurnContext on a SQLite backup copy with a transaction open; `preview(ctx,
  text, complaints, calls)` = `_settle` in the sandbox + the screen (answer block + `pause_blocks` of the open pause +
  outcome blocks). `_apply` gains `reframe` (ORDER last) and loses `rerender`; `_take_back` closes a pause opened at or
  after the turn. `DisputeResult.outcomes` carries a re-frame's beat outcomes.
- **`turn.py` (one function, out of lane by necessity)**: `_dispute` takes the re-frame's outcomes into the record
  (`_take`) and adds the paused declaration's words as a DECLARATION part when a beat resolved, so the narrator
  narrates the beat, not the complaint. One-line justification: the dispute's turn record is built there.
- **Prompt** (`fixer.md`): the new tools, `reframe`, the take-back rule for a pending turn, open OFFER → re-frame, the
  mechanics digest, "the sheet outranks an Oracle fact", "Prefer the record" qualified; within the 800-word budget.
- **Data**: `pacing.yaml#feedback.investigate.proposals` drops `rerender_display`, adds `reframe_open_offer`,
  `take_back_pending_turn`; `tools` adds `turn_model_io`, `dry_run`, `replay_turn`. Validator 0/0.
- **Eval**: `feedback_corpus.py` runs `play_dispute` through a `TurnContext` with the routed model (`--fixer-model`,
  `--engine-model`) and scores `screen.must`/`must_not`; `fresh` and `round7` sets; `--cached` replays the Fixer and
  Framer answers. `evals/fix_scenarios.py` builds the made-up saves.

## Out-of-lane edits (one line each)
- `engine/dm/turn.py::_dispute`: the re-frame's outcomes join the dispute turn's record (the only place it is built).
- `engine/dm/roles/framer.py`: `target_record` deleted (spec 023's stopgap, replaced by the card in the Framer view).
- `rules/data/pacing.yaml`: the `feedback.investigate` keys this spec implements (validator 0/0).

## Risks
- Packet changes move the replay: re-record `offline_seed11` and rerun the replay tests.
- Reader/Framer behaviour can shift with the card (more context); the live run watches for it.
- The check step adds one Sonnet call per report (about 20-40 s).
