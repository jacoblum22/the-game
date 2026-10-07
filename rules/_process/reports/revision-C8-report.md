# Revision C8 report (rows I-108, I-109, I-110)

## I-108: ch.04 prose figures (resolved)
- `04-recog04.py` re-run (about 3.5 minutes): output byte-identical to the committed `04-recog04-output.txt`, which
  agrees with T-04-8. Only the prose was stale.
- Re-quoted, tagged `[revision: I-108]`: 04.2.3 (Warrior: mixed fighter median session 4, p10–p90 3–5;
  swordsman 4 of 200; archer 46 of 200), 04.4.3 (grant 90, offer 70, abstain 38 of 100), 04.8.2 (lapsed 172 /
  67 / 9 / 0 of 179), WE-04-8 (confirmed in 112 of 179 after one more session; the new calling a median 4 sessions
  after the turn, p10–p90 2–5, which was "3").
- `04-recognition-sim.md`: R3, R7 and R8 tables refreshed from the same output.
- DL-04-35.

## I-109: Wren's worked examples (resolved)
- Cause: WE-04-2 and WE-04-3 quoted the pre-I-089 Wren trace that `04-recognition-sim.md` still carried, where
  stealth was abstained at scene 97 and the grant was at weighted 85.
- `04-wren04.py` (seed 7) now also prints the tag weights at the first grant. The output is re-committed, with
  one line added and nothing else changed.
- WE-04-2's thin row is now Wren's tracking at scene 75 (weighted 95, recent 39, confidence 0). It is offered two
  scenes later, at scene 77, with confidence 2, exactly as WE-04-1 shows. Its "other side" names the K1 and K5
  margins. On the current ladder, stealth is first eligible at scene 95 with confidence 1 and is offered, so it
  has no abstain to show.
- WE-04-3: scene 10, weighted 84, confidence 4.
- WE-04-5: bow 84, archery 84 (a tie), acrobatics 37, tactics 0, cited to the sim.
- The Wren paragraph in `04-recognition-sim.md` is replaced with the current trace.
- DL-04-36.

## I-110: Working with rider timing (resolved, preferred fix)
- Sound: the generator's `FORMS` table and `abilities.yaml#forms` already give Working the timings
  `[beat, rider]`, and the generator rejects any other pairing.
- The rest of the rules already handle a rider Working:
  - the regime is independent_trigger on the `on_degree` hook (05.10.1);
  - riders resolve at depth 0 (05.10.5);
  - the budget's timing term is rider 0 (05.11.2), and 05.11.5 already prices Aimed Shot as "Working · rider";
  - one rider per beat applies (05.4.3).
- Re-forming the 31 entries would not work. Edge is passive only, Lever gives only a lever and Exception only an
  exception, while these abilities deal harm, apply conditions and move targets.
- Edits, tagged `[revision: I-110]`:
  - 05.3.2's Working row now reads `beat or rider`, with a paragraph defining the rider Working;
  - the definition of the word Working in 05.1.3;
  - the `rider` row of 05.3.4.
- `05-ladder-check.py` re-run: 183 callings, 0 failures, output unchanged.
- DL-05-42.
- New rows (IDs taken after I-124; renumber if a parallel agent used them):
  - **I-125**: ch.00's glossary line for `working` is now narrower than 05.1.3. It is outside C8's chapters.
  - **I-126**: 05.3.2's "Operations it may use" column for Working leaves out `lever`, `step`, `modify`,
    `restrict` and `prevent`, which Working entries use 127, 95, 65, 37 and 22 times. This needs a rule decision.

## Close-out
- `appendix/decision-log.md` and `traceability.md` re-assembled with `integration-assemble-appendix.py`.
- Anchors: 129, 0 errors, 0 warnings.
- Validator: 0 ERROR / 0 WARN.
- Committed in the worktree, as the C8 prompt directs.
