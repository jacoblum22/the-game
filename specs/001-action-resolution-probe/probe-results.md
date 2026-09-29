# Action Resolution Probe — Results

**Feature**: [spec.md](spec.md)
**Date**: 2026-09-28
**Method**: A live, turn-by-turn interactive session with a general-purpose subagent (Haiku
model) acting as the AI DM, relayed in real time through the orchestrating session. The
project owner played the character live and reacted to the DM's output turn by turn; nothing
was scripted or run in batch.
**Outcome**: Complete — 13 turns total, 10 resolved (rolled) actions reached as targeted by the
spec.

## Verdict at a glance

The mechanical risk this probe was actually built to test (Patterns P8 and P13/P3 — can the AI
compute a deterministic degree-of-success and keep narration/state honestly in sync with it)
**held up cleanly across the whole session**. The problems that did show up were different
risks the spec didn't target but that earlier research had already predicted: DM pacing/craft
(a soft-lock and its recovery) and a resolution-granularity gap surfaced live by the player
(how to score a single roll that bundles several distinct sub-questions). Both are valuable,
neither contradicts Patterns P8/P13 — they sharpen what still needs design work around them.

## Success Criteria results (per spec.md)

| # | Criterion | Result |
|---|---|---|
| SC-001 | 100% of resolved actions produce a computed degree-of-success, not free-form judgment | **Met.** All 10 resolved actions show an explicit DC, roll, and degree computed from roll-vs-DC, including the final DC 25 edge case. |
| SC-002 | Rate of narration/computed-degree contradiction (target: 0) | **0 mechanical contradictions found** — narration never asserted a success after a computed Failure or vice versa, across all 10 resolved turns. One non-mechanical consistency slip was found on manual review (see Findings) that the DM's own self-assessment did not catch, despite being explicitly asked to hunt for exactly this kind of issue. |
| SC-003 | A reviewer can determine from logged output alone whether state matches the computed outcome | **Met.** The structured per-turn header (Action / Requires Resolution / DC+Roll / Degree / Vitality) made every check trivial without re-reading prose. |
| SC-004 | System declines to roll for 100% of stakes-free descriptions | **Met** for all 3 no-resolution turns (session start, close examination of already-established tree marks, the DM-initiated environmental lead). All correctly marked "Requires Resolution: no." |

## Turn log

| Turn | Action | Req'd? | DC | Roll+mod=Total | Degree | Vitality |
|---|---|---|---|---|---|---|
| 1 | Session start | No | — | — | — | 12/12 |
| 2 | Follow the wheel-ruts | Yes | 15 | 14+2=16 | Success | unchanged |
| 3 | Search clearing for tracks/dismantling/magic | Yes | 15 | 16+2=18 | Success | unchanged |
| 4 | Identify the silver chain's origin | Yes | 15 | 12+2=14 | Failure | unchanged |
| 5 | Examine tree-mark height closely (follow-up on turn 3) | No | — | — | — | unchanged |
| 6 | Discern the marks' purpose | Yes | 16 | 9+2=11 | Failure | unchanged |
| 7 | Identify the ground pattern as a sigil | Yes | 17 | 18+2=20 | Success | unchanged |
| 8 | *(DM-provided environmental lead — player-requested OOC nudge out of a soft-lock)* | No | — | — | — | unchanged |
| 9 | Climb the canopy and sneak toward the chanting | Yes | 15 | 17+2=19 | Success | unchanged |
| 10 | Identify creature type / weakness / intelligence (compound question) | Yes | 16 | 13+2=15 | Failure | unchanged |
| 11 | Assess whether caravan captives are alive/unharmed | Yes | 15 | 19+2=21 | Success | unchanged |
| 12 | Shoot the creature in the head, try to kill it | Yes | 16 | 11+2=13 | Failure | unchanged |
| 13 | Fire ~10 more arrows while cultists close in | Yes | 25 | 16+2=18 | Failure | 12→10 |

Tally: **5 Success, 5 Failure, 0 Critical Success, 0 Critical Failure** across 10 resolved
actions; 3 no-resolution narrative turns.

## Findings

### 1. Mechanical resolution and state tracking: no failures observed

Across combat, investigation, and social/perception checks, the DM never asserted an outcome
inconsistent with its own computed degree, and Vitality stayed correctly pinned at "unchanged"
for 9 of 10 resolved turns, changing exactly once, with an explicit before→after, at the one
point the fiction actually implied harm. This is a clean result for the specific risk (Patterns
P8, P3, P13) this probe was designed to stress-test — though see the caveat under "Scope" below
before treating this as a strong general result.

### 2. Two real design gaps surfaced — neither is the risk we were testing for

- **DM pacing/soft-lock (turns 6-8).** After several escalating-but-inconclusive clues, the
  player reported feeling "soft-locked" with no actionable next step. This is precisely the
  gap the third research pass flagged: spotlight balance and scene pacing don't fall out of
  good mechanical design for free and need to be engineered as an explicit heuristic. The DM
  recovered acceptably when nudged out-of-character (turn 8, an environmental lead with a
  ticking clock), but nothing in the current constitution or this feature's spec would have
  caught this proactively — it took the player noticing and saying so.
- **Compound-question resolution granularity (turn 10 and after).** The player bundled several
  distinct sub-questions ("is it a demon? fey? shade? does it have a weakness? is it
  intelligent?") into one action, which the DM resolved as a single all-or-nothing roll — one
  Failure meant zero information on all five. The player identified, live, that this is the
  wrong shape: degree of success should gate *how much* information comes back (a graduated
  reveal), not just whether any comes back at all. A corrected rule was drafted and relayed
  mid-session (see below) and accepted by the DM, but never actually exercised in a live turn
  afterward — this is a genuine loose end, not a confirmed fix.

### 3. A stress test the DM handled well

Turn 13 ("I shoot it 10 more times") tried to compress many attack attempts into one action
under active time pressure (cultists closing in). Rather than either mechanically granting 10
independent rolls or flatly refusing the action, the DM fictionally throttled the attempt to
2-3 shots given the established seconds-to-spare pressure, explained why, and resolved it as one
roll against a correspondingly steep DC (25). This is a more sophisticated judgment call than
this project has any explicit action-economy rule (Pattern P9) to justify yet — worth noting as
a positive data point on what a capable model can improvise correctly even ahead of the rules
being formally specified.

### 4. The self-assessment missed something a human reviewer caught

In the final turn's narration, the DM referred to the player character as "she" — a gender that
was never established anywhere in the previous 12 turns (all prior narration used second-person
"you"). The DM's own self-assessment, explicitly instructed to hunt for exactly this class of
issue, reported "no inconsistencies detected." This is a small thing on its own, but it is a
direct, concrete instance of the exact problem Pattern P13 is built around: **the narrating
model's own self-report is not a reliable substitute for independent verification.** This
probe's self-assessment step should be read as a useful-but-insufficient check, not a
substitute for the external, code-enforced verification P13 actually calls for.

## Scope caveats — read before generalizing from this result

- This was run via **relayed chat turns with a human in the loop reacting in real time**, not
  the automated, tool-enforced architecture Pattern P13 actually specifies (no real dice-roll
  tool call outside the model's own text, no externalized state store separate from the
  conversation, no independent judge gate). The clean SC-002 result here says the *degree-of-
  success mechanic itself* is learnable and followable by a capable model under attentive,
  favorable conditions — it does **not** yet demonstrate the harder claim that the full P13
  architecture holds up unattended, at scale, or under the state-desync pressure the third
  research pass measured (46-58% consistency in comparable published systems).
- The model used was Haiku, chosen for cost, not capability-matching to a production decision.
  A different model might do better or worse on the same task.
- Sample size is one session, one character, one line of questioning. Turn 10's compound-
  question issue in particular deserves a follow-up test now that a corrected rule exists but
  was never actually exercised.

## Recommended follow-ups

1. **Run a second short session** that deliberately exercises the graduated-info compound-
   question rule from turn 10 onward, since it was agreed but never tested.
2. **Consider whether "spotlight/pacing" needs its own Adopted Design Pattern or Core
   Principle**, distinct from the build-diversity and consolidation principles already in the
   constitution — this probe is the first time the project has direct evidence the gap is real
   in practice, not just in research.
3. **When building the real (non-relayed) version of this feature**, treat this probe's clean
   result as a floor, not a ceiling: the actual tool-calling/externalized-state/judge-gate
   architecture still needs to be tested on its own terms, since this session didn't exercise it.
