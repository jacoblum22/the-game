# "Pinned" with nobody holding: trace (playtest 20261010-175211-fighter-dm-tools, P3 at 38b5993)

Read-only trace. Save `saves/playtest-20261010-175211-fighter-dm-tools.db`, transcript inputs [19], [30], [31] and [28].

## Cause (one line)
The pin is **not** from the woman's sleeve, a DM `change` call, or the hold logic of turns 8–10. It came from
**turn.4 (input [19]), the critical failure on "push through the crowd"**. That cost was `cost.footing` at S4.
`engine/resolve/costs.py` turns footing S4 into `cond.pinned` on the PC and records **the PC as its own holder**.
A hold with no real holder never ends. Eleven turns later the G4 gate refused the strike because of it.

## Evidence chain
1. **The DM picked the cost (P3).** In turn.2, calls 5 and 6, the DM's `propose_roll` included
   `"fail_cost":"cost.footing"`, `"stakes":"risky"` and `verb.move`.
   - At 38b5993, `code_framer` (`engine/dm/dm_tools.py:527-541`) tries the DM's `fail_cost` first.
   - Rebuilding the state before seq 428 gives these stakes menus: `aware_opponent_or_observer` [exposure, footing, closed_door] and
     `hazard` [harm, drain, gear, footing].
   - The hazard candidate passed the check, so the frame was threatened `cost.footing` (S3 on failure, S4 on critical failure)
     with alternate `cost.harm`. That is event 428, and it matches the offer at [17]: "Close call … (you get hurt)".
   - Before P3, `verb.move` had no entry in `PREFERRED_COST`, so the framer took `m["threatened"][0]`. On the hazard
     source that is `cost.harm`, so a pre-P3 run would most likely have charged harm, not a pin. This is inferred, not
     replayed through `frame_check`.
   - The player chose go big (stakes became "dire"), then rolled d20 = 1, a critical failure. Event 432 records costs
     `cost.footing S4`.
2. **The engine wrote the pin.** Event 430 is a `condition_applied`:
   `cond.pinned`, S4, `target pc.kerey_ashley`, `source {"entity":"pc.kerey_ashley","frame_id":"frame.1"}`, rule PR-00-5.
   - The code path is `costs.py:294-301` (unchanged since Feature 004, c45ec6d):
     `conds = re.findall(r"cond\.[a-z_]+", write)` then `cond = form if form in conds else (conds[0] ...)` then
     `apply_condition(..., p.get("target", actor), cond, source={"entity": actor, ...})`.
   - The rule row (`rules/data/resolution.yaml:155-170`) reads `S4: "apply_condition(cond.pinned) OR move to next lower/worse place
     OR held in opponent's control"`. With no form intent, the code takes the first id, `cond.pinned`. That is a
     hold-ladder condition (`conditions.yaml:257`, `exclusion_group: hold`, `duration: while:the hold lasts`), and it
     puts the actor down as the holder.
3. **Nothing ever cleared it.**
   - `release_holds` (`engine/dm/scene_state.py:131-152`, called only from `world_step.py:57`) does not run on the
     dm-tools path at P3.
   - Even when it runs, it would not release this pin. The holder is the PC and is never "out", and
     `_band(pc, pc)` is None, so the "moved away" test never fires.
   - The DM saw `conditions pinned (held by Kerey Ashley)` on the sheet in every DM packet from call 7 to call 20 (11 calls).
     It narrated the PC scrambling up, seizing the woman and hauling her behind the bar, and never used its
     `condition_remove` tool.
   - Call 7's packet told it only "It cost you: you lose your footing — grave", and it narrated a fall with the sword knocked away.
4. **The strike was blocked by the G4 gate.**
   - Turn.15, call 19: the DM's `propose_roll` was `verb.strike`, `fail_cost cost.harm`, `stakes dire`.
   - `run_beats` led to `engine/resolve/gate.py:408-411`: `forbidden_by_condition` then "an active condition forbids verb.strike".
     Event 522 is a ruling with signature `g4:cinst.1`.
   - The tool result given to the DM (call 20 packet) was
     `NOT POSSIBLE AS PROPOSED (refused): an active condition forbids verb.strike` (`dm_tools.py:498`). It does not
     name the condition. The DM then narrated "Your legs stay planted …".
   - The player-facing `[REDIRECT]` is code-authored. `narration.py:705` calls `oof.redirect_block`, and
     `oof.py:520` (`_why`) produces "you are pinned right now, and that stops it; clear it first", followed by the
     clear options of `cond.pinned` ("Break free … Grapple roll").
   - Unrelated: the woman's hold, `cinst.2` (`cond.restrained` on Branella, source PC, event 475, turn.8), was
     applied correctly.

## What /fix did (turn.16, calls 21–25)
- **Investigation.** The Fixer called `turn(15)`, `turn(16)`, `ledger`, `entity(pc)`, `search('pinned')` and `turn(11)`.
  None of these could show where the pin came from:
  - `ledger` lists only quantity history.
  - `entity` shows the current sheet, not condition events.
  - `search` matches transcript words, and turn.4's text never says "pinned".
  - Its "LAST TURNS" window began at turn.10.
  - Only `turn('turn.4')` would have listed event 430. Because of this, the Fixer **invented a cause**: "came from
    you keeping hold of the woman in turn 10, and the hold landed on you instead of her". That is false, and it was
    shown to the player.
- **Proposals.** It made two:
  - `set_fact` with key `conditions`. This was refused by INV-9: the Fixer cited `turn.10` but never opened it
    (`engine/dm/dispute.py:231-239` and `:489-514`). Even if it had been accepted, it would only have written a
    `conditions` fact; it could not remove `cinst.1`.
  - `take_back turn.15`. There was nothing to undo, because a G4 refusal writes only a ruling.
- **No remedy exists.** `PROPOSALS` (`engine/dm/fixer.py:33`) has no condition-removal kind. The outcome was
  "explain (upheld)", nothing changed, and the pin is still on the sheet.

## Frequency and age
**Old bug, not new in P3.** Across every playtest save, `cost.footing` landing at S3 or higher produced a self-held hold
condition in **5 of 5 cases**:
- four pipeline runs on 2026-10-07, each with `cond.restrained` S3 (181737, 193420, 205745, 215325);
- this run, with `cond.pinned` S4.

Footing at S1 or S2 gives `off_balance` or `prone`, which are not holds and are harmless. In **3 of the 5** saves the
self-hold later blocked an action through G4:
- 181737: 6 refusals of `verb.move`;
- 215325: 1 refusal;
- this run: 1 refusal of `verb.strike`.

What P3 is new for is only the *exposure*. The DM's `fail_cost` now picks footing for movement, where before P3 the
framer would have picked harm.

## Anti-patterns
- **Code authoring narrative truth.** A cost-form regex picks the first condition and invents a holder.
- **Mechanics with no exit.** A hold-ladder condition is created with no holder.
- **Code-authored text the model had to repeat.** The REDIRECT text is code-authored, while the DM was given an
  unnamed refusal.
- **Wrong or missing context.** The Fixer has no condition-origin view.

## Lanes (spec 032)
- **Root cause (`costs.py` footing → self-held hold): not in P4, P5 or P6.** It is an engine and rules cost-form defect shared with
  the pipeline. It is best fixed by one guard in `apply_cost`:
  - when the actor would be the "holder" of a hold-ladder condition, take a non-hold form instead (S3: slowed or cornered; S4: the
    worse-place slide, or prone);
  - or require an opposing holder for "held in opponent's control".

  As a P3 follow-up, it belongs to the `fail_cost` lane.
- **P4 (world step).** `release_holds` does not run on the dm-tools path. Wiring it in would not have saved this case
  unless it also ends holds whose source is the held entity, or whose holder is absent.
- **P5 (records and context).** In dm-tools turn records, `parts`, `said`, `claim_log` and `draft_versions` are empty in 15 of 17 turns.
  Turn.15 has `beats: []` even though a G4 beat ran. The DM's refusal string does not name the blocking condition.
- **P6 (`/fix`).** There is no proposal to remove a condition, and condition history does not appear in
  `entity`, `ledger` or `search`. As a result the Fixer made up a cause and could not remove the pin.

## Side note: the [28] offer named only "the leader's name"
This is model wording, not code. In call 17 (turn.12) the DM sent `goal: "Make Eliard give up the leader's name"`
alongside `change_what: "the name and count of the Choir's leader"`. The OFFER title is the goal verbatim
(`dm_tools.py:475-476`, then `oof.offer_title`). The phrase "a name and a count" was the DM's own line from turn.11.
