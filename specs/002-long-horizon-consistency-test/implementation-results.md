# Implementation Results: Long-Horizon Consistency Test (Real, Automated Run)

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)
**Date**: 2026-09-29
**Method**: Several live batches against the Gemini API (`gemini-3.8-flash`), run iteratively
because the first two attempts turned out to be measuring our own bugs, not the DM. The
numbers below are from the corrected final verification run, after both bugs (documented below)
were found and fixed. No relay, no human in the loop during execution.

## Headline result (corrected)

**The first two runs of this batch reported 0% survival across every session — and that number
was wrong.** It was substantially an artifact of two real bugs in this feature's own test
harness, not a measurement of the AI DM. After fixing both, a verification run (5 completed
sessions, 12-turn cap) found **3 of 5 (60%) survived their entire turn cap with zero detected
conflicts**, and the 2 genuine conflicts that remained both share one specific, well-understood
pattern: the DM narrated a state change (new loot, a new position) without calling the matching
tool to persist it — not memory decay, not arithmetic drift, a tool-compliance gap.

This reverses the original conclusion. The corrected picture is **closer to, or better than,**
the NCP-Bench comparison point (42% survival at turn 20 for the best tested model), not starkly
worse than it — though see Scope note below on why this isn't a clean apples-to-apples number.

## The two bugs, and why they fully change the result

### Bug 1: `WorldState.to_dict()` returned live references, not snapshots

`resources`, `possessions`, and `status_flags` were returned by direct reference. Confirmed with
a plain Python reproduction (no API call needed) that an earlier `get_state()` result silently
changes if a later call in the same turn mutates `world_state` — and confirmed, separately, that
this live reference survives all the way through the google-genai SDK's own `Part` construction
(`FunctionResponse.response` also holds the object, not a copy). This meant a `get_state` result
requested early in a turn could be corrupted by a later tool call in the same batch before the
model (or our own diagnostic logging) ever inspected it. Fixed by deep-copying `resources` and
shallow-copying `possessions`/`status_flags` on every `to_dict()` call; locked in with
`test_get_state_snapshot_is_not_mutated_by_a_later_change`.

### Bug 2 (the bigger one): the auditor was never given the pre-turn state

`auditor.check_turn` only ever received the *current* (already-mutated-by-this-turn) world
state — never what it looked like before the turn. It had no way to distinguish "this was
already true before the action" from "this became true because of the tool call this turn's own
narration is describing." Concretely, this produced false positives like: narration says "you
find and pick up the spyglass," this turn's own `set_fact` call granted the spyglass, and the
auditor still flagged it as "the world state shows the character already possesses the
spyglass" — completely ordinary cause-and-effect, misread as a contradiction. A resource-delta
conflict was traced the same way: the auditor asserted an incorrect "before" value it was never
actually shown, rather than the DM making a real math error. Verified by reading the raw
tool-call log (added specifically to check this) against each conflict's claimed cause, across
two separate reproductions.

Fixed by passing `state_before` explicitly alongside the current state, and revising the "fact"
conflict criterion to explicitly exempt a before→after change the narration itself explains (see
`contracts/pipeline-prompts.md`'s amendment note for the full contract change).

## What the corrected data actually shows

| Run | Persona | Turns completed | Conflict? | What actually happened |
|---|---|---|---|---|
| outpost-adversarial | adversarial | 1 | Yes (fact/resources) | Narrated recovering "15 silver pieces"; no tool call ever added a resource for it. |
| outpost-natural | natural | 12 (full cap) | No | — |
| lighthouse-adversarial | adversarial | 5 | Yes (fact/position) | Narrated moving to "an elevated staircase landing"; no `set_fact` call updated position away from the vestibule. |
| lighthouse-natural | natural | 12 (full cap) | No | — |
| archive-adversarial | adversarial | 12 (full cap) | No | — |
| archive-natural | natural | 4 (cut short) | N/A | A transient `RemoteProtocolError` (server disconnected) ended the batch here — a real network hiccup, not a bug. The graceful-interruption handling added earlier caught it cleanly and reported on the other 5 completed runs; nothing was lost from them. |

Both genuine conflicts are the same failure shape: **the DM's narration is ahead of its own
tool-call record** — it describes an effect but doesn't call the tool that would make that
effect real in the tracked state. That's a concrete, actionable thing (reinforce "if your
narration describes a state change, you must call the matching tool" in the system prompt), and
notably different from either of the two originally-suspected mechanisms (long-horizon memory
decay, or same-turn arithmetic confusion) — both of which turned out to be our own bugs.

## Scope note: this is a 12-turn cap, not the spec'd 50

This verification run used a 12-turn cap to keep iteration cheap while still actively fixing
bugs, not spec.md's originally intended up-to-50-turn cap. That was a deliberate, cost-conscious
choice during debugging, agreed with the project owner rather than assumed. Once conflicts
stopped being manufactured by auditor bugs, 3 of 5 sessions ran their *entire* cap without
issue — meaning a real 50-turn batch would very plausibly cost meaningfully more (longer
surviving sessions run more turns, hence more API calls) than the original, artificially-short
buggy runs did. The project owner and I agreed this deeper, full-length run isn't worth doing
right now: the two real bugs are fixed and documented, the core mechanism looks sound once given
accurate state, and this feature's actual reusable value going forward is the `WorldState`/
`auditor` machinery itself — now that its false-positive bug is fixed, ordinary future testing
and playtesting (built on the same architecture) will keep generating comparable consistency
data as a side effect, without needing a dedicated synthetic-scenario batch every time.

## Comparison to Feature 001's implementation-results.md

| | Feature 001 (10 turns, 1 tracked resource) | Feature 002, corrected (up to 12 turns, 4+ tracked categories) |
|---|---|---|
| What was tested | Does a single resolved turn's narration match its computed degree | Does narration stay consistent with an externalized multi-category state ledger, across many turns and two persona conditions |
| Result | 0/8 contradictions | 3/5 sessions ran their full cap with 0 conflicts; the 2 genuine conflicts found were both "narrated a change, didn't call the tool for it" |
| What this shows | The core resolve→narrate mechanism (Pattern P8) holds for isolated, well-formed turns | The same general reliability extends to multi-turn, multi-category state — genuinely more fragile than Feature 001's single-resource case, but not by the dramatic margin the (buggy) first attempt suggested |
| Bugs found | SDK/provider plumbing issues (role name, parameter name, model deprecation) | A harness data-integrity bug (live references) and a test-methodology bug (auditor missing pre-turn context) — both more consequential than Feature 001's plumbing issues, since they directly inverted this feature's headline conclusion until caught |

## Limitations (read before citing this result elsewhere)

- **Small, further-reduced sample.** 5 completed runs (not 6 — a transient network error, not a
  bug, cut the 6th short), at a 12-turn cap, not the originally-scoped 50. Treat this as "enough
  to correct course and establish a plausible direction," not a statistically powered result.
- **The auditor is still not an independent judge**, even after this fix. It's a same-model-
  family bounded LLM call (Pattern P13's already-disclosed limitation) — fixing its missing
  before/after context removed a specific, confirmed source of false positives, but doesn't make
  it a validated classifier in general.
- **This process is itself a live demonstration of why the project's "test empirically, verify
  before trusting a surprising result" habit matters.** The original 0/6 headline would have
  shipped as this feature's documented conclusion if it hadn't been directly challenged and
  checked against raw tool-call ground truth.

## Recommended follow-ups

1. **Reinforce tool-call compliance in the system prompt** — both genuine conflicts found were
   the DM narrating an effect without calling the matching tool. A prompt addition like "if your
   narration describes any change to a tracked resource, possession, position, or status flag,
   you must call the matching tool in the same turn" is a cheap, targeted next experiment.
2. **Let future testing and playtesting accumulate this data organically**, now that the
   auditor's false-positive bug is fixed — no dedicated large batch needed until there's a
   specific reason to target very long sessions on demand again.
3. Same follow-up already recorded twice now: if a real judge-gate is ever built into the live
   game (Principle III's revisit trigger), don't reuse `auditor.check_turn` as-is — it doesn't
   meet Pattern P13's independent-model-family requirement, this fix notwithstanding.
