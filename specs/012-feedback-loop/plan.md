# Plan: The player feedback loop (spec 012)

**Spec**: [spec.md](spec.md). **Tasks**: [tasks.md](tasks.md). Items cite `R2-G-report.md` "engine checklist →
Spec 012" (C1-C9).

## Constitution check
- I (code resolves, the model judges only what it must): the locator call only finds the passage; code decides.
- III / INV-9: the player's reading wins only on incidental detail slots with uncertain evidence.
- IV (scope): no new subsystem; `engine/dm/dispute.py` is extended. Lanes respected (spec 011 files: call sites
  only, listed in the results).

## Design

- **Locate (C2)** `dispute.locate(ctx, text) -> DisputedClaim`: code pins first, over **every** turn
  (`_turns` loses its limit): `turn N` / `turn.N`, `frame.N`, `fact.N`, a quoted phrase (the turn whose delivered
  text holds it), entity names (full names and aliases of visible entities), quantity words, detail-slot words
  (`details.slot_of`), the first number. Category by code only from structural markers (a `frame.N`, or a fact id:
  rule_wrong; a named key with a stored value: remembered_wrong); otherwise the category is the locator's
  `[J:enum]` (12.3.6 item 2; constitution I) [analyze D1]. Unpinned passage, or a pinned passage with no
  structural category → one call (never two), new `Role.LOCATOR` (`prompts/locator.md`; schema in `dispute.py`;
  offline heuristic in `engine/llm/offline.py`): `{turn, quote, category, subject, key, value}`, candidates = this
  scene's turns, then search hits. Code checks the turn exists; the claim fields fill only what code missed.
- **Evidence (C3)** `gather`: passage quote, other turns naming the subject (whole transcript), the value's
  provenance from the event log (source event seq, `source`, source kind, turn), fact history, frame + cited facts,
  meta `claim_log` entries for the turns (spec 011 writes them; absent = none).
- **Recompute (C4)** `recompute(store, frame_rec)`: state at the commit (`project(events < commit seq)`), DC
  (tier → `resolution.dc_tiers` + mode shift; stored → the stored fact; opposed → kept), modifier (attribute,
  competence, edge, status from engine/resolve helpers; circumstance as recorded, cited facts must be usable),
  odds (`odds.odds`). Any difference → ruling error (`_ruling`, reliance true).
- **Decide (C5)**, first row that fits (PR-12-11): rule_wrong → recompute/missed fact; misread (no OFFER shown:
  auto or no roll, and report words found in the player's input but not in the restatement) → take back; a
  resolved earlier write of the player's value superseded by an unsourced one → record error (pinned
  `fact_set source=correction`); store ≠ value and the narration said the value → narration error (store wins,
  reliance); store = value → state the store's value; store ≠ value, never said → explain with the provenance
  quote; nothing stored + incidental detail slot → player's reading wins (pinned); nothing stored + anything else
  → explain and log (INV-9).
- **Pinned (C5)**: `FactSet.pinned` / `FactRecord.pinned` (events + projection); `FactSet.source` gains
  `correction`. `packet.scene_view` adds every pinned fact about an entity in scope (never archived, past the
  budget); `render_view` marks it `(corrected)`; `spot_lines` keeps pinned details.
- **Take-back (C6)** `_rewind(..., take_back=True)`: past the scene start when code-confirmed, ≤
  `max_turns_back` turns, no blocker since the beat (`dying_step` / `setback.dying_entered` / `exists=dead` facts,
  `unsealed`, a completed `clock_ticked`, a `session_start`/`session_end` boundary). Store: `WritesReverted.take_back`
  lets the revert reach before the scene start and also revert `scene_started` / `scene_ended`, so the PC is back
  in the beat's scene. A misread beat is taken back whenever reported, within the same limit (12.5.8 item 2)
  [analyze I1].
- **Labels (C7)**: `[CORRECTION]` and `[FIX]` only.
- **Review log (C8)**: ledger record (meta `corrections`, `type: dispute`, id `dsp.N`, game time) and a markdown
  block appended to `<save stem>.disputes.md` beside the game file (wall-clock time there only). A pending CHOICE
  logs `outcome: pending`, the answer replaces the record and appends a resolution block.
- **Hint (C1)**: `dispute.FIX_HINT` (= `pacing.yaml#feedback.hint`, asserted by a test). CLI prints it after the
  first play screen of a session; `oof.glossary()` ends with it; `reader.possible_dispute(message)` (a code scan for "you said",
  "that's wrong / not right", "already told / said / gave", "I meant", "not what I meant", "never happened") adds a
  NOTE block with the hint when the Reader returned no DISPUTE part [analyze B1, C1]. Reader prompt: 12.2.2's examples.
- **Metric (C9)**: `longhorizon.dispute_lines(store, narrated)` (all, upheld, by category); `--fix-every`
  plants reports in the scripted run (default 0). Playtest persona: one line about `/fix`.

## Files
Mine: `engine/dm/dispute.py`, `engine/dm/turn.py` (`_dispute` hint/locate wiring), `engine/dm/roles/reader.py`
+ `prompts/reader.md` (dispute only), `prompts/locator.md`, `engine/store/events.py` / `projection.py` / `db.py`
(pinned, take_back), `engine/dm/packet.py`, `engine/dm/oof.py` (glossary line), `engine/llm/base.py` / `offline.py`
/ `gemini.py` (the role), `play/cli.py`, `evals/longhorizon.py`, `evals/playtest.py`, tests. Spec 011's: none.

## Not done (deferred)
- Make-whole refunds for spends before the scene (12.3.4 step 3): still M1's "coarse" note.
- In-fiction reconciliation form (12.3.4 step 2): disputes always answer OOF.
- The `[J:flag]` "omitted fact that changes the frame" beyond a fact the player names.
