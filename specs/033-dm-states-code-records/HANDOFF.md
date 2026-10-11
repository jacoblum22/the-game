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
