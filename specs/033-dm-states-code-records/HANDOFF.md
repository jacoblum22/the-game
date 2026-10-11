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
Owner decisions open (plan Risks 1-3): D1 foe-choice guidance and 06.9.1's retired rationale; D2 foe acts declared
with the move vs after the result; D3 defaults vs refusals for omitted details. The plan builds on the recommendations.
Traps:
1. 06.9.1 says "the DM never chooses for an adversary" (research-backed): R must rewrite it before P3 merges.
2. Footing forms depend on the severity, known only after the roll: pick on the answer turn (A4), never at propose.
3. Most `excludes` entries name no licence id ("a license"): R adds `covered_by`, or P2b has nothing exact to grant.
4. `dm_tools.py` is touched by P1, P4, P3, P5: stay inside the function lanes in plan 5; merge order is fixed there.
5. Re-record only `offline_seed11_dmtools`, never from two parallel phases. Files are CRLF in the working copy.
6. P0's census may find word matchers the inventories missed: assign each to a lane, else P6.
