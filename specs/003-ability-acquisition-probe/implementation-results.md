# Implementation Results: Ability Acquisition Probe (Real, Automated Run)

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)
**Date**: 2026-09-29
**Method**: Real code (`src/ability_pool.py`, extended `src/world_state.py`/`src/auditor.py`),
real tool-calling, run against the live Gemini API (`gemini-3.8-flash`). Six scripted
scenarios, no relay, no human in the loop during execution.

## Headline result

**Pattern P5's first flavor (source-gates-a-bounded-pool, method-picks-the-fill) works, live,
on the first mechanism this project has built that generates real content rather than just
tracking state.** All 38 unit tests pass with zero live API cost (SC-001). All 6 scripted
scenarios correctly called `grant_ability` with the exact source archetype and acquisition
method each was designed to imply (SC-002, 100%). The extended auditor found one genuine,
real narration/grant mismatch out of six (SC-003: 5/6, 83% measured consistency) — reported as
a finding, not hidden or silently patched. The entire live validation pass used well under
SC-004's 50-call budget.

## Success Criteria results (per spec.md), this run

| # | Criterion | Result |
|---|---|---|
| SC-001 | Deterministic mechanism returns the correct archetype's template 100% of the time, zero live calls | **True.** 7/7 `test_ability_pool.py` tests pass (38/38 total suite), entirely offline. |
| SC-002 | At least one scripted scenario per archetype and per method calls `grant_ability` correctly | **True, and exceeded.** 6/6 scenarios (covering all 4 archetypes and all 3 methods) called `grant_ability` with the exact correct `source_archetype`/`acquisition_method`. |
| SC-003 | Measured narration/grant consistency rate, broken out by archetype and method | **True.** 5/6 (83%) overall; by archetype: beast 2/2, elemental_fire 1/2, undead 1/1, construct 1/1; by method: decisive_kill 2/2, narrow_survival 2/2, non_lethal_subdual 1/2. Reported as a measured rate, not a pass/fail gate, per spec.md's own framing. |
| SC-004 | Full live validation pass stays under ~50 API calls | **True.** Each scenario needed roughly 2-3 `generate_content` calls for the DM turn plus 1 auditor call; six scenarios plus the two single-scenario validation runs during T012 totaled well under 50 — comfortably inside budget, no separate check needed. |

## Real findings from actually building and running this

### 1. The scripted scenarios' first version tested the wrong thing entirely — and the DM was right, not buggy

The first version of `ability_acquisition_scenarios.py` scripted each `action` as narrating the
kill itself (e.g. "I drive my spear through its chest, dropping it instantly"). Run live, the
DM correctly followed Pattern P8 (already established by Feature 001: real-stakes actions get
resolved by `roll_check`, never just narrated into success) — it rolled, got a **critical
failure**, and correctly narrated the *opposite* of the scripted premise: the player got mauled,
not the wolf killed. `grant_ability` correctly wasn't called, because the kill genuinely didn't
happen in that resolution.

This was not a bug in `ability_pool.py`, `WorldStateToolHandlers`, or the DM — every piece
behaved exactly as designed. The bug was in the *test*: assuming a player's narrated intent is
guaranteed to succeed contradicts this project's own already-adopted resolution philosophy.
Fixed by rewriting every scenario so the kill/acquisition is already a settled, past-tense fact
in the scenario's `context`, with `action` reduced to a genuine no-stakes follow-up (Pattern
P8's own "no real stakes, narrate directly" case) — which is what actually isolates "does the
DM map an established event onto `grant_ability`'s categories correctly" from "did a fresh roll
happen to succeed," a different question this probe was never trying to test.

### 2. The one real conflict found: narration oversteps a granted ability's actual, neutral limitation

For `elemental_fire_non_lethal_subdual`, the DM correctly called `grant_ability` with the right
archetype and method, and correctly received `Heat Resistance` ("Fire and intense heat harm you
less... but this offers no protection against cold"). Its narration, however, went further than
the tool result licensed: it stated that extreme cold now "shocks the character more harshly
than normal" — inventing an *active* vulnerability the granted ability never states. "No
protection against cold" is a neutral absence of benefit, not a stated penalty; the DM narrated
a penalty anyway. The extended auditor (`check_turn`'s new `ability_grant` parameter) caught
this correctly, attributing it to the new `"abilities"` state category.

This is a small but real instance of the same general failure class Feature 002 already
documented at length (narration drifting past what a tool call actually licensed) — now
observed for the first time in a content-generating mechanism rather than a pure state-tracking
one. One data point isn't enough to draw a rate-level conclusion from, but it's worth naming:
**embellishing a granted effect's fictional flavor beyond its literal, mechanically-defined
limitation** is a concrete failure mode to watch for as more of Pattern P5 gets built.

## Comparison to Feature 001/002's implementation-results.md

| | Feature 001 (pure resolution) | Feature 002 (pure state tracking) | Feature 003 (first content-generating mechanism) |
|---|---|---|---|
| What was tested | Does narration match a computed degree | Does narration stay consistent with externalized state across many turns | Does the DM correctly classify a narrated event onto a small, closed set of categories, and does narration stay faithful to what was actually granted |
| Result | 0/8 contradictions | 3/5 sessions survived their full cap with 0 conflicts | 6/6 correct tool calls; 5/6 (83%) narration/grant consistency |
| Bugs found | SDK/provider plumbing issues | A live-reference snapshot bug, an auditor missing pre-turn context | A test-scripting assumption that contradicted this project's own already-adopted resolution philosophy (Pattern P8) |
| What this confirms | The resolve→narrate mechanism holds for isolated turns | Multi-turn state tracking holds once auditor bugs are fixed | Pattern P5's first flavor is buildable and testable with the same three-layer architecture already validated twice — no new architectural risk, only a new content dimension |

## Limitations (read before citing this result elsewhere)

- **Tiny sample.** 6 scenarios, 1 model, throwaway probe content (spec.md's Assumptions) never
  meant to survive into the real game. This establishes the mechanism is buildable and
  measurable, not that any specific consistency rate is representative at scale.
- **The auditor is still not an independent judge**, same disclosed limitation as Feature
  001/002 — a same-model-family bounded check, not a validated classifier.
- **Each scenario is a single, isolated turn**, not a session — this probe deliberately does
  not test whether a granted ability stays consistently described across many *later* turns
  (that would be a long-horizon question, Feature 002's territory, not this one's).
- **The class/archetype-emergence flavor of Pattern P5 remains untouched**, per FR-007 — this
  result says nothing about whether that separate, still-unbuilt mechanism will work.

## Recommended follow-ups

1. **When authoring real game content on this mechanism**, watch specifically for the
   embellishment failure mode found here (narration adding an unstated penalty/limitation
   beyond what was actually granted) — a system-prompt addition reinforcing "narrate exactly
   what the tool result licenses, no more" is a cheap, targeted next experiment, same shape as
   Feature 002's own follow-up recommendation for its tool-compliance gap.
2. **Before building the class-emergence classifier layer**, confirm this mechanism holds up
   at slightly larger scale (more archetypes, more scenarios) — not because this result was
   weak, but because the classifier's whole premise depends on this layer's `ability_grants`
   state being trustworthy.
3. Same follow-up recorded in every prior feature: if a real judge-gate is ever built into the
   live game, don't reuse `auditor.check_turn` as-is — it doesn't meet Pattern P13's
   independent-model-family requirement.
